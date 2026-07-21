---
name: quantum-computing-fundamentals
description: "Fondations de l'informatique quantique : qubits, superposition, mesure, sphère de Bloch, décohérence et postulats de la mécanique quantique."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, qubit, superposition, bloch-sphere, decoherence, measurement, quantum-mechanics]
    related_skills: [quantum-gates, qiskit-programming, quantum-entanglement]
platforms: [linux, macos, windows]
---

# Fondamentaux de l'Informatique Quantique

## Vue d'ensemble

Cette compétence couvre les **fondations mathématiques et physiques** de l'informatique quantique : la représentation des qubits, le formalisme de la mécanique quantique (postulats, opérateurs, mesure), la sphère de Bloch, la superposition, la décohérence et les types de qubits physiques. Niveau ingénieur/docteur — pas de vulgarisation.

## Quand l'utiliser

- Lorsque l'utilisateur demande les bases théoriques du calcul quantique.
- Pour implémenter une simulation de qubit, un état |ψ⟩ ou une mesure projective.
- Pour comprendre et modéliser la décohérence ou les canaux quantiques.
- Pour évaluer quel type de qubit physique (supraconducteur, ion piégé, photonique) est adapté à une application.

---

## 1. Formalisme Mathématique

### 1.1 Notation de Dirac

Un qubit est un vecteur unitaire dans ℂ² :

```
|ψ⟩ = α|0⟩ + β|1⟩,   α, β ∈ ℂ,   |α|² + |β|² = 1
```

- **Bra** : ⟨ψ| = (|ψ⟩)† = [α*, β*]
- **Produit scalaire** : ⟨φ|ψ⟩
- **Produit tensoriel** : |ψ⟩ ⊗ |φ⟩ = |ψφ⟩

Base standard :
```
|0⟩ = [1, 0]ᵀ    |1⟩ = [0, 1]ᵀ
|+⟩ = (|0⟩ + |1⟩)/√2    |−⟩ = (|0⟩ − |1⟩)/√2
```

### 1.2 Opérateurs et matrices

Un opérateur linéaire A : ℋ → ℋ agit sur un état par multiplication matricielle.

**Matrices de Pauli** (base des opérateurs 2×2 hermitiens) :

```
σₓ = [[0,1],[1,0]]   σᵧ = [[0,-i],[i,0]]   σ_z = [[1,0],[0,-1]]
```

Propriétés : σᵢ² = I, σᵢσⱼ = iεᵢⱼₖσₖ, Tr(σᵢ) = 0.

### 1.3 Sphère de Bloch

Tout état pur d'un qubit peut s'écrire :

```
|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩
```

avec 0 ≤ θ ≤ π, 0 ≤ φ < 2π.

Coordonnées de Bloch : (sin θ cos φ, sin θ sin φ, cos θ).

```python
import numpy as np

def bloch_to_state(theta: float, phi: float) -> np.ndarray:
    """Convertit les angles de Bloch en vecteur d'état."""
    return np.array([
        np.cos(theta/2),
        np.exp(1j * phi) * np.sin(theta/2)
    ])

def state_to_bloch(state: np.ndarray) -> tuple:
    """Calcule les angles (θ, φ) et le vecteur de Bloch."""
    alpha, beta = state[0], state[1]
    theta = 2 * np.arccos(np.abs(alpha))
    phi = np.angle(beta) - np.angle(alpha)
    # Vecteur de Bloch
    x = 2 * np.real(alpha.conj() * beta)
    y = 2 * np.imag(alpha.conj() * beta)
    z = np.abs(alpha)**2 - np.abs(beta)**2
    return theta, phi, (x, y, z)
```

### 1.4 États mixtes et matrice densité

Pour un système dans un mélange statistique d'états {|ψᵢ⟩, pᵢ} :

```
ρ = Σᵢ pᵢ |ψᵢ⟩⟨ψᵢ|
```

Propriétés : Tr(ρ) = 1, ρ ≥ 0 (semi-définie positive), Tr(ρ²) ≤ 1.

État pur ⇔ Tr(ρ²) = 1. État maximalement mélangé : ρ = I/2.

```python
def purity(rho: np.ndarray) -> float:
    """Calcule la pureté Tr(ρ²) d'un état."""
    return np.real(np.trace(rho @ rho))

def von_neumann_entropy(rho: np.ndarray) -> float:
    """Calcule l'entropie de von Neumann S(ρ) = -Tr(ρ log ρ)."""
    evals = np.linalg.eigvalsh(rho)
    evals = evals[evals > 1e-15]
    return -np.sum(evals * np.log2(evals))
```

