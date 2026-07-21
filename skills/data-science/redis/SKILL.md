---
name: redis
description: "Guide complet Redis — cache, sessions, files d'attente, pub/sub, structures de données avancées, haute disponibilité, persistance, et optimisation."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [redis, cache, base-de-donnees, in-memory, nosql, pubsub, queue, performance]
    homepage: https://redis.io/
    related_skills: [mongodb, optimisation-performance, replication-haute-disponibilite]
prerequisites:
  commands: [redis-cli, redis-server, redis-sentinel, redis-benchmark]
---

# Compétence Redis — Cache, Files d'Attente, Structures de Données et Exploitation

## Vue d'ensemble

Redis est un serveur de structures de données en mémoire, open-source, utilisé comme base de données, cache, et broker de messages. Il supporte les strings, hash, lists, sets, sorted sets, streams, bitmaps, HyperLogLog, et geospatial. Depuis Redis 7.4+, il offre également le clustering natif, ACLs, et les fonctions Lua.

Sa performance est exceptionnelle : 100k-1M ops/s sur un seul nœud avec une latence < 1ms.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Veut mettre en cache des résultats de requêtes SQL ou d'API
- A besoin de files d'attente (task queues) ou de pub/sub
- Demande de gérer des sessions utilisateur ou des rate limits
- Veut utiliser Sorted Sets pour des leaderboards, classements
- Doit configurer la persistance (RDB, AOF) ou la haute disponibilité (Sentinel, Redis Cluster)
- A besoin de Streams pour l'event sourcing ou les logs centralisés

---

## 1. Structures de Données Fondamentales

### 1.1 String (cache, compteurs, rate limiting)

```bash
# SET avec TTL
SET cache:capteur:42 "{'temperature':23.5,'pression':1.02}" EX 300 NX

# Rate limiting
INCR rate_limit:user:42
EXPIRE rate_limit:user:42 60

# Atomic counter
INCRBY stats:page_vues:accueil 1

# Get et Set atomique
GETSET dernier_ts "2025-06-15T10:00:00Z"
```

### 1.2 Hash (objets, sessions)

```bash
# Stocker un objet capteur
HSET capteur:42 nom "Thermocouple L3" temperature 23.5 pression 1.02 statut "OK"
HGETALL capteur:42
HGET capteur:42 temperature
HINCRBY capteur:42 alertes 1

# Sessions utilisateur
HSET session:abc123 user_id 42 last_access 1748800000 ip "192.168.1.10"
EXPIRE session:abc123 3600
```

### 1.3 List (files d'attente, FIFO)

```bash
# Producer (queue classique)
LPUSH task_queue "{\"type\":\"analyse\",\"payload\":\"mesure_42\"}"

# Consumer (bloquant avec timeout)
BRPOP task_queue 5

# LRANGE pour pagination (attention: O(n) pour les grandes listes)
LPUSH logs:recent "2025-06-15T10:00:00 [INFO] Démarrage OK"
LTRIM logs:recent 0 99  # garder 100 entrées max
```

### 1.4 Set (appartenance, uniques)

```bash
# Tags d'un article
SADD article:42:tags "machine-learning" "python" "redis"
SMEMBERS article:42:tags
SISMEMBER article:42:tags "redis"  # 1 si présent

# Intersection : articles communs à deux catégories
SINTER machine-learning:articles python:articles
```

### 1.5 Sorted Set (leaderboards, classements temporels)

```bash
# Score = température, member = capteur_id
ZADD temperatures:now 23.5 "capteur:42"
ZADD temperatures:now 24.1 "capteur:17"
ZADD temperatures:now 22.8 "capteur:89"

# Top 3 des plus chauds
ZREVRANGE temperatures:now 0 2 WITHSCORES

# Range par score (tous les capteurs entre 23 et 25°C)
ZRANGEBYSCORE temperatures:now 23.0 25.0

# Score d'un membre
ZSCORE temperatures:now "capteur:42"
```

