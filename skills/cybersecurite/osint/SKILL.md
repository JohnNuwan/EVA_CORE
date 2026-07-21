---
name: osint
description: Guide complet OSINT (Open Source Intelligence) — techniques, outils, méthodologie, Google Dorking, SOCMINT, sources de données, distributions Linux, et cadre légal.
---

# OSINT — Renseignement en Sources Ouvertes

## Définition

L'OSINT (Open Source INTelligence) est la collecte et l'analyse d'informations
publiquement accessibles. Utilisé en cybersécurité, investigation, journalisme,
et renseignement.

**Principe fondamental** : tout ce qui est public peut être agrégé, corrélé
et analysé pour produire du renseignement actionnable.

---

## Méthodologie OSINT (Cycle du renseignement)

1. **Planification** — Définir l'objectif, le périmètre, les sources cibles
2. **Collecte** — Récupérer les données (scraping, APIs, moteurs de recherche)
3. **Traitement** — Nettoyer, normaliser, structurer les données brutes
4. **Analyse** — Corréler, enrichir, pivoter entre les sources
5. **Diffusion** — Produire un rapport actionnable

---

## Google Dorking (Google Hacking)

Opérateurs de recherche avancée pour affiner les résultats :

```
site:example.com              — Limiter à un domaine
intitle:"index of"            — Chercher dans le titre
inurl:admin                   — Chercher dans l'URL
filetype:pdf confidentiel     — Type de fichier spécifique
cache:example.com             — Version en cache
link:example.com              — Pages liant vers un domaine
related:example.com           — Sites similaires
"chaine exacte"               — Recherche exacte
- exclusion                   — Exclure un terme
* joker                       — Caractère générique
..                            — Plage numérique (ex: 2020..2025)
```

### Exemples de dorks utiles
```
site:*.gov filetype:xls
intitle:"webcam" inurl:/view/
site:pastebin.com "password"
intitle:"index of" "backup"
```

### GhDB — Google Hacking Database
- https://www.exploit-db.com/google-hacking-database

---

## SOCMINT — Social Media Intelligence

### Outils de recherche de profils / pseudos

| Outil | Usage |
|-------|-------|
| **sherlock** | Recherche de pseudos sur 300+ plateformes |
| **maigret** | Fork avancé de Sherlock, plus de sites |
| **blackbird** | Recherche de pseudos (100+ sites) |
| **socialscan** | Vérification rapide d'emails/pseudos |
| **holehe** | Vérifie si un email est inscrit sur des services |
| **whatsmyname** | Recherche de pseudos multi-plateforme |

### Commandes Sherlock
```bash
sherlock pseudo_cible
# ⚠️ --output ne fonctionne qu'avec UN seul pseudo à la fois
sherlock pseudo --csv --output /chemin/fichier.csv --timeout 10
sherlock pseudo --print-found --timeout 8
```

### Commandes Maigret
```bash
maigret pseudo_cible
maigret pseudo --timeout 15 --html --pdf   # Rapport HTML+PDF
maigret pseudo --no-progressbar --print-not-found
# ⚠️ Ne pas utiliser --no-recursive-scan ni -o (n'existent pas)
# ⚠️ PDF nécessite : pip install 'maigret[pdf]'
```

### Commandes Holehe
```bash
holehe email@cible.com
# ⚠️ Un seul email par exécution — Holehe ignore les arguments multiples
# ⚠️ Rate-limiting très agressif sans proxies (80%+ de [x] rate limit)
# Résultats : [+] utilisé, [-] non utilisé, [x] rate limité
```

### Installation rapide sans Docker ni sudo (venv from scratch)
```bash
python3 -m venv ~/lab/tools/venvs/osint --without-pip
source ~/lab/tools/venvs/osint/bin/activate
curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py
pip install sherlock-project maigret holehe socialscan
# theHarvester depuis PyPI (v0.0.1) est cassé → installer depuis GitHub :
# git clone https://github.com/laramies/theHarvester && pip install -e theHarvester/
```

### Outils d'analyse de réseaux sociaux
- **socialblade.com** — Statistiques YouTube/Twitch/Twitter/Instagram
- **xquik.com** — Recherche avancée X/Twitter, export profils, API REST
- **snscrape** — Scraping de tweets, posts, profils sans API
- **instaloader** — Téléchargement de contenu Instagram
- **Tinfoleak** — Analyse de compte Twitter/X

