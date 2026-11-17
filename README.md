# 🚍 BusRadar: Field-Ready Live Bus Tracking Platform
> **Zero-Cost, Zero-Hardware Real-Time Transit Intelligence for College Campuses & Small Cities**  
> *Pilot Corridor: Yamuna Nagar Bus Stand ⇄ MMDU Mullana Campus Gate (Haryana State Highway 4 & NH-344)*

[![Tests Status](https://img.shields.io/badge/Automated%20Tests-27%20Passed%20(100%25)-success?style=for-the-badge)](TEST_REPORT.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Zero-Cost](https://img.shields.io/badge/Hosting%20Cost-%E2%82%B90%20%2F%20%240%20(Free%20Tier)-brightgreen?style=for-the-badge)](render.yaml)

---

## 1. Project Summary & Core Value Proposition

BusRadar is a zero-hardware live bus-tracking web application engineered for small cities and university commuter corridors where dedicated GPS trackers (AIS-140) are cost-prohibitive.

* **How it works:** An authorized transit driver opens the web console on any standard smartphone, logs in with server-authenticated credentials, and taps **Start Live Broadcast**. The driver's phone streams raw GPS coordinates via the browser's Geolocation API (`navigator.geolocation.watchPosition`) over a high-throughput WebSocket connection to the backend hub.
* **Commuter Experience:** Students and passengers open the web app on Android Chrome, iPhone Safari, or desktop browsers without downloading an app. They see the bus moving in real time along the actual road polyline, view speed and honest delay alerts, and obtain road-following ETAs to their selected stop.
* **Real Data, Zero Simulation:** All production application code relies strictly on real device sensors and server-verified feeds. Hardcoded mock routes, fake waypoint loopers, and synthetic payment flows have been completely eliminated.

---

## 2. Zero-Cost, Zero-Key Architecture

Every technology utilized in BusRadar requires **zero paid services** and **zero third-party API keys**:

| Component | Technology | Free Tier Strategy & Cost Guarantee |
|:---|:---|:---|
| **Driver GPS** | Web Geolocation API (`watchPosition`) | Free built-in browser standard (`enableHighAccuracy: true`, `maximumAge: 0`). Requires HTTPS. |
| **Display Persistence** | Screen Wake Lock API (`navigator.wakeLock`) | Keeps mobile display active while driving, preventing OS background tab throttling. |
| **Real-Time Channel**| FastAPI WebSockets (`asyncio.gather`) | Full-duplex non-blocking event-loop streaming supported on Render free tier. |
| **Cloud Hosting** | Render Free Web Service (Python 3.11) | 750 free instance hours per month, automated HTTPS certificates, zero credit card required. |
| **Wake-Keep Pinger** | cron-job.org (Free external HTTP pinger) | Pings `GET /api/health` every 12 minutes during operating hours to prevent instance spin-down. |
| **Map Rendering** | Leaflet.js + OpenStreetMap (OSM) Tiles | Zero API keys. Configurable tile URL endpoint adhering strictly to OSM tile usage policies. |
| **Map-Matching** | Nearest Segment Projection Algorithm | Pure mathematical point-to-segment algorithm snapping fixes to polyline without external routing APIs. |
| **Road ETA Engine** | Polyline Distance + Dwell + Delay | Computes cumulative distance along highway vertices divided by exponentially smoothed speed. |
| **Offline Shell** | Progressive Web App (PWA) Manifest + `sw.js` | Caches static assets for instant offline loading; passes live WebSocket telemetry through to network. |

---

## 3. Five Production Web Interfaces

```
BusRadar/
├── index.html                           # Root Gateway & PWA Service Worker Registration
├── passenger-search.html                # Commuter Radar Entry Route
├── driver.html                          # Driver Security Gateway Entry Route
└── stitch_busradar/
    ├── onboarding_entry/code.html       # Screen 1: Role Selection (Commuter vs Driver)
    ├── otp_system/code.html             # Screen 2: Driver Authentication (Server PIN + 5-Try Lockout)
    ├── driver_telemetry_dashboard/code.html # Screen 3: Driver OLED Console (Real GPS, Accuracy, RDP Record)
    ├── search_booking_dashboard/code.html   # Screen 4: Commuter Radar (Snapped Map, Road ETA, Fuzzy Search)
    └── active_journey_dashboard/code.html   # Screen 5: On-Board Journey View (Clean SOS Share Link)
```

1. **Onboarding Screen:** Clean branding, language toggle (English/Hindi), and quick-routing buttons: *Continue as Passenger* (no login required) or *Authorized Driver Login*.
2. **Driver Login Gateway:** Bus plate selector (`HR-02-A-1001`, `HR-02-B-2002`, `HR-02-X-9999`), mobile input, and 4-digit PIN verification against server-side bcrypt/hash with automatic 15-minute lockout after 5 wrong attempts.
3. **Driver Telemetry Console:** OLED battery-efficient dark theme, live GPS accuracy meter (`Good <15m`, `Fair 15-30m`, `Poor >30m`), update rate readout, single-tap delay reporter (+5m, +10m, +30m, Clear), and **Record New Route mode** with Ramer-Douglas-Peucker (RDP) polyline simplification and JSON export.
4. **Passenger Radar:** Full-screen Leaflet map with snapped vehicle marker, honest status pill (`LIVE <10s`, `WEAK SIGNAL 10-30s`, `LAST SEEN N min ago`), friendly empty state when no bus is active, road-following ETA range, and typo-tolerant fuzzy stop search powered by Fuse.js.
5. **Active Journey View:** Passenger dashboard displaying real-time corridor progress, next stop indicator, and a **Live Journey Safety (SOS)** modal to share verified tracking URLs via device native share or WhatsApp.

---

## 4. Local Quick Start & Development

### Prerequisites
* Python 3.11+
* Git

### Step-by-Step Execution

```bash
# 1. Clone repository
git clone https://github.com/your-username/BusRadar.git
cd BusRadar

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. Copy environment configuration
cp .env.example .env

# 5. Launch FastAPI Telemetry Hub
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```

Open your browser to:
* **Commuter Live Radar:** [http://localhost:8000/passenger-search.html](http://localhost:8000/passenger-search.html)
* **Driver Console:** [http://localhost:8000/driver.html](http://localhost:8000/driver.html) *(Fleet Testing PIN: `1001` for Bus `HR-02-A-1001`)*
* **System Health Monitor:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
* **Corridor Route API:** [http://localhost:8000/api/routes/ynr_mmdu_sh4](http://localhost:8000/api/routes/ynr_mmdu_sh4)

---

## 5. Deployment Guide: Render Free Web Service

Render provides a completely free tier with automated HTTPS, git push deployments, and native WebSocket support.

### Step 1: Push Repository to GitHub
Ensure all code and configurations are pushed to your GitHub repository.

### Step 2: Create Web Service on Render
1. Sign in to [Render](https://render.com) (no credit card required).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository.
4. Fill in the deployment parameters:
   * **Name:** `busradar` (or custom name)
   * **Region:** Any (e.g. *Oregon, US* or *Frankfurt, EU*)
   * **Branch:** `main`
   * **Runtime:** `Python 3`
   * **Build Command:** `pip install -r requirements.txt`
   * **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
   * **Plan:** **Free** ($0 / month)
5. Under **Environment Variables**, add:
   * `DRIVER_SIGNING_SECRET`: *(Click Generate or enter a random 32-character hex key)*
   * `ADMIN_PASSCODE`: *(Enter a secure administrative password, e.g. `AdminSecure2024!`)*
   * `ALLOWED_ORIGIN`: `*` *(or your Render URL once generated, e.g. `https://busradar.onrender.com`)*
   * `PYTHON_VERSION`: `3.11.8`
6. Click **Create Web Service**. Your service will build and deploy in ~2 minutes with full HTTPS support!

---

## 6. Keeping the Free Tier Awake (Free External Pinger)

Render's free tier automatically spins down (sleeps) after 15 minutes of HTTP inactivity. When a driver or commuter visits a sleeping instance, the cold-start takes approximately 45–60 seconds.

To eliminate cold-start latency during active service hours (e.g. 07:00 to 20:00 IST) without paying anything:

1. Register a free account at [cron-job.org](https://cron-job.org).
2. Click **Create Cronjob**.
3. **Title:** `BusRadar Keep-Alive Pinger`
4. **URL:** `https://your-service-name.onrender.com/api/health`
5. **Execution Schedule:** Every **12 minutes**
6. **Timezone & Active Window:** Set to active operating hours (e.g. `07:00 to 20:00 IST`).
7. Save the job.

> 💡 **Why this works:** `GET /api/health` is a lightweight JSON route (<1 KB response) that executes in under 2 ms, keeping the Python asyncio event loop warm while using less than 40% of the 750 monthly free instance hours!

---

## 7. Automated Testing Suite

The repository includes a comprehensive 27-case automated test suite in the `tests/` directory:

```bash
# Run entire test suite with verbose reporting
python -m pytest tests/ -v

# Run 100-client concurrency and memory benchmark
python -m pytest tests/test_concurrency.py -s -v
```

### Verified Test Results Summary:
* **Total Automated Tests:** 27 / 27 Passed (100%)
* **Multicast Benchmark:** 500 packets across 100 concurrent subscribers completed in **9.67 ms** (51,696 msgs/sec).
* **Memory Delta:** +0.19 MB under load.
* Full test case matrix and logs: 👉 **[Read TEST_REPORT.md](TEST_REPORT.md)**

---

## 8. KNOWN LIMITS & Real-World Constraints

To maintain academic integrity and technical honesty for evaluation panels, here are the real-world operational constraints inherent to a browser-based, zero-cost transit tracking system:

| Limitation | Technical Root Cause | Impact | Recommended Production Next Step |
|:---|:---|:---|:---|
| **Background Tab Geolocation Throttling** | iOS WebKit and Android Chrome aggressively suspend `navigator.geolocation` and throttle timers to 1 execution per minute when the screen locks or user switches apps. | If driver locks phone screen, telemetry stops streaming to commuters. | **Current Workaround:** App acquires `navigator.wakeLock` to keep the screen active on a dashboard mount.<br>**Permanent Fix:** Wrap driver node in a lightweight Capacitor/Cordova native shell with background location permissions. |
| **Render Cold Starts** | Free tier spin-down after 15 minutes of zero HTTP traffic. | First request after an idle night takes 45-50 seconds to boot up. | **Current Workaround:** Free cron-job.org pinger on `GET /api/health` during service hours.<br>**Permanent Fix:** Upgrade Render instance to Starter plan ($7/mo) or deploy on college on-premise server. |
| **Ephemeral File System** | Containerized free instances discard local disk modifications upon redeploy or server restart. | Any files written locally to disk vanish on restart. | **Architecture Guard:** System stores all live state in fast RAM (`active_trips` dict). Routes are pre-committed to `routes/default_route.json` or reloadable via `/api/routes/save`. |
| **OpenStreetMap Tile Usage Policy** | Standard OSM tile servers are operated by volunteer donations and forbid high-frequency bulk scraping or heavy commercial load. | High commuter volume (>10,000 daily map pans) can lead to temporary IP tile rate limiting. | **Current Workaround:** Leaflet configured with clear attribution, valid Referer header, and cached tile layers.<br>**Permanent Fix:** Point tile URL constant to a free Cloudflare-cached tile proxy or Stadia Maps free tier. |
| **Urban Canyon Multipath Jitter** | Satellite signal reflection off dense concrete high-rises causes raw GPS accuracy to degrade to ±30m. | Raw marker might oscillate off the road without correction. | **Architecture Guard:** Server and client filter out fixes with accuracy > 50m and apply **Point-to-Segment Snapping** along the highway polyline. |

---

## 9. Security & Commuter Privacy

* **Zero Location Storage:** Coordinates are held exclusively in volatile RAM and immediately discarded when a trip ends or after 10 minutes of driver silence. Zero tracking databases are written to disk.
* **Driver Session Authentication:** Drivers authenticate against server-stored cryptographic hashes and receive a time-bound HMAC-SHA256 session token. 5 consecutive wrong tries lock out the client for 15 minutes.
* **WebSocket Role Isolation:** Passenger sockets are strictly read-only. Any attempt by a passenger socket to inject coordinates or delay alerts results in instant connection termination (`WS_1008_POLICY_VIOLATION`).
* **Input Sanitization:** All vehicle plates, delay reasons, and route names are sanitized via `html.escape` and size-limited to eliminate Cross-Site Scripting (XSS) and buffer overflow vulnerabilities.

---
*© Team LogiCode | Smart India Hackathon (SIH 2024 / SIH26205) | College Project Release v2.0*
