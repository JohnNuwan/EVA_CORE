---
title: WebXR — API de Réalité Étendue pour le Web
description: Guide complet de développement XR avec l'API WebXR Device — immersions VR/AR, WebXR Layers, hit-test, anchors, planes, mesh, JavaScript/Three.js/Babylon.js. Compatible navigateurs Chromium, WebKit, Firefox.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# WebXR — API de Réalité Étendue

## Architecture de l'API WebXR

### Pipeline d'Initialisation
```javascript
// 1. Détection support
if (navigator.xr) {
    const supported = await navigator.xr.isSessionSupported('immersive-vr');
    // 'immersive-vr' | 'immersive-ar' | 'inline'
}

// 2. Demande session
const session = await navigator.xr.requestSession('immersive-vr', {
    requiredFeatures: ['local', 'local-floor', 'bounded-floor', 'unbounded'],
    optionalFeatures: ['hand-tracking', 'layers', 'hit-test', 'anchors', 'plane-detection']
});

// 3. Canvas setup
const canvas = document.getElementById('xr-canvas');
const gl = canvas.getContext('webgl', { xrCompatible: true, alpha: false });

// 4. Espace de référence
const referenceSpace = await session.requestReferenceSpace('local-floor');
// 'viewer' | 'local' | 'local-floor' | 'bounded-floor' | 'unbounded'

// 5. Animation loop
function onXRFrame(time, frame) {
    const session = frame.session;
    const pose = frame.getViewerPose(referenceSpace);
    
    if (pose) {
        for (const view of pose.views) {
            // view.projectionMatrix, view.transform
            // Rendu stéréoscopique œil gauche/droit
        }
    }
    session.requestAnimationFrame(onXRFrame);
}
session.requestAnimationFrame(onXRFrame);
```

## Modes de Session

| Mode | Usage | Dispositifs |
|------|-------|-------------|
| `inline` | XR dans page web (pas immersif) | Tous |
| `immersive-vr` | VR complète, tracking 6DoF | Casques VR |
| `immersive-ar` | AR superposé au monde réel | ARCore/ARKit devices |
| Reference: `local` | Origine = position session, 6DoF | Tous |
| Reference: `local-floor` | Sol = y=0, 6DoF | Room-scale |
| Reference: `bounded-floor` | Sol + limites géométriques | Guardian/Chaperone |
| Reference: `unbounded` | Monde ouvert, tracking continu | Casques avancés |

## WebXR Layers (Performance)

### Projection Layer vs WebGL Layer
```javascript
// WebGL Layer (baseline)
const glLayer = new XRWebGLLayer(session, gl);

// Projection Layer (copie GPU→GPU native)
const projectionLayer = new XRProjectionLayer(session, {
    textureType: 'texture-array',
    colorFormat: gl.RGBA8,
    depthFormat: gl.DEPTH_COMPONENT24
});

// Quad Layer (UI 2D flottante)
const quadLayer = new XRQuadLayer(session, {
    space: referenceSpace,
    layout: 'stereo-top-bottom',
    pixelWidth: 1024,
    pixelHeight: 1024
});
quadLayer.transform = new XRRigidTransform({x:0, y:1.5, z:-2});
session.updateRenderState({ layers: [projectionLayer, quadLayer] });

// Cube Layer (skybox/360°)
const cubeLayer = new XRCubeLayer(session, {
    space: referenceSpace,
    layout: 'mono',
    pixelWidth: 1024
});

// Cylinder Layer (panorama courbe)
const cylinderLayer = new XRCylinderLayer(session, {
    space: referenceSpace,
    radius: 2,
    centralAngle: Math.PI * 0.75,
    aspectRatio: 1.5
});
```

### Layers WebXR vs WebGL Brut
| Layer | Overhead | Usage |
|-------|----------|-------|
| XRWebGLLayer | Élevé | Rendu classique Three.js |
| XRProjectionLayer | Faible | Rendu natif |
| XRQuadLayer | Minimal | UI/affichage 2D |
| XRCubeLayer | Minimal | Environnements 360° |
| XRCylinderLayer | Minimal | Panneaux incurvés |
| XREquirectLayer | Minimal | Vidéo 360° |

## AR WebXR

### Hit Test
```javascript
const hitTestSource = await session.requestHitTestSource({
    space: referenceSpace,
    entityTypes: ['plane', 'point', 'mesh']  // AR features
});

// Frame callback
const hitResults = frame.getHitTestResults(hitTestSource);
for (const hit of hitResults) {
    const pose = hit.getPose(referenceSpace);
    // Placer objet à hit.position
}
```

