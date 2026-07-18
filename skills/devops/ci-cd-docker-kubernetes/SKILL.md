---
name: ci-cd-docker-kubernetes
description: "Optimiser les workflows DevOps avec Docker (multi-stage builds, compose), Kubernetes (pods, services, deployments) et concevoir des pipelines CI/CD."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [docker, docker-compose, kubernetes, k8s, ci-cd, github-actions, devops, deployment]
    related_skills: [os-linux-admin, os-virtualization-hypervisors]
---

# DevOps : Conteneurisation (Docker) et Orchestration (Kubernetes / CI-CD)

## Vue d'ensemble

Le DevOps unifie le développement logiciel (Dev) et l'administration des infrastructures (Ops). Cette compétence fournit les règles et modèles de référence pour concevoir des Dockerfiles sécurisés et légers, orchestrer des environnements locaux via Docker Compose, déployer des applications résilientes sur Kubernetes (k8s) et automatiser l'intégration et le déploiement continus (CI/CD) via GitHub Actions.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Conteneuriser une application en écrivant un `Dockerfile`.
- Configurer un environnement multi-conteneurs local (`docker-compose.yml`) avec bases de données et services.
- Créer ou corriger des manifestes Kubernetes (Deployments, Services, ConfigMaps).
- Configurer un pipeline CI/CD pour builder, tester et déployer du code automatiquement.

**Ne pas utiliser pour :**
- L'administration système OS pure (utilisez plutôt `os-linux-admin` ou `os-windows-admin`).
- L'automatisation industrielle SCADA sans conteneurs.

---

## 1. Optimisation de Dockerfiles (Multi-stage Build)

L'utilisation du multi-stage build permet de diviser la taille de l'image finale par 10 et d'exclure les outils de compilation du runtime, limitant la surface d'attaque.

```dockerfile
# --- ÉTAPE 1 : Compilation et Dépendances ---
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- ÉTAPE 2 : Image Finale de Production (Légère) ---
FROM python:3.11-slim AS runner

WORKDIR /app

# Récupération des dépendances compilées
COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH

# Sécurité : Exécuter l'application sous un utilisateur non-root
RUN useradd -u 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "main.py"]
```

---

## 2. Déploiement Local avec Docker Compose

Docker Compose simplifie la gestion de plusieurs conteneurs interconnectés. Voici une configuration robuste pour une application et sa base de données PostgreSQL :

```yaml
version: '3.8'

services:
  web:
    build:
      context: .
      target: runner
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://app_user:secure_password@db:5432/app_db
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=app_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=app_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_db"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 3. Déploiement Kubernetes de Référence

Le manifeste suivant montre comment déployer une application sur un cluster Kubernetes de manière résiliente avec des sondes de disponibilité (Probes) et des limites de ressources :

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app-deployment
  labels:
    app: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: web
        image: registry.actemium.com/my-app:1.0.0
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "500m"
            memory: "512Mi"
          requests:
            cpu: "250m"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8000
          initialDelaySeconds: 15
          periodSeconds: 20
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
```

---

## 4. Pipeline CI/CD GitHub Actions

Ce fichier `.github/workflows/ci.yml` automatise la validation du code à chaque commit :

```yaml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout Code
      uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
        cache: 'pip'

    - name: Install Dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt

    - name: Run Linter (Ruff)
      run: ruff check .

    - name: Run Tests (pytest)
      run: pytest --cov=app tests/
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1. **Exécution des conteneurs en tant que `root` :**
   * *Erreur :* Ne pas définir d'instruction `USER` dans le Dockerfile. En cas d'intrusion dans le conteneur, l'attaquant obtient des privilèges root sur la machine hôte.
   * *Correction :* Toujours créer un utilisateur système non privilégié et basculer sur lui (`USER 10001`).

2. **Absence de limites de ressources dans Kubernetes :**
   * *Erreur :* Déployer des pods sans définir `resources.limits`. Un pod ayant une fuite de mémoire peut consommer toute la RAM du nœud physique et crash les autres pods co-localisés.
   * *Correction :* Toujours définir des limites et des requêtes CPU/Mémoire réalistes.

3. **Utilisation du tag `latest` en production :**
   * *Erreur :* Déployer avec `image: my-app:latest`. Les nouveaux builds écrasent le tag sans changer le manifeste de déploiement, rendant impossible le retour arrière (rollback) automatique ou le suivi de version.
   * *Correction :* Utiliser des tags précis basés sur le hash de commit git ou la version sémantique (ex: `1.2.3`).

---

## Liste de vérification (Checklist)

- [ ] L'instruction `USER` non-root est spécifiée dans le Dockerfile de production.
- [ ] Les dépendances de build temporaires sont nettoyées dans la même couche `RUN` ou via un multi-stage build.
- [ ] Un fichier `.dockerignore` est configuré à la racine pour exclure les fichiers inutiles (ex: `.git`, `.venv`, `__pycache__`).
- [ ] Les conteneurs dépendant d'autres services (ex: base de données) dans docker-compose utilisent un `healthcheck` avec `condition: service_healthy`.
- [ ] Les manifestes de déploiement Kubernetes incluent explicitement des sondes (`livenessProbe`, `readinessProbe`) et des limites de ressources (`limits`).
- [ ] Aucun secret (clés API, mots de passe) n'est écrit dans les Dockerfiles ou les dépôts git (utilisation des GitHub Secrets / K8s Secrets).

