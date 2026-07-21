---
name: osint-phone-numbers
description: OSINT sur numéros de téléphone — identification opérateur, localisation, recherche de comptes associés, reverse lookup et vérification.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, téléphone, phone, numéro, reverse-lookup, identification]
---

# OSINT sur Numéros de Téléphone

## 🎯 Description

Investigation de numéros de téléphone : identification de l'opérateur, localisation géographique, recherche de comptes associés sur les réseaux sociaux, vérification WhatsApp/Telegram, reverse lookup et détection de fuites.

---

## 📋 Outils Essentiels

### Outils CLI
| Outil | URL | Usage |
|-------|-----|-------|
| PhoneInfoga | https://github.com/sundowndev/PhoneInfoga | Framework avancé (N/B) |
| PhoneInfoga (Nouveau) | https://github.com/ExpertAnonymous/PhoneInfoga | Version réécrite |

### Vérification Opérateur et Localisation
| Outil | URL | Usage |
|-------|-----|-------|
| FreeCarrierLookup | https://freecarrierlookup.com | Opérateur + type (fixe/mobile) |
| Twilio Lookup | https://www.twilio.com/docs/lookup/v2-api | API payante, ~$0.01/recherche |
| mnp_bot (Telegram) | https://t.me/mnp_bot | Opérateur + région (RU) |
| bmi_np_bot (Telegram) | https://t.me/MNProbot | Infos opérateur |
| Infobel | https://www.infobel.com | 164M+ enregistrements, 73 pays |

### Reverse Phone Lookup
| Outil | URL | Usage |
|-------|-----|-------|
| Truecaller | https://truecaller.com | Global, communauté |
| Spy Dialer | https://spydialer.com | Messagerie vocale + nom |
| Reverse Phone Check | https://www.reversephonecheck.com | Recherche inversée |
| USPhoneBook | https://www.usphonebook.com/ | Reverse lookup US |
| SearchPeopleFREE | https://www.searchpeoplefree.com/phone-lookup | Reverse lookup |
| Phone Validator | https://www.phonevalidator.com | Détection Google Voice |
| Sync.ME | https://sync.me/ | Caller ID + spam |
| 411 (US) | https://www.411.com | Annuaire inverse |

### Recherche de Comptes Associés
| Outil | URL | Usage |
|-------|-----|-------|
| Epieos | https://epieos.com | Comptes sociaux par téléphone |
| Blackbird | https://github.com/p1ngul1n0/blackbird | Recherche sur 600+ sites |
| Castrick | https://castrickclues.com | Email, username, téléphone |
| Social Catfish | https://socialcatfish.com/ | Recherche complète |
| CheckLeaked | https://checkleaked.cc/ | Téléphone dans breaches |
| WhatsApp Checker | https://2chat.co/tools/whatsapp-checker | Vérification WhatsApp |
| Telegram Finder | https://www.telegram-finder.io/ | Recherche par téléphone |
| Cupidcr4wl | https://github.com/OSINTI4L/cupidcr4wl | Recherche sur sites adultes |

### Breaches et Fuites
| Outil | URL | Usage |
|-------|-----|-------|
| haveibeenzuckered | https://haveibeenzuckered.com | Breach Facebook 533M |
| LeakCheck | https://leakcheck.io | 7.5B+ entrées |
| Snusbase | https://snusbase.com | Base de fuites |
| DeHashed | https://dehashed.com | Moteur de breaches |
| InfoStealers | https://infostealers.info | Logs infostealer |

---

## 🔧 Méthodologie

### Phase 1 : Identification de Base
```bash
# PhoneInfoga - framework complet
pip install phoneinfoga
phoneinfoga scan -n "+33612345678"

# Format international requis
# Exemples :
# France : +33612345678
# US : +12125551234
# UK : +447911123456
```

### Phase 2 : Opérateur et Localisation
```bash
# FreeCarrierLookup
curl -s "https://freecarrierlookup.com/?number=+33612345678"

# Twilio Lookup (API)
# pip install twilio
# from twilio.rest import Client
# client = Client(account_sid, auth_token)
# phone_number = client.lookups.v2.phone_numbers("+33612345678").fetch()
```

