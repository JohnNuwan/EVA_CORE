---
name: network-monitoring-advanced
description: Guide complet du monitoring réseau avancé — Prometheus, Grafana, Netdata, collecte de métriques, alerting, dashboards temps réel, et stack d'observabilité réseau.
tags: [prometheus, grafana, netdata, monitoring, metrics, observability, alerting, snmp]
---

# Monitoring Réseau Avancé

## Présentation

Stack de monitoring réseau complète couvrant la collecte, le stockage, la visualisation et l'alerte sur les métriques d'infrastructure réseau. Architecture basée sur le pull model (Prometheus) et push model (Netdata).

### Composants de la stack

| Composant | Rôle | Type |
|-----------|------|------|
| **Prometheus** | Collecte et stockage TSDB | Pull |
| **Grafana** | Visualisation et dashboards | Query |
| **Netdata** | Monitoring temps réel haute-fréquence | Push/Agent |
| **Alertmanager** | Gestion des alertes | Push |
| **SNMP Exporter** | Équipements réseau legacy | Pull |
| **Blackbox Exporter** | Probes HTTP/ICMP/TCP externes | Pull |

---

## Prometheus — Architecture et Déploiement

### Architecture

```
                    +--------------------+
                    |   Service Discovery |
                    | (k8s, consul, DNS)  |
                    +---------+----------+
                              |
    +----------+     +--------+--------+     +--------------+
    | Exporters |---->| Prometheus    |---->| Alertmanager |
    | (node,    |    | Server (TSDB)  |     +------+-------+
    |  SNMP,    |    +-------+-------+            |
    |  blackbox)|            |                    +--> Slack/Email/PagerDuty
    +----------+             |
                     +-------v-------+
                     |   Grafana     |
                     | (Dashboards)  |
                     +---------------+
```

### Installation

```bash
# Prometheus Server
wget https://github.com/prometheus/prometheus/releases/latest/download/prometheus-*.linux-amd64.tar.gz
tar xvf prometheus-*.tar.gz
sudo mv prometheus-*/prometheus /usr/local/bin/
sudo mkdir -p /etc/prometheus /var/lib/prometheus

# Netdata (installation one-liner)
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Grafana
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update && sudo apt-get install grafana
```

### Configuration Prometheus de base

```yaml
# /etc/prometheus/prometheus.yml
global:
  scrape_interval: 15s      # Fréquence de collecte
  evaluation_interval: 15s  # Fréquence d'évaluation des règles
  scrape_timeout: 10s       # Timeout de collecte

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - "alerts/*.yml"

scrape_configs:
  # Métriques du serveur lui-même
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Équipements réseau via SNMP
  - job_name: 'snmp'
    scrape_interval: 60s
    scrape_timeout: 30s
    static_configs:
      - targets:
          - 192.168.1.1     # Routeur principal
          - 192.168.1.2     # Switch cœur
    metrics_path: /snmp
    params:
      module: [if_mib]
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
    metric_relabel_configs:
      - source_labels: [ifDescr]
        target_label: interface
        regex: '(.*)'
        replacement: '${1}'

  # Probes externes (HTTP, ICMP, TCP)
  - job_name: 'blackbox'
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://example.com
          - https://api.service.com
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance

  # Métriques système des serveurs
  - job_name: 'node'
    static_configs:
      - targets:
          - 'localhost:9100'
```

---

## Exporteurs Spécialisés

### SNMP Exporter — Équipements Réseau

```yaml
# /etc/prometheus/snmp.yml (généré via snmp_exporter generator)
# Installation
# docker run --rm -v $(pwd):/opt -ti prom/snmp-generator generate
modules:
  if_mib:
    walk:
      - 1.3.6.1.2.1.2        # interfaces
      - 1.3.6.1.2.1.31.1.1   # ifXTable
    metrics:
      - name: ifHCInOctets
        oid: 1.3.6.1.2.1.31.1.1.1.6
        type: counter
      - name: ifHCOutOctets
        oid: 1.3.6.1.2.1.31.1.1.1.10
        type: counter
      - name: ifInErrors
        oid: 1.3.6.1.2.1.2.2.1.14
        type: counter
      - name: ifOutErrors
        oid: 1.3.6.1.2.1.2.2.1.20
        type: counter
      - name: ifOperStatus
        oid: 1.3.6.1.2.1.2.2.1.8
        type: gauge
```

### Blackbox Exporter — Probes Externes

```bash
# Installation
wget https://github.com/prometheus/blackbox_exporter/releases/latest/download/blackbox_exporter-*.linux-amd64.tar.gz
tar xvf blackbox_exporter-*.tar.gz
sudo mv blackbox_exporter-*/blackbox_exporter /usr/local/bin/

# Test manuel
curl 'http://localhost:9115/probe?module=http_2xx&target=https://google.com'
```

