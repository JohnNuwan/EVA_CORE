---
name: cloud-defense-hardening
description: Guide complet de durcissement et défense cloud — CIS benchmarks, Security Score, hardening AWS/GCP/Azure, least privilege, network segmentation, encryption, logging, et monitoring
category: cybersecurite
---

# Cloud Defense & Hardening — Guide Multi-Cloud

---

## Principes Fondamentaux

### Shared Responsibility Model
```
┌─────────────────────────────────────────────────┐
│                    CUSTOMER                       │
│  Données, Chiffrement côté client, IAM, Réseau   │
├─────────────────────────────────────────────────┤
│                   CLOUD PROVIDER                  │
│  Infrastructure physique, Hyperviseur, Réseau     │
│  (AWS: jusqu'à l'OS hôte | SaaS: jusqu'à l'app)  │
└─────────────────────────────────────────────────┘
```

### Pillars de la Défense Cloud
1. **Identity & Access** — Least privilege, MFA, Zero Trust
2. **Network Security** — Segmentation, micro-segmentation, WAF
3. **Data Protection** — Encryption at rest/in transit, key management
4. **Logging & Monitoring** — Audit trails, SIEM, threat detection
5. **Compliance** — CIS benchmarks, regulatory frameworks
6. **Incident Response** — Playbooks, forensic readiness
7. **Infrastructure** — Secure IaC, patch management, scanning

---

## 1. CIS Benchmarks par Provider

### AWS CIS Foundations Benchmark
```bash
# Installation de Prowler
pip install prowler

# CIS AWS
prowler aws -g cis_1.4
prowler aws -g cis_1.5  # Latest

# Checks critiques:
# 1.1 - IAM password policy
# 1.3 - IAM users with console access have MFA
# 1.4 - No root user access keys
# 1.5 - IAM policies attached to groups/roles only
# 2.1 - CloudTrail enabled
# 2.4 - S3 buckets with public access blocked
# 3.1 - CloudTrail log file validation
# 4.1 - Security Groups with unrestricted access

# Format sortie
prowler aws -M csv,json,html
```

### GCP CIS Benchmark
```bash
# Prowler GCP
prowler gcp -p <project-id> -g cis_1.2

# Checks CIS GCP:
# 1.1 - IAM default service accounts disabled
# 1.2 - IAM roles with separation of duties
# 2.1 - Cloud Audit Logs enabled
# 2.2 - Logging sinks configured
# 3.1 - VPC Flow Logs enabled
# 4.1 - GKE clusters with private clusters
# 5.1 - Cloud SQL with SSL/TLS
# 6.1 - Cloud Storage uniform bucket-level access

# ScoutSuite
scout gcp --project-id <project>
```

### Azure CIS Benchmark
```bash
# Prowler Azure
prowler azure -g cis_2.0

# Checks CIS Azure:
# 1.1 - Security Contacts with phone/email
# 2.1 - Microsoft Defender for Cloud enabled
# 3.1 - RBAC with least privilege
# 4.1 - NSG with no unrestricted access (22, 3389)
# 5.1 - Key Vault with purge protection
# 6.1 - SQL Server with AD-only auth
# 7.1 - Diagnostic logs enabled
# 8.1 - Azure Policy with mandatory tags

# Azure Security Score
az security secure-score list --output table
```

---

## 2. IAM Hardening

### AWS IAM Hardening
```bash
# 1. Password policy forte
aws iam update-account-password-policy \
  --minimum-password-length 16 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 24

# 2. No inline policies — use managed policies
aws iam list-user-policies --user-name <user>

# 3. Permission boundaries
# Créer une boundary policy
# Attacher à l'utilisateur/role
aws iam put-user-permissions-boundary \
  --user-name <user> \
  --permissions-boundary arn:aws:iam::...:policy/boundary

# 4. MFA obligatoire
# IAM policy for MFA enforcement
aws iam create-policy --policy-name EnforceMFAPolicy --policy-document file://mfa-policy.json

# 5. Access Analyzer
aws accessanalyzer create-analyzer --analyzer-name <name> --type ACCOUNT
```

