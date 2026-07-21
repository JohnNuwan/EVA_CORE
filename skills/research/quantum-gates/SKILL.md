---
name: quantum-gates
description: "Portes quantiques : catalogue complet des portes à 1 et 2 qubits, jeux de portes universels, Clifford+T, décomposition, transpilation et synthèse de circuits."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, gates, pauli, clifford, toffoli, transpilation, circuit-synthesis, universal-gate-set]
    related_skills: [quantum-computing-fundamentals, qiskit-programming, quantum-error-correction]
platforms: [linux, macos, windows]
---

# Portes Quantiques

## Vue d'ensemble

Les **portes quantiques** sont les opérateurs unitaires qui transforment l'état d'un système quantique. Cette compétence couvre le catalogue complet : portes à 1 qubit (Pauli, Hadamard, phase, rotation), portes à 2 qubits (CNOT, CZ, SWAP), portes à 3 qubits (Toffoli, Fredkin), jeux de portes universels, le groupe de Clifford, les portes non-Clifford (T, Toffoli), la décomposition et la transpilation de circuits, et les métriques de qualité.

## Quand l'utiliser

- Concevoir un circuit quantique pour un algorithme donné.
- Décomposer une porte multi-qubits en portes élémentaires.
- Transpiler un circuit pour une architecture cible (topologie, jeu de portes).
- Analyser la profondeur, le nombre de portes et la fidélité d'un circuit.
- Implémenter des opérations Clifford ou non-Clifford pour la correction d'erreur.

---

## 1. Portes à 1 Qubit

### 1.1 Portes de Pauli

```
I = [[1,0],[0,1]]      Identité
X = [[0,1],[1,0]]      Pauli-X (NON quantique) : |0⟩↔|1⟩
Y = [[0,-i],[i,0]]     Pauli-Y : |0⟩→i|1⟩, |1⟩→-i|0⟩
Z = [[1,0],[0,-1]]     Pauli-Z : |0⟩→|0⟩, |1⟩→-|1⟩ (changement de phase π)
```

```python
import numpy as np
I = np.eye(2, dtype=complex)
X = np.array([[0,1],[1,0]], dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)
PAULIS = {'I': I, 'X': X, 'Y': Y, 'Z': Z}
```

**Propriétés :** σ² = I, dét(σ) = -1, auto-adjointes (σ† = σ).

### 1.2 Porte de Hadamard

```
H = 1/√2 [[1,1],[1,-1]]
H : |0⟩ → |+⟩ = (|0⟩ + |1⟩)/√2,   |1⟩ → |−⟩ = (|0⟩ − |1⟩)/√2
```

Propriétés : H² = I, H X H = Z, H Z H = X.

### 1.3 Portes de Phase

```
S = [[1,0],[0,i]]           Porte S (π/2)      : S² = Z
T = [[1,0],[0,e^{iπ/4}]]   Porte T (π/4)      : T² = S, T⁴ = Z
S† = [[1,0],[0,-i]]         Porte S†
T† = [[1,0],[0,e^{-iπ/4}]] Porte T†
```

### 1.4 Portes de Rotation

```
R_x(θ) = exp(-iθX/2) = [[cos(θ/2), -i sin(θ/2)], [-i sin(θ/2), cos(θ/2)]]
R_y(θ) = exp(-iθY/2) = [[cos(θ/2), -sin(θ/2)], [sin(θ/2), cos(θ/2)]]
R_z(θ) = exp(-iθZ/2) = [[e^{-iθ/2}, 0], [0, e^{iθ/2}]]
```

```python
def Rx(theta: float) -> np.ndarray:
    return np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                     [-1j*np.sin(theta/2), np.cos(theta/2)]])

def Ry(theta: float) -> np.ndarray:
    return np.array([[np.cos(theta/2), -np.sin(theta/2)],
                     [np.sin(theta/2), np.cos(theta/2)]])

def Rz(theta: float) -> np.ndarray:
    return np.array([[np.exp(-1j*theta/2), 0],
                     [0, np.exp(1j*theta/2)]])
```

Phase globale vs relative : R_z(θ) = e^{-iθ/2} [[1,0],[0,e^{iθ}]] — la phase e^{-iθ/2} est globale (indétectable), e^{iθ} est relative (observable via interférence).

---

## 2. Portes à 2 Qubits

### 2.1 CNOT (CX)

```
CNOT = [[1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]]
|control, target⟩ → |control, target ⊕ control⟩
```

Propriétés : CNOT² = I, génère l'intrication à partir d'états séparables.

### 2.2 CZ (Controlled-Z)

```
CZ = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,-1]]
```

Relation : CZ = (I ⊗ H) ⋅ CNOT ⋅ (I ⊗ H).

### 2.3 SWAP

```
SWAP = [[1,0,0,0],[0,0,1,0],[0,1,0,0],[0,0,0,1]]
|a,b⟩ → |b,a⟩
```

