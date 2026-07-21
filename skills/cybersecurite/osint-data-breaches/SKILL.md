---
name: osint-data-breaches
description: Investigation de fuites de données — breach databases, credential leaks, stealer logs, analyse de mots de passe et vérification d'identités compromises.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, data-breach, fuites, mots-de-passe, credentials, leak]
---

# Investigation de Fuites de Données (Data Breaches)

## 🎯 Description

Techniques d'investigation des fuites de données : recherche dans les bases de données de breaches, analyse de credentials exposés, vérification d'emails et mots de passe compromis, exploitation de stealer logs et corrélation multi-sources.

---

## 📋 Outils Essentiels

### Moteurs de Recherche de Breaches
| Outil | URL | Usage |
|-------|-----|-------|
| Have I Been Pwned | https://haveibeenpwned.com | Vérification email (gratuit, 11B+ entrées) |
| DeHashed | https://dehashed.com | Moteur de recherche de breaches (payant) |
| LeakCheck | https://leakcheck.io | 7.5B+ entrées, 3000+ bases |
| Snusbase | https://snusbase.com | Base de données de fuites |
| IntelX | https://intelx.io | Dark web + fuites (payant, version gratuite limitée) |
| LeakRadar | https://leakradar.io | Scan de stealer logs |
| InfoStealers | https://infostealers.info | Index de logs infostealer |
| StealSeek | https://stealseek.io | Moteur de recherche de fuites |
| OsintCat | https://www.osintcat.net | Vérification multi-breaches |
| CheckLeaked | https://checkleaked.cc/ | Email/username/phone dans breaches |
| Venacus | https://venacus.com | Surveillance de fuites |
| IKnowYour.Dad | https://iknowyour.dad/ | Moteur de recherche de fuites |
| CredenShow | https://credenshow.com | Identification credentials compromis |
| HEROIC.NOW | https://heroic.com | Scan identités dark web |
| HIB Ransomed | https://haveibeenransom.com | Vérification ransomwares |

### Outils CLI
| Outil | URL | Usage |
|-------|-----|-------|
| Leaker | https://github.com/vflame6/leaker | Enumération passive sur 10 bases |
| NOX | https://github.com/nox-project/nox-framework | Analyse récursive de breaches |
| h8mail | https://github.com/khast3x/h8mail | Password breach hunting |
| MailAccess | https://github.com/KatrielMoses/MailAccess | Vérification 800+ plateformes + breaches |

### Breaches Spécifiques (Facebook, etc.)
| Outil | URL | Usage |
|-------|-----|-------|
| haveibeenzuckered | https://haveibeenzuckered.com | Breach Facebook 533M comptes |
| Offshore Leak DB | https://offshoreleaks.icij.org | Fuites offshore ICIJ |

---

## 🔧 Méthodologie

### Phase 1 : Vérification Email
```bash
# HIBP API (gratuit, sans clé)
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/email@example.com"

# HIBP avec User-Agent (obligatoire)
curl -s -H "User-Agent: OSINT-Tool" \
  "https://haveibeenpwned.com/api/v3/breachedaccount/email@example.com"

# HIBP - Vérification des mots de passe (k-anonymity)
# Ne jamais envoyer le mot de passe complet
hash=$(echo -n "password123" | sha1sum | cut -c1-5)
curl -s "https://api.pwnedpasswords.com/range/$hash"
```

### Phase 2 : Recherche Multi-Sources
```bash
# Leaker - recherche sur 10 bases simultanément
git clone https://github.com/vflame6/leaker
cd leaker && pip install -r requirements.txt
python3 leaker.py -e email@example.com
python3 leaker.py -u username
```

### Phase 3 : Analyse de Stealer Logs
```bash
# InfoStealers - recherche de logs
# Naviguer sur https://infostealers.info/en/info

# Hudson Rock - recherche dans les infections
# Naviguer sur https://www.hudsonrock.com/threat-intelligence-cybercrime-tools
```

