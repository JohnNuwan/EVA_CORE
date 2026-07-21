---
title: Figma — Design & collaboration
description: Figma — conception UI/UX, auto-layout, composants, variables, plugins, API REST, prototypage, collaboration temps réel, design tokens
category: creative
author: E.V.A
tags: [figma, ui-design, auto-layout, composants, design-tokens, plugins, figma-api, variables]
version: 1.0
---

# Figma — Design & Collaboration

## Concepts Fondamentaux

Figma est un outil de design vectoriel collaboratif fonctionnant dans le navigateur. Architecture basée sur **frames** (équivalent artboards), **composants** (instances réutilisables), **variables** (design tokens natifs), **auto-layout** (contraintes responsive).

### Structure d'un fichier Figma
```
Fichier (.fig)
├── Pages
│   ├── Couverture
│   ├── Design System
│   ├── Écrans (dashboard, profil, settings…)
│   └── Prototype & Flow
└── Assets (Composants, Styles, Variables)
```

## Auto-Layout (Mise en page automatique)

Auto-layout = Flexbox dans Figma. Tout design responsive s'appuie dessus.

```css
/* Équivalent CSS de l'auto-layout */
.auto-layout-horizontal {
  display: flex;
  flex-direction: row;
  gap: 8px;           /* Space between */
  padding: 16px;       /* Padding */
  align-items: center; /* Vertical align */
  justify-content: flex-start; /* Horizontal align */
}

.auto-layout-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
```

### Raccourcis Auto-Layout
| Action | Raccourci |
|--------|-----------|
| Appliquer auto-layout | Shift + A |
| Enlever auto-layout | Shift + Alt + A |
| Ajouter frame | Ctrl + Alt + G |
| Renommer calque | Ctrl + R |
| Toggle constraints | Aucun — utiliser le panneau design |

### Propriétés clés
- **Direction** : Row (horizontal) ou Column (vertical)
- **Padding** : Top, Right, Bottom, Left (individuels ou uniforme)
- **Gap** : Espacement entre les enfants
- **Alignment** : Min, Center, Max, Space Between
- **Sizing** : Hug (fit content), Fill (stretch), Fixed (pixel exact)

## Composants & Instances

### Création
1. Sélectionner un élément → Ctrl + Alt + K (Create Component)
2. Le composant apparaît dans le panneau Assets
3. Glisser-déposer pour créer des instances

### Propriétés de composant
```yaml
Composant: Button
  Variants:
    - size: sm | md | lg
    - variant: primary | secondary | ghost
    - state: default | hover | active | disabled
  Properties:
    - label: text (string)
    - icon: boolean (show/hide)
    - loading: boolean (spinner swap)
```

### Best Practices
- **Atomic Design** : Atomes → Molécules → Organismes → Templates → Pages
- **Variants** : Regrouper les états dans un seul composant
- **Component Properties** : Exposer les textes, icônes, états
- **Nesting** : Éviter plus de 3 niveaux de profondeur
- **Detach instance** : Dernier recours — casser le lien perd la synchro

## Variables (Design Tokens natifs)

Figma Variables (2023+) remplacent les styles pour les tokens.

### Types de variables
- **Color** : Couleurs (hex, rgba, hsl)
- **Number** : Espacements, rayons, opacités
- **String** : Labels, URLs
- **Boolean** : Toggles (show/hide)

### Modes (Themes)
```yaml
Collection: Theme
  Mode: Light
    color-bg-primary: #FFFFFF
    color-text-primary: #1A1A1A
    spacing-md: 16
  Mode: Dark
    color-bg-primary: #1A1A1A
    color-text-primary: #FFFFFF
    spacing-md: 16  # inchangé
```

### Liaison automatique
Les variables se lient automatiquement aux propriétés :
- Fill → `{color-bg-primary}`
- Stroke → `{color-border}`
- Gap → `{spacing-md}`
- Radius → `{radius-sm}`

### Alias (Variable Aliasing)
```yaml
color-primary: #0066FF
color-button-bg: {color-primary}  # alias
color-button-hover: {color-primary-600}  # alias vers un dérivé
```

## Styles (Légacy, mais toujours utilisés)

### Types de styles
- **Fill** : Couleurs de fond
- **Stroke** : Couleurs de contour
- **Text** : Polices, tailles, espacements
- **Effect** : Ombres, flous

### Bonnes pratiques
- Nommer avec préfixe : `Color/Primary`, `Text/H1`, `Shadow/Sm`
- Utiliser les styles pour les cas simples, les variables pour les tokens complexes
- Ne pas mélanger styles et variables sur la même propriété

## Plugins essentiels

### Design & Prototypage
| Plugin | Usage |
|--------|-------|
| **Content Reel** | Générer du faux contenu textuel |
| **Unsplash** | Photos libres de droit |
| **Iconify** | 200k+ icônes SVG |
| **Map Maker** | Cartes interactives |
| **Blob Maker** | Formes organiques |

