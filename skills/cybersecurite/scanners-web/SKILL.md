---
name: scanners-web
description: Guide complet des scanners de vulnérabilités web — Nuclei, OWASP ZAP, templates, automatisation, CI/CD, workflow de scan, et intégration.
---

# Scanners Web — Nuclei & OWASP ZAP

---

## 1. Nuclei — Scanner YAML ultra-rapide

### Installation
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Ou via apt (Kali)
apt install nuclei

# Mettre à jour les templates
nuclei -update-templates
```

### Concepts
Nuclei utilise des **templates YAML** qui décrivent :
- La requête HTTP à envoyer
- Les matchers pour détecter la vulnérabilité
- Les extractors pour récupérer des données

### Templates — Structure YAML
```yaml
id: example-detection
info:
  name: Example Vulnerability Detection
  author: researcher
  severity: medium
  description: Detects an example vulnerability
  tags: example,detection

requests:
  - method: GET
    path:
      - "{{BaseURL}}/vulnerable-path"
    matchers:
      - type: word
        words:
          - "sensitive-information"
        part: body
    matchers-condition: and
```

### Commandes essentielles
```bash
# Scan d'une URL unique
nuclei -u https://cible.com

# Scan d'une liste d'URLs
nuclei -l urls.txt

# Filtrer par sévérité
nuclei -u https://cible.com -severity critical,high,medium

# Filtrer par tags
nuclei -u https://cible.com -tags cve,oast
nuclei -u https://cible.com -tags xss,sqli

# Exclure des tags
nuclei -u https://cible.com -etags dos,fuzz

# Utiliser des templates spécifiques
nuclei -u https://cible.com -t /chemin/templates/
nuclei -u https://cible.com -t cves/2024/
nuclei -u https://cible.com -t exposures/configs/

# Workflows (séquences de templates)
nuclei -u https://cible.com -w workflows/

# Détection de technologies
nuclei -u https://cible.com -t technologies/

# Sortie
nuclei -u https://cible.com -o resultats.txt
nuclei -u https://cible.com -json -o resultats.json
nuclei -u https://cible.com -silent    # Mode silencieux
```

### Performance
```bash
# Concurrence (threads)
nuclei -l urls.txt -c 100          # 100 templates simultanés
nuclei -l urls.txt -rl 150         # Rate limit : 150 req/s

# Timeout
nuclei -u https://cible.com -timeout 5
```

### Authentification
```bash
# Headers personnalisés
nuclei -u https://cible.com -H "Authorization: Bearer token"
nuclei -u https://cible.com -H "Cookie: session=xxx"

# Scan avec proxy (Burp)
nuclei -u https://cible.com -proxy http://127.0.0.1:8080
```

### Intégration CI/CD
```bash
# Dans un pipeline GitLab CI
nuclei -u $STAGING_URL -severity critical -json -o nuclei.json
# Si CRITICAL trouvé → bloquer le déploiement
```

### Templates populaires
```bash
# CVE récentes
nuclei -t cves/2024/
nuclei -t cves/2025/

# Exposures
nuclei -t exposures/
nuclei -t exposures/configs/
nuclei -t exposures/backups/

# Misconfiguration
nuclei -t misconfiguration/
nuclei -t misconfiguration/http-missing-security-headers.yaml

# Technologies
nuclei -t technologies/wordpress-detect.yaml
```

---

## 2. OWASP ZAP — Scanner web complet

### Installation
```bash
# Kali (pré-installé)
apt install zaproxy

# Ou télécharger depuis
# https://www.zaproxy.org/download/
```

### Lancement
```bash
# Mode headless
zap.sh -daemon -port 8080

# Mode GUI
zap.sh

# Scan rapide (CLI)
zap.sh -cmd -quickurl https://cible.com -quickprogress

