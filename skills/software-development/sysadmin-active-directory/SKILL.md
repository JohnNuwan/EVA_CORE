---
name: sysadmin-active-directory
description: "Intégration Linux dans Active Directory/LDAP : SSSD, Winbind, Samba, Kerberos, Realmd, authentification centralisée, GPO, ACLs étendues et dépannage."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [ad, ldap, active-directory, sssd, samba, kerberos, realm, authentication, domain, gpo]
    related_skills: [os-linux-admin, os-debian-ubuntu-engineering, os-rhel-engineering, sysadmin-logging]
---

# Intégration Linux dans Active Directory / LDAP

## Vue d'ensemble

L'intégration Linux dans un domaine Active Directory permet l'authentification centralisée des utilisateurs, l'application de politiques (GPO), l'accès aux ressources réseau et la gestion des permissions via les groupes AD — exactement comme pour les postes Windows.

**Architecture :**
```
[Client Linux]
    │
    ├── SSSD (System Security Services Daemon) — recommandé moderne
    │      ├─── LDAP/KRB5 vers AD
    │      ├─── Cache local
    │      └─── PAM + NSS
    │
    └── Winbind (Samba) — alternative legacy
           └─── SMB/KRB5 vers AD
```

## Quand l'utiliser

- Authentifier des utilisateurs Linux avec leurs comptes AD
- Centraliser la gestion des comptes (création/suppression via AD)
- Contrôler l'accès aux fichiers avec des groupes AD
- Appliquer des GPO Linux (avec gpupdate)
- Migrer d'une authentification locale à centralisée

## 1. SSSD (Méthode Recommandée)

### Installation du Client

```bash
# Debian/Ubuntu
sudo apt install sssd-ad sssd-tools realmd adcli krb5-user

# RHEL/CentOS/Fedora
sudo dnf install sssd realmd oddjob oddjob-mkhomedir adcli krb15-workstation
```

### Joindre le Domaine

```bash
# Découvrir le domaine (DNS doit être configuré)
sudo realm discover DOMAINE.LOCAL
# Résultat :
#  DOMAINE.LOCAL
#    type: kerberos
#    realm-name: DOMAINE.LOCAL
#    domain-name: domaine.local
#    ...

# Joindre (avec admin AD)
sudo realm join --user=administrator DOMAINE.LOCAL

# Vérifier
sudo realm list
```

### Configuration SSSD

```bash
# /etc/sssd/sssd.conf (généré automatiquement par realm, mais personnalisable)
cat > /etc/sssd/sssd.conf << 'EOF'
[sssd]
domains = DOMAINE.LOCAL
config_file_version = 2
services = nss, pam

[domain/DOMAINE.LOCAL]
ad_domain = DOMAINE.LOCAL
krb5_realm = DOMAINE.LOCAL
realmd_tags = manages-system joined-with-adcli
cache_credentials = True
id_provider = ad
auth_provider = ad
access_provider = ad

# Cache homes
override_homedir = /home/%u@%d
default_shell = /bin/bash

# Optimisations réseau
ldap_id_mapping = True
ldap_idmap_range_min = 200000
ldap_idmap_range_max = 2000200000

# Sécurité : ne pas autoriser root via AD
simple_allow_groups = linux_admins, domain\ users

# Sessions PAM
pam_gssapi_services = sudo, sshd
EOF

# Permissions strictes (SSSD refuse de démarrer sinon)
sudo chmod 600 /etc/sssd/sssd.conf
sudo systemctl restart sssd
```

### Création Automatique du Home Directory

```bash
# Via oddjob-mkhomedir
sudo systemctl enable --load oddjobd

# Ou via pam auth supplémentaire
# /etc/pam.d/common-session (Debian) — ajouter :
# session required pam_mkhomedir.so skel=/etc/skel umask=0022
```

## 2. Configuration Kerberos

```bash
# /etc/krb5.conf
cat > /etc/krb5.conf << 'EOF'
[libdefaults]
    default_realm = DOMAINE.LOCAL
    dns_lookup_realm = true
    dns_lookup_kdc = true
    ticket_lifetime = 24h
    renew_lifetime = 7d
    forwardable = true
    rdns = false

[realms]
    DOMAINE.LOCAL = {
        kdc = dc01.domaine.local
        admin_server = dc01.domaine.local
    }

[domain_realm]
    .domaine.local = DOMAINE.LOCAL
    domaine.local = DOMAINE.LOCAL
EOF

# Obtenir un ticket Kerberos pour tester
kinit administrator@DOMAINE.LOCAL
klist        # Voir le ticket
```

## 3. Samba + Winbind (Alternative)

```bash
# Installation
sudo apt install samba winbind libnss-winbind libpam-winbind

# /etc/samba/smb.conf
[global]
    workgroup = DOMAINE
    realm = DOMAINE.LOCAL
    security = ads
    server string = Serveur Linux %h
    log file = /var/log/samba/%m.log
    max log size = 50
    idmap config * : backend = tdb
    idmap config * : range = 20000-99999
    idmap config DOMAINE : backend = rid
    idmap config DOMAINE : range = 10000-19999
    winbind use default domain = yes
    winbind offline logon = true
    winbind enum users = yes
    winbind enum groups = yes
    template shell = /bin/bash
    template homedir = /home/%U

# Joindre le domaine
sudo net ads join -U administrator

# Démarrer
sudo systemctl enable --now winbind smbd nmbd
```

