---
name: game-optimization
description: Optimisation de jeux vidéo — profiling CPU/GPU, draw calls, batching, LOD, occlusion culling, mémoire, asset budgeting, mobile/VR/console, object pooling, Addressables, IL2CPP, SIMD.
tags: [optimisation, performance, profiling, gpu, cpu, memory, lod, culling, mobile, vr, console, il2cpp]
---

# Game Optimization — Guide Complet

Ce skill couvre l'optimisation de performance pour jeux vidéo sur tous les supports. À charger pour toute tâche de profiling, réduction de draw calls, optimisation mémoire, ou débogage de framerate.

---

## 1. Pipeline de Profiling — Trouver les Goulots

### Outils par Plateforme

| Outil | Usage | Plateforme |
|-------|-------|------------|
| **Unity Profiler** | CPU/GPU/Memory/UI | Unity |
| **Unreal Insights** | Frame trace détaillée | Unreal |
| **Godot Monitor** | FPS, draw calls, mémoire | Godot |
| **RenderDoc** | Frame capture GPU | Tous moteurs |
| **NVIDIA Nsight** | GPU warp occupancy, shader | PC/Console |
| **AMD Radeon GPU Profiler** | GPU pipeline | PC |
| **PIX** | GPU timing DirectX | Windows |
| **Tracy** | Frame profiler C++ | Natif |
| **Xcode Instruments** | Metal, CPU, mémoire | iOS/macOS |
| **Android GPU Inspector** | GPU Android | Android |

### Phases de Profiling

```text
1. CAPTURE → Frame complete (rendu, scripts, physique, réseau)
2. IDENTIFIER → Quel est le goulot?
   → GPU bound  : draw calls, shaders, fillrate, overdraw
   → CPU bound  : scripts, physics, animation, garbage collection
   → Memory     : assets trop lourds, fuites, fragmentation
3. MESURER → Sans profiling, pas d'optimisation
4. OPTIMISER → Une variable à la fois
5. VÉRIFIER → La modification a-t-elle amélioré? Régressé?
```

### Metrics Clés

```text
FPS Target:          30 (mobile), 60 (console/PC), 72/90/120 (VR)

Draw Calls:          < 2000 (PC), < 500 (mobile), < 200 (VR)
Triangles:           < 2M (PC), < 200K (mobile)
Vertices:            < 4M (PC), < 500K (mobile)

SetPass Calls:       < 200 (PC), < 100 (mobile)
Batches:             < 500 (PC), < 200 (mobile)
Overdraw:            < 3x (PC), < 1.5x (mobile)

RAM:                 < 4GB (PC), < 1.5GB (mobile), < 5GB (console)
VRAM:                < 2GB (PC), < 256MB (mobile)
GC Alloc/frame:      < 2KB (éviter les spikes)
```

---

## 2. Optimisation CPU

### Scripting — Réduire le Coût du Code

```csharp
// MAUVAIS: allocations dans Update()
void Update()
{
    // Alloue un new Vector3 à chaque frame
    transform.position = new Vector3(x, y, z);
    // Alloue une string
    Debug.Log("Position: " + transform.position);
}

// BON: pas d'allocations
private Vector3 _tempPos;
void Update()
{
    _tempPos.Set(x, y, z); // Set() ne crée pas de garbage
    transform.position = _tempPos;
}

// BON: string builder / string interpolation sans alloc
// (les versions Unity récentes optimisent l'interpolation)
```

### Object Pooling — Pattern Essentiel

```csharp
public class ObjectPool<T> where T : Component
{
    private Queue<T> _pool = new();
    private T _prefab;
    private Transform _parent;

    public ObjectPool(T prefab, int initialSize, Transform parent = null)
    {
        _prefab = prefab;
        _parent = parent;
        for (int i = 0; i < initialSize; i++)
        {
            var obj = CreateNew();
            obj.gameObject.SetActive(false);
            _pool.Enqueue(obj);
        }
    }

    public T Get()
    {
        if (_pool.Count == 0)
        {
            var obj = CreateNew();
            _pool.Enqueue(obj);
        }
        var instance = _pool.Dequeue();
        instance.gameObject.SetActive(true);
        return instance;
    }

    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        _pool.Enqueue(obj);
    }

    private T CreateNew()
    {
        var obj = Object.Instantiate(_prefab, _parent);
        obj.gameObject.name = _prefab.name + "_pooled";
        return obj;
    }
}

// Usage: balles, particules, ennemis, UI elements
private ObjectPool<Bullet> _bulletPool;

void Start()
{
    _bulletPool = new ObjectPool<Bullet>(bulletPrefab, 50);
}

void Fire()
{
    var bullet = _bulletPool.Get();
    bullet.transform.position = gunPoint.position;
    bullet.Fire(direction);
}

void OnBulletExpired(Bullet bullet)
{
    _bulletPool.Return(bullet);
}
```

