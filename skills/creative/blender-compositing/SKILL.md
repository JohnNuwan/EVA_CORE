---
name: blender-compositing
description: "Compositing dans Blender — Node Compositor, post-processing, color grading, passes (diffuse, glossy, mist, cryptomatte), glow, bloom, depth of field, VFX, render layers."
version: 1.0.0
category: creative
tags:
  - blender
  - compositing
  - node-compositor
  - post-processing
  - color-grading
  - vfx
  - render-passes
  - cryptomatte
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Node Wrangler add-on recommandé pour le compositing."
metadata:
  hermes:
    tags:
      - blender
      - compositing
      - node-compositor
      - post-processing
      - color-grading
      - vfx
      - render-passes
      - cryptomatte
    related_skills:
      - blender-lighting
      - blender-shading
      - blender-texturing
    category: creative
---

# Blender — Compositing

Guide complet du Compositing dans Blender. Node Compositor, color grading,
render passes, cryptomatte, effets visuels, corrections et exports.

## Node Compositor

**Accès** : `Compositing` workspace (split view + compositor nodes)
**Activer** : Cocher `Use Nodes` dans le backdrop

### Noeuds Essentiels

| Noeud | Catégorie | Usage |
|-------|-----------|-------|
| **Composite** | Output | Sortie finale |
| **Viewer** | Output | Aperçu dans le backdrop |
| **RLayers** | Input | Render layers de la scène |
| **Image** | Input | Image externe |
| **Alpha Over** | Color | Superposer avec alpha |
| **Mix** | Color | Mixer couleurs |
| **Z Combine** | Color | Combiner selon profondeur |
| **Color Balance** | Color | Balance des couleurs |
| **Hue Correct** | Color | Correction teinte/sat/val |
| **RGB Curves** | Color | Courbes de couleur |
| **Color Ramp** | Converter | Remap couleur |
| **Bright/Contrast** | Color | Luminosité/contraste |
| **Exposure** | Color | Exposition (EV) |
| **Gamma** | Color | Correction gamma |
| **Blur** | Filter | Flou (gaussien, box, fast) |
| **Defocus** | Filter | Profondeur de champ |
| **Glare** | Filter | Bloom/Ghosts |
| **Lens Distortion** | Distort | Distorsion d'objectif |
| **Scale** | Distort | Redimensionnement |
| **Render Layers** | Input | Passes de rendu |
| **Cryptomatte** | Matte | Masques par nom d'objet |
| **ID Mask** | Matte | Masques par index |
| **Keying** | Matte | Keying green/blue screen |
| **Chroma Key** | Matte | Keying simple |
| **Track Position** | Distort | Données de tracking |
| **Plane Track Deform** | Distort | Déformation trackée |
| **Sun Beams** | Filter | Rayons de soleil |
| **Pixelate** | Filter | Pixelation |
| **Invert** | Color | Inversion de couleur |
| **Stabilize** | Filter | Stabilisation d'image |

## Render Passes

### Activation

1. `View Layer Properties > Passes`
2. Cocher les passes nécessaires
3. Connecter `Render Layers` au Compositor

### Passes Disponibles

| Passe | Usage | Type |
|-------|-------|------|
| **Combined** | Image finale (tout mélangé) | Couleur |
| **Diffuse** | Couleur diffuse seule | Couleur |
| **Glossy** | Réflexions glossy | Couleur |
| **Transmission** | Lumière transmise (verre) | Couleur |
| **Emission** | Lumière émise | Couleur |
| **Environment** | Éclairage HDRI | Couleur |
| **Shadow** | Zones d'ombre | Couleur |
| **Ambient Occlusion** | AO seule | Couleur |
| **Normal** | Normales world space | Vecteur |
| **Position** | Position 3D | Vecteur |
| **Mist** | Brume de distance | Valeur |
| **Z** | Profondeur | Valeur |
| **IndexOB** | Index d'objet | Valeur |
| **IndexMA** | Index de matériau | Valeur |
| **UV** | Coordonnées UV | Vecteur |
| **Vector** | Vecteur de mouvement (motion blur) | Vecteur |
| **Cryptomatte** | Masques intelligents | Couleur |

### Utilisation des Passes

```
RLayers (Combined) → Mix → Composite
RLayers (Diffuse) → Color Balance → Mix
RLayers (Mist) → Color Ramp → Mix (facultatif)
```

## Color Grading

### RGB Curves Workflow

1. Connecter `RLayers Image` → `RGB Curves`
2. Ajuster les courbes R/G/B individuellement
3. Master curve pour le contraste général
4. C (cyan/M), M (magenta/Y), Y (yellow) pour les compléments

