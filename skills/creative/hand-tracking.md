---
title: Hand Tracking — Suivi des Mains en Réalité Étendue
description: Guide complet du hand tracking pour XR — détection 21/28 joints, skeleton, interaction naturelle, gestures, collisions, haptiques, API Meta/ARKit/WebXR, machine learning hand pose.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# Hand Tracking — Suivi des Mains en XR

## Principes Fondamentaux

### Technologies de Tracking
| Technologie | Précision | Latence | FOV | Plateformes |
|-------------|-----------|---------|-----|-------------|
| **Vision (caméra IR)** | ±2mm | ~5-15ms | 160°×160° | Quest, Pico, Magic Leap |
| **Vision (RGB)** | ±5mm | ~20-40ms | 120°×80° | Vision Pro (LiDAR + RGB) |
| **LiDAR + ML** | ±1mm | ~8ms | 180° | Vision Pro (Apple) |
| **Ultrasons** | ±10mm | ~50ms | 120° | Leap Motion (discontinué) |
| **Capteurs gants** | ±0.5mm | ~2ms | ∞ (mécanique) | Manus, HaptX, SenseGlove |

### Squelettes de Main Standards

#### 21 Joints (OpenXR / Meta)
```
Wrist (poignet)
├── Thumb: CMC → MCP → IP → Tip (4 joints)
├── Index: MCP → PIP → DIP → Tip (4 joints)
├── Middle: MCP → PIP → DIP → Tip (4 joints)
├── Ring: MCP → PIP → DIP → Tip (4 joints)
└── Little: MCP → PIP → DIP → Tip (4 joints)
+ Palm (paume) = 21 joints
```

#### 28 Joints (Apple ARKit / OVR)
Ajoute aux 21 : Thumb Proximal, Index Proximal, Middle Proximal, Ring Proximal, Little Proximal, Distal supplémentaire + rotation palmaire

### Anatomie pour XR
```
Joint hierarchy:
       WRIST
    ┌───┼───┬───┬───┐
   TH  ID  MI  RI  LI
  CMC  MCP MCP MCP MCP
  MCP  PIP PIP PIP PIP
  IP   DIP DIP DIP DIP
  TIP  TIP TIP TIP TIP
```

## Meta Quest Hand Tracking

```csharp
using Oculus.Interaction.Input;
using UnityEngine;

public class HandVisualizer : MonoBehaviour {
    [SerializeField] private Hand hand; // OVRHand
    [SerializeField] private Transform[] jointTransforms = new Transform[21];
    
    void Update() {
        for (int i = 0; i < 21; i++) {
            if (hand.GetJointPose((HandJointId)i, out Pose pose)) {
                jointTransforms[i].position = pose.position;
                jointTransforms[i].rotation = pose.rotation;
            }
        }
        
        // Pinch détection
        if (hand.GetIndexFingerIsPinching()) {
            OnPinch();
        }
    }
    
    void OnPinch() { /* Action pincement */ }
}
```

### Gestes Natifs Meta
- **Pinch** (pouce + index) → sélection, grab distant
- **Palm** (paume ouverte) → menu
- **Fist** (poing) → fermeture
- **Point** (index pointé) → pointer
- **Wrist flick** → lancer objet
- **Grab** (prise) → attraper objet

### Hand-to-Object Interaction
```csharp
public class HandGrab : MonoBehaviour {
    public Hand handLeft, handRight;
    private bool isGrabbing = false;
    
    void Update() {
        // Détecter pincement + proximité d'objet
        float distance = Vector3.Distance(handLeft.PinchPoint, target.position);
        if (handLeft.GetIndexFingerIsPinching() && distance < 0.1f) {
            if (!isGrabbing) {
                isGrabbing = true;
                GetComponent<Rigidbody>().isKinematic = true;
                GetComponent<Rigidbody>().useGravity = false;
            }
        } else if (isGrabbing) {
            Release();
        }
    }
    
    void Release() {
        isGrabbing = false;
        rb.isKinematic = false;
        rb.useGravity = true;
        rb.linearVelocity = handLeft.Velocity; // Transfert momentum
    }
}
```

## Apple Hand Tracking (ARKit / visionOS)

```swift
import ARKit

class HandTrackingManager {
    let session = ARSession()
    
    func start() async {
        let handTracking = HandTrackingProvider()
        
        for await update in handTracking.anchorUpdates {
            let handAnchor = update.anchor
            let chirality = handAnchor.chirality  // .left, .right
            
            for joint in handAnchor.handSkeleton.allJoints {
                guard joint.isTracked else { continue }
                
                let transform = joint.anchorFromJointTransform
                let position = transform.rows.columns[3]
                
                // Joint types
                switch joint.name {
                case .wrist:
                    // Position poignet
                case .thumbTip:
                    // Bout du pouce
                case .indexFingerTip:
                    // Bout de l'index
                // ... 28 joints
                @unknown default:
                    break
                }
            }
        }
    }
}
```

## WebXR Hand Tracking

