---
title: VR Optimization — Optimisation de Performance pour la Réalité Virtuelle
description: Guide complet d'optimisation VR — profiling, rendu stéréo, foveated rendering, LOD, shader, GPU/CPU budgeting, memory management, frame timing, ASW/SSW, Android/Quest/SteamVR, thermal throttling.
category: creative
domain: AR/VR
author: EVA (The Hive)
version: 1.0.0
created: 2026-07-22
updated: 2026-07-22
---

# VR Optimization — Optimisation de Performance VR

## Principes Fondamentaux

### Budget Frame VR
```
Frame total: 11.1ms @ 90Hz / 13.9ms @ 72Hz / 8.3ms @ 120Hz
├── CPU: 30% → 3.3-4.2ms (Physics, Anim, Culling, Scripts)
├── GPU: 50% → 5.5-7ms (Draw calls, Shaders, Post-process, Render targets)
└── Compositing: 20% → 2.2-2.8ms (Warp, Timewarp, Distortion)
```

### Règle d'Or VR
> **Chaque milliseconde économisée = 1ms de plus pour la fidélité visuelle**

### Métriques Clés
| Métrique | Cible | Seuil critique |
|----------|-------|---------------|
| Frame Time | < 11ms (90Hz) | > 13ms → reprojection |
| Draw Calls | < 200 (mobile) / < 500 (PC) | > 400/+1000 → drop frames |
| Vertices | < 150k (mobile) / < 500k (PC) | > 300k/+1M → GPU bound |
| Render Res | 1.0-1.5× natif | > 2.0× → overkill perceptif |
| PSO (Pipeline States) | < 50 | > 100 → driver overhead |
| Allocations Frame | 0 (pooling) | > 10KB → GC spikes |
| Fillrate | < 2× pixels natifs | > 3× → overdraw |
| VRAM | < 80% capacité | > 90% → texture thrashing |

## Rendering Pipeline VR

### Single Pass Instanced (Obligatoire)
```csharp
// Unity : Player Settings → XR Settings → Stereo Rendering Method
// ⚠️ Multi Pass = EXCLU → 2× draw calls, 2× state changes

// Vérifier que Single Pass Instanced est actif
bool usesSPI = XRSettings.stereoRenderingMode == XRSettings.StereoRenderingMode.SinglePassInstanced;
if (!usesSPI) {
    Debug.LogError("Single Pass Instanced désactivé !");
}

// Shader doit supporter INSTANCING
// #pragma multi_compile_instancing
// UNITY_VERTEX_INPUT_INSTANCE_ID dans struct
// UNITY_SETUP_INSTANCE_ID(v);
```

### Foveated Rendering
```csharp
// Meta Quest : Fixed Foveated Rendering (FFR)
OVRManager.foveatedRenderingLevel = OVRManager.FoveatedRenderingLevel.High;
OVRManager.foveatedRenderingDynamic = true;

// Niveaux FFR Meta: Off, Low, Medium, High, HighTop
// High = 4 rings: centre 1.0× → périphérie 0.125× résolution

// Eye Tracked Foveated Rendering (ETFR) — Quest Pro
OvrManager.eyeTrackedFoveatedRenderingEnabled = true;
// Économie : 30-50% GPU

// Vulkan : VK_FOVEATED_RENDERING
```

### Dynamic Resolution
```csharp
// Meta — Auto resolution scaling basé GPU load
OVRManager.enableDynamicResolution = true;

// Ajustement manuel avec seuils
float scale = 1.0f;
float gpuTime = FrameTimingManager.GetGpuFrameTime();

if (gpuTime > 11f) scale = Mathf.Lerp(scale, 0.7f, 0.1f);
else if (gpuTime < 8f) scale = Mathf.Lerp(scale, 1.2f, 0.05f);

XRSettings.renderViewportScale = scale;
```

### Application SpaceWarp (ASW)
```csharp
// ASW 2.0 : interpolation de frames (30→60, 45→90 FPS)
// Active quand GPU < cible FPS
OVRManager.enableSpaceWarp = true;

// Motion vectors requis
// Inclure _CameraDepthTexture + _CameraMotionVectorsTexture
// Shader doit output motion vectors

// Contrepartie : artefacts visuels sur animations rapides
```

