---
name: blender-shading
description: "Shading dans Blender — Shader Nodes, matériaux procéduraux, Principled BSDF, Cycles vs EEVEE, volumes, subsurface scattering, displacement, matériaux complexes node-based."
version: 1.0.0
category: creative
tags:
  - blender
  - shading
  - shader-nodes
  - materials
  - cycles
  - eevee
  - procedural-textures
  - pbr
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Node Wrangler add-on fortement recommandé pour la navigation dans les shader nodes."
metadata:
  hermes:
    tags:
      - blender
      - shading
      - shader-nodes
      - materials
      - cycles
      - eevee
      - procedural-textures
      - pbr
    related_skills:
      - blender-texturing
      - blender-lighting
      - blender-modeling
    category: creative
---

# Blender — Shading

Guide complet pour la création de matériaux et shaders dans Blender.
Couvre le Shader Editor, les matériaux procéduraux, Cycles, EEVEE,
volumes et subsurface scattering.

## Shader Editor

**Workflow** : `Shading` workspace (split 3D view + Shader Editor)

### Noeuds Essentiels

| Noeud | Catégorie | Usage |
|-------|-----------|-------|
| **Principled BSDF** | Shader | Matériau universel PBR |
| **Diffuse BSDF** | Shader | Lambertien simple |
| **Glossy BSDF** | Shader | Réflexions |
| **Glass BSDF** | Shader | Verre, réfractions |
| **Transparent BSDF** | Shader | Transparence alpha |
| **Emission** | Shader | Lumière émise |
| **Mix Shader** | Color | Mélanger 2 shaders |
| **Add Shader** | Color | Additionner shaders |
| **Volume Absorption** | Volume | Fumée, brouillard |
| **Volume Scatter** | Volume | Nuages, milk |
| **Principled Volume** | Volume | Volume PBR complet |
| **Musgrave** | Texture | Bruit procédural |
| **Noise Texture** | Texture | Bruit fractal |
| **Wave Texture** | Texture | Ondes |
| **Checker** | Texture | Damier |
| **Voronoi** | Texture | Cellules, taches |
| **Brick** | Texture | Brique |
| **Map Range** | Converter | Remapper les valeurs |
| **Color Ramp** | Converter | Gradient de couleurs |
| **Math** | Converter | Opérations arithmétiques |
| **Vector Math** | Converter | Opérations vectorielles |
| **Bump** | Vector | Normal mapping procédural |
| **Displacement** | Vector | Déplacement géométrique |
| **Normal Map** | Vector | Normal map depuis texture |

### Principled BSDF — Réglages Clés

| Paramètre | Valeur | Description |
|-----------|--------|-------------|
| Base Color | Color | Couleur diffuse / albedo |
| Metallic | 0.0-1.0 | Métal (1 = conducteur) |
| Roughness | 0.0-1.0 | Rugosité (0 = mirror) |
| IOR | 1.0-2.5 | Indice de réfraction |
| Alpha | 0.0-1.0 | Transparence |
| Normal | Vector | Normal map en tangent space |
| Clearcoat | 0.0-1.0 | Couche vernis |
| Clearcoat Roughness | 0.0-1.0 | Rugosité du vernis |
| Subsurface | 0.0-1.0 | Subsurface scattering weight |
| Subsurface Radius | Color | Rayon SSS (R/G/B) |
| Subsurface Color | Color | Teinte du SSS |
| Sheen | 0.0-1.0 | Microfibre (velours) |
| Sheen Tint | 0.0-1.0 | Teinte du sheen |
| Emission | Color | Lumière émise |
| Emission Strength | 0.0+ | Intensité émissive |

## Matériaux Procéduraux

Exemples de matériaux 100% nodes (sans image texture).

### Métal brossé

```
Noise Texture (scale:200) → Color Ramp (contraste) → Bump →
Principled BSDF (Metallic:1, Roughness:0.1-0.3)
```

### Caoutchouc / Mat

```
Musgrave Texture → Color Ramp (subtle contrast) → Bump →
Principled BSDF (Metallic:0, Roughness:0.8-1.0)
```

### Verre

```
Principled BSDF (Transmission:1, IOR:1.45, Roughness:0.0)
→ Mix avec Glossy pour le reflet
```

### Eau

```
Principled BSDF (Transmission:1, IOR:1.33, Roughness:0.0-0.05)
Wave Texture en Normal map (scale:1m-10m)
Displacement avec Noise Texture
```

