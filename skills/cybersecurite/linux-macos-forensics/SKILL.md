---
name: linux-macos-forensics
description: Guide complet de forensic Linux et macOS — artefact analysis (auth.log, journald, bash_history, crontab), MAC times, acquisition RAM/disk, HFS+/APFS, Unified Log, Keychain, FileVault, TCC, SIP, et analyse de persistence
tags: [forensics, linux, macos, artifacts, journald, apfs, unified-log, keychain, persistence]
version: 1.0
---

# Forensic Linux et macOS — Guide Complet

Guide exhaustif d'investigation numérique sur systèmes Linux et macOS : artefacts, acquisition, analyse de logs, persistence, et chaîne de custody.

---

## 1. Linux Forensics — Artefacts Système

### Structure des Logs Linux

```txt
/var/log/
├── auth.log*              # Authentifications SSH, sudo, login
├── syslog*                # Log système général
├── kern.log*              # Noyau / Kernel
├── daemon.log*            # Services démons
├── debug*                 # Debug messages
├── dpkg.log*              # Paquets installés (Debian/Ubuntu)
├── alternatives.log*      # Alternatives update
├── bootstrap.log          # Boot messages
├── faillog*               # Échecs login
├── lastlog*               # Dernière connexion de chaque user
├── wtmp*                  # Historique des sessions
├── btmp*                  # Tentatives échouées
├── apt/                   # Logs APT
│   ├── history.log        # Historique des opérations APT
│   └── term.log           # Sorties terminal APT
├── apache2/               # Apache HTTPD
│   ├── access.log         # Requêtes HTTP (IP, URL, UA)
│   └── error.log          # Erreurs Apache
├── nginx/                 # Nginx (même pattern)
├── mysql/                 # MySQL/MariaDB
│   ├── error.log
│   └── slow.log
├── postgresql/            # PostgreSQL
├── fail2ban.log           # Fail2ban blocages
├── ufw.log                # UFW firewall logs
├── cups/                  # Impression
├── samba/                 # Samba
├── cron.log*              # Cron
├── mail.log*              # Mail (postfix, sendmail)
├── unattended-upgrades/   # Mises à jour auto
└── audit/                 # AuditD logs
    └── audit.log          # SELinux/apparmor messages
```

### Acquisition des Logs

```bash
# Copier tous les logs
sudo tar czf /evidence/linux_logs.tar.gz /var/log/

# Logs compressés (logrotate)
ls /var/log/*.gz          # Logs anciens
zcat /var/log/auth.log.2.gz | grep "Accepted"   # Lire un .gz

# Avec préservation des métadonnées
rsync -a /var/log/ /evidence/logs/

# Logs volatils (RAM) — par Volatility
vol -f memory.raw linux.bash        # Bash history depuis RAM
vol -f memory.raw linux.dmesg       # Kernel ring buffer
vol -f memory.raw linux.psaux       # Arguments des processus
```

### Authentification (auth.log)

```bash
# Connexions SSH réussies
grep "Accepted" /var/log/auth.log | awk '{print $1, $2, $3, $9, $11, $13}'

# Tentatives échouées (brute force)
grep "Failed password" /var/log/auth.log | awk '{print $1, $2, $3, $9, $11, $13}'

# sudo exécutions
grep "sudo:" /var/log/auth.log | grep "COMMAND"

# Erreurs PAM (authentification modules)
grep "pam_unix" /var/log/auth.log | grep "authentication failure"

# Création/suppression de comptes
grep -E "useradd|userdel|groupadd|passwd" /var/log/auth.log

# Connexions physiques (terminal)
grep "login:" /var/log/auth.log

# Journalisation en temps réel
tail -f /var/log/auth.log

# Afficher les IPs les plus fréquentes dans les tentatives échouées
grep "Failed password" /var/log/auth.log | grep -oP 'from \K[0-9.]+' | sort | uniq -c | sort -rn | head -10
```

### Systemd Journal (journalctl)

