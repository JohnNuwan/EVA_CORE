---
name: sysadmin-logging
description: "Centralisation et gestion des logs Linux : rsyslog, journald, logrotate, syslog-ng, Loki, Graylog, ELK stack, auditd, rotation et archivage."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [logging, rsyslog, journald, logrotate, syslog-ng, loki, auditd, centralisation, logs]
    related_skills: [sysadmin-systemd, sysadmin-monitoring, os-linux-admin]
---

# Centralisation et Gestion des Logs Linux

## Vue d'ensemble

Les logs sont la mémoire du système — ils enregistrent chaque événement, erreur et action de l'utilisateur. Un bon système de logging permet de :
- Diagnostiquer les pannes rapidement
- Détecter les intrusions (via auditd)
- Assurer la conformité (RGPD, SOC2, ISO 27001)
- Centraliser des centaines de serveurs

## Composants du Logging Linux

| Composant | Rôle | Port/protocole |
|-----------|------|----------------|
| **journald** | Log binaire systemd, capture stdout/stderr des services | Interne (journal) |
| **rsyslog** | Log textuel traditionnel, routage et centralisation | 514/UDP, 6514/TCP TLS |
| **syslog-ng** | Alternative moderne à rsyslog, meilleure performance | 514/UDP, 6514/TCP TLS |
| **logrotate** | Rotation automatique des fichiers de logs | N/A |
| **auditd** | Audit de sécurité (accès fichiers, syscalls) | N/A |
| **Loki** | Agrégation de logs Cloud Native (Grafana) | 3100/HTTP |

## Quand l'utiliser

- Configurer la rétention et rotation des logs
- Mettre en place un serveur de logs centralisé
- Analyser des logs système pour diagnostiquer un problème
- Configurer auditd pour la conformité et la détection d'intrusion
- Envoyer les logs vers une stack centralisée (Loki, Graylog, ELK)

## 1. Journald — Configuration et Maintenance

```bash
# Configuration : /etc/systemd/journald.conf
# Paramètres clés
cat >> /etc/systemd/journald.conf << 'EOF'
# Taille maximale du journal persistent
SystemMaxUse=500M
# Temps de rétention
MaxRetentionSec=2week
# Compression
Compress=yes
# Synchronisation disque (yes=durable, no=performant)
SyncIntervalSec=5m
EOF

sudo systemctl restart systemd-journald

# Commandes utiles
journalctl --disk-usage                    # espace utilisé
journalctl --vacuum-size=200M             # réduire à 200 Mo
journalctl --vacuum-time=7d               # supprimer les logs > 7 jours
journalctl -u nginx --since "1 hour ago"  # logs récents d'un service

# Forward vers rsyslog (activé par défaut)
# ForwardToSyslog=yes dans journald.conf
```

## 2. Rsyslog — Centralisation Serveur

### Configuration Client (envoie ses logs)

```bash
# /etc/rsyslog.d/50-central.conf
# Envoi de tous les logs vers le serveur central
*.* @192.168.1.100:514           # UDP (perte possible)
## *.* @@192.168.1.100:514       # TCP (fiable)
## *.* @@192.168.1.100:6514      # TLS (chiffré)

# Avec queue disque pour éviter la perte réseau
$ActionQueueFileName fwdRule1
$ActionQueueMaxDiskSpace 1g
$ActionQueueSaveOnShutdown on
$ActionQueueType LinkedList
$ActionResumeRetryCount -1
```

### Configuration Serveur (reçoit les logs)

```bash
# /etc/rsyslog.conf — décommenter les modules TCP/UDP
module(load="imudp")
input(type="imudp" port="514")
# module(load="imtcp")
# input(type="imtcp" port="514")

# /etc/rsyslog.d/50-templates.conf
template(name="RemoteLogs" type="string"
  string="/var/log/remote/%HOSTNAME%/%PROGRAMNAME%.log")

# Stocker les logs entrants par hôte
if $fromhost-ip != "127.0.0.1" then {
  action(type="omfile" dynaFile="RemoteLogs")
  stop
}
```

### Templates Personnalisés

```bash
# /etc/rsyslog.d/60-formats.conf
template(name="JsonFormat" type="list") {
  constant(value="{")
  constant(value="\"@timestamp\":\"")
  property(name="timegenerated" dateFormat="rfc3339")
  constant(value="\",\"host\":\"")
  property(name="hostname")
  constant(value="\",\"severity\":\"")
  property(name="syslogseverity-text")
  constant(value="\",\"facility\":\"")
  property(name="syslogfacility-text")
  constant(value="\",\"msg\":\"")
  property(name="msg")
  constant(value="\"}")
}

# Logs au format JSON pour ingestion facile
*.* action(type="omfile" file="/var/log/all.json" template="JsonFormat")
```

## 3. Logrotate — Rotation Automatique

```bash
# /etc/logrotate.conf — Configuration globale
weekly                # rotation hebdomadaire
rotate 4              # garder 4 archives
create                # recréer le fichier vide après rotation
dateext              # suffixe date (log-20250101.gz)
compress             # compresser les archives (gzip)
missingok            # pas d'erreur si fichier absent
notifempty           # ne pas faire tourner si vide

# Inclure les configurations spécifiques
include /etc/logrotate.d
```

### Exemple par Application

```bash
# /etc/logrotate.d/nginx
/var/log/nginx/*.log {
    weekly
    rotate 8
    missingok
    compress
    delaycompress           # compresser au tour suivant (pour avoir 1 fichier récent non compressé)
    notifempty
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}

# /etc/logrotate.d/postgresql
/var/log/postgresql/*.log {
    daily
    rotate 30
    compress
    missingok
    notifempty
    size 100M               # rotation si > 100 Mo même avant la fin du jour
    postrotate
        systemctl reload postgresql
    endscript
}

# /etc/logrotate.d/custom-app
/opt/myapp/log/*.log {
    daily
    rotate 7
    dateext
    maxsize 200M
    compress
    copytruncate           # copier + tronquer sans changer le handle (utile pour apps qui ne rouvrent pas leur log)
    missingok
}
```

