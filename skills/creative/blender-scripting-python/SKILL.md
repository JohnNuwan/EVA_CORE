---
name: blender-scripting-python
description: "Scripting Python dans Blender — API bpy, add-ons, automation, batch processing, création d'outils personnalisés, panels, operators, UI, pipeline et intégration."
version: 1.0.0
category: creative
tags:
  - blender
  - python
  - scripting
  - bpy
  - addon
  - automation
  - api
  - pipeline
  - 3d
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Python est intégré à Blender (bpy, bmesh, bpy_extras). Utiliser l'interpréteur Python de Blender ('blender --python script.py')."
metadata:
  hermes:
    tags:
      - blender
      - python
      - scripting
      - bpy
      - addon
      - automation
      - api
      - pipeline
    related_skills:
      - blender-modeling
      - blender-animation
      - blender-geometry-nodes
    category: creative
---

# Blender — Scripting Python

Guide complet du scripting Python dans Blender : API bpy, bmesh,
création d'add-ons, automation, batch processing, panels, operators,
et pipeline d'intégration.

## Architecture Blender Python

```
┌─────────────────────────────────────────┐
│           bpy (module principal)        │
│  ┌──────────────┐  ┌────────────────┐   │
│  │   bpy.data   │  │  bpy.context   │   │
│  │  (BDNA data)  │  │  (contexte)    │   │
│  └──────┬───────┘  └───────┬────────┘   │
│         │                  │            │
│  ┌──────▼──────────────────▼────────┐   │
│  │        bpy.ops (operators)       │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │     bpy.types (classes)          │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │     bmesh (mesh editing)          │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │     bpy.app (timers, handlers)   │   │
│  └──────────────────────────────────┘   │
│  ┌──────────────────────────────────┐   │
│  │     mathutils (vectors, mats)    │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## bpy — Accès aux Données

### bpy.data (Data Blocks)

```python
# Objets
bpy.data.objects["Cube"]
bpy.data.objects["Camera"]
bpy.data.objects["Light"]

# Meshes
bpy.data.meshes["Cube.001"]
bpy.data.meshes.new("MonMeshe")

# Matériaux
bpy.data.materials["Material"]
bpy.data.materials.new("MonMat")

# Textures, Images
bpy.data.images["render_output.png"]

# Collections
bpy.data.collections["Collection"]
```

### bpy.context (Contexte)

```python
bpy.context.scene         # Scène active
bpy.context.view_layer    # View layer
bpy.context.object        # Objet actif
bpy.context.selected_objects  # Liste séléction
bpy.context.visible_objects   # Objets visibles
bpy.context.active_object     # Objet actif
bpy.context.mode             # Mode courant
bpy.context.area             # Zone de l'éditeur
bpy.context.space_data       # Données de l'éditeur
```

### bpy.ops (Operators)

Appel des opérateurs Blender :

```python
# Ajout
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.ops.object.light_add(type='POINT', location=(1, 1, 5))

# Selection
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects["Cube"].select_set(True)

# Mode
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.object.mode_set(mode='SCULPT')

# Modifiers
bpy.ops.object.modifier_add(type='SUBSURF')
bpy.ops.object.modifier_apply(modifier="Subdivision")

# Files
bpy.ops.wm.open_mainfile(filepath="scene.blend")
bpy.ops.wm.save_mainfile()
bpy.ops.export_scene.fbx(filepath="output.fbx")
```

### bpy.app (Application)

```python
bpy.app.version              # Version Blender [4, 0, 0]
bpy.app.background           # True en mode --background
bpy.app.debug_value          # Debug flags
bpy.app.handlers             # Liste des handlers (events)
bpy.app.timers.register()    # Timer personnalisé
```

## bmesh — Edition de Maillage

```python
import bmesh

# Créer un BMesh
bm = bmesh.new()
v1 = bm.verts.new((0, 0, 0))
v2 = bm.verts.new((1, 0, 0))
v3 = bm.verts.new((1, 1, 0))
v4 = bm.verts.new((0, 1, 0))

