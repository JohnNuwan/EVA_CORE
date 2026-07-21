---
name: post-quantum-crypto
description: Guide complet de la cryptographie post-quantique — Kyber (ML-KEM), Dilithium (ML-DSA), FALCON, SPHINCS+, NIST standards, réseaux euclidiens, isogenies, code-based, hash-based, et implémentations.
category: cybersecurite
tags: [post-quantum, pqc, kyber, dilithium, falcon, sphincs, lattice, nist, quantum, cryptography]
---

# Cryptographie Post-Quantique — Guide Approfondi

## Sommaire
1. [Le Problème Quantique](#le-problème-quantique)
2. [NIST PQC Standardization](#nist-pqc-standardization)
3. [Lattice-Based Crypto (Réseaux Euclidiens)](#lattice-based-crypto)
4. [ML-KEM (Kyber) — Key Encapsulation Mechanism](#ml-kem-kyber)
5. [ML-DSA (Dilithium) — Digital Signatures](#ml-dsa-dilithium)
6. [FALCON — Signatures Compactes](#falcon)
7. [SLH-DSA (SPHINCS+) — Signatures Stateless Hash-Based](#slh-dsa-sphincs)
8. [FN-DSA (FALCON-based) et Autres Finalistes](#fn-dsa-et-autres)
9. [Implémentations et Migration](#implémentations-et-migration)

---

## 1. Le Problème Quantique

### 1.1 Algorithme de Shor (1994)

L'algorithme de Shor factorise un entier `n` en temps `O((log n)³)` sur un ordinateur quantique :

```
|0⟩ → H⊗ⁿ → |ψ₁⟩ → U_a^2⁰ → U_a^2¹ → ... → |ψ₂⟩ → QFT → |ψ₃⟩ → mesure

Étapes :
1. Superposition : préparer ∑|x⟩|0⟩
2. Exponentiation modulaire : ∑|x⟩|aˣ mod n⟩
3. Transformée de Fourier Quantique (QFT)
4. Mesure → période r de aˣ mod n
5. Si r pair, factorisation : pgcd(a^{r/2} ± 1, n)
```

**Impact direct :**
- RSA : cassé (factorisation)
- ECC (ECDSA, EdDSA, X25519) : cassé (logarithme discret)
- DSA (FIPS 186) : cassé (logarithme discret)
- Pairings (BLS, zk-SNARKs) : cassé
- **Résistants** : AES, SHA-2/3, BLAKE2/3 (Grover seulement)

### 1.2 Algorithme de Grover (1996)

Recherche non-structurée en `O(√N)` au lieu de `O(N)`.

**Impact sur la cryptographie symétrique :**
- AES-128 : réduction de 128 à 64 bits de sécurité
- AES-256 : réduction de 256 à 128 bits de sécurité (toujours sûr)
- SHA-256 : réduction de 128 à 64 bits de résistance aux collisions

**Mitigation** : doubler la taille des clés symétriques.

### 1.3 Échéances Quantiques

| Année | Estimation | Source |
|-------|-----------|--------|
| 2030-2035 | QuBits logiques : ~2000 (casser ECC-256) | Mosca (2018) |
| 2035-2045 | QuBits physiques : ~10⁷ (casser RSA-2048) | NIST (2023) |
| 2035 | 50% de chance de casser RSA-2048 | Global Risk Institute (2023) |

**Mosca's Theorem** : le temps nécessaire pour migrer doit être < (année d'arrivée quantique - année actuelle).

---

## 2. NIST PQC Standardization

### 2.1 Processus NIST (2017-2024)

```
Round 1 (2017) : 69 candidats
Round 2 (2019) : 26 candidats
Round 3 (2022) : 7 finalistes + 8 alternates
Round 4 (2023) : 4 candidates supplémentaires

Sélectionnés (2024) :
  ML-KEM (Kyber)        → KEM standard
  ML-DSA (Dilithium)    → Signature standard
  SLH-DSA (SPHINCS+)    → Signature (hash-based, backup)
  FN-DSA (FALCON)       → Signature (compacte, optionnelle)
```

### 2.2 Standards NIST (FIPS)

| Standard | Algorithme | Type | Taille clé publique | Taille signature | Sécurité |
|----------|-----------|------|-------------------|-----------------|----------|
| FIPS 203 | **ML-KEM** (Kyber) | KEM | 800-1568 B | — | 128-256 bits |
| FIPS 204 | **ML-DSA** (Dilithium) | Signature | 1184-2592 B | 2420-4595 B | 128-256 bits |
| FIPS 205 | **SLH-DSA** (SPHINCS+) | Signature | 32-64 B | ~17-50 KB | 128-256 bits |
| FIPS 206 | **FN-DSA** (FALCON) | Signature | 897-1793 B | 666-1280 B | 128-256 bits |

---

## 3. Lattice-Based Crypto (Réseaux Euclidiens)

### 3.1 Modules Learning With Errors (MLWE)

La sécurité des algorithmes comme Kyber et Dilithium repose sur le problème **Module Learning With Errors (M-LWE)** :

```
Étant donné :
  A ∈ R_q^{k×k} (matrice aléatoire)
  t = A·s + e  (où s, e sont petits)

Trouver s est difficile, même pour un ordinateur quantique.
R_q = Z_q[x]/(x^n + 1) : anneau de polynômes modulo cyclotomique.
```

**Paramètres typiques (Kyber-512) :**
- n = 256 (degré polynomial)
- q = 3329 (modulus)
- k = 2 (dimension du module)
- σ ≈ 2 (écart-type pour l'erreur gaussienne)

### 3.2 Syndrome Decoding Problem

Les attaques sur les réseaux euclidiens se réduisent à :
- **SVP (Shortest Vector Problem)** : trouver le plus court vecteur non-nul
- **CVP (Closest Vector Problem)** : trouver le point du réseau le plus proche d'une cible
- **LWE** : version moyennée, prouvée aussi difficile que SVP (Regev, 2005)

### 3.3 Estimation de sécurité (Lattice Estimator)

```bash
pip install lattice-estimator
```

```python
from estimator import *

# Estimer la sécurité d'un schéma LWE
params = LWE.Parameters(n=256, q=3329, Xs=ND.CenteredBinomial(2), Xe=ND.CenteredBinomial(2))
security = estimate_lwe(params)
# → ~128 bits de sécurité pour Kyber-512
```

---

## 4. ML-KEM (Kyber) — Key Encapsulation Mechanism

### 4.1 Principe

**Key Encapsulation Mechanism (KEM)** : protocole en 3 étapes :
1. **KeyGen** : génération de la paire (sk, pk)
2. **Encaps** : produit un secret partagé + ciphertext
3. **Decaps** : récupère le secret partagé depuis le ciphertext

### 4.2 Spécifications

| Paramètre | ML-KEM-512 | ML-KEM-768 | ML-KEM-1024 |
|-----------|-----------|-----------|------------|
| Sécurité NIST | 128 bits | 192 bits | 256 bits |
| k (module) | 2 | 3 | 4 |
| η₁ | 3 | 2 | 2 |
| η₂ | 2 | 2 | 2 |
| du | 10 | 10 | 11 |
| dv | 4 | 4 | 5 |
| Clé publique | 800 B | 1184 B | 1568 B |
| Clé privée | 1632 B | 2400 B | 3168 B |
| Ciphertext | 768 B | 1088 B | 1568 B |

### 4.3 Algorithme

```python
import hashlib
from random import randint

# Constantes Kyber-512
N = 256          # degré polynomial
Q = 3329         # modulus
K = 2            # module dimension
ETA1 = 3         # Centered binomial distribution
ETA2 = 2

def kyber_keygen():
    """ML-KEM.KeyGen : génération de clé"""
    # 1. Générer seed aléatoire
    d = os.urandom(32)
    rho, sigma = SHAKE256(d, 64)  # split en deux seeds
    
    # 2. Matrice pseudo-aléatoire A ∈ R_q^{k×k}
    A = generate_matrix_A(rho, k)
    
    # 3. Échantillonner s, e depuis distribution binomiale centrée
    s = sample_poly_cbd(ETA1, k)
    e = sample_poly_cbd(ETA1, k)
    
    # 4. t = A·s + e
    t = ntt_multiply_inverse(A, s) + e  # en NTT domain
    
    # 5. Empaqueter
    ek = encode_pk(t, rho)       # public key
    dk = encode_sk(s)            # secret key
    
    return ek, dk

def kyber_encaps(ek):
    """ML-KEM.Encaps : encapsulation"""
    # 1. Dépaqueter t, rho
    t, rho = decode_pk(ek)
    
    # 2. Message aléatoire m ∈ {0,1}²⁵⁶
    m = os.urandom(32)
    
    # 3. Hachages
    m_hash = H(m)  # SHA3-256
    
    # 4. Échantillonner r
    r = G(m_hash, H(ek))  # XOF
    
    # 5. Générer A depuis rho
    A = generate_matrix_A(rho, k)
    
    # 6. Chiffrement
    c1 = vector_ntt(A.T, r) + e1
    c2 = encode_byte(t·r) + encode_bit(m)
    
    # 7. KDF sur le secret partagé
    K = KDF(m_hash, H(c1 || c2))
    
    return K, (c1, c2)

def kyber_decaps(dk, ciphertext):
    """ML-KEM.Decaps : décapsulation"""
    c1, c2 = ciphertext
    s = decode_sk(dk)
    
    # Déchiffrement
    m_prime = decode_bit(c2 - s·c1)
    
    # Re-encapsuler pour vérification
    K_prime = recalculate_K(m_prime)
    
    return K_prime
```

### 4.4 Intégration TLS

Fonctionne comme un KEM hybride avec X25519 (RFC X-Wing) :

```python
# Hybrid key exchange : X25519 + ML-KEM-768
def hybrid_key_exchange(ecdhe_key, kyber_ek):
    ecdhe_shared = x25519_ecdh(ecdhe_key)
    kyber_shared, kyber_ct = kyber_encaps(kyber_ek)
    
    # Combiner les deux secrets
    shared_secret = SHA3_256(ecdhe_shared || kyber_shared)
    return shared_secret, kyber_ct
```

---

## 5. ML-DSA (Dilithium) — Digital Signatures

### 5.1 Spécifications

| Paramètre | ML-DSA-44 | ML-DSA-65 | ML-DSA-87 |
|-----------|----------|----------|----------|
| Sécurité NIST | 128 bits | 192 bits | 256 bits |
| k, l | 3, 2 | 4, 3 | 5, 4 |
| η | 2 | 4 | 2 |
| γ₁ | 2¹⁷ | 2¹⁹ | 2¹⁹ |
| γ₂ | (Q-1)/88 | (Q-1)/32 | (Q-1)/32 |
| Clé publique | 1312 B | 1952 B | 2592 B |
| Clé privée | 2560 B | 4032 B | 4896 B |
| Signature | 2420 B | 3309 B | 4595 B |

### 5.2 Algorithme Fiat-Shamir avec Aborts

Dilithium utilise le paradigme **Fiat-Shamir with Aborts** :

```python
def dilithium_sign(sk, message):
    """ML-DSA.Sign — Signature Dilithium"""
    # 1. Dépaqueter la clé privée
    s1, s2, t0 = unpack_sk(sk)
    
    # 2. Nonce déterministe basé sur message + clé
    mu = H(message)  # SHAKE256
    
    # 3. Boucle avec aborts
    while True:
        # 4. Échantillonner y uniforme dans [-γ₁, γ₁-1]
        y = sample_y(gamma_1)
        
        # 5. w = A·y (transformed en NTT)
        w = ntt_multiply(A, y)
        
        # 6. Haute résolution : w₁ = HighBits(w, 2·γ₂)
        w1 = high_bits(w, 2 * gamma_2)
        
        # 7. Défi c = H(mu || w₁) — hash vers un petit polynôme
        c = sample_in_ball(Hash(mu, w1))
        
        # 8. Réponse : z = y + c·s₁
        z = y + c * s1
        
        # 9. Vérification d'abort : si z est trop grand → recommencer
        if norm_infinity(z) >= gamma_1 - beta:
            continue
        
        # 10. Hint : r₀ = LowBits(w - c·s₂, 2·γ₂)
        r0 = low_bits(w - c * s2, 2 * gamma_2)
        if norm_infinity(r0) >= gamma_2 - beta:
            continue
        
        # 11. Hint pour aider la vérification
        hint = make_hint(-c * t0, w - c * s2 + c * t0)
        
        return (z, hint, c)

def dilithium_verify(pk, message, signature):
    """ML-DSA.Verify — Vérification Dilithium"""
    z, hint, c = signature
    mu = H(message)
    
    # Reconstruire w₁
    Az = ntt_multiply(A, z)
    ct1 = c * t1
    w_prime = Az - ct1
    w1_prime = use_hint(hint, w_prime, 2 * gamma_2)
    
    # Vérifier le défi
    c_prime = sample_in_ball(Hash(mu, w1_prime))
    
    return c == c_prime and norm_infinity(z) < gamma_1 - beta
```

---

## 6. FALCON

### 6.1 Spécifications

**FALCON** (Fast Fourier Lattice-based Compact Signatures Over NTRU) :

| Paramètre | FALCON-512 | FALCON-1024 |
|-----------|-----------|------------|
| Sécurité NIST | 128 bits | 256 bits |
| n | 512 | 1024 |
| q | 12289 | 12289 |
| Clé publique | 897 B | 1793 B |
| Clé privée | 1281 B | 2305 B |
| Signature | 666 B | 1280 B |

**Avantage** : signatures les plus compactes parmi les candidats NIST. Utilisé quand la bande passante est critique (DNS, IoT).

### 6.2 Principe (GPV Trapdoor)

FALCON utilise la construction **Gentry-Peikert-Vaikuntanathan (GPV)** avec l'échantillonnage **FFT-based** :

```python
def falcon_sign(sk, message):
    """Signatures FALCON via échantillonnage Gaussian GPV"""
    # 1. Hachage vers le réseau
    c = HashToPoint(message, n)
    
    # 2. Échantillonnage Gaussian FFT
    # Utilise le trapdoor (B, basis) pour trouver un court vecteur v tel que
    # v ≡ c (mod Λ)
    v = gaussian_fft_sampler(c, B, sigma)
    
    # 3. Conversion en signature compacte
    s = compress_signature(v)
    
    return s
```

**Défi technique** : l'échantillonnage Gaussian nécessite une précision arithmétique (FP) élevée — difficile à implémenter en temps constant.

---

## 7. SLH-DSA (SPHINCS+)

### 7.1 Spécifications

**SPHINCS+** : signature basée uniquement sur des fonctions de hash (AES, SHA-2, SHA-3).

| Paramètre | SLH-DSA-128s | SLH-DSA-128f | SLH-DSA-192s | SLH-DSA-256s |
|-----------|-------------|-------------|-------------|-------------|
| Sécurité | 128 bits | 128 bits | 192 bits | 256 bits |
| Clé publique | 32 B | 32 B | 48 B | 64 B |
| Clé privée | 64 B | 64 B | 96 B | 128 B |
| Signature | 7856 B | 17088 B | 16224 B | 29792 B |
| Hash | SHA-256 | SHA-256 | SHA-256 | SHA-256 |

**Avantage** : **seul standard PQC post-quantum prouvé.** Basé uniquement sur la sécurité des hash (aucun réseau, aucun pairing).

### 7.2 Architecture (XMSS + WOTS + Hypertree)

```
SPHINCS+ utilise une structure arborescente :
    
    FORS (Forest of Random Subsets) — feuilles
      │
    WOTS+ (Winternitz One-Time Signatures)
      │
    XMSS (eXtended Merkle Signature Scheme) — couches
      │
    Hypertree (couches d'arbres XMSS)
```

```python
# Principe WOTS+ (Winternitz OTS)
# Chaque signature WOTS utilise un one-time key pair
# Paramètre w = 16 (compression)
def wots_sign(message, secret_seed, w=16):
    """
    WOTS+ : signature one-time avec paramètre w.
    Plus w est grand, plus la signature est petite mais plus le calcul est lent.
    """
    # 1. Diviser le message en blocs de w bits
    n = len(message) * 8 // w  # nombre de blocs
    msg_chunks = bytes_to_chunks(message, w)
    
    # 2. Calculer le checksum
    checksum = sum(2**w - 1 - c for c in msg_chunks)
    
    # 3. Chaîne d'itérations pour chaque bloc
    signature = []
    for i in range(n + 1):
        if i < n:
            chain_len = msg_chunks[i]
        else:
            chain_len = checksum
        
        # Appliquer la fonction de hash chain_len fois
        secret = derive_secret(secret_seed, i)
        sig_i = iterate_hash(secret, chain_len)
        signature.append(sig_i)
    
    return signature
```

---

## 8. FN-DSA et Autres

### 8.1 FN-DSA (FALCON-based)

Le NIST a standardisé FALCON comme **FN-DSA** (FIPS 206), prévu pour 2025.

### 8.2 Alternates et Autres Approches

| Approche | Exemple | Sécurité | Statut |
|----------|---------|----------|--------|
| Code-based | Classic McEliece | 256 bits | Finaliste NIST round 4 |
| Isogeny-based | SIKE (SIDH) | 128 bits | **CASSÉ** (2022, Castryck-Decru) |
| Hash-based | SPHINCS+ | 256 bits | Standardisé |
| Multivariate | GeMSS, Rainbow | 192 bits | **CASSÉ** (Rainbow 2022) |

### 8.3 Classic McEliece

L'un des plus vieux systèmes post-quantiques, toujours non-cassé depuis 1978.

```python
# Classic McEliece : basé sur le syndrome decoding des codes Goppa binaires
# Avantage : sécurité très étudiée (~50 ans)
# Inconvénient : clé publique énorme (1 MB pour 256 bits)
def mceliece_keygen(m, t):
    """Génération de clé McEliece"""
    n = 2**m  # longueur du code
    k = n - m * t  # dimension
    
    # Code Goppa binaire
    g = random_goppa_polynomial(m, t)
    
    # Matrice génératrice G
    G = generate_generator_matrix(g, m, t)
    
    # Masquage
    S = random_invertible_matrix(k, k)
    P = random_permutation_matrix(n, n)
    
    G_pub = S * G * P  # clé publique
    
    return (S, G, P), G_pub  # privée, publique
```

---

## 9. Implémentations et Migration

### 9.1 Bibliothèques PQC

**C/C++ :**
```bash
# liboqs (Open Quantum Safe) — la référence
git clone https://github.com/open-quantum-safe/liboqs
cd liboqs && mkdir build && cd build
cmake -DCMAKE_INSTALL_PREFIX=/usr/local ..
make -j$(nproc)
sudo make install
```

**Python :**
```bash
pip install liboqs-python
pip install pqcrypto      # Wrapper léger
```

**Rust :**
```bash
cargo add pqcrypto-kyber
cargo add pqcrypto-dilithium
cargo add pqcrypto-falcon
```

**Go :**
```go
import "github.com/cloudflare/circl/kem/kyber"
import "github.com/cloudflare/circl/sign/dilithium"
```

### 9.2 Exemple complet (Python + liboqs)

```python
import liboqs

# ===== ML-KEM (Kyber) =====
def kem_demo():
    # Key Generation
    kem = liboqs.KeyEncapsulation("Kyber768")
    public_key = kem.generate_keypair()
    secret_key = kem.export_secret_key()
    
    # Encapsulation (Bob)
    kem_bob = liboqs.KeyEncapsulation("Kyber768")
    ciphertext, shared_secret_bob = kem_bob.encap_secret(public_key)
    
    # Decapsulation (Alice)
    shared_secret_alice = kem.decap_secret(ciphertext)
    
    assert shared_secret_alice == shared_secret_bob
    print(f"KEM OK: {len(shared_secret_alice)} bytes shared secret")

# ===== ML-DSA (Dilithium) =====
def sig_demo():
    # Key generation
    signer = liboqs.Signature("Dilithium3")
    public_key = signer.generate_keypair()
    
    # Sign
    message = b"Message to sign"
    signature = signer.sign(message)
    
    # Verify
    verifier = liboqs.Signature("Dilithium3")
    is_valid = verifier.verify(message, signature, public_key)
    
    print(f"Signature valide: {is_valid} ({len(signature)} bytes)")

# ===== FALCON =====
def falcon_demo():
    signer = liboqs.Signature("Falcon-1024")
    pk = signer.generate_keypair()
    sig = signer.sign(b"test")
    print(f"FALCON-1024: signature {len(sig)} bytes")

# ===== SPHINCS+ =====
def sphincs_demo():
    signer = liboqs.Signature("SPHINCS+-SHA256-128s")  # small signature
    pk = signer.generate_keypair()
    sig = signer.sign(b"test")
    print(f"SPHINCS+: signature {len(sig)} bytes")
```

### 9.3 TLS Hybrides (OpenSSL + oqsprovider)

```bash
# Installer oqsprovider
pip install oqsprovider

# Configurer OpenSSL 3.x pour TLS hybride
openssl s_server -cert server.crt -key server.key \
  -groups x25519_kyber768:p384_kyber768

# Vérifier la négociation
openssl s_client -connect localhost:4433 -groups x25519_kyber768

# Lister les groupes hybrides disponibles
openssl list -groups | grep -E "kyber|dilithium"
```

### 9.4 Benchmarks Comparatifs (ML-DSA-65)

```python
import time
import liboqs

def benchmark():
    signer = liboqs.Signature("Dilithium3")
    
    # KeyGen
    t0 = time.time()
    pk = signer.generate_keypair()
    print(f"KeyGen: {(time.time()-t0)*1000:.1f}ms")
    
    # Sign
    msg = b"x" * 100
    t0 = time.time()
    sig = signer.sign(msg)
    print(f"Sign: {(time.time()-t0)*1000:.1f}ms ({len(sig)} B)")
    
    # Verify
    verifier = liboqs.Signature("Dilithium3")
    t0 = time.time()
    verifier.verify(msg, sig, pk)
    print(f"Verify: {(time.time()-t0)*1000:.1f}ms")
```

### 9.5 Migration Strategy

```yaml
# Phase 1 — Hybrid (maintenant) : chiffrer avec classique + PQ
# Phase 2 — PQ seul (2030+) : après confiance dans la sécurité PQ

# Exemple : certificat hybride X.509
# Le certificat contient DEUX clés publiques :
#   P-256 (ECDSA) + ML-DSA (Dilithium)
# Les deux signatures sont combinées dans la chaîne

# Configuration serveur recommandée (2025+) :
ssl_certificate /etc/ssl/certs/hybrid-ecdsa-dilithium.pem
ssl_certificate_key /etc/ssl/private/hybrid-ecdsa-dilithium.key
ssl_groups "x25519:x448:kyber768"
```

---

## Références

- **FIPS 203 (ML-KEM)** : https://csrc.nist.gov/pubs/fips/203/final
- **FIPS 204 (ML-DSA)** : https://csrc.nist.gov/pubs/fips/204/final
- **FIPS 205 (SLH-DSA)** : https://csrc.nist.gov/pubs/fips/205/final
- **NIST PQC Standardization** : https://csrc.nist.gov/Projects/post-quantum-cryptography
- **liboqs (Open Quantum Safe)** : https://github.com/open-quantum-safe/liboqs
- **Cloudflare PQ** : https://blog.cloudflare.com/post-quantum-cryptography/
- **OQS Provider** : https://github.com/open-quantum-safe/oqsprovider
- **Regev's LWE Paper** : https://www.cims.nyu.edu/~regev/papers/lwesurvey.pdf
- **Shor's Algorithm** : https://arxiv.org/abs/quant-ph/9508027
- **Mosca's Theorem** : https://eprint.iacr.org/2015/580