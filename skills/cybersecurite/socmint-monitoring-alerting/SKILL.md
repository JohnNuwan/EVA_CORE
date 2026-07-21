---
name: socmint-monitoring-alerting
description: SOCMINT — surveillance temps réel des réseaux sociaux, systèmes d'alerte précoce, monitoring de mentions, tracking de campagnes, détection de fuites.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, monitoring, alerting, real-time, early-warning, social-listening]
---

# SOCMINT : Monitoring et Alerting Temps Réel

## 🎯 Description

Mise en place de systèmes de surveillance continue des réseaux sociaux pour la détection précoce de menaces, le tracking de mentions, la veille sur des cibles spécifiques, et l'alerte automatisée sur des signaux prédéfinis.

Permet de passer d'une investigation ponctuelle à une **capacité de surveillance permanente** couvrant des centaines de sources en parallèle.

---

## 📋 Architecture de Monitoring SOCMINT

```
[Sources]
  ├── Twitter/X (API streaming)
  ├── Reddit (PRAW polling)
  ├── Telegram (Telethon events)
  ├── Discord (Bot + Intents)
  ├── RSS/Atom feeds
  ├── Google Alerts
  ├── RSS Bridge
  └── Custom scrapers
          │
          ▼
[Moteur de Surveillance]
  ├── Keyword/Regex matcher
  ├── Sentiment analyzer
  ├── Anomaly detector
  ├── Entity extractor (NER)
  └── Priority scorer
          │
          ▼
[Alerting]
  ├── Discord/Slack webhook
  ├── Telegram bot
  ├── Email (SMTP)
  ├── SMS (Twilio)
  ├── Webhook HTTP
  └── Dashboard (Grafana)
```

---

## 🛠️ Infrastructure de Monitoring

### Option 1 : Lightweight (Cron + Scripts)
```bash
# Cron : Toutes les 15 minutes
*/15 * * * * /usr/bin/python3 /home/socmint/monitor.py

# Script principal
```

```python
import json
import requests
from datetime import datetime

def check_twitter_mentions(target):
    # Via API Twitter v2
    url = f"https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": f"@{target} -is:retweet",
        "max_results": 10,
        "tweet.fields": "created_at,public_metrics,source"
    }
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    r = requests.get(url, params=params, headers=headers)
    return r.json().get("data", [])

def check_reddit_mentions(target):
    headers = {"User-Agent": "socmint-monitor/v1.0"}
    r = requests.get(
        f"https://www.reddit.com/search.json?q={target}&limit=10",
        headers=headers
    )
    return r.json().get("data", {}).get("children", [])

def alert_if_critical(mentions, webhook_url):
    critical_keywords = ["leak", "dox", "hack", "breach", "dump", "password"]
    for m in mentions:
        text = m.get("text", "").lower()
        if any(k in text for k in critical_keywords):
            requests.post(webhook_url, json={
                "content": f"🚨 ALERTE CRITIQUE: {text[:200]}"
            })

if __name__ == "__main__":
    target = "entreprise_cible"
    tweets = check_twitter_mentions(target)
    reddit_posts = check_reddit_mentions(target)
    all_mentions = tweets + [r["data"] for r in reddit_posts]
    alert_if_critical(all_mentions, "https://discord.com/api/webhooks/...")
```

### Option 2 : Moteur de Surveillance Dédié
| Outil | Type | Description |
|-------|------|-------------|
| **TweetFeed** | Twitter monitoring | Script watch Twitter sur mots-clés |
| **TGMon** | Telegram monitoring | Surveillance de chaînes/groups Telegram |
| **Reddit Watch** | Reddit monitoring | Script de veille subreddits |
| **RSS-Bridge** | Self-hosted | Générateur RSS pour sites sans flux |
| **Huginn** | Agent system | Automatisation complète (alternatif à n8n) |
| **n8n** | Workflow automation | No-code monitoring pipelines |
| **Changedetection.io** | Page monitoring | Détection de changements sur pages web |
| **TheHive** | Incident response | Corrélation d'alertes SOCMINT |

### Option 3 : Serveurs SOCMINT Dédiés
```bash
# Exemple: Stack Docker de monitoring SOCMINT
# docker-compose.yml
services:
  changedetection:
    image: ghcr.io/dgtlmoon/changedetection.io
    ports: ["5000:5000"]
    
  huginn:
    image: huginn/huginn
    ports: ["3000:3000"]
    
  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
```

---

## 🔍 Signaux de Surveillance

### Mots-Clés Critiques
```
Catégorie Entreprise :
  - "[nom_entreprise] breach"
  - "[nom_entreprise] leak"
  - "[nom_entreprise] hack"
  - "[domaine] dump"
  - Exemple: "acme-corp.com dump"

Catégorie Personne :
  - "[nom_complet] dox"
  - "[username] leak"
  - "[email] pastebin"
  - "[téléphone] scam"

Catégorie Menace :
  - "targeting [secteur]"
  - "operation [code_name]"
  - "[CVE-2024-XXXX] exploit"
  - "zero day [technologie]"
```

