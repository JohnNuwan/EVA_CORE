---
name: creative-problem-solving-ai
description: "Explorer les techniques de résolution créative de problèmes pour des agents d'IA industriels, incluant le raisonnement analogique, la reformulation et l'exploration multi-modèles."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
tags: [cps, créativité, résolution-problèmes, raisonnement-analogique, exploration, agents-adaptatifs]
keywords: [Creative Problem Solving, CPS, raisonnement latéral, reformulation, exploration stratégies]
---

# Résolution Créative de Problèmes en IA

## Vue d'ensemble

La résolution créative de problèmes (Creative Problem Solving — CPS) est un ensemble de méthodologies permettant à un agent IA de faire face à des situations inédites pour lesquelles aucune solution pré-encodée n'existe. Contrairement aux approches déterministes qui appliquent des règles fixes, la CPS mobilise des mécanismes de **reformulation**, de **raisonnement analogique** et d'**exploration multi-modèles** pour générer des solutions originales et adaptées au contexte.

Cette compétence est particulièrement critique dans les environnements industriels imprévisibles — pannes non documentées, configurations inédites, objectifs contradictoires — où les solutions connues échouent systématiquement.

### Principes fondamentaux

| Principe | Description |
|---|---|
| **Divergence / Convergence** | Générer un maximum d'idées (divergence), puis les filtrer (convergence) |
| **Reformulation** | Changer la représentation du problème pour débloquer des solutions |
| **Analogie** | Transposer une solution d'un domaine connu vers le problème actuel |
| **Itération adaptative** | Essai-erreur avec ajustement continu de la stratégie |

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Le problème rencontré n'a pas de solution documentée dans la base de connaissances | Élevée |
| Plusieurs approches contradictoires existent et doivent être évaluées | Élevée |
| Le problème implique des contraintes multiples et changeantes | Élevée |
| Une solution rapide (bricolée) est acceptable comme premier jet | Moyenne |
| La solution optimale est connue et peut être exécutée directement | Faible (préférer une exécution directe) |

---

## 1. Reformulation des problèmes

### 1.1 Cadre de reformulation

La reformulation consiste à ré-encoder le problème sous un angle différent pour révéler des solutions cachées :

```
Problème initial : "Comment réduire la latence d'inférence ?"
     ↓
Reformulation 1 : "Comment exécuter le même calcul avec moins d'opérations ?"
Reformulation 2 : "Comment tolérer une latence plus élevée sans dégrader l'expérience ?"
Reformulation 3 : "Comment déporter une partie du calcul en parallèle ?"
     ↓
Nouvelles solutions (inaccessibles depuis l'énoncé initial)
```

### 1.2 Implémentation Python

```python
import re
from typing import Callable

class ReformulateurDeProbleme:
    """Moteur de reformulation utilisant des patrons de transformation linguistique."""

    PATRONS = [
        (r"réduire (.+)", "Comment tolérer {0} plus élevé sans conséquence ?"),
        (r"augmenter (.+)", "Comment éliminer le besoin de {0} ?"),
        (r"éviter (.+)", "Comment transformer {0} en avantage ?"),
        (r"optimiser (.+)", "Comment supprimer complètement {0} ?"),
    ]

    def reformuler(self, enonce: str) -> list[str]:
        """Génère des reformulations alternatives d'un problème.

        Args:
            enonce: Énoncé original du problème.

        Returns:
            Liste de reformulations.
        """
        resultats = []
        for patron, template in self.PATRONS:
            match = re.search(patron, enonce, re.IGNORECASE)
            if match:
                resultats.append(template.format(match.group(1)))
        return resultats if resultats else [enonce]


# Exemple d'utilisation
reformulateur = ReformulateurDeProbleme()
reformulations = reformulateur.reformuler(
    "Comment réduire la consommation mémoire du modèle ?"
)
for r in reformulations:
    print(f"→ {r}")
```

---

## 2. Raisonnement analogique

### 2.1 Mécanisme de transfert跨-domaine

Le raisonnement analogique identifie des similarités structurelles entre le problème courant et un problème connu dans un autre domaine, puis adapte la solution.

```
Domaine source : Ordonnancement de tâches usine
    ↕ Analogie structurelle (graphe de dépendances, contraintes de ressources)
Domaine cible : Routage de paquets réseau
    ↕ Adaptation
Solution : Algorithme de plus court chemin avec fenêtres temporelles
```

### 2.2 Implémentation d'un moteur d'analogie simple

