---
name: cloud-detection-response
description: Guide complet de détection et réponse aux incidents cloud — GuardDuty, Security Hub, Security Command Center, Defender for Cloud, Sentinel, CloudTrail, Audit Logs, SIEM integration, forensic cloud, playbooks IR
category: cybersecurite
---

# Cloud Detection & Incident Response

---

## 1. AWS — Detection & Monitoring

### AWS GuardDuty
```bash
# Activation
aws guardduty create-detector --enable --finding-publishing-frequency FIFTEEN_MINUTES

# Lister les findings
aws guardduty list-findings --detector-id <id>
aws guardduty get-findings --detector-id <id> --finding-ids <ids> --output json

# Types de findings critiques
# UnauthorizedAccess:EC2/SSHBruteForce
# UnauthorizedAccess:IAMUser/ConsoleLoginSuccess
# CryptoCurrency:EC2/BitcoinTool.B
# Backdoor:EC2/C&CActivity.B
# Policy:IAMUser/RootCredentialUsage
# Discovery:S3/MaliciousIPCaller
# PrivilegeEscalation:IAMUser/AnomalousBehavior

# CRON — muted low severity
aws guardduty update-filter --detector-id <id> --filter-name auto-mute --finding-criteria '{"Criterion":{"severity":{"Gte":1,"Lte":4}}}'
```

### AWS Security Hub
```bash
# Activation
aws securityhub enable-security-hub --enable-standards "arn:aws:securityhub:us-east-1::standards/aws-foundational-security-best-practices/v/1.0.0"

# Findings
aws securityhub get-findings --filters '{"SeverityLabel":[{"Value":"CRITICAL","Comparison":"EQUALS"}],"ComplianceStatus":[{"Value":"FAILED","Comparison":"EQUALS"}]}'

# Custom actions
aws securityhub create-action-target --name "Create Jira Ticket" --description "Create Jira" --id "create-jira"
```

### AWS CloudTrail
```bash
# Organisation trail
aws cloudtrail create-trail --name org-trail --s3-bucket-name <bucket> --is-organization-trail --enable-log-file-validation
aws cloudtrail start-logging --name org-trail

# Lookup events
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=CreateUser --start-time "2026-07-20T00:00:00Z"

# Queries Athena
# CREATE EXTERNAL TABLE cloudtrail_logs (...)
# SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress
# FROM cloudtrail_logs
# WHERE eventName IN ('CreateUser', 'CreateAccessKey', 'PutUserPolicy')
# ORDER BY eventTime DESC
```

### AWS Config
```bash
# Config rules — détection de drift
aws configservice put-config-rule --config-rule file://s3-public-read-prohibited.json
aws configservice put-config-rule --config-rule file://restricted-ssh.json

# Aggregator multi-compte
aws configservice put-configuration-aggregator --configuration-aggregator-name org-aggregator --organization-aggregation-source '{"RoleArn":"...","AwsRegions":["us-east-1","eu-west-1"],"AllAwsRegions":true}'
```

### Incident Response Playbook AWS

**Playbook: Compromission IAM**
```bash
# 1. Identifier le scope
aws cloudtrail lookup-events --lookup-attributes AttributeKey=UserArn,AttributeValue=<arn>
aws accessanalyzer list-findings --analyzer-arn <arn>

# 2. Désactiver les credentials
aws iam update-access-key --access-key-id <key> --status Inactive --user-name <user>
aws iam create-login-profile --user-name <user> --password "ResetTemporary!" --password-reset-required

# 3. Revoke sessions
aws iam delete-service-specific-credential --service-specific-credential-id <id> --user-name <user>

# 4. Analyser le périmètre
# Quelles ressources ont été touchées ?
aws s3 ls # vérifier les buckets accessibles
aws ec2 describe-instances --filters "Name=instance-state-name,Values=running"

# 5. Isoler
# SCP deny all pour le compte
# Security group deny all sur les instances
# Chiffrer les clés compromises

# 6. Forensic
# Snapshot des volumes EBS
aws ec2 create-snapshot --volume-id <vol> --description "Forensic snapshot $(date)"
# CloudTrail logs → S3 → Athena → SIEM
```

