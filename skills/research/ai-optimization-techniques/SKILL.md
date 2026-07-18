---
name: ai-optimization-techniques
description: "Développer et explorer des techniques d'optimisation avancées pour l'IA, couvrant l'efficacité des modèles, leur compression, et la scalabilité des algorithmes."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
tags: [optimisation, compression-modèles, quantification, pruning, fine-tuning, edge-ai]
keywords: [quantization, pruning, distillation, ONNX, TensorRT, hyperparameter-tuning]
---

# Techniques d'Optimisation en Intelligence Artificielle

## Vue d'ensemble

Cette compétence présente un catalogue structuré des techniques d'optimisation essentielles pour les modèles d'intelligence artificielle. L'objectif est de maximiser la performance tout en minimisant les coûts de calcul, la latence d'inférence et l'empreinte mémoire, que ce soit pour le déploiement sur le cloud, en embarqué (Edge), ou dans des systèmes industriels temps réel.

L'optimisation des modèles IA s'articule autour de quatre axes principaux :

1. **Compression** : réduire la taille du modèle sans sacrifier la précision.
2. **Accélération** : diminuer le temps d'inférence via des transformations structurelles.
3. **Adaptation dynamique** : ajuster le comportement du modèle en fonction des contraintes d'exécution.
4. **Optimisation post-déploiement** : affiner le modèle en continu à partir de nouvelles données.

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Déploiement d'un modèle sur un appareil contraint en mémoire (Edge, mobile, IoT) | Élevée |
| Réduction des coûts d'inférence cloud (facturation à la requête) | Élevée |
| Amélioration de la latence pour des applications temps réel (robotique, trading) | Élevée |
| Adaptation d'un modèle pré-entraîné à un nouveau domaine (fine-tuning ciblé) | Moyenne |
| Expérimentation académique sur les méthodes de compression | Moyenne |

---

## 1. Compression de modèles

### 1.1 Élagage (Pruning)

Le pruning supprime les poids ou neurones les moins importants du réseau. Deux stratégies principales :

| Type | Description | Taux de compression typique |
|---|---|---|
| **Pruning non-structuré** | Met à zéro les poids individuels en dessous d'un seuil | 50–90 % |
| **Pruning structuré** | Supprime des canaux, filtres ou couches entiers | 30–60 % |

#### Exemple avec PyTorch

```python
import torch
import torch.nn.utils.prune as prune

def appliquer_pruning_modele(modele: torch.nn.Module, taux: float = 0.3) -> torch.nn.Module:
    """Applique un pruning global non-structuré sur toutes les couches Linear.

    Args:
        modele: Modèle PyTorch à élaguer.
        taux: Proportion de poids à élaguer (entre 0 et 1).

    Returns:
        Modèle élagué.
    """
    parametres_a_elaguer = []
    for nom, module in modele.named_modules():
        if isinstance(module, torch.nn.Linear):
            parametres_a_elaguer.append((module, "weight"))

    prune.global_unstructured(
        parametres_a_elaguer,
        pruning_method=prune.L1Unstructured,
        amount=taux,
    )

    # Rendre le pruning permanent
    for module, nom in parametres_a_elaguer:
        prune.remove(module, nom)

    return modele
```

### 1.2 Quantification (Quantization)

La quantification réduit la précision numérique des poids (ex. float32 → int8), diminuant la taille mémoire et accélérant les opérations matricielles.

| Format | Taille | Précision relative | Usage recommandé |
|---|---|---|---|
| FP32 | 100 % (base) | Référence | Entraînement |
| FP16 | 50 % | ~identique | Inférence GPU |
| INT8 | 25 % | Légère perte | Inférence CPU/Edge |
| INT4 | 12,5 % | Perte modérée | Expérimentation |

```python
import torch

def quantifier_modele(modele: torch.nn.Module, mode: str = "dynamique") -> torch.nn.Module:
    """Quantifie un modèle PyTorch en mode dynamique ou statique.

    Args:
        modele: Modèle à quantifier.
        mode: 'dynamique' (poids quantifiés à l'inférence) ou 'statique' (calibration requise).

    Returns:
        Modèle quantifié.

    Raises:
        ValueError: Si le mode n'est pas 'dynamique' ou 'statique'.
    """
    if mode == "dynamique":
        return torch.quantization.quantize_dynamic(
            modele, {torch.nn.Linear, torch.nn.LSTM}, dtype=torch.qint8
        )
    elif mode == "statique":
        modele.qconfig = torch.quantization.get_default_qconfig("fbgemm")
        modele_prepare = torch.quantization.prepare(modele)
        # Une étape de calibration sur un lot représentatif serait nécessaire ici
        return torch.quantization.convert(modele_prepare)
    else:
        raise ValueError(f"Mode inconnu : {mode}. Utilisez 'dynamique' ou 'statique'.")
```

