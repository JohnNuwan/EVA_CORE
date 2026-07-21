---
name: ssr-ssg
description: "Guide complet SSR, SSG, ISR, Streaming SSR : architectures, stratégies de rendu, hydratation, performance SEO, frameworks compatibles."
tags: [ssr, ssg, isr, streaming, rendu-serveur, hydratation, seo, performance, nextjs, nuxt, sveltekit, astro]
---

# SSR/SSG — Rendu Côté Serveur et Sites Statiques

## Stratégies de Rendu

| Stratégie | Rendu | Bundle JS | SEO | Revalidation |
|-----------|-------|-----------|-----|--------------|
| **CSR** | Navigateur | Lourd | Mauvais | N/A |
| **SSR** | Serveur + Client | Lourd | Excellent | Chaque requête |
| **SSG** | Build time | Léger | Excellent | Rebuild |
| **ISR** | Build + Runtime | Léger | Excellent | Intervalle/on-demand |
| **Streaming SSR** | Progressif | Progressif | Excellent | Temps réel |

## CSR (Client-Side Rendering)
```
HTML vide → JS chargé → Render → API call → DOM
```
**Quand :** apps internes, SaaS, jeux. **Problème :** LCP lent, SEO limité.

## SSR (Server-Side Rendering)
```
HTML complet (serveur) + JS → Hydratation → Interactif
```
```tsx
import { renderToString } from 'react-dom/server';
const html = renderToString(<StaticRouter><App /></StaticRouter>);
hydrateRoot(document.getElementById('root'), <BrowserRouter><App /></BrowserRouter>);
```
**Quand :** dashboard, e-commerce, données temps réel. **Problème :** TTFB lent, charge serveur.

## Streaming SSR (React 18+)
```
Shell HTML immédiat → Contenu streamé → Hydratation sélective
```
```tsx
const { pipe } = renderToPipeableStream(<App />, {
  onShellReady() { pipe(res); },
});
```
**Avantages :** TTFB ultra-rapide, hydratation prioritaire, meilleur INP.

## SSG (Static Site Generation)
```
Build → fetch data → generate HTML → CDN
```
```tsx
export async function generateStaticParams() {
  const products = await db.products.findMany({ select: { id: true } });
  return products.map(p => ({ id: p.id.toString() }));
}
```

### Outils SSG
| Outil | Type | Particularité |
|-------|------|---------------|
| Next.js | Framework React | ISR, `generateStaticParams` |
| Astro | Islands | Zéro JS par défaut |
| Gatsby | React | Plugin ecosystem |
| 11ty | SSG simple | Multi-format |
| Hugo | SSG Go | Ultra-rapide |
| Vitepress | SSG docs | Markdown → site |

## ISR (Incremental Static Regeneration)
```tsx
fetch(url, { next: { revalidate: 60 } }); // 60s
await revalidatePath('/products');         // On-demand
```
**Quand :** catalogue produits, blog avec MAJ fréquentes.

## Hydratation

| Type | Description |
|------|-------------|
| **Classique** | React hydrate tout le DOM |
| **Partial** (Islands) | Seuls les composants interactifs sont hydratés (Astro) |
| **Selective** | Hydratation par priorité (React 18 + Suspense) |
| **Resumability** | Pas d'hydratation — tout dans le HTML (Qwik) |

## Performances

| Métrique | CSR | SSR | SSG | Streaming |
|----------|-----|-----|-----|-----------|
| TTFB | Très rapide | Lent | Très rapide | Très rapide |
| LCP | Très lent | Rapide | Très rapide | Rapide |
| INP | Moyen | Moyen | Excellent | Bon |

## Stratégie de Choix
- **SSG** — Blog, docs, landing pages
- **SSR** — Dashboard, e-commerce, données perso
- **ISR** — Catalogue, blog MAJ fréquentes
- **Streaming** — Pages complexes sections lentes/rapides
- **CSR** — Apps internes, outils SaaS

## Pièges Courants
- **SSR + `window`** — toujours `typeof window !== 'undefined'`
- **Hydratation mismatch** — dates, IDs aléatoires
- **ISR + transactions** — ne pas utiliser pour panier/auth
- **Bundle trop lourd** — Server Components + code splitting

## Références
- [Next.js Rendu](https://nextjs.org/docs/app/building-your-application/rendering)
- [React 18 Streaming](https://react.dev/reference/react-dom/server/renderToPipeableStream)
- [Astro Islands](https://docs.astro.build/en/concepts/islands)
- [Web Vitals Rendering](https://web.dev/articles/rendering-on-the-web)
- [Vercel ISR](https://vercel.com/docs/incremental-static-regeneration)