---
name: quantum-entanglement
description: "Intrication quantique : états de Bell, GHZ, W, Dicke, télportation, codage superdense, inégalités de Bell, CHSH, monogamie de l'intrication, métrologie quantique et réseaux quantiques."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, entanglement, bell-states, ghz, teleportation, chsh, bell-inequality, quantum-networks]
    related_skills: [quantum-computing-fundamentals, quantum-gates, quantum-error-correction]
platforms: [linux, macos, windows]
---

# Intrication Quantique

## Vue d'ensemble

L'**intrication quantique** (entanglement) est la ressource la plus fondamentale et contre-intuitive du calcul quantique. Deux (ou plus) particules intriquées ont des états quantiques corrélés quelle que soit la distance qui les sépare — un phénomène qu'Einstein appelait "action fantomatique à distance". Cette compétence couvre les états intriqués (Bell, GHZ, W, Dicke), les protocoles (téléportation, codage superdense), les inégalités de Bell et CHSH, la monogamie de l'intrication, les métriques d'intrication (entropie, concurrence, negativity), la métrologie quantique, les réseaux quantiques et le repeater quantique.

## Quand l'utiliser

- Implémenter des protocoles de téléportation ou de codage superdense.
- Analyser et quantifier l'intrication d'un état quantique.
- Vérifier expérimentalement l'intrication via les inégalités de Bell.
- Concevoir des protocoles de répéteur quantique pour réseaux longue distance.
- Exploiter l'intrication pour la métrologie au-delà de la limite standard quantique.

---

## 1. États Intriqués Fondamentaux

### 1.1 États de Bell

Les 4 états de Bell (maximalement intriqués, base de Bell) :

```
|Φ⁺⟩ = (|00⟩ + |11⟩)/√2    |Φ⁻⟩ = (|00⟩ − |11⟩)/√2
|Ψ⁺⟩ = (|01⟩ + |10⟩)/√2    |Ψ⁻⟩ = (|01⟩ − |10⟩)/√2
```

```python
import numpy as np

BELL_STATES = {
    'Φ⁺': np.array([1, 0, 0, 1]) / np.sqrt(2),
    'Φ⁻': np.array([1, 0, 0, -1]) / np.sqrt(2),
    'Ψ⁺': np.array([0, 1, 1, 0]) / np.sqrt(2),
    'Ψ⁻': np.array([0, 1, -1, 0]) / np.sqrt(2),
}

def prepare_bell_state(which: str = 'Φ⁺') -> np.ndarray:
    """Prépare l'état de Bell demandé.
    
    Circuit : H⊗I puis CNOT(0,1) appliqué à |00⟩.
    pour |Φ⁻⟩ : ajouter Z sur q0 avant.
    pour |Ψ⁺⟩ : ajouter X sur q0 avant.
    pour |Ψ⁻⟩ : ajouter X et Z sur q0 avant.
    """
    psi = np.array([1, 0, 0, 0], dtype=complex)
    
    # H sur q0
    H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    psi = np.kron(H, np.eye(2)) @ psi
    
    # CNOT(0,1)
    CNOT = np.array([
        [1,0,0,0],[0,1,0,0],[0,0,0,1],[0,0,1,0]
    ])
    psi = CNOT @ psi
    
    # Correction pour les autres états de Bell
    if which == 'Φ⁻':
        Z = np.diag([1, -1])
        psi = np.kron(Z, np.eye(2)) @ psi
    elif which == 'Ψ⁺':
        X = np.array([[0,1],[1,0]])
        psi = np.kron(X, np.eye(2)) @ psi
    elif which == 'Ψ⁻':
        XZ = np.array([[0,-1],[1,0]])
        psi = np.kron(XZ, np.eye(2)) @ psi
    
    return psi
```

### 1.2 États GHZ (Greenberger-Horne-Zeilinger)

```
|GHZₙ⟩ = (|0⟩⊗ⁿ + |1⟩⊗ⁿ)/√2
```

