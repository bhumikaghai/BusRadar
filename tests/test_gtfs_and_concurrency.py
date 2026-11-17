import pytest
import time
import json
import asyncio
from starlette.testclient import TestClient
from server import app, active_trips, registered_buses, manager

@pytest.fixture(autouse=True)
def clear_trips():
    active_trips.clear()
    yield
    active_trips.clear()

def test_gtfs_static_feed_endpoints():
    client = TestClient(app)
    
    # 1. feed.json
    res = client.get("/api/gtfs/feed.json")
    assert res.status_code == 200
    feed = res.json()
    assert feed["agency_id"] == "HR_ROADWAYS"
    assert len(feed["available_tables"]) == 5
    assert feed["routes_count"] >= 1
    
    # 2. agency.txt
    res_agency = client.get("/api/gtfs/agency.txt")
    assert res_agency.status_code == 200
    assert "agency_id,agency_name" in res_agency.text
    assert "HR_ROADWAYS" in res_agency.text
    
    # 3. routes.txt
    res_routes = client.get("/api/gtfs/routes.txt")
    assert res_routes.status_code == 200
    assert "route_id,agency_id,route_short_name" in res_routes.text
    assert "ynr_mmdu_sh4" in res_routes.text
    
    # 4. stops.txt
    res_stops = client.get("/api/gtfs/stops.txt")
    assert res_stops.status_code == 200
    assert "stop_id,stop_name,stop_lat,stop_lon" in res_stops.text
    assert "Yamuna Nagar Bus Stand" in res_stops.text
    
    # 5. trips.txt
    res_trips = client.get("/api/gtfs/trips.txt")
    assert res_trips.status_code == 200
    assert "trip_ynr_mmdu_sh4_up" in res_trips.text

    # 6. stop_times.txt
    res_st = client.get("/api/gtfs/stop_times.txt")
    assert res_st.status_code == 200
    assert "stop_sequence" in res_st.text

def test_gtfs_rt_vehicle_positions_empty_and_populated():
    client = TestClient(app)
    
    # Empty fleet on boot
    res = client.get("/api/gtfs-rt/vehicle-positions")
    assert res.status_code == 200
    feed = res.json()
    assert feed["header"]["gtfs_realtime_version"] == "2.0"
    assert feed["header"]["incrementality"] == "FULL_DATASET"
    assert len(feed["entity"]) == 0
    
    # Seed active trip
    now = time.time()
    active_trips["HR-02-A-1001"] = {
        "bus_id": "HR-02-A-1001",
        "route_id": "ynr_mmdu_sh4",
        "route_name": "Yamuna Nagar Stand ⇄ MMDU Campus Gate",
        "lat": 30.1290,
        "lng": 77.2674,
        "speed_kmh": 40.0,
        "heading": 90.0,
        "delay_minutes": 0,
        "last_updated_timestamp": now,
        "status": "LIVE"
    }
    
    res_pop = client.get("/api/gtfs-rt/vehicle-positions")
    assert res_pop.status_code == 200
    feed_pop = res_pop.json()
    assert len(feed_pop["entity"]) == 1
    entity = feed_pop["entity"][0]
    assert entity["id"] == "entity_HR-02-A-1001"
    assert entity["vehicle"]["vehicle"]["id"] == "HR-02-A-1001"
    assert entity["vehicle"]["position"]["latitude"] == 30.1290
    assert entity["vehicle"]["position"]["longitude"] == 77.2674
    assert entity["vehicle"]["position"]["speed"] == round(40.0 / 3.6, 2)
    assert entity["vehicle"]["current_status"] == "IN_TRANSIT_TO"

def test_deep_health_endpoint_diagnostics():
    client = TestClient(app)
    res = client.get("/api/health")
    assert res.status_code == 200
    health = res.json()
    assert health["status"] == "healthy"
    assert health["version"] == "2.1.0"
    assert "gtfs_rt_available" in health
    assert health["gtfs_rt_available"] is True
    assert "gtfs_static_available" in health
    assert health["gtfs_static_available"] is True
    assert "registered_fleet_count" in health
    assert health["registered_fleet_count"] >= 3
    assert "active_fleet_summary" in health

def test_multi_bus_concurrency_and_stale_detection():
    client = TestClient(app)
    
    # Authenticate Bus 1
    auth1 = client.post("/api/driver/auth", json={"bus_id": "HR-02-A-1001", "pin": "1001"})
    assert auth1.status_code == 200
    token1 = auth1.json()["token"]
    
    # Authenticate Bus 2 (HR-02-C-3003)
    auth2 = client.post("/api/driver/auth", json={"bus_id": "HR-02-C-3003", "pin": "3003"})
    assert auth2.status_code == 200
    token2 = auth2.json()["token"]
    
    now = time.time()
    
    # Stream telemetry for both buses concurrently
    with client.websocket_connect(f"/ws/telemetry?token={token1}&bus_id=HR-02-A-1001") as ws1:
        # Initial snapshot
        snap1 = ws1.receive_json()
        assert snap1["event_type"] == "CONNECTION_ESTABLISHED"
        
        with client.websocket_connect(f"/ws/telemetry?token={token2}&bus_id=HR-02-C-3003") as ws2:
            snap2 = ws2.receive_json()
            assert snap2["event_type"] == "CONNECTION_ESTABLISHED"
            
            # Bus 1 sends packet
            ws1.send_json({
                "event_type": "DRIVER_TELEMETRY",
                "bus_id": "HR-02-A-1001",
                "lat": 30.1435,
                "lng": 77.2880,
                "accuracy": 8.0,
                "speed_kmh": 45.0,
                "heading": 85.0,
                "client_timestamp": now
            })
            
            # Bus 2 sends packet
            ws2.send_json({
                "event_type": "DRIVER_TELEMETRY",
                "bus_id": "HR-02-C-3003",
                "lat": 30.2200,
                "lng": 77.1300,
                "accuracy": 12.0,
                "speed_kmh": 50.0,
                "heading": 180.0,
                "client_timestamp": now
            })
            
            # Allow event-loop dispatch
            time.sleep(0.1)
    
    # Verify both buses are in active trips
    assert "HR-02-A-1001" in active_trips
    assert "HR-02-C-3003" in active_trips
    assert active_trips["HR-02-A-1001"]["status"] == "LIVE"
    assert active_trips["HR-02-C-3003"]["status"] == "LIVE"
    
    # Verify both buses appear in GTFS-RT feed
    res_rt = client.get("/api/gtfs-rt/vehicle-positions")
    assert res_rt.status_code == 200
    entities = res_rt.json()["entity"]
    assert len(entities) == 2
    entity_ids = {e["vehicle"]["vehicle"]["id"] for e in entities}
    assert entity_ids == {"HR-02-A-1001", "HR-02-C-3003"}

def test_scaffolding_stubs():
    client = TestClient(app)
    
    res_proto = client.get("/api/gtfs-rt/proto-stub")
    assert res_proto.status_code == 200
    assert res_proto.json()["status"] == "scaffolded"
    
    res_delay = client.post("/api/rider/verify-delay", json={"bus_id": "HR-02-A-1001", "delay_confirmed": True})
    assert res_delay.status_code == 200
    assert res_delay.json()["status"] == "recorded"