# Scan API
zap.sh -daemon -port 8080 -host 127.0.0.1 -config api.key=changethis
```

### Composants ZAP
| Composant | Fonction |
|-----------|----------|
| **Proxy** | Intercepter le trafic |
| **Spider** | Crawler le site (traditionnel + AJAX) |
| **Active Scanner** | Attaquer activement les endpoints |
| **Passive Scanner** | Analyser le trafic sans envoyer de requêtes |
| **Fuzzer** | Fuzzer les paramètres |
| **Forced Browse** | Énumérer les répertoires |
| **WebSockets** | Tester les WebSockets |
| **Scripts** | Automatiser via Python/JS/Zest |

### Workflow ZAP
```
1. Proxy → Intercepter le trafic du navigateur
2. Spider → Crawler toutes les pages découvertes
3. Active Scan → Scanner les vulnérabilités
4. Alerts → Analyser les alertes (classées par risque)
5. Generate Report → Rapport HTML/PDF/Markdown
```

### Automatisation via API REST
```bash
# Lancer ZAP en daemon
zap.sh -daemon -port 8080 -host 127.0.0.1

# Depuis un autre terminal (curl ou zap-cli)
# Accéder à la cible
curl "http://localhost:8080/JSON/core/action/accessUrl/?url=https://cible.com"

# Lancer le spider
curl "http://localhost:8080/JSON/spider/action/scan/?url=https://cible.com"

# Lancer le scan actif
curl "http://localhost:8080/JSON/ascan/action/scan/?url=https://cible.com"

# Vérifier la progression
curl "http://localhost:8080/JSON/ascan/view/status/?scanId=0"

# Générer un rapport
curl "http://localhost:8080/OTHER/core/other/htmlreport/" > rapport.html
```

### zap-cli — Interface CLI simplifiée
```bash
pip install zap-cli
zap-cli start --start-options '-config api.key=key'
zap-cli open-url https://cible.com
zap-cli spider https://cible.com
zap-cli active-scan https://cible.com
zap-cli alerts --severity High
zap-cli report -o rapport.html -f html
zap-cli shutdown
```

---

## 3. Workflow combiné Nuclei + ZAP

```bash
# 1. ZAP : Crawl profond, analyse passive
zap.sh -daemon -port 8080
zap-cli spider https://cible.com

# 2. Nuclei : Scan rapide des endpoints découverts
nuclei -l endpoins.txt -t exposures/ -t misconfiguration/

# 3. ZAP : Scan actif ciblé
zap-cli active-scan https://cible.com

# 4. Nuclei : Vérification CVE
nuclei -u https://cible.com -t cves/2025/ -severity critical

# 5. Rapport consolidé
zap-cli report -o zap-report.html -f html
nuclei -u https://cible.com -json -o nuclei-report.json
```

---

## 4. Autres scanners notables

### Wapiti
```bash
wapiti -u https://cible.com
wapiti -u https://cible.com --scope page
wapiti -u https://cible.com -m xss,sqli,exec
```

### Arachni
```bash
arachni https://cible.com
arachni --checks=xss*,sql* https://cible.com
```

### WhatWeb (fingerprint web)
```bash
whatweb https://cible.com
whatweb -a 3 https://cible.com    # Agressivité maximale
```

### WPScan (WordPress)
```bash
wpscan --url https://cible.com
wpscan --url https://cible.com -e ap,at,t  # Plugins, thèmes, timthumbs
wpscan --url https://cible.com -U users.txt -P rockyou.txt  # Bruteforce
```

---

## Cheatsheet rapide

```bash
# Nuclei : scan rapide par template
nuclei -u https://cible.com -severity critical,high

# ZAP : scan complet
zap.sh -cmd -quickurl https://cible.com -quickprogress

# WPScan : audit WordPress
wpscan --url https://cible.com --enumerate ap,at,t

# WhatWeb : identification de technologies
whatweb https://cible.com
```

### Ressources
- **Nuclei** : https://github.com/projectdiscovery/nuclei
- **Nuclei Templates** : https://github.com/projectdiscovery/nuclei-templates
- **OWASP ZAP** : https://www.zaproxy.org
- **WPScan** : https://wpscan.com