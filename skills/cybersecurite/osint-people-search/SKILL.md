---
name: osint-people-search
description: Recherche de personnes — annuaires, registres publics, généalogie, casiers judiciaires, recherche inversée et enquête d'identité.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, personnes, recherche, annuaires, registres, identité]
---

# Recherche de Personnes (People Search)

## 🎯 Description

Techniques de recherche de personnes via sources ouvertes : annuaires, registres publics, généalogie, casiers judiciaires, recherche inversée (nom, téléphone, adresse), et enquête d'identité numérique.

---

## 📋 Annuaires et Moteurs de Recherche de Personnes

### Internationaux
| Outil | URL | Usage |
|-------|-----|-------|
| Pipl | https://pipl.com | Recherche identité complète |
| Spokeo | https://www.spokeo.com | Recherche personne (payant) |
| PeekYou | https://www.peekyou.com/ | Recherche personne + arrestations |
| IDCrawl | https://www.idcrawl.com/ | Recherche multi-réseaux |
| Social Catfish | https://socialcatfish.com/ | 200B+ enregistrements |
| Clustermaps | https://clustrmaps.com/ | Personnes + adresses |
| BeenVerified | https://www.backgroundchecks.com/solutions/beenverified | Vérifications |
| InfoTracer | https://infotracer.com/ | Recherche personne (payant) |
| SearchBug | https://www.searchbug.com | Recherche personne |
| Reunion | https://reunion.com | Recherche personne |
| ZabaSearch | https://www.zabasearch.com/ | Recherche personne |
| FamilyTreeNow | https://familytreenow.com | Généalogie gratuit |

### États-Unis
| Outil | URL | Usage |
|-------|-----|-------|
| 411 (US) | https://www.411.com | Personne, téléphone, adresse |
| White Pages (US) | https://www.whitepages.com | Annuaire américain |
| Voter Records | https://voterrecords.com/ | 100M+ électeurs US |
| Judyrecords | https://www.judyrecords.com/ | 400M+ cas judiciaires US |
| UniCourt | https://unicourt.com/ | 100M+ cas judiciaires |
| Black Book Online | https://www.blackbookonline.info | Registres publics |
| BOP Inmate Locator | https://www.bop.gov/inmateloc | Prisonniers fédéraux |
| VineLink | https://www.vinelink.com | Notification prisonniers |
| Fold3 | https://www.fold3.com | Archives militaires US |

### France
| Outil | URL | Usage |
|-------|-----|-------|
| Pages Blanches | https://www.pagesblanches.fr | Annuaire téléphonique |
| Pages Jaunes | https://www.pagesjaunes.fr | Annuaire professionnel |
| 118000 | https://www.118000.fr | Annuaire inverse |
| Copains d'Avant | https://www.copainsdavant.com | Recherche scolaire |
| Societe.com | https://www.societe.com | Information entreprises |
| Infogreffe | https://www.infogreffe.fr | Registre commerce |
| Bodacc | https://www.bodacc.fr | Annonces légales |

### UK
| Outil | URL | Usage |
|-------|-----|-------|
| 192 (UK) | https://www.192.com | Personne, entreprise, adresse |
| UK Phone Book | https://www.ukphonebook.com/ | Annuaire UK |
| Canada411 | https://www.canada411.ca | Annuaire Canada |

---

## 🔧 Méthodologie

### Phase 1 : Recherche par Nom
```bash
# 1. Recherche Google
"Prénom Nom" "ville"
"Prénom Nom" "profession"
"Prénom Nom" "email"
"Prénom Nom" "linkedin"
"P. Nom" OR "Prénom N."

# 2. IDCrawl - recherche multi-réseaux
# Naviguer sur https://www.idcrawl.com/

# 3. Social Catfish - recherche avancée
# Naviguer sur https://socialcatfish.com/
```

### Phase 2 : Recherche par Adresse
```bash
# Google Maps
# Naviguer sur https://maps.google.com -> chercher l'adresse

# Clustermaps
# Naviguer sur https://clustrmaps.com/

# Homemetry - reverse address
# Naviguer sur https://homemetry.com
```

### Phase 3 : Registres Publics
```bash
# États-Unis
# Judyrecords - 400M+ cas judiciaires
# Voter Records - électeurs
# BOP - prisonniers fédéraux

# France
# Societe.com - dirigeants d'entreprises
# Infogreffe - registre commerce
# Bodacc - annonces légales
```

