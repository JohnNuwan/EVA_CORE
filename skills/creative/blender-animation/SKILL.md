---
name: blender-animation
description: "Animation dans Blender — keyframes, Graph Editor, Dope Sheet, NLA, Action Editor, pose-to-pose, animation procédurale, physics simulation, constraints-driven, timing et spacing."
version: 1.0.0
category: creative
tags:
  - blender
  - animation
  - keyframes
  - graph-editor
  - nla
  - action-editor
  - f-curves
  - interpolation
  - 3d
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Pas de plugins supplémentaires requis."
metadata:
  hermes:
    tags:
      - blender
      - animation
      - keyframes
      - graph-editor
      - nla
      - action-editor
      - f-curves
      - interpolation
    related_skills:
      - blender-rigging
      - blender-modeling
      - blender-scripting-python
    category: creative
---

# Blender — Animation

Guide complet de l'animation 3D dans Blender : keyframes, Graph Editor,
NLA, Action Editor, courbes, timing, spacing, animation physique et
procédurale.

## Concepts Fondamentaux

### Keyframes

- **Insert Keyframe** — `I` (Location/Rotation/Scale ou Custom)
- **Remove Keyframe** — `Alt+I`
- **Clear Keyframes** — `Alt+R` (rotation), `Alt+G` (location), `Alt+S` (scale)
- **Auto Keying** — bouton clé rouge dans le timeline header
- **Keying Set** — `Ctrl+I` (prédéfini pour quelles propriétés)

### Timeline

| Touche | Action |
|--------|--------|
| `Space` | Play / Pause |
| `←` / `→` | Frame précédente/suivante |
| `↑` / `↓` | Aller au début/fin |
| `Shift+←→` | Saut de 10 frames |
| `T` | Effacer les keyframes sélectionnées |
| `Ctrl+Shift+T` | Toggle Timeline |

### Dope Sheet

Vue d'ensemble de tous les keyframes :

- **Summary** — résumé par objet
- **Channel** — liste des canaux (location, rotation, scale, shape keys)
- **Grease Pencil** — frames de dessin
- **Action Editor** — éditer les actions individuelles
- **Ghost Curves** — aperçu des courbes adjacentes

## Graph Editor

Contrôle précis des interpolations.

### Modes d'Interpolation

| Mode | Raccourci | Description |
|------|-----------|-------------|
| **Bezier** | `V > Automatic/Vectors` | Smooth par défaut |
| **Linear** | `T > Linear` | Changement constant |
| **Constant** | `T > Constant` | Saut instantané |
| **Bézier Vector** | `V > Vector` | Tangentes automatiques |
| **Ease In/Out** | `Ctrl+E` | Départ/arrivée progressif |
| **Bounce** | `Shift+Ctrl+E` | Rebond (élasticité) |
| **Elastic** | `Shift+Ctrl+E` | Oscillation amortie |
| **Back** | `Shift+Ctrl+E` | Dépassement (overshoot) |
| **Exponential** | `Shift+Ctrl+E` | Accélération exponentielle |

### Modifiers F-Curve

- **Generator** — fonction mathématique (sinus, etc.)
- **Envelope** — contrôler les min/max
- **Cycles** — répétition (pour boucles)
- **Noise** — bruit procédural (tremblements)
- **Limit** — clamp valeurs
- **Stepped** — animation par paliers

### Keyframe Handles

- `V` — Handle type menu
- `Ctrl+H` — Make handles free
- `Ctrl+Alt+H` — Make handles auto
- `Shift+E` — Ease (adoucir)

## 12 Principes de l'Animation

| # | Principe | Application Blender |
|---|----------|-------------------|
| 1 | **Squash & Stretch** | Scale + volume preserve |
| 2 | **Anticipation** | Petite rotation inverse avant action |
| 3 | **Staging** | Pose claire au bon moment |
| 4 | **Straight Ahead / Pose to Pose** | Pose-to-pose pour le contrôle |
| 5 | **Follow Through & Overlap** | Secondary actions décalées |
| 6 | **Ease In / Ease Out** | Tangentes smooth in/out |
| 7 | **Arcs** | Trajectoires courbes (Graph Editor) |
| 8 | **Secondary Action** | Vêtements, cheveux, accessoires |
| 9 | **Timing** | Espacement des keyframes |
| 10 | **Exaggeration** | Amplifier les poses |
| 11 | **Solid Drawing** | Silhouette lisible |
| 12 | **Appeal** | Personnalité, caractère |

## NLA (Non-Linear Animation)

Permet de combiner et mixer des actions.

**Workflow NLA :**

