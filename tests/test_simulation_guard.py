"""
Test Simulation Guard: Enforce Real-Only Telemetry by Default & Zero Auto-Simulation
"""
import os
import re
import pytest
from starlette.testclient import TestClient
from server import app, active_trips, SIMULATION_ENABLED

@pytest.fixture
def client():
    return TestClient(app)

def test_server_simulation_disabled_by_default():
    """Verify that server-side simulation flag is False by default."""
    assert SIMULATION_ENABLED is False, "SIMULATION_ENABLED must be False by default"

def test_fleet_starts_empty_without_simulation(client):
    """Verify that active fleet starts empty with 0 active trips on boot."""
    res = client.get("/api/fleet")
    assert res.status_code == 200
    data = res.json()
    assert data["total_active"] == 0
    assert len(data.get("active_trips", [])) == 0
    assert len(data["fleet"]) >= 8

def test_passenger_websocket_sees_no_ghost_buses(client):
    """Verify that a connecting passenger sees an empty active_trips list."""
    with client.websocket_connect("/ws/telemetry") as ws:
        msg = ws.receive_json()
        assert msg["event_type"] == "CONNECTION_ESTABLISHED"
        assert msg["role"] == "PASSENGER"
        assert msg["active_trips"] == []

def test_no_unattended_simulation_timers_in_frontend():
    """
    Static code analysis test:
    Verify that frontend HTML files do NOT contain unattended setInterval loops
    that advance coordinates or trigger dead-reckoning on page load.
    Any setInterval in passenger code must only be for heartbeat or explicit user toggle.
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    passenger_dashboard = os.path.join(repo_root, "stitch_busradar", "search_booking_dashboard", "code.html")
    journey_dashboard = os.path.join(repo_root, "stitch_busradar", "active_journey_dashboard", "code.html")

    assert os.path.exists(passenger_dashboard), f"Missing {passenger_dashboard}"
    assert os.path.exists(journey_dashboard), f"Missing {journey_dashboard}"

    with open(passenger_dashboard, "r", encoding="utf-8") as f:
        passenger_code = f.read()

    with open(journey_dashboard, "r", encoding="utf-8") as f:
        journey_code = f.read()

    # Verify that passenger dashboard does NOT initialize simulation on page load
    assert "let isSimulationMode = false;" in passenger_code, "Simulation mode must default to false"
    assert "WAITING FOR DRIVER" in passenger_code, "Status must display WAITING FOR DRIVER on load"

    # Verify that active journey dashboard does not place premature bus marker
    assert "let busMarker = null;" in journey_code, "Active journey busMarker must start null"
    assert "WAITING FOR DRIVER GPS" in journey_code or "WAITING FOR LIVE GPS" in journey_code

    # Verify that simulation in passenger page is guarded by isSimulationMode check
    sim_matches = re.findall(r"simInterval\s*=\s*setInterval\([^)]+\)", passenger_code)
    for m in sim_matches:
        # Must be inside explicit startSimulationMode function
        assert "startSimulationMode" in passenger_code
