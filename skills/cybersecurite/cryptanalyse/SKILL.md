---
name: cryptanalyse
description: Cryptanalyse — attaques de chiffrement classique et moderne, side-channel, padding oracle, meet-in-the-middle, attaques d'implémentation, et outils de cracking
tags: [cryptanalyse, crypto, AES, RSA, side-channel, padding-oracle, hash, cracking]
version: 1.0
---

# Cryptanalyse

Guide de cryptanalyse offensive — attaques sur chiffrements symétriques, asymétriques, hachages, et implémentations.

## 1. Cryptanalyse Classique

### Fréquence (Substitution simple)
```bash
# Analyse de fréquences des lettres françaises : E > A > S > T > I > N > R > U > L > O
# Bigrammes : ES, LE, DE, EN, NT, TE, ON, RE, IT, SE
# Trigrammes : ENT, LES, QUE, DES, AIT, ION, EST, POU

# Outils
# - quipquip (automatic solver)
# - https://www.quipquip.com
# - CrypTool 2 (all-in-one)
```

### Vigenère (Kasiski / Index of Coincidence)
```bash
# 1. Kasiski examination : trouver répétitions → key length
# 2. Index of Coincidence : confirmer key length
# 3. Frequency analysis per column

# Auto-solve
python3 -c "
from pwn import *
# Vigenere solver with chi-squared scoring
# Utiliser https://github.com/woodfrog/pycipher
"
```

### Enigma (WWII)
```bash
# 3 rotors + reflector + plugboard
# 26^3 × 26^3 × 26 = 26^7 = 8B combinaisons
# Bombe de Turing : crib-based attack (known plaintext)

# Tools
# - Enigma simulator : https://github.com/omarmhaimdat/pyEnigma
# - Bombe simulator : https://github.com/hyperreality/Bombe
```

## 2. Cryptanalyse Symétrique Moderne

### Padding Oracle Attack (AES-CBC)
```python
# Exploite un oracle qui révèle si padding est valide
# Objectif : déchiffrer sans la clé

from pwn import *

def oracle(ciphertext):
    """Retourne True si padding valide, False sinon"""
    r = remote('target.com', 443)
    r.send(ciphertext)
    response = r.recv()
    return b'Invalid padding' not in response

def decrypt_block(block, oracle):
    """Déchiffrer un bloc CBC via padding oracle"""
    intermediate = [0] * 16
    plaintext = [0] * 16
    
    for byte_pos in range(15, -1, -1):
        for guess in range(256):
            # Construire fake ciphertext
            fake = [0] * 16
            for i in range(byte_pos + 1, 16):
                fake[i] = intermediate[i] ^ (16 - byte_pos)
            fake[byte_pos] = guess
            
            if oracle(bytes(fake)):
                intermediate[byte_pos] = guess ^ (16 - byte_pos)
                break
    return bytes(intermediate)
```

### CBC Bit Flipping
```python
# Modifier un byte du plaintext en changeant IV ou bloc précédent
# Utile pour : modifier cookie, privilège, userid

# Pour changer plaintext byte P[i] → P'[i] :
# C[i-1][i] = C[i-1][i] XOR P[i] XOR P'[i]

def bit_flip(ciphertext, block_num, byte_pos, original, desired):
    ct = bytearray(ciphertext)
    ct[block_num * 16 + byte_pos] ^= original ^ desired
    return bytes(ct)
```

### ECB Byte-at-a-Time
```python
# AES-ECB : blocs indépendants
# Technique : ajouter préfixe contrôlé pour isoler bytes inconnus

def detect_block_size(oracle):
    """Détecter taille de bloc"""
    base = len(oracle(b''))
    for i in range(1, 33):
        if len(oracle(b'A' * i)) != base:
            return len(oracle(b'A' * i)) - base
    return 16

def ecb_oracle_attack(oracle, block_size=16):
    """Déchiffrer byte par byte via oracle ECB"""
    unknown = b''
    for _ in range(len(oracle(b''))):
        prefix = b'A' * (block_size - 1 - len(unknown) % block_size)
        target = oracle(prefix)[:len(prefix) + len(unknown) + 1]
        for b in range(256):
            test = oracle(prefix + unknown + bytes([b]))
            if test[:len(target)] == target:
                unknown += bytes([b])
                break
    return unknown
```

## 3. Cryptanalyse Asymétrique

### RSA Attacks

#### Wiener Attack (d < N^0.25)
```python
# Si d < N^0.25, e/d approx = k/phi(N)
# Continued fraction expansion

from sympy import continued_fraction, convergents

def wiener_attack(e, n):
    cf = continued_fraction(e, n)
    for k, d in convergents(cf):
        if k != 0:
            phi = (e * d - 1) // k
            # Vérifier : p+q = n - phi + 1
            # Résoudre x² - (n - phi + 1)x + n = 0
            discriminant = (n - phi + 1)**2 - 4*n
            if discriminant > 0:
                p = (n - phi + 1 - sqrt(discriminant)) // 2
                if p * n // p == n:
                    return d
    return None
```

#### Common Modulus Attack
```python
# Même n, e1 et e2 coprime
# e1*m1 + e2*m2 = gcd(e1, e2) = 1
# c1^m1 * c2^m2 = m mod n

def common_modulus(c1, c2, e1, e2, n):
    g, a, b = extended_gcd(e1, e2)
    if a < 0:
        c1 = pow(c1, -1, n)  # modular inverse
        a = -a
    if b < 0:
        c2 = pow(c2, -1, n)
        b = -b
    return (pow(c1, a, n) * pow(c2, b, n)) % n
```

