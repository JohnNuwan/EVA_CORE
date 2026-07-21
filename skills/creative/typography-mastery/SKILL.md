---
title: Typographie Web & Variable Fonts
description: Typographie pour le web moderne — variable fonts, hiérarchie, pairing, systèmes de taille fluide, performance
category: creative
author: E.V.A
tags: [typographie, variable-fonts, google-fonts, hierarchy, css, font-pairing]
version: 1.0
---

# Typographie Web & Variable Fonts

## Constat d'Exploration

L'analyse des sites award-winners révèle que **la typographie est l'élément #1**
qui distingue un site primé d'un site standard. Les tendances :

- **Variable fonts** présentes dans ~60% des SOTD
- **Très gros titres** (4-8rem) comme élément de design
- **Tracking large** (letter-spacing: 0.05-0.15em) pour l'élégance
- **Hiérarchie minimaliste** — max 2-3 tailles de police

## Variable Fonts

### Avantages
```css
/* Un seul fichier = tout le spectrum */
@font-face {
  font-family: 'Inter';
  src: url('Inter.var.woff2') format('woff2');
  font-weight: 100 900;
  font-stretch: 75% 100%;
}

/* Usage */
h1 {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
}
.light {
  font-weight: 300;
  font-stretch: 75%;
}
```

### Fonts Variables Populaires (Award-Winners)
| Font | Axes disponibles | Sites |
|------|------------------|-------|
| Inter | wght, slnt | Généraliste |
| Satoshi | wght | Design studios |
| General Sans | wght, ital | FLOT NOIR |
| Cabinet Grotesk | wght | Agences créatives |
| Zodiak | wght, ital | Studios design |
| Diatype | wght | Swiss design |

### Fluid Type Scale (CSS Clamp)
```css
/* Échelle fluide — s'adapte à la viewport */
:root {
  --text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);
  --text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);
  --text-base: clamp(1rem, 0.9rem + 0.5vw, 1.125rem);
  --text-lg: clamp(1.125rem, 1rem + 0.625vw, 1.25rem);
  --text-xl: clamp(1.25rem, 1.1rem + 0.75vw, 1.5rem);
  --text-2xl: clamp(1.5rem, 1.3rem + 1vw, 2rem);
  --text-3xl: clamp(2rem, 1.5rem + 2vw, 3rem);
  --text-4xl: clamp(2.5rem, 1.8rem + 3vw, 4rem);
  --text-5xl: clamp(3rem, 2rem + 5vw, 6rem);
}
```

## Pairing (Associations Testées)

### Classiques
```
Titre: Inter (700) + Corps: Inter (400)
→ Monochrome, sûr, élégant
```

### Contraste
```
Titre: Playfair Display (700) + Corps: Inter (400)
→ Sérif + Sans-sérif, editorial
```

### Moderne
```
Titre: Satoshi (700) + Corps: Satoshi (400)
→ Variable, tracking large, minimal
```

### Technique
```
Titre: JetBrains Mono (700) + Corps: Inter (400)
→ Monospace + Sans, vibe tech
```

## Hiérarchie Typographique

```css
/* Système de titres */
h1 {
  font-size: var(--text-5xl);
  font-weight: 700;
  letter-spacing: -0.02em;
  line-height: 1.05;
}
h2 {
  font-size: var(--text-3xl);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1.1;
}
h3 {
  font-size: var(--text-2xl);
  font-weight: 600;
  line-height: 1.2;
}
p {
  font-size: var(--text-base);
  line-height: 1.6;
  max-width: 65ch;        /* Lecture confortable */
}
.caption {
  font-size: var(--text-sm);
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--text-secondary);
}
```

## Tracking & Kerning

```css
.tracking-tight { letter-spacing: -0.02em; }
.tracking-normal { letter-spacing: 0; }
.tracking-wide { letter-spacing: 0.05em; }
.tracking-wider { letter-spacing: 0.1em; }
.tracking-widest { letter-spacing: 0.15em; }

/* Award-winner style: large tracking sur uppercase */
.nav-link {
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
```

## Performance Font

```html
<!-- Stratégie: display=swap + preload -->
<link rel="preload" 
      href="/fonts/Inter.var.woff2" 
      as="font" 
      type="font/woff2" 
      crossorigin>

<!-- Subset + WOFF2 uniquement -->
<!-- Éviter Google Fonts en prod → self-host -->
```

## Feature Settings CSS
```css
.typography-advanced {
  font-variant-numeric: tabular-nums;  /* Chiffres alignés */
  font-optical-sizing: auto;            /* Optical sizing */
  font-kerning: normal;                 /* Kerning automatique */
  text-rendering: optimizeLegibility;   /* Meilleur rendu */
  -webkit-font-smoothing: antialiased;  /* Anti-aliasing */
  -moz-osx-font-smoothing: grayscale;
}
```

## Pièges
- ⚠️ Web Safe Fonts → trop limité pour un award-winner
- ⚠️ Google Fonts en prod → latence, privacy, pas de contrôle
- ⚠️ Trop de font-weights → ralentit le chargement
- ⚠️ line-height trop serré → illisible sur mobile
- ⚠️ text-shadow sur body text → flou, mauvais contraste