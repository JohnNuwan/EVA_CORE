---
name: api-automation-pipeline
description: Guide complet d'automatisation de pentest API — pipelines CI/CD, nuclei templates, custom scanners, Burp automation, Postman-to-Burp workflows, rapport génération, monitoring continu, et workflows intégrés
category: cybersecurite
---

# API Automation Pipeline — Guide Avancé

## Introduction

L'automatisation est clé pour tester les API en continu : intégration CI/CD, templates reproductibles, scripts custom, et génération de rapports. Ce skill couvre la construction d'un pipeline complet de sécurité API.

## 1. Nuclei — Templates API

### 1.1 Template Basique

```yaml
# nuclei-api-health.yaml
id: api-healthcheck
info:
  name: API Health Check
  severity: info
  tags: api,info

http:
  - method: GET
    path:
      - "{{BaseURL}}/health"
      - "{{BaseURL}}/healthz"
      - "{{BaseURL}}/status"
      - "{{BaseURL}}/api/v1/health"
    matchers:
      - type: word
        words:
          - "ok"
          - "healthy"
          - "alive"
        condition: or
```

### 1.2 Template BOLA/IDOR

```yaml
# nuclei-api-bola.yaml
id: api-bola-check
info:
  name: API BOLA Check
  severity: high
  tags: api,bola,idor

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/v1/users/1"
      - "{{BaseURL}}/api/v1/users/2"
      - "{{BaseURL}}/api/v1/users/3"
      - "{{BaseURL}}/api/v1/users/admin"
    headers:
      Authorization: "Bearer {{token}}"
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: word
        words:
          - "email"
          - "role"
          - "admin"
        condition: or
```

### 1.3 Template Mass Assignment

```yaml
# nuclei-api-mass-assignment.yaml
id: api-mass-assignment
info:
  name: API Mass Assignment Check
  severity: high
  tags: api,mass-assignment

http:
  - method: POST
    path:
      - "{{BaseURL}}/api/v1/users/signup"
      - "{{BaseURL}}/api/v1/auth/signup"
    headers:
      Content-Type: application/json
    body: '{"username":"test{{randstr}}","password":"test123","isAdmin":true,"role":"admin"}'
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
          - 201
      - type: word
        words:
          - "isAdmin"
          - "admin"
          - "role"
```

### 1.4 Template Shadow API

```yaml
# nuclei-api-shadow.yaml
id: api-shadow-discovery
info:
  name: API Shadow Endpoint Discovery
  severity: medium
  tags: api,shadow

http:
  - method: GET
    path:
      - "{{BaseURL}}/swagger.json"
      - "{{BaseURL}}/openapi.json"
      - "{{BaseURL}}/api-docs"
      - "{{BaseURL}}/graphql"
      - "{{BaseURL}}/v2/api-docs"
      - "{{BaseURL}}/api/v2/users"
      - "{{BaseURL}}/api/v3/users"
      - "{{BaseURL}}/admin"
      - "{{BaseURL}}/debug"
      - "{{BaseURL}}/internal"
    matchers:
      - type: status
        status:
          - 200
          - 401
          - 403
```

### 1.5 Template avec Extraction

```yaml
# nuclei-api-secrets.yaml
id: api-secret-leak
info:
  name: API Secret Leak Response
  severity: critical
  tags: api,secrets

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/v1/config"
      - "{{BaseURL}}/api/v1/env"
      - "{{BaseURL}}/.env"
      - "{{BaseURL}}/debug"
    extractors:
      - type: regex
        regex:
          - "(?:ASIA|AKIA)[A-Z0-9]{16}"
          - "ghp_[a-zA-Z0-9]{36}"
          - "sk-[a-zA-Z0-9]{32,}"
          - "xox[baprs]-[a-zA-Z0-9-]{10,}"
```

## 2. Pipeline CI/CD Complet

### 2.1 GitHub Actions

```yaml
# .github/workflows/api-pentest.yml
name: API Security Scan
on:
  schedule:
    - cron: '0 6 * * 1'  # Chaque lundi à 6h
  workflow_dispatch:  # Déclenchement manuel

jobs:
  api-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install tools
        run: |
          go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
          go install github.com/ffuf/ffuf/v2@latest
          pip install requests httpx

      - name: Nuclei API scan
        run: |
          nuclei -u ${{ secrets.API_URL }} \
            -t nuclei-templates/api/ \
            -H "Authorization: Bearer ${{ secrets.API_TOKEN }}" \
            -severity critical,high,medium \
            -o api_vulns.txt \
            -json -silent

      - name: Rate limit test
        run: |
          python3 scripts/test_rate_limit.py \
            --url ${{ secrets.API_URL }} \
            --token ${{ secrets.API_TOKEN }}

      - name: Generate report
        run: |
          python3 scripts/generate_report.py \
            --input api_vulns.txt \
            --output report.html

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: api-security-report
          path: report.html

      - name: Notify
        if: failure()
        run: |
          curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
            -d '{"text":"⚠️ API Security Scan failed on ${{ github.repository }}"}'
```

