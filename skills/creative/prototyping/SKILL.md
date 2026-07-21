---
title: Prototypage — Design interactif & motion
description: Prototypage — outils, fidelity, interactions, micro-animations, transitions, gesture, feedback, testing utilisateur, design critique
category: creative
author: E.V.A
tags: [prototypage, prototyping, interactions, micro-interactions, animation, figma, motion, ui]
version: 1.0
---

# Prototypage — Design Interactif & Motion

## Qu'est-ce que le Prototypage ?

Le prototypage est la simulation d'une interface utilisateur pour tester des interactions, des flux et des comportements avant développement. Il permet de valider des hypothèses de design, de recueillir du feedback et de communiquer l'intention de conception.

### Niveaux de Fidelity
```yaml
Low-Fidelity (Papier, wireframe):
  - Croquis, boîtes grises
  - Pas d'interactions
  - Idéal pour : exploration, idéation rapide
  - Temps : minutes

Mid-Fidelity (Figma basique):
  - Layout précis, gris + une couleur
  - Liens simples entre écrans
  - Idéal pour : validation de flux
  - Temps : heures

High-Fidelity (Figma + animations):
  - Design final, couleurs, typo
  - Animations, transitions, micro-interactions
  - Idéal pour : tests utilisateurs, présentation client
  - Temps : jours

Code Prototype (React, Framer, Protopie):
  - Fonctionnel, données réelles
  - Interactions complexes, API
  - Idéal pour : validation technique, design critique
  - Temps : semaines
```

## Outils de Prototypage

### Comparatif
| Outil | Type | Fidelity | Interactivité | Collaboration | Pricing |
|-------|------|----------|---------------|---------------|---------|
| **Figma** | Design → Proto | Hi-Fi | Élevée | Excellente | Gratuit+ |
| **Protopie** | Proto pur | Hi-Fi | Très élevée | Bonne | Payant |
| **Framer** | Design → Code | Hi-Fi | Élevée | Moyenne | Payant |
| **Principle** | Motion | Hi-Fi | Très élevée | Faible | Payant |
| **Axure** | UX complexe | Mid-Hi | Extrême | Moyenne | Payant |
| **Penpot** | Open source | Mid-Hi | Moyenne | Bonne | Gratuit |
| **Webflow** | No-code | Hi-Fi | Élevée | Moyenne | Payant |
| **Balsamiq** | Wireframes | Low | Faible | Moyenne | Payant |

### Choix selon le besoin
```yaml
Flow validation:        Figma (liens entre frames)
Motion design:          Principle, Protopie, After Effects
Micro-interactions:     Protopie, Framer
Design critique:        Framer (React), Webflow
Test utilisateur:       Figma (prototype + mirror)
Documentation:          Axure (logique conditionnelle)
Open source:            Penpot, Quant UX
```

## Interactions & Transitions

### Types d'interactions Figma

| Déclencheur | Usage |
|-------------|-------|
| **On Click** | Bouton, lien, action |
| **On Drag** | Swipe, slider, pull-to-refresh |
| **While Hovering** | Tooltip, preview, état hover |
| **While Pressing** | Bouton enfoncé, accordéon |
| **Key/Gamepad** | Raccourcis clavier |
| **After Delay** | Auto-advance, carousel |
| **Mouse Enter/Leave** | Dropdown, menu flyout |
| **Scroll** | Parallax, infinite scroll |

### Écran de transition
```yaml
Smart Animate:
  - Anime automatiquement les propriétés communes
  - Nécessite des noms de calques identiques
  - Compatible: position, taille, rotation, opacité, fill

Dissolve:       Fade in/out (modale, toast)
Move In/Out:    Glissement (navigation, slide panel)
Push:           Pousser l'écran actuel (navigation native)
Slide:          Glissement par dessus (menu latéral)
Scale:          Zoom (gallery, lightbox)
Cube:           Rotation 3D (carousel)
Overlay:        Superposition (modale, tooltip)
```

### Timing & Easing
```css
/* Durées standard UI */
--duration-instant: 50ms;
--duration-fast: 150ms;      /* Hover, focus */
--duration-normal: 250ms;    /* Transitions standard */
--duration-slow: 400ms;      /* Modale, panel */
--duration-very-slow: 600ms; /* Page transition */

/* Easing functions */
--ease-out: cubic-bezier(0.16, 1, 0.3, 1);       /* Entrée naturelle */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);    /* Symétrique */
--ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1); /* Rebond subtil */
--ease-smooth: cubic-bezier(0.4, 0, 0.2, 1);      /* Material Design */
```

## Micro-Interactions

Les micro-interactions sont des animations de **feedback** qui durent 50-300ms. Elles transforment une interface fonctionnelle en expérience plaisante.

### Patterns de micro-interactions

```yaml
1. Feedback visuel:
   - Bouton : scale(0.95) au press, retour à 1.0 au release
   - Toggle : translation + couleur (150ms)
   - Checkbox : checkmark draw animation (200ms)
   - Like : icône pulse + remplissage (300ms)

2. Feedback d'état:
   - Loading : spinner, skeleton, progress bar
   - Success : checkmark + green flash
   - Error : shake input + red border
   - Empty : illustration + message

3. Feedback contextuel:
   - Tooltip : fade + slide (200ms)
   - Dropdown : scale + opacity (200ms)
   - Toast : slide from top + fade out (3s + 300ms)
   - Badge : pulse notification (1s loop)

4. Feedback haptique (mobile):
   - Long press : vibration légère
   - Error : vibration courte
   - Success : vibration douce
```

