---
name: hash-functions
description: Guide complet des fonctions de hachage cryptographiques — SHA-2, SHA-3, BLAKE2, BLAKE3, SHAKE, KMAC, constructions Merkle-Damgård et Sponge, collisions, HMAC, et applications.
category: cybersecurite
tags: [hash, sha256, sha3, blake2, blake3, merkle-damgard, sponge, hmac, kdf, cryptography]
---

# Fonctions de Hachage Cryptographiques — Guide Approfondi

## Sommaire
1. [Propriétés Fondamentales](#propriétés-fondamentales)
2. [Construction Merkle-Damgård (SHA-2, MD5, SHA-1)](#construction-merkle-damgård)
3. [Construction Sponge (SHA-3, SHAKE)](#construction-sponge-sha-3)
4. [SHA-2 Architecture Interne](#sha-2-architecture-interne)
5. [SHA-3 / Keccak Architecture Interne](#sha-3-keccak-architecture-interne)
6. [BLAKE2 et BLAKE3](#blake2-et-blake3)
7. [HMAC — Message Authentication Code](#hmac)
8. [KDF — Key Derivation Functions](#kdf)
9. [Collisions et Cryptanalyse](#collisions-et-cryptanalyse)
10. [Applications et Implémentations](#applications-et-implémentations)

---

## 1. Propriétés Fondamentales

### 1.1 Les 5 propriétés de sécurité

**1. Préimage Resistance (One-Way)**
Étant donné `h = H(m)`, il est difficile de trouver `m`.
→ Complexité : `O(2^n)` pour un hash de n bits.

**2. Second Preimage Resistance (Weak Collision)**
Étant donné `m₁`, il est difficile de trouver `m₂ ≠ m₁` avec `H(m₁) = H(m₂)`.
→ Complexité : `O(2^n)`

**3. Collision Resistance (Strong Collision)**
Il est difficile de trouver `m₁ ≠ m₂` avec `H(m₁) = H(m₂)`.
→ Complexité : `O(2^{n/2})` (anniversaire)

**4. Avalanche Effect**
Un changement de 1 bit dans l'entrée modifie ~50% des bits de sortie.

**5. Deterministic**
La même entrée produit toujours la même sortie.

### 1.2 Résistance par Anniversaire

L'attaque des anniversaires : pour un hash de n bits, une collision est attendue après `~√(2·π·2^n / 2) ≈ 2^{n/2}` essais.

```
n bits    2^{n/2}     Type
128       2^64        Attaquable (MD5/SHA-1)
160       2^80        Limite (SHA-1 cassé)
224       2^112       Sûr (SHA-224)
256       2^128       Sûr (SHA-256, BLAKE2s)
384       2^192       Très sûr (SHA-384)
512       2^256       Extrême (SHA-512, BLAKE2b)
```

---

## 2. Construction Merkle-Damgård

### 2.1 Structure

```
Message M = M₁ || M₂ || ... || M_k
Chaque bloc M_i = r bits

                    IV
                     │
M₁ ──→ [Compress] ──→ H₁
                     │
M₂ ──→ [Compress] ──→ H₂...
                     │
                  ...│...
                     │
M_k ──→ [Compress] ──→ H_k (hash final)
```

**Padding de Merkle-Damgård** (MD strengthening) : ajoute 1, puis des 0, puis la longueur du message en bits.

Pour SHA-256 (blocs de 512 bits) :
```
Message original (L bits)
│
┌────────────────────────────────────────────┐
│ M || 1 || 0...0 (k bits) || L (64 bits)   │
└────────────────────────────────────────────┘
         512 * ceil((L + 65) / 512)
```

### 2.2 Vulnérabilité : Length Extension

Propriété inhérente à Merkle-Damgård :
```
Si on connaît H(M) et la longueur de M, on peut calculer H(M || padding || extension)
sans connaître M.
```

**Fonctions vulnérables** : MD5, SHA-1, SHA-256, SHA-512
**Résistantes** : SHA-3 (sponge), BLAKE2 (counter-based), HMAC

```python
import struct

def md_length_extension(hash_state, original_len, extension, compress_func, block_size):
    """
    Length extension sur construction Merkle-Damgård.
    Compress_func prend (state, block) et retourne le nouvel état.
    """
    # Reconstruire le padding du message original
    padding = b'\x80'  # bit 1
    padding += b'\x00' * ((block_size - (original_len + 8 + 1) % block_size) % block_size)
    padding += struct.pack('>Q', original_len * 8)
    
    # Nouveau message : original || padding || extension
    # Hachage depuis l'état interne connu
    for i in range(0, len(extension), block_size):
        block = extension[i:i+block_size]
        if len(block) < block_size:
            # Ajouter le padding de Merkle-Damgård pour le nouveau message
            pad_len = (len(extension) + 8 + 1) % block_size
            block += b'\x80' + b'\x00' * ((block_size - pad_len - 8 - 1) % block_size)
            block += struct.pack('>Q', (original_len + len(extension)) * 8)
        hash_state = compress_func(hash_state, block)
    
    return hash_state
```

---

## 3. Construction Sponge (SHA-3)

### 3.1 Principe

```
        M₁     M₂           M_k
         │      │            │
         ↓      ↓            ↓
    ┌──────────────────────────────────┐
    │          Sponge (f)              │
    │  ┌─────┐  ┌─────┐      ┌─────┐  │
    │  │ f   │  │ f   │ ...  │ f   │  │
    │  └─────┘  └─────┘      └─────┘  │
    │  ─────────────────────────────── │
    │  Absorbing phase        Squeezing│
    └──────────────────────────────────┘
                              │  │  │
                              ↓  ↓  ↓
                              Z₁ Z₂ Z₃
```

La construction sponge est composée de trois éléments :
- **State** : `s = r + c` bits (rate + capacity)
- **Permutation f** : fonction pseudo-aléatoire (Keccak-f pour SHA-3)
- **Pad** : règle de padding (multi-rate, `pad10*1`)

### 3.2 Propriétés

- **Longueur de sortie variable** (SHAKE128, SHAKE256 — XOF)
- **Résistance au length extension** par construction
- **Security level** : min(c/2, r/2)
  - SHA3-256 : c = 512, r = 1088 → 256 bits
  - SHA3-512 : c = 1024, r = 576 → 512 bits
  - SHAKE128 : c = 256, r = 1344 → 128 bits de sécurité
  - SHAKE256 : c = 512, r = 1088 → 256 bits de sécurité

---

## 4. SHA-2 Architecture Interne

### 4.1 Famille SHA-2

| Fonction | Taille output | Bloc | Mots | Rounds |
|----------|--------------|------|------|--------|
| SHA-224 | 224 bits | 512 bits | 32-bit × 8 | 64 |
| SHA-256 | 256 bits | 512 bits | 32-bit × 8 | 64 |
| SHA-384 | 384 bits | 1024 bits | 64-bit × 8 | 80 |
| SHA-512 | 512 bits | 1024 bits | 64-bit × 8 | 80 |
| SHA-512/224 | 224 bits | 1024 bits | 64-bit × 8 | 80 |
| SHA-512/256 | 256 bits | 1024 bits | 64-bit × 8 | 80 |

### 4.2 SHA-256 Round Function

```python
# Constantes K (64 premières racines cubiques des nombres premiers)
K = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
    # ... 60 autres constantes
]

# Fonctions de compression
def Ch(x, y, z):   return (x & y) ^ (~x & z)
def Maj(x, y, z):  return (x & y) ^ (x & z) ^ (y & z)
def Sigma0(x):     return rot_r(x, 2) ^ rot_r(x, 13) ^ rot_r(x, 22)
def Sigma1(x):     return rot_r(x, 6) ^ rot_r(x, 11) ^ rot_r(x, 25)
def sigma0(x):     return rot_r(x, 7) ^ rot_r(x, 18) ^ shr(x, 3)
def sigma1(x):     return rot_r(x, 17) ^ rot_r(x, 19) ^ shr(x, 10)

def compress_sha256(state, block):
    """Compresse un bloc de 512 bits dans l'état de 256 bits"""
    A, B, C, D, E, F, G, H = state
    
    # Message Schedule : 16 → 64 mots
    W = list(struct.unpack('>16I', block))
    for t in range(16, 64):
        W.append((sigma1(W[t-2]) + W[t-7] + sigma0(W[t-15]) + W[t-16]) & 0xFFFFFFFF)
    
    # Compression : 64 rounds
    for t in range(64):
        T1 = (H + Sigma1(E) + Ch(E, F, G) + K[t] + W[t]) & 0xFFFFFFFF
        T2 = (Sigma0(A) + Maj(A, B, C)) & 0xFFFFFFFF
        H, G, F, E, D, C, B, A = G, F, E, (D + T1) & 0xFFFFFFFF, C, B, A, (T1 + T2) & 0xFFFFFFFF
    
    # Ajouter à l'état initial (Davies-Meyer)
    return [
        (state[0] + A) & 0xFFFFFFFF,
        (state[1] + B) & 0xFFFFFFFF,
        (state[2] + C) & 0xFFFFFFFF,
        (state[3] + D) & 0xFFFFFFFF,
        (state[4] + E) & 0xFFFFFFFF,
        (state[5] + F) & 0xFFFFFFFF,
        (state[6] + G) & 0xFFFFFFFF,
        (state[7] + H) & 0xFFFFFFFF,
    ]

def sha256(message: bytes) -> bytes:
    """SHA-256 complet"""
    # Padding
    ml = len(message) * 8
    message += b'\x80'
    while (len(message) * 8) % 512 != 448:
        message += b'\x00'
    message += struct.pack('>Q', ml)
    
    # Vecteurs d'initialisation
    IV = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
          0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    
    state = IV[:]
    for i in range(0, len(message), 64):
        state = compress_sha256(state, message[i:i+64])
    
    return struct.pack('>8I', *state)
```

---

## 5. SHA-3 / Keccak Architecture Interne

### 5.1 La Permutation Keccak-f

État : 5×5×64 bits = 1600 bits (25 mots de 64 bits)

```
State[5][5] = Lane[x][y]
x, y ∈ {0, ..., 4}
Un seul round de Keccak-f :

θ (Theta) : XOR diffusion entre colonnes
ρ (Rho)   : Décalage cyclique de chaque lane
π (Pi)    : Permutation des lanes
χ (Chi)   : Non-linéarité (porte NAND-like)
ι (Iota)  : Ajout d'une constante de round

Pour Keccak-f[1600] : 24 rounds
```

### 5.2 Implémentation simplifiée

```python
def keccak_f(state):
    """Keccak-f[1600] : 24 rounds de la permutation"""
    RC = [  # Constantes de round (24)
        0x0000000000000001, 0x0000000000008082, 0x800000000000808A,
        # ... 21 autres constantes
    ]
    ROT = [  # Décalages Rho
        [0, 36, 3, 105, 210], [1, 300, 10, 45, 66],
        [190, 6, 171, 15, 253], [28, 55, 153, 21, 120],
        [91, 276, 231, 136, 78]
    ]
    
    for r in range(24):
        # θ (Theta)
        C = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4] for x in range(5)]
        D = [C[(x-1)%5] ^ rot_l(C[(x+1)%5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                state[x][y] ^= D[x]
        
        # ρ (Rho) + π (Pi) — combinés
        new_state = [[0]*5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                new_state[y][(2*x+3*y)%5] = rot_l(state[x][y], ROT[x][y])
        state = new_state
        
        # χ (Chi) — non-linéarité
        for x in range(5):
            for y in range(5):
                state[x][y] ^= (~state[(x+1)%5][y]) & state[(x+2)%5][y]
        
        # ι (Iota) — round constant
        state[0][0] ^= RC[r]
    
    return state
```

### 5.3 SHA-3 vs SHAKE

```python
# SHA3-256 : tag = 0x06, 256 bits de sortie
# SHA3-512 : tag = 0x06, 512 bits de sortie
# SHAKE128 : tag = 0x1F, sortie variable
# SHAKE256 : tag = 0x1F, sortie variable

# SHAKE256 — Extendable-Output Function (XOF)
from hashlib import shake_256

# Sortie de longueur arbitraire
h = shake_256(b"Message")
output_32 = h.digest(32)    # 32 octets
output_64 = h.digest(64)    # 64 octets (même hachage, continue à squeezer)
```

---

## 6. BLAKE2 et BLAKE3

### 6.1 BLAKE2

Finaliste SHA-3, plus rapide que SHA-2 tout en étant au moins aussi sécurisé.

| Fonction | Output | Sécurité | Performance |
|----------|--------|----------|-------------|
| BLAKE2s | 256 bits | 128 bits | ~3× plus rapide que SHA-256 |
| BLAKE2b | 512 bits | 256 bits | ~2× plus rapide que SHA-512 |
| BLAKE2bp | 256 bits | 128 bits | parallèle (4 voies) |
| BLAKE2sp | 256 bits | 128 bits | parallèle (8 voies) |

**Différences clés avec SHA-2** :
- Pas de **length extension** (padding final avec compteur)
- **Paramètres personnalisables** : sel, personnalisation, clé (MAC)
- **Mode parallèle** disponible (BLAKE2sp/bp)

```python
import hashlib

# BLAKE2b avec clé (MAC)
key = b'super secret key'
h = hashlib.blake2b(b'Message', key=key, digest_size=32)
mac = h.digest()

# BLAKE2s avec personnalisation
person = b'MyProtocol v1.0'
h = hashlib.blake2s(b'Message', person=person)

# Arbre (tree hashing)
h = hashlib.blake2b(b'Message', 
    fanout=4, depth=2, leaf_size=4096, node_depth=0, inner_size=64)
```

### 6.2 BLAKE3

Fonction de hachage la plus rapide (Jack O'Connor, 2020).

**Caractéristiques** :
- **~10× plus rapide que SHA-256** sur les longs messages (SIMD + multi-thread)
- **Arbre de Merkle binaire** intégré : hachage parallèle naturel
- **Sortie de longueur variable** (XOF)
- **MAC, KDF, PRF** en un seul primitif
- **Sécurité** : 128 bits contre les préimages, 256 bits contre les collisions

```bash
# Installer
pip install blake3
```

```python
import blake3

# Hash simple
h = blake3.blake3(b"Message")
digest = h.digest()      # 32 octets
hexdigest = h.hexdigest() # 64 caractères hex

# XOF : sortie de longueur variable
h = blake3.blake3(b"Message")
output_100 = h.digest(length=100)

# Keyed hash (MAC)
key = b'\x00' * 32
h = blake3.blake3(b"Message", key=key)

# Key derivation
ctx = blake3.blake3(b"my app", key=b'salt_or_key')
h = ctx.derive_key(b"subkey context")

# Hachage incrémental
h = blake3.blake3()
h.update(b"Partie 1")
h.update(b"Partie 2")
h.update(b"Partie 3")
digest = h.digest()
```

**Structure interne de BLAKE3 :**
```
┌────────────────────────────────────────────┐
│         Binary Merkle Tree                 │
│                                            │
│  ┌──────┐ ┌───┐ ┌────┐ ┌───┐              │
│  │CV_1   │ │CV_2│ │CV_3│ │CV_4│            │
│  └───┬───┘ └───┘ └───┬┘ └───┘              │
│      └──────┬────────┘                     │
│             │                              │
│        ┌────┴────┐                        │
│        │  CV_12   │                        │
│        └────┬────┘                        │
│             │                              │
│         ┌───┴───┐                         │
│         │  Root  │                         │
│         └───────┘                         │
└────────────────────────────────────────────┘
```

---

## 7. HMAC — Message Authentication Code

### 7.1 Définition (RFC 2104)

```
HMAC(K, M) = H((K' ⊕ opad) || H((K' ⊕ ipad) || M))

où :
  K' = K si len(K) <= block_size
       H(K) sinon (pour les clés trop longues)
  ipad = 0x36 répété block_size fois
  opad = 0x5C répété block_size fois
```

### 7.2 Propriétés de sécurité

- **Attaque sur clef** : pour retrouver K à partir de HMAC(K, M) connus, besoin de `O(2^n)` où n est la taille du hash
- **Attaque par collision** : besoin de `O(2^{n/2})` comme pour le hash sous-jacent
- **Pas de length extension** : HMAC résiste car le secret est dans les deux appels de hash

### 7.3 Implémentation

```python
import hmac
import hashlib

def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """HMAC-SHA256 selon RFC 2104"""
    block_size = 64  # SHA-256 block size
    
    # Si la clé est trop longue, la hacher
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    # Si la clé est trop courte, la paddre avec des 0
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))
    
    ipad = bytes([k ^ 0x36 for k in key])
    opad = bytes([k ^ 0x5C for k in key])
    
    inner = hashlib.sha256(ipad + message).digest()
    return hashlib.sha256(opad + inner).digest()
```

```python
# Avec la bibliothèque standard
h = hmac.new(key, msg=message, digestmod=hashlib.sha256)
expected = h.digest()
```

---

## 8. KDF — Key Derivation Functions

### 8.1 PBKDF2 (RFC 2898)

Basé sur HMAC-SHA256, conçu pour être lent (iterations) :

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=b'salt',
    iterations=600000,  # 600K itérations (recommandé 2024)
)
key = kdf.derive(b"password")
```

### 8.2 Argon2 — Vainqueur PHC

Recommandé pour le stockage de mots de passe :

```python
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=3,      # 3 itérations
    memory_cost=2**16, # 64 MB
    parallelism=4,    # 4 threads
    hash_len=32,
    salt_len=16,
)
hash = ph.hash("mot de passe")
ph.verify(hash, "mot de passe")  # True
```

### 8.3 HKDF (RFC 5869)

Basé sur HMAC, pour dériver des clés cryptographiques dans les protocoles :

```python
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

# Étape 1 : Extract (PRK = HMAC-Hash(salt, IKM))
# Étape 2 : Expand (dérivation en plusieurs sous-clés)
kdf = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    info=b'context info',
)
key = kdf.derive(b"input key material")

# Utilisé dans TLS 1.3, SSH, IPsec
```

---

## 9. Collisions et Cryptanalyse

### 9.1 État des lieux

| Fonction | Output | Collision | Coût collision | État |
|----------|--------|-----------|---------------|------|
| MD4 | 128 | Oui | 2^2 | Complètement cassé |
| MD5 | 128 | Oui | 2^16 (~1 sec) | Cassé |
| SHA-1 | 160 | Oui | 2^63 (SHAttered) | ~10K$ GPU 2017 |
| SHA-224 | 224 | Non | > 2^112 | Sûr |
| SHA-256 | 256 | Non | > 2^128 | Sûr |
| SHA-384 | 384 | Non | > 2^192 | Sûr |
| SHA-512/256 | 256 | Non | > 2^128 | Sûr |
| SHA3-256 | 256 | Non | > 2^128 | Sûr |
| BLAKE2s | 256 | Non | > 2^128 | Sûr |
| BLAKE3 | 256 | Non | > 2^128 | Sûr |

### 9.2 SHA-1 — SHAttered Attack (2017)

Première collision publique sur SHA-1 :

```python
# Attaque de Stevens et al. (2017)
# Coût : ~6500 CPU-années, ~110 GPU-années, ~10K$
# Technique : attaque des anniversaires + differential cryptanalysis
# Résultat : deux PDFs avec le même SHA-1
# https://shattered.io
```

**Outil :**
```bash
# Vérifier SHAttered
sha1sum pdf1.pdf pdf2.pdf  # Même hash !
python -c "
from shattered import check_pdf
pdf1 = open('pdf1.pdf', 'rb').read()
pdf2 = open('pdf2.pdf', 'rb').read()
print(check_pdf(pdf1, pdf2))  # True si pair SHAttered
"
```

### 9.3 Hash Length Extension en pratique

```python
# Attaque sur une API utilisant SHA-256 pour MAC :
# Si verification = SHA256(secret || command), on peut forger :
# SHA256(secret || "pay 10" || padding || "pay 1000000")

def forge_mac(original_mac, original_len, extension, known_suffix=""):
    """
    Forge un nouveau MAC via length extension.
    Retourne (new_mac, new_message).
    """
    from hashpumpy import hashpump
    
    # hashpump(original_mac, original_data, data_to_add, key_len, hash_func)
    new_mac, new_message = hashpump(
        original_mac.hex(),
        known_suffix,
        extension,
        original_len,
        hashlib.sha256
    )
    return bytes.fromhex(new_mac), new_message
```

---

## 10. Applications et Implémentations

### 10.1 Outils CLI

```bash
# Calcul de hashs
sha256sum fichier.bin
sha512sum fichier.bin
b2sum fichier.bin  # BLAKE2 intégré (coreutils 8.26+)

# Vérification de fichiers
sha256sum -c checksums.txt

# b3sum (BLAKE3)
cargo install b3sum
b3sum fichier.bin

# SHA-3 avec OpenSSL
openssl dgst -sha3-256 fichier.bin
openssl dgst -shake256 fichier.bin
```

### 10.2 Intégrité de fichiers

```bash
# Créer la checksum
find /important -type f -exec sha256sum {} \; > /root/manifest.sha256

# Vérification
sha256sum -c /root/manifest.sha256 --quiet --strict
```

### 10.3 Tree Hashing (Merkle Tree)

```python
def merkle_tree(data_blocks, hash_func=hashlib.sha256):
    """Construit un Merkle Tree à partir de blocs de données"""
    if len(data_blocks) == 0:
        return hash_func(b'').digest()
    
    # Nœuds feuilles
    nodes = [hash_func(block).digest() for block in data_blocks]
    
    while len(nodes) > 1:
        if len(nodes) % 2 == 1:
            nodes.append(nodes[-1])
        nodes = [
            hash_func(nodes[i] + nodes[i+1]).digest()
            for i in range(0, len(nodes), 2)
        ]
    
    return nodes[0]  # Merkle Root
```

### 10.4 Implémentations par langage

**Python :**
```python
import hashlib
import hmac

hashlib.sha256(b"data").digest()
hashlib.sha3_256(b"data").digest()
hashlib.blake2b(b"data", digest_size=64).digest()
hashlib.shake_256(b"data").digest(32)
hmac.new(key, b"data", hashlib.sha256).digest()
```

**Rust :**
```rust
use sha2::{Sha256, Digest};
let hash = Sha256::digest(b"data");

// BLAKE3
let hash = blake3::hash(b"data");
```

**C (libsodium) :**
```c
// crypto_hash_sha256
unsigned char hash[32];
crypto_hash_sha256(hash, message, message_len);

// Generic hash
crypto_generichash(hash, 32, message, message_len, NULL, 0);

// BLAKE2b via libsodium
crypto_generichash_blake2b(hash, 64, message, message_len, NULL, 0);
```

---

## Références

- **FIPS 180-4 (SHA-2)** : https://csrc.nist.gov/publications/detail/fips/180/4/final
- **FIPS 202 (SHA-3)** : https://csrc.nist.gov/publications/detail/fips/202/final
- **RFC 2104 (HMAC)** : https://datatracker.ietf.org/doc/html/rfc2104
- **RFC 7693 (BLAKE2)** : https://datatracker.ietf.org/doc/html/rfc7693
- **BLAKE3 Specification** : https://github.com/BLAKE3-team/BLAKE3-specs
- **RFC 5869 (HKDF)** : https://datatracker.ietf.org/doc/html/rfc5869
- **RFC 8018 (PBKDF2)** : https://datatracker.ietf.org/doc/html/rfc8018
- **Argon2 (PHC)** : https://github.com/P-H-C/phc-winner-argon2
- **SHAttered (SHA-1 Collision)** : https://shattered.io
- **Merkle Tree** : https://en.wikipedia.org/wiki/Merkle_tree