```python
class MoteurAnalogique:
    """Moteur de raisonnement analogique basé sur des vecteurs de similarité."""

    def __init__(self):
        self.base_connaissances = {
            "flux_trafic_urbain": {
                "concept": "régulation de flux avec feux tricolores",
                "solution": "algorithme de contention avec priorités tournantes",
                "vecteur": [1.0, 0.8, 0.3, 0.1],
            },
            "optimisation_stock": {
                "concept": "gestion de stock avec demande variable",
                "solution": "politique (s, S) avec seuil de réapprovisionnement",
                "vecteur": [0.3, 0.2, 0.9, 0.7],
            },
            "ordonnancement_taches": {
                "concept": "séquençage de tâches sur machines parallèles",
                "solution": "algorithme glouton avec priorité EDD",
                "vecteur": [0.7, 0.9, 0.4, 0.3],
            },
        }

    def trouver_analogie(self, probleme: str, vecteur_probleme: list[float]) -> str:
        """Trouve la meilleure analogie pour un problème donné.

        Args:
            probleme: Description textuelle du problème.
            vecteur_probleme: Encodage vectoriel du problème (4 dimensions).

        Returns:
            Solution adaptée du domaine source le plus proche.

        Raises:
            ValueError: Si la base de connaissances est vide.
        """
        if not self.base_connaissances:
            raise ValueError("La base de connaissances est vide.")

        meilleur_score = -1.0
        meilleure_solution = "Aucune analogie trouvée."

        for _, source in self.base_connaissances.items():
            score = sum(
                a * b for a, b in zip(vecteur_probleme, source["vecteur"])
            ) / (sum(v ** 2 for v in vecteur_probleme) ** 0.5 *
                 sum(v ** 2 for v in source["vecteur"]) ** 0.5)

            if score > meilleur_score:
                meilleur_score = score
                meilleure_solution = (
                    f"Analogie avec '{source['concept']}' "
                    f"(similarité: {score:.2f})\n"
                    f"Solution adaptée : {source['solution']}"
                )

        return meilleure_solution
```

---

## 3. Exploration multi-modèles

### 3.1 Architecture de l'agent adaptatif

L'agent CPS ne se limite pas à un seul algorithme. Il maintient un portfolio de stratégies et les active selon le contexte :

```python
import random
from abc import ABC, abstractmethod
from typing import Any

class Strategie(ABC):
    """Interface de base pour une stratégie de résolution."""

    @abstractmethod
    def executer(self, probleme: dict) -> Any:
        """Exécute la stratégie sur le problème donné."""

    @abstractmethod
    def nom(self) -> str:
        """Retourne le nom de la stratégie."""

class StrategieGloutonne(Strategie):
    def executer(self, probleme: dict) -> Any:
        valeurs = sorted(probleme.get("options", []), reverse=True)
        return {"strategie": "gloutonne", "solution": valeurs[:1]}

    def nom(self) -> str:
        return "gloutonne"

class StrategieRechercheLocale(Strategie):
    def executer(self, probleme: dict) -> Any:
        meilleur = None
        meilleur_score = float("-inf")
        for _ in range(100):
            candidat = random.choice(probleme.get("options", []))
            if candidat > meilleur_score:
                meilleur_score = candidat
                meilleur = candidat
        return {"strategie": "recherche_locale", "solution": [meilleur]}

    def nom(self) -> str:
        return "recherche_locale"

class AgentCPS:
    """Agent de résolution créative de problèmes."""

    def __init__(self):
        self.strategies: list[Strategie] = [
            StrategieGloutonne(),
            StrategieRechercheLocale(),
        ]
        self.historique_performance: dict[str, float] = {}

    def ajouter_strategie(self, strategie: Strategie) -> None:
        """Ajoute une nouvelle stratégie au portfolio de l'agent."""
        self.strategies.append(strategie)

    def resoudre(self, probleme: dict, profondeur: int = 3) -> list[dict]:
        """Tente de résoudre un problème en explorant plusieurs stratégies.

        Args:
            probleme: Dictionnaire décrivant le problème (clé 'options' pour les valeurs candidates).
            profondeur: Nombre d'itérations d'exploration.

        Returns:
            Liste des tentatives ordonnées par score décroissant.
        """
        tentatives = []
        for _ in range(profondeur):
            for strategie in self.strategies:
                resultat = strategie.executer(probleme)
                score = abs(
                    resultat["solution"][0] - probleme.get("cible", 0)
                ) if resultat["solution"] else float("inf")
                tentatives.append((score, resultat))
                self.historique_performance[strategie.nom()] = (
                    self.historique_performance.get(strategie.nom(), 0) + score
                )

        return [t for _, t in sorted(tentatives, key=lambda x: x[0])]
```

