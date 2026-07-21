---
name: api-rate-limiting
description: "Use when implémenter, configurer ou auditer le rate limiting d'une API. Couvre les algorithmes (token bucket, leaky bucket, sliding window, fixed window), les stratégies (global, par utilisateur, par endpoint), les en-têtes standard, Redis, le backoff exponentiel, et les architectures distribuées."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, rate-limiting, throttle, performance, security, backend]
    related_skills: [api-security, api-rest-best-practices, api-openapi-documentation]
---

# Rate Limiting

## Vue d'ensemble

Le rate limiting (ou throttling) est le mécanisme qui contrôle le nombre de requêtes qu'un client peut envoyer à une API sur une période donnée. Sans lui, un client malveillant (ou buggé) peut saturer le serveur, exploser la facture, ou bruteforcer l'authentification. Le rate limiting est à la fois une mesure de **sécurité** (anti-DoS, anti-bruteforce) et de **gouvernance** (équité entre clients, monétisation par paliers).

## Quand l'utiliser

- Toujours, sur toute API publique ou exposée sur Internet
- APIs avec authentification (protéger contre le bruteforce)
- APIs facturées à l'usage (freemium, paliers de prix)
- Endpoints coûteux (recherche, IA, export PDF)
- APIs avec contrat SLA (garantir la disponibilité)
- Websockets (limiter les messages/seconde par connexion)

Ne pas utiliser pour : des APIs internes strictement intra-service (mais même là, un rate limiting basique est prudent), ou des endpoints critiques où chaque requête doit passer (alertes de sécurité, webhooks de paiement).

## Algorithmes

### 1. Token Bucket (le plus flexible)

Un bucket contient N tokens. Chaque requête consomme un token. Les tokens se régénèrent à un taux fixe (r tokens/seconde). Si le bucket est vide, la requête est rejetée.

```python
import time
import asyncio
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # tokens/seconde
        self.capacity = capacity  # taille max du bucket
        self.tokens = capacity
        self.last_refill = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

# Usage avec FastAPI
buckets: dict[str, TokenBucket] = {}

@app.middleware("http")
async def rate_limit_token_bucket(request: Request, call_next):
    client_id = request.client.host
    if client_id not in buckets:
        buckets[client_id] = TokenBucket(rate=10, capacity=20)  # 10 req/s, burst 20

    if not buckets[client_id].consume():
        return JSONResponse(
            status_code=429,
            content={"error": "Too Many Requests", "retry_after": 1},
            headers={"Retry-After": "1"},
        )
    return await call_next(request)
```

**Avantages :** Permet les bursts, précis, simple à comprendre.
**Inconvénients :** Nécessite un état partagé en mode distribué.

### 2. Fixed Window (le plus simple)

Compteur qui se réinitialise à chaque intervalle de temps fixe :

```python
from collections import defaultdict
import time

class FixedWindow:
    def __init__(self, limit: int, window: int):
        self.limit = limit       # requêtes max
        self.window = window     # fenêtre en secondes
        self.counters: dict[str, tuple[int, int]] = {}  # client → (count, window_start)

    def allow(self, client_id: str) -> bool:
        now = int(time.time())
        window_start = now - (now % self.window)

        if client_id not in self.counters or self.counters[client_id][1] != window_start:
            self.counters[client_id] = (0, window_start)

        count, _ = self.counters[client_id]
        if count >= self.limit:
            return False

        self.counters[client_id] = (count + 1, window_start)
        return True
```

**Problème du "thundering herd" en fin de fenêtre :** 100 requêtes passent à la seconde 59, 100 autres à la seconde 60, soit 200 en 2 secondes. Solution : sliding window.

### 3. Sliding Window Log (le plus précis)

Maintient un timestamp pour chaque requête. Calcule le nombre de requêtes dans les N dernières secondes :

```python
from collections import defaultdict
import time

class SlidingWindowLog:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.logs: dict[str, list[float]] = defaultdict(list)

    def allow(self, client_id: str) -> bool:
        now = time.time()
        cutoff = now - self.window

        # Nettoyer les entrées expirées
        self.logs[client_id] = [t for t in self.logs[client_id] if t > cutoff]

        if len(self.logs[client_id]) >= self.limit:
            return False

        self.logs[client_id].append(now)
        return True
```

**Avantages :** Très précis, pas de thundering herd.
**Inconvénients :** Consommation mémoire O(N), plus lent.

### 4. Sliding Window Counter (compromis précis/efficace)

Compteurs basés sur deux fenêtres (actuelle + précédente) avec interpolation :

```python
import time
from collections import defaultdict

class SlidingWindowCounter:
    def __init__(self, limit: int, window: int):
        self.limit = limit
        self.window = window
        self.counters: dict[str, dict] = defaultdict(lambda: {"count": 0, "prev": 0, "ts": 0})

    def allow(self, client_id: str) -> bool:
        now = time.time()
        state = self.counters[client_id]
        current_window = int(now / self.window)

        if current_window != state["ts"]:
            state["prev"] = state["count"]
            state["count"] = 0
            state["ts"] = current_window

        # Poids de la fenêtre précédente
        elapsed = now - (current_window * self.window)
        weight = (self.window - elapsed) / self.window
        estimated = state["prev"] * weight + state["count"]

        if estimated >= self.limit:
            return False

        state["count"] += 1
        return True
```

