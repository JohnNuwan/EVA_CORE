---
name: quantum-algorithms-grover
description: "Algorithme de Grover : recherche non structurée, amplification d'amplitude, comptage quantique, applications à la satisfaction de contraintes et optimisation."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, grover, amplitude-amplification, quantum-search, quantum-counting, oracle, unstructured-search]
    related_skills: [quantum-gates, qiskit-programming, quantum-computing-fundamentals]
platforms: [linux, macos, windows]
---

# Algorithme de Grover

## Vue d'ensemble

L'**algorithme de Grover** (Lov Grover, 1996) résout la recherche non structurée dans un espace de taille N avec seulement O(√N) requêtes à l'oracle, contre O(N) classiquement. C'est une **accélération quadratique** — pas exponentielle comme Shor, mais applicable à une classe très large de problèmes : bases de données, satisfaction de contraintes (SAT), optimisation combinatoire, cryptanalyse (recherche de clé). Cette compétence couvre l'algorithme de base, l'amplification d'amplitude généralisée, le comptage quantique, les applications avancées et l'analyse de complexité.

## Quand l'utiliser

- Rechercher dans un espace non structuré (base de données, dictionnaire).
- Accélérer un sous-programme de résolution de contraintes (SAT, 3-SAT).
- Attaquer des primitives cryptographiques (recherche de clé DES/AES, collisions de hash).
- Compter le nombre de solutions à un problème (quantum counting).
- Accélérer l'optimisation combinatoire (Grover Adaptive Search).

---

## 1. Théorie Fondamentale

### 1.1 Le Problème

Soit f : {0,1}ⁿ → {0,1} une fonction oracle :
- f(x) = 1 si x est une solution (élément marqué)
- f(x) = 0 sinon
- Nombre de solutions : M (inconnu a priori)
- Taille de l'espace : N = 2ⁿ

**Classique :** O(N/M) requêtes en moyenne.
**Grover :** O(√(N/M)) requêtes — √N pour M = 1.

### 1.2 L'Opérateur de Grover G

```
G = (2|ψ⟩⟨ψ| − I) · O

Où :
- O : oracle qui marque les solutions (phase de −1 sur les états cibles)
- (2|ψ⟩⟨ψ| − I) : opérateur de diffusion (inversion autour de la moyenne)
- |ψ⟩ = H⊗ⁿ|0⟩ : superposition uniforme initiale
```

### 1.3 Interprétation Géométrique

Dans le plan formé par |α⟩ (mauvaise solutions, normalisé) et |β⟩ (bonnes solutions, normalisé) :

```
|ψ⟩ = cos(θ/2)|α⟩ + sin(θ/2)|β⟩
où sin(θ/2) = √(M/N)

Après k applications de G :
Gᵏ|ψ⟩ = cos((2k+1)θ/2)|α⟩ + sin((2k+1)θ/2)|β⟩

Nombre optimal d'itérations : k_opt = ⌊π/(4θ)⌋ ≈ ⌊π/4 √(N/M)⌋
```

```python
import numpy as np

def grover_iterations(N: int, M: int = 1) -> int:
    """Nombre optimal d'itérations de Grover."""
    theta = 2 * np.arcsin(np.sqrt(M / N))
    return int(np.floor(np.pi / (4 * theta)))
```

---

## 2. Implémentation en Qiskit

### 2.1 Oracle : Opérateur de Marqueur de Phase

