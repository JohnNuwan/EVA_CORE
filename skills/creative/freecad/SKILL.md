---
name: freecad
title: "FreeCAD — CAO open source paramétrique et modulaire"
description: "Guide complet FreeCAD : ateliers Part/PartDesign/Sketcher, scripts Python, assemblage, FEM, export STEP/STL, feuilles de calcul, macros"
category: creative
tags: [freecad, cao, open-source, python, partdesign, fem, assembly]
created: 2026-07-22
---

# FreeCAD

## Vue d'ensemble

FreeCAD est un modeleur CAO paramétrique 3D libre et open source (LGPL), multiplateforme. Architecture modulaire basée sur des **ateliers (Workbenches)** : chaque atelier spécialisé (PartDesign, FEM, Draft, TechDraw, etc.).

## 1. Architecture et concepts

### Ateliers principaux

| Atelier | Usage | Rôle |
|---------|-------|------|
| **PartDesign** | Modélisation solide | Corps (Body), esquisses (Sketch), fonctions (Pad/Pocket) |
| **Part** | Géométrie primitive CSG | Booleans, extrusions basiques, primitives |
| **Sketcher** | Contraintes 2D | Esquisses avec contraintes géométriques + cotations |
| **Assembly** | Assemblages | Joints, contraintes d'assemblage, mouvement |
| **TechDraw** | Mise en plan | Vues 2D, cotations, annotations depuis le modèle 3D |
| **FEM** | Éléments finis | Maillage, contraintes, matériaux, solveurs CalculiX |
| **Draft** | DXF/2D | Dessin 2D, import/export DXF |
| **Spreadsheet** | Tableur | Paramètres pilotant le modèle (feuilles de calcul) |

### Corps (Body) et Part Design

- Chaque Body a une **origine** (axes X/Y/Z + plans de base)
- Fonctions : Pad, Pocket, Groove, Revolve, Loft, Sweep, Hole, Thread
- **Tip** = dernière fonction du Body (point de terminaison)

## 2. Workflow Sketcher → PartDesign

```
1. Nouveau document → PartDesign → Create Body
2. Select face/plane → Create Sketch
3. Dessiner profil (lignes, arcs, cercles)
4. Appliquer contraintes
5. Fermer sketch → Pad (extrusion) ou Pocket (enlèvement)
6. Ajouter features : Chamfer, Fillet, Hole, Thread
7. Patterns : LinearPattern, PolarPattern, Mirror
```

## 3. Scripting Python

```python
import FreeCAD as App
import Part

doc = App.newDocument("MonModele")
box = doc.addObject("Part::Box", "Boite")
box.Length = 100; box.Width = 50; box.Height = 30
doc.recompute()
```

## 4. Assemblage (Assembly4)

- Links : instances du même part sans duplication
- LCS (Local Coordinate Systems) : définir les repères de jointure
- Joints : Fixed, Revolute, Cylindrical, Planar, Ball, Distance

## 5. FEM

1. Analysis Container → Material → Fixed Constraint → Force Load → Mesh (GMSH) → Solver CalculiX → Results

## 6. Formats d'échange

STEP (préféré), IGES (legacy), STL (mesh), OBJ, DXF, IFC, FCStd (natif)

## Pitfalls

- **Topological Naming** : FreeCAD (pré-1.0) renomme les faces/arêtes après modification
- **Performance FEM** : maillage dense peut planter (limiter à 50k nœuds)
- **Assembly4** : stable mais pas de gestion des collisions/jeu

## Ressources

- [FreeCAD Documentation](https://wiki.freecad.org/)
- [FreeCAD Python API](https://freecad.github.io/SourceDoc/)