---
name: socmint-cross-platform-profiling
description: SOCMINT — corrélation d'identités cross-platform, reconstruction de persona, cartographie d'empreinte numérique multi-réseaux.
category: cybersecurite
author: EVA
version: 1.0
tags: [socmint, profiling, identité, cross-platform, digital-footprint, persona]
---

# SOCMINT : Profilage Cross-Platform

## 🎯 Description

Corrélation systématique d'identités numériques à travers l'ensemble des plateformes sociales. Reconstruction complète de persona à partir de fragments dispersés : mapping username/email/téléphone, consolidation de profils, analyse de recouvrement, identification de comptes dormants et détection de comptes alias/secondaires.

Contrairement à la simple chasse aux usernames (osint-username-hunting), ce skill couvre la **phase d'analyse** : relier, infirmer/confirmer, et cartographier les identités avec certitude.

---

## 📋 Vecteurs de Corrélation

### 1. Username → Multi-Plateformes
| Méthode | Description | Outil |
|---------|-------------|-------|
| Scan direct | Recherche du même pseudo sur 2000+ sites | Maigret, Sherlock, Blackbird |
| Variation | username, username_, _username, username1, realusername | Générateur manuel + Sherlock |
| Levenshtein | Distance d'édition entre pseudos proches | script custom fuzzy match |
| Soundex/Metaphone | Similarité phonétique (ex: @jhon → @john) | phonetics lib Python |

### 2. Email → Comptes Associés
| Outil | URL | Usage |
|-------|-----|-------|
| Holehe | https://github.com/megadose/holehe | Vérifie si email lié à 120+ services |
| GHunt | https://github.com/mxrch/GHunt | Renseignements Google associés |
| Maigret | https://github.com/soxoj/maigret | Recherche email sur 2500+ sites |
| DeHashed | https://dehashed.com | Fuites de données (payant) |
| IntelX | https://intelx.io | Recherche email multi-sources |
| Epieos | https://epieos.com | Recherche email gratuite |
| Hunter.io | https://hunter.io | Vérification format + domaines |

### 3. Téléphone → Profils Sociaux
| Outil | URL | Usage |
|-------|-----|-------|
| PhoneInfoga | https://github.com/sundowndev/phoneinfoga | OSINT téléphone avancé |
| Truecaller | https://www.truecaller.com | Identification appelant |
| Numverify | https://numverify.com | Validation + opérateur |
| Blackbird | https://github.com/p1ngul1n0/blackbird | Recherche téléphone cross-platform |

### 4. Avatar/Photo → Reverse Image
| Outil | URL | Usage |
|-------|-----|-------|
| PimEyes | https://pimeyes.com | Recherche faciale multi-sites |
| FaceCheck.ID | https://facecheck.id | Reconnaissance faciale social media |
| Google Images | https://images.google.com | Reverse image search standard |
| TinEye | https://tineye.com | Recherche par image sans IA |

---

## 🔬 Méthodologie de Corrélation

### Niveaux de Certitude
```
CONFIRMÉ    = 3+ signaux concordants (même username + email + avatar + bio)
PROBABLE    = 2 signaux forts (même username + même fuseau horaire de posting)
POSSIBLE    = 1 signal fort ou 2 faibles (username proche + même centre d'intérêt)
CONTRE-IND  = Preuve d'identité différente (contradiction temporelle, lieu incompatible)
```

### Matrice de Corrélation
Créer une table 5×5 pour chaque cible :

```
            Twitter  Insta  LinkedIn  Reddit  Telegram
Twitter       ✓      bio     nom       liens    @handle
Insta        style    ✓     école     hashtag  stories
LinkedIn     emploi  lieux    ✓       tech     groupe pro
Reddit       sujets  photos  langues    ✓      channel
Telegram     @ident  média  groupe    invite     ✓
```

### Techniques de Cross-Reference
1. **Bio cross-check** : une bio identique ou similaire sur 2+ plateformes → fort signal
2. **Horodatage** : photos publiées au même moment sur Instagram et Twitter → même personne
3. **Graphe d'amis** : mêmes abonnements/abonnés → clusters identitaires
4. **Style rédactionnel** : mêmes tournures, emojis récurrents, fautes → stylométrie
5. **Localisation** : check-in, géotags, fuseau horaire des posts → corrélation géographique
6. **Liens croisés** : profil A linktree → profil B → profil C → chaîne complète

---

## 🛠️ Workflow de Profilage

### Phase 1 : Collecte Initiale
```bash
# 1. Scanner le username
maigret target_username --all --output maigret_report.html

# 2. Vérifier l'email
holehe target@email.com

# 3. Recherche téléphone
phoneinfoga scan -n "+33612345678"

# 4. Reverse image de l'avatar
# Soumettre manuellement sur PimEyes + Google Images

# 5. Recherche dans les fuites
# https://dehashed.com ou https://intelx.io
```

### Phase 2 : Analyse des Résultats
```python
# Exemple : script de fuzzy matching des pseudos
from rapidfuzz import fuzz

usernames = ["john_doe", "john.doe", "johndoe", "johnnydoe", "jdoe_official"]
target = "johndoe"

for u in usernames:
    score = fuzz.ratio(target, u)
    print(f"{u}: {score}%")
    # >80% = variation probable, >95% = même compte
```

### Phase 3 : Vérification et Confirmation
1. **Check temporel** : le compte B postait-il quand le compte A était inactif ?
2. **Check stylométrique** : même signature d'écriture (longueur, emojis, hashtags)
3. **Check réseau** : partagent-ils des abonnés communs ?
4. **Check URL** : le profil X link vers le profil Y ?

---

## 📊 Matrice pour Rapport

| Élément | Plateforme | Username | Certitude | Preuve |
|---------|-----------|----------|-----------|--------|
| Identité primaire | X/Twitter | @johndoe | Référence | — |
| Alias 1 | Instagram | john.doe | CONFIRMÉ | Même bio + avatar |
| Alias 2 | Reddit | johndoe88 | PROBABLE | Mêmes centres d'intérêt |
| Alias 3 | LinkedIn | John Doe | CONFIRMÉ | Email identique |
| Fantôme | Telegram | jd_2024 | POSSIBLE | Username proche |
| Compte dormant | Tumblr | johnnydoe | CONTRE-IND | Activité 2018, autre ville |

---

## 🔗 Outils Complémentaires

| Outil | URL | Usage SOCMINT |
|-------|-----|---------------|
| SpiderFoot | https://github.com/smicallef/spiderfoot | Automatisation multi-source |
| Recon-ng | https://github.com/lanmaster53/recon-ng | Framework OSINT modulaire |
| Maltego | https://www.maltego.com | Graphe de corrélation visuel |
| theHarvester | https://github.com/laramies/theHarvester | Collecte emails/noms/ips |
| Sn0int | https://github.com/kpcyrd/sn0int | OSINT semi-automatisé |
| Holehe | https://github.com/megadose/holehe | Email → services |
| WhatsMyName | https://whatsmyname.app/ | Web username checker |

---

## ⚠️ Pitfalls

- **Faux positifs** : un même username peut appartenir à 2 personnes différentes (homonyme)
- **Comptes abandonnés** : un profil sans activité depuis 5 ans n'est plus représentatif
- **Usurpation** : les comptes fan/clone/fake reproduisent bio + avatar de la cible
- **Limitation API** : X/Twitter limite fortement le scraping depuis 2023
- **Anti-SOCMINT** : certaines cibles utilisent des pseudos différents par plateforme intentionnellement
- **Privacy sandbox** : Apple/iOS, Android 14+ empêchent le tracking cross-app