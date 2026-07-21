---
name: cloud-compliance-governance
description: Guide complet de la conformité et gouvernance cloud — SOC2, PCI-DSS, HIPAA, GDPR, FedRAMP, ISO 27001, AWS Organizations SCP, GCP Organization Policies, Azure Policy, compliance frameworks, audit logging, et reporting
domain: [cybersecurite, cloud, compliance]
tags: [compliance, governance, soc2, pci-dss, hipaa, gdpr, fedramp, iso-27001, scp, organization-policy, azure-policy, audit-logging]
priority: haute
---

# 📋 Cloud Compliance & Governance — Guide Multi-Cloud

Guide complet des frameworks de conformité cloud, gouvernance multi-compte, et automatisation de la conformité.

---

## 1. Frameworks de Conformité Cloud

### 1.1 Matrice des Frameworks par Provider

| Framework | AWS | GCP | Azure | Focus |
|-----------|-----|-----|-------|-------|
| **SOC 2** | ✓ Artifact | ✓ Compliance Reports | ✓ Service Trust Portal | Contrôles internes |
| **PCI-DSS v4** | ✓ (scope limité) | ✓ (GCP PCI) | ✓ (Azure PCI) | Données bancaires |
| **HIPAA** | ✓ BAA required | ✓ BAA required | ✓ BAA required | Données santé |
| **GDPR** | ✓ DPA | ✓ DPA | ✓ DPA | Données UE |
| **FedRAMP** | ✓ GovCloud | ✓ Assured Workloads | ✓ Azure Government | Gouvernement US |
| **ISO 27001** | ✓ | ✓ | ✓ | ISMS |
| **NIST 800-53** | ✓ GovCloud | ✓ Assured | ✓ Azure Gov | Sécurité fédérale |
| **CIS Benchmarks** | ✓ | ✓ | ✓ | Hardening |
| **HITRUST** | ✓ | ✓ | ✓ | Santé |
| **IRAP** | ✓ Sydney | ✓ | ✓ Australia | Australie |

### 1.2 Shared Responsibility Model par Framework

```
┌─────────────────────────────────────────────────────┐
│                  CUSTOMER RESPONSIBILITY              │
│  SOC2: Politiques, contrôles internes, audits       │
│  PCI:  Cardholder data, CDE, segmentation           │
│  HIPAA: ePHI, BAAs, access controls                 │
│  GDPR: Data processing, DPIAs, consent              │
├─────────────────────────────────────────────────────┤
│              SHARED RESPONSIBILITY                    │
│  SOC2: Logical/physical security                     │
│  PCI:  Network security, encryption                 │
│  HIPAA: Encryption, access controls                 │
│  GDPR: Data processing agreements                   │
├─────────────────────────────────────────────────────┤
│             CLOUD PROVIDER RESPONSIBILITY             │
│  PHYSICAL SECURITY, INFRASTRUCTURE                   │
│  SOC2: Type II report (controls)                     │
│  PCI:  Attestation of Compliance (AoC)              │
│  HIPAA: BAA, physical security                      │
│  GDPR: Data processor, DPA                          │
└─────────────────────────────────────────────────────┘
```

---

## 2. SOC 2 dans le Cloud

### 2.1 Trust Services Criteria

| Catégorie | Critère | Contrôle Cloud |
|-----------|---------|----------------|
| **Security** | CC6.1 Logical access | IAM, MFA, least privilege |
| **Availability** | CC7.1 Monitoring | GuardDuty, CloudWatch, Azure Monitor |
| **Processing Integrity** | CC8.1 Change management | IaC, CI/CD, Config |
| **Confidentiality** | CC6.6 Encryption | KMS, Secrets Manager, Key Vault |
| **Privacy** | CC9.1 Privacy notice | Data classification, DLP |

### 2.2 Evidence Collection Automatisée