```yaml
# /etc/blackbox/blackbox.yml
modules:
  http_2xx:
    prober: http
    http:
      valid_http_versions: ["HTTP/1.1", "HTTP/2"]
      valid_status_codes: [200, 301, 302]
      preferred_ip_protocol: ip4
      follow_redirects: true
      tls_config:
        insecure_skip_verify: false

  icmp:
    prober: icmp
    icmp:
      preferred_ip_protocol: ip4
      payload_size: 64

  tcp_connect:
    prober: tcp
    tcp:
      query_response:
        - expect: "^SSH-2.0-"
```

---

## Grafana — Dashboards et Visualisation

### Métriques réseau essentielles à monitorer

| Métrique | Description | Source |
|----------|-------------|--------|
| `node_network_receive_bytes_total` | Octets reçus par interface | node_exporter |
| `node_network_transmit_bytes_total` | Octets transmis par interface | node_exporter |
| `node_network_receive_errors_total` | Erreurs de réception | node_exporter |
| `rate(node_network_receive_bytes_total[5m])` | Débit entrant (bps) | node_exporter |
| `ifHCInOctets` | Octets reçus (SNMP) | snmp_exporter |
| `probe_success` | Succès/monte de la probe | blackbox_exporter |
| `probe_duration_seconds` | Temps de réponse | blackbox_exporter |
| `probe_http_status_code` | Code HTTP retourné | blackbox_exporter |

### Requêtes PromQL essentielles

```promql
# Bande passante utilisée par interface (bps)
rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8

# Pourcentage d'erreurs réseau
rate(node_network_receive_errors_total[5m]) / rate(node_network_receive_bytes_total[5m]) * 100

# Taux de perte de paquets ICMP
avg(probe_success{module="icmp"}) by (instance)

# Latence réseau (percentiles)
histogram_quantile(0.99, rate(probe_http_duration_seconds_bucket[5m])) by (instance)

# Connexions TCP par état
node_netstat_Tcp_CurrEstab

# Interfaces down
count(node_network_up{device!~"lo|br.*|docker.*|veth.*"} == 0) by (instance)
```

### Dashboard JSON pour Grafana

```json
{
  "dashboard": {
    "title": "Monitoring Réseau",
    "panels": [
      {
        "title": "Débit Interfaces",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_bytes_total{device!=\"lo\"}[5m]) * 8",
            "legendFormat": "{{device}} RX"
          },
          {
            "expr": "rate(node_network_transmit_bytes_total{device!=\"lo\"}[5m]) * 8",
            "legendFormat": "{{device}} TX"
          }
        ]
      },
      {
        "title": "Latence Probe HTTP",
        "type": "stat",
        "targets": [
          {
            "expr": "avg(probe_duration_seconds{module=\"http_2xx\"})"
          }
        ]
      },
      {
        "title": "Erreurs Réseau",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(node_network_receive_errors_total[5m])",
            "legendFormat": "{{device}} RX Errors"
          }
        ]
      }
    ]
  }
}
```

---

## Netdata — Monitoring Temps Réel

### Fonctionnalités Réseau

- **Network Monitoring Dashboard** — Visualisation temps réel de tout le trafic
- **Topology Viewer** — Cartographie automatique des connexions réseau
- **NetFlow Traffic Analyzer** — Analyse des flux par protocole, IP, port
- **SNMP Trap Monitoring** — Réception et analyse des traps SNMP
- **Network Device Auto-Discovery** — Découverte automatique des équipements
- **Anomaly Advisor** — Détection d'anomalies par ML

### Architecture Netdata

```
  +--------------+       +--------------+       +-------------+
  | Netdata Agent|<----->| Netdata Cloud|       | Grafana     |
  | (chaque noeud)|       | (SaaS/On-Prem)|      | (via plugin)|
  +--------------+       +--------------+       +-------------+
        |                       |
  +-----v-----+         +------v------+
  | Plugins    |         | Alerting    |
  | (go.d, c,  |         | (email,     |
  |  python)   |         |  slack, web)|
  +------------+         +-------------+
```

### Plugins réseau Netdata

```bash
# Plugins réseau disponibles (go.d)
/usr/libexec/netdata/plugins.d/go.d.plugin -d

# go.d/network.conf — Monitoring interfaces
# go.d/snmp.conf — SNMP devices
# go.d/portcheck.conf — TCP port checks
# go.d/netflow.conf — NetFlow/IPFIX collector
# go.d/wireguard.conf — WireGuard interfaces
```

### Alertes réseau Netdata

```yaml
# /etc/netdata/health.d/net.conf
# Alerte bande passante > 80%
template: 10s_inbound_bandwidth
      on: net.inbound_bytes
    hosts: *
     calc: ($this - $this_before_10s) / ($this_before_10s) * 100
    units: %
    every: 10s
     warn: $this > 80
     crit: $this > 95
    delay: up 1m down 5m
     info: Pourcentage de bande passante entrante utilisée

template: interface_down
      on: net.operstate
    hosts: *
    units: state
     calc: $this
    every: 10s
     warn: $this == 0
    delay: up 30s down 1m
     info: Interface réseau down
```

---

## Alertmanager — Gestion des Alertes

### Configuration

