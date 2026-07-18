---
name: multi-agent-reinforcement-learning
description: "Explorer les techniques d'apprentissage par renforcement multi-agents (MARL), incluant la communication dynamique, la coordination, la décomposition des tâches et les protocoles d'entraînement décentralisés."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
tags: [MARL, apprentissage-renforcement, multi-agents, coordination, communication, CTDE]
keywords: [Multi-Agent Reinforcement Learning, CTDE, communication protocols, cooperative AI, decentralized training]
---

# Apprentissage par Renforcement Multi-Agents (MARL)

## Vue d'ensemble

L'apprentissage par renforcement multi-agents (MARL) étend le cadre classique du reinforcement learning à des environnements où plusieurs agents interagissent simultanément. Chaque agent observe l'état de l'environnement, prend des décisions, et reçoit des récompenses — mais la présence d'autres agents rend l'environnement **non-stationnaire** du point de vue de chaque apprenant.

Cette compétence couvre les aspects fondamentaux du MARL :

1. **Formalisme** : extension des MDP (Markov Decision Processes) aux jeux stochastiques.
2. **Taxonomie des régimes** : coopératif, compétitif, mixte.
3. **Paradigmes d'entraînement** : centralisé, décentralisé, CTDE (Centralized Training Decentralized Execution).
4. **Communication entre agents** : protocoles structurés, message passing, GNN.
5. **Passage à l'échelle** : factorisation de la fonction de valeur, mean-field MARL.

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Coordination de flotte (drones, robots, véhicules autonomes) | Élevée |
| Optimisation de trafic urbain (feux, flux, itinéraires) | Élevée |
| Gestion de ressources partagées (énergie, bande passante, entrepôt) | Élevée |
| Jeux compétitifs multi-agents (stratégie, trading) | Moyenne |
| Problème mono-agent standard (ex. jeu Atari classique) | Faible (préférer RL simple) |

---

## 1. Fondements mathématiques

### 1.1 Jeu stochastique (SG)

Un jeu stochastique à N agents est défini par le tuple $(S, \mathcal{A}^1, \dots, \mathcal{A}^N, P, R^1, \dots, R^N, \gamma)$ où :

- $S$ : ensemble d'états.
- $\mathcal{A}^i$ : espace d'actions de l'agent $i$.
- $P : S \times \mathcal{A}^1 \times \dots \times \mathcal{A}^N \to \Delta(S)$ : fonction de transition.
- $R^i : S \times \mathcal{A}^1 \times \dots \times \mathcal{A}^N \to \mathbb{R}$ : récompense de l'agent $i$.
- $\gamma \in [0, 1)$ : facteur d'actualisation.

L'objectif de chaque agent $i$ est de maximiser son espérance de récompense cumulée : $\mathbb{E} \left[ \sum_{t=0}^{\infty} \gamma^t R^i_t \right]$.

### 1.2 Taxonomie des régimes MARL

| Régime | Type de récompense | Exemple |
|---|---|---|
| **Coopératif** | $R^1 = R^2 = \dots = R^N$ | Robots collaborant à une tâche commune |
| **Compétitif** | $R^1 = -R^2$ (jeu à somme nulle) | Jeu d'échecs, trading opposé |
| **Mixte** | Récompenses indépendantes ou partiellement alignées | Trafic routier, enchères |

### 1.3 Non-stationnarité

Dans MARL, la politique $\pi^i(a^i \mid s)$ de l'agent $i$ dépend de l'état $s$, mais la transition vers $s'$ dépend des actions de **tous** les agents :

$$
s_{t+1} \sim P(\cdot \mid s_t, a^1_t, \dots, a^N_t)
$$

Quand un autre agent met à jour sa politique, la distribution des transitions change du point de vue de l'agent $i$ — c'est la **non-stationnarité**, le défi central du MARL.

---

## 2. Paradigmes d'entraînement

### 2.1 Centralized Training Decentralized Execution (CTDE)

CTDE est le paradigme dominant : les agents sont entraînés avec accès à l'information globale (états et actions de tous), mais exécutent de manière décentralisée (chaque agent n'utilise que ses observations locales).

```
┌──────────────────┐
│   Entraînement   │  ← Accès global (tous états × toutes actions)
│   Centralisé     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Exécution      │  ← Chaque agent n'utilise que ses observations locales
│   Décentralisée  │
└──────────────────┘
```

### 2.2 Implémentation : CTDE avec QMIX

