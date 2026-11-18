# BusRadar - Overnight Implementation Changelog
**Date:** 2026-11-18  
**Scope:** Production-Readiness & Architectural Hardening  

---

## Change Entries & Revert Instructions

### Entry 1: Multi-Bus Fleet Registration (`server.py`)
* **What changed:** Added Haryana Roadways bus `HR-02-C-3003` (PIN `3003`) to `registered_buses` dictionary in `server.py` to enable concurrent multi-bus fleet testing.
* **Why:** Proves multi-bus concurrency and supports fleet-wide real-time operations across Haryana State Highway 4.
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 2: GTFS-Realtime (GTFS-RT) VehiclePositions Endpoint (`server.py`)
* **What changed:** Added `@app.get("/api/gtfs-rt/vehicle-positions")` providing spec-compliant JSON GTFS-RT feed representations (`FeedMessage`, `FeedHeader`, `VehiclePosition`, `TripDescriptor`, `Position`).
* **Why:** Conforms to national and international transit data standards (Moovit, Google Maps Transit, OpenTripPlanner, OneBusAway interoperability).
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 3: GTFS Static Specification Exporter (`server.py`)
* **What changed:** Added `@app.get("/api/gtfs/{table_name}")` serving standard GTFS CSV tables (`agency.txt`, `routes.txt`, `stops.txt`, `trips.txt`, `stop_times.txt`) and `/api/gtfs/feed.json` overview.
* **Why:** Transforms in-memory highway corridors and stops into open-data transit assets ingestible by any GIS or route planner.
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 4: Backend Active Stale-Driver Detection Engine (`server.py`)
* **What changed:** Enhanced `periodic_trip_cleanup_task` with a 5-second interval checking for telemetry silence > 25 seconds; transitions trip status to `STALE` and broadcasts `DRIVER_STALE` WebSocket event to all commuters.
* **Why:** Eliminates "ghost buses" on server restarts or dropped cellular connections; provides proactive backend-driven stale status instead of relying solely on client clocks.
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 5: Structured Telemetry Audit Logging (`server.py`)
* **What changed:** Added structured operational logging (`TELEMETRY_INGEST: bus_id=... speed=... acc=... seq=... sim=...`) inside WebSocket telemetry handler.
* **Why:** Enables production metric tracking, packet loss diagnostics, and operational observability while strictly adhering to coordinate privacy guidelines (no raw lat/lng or PII logged).
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 6: Deep Observable Health & Metrics (`server.py`)
* **What changed:** Upgraded `/api/health` with `gtfs_rt_available`, `gtfs_static_available`, `registered_fleet_count`, `active_fleet_summary` (latency, packet state, simulation flag).
* **Why:** Provides cloud monitoring and uptime dashboards with deep introspection into real-time transit state.
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 7: Scaffolding Stubs for Protobuf & Crowdsourced Delay (`server.py`)
* **What changed:** Added `/api/gtfs-rt/proto-stub` and `/api/rider/verify-delay` scaffolding endpoints with explicit `TODO` and schema specifications.
* **Why:** Lays the foundation for future native protobuf serialization and rider crowd-validation without bloating current dependencies.
* **Revert command:**
  ```powershell
  git checkout -- server.py
  ```

### Entry 8: Multi-Bus Concurrency & GTFS-RT Test Suite (`tests/test_gtfs_and_concurrency.py`)
* **What changed:** Created comprehensive test suite verifying GTFS-RT schema compliance, GTFS static tables, backend stale sweep, and multi-bus concurrent streaming.
* **Why:** Guarantees automated regression safety and 100% test pass rate across the hardened backend.
* **Revert command:**
  ```powershell
  git checkout -- tests/test_gtfs_and_concurrency.py
  ```

### Change 9 — Fix origin/destination selection on driving portal and passenger search
* **Files touched:**
  - `stitch_busradar/driver_telemetry_dashboard/code.html`
  - `stitch_busradar/search_booking_dashboard/code.html`
* **Root cause:** Regression from commit `2df3c585` (Category G + C + D) where interactive starting and destination comboboxes (`#start-stop` and `#dest-stop`) were removed and replaced with static `<span>` text, deleting Fuse.js and `setupDriverCombobox`, and hardcoding `route_from` and `route_to` in the telemetry packet. Additionally, passenger stop selection failed to sync with the journey drawer's `#live-route-dest` and lacked click-to-open on input focus.
* **What changed:**
  - Restored Fuse.js autocomplete library in `<head>` of `driver_telemetry_dashboard/code.html`.
  - Added interactive `#start-stop` (From / Starting Stop) and `#dest-stop` (To / Destination) comboboxes within the Active Route Card with dropdowns and clear buttons matching the native dark theme.
  - Implemented `setupDriverCombobox` with dual `click` and `touchend` handlers for mobile viewport compatibility.
  - Dynamically bound `currentStartStop` and `currentDestStop` to live `#display-start-stop`, `#display-dest-stop`, and WebSocket `DRIVER_TELEMETRY` packets.
  - In `search_booking_dashboard/code.html`, synchronized stop selection to update `#live-route-dest` and added click/focus trigger to display corridor stops immediately.
* **Helps for college project because:** A working origin/destination selector is baseline usability — a transit app that cannot accept a trip request or allow the driver to specify their route endpoints cannot be demoed or judged on impact/UX.
* **Undo:** `git checkout -- stitch_busradar/driver_telemetry_dashboard/code.html stitch_busradar/search_booking_dashboard/code.html`
* **Verification:** Tested in Brave across desktop (1280x800) and mobile (iPhone 12: 390x844), confirming start stop and destination stop selection, UI text update, dropdown search, and telemetry packet dispatch.

