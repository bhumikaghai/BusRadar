# BusRadar - Production Readiness & Architectural Hardening Plan
**Document Version:** 1.0.0 (Overnight Autonomous Run)  
**Target:** SIH26205 / Haryana State Transport Real-Time Telemetry Corridor  
**Base Repository:** FastAPI + WebSockets + Leaflet Vanilla JS  

---

## 1. Current-State Audit (Deep Research - Step 2)

### 1.1 End-to-End Operational Baseline
BusRadar currently operates as a lightweight, zero-cost, in-memory real-time transit telemetry system tailored for Haryana State Highway 4 (`Yamuna Nagar Stand ⇄ MMDU Campus Gate`, 28.4 km corridor). The backend is built with FastAPI (`server.py`) using Python 3.11+, maintaining ephemeral state in memory (`registered_buses`, `active_trips`, `active_tokens`, `routes_db`). Drivers authenticate via a 4-digit PIN against SHA-256 salted hashes (`/api/driver/auth`), receiving an HMAC-SHA256 signed session token (12-hour validity) subject to a 5-attempt rate-limiting lockout (15 minutes). Authenticated drivers stream GPS telemetry via a full-duplex WebSocket (`/ws/telemetry?token=...&bus_id=...`) with client-side screen wake-locks, 25-second keep-alive pings, and exponential reconnection backoff. The ingestion pipeline filters inaccurate GPS fixes (>50m dropped), drops velocity anomalies (>120 km/h jump dropped), snaps coordinates to the highway route polyline using segment vector projection (`point_to_segment_projection`), simplifies polyline data using the Ramer-Douglas-Peucker (RDP) algorithm, and multicasts updates concurrently to connected commuter WebSockets via non-blocking tasks (`asyncio.wait_for` with 250ms timeouts) while culling dead sockets. Commuters view vehicles on a Leaflet map (`passenger-search.html` / `search_booking_dashboard/code.html`) with 60fps dead-reckoning linear interpolation (LERP), real-time ETA recalculations across 7 designated stops, and explicit delay/incident alerts.

### 1.2 Demo / Simulation Shortcuts Audit
Every occurrence of demo, simulation, and timer shortcuts identified across the codebase:
1. `stitch_busradar/search_booking_dashboard/code.html` (Line 184–190, Line 584–668): Indoor Demo Simulation mode with `simInterval = setInterval(...)` stepping through highway waypoints every 1.5s; strictly gated behind an explicit `[Demo Simulation: OFF]` button, confirmation dialog, and purple `⚠️ SIMULATION MODE ACTIVE` banner.
2. `stitch_busradar/driver_telemetry_dashboard/code.html` (Line 146–152, Line 725–809): Driver Evaluation Simulator with `evalSimInterval = setInterval(...)` generating mock highway coordinates; strictly gated behind an explicit `[Indoor Demo Simulation: OFF]` button, confirmation dialog, and explicit simulation payload flag (`is_simulation: true`).
3. `server.py` (Line 41, 277, 725, 745): `SIMULATION_ENABLED` environment variable defaulting to `False`; `is_simulation` payload flag accepted and broadcast to inform all commuters of synthetic data.
4. `stitch_busradar/driver_telemetry_dashboard/code.html` (Line 369): Keep-alive WebSocket ping heartbeat (`setInterval` every 25s); real transport reliability feature, not a simulation.
5. `stitch_busradar/search_booking_dashboard/code.html` (Line 475, 478): `requestAnimationFrame(renderLoop)` 60fps rendering loop interpolating active markers toward WebSocket target coordinates; real UI rendering feature, marker remains strictly stationary when no telemetry is received.
6. `stitch_busradar/active_journey_dashboard/code.html` (Line 391, 394): Reconnection timers (`setTimeout` 3s); real network resilience feature.
7. `routes/default_route.json` (Line 1–92): Single hardcoded corridor definition with 7 static stops and 85 coordinate nodes; currently no dynamic GTFS import or multi-agency route ingestion.

### 1.3 Missing Elements for Enterprise Production
For BusRadar to scale from an academic prototype to a municipal transit deployment (e.g. Haryana Antyodaya Parivahan Samiti / Yamuna Nagar City Bus):
1. **Standards Compliance:** Absence of General Transit Feed Specification (GTFS Static) parser and GTFS-Realtime (GTFS-RT) feeds (VehiclePositions, TripUpdates, ServiceAlerts).
2. **Backend Stale-Driver Management:** While commuters calculate stale status client-side from timestamp delta, the backend lacks active stale broadcast triggers (e.g., publishing `DRIVER_STALE` after 25s of silence) and maintains trips for 10 minutes before eviction.
3. **Multi-Vehicle Scalability:** Need for formal multi-bus concurrency validation (multiple active buses streaming simultaneously along shared corridors without route conflation).
4. **Observable Ops & Deep Health:** Health endpoint (`/api/health`) provides high-level uptime and socket counts but lacks granular per-bus telemetry telemetry telemetry latency, memory safety indicators, or GTFS-RT metrics.
5. **Persistence & Failover:** Ephemeral memory architecture clears active trips on process restart without an event log, Redis sidecar, or SQLite ledger.