```bash
# Script de collecte d'évidences SOC2

#!/bin/bash
# soc2-evidence-collect.sh

DATE=$(date +%Y%m%d)
EVIDENCE_DIR="evidence/soc2-${DATE}"
mkdir -p ${EVIDENCE_DIR}

# 1. IAM Evidence
echo "=== IAM Evidence ==="
aws iam get-account-password-policy > ${EVIDENCE_DIR}/iam-password-policy.json
aws iam list-virtual-mfa-devices > ${EVIDENCE_DIR}/iam-mfa-devices.json
aws iam list-users --query "Users[?PasswordLastUsed!=null]" > ${EVIDENCE_DIR}/iam-active-users.json

# 2. Logging Evidence
echo "=== Logging Evidence ==="
aws cloudtrail describe-trails > ${EVIDENCE_DIR}/cloudtrail-config.json
aws cloudtrail get-trail-status --name <trail> > ${EVIDENCE_DIR}/cloudtrail-status.json
aws guardduty list-detectors > ${EVIDENCE_DIR}/guardduty-status.json

# 3. Encryption Evidence
echo "=== Encryption Evidence ==="
aws kms list-keys > ${EVIDENCE_DIR}/kms-keys.json
aws kms list-key-rotations > ${EVIDENCE_DIR}/kms-rotation.json

# 4. Network Evidence
echo "=== Network Evidence ==="
aws ec2 describe-security-groups --query "SecurityGroups[?IpPermissions[?IpRanges[?CidrIp=='0.0.0.0/0']]]" > ${EVIDENCE_DIR}/sg-public.json

# 5. Backup Evidence
echo "=== Backup Evidence ==="
aws backup list-backup-plans > ${EVIDENCE_DIR}/backup-plans.json
aws backup list-recovery-points-by-backup-vault --backup-vault-name <vault> > ${EVIDENCE_DIR}/recovery-points.json

# 6. User Access Review
echo "=== User Access Review ==="
aws iam list-users --query "Users[*].UserName" > ${EVIDENCE_DIR}/user-list.json
for user in $(jq -r '.[]' ${EVIDENCE_DIR}/user-list.json); do
  aws iam list-attached-user-policies --user-name $user > ${EVIDENCE_DIR}/user-policy-${user}.json
  aws iam list-groups-for-user --user-name $user > ${EVIDENCE_DIR}/user-groups-${user}.json
done

echo "Evidence collected in ${EVIDENCE_DIR}"
```

---

## 3. PCI-DSS v4 dans le Cloud

### 3.1 Périmètre CDE (Cardholder Data Environment)

```yaml
PCI-DSS Cloud Requirements:
  Requirement 1: Firewall configuration
    - AWS: Security Groups, NACL, WAF, Network Firewall
    - GCP: VPC Firewall Rules, Cloud Armor
    - Azure: NSG, Azure Firewall, WAF

  Requirement 2: Default passwords/configs
    - CIS benchmarks, hardening baselines
    - AWS Config rules, GCP Org Policies, Azure Policy

  Requirement 3: Stored CHD protection
    - Encryption at rest: KMS, CMEK, CMK
    - Tokenization: AWS Tokenization, Azure Tokenization
    - Truncation: Database masking

  Requirement 4: CHD in transit
    - TLS 1.2+ only
    - Certificate management: ACM, CAS, Key Vault
    - mTLS for service-to-service

  Requirement 7: Access to CHD
    - Least privilege IAM
    - MFA for all CDE access
    - Just-in-time (PIM)
    - Access reviews quarterly

  Requirement 10: Logging
    - CloudTrail / Audit Logs / Azure Activity
    - SIEM (Sentinel, Splunk)
    - Log retention (1 year min)

  Requirement 11: Vulnerability scanning
    - ASV scanning quarterly (Approved Scanning Vendor)
    - Internal scanning (Inspector, Qualys)
    - Penetration testing annually

  Requirement 12: Policy
    - Cloud security policy
    - Incident response plan
    - Risk assessment
```

### 3.2 Segmentation PCI dans le Cloud