### Burst Compiler et Job System (Unity)

```csharp
using Unity.Burst;
using Unity.Jobs;
using Unity.Collections;
using Unity.Mathematics;

// MAUVAIS: boucle en C# sur 10000 balles
void Update()
{
    for (int i = 0; i _bullets.Length; i++)
    {
        _bullets[i].Position += _bullets[i].Velocity * Time.deltaTime;
    }
}

// BON: Burst + Job System
[BurstCompile]
public struct UpdateBulletsJob : IJobParallelFor
{
    public NativeArray<float3> Positions;
    [ReadOnly] public NativeArray<float3> Velocities;
    public float DeltaTime;

    public void Execute(int index)
    {
        Positions[index] += Velocities[index] * DeltaTime;
    }
}

void Update()
{
    var job = new UpdateBulletsJob
    {
        Positions = _positions,
        Velocities = _velocities,
        DeltaTime = Time.deltaTime
    };
    var handle = job.Schedule(_positions.Length, 64); // batch 64
    handle.Complete(); // ou handle + autre travail
}
// Résultat: 10000 balles → ~0.01ms CPU (vs ~2ms en C# pur)
```

### SIMD (Vectorization)

```text
// Burst auto-vectorise les boucles simples
// Résultat: 4 floats traités en 1 instruction SIMD (SSE/AVX)

// Avant Burst: scalar loop → 4 instructions
// Après Burst: 1 SIMD instruction
// x4 à x8 plus rapide

// Toujours utiliser float3/float4 (Unity.Mathematics)
// pour que Burst puisse vectoriser
// Éviter les structures non-alignées
```

### IL2CPP — Stripping et AOT

```xml
<!-- Unity: PlayerSettings → Managed Stripping Level -->
<!-- Low    : 30% réduction, compatible -->
<!-- Medium : 50% réduction, test nécessaire -->
<!-- High   : 70% réduction, linker.xml requis -->

<!-- Linker.xml — Préserver les classes utilisées par reflection -->
<linker>
  <assembly fullname="Assembly-CSharp">
    <type fullname="MonNamespace.*" preserve="all" />
    <type fullname="Newtonsoft.Json.*" preserve="all" />
  </assembly>
</linker>

<!-- IL2CPP Code Generation:
     - Conversion C# → C++ → binary
     - AOT compilation (pas de JIT)
     - ~2x plus de code binaire
     - Meilleure perf, moins de GC
     - iOS/console obligatoire
-->
```

---

## 3. Optimisation GPU

### Draw Calls — Le Goulot #1

```text
Draw Call = commande au GPU pour dessiner un mesh
Chaque Draw Call = overhead CPU (validation, state change)

COÛT D'UN DRAW CALL:
- Unity: ~0.1-0.5ms CPU par DC
- Cible: < 500 DC sur mobile, < 2000 sur PC

SOLUTIONS:
1. Static Batching  → fusionne les meshes statiques (Unity)
2. GPU Instancing   → un Draw Call pour N instances
3. SRP Batcher      → batch les matériaux compatibles (URP/HDRP)
4. Dynamic Batching → fusionne les petits meshes dynamiques
5. Texture Atlas    → moins de matériaux = moins de DC
```

### GPU Instancing (Unity)

```csharp
// MAUVAIS: 1000 game objects individuels = 1000 draw calls
// BON: GPU Instancing (MaterialPropertyBlock)

public class InstancedRenderer : MonoBehaviour
{
    public Mesh mesh;
    public Material material;
    public int instanceCount = 10000;

    private Matrix4x4[] _matrices;
    private MaterialPropertyBlock _props;

    void Start()
    {
        _matrices = new Matrix4x4[instanceCount];
        _props = new MaterialPropertyBlock();

        // Générer les positions aléatoires
        for (int i = 0; i < instanceCount; i++)
        {
            _matrices[i] = Matrix4x4.TRS(
                Random.insideUnitSphere * 100f,
                Quaternion.identity,
                Vector3.one
            );
        }

        // Couleur unique par instance via per-instance data
        var colors = new Vector4[instanceCount];
        for (int i = 0; i < instanceCount; i++)
            colors[i] = Random.ColorHSV();
        _props.SetVectorArray("_Color", colors);
    }

    void Update()
    {
        // Un SEUL draw call pour 10000 instances
        Graphics.DrawMeshInstanced(mesh, 0, material, _matrices, instanceCount, _props);
    }
}
```

