---
name: quantum-annealing-qaoa
description: "Recuit quantique et QAOA : théorème adiabatique, D-Wave, QUBO, Ising, VQE, optimisation combinatoire hybride classique-quantique, applications industrielles et comparaison des approches."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, annealing, qaoa, dwave, qubo, ising, vqe, adiabatic, hybrid, combinatorial-optimization]
    related_skills: [quantum-computing-fundamentals, qiskit-programming, quantum-gates]
platforms: [linux, macos, windows]
---

# Recuit Quantique et QAOA

## Vue d'ensemble

Le **recuit quantique** (Quantum Annealing) et le **QAOA** (Quantum Approximate Optimization Algorithm) sont deux approches complémentaires pour résoudre des problèmes d'optimisation combinatoire sur du matériel quantique. Le recuit quantique utilise l'évolution adiabatique continue sur des processeurs spécialisés (D-Wave), tandis que QAOA est un algorithme variationnel hybride pour machines à portes (IBM, Google). Cette compétence couvre le théorème adiabatique, la formulation QUBO/Ising, l'implémentation QAOA avec Qiskit, VQE (Variational Quantum Eigensolver), la programmation D-Wave (Ocean SDK), les applications industrielles et la comparaison des approches.

## Quand l'utiliser

- Résoudre un problème d'optimisation combinatoire (QUBO, Ising, Max-Cut, TSP) sur quantique.
- Choisir entre recuit quantique (D-Wave) et QAOA (IBM/Google) pour un problème donné.
- Formuler un problème industriel en QUBO pour solveur quantique.
- Implémenter QAOA avec optimisation classique (VQE).
- Explorer les architectures hybrides (classique + quantique) pour l'optimisation.

---

## 1. Théorème Adiabatique

### 1.1 Principe

Le **théorème adiabatique** (Born-Fock, 1928) : si un système quantique est dans un état propre instantané de son Hamiltonien, et que ce Hamiltonien évolue suffisamment lentement, le système reste dans l'état propre instantané correspondant.

Pour l'optimisation :
1. Préparer l'état fondamental d'un Hamiltonien simple H₀
2. Évoluer adiabatiquement vers H₁ (le Hamiltonien du problème)
3. Mesurer → état fondamental de H₁ = solution optimale

```
H(s) = (1-s)H₀ + sH₁,    s = t/T (temps adimensionné)
```

### 1.2 Gap Énergétique

La vitesse d'évolution est limitée par le gap minimum Δ_min entre l'état fondamental et le premier état excité :

```
T ≫ 1 / Δ_min²  (ou T ≫ 1/Δ_min avec préparation avancée)
```

```python
import numpy as np

def adiabatic_time(Delta_min: float, eps: float = 1e-6) -> float:
    """Temps adiabatique minimal selon le théorème.
    
    T ≫ ||dH/ds||² / (ε · Δ_min³) 
    Approximation standard : T > 1/(ε · Δ_min²)
    
    Args:
        Delta_min : gap énergétique minimum
        eps : erreur de chevauchement tolérée
    """
    return 1.0 / (eps * Delta_min**2)

def estimate_gap_maxcut(n_nodes: int) -> float:
    """Estimation du gap pour un problème Max-Cut aléatoire.
    
    Le gap diminue exponentiellement avec la taille du problème.
    """
    return np.exp(-0.5 * n_nodes)  # Approximation empirique
```

---

## 2. Formulation QUBO et Ising

### 2.1 Format QUBO

Un problème **QUBO** (Quadratic Unconstrained Binary Optimization) s'écrit :

```
min xᵀ Q x,   x ∈ {0,1}ⁿ
```

où Q ∈ ℝⁿˣⁿ est une matrice triangulaire supérieure.

### 2.2 Format Ising

Le modèle **Ising** correspondant :

```
H = Σᵢ hᵢ σ_zⁱ + Σᵢⱼ Jᵢⱼ σ_zⁱ σ_zⱼ
```

où σ_zⁱ ∈ {+1, -1} (spins).

Conversion QUBO ↔ Ising : x = (1 - σ_z)/2.

### 2.3 Problèmes Industriels en QUBO

