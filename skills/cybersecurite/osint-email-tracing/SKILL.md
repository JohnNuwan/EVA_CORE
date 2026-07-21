---
name: osint-email-tracing
description: Investigation d'emails — traçage, vérification, recherche de comptes associés, analyse d'en-têtes et détection de fuites.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, email, tracing, vérification, headers, SMTP, fuites]
---

# Email Tracing et Investigation

## 🎯 Description

Techniques d'investigation d'adresses email : vérification d'existence, recherche de comptes associés, analyse d'en-têtes SMTP, détection de fuites dans les breaches, et reconstruction d'identité numérique à partir d'une adresse email.

---

## 📋 Outils Essentiels

### Vérification d'Email
| Outil | URL | Usage |
|-------|-----|-------|
| Hunter | https://hunter.io | Recherche d'emails par domaine |
| EmailRep | https://emailrep.io | Scoring de réputation d'email |
| Verify Email | https://verify-email.org | Vérification d'existence |
| EmailHippo | https://tools.verifyemailaddress.io | Vérification avancée |
| Email Validator | https://www.email-validator.net | Validation de format |
| Reacher | https://reacher.email | Vérification open-source |
| MailTester | https://mailtester.com | Chasse et vérification |

### Recherche de Comptes par Email
| Outil | URL | Usage |
|-------|-----|-------|
| Holehe | https://github.com/megadose/holehe | Vérifie si email est utilisé sur +100 sites |
| Epieos | https://epieos.com | Recherche de comptes sociaux |
| Blackbird | https://github.com/p1ngul1n0/blackbird | Recherche email sur 600+ sites |
| SherlockEye | https://sherlockeye.io/ | Recherche email multi-sources |
| user-scanner | https://github.com/kaifcodec/user-scanner | Scan email sur sites/gaming |
| MailAccess | https://github.com/KatrielMoses/MailAccess | Vérification 800+ plateformes |

### Fuites et Breaches
| Outil | URL | Usage |
|-------|-----|-------|
| Have I Been Pwned | https://haveibeenpwned.com | Vérification breaches |
| DeHashed | https://dehashed.com | Moteur de recherche de breaches |
| LeakCheck | https://leakcheck.io | 7.5B+ entrées de fuites |
| IntelX | https://intelx.io | Recherche dans fuites et dark web |
| LeakRadar | https://leakradar.io | Scan de stealer logs |
| Snusbase | https://snusbase.com | Base de données de fuites |
| InfoStealers | https://infostealers.info | Index de logs infostealer |
| OsintCat | https://www.osintcat.net | Vérification multi-breaches |
| CheckLeaked | https://checkleaked.cc/ | Email/username/phone dans breaches |

### Google et Comptes Google
| Outil | URL | Usage |
|-------|-----|-------|
| GHunt | https://github.com/mxrch/GHunt | Investigation comptes Google |
| Epieos Tools | https://tools.epieos.com | Google account lookup |

### Analyse d'En-têtes Email
| Outil | URL | Usage |
|-------|-----|-------|
| MXToolbox | https://mxtoolbox.com | Analyse en-têtes, DNS, blacklists |
| Spamhaus | https://check.spamhaus.org | Réputation IP |
| MultiRBL | https://multirbl.valli.org | Vérification blacklists |
| Blacklist Checker | https://blacklistchecker.com | 100+ blacklists |

---

## 🔧 Méthodologie

### Phase 1 : Vérification de Base
```bash
# Holehe - vérifier les comptes associés
pip install holehe
holehe email@example.com

# EmailRep - API de réputation
curl -s "https://emailrep.io/email@example.com"
```

### Phase 2 : Recherche sur les Réseaux Sociaux
```bash
# Epieos - recherche de comptes
# Naviguer sur https://epieos.com

# MailAccess - vérification 800+ plateformes
pip install mailaccess
mailaccess -e email@example.com
```

### Phase 3 : Analyse des Fuites
```bash
# HIBP - API
curl -s "https://haveibeenpwned.com/api/v3/breachedaccount/email@example.com"

# DeHashed - recherche (API payante mais interface web gratuite)
# Naviguer sur https://dehashed.com
```

### Phase 4 : Analyse d'En-têtes SMTP
```
# En-têtes à analyser dans un email :
Received: from [IP] → Serveur d'envoi
Return-Path → Adresse de retour
Reply-To → Adresse de réponse
Message-ID → Identifiant unique
DKIM-Signature → Signature DKIM
SPF → Sender Policy Framework
Authentication-Results → Résultats d'authentification
X-Originating-IP → IP d'origine (dans certains cas)
```

### Phase 5 : Google Account Investigation
```bash
# GHunt - investigation Google
git clone https://github.com/mxrch/GHunt
cd GHunt
pip install -r requirements.txt
python3 hunt.py email@example.com
```

---

## 📊 Commandes CLI

### Permutateurs d'Emails
```bash
# Email Permutator - générer des variations
# Web: https://www.polished.app/email-permutator/

# Formats courants :
# jean.dupont@company.com
# jdupont@company.com
# jeand@company.com
# jean.dupont@company.com
# j.dupont@company.com
```

### Recherche par Domaine
```bash
# Hunter - trouver les emails d'un domaine
curl -s "https://api.hunter.io/v2/domain-search?domain=example.com&api_key=KEY"

# Email Format - formats utilisés par l'entreprise
# Naviguer sur https://email-format.com
```

### Vérification SMTP
```bash
# Vérification sans envoyer d'email
# Telnet (manuel)
telnet mx.example.com 25
HELO example.com
MAIL FROM:<test@example.com>
RCPT TO:<target@example.com>
QUIT
```

---

## 📝 Analyse d'En-tête Complète

```bash
# MXToolbox - analyse des en-têtes
# Naviguer sur https://mxtoolbox.com/EmailHeaders.aspx

# Extraire l'IP d'origine
grep -E "^Received:" email.eml | head -1

# Vérifier SPF
dig example.com TXT | grep "v=spf1"

# Vérifier DKIM
dig _domainkey.example.com TXT

# Vérifier DMARC
dig _dmarc.example.com TXT
```

---

## 🛡️ Services de Recherche Professionnels

| Service | URL | Usage |
|---------|-----|-------|
| Pipl | https://pipl.com | Identité et recherche |
| ThatsThem | https://thatsthem.com/reverse-email-lookup | Reverse email lookup |
| IntelBase | https://intelbase.is/ | Enrichissement de données email |
| ContactOut | https://contactout.com/ | Emails professionnels |
| Snov.io | https://snov.io/email-finder | Recherche d'emails |
| Lusha | https://lusha.com | Contacts B2B |
| VoilaNorbert | https://www.voilanorbert.com | Recherche de contacts |

---

## ⚠️ Pièges et Bonnes Pratiques

- **Catch-all** : Certains serveurs acceptent tous les emails (catch-all). Vérifier plusieurs fois.
- **Rate limiting** : HIBP et autres APIs limitent les requêtes. Utiliser des clés API et des délais.
- **Emails temporaires** : Ignorer les domaines d'emails jetables (mailinator, guerrillamail, etc.).
- **Validation** : Toujours croiser les résultats de plusieurs sources.
- **Légalité** : Vérifier la légalité de l'utilisation des données dans votre juridiction (RGPD, etc.).
- **Faux positifs** : Les vérifications SMTP peuvent donner des faux positifs. Valider avec plusieurs méthodes.

---

## 🔗 Références

- https://github.com/megadose/holehe
- https://github.com/mxrch/GHunt
- https://github.com/jivoi/awesome-osint#email-search--email-check
- https://emailrep.io/