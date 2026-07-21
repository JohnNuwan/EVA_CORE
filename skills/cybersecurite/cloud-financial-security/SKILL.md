---
name: cloud-financial-security
description: Guide complet de sécurité financière cloud — cost anomalies, resource hijacking, crypto mining detection, budget alerts, orphan resources, license compliance, FinOps security, AWS Budgets, GCP quotas, Azure Cost Management
category: cybersecurite
---

# Cloud Financial Security & Cost Attacks

---

## 1. Financial Threats in the Cloud

### Types d'Attaques Financières
```
┌──────────────────────────────────────────────────┐
│           Cloud Financial Attacks                │
├──────────────────────────────────────────────────┤
│ 1. Crypto Mining (EC2/GCE/VM hijacking)           │
│ 2. Resource Hijacking (GPU instances, ASICs)      │
│ 3. Data Egress (exfiltration massive)             │
│ 4. Orphan Resources (forgotten services)          │
│ 5. Reserved Instance Fraud                        │
│ 6. API Key Abuse (external access)                │
│ 7. Budget Anomaly (legitimate but expensive ops)  │
│ 8. Marketplace Fraud (fraudulent AMI/VM images)   │
└──────────────────────────────────────────────────┘
```

### Cost Impact par Service
| Service | Coût élevé (€/h) | Impact |
|---------|------------------|--------|
| GPU Instances (p4d/A100/H100) | 30-40 €/h | Crypto mining |
| Data Transfer (egress) | 0.05-0.12 €/GB | Exfiltration |
| Lambda (million invocations) | 0.20 € | DDoS serverless |
| DynamoDB (million RCUs) | 0.15 € | NoSQL injection |
| Cloud Storage (PB data) | 20 €/TB/mois | Data hoarding |
| KMS (million requests) | 0.03 €/10K | API abuse |

---

## 2. AWS — Financial Security

### AWS Budgets
```bash
# Budget mensuel
aws budgets create-budget --account-id <account> --budget file://budget.json

cat > budget.json << 'EOF'
{
  "BudgetName": "Monthly-Prod",
  "BudgetLimit": { "Amount": "10000", "Unit": "USD" },
  "TimeUnit": "MONTHLY",
  "BudgetType": "COST",
  "CostFilters": {},
  "CostTypes": {
    "IncludeTax": true,
    "IncludeSubscription": true,
    "UseBlended": false,
    "IncludeRefund": false,
    "IncludeCredit": false,
    "IncludeUpfront": false,
    "IncludeRecurring": false,
    "IncludeOtherSubscription": false,
    "IncludeSupport": true,
    "IncludeDiscount": true,
    "UseAmortized": false
  }
}
EOF

# Budget alerts (SNS)
aws budgets create-notification --account-id <account> --budget-name Monthly-Prod --notification file://notification.json

cat > notification.json << 'EOF'
{
  "NotificationType": "ACTUAL",
  "ComparisonOperator": "GREATER_THAN",
  "Threshold": 80,
  "ThresholdType": "PERCENTAGE"
}
EOF
```

### AWS Cost Anomaly Detection
```bash
# Cost Anomaly Monitor
aws ce create-anomaly-monitor --monitor file://monitor.json

cat > monitor.json << 'EOF'
{
  "MonitorName": "Prod-Monitor",
  "MonitorType": "DIMENSIONAL",
  "MonitorDimension": { "DimensionKey": "SERVICE" },
  "MonitorSpecification": { "MonitorArn": "" }
}
EOF

# Monitor subscriptions
aws ce create-anomaly-subscription --subscription file://subscription.json
```