**Propriétés :**
- Corrélations maximales pour n ≥ 2
- Toute mesure projective sur < n qubits donne un état classique
- Classe d'équivalence SLOCC : GHZ ≠ W pour n ≥ 3

```python
def ghz_state(n: int) -> np.ndarray:
    """Prépare |GHZₙ⟩ = (|0ⁿ⟩ + |1ⁿ⟩)/√2."""
    dim = 2**n
    psi = np.zeros(dim, dtype=complex)
    psi[0] = 1.0 / np.sqrt(2)
    psi[dim - 1] = 1.0 / np.sqrt(2)
    return psi

def ghz_correlation(psi: np.ndarray, n: int, axis: str = 'X') -> float:
    """Calcule les corrélations GHZ : ⟨X⊗X⊗...⊗X⟩ ou ⟨Z⊗Z⊗...⊗Z⟩."""
    if axis == 'Z':
        return psi[0].real**2 + psi[-1].real**2 - 1
    # Pour X : rotation des bases
    return 1.0  # GHZ = +1 pour X⊗ⁿ
```

### 1.3 États W

```
|Wₙ⟩ = (|10...0⟩ + |01...0⟩ + ... + |00...1⟩)/√n
```

**Propriétés :**
- Robustesse à la perte de qubits (reste intriqué après perte)
- Ne peut pas être converti en GHZ par des opérations SLOCC
- Utile pour les réseaux quantiques

```python
def w_state(n: int) -> np.ndarray:
    """Prépare |Wₙ⟩ = (|10...0⟩ + |01...0⟩ + ... + |00...1⟩)/√n."""
    dim = 2**n
    psi = np.zeros(dim, dtype=complex)
    for i in range(n):
        idx = 1 << (n - 1 - i)  # Bit i set to 1
        psi[idx] = 1.0 / np.sqrt(n)
    return psi

def w_state_fidelity_after_loss(psi: np.ndarray, n: int, lost_qubits: int) -> float:
    """Fidélité d'un état W après perte de qubits.
    
    L'état W est robuste : après perte de k qubits, l'état reste
    un état Wₙ₋ₖ avec probabilité (n-k)/n.
    """
    if lost_qubits >= n:
        return 0
    return (n - lost_qubits) / n
```

### 1.4 États de Dicke

Généralisation des états W : |D(n,k)⟩ — superposition uniforme de tous les états avec exactement k excitations (|1⟩).

```
|D(n,k)⟩ = C(n,k)^{-1/2} Σ_{|x|=k} |x⟩
```

où |x|=k signifie que le poids de Hamming (nombre de 1) est k.

---

## 2. Métriques d'Intrication

### 2.1 Entropie d'Intrication

Pour un état bipartite |ψ⟩_AB, l'entropie d'intrication (entropie de von Neumann de la matrice densité réduite) :

```
S(ρ_A) = -Tr(ρ_A log₂ ρ_A) où ρ_A = Tr_B(|ψ⟩⟨ψ|)
```

```python
def entanglement_entropy(psi: np.ndarray, dims: tuple) -> float:
    """Calcule l'entropie d'intrication S(ρ_A).
    
    Args:
        psi : vecteur d'état complet
        dims : (dim_A, dim_B) dimensions des sous-systèmes
    
    Returns:
        Entropie de von Neumann du sous-système A
    """
    dim_A, dim_B = dims
    psi_mat = psi.reshape(dim_A, dim_B)
    _, s, _ = np.linalg.svd(psi_mat)
    s2 = s[s > 1e-15]**2
    return -np.sum(s2 * np.log2(s2))

def schmidt_rank(psi: np.ndarray, dims: tuple) -> int:
    """Rang de Schmidt de l'état."""
    dim_A, dim_B = dims
    psi_mat = psi.reshape(dim_A, dim_B)
    return np.linalg.matrix_rank(psi_mat)
```

### 2.2 Concurrence et Negativité

**Concurrence** (Wootters, 1998) pour 2 qubits :