# Créer une face
face = bm.faces.new((v1, v2, v3, v4))

# Extruder
ret = bmesh.ops.extrude_face_region(bm, geom=[face])
extruded_verts = [v for v in ret['geom'] if isinstance(v, bmesh.types.BMVert)]
for v in extruded_verts:
    v.co.z += 1.0

# Finaliser
mesh = bpy.data.meshes.new("Quad")
bm.to_mesh(mesh)
bm.free()
```

### Opérations bmesh

```python
bmesh.ops.subdivide_edges(bm, edges=bm.edges, cuts=2)
bmesh.ops.bevel(bm, geom=bm.edges, offset=0.1)
bmesh.ops.bridge_loops(bm, edges=[edge_list_a, edge_list_b])
bmesh.ops.remove_doubles(bm, dist=0.001)
bmesh.ops.triangulate(bm, faces=bm.faces)
bmesh.ops.dissolve_limit(bm, angle_limit=5, verts=bm.verts)
bmesh.ops.transform(bm, matrix=mat, verts=bm.verts)
```

## mathutils — Vecteurs et Matrices

```python
import mathutils
from mathutils import Vector, Matrix, Euler, Quaternion

# Vecteurs
v = Vector((1, 2, 3))
v2 = Vector((4, 5, 6))
v.dot(v2)      # Produit scalaire
v.cross(v2)    # Produit vectoriel
v.length       # Norme
v.normalized() # Normalisé

# Matrices
mat = Matrix.Translation(Vector((0, 0, 1)))
rot = Euler((0, 0, 1.57), 'XYZ').to_matrix().to_4x4()
scale = Matrix.Scale(2, 4)
transform = mat @ rot @ scale

# Quaternions
q = Quaternion((1, 0, 0, 0))  # Identité
q2 = Quaternion((0.707, 0.707, 0, 0))  # Rotation 90° X
```

## Automatisation et Batch

### Script Headless (mode --background)

```bash
blender scene.blend --background --python mon_script.py
blender --background --python create_scene.py
blender --background --python batch_export.py
```

### Exemple Batch Export FBX

```python
# batch_export.py
import bpy
import os
import sys

input_dir = sys.argv[-2] if len(sys.argv) > 1 else "."
output_dir = sys.argv[-1] if len(sys.argv) > 2 else "exports"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith(".blend"):
        path = os.path.join(input_dir, filename)
        bpy.ops.wm.open_mainfile(filepath=path)
        basename = os.path.splitext(filename)[0]
        out_path = os.path.join(output_dir, f"{basename}.fbx")
        bpy.ops.export_scene.fbx(filepath=out_path)
        print(f"Exported: {path} -> {out_path}")
```

```bash
blender --background --python batch_export.py -- ./scenes ./exports
```

## Add-ons (Modules)

### Structure d'un Add-on

```
mon_addon/
├── __init__.py      # Metadata + register/unregister
├── operators.py     # Classes d'opérateurs
├── ui.py            # Panels et menus
├── properties.py    # PropertyGroups
└── utils.py         # Fonctions utilitaires
```

### __init__.py

```python
bl_info = {
    "name": "Mon Addon",
    "author": "Moi",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > Mon Tab",
    "description": "Description de l'addon",
    "category": "Object",
}

modules = ["operators", "ui", "properties"]

def register():
    for m in modules:
        exec(f"import {m}")
        exec(f"{m}.register()")

def unregister():
    for m in reversed(modules):
        exec(f"{m}.unregister()")
```

### Créer un Operator

```python
import bpy

class MES_OT_mon_operateur(bpy.types.Operator):
    """Description de l'opérateur"""
    bl_idname = "mesh.mon_operateur"
    bl_label = "Mon Opérateur"
    bl_options = {'REGISTER', 'UNDO'}

    # Propriétés (options)
    scale: bpy.props.FloatProperty(
        name="Scale",
        default=1.0,
        min=0.1,
        max=10.0,
    )

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        obj.scale = (self.scale, self.scale, self.scale)
        return {'FINISHED'}
