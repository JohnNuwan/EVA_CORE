---
name: cloud-devsecops
description: Guide complet de DevSecOps cloud — CI/CD pipeline security, IaC scanning (Terraform, CloudFormation, ARM), SAST/DAST, secret scanning, SBOM, supply chain security, et Shift Left
category: cybersecurite
---

# Cloud DevSecOps — CI/CD & Pipeline Security

---

## 1. Shift Left — Principes

### DevSecOps Pipeline
```
Code → IaC Scan → SAST → Secret Scan → Build → SBOM → DAST → Deploy → Post-Deploy
│        │          │        │           │       │       │        │          │
│    Checkov    Semgrep  gitleaks  Docker  Syft   ZAP    Prowler  GuardDuty
│    tfsec      CodeQL   truffleHog        Trivy          Scout    Defender
│    Snyk IaC   SonarQube                  └─ Cosign       └─ OPA/Gatekeeper
```

---

## 2. Infrastructure as Code Security

### Terraform Scanning
```bash
# Checkov — scan complet IaC
checkov -d ./terraform/ --framework terraform -o cli,sarif,json
checkov -d ./terraform/ --skip-check CKV_AWS_1,CKV_AWS_2  # skip checks
checkov -d ./terraform/ --compact  # output compact
checkov -f ./prod/main.tf --repo-root-for-plan-enrichment .

# tfsec
tfsec ./terraform/ --config-file .tfsec/config.yml
tfsec ./terraform/ --format sarif --output results.sarif

# Terrascan
terrascan scan -d ./terraform/ -t aws
terrascan scan -i terraform -f main.tf

# Snyk IaC
snyk iac test ./terraform/
snyk iac test ./terraform/ --report
```

### AWS CloudFormation Scanning
```bash
# cfn-lint (validation syntaxe)
cfn-lint template.yaml
cfn-lint templates/*.yaml --ignore-checks W

# cfn-nag (security)
cfn_nag_scan --input-path ./templates/
cfn_nag_scan --input-path ./templates/ --output-path ./reports/

# AWS Security Hub — CFN integration
# Ou Checkov avec --framework cloudformation
checkov -f template.yaml
```

### Azure ARM / Bicep Scanning
```bash
# Bicep linter
bicep build main.bicep --stdout

# Checkov Azure
checkov -f main.bicep
checkov -d ./arm/

# PSRule (Azure)
Install-Module -Name PSRule.Rules.Azure -Force
Invoke-PSRule -Module PSRule.Rules.Azure -InputPath ./arm/
```

### GitLab CI / GitHub Actions Integration
```yaml
# .github/workflows/iac-scan.yml
name: IaC Security Scan
on:
  pull_request:
    paths:
      - 'terraform/**'
      - '**.tf'
jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Checkov
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: results.sarif
      - name: tfsec
        uses: aquasecurity/tfsec-action@v1.0.3
        with:
          working-directory: terraform/
          additional_flags: --config-file .tfsec/config.yml
```

---

## 3. SAST (Static Application Security Testing)

### CodeQL
```bash
# CodeQL CLI
codeql database create --language=python --source-root=./app ./codeql-db
codeql database analyze ./codeql-db --format=sarif --output=results.sarif codeql/python-queries

# GitHub Actions
# codeql-action/analyze@v3
```

### Semgrep
```bash
# Règles de sécurité
semgrep --config=auto ./app/
semgrep --config=p/python ./app/
semgrep --config=r/semgrep:ci ./app/

# Règles custom
semgrep --config=./.semgrep/hardcoded-secrets.yml ./app/

# CI mode
semgrep ci --json --output results.json
```

### SonarQube
```bash
# SonarQube scan
sonar-scanner \
  -Dsonar.projectKey=myapp \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://sonarqube:9000 \
  -Dsonar.login=<token>
```

---

## 4. Secret Scanning

### gitleaks
```bash
# Scan local
gitleaks detect --source . --verbose
gitleaks detect --source . --report-format json --report-path report.json

# Pre-commit hook
cat > .pre-commit-config.yaml << 'EOF'
repos:
- repo: https://github.com/gitleaks/gitleaks
  rev: v8.18.0
  hooks:
  - id: gitleaks
EOF

# CI scan
gitleaks detect --source . --no-git  # for non-git dirs
gitleaks detect --source . --verbose --redact  # masque les secrets dans le log
```

### truffleHog
```bash
# Scan git history
trufflehog git https://github.com/org/repo --only-verified --json

# Filesystem
trufflehog filesystem --directory . --only-verified

# GitHub API (org-wide)
trufflehog github --org=mon-org --token=<gh-token>
```

### detect-secrets
```bash
# Yelp detect-secrets
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
detect-secrets scan --update .secrets.baseline  # update sans perdre l'audit
```

### GitHub Secret Scanning
```bash
# API — lister les alertes
curl -H "Authorization: token <gh-token>" \
  https://api.github.com/repos/org/repo/secret-scanning/alerts

# Patterns détectés:
# AWS Keys, GCP Service Account, Azure Keys
# GitHub Tokens, Slack Tokens, npm tokens
# Private keys (SSH, PGP, etc.)
```

---

## 5. Build Security

