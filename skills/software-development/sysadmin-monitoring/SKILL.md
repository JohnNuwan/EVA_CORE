---
name: sysadmin-monitoring
description: "Monitoring et supervision Linux : Prometheus, Grafana, Node Exporter, Netdata, collectd, alerting, dashboards, SNMP, métriques système et configuration de sondes."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [monitoring, prometheus, grafana, netdata, node-exporter, alertmanager, snmp, metrics, observability]
    related_skills: [sysadmin-logging, sysadmin-systemd, os-linux-admin, prometheus-grafana]
---

# Monitoring et Supervision Linux

## Vue d'ensemble

Le monitoring permet de détecter proactivement les anomalies (surcharge CPU, disque plein, service down) avant qu'elles n'impactent les utilisateurs. Ce skill couvre les outils de monitoring modernes pour l'infrastructure Linux : Prometheus stack pour la collecte de métriques, Grafana pour la visualisation, et des solutions légères comme Netdata.

## Théorie : Les 4 Signaux d'Or (Golden Signals — Google SRE)

| Signal | Métrique | Seuil typique |
|--------|----------|--------------|
| **Latence** | Temps de réponse API (p95, p99) | < 200ms p95 |
| **Trafic** | Requêtes/s, connexions/s | Dépend de la capacité |
| **Erreurs** | Taux d'erreur HTTP 5xx | < 1% |
| **Saturation** | CPU, RAM, disque, réseau | < 80% CPU/RAM, < 70% disque |

## Quand l'utiliser

- Mettre en place une supervision d'un serveur ou d'un cluster
- Configurer des alertes (CPU > 90%, disque > 85%, service down)
- Créer un dashboard Grafana pour visualiser l'état du système
- Diagnostiquer un goulot d'étranglement (CPU, RAM, I/O, réseau)
- Surveiller des services spécifiques (nginx, postgresql, docker)

## 1. Prometheus Stack (Standard Industriel)

### Architecture
```
[Node Exporter] ──(HTTP :9100)──→ [Prometheus Server] ──→ [Alertmanager]
                                        │                        │
                                        ▼                        ▼
                                   [Grafana]              [Notifications]
                                   :3000                   Email / Slack / PagerDuty
```

### Installation Rapide

```bash
# Prometheus Server (via binaires)
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mkdir -p /etc/prometheus /var/lib/prometheus

# Prometheus YAML (/etc/prometheus/prometheus.yml)
eval cat <<'PROMYAML'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
PROMYAML

# Service systemd (/etc/systemd/system/prometheus.service)
# (cf. skill sysadmin-systemd)
```

### Node Exporter (Métriques Système)

```bash
# Installation
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-*.linux-amd64.tar.gz
tar xvf node_exporter-*.tar.gz
sudo mv node_exporter-*/node_exporter /usr/local/bin/

# Désactiver les collecteurs inutiles pour réduire la charge
/usr/local/bin/node_exporter \
  --collector.disable-defaults \
  --collector.cpu \
  --collector.meminfo \
  --collector.diskstats \
  --collector.filesystem \
  --collector.netdev \
  --collector.loadavg \
  --collector.ntp \
  --web.listen-address=:9100

# Métriques exposées disponibles sur http://localhost:9100/metrics
# Exemple: node_cpu_seconds_total, node_memory_MemTotal_bytes, node_filesystem_avail_bytes
```

### Alertmanager

```yaml
# /etc/alertmanager/alertmanager.yml
route:
  receiver: 'admin'
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

receivers:
  - name: 'admin'
    email_configs:
      - to: 'admin@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
```

### Règles d'Alerte Prometheus (CPU, RAM, Disque)

```yaml
# /etc/prometheus/rules/alerts.yml
groups:
  - name: node_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "CPU > 90% sur {{ $labels.instance }}"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 15
        for: 5m
        labels: { severity: critical }
        annotations:
          summary: "Espace disque < 15% sur {{ $labels.instance }}"

      - alert: MemoryPressure
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels: { severity: warning }
        annotations:
          summary: "RAM > 90% utilisée sur {{ $labels.instance }}"

      - alert: HighLoadAverage
        expr: node_load15 > count(node_cpu_seconds_total{mode="user"}) * 0.8
        for: 5m
        labels: { severity: warning }
```

## 2. Grafana — Visualisation

```bash
# Installation
sudo apt install -y grafana   # ou via .deb
sudo apt install -y apt-transport-https software-properties-common
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
sudo apt update && sudo apt install grafana

# Démarrer
sudo systemctl enable --now grafana-server

# Configuration : /etc/grafana/grafana.ini
# Accès : http://serveur:3000 (admin:admin par défaut)
```

### Dashboards Recommandés

- **Node Exporter Full** (ID 1860) : Dashboard complet pour Node Exporter
- **Linux Hosts Metrics** (ID 16098) : Métriques hôtes Linux
- **1 Node Exporter** (ID 1860) : Simple mais complet

