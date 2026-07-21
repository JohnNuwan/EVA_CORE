---
name: zero-trust-architecture
description: Guide complet d'architecture Zero Trust (ZTNA, BeyondCorp) — micro-segmentation, identity-aware proxy, policy enforcement, et déploiement sur The Hive.
domain: [cybersecurite, reseau, architecture]
tags: [zero-trust, ztna, beyondcorp, micro-segmentation, iam, policy, network-securite]
priority: haute
---

# 🏰 Architecture Zero Trust — ZTNA, BeyondCorp, Micro-Segmentation

Guide de déploiement d'une architecture Zero Trust pour The Hive et services auto-hébergés.  
Couvre : principes ZT, proxy-aware identity, BeyondCorp-like, micro-segmentation, et bouclage avec les solutions existantes.

---

## 1. Principes Fondamentaux du Zero Trust

### 1.1 Les 7 Piliers

```
┌──────────────────────────────────────────────┐
│              ZERO TRUST                       │
├──────────────────────────────────────────────┤
│ 1. Vérifier explicitement — tout, tout le temps│
│ 2. Accès au moindre privilège                  │
│ 3. Assumer la brèche (Assume Breach)           │
│ 4. Micro-segmentation du réseau                │
│ 5. Identity est le nouveau périmètre           │
│ 6. Inspection continue du trafic               │
│ 7. Automatisation de la réponse                │
└──────────────────────────────────────────────┘
```

### 1.2 État Actuel de The Hive

| Zone | Actuel | Cible Zero Trust |
|------|--------|------------------|
| Réseau | 192.168.1.0/24, pas de segmentation | Micro-segmentation par service |
| Accès | IP-based, pas de vérification d'identité | Identity-aware proxy |
| Services | Exposés sur 0.0.0.0:PORT | Proxy inverse + auth |
| VPN | WireGuard (réseau plat) | WireGuard + auth applicative |
| Monitoring | Dashboard public | Authentification + audit |

---

## 2. Identity-Aware Proxy (IAP)

### 2.1 Architecture au-dessus de The Hive

```
Utilisateur → WireGuard Tunnel → nginx (IAP) → Auth → Service Interne
                                  │
                                  ├── Auth via OAuth2 Proxy
                                  ├── Auth via Authelia
                                  └── Auth via Cloudflare Access
```

### 2.2 OAuth2 Proxy (Google/Azure/Github)

```yaml
# docker-compose.yml — OAuth2 Proxy
services:
  oauth2-proxy:
    image: quay.io/oauth2-proxy/oauth2-proxy:latest
    container_name: oauth2-proxy
    restart: unless-stopped
    ports:
      - "127.0.0.1:4180:4180"   # ← Localhost uniquement
    environment:
      OAUTH2_PROXY_CLIENT_ID: "${OAUTH_CLIENT_ID}"
      OAUTH2_PROXY_CLIENT_SECRET: "${OAUTH_CLIENT_SECRET}"
      OAUTH2_PROXY_COOKIE_SECRET: "${OAUTH_COOKIE_SECRET}"
      OAUTH2_PROXY_COOKIE_SECURE: "true"
      OAUTH2_PROXY_HTTP_ADDRESS: "0.0.0.0:4180"
      OAUTH2_PROXY_UPSTREAMS: "http://app:8080"
      OAUTH2_PROXY_EMAIL_DOMAINS: "*"
      OAUTH2_PROXY_PROVIDER: "google"
      OAUTH2_PROXY_PASS_AUTHORIZATION_HEADER: "true"
    networks:
      - private
```

### 2.3 Authelia (Self-Hosted SSO)

```yaml
# docker-compose.yml — Authelia
services:
  authelia:
    image: authelia/authelia:latest
    container_name: authelia
    restart: unless-stopped
    ports:
      - "127.0.0.1:9091:9091"
    volumes:
      - ./authelia/config:/config
    environment:
      TZ: Europe/Paris
    networks:
      - private
```

