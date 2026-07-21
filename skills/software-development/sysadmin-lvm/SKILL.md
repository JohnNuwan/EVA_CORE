---
name: sysadmin-lvm
description: "Gestion avancée de LVM2 : volumes physiques, groupes de volumes, volumes logiques, thin provisioning, snapshots, migration, cache, RAIDs logiciels LVM et dépannage."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [lvm, storage, logical-volume, filesystem, disk, partitioning, pv, vg, lv, thin-provisioning, snapshot]
    related_skills: [os-linux-admin, sysadmin-backup-strategies, sysadmin-kernel-tuning]
---

# Gestion Avancée LVM2 (Logical Volume Manager)

## Vue d'ensemble

LVM2 permet une gestion flexible et dynamique du stockage sur Linux, en abstraction au-dessus des disques physiques. Contrairement au partitionnement traditionnel, LVM permet d'étendre, réduire, migrer et snapshoter des volumes à chaud sans démontage.

**Concepts clés :**
- **PV (Physical Volume)** : disque ou partition brute initialisée pour LVM
- **VG (Volume Group)** : pool de stockage agrégeant un ou plusieurs PV
- **LV (Logical Volume)** : volume logique découpé dans le VG, utilisé comme un bloc device (`/dev/vg_name/lv_name`)
- **PE (Physical Extent)** : unité d'allocation (4 MiB par défaut)

## Quand l'utiliser

- Créer ou étendre des systèmes de fichiers sans partitionnement
- Mettre en place du thin provisioning pour des environnements virtualisés
- Faire des snapshots rapides avant des opérations risquées (mise à jour, upgrade)
- Migrer des données entre disques à chaud (remplacement de disque défaillant)
- Monter des caches LVM sur SSD pour accélérer un volume sur HDD

## Commandes Essentielles

### Création et Découverte

```bash
# Initialiser un disque comme volume physique
sudo pvcreate /dev/sdb /dev/sdc

# Afficher les PVs
sudo pvs              # compact
sudo pvdisplay        # détaillé

# Créer un groupe de volumes
sudo vgcreate vg_data /dev/sdb /dev/sdc

# Afficher les VGs
sudo vgs
sudo vgdisplay

# Créer un volume logique (ext4)
sudo lvcreate -L 100G -n lv_projects vg_data
sudo mkfs.ext4 /dev/vg_data/lv_projects
sudo mount /dev/vg_data/lv_projects /mnt/projects
```

### Extension et Réduction

```bash
# Étendre un LV de 50 Go supplémentaires
sudo lvextend -L +50G /dev/vg_data/lv_projects

# OU étendre à une taille absolue
sudo lvextend -L 200G /dev/vg_data/lv_projects

# Redimensionner le système de fichiers
sudo resize2fs /dev/vg_data/lv_projects       # ext4
sudo xfs_growfs /mnt/projects                  # XFS (monté)

# Ajouter un nouveau disque au VG puis étendre
sudo pvcreate /dev/sdd
sudo vgextend vg_data /dev/sdd
sudo lvextend -L +200G /dev/vg_data/lv_projects
sudo resize2fs /dev/vg_data/lv_projects
```

### Réduction (ext4 uniquement — démonter d'abord)

```bash
# 1. Démonter
sudo umount /mnt/projects
# 2. Vérifier le système de fichiers
sudo e2fsck -f /dev/vg_data/lv_projects
# 3. Réduire le système de fichiers
sudo resize2fs /dev/vg_data/lv_projects 80G
# 4. Réduire le LV
sudo lvreduce -L 80G /dev/vg_data/lv_projects
# 5. Remonter
sudo mount /dev/vg_data/lv_projects /mnt/projects
```

> **Attention** : XFS ne peut PAS être réduit. Pour réduire un LV XFS, il faut sauvegarder, recréer et restaurer.

## Thin Provisioning

Permet de sur-allouer de l'espace (overcommitment) :

```bash
# Créer un pool thin
sudo lvcreate -L 500G -T vg_data/thin_pool

# Créer un volume thin (alloué virtuellement)
sudo lvcreate -V 1T -T vg_data/thin_pool -n lv_thin_vm1
sudo mkfs.ext4 /dev/vg_data/lv_thin_vm1

# Surveiller l'utilisation réelle du pool
sudo lvs -a -o+discards,chunksize,size,data_percent,metadata_percent
```

> ⚠️ **Surveiller le data_percent !** Si le pool thin est plein (100%), tous les volumes thin deviennent inaccessibles. Mettre en place une alerte à 80%.

## Snapshots

Les snapshots LVM sont des copies quasi-instanées (redirect-on-write) :

