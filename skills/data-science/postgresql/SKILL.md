---
name: postgresql
description: "Guide complet PostgreSQL — installation, administration, SQL avancé, PL/pgSQL, replication logique, HAPartitioning, tuning, et sécurisation niveau production."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [postgresql, sql, base-de-donnees, relationnel, plpgsql, replication, administration, performance]
    homepage: https://www.postgresql.org/
    related_skills: [mysql, sqlite, indexation-bases-donnees, replication-haute-disponibilite, sauvegarde-restauration, optimisation-performance]
prerequisites:
  commands: [psql, pg_isready, pg_dump, pg_restore, createdb]
---

# Compétence PostgreSQL — Administration, SQL Avancé et Exploitation

## Vue d'ensemble

PostgreSQL (Postgres) est le SGBD relationnel open-source le plus avancé. Il supporte les transactions ACID, les index avancés (B-tree, Hash, GiST, GIN, SP-GiST, BRIN), le partitionnement natif, la replication logique, les extensions (PostGIS, TimescaleDB, pg_partman), et une conformité SQL exceptionnelle.

Cette compétence couvre l'installation, la configuration, le SQL avancé, la programmation PL/pgSQL, l'administration système, la réplication, le partitionnement, et l'optimisation des performances.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Demande d'installer ou de configurer PostgreSQL (9.6 à 17+)
- A besoin d'écrire des requêtes SQL avancées (CTE, fenêtrage, récursives)
- Souhaite créer des fonctions, triggers, ou procédures stockées en PL/pgSQL
- Veut configurer la réplication logique ou streaming
- Demande du partitionnement de tables (range, list, hash)
- A besoin de diagnostiquer des lenteurs (EXPLAIN ANALYZE, pg_stat_statements)
- Veut sécuriser une instance (SSL, pg_hba.conf, rôle ACL)

---

## 1. Installation et Configuration

### 1.1 Installation Debian/Ubuntu

```bash
# Ajout du dépôt officiel PostgreSQL
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
sudo apt update
sudo apt install -y postgresql-16 postgresql-client-16 postgresql-contrib-16

# Démarrage et activation
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 1.2 Configuration postgresql.conf essentielle

```conf
# Fichier: /etc/postgresql/16/main/postgresql.conf

# Mémoire
shared_buffers = '4GB'             # 25% de la RAM
effective_cache_size = '12GB'      # 75% de la RAM
work_mem = '64MB'                  # par opération de tri
maintenance_work_mem = '1GB'       # pour VACUUM, CREATE INDEX

# Écriture
wal_level = 'replica'              # nécessaire pour la réplication
max_wal_size = '4GB'
min_wal_size = '1GB'
wal_buffers = '16MB'
synchronous_commit = 'on'          # 'off' pour +10% perf en échange de risque

# Connexions
max_connections = 200
listen_addresses = 'localhost'     # liste d'IP autorisées

# Planificateur
random_page_cost = 1.1             # 1.1 pour SSD, 4.0 pour HDD
effective_io_concurrency = 200      # SSD haute performance
default_statistics_target = 500    # meilleures stats = meilleurs plans

# Parallélisme
max_parallel_workers = 8
max_parallel_workers_per_gather = 4
parallel_tuple_cost = 0.01
parallel_setup_cost = 100

# Autovacuum (critique)
autovacuum = on
autovacuum_vacuum_scale_factor = 0.01
autovacuum_analyze_scale_factor = 0.005
autovacuum_vacuum_threshold = 50
autovacuum_naptime = '1min'
```

### 1.3 pg_hba.conf — Sécurité des connexions

```conf
# Fichier: /etc/postgresql/16/main/pg_hba.conf

# Authentification locale (socket Unix)
local   all             all                               peer

# IPv4 local
host    all             all             127.0.0.1/32      scram-sha-256

# Réplication
local   replication     replicator                        peer
host    replication     replicator     10.0.0.0/8         scram-sha-256