```

### Créer un Panel

```python
class MES_PT_mon_panel(bpy.types.Panel):
    bl_label = "Mon Panel"
    bl_idname = "MES_PT_mon_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Mon Outil"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Paramètres")
        layout.prop(context.active_object, "scale")
        layout.operator("mesh.mon_operateur")
```

### Properties (PropertyGroup)

```python
class MonGroupeProprietes(bpy.types.PropertyGroup):
    ma_prop: bpy.props.FloatProperty(
        name="Ma Propriété",
        default=1.0,
        min=0.0,
        max=100.0,
    )

# Enregistrement
bpy.utils.register_class(MonGroupeProprietes)
bpy.types.Scene.mon_groupe = bpy.props.PointerProperty(
    type=MonGroupeProprietes
)

# Usage
bpy.context.scene.mon_groupe.ma_prop
```

## Handlers et Timers

### Handlers (Events)

```python
def mon_handler(scene):
    print(f"Frame changed: {scene.frame_current}")

bpy.app.handlers.frame_change_pre.append(mon_handler)
bpy.app.handlers.render_post.append(mon_handler)
bpy.app.handlers.depsgraph_update_post.append(mon_handler)
```

### Timers

```python
import bpy

def mon_timer():
    print("Timer tick...")
    return 0.5  # Re-appel dans 0.5 sec

bpy.app.timers.register(mon_timer)
```

### Types de Handlers

| Handler | Quand |
|---------|-------|
| `frame_change_pre/post` | Avant/après changement de frame |
| `render_init/complete/cancel` | Rendu |
| `load_pre/post` | Chargement fichier .blend |
| `save_pre/post` | Sauvegarde .blend |
| `depsgraph_update_pre/post` | Mise à jour du graphe |
| `object_updated` | Objet modifié |
| `version_updated` | Mise à jour de version |

## Exemples de Scripts Utiles

```python
# Appliquer scale/rotation à tous les objets
import bpy
for obj in bpy.context.scene.objects:
    obj.select_set(True)
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# Exporter chaque objet individuellement en OBJ
import bpy, os
out = "exports/"
os.makedirs(out, exist_ok=True)
for obj in bpy.data.objects:
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.ops.wm.obj_export(filepath=f"{out}/{obj.name}.obj")

# Créer une animation de rotation
import bpy, math
obj = bpy.context.active_object
for frame in range(0, 100):
    bpy.context.scene.frame_set(frame)
    obj.rotation_euler.z = frame * math.radians(3.6)
    obj.keyframe_insert(data_path="rotation_euler", index=2)
```

## Débogage

```python
# Imprimer toutes les propriétés d'un objet
for prop in dir(bpy.context.object):
    if not prop.startswith('_'):
        print(f"{prop}: {getattr(bpy.context.object, prop)}")

# Imprimer l'arborescence bpy.data
for collection in bpy.data.collections:
    print(f"Collection: {collection.name}")
    for obj in collection.objects:
        print(f"  {obj.name} ({obj.type})")

# Voir les opérateurs disponibles
print([op for op in dir(bpy.ops) if not op.startswith('_')])

# Voir les propriétés d'un operateur
print(bpy.ops.mesh.primitive_cube_add.get_rna().properties)
```

## Pitfalls

1. **bpy n'existe pas en dehors de Blender** — tester avec `blender --python`
2. **bpy.ops échoue en background** — certains ops nécessitent un contexte (area)
3. **Scale non uniforme + Modifier** — `object.scale = (1, 1, 1)` avant modificateurs
4. **BMesh non libéré** — `bm.free()` ou fuite mémoire
5. **Context incorrect** — passer `{'area': ...}` ou utiliser `override`
6. **Blender API changes** — Python API change entre versions majeures
7. **Redraw manuel** — `bpy.context.area.tag_redraw()` après changement UI
8. **Add-on non enregistré** — `bpy.utils.register_class()` oublié

## Voir Aussi

- `blender-modeling` — Automatisation de modélisation
- `blender-animation` — Scripts d'animation
- `blender-geometry-nodes` — Scripts pour créer/modifier des GN