**Playbook: Crypto Mining**
```bash
# 1. Détection GuardDuty: CryptoCurrency:EC2/BitcoinTool.B
aws guardduty get-findings --detector-id <id> --finding-ids <id>

# 2. Isoler l'instance
# Stop l'instance
aws ec2 stop-instances --instance-ids <id>
# Détacher du ASG
aws autoscaling detach-instances --instance-ids <id> --auto-scaling-group-name <asg> --should-decrement-desired-capacity

# 3. Analyser
# CloudTrail: qui a lancé l'instance ?
# VPC Flow Logs: trafic sortant suspect
# Tags: chercher d'autres instances similaires
```

---

## 2. GCP — Detection & Monitoring

### Security Command Center
```bash
# Voir les findings
gcloud scc findings list --organization <org> --filter "state=\"ACTIVE\""
gcloud scc findings list --organization <org> --filter "category=\"cryptomining\"" --format json

# Mute findings
gcloud scc mute-configs create auto-mute --organization <org> --description "Auto-mute low"

# Notification config
gcloud scc notifications create <notification> --organization <org> --pubsub-topic <topic> --filter "state=\"ACTIVE\" AND severity=\"CRITICAL\""
```

### Cloud Audit Logs
```bash
# Admin Activity (toujours activé)
# Data Access (à activer)
gcloud projects get-iam-policy <project> --format json | jq '.auditConfigs'

# Query logs
gcloud logging read "resource.type=project AND protoPayload.methodName=CreateServiceAccount" --limit 10

# Exporter vers BigQuery
gcloud logging sinks create audit-sink bigquery.googleapis.com/projects/<project>/datasets/audit --log-filter="severity>=WARNING"

# Log-based metrics + alerts
gcloud logging metrics create root-activity --description "Root activity" --log-filter "protoPayload.authenticationInfo.principalEmail =~ \"root.*@\""

# Alert policy
gcloud alpha monitoring policies create --policy=root-activity-alert.yaml
```

### Cloud Monitoring + Alerting
```bash
# Uptime check
gcloud monitoring uptime-check-configs create --display-name=api-prod --http-check-path=/health --period=60s

# Alert policy
cat > cpu-alert.yaml << 'EOF'
combiner: OR
conditions:
- conditionThreshold:
    filter: resource.type="gce_instance" AND metric.type="compute.googleapis.com/instance/cpu/utilization"
    thresholdValue: 0.9
    duration: 300s
  displayName: High CPU
displayName: CPU Alert
notificationChannels:
- projects/<project>/notificationChannels/<channel>
EOF
gcloud alpha monitoring policies create --policy-from-file=cpu-alert.yaml
```

### Incident Response Playbook GCP

**Playbook: Service Account Key Compromise**
```bash
# 1. Trouver l'origine
gcloud logging read "protoPayload.methodName=google.iam.admin.v1.CreateServiceAccountKey" --limit 20

# 2. Désactiver la clé
gcloud iam service-accounts keys disable <key-id> --iam-account <sa>@<project>.iam.gserviceaccount.com

# 3. Rotation
gcloud iam service-accounts keys create new-key.json --iam-account <sa>@<project>.iam.gserviceaccount.com

# 4. Audit complet
# Vérifier les actions faites avec ce SA
gcloud logging read "protoPayload.authenticationInfo.principalEmail:<sa>@<project>.iam.gserviceaccount.com"
```

**Playbook: Data Exfiltration via GCS**
```bash
# 1. Identifier le bucket et l'objet exfiltré
gcloud logging read "protoPayload.methodName=storage.objects.get" --limit 50

# 2. VPC Service Controls — perimeter
gcloud access-context-manager perimeters create exfil-perimeter \
  --perimeter-type regular \
  --resources projects/<project> \
  --restricted-services storage.googleapis.com

# 3. Audit IAM du bucket
gsutil iam get gs://<bucket>

# 4. Activation des Data Access Logs
gcloud projects get-iam-policy <project> --format json | jq '.auditConfigs += [{"service":"storage.googleapis.com","auditLogConfigs":[{"logType":"DATA_READ"},{"logType":"DATA_WRITE"}]}]'
```

---

## 3. Azure — Detection & Monitoring