```bash
# AWS — Isoler le CDE avec VPC
# VPC dédié pour les données carte
aws ec2 create-vpc --cidr-block 10.1.0.0/16 --tag-specifications 'ResourceType=vpc,Tags=[{Key=Environment,Value=PCI-CDE}]'

# Aucun accès internet direct
aws ec2 create-nat-gateway --subnet-id <subnet-private> --allocation-id <eip>
aws ec2 create-route --route-table-id rtb-private --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-xxx

# VPC endpoints pour éviter l'internet
aws ec2 create-vpc-endpoint --vpc-id vpc-pci --service-name com.amazonaws.region.s3
aws ec2 create-vpc-endpoint --vpc-id vpc-pci --service-name com.amazonaws.region.kms
aws ec2 create-vpc-endpoint --vpc-id vpc-pci --service-name com.amazonaws.region.logs

# CloudTrail obligatoire pour le CDE
aws cloudtrail create-trail --name pci-trail --s3-bucket-name pci-logs --is-multi-region-trail --enable-log-file-validation
aws cloudtrail start-logging --name pci-trail

# GuardDuty obligatoire
aws guardduty create-detector --enable

# AWS Config avec PCI rules
aws configservice put-config-rule --config-rule file://pci-requirements.json
```

### 3.3 PCI ASV Scanning

```bash
# ASV (Approved Scanning Vendor) — externe
# Utiliser un ASV approuvé par le PCI Council
# AWS Marketplace : Qualys, Tenable, Trustwave

# Scanning interne avec AWS Inspector
aws inspector2 enable --resource-types EC2
aws inspector2 list-findings \
  --filter-criteria '{"severity": [{"comparison": "EQUALS", "value": "CRITICAL"}]}' \
  --query 'findings[].{Title:title, CVEId:cveId, Severity:severity}'
```

---

## 4. HIPAA dans le Cloud

### 4.1 BAA (Business Associate Agreement)

```bash
# AWS — BAA signé automatiquement via AWS Artifact
aws artifact download-document --document-id <hipaa-baa-id>

# GCP — BAA dans Cloud Console
# IAM → Assured Workloads → HIPAA workload

# Azure — BAA dans Service Trust Portal
# https://servicetrust.microsoft.com/
```

### 4.2 Contrôles HIPAA Techniques

```yaml
HIPAA Security Rule (45 CFR 164):
  Administrative Safeguards:
    - Security Management Process (164.308(a)(1))
    - Assigned Security Responsibility (164.308(a)(2))
    - Workforce Security (164.308(a)(3))
    - Information Access Management (164.308(a)(4))
    - Security Awareness/Training (164.308(a)(5))
    - Security Incident Procedures (164.308(a)(6))
    - Contingency Plan (164.308(a)(7))
    - Evaluation (164.308(a)(8))
    - BA agreements (164.308(b)(1))

  Physical Safeguards:
    - Facility Access Controls (164.310(a)(1))
    - Workstation Use/Security (164.310(b)/(c))
    - Device/Media Controls (164.310(d)(1))

  Technical Safeguards:
    - Access Control (164.312(a)(1)) → IAM, MFA, RBAC
    - Audit Controls (164.312(b)) → CloudTrail, Audit Logs
    - Integrity Controls (164.312(c)(1)) → KMS, object integrity
    - Person/Auth Authentication (164.312(d)) → MFA, SSO
    - Transmission Security (164.312(e)(1)) → TLS 1.2+

  ePHI Controls:
    - Encryption at rest (164.312(a)(2)(iv)) → KMS/CMK
    - Encryption in transit (164.312(e)(1)) → TLS
    - Automatic logoff (164.312(a)(3)) → Session policies
    - Unique user IDs (164.312(a)(1)) → IAM identities
    - Emergency access (164.312(a)(1)(ii)) → Break-glass process
```

### 4.3 HIPAA Compliant Architecture

```bash
# Architecture HIPAA sur AWS
# 1. VPC privé, pas de IP publique sur les instances ePHI
# 2. Chiffrement KMS avec CMK (Customer Master Key)
# 3. CloudTrail + GuardDuty + Config
# 4. MFA obligatoire
# 5. Rotation des clés automatique
# 6. Backup chiffré avec AWS Backup
# 7. VPC Flow Logs pour le trafic
# 8. AWS WAF pour les applications web ePHI

# Vérification de conformité HIPAA
prowler aws -g hipaa -M html
```

---

## 5. GDPR dans le Cloud

### 5.1 Data Protection Impact Assessment (DPIA)

