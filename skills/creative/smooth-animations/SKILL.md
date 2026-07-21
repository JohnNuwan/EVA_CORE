---
title: Smooth Animations & Transitions
description: Animations fluides pour le web — GSAP, Framer Motion, CSS Animations avancées, page transitions, scroll-triggered, parallax
category: creative
author: E.V.A
tags: [animation, gsap, framer-motion, css-animations, scroll, parallax, webgl]
version: 1.0
---

# Smooth Animations & Transitions

## Technologies Dominantes (Award-Winners)

D'après l'analyse des sites Awwwards, CSSDA, FWA :

| Technologie | Usage | Sites |
|-------------|-------|-------|
| **GSAP** | Animations scroll, timeline, stagger | IZANAMI, Lama Lama, 60%+ des SOTD |
| **CSS Animations** | Transitions simples, hover states | Universel |
| **Framer Motion** | React, page transitions | Sites en Next.js/React |
| **WebGL (Three.js)** | 3D, particules, arrière-plans | IZANAMI, Brunello Cucinelli |
| **Canvas API** | Dessin interactif, cursor trails | Lama Lama, sites créatifs |
| **Lenis** | Smooth scroll | La lib standard des award-winners |

## GSAP — Le Standard des Award-Winners

### ScrollTrigger
```js
// Animation déclenchée au scroll (GSAP ScrollTrigger)
gsap.registerPlugin(ScrollTrigger);

gsap.from('.hero-title', {
  scrollTrigger: {
    trigger: '.hero-title',
    start: 'top 80%',
    end: 'top 20%',
    toggleActions: 'play none none reverse',
  },
  y: 60,
  opacity: 0,
  duration: 0.8,
  ease: 'power3.out'
});
```

### Stagger (grille d'éléments)
```js
gsap.from('.grid-item', {
  scrollTrigger: {
    trigger: '.grid-section',
    start: 'top 75%',
  },
  y: 40,
  opacity: 0,
  duration: 0.6,
  stagger: 0.08,
  ease: 'power2.out'
});
```

### Timeline Complexe
```js
const tl = gsap.timeline({
  scrollTrigger: {
    trigger: '.section',
    start: 'top top',
    end: 'bottom top',
    scrub: 1,           // lié à la position du scroll
    pin: true,
  }
});
tl.from('.parallax-1', { y: -200 })
  .from('.parallax-2', { y: 100, scale: 0.8 })
  .to('.overlay', { opacity: 0 });
```

### Morph SVG
```js
gsap.to('.path', {
  duration: 0.8,
  morphSVG: '.path-final',
  ease: 'power2.inOut'
});
```

## Framer Motion (React)

```jsx
import { motion, AnimatePresence } from 'framer-motion';

// Page transition
const pageVariants = {
  initial: { opacity: 0, y: 20 },
  enter: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
  exit: { opacity: 0, y: -20, transition: { duration: 0.2 } }
};

<motion.div
  variants={pageVariants}
  initial="initial"
  animate="enter"
  exit="exit"
>
  {children}
</motion.div>

// Stagger children
const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.1 } }
};
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
};
```

## CSS Animations Avancées

### Smooth Reveal
```css
.reveal {
  animation: reveal 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  clip-path: inset(0 100% 0 0);
}
@keyframes reveal {
  to { clip-path: inset(0 0 0 0); }
}
```

### Floating / Float Animation
```css
.float {
  animation: float 6s ease-in-out infinite;
}
@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33% { transform: translateY(-10px) rotate(1deg); }
  66% { transform: translateY(5px) rotate(-1deg); }
}
```

### Magnetic Button
```css
.magnetic-btn {
  transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

```js
// Avec JS pour l'effet magnétique
btn.addEventListener('mousemove', (e) => {
  const rect = btn.getBoundingClientRect();
  const x = (e.clientX - rect.left - rect.width/2) * 0.3;
  const y = (e.clientY - rect.top - rect.height/2) * 0.3;
  btn.style.transform = `translate(${x}px, ${y}px)`;
});
btn.addEventListener('mouseleave', () => {
  btn.style.transform = 'translate(0, 0)';
});
```

## Parallax Layers (IZANAMI Style)

```css
.parallax-container {
  perspective: 1px;
  height: 100vh;
  overflow-x: hidden;
  overflow-y: auto;
}
.parallax-layer {
  position: absolute;
  top: 0; left: 0; right: 0;
}
.parallax-layer--bg {
  transform: translateZ(-1px) scale(2);
}
.parallax-layer--mid {
  transform: translateZ(-0.5px) scale(1.5);
}
```

## Performance Guide

| Technique | GPU | CPU | Notes |
|-----------|-----|-----|-------|
| transform/opacity | ✅ Accéléré | Faible | Toujours préférer |
| clip-path | ✅ Accéléré | Moyen | Bon pour les reveals |
| filter: blur | ✅ Accéléré | Élevé | Limiter aux overlays |
| height/width | ❌ Layout | Élevé | Éviter en animation |
| top/left | ❌ Layout | Élevé | Utiliser translate |

## Pièges
- ⚠️ `transform: translateZ(0)` pour forcer l'accélération GPU
- ⚠️ `will-change: transform` avec modération (consommation mémoire)
- ⚠️ `prefers-reduced-motion: no-preference` pour le motion toggle
- ⚠️ GSAP + React → utiliser useGSAP() hook officiel
- ⚠️ ScrollTrigger sans refresh() sur resize → gsap.matchMedia()