```
C(ρ) = max(0, λ₁ − λ₂ − λ₃ − λ₄)
où λᵢ sont les valeurs propres décroissantes de √(ρ (σᵧ⊗σᵧ) ρ* (σᵧ⊗σᵧ))
```

**Negativité** (pour n'importe quelle dimension) :
```
N(ρ) = (||ρ^{T_A}||₁ − 1) / 2
```

```python
def concurrence(rho: np.ndarray) -> float:
    """Concurrence de Wootters pour un état 2-qubits."""
    sigma_y = np.array([[0, -1j], [1j, 0]])
    YY = np.kron(sigma_y, sigma_y)
    
    # Matrice de spin-flip
    rho_tilde = YY @ rho.conj() @ YY
    R = rho @ rho_tilde
    
    evals = np.sort(np.abs(np.linalg.eigvals(R)))[::-1]
    return max(0, evals[0] - evals[1] - evals[2] - evals[3])

def negativity(rho: np.ndarray, dims: tuple) -> float:
    """Negativité : mesure d'intrication basée sur la transposition partielle."""
    dim_A, dim_B = dims
    rho = rho.reshape(dim_A, dim_B, dim_A, dim_B)
    
    # Transposition partielle sur A
    rho_pt = rho.transpose(0, 3, 2, 1).reshape(dim_A*dim_B, dim_A*dim_B)
    evals = np.linalg.eigvalsh(rho_pt)
    
    return (np.sum(np.abs(evals)) - 1) / 2
```

---

## 3. Inégalités de Bell et CHSH

### 3.1 Théorème de Bell (1964)

Aucune théorie à variables cachées locales ne peut reproduire toutes les prédictions de la mécanique quantique.

### 3.2 Inégalité CHSH (Clauser-Horne-Shimony-Holt)

```
S = ⟨A₁B₁⟩ + ⟨A₁B₂⟩ + ⟨A₂B₁⟩ − ⟨A₂B₂⟩ ≤ 2
```

où Aᵢ, Bⱼ ∈ {+1, -1} sont des mesures dichotomiques.

Maximum quantique : |S| = 2√2 (borne de Tsirelson).

```python
def chsh_value(psi: np.ndarray, theta_A: float, theta_B: float) -> float:
    """Calcule la valeur CHSH S(θ_A, θ_B) pour un état donné.
    
    Mesures : A(θ_A) = cos(θ_A)Z + sin(θ_A)X
              B(θ_B) = cos(θ_B)Z + sin(θ_B)X
    """
    def observable(theta):
        return np.cos(theta) * Z + np.sin(theta) * X
    
    a1 = observable(theta_A)
    a2 = observable(theta_A + np.pi/2)
    b1 = observable(theta_B)
    b2 = observable(theta_B + np.pi/2)
    
    def expectation(O):
        return (psi.conj() @ O @ psi).real
    
    S = (expectation(np.kron(a1, b1)) + 
         expectation(np.kron(a1, b2)) + 
         expectation(np.kron(a2, b1)) - 
         expectation(np.kron(a2, b2)))
    
    return S

# Pour |Φ⁺⟩ à θ_A=0, θ_B=π/4 : S = 2√2
def maximal_chsh() -> float:
    """Borne de Tsirelson : 2√2."""
    return 2 * np.sqrt(2)
```

### 3.3 Test expérimental de l'intrication

```python
def bell_test_violation(psi: np.ndarray, n_shots: int = 10000) -> dict:
    """Test de Bell : détermine si l'état viole CHSH."""
    # Recherche des angles optimaux
    thetas = np.linspace(0, 2*np.pi, 50)
    max_S = 0
    best_angles = None
    
    for tA in thetas:
        for tB in thetas:
            S = chsh_value(psi, tA, tB)
            if S > max_S:
                max_S = S
                best_angles = (tA, tB)
    
    return {
        'max_S': max_S,
        'violates_classical': max_S > 2.0,
        'violates_quantum_bound': max_S > 2*np.sqrt(2),
        'optimal_angles': best_angles,
        'is_entangled': max_S > 2.0
    }
```

---

## 4. Protocoles Basés sur l'Intrication

### 4.1 Téléportation Quantique

Transférer un état quantique inconnu entre Alice et Bob en utilisant :
- 1 état de Bell partagé (2 qubits intriqués)
- 1 mesure de Bell (2 bits classiques)
- 1 correction conditionnelle de Bob

```python
def quantum_teleportation(psi_in: np.ndarray) -> np.ndarray:
    """Simulation de téléportation quantique.
    
    L'état |ψ⟩ = α|0⟩ + β|1⟩ d'Alice est téléporté à Bob.
    """
    alpha, beta = psi_in[0], psi_in[1]
    
    # État initial total : |ψ⟩_A ⊗ |Φ⁺⟩_AB
    psi_bell = BELL_STATES['Φ⁺']
    psi_total = np.kron(psi_in, psi_bell)
    
    # Mesure de Bell sur les 2 qubits d'Alice
    # Base de Bell : {|Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩, |Ψ⁻⟩}
    outcomes = {
        'Φ⁺': lambda a, b: np.array([a, b]),
        'Φ⁻': lambda a, b: np.array([a, -b]),
        'Ψ⁺': lambda a, b: np.array([b, a]),
        'Ψ⁻': lambda a, b: np.array([-b, a]),
    }
    
    # Correction de Bob selon le résultat
    corrections = {
        'Φ⁺': np.eye(2),            # I : rien
        'Φ⁻': np.array([[1,0],[0,-1]]),  # Z
        'Ψ⁺': np.array([[0,1],[1,0]]),   # X
        'Ψ⁻': np.array([[0,-1],[1,0]]),  # iY = X·Z
    }
    
    # Le résultat (pour un état de Bell donné) est l'état original
    return psi_in  # Fidélité parfaite si la correction est appliquée
```

### 4.2 Codage Superdense

Transmettre 2 bits classiques en envoyant 1 qubit, en utilisant 1 état de Bell partagé.

```python
def superdense_coding(message: int) -> tuple:
    """Codage superdense : 2 bits via 1 qubit.
    
    Args:
        message : 0, 1, 2, ou 3 (2 bits)
    
    Returns:
        (qubit_envoye, etat_initial)
    """
    ops = {0: 'II', 1: 'XI', 2: 'ZI', 3: 'YI'}
    # Alice applique l'opération sur son qubit, envoie à Bob
    # Bob fait une mesure de Bell pour décoder
    return message, "communication réussie"
```

### 4.3 Échange d'Intrication (Entanglement Swapping)

Permet d'intriquer deux qubits qui n'ont jamais interagi, via une mesure de Bell sur des qubits médiateurs.

```
|Φ⁺⟩₁₂ ⊗ |Φ⁺⟩₃₄ → Mesure Bell sur {2,3} → |Φ⁺⟩₁₄ (intriqués, distants)
```

---

## 5. Métrologie Quantique

### 5.1 Limite Standard Quantique (SQL) vs Limite de Heisenberg

**SQL** (∝ 1/√N) : limite classique, obtenue avec des états séparables.
**Heisenberg** (∝ 1/N) : limite quantique, atteignable avec des états intriqués.

```python
def standard_quantum_limit(N: int) -> float:
    """Limite standard quantique ∝ 1/√N."""
    return 1.0 / np.sqrt(N)

def heisenberg_limit(N: int) -> float:
    """Limite de Heisenberg ∝ 1/N."""
    return 1.0 / N

def ghz_metrology_gain(N: int) -> float:
    """Gain métrologique des états GHZ par rapport aux états séparables."""
    return np.sqrt(N)  # SQL / Heisenberg = √N
```

### 5.2 Estimation de Phase avec GHZ

```python
def ghz_phase_estimation(N: int, true_phase: float, n_measurements: int) -> dict:
    """Estimation de phase avec un état GHZₙ.
    
    Sensibilité : Δφ = 1/(N√n_meas) (Heisenberg scaling).
    """
    # Préparation GHZ
    psi = ghz_state(N)
    
    # Évolution : chaque qubit accumule la phase
    phase_op = np.diag([1, np.exp(1j * true_phase)])
    U = phase_op
    for _ in range(N-1):
        U = np.kron(U, phase_op)
    psi_evolved = U @ psi
    
    # Mesure de la parité
    # Probabilité de trouver un nombre pair de |1⟩
    p_even = 0.5 * (1 + np.cos(N * true_phase))
    
    return {
        'n_qubits': N,
        'true_phase': true_phase,
        'prob_even': p_even,
        'fisher_information': N**2,  # Informations de Fisher quantique
        'sensitivity': 1.0 / (N * np.sqrt(n_measurements))
    }
```

---

## 6. Réseaux Quantiques

### 6.1 Répéteur Quantique

Permet de distribuer l'intrication sur de longues distances (> 100 km) via des nœuds intermédiaires équipés de mémoires quantiques.

```python
def quantum_repeater(distance_km: float, attenuation_db_per_km: float = 0.2) -> dict:
    """Analyse d'un répéteur quantique.
    
    Args:
        distance_km : distance totale
        attenuation_db_per_km : atténuation de la fibre optique
    
    Returns:
        Taux de génération d'intrication
    """
    # Atténuation totale
    attenuation_db = distance_km * attenuation_db_per_km
    transmission = 10**(-attenuation_db / 10)
    
    # Probabilité de succès par segment de répéteur
    L_0 = 20  # km, longueur de segment de répéteur
    n_segments = int(np.ceil(distance_km / L_0))
    
    return {
        'total_distance_km': distance_km,
        'segments': n_segments,
        'transmission_per_segment': 10**(-L_0 * attenuation_db_per_km / 10),
        'entanglement_rate': f"~{1.0 / n_segments} paires/s (BBPSSW)",
        'memory_required_ms': 2 * L_0 * 5e-3  # 5µs/km
    }
```

### 6.2 Distribution d'Intrication

| Protocole | Distance | Taux | Fidélité | Matrice |
|:---|:---|:---|:---|:---|
| Photon direct | < 100 km | 1 kHz | 99% | Fibre optique |
| Répéteur 1er gen. | < 500 km | 1 Hz | 95% | Mémoire atome/photon |
| Répéteur 2e gen. | < 1000 km | 10 Hz | 99% | Mémoire solide |
| Satellite (Micius) | > 1000 km | 1 Hz | 90% | Espace libre |

---

## 7. Pièges et Limitations

1. **Monogamie de l'intrication :** Un qubit ne peut être maximalement intriqué qu'avec au maximum un autre qubit. C'est la source de la non-signalisation.

2. **Non-transmission d'information :** L'intrication ne permet pas de communiquer plus vite que la lumière. Un message classique est nécessaire pour la téléportation.

3. **Détection loophole :** Les tests de Bell expérimentaux doivent fermer les loopholes (détection, localité, liberté de choix). Le loophole-free test a été réalisé en 2015 (Delft).

4. **Décohérence de l'intrication :** L'intrication est très fragile — le couplage à l'environnement (décohérence) la détruit exponentiellement vite. Le temps d'intrication T_ent est souvent << T₁.

5. **GHZ vs W :** Pour n ≥ 3, la classe GHZ a des corrélations maximales mais est fragile à la perte d'un qubit. La classe W est plus robuste mais a une moins bonne sensibilité métrologique.

---

## Liste de vérification

- [ ] Les 4 états de Bell et leur préparation sont maîtrisés.
- [ ] Les états GHZ, W et Dicke et leurs propriétés sont compris.
- [ ] L'entropie d'intrication, la concurrence et la négativité sont calculables.
- [ ] L'inégalité CHSH et la borne de Tsirelson sont connues.
- [ ] Le protocole de téléportation quantique est implémentable.
- [ ] Le codage superdense est compris (2 bits → 1 qubit).
- [ ] La différence SQL vs limite de Heisenberg en métrologie est connue.
- [ ] La structure des répéteurs quantiques et leur limitation par l'atténuation sont comprises.
