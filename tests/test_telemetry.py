"""
Test Telemetry Schemas, GPS Quality Filtering & Bounds Validation
"""
import pytest
from pydantic import ValidationError
from server import (
    DriverTelemetrySchema,
    DriverDelaySchema,
    haversine_distance_meters,
    snap_to_route_polyline,
    routes_db
)

def test_telemetry_valid():
    payload = {
        "event_type": "DRIVER_TELEMETRY",
        "bus_id": "HR-02-A-1001",
        "lat": 30.1340,
        "lng": 77.2750,
        "accuracy": 8.5,
        "speed_kmh": 45.0,
        "heading": 120.0,
        "client_timestamp": 1700000000.0,
        "sequence_number": 1
    }
    schema = DriverTelemetrySchema(**payload)
    assert schema.lat == 30.1340
    assert schema.lng == 77.2750
    assert schema.accuracy == 8.5
    assert schema.speed_kmh == 45.0

def test_telemetry_out_of_bounds_coords():
    # Outside North India bounding box (lat must be between 27.0 and 33.0)
    with pytest.raises(ValidationError):
        DriverTelemetrySchema(
            bus_id="HR-02-A-1001",
            lat=19.0760, # Mumbai latitude - should be rejected!
            lng=72.8777,
            accuracy=10.0,
            speed_kmh=40.0,
            client_timestamp=1700000000.0
        )

def test_telemetry_impossible_speed():
    # Speed exceeding 130 km/h should fail schema
    with pytest.raises(ValidationError):
        DriverTelemetrySchema(
            bus_id="HR-02-A-1001",
            lat=30.1340,
            lng=77.2750,
            accuracy=10.0,
            speed_kmh=250.0, # Impossible bus speed
            client_timestamp=1700000000.0
        )

def test_xss_string_sanitization():
    schema = DriverTelemetrySchema(
        bus_id="<script>alert('xss')</script>HR-02",
        lat=30.1340,
        lng=77.2750,
        accuracy=10.0,
        speed_kmh=40.0,
        client_timestamp=1700000000.0,
        route_from="<b>Yamuna Nagar</b>"
    )
    assert "<script>" not in schema.bus_id
    assert "&lt;script&gt;" in schema.bus_id
    assert "&lt;b&gt;" in schema.route_from

def test_delay_schema_validation():
    valid = DriverDelaySchema(
        bus_id="HR-02-A-1001",
        delay_minutes=15,
        reason="Heavy Rain & Traffic"
    )
    assert valid.delay_minutes == 15
    assert valid.reason == "Heavy Rain &amp; Traffic" or "Heavy Rain & Traffic" in valid.reason

    # Negative delay rejected
    with pytest.raises(ValidationError):
        DriverDelaySchema(
            bus_id="HR-02-A-1001",
            delay_minutes=-5
        )

def test_haversine_formula_accuracy():
    # Distance between Yamuna Nagar Bus Stand [30.1290, 77.2674] and Jagadhri Bus Stand [30.1435, 77.2880]
    dist = haversine_distance_meters(30.1290, 77.2674, 30.1435, 77.2880)
    # Geodesic distance is approximately 2.5 km (2500m)
    assert 2300 < dist < 2800

def test_snap_to_route_polyline():
    polyline = routes_db["ynr_mmdu_sh4"]["polyline"]
    # Point slightly off highway
    test_lat, test_lng = 30.1320, 77.2700
    snapped_lat, snapped_lng, dist = snap_to_route_polyline(test_lat, test_lng, polyline)

    # Snapped distance to the road segment should be < 200m
    assert dist < 200.0
    assert 30.128 <= snapped_lat <= 30.255
    assert 77.040 <= snapped_lng <= 77.295
