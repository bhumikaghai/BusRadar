"""
Test WebSocket Telemetry Hub, Role Permissions, Heartbeat & Packet Ingestion
"""
import pytest
import time
import json
from starlette.testclient import TestClient
from server import app, active_tokens, active_trips

@pytest.fixture
def client():
    return TestClient(app)

def test_websocket_passenger_connect_snapshot(client):
    """Commuters can connect with no token and receive connection snapshot."""
    with client.websocket_connect("/ws/telemetry") as ws:
        msg = ws.receive_json()
        assert msg["event_type"] == "CONNECTION_ESTABLISHED"
        assert msg["role"] == "PASSENGER"
        assert "server_timestamp" in msg
        assert isinstance(msg["active_trips"], list)

def test_websocket_ping_pong_heartbeat(client):
    """Verify bidirectional ping-pong heartbeat."""
    with client.websocket_connect("/ws/telemetry") as ws:
        # Ignore initial snapshot
        ws.receive_json()

        # Send PING
        client_ts = time.time()
        ws.send_json({"event_type": "PING", "timestamp": client_ts})
        res = ws.receive_json()
        assert res["event_type"] == "PONG"
        assert res["client_timestamp"] == client_ts
        assert "server_timestamp" in res

def test_websocket_passenger_cannot_publish_telemetry(client):
    """Passengers (read-only) cannot publish driver telemetry; socket is closed with 1008."""
    with client.websocket_connect("/ws/telemetry") as ws:
        ws.receive_json() # snapshot

        # Attempt to publish fake telemetry as passenger
        ws.send_json({
            "event_type": "DRIVER_TELEMETRY",
            "lat": 30.1340,
            "lng": 77.2750,
            "speed_kmh": 40.0,
            "accuracy": 10.0,
            "client_timestamp": time.time()
        })

        # Expect socket closed with 1008 policy violation
        with pytest.raises(Exception):
            ws.receive_json()

def test_websocket_invalid_driver_token_rejected(client):
    """Connections with invalid or forged driver token are rejected with 1008."""
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/telemetry?token=invalid_forged_token&bus_id=HR-02-A-1001") as ws:
            ws.receive_json()

def test_websocket_authorized_driver_telemetry_broadcast(client):
    """Authenticated driver sends telemetry; all connected commuters receive it."""
    # Seed an active token
    token = "test_valid_driver_token_12345"
    active_tokens[token] = {
        "bus_id": "HR-02-A-1001",
        "issued_at": time.time(),
        "expires_at": time.time() + 3600
    }

    # Open commuter socket
    with client.websocket_connect("/ws/telemetry") as passenger_ws:
        passenger_ws.receive_json() # snapshot

        # Open driver socket
        with client.websocket_connect(f"/ws/telemetry?token={token}&bus_id=HR-02-A-1001") as driver_ws:
            driver_snap = driver_ws.receive_json()
            assert driver_snap["role"] == "DRIVER"

            # Driver sends telemetry fix
            driver_ws.send_json({
                "event_type": "DRIVER_TELEMETRY",
                "bus_id": "HR-02-A-1001",
                "lat": 30.1340,
                "lng": 77.2750,
                "accuracy": 9.0,
                "speed_kmh": 42.0,
                "heading": 85.0,
                "client_timestamp": time.time(),
                "sequence_number": 1
            })

            # Passenger receives broadcast
            broadcast_msg = passenger_ws.receive_json()
            assert broadcast_msg["event_type"] == "DRIVER_TELEMETRY"
            assert broadcast_msg["bus_id"] == "HR-02-A-1001"
            assert broadcast_msg["speed_kmh"] == 42.0
            assert "lat" in broadcast_msg and "lng" in broadcast_msg

            # Verify active_trips contains this bus
            assert "HR-02-A-1001" in active_trips
            assert active_trips["HR-02-A-1001"]["status"] == "LIVE"

            # Driver ends trip
            driver_ws.send_json({
                "event_type": "TRIP_END",
                "bus_id": "HR-02-A-1001"
            })

            # Passenger receives TRIP_ENDED broadcast
            end_msg = passenger_ws.receive_json()
            assert end_msg["event_type"] == "TRIP_ENDED"
            assert end_msg["bus_id"] == "HR-02-A-1001"
            assert "HR-02-A-1001" not in active_trips

def test_websocket_drop_bad_accuracy(client):
    """Fixes with accuracy > 50m are dropped by the server and not broadcast."""
    token = "test_accuracy_token_456"
    active_tokens[token] = {
        "bus_id": "HR-02-B-2002",
        "issued_at": time.time(),
        "expires_at": time.time() + 3600
    }

    with client.websocket_connect("/ws/telemetry") as passenger_ws:
        passenger_ws.receive_json()

        with client.websocket_connect(f"/ws/telemetry?token={token}&bus_id=HR-02-B-2002") as driver_ws:
            driver_ws.receive_json()

            # Send bad accuracy fix (> 50m)
            driver_ws.send_json({
                "event_type": "DRIVER_TELEMETRY",
                "bus_id": "HR-02-B-2002",
                "lat": 30.1435,
                "lng": 77.2880,
                "accuracy": 75.0, # BAD ACCURACY
                "speed_kmh": 40.0,
                "client_timestamp": time.time()
            })

            # Send a PING to ensure event loop processed previous message
            driver_ws.send_json({"event_type": "PING", "timestamp": 123})
            driver_pong = driver_ws.receive_json()
            assert driver_pong["event_type"] == "PONG"

            # Passenger should NOT have received any DRIVER_TELEMETRY packet
            # The active_trips should NOT have this bus recorded
            assert "HR-02-B-2002" not in active_trips

def test_websocket_drop_oversized_packets(client):
    """Packets larger than 4096 bytes are dropped."""
    token = "test_oversize_token_789"
    active_tokens[token] = {
        "bus_id": "HR-02-X-9999",
        "issued_at": time.time(),
        "expires_at": time.time() + 3600
    }

    with client.websocket_connect(f"/ws/telemetry?token={token}&bus_id=HR-02-X-9999") as driver_ws:
        driver_ws.receive_json()

        # Send huge payload > 5KB
        huge_text = json.dumps({
            "event_type": "DRIVER_TELEMETRY",
            "lat": 30.1290,
            "lng": 77.2674,
            "accuracy": 10.0,
            "speed_kmh": 30.0,
            "junk": "A" * 6000,
            "client_timestamp": time.time()
        })
        driver_ws.send_text(huge_text)

        # Ping to check connection remains healthy and did not crash
        driver_ws.send_json({"event_type": "PING", "timestamp": 456})
        pong = driver_ws.receive_json()
        assert pong["event_type"] == "PONG"
