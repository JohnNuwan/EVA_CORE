---
name: multi-cloud-architecture
description: Guide complet d'architecture multi-cloud — patterns de déploiement, networking cross-cloud, fédération d'identité, DR/BCP, data sovereignty, vendor lock-in avoidance, service mesh, observabilité unifiée
category: cybersecurite
---

# Multi-Cloud Architecture & Security

---

## 1. Multi-Cloud Patterns

### Architecture Patterns
```
┌─────────────────────────────────────────────────────────────────┐
│                    MULTI-CLOUD ARCHITECTURES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│ 1. Active-Passive (DR)                                           │
│    ┌─────┐   ┌─────┐                                            │
│    │AWS   │ ← │GCP  │  (standby / cold / warm)                   │
│    └─────┘   └─────┘                                            │
│                                                                   │
│ 2. Active-Active (Load Sharing)                                  │
│    ┌──────┐    ┌──────┐                                         │
│    │AWS   ├────┤Azure │  (round-robin, geo-routing)               │
│    └──────┘    └──────┘                                         │
│                                                                   │
│ 3. Distributed (Microservices)                                   │
│    ┌───────────────────────────────┐                            │
│    │  Service A (AWS)              │                            │
│    │  Service B (GCP)              │                            │
│    │  Service C (Azure)            │                            │
│    │  DB / Cache (shared)          │                            │
│    └───────────────────────────────┘                            │
│                                                                   │
│ 4. Data Sovereignty (Regions)                                    │
│    ┌──────┐ ┌──────┐ ┌──────┐                                  │
│    │AWS-US│ │GCP-EU│ │Azure-Asia│ (GDPR, local laws)            │
│    └──────┘ └──────┘ └──────┘                                  │
│                                                                   │
│ 5. Vendor-Specific Best Fit                                      │
│    ┌────────────────────────────┐                               │
│    │AWS: AI/ML (SageMaker)       │                               │
│    │GCP: Big Data (BigQuery)     │                               │
│    │Azure: Enterprise (AD/O365)  │                               │
│    └────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### Decision Matrix
| Critère | AWS | GCP | Azure |
|---------|-----|-----|-------|
| **AI/ML** | SageMaker, Bedrock | Vertex AI | Azure ML |
| **Data/Analytics** | EMR, Athena, Redshift | BigQuery, Dataflow | Synapse, Data Lake |
| **Serverless** | Lambda | Cloud Functions | Functions |
| **Kubernetes** | EKS | GKE (best) | AKS |
| **Enterprise AD** | IAM + SSO | Workforce Identity | Azure AD (best) |
| **Hybrid Cloud** | Outposts | Anthos | Azure Arc |
| **CDN** | CloudFront | Cloud CDN | Front Door |
| **Global Reach** | 33 regions | 40+ regions | 60+ regions |

---

## 2. Multi-Cloud Networking

### Cross-Cloud Connectivity

**AWS → GCP via Private Connectivity**
```bash
# Option 1: Direct Peering (VPN)
# AWS: Virtual Private Gateway → Site-to-Site VPN
# GCP: Cloud VPN Gateway → Tunnel

# AWS side
aws vpn-connection create \
  --customer-gateway-id <cgw> \
  --type ipsec.1 \
  --vpn-gateway-id <vgw>

# GCP side
gcloud compute vpn-tunnels create aws-tunnel-1 \
  --region us-central1 \
  --peer-address <aws-vpn-endpoint> \
  --shared-secret <secret> \
  --ike-version 2 \
  --local-traffic-selector 10.0.0.0/8 \
  --remote-traffic-selector 172.16.0.0/12
```

**AWS → Azure via Private Connectivity**
```bash
# AWS: Transit Gateway + VPN
# Azure: Virtual Network Gateway

# Option 2: Equinix / Megaport direct connect
# AWS Direct Connect → Equinix → Azure ExpressRoute
```

**Multi-Cloud Service Mesh**
```yaml
# Istio — mTLS cross-cloud
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: gcp-service
spec:
  hosts:
  - svc.gcp.cluster.local
  addresses:
  - 10.200.0.0/16
  ports:
  - number: 8080
    name: http
    protocol: HTTP
  resolution: DNS
  endpoints:
  - address: gcp-cluster.internal.example.com
    ports:
      http: 80
