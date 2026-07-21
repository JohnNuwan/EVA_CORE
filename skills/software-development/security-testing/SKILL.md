---
name: security-testing
description: "Tests de sécurité automatisés — SAST, DAST, SCA, dependency scanning, ZAP, Nuclei, Trivy, secret detection, et intégration CI/CD DevSecOps."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [security-testing, sast, dast, sca, devsecops, zap, nuclei, trivy, pentest]
    related_skills: [integration-testing, e2e-testing, performance-testing]
---

# Tests de Sécurité — SAST, DAST, SCA et DevSecOps

## Overview

Les tests de sécurité automatisés s'intègrent dans le pipeline CI/CD pour détecter les vulnérabilités tôt dans le cycle de développement (Shift Left). Quatre grandes catégories : **SAST** (statique), **DAST** (dynamique), **SCA** (dépendances), **Secret Detection**.

## When to Use

- **Shift Left** — détecter les failles avant le merge, pas après la mise en prod
- **DevSecOps** — gate de sécurité obligatoire dans le pipeline CI/CD
- **Audit de sécurité** — analyse complète avant release
- **OWASP Top 10** — couvrir les classes de vulnérabilités web les plus critiques
- Ne pas utiliser pour : remplacer un audit de sécurité manuel complet (complémentaire)

## Chaîne d'Outils de Sécurité

```
Code (repo)                Build                      Prod

  SAST ──────────→  SCA ──────────→  Secret ──────→  DAST
  Semgrep           Trivy / Dependabot  Gitleaks /       ZAP / Nuclei
  SonarQube         Grype / Snyk        TruffleHog
  CodeQL
```

## 1. SAST — Analyse Statique de Code

### Semgrep

```bash
# Installation
pip install semgrep

# Lancer sur un projet
semgrep scan --config=auto --config=p/r2c-ci .
semgrep scan --config=auto --output=semgrep-report.sarif

# Règles personnalisées
semgrep scan --config=rules/my-rules.yaml

# Règles OWASP
semgrep scan --config=p/owasp-top-ten

# CI-friendly (code non-zero en cas de trouvaille)
semgrep scan --config=auto --error .
```

**Exemple de règle personnalisée :**
```yaml
# rules/security/no-sql-injection.yaml
rules:
  - id: python-sql-injection
    patterns:
      - pattern: |
          cursor.execute(f"...{...}...")
      - pattern-not: |
          cursor.execute(..., (...,))
    message: "❌ SQL Injection détectée : ne pas utiliser f-strings dans execute()"
    languages: [python]
    severity: ERROR
    metadata:
      cwe: "CWE-89"
      owasp: "A1: Injection"
```

### CodeQL (GitHub)

```yaml
# .github/workflows/codeql.yml
name: CodeQL
on: [push, pull_request]
jobs:
  analyze:
    runs-on: ubuntu-latest
    language: [python, javascript, java]
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: ${{ matrix.language }}
          queries: security-and-quality
      - uses: github/codeql-action/analyze@v3
```

### SonarQube / SonarCloud

```bash
# Local
sonar-scanner \
  -Dsonar.projectKey=myproject \
  -Dsonar.sources=. \
  -Dsonar.host.url=http://localhost:9000 \
  -Dsonar.login=$SONAR_TOKEN

# GitHub Actions — intégré
sonarcloud.github.action
```

## 2. SCA — Analyse des Dépendances

### Trivy

```bash
# Installation
sudo apt install trivy
# ou
docker pull aquasec/trivy

# Scanner le système de fichiers
trivy fs . --severity CRITICAL,HIGH

# Scanner une image Docker
trivy image myapp:latest --severity CRITICAL,HIGH

# Scanner le SBOM
trivy fs --format cyclonedx --output sbom.json .

# En mode CI
trivy fs --exit-code 1 --severity CRITICAL,HIGH .
```

```yaml
# .github/workflows/trivy.yml
name: Trivy SCA
on: [push]
jobs:
  trivy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
      - name: Upload SARIF
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

### Grype

```bash
# Installation
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Analyse
grype . --fail-on high

