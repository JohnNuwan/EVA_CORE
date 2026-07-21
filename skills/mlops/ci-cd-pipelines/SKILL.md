---
name: ci-cd-pipelines
description: "Pipelines CI/CD complets — GitHub Actions, GitLab CI, testing automatisé, déploiement sécurisé, matrix builds, artifacts, caching, auto-versioning"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [ci-cd, github-actions, gitlab-ci, pipelines, déploiement, testing, artifacts, caching]
    related_skills: [docker-avance, kubernetes-avance, gitops-argocd, devsecops-pipelines]
---

# CI/CD — Pipelines d'Intégration et Déploiement Continus

## Vue d'ensemble

Les pipelines CI/CD automatisent la validation, le test et le déploiement du code à chaque commit. Cette compétence couvre GitHub Actions et GitLab CI en profondeur : workflows multi-environnements, matrix builds, caching intelligent, déploiement bleu-vert/canary, auto-versioning sémantique, et bonnes pratiques de sécurité.

## Quand l'utiliser

- Automatiser les tests à chaque push (lint, unit, intégration)
- Builder et publier des images Docker vers un registre
- Déployer sur Kubernetes, VPS, ou serverless après validation
- Gérer des environnements multiples (dev, staging, prod)
- Implémenter du déploiement bleu-vert ou canary
- Générer des releases automatiques (CHANGELOG, version tag)

---

## 1. GitHub Actions

