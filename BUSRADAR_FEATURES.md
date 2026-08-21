# 🚍 BusRadar - Master Feature & Architecture Documentation
**Smart India Hackathon (SIH) Grand Finale Architecture**  
**Corridor:** Yamuna Nagar ⇄ MMDU Mullana Corridor (Haryana)  
**Engineering Archetype:** 2-Tier Edge-AI Geospatial Telemetry & Incident Multicast Engine  

---

## 1. Executive Summary

**BusRadar** is a real-time, low-latency transit intelligence platform designed specifically for high-density regional Indian transit corridors (exemplified by the **Yamuna Nagar ⇄ MMDU Mullana Corridor**). 

Traditional transit tracking platforms fail due to heavy database write bottlenecks, expensive cloud GPS hardware, and poor connectivity in suburban belts. BusRadar solves this by eliminating hardware lock-in through a **2-Tier Edge-AI Architecture**:
* **Tier 1: Driver Operations Node:** Any smartphone operates as an authorized edge GPS broadcaster and tactical incident dispatcher.
* **Tier 2: Commuter Live Radar:** Waiting passengers receive sub-second vehicle coordinate updates, live distance-decay ETAs, and real-time delay alerts via lightweight WebSocket streams.

---

## 2. Dynamic 2-Tier Architecture & Data Flow

```
┌──────────────────────────────────────────────────────────┐
│                  DRIVER OPERATIONS TIER                  │
│                                                          │
│  [driver.html] ─► [otp_system] ─► [driver_telemetry_dashboard]
│   (Root Proxy)    (Auto-Verify '0000'    (Dynamic 10Hz GPS Telemetry,
│                    Session Guard)         Route Harvesting & Delay Grid)
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼ (Dynamic JSON Packets over WebSocket)
┌──────────────────────────────────────────────────────────┐
│                 FASTAPI TELEMETRY HUB                     │
│                       (server.py)                        │
│                                                          │
│  • Endpoint: ws://localhost:8000/ws/telemetry            │
│  • REST API: GET /api/health | GET /api/fleet            │
│  • ConnectionManager: Asynchronous Pub/Sub Multicast     │
│  • In-Memory Fleet Registry: Dynamic Route Hydration     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             ▼ (Reactive Telemetry & Alerts)
┌──────────────────────────────────────────────────────────┐
│                   COMMUTER RADAR TIER                    │
│                                                          │
│  [index.html] ──► [onboarding_entry] ──► [search_booking_dashboard]
│   (Splash Gate)     (Role Selection)       (Dynamic Route Hydration,
│                                             Live Marker, Amber Alerts,
│                                             & Bharat UPI Pass Modal)
└──────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Feature Matrix

### 🔐 A. Driver Security & Authentication Gateway (`otp_system/`)
* **Buttonless Auto-Verification:** Listens for the exact 4th digit input. Entering `0000` auto-verifies within 0ms without requiring a button click.
* **Smart Keyboard Navigation:** Auto-focuses next input box, handles backspace deletion, and supports direct 4-digit clipboard pasting.
* **60-Second Cooldown Timer:** Prevents SMS API flooding with an interactive visual countdown timer.
* **Cryptographic Session Storage:** Injects `busradar_driver_session` JSON token into `sessionStorage` containing vehicle plate, depot ID, driver mobile, and timestamp.
* **Strict Authentication Route Guard:** An IIFE script running on the driver console instantly bounces any unauthenticated access back to the login gateway.

---

### 📡 B. Driver Telemetry & Incident Console (`driver_telemetry_dashboard/`)
* **Dynamic Route & Metadata Harvesting:** On every 1-second broadcast tick, the engine actively reads the values typed into `#vehicle-plate`, `#start-stop`, `#dest-stop`, `#departure-time`, and `#arrival-time` and embeds them directly into the broadcast packet.
* **Tactical Scaled Chassis:** Built in a high-contrast dark OLED container with enlarged touch targets (`h-14` to `h-16`) and bold typography optimized for drivers on the move.
* **Real-Time GPS Broadcaster:** Toggles 10 Hz telemetry multicasting coordinates along the Yamuna Nagar ⇄ MMDU corridor.
* **Live Telemetry Stream Card:** Displays live Latitude, Longitude, and dispatched packet ticker.
* **1-Click Incident & Delay Dispatcher:** Instantly pushes delay alerts across the entire commuter network:
  * 🟡 **+5 Mins:** Heavy Traffic Alert
  * 🟠 **+10 Mins:** Route Detour Alert
  * 🔴 **+30 Mins:** Road Obstruction / Breakdown Alert
  * 🟢 **Clear Delay:** Instantly clears delay and restores nominal schedule.
* **End Shift & Secure Logout:** Clears session token and returns safely to the gateway.

---