### GCP IAM Hardening
```bash
# 1. Désactiver les service accounts par défaut
gcloud iam service-accounts list
gcloud iam service-accounts disable <email>

# 2. Audit des rôles
gcloud projects get-iam-policy <project> --format json | jq '.bindings[] | select(.role | test("owner|editor"))'

# 3. Principe de moindre privilège
# Utiliser des rôles prédéfinis, pas primitifs (owner/editor/viewer)
# gcloud projects add-iam-policy-binding avec conditions
gcloud projects add-iam-policy-binding <project> \
  --member user:email@domain.com \
  --role roles/storage.objectViewer \
  --condition "expression=request.time < timestamp('2026-01-01T00:00:00Z'),title=temp-access"

# 4. OS Login activé (pas de SSH keys)
gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE
```

### Azure RBAC Hardening
```bash
# 1. Custom roles avec least privilege
az role definition create --role-definition @custom-role.json

# 2. Azure AD Privileged Identity Management (PIM)
# Activation just-in-time des rôles privilégiés
az rest --method get --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01"

# 3. Conditional Access
# Bloque les accès depuis des IP non autorisées
# Exige MFA pour les rôles admin

# 4. Managed Identities (pas de credentials hardcodés)
az vm assign-identity --name <vm> --resource-group <RG>
```

---

## 3. Data Protection

### Encryption at Rest
```bash
# AWS: KMS CMK obligatoire
aws kms create-key --description "Production Key"
aws s3api put-bucket-encryption --bucket <name> --server-side-encryption-configuration '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms","KMSMasterKeyID":"<key-id>"}}]}'

# GCP: CMEK
gcloud kms keyrings create prod --location global
gcloud kms keys create prod-key --keyring prod --location global --purpose encryption
gcloud storage buckets update gs://<bucket> --encryption-key projects/<project>/locations/global/keyRings/prod/cryptoKeys/prod-key

# Azure: Customer-Managed Key
az storage account update --name <account> --resource-group <RG> --encryption-key-name <key> --encryption-key-source Microsoft.Keyvault
```

### Encryption in Transit
```bash
# AWS: TLS 1.2+ only
# CloudFront avec TLS 1.2_2021 security policy
# ELB avec TLS 1.2 policies

# GCP: SSL policies
gcloud compute ssl-policies create tls-1-2 --profile MODERN --min-tls-version 1.2

# Azure: Enforce HTTPS
az webapp update --name <app> --resource-group <RG> --https-only true
```

### Secrets Management
```bash
# AWS: Secrets Manager + Rotation automatique
aws secretsmanager rotate-secret --secret-id <name>

# GCP: Secret Manager + IAM Conditions
gcloud secrets add-iam-policy-binding <secret> --member user:email@domain.com --role roles/secretmanager.secretAccessor

# Azure: Key Vault avec RBAC + Soft Delete
az keyvault update --name <vault> --enable-soft-delete true --enable-purge-protection true
```

---

## 4. Network Security

### AWS Network Hardening
```bash
# 1. Security Groups — deny all inbound by default
# No 0.0.0.0/0 on SSH (22), RDP (3389), DB ports

# 2. VPC Flow Logs
aws ec2 create-flow-logs --resource-type VPC --resource-id vpc-xxx --traffic-type ALL --log-group-name vpc-flow-logs

# 3. Network ACLs — stateless filtering
aws ec2 create-network-acl-entry --network-acl-id acl-xxx --rule-number 100 --protocol tcp --port-range From=443,To=443 --cidr-block 10.0.0.0/8 --rule-action allow --egress

# 4. AWS WAF
aws wafv2 create-web-acl --name waf-prod --scope REGIONAL --default-action Allow={} --rules file://waf-rules.json

# 5. AWS Shield Advanced (DDoS)
aws shield create-subscription

# 6. PrivateLink pour les services exposés
# Point d'accès VPC pour S3, DynamoDB, etc.
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx --service-name com.amazonaws.region.s3
```

