"""
BusRadar - Field-Ready Real-Time Transit Telemetry Engine
Zero-cost, Zero-key architecture designed for Render Free Tier & Edge Commuter Devices.
Corridor: Yamuna Nagar Stand ⇄ MMDU Campus Gate (Haryana State Highway 4)
"""

import os
import time
import json
import math
import uuid
import hmac
import hashlib
import asyncio
import logging
import html
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Query, Header, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Configure logging (STRICT PRIVACY: coordinates and phone numbers are never logged to console or disk)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (%(name)s) %(message)s"
)
logger = logging.getLogger("BusRadar")

# Environment configuration
DRIVER_SIGNING_SECRET = os.getenv("DRIVER_SIGNING_SECRET", "busradar_field_secret_key_change_me_in_render")
ADMIN_PASSCODE = os.getenv("ADMIN_PASSCODE", "BusRadarAdmin2024!")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
SIMULATION_ENABLED = os.getenv("SIMULATION_ENABLED", "false").lower() in ("true", "1", "yes")
SERVER_START_TIME = time.time()

# Background task: Clean up inactive trips (>10 minutes silence) for privacy & memory safety
async def periodic_trip_cleanup_task():
    while True:
        await asyncio.sleep(15)
        now = time.time()
        expired_buses = []
        for bus_id, trip in list(active_trips.items()):
            if now - trip.get("last_updated_timestamp", 0) > 600: # 10 minutes silence
                expired_buses.append(bus_id)

        for bus_id in expired_buses:
            logger.info(f"Trip for bus {bus_id} expired after 10m silence. Removing from active state.")
            active_trips.pop(bus_id, None)
            await manager.broadcast({
                "event_type": "TRIP_ENDED",
                "bus_id": bus_id,
                "reason": "EXPIRED_AFTER_SILENCE",
                "server_timestamp": now
            })

@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_task = asyncio.create_task(periodic_trip_cleanup_task())
    yield
    cleanup_task.cancel()

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="BusRadar Transit Engine",
    description="Real-time live bus tracking & incident multicast hub for municipal transit",
    version="2.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
origins = [o.strip() for o in ALLOWED_ORIGIN.split(",") if o.strip()]
if "*" in origins or not origins:
    allow_origins = ["*"]
else:
    allow_origins = origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security and Zero-Cache Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Never cache dynamic HTML or API responses
    if not request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# ==============================================================================
# IN-MEMORY STATE & REGISTRIES (Ephemeral-Disk Safe)
# ==============================================================================

# Authorized fleet registry: pre-configured buses & PIN hashes for field operation
# Password hashes created via SHA-256 with salt
def _hash_pin(pin: str) -> str:
    return hashlib.sha256((pin + "busradar_salt_2024").encode()).hexdigest()

registered_buses: Dict[str, Dict[str, Any]] = {
    "HR-02-A-1001": {
        "bus_id": "HR-02-A-1001",
        "pin_hash": _hash_pin("1001"),
        "route_id": "ynr_mmdu_sh4",
        "route_name": "Yamuna Nagar Stand ⇄ MMDU Campus Gate"
    },
    "HR-02-B-2002": {
        "bus_id": "HR-02-B-2002",
        "pin_hash": _hash_pin("2002"),
        "route_id": "ynr_mmdu_sh4",
        "route_name": "Yamuna Nagar Stand ⇄ MMDU Campus Gate"
    },
    "HR-02-X-9999": {
        "bus_id": "HR-02-X-9999",
        "pin_hash": _hash_pin("9999"),
        "route_id": "ynr_mmdu_sh4",
        "route_name": "Yamuna Nagar Stand ⇄ MMDU Campus Gate"
    }
}

# Live active trips: keyed by bus_id. Empty on boot (no simulated fake buses)
active_trips: Dict[str, Dict[str, Any]] = {}

# Active driver tokens: token -> {bus_id, issued_at, expires_at}
active_tokens: Dict[str, Dict[str, Any]] = {}

# Failed login attempts for rate-limiting: key -> {failed_count, locked_until}
auth_attempts: Dict[str, Dict[str, Any]] = {}

