---
title: Wireframing — Conception & maquettage rapide
description: Wireframing — fidelity, grilles, layout patterns, responsive, information architecture, annotations, outils, bonnes pratiques
category: creative
author: E.V.A
tags: [wireframing, wireframe, maquettage, layout, grille, responsive, information-architecture, low-fidelity]
version: 1.0
---

# Wireframing — Conception & Maquettage Rapide

## Qu'est-ce qu'un Wireframe ?

Un wireframe est un schéma fonctionnel d'une interface, sans design visuel (couleurs, typographie, images). Il se concentre sur :
- **La structure** : disposition des éléments
- **La hiérarchie** : importance relative du contenu
- **La fonction** : comportement des interactions
- **Le flux** : navigation entre les écrans

### Niveaux de Fidelity

```yaml
Low-Fidelity (Papier, croquis):
  - Traits, boîtes, texte griffonné
  - Pas de couleurs, pas de styles
  - Idéal pour : brainstorming, itération rapide
  - Avantage : 5 minutes, tout le monde peut en faire
  - Inconvénient : ambiguïté, pas de testing distant

Mid-Fidelity (Figma, Balsamiq):
  - Gris, formes précises
  - Texte réel (lorem ipsum)
  - Annotations fonctionnelles
  - Idéal pour : validation de structure, documentation
  - Avantage : clair, rapide à modifier
  - Inconvénient : peut sembler "presque fini" aux stakeholders

High-Fidelity (Figma détaillé):
  - Presque le design final, sans couleurs
  - Vrai contenu, icônes, spacing précis
  - Idéal pour : specs développement, tests utilisateurs
  - Avantage : précis, complet
  - Inconvénient : plus long, peut bloquer l'itération
```

## Grilles & Layouts

### Systèmes de grille

```yaml
Grille 4 colonnes (mobile):
  - 4 colonnes, gutter 16px
  - Margin 16px
  - Idéal pour : mobile first

Grille 8 colonnes (tablette):
  - 8 colonnes, gutter 16px
  - Margin 24px
  - Idéal pour : iPad, responsive

Grille 12 colonnes (desktop):
  - 12 colonnes, gutter 24px
  - Margin auto (max-width 1200px)
  - Standard web
  - Idéal pour : la plupart des sites

Grille 16 colonnes (large desktop):
  - 16 colonnes, gutter 24px
  - Idéal pour : dashboards, data-heavy
```

### CSS Grid équivalent
```css
.container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

.col-4 {
  grid-column: span 4;
}

.col-6 {
  grid-column: span 6;
}

.col-8 {
  grid-column: span 8;
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 0 16px;
  }
  .col-4, .col-6, .col-8 {
    grid-column: span 4;
  }
}
```

### Spacing (8px grid)
```yaml
Échelle standard:
  xs:  4px  (1×)
  sm:  8px  (2×)
  md:  16px (4×)
  lg:  24px (6×)
  xl:  32px (8×)
  2xl: 48px (12×)
  3xl: 64px (16×)
  4xl: 96px (24×)

Margin section: 48-96px
Padding section: 64-128px
Gap entre éléments: 8-24px
```

## Layouts Standards

### Page type : Landing
```
┌─────────────────────────────────┐
│ Header (logo, nav, CTA)         │
├─────────────────────────────────┤
│ Hero (titre, sous-titre, CTA)   │
│   ┌─────────┐ ┌───────────────┐ │
│   │ Image    │ │ Texte         │ │
│   │          │ │               │ │
│   └─────────┘ └───────────────┘ │
├─────────────────────────────────┤
│ Features (3 colonnes)           │
│ ┌──────┐ ┌──────┐ ┌──────┐     │
│ │ Icon │ │ Icon │ │ Icon │     │
│ │ Text │ │ Text │ │ Text │     │
│ └──────┘ └──────┘ └──────┘     │
├─────────────────────────────────┤
│ Testimonials (carousel)         │
├─────────────────────────────────┤
│ CTA Section                     │
├─────────────────────────────────┤
│ Footer                          │
└─────────────────────────────────┘
```

### Page type : Dashboard
```
┌─────────────────────────────────────┐
│ Sidebar │ Header (search, profile)  │
│         ├───────────────────────────┤
│ Nav     │ Stats Cards               │
│         │ ┌──┐ ┌──┐ ┌──┐ ┌──┐     │
│         │ │$ │ │% │ │📊│ │👤│     │
│         │ └──┘ └──┘ └──┘ └──┘     │
│         ├───────────────────────────┤
│         │ Chart (line/bar)          │
│         │   ╱╲   ╱╲                │
│         │  ╱  ╲ ╱  ╲               │
│         ├───────────────────────────┤
│         │ Table (recent activity)   │
│         │ ┌──────────────────────┐  │
│         │ │ Row 1 │ Status │ ... │  │
│         │ │ Row 2 │ Done   │ ... │  │
│         │ └──────────────────────┘  │
└─────────────────────────────────────┘
```