### GCP Network Hardening
```bash
# 1. VPC Firewall Rules — deny all ingress
gcloud compute firewall-rules create deny-all --direction INGRESS --priority 65535 --action DENY --rules all

# 2. Private Google Access
gcloud compute networks subnets update <subnet> --enable-private-ip-google-access

# 3. VPC Service Controls
gcloud access-context-manager perimeters create <perimeter> --perimeter-type regular --resources projects/<project> --restricted-services storage.googleapis.com

# 4. Cloud Armor (WAF)
gcloud compute security-policies create waf-policy
gcloud compute security-policies rules create 1000 --security-policy waf-policy --action "deny(403)" --expression "evaluatePreconfiguredExpr('xss-v33-stable')"

# 5. Packet Mirroring (traffic inspection)
gcloud compute packet-mirrorings create mirror --collector-ilb <ilb> --network <vpc> --filter direction=INGRESS
```

### Azure Network Hardening
```bash
# 1. NSG rules — deny by default, explicit allow
az network nsg rule create --nsg-name <NSG> --resource-group <RG> --name Allow-HTTPS --priority 100 --direction Inbound --access Allow --protocol Tcp --destination-port-ranges 443 --source-address-prefixes VirtualNetwork

# 2. Azure Firewall
az network firewall create --name <fw> --resource-group <RG> --sku AZFW_VNet

# 3. Azure DDoS Protection
az network ddos-protection create --resource-group <RG> --name ddos-protection --vnets <vnet>

# 4. Private Endpoints
az network private-endpoint create --name <pe> --resource-group <RG> --vnet-name <vnet> --subnet <subnet> --private-connection-resource-id <resource-id>
```

---

## 5. Logging & Monitoring

### AWS Logging
```bash
# 1. CloudTrail multi-region + management/data events
aws cloudtrail create-trail --name prod-trail --s3-bucket-name <bucket> --is-multi-region-trail --enable-log-file-validation
aws cloudtrail update-trail --name prod-trail --is-organization-trail

# 2. GuardDuty
aws guardduty create-detector --enable

# 3. Security Hub
aws securityhub enable-security-hub

# 4. Config Rules
aws configservice put-config-rule --config-rule file://s3-public-read-prohibited.json

# 5. CloudWatch Alarms
aws cloudwatch put-metric-alarm --alarm-name RootActivity --metric-name RootAccountUsage --namespace AWS/CloudTrail --statistic Sum --period 300 --evaluation-periods 1 --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold
```

### GCP Logging
```bash
# 1. Audit Logs obligatoires
# Admin Activity: toujours activé
# Data Access: à activer pour toutes les APIs
gcloud projects get-iam-policy <project> --format json | jq '.auditConfigs'

# 2. Log Sinks vers BigQuery/S3
gcloud logging sinks create prod-sink bigquery.googleapis.com/projects/<project>/datasets/audit --log-filter="severity>=WARNING"

# 3. Security Command Center
gcloud scc notifications create <notification> --organization <org> --description "Security alerts"

# 4. Threat Detection
gcloud scc mute-configs create auto-mute --description "Auto-mute low severity"
```

### Azure Monitoring
```bash
# 1. Diagnostic Settings — tous les services
az monitor diagnostic-settings create --name "audit" --resource <id> --logs '[{"category":"AuditEvent","enabled":true}]' --workspace <ws-id>

# 2. Microsoft Sentinel
az sentinel setting set --workspace-name <ws> --resource-group <RG> --entity-analytics enabled

# 3. Azure Policy — audit et enforce
az policy assignment create --policy "Audit unrestricted network access to storage accounts" --name audit-storage

# 4. Azure Monitor Alerts
az monitor metrics alert create --name "High CPU" --resource-group <RG> --scopes <vm-id> --condition "avg Percentage CPU > 90" --window-size 5m --evaluation-frequency 1m
```

