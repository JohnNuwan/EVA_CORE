---
name: aws-security-services
description: Guide complet des services de sécurité AWS — GuardDuty, Inspector, Macie, Detective, Firewall Manager, Network Firewall, Security Hub, Config, Artifact, et architecture défensive AWS
domain: [cybersecurite, cloud, aws]
tags: [aws, guardduty, inspector, macie, detective, security-hub, network-firewall, firewall-manager, aws-config, artifact]
priority: haute
---

# 🛡️ AWS Security Services — Guide Défensif Complet

Guide exhaustif des services de sécurité natifs AWS, leur configuration, intégration et bonnes pratiques défensives.

---

## 1. AWS GuardDuty — Détection de Menaces

### 1.1 Architecture et Principes

GuardDuty est un service de détection de menaces alimenté par ML qui analyse :
- **CloudTrail Events** (management + data events S3)
- **VPC Flow Logs** (trafic réseau)
- **DNS Logs** (requêtes DNS)
- **EKS Audit Logs** (Kubernetes)
- **RDS Login Events** (tentatives de connexion)
- **S3 Data Events** (accès aux objets)

```bash
# Activation multi-compte avec Delegated Admin
aws guardduty enable-organization-admin-account --admin-account-id <id>
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES

# Configuration des listes de confiance (threat lists)
aws guardduty create-ip-set --detector-id <id> --name my-whitelist \
  --format TXT --location s3://bucket/whitelist.txt --activate

# Création d'une liste de domaines de confiance
aws guardduty create-threat-intel-set --detector-id <id> \
  --name tor-exit-nodes --format TXT \
  --location s3://bucket/tor-nodes.txt --activate
```

### 1.2 Types de Findings Critiques par Catégorie

| Catégorie | Finding Critique | Sévérité |
|-----------|------------------|----------|
| **Backdoor** | `Backdoor:EC2/C&CActivity.B` | High |
| **Crypto** | `CryptoCurrency:EC2/BitcoinTool.B` | High |
| **IAM** | `UnauthorizedAccess:IAMUser/ConsoleLoginSuccess` | Medium |
| **IAM** | `Policy:IAMUser/RootCredentialUsage` | High |
| **EC2** | `UnauthorizedAccess:EC2/SSHBruteForce` | Medium |
| **S3** | `Discovery:S3/MaliciousIPCaller` | Medium |
| **Privesc** | `PrivilegeEscalation:IAMUser/AnomalousBehavior` | High |
| **Stealth** | `Stealth:IAMUser/CloudTrailLoggingDisabled` | Medium |
| **K8s** | `Policy:Kubernetes/AnonymousAccessGranted` | High |
| **RDS** | `UnauthorizedAccess:RDS/LoginEvent` | Medium |

```bash
# Suppression automatique des findings basse sévérité
aws guardduty create-sampling-filter --detector-id <id> --filter-name auto-suppress \
  --finding-criteria '{"Criterion": {"severity": {"Lt": 4}}}'
```

### 1.3 Intégration avec les Services AWS

```bash
# EventBridge → Lambda → Remediation automatique
# Règle EventBridge pour GuardDuty
cat > guardduty-event-rule.json << 'EOF'
{
  "eventPattern": {
    "source": ["aws.guardduty"],
    "detail-type": ["GuardDuty Finding"],
    "detail": {
      "severity": [7, 8, 9],
      "type": [{"prefix": "CryptoCurrency"}, {"prefix": "Backdoor"}]
    }
  },
  "targets": [{"Arn": "arn:aws:lambda:...:function:auto-remediate", "Id": "remediate"}]
}
EOF
aws events put-rule --name guardduty-critical --event-pattern file://guardduty-event-rule.json

# Lambda de remediation — isolement EC2
cat > remediate.py << 'PYEOF'
import boto3, os

def handler(event, context):
    ec2 = boto3.client('ec2')
    finding = event['detail']
    resource_id = finding['resource']['instanceDetails']['instanceId']
    
    # Appliquer un Security Group d'isolement
    ec2.modify-instance-attribute(
        InstanceId=resource_id,
        Groups=[os.environ['ISOLATION_SG_ID']]
    )
    # Stop si crypto mining
    if 'CryptoCurrency' in finding['type']:
        ec2.stop_instances(InstanceIds=[resource_id])
    
    return {'statusCode': 200, 'body': f'Isolated {resource_id}'}
PYEOF
```

### 1.4 Suppression des Findings (Muting)

```bash
# Muter automatiquement les findings de basse sévérité
aws guardduty update-filter --detector-id <id> --filter-name auto-mute \
  --action ARCHIVE \
  --finding-criteria '{"Criterion": {"severity": {"Lte": 3}}}'
```

