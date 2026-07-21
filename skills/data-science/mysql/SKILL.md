---
name: mysql
description: "Guide complet MySQL/MariaDB — installation, administration, requêtes avancées, stockage, réplication, tuning InnoDB, sécurisation, et migration vers MySQL 8.4+."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [mysql, mariadb, sql, base-de-donnees, relationnel, innodb, replication, performance]
    homepage: https://dev.mysql.com/
    related_skills: [postgresql, sqlite, indexation-bases-donnees, replication-haute-disponibilite, sauvegarde-restauration, optimisation-performance]
prerequisites:
  commands: [mysql, mysqldump, mysqladmin, mysqlsh]
---

# Compétence MySQL/MariaDB — Administration, Requêtes Avancées et Exploitation

## Vue d'ensemble

MySQL (et son fork MariaDB) est le SGBD relationnel le plus déployé au monde, dominant le web (LAMP/LEMP), les applications SaaS, et les grands comptes (Meta, Uber, Netflix). Depuis MySQL 8.0, il supporte les CTE, les window functions, les indexes fonctionnels, le Document Store, et le Group Replication.

Cette compétence couvre l'installation, la configuration InnoDB avancée, les index, le partitionnement, les procédures stockées, la réplication, le tuning, et les bonnes pratiques de sécurisation.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Demande d'installer ou configurer MySQL/MariaDB
- A besoin de requêtes SQL avancées (fenêtrage, CTE, sous-requêtes)
- Veut optimiser un moteur InnoDB (buffer pool, log file, threads)
- Doit configurer la réplication (source → replica, Group Replication, Galera)
- Veut migrer de MySQL 5.7 vers 8.4+ ou de MariaDB vers MySQL
- A besoin de mysqldump, mysqlpump, ou MySQL Shell pour backup

---

## 1. Installation et Configuration

### 1.1 Installation MySQL 8.4+ sur Debian

```bash
# Ajout du dépôt officiel MySQL
wget https://dev.mysql.com/get/mysql-apt-config_0.8.30-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.30-1_all.deb
sudo apt update
sudo apt install -y mysql-server

# Sécurisation
sudo mysql_secure_installation
```

### 1.2 Configuration InnoDB (my.cnf)

```ini
[mysqld]
# Moteur de stockage
default_storage_engine = InnoDB

# Buffer Pool (l'essentiel de la mémoire InnoDB)
innodb_buffer_pool_size = 8G          # 50-70% de la RAM
innodb_buffer_pool_instances = 8      # 1 instance / 1 Go de buffer pool

# Redo Log (ib_logfile)
innodb_log_file_size = 2G             # recommandé = 25% du buffer pool
innodb_log_buffer_size = 64M
innodb_flush_log_at_trx_commit = 1    # 1 = ACID complet, 2 = +rapide mais perte possible

# I/O
innodb_io_capacity = 2000             # pour SSD
innodb_io_capacity_max = 4000
innodb_flush_method = O_DIRECT        # évite le double cache du FS

# Threads
innodb_thread_concurrency = 0         # 0 = auto (recommandé)
innodb_read_io_threads = 8
innodb_write_io_threads = 8

# Connexions
max_connections = 500
thread_cache_size = 64

# Query Cache (déprécié depuis 8.0 — désactivé)
query_cache_type = 0
```

### 1.3 MariaDB specifics

```ini
[mariadb]
# Moteur de stockage par défaut
default_storage_engine = InnoDB

# Moteurs alternatifs MariaDB
# Aria — transactionnel, pas de redo log (plus rapide en écriture)
# MyRocks — basé sur RocksDB, meilleure compression pour write-heavy
# Spider — fédération et sharding intégré

# Optimizer
optimizer_use_condition_selectivity = 1  # meilleures stats histogramme
histogram_size = 254                     # précision des histogrammes
```

---

## 2. SQL Avancé MySQL

### 2.1 CTE et Fenêtrage (MySQL 8.0+)