## CPU Optimisation

### Object Pooling (Zéro Alloc Frame)
```csharp
// ❌ MAUVAIS : allocation dynamique
void Update() {
    var obj = Instantiate(prefab); // Alloc ! → GC spike
    Destroy(obj);                   // Alloc ! → GC collect
}

// ✅ BON : pooling
public class ObjectPool {
    private Stack<GameObject> pool = new Stack<GameObject>();
    
    public GameObject Get() {
        if (pool.Count > 0) return pool.Pop();
        return Instantiate(prefab);
    }
    
    public void Return(GameObject obj) {
        obj.SetActive(false);
        pool.Push(obj);
    }
}
```

### Frustum Culling (Occlusion)
```csharp
// Unity — Occlusion Culling
// Window → Rendering → Occlusion Culling
// → Bake pour scènes statiques

// LOD Groups obligatoires
// LOD0: 100% (proche) → LOD1: 50% (moyen) → LOD2: 25% (loin) → Culled

// Manual frustum
Plane[] planes = GeometryUtility.CalculateFrustumPlanes(camera);
foreach (Renderer r in allRenderers) {
    r.enabled = GeometryUtility.TestPlanesAABB(planes, r.bounds);
}
```

### Physics Optimisation
```csharp
// Augmenter physics timestep
Time.fixedDeltaTime = 0.02f; // 50Hz (au lieu de 0.01/100Hz)

// Supprimer collisions inutiles
// Layer collision matrix : seulement layers pertinents

// Continuous collision (CCD) — désactiver sauf objets rapides (< 5 objets)

// Ragdoll → coroutines espacées
```

## GPU Optimisation

### Draw Call Reduction

| Technique | Gain | Effort |
|-----------|------|--------|
| Static Batching | -50% DC | Faible |
| GPU Instancing | -90% DC | Moyen |
| Texture Atlas | -30% DC | Moyen |
| Material Combining | -40% DC | Élevé |
| Lightmap Baking | -60% DC | Élevé |
| Vertex Baking | -30% DC | Élevé |

### Shader Optimisation
```hlsl
// ❌ MAUX : expensive operations dans fragment
float4 frag(v2f i) : SV_Target {
    float noise = sin(i.uv.x * 100) * cos(i.uv.y * 100); // Perlin coûteux
    float3 reflection = reflect(i.normal, i.viewDir);      // Trop cher
    return float4(noise, noise, noise, 1);
}

// ✅ BIEN : précalculer ou utiliser lookup
float4 frag(v2f i) : SV_Target {
    float noise = tex2D(_NoiseLookup, i.uv * 100).r; // Texture lookup
    return float4(noise, noise, noise, 1);
}
```

### Règles Shader VR
1. **Pas d'alphatest** (clip/discard) → break GPU early-Z
2. **Pas de fragment-heavy ops** (sin/cos/pow/exp) → dans vertex
3. **Préférer `tex2Dlod`** dans vertex shader
4. **Half precision** (`half`/`min16float`) possible sur GPU mobile
5. **Éviter `tex2D` dans des boucles** → trop de latency
6. **LOD bias négatif** pour textures fines
7. **Forward rendering** (pas deferred → overdraw VR)

### Overdraw
```
Écran VR: chaque pixel rendu 1.5-3× (overdraw)
Causes: transparents, terrains, skybox, particles

Solutions:
- Occlusion culling (baked) → z-prepass
- Pas de surcouche transparente (sauf UI critique)
- Z-test : ZWrite On avant passages coûteux
- OIT (Order-Independent Transparency) — coûteux, éviter
```

## Memory

### Texture Budget VR
```
Format compressé requis:
- ASTC 6×6 (Android/Quest) — 0.44 bytes/pixel
- BC7 (PC VR) — 1 byte/pixel

| Scène | Budget VRAM |
|-------|-------------|
| Mobile VR (Quest) | < 2 GB total |
| PC VR (SteamVR) | < 6 GB total |
| Textures max | 2048² (mobile), 4096² (PC) |
| Render target | 2K×2K (×2 stéréo) |
| Cubemap IBL | 256² (réduire à 128² si possible) |
```

