---
name: devsecops-pipeline-security
description: Guide complet de sécurisation des pipelines CI/CD — SAST, DAST, SCA, container scanning, secrets detection, et durcissement GitHub Actions/GitLab CI.
domain: [cybersecurite, devops]
tags: [devsecops, ci-cd, pipeline, sast, dast, sca, github-actions, gitlab-ci]
priority: haute
---

# 🔒 DevSecOps — Sécurisation des Pipelines CI/CD

Guide de sécurisation des pipelines CI/CD avec intégration de la sécurité à chaque étape (Shift Left).  
Couvre : SAST, DAST, SCA, container scanning, secret detection, et hardening CI/CD.

---

## 1. Principes DevSecOps

### 1.1 Shift Left — Intégrer la sécurité tôt

```
Code → Build → Test → Deploy → Run
│       │       │       │       │
SAST    SCA     DAST    INFRA   RUNTIME
Trivy   Trivy   Nuclei  Checkov Falco
Semgrep Grype   ZAP     Terrascan  Wazuh
```

### 1.2 Pipeline Sécurisé — Vue d'Ensemble

```yaml
# Étapes obligatoires
stages:
  - lint          # Code quality
  - sast          # Static Analysis
  - sca           # Dependency Check
  - build         # Image build
  - container-scan # Image scan
  - dast          # Dynamic Analysis
  - deploy        # Deploy
  - post-deploy   # Verify + Monitor
```

---

## 2. SAST — Static Application Security Testing

### 2.1 Semgrep

```yaml
# .github/workflows/sast.yml
name: SAST — Semgrep
on:
  push:
    branches: [main]
  pull_request:

jobs:
  semgrep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Semgrep Scan
        uses: semgrep/semgrep-action@v1
        with:
          config: >-
            p/default
            p/python
            p/owasp-top-ten
            p/security-audit
          auditOn: push
          publishToken: ${{ secrets.SEMGREP_TOKEN }}
      
      - name: Generate SARIF
        run: |
          semgrep --sarif --output=semgrep-results.sarif .
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: semgrep-results.sarif
```

### 2.2 CodeQL (GitHub)

```yaml
# .github/workflows/codeql.yml
name: CodeQL Security
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 8 * * 1'

jobs:
  analyze:
    name: CodeQL Analyze
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    
    strategy:
      fail-fast: false
      matrix:
        language: [python, javascript]
    
    steps:
      - uses: actions/checkout@v4
      
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
      
      - uses: github/codeql-action/analyze@v3
```

---

## 3. SCA — Software Composition Analysis

### 3.1 Trivy (Dépendances + Container)

```yaml
# .github/workflows/sca.yml
name: SCA — Trivy
on: [push]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Scan des dépendances
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-fs.sarif'
          severity: 'CRITICAL,HIGH'
      
      - name: Scan du code terraform
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'config'
          scan-ref: 'terraform/'
          format: 'sarif'
          output: 'trivy-config.sarif'
      
      - name: Upload results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-fs.sarif
```

### 3.2 Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"
    assignees:
      - "devops-team"
  
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
  
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

---

## 4. Container Scanning

### 4.1 Build + Scan

```yaml
# .github/workflows/container-scan.yml
name: Container Security
on: [push]

jobs:
  build-and-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build image
        run: docker build -t app:${{ github.sha }} .
      
      - name: Trivy Container Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'app:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-container.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'    # ❌ Block si CVE critique
      
      - name: Grype Scan
        uses: anchore/scan-action@v3
        with:
          image: 'app:${{ github.sha }}'
          fail-build: true
          severity-cutoff: high
      
      - name: Cosign Signature
        run: |
          cosign sign --key cosign.key app:latest
      
      - name: Push
        run: docker push app:${{ github.sha }}
```

### 4.2 Dockerfile Hardening Check

```bash
#!/bin/bash
# check-dockerfile.sh — Vérifications de sécurité Dockerfile

DOCKERFILE="$1"
ERRORS=0

# Vérification 1 : Utilisateur non-root
if grep -q "^USER root\|^FROM.*AS.*" "$DOCKERFILE" 2>/dev/null; then
    if ! grep -q "^USER [0-9]" "$DOCKERFILE" 2>/dev/null && \
       ! grep -q "^USER [a-z]" "$DOCKERFILE" 2>/dev/null; then
        echo "❌ Pas d'utilisateur non-root défini"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Vérification 2 : Pas de COPY --chmod=ugo+w
if grep -q "COPY --chmod=777" "$DOCKERFILE"; then
    echo "❌ COPY avec permissions world-writable"
    ERRORS=$((ERRORS + 1))
fi

# Vérification 3 : Pas de multi-stage ?
if ! grep -q "^FROM.*AS " "$DOCKERFILE"; then
    echo "⚠️ Pas de multi-stage build — image plus grosse"
fi

# Vérification 4 : ADD vs COPY
if grep -q "^ADD " "$DOCKERFILE"; then
    echo "⚠️ Utilisation de ADD au lieu de COPY"
fi

exit $ERRORS
```

---

## 5. DAST — Dynamic Application Security Testing

### 5.1 OWASP ZAP

