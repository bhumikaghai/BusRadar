import asyncio
import os
import json
import time
from playwright.async_api import async_playwright

BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
SCREENSHOT_DIR = "autocomplete_screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        console_errors = []

        def handle_console(msg):
            if msg.type == "error":
                text = msg.text
                if "favicon.ico" not in text:
                    console_errors.append(text)

        # -------------------------------------------------------------
        # PASSENGER PORTAL DESKTOP VERIFICATION
        # -------------------------------------------------------------
        print("=== 1. PASSENGER PORTAL DESKTOP (1280x800) ===")
        browser = await p.chromium.launch(
            executable_path=BRAVE_PATH,
            headless=True,
            args=["--no-first-run", "--no-default-browser-check"]
        )
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        page.on("console", handle_console)

        await page.goto("http://127.0.0.1:8000/passenger-search.html", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # Clear existing value in search input
        search_input = page.locator("#passenger-stop-search")
        clear_btn = page.locator("#btn-clear-search")
        dropdown = page.locator("#stop-autocomplete-dropdown")

        if await clear_btn.is_visible():
            await clear_btn.click()
            await page.wait_for_timeout(200)

        # 1A. Type "amb"
        await search_input.fill("amb")
        await page.wait_for_timeout(400) # wait for 150ms debounce + fuse search
        await page.wait_for_selector("#stop-autocomplete-dropdown:not(.hidden)", timeout=3000)
        
        amb_items = await page.locator("#stop-autocomplete-dropdown li.passenger-suggest-item").all_inner_texts()
        print(f"Passenger 'amb' suggestions ({len(amb_items)} items):")
        for it in amb_items:
            print("  *", it.replace("\n", " -- "))

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "passenger_typing_amb.png"))
        print("Captured passenger_typing_amb.png")

        # 1B. Type "his"
        await search_input.fill("")
        await search_input.fill("his")
        await page.wait_for_timeout(400)
        await page.wait_for_selector("#stop-autocomplete-dropdown:not(.hidden)", timeout=3000)

        his_items = await page.locator("#stop-autocomplete-dropdown li.passenger-suggest-item").all_inner_texts()
        print(f"Passenger 'his' suggestions ({len(his_items)} items):")
        for it in his_items:
            print("  *", it.replace("\n", " -- "))

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "passenger_typing_his.png"))
        print("Captured passenger_typing_his.png")

        # 1C. Select a suggestion (e.g. click first suggestion)
        first_item = page.locator("#stop-autocomplete-dropdown li.passenger-suggest-item").first
        first_name = await first_item.locator(".text-xs").inner_text()
        print(f"Clicking suggestion: {first_name}")
        await first_item.click()
        await page.wait_for_timeout(300)

        selected_val = await search_input.input_value()
        print(f"Input value after selection: '{selected_val}'")
        is_hidden = await dropdown.evaluate("el => el.classList.contains('hidden')")
        print(f"Dropdown hidden after selection: {is_hidden}")

        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "passenger_selected.png"))
        print("Captured passenger_selected.png")

        await context.close()

        # -------------------------------------------------------------
        # PASSENGER PORTAL MOBILE VERIFICATION (iPhone 12: 390x844)
        # -------------------------------------------------------------
        print("\n=== 2. PASSENGER PORTAL MOBILE (iPhone 12: 390x844) ===")
        iphone12 = p.devices["iPhone 12"]
        m_context = await browser.new_context(**iphone12)
        m_page = await m_context.new_page()
        m_page.on("console", handle_console)

        await m_page.goto("http://127.0.0.1:8000/passenger-search.html", wait_until="networkidle")
        await m_page.wait_for_timeout(1000)

        m_search = m_page.locator("#passenger-stop-search")
        m_clear = m_page.locator("#btn-clear-search")
        if await m_clear.is_visible():
            await m_clear.tap()
            await m_page.wait_for_timeout(200)

        await m_search.fill("amb")
        await m_page.wait_for_timeout(400)
        await m_page.wait_for_selector("#stop-autocomplete-dropdown:not(.hidden)", timeout=3000)

        await m_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "passenger_mobile.png"))
        print("Captured passenger_mobile.png")

        # Tap on an item to verify mobile touch selection
        m_first = m_page.locator("#stop-autocomplete-dropdown li.passenger-suggest-item").first
        await m_first.tap()
        await m_page.wait_for_timeout(300)
        m_val = await m_search.input_value()
        print(f"Mobile selected value: '{m_val}'")

        await m_context.close()

        # -------------------------------------------------------------
        # DRIVER PORTAL VERIFICATION (Desktop & Mobile)
        # -------------------------------------------------------------
        print("\n=== 3. DRIVER PORTAL VERIFICATION ===")
        d_context = await browser.new_context(viewport={"width": 1280, "height": 800})
        d_page = await d_context.new_page()
        d_page.on("console", handle_console)

        await d_page.goto("http://127.0.0.1:8000/driver.html", wait_until="networkidle")
        await d_page.wait_for_timeout(1000)

        # If redirected to OTP gateway, authenticate with PIN 1001
        otp_inputs = await d_page.locator(".otp-input").all()
        if len(otp_inputs) == 4:
            for idx, ch in enumerate("1001"):
                await otp_inputs[idx].fill(ch)
            await d_page.wait_for_url("**/driver_telemetry_dashboard/code.html**", timeout=8000)
            await d_page.wait_for_timeout(1500)

        start_input = d_page.locator("#start-stop")
        start_clear = d_page.locator("#btn-clear-start")
        start_dropdown = d_page.locator("#start-stop-dropdown")

        if await start_clear.is_visible():
            await start_clear.click()
            await d_page.wait_for_timeout(200)

        # 3A. Type "amb" in driver origin
        await start_input.fill("amb")
        await d_page.wait_for_timeout(400)
        await d_page.wait_for_selector("#start-stop-dropdown:not(.hidden)", timeout=3000)

        d_amb_items = await d_page.locator("#start-stop-dropdown .combobox-item").all_inner_texts()
        print(f"Driver 'amb' suggestions ({len(d_amb_items)} items):")
        for it in d_amb_items:
            print("  *", it.replace("\n", " -- "))

        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "driver_typing_amb.png"))
        print("Captured driver_typing_amb.png")

        # 3B. Select a suggestion
        d_first = d_page.locator("#start-stop-dropdown .combobox-item").first
        d_first_name = await d_first.locator(".text-xs").inner_text()
        print(f"Selecting driver item: {d_first_name}")
        await d_first.click()
        await d_page.wait_for_timeout(300)

        d_val = await start_input.input_value()
        disp_val = await d_page.locator("#display-start-stop").inner_text()
        print(f"Driver input value: '{d_val}', display badge: '{disp_val}'")

        await d_page.screenshot(path=os.path.join(SCREENSHOT_DIR, "driver_selected.png"))
        print("Captured driver_selected.png")

        await d_context.close()
        await browser.close()

        # -------------------------------------------------------------
        # REGRESSION CHECKS
        # -------------------------------------------------------------
        print("\n=== 4. REGRESSION CHECKS ===")
        # Check A: Passenger without driver -> marker stationary, WAITING FOR DRIVER
        r_browser = await p.chromium.launch(executable_path=BRAVE_PATH, headless=True)
        r_page = await r_browser.new_page()
        await r_page.goto("http://127.0.0.1:8000/passenger-search.html", wait_until="networkidle")
        await r_page.wait_for_timeout(1500)
        mode_label = await r_page.locator("#telemetry-mode-label").inner_text()
        print(f"Passenger mode without driver: '{mode_label}'")
        assert "WAITING FOR DRIVER" in mode_label, f"Expected WAITING FOR DRIVER, got {mode_label}"

        # Check B: Driver broadcast -> Live GPS
        # Authenticate driver via API
        import urllib.request
        req = urllib.request.Request(
            "http://127.0.0.1:8000/api/driver/auth",
            data=json.dumps({"bus_id": "HR-02-A-1001", "pin": "1001"}).encode(),
            headers={"Content-Type": "application/json"}
        )
        auth_res = json.loads(urllib.request.urlopen(req).read().decode())
        token = auth_res["token"]
        print(f"Driver auth success, token: {token[:12]}...")

        # Broadcast telemetry via driver websocket
        import websockets
        ws_url = f"ws://127.0.0.1:8000/ws/telemetry?token={token}&bus_id=HR-02-A-1001"
        async with websockets.connect(ws_url) as ws:
            # First packet
            await ws.send(json.dumps({
                "event_type": "DRIVER_TELEMETRY",
                "lat": 30.1290,
                "lng": 77.2674,
                "accuracy": 8.0,
                "speed_kmh": 42.0,
                "heading": 85.0,
                "route_from": "Ambala Cantt",
                "route_to": "Hisar",
                "sequence_number": 1,
                "client_timestamp": time.time(),
                "is_simulation": False
            }))
            await asyncio.sleep(0.5)

            # Wait for passenger page to update
            await r_page.wait_for_timeout(1000)
            updated_mode = await r_page.locator("#telemetry-mode-label").inner_text()
            print(f"Passenger mode with active driver: '{updated_mode}'")
            assert "LIVE GPS" in updated_mode, f"Expected LIVE GPS, got {updated_mode}"

            # Check route badges
            ro = await r_page.locator("#live-route-origin").inner_text()
            rd = await r_page.locator("#live-route-dest").inner_text()
            print(f"Synced route in passenger: {ro} ➔ {rd}")
            assert ro == "Ambala Cantt" and rd == "Hisar"

        await r_browser.close()

        # Check C: GTFS & Health endpoints
        for ep in ["/api/gtfs-rt/vehicle-positions", "/api/gtfs/feed.json", "/api/health"]:
            res = urllib.request.urlopen(f"http://127.0.0.1:8000{ep}")
            print(f"Endpoint {ep} HTTP status: {res.status}")
            assert res.status == 200

        print(f"\nTotal Fatal Console Errors: {len(console_errors)}")
        if console_errors:
            print("Errors logged:", console_errors)
        else:
            print("ZERO console errors!")

        summary = {
            "status": "SUCCESS",
            "screenshots": [
                "passenger_typing_amb.png",
                "passenger_typing_his.png",
                "passenger_selected.png",
                "passenger_mobile.png",
                "driver_typing_amb.png",
                "driver_selected.png"
            ],
            "console_errors": console_errors
        }
        with open(os.path.join(SCREENSHOT_DIR, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
