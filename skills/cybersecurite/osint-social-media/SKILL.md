---
name: osint-social-media
description: OSINT sur les réseaux sociaux — Twitter/X, Facebook, Instagram, LinkedIn, Reddit, TikTok, Telegram, VKontakte.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, social-media, twitter, facebook, instagram, linkedin, reddit, telegram]
---

# OSINT sur les Réseaux Sociaux

## 🎯 Description

Collecte et analyse d'informations à partir des réseaux sociaux. Techniques de reconnaissance, extraction de données publiques, analyse de profils et mise en relation d'identités numériques à travers les plateformes.

---

## 📋 Plateformes et Outils

### Twitter / X
| Outil | URL | Usage |
|-------|-----|-------|
| Search | https://search.twitter.com | Recherche par mots-clés |
| Advanced Search | https://twitter.com/search-advanced | Filtres avancés |
| Social Blade | https://socialblade.com | Statistiques de comptes |
| ExportData | https://www.exportdata.io | Export de tweets, followers |
| Trends24 | https://trends24.in | Tendances en temps réel |
| Foller.me | https://foller.me | Analyse détaillée de profil |
| Twitter Audit | https://www.twitteraudit.com | Détection de faux followers |
| Xquik | https://xquik.com | Recherche, users, abonnés |

**Commandes de recherche X/Twitter**
```text
from:@username — tweets d'un utilisateur
to:@username — tweets en réponse à un utilisateur
@username — mentions d'un utilisateur
filter:images — tweets avec images
filter:links — tweets avec liens
since:2024-01-01 until:2024-12-31 — intervalle de dates
min_faves:100 — tweets avec 100+ likes
geocode:48.8566,2.3522,10km — tweets géolocalisés
```

### Facebook
| Outil | URL | Usage |
|-------|-----|-------|
| Facebook Search | https://search.fb.com/ | Recherche interne |
| SearchIsBack | https://searchisback.com | Moteur de recherche Facebook |
| Fanpage Karma | https://www.fanpagekarma.com | Analyse de pages |
| Lookup-ID | https://lookup-id.com | Trouver ID numérique |
| haveibeenzuckered | https://haveibeenzuckered.com | Vérification breach FB |

**Techniques Facebook**
```text
- Rechercher par ville + école + employeur
- Utiliser les photos de profil pour reverse image search
- Explorer les pages likées pour trouver des affiliations
- Vérifier les commentaires publics sur des pages populaires
```

### Instagram
| Outil | URL | Usage |
|-------|-----|-------|
| Osintgram | https://github.com/Datalux/Osintgram | Analyse complète de compte |
| Instagram Monitor | https://github.com/misiektoja/instagram_monitor | Tracking en temps réel |
| Social Blade | https://socialblade.com | Statistiques |
| Iconosquare | https://iconosquare.com | Analyse |
| insto | https://github.com/subzeroid/insto | CLI OSINT interactif |

### LinkedIn
| Outil | URL | Usage |
|-------|-----|-------|
| LinkedInDumper | https://github.com/l4rm4nd/LinkedInDumper | Extraction employés |
| the-endorser | https://github.com/eth0izzle/the-endorser | Relations par endorsements |
| Apollo.io | https://www.apollo.io/ | Find emails & phones B2B |

### Reddit
| Outil | URL | Usage |
|-------|-----|-------|
| Reddit User Analyser | https://atomiks.github.io/reddit-user-analyser/ | Analyse de compte |
| RedditMetis | https://redditmetis.com/ | Statistiques et résumé |
| Reddit Comment Search | https://redditcommentsearch.com/ | Historique de commentaires |
| Pushshift API | https://pushshift.io/ | Données historiques |
| Pullpush | https://pullpush.io/ | Contenu supprimé |
| Filmot | https://filmot.com/ | Recherche dans sous-titres YouTube |

### TikTok
| Outil | URL | Usage |
|-------|-----|-------|
| TikTokStalker | https://tiktok.einzzcookie.org | Infos sur comptes TikTok |