### Phase 4 : Analyse de Mots de Passe
```bash
# h8mail - password breach hunting
pip install h8mail
h8mail -t email@example.com -bc "~/breach_compilation"

# Analyse de patterns de mots de passe
# - Mots de passe réutilisés
# - Variations (2023→2024)
# - Patterns personnels (dates, noms)
```

---

## 📊 Recherche par Domaine

```bash
# Vérifier tous les emails d'un domaine dans les breaches
# DeHashed (Interface web)
# Naviguer sur https://dehashed.com -> Search: @example.com

# Snusbase
# Naviguer sur https://snusbase.com -> Domain search

# API LeakCheck
# curl -s "https://leakcheck.io/api/public?check=@example.com"
```

---

## 🛠️ Analyse de Compromission

### Script de Vérification
```bash
#!/bin/bash
# check_breach.sh
EMAIL="$1"
echo "=== Vérification Breaches pour: $EMAIL ==="

# HIBP
echo "--- HIBP ---"
curl -s -H "User-Agent: OSINT-Check" \
  "https://haveibeenpwned.com/api/v3/breachedaccount/$EMAIL" | \
  python3 -m json.tool 2>/dev/null || echo "Aucune fuite trouvée"

# Vérification pastebins
echo "--- Pastebins ---"
curl -s "https://psbdmp.ws/api/v3/search/$EMAIL" | \
  python3 -m json.tool 2>/dev/null || echo "Aucun résultat"
```

### Vérification k-Anonymity pour Mots de Passe
```bash
#!/bin/bash
# check_password.sh
PASSWORD="$1"
HASH=$(echo -n "$PASSWORD" | sha1sum | awk '{print toupper($1)}')
PREFIX=${HASH:0:5}
SUFFIX=${HASH:5}

# Envoyer seulement les 5 premiers caractères du hash
RESULT=$(curl -s "https://api.pwnedpasswords.com/range/$PREFIX")

# Vérifier si le suffixe apparait
echo "$RESULT" | grep -i "$SUFFIX" && echo "⚠️ MOT DE PASSE COMPROMIS" || echo "✅ Mot de passe non trouvé"
```

---

## 📝 Types de Fuites Courantes

| Type | Description | Exemples |
|------|-------------|----------|
| **Credential stuffing** | Lists d'emails + mots de passe | Collection #1-5, COMB |
| **Stealer logs** | Logs de malware (RedLine, Vidar) | Données de session, cookies |
| **Base de données** | DB complètes exposées | LinkedIn 2012, Facebook 2021 |
| **API leaks** | Données accessibles via API | Twitter, Facebook |
| **Pastebin** | Données postées sur pastebin | Fuites ciblées |
| **Dark web** | Ventes de données sur forums | Marchés noirs |
| **Phishing kits** | Kits de phishing collectés | Credentials récoltés |

---

## 🔗 Corrélation et Enrichissement

```bash
# 1. Trouver un email dans une breach
# 2. Extraire le mot de passe associé
# 3. Chercher cet email sur d'autres plateformes (Holehe)
# 4. Vérifier si le mot de passe est réutilisé ailleurs
# 5. Chercher le nom d'utilisateur associé
# 6. Rechercher l'utilisateur sur les réseaux sociaux
# 7. Croiser avec d'autres fuites
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Légalité** : L'accès à des données volées peut être illégal. Vérifier les lois locales.
- **Fausses fuites** : Certaines "fuites" sont des assemblages de données publiques. Vérifier la source.
- **Données obsolètes** : Les breaches peuvent avoir des années. Les mots de passe ont probablement été changés.
- **Rate limiting** : HIBP limite les requêtes à 1/sec sans clé API. Utiliser une clé API pour les recherches fréquentes.
- **API HIBP** : Nécessite un User-Agent et un header d'API (abonnement).
- **Stockage** : Ne jamais stocker les mots de passe trouvés en clair. Documenter les sources uniquement.

---

## 🔗 Références

- https://haveibeenpwned.com
- https://github.com/khast3x/h8mail
- https://github.com/jivoi/awesome-osint#databreach-search-engines
- https://dehashed.com/