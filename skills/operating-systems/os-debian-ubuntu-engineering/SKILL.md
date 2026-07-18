---
name: os-debian-ubuntu-engineering
description: "Administrer et optimiser Debian et Ubuntu Server, configurer le gestionnaire de paquets APT, paramétrer le réseau avec Netplan, sécuriser via AppArmor et automatiser les installations."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux]
metadata:
  tags: [debian, ubuntu, apt, netplan, apparmor, autoinstall, system-ops]
  helios:
    related_skills: [os-linux-admin, os-rhel-engineering]
---

# Configuration Debian & Ubuntu Server

## Vue d'ensemble

Cette compétence guide l'administration, la configuration et l'optimisation des distributions **Debian** et **Ubuntu Server**. Ces systèmes d'exploitation, très populaires pour l'hébergement de conteneurs (Docker) et d'applications Web légères, requièrent la maîtrise du gestionnaire de paquets **APT** (Advanced Package Tool), de l'outil de configuration réseau moderne **Netplan**, et du module de sécurité noyau **AppArmor** pour isoler les applications.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Gérer, épingler (pinning) ou dépanner des dépôts de paquets avec APT.
- Configurer des adresses IP statiques, des liaisons réseau (Bonds) ou des VLANs sous Ubuntu avec Netplan.
- Créer ou modifier des profils de confinement de sécurité **AppArmor**.
- Mettre en place des installations automatiques de serveurs (Ubuntu Autoinstall / Debian Preseed).
- Dépanner des configurations de paquets corrompues (`dpkg`, `apt-get -f install`).

## Configuration Réseau avec Netplan (Fichier YAML)

Sous Ubuntu, le réseau est configuré via des fichiers YAML situés dans `/etc/netplan/`. Netplan traduit ensuite ces fichiers pour le moteur réseau cible (généralement `systemd-networkd` sur serveur ou `NetworkManager` sur bureau).

### Exemple de configuration IP statique : `/etc/netplan/01-netcfg.yaml`

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    enp3s0:
      dhcp4: no
      addresses:
        - 192.168.1.150/24
      routes:
        - to: default
          via: 192.168.1.254
      nameservers:
        addresses:
          - 1.1.1.1
          - 8.8.8.8
```

*Commandes d'application* :
- **Tester la configuration** (sécurité anti-coupure) : `sudo netplan try` (annule automatiquement les modifications au bout de 120 secondes sans validation de l'administrateur).
- **Appliquer** : `sudo netplan apply`

## Gestion Avancée des Paquets avec APT

### Épinglage de paquets (APT Pinning)
Pour bloquer la mise à jour automatique d'un paquet critique (ex: un serveur de base de données PostgreSQL) afin de garantir la stabilité :
Fichier : `/etc/apt/preferences.d/pin-postgres`
```text
Package: postgresql*
Pin: version 15.*
Pin-Priority: 1001
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Erreur d'indentation dans les fichiers Netplan (YAML) :**
   * *Erreur :* Utiliser des tabulations ou insérer un mauvais nombre d'espaces dans le fichier de configuration réseau `/etc/netplan/*.yaml`. Netplan refusera de charger le fichier, coupant le réseau lors du redémarrage.
   * *Correction :* N'utiliser que des espaces pour l'indentation YAML et valider systématiquement la syntaxe à l'aide de la commande sécurisée `sudo netplan try` avant d'appliquer définitivement.

2. **Échec de déploiement à cause de conflits AppArmor :**
   * *Erreur :* Déplacer le répertoire de données d'un service (comme MySQL) vers un disque externe et voir le service refuser de démarrer avec une erreur "Permission Denied" (alors que les droits `chmod` sont corrects).
   * *Correction :* AppArmor bloque l'accès en écriture en dehors des chemins par défaut déclarés dans son profil. Modifier le profil AppArmor du service (situé dans `/etc/apparmor.d/usr.sbin.mysqld`) pour inclure le nouveau chemin d'accès, puis recharger les profils avec `sudo systemctl reload apparmor`.

## Liste de vérification (Checklist)

- [ ] Les fichiers réseau Netplan ont été testés avec la commande `netplan try` avant application permanente.
- [ ] Les paquets dont la version doit rester fixe pour assurer la stabilité logicielle sont épinglés via les préférences APT (APT Pinning).
- [ ] Les profils AppArmor pour les services exposés sur le réseau sont actifs (`aa-status`) et mis à jour pour autoriser les répertoires personnalisés.
- [ ] Les dépôts de paquets tiers (`/etc/apt/sources.list.d/`) utilisent des clés GPG signées stockées de manière sécurisée sous `/usr/share/keyrings/`.

