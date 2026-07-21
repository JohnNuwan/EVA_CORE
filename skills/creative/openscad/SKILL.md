---
name: openscad
title: "OpenSCAD — Modélisation 3D procédurale par script"
description: "Guide complet OpenSCAD : CSG (Constructive Solid Geometry), modules, boucles, transformations, extrusion, import/export STL/DXF, customizer, optimisation performance"
category: creative
tags: [openscad, csg, script, procedural, stl, cad]
created: 2026-07-22
---

# OpenSCAD

## Vue d'ensemble

OpenSCAD est un **compilateur 3D scripté** : on écrit du code décrivant la géométrie → OpenSCAD le compile en mesh. Idéal pour : pièces paramétriques, algorithmes géométriques, répétitions, CI/CD de fabrication.

## 1. Langage OpenSCAD

### Primitives
```openscad
$fn = 64;
cube([10, 20, 30]);
sphere(r = 10);
cylinder(h = 20, r1 = 5, r2 = 10);
polyhedron(points, faces);
```

### Opérations CSG
| Opération | Syntaxe |
|-----------|---------|
| Union | `union() { A; B; }` |
| Différence | `difference() { A; B; }` |
| Intersection | `intersection() { A; B; }` |
| Minkowski | `minkowski() { A; B; }` |
| Hull | `hull() { A; B; }` |

### Transformations
```openscad
translate([x, y, z])
rotate([rx, ry, rz])
scale([sx, sy, sz])
mirror([x, y, z])
resize([nx, ny, nz])
```

### Modules et boucles
```openscad
module ecrou(trou_diam, epaisseur, hauteur) {
    difference() {
        cylinder(h = hauteur, r = epaisseur/2 + 2);
        cylinder(h = hauteur, r = trou_diam/2);
    }
}

// Pattern circulaire
for (i = [0:60:359]) {
    rotate([0, 0, i])
        translate([50, 0, 0])
            cylinder(h = 5, r = 2);
}
```

## 2. Extrusion

```openscad
linear_extrude(height = 10) circle(r = 5);
linear_extrude(height = 20, twist = 180, slices = 50) square([10, 1]);
rotate_extrude(angle = 360) polygon(points = [[0,0], [10,0], [15,20]]);
```

## 3. Import

```openscad
import("fichier.stl");
import("fichier.3mf");
import("fichier.dxf");
surface("heightmap.png");
```

## 4. Customizer (UI automatique)

```openscad
//! Diamètre du trou (mm)
trou_diam = 5;  // [2:0.5:20]
materiau = "PLA";  // [PLA, PETG, ABS]
forme = "rond";  // [rond, carre, hexa]
```

## 5. CLI headless

```bash
openscad -o piece.stl -D "parametre=42" modele.scad
openscad -o apercu.png --imgsize=800,600 modele.scad
```

## 6. Bibliothèques

- **BOSL2** : formes standard, engrenages, vis
- **MCAD** : composants (roulements, NEMA)
- **Thread Library** : filetages métriques

## Pitfalls

- **$fn global** coûteux : préférer `$fa` + `$fs`
- **CGAL vs Manifold** : préférer Manifold (plus rapide)
- **Polyhedron** : faces en ordre anti-horaire (vue extérieure)
- **Précision** : virgule flottante double précision

## Ressources

- [OpenSCAD Manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- [BOSL2 Library](https://github.com/BelfrySCAD/BOSL2)