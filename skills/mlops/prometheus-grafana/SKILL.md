---
name: prometheus-grafana
description: "Monitoring & observabilité — Prometheus pour la collecte de métriques, Alertmanager pour les alertes, Grafana pour les dashboards, Loki pour les logs, bonnes pratiques SRE"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [prometheus, grafana, monitoring, alerting, metrics, dashboards, loki, alertmanager, observabilité, sre]
    related_skills: [kubernetes-avance, docker-avance, ansible-automation, ci-cd-pipelines]
---

# Prometheus & Grafana — Monitoring & Observabilité

## Vue d'ensemble

Prometheus (collecte de métriques) + Grafana (visualisation) + Alertmanager (notifications) forment la stack de monitoring standard dans l'écosystème cloud-native. Cette compétence couvre l'installation, la configuration, l'écriture de règles d'alerte, la création de dashboards, l'intégration Loki pour les logs, et les patterns SRE (Service Level Objectives).

## Quand l'utiliser

- Monitorer les métriques d'infrastructure (CPU, RAM, disque, réseau)
- Surveiller des applications custom avec endpoints Prometheus
- Créer des dashboards Grafana pour visualiser les KPIs
- Mettre en place des alertes (Slack, PagerDuty, Telegram, email)
- Centraliser les logs avec Loki et les corréler aux métriques
- Définir des SLO/SLI/SLA et suivre les burn rates

---

## 1. Architecture Stack

```
Applications
    │ (métriques HTTP /metrics)
    ▼
Prometheus Server ──► Alertmanager ──► Slack / Telegram / PagerDuty
    │                     ▲
    │ scrape               │
    ▼                     │
TSDB (local)             │
    │                     │
    ▼  (PromQL)           │
Grafana ◄────────────────┘
    │
    ▼
Loki (logs) ← Promtail (agents log)
```

---

## 2. Installation (Docker Compose)

```yaml
# monitoring/docker-compose.yml
version: "3.8"

networks:
  monitoring:
    driver: bridge

volumes:
  prometheus_data:
  grafana_data:
  loki_data:

services:
  prometheus:
    image: prom/prometheus:v2.55
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--web.enable-lifecycle'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules/:/etc/prometheus/rules/
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:v0.27
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    ports:
      - "9093:9093"
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:11.2
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
      - GF_AUTH_ANONYMOUS_ENABLED=false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards/:/etc/grafana/provisioning/dashboards/
      - ./grafana/datasources/:/etc/grafana/provisioning/datasources/
    ports:
      - "3000:3000"
    networks:
      - monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:v1.8
    command:
      - '--path.rootfs=/host'
      - '--collector.filesystem.ignored-mount-points=^/(sys|proc|dev|host|etc)($$|/)'
    pid: host
    volumes:
      - /:/host:ro,rslave
    networks:
      - monitoring

  loki:
    image: grafana/loki:3.1
    command: -config.file=/etc/loki/loki-config.yaml
    volumes:
      - ./loki-config.yaml:/etc/loki/loki-config.yaml
      - loki_data:/loki
    ports:
      - "3100:3100"
    networks:
      - monitoring

  promtail:
    image: grafana/promtail:3.1
    command: -config.file=/etc/promtail/promtail-config.yaml
    volumes:
      - ./promtail-config.yaml:/etc/promtail/promtail-config.yaml
      - /var/log/:/var/log/:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
    networks:
      - monitoring
```

---

## 3. Configuration Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'eva'
    env: 'production'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets:
          - 'node-exporter:9100'
          - '192.168.1.10:9100'  # Serveur distant

  - job_name: 'docker'
    static_configs:
      - targets: ['host.docker.internal:9323']  # Docker Engine metrics

  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  - job_name: 'nginx'
    static_configs:
      - targets: ['192.168.1.10:9113']  # nginx-exporter

  - job_name: 'postgres'
    static_configs:
      - targets: ['192.168.1.20:9187']  # postgres-exporter

  - job_name: 'api-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['192.168.1.10:8000']
