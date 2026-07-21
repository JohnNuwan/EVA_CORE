---
name: cloud-workload-protection
description: Guide complet du Cloud Workload Protection Platform (CWPP) — runtime security, agent-based vs agentless, vulnerability management, file integrity monitoring, container security, serverless protection, et EDR cloud
domain: [cybersecurite, cloud, cwpp]
tags: [cwpp, runtime-security, workload-protection, edr, fim, vulnerability-management, container-security, serverless-security, cloud-antimalware]
priority: haute
---

# 🛡️ Cloud Workload Protection Platform (CWPP) — Guide Complet

Guide exhaustif de la protection des workloads cloud : VMs, conteneurs, serverless, runtime security, et EDR multi-cloud.

---

## 1. Qu'est-ce que le CWPP ?

Le Cloud Workload Protection Platform (CWPP) protège les workloads (VMs, conteneurs, serverless) dans le cloud contre les menaces au niveau runtime.

### 1.1 CWPP vs CSPM vs CASB

| Solution | Focus | Protection |
|----------|-------|------------|
| **CSPM** | Configuration cloud | Posture, compliance |
| **CWPP** | Charge de travail | Runtime, malware, vulns |
| **CASB** | Applications SaaS | Shadow IT, DLP cloud |
| **CIEM** | Entitlements IAM | Permissions, privesc |

### 1.2 Capacités CWPP Essentielles

```
┌──────────────────────────────────────────────────┐
│              CLOUD WORKLOAD PROTECTION             │
├──────────────────────────────────────────────────┤
│  1. Vulnerability Management (scan + prioritise)  │
│  2. Malware & Antivirus (signature + ML)          │
│  3. File Integrity Monitoring (FIM)               │
│  4. Network Security (micro-segmentation)         │
│  5. Application Control (whitelist/blacklist)     │
│  6. Host-based IDS/IPS (HIDS)                    │
│  7. Container Security (runtime)                  │
│  8. Serverless Security (function monitoring)     │
│  9. EDR/EDR for Cloud (detection + response)     │
│  10. Compliance Monitoring (CIS benchmarks)       │
└──────────────────────────────────────────────────┘
```

---

## 2. Approches Agent-Based vs Agentless

### 2.1 Comparaison

| Critère | Agent-Based | Agentless |
|---------|-------------|-----------|
| **Visibilité** | +++ Temps réel | ++ Snapshots/Snapshot |
| **Détection Runtime** | ✓ (process, file, network) | ✗ (scan VM only) |
| **Latence** | Impact sur ressources | Aucun impact |
| **Déploiement** | Agent sur chaque VM | Snapshot/API scan |
| **Maintenance** | Updates, config, monitoring | Aucune |
| **Couverture conteneurs** | ✓ | Partiel |
| **Coût** | Par agent + infrastructure | Par scan |
| **Exemples** | CrowdStrike, Defender ATP | Wiz, Orca, AWS Inspector |

**Recommandation :** Approche hybride = Agentless pour la couverture large + Agent-based pour les workloads critiques

### 2.2 Hybride : Agentless + Agent

```yaml
Stratégie CWPP hybride:
  Agentless:
    - Scan quotidien de toutes les VMs (AWS Inspector, Orca)
    - Détection de vulnérabilités, malwares, secrets
    - Aucun agent à déployer/maintenir
  
  Agent-based (workloads critiques):
    - Protection runtime (EDR, FIM, HIDS)
    - Workloads : Production, PCI-DSS, HIPAA
    - Agents : CrowdStrike Falcon, SentinelOne, Defender for Endpoint
    - Monitoring process, file, network en temps réel
```

---

## 3. Vulnerability Management Cloud

### 3.1 AWS Inspector V2

