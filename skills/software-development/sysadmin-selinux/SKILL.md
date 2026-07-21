---
name: sysadmin-selinux
description: "SELinux : contextes, booleans, politiques personnalisées, audit2allow, semanage, enforcing/permissive, dépannage des denials et intégration avec services."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [selinux, security, mandatory-access-control, policy, enforcement, audit, centos, rhel, fedora]
    related_skills: [os-rhel-engineering, os-linux-admin, sysadmin-logging, sysadmin-kernel-tuning]
---

# SELinux (Security-Enhanced Linux)

## Vue d'ensemble

SELinux est un module de sécurité du noyau Linux implémentant le Mandatory Access Control (MAC). Contrairement aux permissions traditionnelles (DAC - Discretionary Access Control) qui permettent à un utilisateur de modifier les droits de ses fichiers, SELinux applique une politique globale définie par l'administrateur — même root est limité.

**Concepts fondamentaux :**
- **Contexte SELinux** : étiquette (label) attachée à chaque fichier, processus, port, etc.
- **Politique** : ensemble de règles définissant ce qui est autorisé
- **Sujet** : processus (ex: `httpd_t`)
- **Objet** : ressource (ex: fichier `httpd_sys_content_t`)
- **AVC** : décision de contrôle d'accès (Allow/Deny)

## Modes SELinux

| Mode | Comportement | Usage |
|------|-------------|-------|
| **Enforcing** | Applique la politique, bloque les accès non autorisés | Production |
| **Permissive** | Log les violations sans bloquer | Débogage, transition |
| **Disabled** | SELinux désactivé complètement | Non recommandé |

```bash
# Voir le mode actuel
getenforce               # Enforcing / Permissive / Disabled
sestatus                 # Informations détaillées

# Basculer en mode permissive (pour déboguer)
sudo setenforce 0        # Permissive (jusqu'au prochain reboot)
sudo setenforce 1        # Enforcing

# Changer le mode définitif dans /etc/selinux/config
sudo sed -i 's/SELINUX=.*/SELINUX=enforcing/' /etc/selinux/config
```

## Quand l'utiliser

- Un service refuse de démarrer ou d'accéder à ses fichiers → denial SELinux probable
- Configurer un service sur un port non standard (nginx sur 8080, SSH sur 2222)
- Déployer une application avec des chemins de fichiers personnalisés
- Durcir un serveur en production
- Diagnostiquer des "Permission denied" alors que les permissions DAC sont correctes

## 1. Contextes SELinux

Chaque fichier, processus, port et répertoire possède un contexte :

```bash
# Afficher le contexte d'un fichier
ls -Z /var/www/html/index.html
# Résultat : unconfined_u:object_r:httpd_sys_content_t:s0
#              ^user      ^role    ^type              ^level

# Types courants :
# httpd_sys_content_t   — contenu web statique (lecture par httpd)
# httpd_sys_rw_content_t — contenu web rw (uploads, CMS)
# httpd_log_t           — logs Apache
# var_log_t             — logs système
# sshd_exec_t           — binaire SSH
# etc_t                 — fichiers de configuration
```

### Restaurer le Contexte

```bash
# Restaurer le contexte par défaut pour un fichier/dossier
sudo restorecon -v /var/www/html/index.html
sudo restorecon -Rv /var/www/           # récursif

# Appliquer la politique par défaut d'un package
sudo restorecon -Rv /etc/
```

### Modifier un Contexte

```bash
# Si un fichier est dans le mauvais contexte (ex: /data/custom/nginx)
sudo semanage fcontext -a -t httpd_sys_content_t "/data/custom/nginx(/.*)?"
sudo restorecon -Rv /data/custom/nginx/

# Voir les contextes définis
sudo semanage fcontext -l | grep httpd
```

## 2. Booleans SELinux

Les booleans permettent d'activer/désactiver des fonctionnalités sans réécrire la politique :

```bash
# Lister les booleans
getsebool -a
semanage boolean -l | head -20

# Exemples courants
getsebool httpd_can_network_connect     # Apache peut-il faire des connexions réseau ?
getsebool httpd_enable_homedirs         # Apache peut-il accéder aux home dirs ?

# Modifier un boolean
sudo setsebool -P httpd_can_network_connect on   # -P = persistant
sudo setsebool -P httpd_enable_homedirs on
sudo setsebool -P samba_export_all_rw on
```

### Booleans Fréquents

```bash
# Apache/Nginx
httpd_can_network_connect        # connexions réseau sortantes (proxy, API)
httpd_can_network_connect_db     # connexion aux bases de données
httpd_can_sendmail               # envoi d'emails
httpd_enable_homedirs            # accès aux home directories

# FTP
ftpd_full_access                 # accès complet FTP
allow_ftpd_full_access           # lecture/écriture FTP

# Samba
samba_export_all_rw              # export Samba read-write

# PostgreSQL
pgsql_use_nfs                    # BDD sur NFS

# SSH
ssh_chroot_rw_homes              # chroot SSH
```

## 3. Dépannage des Denials (AVC)

### Avec auditd

