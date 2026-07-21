---
name: rsa-cryptography
description: Guide complet du chiffrement RSA — génération de clés, OAEP, PSS, CRT, multi-prime, timing attacks, blinding, threshold RSA, padding oracles, et implémentations sécurisées.
category: cybersecurite
tags: [rsa, asymmetric-crypto, oaep, pss, crt, threshold-crypto, public-key, cryptography, openssl]
---

# RSA — Guide Approfondi

## Sommaire
1. [Fondements Mathématiques](#fondements-mathématiques)
2. [Génération de Clés Sécurisée](#génération-de-clés-sécurisée)
3. [Padding : OAEP et PSS](#padding-oaep-et-pss)
4. [CRT — Théorème des Restes Chinois](#crt-optimisation)
5. [Multi-Prime RSA](#multi-prime-rsa)
6. [Attaques sur RSA](#attaques-sur-rsa)
7. [Blinding et Contre-Mesures](#blinding-et-contre-mesures)
8. [Threshold RSA](#threshold-rsa)
9. [Implémentations et Outils](#implémentations-et-outils)

---

## 1. Fondements Mathématiques

### 1.1 L'One-Way Trapdoor Function

RSA repose sur la difficulté de factoriser le produit de deux grands nombres premiers.

**Fonction à sens unique (one-way)** :
- Facile : `c = m^e mod n`
- Difficile sans `d` : inverser `c^d = m mod n` sans connaître `φ(n)`

**Trapdoor** : connaître `d` (l'exposant privé) permet de déchiffrer.

### 1.2 Le Théorème d'Euler

```
Si gcd(m, n) = 1 :  m^{φ(n)} ≡ 1 (mod n)
```

Pour RSA : `n = p × q`, donc `φ(n) = (p-1)(q-1)`

**Chiffrement :** `E(m) = m^e mod n`
**Déchiffrement :** `D(c) = c^d mod n = m^{e·d} mod n = m^{k·φ(n)+1} mod n = m mod n`
grâce à Euler si `e·d ≡ 1 mod φ(n)`

### 1.3 Le Théorème des Restes Chinois (CRT)

Pour `n = p × q`, on peut résoudre `m mod n` via `m mod p` et `m mod q` :
```
m_p = c^{d mod (p-1)} mod p
m_q = c^{d mod (q-1)} mod q
m = CRT(m_p, m_q) = m_p + p · ((m_q - m_p) · p^{-1} mod q)
```

---

## 2. Génération de Clés Sécurisée

### 2.1 Algorithme

```python
import secrets
from math import gcd

def generate_rsa_keypair(bits: int = 4096, e: int = 65537):
    """
    Génère une paire de clés RSA sécurisée.
    
    Args:
        bits: Taille du module n (recommandé : 2048 min, 4096 recommandé)
        e: Exposant public (Fermat F4 = 2¹⁶+1, standard)
    """
    while True:
        # Générer deux nombres premiers de bits/2 bits
        p = generate_prime(bits // 2)
        q = generate_prime(bits // 2)
        
        n = p * q
        phi = (p - 1) * (q - 1)
        
        # e doit être coprime avec φ(n)
        if gcd(e, phi) != 1:
            continue
        
        d = mod_inverse(e, phi)
        
        # Vérification : e·d ≡ 1 mod φ(n)
        assert (e * d) % phi == 1
        
        return {
            'public': {'n': n, 'e': e},
            'private': {'n': n, 'd': d, 'p': p, 'q': q}
        }

def generate_prime(bits: int) -> int:
    """Génération d'un nombre premier sécurisé"""
    while True:
        candidate = secrets.randbits(bits)
        candidate |= (1 << (bits - 1)) | 1  # Bit MSB et LSB à 1
        
        # Tests de primalité
        if not miller_rabin(candidate, k=128):  # ²⁷ erreur < 2⁻²⁵⁶
            continue
        if not lucas_test(candidate):  # Élimine les Carmichael
            continue
        return candidate
```

### 2.2 Tests de primalité

**Miller-Rabin** (probabiliste) :

```python
def miller_rabin(n: int, k: int = 64) -> bool:
    """Test de primalité Miller-Rabin. Erreur < 4^{-k}"""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    
    # n - 1 = 2^s · d
    s, d = 0, n - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        
        if x == 1 or x == n - 1:
            continue
        
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False  # Témoin de non-primalité
    
    return True
```

**Test déterministe pour < 2⁶⁴ :**
- Si `n < 2⁶⁴`, tester avec `a ∈ {2, 3, 5, 7, 11, 13, 17}` suffit (Pomerance-verified).

### 2.3 Taille de clés recommandée

| Niveau | Clé RSA | Sécurité (bits) | Comparable symétrique |
|--------|---------|-----------------|----------------------|
| Minimum | 2048 | 112 | AES-112 |
| Standard | 3072 | 128 | AES-128 |
| Recommandé | 4096 | 140 | AES-140 |
| Long terme | 8192 | 180 | AES-180 |
| NIST 2030+ | 3072+ | 128+ | AES-128+ |

**Relation taille/sécurité** : factoriser `n = 2048 bits` nécessite ~10¹² MIPS-années.

### 2.4 Cas pathologiques à éviter

```python
def validate_rsa_key(n, e, d, p, q):
    """Vérifications de sécurité sur une paire RSA"""
    assert n.bit_length() >= 2048
    assert e > 2**16  # Exposant public assez grand
    assert e < 2**256
    assert d > n.bit_length() // 2  # Exposant privé pas trop petit
    
    # p et q ne doivent pas être trop proches (Fermat factorization)
    assert abs(p - q).bit_length() > n.bit_length() // 2 - 100
    
    # p-1 et q-1 ne doivent pas avoir que des petits facteurs
    # (Pollard p-1)
    assert gcd(p-1, 65537) == 1  # Au moins une petite vérification
    
    # Vérification du CRT
    dp = d % (p-1)
    dq = d % (q-1)
    qinv = pow(q, p-2, p)
    assert (e * dp) % (p-1) == 1
    assert (e * dq) % (q-1) == 1
```

---

## 3. Padding : OAEP et PSS

### 3.1 Pourquoi le padding est crucial

Sans padding, RSA est déterministe et vulnérable :
- **Attaque de texte clair choisi** : l'attaquant peut déchiffrer en comparant `c = m^e mod n`
- **Malleability** : `E(m₁)·E(m₂) = E(m₁·m₂)`
- **Attaque de message court** : si `m < n^(1/e)`, `m = c^(1/e)` (racine e-ième exacte)

### 3.2 RSA-OAEP (Optimal Asymmetric Encryption Padding)

RFC 8017, standard pour le chiffrement.

```
┌─────────────────────────────────┬────────┬──────────────┐
│   mHash (hash du label)         │  PS    │    M          │
│       (hLen octets)             │(0 ou +)│ (message)     │
└─────────────────────────────────┴────────┴──────────────┘
                              ↓ XOR avec DB mask
         ┌──────────────────────────────────────────────────┐
         │          maskedDB                                  │
         │     (n - hLen - 1 octets)                         │
         └──────────────────────────────────────────────────┘
         ↑ graine aléatoire XOR seed mask
         ┌─────────┬────────────────────────────────────────┐
         │  maskedSeed │       maskedDB                     │
         │  (hLen)     │                                    │
         └─────────┴────────────────────────────────────────┘
```

**Pseudo-code :**
```python
def oaep_encode(M: bytes, label: bytes, n: int, hash_func=hashlib.sha256):
    """
    Encode M avec OAEP pour RSA.
    n : taille du module RSA en octets
    """
    k = (n.bit_length() + 7) // 8  # octets du module
    hLen = hash_func().digest_size
    mLen = len(M)
    
    assert mLen <= k - 2 * hLen - 2
    
    # 1. Hacher le label
    lHash = hash_func(label).digest()
    
    # 2. Construire DB = lHash || PS || 0x01 || M
    PS = b'\x00' * (k - mLen - 2 * hLen - 2)
    DB = lHash + PS + b'\x01' + M
    
    # 3. Graine aléatoire
    seed = secrets.token_bytes(hLen)
    
    # 4. MGF1 (Mask Generation Function) : génère un masque de la bonne taille
    dbMask = mgf1(seed, k - hLen - 1, hash_func)
    
    # 5. Masquer DB
    maskedDB = xor_bytes(DB, dbMask)
    
    # 6. Masquer la graine
    seedMask = mgf1(maskedDB, hLen, hash_func)
    maskedSeed = xor_bytes(seed, seedMask)
    
    # 7. EM = 0x00 || maskedSeed || maskedDB
    EM = b'\x00' + maskedSeed + maskedDB
    return EM

def mgf1(seed: bytes, length: int, hash_func) -> bytes:
    """MGF1 : Mask Generation Function basée sur un hash"""
    result = b''
    counter = 0
    while len(result) < length:
        c = counter.to_bytes(4, 'big')
        result += hash_func(seed + c).digest()
        counter += 1
    return result[:length]
```

### 3.3 RSA-PSS (Probabilistic Signature Scheme)

Standard pour les signatures RSA (remplace PKCS#1 v1.5 signature).

```
┌────────────────────────────────────────────────────────┐
│                 mHash                                    │
│            (hash du message)                             │
└──────────────────────────┬─────────────────────────────┘
                           ↓
   salt aléatoire →  ┌──────────────────────┐
                     │  M' = padding1 ||    │
                     │  mHash || salt       │
                     └──────────────────────┘
                           ↓ hash
                     ┌───────────┐
                     │    H      │
                     └───────────┘
┌────────────────────────────────────────────────────────┐
│ DB = padding2 || salt                                    │
└────────────────────────────────────────────────────────┘
                           ↓
                     ┌───────────┐
                     │  DBMask   │  ← MGF1(H)
                     └───────────┘
                           ↓
                     maskedDB = DB ⊕ DBMask
                     
                     EM = 0xBC || maskedDB || H || 0xBC
```

**Utilisation :**
```bash
# Signature RSA-PSS avec SHA-256
openssl pkeyutl -sign -in message.txt -inkey private.pem \
  -pkeyopt digest:sha256 -pkeyopt rsa_padding_mode:pss \
  -out signature.bin

# Vérification
openssl pkeyutl -verify -in message.txt -pubin -inkey public.pem \
  -sigfile signature.bin \
  -pkeyopt digest:sha256 -pkeyopt rsa_padding_mode:pss
```

### 3.4 Comparaison des schémas de padding

| Schéma | Usage | Sécurité | Remarque |
|--------|-------|----------|----------|
| PKCS#1 v1.5 encrypt | Chiffrement | Vulnérable (Bleichenbacher) | Obsolète, ne PAS utiliser |
| OAEP | Chiffrement | IND-CCA2 (sécurisé) | Standard actuel |
| PKCS#1 v1.5 sign | Signature | Vulnérable (forgery) | Obsolète |
| PSS | Signature | EUF-CMA (sécurisé) | Preuve de sécurité formelle |

---

## 4. CRT — Optimisation

### 4.1 Principe

Utilise le Théorème des Restes Chinois pour accélérer le déchiffrement (~4× plus rapide).

Au lieu de `m = c^d mod n` (coût O(k³)), on calcule :

```python
def crt_decrypt(c: int, p: int, q: int, dp: int, dq: int, qinv: int) -> int:
    """
    Déchiffrement RSA via CRT.
    dp = d mod (p-1)
    dq = d mod (q-1)
    qinv = q⁻¹ mod p
    """
    m1 = pow(c, dp, p)
    m2 = pow(c, dq, q)
    h = (qinv * (m1 - m2)) % p
    return m2 + h * q
```

### 4.2 Attaques sur l'implémentation CRT

**Bellcore Attack (1996)** : injection de faute sur `m₁` ou `m₂` → signature fautée permet de retrouver `p`.

```python
# Si m1_faulty est fauté mais pas m2 :
#   m_faulty = m2 + h_faulty * q
#   gcd(c - m_faulty^e, n) ⟹ q
# ou gcd(m_sig - m_sig_faulty, n) ⟹ p/q
```

**Contre-mesure** : vérifier la signature avant de la renvoyer.

```python
def crt_sign_verify(c, d, n, p, q, dp, dq, qinv):
    """Signature CRT avec vérification contre les fautes"""
    # Signature via CRT
    signature = crt_decrypt(c, p, q, dp, dq, qinv)
    
    # Vérification : c = signature^e mod n ?
    check = pow(signature, e, n)
    if check != c:
        raise ValueError("Attaque par injection de faute détectée !")
    
    return signature
```

---

## 5. Multi-Prime RSA

Variante où `n = p₁ · p₂ · ... · p_k` avec k > 2.

**Avantage** : déchiffrement plus rapide (CRT avec k restes).
**Inconvénient** : moins de sécurité à module égal (plus de facteurs premiers → ECM s'améliore).

```python
def multi_prime_gen(k: int = 3, bits_per_prime: int = 1024) -> dict:
    """Génère une clé RSA multi-premier"""
    primes = [generate_prime(bits_per_prime) for _ in range(k)]
    n = 1
    for p in primes:
        n *= p
    
    phi = 1
    for p in primes:
        phi *= (p - 1)
    
    e = 65537
    d = mod_inverse(e, phi)
    
    # CRT : tous les restes
    crt_info = []
    for p in primes:
        crt_info.append({
            'p': p,
            'dp': d % (p - 1),
            'qinv': pow(n // p, p - 2, p)  # inverse du produit des autres
        })
    
    return n, e, d, crt_info
```

**Usage** : certains certificats utilisent 3-4 facteurs (déprécié pour les nouvelles clés).

---

## 6. Attaques sur RSA

### 6.1 Attaque sur petit exposant privé (Wiener, 1990)

Si `d < n^{0.25}/3`, on peut retrouver `d` via les fractions continues de l'algorithme d'Euclide étendu.

**Détection** : dans l'équation `e·d ≡ 1 mod φ(n)`, `e·d = 1 + k·φ(n)`
→ `e/φ(n) ≈ k/d` → développement en fractions continues de `e/n`.

```python
def wiener_attack(e, n):
    """Attaque de Wiener : retrouve d si d < n^0.25/3"""
    # Développement en fractions continues de e/n
    cf = continued_fraction(e, n)
    
    for k, d in cf:
        if d == 0:
            continue
        if (e * d - 1) % k != 0:
            continue
        
        phi = (e * d - 1) // k
        # Résoudre p+q = n - φ + 1, p·q = n
        # → polynôme x² - (n-φ+1)x + n = 0
        b = n - phi + 1
        discriminant = b*b - 4*n
        if discriminant < 0:
            continue
        sqrt_d = isqrt(discriminant)
        if sqrt_d * sqrt_d == discriminant:
            return d, (b - sqrt_d) // 2  # p
    return None
```

### 6.2 Attaque par petit exposant public (Coppersmith, 1996)

Si `m` est court et `e` petit, `c = m^e mod n ≈ m^e` (pas de réduction modulaire).

**Attaque de diffusion de message** : si `m` est envoyé à `e` destinataires avec `e` clés différentes, on peut retrouver `m` via le CRT.

```
c₁ = m³ mod n₁
c₂ = m³ mod n₂
c₃ = m³ mod n₃

→ m³ = CRT(c₁, c₂, c₃) mod (n₁·n₂·n₃)
→ m = racine cubique exacte
```

### 6.3 Attaque de Hastad (Broadcast Attack)

Si un message est chiffré avec `e` clés publiques `(n_i, e)` et `gcd(n_i, n_j) = 1` :

```python
def hastad_attack(ciphertexts, moduli, e=3):
    """Attaque de Hastad (broadcast)"""
    from functools import reduce
    
    # CRT pour reconstruire m^e
    M = crt_compose(ciphertexts, moduli)
    
    # Racine e-ième entière
    m = integer_nth_root(M, e)
    return m
```

### 6.4 Attaque par module partagé

Si deux clés partagent le même `n` avec des `e` différents :
```python
def common_modulus_attack(n, e1, e2, c1, c2):
    """
    Si deux messages sont chiffrés avec le même n mais e1 et e2
    avec gcd(e1, e2) = 1.
    """
    g, u, v = extended_gcd(e1, e2)
    # u·e1 + v·e2 = 1
    # m = c1^u · c2^v mod n
    if u < 0:
        c1 = mod_inverse(c1, n)
        u = -u
    if v < 0:
        c2 = mod_inverse(c2, n)
        v = -v
    return (pow(c1, u, n) * pow(c2, v, n)) % n
```

### 6.5 Bleichenbacher Attack (Million Message Attack)

**Cible** : PKCS#1 v1.5 encryption (oracle de padding).

**Principe** : l'attaquant envoie `c' = c · s^e mod n` et observe si le déchiffrement produit un padding PKCS#1 valide (les 2 premiers octets = 0x0002).

**Complexité** : ~2²⁰ (1 million) requêtes pour déchiffrer un message. Réduit à ~21500 avec des optimisations.

**Contre-mesure** : utiliser OAEP ou interdire les oracles de padding.

### 6.6 Attaque ROCA (CVE-2017-15361)

Vulnérabilité dans les clés RSA générées par les bibliothèques Infineon (TPM, cartes à puce).

**Cause** : les nombres premiers `p` et `q` sont de la forme `k·M + t` avec `M = P_n#` (primorielle) et `t` petit.

**Détection** :
```bash
pip install roca-detect
python -m roca_detect public_key.pem
```

### 6.7 Factorisation du module

| Algorithme | Complexité | Taille maximale (2024) |
|------------|------------|----------------------|
| GNFS (General Number Field Sieve) | L_n[1/3, (64/9)^(1/3)] | ~1024 bits (record 795 bits, 2019) |
| ECM (Elliptic Curve Method) | L_p[1/2, √2] | ~256 bits par facteur |
| Pollard p-1 | O(B·log B·log²n) | petits facteurs de p-1 |
| Pollard Rho | O(√p) | ~128 bits |

**Record 2024** : factorisation d'un nombre RSA-795 (250 décimales, ~2600 CPU-années).

### 6.8 Attaques par canaux auxiliaires

Voir la section [Blinding](#blinding-et-contre-mesures) pour les contre-mesures.

---

## 7. Blinding et Contre-Mesures

### 7.1 Blinding pour le déchiffrement

Protège contre les attaques par mesure temporelle (timing) où l'attaquant choisit `c` et mesure le temps de `c^d mod n`.

```python
def decrypt_blinded(c: int, d: int, n: int) -> int:
    """
    Déchiffrement RSA avec blinding.
    L'attaquant ne contrôle pas l'entrée réelle de l'exponentiation.
    """
    # 1. Choisir r aléatoire
    r = secrets.randbelow(n)
    while gcd(r, n) != 1:
        r = secrets.randbelow(n)
    
    # 2. Blinder : c' = c · r^e mod n
    c_blinded = (c * pow(r, e, n)) % n
    
    # 3. Déchiffrer (l'exponentiation est sur c_blinded)
    m_blinded = pow(c_blinded, d, n)
    
    # 4. Unblind : m = m_blinded · r^{-1} mod n
    r_inv = mod_inverse(r, n)
    m = (m_blinded * r_inv) % n
    
    return m
```

### 7.2 Square-and-Multiply Always

Protège contre les SPA (Simple Power Analysis) :

```python
def exp_always_multiply(base, exp, mod):
    """
    Exponentiation modulaire à temps constant.
    Toujours multiplier, même si bit = 0.
    """
    result = 1
    for bit in bin(exp)[2:]:
        result = (result * result) % mod
        if bit == '1':
            result = (result * base) % mod
        else:
            # Opération factice (à optimiser par le matériel)
            _ = (base * result) % mod  # squaring factice
    return result
```

### 7.3 Montgomery Multiplication

Optimisation pour les multiplications modulaires fréquentes :

```python
def montgomery_reduce(T, N, R_inv, N_prime):
    """
    Réduction de Montgomery.
    Calcule T·R^{-1} mod N sans division.
    """
    m = ((T & (R-1)) * N_prime) & (R-1)
    t = (T + m * N) >> log2(R)
    if t >= N:
        t -= N
    return t
```

---

## 8. Threshold RSA

Permet de distribuer la clé privée entre `n` parties dont `k` suffisent pour déchiffrer/signer.

### 8.1 Principe (Shamir Secret Sharing + RSA)

```python
from secrets import randbelow

def distribute_rsa_key(d, n, k, num_parts):
    """
    Distribue d via le schéma de Shamir.
    k parts suffisent pour recomposer d.
    """
    # Coefficient du polynôme de degré k-1
    a = [d]
    for _ in range(k-1):
        a.append(randbelow(n))
    
    # Évaluer aux points 1..num_parts
    shares = []
    for i in range(1, num_parts + 1):
        share = 0
        for j in range(k):
            share = (share + a[j] * pow(i, j, n)) % n
        shares.append(share)
    
    return shares  # Partie i : (i, shares[i])
```

### 8.2 RSA avec signature distribuée

Chaque partie calcule `sig_i = m^{d_i} mod n` ; le combinateur reconstruit via CRT :

```python
def combine_signatures(m, signatures, indices, n):
    """Combine k signatures RSA partielles via Lagrange"""
    # Interpolation de Lagrange dans l'exposant
    s = 1
    for i, sig_i in zip(indices, signatures):
        lambda_i = 1
        for j in indices:
            if j != i:
                # λ_i = ∏_{j≠i} j/(j-i) mod φ(n)
                lambda_i *= j * pow(j - i, -1, n)
        s = (s * pow(sig_i, lambda_i, n)) % n
    return s
```

---

## 9. Implémentations et Outils

### OpenSSL

```bash
# Générer clé RSA 4096 avec exposant F4
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 \
  -pkeyopt rsa_keygen_pubexp:65537 -out private.pem

# Extraire la publique
openssl pkey -in private.pem -pubout -out public.pem

# Voir les paramètres
openssl pkey -in private.pem -text -noout

# Chiffrer avec RSA-OAEP
openssl pkeyutl -encrypt -pubin -inkey public.pem \
  -pkeyopt rsa_padding_mode:oaep \
  -pkeyopt rsa_oaep_md:sha256 \
  -pkeyopt rsa_mgf1_md:sha256 \
  -in plaintext.txt -out ciphertext.bin

# Signer avec RSA-PSS
openssl pkeyutl -sign -in message.txt -inkey private.pem \
  -pkeyopt digest:sha384 \
  -pkeyopt rsa_padding_mode:pss \
  -pkeyopt rsa_pss_saltlen:64 \
  -out signature.bin

# Vérifier la force d'une clé
openssl rsa -in private.pem -check -noout
```

### Python (cryptography)

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

# Génération
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=4096,
)
public_key = private_key.public_key()

# Signature RSA-PSS
signature = private_key.sign(
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA384()),
        salt_length=64
    ),
    hashes.SHA384()
)

# Vérification
public_key.verify(
    signature,
    message,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA384()),
        salt_length=64
    ),
    hashes.SHA384()
)

# Chiffrement OAEP
ciphertext = public_key.encrypt(
    plaintext,
    padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()),
        algorithm=hashes.SHA256(),
        label=None
    )
)

# Export PEM
pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.BestAvailableEncryption(b"password")
)
```

### Golang

```go
import "crypto/rsa"
import "crypto/rand"

privateKey, _ := rsa.GenerateKey(rand.Reader, 4096)
publicKey := &privateKey.PublicKey

// OAEP encrypt
ciphertext, _ := rsa.EncryptOAEP(sha256.New(), rand.Reader, publicKey, plaintext, nil)

// PSS sign
signature, _ := rsa.SignPSS(rand.Reader, privateKey, crypto.SHA256, hashed, &rsa.PSSOptions{SaltLength: rsa.PSSSaltLengthAuto})

// Verify
rsa.VerifyPSS(publicKey, crypto.SHA256, hashed, signature, nil)
```

### Analyse et audit de clés

```bash
# Vérifier la taille (bits)
openssl rsa -pubin -in public.pem -text -noout | head -1

# Extraire le modulus hex
openssl rsa -pubin -in public.pem -modulus -noout | cut -d= -f2

# Vérifier la date d'expiration du certificat associé
openssl x509 -in cert.pem -noout -dates

# Vérifier la correspondance clé privée ↔ certificat
openssl x509 -in cert.pem -noout -modulus | md5sum
openssl rsa -in private.pem -noout -modulus | md5sum
# Les deux MD5 doivent être identiques
```

---

## Références

- **RFC 8017 (PKCS#1 v2.2)** : https://datatracker.ietf.org/doc/html/rfc8017
- **NIST SP 800-56B (RSA key transport)** : https://csrc.nist.gov/publications/detail/sp/800-56b/rev-2/final
- **Wiener's Attack** : https://crypto.stanford.edu/~dabo/pubs/papers/RSA-survey.pdf
- **Bleichenbacher Attack** : https://archiv.infsec.ethz.ch/education/fs08/secsem/bleichenbacher98.pdf
- **Boneh Survey of RSA Attacks** : https://crypto.stanford.edu/~dabo/pubs/papers/RSA-survey.pdf
- **ROCA CVE-2017-15361** : https://crocs.fi.muni.cz/public/papers/rsa_ccs17
- **GNFS factorization** : https://en.wikipedia.org/wiki/General_number_field_sieve
- **OpenSSL RSA documentation** : https://www.openssl.org/docs/manmaster/man7/RSA.html