```bash
# Inspector V2 — scan agentless des VMs et conteneurs
aws inspector2 enable --resource-types EC2 ECR LAMBDA

# Scan en continu + mappings CVE
aws inspector2 list-findings \
  --filter-criteria '{
    "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
    "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
  }' \
  --sort-criteria '{"field": "UPDATED_AT", "sortOrder": "DESC"}' \
  --max-results 50

# Priorisation par score CVSS
aws inspector2 get-findings \
  --finding-arns <arn> \
  --query 'findings[].{Title:title, CVEId:cveId, Score:awsEc2InstanceDetails.imageId, Severity:severity, Fix:remediation.url}'

# Export des findings vers S3
aws inspector2 create-findings-report \
  --report-format CSV \
  --s3-destination bucketName=reports,keyPrefix=vulns/
```

### 3.2 Trivy — Scanner Multi-Cloud

```bash
# Trivy — scan multi-format
trivy image --severity CRITICAL,HIGH myapp:latest
trivy repo --severity CRITICAL github.com/org/repo
trivy fs --severity CRITICAL ./terraform/
trivy config --severity CRITICAL ./k8s/

# Sortie SBOM (Software Bill of Materials)
trivy image --format cyclonedx --output result.cdx.json myapp:latest

# Serveur Trivy (scan continu)
trivy server --listen 0.0.0.0:8080
trivy client --server http://localhost:8080 --format sarif alpine:latest

# Intégration CI/CD
trivy image --exit-code 1 --severity CRITICAL,HIGH myapp:latest
```

### 3.3 Priorisation des Vulnérabilités

```yaml
Facteurs de priorisation:
  1. CVSS Score (9.0+ = critique)
  2. Exploitabilité (EPSS > 0.5 = priorité)
  3. Exposure (publique vs interne)
  4. Data sensitivity (données client vs système)
  5. Network access (internet-facing vs VPC interne)
  6. Attestation (CISA KEV = exploitation active)
  7. Runtime (process utilisant la lib vulnérable)

Score de priorité = CVSS × EPSS × Exposure × Data

Exemple:
  CVE-2024-XXXXX: CVSS 9.8, EPSS 0.7, internet-facing, prod data
  Score = 9.8 × 0.7 × 1.0 × 1.0 = 6.86 → PATCH IMMÉDIAT
  
  CVE-2024-YYYYY: CVSS 9.8, EPSS 0.01, internal only, staging
  Score = 9.8 × 0.01 × 0.3 × 0.3 = 0.009 → PATCH PLANIFIÉ
```

---

## 4. Runtime Security — EDR Cloud

### 4.1 AWS GuardDuty Runtime Monitoring

```bash
# GuardDuty Runtime Monitoring — détection au niveau OS
aws guardduty enable-organization-admin-account --admin-account-id <id>
aws guardduty create-detector --enable

# Activer le Runtime Monitoring pour EKS
aws guardduty update-detector --detector-id <id> \
  --features '[
    {"Name": "EKS_RUNTIME_MONITORING", "Status": "ENABLED", "AdditionalConfiguration": [{"Name": "EKS_ADDON_MANAGEMENT", "Status": "ENABLED"}]}
  ]'

# Activer le Runtime Monitoring pour EC2
aws guardduty update-detector --detector-id <id> \
  --features '[
    {"Name": "EC2_RUNTIME_MONITORING", "Status": "ENABLED"}
  ]'

# Findings runtime typiques
# - CryptoCurrency:EC2/BitcoinTool.B
# - Backdoor:EC2/C&CActivity.B
# - PrivilegeEscalation:EC2/NewBinaryExecuted
# - Behavioral:EC2/MaliciousFile
```

### 4.2 Microsoft Defender for Endpoint (Cloud)

```bash
# Onboarding des VMs cloud vers MDE
# Linux
curl -o /tmp/mde_install.sh https://aka.ms/mde-linux-install
chmod +x /tmp/mde_install.sh
sudo /tmp/mde_install.sh --install

# Vérifier l'état
mdatp health
mdatp connectivity test

# Configurer les exclusions
mdatp exclusion extension add --name .log
mdatp exclusion process add --name /usr/bin/python3

# Windows
# Installer via GPO/Intune
# Déployer via SSM Run Command
aws ssm send-command \
  --document-name "AWS-RunPowerShellScript" \
  --targets "Key=instanceids,Values=i-xxx" \
  --parameters 'commands=["Install-MDE.ps1"]'
```