```bash
# Voir les denials en temps réel
sudo tail -f /var/log/audit/audit.log | grep AVC

# Rechercher les denials récents
sudo ausearch -m avc --start today

# Avec interprétation des types
sudo ausearch -m avc --start today -i    # -i = interpréter les types
```

### Avec journald (si auditd pas installé)

```bash
journalctl -k | grep -i "denied\|avc\|selinux"

# Voir les messages kernel liés à SELinux
dmesg | grep -i selinux
```

### Audit2allow — Générer une Politique Personnalisée

L'outil le plus important pour résoudre les denials SELinux :

```bash
# 1. Passer en permissive pour collecter les violations
sudo setenforce 0

# 2. Reproduire le problème (lancer le service, accéder à l'URL, etc.)

# 3. Revenir en enforcing
sudo setenforce 1

# 4. Générer et appliquer la politique
sudo grep "denied" /var/log/audit/audit.log | audit2allow -M monapp_policy
sudo semodule -i monapp_policy.pp

# Alternative : depuis journald
journalctl -k | grep -i denied | audit2allow -M monapp_policy
sudo semodule -i monapp_policy.pp
```

### Audit2why — Expliquer les Denials

```bash
sudo ausearch -m avc --start today | audit2why
# Donne la raison du refus et les solutions possibles
```

## 4. Ports — Définir un Contexte pour un Port Non Standard

```bash
# Si httpd doit écouter sur le port 8080
sudo semanage port -a -t http_port_t -p tcp 8080

# Voir les ports définis
sudo semanage port -l | grep http

# Exemple SSH sur port 2222
sudo semanage port -a -t ssh_port_t -p tcp 2222
```

## 5. Politiques Personnalisées (Avancé)

```bash
# Créer une politique .te (Type Enforcement) manuellement
# /tmp/myapp.te
cat > myapp.te << 'EOF'
policy_module(myapp, 1.0.0)

require {
    type httpd_t;
    type httpd_sys_content_t;
    class tcp_socket connect;
    class file { read write };
}

# Autoriser httpd à écrire dans /var/myapp
allow httpd_t myapp_data_t:file { read write create unlink };
EOF

# Compiler
sudo checkmodule -M -m -o myapp.mod myapp.te
sudo semodule_package -o myapp.pp -m myapp.mod
sudo semodule -i myapp.pp
```

## 6. SELinux et Conteneurs (Docker, Podman)

```bash
# Par défaut, Docker s'exécute en mode permissif SELinux
# Vérifier :
docker info | grep -i selinux

# Activer SELinux pour Docker :
# /etc/docker/daemon.json
{
  "selinux-enabled": true
}

# Podman (natif SELinux)
podman run --security-opt label=type:svirt_sandbox_t -d nginx
```

## 7. Procédure de Diagnostic Rapide

```bash
#!/bin/bash
# /usr/local/bin/selinux-diagnostic.sh
set -euo pipefail

echo "=== MODE SELINUX ==="
getenforce

echo -e "\n=== 10 DERNIERS DENIALS ==="
sudo ausearch -m avc --start today -i --just-one 2>/dev/null | tail -10 || \
  journalctl -k --no-pager | grep -i "denied" | tail -10

echo -e "\n=== SOLUTION RAPIDE ==="
sudo ausearch -m avc --start today 2>/dev/null | audit2allow -a || \
  echo "Aucun denial trouvé"

echo -e "\n=== BOOLEANS COURANTS ==="
getsebool httpd_can_network_connect httpd_enable_homedirs httpd_can_sendmail 2>/dev/null || true
```

## Pièges Courants

1. **Désactiver SELinux au lieu de le configurer** : `setenforce 0` en permanence supprime la couche de sécurité MAC. Toujours utiliser `audit2allow` pour créer une politique.

2. **SELinux disabled vs permissive** : Disabled signifie que les labels ne sont même pas appliqués au boot. Si vous passez de disabled à enforcing, tous les contextes système doivent être relabelés :
   ```bash
   sudo fixfiles onboot
   sudo reboot
   # Le relabeling prend du temps selon la taille du système
   ```

3. **Contextes perdus après mv/cp** : `cp` préserve le contexte, `mv` aussi (car le fichier ne change pas). Mais une archive tar extraite aura des contextes inconnus → toujours faire `restorecon -Rv` après extraction.

4. **Oublier le flag `-P`** sur `setsebool` : Sans `-P`, la modification est perdue au reboot.

5. **auditd pas installé** : SELinux envoie les AVC à auditd. Si auditd n'est pas en service, les logs sont dans `dmesg` / `journalctl -k` mais pas dans `ausearch`.

## Liste de vérification (Checklist)

- [ ] SELinux en mode Enforcing sur les serveurs de production
- [ ] Audit2allow exécuté pour chaque nouveau service
- [ ] Booleans configurés (avec `-P`) pour les services nécessitant des accès réseau/FS
- [ ] Contextes restaurés après extraction d'archives (`restorecon -Rv`)
- [ ] Ports non standards déclarés avec `semanage port`
- [ ] Politiques personnalisées stockées dans `/etc/selinux/policies/`
- [ ] Audit des denials périodique (cron hebdo `audit2allow -a`)
- [ ] Documentation des politiques SELinux personnalisées
