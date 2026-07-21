---
name: sharding-partitionnement
description: "Guide complet du partitionnement et sharding — partition range, list, hash (PostgreSQL, MySQL, MongoDB), sharding horizontal (MongoDB, MySQL Cluster, Vitess), et stratégies de distribution des données."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [sharding, partitionnement, distribution, base-de-donnees, scale-out, horizontale, range, hash]
    homepage: https://www.postgresql.org/docs/current/ddl-partitioning.html
    related_skills: [postgresql, mysql, mongodb, replication-haute-disponibilite, indexation-bases-donnees, optimisation-performance]
prerequisites:
  commands: [psql, mysql, mongosh]
---

# Compétence Sharding et Partitionnement — Distribution des Données à Grande Échelle

## Vue d'ensemble

Le partitionnement (partitioning) divise une table logique en segments physiques plus petits. Le sharding distribue ces segments sur plusieurs serveurs (scale-out). Ensemble, ils permettent de dépasser les limites d'une seule machine.

Cette compétence distingue clairement :
- **Partitionnement vertical** : diviser une table par colonnes (rare)
- **Partitionnement horizontal** : diviser par lignes (range, list, hash)
- **Sharding** : partitionnement horizontal multi-serveurs

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- A des tables dépassant 100M lignes ou 100 Go
- Veut archiver des données anciennes sans supprimer
- Doit distribuer une charge sur plusieurs serveurs
- A besoin de paralléliser les requêtes sur plusieurs nœuds
- Veut configurer le sharding MongoDB, Vitess, ou MySQL Cluster
- Demande de migrer d'une instance monolithique vers une architecture distribuée

---

## 1. Partitionnement PostgreSQL

### 1.1 Partition Range (par périodes)

```sql
-- Table partitionnée par mois
CREATE TABLE mesures (
    id BIGSERIAL,
    ts TIMESTAMPTZ NOT NULL,
    machine_id INT NOT NULL,
    temperature NUMERIC,
    pression NUMERIC,
    PRIMARY KEY (id, ts)  -- la clé de partition DOIT faire partie de la PK
) PARTITION BY RANGE (ts);

-- Création des partitions mensuelles
CREATE TABLE mesures_2025_01 PARTITION OF mesures
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01')
    TABLESPACE fast_storage;

CREATE TABLE mesures_2025_02 PARTITION OF mesures
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01')
    TABLESPACE fast_storage;

-- Partition par défaut (attrape les hors-limites)
CREATE TABLE mesures_defaut PARTITION OF mesures DEFAULT;
```

### 1.2 Partition List (catégories discrètes)

```sql
CREATE TABLE logs_evenements (
    id BIGSERIAL,
    niveau TEXT NOT NULL,
    message TEXT,
    ts TIMESTAMPTZ
) PARTITION BY LIST (niveau);

CREATE TABLE logs_info PARTITION OF logs_evenements
    FOR VALUES IN ('INFO', 'DEBUG');
CREATE TABLE logs_warn PARTITION OF logs_evenements
    FOR VALUES IN ('WARN', 'ERROR');
CREATE TABLE logs_critical PARTITION OF logs_evenements
    FOR VALUES IN ('CRITICAL', 'FATAL');
```

### 1.3 Partition Hash (distribution uniforme)

```sql
CREATE TABLE sessions_utilisateurs (
    session_id BIGINT NOT NULL,
    user_id INT NOT NULL,
    payload JSONB
) PARTITION BY HASH (session_id);

CREATE TABLE sessions_0 PARTITION OF sessions_utilisateurs
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions_utilisateurs
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_2 PARTITION OF sessions_utilisateurs
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_3 PARTITION OF sessions_utilisateurs
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### 1.4 Détachement et archivage

```sql
-- Détacher une partition (quasi-instantané, pas de copie)
ALTER TABLE mesures DETACH PARTITION mesures_2024_01;

-- Attacher une partition (validation des contraintes)
ALTER TABLE mesures ATTACH PARTITION mesures_2025_03
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Valider sans bloquer (PostgreSQL 16+)
ALTER TABLE mesures ATTACH PARTITION mesures_2025_03
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01')
    WITHOUT VALIDATION;
