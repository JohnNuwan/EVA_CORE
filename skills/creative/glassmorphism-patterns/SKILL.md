---
title: Glassmorphism Patterns
description: Maîtrise du glassmorphism — backdrop-filter, frost effect, depth layering, composants glass pour UI modernes
category: creative
author: E.V.A
tags: [glassmorphism, backdrop-filter, css, ui-trend, frost]
version: 1.0
---

# Patterns Glassmorphism

## Principe Fondamental

Le glassmorphism (ou "vitromorphisme") crée l'illusion de verre dépoli superposé.
Trois ingrédients essentiels :

1. **Transparence** — `rgba(255,255,255,0.15)` pour le fond
2. **Flou** — `backdrop-filter: blur(20px)` pour l'effet de verre
3. **Bordure subtile** — `border: 1px solid rgba(255,255,255,0.2)` pour la profondeur

## Formule de Base

```css
.glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}
```

## Variations par Contexte

### Glass Card (sombre)
```css
.glass-dark {
  background: rgba(10, 8, 1, 0.6);  /* #0A0801 inspiré IZANAMI */
  backdrop-filter: blur(24px) saturate(1.4);
  border: 1px solid rgba(217, 215, 212, 0.12);
}
```

### Glass Navbar
```css
.glass-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(1.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  z-index: 100;
}
```

### Glass Modal
```css
.glass-modal {
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(8px);
}
```

## Superpositions et Profondeur

Le glassmorphism brille avec des arrière-plans complexes :

```
┌─────────────────────────────────────────┐
│  Arrière-plan animé (gradient, vidéo)   │
│  ┌─────────────────────────────────┐    │
│  │  Couche glass (blur 20px)       │    │
│  │  ┌─────────────────────────┐   │    │
│  │  │  Contenu + ombre portée  │   │    │
│  │  └─────────────────────────┘   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘
```

## Patterns Composés

### Frost Sidebar
```css
.sidebar-glass {
  background: rgba(30, 30, 40, 0.7);
  backdrop-filter: blur(32px);
  border-right: 1px solid rgba(255,255,255,0.06);
}
```

### Glass Data Card
```css
.data-card-glass {
  background: linear-gradient(
    135deg,
    rgba(255,255,255,0.12) 0%,
    rgba(255,255,255,0.06) 100%
  );
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.15);
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
```

### Glass Input
```css
.input-glass {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255,255,255,0.1);
  transition: border-color 0.2s, background 0.2s;
}
.input-glass:focus {
  background: rgba(255,255,255,0.1);
  border-color: rgba(var(--accent-rgb), 0.5);
}
```

## Combinaison avec d'autres Trends

- **Glass + Dark Theme** → Le plus courant, profondeur maximale
- **Glass + Neumorphism** → "Glassmorphism neu" — éléments gaufrés avec flou
- **Glass + Gradient** → Le gradient en arrière-plan brille à travers le verre
- **Glass + Cyberpunk** → Verre teinté magenta/cyan avec glow

## Limitations / Pièges

| Problème | Solution |
|----------|----------|
| Performance sur mobile | `will-change: backdrop-filter` + test |
| Texte illisible | Doubler le contraste, ombre portée sur le texte |
| Superposition excessive | Max 2 couches glass superposées |
| Firefox Linux | `-webkit-backdrop-filter` peut manquer |
| Safari iOS | Test sur appareil réel, bugs de rendu connus |

## Exemple Complet : Hero Section

```html
<section class="hero">
  <video autoplay muted loop class="hero-bg">
    <source src="bg.mp4" type="video/mp4">
  </video>
  <div class="hero-content glass">
    <h1>Title avec text-shadow</h1>
    <p>Description avec ombre portée pour lisibilité</p>
    <button class="glass-btn">Action</button>
  </div>
</section>
```

```css
.hero-content.glass {
  background: rgba(0,0,0,0.3);
  backdrop-filter: blur(24px);
  padding: 48px;
  border-radius: 24px;
}
.hero-content h1 {
  text-shadow: 0 2px 20px rgba(0,0,0,0.5);
}
```

## Références Design
- **Glitch&Grit** (Awwwards SOTD) — navbar glass subtil
- **Brunello Cucinelli AI E-com** — overlays glass sur vidéo
- **Lama Lama** (Awwwards) — glass pour UI overlays