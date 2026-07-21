---
name: load-balancing-proxies
description: Guide complet des reverse proxies et load balancers — HAProxy, Nginx, Envoy Proxy, Traefik, équilibrage L4/L7, health checks, SSL termination, session persistence, blue-green deployment.
tags: [haproxy, nginx, envoy, traefik, load-balancing, reverse-proxy, ssl-termination, l4-l7, health-check, session-persistence]
---

# Load Balancing et Reverse Proxies

## Présentation

Guide complet des solutions de load balancing et reverse proxy : architecture, algorithmes de répartition, health checks, terminaison SSL, déploiement blue-green/canary, et performance.

### Architecture Globale

```
Internet
    |
    | DNS Round-Robin / Anycast
    v
+------------------------------------------+
|         Reverse Proxy / LB               |
|    HAProxy | Nginx | Envoy | Traefik     |
+------------------------------------------+
    |        |         |          |
    v        v         v          v
+------+ +------+ +------+ +------+
| App1 | | App2 | | App3 | | App4 |
+------+ +------+ +------+ +------+
    |        |         |          |
    +--------+---------+----------+
                     |
                    App Server Pool
```

---

## HAProxy — Le Standard du Load Balancing

### Installation

```bash
# Installation
sudo apt-get install haproxy
# ou source
wget https://www.haproxy.org/download/2.9/src/haproxy-2.9.9.tar.gz
tar xvf haproxy-*.tar.gz && cd haproxy-*/
make TARGET=linux-glibc USE_OPENSSL=1 USE_PCRE2=1 USE_SYSTEMD=1
sudo make install

# Vérifier version
haproxy -vv | head -5
```

### Configuration de Base

```haproxy
# /etc/haproxy/haproxy.cfg
global
    log /dev/log local0
    log /dev/log local1 notice
    chroot /var/lib/haproxy
    stats socket /run/haproxy/admin.sock mode 660 level admin
    stats timeout 30s
    user haproxy
    group haproxy
    daemon
    maxconn 65535
    tune.ssl.default-dh-param 2048
    ssl-default-bind-ciphersuites TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256
    ssl-default-bind-options no-sslv3 no-tlsv10 no-tlsv11

defaults
    log global
    mode http
    option httplog
    option dontlognull
    option http-server-close
    option forwardfor except 127.0.0.0/8
    option redispatch
    retries 3
    timeout http-request 10s
    timeout queue 1m
    timeout connect 5s
    timeout client 30s
    timeout server 30s
    timeout http-keep-alive 10s
    timeout check 10s
    maxconn 3000
    errorfile 400 /etc/haproxy/errors/400.http
    errorfile 403 /etc/haproxy/errors/403.http
    errorfile 500 /etc/haproxy/errors/500.http
    errorfile 502 /etc/haproxy/errors/502.http
    errorfile 503 /etc/haproxy/errors/503.http

# Frontend — point d'entrée
frontend web-frontend
    bind *:80
    bind *:443 ssl crt /etc/haproxy/certs/example.com.pem
    redirect scheme https if !{ ssl_fc }
    stats uri /haproxy?stats
    stats auth admin:password

    # ACLs et règles
    acl is_api path_beg -i /api/
    acl is_static path_end -i .jpg .png .css .js .ico .svg
    acl is_websocket hdr(Upgrade) -i websocket
    acl admin_net src 192.168.100.0/24

    # Routage
    use_backend api_servers if is_api
    use_backend static_servers if is_static
    use_backend ws_servers if is_websocket
    default_backend web_servers

    # Rate limiting
    stick-table type ip size 100k expire 30s store http_req_rate(10s)
    http-request track-sc0 src
    http-request deny deny_status 429 if { sc_http_req_rate(0) gt 100 }

    # Security headers
    http-response set-header X-Frame-Options SAMEORIGIN
    http-response set-header X-Content-Type-Options nosniff
    http-response set-header X-XSS-Protection "1; mode=block"
    http-response set-header Referrer-Policy strict-origin-when-cross-origin
    http-response set-header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"

# Backend — serveurs d'application
backend web_servers
    balance roundrobin
    option httpchk GET /health HTTP/1.1\r\nHost:\ example.com
    http-check expect status 200
    default-server inter 5s fall 3 rise 2

    server web1 10.0.1.10:8080 check weight 10
    server web2 10.0.1.11:8080 check weight 10
    server web3 10.0.1.12:8080 check weight 10 backup

    # Sticky session (cookie)
    cookie SERVERID insert indirect nocache
    server web1 10.0.1.10:8080 cookie w1 check
    server web2 10.0.1.11:8080 cookie w2 check

backend api_servers
    balance leastconn
    option httpchk GET /api/health HTTP/1.1\r\nHost:\ api.example.com
    http-check expect rstring OK
    timeout server 60s

    server api1 10.0.2.10:3000 check
    server api2 10.0.2.11:3000 check

backend static_servers
    balance source  # Persistence par IP source
    option httpchk HEAD /health
    server static1 10.0.3.10:80 check
    server static2 10.0.3.11:80 check

backend ws_servers
    mode http
    balance roundrobin
    option http-server-close
    timeout tunnel 3600s
    timeout client 3600s
    timeout server 3600s

    server ws1 10.0.4.10:8080 check
    server ws2 10.0.4.11:8080 check
```

