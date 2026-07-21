---
name: aes-advanced
description: Guide complet du chiffrement AES — architecture interne, modes opératoires (GCM, CCM, CTR, OCB, XTS), AES-NI, implémentations constant-time, side-channel resistance, AES-GCM-SIV, AES-KW, attaques et cryptanalyse.
category: cybersecurite
tags: [aes, symmetric-crypto, gcm, aes-ni, side-channel, cipher-modes, rijndael, cryptography]
---

# AES (Advanced Encryption Standard) — Guide Approfondi

## Sommaire
1. [Architecture Interne de Rijndael](#architecture-interne-de-rijndael)
2. [Modes Opératoires Détaillés](#modes-opératoires-détaillés)
3. [AES-NI — Accélération Matérielle](#aes-ni--accélération-matérielle)
4. [Implémentations Constant-Time](#implémentations-constant-time)
5. [Attaques par Canaux Auxiliaires](#attaques-par-canaux-auxiliaires)
6. [AES-GCM-SIV — Chiffrement Nonce-Misuse Resistant](#aes-gcm-siv)
7. [AES Key Wrap (AES-KW)](#aes-key-wrap-aes-kw)
8. [Cryptanalyse d'AES](#cryptanalyse-daes)
9. [Implémentations de Référence](#implémentations-de-référence)

---

## 1. Architecture Interne de Rijndael

### Spécifications AES (FIPS 197)

| Paramètre | AES-128 | AES-192 | AES-256 |
|-----------|---------|---------|---------|
| Taille de clé | 128 bits | 192 bits | 256 bits |
| Taille de bloc | 128 bits | 128 bits | 128 bits |
| Nb de rounds | 10 | 12 | 14 |
| Taille de la clé étendue | 176 octets | 208 octets | 240 octets |

### Vue d'ensemble d'un round

Chaque round (sauf le dernier) applique 4 transformations sur une **State Matrix** 4×4 octets :

```
State (16 octets) = [b0  b4  b8  b12]   ← ordre column-major
                     [b1  b5  b9  b13]
                     [b2  b6  b10 b14]
                     [b3  b7  b11 b15]
```

#### 1.1 SubBytes (Substitution Box)

Boîte de substitution non-linéaire — seule opération non-linéaire d'AES.

Construction mathématique :
1. **Inverse multiplicatif** dans GF(2⁸) avec polynôme irréductible `x⁸ + x⁴ + x³ + x + 1` (0x11B). L'élément `0x00` est mappé sur lui-même.
2. **Transformation affine** :
   ```
   b'_i = b_i ⊕ b_{i+4 mod 8} ⊕ b_{i+5 mod 8} ⊕ b_{i+6 mod 8} ⊕ b_{i+7 mod 8} ⊕ c_i
   ```
   où `c = 0x63`

La S-box peut être pré-calculée dans une table 256×8 bits, ou calculée à la volée pour les implémentations contraintes en mémoire.

**Implémentation Python de la S-box :**

```python
def gf_inv(a: int) -> int:
    """Inverse multiplicatif dans GF(2⁸) avec polynôme 0x11B"""
    if a == 0:
        return 0
    # Petit théorème de Fermat dans GF(2⁸): a⁻¹ = a²⁵⁴
    result = 1
    base = a
    exp = 254
    while exp > 0:
        if exp & 1:
            result = gf_mul(result, base)
        base = gf_mul(base, base)
        exp >>= 1
    return result

def gf_mul(a: int, b: int) -> int:
    """Multiplication dans GF(2⁸) modulo 0x11B"""
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B  # Réduction modulo le polynôme irréductible
        b >>= 1
    return result

def affine_transform(a: int) -> int:
    """Transformation affine de la S-box AES"""
    c = 0x63
    result = 0
    for i in range(8):
        b = (a >> i) & 1 ^ (a >> ((i + 4) % 8)) & 1 ^ \
            (a >> ((i + 5) % 8)) & 1 ^ (a >> ((i + 6) % 8)) & 1 ^ \
            (a >> ((i + 7) % 8)) & 1 ^ ((c >> i) & 1)
        result |= b << i
    return result

def build_sbox() -> list:
    return [affine_transform(gf_inv(i)) for i in range(256)]
```

#### 1.2 ShiftRows

Décalage circulaire des lignes de la State Matrix :
- Ligne 0 : pas de décalage
- Ligne 1 : décalage de 1 position vers la gauche
- Ligne 2 : décalage de 2 positions
- Ligne 3 : décalage de 3 positions

```
Avant :  [a0  a4  a8  a12]   →   Après :  [a0  a4  a8  a12]
         [a1  a5  a9  a13]              [a5  a9  a13 a1]
         [a2  a6  a10 a14]              [a10 a14 a2  a6]
         [a3  a7  a11 a15]              [a15 a3  a7  a11]
```

#### 1.3 MixColumns

Multiplie chaque colonne de l'état (vue comme un polynôme dans GF(2⁸)) par le polynôme fixe `c(x) = 0x03·x³ + 0x01·x² + 0x01·x + 0x02` modulo `x⁴ + 1`.

Pour une colonne `[s₀, s₁, s₂, s₃]` :

```
r₀ = 0x02·s₀ ⊕ 0x03·s₁ ⊕ 0x01·s₂ ⊕ 0x01·s₃
r₁ = 0x01·s₀ ⊕ 0x02·s₁ ⊕ 0x03·s₂ ⊕ 0x01·s₃
r₂ = 0x01·s₀ ⊕ 0x01·s₁ ⊕ 0x02·s₂ ⊕ 0x03·s₃
r₃ = 0x03·s₀ ⊕ 0x01·s₁ ⊕ 0x01·s₂ ⊕ 0x02·s₃
```

#### 1.4 AddRoundKey

XOR bit-à-bit entre l'état courant et la clé de round (KeySchedule).

### Key Schedule

Étend la clé initiale en `Nb·(Nr+1)` mots de 32 bits :

```python
def key_expansion(key: bytes, nk: int = 4, nr: int = 10) -> list:
    """Étend la clé AES (nk = Nb de mots 32-bit, nr = nb de rounds)"""
    w = []
    # Remplir les nk premiers mots
    for i in range(nk):
        w.append(int.from_bytes(key[4*i:4*i+4], 'big'))
    
    # Étendre
    for i in range(nk, 4 * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = rot_word(temp)          # Rotation 1 octet
            temp = sub_word(temp)          # SubBytes par octet
            temp ^= rcon[i // nk]          # Constante de round
        elif nk > 6 and i % nk == 4:       # AES-256 seulement
            temp = sub_word(temp)
        w.append(w[i - nk] ^ temp)
    
    return w

def rot_word(w: int) -> int:
    """Rotation cyclique de 1 octet vers la gauche"""
    return ((w << 8) | (w >> 24)) & 0xFFFFFFFF

def sub_word(w: int) -> int:
    """Applique SubBytes sur chaque octet du mot"""
    return (sbox[(w >> 24) & 0xFF] << 24) | \
           (sbox[(w >> 16) & 0xFF] << 16) | \
           (sbox[(w >> 8) & 0xFF] << 8) | \
           sbox[w & 0xFF]

# Constantes de round RCON[i] = [x^(i-1), 0x00, 0x00, 0x00] dans GF(2⁸)
rcon = [0, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]
```

### Inverse AES (déchiffrement)

Pour déchiffrer, on applique les transformations inverses dans l'ordre inverse :
- **InvSubBytes** : applique l'inverse de la transformation affine d'abord, puis l'inverse multiplicatif
- **InvShiftRows** : décalage circulaire vers la droite
- **InvMixColumns** : multiplication par `d(x) = 0x0B·x³ + 0x0D·x² + 0x09·x + 0x0E`
- **AddRoundKey** : identique (XOR est auto-inverse)

**Important** : On peut réordonner les opérations pour utiliser le même code que le chiffrement (Equivalent Inverse Cipher), mais cela nécessite de modifier le Key Schedule.

---

## 2. Modes Opératoires Détaillés

### 2.1 ECB (Electronic Codebook) — Ne JAMAIS utiliser

Chaque bloc est chiffré indépendamment :
```
C_i = AES_K(P_i)
```

**Problème** : déterministe — deux blocs identiques produisent le même ciphertext. Patterns visibles dans les images chiffrées.

### 2.2 CBC (Cipher Block Chaining)

```
C_0 = AES_K(P_0 ⊕ IV)
C_i = AES_K(P_i ⊕ C_{i-1})
```

- **IV** : aléatoire, taille 16 octets, ne doit jamais être réutilisé avec la même clé
- **Padding** : PKCS#7 obligatoire — vulnérable à l'attaque Padding Oracle
- **Parallélisation** : déchiffrement parallélisable, chiffrement non

### 2.3 CTR (Counter Mode)

Transforme AES en chiffrement de flux :
```
C_i = P_i ⊕ AES_K(Nonce || Counter_i)
```

- **Pas de padding nécessaire**
- **Parallélisation totale** (chiffrement et déchiffrement)
- **Nonce** : 8-12 octets, ne jamais réutiliser (Counter = 4-8 octets, commence à 1)
- **Security bound** : après 2⁶⁴ blocs, collision de compteur possible

### 2.4 GCM (Galois/Counter Mode) — Mode standard TLS 1.3

Combine CTR pour le chiffrement et GHASH pour l'authentification.

```
# Chiffrement (CTR)
C_i = P_i ⊕ AES_K(J_0 + i),   J_0 = IV || 0x00000001

# Tag d'authentification (GHASH — multiplication dans GF(2¹²⁸))
GHASH(H, A, C) = X_{m+n+1}
X_0 = 0
X_i = (X_{i-1} ⊕ A_i) · H  pour i=1..m  (AAD)
X_{m+j} = (X_{m+j-1} ⊕ C_j) · H  pour j=1..n
X_{m+n+1} = (X_{m+n} ⊕ [len(A)||len(C)]) · H

Tag = AES_K(J_0) ⊕ GHASH(H, A, C)
```

Où `H = AES_K(0¹²⁸)` et les multiplications sont dans GF(2¹²⁸) modulo `x¹²⁸ + x⁷ + x² + x + 1`.

**Points critiques** :
- **Ne JAMAIS réutiliser un IV avec la même clé** → fuite complète du keystream et possibilité de forger des tags
- IV 96 bits recommandé (NIST SP 800-38D)
- Longueur maximale de plaintext : 2³⁹ - 256 bits (~64 Go)
- **Timing attacks sur GHASH** possibles sans implémentation constant-time

**Application :**
```bash
# AES-256-GCM avec OpenSSL
openssl enc -aes-256-gcm -in plaintext.txt -out ciphertext.bin \
  -K $(openssl rand -hex 32) -iv $(openssl rand -hex 12)
```

### 2.5 GCM-SIV — Mode Misuse-Resistant

Mode AES-GCM-SIV (RFC 8452) qui reste sûr même en cas de réutilisation de nonce.

**Principe** : le nonce est utilisé pour dériver le sous-clé et l'IV effectif via une MAC. La perte en cas de collision nonce est limitée (authentification seulement, pas de récupération du keystream).

```
# Dérivation de clé
K_1 = AES_K(0x00 || nonce)
K_2 = AES_K(0x20 || nonce)
K_3 = AES_K(0x40 || nonce)
K_4 = AES_K(0x60 || nonce)
K_5 = AES_K(0x80 || nonce)

# Polyval (authentification) puis CTR (chiffrement)
# Ordre inversé par rapport à GCM : MAC puis encrypt
```

**Points clés** :
- Nonce de 12 octets recommandé
- Meilleure garantie de sécurité que GCM standard
- 2-3× plus lent que GCM standard
- Standardisé dans l'IETF (RFC 8452)

### 2.6 CCM (Counter with CBC-MAC)

Combine CBC-MAC (authentification) et CTR (chiffrement). Standardisé IEEE 802.11 (WiFi).

- **Format** : `C_i = P_i ⊕ AES_K(CTR_i)` pour i=1..n
- **MAC** : CBC-MAC sur le formatage spécial (flags + nonce + t)

**Limitations** :
- Pas de parallélisation (CBC-MAC séquentiel)
- Longueur limitée du message
- Traitement en deux passes

### 2.7 OCB (Offset Codebook Mode)

Mode authentifié le plus rapide (une seule passe, parallélisable).

- Breveté (libre pour usage open-source depuis 2021)
- Utilise une **tweakey** (offset) calculée via multiplication par 2 dans GF(2¹²⁸)
- Besoin de seulement `n+2` appels AES pour n blocs (vs 2n pour GCM)

**OCB3 (RFC 7253)** :
```
# Pour chaque bloc (sauf le dernier)
Offset_i = Offset_{i-1} ⊕ L · x^{ntz(i)}  # L = AES_K(0), ntz = nombre de trailing zeros
C_i = AES_K(P_i ⊕ Offset_i) ⊕ Offset_i
Tag = AES_K(Sum ⊕ Offset_m)  # Sum = XOR de tous les P_i
```

### 2.8 XTS (XEX-based Tweaked CodeBook mode)

Standard IEEE 1619 pour le chiffrement de disque (dm-crypt, BitLocker, FileVault).

- **Tweak** basé sur le numéro de secteur
- Pas de MAC — ne fournit **pas** d'authentification
- Parallélisable, aléatoire à taille fixe

---

## 3. AES-NI — Accélération Matérielle

### Instructions AES-NI (Intel/AMD)

6 instructions ajoutées au jeu x86 (Westmere, 2010) :

| Instruction | Description |
|-------------|-------------|
| `AESENC` | 1 round AES (SubBytes+ShiftRows+MixColumns+AddRoundKey) |
| `AESENCLAST` | Dernier round (SubBytes+ShiftRows+AddRoundKey) |
| `AESDEC` | 1 round inverse |
| `AESDECLAST` | Dernier round inverse |
| `AESKEYGENASSIST` | 1 étape du key schedule |
| `PCLMULQDQ` | Multiplication carry-less 64-bit (GHASH) |

### Utilisation en C

```c
#include <wmmintrin.h>

void aes_encrypt_block(__m128i *state, __m128i *round_keys, int rounds) {
    *state = _mm_xor_si128(*state, round_keys[0]);
    for (int r = 1; r < rounds; r++)
        *state = _mm_aesenc_si128(*state, round_keys[r]);
    *state = _mm_aesenclast_si128(*state, round_keys[rounds]);
}
```

### Vérification de disponibilité

**Linux** :
```bash
grep aes /proc/cpuinfo
# Flags: ... aes ...
```

**Programmatique** :
```c
#include <cpuid.h>
int has_aes_ni() {
    unsigned int eax, ebx, ecx, edx;
    __get_cpuid(1, &eax, &ebx, &ecx, &edx);
    return ecx & bit_AES;  // bit 25
}
```

### Performances

Avec AES-NI, AES-128 atteint ~1 cycle/octet (vs ~10-15 cycles/octet sans). OpenSSL utilise automatiquement AES-NI quand disponible.

```bash
openssl speed -evp aes-128-gcm
openssl speed -evp aes-256-gcm
```

### Implémentation Python avec AES-NI

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# cryptography utilise automatiquement AES-NI si disponible
backend = default_backend()
key = algorithms.AES(os.urandom(32))
cipher = Cipher(algorithms.AES(key), modes.GCM(os.urandom(12)), backend=backend)
encryptor = cipher.encryptor()
ciphertext = encryptor.update(b"Message secret") + encryptor.finalize()
tag = encryptor.tag
```

---

## 4. Implémentations Constant-Time

Une impléplementation **constant-time** s'exécute en temps identique quels que soient les données ou la clé, empêchant les attaques par analyse temporelle.

### Principes

1. **Pas de branchements dépendants du secret** : pas de `if (secret_bit)`, pas de `switch` sur données secrètes
2. **Pas d'accès mémoire indexé par secret** : pas de tableaux indexés par byte secret
3. **Opérations arithmétiques à temps constant** : utiliser uniquement AND, OR, XOR, décalages
4. **Éviter les permutations de bits coûteuses**

### S-box à temps constant

La S-box AES est difficile à implémenter en temps constant à cause de la recherche dans un tableau.

**Approche 1 : T-table avec masquage**
```c
// Combiner SubBytes+ShiftRows+MixColumns en lookup tables
// mais indexer par un mélange de plaintext et masque
uint32_t t0_te0[256];  // Te0 = [02·S(a), 01·S(a), 01·S(a), 03·S(a)]

// Double masquage booléen
uint8_t masked_sbox(uint8_t x, uint8_t mask) {
    // Calculer la S-box sans révéler x via le cache
    uint8_t result = 0;
    for (int i = 0; i < 256; i++) {
        // Dans GF(2⁸) : comparateur constant-time
        uint8_t match = is_equal_ct(x ^ mask, i);
        result |= match & sbox[i];
    }
    return result;
}
```

**Approche 2 : Calcul de l'inverse dans GF(2⁸) par bitslicing**

Technique utilisée par BearSSL et d'autres bibliothèques :

```c
// Bitslicing : 128 chiffrements parallèles, chaque bit de S(a) calculé
// via opérations logiques sur les 8 registres 128-bit
void bitslice_sbox(uint32_t b[8]) {
    // Implémentation selon Boyar-Peralta (2010)
    uint32_t t1, t2, t3, t4, t5, t6, t7, t8;
    // ~24 opérations logiques, pas de lookup table
    // ... (code trop long pour cette référence)
}
```

**Approche 3 : Utiliser AES-NI**
L'instruction `AESENC` est naturellement constant-time.

### Comparaison de chaînes constant-time

```python
import hmac

def constant_time_compare(a: bytes, b: bytes) -> bool:
    """Comparaison à temps constant (évite timing attack)"""
    return hmac.compare_digest(a, b)

# Équivalent manuel
def ct_compare(a: bytes, b: bytes) -> bool:
    if len(a) != len(b):
        return False
    result = 0
    for x, y in zip(a, b):
        result |= x ^ y
    return result == 0
```

---

## 5. Attaques par Canaux Auxiliaires (Side-Channel)

### 5.1 Attaque par analyse temporelle

Exploite les variations de temps d'exécution selon les données.

**Contre-mesure** : code constant-time, blinding.

### 5.2 Attaque par analyse de cache (Cache-Timing)

L'accès à `sbox[secret_byte]` laisse une trace dans le cache L1/L2. Un attaquant peut :
1. **Prime+Probe** : remplir le cache, mesurer l'éviction
2. **Flush+Reload** : surveiller l'accès à une ligne de cache partagée (librairie dynamique)
3. **Evict+Time** : évincer et mesurer le temps de rechargement

**Révélations** : Bernstein (2005) — clé AES extraite via cache-timing en 65ms.

**Contre-mesure** : S-box calculée par bitslicing, utilisation d'AES-NI (instructions atomiques).

### 5.3 Attaque par analyse de consommation (SPA/DPA)

**Simple Power Analysis (SPA)** : lire la clé directement dans le tracé de consommation.

**Differential Power Analysis (DPA)** : statistique sur des centaines de tracés.

**Contre-mesure** :
- **Masquage booléen** : diviser chaque variable secrète en shares `x = x₁ ⊕ x₂ ⊕ ... ⊕ x_d`
- **Masquage multiplicatif** : multiplier par un aléatoire avant l'opération
- **Hiding** : désynchroniser les traces, ajouter du bruit

### 5.4 Attaque par injection de fautes

Modifier un registre ou une mémoire pour obtenir un ciphertext fauté.

**Application à AES** :
- **Single bit fault** : injecter une faute dans le dernier round → peut réduire la clé à 4-8 candidates
- **DFA (Differential Fault Analysis)** : comparer sortie correcte et fautée

**Démonstration** :
```python
# Principe DFA sur AES-128
# Avec une faute 1-byte entre l'avant-dernier et dernier MixColumns
# et 2 paires (correct, fauté), on peut récupérer la clé entière
def dfa_aes_last_round(correct: bytes, faulty: bytes) -> list:
    """Récupère les bytes de clé candidates via DFA"""
    candidates = []
    for byte_pos in range(16):
        d = correct[byte_pos] ^ faulty[byte_pos]
        # Inverse de la S-box
        inv_d = inv_sbox[d]
        # Chaque byte de clé a 4-8 candidats
        byte_candidates = []
        for k in range(256):
            # Vérifier la relation différentielle
            ...
        candidates.append(byte_candidates)
    return candidates
```

---

## 6. AES-GCM-SIV — Chiffrement Nonce-Misuse Resistant

RFC 8452, aussi appelé **AES-GCM-SIV** (SIV = Synthetic Initialization Vector).

### Principe

Contrairement à GCM où la sécurité s'effondre si un nonce est réutilisé (keystream + tag forgé), AES-GCM-SIV utilise une **construction SIV** (RFC 5297) :

```
# 1. MAC sur AAD + plaintext → nonce synthétique
SIV = POLYVAL(K_1, K_2, A, P)

# 2. Chiffrement CTR avec SIV comme compteur
C = AES(K_3, SIV || 0x00000001) ⊕ P || AES(K_3, SIV || 0x00000002) ⊕ P₂ ...

# 3. Sortie
output = SIV || C
```

**Propriétés** :
- **Déterministe** quand même AAD + P + K identiques → pas de fuite de longueur
- **Réutilisation de nonce** → perte de confidentialité uniquement sur le même (AAD, P) quand le nonce est réutilisé pour des messages différents
- Pas de récupération du keystream par l'attaquant

### Usage

```bash
# OpenSSL 3.2+ supporte AES-GCM-SIV
openssl enc -aes-256-gcm-siv -in plain.txt -out cipher.bin \
  -K $(openssl rand -hex 32) -iv $(openssl rand -hex 12)
```

---

## 7. AES Key Wrap (AES-KW)

RFC 3394 — Chiffrement de clés AES par AES.

Utilisé dans PKI pour transporter des clés privées.

```
n = 64 octets de données (6 blocs de 64-bit)
A = IV (0xA6A6A6A6A6A6A6A6)
For j = 0 to 5:
    For i = 1 to n:
        B = AES_K(A | R[i])
        A = MSB(64, B) XOR (n*j + i)
        R[i] = LSB(64, B)
```

---

## 8. Cryptanalyse d'AES

### Force brute

| Version | Clés | Temps (10¹² clés/s) |
|---------|------|---------------------|
| AES-128 | 2¹²⁸ | ~10¹⁹ années |
| AES-192 | 2¹⁹² | ~10³⁰ années |
| AES-256 | 2²⁵⁶ | ~10⁵⁴ années |

### Attaques connues (meilleures)

| Attaque | Cible | Rounds | Complexité |
|---------|-------|--------|------------|
| Square attack | AES-128 | 7/10 | 2¹²⁸ (pas mieux que force brute) |
| Biclique attack | AES-128 | 10/10 | 2¹²⁶·¹⁸ (réduction marginale) |
| Related-key attack | AES-256 | 10/14 | 2⁹⁹·⁵ (non applicable en pratique, modèle trop fort) |
| Side-channel | Tous | ! | Extraction clé complète |

**Conclusion** : AES-128 est sûr contre la cryptanalyse classique. Les meilleures attaques sont marginalement meilleures que la force brute.

### Biclique Attack (Bogdanov et al., 2011)

Première attaque sur AES complet. Utilise des **bicliques** (graphes bipartis) pour partitionner l'espace de clés :

```
Principe : Partitionner 2¹²⁸ clés en 2¹¹² groupes de 2¹⁶
Chaque groupe : 2⁸ clés internes × 2⁸ clés externes
Complexité : 2¹²⁶·¹⁸ appels AES
```

Impact pratique : nul (2¹²⁶·¹⁸ >> 2⁸⁰).

### Meet-in-the-Middle sur AES

Meilleure attaque sur AES-128 à 7 rounds : 2¹⁰⁰ (pas pratique).

---

## 9. Implémentations de Référence

### Bibliothèques C/C++

```c
// OpenSSL EVP (recommandé)
EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, key, iv);

// BearSSL (constant-time, embarqué) — https://bearssl.org
br_aes_ct_ctr_init(&ctx, key, 32);
br_aes_ct_ctr_run(&ctx, iv, data, len);

// libsodium (XChaCha20 plutôt qu'AES, mais compatible AES-NI)
crypto_aead_aes256gcm_encrypt(c, &clen, m, mlen, ad, adlen, NULL, nonce, key);
```

### Python

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM, AESGCMSIV

# Interface simple (recommandée)
aesgcm = AESGCM(key)
ct = aesgcm.encrypt(nonce, data, aad)

# AES-GCM-SIV
aesgcmsiv = AESGCMSIV(key)
ct_siv = aesgcmsiv.encrypt(nonce, data, aad)

# Bas niveau
cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
enc = cipher.encryptor()
enc.authenticate_additional_data(aad)
ct = enc.update(data) + enc.finalize()
```

### Golang

```go
import "crypto/aes"
import "crypto/cipher"

block, _ := aes.NewCipher(key)
gcm, _ := cipher.NewGCM(block)
ct := gcm.Seal(nil, nonce, data, aad)
```

### Rust

```rust
use aes_gcm::{Aes256Gcm, Key, Nonce};
use aes_gcm::aead::{Aead, KeyInit};

let key = Key::<Aes256Gcm>::from_slice(&key_bytes);
let cipher = Aes256Gcm::new(key);
let nonce = Nonce::from_slice(&nonce_bytes);
let ciphertext = cipher.encrypt(nonce, plaintext.as_ref()).unwrap();
```

---

## Références

- **FIPS 197 (AES)** : https://csrc.nist.gov/publications/detail/fips/197/final
- **NIST SP 800-38D (GCM)** : https://csrc.nist.gov/publications/detail/sp/800-38d/final
- **RFC 8452 (AES-GCM-SIV)** : https://datatracker.ietf.org/doc/html/rfc8452
- **AES-NI Whitepaper (Intel)** : https://www.intel.com/content/dam/doc/white-paper/advanced-encryption-standard-new-instructions-set-paper.pdf
- **BearSSL AES constant-time** : https://bearssl.org/constanttime.html
- **Boyar-Peralta S-box bitslicing** : https://eprint.iacr.org/2011/425
- **Biclique Attack on AES** : https://eprint.iacr.org/2011/449
- **Timing Attack on AES (Bernstein)** : https://cr.yp.to/antiforgery/cachetiming-20050414.pdf