### Anchors (WebXR Anchors Module)
```javascript
const anchor = await session.requestAnchor(
    poseTransform,
    referenceSpace
);

// Écouter nouveaux anchors
session.addEventListener('anchorsupdated', (event) => {
    for (const anchor of event.added) { /* ... */ }
    for (const anchor of event.updated) { /* ... */ }
    for (const anchor of event.removed) { /* ... */ }
});
```

### Plane Detection
```javascript
// Session features: ['plane-detection']
const detectedPlanes = frame.detectedPlanes || [];

for (const plane of detectedPlanes) {
    // plane.orientation: horizontal | vertical
    // plane.polygon: DOMPointReadOnly[]
    // plane.semanticLabel: 'wall' | 'floor' | 'ceiling' | 'table' | ...
    const polygon = plane.polygon;
    // Calculer centre et normal
}
```

### Mesh Detection
```javascript
// Features: ['mesh-detection']
const meshes = frame.detectedMeshes || [];

for (const mesh of meshes) {
    const indices = mesh.indices;    // Uint16Array
    const vertices = mesh.vertices;  // Float32Array
    const normals = mesh.normals;    // Float32Array
    const uvs = mesh.uvs;            // Float32Array
    const semLabel = mesh.semanticLabel; // Classe per-vertex
}
```

## Hand Tracking

```javascript
const inputSources = session.inputSources;
for (const source of inputSources) {
    // source.hand: XRHand
    if (source.hand) {
        const wrist = source.hand.get('wrist');
        // Joints: wrist, thumb-metacarpal, thumb-phalanx-proximal, 
        // thumb-phalanx-distal, thumb-tip, index-finger-*, 
        // middle-finger-*, ring-finger-*, little-finger-*
        
        const pose = frame.getJointPose(wrist, referenceSpace);
        if (pose) {
            // pose.transform.position, rotation
        }
    }
}
```

## Three.js WebXR Integration

```javascript
import { WebXRManager } from 'three';

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.xr.enabled = true;

// Session
document.body.appendChild(VRButton.createButton(renderer));
// ARButton pour AR

// Controllers
const controller1 = renderer.xr.getController(0);
controller1.addEventListener('selectstart', () => { /* grip sélection */ });
controller1.addEventListener('squeeze', () => { /* pincer */ });
scene.add(controller1);

// Animation loop avec session XR
renderer.setAnimationLoop((time, frame) => {
    // Mise à jour scène
    renderer.render(scene, camera);
});
```

## Performance WebXR

### Budget Limites Web
| Métrique | Cible VR | Cible AR |
|----------|----------|----------|
| FPS | 72/90/120 | 60+ |
| Poly count | < 200k | < 100k |
| Draw calls | < 100 | < 50 |
| Texture size | 2048² max | 1024² max |
| JS frame time | < 8ms (120Hz) | < 11ms |
| GPU frame time | < 4ms | < 6ms |

### Optimisations
- **Utiliser `XRWebGLLayer` avec `antialias: false`** → MSAA trop coûteuse
- **RequestAnimationFrame natif** (éviter setTimeout/setInterval)
- **Uniform buffers** pour matrices partagées
- **Instanced rendering** pour objets répétés
- **Foveated rendering** : `session.updateRenderState({ foveationLevel: 1 })` (0 = aucun, 1 = max)
- **Layers multiples** pour UI vs scène (éviter re-render complet)

## Débogage

```javascript
navigator.xr.addEventListener('devicechange', ...)
// Chrome: chrome://flags/#webxr
// about://gpu → GPU info
// DevTools: More Tools → WebXR

// Métriques
session.requestAnimationFrame((time, frame) => {
    console.log(frame.pose?.transform);
});
```

## Pitfalls

- **WebXR non supporté sur Safari iOS avant 16.4** (partiel depuis 17.0)
- **Firefox Nightly** uniquement pour VR (pas de support AR)
- **Pas de microphone AR** dans spec WebXR (utiliser Web Audio API)
- `requestSession()` doit être déclenché par geste utilisateur (click/tap)
- **WebXR Layers** requièrent Chrome 90+ ou Edge
- **Hit test + anchors** nécessitent ARCore/ARKit natif (pas WebXR abstrait)
- `XRReferenceSpaceEvent` résilient : gérer `reset` events
- Pas de fallback AR→VR intégré : coder les deux séparément
- **Double/triple rendu** en AR (caméra + scène) → attention overdraw
