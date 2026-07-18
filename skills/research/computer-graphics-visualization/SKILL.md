---
name: computer-graphics-visualization
description: "Compétence en recherche en infographie et visualisation suivie sur arXiv sous cs.GR, cs.CV et domaines connexes. Couvre le rendu 3D, l'animation, la modélisation géométrique, la visualisation de données, la visualisation scientifique, l'infographie temps réel, le ray tracing, et les techniques de rendu neuronal."
category: research
---

# Compétence en Recherche — Infographie et Visualisation (cs.GR & cs.CV)

## Présentation

Cette compétence assure une veille scientifique sur l'**infographie** (computer graphics) et la **visualisation** via arXiv, principalement sous **cs.GR** (Graphics), ainsi que **cs.CV** (Computer Vision and Pattern Recognition) et **cs.HC** (Human-Computer Interaction). Elle couvre le rendu 3D, l'animation, la modélisation géométrique, la visualisation de données et les techniques neuronales de pointe.

---

## Rendu 3D et Synthèse d'Images

- **Rendu neuronal** — NeRF (Neural Radiance Fields), rendu neuronal volumétrique, Neural SDF, neural implicit surfaces
- **3D Gaussian Splatting** — Représentation par gaussiennes 3D pour le rendu temps réel, éclatement et fusion de primitives, optimisation differentiable
- **Ray tracing et Path tracing** — Lancé de rayons, Monte Carlo, importance sampling, multiple importance sampling, next event estimation, denoising
- **Rendu basé sur la physique (PBR)** — BRDF, BSDF, microfacet models, subsurface scattering, participating media
- **Rendu non-photoréaliste** — NPR, stylisation, rendu à la main levée, watercolor, cartoon shading
- **Ombres et éclairage global** — Shadow mapping, ambient occlusion, photon mapping, light probes, irradiance caching

---

## Animation et Simulation

- **Animation de personnages** — Skinning, blend shapes, animation procédurale, motion capture, retargeting, animation par apprentissage (deep motion)
- **Simulation physique** — Corps rigides, corps déformables, contraintes, collisions, résolution d'impulsions
- **Simulation de fluides** — Navier-Stokes, SPH (Smoothed Particle Hydrodynamics), FLIP, PIC, simulation de fumée et de liquides
- **Déformations** — Déformation élastique, plastique, hyperélastique, simulation de tissus et vêtements, FEM (Finite Element Method)
- **Simulation de cheveux et fourrure** — Modèles de cheveux, coiffage dynamique, frisottis, rendu de cheveux
- **Animation procédurale et bruit** — Bruit de Perlin, Worley, FBM, animation de foules, comportements de groupes

---

## Modélisation Géométrique

- **Maillages polygonaux** — Triangulation, remaillage, simplification (quadric error metrics), subdivision (Catmull-Clark, Loop, Butterfly)
- **Surfaces implicites** — Metaballs, blobby modeling, level sets, signed distance fields (SDF), Moving Least Squares
- **Reconstruction 3D** — From multi-view stereo, structured light, LiDAR, depth cameras, reconstruction neuronale (NeRF-based, Poisson reconstruction)
- **Géométrie différentielle appliquée** — Courbure, géodésiques, Laplace-Beltrami, discrete differential geometry
- **Modélisation procédurale** — Shape grammars, L-systems, génération de villes/terrains

---

## Visualisation de Données

- **Visualisation scientifique** — Visualisation de champs scalaires/vectoriels, isosurfaces, volume rendering, flow visualization, visualisation de maillages
- **Visualisation d'information** — Graph drawing, trees, networks, matrices, high-dimensional data, t-SNE, UMAP
- **Visualisation de ML** — Feature visualization, saliency maps, activation atlases, embedding visualization, model debugging visuel
- **Visualisation interactive** — D3.js, Vega-Lite, Observable, bokeh, Dash, Tableau, systèmes de visualisation temps réel
- **Analyse visuelle (Visual Analytics)** — Intégration d'analyse et visualisation, exploration interactive de données massives

---

## Rendu Temps Réel

- **Architectures de rendu temps réel** — Vulkan, DirectX 12, Metal, WebGPU, pipelines configurables
- **Shading et programmation GPU** — Vertex shaders, fragment shaders, compute shaders, mesh shaders, ray tracing hardware (RTX)
- **Techniques de rendu différé** — Deferred shading, forward+ rendering, clustered shading
- **Niveau de détail (LOD)** — Géométrie adaptative, tessellation, occlusion culling, frustum culling
- **Moteurs de jeu** — Unity, Unreal Engine, Godot, architecture de moteur, systèmes de rendu

---

## NeRF et Synthèse de Vues

- **ELSA3D** — Techniques récentes de rendu neuronal, ELSA (Efficient Learning of Surface Appearance)
- **Synthèse de vues** — View synthesis, plénoptique, light fields, image-based rendering, novel view synthesis
- **NeRF accéléré** — Instant NGP, PlenOctrees, KiloNeRF, FastNeRF, TensoRF, tri-planes
- **NeRF dynamique** — NeRF avec scènes animées, vidéo NeRF, déformation temporelle, D-NeRF
- **NeRF pour applications** — NeRF en robotique, cartographie, réalité virtuelle, production cinématographique

---

## Catégories arXiv surveillées

| Catégorie | Description |
|-----------|-------------|
| **cs.GR** | Computer Graphics |
| **cs.CV** | Computer Vision and Pattern Recognition |
| **cs.HC** | Human-Computer Interaction |
| **cs.LG** | Machine Learning |
| **cs.MM** | Multimedia |

---

## Articles notables et tendances

- **3D Gaussian Splatting for Real-Time Radiance Field Rendering** (Kerbl et al.) — Rendu neuronal temps réel par gaussiennes 3D
- **NeRF: Representing Scenes as Neural Radiance Fields** (Mildenhall et al.) — Article fondateur du rendu neuronal
- **Instant Neural Graphics Primitives** (Müller et al.) — Accélération massive du rendu neuronal avec des hash grids
- **ELSA3D** — Rendu neuronal avec apprentissage efficace de l'apparence de surface
- **DreamFusion / Text-to-3D** — Génération 3D à partir de texte avec guidance de diffusion

---

## Requêtes arXiv recommandées

```bash
# Infographie générale
# cat:cs.GR

# Rendu neuronal
# cat:cs.GR AND (NeRF OR neural rendering OR gaussian splatting)

# Visualisation
# cat:cs.GR AND (visualization OR visual analytics)

# Animation et simulation
# cat:cs.GR AND (animation OR simulation OR physics)
```