### Vérification et Test

```bash
# Test de configuration
sudo logrotate -d /etc/logrotate.conf   # dry-run
sudo logrotate -f /etc/logrotate.conf   # forcer la rotation immédiatement
sudo logrotate -vf /etc/logrotate.d/nginx  # verbeux + force pour un fichier
```

## 4. Auditd — Audit de Sécurité

```bash
# /etc/audit/rules.d/audit.rules
# Surveiller les modifications de fichiers critiques
-w /etc/passwd -p wa -k identity
-w /etc/shadow -p wa -k identity
-w /etc/ssh/sshd_config -p wa -k sshd_config
-w /etc/sudoers -p wa -k sudoers

# Surveiller les syscalls sensibles
-a always,exit -S execve -k executed_commands

# Surveiller les modifications de permissions
-a always,exit -S chmod -S chown -S fchmod -S fchown -k perm_mod

# Surveiller les connexions réseau
-a exit,always -S bind -k network_bind

# Surveiller les montages/umount
-a always,exit -S mount -S umount2 -k mount

# Réappliquer
sudo augenrules --load
sudo systemctl restart auditd

# Consultation
ausearch -k identity --start today       # événements "identity" du jour
ausearch -m execve -i                     # commandes exécutées avec interprétation
aureport -k                               # résumé par clé
aureport -m                               # résumé par type d'événement
```

## 5. Loki — Agrégation Cloud Native

```bash
# Installation rapide (simple binaire)
wget https://github.com/grafana/loki/releases/latest/download/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki

# Configuration minimale /etc/loki/config.yaml
auth_enabled: false
server:
  http_listen_port: 3100
ingester:
  lifecycler:
    ring:
      kvstore:
        store: inmemory
  chunk_idle_period: 5m
storage_config:
  boltdb_shipper:
    active_index_directory: /var/lib/loki/index
    cache_location: /var/lib/loki/cache
  filesystem:
    directory: /var/lib/loki/chunks

# Agent Promtail (collecte et envoie)
# /etc/promtail/config.yaml
positions:
  filename: /var/lib/promtail/positions.yaml
clients:
  - url: http://localhost:3100/loki/api/v1/push
scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*.log
  - job_name: journal
    journal:
      path: /var/log/journal
    relabel_configs:
      - source_labels: ['__journal__systemd_unit']
        target_label: 'unit'
```

## 6. Graylog — Centralisation Complète

```bash
# Stack: Graylog Server + MongoDB + Elasticsearch
# Installation via Docker Compose recommandée
# Ou paquet Debian :
wget https://packages.graylog2.org/repo/packages/graylog-5.0-repository_latest.deb
sudo dpkg -i graylog-5.0-repository_latest.deb
sudo apt update && sudo apt install graylog-server

# Sidecar (collecteur) sur chaque serveur
sudo apt install graylog-sidecar
```

## 7. Script d'Analyse Rapide

```bash
#!/bin/bash
# /usr/local/bin/log-quickcheck.sh
set -euo pipefail

echo "=== ERREURS RÉCENTES (dernière heure) ==="
journalctl -p err --since "1 hour ago" --no-pager | tail -20

echo -e "\n=== TENTATIVES SSH ÉCHOUÉES ==="
journalctl -u sshd -g "Failed password" --since today | wc -l
echo "tentatives échouées aujourd'hui"

echo -e "\n=== LOGROTATE STATUS ==="
sudo logrotate -d /etc/logrotate.conf 2>&1 | grep -E "(error|warning)" || echo "Aucune erreur"

echo -e "\n=== LOGS LES PLUS VOLUMINEUX ==="
du -sh /var/log/*.log 2>/dev/null | sort -rh | head -10

echo -e "\n=== AUDITD: DERNIERS ÉVÉNEMENTS ==="
sudo ausearch --start today -m execve --just-one 2>/dev/null | tail -5 || echo "auditd pas configuré"
```

## Pièges Courants

1. **Logrotate jamais testé** : Un fichier de log peut atteindre 100 Go si la rotation ne fonctionne pas. Tester avec `logrotate -d`.

2. **journald sans persistence** : Par défaut, journald est volatile sur certaines distributions. Activer la persistence :
   ```bash
   sudo mkdir -p /var/log/journal
   sudo systemd-tmpfiles --create --prefix /var/log/journal
   ```

3. **Rsyslog UDP sans queue** : Si le serveur central est injoignable, les logs UDP sont perdus. Configurer `ActionQueueType LinkedList`.

4. **Taille illimitée des logs** : Toujours configurer `SystemMaxUse=` dans journald.conf ET `maxsize` dans logrotate.

5. **Rotation sans signal au processus** : Certaines applications (nginx, syslog) ne recréent pas leur handle de fichier. Ajouter `postrotate` avec le bon signal.

## Liste de vérification (Checklist)

- [ ] journald.conf configuré (SystemMaxUse, MaxRetentionSec)
- [ ] logrotate configuré pour tous les services critiques
- [ ] Logrotate testé : `logrotate -d /etc/logrotate.conf`
- [ ] Centralisation des logs active (rsyslog → serveur central ou Loki)
- [ ] auditd configuré avec règles essentielles
- [ ] Alerte rotation échouée (surveiller /var/log avec monitoring)
- [ ] Logs sensibles protégés (chmod 640, groupe adm)
- [ ] Archivage des logs froids (plus de 90 jours) vers stockage froid
