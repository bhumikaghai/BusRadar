"""
Test Driver Authentication, Rate Limiting & Lockout Mechanisms
"""
import pytest
from httpx import AsyncClient, ASGITransport
import time
from server import app, auth_attempts, active_tokens, registered_buses

@pytest.mark.asyncio
async def test_auth_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/driver/auth", json={
            "bus_id": "HR-02-A-1001",
            "pin": "1001",
            "phone": "9876543210"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "authenticated"
        assert "token" in data
        assert data["bus_id"] == "HR-02-A-1001"
        assert data["expires_in"] == 43200
        assert data["token"] in active_tokens

@pytest.mark.asyncio
async def test_auth_invalid_pin():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/driver/auth", json={
            "bus_id": "HR-02-B-2002",
            "pin": "0000"  # Wrong PIN
        })
        assert response.status_code == 401
        data = response.json()
        assert "Invalid Bus ID or PIN" in data["error"]

@pytest.mark.asyncio
async def test_auth_lockout_after_five_failed_attempts():
    # Clear previous attempts
    auth_attempts.clear()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 4 failed attempts
        for i in range(4):
            res = await ac.post("/api/driver/auth", json={
                "bus_id": "HR-02-X-9999",
                "pin": f"wrong{i}"
            })
            assert res.status_code == 401
            assert f"{4 - i} attempt(s) remaining" in res.json()["error"]

        # 5th failed attempt triggers 429 lockout
        res5 = await ac.post("/api/driver/auth", json={
            "bus_id": "HR-02-X-9999",
            "pin": "wrong5"
        })
        assert res5.status_code == 429
        assert "locked for 15 minutes" in res5.json()["error"]

        # Subsequent attempts are blocked immediately
        res_blocked = await ac.post("/api/driver/auth", json={
            "bus_id": "HR-02-X-9999",
            "pin": "9999" # Even correct PIN is blocked during lockout
        })
        assert res_blocked.status_code == 429

@pytest.mark.asyncio
async def test_admin_bus_registration():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Without admin passcode
        unauth = await ac.post("/api/admin/buses", json={
            "bus_id": "HR-02-TEST-777",
            "pin": "7777"
        })
        assert unauth.status_code == 403

        # With valid admin passcode
        auth = await ac.post(
            "/api/admin/buses",
            headers={"X-Admin-Passcode": "BusRadarAdmin2024!"},
            json={
                "bus_id": "HR-02-TEST-777",
                "pin": "7777",
                "route_id": "ynr_mmdu_sh4"
            }
        )
        assert auth.status_code == 200
        assert auth.json()["status"] == "registered"
        assert "HR-02-TEST-777" in registered_buses

        # Authenticate with newly registered bus
        driver_auth = await ac.post("/api/driver/auth", json={
            "bus_id": "HR-02-TEST-777",
            "pin": "7777"
        })
        assert driver_auth.status_code == 200
        assert driver_auth.json()["status"] == "authenticated"