### Crypto Mining Detection (AWS)
```bash
# GuardDuty — crypto mining finding
aws guardduty get-findings --detector-id <id> --finding-ids <id>

# CloudWatch — GPU utilization spike
aws cloudwatch get-metric-statistics --metric-name GPUUtilization --namespace AWS/EC2 --dimensions Name=InstanceId,Value=<id> --start-time "2026-07-20T00:00:00Z" --end-time "2026-07-21T00:00:00Z" --period 300 --statistics Average

# Custom CloudWatch alarm
aws cloudwatch put-metric-alarm --alarm-name GPU-Mining-Detection \
  --alarm-description "Detect GPU crypto mining" \
  --metric-name GPUUtilization \
  --namespace AWS/EC2 \
  --statistic Average \
  --period 300 \
  --threshold 90 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=InstanceType,Value=p3.2xlarge \
  --evaluation-periods 2

# VPC Flow Logs — miner pool traffic
# Query Athena: destination port == 3333(Stratum) ou 8333(Bitcoin)
SELECT dstaddr, dstport, bytes
FROM vpc_flow_logs
WHERE dstport IN (3333, 8333, 4444, 5555)
  AND action = 'ACCEPT'
```

### Resource Hijacking Prevention
```bash
# SCP — restreindre les types d'instances
cat > scp-restrict-instances.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictGPUInstances",
      "Effect": "Deny",
      "Action": "ec2:RunInstances",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringLike": {
          "ec2:InstanceType": [
            "p3.*","p4d.*","p4de.*",
            "g4dn.*","g5.*","g6.*",
            "inf1.*","inf2.*","trn1.*"
          ]
        }
      }
    }
  ]
}
EOF
aws organizations create-policy --content file://scp-restrict-instances.json --name "RestrictGPUInstances" --type SERVICE_CONTROL_POLICY

# Compute Optimizer — detect idle resources
aws compute-optimizer get-ec2-instance-recommendations --instance-arns <arn>
```

### Cost Optimization Security
```bash
# AWS Trusted Advisor
# Cost Optimization checks:
# - Idle Load Balancers
# - Underutilized EC2 instances
# - Unassociated Elastic IPs
# - RDS idle DB instances

# AWS Instance Scheduler (auto stop/start)
# CloudFormation template: AWS Solutions Instance Scheduler
# Schedule: 08:00-20:00 weekdays

# Orphan Resources Detection
aws resourcegroupstaggingapi get-resources --resources-per-page 50
aws ec2 describe-instances --filters "Name=instance-state-name,Values=stopped"
aws ebs describe-volumes --filters "Name=status,Values=available"
```

---

## 3. GCP — Financial Security

### Budget & Alerts
```bash
# Créer un budget
gcloud billing budgets create \
  --billing-account <billing-id> \
  --display-name "Monthly-Prod" \
  --budget-amount 10000 \
  --threshold-rules percent=0.5,percent=0.9,percent=1.0 \
  --filter-credit-types "PROMOTION,COMMITTED_USAGE_DISCOUNT" \
  --notifications-rule-pubsub-topic <topic> \
  --notifications-rule-schema-format "JSON"

# Alert thresholds
# 50%: notify
# 90%: warn
# 100%: critical + auto-block
# 150%: emergency
```

### Crypto Mining Detection (GCP)
```bash
# Security Command Center
gcloud scc findings list --organization <org> \
  --filter "category=\"cryptomining\" AND state=\"ACTIVE\"" \
  --format json

# Cloud Monitoring — GPU utilization
gcloud logging read "resource.type=gce_instance AND metric.type=compute.googleapis.com/instance/gpu/utilization" \
  --freshness=24h

# Recommender — cost insights
gcloud recommender insights list \
  --insight-type=google.cloud.billing.CostInsight \
  --project=<project> \
  --location=global

# Cloud Quotas — prevent resource abuse
gcloud compute quotas list --project=<project>
gcloud compute project-info describe --project=<project>
```

### Quota Management
```bash
# Vérifier les quotas
gcloud compute regions describe us-central1 --format="table(quotas)"

# Demander des quotas augmentés
# Dans la console: IAM & Admin → Quotas
# Limiter par défaut les GPU quotas

# Organization Policy — quota restrictions
gcloud resource-manager org-policies set-policy --organization=<org> file://gpu-quota-policy.yaml
```