```

---

## 4. Règles d'Alerte

```yaml
# rules/alerts.yml
groups:
  - name: infrastructure
    interval: 30s
    rules:
      - alert: NodeDown
        expr: up{job="node"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Nœud {{ $labels.instance }} down"
          description: "Le nœud {{ $labels.instance }} est injoignable depuis 5 minutes."

      - alert: HighCPUUsage
        expr: 100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CPU > 90% sur {{ $labels.instance }}"
          description: "CPU à {{ $value | humanizePercentage }} depuis 10 min."

      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Mémoire > 90% sur {{ $labels.instance }}"

      - alert: DiskSpaceCritical
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Espace disque < 10% sur {{ $labels.instance }}"
          description: "{{ $value | humanizePercentage }} restant sur {{ $labels.mountpoint }}"

      - alert: HighDiskIO
        expr: rate(node_disk_io_time_seconds_total[5m]) > 0.5
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "I/O disque élevé sur {{ $labels.device }}"
          description: "Disque occupé à {{ $value | humanizePercentage }}"

  - name: applications
    interval: 15s
    rules:
      - alert: APIHighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="api-service"}[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API lente (p95 > 2s)"
          description: "Latence p95 à {{ $value }}s"

      - alert: APIErrorRate
        expr: rate(http_requests_total{job="api-service", status=~"5.."}[5m]) / rate(http_requests_total{job="api-service"}[5m]) * 100 > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Taux d'erreur API > 5%"
          description: "{{ $value | humanizePercentage }} d'erreurs 5xx"

      - alert: ServiceDown
        expr: up{job="api-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} down"

  - name: sre
    interval: 1m
    rules:
      - alert: HighBurnRate
        expr: |
          (1 - (rate(http_requests_total{status=~"2..|3.."}[1h]) / rate(http_requests_total[1h]))) * 100 > 0.1
          and on()
          (1 - (rate(http_requests_total{status=~"2..|3.."}[1h]) / rate(http_requests_total[1h]))) * 100 > 5 * 0.1
        for: 1h
        labels:
          severity: page
        annotations:
          summary: "Burn rate d'erreur > 5x le budget SLO"
```

---

## 5. Alertmanager

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/T00/B00/xxx'
  telegram_api_url: 'https://api.telegram.org'

route:
  receiver: 'default'
  group_by: [alertname, cluster, severity]
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h

  routes:
    - match:
        severity: critical
      receiver: 'critical'
      repeat_interval: 1h

    - match:
        severity: page
      receiver: 'pagerduty'

receivers:
  - name: 'default'
    telegram_configs:
      - bot_token: ${TELEGRAM_BOT_TOKEN}
        chat_id: ${TELEGRAM_CHAT_ID}
        parse_mode: HTML
        message: |
          <b>{{ .GroupLabels.alertname }}</b>
          Sévérité : {{ .CommonLabels.severity }}
          {{ range .Alerts }}
          • {{ .Annotations.summary }}
          {{ end }}

  - name: 'critical'
    slack_configs:
      - channel: '#alerts-critical'
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}'
        color: 'danger'

  - name: 'pagerduty'
    pagerduty_configs:
      - routing_key: ${PD_ROUTING_KEY}
        severity: critical
```

---

## 6. Dashboards Grafana (Datasources provisionnées)

```yaml
# grafana/datasources/datasource.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: "15s"

  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100

  - name: PostgreSQL
    type: postgres
    url: db:5432
    database: eva
    user: grafana
    secureJsonData:
      password: ${DB_PASSWORD}
    jsonData:
      sslmode: disable
```

### Exemple de dashboard JSON (Node Exporter Full)

```json
{
  "title": "Infrastructure - Nœud {{instance}}",
  "tags": ["infrastructure", "node-exporter"],
  "panels": [
    {
      "title": "CPU Usage",
      "type": "timeseries",
      "datasource": "Prometheus",
      "targets": [{
        "expr": "100 - (avg by(cpu)(rate(node_cpu_seconds_total{mode=\"idle\", instance=~\"$instance\"}[5m])) * 100)",
        "legendFormat": "CPU {{cpu}}"
      }]
    },
    {
      "title": "Memory",
      "type": "gauge",
      "targets": [{
        "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
      }],
      "options": {
        "minViz": 0,
        "maxViz": 100,
        "thresholds": [
          {"color": "green", "value": null},
          {"color": "orange", "value": 80},
          {"color": "red", "value": 90}
        ]
      }
    },
    {
      "title": "Disk Usage",
      "type": "table",
      "targets": [{
        "expr": "100 - (node_filesystem_avail_bytes{mountpoint!=\"\", instance=~\"$instance\"} / node_filesystem_size_bytes{mountpoint!=\"\"} * 100)",
        "legendFormat": "{{mountpoint}}"
      }]
    }
  ]
}
```

---

## 7. Loki & Promtail (Logs)

```yaml
# loki-config.yaml
auth_enabled: false
server:
  http_listen_port: 3100
  grpc_listen_port: 9095

common:
  path_prefix: /loki
  ring:
    kvstore:
      store: inmemory
  replication_factor: 1

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      schema: v13
      index:
        prefix: index_
        period: 24h
      object_store: filesystem

storage_config:
  tsdb_shipper:
    active_index_directory: /loki/index
    cache_location: /loki/cache
  filesystem:
    directory: /loki/chunks

compactor:
  working_directory: /loki/compactor
  retention_enabled: true
  retention_delete_delay: 2h

limits_config:
  retention_period: 90d
  ingestion_rate_mb: 10
```

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 9095

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: system
    static_configs:
      - targets: [localhost]
        labels:
          job: varlogs
          __path__: /var/log/*.log

  - job_name: docker
    pipeline_stages:
      - docker: {}
    static_configs:
      - targets: [localhost]
        labels:
          job: docker
          __path__: /var/lib/docker/containers/*/*-json.log
```

---

## 8. Pièges Courants

1. **Rétention trop courte :** 7 jours par défaut. En production, 30 jours minimum (`--storage.tsdb.retention.time=30d`).
2. **Trop de métriques cardinales :** Des labels comme `request_id` ou `user_email` explosent la cardinalité. Éviter les labels uniques.
3. **Sondes Alertmanager sans groupement :** 100 alertes par seconde pour un même incident submerge tout le monde. Grouper par `alertname`, `cluster`.
4. **Dashboard sans variables :** Un dashboard codé en dur pour un serveur ne sert à rien pour 50 serveurs. Ajouter des variables `$instance`, `$job`.
5. **Promtail lit tout Docker :** Sans filtrage, promtail ingère les logs de TOUS les conteneurs, même ceux non monitorés. Filtrer par label.
6. **Absence de scrape targets :** `promtool check config prometheus.yml` ne vérifie pas la résolution DNS. Tester avec `curl http://target:9090/metrics`.

---

## 9. SLO / SLI / SLA — Patterns SRE

```yaml
# Exemple : SLO 99.9% de disponibilité API sur 30 jours
groups:
  - name: slo
    rules:
      - record: job:slo_errors_total:ratio_rate1h
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[1h]))
          /
          sum(rate(http_requests_total[1h]))

      - record: job:slo_burn_rate
        expr: |
          job:slo_errors_total:ratio_rate1h / (1 - 0.999)

      - alert: SLOWarning
        expr: job:slo_burn_rate > 1
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Burn rate SLO > 1x (atteindra le budget en 30j)"
```

---

## 10. Checklist Production

- [ ] Rétention Prometheus configurée (≥30 jours)
- [ ] Règles d'alerte testées avec `promtool test rules rules/alerts.yml`
- [ ] Alertmanager avec groupement et répétition raisonnable
- [ ] Notifications configurées (Slack/Telegram/PagerDuty)
- [ ] Dashboards Grafana avec variables réutilisables ($instance, $job)
- [ ] Datasources provisionnées automatiquement
- [ ] Loki configuré avec rétention (≥90 jours)
- [ ] Promtail ne suit que les logs pertinents
- [ ] SLO définis et alertés (burn rate alerts)
- [ ] `promtool check config` intégré au CI