---
title: Passthrough AR — Réalité Mixte à Flux Vidéo
description: Guide complet de la technologie Passthrough AR/MR — flux caméra couleur, stéréoscopie, occlusion, segmentation, environnement lighting, profondeur, composition GPU, Meta Passthrough, Vision Pro, WebXR AR.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# Passthrough AR — Réalité Mixte à Traversée Vidéo

## Principes Fondamentaux

### Qu'est-ce que le Passthrough ?
Technologie de **Video See-Through (VST)** où les caméras du casque capturent le monde réel et l'affichent sur les écrans internes, permettant la superposition d'objets virtuels. Contrairement à l'AR optique (Hololens, Magic Leap) qui utilise un guide d'onde transparent, le VST offre un **champ de vision complet** et une **occlusion parfaite** des objets virtuels.

### Latence Critique
```
Caméra capture → ISP → Warp → GPU Composition → Display = Cycle total
Target: < 12ms (perception humaine)
Fail: > 20ms → nausée, désorientation
```

### Casques VST Principaux
| Casque | Caméras | Résolution | FOV | Fréquence | Warp HW |
|--------|---------|------------|-----|-----------|---------|
| **Apple Vision Pro** | 2× RGB 18mm f/2.0 | 4K (×2) | ~100° | 90-100 Hz | M2 + R1 |
| **Meta Quest 3** | 2× RGB 4MP | 18 PPD | 110° H × 96° V | 72-90 Hz | XR2 Gen2 |
| **Meta Quest Pro** | 2× RGB 10MP | 22 PPD | 106° | 90 Hz | XR2+ Gen1 |
| **Varjo XR-4** | 2× RGB 20MP + LiDAR | 51 PPD (focus) | 120°×105° | 90 Hz | Custom FPGA |

## Pipeline de Passthrough

### Architecture de Composition
```
[Caméra Gauche] → [ISP] → [Rectification] → [Warp] ─┐
                                                      ├→ [Compositor Stereo] → [HMD Display]
[Caméra Droite] → [ISP] → [Rectification] → [Warp] ─┘
                                                      │
[GPU Rendering] → [Alpha Blending] → [Occlusion] ────┘
```

### Composants Clés
1. **Rectification** : correction distorsion optique + alignement stéréo
2. **Warp** : Time-Warp / Space-Warp pour compenser latence mouvement tête
3. **Compositing** : fusion caméra + rendu GPU (multilayer)
4. **Occlusion** : objets virtuels cachés par éléments réels (profondeur)
5. **Color matching** : balance blanc, exposition, gamma entre virtuel et réel

### Meta Passthrough MR (Quest 3 / Pro)

```csharp
using Meta.XR.MRUtilityKit;
using UnityEngine;

public class PassthroughMR : MonoBehaviour {
    private OVRPassthroughLayer passthrough;
    
    void Start() {
        passthrough = gameObject.AddComponent<OVRPassthroughLayer>();
        
        // Configuration
        passthrough.textureOpacity = 0.8f;     // Opacité du monde réel
        passthrough.edgeRenderingEnabled = true; // Contour coloré
        passthrough.edgeColor = Color.cyan;
        
        // Surface Projected Passthrough (projection sur mesh surface)
        passthrough.SetProjectedPassthroughEnabled(true);
        
        // Passthrough sur surface spécifique (table, mur)
        var tableSurface = roomAnchor.GetSurface();
        passthrough.AddSurfaceToProjectedPassthrough(OVRPassthroughLayer.SurfaceProjectionType.Rectangle);
    }
    
    void TogglePassthrough(bool enabled) {
        passthrough.enabled = enabled;
    }
}
```

### Occlusion Passthrough (Profondeur)
```csharp
// Occlusion basée sur depth map
public class DepthOcclusion : MonoBehaviour {
    private OVRManager ovrManager;
    
    void Start() {
        // Mode occlusion : objets VR masqués par environnement réel
        OVRManager.occlusionMesh = true;
        OVRManager.depthSubmission = true;
        
        // Shader occlusion : comparer depth rendu vs depth caméra
        GetComponent<Renderer>().material = occlusionMaterial;
    }
}
```

### Shader d'Occlusion
```glsl
// Unity shader — occlusion passthrough
Shader "Custom/DepthOcclusion" {
    SubShader {
        Pass {
            ZWrite On
            ZTest LEqual
            
            // Comparer depth fragment avec depth map caméra
            float4 frag(v2f i) : SV_Target {
                float camDepth = SampleCameraDepth(i.uv);
                float fragDepth = i.screenPos.z;
                
                // Si fragment est derrière l'objet réel → cacher
                clip(fragDepth - camDepth);
                
                return _Color;
            }
        }
    }
}
```

## Apple Vision Pro Passthrough

```swift
import RealityKit
import SwiftUI

struct MixedRealityView: View {
    @Environment(\.openImmersiveSpace) var openImmersive
    
    var body: some View {
        RealityView { content in
            // Le passthrough est natif dans visionOS
            // ImmersiveSpace en mode .mixed
            
            let entity = ModelEntity(mesh: .generateSphere(radius: 0.1))
            
            // Matériau qui interagit avec la lumière réelle
            var material = PhysicallyBasedMaterial()
            material.baseColor = .init(tint: .cyan)
            material.metallic = 0.8
            material.roughness = 0.2
            
            // Occlusion automatique (ARKit gère la profondeur)
            entity.components.set(TrackingComponent())
            
        } update: { content in
            // Mise à jour
        }
    }
}

// Passthrough programmatique
import ARKit

// Activer/désactiver passthrough
// Le passthrough est toujours actif en mode .mixed
// En .full immersion, background = noir complet
```

## WebXR Passthrough AR

