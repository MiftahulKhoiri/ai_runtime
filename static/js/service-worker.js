const CACHE_NAME = "ai-chat-v2";

const ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/chat.js",
  "/static/json/manifest.json"
];

// ===============================
// INSTALL
// ===============================
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// ===============================
// ACTIVATE
// ===============================
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_NAME)
          .map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// ===============================
// FETCH
// ===============================
self.addEventListener("fetch", event => {
  const req = event.request;

  // ❌ JANGAN cache API runtime
  if (
    req.url.includes("/chat") ||
    req.url.includes("/reset") ||
    req.url.includes("/reload") ||
    req.url.includes("/health") ||
    req.url.includes("/info")
  ) {
    return;
  }

  // ✅ Cache-first untuk UI
  event.respondWith(
    caches.match(req).then(res => res || fetch(req))
  );
});