```python
import numpy as np

class QUBOProblem:
    """Formulation QUBO d'un problème d'optimisation."""
    
    def __init__(self, n_vars: int):
        self.n = n_vars
        self.Q = np.zeros((n_vars, n_vars))
    
    def add_linear_term(self, i: int, coeff: float):
        """Ajoute un terme linéaire."""
        self.Q[i, i] += coeff
    
    def add_quadratic_term(self, i: int, j: int, coeff: float):
        """Ajoute un terme quadratique (i ≤ j)."""
        if i <= j:
            self.Q[i, j] += coeff
        else:
            self.Q[j, i] += coeff
    
    def add_penalty(self, constraint_func: callable, penalty: float = 10.0):
        """Ajoute une contrainte comme pénalité quadratique."""
        pass
    
    def to_ising(self) -> tuple:
        """Convertit QUBO en hamiltonien Ising (h, J)."""
        h = np.zeros(self.n)
        J = np.zeros((self.n, self.n))
        
        for i in range(self.n):
            h[i] = -0.5 * self.Q[i, i] - 0.25 * sum(self.Q[i, j] for j in range(self.n))
            for j in range(self.n):
                if i != j:
                    J[i, j] = 0.25 * (self.Q[i, j] + self.Q[j, i])
                elif i == j:
                    h[i] += -0.5 * sum(self.Q[i, k] for k in range(self.n))
                    h[i] += -0.5 * sum(self.Q[k, i] for k in range(self.n))
        
        # Correction : simplification
        # h_i = -0.5 * Q[i,i] - 0.25 * sum_j Q[i,j] 
        # J_ij = 0.25 * Q[i,j] (pour i ≠ j)
        offset = 0.25 * np.sum(self.Q) + 0.5 * np.sum(np.diag(self.Q))
        
        return h, J, offset
    
    def evaluate(self, x: np.ndarray) -> float:
        """Évalue la fonction objectif pour une solution binaire x."""
        return x @ self.Q @ x


def max_cut_qubo(weights: np.ndarray) -> QUBOProblem:
    """Problème Max-Cut : partitionner un graphe en maximisant les arêtes coupées.
    
    Objectif QUBO : max Σ w_ij (1 - x_i x_j) / 2
    Equivalent à min -Σ w_ij x_i x_j + const
    """
    n = weights.shape[0]
    problem = QUBOProblem(n)
    
    for i in range(n):
        for j in range(i+1, n):
            if weights[i, j] != 0:
                problem.add_quadratic_term(i, j, -weights[i, j])
                problem.add_linear_term(i, -weights[i, j])
                problem.add_linear_term(j, -weights[i, j])
    
    return problem


def tsp_qubo(n_cities: int, distances: np.ndarray) -> QUBOProblem:
    """Problème du voyageur de commerce en QUBO.
    
    Variables : x_{t,i} = 1 si la ville i est visitée à l'étape t
    Contraintes : une ville par étape, toutes les villes une fois.
    """
    n = n_cities * n_cities  # n² variables binaires
    problem = QUBOProblem(n)
    P = max(distances.max() * 2, 10)  # Pénalité
    
    def idx(t: int, i: int) -> int:
        return t * n_cities + i
    
    # Objectif : minimiser la distance totale
    for t in range(n_cities - 1):
        for i in range(n_cities):
            for j in range(n_cities):
                if i != j:
                    problem.add_quadratic_term(
                        idx(t, i), idx(t+1, j), distances[i, j]
                    )
    # Retour au départ
    for i in range(n_cities):
        for j in range(n_cities):
            if i != j:
                problem.add_quadratic_term(
                    idx(n_cities-1, i), idx(0, j), distances[i, j]
                )
    
    # Contrainte : exactement une ville par étape
    for t in range(n_cities):
        for i in range(n_cities):
            problem.add_linear_term(idx(t, i), -2*P)
            for j in range(i+1, n_cities):
                problem.add_quadratic_term(idx(t, i), idx(t, j), 2*P)
    
    # Contrainte : chaque ville visitée exactement une fois
    for i in range(n_cities):
        for t in range(n_cities):
            problem.add_linear_term(idx(t, i), -2*P)
            for s in range(t+1, n_cities):
                problem.add_quadratic_term(idx(s, i), idx(t, i), 2*P)
    
    return problem
```

---

## 3. QAOA (Quantum Approximate Optimization Algorithm)

### 3.1 Principe

QAOA approxime l'évolution adiabatique par une séquence discrète de couches :

```
|ψ(β,γ)⟩ = e^{-iβ_p H_B} e^{-iγ_p H_P} ... e^{-iβ₁ H_B} e^{-iγ₁ H_P} |+⟩⊗ⁿ

où :
H_P = Hamiltonien du problème (Ising)
H_B = Hamiltonien du mélangeur (drive transverse)
(β,γ) = paramètres variationnels optimisés classiquement
```

