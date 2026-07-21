---
title: Unity XR — Développement XR Multiplateforme Unity
description: Guide complet de développement VR/AR/MR avec Unity — AR Foundation, XR Interaction Toolkit, Universal Render Pipeline (URP/XR), OpenXR, Meta XR, Pico XR, rendu stéréo, locomotion, interaction, optimisation.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# Unity XR — Développement XR Multiplateforme Unity

## Architecture Unity XR

### Pipeline de Rendu XR
```
Unity XR Pipeline:
Monoscopic Render → [XRSDK] → [Graphics API] → [HMD Display]

Deferred Render: Forward+ / Forward → Single Pass Instanced
```

### Prérequis Unity
- **Unity 2022.3+ LTS** (recommandé)
- **Package Manager** : OpenXR Plugin, AR Foundation, XR Interaction Toolkit
- **Renderer** : URP 14+ (Forward) ou Built-in
- **API Graphique** : Vulkan (Android) / Metal (iOS) / DX12 (Windows)
- **Editor** : Game View → Simulator XR (Meta Quest, Pico, iOS)

## Configuration Projet

### Project Settings Clés
| Setting | Valeur | Raison |
|---------|--------|--------|
| Color Space | Linear | Précision lumière, pas de gamma |
| MSAA | 4x | Anti-aliasing VR (coûteux) |
| HDR | Off (VR) | Overhead inutile en HMD |
| Shadow Resolution | 512–1024 | Budget VR limité |
| Shadow Distance | 20m max | Inutile au-delà |
| VR Single Pass Instanced | ✅ | 2x perf vs Multi Pass |
| Foveated Rendering | Variable (Meta: 2/3/4) | Réduction charge GPU |
| Texture Quality | Half Res | 2K × 2K suffit casque 4K |
| Anisotropic | 1x | Éviter oversampling |

### XR Interaction Toolkit Setup
```
[XR Origin]
├── Camera Offset (Camera)
│   ├── Main Camera → Tag: MainCamera
│   └── [Locomotion System]
├── [Left Controller] → XR Controller (Action-based)
└── [Right Controller] → XR Controller (Action-based)

[Interaction Manager]
[XR Ray Interactor] (UI / distant grab)
[XR Direct Interactor] (proximité)
[XR Socket Interactor] (points d'attache)
[Teleportation Provider] + [Teleportation Area]
[Continuous Move Provider] (joystick locomotion)
```

### OpenXR Plugin
```xml
<!-- Packages/manifest.json -->
{
  "dependencies": {
    "com.unity.xr.openxr": "1.10.0",
    "com.unity.xr.arfoundation": "5.1.0",
    "com.unity.xr.interaction.toolkit": "2.5.0",
    "com.unity.render-pipelines.universal": "14.0.0"
  }
}
```

## AR Foundation (ARKit + ARCore)

```csharp
using UnityEngine.XR.ARFoundation;
using UnityEngine.XR.ARSubsystems;

public class ARManager : MonoBehaviour {
    public ARSession session;
    public ARPlaneManager planeManager;
    public ARRaycastManager raycastManager;
    public ARAnchorManager anchorManager;
    public ARMeshManager meshManager;
    
    void Start() {
        // Plan detection
        planeManager.planesChanged += OnPlanesChanged;
        
        // Mesh (LiDAR)
        meshManager.meshesChanged += OnMeshesChanged;
    }
    
    void Update() {
        // Raycast centre écran
        var hits = new List<ARRaycastHit>();
        if (raycastManager.Raycast(new Vector2(0.5f, 0.5f), hits, TrackableType.PlaneWithinBounds)) {
            var hitPose = hits[0].pose;
            var anchor = anchorManager.AddAnchor(hitPose);
            // Instancier objet à anchor
        }
    }
    
    void OnMeshesChanged(ARMeshesChangedEventArgs args) {
        foreach (var mesh in args.added) {
            // mesh.meshFilter.sharedMesh → mesh du monde
            // mesh.classification: Wall, Floor, Ceiling, Table, etc.
        }
    }
}
```

## Locomotion VR

### Types de Locomotion
```csharp
// Teleportation
public class TeleportHandler : MonoBehaviour {
    public XRRayInteractor rayInteractor;
    public TeleportationProvider provider;
    
    void OnSelectEnter(SelectEnterEventArgs args) {
        if (rayInteractor.TryGetCurrent3DRaycastHit(out var hit)) {
            provider.QueueTeleportRequest(new TeleportRequest() {
                destinationPosition = hit.point,
                destinationRotation = Quaternion.identity,
                matchOrientation = MatchOrientation.TargetUp
            });
        }
    }
}

// Continuous Movement (joystick)
public class ContinuousMove : MonoBehaviour {
    public CharacterController cc;
    public XRController controller;
    public float speed = 1.5f;
    
    void Update() {
        var input = controller.selectAction.ReadValue<Vector2>();
        var move = new Vector3(input.x, 0, input.y);
        move = transform.TransformDirection(move);
        cc.Move(move * speed * Time.deltaTime);
    }
}

// Snap Turn / Continuous Turn
// XR Continuous Turn Provider (composant sur XR Origin)
// Input: controller.rotateAnchor.action
```

