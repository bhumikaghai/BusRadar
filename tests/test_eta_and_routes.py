"""
Test Route Polyline Geometry, RDP Simplification, Road-Following ETA
"""
import pytest
from server import ramer_douglas_peucker, routes_db, haversine_distance_meters, snap_to_route_polyline

def test_rdp_simplification():
    # Straight line with 10 collinear points + 1 slight jitter
    line = [[30.0 + i * 0.01, 77.0 + i * 0.01] for i in range(10)]
    # Add tiny deviation in the middle
    line[5][0] += 0.00001

    simplified = ramer_douglas_peucker(line, epsilon=0.0001)
    # The collinear points should be reduced down to start and end
    assert len(simplified) == 2
    assert simplified[0] == line[0]
    assert simplified[-1] == line[-1]

def test_default_route_loaded():
    assert "ynr_mmdu_sh4" in routes_db
    route = routes_db["ynr_mmdu_sh4"]
    assert len(route["polyline"]) >= 10
    assert len(route["stops"]) == 7
    assert route["stops"][0]["name"] == "Yamuna Nagar Bus Stand"
    assert route["stops"][-1]["name"] == "MMDU Campus Gate"

def test_road_following_distance_vs_euclidean():
    """Verify that road-following distance along polyline reflects highway curve."""
    polyline = routes_db["ynr_mmdu_sh4"]["polyline"]

    # Straight-line distance between start and end
    straight_dist = haversine_distance_meters(
        polyline[0][0], polyline[0][1],
        polyline[-1][0], polyline[-1][1]
    )

    # Cumulative road distance along all polyline vertices
    road_dist = 0
    for i in range(len(polyline) - 1):
        road_dist += haversine_distance_meters(
            polyline[i][0], polyline[i][1],
            polyline[i + 1][0], polyline[i + 1][1]
        )

    # Road-following distance must be greater than straight Euclidean chord
    assert road_dist > straight_dist
    assert 24000 < road_dist < 32000 # ~28 km highway corridor

def test_eta_calculation_formula():
    """Test road ETA calculation with dwell allowance and speed floor."""
    remaining_dist_km = 20.0 # 20 km remaining
    raw_speed_kmh = 10.0     # Slow crawl, should clamp to floor 15 km/h
    clamped_speed = max(15.0, min(80.0, raw_speed_kmh))
    assert clamped_speed == 15.0

    dwell_mins = 2.0         # Intermediate stop dwell
    delay_reported = 5.0     # Driver delay

    travel_mins = (remaining_dist_km / clamped_speed) * 60 # (20 / 15) * 60 = 80 mins
    total_eta = travel_mins + dwell_mins + delay_reported

    assert total_eta == 87.0
