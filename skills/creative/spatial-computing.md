---
title: Spatial Computing — Informatique Spatiale & Apple Vision Pro
description: Guide complet de l'informatique spatiale — Apple Vision Pro / visionOS, Meta Quest MR, spatial UI/UX, Room Understanding, Scene Geometry, Window-Based Interfaces, Reality Composer Pro.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# Spatial Computing — Informatique Spatiale

## Concepts Fondamentaux

### Définition
L'informatique spatiale (Spatial Computing) est la fusion de l'informatique traditionnelle avec l'environnement physique de l'utilisateur. Contrairement à la VR (monde fermé) ou l'AR (superposition 2D), le Spatial Computing ancre numériquement des **interfaces, objets et agents** dans l'espace 3D réel avec une conscience complète de la géométrie des lieux.

### Piliers du Spatial Computing
1. **Scène Sensing** : cartographie en temps réel du monde (LiDAR, depth, mesh)
2. **Spatial UI** : fenêtres, menus et interfaces ancrées dans l'espace
3. **Spatial Audio** : audio directionnel basé sur HRTF et géométrie
4. **Presence** : cohérence visuelle, occlusions, éclairage réel
5. **Interaction Naturelle** : yeux, mains, voix — pas de contrôleur
6. **Multitasking Spatial** : plusieurs fenêtres / apps flottantes simultanées

### Plateformes Majeures

| Plateforme | OS | SDK | Rendu | Tracking |
|------------|----|-----|-------|----------|
| **Apple Vision Pro** | visionOS 2.x | RealityKit 4 + ARKit | Metal/RealityKit | Eye + Hand + Room |
| **Meta Quest 3/Pro** | Android (Horizon OS) | Meta XR SDK + OpenXR | Vulkan/OpenXR | Hand + Controller + Room |
| **Magic Leap 2** | Android | Lumin SDK + OpenXR | Vulkan/WebGPU | Eye + Hand + Mesh |
| **Pico 4 Ultra** | Android | Pico XR SDK + OpenXR | Vulkan/OpenXR | Hand + Controller |

## Apple visionOS / Vision Pro

### Architecture visionOS
```
SwiftUI / RealityKit / ARKit
       ↕
Compositor Services (rendu stereo)
       ↕
Metal / DisplayLink (90-100 Hz)
       ↕
R1 + M2 Coprocesseurs
```

### Fenêtres Spatiales (Windows)
```swift
// SwiftUI — Fenêtre standard immersive
struct SpatialWindow: View {
    @Environment(\.openWindow) var openWindow
    @Environment(\.dismissWindow) var dismissWindow
    
    var body: some View {
        VStack {
            Text("Bonjour, Spatial Computing")
                .font(.extraLargeTitle)
            Button("Ouvrir monde immersif") {
                openWindow(id: "immersive")
            }
        }
        .frame(width: 600, height: 400)
        .glassBackgroundEffect()
    }
}
```

### Ornaments (Accessoires de Fenêtre)
```swift
Window(id: "main") {
    ContentView()
        .ornament(attachmentAnchor: .scene(.topTrailing)) {
            Button("✕", action: dismissWindow)
                .buttonStyle(.borderless)
        }
}
```

### Volumes 3D (Objets Ancrés)
```swift
struct ModelVolume: View {
    var body: some View {
        RealityView { content in
            // Charger USDZ
            if let entity = try? await Entity(named: "robot") {
                entity.components.set(InputTargetComponent())
                entity.generateCollisionShapes(recursive: true)
                content.add(entity)
            }
        } update: { content in
            // Mise à jour par frame
        }
        .gesture(TapGesture().targetedToAnyEntity().onEnded { value in
            // Interaction tap sur objet 3D
        })
        // Taille physique du volume
        .frame(depth: 0.5, alignment: .center)
    }
}
```

### Immersive Spaces
```swift
// Types d'immersion
// .mixed : monde réel visible + objets virtuels
// .progressive : fond graduellement remplacé
// .full : monde entièrement virtuel

@main
struct SpatialApp: App {
    @State private var immersion = ImmersionStyle.mixed
    
    var body: some SwiftUI.Scene {
        WindowGroup {
            ContentView()
        }
        .windowStyle(.volumetric)
        
        ImmersiveSpace(id: "experience") {
            ImmersiveView()
        }
        .immersionStyle(selection: $immersion, in: .mixed, .progressive, .full)
    }
}
```