# Application distante avec certificat
hostssl all             app_user        10.0.0.0/8        cert
```

---

## 2. SQL Avancé

### 2.1 CTE Récursives (WITH RECURSIVE)

```sql
-- Hiérarchie d'employés (table: employees(id, name, manager_id))
WITH RECURSIVE org_tree AS (
    -- Racine : le PDG
    SELECT id, name, manager_id, 1 AS niveau, name::text AS chemin
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Récurrence : les N-1, N-2, etc.
    SELECT e.id, e.name, e.manager_id,
           ot.niveau + 1,
           ot.chemin || ' -> ' || e.name
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY chemin;
```

### 2.2 Fenêtrage (Window Functions)

```sql
-- Rang, moyenne mobile, lead/lag
SELECT
    date, valeur,
    ROW_NUMBER() OVER (PARTITION BY capteur_id ORDER BY date) AS rang,
    AVG(valeur) OVER (
        PARTITION BY capteur_id
        ORDER BY date
        ROWS BETWEEN 7 PRECEDING AND CURRENT ROW
    ) AS moyenne_mobile_7j,
    LAG(valeur, 1) OVER (PARTITION BY capteur_id ORDER BY date) AS valeur_precedente,
    LEAD(valeur, 1) OVER (PARTITION BY capteur_id ORDER BY date) AS valeur_suivante,
    valeur - LAG(valeur, 1) OVER (PARTITION BY capteur_id ORDER BY date) AS delta
FROM mesures_capteurs;
```

### 2.3 Aggrégation avec FILTER

```sql
SELECT
    machine_id,
    COUNT(*) AS total_cycles,
    COUNT(*) FILTER (WHERE statut = 'OK') AS cycles_ok,
    COUNT(*) FILTER (WHERE statut = 'ALARME') AS cycles_alarme,
    ROUND(100.0 * COUNT(*) FILTER (WHERE statut = 'OK') / COUNT(*), 2) AS taux_conformite
FROM production_cycles
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY machine_id;
```

### 2.4 Génération de séries et Gap Filling

```sql
-- Remplir les trous temporels avec des zéros
WITH heures AS (
    SELECT generate_series(
        date_trunc('hour', NOW() - INTERVAL '24 hours'),
        date_trunc('hour', NOW()),
        '1 hour'::interval
    ) AS heure
)
SELECT
    h.heure,
    COALESCE(SUM(p.quantite), 0) AS production
FROM heures h
LEFT JOIN production p
    ON date_trunc('hour', p.timestamp) = h.heure
GROUP BY h.heure
ORDER BY h.heure;
```

---

## 3. PL/pgSQL — Fonctions, Procédures et Triggers

### 3.1 Fonction avec paramètres

```sql
CREATE OR REPLACE FUNCTION calculer_statistiques(
    p_machine_id INT,
    p_periode_depuis TIMESTAMPTZ DEFAULT NOW() - INTERVAL '7 days'
)
RETURNS TABLE(
    nb_cycles BIGINT,
    temps_moyen_cycle NUMERIC,
    taux_erreur NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        AVG(duree_cycle_ms)::NUMERIC,
        ROUND(100.0 * SUM(CASE WHEN statut != 'OK' THEN 1 ELSE 0 END) / COUNT(*), 2)
    FROM cycles
    WHERE machine_id = p_machine_id
      AND timestamp >= p_periode_depuis;
END;
$$;
```

### 3.2 Trigger d'audit et historisation

```sql
-- Table d'audit
CREATE TABLE audit_changements (
    id BIGSERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id INT NOT NULL,
    old_data JSONB,
    new_data JSONB,
    changed_by TEXT,
    changed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Fonction trigger générique
CREATE OR REPLACE FUNCTION audit_trigger_fn()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_changements(table_name, record_id, old_data, new_data, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, row_to_json(OLD)::JSONB, row_to_json(NEW)::JSONB, current_user);
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_changements(table_name, record_id, old_data, changed_by)
        VALUES (TG_TABLE_NAME, OLD.id, row_to_json(OLD)::JSONB, current_user);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$;

-- Attacher le trigger à une table
CREATE TRIGGER audit_machines
AFTER UPDATE OR DELETE ON machines
FOR EACH ROW
EXECUTE FUNCTION audit_trigger_fn();
```

### 3.3 Procédure avec transaction et rollback partiel (savepoint)

```sql
CREATE OR REPLACE PROCEDURE transferer_stock(
    p_origine INT,
    p_destination INT,
    p_quantite INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    disponible INT;
BEGIN
    -- Vérification et lock
    SELECT quantite INTO disponible
    FROM stocks WHERE produit_id = p_origine
    FOR UPDATE;  -- verrouillage pessimiste

    IF disponible < p_quantite THEN
        RAISE EXCEPTION 'Stock insuffisant : % disponible, % requis', disponible, p_quantite;
    END IF;

    -- Débit
    UPDATE stocks SET quantite = quantite - p_quantite
    WHERE produit_id = p_origine;

    -- Crédit
    UPDATE stocks SET quantite = quantite + p_quantite
    WHERE produit_id = p_destination;

    COMMIT;
END;
$$;
```

---

## 4. Partitionnement Natif

### 4.1 Partition Range (par mois)

```sql
-- Table partitionnée
CREATE TABLE mesures (
    timestamp TIMESTAMPTZ NOT NULL,
    machine_id INT NOT NULL,
    temperature NUMERIC,
    pression NUMERIC
) PARTITION BY RANGE (timestamp);

-- Partitions mensuelles
CREATE TABLE mesures_2025_01 PARTITION OF mesures
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE mesures_2025_02 PARTITION OF mesures
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

-- Index local (indépendant par partition)
CREATE INDEX idx_mesures_machine_2025_01 ON mesures_2025_01 (machine_id);
CREATE INDEX idx_mesures_machine_2025_02 ON mesures_2025_02 (machine_id);

-- Fonction de création automatique de partitions mensuelles
CREATE OR REPLACE FUNCTION creer_partition_si_necessaire()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    debut DATE;
    fin DATE;
    nom_partition TEXT;
BEGIN
    FOR i IN 0..2 LOOP  -- crée les 3 prochains mois
        debut := date_trunc('month', CURRENT_DATE + (i || ' months')::INTERVAL)::DATE;
        fin := (debut + INTERVAL '1 month')::DATE;
        nom_partition := 'mesures_' || TO_CHAR(debut, 'YYYY_MM');

        IF NOT EXISTS (
            SELECT 1 FROM pg_class WHERE relname = nom_partition
        ) THEN
            EXECUTE format(
                'CREATE TABLE %I PARTITION OF mesures FOR VALUES FROM (%L) TO (%L)',
                nom_partition, debut, fin
            );
        END IF;
    END LOOP;
END;
$$;
```

### 4.2 Partition Hash pour distribution uniforme

```sql
CREATE TABLE logs_evenements (
    id BIGSERIAL,
    evenement TEXT,
    niveau TEXT,
    payload JSONB
) PARTITION BY HASH (id);

CREATE TABLE logs_evenements_0 PARTITION OF logs_evenements
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE logs_evenements_1 PARTITION OF logs_evenements
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE logs_evenements_2 PARTITION OF logs_evenements
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE logs_evenements_3 PARTITION OF logs_evenements
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## 5. Extensions Puissantes

### 5.1 pg_stat_statements — Analyse des requêtes

```sql
-- Activer dans postgresql.conf
-- shared_preload_libraries = 'pg_stat_statements'
-- puis redémarrer

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Top 10 des requêtes les plus lentes
SELECT
    queryid,
    ROUND(total_exec_time::NUMERIC / 1000, 2) AS total_seconds,
    ROUND(mean_exec_time::NUMERIC, 2) AS mean_ms,
    calls,
    ROUND(shared_blks_hit::NUMERIC / GREATEST(shared_blks_hit + shared_blks_read, 1) * 100, 1) AS cache_hit_ratio,
    query
FROM pg_stat_statements
WHERE query NOT LIKE '%pg_stat%'
ORDER BY total_exec_time DESC
LIMIT 10;
```

### 5.2 PostGIS — Géospatial

```sql
CREATE EXTENSION IF NOT EXISTS postgis;

-- Table avec colonne géographique
CREATE TABLE sites_industriels (
    id SERIAL PRIMARY KEY,
    nom TEXT,
    geom GEOMETRY(Point, 4326)
);

-- Index spatial
CREATE INDEX idx_sites_geom ON sites_industriels USING GIST (geom);

-- Requête de distance
SELECT nom, ST_DistanceSphere(geom, ST_SetSRID(ST_MakePoint(4.387, 45.441), 4326)) AS distance_m
FROM sites_industriels
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(4.387, 45.441), 4326)
LIMIT 10;
```

### 5.3 pg_partman — Gestion automatisée du partitionnement

```sql
CREATE EXTENSION IF NOT EXISTS pg_partman;

-- Configuration d'une partition automatique mensuelle
SELECT partman.create_parent(
    p_parent_table := 'public.mesures',
    p_control := 'timestamp',
    p_type := 'native',
    p_interval := '1 month',
    p_premake := 3
);

-- Maintenance automatique (à planifier en cron)
-- SELECT partman.run_maintenance();
```

### 5.4 TimescaleDB — Séries temporelles

```sql
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Créer une hypertable
SELECT create_hypertable('mesures', 'timestamp', chunk_time_interval => INTERVAL '1 day');

-- Compression automatique (après 7 jours)
ALTER TABLE mesures SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'machine_id'
);
SELECT add_compression_policy('mesures', INTERVAL '7 days');

-- Continuous aggregates (vues matérialisées automatiques)
CREATE MATERIALIZED VIEW mesures_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', timestamp) AS heure,
    machine_id,
    AVG(temperature) AS temp_moyenne,
    MAX(temperature) AS temp_max
FROM mesures
GROUP BY heure, machine_id;
```

---

## 6. Diagnostic des Performances

### 6.1 EXPLAIN ANALYZE

```sql
-- Plan d'exécution avec coûts réels
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT m.*, c.nom
FROM mesures m
JOIN capteurs c ON m.capteur_id = c.id
WHERE m.timestamp >= '2025-06-01'
  AND m.temperature > 100
ORDER BY m.timestamp DESC;
```

### 6.2 Requêtes en cours et verrous

```sql
-- Sessions actives et leur requête
SELECT
    pid,
    now() - pg_stat_activity.query_start AS duree,
    state,
    wait_event_type || ': ' || wait_event AS attente,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND pid != pg_backend_pid()
ORDER BY duree DESC;

-- Verrous bloquants
SELECT
    blocked.pid AS pid_bloque,
    blocked.query AS requete_bloquee,
    blocking.pid AS pid_bloqueur,
    blocking.query AS requete_bloquante
FROM pg_locks blocked
JOIN pg_stat_activity blocked_act ON blocked.pid = blocked_act.pid
JOIN pg_locks blocking ON blocked.locktype = blocking.locktype
    AND blocked.database = blocking.database
    AND blocked.relation = blocking.relation
    AND blocked.pid != blocking.pid
JOIN pg_stat_activity blocking_act ON blocking.pid = blocking_act.pid
WHERE NOT blocked.granted;
```

### 6.3 Taille des tables et index

```sql
SELECT
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_table_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    n_live_tup AS lignes_estimees,
    n_dead_tup AS lignes_mortes,
    ROUND(100.0 * n_dead_tup / GREATEST(n_live_tup + n_dead_tup, 1), 2) AS dead_ratio
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

---

## 7. Réplication Logique

### 7.1 Configuration du Publisher

```sql
-- postgresql.conf du Publisher
-- wal_level = 'logical'
-- max_replication_slots = 10
-- max_wal_senders = 10

-- Publication
CREATE PUBLICATION pub_production
FOR TABLE mesures, machines, capteurs
WITH (publish = 'insert, update, delete');
```

### 7.2 Configuration du Subscriber

```sql
-- Subscription avec connexion au Publisher
CREATE SUBSCRIPTION sub_production
CONNECTION 'host=192.168.1.10 port=5432 dbname=prod user=replicator password=***'
PUBLICATION pub_production
WITH (copy_data = true);
```

---

## Pièges Courants

1. **Autovacuum insuffisant.** Des ratios élevés de `n_dead_tup` (dead rows) ralentissent les index et gonflent la taille. Solution : ajuster `autovacuum_vacuum_scale_factor` à 0.01 sur les tables fréquemment modifiées.

2. **work_mem trop bas pour des tris volumineux.** PostgreSQL écrit sur disque si `work_mem` est dépassé. Utiliser `EXPLAIN ANALYZE` pour repérer les `External Sort`.

3. **Pas d'index adaptés aux filtres de requêtes.** Une clause `WHERE` sur une colonne non indexée provoque un `Seq Scan` sur toute la table. Utiliser `pg_stat_user_indexes` pour détecter les index inutilisés.

4. **Forcer des requêtes DISTINCT inutilesment.** `EXISTS` est presque toujours plus rapide que `DISTINCT` ou `IN` sur de grands volumes.

5. **Index B-tree sur des colonnes de faible cardinalité (booléens, statuts).** Préférer un `partial index` : `CREATE INDEX idx_alertes_critiques ON mesures(valeur) WHERE niveau = 'CRITIQUE'`.

6. **Oublier VACUUM FREEZE** sur les tables partitionnées anciennes. Sur des partitions en lecture seule, ajouter un `VACUUM FREEZE` manuel pour éviter un wrap-around de XID.

---

## Checklist

- [ ] `shared_buffers` configuré à 25% de la RAM
- [ ] `effective_cache_size` à 75% de la RAM
- [ ] `wal_level = 'replica'` si réplication nécessaire
- [ ] Extensions critiques installées : `pg_stat_statements`, `postgis` (si géospatial), `pg_partman` (si partitionnement)
- [ ] pg_hba.conf utilise `scram-sha-256`, pas `trust` en production
- [ ] Index créés selon les `WHERE`, `JOIN`, `ORDER BY` des requêtes réelles
- [ ] Partitionnement mis en place pour les tables > 100M lignes
- [ ] Réplication logique testée avec un slot de réplication
- [ ] pg_dump/pg_restore testé avec restauration sur un serveur de staging
- [ ] `autovacuum` actif et monitoré via `pg_stat_user_tables`