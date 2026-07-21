---
name: cloud-cspm
description: Guide complet du Cloud Security Posture Management (CSPM) — Prowler, ScoutSuite, Checkov, CloudSploit, Security Hub, et automatisation de la posture multi-cloud AWS/GCP/Azure
domain: [cybersecurite, cloud, cspm]
tags: [cspm, prowler, scoutsuite, cloudsploit, security-posture, checkov, terrascan, drift-detection, compliance-as-code]
priority: haute
---

# 📊 Cloud Security Posture Management (CSPM) — Guide Multi-Cloud

Guide complet des outils, frameworks et bonnes pratiques pour la gestion de la posture de sécurité cloud.

---

## 1. Qu'est-ce que le CSPM ?

Le Cloud Security Posture Management (CSPM) est une catégorie de solutions de sécurité qui surveille en continu les configurations cloud pour détecter :
- **Les mauvaises configurations** (buckets publics, SGs trop ouverts)
- **Les violations de conformité** (CIS, NIST, SOC2, PCI-DSS)
- **Les dérives de configuration** (drift detection)
- **Les chemins d'attaque** (privesc IAM, exposition réseau)
- **Les anomalies** (ressources orphelines, changements inattendus)

### 1.1 CSPM vs Autres Solutions

| Solution | Focus | Exemples |
|----------|-------|----------|
| **CSPM** | Posture & configuration | Prowler, ScoutSuite, Wiz |
| **CWPP** | Runtime workload protection | Defender for Servers, Prisma Cloud |
| **CIEM** | Cloud Infrastructure Entitlement Mgmt | Ermetic, SailPoint |
| **CASB** | Application SaaS security | Defender for Cloud Apps, Netskope |
| **SIEM** | Logs & events centralisés | Sentinel, Splunk |

---

## 2. Prowler — L'Outil CSPM Multi-Cloud de Référence

### 2.1 Installation et Configuration

```bash
# Installation
pip install prowler
prowler --help

# Configuration multi-compte AWS
cat > ~/.prowler/config.yaml << 'EOF'
aws:
  accounts:
    - "123456789012"
    - "234567890123"
  regions:
    - "eu-west-1"
    - "us-east-1"
  organizations_role: "arn:aws:iam::*:role/ProwlerRole"
  
gcp:
  projects:
    - "prod-project"
    - "staging-project"
  organization_id: "123456789"

azure:
  subscriptions:
    - "sub-id-1"
    - "sub-id-2"
  tenant_id: "tenant-id"
EOF
```

### 2.2 Commandes Prowler Essentielles

```bash
# AWS - Audit complet
prowler aws -M csv,json,json-asff,html

# AWS - Groupe spécifique (CIS)
prowler aws -g cis_1.5 -M html

# AWS - Check spécifique
prowler aws -c s3_bucket_public_access -M json

# AWS - Rapport d'écart (baseline comparison)
prowler aws -o report-2026-07-22
prowler aws -o report-2026-07-29 --diff report-2026-07-22

# GCP - Audit
prowler gcp -p prod-project -M csv,html

# Azure - Audit
prowler azure -g cis_2.0 -M csv,html
```

### 2.3 Checks Prowler par Catégorie

| Catégorie | AWS | GCP | Azure |
|-----------|-----|-----|-------|
| **Identity & Access** | 25 checks | 18 checks | 22 checks |
| **Storage** | 15 checks | 12 checks | 10 checks |
| **Network** | 20 checks | 15 checks | 18 checks |
| **Compute** | 12 checks | 10 checks | 14 checks |
| **Logging & Monitoring** | 18 checks | 14 checks | 16 checks |
| **Encryption** | 10 checks | 8 checks | 12 checks |
| **Kubernetes** | 8 checks | 10 checks | 6 checks |
| **Serverless** | 6 checks | 4 checks | 4 checks |

### 2.4 Intégration Continue

```bash
# GitHub Actions — Prowler CI
cat > .github/workflows/prowler.yml << 'EOF'
name: CSPM Scan
on:
  schedule:
    - cron: '0 6 * * 1'  # Chaque lundi
  workflow_dispatch:

jobs:
  prowler-scan:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install prowler
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT }}:role/ProwlerRole
          aws-region: eu-west-1
      - run: prowler aws -M json-asff,html -o reports/
      - name: Upload Report
        uses: actions/upload-artifact@v4
        with:
          name: prowler-report
          path: reports/
EOF
```

---

## 3. ScoutSuite — Audit de Configuration Multi-Cloud

