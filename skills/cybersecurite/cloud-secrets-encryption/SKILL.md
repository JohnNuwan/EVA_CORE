---
name: cloud-secrets-encryption
description: Guide complet de gestion des secrets et chiffrement multi-cloud — KMS, Secrets Manager, Key Vault, HSM, chiffrement au repos/transit, PKI, rotation automatique, durcissement crypto
category: cybersecurite
---

# Cloud Secrets & Encryption — AWS / GCP / Azure

---

## 1. AWS — Gestion des Secrets & Chiffrement

### AWS KMS (Key Management Service)
```bash
# Créer une clé symétrique
aws kms create-key --description "Production Master Key" --origin AWS_KMS

# Clé asymétrique (sign/verify)
aws kms create-key --description "Signing Key" --key-usage SIGN_VERIFY --customer-master-key-spec RSA_2048

# Alias
aws kms create-alias --alias-name alias/prod-key --target-key-id <key-id>

# Rotation automatique
aws kms enable-key-rotation --key-id <key-id>

# Policy key — qui peut l'utiliser
aws kms get-key-policy --key-id <key-id> --policy-name default
aws kms put-key-policy --key-id <key-id> --policy-name default --policy file://key-policy.json

# Chiffrer/déchiffrer
aws kms encrypt --key-id alias/prod-key --plaintext fileb://secret.txt --output text --query CiphertextBlob | base64 --decode > secret.encrypted
aws kms decrypt --ciphertext-blob fileb://secret.encrypted --output text --query Plaintext | base64 --decode

# Générer un secret
aws kms generate-random --number-of-bytes 32
```

### AWS Secrets Manager
```bash
# Créer un secret
aws secretsmanager create-secret --name prod/db/password --secret-string '{"username":"admin","password":"P@ssw0rd"}'

# Rotation automatique (Lambda)
aws secretsmanager rotate-secret --secret-id prod/db/password

# Récupérer un secret
aws secretsmanager get-secret-value --secret-id prod/db/password
aws secretsmanager get-secret-value --secret-id prod/db/password --query SecretString --output text | jq .

# Lister les secrets
aws secretsmanager list-secrets
aws secretsmanager list-secret-version-ids --secret-id prod/db/password

# Policy de ressource
aws secretsmanager get-resource-policy --secret-id prod/db/password
```

### AWS Systems Manager Parameter Store
```bash
# Créer un paramètre (Standard ou Advanced)
aws ssm put-parameter --name /prod/app/db-url --value "postgresql://prod.internal:5432" --type SecureString --key-id alias/prod-key

# Récupérer
aws ssm get-parameter --name /prod/app/db-url --with-decryption
aws ssm get-parameters-by-path --path /prod/ --recursive

# Hiérarchie
# /prod/app/db-url
# /prod/app/db-password
# /staging/app/db-url
```

### AWS CloudHSM
```bash
# HSM dédié (FIPS 140-2 Level 3)
aws cloudhsmv2 create-cluster --hsm-type hsm1.medium
aws cloudhsmv2 initialize-cluster --cluster-id <id> --signed-cert file://customerCert.pem

# Cas d'usage: clés réglementaires, PKI, signatures
```

### AWS Certificate Manager (ACM)
```bash
# Provisionner un certificat TLS
aws acm request-certificate --domain-name app.domain.com --validation-method DNS

# Certificats importés (pour BYO PKI)
aws acm import-certificate --certificate file://cert.pem --private-key file://key.pem --certificate-chain file://chain.pem

# ACM Private CA
aws acm-pca create-certificate-authority --certificate-authority-configuration file://ca-config.json
```

---

## 2. GCP — Gestion des Secrets & Chiffrement

### Cloud KMS
```bash
# Créer un keyring
gcloud kms keyrings create prod --location global

# Créer une clé
gcloud kms keys create prod-key --keyring prod --location global --purpose encryption

# Rotation schedule
gcloud kms keys update prod-key --keyring prod --location global --rotation-period 30d --next-rotation-time "2026-01-01T00:00:00Z"

# Chiffrer/déchiffrer
echo -n "secret-data" | gcloud kms encrypt --key prod-key --keyring prod --location global --plaintext-file - --ciphertext-file - | base64
gcloud kms decrypt --key prod-key --keyring prod --location global --ciphertext-file - --plaintext-file - | base64 --decode

# Clés asymétriques
gcloud kms keys create signing-key --keyring prod --location global --purpose asymmetric-signing --default-algorithm rsa-sign-pkcs1-2048-sha256

# IAM sur les clés
gcloud kms keys add-iam-policy-binding prod-key --keyring prod --location global --member user:admin@domain.com --role roles/cloudkms.cryptoKeyEncrypterDecrypter
```