---

## 2. AWS Inspector — Analyse de Vulnérabilités

### 2.1 Amazon Inspector Classic vs Inspector V2

| Fonctionnalité | Inspector Classic | Inspector V2 |
|---------------|-------------------|--------------|
| Scan EC2 (Agent) | ✓ | ✓ (SSM Agent) |
| Scan conteneurs | ✗ | ✓ (ECR) |
| Scan Lambda | ✗ | ✓ |
| Network Reachability | ✓ | ✓ |
| Code scan (Lambda) | ✗ | ✓ |
| Pricing | Par instance/heure | Par scan |

```bash
# Activation Inspector V2
aws inspector2 enable --resource-types EC2 ECR LAMBDA

# Activation multi-compte
aws inspector2 enable-delegated-admin-account --delegated-admin-account-id <id>

# Créer un template de scan avec Scheduled Rule
aws inspector2 create-filter --action SUPPRESS \
  --filter-criteria '{"findingStatus": [{"comparison": "EQUALS", "value": "SUPPRESSED"}]}' \
  --name suppress-false-positives
```

### 2.2 Gestion des Findings

```bash
# Lister les findings vulnérabilités critiques
aws inspector2 list-findings --filter-criteria '{
  "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
  "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
}'

# Créer un rapport SBOM
aws inspector2 create-sbom-export --report-format CYCLONEDX_1_5 \
  --s3-destination bucketName=reports,keyPrefix=sbom/
```

### 2.3 Remediation Automatique

```bash
# SSM Automation Document pour patcher
cat > patch-critical.yaml << 'EOF'
schemaVersion: '0.3'
description: Auto-patch critical CVEs
mainSteps:
  - name: PatchWithPatchManager
    action: 'aws:runCommand'
    inputs:
      DocumentName: AWS-RunPatchBaseline
      InstanceIds: ['{{InstanceId}}']
      Parameters:
        Operation: Install
        RebootOption: RebootIfNeeded
EOF
```

---

## 3. Amazon Macie — Protection des Données Sensibles

### 3.1 Architecture Macie

Macie utilise le ML pour découvrir, classifier et protéger les données sensibles dans S3.

```bash
# Activation Macie
aws macie2 enable-macie

# Créer un job de découverte
aws macie2 create-classification-job --name prod-scan \
  --job-type SCHEDULED --schedule-frequency WEEKLY \
  --s3-job-definition '{
    "bucketDefinitions": [{"accountId": "123456789012", "buckets": ["prod-data"]}],
    "scoping": {"includes": {"and": [{"simpleScopeTerm": {"key": "OBJECT_EXTENSION", "values": [".csv", ".json", ".xlsx"]}}]}}
  }' \
  --managed-data-identifier-ids '[
    "AWS_CREDENTIALS", "AWS_MANAGED_CREDENTIALS", "CREDIT_CARD_NUMBER",
    "USA_SOCIAL_SECURITY_NUMBER", "CUSTOM_IDENTIFIER"
  ]'

# Identifiant personnalisé (regex)
aws macie2 create-custom-data-identifier --name api-key \
  --regex 'sk-[a-zA-Z0-9]{20,}' \
  --description "Detection des clés API OpenAI/ChatGPT"
```

### 3.2 Types de Données Détectées par Macie

| Identifiant | Type | Exemple |
|-------------|------|---------|
| AWS Credentials | Credentials | `AKIAIOSFODNN7EXAMPLE` |
| Credit Card | PII | `4111-1111-1111-1111` |
| SSN | PII | `123-45-6789` |
| API Key | Secrets | `sk-proj-xxxxxxxxxx` |
| Private Key | Crypto | `-----BEGIN RSA PRIVATE KEY-----` |
| JSON Web Token | Auth | `eyJhbGciOiJIUzI1NiIs...` |

### 3.3 Alerts et Remediation

```bash
# EventBridge → Macie finding → remediation
cat > macie-auto-block.json << 'EOF'
{
  "eventPattern": {
    "source": ["aws.macie"],
    "detail-type": ["Macie Finding"],
    "detail": {"severity": {"description": ["CRITICAL", "HIGH"]}}
  }
}
EOF

# Suppression automatique des buckets à risque
# Blocage des ACLs publiques sur les buckets sensibles
```

---

## 4. AWS Detective — Investigation Forensique

### 4.1 Mise en Place

```bash
# Créer un graph Detective
aws detective create-graph --graph-name prod-graph

# Inviter des comptes membres (multi-compte)
aws detective create-members --graph-arn <arn> \
  --accounts AccountId=123456789012,EmailAddress=admin@example.com
```

