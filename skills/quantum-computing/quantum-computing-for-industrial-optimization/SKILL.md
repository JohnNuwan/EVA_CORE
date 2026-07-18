---
name: quantum-computing-for-industrial-optimization
description: "Exploiter l'informatique quantique (QAOA, recuit quantique) pour résoudre des problèmes d'optimisation industrielle complexes : ordonnancement, logistique, allocation de ressources et énergie."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [quantum, quantum-computing, qaoa, annealing, optimization, scheduling, logistics, industry40]
    related_skills: [optimization-algorithms-industry4, algorithms-optimization-industry4, ai-optimization-techniques]
---

# Optimisation Quantique pour l'Industrie 4.0

## Vue d'ensemble

Cette compétence explore comment l'**informatique quantique** peut être appliquée à l'Industrie 4.0 pour résoudre des problèmes d'optimisation complexes (NP-difficiles) comme l'ordonnancement de production, l'allocation de ressources, l'optimisation logistique et la gestion énergétique. Elle couvre les algorithmes quantiques (QAOA, recuit quantique), les plateformes disponibles (IBM Qiskit, D-Wave, AWS Braket) et les architectures hybrides classique-quantique.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'explorer le potentiel du calcul quantique pour un problème d'optimisation industriel.
- D'implémenter un prototype QAOA ou un recuit quantique sur Qiskit ou D-Wave.
- De résoudre un problème d'ordonnancement combinatoire complexe.
- D'évaluer si un problème industriel est adapté à un accélérateur quantique.
- De concevoir une architecture hybride classique-quantique.

---

## 1. Problèmes Industriels Adaptés au Quantique

### 1.1 Critères d'Adaptation

Un problème est candidat au calcul quantique si :

1. Il est **NP-difficile** ou **NP-complet** (temps de résolution classique exponentiel).
2. Il peut être formulé comme un **QUBO** (Quadratic Unconstrained Binary Optimization).
3. La taille du problème dépasse les capacités des solveurs classiques (≥ 1000 variables).
4. Une solution approchée (non exacte) est acceptable.

### 1.2 Problèmes Industriels Candidates

| Problème | Complexité | Temps Classique | Accélération Quantique Potentielle |
|:---|:---|:---|:---|
| **Job Shop Scheduling** (n machines × m jobs) | NP-difficile | Heures → jours | Quadratique à exponentielle |
| **Vehicle Routing** (n clients) | NP-difficile | Heures | Quadratique |
| **Portfolio / Resource Allocation** (n actifs) | NP-difficile | Minutes → heures | Quadratique |
| **Trajectory Optimization** | NP-difficile | Heures | Quadratique |
| **Supply Chain Network Design** | NP-difficile | Jours | Exponentielle (théorique) |

---

## 2. Formulation QUBO d'un Problème Industriel

### 2.1 Ordonnancement sous Forme QUBO

Prenons l'exemple de l'affectation de n jobs à m machines avec des contraintes de précédence.

```python
import numpy as np
from dimod import BinaryQuadraticModel
from dwave.system import DWaveSampler, EmbeddingComposite

# Problème : 3 jobs, 2 machines, 2 slots temporels
n_jobs = 3
n_machines = 2
n_slots = 2

# Variables binaires : x[i,j,t] = 1 si job i sur machine j au slot t
n_vars = n_jobs * n_machines * n_slots

# Matrice QUBO
Q = np.zeros((n_vars, n_vars))

# Contrainte : chaque job doit être affecté exactement une fois
for i in range(n_jobs):
    for j in range(n_machines):
        for t in range(n_slots):
            idx = i * n_machines * n_slots + j * n_slots + t
            Q[idx, idx] -= 2
            for j2 in range(n_machines):
                for t2 in range(n_slots):
                    if j != j2 or t != t2:
                        idx2 = i * n_machines * n_slots + j2 * n_slots + t2
                        Q[idx, idx2] += 1

# Contrainte : chaque machine ne peut traiter qu'un job par slot
for j in range(n_machines):
    for t in range(n_slots):
        vars_slot = [i * n_machines * n_slots + j * n_slots + t for i in range(n_jobs)]
        for a in range(len(vars_slot)):
            for b in range(len(vars_slot)):
                if a != b:
                    Q[vars_slot[a], vars_slot[b]] += 1
```

### 2.2 Résolution avec D-Wave

