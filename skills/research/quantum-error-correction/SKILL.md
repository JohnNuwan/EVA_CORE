---
name: quantum-error-correction
description: "Codes correcteurs quantiques : codes de surface, formalisme des stabilisateurs, code de Shor, Steane, Bacon-Shor, seuil de tolérance aux fautes, décodage par Maximum Likelihood et Minimum Weight Perfect Matching."
version: 1.0.0
author: EVA
license: Privée EVA
metadata:
  EVA:
    tags: [quantum, error-correction, qec, surface-code, stabilizer, fault-tolerance, syndrome, MWPM]
    related_skills: [quantum-gates, quantum-computing-fundamentals, qiskit-programming]
platforms: [linux, macos, windows]
---

# Correction d'Erreur Quantique

## Vue d'ensemble

La **correction d'erreur quantique (QEC)** est essentielle pour construire un ordinateur quantique tolérant aux fautes (FTQC). Sans elle, le bruit et la décohérence limitent les calculs à quelques centaines de portes. Cette compétence couvre le formalisme des **stabilisateurs**, les **codes de surface** (standard actuel), le code de Shor, le code de Steane, le code de Bacon-Shor, les limites de seuil, le **décodage** (MWPM, Union-Find, Maximum Likelihood), les architectures tolérantes aux fautes, et l'estimation des ressources pour FTQC.

## Quand l'utiliser

- Concevoir ou analyser un schéma de correction d'erreur quantique.
- Implémenter un décodeur de code de surface (MWPM, Union-Find).
- Estimer le nombre de qubits physiques nécessaires pour un qubit logique de fidélité donnée.
- Analyser le seuil de tolérance aux fautes d'un code ou d'une architecture.
- Comprendre le formalisme des stabilisateurs et son application.

---

## 1. Formalisme des Stabilisateurs

### 1.1 Groupe de Stabilisation

Un code correcteur quantique [[n, k, d]] est défini par un groupe de stabilisateurs S ⊂ Pₙ (groupe de Pauli sur n qubits).

Propriétés :
- S est abélien : ∀ s₁, s₂ ∈ S, [s₁, s₂] = 0
- -I ∉ S
- |S| = 2^{n-k} (n-k générateurs indépendants)
- Code space : {|ψ⟩ | s|ψ⟩ = |ψ⟩ ∀ s ∈ S}

```python
import numpy as np

class StabilizerCode:
    """Code correcteur quantique basé sur les stabilisateurs."""
    
    def __init__(self, n: int, k: int, generators: list):
        """
        Args:
            n : nombre de qubits physiques
            k : nombre de qubits logiques
            generators : liste des générateurs (matrices de Pauli n-qubits)
        """
        self.n = n
        self.k = k
        self.generators = generators
        self.distance = None  # À calculer
        
    def compute_syndrome(self, error: np.ndarray) -> list:
        """Calcule le syndrome pour une erreur donnée.
        
        Syndrome = [s₁·error, s₂·error, ...] où s·e = 0 si commute, 1 si anticommute.
        """
        syndrome = []
        for gen in self.generators:
            # Commutation : s·e = 0 si commute, 1 si anticommute
            commute = self.check_commutation(gen, error)
            syndrome.append(commute)
        return syndrome
    
    def check_commutation(self, a: np.ndarray, b: np.ndarray) -> int:
        """Vérifie si deux éléments du groupe de Pauli commutent.
        
        0 = commute, 1 = anticommute.
        """
        phase = 0
        for i in range(len(a)):
            # Pour des matrices Pauli sur le qubit i
            # Table de commutation : I tout commute, X↔Z anticommutent
            if a[i] != 'I' and b[i] != 'I' and a[i] != b[i]:
                phase += 1
        return phase % 2
```

### 1.2 Représentation Binaire

Un élément P ∈ Pₙ peut être représenté par deux vecteurs binaires (v_z, v_x) ∈ 𝔽₂²ⁿ :