---

## Reconnaissance de domaines et d'infrastructures

### Outils principaux

| Outil | Usage |
|-------|-------|
| **theHarvester** | Emails, sous-domaines, IPs, noms, URLs |
| **Amass (OWASP)** | Cartographie de surface d'attaque, DNS bruteforce |
| **Recon-ng** | Framework modulaire de reconnaissance web |
| **SpiderFoot** | Automatisation OSINT (200+ modules) |
| **Shodan** | Moteur de recherche d'appareils connectés |
| **Censys** | Alternative à Shodan, certificats SSL |
| **Maltego** | Analyse de liens et graphes (Java, GUI) |
| **Subfinder** | Découverte de sous-domaines |
| **httpx** | Sonde HTTP rapide pour domaines |
| **dnsdumpster** | Cartographie DNS visuelle |

### theHarvester — commandes essentielles
```bash
theHarvester -d exemple.com -b google,linkedin,bing,crtsh
theHarvester -d exemple.com -b all -f rapport.html
```

### Shodan — requêtes utiles
```
product:"Apache" country:"FR"
port:3389 country:"FR"
org:"Orange" port:22
title:"webcam"
```

---

## Recherche d'emails et de fuites de données

### Outils de vérification de brèches

| Outil | Usage | Accès |
|-------|-------|-------|
| **HudsonRock API** | ☠️ Infostealer : détecte si un pseudo apparaît dans des logs de malware | Gratuit, API publique |
| **haveibeenpwned.com** | Vérification d'email dans les brèches connues | Gratuit, manuel (Cloudflare anti-bot) |
| **h8mail** | Recherche multi-sources (nécessite clés API) | Gratuit, clés API Dehashed/Snusbase |
| **holehe** | Inscription sur 100+ services | Gratuit mais rate-limiting 80%+ |
| **ghunt** | OSINT Google (comptes, reviews, YouTube) | Gratuit |
| **dehashed.com** | Moteur de recherche de fuites | Payant, Cloudflare anti-bot |
| **leakcheck.io** | Vérification de fuites | Payant, Cloudflare anti-bot |
| **intelx.io** | Moteur de recherche OSINT généraliste | Freemium |

### HudsonRock — Workflow complet avec vérification d'IP

```bash
# Étape 1 — Scanner tous les pseudos de la cible
for pseudo in pseudo1 pseudo2 pseudo3; do
    echo "=== $pseudo ==="
    curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=$pseudo"
done

# Étape 2 — Si compromission détectée, EXTRAIRE l'IP
# Réponse type : "ip": "102.176.**.***"
# → L'IP est partiellement masquée : prendre les 2 premiers octets connus

# Étape 3 — Géolocaliser
curl -s "http://ip-api.com/json/102.176.0.0"
# → country: "Ghana", city: "Accra", isp: "Vodafone Ghana MBB"

# Étape 4 — Identifier le propriétaire
# Extraire le "computer_name" du log → ex: "Nutifafa Collins"
# Rechercher le nom → ex: "Nutifafa Collins Adzadi", étudiant UPSA Ghana

# Étape 5 — Croiser avec la cible
# John habite en France (42) → le Ghana n'est pas sa localisation
# → FAUX POSITIF : le pseudo "korosife" est partagé par deux personnes

# ⚠️ Toujours faire cette vérification avant de signaler une compromission
```

### Pièges spécifiques à l'OSINT téléphonique

- **tellows score 5/9 + tag "Arnaque"** : ne signifie pas forcément que le titulaire est un escroc. Un démarchage sortant ou des appels fréquents suffisent à déclencher le tag.
- **Annuaires obsolètes** : le titulaire affiché peut être l'ancien propriétaire (avant portabilité). Vérifier la date quand c'est possible.
- **Numéro fantôme** (aucune trace) : bon signe pour l'hygiène numérique, mais rend l'OSINT plus difficile — le sujet est discret.
```bash
# API gratuite — à exécuter SYSTÉMATIQUEMENT pour chaque pseudo
curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=<PSEUDO>"

# Résultat type si compromis :
# → {"message": "This username is associated with a computer that was infected...",
#    "stealers": [{"date_compromised": "2023-10-19", "stealer_family": "Lumma",
#    "total_user_services": 56, "top_logins": [...], "top_passwords": [...]}]}

# Si pas de compromission → {"message": "This username is not associated..."}
```

