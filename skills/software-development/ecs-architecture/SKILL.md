---
name: ecs-architecture
description: Architecture Entity Component System (ECS/DOTS) — Unity Entities 1.0, Flecs, EnTT, Bevy ECS, data-oriented design, Job System, Burst Compiler, archetypes, systèmes de requête et optimisation cache CPU.
tags: [ecs, dots, unity, flecs, entt, bevy, data-oriented-design, burst, job-system]
---

# ECS Architecture — Guide Complet

Ce skill couvre l'architecture Entity Component System (ECS) et le Data-Oriented Design (DOD) pour le développement de jeux. À charger pour toute tâche impliquant Unity DOTS, Flecs, EnTT, Bevy ECS, ou la conception orientée données.

---

## 1. Principes Fondamentaux du Data-Oriented Design

### Problème de l'OOP classique

```text
OOP (Objet):  Player { Transform, Rigidbody, Health, MeshRenderer, Collider }
              → Mémoire dispersée (cache misses)
              → Virtual table overhead
              → Difficulté de parallélisation

ECS (Données): Position[]  (tableau contigu)
               Velocity[]  (tableau contigu)
               Health[]    (tableau contigu)
               → Cache CPU friendly (SoA)
               → Pas de vtable
               → Parallélisable trivialement
```

### AoS vs SoA

```text
AoS (Array of Structs)        | SoA (Struct of Arrays)
struct Particle {             | struct ParticleSystem {
    float3 pos;               |     float3* positions;
    float3 vel;               |     float3* velocities;
    float life;               |     float* lifetimes;
    float mass;               |     float* masses;
};                            | };
                              |
Cache miss élevé si on ne     | Cache friendly: on lit/écrit
lit que la position           | SEULEMENT ce dont on a besoin
```

### Itérration chaude vs froide

```csharp
// CHAUD (hot path) — ce qui tourne à 60+ FPS
// - Positions, velocities, transformations
// - Collision detection (AABB)
// - Animation blend

// FROID (cold path) — ce qui arrive rarement
// - Health, death, respawn
// - UI events
// - Pathfinding (A*)
// - Network events
```

Séparer les données chaudes des données froides = principe clé du DOD.

---

## 2. Unity DOTS (Entities 1.0)

### Architecture DOTS

```text
World
├── EntityManager      # Crée/détruit des entités, ajoute/retire des components
├── EntityCommandBuffer # File les changements structuraux (playback différé)
├── SystemState        # Lifecycle des systèmes
└── EntityQuery        # Requêtes sur les composants
    └── Archetype      # Groupe d'entités avec les MÊMES types de composants
        ├── Chunk      # Bloc mémoire contigu (16KB = ArchetypeChunk)
        │   ├── EntityA → Position, Velocity, Health
        │   ├── EntityB → Position, Velocity, Health
        │   └── ...     (max 128 entités par chunk)
        └── ...
```

### Component Data (IComponentData)

```csharp
using Unity.Entities;

// Composant basique — 8 bytes alignés, pas de référence managed
public struct Position : IComponentData
{
    public float3 Value;
}

public struct Velocity : IComponentData
{
    public float3 Value;
}

// Tag component — zéro byte, sert de marqueur
public struct JoueurTag : IComponentData { }

// Shared component — partagé entre entités du même chunk
// Change quand la valeur change (structural change)
public struct Equipe : ISharedComponentData
{
    public int Valeur; // 0 = rouge, 1 = bleue
}

// Buffer component — tableau dynamique sur une entité
[InternalBufferCapacity(8)] // Capacité initiale inline dans le chunk
public struct WaypointBuffer : IBufferElementData
{
    public float3 Position;
}

// Enableable component — peut être activé/désactivé sans structural change
// (Entités 1.0+)
public struct EnableableTag : IComponentData, IEnableableComponent { }

// Cleanup component — callback automatique à la destruction
public struct CleanupTag : ICleanupComponentData { }
```

### Création d'Entité et Archétypes