### 1.4 Comparative Industry Analysis (Moovit, OneBusAway, OpenTripPlanner)
| Architectural Dimension | BusRadar (Current) | OneBusAway (OBA) | OpenTripPlanner (OTP) | Moovit / Citymapper |
| :--- | :--- | :--- | :--- | :--- |
| **Static Schedule Ingestion** | Single static JSON (`default_route.json`) | GTFS static bundle (CSV/Zip) with calendar schedules | Full GTFS static + OpenStreetMap (OSM) multi-modal graph | Proprietary multi-agency transit databases & GTFS |
| **Real-Time Data Protocol** | Custom JSON WebSocket (`/ws/telemetry`) | GTFS-RT + SIRI (Service Interface for Real Time Information) | GTFS-RT (PB/JSON) VehiclePositions & TripUpdates | GTFS-RT + proprietary crowd-sourced beacons |
| **Routing & Journey Planning** | Linear ETA along pre-baked polyline | Graph-based stop-to-stop scheduled arrivals | A* multi-modal journey planning (Walk + Bus + Rail) | Heuristic multi-modal routing with live traffic |
| **Rider Incident Reporting** | Driver-only delay broadcasts (`DRIVER_DELAY`) | Transit agency service alerts (GTFS-RT ServiceAlerts) | GTFS-RT ServiceAlerts feed integration | Crowdsourced rider delay, overcrowding, and AC reports |
| **Network Resilience** | PWA cache + WebSocket reconnect backoff | Local SQLite timetable cache for offline browsing | Pre-computed timetable lookup tables | Offline static schedule downloads & map caching |

---

## 2. Comprehensive Gap Analysis

### 2.1 Data Layer Gaps
- **No GTFS Static Feed:** Routes are defined in custom non-standard JSON schemas. Third-party mapping providers and Google Maps cannot consume BusRadar transit schedules.
- **No Timetable Stop-Times:** Stop arrival predictions rely entirely on real-time speed/distance projections rather than scheduled timetable comparison (preventing scheduled vs. actual delay metrics).
- **Single Corridor Rigidity:** Hardcoded route loading prevents automated multi-route expansion without manual JSON configuration.

### 2.2 Real-Time Robustness Gaps
- **Passive Backend Stale Detection:** The server relies on client-side timestamp math; if a driver loses cellular connection in a rural dead-zone, the server continues listing the trip as "LIVE" until the 10-minute expiry task sweeps it.
- **Unstructured Audit Logging:** Telemetry packets are processed without structured telemetry logs, preventing post-incident replay or latency audit trails.
- **Missing Protocol Buffers (Protobuf) Export:** External transit aggregators require binary GTFS-RT Protobuf feeds or standard GTFS-RT JSON representations.

### 2.3 Passenger & Operator UX Gaps
- **Passenger UX:** Lacks explicit GTFS feed download link or clear real-time feed metadata for commuters and researchers.
- **Operator UX:** Fleet managers lack an administrative birds-eye view of all registered vs. active vehicles with detailed ping latency.

### 2.4 Security & Operational Infrastructure Gaps
- **Health Check Depth:** `/api/health` does not expose per-bus telemetry state, memory consumption, or GTFS export availability.
- **Graceful Shutdown & State Eviction:** Clean socket disconnect broadcast when server restarts.

---

## 3. Prioritized Product Roadmap

| Milestone | Action / Feature Description | SIH Criterion Alignment | Effort | Risk |
| :--- | :--- | :--- | :---: | :---: |
| **M1: Standards** | Expose standard GTFS-RT JSON & static route mappings (`/api/gtfs-rt/vehicle-positions`, `/api/gtfs/routes`) | **Novelty & Feasibility:** Interoperates with national open-transit datasets (NDAP / OGD India) | M | Low |
| **M2: Reliability** | Backend Stale Telemetry Engine: Periodic 5s sweep broadcasting `DRIVER_STALE` when silence > 25s | **Scalability & UX:** Eliminates ghost buses and provides deterministic stale feedback to all clients | S | Low |
| **M3: Concurrency** | Multi-Bus Fleet Concurrency: Explicit multi-bus registration and automated multi-bus streaming test suite | **Scalability & Technical Rigor:** Proves zero race conditions across concurrent bus sessions | S | Low |
| **M4: Observability**| Deep Health & Structured Audit Logging: Enriched `/api/health` with per-bus metrics and packet audit trail | **Feasibility & Ops Readiness:** Enables production monitoring on Render / cloud tiers | S | Low |
| **M5: Data Export** | GTFS Static Feed Generator: Exposes standard GTFS text tables (`agency.txt`, `routes.txt`, `stops.txt`, `trips.txt`) | **Impact & Future Progression:** Allows Google Maps transit integration | M | Low |
| **M6: Passenger UX**| Crowdsourced Rider Delay Verification & Offline Schedule Fallback | **Impact & UX:** Commuters can report delays and view offline timetables | L | Med |
| **M7: Persistence** | SQLite / Redis persistence layer for trip history and route management | **Scalability:** Enables multi-instance cluster deployment | L | Med |

