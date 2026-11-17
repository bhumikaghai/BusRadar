# BusRadar: Automated Test Suite & Field-Verification Report

**Project:** BusRadar (Zero-Hardware Real-Time Transit Telemetry & Commuter Radar)  
**Corridor:** Yamuna Nagar Stand ⇄ MMDU Mullana Campus Gate (Haryana State Highway 4)  
**Execution Timestamp:** 2026-11-17T22:54:21+05:30  
**Test Engine:** pytest 9.1.1, pytest-asyncio 1.4.0, anyio 4.8.0, Python 3.13.1  
**Total Automated Tests:** 27  
**Passed:** 27 (100%)  
**Failed:** 0 (0%)  

---

## 1. Automated Test Execution Matrix

| Test ID | Test Name | Tested Target / Function | Expected Behavior | Actual Measured Outcome | Status |
|:---|:---|:---|:---|:---|:---:|
| **AUTH-01** | `test_auth_success` | `POST /api/driver/auth` | Valid PIN returns HMAC token and bus metadata | Returned HTTP 200, signed token generated, `expires_in: 43200` | **PASS** |
| **AUTH-02** | `test_auth_invalid_pin` | `POST /api/driver/auth` | Invalid PIN returns HTTP 401 with remaining attempts | Returned HTTP 401: `Invalid Bus ID or PIN. 4 attempt(s) remaining.` | **PASS** |
| **AUTH-03** | `test_auth_lockout_after_five_failed_attempts` | `POST /api/driver/auth` | 5 failed attempts locks driver IP/bus for 15 minutes | 5th attempt returned HTTP 429 lockout. Subsequent attempts blocked | **PASS** |
| **AUTH-04** | `test_admin_bus_registration` | `POST /api/admin/buses` | Admin passcode required to register new bus | Unauth returned 403. With passcode returned 200 and bus usable immediately | **PASS** |
| **PERF-01** | `test_100_concurrent_broadcast_subscribers` | `ConnectionManager.broadcast` | Concurrently multicasts to 100 WebSocket clients | 500 deliveries completed in 9.67 ms (51,696 msg/sec). Delta: +0.19 MB | **PASS** |
| **GEO-01** | `test_rdp_simplification` | `ramer_douglas_peucker` | Reduces collinear polyline vertices within epsilon | 10 collinear points reduced to 2 endpoints (80% node compression) | **PASS** |
| **GEO-02** | `test_default_route_loaded` | `routes/default_route.json` | Loads 23-node SH-4 corridor & 7 verified stops | Successfully loaded `ynr_mmdu_sh4` (28.4 km total highway corridor) | **PASS** |
| **GEO-03** | `test_road_following_distance_vs_euclidean` | Polyline Distance Engine | Cumulative road distance exceeds Euclidean chord | Road distance ~28.4 km > straight line ~24.1 km | **PASS** |
| **GEO-04** | `test_eta_calculation_formula` | Road ETA Equation | Computes ETA with dwell time and speed floor (15 km/h) | Computed 87.0 mins for 20 km crawl + dwell + delay | **PASS** |
| **SEC-01** | `test_security_headers_present` | Security Middleware | Injects nosniff, SAMEORIGIN, and zero-cache | All security headers present; Cache-Control: no-cache, no-store | **PASS** |
| **SEC-02** | `test_health_endpoint` | `GET /api/health` | Lightweight JSON for cron-job.org pinger | Returned HTTP 200, uptime, active connections, `free_tier_ready: true` | **PASS** |
| **PRIV-01** | `test_zero_location_files_written` | File System Audit | Zero SQLite/DB/GPX/KML files persisted on disk | 0 tracking or database files found on disk (ephemeral memory only) | **PASS** |
| **PRIV-02** | `test_trip_cleanup_after_silence` | Silence Reaper Task | Purges inactive trips from memory after 10m silence | Silent trip purged; `TRIP_ENDED` broadcast dispatched to commuters | **PASS** |
| **TEL-01** | `test_telemetry_valid` | `DriverTelemetrySchema` | Ingests valid lat, lng, speed, accuracy, heading | Validated and parsed in <0.1 ms | **PASS** |
| **TEL-02** | `test_telemetry_out_of_bounds_coords` | Pydantic Bounding Box | Drops coordinates outside North India ($27^\circ-33^\circ$ N) | Validation error raised; Mumbai coordinates rejected | **PASS** |
| **TEL-03** | `test_telemetry_impossible_speed` | Speed Ceiling Filter | Drops velocities exceeding 130 km/h | Validation error raised for 250 km/h fix | **PASS** |
| **TEL-04** | `test_xss_string_sanitization` | `html.escape` Validator | Neutralizes script tags in bus IDs & stop strings | `<script>` sanitized to `&lt;script&gt;` | **PASS** |
| **TEL-05** | `test_delay_schema_validation` | `DriverDelaySchema` | Accepts non-negative delay minutes and reasons | Validated; negative delay (-5m) rejected with ValidationError | **PASS** |
| **TEL-06** | `test_haversine_formula_accuracy` | `haversine_distance_meters` | Accurate geodesic distance calculation | YNR to Jagadhri stand computed at 2,480m (~2.5 km actual) | **PASS** |
| **TEL-07** | `test_snap_to_route_polyline` | `snap_to_route_polyline` | Projects off-road GPS fix to nearest highway segment | Snapped point distance to highway road < 120m | **PASS** |
| **WS-01** | `test_websocket_passenger_connect_snapshot` | `/ws/telemetry` | Delivers state snapshot without requiring auth token | Received `CONNECTION_ESTABLISHED`, `role: PASSENGER`, active fleet list | **PASS** |
| **WS-02** | `test_websocket_ping_pong_heartbeat` | Full-duplex Heartbeat | Responds to PING with PONG and server timestamp | PONG received with matching client timestamp | **PASS** |
| **WS-03** | `test_websocket_passenger_cannot_publish_telemetry` | Role Authorization | Read-only passenger cannot publish coordinates | Socket terminated with code `1008 Policy Violation` | **PASS** |
| **WS-04** | `test_websocket_invalid_driver_token_rejected` | Token Guard | Forged or expired driver token rejected | Handshake rejected with code `1008 Policy Violation` | **PASS** |
| **WS-05** | `test_websocket_authorized_driver_telemetry_broadcast` | End-to-End Multicast | Driver sends fix -> all commuters receive update | Telemetry multicasted; trip dynamically created & cleared on `TRIP_END` | **PASS** |
| **WS-06** | `test_websocket_drop_bad_accuracy` | Accuracy Guard (>50m) | Server drops low-precision GPS fixes | Fix with accuracy 75m dropped; not broadcast to commuters | **PASS** |
| **WS-07** | `test_websocket_drop_oversized_packets` | Size Limit Guard (>4KB) | Drops oversized malicious payloads | >5KB payload dropped; connection remained operational | **PASS** |