### Color Balance

- **Lift** — Ombres (shadows)
- **Gamma** — Tons moyens (midtones)
- **Gain** — Hautes lumières (highlights)
- **Offset / Power / Slope (ASC CDL)** — Davinci Resolve colorspace

### Look (LUT)

- **Apply LUT** — fichier `.cube` ou `.png`
- **Convert Colorspace** — sRGB, Rec709, ACES, etc.
- **Filmic** — AGX (Blender 4.x) pour dynamique réaliste

### Vignette

1. Créer un dégradé radial
2. Mix avec l'image (Multiply ou Screen)
3. Adoucir avec Blur

## Effets Visuels

### Glare / Bloom

| Type | Usage |
|------|-------|
| **Glare > Fog Glow** | Brume lumineuse (soft) |
| **Glare > Bloom** | Bloom éclatant |
| **Glare > Simple Star** | Étoiles (4 pointes) |
| **Glare > Ghosts** | Lentilles fantômes |

**Réglages :** Mix (0-1), Threshold, Size, Streaks

### Depth of Field

1. Passe Z connectée au `Defocus` node
2. **fStop** — profondeur de champ (petit = flou fort)
3. **Max Blur** — limite du flou
4. **Focus Distance** — distance de mise au point
5. **Use Z Buffer** — basé sur la passe Z

### Motion Blur

- Soit dans le Render Settings (Cycles/EEVEE)
- Soit passe Vector → `Vector Blur` node

### Lens Distortion

- **Distortion** — négatif (fisheye) / positif (barrel)
- **Dispersion** — aberration chromatique (RGB split)
- **Jitter** — grain de projecteur

## Cryptomatte

Masques intelligents par nom d'objet ou matériau.

1. Activer `Cryptomatte` dans View Layer Passes
2. Ajouter `Cryptomatte` node dans Compositor
3. **Pick** — sélectionner l'objet/matériau dans l'aperçu
4. **Matte** — sortie du masque
5. **Image** — sortie avec fond transparent

### Cryptomatte Operations

- Alpha Over avec fond transparent
- Correction de couleur par objet
- Effets isolés sur un objet

## Keying (Green/Blue Screen)

1. Ajouter **Keying** node
2. Connecter l'image source
3. **Screen Color** — pipette sur le fond vert
4. **Clip Black / White** — ajuster le key
5. **Despill** — supprimer le reflet vert
6. **Edge Artifacts** — Dilate/Erode + Blur

## Time Effects

| Noeud | Usage |
|-------|-------|
| **Time** | Sélectionner une frame spécifique |
| **Movie Clip** | Entrée vidéo |
| **Time Shift** | Décaler le clip (retard/avance) |
| **Speed Control** | Ralentir/accélérer |

## Multi-Layer Compositing

```bash
# Rendu avec passes séparées via CLI
blender scene.blend --background --render-output //render_ \
  --render-format OPEN_EXR_MULTILAYER --render-frame 1
```

Le fichier EXR contient toutes les passes. Re-compositer plus tard
sans re-rendre.

## Scripts Compositing

```python
# Ajouter un node Glare au compositor
import bpy
tree = bpy.context.scene.node_tree
glare = tree.nodes.new('CompositorNodeGlare')
glare.glare_type = 'FOG_GLOW'
glare.quality = 'HIGH'
glare.threshold = 0.5
glare.mix = 0.3
tree.links.new(
    tree.nodes['Render Layers'].outputs['Image'],
    glare.inputs['Image']
)
tree.links.new(
    glare.outputs['Image'],
    tree.nodes['Composite'].inputs['Image']
)
```

```python
# Afficher toutes les passes disponibles
import bpy
rl = bpy.context.view_layer
for attr in dir(rl):
    if attr.startswith('use_pass') and getattr(rl, attr):
        print(attr)
```

## Pitfalls

1. **Passes vides** — une passe non activée dans View Layer ne contient rien
2. **Cryptomatte bruité** — augmenter les samples ou lisser le matte
3. **Gamma sur HDR** — ne pas appliquer de correction gamma sur EXR linéaire
4. **Backdrop lent** — désactiver le backdrop pour les grosses compos
5. **Node tree non connecté** — le Composite output doit être connecté
6. **File format limité** — EXR avec passes ne s'exporte pas en PNG
7. **Color space mismatch** — les textures sRGB vs linear causent des décalages
8. **Z/Depth overflow** — valeurs Z trop grandes écrasent le Defocus

## Voir Aussi

- `blender-lighting` — Éclairage qui affecte les passes
- `blender-shading` — Matériaux et leurs passes
- `blender-texturing` — Textures en entrée du compositor