### 5. Leaky Bucket (pour le lissage de débit)

File d'attente qui se vide à taux constant. Les requêtes au-delà de la capacité de la file sont rejetées :

```python
import asyncio

class LeakyBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=capacity)

    async def process(self, request):
        try:
            self.queue.put_nowait(request)
            # Traiter au taux rate
            await asyncio.sleep(1.0 / self.rate)
            self.queue.get_nowait()
            self.queue.task_done()
            return True
        except asyncio.QueueFull:
            return False
```

## En-Têtes Standard

Toute réponse rate-limited DOIT inclure ces en-têtes :

```python
from fastapi import Response

def add_rate_limit_headers(
    response: Response,
    limit: int,
    remaining: int,
    reset: int,
    window_seconds: int,
):
    response.headers.update({
        "X-RateLimit-Limit": str(limit),           # Requêtes max par fenêtre
        "X-RateLimit-Remaining": str(remaining),    # Requêtes restantes
        "X-RateLimit-Reset": str(reset),            # Timestamp de réinitialisation
        "X-RateLimit-Window": str(window_seconds),  # Fenêtre en secondes
    })

# Quand la limite est dépassée (429) :
def rate_limited_response(retry_after_seconds: int):
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too Many Requests",
            "message": f"Limite dépassée. Réessayer dans {retry_after_seconds}s.",
            "retry_after": retry_after_seconds,
        },
        headers={
            "Retry-After": str(retry_after_seconds),
            "X-RateLimit-Remaining": "0",
        },
    )
```

## Redis (Rate Limiting Distribué)

Pour les architectures multi-serveurs, le state doit être partagé :

```python
import redis.asyncio as redis
import time

class RedisTokenBucket:
    def __init__(self, redis_client: redis.Redis, rate: float, capacity: int, prefix: str = "rl:"):
        self.redis = redis_client
        self.rate = rate
        self.capacity = capacity
        self.prefix = prefix

    async def allow(self, client_id: str, cost: int = 1) -> bool:
        key = f"{self.prefix}{client_id}"
        now = time.monotonic()

        # Lua script pour atomicité
        script = """
        local key = KEYS[1]
        local rate = tonumber(ARGV[1])
        local capacity = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local cost = tonumber(ARGV[4])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1] or capacity)
        local last_refill = tonumber(bucket[2] or now)

        local elapsed = now - last_refill
        tokens = math.min(capacity, tokens + elapsed * rate)

        if tokens >= cost then
            tokens = tokens - cost
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, 60)
            return 1
        else
            return 0
        end
        """
        result = await self.redis.eval(script, 1, key, self.rate, self.capacity, now, cost)
        return bool(result)
```

### Sliding Window avec Redis Sorted Set

```python
class RedisSlidingWindow:
    def __init__(self, redis_client: redis.Redis, limit: int, window: int, prefix: str = "rl:"):
        self.redis = redis_client
        self.limit = limit
        self.window = window
        self.prefix = prefix

    async def allow(self, client_id: str) -> tuple[bool, int, int]:
        key = f"{self.prefix}sw:{client_id}"
        now = int(time.time() * 1000)  # millisecondes
        window_start = now - (self.window * 1000)

        pipeline = self.redis.pipeline()
        pipeline.zremrangebyscore(key, 0, window_start)  # Nettoyer les anciens
        pipeline.zcard(key)                                # Compter les requêtes récentes
        pipeline.zadd(key, {str(now): now})               # Ajouter la requête
        pipeline.expire(key, self.window + 1)               # TTL
        _, count, _, _ = await pipeline.execute()

        if count >= self.limit:
            # Obtenir le timestamp de la plus ancienne requête dans la fenêtre
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = int(oldest[0][1] / 1000) + self.window if oldest else int(time.time()) + self.window
            return False, 0, reset_time

        remaining = self.limit - count - 1
        reset_time = int(time.time()) + self.window
        return True, remaining, reset_time
```

## Stratégies de Rate Limiting

### Par Client

```python
# Basé sur IP
@app.middleware("http")
async def rate_limit_by_ip(request: Request, call_next):
    client_ip = request.client.host
    allowed, remaining, reset = await rl.allow(client_ip)
    ...

# Basé sur token (utilisateur connecté)
@app.middleware("http")
async def rate_limit_by_user(request: Request, call_next):
    user_id = request.state.user.get("id") if hasattr(request.state, "user") else None
    if user_id:
        allowed, remaining, reset = await rl.allow(f"user:{user_id}")
    else:
        allowed, remaining, reset = await rl.allow(f"ip:{request.client.host}")
    ...
```

### Par Endpoint

