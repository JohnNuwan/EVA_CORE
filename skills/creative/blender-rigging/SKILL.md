---
name: blender-rigging
description: "Rigging dans Blender — armatures, contraintes, skinning, weight painting, Inverse Kinematics, métarig (Rigify), facial rigging, stretchy bones, drivers, automation."
version: 1.0.0
category: creative
tags:
  - blender
  - rigging
  - armature
  - animation
  - ik
  - fk
  - weight-painting
  - rigify
  - skinning
  - character-rig
prerequisites:
  commands: ["blender"]
setup:
  help: "Blender installé. Rigify add-on recommandé (activé par défaut)."
metadata:
  hermes:
    tags:
      - blender
      - rigging
      - armature
      - animation
      - ik
      - fk
      - weight-painting
      - rigify
      - skinning
      - character-rig
    related_skills:
      - blender-modeling
      - blender-animation
      - blender-sculpting
    category: creative
---

# Blender — Rigging

Guide complet pour le rigging dans Blender : création d'armatures,
contraintes, skinning, weight painting, IK/FK, Rigify, facial rigging
et automation avec drivers.

## Concepts Fondamentaux

### Armature

- **Bones** — segments de l'armature (os)
- **Edit Mode** — placement et connexion des bones
- **Pose Mode** — animation des bones
- **Rest Pose** — position de référence (Apply as Rest Pose avec `Ctrl+A`)
- **Bone Roll** — rotation locale du bone (influence les déformations)
- **Head/Tail** — début/fin d'un bone
- **Parent** — chaîne hiérarchique (bone > bone)

### Bone Properties

| Propriété | Description |
|-----------|-------------|
| **Deform** | Le bone déforme le mesh |
| **Inherit Rotation** | Transmet la rotation du parent |
| **Local Location** | Position locale héritée |
| **Scale** | Échelle héritée |
| **Envelope** | Distance d'influence (envelope weight) |
| **Ease In/Out** | Transition de l'enveloppe |
| **Segment** | Subdivise le bone (pour courbes) |
| **Connected** | Bone connecté à la tête du parent |

## Workflow de Rigging

### Étape 1: Créer l'Armature

```
1. Shift+A > Armature > Single Bone
2. Edit Mode: E (extrude) pour chaîner
3. Noms: prefix L/R (Left/Right), suffix .001
4. Symmetry: X-Axis Mirror dans Armature Options
```

**Convention de Noms :**
```
spine, chest, neck, head
upper_arm.L / upper_arm.R
forearm.L / forearm.R
hand.L / hand.R
thigh.L / thigh.R
shin.L / shin.R
foot.L / foot.R
```

### Étape 2: Parent (Skinning)

- **Automatic Weights** — `Parent > Armature Deform > With Automatic Weights`
- **Envelope Weights** — basé sur la distance (enveloppes)
- **Empty Groups** — weights à peindre manuellement

### Étape 3: Weight Painting

Mode `Weight Paint` (sélectionner mesh, `Ctrl+Tab > Weight Paint`)

| Outil | Usage |
|-------|-------|
| **Draw** | Ajouter du poids (Add mode) |
| **Blur** | Adoucir les transitions |
| **Average** | Moyenne des poids adjacents |
| **Smear** | Étirer les poids |
| **Gradient** | Remplissage progressif |
| **Sample Weight** | Pipette de poids |

**Weight Paint Bonnes Pratiques :**
- Maximum 3-4 bones par vertex
- Smooth transitions aux joints
- Vérifier avec la pose (`Pose Mode > rotate bone`)
- **Auto Normalize** dans Tool Settings
- **Mirror** : activer `Tool > Options > Mirror` dans weight paint

## Contraintes Essentielles

| Contrainte | Usage |
|------------|-------|
| **Copy Location** | Copier position XYZ |
| **Copy Rotation** | Copier rotation |
| **Copy Scale** | Copier échelle |
| **Copy Transforms** | Copier tout (location+rotation+scale) |
| **Limit Location/Rotation/Scale** | Limiter les transformations |
| **Track To** | Viser un objet (ex: œil, tête) |
| **Locked Track** | Viser avec un axe verrouillé |
| **Stretch To** | Étirer vers une cible |
| **IK (Inverse Kinematics)** | IK solver |
| **Child Of** | Parent dynamique (switchable) |
| **Floor** | Plancher (empêche de traverser) |
| **Transform** | Transformer une valeur en une autre |
| **Action** | Piloter une action NLA |
| **Armature** | Contrainte de bone |
| **Damped Track** | Tracking fluide |

