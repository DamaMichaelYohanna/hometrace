const CACHE_NAME = 'hometrace-pwa-v2';
const STATIC_ASSETS = [
  '/',
  '/offline/',
  '/static/css/custom.css',
  '/static/js/app.js',
  '/static/images/hero-bg.jpg',
  '/static/icons/favicon.svg',
  '/static/icons/icon-192x192.png',
  '/static/icons/icon-512x512.png',
  'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
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
  const req = event.request;
  const url = new URL(req.url);

  // Skip non-GET requests or admin/payment sensitive endpoints from caching
  if (req.method !== 'GET' || url.pathname.startsWith('/admin/') || url.pathname.startsWith('/payments/callback')) {
    return;
  }

  // Static assets: Cache-first, fall back to network
  if (url.pathname.startsWith('/static/') || url.origin.includes('fonts.googleapis.com')) {
    event.respondWith(
      caches.match(req).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(req).then((networkResponse) => {
          if (networkResponse && networkResponse.status === 200) {
            const responseClone = networkResponse.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, responseClone));
          }
          return networkResponse;
        });
      })
    );
    return;
  }

  // HTML pages: Network-first, fall back to offline.html
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req).catch(() => {
        return caches.match('/offline/').then((fallback) => {
          return fallback || new Response(
            '<h1>Offline</h1><p>You appear to be offline. Please check your internet connection.</p>',
            { headers: { 'Content-Type': 'text/html' } }
          );
        });
      })
    );
    return;
  }
});
