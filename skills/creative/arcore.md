---
title: ARCore — Développement AR Google (Android)
description: Guide complet de développement en Réalité Augmentée avec ARCore 1.40+ — Cloud Anchors, Geospatial API, Depth API, Scene Understanding, Augmented Images/Faces, Light Estimation.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# ARCore — Développement AR Google

## Architecture Fondamentale

### Concepts Clés
- **Motion Tracking** : 6DoF via Visual-Inertial Odometry (VIO) — fusion caméra + IMU
- **Environmental Understanding** : détection plans horizontaux/verticaux, mesh du monde
- **Light Estimation** : moyenne environnementale + estimateur HDR
- **Depth API** : carte de profondeur via stéréo passive (RGB) + active (LiDAR compat.)

### SDK Supportés
- **ARCore SDK for Android (Java/Kotlin)** : OpenGL ES, GLSurfaceView
- **ARCore SDK for Unity** : AR Foundation + ARCore XR Plugin
- **ARCore SDK for Sceneform** : Java 3D framework (maintenance)
- **ARCore SDK for Web** : WebXR avec ARCore backend (Chrome Android)
- **ARCore SDK for Unreal** : Unreal Engine 4.26+

## ARCore Session Lifecycle

```kotlin
// Kotlin — SDK natif
class ArActivity : AppCompatActivity() {
    private lateinit var session: Session
    private lateinit var renderer: BackgroundRenderer
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Vérifier ARCore disponible + compatible
        if (!Session.isSupported(this)) {
            showToast("ARCore non supporté")
            finish()
            return
        }
        // Camera permission (Android 6+)
        requestCameraPermission()
    }
    
    private fun createSession() {
        session = Session(this)
        val config = Config(session)
        config.depthMode = Config.DepthMode.AUTOMATIC  // Depth API
        config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
        config.instantPlacementMode = true
        config.geospatialMode = Config.GeospatialMode.ENABLED  // Geospatial API
        session.configure(config)
    }
    
    // Frame callback
    override fun onDrawFrame(gl: GL10?) {
        val frame = session.update()
        val camera = frame.camera
        
        // Raycast au centre écran
        val screenPoint = floatArrayOf(centerX, centerY)
        val hits = frame.hitTest(screenPoint)
        if (hits.isNotEmpty()) {
            val planeAttachment = hits[0].createAnchorOrCancel()?.let { anchor ->
                attachObject(anchor.pose)
            }
        }
        
        // Depth map
        val depthImage = frame.acquireDepthImage()
        // ... utiliser depth buffer
        depthImage.close()
        
        // Light estimation
        val lightEstimate = frame.lightEstimate
        val ambientIntensity = lightEstimate.pixelIntensity  // lux
    }
}
```

## API Clés

### Augmented Images (Détection d'Images)
```kotlin
val imageDatabase = AugmentedImageDatabase(session)
imageDatabase.addImage("qr_code", BitmapFactory.decodeResource(resources, R.drawable.qr_ref))
config.augmentedImageDatabase = imageDatabase

// onUpdate:
val augmentedImages = frame.getUpdatedTrackables(AugmentedImage::class.java)
for (image in augmentedImages) {
    if (image.trackingState == TrackingState.TRACKING) {
        when (image.trackingMethod) {
            AugmentedImage.TrackingMethod.FULL_TRACKING   → // tracking complet
            AugmentedImage.TrackingMethod.LAST_KNOWN_POSE → // pose estimée (perdu partiel)
        }
    }
}
```

### Augmented Faces
```kotlin
val config = Config(session)
config.augmentedFaceMode = Config.AugmentedFaceMode.MESH3

// Face mesh: 468 vertices, topology triangulaire
val faces = frame.getUpdatedTrackables(AugmentedFace::class.java)
for (face in faces) {
    val mesh = face.mesh  // vertex, normal, texture UV
    val pose = face.centerPose  // centre de la tête
    // regionPose: NOSE, FOREHEAD_LEFT, FOREHEAD_RIGHT
}
```

### Geospatial API (VPS — Visual Positioning Service)
```kotlin
// Résolution de pose par rue locale (Visual Positioning System)
val earth = session.earth
if (earth.trackingState == TrackingState.TRACKING) {
    val cameraGeospatialPose = earth.cameraGeospatialPose
    // latitude, longitude, altitude, heading, hAccuracy, vAccuracy
    
    // Créer ancrage à coordonnées GPS
    val geospatialAnchor = earth.createAnchor(lat, lon, altitude, quaternion)
    
    // Terrain anchor (altitude depuis modèle terrain Google)
    val terrainAnchor = earth.createAnchor(lat, lon, 0.0, quaternion, altitudeType = TERRAIN)
    
    // Rooftop anchor (altitude toit bâtiment)
    val rooftopAnchor = earth.createAnchor(lat, lon, 0.0, quaternion, altitudeType = ROOFTOP)
}
```

