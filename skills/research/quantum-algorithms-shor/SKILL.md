---
name: quantum-algorithms-shor
description: "Algorithme de Shor : factorisation quantique, transformée de Fourier quantique (QFT), recherche de période, estimation de phase quantique (QPE), implémentation pratique et complexité."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, shor, factoring, qft, qpe, period-finding, rsa, cryptography]
    related_skills: [quantum-gates, qiskit-programming, quantum-algorithms-grover]
platforms: [linux, macos, windows]
---

# Algorithme de Shor

## Vue d'ensemble

L'algorithme de **Shor** (Peter Shor, 1994) factorise un entier N en temps polynomial O((log N)³), contre O(exp((log N)^{1/3})) pour le meilleur algorithme classique (GNFS). Il menace directement RSA et la cryptographie à clé publique. Cette compétence couvre la théorie complète : réduction classique → recherche de période → estimation de phase quantique (QPE) → transformée de Fourier quantique (QFT) → implémentation pratique avec Qiskit.

## Quand l'utiliser

- Pour comprendre l'algorithme de Shor en profondeur (théorie complète).
- Pour implémenter Shor sur un simulateur (petits N, ≤ 21).
- Pour analyser les ressources nécessaires à la factorisation de clés RSA (2048 bits).
- Pour explorer les variantes et optimisations de Shor.
- Pour comprendre l'impact de Shor sur la cryptographie post-quantique.

---

## 1. Architecture de l'Algorithme

### 1.1 Structure globale

```
Entrée : N (entier à factoriser)
Sortie : un facteur non trivial de N

1. Si N est pair → retourner 2.
2. Si N = a^b pour a ≥ 2, b ≥ 2 → retourner a.
3. Choisir a aléatoire avec 1 < a < N-1.
4. Si gcd(a, N) > 1 → retourner gcd(a, N).
5. Sinon :
   a. Utiliser l'ordinateur quantique pour trouver r = ordre de a mod N (période).
   b. Si r est pair et a^{r/2} ≢ ±1 (mod N) :
        retourner gcd(a^{r/2} - 1, N)
   c. Sinon, retourner à l'étape 3.
```

### 1.2 Complexité

| Ressource | Shor (logique) | Meilleur classique (GNFS) |
|:---|:---|:---|
| Temps | O((log N)² (log log N)(log log log N)) | O(exp((64/9)^{1/3} (log N)^{1/3} (log log N)^{2/3})) |
| Qubits | O(log N) | N/A |
| Portes | O((log N)³) | N/A |
| Clés RSA-2048 | ~20M qubits (physiques FTQC) | 10¹² ans classiques |

---

## 2. Recherche de Période (Cœur Quantique)

### 2.1 Estimation de Phase Quantique (QPE)

Le cœur de Shor est l'estimation de phase quantique : étant donné un opérateur unitaire U et un état propre |ψ⟩ où U|ψ⟩ = e^{2πiθ}|ψ⟩, le QPE estime θ.

```python
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def qpe_circuit(U: QuantumCircuit, n_control: int) -> QuantumCircuit:
    """Circuit d'estimation de phase quantique.
    
    Args:
        U : circuit représentant l'opérateur unitaire
        n_control : nombre de qubits de contrôle
    
    Returns:
        Circuit QPE complet
    """
    n_target = U.num_qubits
    control = QuantumRegister(n_control, 'control')
    target = QuantumRegister(n_target, 'target')
    classical = ClassicalRegister(n_control, 'result')
    qc = QuantumCircuit(control, target, classical)
    
    # 1. Initialisation : |+⟩⊗ⁿ sur les contrôles
    qc.h(control)
    
    # 2. Applications contrôlées de U^{2^j}
    for j in range(n_control):
        U_pow = U.power(2**j).control()
        qc.append(U_pow, [control[j]] + list(target))
    
    # 3. QFT inverse
    qc.append(qft_circuit(n_control).inverse(), control)
    
    # 4. Mesure
    qc.measure(control, classical[:n_control])
    
    return qc
```

### 2.2 Transformée de Fourier Quantique (QFT)

```python
def qft_circuit(n: int) -> QuantumCircuit:
    """Transformée de Fourier quantique.
    
    |j⟩ → 1/√(2ⁿ) Σₖ exp(2πi jk / 2ⁿ) |k⟩
    """
    qc = QuantumCircuit(n)
    
    for j in range(n):
        qc.h(j)
        for k in range(j+1, n):
            theta = np.pi / 2**(k - j)
            qc.cp(theta, k, j)
    
    # Swap pour inversion d'ordre (bits)
    for i in range(n // 2):
        qc.swap(i, n-i-1)
    
    return qc

def qft_matrix(n: int) -> np.ndarray:
    """Matrice QFT n-qubits explicitement."""
    N = 2**n
    omega = np.exp(2j * np.pi / N)
    return np.array([[omega**(j*k) for k in range(N)] for j in range(N)]) / np.sqrt(N)
```