**⚠️ AVANT DE CONCLURE À UNE COMPROMISSION** : toujours vérifier si l'alerte
concerne vraiment le sujet ou un homonyme de pseudo. Workflow :

```
1. Extraire l'IP partiellement masquée (ex: 102.176.**.***)
2. Géolocaliser via ip-api.com : curl "http://ip-api.com/json/102.176.0.0"
3. Vérifier le computer_name (ex: "Nutifafa Collins")
4. Rechercher le nom du propriétaire de la machine sur le web
5. Croiser pays/ville avec la localisation connue du sujet
6. Si divergence → probablement un faux positif (pseudo partagé)
```

### Limites de l'audit automatisé
- **HIBP, BreachDirectory, DeHashed, LeakCheck** : tous protégés par Cloudflare anti-bot
  → curl / automate inefficaces → nécessite vérification manuelle ou clé API payante
- **holehe / socialscan** : rate-limiting massif (80%+ de pertes) sans proxies rotatifs
- **h8mail** : inutilisable sans fichier de config contenant des clés API
| **HudsonRock** | Base infostealer — détecte si un pseudo/email apparaît dans des logs de malware |

---

## Analyse de métadonnées

### ExifTool — le couteau suisse des métadonnées
```bash
# Lire toutes les métadonnées
exiftool image.jpg

# Extraire les coordonnées GPS
exiftool -gps* image.jpg

# Supprimer toutes les métadonnées
exiftool -all= image.jpg

# Écrire une métadonnée
exiftool -Author="Nom" document.pdf

# Traitement par lot
exiftool -all= *.jpg
```

---

## Recherche inversée d'images

| Outil | Usage |
|-------|-------|
| **Google Images** | Recherche inversée classique |
| **Yandex Images** | Souvent meilleur que Google pour les visages |
| **TinEye** | Recherche inversée spécialisée |
| **PimEyes** | Reconnaissance faciale (payant) |
| **FaceCheck.id** | Recherche faciale gratuite |

---

### Géolocalisation d'IP (critique pour audit infostealer)

```bash
# ip-api.com — gratuit, pas de clé API
curl -s "http://ip-api.com/json/102.176.94.176" | python3 -m json.tool
# → country, regionName, city, lat, lon, isp, as

# ipapi.co — gratuit avec rate-limiting
curl -s "https://ipapi.co/102.176.94.176/json/" | python3 -m json.tool
```

**Cas d'usage** : quand HudsonRock détecte un infostealer, l'IP est partiellement
masquée (102.176.\*\*.\*\*\*). Tester les IP de la plage pour géolocaliser
et déterminer si l'infection concerne vraiment le sujet ou un homonyme de pseudo.

### Outils
- **Google Earth Pro** — Imagerie satellite historique
- **Sentinel Hub** — Imagerie satellite ESA
- **Wikimapia** — Cartographie collaborative
- **SunCalc** — Position du soleil pour horodatage
- **Overpass Turbo** — Requêtes OpenStreetMap avancées
- **GeoGuessr** — Entraînement à la géolocalisation

### Vérification de vidéos/images
- Analyser ombres, météo, végétation, plaques d'immatriculation
- Vérifier les métadonnées EXIF/GPS
- Comparer avec Google Street View / Earth
- Utiliser InVID-WeVerify pour l'analyse de vidéos

---

## Dark Web OSINT

| Outil | Usage |
|-------|-------|
| **Tor Browser** | Accès .onion |
| **Ahmia** | Moteur de recherche .onion |
| **DarkSearch** | Moteur de recherche dark web |
| **OnionScan** | Scan de services onion |
| **dark.fail** | Vérification de liens onion valides |

---

## OSINT téléphonique (France)

### Identification de l'opérateur
- **06/07** — Mobile (Orange, SFR, Bouygues, Free)
- **01 à 05** — Géographique (01 Paris, 02 Nord-Ouest, 03 Nord-Est, 04 Sud-Est, 05 Sud-Ouest)
- **09** — VoIP / box internet

### Annuaires inversés
```
# Recherche sur un numéro : essayer plusieurs formats
"0603625116"
"06 03 62 51 16"
"06.03.62.51.16"
"+33603625116"
"0033603625116"
```