```yaml
Éléments requis GDPR:
  DPA (Data Processing Agreement):
    - Signé avec le provider cloud (AWS/GCP/Azure)
    - Standard Contractual Clauses (SCC)
    - Data Processor obligations

  Data Classification:
    - Personal Data (nom, email, téléphone)
    - Special Categories (santé, biométrie, politique)
    - Pseudonymization vs Anonymization

  Data Residency:
    - AWS: Region selection (eu-west-1, eu-central-1)
    - GCP: Belgium, Frankfurt, London, Zurich
    - Azure: France, Germany, Switzerland, UK

  Data Retention:
    - AWS Object Lock (WORM)
    - GCP Bucket Lock
    - Azure Immutable Blob Storage

  Right to Erasure:
    - AWS: S3 lifecycle policies
    - GCP: Object lifecycle management
    - Azure: Blob lifecycle management
```

### 5.2 GDPR Technical Controls

```bash
# 1. Data Residency — Restreindre les régions
# AWS SCP
aws organizations create-policy --content file://scp-regions.json --name "DenyNonEU-Regions" --type SERVICE_CONTROL_POLICY

# 2. Encryption of Personal Data
aws kms create-key --description "GDPR Key" --policy file://gdpr-key-policy.json
aws kms enable-key-rotation --key-id <key-id>

# 3. Access Logging
aws cloudtrail create-trail --name gdpr-trail --is-multi-region-trail --enable-log-file-validation
aws cloudtrail start-logging --name gdpr-trail

# 4. Data Deletion
# S3 lifecycle policy
aws s3api put-bucket-lifecycle-configuration --bucket <bucket> --lifecycle-configuration file://lifecycle.json

# 5. Data Portability
# Export via AWS Glue + Athena
```

### 5.3 Data Subject Access Request (DSAR)

```bash
# Script de réponse DSAR automatisé
cat > dsar-response.sh << 'EOF'
#!/bin/bash
# dsar-response.sh — Répondre à une demande d'accès

USER_EMAIL=$1
DATE=$(date +%Y%m%d)
OUTPUT_DIR="dsar/${USER_EMAIL}/${DATE}"
mkdir -p ${OUTPUT_DIR}

echo "=== DSAR Response for ${USER_EMAIL} ==="

# 1. CloudTrail — toutes les actions de l'utilisateur
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=Username,AttributeValue=${USER_EMAIL} \
  --start-time $(date -d '30 days ago' +%s) \
  --output json > ${OUTPUT_DIR}/cloudtrail-actions.json

# 2. IAM — user details
aws iam list-users --query "Users[?UserName=='${USER_EMAIL}']" > ${OUTPUT_DIR}/iam-user.json

# 3. S3 — objects access
aws s3api list-objects --bucket <bucket> --prefix users/${USER_EMAIL}/ > ${OUTPUT_DIR}/s3-objects.json

# 4. DynamoDB — items
# aws dynamodb query --table-name users --key-condition-expression "email=:e" \
#   --expression-attribute-values '{":e":{"S":"${USER_EMAIL}"}}' > ${OUTPUT_DIR}/dynamodb-items.json

echo "DSAR data collected in ${OUTPUT_DIR}"
echo "Total size: $(du -sh ${OUTPUT_DIR} | cut -f1)"
EOF
```

---

## 6. AWS Organizations — Governance Multi-Compte