```bash
# Exporter le journal complet
journalctl --no-pager > /evidence/journal.txt
journalctl -o json-pretty > /evidence/journal.json

# Exporter le journal binaire (pour analyse forensique)
sudo journalctl --flush   # Synchroniser en RAM → disque
sudo cp -r /var/log/journal/ /evidence/journal_binary/

# Filtres temporels
journalctl --since "2024-07-20 00:00:00" --until "2024-07-22 23:59:59"
journalctl --since "-7 days"
journalctl --since "-1h"

# Filtres par service
journalctl -u sshd.service                           # SSH
journalctl -u nginx.service                          # Nginx
journalctl -u docker.service                         # Docker
journalctl -u systemd-networkd.service               # Réseau
journalctl _SYSTEMD_UNIT=cron.service                # Cron

# Filtres par PID / processus
journalctl _PID=1234                                 # Process spécifique
journalctl _COMM=sshd                                # Commande
journalctl _UID=0                                    # Root seulement

# Priorité
journalctl -p err                                    # Erreurs seulement
journalctl -p warning                                # Avertissements
journalctl -p crit                                   # Critique

# Analyse pattern
journalctl -u sshd.service | grep -E "Accepted|Failed"
journalctl -u sshd.service --output=json | grep -E "Invalid user"
```

### Authentification Locale

```bash
# Dernières connexions
last -100                   # /var/log/wtmp
lastb -100                  # /var/log/btmp (failed logins)

# Utilisateurs connectés
who
w

# Dernière connexion de chaque utilisateur
lastlog

# Historique des sessions utilisateur
last -f /var/log/wtmp -100

# Sessions SSH actuellement actives (PID, depuis quand)
ss -tnp | grep :22
lsof -i :22
```

### Analyse des Historiques

```bash
# .bash_history — Commandes exécutées
cat ~/.bash_history

# .bash_history de tous les utilisateurs
for user in /home/*/; do
    echo "=== $user ==="
    cat "${user}.bash_history" 2>/dev/null
done
cat /root/.bash_history 2>/dev/null

# .zsh_history (zsh)
cat ~/.zsh_history

# .lesshst — less history
cat ~/.lesshst

# .mysql_history, .psql_history, .python_history
cat ~/.mysql_history
cat ~/.pgsql_history

# Vim history
cat ~/.viminfo | grep -E "^|" | head -100

# Dernières commandes (bash)
history 100

# ATTENTION : .bash_history n'est écrit qu'à la fermeture de session
# Si l'utilisateur est encore connecté → plus récent dans la RAM
# → Volatility linux.bash

# Commandes effacées ?
# Vérifier le fichier .bash_history en hex :
xxd ~/.bash_history | head
# Si rempli de 0x00 → effacement volontaire
# Si lignes tronquées → édition manuelle du fichier
```

### Analyse de Persistance Linux

```bash
# Crontab (tâches planifiées)
cat /etc/crontab
ls -la /etc/cron.d/
ls -la /etc/cron.daily/
ls -la /etc/cron.hourly/
ls -la /etc/cron.weekly/
ls -la /etc/cron.monthly/
crontab -l -u root          # Crontab root
for user in $(cut -f1 -d: /etc/passwd); do
    crontab -u "$user" -l 2>/dev/null | grep -v "no crontab"
done

# Systemd services (modern Linux)
ls -la /etc/systemd/system/          # Services activés
ls -la /usr/lib/systemd/system/      # Services installés
systemctl list-unit-files --type=service
systemctl list-units --type=service --state=enabled

# Services masqués
systemctl list-unit-files | grep masked

# .service files suspects
find /etc/systemd/system/ -name "*.service" -exec cat {} \;

# Init.d (legacy)
ls -la /etc/init.d/
ls -la /etc/rc*.d/

# XDG autostart (GUI)
ls -la /etc/xdg/autostart/
ls -la ~/.config/autostart/

# .bashrc, .bash_profile, .profile
cat ~/.bashrc
cat ~/.bash_profile

# rc.local
cat /etc/rc.local

# Module kernel
lsmod            # Modules kernel chargés
ls -la /lib/modules/$(uname -r)/
cat /etc/modules  # Modules auto-load

# Modprobe config
cat /etc/modprobe.d/*.conf

# LD_PRELOAD / LD_LIBRARY_PATH
# Vérifier ld.so.preload
cat /etc/ld.so.preload 2>/dev/null
cat /etc/ld.so.conf
ldconfig -p
```

---

## 2. Linux Forensics — Acquisition Disque et RAM

### Acquisition Disque

```bash
# Avec write-blocker hardware
# Identique à Windows : dd, ewfacquire, etc.

# Acquisition d'une partition montée (à éviter si possible)
# Sinon, utiliser dd avec lecture seule
sudo mount -o ro /dev/sda1 /mnt/evidence/
sudo dd if=/dev/sda1 of=/evidence/partition.dd bs=4M

# LVM (Logical Volume Manager)
sudo lvdisplay
sudo lvs
sudo dd if=/dev/vg01/lv_root of=/evidence/lvm_root.dd bs=4M

# RAID logiciel
cat /proc/mdstat
sudo dd if=/dev/md0 of=/evidence/raid_image.dd bs=4M
```

