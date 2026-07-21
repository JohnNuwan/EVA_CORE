---
name: blender-texturing
description: "Texturing dans Blender — UV unwrapping, texture painting, PBR maps, baking, image textures, matériaux avec Node Wrangler, workflows Substance Painter ↔ Blender."
version: 1.0.0
category: creative
tags:
  - blender
  - texturing
  - uv-mapping
  - texture-painting
  - pbr
  - baking
  - materials
  - 3d
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Node Wrangler add-on recommandé (activé par défaut dans Blender 4.x)."
metadata:
  hermes:
    tags:
      - blender
      - texturing
      - uv-mapping
      - texture-painting
      - pbr
      - baking
      - materials
    related_skills:
      - blender-modeling
      - blender-shading
      - blender-sculpting
    category: creative
---

# Blender — Texturing

Guide complet pour le texturing dans Blender : UV unwrapping, texture
painting, baking PBR, et workflows de matériaux.

## UV Unwrapping

### Le Processus

1. **Mark Seams** — `Ctrl+E > Mark Seam` (arêtes où l'UV se déchire)
   - Zones cachées (inner elbow, under chin)
   - Suivre l'edge flow naturel
   - Éviter les faces avant visibles
2. **Unwrap** — `U > Unwrap` (ou `U > Smart UV Project pour hard-surface`)
3. **Pack Islands** — `U > Pack Islands` (optimise l'espace)
4. **Scale/rotation manuelle** — `G/R/S` en UV editor
5. **Checker Texture** (Add-on > New Grid Texture) — vérifier la distortion

### Méthodes d'Unwrap

| Méthode | Raccourci | Usage |
|---------|-----------|-------|
| **Unwrap** (angle-based) | `U` | Général |
| **Smart UV Project** | `U > Smart UV` | Hard-surface, rapide |
| **Cube Projection** | `U > Cube` | Boîtes/archi |
| **Sphere/Cylinder** | `U > Sphere/Cylinder` | Objets ronds |
| **Project from View** | `U > Project from View` | Décalquer un angle |
| **Follow Active Quads** | `U > Follow Active Quads` | Maille régulière |
| **Lightmap Pack** | `U > Lightmap Pack` | Jeux (max coverage) |

### UV Layout Bonnes Pratiques

- **Texel Density** — uniforme si possible (vérifier avec `UV > Texel Density`)
- **Padding** — espace entre îles (2-4px pour 2K, 4-8px pour 4K)
- **Déformation minimale** — zones à haute courbure = plus de seams
- **UDIM** — `UV > Export UV Layout` pour peinture externe
- **Overlap checker** — `View > UV Overlap` pour détecter les faces superposées

## Texture Painting

### Mode Paint

1. **Texture Paint mode** — `Mode dropdown > Texture Paint`
2. **Créer une texture** — `Texture Slot > New` (taille, couleur, alpha)
3. **Brosses** — même palette que sculpt (Draw, Soft, etc.)
4. **Stencil** — projeter une image sur le mesh
5. **Project Painting** — peindre sur des faces adjacentes en 3D viewport

### Brosses de Peinture

| Brosse | Usage |
|--------|-------|
| Draw | Peinture standard |
| Soft | Bord doux |
| Multiply/Add | Blending |
| Blur | Adoucir |
| Smear | Étirer |
| Clone | Dupliquer depuis une source |
| Fill | Remplir une île UV |
| Mask | Protéger des zones |

### Texture Slots

- **Base Color** — Couleur diffuse
- **Roughness** — Rugosité (blanc = brillant, noir = mat)
- **Metallic** — Métal (blanc = métal, noir = non-métal)
- **Normal** — Normal map (tangent space)
- **Displacement** — Bump/height
- **Alpha** — Transparence
- **Subsurface** — SSS map
- **Emission** — Émissive map

## Baking (High → Low Poly)

Essentiel après sculpting (blender-sculpting) pour reporter les détails.

### Setup

1. **Low-poly sélectionné** actif, **High-poly** sélectionné en Shift
2. **Render Properties > Bake**
3. **Selected to Active** — cocher
4. **Cage** — distance max de projection (0.01-0.1)

### Maps à Baker

| Map | Space | Description |
|-----|-------|-------------|
| Normal | Tangent | Détails de surface |
| Displacement | Object | Déformation géométrique |
| AO (Ambient Occlusion) | — | Ombres de proximité |
| Curvature | — | Creux/bosses |
| Position | Object | Position map |
| Roughness | — | Depuis matériaux high-poly |
| Metalness | — | Metalness map |
| Combined | — | Toutes couleurs |
| Texture | UV | Diffuse/texture bake |

### Vérification

- `Shader Editor > Normal Map node` connecté
- `Viewport > MatCap` — checker les artefacts
- `Bake margin` — 2-16px selon résolution

## Workflow avec Node Wrangler

Raccourcis clés (`Ctrl+Shift+T` avec Node Wrangler) :

1. Sélectionner le **Principled BSDF**
2. `Ctrl+Shift+T` → sélectionner les fichiers PBR (albedo, roughness, metallic, normal, etc.)
3. Blender connecte automatiquement tous les nodes

**Naming convention** (reconnue automatiquement) :
- `_col` / `_albedo` / `_diff` / `_baseColor` → Base Color
- `_nor` / `_nrm` / `_normal` → Normal
- `_rgh` / `_rough` → Roughness
- `_mtl` / `_metalness` → Metallic
- `_ao` → Ambient Occlusion
- `_disp` / `_height` → Displacement
- `_opac` / `_alpha` → Alpha

## Formats de Texture

| Format | Usage | Bits |
|--------|-------|------|
| PNG | Web, jeux, perte sans perte | 8/16 |
| JPEG | Web, preview (compressé) | 8 |
| EXR | Film, VFX, HDR (16/32 bit float) | 16/32 |
| TGA | Jeux anciens | 8/16 |
| TIFF | Impression, archive | 8/16/32 |
| OpenEXR | Multi-layer, cryptomatte | 16/32 float |

## Export des Textures

```bash
# Export UV Layout via ligne de commande
blender scene.blend --background -- python -c "
import bpy
bpy.context.view_layer.objects.active = bpy.data.objects['mon_objet']
bpy.ops.uv.export_layout(filepath='uv_layout.svg')
"
```

```bash
# Bake via script Python
blender scene.blend --background -- python -c "
import bpy
# Configurer les paramètres de bake
bpy.context.scene.render.bake.use_pass_direct = False
bpy.context.scene.render.bake.use_pass_indirect = False
bpy.context.scene.render.bake.use_pass_color = True
bpy.context.scene.render.bake.margin = 16
bpy.ops.object.bake(type='DIFFUSE')
"
```

## Pitfalls

1. **Seams visibles** — trop peu de seams ou seams mal placés
2. **Texel density inégale** — certaines zones floues/d'autres nettes
3. **Padding insuffisant** — bordures d'artefacts entre îles UV
4. **Normal map mal orientée** — switch Y/Z ou espace tangent
5. **Overlap UV** — faces superposées = artefacts de bake
6. **Échelle non appliquée** — le bake ne fonctionne pas correctement
7. **Textures non packées** — .blend ne s'ouvre pas sans les textures externes
8. **Mip-mapping artefacts** — sur textures très fines, activer interpolation

## Voir Aussi

- `blender-shading` — Matériaux et shader nodes
- `blender-sculpting` — High-poly pour baking
- `blender-modeling` — Low-poly pour baking