---
name: sysadmin-systemd
description: "Administration complète de systemd : unités (service, timer, socket, path, mount), targets, dépendances, journald, hardening de services, drop-ins et débogage."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [systemd, services, timers, journald, init, units, sockets, targets, cgroups, boot]
    related_skills: [os-linux-admin, sysadmin-logging, sysadmin-monitoring]
---

# Administration Systemd Complète

## Vue d'ensemble

systemd est le système d'init et le gestionnaire de services du noyau Linux moderne, adopté par toutes les distributions majeures. Il gère le démarrage, l'arrêt, la supervision, l'isolation et la journalisation des processus système.

**Concepts Fondamentaux :**
- **Unit** : ressource gérée par systemd (service, timer, socket, path, mount, target)
- **Target** : groupe d'unités → remplace les runlevels SysV
- **Journald** : service de journalisation binaire centralisée
- **CGroup** : isolation des processus par groupe de contrôle

## Quand l'utiliser

- Créer un service personnalisé pour une application ou un script
- Planifier des tâches récurrentes avec des timers (alternative moderne à cron)
- Activer un service au démarrage d'un événement (socket, path, device)
- Diagnostiquer un démarrage lent, un service qui refuse de s'arrêter
- Durcir un service avec les options de sandboxing (PrivateTmp, ProtectHome, etc.)

## Types d'Unités

| Type | Extension | Rôle |
|------|-----------|------|
| Service | `.service` | Processus démon (le plus courant) |
| Timer | `.timer` | Planification temporelle (remplace cron) |
| Socket | `.socket` | Activation sur connexion (listen) |
| Path | `.path` | Activation sur changement fichier |
| Mount | `.mount` | Point de montage systemd |
| Automount | `.automount` | Montage à la demande |
| Target | `.target` | Groupe d'unités (multi-user.target = runlevel 3) |

## Commandes Quotidiennes

### Gestion des Services

```bash
# Démarrer/arrêter/redémarrer
sudo systemctl start nginx.service
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx        # recharger la config sans interrompre

# Activer/désactiver au démarrage
sudo systemctl enable nginx        # lien symbolique dans /etc/systemd/system/*.wants/
sudo systemctl disable nginx
sudo systemctl enable --now nginx  # enable + start atomique

# Statut complet
systemctl status nginx             # PID, mémoire, logs récents
systemctl is-active nginx          # active/inactive
systemctl is-enabled nginx         # enabled/disabled
systemctl is-failed nginx          # failed/active

# Lister
systemctl list-units --type=service --state=running
systemctl list-units --type=timer --all
```

### Gestion des Timers

```bash
# Lister tous les timers
systemctl list-timers --all

# Créer un timer (ex: backup-daily.timer + backup-daily.service)
# Voir section "Exemple Complet" ci-dessous

# Déclencher manuellement un timer
sudo systemctl start backup-daily.timer

# Désactiver
sudo systemctl disable --now backup-daily.timer
```

### Journald (Consultation des Logs)

```bash
# Voir les logs d'un service
journalctl -u nginx.service
journalctl -u nginx -f              # follow (tail -f)
journalctl -u nginx --since today
journalctl -u nginx -p err          # seulement les erreurs

# Voir les logs du boot actuel
journalctl -b

# Voir les logs d'un PID spécifique
journalctl _PID=1234

# Voir les logs du noyau
journalctl -k

# Vider les logs (après rotation)
sudo journalctl --vacuum-time=7d    # garder 7 jours
sudo journalctl --vacuum-size=500M  # garder 500 Mo max

# Configurer la rétention dans /etc/systemd/journald.conf
# MaxRetentionSec=1week
# SystemMaxUse=500M
```

## Structure d'une Unité Service

```
[Unit]
Description=Mon service personnalisé
Documentation=https://docs.example.com
After=network.target postgresql.service
Requires=postgresql.service          # démarre avec, échoue si manquant
Wants=postgresql.service             # démarre avec, tolérant

[Service]
Type=simple                           # défaut, le processus principal
ExecStart=/usr/local/bin/monservice --config /etc/monservice/config.yaml
ExecReload=/bin/kill -HUP $MAINPID
ExecStop=/bin/kill -TERM $MAINPID
Restart=on-failure
RestartSec=5
User=monservice
Group=monservice
WorkingDirectory=/opt/monservice
EnvironmentFile=-/etc/monservice/env  # le - ignore si fichier absent
StandardOutput=journal
StandardError=journal

# Durcissement (sandboxing)
PrivateTmp=true
ProtectHome=true
ProtectSystem=full
NoNewPrivileges=true
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
ReadWritePaths=/var/lib/monservice

[Install]
WantedBy=multi-user.target
```

### Types de Services

| Type | Comportement |
|------|-------------|
| `simple` | Processus principal = ExecStart, ne fork pas |
| `forking` | Processus principal fork, le parent exit (démons classiques) |
| `oneshot` | S'exécute une fois, attend la fin (pour timers) |
| `notify` | Le processus envoie `sd_notify(READY=1)` via libsystemd |
| `dbus` | S'enregistre sur le bus D-Bus, systemd attend le nom |
| `idle` | Démarre après que tous les jobs soient soumis |

## Exemple Complet : Service + Timer

### 1. Script à exécuter
```bash
#!/bin/bash
# /usr/local/bin/backup-db.sh
set -euo pipefail
/usr/bin/pg_dump mydb | gzip > /var/backups/mydb-$(date +\%Y\%m\%d).sql.gz
```