QMIX factorise la fonction de valeur globale $Q_\text{tot}$ comme une combinaison monotone des fonctions de valeur individuelles $Q_i$ :

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class ReseauQMIX(nn.Module):
    """Réseau de mélange QMIX pour MARL coopératif."""

    def __init__(self, n_agents: int, dim_etat: int, dim_action: int, dim_embedding: int = 64):
        super().__init__()
        self.n_agents = n_agents

        # Réseaux individuels (agents partagent les poids ou non)
        self.reseaux_agents = nn.ModuleList([
            nn.Sequential(
                nn.Linear(dim_etat, dim_embedding),
                nn.ReLU(),
                nn.Linear(dim_embedding, dim_embedding),
                nn.ReLU(),
                nn.Linear(dim_embedding, dim_action),
            )
            for _ in range(n_agents)
        ])

        # Hyper-réseaux pour les poids du mélangeur
        self.hyper_w1 = nn.Linear(dim_etat, dim_embedding * n_agents)
        self.hyper_w2 = nn.Linear(dim_etat, dim_embedding)
        self.hyper_b1 = nn.Linear(dim_etat, dim_embedding)
        self.hyper_b2 = nn.Linear(dim_etat, 1)

    def forward(self, etats: torch.Tensor) -> torch.Tensor:
        """Calcule Q_tot à partir des états et actions.

        Args:
            etats: Tenseur (batch, n_agents, dim_etat).

        Returns:
            Q_tot valeurs (batch, n_actions_tot).
        """
        batch_size = etats.shape[0]

        # Q_i pour chaque agent
        q_i = torch.stack([
            reseau(etats[:, i]) for i, reseau in enumerate(self.reseaux_agents)
        ], dim=1)  # (batch, n_agents, n_actions)

        # État global (concaténation)
        etat_global = etats.reshape(batch_size, -1)

        # Poids du mélangeur
        w1 = torch.abs(self.hyper_w1(etat_global)).reshape(
            batch_size, self.n_agents, -1
        )
        b1 = self.hyper_b1(etat_global).reshape(batch_size, -1, 1)
        w2 = torch.abs(self.hyper_w2(etat_global)).reshape(
            batch_size, -1, 1
        )
        b2 = self.hyper_b2(etat_global)

        # Q_tot = mélange monotone
        q_hidden = F.elu(torch.bmm(q_i, w1) + b1)
        q_tot = (torch.bmm(q_hidden, w2) + b2).squeeze(-1)

        return q_tot
```

### 2.3 MARL complètement décentralisé (IQL)

Independent Q-Learning (IQL) traite chaque agent comme un apprenant RL indépendant, ignorant les autres agents :

```python
class AgentIQL:
    """Agent Q-Learning indépendant pour MARL décentralisé."""

    def __init__(self, dim_etat: int, dim_action: int, lr: float = 1e-3,
                 gamma: float = 0.99, epsilon: float = 0.1):
        self.q_network = nn.Sequential(
            nn.Linear(dim_etat, 128),
            nn.ReLU(),
            nn.Linear(128, dim_action),
        )
        self.optimiseur = torch.optim.Adam(self.q_network.parameters(), lr=lr)
        self.gamma = gamma
        self.epsilon = epsilon

    def selectionner_action(self, etat: np.ndarray) -> int:
        """Sélection epsilon-gloutonne (décentralisée : n'utilise que l'état local).

        Args:
            etat: Observation locale de l'agent.

        Returns:
            Action sélectionnée.
        """
        if np.random.random() < self.epsilon:
            return np.random.randint(self.q_network[-1].out_features)

        with torch.no_grad():
            q_vals = self.q_network(torch.FloatTensor(etat))
        return int(q_vals.argmax().item())

    def mettre_a_jour(self, etat, action, recompense, etat_suivant, termine):
        """Met à jour Q via l'équation de Bellman (indépendamment des autres agents)."""
        etat_t = torch.FloatTensor(etat)
        etat_suivant_t = torch.FloatTensor(etat_suivant)

        q_courant = self.q_network(etat_t)[action]
        q_suivant = self.q_network(etat_suivant_t).max() if not termine else 0.0
        cible = recompense + self.gamma * q_suivant

        perte = F.mse_loss(q_courant, torch.tensor(cible))
        self.optimiseur.zero_grad()
        perte.backward()
        self.optimiseur.step()
```

---

## 3. Communication entre agents

### 3.1 Pourquoi communiquer ?

| Bénéfice | Description |
|---|---|
| **Partage d'observation** | Un agent voit ce qu'un autre ne voit pas |
| **Coordination** | Éviter les conflits d'actions (ex. deux robots vers le même objet) |
| **Apprentissage accéléré** | Transmission de politiques apprises (knowledge transfer) |

### 3.2 Message Passing avec GNN

```python
import torch.nn as nn