### Page type : Form
```
┌─────────────────────────────────┐
│ Header (titre, steps)           │
├─────────────────────────────────┤
│ Form Section                    │
│ ┌─────────────────────────────┐ │
│ │ Label                       │ │
│ │ [Input field]               │ │
│ ├─────────────────────────────┤ │
│ │ Label                       │ │
│ │ [Input field]               │ │
│ ├─────────────────────────────┤ │
│ │ [ ] Checkbox                │ │
│ ├─────────────────────────────┤ │
│ │ [Dropdown select]           │ │
│ ├─────────────────────────────┤ │
│ │ [Button: Submit]            │ │
│ └─────────────────────────────┘ │
├─────────────────────────────────┤
│ Validation summary              │
└─────────────────────────────────┘
```

### Page type : Listing / Search Results
```
┌─────────────────────────────────┐
│ Header + Search bar + Filters   │
├─────────────────────────────────┤
│ Filters │ Results               │
│ ┌──────┐│ ┌──────────────────┐ │
│ │ Cat  ││ │ Card 1           │ │
│ │ ☐ A  ││ │ Title, desc, $   │ │
│ │ ☐ B  ││ ├──────────────────┤ │
│ │ ☐ C  ││ │ Card 2           │ │
│ │      ││ │ Title, desc, $   │ │
│ │ Price││ ├──────────────────┤ │
│ │ [--] ││ │ Card 3           │ │
│ └──────┘│ └──────────────────┘ │
│         │ Pagination           │
└─────────────────────────────────┘
```

## Information Architecture

### Structure de navigation
```yaml
Hiérarchique:
  Home → Category → Subcategory → Item
  ✅ Naturel, familier
  ❌ Peut enterrer le contenu

Matriciel:
  Navigation par attributs (filtres, tags)
  ✅ Flexible, puissant
  ❌ Peut submerger l'utilisateur

Séquentiel:
  Wizard, onboarding, checkout
  ✅ Guidé, pas de choix
  ❌ Pas de liberté

En hub:
  Dashboard → plusieurs modules
  ✅ Power users, complexe
  ❌ Courbe d'apprentissage
```

### Card Sorting pour IA
```yaml
Items à trier:
  - Toutes les pages/fonctionnalités
  - Sur des cartes physiques ou virtuelles

Résultat:
  - Catégories naturelles
  - Nommage utilisateur
  - Dendrogramme de similarité
  - Recommandation de navigation

Exemple output:
  Catégorie "Compte": Profil, Paramètres, Facturation, Sécurité
  Catégorie "Produits": Catalogue, Recherche, Favoris, Comparateur
  Catégorie "Support": FAQ, Chat, Tickets, Documentation
```

## Wireframing Patterns

### Patterns de liste
```yaml
Liste simple:
  ┌────────────────────────┐
  │ Icon │ Title        > │
  │      │ Description    │
  ├────────────────────────┤
  │ Icon │ Title        > │
  │      │ Description    │
  └────────────────────────┘

Liste avec actions:
  ┌────────────────────────┐
  │ ☐ │ Title    │ Edit ✕ │
  ├────────────────────────┤
  │ ☐ │ Title    │ Edit ✕ │
  └────────────────────────┘

Grid cards:
  ┌──────┐ ┌──────┐ ┌──────┐
  │ Img  │ │ Img  │ │ Img  │
  │ Title│ │ Title│ │ Title│
  │ Desc │ │ Desc │ │ Desc │
  └──────┘ └──────┘ └──────┘
```

### Patterns de navigation
```yaml
Top navigation:
  Logo | Link1 | Link2 | Link3 | CTA

Sidebar:
  ┌─────────┐ ┌─────────────────┐
  │ Logo    │ │ Content         │
  │ Nav 1   │ │                 │
  │ Nav 2   │ │                 │
  │ Nav 3   │ │                 │
  └─────────┘ └─────────────────┘

Tab bar (mobile):
  ┌────┬────┬────┬────┬────┐
  │ 🏠 │ 🔍 │ ➕ │ ❤️ │ 👤 │
  └────┴────┴────┴────┴────┘

Breadcrumb:
  Home > Category > Product
```