```csharp
using Unity.Entities;
using Unity.Transforms;

public partial class GameInitializationSystem : SystemBase
{
    protected override void OnUpdate()
    {
        // NE PAS créer d'entités dans OnUpdate — utiliser ECB
        // Ceci est un exemple conceptuel
        EntityManager entityManager = World.EntityManager;

        // Création simple
        Entity player = entityManager.CreateEntity(
            typeof(LocalTransform),
            typeof(Velocity),
            typeof(JoueurTag)
        );

        // Avec valeurs initiales
        entityManager.SetComponentData(player, new LocalTransform
        {
            Position = float3.zero,
            Rotation = quaternion.identity,
            Scale = 1f
        });
        entityManager.SetComponentData(player, new Velocity
        {
            Value = new float3(0, 0, 5)
        });

        // Création batch (optimisé)
        // Plusieurs entités du MÊME archétype = 1 allocation
        var archetype = entityManager.CreateArchetype(
            typeof(LocalTransform),
            typeof(Velocity)
        );

        NativeArray<Entity> entities = entityManager.CreateEntity(archetype, 10000,
            Allocator.Temp);
        // Définir les valeurs via requête ensuite
    }
}
```

### EntityCommandBuffer (ECB) — Le Pattern Standard

```csharp
// NE JAMAIS faire de structural changes dans un système en cours d'exécution
// Toujours utiliser EntityCommandBuffer

public partial struct WeaponSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        // Créer un ECB pour ce système (ou par thread)
        EntityCommandBuffer ecb = new EntityCommandBuffer(Allocator.Temp);

        foreach (var (bullet, entity) in SystemAPI.Query<BulletComponent>().WithEntityAccess())
        {
            if (bullet.Destroyed)
            {
                ecb.DestroyEntity(entity); // Structural change différé
            }
        }

        // Jouer l'ECB immédiatement — les changements s'appliquent ici
        // Alternative: utiliser un ECBSystem pour le jouer en fin de frame
        state.EntityManager.DestroyEntity(ecb);
        // ATTENTION: ne PAS utiliser l'ECB après l'avoir passé à DestroyEntity
    }
}

// MÉTHODE RECOMMANDÉE: ECB System avec fin de groupe
[UpdateInGroup(typeof(SimulationSystemGroup))]
[UpdateAfter(typeof(WeaponSystem))]
public partial struct WeaponEcbSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        var ecbSingleton = SystemAPI.GetSingleton<BeginSimulationEntityCommandBufferSystem.Singleton>();
        var ecb = ecbSingleton.CreateCommandBuffer(state.WorldUnmanaged);

        // Utiliser ecb dans les jobs — thread-safe
        // Joué automatiquement en fin de groupe
    }
}
```

### System Types and Lifecycle

```csharp
using Unity.Entities;
using Unity.Burst;

// 1. ISystem — Moderne (recommandé)
// Value type, pas d'allocation, Burst-compatible
[BurstCompile]
public partial struct MovementSystem : ISystem
{
    // Requête stockée pour éviter la recréation
    private EntityQuery _query;

    [BurstCompile]
    public void OnCreate(ref SystemState state)
    {
        _query = state.GetEntityQuery(
            ComponentType.ReadWrite<LocalTransform>(),
            ComponentType.ReadOnly<Velocity>()
        );
    }

    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        float dt = SystemAPI.Time.DeltaTime;

        // Version simple
        foreach (var (transform, velocity) in
                 SystemAPI.Query<RefRW<LocalTransform>, RefRO<Velocity>>())
        {
            transform.ValueRW.Position += velocity.ValueRO.Value * dt;
        }
    }

    [BurstCompile]
    public void OnDestroy(ref SystemState state) { }
}

// 2. SystemBase — Héritage (legacy, moins performant)
public partial class LegacyMovementSystem : SystemBase
{
    protected override void OnUpdate()
    {
        float dt = SystemAPI.Time.DeltaTime;

        Entities.ForEach((ref LocalTransform transform, in Velocity velocity) =>
        {
            transform.Position += velocity.Value * dt;
        }).Schedule();
    }
}

// 3. Aspects
public readonly partial struct MovementAspect : IAspect
{
    public readonly Entity Self;
    readonly RefRW<LocalTransform> Transform;
    readonly RefRO<Velocity> Velocity;
    readonly RefRO<JoueurTag> Tag; // Optionnel

    public void Move(float dt)
    {
        Transform.ValueRW.Position += Velocity.ValueRO.Value * dt;
    }
}

// Système avec Aspect
[BurstCompile]
public partial struct MovementAspectSystem : ISystem
{
    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        float dt = SystemAPI.Time.DeltaTime;
        foreach (var aspect in SystemAPI.Query<MovementAspect>())
        {
            aspect.Move(dt);
        }
    }
}
```

