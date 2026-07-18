---
name: reinforcement-learning-research
description: >-
  Compétence professionnelle en recherche en apprentissage par renforcement
  suivie sur arXiv. Couvre le RL profond, le RL multi-agents, le RL basé sur
  modèle, le RL hors ligne, l'exploration, la théorie du RL, et les
  applications du RL en robotique, jeux et modèles de langage.
category: research
---

# Compétence en Recherche en Apprentissage par Renforcement

## Présentation

La recherche en apprentissage par renforcement (RL) sur arXiv est répartie entre cs.LG, cs.AI, cs.MA, cs.RO et stat.ML avec environ 44 000+ articles au total étiquetés "reinforcement learning". Cette compétence fournit une structure pour suivre, évaluer et synthétiser la recherche en RL.

## Domaines de Recherche Principaux

### 1. RL Profond (cs.LG, cs.AI)
**Algorithmes fondamentaux** :
- **Méthodes basées sur la valeur** : DQN, Rainbow, C51 (DQN catégoriel), QR-DQN
- **Méthodes de gradient de politique** : REINFORCE, PPO, TRPO, A2C/A3C
- **Méthodes acteur-critique** : SAC, TD3, DDPG, IMPALA
- **Apprentissage hors politique** : Retrace, Vtrace, corrections d'importance
- **RL distributionnel** : Apprentissage de la distribution des retours, régression quantile

### 2. RL Multi-Agents (cs.MA)
**Densité arXiv** : ~78 entrées/semaine dans cs.MA (en croissance rapide)

- **Entraînement centralisé avec exécution décentralisée (CTDE)** : QMIX, VDN, MADDPG, MAPPO
- **MARL coopératif** : Décomposition de valeur, attribution de crédit, formation de récompense
- **MARL compétitif** : Jeux à somme nulle, équilibre de Nash, minimax
- **MARL à motifs mixtes** : Dilemmes sociaux, émergence de coopération, négociation
- **Communication** : Communication émergente, protocoles, attention
- **RL décentralisé** : Apprenants indépendants, méthodes basées sur le consensus
- **Applications** : Conduite autonome, essaims de drones, robotique

### 3. RL Basé sur Modèle (cs.LG, cs.RO)
- **Modèles du monde** : Dreamer, DreamerV2/V3, MuZero, EfficientZero
- **Planification** : Monte Carlo tree search, méthode de l'entropie croisée
- **Dynamiques latentes** : RSSM, PlaNet, planification par simulateur appris
- **Incertitude du modèle** : Ensembles, dynamiques bayésiennes, incertitude épistémique
- **Modèles du monde incarnés** : Modèles 4D pour la manipulation robotique (RynnWorld-4D)
- **Modèles conditionnés par l'action** : Téléopération numérique par modèles du monde

### 4. RL Hors Ligne (Offline RL) (cs.LG)
- **Méthodes conservatrices** : CQL, IQL, BCQ, BRAC
- **Q-learning implicite** : IQL, apprentissage dans l'échantillon
- **Modélisation de séquences** : Decision Transformer, Trajectory Transformer
- **Hors ligne vers en ligne** : Fine-tuning, adaptation
- **RL hors ligne sécurisé** : Satisfaction de contraintes, sécurité conservative

### 5. Exploration et Motivation Intrinsèque
- **Exploration par curiosité** : ICM, RND, exploration par désaccord
- **Exploration information-théorique** : Empowerment, gain d'information
- **Recherche de nouveauté** : Nouveauté d'état, exploration de l'espace des paramètres
- **RL orienté objectif** : Hindsight experience replay, exploration d'objectifs

### 6. Théorie du RL (stat.ML, cs.LG)
- **Complexité d'échantillonnage** : Bornes PAC, bornes de regret, analyse à échantillon fini
- **Compromis exploration-exploitation** : Bandits multi-bras, bandits contextuels
- **Programmation dynamique approchée** : Approximation de fonction de valeur, évaluation de politique
- **RL inverse** : MaxEnt IRL, RL adversaire, RL par préférences

