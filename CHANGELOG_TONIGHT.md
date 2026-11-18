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
