---
name: sysadmin-kernel-tuning
description: "Réglage fin du noyau Linux : sysctl, paramètres mémoire/CPU/réseau, scheduler, swappiness, hugepages, cgroups, I/O scheduler, limites système et profils de performance."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [kernel, sysctl, tuning, performance, memory, cpu, scheduler, cgroups, hugepages, i-o, filesystem, networking]
    related_skills: [os-linux-admin, sysadmin-monitoring, sysadmin-lvm, os-debian-ubuntu-engineering, os-rhel-engineering]
---

# Réglage Fin du Noyau Linux (Kernel Tuning)

## Vue d'ensemble

Le noyau Linux offre des centaines de paramètres ajustables via `sysctl` pour optimiser les performances selon la charge de travail : base de données, serveur web, calcul Haute Performance (HPC), conteneurisation, etc.

**Principe :** Charger les paramètres au boot via `/etc/sysctl.d/` — chaque fichier `.conf` est appliqué automatiquement.

## Quand l'utiliser

- Optimiser un serveur de base de données (PostgreSQL, MySQL)
- Réduire la latence réseau (serveur web, API)
- Améliorer les performances I/O pour du calcul intensif
- Configurer HugePages pour des applications mémoire-intensive
- Ajuster les limites système (open files, threads, processes)
- Activer/désactiver des fonctionnalités du noyau (sécurité, debogage)

## 1. Paramètres Généraux

```bash
# /etc/sysctl.d/99-performance.conf

# Kernel : réduction du swapping (essentiel pour serveurs)
vm.swappiness = 10
# Valeur 0 = désactiver le swap (sauf OOM)
# Valeur 10 = swap seulement en cas de pression mémoire extrême
# Valeur 60 = valeur par défaut (équilibré)

# Cache VFS (utilise la RAM libre pour les métadonnées fichiers)
vm.vfs_cache_pressure = 50
# 100 = défaut, plus agressif pour libérer le cache de dentries/inodes
# 50 = garder le cache plus longtemps

# Dirty pages (écriture disque)
vm.dirty_ratio = 40
vm.dirty_background_ratio = 5
# dirty_ratio = % max de RAM sale avant que les écritures soient bloquées
# dirty_background_ratio = % de RAM sale pour lancer l'écriture async

# Nombre max de mappages mémoire
vm.max_map_count = 1048576
# Augmenter pour Elasticsearch, MongoDB, jeux, conteneurs
```

## 2. Mémoire et HugePages

```bash
# /etc/sysctl.d/99-hugepages.conf

# HugePages (pages mémoire de 2 Mo au lieu de 4 Ko)
# Essentiel pour les bases de données (PostgreSQL, Oracle, MySQL)
# et les VMs (KVM, QEMU)
vm.nr_hugepages = 2048      # 2048 * 2Mo = 4 Go réservés

# Voir l'état des HugePages
grep HugePages /proc/meminfo
# HugePages_Total: 2048
# HugePages_Free: 2048
# HugePages_Rsvd: 0

# Transparent HugePages (THP) — souvent problématique pour les BDD
# Désactiver pour bases de données (fragmentation, latences)
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/enabled
echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag
# ou via sysfs :
# kernel/mm/transparent_hugepage/enabled = never

# Limiter la mémoire allocatable pour un processus (via systemd)
# MemoryMax=4G dans l'unité systemd
```

### Taille des Pages et Performances

| Page Size | Avantage | Usage |
|-----------|----------|-------|
| 4 Ko (défaut) | Standard, faible gaspillage | Usage général |
| 2 Mo (HugePages) | Moins de TLB misses, meilleure cache | BDD, VMs, HPC |
| 1 Go (HugePages géants) | Très grandes allocs | VMs lourdes, GPU |

## 3. Scheduler CPU et Process

