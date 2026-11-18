"""
Step 1: Reproduce Bug in Real Brave (Desktop & Mobile)
Navigates to /driver.html and /passenger-search.html on both local and live Render deployment.
Captures screenshots before and after attempting selection, console logs, and network failures.
"""
import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

LOCAL_BASE = "http://127.0.0.1:8000"
LIVE_BASE = "https://busradar-bre5.onrender.com"
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
SCREENSHOT_DIR = os.path.abspath("bugfix_screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

findings = {
    "console_errors": {},
    "failed_requests": {},
    "page_observations": {}
}

def log_console(msg, key):
    if msg.type in ("error", "warning"):
        findings["console_errors"].setdefault(key, []).append(f"[{msg.type}] {msg.text}")

def log_failed_request(request, key):
    findings["failed_requests"].setdefault(key, []).append(f"{request.method} {request.url} - {request.failure}")

def run_reproduction():
    print("=" * 60)
    print("REPRODUCING BUG IN BRAVE BROWSER")
    print("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=BRAVE_PATH,
            headless=True,
            args=["--no-first-run", "--no-default-browser-check", "--disable-gpu"]
        )

        # -------------------------------------------------------------
        # 1. LOCAL DRIVER PORTAL
        # -------------------------------------------------------------
        print("\n--- 1. Testing Local Driver Portal ---")
        ctx_driver = browser.new_context(viewport={"width": 450, "height": 850})
        page_driver = ctx_driver.new_page()
        page_driver.on("console", lambda m: log_console(m, "local_driver"))
        page_driver.on("requestfailed", lambda r: log_failed_request(r, "local_driver"))

        # Navigate to /driver.html (redirects to otp_system/code.html)
        page_driver.goto(f"{LOCAL_BASE}/driver.html", wait_until="networkidle")
        time.sleep(1)

        # Login with PIN 1001
        otp_inputs = page_driver.query_selector_all(".otp-input")
        if len(otp_inputs) >= 4:
            for idx, ch in enumerate("1001"):
                otp_inputs[idx].fill(ch)

        page_driver.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
        time.sleep(2)

        # Screenshot before attempting selection
        shot_driver_before = os.path.join(SCREENSHOT_DIR, "local_driver_before.png")
        page_driver.screenshot(path=shot_driver_before)
        print(f"Captured: {shot_driver_before}")

        # Check for start/dest selectors
        start_selector = page_driver.query_selector("#start-stop")
        dest_selector = page_driver.query_selector("#dest-stop")
        active_corridor = page_driver.query_selector("#display-route-name")
        corridor_text = active_corridor.inner_text().strip() if active_corridor else "NOT_FOUND"

        findings["page_observations"]["local_driver"] = {
            "start_selector_exists": bool(start_selector),
            "dest_selector_exists": bool(dest_selector),
            "active_corridor_text": corridor_text,
            "can_select_start": False,
            "can_select_dest": False,
            "bug_type": "selector_missing_replaced_with_static_text" if not (start_selector or dest_selector) else "present"
        }
        print(f"Local Driver: start_selector={bool(start_selector)}, dest_selector={bool(dest_selector)}, corridor='{corridor_text}'")

        # Mobile viewport (iPhone 12: 390x844)
        page_driver.set_viewport_size({"width": 390, "height": 844})
        shot_driver_mobile = os.path.join(SCREENSHOT_DIR, "local_driver_mobile.png")
        page_driver.screenshot(path=shot_driver_mobile)
        ctx_driver.close()

        # -------------------------------------------------------------
        # 2. LOCAL PASSENGER SEARCH PORTAL
        # -------------------------------------------------------------
        print("\n--- 2. Testing Local Passenger Search Portal ---")
        ctx_pass = browser.new_context(viewport={"width": 1280, "height": 800})
        page_pass = ctx_pass.new_page()
        page_pass.on("console", lambda m: log_console(m, "local_passenger"))
        page_pass.on("requestfailed", lambda r: log_failed_request(r, "local_passenger"))

        page_pass.goto(f"{LOCAL_BASE}/passenger-search.html", wait_until="networkidle")
        time.sleep(2)

        shot_pass_before = os.path.join(SCREENSHOT_DIR, "local_passenger_before.png")
        page_pass.screenshot(path=shot_pass_before)

        # Check selectors on passenger page
        pass_dest_search = page_pass.query_selector("#passenger-stop-search")
        pass_from_search = page_pass.query_selector("#from-search-input")
        pass_dest_val_before = pass_dest_search.input_value() if pass_dest_search else "NOT_FOUND"

        # Attempt to select a destination
        selection_succeeded = False
        if pass_dest_search:
            pass_dest_search.click()
            pass_dest_search.fill("Barara")
            time.sleep(1)
            # Check dropdown
            dropdown_items = page_pass.query_selector_all("#stop-autocomplete-dropdown li")
            print(f"Passenger dropdown items count: {len(dropdown_items)}")
            if dropdown_items:
                dropdown_items[0].click()
                time.sleep(1)
                pass_dest_val_after = pass_dest_search.input_value()
                selection_succeeded = ("Barara" in pass_dest_val_after)
                print(f"Selected destination: '{pass_dest_val_after}', stuck={selection_succeeded}")

        shot_pass_after = os.path.join(SCREENSHOT_DIR, "local_passenger_after.png")
        page_pass.screenshot(path=shot_pass_after)

        # Mobile viewport for passenger
        page_pass.set_viewport_size({"width": 390, "height": 844})
        shot_pass_mobile = os.path.join(SCREENSHOT_DIR, "local_passenger_mobile.png")
        page_pass.screenshot(path=shot_pass_mobile)

        findings["page_observations"]["local_passenger"] = {
            "has_origin_selector": bool(pass_from_search),
            "has_dest_selector": bool(pass_dest_search),
            "dest_selection_works": selection_succeeded
        }
        ctx_pass.close()

        # -------------------------------------------------------------
        # 3. LIVE RENDER DEPLOYMENT
        # -------------------------------------------------------------
        print("\n--- 3. Testing Live Deployment on Render ---")
        ctx_live = browser.new_context(viewport={"width": 450, "height": 850})
        page_live_driver = ctx_live.new_page()
        page_live_driver.on("console", lambda m: log_console(m, "live_driver"))
        page_live_driver.on("requestfailed", lambda r: log_failed_request(r, "live_driver"))

        try:
            page_live_driver.goto(f"{LIVE_BASE}/driver.html", wait_until="networkidle", timeout=30000)
            time.sleep(1)
            live_otp = page_live_driver.query_selector_all(".otp-input")
            if len(live_otp) >= 4:
                for idx, ch in enumerate("1001"):
                    live_otp[idx].fill(ch)
            page_live_driver.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=12000)
            time.sleep(2)
            shot_live_driver = os.path.join(SCREENSHOT_DIR, "live_driver_before.png")
            page_live_driver.screenshot(path=shot_live_driver)

            live_start_sel = page_live_driver.query_selector("#start-stop")
            live_dest_sel = page_live_driver.query_selector("#dest-stop")
            findings["page_observations"]["live_driver"] = {
                "accessible": True,
                "start_selector_exists": bool(live_start_sel),
                "dest_selector_exists": bool(live_dest_sel),
                "is_also_live": not (live_start_sel and live_dest_sel)
            }
            print(f"Live Driver: start_sel={bool(live_start_sel)}, dest_sel={bool(live_dest_sel)}")
        except Exception as e_live:
            print(f"Live driver test error: {e_live}")
            findings["page_observations"]["live_driver"] = {"error": str(e_live)}

        ctx_live.close()

        browser.close()

    with open(os.path.join(SCREENSHOT_DIR, "reproduction_summary.json"), "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    print("\nReproduction complete. Results written to bugfix_screenshots/reproduction_summary.json")
    return findings

if __name__ == "__main__":
    res = run_reproduction()
    print(json.dumps(res, indent=2))
