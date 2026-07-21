---
name: gitops-argocd
description: "GitOps avec ArgoCD et Flux — déploiement continu, sync automatique, ApplicationSets, multi-cluster, health checks, rollback, Vault integration, bonnes pratiques"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [gitops, argocd, flux, déploiement-continu, synchronisation, kubernetes, applicationset, multi-cluster]
    related_skills: [kubernetes-avance, helm-charts, ci-cd-pipelines, devsecops-pipelines]
---

# GitOps — ArgoCD & Flux

## Vue d'ensemble

GitOps est un modèle opérationnel où Git est la source unique de vérité pour l'infrastructure et les applications. ArgoCD et Flux sont les deux implémentations majeures pour Kubernetes. Cette compétence couvre la configuration, le sync automatique, les ApplicationSets, le multi-cluster, les health checks, les rollbacks, l'intégration avec Vault/external-secrets, et les bonnes pratiques.

## Quand l'utiliser

- Déployer des applications Kubernetes avec Git comme source de vérité
- Automatiser la synchronisation entre le repo Git et le cluster
- Gérer des déploiements multi-environnements (plusieurs clusters ou namespaces)
- Implémenter le self-healing (ArgoCD corrige automatiquement le drift)
- Intégrer des secrets externes (Vault, AWS Secrets Manager, SOPS)

---

## 1. ArgoCD — Installation

```bash
# Installation avec Helm
helm repo add argo https://argoproj.github.io/argo-helm
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd --create-namespace \
  --set server.service.type=LoadBalancer \
  --set server.ingress.enabled=true \
  --set server.ingress.hosts=["argocd.eva.local"] \
  --set configs.params."server\.insecure"=true \
  --atomic --timeout 10m

# Récupérer le mot de passe admin
kubectl get secret argocd-initial-admin-secret \
  -n argocd -o jsonpath="{.data.password}" | base64 -d

# Connexion CLI
argocd login argocd.eva.local --username admin --password <password>
argocd account update-password
```

---

## 2. Application ArgoCD (Application CRD)

```yaml
# apps/api/application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io  # Nettoie les ressources à la suppression
spec:
  project: production

  source:
    repoURL: https://git.eva.local/infrastructure.git
    targetRevision: main
    path: charts/api
    helm:
      valueFiles:
        - values-production.yaml
      releaseName: api

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
      - RespectIgnoreDifferences=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

---

## 3. Projets ArgoCD (RBAC)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: production
  namespace: argocd
spec:
  description: Projet production

  sourceRepos:
    - 'https://git.eva.local/infrastructure.git'
    - 'https://charts.bitnami.com/bitnami'

  destinations:
    - namespace: production
      server: https://kubernetes.default.svc
    - namespace: staging
      server: https://kubernetes.default.svc

  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: 'rbac.authorization.k8s.io'
      kind: ClusterRole
      kind: ClusterRoleBinding

  namespaceResourceBlacklist:
    - group: 'apps'
      kind: DaemonSet

  roles:
    - name: developer
      description: Accès en lecture seule + sync
      policies:
        - p, proj:production:developer, applications, get, production/*, allow
        - p, proj:production:developer, applications, sync, production/*, allow
      groups:
        - eva-developers
```

---

## 4. ApplicationSet (Génération Multi-Environnements)

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: api-appset
  namespace: argocd
