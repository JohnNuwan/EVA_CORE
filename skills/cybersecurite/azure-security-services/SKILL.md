---
name: azure-security-services
description: Guide complet des services de sécurité Azure — Microsoft Defender for Cloud, Sentinel, Azure Policy, Azure AD Identity Protection, Defender XDR, Azure Security Benchmark, Key Vault, Managed HSM, et architecture défensive Azure
domain: [cybersecurite, cloud, azure]
tags: [azure, defender, sentinel, azure-policy, identity-protection, security-benchmark, key-vault, managed-hsm, purview]
priority: haute
---

# 🛡️ Azure Security Services — Guide Défensif Complet

Guide exhaustif des services de sécurité natifs Azure, leur configuration, intégration et bonnes pratiques défensives.

---

## 1. Microsoft Defender for Cloud

### 1.1 Plans Defender

Defender for Cloud (ex Azure Security Center) propose plusieurs plans de protection :

| Plan | Description | Cas d'Usage |
|------|-------------|-------------|
| **Defender for Servers** | Protection VM (OS, app, network) | VMs Windows/Linux |
| **Defender for Storage** | Détection menaces stockage | Blob, Files, ADLS |
| **Defender for SQL** | Détection menaces SQL DB | SQL DB, SQL Managed Instance |
| **Defender for Containers** | Sécurité conteneurs | AKS, ACR, ARC |
| **Defender for App Service** | Détection attaques web | App Service, Functions |
| **Defender for Key Vault** | Détection accès anormaux | Key Vault |
| **Defender for DNS** | Détection tunnellisation DNS | DNS queries |
| **Defender for Resource Manager** | Détection ARM anormales | ARM API |
| **Defender for API** | Détection d'attaques API | API Management |
| **Defender for Open-Source DBs** | Protection MariaDB/MySQL/PostgreSQL | PaaS DBs |

```bash
# Activer tous les plans Defender
az security pricing create --name VirtualMachines --tier Standard
az security pricing create --name StorageAccounts --tier Standard
az security pricing create --name SqlServers --tier Standard
az security pricing create --name AppServices --tier Standard
az security pricing create --name KeyVaults --tier Standard
az security pricing create --name Containers --tier Standard
az security pricing create --name Dns --tier Standard
az security pricing create --name Arm --tier Standard
az security pricing create --name OpenSourceRelationalDatabases --tier Standard
az security pricing create --name Api --tier Standard

# Voir les plans actifs
az security pricing list --output table
```

### 1.2 Secure Score et Recommendations

```bash
# Secure Score global
az security secure-score list --output table

# Score par contrôle
az security secure-score-controls list --output table

# Recommendations par sévérité
az security assessment list --filter "properties.status.code eq 'Unhealthy'" \
  --query "[?properties.displayName].{Name:properties.displayName, Severity:properties.severity}"

# Implémentation automatique
az security assessment create \
  --assessment-name "MFA-required" \
  --status-code healthy
```

### 1.3 Workflow Automation

```bash
# Automation vers Logic App pour les alertes critiques
az security workflow-automation create \
  --name critical-alerts \
  --resource-group <RG> \
  --triggers '[
    {"property": "Severity", "operator": "Equals", "value": "High"},
    {"property": "Severity", "operator": "Equals", "value": "Critical"}
  ]' \
  --actions '[
    {"actionType": "LogicApp", "logicAppResourceId": "<logic-app-id>"},
    {"actionType": "EventHub", "eventHubResourceId": "<eventhub-id>"}
  ]
```

---

## 2. Microsoft Sentinel (SIEM/SOAR Cloud)

### 2.1 Déploiement et Connecteurs

```bash
# Créer un workspace Sentinel
az sentinel setting set \
  --workspace-name sentinel-ws \
  --resource-group <RG> \
  --entity-analytics enabled \
  --ueba enabled

# Connecteurs data sources
cat > sentinel-connectors.sh << 'EOF'
# Azure Activity Logs
az monitor diagnostic-settings create \
  --name sentinel-activity \
  --workspace sentinel-ws \
  --logs '[{"category":"Administrative","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'

# Azure AD Logs (Sign-in + Audit)
# Nécessite Azure AD Premium P2
az monitor diagnostic-settings create \
  --name sentinel-aad \
  --workspace sentinel-ws \
  --logs '[
    {"category":"AuditLogs","enabled":true},
    {"category":"SignInLogs","enabled":true}
  ]'

# Microsoft 365 Defender
az security connector create \
  --resource-group <RG> \
  --location centralus \
  --connector-name m365defender \
  --connector-settings '{"dataTypes": {"alerts": {"state": "Enabled"}, "incidents": {"state": "Enabled"}}}'

# AWS CloudTrail connector
# Via SIEM on AWS S3 → Event Hubs → Sentinel

# GCP Audit Logs connector
# Via Pub/Sub → Cloud Function → Event Hubs → Sentinel
EOF
```

