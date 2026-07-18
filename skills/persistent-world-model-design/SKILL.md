---
name: persistent-world-model-design
description: "Concevoir des modèles du monde persistants capables de maintenir un état global cohérent en l'absence d'observation directe."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [world-model, persistent-state, simulation, robotics, computer-vision, autonomous-systems]
    related_skills: [agentic-systems-design, spatial-decodable-image-generation, autonomous-agent-evolution-strategy]
---

# Conception de Modèles du Monde Persistants

## Vue d'ensemble

Un **modèle du monde persistant** (Persistent World Model) est un système capable de maintenir une représentation interne cohérente de son environnement, même lorsque celui-ci n'est pas directement observable. Contrairement aux modèles traditionnels qui ne fonctionnent que sur des flux d'observation continus, un modèle persistant conserve un **état global** qui évolue de manière autonome entre les observations.

Cette compétence s'appuie sur les principes décrits dans l'article fondateur : [Current World Models Lack a Persistent State Core (arXiv:2606.20545)](https://arxiv.org/abs/2606.20545).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De concevoir un système autonome (robot, véhicule) capable de raisonner sur l'état du monde hors-ligne.
- D'implémenter un noyau d'état persistant pour un modèle de simulation.
- D'améliorer la cohérence temporelle d'un système de vision ou de prédiction.
- De développer un jumeau numérique avec mémoire d'état à long terme.

---

## 1. Architecture d'un Modèle du Monde Persistant

### 1.1 Composants Fondamentaux

| Composant | Description | Rôle |
|:---|:---|:---|
| **Noyau d'État (State Core)** | Représentation latente continue de l'environnement | Stocke et met à jour la connaissance du monde |
| **Encodeur d'Observation** | Transforme les entrées sensorielles en représentations latentes | Met à jour le noyau d'état |
| **Module de Prédiction** | Projette l'état futur à partir de l'état courant | Anticipe les conséquences des actions |
| **Décodeur** | Reconstruit les observations à partir de l'état latent | Permet la visualisation et la vérification |
| **Module de Mise à Jour Autonome** | Fait évoluer l'état même sans nouvelle observation | Maintient la cohérence temporelle |

### 1.2 Principe de Fonctionnement

```
Observation → [Encodeur] → État Latent → [Prédiction] → État Futur
                                ↓                              ↓
                     [Mise à Jour Autonome]           [Décodeur] → Sortie
                                ↓
                         Nouvel État
```

L'état latent est mis à jour périodiquement par le module de mise à jour autonome, même en l'absence de nouvelles observations, permettant au modèle de simuler le passage du temps.

---

## 2. Implémentation d'un Noyau d'État Persistant

### 2.1 Structure du Noyau d'État en Python (PyTorch)

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class PersistentStateCore(nn.Module):
    """Noyau d'état persistant avec mise à jour autonome."""

    def __init__(self, state_dim: int = 256, action_dim: int = 8):
        super().__init__()
        self.state_dim = state_dim
        # Encodeur d'observation → espace latent
        self.encoder = nn.Sequential(
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, state_dim),
        )
        # Module de transition autonome (sans observation)
        self.transition = nn.GRUCell(state_dim, state_dim)
        # Module de transition avec action (contrôlé)
        self.action_projection = nn.Linear(state_dim + action_dim, state_dim)
        # Décodeur état → observation reconstruite
        self.decoder = nn.Sequential(
            nn.Linear(state_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
        )

    def update_from_obs(self, state: torch.Tensor, obs: torch.Tensor) -> torch.Tensor:
        """Met à jour l'état à partir d'une nouvelle observation."""
        obs_feat = self.encoder(obs)
        return self.transition(obs_feat, state)

    def update_autonomous(self, state: torch.Tensor, steps: int = 1) -> torch.Tensor:
        """Met à jour l'état de manière autonome pendant `steps` pas de temps."""
        for _ in range(steps):
            state = self.transition(state)
        return state

    def update_with_action(self, state: torch.Tensor, action: torch.Tensor) -> torch.Tensor:
        """Met à jour l'état en fonction d'une action appliquée."""
        combined = torch.cat([state, action], dim=-1)
        return self.action_projection(combined)
```

### 2.2 Gestion de l'Incertitude

Un modèle du monde persistant doit gérer l'augmentation de l'incertitude lorsque le temps depuis la dernière observation s'allonge :

```python
class UncertaintyAwareCore(PersistentStateCore):
    """Noyau avec estimation d'incertitude."""

    def __init__(self, state_dim: int = 256):
        super().__init__(state_dim)
        self.uncertainty_head = nn.Linear(state_dim, 1)

    def forward(self, state: torch.Tensor, steps_since_obs: int) -> tuple:
        """Retourne (état, incertitude)."""
        uncertainty = torch.sigmoid(self.uncertainty_head(state))
        # L'incertitude croît avec le nombre de pas sans observation
        uncertainty = uncertainty * (1.0 + 0.1 * steps_since_obs)
        uncertainty = torch.clamp(uncertainty, 0.0, 1.0)
        return state, uncertainty
```

---

## 3. Applications Pratiques

| Domaine | Application | Bénéfice du Modèle Persistant |
|:---|:---|:---|
| **Robotique mobile** | Navigation avec odométrie visuelle intermittente | Maintien de la localisation entre deux frames |
| **Jumeaux numériques** | Simulation d'usine avec données capteurs espacées | Prédiction d'état entre les cycles de lecture |
| **Jeux vidéo / Simulation** | Mondes persistants avec zones non observées | Comportement crédible des entités hors-champ |
| **Conduite autonome** | Perception avec occultations temporaires | Prédiction de la trajectoire des obstacles masqués |

---

## 4. Pièges Courants

1. **Dérive de l'état latent (State Drift) :**
   - *Erreur* : L'état latent dérive vers des valeurs non informatives après plusieurs mises à jour autonomes sans observation.
   - *Correction* : Ajoutez un terme de régularisation qui ancre l'état à des observations récentes, ou un mécanisme de réinitialisation partielle.

2. **Confiance excessive (Overconfidence) :**
   - *Erreur* : Le modèle est aussi confiant après 100 pas sans observation qu'immédiatement après une observation.
   - *Correction* : Implémentez toujours une tête d'incertitude qui croît avec le temps écoulé.

3. **Effondrement modal :**
   - *Erreur* : Le noyau d'état collapse vers une représentation unique quelle que soit l'entrée.
   - *Correction* : Utilisez une perte de diversité (VIB, β-VAE loss) et normalisez régulièrement l'état latent.

---

## Liste de vérification

- [ ] Le noyau d'état persistant implémente une mise à jour autonome sans observation.
- [ ] L'incertitude est estimée et croît avec le temps depuis la dernière observation.
- [ ] Les encodeur et décodeur sont symétriques (dimensions compatibles).
- [ ] Un mécanisme de régularisation prévient la dérive de l'état latent.
- [ ] Le modèle est testé sur un scénario avec occultation temporaire des observations.
- [ ] Les temps de calcul du module de transition autonome sont compatibles avec l'application temps réel cible.