### 1.6 Stream (event sourcing, logs, messagerie persistante)

```bash
# Ajouter un événement au stream
XADD mesures:stream * capteur_id 42 temperature 23.5 pression 1.02

# Lire les nouveaux événements (consumer group)
XGROUP CREATE mesures:stream analyse_group $
XREADGROUP GROUP analyse_group consumer1 BLOCK 5000 COUNT 10 STREAMS mesures:stream >

# Range par ID (horodatage)
XRANGE mesures:stream 1728000000000-0 1728001000000-0

# Taille du stream
XLEN mesures:stream

# Trim (garder les 1000 derniers)
XTRIM mesures:stream MAXLEN ~ 1000
```

---

## 2. Cache Design Patterns

### 2.1 Cache-Aside (lazy loading)

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_capteur(capteur_id):
    cache_key = f"capteur:{capteur_id}"

    # 1. Essayer le cache
    cached = r.get(cache_key)
    if cached is not None:
        return json.loads(cached)

    # 2. Fallback DB (cache miss)
    capteur = query_db(f"SELECT * FROM capteurs WHERE id = {capteur_id}")

    # 3. Remplir le cache (TTL 300s = 5 minutes)
    r.setex(cache_key, 300, json.dumps(capteur))
    return capteur
```

### 2.2 Cache Penetration (Bloom Filter)

```bash
# Éviter les requêtes pour des IDs inexistants
BF.RESERVE capteurs_ids 0.01 1000000  # 1% false positive, 1M entrées
BF.ADD capteurs_ids 42
BF.EXISTS capteurs_ids 42  # 1 si probablement présent
```

### 2.3 Cache Stampede (protection)

```bash
# Éviter que N requêtes ne rechargent le cache simultanément
# Utiliser SET NX avec TTL court
SET cache:heavy_data "$heavy" EX 60 NX
# Si NX échoue, le cache est déjà en cours de reconstruction
```

### 2.4 Write-Through (mise à jour synchrone)

```python
def update_capteur(capteur_id, data):
    # Mise à jour DB
    update_db(f"UPDATE capteurs SET temperature = {data['temperature']} WHERE id = {capteur_id}")

    # Mise à jour cache immédiate
    cache_key = f"capteur:{capteur_id}"
    r.setex(cache_key, 300, json.dumps(data))
```

---

## 3. Publier/Souscrire (Pub/Sub)

```bash
# Subscribe (sur un terminal)
SUBSCRIBE canal:alarmes

# Publish (sur un autre)
PUBLISH canal:alarmes "{\"capteur_id\":42,\"niveau\":\"CRITIQUE\",\"valeur\":150.0}"

# Pattern matching
PSUBSCRIBE canal:*  # souscrit à tous les canaux
```

### 3.1 Pub/Sub en Python (asynchrone)

```python
import asyncio
import redis.asyncio as redis

async def subscriber():
    r = redis.Redis()
    pubsub = r.pubsub()
    await pubsub.subscribe("canal:alarmes")

    async for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"ALARME: {message['data']}")
            # Déclencher une action (notification, envoi email, etc.)
```

---

## 4. Persistance

### 4.1 RDB (Redis Database) — Snapshots périodiques

```conf
# redis.conf
save 900 1        # 1 changement en 15 minutes
save 300 10       # 10 changements en 5 minutes
save 60 10000     # 10k changements en 1 minute
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
```

### 4.2 AOF (Append-Only File) — Log d'écriture complet

```conf
# redis.conf
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # fsync toutes les secondes (bon compromis)
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

### 4.3 AOF+RDB hybride (Redis 4.0+)

```conf
aof-use-rdb-preamble yes  # RDB initial + AOF incrémental
```

---

## 5. Haute Disponibilité

### 5.1 Redis Sentinel

```conf
# sentinel.conf
sentinel monitor mymaster 192.168.1.10 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
sentinel auth-pass mymaster "mon_password"
```

