---
name: web-vitals
description: "Guide complet des Web Vitals : LCP, FID, CLS, INP, TTFB, Core Web Vitals, optimisation, Lighthouse, RUM, CrUX, WebPageTest."
tags: [web-vitals, performance, lcp, fid, cls, inp, ttfb, lighthouse, rum, crux, webpagetest, optimisation]
---

# Web Vitals — Performance Web

## Core Web Vitals (Google Ranking)

| Métrique | Mesure | Bon | À améliorer | Mauvais |
|----------|--------|-----|-------------|---------|
| **LCP** | Perceived loading | ≤ 2.5s | ≤ 4.0s | > 4.0s |
| **INP** | Interactivity | ≤ 200ms | ≤ 500ms | > 500ms |
| **CLS** | Visual stability | ≤ 0.1 | ≤ 0.25 | > 0.25 |

### Métriques Secondaires
- **FCP** — ≤ 1.8s (premier contenu visible)
- **TTFB** — ≤ 800ms (latence serveur)
- **TBT** — ≤ 200ms (temps avant interactivité)
- **TTI** — ≤ 3.8s (interactivité complète)

## LCP — Largest Contentful Paint

### Éléments LCP
Images (`<img>`, `<svg>`, poster vidéo), blocs de texte, div avec background-image

### Causes + Solutions
| Cause | Solution |
|-------|----------|
| TTFB lent | CDN, caching serveur |
| Ressource bloquante | Defer JS, CSS critique inline |
| Image lente | WebP/AVIF, responsive images, preload |
| CSR | SSR, pre-rendering, streaming |

```html
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high" />
<img src="/hero-400.webp" srcset="... 400w, ... 800w, ... 1200w"
     sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
     width="1200" height="630" fetchpriority="high" />
```

## INP — Interaction to Next Paint (remplace FID mars 2024)

### Ce qui est mesuré
Clics (`click`, `pointerdown`), touches (`keydown`), taps

### Causes
| Cause | Solution |
|-------|----------|
| Long tasks (> 50ms) | Découper en micro-tasks, Web Workers |
| Heavy DOM | Virtualisation |
| Layout thrashing | Batching DOM reads/writes |
| Hydratation lente | Selective/partial hydration |

```js
// Découpage de tâches longues
function processItems(items) {
  const chunk = items.splice(0, 50);
  chunk.forEach(processItem);
  if (items.length > 0) setTimeout(() => processItems(items), 0);
}

// Web Worker
const worker = new Worker('heavy-task.js');
```

## CLS — Cumulative Layout Shift

### Causes + Solutions
| Cause | Solution |
|-------|----------|
| Images sans dimensions | `width`/`height` ou `aspect-ratio` |
| Annonces/embeds | Réservation d'espace (`min-height`) |
| Web fonts | `font-display: swap` |
| Contenu injecté | Positionnement statique |

```html
<img width="800" height="450" src="..." />
<div style="aspect-ratio: 16/9"><img src="..." /></div>
<div style="min-height: 250px" id="ad-slot"></div>
<link href="..." rel="stylesheet" />
<link rel="preload" as="font" href="/inter.woff2" crossorigin />
```

## TTFB — Time to First Byte

```
TTFB = Redirect + DNS + TCP + TLS + Server processing
```

### Optimisation
- **CDN** — Cloudflare, Fastly, CloudFront
- **Edge** — Cloudflare Workers, Vercel Edge
- **Caching** — HTTP, CDN, Service Worker
- **HTTP/2 & HTTP/3** — multiplexing, 0-RTT
- **Preconnect** — origines tierces

```html
<link rel="preconnect" href="https://api.example.com" />
<link rel="dns-prefetch" href="https://api.example.com" />
```

## RUM — Real User Monitoring

```js
import { onLCP, onINP, onCLS, onFCP, onTTFB } from 'web-vitals';
function sendToAnalytics({ name, value, rating }) {
  navigator.sendBeacon('/analytics', JSON.stringify({ name, value, rating }));
}
[onLCP, onINP, onCLS, onFCP, onTTFB].forEach(fn => fn(sendToAnalytics));
```

### Services RUM
| Service | Gratuit |
|---------|---------|
| Google CrUX | Oui (agrégé Chrome) |
| Vercel Analytics | Oui (limité) |
| Cloudflare Web Analytics | Oui |
| Plausible | Payant |
| Grafana Faro | OSS gratuit |

## Lighthouse

### Scoring
```
Performance = LCP(25%) + TBT(25%) + CLS(15%) + SI(15%) + FCP(10%) + TTI(10%)
```

### Budget
```json
{
  "budget": [
    { "resourceSize": { "total": 500, "script": 200, "image": 200 } },
    { "timings": { "lcp": 2500, "fcp": 1800, "cls": 0.1 } }
  ]
}
```

## Optimisation Images

| Format | Usage |
|--------|-------|
| WebP | Photos, illustrations (lossy + lossless) |
| AVIF | Photos (meilleur ratio) |
| SVG | Icônes, logos vectoriels |
| JPEG | Compatibilité maximale |

```html
<picture>
  <source srcset="/image.avif" type="image/avif" />
  <source srcset="/image.webp" type="image/webp" />
  <img src="/image.jpg" width="800" height="450" alt="" loading="lazy" />
</picture>
```

## Composants Clés par Métrique
```
TTFB → CDN, Cache, Preconnect
FCP  → CSS critique, Font loading
LCP  → Image, SSR, Preload
INP  → Bundle JS, Web Workers, Hydration
CLS  → Dimensions, Font-display, Reserved space
```

## Pièges Courants
- **Mesurer en dev** — tester en prod avec throttling
- **Lazy loading LCP** — ne pas mettre `loading="lazy"` sur l'image LCP
- **Trop de librairies** — chaque dépendance = JS + requêtes
- **Fonts Google** — toujours `display=swap`

## Références
- [web.dev/vitals](https://web.dev/vitals)
- [Lighthouse](https://developer.chrome.com/docs/lighthouse)
- [WebPageTest](https://www.webpagetest.org)
- [CrUX API](https://developer.chrome.com/docs/crux/api)
- [web-vitals library](https://github.com/GoogleChrome/web-vitals)
- [PageSpeed Insights](https://pagespeed.web.dev)
- [BundlePhobia](https://bundlephobia.com)
- [Squoosh](https://squoosh.app)