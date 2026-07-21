---
name: tailwind-css
description: "Guide complet Tailwind CSS v4 : utility-first, configuration, responsive, dark mode, variants, plugins, optimisation, intégration frameworks."
tags: [tailwind, tailwindcss, css, utility-first, responsive, dark-mode, design-system, postcss, vite, nextjs]
---

# Tailwind CSS — Framework Utilitaire

## Philosophie Utility-First

Au lieu de CSS personnalisé, on compose des classes utilitaires dans le HTML/JSX :

```html
<div class="p-6 max-w-sm mx-auto bg-white rounded-xl shadow-md flex items-center space-x-4">
  <img class="size-12" src="/logo.svg" alt="Logo" />
  <div>
    <div class="text-xl font-medium text-black">Titre</div>
    <p class="text-gray-500">Sous-titre</p>
  </div>
</div>
```

**Avantages :** pas de nommage, design cohérent, petit bundle (purge CSS), responsive natif, rapide.

## Tailwind v4 (nouveau)

### Installation
```bash
npm install tailwindcss @tailwindcss/vite
```

```ts
// vite.config.ts
import tailwindcss from '@tailwindcss/vite';
export default { plugins: [tailwindcss()] };
```

```css
/* app.css — un seul import */
@import "tailwindcss";
```

### Nouveautés v4
- **CSS-first config** — plus de `tailwind.config.js` par défaut
- **`@theme`** directive — design tokens dans CSS
- **`@variant`** / **`@utility`** — variants et utilitaires custom inline
- **Engine Rust (Oxide)** — build 2–5× plus rapide

```css
@theme {
  --color-brand: #ff6b35;
  --font-display: "Inter", sans-serif;
  --breakpoint-xs: 30rem;
}
```

## Classes Essentielles

### Layout
`container`, `flex`, `grid`, `gap-{size}`, `grid-cols-{n}`, `items-center`, `justify-between`

### Spacing
`p-{size}`, `px-{size}`, `py-{size}`, `m-{size}`, `mx-auto`, `space-x-{size}`

### Typographie
`text-{xs/sm/base/lg/xl/2xl-9xl}`, `font-{thin/light/normal/medium/semibold/bold}`, `leading-{none/tight/normal/relaxed/loose}`, `tracking-{tighter/tight/normal/wide}`

### Couleurs
Palette : `slate/gray/zinc/neutral/stone/red/orange/amber/yellow/lime/green/emerald/teal/cyan/sky/blue/indigo/violet/purple/fuchsia/pink/rose` — shades `50–950`

### Responsive
```html
<div class="text-base md:text-lg lg:text-xl">
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
```

### Dark Mode
```html
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
```

### States
`hover:`, `focus:`, `active:`, `disabled:`, `group-hover:`, `peer:`

### Animations
`animate-spin`, `animate-ping`, `animate-pulse`, `animate-bounce`

## Patterns Avancés
```html
<!-- Group Hover -->
<div class="group cursor-pointer">
  <h3 class="group-hover:text-blue-500">Titre</h3>
</div>

<!-- Arbitrary Values -->
<div class="w-[calc(100%-2rem)] text-[#ff6b35]">
```

## Plugins Officiels
```bash
npm install @tailwindcss/typography @tailwindcss/forms @tailwindcss/container-queries
```

## Intégration Frameworks
- **React/Next.js/Vue/Svelte** — classes utilitaires directement dans le template
- **`className="..."`** pour React, `class="..."` pour Vue/Svelte

## Pièges Courants
- **`@apply` excessif** — ré-introduit les problèmes de nommage
- **Classes dynamiques** — `text-${color}-500` ne fonctionne pas avec purge CSS
- **`content` manquant** — fichier CSS de 800KB+ (pas de purge)

## Références
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Tailwind v4 Upgrade Guide](https://tailwindcss.com/docs/upgrade-guide)
- [Cheat Sheet](https://nerdcave.com/tailwind-cheat-sheet)
- [Tailwind UI](https://tailwindui.com)
- [shadcn/ui](https://ui.shadcn.com)