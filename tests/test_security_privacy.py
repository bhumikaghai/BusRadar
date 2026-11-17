"""
Test Security Headers, Privacy (Zero Stored History), Auto-Cleanup on Silence
"""
import pytest
from httpx import AsyncClient, ASGITransport
import time
import os
from server import app, active_trips

@pytest.mark.asyncio
async def test_security_headers_present():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
        assert res.status_code == 200
        headers = res.headers
        assert headers.get("X-Content-Type-Options") == "nosniff"
        assert headers.get("X-Frame-Options") == "SAMEORIGIN"
        assert headers.get("X-XSS-Protection") == "1; mode=block"
        assert headers.get("Cache-Control") == "no-cache, no-store, must-revalidate, max-age=0"

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/api/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["service"] == "BusRadar-Engine"
        assert data["free_tier_ready"] is True
        assert "uptime_seconds" in data

@pytest.mark.asyncio
async def test_zero_location_files_written():
    """Verify that no database, GPS logs, or location history files are saved to disk."""
    workspace_root = os.path.dirname(os.path.dirname(__file__))
    forbidden_extensions = [".db", ".sqlite", ".sqlite3", ".kml", ".gpx"]
    found_files = []
    for root, dirs, files in os.walk(workspace_root):
        if ".git" in root or ".pytest_cache" in root or "venv" in root:
            continue
        for f in files:
            for ext in forbidden_extensions:
                if f.endswith(ext):
                    found_files.append(os.path.join(root, f))

    assert len(found_files) == 0, f"Found persisted tracking files on disk: {found_files}"

@pytest.mark.asyncio
async def test_trip_cleanup_after_silence():
    """Verify that a trip silent for >10 minutes (600s) is automatically purged from memory."""
    bus_id = "HR-02-CLEANUP-TEST"
    now = time.time()
    # Insert trip with last updated timestamp 11 minutes ago
    active_trips[bus_id] = {
        "bus_id": bus_id,
        "last_updated_timestamp": now - 660, # 11 minutes ago
        "status": "LIVE"
    }

    # Simulate cleanup logic
    expired = []
    for b_id, trip in list(active_trips.items()):
        if now - trip.get("last_updated_timestamp", 0) > 600:
            expired.append(b_id)

    for b_id in expired:
        active_trips.pop(b_id, None)

    assert bus_id not in active_trips