1. **Créer une action** en animant
2. **Push Down Action** (bouton dans Action Editor)
3. L'action devient un strip NLA
4. **Dupliquer, décaler, répéter** les strips
5. **Blend** — Combine, Add, Subtract

### NLA Features

| Feature | Usage |
|---------|-------|
| **Strip Extrapolation** | Hold / Nothing / Repeat |
| **Blend Mode** | Combine / Add / Subtract / Multiply |
| **Auto Blend** | Transition automatique avec overlap |
| **Strip Time** | Scale (vitesse), offset |
| **Strip Meta** | Grouper plusieurs strips |
| **Action Clip** | Action individuelle |
| **Transition** | Crossfade entre strips |

## Animation par Contraintes

Combiner constraints + animation pour des effets complexes :

- **Child Of** — parent switcher (objet tenu, relâché)
- **Copy Location/Rotation** — follow un autre objet
- **Floor** — empêcher de traverser
- **Stretch To** — ressort, élastique
- **Follow Path** — objet suivant une courbe
- **Action Constraint** — pilote une action par la valeur d'un bone

## Animation Procédurale

Utiliser des modificateurs et drivers :

- **Sine driver** : `sin(frame * 2 * pi / period)`
- **Build modifier** — apparition progressive
- **Wave modifier** — ondulation
- **Simple Deform (Bend)** — torsion animée
- **Shape Key drivers** — expression faciale pilotée par bones
- **Geometry Nodes + animation** — systèmes de particules
- **Noise F-Curve modifier** — vibration aléatoire

## Physics Simulation

| Simulation | Ajout | Usage |
|------------|-------|-------|
| **Rigid Body** | `Object > Rigid Body` | Chutes, collisions |
| **Cloth** | `Object > Cloth` | Tissus, draps |
| **Soft Body** | `Object > Soft Body` | Gélatine, chair |
| **Fluid** | `Quick Liquid` | Eau, fumée |
| **Dynamics (Particles)** | Particle System | Foule, cheveux |
| **Force Fields** | `Shift+A > Force Field` | Vent, turbulence |

**Baking :** `Object > Rigid Body > Bake to Keyframes` — transforme
la simulation en keyframes modifiables.

## Animation Grease Pencil

2D frame-by-frame dans Blender :

1. `Draw Mode` — dessiner frame par frame
2. `Edit Mode` — ajuster les strokes
3. `Onion Skinning` — voir frames précédentes/suivantes
4. `Interpolate` — interpolation de strokes

## Raccourcis Animation

| Touche | Action |
|--------|--------|
| `I` | Insert keyframe |
| `Alt+I` | Remove keyframe |
| `T` | Interpolation type |
| `V` | Handle type |
| `Shift+E` | Ease (adoucir) |
| `Ctrl+C / Ctrl+V` | Copy/paste keyframes |
| `Shift+D` | Duplicate keyframes |
| `M` | Mirror keyframes |
| `[` / `]` | Set preview range |
| `Alt+O` | Clear all keyframes |
| `Ctrl+Shift+C` | Copy vector |
| `Ctrl+Shift+V` | Paste vector |
| `J` | Auto keyframe (toggle) |

## Scripts Animation

```python
# Définir un keyframe sur tous les objets sélectionnés
import bpy
frame = bpy.context.scene.frame_current
for obj in bpy.context.selected_objects:
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)
```

```python
# Appliquer Noise modifier à toutes les F-Curves
for fc in bpy.context.object.animation_data.action.fcurves:
    mod = fc.modifiers.new('NOISE')
    mod.strength = 0.2
    mod.scale = 10
```

```python
# Bake une simulation rigide en keyframes
import bpy
for obj in bpy.data.objects:
    if obj.rigid_body:
        bpy.context.view_layer.objects.active = obj
        bpy.ops.rigidbody.bake_to_keyframes(frame_start=1, frame_end=250)
```

## Pitfalls

1. **Keyframes oubliés** — propriété non keyée cause des sauts
2. **Mauvaises tangentes** — overshoot indésirable aux poses extrêmes
3. **Actions non poussées NLA** — les changements écrasent l'action originale
4. **Scale keying** — le scale non uniforme casse les contraintes
5. **Armature en Object Mode animé** — toujours animer en Pose Mode
6. **Physics non baked** — à chaque ouverture du .blend la simulation change
7. **Auto Keying accidentel** — désactiver le bouton clé rouge
8. **F-Curve modifiers cumulés** — ordre d'évaluation différent du résultat attendu

## Voir Aussi

- `blender-rigging` — Créer les rigs pour l'animation
- `blender-modeling` — Shape keys pour expressions faciales
- `blender-scripting-python` — Automation d'animation