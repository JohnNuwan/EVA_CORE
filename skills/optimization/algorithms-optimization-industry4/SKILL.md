---
name: optimization-algorithms-industry4
description: "Analyser, sélectionner et implémenter des algorithmes d'optimisation pour les problématiques Industrie 4.0 : ordonnancement, allocation de ressources, maintenance prédictive et logistique."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [optimization, algorithms, genetic, pso, reinforcement-learning, scheduling, industry4, predictive-maintenance]
    related_skills: [algorithms-optimization-industry4, ai-foundations-exploration, multi-agent-reinforcement-learning]
---

# Algorithmes d'Optimisation pour l'Industrie 4.0

## Vue d'ensemble

Cette compétence fournit une méthodologie pour explorer, sélectionner et implémenter des **algorithmes d'optimisation** adaptés aux problématiques industrielles : ordonnancement de production, allocation de ressources, maintenance prédictive, optimisation logistique et planification énergétique. Elle couvre les algorithmes classiques (génétiques, PSO) et modernes (apprentissage par renforcement, optimisation bayésienne).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'optimiser un ordonnancement de production (Job Shop, Flow Shop).
- De minimiser les coûts énergétiques d'une ligne de production.
- D'allouer des ressources (machines, opérateurs) de manière optimale.
- De planifier des tournées de maintenance ou des routes logistiques.
- D'explorer et comparer des algorithmes d'optimisation pour un cas industriel.

---

## 1. Panorama des Algorithmes

### 1.1 Tableau Comparatif

| Algorithme | Type | Complexité | Usage Principal | Avantage | Inconvénient |
|:---|:---|:---|:---|:---|:---|
| **Algorithmes Génétiques (GA)** | Évolutionnaire | O(n·g) | Ordonnancement, allocation | Robuste, parallélisable | Lent sur grands espaces |
| **PSO (Essaim de Particules)** | Bio-inspiré | O(n·i) | Optimisation continue | Simple, rapide | Convergeance prématurée |
| **Recuit Simulé (SA)** | Stochastique | O(n·t) | TSP, logistique | Garantie théorique | Réglage température délicat |
| **Colonies de Fourmis (ACO)** | Bio-inspiré | O(n²·c) | Routage, graphes | Spécialisé graphes | Coût quadratique |
| **Q-Learning / Deep Q** | RL | Variable | Contrôle, décision | Adaptatif, apprentissage | Nécessite simulateur |
| **Optimisation Bayésienne** | Probabiliste | O(n³) | Hyperparamètres, expériences | Faible nombre d'évaluations | Ne passe pas à l'échelle |
| **Branch & Bound** | Exact | O(2ⁿ) | Petits problèmes | Solution optimale garantie | NP-difficile |

### 1.2 Critères de Sélection

```
Problème à résoudre
├── Taille petite (< 100 variables) → Branch & Bound
├── Taille grande / incertain
│   ├── Continue → PSO ou Recuit Simulé
│   ├── Combinatoire → Algorithmes Génétiques
│   ├── Sur graphe → ACO
│   └── Dynamique / séquentiel → RL (Q-Learning, PPO)
└── Objectif
    ├── Solution exacte → Branch & Bound
    ├── Bonne solution rapidement → PSO, GA
    └── Adaptabilité → RL
```

---

## 2. Implémentation d'Algorithmes

### 2.1 Algorithme Génétique pour l'Ordonnancement Job Shop

```python
import random
import numpy as np

class JobShopGA:
    """Algorithme génétique pour l'ordonnancement d'atelier (Job Shop)."""

    def __init__(self, n_jobs: int, n_machines: int, processing_times: np.ndarray):
        self.n_jobs = n_jobs
        self.n_machines = n_machines
        self.processing_times = processing_times  # (n_jobs, n_machines)

    def fitness(self, chromosome: list) -> float:
        """Calcule le makespan (temps total d'exécution) d'un chromosome."""
        machine_times = [0] * self.n_machines
        job_times = [0] * self.n_jobs
        for job in chromosome:
            machine = job % self.n_machines
            job_id = job // self.n_machines
            start = max(machine_times[machine], job_times[job_id])
            end = start + self.processing_times[job_id][machine]
            machine_times[machine] = end
            job_times[job_id] = end
        return -max(machine_times)  # Négatif pour maximisation

    def crossover(self, parent1: list, parent2: list) -> list:
        """Croisement OX (Order Crossover) pour les chromosomes."""
        size = len(parent1)
        start, end = sorted(random.sample(range(size), 2))
        child = [-1] * size
        child[start:end] = parent1[start:end]
        remaining = [g for g in parent2 if g not in child]
        idx = 0
        for i in range(size):
            if child[i] == -1:
                child[i] = remaining[idx]
                idx += 1
        return child

    def mutate(self, chromosome: list, mutation_rate: float = 0.1):
        """Mutation par échange de deux gènes."""
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(chromosome)), 2)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

    def optimize(self, population_size: int = 100, generations: int = 500) -> tuple:
        """Exécute l'optimisation génétique."""
        # Initialisation
        pop = [self._random_chromosome() for _ in range(population_size)]

        for gen in range(generations):
            # Évaluation
            scores = [(self.fitness(ind), ind) for ind in pop]
            scores.sort(key=lambda x: x[0], reverse=True)

            if gen % 50 == 0:
                print(f"Génération {gen}: meilleur fitness = {-scores[0][0]:.1f}")

            # Sélection (tournoi)
            new_pop = [scores[0][1]]  # Élitisme
            while len(new_pop) < population_size:
                p1 = random.choice(pop[:population_size // 2])
                p2 = random.choice(pop[:population_size // 2])
                child = self.crossover(p1, p2)
                self.mutate(child)
                new_pop.append(child)
            pop = new_pop

        best = max(pop, key=self.fitness)
        return best, -self.fitness(best)
```