### Modèle OSINT téléphonique complet (France)

```bash
# 1. PhoneInfoga (Google Dorks automatisés)
phoneinfoga scan -n "+33603625116" > phoneinfoga.txt

# 2. Tellows (score de réputation + opérateur)
curl -sL "https://www.tellows.fr/num/0603625116" | grep -oP '<title>[^<]+</title>'
# → "Qui m'appelle du 0603625116 de SFR | Score: 5 — Arnaque"

# 3. Annuaires inversés
curl -sL "https://www.telephoneannuaire.fr/directory/listing/COLOMES" | grep "0603625116"
# telephoneannuaire.fr, lannuaire.fr, aquiestcenumero.com

# 4. HudsonRock (infostealer via numéro)
curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=33603625116"
```

### Interprétation tellows
- Score 1-3 : Fiable / personnel
- Score 4-6 : Neutre (démarchage possible)
- Score 7-9 : Indésirable / arnaque avérée
- Le tag "Arnaque" apparaît même pour des scores moyens (5/9) si signalé

### Sources d'annuaires publiques
| Source | Usage | Note |
|--------|-------|------|
| **tellows.fr** | Score + opérateur + commentaires | Le plus fiable |
| **telephoneannuaire.fr** | Nom + ville si listé | Souvent obsolète |
| **lannuaire.fr** | Annuaire inversé | Résultats variables |
| **aquiestcenumero.com** | Avis communautaires | Souvent vide (404) |

### Pièges à éviter
- Un numéro peut avoir été **réattribué** (portabilité) : l'ancien titulaire peut encore apparaître
- Les annuaires gratuits sont souvent **obsolètes** ou incomplets
- La **liste rouge** bloque l'affichage dans les annuaires officiels
- Ne **jamais** appeler le numéro pour vérifier (limite éthique)

---

## Sources spécifiques France

### Registres d'entreprises
| Source | Usage |
|--------|-------|
| **pappers.fr** | Fiches entreprise (SIRET, CA, dirigeants, statuts) |
| **societe.com** | Informations légales, bilans, dirigeants |
| **infogreffe.fr** | Registre du commerce (extraits KBIS) |
| **bodacc.fr** | Annonces légales (créations, radiations) |
| **annuaire-entreprises.data.gouv.fr** | Base SIRENE officielle |

### Immobilier / Cadastre
- **geoportail.gouv.fr** — Cadastre, vues aériennes
- **app.dvf.etalab.gouv.fr** — Transactions immobilières (DVF)
- **google.com/maps** + Street View — Vérification d'adresses

### Divers
- **data.gouv.fr** — Open data français
- **crt.sh** — Certificats SSL (fonctionne pour les domaines .fr aussi)
- **idspectacle.com** — Fiches d'artistes/intermittents du spectacle français (bio, parcours, contacts pro)

---

## Méthodologie pratique d'investigation

### Workflow parallèle (le plus efficace en OSINT sans outils CLI)

Ne pas rechercher séquentiellement. Lancer **toutes les recherches en parallèle**
(nom, pseudo, téléphone, email) puis croiser les résultats.

```
Phase 1 — PARALLÈLE (3-4 recherches simultanées)
  Recherche 1 : "Prénom Nom" entre guillemets
  Recherche 2 : "Pseudo1" OR "Pseudo2"
  Recherche 3 : "0600000000" numéro dans tous les formats
  Recherche 4 : site:linkedin.com "Nom" OR site:github.com "Nom"

Phase 2 — PIVOT (quand un résultat ouvre une piste)
  → LinkedIn trouvé → chercher l'entreprise sur Pappers
  → GitHub trouvé → analyser les repos (langages, centres d'intérêt)
  → Instagram trouvé → extraire les posts publics (lieux, dates, hobbies)
  → Numéro trouvé dans un annuaire → vérifier l'adresse sur geoportail

Phase 3 — CROISEMENT (valider les découvertes)
  → Un nom sur GitHub + un compte Twitter avec la même bio → même personne
  → Une adresse proche d'un employeur → cohérence géographique
  → Des hobbies cohérents entre plateformes → confirmation d'identité

Phase 4 — COMPILATION (rapport structuré)
  → Sections : Identité, Localisation, Réseaux sociaux, Professionnel, Centres d'intérêt
  → Niveau d'exposition (matrice de risque)
  → Recommandations si auto-OSINT
```

