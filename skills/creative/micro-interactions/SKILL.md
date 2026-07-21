---
title: Micro-Interactions Design
description: Micro-interactions UI — retours visuels, feedback loop, animations contextuelles, hover states, transitions
category: creative
author: E.V.A
tags: [micro-interactions, animation, feedback, ui, hover, transition]
version: 1.0
---

# Micro-Interactions Design

## Définition

Micro-interaction = un événement déclenché par l'utilisateur avec un retour visuel
immédiat (< 300ms). Quatre parties :

1. **Déclencheur** (hover, click, scroll, input)
2. **Règle** (ce qui se passe)
3. **Feedback** (l'animation visuelle)
4. **Mode/boucle** (état après l'interaction)

## Références Dribbble

- **Add Button Micro Interaction** (240k likes) — Bouton + → ✓ avec splash
- **Bottom Navigation Micro Interaction** (403k likes) — Tab bar animée
- **Card Scrolling Micro Interaction** (83.1k likes) — Scroll horizontal with snap
- **Daily UI 007 - Settings Tab** (82.5k likes) — Settings toggle animation
- **IZANAMI** (Awwwards) — Fluid navigation, parallax scroll, transitions
- **Lama Lama** (Awwwards) — Canvas cursor interaction, hover drawing

## Catalogue de Micro-Interactions

### 1. Hover Card Scale
```css
.card-hover {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), 
              box-shadow 0.2s ease;
}
.card-hover:hover {
  transform: scale(1.03) translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.15);
}
```

### 2. Button With Ripple
```css
.btn-ripple {
  position: relative;
  overflow: hidden;
}
.btn-ripple::after {
  content: '';
  position: absolute;
  width: 100%; height: 100%;
  top: 0; left: 0;
  background: radial-gradient(circle, rgba(255,255,255,0.3) 10%, transparent 10%);
  background-position: center;
  background-size: 0%;
  transition: background-size 0.4s;
}
.btn-ripple:active::after {
  background-size: 1000%;
}
```

### 3. Like Heart Animated
```css
@keyframes heart-pop {
  0% { transform: scale(1); }
  25% { transform: scale(1.3); }
  50% { transform: scale(0.95); }
  100% { transform: scale(1); }
}
.heart.liked {
  animation: heart-pop 0.4s ease;
  fill: #FF4757;
}
```

### 4. Input Focus
```css
.input-micro {
  border: 2px solid transparent;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.input-micro:focus {
  border-color: #6C63FF;
  box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.15);
}
```

### 5. Skeleton Loading
```css
@keyframes shimmer {
  0% { background-position: -200px 0; }
  100% { background-position: 200px 0; }
}
.skeleton {
  background: linear-gradient(90deg, 
    var(--surface) 25%, 
    var(--surface-2) 50%, 
    var(--surface) 75%
  );
  background-size: 400px 100%;
  animation: shimmer 1.5s ease-in-out infinite;
}
```

### 6. Toast Notification
```css
@keyframes slide-in {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
@keyframes slide-out {
  from { transform: translateX(0); opacity: 1; }
  to { transform: translateX(100%); opacity: 0; }
}
.toast {
  animation: slide-in 0.3s ease;
}
.toast.removing {
  animation: slide-out 0.3s ease;
}
```

### 7. Progress Bar Animated
```css
.progress-micro {
  height: 4px;
  border-radius: 2px;
  overflow: hidden;
}
.progress-micro::before {
  content: '';
  display: block;
  height: 100%;
  width: var(--progress);
  background: linear-gradient(90deg, #6C63FF, #FF6584);
  transition: width 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 8. Navigation Active Indicator
```css
.nav-micro {
  position: relative;
  padding: 8px 16px;
}
.nav-micro.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 100%;
  height: 2px;
  background: #6C63FF;
  animation: nav-in 0.3s ease;
}
@keyframes nav-in {
  from { transform: scaleX(0); }
  to { transform: scaleX(1); }
}
```

### 9. Checkbox / Toggle
```css
.toggle-micro {
  width: 44px; height: 24px;
  background: #ccc;
  border-radius: 12px;
  transition: background 0.2s;
  cursor: pointer;
}
.toggle-micro.active {
  background: #6C63FF;
}
.toggle-micro::after {
  content: '';
  width: 20px; height: 20px;
  background: white;
  border-radius: 50%;
  display: block;
  margin: 2px;
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.toggle-micro.active::after {
  transform: translateX(20px);
}
```

### 10. Scroll Progress
```css
.scroll-progress {
  position: fixed;
  top: 0; left: 0;
  height: 3px;
  background: linear-gradient(90deg, #6C63FF, #FF6584);
  width: var(--scroll, 0%);
  transition: width 0.1s linear;
  z-index: 9999;
}
```

## Timing Guide (Issu des Award-Winners)

| Interaction | Durée | Easing |
|--------------|-------|--------|
| Hover card | 200ms | ease-out |
| Button click | 150ms | ease |
| Modal open | 300ms | cubic-bezier(0.34, 1.56, 0.64, 1) |
| Page transition | 400-600ms | cubic-bezier(0.16, 1, 0.3, 1) |
| Notification | 300ms in, 4000ms visible, 300ms out | ease |
| Tooltip | 100ms delay, 150ms fade | ease-out |
| Progress bar | 600ms | cubic-bezier(0.34, 1.56, 0.64, 1) |

## Framework : Lottie / Rive

Pour des micro-interactions complexes :
```js
// Lottie (JSON animation)
import lottie from 'lottie-web';
lottie.loadAnimation({
  container: document.getElementById('interaction'),
  path: 'animation.json',
  renderer: 'svg',
  loop: false,
  autoplay: false
});
element.addEventListener('click', () => animation.play());
```

## Pièges
- ⚠️ Micro-interactions trop lentes → garder < 300ms
- ⚠️ Trop d'animations → désorientation utilisateur
- ⚠️ Réduire le mouvement → respecter `prefers-reduced-motion`
- ⚠️ Performance → préférer transform/opacity à left/top/width