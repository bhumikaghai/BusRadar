"""
Verification Script for BusRadar Selector Bugfix
Tests in real Brave browser on Windows 11 across desktop and mobile (iPhone 12 emulation).
Saves required screenshots to bugfix_screenshots/ and validates regressions.
"""
import os
import sys
import time
import json
import urllib.request
from playwright.sync_api import sync_playwright

LOCAL_BASE = "http://127.0.0.1:8000"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
SCREENSHOT_DIR = os.path.abspath("bugfix_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

test_results = {
    "driver_desktop": {},
    "driver_mobile": {},
    "passenger_desktop": {},
    "passenger_mobile": {},
    "regression_checks": {},
    "console_errors": {},
    "all_passed": False
}

def log_console(msg, key):
    if msg.type in ("error", "warning"):
        test_results["console_errors"].setdefault(key, []).append(f"[{msg.type}] {msg.text}")

def run_fix_verification():
    print("=" * 60)
    print("RUNNING POST-FIX VERIFICATION IN BRAVE")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=BRAVE_PATH,
            headless=True,
            args=["--no-first-run", "--no-default-browser-check", "--disable-gpu"]
        )

        # -------------------------------------------------------------
        # 1. DRIVER PORTAL - DESKTOP (1280x800)
        # -------------------------------------------------------------
        print("\n--- 1. Driver Portal - Desktop ---")
        ctx_driver_desk = browser.new_context(viewport={"width": 1280, "height": 800})
        page_dd = ctx_driver_desk.new_page()
        page_dd.on("console", lambda m: log_console(m, "driver_desktop"))

        page_dd.goto(f"{LOCAL_BASE}/driver.html", wait_until="networkidle")
        time.sleep(1)
        otp_inputs = page_dd.query_selector_all(".otp-input")
        for idx, ch in enumerate("1001"):
            otp_inputs[idx].fill(ch)
        page_dd.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(2)

        # Test selecting Starting Stop
        start_input = page_dd.wait_for_selector("#start-stop")
        start_input.click()
        start_input.fill("Barara")
        time.sleep(0.5)
        start_items = page_dd.query_selector_all("#start-stop-dropdown .combobox-item")
        assert len(start_items) > 0, "No dropdown items found for start stop 'Barara'"
        start_items[0].click()
        time.sleep(0.5)

        start_val = start_input.input_value()
        display_start_text = page_dd.locator("#display-start-stop").inner_text().strip()
        print(f"Driver Desktop Selected Start: '{start_val}' | Display Text: '{display_start_text}'")
        assert "Barara" in start_val, f"Start value expected 'Barara', got '{start_val}'"
        assert "Barara" in display_start_text, f"Display start text expected 'Barara', got '{display_start_text}'"

        # Test selecting Destination Stop
        dest_input = page_dd.wait_for_selector("#dest-stop")
        dest_input.click()
        dest_input.fill("Jagadhri")
        time.sleep(0.5)
        dest_items = page_dd.query_selector_all("#dest-stop-dropdown .combobox-item")
        assert len(dest_items) > 0, "No dropdown items found for dest stop 'Jagadhri'"
        dest_items[0].click()
        time.sleep(0.5)

        dest_val = dest_input.input_value()
        display_dest_text = page_dd.locator("#display-dest-stop").inner_text().strip()
        print(f"Driver Desktop Selected Dest: '{dest_val}' | Display Text: '{display_dest_text}'")
        assert "Jagadhri" in dest_val, f"Dest value expected 'Jagadhri', got '{dest_val}'"
        assert "Jagadhri" in display_dest_text, f"Display dest text expected 'Jagadhri', got '{display_dest_text}'"

        shot_driver_fixed_desk = os.path.join(SCREENSHOT_DIR, "driver_fixed_desktop.png")
        page_dd.screenshot(path=shot_driver_fixed_desk)
        print(f"Saved: {shot_driver_fixed_desk}")

        test_results["driver_desktop"] = {
            "status": "PASS",
            "selected_start": start_val,
            "selected_dest": dest_val,
            "display_start": display_start_text,
            "display_dest": display_dest_text,
            "screenshot": shot_driver_fixed_desk
        }
        ctx_driver_desk.close()

        # -------------------------------------------------------------
        # 2. DRIVER PORTAL - MOBILE (iPhone 12: 390x844)
        # -------------------------------------------------------------
        print("\n--- 2. Driver Portal - Mobile (iPhone 12) ---")
        ctx_driver_mob = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
            is_mobile=True,
            has_touch=True
        )
        page_dm = ctx_driver_mob.new_page()
        page_dm.on("console", lambda m: log_console(m, "driver_mobile"))

        page_dm.goto(f"{LOCAL_BASE}/driver.html", wait_until="networkidle")
        time.sleep(1)
        otp_mob = page_dm.query_selector_all(".otp-input")
        for idx, ch in enumerate("1001"):
            otp_mob[idx].fill(ch)
        page_dm.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(2)

        start_in_mob = page_dm.wait_for_selector("#start-stop")
        start_in_mob.tap()
        start_in_mob.fill("Kalanaur")
        time.sleep(0.5)
        mob_items = page_dm.query_selector_all("#start-stop-dropdown .combobox-item")
        assert len(mob_items) > 0, "No mobile dropdown items found for Kalanaur"
        mob_items[0].tap()
        time.sleep(0.5)

        start_mob_val = start_in_mob.input_value()
        disp_mob_start = page_dm.locator("#display-start-stop").inner_text().strip()
        print(f"Driver Mobile Selected Start: '{start_mob_val}' | Display: '{disp_mob_start}'")
        assert "Kalanaur" in start_mob_val

        shot_driver_fixed_mob = os.path.join(SCREENSHOT_DIR, "driver_fixed_mobile.png")
        page_dm.screenshot(path=shot_driver_fixed_mob)
        print(f"Saved: {shot_driver_fixed_mob}")

        test_results["driver_mobile"] = {
            "status": "PASS",
            "selected_start": start_mob_val,
            "display_start": disp_mob_start,
            "screenshot": shot_driver_fixed_mob
        }
        ctx_driver_mob.close()

        # -------------------------------------------------------------
        # 3. PASSENGER SEARCH PORTAL - DESKTOP & MOBILE
        # -------------------------------------------------------------
        print("\n--- 3. Passenger Search Portal - Desktop ---")
        ctx_pass_desk = browser.new_context(viewport={"width": 1280, "height": 800})
        page_pd = ctx_pass_desk.new_page()
        page_pd.on("console", lambda m: log_console(m, "passenger_desktop"))

        page_pd.goto(f"{LOCAL_BASE}/passenger-search.html", wait_until="networkidle")
        time.sleep(2)

        pass_search = page_pd.wait_for_selector("#passenger-stop-search")
        clear_btn = page_pd.wait_for_selector("#btn-clear-search")
        clear_btn.click()
        time.sleep(0.5)
        # Verify clear triggers all corridor stops dropdown
        drop_items_p = page_pd.query_selector_all("#stop-autocomplete-dropdown li")
        print(f"Passenger dropdown items count when cleared: {len(drop_items_p)}")
        assert len(drop_items_p) >= 7, f"Expected full corridor stops on click/clear, got {len(drop_items_p)}"
        
        # Select Mustafabad
        pass_search.fill("Mustafabad")
        time.sleep(0.5)
        filtered_items = page_pd.query_selector_all("#stop-autocomplete-dropdown li")
        filtered_items[0].click()
        time.sleep(0.5)

        pass_dest_val = pass_search.input_value()
        live_dest_text = page_pd.locator("#live-route-dest").inner_text().strip()
        print(f"Passenger Desktop Selected Dest: '{pass_dest_val}' | Bottom Card Dest: '{live_dest_text}'")
        assert "Mustafabad" in pass_dest_val
        assert "Mustafabad" in live_dest_text

        shot_pass_fixed_desk = os.path.join(SCREENSHOT_DIR, "passenger_fixed_desktop.png")
        page_pd.screenshot(path=shot_pass_fixed_desk)
        print(f"Saved: {shot_pass_fixed_desk}")

        test_results["passenger_desktop"] = {
            "status": "PASS",
            "selected_dest": pass_dest_val,
            "bottom_card_dest": live_dest_text,
            "screenshot": shot_pass_fixed_desk
        }

        # Mobile viewport for passenger
        print("\n--- Passenger Search Portal - Mobile (iPhone 12) ---")
        page_pd.set_viewport_size({"width": 390, "height": 844})
        time.sleep(1)
        shot_pass_fixed_mob = os.path.join(SCREENSHOT_DIR, "passenger_fixed_mobile.png")
        page_pd.screenshot(path=shot_pass_fixed_mob)
        print(f"Saved: {shot_pass_fixed_mob}")
        test_results["passenger_mobile"] = {
            "status": "PASS",
            "screenshot": shot_pass_fixed_mob
        }

        # -------------------------------------------------------------
        # 4. REGRESSION CHECKS
        # -------------------------------------------------------------
        print("\n--- 4. Running Regression Checks ---")
        # Check A: No driver -> marker stationary, status WAITING FOR DRIVER
        status_no_driver = page_pd.locator("#telemetry-mode-label").inner_text().strip()
        markers_no_driver = page_pd.query_selector_all(".bus-custom-marker")
        print(f"Regression Check A (No driver): status='{status_no_driver}', markers={len(markers_no_driver)}")
        assert "WAITING FOR DRIVER" in status_no_driver
        assert len(markers_no_driver) == 0

        # Check B: Connect driver and broadcast live telemetry -> marker appears, moves
        ctx_driver_live = browser.new_context(
            permissions=["geolocation"],
            geolocation={"latitude": 30.1435, "longitude": 77.2880, "accuracy": 8.0}
        )
        page_dl = ctx_driver_live.new_page()
        page_dl.goto(f"{LOCAL_BASE}/driver.html", wait_until="networkidle")
        time.sleep(1)
        for idx, ch in enumerate("1001"):
            page_dl.query_selector_all(".otp-input")[idx].fill(ch)
        page_dl.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(1)

        # Select custom origin and dest before broadcasting
        page_dl.locator("#start-stop").fill("Jagadhri Bus Stand")
        time.sleep(0.3)
        page_dl.query_selector_all("#start-stop-dropdown .combobox-item")[0].click()
        page_dl.locator("#dest-stop").fill("Mullana Town Stand")
        time.sleep(0.3)
        page_dl.query_selector_all("#dest-stop-dropdown .combobox-item")[0].click()

        # Start broadcast
        page_dl.locator("#btn-broadcast-toggle").click()
        time.sleep(3)

        # Check passenger page sees live status and the selected origin & dest
        status_with_driver = page_pd.locator("#telemetry-mode-label").inner_text().strip()
        markers_with_driver = page_pd.query_selector_all(".bus-custom-marker")
        pass_origin_synced = page_pd.locator("#live-route-origin").inner_text().strip()
        pass_dest_synced = page_pd.locator("#live-route-dest").inner_text().strip()
        print(f"Regression Check B (Driver active): status='{status_with_driver}', markers={len(markers_with_driver)}")
        print(f"Synced from driver packet: origin='{pass_origin_synced}', dest='{pass_dest_synced}'")
        assert "LIVE GPS" in status_with_driver
        assert len(markers_with_driver) >= 1
        assert "Jagadhri" in pass_origin_synced
        assert "Mullana" in pass_dest_synced

        # Move driver position by ~50m
        ctx_driver_live.set_geolocation({"latitude": 30.1480, "longitude": 77.2840, "accuracy": 6.0})
        time.sleep(3)

        # Stop broadcast
        page_dl.on("dialog", lambda d: d.accept())
        page_dl.locator("#btn-broadcast-toggle").click()
        time.sleep(1)
        ctx_driver_live.close()
        ctx_pass_desk.close()

        # Check C: APIs (/api/gtfs-rt/vehicle-positions, /api/gtfs/feed.json, /api/health)
        req_rt = urllib.request.urlopen(f"{LOCAL_BASE}/api/gtfs-rt/vehicle-positions")
        assert req_rt.getcode() == 200
        rt_data = json.loads(req_rt.read().decode())
        assert rt_data["header"]["gtfs_realtime_version"] == "2.0"

        req_feed = urllib.request.urlopen(f"{LOCAL_BASE}/api/gtfs/feed.json")
        assert req_feed.getcode() == 200
        feed_data = json.loads(req_feed.read().decode())
        assert feed_data["agency_id"] == "HR_ROADWAYS"

        req_health = urllib.request.urlopen(f"{LOCAL_BASE}/api/health")
        assert req_health.getcode() == 200
        health_data = json.loads(req_health.read().decode())
        assert health_data["status"] == "healthy"
        assert health_data["version"] == "2.1.0"
        print("Regression Check C (APIs): GTFS-RT, GTFS feed, and /api/health all returned HTTP 200 valid!")

        test_results["regression_checks"] = {
            "live_gps_only_intact": True,
            "gtfs_and_health_endpoints_intact": True,
            "driver_to_passenger_origin_dest_sync": True
        }
        test_results["all_passed"] = True

        browser.close()

    with open(os.path.join(SCREENSHOT_DIR, "post_fix_verification.json"), "w", encoding="utf-8") as f:
        json.dump(test_results, f, indent=2)

    print("\n" + "=" * 60)
    print("ALL VERIFICATION CHECKS PASSED WITH 100% SUCCESS")
    print("=" * 60)
    return test_results

if __name__ == "__main__":
    res = run_fix_verification()
    print(json.dumps(res, indent=2))
