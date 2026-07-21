---
name: osint-threat-intelligence
description: Renseignement de menace (CTI) — collecte d'IOCs, analyse de malwares, profilage d'acteurs, OSINT cyber et surveillance de menaces.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, cti, threat-intelligence, menace, malware, ioc, apt]
---

# Threat Intelligence (Renseignement de Menace)

## 🎯 Description

Collecte et analyse de renseignements sur les menaces cyber : identification d'acteurs malveillants, analyse de malwares, collecte d'indicateurs de compromission (IOCs), surveillance de campagnes, et corrélation multi-sources pour l'anticipation des attaques.

---

## 📋 Outils Essentiels

### Plateformes CTI
| Outil | URL | Usage |
|-------|-----|-------|
| VirusTotal | https://www.virustotal.com | Analyse fichiers/URLs/domaines |
| AlienVault OTX | https://otx.alienvault.com | Open Threat Exchange |
| MISP | https://www.misp-project.org | Plateforme de partage d'IOCs |
| Taranis AI | https://github.com/taranis-ai/taranis-ai | OSINT + AI/NLP |
| OpenCTI | https://github.com/OpenCTI-Platform/opencti | Plateforme CTI open-source |

### Analyse de Malwares
| Outil | URL | Usage |
|-------|-----|-------|
| MalwareBazaar | https://bazaar.abuse.ch/browse/ | Base d'échantillons |
| Hybrid Analysis | https://www.hybrid-analysis.com | Analyse sandbox |
| Malpedia | https://malpedia.caad.fkie.fraunhofer.de | Base de malwares |
| YARAif | https://yaraify.abuse.ch/scan/ | Moteur YARA collaboratif |
| MetaDefender | https://metadefender.com | Analyse multi-antivirus |
| URLScan | https://urlscan.io | Analyse de sites |

### IOCs et Réputation
| Outil | URL | Usage |
|-------|-----|-------|
| AbuseIPDB | https://www.abuseipdb.com | Réputation IP |
| GreyNoise | https://viz.greynoise.io | IP malveillantes |
| Pulsedive | https://pulsedive.com | Indicateurs enrichis |
| URLhaus | https://urlhaus.abuse.ch | URLs malveillantes |
| PhishStats | https://phishstats.info | Stats de phishing |
| ThreatLens | https://github.com/AbdaullahAG/Threat_Intel_Project | CLI CTI multi-API |
| isMalicious | https://ismalicious.com | Agrégateur de menaces |

### Acteurs de Menace
| Outil | URL | Usage |
|-------|-----|-------|
| Threat Actor Usernames | https://threatactorusernames.com/ | 3M+ usernames d'acteurs |
| Dark Web Informer | https://darkwebinformer.com/threat-actor-database/ | 854+ acteurs |
| Bi.Zone | https://gti.bi.zone/ | 148 groupes APT |
| BreachHQ | https://breach-hq.com/threat-actors | Acteurs malveillants |
| SOCRadar LABS | https://socradar.io/labs/threat-actor/ | Profils d'acteurs |
| Lazarus Day | https://lazarus.day/actors/ | 203 acteurs |

### Infostealer Logs
| Outil | URL | Usage |
|-------|-----|-------|
| Hudson Rock | https://www.hudsonrock.com/threat-intelligence-cybercrime-tools | Infection logs |
| InfoStealers | https://infostealers.info | Index de logs |
| LeakRadar | https://leakradar.io | Scan stealer logs |
| Dropbase | https://dropbase.fun | Breach + malware logs |

---

## 🔧 Méthodologie

### Phase 1 : Collecte d'IOCs
```bash
# VirusTotal API
curl -s "https://www.virustotal.com/api/v3/domains/example.com" \
  -H "x-apikey: YOUR_API_KEY"

# AbuseIPDB
curl -s "https://api.abuseipdb.com/api/v2/check?ipAddress=8.8.8.8" \
  -H "Key: YOUR_API_KEY" \
  -H "Accept: application/json"

# GreyNoise
curl -s "https://api.greynoise.io/v3/community/8.8.8.8"
```

### Phase 2 : Analyse de Malwares
```bash
# Téléchargement depuis MalwareBazaar
curl -s "https://mb-api.abuse.ch/api/v1/" \
  -d "query=get_file&sha256_hash=HASH" \
  -o malware_sample.zip

# Analyse YARA
# yara -s rules.yar malware_sample.bin

# Hybrid Analysis
# Naviguer sur https://www.hybrid-analysis.com -> uploader l'échantillon

# Analyse statique
# file malware_sample.bin
# strings malware_sample.bin
# pecheck malware_sample.exe  # Python tool
```