### 3.2 Implémentation Qiskit

```python
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
import numpy as np

def qaoa_circuit(n_qubits: int, p_layers: int, 
                 h: np.ndarray, J: np.ndarray) -> QuantumCircuit:
    """Circuit QAOA pour un problème Ising.
    
    Args:
        n_qubits : nombre de qubits (variables)
        p_layers : nombre de couches QAOA
        h : champ magnétique local (n_qubits,)
        J : couplages (n_qubits, n_qubits)
    
    Returns:
        Circuit QAOA paramétré
    """
    qc = QuantumCircuit(n_qubits)
    
    # Superposition uniforme initiale
    qc.h(range(n_qubits))
    
    # Paramètres variationnels
    betas = [Parameter(f'β_{i}') for i in range(p_layers)]
    gammas = [Parameter(f'γ_{i}') for i in range(p_layers)]
    
    for layer in range(p_layers):
        # Couche problème : exp(-i γ H_P)
        for i in range(n_qubits):
            if h[i] != 0:
                qc.rz(-2 * gammas[layer] * h[i], i)
        for i in range(n_qubits):
            for j in range(i+1, n_qubits):
                if J[i, j] != 0:
                    qc.cx(i, j)
                    qc.rz(-2 * gammas[layer] * J[i, j], j)
                    qc.cx(i, j)
        
        # Couche mélangeur : exp(-i β H_B) où H_B = Σ X_i
        for i in range(n_qubits):
            qc.rx(2 * betas[layer], i)
    
    return qc


def qaoa_maxcut(weights: np.ndarray, p_layers: int = 1) -> QuantumCircuit:
    """QAOA pour Max-Cut."""
    n = weights.shape[0]
    
    # Hamiltonien Max-Cut : H_P = -0.5 Σ w_ij (I - Z_i Z_j)
    h = np.zeros(n)
    J = np.zeros((n, n))
    for i in range(n):
        for j in range(i+1, n):
            J[i, j] = -0.5 * weights[i, j]  # Le signe est absorbé dans l'objectif
    
    return qaoa_circuit(n, p_layers, h, J)


def qaoa_cost_expectation(qc: QuantumCircuit, params: np.ndarray,
                          h: np.ndarray, J: np.ndarray, 
                          backend=None) -> float:
    """Calcule la valeur d'espérance du coût pour des paramètres QAOA donnés.
    
    Utilise Qiskit Estimator ou simulateur local.
    """
    from qiskit.primitives import Estimator
    
    bound_qc = qc.assign_parameters(params)
    
    # Observable : H_P = Σ h_i Z_i + Σ J_ij Z_i Z_j
    from qiskit.quantum_info import SparsePauliOp
    pauli_terms = []
    for i in range(len(h)):
        if h[i] != 0:
            z_str = ['I'] * len(h)
            z_str[i] = 'Z'
            pauli_terms.append((''.join(z_str), h[i]))
    for i in range(len(h)):
        for j in range(i+1, len(h)):
            if J[i, j] != 0:
                z_str = ['I'] * len(h)
                z_str[i] = 'Z'
                z_str[j] = 'Z'
                pauli_terms.append((''.join(z_str), J[i, j]))
    
    H_obs = SparsePauliOp.from_list(pauli_terms)
    
    estimator = Estimator()
    result = estimator.run(bound_qc, H_obs).result()
    return result.values[0]
```

### 3.3 Optimisation Classique des Paramètres

```python
from scipy.optimize import minimize

def qaoa_optimize(qc: QuantumCircuit, n_params: int,
                  h: np.ndarray, J: np.ndarray,
                  backend=None, n_shots: int = 1000) -> dict:
    """Optimise les paramètres QAOA par boucle classique.
    
    Returns:
        Meilleurs paramètres et valeur d'énergie.
    """
    # Initialisation : approx. du recuit simulé
    p = n_params // 2
    beta_init = np.linspace(0.1, 0.5, p)  # Diminution lente
    gamma_init = np.linspace(0.1, 2.0, p)  # Augmentation
    
    def objective(params):
        return qaoa_cost_expectation(qc, params, h, J, backend)
    
    result = minimize(
        objective,
        np.concatenate([gamma_init, beta_init]),
        method='COBYLA',
        options={'maxiter': 500, 'rhobeg': 0.1, 'tol': 1e-3}
    )
    
    return {
        'optimal_energy': result.fun,
        'optimal_params': result.x,
        'n_evaluations': result.nfev,
        'success': result.success
    }
```