### Microsoft Defender for Cloud
```bash
# Plans Defender
az security pricing list --output table
az security pricing create --name VirtualMachines --tier Standard  # Activer

# Secure Score
az security secure-score list --output table
az security secure-score-controls list

# Alerts
az security alert list --output table
az security alert show --name <alert-name>
az security alert update --name <alert-name> --status Dismiss

# Workflow automation
az security workflow-automation create --name jira-ticket --resource-group <RG> --triggers '[{"property":"All","operator":"Contains","value":"Critical"}]' --actions '[{"actionType":"LogicApp","logicAppResourceId":"<logic-app-id>"}]'
```

### Azure Sentinel (Microsoft Sentinel)
```bash
# Déploiement
az sentinel setting set --workspace-name <ws> --resource-group <RG> --entity-analytics enabled

# Data connectors
# Azure Activity → Sentinel
# Azure AD Logs → Sentinel
# Azure Defender Alerts → Sentinel

# Analytics rules (KQL)
# Brute force attempt
SigninLogs
| where ResultType == 50057  # User account disabled
| summarize Count = count() by UserPrincipalName, IPAddress
| where Count > 10

# Suspicious role assignment
AuditLogs
| where OperationName == "Add member to role"
| where TargetResources[0].displayName has_any("Global Admin", "Owner")
```

### Azure Monitor
```bash
# Metrics + Alerts
az monitor metrics alert create --name "High CPU" --resource-group <RG> --scopes <vm-id> --condition "avg Percentage CPU > 90" --window-size 5m --evaluation-frequency 1m

# Action Groups
az monitor action-group create --name critical-team --resource-group <RG> --action email admin@domain.com

# Log Analytics Workspace Queries
# Required: Azure Activity, NSG Flow Logs
```

### Incident Response Playbook Azure

**Playbook: Azure AD Compromise**
```bash
# 1. Détection via Identity Protection
az rest --method get --url "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
az rest --method get --url "https://graph.microsoft.com/v1.0/identityProtection/riskySignIns"

# 2. Bloquer
# Désactiver l'utilisateur
az ad user update --id <user> --account-enabled false

# Revoke sessions
az rest --method post --url "https://graph.microsoft.com/v1.0/users/<user>/revokeSignInSessions"

# Reset MFA
az rest --method patch --url "https://graph.microsoft.com/v1.0/users/<user>/authentication/methods/<method-id>" --body "{}"

# 3. Investiguer
# Quelles applications ? Quelles données ?
az rest --method get --url "https://graph.microsoft.com/v1.0/users/<user>/appRoleAssignments"
az rest --method get --url "https://graph.microsoft.com/v1.0/users/<user>/ownedDevices"
```

**Playbook: VM Cryptojacking**
```bash
# 1. Identifier via Defender
az security alert list --filter "alertDisplayName eq 'VM with high CPU crypto mining'"

# 2. Stop immédiat
az vm deallocate --name <vm> --resource-group <RG>

# 3. Snapshot forensic
az snapshot create --name forensic-snap --resource-group <RG> --source <vm-os-disk>

# 4. Analyser
# Network Watcher NSG Flow Logs
# VM process (via Run Command)
az vm run-command invoke --command-id RunShellScript --name <vm> --resource-group <RG> --scripts "ps aux | grep miner"
```

---

## 4. SIEM Integration Multi-Cloud

### SIEM Architectures
```bash
# Open-Source: ELK Stack
# Filebeat (CloudTrail) → Logstash → Elasticsearch → Kibana
# Audit Logs (GCP) → Pub/Sub → Logstash → ES
# Azure Event Hubs → Logstash → ES

# Splunk
# AWS: Splunk Add-on for AWS
# GCP: Google Cloud Source
# Azure: Splunk Add-on for Microsoft Cloud Services

# Microsoft Sentinel (natif Azure + multi-cloud)
# AWS: AWS S3 connector → Sentinel
# GCP: Google Cloud Logging connector
```

### Log Sources by Provider
```bash
# AWS
# CloudTrail (management, data events)
# VPC Flow Logs (network traffic)
# CloudWatch Logs (app logs)
# GuardDuty findings
# Security Hub findings
# AWS Config (resource changes)
# WAF logs
# Route53 resolver logs

# GCP
# Admin Activity audit logs
# Data Access audit logs
# System Event audit logs
# VPC Flow Logs
# Cloud Monitoring metrics
# Security Command Center findings

# Azure
# Azure Activity Logs
# Azure AD Audit Logs + Sign-in Logs
# NSG Flow Logs
# Azure Monitor metrics
# Defender for Cloud alerts
# Key Vault audit logs
```

