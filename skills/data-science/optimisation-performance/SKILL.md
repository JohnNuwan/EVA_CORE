---
name: optimisation-performance
description: "Guide complet d'optimisation des performances des bases de données — EXPLAIN, query planning, statistiques, paramètres mémoire, parallélisme, connection pooling, caching, et monitoring."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [optimisation, performance, tuning, index, query-plan, explain, cache, pool, monitoring]
    homepage: https://use-the-index-luke.com/
    related_skills: [postgresql, mysql, redis, indexation-bases-donnees, sharding-partitionnement]
prerequisites:
  commands: [psql, mysql, mongosh, redis-cli]
---

# Compétence Optimisation des Performances des Bases de Données

## Vue d'ensemble

L'optimisation des performances d'une base de données est un processus itératif : mesurer → identifier le goulot → corriger → mesurer à nouveau. Cette compétence couvre l'analyse des plans d'exécution, la configuration mémoire, le parallélisme, le connection pooling, le caching, le monitoring, et l'optimisation continue.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Se plaint de requêtes lentes (pages qui chargent en > 1s)
- Doit optimiser les configurations mémoire d'une base existante
- Veut configurer un pool de connexions (PgBouncer, ProxySQL)
- A besoin de mettre en place un cache (Redis, memcached)
- Veut monitorer les performances (pg_stat_statements, PMM, slow query log)
- Doit dimensionner une nouvelle instance pour un workload connu

---

## 1. Analyse des Requêtes Lentes

### 1.1 PostgreSQL — EXPLAIN

```sql
-- Plan d'exécution de base
EXPLAIN (ANALYZE, BUFFERS, TIMING, SETTINGS)
SELECT m.*, c.nom
FROM mesures m
JOIN capteurs c ON m.capteur_id = c.id
WHERE m.timestamp >= '2025-06-01'
  AND m.temperature > 100
ORDER BY m.timestamp DESC
LIMIT 100;
```

**Lire un plan EXPLAIN :**

| Nœud | Signification | Action |
|------|--------------|--------|
| Seq Scan | Parcours complet de la table | Ajouter un index |
| Index Scan | Recherche dans l'index + lecture table | Vérifier si covering possible |
| Index Only Scan | Tout dans l'index, pas de lecture table | Excellent ! |
| Bitmap Heap Scan | Construction d'un bitmap + scan | Moyen, souvent améliorable |
| Nested Loop | Boucle pour chaque ligne externe | Bon si peu de lignes externes |
| Hash Join | Table hachée en mémoire | Bon pour des jointures size > 100k |
| Merge Join | Tri + fusion | Bon si déjà trié |
| Sort | Tri explicite | Ajouter un index ou ORDER BY couvert |
| Materialize | Matérialisation d'un CTE/Subquery | Souvent signe de mauvaise optimisation |

### 1.2 MySQL — EXPLAIN

```sql
EXPLAIN ANALYZE
SELECT m.*, c.nom
FROM mesures m
JOIN capteurs c ON m.capteur_id = c.id
WHERE m.timestamp >= '2025-06-01' AND m.temperature > 100
ORDER BY m.timestamp DESC;
```

**Lecture :**
- `type` : `ALL` = table scan, `ref` = index lookup, `eq_ref` = PK lookup, `range` = range scan
- `rows` : estimation du nombre de lignes examinées
- `Extra` : `Using index` = covering, `Using filesort` = tri disque, `Using temporary` = table temporaire
- `filtered` : % de lignes filtrées après index scan

### 1.3 MongoDB — explain

```javascript
db.mesures.find({
    capteur_id: "TEMP-A001",
    ts: { $gte: ISODate("2025-06-01") },
    temperature: { $gt: 100 }
}).sort({ ts: -1 }).explain("executionStats");

// Indicateurs clés :
// executionStats.totalDocsExamined vs totalKeysExamined
// IXSCAN vs COLLSCAN
// executionTimeMillis
```

---

## 2. Slow Query Log

### 2.1 PostgreSQL

```conf
# postgresql.conf
log_min_duration_statement = 500       # log les requêtes > 500ms
log_line_prefix = '%t [%p]: [%l-%x] '  # timestamp, pid, session
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0                      # log les fichiers temporaires
```

### 2.2 MySQL

```ini
[mysqld]
slow_query_log = ON
slow_query_log_file = /var/log/mysql/slow-queries.log
long_query_time = 0.5                  # 500ms
log_queries_not_using_indexes = ON
log_slow_admin_statements = ON
```

### 2.3 Analyse avec pt-query-digest (Percona Toolkit)

```bash
# Analyse du slow query log
pt-query-digest /var/log/mysql/slow-queries.log

# Analyse en temps réel
pt-query-digest --processlist h=localhost

# PostgreSQL
pt-query-digest --type pgslowlog /var/log/postgresql/slow.log
```

---

## 3. Configuration Mémoire

### 3.1 PostgreSQL — Mémoire

