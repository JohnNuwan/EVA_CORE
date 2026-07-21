---
name: oauth2-openid-attacks
description: Guide complet d'attaques OAuth 2.0 et OpenID Connect — redirect_uri manipulation, CSRF, scope elevation, code injection, token theft, PKCE bypass, et outils.
category: cybersecurite
tags: [oauth2, openid, oidc, sso, authentication, authorization, portswigger, jwt]
---

# Attaques OAuth 2.0 et OpenID Connect

## Sommaire
1. [Concepts OAuth 2.0](#concepts-oauth-20)
2. [Flux Authorization Code vs Implicit](#flux-authorization-code-vs-implicit)
3. [Vulnérabilités redirect_uri](#vulnerabilites-redirect-uri)
4. [CSRF et State Parameter](#csrf-et-state-parameter)
5. [Code Injection / Token Theft](#code-injection--token-theft)
6. [Scope Elevation](#scope-elevation)
7. [PKCE Bypass](#pkce-bypass)
8. [Flawed CSRF Protection (Login CSRF)](#flawed-csrf-protection)
9. [OpenID Connect Attacks](#openid-connect-attacks)
10. [Endpoints Discovery](#endpoints-discovery)
11. [Outils et Commandes](#outils-et-commandes)

## Concepts OAuth 2.0

OAuth 2.0 est un framework d'autorisation qui permet à une application cliente d'accéder
à des ressources protégées sans connaître les identifiants de l'utilisateur.

### Acteurs :
- **Resource Owner** : l'utilisateur
- **Client Application** : l'application qui demande l'accès
- **Authorization Server** : le serveur qui délivre les tokens
- **Resource Server** : le serveur qui héberge les données protégées

### Flux simplifié :
```
Client → Authorization Server : demande d'autorisation
User → Authorization Server : authentification + consentement
Authorization Server → Client : authorization code (ou token)
Client → Authorization Server : échange du code contre access token
Client → Resource Server : accès aux données avec le token
```

## Flux Authorization Code vs Implicit

### Authorization Code Grant (recommandé) :
```
GET /authorize?response_type=code&client_id=...&redirect_uri=...&state=...
→ Authorization code dans l'URL de callback
POST /token?grant_type=authorization_code&code=...&redirect_uri=...&client_secret=...
→ Access token + refresh token
```

### Implicit Grant (obsolète, déconseillé) :
```
GET /authorize?response_type=token&client_id=...&redirect_uri=...&state=...
→ Access token dans le fragment d'URL (#access_token=...)
```
**Problème** : le token est exposé dans l'URL, accessible via l'historique, les logs, les referers.

## Vulnérabilités redirect_uri

Le paramètre `redirect_uri` détermine où le code/token est envoyé.
Si mal validé, l'attaquant peut rediriger le flux vers son propre serveur.

### Techniques de bypass :

**1. Subdomain whitelist bypass :**
```
https://client.com.evil.com/callback
```

**2. Path traversal :**
```
https://client.com/oauth/callback/../../evil.com/
```

**3. Parameter pollution :**
```
?redirect_uri=client.com/callback&redirect_uri=evil.com
```

**4. Parsing confusion (@) :**
```
https://client.com@evil.com/callback
https://client.com#@evil.com
```

**5. localhost bypass :**
```
https://localhost.evil.com/
```

**6. Open redirect sur le même domaine :**
```
https://client.com/redirect?url=evil.com
```

### Exploitation complète :
1. Enregistrer un client OAuth malveillant
2. Tricker la victime : cliquer sur un lien avec `redirect_uri` pointant vers l'attaquant
3. L'attaquant intercepte le code/token dans ses logs serveur
4. Échanger le code contre un access token (étape serveur→serveur)

## CSRF et State Parameter

Le paramètre `state` est un token CSRF qui lie la requête d'autorisation à la session.

### Test :
Si la requête `GET /authorize` n'a PAS de paramètre `state` → vulnérable.

### Exploitation :
1. L'attaquant initie un flux OAuth avec son propre compte
2. Tricker la victime à cliquer sur `https://client.com/callback?code=...&state=...`
3. La victime est connectée au compte de l'attaquant (Login CSRF)
4. **Impact** : Liage du compte victime au compte social de l'attaquant

### Impact plus grave :
Si le site permet de lier des comptes sociaux : l'attaquant lie son propre compte social
au compte de la victime sur le site client → takeover permanent.

## Code Injection / Token Theft

### Interception de l'authorization code :
Dans le flux Auth Code, le code est envoyé via le navigateur de l'utilisateur.
Si l'attaquant peut intercepter ce code (via redirect_uri vulnérable, XSS, etc.) :

```
POST /callback HTTP/1.1
Host: client-app.com
code=STOLEN_CODE&state=xyz
```

### Pas besoin du client_secret pour l'échange :
Si le serveur d'autorisation ne vérifie PAS le `redirect_uri` lors de l'échange
du code (POST /token), l'attaquant peut échanger le code volé directement.

### Proxy page technique :
Même si le redirect_uri est whitelisté sur le même domaine, chercher :
- `/proxy?url=`
- `/redirect?to=`
- `/forward?target=`
- `/download?file=`

Ces pages peuvent être utilisées pour transmettre le code à l'attaquant.

## Scope Elevation

### Principe :
Si le serveur d'autorisation ne vérifie pas le scope réellement accordé
vs le scope utilisé dans le token.

### Test :
```bash
# Original
GET /authorize?response_type=code&scope=openid+profile&client_id=...

# Modifié
GET /authorize?response_type=code&scope=openid+profile+admin+email&client_id=...
```

### Autres techniques :
- Retirer le consentement utilisateur, puis réutiliser un ancien token avec scope plus large
- Scope swappping : changer `scope=openid` → `scope=openid email` après le consentement
- Utiliser l'API introspection pour découvrir les scopes disponibles

## PKCE Bypass

PKCE (Proof Key for Code Exchange) protège contre l'interception du code.

### Vulnérabilités courantes :
- **Serveur n'enforce pas PKCE** : si le client ne l'envoie pas, le serveur accepte sans
- **code_challenge_method = "plain"** (obsolète) : le code_verifier est identique au code_challenge
- **Replay du code_verifier** : non lié à la session, donc réutilisable

### Test :
```bash
# Envoyer sans code_challenge
GET /authorize?response_type=code&client_id=...&code_challenge=&code_challenge_method=

# Si la requête fonctionne → pas de PKCE → interception facile
```

## Flawed CSRF Protection (Login CSRF)

### Scénario :
1. L'attaquant crée son propre compte sur le site cible via OAuth
2. Il capture le authorization code ou access token
3. Il tricke la victime à visiter : `https://victim.com/oauth/callback?code=ATTACKER_CODE`
4. La victime est maintenant connectée au compte de l'attaquant

### Impact :
- La victime effectue des actions sur le compte de l'attaquant (achats, posts)
- Possible vol de données si l'attaquant peut récupérer les cookies de session

## OpenID Connect Attacks

OIDC ajoute un token ID (JWT) contenant l'identité de l'utilisateur.

### Endpoint spécifique :
```bash
curl https://auth-server/.well-known/openid-configuration
```

### Vulnérabilités :
- **`sub` (subject) non vérifié** : usurpation d'identité entre utilisateurs
- **`aud` (audience) non vérifié** : token volé utilisable sur un autre client
- **`nonce` absent** : pas de protection CSRF sur le flux OIDC
- **`exp` non vérifié** : token intemporel
- **`iat` (issued at) non vérifié** : pas de détection de replay

### Attaque par confusion de provider :
Si le serveur OIDC supporte plusieurs providers (Google, Facebook, etc.) :
- Modifier `iss` (issuer) dans le token ID
- Utiliser un provider malveillant qui retourne un sub valide

## Endpoints Discovery

### Discovery standard :
```bash
curl -s https://auth-server.com/.well-known/oauth-authorization-server | jq .
curl -s https://auth-server.com/.well-known/openid-configuration | jq .
```

### Informations récupérées :
- `authorization_endpoint`
- `token_endpoint`
- `userinfo_endpoint`
- `jwks_uri`
- `scopes_supported`
- `response_types_supported`
- `grant_types_supported`
- `code_challenge_methods_supported`

## Outils et Commandes

### oauth2c (CLI OAuth client) :
```bash
# Installation
go install github.com/oauth2c/oauth2c@latest

# Test de flux complet
oauth2c https://auth-server.com \
  --client-id client123 \
  --response-type code \
  --redirect-uri https://client.com/callback \
  --scope openid profile
```

### curl manuel (Authorization Code) :
```bash
# 1. Demander le code
curl -v "https://auth-server.com/authorize?response_type=code&client_id=123&redirect_uri=https://client.com/callback&scope=openid&state=xyz"

# 2. Échanger le code contre un token
curl -X POST "https://auth-server.com/token" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=https://client.com/callback" \
  -d "client_id=123" \
  -d "client_secret=secret"

# 3. Accéder aux ressources
curl -H "Authorization: Bearer ACCESS_TOKEN" "https://resource-server.com/userinfo"
```

### Burp Suite :
- **Autorize** extension : détection automatique d'IDOR
- **Auth Analyzer** : analyse des flux OAuth
- **OAuth Scan** : scan des vulnérabilités OAuth courantes

### Script Python d'analyse OAuth :
```python
import requests

def oauth_enum(auth_server):
    """Énumérer les endpoints OAuth"""
    # Discovery
    for path in ['.well-known/oauth-authorization-server',
                 '.well-known/openid-configuration',
                 'jwks.json']:
        r = requests.get(f"{auth_server}/{path}")
        if r.status_code == 200:
            print(f"[+] {path}: {r.json()}")
    
    # Tester les endpoints
    endpoints = ['authorize', 'token', 'userinfo', 'introspect', 'revoke', 'register']
    for ep in endpoints:
        r = requests.get(f"{auth_server}/{ep}")
        print(f"[{r.status_code}] /{ep}")
```

## Ressources
- **PortSwigger OAuth Academy** : https://portswigger.net/web-security/oauth
- **HackTricks OAuth** : https://book.hacktricks.xyz/pentesting-web/oauth-to-account-takeover
- **PayloadsAllTheThings OAuth** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/OAuth
- **Hidden OAuth Attack Vectors** (PortSwigger) : https://portswigger.net/research/hidden-oauth-attack-vectors
- **RFC 6749 (OAuth 2.0)** : https://datatracker.ietf.org/doc/html/rfc6749
- **RFC 7636 (PKCE)** : https://datatracker.ietf.org/doc/html/rfc7636
- **OAuth 2.0 Threat Model** : https://tools.ietf.org/html/rfc6819