```

---

## 2. Partitionnement MySQL (InnoDB)

### 2.1 Range avec sous-partitions

```sql
CREATE TABLE transactions (
    id BIGINT NOT NULL,
    date_transaction DATE NOT NULL,
    montant DECIMAL(10,2),
    client_id INT,
    PRIMARY KEY (id, date_transaction)
) PARTITION BY RANGE (YEAR(date_transaction))
  SUBPARTITION BY HASH (MONTH(date_transaction))
  SUBPARTITIONS 4 (
    PARTITION p2024 VALUES LESS THAN (2025),
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p2026 VALUES LESS THAN (2027),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### 2.2 Partition Exchange pour archivage

```sql
-- Échange instantané entre partition et table
CREATE TABLE transactions_2024_archive LIKE transactions;
ALTER TABLE transactions EXCHANGE PARTITION p2024 WITH TABLE transactions_2024_archive;

-- La table transactions_2024_archive contient maintenant les données
-- On peut la déplacer, la compresser, ou la stocker ailleurs
```

---

## 3. Sharding MongoDB

### 3.1 Architecture

```
Client → mongos (router) → config servers (CSRS) → shard1, shard2, ..., shardN
```

### 3.2 Activation du sharding

```javascript
// Depuis le mongos
sh.enableSharding("eva_industrial");

// Choix de la clé de shard
// Règle : cardinalité élevée, distribution uniforme, pattern d'accès équilibré

// 1. Hashed (distribution parfaite, pas de range queries efficaces)
sh.shardCollection("eva_industrial.mesures", { _id: "hashed" });

// 2. Range-based (range queries efficaces, risque de hot spot)
sh.shardCollection("eva_industrial.mesures", { machine_id: 1, ts: -1 });

// 3. Zone-based (données localisées géographiquement)
sh.addShardTag("shard_eu", "EUROPE");
sh.addShardTag("shard_us", "AMERICA");

sh.updateZoneKeyRange(
    "eva_industrial.mesures",
    { region: "EU" }, { region: "EU\uFFFF" },
    "EUROPE"
);
```

### 3.3 Chunk sizing et balancing

```javascript
// Taille des chunks (défaut: 128MB)
db.adminCommand({ configureCollectionBalancing: "eva_industrial.mesures", chunkSize: 64 });

// Désactiver le balancer pour maintenance
sh.stopBalancer();
// Activer
sh.startBalancer();

// Forcer un split
sh.splitAt("eva_industrial.mesures", { machine_id: 1000 });

// Vérifier la distribution
sh.status();
```

---

## 4. Sharding avec Vitess

Vitess (YouTube/PlanetScale) est la solution de sharding la plus mature pour MySQL. Il transforme MySQL en un cluster distribué.

```yaml
# Topology (vschema)
{
  "sharded": true,
  "vindexes": {
    "hash": { "type": "hash" },
    "binary_md5": { "type": "binary_md5" },
    "lookup_capteur": { "type": "lookup_hash", "params": { "from": "capteur_id", "table": "capteur_lookup" } }
  },
  "tables": {
    "mesures": {
      "type": "table",
      "column_vindexes": [
        { "column": "capteur_id", "name": "hash" }  # clé de shard
      ],
      "auto_increment": { "column": "id", "sequence": "mesures_seq" }
    }
  }
}
```

```bash
# Deployer le shard
vtctl ApplyShard -cells cell1 -master-tablet_type replica eva/0
vtctl InitShardMaster -force eva/0 cell1-0000000100

# Resharding (sans downtime)
vtctl Reshard eva.reshard_workflow eva/0 eva/40-80,80-c0,c0-100
```

---

## 5. Sharding avec Citus (PostgreSQL)

Citus transforme PostgreSQL en base de données distribuée compatible SQL.

```sql
-- Activer Citus
CREATE EXTENSION citus;

-- Ajouter des nœuds workers
SELECT master_add_node('worker1.example.com', 5432);
SELECT master_add_node('worker2.example.com', 5432);
SELECT master_add_node('worker3.example.com', 5432);

-- Créer une table distribuée
CREATE TABLE mesures (
    capteur_id INT,
    ts TIMESTAMPTZ,
    temperature NUMERIC
);

-- Choisir la colonne de distribution
SELECT create_distributed_table('mesures', 'capteur_id');

-- Colocate deux tables (évite les requêtes cross-shard)
SELECT create_distributed_table('capteurs', 'id');
SELECT create_reference_table('types_capteurs');  -- copiée partout

-- Requêtes distributées (SQL transparent)
SELECT capteur_id, COUNT(*)
FROM mesures
WHERE ts > NOW() - INTERVAL '1 hour'
GROUP BY capteur_id
ORDER BY COUNT(*) DESC;
```

---

## 6. Stratégies de Clé de Shard

| Stratégie | Avantages | Inconvénients | Idéal pour |
|-----------|-----------|---------------|------------|
| **Hashed** | Distribution uniforme garantie | Range scans impossibles, pas de localité | Lookup par ID, sessions |
| **Range** | Range scans efficaces, aggregation locale | Hot spots sur les clés récentes | Séries temporelles |
| **Zone-based** | Localité des données (régions) | Déséquilibre si une zone domine | Applications multirégions |
| **Lookup table** | Distribution selon attribut secondaire | Requête supplémentaire, complexité | Data où la PK n'est pas la bonne clé |
| **Directory-based** | Contrôle total de la distribution | SPOF sur le service de routage | Applications legacy |

---

## 7. Anti-Patterns du Sharding

### 7.1 Hot Spot (clé mal choisie)

```javascript
// MAUVAIS : partition par date avec écritures concentrées sur la partition courante
sh.shardCollection("logs.journal", { date: 1 });

// MEILLEUR : hashed sur un champ composite
sh.shardCollection("logs.journal", { serveur_id: 1, date: 1 });
```

### 7.2 Cross-shard Queries

```sql
-- MAUVAIS (MySQL avec Vitess / Citus)
-- JOIN entre deux tables sur des shards différents = très lent

-- BON : colocation des tables fréquemment jointes
SELECT create_distributed_table('commandes', 'client_id');
SELECT create_distributed_table('lignes_commande', 'client_id');  -- colocated
```

### 7.3 Resharding coûteux

Le resharding (changer le nombre de shards) est LOURD. Anticiper :
- MongoDB : balancer automatique (mais lent : ~50MB/s par nœud)
- Vitess : resharding vertical (split sans downtime)
- Citus : `rebalance_table_shards()` avec mouvement des données

---

## Pièges Courants

1. **Partitionnement sans pruning.** Une requête qui scannne toutes les partitions est plus lente que sans partitionnement. Vérifier avec `EXPLAIN` que seules les partitions pertinentes sont scannées.

2. **Trop de partitions.** PostgreSQL gère bien jusqu'à ~1000 partitions, au-delà le planner ralentit. Planifier maximum 12-24 par an pour un partitionnement mensuel.

3. **Index globaux vs locaux.** Dans PostgreSQL, les index sont locaux à chaque partition. MySQL les index globaux n'existent pas. MongoDB a un index global sur la collection.

4. **Clé de partition qui change.** On ne peut pas changer la clé de partition d'une table existante. Créer une nouvelle table partitionnée et migrer les données avec `pg_transport` ou `INSERT...SELECT`.

5. **Distribution non uniforme.** Une clé de shard mal choisie crée des shards surchargés. Monitorer la taille des chunks/chunks régulièrement.

6. **Transactions cross-shard.** MongoDB et Citus supportent les transactions cross-shard, mais elles sont beaucoup plus lentes. Minimiser les transactions qui traversent les shards.

---

## Checklist

- [ ] Type de partitionnement adapté : range (temporel), list (catégoriel), hash (uniforme)
- [ ] Clé de partition/sharding a une cardinalité élevée
- [ ] Partition pruning confirmé via EXPLAIN
- [ ] Pas plus de 1000 partitions par table (PostgreSQL)
- [ ] Partitions anciennes détachées/archivées régulièrement
- [ ] Index locaux créés sur chaque partition
- [ ] Balancer actif (MongoDB) ou resharding planifié
- [ ] Tables colocated pour les JOINs fréquents (Citus/Vitess)
- [ ] Monitoring du déséquilibre : `pg_stat_user_tables`, `sh.status()`
- [ ] Stratégie de resharding documentée avant que le besoin ne devienne critique