### 2.2 Analytics Rules (KQL)

```sql
-- Règle : Tentative de brute force RDP/SSH
SigninLogs
| where ResultType == 50057  -- User account disabled
| summarize Attempts = count() by UserPrincipalName, IPAddress, ResultType
| where Attempts > 10
| extend Severity = "Medium"

-- Règle : Création de rôle admin suspecte
AuditLogs
| where OperationName contains "Add member to role"
| extend RoleName = tostring(TargetResources[0].displayName)
| where RoleName contains "Global Administrator"
| extend Initiator = tostring(InitiatedBy.user.userPrincipalName)
| project TimeGenerated, Initiator, RoleName, TargetResources
| sort by TimeGenerated desc

-- Règle : Anomalie de volume de transfert Storage
StorageBlobLogs
| where OperationName == "PutBlob"
| summarize TotalBytes = sum(ResponseBodySize) by AccountName, bin(TimeGenerated, 1h)
| where TotalBytes > 10000000000  -- > 10GB en 1h
| extend Severity = "High"

-- Règle : Tentatives d'accès Key Vault échouées
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.KEYVAULT"
| where OperationName == "Authentication" and ResultSignature == "Unauthorized"
| summarize FailedAttempts = count() by CallerIPAddress, bin(TimeGenerated, 5m)
| where FailedAttempts > 20
| extend Severity = "High"

-- Règle : Déploiement de VM dans une région non autorisée
AzureActivity
| where OperationNameValue contains "virtualMachines/write"
| extend Region = tostring(parse_json(Properties).resourceLocation)
| where Region !in ("westeurope", "francecentral")
| extend Severity = "High"

-- Règle : Anomalies de débit réseau sortant
VMConnection
| where Direction == "outbound"
| summarize TotalBytesSent = sum(BytesSent) by Computer, bin(TimeGenerated, 1h)
| where TotalBytesSent > 5000000000  -- > 5GB sortant en 1h
| extend Severity = "Medium"
```

### 2.3 SOAR Playbooks (Logic Apps)

```powershell
# Déployer un playbook de réponse aux incidents
# via Azure Logic Apps avec déclencheur Sentinel

# Exemple : Isole une VM compromise
# Déclencheur : Alerte Sentinel "VM Crypto Mining"
# Action 1 : Désactiver le NIC
# Action 2 : Prendre snapshot pour forensics
# Action 3 : Envoyer notification Teams
# Action 4 : Créer ticket ServiceNow/Jira

# Paramétrage via ARM template
az deployment group create \
  --resource-group <RG> \
  --template-file playbook-arm.json \
  --parameters sentinelWorkspace=sentinel-ws
```

---

## 3. Azure Policy — Gouvernance et Conformité

### 3.1 Policies Essentielles

```bash
# Built-in policies critiques
# Audit / Deny les configurations dangereuses

# 1. Bloquer les accès publics aux Storage Accounts
az policy assignment create \
  --name "deny-storage-public" \
  --display-name "Deny public storage access" \
  --policy "StorageAccountPublicAccessShouldBeDisabled" \
  --params '{"effect": "Deny"}' \
  --scope /subscriptions/<SUB>

# 2. Exiger des Private Endpoints
az policy assignment create \
  --name "require-private-endpoint" \
  --display-name "Require Private Endpoint for SQL" \
  --policy "SQLManagedInstanceShouldUsePrivateEndpoint" \
  --params '{"effect": "Deny"}'

# 3. Imposer TLS 1.2+
az policy assignment create \
  --name "enforce-tls12" \
  --display-name "Enforce TLS 1.2" \
  --policy "WebAppShouldUseTheLatestTLSVersion" \
  --params '{"effect": "Deny"}'

# 4. Bloquer SKUs VM non autorisés
az policy assignment create \
  --name "restrict-vm-skus" \
  --display-name "Restrict VM SKUs" \
  --policy "AllowedVirtualMachineSizeSkus" \
  --params '{"listOfAllowedSKUs": ["Standard_D2s_v3", "Standard_D4s_v3", "Standard_E2s_v3"]}'

# 5. Bloquer les régions non autorisées
az policy assignment create \
  --name "restrict-regions" \
  --display-name "Allowed Locations" \
  --policy "AllowedLocations" \
  --params '{"listOfAllowedLocations": ["westeurope", "francecentral", "uksouth"]}'
```