### 4.3 FIM (File Integrity Monitoring)

```bash
# AWS CloudWatch Agent — FIM
cat > cw-agent-config.json << 'EOF'
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "/etc/passwd",
            "log_group_name": "FIM/etc-passwd",
            "log_stream_name": "{instance_id}",
            "timestamp_format": "%Y-%m-%d %H:%M:%S",
            "retention_in_days": 365
          },
          {
            "file_path": "/etc/shadow",
            "log_group_name": "FIM/etc-shadow",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/etc/ssh/sshd_config",
            "log_group_name": "FIM/sshd-config",
            "log_stream_name": "{instance_id}"
          },
          {
            "file_path": "/var/log/auth.log",
            "log_group_name": "FIM/auth-log",
            "log_stream_name": "{instance_id}"
          }
        ]
      }
    }
  }
}
EOF

# Déployer la config
aws ssm send-command \
  --document-name "AWS-ConfigureAWSPackage" \
  --targets "Key=instanceids,Values=i-xxx" \
  --parameters '{"action": "Install", "name": "AmazonCloudWatchAgent", "version": "latest"}'
```

---

## 5. Container Security

### 5.1 Image Scanning (Build Time)

```yaml
# CI/CD Pipeline — Container Security
# 1. Build image
# 2. Scan with Trivy/Grype
# 3. Sign with Cosign
# 4. Push to registry
# 5. Deploy if scan passes

# .github/workflows/container-scan.yml
name: Container Security Scan
on:
  push:
    branches: [main]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: docker build -t app:${GITHUB_SHA::7} .
      - name: Trivy Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: app:${GITHUB_SHA::7}
          format: sarif
          output: trivy-results.sarif
          severity: CRITICAL,HIGH
          exit-code: 1
      - name: Cosign Sign
        uses: sigstore/cosign-installer@main
      - run: cosign sign --key env://COSIGN_KEY app:${GITHUB_SHA::7}
```

### 5.2 Runtime Container Security

```yaml
# Falco — Runtime Security (CNCF)
# Règles Falco pour conteneurs

# Installation
curl -fsSL https://falco.org/repo/falcosecurity-packages.asc | \
  gpg --dearmor -o /usr/share/keyrings/falco-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/falco-archive-keyring.gpg] https://download.falco.org/packages/deb stable main" | \
  tee /etc/apt/sources.list.d/falcosecurity.list
apt-get update && apt-get install -y falco

# Règles Falco personnalisées
cat > /etc/falco/rules.d/custom-rules.yaml << 'EOF'
- rule: Terminal Shell in Container
  desc: Detects shell execution in container
  condition: >
    spawned_process and container
    and proc.name in (bash, zsh, sh, dash, ash)
    and proc.tty != 0
  output: >
    Shell opened in container (user=%user.name container=%container.name shell=%proc.name)
  priority: WARNING
  tags: [container, mitre_execution]

- rule: Crypto Mining Binary
  desc: Detect crypto mining executables
  condition: >
    spawned_process and container
    and proc.name in (xmrig, miner, cpuminer, ethminer, t-rex, nbminer, lolminer)
  output: >
    Crypto miner detected in container (user=%user.name container=%container.name process=%proc.name)
  priority: CRITICAL
  tags: [container, crypto, mitre_impact]

- rule: Mount of Sensitive Directory
  desc: Detect mount of /etc or /var/run
  condition: >
    mount and container
    and (mount.target startswith /etc or mount.target startswith /var/run)
  output: >
    Sensitive mount detected (container=%container.name target=%mount.target)
  priority: HIGH
  tags: [container, mitre_privilege_escalation]
EOF

# Démarrer Falco
systemctl start falco
systemctl enable falco
```

### 5.3 Kubernetes Security

