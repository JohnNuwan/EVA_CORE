---
name: cloud-iam-security
description: Guide complet de sécurité IAM multi-cloud — AWS IAM, GCP IAM, Azure RBAC/AD, politiques, rôles, fédération d'identité, moindre privilège, analyse des chemins de privesc, et durcissement
category: cybersecurite
---

# Cloud IAM Security — AWS / GCP / Azure

---

## 1. AWS IAM

### Structure IAM AWS
```
┌─────────────────────────────────────────────┐
│                   AWS Root                    │
├─────────────────────────────────────────────┤
│  Users (personnes)  │  Roles (services)     │
│  Groups (collection) │  Policies (droits)    │
│  Service Accounts <=> │  Instance Profiles    │
│  SAML/OIDC Providers  │  Permission Boundaries│
│  Organizations (SCP)  │  Access Analyzer     │
└─────────────────────────────────────────────┘
```

### Types de Politiques
```bash
# 1. AWS Managed Policies (prédéfinies par AWS)
arn:aws:iam::aws:policy/AdministratorAccess
arn:aws:iam::aws:policy/ReadOnlyAccess

# 2. Customer Managed Policies (créées par vous)
aws iam create-policy --policy-name custom-policy --policy-document file://policy.json

# 3. Inline Policies (attachées directement à un user/role)
aws iam put-user-policy --user-name <user> --policy-name inline-policy --policy-document file://policy.json

# 4. Resource-based Policies (attachées à la ressource)
# S3 bucket policy, KMS key policy, Lambda resource policy
aws s3api put-bucket-policy --bucket <name> --policy file://bucket-policy.json

# 5. Service Control Policies (SCP — AWS Organizations)
# Limite les permissions max dans un compte
aws organizations create-policy --content file://scp.json --name "DenyRootAccess" --type SERVICE_CONTROL_POLICY

# 6. Permission Boundaries
# Définit le maximum de permissions qu'un IAM principal peut avoir
```

### Évaluation des Politiques IAM
```bash
# Simulateur de politique
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::<account>:user/<user> \
  --action-names s3:ListBucket ec2:DescribeInstances iam:CreateUser

# Policy Simulator complet
# https://policysim.aws.amazon.com/

# Access Analyzer — validation
aws accessanalyzer validate-policy --policy-type IDENTITY_POLICY --policy-document file://policy.json
```

### Chemins de Privesc IAM

| Permission | Attaque |
|------------|---------|
| `iam:CreatePolicyVersion` | Créer une version admin d'une politique |
| `iam:SetDefaultPolicyVersion` | Changer la version active |
| `iam:CreateAccessKey` | Créer une clé pour un autre user |
| `iam:UpdateLoginProfile` | Changer le mot de passe d'un autre user |
| `iam:PassRole` | Passer un rôle à un service |
| `iam:CreateUser` + `iam:AttachUserPolicy` | Créer un user admin |
| `iam:UpdateAssumeRolePolicy` | Modifier le trust policy |
| `sts:AssumeRole` | Usurper un rôle |
| `lambda:UpdateFunctionCode` | Backdoor une Lambda |
| `ec2:RunInstances` + `iam:PassRole` | Lancer une instance avec un rôle privilégié |

```bash
# Analyse PMapper
pip install pmapper
pmapper --profile default query 'presigned privesc'
pmapper --profile default query 'can privesc to *'
pmapper --profile default visualize
pmapper --profile default query 'who can do iam:CreateUser'
```

### AWS Organizations
```bash
# SCP — bloquer les actions dangereuses
cat > scp-deny-leave-org.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Deny",
    "Action": [
      "organizations:LeaveOrganization",
      "organizations:DeleteOrganization",
      "iam:CreateAccessKey",
      "iam:CreateUser"
    ],
    "Resource": "*"
  }]
}
EOF
aws organizations create-policy --content file://scp-deny-leave-org.json --name "SCP-Deny-Dangerous" --type SERVICE_CONTROL_POLICY

# SCP — deny root access keys
aws organizations create-policy --content file://scp-root-no-keys.json --name "DenyRootAccessKeys" --type SERVICE_CONTROL_POLICY
```