```bash
# /etc/sysctl.d/99-sched.conf

# Priorité du scheduler pour tâches interactives
kernel.sched_min_granularity_ns = 4000000    # 4 ms
kernel.sched_latency_ns = 24000000           # 24 ms
kernel.sched_wakeup_granularity_ns = 3000000 # 3 ms (défaut: 4ms)

# Paramètres CPUFreq (selon driver)
# Performance (max fréquence) :
sudo cpupower frequency-set -g performance
# Powersave (économique) :
# sudo cpupower frequency-set -g powersave

# Afficher le gouverneur actuel
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

# CPU isolation (isoler des cœurs pour des processus dédiés)
# Dans /etc/default/grub :
# GRUB_CMDLINE_LINUX="isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3"
# Puis sudo update-grub && reboot
```

### Scheduler I/O

```bash
# Voir le scheduler d'un disque
cat /sys/block/sda/queue/scheduler
# Résultat: [mq-deadline] kyber bfq none

# Changer le scheduler pour un disque (ex: nvme -> none)
echo none | sudo tee /sys/block/nvme0n1/queue/scheduler

# Paramètres I/O avancés
# /etc/sysctl.d/99-io.conf
vm.dirty_writeback_centisecs = 1500        # pdflush toutes les 15s
# Augmenter la priorité des I/O pour un processus
# via ionice : ionice -c 1 -n 0 command
```

## 4. Réseau (Optimisation pour Faible Latence / Haut Débit)

```bash
# /etc/sysctl.d/99-network.conf

# Backlog de connexions (augmenter pour serveurs à forte charge)
net.core.somaxconn = 65535
net.core.netdev_max_backlog = 5000

# Buffer réseau TCP (augmenter pour haut débit)
net.core.rmem_max = 134217728     # 128 Mo max réception
net.core.wmem_max = 134217728     # 128 Mo max envoi

# TCP auto-tuning
net.ipv4.tcp_rmem = 4096 87380 134217728   # min, default, max
net.ipv4.tcp_wmem = 4096 65536 134217728

# Réduction de latence
net.ipv4.tcp_fastopen = 3          # TFO (client + server)
net.ipv4.tcp_slow_start_after_idle = 0  # pas de reset du slow start
net.ipv4.tcp_notsent_lowat = 16384     # low watermark

# Réutilisation rapide des ports
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15

# TCP BBR (congestion control moderne, très performant)
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Sécurité réseau (syn flood, etc.)
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_syn_retries = 2
net.ipv4.conf.all.rp_filter = 1

# Augmenter les ports locaux disponibles
net.ipv4.ip_local_port_range = 1024 65535
```

### TCP BBR

```bash
# Vérifier si BBR est disponible
cat /proc/sys/net/ipv4/tcp_available_congestion_control
# Résultat: reno cubic bbr

# Activer BBR (déjà dans la config ci-dessus)
sysctl net.ipv4.tcp_congestion_control
# Résultat: bbr
```

## 5. Limites Système (ulimit)

```bash
# /etc/security/limits.conf — limites PAM (par utilisateur)
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 65536
* hard nproc 65536
* soft memlock unlimited
* hard memlock unlimited

# Vérifier les limites actuelles d'un processus
cat /proc/1/limits   # init/systemd
ulimit -n            # shell actuel
ulimit -a            # toutes les limites

# Pour systemd services : dans l'unité .service
# [Service]
# LimitNOFILE=1048576
# LimitNPROC=65536
# LimitMEMLOCK=infinity
# TasksMax=65536
```

## 6. Cgroups v2 (Contrôle des Ressources)

```bash
# cgroups v2 est utilisé par systemd et les conteneurs
# Voir la hiérarchie
ls /sys/fs/cgroup/
# Résultat: cpu/ memory/ io/ pids/ ...

# Limiter la mémoire d'un processus via cgroups
sudo mkdir /sys/fs/cgroup/memory/myapp
echo 500000000 | sudo tee /sys/fs/cgroup/memory/myapp/memory.max  # 500 Mo
echo $PID | sudo tee /sys/fs/cgroup/memory/myapp/cgroup.procs

# Via systemd (recommandé) :
systemd-run --user --scope -p MemoryMax=500M -p CPUQuota=50% ./myapp
```

## 7. Profils par Charge de Travail

### Serveur de Base de Données (PostgreSQL / MySQL)

