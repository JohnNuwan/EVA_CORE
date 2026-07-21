---
name: osint-automation-frameworks
description: Frameworks d'automatisation OSINT — SpiderFoot, BBoT, Recon-ng, Maltego, Little Brother, outils de pipeline et intégration.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, automation, framework, spiderfoot, bbot, recon-ng, maltego, pipeline]
---

# OSINT Automation Frameworks

## 🎯 Description

Frameworks et outils d'automatisation OSINT pour scaler les investigations : orchestration multi-modules, pipelines de collecte automatisée, analyse corrélée, rapports structurés et intégration avec d'autres outils de cybersécurité.

---

## 📋 Frameworks Principaux

### 🕷️ SpiderFoot — Le plus complet
| Caractéristique | Détail |
|----------------|--------|
| **Modules** | 200+ modules de collecte OSINT |
| **Interfaces** | CLI + Serveur Web |
| **Format** | Scan → Graphes → Rapports CSV/JSON/XLSX |
| **License** | GPL v2 (communauté) / Commerciale |
| **Installation** | pip, Docker, binaire |

```bash
# Installation
git clone https://github.com/smicallef/spiderfoot
cd spiderfoot
pip install -r requirements.txt

# Lancement serveur web
python3 sf.py -l 127.0.0.1:5001
# → Naviguer sur http://127.0.0.1:5001

# CLI
python3 sf.py -m "sfp__stor_stdout" -s "example.com" -o csv > results.csv

# Scan avec modules spécifiques
python3 sf.py -s "example.com" -t "DOMAIN_NAME" \
  -m "sfp_dnsresolve,sfp_whois,sfp_crtsh,sfp_shodan" \
  -o json

# Scan complet (tous les modules)
python3 sf.py -s "example.com" -t "DOMAIN_NAME" -o xlsx > report.xlsx
```

**Modules clés SpiderFoot :**
```text
sfp_dnsresolve     → Résolution DNS
sfp_whois          → WHOIS
sfp_crtsh          → Certificats SSL
sfp_shodan         → Shodan
sfp_haveibeenpwned → HIBP
sfp_socialmedia    → Réseaux sociaux
sfp_emailformat    → Format emails
sfp_socialnetwork  → Profils sociaux
sfp_webanalytics   → Analytics
sfp_webrecon       → Reconnaissance web
sfp_subdomaintakeover → Sous-domaines
sfp_portscan_tcp   → Scan de ports
```

### 🤖 BBoT (Bighorn BOT) — Performance et modularité
| Caractéristique | Détail |
|----------------|--------|
| **Modules** | 50+ modules, extensible |
| **Interfaces** | CLI uniquement |
| **Format** | Scan → JSON/CSV/TXT |
| **License** | Apache 2.0 |
| **Performance** | Très rapide, parallélisation native |

```bash
# Installation
pip install bbot

# Scan OSINT complet
bbot -t example.com -m osint scan

# Scan avec modules spécifiques
bbot -t example.com -m crtsh dns brutella subdomain-enum scan

# Scan avec plusieurs cibles
bbot -t example.com -t example.org -m leakix hudsonrock scan

# Scan avec rapport
bbot -t example.com -m osint --output-dir ./results scan

# Agent autonome (surveillance continue)
bbot -t example.com -m badops --allow-dead-domains -af
```

**Flags utiles BBoT :**
```bash
--output-dir DIR     # Répertoire de sortie
--output-module csv  # Format CSV
-s                   # Silencieux
-v                   # Verbose
--no-dns-resolve     # Pas de résolution DNS
--force              # Forcer le scan même si déjà fait
```

### 🔧 Recon-ng — Framework modulaire Recon
```bash
# Installation
git clone https://github.com/lanmaster53/recon-ng
cd recon-ng
pip install -r REQUIREMENTS

# Lancement
./recon-ng  # interface interactive

# CLI (non-interactive) - workflow typique
./recon-ng -r <(echo '
workspaces create investigation
db insert companies
companies set company "Target Corp"
keys add shodan_api KEY
use recon/companies-contacts/whoxy_whois
run
use recon/companies-multi/github_miner
run
')
```

### 📊 Maltego — Analyse de liens et visualisation
| Version | URL | Usage |
|---------|-----|-------|
| **Maltego CE** | https://maltego.com/downloads/ | Gratuite (limitée) |
| **Maltego XL** | https://maltego.com/maltego-xl/ | Payante (10k entités) |
| **Maltego Classic** | https://maltego.com/maltego-classic/ | Payante (2.5k entités) |
| **Paterva** | https://paterva.com/ | Éditeur historique |

```bash
# Maltego CE (installation Linux)
# 1. Télécharger depuis le site officiel
# 2. Installer Java : sudo apt install openjdk-17-jre
# 3. Lancer : sh Maltego_v*.sh
# 4. Créer un compte Paterva (gratuit)
# 5. Ajouter les transforms OSINT :
#    - Shodan
#    - Have I Been Pwned
#    - VirusTotal
#    - BuiltWith
#    - Whois
#    - Social Media
```

### 🐣 Little Brother — Surveillance OSINT modulaire
```bash
# Installation
git clone https://github.com/lulz3xploit/LittleBrother
cd LittleBrother
pip install -r requirements.txt

# Usage
python3 littlebrother.py --name "Prénom Nom" --country FR
# Recherche : Facebook, Twitter, Instagram, LinkedIn + moteurs
```

---

## 📊 Pipelines d'Automatisation

