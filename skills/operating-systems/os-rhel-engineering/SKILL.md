---
name: os-rhel-engineering
description: "Administrer et optimiser des serveurs Red Hat Enterprise Linux (RHEL), configurer les politiques SELinux, gérer les abonnements, administrer le pare-feu firewalld et déployer des configurations automatisées."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux]
metadata:
  tags: [rhel, redhat, selinux, dnf, firewalld, ansible, system-ops]
  helios:
    related_skills: [os-linux-admin, os-suse-engineering]
---

# Ingénierie Red Hat Enterprise Linux (RHEL)

## Vue d'ensemble

Cette compétence guide l'administration et l'ingénierie système de la distribution commerciale **Red Hat Enterprise Linux (RHEL)** et de ses dérivés (Rocky Linux, AlmaLinux). RHEL est largement privilégié en environnement industriel critique pour sa stabilité et son cycle de vie. Sa gestion exige la maîtrise de technologies spécifiques de sécurité renforcée (politiques **SELinux**), la configuration du pare-feu applicatif **firewalld**, le cycle d'enregistrement des serveurs (subscription-manager) et la gestion des paquets via **DNF/Yum**.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Gérer l'enregistrement et les dépôts de paquets sous RHEL (`subscription-manager`).
- Configurer ou dépanner des blocages de sécurité causés par **SELinux** (Security-Enhanced Linux).
- Ouvrir ou fermer des ports réseau de manière persistante avec **firewalld** (notamment les zones de confiance).
- Automatiser le déploiement de rôles de configuration système sur RHEL (RHEL System Roles / Ansible).
- Analyser des rapports d'audit de sécurité ou de conformité (SCAP/OpenSCAP) sous RHEL.

## Dépannage et Configuration SELinux

SELinux applique un contrôle d'accès obligatoire (MAC) au niveau du noyau. Les fichiers, processus et ports ont tous des contextes de sécurité spécifiques (Security Context).

### 1. Diagnostiquer un blocage SELinux
Si un service (ex: Apache sur le port 8080) ne démarre pas malgré des droits fichiers OK (`chmod 777`) :
```bash
# Vérifier l'état actuel de SELinux (Enforcing / Permissive / Disabled)
sestatus
# Rechercher les violations récentes dans les logs d'audit
sudo ausearch -m AVC -ts recent
# Traduire les erreurs d'audit en explications humaines
sudo sealert -a /var/log/audit/audit.log
```

### 2. Corriger un contexte de fichier
Si un répertoire personnalisé (ex: `/srv/data`) doit être lu par un service spécifique :
```bash
# Lister le contexte de sécurité d'un dossier (colonne t_type)
ls -Z /srv/data
# Définir de manière persistante le bon type (ex: httpd_sys_content_t)
sudo semanage fcontext -a -t httpd_sys_content_t "/srv/data(/.*)?"
# Appliquer le nouveau contexte physiquement sur le disque
sudo restorecon -R -v /srv/data
```

## Configuration du Pare-feu avec firewalld

```bash
# Ouvrir le port 502 (Modbus-TCP) de manière persistante dans la zone par défaut
sudo firewall-cmd --add-port=502/tcp --permanent
# Recharger la configuration pour appliquer le changement
sudo firewall-cmd --reload
# Lister la configuration active pour vérification
sudo firewall-cmd --list-all
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Désactiver SELinux en production par facilité :**
   * *Erreur :* Passer SELinux à `disabled` dans le fichier `/etc/selinux/config` dès qu'un service rencontre une erreur de permission. Cela annule une barrière de sécurité noyau majeure et rend le serveur non conforme aux audits de sécurité.
   * *Correction :* Passer SELinux en mode `permissive` temporairement pour collecter les logs (`setenforce 0`), identifier le problème (contexte de fichier, port non autorisé ou type de processus), appliquer la correction de contexte, puis repasser en mode strict (`setenforce 1`).

2. **Perdre l'accès réseau lors de l'activation du pare-feu :**
   * *Erreur :* Activer firewalld à distance (SSH) sans avoir préalablement ajouté le service SSH à la zone active, provoquant une coupure de connexion définitive.
   * *Correction :* Toujours exécuter `sudo firewall-cmd --add-service=ssh --permanent` avant de démarrer ou d'activer le service firewalld.

## Liste de vérification (Checklist)

- [ ] L'état de SELinux est configuré sur `Enforcing` en production.
- [ ] Les exceptions SELinux sont configurées via des types de fichiers ou de ports précis et non par des règles trop larges.
- [ ] Le pare-feu `firewalld` est actif et configuré avec les seuls ports nécessaires ouverts.
- [ ] L'enregistrement système et les abonnements RHEL (`subscription-manager status`) sont valides pour recevoir les mises à jour de sécurité.