class CommunicateurGNN(nn.Module):
    """Couche de communication entre agents basée sur un GNN (message passing)."""

    def __init__(self, dim_etat: int, dim_message: int = 32):
        super().__init__()
        self.encoder_message = nn.Linear(dim_etat, dim_message)
        self.aggregateur = nn.Linear(dim_message * 2, dim_message)
        self.decodeur = nn.Linear(dim_message + dim_etat, dim_etat)

    def forward(self, etats: torch.Tensor, matrice_adjacence: torch.Tensor) -> torch.Tensor:
        """Fait passer des messages entre agents connectés.

        Args:
            etats: Tenseur (n_agents, dim_etat).
            matrice_adjacence: Tenseur booléen (n_agents, n_agents) — qui parle à qui.

        Returns:
            États mis à jour après communication (n_agents, dim_etat).
        """
        n_agents = etats.shape[0]
        messages = self.encoder_message(etats)  # (n_agents, dim_message)

        # Agrégation des messages entrants
        messages_aggreges = []
        for i in range(n_agents):
            voisins = matrice_adjacence[i].nonzero(as_tuple=True)[0]
            if len(voisins) > 0:
                msg_voisins = messages[voisins].mean(dim=0)
            else:
                msg_voisins = torch.zeros_like(messages[0])
            messages_aggreges.append(msg_voisins)

        messages_aggreges = torch.stack(messages_aggreges)

        # Mise à jour des états avec les messages reçus
        entrees = torch.cat([messages_aggreges, etats], dim=-1)
        return self.decodeur(entrees)
```

### 3.3 Apprentissage de protocoles de communication

Les agents peuvent apprendre **quand** et **quoi** communiquer :

```python
class AgentAvecCommunication:
    """Agent MARL avec protocole de communication appris."""

    def __init__(self, dim_etat: int, dim_action: int, dim_message: int = 16):
        # Politique de communication : génère un message
        self.reseau_emission = nn.Sequential(
            nn.Linear(dim_etat, 32),
            nn.ReLU(),
            nn.Linear(32, dim_message),
        )
        # Gating : décide si le message est envoyé
        self.gating = nn.Sequential(
            nn.Linear(dim_etat, 1),
            nn.Sigmoid(),
        )
        # Politique d'action : combine état et messages reçus
        self.reseau_action = nn.Sequential(
            nn.Linear(dim_etat + dim_message, 64),
            nn.ReLU(),
            nn.Linear(64, dim_action),
        )

    def emettre_message(self, etat: torch.Tensor) -> tuple[torch.Tensor, float]:
        """Génère un message et décide s'il est envoyé.

        Args:
            etat: État local de l'agent.

        Returns:
            Tuple (message, probabilité d'envoi).
        """
        message = self.reseau_emission(etat)
        proba_envoi = self.gating(etat)
        # Pendant l'entraînement, échantillonner depuis Bernoulli(proba_envoi)
        envoyer = torch.bernoulli(proba_envoi) > 0.5
        return message if envoyer else torch.zeros_like(message), proba_envoi

    def agir(self, etat: torch.Tensor, messages_recus: torch.Tensor) -> int:
        """Sélectionne une action basée sur l'état local et les messages reçus.

        Args:
            etat: État local de l'agent.
            messages_recus: Messages reçus des autres agents (agrégés).

        Returns:
            Action sélectionnée.
        """
        entrees = torch.cat([etat, messages_recus], dim=-1)
        return self.reseau_action(entrees).argmax().item()
```

---

## 4. Applications MARL

### 4.1 Coordination de drones

```python
from marl_library.simulation import configure_agents, initialize_environment, train_agents

def entrainer_flotte_drones(n_drones: int = 5, n_epochs: int = 100) -> dict:
    """Entraîne une flotte de drones pour une mission de couverture coopérative.

    Args:
        n_drones: Nombre de drones dans la flotte.
        n_epochs: Nombre d'épisodes d'entraînement.

    Returns:
        Métriques de performance (récompense moyenne, taux de couverture).
    """
    environnement = initialize_environment("couverture_cooperative", n_agents=n_drones)
    agents = configure_agents(n_agents=n_drones, algorithme="qmix")

    resultats = train_agents(
        agents=agents,
        env=environnement,
        n_episodes=n_epochs,
        evaluer_tous=10,  # Évaluer tous les 10 épisodes
    )

    return analyser_performance(resultats)
