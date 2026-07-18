---
name: os-bsd-engineering
description: "Administrer et sécuriser les systèmes BSD (FreeBSD, OpenBSD), configurer l'isolation par Jails, paramétrer le pare-feu PF (Packet Filter), et intégrer le stockage ZFS."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [bsd, freebsd, openbsd, jails, pf, zfs, security, firewall]
  helios:
    related_skills: [os-linux-admin, os-solaris-engineering]
---

# Ingénierie des Systèmes BSD (FreeBSD & OpenBSD)

## Vue d'ensemble

Cette compétence guide l'administration et la sécurisation des systèmes d'exploitation de la famille **BSD** (principalement **FreeBSD** pour les serveurs et le stockage, et **OpenBSD** pour la sécurité réseau et les pare-feu). L'ingénierie BSD se distingue par une architecture propre unifiant le noyau et l'espace utilisateur de base. Elle fait appel à des outils avancés d'isolation comme les **Jails** de FreeBSD, au système de fichiers transactionnel **ZFS** et au pare-feu réseau **PF (Packet Filter)**.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Créer, configurer ou isoler des applications dans des conteneurs légers de sécurité (**Jails** sous FreeBSD).
- Rédiger des règles de pare-feu réseau complexes pour **PF (Packet Filter)** sous OpenBSD ou FreeBSD.
- Administrer des pools de stockage et des datasets avec **ZFS** (clichés/snapshots, compression, quotas).
- Compiler et gérer des logiciels tiers via le système des Ports ou le gestionnaire de paquets `pkg`.
- Configurer les mécanismes de sécurité d'OpenBSD comme la restriction d'appels système via `pledge` et `unveil`.

## Configuration du Pare-feu PF (Packet Filter)

Le pare-feu PF d'OpenBSD est réputé pour sa syntaxe claire et sa robustesse.
Fichier type : `/etc/pf.conf`

```text
# Déclarer les interfaces réseau
ext_if = "em0"
int_if = "em1"

# Déclarer les ports autorisés
allowed_tcp_ports = "{ 22, 80, 443 }"

# Politique par défaut : bloquer tout le trafic entrant et sortant
set skip on lo0
block all

# Autoriser le trafic sortant sécurisé
pass out on $ext_if proto { tcp, udp, icmp } keep state

# Autoriser les connexions entrantes sur les ports configurés
pass in on $ext_if proto tcp to any port $allowed_tcp_ports keep state
```

*Commandes d'administration* :
- **Tester la syntaxe** du fichier : `sudo pfctl -nf /etc/pf.conf`
- **Charger** les règles : `sudo pfctl -f /etc/pf.conf`
- **Activer/Désactiver** le pare-feu : `sudo pfctl -e` / `sudo pfctl -d`

## Virtualisation Légère : Les Jails de FreeBSD

Les Jails permettent d'isoler un processus et ses sous-processus dans un environnement racine virtuel (chroot amélioré) disposant de sa propre adresse IP et de sa configuration d'utilisateurs.

```bash
# Exemple de création simplifiée de Jail sous FreeBSD (via l'outil iocage)
# 1. Télécharger la version de base de FreeBSD
sudo iocage fetch
# 2. Créer une nouvelle Jail nommée "actemium_web"
sudo iocage create -r 13.2-RELEASE -n actemium_web ip4_addr="em1|192.168.1.50/24"
# 3. Démarrer la Jail
sudo iocage start actemium_web
# 4. Ouvrir une console interactive dans la Jail
sudo iocage console actemium_web
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Dépassement de capacité mémoire de ZFS (ARC) :**
    *   *Erreur :* Laisser ZFS utiliser toute la RAM disponible pour son cache de lecture (ARC) sur un serveur FreeBSD hébergeant également des applications lourdes (bases de données, machines virtuelles). Cela peut provoquer des crashs par manque de mémoire (Out of Memory).
    *   *Correction :* Limiter la taille maximale du cache ARC dans le fichier de configuration du noyau `/boot/loader.conf`. Exemple : `vfs.zfs.arc_max="4G"` (pour limiter à 4 Go).

2.  **Ignorer l'ordre d'évaluation des règles dans PF :**
    *   *Erreur :* Sous PF, contrairement à d'autres pare-feu (comme iptables), c'est la **dernière règle correspondante** (Last Match) qui s'applique, sauf si le mot-clé `quick` est utilisé. Écrire une règle de blocage au début du fichier puis une règle générique d'ouverture à la fin peut réouvrir des ports non souhaités.
    *   *Correction :* Utiliser le mot-clé `quick` (ex: `block in quick on $ext_if proto tcp to any port 23`) pour arrêter l'évaluation dès qu'une règle correspond, ou structurer rigoureusement le fichier du général au particulier.

## Liste de vérification (Checklist)

- [ ] La syntaxe du fichier de règles PF est testée avec `pfctl -nf` avant d'être rechargée.
- [ ] Le cache ZFS (ARC) est limité pour préserver la RAM des applications hôtes.
- [ ] Les Jails possèdent des adresses IP dédiées et des restrictions d'accès réseau via le système de fichiers `/dev` de la Jail.
- [ ] Les systèmes OpenBSD utilisent les privilèges minimaux (ex: interdiction d'accès root direct en SSH, authentification par clés).