### Cloud Anchors (Ancres Multi-utilisateurs)
```kotlin
// Hôte
val cloudAnchor = session.hostCloudAnchor(anchor) { result ->
    when (result) {
        CloudAnchorResponse.SUCCESS -> {
            val cloudAnchorId = cloudAnchor.cloudAnchorId
            // Partager cloudAnchorId aux pairs
        }
    }
}

// Résolveur (autre device)
val resolvedAnchor = session.resolveCloudAnchor(cloudAnchorId) { result ->
    when (result) {
        CloudAnchorResponse.SUCCESS -> {
            // Ancrage récupéré → objet visible
        }
    }
}
```

### Depth API
```kotlin
// Mode: AUTOMATIC (best effort) ou RAW_DEPTH (full resolution)
val depthImage = frame.acquireDepthImage()

// Confiance de chaque pixel (0–1)
val confidenceImage = frame.acquireDepthConfidenceImage()

// Occlusion via depth buffer
// 1. Obtenir depth matrix → gl_FragDepth
// 2. Shader occlusion: comparer depth fragment vs depth map

// Obstruction avoidance
val rayDirection = camera.pose.zAxis.negated()
val depthRay = frame.hitTest(centerX, centerY)  // inclut profondeur réelle

// Geometry snapping
val point = depthImage.depthToPoint(u, v, depthImage.normalizedUV)
val worldPoint = camera.pose.compose(point)
```

## AR Foundation & Unity

```csharp
// Unity AR Foundation — ARCore backend
public class ARPlacement : MonoBehaviour {
    public GameObject prefab;
    private ARRaycastManager raycastManager;
    
    void Start() {
        raycastManager = GetComponent<ARRaycastManager>();
    }
    
    void Update() {
        if (Input.touchCount <= 0) return;
        var touch = Input.GetTouch(0);
        
        var hits = new List<ARRaycastHit>();
        if (raycastManager.Raycast(touch.position, hits, TrackableType.PlaneWithinPolygon)) {
            // ARCore hit
            var anchorManager = GetComponent<ARAnchorManager>();
            var anchor = anchorManager.AddAnchor(new Pose(hits[0].pose.position, hits[0].pose.rotation));
            Instantiate(prefab, anchor.transform);
        }
    }
}
```

## Performance

### Budget ARCore
| Métrique | Cible | Dégradé |
|----------|-------|---------|
| FPS | 30 | < 20 → tracking instable |
| CPU | < 50% | ARCore thread consomme 25-40% |
| Thermal | < 40°C | Throttling → perte tracking |
| RAM | < 200 MB | + texture/depth buffer |

### Optimisations
- **Reduce camera resolution** : `CameraConfig.TargetFps.TARGET_FPS_30`
- **GPU Texture sharing** : `CameraConfig.CameraTextureSharingBehavior.PRIVILEGED_CPU_ACCESS` (éviter copie)
- **Depth min interval** : `Config.DepthMode.DISABLED` si non nécessaire
- **Light estimation period** : `Config.LightEstimationMode.AMBIENT_INTENSITY` (moins coûteux que HDR)

## Débogage

```kotlin
// Google Play Services for AR diagnostics
// 1. Installer: com.google.ar.core.examples.app.apk
// 2. ADB shell dumpsys arcore
// 3. Logcat tag: ArCoreApi, ArCoreNative

// Capturer frame debugging
frame.transformDisplayGeometry(glMat4)
```

## Pitfalls

- ARCore **non supporté** sur devices sans Google Play Services (Huawei, certains China ROM)
- Geospatial API nécessite **Google Play Services for AR** v1.35+ et connexion réseau
- Cloud Anchors expirées après 24h sur plan gratuit (payant: 365 jours)
- Depth API qualité variable selon conditions lumière et texture surface
- AugmentedImages limitées à 20 images par base, résolution minimale 300×300px
- Ne pas appeler `session.update()` depuis plusieurs threads
- Toujours `close()` les `Image` acquises (depthImage, etc.)
- Camera permission requise runtime (Android 6+), `ACCESS_FINE_LOCATION` pour Geospatial