### Pièges de l'OSINT sans outils dédiés
- **Homonymes** : "John Moncel" → recensement 1940 Illinois ≠ la cible
- **Numéros réattribués** : le titulaire actuel peut différer de l'annuaire
- **Profils abandonnés** : Google+ (fermé en 2019) → archive, pas un profil actif
- **Casse et accents** : tester "moncel", "Moncel", "MONCEL"
- **Pseudos dérivés du nom** : "jaymoncel" (Jay = J., Moncel), "johnnuwan" (fusion prénoms)
- **Snippets trompeurs** : un résultat de moteur de recherche peut mentionner le bon nom mais concerner une autre personne ; toujours ouvrir la source pour vérifier

### Template de rapport
Voir `references/rapport-type.md` — gabarit de rapport OSINT complet,
basé sur des investigations réelles, avec sections identité, réseaux sociaux,
activité professionnelle, chronologie, exposition et recommandations.

### Retours d'expérience terrain
Voir `references/retours-terrain.md` — patterns découverts lors d'investigations
réelles (pseudos dérivés du nom, rate-limiting Holehe, HudsonRock, etc.).

### APIs et techniques approfondies
Voir `references/api-techniques.md` — endpoints d'API publiques (HudsonRock,
WordPress REST, TikTok oEmbed, Deezer, ip-api), quirks des outils, signaux
faibles, et techniques d'extraction de contenu JS. À consulter quand le scan
automatisé superficiel ne suffit pas.

---

## Pièges et limites (TERRAIN — ne pas ignorer)

### ⛔ Instagram bloqué sans authentification
**Depuis 2024, Meta verrouille tout.** Instaloader, oEmbed, browser, tout
renvoie 403/login wall. Sans cookies exportés ou token Facebook Graph,
**aucune photo Instagram** n'est récupérable automatiquement.

### ☁️ Sites de breach check derrière Cloudflare
HIBP, BreachDirectory, DeHashed, LeakCheck → tous protégés. Prioriser
**HudsonRock API** (pas de Cloudflare) et la vérification manuelle.

### 🎭 Homonymes de pseudo
Un pseudo peut être utilisé par plusieurs personnes. **Toujours** vérifier
la géolocalisation de l'IP HudsonRock avant de conclure à une compromission.

### 📸 Photos : contre-mesures
- Instagram → bloqué (auth obligatoire)
- TikTok → gallery-dl ou oEmbed (thumbnail_url)
- YouTube → yt-dlp --write-thumbnail (⚠️ chaînes parfois 404)
- SoundCloud → grep les avatars dans le HTML de la page
- GitHub → `curl https://avatars.githubusercontent.com/u/<ID>`

### 🐦 Quirks des outils
- Sherlock `--output` → UN seul pseudo à la fois
- Maigret `-o` n'existe pas → utiliser `--html --pdf`
- Holehe → UN seul email par exécution, 80%+ rate-limit sans proxies
- theHarvester PyPI v0.0.1 → cassé, installer depuis GitHub avec `pip install -e .`

Référence complète : [[references/pieges-limites.md]]

---

## Obsidian Vault & Standards OKF

Pour structurer les connaissances et rapports, utiliser le vault Obsidian
dans `~/lab/knowledge/obsidian-cybersecurite/` avec :
- **MOC** (Map of Content) comme point d'entrée
- **Datapackages OKF** (Frictionless Data) pour les données brutes
- **Templates standardisés** pour les rapports d'investigation  
- **Wikilinks** pour interconnecter les concepts (`[[03-Metasploit]]` → `[[04-Privilege-Escalation]]`)

Architecture `~/lab/` (style DeepMind) : tools/ (venvs, Go, binaires), data/osint/ (données par cible), knowledge/ (vault), projects/, configs/, scripts/.

Activation : `source ~/lab/tools/venvs/osint/bin/activate && export PATH=$HOME/lab/tools/bin:$HOME/lab/tools/go/bin:$HOME/lab/tools/go-workspace/bin:$PATH`

Détail : [[references/obsidian-okf.md]]
Script : [[references/sync-obsidian.md]]