### Pipeline Basique (BBoT → SpiderFoot → Rapport)
```bash
#!/bin/bash
# osint_pipeline.sh
TARGET="$1"
DIR="./results/$TARGET"
mkdir -p "$DIR"

echo "=== Phase 1: BBoT - Scan rapide ==="
bbot -t "$TARGET" -m osint --output-dir "$DIR/bbot" scan

echo "=== Phase 2: SpiderFoot - Scan détaillé ==="
cd ~/tools/spiderfoot
python3 sf.py -s "$TARGET" -o json > "$DIR/spiderfoot.json"

echo "=== Phase 3: Sous-domaines ==="
curl -s "https://crt.sh/?q=%25.$TARGET&output=json" | \
  jq -r '.[].name_value' | sort -u | grep -v "\*" > "$DIR/subdomains.txt"

echo "=== Phase 4: Vérification HTTP ==="
while read -r sub; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "https://$sub" 2>/dev/null)
    echo "$sub -> HTTP $code" >> "$DIR/httpx.txt"
done < "$DIR/subdomains.txt"

echo "=== Terminé. Résultats dans $DIR ==="
```

### Pipeline de Surveillance Continue
```bash
#!/bin/bash
# continuous_monitor.sh
TARGETS=("example.com" "example.org")
INTERVAL=86400  # 24h

while true; do
    for target in "${TARGETS[@]}"; do
        bbot -t "$target" \
             -m osint,darkleak \
             --output-dir "./continuous/$target/$(date +%Y%m%d)" \
             scan
    done
    sleep "$INTERVAL"
done
```

### Pipeline d'Enrichissement Automatisé
```bash
#!/bin/bash
# enrich.sh
# Prend une liste d'emails/usernames et les enrichit via toutes les sources

INPUT="$1"
while IFS= read -r item; do
    # Vérifier si c'est un email ou un username
    if echo "$item" | grep -q '@'; then
        echo "=== Email: $item ==="
        holehe "$item" 2>/dev/null | grep "\\[+\\]"
        curl -s "https://emailrep.io/$item" | jq '{reputation, suspicious, details}'
        curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=$item" | jq .
    else
        echo "=== Username: $item ==="
        maigret "$item" --json 2>/dev/null | python3 -c "
import json, sys
data = json.load(sys.stdin)
for site, info in data.get('sites', {}).items():
    if info.get('status') == 'claimed':
        print(f'  ✓ {site}: {info.get(\"url\", \"\")}')
"
    fi
    sleep 3  # Rate limiting
done < "$INPUT"
```

---

## 🛠️ Comparatif des Frameworks

| Critère | SpiderFoot | BBoT | Recon-ng | Maltego |
|---------|-----------|------|----------|---------|
| **Modules** | 200+ | 50+ | 100+ | 1000+ (transforms) |
| **Installation** | Python/Docker | pip | pip | Java (lourd) |
| **Interface** | CLI + Web | CLI | CLI + Console | GUI |
| **Performance** | Moyenne | Très rapide | Rapide | Lente |
| **Visualisation** | Graphes intégrés | Fichiers JSON | Tabulaire | Graphes avancés |
| **API intégrées** | Nombreuses | Principales | Modulables | Transforms |
| **Rapports** | CSV/JSON/XLSX | TXT/JSON | Scriptable | Exports graphiques |
| **Scalabilité** | Docker swarm | Native parallèle | Simple | Payante |
| **Mise à jour** | Mensuelle | Active | Modérée | Active |

---

## 📝 Workflow Recommandé

```text
Phase 1 — Découverte rapide (BBoT)
  → bbot -t cible -m osint scan
  → Obtention : sous-domaines, emails, IPs, technologies

Phase 2 — Analyse approfondie (SpiderFoot)
  → Lancer SpiderFoot sur le domaine/IP
  → 200+ modules de collecte passive
  → Graphe de corrélation

Phase 3 — Pivot et enrichissement (Recon-ng)
  → Workspace dédié
  → DB locale SQLite
  → Export structuré

Phase 4 — Visualisation (Maltego)
  → Importer les résultats
  → Explorer les relations
  → Graphe actionnable
```

---

## 🐳 Déploiement Docker (optionnel)

```yaml
# docker-compose.yml
version: '3'
services:
  spiderfoot:
    image: spiderfoot
    ports:
      - "5001:5001"
    volumes:
      - ./data:/var/lib/spiderfoot
    command: -l 0.0.0.0:5001
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Rate limiting** : Tous les frameworks doivent respecter les limites de taux des APIs. Configurer des délais entre les requêtes.
- **Détection** : Les scans OSINT automatisés sont facilement détectables. Utiliser Tor/VPN si l'anonymat est requis.
- **Volume de données** : SpiderFoot sur une cible peut générer des centaines de milliers de résultats. Filtrer tôt dans le pipeline.
- **API keys** : La plupart des modules nécessitent des clés API. Centraliser dans les fichiers de config des frameworks.
- **Corrélation** : Les résultats sont aussi bons que les données en entrée. Nettoyer et normaliser avant l'analyse.
- **Performance** : BBoT est significativement plus rapide que SpiderFoot. Utiliser BBoT pour les scans larges, SpiderFoot pour la profondeur.
- **Stockage** : Les résultats de scans OSINT sont sensibles. Stocker dans des bases chiffrées (SQLite avec SQLCipher).
- **Légalité** : Le scraping automatisé peut violer les CGU. Vérifier la légalité pour chaque source.

---

## 🔗 Références

- https://github.com/smicallef/spiderfoot
- https://github.com/blacklanternsecurity/bbot
- https://github.com/lanmaster53/recon-ng
- https://www.maltego.com
- https://github.com/lulz3xploit/LittleBrother
- https://github.com/jivoi/awesome-osint#osint-automation-frameworks