### Telegram
| Outil | URL | Usage |
|-------|-----|-------|
| TGStat | https://tgstat.com/ | Analyse de chaînes |
| Telegago (CSE) | https://cse.google.com/cse?cx=006368593537057042503:efxu7xprihg | Recherche chaînes/groupes |
| Telepathy | https://github.com/proseltd/Telepathy-Community | Archive et analyse |
| Telerecon | https://github.com/sockysec/Telerecon | Framework de reconnaissance |
| CTMV | https://github.com/IvanGlinkin/CCTV | Tracking de localisation |
| Telegram Finde | https://www.telegram-finder.io/ | Recherche par téléphone/email |
| TgramSearch | https://tgramsearch.com/ | Catalogue de chaînes |
| TeleSearch | https://telesearch.me/ | Recherche chaînes/groupes |

### VKontakte
| Outil | URL | Usage |
|-------|-----|-------|
| VK.watch | https://vk.watch/ | OSINT VK |
| VK5 | https://vk5.city4me.com | Analyse VK |
| VK Community Search | https://vk.com/communities | Recherche de communautés |

---

## 🔧 Méthodologie

### 1. Recherche Multi-Plateforme
```bash
# Utiliser Sherlock pour username check
pip install sherlock
sherlock username

# Maigret (plus complet)
pip install maigret
maigret username --all --html

# Blackbird (600+ sites)
pip install blackbird
blackbird --username username
```

### 2. Analyse de Profil
```bash
# Social Analyzer
pip install social-analyzer
social-analyzer --username username

# Nexfil
# pip install nexfil
# nexfil --username username
```

### 3. Recherche par Email
```bash
# Holehe - vérifie les comptes associés à un email
pip install holehe
holehe email@example.com

# Epieos (web)
# Naviguer vers https://epieos.com
```

### 4. Recherche par Téléphone
```bash
# PhoneInfoga
pip install phoneinfoga
phoneinfoga scan -n "+33612345678"
```

---

## 📊 Google Dorks Sociaux

```text
# Profils spécifiques
site:twitter.com "username" OR "nom complet"
site:facebook.com "nom complet" "ville"
site:linkedin.com "nom complet" "entreprise"
site:instagram.com "username"
site:reddit.com "username" OR "pseudo"

# Email sur réseaux
site:facebook.com "email@example.com"
site:twitter.com "email@example.com"
site:reddit.com "email@example.com"

# Informations personnelles
inurl:facebook.com "photos" "nom complet"
site:linkedin.com "nom complet" "email" OR "phone"
```

---

## 🛡️ Analyse de Relations

### Social Network Analysis (SNA)
```bash
# Maltego (CE gratuit)
# https://www.maltego.com/downloads/

# Gephi (visualisation de graphes)
# https://gephi.org/
```

### Outils Web
| Outil | URL | Usage |
|-------|-----|-------|
| IDCrawl | https://www.idcrawl.com/ | Recherche nom dans réseaux |
| Social Searcher | https://www.social-searcher.com | Recherche multi-réseaux |
| UVRX | https://www.uvrx.com/social.html | Recherche sociale |
| Castrick | https://castrickclues.com | Trouver comptes par email/username/tel |
| Predicta Search | https://predictasearch.com | Recherche comptes sociaux |

---

## ⚠️ Pièges et Bonnes Pratiques

- **Comptes privés** : Ne pas tenter de contourner la confidentialité — se limiter aux données publiques.
- **Faux comptes** : Vérifier la légitimité des comptes (date de création, activité, followers réels).
- **Rate limiting** : La plupart des plateformes limitent le scraping. Utiliser des API officielles quand possible.
- **Anonymat** : Créer des comptes de recherche séparés, utiliser Tor/VPN.
- **Légalité** : Le scraping peut violer les CGU. Vérifier la légalité dans votre juridiction.

---

## 🔗 Références

- https://github.com/jivoi/awesome-osint#social-media-tools
- https://github.com/sherlock-project/sherlock
- https://whatsmyname.app/
- https://github.com/p1ngul1n0/blackbird