### EntityQuery — Requêtes Avancées

```csharp
[BurstCompile]
public partial struct QueryExampleSystem : ISystem
{
    private EntityQuery _query;

    public void OnCreate(ref SystemState state)
    {
        _query = new EntityQueryBuilder(Allocator.Temp)
            .WithAll<LocalTransform, Velocity>()     // REQUIS
            .WithAny<JoueurTag, EnnemiTag>()          // AU MOINS UN
            .WithNone<DeadTag>()                      // EXCLU
            .WithOptions(EntityQueryOptions.IncludePrefab
                        | EntityQueryOptions.IncludeDisabledEntities)
            .Build(ref state);
    }

    [BurstCompile]
    public void OnUpdate(ref SystemState state)
    {
        var entities = _query.ToEntityArray(Allocator.TempJob);

        // Compter
        int count = _query.CalculateEntityCount();

        // Itération manuelle (pour calculs complexes)
        var chunks = _query.ToArchetypeChunkArray(Allocator.TempJob);
        foreach (var chunk in chunks)
        {
            var transforms = chunk.GetNativeArray<LocalTransform>(ref state
                .GetArchetypeChunkComponentType<LocalTransform>());
            // Traiter le chunk...
        }
    }
}
```

### Chunk Iteration — Bas Niveau

```csharp
[BurstCompile]
public struct ChunkIterationJob : IJobChunk
{
    [ReadOnly] public ComponentTypeHandle<Velocity> VelocityHandle;
    public ComponentTypeHandle<LocalTransform> TransformHandle;
    public float DeltaTime;

    public void Execute(in ArchetypeChunk chunk, int unfilteredIndex, bool useEnabledMask,
        in Unity.Entities.CodeGenerated.JobChunkJobSafetyCache safety)
    {
        var transforms = chunk.GetNativeArray(ref TransformHandle);
        var velocities = chunk.GetNativeArray(ref VelocityHandle);

        for (int i = 0; i < chunk.Count; i++)
        {
            transforms[i] = new LocalTransform
            {
                Position = transforms[i].Position + velocities[i].Value * DeltaTime,
                Rotation = transforms[i].Rotation,
                Scale = transforms[i].Scale
            };
        }
    }
}
```

### Bake et SubScenes

```csharp
using Unity.Entities;
using Unity.Baking;

// Baker — convertit un GameObject/MonoBehaviour en entités DOTS
public class CubeAuthoring : MonoBehaviour
{
    public float Vitesse = 5f;
    public float Direction = 1f;
}

public class CubeBaker : Baker<CubeAuthoring>
{
    public override void Bake(CubeAuthoring authoring)
    {
        DependsOn(authoring); // Re-bake si les valeurs changent

        var entity = GetEntity(TransformUsageFlags.Dynamic);

        AddComponent(entity, new Velocity
        {
            Value = new float3(authoring.Direction * authoring.Vitesse, 0, 0)
        });

        // Ajouter des composants supplémentaires
        AddComponent<JoueurTag>(entity);
    }
}

// Usage dans l'éditeur:
// 1. Créer un SubScene (GameObject → SubScene)
// 2. Mettre le GameObject avec CubeAuthoring DANS le SubScene
// 3. Le baking convertit automatiquement en entités
// 4. Les entités sont streamées au runtime
```

### Blob Assets — Données Immuables Partagées

