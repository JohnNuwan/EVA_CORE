---
title: ARKit — Développement AR Apple (iOS/iPadOS)
description: Guide complet de développement en Réalité Augmentée avec ARKit 6+ — suivi 6DoF, géométrie du monde, occlusion, LiDAR, Scene Understanding, raycasting, Collaboration.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# ARKit — Développement AR Apple

## Architecture Fondamentale

### Session AR (ARSession)
- **Configuration ARWorldTrackingConfiguration** : tracking 6DoF complet, cartographie du monde, détection de plans, estimation lumineuse
- **ARBodyTrackingConfiguration** : tracking du corps humain (A12+)
- **ARGeoTrackingConfiguration** : ancrage géospatial (A12+, régions supportées)
- **ARFaceTrackingConfiguration** : tracking facial (TrueDepth/A12+)
- **ARImageTrackingConfig** : tracking d'images 2D sans cartographie du monde
- **ARObjectScanningConfiguration** : scan et détection d'objets 3D

### Frame Pipeline
```
ARSession → ARFrame → capturedImage (camera) + sceneDepth (LiDAR) + 
  rawFeaturePoints + anchors + lightEstimate → ARSCNView/ARView render
```

### Types d'Ancres (ARAnchor)
| Ancre | Usage | Source |
|-------|-------|--------|
| ARPlaneAnchor | Plans horizontaux/verticaux | Détection automatique |
| ARImageAnchor | Images de référence | Tracking images 2D |
| ARObjectAnchor | Objets scannés | Détection objets 3D |
| ARFaceAnchor | Géométrie faciale 64 blend shapes | TrueDepth |
| ARBodyAnchor | Squelette 19 joints | Body tracking |
| AREnvironmentProbeAnchor | Environnement HD pour réflexions | Light estimation |
| ARGeoAnchor | Position géographique | GeoTracking |
| ARMeshAnchor | Mesh du monde (LiDAR) | Scene Reconstruction |

## ARKit 6+ Fonctionnalités Clés

### Scene Reconstruction (LiDAR — A12 Pro/M1+)
```swift
let config = ARWorldTrackingConfiguration()
config.sceneReconstruction = .meshWithClassification
config.planeDetection = [.horizontal, .vertical]
session.run(config)
// ARMeshAnchor → classifications: .floor, .ceiling, .wall, .door, .seat, .table, .window, .none
```

### Occulsion Basée sur la Profondeur
```swift
// People occlusion (A12+)
config.frameSemantics.insert(.personSegmentationWithDepth)

// LiDAR depth occlusion (A14 Pro/M1+)
config.frameSemantics.insert(.sceneDepth)
```

### Collaboration
```swift
config.isCollaborationEnabled = true
// Transmettre: session.currentFrame?.collaborationData → data → peer
// Recevoir: session(_:didAdd:) avec ARCollaborationData
```

### Raycasting
```swift
// ARRaycastQuery (remplace hitTest déprécié)
let query = arView.raycastQuery(from: screenPoint, 
                                 allowing: .estimatedPlane, 
                                alignment: .horizontal)
let results = session.raycast(query)
// .existingPlaneGeometry, .existingPlaneInfinite, .estimatedPlane
```

## RealityKit vs SceneKit

| Critère | RealityKit | SceneKit |
|---------|-----------|----------|
| Entité | Entity + ModelEntity | SCNNode + SCNNodeRenderer |
| Animation | Transform + PhysicsMotion | CAAnimation + SCNAction |
| Physique | PhysicsBody + CollisionComponent | SCNPhysicsBody |
| Occlusion | OcclusionMaterial | SCNFloor + shadow |
| Audio | AmbientAudioChannel | SCNAudioSource |
| Shaders | MaterialX / Metal | SCNProgram / Metal |
| Networking | MultipeerConnectivity | Synchronization |
| Platforme | iOS 13+ | iOS 11+ (déprécié ARKit) |

### RealityKit — Entités et Composants
```swift
let model = try! ModelEntity.load(named: "robot")
model.generateCollisionShapes(recursive: true)
model.components.set(InputTargetComponent())
model.components.set(CollisionComponent(shapes: [.generateSphere(radius: 0.5)]))

let anchor = AnchorEntity(plane: .horizontal, classification: .floor)
anchor.addChild(model)
arView.scene.addAnchor(anchor)

// Physique
model.physicsBody = PhysicsBodyComponent(mass: 1.0, 
    material: .generate(friction: 0.8, restitution: 0.2),
    mode: .dynamic)
model.physicsMotion = PhysicsMotionComponent(linearVelocity: [0, 2, 0])

// Animation
let animation = try! AnimationResource.generate(with: [
    Transform.identity,
    Transform(translation: [0, 1, 0])
].keyframes(duration: 1.0))
model.playAnimation(animation)
```

## Intégration Vision + ARKit

### Détection d'Objets avec Vision
```swift
func session(_ session: ARSession, didUpdate frame: ARFrame) {
    guard let pixelBuffer = frame.capturedImage else { return }
    
    let request = VNCoreMLRequest(model: model) { request, error in
        for observation in request.results as! [VNRecognizedObjectObservation] {
            // Transformer boîte pixel → coordonnées monde via frame.displayTransform
            let rect = observation.boundingBox
            let screenPoint = CGPoint(x: rect.midX, y: rect.midY)
            let query = arView.raycastQuery(from: screenPoint, 
                                           allowing: .existingPlaneInfinite, 
                                           alignment: .any)
            let results = session.raycast(query)
            if let hit = results.first {
                let anchor = AnchorEntity(world: hit.worldTransform)
                // Placer objet détecté dans le monde
            }
        }
    }
}
```

## Performance & Optimisation

### Budget GPU ARKit
- **Target 30 FPS** minimum → mesurer avec `ARFrame.timestamp`
- **Triangle budget** : < 100k tris pour scène AR
- **Draw calls** : < 50 (batch par entité RealityKit)
- **Textures** : ASTC 4×4 compressées, max 2048×2048
- **LiDAR mesh** : simplifier avec `ARMeshGeometry` → low poly

### Memory Management
```swift
// Libérer ancres distantes
session.remove(anchor: oldAnchor)

// Réinitialiser avec persistance
session.run(config, options: [.removeExistingAnchors, .resetTracking])

// WorldMap pour persistance
session.getCurrentWorldMap { worldMap, error in
    // save worldMap to file
}
```

## Débogage

```swift
arView.debugOptions = [.showStatistics, .showWorldOrigin, .showAnchorGeometry]
// Métriques: draw count, polygon count, FPS, GPU utilization
```

## Outils Apple

- **Reality Composer Pro** : conception 3D, animations, comportements
- **Reality Converter** : USDZ pipeline (glTF, OBJ, FBX → USDZ)
- **ARKit Debugger (Xcode)** : visualisation ancres, profondeur, features points
- **Metal Debugger** : analyse GPU, overdraw, shader execution
- **Instruments** : Core Animation, Metal System Trace, ARKit Trace

## Pitfalls

- ARKit nécessite **A9+ et iOS 11+** (LiDAR: A12 Pro / M1+ uniquement)
- Les mesh LiDAR sont denses → simplifier avant usage physique
- `ARWorldMap` limitée à ~200 anchors
- `Collaboration` nécessite BlueTooth LE ou WiFi direct
- GeoTracking indisponible dans ~30% du globe
- Toujours gérer `ARSessionError` et `ARErorr` avec fallback
