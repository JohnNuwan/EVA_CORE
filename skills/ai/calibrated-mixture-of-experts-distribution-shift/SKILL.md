---
name: calibrated-mixture-of-experts-distribution-shift
description: "Implémenter et calibrer des modèles Mixture-of-Experts (MoE) robustes aux changements de distribution, avec routage dur/doux et rééquilibrage adverse."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [mixture-of-experts, moe, calibration, distribution-shift, machine-learning, deep-learning, routing]
    related_skills: [ai-foundations-exploration, ai-optimization-techniques, llm-frameworks-exploration]
---

# Calibration de Mixture-of-Experts sous Changement de Distribution

## Vue d'ensemble

Cette compétence couvre l'implémentation et la calibration de **modèles Mixture-of-Experts (MoE)** capables de maintenir des prédictions précises et bien calibrées même lorsque la distribution des données d'entrée change (distribution shift). Basée sur l'article [Toward Calibrated Mixture-of-Experts Under Distribution Shift (arXiv:2606.20544)](https://arxiv.org/abs/2606.20544), elle aborde le routage dynamique, la calibration par expert, et les mécanismes adverses de rééquilibrage.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter un modèle MoE robuste aux changements de distribution.
- D'améliorer la calibration probabiliste d'un modèle existant.
- De concevoir un système de routage dynamique (dur/doux) pour experts spécialisés.
- D'appliquer des techniques de rééquilibrage adverse pour la robustesse.
- De déployer un modèle MoE dans un environnement non stationnaire (données changeantes).

---

## 1. Architecture Mixture-of-Experts (MoE)

### 1.1 Structure Fondamentale

Un modèle MoE se compose de :

1. **n Experts** : Sous-modèles spécialisés (réseaux de neurones).
2. **Routeur (Gate)** : Module qui détermine quel(s) expert(s) activer pour chaque entrée.
3. **Mécanisme de combinaison** : Pondération des sorties des experts.

```
Entrée x
    ↓
[Routeur] → poids w₁, w₂, ..., wₙ
    ↓
[Expert 1] → y₁ ─┐
[Expert 2] → y₂ ─┼── [Combinaison pondérée] → y
...               │
[Expert n] → yₙ ─┘
    ↓
Sortie finale y = Σ w_i · y_i
```

### 1.2 Types de Routage

| Routage | Description | Avantage | Inconvénient |
|:---|:---|:---|:---|
| **Dur (Hard)** | Un seul expert sélectionné (top-1) | Efficacité computationnelle | Perte d'information |
| **Doux (Soft)** | Pondération de tous les experts | Utilisation de toute la capacité | Coût calcul plus élevé |
| **Top-k** | Sélection des k meilleurs experts | Bon compromis | Réglage du k |

---

## 2. Implémentation d'un MoE Calibré

### 2.1 Architecture de Base

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class Expert(nn.Module):
    """Expert spécialisé dans un sous-domaine."""

    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)

class CalibratedGate(nn.Module):
    """Routeur calibré avec estimation de confiance."""

    def __init__(self, input_dim: int, n_experts: int):
        super().__init__()
        self.router = nn.Linear(input_dim, n_experts)
        # Tête de calibration (Expected Calibration Error)
        self.calibration_head = nn.Linear(input_dim, 1)

    def forward(self, x: torch.Tensor) -> tuple:
        """Retourne (poids des experts, score de calibration)."""
        logits = self.router(x)
        weights = F.softmax(logits, dim=-1)
        confidence = torch.sigmoid(self.calibration_head(x))
        return weights, confidence

class CalibratedMoE(nn.Module):
    """Modèle Mixture-of-Experts avec calibration intégrée."""

    def __init__(self, input_dim: int, n_experts: int, expert_hidden: int,
                 output_dim: int, routing: str = "top2"):
        super().__init__()
        self.n_experts = n_experts
        self.routing = routing
        self.gate = CalibratedGate(input_dim, n_experts)
        self.experts = nn.ModuleList([
            Expert(input_dim, expert_hidden, output_dim)
            for _ in range(n_experts)
        ])

    def forward(self, x: torch.Tensor) -> tuple:
        """Retourne (sortie, poids, calibration)."""
        weights, confidence = self.gate(x)

        if self.routing == "soft":
            # Routage doux : tous les experts pondérés
            expert_outputs = torch.stack([e(x) for e in self.experts], dim=1)
            output = torch.sum(weights.unsqueeze(-1) * expert_outputs, dim=1)

        elif self.routing.startswith("top"):
            k = int(self.routing[3:])  # "top2" → k=2
            top_weights, top_indices = torch.topk(weights, k, dim=-1)
            output = torch.zeros_like(x[:, :self.experts[0](x).shape[-1]])
            for i in range(k):
                expert_out = self.experts[top_indices[:, i]](x)
                output += top_weights[:, i:i+1] * expert_out
        else:
            raise ValueError(f"Routage non supporté : {self.routing}")

        return output, weights, confidence