### Phase 3 : Profilage d'Acteurs
```bash
# Recherche d'acteurs
# Naviguer sur https://threatactorusernames.com/
# Naviguer sur https://malpedia.caad.fkie.fraunhofer.de/actors

# Collecte d'informations sur un groupe APT :
# - Pays parrainé
# - TTPs (MITRE ATT&CK)
# - Malwares utilisés
# - Cibles privilégiées
# - Période d'activité
```

### Phase 4 : Surveillance Continue
```bash
# AlienVault OTX - pulses
curl -s "https://otx.alienvault.com/api/v1/pulses/subscribed" \
  -H "X-OTX-API-KEY: YOUR_KEY"

# Feeds RSS
# - URLhaus: https://urlhaus.abuse.ch/feed/
# - MalwareBazaar: https://bazaar.abuse.ch/export/
# - Shadowserver: https://dashboard.shadowserver.org/

# Cron de surveillance
# 0 */6 * * * /usr/local/bin/check_threats.sh
```

---

## 📊 Framework MITRE ATT&CK

### Cartographie des TTPs
```text
# Ressources MITRE ATT&CK :
# Naviguer sur https://attack.mitre.org

# Exemple de mapping :
TA0001 - Accès Initial
├── T1566 - Phishing
├── T1078 - Comptes valides
└── T1190 - Exploit public

TA0002 - Exécution
├── T1059 - Command and Scripting Interpreter
├── T1204 - User Execution
└── T1559 - Inter-Process Communication
```

### Script de Vérification MITRE
```bash
#!/bin/bash
# check_ttps.sh
echo "=== Mapping TTPs for Threat Actor ==="
echo "Recherche sur https://attack.mitre.org/groups/"

# API MITRE
curl -s "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json" | \
  python3 -c "
import json,sys
data = json.load(sys.stdin)
for obj in data['objects']:
    if obj.get('type') == 'attack-pattern':
        print(f\"{obj['external_references'][0]['external_id']}: {obj['name']}\")
" | head -50
```

---

## 🛠️ Script CTI Automatisé

```bash
#!/bin/bash
# threat_intel_check.sh
IOC="$1"
echo "=== CTI Check for: $IOC ==="

# VirusTotal
echo "--- VirusTotal ---"
curl -s "https://www.virustotal.com/api/v3/search?query=$IOC" \
  -H "x-apikey: $VT_API_KEY" 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('data',[{}])[0].get('attributes',{}).get('last_analysis_stats',{}))"

# URLScan.io
echo "--- URLScan ---"
curl -s "https://urlscan.io/api/v1/search/?q=$IOC" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"Résultats: {d.get('total',0)}\")"

# AlienVault
echo "--- AlienVault OTX ---"
curl -s "https://otx.alienvault.com/api/v1/indicators/domain/$IOC/general" \
  -H "X-OTX-API-KEY: $OTX_KEY" 2>/dev/null | \
  python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"Pulses: {len(d.get('pulse_info',{}).get('pulses',[]))}\")"
```

---

## 📝 Flux de Travail CTI

```text
1. Collecte
   ├── Sources automatisées (feeds RSS, API)
   ├── OSINT manuel (forums, dark web)
   └── Partage communautaire (MISP, OTX)

2. Enrichissement
   ├── Validation des IOCs
   ├── Contexte (acteur, campagne)
   └── Scoring de risque

3. Analyse
   ├── Cartographie MITRE ATT&CK
   ├── Corrélation avec incidents
   └→ Identification de patterns

4. Diffusion
   ├── Rapports
   ├── Alertes
   └── Mise à jour des règles de détection
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Faux positifs** : Les IOCs peuvent être obsolètes ou incorrects. Toujours valider.
- **Volatilité** : Les IOCs changent rapidement (domaines, IPs). Mettre à jour les bases régulièrement.
- **Sources multiples** : Ne jamais se fier à une seule source. Croiser les données.
- **Partage** : Partager les IOCs via MISP/OTX enrichit la communauté.
- **Stockage** : Les échantillons de malwares doivent être stockés de manière sécurisée (sandbox, isolation).
- **Légalité** : Vérifier les conditions d'utilisation des APIs et sources.

---

## 🔗 Références

- https://attack.mitre.org
- https://otx.alienvault.com
- https://github.com/jivoi/awesome-osint#threat-intelligence
- https://www.virustotal.com
- https://github.com/AbdaullahAG/Threat_Intel_Project