### Hardening IAM AWS
```bash
# 1. No inline policies
aws iam list-user-policies --user-name <user>  # doit être vide

# 2. No access keys for root
aws iam get-account-summary | grep AccountAccessKeysPresent

# 3. MFA for all human users
aws iam list-virtual-mfa-devices

# 4. Password policy forte
aws iam update-account-password-policy --minimum-password-length 16 --require-symbols

# 5. Conditions dans les politiques
# Exemple: deny access outside VPC
"Condition": {
  "StringNotEquals": {
    "aws:SourceVpc": "vpc-12345678"
  }
}

# 6. Permission Boundaries
aws iam put-user-permissions-boundary --user-name <user> --permissions-boundary arn:aws:iam::...:policy/boundary

# 7. Access Analyzer — détection des accès externes
aws accessanalyzer create-analyzer --analyzer-name prod-analyzer --type ACCOUNT
aws accessanalyzer list-findings --analyzer-arn <arn>
```

---

## 2. GCP IAM

### Structure IAM GCP
```
┌──────────────────────────────────────────────┐
│          Organization (<org>)                  │
├──────────────────────────────────────────────┤
│  Folders (hiérarchie)                          │
│  Projects (ressources)                         │
│  Service Accounts (identités non-humaines)    │
│  Roles (prédéfinis, custom, primitifs)        │
│  Members (user, group, SA, domain, allUsers)  │
│  Conditions (context-aware)                    │
│  Workload Identity Federation (OIDC/SAML)     │
└──────────────────────────────────────────────┘
```

### Types de Rôles GCP
```bash
# 1. Rôles primitifs (à éviter)
# roles/owner, roles/editor, roles/viewer

# 2. Rôles prédéfinis
# roles/storage.objectViewer, roles/compute.admin

# 3. Rôles custom
gcloud iam roles create CustomRole --project <project> --title "Custom Role" --permissions storage.objects.list,storage.objects.get

# 4. Rôles de base (Basic Roles) — dépréciés
# Utiliser des rôles prédéfinis ou custom
```

### Service Accounts GCP
```bash
# Création
gcloud iam service-accounts create <name> --display-name "My SA"

# Attribution de rôles
gcloud projects add-iam-policy-binding <project> \
  --member "serviceAccount:<name>@<project>.iam.gserviceaccount.com" \
  --role "roles/storage.admin"

# Création de clés
gcloud iam service-accounts keys create key.json \
  --iam-account <name>@<project>.iam.gserviceaccount.com

# Workload Identity Federation (OIDC)
gcloud iam workload-identity-pools create <pool> --location global
gcloud iam workload-identity-pools providers create-oidc <provider> \
  --location global \
  --workload-identity-pool <pool> \
  --issuer-uri https://token.actions.githubusercontent.com \
  --attribute-mapping "google.subject=assertion.sub"
```

### Conditions IAM GCP
```bash
# Conditions contextuelles
gcloud projects add-iam-policy-binding <project> \
  --member user:admin@domain.com \
  --role roles/compute.admin \
  --condition "expression=request.time < timestamp('2026-12-31T23:59:59Z'),title=expiry"

# Resource-based conditions
gcloud projects add-iam-policy-binding <project> \
  --member user:dev@domain.com \
  --role roles/storage.objectViewer \
  --condition "expression=resource.name.startsWith('projects/_/buckets/dev-'),title=dev-only"
```

### Chemins de Privesc GCP

| Permission | Impact |
|------------|--------|
| `iam.roles.update` | Modifier un rôle custom |
| `iam.serviceAccountKeys.create` | Créer une clé pour un autre SA |
| `iam.serviceAccounts.actAs` | Impersonate un SA |
| `iam.serviceAccounts.implicitDelegation` | Delegation de SA |
| `iam.serviceAccounts.getAccessToken` | Obtenir un token OAuth |
| `compute.instances.setMetadata` | Changer les SSH keys |
| `compute.instances.setIamPolicy` | Modifier l'IAM d'une instance |
| `iam.roles.create` | Créer un rôle avec toutes les permissions |
| `iam.serviceAccounts.setIamPolicy` | Se donner accès à un SA |

```bash
# Analyser les permissions IAM
gcloud projects get-iam-policy <project> --format json | jq '.bindings[] | select(.role | test("owner|admin|editor"))'

# Trouver les SA avec des clés
gcloud iam service-accounts keys list --iam-account <sa>@<project>.iam.gserviceaccount.com
```

