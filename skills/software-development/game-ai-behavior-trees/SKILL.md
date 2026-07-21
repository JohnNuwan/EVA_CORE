---
name: game-ai-behavior-trees
description: Guide complet d'IA pour jeux vidéo — Behavior Trees, Finite State Machines (FSM), GOAP, Utility AI, Pathfinding (A*, NavMesh), perception, animation blending, et architecture de décision pour NPCs et ennemis.
---

# Game AI — Behavior Trees et Systèmes de Décision

Ce skill couvre la conception et l'implémentation d'IA pour jeux vidéo, des FSM aux Behavior Trees, en passant par GOAP et Utility AI. À charger pour toute tâche d'IA de jeu, comportement d'ennemi, ou pathfinding.

---

## 1. Finite State Machines (FSM) — L'IA Classique

### FSM basique (C# Unity)

```csharp
public enum EtatNPC { IDLE, PATROL, CHASE, ATTACK, FLEE }

public class NPCAI : MonoBehaviour
{
    public EtatNPC etatCourant = EtatNPC.IDLE;
    public Transform cible;
    public float detectionRange = 10f;
    public float attackRange = 2f;
    
    void Update()
    {
        switch (etatCourant)
        {
            case EtatNPC.IDLE:
                // Attendre
                if (DetecterJoueur())
                    etatCourant = EtatNPC.CHASE;
                break;
                
            case EtatNPC.PATROL:
                // Patrouiller entre waypoints
                if (DetecterJoueur())
                    etatCourant = EtatNPC.CHASE;
                if (Sante < 0.2f)
                    etatCourant = EtatNPC.FLEE;
                break;
                
            case EtatNPC.CHASE:
                // Poursuivre le joueur
                if (DistanceCible() < attackRange)
                    etatCourant = EtatNPC.ATTACK;
                if (!DetecterJoueur())
                    etatCourant = EtatNPC.PATROL;
                break;
                
            case EtatNPC.ATTACK:
                // Attaquer
                if (DistanceCible() > attackRange)
                    etatCourant = EtatNPC.CHASE;
                if (Sante < 0.1f)
                    etatCourant = EtatNPC.FLEE;
                break;
        }
    }
    
    bool DetecterJoueur() => Vector3.Distance(transform.position, cible.position) < detectionRange;
    float DistanceCible() => Vector3.Distance(transform.position, cible.position);
}
```

### FSM avec pattern State (modulaire)

```csharp
public interface IEtat
{
    void Entrer();
    void Executer();
    void Sortir();
}

public class EtatChase : IEtat
{
    private NPCAI _npc;
    public EtatChase(NPCAI npc) => _npc = npc;
    
    public void Entrer() => _npc.agent.speed = 5f;
    public void Executer() => _npc.agent.SetDestination(_npc.cible.position);
    public void Sortir() => _npc.agent.ResetPath();
}
```

---

## 2. Behavior Trees (BT) — L'IA Moderne

### Architecture d'un Behavior Tree

```
Racine (Selector)
├── Séquence "Attaquer"
│   ├── Condition "Joueur à portée"
│   ├── Action "Attaquer"
│   └── Action "Attendre cooldown"
├── Séquence "Chasser"
│   ├── Condition "Joueur détecté"
│   ├── Action "Poursuivre"
│   └── Action "Perdre vu" (timer)
└── Patrouille
    ├── Action "Aller au waypoint"
    └── Action "Attendre"
```

### Implémentation BT (C# Unity)