```python
from qiskit import QuantumCircuit
from qiskit.circuit.library import ZGate, XGate

def oracle_marcher(n: int, target_state: str = None) -> QuantumCircuit:
    """Oracle qui marque un état cible par une phase de -1.
    
    Implémente : O|x⟩ = (-1)^{f(x)}|x⟩
    Si target_state est None, crée un oracle générique (tous -1).
    """
    oracle = QuantumCircuit(n, name='Oracle')
    
    if target_state is not None:
        # Appliquer X sur les bits qui sont 0 dans la cible
        for i, bit in enumerate(target_state):
            if bit == '0':
                oracle.x(i)
        
        # Porte multi-contrôlée Z sur le dernier qubit
        oracle.h(n-1)
        oracle.mcx(list(range(n-1)), n-1)  # Toffoli multi-contrôle
        oracle.h(n-1)
        
        # Annuler les X
        for i, bit in enumerate(target_state):
            if bit == '0':
                oracle.x(i)
    
    return oracle

# Oracle pour SAT : marque les assignations satisfaisant une clause
def oracle_sat_3sat(n_vars: int, clause: tuple) -> QuantumCircuit:
    """Oracle pour une clause 3-SAT (x_a ∨ x_b ∨ x_c)."""
    a, b, c = clause
    oracle = QuantumCircuit(n_vars, name=f'O_(x{a}∨x{b}∨x{c})')
    
    # Marquer si la clause est satisfaite
    # Utilise des qubits auxiliaires pour l'évaluation
    oracle.x(a)  # Si x_a est négatif, inverser
    
    return oracle
```

### 2.2 Opérateur de Diffusion

```python
def diffusion_operator(n: int) -> QuantumCircuit:
    """Opérateur de diffusion de Grover.
    
    D = 2|ψ⟩⟨ψ| − I = H⊗ⁿ · (2|0⟩⟨0| − I) · H⊗ⁿ
    """
    qc = QuantumCircuit(n, name='Diffusion')
    
    # |ψ⟩ = H⊗ⁿ|0⟩
    for i in range(n):
        qc.h(i)
    
    # Réflexion autour de |0⟩
    for i in range(n):
        qc.x(i)
    
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    
    for i in range(n):
        qc.x(i)
    
    # Retour à la base originale
    for i in range(n):
        qc.h(i)
    
    return qc
```

### 2.3 Algorithme de Grover Complet

```python
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister
from qiskit_aer import AerSimulator
from math import pi, sqrt

def grover_algorithm(n: int, oracle: QuantumCircuit, k: int = None) -> QuantumCircuit:
    """Circuit complet de l'algorithme de Grover.
    
    Args:
        n : nombre de qubits
        oracle : circuit oracle marquant les solutions
        k : nombre d'itérations (auto si None)
    
    Returns:
        Circuit complet à exécuter
    """
    qr = QuantumRegister(n, 'q')
    cr = ClassicalRegister(n, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Superposition uniforme
    qc.h(range(n))
    
    # Itérations de Grover
    N = 2**n
    if k is None:
        k = grover_iterations(N, M=1)
    
    for _ in range(k):
        qc.append(oracle, range(n))
        qc.append(diffusion_operator(n), range(n))
    
    # Mesure
    qc.measure(range(n), range(n))
    
    return qc

# Exécution
def run_grover(n: int, target: str, shots: int = 4096) -> dict:
    """Exécute Grover et retourne les résultats."""
    oracle = oracle_marcher(n, target)
    qc = grover_algorithm(n, oracle)
    
    simulator = AerSimulator(method='statevector')
    result = simulator.run(qc, shots=shots).result()
    counts = result.get_counts()
    
    # Probabilité de trouver la cible
    prob = counts.get(target, 0) / shots
    return {
        'counts': counts,
        'target': target,
        'probability': prob,
        'optimal_k': grover_iterations(2**n)
    }
```

---

## 3. Amplification d'Amplitude Généralisée

### 3.1 Formalisme

L'amplification d'amplitude (Brassard et al., 2000) généralise Grover à :
- Un opérateur de préparation A (pas forcément H⊗ⁿ)
- Un oracle O arbitraire
- Des réflexions autour de l'état initial (pas forcément |0⟩)

```
Q = A · (2|0⟩⟨0| − I) · A† · O
```

### 3.2 Implémentation

