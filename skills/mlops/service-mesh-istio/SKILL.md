---
name: service-mesh-istio
description: "Service Mesh avec Istio — mTLS, traffic management, observabilité, canary deployments, circuit breaking, fault injection, ingress/egress, authorization policies, mesh multi-cluster"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [service-mesh, istio, linkerd, mTLS, traffic-management, canary, circuit-breaker, observabilité, envoy, sidecar]
    related_skills: [kubernetes-avance, prometheus-grafana, gitops-argocd, helm-charts]
---

# Service Mesh — Istio & Linkerd

## Vue d'ensemble

Un service mesh (maillage de services) gère la communication entre microservices via des sidecars proxies (Envoy pour Istio, linkerd-proxy pour Linkerd). Cette compétence couvre Istio en profondeur : mTLS automatique, traffic routing, canary/blue-green, circuit breaking, fault injection, observabilité (Kiali, Jaeger, Prometheus), authorization policies, et multi-cluster mesh.

## Quand l'utiliser

- Chiffrer tout le trafic inter-services avec mTLS sans modifier le code
- Implémenter du canary routing, A/B testing, miroir de trafic
- Ajouter du circuit breaking et retry pour la résilience
- Obtenir des métriques L7 (HTTP/gRPC) sans instrumentation
- Appliquer des politiques d'accès entre services (AuthorizationPolicy)
- Connecter des services entre plusieurs clusters Kubernetes

---

## 1. Installation Istio

```bash
# Avec istioctl
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.23
istioctl install --set profile=default -y

# Profile minimal (production)
istioctl install --set profile=production \
  --set meshConfig.accessLogFile=/dev/stdout \
  --set meshConfig.enableTracing=true \
  --set values.global.proxy.accessLogFile=/dev/stdout \
  -y

# Activation de l'injection de sidecar sur un namespace
kubectl label namespace production istio-injection=enabled

# Vérification
istioctl version
istioctl proxy-status
kubectl get pods -n istio-system
```

### Installation Helm

```yaml
# helm/istio/base.yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
spec:
  profile: default
  components:
    ingressGateways:
      - name: istio-ingressgateway
        enabled: true
        k8s:
          resources:
            requests:
              cpu: 500m
              memory: 512Mi
            limits:
              cpu: 2
              memory: 1Gi
          hpaSpec:
            minReplicas: 2
            maxReplicas: 5
    egressGateways:
      - name: istio-egressgateway
        enabled: true
  meshConfig:
    accessLogFile: /dev/stdout
    enableTracing: true
    defaultConfig:
      holdApplicationUntilProxyStarts: true
```

---

## 2. mTLS Automatique

```yaml
# mTLS strict sur tout le mesh
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT  # STRICT, PERMISSIVE, DISABLE
```

```yaml
# mTLS permissif pour un namespace spécifique (transition)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: namespace-mtls
  namespace: legacy
spec:
  mtls:
    mode: PERMISSIVE
  portLevelMtls:
    8080:
      mode: STRICT  # Port 8080 en strict, les autres en permissif
```

---

## 3. Traffic Management

### Gateway + VirtualService

```yaml
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: api-gateway
  namespace: production
spec:
  selector:
    istio: ingressgateway
  servers:
    - port:
        number: 443
        name: https
        protocol: HTTPS
      tls:
        mode: SIMPLE
        credentialName: eva-tls-cert
      hosts:
        - api.eva.local
        - api.eva.dev
---
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-virtualservice
  namespace: production
spec:
  hosts:
    - api.eva.local
  gateways:
    - api-gateway
    - mesh  # Règles aussi pour le trafic interne
  http:
    - match:
        - uri:
            prefix: /api/v1
      route:
        - destination:
            host: api-service
            port:
              number: 8000
          weight: 100
      retries:
        attempts: 3
        perTryTimeout: 2s
        retryOn: gateway-error,connect-failure,refused-stream
      timeout: 10s
      corsPolicy:
        allowOrigins:
          - exact: https://app.eva.local
        allowMethods:
          - GET
          - POST
        allowHeaders:
          - authorization
```

### Canary Deployment

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-canary
  namespace: production
spec:
  hosts:
    - api-service
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: api-service
            subset: v2
          weight: 100
    - route:
        - destination:
            host: api-service
            subset: v1
          weight: 90
        - destination:
            host: api-service
            subset: v2
          weight: 10
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-destination
  namespace: production
spec:
  host: api-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 10
    loadBalancer:
      simple: LEAST_CONN
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
      maxEjectionPercent: 50
  subsets:
    - name: v1
      labels:
        version: v1
    - name: v2
      labels:
        version: v2
```

### Fault Injection (Test de résilience)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-fault
  namespace: production
spec:
  hosts:
    - api-service
  http:
    - fault:
        delay:
          fixedDelay: 5s
          percentage:
            value: 10  # 10% du trafic a 5s de latence
        abort:
          httpStatus: 500
          percentage:
            value: 1  # 1% du trafic est rejeté en 500
      route:
        - destination:
            host: api-service
            subset: v1
```

### Mirroring (Traffic shadow)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-mirror
  namespace: production
spec:
  hosts:
    - api-service
  http:
    - route:
        - destination:
            host: api-service
            subset: v1
      mirror:
        host: api-service
        subset: v2
      mirrorPercentage:
        value: 50