### Cost Anomaly Detection
```bash
# Cloud Billing Reports
gcloud billing accounts describe <billing-id>

# BigQuery — cost analysis
# SELECT service.description, SUM(cost) as total_cost
# FROM `<project>.billing_dataset.gcp_billing_export_v1_*`
# WHERE _PARTITIONTIME >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
# GROUP BY service.description
# ORDER BY total_cost DESC
```

---

## 4. Azure — Financial Security

### Azure Cost Management
```bash
# Budget
az consumption budget create \
  --amount 10000 \
  --budget-name "Monthly-Prod" \
  --category cost \
  --scope /subscriptions/<sub-id> \
  --time-grain Monthly \
  --time-period start-date=2026-07-01,end-date=2027-07-01 \
  --notifications '{"thresholdType":"Actual","threshold":80,"operator":"GreaterThan","enabled":true,"contactEmails":["admin@domain.com"]}'

# Anomaly Alerts
# Cost Alerts → Anomaly Detection
# (Preview feature dans Cost Management)
```

### Resource Hijacking Prevention (Azure)
```bash
# Azure Policy — restrict VM SKU
cat > restrict-vm-sku.json << 'EOF'
{
  "policyRule": {
    "if": {
      "anyOf": [
        { "field": "Microsoft.Compute/virtualMachines/sku.name", "like": "Standard_NC*" },
        { "field": "Microsoft.Compute/virtualMachines/sku.name", "like": "Standard_ND*" },
        { "field": "Microsoft.Compute/virtualMachines/sku.name", "like": "Standard_NV*" }
      ]
    },
    "then": { "effect": "deny" }
  },
  "parameters": {},
  "displayName": "Restrict GPU VM Sizes"
}
EOF
az policy definition create --name restrict-gpu --rules restrict-vm-sku.json

# Blueprint — enforce cost controls
az blueprint create --name cost-controls --resource-group <RG>
```

### Orphan Resources Cleanup
```bash
# Azure Resource Graph — find orphans
# Resources
# | where type has 'Microsoft.Compute/disks'
# | where managedBy == ''  # unattached disks

# Stopped VMs (deallocated = no compute cost, but disk cost remains)
az vm list --query "[?powerState=='VM deallocated']" --output table

# Unused Public IPs
az network public-ip list --query "[?ipConfiguration==null]" --output table

# Old snapshots (> 30 days)
az snapshot list --query "[?timeCreated < '2026-06-01']" --output table
```

---

## 5. Multi-Cloud Cost Detection

### Unified Cost Monitoring
```bash
# OpenCost (CNCF) — Kubernetes cost
helm install opencost opencost/opencost --namespace opencost
kubectl port-forward service/opencost 9001:9001
curl http://localhost:9001/allocation/compute?aggregate=namespace

# CloudHealth (VMware/broadcom)
# Multi-cloud cost + security analytics

# Infracost — Terraform cost estimation
infracost breakdown --path ./terraform/
infracost diff --path ./terraform/ --compare-to infracost-base.json
```

### Anomaly Detection Patterns

**Pattern 1: Unexplained GPU Spike**
```yaml
# Multi-cloud watcher
# AWS: p3/p4 instances launching
# GCP: A100/V100 instances
# Azure: NC/ND series
# ALERT: new GPU instance not through approved AMI/Image
```

**Pattern 2: Data Transfer Explosion**
```yaml
# AWS: > 1TB/day egress (normally < 100GB)
# GCP: > 500GB/day network egress
# Azure: > 1TB/day bandwidth
# ALERT: > 5x baseline data transfer
```

**Pattern 3: API Call Abuse**
```yaml
# AWS: CloudTrail > 100k events/hour
# GCP: > 50k audit log events/hour
# Azure: > 100k Activity log events/hour
# ALERT: 10x normal API call volume
```

---

## 6. Automated Response Playbooks