```csharp
using Unity.Entities;

// Les Blob Assets sont des données partagées, immuables, alignées en mémoire
// Parfait pour: stats d'armes, données de quêtes, tables de damage

public struct ArmeStatBlob
{
    public float Degats;
    public float Portee;
    public float CadenceTir;
    public int MunitionsMax;
    public BlobArray<float> DegatsParDistance; // Tableau variable
}

public struct ArmeComponent : IComponentData
{
    public BlobAssetReference<ArmeStatBlob> Stats;
}

// Création d'un Blob Asset
public static BlobAssetReference<ArmeStatBlob> CreerStatsArme()
{
    var builder = new BlobBuilder(Allocator.Temp);
    ref var root = ref builder.ConstructRoot<ArmeStatBlob>();

    root.Degats = 50f;
    root.Portee = 100f;
    root.CadenceTir = 0.5f;
    root.MunitionsMax = 30;

    // Tableau variable
    var array = builder.Allocate(ref root.DegatsParDistance, 5);
    array[0] = 50f; array[1] = 40f; array[2] = 30f;
    array[3] = 20f; array[4] = 10f;

    var result = builder.CreateBlobAssetReference<ArmeStatBlob>(Allocator.Persistent);
    builder.Dispose();
    return result;
}

// Utilisation
var stats = armeComponent.Stats.Value;
float damage = stats.DegatsParDistance[(int)(distance / 20f)];
```

### System Groups et Ordre d'Exécution

```csharp
using Unity.Entities;

// Hiérarchie des groupes
// InitializationSystemGroup
//   ├── BeginInitializationEntityCommandBufferSystem
//   └── EndInitializationEntityCommandBufferSystem
// SimulationSystemGroup
//   ├── BeginSimulationEntityCommandBufferSystem
//   ├── FixedStepSimulationSystemGroup (physics à 50/60Hz)
//   └── EndSimulationEntityCommandBufferSystem
// PresentationSystemGroup
//   ├── BeginPresentationEntityCommandBufferSystem
//   └── LateSimulationSystemGroup

[UpdateInGroup(typeof(SimulationSystemGroup))]
[UpdateBefore(typeof(MovementSystem))]
[BurstCompile]
public partial struct InputSystem : ISystem { }

[UpdateInGroup(typeof(SimulationSystemGroup))]
[UpdateAfter(typeof(InputSystem))]
[BurstCompile]
public partial struct MovementSystem : ISystem { }

// Groupe personnalisé
[UpdateInGroup(typeof(SimulationSystemGroup))]
public partial struct CombatSystemGroup : ISystemGroup { }

[UpdateInGroup(typeof(CombatSystemGroup))]
public partial struct AttackSystem : ISystem { }

[UpdateInGroup(typeof(CombatSystemGroup))]
[UpdateAfter(typeof(AttackSystem))]
public partial struct DamageSystem : ISystem { }
```

---

## 3. Flecs (C/C++) — ECS Multiplateforme

Flecs est un ECS en C, avec bindings C++, Rust, Python, Lua, TypeScript. Très performant et riche.

```c
// Flecs — Composant et Système de base
typedef struct {
    float x, y, z;
} Position;

typedef struct {
    float x, y, z;
} Velocity;

// Enregistrement des composants
ECS_COMPONENT(world, Position);
ECS_COMPONENT(world, Velocity);

// Système
ECS_SYSTEM(world, MoveSystem, EcsOnUpdate, Position, Velocity);

void MoveSystem(ecs_iter_t *it) {
    Position *p = ecs_field(it, Position, 1);
    Velocity *v = ecs_field(it, Velocity, 2);

    for (int i = 0; i < it->count; i++) {
        p[i].x += v[i].x * it->delta_time;
        p[i].y += v[i].y * it->delta_time;
    }
}

// Création d'entité
ecs_entity_t e = ecs_new(world, Position);
ecs_set(world, e, Velocity, {5, 0, 0});

// Query fluide
ecs_query_t *q = ecs_query(world, {
    .filter.terms = {
        { .id = ecs_id(Position) },
        { .id = ecs_id(Velocity), .inout = EcsIn },
    }
});

// Flecs — Relations
// Les relations sont des paires (objet, sujet) — pas juste des tags
ECS_TAG(world, AmiDe);
ECS_TAG(world, Equipe);
ECS_TAG(world, PortePar);

ecs_add_pair(world, alice, AmiDe, bob);
ecs_add_pair(world, epee, PortePar, alice);

// Query avec relation
ecs_query(world, {
    .filter.terms = {
        { .id = ecs_pair(PortePar, EcsWildcard) } // Tout ce qui est porté
    }
});
```