## 4. Authentification SSH avec AD

```bash
# /etc/ssh/sshd_config
# Autoriser uniquement les groupes AD autorisés
AllowGroups domain\ users linux_admins
# ou
AllowUsers *@domaine.local

# Désactiver l'auth root SSH (toujours)
PermitRootLogin no

# PAM pour SSH
# /etc/pam.d/sshd — s'assurer que la ligne suivante est avant @include common-auth
auth sufficient pam_sss.so

# Vérifier
sudo systemctl restart sshd
```

## 5. sudo pour Groupes AD

```bash
# /etc/sudoers.d/admins
# Donner sudo à un groupe AD
%domain\ admins ALL=(ALL) ALL
%linux_admins@domaine.local ALL=(ALL) ALL

# Vérifier la syntaxe
sudo visudo -c
```

## 6. Contrôle d'Accès aux Fichiers

```bash
# Permissions POSIX étendues avec ACL
setfacl -m g:"DOMAINE\ingénieurs":rwx /var/www/projects
setfacl -m g:"domain engineers":rwx /var/www/projects   # selon config

# Les groupes AD sont visibles via getent
getent group "domain users"
getent passwd "user@domaine.local"

# Lister tous les utilisateurs AD (peut être lent)
getent passwd | grep domaine
```
```

## 7. GPO Linux (Politiques de Groupe)

Avec le client gpupdate pour Linux :

```bash
# L'extension GPO Linux est disponible sur RHEL 8+ / CentOS 8+
# Activation :
sudo dnf install adcli realmd samba samba-client
sudo grep -q "^apply_group_policy" /etc/sssd/sssd.conf || \
  echo "ad_gpo_map_interactive = +gdm-vendor" >> /etc/sssd/sssd.conf

# Appliquer les GPO manuellement (Samba)
sudo net ads gpupdate

# Simuler (dry-run)
sudo net ads gpolist
```

## 8. Diagnostic et Dépannage

```bash
#!/bin/bash
# /usr/local/bin/ad-diagnostic.sh
set -euo pipefail

echo "=== STATUT SSSD ==="
systemctl status sssd --no-pager | head -5
echo -e "\n=== CONNEXION AD ==="
sudo realm list

echo -e "\n=== KERBEROS ==="
klist -5 2>/dev/null || echo "Pas de ticket Kerberos"

echo -e "\n=== TEST AUTHENTIFICATION ==="
# Tester l'authentification d'un utilisateur AD
sudo id testuser@domaine.local 2>&1 || echo "ATTENTION: utilisateur AD non trouvé"

echo -e "\n=== CACHE SSSD ==="
sudo sss_cache -E && echo "Cache SSSD vidé"

echo -e "\n=== LOGS RÉCENTS ==="
journalctl -u sssd --since "10 min ago" --no-pager | grep -i "error\|warn\|fail" | tail -5
```

### Erreurs Fréquentes

```bash
# "Couldn't join realm: DNS resolution failed"
# → Vérifier le DNS pointe vers le DC
# /etc/resolv.conf : nameserver <IP_DC>
nslookup domaine.local

# "sssd: Failed to start up daemon"
# → Vérifier les permissions du fichier de config
sudo chmod 600 /etc/sssd/sssd.conf

# "Authentication failure: SASL(-1): generic failure"
# → Rejoindre le domaine avec un compte admin
sudo realm leave
sudo realm join -U administrator DOMAINE.LOCAL

# "id: testuser: no such user"
# → SSSD cache non chargé
sudo sss_cache -E
sudo systemctl restart sssd
getent passwd testuser@domaine.local
```

## Pièges Courants

1. **DNS mal configuré** : Le client Linux DOIT utiliser le serveur DNS du domaine AD. `systemd-resolved` peut interférer. Configurer `dns=default` dans `/etc/NetworkManager/NetworkManager.conf` ou utiliser `/etc/resolv.conf` statique.

2. **Décalage horaire > 5 minutes** : Kerberos est intolérant au décalage. Synchroniser automatiquement avec le DC : installer `chrony` ou `ntp` avec le DC comme source :
   ```bash
   # /etc/chrony/chrony.conf
   server dc01.domaine.local iburst
   ```

3. **SSSD refuse de démarrer** : SSSD refuse de démarrer si les permissions de `/etc/sssd/sssd.conf` ne sont pas 600.

4. **home directory non créé** : L'utilisateur AD se connecte mais son home n'existe pas. Installer `oddjob-mkhomedir` ou ajouter `pam_mkhomedir.so` à PAM.

5. **GPO ignorées** : Les GPO Linux ne fonctionnent qu'avec des extensions spécifiques. Vérifier `ad_gpo_map_interactive` dans sssd.conf.

## Liste de vérification (Checklist)

- [ ] DNS configuré vers le contrôleur de domaine
- [ ] Synchronisation temporelle (NTP/Chrony) active
- [ ] `realm join` réussi
- [ ] `sssd.conf` permissions 600
- [ ] Test d'authentification réussi : `ssh testuser@localhost`
- [ ] Home directory créé automatiquement (`pam_mkhomedir`)
- [ ] sudo configuré pour les groupes AD
- [ ] Kerberos fonctionnel : `kinit administrator@DOMAINE.LOCAL && klist`
- [ ] Backups des configurations (/etc/sssd, /etc/krb5.conf, /etc/samba/)
