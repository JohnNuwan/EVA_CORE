---
name: game-design
description: Guide complet de conception de jeu vidéo — mécaniques (MDA), game feel, systèmes de progression, level design, UX/UI, équilibrage, game design documents (GDD), playtesting et psychologie du joueur.
---

# Game Design — Guide Complet

Ce skill couvre la conception de jeux vidéo, de l'idée au prototype jouable. À charger pour toute tâche de game design, rédaction de GDD, équilibrage de systèmes, ou analyse de mécaniques de jeu.

---

## 1. Le Modèle MDA (Mechanics, Dynamics, Aesthetics)

Le cadre d'analyse le plus utilisé en game design (Robin Hunicke, Marc LeBlanc, Robert Zubek).

| Couche | Définition | Exemple (Super Mario) |
|--------|-----------|----------------------|
| **Mechanics** | Règles, données, algorithmes du jeu | Saut → gravité → plateforme |
| **Dynamics** | Comportements émergents des règles | Rythme saut/précision/ennemis |
| **Aesthetics** | Réponses émotionnelles du joueur | Défi, maîtrise, progression |

**Règle d'or** : Le designer travaille *des Mechanics vers les Aesthetics*. Le joueur vit *des Aesthetics vers les Mechanics*.

### Les 8 Aesthetics (Types de Plaisir)

1. **Sensation** (plaisir sensoriel) — VFX, son, vibrations
2. **Fantasy** (évasion, imaginaire) — Narration, worldbuilding
3. **Narrative** (histoire, drame) — Quêtes, dialogues, lore
4. **Challenge** (obstacle à surmonter) — Difficulté, puzzles
5. **Fellowship** (social) — Multiplayer, guildes, chat
6. **Discovery** (exploration, surprise) — Secrets, loot, zones cachées
7. **Expression** (créativité, customisation) — Skins, builds, éditeur
8. **Submission** (grind, relaxation) — Farming, idle games

---

## 2. Game Design Document (GDD)

### Structure standard

```markdown
# GDD — [Titre du Jeu]

## 1. Executive Summary (1 page)
- Concept : 3 phrases max
- Genre, plateformes, public cible
- USP (Unique Selling Point) — "En quoi c'est différent ?"
- Compétiteurs directs

## 2. Core Loop
- [Boucle principale] → Ex: Explorer → Combattre → Looter → Améliorer → Explorer
- [Boucle secondaire] → Ex: Quêtes → XP → Compétences → Quêtes
- [Boucle méta] → Ex: Saison → Rank → Récompenses → Saison

## 3. Mécaniques Détaillées
- Mouvement, combat, crafting, progression
- Systèmes de stats, équations, tables d'équilibrage
- Input mapping (manette/clavier/tactile)

## 4. Systèmes de Progression
- Arbre de compétences / tech tree
- Niveaux, XP, déblocages
- Économie du jeu (monnaies, ressources, crafting)

## 5. Level Design
- Liste des niveaux/zones
- Flowchart des connexions
- Moments forts par niveau (beat chart)

## 6. UX/UI
- Menu, HUD, inventaire
- Flow utilisateur (User Journey Map)
- Wireframes des écrans principaux

## 7. Narration et Lore
- Synopsis, personnages, factions
- Arbre de dialogues / quêtes
- Ton et direction artistique

## 8. Monetization (si applicable)
- Modèle économique (Premium, F2P, Battle Pass)
- Items payants vs farmables
- Économie et équilibrage pay-to-win

## 9. Technical Scope
- Moteur, langages, dépendances
- Cibles de performance (FPS, RAM, storage)
- Multiplayer / Online requirements

## 10. Production Roadmap
- Phases : Prototype → Vertical Slice → Alpha → Beta → Release
- Milestones et deliverables
- Équipe nécessaire
```

---

## 3. Game Feel — Le Secret du "Bon" Jeu

### Les 12 dimensions du Game Feel (Steve Swink)