---

## 4. Tonight's Implementation Scope

### Features to IMPLEMENT Tonight:
1. **GTFS-Realtime (GTFS-RT) VehiclePositions Endpoint (`/api/gtfs-rt/vehicle-positions`):**
   - Implements GTFS-RT JSON representation according to the official Transit Realtime Specification.
   - Translates live `active_trips` into standard `FeedMessage` entities with `VehiclePosition`, `TripDescriptor`, and `Position` objects.
2. **GTFS Static Specification Exporter (`/api/gtfs/agency.txt`, `/api/gtfs/routes.txt`, `/api/gtfs/stops.txt`, `/api/gtfs/trips.txt`):**
   - Automatically projects `routes_db` into standard GTFS CSV/text tables for transit agency interoperability.
3. **Backend Active Stale-Driver Sweep & Event Multicast:**
   - Enhances server background loop to detect telemetry silence > 25 seconds.
   - Marks trip status as `STALE` and broadcasts `DRIVER_STALE` event to all connected commuter WebSockets.
4. **Multi-Bus Concurrency Verification & Fleet Seeding:**
   - Pre-registers multiple Haryana Roadways buses (`HR-02-A-1001`, `HR-02-B-2002`, `HR-02-C-3003`).
   - Implements end-to-end automated tests streaming concurrent telemetry for multiple buses.
5. **Deep Observable Health Check (`/api/health`):**
   - Extends `/api/health` with `memory_trips`, `active_buses_detail` (latency, packet sequence, mode), `gtfs_rt_status`, and `simulation_mode`.
6. **Structured Telemetry Ingestion Audit Logging:**
   - Logs validated telemetry metadata (bus_id, speed, accuracy, sequence, latency) while maintaining strict GPS coordinate privacy.

### Features to SCAFFOLD (Stub with Clear TODO):
1. **GTFS-RT Protobuf Binary Serializer:** Scaffolded helper stub for protobuf compilation without heavy external compilation dependencies.
2. **Passenger Crowdsourced Delay Verification:** API scaffold for commuters to confirm or upvote reported delays.

### Features to DEFER (Future Milestones):
1. **Full Leaflet UI Redesign / Multi-Route Picker UI:** Deferred to preserve existing UI layout and prevent interface regressions.
2. **Redis / Persistent Database Layer:** Deferred to preserve zero-cost ephemeral free-tier operation.

---

## 5. Plan Verification (Step 4)

Before implementing any code, each proposed item was verified against the codebase:

| Candidate Feature | Target Files | Verification Check & Impact Assessment | Status | Decision Reason |
| :--- | :--- | :--- | :---: | :--- |
| **GTFS-RT VehiclePositions Endpoint** | `server.py` | Verified: Pure REST GET endpoint. Consumes `active_trips` without mutating existing state. Does not touch `/ws/telemetry` or frontend HTML. Revertible cleanly. | **KEPT** | Direct standards compliance; zero risk to existing clients. |
| **GTFS Static Tables Exporter** | `server.py` | Verified: Exposes standard GTFS endpoints (`/api/gtfs/{feed_file}`). Pure read-only transformation of `routes_db`. Zero frontend impact. | **KEPT** | Essential for transit agency integration; zero risk. |
| **Backend Stale-Driver Event Engine** | `server.py` | Verified: Runs in background asyncio loop every 5s. Checks silence > 25s, updates trip status, and multicasts `DRIVER_STALE`. Frontend `renderLoop` already gracefully handles `STALE` events and timestamp age. | **KEPT** | Solves core professor critique regarding honest state reporting. |
| **Deep Observable Health Check** | `server.py` | Verified: Enriches existing `/api/health` response dictionary with additional diagnostic keys without breaking existing schema keys. | **KEPT** | Backward-compatible; enhances operational transparency. |
| **Structured Telemetry Audit Logging** | `server.py` | Verified: Internal Python logger inside `telemetry_websocket`. Preserves privacy (does not write lat/long coordinates or PII). | **KEPT** | Critical for operational visibility; zero architectural risk. |
| **Multi-Bus Fleet Concurrency Testing** | `server.py`, `tests/` | Verified: Added `HR-02-C-3003` to `registered_buses`. Created comprehensive multi-bus concurrent streaming test. | **KEPT** | Validates scalability without UI churn. |
| **UI Journey Planner Overhaul** | Frontend HTML | Dropped: Requires redesigning passenger card layout and route selection panels. Violates hard constraint. | **DROPPED** | Strict constraint: zero UI redesign. Added to roadmap M6. |
| **Database Migration (SQLite/PostgreSQL)** | `server.py` | Dropped: Would break zero-dependency, ephemeral Render free-tier requirement. | **DROPPED** | Preserves zero-config deployment. Added to roadmap M7. |
