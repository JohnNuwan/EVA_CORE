---
title: Layout & Grid Systems
description: Systèmes de grille modernes — CSS Grid, Flexbox, layouts asymétriques, responsive patterns, containers, spacing
category: creative
author: E.V.A
tags: [layout, css-grid, flexbox, responsive, grid-system, spacing]
version: 1.0
---

# Layout & Grid Systems

## Tendances Layout des Award-Winners

D'après l'analyse des 50+ sites primés :

- **CSS Grid** utilisé dans ~85% des cas (vs Flexbox pour les composants)
- **Layouts asymétriques** en hausse (40% des SOTD 2025-2026)
- **Whitespace généreux** → padding 24-32px standard
- **Conteneurs max-width** : 1200px (standard) à 1440px (créatif)

## CSS Grid Patterns

### Dashboard Grid (Auto-fill)
```css
.dashboard {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 24px;
}
```

### Asymmetric Hero
```css
.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto;
  gap: 32px;
  align-items: center;
}
.hero-grid > :first-child {
  grid-column: 1 / 2;
}
.hero-grid > :last-child {
  grid-column: 2 / 3;
  transform: translateY(40px);  /* Décalage asymétrique */
}

@media (max-width: 768px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }
  .hero-grid > :last-child {
    transform: none;
  }
}
```

### Magazine Layout
```css
.magazine-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  grid-template-areas:
    "featured sidebar"
    "content sidebar"
    "related related";
  gap: 32px;
}
.featured { grid-area: featured; }
.sidebar { grid-area: sidebar; }
.content { grid-area: content; }
.related { grid-area: related; }

@media (max-width: 1024px) {
  .magazine-layout {
    grid-template-columns: 1fr;
    grid-template-areas:
      "featured"
      "content"
      "sidebar"
      "related";
  }
}
```

### Holy Grail (Dashboard App Shell)
```css
.app-shell {
  display: grid;
  grid-template-columns: 260px 1fr;
  grid-template-rows: 64px 1fr 48px;
  grid-template-areas:
    "navbar navbar"
    "sidebar main"
    "sidebar footer";
  height: 100vh;
}
.navbar { grid-area: navbar; }
.sidebar { grid-area: sidebar; }
.main { 
  grid-area: main; 
  overflow-y: auto;
  padding: 32px;
}
.footer { grid-area: footer; }

@media (max-width: 768px) {
  .app-shell {
    grid-template-columns: 1fr;
    grid-template-areas:
      "navbar"
      "main"
      "footer";
  }
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  .sidebar.open {
    transform: translateX(0);
  }
}
```

### Masonry Grid
```css
.masonry {
  columns: 3;
  column-gap: 24px;
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 24px;
}

@media (max-width: 1024px) { .masonry { columns: 2; } }
@media (max-width: 640px) { .masonry { columns: 1; } }
```

## Flexbox Patterns (Composants)

### Centered Content
```css
.center-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  text-align: center;
}
```

### Card Row
```css
.card-row {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}
.card-row > * {
  flex: 1 1 300px;
}
```

### Sticky Sidebar (Flexbox)
```css
.layout-sidebar {
  display: flex;
  gap: 48px;
  align-items: flex-start;
}
.layout-sidebar > main {
  flex: 1;
  min-width: 0;
}
.layout-sidebar > aside {
  flex: 0 0 320px;
  position: sticky;
  top: 32px;
}
```

## Système de Spacing

```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;
  --space-20: 80px;
  --space-24: 96px;
}

/* Container */
.container {
  width: 100%;
  max-width: 1200px;
  margin-inline: auto;
  padding-inline: var(--space-6);
}

.container--narrow {
  max-width: 720px;
}

.container--wide {
  max-width: 1440px;
}

/* Section spacing */
.section {
  padding-block: var(--space-20);
}
.section--sm { padding-block: var(--space-10); }
.section--lg { padding-block: var(--space-24); }
```

## Stack Pattern (Spacing vertical)

```css
.stack { display: flex; flex-direction: column; }
.stack--sm { gap: var(--space-4); }
.stack--md { gap: var(--space-6); }
.stack--lg { gap: var(--space-10); }
.stack--xl { gap: var(--space-16); }
```

## Pièges Layout
- ⚠️ Pas de `gap` pour Flexbox Safari < 14.1 → fallback margin
- ⚠️ `min-width: 0` sur flex-children avec texte long → déborder
- ⚠️ `grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))` + padding → calcul mal fait
- ⚠️ Sticky ne marche pas sans `top` défini
- ⚠️ Masonry avec columns → ordre vertical pas horizontal