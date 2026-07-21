---
name: cryptographic-protocols
description: Guide complet des protocoles cryptographiques avancés — Secret Sharing (Shamir, additive), MPC (Garbled Circuits, SPDZ, ABY), Oblivious Transfer, Homomorphic Encryption (BFV, CKKS, TFHE), VDF, et applications.
category: cybersecurite
tags: [mpc, secret-sharing, garbled-circuits, homomorphic-encryption, oblivious-transfer, vdf, cryptography, protocols]
---

# Protocoles Cryptographiques Avancés — Guide Approfondi

## Sommaire
1. [Secret Sharing (Partage de Secret)](#secret-sharing)
2. [Oblivious Transfer (Transfert Aveugle)](#oblivious-transfer)
3. [Garbled Circuits (Yao's Protocol)](#garbled-circuits)
4. [Secure Multi-Party Computation (MPC)](#mpc)
5. [SPDZ et ABY Frameworks](#spdz-et-aby)
6. [Homomorphic Encryption (Chiffrement Homomorphe)](#homomorphic-encryption)
7. [BFV, CKKS, TFHE — Comparaison](#bfv-ckks-tfhe)
8. [Verifiable Delay Functions (VDF)](#vdf)
9. [Applications et Implémentations](#applications)

---

## 1. Secret Sharing (Partage de Secret)

### 1.1 Shamir's Secret Sharing (SSS)

**Principe** : diviser un secret S en n parts, où k parts (threshold) suffisent pour le reconstruire.

**Fondement** : un polynôme de degré k-1 est déterminé de façon unique par k points.

```python
import random
from functools import reduce

def shamir_share(secret: int, n: int, k: int, prime: int) -> list:
    """
    Partage le secret en n parts.
    k parts suffisent pour reconstruire.
    """
    # 1. Générer un polynôme aléatoire P(x) = a₀ + a₁·x + ... + a_{k-1}·x^{k-1}
    #    avec a₀ = secret
    coeffs = [secret] + [random.randint(1, prime-1) for _ in range(k-1)]
    
    # 2. Évaluer le polynôme en n points non-nuls
    shares = []
    for i in range(1, n + 1):
        x = i
        y = 0
        for power, coef in enumerate(coeffs):
            y = (y + coef * pow(x, power, prime)) % prime
        shares.append((x, y))
    
    return shares

def shamir_reconstruct(shares: list, prime: int) -> int:
    """
    Reconstruit le secret depuis k parts via l'interpolation de Lagrange.
    """
    def lagrange_basis(x, i, xs):
        """Calcule L_i(0) = ∏_{j≠i} (0 - x_j) / (x_i - x_j)"""
        num = 1
        den = 1
        for j, x_j in enumerate(xs):
            if j != i:
                num = (num * (0 - x_j)) % prime
                den = (den * (x_i - x_j)) % prime
        return num * pow(den, -1, prime) % prime
    
    xs = [s[0] for s in shares]
    ys = [s[1] for s in shares]
    
    result = 0
    for i, (x_i, y_i) in enumerate(shares):
        result = (result + y_i * lagrange_basis(x, i, xs)) % prime
    
    return result
```

### 1.2 Additive Secret Sharing

Plus simple : `S = S₁ + S₂ + ... + Sₙ mod p`

```python
def additive_share(secret: int, n: int, prime: int) -> list:
    """Partage additif : S = ∑ S_i mod p"""
    shares = [random.randint(0, prime-1) for _ in range(n-1)]
    # La dernière part assure la somme
    shares.append((secret - sum(shares)) % prime)
    return shares

# Reconstruire : il faut TOUTES les parts
def additive_reconstruct(shares: list, prime: int) -> int:
    return sum(shares) % prime
```

### 1.3 VSS (Verifiable Secret Sharing)

Le VSS permet aux participants de vérifier que leur part est correcte :

```python
def vss_share(secret, n, k, prime, G):
    """
    Partage vérifiable : chaque participant peut vérifier sa part
    sans connaître les parts des autres.
    """
    # Phase 1 : comme Shamir
    shares, coeffs = shamir_share_with_coeffs(secret, n, k, prime)
    
    # Phase 2 : engagements aux coefficients
    # Chaque participant reçoit sa part (x_i, y_i) + les engagements
    commitments = {i: coeffs[i] * G for i in range(k)}  # Points sur courbe
    
    # Phase 3 : vérification individuelle
    # participant i vérifie : y_i·G = ∑_{j=0}^{k-1} C_j · x_i^j
    def verify_share(x_i, y_i, commitments, G):
        lhs = y_i * G
        rhs = sum(c_j * pow(x_i, j) for j, c_j in enumerate(commitments))
        return lhs == rhs
    
    return shares, commitments
```

---

## 2. Oblivious Transfer (Transfert Aveugle)

### 2.1 Principe

```
Alice a deux messages : m₀, m₁
Bob choisit un bit b ∈ {0, 1}

OT : Bob reçoit m_b sans qu'Alice sache quel message il a choisi
     Bob n'apprend rien sur m_{1-b}
```

### 2.2 1-out-of-2 OT (Naor-Pinkas)

```python
def ot_send(m0: bytes, m1: bytes, curve, G):
    """
    Alice : génère une clé publique et envoie deux ciphertexts
    """
    from secrets import randbelow
    n = curve.order
    
    # Génération de la paire de clés
    a = randbelow(n)
    A = a * G  # Clé publique
    
    # Envoie A à Bob

def ot_receive(b: int, A, curve, G, pk_enc):
    """
    Bob : choisit b et reçoit m_b
    """
    n = curve.order
    k = randbelow(n)
    
    if b == 0:
        # Bob envoie B = k·G
        B = k * G
        # La clé dérivée est k·A
        shared = k * A
    else:
        # Bob envoie B = A + k·G → masqué
        B = A + k * G
        # La clé dérivée est k·A - a·k·G ??? Correction :
        # shared = B - a·G = A + k·G - a·G = ... non
        # En réalité : shared = k·A (les deux cas utilisent k·A)
        pass
    
    # Le protocole correct utilise la paire (pk, sk) d'Alice
    # pour générer une base (R_0, R_1)
    return shared  # H(shared) ⊕ ciphertext
```

### 2.3 OT Extension (IKNP)

Permet de calculer des millions d'OT depuis très peu d'OT de base :

```python
def ot_extension(base_ots, messages_matrix, choices):
    """Extension OT : de κ OT de base vers n OT actifs"""
    # Avec κ=128 OT de base, on peut générer 2²⁰ OT
    # Ishai, Kilian, Nissim, Petrank (2003)
    
    # Matrice de corrélation
    # Bob envoie une matrice M de taille (κ × n)
    # Alice reçoit M_i si le choix est correct
    
    # Gain : chaque OT de base génère ~O(n/κ) OT
    pass
```

---

## 3. Garbled Circuits (Yao's Protocol)

### 3.1 Principe

Protocole de Yao (1986) : deux parties calculent une fonction sur leurs entrées privées.

```
Alice : construit le circuit chiffré (garbled circuit)
Bob : évalue le circuit chiffré

Alice ne connaît que la fonction et sa propre entrée
Bob apprend le résultat de la fonction
```

### 3.2 Construction d'une porte ET (AND)

```python
import hashlib
from secrets import randbits

# Chaque fil a deux étiquettes (labels) : 0 et 1
# Une étiquette est une clé AES de 128 bits

def garble_gate(gate_type, labels_a, labels_b):
    """
    Chiffre une porte logique avec les 4 combinaisons d'entrée.
    labels_a = (label_a0, label_a1)
    labels_b = (label_b0, label_b1)
    """
    truth_table = {
        'AND': [(0,0,0), (0,1,0), (1,0,0), (1,1,1)],
        'XOR': [(0,0,0), (0,1,1), (1,0,1), (1,1,0)],
        'OR':  [(0,0,0), (0,1,1), (1,0,1), (1,1,1)],
    }
    
    garbled = []
    for a, b, out in truth_table[gate_type]:
        # Chiffrer l'étiquette de sortie avec les étiquettes d'entrée
        input_key = labels_a[a] + labels_b[b]
        label_out = generate_label()  # 128 bits aléatoires
        
        # Double chiffrement
        ciphertext = double_encrypt(input_key, label_out)
        garbled.append(ciphertext)
    
    # Mélanger les 4 entrées
    random.shuffle(garbled)
    return garbled

def evaluate_gate(garbled, label_a, label_b):
    """Évalue une porte chiffrée avec les étiquettes réelles"""
    for entry in garbled:
        # Essayer de déchiffrer avec (label_a + label_b)
        result = try_decrypt(label_a + label_b, entry)
        if result is not None:
            return result
    return None
```

### 3.3 Point-and-Permute

Optimisation : chaque étiquette a un **pointeur** (2 bits de permutation) pour identifier la ligne correcte sans essayer les 4.

```python
def garble_gate_optimized(gate_type, labels_a, labels_b):
    """Avec point-and-permute : chaque ligne a un indice de permutation"""
    garbled_table = {}
    for a, b, out in truth_table[gate_type]:
        # Les étiquettes ont leur bit de permutation dans le LSB
        perm_a = labels_a[a] & 1
        perm_b = labels_b[b] & 1
        index = (perm_a << 1) | perm_b
        
        label_out = generate_label()
        label_out_with_perm = label_out | (randbits(1))  # Permutation sortie
        
        input_key_h = hash_labels(labels_a[a], labels_b[b])
        ciphertext = encrypt(input_key_h, label_out_with_perm)
        
        garbled_table[index] = ciphertext
    
    return garbled_table
```

### 3.4 Free XOR (Kolesnikov-Schneider)

Les portes XOR ne nécessitent aucun chiffrement :

```python
# Free XOR : si toutes les étiquettes sont liées par un delta R
# label_1 = label_0 ⊕ R  (pour chaque fil)
# XOR gate : output = label_a ⊕ label_b ⊕ R
# Aucun ciphertext nécessaire !
```

---

## 4. Secure Multi-Party Computation (MPC)

### 4.1 Architecture Générale

```python
# MPC : N parties calculent f(x₁, x₂, ..., x_N)
# où x_i est la donnée privée de la partie i
# Les parties apprennent le résultat, rien d'autre

# Représentation du secret : partagé (shares)
# Les calculs sont faits sur des shares

# Exemple : N=2, P₁ a x₁, P₂ a x₂
# On veut calculer x₁ + x₂ (additif)
# Sans qu'aucune partie ne voie la valeur de l'autre
```

### 4.2 Protocole de Somme Sécurisé (N parties)

```python
def secure_sum(parties_values, network):
    """
    Chaque partie i :
    1. Génère des parts aléatoires r_{i→j} pour chaque partie j ≠ i
    2. Garde localement sa contribution
    3. Envoie r_{i→j} à chaque partie j
    4. Recoit r_{j→i} de chaque partie j
    5. Somme locale : v_i + ∑(r_{i→j}) - ∑(r_{j→i})
    6. Toutes les parties envoient leur somme locale → résultat final
    """
    n = len(network)
    shares_sent = [random.randint(0, 2**64) for _ in range(n)]
    
    # Chaque partie calcule sa contribution masquée
    local_share = network.my_value + sum(shares_sent)
    
    # Envoie des parts aux autres
    for peer in network.peers:
        peer.receive_share(shares_sent[peer.id])
        local_share -= peer.send_share()  # Reçu de ce peer
    
    # Diffusion de la somme locale
    all_shares = network.broadcast_and_collect(local_share)
    
    return sum(all_shares) % (2**64)
```

---

## 5. SPDZ et ABY Frameworks

### 5.1 SPDZ (Keller et al.)

Framework MPC avec **preprocessing** (triples de multiplication) :

```python
# Phase 1 (Offline) : génération de triples de multiplication
# (a, b, c) où c = a·b sur des shares

def generate_multiplication_triple(n_parties, field_size):
    """
    Génère un triple de multiplication SPDZ.
    a, b sont aléatoires, c = a·b (shares additifs)
    """
    # Chaque partie génère ses parts de a, b
    a_shares = additive_share(random.random(), n_parties, field_size)
    b_shares = additive_share(random.random(), n_parties, field_size)
    
    # Calcul sécurisé de c = a·b
    c_shares = mpc_mul_additive(a_shares, b_shares)
    
    return a_shares, b_shares, c_shares

# Phase 2 (Online) : utilisation des triples
def mpc_multiply(x_shares, y_shares, triple_shares):
    """
    Multiplication sécurisée de x et y en utilisant un triple.
    Coût : 2 Reveal (broadcast) + 1 multiplication locale
    """
    # Chaque partie calcule localement :
    delta_i = x_i - a_i  # a_i est sa part du triple
    epsilon_i = y_i - b_i
    
    # Reveal de delta et epsilon
    delta = reconstruct(delta_shares)
    epsilon = reconstruct(epsilon_shares)
    
    # Calcul du produit
    z_i = c_i + delta * y_i + epsilon * x_i - delta * epsilon
    
    return z_shares
```

### 5.2 ABY Framework

**Mixed-Protocol** : combine **A**rithmetic + **B**oolean + **Y**ao (Garbled Circuits).

```python
class ABYFramework:
    """
    ABY : trois types de partages :
    - Arithmetic Sharing (somme additive, efficace pour +, *)
    - Boolean Sharing (XOR sharing, efficace pour XOR, AND)
    - Yao Sharing (Garbled Circuits, efficace pour les comparaisons)
    """
    
    # Conversion entre partages (coût élevé)
    def arithmetic_to_boolean(self, a_share):
        """Conversion de partage arithmétique → booléen"""
        pass
    
    def boolean_to_yao(self, b_share):
        """Conversion de partage booléen → Yao (garbled)"""
        pass
```

---

## 6. Homomorphic Encryption (Chiffrement Homomorphe)

### 6.1 Principe

Un chiffrement est **homomorphe** s'il permet d'effectuer des opérations sur les données chiffrées.

```
E(a) ⊕ E(b) = E(a + b)     Additive
E(a) ⊗ E(b) = E(a × b)     Multiplicative
```

Générations :
- **Partially HE (PHE)** : addition ou multiplication (Pailier, ElGamal)
- **Somewhat HE (SHE)** : quelques additions et multiplications
- **Fully HE (FHE)** : un nombre illimité d'opérations (Gentry, 2009)

### 6.2 Algorithme de Gentry (2009)

**Premier FHE** basé sur les réseaux idéaux :

```python
# Bootstrap (Gentry) : réduire le bruit dans le ciphertext
# En déchiffrant le ciphertext... chiffré (encrypted decryption)
# Refresh le ciphertext sans révéler le plaintext

# Le défi : le bruit croît avec chaque multiplication
# Bootstrap = exécuter le circuit de déchiffrement FHE
# pour "rafraîchir" le ciphertext

# Complexité : le bootstrap coûte ~O(λ⁶) → très lent
```

### 6.3 Leveled HE (sans bootstrap)

Plus efficace que FHE complet, mais avec un nombre limité de multiplications :

```python
# Leveled HE = paramètres de sécurité plus larges
# pour supporter L multiplications sans bootstrap
# Taille du ciphertext : O(λ·L) (croît avec la profondeur du circuit)
```

---

## 7. BFV, CKKS, TFHE — Comparaison

### 7.1 BFV (Brakerski-Fan-Vercauteren)

Chiffrement homomorphe pour les entiers modulo t.

```python
# BFV sur le problème Ring-LWE
# Plaintext : Z_t (arithmétique modulaire exacte)
# Utile pour : circuits arithmétiques exacts

# Paramètres typiques pour 128 bits de sécurité :
# n = 4096 (degré polynomial)
# t = 65537 (plaintext modulus)
# q ~ 2⁶⁰ (ciphertext modulus)

# Multiplication BFV : bruit O(t·B·∥c₁∥·∥c₂∥)
# Relinéarisation : réduit le ciphertext de 3 à 2 éléments
```

### 7.2 CKKS (Cheon-Kim-Kim-Song)

Chiffrement homomorphe pour les nombres à virgule flottante.

```python
# CKKS supporte les approximations arithmétiques
# Plaintext : C^N/2 (nombres complexes, flottants)
# Utile pour : machine learning, inference

# Scaling : les entrées sont mises à l'échelle par Δ
# Rescaling : réduction du facteur d'échelle après multiplication
# Perte de précision contrôlée

# Paramètres typiques :
# n = 16384, log₂(q) = 600, levels = 10-20 multiplications

import tenseal as ts

# Chiffrement CKKS
context = ts.context(
    ts.SCHEME_TYPE.CKKS,
    poly_modulus_degree=16384,
    coeff_mod_bit_sizes=[60, 40, 40, 60]
)
context.generate_galois_keys()
secret_key = context.secret_key()

# Calcul sur données chiffrées
enc_v1 = ts.ckks_vector(context, [1.0, 2.0, 3.0])
enc_v2 = ts.ckks_vector(context, [4.0, 5.0, 6.0])

result = enc_v1 + enc_v2           # Addition
result = (enc_v1 * enc_v2) * 2    # Multiplication + scaling

# Déchiffrement
decrypted = result.decrypt()
```

### 7.3 TFHE (Chillotti et al.)

Chiffrement homomorphe pour les circuits booléens — **le plus rapide** en pratique.

```python
# TFHE : supporte les portes logiques en 13ms par gate
# Bootstrapping très rapide (< 0.1s)
# Plaintext : Z_2 (bits)

# Programme en TFHE :
# 1. Chiffrer les bits d'entrée
# 2. Évaluer un circuit booléen complet
# 3. Déchiffrer la sortie

import tfhe

# Chiffrement de bits
params = tfhe.Parameters(128)
key = tfhe.SecretKey(params)
ct = key.encrypt(1)  # Chiffrement d'un bit

# Évaluation de circuits (portes logiques)
not_ct = tfhe.NOT(ct)
and_ct = tfhe.AND(ct, not_ct)
xor_ct = tfhe.XOR(ct, tfhe.encrypt_0(params))
```

### 7.4 Comparaison

| Critère | BFV | CKKS | TFHE |
|---------|-----|------|------|
| Plaintext | Entiers Z_t | Flottants approx | Bits |
| Opérations | Mult + Add | Mult + Add (approx) | XOR, AND, NOT |
| Précision | Exacte | Approximée | Exacte booléenne |
| Bootstrap | Lent | Pas natif | Très rapide (<0.1s) |
| Inference ML | ✓ | ✓✓ (recommandé) | Non optimal |
| Évaluation circuit | ✓ (sans bootstrap) | Non | ✓✓ (recommandé) |
| Taux (op/s) | ~0.1-1 | ~1-10 | ~100-1000 |

---

## 8. Verifiable Delay Functions (VDF)

### 8.1 Principe

Une **VDF** est une fonction qui prend un temps minimum à calculer (même avec parallélisme), mais dont le résultat est facilement vérifiable.

```python
# Propriétés :
# 1. Sequential : T est le temps minimum (pas d'accélération parallèle)
# 2. Efficace à vérifier : log(T) ≪ T

# Utilité : randomness beacon (Éthereum, Chia), time-stamping

# Construction VDF (Wesolowski, 2019)
def vdf_eval(G, T, seed):
    """
    Calcule la VDF : y = seed^{2^T} mod N
    Obligé de faire T squarings séquentiellement.
    """
    y = seed
    for _ in range(T):
        y = pow(y, 2, N)
    return y

def vdf_prove(G, T, seed):
    """Preuve que y = seed^{2^T} mod N est correct (Wesolowski)"""
    y = vdf_eval(G, T, seed)
    
    # Preuve : (y, π) où π = seed^{⌊2^T / 2^ℓ⌋}
    # ℓ est un défi aléatoire
    l = hash(seed, y)  # Défi
    
    # π = seed^{floor(2^T / l)} mod N
    # Calculable en O(T) par l'évaluateur
    # Vérifiable en O(log T) car π^l · y = seed^{2^T}
    
    return y, pi
```

### 8.2 VDF dans Ethereum 2.0 (RANDAO + VDF)

```python
# Ethereum 2.0 combine RANDAO + VDF pour générer l'aléa du beacon chain
# RANDAO fournit l'entropie initiale
# VDF garantit l'imprévisibilité (pas de dernier reveal attack)

# Chaque epoch, le VDF est exécuté sur le RANDAO mix
# pour produire le random seed de l'epoch suivante
# Temps : 1024 squarings (~100ms)
```

---

## 9. Applications et Implémentations

### 9.1 Implémentations par langage

**C++ :**
```bash
# SEAL (Microsoft) — BFV + CKKS
git clone https://github.com/microsoft/SEAL
cd SEAL && cmake -S . -B build && cmake --build build

# HElib (IBM) — BGV
git clone https://github.com/homenc/HElib
cd HELib && make

# TFHE (Zama)
git clone https://github.com/zama-ai/tfhe
cd tfhe && make

# MP-SPDZ (MPC Framework)
git clone https://github.com/data61/MP-SPDZ
cd MP-SPDZ && make setup
```

**Python :**
```bash
pip install tenseal      # BFV + CKKS (recommandé)
pip install phe          # Paillier (PHE)
pip install spdz         # SPDZ MPC
pip install charm-crypto # Pairings, BLS, etc.
```

**Rust :**
```bash
cargo add tfhe           # Zama TFHE
cargo add sunscreen      # FHE compiler
cargo add concrete       # Concrete ML (Zama)
cargo add mpz            # MPC utilities
```

### 9.2 Exemple complet : Somme sécurisée (MPC + Paillier)

```python
from phe import paillier

def threshold_sum(parties_data, public_key):
    """
    Somme chiffrée de plusieurs parties utilisant Paillier.
    Chaque partie chiffre sa contribution.
    """
    # Chaque partie chiffre sa valeur
    encrypted_values = [
        public_key.encrypt(v) for v in parties_data
    ]
    
    # Le serveur somme les valeurs chiffrées
    encrypted_sum = encrypted_values[0]
    for e in encrypted_values[1:]:
        encrypted_sum = encrypted_sum + e  # Homomorphic addition
    
    return encrypted_sum  # ← à déchiffrer seulement si toutes les parties sont d'accord
```

### 9.3 Applications Industrielles

| Application | Technologie | Usage |
|-------------|-------------|-------|
| Private Set Intersection | MPC (OT + circuit) | Partage de données sans fuite |
| Secure Inference | CKKS | ML sur données chiffrées (Cryptonets) |
| E-Voting | Paillier | Bulletins chiffrés, décompte homomorphe |
| Auctions | MPC (Yao) | Enchères sans révélation des bids |
| Privacy-Preserving Analytics | SPDZ | Calcul d'agrégats sur données sensibles |
| Threshold Wallets | MPC (GG18) | Signature sans clé complète |
| Randomness Beacon | VDF | Aléa vérifiable |

---

## Références

- **Shamir Secret Sharing** : https://dl.acm.org/doi/10.1145/359168.359176
- **Yao's Garbled Circuits** : https://eprint.iacr.org/1982/004
- **Oblivious Transfer (Naor-Pinkas)** : https://www.wisdom.weizmann.ac.il/~naor/PAPERS/ot.ps
- **SPDZ Protocol** : https://eprint.iacr.org/2012/642
- **ABY Framework** : https://eprint.iacr.org/2014/008
- **CKKS Scheme** : https://eprint.iacr.org/2016/421
- **BFV Scheme** : https://eprint.iacr.org/2012/144
- **TFHE (Zama)** : https://tfhe.github.io/tfhe/
- **FHE (Gentry)** : https://dl.acm.org/doi/10.1145/1536414.1536426
- **VDF (Wesolowski)** : https://eprint.iacr.org/2018/623
- **MP-SPDZ** : https://github.com/data61/MP-SPDZ
- **TenSEAL** : https://github.com/OpenMined/TenSEAL
- **Microsoft SEAL** : https://github.com/microsoft/SEAL
- **VDF Research** : https://vdfresearch.org