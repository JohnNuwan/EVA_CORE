---
name: blender-lighting
description: "Éclairage dans Blender — Cycles et EEVEE, types de lumières, HDRI, trois-points lighting, studio lighting, light probes (EEVEE), world shaders, optimisation et rendu."
version: 1.0.0
category: creative
tags:
  - blender
  - lighting
  - éclairage
  - cycles
  - eevee
  - hdri
  - studio-lighting
  - rendering
  - 3d
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Les fichiers HDRI peuvent être téléchargés depuis Poly Haven (ex-HDRI Haven)."
metadata:
  hermes:
    tags:
      - blender
      - lighting
      - éclairage
      - cycles
      - eevee
      - hdri
      - studio-lighting
      - rendering
    related_skills:
      - blender-shading
      - blender-compositing
      - blender-texturing
    category: creative
---

# Blender — Éclairage

Guide complet de l'éclairage 3D dans Blender. Techniques pour Cycles
(path tracing) et EEVEE (temps réel), du lighting studio à l'éclairage
architectural, extérieur et volumétrique.

## Types de Lumières

| Type | Raccourci | Usage |
|------|-----------|-------|
| **Point** | `Shift+A > Light > Point` | Ampoule, omnidirectionnelle |
| **Sun** | `Shift+A > Light > Sun` | Soleil (directionnel, parallèle) |
| **Spot** | `Shift+A > Light > Spot` | Projecteur (spot angle + blend) |
| **Area** | `Shift+A > Light > Area` | Softbox, fenêtre (réaliste) |
| **Sphere** + Emission | Mesh + Emission shader | Panneau lumineux physique |

### Paramètres de Lumière

| Paramètre | Point | Sun | Spot | Area |
|-----------|-------|-----|------|------|
| Power (W) | ✓ | ✓ | ✓ | ✓ |
| Color | ✓ | ✓ | ✓ | ✓ |
| Shadow Softness | — | Angle | ✓ | ✓ |
| Spot Size | — | — | ✓ | — |
| Spot Blend | — | — | ✓ | — |
| Size | ✓ | — | — | ✓ |
| Radius | ✓ | — | ✓ | — |

## Techniques d'Éclairage

### Three-Point Lighting (Standard)

```
Back Light (Rim)
     │
     │
   Key ────── Fill
```

| Lumière | Position | Puissance | Usage |
|---------|----------|-----------|-------|
| **Key** | 45° horizontal, 30-45° vertical | 100% | Source principale |
| **Fill** | 45° opposé du key, hauteur similaire | 30-60% | Adoucir les ombres |
| **Back/Rim** | Derrière, au-dessus | 80-120% | Séparer du fond |

### Studio Lighting

- **Softbox** (Area light, size > distance) — portrait/produit
- **Beauty Dish** (Area light, medium soft) — portrait contrasté
- **Hard light** (Point/Spot, petite taille) — drame, effets
- **RGB lights** — effets créatifs, néons
- **Gobo** — pattern projeté avec texture sur Spot

### HDRI / World Lighting

1. **World Properties** → Color (Surface)
2. **Environment Texture** node → charger .hdr
3. **Poly Haven** : https://polyhaven.com/hdris
4. **Rotation** — `World > Mapping > Rotation (Z)`
5. **Strength** — `Background > Strength`
6. **Transparent** — `Film > Transparent` (rendu sans fond)

**Avantages HDRI** : éclairage réaliste, réflexions environnementales,
ombres douces, temps de setup minimal.

### Éclairage Extérieur / Daylight

- **Sun light** — direction et angle principal
- **Color** — bleuté (midi) → orangé (coucher du soleil)
- **Strength** — 1-10 W/m² selon ambiance
- **Sky Texture** (World) — ciel procedural avec sun position
- **Sun Positioner** (Add-on) — géolocalisation précise

### Éclairage Architectural

- **Area lights aux fenêtres** — simuler la lumière naturelle
- **Portal lights** — Cycles only, accélère l'éclairage intérieur
- **IES profiles** — Spot + IES pour luminaires réalistes
- **Mesh lights** — ampoules et tubes physiques
- **Ambient occlusion** dans le world shader