---

## 4. VQE (Variational Quantum Eigensolver)

### 4.1 Principe

VQE est le cas limite de QAOA pour p → ∞, mais VQE peut utiliser n'importe quel ansatz (pas seulement l'adiabatique).

```python
from qiskit.circuit.library import EfficientSU2, RealAmplitudes
from qiskit.quantum_info import SparsePauliOp

def vqe_molecule(H: SparsePauliOp, n_qubits: int, reps: int = 3) -> dict:
    """VQE pour estimer l'état fondamental d'un Hamiltonien moléculaire.
    
    Architecture :
    1. Ansatz : EfficientSU2 (circuit variationnel)
    2. Estimation : Estimator Primitive
    3. Optimisation : SPSA ou COBYLA
    """
    ansatz = EfficientSU2(n_qubits, reps=reps, entanglement='linear')
    n_params = ansatz.num_parameters
    
    np.random.seed(42)
    params = np.random.rand(n_params) * 0.1  # Initialisation proche de 0
    
    # Boucle VQE
    from qiskit.primitives import Estimator
    estimator = Estimator()
    
    def cost(params):
        bound_qc = ansatz.assign_parameters(params)
        result = estimator.run(bound_qc, H).result()
        return result.values[0]
    
    result = minimize(cost, params, method='SPSA', 
                      options={'maxiter': 1000, 'learning_rate': 0.1})
    
    return {
        'energy': result.fun,
        'params': result.x,
        'n_evals': result.nfev
    }
```

### 4.2 Ansätze courants

| Ansatz | Paramètres | Profondeur | Expressivité |
|:---|:---|:---|:---|
| **RealAmplitudes** | R_y + CX | O(n · reps) | Faible | Simple, peu de paramètres |
| **EfficientSU2** | R_y, R_z + CX | O(n · reps) | Moyenne | Standard pour VQE |
| **TwoLocal** | Rotations + intriquation | O(n · reps) | Haute | Général |
| **Hardware-efficace** | Portes natives du backend | Variable | Optimale | Adapté au matériel |

---

## 5. Programmation D-Wave (Ocean SDK)

### 5.1 Installation et Connexion

```python
# pip install dwave-ocean-sdk
# Configuration : dwave config create
from dwave.system import DWaveSampler, EmbeddingComposite, LeapHybridSampler
from dwave.cloud import Client
import dimod

# Connexion avec token API (gratuit : 1 min/mois sur Leap)
client = Client.from_config()
sampler = DWaveSampler(solver='Advantage_system6.3')
print(f"Qubits disponibles : {sampler.properties['num_qubits']}")
print(f"Topologie : {sampler.properties['topology']}")
```

### 5.2 Recuit sur D-Wave

```python
def dwave_optimize(Q: np.ndarray, num_reads: int = 1000) -> dict:
    """Optimisation QUBO sur D-Wave.
    
    Args:
        Q : matrice QUBO (n×n)
        num_reads : nombre d'échantillons
    
    Returns:
        Meilleure solution et énergie.
    """
    # Conversion en BQM (Binary Quadratic Model)
    bqm = dimod.BQM('BINARY')
    n = Q.shape[0]
    
    for i in range(n):
        for j in range(i, n):
            if Q[i, j] != 0:
                if i == j:
                    bqm.add_variable(i, Q[i, i])
                else:
                    bqm.add_interaction(i, j, Q[i, j] + Q[j, i])
    
    # Embedding automatique (placement sur la topologie Advantage)
    sampler = EmbeddingComposite(DWaveSampler())
    
    # Échantillonnage
    sampleset = sampler.sample(
        bqm, 
        num_reads=num_reads,
        label="QUBO Optimisation EVA",
        annealing_time=20,  # µs
        num_spin_reversal_transforms=10  # Mitigation de bruit
    )
    
    # Meilleur résultat
    best = sampleset.first
    solution = [best.sample[i] for i in range(n)]
    
    return {
        'solution': solution,
        'energy': best.energy,
        'num_occurrences': best.num_occurrences,
        'all_samples': sampleset,
        'energies': sampleset.record.energy
    }
```

### 5.3 Solveur Hybride (Leap)

```python
# Solveur hybride pour problèmes > qubits disponibles
hybrid_sampler = LeapHybridSampler()

result = hybrid_sampler.sample(
    bqm,
    time_limit=10,  # secondes
    label="Hybride EVA"
)

best = result.first
print(f"Énergie : {best.energy}")
```