### 3.2 Initiative (Policy Set) Personnalisée

```bash
# Créer une initiative de sécurité
az policy set-definition create \
  --name "security-baseline" \
  --display-name "Azure Security Baseline" \
  --definitions '[
    {"policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/0a914e76-4921-4c19-b460-a2d36003525a", "parameters": {"effect": {"value": "Deny"}}},
    {"policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/b7ddfbdc-1260-477d-91fd-98bd9be789a6", "parameters": {"effect": {"value": "Deny"}}},
    {"policyDefinitionId": "/providers/Microsoft.Authorization/policyDefinitions/0961003e-5a0a-4549-abde-af6a37f2724d", "parameters": {"effect": {"value": "Deny"}}}
  ]'

# Assigner l'initiative au Management Group
az policy assignment create \
  --name "security-baseline" \
  --policy-set-definition "security-baseline" \
  --scope /providers/Microsoft.Management/managementGroups/<MG> \
  --display-name "Security Baseline Initiative"
```

---

## 4. Azure AD Identity Protection

### 4.1 Configuration

```bash
# Nécessite Azure AD Premium P2

# Configurer les politiques de risque utilisateur
# via Microsoft Graph API
cat > user-risk-policy.json << 'EOF'
{
  "@odata.type": "#microsoft.graph.riskDetectionTimingType",
  "isEnabled": true,
  "riskDetections": [
    {"riskType": "anonymizedIPAddress", "level": "medium"},
    {"riskType": "unfamiliarFeatures", "level": "medium"},
    {"riskType": "leakedCredentials", "level": "low"},
    {"riskType": "malwareInfectedIPAddress", "level": "medium"},
    {"riskType": "suspiciousSessions", "level": "medium"},
    {"riskType": "unlikelyTravel", "level": "medium"}
  ]
}
EOF

# Configurer MFA avec Conditional Access
cat > conditional-access-mfa.json << 'EOF'
{
  "displayName": "Require MFA for Admins",
  "state": "enabled",
  "conditions": {
    "applications": {"includeApplications": ["All"]},
    "users": {"includeRoles": ["62e90394-69f5-4237-9190-012177145e10"]},
    "clientAppTypes": ["all"],
    "locations": {"includeLocations": ["All"], "excludeLocations": ["trusted"]}
  },
  "grantControls": {
    "builtInControls": ["mfa"],
    "operator": "OR"
  }
}
EOF
```

### 4.2 Risky Sign-ins et Users

```bash
# Lister les sign-ins risqués (API Graph)
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/identityProtection/riskySignIns" \
  --query "value[].{User:userPrincipalName, Risk:riskLevel, Type:riskEventTypes, IP:ipAddress}"

# Users risqués
az rest --method GET \
  --url "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers" \
  --query "value[].{User:userPrincipalName, Risk:riskLevel, LastUpdate:riskLastUpdatedDateTime}"

# Confirmer compromission et bloquer
az rest --method POST \
  --url "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers/confirmCompromised" \
  --body '{"userIds": ["<user-id>"]}'
```

---

## 5. Azure DDoS Protection

### 5.1 Activation

```bash
# Créer un DDoS Protection Plan
az network ddos-protection create \
  --name ddos-plan \
  --resource-group <RG> \
  --vnets prod-vnet

# Lier un VNet existant
az network vnet update \
  --name prod-vnet \
  --resource-group <RG> \
  --ddos-protection-plan ddos-plan
```

### 5.2 Monitoring DDoS

```bash
# Metrics DDoS
az monitor metrics list \
  --resource <pip-id> \
  --metric "DDoSProtectionTriggeredTCPPackets" \
  --start-time "2026-07-20T00:00:00Z"

# Alerts
az monitor metrics alert create \
  --name "ddos-attack" \
  --resource-group <RG> \
  --scopes <pip-id> \
  --condition "avg DDoSProtectionTriggeredTCPPackets > 1000" \
  --window-size 5m \
  --action email admin@domain.com,security@domain.com
```

---

## 6. Azure Key Vault — Gestion Centralisée des Secrets

### 6.1 Hardening Key Vault