spec:
  goTemplate: true
  goTemplateOptions: ["missingkey=error"]

  generators:
    - matrix:
        generators:
          - git:
              repoURL: https://git.eva.local/infrastructure.git
              revision: HEAD
              directories:
                - path: configs/clusters/*
          - list:
              elements:
                - env: dev
                - env: staging
                - env: prod

  template:
    metadata:
      name: 'api-{{.path.basename}}-{{.env}}'
      labels:
        app: api
        environment: '{{.env}}'
        cluster: '{{.path.basename}}'
    spec:
      project: '{{.env}}'
      source:
        repoURL: https://git.eva.local/infrastructure.git
        targetRevision: '{{if eq .env "prod"}}main{{else}}develop{{end}}'
        path: charts/api
        helm:
          valueFiles:
            - 'values-{{.env}}.yaml'
      destination:
        server: 'https://{{.path.basename}}.k8s.eva.local'
        namespace: '{{.env}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

---

## 5. Multi-Cluster

```bash
# Ajouter un cluster distant
argocd cluster add context-k8s-prod \
  --name k8s-prod \
  --label env=production \
  --label region=eu-west-3

# Liste des clusters
argocd cluster list
```

```yaml
# Secret pour cluster distant
apiVersion: v1
kind: Secret
metadata:
  name: k8s-prod-cluster
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: cluster
type: Opaque
stringData:
  name: k8s-prod
  server: https://192.168.1.50:6443
  config: |
    {
      "bearerToken": "...",
      "tlsClientConfig": {
        "insecure": false,
        "caData": "..."
      }
    }
```

---

## 6. Flux (Alternative)

```yaml
# Installation Flux
apiVersion: v1
kind: Namespace
metadata:
  name: flux-system
---
# flux-system/gotk-components.yaml
# (généré par flux install --export)
---
# Source Git
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: infrastructure
  namespace: flux-system
spec:
  interval: 1m
  url: https://git.eva.local/infrastructure.git
  ref:
    branch: main
  secretRef:
    name: flux-git-auth

# Kustomization (déploiement)
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: api-production
  namespace: flux-system
spec:
  interval: 5m
  sourceRef:
    kind: GitRepository
    name: infrastructure
  path: ./charts/api
  prune: true
  timeout: 5m
  healthChecks:
    - apiVersion: apps/v1
      kind: Deployment
      name: api
      namespace: production
  postBuild:
    substitute:
      ENV: production
    substituteFrom:
      - kind: ConfigMap
        name: flux-cluster-config
```

### Flux vs ArgoCD

| Critère | ArgoCD | Flux |
|---------|--------|------|
| Installation | Helm + CRD | CLI bootstrap + CRD |
| UI Web | Intégrée (riche) | Aucune (CLI seulement) |
| Multi-cluster | Natif via cluster secrets | Kustomization + cross-cluster |
| ApplicationSet | Oui (générateurs puissants) | Non (via Kustomize) |
| Sync | Pull (agent dans cluster) | Pull (agent dans cluster) |
| Secrets | + Vault Plugin / SOPS | + SOPS / Sealed Secrets |
| Performances | Plus lent (UI, sync) | Plus léger |

---

## 7. Gestion des Secrets

### External Secrets Operator

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: api-secrets
    creationPolicy: Owner
  data:
    - secretKey: DB_PASSWORD
      remoteRef:
        key: eva/production/database
        property: password
    - secretKey: API_KEY
      remoteRef:
        key: eva/production/api
        property: key
```

### SOPS (Mozilla)

```yaml
# .sops.yaml
creation_rules:
  - path_regex: secrets/.*\.yaml
    encrypted_regex: ^(data|stringData)$
    age: age1abc123...
```

```bash
# Chiffrer un fichier
sops --encrypt secrets/prod/secrets.yaml > secrets/prod/secrets.enc.yaml

# ArgoCD lit le fichier déchiffré via le plugin SOPS
# (configuré dans argocd-cm)
```

---

## 8. Intégration CI/CD

```yaml
# CI: build et push image, puis déclencher ArgoCD
# .github/workflows/gitops.yml
name: GitOps Deploy

on:
  push:
    branches: [main]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: registry.eva.local/api:${{ github.sha }}

      - name: Update manifest
        run: |
          cd charts/api
          yq eval -i '.image.tag = "${{ github.sha }}"' values-production.yaml
          git add .
          git commit -m "chore: bump api to ${{ github.sha }}"
          git push

      # ArgoCD détecte le changement dans Git et sync automatiquement
```

---

## 9. Pièges Courants

1. **Prune=true sans précaution :** `prune: true` supprime les ressources qui ne sont plus dans Git. Si on supprime un dossier par erreur, ArgoCD nettoie tout le namespace.
2. **Sync trop fréquent :** `syncInterval: 5s` épuise l'API Kubernetes. Garder ≥ 3 min sauf urgence.
3. **Self-healing mal compris :** Self-healing ramène au dernier état commité dans Git. Les modifications manuelles (kubectl edit) sont annulées au prochain sync.
4. **Secrets exposés dans Git :** Un fichier YAML avec `stringData` en clair dans Git n'est pas chiffré. Utiliser SOPS, Sealed Secrets, ou External Secrets Operator.
5. **Finalizer absent :** Sans `resources-finalizer.argocd.argoproj.io`, la suppression d'une Application ne nettoie pas les ressources déployées. Les ressources restent orphelines.
6. **ApplicationSet mal configuré :** Un template buggé peut générer des centaines d'applications. Toujours tester avec `argocd appset generate`.

---

## 10. Checklist Production

- [ ] Projets ArgoCD configurés avec RBAC (sourceRepos, destinations, roles)
- [ ] `selfHeal: true` + `prune: true` sur les applications de production
- [ ] Finalizer `resources-finalizer.argocd.argoproj.io` présent
- [ ] External Secrets Operator ou SOPS pour les secrets
- [ ] ApplicationSet pour les déploiements multi-environnements
- [ ] Manifests tests dans un dossier `argo-e2e` avant déploiement prod
- [ ] Notifications ArgoCD configurées (Slack/Telegram)
- [ ] `argocd appset generate` testé avant commit
- [ ] Secrets jamais en clair dans le repo Git
- [ ] Rollback documenté (argocd app rollback) dans le runbook