### 1.3 Distillation de connaissances (Knowledge Distillation)

Un grand modèle ("teacher") transfère son savoir à un modèle plus petit ("student") via les logits ou les représentations intermédiaires.

```python
import torch.nn.functional as F

def perte_distillation(logits_student: torch.Tensor, logits_teacher: torch.Tensor,
                       temperature: float = 4.0, alpha: float = 0.7) -> torch.Tensor:
    """Calcule la perte de distillation entre un teacher et un student.

    Args:
        logits_student: Logits du modèle student.
        logits_teacher: Logits du modèle teacher (détachés du gradient).
        temperature: Température pour adoucir les distributions de probabilité.
        alpha: Pondération entre la perte de distillation et la perte supervise.

    Returns:
        Perte de distillation scalaire.
    """
    perte_soft = F.kl_div(
        F.log_softmax(logits_student / temperature, dim=-1),
        F.softmax(logits_teacher.detach() / temperature, dim=-1),
        reduction="batchmean",
    ) * (temperature ** 2)

    return perte_soft * alpha
```

---

## 2. Optimisation dynamique

### 2.1 Recherche d'hyperparamètres (HPO)

Trois méthodes éprouvées :

| Méthode | Avantage | Inconvénient |
|---|---|---|
| Grid Search | Exhaustif | Exponentiel en dimension |
| Random Search | Bon compromis | Pas d'exploitation |
| Bayesian Optimization | Efficace (faible budget) | Complexe à implémenter |

```python
from optimization_framework import HyperOptimizer  # Exemple conceptuel

def optimiser_hyperparametres(espace: dict, donnees: Dataset,
                              iterations: int = 50) -> dict:
    """Recherche bayésienne des meilleurs hyperparamètres.

    Args:
        espace: Dictionnaire définissant l'espace de recherche
                (ex. {'lr': (1e-5, 1e-2), 'dropout': (0.1, 0.5)}).
        donnees: Jeu de données d'entraînement.
        iterations: Nombre d'itérations d'optimisation.

    Returns:
        Configuration optimale des hyperparamètres.
    """
    optimiseur = HyperOptimizer(
        modele="LSTM",
        espace_recherche=espace,
        dataset=donnees,
        methode="bayesienne",
    )
    return optimiseur.run(iterations=iterations)
```

### 2.2 Routage adaptatif

Dans les systèmes distribués, le routage adaptatif achemine chaque requête vers le modèle le plus adapté (précision vs. latence) :

```python
class RouteurAdaptatif:
    """Routeur qui sélectionne dynamiquement le modèle d'inférence optimal."""

    def __init__(self):
        self.modeles = {
            "haute-precision": {"modele": None, "cout": 10.0, "precision": 0.97},
            "rapide": {"modele": None, "cout": 1.0, "precision": 0.85},
            "edge": {"modele": None, "cout": 0.5, "precision": 0.80},
        }

    def selectionner_modele(self, requis_precision: float,
                            budget_temps: float) -> str:
        """Sélectionne le meilleur modèle selon les contraintes.

        Args:
            requis_precision: Précision minimale requise.
            budget_temps: Temps d'inférence maximum (ms).

        Returns:
            Nom du modèle sélectionné.

        Raises:
            RuntimeError: Si aucun modèle ne satisfait les contraintes.
        """
        eligibles = {
            nom: infos for nom, infos in self.modeles.items()
            if infos["precision"] >= requis_precision and infos["cout"] <= budget_temps
        }
        if not eligibles:
            raise RuntimeError("Aucun modèle ne satisfait les contraintes.")
        return min(eligibles, key=lambda n: eligibles[n]["cout"])
```

---

## 3. Optimisation post-déploiement

### 3.1 Fine-tuning continu

Le fine-tuning incrémental adapte le modèle à des distributions de données changeantes sans ré-entraînement complet :

```python
def fine_tuning_continu(modele: torch.nn.Module,
                        nouveau_dataset: torch.utils.data.DataLoader,
                        taux_apprentissage: float = 1e-5,
                        epochs: int = 3) -> torch.nn.Module:
    """Effectue un fine-tuning léger sur un modèle déployé.

    Args:
        modele: Modèle déjà déployé.
        nouveau_dataset: DataLoader contenant les nouvelles données.
        taux_apprentissage: Taux d'apprentissage réduit (typiquement 1e-5 à 1e-4).
        epochs: Nombre d'époques de fine-tuning.

    Returns:
        Modèle mis à jour.
    """
    optimiseur = torch.optim.AdamW(modele.parameters(), lr=taux_apprentissage)

    for epoch in range(epochs):
        for batch in nouveau_dataset:
            optimiseur.zero_grad()
            sortie = modele(batch["entree"])
            perte = torch.nn.functional.cross_entropy(sortie, batch["cible"])
            perte.backward()
            torch.nn.utils.clip_grad_norm_(modele.parameters(), 1.0)  # Anti-oubli
            optimiseur.step()

    return modele
```

