---
name: socmint-disinformation-bot-detection
description: SOCMINT — détection de bots, fake accounts, désinformation, opérations d'influence, astroturfing, manipulation algorithmique et analyse de campagnes.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, disinformation, bot-detection, fake-accounts, influence-operations, astroturfing]
---

# SOCMINT : Détection de Désinformation et Bots

## 🎯 Description

Identification et analyse des opérations de manipulation de l'information sur les réseaux sociaux : détection de comptes automatisés (bots), fermes à likes/followers, campagnes d'astroturfing, amplification artificielle, désinformation coordonnée, et influence operations (IO) étatiques ou commerciales.

---

## 🤖 Détection de Bots Sociaux

### Métriques de Score Bot
```python
class BotDetector:
    """Score de 0 (humain) à 100 (bot certain)"""
    
    def score(self, account: dict) -> float:
        score = 0.0
        
        # 1. Ratio followers/following
        ff_ratio = account["followers"] / max(account["following"], 1)
        if ff_ratio < 0.1: score += 15  # suit bcp, peu suivi
        if ff_ratio > 100: score += 10   # bcp followers, suit peu
        
        # 2. Ratio posts/jour
        account_age = (datetime.now() - account["created_at"]).days
        posts_per_day = account["statuses_count"] / max(account_age, 1)
        if posts_per_day > 50: score += 20      # spam
        if posts_per_day > 5: score += 10       # très actif
        
        # 3. Age du compte
        if account_age < 30: score += 15         # compte récent
        if account_age < 7: score += 25          # compte très récent
        
        # 4. Default profile
        if account.get("default_profile"): score += 10
        if account.get("default_profile_image"): score += 15
        
        # 5. Bio vide ou générique
        bio = account.get("description", "")
        if not bio: score += 10
        if bio in GENERIC_BIOS: score += 15
        
        # 6. Username pattern
        username = account.get("username", "")
        if re.search(r"[0-9]{4,}", username): score += 10  # username_suffix7892
        if re.search(r"^[a-z]+[0-9]+$", username): score += 5
        
        return min(100, score)
```

### Caractéristiques des Bots
| Indicateur | Bot | Humain |
|------------|-----|--------|
| Ratio followers/following | < 0.1 ou > 100 | 0.5 - 10 |
| Âge du compte | < 30 jours (campagne) | > 1 an |
| Posts/jour | > 20 (spam) | 0.1 - 5 |
| Image de profil | Par défaut ou stock photo | Photo personnelle |
| Bio | Vide / copiée / générique | Personnalisée |
| Username | Nom + chiffres aléatoires | Nom cohérent |
| Variance horaire | Publie 24h/24 (pas de sommeil) | Pics jour + sommeil |
| Réseau | Suit 1000+ comptes en masse | Croissance organique |
| Interactions | RT massifs, peu de replies | Conversation équilibrée |
| Ratio RT/original | > 10:1 | Variable, < 5:1 |

---

## 🏭 Détection de Fermes à Bots

### Topologies Caractéristiques
```
Topologie 1 : Étoile (Follow Farm)
        ┌── bot1 ──┐
        │          │
  hub ──┼── bot2 ──┼── target
        │          │
        └── bot3 ──┘
  → Hub central suit 500 bots qui suivent tous la cible

Topologie 2 : Chaîne (Retweet Ring)
  bot1 → RT → bot2 → RT → bot3 → RT → bot4
  → Même contenu amplifié en cascade

Topologie 3 : Grille (Coordinated Network)
  bot1 ── bot2 ── bot3
    │       │       │
  bot4 ── bot5 ── bot6
    │       │       │
  bot7 ── bot8 ── bot9
  → Tous postent le même message au même moment
```

### Détection par Graphe
```python
import networkx as nx

# Analyser la topologie du réseau suspect
def detect_bot_farm(G):
    # 1. Degré entrant/sortant déséquilibré
    in_degrees = dict(G.in_degree())
    out_degrees = dict(G.out_degree())
    
    suspects = []
    for node in G.nodes():
        if out_degrees.get(node, 0) > 100 and in_degrees.get(node, 0) < 5:
            suspects.append(node)  # follow mass, peu suivi
    
    # 2. Densité locale (bot farms = très dense)
    for node in suspects:
        neighbors = list(G.neighbors(node))
        subgraph = G.subgraph(neighbors)
        density = nx.density(subgraph)
        if density < 0.01:  # Pas de liens entre eux = bots indépendants
            suspects.append(node)
    
    # 3. Modularité — si tous dans la même petite communauté
    communities = nx.community.greedy_modularity_communities(G.to_undirected())
    for comm in communities:
        if len(comm) > 50:  # Grande communauté suspecte
            suspects.extend(comm)
    
    return list(set(suspects))
```

---

## 📢 Détection d'Astroturfing

### Signaux d'Astroturfing
| Signal | Description | Détection |
|--------|-------------|-----------|
| Burst synchrone | Soudain, 50 posts sur le même sujet en 5 min | Temporal clustering |
| Copy-paste | Texte identique posté par X comptes | Simhash / MinHash |
| Ratio viral anormal | 1000 RT pour 2 likes | Anomaly detection |
| Coordination temporelle | Tous les comptes postent à :00 ou :30 | Timestamp roundness analysis |
| Réseau cloisonné | Les comptes interagissent uniquement entre eux | Graph community detection |
| Amplification inverse | Les comptes avec peu de followers génèrent soudain une tendance | Imbalance ratio |