# SBOM
syft . -o json > sbom.json
grype sbom:sbom.json
```

### Dependabot (GitHub natif)

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: 'pip'
    directory: '/'
    schedule:
      interval: 'weekly'
      day: 'monday'
    open-pull-requests-limit: 10
    labels:
      - 'dependencies'
      - 'security'
  - package-ecosystem: 'npm'
    directory: '/'
    schedule:
      interval: 'weekly'
```

## 3. Secret Detection

### Gitleaks

```bash
# Installation
brew install gitleaks
# ou
docker pull zricethezav/gitleaks

# Détection de secrets dans le repo
gitleaks detect --source . --verbose

# En mode CI
gitleaks detect --source . --report-path gitleaks-report.json --exit-code 1

# Scan les commits passés
gitleaks detect --source . --log-opts="--all"
```

```yaml
# .github/workflows/gitleaks.yml
name: Secret Detection
on: [push, pull_request]
jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### TruffleHog

```bash
# Installation
pip install trufflehog

# Scan du repo
trufflehog git https://github.com/user/repo --only-verified

# Scan de fichiers
trufflehog filesystem . --only-verified

# Scan Docker
trufflehog docker myimage:latest --only-verified
```

## 4. DAST — Analyse Dynamique (OWASP ZAP)

### Installation et Scan de Base

```bash
# Docker
docker pull ghcr.io/zaproxy/zaproxy:stable

# Scan passif (sans attaque)
docker run -v $(pwd):/zap/wrk/:rw -t \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t https://target.com \
  -r report.html

# Scan actif (avec attaques)
docker run -v $(pwd):/zap/wrk/:rw -t \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t https://target.com/api/openapi.json \
  -f openapi -r report.html

# Avec authentification
docker run -v $(pwd):/zap/wrk/:rw -t \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t https://target.com \
  -r report.html \
  --hook=/zap/wrk/auth_hook.py
```

### Context et Authentification (ZAP)

```python
# auth_hook.py
def zap_started(zap, target):
    """Prépare le contexte d'authentification pour ZAP."""

    # Configurer le context
    context_id = zap.context.new_context('myapp')
    zap.context.include_in_context(context_id, 'https://target.com/.*')

    # Login via POST form
    session_id = zap.replacer.add_rule(
        description='Auth session',
        match_type='REQ_HEADER',
        match_string='Authorization',
        replacement='Bearer mock-token',
    )

    # Ajouter l'utilisateur
    user_id = zap.users.new_user(context_id, 'testuser')
    zap.users.set_authentication_credentials(
        context_id, user_id,
        {'username': 'admin@test.com', 'password': 'test123'}
    )
    zap.users.set_user_enabled(context_id, user_id, True)
```

## 5. Nuclei — Scan de Vulnérabilités Automatisé

```bash
# Installation
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
# ou
brew install nuclei

# Scan d'une cible
nuclei -u https://target.com

# Templates spécifiques
nuclei -u https://target.com -t cves/ -t exposures/

# Scan OWASP Top 10
nuclei -u https://target.com -t ~/nuclei-templates/http/misconfiguration/

# Export
nuclei -u https://target.com -o nuclei-report.json -json
```

```yaml
# .github/workflows/nuclei.yml
name: Nuclei DAST
on:
  schedule:
    - cron: '0 8 * * 1'  # Chaque lundi
jobs:
  nuclei:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Nuclei
        uses: projectdiscovery/nuclei-action@main
        with:
          target: https://staging.example.com
          templates: cves,misconfiguration
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: nuclei-report
          path: nuclei-report.json
```

## Pipelines DevSecOps Complets

### CI/CD — Multi-Étapes

```yaml
name: DevSecOps Pipeline
on: [push, pull_request]
jobs:
  security-checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }

      # 1. SAST
      - name: Semgrep SAST
        uses: semgrep/semgrep-action@v1
        with:
          config: auto

      # 2. Secret Detection
      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2

      # 3. SCA
      - name: Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          severity: CRITICAL,HIGH

      # 4. Container Scan
      - name: Trivy Image
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: image
          scan-ref: myapp:latest
          severity: CRITICAL,HIGH
