---
name: socmint-platform-advanced-intel
description: SOCMINT — techniques avancées par plateforme sociale, exploitation d'API, scraping, extraction de données cachées, métadonnées enrichies.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, platform-intel, twitter, instagram, linkedin, tiktok, reddit, discord, advanced]
---

# SOCMINT : Renseignement Avancé par Plateforme

## 🎯 Description

Techniques SOCMINT avancées spécifiques à chaque plateforme sociale : exploitation d'API officielles et non documentées, scraping de données publiques et semi-publiques, extraction de métadonnées enrichies, contournement de limitations, et collecte de données non accessibles via l'interface standard.

Ce skill va au-delà des techniques OSINT de base pour exploiter les **fissures** et **données cachées** de chaque plateforme.

---

## 🐦 X / Twitter — Renseignement Avancé

### API Officielle (v2 avec OAuth 2.0)
```python
import tweepy

client = tweepy.Client(bearer_token="...")

# Récupérer les abonnés en paginant
followers = []
paginator = tweepy.Paginator(
    client.get_users_followers, id=target_id,
    max_results=100, limit=50  # 5000 followers max
)
for page in paginator:
    followers.extend(page.data or [])

# Likes d'un utilisateur (nécessite OAuth utilisateur)
likes = client.get_liked_tweets(id=target_id, max_results=100)

# Listes d'un utilisateur
lists = client.get_lists_memberships(id=target_id)

# Espaces Twitter Spaces
spaces = client.search_spaces(query=target_username, state="all")
```

### Techniques Avancées
| Technique | Méthode | Données Extraites |
|-----------|---------|-------------------|
| User Timeline scraping | `get_users_tweets()` + pagination | Posts supprimés visibles via cache | 
| Follower graph crawl | BFS sur les followers des followers | Écosystème complet |
| Tweet deletion detection | Cron de snapshot quotidien | Détection de nettoyage |
| Like graph | Likes de la cible → centres d'intérêt | Affinités politiques, goûts |
| Retweet tree | Chaîne complète de RT | Propagation de l'information |
| Quote tweet scraping | `get_quote_tweets()` | Commentaires sur la cible |
| Search API avancé | `search_recent_tweets()` avec opérateurs | Mentions indirectes |

### Opérateurs de Recherche Avancés (Twitter/X)
```
has:hashtags          — posts avec hashtags
has:cashtags          — posts avec $CASHTAG
has:media             — posts avec média
has:images            — posts avec images
has:video             — posts avec vidéo
has:mentions          — posts avec @mentions
is:reply              — uniquement les réponses
is:retweet            — uniquement les RT
is:quote              — uniquement les quote tweets
lang:fr               — langue
place:paris           — géolocalisation
point_radius:[lat lon radius] — cercle géographique
bbox:[west south east north]   — rectangle géographique
```

---

## 📸 Instagram — Renseignement Avancé

### Techniques API/Scraping
| Méthode | Outil | Données |
|---------|-------|---------|
| Scraping stories anonyme | Instaloader | Stories même sans login (partiellement) |
| Highlights extraction | Instaloader | Stories archivées |
| Reel téléchargement | yt-dlp + Instagram | Reels avec métadonnées |
| Stories viewer anonyme | dumpor | Stories sans login (site tiers) |
| Profil complet | Instaloader + `--login` | Bio, posts, followers, followings |
| Comment scraping | Instaloader `get_comments()` | Commentaires sur les posts |
| Location scraping | Instaloader location ID | Posts géolocalisés |
| Hashtag scraping | Instaloader `get_hashtag_posts()` | Posts par hashtag |

```bash
# Installation
pip install instaloader

# Téléchargement profil complet
instaloader profile target_username --metadata --no-videos --no-captions

# Stories
instaloader --stories --fast-update target_username

# Posts par hashtag
instaloader #paris --no-pictures --no-videos --no-captions

# Commentaires
instaloader --comments target_username
```

### Métadonnées Instagram Exploitables
- **Location tags** : historique des déplacements
- **Tagged users** : réseau social implicite
- **Likers récurrents** : affinités, communauté proche
- **Story viewers** : qui regarde silencieusement (via API privée)
- **Follow request** : comptes privés qui intéressent la cible
- **Close friends** : cercle restreint (déduit par différence stories IG vs cross-posts)

---

## 💼 LinkedIn — Renseignement Avancé

| Technique | Outil/Méthode | Données |
|-----------|--------------|---------|
| Profile scraping public | Proxy + requests | CV, compétences, recommandations |
| Cross-reference email | Hunter.io + RocketReach | Email pro déduit |
| Network graph | LinkedIn Sales Navigator | 2nd/3rd degree connections |
| Company scraping | `linkedin-jobs-scraper` | Employee list, org chart |
| Post scraping | Playwright/Selenium | Posts, commentaires, likes |
| Endorsement analysis | Scraping manuel | Compétences validées par qui |
| Group membership | Scraping groupes publics | Affiliations professionnelles |

```python
# Exemple : scraping LinkedIn avec Selenium (headless)
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.linkedin.com/in/target_username/")

# Extraire les données du profil
name = driver.find_element(By.CSS_SELECTOR, "h1").text
headline = driver.find_element(By.CSS_SELECTOR, ".headline").text
location = driver.find_element(By.CSS_SELECTOR, ".location").text

# Expérience
experiences = driver.find_elements(By.CSS_SELECTOR, ".experience-section li")
for exp in experiences:
    print(exp.text)
```