Décomposition : SWAP = 3 CNOTs = CNOT(1,2) ⋅ CNOT(2,1) ⋅ CNOT(1,2).

### 2.4 Portes contrôlées générales

```python
def controlled(U: np.ndarray, n_controls: int = 1) -> np.ndarray:
    """Construit une version contrôlée de U (2×2) avec n qubits de contrôle."""
    d = 2**n_controls
    full_size = d * 2
    result = np.eye(full_size, dtype=complex)
    result[d:, d:] = U
    return result
```

---

## 3. Portes à 3+ Qubits

### 3.1 Toffoli (CCNOT, C²NOT)

```
Toffoli |a,b,c⟩ → |a,b,c ⊕ (a ∧ b)⟩
```

Matrice 8×8 qui permute [110]↔[111].

**Décomposition en portes élémentaires :** Toffoli = 6 CNOTs + 10 portes 1-qubit (dont T/T†).

```python
def toffoli_decomposition():
    """Décomposition standard de Toffoli avec portes élémentaires.
    
    Circuit :
    q0 ──■────■────────────■──
    q1 ──■────■────────────■──
    q2 ──T────┼────T†──────XdX (X = H·T†·H·T·H)
         └────┼────────────────
              └────────────────
    """
    pass
```

### 3.2 Fredkin (CSWAP)

```
Fredkin |a,b,c⟩ → |a, b ⊕ a(c⊕b), c ⊕ a(c⊕b)⟩ (SWAP conditionnel)
```

### 3.3 Portes multi-contrôlées (MCT)

Un CⁿNOT (n qubits de contrôle) peut être décomposé en O(n) Toffolis en utilisant des qubits auxiliaires (dirty ancillae).

**Théorème de Barenco et al. (1995) :** Tout CⁿNOT sans auxiliaire nécessite O(n²) portes élémentaires. Avec n-2 auxiliaires sales, O(n).

```python
def mcx_decomposition(n_controls: int, clean_ancilla: int = 0) -> int:
    """Retourne le nombre de Toffolis nécessaires pour un CⁿNOT.
    
    Avec auxiliaires propres : 2(n-2) + 1 Toffolis.
    Avec auxiliaires sales : 4(n-2) + 1 Toffolis.
    Sans auxiliaire : O(n²) portes 1 et 2 qubits.
    """
    if clean_ancilla >= n_controls - 2:
        return 2 * (n_controls - 2) + 1
    return 4 * (n_controls - 2) + 1
```

---

## 4. Jeux de Portes Universels

Un jeu de portes est **universel** si toute opération unitaire peut être approchée à ε près par une séquence finie de ces portes.

### 4.1 Jeu Clifford + T

Le groupe de Clifford est le normalisateur du groupe de Pauli : {U | U P U† ⊂ Pₙ}.