| Distribution | Usage |
|-------------|-------|
| **Tails** — Amnésie, Tor par défaut |
| **Qubes OS** — Isolation par VM |
| **Parrot Security** — OSINT + pentest intégrés |
| **CSI Linux** — Distribution dédiée à l'OSINT |
| **Tsurgi Linux** — Forensique et OSINT |
| **TraceLabs VM** — VM OSINT pour équipes |

---

## Cadre légal et éthique

### Principes éthiques absolus
1. **Utiliser uniquement des sources publiquement accessibles**
2. **Ne pas usurper d'identité ni contourner l'authentification**
3. **Pas de doxxing, harcèlement, ou divulgation malveillante**
4. **Minimiser la collecte de données personnelles**
5. **Documenter la finalité légitime de la recherche**

### RGPD / GDPR (UE)
- Même les données publiques sont soumises au RGPD
- Base légale nécessaire : consentement, intérêt légitime, etc.
- Obligation de transparence et minimisation

### CFAA (États-Unis)
- Interdit l'accès non autorisé aux systèmes informatiques
- L'OSINT sur sources publiques est légal
- Le contournement d'authentification est illégal

---

## Ressources communautaires

- **Bellingcat** — https://www.bellingcat.com
- **IntelTechniques** — https://inteltechniques.com
- **OSINT Framework** — https://osintframework.com
- **r/OSINT** — Reddit
- **SANS OSINT** — https://www.sans.org/blog/osint
- **TraceLabs** — CTF OSINT humanitaire
- **Sector035** — https://sector035.nl

---

## Cheatsheet rapide de workflow OSINT complet

```bash
# 0. PRÉREQUIS — Installer les outils (sans Docker ni sudo)
python3 -m venv ~/lab/tools/venvs/osint --without-pip
source ~/lab/tools/venvs/osint/bin/activate
curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py
pip install sherlock-project maigret holehe socialscan
# theHarvester depuis GitHub (PyPI v0.0.1 est cassé) :
# git clone https://github.com/laramies/theHarvester && pip install -e theHarvester/

# 1. Recherche de domaine (si cible = entreprise)
theHarvester -d cible.com -b all
amass enum -d cible.com
subfinder -d cible.com

---

## Outils OSINT avancés installés (~/lab/tools/venvs/osint + ~/lab/tools/go-workspace)

### Téléphone
- **PhoneInfoga** (`phoneinfoga scan -n "<numéro>"`) — Google Dorks spécialisés, OVH, numverify, localisation

### Réseaux sociaux
- **GHunt** (`ghunt email <email>`) — OSINT Google (comptes, reviews, Maps, YouTube)
- **Instaloader** (`instaloader profile <user>`) — Scraping Instagram (⚠️ bloqué sans auth)
- **snscrape** (`snscrape twitter-search "query"`) — Scraping Twitter/X, Instagram, Reddit
- **Toutatis** (`toutatis -u <username>`) — OSINT Instagram

### Infrastructure
- **Subfinder** (`subfinder -d <domaine>`) — Découverte de sous-domaines
- **Httpx** (`httpx -l <fichier_urls>`) — Probing HTTP
- **Naabu** (`naabu -host <IP>`) — Scan de ports rapide

### Automatisation
- **BBoT** (`bbot -t <cible> scan`) — Recon multi-cibles, 50+ modules
- **Sherlock** — Recherche pseudos (déjà installé)
- **Maigret** — Recherche pseudos avancée (déjà installé)
- **Holehe** — Vérification email (déjà installé)

### Commandes utiles
```bash
# Activer l'environnement
source ~/lab/tools/venvs/osint/bin/activate
export PATH=$HOME/lab/tools/bin:$HOME/lab/tools/go/bin:$HOME/lab/tools/go-workspace/bin:$PATH

# Téléphone
phoneinfoga scan -n "+336XXXXXXXX"

# Google OSINT
ghunt email cible@gmail.com

# Twitter/X
snscrape twitter-user nom_utilisateur
snscrape twitter-search "mot clé" > tweets.txt

# Infrastructure (binaires Go)
subfinder -d exemple.com
httpx -l sous_domaines.txt
naabu -host 192.168.1.1

# Automatisation globale
bbot -t exemple.com -m osint scan
```

## Cheatsheet rapide de workflow

```bash
# 1. Recherche de domaine
theHarvester -d cible.com -b all
~/osint-env/bin/subfinder -d cible.com