```bash
# Créer un vault hardened
az keyvault create \
  --name prod-kv \
  --resource-group <RG> \
  --sku Premium \
  --enable-rbac-authorization true \
  --enable-soft-delete true \
  --enable-purge-protection true \
  --retention-days 90 \
  --default-action Deny \
  --bypass AzureServices \
  --network-acls '{"ipRules": [{"value": "192.168.0.0/16", "action": "Allow"}], "virtualNetworkRules": []}'

# RBAC roles au lieu de Access Policies
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee user@domain.com \
  --scope /subscriptions/<SUB>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/prod-kv

# Rotation automatique des secrets
# Key Vault n'a pas de rotation native — utiliser Event Grid + Function
az eventgrid event-subscription create \
  --name secret-expiry \
  --source-resource-id /subscriptions/.../vaults/prod-kv \
  --endpoint-type azurefunction \
  --endpoint https://rotate-function.azurewebsites.net/runtime/webhooks/EventGrid

# Managed HSM (FIPS 140-2 Level 3)
az keyvault create \
  --name prod-hsm \
  --resource-group <RG> \
  --sku Premium \
  --hsm-enabled true \
  --enable-purge-protection true
```

### 6.2 Key Vault Firewall et Logs

```bash
# Audit logs
az monitor diagnostic-settings create \
  --name kv-audit \
  --resource /subscriptions/.../vaults/prod-kv \
  --workspace sentinel-ws \
  --logs '[
    {"category": "AuditEvent", "enabled": true, "retentionPolicy": {"days": 365, "enabled": true}}
  ]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]'
```

---

## 7. Microsoft Defender XDR (365 Defender)

### 7.1 Intégration Multi-Domaine

```bash
# Microsoft 365 Defender unifie :
# - Defender for Endpoint (EDR)
# - Defender for Office 365 (email)
# - Defender for Identity (AD)
# - Defender for Cloud Apps (CASB)
# - Defender for Cloud (IaaS/PaaS)

# Activation via CLI
# Nécessite Azure AD Global Admin
az rest --method POST \
  --url "https://api.security.microsoft.com/api/m365defender/onboard" \
  --body '{}'
```

### 7.2 Chasses Croisées (KQL)

```sql
-- Cross-domain hunting : Email → Device
EmailEvents
| where Timestamp > ago(7d)
| where ThreatTypes has "Malware"
| join kind=inner (
    DeviceEvents
    | where Timestamp > ago(7d)
    | where ActionType == "AntivirusDetection"
) on RecipientEmailAddress
| project Timestamp, RecipientEmailAddress, FileName, ThreatName, DeviceName, ActionType

-- Identity → Cloud : Utilisateur compromis accède au cloud
IdentityLogonEvents
| where Timestamp > ago(1d)
| where RiskLevelDuringSignIn == "high"
| join kind=inner (
    CloudAppEvents
    | where Timestamp > ago(1d)
    | where ActivityObjects[0].Role == "Admin"
) on AccountUpn
```

---

## 8. Azure Privileged Identity Management (PIM)

```bash
# Activer PIM
az rest --method POST \
  --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleRequests?api-version=2020-10-01"

# Configurer l'activation JIT d'un rôle
cat > pim-config.json << 'EOF'
{
  "properties": {
    "roleDefinitionId": "/subscriptions/.../providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635",
    "principalId": "<user-id>",
    "requestType": "AdminAssign",
    "scheduleInfo": {
      "startDateTime": "2026-07-22T00:00:00Z",
      "expiration": {"type": "AfterDuration", "duration": "PT8H"},
      "approvalRequired": true
    },
    "ticketInfo": {"ticketNumber": "SEC-12345"}
  }
}
EOF

# Voir les activations actives
az rest --method GET \
  --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01"
```

---

## 9. Microsoft Purview — Protection des Données

### 9.1 Information Protection

```bash
# Purview Information Protection
# Labels de sensibilité, DLP, classification automatique

# Activer Purview
az purview account create \
  --name purview-prod \
  --resource-group <RG> \
  --location westeurope

# Scanner des sources
az purview scan create \
  --account-name purview-prod \
  --name scan-s3 \
  --scan-ruleset-name "AmazonS3" \
  --collection <collection-id> \
  --data-source-identifier <ds-id>
```

### 9.2 Data Loss Prevention (DLP)