### SRP Batcher (Unity URP/HDRP)

```text
SRP Batcher: regroupe les Draw Calls partageant le MÊME shader

CONDITIONS:
1. Tous les matériaux utilisent le même shader
2. Pas de MaterialPropertyBlock (préférer per-object data)
3. Pas de shader avec #pragma multi_compile complexes

AVANT: 100 matériaux → 100 draw calls (même shader)
APRÈS SRP Batcher: 100 matériaux → 3-4 batches → ~95% réduction
```

### Occlusion Culling

```csharp
// Unity: Window → Rendering → Occlusion Culling
// 1. Marquer les objets comme Occluder Static / Occludee Static
// 2. Bake → génère un volume qui cache les objets derrière les murs

// GODOT: VisibilityNotifier + Room system
// Utiliser des Portals pour les espaces intérieurs

// UNREAL: Precomputed Visibility Volume (PVV)
// Automatiquement baked dans World Partition
```

### LOD (Level of Detail)

```csharp
// Unity — LOD Group Component
public class LODSetup : MonoBehaviour
{
    void Start()
    {
        var lodGroup = gameObject.AddComponent<LODGroup>();
        var renderers = GetComponentsInChildren<Renderer>();

        // 3 niveaux de détail
        LOD[] lods = new LOD[3];

        // LOD 0: Mesh haute qualité (0-30m)
        lods[0] = new LOD(0.3f, new[] { renderers[0] });
        // LOD 1: Mesh moyen (30-60m)
        lods[1] = new LOD(0.1f, new[] { renderers[1] });
        // LOD 2: Mesh bas (60-100m)
        lods[2] = new LOD(0.01f, new[] { renderers[2] });

        lodGroup.SetLODs(lods);
        lodGroup.RecalculateBounds();
    }
}

// Alternative: LOD via scripts (pour du procédural)
// - Distance < 20m → full detail
// - 20-50m → skip normal maps, reduce shadow
// - 50-100m → low poly impostor
// - > 100m → billboard sprite
```

### Texture Streaming et Mip Maps

```text
Textures:
- Toujours générer des Mip Maps → le GPU charge la résolution adaptée
- Max texture size: 2048 (mobile), 4096 (PC) pour les textures de base
- Format: ASTC (mobile), BC7/BC3 (PC), PVRTC (iOS legacy)
- Texture Atlas: regrouper les textures pour réduire les matériaux

Texture Streaming Pool:
- Unity: QualitySettings.streamingMipmapsActive = true
- Unreal: r.Streaming.PoolSize (en MB)
- Limiter la RAM texture: 256MB (mobile), 1GB (PC)

Budget Texture par plateforme:
Mobile:  256MB textures, 512MB total RAM
PC Low:  512MB textures, 2GB total RAM
PC High: 2GB textures, 8GB total RAM
```

---

## 4. Optimisation Mémoire

### Garbage Collection (GC) — Le Tueur de Framerate

```csharp
// MAUVAIS: GC spikes
void Update()
{
    // Allocation → GC va devoir collecter
    var list = new List<int>();
    for (int i = 0; i < 100; i++)
        list.Add(i);

    // Boxing → allocation heap
    object boxed = 42;
}

// BON: Pooling et structs

// Pool de listes
private static ObjectPool<List<int>> _listPool = new(() => new List<int>(100));

void Update()
{
    var list = _listPool.Get();
    for (int i = 0; i < 100; i++)
        list.Add(i);

    // Traiter...
    list.Clear();
    _listPool.Return(list);
}

// Éviter le boxing: utiliser des structs génériques, pas des objets
// Éviter params[]: créer des overloads explicites
// Éviter les closures: stocker les variables dans des fields
// Éviter LINQ: foreach > .Select().Where().ToList()
```

### Addressables et Asset Bundles