```
P ∝ i^c Πⱼ (Z)^{v_z[j]} (X)^{v_x[j]}
```

```python
def pauli_to_binary(op: str) -> tuple:
    """Convertit une chaîne Pauli en représentation binaire (v_z, v_x).
    
    Ex: 'XZ' → ([0,1], [1,0])
         'IY' → ([1,1], [1,0])  car Y = iXZ
    """
    n = len(op)
    v_z = np.zeros(n, dtype=int)
    v_x = np.zeros(n, dtype=int)
    
    for i, p in enumerate(op):
        if p == 'X':
            v_x[i] = 1
        elif p == 'Z':
            v_z[i] = 1
        elif p == 'Y':
            v_z[i] = 1
            v_x[i] = 1
    
    return v_z, v_x

def check_commutation_binary(vz1, vx1, vz2, vx2) -> int:
    """Test de commutation en représentation binaire."""
    return (vz1 @ vx2 + vx1 @ vz2) % 2
```

---

## 2. Codes Correcteurs Classiques

### 2.1 Code de Shor [[9,1,3]]

Premier code correcteur quantique : combine des répétitions de bits et de phase.

```
Protège contre 1 erreur X et 1 erreur Z (arbitraire sur 1 qubit).
Distance : d = 3 (corrige ⌊(d-1)/2⌋ = 1 erreur).
```

### 2.2 Code de Steane [[7,1,3]]

Basé sur le code classique de Hamming [7,4,3].

```
Générateurs :
g₁ = IIIXXXX
g₂ = IXXIIXX
g₃ = XIXIXIX
g₄ = IIIZZZZ
g₅ = IZZIIZZ
g₆ = ZIZIZIZ
```

```python
steane_generators = [
    'IIIXXXX', 'IXXIIXX', 'XIXIXIX',  # Stabilisateurs X
    'IIIZZZZ', 'IZZIIZZ', 'ZIZIZIZ'   # Stabilisateurs Z
]
```

### 2.3 Code de Bacon-Shor [[n², 1, n]]

Code avec sous-système (gabarit) : les qubits sont organisés en grille n×n, avec des stabilisateurs sur les lignes et colonnes.

```
Avantage : mesure de syndrome uniquement 2-locale (pas de portes 4-qubits).
Inconvénient : distance = n (plus petit que le code de surface à taille égale).
```

---

## 3. Codes de Surface (Surface Codes)

### 3.1 Architecture

Le **code de surface** (Kitaev, 1997) est le code QEC dominant aujourd'hui (Google, IBM utilisent des variantes).

- Qubits de données sur les sommets d'une grille
- Qubits de mesure (ancilla) sur les faces (plaquettes)
- Stabilisateurs : plaquettes X et Z alternées

```
Grille d = 5 (distance 5) :
•—X—•—X—•—X—•—X—•
Z   Z   Z   Z   Z
•—X—•—X—•—X—•—X—•
Z   Z   Z   Z   Z
•—X—•—X—•—X—•—X—•
Z   Z   Z   Z   Z
•—X—•—X—•—X—•—X—•
Z   Z   Z   Z   Z
•—X—•—X—•—X—•—X—•

• = qubit de donnée, X/Z = qubit de mesure (type X/Z)
```

```python
class SurfaceCode:
    """Code de surface planaire."""
    
    def __init__(self, distance: int):
        """
        Args:
            distance : distance du code (d = 2L+1 pour une grille L×L)
        """
        self.d = distance
        self.L = (distance - 1) // 2  # Taille interne
        self.n_data = distance**2
        self.n_x_meas = self.L * (self.L + 1)  # Plaquettes X
        self.n_z_meas = self.L * (self.L + 1)  # Plaquettes Z
        self.n_total = self.n_data + self.n_x_meas + self.n_z_meas
        
    def plaquette_operators(self) -> tuple:
        """Génère les opérateurs de plaquette X et Z.
        
        Returns:
            (plaquettes_X, plaquettes_Z) : listes de listes d'indices
        """
        plaq_x = []
        plaq_z = []
        
        for i in range(self.L):
            for j in range(self.L):
                # Plaquette Z : autour d'un sommet intérieur
                # (i,j), (i,j+1), (i+1,j), (i+1,j+1)
                plaq_z.append([
                    i * self.d + j, 
                    i * self.d + j + 1,
                    (i+1) * self.d + j,
                    (i+1) * self.d + j + 1
                ])
                
                # Plaquette X : centrée entre 4 données
                plaq_x.append([
                    i * self.d + j + self.L,
                    (i+1) * self.d + j + self.L,
                    # ...
                ])
        
        return plaq_x, plaq_z
```

