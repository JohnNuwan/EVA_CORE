---
name: solidworks-concepts
title: "SolidWorks — Concepts avancés de CAO paramétrique"
description: "Guide des concepts clés SolidWorks : FeatureManager, esquisses 3D, assemblages (mates), configurations, equations, family tables, mise en plan, simulation, tolérancement"
category: creative
tags: [solidworks, dassault, cao, parametrique, assemblage, mise-en-plan, simulation]
created: 2026-07-22
---

# SolidWorks — Concepts

## Vue d'ensemble

SolidWorks (Dassault Systèmes) est le standard de l'industrie pour la CAO mécanique paramétrique. Dominant en mécanique générale, outillage, machines spéciales.

## 1. FeatureManager (arbre de création)

```
Document (SLDPRT/SLDASM)
├── Annotations, Material, Planes (Front, Top, Right)
├── Origin, Sketch1 → Boss-Extrude1 → Cut-Extrude1 → Fillet1
└── End
```

### Types de features : Boss-Extrude, Cut-Extrude, Revolved, Lofted, Swept, Dome, Wrap, Pattern (Linear/Circular), Mirror, Rib, Shell

## 2. Esquisses (Sketches)

- **Fully Defined** = noir ; **Under Defined** = bleu ; **Over Defined** = rouge
- Contraintes : Horizontal, Vertical, Collinear, Tangent, Concentric, Equal
- **Smart Dimension** : cote simple, angulaire, diamètre, rayon

## 3. Assemblages (Mates)

| Mate | DDL restants |
|------|-------------|
| Coincident | 0 DDL |
| Concentric | 4 DDL (rotation + translation) |
| Parallel | 2 DDL |
| Tangent | 1 DDL |
| Distance | 1 DDL |
| Angle | 1 DDL |

## 4. Configurations et Design Table

- Design Table : feuille Excel intégrée (Insert → Tables → Design Table)
- Lignes = configurations, Colonnes = côtes + propriétés
- `$PRP@Material`, `$STATE@Fillet1` (S=Suppressed, U=Unsuppressed)

## 5. Equations et Global Variables

```solidworks
"d1@Sketch1" = "d2@Sketch1" * 1.5
"d3@Extrude1" = if("d1@Sketch1" > 100, 10, 5)
```

## 6. Mise en plan (Drawing)

- Standard 3 View, Projected View, Section, Detail, Broken
- Model Items : importer les côtes du modèle
- DimXpert : GD&T automatique
- Tables : BOM, Hole table, Revision table
- Export : DWG, DXF, PDF, eDrawings

## 7. Simulation

| Étude | Usage |
|-------|-------|
| Static | Contrainte/déplacement |
| Frequency | Modes propres |
| Buckling | Flambement |
| Fatigue | Endurance (S-N curve) |
| Nonlinear | Grandes déformations |

## 8. Formats

SLDPRT (natif), SLDASM (assemblage), STEP, IGES, STL, Parasolid (.x_t), eDrawing

## Pitfalls

- **Large assemblies** : >1000 parts → Large Assembly Mode
- **Lightweight components** : charge mémoire partielle
- **Design Table sans Excel** : utiliser CSV-based ou API
- **Rebuild time** : éviter chaînes de dépendances profondes

## Ressources

- [SolidWorks Help](https://help.solidworks.com/)
- [SolidWorks API](https://help.solidworks.com/2023/english/api/sldworksapiprogguide/)