```bash
# Démarrer 3 sentinelles
redis-sentinel /etc/redis/sentinel.conf --port 26379
redis-sentinel /etc/redis/sentinel-2.conf --port 26380
redis-sentinel /etc/redis/sentinel-3.conf --port 26381
```

### 5.2 Redis Cluster (sharding natif)

```bash
# Min 3 masters + 3 réplicas
# Chaque nœud avec cluster-enabled yes
redis-cli --cluster create \
    192.168.1.10:6379 192.168.1.11:6379 192.168.1.12:6379 \
    192.168.1.13:6379 192.168.1.14:6379 192.168.1.15:6379 \
    --cluster-replicas 1

# Vérifier
redis-cli --cluster check 192.168.1.10:6379

# Resharding (redistribuer les slots)
redis-cli --cluster reshard 192.168.1.10:6379
```

---

## 6. Administration et Optimisation

### 6.1 Monitoring

```bash
# Info complète
redis-cli INFO

# Mémoire
redis-cli INFO memory
# used_memory_human : mémoire utilisée
# maxmemory : limite configurée
# evicted_keys : clés expulsées (monitorer absolument)

# Opérations par seconde
redis-cli INFO stats | grep instantaneous_ops_per_sec

# Requêtes lentes (latence > 100ms)
redis-cli SLOWLOG GET 10
redis-cli SLOWLOG RESET
```

### 6.2 Éviction des clés

```conf
# redis.conf
maxmemory 8gb
maxmemory-policy allkeys-lru  # LRU sur toutes les clés

# Autres politiques :
# allkeys-lfu : Least Frequently Used (Redis 4.0+)
# volatile-lru : LRU seulement sur les clés avec TTL
# allkeys-random : aléatoire (surprise)
# noeviction : retourne erreur au lieu d'expulser
```

### 6.3 Benchmark

```bash
# Test de performance
redis-benchmark -h 127.0.0.1 -p 6379 -n 100000 -c 50 -t SET,GET,LPUSH,RPUSH,LRANGE,MSET

# Avec pipeline
redis-benchmark -h 127.0.0.1 -p 6379 -n 1000000 -c 50 -P 16 -t SET,GET
```

---

## Pièges Courants

1. **KEYS en production.** `KEYS *` bloque Redis pendant des secondes sur une base chargée. Utiliser `SCAN 0` (cursor-based) pour itérer sans bloquer.

2. **Pas de TTL sur les caches.** Les clés de cache sans expiration s'accumulent jusqu'à saturer la mémoire. Toujours utiliser `EX` ou `SETEX`.

3. **Big keys.** Une clé de 100 Mo ralentit tout Redis (bloque le thread unique). Utiliser `redis-cli --bigkeys` pour les détecter.

4. **Pas de pipeline pour les opérations en masse.** Chaque commande Redis est un RTT. Utiliser `PIPELINE` (Redis CLI) ou `pipeline()` (Python) pour les batchs.

5. **LPUSH + BRPOP pour les files d'attente.** Préférer les Streams (XADD/XREADGROUP) pour les queues persistantes, avec consumer groups et rejet des messages échoués.

6. **AOF sans rewrite.** L'AOF croît indéfiniment. Activer `auto-aof-rewrite-percentage 100` pour le réécrire périodiquement.

---

## Checklist

- [ ] `maxmemory` configuré avec une politique d'éviction adaptée
- [ ] TTL défini sur toutes les clés de cache
- [ ] Pas de `KEYS` en production (utiliser `SCAN`)
- [ ] AOF+RDB hybride activé pour la persistance (`aof-use-rdb-preamble yes`)
- [ ] Pipeline utilisé pour les opérations batch
- [ ] Sentinel ou Cluster configuré pour la HA
- [ ] `redis-benchmark` exécuté pour valider les performances
- [ ] `redis-cli --bigkeys` exécuté pour détecter les grosses clés
- [ ] Monitoring des évictions (`evicted_keys` dans INFO stats)
- [ ] `slowlog` configuré avec `slowlog-log-slower-than 10000` (10ms)