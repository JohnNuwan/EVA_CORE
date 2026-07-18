---
name: os-linux-admin
description: "Administrer les systèmes Linux, gérer les utilisateurs/permissions, configurer systemd (services, timers), administrer les volumes de stockage avec LVM et concevoir des scripts d'automatisation Bash avancés."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux]
metadata:
  helios:
    tags: [linux, bash, systemd, lvm, administration, scripting, sysctl, storage]
    related_skills: [os-rhel-engineering, os-debian-ubuntu-engineering]
---

# Administration Linux Générique & Automatisation (Bash / systemd)

## Vue d'ensemble

Cette compétence guide l'administration système de serveurs Linux (indépendamment de la distribution). Elle couvre la configuration fine du gestionnaire de volumes logiques **LVM** pour l'extension dynamique de stockage, la création de services d'arrière-plan et de tâches planifiées via **systemd** (units et timers), la gestion sécurisée des droits d'accès (propriétaires, groupes, ACLs), et le développement de scripts d'automatisation robustes en langage **Bash**.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Écrire un script shell Bash pour automatiser des sauvegardes, surveiller des ressources ou analyser des logs (avec `grep`, `awk`, `sed`).
- Configurer un service systemd pour lancer automatiquement un script ou un binaire au démarrage du serveur.
- Créer ou étendre des partitions et systèmes de fichiers avec LVM (Logical Volume Manager).
- Diagnostiquer des problèmes de droits ou d'accès fichier (`chmod`, `chown`, `getfacl`).
- Configurer des paramètres réseau ou système persistants via `sysctl`.

## Exemple de Script systemd (Unit Service et Timer)

### 1. Le service : `/etc/systemd/system/backup.service`
Définit comment le script de sauvegarde doit être exécuté :

```ini
[Unit]
Description=Service de sauvegarde automatique Actemium
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup_script.sh
User=root
Group=root

[Install]
WantedBy=multi-user.target
```

### 2. Le timer (Alternative moderne aux tâches cron) : `/etc/systemd/system/backup.timer`
Planifie le déclenchement du service toutes les nuits à 2 heures du matin :

```ini
[Unit]
Description=Planificateur de la sauvegarde automatique Actemium

[Timer]
OnCalendar=*-*-* 02:00:00
Persistent=true

[Install]
WantedBy=timers.target
```
*Commandes pour activer* :
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup.timer
```

## Manipulation LVM de Base (Extension de volume logique)

```bash
# 1. Scanner les volumes physiques et groupes de volumes existants
sudo vgdisplay
# 2. Créer un volume physique sur un nouveau disque (ex: /dev/sdb)
sudo pvcreate /dev/sdb
# 3. Étendre le groupe de volumes "vg_system"
sudo vgextend vg_system /dev/sdb
# 4. Étendre le volume logique "lv_data" de 50 Go
sudo lvextend -L +50G /dev/vg_system/lv_data
# 5. Étendre à chaud le système de fichiers (ex: ext4)
sudo resize2fs /dev/vg_system/lv_data
```

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Scripts Bash sensibles aux espaces dans les variables :**
   * *Erreur :* Écrire `if [ $var == "test" ]` sans guillemets. Si `$var` est vide ou contient un espace, le script plante avec une erreur de syntaxe (`unary operator expected`).
   * *Correction :* Toujours entourer les variables de guillemets doubles dans les expressions de comparaison : `if [ "$var" = "test" ]`. De plus, commencer tous les scripts critiques par `set -euo pipefail` pour que le script s'arrête à la première erreur.

2. **Épuisement des Inodes sur le système de fichiers :**
   * *Erreur :* Le disque affiche de l'espace disponible (ex: 50% libre), mais les applications renvoient une erreur "No space left on device" car un trop grand nombre de petits fichiers temporaires a été créé.
   * *Correction :* Vérifier l'utilisation des inodes avec `df -i`. Nettoyer régulièrement les fichiers de session ou de cache obsolètes.

## Liste de vérification (Checklist)

- [ ] Les scripts Bash contiennent `set -euo pipefail` en tête pour stopper immédiatement l'exécution en cas d'erreur.
- [ ] Toutes les variables de chemin d'accès dans les scripts shell sont protégées par des guillemets doubles.
- [ ] Les services systemd personnalisés ont des directives `After=` appropriées pour s'assurer que le réseau ou les bases de données sont démarrés avant le script.
- [ ] Les volumes LVM disposent d'un espace libre non alloué dans le Volume Group (VG) pour permettre des extensions rapides en cas d'alerte disque.
- [ ] Les tâches planifiées systemd (timers) sont vérifiées avec la commande `systemctl list-timers`.

