---
title: Neumorphism / Soft UI Design
description: Design neumorphe — ombres extrudées, composants mous, alternance dark/light neumorphism, patterns tactiles
category: creative
author: E.V.A
tags: [neumorphism, soft-ui, skeuomorphism, ombres, tactile]
version: 1.0
---

# Neumorphism / Soft UI

## Définition

Le neumorphism (ou Soft UI) crée des interfaces tactiles où les éléments semblent
extrudés ou enfoncés dans le fond. Contrairement au flat design, il utilise des
ombres intérieures et extérieures pour simuler la profondeur.

## Références Dribbble

- **Neumorphism UI Trend 2023** (20.6k likes) — Guide complet
- **Neumorphism UI Elements** (443k vues) — Boutons, sliders, toggle
- **Smart Home App** (122k likes) — Design neumorphe en contexte IoT
- **Neumorphism UI Trend 2020** (594k vues) — Le trend original

## Formule de Base

### Neumorphism Extrudé (bouton bombé)
```css
.neumorph {
  background: #E0E5EC;
  border-radius: 20px;
  box-shadow:
    9px 9px 16px rgba(163, 177, 198, 0.6),    /* ombre foncée (bas/droite) */
    -9px -9px 16px rgba(255, 255, 255, 0.8);   /* lumière haute (haut/gauche) */
}
```

### Neumorphism Enfoncé (bouton pressé)
```css
.neumorph--pressed {
  background: #E0E5EC;
  border-radius: 20px;
  box-shadow:
    inset 9px 9px 16px rgba(163, 177, 198, 0.6),
    inset -9px -9px 16px rgba(255, 255, 255, 0.8);
}
```

## Version Dark Neumorphism

```css
.neumorph-dark {
  background: #1A1A2E;
  border-radius: 20px;
  box-shadow:
    9px 9px 16px rgba(0, 0, 0, 0.5),
    -9px -9px 16px rgba(255, 255, 255, 0.05);
}

.neumorph-dark--pressed {
  background: #1A1A2E;
  box-shadow:
    inset 9px 9px 16px rgba(0, 0, 0, 0.5),
    inset -9px -9px 16px rgba(255, 255, 255, 0.05);
}
```

## Composants Neumorph

### Input / Search Bar
```css
.neumorph-input {
  background: #E0E5EC;
  border: none;
  border-radius: 16px;
  padding: 16px 24px;
  box-shadow:
    inset 4px 4px 8px rgba(163, 177, 198, 0.6),
    inset -4px -4px 8px rgba(255, 255, 255, 0.8);
  font-size: 16px;
  color: #333;
}
```

### Toggle Switch
```css
.neumorph-toggle {
  width: 60px;
  height: 32px;
  background: #E0E5EC;
  border-radius: 16px;
  box-shadow:
    inset 3px 3px 6px rgba(163, 177, 198, 0.6),
    inset -3px -3px 6px rgba(255, 255, 255, 0.8);
  cursor: pointer;
  position: relative;
}
.neumorph-toggle::after {
  content: '';
  position: absolute;
  width: 26px; height: 26px;
  background: #E0E5EC;
  border-radius: 50%;
  top: 3px; left: 3px;
  box-shadow:
    2px 2px 4px rgba(163, 177, 198, 0.6),
    -2px -2px 4px rgba(255, 255, 255, 0.8);
  transition: left 0.2s;
}
.neumorph-toggle.active::after {
  left: 31px;
  background: #6C63FF;
}
```

### Progress Ring
```css
.neumorph-ring {
  width: 120px; height: 120px;
  border-radius: 50%;
  background: #E0E5EC;
  box-shadow:
    6px 6px 12px rgba(163, 177, 198, 0.6),
    -6px -6px 12px rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
}
```

## Patterns par Contexte

| Contexte | Style | Commentaire |
|----------|-------|-------------|
| Dashboard dark | Neumorph sombre subtil | Ombre externes légères |
| Music Player | Neumorph classique | Très populaire sur Dribbble |
| Smart Home | Neumorph light | IoT apps |
| Calculator | Neumorph pur | Le cas d'usage classique |

## Pièges

- ⚠️ **Accessibilité** — Le faible contraste est le problème #1 du neumorphism
- ⚠️ **Couleur fond** — La couleur du fond doit être exactement entre l'ombre claire et foncée
- ⚠️ **Neumorph uniquement** — Ne jamais faire un site 100% neumorph (fatigue visuelle)
- ⚠️ **Fond dégradé** — Les ombres neumorphes ne fonctionnent pas sur fond dégradé
- ⚠️ **Mobile** — Tester les ombres sur écran OLED (noirs profonds)

## Recette des Ombres Parfaites

```
Propriété           | Light                 | Dark
-------------------|-----------------------|---------------------
Couleur fond       | #E0E5EC               | #1A1A2E
Ombre foncée       | rgba(163,177,198,0.6) | rgba(0,0,0,0.5)
Ombre claire       | rgba(255,255,255,0.8) | rgba(255,255,255,0.05)
Distance base      | 9px                   | 9px
Blur               | 16px                  | 16px
```

### Générateur CSS d'Ombres
```scss
@mixin neumorph($bg, $dark: darken($bg, 15%), $light: lighten($bg, 15%)) {
  background: $bg;
  box-shadow: 
    9px 9px 16px $dark,
    -9px -9px 16px $light;
}
```