#### Low Public Exponent (e=3, small m)
```python
# Si m^3 < n, alors c = m^3 (pas de mod n)
# Cube root attack
import gmpy2

def cube_root_attack(c):
    # c = m^3 (no wrap)
    m, exact = gmpy2.iroot(c, 3)
    return int(m) if exact else None

# Hastad Broadcast Attack (même m, n différents, e=3)
# 3 équations → CRT → cube root
```

#### Coppersmith Attack
```python
# Small roots of polynomial modulo n
# Utilisé quand : bits de p connus, partial key exposure
# Implémentation : SageMath
# small_roots() method
```

### ECDLP (Elliptic Curve Discrete Log)
```bash
# Pollard's Rho (Pohlig-Hellman pour petits sous-groupes)
# MOV attack (si embedding degree small)

# Tools
# - SageMath ECDLP
# - ECDLP solver : https://github.com/elliptic-shiho/ecdsa-notes
```

## 4. Hash Attacks

### Length Extension Attack
```python
# MD5, SHA1, SHA256 : vulnérables à length extension
# H(secret || message) peut être étendu à H(secret || message || padding || append)

import struct
import hashlib

def md5_length_extension(original_hash, original_msg, append_msg, key_len):
    # Simuler l'état interne après H(secret || original_msg)
    # Ajouter padding + append_msg
    # Calculer nouvelle hash sans connaître secret
    pass
```

### Hash Collision
```bash
# SHA1 : SHAttered (Google, 2017) — 2^63 op → 2^63
# MD5 : collision en quelques secondes (hashclash)
# SHA256 : pas de collision publique

# Tool : hashclash (MD5)
# https://github.com/cr-marcstevens/hashclash
```

## 5. Side-Channel Attacks

### Timing Attack
```python
# Mesurer temps d'exécution dépendant de la clé
# Ex: strcmp, memcmp, RSA exponentiation

import time
import statistics

def timing_attack(oracle, secret_len):
    recovered = ''
    for pos in range(secret_len):
        times = {}
        for c in range(32, 127):
            test = recovered + chr(c)
            measurements = []
            for _ in range(100):
                start = time.perf_counter_ns()
                oracle(test + 'A' * (secret_len - len(test)))
                end = time.perf_counter_ns()
                measurements.append(end - start)
            times[chr(c)] = statistics.median(measurements)
        recovered += max(times, key=times.get)
    return recovered
```

### Power Analysis (SPA/DPA)
```bash
# Simple Power Analysis : observer tracé de puissance
# Differential Power Analysis : analyse statistique
# CPA : Correlation Power Analysis

# Tools
# - ChipWhisperer (hardware + software)
# - Jupyter + ChipWhisperer API
# - PicoScope (oscilloscope)
```

### Cache Timing (Spectre/Meltdown class)
```python
# Flush+Reload : mesurer temps d'accès cache
# Prime+Probe : remplir cache, mesurer éviction
# Evict+Reload : éviction forcée + reload

# Flush+Reload sur AES T-tables
# Permet de récupérer la clé AES
```

## 6. Implementation Attacks

### Lattice-based Attacks
```python
# Hidden Number Problem (HNP) — DSA/ECDSA nonce bias
# LLL algorithm pour réduire base

def lattice_attack_dsa(signatures, hash_values, n, k_bits):
    """
    Signatures ECDSA avec nonces biaisés
    Réduire avec LLL → trouver clé privée
    """
    # Construire matrice de contraintes HNP
    # Appliquer LLL reduction
    # Extraire secret key
```

### Bleichenbacher Attack (PKCS#1 v1.5)
```python
# Million message attack
# Oracle : padding valide ou non
# Permet de déchiffrer RSA sans clé privée

# Manger's attack (variante améliorée)
# Borcherding's attack (encore plus rapide)
```

## 7. Tools de Cracking

### Hashcat
```bash
# Modes courants
# 0     : MD5
# 1000  : NTLM
# 22000 : WPA2 PMKID
# 2500  : WPA/WPA2
# 3200  : bcrypt
# 1410  : sha256($pass.$salt)
# 2711  : sha256(ikm)
# 2100  : Domain Cached Credentials

hashcat -m 0 hash.txt wordlist.txt
hashcat -m 0 hash.txt wordlist.txt -r rules/best64.rule
hashcat -m 0 hash.txt -a 3 ?l?l?l?l?l?l?l?l  # brute force 8 chars lowercase
```

### John the Ripper
```bash
# Smart wordlist + rules
john --wordlist=wordlist.txt hash.txt
john --incremental hash.txt
john --show hash.txt
```

## 8. Tools Compendium

| Outil | Usage |
|-------|-------|
| **CrypTool 2** | Cryptanalyse visuelle |
| **SageMath** | Mathématiques avancées (LLL, Coppersmith) |
| **Hashcat** | GPU cracking |
| **John the Ripper** | CPU cracking |
| **RsaCtfTool** | RSA multi-attack automatisé |
| **xortool** | XOR analysis |
| **FeatherDuster** | Crypto analysis framework |
| **CryptoHack** | Practice + writeups |
| **Z3/SMT** | Constraint solving (opaque predicates) |
| **Galois** | EC crypto analysis |

## 9. Ressources

- **CryptoHack** : https://cryptohack.org (challenges)
- **CryptoPals** : https://cryptopals.com (classic challenges)
- **RsaCtfTool** : https://github.com/RsaCtfTool/RsaCtfTool
- **Hashcat** : https://hashcat.net/wiki
- **ChipWhisperer** : https://github.com/newaetech/chipwhisperer
- **Aumasson's Book** : Serious Cryptography
- **Boneh-Shoup** : A Graduate Course in Applied Cryptography
- **CRYPTANALYSIS** : Helen Fouché Gaines (classical)