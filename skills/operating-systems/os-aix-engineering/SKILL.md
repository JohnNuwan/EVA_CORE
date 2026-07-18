---
name: os-aix-engineering
description: "Administrer et optimiser IBM AIX sur architecture IBM Power, configurer les partitions logiques (LPARs), gérer la base système ODM, administrer le stockage avec LVM AIX et installer via NIM."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [aix, ibm, power, lpar, odm, lvm-aix, nim, unix, system-ops]
  EVA:
    related_skills: [os-solaris-engineering, os-linux-admin]
---

# Ingénierie IBM AIX (LPAR, ODM & LVM AIX)

## Vue d'ensemble

Cette compétence guide l'administration, la maintenance et l'optimisation des serveurs **IBM AIX** s'exécutant sur l'architecture processeur **IBM Power Systems**. AIX est un Unix propriétaire très répandu dans le secteur bancaire et les grands systèmes industriels pour sa fiabilité de calcul. Il possède des spécificités majeures : la virtualisation matérielle par partitions logiques (**LPARs**), la base de données système centralisée **ODM (Object Data Manager)**, sa propre version du gestionnaire de volumes logiques (**LVM AIX**), et l'outil de déploiement réseau centralisé **NIM (Network Installation Management)**.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Gérer le stockage physique et logique sous AIX (Volume Groups, Logical Volumes, disques physiques) à l'aide des commandes `mkvg`, `chvg`, `mklv`.
- Interroger ou modifier la configuration des périphériques matériels dans la base de données **ODM** (`odmget`, `odmchange`, `lsdev`).
- Dépanner des configurations réseau, de routage ou de carte virtuelle Ethernet (VIO Client).
- Gérer les services système avec le contrôleur de ressources système **SRC (System Resource Controller)** (`startsrc`, `stopsrc`, `lssrc`).
- Effectuer des installations ou restaurations de serveurs à distance à l'aide de fichiers d'images de sauvegarde système (mksysb) via un serveur **NIM**.

## Manipulation de la Base de Configuration ODM (Object Data Manager)

L'ODM est une base de données orientée objet qui contient toute la configuration physique et logique du serveur (cartes réseau, disques, attributs système). Elle remplace les fichiers textes de configuration traditionnels.

```bash
# Lister tous les périphériques réseaux configurés (états "Defined" ou "Available")
lsdev -Cc adapter
# Afficher les attributs détaillés d'un équipement (ex: carte réseau ent0)
lsattr -El ent0
# Rechercher une définition d'objet dans l'ODM (ex: attributs de boot)
odmget -q "attribute=bootlist" PdAt
```

## Gestion du Stockage (LVM AIX)

Le LVM d'AIX possède une structure stricte de repérage et de montage.

```bash
# 1. Identifier les disques physiques connectés (Physical Volumes - PV)
lspv
# 2. Créer un groupe de volumes "datavg" sur le disque hdisk1
mkvg -y datavg hdisk1
# 3. Créer un volume logique "datalv" de 20 partitions logiques (LPs)
mklv -y datalv datavg 20
# 4. Créer un système de fichiers JFS2 sur le volume logique
crfs -v jfs2 -d datalv -m /data -A yes
# 5. Monter le système de fichiers
mount /data
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Modification manuelle de fichiers système sans utiliser l'ODM :**
   * *Erreur :* Configurer des cartes réseau ou ajouter des paramètres de boot manuellement dans des scripts de démarrage généraux. Au redémarrage, l'ODM restaurera la configuration enregistrée dans sa base, écrasant vos modifications.
   * *Correction :* Toujours utiliser les commandes dédiées (`chdev`, `mkdev`, `rmdev`) ou l'interface d'administration en mode texte **SMIT** (`smit` ou `smitty`) qui modifie simultanément l'ODM et le système actif.

2. **Dépassement de la taille des VG (Volume Groups) par manque de partitions physiques :**
   * *Erreur :* Définir une taille de partition physique (PP Size) trop petite lors de la création d'un Volume Group, empêchant ensuite d'étendre la taille du volume ou d'ajouter de nouveaux disques.
   * *Correction :* Anticiper la croissance du stockage et choisir une taille de PP (ex: 64M, 128M ou 256M) adaptée à la taille finale estimée du stockage.

## Liste de vérification (Checklist)

- [ ] L'outil d'administration textuel `smitty` est privilégié pour éviter les erreurs de syntaxe sur les commandes complexes.
- [ ] La base ODM est cohérente (aucun équipement n'est bloqué à l'état `Defined` s'il doit être actif, vérifier qu'il est bien `Available`).
- [ ] Les sauvegardes régulières du système d'exploitation sont générées à l'aide de la commande `mksysb` et stockées sur un serveur NIM externe.
- [ ] Le statut des services système critiques gérés par le SRC est valide (`lssrc -a`).