### 3.2 Seuil de Tolérance aux Fautes

| Code | Type | Seuil (est.) | Taux d'erreur corrigé | Réf. |
|:---|:---|:---|:---|:---|
| **Surface** | Toric/planaire | ~1-1.5% | Toute erreur < seuil | Fowler, 2012 |
| **Color** | 2D triangulaire | ~0.1% | Erreurs corrélées | Landahl, 2011 |
| **LDPC quantique** | Hypergraphe | ~0.5-1% | Avantage en taux | Gottesman, 2013 |
| **Concatené** | Steane × Steane | ~10⁻⁴ | Faible taux erreur | Knill, 2005 |

### 3.3 Distance et Réduction d'Erreur

Pour un code de surface de distance d :
- Corrige ⌊(d-1)/2⌋ erreurs
- Taux d'erreur logique : p_L ∝ (p/p_th)^{(d+1)/2}

```python
def logical_error_rate(p_phys: float, d: int, p_th: float = 0.01) -> float:
    """Estime le taux d'erreur logique pour un code de surface.
    
    Modèle standard : p_L ≈ C (p/p_th)^{(d+1)/2}
    """
    C = 0.1  # Facteur pré-exponentiel (empirique)
    return C * (p_phys / p_th)**((d + 1) / 2)

def required_distance(p_phys: float, target_pL: float, p_th: float = 0.01) -> int:
    """Calcule la distance de code nécessaire pour atteindre un taux d'erreur logique cible."""
    C = 0.1
    ratio = target_pL / C
    d_min = 2 * np.log(ratio) / np.log(p_phys / p_th) - 1
    d = int(np.ceil(d_min))
    if d % 2 == 0:
        d += 1  # Distance impaire pour les codes de surface
    return max(d, 3)
```

---

## 4. Décodage des Codes de Surface

### 4.1 Décodage MWPM (Minimum Weight Perfect Matching)

Algorithme standard : les syndromes sont des "défauts" qui s'annihilent par paires. Le meilleur appariement minimise la somme des poids (distances de Manhattan).

```python
import networkx as nx
from typing import List, Tuple

class SurfaceDecoder:
    """Décodeur MWPM pour code de surface."""
    
    def __init__(self, distance: int):
        self.d = distance
        self.L = (distance - 1) // 2
        
    def decode(self, syndrome: np.ndarray) -> List[Tuple[int, int]]:
        """Décode un syndrome et retourne les corrections à appliquer.
        
        Algorithme :
        1. Identifier les défauts (syndrome = 1)
        2. Construire un graphe complet des distances entre défauts
        3. Minimum Weight Perfect Matching (blossom algorithm)
        4. Retourner les corrections
        """
        # Indices des défauts
        defects = np.where(syndrome == 1)[0]
        
        if len(defects) == 0:
            return []  # Pas d'erreur détectée
        
        if len(defects) % 2 != 0:
            # Nombre impair → ajouter une frontière virtuelle
            defects = np.append(defects, -1)  # -1 = frontière
        
        # Graphe complet des défauts
        G = nx.Graph()
        for i in range(len(defects)):
            for j in range(i+1, len(defects)):
                if defects[i] >= 0 and defects[j] >= 0:
                    # Distance de Manhattan sur la grille
                    d = self._manhattan_distance(defects[i], defects[j])
                    G.add_edge(i, j, weight=d)
                elif defects[i] >= 0 or defects[j] >= 0:
                    # Distance à la frontière
                    real = max(defects[i], defects[j])
                    d = self._border_distance(real)
                    G.add_edge(i, j, weight=d)
        
        # MWPM via algorithme de blossom (Edmonds)
        matching = nx.max_weight_matching(G, maxcardinality=True, weight='weight')
        
        # Convertir matching en corrections
        corrections = []
        for u, v in matching:
            if defects[u] >= 0 and defects[v] >= 0:
                corrections.append((defects[u], defects[v]))
        
        return corrections
    
    def _manhattan_distance(self, i: int, j: int) -> int:
        """Distance de Manhattan entre deux défauts sur la grille."""
        xi, yi = i // (2*self.L+1), i % (2*self.L+1)
        xj, yj = j // (2*self.L+1), j % (2*self.L+1)
        return abs(xi - xj) + abs(yi - yj)
    
    def _border_distance(self, i: int) -> int:
        """Distance minimale du défaut à la frontière."""
        x, y = i // (2*self.L+1), i % (2*self.L+1)
        return min(x, y, 2*self.L - x, 2*self.L - y)
```