---

## 2. Postulats de la Mécanique Quantique

| Postulat | Énoncé | Implication |
|:---|:---|:---|
| **1 — États** | L'état d'un système est un vecteur unitaire dans un espace de Hilbert | Un qubit = ℂ², n qubits = (ℂ²)⊗ⁿ |
| **2 — Évolution** | L'évolution est unitaire : |ψ(t)⟩ = U(t)|ψ(0)⟩ | Portes quantiques = opérateurs unitaires |
| **3 — Mesure** | La mesure projette l'état selon un ensemble d'opérateurs {Mₘ} | Résultat m avec probabilité p(m) = ⟨ψ|Mₘ†Mₘ|ψ⟩ |
| **4 — Produit tensoriel** | L'espace d'état composite est le produit tensoriel des espaces | L'intrication émerge du non-séparabilité |

### 2.1 Mesure projective

Opérateur de mesure : Mₘ = |m⟩⟨m| (projecteur). Résultat m, probabilité p(m) = |⟨m|ψ⟩|².

Après mesure, l'état devient : |ψ'⟩ = (Mₘ|ψ⟩) / √p(m).

```python
def measure(psi: np.ndarray, num_qubits: int) -> tuple:
    """Mesure projective dans la base computationnelle."""
    n = len(psi)
    probs = np.abs(psi)**2
    outcome = np.random.choice(n, p=probs)
    # Nouvel état après mesure
    new_psi = np.zeros_like(psi)
    new_psi[outcome] = 1.0
    return outcome, new_psi
```

---

## 3. Décohérence et Bruit

### 3.1 Canaux quantiques (CPTP)

Un canal quantique est une carte linéaire complètement positive et préservant la trace (CPTP) :

```
ε(ρ) = Σₖ Eₖ ρ Eₖ†,   Σₖ Eₖ†Eₖ = I
```

### 3.2 Canaux importants

**Canal de dépolarisation** (bruit isotrope) :
```
E₀ = √(1-p) I,   E₁ = √(p/3) σₓ,   E₂ = √(p/3) σᵧ,   E₃ = √(p/3) σ_z
```

**Canal d'amortissement de phase** (T₂) :
```
E₀ = √(λ) I,   E₁ = √(1-λ) σ_z,   λ = (1+e^{-t/T₂})/2
```

**Canal d'amortissement d'amplitude** (T₁) :
```
E₀ = [[1,0],[0,√(1-γ)]],   E₁ = [[0,√γ],[0,0]]
```

```python
def depolarizing_channel(rho: np.ndarray, p: float) -> np.ndarray:
    """Applique un canal de dépolarisation d'intensité p."""
    dim = rho.shape[0]
    result = (1 - p) * rho
    result += (p / 3) * sigma_x @ rho @ sigma_x
    result += (p / 3) * sigma_y @ rho @ sigma_y
    result += (p / 3) * sigma_z @ rho @ sigma_z
    return result
```

### 3.3 Temps caractéristiques

- **T₁** : temps de relaxation d'amplitude (|1⟩ → |0⟩) — perte d'énergie
- **T₂*** : temps de déphasage inhomogène (FID)
- **T₂** : temps de déphasage homogène (Echo), 1/T₂ = 1/(2T₁) + 1/T_φ
- **Fidélité** : F(ρ, σ) = Tr(√(√ρ σ √ρ)) — overlap entre état réel et idéal

```python
def fidelity(rho: np.ndarray, sigma: np.ndarray) -> float:
    """Calcule la fidélité Uhlmann-Jozsa entre deux états."""
    sqrt_rho = scipy.linalg.sqrtm(rho)
    inner = sqrt_rho @ sigma @ sqrt_rho
    return np.real(np.trace(scipy.linalg.sqrtm(inner)))**2
```

---

## 4. Types de Qubits Physiques

