# JEPA dans le paysage IA 2026

## Contexte

Cette référence positionne JEPA dans l'écosystème des avancées IA 2025-2026,
identifiées lors de la veille du 2 juillet 2026.

## Sources consultées

- Anthropic Engineering Blog (2025-2026) : Scaling Managed Agents, Harness Design,
  Agent Skills, Context Engineering, Claude Code auto mode
- Hugging Face Daily Papers 2026 : DeepSeek mHC, Tencent Youtu-LLM, mémoire agent
- Meta AI / FAIR : 7 repos JEPA (I-JEPA, V-JEPA, EB-JEPA, JEPA-WMS, TD-JEPA,
  3D-JEPA, Intuitive Physics)

## JEPA dans l'écosystème agentique

```
                    ┌──────────────────────────────┐
                    │     AGENT ARCHITECTURE       │
                    │         (2026 trends)        │
                    ├──────────────────────────────┤
Brain/Hands ───────│  Planner (cheap) → Workers    │
(Anthropic 04/2026) │                              │
                    │  ┌──────────┐ ┌───────────┐ │
Context Budget ────│  │ Context  │ │ Harness   │ │
                    │  │ Budget   │ │ Checkpoint│ │
Agent Skills 2.0 ──│  │          │ │ Resume    │ │
                    │  └──────────┘ └───────────┘ │
                    │                              │
                    │  ┌──────────────────────┐   │
JEPA as World ─────│  │  JEPA-WMS / V-JEPA   │   │
Model               │  │  Prédiction physique │   │
                    │  │  Planification robot │   │
                    │  └──────────────────────┘   │
                    │                              │
Smart Permissions ─│  │  Risk-based auto-approval │
                    └──────────────────────────────┘
```

## Synergies identifiées

| Composant 2026 | Variante JEPA | Application |
|---|---|---|
| **Brain/Hands** | EB-JEPA (AC Video) | Le Planner utilise AC-JEPA pour simuler les conséquences d'actions |
| **Harness Design** | JEPA-WMS | Checkpoint = état latent JEPA, resume = reprendre la prédiction |
| **Context Budget** | I-JEPA | Compression = ne garder que les patches à haute erreur de prédiction |
| **Agent Skills 2.0** | EB-JEPA | Skill "jepa-inspector" composable avec "siemens-scl-expert" |
| **Smart Permissions** | — | JEPA n'écrit pas sur le disque → risque LOW par défaut |

## Articles Anthropic clés (2025-2026)

| Date | Titre | Pertinence Helios |
|---|---|---|
| Avr 2026 | Scaling Managed Agents: Decoupling brain from hands | `agent/brain_hands.py` |
| Mar 2026 | Harness design for long-running apps | `agent/harness.py` |
| Mar 2026 | Claude Code auto mode: safer skip permissions | `agent/smart_permissions.py` |
| Fév 2026 | Building a C compiler with parallel Claudes | `agent/task_graph.py` |
| Oct 2025 | Equipping agents for the real world with Agent Skills | `agent/skills_v2.py` |
| Sep 2025 | Effective context engineering for AI agents | `agent/context_budget.py` |

## Modèles 2026 pertinents

| Modèle | Usage recommandé |
|---|---|
| DeepSeek V4 | Worker (Brain/Hands), tâches complexes |
| Claude Haiku 4.5 | Planner (Brain/Hands), cheap/fast |
| Claude Sonnet 4.5 | Worker polyvalent |
| EB-JEPA (Apache 2.0) | Inspection qualité, world model |

## Positionnement concurrentiel JEPA vs autres approches 2026

| Approche | Force | Faiblesse | JEPA vs |
|---|---|---|---|
| **LLM agents** (Claude Code) | Raisonnement général | Pas de modèle du monde physique | JEPA complète pour la robotique |
| **Diffusion models** (Sora, Flux) | Génération vidéo | Coûteux, pas prédictif | JEPA prédit sans générer |
| **RL zero-shot** (TD-JEPA, Meta Motivo) | Pas d'entraînement par tâche | Encore recherche | TD-JEPA = JEPA + RL |
| **MCP ecosystem** | Standard ouvert | Pas de composante physique | 3D-JEPA = MCP + vision 3D |