### HAProxy — Statistiques et API

```bash
# Stats via socket
echo "show info" | socat /run/haproxy/admin.sock stdio
echo "show stat" | socat /run/haproxy/admin.sock stdio
echo "show pools" | socat /run/haproxy/admin.sock stdio

# Activer/Désactiver un serveur
echo "enable server web_servers/web1" | socat /run/haproxy/admin.sock stdio
echo "disable server web_servers/web2" | socat /run/haproxy/admin.sock stdio
echo "set weight web_servers/web1 50" | socat /run/haproxy/admin.sock stdio

# Drain (arrêt progressif)
echo "set server web_servers/web1 state drain" | socat /run/haproxy/admin.sock stdio

# Rate limiting dynamique
echo "clear table web-frontend" | socat /run/haproxy/admin.sock stdio

# Voir la configuration actuelle
echo "show acl" | socat /run/haproxy/admin.sock stdio
echo "show map" | socat /run/haproxy/admin.sock stdio

# API REST (stats socket en mode http)
# /etc/haproxy/haproxy.cfg
# stats socket /run/haproxy/admin.sock mode 660 level admin expose-experimental
curl -X POST --unix-socket /run/haproxy/admin.sock \
  -H "Content-Type: application/json" \
  -d '{"version": "2.9", "frontend": "web-frontend"}' \
  http://localhost/v2/version
```

### HAProxy — Algorithmes de Load Balancing

```haproxy
# Round Robin (par défaut) — distribution équitable
balance roundrobin

# Least Connections — au serveur le moins chargé
balance leastconn

# Source — persistance par hash IP source
balance source
hash-type consistent  # Consistent hashing (redistribution minimale)

# URI — persistance par URI
balance uri
hash-type consistent

# Param — persistance par paramètre URL
balance url_param userid

# HDR — persistance par en-tête HTTP
balance hdr(X-Session-ID)

# Random — distribution aléatoire (bon pour très grandes pools)
balance random

# First — remplit le premier serveur avant le second
balance first
```

### HAProxy — Blue-Green / Canary

```haproxy
# Déploiement Canary (5% du trafic vers nouvelle version)
backend web_servers
    balance roundrobin

    server web-v1-1 10.0.1.10:8080 check weight 95
    server web-v1-2 10.0.1.11:8080 check weight 95
    server web-v2-1 10.0.1.12:8080 check weight 5   # Canary 5%
    server web-v2-2 10.0.1.13:8080 check weight 5   # Canary 5%

# Canary par header (interne uniquement)
frontend web-frontend
    acl canary_header hdr(X-Canary) -i true
    use_backend web_v2 if canary_header
    default_backend web_v1

backend web_v1
    server web-v1 10.0.1.10:8080 check weight 100

backend web_v2
    server web-v2 10.0.1.20:8080 check weight 100

# Blue-Green (bascule totale)
# Activer en changeant le backend par défaut
# default_backend web-v2  # après validation
```

---

## Nginx — Reverse Proxy Polyvalent

### Configuration Base