```sql
-- CTE simple avec fenêtrage
WITH stats_machines AS (
    SELECT
        machine_id,
        DATE(timestamp) AS jour,
        AVG(temperature) AS temp_moy,
        STDDEV(temperature) AS temp_std
    FROM mesures
    GROUP BY machine_id, DATE(timestamp)
)
SELECT
    machine_id,
    jour,
    temp_moy,
    temp_moy - AVG(temp_moy) OVER (
        PARTITION BY machine_id
        ORDER BY jour
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS ecart_moyenne_mobile
FROM stats_machines;
```

### 2.2 Index Fonctionnels (MySQL 8.0.13+)

```sql
-- Index sur une expression (pas besoin de colonne dérivée)
ALTER TABLE utilisateurs
    ADD INDEX idx_email_domaine ((SUBSTRING_INDEX(email, '@', -1)));

-- Index sur JSON
ALTER TABLE logs
    ADD INDEX idx_log_niveau ((CAST(log_data->>'$.niveau' AS CHAR(20))));
```

### 2.3 Document Store (X Plugin)

```sql
-- Collection JSON avec index
CREATE TABLE catalog_produits (
    id BINARY(16) PRIMARY KEY,
    doc JSON,
    INDEX idx_categorie ((CAST(doc->>'$.categorie' AS CHAR(50))))
);

-- Recherche dans le document JSON
SELECT id, doc->>'$.nom' AS nom
FROM catalog_produits
WHERE JSON_CONTAINS(doc, '"électronique"', '$.tags');

-- Index multi-valeurs pour les tableaux JSON
ALTER TABLE catalog_produits
    ADD INDEX idx_tags ((CAST(doc->>'$.tags' AS CHAR(100) ARRAY)));
```

---

## 3. Administration InnoDB Avancée

### 3.1 Monitoring du Buffer Pool

```sql
-- Taux de hit du buffer pool (doit être > 95%)
SELECT
    ROUND(100 * (
        SELECT SUM(a.innodb_buffer_pool_read_requests)
        FROM information_schema.INNODB_METRICS a
        WHERE a.name = 'buffer_pool_read_requests'
    ) / (
        SELECT SUM(b.innodb_buffer_pool_read_requests + b.innodb_buffer_pool_reads)
        FROM information_schema.INNODB_METRICS b
        WHERE b.name IN ('buffer_pool_read_requests', 'buffer_pool_reads')
    ), 2) AS buffer_pool_hit_ratio;
```

### 3.2 Fragmentation des tables

```sql
-- Tables les plus fragmentées
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    ROUND(DATA_LENGTH / 1024 / 1024, 2) AS data_mb,
    ROUND(INDEX_LENGTH / 1024 / 1024, 2) AS index_mb,
    ROUND(DATA_FREE / 1024 / 1024, 2) AS free_mb,
    ROUND(100 * DATA_FREE / (DATA_LENGTH + INDEX_LENGTH + DATA_FREE), 2) AS frag_pct
FROM information_schema.TABLES
WHERE TABLE_SCHEMA NOT IN ('mysql', 'performance_schema', 'sys')
  AND DATA_LENGTH + INDEX_LENGTH > 104857600  -- > 100 MB
ORDER BY free_mb DESC;
```

### 3.3 Optimiser une table fragmentée

```sql
-- Reconstruit la table et les index (InnoDB)
ALTER TABLE mesures ENGINE=InnoDB, ALGORITHM=INPLACE, LOCK=NONE;

-- Analyse des statistiques
ANALYZE TABLE mesures;

-- Optimize (équivalent à ALTER + ANALYZE, verrouille en MySQL < 8.0.25)
OPTIMIZE TABLE mesures;
```

---

## 4. Indexation Avancée

### 4.1 Index composites optimaux