```csharp
using System.Collections.Generic;

public abstract class BTNode
{
    public enum State { SUCCESS, FAILURE, RUNNING }
    public abstract State Execute();
}

public class Selector : BTNode
{
    private List<BTNode> _children = new();
    public Selector(params BTNode[] children) => _children.AddRange(children);
    
    public override State Execute()
    {
        foreach (var child in _children)
        {
            var result = child.Execute();
            if (result != State.FAILURE)
                return result;
        }
        return State.FAILURE;
    }
}

public class Sequence : BTNode
{
    private List<BTNode> _children = new();
    public Sequence(params BTNode[] children) => _children.AddRange(children);
    
    public override State Execute()
    {
        foreach (var child in _children)
        {
            var result = child.Execute();
            if (result != State.SUCCESS)
                return result;
        }
        return State.SUCCESS;
    }
}

public class Condition : BTNode
{
    private System.Func<bool> _condition;
    public Condition(System.Func<bool> condition) => _condition = condition;
    
    public override State Execute() => _condition() ? State.SUCCESS : State.FAILURE;
}

public class Action : BTNode
{
    private System.Func<State> _action;
    public Action(System.Func<State> action) => _action = action;
    
    public override State Execute() => _action();
}

public class Inverter : BTNode
{
    private BTNode _child;
    public Inverter(BTNode child) => _child = child;
    
    public override State Execute()
    {
        var result = _child.Execute();
        return result switch
        {
            State.SUCCESS => State.FAILURE,
            State.FAILURE => State.SUCCESS,
            _ => State.RUNNING
        };
    }
}

// Usage
public class EnnemiBT : MonoBehaviour
{
    private BTNode _root;
    
    void Start()
    {
        _root = new Selector(
            new Sequence(
                new Condition(() => DistanceCible() < 2f),
                new Action(() => Attaquer())
            ),
            new Sequence(
                new Condition(() => DetecterJoueur()),
                new Action(() => Poursuivre())
            ),
            new Action(() => Patrouiller())
        );
    }
    
    void Update() => _root.Execute();
    
    private BTNode.State Attaquer() { /* ... */ return BTNode.State.SUCCESS; }
    private BTNode.State Poursuivre() { /* ... */ return BTNode.State.RUNNING; }
    private BTNode.State Patrouiller() { /* ... */ return BTNode.State.RUNNING; }
    private bool DetecterJoueur() { /* ... */ return true; }
    private float DistanceCible() { /* ... */ return 5f; }
}
```

### Behavior Tree avec Decorators (Wait, Cooldown, Blackboard)

```csharp
public class Wait : BTNode
{
    private float _duration, _elapsed;
    
    public Wait(float duration) => _duration = duration;
    
    public override State Execute()
    {
        _elapsed += Time.deltaTime;
        if (_elapsed >= _duration)
        {
            _elapsed = 0;
            return State.SUCCESS;
        }
        return State.RUNNING;
    }
}

public class Cooldown : BTNode
{
    private BTNode _child;
    private float _cooldown, _lastExecution;
    
    public Cooldown(BTNode child, float cooldown)
    {
        _child = child;
        _cooldown = cooldown;
    }
    
    public override State Execute()
    {
        if (Time.time - _lastExecution < _cooldown)
            return State.FAILURE;
        var result = _child.Execute();
        if (result != State.RUNNING)
            _lastExecution = Time.time;
        return result;
    }
}
```

---

## 3. GOAP (Goal-Oriented Action Planning)

GOAP est utilisé dans F.E.A.R. (2005) et des jeux modernes. L'IA planifie une séquence d'actions pour atteindre un but.

```csharp
public class GOAPAction
{
    public string Nom;
    public float Cout;
    public Dictionary<string, bool> Preconditions = new();
    public Dictionary<string, bool> Effects = new();
    public System.Func<bool> Execute;
}

public class GOAPPlanner
{
    public Queue<GOAPAction> Plan(
        Dictionary<string, bool> worldState,
        Dictionary<string, bool> goal,
        List<GOAPAction> actions)
    {
        // A* sur l'espace d'état
        var frontier = new PriorityQueue<GOAPNode, float>();
        var visited = new HashSet<string>();
        
        frontier.Enqueue(new GOAPNode(worldState, null, null, 0), 0);
        
        while (frontier.Count > 0)
        {
            var current = frontier.Dequeue();
            string key = SerializeState(current.State);
            
            if (visited.Contains(key)) continue;
            visited.Add(key);
            
            // Vérifier si le but est atteint
            if (GoalMet(current.State, goal))
                return ReconstructPath(current);
            
            foreach (var action in actions)
            {
                if (CanExecute(action, current.State))
                {
                    var newState = ApplyEffects(action, current.State);
                    float cost = current.Cost + action.Cout;
                    float heuristic = Heuristic(newState, goal);
                    frontier.Enqueue(new GOAPNode(newState, action, current, cost), cost + heuristic);
                }
            }
        }
        
        return null; // Aucun plan trouvé
    }
    
    private bool GoalMet(Dictionary<string, bool> state, Dictionary<string, bool> goal)
    {
        foreach (var kvp in goal)
            if (!state.ContainsKey(kvp.Key) || state[kvp.Key] != kvp.Value)
                return false;
        return true;
    }
    
    private bool CanExecute(GOAPAction action, Dictionary<string, bool> state)
    {
        foreach (var pre in action.Preconditions)
            if (!state.ContainsKey(pre.Key) || state[pre.Key] != pre.Value)
                return false;
        return true;
    }
}
```