```bash
# /etc/sysctl.d/90-database.conf
vm.swappiness = 1
vm.dirty_ratio = 30
vm.dirty_background_ratio = 3
vm.nr_hugepages = 4096
kernel.numa_balancing = 0        # désactiver NUMA balancing (important pour BDD)
net.core.somaxconn = 65535
fs.aio-max-nr = 1048576
```

### Serveur Web / API (Haute Concurrence)

```bash
# /etc/sysctl.d/90-webserver.conf
net.core.somaxconn = 65535
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 10
net.core.rmem_max = 67108864
net.core.wmem_max = 67108864
net.ipv4.tcp_congestion_control = bbr
fs.file-max = 2097152
```

### HPC / Calcul Intensif

```bash
# /etc/sysctl.d/90-hpc.conf
kernel.numa_balancing = 0
vm.swappiness = 0
vm.nr_hugepages = 16384
kernel.sched_min_granularity_ns = 10000000
kernel.sched_migration_cost_ns = 5000000
kernel.sched_autogroup_enabled = 0   # désactiver autogroup pour isolation
```

## 8. Script d'Application au Boot

```bash
#!/bin/bash
# /usr/local/bin/apply-kernel-tune.sh
# Appliqué par systemd (sysctl.d est automatique, mais certains paramètres
# sysfs nécessitent un script)

set -euo pipefail

echo "=== Application des réglages noyau avancés ==="

# THP : désactiver pour bases de données
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# Scheduler I/O pour NVMe
for disk in /sys/block/nvme*/queue/scheduler; do
    echo none > "$disk"
done

# CPU governor (si cpupower pas installé)
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor 2>/dev/null || true

echo "OK"
```

```bash
# Service systemd correspondant (si nécessaire)
# /etc/systemd/system/kernel-tune.service
```

## 9. Diagnostic et Vérification

```bash
# Voir tous les paramètres sysctl actifs
sysctl -a | grep -E "swappiness|dirty|hugepage"
sysctl net.ipv4.tcp_congestion_control

# Benchmarks de base
# CPU :
sysbench cpu run
# Mémoire :
sysbench memory run
# I/O :
fio --randrepeat=1 --ioengine=libaio --direct=1 --gtod_reduce=1 \
    --name=test --bs=4k --iodepth=64 --size=1G --readwrite=randrw --rwmixread=75
# Réseau :
iperf3 -c serveur_central
```

## Pièges Courants

1. **Réglages trop agressifs** : Modifier tous les paramètres d'un coup sans les tester individuellement. Utiliser des changements incrémentaux et mesurer l'impact.

2. **vm.swappiness=0** : Ne désactive PAS complètement le swap. Le noyau peut encore swapper. Pour désactiver, retirer complètement le swap (`swapoff -a`).

3. **THP pour les BDD** : Transparent HugePages cause des latences importantes (allocation de pages fragmentée). Toujours désactiver pour PostgreSQL, MySQL, MongoDB.

4. **net.core.rmem_max / wmem_max trop bas** : Limite le débit réseau pour les connexions à haute latence (longue distance). Vérifier avec `iperf3`.

5. **BBR non disponible** : BBR nécessite un noyau ≥ 4.9. Vérifier avec `modprobe tcp_bbr`.

6. **Oublier de rendre les changements persistants** : Les modifications `/sys/` sont volatiles. Les passer par sysctl.d/.

## Liste de vérification (Checklist)

- [ ] Sysctl configuré dans `/etc/sysctl.d/` pour le profil serveur
- [ ] THP désactivé pour les bases de données si présentes
- [ ] BBR activé si noyau ≥ 4.9 et driver réseau compatible
- [ ] HugePages configurées si application mémoire-intensive
- [ ] Limites nofile/nproc augmentées dans `/etc/security/limits.conf`
- [ ] CPU governor en mode "performance" pour les charges serveur
- [ ] Swap désactivé ou swappiness réduit (< 10)
- [ ] Scheduler I/O adapté (none pour NVMe, mq-deadline pour SSD)
- [ ] Tests de charge effectués après tuning
- [ ] Sauvegarde des paramètres précédents avant modification