```sql
-- Règle : colonnes d'égalité d'abord, puis de tri, puis de plage
-- BON : WHERE machine_id = ? AND statut = ? ORDER BY timestamp
CREATE INDEX idx_covering ON mesures (machine_id, statut, timestamp);

-- Index couvrant (covering index) : toutes les colonnes de la requête
-- Évite de lire les lignes depuis la table (réduit I/O de 90%)
CREATE INDEX idx_covering_full ON mesures (machine_id, statut, timestamp, temperature, pression);
```

### 4.2 Index DESC / ASC

```sql
-- Trie descendant pour ORDER BY ... DESC (MySQL 8.0+)
CREATE INDEX idx_timestamp_desc ON mesures (machine_id, timestamp DESC);
```

### 4.3 Index invisible (test avant suppression)

```sql
-- Rendre un index invisible pour tester si les requêtes en ont besoin
ALTER TABLE mesures ALTER INDEX idx_peu_utile INVISIBLE;

-- Attendre 24h, puis vérifier les requêtes lentes
-- Si pas d'impact, suppression définitive
DROP INDEX idx_peu_utile ON mesures;
```

---

## 5. Partitionnement

### 5.1 Partitionnement par plage (RANGE)

```sql
CREATE TABLE logs_systeme (
    id BIGINT NOT NULL,
    date_log DATE NOT NULL,
    niveau ENUM('INFO', 'WARN', 'ERROR', 'CRITICAL'),
    message TEXT,
    PRIMARY KEY (id, date_log)
) PARTITION BY RANGE (YEAR(date_log)) (
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 5.2 Partition pruning

```sql
-- MySQL n'utilise que les partitions nécessaires
-- avec cette clause :
EXPLAIN SELECT * FROM logs_systeme
WHERE date_log BETWEEN '2025-01-01' AND '2025-06-30';
-- Vérifier 'partitions' dans l'EXPLAIN : doit montrer p2025 seulement
```

### 5.3 Exchange partition (archivage instantané)

```sql
-- Échanger une partition avec une table vide (instantané)
CREATE TABLE logs_2023_archive LIKE logs_systeme;

ALTER TABLE logs_systeme
    EXCHANGE PARTITION p2023
    WITH TABLE logs_2023_archive;

-- Maintenant logs_2023_archive contient les anciennes données
-- On peut l'exporter/compresser/supprimer
```

---

## 6. Réplication

### 6.1 Réplication Asynchrone (Source → Réplica)

```sql
-- Sur le SOURCE :
CREATE USER 'replicator'@'%' IDENTIFIED BY '***';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;

SHOW MASTER STATUS\G
-- Retenir File et Position

-- Sur le RÉPLICA :
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='192.168.1.10',
    SOURCE_USER='replicator',
    SOURCE_PASSWORD='***',
    SOURCE_LOG_FILE='mysql-bin.000017',
    SOURCE_LOG_POS=851243;

START REPLICA;
SHOW REPLICA STATUS\G
-- Vérifier : Seconds_Behind_Source: 0
```

### 6.2 Semi-Sync (réduction des pertes)

```ini
[mysqld]
# Activer sur SOURCE ET RÉPLICA
plugin_load = "rpl_semi_sync_source=semisync_source.so;rpl_semi_sync_replica=semisync_replica.so"
rpl_semi_sync_source_enabled = 1
rpl_semi_sync_replica_enabled = 1
rpl_semi_sync_source_timeout = 1000  # ms avant fallback async
```

### 6.3 Group Replication (HA multi-source)

```sql
-- Configuration minimale (3 nœuds)
-- my.cnf
-- server_id = 1
-- gtid_mode = ON
-- enforce_gtid_consistency = ON
-- binlog_checksum = NONE
-- plugin_load_add = 'group_replication.so'
-- group_replication_group_name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
-- group_replication_start_on_boot = off
-- group_replication_local_address = "192.168.1.10:33061"
-- group_replication_group_seeds = "192.168.1.10:33061,192.168.1.11:33061,192.168.1.12:33061"
-- group_replication_bootstrap_group = off