> **⚠️ LinkedIn est hostiles au scraping** : compte requis, rate limiting agressif, CAPTCHA. Préférer les API tierces (Proxycurl, Apollo) ou Sales Navigator pour l'analyse réseau.

---

## 🎵 TikTok — Renseignement Avancé

| Outil | URL | Usage |
|-------|-----|-------|
| TikTokAPI | https://github.com/davidteather/TikTok-Api | API non officielle Python |
| TikTok Scraper | https://github.com/drawrowfly/tiktok-scraper | CLI Node.js |
| Snaptik | https://snaptik.app | Téléchargement vidéo |
| Analitik | https://analitik.net | Analyse de profil |
| TikStats | https://tikstats.org | Statistiques TikTok |
| Exolyt | https://exolyt.com | Analyse compétitive |

### Données Exploitables
- **Vidéos likées** (si profil public) : centres d'intérêt
- **Duets** : qui crée du contenu avec la cible
- **Followers/following** : analyse réseau
- **Sound usage** : mêmes sons = même communauté
- **Effects** : tendances suivies par la cible
- **Comment thread** : réseau d'interaction
- **Bio links** : Linktree/Beacons → autres plateformes

---

## 🔴 Reddit — Renseignement Avancé

| Outil | URL | Usage |
|-------|-----|-------|
| PRAW | `pip install praw` | API Reddit Python |
| RedditSearch | https://redditsearch.io | Recherche avancée |
| ReSavr | https://www.resavr.com | Posts supprimés |
| Unddit | https://unddit.com | Posts supprimés archive |
| Redective | https://www.redective.com | Analyse de compte |
| Reddit User Analyser | https://reddit-user-analyser.netlify.app | Stats utilisateur |
| Reddit Comment Search | https://redditcommentsearch.com | Recherche commentaires |

```python
import praw

reddit = praw.Reddit(
    client_id="...",
    client_secret="...",
    user_agent="socmint:v1.0"
)

target = reddit.redditor("target_username")

# Tous les posts et commentaires
for post in target.submissions.new(limit=None):
    print(f"[{post.subreddit}] {post.title} ({post.score})")

for comment in target.comments.new(limit=None):
    print(f"[{comment.subreddit}] {comment.body[:100]} ({comment.score})")

# Subreddits fréquentés
subs = {}
for item in target.submissions.new(limit=1000):
    name = str(item.subreddit)
    subs[name] = subs.get(name, 0) + 1

top_subs = sorted(subs.items(), key=lambda x: x[1], reverse=True)[:20]
print("Subreddits les plus actifs:", top_subs)
```

---

## 🎮 Discord — Renseignement Avancé

| Technique | Outil | Données |
|-----------|-------|---------|
| Scraping profils (utilisateurs accessibles) | Discord.py | Avatar, banner, bio, common servers |
| Message history (serveurs accessibles) | Discord.py `history()` | Messages, réactions, fichiers |
| Voice channel activity | Discord.py | Présence, temps en vocal |
| Mutual servers | API Discord | 0 à N serveurs communs |
| User ID lookup | `discord.id` lookup | Création du compte, flags |
| Avatar changelog | Cache/archives | Évolution avatar |
| Discord Bots | Bot personnel dans le serveur | Logs complets (si autorisé) |

```python
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    user = await client.fetch_user(target_id)
    print(f"User: {user.name}#{user.discriminator}")
    print(f"Created: {user.created_at}")
    print(f"Avatar: {user.display_avatar.url}")
    print(f"Banner: {user.banner.url if user.banner else 'None'}")
    
    # Serveurs communs (si le bot y est aussi)
    for guild in client.guilds:
        member = guild.get_member(target_id)
        if member:
            print(f"Serveur commun: {guild.name}")
            print(f"  Rejoint: {member.joined_at}")
            print(f"  Rôles: {[r.name for r in member.roles]}")
```

---

## 🎯 Guide Rapide par Objectif

| Cible | Techniques SOCMINT par Plateforme |
|-------|-----------------------------------|
| **Localisation** | Twitter geocode + Instagram location tags + TikTok geotags + Foursquare check-ins |
| **Emploi/Réseau pro** | LinkedIn profile + Twitter bio + GitHub orgs + Crunchbase + Glassdoor |
| **Centres d'intérêt** | Reddit posting history + TikTok liked videos + Instagram followed accounts + Twitter likes |
| **Réseau social** | Instagram follower graph + Twitter friend graph + Facebook mutual friends + LinkedIn connections |
| **Horaires/Routine** | Twitter posting times + Instagram story timestamps + Discord activity + Reddit comment times |
| **Relations** | Instagram tagged photos + Facebook relationship status + Twitter @mentions récurrentes |
| **Valeurs/Politique** | Reddit subreddits + Twitter hashtags + Facebook group membership + TikTok following |
| **Évolution temporelle** | Archive.org snapshots + deleted post archives + WayBack Machine profiles |

---

## ⚠️ Pitfalls

- **Rate limiting** : chaque plateforme a ses limites — toujours les documenter avant de scale
- **Détection de scraping** : les grosses plateformes (LinkedIn, Meta) détectent et bannissent les scrapers
- **API payantes** : X/Twitter API v2 Basic coûte $100/mois pour des limites très basses
- **Comptes privés** : la majorité des comptes Facebook/Instagram sont privés aujourd'hui
- **Rotation d'IP** : nécessaire pour le scraping à grande échelle (résidentiel proxies)
- **Légalité** : le scraping de données publiques est dans une zone grise légale selon les juridictions