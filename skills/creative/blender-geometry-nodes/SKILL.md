---
name: blender-geometry-nodes
description: "Geometry Nodes dans Blender — modélisation procédurale, systèmes génératifs, fields, attributes, instancing, simulations, scattering, destruction, animation par nœuds."
version: 1.0.0
category: creative
tags:
  - blender
  - geometry-nodes
  - procedural-modeling
  - nodes
  - generative
  - fields
  - mesh-operations
  - 3d
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender 3.0+ (Geometry Nodes). Blender 4.x+ pour la simulation. Blender installé sur le PATH."
metadata:
  hermes:
    tags:
      - blender
      - geometry-nodes
      - procedural-modeling
      - nodes
      - generative
      - fields
      - mesh-operations
    related_skills:
      - blender-modeling
      - blender-animation
      - blender-shading
    category: creative
---

# Blender — Geometry Nodes

Guide complet pour la modélisation procédurale avec Geometry Nodes dans
Blender. Fields, grids, scattering, destruction procédurale, simulations,
et animation.

## Concepts Fondamentaux

### Geometry Node Modifier

- Ajouté comme n'importe quel modificateur
- Reçoit la géométrie d'entrée et produit une sortie
- Évalué de haut en bas
- Support des Groupes (Group = nouveau node)

### Fields (Champs)

Données qui varient sur la géométrie (attributs).

| Field | Description |
|-------|-------------|
| **Position** | Position XYZ de chaque point |
| **Normal** | Normale de chaque face/vertex |
| **Index** | Index de l'élément (0, 1, 2...) |
| **ID** | ID unique (peut être ré-assigné) |
| **Radius** | Rayon (courbes, points) |
| **Density** | Densité pour le scattering |

### Attributes

Attributs stockés sur la géométrie :

- **Capture Attribute** — échantillonner un champ
- **Store Named Attribute** — écrire un attribut
- **Attribute Statistic** — min/max/moyenne d'un attribut
- **Domain Size** — compter le nombre d'éléments

## Noeuds Essentiels

### Générateurs

| Noeud | Usage |
|-------|-------|
| **Grid** | Grille de faces |
| **Mesh Circle** | Cercle maille |
| **Mesh Line** | Ligne de vertex |
| **Mesh Grid** | Grille de quads |
| **UV Sphere** | Sphère UV |
| **Cone** | Cône |
| **Cylinder** | Cylindre |
| **Cube** | Cube |
| **Ico Sphere** | Sphère icosaèdre |
| **Curve Circle** | Cercle courbe |
| **Curve Line** | Ligne courbe |
| **Curve Grid** | Grille de courbes |
| **Points** | Points (pour instances) |
| **Distribute Points on Faces** | Points sur surface |
| **Noise Texture** | Bruit pour déplacement |

### Opérations

| Noeud | Usage |
|-------|-------|
| **Transform** | Location/Rotation/Scale |
| **Translate Instances** | Déplacer des instances |
| **Rotate Instances** | Rotation d'instances |
| **Scale Instances** | Échelle d'instances |
| **Set Position** | Déplacer des points |
| **Set Material** | Assigner matériau |
| **Set Shade Smooth** | Shading smooth/flat |
| **Set ID** | Assigner ID |
| **Set Curve Radius** | Rayon de courbe |
| **Set Point Radius** | Rayon de point |

### Sélection

| Noeud | Usage |
|-------|-------|
| **Selection** | Booléen par attribut |
| **Compare** | Comparer valeurs |
| **Evaluate at Index** | Valeur à un index |
| **Evaluate on Domain** | Changer de domaine |
| **Switch** | Switch booléen/nombre |
| **Endpoint Selection** | Sélection des bouts |
| **Random Value** | Valeur aléatoire |

### Mesh Operations

| Noeud | Usage |
|-------|-------|
| **Subdivision Surface** | Subdiviser |
| **Subdivide Mesh** | Subdiviser linéaire |
| **Triangulate** | Trianguler les faces |
| **Dual Mesh** | Dual mesh (inversion) |
| **Split Edges** | Split edges |
| **Merge by Distance** | Fusionner vertices |
| **Flip Faces** | Inverser normales |
| **Extrude Mesh** | Extrusion |
| **Scale Elements** | Échelle locale |
| **Split to Instances** | Séparer par île |
| **Delete Geometry** | Supprimer sélection |
| **Separate Geometry** | Séparer en 2 flux |
| **Geometry Proximity** | Distance à un autre mesh |

### Instancing

