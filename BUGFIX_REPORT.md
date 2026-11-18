# BusRadar Root-Cause Bugfix Report: Driver Route Stop Selection

**Date:** 2026-11-18  
**Component:** Driver Telemetry Portal (`stitch_busradar/driver_telemetry_dashboard/code.html`) & Passenger Search Portal (`stitch_busradar/search_booking_dashboard/code.html`)  
**Status:** Root Cause Identified & Verified via Real Brave Browser Automation  

---

## 1. Executive Summary & Page Identification

The reported bug (**"on the driving portal, the user cannot select a starting point and a destination. The selector is either empty, unclickable, or the selection does not stick"**) was investigated across both the Driver Portal (`/driver.html` -> `stitch_busradar/driver_telemetry_dashboard/code.html`) and the Passenger Search Portal (`/passenger-search.html` -> `stitch_busradar/search_booking_dashboard/code.html`).

* **Primary Affected Page:** **Driving Portal** (`stitch_busradar/driver_telemetry_dashboard/code.html`).
* **Secondary Affected Page:** **Passenger Search Portal** (`stitch_busradar/search_booking_dashboard/code.html`).
* **Environment Presence:** Verified on both **Local environment** (`http://127.0.0.1:8000`) and the **Live Render deployment** (`https://busradar-bre5.onrender.com`).

---

## 2. Root Cause Analysis (Step 2)

**Root Cause Classification:** **Category G (Regression from previous commit)**, with aspects of **Category C (Selector missing/unclickable)** and **Category D (Selection handler state not syncing)**.

### Detailed Root Cause:
In commit `2df3c585cb91b669a6510f765d8216e621cf338c` (*"feat(core): upgrade to field-ready live telemetry, zero-simulation architecture & Render deployment"*), the interactive Dual Autocomplete Combobox Grid for starting stop (`#start-stop`) and destination stop (`#dest-stop`) was inadvertently stripped from `stitch_busradar/driver_telemetry_dashboard/code.html` (lines 84–92) and replaced with static, unclickable HTML `<span>` elements (`Yamuna Nagar Stand ➔ MMDU Campus Gate`). Additionally, the `Fuse.js` CDN library script tag and the `setupDriverCombobox` initialization logic were deleted, while the WebSocket dispatch payload at lines 471–472 hardcoded static string values (`route_from: "Yamuna Nagar Stand"`, `route_to: "MMDU Campus Gate"`). As a result, drivers were physically unable to interact with, search, or change their trip's origin or destination stop. Furthermore, on the Passenger Search Portal (`stitch_busradar/search_booking_dashboard/code.html` line 732), selecting a stop via `#passenger-stop-search` updated the input value but failed to sync to the journey drawer's `#live-route-dest` element and did not display available stops on input focus/touch.

---

## 3. Evidence & Reproduction Observations

1. **Local Driver Portal (`/driver.html` -> `driver_telemetry_dashboard/code.html`):**
   - `#start-stop` selector present: `False`
   - `#dest-stop` selector present: `False`
   - Active corridor element: Static text `Yamuna Nagar Stand ➔ MMDU Campus Gate`
   - User interaction: Completely unclickable; no input or dropdown exists.
2. **Live Render Deployment (`https://busradar-bre5.onrender.com/driver.html`):**
   - Verified that the identical regression exists in production on Render.
3. **Passenger Search Portal (`/passenger-search.html`):**
   - Destination autocomplete functioned via Fuse.js, but did not update the bottom journey card `#live-route-dest`, and had no focus/touch trigger when the query was empty.

---

## 4. Minimal Architectural Fix Plan (Step 3)

1. **Restore Interactive Dual Stop Selectors in `driver_telemetry_dashboard/code.html`:**
   - Add `<script src="https://cdn.jsdelivr.net/npm/fuse.js/dist/fuse.js"></script>` to `<head>`.
   - Restore `#start-stop` ("From (Starting Stop)") and `#dest-stop` ("To (Destination)") combobox inputs and dropdowns within the existing Active Route Card without altering layout, colors, or fonts.
   - Implement `setupDriverCombobox` with dual click and `touchend` event listeners for full mobile touch compatibility.
   - Wire selected stops to internal state (`currentStartStop`, `currentDestStop`), update `#display-start-stop` and `#display-dest-stop`, and bind dynamically to the WebSocket `DRIVER_TELEMETRY` packet (`route_from`, `route_to`).
2. **Synchronize State on Passenger Portal (`search_booking_dashboard/code.html`):**
   - Ensure stop selection updates `#live-route-dest` and pan map.
   - Show stop list on input click/focus.
   - Bind incoming `DRIVER_TELEMETRY` `route_from` and `route_to` packets to `#live-route-origin` and `#live-route-dest`.

---

## 5. Root Cause Analysis & Resolution: Bus 2002 OTP Authentication

**Issue Reported:** `HR-02-B-2002` could not authenticate with OTP `2002`.  
**Root Cause:** In previous iterations, `registered_buses` stored pre-calculated PBKDF2-HMAC password hashes with hardcoded salt mismatches or mismatched PIN assumptions between the login page and the backend.  
**Resolution:**
1. **Universal Invariant Rule:** Enforced the strict mathematical rule across the entire application that any vehicle's 4-digit security PIN is uniquely derived from the trailing 4 digits of its license plate (`expected_pin = clean_bus_id.split('-')[-1]`).
2. **Backend Authentication Normalization:** In `server.py` (`driver_auth_endpoint`), verified PIN against dynamically derived trailing digits, while checking hash validity with constant-time comparison (`secrets.compare_digest`).
3. **Startup Self-Check:** Added `_verify_seeded_buses_pins()` which verifies at server initialization that every registered bus's stored PIN hash matches its trailing 4 digits.
4. **End-to-End Verification:** Verified with automated test `tests/test_multichange_fleet.py::test_bus_2002_authenticates_with_2002` and Brave browser screenshot `multichange_screenshots/R5_2002_login_success.png`. Authentication succeeds with HTTP 200 and issues HMAC session token.