### Dump de la RAM Linux

```bash
# LiME (recommandé)
sudo insmod lime.ko "path=/evidence/memory.lime format=lime"

# fmem
sudo insmod fmem.ko
sudo dd if=/dev/fmem of=/evidence/memory.raw bs=1M status=progress

# AVML (Microsoft, sans module kernel)
sudo avml /evidence/memory.raw
```

### Analyse du Disque

```bash
# Analyse des métadonnées système
# Liste de fichiers avec timestamps
find /evidence/mount/ -type f -printf "%T@ %Tc %p\n" | sort -rn | head -100

# Fichiers modifiés récemment
find /evidence/mount/ -mmin -60 -exec ls -la {} \;
find /evidence/mount/ -newer /tmp/reference.txt -ls

# Fichiers setuid / setgid
find /evidence/mount/ -perm -4000 -o -perm -2000 -ls

# Fichiers cachés
find /evidence/mount/ -name ".*" -type f

# SUID root (privesc potentielle)
find /evidence/mount/ -user root -perm -4000 -exec ls -la {} \;
```

---

## 3. Linux Forensics — Artefacts Réseau

```bash
# Interfaces réseau
cat /var/log/syslog | grep -E "eth0|wlan0|enp" | tail -20

# Connexions réseau actives (depuis RAM)
vol -f memory.raw linux.netstat
vol -f memory.raw linux.arp

# Firewall iptables
iptables-save > /evidence/iptables.txt
ip6tables-save > /evidence/iptables6.txt

# Firewall nftables
nft list ruleset > /evidence/nftables.txt

# Fail2ban status
fail2ban-client status
fail2ban-client status sshd

# DNS resolv
cat /etc/resolv.conf
cat /etc/hosts

# Hostname
cat /etc/hostname
cat /etc/hosts
```

---

## 4. Linux Forensics — Analyse des Binaries

```bash
# Dépendances vulnérables
dpkg -l | grep -E "openssl|bash|sudo|kernel"  # Debian/Ubuntu
rpm -qa | grep -E "openssl|bash|sudo|kernel"   # RedHat/Fedora

# Paquets installés (date)
grep " install " /var/log/dpkg.log | tail -50

# Fichiers récemment modifiés dans /usr/bin, /usr/sbin
find /usr/bin/ -mmin -1440 -ls       # Dernières 24h
find /usr/sbin/ -mtime -7 -ls        # 7 jours

# Processus suspects (depuis RAM)
vol -f memory.raw linux.psaux
vol -f memory.raw linux.check_modules

# Kernel modules suspects
lsmod | grep -vE "^(Module|$)"
# Modules inconnus ? → rootkit possible
```

---

## 5. macOS Forensics — Artefacts Système

### Unified Log (Logs macOS)

```bash
# Unified log = système de logs binaire (similaire à journald)
# Commande : log

# Tout le log système depuis le début
log show --last boot --output /evidence/macos_logs.log

# Logs depuis une date
log show --start "2024-07-20 00:00:00" --end "2024-07-22 23:59:59"

# Filtre par processus
log show --process Terminal
log show --process sshd-keygen-wrapper

# Filtre par niveau
log show --level debug
log show --level error
log show --level fault   # Crash

# Filtre par prédicat (comme Spotlight)
log show --predicate 'eventMessage contains "sudo"'
log show --predicate 'eventMessage contains "password"'
log show --predicate 'process == "sshd"'

# Stream en temps réel
log stream --level debug --predicate 'process == "sshd"'

# Exporter les logs compressés
log collect --output /evidence/system_logs.logarchive
# Format .logarchive = vue dans Console.app sur Mac
```

### Analyse des Préférences

```bash
# User defaults (équivalent registre)
# Stockés dans ~/Library/Preferences/ (fichiers .plist)

# Dernières connexions SSH
defaults read /var/db/dslocal/nodes/Default/users/$USER.plist

# WiFi networks connus
security find-generic-password -wa "AirPort"
# ou via les fichiers :
cat /Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist
plutil -p /Library/Preferences/SystemConfiguration/com.apple.airport.preferences.plist

# Historique Spotlight
# ~/Library/Application Support/com.apple.spotlight/.../
```

### Analyse du Keychain (Trousseau)