### 2.2 PSO pour l'Optimisation de Paramètres

```python
import numpy as np

class PSO:
    """Optimisation par essaim de particules (PSO)."""

    def __init__(self, n_particles: int, dim: int, bounds: np.ndarray):
        self.n_particles = n_particles
        self.dim = dim
        self.bounds = bounds
        # Initialisation
        self.positions = np.random.uniform(bounds[:, 0], bounds[:, 1], (n_particles, dim))
        self.velocities = np.random.uniform(-1, 1, (n_particles, dim))
        self.personal_best = self.positions.copy()
        self.personal_best_scores = np.full(n_particles, np.inf)
        self.global_best = np.zeros(dim)
        self.global_best_score = np.inf

    def optimize(self, objective_func, max_iter: int = 100, w: float = 0.7, c1: float = 1.5, c2: float = 2.0):
        """Exécute l'optimisation PSO.
        
        Args:
            objective_func: Fonction objectif à minimiser.
            max_iter: Nombre maximal d'itérations.
            w: Inertie.
            c1: Coefficient cognitif (attraction vers meilleur personnel).
            c2: Coefficient social (attraction vers meilleur global).
        """
        for iteration in range(max_iter):
            # Évaluation
            scores = np.array([objective_func(p) for p in self.positions])

            # Mise à jour des meilleurs personnels
            improved = scores < self.personal_best_scores
            self.personal_best[improved] = self.positions[improved]
            self.personal_best_scores[improved] = scores[improved]

            # Mise à jour du meilleur global
            best_idx = np.argmin(scores)
            if scores[best_idx] < self.global_best_score:
                self.global_best = self.positions[best_idx].copy()
                self.global_best_score = scores[best_idx]

            # Mise à jour des vitesses et positions
            r1, r2 = np.random.random((2, self.n_particles, self.dim))
            self.velocities = (w * self.velocities
                + c1 * r1 * (self.personal_best - self.positions)
                + c2 * r2 * (self.global_best - self.positions))
            self.positions += self.velocities
            
            # Contrainte aux bornes
            self.positions = np.clip(self.positions, self.bounds[:, 0], self.bounds[:, 1])

        return self.global_best, self.global_best_score
```

---

## 3. Cas d'Usage Industriels

| Problème | Algorithme | Entrées | Sorties |
|:---|:---|:---|:---|
| **Ordonnancement Job Shop** | Algo Génétique | n jobs × m machines × temps | Séquence optimale, makespan |
| **Optimisation de paramètres procédé** | PSO | Plage des paramètres | Paramètres optimaux |
| **Planification maintenance** | Recuit Simulé | Historique pannes, coûts | Planning maintenance |
| **Tournées logistiques** | ACO | Distances inter-sites | Routes optimisées |
| **Contrôle qualité adaptatif** | Q-Learning | Qualité entrante, taux rebut | Réglages machine |

---

## 4. Pièges Courants

1. **Optimum local vs global :**
   - *Erreur* : L'algorithme converge vers un minimum local et ne trouve pas la solution globale.
   - *Correction* : Augmentez la taille de population, utilisez le recuit simulé pour la diversification, ou faites du multi-start.

2. **Fonction objectif mal définie :**
   - *Erreur* : Optimiser un seul critère (ex: makespan) sans considérer les contraintes (coût, qualité).
   - *Correction* : Utilisez l'optimisation multi-objectifs (NSGA-II, Pareto front).

3. **Paramètres non réglés :**
   - *Erreur* : Utiliser les paramètres par défaut sans les adapter au problème.
   - *Correction* : Faites une recherche d'hyperparamètres (Grid Search, Bayesian Optimization).

---

## Liste de vérification

- [ ] Le problème d'optimisation est correctement formulé (variables, contraintes, objectif).
- [ ] L'algorithme est choisi en fonction de la nature du problème (combinatoire, continu, dynamique).
- [ ] Une baseline (solution aléatoire ou heuristique simple) est établie pour comparaison.
- [ ] Les paramètres de l'algorithme (taille population, taux mutation, etc.) sont réglés.
- [ ] Au moins deux algorithmes sont comparés sur le même jeu de données.
- [ ] Les résultats sont visualisés (courbe de convergence, Pareto front si multi-objectif).
- [ ] La solution optimisée est validée sur un cas réel ou simulé avant déploiement.