```bash
# Politiques DLP pour Microsoft 365
# Bloquer l'exfiltration de données sensibles via email/Teams/OneDrive

# Cas typiques :
# - Carte de crédit partagée en externe → Block + Notify
# - Code source envoyé par email → Block + Encrypt
# - Document confidentiel uploadé OneDrive → Audit only
```

---

## 10. Architecture Défensive Complète Azure

```
                    ┌───────────────────────────────────────┐
                    │     Azure AD / Entra ID               │
                    │  Conditional Access + Identity Protect │
                    │  PIM + MFA + Legacy Auth Bloqué        │
                    └───────────┬───────────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                  │
    ┌─────────▼───────┐  ┌─────▼───────┐  ┌──────▼─────────┐
    │  Defender for   │  │  Azure      │  │  Microsoft     │
    │  Cloud (CSPM)   │  │  Policy     │  │  Sentinel      │
    └─────────┬───────┘  └─────────────┘  └──────┬─────────┘
              │                                   │
    ┌─────────▼───────────────────────────────────▼─────────┐
    │                    Azure DDoS Protection                │
    │                    Azure Firewall + WAF                 │
    │                    Private Endpoints                    │
    └─────────┬───────────────────────────────────┬──────────┘
              │                                   │
    ┌─────────▼──────────┐  ┌───────────────────▼──────────┐
    │  Key Vault +       │  │  Purview + Defender          │
    │  Managed HSM       │  │  XDR (365)                   │
    │  Secrets Mgmt      │  │  Cross-Domain Hunting        │
    └────────────────────┘  └──────────────────────────────┘
```

### 10.1 Azure Security Benchmark (V3)

```bash
# Les 5 piliers du benchmark Azure :
# 1. Network Security (NS)
# 2. Identity Management (IM)
# 3. Privileged Access (PA)
# 4. Data Protection (DP)
# 5. Asset Management (AM)

# Score automatisé via Defender for Cloud
# Basé sur CIS Microsoft Azure Foundations Benchmark
```

---

## 11. Tableau des Services Azure par Fonction

| Fonction | Service Azure | Alternative |
|----------|--------------|-------------|
| CSPM / Posture | Defender for Cloud | Prowler, ScoutSuite |
| SIEM | Microsoft Sentinel | ELK, Splunk |
| SOAR | Logic Apps + Sentinel | TheHive, Shuffle |
| WAF | Azure WAF v2 + Front Door | Cloudflare |
| DDoS | Azure DDoS Protection | Cloudflare |
| Identité | Azure AD + Conditional Access | Okta, Keycloak |
| PIM | Azure AD PIM | — |
| Secrets | Key Vault + Managed HSM | HashiCorp Vault |
| DLP | Microsoft Purview | Netskope DLP |
| Gouvernance | Azure Policy + Blueprints | OPA, Terraform Sentinel |
| Container Security | Defender for Containers | Aqua, Prisma |
| Protection API | Defender for API | 42Crunch, Salt |

## Pitfalls

- **Ne PAS** activer tous les plans Defender sans budget — le coût peut exploser
- **Ne PAS** configurer Sentinel sans workspace sizing (ingestion GB/jour)
- **Ne PAS** oublier d'exclure les IPs Azure Services des règles Key Vault Firewall
- **TOUJOURS** activer soft-delete + purge protection sur Key Vault
- **TOUJOURS** utiliser RBAC au lieu des Access Policies Key Vault
- PIM nécessite Azure AD Premium P2 — coût par user licence
- Azure Policy peut casser des déploiements — tester en mode audit d'abord
- Sentinel: chaque data source connectée a un coût d'ingestion
- Les playbooks Logic Apps coûtent par exécution

## Ressources

- **Microsoft Defender for Cloud**: https://docs.microsoft.com/en-us/azure/defender-for-cloud/
- **Azure Sentinel**: https://docs.microsoft.com/en-us/azure/sentinel/
- **Azure Policy**: https://docs.microsoft.com/en-us/azure/governance/policy/
- **Azure AD Security**: https://docs.microsoft.com/en-us/azure/active-directory/identity-protection/
- **Azure DDoS Protection**: https://docs.microsoft.com/en-us/azure/ddos-protection/
- **Azure Key Vault**: https://docs.microsoft.com/en-us/azure/key-vault/
- **Azure Security Benchmark**: https://docs.microsoft.com/en-us/security/benchmark/azure/
- **Microsoft Defender XDR**: https://docs.microsoft.com/en-us/microsoft-365/security/defender/
- **Microsoft Purview**: https://docs.microsoft.com/en-us/purview/