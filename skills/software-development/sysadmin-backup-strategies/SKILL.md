---
name: sysadmin-backup-strategies
description: "Stratégies de sauvegarde Linux : rsync, Borg Backup, restic, duplicity, dump/restore, snapshots LVM, rotation, archivage, stratégie 3-2-1 et scripts d'automatisation."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [backup, rsync, borg, restic, duplicity, snapshots, restore, disaster-recovery, 3-2-1, automation]
    related_skills: [sysadmin-lvm, sysadmin-systemd, os-linux-admin]
---

# Stratégies de Sauvegarde Linux

## Vue d'ensemble

Une stratégie de sauvegarde robuste garantit la récupération des données après sinistre, erreur humaine ou corruption. Ce skill couvre les outils et méthodes standard pour la sauvegarde de serveurs Linux, de la simple copie rsync à la déduplication avancée avec Borg/Restic.

## Règle d'Or : 3-2-1

- **3** copies des données
- **2** supports différents (disque local, NAS, cloud)
- **1** copie hors-site (off-site)

## Quand l'utiliser

- Mettre en place une sauvegarde automatisée de fichiers/dossiers
- Sauvegarder des bases de données (PostgreSQL, MySQL, SQLite)
- Créer des archives de configurations système avant une mise à jour
- Planifier une rotation des sauvegardes (quotidienne, hebdomadaire, mensuelle)
- Tester une procédure de restauration complète

## Outils par Cas d'Usage

| Outil | Idéal pour | Avantage principal |
|-------|-----------|-------------------|
| `rsync` | Copies incrémentales, synchronisation | Simple, présent partout, efficace réseau |
| `BorgBackup` | Archives dédupliquées, compression | Déduplication, chiffrement intégré |
| `restic` | Backup cloud, S3, multi-plateforme | Support S3 natif, vérification intégrité |
| `duplicity` | Backup chiffré vers cloud | GPG natif, nombreux backends |
| `dd` | Backup bloc (disque entier, MBR) | Copie bit-à-bit, idéal pour forensique |
| `dump/restore` | Backup ext2/3/4 par inodes | Sauvegarde FS au niveau système de fichiers |

## 1. Rsync — Sauvegarde Incrémentale Simple

```bash
# Sauvegarde locale (preserve permissions, owner, timestamps)
rsync -avz --delete /home/user/ /backup/home/user/

# Sauvegarde distante via SSH
rsync -avz --delete -e ssh /var/www/ user@backup-server:/backup/www/

# Avec exclussion
rsync -avz --delete --exclude='.cache/' --exclude='node_modules/' /home/user/ /backup/home/

# Backup différentiel (hard link) : chaque backup est complet mais partage les fichiers
rsync -avz --delete --link-dest=/backup/weekly/ /home/user/ /backup/daily/$(date +%Y%m%d)/
```

### Script de Rotation Rsync

```bash
#!/bin/bash
# /usr/local/bin/backup-rotate.sh
set -euo pipefail
SOURCE="/home/user/"
DEST="/backup/user/"
DATE=$(date +%Y%m%d)
WEEKDAY=$(date +%u)

# Backup quotidien avec hard links
rsync -avz --delete --link-dest="$DEST/latest" "$SOURCE" "$DEST/$DATE/"

# Mise à jour du lien "latest"
rm -f "$DEST/latest"
ln -s "$DEST/$DATE/" "$DEST/latest"

# Garder 7 jours, supprimer les plus vieux
find "$DEST" -maxdepth 1 -type d -name "20*" -mtime +7 -exec rm -rf {} \; 2>/dev/null

# Si dimanche (7), copier vers hebdomadaire
if [ "$WEEKDAY" -eq 7 ]; then
  cp -al "$DEST/$DATE/" "$DEST/weekly/$(date +%Y-week%V)"
fi
```

## 2. BorgBackup — Déduplication et Chiffrement

### Initialisation et Backup

```bash
# Installer
sudo apt install borgbackup   # Debian/Ubuntu
sudo dnf install borgbackup   # RHEL/Fedora

# Initialiser un dépôt
borg init --encryption=repokey-blake2 /mnt/backup/borg/filer

# Créer un backup (compression LZ4 rapide)
borg create --stats --progress --compression lz4 \
  /mnt/backup/borg/filer::{hostname}-{now:%Y%m%d_%H%M%S} \
  /home /etc /var/www

# Compression plus agressive
borg create --compression zstd,10 ...   # ratio meilleur, CPU modéré
```

### Restauration et Maintenance

```bash
# Lister les archives
borg list /mnt/backup/borg/filer

# Montrer les différences entre deux archives
borg diff /mnt/backup/borg/filer::archive1 archive2

# Restaurer une archive complète
cd / && borg extract /mnt/backup/borg/filer::20241001_030000

# Restaurer un dossier spécifique
borg extract /mnt/backup/borg/filer::20241001_030000 home/user/documents

# Vérifier l'intégrité
borg check /mnt/backup/borg/filer

# Purger les vieilles archives (rétention)
borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 3 \
  /mnt/backup/borg/filer
```