Configuration :
```yaml
# authelia/config/configuration.yml
host: 0.0.0.0
port: 9091
theme: dark

log:
  level: info

totp:
  issuer: thehive.lan
  period: 30
  skew: 1

authentication_backend:
  file:
    path: /config/users.yml

access_control:
  default_policy: deny
  rules:
    - domain: "grafana.thehive.lan"
      policy: one_factor
    - domain: "vllm.thehive.lan"
      policy: two_factor
      subject: ["user:aza"]
    - domain: "dashboard.thehive.lan"
      policy: one_factor
```

### 2.4 Cloudflare Zero Trust (Tunnel)

```bash
# Installer cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Configurer le tunnel
cloudflared tunnel login
cloudflared tunnel create the-hive

# Configurer le tunnel
cat > ~/.cloudflared/config.yml << 'EOF'
tunnel: the-hive
credentials-file: /home/aza/.cloudflared/the-hive.json

ingress:
  - hostname: grafana.thehive.domain.com
    service: http://localhost:3000
  - hostname: vllm.thehive.domain.com
    service: http://localhost:8001
  - hostname: dashboard.thehive.domain.com
    service: http://localhost:8081
  - service: http_status:404
EOF

# Démarrer le tunnel (service systemd)
cloudflared service install
```

---

## 3. Micro-Segmentation Réseau

### 3.1 Plan de Segmentation pour The Hive

```
┌─────────────────────────────────────────────────┐
│                ROUTEUR (192.168.1.1)             │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          │   WireGuard (51820)  │ VLAN VPN
          └──────────┬──────────┘
                     │
          ┌──────────┴──────────┐
          │   nginx Proxy        │ VLAN DMZ
          │   (80, 443, 4180)    │
          └──────────┬──────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
   VLAN APP     VLAN DATA    VLAN GPU
   - vLLM        - Minio      - Entraînement
   - Grafana     - Wiki       - ComfyUI
   - Dashboard   - Portainer
```

### 3.2 Segmentation avec iptables

```bash
#!/bin/bash
# segment-network.sh — Segmentation Zero Trust

# VLAN / Sous-réseaux
DMZ_SUBNET="10.0.1.0/24"        # Proxy, Auth
APP_SUBNET="10.0.2.0/24"        # Applications
DATA_SUBNET="10.0.3.0/24"       # Base de données, Stockage
GPU_SUBNET="10.0.4.0/24"        # GPU / Calcul

# Créer les bridges
ip link add dmz type bridge
ip link add app type bridge
ip link add data type bridge
ip link add gpu type bridge

# VLAN tagging sur l'interface physique (si switch supporte)
ip link add link eth0 name eth0.100 type vlan id 100  # DMZ
ip link add link eth0 name eth0.200 type vlan id 200  # APP
ip link add link eth0 name eth0.300 type vlan id 300  # DATA

# Règles iptables — Inter-VLAN strict
iptables -A FORWARD -i dmz -o app -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -i app -o data -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -i app -o gpu -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -i data -o app -j DROP         # Pas de sortie data → app
iptables -A FORWARD -i gpu -o dmz -j DROP          # Pas de sortie GPU → DMZ
```

### 3.3 Docker Network Segmentation

```yaml
# docker-compose.yml — Réseaux isolés
networks:
  dmz:
    driver: bridge
    ipam:
      config:
        - subnet: "10.0.1.0/24"
  app:
    driver: bridge
    ipam:
      config:
        - subnet: "10.0.2.0/24"
  data:
    driver: bridge
    ipam:
      config:
        - subnet: "10.0.3.0/24"
    internal: true     # ← Pas d'accès internet

services:
  nginx-proxy:
    networks:
      dmz:
        aliases:
          - proxy
    ports:
      - "127.0.0.1:80:80"
      - "127.0.0.1:443:443"
  
  grafana:
    networks:
      app:
      dmz:    # Accès limité pour le proxy
  
  minio:
    networks:
      data:
    volumes:
      - minio_data:/data
      
  vllm:
    networks:
      app:
      gpu:
  
  ollama:
    networks:
      gpu:
```

