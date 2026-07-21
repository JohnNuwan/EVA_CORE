---
name: devsecops-pipelines
description: "Sécurité des pipelines DevOps — SAST, DAST, SCA, secret scanning, signature d'images, SBOM, CI/CD security gates, runtime security, bonnes pratiques DevSecOps"
version: 1.0.0
author: EVA
license: Privée EVA
category: mlops
metadata:
  EVA:
    tags: [devsecops, sécurité, sast, dast, sca, snyk, trivy, sbom, cosign, secret-scanning, pipelines]
    related_skills: [ci-cd-pipelines, docker-avance, kubernetes-avance, gitops-argocd]
---

# DevSecOps — Sécurité des Pipelines

## Vue d'ensemble

DevSecOps intègre la sécurité à chaque étape du cycle DevOps — pas à la fin. Cette compétence couvre l'analyse statique (SAST), l'analyse dynamique (DAST), l'analyse de composition logicielle (SCA), la détection de secrets, la signature d'images (Cosign), les SBOM, les security gates dans les pipelines CI/CD, et les bonnes pratiques de runtime security.

## Quand l'utiliser

- Ajouter des checks de sécurité automatiques dans le pipeline CI/CD
- Détecter les vulnérabilités dans les dépendances (SCA)
- Scanner les secrets exposés dans le code
- Signer et vérifier les images Docker
- Générer des SBOM (Software Bill of Materials)
- Bloquer un déploiement si une vulnérabilité critique est détectée
- Auditer la conformité CIS/DISA des images et clusters

---

## 1. Architecture DevSecOps (Shift Left)

```
Code (IDE) → Commit → PR → CI Pipeline → Registry → CD → Runtime
    │          │       │        │            │        │      │
    ▼          ▼       ▼        ▼            ▼        ▼      ▼
 pre-commit  secret   SAST    SCA+SAST     SBOM+    image   runtime
 hooks       scan     +lint   +build       sign     verify  scan
```

---

## 2. SAST — Analyse Statique

### GitHub Actions

```yaml
name: DevSecOps Pipeline

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  sast:
    name: Static Analysis
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Semgrep SAST
        uses: semgrep/semgrep-action@v1
        with:
          config: |
            p/default
            p/python
            p/owasp-top-ten
          severity: ERROR,WARNING

      - name: Bandit (Python security)
        run: |
          pip install bandit
          bandit -r app/ -f json -o bandit-report.json

      - name: CodeQL Analysis
        uses: github/codeql-action/analyze@v3
        with:
          languages: python, javascript
          queries: security-extended,security-and-quality

      - name: Upload SARIF results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: bandit-report.json
```

### Semgrep Rules (exemple)

```yaml
# .semgrep/rules/python-security.yaml
rules:
  - id: avoid-hardcoded-passwords
    patterns:
      - pattern: |
          $PASSWORD = "..."
      - metavariable-regex:
          metavariable: $PASSWORD
          regex: (password|secret|token|api_key)
    message: "Mot de passe ou secret codé en dur détecté"
    severity: ERROR
    languages: [python]

  - id: avoid-sql-injection
    pattern: |
      cursor.execute(f"...{...}...")
    message: "SQL injection possible — utiliser des paramètres nommés"
    severity: ERROR
    languages: [python]
```

---

## 3. Secret Scanning

```yaml
# Gitleaks + TruffleHog
jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: TruffleHog
        run: |
          docker run --rm -v $(pwd):/repo trufflesecurity/trufflehog:latest \
            filesystem /repo --only-verified --json > trufflehog-report.json
        continue-on-error: true

      - name: Block if secrets found
        run: |
          if [ -s trufflehog-report.json ]; then
            echo "⚠️ Secrets détectés ! Vérifier le rapport."
            exit 1
          fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
      - id: check-added-large-files
      - id: end-of-file-fixer

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18
    hooks:
      - id: gitleaks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

---

## 4. SCA — Analyse de Composition Logicielle

```yaml
jobs:
  sca:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Trivy (SCA + filesystem)
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'
          exit-code: 1   # Bloque si critique ou high

      - name: Snyk (dépendances)
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          command: monitor
          args: --severity-threshold=high

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: trivy-results.sarif

      - name: Python dependency audit
        run: |
          pip install pip-audit
          pip-audit --desc on --severity critical --fix
```

---

## 5. Image Docker — Build Sécurisé

```yaml
jobs:
  secure-image:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # Pour Cosign
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3

      - name: Build and sign
        uses: docker/build-push-action@v6
        id: build
        with:
          push: true
          tags: registry.eva.local/api:${{ github.sha }}

      - name: Scan image
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'image'
          image-ref: 'registry.eva.local/api:${{ github.sha }}'
          format: 'sarif'
          output: 'trivy-image.sarif'
          severity: 'CRITICAL'
          exit-code: 1  # Bloque si CVE critique

      - name: Generate SBOM
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'sbom'
          image-ref: 'registry.eva.local/api:${{ github.sha }}'
          format: 'spdx-json'
          output: 'sbom.spdx.json'

      - name: Sign image with Cosign
        env:
          COSIGN_PRIVATE_KEY: ${{ secrets.COSIGN_PRIVATE_KEY }}
          COSIGN_PASSWORD: ${{ secrets.COSIGN_PASSWORD }}
        run: |
          cosign sign --key env://COSIGN_PRIVATE_KEY \
            registry.eva.local/api:${{ github.sha }}

      - name: Verify attestation
        run: |
          cosign verify --key env://COSIGN_PUBLIC_KEY \
            registry.eva.local/api:${{ github.sha }}