### 6.1 SCP de Sécurité

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootAccessKeys",
      "Effect": "Deny",
      "Action": ["iam:CreateAccessKey", "iam:UpdateAccessKey", "iam:DeleteAccessKey"],
      "Resource": ["arn:aws:iam::*:root"]
    },
    {
      "Sid": "DenyLeavingOrg",
      "Effect": "Deny",
      "Action": [
        "organizations:LeaveOrganization",
        "organizations:DeleteOrganization"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyUnapprovedRegions",
      "Effect": "Deny",
      "Action": ["ec2:*", "rds:*", "lambda:*", "s3:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["eu-west-1", "eu-west-3", "eu-central-1"]
        }
      }
    },
    {
      "Sid": "DenyPublicS3Access",
      "Effect": "Deny",
      "Action": [
        "s3:PutBucketAcl",
        "s3:PutBucketPolicy",
        "s3:PutObjectAcl"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": ["public-read", "public-read-write", "authenticated-read"]
        }
      }
    },
    {
      "Sid": "RequireEncryption",
      "Effect": "Deny",
      "Action": ["s3:PutObject"],
      "Resource": "*",
      "Condition": {
        "Null": {
          "s3:x-amz-server-side-encryption": "true"
        }
      }
    },
    {
      "Sid": "DenyUnapprovedInstanceTypes",
      "Effect": "Deny",
      "Action": ["ec2:RunInstances"],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringNotEquals": {
          "ec2:InstanceType": ["t3.*", "m5.*", "c5.*", "r5.*"]
        }
      }
    },
    {
      "Sid": "RequireVPC",
      "Effect": "Deny",
      "Action": ["ec2:RunInstances"],
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "Null": {
          "ec2:Vpc": "true"
        }
      }
    }
  ]
}
```

### 6.2 Structure Organisationnelle Recommandée

```
root/
├── Security OU
│   ├── Security Audit Account (CloudTrail, GuardDuty)
│   └── Log Archive Account (S3 logs, Config)
├── Infrastructure OU
│   ├── Network Account (Transit Gateway, Firewall)
│   └── Shared Services (AD, DNS, Monitoring)
├── Workloads OU
│   ├── Production OU
│   │   ├── Prod Account 1
│   │   ├── Prod Account 2
│   │   └── ...
│   ├── Staging OU
│   │   ├── Staging Account 1
│   │   └── ...
│   └── Development OU
│       ├── Dev Account 1
│       └── ...
├── Sandbox OU
│   └── (SCP plus permissif)
└── Suspended OU
    └── (SCP deny all)
```

---

## 7. GCP Organization Policies

### 7.1 Policies Essentielles

```bash
# Organisation Policies GCP

# 1. Domain Restricted Sharing
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C0xxxxxxx  # Google Workspace Customer ID
EOF

# 2. Interdire les IP publiques
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/compute.vmExternalIpAccess
listPolicy:
  deny: all
EOF

# 3. Uniform bucket access
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/storage.uniformBucketLevelAccess
booleanPolicy:
  enforced: true
EOF

# 4. Désactiver les SA par défaut
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/iam.automaticIamGrantsForDefaultServiceAccounts
booleanPolicy:
  enforced: true
EOF

# 5. OS Login obligatoire
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/compute.requireOsLogin
booleanPolicy:
  enforced: true
EOF

# 6. Régions autorisées
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/gcp.resourceLocations
listPolicy:
  allowedValues:
  - europe-west1  # Belgium
  - europe-west9  # Paris
  - europe-west10 # Berlin
EOF
```

---

## 8. Azure Policy — Governance

### 8.1 Initiatives de Sécurité

```bash
# Azure Policy — Security initiatives

# 1. Audit Logs obligatoires
az policy assignment create \
  --name "audit-logs" \
  --display-name "Audit Logs Required" \
  --policy "AuditDiagnosticSetting" \
  --params '{"effect": "AuditIfNotExists"}' \
  --scope /subscriptions/<SUB>

# 2. Network Security
az policy assignment create \
  --name "deny-ssh-from-internet" \
  --display-name "Deny SSH from Internet" \
  --policy "StorageAccountPublicAccessShouldBeDisabled" \
  --params '{"effect": "Deny"}'

# 3. Encryption
az policy assignment create \
  --name "require-encryption" \
  --display-name "Require Encryption" \
  --policy "AuditUnusedResourcesCostOptimization" \
  --params '{"effect": "Audit"}'

# 4. Management Groups structure
# Root MG
# ├── Platform MG
# │   ├── Identity MG (Azure AD, PIM)
# │   └── Management MG (Log Analytics, Sentinel)
# ├── Landing Zones MG
# │   ├── Corp MG (Corporate workloads)
# │   ├── Online MG (Customer-facing)
# │   └── Sandbox MG
# └── Decommissioned MG
```

---

## 9. Audit Logging & Reporting

### 9.1 Centralisation des Logs

```bash
# Architecture de logs multi-compte
# AWS: CloudTrail Organization Trail → S3 → Athena → QuickSight
# GCP: Audit Logs → BigQuery → Looker
# Azure: Diagnostic Settings → Log Analytics → Sentinel

