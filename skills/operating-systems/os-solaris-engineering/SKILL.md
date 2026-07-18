---
name: os-solaris-engineering
description: "Administrer et optimiser Oracle Solaris, gérer la virtualisation légère par zones (Solaris Zones), configurer le système de fichiers ZFS, dépanner via DTrace et gérer les services avec SMF."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [solaris, oracle, zones, zfs, smf, dtrace, unix, system-ops]
  EVA:
    related_skills: [os-bsd-engineering, os-aix-engineering]
---

# Ingénierie Oracle Solaris (Zones, ZFS & DTrace)

## Vue d'ensemble

Cette compétence guide l'administration, la maintenance et l'optimisation des systèmes d'exploitation **Oracle Solaris** (anciennement Sun Solaris). Ce système Unix d'entreprise est réputé pour ses fonctionnalités innovantes de virtualisation intégrée (les **Zones Solaris**), son système de fichiers transactionnel **ZFS** (créé sous Solaris), sa gestion de services avancée **SMF (Service Management Facility)** et son outil de diagnostic dynamique de bas niveau **DTrace**.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Créer, cloner ou migrer des conteneurs système virtuels isolés (**Zones Solaris**).
- Gérer les pools de stockage (`zpool`) et les systèmes de fichiers ZFS (snapshots, miroirs, disques de secours).
- Diagnostiquer et résoudre des goulots d'étranglement de performance système à l'aide de scripts **DTrace** (appels système, latences E/S, mémoire).
- Gérer l'état des services système (démarrage, arrêt, dépendances) via l'outil **SMF** (`svcadm`, `svcs`).
- Administrer le système de paquets IPS (Image Packaging System).

## Virtualisation : Les Zones Solaris

Les zones Solaris permettent d'exécuter des environnements virtuels isolés partageant le même noyau que l'hôte (Global Zone), mais disposant de leurs propres processus et configurations réseau.

```bash
# Exemple de configuration et installation d'une zone nommée "EVA-zone"
# 1. Configurer la zone
sudo zonecfg -z EVA-zone
# (Dans l'invite zonecfg)
# zonecfg:EVA-zone> create
# zonecfg:EVA-zone> set zonepath=/zones/EVA-zone
# zonecfg:EVA-zone> set autoboot=true
# zonecfg:EVA-zone> add net
# zonecfg:EVA-zone:net> set physical=vnic1
# zonecfg:EVA-zone:net> end
# zonecfg:EVA-zone> commit
# zonecfg:EVA-zone> exit

# 2. Installer la zone (téléchargement des paquets requis)
sudo zoneadm -z EVA-zone install

# 3. Démarrer la zone
sudo zoneadm -z EVA-zone boot

# 4. Se connecter à la console de la zone
sudo zlogin -C EVA-zone
```

## Gestion des Services avec SMF (Service Management Facility)

Contrairement aux scripts d'initialisation SysV traditionnels, SMF gère automatiquement les dépendances entre services et redémarre instantanément les services qui tombent en panne.

```bash
# Vérifier le statut de tous les services locaux
svcs
# Rechercher les détails d'un service défaillant (ex: Apache)
svcs -xv apache24
# Activer/Démarrer un service de manière persistante
sudo svcadm enable apache24
# Désactiver/Arrêter un service
sudo svcadm disable apache24
# Redémarrer un service
sudo svcadm restart apache24
```

## Dépannage Dynamique avec DTrace

DTrace permet d'insérer des sondes dynamiques dans le système en production sans le ralentir ni l'interrompre.
Exemple de script simple (One-Liner) pour lister en temps réel quels fichiers sont ouverts et par quels processus :
```bash
sudo dtrace -n 'syscall::open*:entry { printf("%s opened %s", execname, copyinstr(arg0)); }'
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Perte de configuration de zone suite à des modifications directes :**
   * *Erreur :* Tenter de modifier manuellement les fichiers de configuration de la zone dans le chemin d'installation `/zones/` au lieu d'utiliser l'outil officiel `zonecfg`. Cela corrompt la base de données interne de Solaris et empêche le démarrage de la zone.
   * *Correction :* Toujours passer par les commandes `zonecfg` pour modifier les ressources physiques (RAM, CPU, cartes réseau) allouées à une zone.

2. **Désactivation forcée de services SMF sans analyser les dépendances :**
   * *Erreur :* Désactiver un service SMF de bas niveau nécessaire au réseau ou au stockage, bloquant ainsi le démarrage de nombreux services applicatifs qui en dépendent.
   * *Correction :* Toujours exécuter `svcs -d <nom_service>` pour lister les dépendances directes d'un service avant de le désactiver.

## Liste de vérification (Checklist)

- [ ] Les modifications des ressources de zones utilisent uniquement l'utilitaire `zonecfg`.
- [ ] Les services SMF sont vérifiés avec `svcs -xv` pour s'assurer qu'aucun service n'est dans l'état dégradé ou de maintenance (maintenance state).
- [ ] Le stockage ZFS utilise des disques configurés en miroir (`mirror`) ou en RAID-Z pour garantir la tolérance aux pannes matérielles.
- [ ] Les scripts DTrace exécutés en production n'utilisent pas d'agrégations trop gourmandes en mémoire pour éviter d'impacter le CPU.

