---
name: kubernetes-avance
description: "Déploiement, orchestration et administration avancés de clusters Kubernetes — Pods, Deployments, Services, RBAC, stockage persistant, HPA, réseau, debugging"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [kubernetes, k8s, orchestration, déploiement, pods, services, ingress, rbac, hpa, stockage]
    related_skills: [docker-avance, helm-charts, gitops-argocd, prometheus-grafana]
---

# Kubernetes — Orchestration Avancée

## Vue d'ensemble

Kubernetes (k8s) est le standard de fait pour l'orchestration de conteneurs en production. Cette compétence couvre les ressources fondamentales, les patterns de déploiement résilients, le RBAC, le stockage persistant, l'autoscaling, le réseau, le dépannage et les bonnes pratiques de production.

## Quand l'utiliser

- Déployer une application conteneurisée sur un cluster Kubernetes
- Configurer l'accès réseau (Services, Ingress, mTLS)
- Mettre en place du stockage persistant (PersistentVolume, PVC, StorageClass)
- Gérer les permissions (RBAC, ServiceAccounts)
- Configurer l'autoscaling horizontal (HPA) et vertical (VPA)
- Debugger un Pod qui crash, un nœud NotReady, ou un problème DNS

---

## 1. Ressources Fondamentales

### Pod (unité atomique)

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:1.27-alpine
      ports:
        - containerPort: 80
      resources:
        requests:
          cpu: "100m"
          memory: "128Mi"
        limits:
          cpu: "500m"
          memory: "256Mi"
```

### Deployment (déploiement déclaratif avec rollout)

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-deployment
  labels:
    app: api
spec:
  replicas: 3
  revisionHistoryLimit: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: registry.eva.local/api:1.2.3
          ports:
            - containerPort: 8000
          env:
            - name: LOG_LEVEL
              value: "info"
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
            timeoutSeconds: 3
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "250m"
              memory: "256Mi"
            limits:
              cpu: "1"
              memory: "512Mi"
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchLabels:
                    app: api
                topologyKey: kubernetes.io/hostname
```

### Service (exposition réseau)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
      protocol: TCP
      name: http
```

### Ingress (routage L7)

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-ingress
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - api.eva.local
      secretName: eva-tls
  rules:
    - host: api.eva.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api-service
                port:
                  number: 80
```

### ConfigMap & Secret (configuration)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-config
data:
  config.yaml: |
    log_level: info
    max_connections: 100
---
apiVersion: v1
kind: Secret
type: Opaque
metadata:
  name: api-secrets
stringData:
  DB_PASSWORD: "ch@nge-m3!"
```

---

## 2. RBAC (Sécurité des Accès)

### ServiceAccount + Role + RoleBinding

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-sa
  namespace: production
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: app-role
rules:
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: production
  name: app-role-binding
subjects:
  - kind: ServiceAccount
    name: app-sa
    namespace: production
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
```

### ClusterRole (cluster-wide)

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: reader-clusterrole
rules:
  - apiGroups: [""]
    resources: ["nodes", "persistentvolumes"]
    verbs: ["get", "list", "watch"]
```

---

## 3. Stockage Persistant

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-path
  resources:
    requests:
      storage: 10Gi
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
        - name: postgres
          image: postgres:16-alpine
          volumeMounts:
            - name: data
              mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 50Gi
```

---

## 4. Autoscaling (HPA)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

---

## 5. Réseau & Debugging

### Commandes essentielles

```bash
# Debug d'un Pod
kubectl describe pod <name>                    # Événements + status
kubectl logs -f <name> --tail=100              # Logs en live
kubectl logs <name> -c <container>             # Logs d'un sidecar

# Debug réseau
kubectl run debug --image=nicolaka/netshoot:latest --rm -it -- sh
kubectl port-forward service/api-service 8080:80

# État du cluster
kubectl get nodes -o wide
kubectl top nodes
kubectl top pods --all-namespaces
kubectl get events --sort-by='.lastTimestamp'

# Rollback
kubectl rollout history deployment/api-deployment
kubectl rollout undo deployment/api-deployment --to-revision=2

# Drain un nœud pour maintenance
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data
kubectl uncordon node-1
```

### NetworkPolicy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-network-policy
spec:
  podSelector:
    matchLabels:
      app: api
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: ingress-gateway
      ports:
        - port: 8000
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: postgres
      ports:
        - port: 5432
```

---

## 6. Pièges Courants

1. **Pas de ressources limits → OOMKill :** Sans `resources.limits.memory`, un Pod peut consommer toute la RAM du nœud et se faire tuer brutalement.
2. **Port non exposé dans containerPort :** Le champ `containerPort` est informatif. Le port doit aussi être exposé par le container dans son image.
3. **ServiceAccount par défaut :** Le ServiceAccount `default` est monté automatiquement. Pour les workloads sensibles, désactiver avec `automountServiceAccountToken: false`.
4. **Readiness probe trop stricte :** Si le readiness probe échoue 3x, le Pod est retiré du Service. Un probe mal configuré peut empêcher tout trafic.
5. **Anti-affinité non configurée :** Sans `podAntiAffinity`, les réplicas peuvent s'accumuler sur le même nœud — perte totale si le nœud tombe.
6. **PVC ReadWriteOnce vs ReadWriteMany :** RWO = un seul nœud peut monter. Pour plusieurs Pods sur différents nœuds, utiliser RWX avec NFS ou Longhorn.
7. **RollingUpdate maxUnavailable=0 :** Si `maxUnavailable: 0`, les nouveaux Pods DOIVENT démarrer avant que les anciens soient arrêtés. Peut bloquer la désaturation du nœud.

---

## 7. Checklist Production

- [ ] Tous les Pods ont `resources.requests` et `resources.limits`
- [ ] `livenessProbe` et `readinessProbe` configurées avec timeouts réalistes
- [ ] `automountServiceAccountToken: false` sur les Pods qui n'ont pas besoin d'API k8s
- [ ] Les Secrets sont chiffrés au repos (KMS ou `kubectl create secret generic`)
- [ ] RBAC minimal : chaque ServiceAccount a les plus petits privilèges
- [ ] NetworkPolicy appliquée pour restreindre le trafic inter-Pods
- [ ] PodDisruptionBudget configuré pour les applications critiques
- [ ] `revisionHistoryLimit` paramétré (< 5 pour éviter la dérive)
- [ ] Les images utilisent des tags de version, pas `latest`
- [ ] `imagePullPolicy: Always` pour les tags non-uniques
- [ ] Anti-affinité entre réplicas (ou topology spread constraints)
- [ ] Logs structurés (JSON) pour ELK/Loki