---

## 2. Measured Performance & Resource Benchmarks

From automated load and concurrency test runs (`tests/test_concurrency.py`):

* **Concurrent Active Commuter Clients:** 100 simultaneous WebSockets
* **Total Telemetry Deliveries:** 500 packets across 100 subscribers
* **Total Multicast Execution Time:** 9.67 ms (0.0097 seconds)
* **Average Server Latency per Multicast:** **1.93 ms**
* **Multicast Broadcast Throughput:** **51,696.7 deliveries / second**
* **Memory RSS Before Load Test:** 56.51 MB
* **Memory RSS After 100 Clients & 500 Broadcasts:** 56.70 MB
* **Memory Delta:** **+0.19 MB** (Zero memory leaks detected)

---

## 3. Manual Field-Test Checklist & Driving Verification Protocol

Automated test fixtures verify mathematical and network integrity; however, field evaluation on physical hardware must follow this checklist:

### Test Scenario A: Physical Driver Node (Phone 1)
1. **Device Setup:** Mount phone on vehicle dashboard bracket connected to charger.
2. **Launch:** Open `https://your-service.onrender.com/driver.html` in mobile Chrome or Safari.
3. **Login:** Select bus `HR-02-A-1001` and enter PIN `1001`. Verify entry into Driver Console.
4. **Wake Lock Test:** Tap **START LIVE BROADCAST**. Verify that screen does not dim or lock after 30 seconds.
5. **Accuracy Verification:** Observe accuracy indicator:
   * *Good (<15m):* Green badge outdoors under clear sky.
   * *Fair (15-30m):* Amber badge between tall buildings.
   * *Poor (>30m):* Red badge indoors; packet broadcast suspended if >50m.
6. **Incident Dispatch:** Tap **+5 Mins** delay button. Verify badge updates to `+5M DELAY (HEAVY TRAFFIC)`. Tap **Clear Delay** to restore nominal schedule.
7. **Route Recording:** Tap **Record New Route**. Drive corridor, tap **Stop & Save Route**, verify Ramer-Douglas-Peucker compression count.

### Test Scenario B: Commuter Radar Nodes (Phones 2 & 3)
1. **Device Setup:** Connect Phone 2 to Wi-Fi and Phone 3 to cellular 4G data.
2. **Empty State Check:** Open `https://your-service.onrender.com/passenger-search.html` before driver starts trip. Verify friendly empty state: *"No buses currently broadcasting on this corridor"*. No fake ghost bus appears.
3. **Live Stream Verification:** Once Driver Phone 1 starts broadcasting, verify bus marker appears within 1 second and snaps smoothly to the road polyline.
4. **Honest Stale Data Labels:**
   * Put Driver Phone into Airplane Mode for 15 seconds: Passenger status changes from `LIVE (<10s ago)` to `WEAK SIGNAL (10-30s)`.
   * Keep offline for 35 seconds: Status changes to `LAST SEEN 1M AGO`.
   * Re-enable Airplane Mode: Connection auto-reconnects with exponential backoff and restores `LIVE` status.
5. **Road-Following ETA:** Search for destination stop *"MMDU Campus Gate"*. Verify ETA displays range (e.g. `12-15 mins`) calculated strictly along the polyline distance.
6. **SOS Safety Link:** Tap **Safety SOS Link** in Active Journey view. Tap **Copy Live Tracking Link** and send to another device. Verify the link opens the live radar directly.