# AWS — Organization Trail
aws cloudtrail create-trail \
  --name org-trail \
  --s3-bucket-name org-logs-<account> \
  --is-organization-trail \
  --enable-log-file-validation \
  --is-multi-region-trail

# GCP — Log Sink vers BigQuery
gcloud logging sinks create org-sink \
  bigquery.googleapis.com/projects/<PROJECT>/datasets/audit \
  --organization <ORG_ID> \
  --include-children \
  --log-filter="severity>=WARNING"

# Azure — Diagnostic Settings
az policy assignment create \
  --name "deploy-diag-settings" \
  --display-name "Deploy Diagnostic Settings" \
  --policy "DeployDiagnosticSettings"
```

### 9.2 Compliance Dashboard

```bash
# Script de reporting de conformité
#!/bin/bash
# compliance-report.sh

echo "=== Compliance Report $(date +%Y-%m-%d) ==="

# AWS
echo ""
echo "--- AWS Compliance ---"
echo "CIS Score: $(prowler aws -g cis_1.5 -M json | jq '.summary.pass_percentage')"
echo "PCI Findings: $(prowler aws -g pci_3.2.1 -M json | jq '.summary.fail')"
echo "HIPAA Controls: $(prowler aws -g hipaa -M json | jq '.summary.pass')"

# GCP
echo ""
echo "--- GCP Compliance ---"
echo "CIS Score: $(prowler gcp -p <project> -g cis_1.2 -M json | jq '.summary.pass_percentage')"

# Azure
echo ""
echo "--- Azure Compliance ---"
echo "Secure Score: $(az security secure-score list --query [].currentScore --output tsv)"
echo "Defender Score: $(az security pricing list --query '[].{Name:name, Tier:tier}' --output table)"
```

---

## 10. Outils de Conformité Cloud

| Outil | Frameworks | Description |
|-------|-----------|-------------|
| **Prowler** | CIS, PCI, HIPAA, NIST | Cloud compliance scanning |
| **Checkov** | CIS, PCI, HIPAA, SOC2 | IaC compliance scanning |
| **ScoutSuite** | CIS, custom | Cloud config audit |
| **CloudSploit** | CIS, custom | Cloud security scanning |
| **Terraform Sentinel** | Custom | Policy as code |
| **OPA (Rego)** | Custom | Policy engine |
| **Kyverno** | K8s security | K8s policy engine |
| **OpenSCAP** | SCAP, CIS | System compliance |
| **InSpec** | SOC2, PCI, CIS | Compliance as code |
| **Lynis** | CIS, custom | System hardening audit |

## Pitfalls

- **Ne PAS** confondre certification du provider et votre propre conformité — le modèle de responsabilité partagée s'applique
- **Ne PAS** importer des données sensibles sans vérifier le BAA/DPA d'abord
- **TOUJOURS** documenter les exceptions de conformité avec justification
- **TOUJOURS** automatiser la collecte d'évidences (ne pas attendre l'audit)
- Les SCP trop restrictives peuvent bloquer des pipelines CI/CD — tester dans une OU sandbox
- Chaque framework a des exigences de logging spécifiques — vérifier les rétentions
- Les audits cloud nécessitent des accès read-only pour les auditeurs — configurer correctement
- Les données de logs contiennent des PII — activer la redaction des champs sensibles

## Ressources

- **AWS Compliance**: https://aws.amazon.com/compliance/
- **GCP Compliance**: https://cloud.google.com/security/compliance
- **Azure Compliance**: https://docs.microsoft.com/en-us/azure/compliance/
- **PCI Security Standards**: https://www.pcisecuritystandards.org/
- **HIPAA Journal**: https://www.hipaajournal.com/
- **GDPR.eu**: https://gdpr.eu/
- **CIS Benchmarks**: https://www.cisecurity.org/benchmark/cloud
- **SOC 2 Guide**: https://www.aicpa.org/soc2
- **NIST CSF**: https://www.nist.gov/cyberframework