## Interactions

### Grab (Prise)
```csharp
[RequireComponent(typeof(XRGrabInteractable))]
public class GravityController : MonoBehaviour {
    private XRGrabInteractable grabInteractable;
    private Rigidbody rb;
    
    void Start() {
        grabInteractable = GetComponent<XRGrabInteractable>();
        rb = GetComponent<Rigidbody>();
        
        grabInteractable.selectEntered.AddListener(OnGrab);
        grabInteractable.selectExited.AddListener(OnRelease);
    }
    
    void OnGrab(SelectEnterEventArgs args) {
        rb.useGravity = false;
        rb.isKinematic = true;
    }
    
    void OnRelease(SelectExitEventArgs args) {
        rb.isKinematic = false;
        rb.useGravity = true;
        // Transfer momentum
        var interactor = args.interactorObject;
        rb.linearVelocity = interactor.GetAttachTransform(this).forward * velocity;
    }
}
```

### Haptique
```csharp
using UnityEngine.XR.Interaction.Toolkit.Inputs;

XRController controller;
InputDevice device = InputDevices.GetDeviceAtXRNode(XRNode.RightHand);
HapticCapabilities capabilities;
if (device.TryGetHapticCapabilities(out capabilities) && capabilities.supportsImpulse) {
    device.SendHapticImpulse(0u, amplitude, duration);
}
```

## Optimisation XR

### Profiling Targets
| Métrique | Quest 2 | Quest 3 | Pico 4 | Apple VP |
|----------|---------|---------|--------|----------|
| FPS cible | 72/90 | 72/90/120 | 72/90 | 90 |
| Triangles max | 150k | 300k | 200k | 500k |
| Draw calls | < 150 | < 250 | < 200 | < 300 |
| VRAM | 6 GB | 8 GB | 8 GB | 16 GB |
| Resolution scale | 1.0–1.4 | 1.0–1.7 | 1.0–1.5 | N/A |

### Single Pass Instanced (Critique VR)
```csharp
// Player Settings → XR Settings → Stereo Rendering Mode
// ⚡ Single Pass Instanced (obligatoire pour VR)
// Multi Pass = 2x les draw calls ! → BANNIR
```

### Oculus Performance Kit
```csharp
using Meta.XR.Performance;

// Fixed Foveated Rendering
OVRManager.foveatedRenderingLevel = OVRManager.FoveatedRenderingLevel.High;
OVRManager.foveatedRenderingDynamic = true;  // Auto basé charge GPU

// Dynamic Resolution
OVRManager.enableDynamicResolution = true;

// Application SpaceWarp (ASW 2.0) — interpolation de frames
OVRManager.enableSpaceWarp = true;
```

### LOD et Frustum
- **LOD Group** : LOD0 (close), LOD1 (medium), LOD2 (far), Culled
- **Occlusion Culling** : `Window → Rendering → Occlusion Culling`
- **Static Batching** : marquer meshes statiques
- **GPU Skinning** : SkinnedMeshRenderer → GPU (Shader Model 5.0)
- **Texture Atlas** : regrouper textures (éviter multiples draw calls)

## Post-Processing VR

### URP Volume Overrides
- **Bloom** : léger (éviter blanchement HMD)
- **Vignette** : réduit motion sickness
- **Tonemapping** : ACES (standard cinéma HMD)
- **Chromatic Aberration** : désactivé (cause malaise VR)
- **Depth of Field** : désactivé (oculaire fixé)

## Meta XR SDK (Quest Spécifique)

```csharp
// Passthrough MR
using Meta.XR.MRUtilityKit;

// Initialiser Passthrough
var passthrough = gameObject.AddComponent<OVRPassthroughLayer>();
passthrough.textureOpacity = 0.7f;
passthrough.edgeRenderingEnabled = true;

// Room setup (Scene API)
var room = MRUK.Instance.GetCurrentRoom();
var walls = room.GetBounds(MRUKAnchor.SceneLabels.WALL);
var floor = room.GetBounds(MRUKAnchor.SceneLabels.FLOOR);

// Hand Tracking (pas controller)
var hand = OVRPlugin.GetTrackingState();
// Skeleton 21 joints par main
```

## Pitfalls

- **Multi Pass Stereo = mort GPU VR** → toujours Single Pass Instanced
- **Pas de transparent shaders en VR** → utiliser unlit/URP Lit
- **UI Canvas en VR** → mettre en mode `World Space`, scale fixe
- **Ne pas instancier/détruire pendant frame** → Object Pooling obligatoire
- **Baking lightmaps** → éviter GI en temps réel
- **VR et Post-stack** → alléger (pas de DoF, Motion Blur)
- **Quest** : attention au throttling thermique (test 30min+)
- **AR Foundation** : `ARSession` ne fonctionne pas dans Editor sans appareil
- **XR Interaction Toolkit** : callbacks lents dans `Update` → utiliser événements