### Script Automatisé Borg

```bash
#!/bin/bash
# /usr/local/bin/borg-backup.sh
set -euo pipefail
export BORG_REPO="/mnt/backup/borg/filer"
export BORG_PASSPHRASE_FILE="/etc/borg-passphrase"
export BACKUP_PATH="/home /etc /var/www"

# Arrêter si verrou présent
borg lock $BORG_REPO && true

borg create --verbose --stats --compression zstd,6 \
  $BORG_REPO::{hostname}-{now:%Y%m%d_%H%M%S} $BACKUP_PATH

borg prune --keep-daily 7 --keep-weekly 4 --keep-monthly 6 $BORG_REPO

# Notifier
logger "Borg backup completed successfully"
```

## 3. Restic — Backup Cloud Natif

```bash
# Installer
sudo apt install restic

# Initialiser (exemple S3-compatible)
restic init --repo s3:https://s3.eu-west-3.amazonaws.com/mon-bucket/backup

# Backup
restic --repo s3:s3.eu-west-3.amazonaws.com/mon-bucket/backup \
  --password-file /etc/restic-password \
  backup /home /etc

# Restauration
restic restore latest --target /restore

# Monter une archive pour consultation
restic mount /mnt/restic-mount

# Vérifier
restic check
```

## 4. Sauvegarde de Bases de Données

### PostgreSQL
```bash
# Dump logique (complet)
pg_dumpall -U postgres -f /backup/pg/full_$(date +%Y%m%d).sql

# WAL archiving (PITR — Point In Time Recovery) dans postgresql.conf
# archive_command = 'cp %p /backup/wal/%f'
# restore_command = 'cp /backup/wal/%f %p'
```

### MySQL / MariaDB
```bash
# Dump toutes les bases
mysqldump --all-databases --single-transaction -u root -p | gzip > /backup/mysql/full_$(date +%Y%m%d).sql.gz

# Binary logs (PITR)
mysqlbinlog /var/log/mysql/mysql-bin.000001 > /backup/mysql/binlog_000001.sql
```

## 5. Sauvegarde de Configuration Système

```bash
# Avant une mise à jour critique
mkdir -p /var/backups/pre-upgrade
cp -a /etc /var/backups/pre-upgrade/etc/
dpkg --get-selections > /var/backups/pre-upgrade/dpkg-list.txt
# Pour RHEL : rpm -qa --qf '%{NAME}\n' > package-list.txt

# Restauration
dpkg --clear-selections && dpkg --set-selections < dpkg-list.txt
apt-get dselect-upgrade
```

## 6. Vérification et Tests de Restauration

> **Une sauvegarde non testée n'est pas une sauvegarde — c'est un vœu pieux.**

```bash
# Script de test de restauration (dry-run)
#!/bin/bash
set -euo pipefail

cd /tmp/restore-test
rm -rf test-restore

borg extract /mnt/backup/borg/filer::latest --dry-run

# Vérifier l'intégrité des dumps SQL
gunzip -c /backup/mysql/full_latest.sql.gz | head -50 > /dev/null
echo "Archive SQL OK"

# Vérifier que les fichiers critiques sont présents
borg list /mnt/backup/borg/filer::latest | grep -q /etc/passwd
echo "checkpoint: /etc/passwd présent"
```

## Pièges Courants

1. **Jamais testé** : La pire erreur. Tester la restauration au moins une fois par mois. Automatiser un script de vérification.

2. **Rotation non configurée** : Les sauvegardes s'accumulent jusqu'à saturer le disque. Toujours configurer `prune` ou `find -mtime`.

3. **Chiffrement sans gestion de clé** : Perdre la passphrase Borg/restic = perte définitive des données. Stocker les clés hors-site (password manager, coffre).

4. **Backup applications ouvertes** : Les fichiers modifiés pendant la copie peuvent être incohérents. Utiliser `fsfreeze` ou snapshots LVM figés.

5. **Chemin d'exclusion oublié** : Backuper `.cache/`, `node_modules/`, ou `.venv/` triple le volume. Toujours exclure ce qui est régénérable.

## Liste de vérification (Checklist)

- [ ] Règle 3-2-1 appliquée (3 copies, 2 supports, 1 hors-site)
- [ ] Test de restauration effectué et réussi
- [ ] Rotation configurée (quotidien → 7j, hebdo → 4 semaines, mensuel → 6 mois)
- [ ] Base de données sauvegardée en mode cohérent (`--single-transaction`, `pg_start_backup()`)
- [ ] Clés de chiffrement stockées hors-site
- [ ] Monitoring des sauvegardes (alerte si échec)
- [ ] Backup de la configuration système avant chaque mise à jour majeure
- [ ] Scripts système timer (systemd) activés et testés
- [ ] Documentation des procédures de restauration (DRP)
