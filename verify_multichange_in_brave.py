import os
import sys
import time
import subprocess
import requests
from playwright.sync_api import sync_playwright

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
SCREENSHOT_DIR = r"multichange_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def wait_for_server(url="http://127.0.0.1:8000/api/health", timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1)
            if r.status_code == 200:
                print(f"[OK] Server is up: {r.status_code}", flush=True)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError(f"Server at {url} did not respond within {timeout}s")

def run_verification():
    print(">>> Starting Uvicorn server...", flush=True)
    server_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        wait_for_server()

        with sync_playwright() as p:
            print(">>> Launching Brave Browser...", flush=True)
            browser = p.chromium.launch(
                executable_path=BRAVE_PATH,
                headless=True,
                args=["--no-first-run", "--disable-gpu", "--no-sandbox"]
            )
            context = browser.new_context(viewport={"width": 1280, "height": 800})

            # ==========================================
            # REQUIREMENT 1: Passenger Portal Dynamic From/To + Ticket
            # ==========================================
            print("\n>>> Testing Requirement 1: Passenger From/To + Dynamic Ticket...", flush=True)
            page = context.new_page()
            page.goto("http://127.0.0.1:8000/passenger-search.html")
            page.wait_for_selector("#passenger-origin-search", timeout=10000)
            page.wait_for_selector("#passenger-stop-search", timeout=10000)
            page.wait_for_timeout(1000)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R1_from_to_empty.png"))
            print("Captured R1_from_to_empty.png", flush=True)

            # Clear origin and type "Ambala"
            page.click("#btn-clear-origin-search")
            page.fill("#passenger-origin-search", "Ambala")
            page.wait_for_selector("#origin-autocomplete-dropdown .suggest-item-passenger-origin-search", timeout=5000)
            page.click("#origin-autocomplete-dropdown .suggest-item-passenger-origin-search")

            # Clear destination and type "Chandigarh"
            page.click("#btn-clear-search")
            page.fill("#passenger-stop-search", "Chandigarh")
            page.wait_for_selector("#stop-autocomplete-dropdown .suggest-item-passenger-stop-search", timeout=5000)
            page.click("#stop-autocomplete-dropdown .suggest-item-passenger-stop-search")
            page.wait_for_timeout(500)

            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R1_from_to_filled.png"))
            print("Captured R1_from_to_filled.png", flush=True)

            # Open Ticket Modal
            page.click("#btn-open-ticket-modal")
            page.wait_for_selector("#modal-ticket-soon:not(.hidden)", timeout=5000)
            route_text = page.locator("#ticket-route-display").inner_text()
            fare_text = page.locator("#ticket-fare-display").inner_text()
            print(f"Ticket Modal Display: Route='{route_text}', Fare='{fare_text}'", flush=True)
            assert "Ambala" in route_text, f"Expected Ambala in {route_text}"
            assert "Chandigarh" in route_text, f"Expected Chandigarh in {route_text}"
            assert "₹" in fare_text, f"Expected currency symbol in {fare_text}"
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R1_ticket_dynamic.png"))
            print("Captured R1_ticket_dynamic.png", flush=True)

            # Test Generate Pass button
            page.click("#btn-generate-pass")
            page.wait_for_timeout(500)
            btn_text = page.locator("#btn-generate-pass-text").inner_text()
            assert "Pass Issued" in btn_text, f"Expected pass issued confirmation, got '{btn_text}'"

            # Close Modal
            page.click("#btn-close-ticket-modal")
            page.wait_for_timeout(500)

            # Reload Page and verify localStorage persistence
            page.reload()
            page.wait_for_selector("#passenger-origin-search", timeout=10000)
            reloaded_from = page.locator("#passenger-origin-search").input_value()
            reloaded_to = page.locator("#passenger-stop-search").input_value()
            print(f"Reloaded Values from localStorage: From='{reloaded_from}', To='{reloaded_to}'", flush=True)
            assert "Ambala" in reloaded_from, f"Expected Ambala in {reloaded_from}"
            assert "Chandigarh" in reloaded_to, f"Expected Chandigarh in {reloaded_to}"
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R1_persist.png"))
            print("Captured R1_persist.png", flush=True)
            page.close()

            # ==========================================
            # REQUIREMENT 2: Driver Register New Vehicle
            # ==========================================
            print("\n>>> Testing Requirement 2: Driver Register New Vehicle & Auth...", flush=True)
            driver_page = context.new_page()
            driver_page.goto("http://127.0.0.1:8000/driver.html")
            driver_page.wait_for_selector("#btn-toggle-register", timeout=10000)
            driver_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R2_login_with_register_option.png"))
            print("Captured R2_login_with_register_option.png", flush=True)

            # Open Register Form
            driver_page.click("#btn-toggle-register")
            driver_page.wait_for_selector("#driver-register-container:not(.hidden)", timeout=5000)
            unique_vnum = f"HR-02-A-{int(time.time()) % 9000 + 1000}"
            print(f"Registering unique test vehicle: {unique_vnum}", flush=True)
            driver_page.fill("#reg-vehicle-number", unique_vnum)
            driver_page.fill("#reg-driver-name", "Ramesh Sharma")
            driver_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R2_register_form.png"))
            print("Captured R2_register_form.png", flush=True)

            # Submit Registration
            driver_page.click("#btn-submit-register")
            driver_page.wait_for_selector("#reg-success-msg:not(.hidden)", timeout=5000)
            driver_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R2_register_success.png"))
            print("Captured R2_register_success.png", flush=True)

            # Wait for auto-transition to Auth form (1200ms setTimeout in frontend)
            driver_page.wait_for_timeout(2000)

            plate_val = driver_page.locator("#driver-bus-id").input_value()
            print(f"Auth Form Active for Bus ID: {plate_val}", flush=True)
            assert plate_val == unique_vnum

            # Fill OTP (last 4 digits of unique_vnum)
            last4 = unique_vnum.split("-")[-1]
            for idx, digit in enumerate(last4):
                driver_page.locator(f'.otp-input[data-index="{idx}"]').fill(digit)
            
            # Wait for successful auth redirect to telemetry dashboard
            driver_page.wait_for_url("**/driver_telemetry_dashboard/**", timeout=8000)
            driver_page.wait_for_selector("#display-bus-plate", timeout=5000)
            displayed_bus = driver_page.locator("#display-bus-plate").inner_text()
            print(f"[OK] Driver authenticated! Displayed vehicle: {displayed_bus}", flush=True)
            assert displayed_bus == unique_vnum
            driver_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R2_new_vehicle_login.png"))
            print("Captured R2_new_vehicle_login.png", flush=True)
            driver_page.close()

            # ==========================================
            # REQUIREMENT 3: Synchronous Fleet Update over WebSocket
            # ==========================================
            print("\n>>> Testing Requirement 3: Synchronous Fleet Update...", flush=True)
            p_tab = context.new_page()
            p_tab.goto("http://127.0.0.1:8000/passenger-search.html")
            p_tab.wait_for_selector("#passenger-fleet-list", timeout=10000)
            p_tab.wait_for_timeout(1000)

            d_tab = context.new_page()
            d_tab.goto("http://127.0.0.1:8000/driver.html")
            d_tab.wait_for_selector("#btn-toggle-register", timeout=10000)
            d_tab.click("#btn-toggle-register")
            d_tab.wait_for_selector("#reg-vehicle-number", timeout=5000)
            live_test_bus = f"HR-02-S-{int(time.time() * 10) % 9000 + 1000}"
            print(f"Registering fleet sync test vehicle: {live_test_bus}", flush=True)
            d_tab.fill("#reg-vehicle-number", live_test_bus)
            d_tab.fill("#reg-driver-name", "Kavita Devi")
            d_tab.click("#btn-submit-register")
            d_tab.wait_for_selector("#reg-success-msg:not(.hidden)", timeout=5000)
            print(f"Registered {live_test_bus} in driver tab.", flush=True)

            # In passenger tab, verify live_test_bus appears within 5s without reload
            p_tab.bring_to_front()
            p_tab.wait_for_function(
                f"() => document.getElementById('passenger-fleet-list') && document.getElementById('passenger-fleet-list').innerText.includes('{live_test_bus}')",
                timeout=5000
            )
            print(f"[OK] Passenger tab received FLEET_UPDATED event and rendered {live_test_bus} without reload!", flush=True)
            p_tab.screenshot(path=os.path.join(SCREENSHOT_DIR, "R3_passenger_sees_new_bus.png"))
            print("Captured R3_passenger_sees_new_bus.png", flush=True)
            d_tab.close()
            p_tab.close()

            # ==========================================
            # REQUIREMENT 4: Seed 5 More Buses (at least 8 buses in fleet)
            # ==========================================
            print("\n>>> Testing Requirement 4: Seeded Fleet Verification...", flush=True)
            fleet_page = context.new_page()
            fleet_page.goto("http://127.0.0.1:8000/api/fleet")
            fleet_page.wait_for_timeout(500)
            fleet_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R4_fleet_list.png"))
            print("Captured R4_fleet_list.png", flush=True)
            fleet_page.close()

            # Verify API directly
            f_res = requests.get("http://127.0.0.1:8000/api/fleet").json()
            assert len(f_res["fleet"]) >= 8, f"Expected >= 8 buses, got {len(f_res['fleet'])}"
            expected_seeded = ["HR-02-A-1001", "HR-02-B-2002", "HR-02-C-3003", "HR-02-A-4004", "HR-02-B-5005", "HR-02-C-6006", "HR-02-D-7007", "HR-02-E-8008"]
            fleet_ids = [b["bus_id"] for b in f_res["fleet"]]
            for eb in expected_seeded:
                assert eb in fleet_ids, f"Expected {eb} in fleet list"
            print(f"[OK] Seeded fleet verified: {fleet_ids}", flush=True)

            # ==========================================
            # REQUIREMENT 5: Bus 2002 OTP Fix
            # ==========================================
            print("\n>>> Testing Requirement 5: Bus 2002 Login with OTP 2002...", flush=True)
            bus2002_page = context.new_page()
            bus2002_page.goto("http://127.0.0.1:8000/driver.html")
            bus2002_page.wait_for_selector("#bus-preset-select", timeout=10000)
            bus2002_page.select_option("#bus-preset-select", "HR-02-B-2002")
            bus2002_page.wait_for_timeout(500)

            # Fill OTP 2002
            for idx, digit in enumerate("2002"):
                bus2002_page.locator(f'.otp-input[data-index="{idx}"]').fill(digit)
            
            bus2002_page.wait_for_url("**/driver_telemetry_dashboard/**", timeout=8000)
            bus2002_page.wait_for_selector("#display-bus-plate", timeout=5000)
            plate_2002 = bus2002_page.locator("#display-bus-plate").inner_text()
            print(f"[OK] Bus HR-02-B-2002 authenticated with PIN 2002! Displayed plate: {plate_2002}", flush=True)
            assert plate_2002 == "HR-02-B-2002"
            bus2002_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "R5_2002_login_success.png"))
            print("Captured R5_2002_login_success.png", flush=True)
            bus2002_page.close()

            # ==========================================
            # REGRESSION: Verify APIs return HTTP 200
            # ==========================================
            print("\n>>> Verifying API regressions...", flush=True)
            endpoints = [
                "/api/gtfs-rt/vehicle-positions",
                "/api/gtfs/feed.json",
                "/api/health",
                "/api/bus-stands"
            ]
            for ep in endpoints:
                resp = requests.get(f"http://127.0.0.1:8000{ep}")
                assert resp.status_code == 200, f"Endpoint {ep} failed with {resp.status_code}"
                print(f"[OK] {ep} returned 200", flush=True)

            browser.close()
            print("\n==========================================", flush=True)
            print("ALL 5 REQUIREMENTS AND REGRESSIONS VERIFIED!", flush=True)
            print("==========================================", flush=True)

    finally:
        print(">>> Shutting down Uvicorn server...", flush=True)
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()

if __name__ == "__main__":
    run_verification()