---

## 4. EnTT (C++17) — ECS Header-Only

```cpp
#include <entt/entt.hpp>

struct Position {
    float x, y, z;
};
struct Velocity {
    float dx, dy, dz;
};
struct Health {
    int current, max;
};
struct DeadTag {};

int main() {
    entt::registry registry;

    // Création
    auto entity = registry.create();
    registry.emplace<Position>(entity, 0.f, 0.f, 0.f);
    registry.emplace<Velocity>(entity, 1.f, 0.f, 0.f);
    registry.emplace<Health>(entity, 100, 100);

    // Query + update
    auto view = registry.view<Position, Velocity>(entt::exclude<DeadTag>);
    view.each([](auto &pos, auto &vel) {
        pos.x += vel.dx;
        pos.y += vel.dy;
    });

    // Group (optimisé pour Itérration fréquente)
    auto group = registry.group<Position>(entt::get<Velocity>);

    // Events (signals)
    registry.on_construct<Health>().connect<&on_health_created>();
    registry.on_update<Position>().connect<&on_position_changed>();

    // Runtime components (utile pour scripting)
    auto type = registry.type("ComposantDynamique"_hs);

    // Snapshot pour serialisation / networking
    entt::snapshot{registry}
        .get<entt::entity>([](auto, auto &entity) { /* write */ })
        .get<Position>([](auto &pos) { /* write */ });
}
```

---

## 5. Bevy ECS (Rust)

```rust
use bevy::prelude::*;

#[derive(Component)]
struct Position(Vec3);

#[derive(Component)]
struct Velocity(Vec3);

#[derive(Component)]
struct Health {
    current: f32,
    max: f32,
}

#[derive(Component)]
struct Player;

// Système
fn movement_system(mut query: Query<(&mut Position, &Velocity)>, time: Res<Time>) {
    for (mut pos, vel) in query.iter_mut() {
        pos.0 += vel.0 * time.delta_seconds();
    }
}

// Système avec conditions
fn damage_system(
    mut commands: Commands,
    mut query: Query<(Entity, &mut Health)>,
    time: Res<Time>,
) {
    for (entity, mut health) in query.iter_mut() {
        health.current -= 10.0 * time.delta_seconds();
        if health.current <= 0.0 {
            commands.entity(entity).despawn();
        }
    }
}

// SystemSets pour l'ordre d'exécution
#[derive(SystemSet, Debug, Hash, PartialEq, Eq, Clone)]
enum GameSystem {
    Input,
    Movement,
    Combat,
    Render,
}

fn main() {
    App::new()
        .add_plugins(DefaultPlugins)
        .add_systems(Update,
            input_system.in_set(GameSystem::Input),
            movement_system.in_set(GameSystem::Movement).after(GameSystem::Input),
            damage_system.in_set(GameSystem::Combat).after(GameSystem::Movement),
        )
        .run();
}

// Query avancée
fn complex_query(
    // Tous les ennemis avec Position et Velocity, qui n'ont PAS Dead
    // ET qui ont AU MOINS Health > 0
    mut enemies: Query<(&mut Position, &Velocity), (
        With<Enemy>,
        Without<Dead>,
    )>,
) {}
```

---

## 6. Data-Oriented Design Patterns

### Component Design Patterns

```text
1. CHAUD (hot) — dans le path critique, itéré chaque frame
   LocalTransform, Velocity, AABB, AnimationBone

2. TIÈDE (warm) — itéré quelques fois par frame
   Health, Mana, ColliderRadius, Team

3. FROID (cold) — rarement accédé, souvent via lookup
   Name, Description, QuestFlags, DialogState
   → Mettre dans des Blob Assets ou des singletons
```

### Singleton Pattern (ECS)

```csharp
// ECS Singleton — UNE SEULE entité avec ce component
[BurstCompile]
public partial struct GameStateSystem : ISystem
{
    public void OnUpdate(ref SystemState state)
    {
        // GetSingleton est optimal pour les singletons
        var gameState = SystemAPI.GetSingleton<GameState>();
        var timeOfDay = SystemAPI.GetSingleton<TimeOfDay>();

        // SetSingleton
        SystemAPI.SetSingleton(new TimeOfDay { Value = timeOfDay.Value + 0.016f });
    }
}

// Créer le singleton
var singletonEntity = entityManager.CreateEntity(typeof(GameState));
entityManager.SetComponentData(singletonEntity, new GameState { ... });
```