| Dimension | Description | Technique |
|-----------|-------------|-----------|
| **Response Time** | Latence input → action | < 100ms pour un jeu réactif |
| **Polish** | VFX, son, caméra shake | Particules sur saut, trail, screen shake |
| **Weight** | Sensation de masse/gravité | Courbes d'accélération, momentum |
| **Control** | Précision et tolérance | Coyote time, input buffering |
| **Juice** | Sur-réaction visuelle | Tout bouge et réagit aux actions |
| **Camera** | Suivi et framing | Interpolation, lead, bound |

### Coyote Time & Input Buffering (code pattern)

```gdscript
# Godot — Coyote Time
extends CharacterBody2D

var coyote_timer := 0.0
const COYOTE_TIME := 0.1  # 100ms

func _process(delta: float) -> void:
    if is_on_floor():
        coyote_timer = COYOTE_TIME
    else:
        coyote_timer -= delta
    
    if Input.is_action_just_pressed("sauter") and coyote_timer > 0:
        sauter()
        coyote_timer = 0
```

```csharp
// Unity — Input Buffering
public class BufferSaut : MonoBehaviour
{
    private float _sautBufferTimer;
    private const float BufferTime = 0.15f;

    void Update()
    {
        if (Input.GetButtonDown("Jump"))
            _sautBufferTimer = BufferTime;
        else
            _sautBufferTimer -= Time.deltaTime;
        
        if (_sautBufferTimer > 0 && EstAuSol())
        {
            Sauter();
            _sautBufferTimer = 0;
        }
    }
}
```

---

## 4. Level Design — Flowchart et Beat Chart

### Beat Chart (Rythme de la session)

```
Émotion ↑
  │   Intro → Apprentissage → Défi → Récompense → Pause → Boss → Climax
  │     │        │            │         │          │       │       │
  │     😊      🤔          😤        🎉        😌     😱      🎊
  └─────────────────────────────────────────────────────────────→ Temps
```

### Golden Path (Chemin critique)
1. **Tutorial** caché dans les premiers niveaux (pas de texte, learning by doing)
2. **Nouvelle mécanique** toutes les 3-5 minutes
3. **Combinaison** des mécaniques apprises (test de maîtrise)
4. **Pacing** : pic → calme → pic (courbe sinusoïdale de difficulté)

### Règle des 3 C (Cinéma interactif)
- **Character** (avatar, silhouette lisible)
- **Camera** (angle, suivi, transitions)
- **Control** (input, feedback, accessibilité)

---

## 5. Équilibrage (Balancing)

### Formule de difficulté progressive

```
# Difficulté = Base * (1 + Niveau^x)
PUISSANCE_ENNEMI = 10 * (1 + niveau_joueur * 0.15)
PV_ENNEMI = 50 * (1 + niveau_joueur * 0.1)
DEGATS_ENNEMI = 5 * (1 + niveau_joueur * 0.2)
```

### Courbe de progression

```python
# XP nécessaire pour atteindre niveau N
import math

def xp_pour_niveau(n: int, base: int = 100, pente: float = 1.5) -> int:
    return int(base * (n ** pente))

# XP totale pour niveau N
def xp_totale(n: int, base: int = 100, pente: float = 1.5) -> int:
    return sum(xp_pour_niveau(i, base, pente) for i in range(1, n + 1))

# Test : niveaux 1-50
for lvl in [1, 5, 10, 25, 50]:
    print(f"Niveau {lvl}: {xp_pour_niveau(lvl)} XP, Total: {xp_totale(lvl)}")
```

### Économie de jeu — Gold sink vs Gold faucet

| Source (Faucet) | Sortie (Sink) |
|----------------|---------------|
| Quêtes | Équipement |
| Loot mobs | Réparations |
| Vente items | Consommables |
| Farming | Améliorations |
| Récompenses | Skins cosmétiques |

Règle : **Faute ≥ Sink + 10%** pour inflation maîtrisée.

---

## 6. UX/UI pour Jeux Vidéo

### Principes d'Interface de Jeu