---

## 4. Utility AI (IA Pondérée)

Utility AI évalue plusieurs actions avec des scores et choisit la meilleure.

```csharp
public class UtilityAI
{
    public class Consideration
    {
        public string Nom;
        public System.Func<float> Evaluate; // Retourne 0.0 - 1.0
        public float Poids = 1f;
    }
    
    public class Action
    {
        public string Nom;
        public List<Consideration> Considerations = new();
        public System.Action Execute;
        
        public float Evaluate()
        {
            if (Considerations.Count == 0) return 0;
            
            float score = 1f;
            foreach (var c in Considerations)
            {
                // Multiplication des considérations (AND logique)
                score *= 1f - (c.Poids * (1f - c.Evaluate()));
            }
            
            // Effet de compensation (pas de score nul)
            float mod = 1f - (1f / Considerations.Count);
            return score + mod * (score * 0.5f);
        }
    }
    
    private List<Action> _actions = new();
    
    public void AddAction(Action action) => _actions.Add(action);
    
    public Action GetBestAction()
    {
        Action best = null;
        float bestScore = float.MinValue;
        
        foreach (var action in _actions)
        {
            float score = action.Evaluate();
            if (score > bestScore)
            {
                bestScore = score;
                best = action;
            }
        }
        return best;
    }
}

// Usage
var ai = new UtilityAI();
ai.AddAction(new UtilityAI.Action
{
    Nom = "Attaquer",
    Considerations = new()
    {
        new() { Nom = "Distance", Evaluate = () => Mathf.Clamp01(1f - dist / 20f), Poids = 0.8f },
        new() { Nom = "Sante", Evaluate = () => sante / 100f, Poids = 0.6f },
        new() { Nom = "Munitions", Evaluate = () => munitions / 30f, Poids = 0.5f },
    }
});
```

---

## 5. Pathfinding — A* et NavMesh

### A* (C#)

```csharp
public class AStar
{
    public class Node
    {
        public int X, Y;
        public bool Walkable;
        public float GCost, HCost;
        public Node Parent;
        public float FCost => GCost + HCost;
    }
    
    private Node[,] _grid;
    
    public List<Node> FindPath(Node start, Node end)
    {
        var open = new List<Node> { start };
        var closed = new HashSet<Node>();
        
        while (open.Count > 0)
        {
            // Trouver le noeud avec le plus bas FCost
            var current = open.OrderBy(n => n.FCost).First();
            
            if (current == end)
                return RetracerChemin(start, end);
            
            open.Remove(current);
            closed.Add(current);
            
            foreach (var neighbor in GetNeighbors(current))
            {
                if (!neighbor.Walkable || closed.Contains(neighbor))
                    continue;
                
                float newGCost = current.GCost + Distance(current, neighbor);
                if (newGCost < neighbor.GCost || !open.Contains(neighbor))
                {
                    neighbor.GCost = newGCost;
                    neighbor.HCost = Distance(neighbor, end);
                    neighbor.Parent = current;
                    if (!open.Contains(neighbor))
                        open.Add(neighbor);
                }
            }
        }
        
        return null; // Aucun chemin
    }
    
    private float Distance(Node a, Node b) => Mathf.Sqrt((a.X-b.X)^2 + (a.Y-b.Y)^2);
}
```

### NavMesh Unity

```csharp
using UnityEngine.AI;

public class NPCMovement : MonoBehaviour
{
    private NavMeshAgent _agent;
    
    void Start() => _agent = GetComponent<NavMeshAgent>();
    
    public void MoveTo(Vector3 destination)
    {
        _agent.SetDestination(destination);
    }
    
    public void FleeFrom(Vector3 threat, float distance = 10f)
    {
        Vector3 dir = (transform.position - threat).normalized;
        Vector3 fleePos = transform.position + dir * distance;
        
        // Trouver le point valide le plus proche sur le NavMesh
        if (NavMesh.SamplePosition(fleePos, out NavMeshHit hit, distance, NavMesh.AllAreas))
            _agent.SetDestination(hit.position);
    }
}
```