| Noeud | Usage |
|-------|-------|
| **Instance on Points** | Instancier sur des points |
| **Object Info** | Référencer un objet |
| **Collection Info** | Référencer une collection |
| **Realize Instances** | Convertir instances en mesh |
| **Instance Index** | Index de l'instance |
| **Pick Instance** | Sélectionner une instance |

### Utilities

| Noeud | Usage |
|-------|-------|
| **Math** | Opérations mathématiques |
| **Boolean Math** | AND, OR, NOT, NAND |
| **Map Range** | Remapper valeurs |
| **Float Curve** | Courbe de mapping |
| **Color Ramp** | Gradient de couleurs |
| **Mix** | Mixer valeurs/colors/vectors |
| **Accumulate Field** | Somme cumulative |
| **Sample Index** | Échantillonner par index |
| **Sample Nearest** | Échantillonner plus proche |
| **Viewer** | Déboguer les geometry nodes |

## Workflows Essentiels

### Scattering (Distribution)

```
Grid → Distribute Points on Faces (Poisson Disk)
    ↓
Instance on Points → Object (rocher/arbre)
    ↓
Random Value → Rotation/Scale (aléatoire)
```

### Destruction Procédurale

```
Object → Noise Texture (déplacement)
    ↓
Split to Instances (par île)
    ↓
Set Position (aléatoire)
    ↓
Rigid Body (simulation)
```

### Terrain Génératif

```
Grid → Noise Texture → Set Position (Y displacement)
    ↓
Subdivision Surface (smooth)
    ↓
Color Ramp → Set Material
```

### Végétation

```
Curve Line → Resample Curve
    ↓
Set Curve Radius (tapering)
    ↓
Instance on Points → Branches
    ↓
Repeat Zone (Blender 4.x) → Récursion
```

### Building Generator

```
Mesh Grid → Extrude (Random per face)
    ↓
Split to Instances → Scale Y (étages)
    ↓
Instance → Windows (points sur faces)
```

## Simulations (Blender 4.x+)

Geometry Nodes Simulation Zone :

```
Input Geometry → Simulation Zone
                    ↓
        [Cache: Start / Frame]
                    ↓
        [Move, Noise, Rotate]
                    ↓
Output Geometry
```

### Exemple Simulation Particules

```
[Points] → Simulation Zone
    ↓
Set Position (Noise Texture + Time)
    ↓
Accumulate Field (vitesse)
    ↓
Delete Geometry (hors limite)
```

## Groupes et Réutilisabilité

1. Sélectionner les noeuds → `Ctrl+G`
2. Modifier le nom du groupe
3. Exposer les paramètres (Group Input interface)
4. **Asset Browser** — sauvegarder dans `.blend` library
5. **Modifier** — exporter en `.py` avec des valeurs par défaut

## Modificateur vs Geometry Nodes

| Cas | Modificateur Classique | Geometry Nodes |
|-----|----------------------|----------------|
| **Subdivision** | Subsurf modifier | Subdivision Surface node |
| **Mirror symétrie** | Mirror modifier | Mirror (via Transform) |
| **Array** | Array modifier | Instance on Points |
| **Bevel** | Bevel modifier | Bevel (Mesh > Bevel) |
| **Boolean** | Boolean modifier | Mesh Boolean |
| **Displace** | Displace modifier | Noise + Set Position |

## Debugging

- **Viewer Node** — connecte à un geometry viewer dans le Spreadsheet
- **Spreadsheet** — inspecter les attributs (Position, Normal, etc.)
- **Mute Node** — `M` pour désactiver un noeud
- **Frame** — `Ctrl+J` pour grouper visuellement
- **Reroute** — `Ctrl+Shift+R` pour repositionner les connexions

## Pitfalls

1. **Realize Instances oublié** — les instances ne sont pas des mesh editables sans realise
2. **Domain confusion** — champ sur faces vs vertices (résultats différents)
3. **Performance avec trop d'instances** — garder les instances (ne pas realize)
4. **Simulation Cache** — les simulations zones cachent les frames intermédiaires
5. **Noise texture en world space** — position relative de l'objet
6. **Attribute clash** — attributs nommés qui entrent en conflit
7. **Blender 3.x vs 4.x** — certains noeuds ont changé de nom ou d'API
8. **Mesh to Curve / Curve to Mesh** — perte de faces en conversion

## Voir Aussi

- `blender-modeling` — Modélisation classique combinée aux GN
- `blender-animation` — Animation des paramètres GN
- `blender-shading` — Shading procédural combiné aux attributs GN