```javascript
async function startPassthrough() {
    const session = await navigator.xr.requestSession('immersive-ar', {
        requiredFeatures: ['local', 'hit-test'],
        optionalFeatures: ['dom-overlay', 'light-estimation']
    });
    
    const canvas = document.getElementById('xr-canvas');
    const gl = canvas.getContext('webgl', { xrCompatible: true, alpha: true });
    
    // Le navigateur fournit automatiquement le fond caméra
    // On ne rend que les objets virtuels (alpha = vide → passthrough)
    
    gl.clearColor(0, 0, 0, 0); // Transparent pour passthrough
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
    
    // Occlusion : depth test
    gl.enable(gl.DEPTH_TEST);
}
```

## Qualité d'Image Passthrough

### Facteurs Déterminants
| Facteur | Impact | Solution |
|---------|--------|----------|
| **Distorsion optique** | Image déformée (barrel/pincushion) | Calibration par pixel |
| **Chromatic Aberration** | Franges couleur sur bords | Shader correction |
| **Exposition** | Surex/sous-ex basse lumière | Auto-exposition HDR |
| **White Balance** | Teinte non naturelle | AWB + calibration manuelle |
| **Motion Blur** | Tremblement caméra | Electronic stabilization |
| **Grain/Noise** | Bruit basse lumière | Temporal denoise (NeRF/ML) |
| **Latence** | Désynchronisation | Time Warp + Async Reprojection |
| **FOV mismatch** | Bordure noire | Multi-cam blending |

### Calibration Passthrough
```csharp
// Meta — réglages utilisateur
OVRPlugin.SetPassthroughColorMap(OVRPlugin.PassthroughColorMap {
    brightness: 0.0f,  // -1 à 1
    contrast: 1.0f,     // 0 à 2
    saturation: 1.0f,   // 0 à 2
    temperature: 0.0f   // -1 (froid) à 1 (chaud)
});
```

## Segmentation Sémantique du Passthrough

```python
# ML Segmentation du monde réel
import torch
import torchvision.transforms as T
from torchvision.models.segmentation import deeplabv3_resnet50

model = deeplabv3_resnet50(pretrained=True)
model.eval()

labels = {
    0: "background",    4: "wall",       5: "floor",
    6: "ceiling",       8: "table",      12: "chair",
    15: "person",       21: "electronic", 74: "book"
}

def segment_passthrough(frame_tensor):
    with torch.no_grad():
        output = model(frame_tensor)['out'][0]
        mask = output.argmax(0)
    
    # Masque pour occlusion sélective
    person_mask = (mask == 15).numpy()
    table_mask = (mask == 8).numpy()
    return person_mask, table_mask
```

### Utilisation en XR
```csharp
// Meta — Scene API segmentation
var roomLayout = MRUK.Instance.GetCurrentRoom();
foreach (var anchor in roomLayout.GetAnchors()) {
    var label = anchor.GetSemanticClassification();
    // "TABLE", "COUCH", "WALL", "FLOOR", "DOOR", "WINDOW", ...
    
    if (label == "TABLE") {
        // Rendre objet virtuel SUR la table
        PlacerObjetSur(anchor.transform);
    } else if (label == "WALL") {
        // Passthrough atténué pour cadre photo virtuel
    }
}
```

## Lighting & Environment

### Estimation de Lumière Réelle
```csharp
// Meta — Light Estimation
OVRLightEstimator lightEstimator;
var light = lightEstimator.GetLightEstimate();

// Direction & intensité de la lumière réelle
Vector3 lightDir = light.mainLightDirection;
float lux = light.averageBrightness; // Lux

// Appliquer à objets virtuels
foreach (var renderer in virtualObjects) {
    renderer.material.SetVector("_LightDir", lightDir);
    renderer.material.SetFloat("_LightIntensity", lux);
}
```

### Réflexions Environnementales (IBL)
```csharp
// Capturer HDRI du monde réel
var cubemap = new Cubemap(256, RGB24, false);
passthrough.CaptureEnvironmentCubemap(cubemap);
RenderSettings.customReflection = cubemap;
RenderSettings.reflectionIntensity = 0.5f;
```

## Performance Passthrough

### Budget GPU
| Opération | Coût | Optimisation |
|-----------|------|-------------|
| Camera capture + ISP | ~3ms | Hardware path (R1/XR2) |
| Warp + Compositing | ~2ms | Fixed function HW |
| Occlusion depth | ~1ms | Half-res depth buffer |
| Scene Understanding | ~5ms | Reduce update rate (10Hz) |
| Total Passthrough | ~6ms (HW) / ~12ms (SW) | Target < 4ms rest GPU |

### Optimisation Rendu Mixte
- **Réduire alphas** → peupler depth buffer pour occlusion
- **Single Pass Instanced** → pas de multi-camera séparée
- **VRAM** : passthrough textures = 4K × 2 × 4 bytes = ~64 MB
- **Foveated Passthrough** : périphérie basse résolution (Meta: niveau 3-4)
- **Limiter overlays** : chaque overlay OVR = layer GPU supplémentaire

## Pitfalls

- **Latence > 12ms** = nausée → toujours vérifier `OVRManager.passthroughLatencyMs`
- **Baseline caméra trop large** → perception profondeur déformée (hyper-stéréo)
- **Changement lumière** brusque → auto-exposure à bien calibrer
- **Occlusion imparfaite** → objets flottants, cassure d'immersion
- **Passthrough désactivé en mode économie** → planifier fallback VR
- **Bruit basse lumière** → utiliser denoise temporel, pas spatial (trop flou)
- **Texture caméra en alpha** → nécessite `ColorFormat.RGBA` (32-bit)
- **Vision Pro** : pas de contrôle API direct sur passthrough (Apple gère)