### 3.2 Conversion pour déploiement (ONNX / TensorRT)

```python
import torch.onnx

def exporter_vers_onnx(modele: torch.nn.Module, chemin: str,
                       entree_exemple: torch.Tensor) -> None:
    """Exporte un modèle PyTorch vers le format ONNX.

    Args:
        modele: Modèle PyTorch à exporter.
        chemin: Chemin de sortie du fichier .onnx.
        entree_exemple: Tenseur d'entrée typique pour la trace.
    """
    torch.onnx.export(
        modele,
        entree_exemple,
        chemin,
        export_params=True,
        opset_version=17,
        input_names=["input"],
        output_names=["output"],
        dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
    )
```

---

## 4. Pièges courants (Pitfalls)

### 4.1 Quantification sans calibration

> **Problème** : La quantification statique sans calibration préalable peut dégrader la précision de 10 à 30 %.

**Solution** : Utilisez toujours un petit lot de calibration représentatif du domaine cible avant de quantifier.

### 4.2 Pruning trop agressif

> **Problème** : Un taux de pruning > 80 % non-structuré détruit la capacité du modèle à généraliser.

**Solution** : Appliquez un pruning itératif avec évaluation après chaque étape. Arrêtez-vous dès que la perte de précision dépasse 2 %.

### 4.3 Fine-tuning sans protection contre l'oubli catastrophique

> **Problème** : Le fine-tuning sur un petit jeu de données spécifique écrase les connaissances générales du modèle.

**Solution** : Utilisez un taux d'apprentissage réduit (×0.01 du taux initial) et la méthode EWC (Elastic Weight Consolidation) ou Replay.

### 4.4 Framework lock-in

> **Problème** : Un modèle optimisé avec TensorRT est lié à NVIDIA, un modèle CoreML lié à Apple.

**Solution** : Exportez d'abord vers ONNX (intermédiaire standard), puis convertissez vers le format cible.

---

## 5. Checklist de validation

- [ ] Le modèle original a-t-il été benchmarké (précision, latence, taille) avant optimisation ?
- [ ] La méthode de compression choisie (pruning, quantification, distillation) est-elle adaptée au cas d'usage ?
- [ ] La calibration de quantification a-t-elle été effectuée sur un jeu représentatif ?
- [ ] Le pruning a-t-il été appliqué de manière itérative avec validation intermédiaire ?
- [ ] Le fine-tuning utilise-t-il un taux d'apprentissage réduit (< 1e-4) ?
- [ ] Une protection contre l'oubli catastrophique est-elle en place ?
- [ ] Le format d'export (ONNX, TensorRT, CoreML) est-il compatible avec la cible de déploiement ?
- [ ] Les tests d'inférence incluent-ils des mesures de latence (P50, P99) ?
- [ ] Le modèle optimisé a-t-il été validé sur un jeu de test indépendant ?
- [ ] Une procédure de rollback est-elle définie en cas de dérive post-déploiement ?

---

## 6. Intégrations et extensions

### 6.1 Frameworks recommandés

| Framework | Usage principal | Lien |
|---|---|---|
| [TensorRT](https://developer.nvidia.com/tensorrt) | Optimisation GPU NVIDIA | Export ONNX → TensorRT |
| [ONNX Runtime](https://onnxruntime.ai/) | Inférence multiplateforme | Exécution directe .onnx |
| [PyTorch Model Optimization Toolkit](https://pytorch.org/docs/stable/quantization.html) | Quantification & pruning PyTorch | Intégration native |
| [TensorFlow Lite](https://www.tensorflow.org/lite) | Déploiement mobile/Edge | Conversion TFLite |

### 6.2 Compétences complémentaires

- **`memory-management-ai`** : pour la gestion de la mémoire lors de l'inférence de grands modèles.
- **`probabilistic-modeling-ai`** : pour l'optimisation bayésienne des hyperparamètres.

---

## 7. Références

- `references/benchmark_protocols.md` : protocoles standardisés pour mesurer vitesse et précision.
- `scripts/quantize_and_benchmark.py` : script de quantification automatisée avec benchmarking.
- `templates/model_optimization_report.md` : template de rapport d'optimisation.

---

*Documentation maintenue par Helios Agent — Dernière mise à jour : 2025*
