---
name: adam-sentinel
description: ADAM-SENTINEL — Veilleur technologique 24h/24h. Scanne 10 domaines, cree des rapports, met a jour les skills, alerte sur les CVE et breaking changes.
category: agents
---

# ADAM-SENTINEL — Veilleur Technologique

## Quand utiliser

- L'utilisateur demande de surveiller des domaines technologiques
- L'utilisateur veut creer un systeme de veille automatisee
- L'utilisateur demande des alertes sur les CVEs, breaking changes, nouveaux modeles IA
- L'utilisateur veut un dashboard de tendances technologiques

## Structure

```
~/scripts/
├── sentinel-watch.sh        # Scan quotidien (cron 8h)
├── sentinel-update.sh       # Mise a jour des skills
└── sentinel-scraper.py      # Scraper web Python (BeautifulSoup + requests)

~/wiki/sentinel/
├── INDEX.md                 # Dashboard de veille
└── daily-YYYY-MM-DD.md      # Rapports quotidiens

~/wiki/entities/
└── adam-sentinel.md         # Documentation
```

## Domaines surveilles (10)

1. **cybersec** → https://thehackernews.com
2. **ai-ml** → https://www.marktechpost.com
3. **osint** → https://www.osintme.com
4. **devops** → https://devops.com
5. **cloud** → https://aws.amazon.com/blogs/aws/
6. **design** → https://www.smashingmagazine.com/articles/
7. **blockchain** → https://cointelegraph.com
8. **crypto** → https://decrypt.co
9. **network** → https://blog.cloudflare.com
10. **programmation** → https://dev.to

## Installation

```bash
# Rendre les scripts executables
chmod +x ~/scripts/sentinel-*.sh ~/scripts/sentinel-scraper.py

# Creer le cron job
hermes cron create "0 8 * * *" \
  --name "ADAM-SENTINEL Veille Quotidienne" \
  --prompt "Execute ADAM-SENTINEL" \
  --deliver all
```

## Execution manuelle

```bash
bash ~/scripts/sentinel-watch.sh
bash ~/scripts/sentinel-update.sh
```

## Regles d'alerte

- **CVE critique** (score >= 9.0) → alerte immediate
- **Framework majeur** (React, Kubernetes, Docker, Terraform) qui change
- **Nouveau modele IA** majeur (GPT-5, Gemini 3, Claude 4, etc.)
- **Breaking change** dans un outil utilise par The Hive

## Fichiers

- `sentinel-watch.sh` : Scrape 10 sites, genere le rapport daily, met a jour l'INDEX
- `sentinel-scraper.py` : Scraper Python robuste avec BeautifulSoup + fallback lynx
- `sentinel-update.sh` : Verifie les skills existants, suggere des nouveaux
- `INDEX.md` : Dashboard avec tendances, alertes, statistiques
- `adam-sentinel.md` : Documentation complete de l'entite