### 4.2 Utilisation pour l'Investigation

```bash
# Via AWS CLI — obtenir les données d'investigation
# Detective n'a pas de CLI riche — utiliser le SDK boto3
# Exemple Python
cat > detective_investigate.py << 'PYEOF'
import boto3

detective = boto3.client('detective')
graph_arn = 'arn:aws:detective:...'

# Obtenir les ressources d'un IP suspect
ip_data = detective.get_indicators(
    GraphArn=graph_arn,
    IndicatorValues=[{'IpAddress': {'IpAddress': '1.2.3.4'}}]
)

# Voir les entités associées
resources = detective.list_resources(
    GraphArn=graph_arn,
    Filters={'ResourceType': 'AwsResource'}
)
PYEOF
```

### 4.3 Integration avec Jupyter Notebooks

```bash
# Detective + Athena pour les logs CloudTrail
# Lancer une investigation interactive
# aws detective query → graph visualization
```

---

## 5. AWS Network Firewall

### 5.1 Architecture

```
Internet → IGW → Public Subnet (Firewall) → Protected Subnets
                          ↓
                AWS Network Firewall
               - Stateful rules (Suricata)
               - Stateless rules
               - Domain filtering
```

### 5.2 Configuration

```bash
# Créer le Firewall
aws network-firewall create-firewall-policy \
  --firewall-policy-name fw-policy \
  --firewall-policy '{
    "StatelessDefaultActions": ["aws:forward_to_snf"],
    "StatelessFragmentDefaultActions": ["aws:forward_to_snf"]
  }'

# Règles stateful (Suricata format)
cat > suricata-rules.txt << 'EOF'
# Bloquer les C2 connus
drop tls $HOME_NET any -> $EXTERNAL_NET 443
  (tls.sni; content:"evil.com"; msg:"C2 Domain Blocked";
  sid:1000001; rev:1;)

# Bloquer les cryptominers DNS
drop dns $HOME_NET any -> any 53
  (dns.query; content:"mining"; msg:"Crypto Mining DNS query";
  sid:1000002; rev:1;)

# Bloquer les protocoles non autorisés
drop tcp $HOME_NET any -> $EXTERNAL_NET 22
  (msg:"SSH Outbound Blocked"; sid:1000003; rev:1;)

# Détection SQLi dans le trafic HTTP
alert http $EXTERNAL_NET any -> $HOME_NET any
  (http.uri; content:"union+select"; nocase;
   msg:"Possible SQL Injection"; sid:1000004; rev:1;)
EOF

# Upload des règles
aws network-firewall create-rule-group \
  --rule-group-name suricata-block \
  --type STATEFUL \
  --capacity 10000 \
  --rules-source file://suricata-rules.txt

# Domain filter rules
aws network-firewall create-rule-group \
  --rule-group-name domain-block \
  --type STATEFUL \
  --rule-group '{
    "RulesSource": {
      "RulesSourceList": {
        "Targets": [".cryptominer.com", ".malware.com"],
        "TargetTypes": ["TLS_SNI", "HTTP_HOST"],
        "GeneratedRulesType": "DENYLIST"
      }
    }
  }'
```

### 5.3 Monitorer le Firewall

```bash
# CloudWatch Metrics
aws cloudwatch list-metrics --namespace AWS/NetworkFirewall \
  --metric-name DroppedPackets --dimensions Name=FirewallName,Value=fw-prod

# Flow Logs vers S3
aws network-firewall describe-firewall --firewall-name fw-prod \
  --query 'FirewallStatus.SyncStates'
```

---

## 6. AWS Firewall Manager

### 6.1 Architecture Multi-Compte

```bash
# Activation du Firewall Manager Admin
aws organizations enable-aws-service-access \
  --service-principal fms.amazonaws.com
aws organizations register-delegated-administrator \
  --account-id <admin-account> --service-principal fms.amazonaws.com

# Créer une Security Policy (WAF)
aws fms put-policy --policy '{
  "PolicyName": "waf-org-policy",
  "SecurityServicePolicyData": {
    "Type": "WAF",
    "ManagedServiceData": "{\"type\":\"WAF\",\"defaultAction\":{\"type\":\"ALLOW\"},\"preProcessRuleGroups\":[{\"managedRuleGroupIdentifier\":{\"vendor\":\"AWS\",\"name\":\"AWSManagedRulesCommonRuleSet\"},\"overrideAction\":{\"type\":\"NONE\"}}]}"
  },
  "ResourceType": "ResourceTypeList",
  "ResourceTags": [{"Key": "Environment", "Value": "Production"}],
  "ExcludeResourceTags": false,
  "RemediationEnabled": true
}'
```

