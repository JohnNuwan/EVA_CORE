---
title: "Arbres de Comportement pour PNJ"
description: "Guide complet pour concevoir et implémenter des arbres de comportement (Behavior Trees) pour PNJ dans les jeux vidéo. Basé sur les systèmes de The Last of Us, God of War, Horizon, et les standards de l'industrie."
category: creative
tags: [npc, behavior-trees, ai, game-design, animation]
---

# Arbres de Comportement pour PNJ

## Standards de l'Industrie

### Références Primées

| Jeu | Prix | Système IA |
|-----|------|------------|
| **The Last of Us Part II** | BAFTA 2021 Animation, TGA 2020 | Compagnons autonomes, IA ennemie tactique |
| **God of War Ragnarök** | BAFTA 2023 Animation | Atreus compagnon dynamique |
| **Horizon Forbidden West** | BAFTA 2022 | IA machines, comportements de meute |
| **Elden Ring** | GDCA 2023 | PNJ énigmatiques, IA de boss |
| **Control** | GDCA 2020 | IA ennemie télékinésique |
| **Alan Wake 2** | GDCA 2024 | IA narrative, PNJ procéduraux |
| **Black Myth: Wukong** | GDCA 2025 | IA de boss complexe |
| **Dispatch** | BAFTA 2026 | IA narrative conversationnelle |

## Architecture Behavior Tree

### Nœuds Fondamentaux

```
Root
├── Selector (OR) — essaie les enfants dans l'ordre
│   ├── Sequence (AND) — tous les enfants doivent réussir
│   │   ├── Condition → Vérifier état
│   │   ├── Action → Exécuter comportement
│   │   └── Wait → Attendre X secondes
│   ├── Parallel → Exécuter en parallèle
│   └── Decorator → Modifier le comportement
│       ├── Inverter → Inverser le résultat
│       ├── Repeater → Répéter N fois
│       ├── UntilSuccess → Jusqu'à succès
│       └── Cooldown → Temps de recharge
└── Fallback → Plan de secours
```

### Exemple: Compagnon IA (Atreus — God of War)

```
Comportement Atreus (Selector)
├── Combat Mode
│   ├── Sequence (Attaquer)
│   │   ├── Condition: Ennemis détectés
│   │   ├── Action: Sélectionner cible (priorité: plus proche, faible, dans le dos)
│   │   ├── Action: Se positionner (flanc, distance optimale)
│   │   ├── Action: Attaquer (arc, runique, stun)
│   │   └── Action: Reculer (sécurité)
│   ├── Sequence (Soutenir)
│   │   ├── Condition: Kratos en danger
│   │   ├── Action: Lancer flèche de soutien
│   │   └── Action: Cri de distraction
│   └── Action: Esquiver (ennemi qui charge)
│
├── Exploration Mode
│   ├── Sequence (Suivre)
│   │   ├── Condition: Distance > 5m
│   │   ├── Action: Courir vers Kratos
│   │   └── Action: Regarder autour
│   ├── Sequence (Interagir)
│   │   ├── Condition: Point d'intérêt détecté
│   │   ├── Action: S'approcher
│   │   ├── Action: Commenter (dialogue contextuel)
│   │   └── Action: Attendre réaction
│   └── Action: Idle (regarder, respirer, bouger)
│
└── Narrative Mode
    ├── Sequence (Dialogue)
    │   ├── Condition: Kratos a parlé
    │   ├── Action: Répondre (animation faciale + voix)
    │   └── Action: Regarder Kratos
    └── Action: Écouter (hocher la tête, réagir)
```

## Patterns de Comportement

### 1. Compagnon Dynamique (The Last of Us, God of War)

**Caractéristiques**:
- Suit le joueur sans être collé (distance 2-5m)
- Commente l'environnement (procédural, pas scripté)
- Aide au combat (attaque, soutien, distraction)
- Réagit aux actions du joueur
- A une personnalité (timide, courageux, curieux)

**Techniques**:
- **Spline follower**: Chemin lissé derrière le joueur
- **Cover system**: Cachettes automatiques en combat
- **Look-at system**: Regarde ce que le joueur regarde
- **Dialogue contextual**: Déclenché par position, action, événement
- **Animation blending**: Transitions fluides entre états

### 2. IA Ennemie Tactique (The Last of Us Part II)