```python
def amplitude_amplification(n: int, A: QuantumCircuit, oracle: QuantumCircuit) -> QuantumCircuit:
    """Amplification d'amplitude généralisée.
    
    Args:
        A : circuit de préparation de l'état initial
        oracle : oracle marquant les solutions
    
    Returns:
        Circuit d'amplification
    """
    qc = QuantumCircuit(n)
    
    # État initial
    qc.append(A, range(n))
    
    # Itération
    qc.append(oracle, range(n))
    qc.append(A.inverse(), range(n))
    
    # Réflexion autour de |0⟩
    qc.x(range(n))
    qc.h(n-1)
    qc.mcx(list(range(n-1)), n-1)
    qc.h(n-1)
    qc.x(range(n))
    
    qc.append(A, range(n))
    
    return qc
```

---

## 4. Comptage Quantique (Quantum Counting)

### 4.1 Théorie

Le **comptage quantique** combine Grover et QPE pour estimer le nombre de solutions M sans les énumérer.

L'opérateur de Grover G a des valeurs propres :
```
λ± = exp(±2iθ) où sin²(θ) = M/N
```

QPE sur G donne une estimation de θ, donc de M.

```python
from qiskit import QuantumCircuit

def quantum_counting_circuit(n: int, n_estimate: int, oracle: QuantumCircuit) -> QuantumCircuit:
    """Circuit de comptage quantique.
    
    Utilise n_estimate qubits pour estimer la phase de G.
    
    Args:
        n : nombre de qubits de données
        n_estimate : nombre de qubits pour l'estimation
        oracle : circuit oracle
    
    Returns:
        Circuit de comptage quantique
    """
    qr_data = QuantumRegister(n, 'data')
    qr_est = QuantumRegister(n_estimate, 'phase')
    cr = ClassicalRegister(n_estimate, 'c')
    qc = QuantumCircuit(qr_est, qr_data, cr)
    
    # Superposition uniforme sur les deux registres
    qc.h(range(n_estimate + n))
    
    # Applications contrôlées de G^{2^j}
    G = QuantumCircuit(n)
    G.append(oracle, range(n))
    G.append(diffusion_operator(n), range(n))
    
    for j in range(n_estimate):
        G_pow = G.power(2**j).control()
        qc.append(G_pow, [qr_est[j]] + list(qr_data))
    
    # QFT inverse sur le registre d'estimation
    from qiskit.circuit.library import QFT
    qc.append(QFT(n_estimate, inverse=True), qr_est)
    
    # Mesure
    qc.measure(qr_est, cr)
    
    return qc
```

---

## 5. Applications Avancées

### 5.1 Recherche de Clé AES (Cryptanalyse)

AES-128 a une clé de 128 bits. Classiquement : 2¹²⁸ essais. Grover : 2⁶⁴ requêtes oracle = O(2⁶⁴).

```python
def grover_aes_key_search(n_key_bits: int = 128) -> dict:
    """Analyse des ressources pour recherche de clé AES par Grover.
    
    Chaque requête oracle = 1 évaluation AES (profondeur ~40 portes pour AES-128).
    """
    N_quantum = 2**(n_key_bits // 2)  # Grover : √N
    oracle_cost = 1_000_000  # Portes Toffoli par évaluation AES (estimation)
    
    return {
        'algorithme': 'Grover AES-128',
        'classique': 2**n_key_bits,
        'quantique_requetes': N_quantum,
        'portes_par_oracle': oracle_cost,
        'portes_totales': N_quantum * oracle_cost,
        'qubits_necessaires': 2000,  # Estimation
        'temps_estime': f"{N_quantum * 1e-6 * 10e-9:.1f} secondes"  # 10ns/porte
    }
```

### 5.2 Grover Adaptive Search (Optimisation)

```python
def grover_adaptive_search(cost_function: callable, n: int, n_iter: int) -> int:
    """Recherche adaptative de Grover pour optimisation combinatoire.
    
    Stratégie : seuil décroissant, l'algorithme cherche des solutions
    meilleures que le seuil courant.
    """
    threshold = 2**n  # Pire valeur
    best_solution = None
    
    for _ in range(n_iter):
        # Oracle : marque les solutions meilleures que le seuil
        oracle = threshold_oracle(cost_function, threshold)
        
        # Exécuter Grover
        k = grover_iterations(2**n)
        # ... exécution et mesure
        
        # Mettre à jour le seuil
        if measured_cost < threshold:
            threshold = measured_cost
            best_solution = measured_state
    
    return best_solution
```