```yaml
# Kyverno — Policy Engine Kubernetes
# ClusterPolicy: Deny privileged containers
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: deny-privileged-containers
spec:
  validationFailureAction: enforce
  background: true
  rules:
  - name: check-privileged
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Privileged containers are not allowed."
      pattern:
        spec:
          containers:
          - securityContext:
              privileged: false
  - name: check-run-as-non-root
    match:
      any:
      - resources:
          kinds:
          - Pod
    validate:
      message: "Containers must run as non-root."
      pattern:
        spec:
          securityContext:
            runAsNonRoot: true

# ClusterPolicy: Read-only root filesystem
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: read-only-root-fs
spec:
  validationFailureAction: enforce
  rules:
  - name: require-read-only-rootfs
    match:
      resources:
        kinds:
        - Pod
    validate:
      message: "Containers must have readOnlyRootFilesystem: true"
      pattern:
        spec:
          containers:
          - securityContext:
              readOnlyRootFilesystem: true
```

---

## 6. Serverless Security

### 6.1 Lambda Security

```bash
# AWS Lambda — Protection au runtime
# 1. Limiter les permissions IAM (least privilege)
# 2. Scanner les dépendances (Trivy, Snyk)
# 3. Activer AWS Signer (code signing)
# 4. VPC placement + Security Groups
# 5. Environnement variables chiffrées (KMS)

# Vérifier les permissions Lambda trop larges
aws lambda get-function-configuration --function-name <func> \
  --query 'Role'

# Analyser les politiques IAM des fonctions
aws iam list-attached-role-policies --role-name <role-name>

# Code signing obligatoire
aws signer create-signing-profile --platform-id "AWSLambda-SHA384-ECDSA" \
  --name lambda-signer

aws lambda update-function-code --function-name <func> \
  --s3-bucket <bucket> --s3-key <code.zip> \
  --signing-profile-arn arn:aws:signer:....:signing-profile/lambda-signer
```

### 6.2 Cloud Functions Security (GCP)

```bash
# GCP Cloud Functions — Hardening
# 1. Utiliser des Service Accounts dédiés
# 2. Pas de --allow-unauthenticated sauf nécessaire
# 3. Chiffrement des variables d'env (Secret Manager)
# 4. VPC Connector pour les accès réseau
# 5. Cloud Audit Logs activé

# Déployer avec SA dédié
gcloud functions deploy secure-func \
  --runtime python311 \
  --trigger-http \
  --service-account secure-func-sa@project.iam.gserviceaccount.com \
  --set-secrets 'DB_PASSWORD=db-password:latest' \
  --vpc-connector projects/<project>/locations/us-central1/connectors/vpc-connector \
  --ingress-settings internal-only

# Limiter l'invocation
gcloud functions add-invoker-policy-binding secure-func \
  --member "serviceAccount:allowed-sa@project.iam.gserviceaccount.com"
```

### 6.3 Azure Functions Security

```bash
# Azure Functions — Hardening
# 1. Managed Identity au lieu de keys
# 2. App Settings avec Key Vault references
# 3. Network isolation (VNet integration)
# 4. Authentication (EasyAuth)
# 5. Defender for Cloud monitoring

# Key Vault reference
az functionapp config appsettings set \
  --name secure-func \
  --resource-group <RG> \
  --settings 'DB_PASSWORD=@Microsoft.KeyVault(SecretUri=https://kv.vault.azure.net/secrets/db-password/)'

# Network isolation
az functionapp vnet-integration add \
  --name secure-func \
  --resource-group <RG> \
  --vnet prod-vnet \
  --subnet functions-subnet
```

---

## 7. CWPP par Provider

### 7.1 AWS CWPP Stack

```yaml
Services AWS CWPP:
  - Vulnerability: AWS Inspector V2 (agentless)
  - Runtime: GuardDuty Runtime Monitoring (agentless)
  - EDR: AWS Systems Manager + MDE/CrowdStrike (agent)
  - FIM: CloudWatch Agent (agent)
  - Container: ECR scanning + GuardDuty EKS Runtime
  - Serverless: Lambda scanning + IAM least privilege
  - Compliance: Security Hub + Config

Recommandation:
  - Agentless: Inspector V2 + GuardDuty (couverture large)
  - Agent: MDE ou CrowdStrike sur VMs de production
  - Container: Trivy CI/CD + Falco runtime
```