### Centralized Detection Rules (Multi-Cloud)

**Rule: Root/Admin Account Activity**
```bash
# AWS: eventName == RootAccountUsage
# GCP: principalEmail endsWith @<org> && permission == admin
# Azure: OperationCategory == Administrative && Status == Succeeded
```

**Rule: Unauthorized API Call**
```bash
# AWS: errorCode == AccessDenied || errorCode == UnauthorizedOperation
# GCP: protoPayload.status.code == 7 (PERMISSION_DENIED)
# Azure: ResultType == Authorization_RequestDenied
```

**Rule: Resource Hijacking**
```bash
# AWS: instanceType contains gpu || p3 || p4
# GCP: machineType contains accelerator
# Azure: vmSize contains Standard_NC || Standard_ND
```

---

## 5. Cloud Forensics

### AWS Forensic
```bash
# 1. Snapshot EBS
aws ec2 create-snapshot --volume-id <vol> --description "Forensic $(date +%Y%m%d)"

# 2. Create volume from snapshot
aws ec2 create-volume --snapshot-id <snap> --availability-zone us-east-1a
aws ec2 attach-volume --volume-id <new-vol> --instance-id <forensic-vm> --device /dev/xvdf

# 3. Memory dump (if access)
# LiME (Linux Memory Extractor)
insmod lime.ko "path=/tmp/mem.dump format=lime"

# 4. CloudTrail analysis (Athena)
SELECT eventTime, eventName, userIdentity.arn, sourceIPAddress, requestParameters
FROM cloudtrail_logs
WHERE eventName IN ('CreateInstance', 'CreateUser')
  AND eventTime > '2026-07-20T00:00:00Z'
ORDER BY eventTime
```

### GCP Forensic
```bash
# 1. Snapshot disk
gcloud compute disks snapshot <disk> --snapshot-names forensic-$(date +%Y%m%d) --zone us-central1-a

# 2. Create disk + attach
gcloud compute disks create forensic-disk --source-snapshot forensic-20260720 --zone us-central1-a
gcloud compute instances attach-disk <forensic-vm> --disk forensic-disk

# 3. Audit logs → BigQuery
# SELECT protopayload_auditlog.methodName, protopayload_auditlog.authenticationInfo.principalEmail
# FROM `<project>.audit.cloudaudit_googleapis_com_activity`
# WHERE timestamp > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
```

### Azure Forensic
```bash
# 1. Disk snapshot
az snapshot create --name forensic-snap --resource-group <RG> --source <vm-os-disk>

# 2. Create disk
az disk create --name forensic-disk --resource-group <RG> --source <snapshot-id>

# 3. Attach to forensic VM
az vm disk attach --vm-name <forensic-vm> --resource-group <RG> --disk forensic-disk

# 4. Azure Activity Logs → Log Analytics
# AzureActivity
# | where OperationNameValue contains "virtualMachines"
# | where ActivityStatusValue == "Succeeded"
```

---

## 6. Outils & Ressources

| Outil | Cloud | Usage |
|-------|-------|-------|
| **Prowler** | Multi | Posture assessment |
| **ScoutSuite** | Multi | Config audit |
| **CloudSploit** | Multi | Security scanning |
| **Cartography** | Multi | Relationship mapping |
| **CloudMapper** | AWS | Network visualization |
| **Forseti Security** | GCP | Policy enforcement |
| **AzureHound** | Azure | Attack path mapping |
| **TheHive** | Multi | Incident management |
| **Cortex XSOAR** | Multi | SOAR playbooks |
| **Splunk ES** | Multi | SIEM |

## Ressources

- **AWS IR Guide**: https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/
- **GCP IR Guide**: https://cloud.google.com/security/incident-response
- **Azure IR Guide**: https://docs.microsoft.com/en-us/azure/security/fundamentals/incident-response
- **NIST Incident Response**: https://csrc.nist.gov/publications/detail/sp/800-61/rev-2/final
- **MITRE ATT&CK Cloud**: https://attack.mitre.org/matrices/enterprise/cloud/
- **AWS GuardDuty Finding Types**: https://docs.aws.amazon.com/guardduty/latest/ug/guardduty_finding-types-active.html
- **Cloud Security Alliance IR**: https://cloudsecurityalliance.org/research/incident-response/