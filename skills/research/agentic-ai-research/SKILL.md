---
name: agentic-ai-research
description: >-
  Compétence professionnelle en recherche sur l'IA agentique et les agents
  LLM suivie sur arXiv. Couvre les agents LLM autonomes, l'utilisation
  d'outils, le raisonnement, la planification, la génération de code, les
  cadres d'agents, les systèmes de mémoire, MCP, les modèles VLA,
  l'évaluation, la sécurité des agents et le domaine émergent de
  l'ingénierie de l'IA agentique.
category: research
---

# Compétence en Recherche sur l'IA Agentique

## Présentation

L'IA agentique est l'un des domaines de recherche les plus dynamiques sur arXiv avec ~9 840+ résultats pour "agentic AI agents". Elle couvre les agents LLM autonomes, les modèles vision-langage-action, l'orchestration multi-agents, l'utilisation d'outils, la planification et l'évaluation. Cette compétence fournit une structure pour suivre ce paysage en évolution rapide.

## Domaines de Recherche Principaux

### 1. Agents Autonomes Basés sur LLM
**Définition** : LLMs agissant comme des entités autonomes qui perçoivent, raisonnent et agissent
- **Architectures d'agents** : ReAct (Raisonnement + Action), Reflexion, AutoGPT
- **Cadres de raisonnement** : Chaîne de pensée, arbre de pensée, graphe de pensée
- **Cycle Observation → Planification → Exécution** : Boucles d'agents fermées
- **Autoréflexion** : Agents qui critiquent et améliorent leurs propres sorties
- **Mémoire d'agent** : Mémoire à court/long terme, épisodique, sémantique
- **Utilisation d'outils** : Appels API, exécution de code, navigation web

### 2. Modèles Vision-Langage-Action (VLA)
- **Architectures VLA** : Grands modèles vision-langage + têtes d'action pour la robotique
- **Lift3D-VLA** : Élévation des modèles VLA vers la géométrie 3D
- **Alignement du raisonnement physique** : Résultats d'action visuelle (VAORA — ICML'26)
- **Raisonnement incarné** : Combinaison de la compréhension du langage avec l'interaction physique

### 3. Cadres d'Agents et Boîtes à Outils
**Densité arXiv** : Très élevée (cs.AI, cs.SE)
- **MCP (Model Context Protocol)** : Protocole standardisé pour l'interaction avec les outils
- **Orchestration d'agents** : Cadres agnostiques pour flux multi-agents (LCA)
- **Test d'agents** : LogicHunter — test des cadres d'agents LLM
- **Systèmes de mémoire** : Danus (graphe de faits), StateFuse (mémoire déterministe)
- **Évaluation** : AgentBench, SWE-bench, WebArena, GAIA

### 4. Raisonnement et Planification Agentique
- **Agents de raisonnement mathématique** : Orchestration d'agents spécialisés (Danus)
- **Agents de génération de code** : Flux SQL natifs IA (Spider 2.0-AIFunc)
- **Planification multi-étapes** : Planification hiérarchique, décomposition de tâches
- **Découverte scientifique** : Conception expérimentale pour l'IA agentique (stat.ME)

### 5. Mémoire et Connaissances pour Agents
- **Mémoire par graphe de faits** : Graphes de connaissances comme mémoire d'agent
- **Mémoire avec préservation des conflits** : Gestion des contradictions (StateFuse)
- **RAG (Génération augmentée par récupération)** : RAG par embedding, hybride, agentique
- **Mémoire épisodique** : Rejeu d'expérience, mémoire de trajectoires

### 6. Orchestration Multi-Agents
- **Communication agent-agent** : Protocoles structurés, négociation en langage naturel
- **Délégation basée sur les rôles** : Agents spécialisés pour différentes sous-tâches
- **Consensus et vote** : Protocoles de décision pour collectifs d'agents
- **Débat et critique** : Vérification collaborative des faits

### 7. Sécurité, Alignement et Évaluation
- **Sécurité des agents** : Supervision, sandboxing, contrôle des capacités
- **Alignement** : Alignement des valeurs pour les agents autonomes
- **Évaluation des agents** : Références, tests adversaires, test de généralisation
- **Tests par oracle** : Détection de défaillances logiques (LogicHunter)

### 8. Applications
- **Découverte scientifique** : Automatisation d'expériences, découverte de modèles
- **Santé** : Support clinique, agents médicaux multimodaux (LCA)
- **Génie logiciel** : Débogage autonome, revue de PR, refactorisation
- **Automatisation réseau** : Gestion du cycle de vie IPoDWDM via MCP
- **Ingénierie des données** : Flux SQL natifs IA

## Taxonomie des Architectures d'Agents

```
                    ┌──────────────────┐
                    │    Perception    │
                    │ (Vision, Texte,  │
                    │  Environnement)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │     Mémoire     │
                    │ (Graphe de faits │
                    │  / KV / Épisod.)│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Raisonnement  │
                    │ (CoT / Plan /    │
                    │  Décomposition)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Action/Outil   │
                    │ (API / Code /    │
                    │  Actionneur)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    Feedback     │
                    │ (Observation /   │
                    │  RL / Critique)  │
                    └──────────────────┘
```

## Articles Notables Récents (Mi-2026)
1. **An Experimental Design Approach to Evaluating Agentic AI's Autonomous Model Discovery** — stat.ME/cs.AI
2. **Spider 2.0-AIFunc: Text-to-SQL vers Flux SQL Natifs IA** — cs.AI
3. **LogicHunter: Testing LLM Agent Frameworks with an Agentic Oracle** — cs.SE
4. **Danus: Orchestrating Mathematical Reasoning Agents with Fact-Graph Memory** — cs.AI/cs.MA
5. **StateFuse: Deterministic Conflict-Preserving Memory** — cs.AI
6. **MCP-Enabled Agentic AI for Autonomous Network Lifecycle Automation** — ECOC 2026
7. **The Large Cancer Assistant (LCA): Model-Agnostic Orchestration Framework** — cs.AI/cs.LG

## Comment Effectuer la Veille
- **Principal** : `/list/cs.AI/recent` (1 283 entrées/semaine — filtrer par "agent")
- **Requête** : `https://arxiv.org/search/?query=agentic+AI+agents&searchtype=all`
- **Mots-clés** : "agentic", "autonomous agent", "LLM agent", "VLA", "tool-use", "agent framework", "MCP"
- **Cross-list** : cs.AI ⇄ cs.MA, cs.CL, cs.RO, stat.ME