---
name: replication-haute-disponibilite
description: "Guide complet de la réplication et haute disponibilité des bases de données — streaming, logique, synchrone/asynchrone, failover automatique, load balancing lecture, et architecture multi-site."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [réplication, haute-disponibilité, failover, streaming, logique, postgresql, mysql, mongodb, redis]
    homepage: https://www.postgresql.org/docs/current/high-availability.html
    related_skills: [postgresql, mysql, mongodb, redis, sharding-partitionnement, sauvegarde-restauration]
prerequisites:
  commands: [psql, mysql, mongosh, redis-cli]
---

# Compétence Réplication et Haute Disponibilité des Bases de Données

## Vue d'ensemble

La réplication crée des copies synchronisées des données pour assurer la tolérance aux pannes (HA), la répartition des lectures (scale-out read), et la récupération après sinistre (DR). Cette compétence couvre toutes les formes de réplication : streaming, logique, synchrone/asynchrone, multi-master, et les architectures DR multi-site.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Veut configurer un réplica de lecture PostgreSQL/MySQL/MongoDB
- A besoin de haute disponibilité (failover automatique)
- Doit synchroniser des données entre datacenters
- Veut répliquer vers un serveur de reporting sans impacter la production
- Configure un cluster de bases de données (Patroni, Galera, MongoDB Replica Set)
- Planifie une reprise après sinistre (DRP)

---

## 1. Concepts Fondamentaux

### 1.1 Modes de réplication

| Mode | PostgreSQL | MySQL | MongoDB | Redis |
|------|-----------|-------|---------|-------|
| **Asynchrone** | Streaming asynchrone | Réplication async | Réplication async | Redis Replication |
| **Semi-synchrone** | `synchronous_standby_names` | `rpl_semi_sync` | `w: majority` | `WAIT` |
| **Synchrone** | Quorum commit (PostgreSQL 16+) | Group Replication | Réplica sets | Redis Cluster (multi-master) |
| **Logique (multi-version)** | `pgoutput` + `pglogical` | `binlog` + décodeur | Change Streams | AOF |

### 1.2 Topologies

```
Asynchrone (simple) :
  Primary ──(async)──→ Réplica (lecture seule)

Semi-synchrone (2 data centers) :
  Primary ──(sync)──→ Réplica DC1
     └─(async)──→ Réplica DC2 (DR)

Multi-master (actif-actif) :
  Node A ←──(sync)──→ Node B
  Node B ←──(sync)──→ Node C

Cascading (répartition) :
  Primary ──→ Replica1 ──→ Replica2 ──→ Replica3
```

---

## 2. Réplication PostgreSQL

### 2.1 Streaming Replication (asynchrone, WAL)

```conf
# postgresql.conf (Primary)
wal_level = replica
max_wal_senders = 10              # nombre max de réplicas
wal_keep_size = 4096              # 4 GB de WAL gardés
hot_standby = on                  # lectures sur le réplica

# postgresql.conf (Standby)
primary_conninfo = 'host=192.168.1.10 port=5432 user=replicator password=***'
hot_standby = on                  # permet les lectures
hot_standby_feedback = on         # évite les query conflicts
```

```bash
# Initialiser le Standby
pg_basebackup -h 192.168.1.10 -D /var/lib/postgresql/16/main \
  -U replicator -P -v --wal-method=stream

# Créer le fichier standby.signal
touch /var/lib/postgresql/16/main/standby.signal
systemctl start postgresql
```

### 2.2 Réplication Synchrone

```conf
# postgresql.conf (Primary)
synchronous_commit = on
synchronous_standby_names = '1 (standby1)'  # 1 réplica synchrone

# Test de commit : attend que standby1 ait écrit le WAL
```

### 2.3 Cascading Replication

```conf
# standby1 (relais)
primary_conninfo = 'host=192.168.1.10 ...'
# Ajouter dans postgresql.conf :
max_wal_senders = 5
wal_level = replica
hot_standby = on

# standby2 (cascade)
# primary_conninfo pointe vers standby1
primary_conninfo = 'host=192.168.1.11 ...'
```

### 2.4 Réplication Logique

```sql
-- Publisher (Primary)
CREATE PUBLICATION pub_mesures FOR TABLE mesures, capteurs
WITH (publish = 'insert, update, delete, truncate');

-- Subscriber (Réplica logique)
CREATE SUBSCRIPTION sub_mesures
CONNECTION 'host=192.168.1.10 dbname=prod user=replicator password=***'
PUBLICATION pub_mesures
WITH (copy_data = true);

-- Ajouter une table sans redémarrer
ALTER PUBLICATION pub_mesures ADD TABLE logs_alarmes;

-- Réplication filtrée (PostgreSQL 15+)
CREATE PUBLICATION pub_critiques
FOR TABLE mesures WHERE (niveau = 'CRITIQUE');
```