```nginx
# /etc/nginx/nginx.conf
user nginx;
worker_processes auto;
worker_rlimit_nofile 65535;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 65535;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct=$upstream_connect_time '
                    'uht=$upstream_header_time urt=$upstream_response_time';
    access_log /var/log/nginx/access.log main buffer=512k flush=1m;

    # Performances
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 1000;
    client_max_body_size 100m;
    server_tokens off;
    types_hash_max_size 2048;

    # Buffer
    client_body_buffer_size 128k;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;
    output_buffers 32 32k;
    postpone_output 1460;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_min_length 1000;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml+rss image/svg+xml;

    # Upstreams (backends)
    upstream web_backend {
        #least_conn;  # Ou round-robin (par défaut)
        #ip_hash;     # Persistence par IP

        server 10.0.1.10:8080 weight=10 max_fails=3 fail_timeout=30s;
        server 10.0.1.11:8080 weight=10 max_fails=3 fail_timeout=30s;
        server 10.0.1.12:8080 backup;
        keepalive 32;
    }

    upstream api_backend {
        least_conn;
        server 10.0.2.10:3000;
        server 10.0.2.11:3000;
        keepalive 32;
    }

    # Server HTTP → HTTPS redirect
    server {
        listen 80;
        listen [::]:80;
        server_name example.com www.example.com;
        return 301 https://$server_name$request_uri;
    }

    # Server HTTPS
    server {
        listen 443 ssl http2;
        listen [::]:443 ssl http2;
        server_name example.com www.example.com;

        # TLS
        ssl_certificate /etc/nginx/certs/example.com.pem;
        ssl_certificate_key /etc/nginx/certs/example.com-key.pem;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_session_tickets off;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_stapling on;
        ssl_stapling_verify on;
        resolver 1.1.1.1 8.8.8.8 valid=300s;
        resolver_timeout 5s;

        # HSTS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;

        # Security headers
        add_header X-Frame-Options SAMEORIGIN always;
        add_header X-Content-Type-Options nosniff always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy strict-origin-when-cross-origin always;

        # Root location
        location / {
            proxy_pass http://web_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_read_timeout 30s;
            proxy_send_timeout 30s;
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 16k;
            proxy_busy_buffers_size 32k;
        }

        # API — timeout plus long
        location /api/ {
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 120s;
            proxy_send_timeout 120s;
        }

        # Statique — cache long
        location /static/ {
            root /var/www;
            expires 365d;
            add_header Cache-Control "public, immutable";
        }

        # Health check pour le load balancer
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }

        # Nginx status
        location /nginx_status {
            stub_status;
            access_log off;
            allow 127.0.0.1;
            deny all;
        }
    }
}
```

### Nginx — Rate Limiting

```nginx
# /etc/nginx/conf.d/rate-limit.conf

# Zones de rate limiting
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
limit_req_zone $binary_remote_addr zone=static:10m rate=1000r/s;
limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;

# Limiter connexions simultanées
limit_conn conn_per_ip 10;

# Limiter requêtes login
location /login {
    limit_req zone=login burst=3 nodelay;
    proxy_pass http://web_backend;
}

# Limiter requêtes API
location /api/ {
    limit_req zone=api burst=20 nodelay;
    limit_conn conn_per_ip 5;
    proxy_pass http://api_backend;
}
```

### Nginx — Load Balancing Avancé

```nginx
# Weighted load balancing
upstream backend {
    server 10.0.1.10 weight=5;
    server 10.0.1.11 weight=3;
    server 10.0.1.12 weight=1;
}

# Least connections
upstream backend_least {
    least_conn;
    server 10.0.1.10;
    server 10.0.1.11;
}

# IP hash (persistence)
upstream backend_ip_hash {
    ip_hash;
    server 10.0.1.10;
    server 10.0.1.11;
}

# Generic hash
upstream backend_hash {
    hash $request_uri consistent;
    server 10.0.1.10;
    server 10.0.1.11;
}

# Random with fallback
upstream backend_random {
    random two least_time=header;
    server 10.0.1.10;
    server 10.0.1.11;
    server 10.0.1.12 backup;
}

# Active health checks (nginx plus)
upstream backend_health {
    zone backend 64k;
    server 10.0.1.10;
    server 10.0.1.11;

    health_check interval=5s fails=3 passes=2 uri=/health;
    health_check_timeout 3s;
}

# Slow start (pour éviter le surge)
upstream backend_slowstart {
    server 10.0.1.10 slow_start=30s;
    server 10.0.1.11 slow_start=30s;
}
```

---