```python
# Conversion en BQM
bqm = BinaryQuadraticModel('BINARY')
for i in range(n_vars):
    for j in range(i, n_vars):
        if Q[i, j] != 0:
            bqm.add_interaction(i, j, Q[i, j] if i == j else Q[i, j] * 2)

# Exécution sur D-Wave
sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=1000, label="Job Shop QUBO")

# Meilleure solution
best = sampleset.first
print(f"Énergie : {best.energy}")
solution = [best.sample[f'x{i}'] for i in range(n_vars)]
print(f"Solution : {solution}")
```

---

## 3. Algorithmes Quantiques pour l'Optimisation

### 3.1 QAOA (Quantum Approximate Optimization Algorithm) avec Qiskit

```python
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.quantum_info import SparsePauliOp
from qiskit_algorithms import QAOA
from qiskit_algorithms.optimizers import COBYLA
from qiskit_ibm_runtime import QiskitRuntimeService, Session
import networkx as nx

# Modélisation du problème : Max-Cut (partitionnement de graphe)
G = nx.Graph()
G.add_edges_from([(0, 1), (0, 2), (1, 2), (2, 3)])

# Conversion en Hamiltonien
qubit_op = SparsePauliOp.from_list([
    ('ZZ', -0.5),  # Pour chaque arête : -(1/2)*ZZ
])  # Version simplifiée

# Configuration QAOA
qaoa = QAOA(
    sampler=None,  # Utiliser un backend réel ou simulateur
    optimizer=COBYLA(maxiter=100),
    reps=2,  # Nombre de couches QAOA
)

# Exécution
# result = qaoa.compute_minimum_eigenvalue(qubit_op)
# print(f"Valeur optimale : {result.optimal_value}")
```

### 3.2 Recuit Quantique (Quantum Annealing) avec D-Wave

```python
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod

# Problème de partitionnement simple
bqm = dimod.BQM('BINARY')
bqm.add_variable('a', -1)
bqm.add_variable('b', -1)
bqm.add_interaction('a', 'b', 2)  # Favoriser des valeurs différentes

# Exécution sur D-Wave
sampler = EmbeddingComposite(DWaveSampler())
sampleset = sampler.sample(bqm, num_reads=100)

print(sampleset)
```

---

## 4. Plateformes Quantiques Disponibles

| Plateforme | Type | Accès | Gratuité | Spécialité |
|:---|:---|:---|:---|:---|
| **IBM Qiskit** | Portes quantiques | Cloud (IBM Quantum) | Oui (10 min/mois) | QAOA, VQE, algorithmes généraux |
| **D-Wave Leap** | Recuit quantique | Cloud (D-Wave) | Oui (1 min/mois) | QUBO, optimisation combinatoire |
| **AWS Braket** | Portes + Recuit | Cloud (AWS) | Payant | Multi-plateforme |
| **Azure Quantum** | Portes + Recuit | Cloud (Azure) | Payant | Optimisation + chimie |
| **Rigetti** | Portes quantiques | Cloud + QCS | Payant | Algorithmes hybrides |

---

## 5. Pièges Courants

1. **Surapplication du quantique :**
   - *Erreur* : Vouloir utiliser le quantique pour des problèmes triviaux solubles en O(n log n).
   - *Correction* : Estimez d'abord le temps classique ; si < 1 minute, le quantique n'est pas justifié.

2. **Bruit quantique ignoré :**
   - *Erreur* : Exécuter QAOA sur du vrai matériel sans mitigation du bruit.
   - *Correction* : Utilisez des techniques de Zero-Noise Extrapolation (ZNE) ou des simulateurs.

3. **Mauvaise formulation QUBO :**
   - *Erreur* : Contrainte mal modélisée → solution violant des règles métier.
   - *Correction* : Validez la formulation QUBO sur un petit cas où la solution optimale est connue.

---

## Liste de vérification

- [ ] Le problème industriel est confirmé NP-difficile et à grande échelle (≥ 100 variables).
- [ ] Le problème est formulé en QUBO ou Ising (format accepté par les solveurs quantiques).
- [ ] Une solution classique (Branch & Bound, heuristique) est établie comme baseline.
- [ ] Le modèle QUBO est validé sur un petit cas avec solution optimale connue.
- [ ] L'algorithme (QAOA, recuit, VQE) est choisi selon la plateforme disponible.
- [ ] Le code est testé sur un simulateur avant déploiement sur matériel quantique réel.