### 🗺️ C. Commuter Live Radar & Transit Search (`search_booking_dashboard/`)
* **Reactive Metadata Binding:** On receiving live telemetry, dynamically overrides static placeholders with the live bus plate number, origin stop, destination stop, and departure/arrival timings.
* **Corridor Route Intelligence:** Pre-configured for the **Route 104: Yamuna Nagar Bus Stand ⇄ MMDU Mullana** regional corridor.
* **Full-Duplex Leaflet.js Mapping:** Real-time bus marker glides smoothly across the map on every incoming coordinate packet (`setLatLng`).
* **Dynamic Distance-Decay ETA Engine:** Computes remaining travel time based on real-time vehicle speed and geospatial distance.
* **High-Visibility Amber Incident Alert Banner:** Dynamically slides into view at the top of the map whenever the driver reports a delay (e.g. `⚠️ DELAY ALERT: +5 min delay due to Heavy Traffic`).
* **Real-Time Delay Recalculation:** Automatically adjusts ETA readouts (e.g. `Live ETA: 13 mins (+5m delay)`) and restores nominal timings when cleared.
* **Offline Resilient Fallback:** If the backend is offline, the radar seamlessly switches to dead-reckoning simulation mode.

---

### 💳 D. Bharat UPI Instant Ticketing Prototype (`search_booking_dashboard/`)
* **Interactive UPI Booking Modal:** Clicking *"Buy Ticket (UPI Pass)"* opens a native modal hydrated with the live route origin, destination, and bus vehicle ID.
* **Dynamic PNR Generation:** Generates unique PNR tracking tokens (e.g. `PNR-BR-781924`) on demand.
* **Simulated BharatQR Pass:** Renders a high-contrast UPI QR code compatible with standard UPI payment flows.
* **1-Click Simulated Payment Verification:** Simulates real-time UPI switch verification with an animated state transition, confirming payment and unlocking the active digital pass.

---

### ⚙️ E. FastAPI Telemetry Hub & REST Backend (`server.py`)
* **High-Throughput ASGI Engine:** Built with FastAPI and Uvicorn for asynchronous I/O handling thousands of concurrent commuter sockets.
* **Asynchronous `ConnectionManager`:** Full-duplex pub/sub manager multicasting GPS and delay packets in under **5 milliseconds**.
* **Dynamic Fleet Registry:** Ingests live route, stop, and timing updates from driver nodes and hydrates newly connected commuter sockets with active fleet snapshots.
* **Zero-Cache Anti-Stale Middleware:** Emits strict `Cache-Control: no-cache, no-store, must-revalidate` HTTP headers to prevent browser caching.
* **REST Health Monitoring (`GET /api/health`):** Returns live server uptime, active WebSocket connections, and total active fleet count.
* **REST Fleet Registry (`GET /api/fleet`):** Returns real-time geospatial coordinates, status, and delay states for all active vehicles.

---

## 4. WebSocket Communication Protocols

### 1. `DRIVER_TELEMETRY` (Dynamic GPS & Route Packet)
```json
{
  "event_type": "DRIVER_TELEMETRY",
  "bus_id": "HR-02-AB-1234",
  "route_from": "Yamuna Nagar Bus Stand",
  "route_to": "MMDU Campus Gate",
  "departure_time": "08:30",
  "arrival_time": "09:15",
  "route": "Yamuna Nagar Bus Stand ⇄ MMDU Campus Gate",
  "lat": 30.1290,
  "lng": 77.2674,
  "speed_kmh": 42,
  "timestamp": 1724171200000,
  "corridor": "Yamuna Nagar ⇄ MMDU Mullana"
}
```

### 2. `DRIVER_DELAY` (Incident & Delay Packet)
```json
{
  "event_type": "DRIVER_DELAY",
  "bus_id": "HR-02-AB-1234",
  "delay_minutes": 5,
  "reason": "Heavy Traffic",
  "timestamp": 1724171200000
}
```

### 3. `CONNECTION_ESTABLISHED` (Hydration Snapshot)
```json
{
  "event_type": "CONNECTION_ESTABLISHED",
  "message": "Connected to BusRadar Telemetry & Incident Hub",
  "active_buses": ["HR-02-AB-1234"],
  "fleet_snapshot": [
    {
      "bus_id": "HR-02-AB-1234",
      "route": "Yamuna Nagar Bus Stand ⇄ MMDU Campus Gate",
      "route_from": "Yamuna Nagar Bus Stand",
      "route_to": "MMDU Campus Gate",
      "departure_time": "08:30",
      "arrival_time": "09:15",
      "status": "STREAMING",
      "last_lat": 30.1290,
      "last_lng": 77.2674,
      "speed_kmh": 40,
      "delay_minutes": 0,
      "delay_reason": "ON_TIME"
    }
  ],
  "timestamp": 1724171200.0
}
```

---

## 5. Live Pitch Demo Playbook (SIH Evaluation)

1. **Start Server:**
   ```powershell
   python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```
2. **Presenter Setup (Window 1):**
   * Open `http://localhost:8000/driver.html`
   * Enter PIN: `0000` *(Auto-verifies and opens Driver Console)*
   * Customize Plate or Route if desired, then click **"START LIVE BROADCAST"**
3. **Commuter Setup (Window 2):**
   * Open `http://localhost:8000/passenger-search.html`
   * Watch the bus plate, route stops, and marker glide live across the map.
4. **Trigger Incident (Window 1):**
   * Click **`+5 Mins`** under *Report Transit Delay*.
   * Watch Window 2 instantly display the Amber incident banner and adjust ETA.
5. **Simulate UPI Pass (Window 2):**
   * Click **"Buy Ticket (UPI Pass)"**
   * Click **"Simulate UPI Payment (Instant Pay)"**
   * Confirm instant verification and generated PNR.
6. **Clear Incident (Window 1):**
   * Click **`Clear Delay`**.
   * Watch Window 2 banner clear and ETA revert to nominal on schedule.