## Envoy Proxy — Proxy Cloud-Native

### Configuration de Base

```yaml
# /etc/envoy/envoy.yaml
admin:
  address:
    socket_address:
      address: 0.0.0.0
      port_value: 9901
  access_log_path: /var/log/envoy/admin.log

static_resources:
  listeners:
    # Listener HTTP
    - name: listener_http
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 80
      filter_chains:
        - filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_http
                codec_type: AUTO
                route_config:
                  name: local_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/api/"
                          route:
                            cluster: api_service
                            timeout: 60s
                        - match:
                            prefix: "/"
                          route:
                            cluster: web_service
                            timeout: 30s
                http_filters:
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

    # Listener HTTPS
    - name: listener_https
      address:
        socket_address:
          address: 0.0.0.0
          port_value: 443
      filter_chains:
        - transport_socket:
            name: envoy.transport_sockets.tls
            typed_config:
              "@type": type.googleapis.com/envoy.extensions.transport_sockets.tls.v3.DownstreamTlsContext
              common_tls_context:
                tls_certificates:
                  - certificate_chain:
                      filename: /etc/envoy/certs/example.com.pem
                    private_key:
                      filename: /etc/envoy/certs/example.com-key.pem
          filters:
            - name: envoy.filters.network.http_connection_manager
              typed_config:
                "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                stat_prefix: ingress_https
                route_config:
                  name: https_route
                  virtual_hosts:
                    - name: backend
                      domains: ["*"]
                      routes:
                        - match:
                            prefix: "/"
                          route:
                            cluster: web_service
                http_filters:
                  - name: envoy.filters.http.router
                    typed_config:
                      "@type": type.googleapis.com/envoy.extensions.filters.http.router.v3.Router

  clusters:
    - name: web_service
      connect_timeout: 5s
      type: STRICT_DNS
      dns_lookup_family: V4_ONLY
      lb_policy: LEAST_REQUEST
      load_assignment:
        cluster_name: web_service
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: web1.example.com
                      port_value: 8080
              - endpoint:
                  address:
                    socket_address:
                      address: web2.example.com
                      port_value: 8080
      health_checks:
        - timeout: 2s
          interval: 5s
          unhealthy_threshold: 3
          healthy_threshold: 2
          http_health_check:
            path: /health
            expected_statuses:
              - start: 200
                end: 200

    - name: api_service
      connect_timeout: 5s
      type: STRICT_DNS
      lb_policy: ROUND_ROBIN
      load_assignment:
        cluster_name: api_service
        endpoints:
          - lb_endpoints:
              - endpoint:
                  address:
                    socket_address:
                      address: api1.example.com
                      port_value: 3000
              - endpoint:
                  address:
                    socket_address:
                      address: api2.example.com
                      port_value: 3000
```

### Envoy — Circuit Breaking

```yaml
clusters:
  - name: api_service
    circuit_breakers:
      thresholds:
        - priority: DEFAULT
          max_connections: 1000
          max_pending_requests: 100
          max_requests: 1000
          max_retries: 3
        - priority: HIGH
          max_connections: 500
          max_pending_requests: 50
          max_requests: 500
          max_retries: 1
```

### Envoy — Retry et Timeout

```yaml
routes:
  - match:
      prefix: "/api/"
    route:
      cluster: api_service
      timeout: 30s
      retry_policy:
        retry_on: "5xx,gateway-error,connect-failure,refused-stream"
        num_retries: 3
        retry_host_predicate:
          - name: envoy.retry_host_predicates.previous_hosts
        host_selection_retry_max_attempts: 3
        retry_back_off:
          base_interval: 0.25s
          max_interval: 3s
```

---

## Traefik — Reverse Proxy Moderne (Cloud-Native)

### Configuration de Base

```yaml
# traefik.yml
api:
  dashboard: true
  insecure: true

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entrypoint:
          to: websecure
          scheme: https
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
  file:
    directory: /etc/traefik/dynamic
    watch: true

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@example.com
      storage: /acme.json
      httpChallenge:
        entryPoint: web
```

