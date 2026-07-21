---
name: cloud-container-defense
description: Guide complet de sécurité des conteneurs cloud — EKS, GKE, AKS, image scanning, admission controllers, runtime security, CIS benchmarks, Pod Security Standards, network policies, secrets management
category: cybersecurite
---

# Cloud Container Security — EKS / GKE / AKS

---

## 1. Principes Fondamentaux

### Container Security Stack
```
┌──────────────────────────────────────┐
│          Container Image             │
│  Scanning (Trivy, Grype, Snyk)      │
├──────────────────────────────────────┤
│         Image Registry              │
│  Auth, Signing (Cosign, Notary)     │
├──────────────────────────────────────┤
│       Admission Control             │
│  OPA/Gatekeeper, Kyverno, PSA       │
├──────────────────────────────────────┤
│        Runtime Security             │
│  Falco, Tracee, Aqua, Sysdig       │
├──────────────────────────────────────┤
│         Network Security            │
│  Network Policies, Cilium, Calico   │
├──────────────────────────────────────┤
│       Cluster Security             │
│  RBAC, Secrets, Audit, CIS          │
└──────────────────────────────────────┘
```

---

## 2. Image Security

### Image Scanning
```bash
# Trivy — le plus rapide
trivy image --severity CRITICAL,HIGH <image>
trivy image --severity MEDIUM --ignore-unfixed --exit-code 1 <image>
trivy image --format sarif --output report.sarif <image>

# Grype
grype <image> --only-fixed --fail-on high

# Clair (intégré registre)
clairctl analyze <image>

# Docker Scout
docker scout quickview <image>
docker scout cves <image> --only-severity critical

# Snyk
snyk container test <image> --severity-threshold=high
```

### Image Hardening
```dockerfile
# Multi-stage build
FROM python:3.11-slim AS builder
# build dependencies

FROM python:3.11-slim AS runtime
# Minimal runtime
COPY --from=builder /app /app
RUN groupadd -r appuser && useradd -r -g appuser appuser
USER appuser
ENTRYPOINT ["python", "/app/main.py"]

# Pas de root
# USER 10001:10001 (non-root)
# readOnly: true
# capabilities: drop all, add only needed
```

### Image Signing (Cosign)
```bash
# Signer une image
cosign generate-key-pair
cosign sign --key cosign.key <registry>/image:tag

# Vérifier
cosign verify --key cosign.pub <registry>/image:tag

# Keyless (OIDC)
cosign sign <registry>/image:tag
cosign verify <registry>/image:tag

# Attestation SLSA
cosign attest --predicate slsa.json --type slsa.dev/v1 <registry>/image:tag
```

### Registry Security
```bash
# ECR (AWS)
# Image scanning on push
aws ecr put-image-scanning-configuration --repository <name> --image-scanning-configuration scanOnPush=true

# GCR (GCP)
# Vulnerability scanning (automatique)
gcloud artifacts repositories list
gcloud artifacts docker images list <location>/<repo>

# ACR (Azure)
# Defender for Containers scanning
az acr show --name <registry> --query "policies.quarantinePolicy"
az acr update --name <registry> --anonymous-pull-enabled false
```

---

## 3. Amazon EKS Security

### Cluster Creation Hardened
```bash
# Private cluster
eksctl create cluster --name prod --region us-east-1 --nodegroup-name workers --node-type t3.medium --nodes 3 --node-private-networking

# Audit logging
aws eks update-cluster-config --name prod --logging '{"clusterLogging":[{"types":["api","audit","authenticator","controllerManager","scheduler"],"enabled":true}]}'

# Encryption (KMS)
aws eks create-cluster ... --encryption-config '{"resources":["secrets"],"provider":{"keyArn":"arn:aws:kms:...:key/..."}}'

# IAM Roles for Service Accounts (IRSA)
eksctl create iamserviceaccount --name app-sa --namespace prod --cluster prod --attach-policy-arn arn:aws:iam::...:policy/app-policy
```

### EKS Security Best Practices
```bash
# 1. Pod Identity (au lieu de IRSA)
aws eks create-pod-identity-association --cluster-name prod --namespace prod --service-account app-sa --role-arn arn:aws:iam::...:role/pod-role

# 2. Security Groups for Pods
# SecurityGroupPolicy pour les pods
aws elbv2 create-target-group ...

# 3. VPC CNI + Network Policies
kubectl apply -f https://raw.githubusercontent.com/aws/amazon-vpc-cni-k8s/master/config/master/calico-operator.yaml

# 4. EKS Fargate (sans node)
eksctl create fargateprofile --cluster prod --namespace prod --name prod-fargate

# 5. Bottlerocket OS (minimal, security-focused)
eksctl create nodegroup --cluster prod --node-type t3.medium --node-ami-family Bottlerocket
```

---

## 4. GKE Security