# In-memory route store: preloaded with default route
routes_db: Dict[str, Dict[str, Any]] = {}

def load_default_routes():
    route_file = os.path.join(os.path.dirname(__file__), "routes", "default_route.json")
    if os.path.exists(route_file):
        try:
            with open(route_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                routes_db[data["route_id"]] = data
                logger.info(f"Loaded default route: {data['route_id']} ({len(data['polyline'])} polyline nodes)")
        except Exception as e:
            logger.error(f"Failed to load default route: {e}")

load_default_routes()

# ==============================================================================
# GEOSPATIAL & MAP-MATCHING ALGORITHMS
# ==============================================================================

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def point_to_segment_projection(p: Tuple[float, float], a: Tuple[float, float], b: Tuple[float, float]) -> Tuple[float, float, float]:
    """Projects point p onto segment a-b. Returns (proj_lat, proj_lng, distance_meters)."""
    ax, ay = a[1], a[0]
    bx, by = b[1], b[0]
    px, py = p[1], p[0]

    dx = bx - ax
    dy = by - ay
    seg_len_sq = dx * dx + dy * dy

    if seg_len_sq == 0:
        proj = (ay, ax)
    else:
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
        proj = (ay + t * dy, ax + t * dx)

    dist = haversine_distance_meters(p[0], p[1], proj[0], proj[1])
    return (proj[0], proj[1], dist)

def snap_to_route_polyline(lat: float, lng: float, polyline: List[List[float]]) -> Tuple[float, float, float]:
    """Finds nearest segment projection along polyline. Returns (snapped_lat, snapped_lng, dist_to_segment)."""
    if not polyline:
        return (lat, lng, 0.0)
    if len(polyline) == 1:
        return (polyline[0][0], polyline[0][1], haversine_distance_meters(lat, lng, polyline[0][0], polyline[0][1]))

    min_dist = float("inf")
    best_proj = (lat, lng)

    for i in range(len(polyline) - 1):
        a = (polyline[i][0], polyline[i][1])
        b = (polyline[i + 1][0], polyline[i + 1][1])
        proj_lat, proj_lng, dist = point_to_segment_projection((lat, lng), a, b)
        if dist < min_dist:
            min_dist = dist
            best_proj = (proj_lat, proj_lng)

    return (best_proj[0], best_proj[1], min_dist)

def ramer_douglas_peucker(coords: List[List[float]], epsilon: float) -> List[List[float]]:
    """Simplifies polyline coordinates within epsilon tolerance (degrees)."""
    if len(coords) < 3:
        return coords

    dmax = 0.0
    index = 0
    end = len(coords) - 1

    # Line from start to end
    x1, y1 = coords[0][1], coords[0][0]
    x2, y2 = coords[end][1], coords[end][0]
    line_len = math.hypot(x2 - x1, y2 - y1)

    for i in range(1, end):
        px, py = coords[i][1], coords[i][0]
        if line_len == 0:
            d = math.hypot(px - x1, py - y1)
        else:
            d = abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) / line_len
        if d > dmax:
            index = i
            dmax = d

    if dmax > epsilon:
        rec_results1 = ramer_douglas_peucker(coords[:index + 1], epsilon)
        rec_results2 = ramer_douglas_peucker(coords[index:], epsilon)
        return rec_results1[:-1] + rec_results2
    else:
        return [coords[0], coords[end]]

# ==============================================================================
# PYDANTIC VALIDATION SCHEMAS
# ==============================================================================

class DriverAuthRequest(BaseModel):
    bus_id: str = Field(..., min_length=3, max_length=30)
    pin: str = Field(..., min_length=4, max_length=10)
    phone: Optional[str] = Field(default=None, max_length=15)

    @field_validator("bus_id", mode="before")
    @classmethod
    def sanitize_bus_id(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip().upper())
        return v