```ini
# RAM totale : 32 GB
shared_buffers = '8G'                # 25% de la RAM
effective_cache_size = '24G'         # 75% de la RAM (estimation du cache OS)
work_mem = '32MB'                    # Mémoire par tri/hash (attention : × n_connections)
maintenance_work_mem = '1GB'         # VACUUM, CREATE INDEX
wal_buffers = '16MB'                 # 1/32 de shared_buffers

# Éviter le swapping
vm.swappiness = 1
```

### 3.2 MySQL — Mémoire

```ini
[mysqld]
# RAM 32 GB
innodb_buffer_pool_size = '24G'      # 70-80% de la RAM (InnoDB)
innodb_buffer_pool_instances = 8     # 1 instance par 2-4 GB
innodb_log_file_size = '2G'
innodb_log_buffer_size = '64M'
tmp_table_size = '64M'
max_heap_table_size = '64M'
sort_buffer_size = '4M'
read_buffer_size = '2M'
read_rnd_buffer_size = '4M'
join_buffer_size = '2M'
```

### 3.3 MongoDB — Cache

```bash
# WiredTiger cache (défaut: 50% de RAM - 1GB)
# /etc/mongod.conf
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 16  # sur 32 GB de RAM
```

---

## 4. Parallélisme

### 4.1 PostgreSQL

```ini
# PostgreSQL 16
max_parallel_workers = 8
max_parallel_workers_per_gather = 4
parallel_tuple_cost = 0.01
parallel_setup_cost = 100
min_parallel_table_scan_size = '8MB'
min_parallel_index_scan_size = '512MB'

# Forcer le parallélisme pour les analyses
SET parallel_leader_participation = on;
```

### 4.2 MySQL (pas de parallélisme automatique)

MySQL n'a pas de parallélisme de requêtes natif (sauf MySQL HeatWave). Alternatives :
- Utiliser le connection pooling pour paralléliser au niveau applicatif
- Diviser les requêtes manuellement (sharding)
- Utiliser MySQL 8.0.17+ avec `innodb_parallel_read_threads` pour les scans

---

## 5. Connection Pooling

### 5.1 PgBouncer (PostgreSQL)

```ini
[databases]
eva_prod = host=192.168.1.10 port=5432 dbname=eva_prod

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt

pool_mode = transaction          # transaction pooling (recommandé)
default_pool_size = 25           # max connexions par pool
max_client_conn = 200            # connexions clients max
reserve_pool_size = 5
reserve_pool_timeout = 3.0
server_idle_timeout = 300
query_timeout = 30
```

### 5.2 ProxySQL (MySQL)

```ini
[mysql_variables]
mysql-threads=8
mysql-max_connections=1000
default_query_delay=0
default_query_timeout=36000000
have_compress=true

# Configuration du pool
mysql_servers:
  +-----------+-----------+------+-----------+--------+---------+
  | hostgroup | hostname  | port | weight    | status | ...     |
  +-----------+-----------+------+-----------+--------+---------+
  | 0         | 10.0.0.1  | 3306 | 1         | ONLINE | ...     |
  | 0         | 10.0.0.2  | 3306 | 1         | ONLINE | ...     |
  +-----------+-----------+------+-----------+--------+---------+

mysql_query_rules:
  SELECT * FROM mesures → hostgroup 0 (lecture)
  INSERT INTO mesures  → hostgroup 1 (écriture)
```

---

## 6. Cache Stratégies

### 6.1 Cache Redis (en amont de la DB)

```python
import redis, json, time
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_capteur(capteur_id, force_refresh=False):
    cache_key = f"capteur:{capteur_id}"
    
    # Refresh forcé (invalidation)
    if force_refresh:
        r.delete(cache_key)
    
    # Cache-aside pattern
    cached = r.get(cache_key)
    if cached is not None and not force_refresh:
        return json.loads(cached)
    
    start = time.time()
    data = query_db(f"SELECT * FROM capteurs WHERE id = {capteur_id}")
    query_time = (time.time() - start) * 1000
    
    # Mettre en cache seulement si la requête était lente
    if query_time > 100:  # > 100ms
        r.setex(cache_key, 300, json.dumps(data))
    
    return data
```

### 6.2 Cache du plans (Prepared Statements)

```sql
-- PostgreSQL : cache des plans
-- PREPARE + EXECUTE évite de re-planifier
PREPARE capteur_query(INT) AS
    SELECT * FROM capteurs WHERE id = $1;
EXECUTE capteur_query(42);

-- Le plan est mis en cache pour les 5 premières exécutions
-- (configurable avec plan_cache_mode = force_custom_plan)
```

---

## 7. Statistiques et Autovacuum

### 7.1 PostgreSQL — Statistiques

```sql
-- Vérifier les statistiques
SELECT
    attname,
    n_distinct,         -- cardinalité estimée
    correlation,        -- corrélation physique (1.0 = parfaitement trié)
    null_frac,           -- fraction de NULLs
    avg_width           -- taille moyenne en bytes
FROM pg_stats
WHERE tablename = 'mesures'
ORDER BY attname;
```

