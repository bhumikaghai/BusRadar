// BusRadar Service Worker - Offline Shell Only
// Live WebSocket telemetry and REST API endpoints are explicitly excluded from caching.

const CACHE_NAME = 'busradar-shell-v2.0.0';
const SHELL_ASSETS = [
  '/',
  '/index.html',
  '/driver.html',
  '/passenger-search.html',
  '/stitch_busradar/i18n.js',
  '/stitch_busradar/onboarding_entry/code.html',
  '/stitch_busradar/otp_system/code.html',
  '/stitch_busradar/driver_telemetry_dashboard/code.html',
  '/stitch_busradar/search_booking_dashboard/code.html',
  '/stitch_busradar/active_journey_dashboard/code.html',
  '/static/manifest.json',
  '/static/icons/icon-192.svg',
  '/static/icons/icon-512.svg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(SHELL_ASSETS);
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // STRICT GUARD: NEVER cache live telemetry WebSockets, API calls, or non-GET requests
  if (
    event.request.method !== 'GET' ||
    url.pathname.startsWith('/ws/') ||
    url.pathname.startsWith('/api/') ||
    url.protocol.startsWith('ws')
  ) {
    return; // Pass through to network
  }

  // Network-first for HTML pages with cache fallback
  if (event.request.mode === 'navigate' || url.pathname.endsWith('.html') || url.pathname === '/') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          if (response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Stale-while-revalidate for static shell assets
  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      const fetchPromise = fetch(event.request)
        .then((networkResponse) => {
          if (networkResponse.status === 200) {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, networkResponse.clone()));
          }
          return networkResponse;
        })
        .catch(() => cachedResponse);

      return cachedResponse || fetchPromise;
    })
  );
});