---

## 4. Pièges courants (Pitfalls)

### 4.1 Convergence prématurée

> **Problème** : L'agent sélectionne la première solution "acceptable" sans explorer suffisamment l'espace des possibles, passant à côté de solutions bien meilleures.

**Solution** : Imposez un temps minimum de divergence (phase d'exploration pure) avant toute convergence. Utilisez une politique epsilon-gloutonne : 30 % d'exploration aléatoire, 70 % d'exploitation.

### 4.2 Analogies forcées

> **Problème** : Établir des analogies superficielles entre des domaines qui ne partagent qu'une similarité de surface (ex. comparer un réseau de neurones à un réseau social).

**Solution** : Validez l'analogie à trois niveaux : (1) similarité structurelle, (2) similarité de contrainte, (3) similarité d'objectif. Si un seul niveau est satisfait, rejetez l'analogie.

### 4.3 Paralysie par surcharge d'options

> **Problème** : L'agent dispose de trop de stratégies et passe plus de temps à choisir qu'à résoudre.

**Solution** : Limitez le portfolio actif à 5 stratégies maximum. Utilisez un mécanisme de bandit manchot (Thompson Sampling) pour sélectionner la stratégie la plus prometteuse en fonction de l'historique.

### 4.4 Absence de critère d'arrêt

> **Problème** : L'agent itère indéfiniment sans détecter qu'il a atteint une solution satisfaisante.

**Solution** : Définissez un critère d'arrêt explicite dès le début :

```python
class CritereArret:
    def __init__(self, seuil_qualite: float = 0.9, iterations_max: int = 100):
        self.seuil_qualite = seuil_qualite
        self.iterations_max = iterations_max
        self.compteur = 0

    def doit_arreter(self, meilleure_qualite: float) -> bool:
        self.compteur += 1
        return (meilleure_qualite >= self.seuil_qualite or
                self.compteur >= self.iterations_max)
```

---

## 5. Checklist de validation

- [ ] Le problème a-t été reformulé sous au moins 3 angles différents ?
- [ ] Au moins une analogie a-t été identifiée avec un domaine source ?
- [ ] La phase de divergence (exploration) a-t-elle duré suffisamment (≥ 30 % du budget total) ?
- [ ] Les critères d'arrêt sont-ils définis (seuil de qualité + itérations max) ?
- [ ] Les stratégies explorées sont-elles suffisamment diverses (au moins 3 familles) ?
- [ ] La solution retenue a-t été évaluée sur des données de validation ?
- [ ] Un mécanisme de rollback est-il prévu si la solution dégrade le système ?
- [ ] L'agent conserve-t-il un historique des tentatives (pour apprentissage futur) ?
- [ ] Les dépendances logicielles (numpy, scikit-learn) sont-elles installées ?
- [ ] Le rapport de résolution inclut-il le chemin de décision (stratégies testées, scores) ?

---

## 6. Extensions et intégrations

### 6.1 Apprentissage par renforcement pour la sélection de stratégies

Combinez CPS avec MARL (Multi-Agent Reinforcement Learning) pour qu'un agent méta-apprenne à sélectionner la meilleure stratégie :

```python
# Concept : bandit manchot contextuel pour la sélection de stratégie
class SelectionneurStrategieRL:
    def __init__(self, strategies: list[Strategie]):
        self.strategies = strategies
        self.compteurs = {s.nom(): 1 for s in strategies}     # Pseudo-comptes
        self.recompenses = {s.nom(): 0.0 for s in strategies}

    def selectionner(self) -> Strategie:
        """Thompson Sampling pour sélectionner la meilleure stratégie."""
        scores = {
            s: random.betavariate(
                self.recompenses[s.nom()] + 1,
                self.compteurs[s.nom()] - self.recompenses[s.nom()] + 1,
            )
            for s in self.strategies
        }
        return max(scores, key=scores.get)
```

### 6.2 Compétences complémentaires

- **`probabilistic-modeling-ai`** : pour l'exploration bayésienne de l'espace des solutions.
- **`multi-agent-reinforcement-learning`** : pour la coordination de plusieurs agents CPS.

---

## 7. Références

- `references/techniques_divergence.md` : catalogue détaillé de techniques créatives (SCAMPER, TRIZ, brainwriting).
- `scripts/cps_agent_framework.py` : squelette complet d'agent CPS avec persistance.
- `templates/solution_report_template.md` : template de rapport de résolution CPS.

---

*Documentation maintenue par Helios Agent — Dernière mise à jour : 2025*