### AWS — Auto-shutdown Crypto Mining
```bash
# Lambda + GuardDuty + EventBridge
# 1. GuardDuty finding → EventBridge → Lambda
# 2. Lambda: stop instance + snapshot + tag "compromised"
# 3. SNS notification to security team
# 4. CloudTrail audit

cat > lambda-crypto-response.py << 'EOF'
import boto3

def handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = event['detail']['resource']['instanceDetails']['instanceId']
    finding_id = event['detail']['id']
    
    # Tag as compromised
    ec2.create_tags(Resources=[instance_id], Tags=[{'Key':'Compromised', 'Value':'CryptoMining'}])
    
    # Snapshot for forensics
    volumes = ec2.describe_volumes(Filters=[{'Name':'attachment.instance-id', 'Values':[instance_id]}])
    for vol in volumes['Volumes']:
        ec2.create_snapshot(VolumeId=vol['VolumeId'], Description=f"Forensic_{finding_id}")
    
    # Stop instance
    ec2.stop_instances(InstanceIds=[instance_id])
    
    return {'statusCode': 200, 'body': f'Instance {instance_id} stopped'}
EOF
```

### GCP — Quota Block on Anomaly
```bash
# Cloud Function + Security Command Center
# Détection → désactiver les rights du SA → alert

gcloud functions deploy crypto-block \
  --runtime python311 \
  --trigger-topic crypto-alerts \
  --source ./ \
  --entry-point block_resource
```

### Azure — Auto-remediate
```bash
# Logic App + Defender for Cloud
# Workflow Automation: on alert → Logic App → shutdown VM
az logic workflow create --name crypto-response --resource-group <RG> --definition @response-workflow.json
```

---

## 7. FinOps Security Checklist

```
BUDGETS & ALERTS
☐ Budgets multi-niveaux (80%, 90%, 100%, 150%)
☐ Anomaly detection activée (AWS Cost Anomaly, Azure Anomaly, GCP Recommender)
☐ Alertes SMS/Email/Pager configurées
☐ Budgets par équipe/projet/environnement

COST PREVENTION
☐ SCP/Organization Policy: restriction GPU instances
☐ Quotas GPU: valeur par défaut = 0
☐ Pas de ressources publiques (buckets, RDS, etc.)
☐ Pas de IAM user avec AdminAccess (use roles)

DETECTION
☐ GuardDuty / SCC / Defender crypto mining activé
☐ GPU Utilization monitoring + alert
☐ Data egress anomaly detection
☐ API call rate monitoring

CLEANUP
☐ Orphan resources: unattached disks, unused IPs, stopped VMs
☐ Idle instances: stop after X hours inactivity
☐ Old snapshots: delete after X days
☐ Unused load balancers: detect + delete
☐ Expired reserved instances: renew or remove

IAM & COMPLIANCE
☐ Permission boundaries: empêcher les user de lancer des instances chères
☐ Approval workflow pour GPU instances
☐ Tagging policy: obligatoire (cost center, environment)
☐ Resource locks sur les ressources critiques

AUTOMATION
☐ Instance Scheduler: stop at night/weekend
☐ Auto-scaling limits: min/max bounded
☐ Lambda/Function auto-response on crypto detection
☐ Weekly cost report to team
```

## Ressources

- **AWS Cost Anomaly Detection**: https://docs.aws.amazon.com/cost-management/latest/userguide/manage-ad.html
- **GCP Cost Anomaly Detection**: https://cloud.google.com/billing/docs/how-to/notify
- **Azure Cost Alerts**: https://docs.microsoft.com/en-us/azure/cost-management-billing/costs/cost-mgt-alerts-monitor-usage-spending
- **FinOps Foundation**: https://www.finops.org/
- **Cloud Cryptomining Defense**: https://aws.amazon.com/blogs/security/how-to-protect-your-aws-account-from-cryptocurrency-mining/
- **OpenCost**: https://www.opencost.io/
- **Infracost**: https://www.infracost.io/