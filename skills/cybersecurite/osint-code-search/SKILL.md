---
name: osint-code-search
description: Recherche dans le code source — GitHub OSINT, pastebins, fuites de code, secrets exposés, code search engines et analyse de repositories.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, code, github, pastebin, repository, secrets, fuites-code]
---

# Recherche dans le Code Source et Pastebins

## 🎯 Description

Techniques OSINT appliquées au code source : recherche de secrets exposés (API keys, tokens, mots de passe) dans les repositories publics, analyse de pastebins pour trouver des fuites de données, exploration de GitHub, GitLab et autres plateformes de code, et exploitation des moteurs de recherche de code.

---

## 📋 Outils Essentiels

### Code Search Engines
| Outil | URL | Usage |
|-------|-----|-------|
| GitHub Code Search | https://github.com/search?type=code | Recherche code GitHub |
| SourceGraph | https://sourcegraph.com/search | Recherche multi-repos |
| grep.app | https://grep.app/ | Recherche regex GitHub |
| SearchCode | https://searchcode.com | 10+ sources |
| PublicWWW | https://publicwww.com/ | Recherche dans code source web |
| NerdyData | https://nerdydata.com | Recherche source code |
| Code Finder | https://codefinder.dev/ | Recherche repos GitHub |
| AnalyzeID | https://analyzeid.com | Sites web mêmes propriétaires |

### GitHub OSINT
| Outil | URL | Usage |
|-------|-----|-------|
| GitLeak | https://gitleak.io | Secrets exposés via .patch |
| GHNames | https://ghnames.com/ | Historique usernames, emails |
| GithubRecon | https://kriztalz.sh/github-recon/ | Recherche username/email |
| GitHub Monitor | https://github.com/misiektoja/github_monitor | Tracking en temps réel |
| Gitrecon | https://github.com/atiilla/gitrecon | Scan emails/noms exposés |
| GitGuardian | https://www.gitguardian.com/monitor-public-github-for-secrets | Monitoring secrets |
| Related Repos | https://relatedrepos.com/ | Repos similaires |
| Shotstars | https://github.com/snooppr/shotstars | Analyse fake stars |

### Pastebin Search
| Outil | URL | Usage |
|-------|-----|-------|
| Pastebin | https://pastebin.com | Principal site de paste |
| GitHub Gist | https://gist.github.com | Gists GitHub |
| psbdmp | https://psbdmp.ws | Moteur de recherche pastebins |
| IntelX | https://intelx.io | Recherche dans pastebins + fuites |
| JustPaste | https://justpaste.it | Alternative pastebin |
| Rentry | https://rentry.co | Markdown paste |
| Write.as | https://write.as | Publication anonyme |
| PrivateBin | https://privatebin.info | Pastebin crypté |

### Secrets Detection
| Outil | URL | Usage |
|-------|-----|-------|
| TruffleHog | https://github.com/trufflesecurity/trufflehog | Scan de secrets dans git |
| Gitleaks | https://github.com/gitleaks/gitleaks | Détection de secrets |
| GitLeak.io | https://gitleak.io | Web-based |
| GitGuardian | https://www.gitguardian.com | Monitoring pro |

---

## 🔧 Méthodologie

### Phase 1 : GitHub Code Search
```bash
# Recherche basique GitHub
# Naviguer sur https://github.com/search?type=code

# Syntaxe de recherche GitHub :
# "API_KEY" language:python
# "-----BEGIN RSA PRIVATE KEY-----" 
# "password" OR "secret" repo:user/repo
# "sendgrid" filename:.env
# "aws_secret_access_key" language:python
# "token" "slack" "bot" path:config
# "mongodb://" NOT "example"

# Recherche avec SourceGraph
# Naviguer sur https://sourcegraph.com/search
# "patternType:regexp (password|secret|token)" -file:test
```

### Phase 2 : grep.app
```bash
# Naviguer sur https://grep.app/
# Requêtes types :
#   "AKIA[0-9A-Z]{16}" (AWS Access Keys)
#   "sk-[a-zA-Z0-9]{32,}" (OpenAI keys)
#   "-----BEGIN OPENSSH PRIVATE KEY-----"
#   "DB_PASSWORD" "DB_HOST" "DB_USERNAME"
#   "api_key" "api_secret" lang:python
#   "token" "secret" lang:javascript NOT "test" NOT "example"
```

### Phase 3 : Recherche dans Pastebins
```bash
# psbdmp.ws - API
curl -s "https://psbdmp.ws/api/v3/search/email@example.com"

# IntelX - recherche
# Naviguer sur https://intelx.io -> onglet Pastebin

# Google Dorks pour pastebins
# site:pastebin.com "email@example.com"
# site:pastebin.com "password" "login"
# site:pastebin.com "API_KEY" OR "SECRET_KEY"
# site:pastebin.com "username" "password" "email"
# site:gist.github.com "email@example.com"
# site:rentry.co "password" OR "secret"
```