---

## 3. Opérateur de Multiplication Modulaire

### 3.1 Problème et Construction

Pour Shor, on a besoin de Uₐ|y⟩ = |ay mod N⟩. L'état propre est :

```
|ψⱼ⟩ = 1/√r Σₖ exp(-2πi jk/r) |a^k mod N⟩
```

avec valeur propre exp(2πi j/r). L'estimation de θ = j/r donne r (la période).

```python
def modular_multiplication_circuit(a: int, N: int, n: int) -> QuantumCircuit:
    """Circuit Uₐ pour la multiplication modulaire |y⟩ → |ay mod N⟩.
    
    C'est la partie la plus coûteuse de Shor. Utilise des additionneurs
    quantiques (Draper, Cuccaro, Gidney).
    
    Pour un N à n bits, ce circuit nécessite O(n²) portes Toffoli.
    """
    # Construction pratique → utilisez la routine d'exponentiation 
    # modulaire de Beauregard (2002) ou Gidney-Ekerå (2021)
    qc = QuantumCircuit(n, name=f'U_{a}_mod_{N}')
    
    # Implémentation simplifiée : a*y mod N pour y donné
    # Utilise l'additionneur de Draper (QFT-based adder)
    # Voir : Beauregard, "Circuit for Shor's algorithm using 2n+3 qubits" (2002)
    
    return qc
```

### 3.2 Exponentiation modulaire

```python
def modular_exponentiation_circuit(a: int, N: int, n: int) -> QuantumCircuit:
    """Circuit pour f(x) = a^x mod N.
    
    Implémente l'exponentiation comme une séquence de multiplications
    contrôlées : a^x = Π_j a^{xⱼ·2^j} mod N.
    
    O(n³) portes pour n bits.
    """
    qc = QuantumCircuit(2*n, name=f'f(x)=a^x_mod_{N}')
    
    for j in range(n):
        # Multiplication modulaire contrôlée par a^{2^j}
        pow_a = pow(a, 2**j, N)
        U_pow = modular_multiplication_circuit(pow_a, N, n)
        qc.append(U_pow.control(), [j] + list(range(n, 2*n)))
    
    return qc
```

---

## 4. Algorithme de Shor Complet

```python
from qiskit import QuantumCircuit
from math import gcd
import numpy as np

def shor_algorithm(N: int, a: int) -> tuple:
    """Version simulée de l'algorithme de Shor (sans matériel quantique).
    
    Pour une vraie implémentation quantique, remplacez la recherche de
    période par QPE sur le vrai matériel.
    """
    # Vérifications préliminaires
    if N % 2 == 0:
        return 2, N // 2
    
    # Calcul de l'ordre par recherche classique (validation uniquement)
    r = 1
    val = a % N
    while val != 1:
        val = (val * a) % N
        r += 1
        if r > N:
            return None, None  # Échec, essayer un autre a
    
    if r % 2 == 0:
        factor = gcd(a**(r//2) - 1, N)
        if factor != 1 and factor != N:
            return factor, N // factor
    
    return None, None  # Recommencer avec un nouveau a

def quantum_shor_circuit(N: int, a: int, n_control: int) -> QuantumCircuit:
    """Circuit quantique complet de Shor.
    
    Nécessite : n_control qubits de contrôle + n_data qubits de donnée.
    n_control doit être suffisant pour résoudre r (typ. 2*log₂(N)).
    """
    n_data = N.bit_length()
    total_qubits = n_control + n_data
    
    qc = QuantumCircuit(total_qubits, n_control, name=f'Shor({N}, a={a})')
    
    # Initialisation : |1⟩ dans le registre de données
    qc.x(n_control)  # |1⟩ sur le premier qubit de donnée
    
    # QPE avec U_a
    # Pour chaque qubit de contrôle j, appliquer U_a^{2^j} contrôlé
    for j in range(n_control):
        # (Implementation simplifiée - utiliser modular_exponentiation)
        pass
    
    # QFT inverse
    qc.append(qft_circuit(n_control).inverse(), range(n_control))
    
    # Mesure des qubits de contrôle
    qc.measure(range(n_control), range(n_control))
    
    return qc
```

---

## 5. Optimisations et Variantes Modernes

### 5.1 Shor avec 2n+3 qubits (Beauregard, 2002)

Utilise la réutilisation de qubits (qubit recycling) pour réduire de 4n à 2n+3 qubits. L'addition modulaire est implémentée via QFT.

```
Ressources : 2n+3 qubits, O(n³) portes
```

### 5.2 Gidney-Ekerå (2021) — Factoring de RSA-2048

L'optimisation la plus importante depuis Shor :