### Secret Manager
```bash
# Créer un secret
echo -n "supersecret" | gcloud secrets create db-password --data-file=-

# Versions
gcloud secrets versions list db-password
gcloud secrets versions access latest --secret=db-password
gcloud secrets versions add db-password --data-file=new-secret.txt

# Accès
gcloud secrets add-iam-policy-binding db-password --member user:admin@domain.com --role roles/secretmanager.secretAccessor

# Rotation automatique (Cloud Function)
gcloud secrets update db-password --rotation-period 30d --next-rotation-time "2026-01-01T00:00:00Z" --next-rotation-topic projects/<project>/topics/rotate
```

### Cloud HSM
```bash
# HSM géré (FIPS 140-2 Level 3)
# Créer une clé Cloud HSM
gcloud kms keys create hsm-prod-key --keyring prod --location global --purpose encryption --protection-level hsm

# Même API que Cloud KMS, mais clés stockées dans HSM
```

### Certificate Authority Service
```bash
# Créer une CA privée
gcloud privateca pools create prod-pool --location us-central1
gcloud privateca roots create prod-ca --pool prod-pool --location us-central1 --subject "CN=CA Root,O=MyOrg"

# Créer un certificat
gcloud privateca certificates create app-cert \
  --pool prod-pool --location us-central1 \
  --csr file://app.csr \
  --validity "P365D"
```

---

## 3. Azure — Gestion des Secrets & Chiffrement

### Key Vault
```bash
# Créer un vault
az keyvault create --name <vault> --resource-group <RG> --sku Premium --enable-rbac-authorization true --enable-soft-delete true --enable-purge-protection true

# Secrets
az keyvault secret set --vault-name <vault> --name "db-password" --value "P@ssw0rd"
az keyvault secret show --vault-name <vault> --name "db-password"
az keyvault secret list --vault-name <vault>

# Soft-delete — récupérer un secret supprimé
az keyvault secret recover --vault-name <vault> --name "db-password"
az keyvault secret purge --vault-name <vault> --name "db-password"  # permanent

# Keys
az keyvault key create --vault-name <vault> --name "rsa-key" --protection hsm --kty RSA-HSM --size 4096
az keyvault key encrypt --vault-name <vault> --name "rsa-key" --algorithm RSA-OAEP --value <plaintext>
az keyvault key decrypt --vault-name <vault> --name "rsa-key" --algorithm RSA-OAEP --value <ciphertext>
```

### Azure Disk Encryption
```bash
# Chiffrement de disques VM avec SSE + CMK
az vm encryption enable --resource-group <RG> --name <vm> --disk-encryption-keyvault <vault> --key-encryption-key <key>

# Storage Service Encryption (SSE)
az storage account update --name <account> --resource-group <RG> --encryption-key-name <key> --encryption-key-source Microsoft.Keyvault
```

### App Configuration / Managed Identity
```bash
# Azure App Configuration
az appconfig kv set --name <config-store> --key "db:password" --value "P@ssw0rd" --label prod
az appconfig kv set --name <config-store> --key "db:password" --value "dev_pass" --label dev

# Key Vault References dans App Config
# @Microsoft.KeyVault(SecretUri=https://vault.vault.azure.net/secrets/db-password/)
```

---

## 4. Attaques sur les Secrets Cloud

### Extraction depuis Variables d'Environnement
```bash
# AWS Lambda
aws lambda get-function-configuration --function-name <name> --query Environment

# GCP Cloud Functions
gcloud functions describe <name> --format="get(environmentVariables)"

# Azure Functions
az functionapp config appsettings list --name <app> --resource-group <RG>
```

### Side-Channel via Logs
```bash
# Chercher des secrets dans CloudWatch
aws logs filter-log-events --log-group-name /aws/lambda/<func> --filter-pattern "password"
aws logs filter-log-events --log-group-name /aws/lambda/<func> --filter-pattern "secret"

# CloudTrail — sensitive data in API calls
aws cloudtrail lookup-events --lookup-attributes AttributeKey=ResourceName,AttributeValue=<bucket> --query "Events[].CloudTrailEvent"

# Stackdriver (GCP)
gcloud logging read "resource.type=cloud_function AND textPayload=password"
```

