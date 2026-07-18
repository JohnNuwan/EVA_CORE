---
name: os-suse-engineering
description: "Administrer SUSE Linux Enterprise Server (SLES), utiliser l'outil d'administration centralisé YaST, configurer les paquets avec Zypper et déployer des clusters de haute disponibilité (SLES HA)."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  tags: [sles, suse, yast, zypper, high-availability, clustering, system-ops]
  EVA:
    related_skills: [os-linux-admin, os-rhel-engineering]
---

# Configuration SUSE Linux Enterprise Server (SLES)

## Vue d'ensemble

Cette compétence guide l'administration et l'ingénierie système de **SUSE Linux Enterprise Server (SLES)**. SLES est une distribution Linux commerciale de classe entreprise, largement utilisée dans les environnements SAP et dans l'industrie lourde. Sa gestion se caractérise par l'utilisation de l'outil d'administration centralisé **YaST** (Yet another Setup Tool), du gestionnaire de paquets en ligne de commande **Zypper**, et de la mise en place de clusters de haute disponibilité (**SLES HA Extension**).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Configurer le système (réseau, pare-feu, services, matériel) à l'aide de l'interface graphique ou textuelle de **YaST**.
- Gérer l'installation, la mise à jour et les verrous (locks) de paquets sous SLES avec **Zypper**.
- Configurer ou dépanner un cluster de haute disponibilité (HA) basé sur Pacemaker et Corosync sous SLES.
- Mettre en place des serveurs d'installation automatisée AutoYaST.
- Gérer des systèmes SLES d'entreprise via SUSE Manager.

## Gestion des Paquets avec Zypper

### 1. Commandes de base
Contrairement à APT ou DNF, Zypper possède des fonctionnalités avancées intégrées de gestion des dépendances et de verrouillage de versions.
```bash
# Rechercher un paquet
zypper se <nom_paquet>
# Installer un paquet sans interaction
zypper in -y <nom_paquet>
# Appliquer toutes les mises à jour de sécurité disponibles
zypper patch
```

### 2. Épinglage (verrouillage) de versions avec Zypper
Pour empêcher la mise à jour involontaire d'un paquet critique (ex: la base de données SAP HANA ou un noyau) :
```bash
# Verrouiller le paquet kernel-default
sudo zypper addlock kernel-default
# Lister les verrous actifs
zypper locks
# Supprimer le verrou
sudo zypper removelock kernel-default
```

## Haute Disponibilité (SLES HA Extension)

Le cluster SLES HA utilise **Corosync** pour la communication entre nœuds et **Pacemaker** pour la gestion des ressources du cluster (ex: adresses IP virtuelles, services de base de données).

```bash
# Vérifier l'état du cluster Pacemaker
sudo crm status
# Lister les ressources configurées
sudo crm resource list
# Mettre un nœud en mode maintenance
sudo crm node maintenance <nom_noeud>
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Conflits entre YaST et les configurations manuelles :**
    *   *Erreur :* Modifier directement des fichiers de configuration complexes à la main (ex: `/etc/sysconfig/network/config`) puis lancer l'outil YaST. YaST peut écraser ou ignorer les modifications manuelles non standard lors de sa prochaine exécution.
    *   *Correction :* Privilégier l'utilisation de YaST (en mode texte `sudo yast` dans le terminal) pour toutes les configurations réseau et système principales afin de préserver la cohérence de la base de données système SUSE.

2.  **Mises à jour rompant le cluster HA (Haute Disponibilité) :**
    *   *Erreur :* Mettre à jour les packages de Pacemaker ou de Corosync sur un seul nœud du cluster en production, créant un désalignement de version qui sépare le cluster (Split-Brain).
    *   *Correction :* Toujours mettre un nœud en mode maintenance avant mise à jour, et planifier les mises à jour de packages HA de manière synchronisée sur tous les nœuds du cluster lors d'une fenêtre de maintenance.

## Liste de vérification (Checklist)

- [ ] L'outil YaST (`yast` ou `yast2`) est utilisé en priorité pour les configurations système fondamentales.
- [ ] Les verrous de paquets critiques (`zypper locks`) sont en place pour interdire les mises à jour de version majeures non testées.
- [ ] Le statut du cluster HA (`crm status`) indique que tous les nœuds sont en ligne et que les ressources sont réparties correctement sans erreurs.
- [ ] Les dépôts de paquets SUSE officiels (Customer Center) sont connectés et valides pour recevoir les correctifs de sécurité critiques.