### Phase 3 : Recherche sur Réseaux Sociaux
```bash
# Epieos - recherche multi-plateforme
# Naviguer sur https://epieos.com -> entrer le numéro

# Blackbird
git clone https://github.com/p1ngul1n0/blackbird
cd blackbird
python blackbird.py --phone "+33612345678"
```

### Phase 4 : Messagerie Instantanée
```bash
# WhatsApp - vérifier si le numéro est sur WhatsApp
# Naviguer vers https://wa.me/33612345678

# Telegram - vérifier si le numéro a un compte
# Naviguer vers https://t.me/+33612345678

# Telegram Finder
# Naviguer sur https://www.telegram-finder.io/
```

---

## 📊 Formats de Numéros

```text
# Format international (E.164) : +[indicatif][numéro]
# France : +33612345678
# US/Canada : +12125551234
# UK : +447911123456
# Allemagne : +491512345678
# Espagne : +34612345678
# Italie : +393123456789
# Belgique : +32470123456
# Suisse : +41791234567

# Indicatifs importants :
# +1 : US/Canada
# +33 : France
# +44 : UK
# +49 : Allemagne
# +34 : Espagne
# +39 : Italie
# +31 : Pays-Bas
# +32 : Belgique
# +41 : Suisse
# +46 : Suède
# +7 : Russie
# +86 : Chine
# +81 : Japon
# +91 : Inde
```

---

## 🛠️ Script d'Investigation Automatisé

```bash
#!/bin/bash
# phone_investigate.sh
PHONE="$1"

echo "=== Investigation du numéro: $PHONE ==="

# 1. Format international
echo "Format: $PHONE"

# 2. Opérateur
echo "--- Opérateur ---"
curl -s "https://freecarrierlookup.com/?number=$PHONE" | \
  grep -oP '(?<=<td>)[^<]+' | head -5

# 3. WhatsApp
echo "--- WhatsApp ---"
curl -sI "https://wa.me/$PHONE" | grep -i "location\|HTTP"

# 4. Truecaller (web)
echo "--- Truecaller ---"
echo "Naviguer sur https://truecaller.com/search/$PHONE"

# 5. Breaches
echo "--- Breaches ---"
echo "Vérifier sur https://checkleaked.cc/"
```

---

## 📝 Techniques Avancées

### Détection de Google Voice
```bash
# Les numéros Google Voice sont souvent utilisés pour l'anonymisation
# Phone Validator: https://www.phonevalidator.com
# Truecaller: marque souvent les numéros VoIP
```

### Analyse de Messagerie Vocale
```bash
# Spy Dialer - écouter la messagerie vocale
# Naviguer sur https://spydialer.com
# Entrer le numéro → écouter le message d'accueil
# Permet souvent d'identifier le propriétaire
```

### Recherche dans les Breaches Spécifiques
```bash
# Breach Facebook 533M (haveibeenzuckered)
# Naviguer sur https://haveibeenzuckered.com
# Entrer le numéro de téléphone
# Vérifie si le numéro était dans la fuite Facebook
```

### Recherche d'Annonces et Petites Annonces
```bash
# Rechercher le numéro dans les sites d'annonces
# site:leboncoin.fr "0612345678"
# site:craigslist.org "12125551234"
# site:ebay-kleinanzeigen.de "01791234567"
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Numéros VoIP** : Les numéros virtuels (Google Voice, Skype) sont difficiles à tracer.
- **Numéros jetables** : Beaucoup de services de numéros temporaires existent.
- **Portabilité** : Un numéro peut être porté d'un opérateur à l'autre. L'opérateur actuel peut être différent.
- **International** : Les formats et la disponibilité des données varient énormément selon les pays.
- **RGPD** : En Europe, les données téléphoniques sont protégées. Vérifier la légalité.
- **Frais** : Certains services (Truecaller, Twilio) sont payants pour les recherches avancées.
- **Faux positifs** : Les numéros réutilisés peuvent avoir des historiques trompeurs.

---

## 🔗 Références

- https://github.com/sundowndev/PhoneInfoga
- https://github.com/p1ngul1n0/blackbird
- https://github.com/jivoi/awesome-osint#phone-number-research
- https://truecaller.com