### EntityCommandBuffer — Bonnes Pratiques

```csharp
// Mauvais: ECB parallèle sans précautions
var ecb = new EntityCommandBuffer(Allocator.Temp);

// Bon: ECB parallèle thread-safe
var ecb = new EntityCommandBuffer(Allocator.TempJob);
// OU: utiliser un EntityCommandBufferSystem existant
var ecbSystem = World.GetExistingSystemManaged<EndSimulationEntityCommandBufferSystem>();
var ecb = ecbSystem.CreateCommandBuffer();

// Parallèle: un ECB par thread, puis Playback séquentiel
var ecbs = new NativeArray<EntityCommandBuffer>(threadCount, Allocator.TempJob);
// Chaque job écrit dans ecbs[threadIndex]
// Puis:
foreach (var e in ecbs)
{
    state.EntityManager.DestroyEntity(e); // Playback sécurisé
}
```

---

## 7. Performance — Cache CPU et Optimisation

### Cache Line (64 bytes)

```text
Cache L1: 32KB   → ~512 positions (float3 × 4 = 16 bytes)
Cache L2: 256KB  → ~16000 positions
Cache L3: 8-32MB → ~1M positions

SoA Position[]: accès séquentiel → préfetcher CPU heureux → bande passante saturée
AoS Particle[]: accès dispersé → cache misses → starvation ALU
```

### Branch Prediction

```csharp
// Mauvais — branchement non prédictible
[BurstCompile]
public void OnUpdate(ref SystemState state)
{
    foreach (var (transform, health) in SystemAPI.Query<RefRW<LocalTransform>, Health>())
    {
        if (health.Value < 0.5f) // 50% de chance → mal prédit
        {
            transform.ValueRW.Scale *= 0.95f; // Branchement coûteux
        }
    }
}

// Mieux — séparer les entités par état (tag component)
// Entities avec DamagedTag dans un chunk séparé
foreach (var transform in SystemAPI.Query<RefRW<LocalTransform>>()
    .With<DamagedTag>())
{
    transform.ValueRW.Scale *= 0.95f; // Pas de branchement
}
```

### Structural Changes — Coût

```csharp
// COÛT d'un structural change (AddComponent, RemoveComponent, DestroyEntity)
// → L'entité change d'archétype
// → Memcpy de TOUS les composants vers un nouveau chunk
// → Invalide les références (NativeArray, Lookup)
// → Bloque les jobs en cours

// Limiter les structural changes:
// 1. Grouper par type
// 2. Utiliser EnableableComponent (Entités 1.0+) pour activer/désactiver
// 3. Pooling d'entités (CreateEntity + AddComponent une fois, puis Enable)
// 4. Tamponner dans un ECB et jouer une fois par frame

// Enableable → pas de structural change !
entityManager.SetComponentEnabled<DisabledTag>(entity, false); // Pas cher
// Au lieu de:
entityManager.RemoveComponent<DisabledTag>(entity); // Cher (structural change)
```

---

## 8. Pièges Courants

- **Structural changes dans Update()** → plantage (thread safety). Toujours utiliser ECB.
- **Lookup<T> périmé** → invalide après structural change. Recréer après chaque ECB Playback.
- **Trop de composants par entité** → archétype fragmenté (peu d'entités par chunk = gaspillage mémoire). Maximum ~20 composants.
- **Shared Components avec valeurs trop diverses** → fragmentation des chunks.
- **Burst pas activé** → `[BurstCompile]` oublié sur ISystem → perte de perf × 10.
- **Allocation mémoire dans les jobs** → utiliser `Allocator.TempJob` et disposer.
- **Changement de world** → ne pas mélanger des Entity de Worlds différents.
- **Blob Assets oubliés** → memory leak si `Dispose()` pas appelé.
- **Hybrid Mono en production** → un composant managed = pas de Burst = goulot.