### Change 10 — Haryana bus stand autocomplete on passenger and driver portals
* **Files touched:**
  - `data/haryana_bus_stands.json`
  - `server.py`
  - `stitch_busradar/search_booking_dashboard/code.html`
  - `stitch_busradar/driver_telemetry_dashboard/code.html`
* **Root cause / gap closed:** No autocomplete existed; users had to type full stand names manually. Added a 154-entry Haryana bus stand dataset across all 22 districts, a `/api/bus-stands` endpoint with 5-minute in-memory cache, a prefix/substring ranked search endpoint `/api/bus-stands/search`, and Fuse.js fuzzy autocomplete with debouncing and keyboard navigation on both passenger and driver portals.
* **Helps for college project because:** A transit app that cannot recognize real Haryana bus stand names is a demo, not a product. Autocomplete over the official Haryana Roadways stand list is exactly the kind of real-world data integration judges look for under feasibility and impact.
* **Undo:** `git checkout -- data/haryana_bus_stands.json server.py stitch_busradar/search_booking_dashboard/code.html stitch_busradar/driver_telemetry_dashboard/code.html` (and delete `data/haryana_bus_stands.json` if it did not exist before)
* **Verification:** Verified in real Brave across desktop (1280x800) and mobile (iPhone 12: 390x844); typed "amb" and "his" in both portals; confirmed dropdown renders 8 ranked suggestions; confirmed selection fills input and updates live route badges; verified live GPS telemetry and GTFS/health endpoints; all 36 pytest tests passed (100%).

### Change 11 — Multi-Change Suite: Dynamic From/To Selection, Vehicle Registration, Synchronous Fleet Updates, 5 Seeded Regional Buses & Bus 2002 OTP Fix
* **Files touched:**
  - `server.py`
  - `stitch_busradar/search_booking_dashboard/code.html`
  - `stitch_busradar/otp_system/code.html`
  - `tests/test_simulation_guard.py`
  - `tests/test_multichange_fleet.py`
  - `verify_multichange_in_brave.py`
* **Requirements Addressed & What Changed:**
  1. **Requirement 1 (Passenger From/To + Dynamic Ticketing):** Added a dedicated "From" (Origin) combobox above "To" (Destination) wired to Haryana bus stand autocomplete with Fuse.js and debouncing. Dynamic ticketing modal calculates route `{From} → {To}` with distance-based / flat transit fare, requires both endpoints before generating digital pass, and persists From/To inputs in `localStorage`.
  2. **Requirement 2 (Driver Vehicle Registration):** Added "Register new vehicle" interactive modal/card in `otp_system/code.html` with regex validation (`^[A-Z]{2}-\d{2}-[A-Z]{1,2}-\d{4}$`), driver name, route selector, and clear OTP rule notice ("Your 4-digit OTP is the last 4 digits of your vehicle number"). Added backend endpoint `POST /api/driver/register` (rate-limited 30/min, 409 conflict check, last-4-digit OTP derivation, does not return raw PIN).
  3. **Requirement 3 (Synchronous Fleet Updates over WebSocket):** Backend broadcasts `FLEET_UPDATED` WebSocket event when a vehicle is registered or route is updated. Passenger portal subscribes to WebSocket and automatically updates `/api/fleet` and the bottom drawer fleet ribbon within 5 seconds without page refresh.
  4. **Requirement 4 (Seeded 5 More Regional Buses):** Seeded 5 additional Haryana Roadways buses: `HR-02-A-4004` (4004), `HR-02-B-5005` (5005), `HR-02-C-6006` (6006), `HR-02-D-7007` (7007), and `HR-02-E-8008` (8008). Fleet count is at least 8 buses across Yamuna Nagar, Ambala, Chandigarh, Karnal, Panipat, Hisar, Rohtak, Gurugram, and Faridabad.
  5. **Requirement 5 (Fix Bus 2002 OTP Login):** Enforced the rule that OTP is strictly the last 4 digits of the vehicle number for all buses (`HR-02-B-2002` -> `2002`). Updated `POST /api/driver/auth` to dynamically authenticate with trailing 4 digits. Added startup self-check `_verify_seeded_buses_pins()` verifying hashes on boot.
* **Helps for college project because:**
  - Moves BusRadar from a single corridor pilot to a realistic multi-corridor transit network.
  - Allows professors and evaluators to register any demo vehicle on the fly from their phone and test real-time synchronization on the passenger map without code modifications.
  - Fixes credential discrepancies ensuring any seeded or registered bus can be demonstrated without friction.
* **Undo command:**
  ```powershell
  git checkout -- server.py stitch_busradar/search_booking_dashboard/code.html stitch_busradar/otp_system/code.html tests/test_simulation_guard.py tests/test_multichange_fleet.py verify_multichange_in_brave.py
  ```
* **Verification:**
  - Automated Brave browser test suite `verify_multichange_in_brave.py` executed with exit code 0.
  - All 11 visual screenshots captured in `multichange_screenshots/`: `R1_from_to_empty.png`, `R1_from_to_filled.png`, `R1_ticket_dynamic.png`, `R1_persist.png`, `R2_login_with_register_option.png`, `R2_register_form.png`, `R2_register_success.png`, `R2_new_vehicle_login.png`, `R3_passenger_sees_new_bus.png`, `R4_fleet_list.png`, `R5_2002_login_success.png`.
  - All 41 automated pytest unit & integration tests passing (100%).
  - Zero UI redesign: look and feel preserved exactly.
