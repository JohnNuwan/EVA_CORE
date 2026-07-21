---
name: osint-telegram
description: OSINT sur Telegram — analyse de chaînes, groupes, bots, recherche de profils, extraction de données et surveillance.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, telegram, messagerie, chaînes, groupes, bots]
---

# OSINT sur Telegram

## 🎯 Description

Investigation et collecte de renseignements sur Telegram : analyse de chaînes et groupes, identification de profils, extraction de métadonnées, recherche de contenu, surveillance en temps réel et exploitation de bots OSINT.

---

## 📋 Outils Essentiels

### Moteurs de Recherche Telegram
| Outil | URL | Usage |
|-------|-----|-------|
| TGStat | https://tgstat.com | Analyse de chaînes, métriques, tendances |
| TgramSearch | https://tgramsearch.com | Catalogue 700K+ chaînes |
| TeleSearch | https://telesearch.me | Recherche chaînes/groupes/bots |
| Telegago (CSE) | https://cse.google.com/cse?cx=006368593537057042503:efxu7xprihg | Recherche Google avancée Telegram |
| Teleteg | https://teleteg.com | Moteur de recherche Telegram |
| tg.world | https://tg.world | Recherche globale |
| GroupDa | https://groupda.com/telegram/group/search | Recherche par catégorie/pays |
| MotherSearchBot | https://t.me/MotherSearchBot | Recherche dans Telegram |
| OKSearch | https://telegram.me/OkSearchBot | Recherche par mot-clé |

### Frameworks d'Investigation
| Outil | URL | Usage |
|-------|-----|-------|
| Telerecon | https://github.com/sockysec/Telerecon | Framework de reconnaissance |
| Telepathy | https://github.com/proseltd/Telepathy-Community | Archive + analyse de patterns |
| TeleTracker | https://github.com/tsale/TeleTracker | Scripts d'investigation |
| TOsint | https://github.com/drego85/tosint | Extraction d'infos bots/chaînes |
| Maltego Telegram | https://github.com/vognik/maltego-telegram | Entités Maltego pour Telegram |
| CTMV | https://github.com/IvanGlinkin/CCTV | Tracking de localisation 50-100m |

### Scrapers et Extracteurs
| Outil | URL | Usage |
|-------|-----|-------|
| TeleGraphite | https://github.com/hamodywe/telegram-scraper-TeleGraphite | Scraper chaînes → JSON |
| Channel Joiner | https://github.com/spmedia/Telegram-Channel-Joiner | Auto-join de chaînes |

---

## 🔧 Méthodologie

### Phase 1 : Recherche de Chaînes et Groupes
```bash
# Telegago (Google Custom Search)
# Naviguer sur https://cse.google.com/cse?cx=006368593537057042503:efxu7xprihg
# Requêtes types :
#   "mot-clé" site:t.me
#   "mot-clé" "telegram" "channel" OR "group"

# TgramSearch
# Naviguer sur https://tgramsearch.com
# Recherche par mot-clé, catégorie, langue

# TGStat
# Naviguer sur https://tgstat.com
# Top chaînes, catégories, mots-clés tendance
```

### Phase 2 : Analyse de Profil
```bash
# Telerecon
git clone https://github.com/sockysec/Telerecon
cd Telerecon
pip install -r requirements.txt
# Nécessite une API Telegram

# Créer une application Telegram
# Naviguer sur https://my.telegram.org/apps

# Configuration Telerecon
# python3 telerecon.py --api-id API_ID --api-hash API_HASH

# Commandes types :
# python3 telerecon.py --target "username"
# python3 telerecon.py --target "+33612345678" --phone
# python3 telerecon.py --target "channel_name" --channel
```

### Phase 3 : Bots OSINT Utiles
```bash
# Bots d'identification
# @creationdatebot → date de création du compte
# @username_to_id_bot → ID numérique
# @usinfobot → username depuis ID
# @unamer_bot → historique des usernames
# @getchatlistbot → liste des groupes d'un utilisateur

# Bots de recherche
# @TuriBot → ID depuis username
# @RegDateBot → date d'enregistrement
# @GetSendGiftsProBot → cadeaux envoyés/reçus
# @insightbot → centres d'intérêt

# Bots de fuites et vérification
# @Leak_SSINTbot → phone number leakage
# @PasswordSearchBot → mots de passe fuités
# @osint_maigret_bot → username search 1366 sites
# @PimEyesBot → face search
```