### 7.2 GCP CWPP Stack

```yaml
Services GCP CWPP:
  - Vulnerability: Security Command Center + Web Security Scanner
  - Runtime: SCC Virtual Machine Threat Detection
  - EDR: SCC + Agent (CrowdStrike/SentinelOne)
  - FIM: Cloud Audit Logs + Forseti
  - Container: GKE Security Posture + Artifact Registry scanning
  - Serverless: Cloud Functions + SCC
  - Compliance: SCC Premium + Organization Policies

Recommandation:
  - Agentless: SCC Premium (couverture native)
  - Agent: CrowdStrike sur Compute Engine
  - Container: GKE Security Posture + Binary Authorization
```

### 7.3 Azure CWPP Stack

```yaml
Services Azure CWPP:
  - Vulnerability: Defender for Cloud + Qualys/Tenable (built-in)
  - Runtime: Defender for Servers (Plan 2)
  - EDR: Defender for Endpoint (integrated)
  - FIM: Defender for Servers + Change Tracking
  - Container: Defender for Containers
  - Serverless: Defender for App Service
  - Compliance: Defender for Cloud + Azure Policy

Recommandation:
  - Agentless: Defender for Cloud (couverture native)
  - Agent: Defender for Endpoint (inclus dans Defender for Servers)
  - Container: Defender for Containers + AKS Policy
```

---

## 8. Outils CWPP Open Source

| Outil | Type | Description |
|-------|------|-------------|
| **Falco** | Runtime Security | HIDS/IDS pour conteneurs (CNCF) |
| **Trivy** | Vulnerability Scanner | Images, FS, repos, IaC |
| **Grype** | Vulnerability Scanner | Fast image scanning |
| **Wazuh** | EDR/SIEM | Open source EDR + FIM |
| **Osquery** | OS Instrumentation | SQL-based OS monitoring |
| **Auditd** | Linux Audit | Kernel-level audit |
| **ClamAV** | Antivirus | Open source AV |
| **Lynis** | Security Auditing | System hardening audit |
| **Rkhunter** | Rootkit Hunter | Rootkit detection |
| **Chkrootkit** | Rootkit Detector | Local rootkit detection |
| **OpenSCAP** | Compliance | CIS/SCAP scanning |
| **Suricata** | IDS/IPS | Network-based IDS |

## Pitfalls

- **Ne PAS** se fier uniquement au scanning agentless — les vulnérabilités runtime nécessitent des agents
- **Ne PAS** ignorer les containers — Falco ou équivalent runtime est indispensable
- **TOUJOURS** prioriser les vulnérabilités par contexte (exposition, données, exploitabilité)
- **TOUJOURS** tester les agents EDR sur des workloads non-critiques avant le déploiement
- Les agents CWPP peuvent impacter les performances CPU/mémoire — dimensionner
- Les scanners agentless ne détectent pas les malwares runtime (mémoire, process)
- Les politiques de container security (Kyverno/OPA) doivent être en mode audit d'abord
- La rotation des images container ne suffit pas — scanner au build ET au runtime

## Ressources

- **Falco**: https://falco.org/
- **Trivy**: https://github.com/aquasecurity/trivy
- **Grype**: https://github.com/anchore/grype
- **Kyverno**: https://kyverno.io/
- **Wazuh**: https://wazuh.com/
- **Osquery**: https://osquery.io/
- **AWS CWPP Best Practices**: https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/
- **GCP CWPP**: https://cloud.google.com/security
- **Azure CWPP**: https://docs.microsoft.com/en-us/azure/defender-for-cloud/
- **CIS Benchmarks**: https://www.cisecurity.org/benchmark/cloud