---
name: sauvegarde-restauration
description: "Guide complet de sauvegarde et restauration des bases de données — pg_dump, mysqldump, mongodump, WAL archiving, PITR, backup stratégies, test de restauration, et automation cron."
version: 1.0.0
author: EVA & communauté EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [sauvegarde, restauration, backup, pitr, pg_dump, mysqldump, mongodump, wal, drp]
    homepage: https://www.postgresql.org/docs/current/backup.html
    related_skills: [postgresql, mysql, mongodb, replication-haute-disponibilite, optimisation-performance]
prerequisites:
  commands: [pg_dump, pg_restore, mysqldump, mongodump, mongorestore, sqlite3, borg, restic, duplicity]
---

# Compétence Sauvegarde et Restauration des Bases de Données

## Vue d'ensemble

Sans sauvegarde testée, vos données n'existent pas. Cette compétence couvre toutes les stratégies de backup (logique, physique, WAL archiving, snapshots), la restauration point-in-time (PITR), l'automatisation, la compression, le chiffrement, et les tests de restauration. L'objectif : pouvoir restaurer n'importe quelle base à n'importe quel point dans le temps avec une procédure documentée.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :
- Demande de configurer une stratégie de backup pour production
- Veut automatiser les sauvegardes avec cron ou borg
- Doit restaurer une base après un incident
- A besoin de PITR (Point-In-Time Recovery)
- Veut sécuriser les backups (chiffrement, stockage distant)
- Doit auditer une stratégie existante

---

## 1. Stratégies de Backup

### 1.1 Choix du type

| Stratégie | Taille | Vitesse Restauration | RPO | Idéal pour |
|-----------|--------|---------------------|-----|------------|
| **Dump SQL logique** | Grosse | Lente | Au moment du dump | Petites bases (< 50 Go) |
| **Snapshot physique** | Petite | Rapide | Au moment du snapshot | Grandes bases (> 100 Go) |
| **WAL archiving + base** | Minime | Instantané | 1 minute | Production critique |
| **Snapshots ZFS/btrfs** | Nulle (COW) | Instantané | 5 minutes | VM / conteneurs |
| **Réplica physique** | Même taille | Secondes | Réplication lag | HA avec DR |

### 1.2 Règle 3-2-1

- **3** copies des données
- **2** supports différents (ex: local + S3)
- **1** copie hors-site

---

## 2. PostgreSQL — Sauvegarde et PITR

### 2.1 pg_dump (logique)

```bash
# Base complète au format custom (compressé, parallélisable)
pg_dump -h localhost -p 5432 -U postgres \
  -Fc --compress=9 -j 4 \
  -f /backup/pg/eva_prod_$(date +%Y%m%d_%H%M).dump \
  eva_prod

# Format directory (plus rapide pour les grosses bases)
pg_dump -h localhost -U postgres \
  -Fd -j 8 \
  -f /backup/pg/eva_prod_dir \
  eva_prod

# Dump en SQL pur (portable)
pg_dump -h localhost -U postgres \
  --no-owner --no-acl \
  eva_prod > /backup/pg/eva_prod_$(date +%Y%m%d).sql

# Dump avec compression gzip
pg_dump -h localhost -U postgres eva_prod | gzip -9 > /backup/pg/eva_prod_$(date +%Y%m%d).sql.gz

# Dump d'une seule table
pg_dump -h localhost -U postgres \
  -t mesures -Fc \
  -f /backup/pg/mesures.dump eva_prod

# Dump avec data only (sans schéma)
pg_dump -h localhost -U postgres \
  --data-only --exclude-table=logs_audit \
  -Fc -f /backup/pg/data_only.dump eva_prod
```

### 2.2 pg_restore

```bash
# Restauration complète
pg_restore -h localhost -U postgres \
  -d eva_prod_restored --clean --if-exists \
  -j 4 /backup/pg/eva_prod_20250601.dump

# Restauration d'une seule table
pg_restore -h localhost -U postgres \
  -d eva_prod -t mesures \
  /backup/pg/eva_prod_20250601.dump

# Restauration du schéma seulement
pg_restore -h localhost -U postgres \
  -d eva_prod --schema-only \
  /backup/pg/eva_prod_20250601.dump

# Liste du contenu d'un dump
pg_restore -l /backup/pg/eva_prod_20250601.dump
```