```bash
# Importer un dashboard via API
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"dashboard": {"id": null, "title": "Linux Host"}, "overwrite": true}' \
  http://localhost:3000/api/dashboards/db
```

## 3. Netdata — Monitoring Temps Réel Léger

```bash
# Installation one-liner
wget -O /tmp/netdata-kickstart.sh https://my-netdata.io/kickstart.sh
sudo bash /tmp/netdata-kickstart.sh

# Accès : http://serveur:19999

# Configuration alertes dans /etc/netdata/health.d/cpu.conf
# Les alertes sont pré-configurées (CPU, RAM, disque, réseau, inode)

# Réduire la consommation mémoire (optionnel)
echo "memory mode = ram" > /etc/netdata/netdata.conf
sudo systemctl restart netdata
```

## 4. Métriques Essentielles à Surveiller

### CPU
```bash
# Observabilité manuelle
top -b -n1 | head -15
htop
mpstat -P ALL 1 5

# Métrique Prometheus : node_cpu_seconds_total{instance="server1"}
# Alertes : > 90% pendant > 5 minutes
```

### Mémoire
```bash
free -h
vmstat 1 5

# RAM : /proc/meminfo
# Métrique Prometheus : node_memory_MemAvailable_bytes
# Swappiness : cat /proc/sys/vm/swappiness
# OOM killer : dmesg | grep -i "oom"
# Alerte : RAM disponible < 10% ET swap actif > 0
```

### Disque
```bash
df -h
iostat -x 1 5          # I/O détaillé par disque
iotop                  # I/O par processus
du -sh /var/log/

# Métriques Prometheus : node_filesystem_avail_bytes, node_disk_io_time_seconds_total
# Alertes : disque > 85%, inodes > 80% (df -i)
```

### Réseau
```bash
# Observabilité manuelle
ss -tulpn              # sockets TCP/UDP
iftop                  # bande passante par connexion
nethogs                # bande passante par processus

# Métriques Prometheus : node_network_receive_bytes_total, node_network_transmit_bytes_total
# Alertes : erreurs réseau > 0 (node_network_receive_errors_total)
```

## 5. Script de Monitoring Léger (sans Prometheus)

```bash
#!/bin/bash
# /usr/local/bin/syscheck.sh — vérification rapide système
set -euo pipefail

THRESHOLD_CPU=90
THRESHOLD_DISK=85
THRESHOLD_RAM=90

# CPU
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
if [ "$CPU" -gt "$THRESHOLD_CPU" ]; then
  echo "ALERTE: CPU à ${CPU}% (seuil: ${THRESHOLD_CPU}%)"
fi

# Disque
DISK=$(df -h / | awk 'NR==2 {print $5}' | cut -d% -f1)
if [ "$DISK" -gt "$THRESHOLD_DISK" ]; then
  echo "ALERTE: Disque / à ${DISK}% (seuil: ${THRESHOLD_DISK}%)"
fi

# RAM
RAM=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
if [ "$RAM" -gt "$THRESHOLD_RAM" ]; then
  echo "ALERTE: RAM à ${RAM}% (seuil: ${THRESHOLD_RAM}%)"
fi

# Service check
systemctl is-active --quiet nginx || echo "ALERTE: nginx est down"
systemctl is-active --quiet postgresql || echo "ALERTE: postgresql est down"
```

## Pièges Courants

1. **Trop de métriques** : Collecter 1000 métriques inutiles crée du bruit et du coût. Commencer par les 4 signaux d'or, ajouter au besoin.

2. **Pas d'alerte sur disque saturé** : C'est la panne la plus fréquente. Alerter à 80% pour avoir le temps d'agir.

3. **Alerte CPU à 100% normale** : Les CPU modernes montent à 100% en pic. Toujours mettre `for: 5m` minimum.

4. **Rétention non configurée** : Prometheus stocke par défaut 15 jours. Configurer `retention.size` et `retention.time`.

5. **Node Exporter sur le même volume que les données** : Si `/var` est plein, Node Exporter ne répond plus → alerte silencieuse. Mettre le collector sur une partition séparée.

## Liste de vérification (Checklist)

- [ ] Node Exporter installé sur chaque serveur
- [ ] Prometheus scrape targets configuré avec toutes les instances
- [ ] Alertmanager route configurée (email, Slack, Discord)
- [ ] Grafana dashboard importé (Node Exporter Full ID 1860)
- [ ] Alertes critiques : disque > 80%, CPU > 90%, RAM > 90%, service down
- [ ] Notification testée (alerte déclenchée et reçue)
- [ ] Rétention configurée (Prometheus `storage.tsdb.retention.time=30d`)
- [ ] Backup des configurations Prometheus + Grafana