### Room Tracking & Scene Understanding
```swift
import ARKit
import RealityKit

class RoomScanner {
    let arSession = ARSession()
    var worldAnchoring: WorldTrackingProvider!
    
    func start() async {
        // Scene Reconstruction
        let sceneProvider = SceneReconstructionProvider()
        let handTracking = HandTrackingProvider()
        let worldTracking = WorldTrackingProvider()
        let planeDetection = PlaneDetectionProvider(alignments: [.horizontal, .vertical])
        
        // Lancer run
        try? await arSession.run([sceneProvider, handTracking, worldTracking, planeDetection])
        
        // Itérer sur les ancres de scène
        for await update in sceneProvider.anchorUpdates {
            switch update.event {
            case .added, .updated:
                let mesh = update.anchor.meshGeometry
                let classification = update.anchor.classification
                // .wall, .floor, .ceiling, .table, .seat, .window, .door, .stairs, .bed
                
            case .removed:
                // Nettoyer
            }
        }
    }
}
```

### Eye Tracking (Oculométrie)
```swift
// Eye Tracking fourni par ARKit
let eyeProvider = WorldTrackingProvider()
let pose = eyeProvider.originFromDeviceTransform

// Pour interaction regard, utiliser SwiftUI par défaut:
// .onTapGesture, .onHover, .focusEffect — visionOS gère le eye gaze automatiquement
```

### Metal Compositor (Rendu Bas Niveau)
```csharp
// Metal Shader — compositing spatial
// Utiliser MTLDevice via compositorLayer
```

## Meta MR (Quest 3 / Pro)

### Spatial Anchor API (Meta XR SDK)
```csharp
using Meta.XR.MRUtilityKit;

// Sauvegarder ancres spatiales
OVRSpatialAnchor anchor = go.AddComponent<OVRSpatialAnchor>();
anchor.Save((result, uuid) => {
    PlayerPrefs.SetString("spatial_anchor", uuid.ToString());
});

// Charger ancres préexistantes
OVRSpatialAnchor.Load(new Guid(playerPrefsId), (anchors) => {
    foreach (var a in anchors) {
        // Restaurer objets liés
    }
});
```

### Scene Understanding (Meta Scene API)
```csharp
// Room setup
var room = MRUK.Instance.GetCurrentRoom();

// Layout des meubles
foreach (var anchor in room.GetAnchors()) {
    var label = anchor.GetSemanticClassification();
    switch (label) {
        case "TABLE":
            PlacerObjetSur(anchor.transform, anchor.PlaneBounds.Value);
            break;
        case "COUCH":
            // Interactions assises
            break;
        case "WALL_FACE":
            // Cadre photo mural
            break;
    }
}

// Virtual keyboard placement
MRUK.Instance.GetCurrentRoom().GenerateDrivableSurfaces();
```

## Spatial UI Design Principles

### Règles d'Or
| Règle | Description |
|-------|-------------|
| **Confort visuel** | Fenêtres entre 1.2m et 2m, angle vertical ±20° |
| **Pas de 2D plat** | UI intégrée dans le monde (ombres, profondeur, flou) |
| **Distance minimale** | 0.5m (objets), 0.7m (fenêtres) — éviter strabisme |
| **Scale fixe** | Pas de pinch-to-zoom spatial : objets taille réelle |
| **Snap to world** | Fenêtres s'alignent aux surfaces (murs, tables) |
| **Eyes-free** | Ne pas dépendre uniquement du regard pour actions critiques |
| **Spatial Audio** | Sons attachés aux objets dans l'espace (HRTF) |

### Confort de Champ Visuel
```
      [Périphérie]
   ┌─────────────┐  ─ 30° (limite confort)
   │   [Proche]   │
   │  ┌───────┐  │  ─ 15° (confort optimal)
   │  │ FOVEA │  │
   │  │  5°   │  │  ─ 0° (focus)
   │  └───────┘  │
   └─────────────┘
```

### Spatial Input Modalities
| Modalité | Vision Pro | Quest 3 | Latence |
|----------|------------|---------|---------|
| Eye gaze | ✅ Natif | OVR | ~10ms |
| Hand pinch | ✅ | ✅ | ~15ms |
| Hand gesture | ✅ | ✅ | ~20ms |
| Voice | ✅ Siri | ✅ Voice SDK | ~100ms |
| Controller | ❌ | ✅ Touch+ | ~5ms |

## Pitfalls

- **Eye tracking = batterie** : limiter polling à 30Hz max pour usage non critique
- **Fenêtres sans ancrage** : l'utilisateur perd ses fenêtres au redémarrage → toujours sauvegarder les poses
- **Taille de fenêtre fixe** : trop grande → inconfort cervical (mouvement tête excessif)
- **Éviter l'effet "portail"** : fenêtres sans ombre portée → casser l'immersion spatiale
- **Performance fenêtres multiples** : chaque fenêtre = rendu stéréo séparé → limiter à 4-5 max
- **Motion sickness** : éviter mouvements caméra brusques, privilégier téléportation
- **Accessibilité** : proposer alternatives à eye gaze (hand + voice)