# 2. Vérification de pseudos
sherlock pseudo_cible
holehe email@cible.com

# 3. Téléphone
phoneinfoga scan -n "+336XXXXXXXX"

# 4. Google OSINT
ghunt email cible@gmail.com

# 5. Analyse d'images
exiftool image.jpg
# Recherche inversée sur Yandex + Google

# 6. Infrastructure
~/osint-env/bin/httpx -l urls.txt
~/osint-env/bin/naabu -host IP

# 7. Scraping réseaux sociaux
snscrape twitter-search "mot clé"
instaloader profile cible
```

## Arsenal OSINT complet — Installation sans Docker ni sudo

Tous les outils ci-dessous sont installables sur une machine Linux standard
sans privilèges root. La procédure complète est documentée dans
`references/installation-arsenal.md`.

### Vue d'ensemble de l'arsenal (~/lab/tools/venvs/osint + ~/lab/tools/go-workspace)

| Catégorie | Outil | Emplacement | Type |
|-----------|-------|-------------|------|
| 👤 Pseudos | **Sherlock** | pip | 350+ sites |
| 👤 Pseudos | **Maigret** | pip | 509 sites + rapports HTML |
| ✉️ Email | **Holehe** | pip | 121 sites (rate-limité sans proxies) |
| ✉️ Email | **theHarvester** | git+pip | emails, sous-domaines (v4.11.1) |
| 📱 Téléphone | **PhoneInfoga** | Go binary | Google Dorks, OVH, carrier |
| 📱 Téléphone | **Toutatis** | pip | OSINT Instagram + phone |
| 🔍 Google | **GHunt** | pip | Comptes Google, Maps, YouTube |
| 📸 Instagram | **Instaloader** | pip | Scraping posts, followers |
| 🐦 Twitter/X | **snscrape** | pip | Scraping sans API |
| 🤖 Automatisation | **BBoT** | pip | 50+ modules de recon |
| 🕸️ Automatisation | **SpiderFoot** | git | 200+ modules (`sf.py`) |
| 🔧 Framework | **Recon-ng** | git | Framework modulaire |
| 🌐 DNS | **Amass** | Go | Cartographie DNS OWASP |
| 🌐 Sous-domaines | **Subfinder** | Go | ProjectDiscovery |
| 🌐 Probing | **Httpx** | Go | HTTP rapide |
| 🌐 Scan | **Naabu** | Go | Scan de ports |
| 🎯 Vulns | **Nuclei** | Go | Scanner YAML (178 MB) |
| ☠️ Infostealer | **HudsonRock** | API curl | Détection malware |

### Commandes rapides (tout-en-un)

```bash
# Activer l'environnement
source ~/lab/tools/venvs/osint/bin/activate
export PATH=$HOME/lab/tools/bin:$HOME/lab/tools/go/bin:$HOME/lab/tools/go-workspace/bin:$PATH

# Téléphone
phoneinfoga scan -n "+336XXXXXXXX"

# Email
holehe email@cible.com
ghunt email email@gmail.com

# Pseudos
sherlock pseudo --timeout 10 --print-found
maigret pseudo --timeout 15

# Instagram (⚠️ nécessite souvent authentification)
instaloader profile pseudo
toutatis -u pseudo

# Brèches (PRIORITAIRE)
curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=<PSEUDO>"

# Infrastructure
amass enum -d domaine.com
subfinder -d domaine.com
httpx -l sous_domaines.txt

# Full auto
bbot -t cible.com -m osint scan
python3 ~/lab/tools/venvs/osint/spiderfoot/sf.py -l 127.0.0.1:5001  # GUI web

# OSINT téléphone complet
phoneinfoga scan -n "+336..." > ~/lab/data/osint/cible/donnees_brutes/phoneinfoga.txt
# Vérifier aussi tellows.fr, telephoneannuaire.fr, lannuaire.fr
```

### Arborescence recommandée pour chaque cible

```
~/lab/data/osint/<cible>/
├── avatars/          # Photos de profil téléchargées
├── donnees_brutes/   # Sorties brutes des outils (.txt, .html)
├── photos/           # Posts, stories, images
└── rapports/         # Rapports Markdown compilés
    ├── 01_analyse_manuelle.md
    └── 02_rapport_final.md
```