```yml
# dynamic/routers.yml
# Routeurs HTTP
http:
  routers:
    api:
      rule: "Host(`api.example.com`)"
      entryPoints:
        - websecure
      service: api-service
      tls:
        certResolver: letsencrypt
      middlewares:
        - rate-limit
        - security-headers

    web:
      rule: "Host(`example.com`) || Host(`www.example.com`)"
      entryPoints:
        - websecure
      service: web-service
      tls:
        certResolver: letsencrypt

  services:
    web-service:
      loadBalancer:
        servers:
          - url: "http://10.0.1.10:8080"
          - url: "http://10.0.1.11:8080"
        healthCheck:
          path: /health
          interval: 5s
          timeout: 3s
        passHostHeader: true

    api-service:
      loadBalancer:
        servers:
          - url: "http://10.0.2.10:3000"
          - url: "http://10.0.2.11:3000"
        healthCheck:
          path: /api/health

  middlewares:
    rate-limit:
      rateLimit:
        average: 100
        burst: 50

    security-headers:
      headers:
        frameDeny: true
        contentTypeNosniff: true
        browserXssFilter: true
        customFrameOptionsValue: SAMEORIGIN
        referrerPolicy: strict-origin-when-cross-origin
        strictTransportSecurity:
          maxAge: 31536000
          includeSubDomains: true

    circuit-breaker:
      circuitBreaker:
        expression: "NetworkErrorRatio() > 0.5 || LatencyAtQuantileMS(50.0) > 100"
```

### Traefik — Docker Labels

```yaml
# docker-compose.yml
services:
  app:
    image: myapp:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.app.rule=Host(`app.example.com`)"
      - "traefik.http.routers.app.entrypoints=websecure"
      - "traefik.http.routers.app.tls.certresolver=letsencrypt"
      - "traefik.http.services.app.loadbalancer.server.port=8080"
      - "traefik.http.services.app.loadbalancer.healthcheck.path=/health"
```

---

## SSL/TLS Termination

### Certificats HAProxy

```bash
# Créer un PEM combiné (certificat + clé)
cat fullchain.pem privkey.pem > /etc/haproxy/certs/example.com.pem
chmod 600 /etc/haproxy/certs/example.com.pem

# Let's Encrypt avec certbot
certbot certonly --standalone -d example.com -d www.example.com
cat /etc/letsencrypt/live/example.com/fullchain.pem \
    /etc/letsencrypt/live/example.com/privkey.pem \
    > /etc/haproxy/certs/example.com.pem

# Auto-renewal hook
# /etc/letsencrypt/renewal-hooks/deploy/haproxy.sh
#!/bin/bash
for domain in "$@"; do
    cat /etc/letsencrypt/live/$domain/fullchain.pem \
        /etc/letsencrypt/live/$domain/privkey.pem \
        > /etc/haproxy/certs/$domain.pem
done
systemctl reload haproxy
```

### HAProxy — Mutual TLS

```haproxy
frontend mtls-frontend
    bind *:8443 ssl crt /etc/haproxy/certs/server.pem \
         verify required ca-file /etc/haproxy/certs/ca.crt \
         crl-file /etc/haproxy/certs/crl.pem
    http-request deny unless { ssl_c_verify 0 }  # Verify = SUCCESS
    default_backend api_servers
```

---

## Pièges et Bonnes Pratiques

- **Health checks** : Toujours configurer avec `inter 5s fall 3 rise 2` minimum
- **Timeouts** : Adapter selon l'application (API 60s, WebSocket 3600s, static 10s)
- **Logging** : Logguer les temps de réponse upstream (rt=, urt=)
- **Buffer tuning** : Ajuster les buffers selon le trafic (128k pour body, 4k pour headers)
- **Sticky sessions** : Préférer les cookies aux hash IP (les IPs changent avec le mobile)
- **Backup servers** : Toujours avoir un serveur `backup` pour les pannes
- **Graceful shutdown** : Utiliser `drain` avant `disable` pour arrêts progressifs
- **Monitoring** : Exposer les métriques (Prometheus endpoint) et dashboards Grafana
- **Blue-Green** : Tester en canary (5%) avant bascule complète

## Ressources

- HAProxy : https://www.haproxy.org/documentation/
- Nginx LB : https://docs.nginx.com/nginx/admin-guide/load-balancer/
- Envoy Proxy : https://www.envoyproxy.io/docs
- Traefik : https://doc.traefik.io/traefik/
- Let's Encrypt : https://letsencrypt.org/docs/
- SSL Labs : https://www.ssllabs.com/ssltest/