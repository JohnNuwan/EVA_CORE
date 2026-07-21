---
name: socmint-behavioral-analysis
description: SOCMINT — analyse comportementale, pattern-of-life, rythmes de publication, stylométrie, fingerprinting numérique et profilage psychologique via social media.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, behavioral-analysis, pattern-of-life, stylométrie, psychographie, fingerprinting]
---

# SOCMINT : Analyse Comportementale

## 🎯 Description

Analyse des patterns comportementaux sur les réseaux sociaux : rythmes de publication, style rédactionnel (stylométrie), horaires d'activité, centres d'intérêt récurrents, réseau lexical, évolution temporelle du discours, et reconstruction du **pattern-of-life** numérique d'une cible.

Contrairement aux techniques de collecte statique, l'analyse comportementale permet de **prédire** les actions futures, **identifier** les changements d'état psychologique, et **profiler** la cible au-delà de ses déclarations explicites.

---

## 📋 Axes d'Analyse Comportementale

### 1. Chronobiologie Sociale (Rythmes de Publication)
| Paramètre | Analyse | Interprétation SOCMINT |
|-----------|---------|------------------------|
| Heures de posting | Histogramme 24h | Fuseau horaire = localisation probable |
| Jours de la semaine | Distribution jour/jour | Loisir ↔ travail, week-end ↔ semaine |
| Pics d'activité | Détection de clusters temporels | Moments de vulnérabilité (réponse rapide) |
| Pauses | Silence > 48h | Vacances, événement, hospitalisation, arrestation |
| Saisonnalité | Patterns mensuels/saisonniers | Routines professionnelles ou scolaires |

### 2. Stylométrie (Signature d'Écriture)
| Trait | Métrique | Outil |
|-------|----------|-------|
| Longueur moyenne | Mots par post | Script Python NLTK |
| Vocabulaire | Richesse lexicale, type/token ratio | `nltk.Text.lexical_diversity()` |
| Ponctuation | Fréquence !, ?, ..., — | Regex counting |
| Emojis | Catalogue d'emojis récurrents | `emoji` library |
| Hashtags | Fréquence, thèmes, format (PascalCase, lowercase) | Regex extraction |
| Fautes | Orthographe, répétitions | LanguageTool API |
| Syntaxe | Longueur de phrases, complexité | SpaCy dependency parsing |
| Majuscules | FRÉQUENCE DES CAPS, cAmElCaSe | Pattern matching |

### 3. Analyse Thématique
| Technique | Bibliothèque | Usage |
|-----------|-------------|-------|
| LDA Topic Modeling | `gensim` | Extraction de sujets latents |
| BERT Topic | `bertopic` | Clustering sémantique avancé |
| TF-IDF | `sklearn` | Mots-clés caractéristiques |
| Sentiment Analysis | `transformers` (camembert, roBERTa) | Évolution émotionnelle |
| NER | `spaCy` | Entités nommées récurrentes |

### 4. Analyse Relationnelle
- **@mentions** : qui est cité, à quelle fréquence
- **Replies vs RT** : ratio de conversation vs amplification
- **Threads** : profondeur des conversations, qui répond à qui
- **Communautés d'interaction** : clustering des interlocuteurs réguliers

---

## 🔬 Workflow d'Analyse Comportementale

### Phase 1 : Collecte Temporelle
```python
import pandas as pd
import json
from datetime import datetime

# Posts déjà collectés (ex: export Twitter)
with open("posts.json") as f:
    posts = json.load(f)

df = pd.DataFrame(posts)
df["created_at"] = pd.to_datetime(df["created_at"])
df["hour"] = df["created_at"].dt.hour
df["day"] = df["created_at"].dt.day_name()
df["date"] = df["created_at"].dt.date

# Histogramme 24h
hourly = df.groupby("hour").size()
print("Pic d'activité:", hourly.idxmax(), "h ->", hourly.max(), "posts")

# Activité par jour
daily = df.groupby("day").size().sort_values()
print("Jour le plus actif:", daily.idxmax())

# Détection de silence
df["gap_hours"] = df["created_at"].sort_values().diff().dt.total_seconds() / 3600
long_silences = df[df["gap_hours"] > 48]
print(f"Silences > 48h: {len(long_silences)} occurences")
```