-- Sur le premier nœud seulement, démarrer le groupe
SET GLOBAL group_replication_bootstrap_group = ON;
START GROUP_REPLICATION;
SET GLOBAL group_replication_bootstrap_group = OFF;

-- Sur les autres nœuds
START GROUP_REPLICATION;

-- Vérifier les membres
SELECT * FROM performance_schema.replication_group_members;
```

### 6.4 Galera Cluster (MariaDB)

```ini
[mariadb]
wsrep_on = ON
wsrep_provider = /usr/lib/galera/libgalera_smm.so
wsrep_cluster_name = "cluster_eva"
wsrep_cluster_address = "gcomm://192.168.1.10,192.168.1.11,192.168.1.12"
wsrep_node_name = "node1"
wsrep_node_address = "192.168.1.10"
wsrep_sst_method = mariabackup
wsrep_slave_threads = 8

# Démarrer le premier nœud
# galera_new_cluster

# Rejoindre les autres nœuds
# systemctl start mariadb
```

---

## 7. Tuning et Diagnostic

### 7.1 Requêtes lentes (slow query log)

```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow-queries.log
long_query_time = 1          # >= 1 seconde
log_queries_not_using_indexes = 1
```

### 7.2 pt-query-digest (Percona Toolkit)

```bash
# Analyse des requêtes lentes
pt-query-digest /var/log/mysql/slow-queries.log

# Analyse en temps réel
pt-query-digest --processlist h=localhost
```

### 7.3 Index usage statistics

```sql
-- Index non utilisés
SELECT
    OBJECT_SCHEMA AS db,
    OBJECT_NAME AS table_name,
    INDEX_NAME,
    COUNT_STAR AS utilisations,
    TIMER_WAIT/1000000000 AS ns_totaux
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE INDEX_NAME IS NOT NULL
  AND INDEX_NAME != 'PRIMARY'
  AND COUNT_STAR = 0
  AND OBJECT_SCHEMA NOT IN ('mysql', 'performance_schema', 'sys');
```

---

## Pièges Courants

1. **innodb_buffer_pool_size trop petit.** La performance chute dès que les données ne tiennent plus dans le buffer pool. Monitorer via `Innodb_buffer_pool_reads` (lectures disque) vs `Innodb_buffer_pool_read_requests` (demandes).

2. **Utiliser MyISAM en production.** MyISAM n'est pas transactionnel, a des verrous de table (pas de ligne), et corrompt facilement. Toujours utiliser InnoDB.

3. **Lack of ORDER BY avec GROUP BY.** MySQL 8.0+ n'ordonne plus automatiquement les GROUP BY — ajouter ORDER BY explicitement.

4. **Jointures sans index.** Les requêtes Nested Loop sans index sur la colonne de jointure sont catastrophiques. Vérifier avec EXPLAIN.

5. **Oublier le Thread Pool (MariaDB).** Sur MariaDB avec beaucoup de connexions, activer `thread_handling=pool-of-threads` — réduit la contention.

6. **Pas de versionning des schémas.** Utiliser `mysqlsh` avec `migrate` ou des outils comme `gh-ost` (GitHub) ou `pt-online-schema-change` pour les migrations sans downtime.

---

## Checklist

- [ ] `innodb_buffer_pool_size` configuré à 50-70% de la RAM
- [ ] `innodb_flush_log_at_trx_commit = 1` pour l'ACID complet
- [ ] `innodb_flush_method = O_DIRECT` (évite double cache)
- [ ] Slow query log activé avec `long_query_time = 1`
- [ ] Index composites optimisés (égalité → tri → plage)
- [ ] Partitionnement mis en place si > 50M lignes
- [ ] Réplication testée avec GTID (source/réplica)
- [ ] `mysql_secure_installation` exécuté
- [ ] Extensions de monitoring : Percona Monitoring and Management (PMM) ou MySQL Enterprise Monitor
- [ ] pt-query-digest régulier pour détecter les dérégations