### Bois

```
Wave Texture (scale:500) → Color Ramp (teintes bois)
Mix avec Noise Texture (grain)
→ Principled BSDF (Roughness:0.6-0.9)
```

## Cycles vs EEVEE

| Feature | Cycles | EEVEE |
|---------|--------|-------|
| Renderer | Path tracing (physique) | Rasterization (temps réel) |
| Réflexions | Réelles (tracing) | Screen-space / Planar probes |
| Réfractions | Oui | Limited / Screen-space |
| SSS | Physique | Approximé |
| Volumes | Oui (Heterogeneous) | Oui (homogène, limited) |
| Caustics | Oui (option) | Non |
| AO | Oui | Screen-space |
| Shadows | Physique | Shadow maps + raytracing |
| Temps | Lent (seconds-minutes) | Instantané |
| Bruit | Oui (nécessite échantillons) | Non (raster) |
| Optix denoise | Oui (automatique) | N/A |

### Optimisation Cycles

- **Échantillons** : 128-512 (prévisualisation), 1024-4096 (final)
- **Light Paths** : Max Bounces 4-8, Diffuse 4, Glossy 4, Transmission 8, Volume 1
- **Denoising** : Activer OptiX (NVIDIA) ou OpenImageDenoise
- **Tile Size** : 256×256 (GPU), 64×64 (CPU)
- **Noise Threshold** : 0.01 (auto-stop)
- **Caustics** : Désactiver si non nécessaires
- **Portal lights** : Accélère l'éclairage intérieur
- **Adaptive Sampling** : Activer

## Volumes

### Brume / Atmosphère

```
World Shader:
Volume Scatter (Density:0.001-0.01, Color: bleu/brume)
```

### Nuages

```
Object avec volume shader:
Principled Volume (Density:1-5, anisotropy:0.8)
+ Noise Texture contrôlant la densité
```

### Fumée (avec simulation)

```
Quick Smoke → Domain object
Flow: Temperature (+ Color Ramp)
Density: control with Math nodes
```

## Groupes de Noeuds

Créer des groupes réutilisables :

1. Sélectionner les noeuds → `Ctrl+G`
2. Nommer le groupe dans le Group panel
3. Exposer les entrées/sorties (`Node Socket` dans `Group > Interface`)
4. Réutiliser avec `Shift+A > Group`

**Stockage** — `.blend` library (`File > Link/Append`) ou asset browser.

## Shader to RGB (EEVEE Only)

Permet de manipuler les couleurs d'un shader avec des noeuds de texture :

1. `Shader to RGB` → donne la couleur visible
2. Peut être utilisé avec `Color Ramp`, `Hue/Saturation`, etc.
3. **Pas disponible dans Cycles** (physiquement incorrect)

## Light Paths Nodes

Noeuds basés sur Light Paths pour des effets avancés :

- **Is Camera Ray** — visible à la caméra seulement
- **Is Shadow Ray** — shadows only
- **Is Diffuse/Glossy/Singular/Transmission Ray**
- **Ray Length** — longueur du rayon
- **Backfacing** — face arrière (utile pour la translucidité)

## Baking de Shaders

Processus pour convertir des shaders complexes en textures (jeux, export) :

1. Créer un matériau avec shader
2. UV unwrap (voir blender-texturing)
3. Render Properties > Bake
4. Type: Diffuse / Combined / Normal / Emission / Roughness / Etc.
5. Sélectionner le matériau cible → Bake

## Pitfalls

1. **Non-manifold geometry** cause des artefacts de shading — `Select > Select All By Trait > Non Manifold`
2. **Échelle non appliquée** — les textures procédurales ne s'alignent pas
3. **Normal map sur mauvais espace** — Tangent space uniquement sauf obj/global
4. **Mix Shader avec Alpha** — laisser le Weight à 1.0 sauf blending
5. **EEVEE Reflections** — plan probes nécessaires pour réflections hors écran
6. **Thin Film Interference** — utiliser `Layer Weight > Fresnel` + `Hue/Saturation` pour l'iridescence
7. **Cycles Fireflies** — Clamp indirect light (1-10), augment samples, caustics off
8. **Displacement vs Bump** — Displacement modifie la géométrie (nécessite subdiv), Bump est un faux relief

## Voir Aussi

- `blender-texturing` — Textures et UV maps pour les shaders
- `blender-lighting` — Éclairage pour mettre en valeur les matériaux
- `blender-compositing` — Post-processing des rendus