---
title: "Patterns d'Animation pour UI de Jeux Vidéo"
description: "Catalogue de patterns d'animation UI pour jeux vidéo — transitions, feedback, micro-interactions, HUD dynamique, menus animés. Références des jeux primés aux GDC Awards, BAFTA Games, The Game Awards."
category: creative
tags: [ui-animation, game-ui, transitions, micro-interactions, hud]
---

# Patterns d'Animation pour UI de Jeux Vidéo

## Principes Fondamentaux

### Les 12 Principes d'Animation Appliqués à l'UI
1. **Squash & Stretch**: Boutons qui s'étirent au clic
2. **Anticipation**: Tooltip qui apparaît avant le survol
3. **Mise en scène**: Éléments importants qui arrivent en premier
4. **Straight Ahead / Pose to Pose**: Keyframes vs interpolation
5. **Follow Through & Overlapping**: Éléments qui continuent après le mouvement
6. **Slow In & Slow Out**: Easing (cubic-bezier, spring)
7. **Arc**: Mouvements naturels en courbe
8. **Secondary Action**: Particules, glow, ombres
9. **Timing**: Durée des animations (50ms-500ms)
10. **Exaggeration**: Feedback amplifié pour actions importantes
11. **Solid Drawing**: Cohérence visuelle
12. **Appeal**: UI agréable à regarder

## Catégories de Patterns

### 1. Transitions d'Écran

| Pattern | Durée | Easing | Usage |
|---------|-------|--------|-------|
| Fade | 200-400ms | ease-in-out | Menus simples |
| Slide | 300-500ms | ease-out | Navigation latérale |
| Zoom | 300-400ms | ease-out | Focus sur élément |
| Scale | 200-300ms | spring | Boutons, cartes |
| Morph | 400-600ms | ease-in-out | Transformation d'élément |
| Stagger | 50-100ms/item | ease-out | Listes, grilles |
| Mask | 300-500ms | ease-in-out | Révélation créative |

**Références Primées**:
- **God of War Ragnarök (BAFTA 2023)**: Transitions de menu cinématiques
- **Ratchet & Clank: Rift Apart (GDCA 2022)**: Transitions dimensionnelles
- **Ghost of Tsushima (GDCA 2021)**: Transitions naturelles (vent, feuilles)

### 2. Micro-Interactions

| Type | Durée | Effet |
|------|-------|-------|
| Hover | 100-150ms | Scale 1.05, glow, highlight |
| Click | 50-100ms | Scale 0.95, ripple |
| Toggle | 200-300ms | Slide/rotate avec easing spring |
| Progress | 500-2000ms | Barre qui se remplit, particules |
| Notification | 300-500ms apparition, 3000ms affichage | Slide-in, bounce |
| Tooltip | 200ms délai, 150ms apparition | Fade + slide |
| Loading | Continu | Spinner, skeleton, progress |

**Références Primées**:
- **Hi-Fi Rush (BAFTA 2024)**: Animations synchronisées sur le beat
- **Astro Bot (TGA 2024, BAFTA 2025)**: Feedback haptique + visuel
- **Control (GDCA 2020)**: UI dynamique qui réagit aux pouvoirs

### 3. HUD Dynamique

**Éléments**:
- **Barre de vie**: Animation fluide (pas instantanée)
- **Mini-carte**: Rotation, zoom, ping
- **Inventaire**: Grille avec animations d'ouverture
- **Compétences**: Cooldown visuel, recharge animée
- **Notifications**: File d'attente avec priorité
- **Indicateurs de dégâts**: Direction, type, intensité

**Patterns**:
- **Diegetic UI**: Dans le monde (Dead Space, Horizon) — plus immersif
- **Non-diegetic UI**: Superposé (HUD classique) — plus lisible
- **Spatial UI**: Dans l'espace 3D (Iron Man VR) — contextuel
- **Meta UI**: En dehors du jeu (inventaire, carte) — fonctionnel

**Références Primées**:
- **Horizon Forbidden West (BAFTA 2022)**: HUD diégétique avec hologrammes
- **Dead Space (GDCA 2009 Audio)**: Barre de vie intégrée au costume
- **Metroid Dread (TGA 2021)**: Mini-carte et transitions fluides

### 4. Menus Animés

**Éléments Clés**:
- **Background animé**: Parallax, vidéo, particules
- **Curseur personnalisé**: Animation au survol
- **Liste déroulante**: Stagger animation des items
- **Boutons**: Hover, active, disabled states
- **Checkboxes/Radio**: Animation de coche
- **Sliders**: Handle qui suit le curseur

**Bonnes Pratiques**:
- Toujours < 500ms pour les animations fonctionnelles
- Easing spring pour les interactions utilisateur
- Les éléments non-interactifs ne doivent pas distraire
- Cohérence des easing dans tout le jeu

### 5. Feedback Visuel

**Actions du Joueur**:
- **Clic/Sélection**: Pulse, glow, scale
- **Erreur**: Shake, rouge, flash
- **Succès**: Particules, glow vert, checkmark animé
- **Attente**: Spinner, skeleton, barre de progression
- **Changement d'état**: Transition fluide, icon morph

**Événements du Jeu**:
- **Dégâts**: Red flash, vignette, écran qui tremble
- **Soin**: Green pulse, particules montantes
- **Level up**: Explosion de lumière, célébration
- **Quête complétée**: Checkmark, confettis
- **Mort**: Désaturation, ralenti, fondu

## Techniques d'Implémentation

### CSS/Web (pour UI web-based)
```css
.btn {
  transition: transform 150ms ease-out, box-shadow 150ms ease-out;
}
.btn:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}
.btn:active {
  transform: scale(0.95);
}
```

### Timeline d'Animation (Game Engine)
```
State: Idle → Hover → Active → Disabled
Duration: 150ms → 100ms → 300ms
Easing: ease-out → ease-in → ease-in-out
```

### Structuration des Animations
```
Animation Layer:
  ├── Background (lent, continu)
  ├── Content (moyen, réactif)
  ├── Interactive (rapide, feedback)
  └── Effects (particules, glow)
```

## Références par Jeu Primé

| Jeu | Prix | Catégorie UI/Animation |
|-----|------|----------------------|
| **God of War Ragnarök** | BAFTA 2023 | Animation, UI contextuelle |
| **Hi-Fi Rush** | BAFTA 2024 | Animation synchronisée |
| **Astro Bot** | BAFTA 2025, TGA 2024 | HUD minimaliste, feedback |
| **Ratchet & Clank: Rift Apart** | GDCA 2022, BAFTA 2022 | Transitions dimensionnelles |
| **Control** | GDCA 2020 | UI dynamique, effets |
| **Ghost of Tsushima** | GDCA 2021 | UI naturelle, vent |
| **Alan Wake 2** | GDCA 2024 | UI live-action, meta |
| **Black Myth: Wukong** | GDCA 2025 | UI épique, animations |

## Pitfalls

- **Animations trop lentes** → frustration utilisateur
- **Incohérence des easing** → sensation désagréable
- **Trop d'animations simultanées** → confusion cognitive
- **Pas de feedback** → l'utilisateur ne sait pas si son action a fonctionné
- **Animation sans fonction** → superflu, distractif

## Voir Aussi

- [game-ai-character-design](../game-ai-character-design/SKILL.md)
- [holographic-interface-design](../holographic-interface-design/SKILL.md)
- [video-game-award-winning-ui](../video-game-award-winning-ui/SKILL.md)