### Structure d'un workflow

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
    tags: ['v*']
  pull_request:
    branches: [main]
  workflow_dispatch:  # Déclenchement manuel

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
      - run: pip install ruff
      - run: ruff check .

  test:
    needs: lint
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        os: [ubuntu-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: 'pip'
      - run: pip install -r requirements-dev.txt
      - run: pytest --cov=app tests/ --junitxml=results.xml
      - uses: actions/upload-artifact@v4
        with:
          name: test-results-${{ matrix.python-version }}
          path: results.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,format=short
            type=ref,event=branch
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Déploiement multi-environnement

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  workflow_run:
    workflows: ["CI Pipeline"]
    branches: [main, staging]
    types:
      - completed

jobs:
  deploy-staging:
    if: ${{ github.ref == 'refs/heads/staging' && github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Déploiement staging via Helm..."
          helm upgrade --install app ./charts/app \
            --namespace staging \
            --set image.tag=${{ github.sha }}

  deploy-production:
    if: ${{ github.ref == 'refs/heads/main' && github.event.workflow_run.conclusion == 'success' }}
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://app.eva.local
    needs: deploy-staging
    steps:
      - uses: actions/checkout@v4
      - run: |
          echo "Déploiement production via ArgoCD..."
          argocd app sync app-production
```

---

## 2. GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""
  IMAGE_TAG: $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA

cache:
  paths:
    - .venv/
    - node_modules/
  key: ${CI_COMMIT_REF_SLUG}

.lint-job:
  stage: lint
  script:
    - pip install ruff
    - ruff check .

test:python3.12:
  stage: test
  image: python:3.12-slim
  services:
    - postgres:16-alpine
  variables:
    DATABASE_URL: "postgresql://user:pass@postgres:5432/test"
  script:
    - pip install -r requirements-dev.txt
    - pytest --cov=app --junitxml=report.xml
  artifacts:
    reports:
      junit: report.xml
    when: always

build:docker:
  stage: build
  image: docker:27
  services:
    - docker:27-dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - docker build -t $IMAGE_TAG .
    - docker push $IMAGE_TAG
  only:
    - main
    - tags

deploy:staging:
  stage: deploy
  image: alpine/k8s:latest
  script:
    - kubectl set image deployment/app app=$IMAGE_TAG
    - kubectl rollout status deployment/app
  environment:
    name: staging
  only:
    - main

deploy:production:
  stage: deploy
  image: alpine/k8s:latest
  script:
    - kubectl set image deployment/app app=$IMAGE_TAG --namespace=production
    - kubectl rollout status deployment/app --namespace=production
  environment:
    name: production
  when: manual
  only:
    - tags
```

---

## 3. Auto-versioning Sémantique

```yaml
# GitHub Action pour versioning automatique
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Bump version and push tag
        id: tag
        uses: mathieudutour/github-tag-action@v6
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          release_branches: main
          default_bump: patch  # auto-detects major/minor/patch from commit messages

      - name: Generate changelog
        uses: orhun/git-cliff-action@v3
        with:
          config: cliff.toml
          args: --verbose --latest
        env:
          OUTPUT: CHANGELOG.md

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ steps.tag.outputs.new_tag }}
          body: ${{ steps.tag.outputs.changelog }}
          generate_release_notes: true
```

**Conventions de commit pour auto-bump :**

| Préfixe | Bump | Exemple |
|---------|------|---------|
| `fix:` | patch | `fix: correction timeout API` |
| `feat:` | minor | `feat: ajout endpoint /users` |
| `feat!:` ou `BREAKING CHANGE` | major | `feat!: refonte auth breaking` |

---

## 4. Caching & Optimisation

```yaml
# GitHub Actions — caching pip, Docker, node_modules
steps:
  - name: Cache pip
    uses: actions/cache@v4
    with:
      path: ~/.cache/pip
      key: pip-${{ hashFiles('requirements.txt') }}
      restore-keys: |
        pip-

  - name: Cache Docker layers
    uses: actions/cache@v4
    with:
      path: /tmp/.buildx-cache
      key: buildx-${{ runner.os }}-${{ hashFiles('Dockerfile', 'requirements.txt') }}
      restore-keys: |
        buildx-${{ runner.os }}-

  - name: Build with cache
    uses: docker/build-push-action@v6
    with:
      cache-from: type=local,src=/tmp/.buildx-cache
      cache-to: type=local,dest=/tmp/.buildx-cache,mode=max
```

---

## 5. Déploiement Bleu-Vert & Canary

### Bleu-Vert (GitHub Actions)

```yaml
deploy-blue-green:
  runs-on: ubuntu-latest
  steps:
    - name: Switch active service (blue → green)
      run: |
        kubectl apply -f k8s/green-deployment.yaml
        kubectl rollout status deployment/app-green
        kubectl patch service app -p '{"spec":{"selector":{"version":"green"}}}'
```

### Canary (ArgoCD Rollout)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: app-rollout
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 20
        - pause: {duration: 60}     # surveiller 1 min
        - setWeight: 50
        - pause: {duration: 60}
        - setWeight: 100
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: registry.eva.local/app:1.2.3
```

---

## 6. Sécurité des Pipelines

### Principales mesures

```yaml
# Protection des secrets — ne jamais faire ça :
- run: echo "TOKEN=${{ secrets.API_TOKEN }}" >> .env  # EXPOSÉ !

# À la place, passer via env :
- run: deploy.sh
  env:
    API_TOKEN: ${{ secrets.API_TOKEN }}

# Vérification des dépendances
- run: |
    pip audit requirements.txt
    trivy fs --severity CRITICAL .

# Signatures des images (cosign)
- run: |
    cosign sign --key env://COSIGN_PRIVATE_KEY \
      ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}@${{ steps.push.outputs.digest }}
```

### OIDC (sans secrets statiques)

```yaml
# Utiliser OIDC plutôt que des clés statiques
permissions:
  id-token: write
  contents: read

steps:
  - name: Configure AWS credentials via OIDC
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/GitHubActionsRole
      aws-region: eu-west-3
```

---

## 7. Pièges Courants

1. **Secrets dans les logs :** `echo` d'une variable sensible la publie dans les logs GitHub. Toujours masquer avec `::add-mask::`.
2. **Matrix explosion :** Une matrix 4×3×2 produit 24 jobs. Attention aux limites de concurrence GitHub (20 jobs max en gratuit).
3. **Dépendances sans cache :** Chaque job refetch pip/npm → +2 min par job. Ajouter un cache explicite.
4. **Pipeline trop long :** Un pipeline CI > 15 min tue la productivité. Paralléliser lint, test, security en jobs séparés.
5. **Pas de concurrency group :** Deux pushs rapprochés = deux déploiements concurrents qui s'écrasent. Toujours configurer `concurrency`.
6. **build --push sans test :** Docker build/test en parallèle = l'image peut être poussée même si les tests échouent. Structurer en dépendances séquentielles.

---

## 8. Checklist Production

- [ ] Concurrency group configuré pour éviter les déploiements parallèles
- [ ] Secrets injectés via GitHub Secrets/GitLab CI Variables, jamais dans le code
- [ ] Cache pip/npm/Docker configuré sur les jobs répétitifs
- [ ] Tests unitaires + lint + security scan dans des jobs parallèles
- [ ] Déploiement manuel requis pour la production (environment with protection rules)
- [ ] Artifacts de test (rapports JUnit, screenshots) uploadés en cas d'échec
- [ ] Images Docker taguées avec SHA du commit ou version sémantique
- [ ] OIDC préféré aux clés statiques pour l'authentification cloud
- [ ] Pipeline chronométré : idéalement < 10 min total
- [ ] Rollback documenté (commande Helm/kubectl à exécuter en cas d'incident)