### 2.2 GitLab CI

```yaml
# .gitlab-ci.yml
api-security:
  stage: security
  image: kalilinux/kali-rolling
  script:
    - apt-get update && apt-get install -y nuclei ffuf python3-pip
    - pip3 install requests
    - nuclei -u $API_URL -t nuclei-templates/api/ \
      -H "Authorization: Bearer $API_TOKEN" -severity critical,high
    - ffuf -u $API_URL/api/v1/users/FUZZ -w ids.txt -fc 404
  artifacts:
    paths:
      - nuclei_report.json
  only:
    - schedules
```

## 3. Scripts d'Automatisation

### 3.1 Scan Complet Multi-Outil

```python
#!/usr/bin/env python3
"""Pipeline de scan API automatisé complet."""
import subprocess
import json
import os
import argparse
from datetime import datetime

class APIScanner:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.results = {"critical": [], "high": [], "medium": [], "low": [], "info": []}

    def nuclei_scan(self):
        """Scan Nuclei avec templates API."""
        print("[*] Nuclei scan...")
        cmd = [
            "nuclei", "-u", self.base_url,
            "-t", "nuclei-templates/api/",
            "-H", f"Authorization: Bearer {self.token}",
            "-json", "-silent", "-severity", "critical,high,medium"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    vuln = json.loads(line)
                    severity = vuln.get('info', {}).get('severity', 'info')
                    self.results[severity].append(vuln)
                except:
                    pass
        print(f"  → {len(self.results['critical'])} critical, {len(self.results['high'])} high")

    def ffuf_scan(self):
        """Fuzzing d'endpoints API."""
        print("[*] ffuf scan...")
        cmd = [
            "ffuf", "-u", f"{self.base_url}/api/v1/users/FUZZ",
            "-w", "wordlists/ids.txt",
            "-H", f"Authorization: Bearer {self.token}",
            "-fc", "404,403", "-o", "/tmp/ffuf_results.json", "-of", "json", "-silent"
        ]
        subprocess.run(cmd, timeout=120)

    def check_shadow_endpoints(self):
        """Test des endpoints shadow courants."""
        endpoints = [
            "/swagger.json", "/openapi.json", "/api-docs",
            "/graphql", "/.env", "/debug", "/admin",
            "/api/v1/users", "/api/v2/users", "/api/v3/users",
            "/internal", "/health", "/metrics",
        ]
        import requests
        for ep in endpoints:
            try:
                r = requests.get(self.base_url + ep, timeout=5,
                    headers={"Authorization": f"Bearer {self.token}"})
                if r.status_code not in [404, 000]:
                    print(f"  [SHADOW] {ep} → {r.status_code}")
            except:
                pass

    def generate_report(self):
        """Génère un rapport HTML."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        html = f"""
        <!DOCTYPE html>
        <html><head><title>API Security Report - {now}</title>
        <style>
        body {{ font-family: monospace; margin: 20px; background: #0d1117; color: #c9d1d9; }}
        h1 {{ color: #58a6ff; }}
        .critical {{ color: #f85149; }} .high {{ color: #d29922; }}
        .medium {{ color: #58a6ff; }} .low {{ color: #8b949e; }}
        table {{ border-collapse: collapse; width: 100%; }}
        td, th {{ border: 1px solid #30363d; padding: 8px; }}
        </style></head><body>
        <h1>🔐 API Security Scan Report</h1>
        <p>Date: {now}</p>
        <p>Target: {self.base_url}</p>
        <h2>Résumé</h2>
        <ul>
            <li>Critical: {len(self.results['critical'])}</li>
            <li>High: {len(self.results['high'])}</li>
            <li>Medium: {len(self.results['medium'])}</li>
        </ul>
        <h2>Vulnérabilités</h2>
        <table>
        <tr><th>Severity</th><th>Name</th><th>Extract</th></tr>
        """
        for sev in ['critical', 'high', 'medium']:
            for v in self.results[sev]:
                info = v.get('info', {})
                html += f"<tr><td class='{sev}'>{sev}</td>"
                html += f"<td>{info.get('name', '')}</td>"
                html += f"<td>{json.dumps(v.get('extracted-results', {}))[:100]}</td></tr>"
        html += "</table></body></html>"

        os.makedirs("reports", exist_ok=True)
        path = f"reports/api_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(path, 'w') as f:
            f.write(html)
        print(f"\n[+] Rapport généré: {path}")
        return path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    scanner = APIScanner(args.url, args.token)
    scanner.nuclei_scan()
    scanner.ffuf_scan()
    scanner.check_shadow_endpoints()
    scanner.generate_report()
```

### 3.2 Postman Collection Automation

```bash
# Exporter les collections Postman en JSON
# Utiliser Newman pour exécuter les tests
npm install -g newman

# Exécuter la collection avec des variables
newman run api-tests.postman_collection.json \
  --env-var "base_url=https://api.target.com" \
  --env-var "token=Bearer <token>" \
  --reporters cli,json \
  --reporter-json-export newman_report.json

# Avec test de sécurité
newman run api-security.postman_collection.json \
  --env-var "base_url=https://api.target.com" \
  --timeout-request 5000 \
  --delay-request 100 \
  --bail
```

