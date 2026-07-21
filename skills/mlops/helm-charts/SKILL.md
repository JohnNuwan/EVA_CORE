---
name: helm-charts
description: "Gestion de packages Kubernetes avec Helm — création de charts, templating Go, sous-charts, hooks, repositories, CI/CD intégré, rollback, bonnes pratiques"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [helm, charts, kubernetes, templating, go-templates, package-manager, releases, rollback]
    related_skills: [kubernetes-avance, ci-cd-pipelines, gitops-argocd, docker-avance]
---

# Helm — Gestion de Charts Kubernetes

## Vue d'ensemble

Helm est le gestionnaire de paquets Kubernetes. Il permet de définir, installer et mettre à jour des applications complexes via des charts paramétrables. Cette compétence couvre la création de charts, le templating Go, les sous-charts et dépendances, les hooks, la gestion des repositories, l'intégration CI/CD, et les bonnes pratiques.

## Quand l'utiliser

- Packager une application pour des déploiements reproductibles sur Kubernetes
- Paramétrer des déploiements multi-environnements (dev/staging/prod)
- Distribuer des applications via un repository Helm
- Gérer les dépendances entre plusieurs charts
- Automatiser les mises à jour avec des pipelines CI/CD

---

## 1. Structure d'un Chart

```
my-app/
├── Chart.yaml              # Métadonnées du chart
├── values.yaml             # Valeurs par défaut
├── values.schema.json      # Validation JSON Schema (optionnel)
├── charts/                 # Sous-charts dépendants
│   └── postgresql/
│       └── ...
├── templates/
│   ├── _helpers.tpl        # Templates partagés (named templates)
│   ├── deployment.yaml     # Déploiement
│   ├── service.yaml        # Service
│   ├── ingress.yaml        # Ingress
│   ├── configmap.yaml      # Configuration
│   ├── secret.yaml         # Secrets
│   ├── hpa.yaml            # Autoscaling
│   ├── tests/
│   │   └── test-connection.yaml
│   └── NOTES.txt           # Instructions post-install
└── .helmignore             # Exclusions
```

### Chart.yaml

```yaml
apiVersion: v2
name: my-app
description: Application EVA déployée via Helm
type: application
version: 1.2.3
appVersion: "1.2.0"
kubeVersion: ">= 1.28.0"
keywords:
  - eva
  - api
home: https://eva.local
sources:
  - https://git.eva.local/my-app
maintainers:
  - name: EVA Team
    email: devops@eva.local
dependencies:
  - name: postgresql
    version: "~15.0"
    repository: "oci://registry-1.docker.io/bitnamicharts"
    condition: postgresql.enabled
    alias: db
  - name: redis
    version: "~19.0"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
icon: https://eva.local/icon.png
annotations:
  category: Infrastructure
```

---

## 2. Templating Go (Fonctions Essentielles)

```yaml
# _helpers.tpl
{{- define "my-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "my-app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "my-app.labels" -}}
helm.sh/chart: {{ include "my-app.name" . }}-{{ .Chart.Version | replace "+" "_" }}
{{ include "my-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "my-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
```

### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "my-app.fullname" . }}
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "my-app.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "my-app.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "my-app.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.port }}
              protocol: TCP
          livenessProbe:
            {{- toYaml .Values.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          env:
            {{- toYaml .Values.env | nindent 12 }}
          envFrom:
            - configMapRef:
                name: {{ include "my-app.fullname" . }}
            - secretRef:
                name: {{ include "my-app.fullname" . }}
          volumeMounts:
            {{- toYaml .Values.volumeMounts | nindent 12 }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

---

## 3. values.yaml (Paramétrage)

```yaml
# values.yaml
replicaCount: 2

image:
  repository: registry.eva.local/my-app
  tag: ""
  pullPolicy: IfNotPresent

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  automount: true
  annotations: {}
  name: ""

podAnnotations: {}
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 10001
  fsGroup: 10001

securityContext:
  capabilities:
    drop: ["ALL"]
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 10001

service:
  type: ClusterIP
  port: 8000

ingress:
  enabled: false
  className: nginx
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
  hosts:
    - host: api.eva.local
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: eva-tls
      hosts:
        - api.eva.local

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

env:
  - name: LOG_LEVEL
    value: "info"
  - name: ENVIRONMENT
    value: "production"

livenessProbe:
  httpGet:
    path: /healthz
    port: http
  initialDelaySeconds: 15
  periodSeconds: 20

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10

nodeSelector: {}
tolerations: []
affinity: {}

postgresql:
  enabled: true
  auth:
    database: myapp
    username: myapp

redis:
  enabled: true
  architecture: standalone
```

### Valeurs multi-environnements

```yaml
# values-prod.yaml
replicaCount: 5
resources:
  limits:
    cpu: 2
    memory: 2Gi
  requests:
    cpu: 1
    memory: 1Gi
autoscaling:
  maxReplicas: 20
postgresql:
  enabled: true
  auth:
    database: myapp_prod
```

```yaml
# values-dev.yaml
replicaCount: 1
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
postgresql:
  enabled: false
```

---

## 4. Commandes Essentielles

```bash
# Créer un nouveau chart
helm create my-app

# Dépendances
helm dependency update my-app/          # Télécharge les dépendances
helm dependency build my-app/           # Build et vérifie

# Lint et validation
helm lint my-app/                       # Vérifie la syntaxe
helm template my-app ./my-app/          # Génère les manifestes sans installer
helm template my-app ./my-app/ --debug  # Voir les templates compilés
helm get manifest my-app --namespace prod # Voir les manifestes déployés

# Installer / Mettre à jour
helm install my-app ./my-app/ --namespace prod --create-namespace
helm upgrade --install my-app ./my-app/ -f values-prod.yaml --atomic --timeout 10m
helm upgrade --install my-app ./my-app/ --set image.tag=v1.2.3

# Rollback
helm rollback my-app 2 --namespace prod        # Revenir à la révision 2
helm history my-app --namespace prod           # Voir l'historique

# Désinstaller
helm uninstall my-app --namespace prod

# Repository
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
helm search repo bitnami/nginx
helm pull bitnami/nginx --untar               # Télécharger et extraire
```

---

## 5. Hooks Helm

```yaml
# templates/migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "my-app.fullname" . }}-migration
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "-5"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migration
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["alembic", "upgrade", "head"]
```

| Annotation `helm.sh/hook` | Déclencheur |
|---------------------------|-------------|
| `pre-install` | Avant l'installation |
| `post-install` | Après l'installation |
| `pre-upgrade` | Avant la mise à jour |
| `post-upgrade` | Après la mise à jour |
| `pre-rollback` | Avant le rollback |
| `post-rollback` | Après le rollback |
| `pre-delete` | Avant la suppression |
| `test` | Lors de `helm test` |

---

## 6. Test de Chart

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: "{{ include "my-app.fullname" . }}-test-connection"
  labels:
    {{- include "my-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
spec:
  containers:
    - name: wget
      image: busybox
      command: ['wget']
      args: ['{{ include "my-app.fullname" . }}:{{ .Values.service.port }}']
  restartPolicy: Never
```

```bash
helm test my-app --namespace prod
```

---

## 7. Pièges Courants

1. **values.yaml trop long :** 500 lignes de valeurs sont illisibles. Structurer en sections claires, utiliser des valeurs calculées dans `_helpers.tpl`.
2. **Dépendances non verrouillées :** `helm dependency update` sans `Chart.lock` dans le repo = build non reproductible. Toujours commiter `Chart.lock`.
3. **Templates non testés :** `helm template` ne déploie pas, mais ne valide pas la logique métier. Utiliser `helm unittest` (plugin) ou `helm test`.
4. **Secrets en clair dans values :** `values.yaml` est en clair. Utiliser un plugin vault (Helm Secrets, SOPS) ou ArgoCD Vault Plugin.
5. **Hooks mal priorités :** Deux hooks pre-install sans poids peuvent s'exécuter dans n'importe quel ordre. Toujours définir `helm.sh/hook-weight`.
6. **Pas de --atomic :** Sans `--atomic`, un upgrade qui échoue laisse le release cassé. `--atomic` rollback automatiquement.

---

## 8. Checklist Production

- [ ] `Chart.yaml` complet (version, appVersion, maintainers, dependencies)
- [ ] `Chart.lock` committé pour les dépendances reproductibles
- [ ] `values.schema.json` pour valider les valeurs utilisateur
- [ ] `_helpers.tpl` définit les noms, labels, selectors (pas de duplication)
- [ ] `NOTES.txt` donne les instructions d'accès post-install
- [ ] `helm lint` passe sans erreur
- [ ] `helm template` génère des manifestes valides (`kubectl apply --dry-run=client`)
- [ ] `helm unittest` teste la logique de templating
- [ ] Hooks avec poids pour ordonner les jobs
- [ ] Sécurité : `securityContext.runAsNonRoot: true`, `readOnlyRootFilesystem: true`
- [ ] `--atomic` utilisé dans tous les upgrades CI/CD
- [ ] Secrets gérés via plugin vault ou externe (pas en clair dans values)