### GKE Cluster Hardening
```bash
# Private cluster
gcloud container clusters create prod-cluster \
  --enable-private-nodes \
  --enable-private-endpoint \
  --master-ipv4-cidr 172.16.0.0/28 \
  --enable-master-authorized-networks \
  --master-authorized-networks <ip-range>

# Workload Identity
gcloud container clusters update prod-cluster --workload-pool=<project>.svc.id.goog
kubectl annotate serviceaccount app-sa --namespace prod iam.gke.io/gcp-service-account=<sa>@<project>.iam.gserviceaccount.com

# Shielded Nodes
gcloud container node-pools create shielded-nodes --cluster prod-cluster --shielded-secure-boot --shielded-integrity-monitoring

# Confidential VMs (chiffrement en mémoire)
gcloud container node-pools create confidential --cluster prod-cluster --confidential-nodes

# Data Plane V2 (ebpf-based network policy)
gcloud container clusters create prod-cluster --enable-dataplane-v2
```

### GKE Security Features
```bash
# Binary Authorization (image signing enforcement)
gcloud container binauthz policy create --default-admission-rule deny
gcloud container binauthz attestations create --artifact-url <image> --public-key-id <key>

# Config Connector (IAM via K8s CRDs)
kubectl apply -f iam-policy.yaml

# GKE Sandbox (hypervisor isolation)
gcloud container node-pools create sandbox --cluster prod-cluster --sandbox type=gvisor

# GKE Autopilot (sécurité gérée)
gcloud container clusters create auto --autopilot --region us-central1
```

---

## 5. AKS Security

### AKS Cluster Hardening
```bash
# Private cluster
az aks create --name prod-aks --resource-group <RG> --enable-private-cluster --enable-managed-identity

# Azure AD Integration
az aks create --name prod-aks --resource-group <RG> --enable-aad --aad-admin-group-object-ids <admin-group-id>

# Azure Policy for AKS
az aks enable-addons --name prod-aks --resource-group <RG> --addons azure-policy

# Pod Identity
az aks create --name prod-aks --resource-group <RG> --enable-pod-identity
az aks pod-identity add --name app-identity --namespace prod --cluster prod-aks --identity-resource-id <identity>
```

### AKS Security Features
```bash
# Azure CNI + Network Policies
# Azure Network Policy Manager (NPM) ou Calico
az aks create --name prod-aks --resource-group <RG> --network-plugin azure --network-policy calico

# Container Insights
az aks enable-addons --name prod-aks --resource-group <RG> --addons monitoring

# Key Management Service (KMS with Key Vault)
az aks create --name prod-aks --resource-group <RG> --enable-encryption-at-host --enable-keyvault

# Defender for Cloud — Containers
az aks update --name prod-aks --resource-group <RG> --enable-defender
```

---

## 6. Admission Controllers

### OPA/Gatekeeper
```bash
# Installer Gatekeeper
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/master/deploy/gatekeeper.yaml

# Constraint template: deny privileged
cat > deny-privileged-template.yaml << 'EOF'
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8spspprivilegedcontainer
spec:
  crd:
    spec:
      names:
        kind: K8sPSPPrivilegedContainer
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8spspprivilegedcontainer
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          container.securityContext.privileged
          msg := sprintf("Container %v is privileged, not allowed", [container.name])
        }
EOF
kubectl apply -f deny-privileged-template.yaml

# Constraint
cat > deny-privileged-constraint.yaml << 'EOF'
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sPSPPrivilegedContainer
metadata:
  name: deny-privileged
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
EOF
kubectl apply -f deny-privileged-constraint.yaml
```

### Kyverno
```yaml
# Kyverno policy: deny latest tag
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-latest-tag
spec:
  validationFailureAction: enforce
  rules:
  - name: require-image-tag
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Using 'latest' tag is not allowed"
      pattern:
        spec:
          containers:
          - image: "!*:latest"
---
# Kyverno: add resource limits
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: add-resource-limits
spec:
  validationFailureAction: audit
  rules:
  - name: add-limits
    match:
      resources:
        kinds:
        - Pod
    mutate:
      patchStrategicMerge:
        spec:
          containers:
          - (name): "*"
            resources:
              limits:
                memory: "512Mi"
                cpu: "500m"
```

### Pod Security Standards (PSS)
```bash
# Baseline — minimal restrictions
kubectl label --overwrite ns prod pod-security.kubernetes.io/enforce=baseline
kubectl label --overwrite ns prod pod-security.kubernetes.io/audit=restricted
kubectl label --overwrite ns prod pod-security.kubernetes.io/warn=restricted

# Restricted — maximum security
# (similar to old PSP restricted)
```

---

## 7. Runtime Security

### Falco
```bash
# Installation
helm install falco falcosecurity/falco --set driver.kind=ebpf

# Règles Falco
# Lancement de shell dans un conteneur
# Reverse shell
# Montage de /var/run/docker.sock
# Modification de binaires système
# Write below /etc
# Sensitive mount (hostPath)
# Privileged container

# Alertes Falco
curl -s http://localhost:8765/metrics
falco # logs en continu
```