---

## 4. Identity & Access Management

### 4.1 OPA (Open Policy Agent)

```rego
# policy/authz.rego — Politique d'accès
package authz

import future.keywords.if

# Règle par défaut : refuser
default allow = false

# Accès admin uniquement depuis le VPN
allow if {
    input.user == "aza"
    input.source_ip == "10.0.0.0/8"
    input.action == "admin"
}

# Accès API avec clé valide
allow if {
    input.path =~ "^/api/v1/"
    input.method in ["GET", "POST"]
    input.api_key == data.valid_keys[_]
}

# Accès lecture seul pour les dashboards
allow if {
    input.path =~ "^/grafana/"
    input.method == "GET"
    input.group == "viewer"
}

# Bloquer les requêtes sans User-Agent
deny["missing_user_agent"] {
    not input.headers["User-Agent"]
}
```

### 4.2 OIDC avec Keycloak

```yaml
services:
  keycloak:
    image: quay.io/keycloak/keycloak:latest
    container_name: keycloak
    environment:
      KC_HOSTNAME: auth.thehive.lan
      KC_HTTP_PORT: 8080
      KC_HTTPS_PORT: 8443
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: ${KEYCLOAK_PASSWORD}
    command:
      - start-dev
      - --import-realm
    volumes:
      - ./keycloak/realm-export.json:/opt/keycloak/data/import/realm.json
    ports:
      - "127.0.0.1:8080:8080"
```

---

## 5. Assume Breach — Détection & Réponse

### 5.1 Audit Logs Centralisé

```yaml
services:
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "127.0.0.1:3100:3100"
    volumes:
      - ./loki:/etc/loki
    command: -config.file=/etc/loki/loki-config.yaml

  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      - /var/log:/var/log
      - /home/aza/.hermes/logs:/hermes/logs
      - ./promtail/promtail-config.yaml:/etc/promtail/config.yaml
    command: -config.file=/etc/promtail/config.yaml
```

### 5.2 Alerting Zero Trust

```yaml
# Règles Prometheus pour ZT
groups:
  - name: zero-trust-alerts
    rules:
      - alert: AccèsNonAuthorisé
        expr: rate(nginx_http_requests_total{status="401"}[5m]) > 10
        for: 1m
        annotations:
          summary: "Tentatives d'accès non autorisé"
      
      - alert: ConnexionInterVLANBloquée
        expr: rate(iptables_dropped_packets_total[5m]) > 0
        for: 1m
        annotations:
          summary: "Trafic inter-VLAN bloqué"
      
      - alert: NouveauProcessusSuspect
        expr: changes(process_count[1h]) > 20
        for: 5m
        annotations:
          summary: "Pic de nouveaux processus détecté"
      
      - alert: ConnexionSortanteInhabituelle
        expr: rate(node_network_transmit_bytes_total{destination!~"192.168.*|10.0.*"}[5m]) > 1e7
        for: 1m
        annotations:
          summary: "Trafic sortant inhabituel vers l'extérieur"
```

---

## 6. Mise en Œuvre sur The Hive

### 6.1 Plan de Migration

| Phase | Action | Durée |
|-------|--------|-------|
| **Phase 1** | Pare-feu + restriction 127.0.0.1 | 1 jour |
| **Phase 2** | WireGuard VPN + nginx proxy | 2 jours |
| **Phase 3** | OAuth2 Proxy ou Authelia | 3 jours |
| **Phase 4** | Micro-segmentation Docker | 1 semaine |
| **Phase 5** | Audit logs + alerting ZT | 1 semaine |
| **Phase 6** | OPA / Keycloak SSO | 2 semaines |

### 6.2 nginx as ZT Gateway