```

---

## 6. DAST — Analyse Dynamique

```yaml
jobs:
  dast:
    runs-on: ubuntu-latest
    steps:
      - name: Start target app
        run: |
          docker compose -f docker-compose.test.yml up -d
          sleep 10

      - name: OWASP ZAP DAST Scan
        uses: zaproxy/action-full-scan@v0.11
        with:
          target: 'http://localhost:8000'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a -j'
          allow_issue_writing: false
          fail_action: true

      - name: Generate HTML report
        run: |
          curl -s http://localhost:8000/report > zap-report.html

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: zap-report
          path: zap-report.html
```

---

## 7. Runtime Security (Kubernetes)

```yaml
# Falco — détection d'anomalies runtime
# Installé via Helm
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm upgrade --install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set falco.driver.kind=modern_ebpf \
  --set falco.rules.http_output.enabled=true \
  --set falco.rules.http_output.url=http://alertmanager:9093/api/v1/alerts

# Exemple de règle Falco
# /etc/falco/rules.d/custom.yaml
- rule: Shell in Container
  desc: Shell interactif détecté dans un conteneur
  condition: >
    spawned_process and container and
    (proc.name = "bash" or proc.name = "sh" or proc.name = "zsh")
  output: "Shell in container (user=%user.name, container=%container.name)"
  priority: WARNING
  tags: [container, shell]
```

### Pod Security Standards

```yaml
# Namespace labels (PSS)
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### OPA Gatekeeper (admission control)

```yaml
# Interdire les images avec tag latest
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sDisallowedTags
metadata:
  name: block-latest-tag
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    tags: ["latest"]
    message: "L'image ne doit pas utiliser le tag 'latest'"
```

---

## 8. Signature et Attestation

```bash
# Générer une paire de clés Cosign
cosign generate-key-pair

# Signer une image
cosign sign --key cosign.key registry.eva.local/api:1.2.3

# Vérifier
cosign verify --key cosign.pub registry.eva.local/api:1.2.3

# Attestation SLSA
cosign attest --predicate slsa-provenance.json \
  --key cosign.key registry.eva.local/api:1.2.3

# Vérifier l'attestation
cosign verify-attestation --key cosign.pub \
  --type slsaprovenance registry.eva.local/api:1.2.3
```

---

## 9. Intégration Security Gates

```yaml
# Politique de gate centralisée
# blocked.yaml
gates:
  - name: critical-vulnerabilities
    description: "Pas de CVEs critiques dans l'image"
    tool: trivy
    condition: ${TRIVY_CRITICAL} == 0

  - name: hardcoded-secrets
    description: "Pas de secrets en clair dans le code"
    tool: gitleaks
    condition: ${GITLEAKS_FINDINGS} == 0

  - name: sbom-generated
    description: "SBOM présent et signé"
    condition: ${SBOM_DIGEST} != ""
```

---

## 10. Pièges Courants

1. **Faux positifs ignorés :** SAST produit des faux positifs. Configurer des `.semgrepignore` et des annotations de suppression documentées.
2. **Scan trop tardif :** Scanner la sécurité après le build, c'est trop tard. Intégrer le scan dès le commit (pre-commit).
3. **Secrets dans les logs CI :** Un secret leaké dans les logs GitHub Actions est visible pour toujours. Masquer avec `::add-mask::`.
4. **Image signée mais pas vérifiée au runtime :** Cosign signe l'image, mais si le cluster n'a pas de webhook de vérification (Ratify, Connaisseur), la signature ne sert à rien.
5. **Politique trop stricte :** Bloquer TOUS les builds pour une CVE low dans une dépendance de test. Nuancer par sévérité et exploitabilité.
6. **SBOM oublié :** Un SBOM n'est utile que s'il est stocké et mis à jour. L'uploader dans le registry aux côtés de l'image.

---

## 11. Checklist Production

- [ ] Pre-commit hooks installés (gitleaks, detect-secrets, ruff)
- [ ] SAST (Semgrep/CodeQL) dans le pipeline CI, bloque sur ERROR
- [ ] Secret scanning (Gitleaks/TruffleHog) dans le CI
- [ ] SCA (Trivy/Snyk/DependencyCheck) bloque sur CRITICAL
- [ ] Image Docker scannée avant push au registry
- [ ] SBOM (SPDX/CycloneDX) généré et stocké
- [ ] Image signée avec Cosign (clé privée dans GitHub Secrets)
- [ ] DAST (OWASP ZAP) sur l'environnement de staging
- [ ] Falco installé sur le cluster pour la runtime security
- [ ] Pod Security Standards (baseline/restricted) appliqués
- [ ] OPA/Gatekeeper bloque les violations de politique
- [ ] Vérification de signature à l'admission (Ratify/Connaisseur)
- [ ] Dashboard de sécurité (Dependabot + GitHub Security tab)