### 4.2 Union-Find Decoder

Alternative plus rapide à MWPM (O(n α(n)) vs O(n³)) avec qualité de décodage comparable pour les codes de surface.

```python
class UnionFindDecoder:
    """Décodeur Union-Find pour code de surface.
    
    Complexité : O(n α(n)) où α(n) est l'inverse d'Ackermann.
    Seuil : ~0.9% (vs ~1% pour MWPM).
    """
    
    def __init__(self, distance: int):
        self.d = distance
        self.parent = {}
        self.size = {}
    
    def find(self, x: int) -> int:
        """Find avec compression de chemin."""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int):
        """Union par rang."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return
        if self.size[rx] < self.size[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx
        self.size[rx] += self.size[ry]
    
    def decode(self, syndrome: np.ndarray) -> list:
        """Décodage Union-Find."""
        # Phase 1 : clustering des défauts
        defects = np.where(syndrome == 1)[0]
        for d in defects:
            if d not in self.parent:
                self.parent[d] = d
                self.size[d] = 0
        
        # ... (implémentation complète dans la littérature)
        return []
```

### 4.3 Décodage par Réseau de Neurones

```python
import torch
import torch.nn as nn

class NeuralDecoder(nn.Module):
    """Décodeur par réseau de neurones pour code de surface 5×5."""
    
    def __init__(self, d: int):
        super().__init__()
        self.d = d
        self.n_plaquettes = 2 * d * (d - 1)
        
        self.conv1 = nn.Conv2d(2, 16, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(16, 32, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(32, 1, kernel_size=3, padding=1)
        
    def forward(self, syndrome: torch.Tensor) -> torch.Tensor:
        """Entrée : syndrome shape (batch, 2, d, d-1).
        Sortie : corrections shape (batch, 1, d, d).
        """
        x = torch.relu(self.conv1(syndrome))
        x = torch.relu(self.conv2(x))
        return torch.sigmoid(self.conv3(x))
```

---

## 5. Tolérance aux Fautes (FTQC)

### 5.1 Portes Logiques Transversales

Une porte logique est **transversale** si elle agit qubit par qubit sur le code :
```
Ū|ψ⟩_L = (U ⊗ U ⊗ ... ⊗ U)|ψ⟩_L
```

Portes transversales pour le code de surface :
- CNOT : transversal ✓
- H : transversal ✓
- S : transversal (code torique) ✓
- **T : PAS transversal** ✗

### 5.2 Consommation d'État Magique (T-gate)

Puisque T n'est pas transversale, on utilise des **états magiques** (|A⟩ = |0⟩ + e^{iπ/4}|1⟩).

