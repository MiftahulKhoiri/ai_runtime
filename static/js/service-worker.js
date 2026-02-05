const CACHE_NAME = "ai-chat-v1";
const ASSETS = [
  "/",
  "/static/css/style.css",
  "/static/js/chat.js",
  "/static/json/manifest.json"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", event => {
  const req = event.request;

  // API tetap online (jangan di-cache)
  if (req.url.includes("/ask") || req.url.includes("/learn")) {
    return;
  }

  event.respondWith(
    caches.match(req).then(res => res || fetch(req))
  );
});