### GC Management
```csharp
// Pool mono-objet pour éviter allocations
private readonly List<RaycastHit> hitCache = new List<RaycastHit>();
void Update() {
    // Réutiliser hitCache.clear() au lieu de new List<>()
    Physics.RaycastNonAlloc(ray, hitCache);
}

// Éviter foreach sur List<> (→ alloc iterator)
for (int i = 0; i < list.Count; i++) { /* ... */ }

// Pas de LINQ dans update
// Pas de strings concat (StringBuilder)
// Pas de delegates / events lambda dans Update
```

## Profiling

### Tools par Plateforme

| Plateforme | Outil | Usage |
|------------|-------|-------|
| **Unity Editor** | Frame Debugger | Draw calls, shader variants |
| **Quest** | Oculus Performance HUD | FPS, GPU/CPU time, FFR level |
| **Quest** | ADB + systrace | CPU threads, vsync |
| **Quest** | RenderDoc (Vulkan) | GPU debug frame by frame |
| **PC VR** | SteamVR Advanced Frame Timing | Compositor wait, reprojection |
| **PC VR** | PIX (DX12) / Nsight | GPU counters |
| **Vision Pro** | Metal Debugger | GPU trace, shader perf |

### OVR Metrics Tool (Quest)
```csharp
// Activer HUD debug
OVRManager.displayPerformanceHud = true;

// Lire métriques programmatiquement
OVRPlugin.GetPerfMetrics();
// perfMetrics["CompositorDroppedFrameCount"]
// perfMetrics["CompositorLatency"]
// perfMetrics["AppCPUTime"]
// perfMetrics["AppGPUTime"]
```

### SteamVR Frame Timing
```
Compositor wait (idéal < 1ms)
├── App CPU time (target < 4ms)
├── App GPU time (target < 6ms)  
└── Compositor time (warp + submit < 2ms)

Reprojection ratio > 5% → problème
```

## Thermal Management

| Température | Réaction | Action |
|-------------|----------|--------|
| < 38°C | ✅ Normal | — |
| 38-40°C | ⚠️ Attention | Réduire résolution / FFR level |
| 40-42°C | 🔴 Critique | Désactiver post-process |
| > 42°C | 🛑 Throttling (45 FPS) | Mode économie minimal |

```csharp
// Détecter throttling sur Quest
OVRManager.TrackingOriginType = OVRManager.TrackingOrigin.EyeLevel;

// Réagir à la chauffe
void CheckThermal() {
    int level = OVRPlugin.GetSystemThermalLevel();
    if (level >= 3) {
        XRSettings.renderViewportScale = 0.7f;
        OVRManager.foveatedRenderingLevel = FoveatedRenderingLevel.HighTop;
        QualitySettings.shadowDistance = 5f;
        QualitySettings.shadowResolution = ShadowResolution.Low;
    }
}
```

## Checklist Finale (Pré-Release VR)

- [ ] Single Pass Instanced activé
- [ ] Aucune allocation dans Update (zero GC)
- [ ] FFR dynamique activé (High)
- [ ] LOD Groups sur tous les meshes > 100 tris
- [ ] Occlusion Culling baked
- [ ] Pas de shader avec clip/discard
- [ ] Toutes textures en ASTC/BC compressé
- [ ] Pas de lumière dynamique > 2
- [ ] Particle system < 100 max particles
- [ ] Physics timestep = 0.02s (50Hz)
- [ ] ASW activé (fallback 45→90 FPS)
- [ ] Test thermique 30 minutes continu
- [ ] VRAM < 80% capacity
- [ ] Draw calls < 200 (mobile) / < 400 (PC)
- [ ] Frame time stable < 11ms (90Hz)
- [ ] Audio spatialisé, pas de clips longs

## Pitfalls

- **Multi Pass = double travail** → toujours vérifier mode rendu
- **FFR Off = 2× GPU cost** sur périphérie (personne ne regarde)
- **Transparent shaders tuent le early-Z** → réserver à UI minime
- **Physics 100Hz = double CPU** pour rien (50Hz suffit VR)
- **Texture trop grande** → thrashing VRAM, drops frames
- **Lightmaps non cuites** → GI temps réel = mort GPU VR
- **Oublier le test thermique** → throttling après 10min
- **Profiling sans casque** = données invalides (compositor absent)