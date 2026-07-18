---
name: multi-agent-systems-research
description: >-
  Compétence professionnelle en recherche sur les systèmes multi-agents suivie
  sur arXiv sous cs.MA. Couvre la coordination multi-agents, la théorie des
  jeux, la communication entre agents, les systèmes multi-agents basés sur
  LLM, l'intelligence en essaim, l'intelligence collective et la prise de
  décision distribuée.
category: research
---

# Compétence en Recherche sur les Systèmes Multi-Agents (cs.MA)

## Présentation

Les systèmes multi-agents (cs.MA) sur arXiv reçoivent environ 78 nouvelles soumissions par semaine, couvrant des protocoles de décision théoriques aux systèmes multi-agents basés sur LLM. Cette compétence fournit une structure pour naviguer dans le paysage de la recherche multi-agents.

## Domaines de Recherche Principaux

### 1. Prise de Décision Multi-Agents et Théorie des Jeux
- **Modèles théoriques des jeux** : Jeux sous forme normale/extensive, jeux stochastiques
- **Concepts d'équilibre** : Équilibre de Nash, équilibre corrélé, équilibre grossièrement corrélé
- **Conception de mécanismes** : Enchères, vote, choix social, compatibilité des incitations
- **Théorie des jeux coopératifs** : Valeur de Shapley, négociation, formation de coalitions
- **Protocoles de décision** : Prise de décision structurée dans les conversations multi-agents LLM

### 2. Apprentissage par Renforcement Multi-Agents (MARL)
**Fortement cross-listé avec cs.LG et cs.AI** :
- **CTDE** : Architectures d'entraînement centralisé avec exécution décentralisée
- **Décomposition de valeur** : QMIX, QTRAN, VDN, QMIX pondéré
- **Gradients de politique MARL** : MADDPG, MAPPO, COMA, FACMAC
- **Coordination** : Apprentissage de rôles, communication émergente, protocoles

### 3. Systèmes Multi-Agents Basés sur LLM
**Domaine en forte croissance** : ~9 840 articles pour "agentic AI agents"
- **Orchestration d'agents LLM** : Mémoire par graphe de faits (Danus)
- **Mémoire avec préservation des conflits** : Résolution déterministe de conflits (StateFuse)
- **Protocoles de décision** : Comment les agents LLM parviennent à un consensus
- **Limites informationnelles** : Dynamiques d'attracteur dans les économies d'agents LLM

### 4. Communication et Protocoles entre Agents
- **Langages de communication** : ACL, protocoles FIPA, actes de langage
- **Communication émergente** : Jeux référentiels, signalisation, langage ancré
- **MCP (Model Context Protocol)** : Agents activés par MCP pour l'automatisation réseau
- **Systèmes de mémoire partagée** : Graphes de faits, mémoire distribuée

### 5. Intelligence en Essaim et Comportement Collectif
- **Robotique en essaim** : Flocking, formation, allocation de tâches
- **Dynamique des foules topologique** : Analyse des régimes de dynamique des foules
- **Prise de décision collective** : Consensus dans les essaims, algorithmes inspirés des abeilles
- **Auto-organisation** : Motifs émergents à partir d'interactions locales

### 6. IA Distribuée et Planification Multi-Agents
- **Optimisation sous contraintes distribuée** : DCOP, ADOPT, DPOP
- **Planification multi-agents** : HTN distribué, planification coordonnée
- **Allocation de tâches** : Enchères, marchés, protocoles de contrat

### 7. Interaction Homme-Agent et Équipes
- **Équipes humain-IA** : Planification à initiative mixte, modèles mentaux partagés
- **Interaction homme-robot** : Interaction acoustique (AcoustoBots)
- **Explicabilité dans les MAS** : Explications des actions des agents, négociation transparente

### 8. Applications
- **Automatisation réseau** : Cycle de vie IPoDWDM via MCP (ECOC 2026)
- **Défense anti-drones** : MARL avec prise en compte du délai (IROS 2026)
- **Réseaux intelligents** : Gestion d'énergie distribuée
- **Gestion du trafic** : Gestion d'intersections autonomes

## Théories et Cadres Clés
| Cadre | Type | Description |
|-------|------|-------------|
| **CTDE** | Paradigme d'entraînement | Critiques centralisés, acteurs décentralisés |
| **Décomposition de valeur** | Algorithme MARL | Factorisation de Q jointe en utilités par agent |
| **Bien-être social** | Évaluation | Utilitariste, égalitariste, Nash |
| **Jeux potentiels** | Classe de jeux | Convergence garantie vers l'équilibre de Nash |
| **Jeux de Markov** | Modèle | Jeux stochastiques avec transitions d'état |
| **Jeux à champ moyen** | Approximation | Comportement limite des grandes populations |

## Articles Notables Récents (Mi-2026)
1. **Decision Protocols in Multi-Agent LLM Conversations** — Master, Univ. Göttingen
2. **Danus: Orchestrating Mathematical Reasoning Agents with Fact-Graph Memory** — cs.AI/cs.MA
3. **StateFuse: Deterministic Conflict-Preserving Memory** — cs.AI
4. **Information Limits in Economies of Frontier LLM Agents** — Pré-enregistré
5. **MCP-Enabled Agentic AI for Autonomous Network Lifecycle Automation** — ECOC 2026
6. **Delay-Aware MARL for Counter-UAS** — IROS 2026

## Comment Effectuer la Veille
- **Flux principal** : `/list/cs.MA/recent` (78 entrées/semaine)
- **Scan des cross-lists** : `/list/cs.AI/recent` et `/list/cs.LG/recent` en filtrant par titres multi-agents
- **Mots-clés** : "multi-agent", "MARL", "coordination", "agent communication", "swarm", "consensus"