### 2.3 WAL Archiving + PITR (La Rolls-Royce)

```conf
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'rsync -a %p /backup/pg/wal/%f && borg create /backup/borg::wal-$(date +%Y%m%d) /backup/pg/wal/'
archive_timeout = 60  # forcer un WAL toutes les 60 secondes (RPO ≈ 1 min)
```

```bash
# Script de base backup
#!/bin/bash
pg_basebackup -h localhost -D /backup/pg/basebackup/$(date +%Y%m%d_%H%M) \
  -U postgres -P -v --wal-method=stream -X f
```

```bash
# Restauration PITR à un timestamp précis
# 1. Restaurer la base backup
rsync -a /backup/pg/basebackup/20250601_020000/ /var/lib/postgresql/16/main/

# 2. Créer restore.signal (PostgreSQL 12+)
touch /var/lib/postgresql/16/main/restore.signal

# 3. Configurer recovery.conf (façon PostgreSQL 15+)
echo "restore_command = 'cp /backup/pg/wal/%f %p'" >> /var/lib/postgresql/16/main/postgresql.auto.conf
echo "recovery_target_time = '2025-06-01 14:30:00+02'" >> /var/lib/postgresql/16/main/postgresql.auto.conf

# 4. Démarrer PostgreSQL
systemctl start postgresql
# PostgreSQL applique tous les WAL jusqu'au timestamp spécifié,
# puis s'arrête en mode recovery.
```

### 2.4 pgBackRest (outil professionnel)

```bash
# Installation
sudo apt install pgbackrest

# Configuration /etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/backup/pgbackrest
repo1-retention-full=7
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=***

[stanza]
eva_prod
pg1-path=/var/lib/postgresql/16/main

# Backup full
pgbackrest --stanza=eva_prod --type=full backup

# Backup incrémental
pgbackrest --stanza=eva_prod --type=incr backup

# Restauration
pgbackrest --stanza=eva_prod --type=time --target="2025-06-01 14:30:00+02" restore

# Vérification
pgbackrest --stanza=eva_prod check
```

---

## 3. MySQL — Sauvegarde

### 3.1 mysqldump

```bash
# Backup logique complet
mysqldump -h localhost -u root -p \
  --all-databases --single-transaction --routines --triggers --events \
  --flush-logs --master-data=2 \
  | gzip -9 > /backup/mysql/all_dbs_$(date +%Y%m%d).sql.gz

# Backup d'une base unique
mysqldump -h localhost -u root -p \
  --databases eva_prod --single-transaction --routines \
  | gzip -9 > /backup/mysql/eva_prod_$(date +%Y%m%d).sql.gz

# Backup avec compression et chunking
mysqldump -h localhost -u root -p \
  eva_prod mesures --where="ts > '2025-01-01'" \
  | gzip -9 | split -b 1G - /backup/mysql/mesures_2025.sql.gz.
```

### 3.2 mysqlpump (MySQL 8.0+, parallélisé)

```bash
# Parallélisé (4 threads) — jusqu'à 10x plus rapide
mysqlpump -h localhost -u root -p \
  --parallel-schemas=4:eva_prod \
  --exclude-databases=mysql,sys \
  --add-drop-database \
  | gzip -9 > /backup/mysql/pump_eva_prod_$(date +%Y%m%d).sql.gz
```

### 3.3 MySQL Shell (utilitaire officiel)

```bash
# Backup avec compression et parallélisme
mysqlsh --uri root@localhost:3306 -- util dumpInstance /backup/mysql/shell_backup \
  --threads=8 --ocimds=false --compatibility=strip_definers

mysqlsh --uri root@localhost:3306 -- util dumpSchemes --excludeSchemas=mysql,sys \
  /backup/mysql/shell_schemas --threads=8

# Restauration
mysqlsh --uri root@localhost:3306 -- util loadDump /backup/mysql/shell_backup \
  --threads=8 --progressFile=/tmp/progress.json
```

