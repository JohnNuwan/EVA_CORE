---
name: physics-engines
description: Moteurs physiques pour jeux vidéo — collision detection (AABB, SAT, GJK, CCD), rigidbodies, joints, constraints, character controllers, soft bodies, raycasts, moteurs (PhysX, Havok, Jolt, Box2D, Bullet, Godot Physics, Rapier).
tags: [physics, collision-detection, rigidbody, joints, constraints, physx, havok, jolt, box2d, bullet, godot-physics, rapi-er]
---

# Physics Engines — Guide Complet

Ce skill couvre la conception et l'utilisation de moteurs physiques pour jeux vidéo, de la détection de collision aux contraintes avancées. À charger pour toute tâche impliquant la physique de jeu (collisions, ragdolls, véhicules, destruction).

---

## 1. Moteurs Physiques — Comparaison

| Moteur | Langage | Usage | Particularité |
|--------|---------|-------|---------------|
| **PhysX 4/5** | C++ | Unity, UE4/5 (jusqu'à 5.3) | Standard industrie, GPU Flex |
| **Jolt** | C++ | Horizon FW, Godot 4 | Bon multithreading, déterminisme |
| **Havok** | C++ | Halo, Battlefield, Skyrim | Legacy, racheté par Microsoft |
| **Bullet** | C++ | GTA V, Blender | Open source, pybullet |
| **Box2D** | C++ | Angry Birds, Limbo | 2D uniquement, très stable |
| **Box2D (Godot)** | C++ | Godot 4 | Fork Godot du Box2D |
| **Rapier** | Rust | Bevy ECS | Moderne, WASM, déterministe |
| **Chipmunk** | C | 2D jeux indie | Léger, simple |

---

## 2. Collision Detection

### Broadphase — Quels objets sont proches?

```text
Broadphase: élimine rapidement les paires impossibles
Coût: O(n log n) ou O(n)

Sweep and Prune (SAP):
1. Trier les AABB sur l'axe X
2. Balayer: si deux AABB se chevauchent → Narrowphase
3. Incrémental: réinsérer les AABB qui bougent

Spatial Hash:
1. Grille de cellules (taille = diamètre max des objets)
2. Chaque objet va dans sa cellule + 8 voisines
3. Tester collision seulement dans la même cellule

BVH (Bounding Volume Hierarchy):
- Arbre binaire d'AABB
- O(log n) pour trouver les collisions
- Utilisé par PhysX, Bullet, Jolt

Multi-SAP (PhysX 5):
- SAP par axe
- Parallélisé par thread
```

### Narrowphase — Forme précise contre forme

```text
AABB vs AABB:      6 comparaisons (min/max x,y,z)
Sphere vs Sphere:  1 distance check
Capsule vs Capsule: distance entre segments + rayons
OBB vs OBB:        SAT (Separating Axis Theorem) → 15 axes max
Convex vs Convex:  GJK (Gilbert-Johnson-Keerthi) + EPA
Mesh vs anything:  BVH traversal + triangle intersection
```

### AABB Collision — La Plus Rapide

```csharp
// Unity — AABB test
public struct AABB
{
    public Vector3 Center;
    public Vector3 HalfExtents;

    public bool Overlaps(AABB other)
    {
        Vector3 d = other.Center - Center;
        return Mathf.Abs(d.x) <= HalfExtents.x + other.HalfExtents.x &&
               Mathf.Abs(d.y) <= HalfExtents.y + other.HalfExtents.y &&
               Mathf.Abs(d.z) <= HalfExtents.z + other.HalfExtents.z;
    }
}
```

### SAT (Separating Axis Theorem) — OBB vs OBB

```csharp
public static bool OBBCollision(Vector3[] axesA, Vector3[] axesB,
                                 float[] projA, float[] projB)
{
    // Tester 15 axes: 3 axes de A + 3 axes de B + 9 cross products
    // Si on trouve UN axe de séparation → pas de collision
    foreach (var axis in GetAllAxes(axesA, axesB))
    {
        float minA, maxA, minB, maxB;
        ProjectOntoAxis(verticesA, axis, out minA, out maxA);
        ProjectOntoAxis(verticesB, axis, out minB, out maxB);

        if (maxA < minB || maxB < minA)
            return false; // Axe de séparation trouvé
    }
    return true; // Tous les axes se chevauchent
}
```

### GJK (Gilbert-Johnson-Keerthi) — Convex vs Convex

```text
GJK: Algorithme itératif qui détermine si deux convexes se touchent

1. Prendre un point de départ (somme des centres)
2. Construire un simplex (tétraèdre en 3D, triangle en 2D)
3. Chercher dans la direction vers l'origine
4. Si l'origine est DANS le simplex → collision
5. Si le simplex ne peut pas s'approcher → pas de collision

Avantages:
- Supporte TOUTES les formes convexes
- Complexité presque O(1)
- Combine avec EPA pour la profondeur de pénétration
```

### CCD (Continuous Collision Detection)

```csharp
// Problème: objet rapide traverse une fine paroi en 1 frame
// Solution: CCD

using UnityEngine;

public class CCDSetup : MonoBehaviour
{
    public Rigidbody rb;

    void Start()
    {
        // Unity — activation du CCD
        rb.collisionDetectionMode = CollisionDetectionMode.Continuous;

        // Continuous: CCD pour les collisions avec des static meshes
        // ContinuousDynamic: CCD pour collisions avec d'autres CCD
        // ContinuousSpeculative: prédiction + balayage (plus lent)
    }
}

// CCD manuel (sweep test)
public class ManualCCD : MonoBehaviour
{
    public float speed = 50f;

    void FixedUpdate()
    {
        Vector3 movement = transform.forward * speed * Time.fixedDeltaTime;
        float distance = movement.magnitude;

        // Sweep test: avancer par pas
        if (Physics.BoxCast(transform.position, _halfExtents,
            movement.normalized, out RaycastHit hit, transform.rotation, distance))
        {
            // S'arrêter au point de contact
            transform.position += movement.normalized * hit.distance;
            // Appliquer la physique de collision
            OnHit(hit);
        }
        else
        {
            transform.position += movement;
        }
    }
}
```

---

## 3. Rigidbodies et Forces

### Types de Rigidbody

```csharp
// Unity Rigidbody types
public enum RigidbodyType
{
    Dynamic,    // Masse, forces, gravité → simulation complète
    Kinematic,  // Pas de forces, mais peut pousser d'autres corps
    Static      // Immobile, collidable seulement
}

Kinematic:
- Pas affecté par la gravité ou les forces
- Se déplace via transform.position ou rigidbody.MovePosition()
- Peut interagir avec les Dynamic (les pousse)
- Utile pour: plateformes mobiles, portes, ascenseurs, personnages

Dynamic:
- Masse, inertie, gravité, forces
- Collision et réaction
- Utile pour: objets physiques, ragdolls, débris
```

### Forces — Types et Application

```csharp
public class ForceExamples : MonoBehaviour
{
    public Rigidbody rb;

    void ApplyForces()
    {
        // Force continue (masse * accélération)
        rb.AddForce(Vector3.forward * 10f, ForceMode.Force);

        // Impulsion instantanée (masse * Δv)
        rb.AddForce(Vector3.up * 5f, ForceMode.Impulse);

        // Changement de vélocité (ignore la masse)
        rb.AddForce(Vector3.forward * 10f, ForceMode.VelocityChange);

        // Accélération (masse * accélération par seconde)
        rb.AddForce(Vector3.forward * 10f, ForceMode.Acceleration);

        // Torque
        rb.AddTorque(Vector3.up * 5f, ForceMode.Impulse);

        // Force au point (pour faire tourner un objet)
        rb.AddForceAtPosition(Vector3.up * 10f, _gripPoint.position, ForceMode.Impulse);
    }

    // Calcul: F = m * a
    // Pour lancer une boîte de 2kg à 10m/s instantanément:
    // Impulse = 2 * 10 = 20 → ForceMode.Impulse avec Vector3.forward * 20
}
```

### Inertia Tensor — Rotation Réaliste

```csharp
// Le tenseur d'inertie contrôle comment un objet tourne
// Plus la masse est éloignée d'un axe, plus il est dur de tourner

// Unity calcule automatiquement le tenseur depuis le mesh
// MAIS: on peut le forcer (boîte parfaite)
void Start()
{
    rb.inertiaTensor = new Vector3(
        (mass / 12f) * (height² + depth²),  // X axis
        (mass / 12f) * (width² + depth²),   // Y axis
        (mass / 12f) * (width² + height²)   // Z axis
    );
    rb.inertiaTensorRotation = Quaternion.identity;
}
```

### Center of Mass (Centre de Masse)

```csharp
// Le centre de masse est automatiquement calculé
// Mais on peut le déplacer pour des comportements spécifiques

public class UnstableBox : MonoBehaviour
{
    void Start()
    {
        // Centre de masse en HAUT de la boîte → elle bascule facilement
        rb.centerOfMass = new Vector3(0, 1.5f, 0);

        // Centre de masse en BAS → stable
        // rb.centerOfMass = new Vector3(0, -1.5f, 0);

        // Afficher visuellement
        Debug.DrawRay(transform.TransformPoint(rb.centerOfMass), Vector3.up, Color.red);
    }
}
```

---

## 4. Joints et Constraints

### Joints Unity

```csharp
// Fixed Joint — rigidement attaché (comme soudé)
[RequireComponent(typeof(FixedJoint))]
public class FixedJointExample : MonoBehaviour
{
    void Start()
    {
        var joint = GetComponent<FixedJoint>();
        joint.connectedBody = _parentRigidbody; // Attaché à un autre corps
        joint.breakForce = 500f; // Force avant rupture
        joint.breakTorque = 500f;
    }
}

// Hinge Joint — charnière (porte, levier)
[RequireComponent(typeof(HingeJoint))]
public class HingeJointExample : MonoBehaviour
{
    void Start()
    {
        var joint = GetComponent<HingeJoint>();

        // Limites d'angle
        var limits = new JointLimits
        {
            min = -90f,
            max = 90f,
            bounciness = 0.2f,
            contactDistance = 0.01f
        };
        joint.limits = limits;
        joint.useLimits = true;

        // Moteur de charnière
        var motor = new JointMotor
        {
            force = 100f,
            targetVelocity = 30f,
            freeSpin = false
        };
        joint.motor = motor;
        joint.useMotor = true;

        // Ressort (ramener au centre)
        var spring = new JointSpring
        {
            spring = 10f,
            damper = 1f,
            targetPosition = 0f
        };
        joint.spring = spring;
        joint.useSpring = false;
    }
}

// Spring Joint — ressort (élasticité)
[RequireComponent(typeof(SpringJoint))]
public class SpringJointExample : MonoBehaviour
{
    void Start()
    {
        var joint = GetComponent<SpringJoint>();
        joint.spring = 20f;      // Raideur
        joint.damper = 1f;       // Amortissement
        joint.minDistance = 0f;
        joint.maxDistance = 5f;
        joint.tolerance = 0.05f;
    }
}

// Configurable Joint — le plus flexible (D6)
[RequireComponent(typeof(ConfigurableJoint))]
public class ConfigurableJointExample : MonoBehaviour
{
    void Start()
    {
        var joint = GetComponent<ConfigurableJoint>();

        // Verrouiller X, Y (mouvement seulement sur Z)
        joint.xMotion = ConfigurableJointMotion.Locked;
        joint.yMotion = ConfigurableJointMotion.Locked;
        joint.zMotion = ConfigurableJointMotion.Free;

        // Rotation libre
        joint.angularXMotion = ConfigurableJointMotion.Free;
        joint.angularYMotion = ConfigurableJointMotion.Free;
        joint.angularZMotion = ConfigurableJointMotion.Free;

        // Drive pour le mouvement motorisé
        var drive = new JointDrive
        {
            positionSpring = 100f,
            positionDamper = 10f,
            maximumForce = float.MaxValue
        };
        joint.xDrive = drive;
    }
}
```

### Breakable Joints — Destruction

```csharp
public class BreakableJoint : MonoBehaviour
{
    public float breakForce = 500f;
    public GameObject brokenPiecePrefab;

    void OnJointBreak(float breakForce)
    {
        Debug.Log($"Joint cassé avec force {breakForce}");

        // Remplacer par des débris
        if (brokenPiecePrefab)
        {
            Instantiate(brokenPiecePrefab, transform.position, transform.rotation);
        }
        Destroy(gameObject);
    }
}
```

---

## 5. Character Controllers

### Unity Character Controller

```csharp
[RequireComponent(typeof(CharacterController))]
public class CustomCharacterController : MonoBehaviour
{
    private CharacterController _controller;
    public float speed = 6f;
    public float jumpHeight = 2f;
    public float gravity = -9.81f;

    private Vector3 _velocity;
    private bool _isGrounded;

    void Start() => _controller = GetComponent<CharacterController>();

    void Update()
    {
        _isGrounded = _controller.isGrounded;
        if (_isGrounded && _velocity.y < 0)
            _velocity.y = -2f;

        // Mouvement horizontal
        float x = Input.GetAxis("Horizontal");
        float z = Input.GetAxis("Vertical");
        Vector3 move = transform.right * x + transform.forward * z;
        _controller.Move(move * speed * Time.deltaTime);

        // Saut
        if (Input.GetButtonDown("Jump") && _isGrounded)
            _velocity.y = Mathf.Sqrt(jumpHeight * -2f * gravity);

        // Gravité
        _velocity.y += gravity * Time.deltaTime;
        _controller.Move(_velocity * Time.deltaTime);
    }
}
```

### PhysX-based Character Controller (Capsule)

```csharp
// CharacterController basé sur PhysX (utilisé par la plupart des jeux)
// Propriétés clés:
// - Step Offset: hauteur de marche de l'escalier (0.1-0.3m)
// - Slope Limit: pente max que le personnage peut gravir (45°)
// - Skin Width: marge de collision (0.01-0.1m)
// - Min Move Distance: distance min avant de bouger (évite les vibrations)

// Problème: se coincer dans les coins → utiliser un capsule collider
// Problème: glisser sur les pentes → réorienter la vélocité
```

### Godot CharacterBody

```gdscript
extends CharacterBody3D

@export var speed := 5.0
@export var jump_velocity := 4.5
@export var max_slope_angle := 45.0

func _physics_process(delta: float) -> void:
    # Mouvement horizontal
    var input_dir := Input.get_vector("gauche", "droite", "avant", "arriere")
    var direction := (transform.basis * Vector3(input_dir.x, 0, input_dir.y)).normalized()

    if direction:
        velocity.x = direction.x * speed
        velocity.z = direction.z * speed
    else:
        velocity.x = move_toward(velocity.x, 0, speed)
        velocity.z = move_toward(velocity.z, 0, speed)

    # Saut
    if Input.is_action_just_pressed("sauter") and is_on_floor():
        velocity.y = jump_velocity

    # Gravité
    if not is_on_floor():
        velocity.y += gravity * delta

    move_and_slide()
```

---

## 6. Soft Bodies et Cloth

```text
Soft Bodies → maillage déformable avec ressorts

Types:
- Tetrahedral: volume complet (découpe réelle)
- Spring Mesh: surface (vêtements, drapeaux)
- Cloth: contraintes spécialisées (plis, cisaillement)

Unreal: Chaos Cloth (héritier d'APEX)
Unity: Cloth component (PhysX legacy)
Godot: SoftBody node (Bullet)
Custom: Verlet Integration (simple, performant)
```

### Verlet Integration — Soft Body Custom

```csharp
// Verlet Integration: simple, stable, pas de vitesses explicites
public struct VerletPoint
{
    public Vector3 Position;
    public Vector3 OldPosition;
    public bool Pinned;
}

public class VerletCloth : MonoBehaviour
{
    public struct Constraint
    {
        public int A, B;
        public float RestLength;
    }

    private VerletPoint[] _points;
    private Constraint[] _constraints;
    public float gravity = -9.81f;
    public int iterations = 8;

    void Update()
    {
        float dt = Time.deltaTime;

        // 1. Mise à jour des positions (Verlet)
        foreach (ref var p in _points.AsSpan())
        {
            if (p.Pinned) continue;

            Vector3 velocity = p.Position - p.OldPosition;
            p.OldPosition = p.Position;
            p.Position += velocity; // Conservation inertie
            p.Position.y += gravity * dt * dt; // Gravité
        }

        // 2. Contraintes (itérations multiples pour stabilité)
        for (int i = 0; i < iterations; i++)
        {
            foreach (var c in _constraints)
            {
                Vector3 delta = _points[c.B].Position - _points[c.A].Position;
                float dist = delta.magnitude;
                float error = (dist - c.RestLength) / dist;

                if (!_points[c.A].Pinned)
                    _points[c.A].Position += delta * error * 0.5f;
                if (!_points[c.B].Pinned)
                    _points[c.B].Position -= delta * error * 0.5f;
            }
        }
    }
}
```

---

## 7. Raycasts et Queries

```csharp
public class RaycastExamples : MonoBehaviour
{
    void Update()
    {
        // Raycast simple
        if (Physics.Raycast(transform.position, transform.forward, out RaycastHit hit, 100f))
        {
            Debug.Log($"Touché: {hit.collider.name} à {hit.distance}m");
            // hit.point, hit.normal, hit.transform
        }

        // Raycast avec masque de layer
        int layerMask = LayerMask.GetMask("Enemies", "Walls");
        Physics.Raycast(origin, direction, out hit, 100f, layerMask);

        // SphereCast (balle large)
        if (Physics.SphereCast(origin, radius, direction, out hit, 100f))
        {
            // hit.point est le centre de la sphère au contact
        }

        // BoxCast
        Physics.BoxCast(center, halfExtents, direction, out hit, rotation, distance);

        // OverlapSphere (tous les colliders dans un rayon)
        Collider[] hits = Physics.OverlapSphere(transform.position, 5f, enemyMask);
        foreach (var c in hits)
            c.GetComponent<Enemy>()?.TakeDamage(10);

        // OverlapBox (zone rectangulaire)
        Collider[] boxHits = Physics.OverlapBox(center, halfExtents, rotation, layerMask);

        // OverlapCapsule (personnage debout)
        Collider[] capsuleHits = Physics.OverlapCapsule(
            bottom, top, radius, layerMask);

        // RaycastAll (tous les obstacles sur le chemin)
        RaycastHit[] allHits = Physics.RaycastAll(origin, direction, 100f);
        // Trier par distance
        System.Array.Sort(allHits, (a, b) => a.distance.CompareTo(b.distance));

        // NonAlloc versions (zéro allocation)
        int count = Physics.RaycastNonAlloc(origin, direction, _hitBuffer, 100f);
        for (int i = 0; i < count; i++)
            ProcessHit(_hitBuffer[i]);
    }
}
```

### Trigger vs Collision

```csharp
// Collision: contact physique réel (rebond, frottement)
void OnCollisionEnter(Collision collision)
{
    // collision.contacts → points de contact
    // collision.impulse → force de l'impact
    // collision.relativeVelocity → vitesse relative
}

// Trigger: détection sans physique (zone, piège, checkpoint)
void OnTriggerEnter(Collider other)
{
    // Pas de réaction physique
    // Idéal pour: zones de dégâts, pickup, portes
}

void OnTriggerStay(Collider other) { } // Tant que dedans
void OnTriggerExit(Collider other) { }  // En sortant
```

---

## 8. Physical Materials (Friction et Rebond)

```csharp
// Unity PhysicMaterial
public class PhysicsMaterialSetup : MonoBehaviour
{
    void Start()
    {
        var mat = new PhysicMaterial();

        // Frottements
        mat.staticFriction = 0.6f;   // Force pour commencer à bouger
        mat.dynamicFriction = 0.4f;  // Force pour continuer à bouger
        mat.frictionCombine = PhysicMaterialCombine.Average;
        // Average, Minimum, Maximum, Multiply

        // Rebond
        mat.bounciness = 0.5f;        // 0 = pas de rebond, 1 = rebond parfait
        mat.bounceCombine = PhysicMaterialCombine.Maximum;

        // Appliquer
        GetComponent<Collider>().material = mat;
    }
}
```

---

## 9. Déterminisme et Fixed Timestep

```csharp
// Le déterminisme est CRUCIAL pour:
// - Replay (enregistrer/relire exactement)
// - Rollback netcode (combat games)
// - Tests automatisés

// Unity ne garantit PAS le déterminisme à travers:
// - Différentes plateformes (PhysX ≠ Jolt)
// - Différents moteurs physiques
// - Floating point (IEEE 754 pas toujours respecté)

// Fixed Timestep
void Awake()
{
    // 50Hz = 0.02s (standard), 60Hz = 0.0166s, 30Hz = 0.033s
    Time.fixedDeltaTime = 0.02f;
    Time.maximumDeltaTime = 0.1f; // Éviter le spiral of death
}

// Pour un lockstep déterministe:
// 1. Même moteur physique (Jolt est bon pour ça)
// 2. Même seed RNG
// 3. Input seulement, pas d'états aléatoires
// 4. Accumulateur de timestep fixe
```

---

## 10. Pièges Courants

- **CCD désactivé** → balles qui traversent les murs à haute vitesse. Toujours activer sur les objets rapides.
- **FixedUpdate à 60Hz inutile** → 30Hz suffit pour 80% des jeux.
- **Layer collision matrix pas configurée** → des balles qui se cognent entre elles → collisions inutiles.
- **Trop d'objets dynamiques** → 100+ rigidbodies = solver surchargé. 30 max pour la stabilité.
- **Kinematic mis à jour via transform** → pas d'interaction physique. Utiliser MovePosition/MoveRotation.
- **Joints sans connectedBody** → attaché au monde (mauvais). Toujours assigner un Rigidbody.
- **Mass trop faible/trop élevée** → masse < 0.01 = instable. > 10000 = perce tout.
- **Sleep désactivé** → tous les rigidbodies simulés tout le temps → CPU saturé. Laisser le sleep.
- **OnCollisionEnter coûteux** → instancier effets à chaque collision → pool d'effets.
- **Mesh colliders convexes** → Mesh Collider non-convexe = pas de collision avec un autre mesh. Marquer comme convexe ou utiliser des colliders simples.