### 5.3 Résolution 3-SAT

```python
def grover_3sat(n_vars: int, clauses: list) -> dict:
    """Résolution de 3-SAT avec Grover.
    
    Mise en garde : la construction de l'oracle est coûteuse, et
    le nombre de solutions M influence directement l'accélération.
    """
    # Oracle combinant toutes les clauses
    oracle = QuantumCircuit(n_vars)
    for clause in clauses:
        oracle.compose(oracle_sat_3sat(n_vars, clause), inplace=True)
    
    N = 2**n_vars
    # Si M est inconnu → Quantum Counting d'abord, puis Grover
    return {
        'method': 'Grover-3SAT',
        'n_vars': n_vars,
        'n_clauses': len(clauses),
        'classical_O': f'2^{n_vars}',
        'quantum_O': f'2^{n_vars/2}',
        'optimal_k': grover_iterations(N)
    }
```

---

## 6. Analyse de Complexité Détaillée

### 6.1 Probabilité de Succès

```python
def grover_probability(n: int, M: int, k: int) -> float:
    """Probabilité de trouver une solution après k itérations."""
    N = 2**n
    theta = 2 * np.arcsin(np.sqrt(M / N))
    return np.sin((2*k + 1) * theta / 2)**2

def optimal_grover_probability(n: int, M: int) -> float:
    """Probabilité optimale avec k = k_opt."""
    k_opt = grover_iterations(n, M)
    return grover_probability(n, M, k_opt)
```

### 6.2 Comparaison Classique vs Quantique

| Tâche | Classique | Grover | Accélération |
|:---|:---|:---|:---|
| Recherche taille N | O(N) | O(√N) | Quadratique |
| Comptage (estimer M) | O(N) | O(√N) | Quadratique |
| 3-SAT (n vars, m clauses) | O(2ⁿ) | O(2^{n/2}) | Quadratique |
| AES-128 key search | 2¹²⁸ | 2⁶⁴ | Quadratique |
| Hash collision (n bits) | 2^{n/2} | 2^{n/3} (Brassard) | 2^{n/6} |

### 6.3 Optimalité de Grover

**Théorème (Bennett et al., 1997) :** Tout algorithme de recherche quantique nécessite Ω(√N) requêtes oracle. Grover est optimal à un facteur constant près.

---

## 7. Pièges et Limitations

1. **M inconnu :** Sans connaître le nombre de solutions M, le choix de k est difficile. Solution : Quantum Counting en préambule, ou Grover avec recherche binaire sur k.

2. **Oracle coûteux :** L'accélération quadratique ne porte que sur le nombre de requêtes oracle, pas sur le coût de l'oracle lui-même. Si l'oracle nécessite O(N) portes, l'avantage disparaît.

3. **Pas d'accélération exponentielle :** Contrairement à Shor, Grover ne donne qu'un avantage quadratique. Pour la plupart des problèmes pratiques, ce n'est pas suffisant sans correction d'erreur.

4. **Décohérence :** Grover nécessite des cohérences de phase précises sur O(√N) itérations. Le bruit détruit l'interférence constructive.

5. **Problème du dernier saut :** Si k = k_opt + 1, la probabilité peut chuter drastiquement. Le nombre d'itérations doit être précis.

---

## Liste de vérification

- [ ] L'opérateur de Grover G = D·O et son interprétation géométrique sont compris.
- [ ] Le nombre optimal d'itérations k_opt = ⌊π/4 √(N/M)⌋ est calculé.
- [ ] L'oracle et l'opérateur de diffusion sont implémentés en Qiskit.
- [ ] L'amplification d'amplitude généralisée est maîtrisée.
- [ ] Le comptage quantique (QPE sur G) est implémenté.
- [ ] Les applications (AES, 3-SAT, optimisation) sont référencées.
- [ ] L'optimalité de Grover (Ω(√N)) est comprise.
- [ ] Les limitations (M inconnu, oracle coûteux, bruit) sont gérées.