### Phase 4 : Surveillance
```bash
# Telepathy - archive et analyse
git clone https://github.com/proseltd/Telepathy-Community
cd telepathy
pip install -r requirements.txt

# TeleTracker
git clone https://github.com/tsale/TeleTracker
python3 teletracker.py --help
```

---

## 📊 Google Dorks Telegram

```text
# Recherche de chaînes
site:t.me "mot-clé" "channel" OR "group"
site:t.me "s" site:t.me
site:t.me "joinchat" "mot-clé"
site:t.me "t.me/joinchat" "hacking" OR "security"
site:t.me "t.me/" "bot"

# Recherche de messages
site:telegram.org "mot-clé" "public"
site:t.me "target_username" OR "target_email"

# Recherche de bots Telegram
site:t.me "bot" "mot-clé"
site:t.me "Bot" "API" "token"
```

---

## 🛠️ Script de Collecte

```bash
#!/bin/bash
# telegram_search.sh
KEYWORD="$1"

echo "=== Recherche Telegram: $KEYWORD ==="

# Google CSE Telegago
echo "--- Telegago ---"
curl -s "https://www.google.com/search?q=site:t.me+$KEYWORD+channel" | \
  grep -oP 't\.me/[a-zA-Z0-9_]+' | sort -u

# Recherche dans TGStat (approximatif)
echo "--- TGStat Search ---"
echo "Naviguer sur https://tgstat.com/search?q=$KEYWORD"

# Vérification de canal
echo "--- Vérification d'accès ---"
for channel in "$@"; do
    echo "https://t.me/$channel :"
    curl -sI "https://t.me/$channel" | grep -i "HTTP\|location"
done
```

---

## 📝 Métadonnées Telegram

### Informations Extractibles
```text
Depuis un profil utilisateur :
- Username (si défini)
- ID numérique unique
- Bio (si publique)
- Photo de profil
- Date d'inscription approximative
- Dernière connexion (si non masquée)
- Liste des groupes communs (si communs)

Depuis une chaîne/ groupe :
- Nom et description
- Nombre d'abonnés/membres
- Date de création
- Pays de création (basé sur préfixe ID)
- Administrateurs (si visibles)
- Statistiques (via TGStat)
```

### ID et Résolution
```bash
# Résoudre un username vers ID
# Envoyer un message à @username_to_id_bot
# Réponse : ID numérique

# Résoudre un ID vers username
# Envoyer un message à @usinfobot
# ou utiliser l'API :
# https://api.telegram.org/botTOKEN/getChat?chat_id=ID

# Vérifier la date de création
# Envoyer /start à @creationdatebot
# Forwarder un message du compte cible
```

---

## 🧩 Analyse de Graphe Social Telegram

```bash
# Analyser les relations :
# 1. Groupes communs entre utilisateurs
# 2. Chaînes auxquelles un utilisateur est abonné
# 3. Interactions dans les commentaires
# 4. Réactions aux posts

# Outils :
# - Telepathy: analyse de patterns de communication
# - Maltego + Telegram Transforms: visualisation de graphe
# - CTMV (CCTV): tracking de localisation
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **API Limits** : Les comptes Telegram sont limités en nombre de requêtes. Utiliser plusieurs comptes si nécessaire.
- **Détection** : L'utilisation de clients non officiels ou de scraping peut faire bannir le compte.
- **Numéros virtuels** : Beaucoup de comptes Telegram utilisent des numéros virtuels (jetables, VoIP).
- **Confidentialité** : Respecter les paramètres de confidentialité des utilisateurs (dernière connexion, bio).
- **Bots publics** : Les bots OSINT publics peuvent logger les requêtes. Utiliser ses propres bots.
- **Légalité** : Le scraping de Telegram peut violer les CGU. Vérifier la légalité.

---

## 🔗 Références

- https://github.com/jivoi/awesome-osint#telegram
- https://github.com/sockysec/Telerecon
- https://tgstat.com/
- https://github.com/tsale/TeleTracker