```

### 2.2 Perte de Calibration

```python
class CalibrationLoss(nn.Module):
    """Perte de calibration basée sur l'Expected Calibration Error (ECE)."""

    def __init__(self, n_bins: int = 10):
        super().__init__()
        self.n_bins = n_bins

    def forward(self, confidences: torch.Tensor, predictions: torch.Tensor,
                targets: torch.Tensor) -> torch.Tensor:
        """Calcule l'ECE pour la calibration.

        Args:
            confidences: Scores de confiance (B, 1).
            predictions: Prédictions du modèle (B, C).
            targets: Cibles (B,).

        Returns:
            torch.Tensor: Perte de calibration.
        """
        # Probabilités prédites pour la classe choisie
        probs = F.softmax(predictions, dim=-1)
        pred_probs, pred_classes = torch.max(probs, dim=-1)
        
        # Pondération par la confiance estimée
        calibrated_probs = pred_probs * confidences.squeeze()
        correct = (pred_classes == targets).float()

        # Discrétisation en bins
        bin_boundaries = torch.linspace(0, 1, self.n_bins + 1, device=predictions.device)
        ece = 0.0
        for i in range(self.n_bins):
            mask = (calibrated_probs > bin_boundaries[i]) & \
                   (calibrated_probs <= bin_boundaries[i + 1])
            if mask.sum() > 0:
                bin_acc = correct[mask].mean()
                bin_conf = calibrated_probs[mask].mean()
                ece += (mask.sum() / len(correct)) * abs(bin_acc - bin_conf)

        return ece
```

---

## 3. Rééquilibrage Adverse (Adversarial Rebalancing)

Pour maintenir la calibration sous changement de distribution, on introduit un mécanisme adverse :

```python
class AdversarialRebalancer(nn.Module):
    """Module de rééquilibrage adverse pour la robustesse MoE."""

    def __init__(self, feature_dim: int):
        super().__init__()
        self.discriminator = nn.Sequential(
            nn.Linear(feature_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, features: torch.Tensor, expert_weights: torch.Tensor) -> torch.Tensor:
        """Calcule la perte adverse pour équilibrer les experts.

        Args:
            features: Caractéristiques d'entrée (B, D).
            expert_weights: Poids de routage des experts (B, n_experts).

        Returns:
            torch.Tensor: Perte adverse.
        """
        # Score de déséquilibre
        imbalance_score = torch.sigmoid(self.discriminator(features))
        
        # Pénalité : les experts doivent être utilisés de manière équilibrée
        expert_usage = expert_weights.mean(dim=0)
        balance_penalty = torch.var(expert_usage)  # Faible variance = bon équilibre
        
        # Perte adverse combinée
        adv_loss = imbalance_score.mean() + balance_penalty
        return adv_loss
```

---

## 4. Pièges Courants

1. **Effondrement du routage (Routing Collapse) :**
   - *Erreur* : Le routeur envoie toujours la même entrée au même expert.
   - *Correction* : Ajoutez une perte de diversité (load balancing loss) dans le routage.

2. **Experts non calibrés individuellement :**
   - *Erreur* : Chaque expert n'est pas calibré séparément, la combinaison finale l'est encore moins.
   - *Correction* : Appliquez la perte de calibration à chaque expert avant combinaison.

3. **Changement de distribution non détecté :**
   - *Erreur* : Le MoE continue à router comme avant le shift de distribution.
   - *Correction* : Implémentez un détecteur de distribution shift (Maximum Mean Discrepancy, etc.).

---

## Liste de vérification

- [ ] Le MoE implémente un routage (dur, doux, ou top-k) avec au moins 3 experts.
- [ ] Chaque expert est calibré individuellement (perte ECE intégrée).
- [ ] La perte de calibration globale de l'ensemble est suivie et minimisée.
- [ ] Un mécanisme de load balancing (diversité de routage) est en place.
- [ ] Le modèle est testé sur un jeu de données avec distribution shift artificiel.
- [ ] Les performances (accuracy + ECE) sont comparées à un modèle dense de taille équivalente.