```bash
# Keychain = stockage de mots de passe macOS
# Système : /Library/Keychains/System.keychain
# Utilisateur : ~/Library/Keychains/login.keychain

# Lister les éléments du keychain
security list-keychains
security dump-keychain /Users/$USER/Library/Keychains/login.keychain

# Dump complet (nécessite le mot de passe)
security dump-keychain -r /Library/Keychains/System.keychain 2>/dev/null

# Extraire des mots de passe spécifiques
security find-internet-password -s "google.com" -w

# WiFi passwords
security find-generic-password -wa "Wi-Fi"

# iCloud tokens
security find-generic-password -s "iCloud"

# ATTENTION : Keychain peut être verrouillé
# Si l'utilisateur était déconnecté → keychain verrouillé = inaccessible
```

---

## 6. macOS Forensics — Système de Fichiers

### APFS (Apple File System)

```bash
# Analyse APFS
diskutil apfs list
diskutil apfs listSnapshots /

# Snapshots (Time Machine-like)
diskutil apfs listSnapshots disk1s1
# Chaque snapshot = point de restauration dans le temps

# Monter un snapshot
diskutil apfs mountSnapshot -uuid <uuid> /Volumes/Snapshot

# Analyser les fichiers
# APFS supporte les clones et les snapshots COW (Copy-on-Write)
# Un fichier peut exister dans plusieurs snapshots sans doublon

# Outils CLI :
# - apfs-fuse (Linux) : monter APFS sur Linux
# - apfsck : vérification APFS
# - python apfs library
```

### Analyse du Volume

```bash
# Lister les fichiers volumineux
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# Recherche de fichiers cachés dans /Applications
find /Applications -name "*.dmg" -type f
find /Applications -name "*.app" -exec ls -la {} \;

# Fichiers modifiés récemment
find / -mtime -1 -ls 2>/dev/null | head -100

# Dérive du système (dyld)
ls -la /usr/lib/dyld/
# Sur macOS, les bibliothèques partagées sont gérées par dyld
# Les dylib malveillants peuvent être chargés via DYLD_INSERT_LIBRARIES
```

### TCC (Transparency, Consent, and Control)

```bash
# Base de données des permissions TCC
# ~/Library/Application Support/com.apple.TCC/TCC.db

# Analyser les accès accordés
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "
SELECT service, client, auth_value, last_modified
FROM access
ORDER BY last_modified DESC;
"

# Permissions suspects :
# - kTCCServiceCamera : accès caméra (espionnage)
# - kTCCServiceMicrophone : accès micro
# - kTCCServiceLiverService : accès Fichiers (exfiltration)
# - kTCCServiceAccessibility : contrôle du système (keylogger)

# Sur les versions récentes (Ventura+), TCC est renforcé
```

---

## 7. macOS Forensics — Persistance

### LaunchDaemons / LaunchAgents

```bash
# LaunchDaemons (système, au boot)
ls -la /Library/LaunchDaemons/
ls -la /System/Library/LaunchDaemons/

# LaunchAgents (utilisateur, au login)
ls -la /Library/LaunchAgents/
ls -la ~/Library/LaunchAgents/
ls -la /System/Library/LaunchAgents/

# Vérifier les plists suspects
for plist in /Library/LaunchDaemons/*.plist; do
    echo "=== $plist ==="
    plutil -p "$plist" 2>/dev/null | grep -E "ProgramArguments|RunAtLoad|KeepAlive"
done

# Exemple plist malveillant :
# <?xml version="1.0" encoding="UTF-8"?>
# <plist version="1.0">
# <dict>
#     <key>Label</key>
#     <string>com.apple.softwareupdate</string>  <-- Masquage
#     <key>ProgramArguments</key>
#     <array>
#         <string>/tmp/malware</string>           <-- Script malveillant
#     </array>
#     <key>RunAtLoad</key>
#     <true/>
# </dict>
# </plist>
```

### Cron / At

```bash
# Cron jobs
crontab -l
for user in $(dscl . list /Users | grep -v '^_'); do
    crontab -u "$user" -l 2>/dev/null | grep -v "no crontab"
done
ls -la /usr/lib/cron/tabs/  # Fichiers cron

# At jobs
at -l
```

### Login Items

```bash
# Applications au login
# ~/Library/Application Support/com.apple.backgroundtaskmanagement/
# Analyse via AppleScript :

osascript -e 'tell application "System Events" to get the name of every login item'
```

### Kernel Extensions (kext)