```python
def magic_state_factory(physical_error_rate: float, target_fidelity: float) -> dict:
    """Estime les ressources pour une factory d'états magiques.
    
    Le processus de distillation (Bravyi-Kitaev) produit un état 
    magique à haute fidélité à partir de 15 états bruyants.
    """
    # Erreur par distillation
    p_out = 35 * p_in**3  # 15→1 Bravyi-Kitaev
    n_levels = int(np.ceil(np.log(target_fidelity / physical_error_rate) / np.log(35)))
    
    return {
        'physical_error_rate': physical_error_rate,
        'n_levels': n_levels,
        'n_magic_states_per_shot': 15**n_levels,
        'n_qubits_per_factory': 15**n_levels * 10,  # Estimation
        'area_overhead': f"{15**n_levels}x le qubit logique"
    }
```

### 5.3 Estimation des Ressources FTQC

```python
def ftqc_resources(n_logical_qubits: int, error_rate: float, 
                   target_error: float = 1e-12) -> dict:
    """Estime les ressources physiques pour FTQC.
    
    Args:
        n_logical_qubits : nombre de qubits logiques
        error_rate : taux d'erreur physique par porte
        target_error : taux d'erreur logique cible
    
    Returns:
        Dict avec qubits physiques, qubits totaux, overhead
    """
    d = required_distance(error_rate, target_error)
    
    # Code de surface : (2d+1)² = (2d-1)² qubits physiques par qubit logique
    n_physical_per_logical = (2 * d - 1)**2
    
    # Overhead supplémentaire pour les portes T :
    # ~50% en plus pour les magic state factories
    n_total_physical = n_logical_qubits * n_physical_per_logical * 1.5
    
    return {
        'distance': d,
        'qubits_physiques_par_logique': n_physical_per_logical,
        'qubits_physiques_totaux': int(n_total_physical),
        'overhead_n_qubits': n_total_physical / n_logical_qubits,
        'taux_erreur_logique': logical_error_rate(error_rate, d)
    }

# Exemple : 100 qubits logiques avec erreur physique 10⁻³
resources = ftqc_resources(100, 1e-3)
print(f"Distance : d={resources['distance']}")
print(f"Qubits physiques totaux : {resources['qubits_physiques_totaux']:,}")
```

---

## 6. Pièges et Limitations

1. **Seuil vs pratique :** Le seuil théorique de ~1% pour les codes de surface suppose un bruit indépendant. En pratique, le bruit est corrélé (cross-talk, fuite) → seuil réel ~0.5%.

2. **Coût des T-gates :** Chaque T-gate logique nécessite une distillation d'état magique qui occupe ~10-100× l'espace d'un qubit logique. Pour Shor, ~90% des ressources sont dans les T-gates.

3. **Mesure de syndrome :** La mesure des plaquettes nécessite des portes CNOT — ces mesures sont elles-mêmes bruitées. Un cycle de syndrome dure ~1µs (qubit supra).

4. **Fatigue des qubits :** Les qubits subissent un stress répété lors des mesures de syndrome. Au-delà de ~10¹² cycles, certains qubits dérivent et doivent être recalibrés.

5. **Fuites de population (leakage) :** Les qubits supraconducteurs peuvent passer hors de l'espace computationnel (|2⟩, |3⟩). Le leakage nécessite un vidage périodique (leakage reduction unit).

---

## Liste de vérification

- [ ] Le formalisme des stabilisateurs (groupe, syndrome, code space) est maîtrisé.
- [ ] Les codes de Shor [[9,1,3]] et Steane [[7,1,3]] sont connus.
- [ ] La structure du code de surface (plaquettes X et Z) est comprise.
- [ ] Le décodage MWPM avec l'algorithme de blossom est implémentable.
- [ ] Le calcul de distance nécessaire pour un taux d'erreur cible est maîtrisé.
- [ ] Les portes logiques transversales (CNOT, H, S) sont connues.
- [ ] Le processus de distillation des états magiques est compris.
- [ ] L'estimation des ressources FTQC (qubits physiques par logique) est fiable.