### Hardening IAM GCP
```bash
# 1. Pas de rôles primitifs
gcloud projects get-iam-policy <project> --format json | jq '.bindings[] | select(.role | test("roles/owner|roles/editor|roles/viewer"))'

# 2. Désactiver les SA par défaut
gcloud iam service-accounts disable <default-sa>@<project>.iam.gserviceaccount.com

# 3. OS Login — pas de SSH keys manuelles
gcloud compute project-info add-metadata --metadata enable-oslogin=TRUE

# 4. Audit des clés SA
for SA in $(gcloud iam service-accounts list --format="value(email)"); do
  echo "SA: $SA"
  gcloud iam service-accounts keys list --iam-account $SA --managed-by-user
done

# 5. VPC Service Controls
gcloud access-context-manager perimeters create <perimeter> --resources projects/<project>

# 6. Domain Restricted Sharing
# Organisation policy: restrict all users to G Suite domain
```

---

## 3. Azure RBAC & Azure AD

### Structure Azure Identity
```
┌─────────────────────────────────────────────────┐
│               Azure AD (Tenant)                   │
│  Users │ Groups │ Service Principals │ App Regs │
│  Managed Identities │ Conditional Access │ PIM  │
├─────────────────────────────────────────────────┤
│            Azure RBAC (Subscription)              │
│  Role Assignments │ Role Definitions │ Scopes    │
└─────────────────────────────────────────────────┘
```

### Azure RBAC Roles
```bash
# Rôles intégrés (Built-in)
# Owner, Contributor, Reader, User Access Administrator
# Key Vault Secrets User, Storage Blob Data Owner, etc.

# Lister les rôles
az role definition list --output table

# Rôles custom
az role definition create --role-definition @custom-role.json

# Exemple custom role
cat > custom-role.json << 'EOF'
{
  "Name": "Storage Auditor",
  "IsCustom": true,
  "Description": "Read-only storage access",
  "Actions": [
    "Microsoft.Storage/storageAccounts/read",
    "Microsoft.Storage/storageAccounts/blobServices/containers/read"
  ],
  "NotActions": [],
  "AssignableScopes": ["/subscriptions/<sub-id>"]
}
EOF
```

### Azure AD — Identités
```bash
# Users
az ad user list --output table
az ad user show --id <user>

# Groups
az ad group list --output table
az ad group member list --group <group>

# Service Principals
az ad sp list --output table
az ad sp list --query "[].{DisplayName:displayName, AppId:appId, Type:servicePrincipalType}"

# Application Registrations
az ad app list --output table
az ad app list --query "[].{DisplayName:displayName, AppId:appId, SignInAudience:signInAudience}"
```

### Managed Identities Azure
```bash
# System-assigned (liée à une ressource)
az vm identity assign --name <vm> --resource-group <RG>

# User-assigned (indépendante)
az identity create --name <identity> --resource-group <RG>
az vm identity assign --name <vm> --resource-group <RG> --identities <identity-id>

# Obtenir un token depuis la VM
curl "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" -H "Metadata: true"
```

### Azure AD Privileged Identity Management (PIM)
```bash
# PIM — Just-In-Time elevation
# Rôles éligibles vs actifs
# Activation avec approbation + MFA + justification

# Vérifier les rôles PIM
az rest --method get --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01"

# Éligible Owner
az rest --method get --url "https://management.azure.com/providers/Microsoft.Authorization/roleEligibilityScheduleInstances?api-version=2020-10-01&filter=roleDefinitionId eq '8e3af657-a8ff-443c-a75c-2fe8c4bcb635'"
```

### Conditional Access
```bash
# Policies de Conditional Access
# Bloque les accès depuis des IP non fiables
# Exige MFA pour les rôles admin
# Bloque les legacy authentication
# Exige device compliance (Intune)

# Azure AD Identity Protection
# Risky users, risky sign-ins
az rest --method get --url "https://graph.microsoft.com/v1.0/identityProtection/riskyUsers"
```

### Chemins de Privesc Azure

| Permission RBAC | Impact |
|-----------------|--------|
| `Microsoft.Authorization/roleAssignments/write` | Attribuer n'importe quel rôle |
| `Microsoft.Authorization/roleDefinitions/write` | Créer/modifier des rôles custom |
| `Microsoft.ManagedIdentity/userAssignedIdentities/assign/action` | Attacher une MSI |
| `Microsoft.KeyVault/vaults/write` | Modifier les politiques Key Vault |
| `Microsoft.Compute/virtualMachines/write` | Exécuter des commandes sur VM |
| `Microsoft.Authorization/locks/delete` | Supprimer les locks |
| `Microsoft.Automation/automationAccounts/write` | Modifier des runbooks |