```

### DNS Multi-Cloud
```bash
# AWS Route 53 — multi-cloud routing
# Latency-based: redirect to closest cloud
# Geolocation: EU → GCP, US → AWS, Asia → Azure
# Failover: primary cloud → secondary

# Exemple: Route53 Failover
# Primary: ALB in AWS us-east-1 (health check /health)
# Secondary: GCP LB in us-central1 (health check /health)
aws route53 create-health-check --caller-reference hc-app --health-check-config Type=HTTP,FullyQualifiedDomainName=app.aws.com,Port=443,ResourcePath=/health

# GCP Cloud DNS — multi-cloud routing
gcloud dns managed-zones create multi-cloud --description "Multi-cloud routing" --dns-name "app.example.com."
```

### CDN Multi-Cloud
```bash
# AWS CloudFront + GCP + Azure origins
# CloudFront distribution avec origins multiples
# Origin groups: failover entre regions
aws cloudfront create-origin-group \
  --origin-group-config '{"OriginGroupMembers":{"Items":[{"Id":"aws-origin"},{"Id":"gcp-origin"}],"Quantity":2},"FailoverCriteriaSpec":{"StatusCodeFailures":{"Items":[502,503,504],"Quantity":3}}}'
```

---

## 3. Multi-Cloud Identity Federation

### Federation Patterns
```
User → IdP (Azure AD)
         ├── AWS IAM Identity Center (SSO)
         ├── GCP Workforce Identity Federation
         └── Azure AD itself (native)
```

### Azure AD as Central IdP
```bash
# AWS IAM Identity Center (SSO) + Azure AD
# SAML 2.0: Azure AD → AWS SSO
# Provisioning: SCIM → automatic user sync

# GCP Workforce Identity Federation
gcloud iam workforce-pools create azure-pool --location global
gcloud iam workforce-pools providers create-saml azure-provider \
  --location global \
  --workforce-pool azure-pool \
  --identity-provider-arn "arn:aws:iam::<account>:saml-provider/AzureAD" \
  --attribute-mapping "google.subject=assertion.sub"

# Attribute-based access (ABAC)
# Tags AWS: environment=prod, team=platform
# Labels GCP: environment=prod, team=platform
# Tags Azure: environment=prod, team=platform
```

### Cross-Cloud IAM Mapping
```yaml
# AWS IAM → GCP → Azure
# Principal mapping:
AWS: arn:aws:iam::<account>:role/Admin
GCP:  user:admin@domain.com (via federation)
Azure: user:admin@domain.com (native Azure AD)

# Permission hierarchy:
# AWS: AdministratorAccess + SCP
# GCP: roles/owner (organization)
# Azure: Global Administrator
```

---

## 4. Multi-Cloud DR / BCP

### DR Strategies

| Strategy | RPO | RTO | Cost |
|----------|-----|-----|------|
| **Backup & Restore** | 24h | 24-48h | Low |
| **Pilot Lite** | 15min | 1-4h | Medium |
| **Warm Standby** | 5min | 15-60min | Medium-High |
| **Active-Active** | 0s | 0-30s | High |
| **Multi-Site Active** | 0s | 0s | Very High |

### DR Automation

```bash
# AWS → GCP DR failover
# Route53 → GCP DNS on failure

# 1. Replicate data
# AWS RDS → GCP Cloud SQL (via DMS or CDC)
aws dms create-replication-task ...

# 2. Replicate images (ECR → GCR)
# Image replication with skopeo
skopeo copy docker://<ecr>/app:latest docker://<gcr>/app:latest

# 3. Infrastructure as Code
# Terraform: manage both AWS and GCP
# Terragrunt: DR config between clouds

# 4. Automation failover
# Lambda + Cloud Function + Azure Function
# Health check → switch DNS → notify
```

### Cloud SQL DR Replication
```bash
# PostgreSQL — cross-cloud replication
# AWS RDS → GCP Cloud SQL → Azure DB