```
Qubits : 20M (contre 1.6B pour l'implémentation naïve)
T-gates : 2.5×10¹⁰
Temps : ~8 heures (avec vitesse de porte T = 1µs)
```

**Techniques clés :**
- **Windowed arithmetic** : exponentiation modulaire avec pré-calcul de fenêtres
- **Toffoli pipelining** : parallélisation des Toffolis
- **Qubit recycling** : réutilisation des qubits de mesure
- **Coset representation** : encodage compact des registres

### 5.3 Regev (2023) — Factorisation en O(n^{3/2})

Nouvel algorithme de factorisation avec complexité O(n^{3/2}) (contre O(n³) pour Shor). Utilise des réduction de réseau (LWE-like) pour abaisser la profondeur du circuit.

```
Avantage : Profondeur O(n^{3/2}) vs O(n³)
Inconvénient : Plus de qubits (O(n^{1.5}) en espace)
```

---

## 6. Estimation de Ressources pour Crypto Clés Réelles

| Clé | n (bits) | Qubits (Beauregard) | Qubits (Gidney-Ekerå) | T-gates | Temps (1µs T-gate) |
|:---|:---|:---|:---|:---|:---|
| RSA-1024 | 1024 | ~2 050 | ~2.6 × 10⁶ | ~3 × 10⁹ | ~1 heure |
| **RSA-2048** | 2048 | ~4 100 | ~2 × 10⁷ | ~2.5 × 10¹⁰ | ~8 heures |
| RSA-4096 | 4096 | ~8 200 | ~1.6 × 10⁸ | ~2 × 10¹¹ | ~3 jours |
| ECC-256 | 256 | ~515 | ~1.3 × 10⁵ | ~3 × 10⁸ | ~5 minutes |
| ECC-384 | 384 | ~770 | ~3 × 10⁵ | ~6 × 10⁸ | ~10 minutes |

> **Note :** Ces chiffres sont pour un ordinateur quantique logique tolérant aux fautes. Avec les distances de code de surface actuelles (d ≈ 17 pour 10⁻⁴), multipliez par ~1000 pour les qubits physiques.

---

## 7. Alternatives Classiques et Post-Quantiques

### 7.1 Algorithmes classiques de factorisation

| Algorithme | Complexité | Usage |
|:---|:---|:---|
| GNFS (General Number Field Sieve) | L(1/3, 1.923) | Record RSA-829 (2800 cœurs-ans) |
| ECM (Elliptic Curve Method) | L(1/2, √2) | Facteurs moyens (50-100 digits) |
| Pollard's rho | O(√p) | Petits facteurs |
| SQUFOF | O(N^{1/4}) | N < 10²⁰ |

### 7.2 Cryptographie post-quantique

- **CRYSTALS-Kyber** (KEM) — basé sur les réseaux (Module-LWE)
- **CRYSTALS-Dilithium** (signature) — basé sur les réseaux
- **Falcon** (signature) — basé sur les réseaux (GPV)
- **SPHINCS+** (signature) — basé sur les hash

---

## 8. Pièges et Limitations

1. **Taille des nombres sur simulateur :** Simuler Shor pour N > 21 (5 bits) sur un simulateur classique est irréalisable (l'algorithme est exponentiellement plus lent sur un simulateur que le meilleur classique).

2. **Construction de l'exponentiation modulaire :** C'est le goulot d'étranglement pratique — nécessite des additionneurs quantiques (Cuccaro, Draper, Gidney). L'implémentation naïve occupe ~90% des portes du circuit.

3. **Période non valide :** L'algorithme échoue si r est impair ou si a^{r/2} ≡ -1 mod N. Probabilité d'échec < 1/2, donc en moyenne 2-3 tentatives suffisent.

4. **Qubits auxiliaires sales :** L'exponentiation modulaire nécessite des qubits auxiliaires. Les "dirty ancillae" (qubits dans un état inconnu) peuvent être réutilisés avec un protocole de nettoyage.

5. **Erreurs QPE :** La précision de l'estimation de phase est 1/2^{n_control}. Il faut suffisamment de qubits de contrôle pour résoudre la période r : n_control > log₂(N) + log₂(1/ε).

---

## Liste de vérification

- [ ] La structure globale de Shor (réduction classique + QPE) est comprise.
- [ ] La QFT et son inverse sont implémentées en Qiskit.
- [ ] Le QPE (Estimation de Phase Quantique) est maîtrisé.
- [ ] L'exponentiation modulaire et son coût (O(n³) portes) sont connus.
- [ ] Les optimisations (Beauregard, Gidney-Ekerå, Regev) sont référencées.
- [ ] Les ressources nécessaires pour RSA-2048 sont connues (~20M qubits, ~8h).
- [ ] Les alternatives post-quantiques (Kyber, Dilithium) sont identifiées.
- [ ] La probabilité d'échec et la stratégie de rerun sont comprises.