### 3.3 Burp Automation (Headless)

```bash
# Dastardly — Burp headless pour CI/CD
# Docker
docker run --rm -v $(pwd):/output \
  public.ecr.aws/portswigger/dastardly:latest \
  https://api.target.com

# Burp REST API
# Installer Burp, activer l'API REST
curl -X POST http://127.0.0.1:1337/v0.1/scan \
  -H "Content-Type: application/json" \
  -d '{
    "urls": ["https://api.target.com"],
    "name": "API Scan",
    "scope": {"include": [{"rule": "https://api.target.com/*"}]}
  }'

# Récupérer les résultats
curl http://127.0.0.1:1337/v0.1/scan/<scan_id>
```

## 4. Continuous Monitoring

### 4.1 Cron Job de Scan

```bash
# Scan quotidien avec cron
0 6 * * * cd /opt/api-scanner && python3 scan.py --url https://api.target.com --token $TOKEN

# Avec notification
0 6 * * * cd /opt/api-scanner && python3 scan.py --url https://api.target.com --token $TOKEN \
  && python3 notify.py
```

### 4.2 Webhook-Based Monitoring

```python
#!/usr/bin/env python3
"""Moniteur API continu via webhook."""
import requests
import hashlib
import json
from time import sleep

BASE = "https://api.target.com"
TOKEN = "Bearer <token>"

# Snapshot de référence
known_endpoints = set()

def discover_endpoints():
    """Découvre les endpoints API courants."""
    endpoints = [
        "/api/v1/users/1",
        "/api/v1/products/1",
        "/api/v1/orders/1",
        "/api/v1/health",
        "/api/v1/admin/users",
        "/openapi.json",
        "/swagger.json",
    ]
    for ep in endpoints:
        try:
            r = requests.get(BASE + ep, headers={"Authorization": TOKEN}, timeout=5)
            if r.status_code != 404:
                known_endpoints.add(ep)
                # Vérifier si la réponse a changé
                content_hash = hashlib.md5(r.text.encode()).hexdigest()
                print(f"[INFO] {ep}: {r.status_code} | hash={content_hash[:8]}")
        except:
            pass

def check_changes():
    """Vérifie si un nouveau endpoint apparaît."""
    new_endpoints = ["/api/v4/users/1", "/internal/v2/admin", "/api/v2/users/1"]
    for ep in new_endpoints:
        try:
            r = requests.get(BASE + ep, headers={"Authorization": TOKEN}, timeout=5)
            if r.status_code != 404 and ep not in known_endpoints:
                print(f"[NEW SHADOW API] {ep} → {r.status_code}")
                # Alerter
                requests.post("https://hooks.slack.com/services/...",
                    json={"text": f"Nouveau endpoint shadow: {ep}"})
        except:
            pass

if __name__ == "__main__":
    while True:
        discover_endpoints()
        check_changes()
        sleep(3600)  # Toutes les heures
```

## 5. Résumé des Outils par Phase

| Phase | Outil | Usage |
|-------|-------|-------|
| **Recon** | nuclei, katana, waybackpy | Découverte endpoints |
| **Fuzzing** | ffuf, arjun, wfuzz | Paramètres, valeurs |
| **Auth** | jwt_tool, Autorize | BOLA, JWT, ACL |
| **Injection** | sqlmap, graphqlmap | SQL, NoSQL, injection |
| **Automation** | newman, dastardly | Postman, Burp headless |
| **CI/CD** | GitHub Actions, GitLab CI | Scan automatisé |
| **Report** | nuclei -json, custom scripts | Génération rapports |

## Checklist

- [ ] Nuclei templates API personnalisés
- [ ] GitHub Actions / GitLab CI pipeline
- [ ] Script de scan multi-outil automatisé
- [ ] Fuzzing automatisé (ffuf)
- [ ] Shadow endpoint discovery automatisé
- [ ] Postman/Newman collection exécution CI/CD
- [ ] Burp headless / Dastardly CI/CD
- [ ] Rapport HTML généré automatiquement
- [ ] Notification Slack/Telegram sur vulnérabilités
- [ ] Monitoring continu (cron, webhook)
- [ ] Détection de changements (shadow APIs)
- [ ] Wordlists pour fuzzing
- [ ] Rate limiting test automatisé
- [ ] Test BOLA/BFLA automatisé

## Ressources

- **Nuclei Templates** : https://github.com/projectdiscovery/nuclei-templates
- **Dastardly (Burp CI)** : https://portswigger.net/dastardly
- **Newman (Postman CLI)** : https://github.com/postmanlabs/newman
- **GitHub Actions Security** : https://docs.github.com/en/actions/security-guides
- **API Security CI/CD** : https://owasp.org/www-project-api-security/
- **HackTricks Automation** : https://book.hacktricks.wiki/en/pentesting-web/api-pentesting-automation/index.html