### 3.1 Utilisation

```bash
# Installation
pip install scoutsuite

# AWS
scout aws --profile default --report-dir ./scout-reports

# GCP (avec clé SA)
scout gcp --project-id prod-project --service-account-key key.json

# Azure
scout azure --cli

# Résultats : rapport HTML interactif dans scout-reports/
```

### 3.2 Règles Personnalisées ScoutSuite

```python
# rules/custom-rules.py
# Exemple : Détecter les Security Groups avec port 22 ouvert
from ScoutSuite.core.conditions import Condition

def custom_rules():
    return [
        {
            "name": "custom-sg-ssh-public",
            "description": "Security Group with SSH access from 0.0.0.0/0",
            "path": "ec2.regions.id.vpcs.id.security_groups.id.rules.ingress.protocols[22].ports[22]",
            "conditions": [
                Condition("cidr", "==", "0.0.0.0/0")
            ]
        }
    ]
```

### 3.3 ScoutSuite vs Prowler

| Critère | Prowler | ScoutSuite |
|---------|---------|------------|
| **Maintenance** | Active (2026) | Archivé (2022) |
| **Checks** | 300+ AWS, 150+ GCP, 200+ Azure | 800+ AWS, 600+ GCP |
| **Format sortie** | CSV, JSON, HTML, ASFF | HTML interactif |
| **CI/CD** | GitHub Actions, GitLab CI | Manuel |
| **Multi-compte** | Organizations ✓ | Manuel |
| **Remediation** | Auto-remediation SSM | Non |
| **Recommandation** | ✅ Moderne | ❌ Archivé mais complet |

---

## 4. Checkov — IaC Security Scanning

### 4.1 Installation et Utilisation

```bash
pip install checkov

# Scan Terraform
checkov -d ./terraform/ -o cli,sarif,cyclonedx

# Scan CloudFormation
checkov -f ./cfn/template.yaml -o cli

# Scan Kubernetes
checkov -f ./k8s/deployment.yaml -o cli

# Scan ARM (Azure)
checkov -f ./arm/template.json -o cli

# Scan Dockerfile
checkov -d ./docker/ -o cli

# Framework spécifique
checkov -d ./terraform/ --framework terraform -o cli

# Sévérité minimale
checkov -d ./terraform/ --check-severity CRITICAL,HIGH

# Soft fail (pas d'exit code 1)
checkov -d ./terraform/ --soft-fail
```

### 4.2 Politiques Personnalisées Checkov

```python
# .checkov/custom_policies/CustomPolicy.py
from checkov.common.models.enums import CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class S3PublicAccessBlock(BaseResourceCheck):
    def __init__(self):
        name = "S3 Bucket must have public access block"
        id = "CKV_CUSTOM_001"
        supported_resources = ['aws_s3_bucket']
        super().__init__(name=name, id=id, supported_resources=supported_resources)
    
    def scan_resource_conf(self, conf):
        if 'block_public_acls' in conf and conf['block_public_acls'] == [True]:
            return CheckResult.PASSED
        return CheckResult.FAILED

check = S3PublicAccessBlock()
```

### 4.3 Intégration CI/CD

```yaml
# .github/workflows/iac-scan.yml
name: IaC Security Scan
on: [pull_request]

jobs:
  checkov-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          soft_fail: false
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
```

---

## 5. CloudSploit — Scanning de Sécurité

```bash
# Installation
npm install -g cloudsploit

# AWS
cloudsploit aws --config cloudsploit-config.js

# Azure
cloudsploit azure --config azure-config.js

# GCP
cloudsploit gcp --config gcp-config.js

# Configuration
cat > cloudsploit-config.js << 'EOF'
module.exports = {
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    sessionToken: process.env.AWS_SESSION_TOKEN
  },
  settings: {
    api_calls: true,
    max_retries: 3,
    min_interval: 300
  }
};
EOF
```

---

## 6. AWS Security Hub comme CSPM Central

### 6.1 Aggrégation Multi-Compte Multi-Région

