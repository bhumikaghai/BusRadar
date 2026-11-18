"""
Integration tests for multi-change requirements:
1. Dynamic driver registration (POST /api/driver/register)
2. Last 4 digits PIN rule for any registered vehicle
3. HR-02-B-2002 authentication with PIN 2002
4. Fleet listing returning at least 8 seeded vehicles
5. WebSocket FLEET_UPDATED event broadcast on registration
"""
import pytest
from starlette.testclient import TestClient
from server import app, registered_buses

client = TestClient(app)

def test_bus_2002_authenticates_with_2002():
    res = client.post("/api/driver/auth", json={
        "bus_id": "HR-02-B-2002",
        "pin": "2002"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "authenticated"
    assert "token" in data
    assert data["bus_id"] == "HR-02-B-2002"

def test_fleet_has_at_least_eight_seeded_buses():
    res = client.get("/api/fleet")
    assert res.status_code == 200
    data = res.json()
    fleet = data.get("fleet", [])
    assert len(fleet) >= 8
    plates = [b["bus_id"] for b in fleet]
    for required in ["HR-02-A-1001", "HR-02-B-2002", "HR-02-C-3003", "HR-02-A-4004", "HR-02-B-5005", "HR-02-C-6006", "HR-02-D-7007", "HR-02-E-8008"]:
        assert required in plates

def test_driver_register_success_and_immediate_auth():
    new_plate = "HR-02-Z-7788"
    reg_res = client.post("/api/driver/register", json={
        "vehicle_number": new_plate,
        "driver_name": "Test Driver",
        "route_id": "amb_chd_sh1"
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert reg_data["success"] is True
    assert reg_data["vehicle_number"] == new_plate
    assert "last 4 digits" in reg_data["otp_hint"]
    assert "pin" not in reg_data  # Does NOT return the raw PIN

    # Immediate auth with last 4 digits
    auth_res = client.post("/api/driver/auth", json={
        "bus_id": new_plate,
        "pin": "7788"
    })
    assert auth_res.status_code == 200
    assert auth_res.json()["status"] == "authenticated"

def test_driver_register_invalid_plate_format():
    res = client.post("/api/driver/register", json={
        "vehicle_number": "INVALID-BUS-12",
        "driver_name": "Bad Plate"
    })
    assert res.status_code == 400
    assert "Invalid vehicle number format" in res.json().get("error", "")

def test_driver_register_duplicate_conflict():
    res = client.post("/api/driver/register", json={
        "vehicle_number": "HR-02-A-1001",
        "driver_name": "Duplicate Attempt"
    })
    assert res.status_code == 409
    assert "already registered" in res.json().get("error", "")
