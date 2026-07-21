---
name: blender-modeling
description: "Modélisation 3D dans Blender — box modeling, poly modeling, retopologie, curves, modifiers, hard-surface et organic, optimisation de maillage pour jeux et production."
version: 1.0.0
category: creative
tags:
  - blender
  - modeling
  - modélisation
  - 3d
  - retopology
  - poly-modeling
  - hard-surface
  - organic-modeling
  - cg
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender doit être installé (blender sur le PATH). Pas de setup supplémentaire requis. Les scripts de référence utilisent blender --python-background et bpy."
metadata:
  hermes:
    tags:
      - blender
      - modeling
      - modélisation
      - 3d
      - retopology
      - poly-modeling
      - hard-surface
      - organic-modeling
    related_skills:
      - blender-sculpting
      - blender-shading
      - blender-geometry-nodes
    category: creative
---

# Blender — Modélisation 3D

Guide complet de modélisation 3D dans Blender. Couvre les workflows
essentiels du block-in à la livraison finale.

## Techniques de Modélisation

### Box Modeling (Débutant → Intermédiaire)

1. **Démarrer d'un primitif** — `Shift+A > Mesh` (cube, sphere, cylinder)
2. **Extruder** — `E` (extrude faces/edges/verts)
3. **Inset** — `I` (crée des boucles internes)
4. **Loop Cut** — `Ctrl+R` (découpe des boucles de subdivision)
5. **Bevel** — `Ctrl+B` (chanfrein d'arêtes)
6. **Knife** — `K` (coupe libre)
7. **Merge** — `M` (fusionne vertices)
8. **Subdivision Surface** — Modifier (lissage)

### Poly Modeling (Avancé)

- **Edge flow** — suivre les lignes de tension anatomiques/mécaniques
- **All Quad** — privilégier les faces quadrilatères (quads)
- **Pole management** — contrôler les pôles (3/5/6 edges)
- **Support loops** — arêtes de soutien pour les surfaces durcies
- **Crease** — `Shift+E` (plier sans support loops)

### Hard Surface

- **Bevel** et **Boolean** modificateurs
- **Shrinkwrap** pour plaquer sur surface existante
- **Mirror** pour symétrie
- **Array** pour répétitions
- **Solidify** pour l'épaisseur des parois
- **Remesh** pour uniformiser le maillage

### Organic / Character Modeling

- **Sculpt → Retopo** cycle (voir blender-sculpting)
- **Face orientation** — Overlay pour checker les normales
- **Shrinkwrap + Subsurf** pour retopologie sur high-poly
- **Skin modifier** pour squelettes rapides
- **Proportional Editing** `O` — déformations organiques

### Retopologie

| Méthode | Usage | Touche |
|---------|-------|--------|
| Poly Build | Dessiner quad par quad | `Ctrl+Left Click` |
| Grid Fill | Remplir un trou avec grille | `Space > Grid Fill` |
| Snap to Face | Aligner sur surface high-poly | Magnet > Face |
| BSurfaces | Retopo semi-automatique (Add-on) | Inclus Blender 2.80+ |
| Shrinkwrap | Projeter sur mesh cible | Modifier |

### Curves

- **Bezier Curves** — `Shift+A > Curve > Bezier`
- **Curve to Mesh** — `Object > Convert > Mesh`
- **Bevel object** — utiliser une curve comme profile de sweep
- **Geometry Nodes** — bien plus puissant que curves seules

## Modificateurs Clés

| Modifier | Raccourci | Usage |
|----------|-----------|-------|
| Subdivision Surface | Subsurf | Lissage | 
| Mirror | — | Symétrie |
| Array | — | Répétitions |
| Bevel | `Ctrl+B` mesh | Chanfrein |
| Boolean | — | CSG (Union/Diff/Intersect) |
| Solidify | — | Épaisseur |
| Remesh | — | Ré-échantillonnage voxel |
| Decimate | — | Réduction poly-count |
| Shrinkwrap | — | Projection sur surface |
| Multiresolution | — | Subdivision pour sculpting |
| Lattice | — | Déformation grille |
| Simple Deform | — | Bend/Twist/Stretch |
| Skin | — | Création mesh à partir de verts |
| Build | — | Animation de construction |
| Weld | — | Fusion de vertices |

## Raccourcis Essentiels

| Touche | Action |
|--------|--------|
| `Tab` | Edit / Object Mode toggle |
| `1/2/3` | Vertex / Edge / Face select |
| `Ctrl+Tab` | Mesh select mode menu |
| `E` | Extrude |
| `I` | Inset |
| `Ctrl+R` | Loop Cut |
| `K` | Knife |
| `B` | Box select |
| `C` | Circle select (brush mode) |
| `Ctrl+B` | Bevel |
| `Alt+Click Edge` | Edge loop select |
| `Ctrl+E` | Edge menu (bridge, etc.) |
| `Ctrl+F` | Face menu |
| `M` | Merge vertices |
| `O` | Proportional editing toggle |
| `H` | Hide selection |
| `Alt+H` | Unhide all |
| `Shift+Ctrl+Alt+S` | Shear |
| `Ctrl+J` | Join objects |
| `Ctrl+L` | Link data |

## Add-ons Recommandés (Activés par défaut dans Blender 4.x)

- **F2** — Advanced edge/face tools
- **LoopTools** — Bridge, relax, space, flatten, etc.
- **Bsurfaces** — Retopologie
- **Mesh: 3D-Print Toolbox** — Vérification d'impression
- **Node Wrangler** — Gestion shader nodes

## Scripts Python (bpy) — Exemples Rapides

```python
# Créer un cube avec subdivision
import bpy
bpy.ops.mesh.primitive_cube_add(size=2)
bpy.ops.object.modifier_add(type='SUBSURF')
```

```python
# Appliquer tous les modificateurs
for obj in bpy.context.selected_objects:
    for mod in obj.modifiers:
        bpy.ops.object.modifier_apply(modifier=mod.name)
```

```python
# Bridge edge loops entre deux sélections
bpy.ops.mesh.bridge_edge_loops()
```

## Workflow Production

1. **Block-in** — volumes grossiers, proportions
2. **High-poly** — détails, subdivisions, bevels
3. **Low-poly** — retopologie, optimisation poly-count
4. **UV unwrap** — voir blender-texturing
5. **Bake** — normal/displacement maps du high vers le low
6. **Export** — FBX/OBJ/glTF/abc

### Export

```bash
# Ligne de commande Blender pour exporter
blender myfile.blend --background --python \
  -c "import bpy; bpy.ops.export_scene.fbx(filepath='output.fbx', use_selection=True)"
```

## Pitfalls

1. **Ngons sur modèles de jeu** — les ngons (n>4 edges) cassent les subdivisions
2. **Vertices non fusionnés** — `M > By Distance` après boolean
3. **Normales inversées** — `Shift+N` (recalculate outside)
4. **Échelle non appliquée** — `Ctrl+A > Scale` (casse subsurf/bevel sinon)
5. **Support loops trop serrés** — crée des artefacts de shading à distance
6. **Triangles incontrôlés** — les triangles sont acceptables sur des surfaces planes/rigides
7. **Poles à 5+ edges** — déforment le subsurf localement
8. **Overlap de vertices** — Weld modifier après Mirror

## Voir Aussi

- `blender-sculpting` — Sculpture organique / high-poly
- `blender-shading` — Matériaux et shaders
- `blender-geometry-nodes` — Modélisation procédurale par nœuds
- `blender-texturing` — UV maps et texture painting