```bash
# Architecture de Centralisation CSPM
# Security Hub + Prowler + Config + GuardDuty

# 1. Activer Security Hub dans le compte admin
aws securityhub enable-organization-admin-account \
  --admin-account-id <ADMIN_ACCOUNT>

# 2. Activer dans tous les comptes (automatiquement via Organizations)
# Les comptes membres sont automatiquement invités

# 3. Activer les standards
aws securityhub batch-enable-standards \
  --standards-subscription-requests '[
    {"StandardsArn": "arn:aws:securityhub:eu-west-1::standards/aws-foundational-security-best-practices/v/1.0.0"},
    {"StandardsArn": "arn:aws:securityhub:eu-west-1::standards/cis-aws-foundations-benchmark/v/1.4.0"},
    {"StandardsArn": "arn:aws:securityhub:eu-west-1::standards/pci-dss/v/3.2.1"}
  ]'

# 4. Importer les findings Prowler
prowler aws -M json-asff -o prowler-findings/

# 5. Créer des Insights personnalisés
aws securityhub create-insight \
  --name "S3 Public Buckets" \
  --filters '{
    "ResourceType": [{"Comparison": "EQUALS", "Value": "AwsS3Bucket"}],
    "ComplianceStatus": [{"Comparison": "EQUALS", "Value": "FAILED"}],
    "WorkflowStatus": [{"Comparison": "EQUALS", "Value": "NEW"}]
  }' \
  --group-by-attribute "ResourceId"
```

### 6.2 Automatisation de Remediation

```bash
 # Security Hub → EventBridge → SSM Automation
# 1. Créer une Custom Action
aws securityhub create-action-target \
  --name "Remediate S3 Public" \
  --description "Auto-remediate S3 public access" \
  --id "remediate-s3"

# 2. EventBridge rule
cat > securityhub-remediate.json << 'EOF'
{
  "eventPattern": {
    "source": ["aws.securityhub"],
    "detail-type": ["Security Hub Findings - Custom Action"],
    "detail": {
      "actionName": ["Remediate S3 Public"]
    }
  },
  "targets": [{
    "Arn": "arn:aws:ssm:eu-west-1:...:automation-definition/AWS-DisableS3BucketPublicReadWrite",
    "Id": "remediate-s3",
    "RoleArn": "arn:aws:iam::...:role/securityhub-automation"
  }]
}
EOF
```

---

## 7. GCP Security Command Center comme CSPM

### 7.1 Configuration CSPM GCP

```bash
# SCC Premium = CSPM GCP
gcloud scc settings enable --organization <ORG_ID> \
  --service SECURITY_HEALTH_ANALYTICS_SERVICE

# Exporter les findings vers BigQuery
gcloud scc export findings --organization <ORG_ID> \
  --bigquery-table <PROJECT>:scc_dataset.findings

# Analyser la posture avec BigQuery
cat > query-scc.sql << 'SQL'
SELECT
  category,
  COUNT(*) as count,
  severity
FROM `<PROJECT>.scc_dataset.findings`
WHERE state = 'ACTIVE'
  AND event_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
GROUP BY category, severity
ORDER BY count DESC
SQL
```

### 7.2 Détection de Drift GCP

```bash
# Forseti Security (CSPM open source GCP)
# git clone https://github.com/forseti-security/forseti-security
# Scanner les violations de politique
# Détecter les changements de configuration

# Asset Inventory pour le drift
gcloud asset search-all-resources \
  --scope organizations/<ORG_ID> \
  --asset-types compute.googleapis.com/Firewall,storage.googleapis.com/Bucket \
  --query "state=RUNNING"
```

---

## 8. Azure Defender for Cloud comme CSPM

### 8.1 Secure Score et Recommandations

```bash
# Secure Score = Score de posture Azure
az security secure-score list --output table

# Score par contrôle
az security secure-score-controls list --output table

# Recommandations non résolues
az security assessment list \
  --filter "properties.status.code eq 'Unhealthy'" \
  --query "[].{Name:properties.displayName, Severity:properties.severity, Resource:properties.resourceDetails.Id}"

# Exporter les recommandations
az security assessment list --output json > defender-recommendations.json
```

### 8.2 Azure Policy comme CSPM Engine

```bash
# Azure Policy est le moteur CSPM natif d'Azure
# Mode audit + deny + remediation

# Créer une initiative de sécurité (plusieurs policies)
az policy set-definition create \
  --name "cspm-baseline" \
  --display-name "CSPM Baseline" \
  --definitions @cspm-policies.json

# Assigner avec effet Deny ou Audit
az policy assignment create \
  --name "cspm-baseline" \
  --policy-set-definition "cspm-baseline" \
  --scope /subscriptions/<SUB> \
  --params '{"effect": {"value": "Deny"}}'
```

---

## 9. Automatisation de la Posture

### 9.1 Pipeline de Posture Continue