### Code CSS pour micro-interactions
```css
/* Bouton — feedback press */
.button {
  transition: transform var(--duration-fast) var(--ease-out),
              background-color var(--duration-fast) var(--ease-out);
}
.button:active {
  transform: scale(0.96);
}

/* Toggle switch */
.toggle {
  transition: background-color var(--duration-normal) var(--ease-out);
}
.toggle-thumb {
  transition: transform var(--duration-normal) var(--ease-spring);
}
.toggle[data-active="true"] .toggle-thumb {
  transform: translateX(20px);
}

/* Like button animation */
@keyframes like-pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}
.like-active {
  animation: like-pulse 300ms var(--ease-out);
}
```

## Prototypage Avancé

### Gestes mobiles
```yaml
Tap:                Clic standard
Double Tap:         Zoom, like
Long Press:         Menu contextuel, drag mode
Swipe Left/Right:   Navigation, suppression
Pinch:              Zoom in/out
Pull to Refresh:    Rechargement
Pan:                Scroll horizontal
Rotate:             Rotation d'image, map
Force Touch:        3D touch (iOS) — preview
```

### Logique conditionnelle (Protopie, Axure)
```yaml
If:
  - Champ vide → show error
  - Mot de passe < 8 char → show hint
  - Utilisateur connecté → dashboard
  - Sinon → login

Switch:
  - Tab 1 → panel A
  - Tab 2 → panel B
  - Tab 3 → panel C

Variables:
  - $count = 0 → +1 à chaque clic
  - $isLoggedIn = false → true après login
  - $currentStep = 1 → 2 → 3 (wizard)
```

### Prototypage vocal
```yaml
Voice input:
  - Microphone → transcription
  - Commande vocale → action
  - Feedback: "J'ai compris X"

Voice output:
  - TTS confirmation
  - Audio feedback (son de succès)
  - Instructions vocales
```

## Design Critique (Speculative Design)

Le prototypage permet aussi d'explorer des **futurs possibles**, des **états d'erreur extrêmes** et des **edge cases** rarement considérés.

### Scénarios à prototyper
```yaml
Happy path:          Succès, utilisateur expert
Sad path:           Erreur, annulation, timeout
Edge case:           Données vides, 1000+ items, caractères spéciaux
Security:           Session expirée, accès refusé, phishing
Privacy:            Consentement, GDPR, data deletion
Accessibility:      Zoom 200%, mode contraste élevé, lecteur d'écran
Performance:        Latence réseau, offline, battery saver
International:      RTL, textes longs, formats de date régionaux
```

### Erreur célèbre : le "Fail Nul"
Prototyper **toujours** l'état vide :
```yaml
❌ Écran vide (aucune info) → l'utilisateur pense que ça a crashé
✅ Empty state avec illustration + message + CTA
```

## Tests Utilisateurs sur Prototype

### Protocole de test
```yaml
1. Recruter 5 participants (diversité)
2. Préparer 3-5 scénarios
3. "Pensez à voix haute"
4. Observer sans intervenir
5. Mesurer:
   - Task success rate
   - Time on task
   - Error rate
   - Satisfaction (SUS, NPS)
6. Synthétiser: patterns, quotes, recommandations
```

### Outils de test
```yaml
Figma Mirror:       Test mobile en temps réel
Lookback:           Enregistrement + annotations
UserTesting:        Panel de testeurs
Maze:               Analytics de prototype
Hotjar:             Heatmaps + recordings
UsabilityHub:       Tests rapides (5 second test, preference test)
```

### Questions à poser
```yaml
- "Quelle est la première chose que vous voyez ?"
- "Que pensez-vous pouvoir faire ici ?"
- "Comment feriez-vous pour X ?"
- "Qu'attendriez-vous en cliquant sur Y ?"
- "Sur une échelle de 1-5, à quel point c'était facile ?"
- "Qu'est-ce qui vous a frustré ?"
- "Qu'aimeriez-vous changer ?"
```

## Pièges
- ⚠️ Trop de fidelity trop tôt → feedback focus sur le visuel, pas le concept
- ⚠️ Animations trop longues (>400ms) → sensation de lenteur
- ⚠️ Oublier l'état de chargement → l'utilisateur ne sait pas si ça marche
- ⚠️ Tester uniquement le happy path → les vrais problèmes sont dans les edge cases
- ⚠️ Pas de responsive dans le prototype → décisions desktop-only
- ⚠️ Micro-interactions sans `prefers-reduced-motion` → nausée, inconfort
- ⚠️ Prototype ≠ produit final → attention aux promesses excessives (Napoleon Dynamite)
- ⚠️ Pas de logique conditionnelle → flow linéaire irréaliste
- ⚠️ Oublier l'état vide → "fail nul" → l'utilisateur pense à une erreur