### Évitement d'obstacles (RVO / Crowd Simulation)

```csharp
// Unity: NavMeshAgent + ObstacleAvoidance
_agent.obstacleAvoidanceType = ObstacleAvoidanceType.HighQualityObstacleAvoidance;
_agent.radius = 0.5f;

// Paramètres RVO
_agent.agentTypeID = 0; // Agent type défini dans le NavMesh
_agent.speed = 3.5f;
_agent.angularSpeed = 120f;
_agent.acceleration = 8f;
```

---

## 6. Perception — Vision et Ouïe

```csharp
public class Perception : MonoBehaviour
{
    [Header("Vision")]
    public float viewRange = 15f;
    [Range(0, 360)] public float viewAngle = 90f;
    public LayerMask targetMask, obstacleMask;
    
    [Header("Audition")]
    public float hearRange = 20f;
    
    public bool DetectTarget(out Transform target)
    {
        target = null;
        var colliders = Physics.OverlapSphere(transform.position, viewRange, targetMask);
        
        foreach (var col in colliders)
        {
            Vector3 dirToTarget = (col.transform.position - transform.position).normalized;
            float angle = Vector3.Angle(transform.forward, dirToTarget);
            
            // Vérifier l'angle de vue
            if (angle < viewAngle * 0.5f)
            {
                // Vérifier la ligne de vue (pas d'obstacle)
                float dist = Vector3.Distance(transform.position, col.transform.position);
                if (!Physics.Raycast(transform.position, dirToTarget, dist, obstacleMask))
                {
                    target = col.transform;
                    return true;
                }
            }
        }
        return false;
    }
    
    public bool HeardNoise(Vector3 noisePos, float noiseRange)
    {
        float dist = Vector3.Distance(transform.position, noisePos);
        return dist < hearRange && dist < noiseRange;
    }
}
```

---

## 7. Animation Blending — Lier l'IA à l'Animation

```csharp
public class IAAnimationBridge : MonoBehaviour
{
    private Animator _anim;
    private NavMeshAgent _agent;
    
    void Start()
    {
        _anim = GetComponent<Animator>();
        _agent = GetComponent<NavMeshAgent>();
    }
    
    void Update()
    {
        // Sync vitesse animation → mouvement
        _anim.SetFloat("Speed", _agent.velocity.magnitude);
        
        // Sync direction
        Vector3 localVel = transform.InverseTransformDirection(_agent.velocity);
        _anim.SetFloat("DirectionX", localVel.x);
        _anim.SetFloat("DirectionZ", localVel.z);
        
        // État d'alerte
        _anim.SetBool("IsCombat", estEnCombat);
    }
}
```

---

## 8. Architecture de Décision — Comparaison

| Technique | Avantages | Inconvénients | Utilisation |
|-----------|-----------|---------------|-------------|
| **FSM** | Simple, intuitive, débogable | Rigide, difficile à étendre | NPCs simples, états de base |
| **Behavior Tree** | Modulaire, réutilisable, hiérarchique | Plus complexe à déboguer | La plupart des jeux modernes |
| **GOAP** | Adaptatif, planification dynamique | Coût CPU, comportements imprévisibles | IA tactique (F.E.A.R., Hitman) |
| **Utility AI** | Comportements naturels, pondération | Beaucoup de réglage fin | Décisions nuancées (The Sims, CK3) |
| **HTN (Hierarchical Task Network)** | Planification efficace, domaines complexes | Setup complexe | IA stratégique (Killzone) |

---

## 9. Pièges Courants

- **IA trop prévisible** : FSM sans aléa → le joueur apprend les patterns
- **Pathfinding bloqué** : NavMesh non mis à jour → murs destructibles cassés
- **Coût A* trop élevé** : 1000+ noeuds → utiliser des waypoints clusters ou JPS (Jump Point Search)
- **Utility AI plat** : toutes les actions ont le même score → bias de bruit nécessaire
- **GOAP replanning** : replanifier à chaque frame → timer 0.5s minimum
- **Animation/IA désynchronisé** : l'anim joue "attaque" mais l'IA a déjà changé d'état
- **Perception parfaite** : l'IA voit/traverse TOUT → add line of sight checks + fog of war
- **BT sans blackboard** : pas de partage d'état → blackboard (Dictionary global) pour la mémoire de l'IA