### 3.4 Percona XtraBackup (physique, chaud)

```bash
# Backup complet (sans verrouillage)
xtrabackup --backup --target-dir=/backup/mysql/xtrabackup/$(date +%Y%m%d) \
  --user=root --password=***

# Préparer pour restauration
xtrabackup --prepare --target-dir=/backup/mysql/xtrabackup/20250601

# Restaurer
xtrabackup --copy-back --target-dir=/backup/mysql/xtrabackup/20250601 \
  --datadir=/var/lib/mysql/
chown -R mysql:mysql /var/lib/mysql/
```

---

## 4. MongoDB — Sauvegarde

```bash
# mongodump standard
mongodump --uri="mongodb://localhost:27017/eva_industrial" \
  --out=/backup/mongo/$(date +%Y%m%d)

# Avec compression et archive
mongodump --uri="mongodb://localhost:27017/eva_industrial" \
  --gzip --archive=/backup/mongo/eva_industrial_$(date +%Y%m%d).gz

# Avec oplog (PITR pour réplica set)
mongodump --uri="mongodb://192.168.1.10:27017/eva_industrial" \
  --oplog --out=/backup/mongo/oplog_$(date +%Y%m%d)

# Copie physique du réplica set (arrêt du secondaire)
# 1. Arrêter le secondaire
# 2. Copier tout le répertoire dbpath
# 3. Redémarrer
```

```bash
# Restauration
mongorestore --uri="mongodb://localhost:27018/eva_industrial" \
  --drop /backup/mongo/20250601/eva_industrial

mongorestore --uri="mongodb://localhost:27018/eva_industrial" \
  --gzip --archive=/backup/mongo/eva_industrial_20250601.gz \
  --nsInclude="eva_industrial.mesures"
```

---

## 5. Redis — Sauvegarde

```bash
# Sauvegarde RDB (trigger manuel)
redis-cli SAVE
# Copier le fichier dump.rdb
cp /var/lib/redis/dump.rdb /backup/redis/dump_$(date +%Y%m%d).rdb

# Backup avec BGSAVE (asynchrone, recommandé)
redis-cli BGSAVE
# Attendre la fin : LASTSAVE
while [ $(redis-cli LASTSAVE) -lt $(date +%s) ]; do sleep 1; done

# Backup AOF (si appendonly yes)
cp /var/lib/redis/appendonly.aof /backup/redis/aof_$(date +%Y%m%d).aof
```

---

## 6. SQLite — Sauvegarde

```bash
# Backup en ligne (sûr avec WAL)
sqlite3 eva_data.db ".backup /backup/sqlite/eva_data_$(date +%Y%m%d).db"

# Méthode VACUUM INTO (SQLite 3.27+)
sqlite3 eva_data.db "VACUUM INTO '/backup/sqlite/eva_data_clean.db'"

# Backup automatisé
#!/bin/bash
DB="/data/eva_data.db"
BKP="/backup/sqlite/eva_data_$(date +%Y%m%d_%H%M%S).db"
sqlite3 "$DB" ".backup $BKP"
echo "Backup: $BKP ($(du -h $BKP | cut -f1))"
```

---

## 7. Automation et Rotation

### 7.1 Script de backup complet PostgreSQL

```bash
#!/bin/bash
# /usr/local/bin/backup_pg.sh
set -euo pipefail

BACKUP_DIR="/backup/pg"
BASE_NAME="eva_prod"
DATE=$(date +%Y%m%d_%H%M)
RETENTION_DAYS=30
S3_BUCKET="s3://eva-backups/pg/"

# Backup logique
pg_dump -h localhost -U postgres \
  -Fc --compress=9 -j 4 \
  -f "${BACKUP_DIR}/${BASE_NAME}_${DATE}.dump" \
  "${BASE_NAME}"

# Chiffrement (GPG)
gpg --encrypt --recipient admin@eva.io \
  "${BACKUP_DIR}/${BASE_NAME}_${DATE}.dump"

# Transfert S3
aws s3 cp "${BACKUP_DIR}/${BASE_NAME}_${DATE}.dump.gpg" "${S3_BUCKET}"

# Nettoyage local (30 jours)
find "${BACKUP_DIR}" -name "${BASE_NAME}_*.dump*" -mtime +${RETENTION_DAYS} -delete

# Test de vérification
pg_restore -l "${BACKUP_DIR}/${BASE_NAME}_${DATE}.dump" > /dev/null \
  && echo "Backup vérifié OK" \
  || echo "ERREUR : backup corrompu" | mail -s "Backup ERROR" admin@eva.io

# Rotation WAL (supprimer les WAL déjà archivés et plus vieux que 7 jours)
find /backup/pg/wal/ -name "*.gz" -mtime +7 -delete
```