---

## 6. Infrastructure as Code Security

### Terraform Security
```bash
# Checkov — scan IaC
checkov -d ./terraform/ --framework terraform
checkov -f main.tf --output cli,sarif

# tfsec — security scanner
tfsec ./terraform/
tfsec --config-file .tfsec/config.yml

# terrascan
terrascan scan -d ./terraform/ -t aws

# sentinel (Hashicorp policy as code)
# https://developer.hashicorp.com/terraform/cloud-docs/policy-enforcement
```

### Secure IaC Patterns
```hcl
# AWS S3 — private par défaut
resource "aws_s3_bucket" "data" {
  bucket = "secure-bucket-${var.environment}"
}

resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# GCP — deny public buckets
resource "google_storage_bucket_iam_binding" "no_public" {
  bucket = google_storage_bucket.data.name
  role   = "roles/storage.objectViewer"
  members = [
    "serviceAccount:${google_service_account.data.email}"
  ]
}

# Azure — deny public network access
resource "azurerm_storage_account" "secure" {
  name                     = "securesa${var.environment}"
  account_tier             = "Standard"
  account_replication_type = "GRS"
  allow_nested_items_to_be_public = false
  public_network_access_enabled  = false
  network_rules {
    default_action = "Deny"
  }
}
```

---

## 7. Container Security

### Image Scanning
```bash
# Trivy (multi-format)
trivy image --severity CRITICAL,HIGH <image>
trivy repo --severity CRITICAL https://github.com/org/repo
trivy fs --severity CRITICAL ./deployment/

# Grype
grype <image> --fail-on high

# Clair
clair-scanner --ip <host> --report output.json <image>
```

### Admission Controllers
```bash
# OPA/Gatekeeper — enforce policies
# Kyverno — Kubernetes policy engine
# Azure Policy for AKS

# Exemple Kyverno: deny privileged containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-privileged
spec:
  validationFailureAction: enforce
  rules:
  - name: check-privileged
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Privileged containers are not allowed"
      pattern:
        spec:
          containers:
          - securityContext:
              privileged: false
```

---

## 8. Cloud Security Tools Matrix

| Outil | AWS | GCP | Azure | Usage |
|-------|-----|-----|-------|-------|
| **Prowler** | ✓ | ✓ | ✓ | Audit CIS + custom |
| **ScoutSuite** | ✓ | ✓ | ✓ | Configuration audit |
| **Checkov** | ✓ | ✓ | ✓ | IaC scanning |
| **Trivy** | ✓ | ✓ | ✓ | Image/FS/Repo scan |
| **CloudSploit** | ✓ | ✓ | ✓ | Security scanning |
| **kube-bench** | ✓ | ✓ | ✓ | K8s CIS benchmark |
| **kubescape** | ✓ | ✓ | ✓ | K8s security |
| **tfsec** | ✓ | ✓ | ✓ | Terraform security |
| **Security Hub** | ✓ | ✗ | ✗ | AWS native |
| **Security Command Center** | ✗ | ✓ | ✗ | GCP native |
| **Defender for Cloud** | ✗ | ✗ | ✓ | Azure native |

## Ressources

- **CIS Benchmarks**: https://www.cisecurity.org/benchmark/cloud
- **CIS AWS**: https://www.cisecurity.org/benchmark/amazon_web_services
- **CIS GCP**: https://www.cisecurity.org/benchmark/google_cloud_computing_platform
- **CIS Azure**: https://www.cisecurity.org/benchmark/azure
- **Cloud Security Alliance**: https://cloudsecurityalliance.org/
- **OWASP Cloud Security**: https://owasp.org/www-project-cloud-security/
- **NIST Cloud Computing**: https://www.nist.gov/programs-projects/nist-cloud-computing-program
- **WAF Bypass Techniques**: https://github.com/0xInfection/Awesome-WAF