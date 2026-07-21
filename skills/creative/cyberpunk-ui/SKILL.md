---
title: Cyberpunk UI Design
description: Aesthetic cyberpunk pour le web — néons, grilles, glitch, HUD, scanlines, interfaces futuristes
category: creative
author: E.V.A
tags: [cyberpunk, neon, ui, futuriste, glitch, sci-fi]
version: 1.0
---

# Cyberpunk UI Design

## Inspirations Clés

Recherches sur Dribbble, Awwwards, CSS Design Awards :

- **Complex HUD Backgrounds** (Dribbble, 80.8k likes) — Overlays de grille + scanlines
- **Cyberpunk 2077 PPT Template** (Dribbble, 10.4k likes) — UI jeu vidéo
- **RISK** (Awwwards SOTD) — Design sombre agressif
- **FLOT NOIR** (Awwwards) — Dark + accents néon
- **Glitch&Grit** (Awwwards SOTD) — Esthétique grunge digitale

## Principes du Cyberpunk UI

1. **Fond sombre** — #0A0A0F à #0F0F1A
2. **Accents néon** — Cyan (#00FFF7), Magenta (#FF00FF), Vert (#00FF41), Orange (#FF6A00)
3. **Grilles de fond** — Lignes fines, perspective, isométrique
4. **Scanlines / CRT** — Lignes horizontales fines, distorsion
5. **Glitch** — Décallages RGB, artifacts, distortion
6. **Typographie** — Futuriste, uppercase, tracking large
7. **Bords tranchants** — Coins coupés à 45°, hexagones

## Patterns CSS

### Background Grille + Scanlines
```css
.cyber-grid {
  position: relative;
  background-color: #0A0A0F;
  background-image: 
    linear-gradient(rgba(0, 255, 247, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 255, 247, 0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}

.cyber-grid::after {
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    0deg,
    transparent,
    transparent 2px,
    rgba(0, 0, 0, 0.03) 2px,
    rgba(0, 0, 0, 0.03) 4px
  );
  pointer-events: none;
  z-index: 9999;
}
```

### Texte Néon
```css
.neon-text {
  color: #00FFF7;
  text-shadow:
    0 0 7px #00FFF7,
    0 0 10px #00FFF7,
    0 0 21px #00FFF7,
    0 0 42px #00FFF7;
}

.neon-text--magenta {
  color: #FF00FF;
  text-shadow:
    0 0 7px #FF00FF,
    0 0 10px #FF00FF,
    0 0 21px #FF00FF,
    0 0 42px #FF00FF;
}
```

### Bouton Cyberpunk
```css
.cyber-btn {
  position: relative;
  padding: 12px 32px;
  background: transparent;
  color: #00FFF7;
  border: 1px solid #00FFF7;
  text-transform: uppercase;
  letter-spacing: 4px;
  font-family: 'Courier New', monospace;
  clip-path: polygon(
    10px 0%, 100% 0%, calc(100% - 10px) 100%, 0% 100%
  );
  transition: all 0.3s;
}
.cyber-btn:hover {
  background: rgba(0, 255, 247, 0.1);
  box-shadow: 
    inset 0 0 30px rgba(0, 255, 247, 0.2),
    0 0 30px rgba(0, 255, 247, 0.2);
}
.cyber-btn::after {
  content: '▸';
  margin-left: 12px;
}
```

### Card Cyberpunk
```css
.cyber-card {
  background: rgba(10, 10, 15, 0.9);
  border: 1px solid rgba(0, 255, 247, 0.2);
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.cyber-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 4px;
  height: 100%;
  background: linear-gradient(#00FFF7, #FF00FF);
}
```

### Glitch Effect
```css
@keyframes glitch {
  0% { transform: translate(0); }
  20% { transform: translate(-2px, 2px); }
  40% { transform: translate(-2px, -2px); }
  60% { transform: translate(2px, 2px); }
  80% { transform: translate(2px, -2px); }
  100% { transform: translate(0); }
}
.glitch:hover {
  animation: glitch 0.3s ease-in-out;
}

/* RGB Split Glitch */
.rgb-glitch {
  position: relative;
}
.rgb-glitch::before,
.rgb-glitch::after {
  content: attr(data-text);
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 100%;
}
.rgb-glitch::before {
  color: #FF0000;
  clip-path: inset(20% 0 60% 0);
  animation: glitch-split 3s infinite;
}
.rgb-glitch::after {
  color: #00FFF7;
  clip-path: inset(60% 0 20% 0);
  animation: glitch-split 2.7s infinite reverse;
}
```

## Composants HUD

### HUD Corner Frame
```css
.hud-frame {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(0, 255, 247, 0.4);
}
.hud-frame--tl { top: 8px; left: 8px; border-right: none; border-bottom: none; }
.hud-frame--tr { top: 8px; right: 8px; border-left: none; border-bottom: none; }
.hud-frame--bl { bottom: 8px; left: 8px; border-right: none; border-top: none; }
.hud-frame--br { bottom: 8px; right: 8px; border-left: none; border-top: none; }
```

### Progress Bar Cyber
```css
.cyber-progress {
  height: 4px;
  background: rgba(0, 255, 247, 0.1);
  position: relative;
  overflow: hidden;
}
.cyber-progress::before {
  content: '';
  position: absolute;
  height: 100%;
  width: var(--progress, 50%);
  background: linear-gradient(90deg, #00FFF7, #FF00FF);
  animation: progress-pulse 2s ease-in-out infinite;
}
```

## Palette Cyberpunk (Dribbble Data)

| Couleur | Hex | Usage |
|---------|-----|-------|
| Fond | #0A0A0F | Body |
| Surface | #1A1A2E | Cards |
| Cyan | #00FFF7 | Accent primaire |
| Magenta | #FF00FF | Accent secondaire |
| Vert | #00FF41 | Succès / data |
| Orange | #FF6A00 | Warning |
| Text | #E0E0FF | Texte principal |

## Pièges Cyberpunk
- ⚠️ Overload visuel → équilibrer néon avec zones calmes
- ⚠️ Lisibilité → les néons fatiguent les yeux, limiter aux accents
- ⚠️ Accessibilité → les textes néon ont un ratio faible, doubler avec ombre
- ⚠️ Performance → les glitch effects en JS peuvent être lourds, CSS de préférence