```javascript
async function initHandTracking() {
    const session = await navigator.xr.requestSession('immersive-vr', {
        requiredFeatures: ['hand-tracking']
    });
    
    session.addEventListener('inputsourceschange', (event) => {
        for (const source of event.added) {
            if (source.hand) {
                console.log(`Main ${source.handedness} détectée`);
            }
        }
    });
}

function processHandFrame(frame, referenceSpace) {
    const sources = frame.session.inputSources;
    
    for (const source of sources) {
        if (!source.hand) continue;
        
        // Parcourir les joints
        for (const [jointName, joint] of Object.entries(source.hand)) {
            const jointPose = frame.getJointPose(joint, referenceSpace);
            if (jointPose) {
                // jointPose.transform.position, rotation
                const pos = jointPose.transform.position;
                const rot = jointPose.transform.orientation;
                
                // Calculer pincement (distance pouce ↔ index)
                if (jointName === 'thumb-tip') {
                    thumbTip = pos;
                } else if (jointName === 'index-finger-tip') {
                    indexTip = pos;
                }
            }
        }
        
        // Détection pincement
        if (thumbTip && indexTip) {
            const distance = Math.hypot(
                thumbTip.x - indexTip.x,
                thumbTip.y - indexTip.y,
                thumbTip.z - indexTip.z
            );
            if (distance < 0.02) { // 2cm
                handlePinch(source.handedness);
            }
        }
    }
}
```

## Reconnaissance de Gestes Avancée

### ML pour Gesture Recognition (MediaPipe + TensorFlow)
```python
import mediapipe as mp
import numpy as np
from tensorflow import keras

# Modèle MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)

# Points clés → séquence pour LSTM
def extract_landmarks(frame):
    results = hands.process(frame)
    if results.multi_hand_landmarks:
        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks:
            for lm in hand_landmarks.landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
        return np.array(landmarks).flatten()
    return None

# Modèle classifieur LSTM (séquences temporelles)
class HandGestureClassifier:
    def __init__(self):
        self.model = keras.Sequential([
            keras.layers.LSTM(128, input_shape=(30, 63)), # 30 frames × 21 joints × 3
            keras.layers.Dropout(0.2),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(8, activation='softmax') # 8 gestes
        ])
    
    def predict(self, sequence):
        return self.model.predict(np.array([sequence]))
```

### Algorithmes de Détection de Gestes
| Méthode | Précision | Latence | Usage |
|---------|-----------|---------|-------|
| **Distance euclidienne joints** | ~80% | <1ms | Pinch, Point |
| **Angle entre segments** | ~85% | <2ms | Fist, Peace |
| **SVM sur features** | ~90% | ~3ms | Gestes mixtes |
| **LSTM sur séquence** | ~95% | ~10ms | Gestes dynamiques |
| **Transformers (TimesFormers)** | ~97% | ~15ms | Gestes complexes |

## Optimisation Hand Tracking

### Budget CPU/GPU
| Métrique | Cible | Problème si dépassé |
|----------|-------|---------------------|
| CPU hand tracking | <15% | Perte tracking, tremblements |
| GPU inference | <3ms | Latence notable |
| Pose update rate | >60Hz | Mouvement saccadé |
| Joint count | 21 (min) → 28 (max) | Plus de joints = plus de overhead |

### Réduction de Latence
```csharp
// OVR — réduire hand tracking frequency
OVRPlugin.handTrackingVersion = OVRPlugin.HandTrackingVersion.V2;

// Prédiction de pose (extrapolation)
Vector3 predictedPos = currentPos + (currentPos - lastPos) * predictionTime;

// Interpolation visuelle (rendu entre deux mises à jour)
handVisualTransform.position = Vector3.Lerp(
    prevHandPos, currentHandPos, interpolationFactor);
```

## Haptiques pour Mains

```csharp
// Haptiques sur pincement
if (isPinching) {
    InputDevices.GetDeviceAtXRNode(XRNode.RightHand)
        .SendHapticImpulse(0, 0.5f, 0.1f);
}

// Retour haptique au contact
void OnCollisionEnter(Collision collision) {
    if (handMode == HandMode.PALM) {
        // Vibration intense (contact paume)
        SendHaptic(1.0f, 0.2f);
    } else {
        // Vibration légère (effleurement doigt)
        SendHaptic(0.3f, 0.05f);
    }
}
```

## Pitfalls

- **Occulsion main → perte tracking** : mains bloquées (dans les poches, derrière corps)
- **Lumière directe forte** (soleil IR) → bruit tracking
- **Pinch en continu** = fatigue main (gorilla arm) → éviter actions prolongées
- **Fist detection avec objets** : confus si main tient déjà qqchose
- **Hand overlap** (mains croisées) : confusion gauche/droite
- **Latence > 20ms** : cassure d'immersion, tremblements → toujours viser <15ms
- **Précision millimétrique impossible** sans gants → tolérance ≥1cm pour collisions
- **Batterie** : hand tracking consomme 2-4× plus que controllers → limiter tracking zones