# AWS: logical replication (pglogical)
aws rds create-db-instance-read-replica --source-db-instance-identifier <source> --db-instance-identifier dr-replica

# GCP: cross-region replica
gcloud sql instances create dr-replica --master-instance-name <source> --region europe-west1
```

---

## 5. Data Sovereignty & Compliance

### Regional Data Residency
```bash
# AWS — S3 Object Lock (WORM)
aws s3api put-object-legal-hold --bucket <bucket> --key <key> --legal-hold Status=ON

# GCP — Organization Policy: location restriction
gcloud resource-manager org-policies set-policy --organization=<org> file://location-policy.yaml

cat > location-policy.yaml << 'EOF'
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
  - europe-west1
  - europe-west2
  - europe-west3
  deniedValues: []
EOF

# Azure — Azure Policy: allowed locations
az policy definition create --name allowed-locations --rules '{"if":{"field":"location","notIn":["europewest","francecentral"]},"then":{"effect":"deny"}}'
```

### Multi-Cloud Encryption Key Hierarchy
```bash
# Root key: Cloud HSM (AWS CloudHSM / GCP Cloud HSM / Azure Managed HSM)
# Regional keys: KMS (AWS KMS / GCP Cloud KMS / Azure Key Vault)
# Data keys: envelope encryption per object

# Envelope encryption cross-cloud:
# 1. Generate DEK in primary cloud KMS
# 2. Encrypt data with DEK
# 3. Wrap DEK with KEK
# 4. Store wrapped DEK with data
# 5. Decrypt: unwrap DEK with KEK in respective cloud
```

---

## 6. Multi-Cloud Observability

### Unified Logging Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                         SIEM / Observability                    │
│  Splunk / ELK / Sentinel / Datadog / Grafana Cloud               │
├────────┬────────┬────────┬────────┬────────┬────────┬───────────┤
│ AWS    │ GCP    │ Azure  │ K8s    │ App    │ Sec    │ Cost      │
│GuardDuty│SCC    │Defender│kube-   │APM     │Hub     │Anomaly   │
│CloudTr.│Logging│Activity│bench   │logs    │Findings│Budgets    │
│VPC Flw│Metrics│Monitor │Events  │Metrics │Alerts  │Reserved   │
└────────┴────────┴────────┴────────┴────────┴────────┴───────────┘
```

### Centralized Alerting
```yaml
# Grafana — multi-cloud dashboards
# Datasources: CloudWatch, Cloud Monitoring, Azure Monitor
# Unified alert manager: PagerDuty / OpsGenie

# Prometheus federation
# prometheus --web.external-url https://monitoring.internal/
# Scrape: AWS Prometheus + GCP Managed Prometheus + Azure Prometheus

# Unified alert rules
- name: Multi-Cloud CPU
  rules:
  - alert: HighCPU
    expr: |
      avg(aws_ec2_cpu{instance=~"prod-.*"}) > 90
      or avg(gcp_gce_cpu{instance=~"prod-.*"}) > 90
      or avg(azure_vm_cpu{vm=~"prod-.*"}) > 90
    for: 5m
```

### Multi-Cloud Cost Dashboard
```sql
-- BigQuery — multi-cloud cost analysis
SELECT
  cloud_provider,
  service,
  SUM(cost) as total_cost,
  SUM(usage_amount) as total_usage
FROM (
  SELECT 'AWS' as cloud_provider, line_item_type as service, cost, usage_amount
  FROM aws_cur.cost_and_usage
  UNION ALL
  SELECT 'GCP' as cloud_provider, service.description as service, cost, usage.amount as usage_amount
  FROM gcp_billing_export.gcp_billing_export_v1_*
  UNION ALL
  SELECT 'Azure' as cloud_provider, MeterCategory as service, CostInBillingCurrency as cost, Quantity as usage_amount
  FROM azure_consumption.details
)
GROUP BY cloud_provider, service
ORDER BY total_cost DESC
```

---

## 7. Vendor Lock-in Mitigation