1. **HUD minimal** : réduire la charge cognitive (Diegetic UI)
2. **Feedback immédiat** : chaque action → réaction < 100ms
3. **Affordance** : les éléments interactifs doivent "parler d'eux-mêmes"
4. **Consistency** : les mêmes couleurs/icônes pour les mêmes actions

### Types de UI

```
UI Diégétique  → Dans l'univers (Holomap, visor Iron Man)
UI Spatiale    → Dans l'espace 3D (marqueurs, HP au-dessus des têtes)
UI Méta        → En dehors (menus, inventaire)
UI Non-diégétique → Score, HUD classique
```

### Pattern HUD (Mockup ascii)
```
┌──────────────────────────────────────┐
│ ♥♥♥♥♡   ◆ 42    ★ 12/25            │
│                                       │
│                                       │
│         [GAMEPLAY AREA]               │
│                                       │
│                                       │
│                  🗡️ Épée de feu       │
│                  [████████░░] 80%     │
└──────────────────────────────────────┘
```

---

## 7. Engagement et Rétention

### Boucle d'Habit Loop (Nir Eyal adapté)

```
Trigger → Action → Récompense → Investissement
   ↑                                    │
   └────────────────────────────────────┘
```

- **Trigger externe** : Notification, pub, ami qui joue
- **Action** : La plus facile possible (1 tap, 1 clic)
- **Récompense variable** : Loot aléatoire (dopamine → Skinner box)
- **Investissement** : Progression, items, social capital (plus dur de partir)

### Flow State (Csikszentmihalyi)

```
Anxiété ↑     [Zone de Flow]
        │      ╱╲
        │     ╱  ╲
        │    ╱    ╲
        │   ╱  💎  ╲
        │  ╱        ╲
        │ ╱          ╲
Ennui   │╱            ╲
        └──────────────────→ Compétence
```

Le jeu doit constamment ajuster la difficulté pour rester dans la zone de flow (Dynamic Difficulty Adjustment).

---

## 8. Playtesting et Itération

### Checklist de playtest
1. **[First Click Test]** — Le joueur clique-t-il sur la bonne première action ?
2. **[Think Aloud]** — Dire tout ce qui passe par la tête en jouant
3. **[Emotional Mapping]** — Noter les moments de frustration/joie
4. **[Bilan de Session]** — Questionnaire après 30 min de jeu

### Métriques de playtest
```
Taux de complétion du tuto      > 80%
Temps moyen premier niveau       < 5 min
Taux d'abandon au premier boss   < 40%
Session moyenne                   > 20 min (bon jeu)
                                  > 45 min (très bon jeu)
D1 Retention                      > 40%
D7 Retention                      > 20%
D30 Retention                     > 10%
```

---

## 9. Outils de Prototypage Rapide

| Outil | Usage | Exemple |
|-------|-------|---------|
| **Paper Prototype** | Mécaniques, flow, règles | Découper du papier, déplacer des pions |
| **Godot / Unity** | Prototype jouable rapide | 2D platformer en 2h |
| **Figma** | UI wireframes | Menus, HUD layouts |
| **Twine** | Narration interactive, dialogue | Arbres de choix, quêtes |
| **Tiled** | Level design 2D | Tilemaps, zones |
| **Miro / Mermaid** | Flowcharts, system diagrams | Core loop, progression |

---

## 10. Pièges Courants en Game Design

- **Feature creep** : Ajouter sans fin des mécaniques → "Kill your darlings"
- **Tutorial trop long** : Le joueur veut jouer, pas lire → apprendre en faisant
- **Pacing plat** : Même intensité tout le temps → courbe sinusoïdale obligatoire
- **RNG frustrant** : Aléatoire sans mitigation → Bad luck protection
- **Économie cassée** : Trop d'argent, rien à acheter → gold sink planning
- **Accessibilité oubliée** : Daltonisme, surdité, mobilité réduite → options inclusives
- **Playtest trop tard** : Tester seulement en fin de projet → tester dès le jour 1
