---
name: osint-username-hunting
description: Recherche et traçage de pseudos/noms d'utilisateur à travers les plateformes — Sherlock, Maigret, Blackbird, WhatsMyName.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, username, pseudonyme, identification, comptes, cross-platform]
---

# Username Hunting (Chasse aux Pseudos)

## 🎯 Description

Traçage d'un nom d'utilisateur (username) à travers des centaines de plateformes pour identifier les comptes associés, cartographier la présence en ligne d'une cible et relier des identités numériques dispersées.

---

## 📋 Outils Essentiels

### Moteurs de Recherche de Username
| Outil | URL | Sites | Usage |
|-------|-----|-------|-------|
| Sherlock | https://github.com/sherlock-project/sherlock | +400 | CLI Python, résultats rapides |
| Maigret | https://github.com/soxoj/maigret | +2500 | Dossier complet avec capture d'écran |
| Blackbird | https://github.com/p1ngul1n0/blackbird | +600 | Recherche username + email + téléphone |
| WhatsMyName | https://whatsmyname.app/ | +400 | Interface web + API |
| Social Analyzer | https://github.com/qeeqbox/social-analyzer | +1000 | API, CLI, Web |
| User Search | https://www.usersearch.org | +3000 | Web, recherche multi-type |
| User Searcher | https://www.user-searcher.com | +2000 | Web, gratuit |
| Name Chk | https://www.namechk.com | 90+ | Web, domaines + réseaux |
| Snoop | https://github.com/snooppr/snoop | Web | Recherche de nickname |
| Nexfil | https://github.com/thewhiteh4t/nexfil | +350 | CLI rapide |
| Digital Footprint Check | https://www.digitalfootprintcheck.com/free-checker.html | +100 | Web gratuit |
| Seekr | https://github.com/seekr-osint/seekr | Multi | Toolkit avec interface web |
| Antisocial | https://github.com/lukeslp/antisocial | +30/500 | Vérification 3 niveaux |

### Outils Web
| Outil | URL | Usage |
|-------|-----|-------|
| IDCrawl | https://www.idcrawl.com/username | Recherche username |
| CheckUser | https://checkuser.vercel.app/ | Recherche username |
| Name Checkup | https://namecheckup.com | Username + domaine |
| NameKetchup | https://nameketchup.com | Username + domaine |
| Name Checkr | https://www.namecheckr.com | Domaine + username |

---

## 🔧 Installation et Utilisation

### Sherlock
```bash
# Installation
pip install sherlock

# Usage basique
sherlock username

# Sauvegarde en HTML
sherlock username --output output.html

# Recherche de tous les sites (par défaut)
sherlock username --all

# Fichier de timeout
sherlock username --timeout 30

# Recherche par fichier
sherlock --file list_of_usernames.txt
```

### Maigret (Recommandé pour investigations poussées)
```bash
# Installation
pip install maigret

# Usage basique
maigret username

# Rapport HTML complet avec captures d'écran
maigret username --html

# Recherche d'emails associés
maigret username --email-check

# Recherche d'URLs de profil
maigret username --all

# Recherche d'activité récente
maigret username --timeout 60

# Exporter en JSON
maigret username --json
```

### Blackbird
```bash
# Installation
git clone https://github.com/p1ngul1n0/blackbird
cd blackbird
pip install -r requirements.txt

# Username
python blackbird --username username

# Email
python blackbird --email email@example.com

# Téléphone
python blackbird --phone "+33612345678"
```

### WhatsMyName (Web)
```bash
# Naviguer sur https://whatsmyname.app/
# Entrer le username
# L'outil vérifie sur +400 sites automatiquement
```

### Social Analyzer
```bash
# Installation
git clone https://github.com/qeeqbox/social-analyzer
cd social-analyzer && npm install

# Lancer le serveur web
npm start

# CLI
node app.js --username username
```

---

## 📊 Techniques Avancées

### Recherche par Variations
```bash
# Variations courantes d'un username
username
username_
_username
username123
therealusername
officialusername
username_real
usernameofficial
username.alt
xusername
usernamex
```

### Corrélation Multi-Plateforme
```bash
# 1. Lancer Sherlock sur le username principal
sherlock username

# 2. Pour chaque profil trouvé, extraire :
#    - Bio/description
#    - Avatar (reverse image search)
#    - Liens vers d'autres profils
#    - Date de création du compte
#    - Followers/Following

# 3. Lancer Maigret pour un rapport détaillé
maigret username --html

# 4. Chercher les variations
for u in username1 username2 username3; do
    sherlock "$u" --output "output_$u.txt"
done
```

### Analyse des Résultats
```bash
# Filtrer les résultats (exclure les sites morts)
grep -v "Error" output.txt

# Extraire les URLs de profil
grep -oP 'https?://[^ ]+' output.txt

# Vérifier manuellement les meilleurs résultats
# - Profils avec photo de profil
# - Profils avec bio complète
# - Comptes avec activité récente
# - Comptes avec followers
```

---

## 🛠️ Script Automatisé

```bash
#!/bin/bash
# multi_username_check.sh
USERNAMES=("$@")
for username in "${USERNAMES[@]}"; do
    echo "=== Checking: $username ==="
    maigret "$username" --json > "maigret_${username}.json"
    python3 -c "
import json
with open('maigret_${username}.json') as f:
    data = json.load(f)
    for site, info in data['sites'].items():
        if info.get('status') == 'claimed':
            print(f'  ✓ {site}: {info.get(\"url\")}')
    "
    sleep 5
done
```

---

## 📝 Analyse d'un Profil Trouvé

Lorsqu'un profil est trouvé, collecter :

```text
1. URL du profil
2. Nom d'utilisateur exact
3. Nom complet (si disponible)
4. Bio / description
5. Photo de profil → Reverse image search
6. Date de création du compte
7. Nombre de followers / following
8. Liste des posts / tweets publics
9. Liens externes (site web, autres réseaux)
10. Localisation déclarée
11. Langue utilisée
12. Centres d'intérêt
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Rate limiting** : Maigret et Sherlock peuvent être bloqués après trop de requêtes. Utiliser `--timeout` et des délais entre les runs.
- **Faux positifs** : Certains sites retournent des pages d'erreur personnalisées qui ressemblent à des profils. Vérifier manuellement.
- **Sites morts** : Beaucoup de sites dans les bases de données peuvent ne plus exister. Filtrer les résultats.
- **Comptes dormants** : Un compte peut exister sans activité depuis des années. Vérifier la date du dernier post.
- **Anonymat** : Les requêtes sont visibles par les plateformes. Utiliser Tor pour les investigations sensibles.
- **Mises à jour** : Les outils évoluent vite. `pip install --upgrade maigret sherlock` régulièrement.

---

## 🔗 Références

- https://github.com/sherlock-project/sherlock
- https://github.com/soxoj/maigret
- https://github.com/p1ngul1n0/blackbird
- https://whatsmyname.app/
- https://github.com/jivoi/awesome-osint#username-check