### Docker Build
```bash
# BuildKit (sécurité)
DOCKER_BUILDKIT=1 docker build --secret id=aws_creds,src=./aws_creds -t app:latest .

# Pas de secrets dans les layers
# Utiliser --mount=type=secret dans le Dockerfile
RUN --mount=type=secret,id=aws_creds aws sts get-caller-identity
```

### SBOM (Software Bill of Materials)
```bash
# Syft — générer SBOM
syft packages app:latest -o cyclonedx-json > sbom.cdx.json
syft dir:./app -o spdx-json > sbom.spdx.json

# Trivy — SBOM + vulns
trivy image --format cyclonedx --output sbom.json app:latest

# Grype — vulns sur SBOM
grype sbom:sbom.cdx.json

# Dependency-Track (SBOM management)
# API: curl -X PUT "http://dtrack/api/v1/bom" -d @sbom.json
```

### Image Signing (Cosign)
```bash
# Signer
cosign sign --key cosign.key <registry>/app:latest

# Vérifier dans CI
cosign verify --key cosign.pub <registry>/app:latest

# Keyless (OIDC — GitHub Actions)
cosign sign <registry>/app:latest
cosign verify <registry>/app:latest

# Attestation (SLSA)
cosign attest --predicate slsa.json --type https://slsa.dev/provenance/v1 <registry>/app:latest
```

---

## 6. Pipeline Hardening

### GitHub Actions Security
```yaml
# Hardened runners
name: Deploy
on: [push]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:          # Least privilege
      contents: read
      issues: write
      id-token: write    # OIDC
    steps:
    - uses: actions/checkout@v4
    - name: Configure AWS
      uses: aws-actions/configure-aws-credentials@v4
      with:
        role-to-assume: arn:aws:iam::<account>:role/github-actions
        aws-region: us-east-1
    - run: terraform apply -auto-approve

# OIDC — pas de credentials hardcodés
# Vérifier l'audience
```

### GitLab CI Security
```yaml
# GitLab CI — secure variables
variables:
  SECRET: $CI_JOB_TOKEN  # masqué automatiquement

# Protected branches
# Variables protégées sur main uniquement
# Secrets: masked + protected

# Job tokens (CI_JOB_TOKEN)
# Accès limité aux APIs
```

### Prevent Supply Chain Attacks
```bash
# 1. Dependabot / Renovate — auto-update deps
# 2. Package lock verification (npm audit, pip audit)
# 3. Image pinning (digest SHA256, pas :latest)
# 4. Verify Cosign signatures
# 5. SBOM generation + Dependency-Track

# Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker pull alpine:latest  # only signed images

# NPM audit
npm audit --audit-level=high
```

---

## 7. DAST (Dynamic Application Security Testing)

### OWASP ZAP
```bash
# ZAP baseline scan
docker run -t owasp/zap2docker-stable zap-baseline.py \
  -t https://target.com \
  -r report.html

# ZAP API scan (avec auth)
docker run -t owasp/zap2docker-stable zap-api-scan.py \
  -t https://target.com/openapi.json \
  -f openapi \
  -r report.html

# Active scan
docker run -t owasp/zap2docker-stable zap-full-scan.py \
  -t https://target.com \
  -r report.html \
  -x report.xml
```

### Burp Suite (CI)
```bash
# Burp DAST in CI (via REST API)
curl -X POST "https://burp:1337/v0.1/scan" \
  -H "Authorization: Bearer <token>" \
  -d '{"urls":["https://target.com"],"scan_configurations":[{"name":"Crawl and Audit"}]}'
```

---

## 8. Post-Deploy Security Validation

### Prowler (Runtime)
```bash
# AWS post-deploy
prowler aws -g cis_1.5
prowler aws -g serverless

# GCP
prowler gcp -p <project>

# Azure
prowler azure
```

### OPA/Gatekeeper (Admission)
```bash
# Vérifier qu'aucun pod ne peut contourner les policies
kubectl get constrainttemplates
kubectl get constraints
kubectl describe k8spspprivilegedcontainer deny-privileged
```

---

## 9. DevSecOps Toolchain Matrix

| Étape | Outils | Cloud |
|-------|--------|-------|
| **IaC Scan** | Checkov, tfsec, Terrascan, cfn-nag | Multi |
| **SAST** | CodeQL, Semgrep, SonarQube, Snyk | Multi |
| **Secret Scan** | gitleaks, truffleHog, detect-secrets | Multi |
| **Build** | Docker BuildKit, Cosign, Syft | Multi |
| **SBOM** | Syft, Trivy, Dependency-Track | Multi |
| **DAST** | ZAP, Burp, Nikto | Multi |
| **Container** | Trivy, Grype, Clair, Docker Scout | Multi |
| **Deploy** | OPA Gatekeeper, Kyverno | K8s |
| **Post-Deploy** | Prowler, ScoutSuite, CloudSploit | Multi |

## Ressources

- **OWASP DevSecOps**: https://owasp.org/www-project-devsecops-guideline/
- **SLSA Framework**: https://slsa.dev/
- **CNCF Supply Chain Security**: https://www.cncf.io/reports/supply-chain-security/
- **GitHub Security Best Practices**: https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions
- **GitLab Security**: https://docs.gitlab.com/ee/security/
- **Semgrep Registry**: https://semgrep.dev/explore
- **Checkov Policies**: https://www.checkov.io/