## EEVEE Light Probes

EEVEE nécessite des probes pour réflexions et rebonds indirects.

| Probe | Ajout | Usage |
|-------|-------|-------|
| **Reflection Cube** | `Shift+A > Light Probe > Cube` | Réflexions cubemap |
| **Reflection Plane** | `Shift+A > Light Probe > Plane` | Réflexions planes (sols, miroirs) |
| **Irradiance Volume** | `Shift+A > Light Probe > Irradiance` | Éclairage indirect (bounces) |

**Workflow EEVEE Probes :**
1. Placer les Reflection Cubes dans l'espace
2. Placer un Irradiance Volume autour du set
3. `Probe > Bake All` pour calculer
4. Refresh après changement de lighting

### EEVEE Settings Clés

| Setting | Valeur | Description |
|---------|--------|-------------|
| **Bloom** | 0.0-1.0 | Effet lumineux global |
| **SSR** | On | Screen-space reflections |
| **Volumetrics** | On/Off | Volume scattering |
| **Translucence** | On | SSS approximé |
| **Ambient Occlusion** | On | AO screen-space |
| **Soft Shadows** | On | Adoucir les ombres |
| **Jitter** | >0.5 | Anti-crénelage ombres |
| **Light Threshold** | 0.01-0.1 | Qualité/performance |

## Éclairage Volumétrique

### Cycles

1. Ajouter un cube englobant la scène
2. Volume Shader > Principled Volume ou Volume Scatter
3. Density: 0.001-0.1

### EEVEE

1. Activer **Volumetrics** dans Render Properties
2. **Volumetric Start/End** — distance de début/fin
3. **Volumetric Tile Size** — 2px-8px (qualité)
4. **Volumetric Samples** — 64-128

## Light Linking (Blender 4.x)

Lier des lumières à des objets spécifiques :

1. Sélectionner la lampe
2. `Object Properties > Light Linking`
3. Ajouter les objets à éclairer (ou exclure)
4. Permet le contrôle précis sans affecter le reste

## Irradiance / Gobos

- **Gobo avec Spot** : texture dans la source
- **Volumetric Gobo** : nuage de fumée + spot
- **Shadow Catcher** : capturer les ombres sur un plan transparent

## Optimisation Rendu

| Technique | Cycles | EEVEE |
|-----------|--------|-------|
| Limit light bounces | 4-6 | N/A |
| Portal lights (intérieur) | ✓ | — |
| Adaptive sampling | ✓ | — |
| Denoising (OptiX/OIDN) | ✓ | — |
| Light threshold | 0.01 | ✓ |
| Shadow maps | — | ✓ |
| Probe baking | — | ✓ |
| Irradiance cache | ✓ | — |

## Pitfalls

1. **HDRI trop sombre** — augmenter Strength: 1-5 pour scènes intérieures
2. **EEVEE sans probes** — pas de réflexions hors écran, pas d'éclairage indirect
3. **Portal lights oubliées** — rend intérieur Cycles très lent
4. **Light size = 0** — ombres dures et bruit (Cycles)
5. **Sun pas assez puissant** — 1-5 W/m² pour daylight standard
6. **Caustics lentes** — désactiver sauf si absolument nécessaire
7. **Fireflies** — Clamp indirect light à 1-3, augmenter samples
8. **Unités réalistes** — utiliser des watts et lumens pour un résultat prévisible

## Scripts Utiles

```python
# Créer un setup 3-point lights rapidement
import bpy
bpy.ops.object.light_add(type='AREA', location=(2, -2, 4))
bpy.context.object.data.energy = 200  # Key
bpy.ops.object.light_add(type='AREA', location=(-2, 1, 2))
bpy.context.object.data.energy = 80   # Fill
bpy.ops.object.light_add(type='AREA', location=(3, 3, 6))
bpy.context.object.data.energy = 300  # Rim
```

## Voir Aussi

- `blender-shading` — Matériaux réactifs à la lumière
- `blender-compositing` — Post-traitement : glows, adjustments
- `blender-texturing` — Textures qui interagissent avec l'éclairage