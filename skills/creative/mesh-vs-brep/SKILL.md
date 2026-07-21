---
name: mesh-vs-brep
title: "Mesh vs BREP — Géométries polygonales et volumiques en CAO"
description: "Comparaison détaillée des représentations géométriques Mesh (maillage polygonal) et BREP (Boundary Representation), conversions, cas d'usage, outils et limites"
category: creative
tags: [mesh, brep, geometrie, conversion, stl, step, cad, visualisation]
created: 2026-07-22
---

# Mesh vs BREP

## 1. BREP (Boundary Representation)

BREP décrit un solide par ses **frontières** avec des **surfaces mathématiques exactes** (NURBS, B-splines, plans, cylindres, cônes, sphères, tores).

```
Solide BREP → Shell → Face (surface paramétrique) → Loop → Edge (courbe 3D) → Vertex
```

### Propriétés
- Précision exacte (mathématique)
- Paramétrique, modifiable
- Fichier léger (Ko)
- Calculs exacts (volume, centre de masse, intersection)

### Noyaux BREP
| Noyau | Produits |
|-------|----------|
| Parasolid | SolidWorks, NX |
| ACIS | Inventor |
| CGM | CATIA |
| OpenCascade | FreeCAD, pythonOCC |

## 2. Mesh (Maillage polygonal)

Mesh = surface approximative par polygones (triangles/quads).

```
Mesh → Vertices (x,y,z) + Faces (i0,i1,i2) + Normals
```

### Propriétés
- Précision approximative (dépend du nombre de polygones)
- Non-paramétrique (cire durcie)
- Fichier lourd (Mo-Go)
- GPU-friendly (rendu, jeux)

### Formats mesh : STL, OBJ, PLY, 3MF, GLTF/GLB, FBX

## 3. Comparaison

| Critère | BREP | Mesh |
|---------|------|------|
| Précision | Exacte (µm) | Approximative |
| Éditable | Oui (paramètres) | Non (sauf sculpt) |
| Poids | Léger | Lourd |
| Intersections | Exactes | Approximatives |
| Animation | Lourd | Léger |
| Rendu | Mesh converti | Direct GPU |
| Impression 3D | Converti en mesh | Direct |
| FEA/Simulation | Mesh requis | Direct |
| Scan 3D | Reconstruction req. | Naturel |

## 4. Conversion

### BREP → Mesh (tessellation)
```python
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.StlAPI import StlAPI_Writer
mesh = BRepMesh_IncrementalMesh(shape, 0.1)  # deflection mm
mesh.Perform()
StlAPI_Writer().Write(shape, "piece.stl")
```

### Mesh → BREP (reconstruction surfacique)
Difficile, souvent approximatif :
- **Automatique** : Fusion 360 Mesh→T-Spline→BREP, SolidWorks ScanTo3D
- **Semi-auto** : Geomagic Design X, Quicksurface, SpaceClaim
- **Manuel** : redessiner par-dessus le mesh

**Problèmes** : topologie propre = supposition sur l'intention, perte angles vifs, bruit de scan

## 5. Formats hybrides (BREP + Mesh)

| Format | Description |
|--------|-------------|
| JT (Siemens) | BREP exact + Mesh tessellated |
| 3D PDF | BREP + Mesh + métadonnées |
| STEP AP242 | STEP avec tessellation optionnelle |

## 6. Outils

| Besoin | Outil |
|--------|-------|
| Réparation mesh | Netfabb, Meshmixer, Blender |
| Réparation BREP | CADfix, SolidWorks Heal Geometry |
| Mesh→BREP | Geomagic, Quicksurface |
| BREP→mesh | Tout logiciel CAO |
| Remaillage | Instant Meshes, Meshlab, Blender |

## Pitfalls

- **STL 100 Mo ≠ pièce complexe** : peut venir d'une pièce STEP de 2 Ko
- **Trous dans le mesh** : non-watertight = impression impossible
- **Conversion BREP→Mesh** : trop peu de triangles = crénelage, trop = fichier monstrueux
- **Mesh→BREP auto** : échoue sur géométries organiques complexes
- **NURBS vs Poly** : une surface NURBS peut remplacer 10000 triangles

## Ressources

- [OpenCascade](https://dev.opencascade.org/doc/)
- [pythonOCC](https://github.com/tpaviot/pythonOCC)
- [CGAL](https://www.cgal.org/)
- [Instant Meshes](https://github.com/wjakob/instant-meshes)