```bash
# Kernel extensions chargées
kextstat | grep -v com.apple

# Kernel extensions installées
ls -la /Library/Extensions/
ls -la /System/Library/Extensions/

# Vérifier les kext suspects :
# - Non signées
# - Liées à des C2 connus
# - Noms ressemblant à Apple

# SIP protège les extensions système
# Les kext malveillants nécessitent SIP désactivé ou un exploit
```

---

## 8. macOS Forensics — Gatekeeper / XProtect

```bash
# Gatekeeper logs
log show --predicate 'subsystem == "com.apple.security"'

# XProtect (antivirus intégré)
sqlite3 /Library/Apple/System/Library/CoreServices/XProtect.bundle/Contents/Resources/XProtect.plist
# Voir les signatures de malwares connus

# Notarization checks
# Vérifier si une app est notarisée
spctl -a -t exec -vv /Applications/App.app

# Quarantine checks
xattr -l /Applications/App.app
# com.apple.quarantine = date de téléchargement, browser, URL
# Résultat : 0081;64d1f8e8;Google Chrome;3B2C5D1E-...;https://malware.com/app.dmg
```

---

## 9. macOS Forensics — FileVault (Chiffrement)

```bash
# Vérifier si FileVault est activé
fdesetup status
# FileVault est On.
# ou
# FileVault is Off.

# Récupération de clé FileVault
# Si on a le mot de passe administrateur :
fdesetup haspersonalrecoverykey
fdesetup showrecoverykey  # Necessite auth

# Sans mot de passe :
# - Le volume est chiffré, impossible à lire
# - Sauf si le volume est déverrouillé (utilisateur connecté)
# - ou avec PRK (Personal Recovery Key) stockée chez Apple
# - Attaque DMA possible sur Mac Intel (pas Apple Silicon)
```

---

## 10. Linux Forensics — Analyse de Conteneurs Docker

```bash
# Docker forensics — artefacts locaux
ls -la /var/lib/docker/
ls /var/lib/docker/containers/   # Chaque conteneur = dossier

# Logs d'un conteneur
docker logs container_id > container.log

# Images docker
docker images -a
docker history image_name:tag   # Historique des layers

# Inspecter un conteneur
docker inspect container_id | jq '.[0].Mounts'    # Volumes montés
docker inspect container_id | jq '.[0].Config'    # Commande, env vars

# Docker compose
find / -name "docker-compose.yml" -o -name "docker-compose.yaml" 2>/dev/null

# Volume Shadow Copy (si LVM snapshots)
# Les volumes Docker peuvent contenir des preuves
```

---

## 11. Linux Forensics — Analyse SSH

```bash
# Clés autorisées
cat ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys2

# Vérifier les clés ajoutées récemment
ls -la ~/.ssh/
stat ~/.ssh/authorized_keys

# Connexions SSH connues
cat ~/.ssh/known_hosts

# Clés privées
ls -la ~/.ssh/id_rsa
ls -la ~/.ssh/id_ecdsa

# Config SSH
cat ~/.ssh/config
# Vérifier ProxyCommand, LocalForward, RemoteForward

# Attaquant a déposé une clé ?
# Vérifier si authorized_keys contient des clés inconnues
# Comparer avec les utilisateurs légitimes

# Sessions SSH actives
ss -tnp | grep :22
ps aux | grep sshd
```

---

## 12. Script d'Acquisition Linux Automatisée