### Key Vault Misconfigurations
```bash
# Azure — vault accessible publiquement (bypass firewall)
az keyvault show --name <vault> --query properties.networkAcls

# AWS — KMS key policy over-permissive
aws kms get-key-policy --key-id <key> --policy-name default | jq '.Statement[] | select(.Effect == "Allow" and .Principal == "*")'

# GCP — KMS key accessible à allUsers
gcloud kms keys get-iam-policy prod-key --keyring prod --location global
```

### Secrets dans Git / CI/CD
```bash
# gitLeaks
gitleaks detect --source . --verbose

# truffleHog
trufflehog filesystem --directory .

# GitHub secret scanning (API)
curl -H "Authorization: token <gh-token>" https://api.github.com/repos/org/repo/secret-scanning/alerts
```

---

## 5. Bonnes Pratiques

### Rotation Automatique
```bash
# AWS — Secrets Manager rotation
# Créer une Lambda de rotation attachée au secret
# Rotation schedule: 30, 60, 90 jours
aws secretsmanager rotate-secret --secret-id <id> --rotation-rules "AutomaticallyAfterDays=30"

# GCP — Secret Manager rotation (Cloud Function)
gcloud secrets update db-password --rotation-period 2592000s  # 30 jours

# Azure — Key Vault rotation
# Key Vault n'a pas de rotation automatique intégrée
# Utiliser Azure Automation ou Event Grid + Function
```

### Least Privilege sur les Clés
```bash
# AWS — séparer les rôles
# Admin: kms:CreateKey, kms:PutKeyPolicy
# Operator: kms:Encrypt, kms:Decrypt (sur des clés spécifiques)

# Policy KMS conditionnelle
"Condition": {
  "StringEquals": {
    "kms:ViaService": "s3.amazonaws.com"
  }
}

# GCP — conditions par ressource
"condition": {
  "expression": "resource.name.startsWith('projects/_/locations/global/keyRings/prod')"
}

# Azure — Key Vault RBAC
# Key Vault Secrets User (lecture seulement)
# Key Vault Crypto Officer (gestion des clés)
# Key Vault Administrator (full control)
```

### Détection des Anomalies
```bash
# AWS — GuardDuty: CryptoCurrency:EC2/BitcoinTool.B
aws guardduty list-findings --detector-id <id>

# GCP — Security Command Center: Crypto Mining
gcloud scc findings list --organization <org> --filter "state=\"ACTIVE\" AND category=\"cryptomining\""

# Azure — Defender for Cloud: CryptoMining
az security alert list --filter "alertDisplayName eq 'CryptoMining'"
```

### BYOK / HYOK (Bring Your Own Key)
```bash
# AWS — External Key Store (XKS)
# Clés stockées dans votre HSM on-premise
# aws kms create-key --origin EXTERNAL

# GCP — Cloud External Key Manager (EKM)
# Clés gérées via un partenaire (Thales, Fortanix)

# Azure — Managed HSM + BYOK
# Importer une clé HSM dans Azure Key Vault Managed HSM
az keyvault key import --vault-name <vault> --name byok-key --byo-file key.pem
```

---

## 6. Outils

| Outil | Description |
|-------|-------------|
| **gitleaks** | Secret scanning dans git | https://github.com/gitleaks/gitleaks |
| **truffleHog** | Deep secret scanning | https://github.com/trufflesecurity/trufflehog |
| **detect-secrets** | Yelp secret detection | https://github.com/Yelp/detect-secrets |
| **kms-security-audit** | Audit KMS politique | https://github.com/awslabs/kms-security-audit |
| **keyvault-bench** | Benchmark Azure KV | https://github.com/Azure/KeyVault-benchmarking |
| **vault-operator** | HashiCorp Vault | https://www.vaultproject.io/ |
| **aws-nuke** | Nettoyage de comptes | https://github.com/rebuy-de/aws-nuke |

## Ressources

- **AWS Secrets Best Practices**: https://docs.aws.amazon.com/secretsmanager/latest/userguide/best-practices.html
- **GCP Secret Manager Best Practices**: https://cloud.google.com/secret-manager/docs/best-practices
- **Azure Key Vault Best Practices**: https://docs.microsoft.com/en-us/azure/key-vault/general/best-practices
- **OWASP Secrets Management Cheatsheet**: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- **HashiCorp Vault vs Cloud Native**: https://www.hashicorp.com/resources/vault-vs-cloud-native-secrets-management