Portes Clifford : H, S, CNOT (et leurs combinaisons).
Porte non-Clifford : T (nécessaire pour l'universalité).

**Théorème de Gottesman-Knill :** Un circuit composé uniquement de portes Clifford peut être simulé classiquement en temps polynomial. La porte T brise cette barrière.

### 4.2 Jeux universels courants

| Jeu | Portes | Notes |
|:---|:---|:---|
| **Clifford+T** | H, S, CNOT, T | Standard pour correction d'erreur |
| **Rotation + CNOT** | R_x, R_y, R_z, CNOT | Flexible, utilisé en NISQ |
| **Universel IBM** | CX, R_z, √X, X | Basé sur la physique transmon |
| **Universel natif** | XX(θ), ZZ(θ), rot. locale | Dépend de l'architecture |

### 4.3 Mesures de qualité

- **Profondeur du circuit** : nombre de couches parallèles (temps d'exécution)
- **Nombre de portes 2-qubits** : métrique dominante (elles sont ~10× plus bruyantes que les portes 1-qubit)
- **Fidélité du circuit** : F_circuit = Πₚ F_gate,p × Π_c F_meas,c × F_init
- **Nombre de portes T** : métrique pour correction d'erreur (T-gate ≈ 100-1000× plus chère que Clifford)

```python
def circuit_metrics(gates: list) -> dict:
    """Calcule les métriques d'un circuit."""
    n_1q = sum(1 for g in gates if g['qubits'] == 1)
    n_2q = sum(1 for g in gates if g['qubits'] == 2) 
    n_t = sum(1 for g in gates if g['name'] in ('T', 'T†'))
    return {
        '1q_gates': n_1q,
        '2q_gates': n_2q,
        't_gates': n_t,
        't_depth': n_t,  # Sauf parallélisation
        'gate_count': len(gates)
    }
```

---

## 5. Décomposition de Portes

### 5.1 Décomposition ZYZ de toute porte 1-qubit

Toute porte 1-qubit U ∈ SU(2) peut s'écrire :

```
U = e^{iα} R_z(β) R_y(γ) R_z(δ)
```

```python
def zyz_decomposition(U: np.ndarray) -> tuple:
    """Décompose U ∈ U(2) en e^{iα} R_z(β) R_y(γ) R_z(δ)."""
    # S'assurer que U ∈ SU(2) (dét = 1)
    phase = np.angle(np.linalg.det(U)) / 2
    U_su2 = np.exp(-1j * phase) * U
    
    a, b, c, d = U_su2[0,0], U_su2[0,1], U_su2[1,0], U_su2[1,1]
    gamma = 2 * np.arctan2(np.abs(c), np.abs(a))
    beta_delta = np.angle(np.array([a, -c.conj()]))
    beta_minus_delta = np.angle(np.array([b, d]))
    beta = beta_delta[0] + beta_minus_delta[0]
    delta = beta_delta[0] - beta_minus_delta[0]
    
    return phase, beta, gamma, delta
```

### 5.2 Décomposition de Cartan pour portes 2-qubits

Toute porte 2-qubits peut être décomposée comme :

```
U = (A₁ ⊗ A₂) ⋅ exp(i(αₓσₓσₓ + αᵧσᵧσᵧ + α_zσ_zσ_z)) ⋅ (B₁ ⊗ B₂)
```

```python
def cartan_decomposition(U_2q: np.ndarray) -> dict:
    """Décomposition de Cartan-Khaneja-Glaser d'une porte 2-qubits.
    
    U = (A1⊗A2) · K(αx,αy,αz) · (B1⊗B2)Où K est le bloc de Cartan : exp(i(αx XX + αy YY + αz ZZ))
    """
    # Algorithme : diagonaliser dans la base "Bell" (magic basis)
    M = np.array([[1,0,0,1j],
                  [0,1j,1,0],
                  [0,1j,-1,0],
                  [1,0,0,-1j]]) / np.sqrt(2)
    
    U_magic = M.conj().T @ U_2q @ M
    # U_magic est une matrice orthogonale réelle (SO(4))
    O = U_magic.real
    
    # Extraction des angles de Cartan via SVD
    sigma = np.linalg.svd(O, compute_uv=False)
    alpha_x = (sigma[0] - sigma[2]) / 2  # Simplifié
    alpha_y = (sigma[1] - sigma[3]) / 2
    alpha_z = (sigma[2] - sigma[3]) / 2
    
    return {'alpha_x': alpha_x, 'alpha_y': alpha_y, 'alpha_z': alpha_z}
```

---

## 6. Transpilation de Circuits

### 6.1 Processus

1. **Décomposition** : portes multi-qubits → jeu de base
2. **Routing** : ajout de SWAPs pour respecter la topologie de couplage
3. **Optimisation** : fusion de portes adjacentes, élimination de redondances
4. **Traduction** : portes logiques → impulsions micro-ondes

### 6.2 Métriques de transpilation

```python
def transpilation_metrics(circuit_initial, circuit_final) -> dict:
    """Compare un circuit avant et après transpilation."""
    return {
        'depth_initial': circuit_initial['depth'],
        'depth_final': circuit_final['depth'],
        'gates_initial': circuit_initial['gate_count'],
        'gates_final': circuit_final['gate_count'],
        'swaps_added': circuit_final['swaps'],
        'fidelity_loss': 1 - np.prod([g['fidelity'] for g in circuit_final['gates']])
    }
```

---

## 7. Pièges et Optimisations

1. **Coût asymétrique des portes :** Une porte T coûte ~100× plus qu'une porte Clifford dans les architectures tolérantes aux fautes. Minimisez le T-count.

2. **Topologie de couplage :** Sur un processeur quantique réel, CNOT n'est possible qu'entre certaines paires de qubits. L'insertion de SWAPs triple souvent la profondeur.

3. **Phase globale ignorée :** e^{iθ}I est indétectable mais peut affecter les portes contrôlées. Soyez cohérent dans vos conventions.

4. **Décomposition non optimale :** Pour CNOT sur des qubits non adjacents dans une architecture linéaire, le coût en SWAPs est O(d²) où d est la distance.

---

## Liste de vérification

- [ ] Les 4 matrices de Pauli et leurs propriétés sont mémorisées.
- [ ] La décomposition ZYZ d'une porte 1-qubit est maîtrisée.
- [ ] Le jeu de portes Clifford+T est compris (H, S, CNOT, T).
- [ ] La décomposition de Toffoli en portes élémentaires est connue.
- [ ] Le théorème de Gottesman-Knill est compris.
- [ ] La transpilation tient compte de la topologie de couplage.
- [ ] Le T-count est minimisé pour les circuits tolérants aux fautes.
- [ ] La décomposition de Cartan pour les portes 2-qubits est disponible.
