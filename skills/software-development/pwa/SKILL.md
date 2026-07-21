---
name: pwa
description: "Guide complet des Progressive Web Apps : Service Workers, Cache API, IndexedDB, Manifest, Push Notifications, Background Sync, Offline First, Workbox."
tags: [pwa, progressive-web-app, service-worker, cache-api, indexeddb, manifest, push-notifications, background-sync, offline-first, workbox]
---

# PWA — Progressive Web Apps

## Critères PWA (Lighthouse)
1. **HTTPS** — obligatoire pour Service Workers
2. **Web App Manifest** — icônes, thème, orientation
3. **Service Worker** — interception, cache, offline
4. **Fonctionne offline** — au moins une page shell
5. **Rapide** — First Paint < 3s
6. **Responsive** — tous écrans
7. **Installable** — "Ajouter à l'écran d'accueil"

## Web App Manifest
```json
{
  "name": "Mon App PWA",
  "short_name": "App",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## Service Workers — Cycle de Vie
```
Download → Install (pre-cache) → Waiting → Activate (cleanup) → Fetch
```

### Enregistrement
```js
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

### Stratégies de Cache

| Stratégie | Usage |
|-----------|-------|
| **Cache First** | Assets statiques (CSS, JS, fonts) |
| **Network First** | Pages HTML, données API |
| **Stale-While-Revalidate** | API, données semi-fréquentes |
| **Network Only** | Transactions |

```js
// Cache First
event.respondWith(
  caches.match(event.request).then(cached => cached || fetch(event.request))
);

// Stale-While-Revalidate
event.respondWith(
  caches.match(event.request).then(cached => {
    const fetchPromise = fetch(event.request).then(response => {
      caches.open('v1').then(cache => cache.put(event.request, response.clone()));
      return response;
    });
    return cached || fetchPromise;
  })
);
```

### Pre-caching (Install)
```js
const PRECACHE_URLS = ['/', '/styles/main.css', '/scripts/main.js'];
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS)));
});
```

## Workbox (abstraction SW)
```js
import { precacheAndRoute } from 'workbox-precaching';
import { registerRoute } from 'workbox-routing';
import { NetworkFirst, StaleWhileRevalidate, CacheFirst } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';

precacheAndRoute(self.__WB_MANIFEST);

registerRoute(({ request }) => request.mode === 'navigate', new NetworkFirst({ cacheName: 'pages' }));
registerRoute(({ request }) => request.destination === 'image',
  new CacheFirst({ cacheName: 'images', plugins: [new ExpirationPlugin({ maxEntries: 60 })] }));
```

## IndexedDB (données structurées offline)
```js
import { openDB } from 'idb';
const db = await openDB('mon-app', 1, {
  upgrade(db) { db.createObjectStore('notes', { keyPath: 'id', autoIncrement: true }); },
});
await db.add('notes', { title: 'Ma note', content: '...' });
const all = await db.getAll('notes');
```

Alternatives : Dexie.js, localForage, JsStore.

## Push Notifications
```js
// Subscription
const subscription = await registration.pushManager.subscribe({
  userVisibleOnly: true,
  applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
});

// SW — Notification
self.addEventListener('push', event => {
  const data = event.data.json();
  self.registration.showNotification(data.title, { body: data.body, icon: '/icon-192.png' });
});
```

## Background Sync
```js
// Main thread
navigator.serviceWorker.ready.then(reg => reg.sync.register('sync-orders'));

// SW
self.addEventListener('sync', event => {
  if (event.tag === 'sync-orders') event.waitUntil(syncOrders());
});
```

## Offline First
```
Cache → IndexedDB → Network → Fallback UI
```

## Outils
| Outil | Usage |
|-------|-------|
| Lighthouse | Audit PWA |
| Workbox | SW génération + strategies |
| PWABuilder | Wrapper → stores |
| Bubblewrap | TWA → Play Store |

## Testing
```bash
chrome://serviceworker-internals/
chrome://inspect/#service-workers
# Chrome DevTools → Application → Manifest
```

## Pièges Courants
- **Cache trop agressif** — utilisateurs voient données périmées
- **iOS Safari** — support partiel (pas de push, sync limité)
- **HTTPS manquant** — SW refuse de s'enregistrer (sauf localhost)
- **SW non mis à jour** — `skipWaiting()` + `clients.claim()`

## Références
- [Web.dev PWA](https://web.dev/learn/pwa)
- [Workbox](https://developer.chrome.com/docs/workbox)
- [MDN Service Workers](https://developer.mozilla.org/docs/Web/API/Service_Worker_API)
- [PWABuilder](https://www.pwabuilder.com)
- [idb](https://github.com/jakearchibald/idb)
- [Dexie.js](https://dexie.org)