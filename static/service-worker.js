const CACHE_NAME = "college-ai-chatbot-v1";
const PRECACHE_URLS = [
  "/",
  "/static/style.css",
  "/static/script.js",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// Network-first for /chat (always want fresh answers), cache-first for static assets
self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);

  if (url.pathname === "/chat") {
    return; // let it hit the network normally, no caching for live chat responses
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      return (
        cached ||
        fetch(event.request).catch(() => {
          if (event.request.mode === "navigate") {
            return caches.match("/");
          }
        })
      );
    })
  );
});