```

---

## 4. Authorization Policies

```yaml
# RBAC entre services
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  action: ALLOW
  rules:
    - from:
        - source:
            principals: ["cluster.local/ns/production/sa/frontend-sa"]
      to:
        - operation:
            methods: ["GET"]
            paths: ["/api/v1/*"]
      when:
        - key: request.headers[Authorization]
          values: ["Bearer *"]

---
# Deny tout le reste
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-deny-all
  namespace: production
spec:
  selector:
    matchLabels:
      app: api
  action: DENY
  rules:
    - from:
        - source:
            notPrincipals: ["cluster.local/ns/production/sa/frontend-sa"]
```

---

## 5. Observabilité

### Kiali (Topologie des services)

```bash
# Installer Kiali
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.23/samples/addons/kiali.yaml
istioctl dashboard kiali
```

### Jaeger (Tracing distribué)

```yaml
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-default
  namespace: istio-system
spec:
  tracing:
    - providers:
        - name: "zipkin"
      randomSamplingPercentage: 100  # 100% des requêtes tracées (dev)
      customTags:
        environment:
          literal:
            value: "production"
```

### Métriques Prometheus (par défaut)

```yaml
# Istio expose des métriques automatiquement
# Exemple : istio_requests_total, istio_request_duration_milliseconds
# Prometheus les scrape sur le port 15090 du sidecar

# Requête PromQL pour le taux d'erreur L7
sum(rate(istio_requests_total{reporter="destination",response_code=~"5.*"}[5m])) /
sum(rate(istio_requests_total{reporter="destination"}[5m])) * 100
```

---

## 6. Linkerd (Alternative Légère)

```bash
# Installation
curl --proto '=https' --tlsv1.2 -sSfL https://run.linkerd.io/install | sh
linkerd install --crds | kubectl apply -f -
linkerd install | kubectl apply -f -
linkerd check

# Injection sidecar
kubectl get deploy/api -o yaml | linkerd inject - | kubectl apply -f -
# ou annotation
# metadata.annotations: linkerd.io/inject: enabled

# mTLS
linkerd check --proxy
```

### Linkerd vs Istio

| Critère | Istio | Linkerd |
|---------|-------|---------|
| Proxy | Envoy (C++) | linkerd-proxy (Rust) |
| Ressources | ~100-200MB RAM / sidecar | ~10-20MB RAM / sidecar |
| Complexité | Élevée | Faible |
| Features | Rich (auth, fault, mirroring) | Basique (traffic split, mTLS) |
| Observabilité | Kiali, Jaeger, Grafana | Tap, Viz, Grafana |
| Adoption | Standard enterprise | Cloud-native, simplifié |

---

## 7. Multi-Cluster Mesh

```yaml
# Configuration primaire-secondaire
# Cluster 1 (primary)
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
metadata:
  namespace: istio-system
spec:
  meshConfig:
    defaultConfig:
      proxyMetadata:
        ISTIO_META_DNS_CAPTURE: "true"
        ISTIO_META_DNS_AUTO_ALLOCATE: "true"
  values:
    global:
      meshID: eva-mesh
      multiCluster:
        clusterName: cluster-eu-west-3
      network: network-1
```

```bash
# Cluster 2 (remote)
istioctl x create-remote-secret \
  --name=cluster-us-east-1 \
  --namespace=istio-system \
  | kubectl apply -f - --context=cluster-eu-west-3

# DNS inter-cluster
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.23/samples/multicluster/service-export.yaml
```

---

## 8. Pièges Courants

1. **mTLS PERMISSIVE en production :** Le mode PERMISSIF accepte le trafic en clair. Passer à STRICT après validation.
2. **Sidecar non redémarré :** Après avoir ajouté `istio-injection=enabled` sur un namespace, les pods existants ne sont pas automatiquement injectés. Faire un rollout restart.
3. **Timeout trop court :** Les timeouts Istio (15s par défaut) peuvent couper des requêtes légitimes si l'application est lente. Adapter le timeout dans VirtualService.
4. **Circuit breaker trop agressif :** `maxEjectionPercent: 100` peut vider tous les pods. Garder ≤ 50% pour laisser une marge.
5. **Règles d'authorization trop permissives :** `ALLOW` sans `DENY` catch-all = tout ce qui n'est pas explicitement autorisé... est autorisé. Toujours ajouter une règle DENY finale.
6. **Observabilité coûteuse :** 100% de tracing sampling en production génère du volume. Passer à 1-10% en prod.

---

## 9. Checklist Production

- [ ] mTLS en mode STRICT sur tout le mesh
- [ ] PeerAuthentication appliqué sur tous les namespaces
- [ ] AuthorizationPolicy avec DENY catch-all
- [ ] DestinationRule avec circuit breaker et outlier detection
- [ ] VirtualService avec timeouts et retries configurés
- [ ] Canary deployment testé avec 10% de trafic
- [ ] Kiali installé pour la visualisation du mesh
- [ ] Métriques Prometheus scrapées depuis Istio
- [ ] Tracing distribué (Jaeger) configuré avec sampling adapté
- [ ] Ingress Gateway avec TLS terminé
- [ ] Egress Gateway pour le trafic sortant contrôlé
- [ ] Tests de résilience (fault injection) réguliers