"""
BusRadar - Real-Time Geospatial Telemetry & Edge-AI Multicast Engine
Team LogiCode | Smart India Hackathon (SIH) Architecture
Corridor: Yamuna Nagar ⇄ MMDU Mullana (Haryana)
"""

import time
import json
import logging
import os
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("BusRadarEngine")

app = FastAPI(
    title="BusRadar Telemetry Hub",
    description="Real-Time Geospatial Multicast, Driver Telemetry & Incident Reporting Engine",
    version="1.4.0"
)

# Full CORS wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Zero-Cache Middleware to kill stale browser caches
@app.middleware("http")
async def add_no_cache_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

SERVER_START_TIME = time.time()

# In-memory fleet state cache with dynamic route details
fleet_registry: Dict[str, Dict[str, Any]] = {
    "HR-02-AB-1234": {
        "bus_id": "HR-02-AB-1234",
        "route": "Yamuna Nagar Bus Stand ⇄ MMDU Campus Gate",
        "route_from": "Yamuna Nagar Bus Stand",
        "route_to": "MMDU Campus Gate",
        "departure_time": "08:30",
        "arrival_time": "09:15",
        "driver": "Authorized Transit Broadcaster",
        "status": "READY",
        "last_lat": 30.1290,
        "last_lng": 77.2674,
        "speed_kmh": 0,
        "delay_minutes": 0,
        "delay_reason": "ON_TIME",
        "last_ping": time.time()
    }
}


class ConnectionManager:
    """Manages full-duplex WebSocket connections and multicasts telemetry packets."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total active: {len(self.active_connections)}")

    async def broadcast(self, data: dict, sender: WebSocket = None):
        """Broadcast JSON payload to all connected clients."""
        payload_str = json.dumps(data)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload_str)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/driver.html", response_class=HTMLResponse)
async def get_driver():
    with open("driver.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/passenger-search.html", response_class=HTMLResponse)
async def get_passenger_search():
    with open("passenger-search.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/health")
async def health_check():
    """REST Health Endpoint returning server uptime, active sockets, and fleet status."""
    uptime = time.time() - SERVER_START_TIME
    return {
        "status": "online",
        "service": "BusRadar-Telemetry-Hub",
        "uptime_seconds": round(uptime, 2),
        "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
        "active_websocket_clients": len(manager.active_connections),
        "fleet_count": len(fleet_registry),
        "active_buses": list(fleet_registry.keys()),
        "server_time_iso": datetime.utcnow().isoformat() + "Z",
        "corridor": "Yamuna Nagar ⇄ MMDU Mullana, Haryana"
    }


@app.get("/api/fleet")
async def get_fleet():
    """Returns the latest telemetry states and incident alerts of all registered transit vehicles."""
    return {
        "fleet": list(fleet_registry.values()),
        "total_active": len(fleet_registry)
    }


@app.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket):
    """
    WebSocket Telemetry & Incident Multicast Endpoint
    Handles real-time GPS stream (DRIVER_TELEMETRY) and active delay propagation (DRIVER_DELAY).
    """
    await manager.connect(websocket)
    
    await websocket.send_text(json.dumps({
        "event_type": "CONNECTION_ESTABLISHED",
        "message": "Connected to BusRadar Telemetry & Incident Hub",
        "active_buses": list(fleet_registry.keys()),
        "fleet_snapshot": list(fleet_registry.values()),
        "timestamp": time.time()
    }))

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                message = json.loads(raw_data)
            except json.JSONDecodeError:
                logger.warning(f"Malformed JSON: {raw_data}")
                continue

            event_type = message.get("event_type", "UNKNOWN")

            if event_type == "DRIVER_TELEMETRY":
                bus_id = message.get("bus_id", "HR-02-AB-1234")
                lat = message.get("lat")
                lng = message.get("lng")
                speed = message.get("speed_kmh", 40)
                route_from = message.get("route_from", "Yamuna Nagar Bus Stand")
                route_to = message.get("route_to", "MMDU Campus Gate")
                dep_time = message.get("departure_time", "08:30")
                arr_time = message.get("arrival_time", "09:15")
                timestamp = message.get("timestamp", time.time())

                # Dynamically register or update vehicle state in fleet registry
                if bus_id not in fleet_registry:
                    fleet_registry[bus_id] = {
                        "bus_id": bus_id,
                        "driver": "Authorized Transit Broadcaster",
                        "delay_minutes": 0,
                        "delay_reason": "ON_TIME"
                    }

                fleet_registry[bus_id].update({
                    "route": f"{route_from} ⇄ {route_to}",
                    "route_from": route_from,
                    "route_to": route_to,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "last_lat": lat,
                    "last_lng": lng,
                    "speed_kmh": speed,
                    "status": "STREAMING",
                    "last_ping": timestamp
                })

                broadcast_packet = {
                    "event_type": "DRIVER_TELEMETRY",
                    "bus_id": bus_id,
                    "route_from": route_from,
                    "route_to": route_to,
                    "departure_time": dep_time,
                    "arrival_time": arr_time,
                    "route": f"{route_from} ⇄ {route_to}",
                    "lat": lat,
                    "lng": lng,
                    "speed_kmh": speed,
                    "timestamp": timestamp,
                    "corridor": "Yamuna Nagar ⇄ MMDU Mullana"
                }
                await manager.broadcast(broadcast_packet)

            elif event_type == "DRIVER_DELAY":
                bus_id = message.get("bus_id", "HR-02-AB-1234")
                delay_minutes = int(message.get("delay_minutes", 0))
                reason = message.get("reason", "Heavy Traffic")
                timestamp = message.get("timestamp", time.time())

                logger.info(f"🚨 INCIDENT REPORTED for {bus_id}: +{delay_minutes}m delay ({reason})")

                if bus_id in fleet_registry:
                    fleet_registry[bus_id]["delay_minutes"] = delay_minutes
                    fleet_registry[bus_id]["delay_reason"] = reason
                    fleet_registry[bus_id]["last_ping"] = timestamp

                delay_packet = {
                    "event_type": "DRIVER_DELAY",
                    "bus_id": bus_id,
                    "delay_minutes": delay_minutes,
                    "reason": reason,
                    "timestamp": timestamp
                }
                await manager.broadcast(delay_packet)

            elif event_type == "PING":
                await websocket.send_text(json.dumps({"event_type": "PONG", "timestamp": time.time()}))

            else:
                await manager.broadcast(message)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
        manager.disconnect(websocket)


# Mount the entire stitch_busradar folder to serve HTML views and assets
if os.path.exists("stitch_busradar"):
    app.mount("/stitch_busradar", StaticFiles(directory="stitch_busradar"), name="stitch_busradar")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting BusRadar Telemetry & Incident Engine on http://0.0.0.0:8000")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