### Phase 4 : Généalogie
```bash
# FamilySearch - gratuit
# Naviguer sur https://familysearch.org

# FamilyTreeNow - sans inscription
# Naviguer sur https://familytreenow.com

# Ancestry - premium
# Naviguer sur https://www.ancestry.com
```

---

## 📊 Google Dorks pour Personnes

```text
# Recherche par nom complet
"Prénom Nom" "email" OR "contact" OR "phone"
"Prénom Nom" "CV" OR "resume"
"Prénom Nom" site:linkedin.com
"Prénom Nom" site:facebook.com
"Prénom Nom" site:twitter.com

# Recherche par profession
"Prénom Nom" "ingénieur" OR "développeur" OR "consultant"
"Prénom Nom" "CEO" OR "founder" OR "director"

# Recherche par localisation
"Prénom Nom" "Paris" OR "Lyon" OR "Marseille"
"Prénom Nom" "adresse" OR "habite" OR "réside"

# Recherche de documents
"Prénom Nom" filetype:pdf
"Prénom Nom" filetype:docx
"Prénom Nom" "thèse" OR "mémoire" OR "publication"
```

---

## 🛠️ Outils d'Investigation

### Recherche de Casiers Judiciaires
```bash
# US
# Naviguer sur https://www.judyrecords.com/ (gratuit)
# Naviguer sur https://unicourt.com/ (limité gratuit)

# France
# Naviguer sur https://www.casier-judiciaire.com/
# (attention, service payant)
```

### Recherche d'Ancêtres et Famille
```bash
# FamilySearch (gratuit, inscription)
# Naviguer sur https://familysearch.org

# GenealogyBank (premium)
# Naviguer sur https://www.genealogybank.com

# Genealogy Links (50K+ liens)
# Naviguer sur https://www.genealogylinks.net
```

### Recherche d'Inhumations
```bash
# Find a Grave
# Naviguer sur https://www.findagrave.com

# Billion Graves
# Naviguer sur https://billiongraves.com

# FinalNotes - guide de recherche d'avis de décès
# Naviguer sur https://www.finalnotes.page/obituary-research-guide/
```

---

## 📝 Techniques de Recherche Inversée

### Recherche par Photo
```bash
# FaceCheck.ID - reconnaissance faciale
# Naviguer sur https://facecheck.id

# PimEyes - recherche faciale
# Naviguer sur https://pimeyes.com

# Search4faces - recherche par visage
# Naviguer sur https://search4faces.com

# Surfface - face search + réseaux sociaux
# Naviguer sur https://surfface.com
```

### Recherche par Téléphone
```bash
# Truecaller
# Naviguer sur https://truecaller.com

# Spy Dialer - écouter la messagerie
# Naviguer sur https://spydialer.com

# Phone Validator - vérification Google Voice
# Naviguer sur https://www.phonevalidator.com
```

### Recherche par Email
```bash
# ThatsThem - reverse email
# Naviguer sur https://thatsthem.com/reverse-email-lookup

# Pipl - recherche d'identité
# Naviguer sur https://pipl.com
```

---

## 📊 Vérification de Crédibilité

```bash
# Vérifier si une personne existe vraiment
# 1. Recherche Google du nom complet
# 2. LinkedIn (profil professionnel)
# 3. Facebook (profil personnel)
# 4. Registres publics (adresse, profession)
# 5. Recherche d'images (photos d'identité)
# 6. Vérification croisée des informations
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **RGPD** : En Europe, la collecte et le traitement de données personnelles sont strictement réglementés.
- **Homonymes** : Toujours vérifier plusieurs sources pour confirmer qu'il s'agit de la bonne personne.
- **Données obsolètes** : Les annuaires peuvent contenir des informations vieilles de plusieurs années.
- **Services payants** : Beaucoup de sites affichent des résultats gratuits limités puis demandent un paiement.
- **Fausses informations** : Certaines données peuvent être volontairement fausses (profils fictifs).
- **Légalité** : Ne pas utiliser ces informations pour du harcèlement, doxxing ou activités illégales.

---

## 🔗 Références

- https://github.com/jivoi/awesome-osint#people-investigations
- https://www.judyrecords.com/
- https://thatsthem.com/
- https://pipl.com/