```yaml
# .github/workflows/dast.yml
name: DAST — OWASP ZAP
on:
  deployment_status:

jobs:
  zap-scan:
    if: github.event.deployment_status.state == 'success'
    runs-on: ubuntu-latest
    steps:
      - name: ZAP Scan
        uses: zaproxy/action-api-scan@v0.7
        with:
          target: 'https://staging.example.com'
          format: 'openapi'
          specification: 'api/swagger.json'
          fail_action: true
      
      - name: ZAP Full Scan
        uses: zaproxy/action-full-scan@v0.10
        with:
          target: 'https://staging.example.com'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a'
```

### 5.2 Nuclei

```yaml
name: DAST — Nuclei
on: [deployment_status]

jobs:
  nuclei:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Nuclei Scan
        uses: projectdiscovery/nuclei-action@main
        with:
          target: 'https://staging.example.com'
          severity: 'critical,high,medium'
      
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: nuclei-report
          path: nuclei-report.json
```

---

## 6. Infrastructure as Code Security

### 6.1 Checkov (Terraform/K8s)

```yaml
name: IaC Security — Checkov
on: [push]

jobs:
  checkov:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Checkov Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: terraform/
          framework: terraform
          output_format: sarif
          output_file_path: checkov.sarif
          soft_fail: false
      
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: checkov.sarif
```

### 6.2 Terrascan

```yaml
name: IaC — Terrascan
on: [push]

jobs:
  terrascan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Terrascan
        uses: tenable/terrascan-action@main
        with:
          iac_type: 'terraform'
          iac_version: 'v14'
          policy_type: 'aws'
          only_warn: false
          non_recursive: false
```

---

## 7. Hardening CI/CD Pipeline

### 7.1 GitHub Actions — Bonnes Pratiques

```yaml
name: Production Deploy
on:
  push:
    tags:
      - 'v*'

# 🔐 Permissions minimales
permissions:
  contents: read
  id-token: write  # Pour OIDC

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    # 🔐 Pas de tiers non vérifié
    # Toujours spécifier le SHA, pas la version tag
    steps:
      - uses: actions/checkout@v4
      
      # 🔐 OIDC au lieu de secrets de longue durée
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: eu-west-1
      
      # 🔐 Jamais d'injection de code via des noms de PR
      - name: Build
        run: |
          docker build -t app .
        env:
          # 🔐 Isoler les variables
          BUILD_SECRET: ${{ secrets.BUILD_SECRET }}
      
      # 🔐 Signer l'image
      - name: Sign
        run: cosign sign app:latest
```

### 7.2 Anti-Patterns à Éviter

| ❌ Mauvais | ✅ Bon |
|-----------|--------|
| `uses: actions/checkout@v3` (version souple) | `uses: actions/checkout@a12f89...` (SHA fixe) |
| `run: echo "${{ github.event.issue.title }}"` (injection) | `run: echo "$TITLE"` (via variable) |
| `uses: some-unverified-action` (tiers non audité) | Vérifier les actions GitHub Verified |
| `GITHUB_TOKEN: write-all` (permissions larges) | Permissions minimales |
| `secrets.DEPLOY_KEY` dans le code | OIDC-based auth |
| Pull Request auto-merge sans revue | Revue manuelle + tests |

---

## 8. Métriques de Sécurité du Pipeline

| Métrique | Cible | Outil |
|----------|-------|-------|
| Temps moyen de détection | < 1h | SIEM |
| Temps moyen de résolution | < 4h | Incident Response |
| Couverture SAST | 100% | Semgrep |
| Couverture SCA | 100% | Trivy |
| CVE critiques non résolues | 0 | Dependabot |
| Secrets détectés avant merge | 100% | GitLeaks |
| Images signées | 100% | Cosign |
| Pipeline audit trail | Oui | Git history |

---

## 9. Secrets Detection in CI/CD

### 9.1 GitLeaks GitHub Action

```yaml
name: Secrets Detection
on: [pull_request]

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: GitLeaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### 9.2 TruffleHog

```yaml
name: TruffleHog Secrets
on: [pull_request]

jobs:
  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: TruffleHog
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

---

## 10. Compliance et SLSA

### 10.1 SLSA (Supply-chain Levels for Software Artifacts)

| Niveau | Exigences | Actions |
|--------|-----------|---------|
| SLSA 1 | Documentation | Le pipeline existe et est documenté |
| SLSA 2 | Build hermétique | Build isolé, provenance signée |
| SLSA 3 | Build non falsifiable | Build reproductible, matériel dédié |
| SLSA 4 | Build + dépendances | Dép. vérifiées, audit complet |

### 10.2 SBOM (Software Bill of Materials)

```yaml
name: Generate SBOM
on: [push]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate SPDX SBOM
        uses: anchore/sbom-action@v0
        with:
          format: 'spdx-json'
          output-file: 'sbom.spdx.json'
      
      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.spdx.json
      
      - name: Sign SBOM
        run: |
          cosign sign-blob --key cosign.key sbom.spdx.json > sbom.spdx.json.sig
```

---

## Pitfalls

- **NE JAMAIS** utiliser `pull_request_target` sans vérification des chemins — exécution dans le contexte de la branche cible
- **NE JAMAIS** exécuter du code non audité dans les workflows CI/CD
- **TOUJOURS** spécifier les SHA des actions GitHub, pas les tags flottants
- **TOUJOURS** utiliser les permissions minimales pour GITHUB_TOKEN
- **TOUJOURS** scanner les images AVANT de les pousser vers le registry
- Ne pas oublier de scanner aussi les images de base (FROM)
- Désactiver les actions inutilisées et les workflows non maintenus
- Audit régulier des tokens CI/CD (90 jours max)