### 6.2 Types de Policies FMS

| Type | Description |
|------|-------------|
| **WAF** | Web ACLs sur CloudFront/ALB/API Gateway |
| **Security Group** | Common SGs + audit |
| **Network Firewall** | Firewall rules |
| **Shield Advanced** | DDoS protection |
| **Network ACL** | NACL common rules |
| **DNS Firewall** | Route53 Resolver DNS filtering |

---

## 7. AWS Security Hub

### 7.1 Activation Multi-Région Multi-Compte

```bash
# Activation via Organizations
aws securityhub enable-organization-admin-account \
  --admin-account-id <id>

aws securityhub enable-security-hub \
  --enable-standards '[
    "arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0",
    "arn:aws:securityhub:us-east-1::standards/cis-aws-foundations-benchmark/v/1.4.0",
    "arn:aws:securityhub:us-east-1::standards/pci-dss/v/3.2.1"
  ]'

# Ajouter un standard NIST
aws securityhub enable-import-findings-for-product \
  --product-arn "arn:aws:securityhub:us-east-1::product/aws/securityhub"
```

### 7.2 Custom Actions et Automations

```bash
# Custom Action → remediate
aws securityhub create-action-target \
  --name "Remediate S3" \
  --description "Bloquer S3 public" \
  --id "remediate-s3"

# Règles de suppression automatisée
aws securityhub batch-update-findings \
  --finding-identifiers Id=arn:aws:securityhub:... \
  --workflow Status=RESOLVED \
  --note Text="Auto-remediated by SCP",UpdatedBy=automation

# Intégration avec EventBridge → Systems Manager
# Automation document pour remediation
```

### 7.3 Custom Insights

```bash
# Créer un Insight — trouver les ressources sans encryption
aws securityhub create-insight \
  --name "Unencrypted S3 Buckets" \
  --filters '{
    "ResourceType": [{"Comparison": "EQUALS", "Value": "AwsS3Bucket"}],
    "ComplianceStatus": [{"Comparison": "EQUALS", "Value": "FAILED"}]
  }' \
  --group-by-attribute "ResourceId"
```

---

## 8. AWS Config — Gestion de la Conformité

### 8.1 Configuration Multi-Compte

```bash
aws configservice put-configuration-recorder \
  --recording-group '{"allSupported": true, "includeGlobalResourceTypes": true}'

aws configservice put-delivery-channel \
  --delivery-channel '{
    "s3BucketName": "config-bucket",
    "configSnapshotDeliveryProperties": {"deliveryFrequency": "Twelve_Hours"}
  }'

# Aggregator multi-compte
aws configservice put-configuration-aggregator \
  --configuration-aggregator-name org-aggregator \
  --organization-aggregation-source '{
    "RoleArn": "arn:aws:iam::...:role/aws-config-aggregator",
    "AwsRegions": ["us-east-1", "eu-west-1", "ap-southeast-1"],
    "AllAwsRegions": true
  }'
```

### 8.2 Conformance Packs

```bash
# Déployer le Operational Best Practices for S3 pack
aws configservice put-conformance-pack \
  --conformance-pack-name s3-security-pack \
  --template-body file://s3-conformance-pack.yaml
```

**s3-conformance-pack.yaml :**
```yaml
Resources:
  S3BucketPublicReadProhibited:
    Type: AWS::Config::ConfigRule
    Properties:
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED

  S3BucketPublicWriteProhibited:
    Type: AWS::Config::ConfigRule
    Properties:
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_WRITE_PROHIBITED

  S3BucketSSEEnabled:
    Type: AWS::Config::ConfigRule
    Properties:
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED

  S3BucketReplicationEnabled:
    Type: AWS::Config::ConfigRule
    Properties:
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_REPLICATION_ENABLED
```

### 8.3 Remediation Automatique

```bash
# SSM Automation associé à une Config Rule
aws configservice put-remediation-configurations \
  --remediation-configurations '[
    {
      "ConfigRuleName": "S3_BUCKET_PUBLIC_READ_PROHIBITED",
      "TargetType": "SSM_DOCUMENT",
      "TargetId": "AWS-DisableS3BucketPublicReadWrite",
      "Parameters": {
        "AutomationAssumeRole": {"StaticValue": {"Values": ["arn:aws:iam::...:role/config-remediation"]}},
        "BucketName": {"ResourceValue": {"Value": "RESOURCE_ID"}}
      },
      "Automatic": true,
      "MaximumAutomaticAttempts": 3,
      "RetryAttemptSeconds": 60
    }
  ]'
```