### Provider-Agnostic Tooling
```bash
# Terraform — multi-provider IaC
# Kubernetes — portable workloads
# Istio — service mesh
# Prometheus + Grafana — monitoring
# Crossplane — control plane multi-cloud
# Crossplane Composition — abstract cloud resources

# Crossplane example
apiVersion: devopstoolkit.labs/v1alpha1
kind: SQL
metadata:
  name: my-db
spec:
  compositionSelector:
    matchLabels:
      provider: aws  # or gcp, azure
  parameters:
    size: small
    dbName: myapp-db
```

### Kubernetes — Workload Portability
```yaml
# K8s manifest portable between EKS, GKE, AKS
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
      - name: app
        image: myregistry/app:latest
        resources:
          requests:
            cpu: 500m
            memory: 256Mi
        env:
        - name: DB_URL
          valueFrom:
            secretKeyRef:
              name: db-config
              key: url
```

### API Compatibility Layer
```yaml
# Abstraction layer for cloud APIs
# Example: blob storage abstraction
objects:
  list:
    - AWS: aws s3 ls s3://bucket/
    - GCP: gsutil ls gs://bucket/
    - Azure: az storage blob list --container-name bucket
  upload:
    - AWS: aws s3 cp file s3://bucket/
    - GCP: gsutil cp file gs://bucket/
    - Azure: az storage blob upload -f file -c bucket
```

---

## 8. Security Considerations

### Multi-Cloud Security Risks
```
┌─────────────────────────────────────────────┐
│           Multi-Cloud Risks                  │
├─────────────────────────────────────────────┤
│ 1. Inconsistent IAM policies                │
│ 2. Complex key management (KMS ≠ Key Vault) │
│ 3. Network latency / bandwidth costs        │
│ 4. Compliance fragmentation                 │
│ 5. Monitoring gaps (alerts lost between)    │
│ 6. Skill asymmetry (team can't cover all)   │
│ 7. Data egress costs (cross-cloud transfer) │
│ 8. Incident response complexity             │
└─────────────────────────────────────────────┘
```

### Security Best Practices
```bash
# 1. Centralized Identity (Azure AD / Okta)
# SSO across all clouds
# Just-in-time access (PIM)

# 2. Consistent Encryption
# Same algorithm (AES-256-GCM)
# Envelope encryption
# Key rotation policies

# 3. Unified Logging
# All logs → central SIEM
# Consistent retention policies
# Immutable audit trails

# 4. Network Segmentation
# Dedicated interconnect/VPN per cloud
# No open peering
# Consistent firewall policies

# 5. Compliance Framework
# CIS benchmarks per cloud
# FedRAMP / SOC2 / ISO 27001
# Consistent tagging

# 6. Incident Response
# Runbook per scenario
# Cross-cloud playbooks
# Communication bridge
```

---

## 9. Tools & Frameworks

| Outil | Usage | Lien |
|-------|-------|------|
| **Terraform** | Multi-cloud IaC | terraform.io |
| **Crossplane** | Control plane multi-cloud | crossplane.io |
| **Terragrunt** | DRY Terraform | terragrunt.gruntwork.io |
| **Pulumi** | IaC avec langages prog | pulumi.com |
| **Istio** | Service mesh multi-cloud | istio.io |
| **Consul** | Service mesh + DNS | consul.io |
| **Kubefed** | K8s federation | github.com/kubernetes-sigs/kubefed |
| **Grafana** | Multi-cloud observability | grafana.com |
| **OpenCost** | K8s cost multi-cloud | opencost.io |
| **CloudHealth** | Multi-cloud cost | bmc.com |
| **CloudCheckr** | Multi-cloud security | cloudcheckr.com |

## Ressources

- **AWS Multi-Cloud Architecture**: https://aws.amazon.com/architecture/
- **GCP Multi-Cloud**: https://cloud.google.com/anthres/multicloud
- **Azure Multi-Cloud**: https://azure.microsoft.com/en-us/solutions/multicloud/
- **CNCF Cloud Native Security**: https://github.com/cncf/tag-security
- **NIST Multi-Cloud Security**: https://csrc.nist.gov/publications/detail/sp/800-207/final
- **Multi-Cloud Patterns**: https://martinfowler.com/articles/multi-cloud/
- **Well-Architected Framework Multi-Cloud**: https://aws.amazon.com/architecture/well-architected/