### 7.2 Autovacuum tuning

```ini
# postgresql.conf
autovacuum = on
autovacuum_max_workers = 4
autovacuum_naptime = '1min'
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.01     # 1% de lignes mortes
autovacuum_analyze_scale_factor = 0.005   # 0.5% de changements
autovacuum_vacuum_cost_limit = 2000
autovacuum_vacuum_cost_delay = 2          # ms

# Per-table override pour les tables chaudes
ALTER TABLE mesures SET (
    autovacuum_vacuum_scale_factor = 0.005,
    autovacuum_analyze_scale_factor = 0.001,
    autovacuum_vacuum_cost_limit = 5000
);
```

---

## 8. Monitoring

### 8.1 PostgreSQL — pg_stat_statements

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 des requêtes par temps total
SELECT
    queryid,
    ROUND(total_exec_time::NUMERIC / 1000, 2) AS total_sec,
    ROUND(mean_exec_time::NUMERIC, 2) AS mean_ms,
    calls,
    ROUND(100.0 * shared_blks_hit / GREATEST(shared_blks_hit + shared_blks_read, 1), 1) AS cache_hit_ratio,
    ROUND(rows / GREATEST(calls, 1)) AS avg_rows,
    query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 8.2 Table de monitoring complet

```sql
-- Tableau de bord perf
WITH perf AS (
    SELECT
        (SELECT count(*) FROM pg_stat_activity WHERE state != 'idle') AS connexions_actives,
        (SELECT count(*) FROM pg_locks WHERE NOT granted) AS verrous_bloquants,
        (SELECT ROUND(xact_commit::NUMERIC / GREATEST(xact_commit + xact_rollback, 1) * 100, 1)
         FROM pg_stat_database WHERE datname = current_database()) AS taux_succes_transactions,
        (SELECT ROUND(100.0 * sum(heap_blks_hit) / GREATEST(sum(heap_blks_hit) + sum(heap_blks_read), 1), 1)
         FROM pg_statio_user_tables) AS cache_hit_ratio
)
SELECT * FROM perf;
```

### 8.3 Outils de monitoring

| SGBD | Outil | Commande |
|------|-------|----------|
| PostgreSQL | pg_stat_statements | Intégré |
| PostgreSQL | pg_top | `pg_top` |
| PostgreSQL | pgBadger | `pgbadger /var/log/postgresql/postgresql*.log` |
| MySQL | PMM (Percona) | `docker run percona/pmm-server` |
| MySQL | MySQLTuner | `mysqltuner` |
| MySQL | innotop | `innotop` |
| MongoDB | mongostat | `mongostat -h localhost:27017` |
| MongoDB | mongotop | `mongotop -h localhost:27017` |
| Redis | redis-cli info | `redis-cli INFO stats` |
| Tout | Prometheus + Grafana | Exporters dédiés |

---

## Pièges Courants

1. **work_mem trop grand.** `work_mem` est multiplié par le nombre de connexions et le nombre de tris simultanés. `work_mem = 1GB` avec 200 connexions = 200 GB potentiels. Un crash est probable.

2. **Pas de connection pooling.** PostgreSQL supporte mal > 200 connexions directes (fork par connexion). Toujours mettre PgBouncer ou ProxySQL en face.

3. **Planificateur trompé par des stats obsolètes.** Autovacuum insuffisant = statistiques obsolètes = mauvais plans. Vérifier `last_analyze` dans `pg_stat_user_tables`.

4. **Requêtes N+1.** 100 requêtes individuelles au lieu d'une jointure. Détectable dans le slow query log : 100 requêtes identiques dans la même seconde.

5. **Paramètres de configuration copiés depuis internet sans validation.** Les configs "magiques" (pgTune, MySQLTuner) sont des points de départ, pas des réponses absolues. Tester avec votre workload réel.

6. **Oublier que le cache OS existe.** `effective_cache_size` ne réserve PAS de mémoire — il informe le planner de la taille du cache OS. Le fixer trop bas = sous-estimation des index-only scans.

---

## Checklist

- [ ] EXPLAIN ANALYZE vérifié sur les requêtes les plus lentes (top 10)
- [ ] Slow query log activé avec seuil à 500ms (500ms)
- [ ] shared_buffers configuré à 25% RAM, effective_cache_size à 75%
- [ ] Connection pooling en place (PgBouncer/ProxySQL)
- [ ] pg_stat_statements actif et monitoré
- [ ] Statistiques autovacuum à jour (`last_analyze` < 1 jour)
- [ ] Index inutilisés identifiés et supprimés
- [ ] Cache Redis/memcached en amont des requêtes fréquentes
- [ ] Prepared statements utilisées pour les requêtes répétitives
- [ ] Benchmark établi avant/après chaque optimisation majeure