---

## 6. Comparaison : Recuit Quantique vs QAOA

| Critère | Recuit Quantique (D-Wave) | QAOA (IBM/Google) |
|:---|:---|:---|
| **Matériel** | Processeur spécialisé (Advantage) | Machine à portes universelles |
| **Principe** | Évolution adiabatique continue | Discret, variationnel |
| **Paramètres** | Temps de recuit | Profondeur p, angles β,γ |
| **Qualité solution** | Empirique, pas de garantie | Garantie dans limite p→∞ |
| **Taille problème** | Jusqu'à ~5000 qubits (QUBO) | Quelques centaines de qubits |
| **Précision** | Moyenne (bruit analogique) | Potentiellement haute |
| **Flexibilité** | QUBO/Ising uniquement | Tout Hamiltonien local |
| **Maturité** | Commercial (180+ systèmes) | Expérimentale (NISQ) |
| **Accès** | Cloud Leap (gratuit limité) | IBM Quantum (simulateur) |
| **Meilleur pour** | Optimisation combinatoire dense | Chimie, problèmes structurés |

### 6.1 Choix de l'approche

```python
def recommend_approach(problem_type: str, n_vars: int, 
                       required_precision: str) -> str:
    """Recommande le meilleur outil quantique pour un problème."""
    
    if n_vars > 1000 or problem_type in ('QUBO', 'TSP', 'Max-Cut', 'Scheduling'):
        if required_precision == 'approximate':
            return 'D-Wave (recuit quantique)'
        else:
            return 'Hybride Leap (D-Wave)'
    elif n_vars <= 100:
        return 'QAOA (IBM Qiskit)'
    elif problem_type == 'molecular':
        return 'VQE (Qiskit/PennyLane)'
    else:
        return 'Benchmark d\'abord : comparer QAOA, recuit, et solveur classique'
```

---

## 7. Applications Industrielles

| Domaine | Problème | Formulation | Solveur |
|:---|:---|:---|:---|
| **Logistique** | Vehicle Routing Problem (VRP) | QUBO | D-Wave / QAOA |
| **Finance** | Portfolio Optimization | Ising | QAOA / VQE |
| **Énergie** | Unit Commitment | QUBO | D-Wave |
| **Télécom** | Channel Assignment | QUBO | D-Wave |
| **Pharma** | Drug Discovery (VQE) | Hamiltonien | VQE / QAOA |
| **Aéro** | Flight Gate Assignment | QUBO | D-Wave |
| **Manuf.** | Job Shop Scheduling | QUBO | D-Wave / QAOA |

---

## 8. Pièges et Limitations

1. **Gap exponentiel :** Le gap énergétique Δ_min → 0 exponentiellement avec la taille pour la plupart des problèmes NP-difficiles. Le recuit quantique peut donc être exponentiellement lent.

2. **Speedup contestable :** D-Wave montre rarement une accélération par rapport aux solveurs classiques optimisés (Gurobi, CPLEX) pour les mêmes problèmes QUBO.

3. **Précision analogique :** Les processeurs D-Wave ont une précision limitée (~5 bits effectifs). Les couplages J_ij < 1/50 du max sont ignorés.

4. **Pénalités mal équilibrées :** Dans QUBO, si la pénalité pour violation de contrainte est trop faible, la solution viole les contraintes. Trop forte, elle domine l'objectif.

5. **Embedding overhead :** Une variable QUBO peut nécessiter 5-10 qubits physiques sur la topologie chimère (Advantage). Un problème de 100 variables peut prendre 500+ qubits.

6. **QAOA p limité :** Pour p=1, QAOA est parfois pire qu'une relaxation semi-définie (SDP). Pour p > 10, les garanties s'améliorent mais l'optimisation classique devient difficile.

---

## Liste de vérification

- [ ] Le théorème adiabatique et la condition de vitesse lente sont compris.
- [ ] La formulation QUBO et la conversion Ising sont maîtrisées.
- [ ] Les problèmes Max-Cut, TSP et Job Shop sont formulables en QUBO.
- [ ] QAOA est implémenté en Qiskit avec optimisation COBYLA.
- [ ] L'API D-Wave (Ocean SDK, DWaveSampler, EmbeddingComposite) est connue.
- [ ] Les métriques de qualité (énergie, gap, embedding) sont analysées.
- [ ] La comparaison recuit vs QAOA est documentée.
- [ ] Les limites (gap exponentiel, précision, embedding overhead) sont comprises.