### 2.5 Patroni (HA automatisée)

```yaml
# patroni.yml
scope: eva_cluster
namespace: /service/postgresql/
name: pg_eva_1

restapi:
  listen: 0.0.0.0:8008
  connect_address: 192.168.1.10:8008

etcd:
  host: 192.168.1.10:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    postgresql:
      use_pg_rewind: true
      parameters:
        wal_level: replica
        hot_standby: on
        max_connections: 200
        max_wal_senders: 10

postgresql:
  listen: 0.0.0.0:5432
  connect_address: 192.168.1.10:5432
  data_dir: /var/lib/postgresql/16/main
  bin_dir: /usr/lib/postgresql/16/bin
  authentication:
    replication:
      username: replicator
      password: ***
    superuser:
      username: postgres
      password: ***
```

```bash
# Démarrer Patroni sur chaque nœud
patroni /etc/patroni.yml

# Commandes utiles
patronictl -c /etc/patroni.yml list
patronictl -c /etc/patroni.yml failover
patronictl -c /etc/patroni.yml switchover
```

---

## 3. Réplication MySQL

### 3.1 Réplication Asynchrone (Source → Réplica)

```sql
-- Source
CREATE USER 'replicator'@'%' IDENTIFIED BY '***';
GRANT REPLICATION SLAVE ON *.* TO 'replicator'@'%';
FLUSH PRIVILEGES;
SHOW MASTER STATUS;

-- Réplica (MySQL 8.4+)
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='192.168.1.10',
    SOURCE_USER='replicator',
    SOURCE_PASSWORD='***',
    SOURCE_LOG_FILE='mysql-bin.000089',
    SOURCE_LOG_POS=145632;

START REPLICA;
SHOW REPLICA STATUS\G
```

### 3.2 GTID Replication

```ini
[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON
binlog_gtid_simple_recovery = ON

# Sur le réplica (avec GTID, pas besoin de position)
CHANGE REPLICATION SOURCE TO
    SOURCE_HOST='192.168.1.10',
    SOURCE_USER='replicator',
    SOURCE_PASSWORD='***',
    SOURCE_AUTO_POSITION = 1;
```

### 3.3 MySQL InnoDB Cluster

```sql
-- Configurer chaque instance
-- my.cnf
-- server_id = 1
-- gtid_mode = ON
-- enforce_gtid_consistency = ON
-- binlog_checksum = NONE
-- plugin_load_add = 'group_replication.so'
-- group_replication_group_name = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
-- group_replication_start_on_boot = off
-- group_replication_local_address = "192.168.1.10:33061"
-- group_replication_group_seeds = "192.168.1.10:33061,192.168.1.11:33061"
-- group_replication_bootstrap_group = off
-- group_replication_single_primary_mode = ON

-- Premier nœud
SET GLOBAL group_replication_bootstrap_group = ON;
START GROUP_REPLICATION;
SET GLOBAL group_replication_bootstrap_group = OFF;

-- Nœuds suivants
START GROUP_REPLICATION;

-- Vérifier
SELECT * FROM performance_schema.replication_group_members;
```

---

## 4. Réplication MongoDB

### 4.1 Réplica Set

```javascript
// Config
rs.initiate({
    _id: "rs_eva",
    version: 1,
    members: [
        { _id: 0, host: "192.168.1.10:27017", priority: 2 },
        { _id: 1, host: "192.168.1.11:27017", priority: 1 },
        { _id: 2, host: "192.168.1.12:27017", priority: 0, votes: 0, hidden: true }
    ],
    settings: {
        electionTimeoutMillis: 10000,
        heartbeatIntervalMillis: 2000
    }
});

// Écriture : w: majority (par défaut depuis 5.0)
db.mesures.insertOne(doc, { writeConcern: { w: "majority", j: true } });

// Lecture : préférence secondaire
db.getMongo().setReadPref("secondaryPreferred");
```

### 4.2 Changement de Primary (Élection)

```javascript
// Forcer une élection
rs.stepDown(60);  // 60 secondes avant de pouvoir être réélu

// Suivre les événements
rs.printSecondaryReplicationInfo();
rs.printReplicationInfo();
```

---

## 5. Réplication Redis

### 5.1 Master-Replica

```conf
# replica.conf
replicaof 192.168.1.10 6379
masterauth mon_password
replica-read-only yes
replica-serve-stale-data yes
replica-lazy-flush no
```

### 5.2 Redis Sentinel (HA automatisée)

```conf
# /etc/redis/sentinel.conf
sentinel monitor eva_master 192.168.1.10 6379 2
sentinel down-after-milliseconds eva_master 5000
sentinel failover-timeout eva_master 60000
sentinel parallel-syncs eva_master 1
sentinel auth-pass eva_master mon_password
```

