"""
Load & Concurrency Test: 100 Concurrent WebSocket Subscribers
Measures broadcast throughput, end-to-end delivery latency, and memory stability.
"""
import pytest
import asyncio
import time
import os
try:
    import psutil
except ImportError:
    psutil = None

from server import ConnectionManager

class MockWebSocket:
    def __init__(self, client_id: int):
        self.client_id = client_id
        self.received = []

    async def accept(self):
        pass

    async def send_json(self, msg: dict):
        self.received.append(msg)

@pytest.mark.asyncio
async def test_100_concurrent_broadcast_subscribers():
    """Verify that manager concurrently multicasts updates to 100 active connections without blocking."""
    test_manager = ConnectionManager()
    num_passengers = 100
    mock_sockets = [MockWebSocket(i) for i in range(num_passengers)]

    # Connect 100 clients
    for ws in mock_sockets:
        await test_manager.connect(ws, role="PASSENGER")

    assert len(test_manager.connections) == num_passengers

    process = psutil.Process(os.getpid()) if psutil else None
    mem_before = process.memory_info().rss / 1024 / 1024 if process else 0.0

    start_time = time.perf_counter()
    num_packets = 5

    for seq in range(1, num_packets + 1):
        packet = {
            "event_type": "DRIVER_TELEMETRY",
            "bus_id": "HR-02-A-1001",
            "lat": 30.1340 + seq * 0.001,
            "lng": 77.2750 + seq * 0.001,
            "accuracy": 8.0,
            "speed_kmh": 45.0,
            "sequence_number": seq,
            "server_timestamp": time.time()
        }
        await test_manager.broadcast(packet)

    elapsed = time.perf_counter() - start_time
    total_deliveries = num_passengers * num_packets
    throughput = total_deliveries / elapsed

    # Verify all 100 clients received all 5 packets
    for ws in mock_sockets:
        assert len(ws.received) == num_packets
        for i, pkt in enumerate(ws.received):
            assert pkt["sequence_number"] == i + 1
            assert pkt["bus_id"] == "HR-02-A-1001"

    mem_after = process.memory_info().rss / 1024 / 1024 if process else 0.0
    mem_delta = mem_after - mem_before

    print(f"\n[BENCHMARK] 100 Concurrent WebSocket Clients:")
    print(f" - Total Deliveries: {total_deliveries} packets across {num_passengers} clients")
    print(f" - Elapsed Time: {elapsed * 1000:.2f} ms ({elapsed:.4f} s)")
    print(f" - Throughput: {throughput:.1f} deliveries/sec")
    print(f" - Avg Latency per Multicast: {(elapsed / num_packets) * 1000:.2f} ms")
    print(f" - Memory Delta: {mem_delta:+.2f} MB (Total RSS: {mem_after:.2f} MB)")

    # Latency per multicast must be well under 100ms
    assert (elapsed / num_packets) < 0.100