```

### 4.2 Gestion de trafic urbain

| Agent | Action | Récompense |
|---|---|---|
| Feu de signalisation (intersection) | Durée du feu vert/rouge | Réduction du temps d'attente moyen |
| Véhicule autonome | Choix d'itinéraire | Temps de trajet individuel |
| Centre de régulation | Modification des priorités | Flux global maximisé |

---

## 5. Pièges courants (Pitfalls)

### 5.1 Non-stationnarité ignorée

> **Problème** : Traiter MARL comme N problèmes RL indépendants (IQL) ignore la non-stationnarité, conduisant à des politiques instables.

**Solution** : Utilisez le paradigme CTDE. Si IQL est nécessaire, stabilisez avec :
- **Hysteretic Q-learning** : taux d'apprentissage asymétrique pour les récompenses positives/négatives.
- **Experience replay centralisé** : stocke les transitions de tous les agents.

### 5.2 Crédit assignment dans les tâches coopératives

> **Problème** : Quand la récompense est globale (tous les agents reçoivent la même récompense), comment attribuer le crédit à chaque agent ?

**Solution** : Utilisez des mécanismes de **factorisation de la valeur** :
- **VDN** (Value Decomposition Networks) : $Q_\text{tot} = \sum_i Q_i$.
- **QMIX** : $Q_\text{tot} = f(Q_1, \dots, Q_N)$ avec contrainte de monotonie.
- **QTRAN** : relaxation de la contrainte de monotonie.

### 5.3 Passage à l'échelle

> **Problème** : Avec N agents, la dimension de l'espace d'actions conjoint est $|\mathcal{A}|^N$, explosive.

**Solution** : Utilisez des méthodes **mean-field** (approximation du champ moyen) où chaque agent interagit avec la distribution moyenne des autres agents plutôt qu'avec chaque agent individuellement.

### 5.4 Exploration inefficace

> **Problème** : Dans les espaces d'états-actions conjoints, l'exploration aléatoire est extrêmement inefficace.

**Solution** : Implémentez une exploration structurée :
- **Exploration par curiosité** : récompense intrinsèque pour les états inconnus.
- **Parameter space noise** : bruit ajouté aux poids du réseau, pas aux actions.

---

## 6. Checklist de validation

- [ ] Le régime MARL est-il correctement identifié (coopératif, compétitif, mixte) ?
- [ ] Le paradigme d'entraînement choisi (CTDE, IQL, mean-field) est-il adapté au nombre d'agents ?
- [ ] Un mécanisme de factorisation de la valeur est-il implémenté (VDN, QMIX, QTRAN) ?
- [ ] La non-stationnarité est-elle traitée (pas de simples IQL pour N > 2) ?
- [ ] Les agents peuvent-ils communiquer (message passing, protocole appris) ?
- [ ] Le passage à l'échelle est-il assuré (mean-field, ou décomposition) ?
- [ ] L'exploration est-elle structurée (curiosité, paramètre noise) ?
- [ ] Les métriques de performance incluent-elles la récompense moyenne par agent ?
- [ ] L'environnement de simulation (Gym, SMAC) est-il configuré et reproductible ?
- [ ] Les dépendances (PyTorch, RLlib, ou PettingZoo) sont-elles installées ?

---

## 7. Extensions et intégrations

### 7.1 Frameworks MARL

| Framework | Particularité | Langage |
|---|---|---|
| [PettingZoo](https://pettingzoo.farama.org/) | API Gym pour multi-agents | Python |
| [SMAC](https://github.com/oxwhirl/smac) | StarCraft Multi-Agent Challenge | Python |
| [RLlib](https://docs.ray.io/en/latest/rllib/) | MARL distribué (Ray) | Python |
| [EPyMARL](https://github.com/uoe-agents/epymarl) | Implémentations de référence | Python |

### 7.2 Compétences complémentaires

- **`research-multi-agent-complex-tasks`** : pour la planification de tâches complexes dans un cadre multi-agents.
- **`agentic-research-and-arxiv`** : pour la veille sur les publications MARL récentes.

---

## 8. Références

- `references/marl_algorithms_comparison.md` : comparaison détaillée des algorithmes MARL (IQL, VDN, QMIX, MADDPG, MAPPO).
- `scripts/marl_training_loop.py` : boucle d'entraînement MARL générique avec support CTDE.
- `scripts/marl_communication_benchmark.py` : benchmark des protocoles de communication.

---

*Documentation maintenue par EVA Agent — Dernière mise à jour : 2025*