```csharp
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

public class AssetManager : MonoBehaviour
{
    // Chargement asynchrone avec cache
    private Dictionary<string, AsyncOperationHandle> _loadedAssets = new();

    public async void LoadAsset<T>(string key, System.Action<T> callback) where T : UnityEngine.Object
    {
        if (_loadedAssets.TryGetValue(key, out var existingHandle))
        {
            callback(existingHandle.Result as T);
            return;
        }

        var handle = Addressables.LoadAssetAsync<T>(key);
        await handle.Task;

        if (handle.Status == AsyncOperationStatus.Succeeded)
        {
            _loadedAssets[key] = handle;
            callback(handle.Result);
        }
    }

    public void UnloadAsset(string key)
    {
        if (_loadedAssets.TryGetValue(key, out var handle))
        {
            Addressables.Release(handle);
            _loadedAssets.Remove(key);
        }
    }

    // Nettoyage global
    void OnDestroy()
    {
        foreach (var kvp in _loadedAssets)
            Addressables.Release(kvp.Value);
        _loadedAssets.Clear();
    }
}

// Asset Budget:
// - UI: charger tout au début (permanent)
// - Personnages: charger par niveau, Addressables groups
// - Sons: streaming pour musique, pool pour SFX
// - Textures: mipmap streaming
```

---

## 5. Optimisation Mobile

```text
CHECKLIST MOBILE (Android/iOS):
☐ URP avec qualité "Low" ou "Medium"
☐ Max 1 lumière directionnelle réelle
☐ Pas de shadow realtime (sauf pour le joueur)
☐ Ombres: hard shadows seulement, distance < 20m
☐ Post-process: bloom désactivé, pas de DOF, pas de motion blur
☐ LOD distance: moitié de celle du PC
☐ Textures: max 2048, format ASTC 6x6
☐ Audio: ADPCM ou Vorbis 64kbps
☐ Target 30fps (ou 60 si très simple)
☐ V-Sync: activé (évite le tearing, économise batterie)
☐ Fillrate: réduire la résolution de rendu (renderScale 0.7-0.8)
☐ Object pool: TOUT ce qui est instancié/détruit
☐ GC: appel manuel aux moments calmes (fin de niveau)
☐ Batching: priorité sur les draw calls
☐ Physics: timestep 30Hz au lieu de 60Hz
```

---

## 6. Optimisation VR

```text
CHECKLIST VR (Quest/PCVR):
☐ Single-pass instanced rendering (2 eyes = 1 draw call)
☐ Target 72/90/120fps fixe (sous peine de motion sickness)
☐ Pas de post-process lourd (bloom, SSAO, SSR)
☐ Resolution scale: 0.8-1.0 (en dessous de 1.0 = upscaling)
☐ MSAA x2 maximum (x4 trop coûteux)
☐ Pas de real-time shadows (préférer baked)
☐ LOD très agressif (les objets sont vus de près)
☐ Fixed Foveated Rendering (Quest)
☐ Pas de transparent sorting complexe
☐ Application SpaceWarp (ASW) si FPS < target
☐ Audio spatialisé: Oculus Audio SDK
```

---

## 7. Profiling Commands Rapides

```bash
# Unity Profiler shortcuts
Window → Analysis → Profiler
Window → Analysis → Frame Debugger
Window → Rendering → Occlusion Culling
Ctrl+Shift+Stats → Rendered stats overlay

# Unreal Console Commands
stat fps           # Framerate
stat unit          # Frame time breakdown
stat gpu           # GPU timings
r.ScreenPercentage 100  # Resolution scale
r.Streaming.PoolSize 500 # Texture pool (MB)
foliage.DensityScale 0.5
r.ShadowQuality 3
r.Lumen.Reflections.Enable 0
r.Nanite 1

# Godot Monitor
Debugger → Monitors
rendering/quality/driver/driver_name opengl3
rendering/quality/shader_compilation/async_shader_compilation_enabled true
physics/common/physics_ticks_per_second 30
```

---

## 8. Pièges Courants

- **Optimiser sans profiler** → on optimise ce qui n'est pas le problème. Toujours profiler d'abord.
- **Trop d'objets individuels** → 10000 GameObjects = 10000 draw calls = 10000 transform syncs. GPU Instancing ou ECS.
- **GC spikes toutes les 30s** → allocation puis collecte. Object pool + éviter les allocs.
- **Textures 4K partout** → 1 texture 4K = 64MB. 50 textures = 3.2GB VRAM. Toujours mipmap + compression.
- **Physics tick à 60Hz inutile** → 30Hz suffit pour 90% des jeux. Divise par 2 le CPU physics.
- **Canvas rebuild permanent** → UI qui change chaque frame = rebuild du mesh UI complet. Marquer comme static.
- **FindObjectOfType dans Update** → GC + search. Cacher les références une fois dans Start().
- **Oubli du Object Pooling** → Instancier/détruire 100 balles par seconde = GC spike garanti.
- **Pas de stripping IL2CPP** → Build 200MB au lieu de 80MB. Toujours High stripping + linker.xml.
- **Draw calls ignorés** → 3000 DC parce que chaque objet a son matériau. Texture atlas + material instancing.