### 7.2 Cron

```cron
# Tous les jours à 2h du matin (full)
0 2 * * * /usr/local/bin/backup_pg.sh > /var/log/backup_pg.log 2>&1

# Toutes les 5 minutes (WAL archiving)
*/5 * * * * /usr/local/bin/archive_wal.sh
```

---

## 8. Test de Restauration (Le plus important)

### 8.1 Procédure de test mensuelle

```bash
#!/bin/bash
# /usr/local/bin/test_restore.sh

TEST_DIR="/tmp/test_restore"
LATEST_BACKUP=$(ls -t /backup/pg/eva_prod_*.dump | head -1)

echo "=== Test de restauration - $(date) ==="
echo "Backup testé : $LATEST_BACKUP"

# Initialiser un cluster vide
initdb -D ${TEST_DIR}/data

# Restaurer le dump
pg_restore -d postgres --clean "$LATEST_BACKUP" -j 4 || {
    echo "ÉCHEC : restauration impossible"
    exit 1
}

# Vérifier l'intégrité
pg_dump -d postgres --schema-only | grep -q "CREATE TABLE" || {
    echo "ÉCHEC : aucune table trouvée"
    exit 1
}

# Vérifier le nombre de lignes
ROW_COUNT=$(psql -d postgres -tAc "SELECT SUM(n_live_tup) FROM pg_stat_user_tables;")
echo "OK : $ROW_COUNT lignes restaurées"

# Nettoyer
rm -rf ${TEST_DIR}
echo "=== Test terminé : SUCCÈS ==="
```

---

## Pièges Courants

1. **Jamais testé avant le jour J.** Un backup jamais restauré n'est pas un backup. Tester au moins une fois par mois.

2. **Chiffrement sans test de déchiffrement.** Après un crash, la clé GPG perdue = données perdues. Stocker la clé de déchiffrement séparément du backup.

3. **Rotation trop agressive.** Garder au minimum : 7 full backups quotidiens, 4 hebdomadaires, 12 mensuels. Les corruptions peuvent mettre des semaines à être détectées.

4. **Pas de backup du WAL.** Sans WAL, la restauration PITR est impossible. Vérifier que `archive_command` fonctionne avec `pg_switch_wal()`.

5. **Backup sur le même disque que la base.** Un crash disque tue les deux. Toujours stocker les backups sur un filesystem ou un hôte différent.

6. **Oublier les backups logiques pour les migrations.** Les dumps physiques ne sont pas portables entre versions majeures de PostgreSQL. Toujours avoir un dump logique pour les migrations.

---

## Checklist

- [ ] Règle 3-2-1 respectée (3 copies, 2 supports, 1 hors-site)
- [ ] WAL archiving configuré avec `archive_mode = on` (PostgreSQL)
- [ ] Backup automatique journalier avec rotation (30 jours min)
- [ ] Backup testé mensuellement (restauration complète vérifiée)
- [ ] Chiffrement des backups (GPG, AES-256)
- [ ] Script de backup avec notifications d'échec (email, webhook)
- [ ] backup logique (dump) + backup physique (WAL/basebackup)
- [ ] Monitoring de l'espace disque des backups
- [ ] Procédure de restauration documentée (temps estimé : RTO)
- [ ] Backup de la configuration (postgresql.conf, pg_hba.conf, my.cnf) en plus des données