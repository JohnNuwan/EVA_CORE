---
name: unity-game-engine
description: Guide complet du moteur Unity (C#) — scripting, ECS/DOTS, ShaderGraph, optimisation, pipeline de rendu URP/HDRP, build multiplateforme.
---

# Unity Game Engine — Guide Complet

Ce skill couvre le développement avec Unity, de la configuration de projet au déploiement multiplateforme. À charger pour toute tâche impliquant Unity, C# pour jeux, ou pipelines de rendu Unity.

---

## 1. Structure du Projet Unity

```
MonJeu/
├── Assets/
│   ├── Scripts/          # Scripts C# (MonoBehaviour, ScriptableObject)
│   ├── Prefabs/          # Prefabs réutilisables
│   ├── Scenes/           # Scènes .unity
│   ├── Resources/        # Ressources chargées via Resources.Load()
│   ├── Shaders/          # Shaders HLSL/ShaderGraph (.shadergraph)
│   ├── Materials/        # Matériaux et presets
│   ├── Sprites/Textures/ # Assets visuels
│   ├── Models/           # Modèles 3D FBX/glTF
│   ├── Audio/            # Sons et musiques
│   ├── Animations/       # Animations .anim et contrôleurs
│   ├── AddressableAssets/ # Assets adressables (AA)
│   └── Editor/           # Scripts d'éditeur (custom inspectors, tools)
├── Packages/             # Packages Unity (manifest.json)
├── ProjectSettings/      # Paramètres du projet
└── UserSettings/         # Préférences locales (ignorer .gitignore)
```

### .gitignore Unity standard
```
[Ll]ibrary/
[Tt]emp/
[Oo]bj/
[Bb]uild/
[Bb]uilds/
[Ll]ogs/
[Uu]ser[Ss]ettings/
*.csproj
*.sln
```

---

## 2. Scripting C# — Patterns Essentiels

### MonoBehaviour de base

```csharp
using UnityEngine;

public class Joueur : MonoBehaviour
{
    [Header("Paramètres de mouvement")]
    [SerializeField] private float _vitesse = 5f;
    [SerializeField] private float _forceSaut = 10f;

    private Rigidbody _rb;
    private bool _estAuSol;

    private void Awake()
    {
        _rb = GetComponent<Rigidbody>();
    }

    private void Update()
    {
        float horizontal = Input.GetAxis("Horizontal");
        float vertical = Input.GetAxis("Vertical");

        Vector3 direction = (transform.right * horizontal + transform.forward * vertical).normalized;
        _rb.velocity = new Vector3(direction.x * _vitesse, _rb.velocity.y, direction.z * _vitesse);
    }

    public void Sauter()
    {
        if (_estAuSol)
        {
            _rb.AddForce(Vector3.up * _forceSaut, ForceMode.Impulse);
            _estAuSol = false;
        }
    }
}
```

### ScriptableObject — Configuration de jeu

```csharp
using UnityEngine;

[CreateAssetMenu(fileName = "NouvelObjet", menuName = "Jeu/Objet")]
public class ObjetJeu : ScriptableObject
{
    public string NomObjet;
    [TextArea(3, 5)] public string Description;
    public Sprite Icone;
    public int Prix;
    public GameObject Prefab;
}
```

### Coroutines et Async

```csharp
// Coroutine
private IEnumerator AttendreEtAction(float delai)
{
    yield return new WaitForSeconds(delai);
    FaireAction();
}

// Async/Await avec UniTask (package)
private async UniTask ChargerDonneesAsync()
{
    var resultat = await API.ChargerAsync("url");
    AppliquerDonnees(resultat);
}
```

---

## 3. Pipeline de Rendu — URP vs HDRP

| Critère | URP (Universal Render Pipeline) | HDRP (High Definition RP) |
|---------|-------------------------------|---------------------------|
| Usage | Mobile, VR, cross-platform | PC, Console, AAA |
| Perf | Optimisé basse/moyenne | Qualité max, coût élevé |
| Shaders | ShaderGraph + Lit simple | Lit complexe, SSS, volumétrie |
| Post-process | Intégré léger | Full post-process HDR |

### URP — Shader personnalisé

```hlsl
// Assets/Shaders/MonShader.shader
Shader "Custom/MonShader"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _Couleur ("Couleur", Color) = (1,1,1,1)
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

            struct Attributes { float4 positionOS : POSITION; float2 uv : TEXCOORD0; };
            struct Varyings { float4 positionCS : SV_POSITION; float2 uv : TEXCOORD0; };

            TEXTURE2D(_MainTex); SAMPLER(sampler_MainTex);
            float4 _MainTex_ST;
            float4 _Couleur;

            Varyings vert(Attributes input)
            {
                Varyings output;
                output.positionCS = TransformObjectToHClip(input.positionOS.xyz);
                output.uv = TRANSFORM_TEX(input.uv, _MainTex);
                return output;
            }

            float4 frag(Varyings input) : SV_Target
            {
                float4 tex = SAMPLE_TEXTURE2D(_MainTex, sampler_MainTex, input.uv);
                return tex * _Couleur;
            }
            ENDHLSL
        }
    }
}
```

---

## 4. ECS/DOTS (Entity Component System)

```csharp
using Unity.Entities;
using Unity.Transforms;
using Unity.Mathematics;

// Component
public struct Deplacement : IComponentData
{
    public float3 Direction;
    public float Vitesse;
}

// System (Job + Burst Compiler)
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial struct DeplacementSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        float deltaTime = SystemAPI.Time.DeltaTime;

        new DeplacementJob { DeltaTime = deltaTime }.ScheduleParallel();
    }
}

[BurstCompile]
public partial struct DeplacementJob : IJobEntity
{
    public float DeltaTime;

    void Execute(ref LocalTransform transform, in Deplacement deplacement)
    {
        transform.Position += deplacement.Direction * deplacement.Vitesse * DeltaTime;
    }
}
```

---

## 5. Addressables et Gestion Mémoire

```csharp
using UnityEngine.AddressableAssets;
using UnityEngine.ResourceManagement.AsyncOperations;

public class GestionnaireRessources : MonoBehaviour
{
    public async void ChargerPersonnage(string cle)
    {
        AsyncOperationHandle<GameObject> handle = Addressables.LoadAssetAsync<GameObject>(cle);
        await handle.Task;

        if (handle.Status == AsyncOperationStatus.Succeeded)
        {
            GameObject personnage = handle.Result;
            Instantiate(personnage);
        }
        else
        {
            Debug.LogError($"Échec chargement {cle}: {handle.OperationException}");
        }
    }
}
```

---

## 6. Build et Déploiement Multiplateforme

```bash
# Ligne de commande Unity (headless pour CI/CD)
/chemin/vers/Unity -quit -batchmode \
    -buildTarget StandaloneLinux64 \
    -projectPath /chemin/projet \
    -buildLinux64Player ./Build/MonJeu.x86_64

# Options de build
# -buildTarget: StandaloneWindows64, StandaloneLinux64, iOS, Android, WebGL
# -executeMethod: Méthode C# d'éditeur à exécuter (build custom)
```

### PlayerSettings optimaux (PC)

```csharp
// Via script d'éditeur
PlayerSettings.SetScriptingBackend(BuildTargetGroup.Standalone, ScriptingImplementation.IL2CPP);
PlayerSettings.SetManagedStrippingLevel(BuildTargetGroup.Standalone, ManagedStrippingLevel.High);
PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
QualitySettings.SetQualityLevel(QualitySettings.names.Length - 1); // Ultra
```

---

## 7. Optimisation

- **Stats de rendu** : Stats Window (Ctrl+Shift+Stats) → Batching, Tris, Verts
- **Profiler** : Window → Analysis → Profiler (CPU/GPU/Memory)
- **Frame Debugger** : Window → Analysis → Frame Debugger (draw calls individuelles)
- **Occlusion Culling** : Window → Rendering → Occlusion Culling → Bake
- **LOD Group** : Ajouter LODGroup component pour 3 niveaux de détail
- **GPU Instancing** : Cocher "Enable GPU Instancing" dans les matériaux
- **Texture Atlas** : Sprite Atlas pour regrouper les sprites

### Checklist perf mobile
1. URP avec qualité "Low" ou "Medium"
2. Limiter les lumières réelles (max 1-2 dynamiques)
3. Pas de post-process lourd (bloom, DOF)
4. LOD pour tous les modèles > 1000 tris
5. Object pool pour projectiles/ennemis
6. Pas de GC allocations dans Update() (pooling de structs)

---

## 8. Pièges Courants

- **Resources.Load() déconseillé** : préférer Addressables ou references directes
- **Find/FindObjectOfType lents** : cacher les references via [SerializeField] ou singleton
- **PhysX à 60+ FPS** : FixedUpdate() pour la physique, Update() pour l'input
- **Strings en serialization** : préférer des enums ou ScriptableObject IDs
- **Animator.SetTrigger()** : Reset manuel nécessaire en cas de réentrée d'état
- **Build IL2CPP lent** : incrémental via "Incremental GC" + "Fast Script Reload" en dev