**Caractéristiques**:
- Communication entre ennemis (sifflements, cris)
- Flanking (contournement)
- Recherche en groupe (patrouille)
- Réaction aux bruits (distraction)
- Mémoire (dernière position connue du joueur)

**Arbre de Comportement**:
```
Ennemi (Selector)
├── Patrouille
│   ├── Sequence
│   │   ├── Waypoint suivant
│   │   ├── Regarder autour
│   │   └── Attendre (pause)
│   └── Action: Communication radio
│
├── Alerte
│   ├── Sequence: Enquêter
│   │   ├── Dernière position connue
│   │   ├── Chercher
│   │   └── Signaler
│   └── Sequence: Combat
│       ├── Couverture
│       ├── Attaquer
│       ├── Flanker
│       └── Reculer (si blessé)
│
└── Mort
```

### 3. IA de Machines (Horizon)

**Caractéristiques**:
- Comportements de meute
- Réactions aux éléments (feu, glace, électricité)
- Alertes graduelles (vert → jaune → rouge)
- Démontage (destruction de parties)
- Territorialité

### 4. PNJ Narratifs (Elden Ring, Alan Wake 2)

**Caractéristiques**:
- État de quête (progress tracking)
- Dialogue arborescent
- Réactions aux actions du joueur
- Émotions (tristesse, joie, colère)
- Mémoire (souvient des interactions)

## Implémentation Technique

### Unity (C# avec Behavior Designer)
```csharp
public class CompanionAI : MonoBehaviour
{
    public BehaviorTree behaviorTree;
    public Transform player;
    public float followDistance = 3f;
    public float combatDistance = 8f;
    
    void Start()
    {
        behaviorTree = new BehaviorTree();
        
        // Root node
        var root = new Selector("Companion Behavior");
        
        // Combat mode
        var combatSeq = new Sequence("Combat");
        combatSeq.AddChild(new Condition("Enemies Near", () => DetectEnemies()));
        combatSeq.AddChild(new Action("Attack", () => PerformAttack()));
        
        // Follow mode
        var followSeq = new Sequence("Follow");
        followSeq.AddChild(new Condition("Too Far", () => DistanceToPlayer() > followDistance));
        followSeq.AddChild(new Action("Move To Player", () => MoveTo(player.position)));
        
        root.AddChild(combatSeq);
        root.AddChild(followSeq);
        
        behaviorTree.root = root;
    }
    
    void Update()
    {
        behaviorTree.Tick();
    }
}
```

### Unreal Engine (Blueprint)
```
Event Tick → Behavior Tree Component
├── Run Behavior Tree → BT_Companion
│   ├── Selector: Root
│   │   ├── Sequence: Combat
│   │   │   ├── Condition: HasEnemiesInRange
│   │   │   ├── Task: SelectTarget
│   │   │   ├── Task: MoveToTarget
│   │   │   └── Task: Attack
│   │   ├── Sequence: Explore
│   │   │   ├── Condition: PointOfInterest
│   │   │   ├── Task: MoveToPOI
│   │   │   └── Task: Investigate
│   │   └── Task: FollowPlayer
│   └── Blackboard: Data
│       ├── TargetActor
│       ├── MoveToLocation
│       └── CurrentState
```

## Métriques de Qualité

| Métrique | Bon | Excellent |
|----------|-----|-----------|
| Temps de réaction | < 500ms | < 200ms |
| Distance de suivi | 2-5m | 1.5-4m |
| Variété de dialogues | 50+ | 200+ |
| Animations uniques | 20+ | 100+ |
| États de comportement | 5-10 | 15+ |
| Pas de clipping | 95% | 99% |

## Pitfalls

- **PNJ qui bloque le chemin** → système d'évitement
- **Comportement prévisible** → trop de répétition
- **Pas de personnalité** → le PNJ ne se distingue pas
- **Animation rigide** → transitions brutales
- **Ignorer le contexte** → le PNJ ne réagit pas à l'environnement
- **Trop de dialogue** → le joueur skip
- **IA trop parfaite** → pas humaine

## Voir Aussi

- [game-ai-character-design](../game-ai-character-design/SKILL.md)
- [animation-patterns-for-ui](../animation-patterns-for-ui/SKILL.md)
- [video-game-award-winning-ui](../video-game-award-winning-ui/SKILL.md)