### Patterns de feedback
```yaml
Toast / Notification:
  ┌──────────────────────────┐
  │ ✅ Modification sauvegardée  ✕│
  └──────────────────────────┘

Empty state:
  ┌──────────────────────────┐
  │                          │
  │      📭 Illustration     │
  │   Aucun résultat trouvé  │
  │   [Action suggestion]    │
  │                          │
  └──────────────────────────┘

Error state:
  ┌──────────────────────────┐
  │ ⚠️ Impossible de charger│
  │   [Réessayer]            │
  └──────────────────────────┘
```

## Responsive Wireframing

### Breakpoints standards
```yaml
Mobile:    320px - 480px    (4 cols)
Mobile+:   481px - 768px    (4 cols)
Tablette:  769px - 1024px   (8 cols)
Desktop:   1025px - 1440px  (12 cols)
Large:     1441px+          (12-16 cols)
```

### Approche Mobile First
```yaml
1. Commencer par le wireframe mobile (4 cols)
   - Contenu minimal, prioritaire
   - Navigation simplifiée (hamburger)
   - Gestes tactiles

2. Progresser vers tablette (8 cols)
   - Sidebar possible
   - Plus de colonnes pour les listes
   - Navigation visible

3. Desktop (12 cols)
   - Layout complet
   - Navigation horizontale
   - Multi-panels
   - Raccourcis clavier
```

### Stacking & Transformation
```yaml
Mobile → Desktop:
  Navigation:  Hamburger → Top bar
  Sidebar:     Caché → Visible
  Grid:        1 col → 2-3 cols
  Cards:       Stack → Grid
  Table:       Scroll horizontal → Full width
  Form:        Single col → 2 cols
  Footer:      Stack → Multi-colonne
```

## Annotations & Documentation

### Annotations de wireframe
```yaml
Numérotation:
  [1] Identification unique
  → Description du comportement
  → Condition/état
  → Lien vers spec

Exemple:
  [1] Bouton "Valider"
  → État normal: bleu (#0066FF), texte blanc
  → Hover: bleu foncé
  → Disabled: gris clair
  → Click: soumet le formulaire
  → Erreur: message rouge sous le champ
  → Succès: redirection page confirmation

Flux:
  [1] → [2] → [3] (happy path)
  [1] → [4] (error path)
  [2] → [5] (cancel)
```

### Template de spec wireframe
```markdown
## Écran: Dashboard Principal

### Éléments
1. **Header** (fixed, 64px)
   - Logo gauche
   - Navigation: 4 liens
   - Avatar + notifications droite

2. **Stats Cards** (4 colonnes desktop, 2 tablette, 1 mobile)
   - Chaque carte: icône, valeur, label, trend
   - Clic → page détaillée

3. **Chart Section** (full width)
   - Line chart: 30 jours
   - Filtre: 7j, 30j, 90j
   - Tooltip au hover

### États
- **Loading**: Skeleton cards (3 pulses)
- **Empty**: "Pas de données" + CTA config
- **Error**: "Erreur de chargement" + Retry button

### Responsive
- Desktop: Layout 12 cols
- Tablet: 2 cols stats, chart stack
- Mobile: 1 col, chart hidden (CTA "Voir plus")
```

## Outils de Wireframing

| Outil | Fidelity | Prix | Points forts |
|-------|----------|------|-------------|
| **Figma** | Low → High | Gratuit+ | Le plus complet |
| **Balsamiq** | Low | Payant | Vraie vibe croquis |
| **Whimsical** | Mid | Freemium | Rapide, collaboratif |
| **Excalidraw** | Low | Gratuit | Open source, main levée |
| **Penpot** | Mid → High | Gratuit | Open source Figma-like |
| **Miro** | Low → Mid | Freemium | Tableau blanc |
| **Paper + crayon** | Low | Gratuit | Rien de plus rapide |

## Pièges
- ⚠️ Ajouter des couleurs trop tôt → focus sur le visuel, pas la structure
- ⚠️ Oublier les états d'erreur → wireframe du monde parfait uniquement
- ⚠️ Pas de responsive → décisions desktop-only
- ⚠️ Texte lorem ipsum → masque les vrais problèmes de contenu
- ⚠️ Annotations absentes → ambiguïté pour le développeur
- ⚠️ Trop de détails inutiles → ralentit l'itération
- ⚠️ Navigation non standard → l'utilisateur ne comprend pas
- ⚠️ Ignorer l'accessibilité → structure sans heading, sans landmarks
- ⚠️ Trop de clics pour une action simple → friction inutile
- ⚠️ Pas de test sur wireframe → on valide trop tard dans le process