```python
# Endpoints coûteux (recherche, IA) : limites plus basses
RATE_LIMITS = {
    "default": {"limit": 100, "window": 60},
    "search": {"limit": 10, "window": 60},
    "export": {"limit": 5, "window": 3600},  # 5 exports/heure
    "auth": {"limit": 5, "window": 300},     # 5 tentatives/5 minutes
    "webhook": {"limit": 1000, "window": 60},
}
```

### Par Payer (multi-tier)

```python
TIERS = {
    "free": {"limit": 100, "window": 3600, "burst": 10},      # 100 req/h
    "pro": {"limit": 10000, "window": 3600, "burst": 100},     # 10k req/h
    "enterprise": {"limit": 100000, "window": 3600, "burst": 500},  # 100k req/h
}
```

## Backoff Exponentiel (Côté Client)

Le client DOIT implémenter un backoff exponentiel quand il reçoit un 429 :

```python
import asyncio
import random

async def api_call_with_backoff(url: str, max_retries: int = 5):
    for attempt in range(max_retries):
        response = await client.get(url)

        if response.status_code != 429:
            return response

        # Lire Retry-After
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            wait = int(retry_after)
        else:
            # Exponential backoff avec jitter
            wait = min(2 ** attempt + random.random(), 60)

        print(f"Rate limited. Attente {wait}s... (tentative {attempt + 1}/{max_retries})")
        await asyncio.sleep(wait)

    raise Exception("Max retries atteint")
```

## Implémentation Référence

### FastAPI + Redis (complet)

```python
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import time

app = FastAPI()

@app.on_event("startup")
async def startup():
    app.state.redis = await redis.from_url("redis://localhost:6379")
    app.state.rl = RedisSlidingWindow(app.state.redis, limit=100, window=60)

@app.middleware("http")
async def rate_limiter(request: Request, call_next):
    # Ignorer le rate limiting pour certains endpoints
    if request.url.path in ("/health", "/metrics", "/docs", "/openapi.json"):
        return await call_next(request)

    # Identifier le client
    client_id = _get_client_id(request)

    allowed, remaining, reset = await app.state.rl.allow(client_id)

    # Toujours ajouter les en-têtes
    response = await call_next(request) if allowed else None

    if allowed:
        response.headers["X-RateLimit-Limit"] = "100"
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset)
        return response
    else:
        retry_after = max(1, reset - int(time.time()))
        return JSONResponse(
            status_code=429,
            content={
                "error": "Too Many Requests",
                "detail": f"Limite de 100 requêtes/minute dépassée. Réessayer dans {retry_after}s.",
            },
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset),
            },
        )

def _get_client_id(request: Request) -> str:
    # Priorité : token → IP
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        # Extraire l'ID utilisateur du token (sans le décoder à chaque fois)
        # Idéalement, le middleware d'auth a déjà stocké l'utilisateur
        if hasattr(request.state, "user"):
            return f"user:{request.state.user.get('id')}"
    return f"ip:{request.client.host}"
```

## Pièges Courants

1. **Rate limiting pas assez restrictif sur les endpoints d'auth** — 5 tentatives/5 minutes maximum. Un attaquant peut bruteforcer 1000 mots de passe/minute sans limite.
2. **Pas de différenciation par tier** — un client gratuit et un client enterprise ont les mêmes limites. Utiliser des paliers.
3. **Pas d'en-têtes de rate limiting** — le client ne sait pas quand il va être limité et ne peut pas s'adapter. Toujours renvoyer `X-RateLimit-*`.
4. **Reset à minuit (fixed window)** — tous les clients se reconnectent à minuit, créant un pic. Utiliser sliding window.
5. **Rate limiting sans Redis en mode distribué** — 3 serveurs, chaque serveur a sa propre limite. Le client peut faire 3x le nombre de requêtes. Utiliser Redis.
6. **Pas de jitter dans le backoff** — 1000 clients qui reçoivent un 429 et attendent 60s pile se reconnectent en même temps. Ajouter du jitter.
7. **Rate limiting sur les webhooks** — un webhook de paiement peut être bloqué. Whitelister les endpoints critiques.
8. **Pas de monitoring** — si le rate limiting est trop agressif, les clients légitimes sont bloqués sans que personne ne le sache. Surveiller le taux de 429.

## Checklist de Vérification

- [ ] Algorithme de rate limiting choisi (token bucket, sliding window, etc.)
- [ ] En-têtes `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` implémentés
- [ ] En-tête `Retry-After` sur les réponses 429
- [ ] Rate limiting différencié par endpoint (auth vs data vs export)
- [ ] Rate limiting différencié par tier utilisateur (free/pro/enterprise)
- [ ] Redis ou équivalent pour le mode distribué (multi-serveurs)
- [ ] Endpoints whitelistés : health, metrics, webhooks critiques
- [ ] Backoff exponentiel avec jitter documenté pour les clients
- [ ] Monitoring et alerting sur le taux de 429
- [ ] Tests : limites atteintes, dépassées, reset, headers