```yaml
# Pipeline de posture automatisé
# 1. Scan IaC (Checkov) — Pre-commit
# 2. Scan Cloud (Prowler) — Daily
# 3. Remediation automatique — On finding
# 4. Rapport de posture — Weekly
# 5. Évolution de la posture — Monthly

cron:
  - "0 6 * * *"    # Scan quotidien
  - "0 0 * * 1"    # Rapport hebdo
  - "0 0 1 * *"    # Rapport mensuel

# Workflow de remediation
# Finding critique → EventBridge → Lambda/SSM
# → Remediation → Confirmation → Close finding
```

### 9.2 Script de Posture Unifié

```bash
#!/bin/bash
# cspm-unified-scan.sh — Scan multi-cloud

DATE=$(date +%Y%m%d)
REPORT_DIR="reports/cspm-${DATE}"

mkdir -p ${REPORT_DIR}

echo "=== CSPM Scan ${DATE} ==="

# 1. AWS
echo "[AWS] Prowler..."
prowler aws -M csv,json,html -o ${REPORT_DIR}/aws/

# 2. GCP
echo "[GCP] Prowler..."
prowler gcp -p prod-project -M csv,html -o ${REPORT_DIR}/gcp/

# 3. Azure
echo "[Azure] Prowler..."
prowler azure -M csv,html -o ${REPORT_DIR}/azure/

# 4. IaC
echo "[IaC] Checkov..."
checkov -d ../terraform/ -o cli --output-file-path ${REPORT_DIR}/checkov/

# 5. Résumé
echo "=== Résumé de la Posture ==="
python3 -c "
import json
import glob

aws = json.load(open(glob.glob('${REPORT_DIR}/aws/*.json')[0]))
gcp = json.load(open(glob.glob('${REPORT_DIR}/gcp/*.json')[0]))
azure = json.load(open(glob.glob('${REPORT_DIR}/azure/*.json')[0]))

print(f'AWS: {aws[\"summary\"][\"pass\"]} pass, {aws[\"summary\"][\"fail\"]} fail')
print(f'GCP: {gcp[\"summary\"][\"pass\"]} pass, {gcp[\"summary\"][\"fail\"]} fail')
print(f'Azure: {azure[\"summary\"][\"pass\"]} pass, {azure[\"summary\"][\"fail\"]} fail')
"
```

---

## 10. Metriques de Posture Clés

| Métrique | Description | Cible |
|----------|-------------|-------|
| **Secure Score** | Score global de posture | > 85% |
| **CIS Compliance** | Conformité aux benchmarks CIS | > 90% |
| **Critical Findings** | Nombre de findings critiques | < 5 |
| **Mean Time to Remediate** | Temps moyen de correction | < 24h |
| **Drift Events** | Changements de configuration non autorisés | 0 |
| **Public Resources** | Ressources avec accès public | 0 |
| **Unused Resources** | Ressources orphelines/non utilisées | < 10 |
| **MFA Coverage** | Utilisateurs avec MFA | 100% |
| **Encryption Coverage** | Ressources chiffrées | 100% |
| **IaC Coverage** | Infrastructure gérée par IaC | > 90% |

## Pitfalls

- **Ne PAS** se fier à un seul outil CSPM — Prowler + Checkov + Security Hub = meilleure couverture
- **Ne PAS** ignorer les findings LOW/MEDIUM — ils s'accumulent et deviennent critiques
- **TOUJOURS** configurer des alertes pour les **changements** de posture, pas seulement les scans
- **TOUJOURS** comparer les scans (diff report) pour détecter les dérives
- Les CSPM outils peuvent générer des faux positifs — maintenir une baseline
- Le coût de Security Hub/Defender for Cloud dépend du nombre de ressources — budgétiser
- Les scans multi-comptes nécessitent IAM roles/Service Accounts — configurer correctement
- Prowler est plus maintenu que ScoutSuite — privilégier Prowler

## Ressources

- **Prowler**: https://github.com/prowler-cloud/prowler
- **ScoutSuite**: https://github.com/nccgroup/ScoutSuite
- **Checkov**: https://github.com/bridgecrewio/checkov
- **CloudSploit**: https://github.com/aquasecurity/cloudsploit
- **Forseti Security**: https://github.com/forseti-security/forseti-security
- **CIS Benchmarks**: https://www.cisecurity.org/benchmark/cloud
- **CIS Controls**: https://www.cisecurity.org/controls/
- **Cloud Security Alliance**: https://cloudsecurityalliance.org/