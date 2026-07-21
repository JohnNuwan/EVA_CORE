---
name: ecc-elliptic-curve
description: Guide complet des courbes elliptiques — Weierstrass, Edwards, Montgomery, ECDH, ECDSA, EdDSA, Curve25519, secp256k1, pairings, BLS, et implémentations.
category: cybersecurite
tags: [ecc, elliptic-curve, ecdsa, eddsa, curve25519, secp256k1, bls, pairing, cryptography]
---

# ECC (Elliptic Curve Cryptography) — Guide Approfondi

## Sommaire
1. [Fondements Mathématiques](#fondements-mathématiques)
2. [Formes de Courbes](#formes-de-courbes)
3. [ECDH — Échange de Clés](#ecdh-échange-de-clés)
4. [ECDSA — Signatures](#ecdsa-signatures)
5. [EdDSA et Ed25519](#eddsa-et-ed25519)
6. [Schnorr sur Courbes](#schnorr-sur-courbes)
7. [Pairings et leurs Applications](#pairings-et-leurs-applications)
8. [BLS Signatures](#bls-signatures)
9. [Implémentations Sécurisées](#implémentations-sécurisées)
10. [Attaques sur ECC](#attaques-sur-ecc)

---

## 1. Fondements Mathématiques

### 1.1 Groupe de Points d'une Courbe Elliptique

Une courbe elliptique sur un corps fini F_p est l'ensemble des points `(x, y)` satisfaisant :

**Forme de Weierstrass** : `y² = x³ + ax + b mod p`, avec `4a³ + 27b² ≠ 0 mod p`

Les points forment un **groupe abélien** sous l'addition :
- **Élément neutre** : point à l'infini `O`
- **Opposé** : `-(x, y) = (x, -y)`
- **Addition de points** : règle de la sécante (deux points distincts) ou de la tangente (point doublé)

### 1.2 Addition de Points (Loi de Groupe)

```python
# Sur F_p, forme de Weierstrass y² = x³ + ax + b

def point_add(P1, P2, p):
    """Addition de deux points sur la courbe"""
    if P1 is None:  # Point à l'infini
        return P2
    if P2 is None:
        return P1
    
    x1, y1 = P1
    x2, y2 = P2
    
    if x1 == x2 and y1 != y2:
        return None  # P + (-P) = O
    
    if P1 == P2:
        # Doublement : pente = (3x² + a) / 2y
        m = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
    else:
        # Addition : pente = (y2 - y1) / (x2 - x1)
        m = (y2 - y1) * pow(x2 - x1, -1, p) % p
    
    x3 = (m * m - x1 - x2) % p
    y3 = (m * (x1 - x3) - y1) % p
    
    return (x3, y3)


def point_mul(P, k, p):
    """Multiplication scalaire k·P par double-and-add"""
    result = None
    addend = P
    while k:
        if k & 1:
            result = point_add(result, addend, p)
        addend = point_add(addend, addend, p)
        k >>= 1
    return result
```

### 1.3 Le Problème du Logarithme Discret sur Courbe (ECDLP)

**Définition** : étant donné `P` et `Q = k·P`, trouver `k`.

**Complexité** :
- ECC 256 bits ≈ RSA 3072 bits (sécurité 128 bits)
- ECC 384 bits ≈ RSA 7680 bits (sécurité 256 bits)
- ECC 521 bits ≈ RSA 15360 bits (sécurité ~260 bits)

**Meilleur algorithme classique** : Pollard Rho sur ECC → `O(√n)` où n est l'ordre du générateur.

---

## 2. Formes de Courbes

### 2.1 Weierstrass (secp256k1, P-256, P-384)

Forme standard : `y² = x³ + ax + b`

**secp256k1** (Bitcoin) : `y² = x³ + 7` (a=0, b=7)
- Ordre n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
- Générateur G = (0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798, ...)

**P-256 (secp256r1)** :
- a = -3 mod p
- Standard NIST, utilisé dans TLS

### 2.2 Montgomery (Curve25519)

Forme : `By² = x³ + Ax² + x`

**X25519** : `y² = x³ + 486662·x² + x mod 2²⁵⁵ - 19`

Avantages :
- **Échange de clés en constante de temps** (pas de branchements sur le secret)
- Seule la coordonnée x est transmise (32 octets)
- Multiplication scalaire très rapide (implémentation en ladder de Montgomery)

```python
def montgomery_ladder(k, u, p, A):
    """
    Montgomery Ladder pour X25519.
    Calcule x-coord de k·P en temps constant.
    """
    # A24 = (A+2)/4, P = (A-2)/4
    A24 = (A + 2) * pow(4, -1, p) % p
    
    x1 = u
    x2, z2 = 1, 0  # Point O
    x3, z3 = u, 1  # Point P
    
    for i in range(255, -1, -1):
        bit = (k >> i) & 1
        # Échange constant-time selon le bit
        x2, x3 = cswap(x2, x3, bit)
        z2, z3 = cswap(z2, z3, bit)
        
        # Addition/doublement
        x3, z3 = montgomery_add(x2, z2, x3, z3, x1, p)
        x2, z2 = montgomery_double(x2, z2, A24, p)
        
        # Échange inverse
        x2, x3 = cswap(x2, x3, bit)
        z2, z3 = cswap(z2, z3, bit)
    
    return (x2 * pow(z2, -1, p)) % p
```

### 2.3 Edwards (Ed25519, Ed448)

Forme : `x² + y² = 1 + d·x²·y²` (courbe tordue d'Edwards)

**Ed25519** : `-x² + y² = 1 - 0x52036CEE2B6FFE738CC740797779E89800700A4D4141D8AB75EB4DCA135978A3·x²·y²`

Avantages par rapport à Weierstrass :
- **Addition complète** : pas de cas spéciaux (`P + O`, `P + (-P)`)
- **Addition unifiée** : un seul code pour addition et doublement
- Résistance naturelle aux attaques par canaux auxiliaires

```python
def edwards_add(P1, P2, d, p):
    """Addition sur courbe d'Edwards (formule unifiée)"""
    x1, y1 = P1
    x2, y2 = P2
    
    x3 = (x1*y2 + y1*x2) * pow(1 + d*x1*x2*y1*y2, -1, p) % p
    y3 = (y1*y2 - x1*x2) * pow(1 - d*x1*x2*y1*y2, -1, p) % p
    
    return (x3, y3)
```

### 2.4 Comparaison des Courbes

| Courbe | Forme | Taille clé | Sécurité | Performance | Usage |
|--------|-------|-----------|----------|-------------|-------|
| P-256 | Weierstrass | 256 bits | 128 bits | ~ | TLS, FIPS |
| secp256k1 | Weierstrass | 256 bits | 128 bits | ~ | Bitcoin, ETH |
| X25519 | Montgomery | 256 bits | 128 bits | +++ | TLS 1.3 |
| Ed25519 | Edwards | 256 bits | 128 bits | ++ | Signatures |
| P-384 | Weierstrass | 384 bits | 192 bits | - | Haut niveau |
| X448 | Montgomery | 448 bits | 224 bits | ++ | Future-proof |
| Ed448 | Edwards | 448 bits | 224 bits | ++ | Future-proof |
| secp521r1 | Weierstrass | 521 bits | 256 bits | ~ | Militaire |

---

## 3. ECDH — Échange de Clés

### 3.1 Protocole

Alice et Bob conviennent d'une courbe `(p, a, b, G, n)`.

```
Alice : a_priv ← aléatoire, A_pub = a_priv·G
Bob   : b_priv ← aléatoire, B_pub = b_priv·G
       ── A_pub → 
       ←── B_pub ──
Secret partagé : S = a_priv·B_pub = b_priv·A_pub = a_priv·b_priv·G
```

### 3.2 Implémentation

```python
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# Génération des clés (Alice)
private_key = ec.generate_private_key(ec.SECP256R1())
public_key = private_key.public_key()

# Échange (Bob)
shared_key = private_key.exchange(ec.ECDH(), peer_public_key)

# Dérivation de clé (via HKDF)
derived_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b'handshake data',
).derive(shared_key)
```

### 3.3 X25519 (DH sur Curve25519)

```python
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

alice_private = X25519PrivateKey.generate()
alice_public = alice_private.public_key()

# Sérialisation (32 octets)
alice_public_bytes = alice_public.public_bytes_raw()

# Dé-sérialisation (Bob reçoit la clé publique)
bob_private = X25519PrivateKey.generate()
shared = bob_private.exchange(alice_public)
```

**Important** : X25519 n'utilise pas la coordonnée y — seul le transfert de `x` est nécessaire. Les 32 octets sont la coordonnée x du point.

---

## 4. ECDSA — Signatures

### 4.1 Algorithme

**Signature** :
```python
def ecdsa_sign(m: bytes, d: int, G, n, p, a, b):
    """Signature ECDSA d'un message m avec clé privée d"""
    # 1. Hachage du message
    e = int.from_bytes(hashlib.sha256(m).digest(), 'big')
    
    while True:
        # 2. Nonce aléatoire (KRITIQUE : ne jamais réutiliser !)
        k = secrets.randbelow(n)
        
        # 3. Calcul de R = k·G
        R = point_mul(G, k, p)
        r = R[0] % n
        
        if r == 0:
            continue
        
        # 4. Calcul de s = k⁻¹·(e + r·d) mod n
        s = pow(k, -1, n) * (e + r * d) % n
        
        if s == 0:
            continue
        
        return (r, s)
```

**Vérification** :
```python
def ecdsa_verify(m: bytes, signature, Q, G, n, p, a, b):
    """Vérification d'une signature ECDSA"""
    r, s = signature
    if not (1 <= r < n) or not (1 <= s < n):
        return False
    
    e = int.from_bytes(hashlib.sha256(m).digest(), 'big')
    
    w = pow(s, -1, n)  # s⁻¹ mod n
    u1 = (e * w) % n
    u2 = (r * w) % n
    
    R = point_add(point_mul(G, u1, p), point_mul(Q, u2, p), p)
    
    return R is not None and R[0] % n == r
```

### 4.2 La sensibilité du nonce (k)

**Le nonce k est l'aspect le plus critique d'ECDSA.** Sa réutilisation ou sa prédiction brise totalement la sécurité :

```python
# Si k est réutilisé pour deux signatures avec le même d :
def recover_private_key_biased_nonce(r, s1, s2, e1, e2, n):
    """Récupère la clé privée si deux signatures partagent le même k"""
    # s1 = k⁻¹(e1 + r·d), s2 = k⁻¹(e2 + r·d)
    # s1 - s2 = k⁻¹(e1 - e2) → k = (e1 - e2) / (s1 - s2)
    k = ((e1 - e2) * pow(s1 - s2, -1, n)) % n
    d = ((s1 * k - e1) * pow(r, -1, n)) % n
    return d
```

**Biases non-uniforme** : si k n'est pas uniformément aléatoire (par ex. 3 bits biaisés), un attaquant avec un nombre suffisant de signatures (~2⁵⁰) peut récupérer la clé.

### 4.3 Attaque par fuite de k (Lattice Attack)

Si seulement quelques bits du nonce sont connus (par ex. via side-channel), on utilise des **réseaux** (lattices) :

```
Avec m signatures, on a m équations :
s_i·k_i - r_i·d ≡ e_i (mod n)

Si on connaît les ℓ bits supérieurs de chaque k_i, on forme un SVP
sur un réseau de dimension m+1 pour retrouver d.
```

```python
# Using LLL lattice reduction to recover key from biased nonces
def biased_nonce_attack(signatures, n):
    """
    Attaque par lattice sur ECDSA avec nonces biaisés.
    signatures = [(r_i, s_i, e_i, msb_i)] où msb_i sont bits connus de k_i
    """
    # Construction de la matrice de rang (m+1) × (m+1) puis LLL
    # ...
```

---

## 5. EdDSA et Ed25519

### 5.1 Ed25519 - Algorithme

Ed25519 (RFC 8032) est une variante de Schnorr sur une courbe d'Edwards tordue.

**Génération de clé** :
```
seed = 32 octets aléatoires
a = SHA-512(seed)[:32]  # clampée (clear bits 0,1,2 ; set bit 254)
A = a·B  # clé publique (32 octets, encodage de y)
```

**Signature** :
```
r = SHA-512(nonce || M) mod L   # nonce = dernier 32 octets de SHA-512(seed)
R = r·B
k = SHA-512(R || A || M) mod L
S = r + k·a mod L
Signature = R || S (64 octets)
```

**Vérification** :
```
S·B = R + k·A  ?  k = SHA-512(R || A || M)
```

**Avantages sur ECDSA** :
- **Déterministe** : nonce basé sur seed + message → pas de problème de RNG
- **Plus rapide** : pas d'inversion modulaire
- **Batch verification** : vérifier N signatures ensemble coûte moins que N fois

### 5.2 Implémentation

```python
# Python avec PyNaCl (libsodium)
import nacl.signing
import nacl.encoding

# Génération
key_pair = nacl.signing.SigningKey.generate()
signing_key = key_pair  # 32 octets seed
verify_key = key_pair.verify_key  # 32 octets

# Signature
signed = signing_key.sign(b"Message to sign")

# Vérification
try:
    verify_key.verify(signed)
    print("Signature valide")
except nacl.exceptions.BadSignatureError:
    print("Signature invalide")
```

### 5.3 Batch Verification (Ed25519)

```python
def batch_verify(signatures, messages, public_keys, B, L):
    """
    Vérification par lot Ed25519.
    Vérifie n signatures avec ~n·1.25× coût d'une seule.
    """
    import random
    
    # Tire des coefficients aléatoires z_i
    z = [random.randint(1, 2**128) for _ in range(len(signatures))]
    
    # Calcule ∑ z_i·S_i·B
    left = point_mul(B, sum(z_i * S_i for z_i, (_, S_i) in zip(z, signatures)), L)
    
    # Calcule ∑ z_i·(R_i + k_i·A_i)
    right = None
    for z_i, (R_i, S_i), A_i, k_i in zip(z, signatures, public_keys, ks):
        term = point_add(R_i, point_mul(A_i, (z_i * k_i) % L))
        if right is None:
            right = point_mul(term, z_i, L)
        else:
            right = point_add(right, point_mul(term, z_i, L))
    
    return left == right
```

---

## 6. Schnorr sur Courbes

### 6.1 Signature Schnorr

Plus simple qu'ECDSA, avec de meilleures propriétés.

**Principe** :
```
Génération : clé privée x, publique P = x·G
Signature :
  k ← aléatoire, R = k·G
  e = H(R || M || P)
  s = k + x·e mod n
  Signature = (s, e) ou (s, R)

Vérification : R' = s·G - e·P, vérifier e = H(R' || M || P)
```

**Avantages** :
- **Linéarité** : `(s₁ + s₂, R₁ + R₂)` est une signature valide pour `(M₁, M₂)` — permet l'agrégation
- **Preuve de connaissance** : prouve qu'on connaît `x` sans le révéler
- Implémenté dans Bitcoin (Taproot / Schnorr BIP 340)

### 6.2 MuSig — Signature Multi-Signature

Agrège N signatures Schnorr en une seule (Cryptocurrency applications) :

```python
def musig_sign(private_keys, public_keys, message, G, n):
    """Signature MuSig : agrège n signatures Schnorr"""
    # 1. Calcul de l'agrégation : P = ∑ H_agg(L || P_i) · P_i
    L = H_agg(public_keys)
    coefficients = [H_agg(L || P_i) for P_i in public_keys]
    P_agg = sum(c * P_i for c, P_i in zip(coefficients, public_keys))
    
    # 2. Nonces agrégés : R = ∑ R_i
    # 3. Signature partielle : s_i = k_i + H(R || P_agg || M) · c_i · x_i
    e = H_agg(R || P_agg || M)
    s_total = sum(s_i) % n
    
    return (R, s_total, P_agg)
```

**Propriétés** :
- Taille constante quel que soit le nombre de signataires
- Pas de preuve de connaissance nécessaire (contrairement à BLS)
- Sécurité prouvée dans le modèle de l'oracle aléatoire

---

## 7. Pairings et leurs Applications

### 7.1 Qu'est-ce qu'un Pairing ?

Fonction bilinéaire `e : G₁ × G₂ → G_T` avec :
- `e(a·P, b·Q) = e(P, Q)^{ab}`  (bilinéarité)
- Non-dégénéré : `e(P, Q) ≠ 1`

**Types de pairings :**
- **Type 1** : G₁ = G₂ (symmetric pairing, obsolète)
- **Type 3** : G₁ ≠ G₂, pas d'isomorphisme connu (standard actuel)

### 7.2 Courbes avec Pairing

| Courbe | Sécurité | Bits | Usage |
|--------|----------|------|-------|
| BN256 (Barreto-Naehrig) | 128 | 256 | Ethereum BLS, ZK |
| BLS12-381 | 128 | 381 | Ethereum 2.0, BLS |
| BN384 | 192 | 384 | Haut niveau |
| BLS48 | 256 | 576 | Militaire |

**BLS12-381** : utilisée dans Ethereum 2.0
- G₁ sur `y² = x³ + 4` (Fp)
- G₂ sur une extension de corps Fp²
- G_T ⊆ Fp¹²
- Embedding degree k = 12

### 7.3 Implémentation (avec py_ecc / blspy)

```python
# BLS12-381 Signatures via py-ecc
from py_ecc.bls import G2Basic

# Key generation
private_key = 123456  # 32 bytes
public_key = G2Basic.sk_to_pk(private_key)

# Sign
message = b"Hello, world!"
signature = G2Basic.Sign(private_key, message)

# Verify
G2Basic.Verify(public_key, message, signature)
```

---

## 8. BLS Signatures

### 8.1 Principe

Signature basée sur les pairings : **Boneh–Lynn–Shacham**.

```
Clé : privée sk ∈ Z_p, publique pk = sk·G₁
Sign : σ = sk·H(m)   dans G₁
Verify : e(pk, H(m)) = e(G₁, σ)
```

**Propriété clé** : **agrégation de signatures**

```python
def bls_aggregate(signatures):
    """Agrège plusieurs signatures BLS en une seule"""
    return sum(signatures)  # simple addition dans G₁

def bls_aggregate_verify(public_keys, messages, signature_agg, G1, G2):
    """Vérifie une signature BLS agrégée"""
    # Pour des messages identiques :
    # e(pk₁·H(M) + pk₂·H(M), G₂) = e(pk₁ + pk₂, H(M))
    pk_agg = sum(public_keys)
    return pairing(pk_agg, H(messages[0])) == pairing(G1, signature_agg)
```

### 8.2 Applications

**Ethereum 2.0** :
- Un validateur propose un bloc → produit une signature BLS
- Des milliers d'attestations sont agrégées en une seule signature (96 octets)
- Vérification d'un bloc entier : O(log n) pairings

### 8.3 Rogue Key Attack et Défense

Les signatures BLS sont vulnérables à l'attaque « rogue key » sans preuve de connaissance de la clé privée :

```python
# Attaque : un attaquant avec clé pk_2 peut annoncer pk_rogue = pk_2 - pk_1
# → pk_1 + pk_rogue = pk_2 → l'attaquant signe seul

# Défense : Preuve de Possession (PoP)
# Chaque participant prouve connaître sk via une signature de sa clé publique
pop = bls_sign(sk_i, pk_i)
```

---

## 9. Implémentations Sécurisées

### Libsodium (recommandé pour production)

```bash
pip install pynacl
```

```python
import nacl.bindings as sodium

# X25519 key exchange
alice_sk = sodium.crypto_scalarmult_base(secrets.token_bytes(32))
# (X25519: clamp bits 0,1,2, set bit 254)
alice_sk = bytes([alice_sk[0] & 248] + list(alice_sk[1:31]) + [alice_sk[31] | 64])

pk = sodium.crypto_scalarmult_base(alice_sk)  # 32 bytes
```

### OpenSSL

```bash
# Générer clé ECDSA P-256
openssl ecparam -name prime256v1 -genkey -noout -out private.pem

# Extraire publique
openssl ec -in private.pem -pubout -out public.pem

# Afficher les paramètres
openssl ec -in private.pem -text -noout

# Signer avec ECDSA
openssl pkeyutl -sign -in message.txt -inkey private.pem \
  -pkeyopt digest:sha256 -out signature.bin

# Vérifier
openssl pkeyutl -verify -in message.txt -pubin -inkey public.pem \
  -sigfile signature.bin -pkeyopt digest:sha256

# Afficher la courbe
openssl ecparam -list_curves | grep -E "prime|secp"
```

### OpenSSH avec Ed25519

```bash
# Générer une clé Ed25519 (OpenSSH 6.5+)
ssh-keygen -t ed25519 -a 100

# Liste des courbes supportées
ssh-keygen -Q
```

### Python (cryptography)

```python
from cryptography.hazmat.primitives.asymmetric import ec, ed25519

# ECDSA P-256
ec_private = ec.generate_private_key(ec.SECP256R1())
signature = ec_private.sign(message, ec.ECDSA(hashes.SHA256()))

# Ed25519
ed_private = ed25519.Ed25519PrivateKey.generate()
signature = ed_private.sign(message)
ed_private.public_key().verify(signature, message)

# X25519 key exchange
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
x_private = X25519PrivateKey.generate()
shared = x_private.exchange(peer_public_x25519)
```

---

## 10. Attaques sur ECC

### 10.1 Attaque sur le nonce (biases ECDSA)

Voir section 4.2 — **la plus importante** en pratique.

### 10.2 Attaque Invalid Curve

L'attaquant envoie un point qui n'est pas sur la courbe :

```python
def invalid_curve_attack(curve, target_private_key_B, G, n, p, a, b):
    """
    Envoie un point Q qui n'est pas sur la courbe.
    L'adversaire peut récupérer des infos sur la clé privée.
    """
    # Choisir un point Q sur une courbe faible
    # où le logarithme discret est trivial
    # → révélation partielle de la clé B
    cursed_point = (x, y)  # où y² ≠ x³ + ax + b mod p
    Q = point_add(cursed_point, cursed_point)  # sur une autre courbe
    
    # Bob calcule sk_B·Q → on peut récupérer sk_B mod small_order(Q)
    shared = target_private_key_B * Q
    # Avec plusieurs tels points → CRT → clé complète
```

**Contre-mesure** : Vérifier que `y² ≡ x³ + ax + b (mod p)` pour chaque point reçu.

### 10.3 Attaque Twist

Variante de l'invalid curve pour X25519 :
- Curve25519 accepte n'importe quelle coordonnée x
- La coordonnée `x = 5` peut être sur la twist `2·y² = x³ + 486662·x² + x`
- Le ladder de Montgomery calcule `k·x_curve` même si `x` est invalide

**Protection dans X25519** : la multiplication scalaire avec n'importe quelle entrée est sécurisée car le meilleur log discret sur la twist est aussi ~128 bits.

### 10.4 Attaque Pollard Rho sur ECDLP

```python
def pollard_rho_ecdlp(P, Q, G, n, p, a, b):
    """
    Pollard Rho pour ECDLP : trouver k tel que Q = k·P.
    Complexité : O(√n) avec n = ordre de G.
    """
    def f(point):
        # Point → partition en 3 ensembles
        return point
    
    # Tortue et lièvre
    a1, b1 = 0, 0  # indices dans le groupe
    a2, b2 = 0, 0
    R1 = None  # a1·P + b1·Q
    R2 = None  # a2·P + b2·Q
    
    while True:
        # Avancer la tortue (1 pas)
        R1 = f(R1)  # avec mise à jour de a1, b1
        
        # Avancer le lièvre (2 pas)
        R2 = f(R2)
        R2 = f(R2)  # avec mise à jour de a2, b2
        
        if R1 == R2:
            # Collision : a1·P + b1·Q = a2·P + b2·Q
            # (a1 - a2)·P = (b2 - b1)·Q
            # k = (a1 - a2)·(b2 - b1)^{-1} mod n
            return ((a1 - a2) * pow(b2 - b1, -1, n)) % n
```

**Complexité pour P-256** : 2¹²⁸ opérations → impossible. Pour des courbes de 128 bits : ~2⁶⁴ opérations → à la limite du réalisable (clusters de GPU/ASIC).

### 10.5 Quantum Threat (Algorithme de Shor)

L'algorithme de Shor casse ECDLP en temps polynomial `O(log³ n)` sur un ordinateur quantique.

**Conséquences** : ECC-256 est cassée par ~2330 qubits logiques (6·10⁶ qubits physiques avec correction d'erreur).

**Échéance estimée** : 15-25 ans pour des clés de 256 bits.

---

## Références

- **RFC 7748 (Curve25519, Curve448)** : https://datatracker.ietf.org/doc/html/rfc7748
- **RFC 8032 (EdDSA, Ed25519, Ed448)** : https://datatracker.ietf.org/doc/html/rfc8032
- **BIP 340 (Schnorr Bitcoin)** : https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki
- **BLS Signatures (Ethereum)** : https://eips.ethereum.org/EIPS/eip-2333
- **SafeCurves (courbes sécurisées)** : https://safecurves.cr.yp.to
- **Pollard Rho for ECDLP** : https://cr.yp.to/papers.html#ecdlp
- **Invalid Curve Attack** : https://link.springer.com/chapter/10.1007/3-540-46416-6_1
- **BLS Signatures (Boneh-Lynn-Shacham)** : https://eprint.iacr.org/2002/088
- **MuSig Paper** : https://eprint.iacr.org/2018/068