### Tracee
```bash
# Runtime tracing via eBPF
docker run --name tracee --rm --privileged -v /lib/modules:/lib/modules:ro -v /tmp/tracee:/tmp/tracee aquasec/tracee

# Détection: nouveau binaire exécuté
# Détection: syscall inhabituel
# Détection: container escape
```

### Network Security Policies
```yaml
# Deny all ingress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: prod
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
# Allow web → app only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web-to-app
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: app
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: web
    ports:
    - protocol: TCP
      port: 8080
---
# Egress only to database
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-app-to-db
  namespace: prod
spec:
  podSelector:
    matchLabels:
      app: app
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: db
    ports:
    - protocol: TCP
      port: 5432
```

### Cilium — eBPF Networking
```bash
# Installer Cilium
helm install cilium cilium/cilium --namespace kube-system \
  --set hubble.enabled=true \
  --set hubble.relay.enabled=true \
  --set hubble.ui.enabled=true

# Hubble (observabilité réseau)
hubble observe --since 5m
hubble observe --pod prod/web-xxxx

# Cilium Network Policies (L3-L7)
cat > cilium-policy.yaml << 'EOF'
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata:
  name: allow-http-get
  namespace: prod
spec:
  endpointSelector:
    matchLabels:
      app: app
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: web
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
EOF
```

---

## 8. CIS Benchmarks

### kube-bench
```bash
# Installer kube-bench
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml

# Voir les résultats
kubectl logs job.batch/kube-bench

# Checks critiques:
# 1.1.1 - API server --anonymous-auth=false
# 1.1.3 - API server --profiling=false
# 1.1.5 - API server --kubelet-certificate-authority
# 1.2.2 - Controller manager --profiling=false
# 1.3.1 - Scheduler --profiling=false
# 2.1 - etcd --client-cert-auth
# 4.1.1 - Kubelet --anonymous-auth=false
# 5.1.5 - RBAC: cluster-admin restricted
# 5.4.1 - Prefer using secrets over env vars
```

### kubescape
```bash
# Scan complet
kubescape scan --enable-host-scan --format sarif --output kubescape-report.sarif

# Framework NSA/CISA
kubescape scan framework nsa

# Framework MITRE
kubescape scan framework mitre
```

---

## 9. Secrets Management dans K8s

```yaml
# External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secret-store
  namespace: prod
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-password
  namespace: prod
spec:
  refreshInterval: "1h"
  secretStoreRef:
    name: aws-secret-store
    kind: SecretStore
  target:
    name: db-password-secret
  data:
  - secretKey: password
    remoteRef:
      key: prod/db/password
```

---

## 10. Container Security Checklist

```
IMAGES
☐ Images minimales (slim, distroless)
☐ Multi-stage builds
☐ Non-root user
☐ Image scanning (Trivy/Grype) CI intégré
☐ Image signing (Cosign)
☐ Registry avec scanning on push
☐ Aucune image :latest en production

CLUSTER
☐ RBAC — cluster-admin restreint
☐ Service accounts sans automount par défaut
☐ Secrets chiffrés (KMS)
☐ Audit logging activé
☐ CIS benchmark < 50 failures
☐ Network policies appliquées
☐ Pod Security Standards (restricted)
☐ OPA/Kyverno admission policies

RUNTIME
☐ Falco installé et actif
☐ LectureSeccomp profil appliqué
☐ AppArmor/SELinux
☐ Read-only root filesystem
☐ SecurityContext: drop ALL capabilities
☐ Seccomp: RuntimeDefault

RÉSEAU
☐ Network policies — deny-all par défaut
☐ mTLS (service mesh ou Cilium)
☐ Aucun hostNetwork
☐ Aucun hostPort
☐ Egress filtré
☐ NodePort évité (Ingress + LB)

OBSERVABILITÉ
☐ kubescape scan régulier
☐ kube-bench run périodique
☐ Container Insights / Managed Prometheus
☐ Runtime anomaly detection
☐ Audit logs analysés (SIEM)
```

## Ressources

- **Kubernetes Security**: https://kubernetes.io/docs/concepts/security/
- **CIS Kubernetes Benchmark**: https://www.cisecurity.org/benchmark/kubernetes
- **NSA/CISA Kubernetes Hardening**: https://media.defense.gov/2022/Aug/29/2003066362/-1/-1/0/CTR_KUBERNETES_HARDENING_GUIDANCE_1.2_20220829.PDF
- **Falco Rules**: https://falco.org/docs/rules/
- **Kyverno Policies**: https://kyverno.io/policies/
- **Gatekeeper Library**: https://github.com/open-policy-agent/gatekeeper-library
- **EKS Best Practices**: https://aws.github.io/aws-eks-best-practices/
- **GKE Security**: https://cloud.google.com/kubernetes-engine/docs/concepts/security-overview
- **AKS Security**: https://docs.microsoft.com/en-us/azure/aks/concepts-security