### 7. RL pour le Langage et les LLMs
**Domaine de forte densité émergente** (ICML'26 Workshop RLxF) :
- **RLHF** : Apprentissage par renforcement à partir de feedback humain, PPO pour LLMs
- **RLAIF** : IA constitutionnelle, auto-jeu
- **RLxF** : Apprentissage par renforcement à partir de feedback du monde
- **Modèles de récompense de processus** : Signaux de récompense denses pour les chaînes de raisonnement
- **GRPO** : Apprentissage par renforcement par groupes

### 8. Environnements et Références RL
- **Jeux** : Atari, Procgen, NetHack, SMAC, jeux de combat (FootsiesGym — RLC 2026)
- **Contrôle continu** : MuJoCo, DM Control, Isaac Gym, Brax
- **Navigation** : Habitat, AI2Thor, MetaWorld, ManiSkill
- **Multi-agents** : SMACv2, Melting Pot, Overcooked
- **Agents LLM** : AgentBench, WebArena, SWE-Bench

## Conférences Clés (Signal dans le Champ Comments)
- **NeurIPS**, **ICML**, **ICLR** : Articles RL de premier plan
- **RLC** (Reinforcement Learning Conference) : Nouvelle conférence dédiée au RL
- **IROS**, **ICRA**, **CoRL** : Robotique + RL
- **AAMAS** : Systèmes multi-agents
- **Ateliers RLC/ICML** : RL spécialisé (ex : RLxF Workshop)

## Tendances Récentes Notables (Mi-2026)
1. **RL à partir de feedback du monde (RLxF)** : Modèles du monde pour l'alignement du raisonnement physique
2. **MARL pour systèmes réels** : Robotique, essaims de drones, gestion de batteries
3. **Jeux à information imparfaite** : Jeux de combat comme références à somme nulle
4. **RL + LLMs** : Modèles de raisonnement entraînés par RL, modèles de récompense de processus
5. **Modèles du monde pour la robotique** : Modèles incarnés 4D, téléopération conditionnée par l'action

## Références Pratiques

Ce skill contient des références pour l'implémentation pratique du RL :

- **`references/dreamerv3-training-patterns.md`** — Patterns concrets pour
  l'entraînement DreamerV3 : architecture 2 GPUs, bugs fréquents (replay
  buffer parameter swap, HOLD collapse), curriculum learning, spread/slippage
  variables, features multi-timeframes. Inclut le fix définitif V5 (reward_head
  à action explicite sur GPU dédié). À charger avant de travailler sur
  un projet RL concret (entraînement, debugging, optimisation).

- **`references/dreamerv3-final-verdict.md`** — Verdict final après 10+
  itérations de correctifs : DreamerV3 ne fonctionne pas pour le trading
  (RSSM ignore les observations, reward_head collapse vers la moyenne).
  Liste exhaustive des correctifs testés et leur échec. Recommande ES
  ou PPO comme alternatives.

- **`references/evolution-strategies-trading.md`** — Architecture et
  patterns pour Evolution Strategies appliqué au trading. Fitness = PnL
  pur (pas de value function), population naturelle, 30% exploration.
  Inclut le test synthétique de capacité (marché trending) et les
  hyperparamètres optimaux pour 8 actions FTMO.

## Comment Effectuer la Veille
- **Flux principaux** : `/list/cs.LG/recent` + `/list/cs.AI/recent`
- **Multi-agents spécifique** : `/list/cs.MA/recent` (78 entrées/semaine — gérable)
- **Robotique + RL** : `/list/cs.RO/recent`
- **Recherche par requête** : `https://arxiv.org/search/?query=reinforcement+learning&searchtype=all`
- **Surveillance des cross-lists** : cs.MA ⇄ cs.AI, cs.RO, cs.LG
- **Mots-clés** : "reinforcement learning", "RLHF", "world model", "MARL", "exploration", "credit assignment"