class DriverTelemetrySchema(BaseModel):
    event_type: str = Field(default="DRIVER_TELEMETRY")
    bus_id: str = Field(..., min_length=3, max_length=100)
    lat: float = Field(..., ge=27.0, le=33.0)      # North India bounding box
    lng: float = Field(..., ge=74.0, le=80.0)
    accuracy: float = Field(..., ge=0.0, le=1000.0) # Accuracy in meters
    speed_kmh: float = Field(..., ge=0.0, le=130.0)
    heading: Optional[float] = Field(default=0.0, ge=0.0, le=360.0)
    client_timestamp: float = Field(...)
    sequence_number: Optional[int] = Field(default=0)
    is_simulation: Optional[bool] = Field(default=False)
    route_from: Optional[str] = Field(default="Yamuna Nagar Bus Stand", max_length=100)
    route_to: Optional[str] = Field(default="MMDU Campus Gate", max_length=100)

    @field_validator("bus_id", "route_from", "route_to", mode="before")
    @classmethod
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip())
        return v

class DriverDelaySchema(BaseModel):
    event_type: str = Field(default="DRIVER_DELAY")
    bus_id: str = Field(..., min_length=3, max_length=30)
    delay_minutes: int = Field(..., ge=0, le=180)
    reason: str = Field(default="Traffic Delay", max_length=120)
    client_timestamp: Optional[float] = None

    @field_validator("bus_id", "reason", mode="before")
    @classmethod
    def sanitize_delay(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip())
        return v

class RouteSaveRequest(BaseModel):
    route_id: str = Field(..., min_length=3, max_length=50)
    route_name: str = Field(..., min_length=3, max_length=100)
    corridor: Optional[str] = Field(default="", max_length=100)
    polyline: List[List[float]] = Field(..., min_length=2)
    stops: Optional[List[Dict[str, Any]]] = Field(default=[])

    @field_validator("route_id", "route_name", "corridor", mode="before")
    @classmethod
    def sanitize_route(cls, v):
        if isinstance(v, str):
            return html.escape(v.strip())
        return v

# ==============================================================================
# WEBSOCKET CONNECTION & MULTICAST ENGINE
# ==============================================================================