### Phase 4 : Analyse de Secrets
```bash
# TruffleHog
pip install trufflehog
trufflehog git https://github.com/user/repo.git
trufflehog filesystem /path/to/directory

# Gitleaks
sudo apt install gitleaks -y
gitleaks detect --source /path/to/repo -v
gitleaks detect --source /path/to/repo --report-format json --report report.json

# GitHub API - recherche dans les commits
curl -s "https://api.github.com/search/code?q=API_KEY+language:python" \
  -H "Authorization: token YOUR_TOKEN" | python3 -m json.tool
```

---

## 📊 Google Dorks pour le Code

```text
# Fichiers sensibles
filetype:env "DB_PASSWORD" OR "API_KEY"
filetype:yml "database" "password"
filetype:xml "password"
filetype:sql "INSERT INTO" "password"
filetype:conf "password"
filetype:config "password" "username"
filetype:log "password" "POST"
filetype:txt "password" "login" OR "email"
filetype:json "api_key" OR "api_secret"
filetype:toml "api" "key" "token"

# Dumps de bases de données
"INSERT INTO" "users" filetype:sql
"CREATE TABLE" filetype:sql "password"

# AWS et Cloud
"aws_access_key_id" "AKIA" filetype:txt
"aws_secret_access_key" filetype:env
"s3.amazonaws.com" "backup" OR "dump"
```

---

## 🛠️ Script de Scan Automatisé

```bash
#!/bin/bash
# code_scan.sh
QUERY="$1"

echo "=== Scan Code for: $QUERY ==="

# GitHub Code Search
echo "--- GitHub ---"
curl -s "https://api.github.com/search/code?q=$QUERY" \
  -H "Authorization: token $GITHUB_TOKEN" 2>/dev/null | \
  python3 -c "
import json,sys
d = json.load(sys.stdin)
for item in d.get('items', [])[:10]:
    print(f\"  {item['repository']['full_name']}: {item['path']}\")
"

# grep.app
echo "--- grep.app ---"
curl -s "https://grep.app/api/search?q=$QUERY" | \
  python3 -c "
import json,sys
try:
    d = json.load(sys.stdin)
    print(f\"Résultats: {d.get('total',0)}\")
except:
    print('Erreur API')
"
```

---

## 📝 Types de Secrets Recherchés

```text
# API Keys et Tokens
AWS Access Key: AKIA[0-9A-Z]{16}
AWS Secret: [a-zA-Z0-9/+]{40}
OpenAI: sk-[a-zA-Z0-9]{32,}
GitHub Token: ghp_[a-zA-Z0-9]{36}
GitHub Fine-grained: github_pat_[a-zA-Z0-9]{82}
Slack Token: xox[baprs]-[a-zA-Z0-9-]{12,}
Google API: AIza[0-9A-Za-z-_]{35}
Stripe: sk_live_[a-zA-Z0-9]{24,}
Twilio: SK[a-zA-Z0-9]{32}
Heroku: [hH][eE][rR][oO][kK][uU]-[a-zA-Z0-9]{36}

# Clés privées
RSA: -----BEGIN RSA PRIVATE KEY-----
OPENSSH: -----BEGIN OPENSSH PRIVATE KEY-----
PGP: -----BEGIN PGP PRIVATE KEY BLOCK-----

# Mots de passe de bases de données
mongodb://[a-zA-Z0-9]+:[a-zA-Z0-9]+@
mysql://[a-zA-Z0-9]+:[a-zA-Z0-9]+@
postgresql://[a-zA-Z0-9]+:[a-zA-Z0-9]+@
redis://:[a-zA-Z0-9]+@
```

---

## 📊 Analyse de Commit History

```bash
# Recherche dans l'historique git
git log --all --diff-filter=M --name-only --format="%H %s" | head -50

# Recherche de mots de passe dans les commits
git log --all -p | grep -i "password\|secret\|key\|token" | head -20

# Analyse des tags
git tag -l

# Blame
git blame -L 1,50 config/database.yml
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Faux positifs** : Beaucoup de résultats sont des exemples ou des tests. Vérifier le contexte.
- **Rate limiting** : GitHub API limite à 10 req/min sans token, 5000 req/h avec token authentifié.
- **Tokens valides** : Certains tokens exposés peuvent être invalides. Les vérifier avant de les signaler.
- **Responsible disclosure** : Signaler les secrets trouvés via les canaux appropriés (security.txt, email).
- **Droit d'auteur** : Le code source est souvent protégé par le droit d'auteur. Ne pas l'utiliser sans autorisation.
- **Légalité** : L'exploitation de secrets trouvés peut constituer un délit. Signaler uniquement.

---

## 🔗 Références

- https://github.com/trufflesecurity/trufflehog
- https://github.com/gitleaks/gitleaks
- https://grep.app/
- https://github.com/jivoi/awesome-osint#code-search