```bash
# Démarrer les sentinelles (3 minimum)
redis-sentinel /etc/redis/sentinel.conf --port 26379

# Vérifier
redis-cli -p 26379 SENTINEL masters
redis-cli -p 26379 SENTINEL get-master-addr-by-name eva_master
```

---

## 6. Architecture Multi-Datacenter

### 6.1 PostgreSQL — 3 DCs

```
DC1 (Primary) ──(sync)──→ DC2 (Standby synchrone)
   └─(async)──→ DC3 (Standby asynchrone, DR)

pg_rewind pour récupérer un ancien primary après split-brain
```

### 6.2 MySQL — Group Replication multi-DC

```ini
[mysqld]
group_replication_group_seeds = "10.1.0.1:33061,10.2.0.1:33061,10.3.0.1:33061"
group_replication_consistency = EVENTUAL
group_replication_member_expel_timeout = 5
```

### 6.3 MongoDB — Réplica Set géo-distribué

```javascript
rs.initiate({
    _id: "rs_global",
    members: [
        { _id: 0, host: "dc1-primary:27017", tags: { region: "eu-west" }, priority: 2 },
        { _id: 1, host: "dc1-secondary:27017", tags: { region: "eu-west" }, priority: 1 },
        { _id: 2, host: "dc2-secondary:27017", tags: { region: "us-east" }, priority: 0 },
        { _id: 3, host: "dc3-secondary:27017", tags: { region: "ap-southeast" }, priority: 0 }
    ],
    settings: {
        // Éviter les primaires hors Europe
        secondaryDelaySecs: 5  // dc2 et dc3 ont 5s de retard
    }
});

// Lecture depuis le DC local
db.getMongo().setReadPref("secondary", [{ region: "eu-west" }]);
```

---

## 7. Reprise Après Sinistre (DRP)

### 7.1 RPO et RTO

| Niveau | RPO | RTO | Type |
|--------|-----|-----|------|
| Bronze | 1 heure | 4 heures | Backup journalier + WAL |
| Argent | 5 minutes | 1 heure | Réplication asynchrone |
| Or | < 1 seconde | 5 minutes | Réplication synchrone multi-DC |
| Platine | Zéro | Zéro | Multi-master actif-actif |

### 7.2 Switchover/Failover planifié

```bash
# PostgreSQL (manuel) — élève le standby
pg_ctl promote -D /var/lib/postgresql/16/main

# PostgreSQL (Patroni)
patronictl -c /etc/patroni.yml switchover --master pg_eva_1 --candidate pg_eva_2

# MySQL (réplica → master)
STOP REPLICA;
RESET SLAVE ALL;

# MongoDB
rs.stepDown(60);
```

### 7.3 Split-brain prevention

```bash
# Utiliser un fencing mechanism (STONITH) en cluster
# PostgreSQL : standby peut se promouvoir seulement si etcd/consensus le confirme
# MySQL : Group Replication avec majorité
# MongoDB : réplica set avec nombre impair de membres
```

---

## Pièges Courants

1. **Réplication synchrone trop lente.** À chaque commit, le PRIMARY attend le standby. Si le standby est loin (> 5ms RTT), les écritures ralentissent. Utiliser semi-sync comme compromis.

2. **Pas de monitoring du lag.** Un réplica qui prend du retard est inutile. Monitorer : `pg_stat_replication.write_lag`, `Seconds_Behind_Source`, `rs.status().members[n].optimeDate`.

3. **Split-brain après failover.** Deux serveurs qui se croient PRIMARY. Solution : quorum (etcd/Patroni, Sentinel, Galera), STONITH, ou un nombre impair de nœuds.

4. **Blind switchover sans test.** Tester le failover mensuellement : les bases non testées ne fonctionnent pas le jour J.

5. **Réplication asynchrone sans file d'attente.** Le WAL peut saturer si le réplica est trop lent. Configurer `max_wal_size` et `wal_keep_size` généreusement.

6. **Faire confiance à l'auto-failover sans test.** Tester : `pkill -9 postgres` sur le primary, et vérifier que le standby prend le relais en < 30s.

---

## Checklist

- [ ] Au moins un réplica synchrone ou semi-synchrone configuré
- [ ] Patroni/Sentinel/Galera/Group Replication installé et testé
- [ ] Failover testé et documenté (temps de bascule < RTO cible)
- [ ] Monitoring du lag de réplication en place
- [ ] Nombre impair de nœuds MongoDB (évite split-brain)
- [ ] GTID activé en MySQL pour auto-positionnement
- [ ] `recovery.conf` / `standby.signal` correct (PostgreSQL)
- [ ] DRP documenté et testé au moins une fois par trimestre
- [ ] Retour arrière (promotion inverse) testé
- [ ] Alertes configurées : lag > 30s, réplica déconnecté, split-brain probable