### Design Tokens
| Plugin | Usage |
|--------|-------|
| **Design Tokens** | Export/import tokens JSON |
| **Themer** | Gestion multi-thème |
| **Contrast** | Vérification WCAG |
| **A11y** | Analyse d'accessibilité |

### Développement
| Plugin | Usage |
|--------|-------|
| **Anima** | Export HTML/CSS/React |
| **Tailwind CSS** | Génération Tailwind config |
| **SVG Import** | Import/optimisation SVG |
| **Figma to Code** | Export code React/Vue/Swift |

## API REST Figma

### Endpoints clés
```bash
# Récupérer un fichier
GET https://api.figma.com/v1/files/{file_key}

# Récupérer les images d'un nœud
GET https://api.figma.com/v1/images/{file_key}?ids={node_id}

# Récupérer les styles
GET https://api.figma.com/v1/files/{file_key}/styles

# Récupérer les composants
GET https://api.figma.com/v1/files/{file_key}/components
```

### Headers
```bash
Authorization: Bearer {figma_personal_token}
X-Figma-Token: {figma_personal_token}
```

### Webhooks
```bash
POST https://api.figma.com/v2/webhooks
{
  "event_type": "FILE_UPDATE",
  "file_key": "...",
  "endpoint": "https://mon-app.com/figma-webhook",
  "passcode": "secret123"
}
```

## Collaboratif

### Fonctionnalités temps réel
- **Multi-éditeurs** : Jusqu'à 500 personnes sur un même fichier
- **Commentaires** : @mentions, résolution, threads
- **Branching** : Versions parallèles (Figma Professional)
- **Version History** : 30 jours (gratuit), illimité (pro)

### Dev Mode
- **Inspect** : CSS, iOS, Android, SwiftUI, Compose
- **Export** : Assets @1x, @2x, @3x
- **Code snippets** : Génération automatique
- **Link** : URL direct vers un frame

## Prototypage dans Figma

### Interactions
- **Navigate** : Vers une autre frame
- **Overlay** : Modale, tooltip, dropdown
- **Swap** : Changer l'état d'un composant
- **Back** : Retour à la frame précédente
- **Open URL** : Lien externe

### Déclencheurs
| Trigger | Description |
|---------|-------------|
| On Click | Clic simple |
| On Drag | Glisser-déposer |
| While Hovering | Survol (desktop) |
| While Pressing | Maintenir enfoncé |
| Key/Gamepad | Touche clavier |
| After Delay | Minuterie |
| Mouse Enter/Leave | Entrée/sortie de zone |
| Scroll | Défilement |

### Animations
```yaml
Smart Animate: true  # Animation fluide entre états
Easing:
  - Ease In
  - Ease Out
  - Ease In Out
  - Custom Cubic Bezier
Duration: 200-400ms  # standard UI
```

## Raccourcis clavier essentiels

### Navigation
| Raccourci | Action |
|-----------|--------|
| Space + Drag | Panoramique |
| Ctrl + 0 | Zoom 100% |
| Ctrl + 1 | Zoom to fit |
| Ctrl + 2 | Zoom to selection |
| 1-9 | Zoom levels |

### Édition
| Raccourci | Action |
|-----------|--------|
| V | Move tool |
| F | Frame tool |
| R | Rectangle |
| O | Ellipse |
| T | Text |
| P | Pen |
| Shift + 1 | Boolean Union |
| Shift + 2 | Boolean Subtract |
| Shift + 3 | Boolean Intersect |
| Shift + 4 | Boolean Exclude |

### Organisation
| Raccourci | Action |
|-----------|--------|
| Ctrl + G | Group |
| Ctrl + Shift + G | Ungroup |
| Ctrl + ] | Forward |
| Ctrl + [ | Backward |
| Ctrl + Shift + ] | To front |
| Ctrl + Shift + [ | To back |
| Ctrl + D | Duplicate |
| Ctrl + L | Lock |
| / | Search layers |

## Export

### Formats
| Format | Usage |
|--------|-------|
| PNG | Rasters, screenshots |
| JPG | Photos, backgrounds |
| SVG | Icônes, illustrations |
| PDF | Présentations, specs |
| GIF | Animations courtes |

### Export settings
```yaml
Suffix: @2x  # Pour retina
Scale: 2x    # Multiplicateur
Background: transparent  # ou couleur
Constrain: bounds  # Crop automatique
```

## Pièges
- ⚠️ Auto-layout imbriqué sans gap → espacement incohérent
- ⚠️ Trop de variants → complexité, perfs dégradées
- ⚠️ Variables non documentées → perte de contexte en équipe
- ⚠️ Frames sans nom → désorganisation du panneau layers
- ⚠️ Textes sans style → impossible à mettre à jour globalement
- ⚠️ Plugins non vérifiés → peuvent altérer le fichier
- ⚠️ Export sans suffixe @2x → assets flous sur retina