---
name: zero-knowledge-proofs
description: Guide complet des preuves à divulgation nulle de connaissance — zk-SNARKs, zk-STARKs, Bulletproofs, Groth16, PLONK, FRI, circom, applications privacy, et implémentations.
category: cybersecurite
tags: [zero-knowledge, zk-snark, zk-stark, bulletproofs, groth16, plonk, circom, privacy, cryptography]
---

# Zero-Knowledge Proofs (ZKP) — Guide Approfondi

## Sommaire
1. [Fondements Théoriques](#fondements-théoriques)
2. [zk-SNARKs (Groth16)](#zk-snarks-groth16)
3. [PLONK — Universal SNARK](#plonk)
4. [Bulletproofs — Sans Trusted Setup](#bulletproofs)
5. [zk-STARKs — Scalable Transparent](#zk-starks)
6. [FRI — Fast Reed-Solomon IOPP](#fri)
7. [circom — ZK Circuit Language](#circom)
8. [Applications Blockchains](#applications-blockchains)
9. [Applications Privacy](#applications-privacy)
10. [Implémentations](#implémentations)

---

## 1. Fondements Théoriques

### 1.1 Définition Formelle

Un protocole ZK implique deux parties :
- **Prouveur (Prover)** : veut prouver une affirmation sans révéler d'information
- **Vérifieur (Verifier)** : vérifie la preuve

Propriétés requises :
```
1. Complétude (Completeness)    : Si l'affirmation est vraie, le vérifieur accepte (prob. ≥ 1 - negl)
2. Solidité (Soundness)         : Si l'affirmation est fausse, le vérifieur rejette (prob. ≥ 1 - negl)
3. Zéro-Connaissance (ZK)      : Le vérifieur n'apprend rien sauf que l'affirmation est vraie
```

**Sécurité prouvée** : dans le modèle de l'oracle aléatoire (Random Oracle Model) ou le modèle de référence commun (CRS, Common Reference String).

### 1.2 Taxonomie des Preuves ZK

| Type | Taille Preuve | Temps Prouveur | Temps Vérifieur | Trusted Setup | Quantum-Resistant |
|------|--------------|----------------|-----------------|---------------|-------------------|
| Groth16 (SNARK) | ~200 B | O(n log n) | O(1) | Oui (circuit) | Non |
| PLONK (SNARK) | ~1 KB | O(n log n) | O(1) | Oui (universel) | Non |
| Bulletproofs | ~1.3 KB | O(n log n) | O(n) | Non | Non |
| STARK (FRI) | ~100-500 KB | O(n log n) | O(n) | Non | Oui |
| MPC-in-the-Head | ~100 KB | O(n²) | O(n) | Non | Oui |
| ZKBoo | ~100 KB | O(n) | O(n) | Non | Oui |

### 1.3 Circuits Algébriques

Toute affirmation vérifiable peut être représentée par un **circuit arithmétique** (addition, multiplication dans un corps fini F_p) :

```
Exemple : Prouver qu'on connaît x tel que f(x) = y

Circuit :
  w₁ = x (témoin privé)
  w₂ = x × x  (multiplication)
  w₃ = w₂ + 42  (addition)
  output w₃ == y

Contraintes R1CS (Rank-1 Constraint System) :
  A·w ∘ B·w = C·w
  
  où w = (1, x, w₂, w₃, y) est le vecteur de témoins
  et ∘ est la multiplication élément par élément
```

---

## 2. zk-SNARKs (Groth16)

### 2.1 Architecture

zk-SNARK = Zero-Knowledge Succinct Non-interactive ARgument of Knowledge.

**Processus en 3 phases :**
1. **Trusted Setup** (une fois par circuit) : génération des paramètres
2. **Prove** : génération de la preuve
3. **Verify** : vérification

**Taille de preuve** : constante (3 éléments de G₁ + 1 de G₂ ≈ 200 octets pour BLS12-381).

### 2.2 La Construction Groth16

Groth16 (2016) est le SNARK le plus efficace en taille de preuve.

**Trusted Setup :**
```python
# Phase 1 (Powers of Tau — universel pour les courbes)
def setup_phase1(curve, n):
    """
    Génération de [τ¹G₁, τ²G₁, ..., τⁿG₁] et [τ¹G₂, ..., τⁿG₂]
    via MPC (Multi-Party Computation).
    
    τ : secret aléatoire, connu de personne (si MPC correctement fait)
    """
    tau = sample_secret()
    return {
        'pk_vk': [(tau**i * G1) for i in range(n)],
        'pk_wk': [(tau**i * G2) for i in range(n)],
    }

# Phase 2 (spécifique au circuit)
def setup_phase2(circuit, pk_phase1):
    """
    Génération des paramètres de preuve spécifiques au circuit.
    δ est un secret aléatoire de phase 2.
    """
    delta = sample_secret()
    # Génération des clés d'évaluation et de vérification
    # ...
    return proving_key, verification_key
```

**Preuve (3 éléments G₁, 1 G₂) :**
```python
def groth16_prove(circuit, witness, pk):
    """
    Génération d'une preuve Groth16.
    Témoin : valeurs secrètes satisfaisant les contraintes.
    """
    # 1. Interpolation des polynômes A(x), B(x), C(x) du circuit
    a_poly = interpolate(witness, 'A')
    b_poly = interpolate(witness, 'B')
    c_poly = interpolate(witness, 'C')
    
    # 2. Évaluation à τ (en utilisant powers of tau)
    A = commit(a_poly, pk)      # G₁
    B = commit(b_poly, pk)      # G₂
    C = commit(c_poly, pk)      # G₁
    
    # 3. Preuve π = (A, B, C)
    proof = (A, B, C)
    public_inputs = witness.public()
    
    return proof, public_inputs
```

**Vérification :**
```python
def groth16_verify(proof, public_inputs, vk):
    """
    Vérification : une seule équation de pairings.
    e(A, B) = e(public_inputs, γ) · e(C, δ)
    """
    A, B, C = proof
    
    # Equation de vérification
    pairing_lhs = pairing(A, B)
    pairing_rhs = pairing(public_commit, gamma) * pairing(C, delta)
    
    return pairing_lhs == pairing_rhs
```

### 2.3 Avantages et Limitations

**Avantages :**
- Preuves les plus compactes (~200-300 octets)
- Vérification O(1) — une équation de pairing
- Très adapté aux blockchains (stockage minimal)

**Limitations :**
- **Trusted Setup** : nécessite une cérémonie pour chaque circuit
- Menace des « toxic waste » : si τ est connu, on peut forger des preuves
- **Pas quantum-resistant**

---

## 3. PLONK

### 3.1 PLONK (Permutations over Lagrange-bases for Oecumenical Noninteractive Arguments of Knowledge)

Proposé par Gabizon, Williamson, Ciobotaru (2019).

**Innovation clé** : un seul **trusted setup universel** pour tous les circuits de taille ≤ n.

### 3.2 Architecture

```
Setup universel (une fois pour toutes) :
  ┌─────────────────────────────────┐
  │ Structured Reference String     │
  │ [q¹G₁, q²G₁, ..., qⁿG₁]         │
  │ [q¹G₂, q²G₂, ..., qⁿG₂]         │
  └─────────────────────────────────┘
```

**Circuit → Preuve (5 étapes) :**

1. **Réduction du circuit à des contraintes polynomiales**
   - Gate constraints (add/mul) : `L(x)·q_L(x) + R(x)·q_R(x) + O(x)·q_O(x) + M(x)·q_M(x) + q_C(x) = 0`
   - Wiring constraints (permutations) : `σ(L(x)) = σ(R(x)) = σ(O(x))`

2. **Polynôme d'argument** : `f(x) = (W_L(x) + β·σ_L(x) + γ)·(W_R(x) + β·σ_R(x) + γ)·(W_O(x) + β·σ_O(x) + γ)`

3. **Division polynomiale** : prouver que `t(x)` divise le polynôme quotient

```python
def plonk_prove(circuit, witness, srs):
    """Génération d'une preuve PLONK"""
    # 1. Engagement sur les polynômes de témoins (3 polynômes × n points)
    w_L = commit(witness.left, srs)
    w_R = commit(witness.right, srs)
    w_O = commit(witness.output, srs)
    
    # 2. Polynôme quotient
    q(x) = quotient_polynomial(circuit, witness)
    t_x = commit(q, srs)
    
    # 3. Évaluations à aléa ζ
    # ...
    
    # 4. Preuve de permutation (polynômes d'argument)
    z_x = commit(permutation_polynomial, srs)
    
    # 5. Ouvertures des engagements (poly à évaluer en ζ et ζ·ω)
    # ...
    
    return proof
```

**Vérification PLONK :** O(n) (n = nombre de gates). Plus lourde que Groth16 mais plus flexible.

### 3.3 Comparaison Groth16 vs PLONK

| Critère | Groth16 | PLONK |
|---------|---------|-------|
| Taille setup | Spécifique au circuit | Universel (une fois) |
| Taille preuve | 3 éléments (G₁, G₂, G₁) | ~10 éléments |
| Temps vérif | O(1) (1 pairing) | O(n) (plusieurs pairings) |
| Temps prover | O(n log n) | O(n log n) |
| Trusted setup | Cérémonie par circuit | Ceremony Power of Tau |
| Flexibilité | Nouveau circuit = nouveau setup | Même setup pour tous |

---

## 4. Bulletproofs

### 4.1 Principe

Preuves courtes **sans trusted setup**, basées sur les engagements de Pedersen.

**Caractéristiques :**
- Taille de preuve : `O(log n)` (environ 1.3 KB pour n = 2^64)
- Vérification : `O(n)` mais avec log-factor constant
- **Pas besoin de pairing** — fonctionne sur n'importe quelle courbe

### 4.2 Range Proof (Inner Product Argument)

```python
# Bulletproofs range proof : prouver qu'une valeur v est dans [0, 2^n - 1]
def bulletproof_range_prove(v, n, G, H, g):
    """
    Prouve que v ∈ [0, 2^n - 1] sans révéler v.
    Utilise un Inner Product Argument (IPA).
    """
    # 1. Décomposition binaire
    a_L = bits_of(v, n)          # vecteur des bits de v
    a_R = [b - 1 for b in a_L]   # a_R = a_L - 1 (pour la contrainte a_L ∘ a_R = 0)
    
    # 2. Engagement vectoriel de Pedersen
    A = commit(a_L, a_R, g)      # engagement sur les vecteurs
    
    # 3. Défi aléatoire du vérifieur
    y = hash(A, ...)              # défi dans F_p
    z = hash(y, ...)             # second défi
    
    # 4. Construction du polynôme à prouver
    # ... (produit scalaire avec récursion logarithmique)
    
    # 5. Inner Product Argument récursif (log n rounds)
    # Chaque round réduit la taille du vecteur de moitié
    proof = ipa_prove(a_L, a_R, y, z)
    
    return proof, commitment_A

def bulletproof_verify(proof, commitment_A, V, n):
    """Vérification du range proof"""
    # 1. Reconstruire les défis y, z
    # 2. Vérifier l'IPA récursif
    # 3. Vérifier les contraintes quadratiques
    
    return valid
```

### 4.3 Application : Confidential Transactions

Utilisé dans Monero (Bulletproofs depuis 2018) :

```bash
# Taille des proofs CT avant/après Bulletproofs
# Avant (Borromean ring sigs) : ~2.5 KB par output
# Après Bulletproofs (2018) : ~1.3 KB pour 2 outputs
# Après Bulletproofs+ (2019) : ~0.8 KB pour 2 outputs
```

---

## 5. zk-STARKs

### 5.1 Scalable Transparent Arguments of Knowledge

Proposé par Eli Ben-Sasson et al. (2018) — StarkWare.

**Propriétés** :
- **Transparent** : pas de trusted setup
- **Scalable** : temps prover O(n log n), vérif O(poly(log n))
- **Quantum-resistant** : basé seulement sur les hash (pas sur ECDLP)
- **Post-quantum** : sûr contre l'algorithme de Shor

**Taille de preuve** : ~100-500 KB (selon paramètres de sécurité et taille du circuit).

### 5.2 Architecture

```
┌──────────────────────────────────────────┐
│           zk-STARK Architecture          │
│                                          │
│  1. Circuit → Exécution Trace (ALGEBRA)  │
│     (list of states: rows = steps,       │
│      columns = registers)                │
│                                          │
│  2. Trace → Polynomial (IOPP)            │
│     Interpolation polynomiale sur le     │
│     domaine évalué (Reed-Solomon code)   │
│                                          │
│  3. Constraint Checking (AIR)            │
│     Algebraic Intermediate Representation│
│     Vérification que le polynôme         │
│     satisfait les contraintes            │
│                                          │
│  4. FRI — Low Degree Test                │
│     Vérifier que le polynôme est de      │
│     degré limité (pas de triche)         │
│                                          │
│  5. Merkle Tree Commitment               │
│     Engager sur les valeurs évaluées     │
└──────────────────────────────────────────┘
```

### 5.2 AIR (Algebraic Intermediate Representation)

```
Contrainte : à chaque pas, next_state est fonction de prev_state
  f(x, y) = 0 pour tout état valide
  
Exemple (Fibonacci) :
  a₀ = 1, a₁ = 1
  a_{i+2} = a_{i+1} + a_i
  
  Polynomial constraints :
    P(x, next_x, next2_x) = next2_x - next_x - x = 0
```

---

## 6. FRI — Fast Reed-Solomon IOPP

### 6.1 Principe

**Fast Reed-Solomon Interactive Oracle Proof of Proximity.**

Objectif : vérifier qu'une fonction polynomiale `f` est proche d'un polynôme de degré `< d` (test de faible degré).

```
Étape 1 : Engager f via Merkle Tree (évaluations sur un domaine)
Étape 2 : Vérifieur envoie un défi aléatoire α
Étape 3 : Prouveur répond avec la moitié des évaluations (pliage)
Étape 4 : Récursion sur la moitié — log₂(n) rounds
Étape 5 : Vérification de la dernière paire d'évaluations
```

### 6.2 Complexité

| Taille circuit | Taille preuve STARK | Temps prover | Temps vérif |
|---------------|-------------------|--------------|-------------|
| 2¹⁶ (~65K) | ~150 KB | ~2s | ~0.1s |
| 2²⁰ (1M) | ~250 KB | ~30s | ~0.5s |
| 2²⁵ (33M) | ~500 KB | ~15min | ~2s |

### 6.3 Comparaison SNARK vs STARK

| Propriété | SNARK (Groth16) | STARK (FRI) |
|-----------|----------------|-------------|
| Trusted setup | Oui (spécifique) | Non (transparent) |
| Taille preuve | ~200 B | ~150-500 KB |
| Vérification | O(1) (pairing) | O(poly(log n)) |
| Quantum-safe | Non (pairing) | Oui (hash) |
| Courbe | BN128, BLS12-381 | N'importe quel champ |
| Preuve récursive | Facile (taille constante) | Possible (plus cher) |

---

## 7. Circom — ZK Circuit Language

### 7.1 Langage de circuits ZK

Circom permet de décrire des circuits arithmétiques de manière déclarative.

```circom
// Exemple : circuit de vérification de hash SHA-256
pragma circom 2.1.0;

template IsEqual() {
    signal input a;
    signal input b;
    signal output out;
    
    // a == b → (a - b) * inv = 1
    signal inv;
    inv <-- 1 / (a - b + 1);
    
    // Contrainte : (a - b) * out = 0
    0 === (a - b) * (out);
}

template SimpleVote() {
    signal input vote;        // 0 ou 1
    signal input secret;      // preuve de connaissance
    signal output commitment; // Hash(secret)
    
    // vote est un bit
    signal bit_check;
    bit_check <== vote * (1 - vote);
    bit_check === 0;
    
    // Engagement sur le secret
    component hasher = SHA256();
    hasher.input <== secret;
    commitment <== hasher.out;
}

component main = SimpleVote();
```

### 7.2 Workflow Circom

```bash
# 1. Compiler le circuit
circom circuit.circom --r1cs --wasm --sym -o build/

# 2. Générer les témoins (avec une entrée)
node build/circuit_js/generate_witness.js build/circuit_js/circuit.wasm input.json witness.wtns

# 3. Powers of Tau ceremony (setup)
snarkjs powersoftau new bn128 12 pot12.ptau -v
snarkjs powersoftau contribute pot12.ptau pot12_final.ptau --name="First contribution" -v

# 4. Phase 2 — circuit spécifique
snarkjs groth16 setup build/circuit.r1cs pot12_final.ptau circuit_0000.zkey
snarkjs zkey contribute circuit_0000.zkey circuit_final.zkey --name="1st Contributor" -v

# 5. Exporter le verification key
snarkjs zkey export verificationkey circuit_final.zkey verification_key.json

# 6. Générer la preuve
snarkjs groth16 prove circuit_final.zkey witness.wtns proof.json public.json

# 7. Vérifier
snarkjs groth16 verify verification_key.json public.json proof.json
```

### 7.3 Exemple complet en Python (via snarkjs wrapper)

```python
import subprocess
import json

def prove_age_over_18(birth_year, current_year, circuit_dir):
    """
    Circuit : prouver age >= 18 sans révéler l'âge exact.
    age = current_year - birth_year
    age - 18 >= 0
    """
    # input.json
    with open(f"{circuit_dir}/input.json", 'w') as f:
        json.dump({"birth_year": birth_year, "current_year": current_year}, f)
    
    # Générer la preuve
    subprocess.run([
        "snarkjs", "groth16", "prove",
        f"{circuit_dir}/circuit_final.zkey",
        f"{circuit_dir}/witness.wtns",
        f"{circuit_dir}/proof.json",
        f"{circuit_dir}/public.json"
    ], check=True)
    
    return json.load(open(f"{circuit_dir}/proof.json"))
```

---

## 8. Applications Blockchains

### 8.1 zk-Rollups

Couche 2 Ethereum : des milliers de transactions sont compressées en une seule preuve ZK.

**Exemple (zkSync Era) :**
```python
# Dans un zk-rollup, chaque bloc de layer 2 produit :
# 1. Preuve ZK que toutes les transitions d'état sont valides
# 2. La preuve est soumise en une transaction Ethereum
# 3. Le contrat vérifie la preuve et met à jour l'état

def zkrollup_submit_batch(batch_txs, old_state_root, new_state_root):
    """Soumet un lot de transactions en layer 1"""
    # Preuve ZK (via circuit spécifique au rollup)
    proof = generate_batch_proof(batch_txs, old_state_root, new_state_root)
    
    # Appel du contrat
    rollup_contract.submitBatch(
        new_state_root,
        batch_hash,
        proof
    )
    
    # Coût : ~5000 gas (vérification ZK) vs millions pour les tx individuelles
```

**Comparaison zk-Rollups vs Optimistic :**
| Critère | zk-Rollup | Optimistic |
|---------|-----------|------------|
| Finalité | Immédiate | ~7 jours |
| Garantie | Mathématique (ZK) | Économique (fraud proof) |
| Coût vérif | ~5000 gas | ~60000 gas (en conflit) |
| TPS | ~2000-20000 | ~100-300 |

### 8.2 Tornado Cash (Protocol Privacy)

Utilisation de zk-SNARKs pour cacher la provenance des transactions Ethereum :

```python
# Tornado Cash — circuit de retrait
def withdraw_proof(deposit_nullifier, secret, merkle_root, merkle_proof):
    """
    Preuve ZK qu'on connaît un dépôt valide (nullifier, secret)
    inclus dans l'arbre de Merkle, sans révéler lequel.
    """
    # Témoins privés : deposit_nullifier, secret, merkle_proof
    # Entrées publiques : merkle_root, recipient_address, relayer_fee
    
    # Contrainte : le hash(nullifier, secret) est une feuille de l'arbre
    leaf_hash = hash(deposit_nullifier, secret)
    
    # Contrainte : la feuille est dans l'arbre (vérification Merkle)
    # Cette preuve consomme ~400K contraintes en circom
    assert merkle_verify(merkle_root, leaf_hash, merkle_proof)
    
    return proof
```

---

## 9. Applications Privacy

### 9.1 zk-SNARK pour l'Identité

```python
# Prouver son âge sans révéler sa date de naissance
def prove_age_zk(birth_date_encrypted, proof_authority_sig, min_age):
    """
    Circuit ZK :
    1. Vérifier que birth_date_encrypted est signé par une autorité
    2. Prouver que current_date - birth_date >= min_age
    3. Ne pas révéler la date exacte
    """
    return snark_proof

# Vérification par le service
verify_zk_proof(proof, {
    'authority_pk': authority_public_key,
    'min_age': 18
})
```

### 9.2 zk-SNARK pour l'Identité Décentralisée (DID)

### 9.3 zk-Email

Vérification d'un email sans révéler son contenu :
```python
# Prouver qu'on a reçu un email d'un domaine spécifique
# sans révéler l'adresse exacte, le sujet, le corps
def verify_email_zk(email_sig, domain="example.com"):
    """
    Preuve ZK sur une signature DKIM :
    1. Vérifier la signature DKIM de l'email
    2. Extraire le domaine de l'en-tête From
    3. Prouver que domine == "example.com"
    4. Ne pas révéler le reste de l'email
    """
```

---

## 10. Implémentations

### Bibliothèques ZK

```bash
# Rust
cargo add bellman       # Groth16 + BLS12-381
cargo add ark-groth16   # Arkworks framework
cargo add plonky2       # PlonK + Goldilocks fields (StarkWare)
cargo add winterfell    # STARK prover/verifier (Facebook)

# JavaScript/TypeScript
npm install snarkjs     # JavaScript SNARKs (Groth16, PLONK)
npm install circomlib   # Bibliothèque de circuits Circom
npm install @noir-lang/noir_wasm  # Noir language (Aztec)

# Python
pip install py_ecc       # Pairings BLS12-381
pip install lambdaworks   # STARK framework (LambdaClass)
```

### Outils CLI

```bash
# Circom — compilation de circuits
circom circuit.circom --r1cs --wasm --sym

# Snarkjs — manipulation de preuves
snarkjs groth16 prove zkey witness proof.json public.json
snarkjs groth16 verify vk public.json proof.json

# Noir (langage ZK natif Rust)
nargo compile
nargo prove
nargo verify

# RISC Zero (ZK VM)
cargo risczero build
cargo risczzero prove
```

### Exemple Noir (langage ZK)

```noir
// Noir — langage ZK natif pour Aztec Network
fn main(x: Field, y: Field) {
    // Prouver qu'on connaît x et y tels que x * y == 10
    let constraint = x * y;
    constrain constraint == 10;
}
```

---

## Références

- **Groth16 Paper** : https://eprint.iacr.org/2016/260
- **PLONK Paper** : https://eprint.iacr.org/2019/953
- **Bulletproofs Paper** : https://eprint.iacr.org/2017/1066
- **STARKs (Ben-Sasson et al.)** : https://eprint.iacr.org/2018/046
- **FRI Protocol** : https://eccc.weizmann.ac.il/report/2017/134/
- **Circom Documentation** : https://docs.circom.io
- **snarkjs** : https://github.com/iden3/snarkjs
- **Noir Language** : https://noir-lang.org
- **zkSync** : https://zksync.io
- **Tornado Cash Circuits** : https://github.com/tornadocash/circuits-circom
- **RISC Zero** : https://risczero.com
- **Awesome ZK** : https://github.com/ventali/awesome-zk