### Phase 2 : Stylométrie
```python
import nltk
from collections import Counter
import re

texts = df["text"].tolist()
all_words = " ".join(texts)

# Métriques basiques
avg_length = sum(len(t.split()) for t in texts) / len(texts)
print(f"Longueur moyenne: {avg_length:.1f} mots")

# Emojis
emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
all_emojis = [c for t in texts for c in t if c in emoji_pattern]
emoji_freq = Counter(all_emojis).most_common(10)
print("Top emojis:", emoji_freq)

# Ponctuation intense
excited = sum(1 for t in texts if "!!!" in t)
print(f"Posts avec !!! : {excited}")

# Hashtags
hashtags = re.findall(r"#(\w+)", " ".join(texts))
tag_freq = Counter(h.lower() for h in hashtags).most_common(20)
print("Top hashtags:", tag_freq)
```

### Phase 3 : Analyse de Sentiment Temporel
```python
from transformers import pipeline

sentiment = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")
# Pour le français : "nlptown/bert-base-multilingual-uncased-sentiment"

df["sentiment"] = df["text"].apply(lambda x: sentiment(x[:512])[0]["label"])
df["score"] = df["text"].apply(lambda x: sentiment(x[:512])[0]["score"])

# Évolution du sentiment dans le temps
sentiment_timeline = df.groupby("date")["sentiment"].value_counts().unstack()

# Détection d'événements émotionnels
df["emotional_shift"] = df["score"].diff().abs() > 0.5
events = df[df["emotional_shift"]]
print(f"Changements émotionnels brutaux: {len(events)}")
```

---

## 🧠 Psycho-Profiling via Social Media

### Dimensions Psychographiques
| Dimension | Indicateurs Sociaux | Corrélation |
|-----------|---------------------|-------------|
| Ouverture | Vocabulaire riche, sujets variés, art/philo | Haut TTR |
| Conscienciosité | Horaires réguliers, orthographe soignée | Faible variance temporelle |
| Extraversion | Beaucoup d'@mentions, réponses rapides, selfies | Ratio interaction/émission élevé |
| Agréabilité | Émoticônes positives, remerciements, support | Sentiment positif dominant |
| Névrosisme | Postes tardifs, émotions négatives, sautes d'humeur | Haute variance sentiment |

### Détection de Changements d'État
| Signal | Indicateur | Interprétation |
|--------|-----------|----------------|
| Silence soudain | Arrêt >7 jours sans raison | Dépression, hospitalisation, arrestation |
| Changement de fuseau | Posts soudainement à des heures différentes | Voyage, déménagement, décalage horaire |
| Pic négatif | Série de posts négatifs en 24h | Crise personnelle, burn-out |
| Changement stylistique | Évolution brutale du vocabulaire | Nouveau rédacteur, compte compromis |
| Désactivation soudaine | Compte passé privé ou supprimé | Évitement, menace perçue |

---

## 📋 Outils d'Analyse Comportementale

| Outil | URL | Usage SOCMINT |
|-------|-----|---------------|
| Social-Bearing | https://socialbearing.com | Analyse Twitter gratuite |
| TweetBinder | https://www.tweetbinder.com | Analyse hashtag/campagne |
| Foller.me | https://foller.me | Analyse profil Twitter |
| Sociograph | https://www.sociograph.io | Analyse Instagram |
| SparkToro | https://sparktoro.com | Audience intelligence |
| Brandwatch | https://www.brandwatch.com | Social listening pro |
| Talkwalker | https://www.talkwalker.com/fr | Social analytics |
| Crimson Hexagon | https://www.crimsonhexagon.com | Analyse de conversation |

---

## 📊 Rapport Type

| Métrique Comportementale | Valeur |
|--------------------------|--------|
| Fuseau horaire probable | UTC+1 (Paris) |
| Pics d'activité | 12h-14h, 21h-23h |
| Jour le plus actif | Dimanche |
| Silence max | 72h (août 2024) |
| Longueur moyenne | 142 caractères |
| Ratio replies/RT | 0.8 (plutôt conversation) |
| Sentiment dominant | Neutre (58%), Positif (32%), Négatif (10%) |
| Top 3 sujets | Tech, politique, voyages |
| Stabilité émotionnelle | Modérée (6 shifts brutaux en 6 mois) |
| Évolution temporelle | Discours polarisé croissant (2024→2025) |

---

## ⚠️ Pitfalls

- **Comptes multi-utilisateurs** : un profil géré par une équipe (community manager) fausse la stylométrie
- **Période d'échantillonnage** : 1 semaine de données ne suffit pas — minimum 3 mois
- **Biais de plateforme** : le comportement Twitter diffère du comportement Instagram
- **Outils automatisés** : les posts programmés (Buffer, Hootsuite) masquent le rythme réel
- **Changement de vie** : un déménagement, un nouvel emploi changent légitimement les patterns
- **Éthique** : le profilage psychologique via social media est régulé (RGPD, CC PA)