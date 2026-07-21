---
name: docker-avance
description: "Conteneurisation avancée avec Docker — multi-stage builds, réseaux overlay, volumes, registries privés, sécurité d'images, Docker Compose production, debugging de conteneurs"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [docker, conteneurisation, multi-stage, docker-compose, registry, sécurité, volumes, réseaux]
    related_skills: [kubernetes-avance, ci-cd-pipelines, gitops-argocd]
---

# Docker — Conteneurisation Avancée

## Vue d'ensemble

Docker est la plateforme standard de conteneurisation Linux. Cette compétence couvre la construction d'images optimisées (multi-stage, distroless), la gestion des réseaux et volumes, les registres privés, la sécurité des conteneurs, le debugging avancé et les patterns Docker Compose pour la production.

## Quand l'utiliser

- Optimiser la taille et la sécurité d'une image Docker
- Configurer des réseaux multi-conteneurs complexes
- Gérer des volumes persistants avec drivers avancés
- Mettre en place un registre privé (Harbor, Docker Registry)
- Analyser une image pour vulnérabilités
- Debugger un conteneur qui crash au démarrage
- Orchestrer des stacks multi-services avec Docker Compose

---

## 1. Multi-stage Builds Optimisés

### Python — trois étapes

```dockerfile
# STAGE 1 : Dépendances de build
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# STAGE 2 : Test & lint
FROM builder AS tester
COPY . .
RUN pip install ruff pytest && \
    ruff check . && \
    pytest --cov=app tests/

# STAGE 3 : Runtime ultra-léger
FROM python:3.12-alpine AS runner
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=tester /app /app
ENV PATH=/root/.local/bin:$PATH
RUN adduser -D -u 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Go — image distroless (sans OS)

```dockerfile
FROM golang:1.23-alpine AS builder
WORKDIR /src
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /app/server ./cmd/

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /app/server /server
USER 65532:65532
EXPOSE 8080
CMD ["/server"]
```

**Résultat :** Image Go de ~15 Mo (vs ~800 Mo avec golang:1.23).

---

## 2. Réseaux Docker Avancés

```bash
# Créer un réseau overlay pour Swarm
docker network create \
  --driver overlay \
  --attachable \
  --subnet 10.0.50.0/24 \
  --gateway 10.0.50.1 \
  eva-overlay

# Isoler un stack avec son propre réseau
docker network create \
  --driver bridge \
  --internal \
  --subnet 172.20.0.0/24 \
  eva-internal

# Connecter un conteneur à plusieurs réseaux
docker run --network eva-internal --network eva-overlay --name api nginx

# Inspecter le traffic réseau d'un conteneur
docker exec -t api tcpdump -i eth0 port 80
```

### Docker Compose — réseaux isolés

```yaml
version: "3.8"

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # Pas d'accès Internet

services:
  nginx:
    image: nginx:alpine
    networks:
      - frontend
      - backend
    ports:
      - "443:443"

  api:
    image: api:latest
    networks:
      - backend
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    networks:
      - backend
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

---

## 3. Volumes & Stockage

### Drivers de volume avancés

```bash
# NFS (partagé entre nœuds)
docker volume create \
  --driver local \
  --opt type=nfs \
  --opt o=addr=192.168.1.100,rw,nfsvers=4 \
  --opt device=:/exports/data \
  eva-nfs-volume

# tmpfs (RAM, données volatiles)
docker run --tmpfs /app/cache:rw,noexec,nosuid,size=512m alpine

# Bind mount avec options SELinux
docker run -v /host/data:/container/data:z,ro alpine
```

### Backup de volumes

```bash
# Backup d'un volume vers une archive
docker run --rm -v eva-data:/source -v $(pwd):/backup alpine \
  tar czf /backup/eva-data-$(date +%Y%m%d).tar.gz -C /source .
```

---

## 4. Registre Privé

```yaml
# docker-compose.yml pour Harbor alternatif (Docker Registry + UI)
version: "3.8"

services:
  registry:
    image: registry:2.8
    environment:
      REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /data
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
    volumes:
      - registry-data:/data
      - ./auth:/auth
    ports:
      - "5000:5000"

  ui:
    image: joxit/docker-registry-ui:latest
    environment:
      REGISTRY_TITLE: "EVA Registry"
      REGISTRY_URL: http://registry:5000
      DELETE_IMAGES_ENABLED: true
    ports:
      - "8080:80"

volumes:
  registry-data:
```

```bash
# Authentification
docker login registry.eva.local:5000

# Push avec tag versionné
docker tag api:latest registry.eva.local:5000/api:1.2.3
docker push registry.eva.local:5000/api:1.2.3

# Nettoyage des vieux tags (garbage collection)
docker exec registry bin/registry garbage-collect /etc/docker/registry/config.yml
```

---

## 5. Sécurité des Images