```

## Ce que Chaque Outil Détecte

| Outil | Classe | Détecte |
|-------|--------|---------|
| **Semgrep/CodeQL** | SAST | Injections, XSS, path traversal, hardcoded secrets, mauvaises pratiques crypto |
| **Trivy/Grype** | SCA | CVE dans les dépendances, packages obsolètes, licenses |
| **Gitleaks/TruffleHog** | Secrets | API keys, tokens, mots de passe, clés SSH committés |
| **ZAP** | DAST | XSS, SQLi, CSRF, mauvaises configs headers, cookie flaws |
| **Nuclei** | DAST | CVEs connues, misconfigurations cloud, expositions |
| **Dependabot/Renovate** | SCA | Alertes et PRs automatiques pour dépendances vulnérables |

## OWASP Top 10 — Couverture par Outil

| # | Vulnérabilité | SAST | DAST | SCA |
|---|--------------|------|------|-----|
| A1 | Injection (SQL, NoSQL, OS) | ✅ Semgrep/CodeQL | ✅ ZAP | ❌ |
| A2 | Broken Authentication | ⚠️ Partiel | ✅ ZAP | ❌ |
| A3 | Sensitive Data Exposure | ⚠️ Partiel | ✅ ZAP/Nuclei | ❌ |
| A4 | XXE (XML External Entities) | ✅ Semgrep | ✅ ZAP | ❌ |
| A5 | Broken Access Control | ⚠️ Partiel | ✅ ZAP/Nuclei | ❌ |
| A6 | Security Misconfiguration | ❌ | ✅ Nuclei/ZAP | ❌ |
| A7 | XSS (Cross-Site Scripting) | ✅ Semgrep/CodeQL | ✅ ZAP | ❌ |
| A8 | Insecure Deserialization | ✅ Semgrep | ✅ ZAP | ⚠️ (lib vulnérables) |
| A9 | Known Vulnerabilities | ❌ | ❌ | ✅ Trivy/Grype |
| A10 | Logging & Monitoring | ❌ | ❌ | ❌ (ops) |

## Bonnes Pratiques

1. **Shift Left** — plus tôt on détecte, moins cher à corriger
2. **Faux positifs** — configurer des ignores documentés, ne pas tout bloquer
3. **Gate progressif** — bloquer CRITICAL/HIGH en CI, warnings pour MEDIUM
4. **Scan régulier** — pas seulement au commit mais aussi en cron (CVE découvertes après)
5. **SBOM** — générer le Software Bill of Materials pour chaque release
6. **Ne pas confondre scan et audit** — l'automatisation ne remplace pas un test d'intrusion manuel

## Common Pitfalls

1. **Trop de faux positifs** — temps perdu à trier, risque d'ignorer les vrais alertes
2. **Bloquer tout** — 100% des PR sont bloqués, les devs contournent la sécurité
3. **Pas de SBOM** — impossible de savoir quelles dépendances sont vulnérables après build
4. **Scanner sans authentification** — ZAP/nuclei voient la page de login seulement
5. **Dépendances non scannées** — package.json seul ne suffit pas (scanner le lockfile)
6. **Scanner trop tard** — attendre le déploiement pour DAST au lieu de le faire en staging

## Verification Checklist

- [ ] SAST (Semgrep/CodeQL) exécuté à chaque PR
- [ ] Secret detection (Gitleaks) — aucun token commité
- [ ] SCA (Trivy/Grype) — pas de CVE CRITICAL/HIGH non résolue
- [ ] DAST (ZAP) exécuté sur l'environnement staging
- [ ] Nuclei scan régulier sur staging/preprod
- [ ] Seuils de sécurité définis dans le CI (exit code non-zero si CRITICAL)
- [ ] SBOM généré et archivé pour chaque release
- [ ] Les alertes ont un propriétaire et un SLA de résolution