---

## 9. AWS Artifact — Gestion des Rapports de Conformité

```bash
# Télécharger les rapports de conformité
aws artifact download-document --document-id <id>

# Lister les documents disponibles
aws artifact list-documents \
  --filter '{"documentType": "SOC3"}'

# SOC2, SOC3, PCI, ISO 27001, FedRAMP
```

---

## 10. Architecture Défensive Complète AWS

```
                    ┌──────────────────────────┐
                    │     AWS Organizations     │
                    │   SCP + GuardDuty Admin   │
                    └──────────┬───────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                 │
    ┌─────────▼──────┐  ┌─────▼──────┐  ┌──────▼──────────┐
    │  Security Hub   │  │   Config   │  │ CloudTrail      │
    │  Cross-Region   │  │ Conformance │  │ Organization    │
    │  Aggregator     │  │   Packs    │  │  Trail          │
    └─────────┬──────┘  └─────┬──────┘  └──────┬──────────┘
              │               │                 │
    ┌─────────▼───────────────▼─────────────────▼──────────┐
    │                 EventBridge Bus                     │
    │         Centralisation des événements de sécurité    │
    └─────────┬───────────────┬─────────────────┬──────────┘
              │               │                 │
    ┌─────────▼──────┐  ┌─────▼──────┐  ┌──────▼──────────┐
    │   Lambda       │  │    SSM     │  │    SIEM         │
    │ Remediation    │  │ Automation │  │  (Splunk/ES)   │
    └────────────────┘  └────────────┘  └─────────────────┘
```

### 10.1 SCP de Sécurité Essentiels

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyRootAccessKeys",
      "Effect": "Deny",
      "Action": ["iam:CreateAccessKey", "iam:UpdateAccessKey"],
      "Resource": ["arn:aws:iam::*:root"]
    },
    {
      "Sid": "DenyLeavingOrg",
      "Effect": "Deny",
      "Action": ["organizations:LeaveOrganization"],
      "Resource": "*"
    },
    {
      "Sid": "DenyPublicS3",
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
      "Sid": "DenyNonApprovedRegions",
      "Effect": "Deny",
      "Action": ["ec2:*", "rds:*"],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["eu-west-1", "eu-west-3", "us-east-1"]
        }
      }
    }
  ]
}
```

---

## 11. Tableau des Services par Fonction

| Fonction | Service AWS | Alternative Open Source |
|----------|-------------|------------------------|
| Détection de menaces | GuardDuty | Wazuh, Security Onion |
| Scan vulnérabilités | Inspector V2 | OpenVAS, Trivy |
| Protection données sensibles | Macie | S3 inspection custom |
| Investigation forensique | Detective | TheHive, Velociraptor |
| Firewall réseau | Network Firewall | iptables, pfSense |
| WAF applicatif | WAF + Shield | ModSecurity, Coraza |
| Firewall management | Firewall Manager | Custom scripting |
| Security posture | Security Hub | Prowler, ScoutSuite |
| Conformité continue | Config | OPA, Checkov |
| Rapport compliance | Artifact | — |
| Protection DDoS | Shield | Cloudflare |

## Pitfalls

- **Ne PAS** activer GuardDuty sans EventBridge → Lambda de remediation (findings sans action)
- **Ne PAS** configurer Security Hub sans intégrer Config (pas de contexte de ressource)
- **Ne PAS** permettre les SCP trop restrictives qui bloquent les pipelines CI/CD
- **TOUJOURS** activer les Data Events CloudTrail pour S3 (coût modéré, sécurité ++)
- **TOUJOURS** configurer un delegated admin multi-compte pour tous les services
- Les conformance packs Config peuvent coûter cher — n'activer que les règles pertinentes
- Firewall Manager nécessite Organizations — pas de workaround

## Ressources

- **AWS Security Services**: https://docs.aws.amazon.com/security/
- **AWS GuardDuty**: https://docs.aws.amazon.com/guardduty/
- **AWS Inspector**: https://docs.aws.amazon.com/inspector/
- **AWS Macie**: https://docs.aws.amazon.com/macie/
- **AWS Detective**: https://docs.aws.amazon.com/detective/
- **AWS Network Firewall**: https://docs.aws.amazon.com/network-firewall/
- **AWS Firewall Manager**: https://docs.aws.amazon.com/fms/
- **AWS Security Hub**: https://docs.aws.amazon.com/securityhub/
- **AWS Config**: https://docs.aws.amazon.com/config/
- **AWS Well-Architected Security Pillar**: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/