```yaml
# /etc/alertmanager/alertmanager.yml
route:
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
      repeat_interval: 5m
    - match:
        severity: warning
      receiver: 'slack'
      repeat_interval: 30m

receivers:
  - name: 'default'
    email_configs:
      - to: 'admin@example.com'

  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/...'
        channel: '#alerts-network'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ .CommonAnnotations.description }}'

  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: '...'
        severity: 'critical'
```

### Règles d'alerte Prometheus

```yaml
# /etc/prometheus/alerts/network.yml
groups:
  - name: network
    rules:
      - alert: InterfaceDown
        expr: node_network_up{device!~"lo|br.*|docker.*"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Interface {{ $labels.device }} down sur {{ $labels.instance }}"

      - alert: HighBandwidthUsage
        expr: |
          (rate(node_network_receive_bytes_total{device!="lo"}[5m]) * 8) / 1e9 > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Bande passante > 80% sur {{ $labels.device }}"

      - alert: HighErrorRate
        expr: |
          rate(node_network_receive_errors_total[5m]) / rate(node_network_receive_bytes_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreurs réseau élevé sur {{ $labels.device }}"

      - alert: HostUnreachable
        expr: probe_success{module="icmp"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Hôte {{ $labels.instance }} injoignable (ICMP)"

      - alert: EndpointDown
        expr: probe_success{module="http_2xx"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Endpoint HTTP {{ $labels.instance }} down"

      - alert: HighLatency
        expr: probe_duration_seconds > 1.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Latence élevée vers {{ $labels.instance }} ({{ $value }}s)"
```

---

## Métriques Avancées

### Collecte via SNMP Walk

```bash
# Marche SNMP complète
snmpwalk -v2c -c public 192.168.1.1 .1.3.6.1.2.1.2

# Interfaces avec débit
snmpwalk -v2c -c public 192.168.1.1 ifDescr
snmpwalk -v2c -c public 192.168.1.1 ifSpeed
snmpwalk -v2c -c public 192.168.1.1 ifOperStatus

# CPU et mémoire du routeur
snmpwalk -v2c -c public 192.168.1.1 .1.3.6.1.4.1.9.9.109  # Cisco CPU
snmpwalk -v2c -c public 192.168.1.1 .1.3.6.1.4.1.9.9.48   # Cisco Memory
```

### Telegraf comme alternative push

```toml
# /etc/telegraf/telegraf.conf
[[inputs.net]]
  interfaces = ["eth0", "eth1"]
  fielddrop = ["icmp", "tcp", "udp"]

[[inputs.netstat]]
  fields = ["tcp_established", "tcp_time_wait", "tcp_close_wait"]

[[inputs.snmp]]
  agents = ["udp://192.168.1.1:161", "udp://192.168.1.2:161"]
  version = 2
  community = "public"
  [[inputs.snmp.field]]
    oid = "RFC1213-MIB::sysName.0"
    name = "system_name"
  [[inputs.snmp.table]]
    oid = "IF-MIB::ifTable"
    name = "interface"

[[outputs.prometheus_client]]
  listen = ":9273"
```

---

## Cas d'Usage Avancés

### Détection de Débit Anormal

```promql
# Détection de pic soudain (3x la moyenne mobile)
(
  rate(node_network_receive_bytes_total[5m])
  /
  avg_over_time(rate(node_network_receive_bytes_total[5m])[1h:5m])
) > 3
```

### Cartographie des Flux Réseau

```bash
# Netdata NetFlow
# Activer le collector NetFlow dans go.d/netflow.conf
- name: netflow
  listen: ":2055"
  protocol: netflow_v9
  cache_size: 10000
```

### Monitoring BGP

```bash
# Prometheus BGP exporter
docker run -d --name bgp-exporter \
  -p 9449:9449 \
  -e BGP_EXPORTER_TARGETS="192.168.1.1:179,192.168.1.2:179" \
  ghcr.io/juliocri/grafana-bgp-exporter
```

```promql
# Métriques BGP
bgp_prefixes_advertised{}  # Préfixes annoncés
bgp_prefixes_received{}    # Préfixes reçus
bgp_session_up{}           # État de session BGP
bgp_routes_total{}         # Routes totales
```

---

## Pièges et Bonnes Pratiques

- **Scrape interval** : Adapter selon l'équipement (60s+ pour switches, 15s pour serveurs)
- **SNMP Timeout** : Toujours mettre un timeout >30s pour les gros équipements
- **Label hygiene** : Ne pas utiliser d'IDs dynamiques (pod IDs) comme labels
- **Retention** : Configurer `--storage.tsdb.retention.time=30d` dans Prometheus
- **Rate limiting** : Éviter de scraper trop d'équipements depuis un seul Prometheus
- **Netdata** : Ne pas activer tous les plugins sur un serveur avec peu de ressources
- **Grafana** : Utiliser des variables de template pour les dashboards réutilisables

## Ressources

- Prometheus : https://prometheus.io/docs/
- Grafana : https://grafana.com/docs/
- Netdata : https://learn.netdata.cloud/
- SNMP Exporter : https://github.com/prometheus/snmp_exporter
- Blackbox Exporter : https://github.com/prometheus/blackbox_exporter
- Awesome Prometheus : https://github.com/roaldnefs/awesome-prometheus