### Scan de vulnérabilités

```bash
# Trivy (recommandé — rapide, pas de daemon)
trivy image registry.eva.local/api:1.2.3
trivy image --severity CRITICAL,HIGH --format sarif python:3.12-slim

# Docker Scout (nécessite Docker Desktop)
docker scout quickview nginx:alpine

# Analyse SBOM
docker sbom api:latest > sbom.spdx.json
```

### Bonnes pratiques Dockerfile

```dockerfile
# MAUVAIS — tout en root, secrets exposés
FROM node:20
RUN npm install
COPY . .
EXPOSE 3000
CMD ["node", "app.js"]

# BON — utilisateur non-root, sans cache, multi-stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .

FROM node:20-alpine
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY --from=builder /app /app
RUN chown -R appuser:appgroup /app
USER appuser
EXPOSE 3000
CMD ["node", "app.js"]
```

### Docker Bench Security (audit CIS)

```bash
docker run --rm --net host --pid host --userns host \
  --cap-add audit_control \
  -e DOCKER_CONTENT_TRUST=$DOCKER_CONTENT_TRUST \
  -v /var/lib:/var/lib \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /etc:/etc \
  docker/docker-bench-security
```

---

## 6. Debugging Avancé

```bash
# Voir les processus du conteneur
docker top <container>

# Inspecter l'utilisation des ressources
docker stats --no-stream <container>
docker stats <container>  # Live

# Entrer dans un conteneur qui crash (pas de shell)
docker export <container> | tar tf - | head -20
docker cp <container>:/app/config.yaml ./backup.yaml

# nsenter (sans exec — besoin des PID)
docker inspect -f '{{.State.Pid}}' <container>
sudo nsenter -t <PID> -n -- ip addr

# Logs avec timestamps et filtrage
docker logs -f --tail=100 --timestamps <container> 2>&1
docker logs <container> 2>&1 | jq 'select(.level == "ERROR")'

# Analyse de l'espace disque
docker system df -v
docker buildx du
```

---

## 7. Docker Compose Avancé (patterns production)

```yaml
version: "3.8"

x-logging: &default-logging
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"

x-healthcheck: &healthcheck
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s

services:
  app:
    image: eva/app:${APP_VERSION:-latest}
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      <<: *healthcheck
      test: ["CMD", "wget", "--spider", "http://localhost:8000/healthz"]
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: "1G"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    networks:
      - backend

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 5s
      timeout: 5s
      retries: 5
    volumes:
      - pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: app
    networks:
      - backend

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    logging: *default-logging
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
    volumes:
      - redis-data:/data
    networks:
      - backend

volumes:
  pgdata:
    driver: local
  redis-data:
    driver: local

networks:
  backend:
    driver: bridge
```

---

## 8. Pièges Courants

1. **Tag `latest` en production :** Impossible de rollback proprement. Toujours taguer avec le SHA du commit ou la version sémantique.
2. **Build sans cache :** `docker build --no-cache` jette tout le layer caching. Préférer `--cache-from` pour les builds CI.
3. **Variables d'environnement en clair :** Ne jamais mettre de secrets dans `docker-compose.yml`. Utiliser un fichier `.env` ou Docker Secrets en Swarm.
4. **Layer unique géant :** Tout mettre dans un seul `RUN` rend le cache inutile. Séparer : déps système → déps pip → code.
5. **Port mapping sur 0.0.0.0 :** `ports: ["5432:5432"]` expose PostgreSQL à toute la machine. Limiter à `127.0.0.1:5432:5432`.
6. **Pas de .dockerignore :** Le contexte du build (dossier entier) est envoyé au daemon — y compris `.git`, `node_modules`, `.venv`. Créer un `.dockerignore` avec ces exclusions.
7. **Conteneur vs processus :** Docker ne redémarre pas un processus qui crash dans le conteneur. Utiliser `restart: unless-stopped` et `healthcheck`.

---

## 9. Checklist Production

- [ ] `.dockerignore` présent (exclure `.git`, `node_modules`, `__pycache__`, `.env`)
- [ ] Multi-stage build avec runtime minimal (alpine ou distroless)
- [ ] Utilisateur non-root (`USER 10001`) dans l'image finale
- [ ] Les secrets passent via `--secret` (BuildKit) ou Docker Secrets, pas dans l'image
- [ ] Scan de vulnérabilités fait (trivy ou docker scout)
- [ ] `restart: unless-stopped` sur chaque service
- [ ] `healthcheck` sur les services critiques (DB, API, cache)
- [ ] Logging avec rotation (max-size / max-file)
- [ ] Pas de `latest` dans les services de production
- [ ] Réseaux isolés : frontend ≠ backend quand pertinent
- [ ] Ports d'écoute limités à 127.0.0.1 quand l'accès externe n'est pas requis