```bash
# AzureHound — BloodHound pour Azure
# Analyser les chemins de privesc
az ad sp create-for-rbac -n "azurehound" --role "Global Reader"
./AzureHound --tenant <tenant> --username <user> --password <pass>
```

### Hardening Azure Identity
```bash
# 1. Legacy authentication bloqué
# Conditional Access: Block legacy auth

# 2. MFA obligatoire
# Conditional Access: Require MFA for all users

# 3. Guest users restriction
az ad user list --query "[?userType=='Guest']" --output table

# 4. Audit des Service Principals
az ad sp list --query "[?passwordCredentials != null || keyCredentials != null]"

# 5. Azure AD Identity Protection
# Risky user policies
# Sign-in risk policies

# 6. PIM pour tous les rôles admin
# Activation just-in-time, approbation, audit

# 7. Pas de rôle Owner au niveau subscription
az role assignment list --all --query "[?roleDefinitionName=='Owner']"
```

---

## 4. Fédération d'Identité Multi-Cloud

### AWS — SAML/OIDC Federation
```bash
# SAML 2.0
aws iam create-saml-provider --saml-metadata-document file://metadata.xml --name AzureAD

# OIDC (GitHub Actions, GitLab, etc.)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com

# Web Identity — assume role with web token
aws sts assume-role-with-web-identity \
  --role-arn arn:aws:iam::<account>:role/GitHubRole \
  --role-session-name github-actions \
  --web-identity-token <token>
```

### GCP — Workload Identity Federation
```bash
# OIDC federation avec GitHub Actions
gcloud iam workload-identity-pools create gh-pool --location global
gcloud iam workload-identity-pools providers create-oidc gh-provider \
  --location global \
  --workload-identity-pool gh-pool \
  --issuer-uri https://token.actions.githubusercontent.com \
  --attribute-mapping "google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --attribute-condition "assertion.repository_owner == 'my-org'"

# Attribution
gcloud iam service-accounts add-iam-policy-binding <sa>@<project>.iam.gserviceaccount.com \
  --member "principalSet://iam.googleapis.com/projects/<project>/locations/global/workloadIdentityPools/gh-pool/attribute.repository/my-org/*" \
  --role "roles/iam.workloadIdentityUser"
```

### Azure — Managed Identity Federation
```bash
# Federated Identity Credentials
az ad app federated-credential create \
  --id <app-id> \
  --parameters '{
    "name": "GitHubActions",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:my-org/my-repo:environment:prod",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

---

## 5. Outils d'Analyse IAM

| Outil | AWS | GCP | Azure | Description |
|-------|-----|-----|-------|-------------|
| **PMapper** | ✓ | ✗ | ✗ | Analyse des chemins de privesc IAM |
| **Principal Mapper** | ✓ | ✗ | ✗ | Visualisation des permissions |
| **AzureHound** | ✗ | ✗ | ✓ | BloodHound pour Azure AD |
| **ROADtools** | ✗ | ✗ | ✓ | Azure AD investigation |
| **gcp_iam_analyzer** | ✗ | ✓ | ✗ | Analyse IAM GCP |
| **Policy Sentry** | ✓ | ✗ | ✗ | Analyse minimale de politique |
| **Access Analyzer** | ✓ | ✗ | ✗ | AWS IAM Access Analyzer |
| **CloudSploit** | ✓ | ✓ | ✓ | Permissions checking |
| **Prowler** | ✓ | ✓ | ✓ | IAM checks CIS |
| **ScoutSuite** | ✓ | ✓ | ✓ | IAM audit |

## Ressources

- **AWS IAM Documentation**: https://docs.aws.amazon.com/IAM/latest/UserGuide/
- **GCP IAM Documentation**: https://cloud.google.com/iam/docs
- **Azure RBAC Documentation**: https://docs.microsoft.com/en-us/azure/role-based-access-control/
- **IAM Privesc AWS**: https://rhinosecuritylabs.com/aws/aws-iam-privilege-escalation/
- **IAM Privesc GCP**: https://rhinosecuritylabs.com/gcp/privilege-escalation-google-cloud-platform-part-1/
- **IAM Privesc Azure**: https://rhinosecuritylabs.com/azure/azure-privilege-escalation/
- **PMapper**: https://github.com/nccgroup/PMapper
- **AzureHound**: https://github.com/BloodHoundAD/AzureHound
- **ROADtools**: https://github.com/dirkjanm/ROADtools
- **Policy Sentry**: https://github.com/salesforce/policy_sentry