### Analyse de Coordination
```python
from collections import Counter
from datetime import datetime, timedelta

def detect_coordinated_burst(posts, time_window=300):
    """
    Détecte les bursts coordonnés :
    - 5+ posts sur le même sujet en < 5 min
    - par des comptes différents
    - avec un texte similaire (> 70% similarité)
    """
    from rapidfuzz import fuzz
    
    bursts = []
    posts_sorted = sorted(posts, key=lambda p: p["timestamp"])
    
    for i in range(len(posts_sorted)):
        window_posts = []
        for j in range(i+1, len(posts_sorted)):
            diff = (posts_sorted[j]["timestamp"] - posts_sorted[i]["timestamp"]).seconds
            if diff > time_window:
                break
            # Similarité de texte
            sim = fuzz.ratio(posts_sorted[i]["text"], posts_sorted[j]["text"])
            if sim > 70:
                window_posts.append(posts_sorted[j])
        
        if len(window_posts) >= 4:  # 5+ posts coordonnés
            bursts.append({
                "time": posts_sorted[i]["timestamp"],
                "count": len(window_posts) + 1,
                "accounts": [p["author"] for p in window_posts],
                "avg_similarity": sim
            })
    
    return bursts
```

---

## 🕵️ Opérations d'Influence (IO)

### Frameworks d'Analyse
| Framework | Source | Usage |
|-----------|--------|-------|
| BEND | https://github.com/avast/BEND | Détection de campagnes |
| Hoaxley | https://github.com/afreen23/hoaxley | Analyse de fake news |
| ClaimBuster | https://idir.uta.edu/claimbuster/ | Fact-checking automatisé |
| Botometer | https://botometer.iu.edu | Score bot Twitter |
| Twitter Auditor | https://github.com/soxoj/twitter-audit | Audit réseau followers |

### Vecteurs d'Influence
```
Étatiques :
  - Internet Research Agency (IRA) — Russie
  - 50 Cent Army — Chine
  - Khalifa AI — Émirats
  - Troll farms iraniens
  - Opérations d'influence nord-coréennes

Commerciaux :
  - Fake reviews (Amazon, Trustpilot, Google)
  - Astroturfing politique
  - Manipulation de cours (crypto, stocks)
  - Réputation laundering

Hybrides :
  - Disinformation as a Service (DaaS)
  - Black PR firms
  - Political consulting (Cambridge Analytica-style)
```

### Analyse de Campagne IO
```python
def analyze_influence_campaign(tweets):
    """Analyse complète d'une campagne suspecte"""
    
    # 1. Accounts analysis
    accounts = set(t["author_id"] for t in tweets)
    new_accounts = sum(1 for a in accounts if account_age(a) < 7)
    
    # 2. Temporal pattern
    timestamps = [t["created_at"] for t in tweets]
    hours = [t.hour for t in timestamps]
    workday_pattern = len([h for h in hours if 9 <= h <= 17])
    night_pattern = len([h for h in hours if h < 6 or h > 23])
    
    # 3. Content similarity
    texts = [t["text"] for t in tweets]
    similarities = [fuzz.ratio(texts[i], texts[i+1]) 
                    for i in range(len(texts)-1)]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    # 4. Network structure
    G = nx.DiGraph()
    for t in tweets:
        if t.get("in_reply_to_user_id"):
            G.add_edge(t["author_id"], t["in_reply_to_user_id"])
    
    return {
        "accounts_analyzed": len(accounts),
        "new_account_ratio": new_accounts / len(accounts),
        "workday_posting": workday_pattern / len(tweets),
        "night_posting": night_pattern / len(tweets),
        "avg_text_similarity": avg_similarity,
        "network_density": nx.density(G) if G.nodes() else 0,
        "likely_campaign": new_accounts > 0.5 or night_pattern > 0.4 or avg_similarity > 0.6
    }
```

---

## 🛠️ Outils de Détection

| Outil | Type | Usage |
|-------|------|-------|
| Botometer | API | Score bot pour comptes Twitter |
| Hoaxy | Web | Visualisation de propagation |
| Bot Sentinel | Web/API | Détection bots Twitter |
| FakeNewsNet | GitHub | Dataset + outils |
| Check | Web | Fact-checking collaboratif |
| InVID | Extension | Vérification vidéo |
| CrowdTangle | Meta | Analyse de contenu viral Facebook |
| Social Blade | Web | Historique de croissance suspecte |
| SparkToro | Pro | Analyse d'audience réelle |

---

## 📊 Rapport de Détection Type

| Métrique | Valeur | Interprétation |
|----------|--------|----------------|
| Bots détectés | 47/1200 comptes (3.9%) | Taux modéré |
| Score bot moyen | 72/100 | Probablement automatisé |
| Topologie | Étoile + Chaîne | Follow farm + RT ring |
| Burst coordonné | 12 occurences | Campaigne active |
| Période suspecte | 02h-05h UTC | Créneaux automatisés |
| Similarité texte | 83% moyenne | Copy-paste massif |
| Origine probable | IP pool 1.2.3.0/24 | Même infrastructure |
| Confiance | HAUTE | Artefacts concordants |

---

## ⚠️ Pitfalls

- **Évolution des bots** : les bots modernes imitent les humains (avatars IA, bio personnalisées, posting irrégulier)
- **Faux positifs** : les comptes très actifs mais légitimes (journalistes, bots utiles) ressemblent à des bots
- **Faux négatifs** : les comptes humains payés (trolls mécaniques) sont indétectables par l'analyse automatisée
- **LLM-powered bots** : les bots utilisant GPT/Claude écrivent comme des humains — la stylométrie ne suffit plus
- **Jeux de données** : Botometer et autres modèles ML ont un taux d'erreur de 15-30%
- **Plateforme** : X/Twitter restreint l'accès aux données depuis 2023, rendant la détection plus difficile