## IK vs FK

| Caractéristique | IK (Inverse Kinematics) | FK (Forward Kinematics) |
|-----------------|------------------------|------------------------|
| **Contrôle** | Main/pied bouge, le reste suit | Rotation parent → enfant |
| **Précision** | Atteindre une cible (ex: saisir) | Arc naturel, pendule |
| **Setup** | IK constraint + target | Simple (chaîne) |
| **Pose** | Flexible, parfois mécanique | Naturelle, organique |
| **Switch IK/FK** | Driver + action | — |

**IK Solver Settings :**
- **Chain Length** — nombre de bones affectés (0 = all)
- **Target** — objet empty contrôlant l'IK
- **Pole Target** — direction du coude/genou
- **Iterations** — précision (≥100)
- **Pole Angle** — rotation de la chaîne

## Rigify (Métarig)

1. `Shift+A > Armature > Human (Meta-Rig)`
2. **Edit Mode** — redimensionner/adapter à votre personnage
3. **Generate Rig** — `Armature > Generate Rig`
4. Rig complet avec IK/FK switch, stretch, finger roll, etc.

**Options Rigify :**
- **Advanced** — Layers, toggles, mécanisme
- **Face** — bones faciaux (jaw, eyes, brows)
- **Fingers** — FK/IK individuel ou par groupe
- **Custom shapes** — remplacer les os par des formes

## Facial Rigging

### Bones Minimum

- **Jaw** — mâchoire
- **Eyes** (L/R) — Left/Right (Target + Up)
- **Brows** (L/R) — Left/Right

### Shape Keys + Drivers

1. Créer des shape keys sur le mesh facial
2. Driver (`RMB > Add Driver` sur la valeur du shape key)
3. Piloter le driver avec un bone : `# frame` ou transformation de bone
4. **Variable** : single property (bone transform)

### Technique Corrective Blend Shapes

Les shape keys corrigent les déformations aux articulations (coude, genou,
aisselle). Piloter avec des drivers basés sur l'angle du bone.

## Stretchy Bones

Permet à un membre de s'étirer sans perdre la connexion :

1. **Armature** en rest pose
2. **Stretch To** constraint avec volume preserve
3. Mesurer la distance entre head/tail
4. **Map Range** : distance → scale

## Drivers

### Création

- `RMB > Add Driver` sur une propriété
- Open Graph Editor > Drivers workspace
- **Expression** : `var * 2 + sin(frame * 0.1)`
- **Variable** : `Transform Channel` (bone location/rotation/scale)

### Exemples

```python
# Rotation du coude → Shape key de correction
var = pose_bone("upper_arm").rotation_euler.z
var * 0.5 + 1
```

```python
# IK/FK switch (0 = FK, 1 = IK)
var > 0.5 and 1 or 0
```

## Automation (Scripts Python)

```python
# Ajouter un bone IK à la sélection
import bpy
arm = bpy.context.object.data
bpy.ops.object.mode_set(mode='EDIT') 
bone = arm.edit_bones.new('ik_target')
bone.head = (0, 0, 0)
bone.tail = (0, 0, 1)
```

```python
# Créer des contraintes IK pour chaque chaîne
bpy.ops.object.mode_set(mode='POSE')
pb = bpy.context.object.pose.bones.get('arm_ik')
pb.constraints.new('IK')
pb.constraints['IK'].target = bpy.data.objects.get('Target')
```

## Pitfalls

1. **Scale non appliquée** — l'armature ou le mesh casse le skinning
2. **Bones pas des deform bones** — les bones sans deform causent des déformations bizarres
3. **Weight painting incomplet** — vertices à 0 poids = posés à l'origine
4. **Bone roll mal aligné** — twist sur le mesh lors de l'animation
5. **IK sans pole target** — le coude/genou pointe aléatoirement
6. **Contraintes cycliques** — A dépend de B qui dépend de A → boucle
7. **Pose > Apply as Rest Pose** oublié — pose actuelle devient désordre
8. **Rigify non généré** — le métarig n'est pas fait pour être animé

## Voir Aussi

- `blender-animation` — Animer le rig créé
- `blender-modeling` — Modéliser un personnage prêt au rigging
- `blender-scripting-python` — Automation du rigging par code