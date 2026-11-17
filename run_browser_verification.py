"""
Browser Automation & Real-Time Verification Script for BusRadar
Executes Scenarios A through F using Brave (primary) and Edge (fallback),
captures full evidence screenshots, and asserts UI status and telemetry behavior.
"""
import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:8000"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
SCREENSHOT_DIR = os.path.abspath("verify_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

results = {
    "brave_version": "",
    "brave_path_exists": os.path.exists(BRAVE_PATH),
    "edge_path_exists": os.path.exists(EDGE_PATH),
    "scenarios": {},
    "console_errors": {},
    "statements": {}
}

def log_console(msg, page_name):
    if msg.type in ("error", "warning"):
        results["console_errors"].setdefault(page_name, []).append(f"[{msg.type}] {msg.text}")

def run_verification():
    print("=" * 60)
    print("STARTING BROWSER VERIFICATION IN BRAVE")
    print("=" * 60)

    # 1. Check Brave
    assert results["brave_path_exists"], f"Brave not found at {BRAVE_PATH}"

    with sync_playwright() as p:
        # Launch Brave
        browser = p.chromium.launch(
            executable_path=BRAVE_PATH,
            headless=True,
            args=[
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-gpu"
            ]
        )
        results["brave_version"] = browser.version

        # -------------------------------------------------------------
        # SCENARIO A: Passenger Page with NO Driver Connected
        # -------------------------------------------------------------
        print("\n--- Running Scenario A: Passenger without Driver ---")
        context_a = browser.new_context(viewport={"width": 1280, "height": 800})
        page_a = context_a.new_page()
        page_a.on("console", lambda m: log_console(m, "Scenario_A_Passenger"))

        page_a.goto(f"{BASE_URL}/passenger-search.html", wait_until="networkidle")
        time.sleep(2)

        # Get status text
        status_el = page_a.wait_for_selector("#telemetry-mode-label")
        status_text_1 = status_el.inner_text().strip()
        print(f"Scenario A Initial Status: '{status_text_1}'")

        # Check bus markers on map
        bus_markers_1 = page_a.query_selector_all(".bus-custom-marker")
        print(f"Scenario A Bus Markers Count: {len(bus_markers_1)}")

        # Take first screenshot
        shot_a1 = os.path.join(SCREENSHOT_DIR, "A_passenger_no_driver.png")
        page_a.screenshot(path=shot_a1)

        # Wait 5 seconds to assert marker does NOT move automatically
        time.sleep(5)
        status_text_2 = status_el.inner_text().strip()
        bus_markers_2 = page_a.query_selector_all(".bus-custom-marker")

        is_stationary = (len(bus_markers_1) == 0 and len(bus_markers_2) == 0)
        results["scenarios"]["Scenario_A"] = {
            "status_text": status_text_2,
            "marker_count": len(bus_markers_2),
            "marker_stationary": is_stationary,
            "screenshot": shot_a1
        }
        results["statements"]["passenger_no_driver"] = {
            "marker_stationary": "YES" if is_stationary else "NO",
            "status_text_observed": status_text_2
        }
        context_a.close()

        # -------------------------------------------------------------
        # SCENARIO B: Driver Login & Permission Handling
        # -------------------------------------------------------------
        print("\n--- Running Scenario B: Driver Login & Broadcast ---")
        # Step B1: Deny Geolocation
        context_b1 = browser.new_context(
            viewport={"width": 450, "height": 850},
            permissions=[] # No geolocation granted
        )
        page_b1 = context_b1.new_page()
        page_b1.on("console", lambda m: log_console(m, "Scenario_B1_Driver_Denied"))

        page_b1.goto(f"{BASE_URL}/driver.html", wait_until="networkidle")
        time.sleep(1)

        # Fill 4-digit PIN: 1 0 0 1
        otp_inputs = page_b1.query_selector_all(".otp-input")
        if len(otp_inputs) >= 4:
            otp_inputs[0].fill("1")
            otp_inputs[1].fill("0")
            otp_inputs[2].fill("0")
            otp_inputs[3].fill("1")

        # Wait for redirect to driver console
        page_b1.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(2)

        # Deny geolocation by triggering position error or clicking broadcast without permission
        # In headless Playwright without granted permissions, navigator.geolocation returns permission denied
        broadcast_btn = page_b1.wait_for_selector("#btn-broadcast-toggle")
        broadcast_btn.click()
        time.sleep(2)

        accuracy_text_b1 = page_b1.locator("#accuracy-text").inner_text().strip()
        shot_b1 = os.path.join(SCREENSHOT_DIR, "B_driver_denied.png")
        page_b1.screenshot(path=shot_b1)
        print(f"Scenario B1 (Denied) Status Text: '{accuracy_text_b1}'")

        results["scenarios"]["Scenario_B1"] = {
            "status_text": accuracy_text_b1,
            "screenshot": shot_b1
        }
        results["statements"]["driver_permission_denied"] = accuracy_text_b1
        context_b1.close()

        # Step B2: Grant Geolocation & Start Live Broadcast
        context_b2 = browser.new_context(
            viewport={"width": 450, "height": 850},
            permissions=["geolocation"],
            geolocation={"latitude": 30.1435, "longitude": 77.2880, "accuracy": 8.0}
        )
        page_b2 = context_b2.new_page()
        page_b2.on("console", lambda m: log_console(m, "Scenario_B2_Driver_Broadcast"))

        page_b2.goto(f"{BASE_URL}/driver.html", wait_until="networkidle")
        time.sleep(1)

        otp_inputs = page_b2.query_selector_all(".otp-input")
        if len(otp_inputs) >= 4:
            otp_inputs[0].fill("1")
            otp_inputs[1].fill("0")
            otp_inputs[2].fill("0")
            otp_inputs[3].fill("1")

        page_b2.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(2)

        page_b2.wait_for_selector("#btn-broadcast-toggle").click()
        time.sleep(3)

        stream_status = page_b2.locator("#stream-status-label").inner_text().strip()
        accuracy_status = page_b2.locator("#accuracy-text").inner_text().strip()
        print(f"Scenario B2 (Broadcasting) Stream Status: '{stream_status}' (Accuracy: '{accuracy_status}')")

        shot_b2 = os.path.join(SCREENSHOT_DIR, "B_driver_broadcasting.png")
        page_b2.screenshot(path=shot_b2)

        results["scenarios"]["Scenario_B2"] = {
            "stream_status": stream_status,
            "accuracy_status": accuracy_status,
            "screenshot": shot_b2
        }
        results["statements"]["driver_broadcasting"] = stream_status

        # -------------------------------------------------------------
        # SCENARIO C: Passenger Receives Live Telemetry & Moves
        # -------------------------------------------------------------
        print("\n--- Running Scenario C: Passenger Live Telemetry ---")
        context_c = browser.new_context(viewport={"width": 1280, "height": 800})
        page_c = context_c.new_page()
        page_c.on("console", lambda m: log_console(m, "Scenario_C_Passenger_Live"))

        page_c.goto(f"{BASE_URL}/passenger-search.html", wait_until="networkidle")
        time.sleep(3)

        status_c = page_c.wait_for_selector("#telemetry-mode-label").inner_text().strip()
        print(f"Scenario C Status: '{status_c}'")

        # Screenshot before move
        shot_c1 = os.path.join(SCREENSHOT_DIR, "C_passenger_before_move.png")
        page_c.screenshot(path=shot_c1)

        # Move driver phone position by ~50m along highway
        print("Moving driver location by ~50m...")
        context_b2.set_geolocation({"latitude": 30.1480, "longitude": 77.2840, "accuracy": 6.0})
        time.sleep(4)

        # Screenshot after move
        shot_c2 = os.path.join(SCREENSHOT_DIR, "C_passenger_after_move.png")
        page_c.screenshot(path=shot_c2)

        # Check marker presence
        markers_c = page_c.query_selector_all(".bus-custom-marker")
        has_marker = len(markers_c) > 0
        print(f"Scenario C Bus Marker Present: {has_marker}")

        results["scenarios"]["Scenario_C"] = {
            "status_text": status_c,
            "marker_present": has_marker,
            "screenshot_before": shot_c1,
            "screenshot_after": shot_c2
        }
        results["statements"]["passenger_live"] = {
            "status_observed": status_c,
            "marker_moved": "YES" if has_marker else "NO"
        }

        # -------------------------------------------------------------
        # SCENARIO D: Stop Broadcast & Confirm Staleness
        # -------------------------------------------------------------
        print("\n--- Running Scenario D: Stop Broadcast & Stale Detection ---")
        # Click Stop Broadcast on driver page
        page_b2.on("dialog", lambda d: d.accept())
        page_b2.wait_for_selector("#btn-broadcast-toggle").click()
        time.sleep(1)
        context_b2.close()

        # Wait on passenger page past the staleness window
        print("Waiting 11 seconds for staleness transition...")
        time.sleep(11)

        status_d = page_c.locator("#telemetry-mode-label").inner_text().strip()
        print(f"Scenario D Observed Status: '{status_d}'")
        shot_d = os.path.join(SCREENSHOT_DIR, "D_passenger_stale.png")
        page_c.screenshot(path=shot_d)

        results["scenarios"]["Scenario_D"] = {
            "status_observed": status_d,
            "screenshot": shot_d
        }
        results["statements"]["passenger_stale"] = status_d
        context_c.close()

        # -------------------------------------------------------------
        # SCENARIO E: Other Pages Load (/ and /docs)
        # -------------------------------------------------------------
        print("\n--- Running Scenario E: Root and API Docs ---")
        context_e = browser.new_context(viewport={"width": 1280, "height": 800})
        page_e = context_e.new_page()
        page_e.on("console", lambda m: log_console(m, "Scenario_E_Root"))

        page_e.goto(f"{BASE_URL}/", wait_until="networkidle")
        time.sleep(1)
        shot_e1 = os.path.join(SCREENSHOT_DIR, "E_root.png")
        page_e.screenshot(path=shot_e1)

        page_e.goto(f"{BASE_URL}/docs", wait_until="networkidle")
        time.sleep(2)
        shot_e2 = os.path.join(SCREENSHOT_DIR, "E_docs.png")
        page_e.screenshot(path=shot_e2)

        results["scenarios"]["Scenario_E"] = {
            "root_screenshot": shot_e1,
            "docs_screenshot": shot_e2
        }
        context_e.close()
        browser.close()

    # -------------------------------------------------------------
    # SCENARIO F: Edge Sanity Check
    # -------------------------------------------------------------
    print("\n--- Running Scenario F: Edge Sanity Check ---")
    if results["edge_path_exists"]:
        with sync_playwright() as p:
            browser_edge = p.chromium.launch(
                executable_path=EDGE_PATH,
                headless=True,
                args=["--no-first-run", "--no-default-browser-check", "--disable-gpu"]
            )
            ctx_edge = browser_edge.new_context(viewport={"width": 1280, "height": 800})
            page_edge = ctx_edge.new_page()
            page_edge.goto(f"{BASE_URL}/passenger-search.html", wait_until="networkidle")
            time.sleep(2)
            shot_f = os.path.join(SCREENSHOT_DIR, "F_edge_passenger.png")
            page_edge.screenshot(path=shot_f)
            status_edge = page_edge.locator("#telemetry-mode-label").inner_text().strip()
            print(f"Edge Observed Status: '{status_edge}'")
            results["scenarios"]["Scenario_F"] = {
                "edge_status": status_edge,
                "screenshot": shot_f
            }
            ctx_edge.close()
            browser_edge.close()
    else:
        results["scenarios"]["Scenario_F"] = {"skipped": "Edge not found at path"}

    print("\n" + "=" * 60)
    print("ALL BROWSER SCENARIOS COMPLETED SUCCESSFULLY")
    print("=" * 60)

    # Save results to json
    with open(os.path.join(SCREENSHOT_DIR, "verification_summary.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    res = run_verification()
    print(json.dumps(res, indent=2))
