---
name: blender-sculpting
description: "Sculpture numérique dans Blender — Dyntopo, Multiresolution, brosses, masks, remesh, anatomie, détails de surface, de block-in au high-poly final."
version: 1.0.0
category: creative
tags:
  - blender
  - sculpting
  - sculpture
  - 3d
  - digital-sculpting
  - dyntopo
  - multires
  - organic-modeling
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender doit être installé. Fonctionne mieux avec une tablette graphique (pression supportée)."
metadata:
  hermes:
    tags:
      - blender
      - sculpting
      - sculpture
      - 3d
      - digital-sculpting
      - dyntopo
      - multires
      - organic-modeling
    related_skills:
      - blender-modeling
      - blender-texturing
      - blender-rigging
    category: creative
---

# Blender — Sculpture Numérique

Guide complet de sculpture 3D dans Blender. Du block-in grossier au
high-poly détaillé, avec gestion DynTopo et Multiresolution.

## Modes de Sculpture

### DynTopo (Dynamic Topology)

Le maillage s'adapte dynamiquement (subdivision/décimation locale).

- **Activation** — `Dyntopo` dans le header du viewport
- **Detail Size** — taille des détails en pixels d'écran
- **Detail Method:**
  - `Relative Detail` — basé sur l'écran (jeu par défaut)
  - `Constant Detail` — taille absolue en mm
  - `Brush Detail` — adapté à la taille du pinceau
- **Optimise** — `Refine Method: Subdivide Collapse` (meilleur rendu)
- **Détopologiser** — `Remesh` après DynTopo pour clean quad-flow

### Multiresolution

Subdivisions non-destructives, idéal pour normal map baking.

- **Ajouter** — `Multiresolution` modifier
- **Subdivisions** — `Ctrl+1..5`
- **Bake normals** — du haut niveau vers le bas niveau
- **Reshape** — après subdivision, sculpte sur niveau 1-2
- **Limitation** — pas d'undo sur les niveaux, sauvegarder avant

## Brosses Essentielles

| Brosse | Raccourci | Usage |
|--------|-----------|-------|
| **Draw** | `S` | Formes générales |
| **Clay Strips** | `C` | Ajout de matière plate |
| **Clay Thumb** | — | Pousser/tasser la matière |
| **Crease** | `Shift+C` | Creuser des lignes |
| **Inflate/Deflate** | `I` | Gonfler/dégonfler |
| **Grab** | `G` | Déplacer la géométrie |
| **Snake Hook** | — | Tirer des formes |
| **Flatten/Contrast** | `Shift+T` | Aplatir |
| **Pinch/Magnify** | `P` | Pincer/étirer |
| **Smooth** | `Shift+S` | Lisser |
| **Scrape/Peaks** | — | Racler les hauts |
| **Fill/Deepen** | — | Remplir/creuser |
| **Mask Brush** | `M` | Peindre un masque |
| **Box Mask** | `B` | Masquer zone rectangulaire |
| **Lasso Mask** | `Shift+LMB` | Masquer lasso |
| **Move** | — | Déplacer sous le pinceau |
| **Rotate** | — | Tordre |
| **Simplify** | — | Réduire le détail |

## Raccourcis Clés

| Touche | Action |
|--------|--------|
| `F` | Taille du pinceau |
| `Shift+F` | Force du pinceau |
| `F` puis bouger souris | Ajuster taille |
| `Ctrl+Click` | Inverser la brosse (Soustraction) |
| `Shift+Click` | Smooth |
| `Ctrl+Shift+Click` | Inverser la direction du smooth |
| `R` | Rotation texture du pinceau |
| `M` | Masquer |
| `Alt+M` | Dé-masquer tout |
| `Control+I` | Inverser le masque |
| `H` | Cacher la sélection |
| `Alt+H` | Afficher tout |
| `Shift+R` | Remesh |
| `Shift+D` | Détails du pinceau |
| `O` | Pression dynamo (toggle) |
| `W` | Viewport shading menu |
| `Shift+Space` | Maximise la zone de vue |

## Workflow Organique

### Phase 1: Block-in (DynTopo, faible résolution)

1. **Sphere/cube** de base
2. **Remesh** → Résolution très basse (blocs)
3. **Grab** + **Snake Hook** → Silhouette générale
4. **Clay Strips** → Masses principales
5. **Symmétrie** — `X/Y/Z` activée

### Phase 2: Formes secondaires (DynTopo, résolution moyenne)

1. **Clay Strips / Draw** → Formes musculaires
2. **Crease** → Plis, sillons
3. **Smooth** → Transition entre volumes
4. **Mask** + **Grab** = repositionner localement

### Phase 3: Détails (Multires ou DynTopo haute)

1. **Remplacer DynTopo par Multires** si baking prévu
2. **Crease** + **Pinch** → Pores, rides
3. **Alphas** (brosses texture) → Peau, écailles
4. **Filter by Topology** — sélectionner zones par angle

### Phase 4: Finalisation

1. **Remesh** (quadriflow) pour retopo rapide
2. **Decimate** si low-poly nécessaire
3. **Bake normals** + **Bake displacement**
4. **Export** vers le shading/texturing

## Masques et Transforms

- **Masquer** — protège la zone du pinceau
- **Inverser masque** — `Ctrl+I`
- **Masque doux** — plus la brosse est faible, plus le masque est progressif
- **Grab avec masque** — déforme la zone visible seulement
- **Mesh Filter** → `Mask` pour effacer un masque globalement
- **Transform** (masque actif) — bouger/scale/rotate la zone non masquée

## Remesh (QuadriFlow / Voxel)

| Méthode | Usage | 
|---------|-------|
| **Voxel Remesh** | Bloc grossier, symétrie rapide |
| **QuadriFlow** | Clean quad flow pour retopo |
| **Remesh modifier** | Non-destructif (procédural) |
| **Decimate** | Réduction polygonale propre |

## Brush Textures / Alphas

- **Texture Panel** dans le header sculpt
- **Alpha personnalisées** — images PNG en niveaux de gris
- **Drag Dot** — placer l'alpha exactement
- **rake** — pour poils/fourrure
- **Paquets gratuits** : Quixel Megascans, Texturing.xyz

## Pitfalls

1. **Dyntopo + Multires incompatibles** — un seul à la fois
2. **Multires + Mirror Modifier** peut poser problème — utiliser le Symmetry intégré
3. **Polycount explose vite** — sauvegarder un niveau bas avant Dyntopo détaillé
4. **Tablette requise** pour pression réaliste (sans souris OK mais limité)
5. **Sauvegarde fréquente** — sculpting est lourd, Blender peut crasher
6. **Scale non appliquée** casse le Multires modifier
7. **Angles morts** — tourner souvent l'objet, l'œil s'habitue
8. **Optimiser les masques** avec `Mesh Filter > Sharpen/Soften`

## Voir Aussi

- `blender-modeling` — Retopologie après sculpt
- `blender-shading` — Matériaux PBR sur sculpt
- `blender-texturing` — Peinture de texture sur high-poly