### Expressions Régulières (Pattern Detection)
```python
import re

PATTERNS = {
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone_fr": r"(?:\+33|0033|0)[1-9](?:[\s.-]?\d{2}){4}",
    "ip": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "siren": r"\b\d{9}\b",
    "pastebin_url": r"https?://pastebin\.com/\w+",
    "btc_address": r"\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b",
    "discord_token": r"[mN][\w-]{23,25}\.[\w-]{6,7}\.[\w-]{26,28}",
    "api_key": r"(?:sk-|api[-_]?key|token)[:=]\s*['\"]?[\w-]{20,}",
}
```

---

## 📊 Priorisation des Alertes

### Système de Scoring
```python
class AlertScorer:
    def score_alert(self, mention):
        score = 0
        
        # Critères de score
        source_reliability = {
            "twitter": 30, "reddit": 40, "telegram": 50,
            "discord": 45, "pastebin": 80, "darkweb": 90,
            "breach_forum": 85
        }
        
        keywords_score = {
            "leak": 40, "breach": 50, "dox": 70, "dump": 60,
            "credentials": 50, "password": 45, "hacked": 40,
            "database": 35, "sql": 30, "exploit": 40
        }
        
        # Score base source
        score += source_reliability.get(mention["source"], 20)
        
        # Score mots-clés
        text = mention.get("text", "").lower()
        for kw, pts in keywords_score.items():
            if kw in text:
                score += pts
        
        # Priorité temporelle (récent = plus prioritaire)
        age_hours = mention.get("age_hours", 0)
        score += max(0, 20 - age_hours)
        
        return min(100, score)
    
    def classify(self, score):
        if score >= 75: return "CRITIQUE"
        if score >= 50: return "HAUTE"
        if score >= 25: return "MOYENNE"
        return "BASSE"
```

---

## 🔄 Workflow de Réponse aux Alertes

```
ALERTE (score > 75)
    │
    ▼
1. VÉRIFICATION : 
   └─ L'alerte est-elle légitime ? (pas de faux positif)
   
2. QUALIFICATION :
   └─ Quel est l'impact potentiel ?
   └─ Quelle est la source ?
   └─ Quel est le contenu exact ?

3. COLLECTE DE PREUVES :
   └─ Screenshot de la source
   └─ Archive (archive.is, Wayback Machine)
   └─ Export texte brut
   └─ Hash du contenu (SHA256)

4. RÉPONSE :
   └─ Alerter les parties concernées
   └─ Initier la procédure de remédiation
   └─ Surveiller l'évolution

5. SUIVI :
   └─ Monitorer la propagation
   └─ Vérifier les re-posts
   └─ Mettre à jour les règles de surveillance
```

---

## 📡 Plateformes de Social Listening

| Outil | URL | Type | Prix |
|-------|-----|------|------|
| Brand24 | https://brand24.com | Social listening pro | $99/mois+ |
| Meltwater | https://www.meltwater.com/fr | Media monitoring | Sur devis |
| Talkwalker | https://www.talkwalker.com/fr | Social analytics | Sur devis |
| Mention | https://mention.com/en/ | Media monitoring | $29/mois+ |
| Awario | https://awario.com | Social listening | $39/mois+ |
| Social Searcher | https://www.social-searcher.com | Gratuit limité | Gratuit+ |
| BoardReader | https://boardreader.com | Forums monitoring | Gratuit |
| Google Alerts | https://www.google.com/alerts | Web monitoring | Gratuit |
| Talkwalker Alerts | https://www.talkwalker.com/fr/alerts | Monitoring gratuit | Gratuit |
| Alerti | https://alerti.com | Social listening | Gratuit+ |

---

## 📊 Dashboards de Surveillance

### Exemple : Dashboard SOCMINT
```yaml
Vue d'ensemble:
  - Alertes aujourd'hui: 12 (3 critiques, 5 hautes, 4 moyennes)
  - Sources: Twitter(45), Reddit(23), Telegram(8), Discord(5)
  - Tendances: [+15% mentions cible cette semaine]
  
Top Alertes (24h):
  1. [CRITIQUE] @pastebin_alerte — Base de données fuitée (score 88)
  2. [HAUTE] Reddit r/cybersecurity — CVE-2025-XXXX exploit (score 72)
  3. [HAUTE] Telegram channel — Vente de données secteur (score 65)

Sources actives: 47/52
Dernière alerte: il y a 3 minutes (Discord)
Taux faux positifs: 18%
```

---

## ⚠️ Pitfalls

- **Volume de bruit** : sans filtrage correct, 95% des alertes sont du bruit — investir dans les règles de scoring
- **Épuisement** : un système qui alerte trop tue la vigilance — viser <5 alertes critiques/jour
- **Délai de détection** : Twitter API streaming a 30-60s de latence, pas du temps réel parfait
- **Dépendance API** : une API qui change ou est coupée = trou dans la surveillance
- **Faux positifs** : homonymes, mentions non pertinentes — utiliser des regex négatives
- **Coût API** : Twitter API Pro = $5,000/mois, hors de prix pour un usage personnel
- **RGPD** : la surveillance automatisée de personnes peut violer le RGPD selon l'usage