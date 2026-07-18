---
name: spatial-decodable-image-generation
description: "Accélérer la génération d'images auto-régressive par détection spéculative spatiale (SSD) pour une inference plus rapide."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [computer-vision, image-generation, speculative-decoding, SSD, autoregressive, machine-learning]
    related_skills: [persistent-world-model-design, ai-foundations-exploration, comfyui]
---

# Génération d'Images par Détection Spéculative Spatiale (SSD)

## Vue d'ensemble

La **détection spéculative spatiale** (Spatially Speculative Decoding — SSD) est une technique avancée qui accélère la génération d'images auto-régressive en prédisant simultanément **plusieurs pixels adjacents** dans une structure 2D. Contrairement au décodage auto-régressif pixel par pixel (séquentiel), SSD exploite la redondance spatiale naturelle des images pour générer des blocs entiers de pixels en une seule passe, réduisant drastiquement le nombre d'itérations d'inférence.

Cette compétence s'appuie sur les principes du décodage spéculatif appliqué à la génération d'images.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'accélérer un pipeline de génération d'images auto-régressif.
- D'optimiser un modèle de type Image GPT, PixelCNN, ou ViT génératif.
- De réduire la latence d'inférence pour la génération d'images haute résolution.
- D'explorer des techniques de décodage spéculatif au-delà du domaine textuel.

---

## 1. Principe du Décodage Spéculatif Spatial

### 1.1 Concept Fondamental

Le décodage auto-régressif standard génère une image pixel par pixel ou patch par patch :

```
Image complète = [P₁] → [P₂] → [P₃] → ... → [Pₙ]   (n étapes séquentielles)
```

Avec SSD, on prédit un bloc de pixels à la fois :

```
Image complète = [P₁ P₂ P₃ P₄] → [P₅ P₆ P₇ P₈] → ...   (n/4 étapes)
```

Le **modèle spéculatif** (petit et rapide) propose des blocs entiers, tandis que le **modèle principal** (grand et précis) les valide. Si un bloc est accepté, on économise plusieurs étapes d'inférence ; s'il est rejeté, on revient à la position sûre et on régénère.

### 1.2 Architecture du Système

```
Entrée (bruit / condition) 
        ↓
  [Modèle Spéculatif Léger]  → proposition de blocs de pixels
        ↓
  [Modèle Principal (Target)] → validation des blocs proposés
        ↓
  [Acceptation/Rejet] → Mise à jour de l'image générée
        ↓
  Image finale
```

---

## 2. Implémentation d'un Pipeline SSD

### 2.1 Modèle Spéculatif Spatial

```python
import torch
import torch.nn as nn

class SpatialSpeculator(nn.Module):
    """Modèle spéculatif léger qui propose des blocs de pixels."""

    def __init__(self, block_size: int = 4, latent_dim: int = 128):
        super().__init__()
        self.block_size = block_size
        # Encodeur de contexte (pixels déjà générés)
        self.context_encoder = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, latent_dim, kernel_size=3, padding=1),
        )
        # Prédicteur de bloc
        self.block_predictor = nn.Sequential(
            nn.Linear(latent_dim, latent_dim * 2),
            nn.ReLU(),
            nn.Linear(latent_dim * 2, block_size * block_size * 3),  # RGB
        )

    def forward(self, context: torch.Tensor) -> torch.Tensor:
        """Propose un bloc de pixels à partir du contexte.

        Args:
            context (torch.Tensor): Contexte d'image existant (B, 3, H, W)

        Returns:
            torch.Tensor: Bloc de pixels proposé (B, 3, block_size, block_size)
        """
        features = self.context_encoder(context).mean(dim=[2, 3])
        block_flat = self.block_predictor(features)
        return block_flat.view(-1, 3, self.block_size, self.block_size)
```

### 2.2 Mécanisme d'Acceptation/Rejet

```python
def speculative_acceptance(
    target_model: nn.Module,
    proposed_block: torch.Tensor,
    context: torch.Tensor,
    temperature: float = 1.0,
) -> tuple[torch.Tensor, bool]:
    """Valide un bloc proposé selon la distribution du modèle cible.

    Args:
        target_model: Le modèle principal (target) précis mais lent.
        proposed_block: Bloc de pixels proposé par le spéculateur.
        context: Contexte d'image existant.
        temperature: Température pour l'échantillonnage.

    Returns:
        Tuple (bloc accepté ou régénéré, booléen d'acceptation).
    """
    with torch.no_grad():
        # Distribution cible sur le prochain pixel
        target_logits = target_model(context)
        target_probs = torch.softmax(target_logits / temperature, dim=-1)

        # Distribution spéculative
        spec_logits = speculator(context)
        spec_probs = torch.softmax(spec_logits / temperature, dim=-1)

        # Ratio d'acceptation (rejection sampling)
        acceptance_ratio = target_probs / (spec_probs + 1e-8)

        if torch.rand(1) < acceptance_ratio.min():
            return proposed_block, True  # Accepté
        else:
            # Rejet : on régénère avec le modèle cible
            target_block = target_model.sample(context, temperature=temperature)
            return target_block, False
```

---

## 3. Optimisations et Réglages

### 3.1 Taille de Blot Recommandée

| Résolution Image | Taille de Blot SSD | Facteur d'Accélération Estimé |
|:---|:---|:---|
| 64×64 | 2×2 pixels | 2× – 3× |
| 128×128 | 4×4 pixels | 3× – 5× |
| 256×256 | 4×4 ou 8×8 pixels | 4× – 8× |
| 512×512 | 8×8 pixels | 5× – 10× |

### 3.2 Trade-off Précision / Vitesse

Le paramètre clé est la **température** d'échantillonnage :
- **Température basse (< 0.5)** : Taux d'acceptation élevé, mais qualité réduite.
- **Température moyenne (0.8–1.2)** : Bon équilibre recommandé.
- **Température haute (> 1.5)** : Taux d'acceptation faible, mais meilleure diversité.

---

## 4. Pièges Courants

1. **Effondrement du spéculateur :**
   - *Erreur* : Le modèle spéculatif apprend à toujours proposer la même valeur moyenne.
   - *Correction* : Entraînez le spéculateur avec une perte de diversité et variez le bloc_size.

2. **Rejet en cascade :**
   - *Erreur* : Le rejet d'un bloc force la régénération de toute la séquence suivante.
   - *Correction* : Implémentez un mécanisme de « rejet partiel » où seuls les pixels invalides du bloc sont régénérés.

3. **Surcharge mémoire du spéculateur :**
   - *Erreur* : Le spéculateur a une taille comparable au modèle principal, annulant le bénéfice.
   - *Correction* : Limitez le spéculateur à ≤ 10% des paramètres du modèle cible.

---

## Liste de vérification

- [ ] Le modèle spéculateur fait moins de 10% de la taille du modèle cible.
- [ ] Le mécanisme d'acceptation par rejection sampling est correctement implémenté.
- [ ] La taille de bloc est adaptée à la résolution d'image cible (voir tableau).
- [ ] La température d'échantillonnage est réglable et son impact est documenté.
- [ ] Un benchmark mesure le facteur d'accélération réel par rapport à la baseline auto-régressive.
- [ ] Les cas de rejet sont tracés pour analyser le taux d'acceptation moyen.