```bash
#!/bin/bash
# linux_acquire.sh — Acquisition forensique Linux

OUTDIR="/evidence/linux_$(hostname)_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== LINUX FORENSICS ACQUISITION ==="
echo "Host: $(hostname)"
echo "Output: $OUTDIR"

# 1. Informations système
echo "[1] System info..."
uname -a > "$OUTDIR/uname.txt"
cat /etc/*release > "$OUTDIR/os_release.txt"
cat /proc/version > "$OUTDIR/kernel.txt"
cat /proc/cpuinfo > "$OUTDIR/cpu.txt"
free -h > "$OUTDIR/memory.txt"
df -h > "$OUTDIR/disk.txt"
mount > "$OUTDIR/mounts.txt"
lshw -short > "$OUTDIR/hardware.txt" 2>/dev/null

# 2. Utilisateurs
echo "[2] Users..."
cat /etc/passwd > "$OUTDIR/passwd.txt"
cat /etc/shadow > "$OUTDIR/shadow.txt" 2>/dev/null
cat /etc/group > "$OUTDIR/group.txt"
last -100 > "$OUTDIR/last.txt"
lastlog > "$OUTDIR/lastlog.txt"

# 3. Processus
echo "[3] Processes..."
ps auxf > "$OUTDIR/ps_aux.txt"
lsmod > "$OUTDIR/lsmod.txt"
lsof > "$OUTDIR/lsof.txt" 2>/dev/null

# 4. Réseau
echo "[4] Network..."
ss -tupan > "$OUTDIR/ss.txt"
iptables-save > "$OUTDIR/iptables.txt" 2>/dev/null
ip addr > "$OUTDIR/ip.txt"
cat /etc/hosts > "$OUTDIR/hosts.txt"
cat /etc/resolv.conf > "$OUTDIR/resolv.txt"

# 5. Logs
echo "[5] Logs..."
cp -r /var/log/* "$OUTDIR/logs/" 2>/dev/null
journalctl --no-pager -o short-full > "$OUTDIR/journal.txt" 2>/dev/null

# 6. Persistance
echo "[6] Persistence..."
ls -la /etc/cron* > "$OUTDIR/cron.txt"
ls -la /etc/systemd/system/ > "$OUTDIR/systemd.txt"
find / -name "*.service" -path "*/systemd/*" -exec cat {} \; > "$OUTDIR/services.txt" 2>/dev/null
cat /etc/rc.local > "$OUTDIR/rclocal.txt" 2>/dev/null
ls -la /etc/init.d/ > "$OUTDIR/initd.txt" 2>/dev/null

# 7. Bash histories
echo "[7] Bash histories..."
for user in /home/*/ /root/; do
    cat "${user}.bash_history" 2>/dev/null >> "$OUTDIR/bash_history_$(basename $user).txt"
done

# 8. SSH
echo "[8] SSH..."
find /home -name ".ssh" -type d > "$OUTDIR/ssh_dirs.txt"
cat /root/.ssh/authorized_keys > "$OUTDIR/root_authorized_keys.txt" 2>/dev/null
cat /etc/ssh/sshd_config > "$OUTDIR/sshd_config.txt" 2>/dev/null

# 9. Hash
echo "[9] Hashing..."
sha256sum "$OUTDIR"/*.txt "$OUTDIR"/logs/* > "$OUTDIR/hashes.txt" 2>/dev/null

echo ""
echo "=== DONE ==="
echo "Files in: $OUTDIR"
```

---

## 13. Dépannage Cross-Platform

```txt
PROBLÈME : Logs Linux effacés (journals vides)
SOLUTION : 
   - Vérifier /var/log/journal/ (pas /run/log/journal)
   - Les logs systemd persistent par défaut
   - Vérifier : journalctl --list-boots (boots précédents)
   - Si effacé → logs dans la RAM (Volatility linux.dmesg, linux.bash)

PROBLÈME : macOS SIP empêche l'acquisition
SOLUTION :
   - Contournement via Recovery Mode (Cmd+R → csrutil disable)
   - Checkm8 + ramdisk (Mac Intel)
   - DMA via Thunderbolt (Intel uniquement)
   - Sur Apple Silicon M1/M2/M3 : quasiment impossible sans auth

PROBLÈME : APFS verrouillé sur Mac (FileVault)
SOLUTION :
   - Si l'utilisateur est connecté → image du volume déverrouillé
   - Demander le mot de passe / PRK
   - Contournement via DMA (Intel)
   - Sur Apple Silicon : T2/Secure Enclave → extraction impossible sans clé

PROBLÈME : Logs macOS unifiés (log show) trop volumineux
SOLUTION : 
   - Utiliser des prédicats précis
   - Exporter au format .logarchive
   - Analyser avec l'outil Console.app sur macOS
```

---

## 14. Ressources

- **Log2Timeline/Plaso (Linux/macOS)** : https://github.com/log2timeline/plaso
- **SANS SIFT Workstation** : https://www.sans.org/tools/sift-workstation/
- **macOS Forensics Guide** : https://www.cellebrite.com/mobile-forensics/mac-forensics/
- **APFS-FUSE** : https://github.com/sgan81/apfs-fuse
- **LiME (Linux Memory)** : https://github.com/504ensicsLabs/LiMe
- **AVML (Microsoft)** : https://github.com/microsoft/avml
- **The Art of Mac Malware** : https://taomm.org/
- **Objective-See** : https://objective-see.com/ (Mac security tools)
- **Linux Forensics (SANS)** : https://www.sans.org/white-papers/36082/