```bash
# Créer un snapshot (allouer assez d'espace pour les changements)
sudo lvcreate -s -n lv_projects_snap -L 20G /dev/vg_data/lv_projects

# Fusionner un snapshot (restaurer l'état)
sudo lvconvert --merge /dev/vg_data/lv_projects_snap
# Le snapshot est fusionné au prochain mount ou immédiatement si le FS est démonté

# Supprimer un snapshot
sudo lvremove /dev/vg_data/lv_projects_snap
```

> Pour un snapshot cohérent au niveau fichier, figer le FS avec `fsfreeze -f /mount/point` avant, puis dégeler avec `fsfreeze -u /mount/point`.

## Migration à Chaud (Pvmove)

```bash
# Déplacer les données d'un disque défaillant vers un autre PV
sudo pvmove /dev/sdb /dev/sdd

# Retirer le PV du VG
sudo vgreduce vg_data /dev/sdb
sudo pvremove /dev/sdb
# Le disque peut maintenant être physiquement retiré
```

## Cache LVM (HDD + SSD)

```bash
# Créer un LV cache (sur SSD rapide)
sudo lvcreate -L 50G -n lv_cache vg_data /dev/sdf

# Créer le LV de métadonnées du cache
sudo lvcreate -L 8G -n lv_cache_meta vg_data /dev/sdf

# Associer le cache au LV lent
sudo lvconvert --type cache --cachepool vg_data/lv_cache \
  --cachemode writethrough /dev/vg_data/lv_projects

# Voir l'état du cache
sudo lvs -a -o+policy,cache_settings,cache_mode
# cachemode writethrough = safe (données écrites sur HDD+SSD)
# cachemode writeback  = plus rapide mais perte possible si crash SSD
```

## RAID Logiciel LVM

```bash
# RAID 1 (mirror) entre deux PVs
sudo lvcreate --type raid1 -L 200G -n lv_mirror vg_data

# RAID 5 (3 PVs minimum)
sudo lvcreate --type raid5 -L 500G -n lv_raid5 vg_data

# RAID 6 (4 PVs minimum, double parité)
sudo lvcreate --type raid6 -L 500G -n lv_raid6 vg_data

# Vérifier le statut RAID
sudo lvs -a -o+raid_sync_action,raid_mismatch_count,sync_percent
```

## Dépannage (Troubleshooting)

### LV manquant au boot (LVM non activé)
```bash
sudo vgchange -ay          # Activer tous les VGs
sudo lvscan                # Scanner et afficher les LVs
```

### PV manquant ou perdu (disque remplacé)
```bash
# Marquer le PV manquant comme absent
sudo vgreduce --removemissing vg_data

# Si le disque revient avec un nouveau path (ex: /dev/sdb vs /dev/sdc)
sudo pvcreate /dev/sdc -u <UUID_original> --restorefile /etc/lvm/backup/vg_data
sudo vgcfgrestore vg_data
```

### Métadonnées corrompues
```bash
# Restaurer depuis le backup automatique LVM
sudo vgcfgrestore -f /etc/lvm/archive/vg_data_00000.vg vg_data
```

## Pièges Courants

1. **Snapshot plein** : Un snapshot LVM devient inaccessible quand il est plein. Surveiller avec `lvs -o+snap_percent`. Supprimer et recréer dès qu'il dépasse 80%.

2. **Thin pool full** : Irrécupérable sans ajout d'espace au pool. Ne jamais sur-allouer sans monitoring, ou configurer `dm-thin-pool` avec auto-extension :
   ```
   # /etc/lvm/lvm.conf
   thin_pool_autoextend_threshold = 75
   thin_pool_autoextend_percent = 20
   ```

3. **LVREDUCE XFS impossible** : Vérifier le type de FS avant toute réduction. Sur XFS, seule l'extension est possible à chaud.

4. **pvcreate efface les données** : `pvcreate` écrit un label LVM sur le disque, détruisant la table de partitions. Vérifier que le disque ne contient pas de données importantes avant.

## Liste de vérification (Checklist)

- [ ] Vérifier l'espace dans le VG avant d'étendre : `vgs vg_data`
- [ ] Vérifier le type de FS avant réduction : `blkid /dev/vg_data/lv_name`
- [ ] Toujours démonter avant de réduire un LV
- [ ] Surveiller les snapshots et thin pools avec `lvs -a -o+snap_percent,data_percent`
- [ ] Configurer l'auto-extension pour thin pools dans `/etc/lvm/lvm.conf`
- [ ] Activer les snapshots LVM dans les scripts de backup avant une tâche risquée
- [ ] Documenter la topologie LVM (PV → VG → LV) dans un fichier `/etc/lvm/topology.txt`