```nginx
# /etc/nginx/sites-available/the-hive
server {
    listen 127.0.0.1:443 ssl;
    server_name grafana.thehive.lan;
    
    ssl_certificate /etc/nginx/ssl/thehive.crt;
    ssl_certificate_key /etc/nginx/ssl/thehive.key;
    
    # Auth via OAuth2 Proxy
    auth_request /oauth2/auth;
    error_page 401 = /oauth2/sign_in;
    
    # En-têtes de sécurité
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000" always;
    
    # Proxy vers Grafana
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # OAuth2 endpoint
    location /oauth2/ {
        proxy_pass http://127.0.0.1:4180;
        proxy_set_header Host $host;
    }
}

# Portainer — auth basique + VPN only
server {
    listen 127.0.0.1:9444 ssl;
    server_name portainer.thehive.lan;
    
    allow 10.0.0.0/8;   # VPN only
    allow 192.168.1.0/24;
    deny all;
    
    # Auth HTTP basique + mdp
    auth_basic "Portainer Admin";
    auth_basic_user_file /etc/nginx/.htpasswd;
    
    location / {
        proxy_pass https://127.0.0.1:9443;
    }
}
```

---

## 7. Vérification de la Posture ZT

### 7.1 Script d'Audit

```bash
#!/bin/bash
# zt-audit.sh — Audit de conformité Zero Trust

SCORE=0
TOTAL=20

echo "═══ Zero Trust Audit — The Hive ═══"
echo

# 1. Services exposés ?
echo -n "[1] Services sur 0.0.0.0... "
EXPOSED=$(ss -tlnp | grep "0.0.0.0:" | wc -l)
if [ "$EXPOSED" -le 2 ]; then
    echo "✅ ($EXPOSED services)"
    SCORE=$((SCORE + 1))
else
    echo "❌ ($EXPOSED services — trop!)"
fi

# 2. Pare-feu actif ?
echo -n "[2] iptables rules... "
if iptables -L -n 2>/dev/null | grep -q "DROP"; then
    echo "✅" && SCORE=$((SCORE + 1))
else
    echo "❌"
fi

# 3. Auth sur dashboard ?
echo -n "[3] Dashboard auth... "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8081/ | grep -q 401; then
    echo "✅" && SCORE=$((SCORE + 1))
else
    echo "❌ (pas d'auth)"
fi

# 4. WireGuard actif ?
echo -n "[4] WireGuard tunnel... "
if ip link show wg0 2>/dev/null | grep -q "UP"; then
    echo "✅" && SCORE=$((SCORE + 1))
else
    echo "⚠️ (non actif)"
fi

echo
echo "═══ Score ZT: $SCORE/$TOTAL ═══"
echo "Sévérité: $( [ $SCORE -lt 5 ] && echo 'CRITIQUE' || [ $SCORE -lt 10 ] && echo 'ÉLEVÉE' || [ $SCORE -lt 15 ] && echo 'MOYENNE' || echo 'BONNE' )"
```

### 7.2 Métriques Clés

| Métrique | Cible | État The Hive |
|----------|-------|---------------|
| Services sur 0.0.0.0 | ≤ 2 | **18** ❌ |
| Pare-feu actif | Oui | **Non** ❌ |
| Auth sur tous les services | Oui | **Non** ❌ |
| Micro-segmentation | Oui | **Non** ❌ |
| Audit logs centralisé | Oui | Partiel ⚠️ |
| Rotation des secrets | 90 jours | **Non** ❌ |
| VPN/WireGuard | Oui | **Oui** ✅ |

---

## Pitfalls

- **Ne PAS** confondre VPN et Zero Trust — WireGuard ne remplace pas l'auth applicative
- **Ne PAS** exposer Authelia/Keycloak sur 0.0.0.0 — utiliser nginx en reverse proxy
- **Ne PAS** segmenter sans tester les dépendances inter-services
- **TOUJOURS** vérifier que le proxy OAuth2 n'introduit pas de bypass
- **TOUJOURS** ajouter des rate limits sur les endpoints d'auth
- La micro-segmentation augmente la complexité — documenter chaque règle
- Les tokens OAuth short-lived (15 min) sont meilleurs que les long-lived (30+ jours)
- Ne pas oublier de protéger les endpoints d'API avec les mêmes règles que les endpoints humains