class ConnectionManager:
    """Non-blocking concurrent multicast manager with dead-socket culling."""
    def __init__(self):
        # Maps websocket -> {"role": "DRIVER"|"PASSENGER", "bus_id": str|None, "last_active": float}
        self.connections: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, role: str = "PASSENGER", bus_id: Optional[str] = None):
        await websocket.accept()
        self.connections[websocket] = {
            "role": role,
            "bus_id": bus_id,
            "last_active": time.time(),
            "msg_count": 0,
            "window_start": time.time()
        }
        logger.info(f"Client connected ({role}). Total active sockets: {len(self.connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            info = self.connections.pop(websocket)
            logger.info(f"Client disconnected ({info.get('role')}). Active sockets: {len(self.connections)}")

    async def _safe_send(self, ws: WebSocket, message: dict):
        try:
            await asyncio.wait_for(ws.send_json(message), timeout=0.25)
        except (asyncio.TimeoutError, WebSocketDisconnect, Exception):
            self.disconnect(ws)

    async def broadcast(self, data: dict):
        """Concurrently multicasts to all active WebSocket clients."""
        if not self.connections:
            return
        tasks = [asyncio.create_task(self._safe_send(ws, data)) for ws in list(self.connections.keys())]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

manager = ConnectionManager()

# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

# Static & PWA Root Routes
@app.get("/", response_class=HTMLResponse)
async def get_index():
    return FileResponse("index.html")

@app.get("/driver.html", response_class=HTMLResponse)
async def get_driver():
    return FileResponse("driver.html")

@app.get("/passenger-search.html", response_class=HTMLResponse)
async def get_passenger_search():
    return FileResponse("passenger-search.html")

@app.get("/manifest.json")
async def get_manifest():
    return FileResponse("static/manifest.json", media_type="application/manifest+json")

@app.get("/sw.js")
async def get_sw():
    return FileResponse("static/sw.js", media_type="application/javascript")

# Health Endpoint (Lightweight for cron-job.org or monitoring)
@app.get("/api/health")
@limiter.limit("120/minute")
async def health_check(request: Request):
    uptime = round(time.time() - SERVER_START_TIME, 1)
    return {
        "status": "healthy",
        "service": "BusRadar-Engine",
        "version": "2.0.0",
        "uptime_seconds": uptime,
        "active_trips_count": len(active_trips),
        "active_connections": len(manager.connections),
        "timestamp": time.time(),
        "free_tier_ready": True
    }

# Driver Authentication (Server-Side PIN & Rate-Limited Lockout)
@app.post("/api/driver/auth")
@limiter.limit("30/minute")
async def driver_auth_endpoint(request: Request, auth_req: DriverAuthRequest):
    client_ip = request.client.host if request.client else "unknown"
    lock_key = f"{client_ip}:{auth_req.bus_id}"
    now = time.time()

    # Check lockout
    attempt = auth_attempts.get(lock_key, {"failed_count": 0, "locked_until": 0})
    if attempt["locked_until"] > now:
        remaining_lock = int(attempt["locked_until"] - now)
        return JSONResponse(
            status_code=429,
            content={"error": f"Account temporarily locked due to 5 failed attempts. Please try again in {remaining_lock} seconds."}
        )

    # Validate against registered bus credentials
    bus_info = registered_buses.get(auth_req.bus_id)
    pin_hash = _hash_pin(auth_req.pin)

    if not bus_info or bus_info.get("pin_hash") != pin_hash:
        attempt["failed_count"] += 1
        if attempt["failed_count"] >= 5:
            attempt["locked_until"] = now + 900 # 15 minute lockout
            auth_attempts[lock_key] = attempt
            return JSONResponse(
                status_code=429,
                content={"error": "Too many failed attempts. Driver access locked for 15 minutes."}
            )
        auth_attempts[lock_key] = attempt
        remaining = 5 - attempt["failed_count"]
        return JSONResponse(
            status_code=401,
            content={"error": f"Invalid Bus ID or PIN. {remaining} attempt(s) remaining."}
        )

    # Reset failed attempts on success
    auth_attempts[lock_key] = {"failed_count": 0, "locked_until": 0}

    # Issue signed session token (HMAC-SHA256)
    token = hmac.new(
        DRIVER_SIGNING_SECRET.encode(),
        f"{auth_req.bus_id}:{now}:{uuid.uuid4().hex}".encode(),
        hashlib.sha256
    ).hexdigest()

    active_tokens[token] = {
        "bus_id": auth_req.bus_id,
        "issued_at": now,
        "expires_at": now + 43200 # 12 hours validity
    }

    return {
        "status": "authenticated",
        "token": token,
        "bus_id": auth_req.bus_id,
        "route_id": bus_info.get("route_id", "ynr_mmdu_sh4"),
        "route_name": bus_info.get("route_name", "Yamuna Nagar Stand ⇄ MMDU Campus Gate"),
        "expires_in": 43200
    }

# Fleet Endpoint (Returns current live trips on the road)
@app.get("/api/fleet")
async def get_fleet():
    now = time.time()
    fleet_list = []
    for trip in active_trips.values():
        age = now - trip.get("last_updated_timestamp", now)
        status_label = "LIVE" if age < 10 else ("WEAK_SIGNAL" if age < 30 else "LAST_SEEN")
        trip_copy = dict(trip)
        trip_copy["status_label"] = status_label
        trip_copy["age_seconds"] = round(age, 1)
        fleet_list.append(trip_copy)

    return {
        "fleet": fleet_list,
        "total_active": len(fleet_list)
    }

# Routes Retrieval & Management Endpoints
@app.get("/api/routes")
async def list_routes():
    routes_summary = []
    for r_id, r_data in routes_db.items():
        routes_summary.append({
            "route_id": r_id,
            "route_name": r_data.get("route_name"),
            "corridor": r_data.get("corridor"),
            "origin": r_data.get("origin"),
            "destination": r_data.get("destination"),
            "total_distance_km": r_data.get("total_distance_km"),
            "stops_count": len(r_data.get("stops", []))
        })
    return {"routes": routes_summary}

@app.get("/api/routes/{route_id}")
async def get_route_details(route_id: str):
    if route_id not in routes_db:
        return JSONResponse(status_code=404, content={"error": "Route not found"})
    return routes_db[route_id]

@app.post("/api/routes/save")
async def save_recorded_route(
    route_req: RouteSaveRequest,
    x_admin_passcode: Optional[str] = Header(None),
    x_driver_token: Optional[str] = Header(None)
):
    # Verify either admin passcode or active driver session
    is_admin = x_admin_passcode == ADMIN_PASSCODE
    is_driver = x_driver_token in active_tokens and active_tokens[x_driver_token]["expires_at"] > time.time()
    if not (is_admin or is_driver):
        return JSONResponse(status_code=403, content={"error": "Unauthorized to save route. Valid driver or admin credentials required."})

    # Simplify polyline with RDP algorithm (~5 meter tolerance in degrees)
    simplified_polyline = ramer_douglas_peucker(route_req.polyline, epsilon=0.00005)

    route_data = {
        "route_id": route_req.route_id,
        "route_name": route_req.route_name,
        "corridor": route_req.corridor,
        "origin": route_req.stops[0]["name"] if route_req.stops else "Origin",
        "destination": route_req.stops[-1]["name"] if route_req.stops else "Destination",
        "total_distance_km": round(len(simplified_polyline) * 0.1, 1),
        "stops": route_req.stops or [],
        "polyline": simplified_polyline,
        "recorded_at_iso": datetime.utcnow().isoformat() + "Z"
    }
    routes_db[route_req.route_id] = route_data
    logger.info(f"Saved route {route_req.route_id} with {len(simplified_polyline)} points (reduced from {len(route_req.polyline)})")
    return {
        "status": "saved",
        "route_id": route_req.route_id,
        "original_nodes": len(route_req.polyline),
        "simplified_nodes": len(simplified_polyline)
    }

# Admin endpoint to register or update bus credentials
@app.post("/api/admin/buses")
async def register_bus_admin(
    payload: Dict[str, Any],
    x_admin_passcode: Optional[str] = Header(None)
):
    if x_admin_passcode != ADMIN_PASSCODE:
        return JSONResponse(status_code=403, content={"error": "Invalid admin passcode"})

    bus_id = html.escape(str(payload.get("bus_id", "")).strip().upper())
    pin = str(payload.get("pin", "")).strip()
    route_id = str(payload.get("route_id", "ynr_mmdu_sh4")).strip()

    if not bus_id or len(pin) < 4:
        return JSONResponse(status_code=400, content={"error": "bus_id and pin (min 4 digits) required"})

    registered_buses[bus_id] = {
        "bus_id": bus_id,
        "pin_hash": _hash_pin(pin),
        "route_id": route_id,
        "route_name": routes_db.get(route_id, {}).get("route_name", "Transit Route")
    }
    logger.info(f"Admin registered bus credentials for {bus_id}")
    return {"status": "registered", "bus_id": bus_id, "route_id": route_id}

# Urban Transit Analytics Endpoint
@app.get("/api/urban-analytics")
@limiter.limit("60/minute")
async def get_urban_analytics(request: Request):
    active_buses = list(active_trips.values())
    total_active = len(active_buses)
    speeds = [b.get("speed_kmh", 0) for b in active_buses if b.get("speed_kmh", 0) > 0]
    avg_speed = round(sum(speeds) / len(speeds), 1) if speeds else 0.0
    delays = [b.get("delay_minutes", 0) for b in active_buses]
    total_delay = sum(delays)

    return {
        "timestamp_iso": datetime.utcnow().isoformat() + "Z",
        "corridor": "Yamuna Nagar Stand ⇄ MMDU Campus Gate",
        "active_fleet_count": total_active,
        "average_fleet_speed_kmh": avg_speed,
        "total_cumulative_delay_mins": total_delay,
        "congestion_status": "Free Flow" if total_delay == 0 else ("Moderate" if total_delay <= 10 else "Heavy Delay")
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    icon_path = os.path.join("static", "icons", "icon-192.svg")
    if os.path.exists(icon_path):
        return FileResponse(icon_path, media_type="image/svg+xml")
    return Response(status_code=204)

# ==============================================================================
# WEBSOCKET TELEMETRY & INCIDENT GATEWAY
# ==============================================================================

@app.websocket("/ws/telemetry")
async def telemetry_websocket(websocket: WebSocket, token: Optional[str] = Query(None), bus_id: Optional[str] = Query(None)):
    """
    Full-duplex WebSocket Telemetry Gateway:
    - Drivers authenticate via token parameter and are granted publish rights for their specific bus.
    - Commuters connect without a token and operate in read-only subscription mode.
    """
    role = "PASSENGER"
    auth_bus_id = None

    if token:
        token_info = active_tokens.get(token)
        if token_info and token_info["expires_at"] > time.time():
            role = "DRIVER"
            auth_bus_id = token_info["bus_id"]
        else:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await manager.connect(websocket, role=role, bus_id=auth_bus_id)

    # Send initial state snapshot on connect
    await websocket.send_json({
        "event_type": "CONNECTION_ESTABLISHED",
        "role": role,
        "bus_id": auth_bus_id,
        "server_timestamp": time.time(),
        "active_trips": list(active_trips.values())
    })

    try:
        while True:
            raw_text = await websocket.receive_text()

            # Guard: Size-limit incoming message (drop >4KB)
            if len(raw_text) > 4096:
                logger.warning("Dropped oversized WebSocket packet (>4096 bytes)")
                continue

            # Guard: Rate-limit publisher (max 5 msgs/sec)
            client_meta = manager.connections.get(websocket)
            if client_meta:
                now_t = time.time()
                if now_t - client_meta["window_start"] > 1.0:
                    client_meta["window_start"] = now_t
                    client_meta["msg_count"] = 0
                client_meta["msg_count"] += 1
                if client_meta["msg_count"] > 5:
                    logger.warning("WebSocket client exceeded 5 msg/sec rate limit")
                    continue

            try:
                data = json.loads(raw_text)
            except json.JSONDecodeError:
                continue

            event_type = data.get("event_type", "")

            # Heartbeat ping/pong
            if event_type == "PING":
                await websocket.send_json({
                    "event_type": "PONG",
                    "client_timestamp": data.get("timestamp"),
                    "server_timestamp": time.time()
                })
                continue

            # READ-ONLY ENFORCEMENT: Passengers cannot publish telemetry, delays, or trip actions
            if role != "DRIVER":
                logger.warning(f"Unauthorized event '{event_type}' attempted by read-only client")
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                manager.disconnect(websocket)
                return

            # Handle Driver Telemetry
            if event_type == "DRIVER_TELEMETRY":
                # Ensure bus_id matches authenticated session
                data["bus_id"] = auth_bus_id

                try:
                    payload = DriverTelemetrySchema(**data)
                except ValidationError as ve:
                    logger.warning(f"Invalid telemetry schema from {auth_bus_id}: {ve}")
                    continue

                # Filter bad GPS fixes: drop if accuracy > 50 meters
                if payload.accuracy > 50.0:
                    logger.info(f"Dropped poor accuracy fix ({payload.accuracy}m > 50m) for {auth_bus_id}")
                    continue

                # Check velocity jump: drop if implied speed > 120 km/h from last fix
                prev_trip = active_trips.get(auth_bus_id)
                now_ts = time.time()

                if prev_trip and prev_trip.get("last_raw_lat"):
                    dt = now_ts - prev_trip.get("last_updated_timestamp", now_ts)
                    if dt <= 0: # Drop duplicate or backwards timestamps
                        continue
                    jump_dist = haversine_distance_meters(
                        prev_trip["last_raw_lat"], prev_trip["last_raw_lng"],
                        payload.lat, payload.lng
                    )
                    implied_speed_kmh = (jump_dist / dt) * 3.6
                    if implied_speed_kmh > 120.0 and jump_dist > 100.0:
                        logger.warning(f"Dropped impossible GPS teleportation jump ({implied_speed_kmh:.1f} km/h) for {auth_bus_id}")
                        continue

                # Snap coordinates to recorded route polyline
                route_data = routes_db.get(prev_trip.get("route_id", "ynr_mmdu_sh4") if prev_trip else "ynr_mmdu_sh4")
                polyline = route_data.get("polyline", []) if route_data else []
                snapped_lat, snapped_lng, dist_to_segment = snap_to_route_polyline(payload.lat, payload.lng, polyline)

                # Update in-memory active trip state
                trip_record = active_trips.get(auth_bus_id, {
                    "bus_id": auth_bus_id,
                    "route_id": "ynr_mmdu_sh4",
                    "route_name": route_data.get("route_name", "Yamuna Nagar Stand ⇄ MMDU Campus Gate") if route_data else "Yamuna Nagar Stand ⇄ MMDU Campus Gate",
                    "route_from": payload.route_from,
                    "route_to": payload.route_to,
                    "delay_minutes": 0,
                    "delay_reason": "ON_TIME",
                    "started_at": now_ts
                })

                trip_record.update({
                    "last_raw_lat": payload.lat,
                    "last_raw_lng": payload.lng,
                    "lat": snapped_lat,
                    "lng": snapped_lng,
                    "accuracy": payload.accuracy,
                    "speed_kmh": payload.speed_kmh,
                    "heading": payload.heading,
                    "sequence_number": payload.sequence_number,
                    "is_simulation": bool(payload.is_simulation),
                    "last_updated_timestamp": now_ts,
                    "status": "LIVE"
                })
                active_trips[auth_bus_id] = trip_record

                # Broadcast live telemetry packet to all connected commuter clients
                broadcast_packet = {
                    "event_type": "DRIVER_TELEMETRY",
                    "bus_id": auth_bus_id,
                    "route_id": trip_record.get("route_id"),
                    "route_from": trip_record.get("route_from"),
                    "route_to": trip_record.get("route_to"),
                    "lat": snapped_lat,
                    "lng": snapped_lng,
                    "raw_lat": payload.lat,
                    "raw_lng": payload.lng,
                    "accuracy": payload.accuracy,
                    "speed_kmh": payload.speed_kmh,
                    "heading": payload.heading,
                    "is_simulation": bool(payload.is_simulation),
                    "delay_minutes": trip_record.get("delay_minutes", 0),
                    "delay_reason": trip_record.get("delay_reason", "ON_TIME"),
                    "sequence_number": payload.sequence_number,
                    "client_timestamp": payload.client_timestamp,
                    "server_timestamp": now_ts
                }
                await manager.broadcast(broadcast_packet)

            # Handle Driver Delay & Incident Reporting
            elif event_type == "DRIVER_DELAY":
                data["bus_id"] = auth_bus_id
                try:
                    payload = DriverDelaySchema(**data)
                except ValidationError as ve:
                    logger.warning(f"Invalid delay payload from {auth_bus_id}: {ve}")
                    continue

                if auth_bus_id in active_trips:
                    active_trips[auth_bus_id]["delay_minutes"] = payload.delay_minutes
                    active_trips[auth_bus_id]["delay_reason"] = payload.reason
                    active_trips[auth_bus_id]["last_updated_timestamp"] = time.time()

                await manager.broadcast({
                    "event_type": "DRIVER_DELAY",
                    "bus_id": auth_bus_id,
                    "delay_minutes": payload.delay_minutes,
                    "reason": payload.reason,
                    "server_timestamp": time.time()
                })

            # Handle Trip End
            elif event_type == "TRIP_END":
                logger.info(f"Driver ended trip for {auth_bus_id}")
                active_trips.pop(auth_bus_id, None)
                await manager.broadcast({
                    "event_type": "TRIP_ENDED",
                    "bus_id": auth_bus_id,
                    "server_timestamp": time.time()
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket session error: {e}")
        manager.disconnect(websocket)

# Mount static files and UI dashboards
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("stitch_busradar"):
    app.mount("/stitch_busradar", StaticFiles(directory="stitch_busradar"), name="stitch_busradar")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting BusRadar Transit Engine on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