### 2. Service (oneshot car le script se termine)
```ini
# /etc/systemd/system/backup-db.service
[Unit]
Description=Sauvegarde quotidienne de la base

[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup-db.sh
User=postgres
Group=postgres
```

### 3. Timer (planification)
```ini
# /etc/systemd/system/backup-db.timer
[Unit]
Description=Minuterie sauvegarde base

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true           # si le système était éteint, exécute au prochain boot
RandomizedDelaySec=60     # évite les pics de charge à 03:00 pile

[Install]
WantedBy=timers.target
```

### 4. Activation
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now backup-db.timer
systemctl list-timers backup-db.timer
```

## Drop-in (Override) — Ne JAMAIS modifier les unités système

Pour surcharger une option d'une unité existante :

```bash
# Créer le drop-in
sudo systemctl edit nginx.service
# ou manuellement :
sudo mkdir -p /etc/systemd/system/nginx.service.d/
sudo tee /etc/systemd/system/nginx.service.d/override.conf << 'EOF'
[Service]
Restart=always
RestartSec=10
LimitNOFILE=65536
EOF

# Appliquer
sudo systemctl daemon-reload
sudo systemctl restart nginx
```

Les drop-ins sont prioritaires sur l'unité d'origine et survivent aux mises à jour du paquet.

## Durcissement (Hardening) de Service

systemd offre des options de sandboxing pour limiter la surface d'attaque :

```ini
[Service]
# Système de fichiers
ProtectSystem=full           # /usr et /etc readonly
ProtectHome=true             # /root, /home inaccessible
PrivateTmp=true              # /tmp isolé
ReadWritePaths=/var/lib/app  # exceptions en écriture

# Réseau
PrivateNetwork=true          # pas de réseau du tout
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

# Process
NoNewPrivileges=true         # empêche l'escalade (sudo, setuid)
CapabilityBoundingSet=CAP_NET_BIND_SERVICE  # capabilities autorisées
SystemCallFilter=@system-service           # syscalls autorisés
SystemCallArchitectures=native

# Exécution
ProtectKernelModules=true
ProtectKernelTunables=true
ProtectControlGroups=true
MemoryMax=512M               # limite mémoire via cgroups
TasksMax=100                 # max threads/processes
```

Vérifier le niveau de durcissement :
```bash
systemd-analyze security nginx.service
```

## Activation par Socket et Path

### Socket Activation (ex: service qui écoute sur une socket UNIX)
```ini
# /etc/systemd/system/myapp.socket
[Socket]
ListenStream=/var/run/myapp.sock
SocketUser=myapp
SocketGroup=myapp
SocketMode=0660

[Install]
WantedBy=sockets.target
```

```ini
# /etc/systemd/system/myapp.service
[Service]
ExecStart=/usr/bin/myapp
```
Le service est démarré automatiquement quand une connexion arrive sur la socket.

### Path Activation (ex: traitement dès qu'un fichier apparaît)
```ini
# /etc/systemd/system/processor.path
[Path]
PathModified=/var/spool/incoming/
Unit=processor.service

[Install]
WantedBy=multi-user.target
```

## Débogage (Troubleshooting)

```bash
# Analyser le temps de démarrage
systemd-analyze
systemd-analyze blame           # temps par unité
systemd-analyze critical-chain  # chemin critique de boot

# Vérifier la syntaxe d'une unité
systemd-analyze verify /etc/systemd/system/monservice.service

# Voir la liste des dépendances d'une unité
systemctl list-dependencies nginx.service

# Recharger systemd après modification
sudo systemctl daemon-reload

# Désactiver/masquer complètement un service
sudo systemctl mask nginx.service   # lien vers /dev/null
sudo systemctl unmask nginx.service

# Tuer un service qui refuse de s'arrêter
sudo systemctl kill -s SIGKILL nginx.service
```

## Pièges Courants

1. **Oublier `systemctl daemon-reload`** après avoir modifié une unité.

2. **Type=simple avec un script qui fork** : Si votre script lance un processus fils et exit, systemd pense que le service s'est arrêté. Utiliser `Type=forking` ou `Type=notify`.

3. **Timer `OnCalendar` mal formaté** : Vérifier avec `systemd-analyze calendar "*-*-* 02:00:00"`. Les expressions cron ne sont pas compatibles — utiliser `OnCalendar=`.

4. **StandardOutput=journal** : Les logs passent par journald, pas par un fichier. Si un logiciel écrit dans `/var/log/` ET dans stdout, les logs sont dupliqués.

5. **Limites par défaut** : `LimitNOFILE=1024` pour les services. Les bases de données et serveurs web nécessitent `LimitNOFILE=65536`.

## Liste de vérification (Checklist)

- [ ] `systemctl daemon-reload` après chaque modification d'unité
- [ ] Vérifier avec `systemd-analyze verify` avant d'activer
- [ ] Tester avec `systemctl start` avant `enable`
- [ ] Vérifier les logs avec `journalctl -u service -f` en temps réel
- [ ] Utiliser `Type=oneshot` pour les tâches timer
- [ ] Toujours utiliser les drop-ins (`systemctl edit`) pour modifier les unités système
- [ ] Configurer `journald.conf` : rétention, taille max, persistance
- [ ] Durcir avec `ProtectSystem`, `PrivateTmp`, `NoNewPrivileges`