| Technologie | T₁ (typ.) | T₂ (typ.) | Fidélité porte | Porte 2q | Échelle | Avantage |
|:---|:---|:---|:---|:---|:---|:---|
| **Supraconducteur** (IBM, Google) | 100-300 µs | 50-200 µs | 99.9% | 99.6% | 1000+ | Maturité, connectique |
| **Ion piégé** (IonQ, Quantinuum) | Minutes | 100 ms-1 s | 99.99% | 99.9% | 50+ | Faible erreur, connectivité |
| **Photonique** (Xanadu, PsiQuantum) | N/A | N/A | 99% | 98% | 100+ | Température ambiante |
| **Atome neutre** (QuEra) | 1 s | 100 ms | 99.9% | 99.5% | 256+ | Taille massive |
| **Spin de silicium** (Intel) | 1 s | 100 µs | 99.9% | 99.5% | 100+ | Compatible fonderie |
| **Topologique** (Microsoft) | Théorique | Théorique | Théorique | — | 0 | Correction d'erreur native |

---

## 5. Circuits Quantiques Fondamentaux

### 5.1 Préparation d'états de base

```python
import numpy as np

def prepare_bell_state() -> np.ndarray:
    """Prépare |Φ⁺⟩ = (|00⟩ + |11⟩)/√2."""
    psi = np.zeros(4, dtype=complex)
    psi[0] = 1.0
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    CNOT = np.array([
        [1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]
    ])
    psi = np.kron(H, np.eye(2)) @ psi
    psi = CNOT @ psi
    return psi

def prepare_ghz_state(n: int) -> np.ndarray:
    """Prépare |GHZₙ⟩ = (|0⟩⊗ⁿ + |1⟩⊗ⁿ)/√2."""
    dim = 2**n
    psi = np.zeros(dim, dtype=complex)
    psi[0] = 1.0
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    # H sur premier qubit
    psi = np.kron(H, np.eye(dim // 2)) @ psi
    # CNOT i → i+1
    for i in range(n-1):
        psi = apply_cnot(psi, n, i, i+1)
    return psi

def apply_cnot(psi, n, control, target):
    """Applique CNOT entre control et target sur n qubits."""
    dim = 2**n
    result = np.zeros_like(psi)
    for i in range(dim):
        c_bit = (i >> (n-1-control)) & 1
        t_bit = (i >> (n-1-target)) & 1
        if c_bit == 1:
            j = i ^ (1 << (n-1-target))
        else:
            j = i
        result[j] = psi[i]
    return result
```

### 5.2 Discriminabilité d'états (Helstrom)

```python
def helstrom_bound(rho0: np.ndarray, rho1: np.ndarray) -> float:
    """Borne de Helstrom : probabilité max de distinguer deux états."""
    delta = rho0 - rho1
    # Norme trace : ||Δ||₁ = Tr(√(Δ†Δ))
    trace_norm = np.sum(np.abs(np.linalg.eigvalsh(delta)))
    return 0.5 * (1 + 0.5 * trace_norm)
```

---

## 6. Pièges et Limitations

1. **Simulation classique de qubits :** Simuler n qubits nécessite O(2ⁿ) éléments — au-delà de 30-35 qubits, la mémoire explose (~16 Go pour 30 qb). Utilisez des simulateurs GPU ou tensor network pour n > 30.

2. **Confusion probabilité vs amplitude :** Les amplitudes α, β sont complexes ; les probabilités sont |α|², |β|². Les interférences (signes) sont cruciales pour les algorithmes quantiques.

3. **Non-clonage :** Un qubit inconnu ne peut pas être copié parfaitement (no-cloning theorem). Impossible de faire backup d'un état quantique.

4. **Mesure destructive :** La mesure projette l'état — on ne mesure pas un qubit sans le modifier. Compensez par des mesures répétées sur des préparations identiques.

5. **Échelle de la décohérence :** T₁ et T₂ typiques sont de l'ordre de 100 µs pour les qubits supraconducteurs. Une porte à 50 ns donne ~2000 portes max avant décohérence.

---

## Liste de vérification

- [ ] Le formalisme (notation de Dirac, opérateurs, mesure projective) est maîtrisé.
- [ ] La sphère de Bloch est utilisée pour visualiser l'état d'un qubit.
- [ ] Les matrices de Pauli et leurs propriétés sont connues.
- [ ] La différence entre états purs et mixtes (matrice densité) est comprise.
- [ ] Les canaux quantiques (dépolarisation, phase, amplitude) sont modélisés.
- [ ] Les temps T₁, T₂ et la fidélité sont calculés pour un système donné.
- [ ] Les types de qubits physiques et leurs caractéristiques sont comparés.
- [ ] Les limites de simulation classique (2ⁿ mémoire) sont respectées.
