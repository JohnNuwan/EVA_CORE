---
name: osint-corporate-intelligence
description: Renseignement d'entreprise OSINT — registres de commerce, actionnariat, brevets, marchés publics, lobbying, filiales, concurrents et analyse de risque fournisseur.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, corporate, intelligence, entreprise, registres, brevets, marchés-publics, actionnariat]
---

# Corporate Intelligence OSINT

## 🎯 Description

Renseignement d'entreprise à partir de sources ouvertes : analyse de registres de commerce, identification d'actionnaires et bénéficiaires effectifs, surveillance de brevets et PI, veille sur marchés publics, analyse de concurrence, détection de liens entre entités, et évaluation de risque fournisseur.

---

## 📋 Outils Essentiels

### Registres de Commerce — France
| Outil | URL | Usage |
|-------|-----|-------|
| **Societe.com** | https://societe.com | Fiches d'entreprises (SIRET, CA, dirigeants, bilans) |
| **Pappers** | https://pappers.fr | Annuaire + alertes + documents |
| **Infogreffe** | https://www.infogreffe.fr | Registre du commerce officiel (extraits KBIS) |
| **Bodacc** | https://www.bodacc.fr | Annonces légales (créations, modifications, radiations) |
| **Annuaire-Entreprises** | https://annuaire-entreprises.data.gouv.fr | Base SIRENE officielle |
| **Data.gouv.fr** | https://data.gouv.fr | Open data français |
| **INSEE** | https://www.insee.fr | Statistiques, données SIRENE |
| **Verif.com** | https://www.verif.com | Scoring financier |
| **Kompass** | https://fr.kompass.com | Annuaire B2B |
| **Europages** | https://www.europages.fr | Annuaire européen |
| **Corse-pme.org** | https://www.corse-pme.org | Annuaire Corse |

### Registres — International
| Pays/Zone | Outil | URL |
|-----------|-------|-----|
| **Monde (général)** | OpenCorporates | https://opencorporates.com |
| **Monde (offshore)** | ICIJ Offshore Leaks | https://offshoreleaks.icij.org |
| **UE** | EU Business Registers | https://e-justice.europa.eu |
| **UK** | Companies House | https://find-and-update.company-information.service.gov.uk |
| **US** | OpenCorporates US | https://us.opencorporates.com |
| **US** | SEC EDGAR | https://www.sec.gov/edgar |
| **US** | OpenStates | https://openstates.org |
| **Suisse** | ZEFIX | https://www.zefix.ch |
| **Allemagne** | Bundesanzeiger | https://www.bundesanzeiger.de |
| **Pays-Bas** | KVK | https://www.kvk.nl |
| **Luxembourg** | LBR | https://www.lbr.lu |
| **Panama** | Registro Público | https://www.registro-publico.gob.pa |
| **Irlande** | CRO | https://search.cro.ie |
| **Singapour** | ACRA | https://www.acra.gov.sg |
| **Hong Kong** | CR | https://www.icris.cr.gov.hk |
| **Canada** | Innovation Canada | https://ised-isde.canada.ca |
| **Australie** | ASIC | https://connectonline.asic.gov.au |

### Bénéficiaires Effectifs et Transparence
| Outil | URL | Usage |
|-------|-----|-------|
| **Register of Beneficial Owners (UE)** | https://ec.europa.eu/info/policies/justice-and-fundamental-rights/company-law/beneficial-ownership-registers_en | Registres des bénéficiaires effectifs |
| **ICIJ Offshore Leaks** | https://offshoreleaks.icij.org | Panama Papers, Pandora Papers, etc. |
| **Open Ownership** | https://www.openownership.org | Données sur la propriété effective |
| **OCCRP Aleph** | https://aleph.occrp.org | Base de données d'enquêtes |
| **FinCEN Files** | https://www.icij.org/investigations/fincen-files/ | Documents FinCEN |
| **Transparency International** | https://www.transparency.org | Corruption Perception Index |

### Brevets et Propriété Intellectuelle
| Outil | URL | Usage |
|-------|-----|-------|
| **Google Patents** | https://patents.google.com | Recherche mondiale de brevets |
| **Espacenet** | https://worldwide.espacenet.com | Base brevets européenne (EPO) |
| **USPTO** | https://www.uspto.gov/patents/search | Brevets US |
| **WIPO Patentscope** | https://patentscope.wipo.int | Brevets PCT internationaux |
| **INPI** | https://www.inpi.fr | Brevets et marques France |
| **DPMA** | https://www.dpma.de | Brevets Allemagne |
| **J-PlatPat** | https://www.j-platpat.inpit.go.jp | Brevets Japon |
| **Patent Inspiration** | https://patentinspiration.com | Analyse de familles de brevets |
| **Lens.org** | https://www.lens.org | Brevets + littérature scientifique |
| **The Patent** | https://www.thepatent.com | Analyse de brevets |
| **Clarivate (Derwent)** | https://clarivate.com/derwent | Analyse PI (payant) |
| **Questel (Orbit)** | https://www.questel.com | Intelligence PI (payant) |

### Marchés Publics et Appels d'Offres
| Outil | URL | Usage |
|-------|-----|-------|
| **BOAMP** | https://www.boamp.fr | Marchés publics français |
| **TED (Tenders Electronic Daily)** | https://ted.europa.eu | Marchés publics européens |
| **Maximilien** | https://www.maximilien.fr | Intelligence marchés publics |
| **Place des Marchés** | https://www.placedesmarches.com | Plateforme d'achat public |
| **aws-alexa** | https://aws.amazon.com/fr/ | Cloud AWS (marchés publics) |
| **US SAM** | https://sam.gov | Marchés publics US |
| **OpenProcurement (Ukraine)** | https://prozorro.gov.ua | Marchés publics Ukraine |
| **Opentender** | https://opentender.eu | Analyse multi-pays UE |
| **DG Market (UE)** | https://etendering.ted.europa.eu | Procédures UE |

### Lobbying et Influence
| Outil | URL | Usage |
|-------|-----|-------|
| **Registre Transparence UE** | https://transparency-register.europa.eu | Lobbying UE |
| **LobbyFacts.eu** | https://www.lobbyfacts.eu | Analyse du lobbying UE |
| **OpenSecrets** | https://www.opensecrets.org | Lobbying US, dépenses politiques |
| **LittleSis** | https://littlesis.org | Réseaux d'influence |
| **SourceWatch** | https://www.sourcewatch.org | Surveillance des spin doctors |
| **Corporate Europe Observatory** | https://corporateeurope.org | Lobbying des entreprises |

### Analyse de Fournisseurs
| Outil | URL | Usage |
|-------|-----|-------|
| **EcoVadis** | https://ecovadis.com | Scoring RSE fournisseurs |
| **CSRHub** | https://www.csrhub.com | Données ESG |
| **Sustainalytics** | https://www.sustainalytics.com | ESG ratings |
| **RepRisk** | https://www.reprisk.com | Risque réputationnel |
| **IntegrityNext** | https://www.integritynext.com | Due diligence fournisseur |

---

## 🔧 Méthodologie

### Phase 1 : Cartographie d'Entreprise

```bash
# 1. Recherche de base
echo "=== Recherche de base ==="
# Société.com
# Naviguer sur https://societe.com -> chercher par SIRET, nom, dirigeant

# Pappers (gratuit, sans inscription)
# Naviguer sur https://pappers.fr -> rechercher

# OpenCorporates
curl -s "https://api.opencorporates.com/v0.4/companies/search?q=ENTREPRISE" | jq .

# 2. Dirigeants et mandats
echo "=== Dirigeants ==="
# Identifier tous les mandats d'un dirigeant
# Pappers: https://pappers.fr/personne/PRENOM-NOM

# 3. Filiales et participation
echo "=== Filiales ==="
# Vérifier les liens de participation
# Recherche : "filiale" OR "groupe" OR "holding"
```

### Phase 2 : Analyse Financière

```bash
# 1. Bilans et comptes annuels
# Societe.com -> rubrique "Comptes annuels"
# Pappers -> "Documents financiers"

# 2. Scoring financier
# Verif.com -> score + cotation
# Altman Z-score pour prédiction de faillite

# 3. Dette et financement
# Bodacc -> annonces de cession, dépôt de garantie
# Infogreffe -> privilèges, nantissements
```

### Phase 3 : Brevets et Innovation

```bash
# 1. Google Patents
# Naviguer sur https://patents.google.com
# Recherche par: entreprise, inventeur, classification CPC

# 2. Espacenet (EPO)
# Naviguer sur https://worldwide.espacenet.com
# Recherche avancée par:

# Commandes Google Patents
# "company name" patents
# inventor:"Nom Prénom"
# assignee:"Company Name"
# (date:2022-2024) AND assignee:"Company"

# 3. Analyse de portfolio
# - Nombre de brevets par année
# - Classification CPC (domain mapping)
# - Inventeurs récurrents
# - Citations (brevets cités et citants)
```

### Phase 4 : Marchés Publics

```bash
# 1. BOAMP
# Naviguer sur https://www.boamp.fr
# Recherche par: SIRET, code CPV, montant

# 2. TED (UE)
# Naviguer sur https://ted.europa.eu
# Recherche multi-critères

# 3. Analyse des marchés remportés
# - Montant total par année
# - Clients récurrents
# - Types de marchés (fournitures, services, travaux)
# - Co-traitants et sous-traitants
```

### Phase 5 : Bénéficiaires Effectifs

```bash
# 1. ICIJ Offshore Leaks
# Naviguer sur https://offshoreleaks.icij.org
# Recherche par nom, pays, intermédiaire

# 2. Register of Beneficial Owners
# Naviguer sur https://opencorporates.com
# Chercher les bénéficiaires effectifs déclarés

# 3. LittleSis
# Naviguer sur https://littlesis.org
# Cartographie des réseaux d'influence

# 4. OCCRP Aleph
# Naviguer sur https://aleph.occrp.org
# Recherche multi-sources
```

---

## 📊 Google Dorks Corporate

```text
# Fiches d'entreprise
site:societe.com "Nom Dirigeant"
site:pappers.fr "Prénom Nom"
site:opencorporates.com "Company Name"

# Brevets
site:patents.google.com "inventor" "Company"
site:patents.google.com "assignee" "Company"
site:worldwide.espacenet.com "applicant" "Company"

# Marchés publics
site:boamp.fr "SIRET" OR "company name"
site:ted.europa.eu "company name" "procurement"

# Litiges et contentieux
site:legifrance.gouv.fr "company name" OR "SIRET"
site:doctrine.fr "company name" (Décisions de justice)
filetype:pdf "company name" "jugement" OR "tribunal"

# Presse et actualités
"Company Name" "contrat" OR "partenariat" OR "acquisition"
"Company Name" "procès" OR "amende" OR "sanction"
"Company Name" "levée de fonds" OR "investissement"
```

---

## 🛠️ Scripts Utiles

### Script d'Analyse Concurrentielle
```bash
#!/bin/bash
# competitive_intel.sh
COMPANY="$1"

echo "=== Analyse de: $COMPANY ==="

# 1. Recherche de brevets
echo "--- Brevets ---"
curl -s "https://patents.google.com/?assignee=$COMPANY&language=ENGLISH&num=5" | \
  grep -oP '(?<=<h3 class="result-title">)[^<]+' | head -10

# 2. Recherche de marchés publics
echo "--- Marchés publics (UE) ---"
curl -s "https://ted.europa.eu/api/search?q=$COMPANY&limit=5" | jq '.results[] | {title, value, date}'

# 3. Recherche d'actualités
echo "--- Actualités récentes ---"
curl -s "https://newsapi.org/v2/everything?q=$COMPANY&pageSize=5&apiKey=KEY" | \
  jq '.articles[] | {title, source: .source.name, date: .publishedAt}'
```

### Script de Vérification de Chaîne d'Approvisionnement
```bash
#!/bin/bash
# supply_chain_check.sh
SIRET="$1"

echo "=== Vérification SIRET: $SIRET ==="

# 1. Infogreffe - extrait KBIS
echo "--- Infogreffe ---"
curl -s "https://www.infogreffe.fr/entreprise/$SIRET" | \
  grep -oP '(?<=<span class="label">)[^<]+'

# 2. Pappers - scoring
echo "--- Pappers ---"
curl -s "https://api.pappers.fr/v2/entreprise?siren=${SIRET:0:9}&api_token=TOKEN" | \
  jq '{nom, forme_juridique, capital, ca, resultat, effectif}'

# 3. Bodacc - annonces légales
echo "--- Bodacc ---"
curl -s "https://www.bodacc.fr/annonces?siren=${SIRET:0:9}" | \
  grep -oP '(?<=<div class="annonce">)[^<]+' | head -5
```

---

## 📝 Techniques Avancées

### Cartographie de Réseau d'Entreprises
```bash
# 1. Identifier toutes les entités liées
#    - Filiales (>=50% capital)
#    - Participations (<50%)
#    - Dirigeants communs
#    - Adresses partagées
#    - Numéros de téléphone partagés

# 2. Analyser les liens faibles
#    - Anciens dirigeants
#    - Fournisseurs récurrents
#    - Clients communs

# 3. Visualisation
#    - Gephi (https://gephi.org) — graphe de relations
#    - LittleSis (https://littlesis.org) — réseaux pré-construits
#    - Maltego — transforms corporate
```

### Analyse de Litiges et Contentieux
```bash
# 1. Doctrine.fr (France)
# Naviguer sur https://www.doctrine.fr
# Recherche: nom entreprise, SIRET, dirigeant

# 2. Legifrance
# Naviguer sur https://www.legifrance.gouv.fr
# Recherche: "NOM ENTREPRISE" "arrêt" OR "jugement"

# 3. PACER (US Federal Courts)
# Naviguer sur https://pacer.uscourts.gov
# Recherche: company name, docket number
```

### Due Diligence Rapide (15 min)
```bash
# 1. Vérification d'existence (1 min)
#   OpenCorporates / Societe.com / Companies House

# 2. Scoring financier (2 min)
#   Pappers / Verif / D&B

# 3. Dirigeants (2 min)
#   Pappers personnes / LinkedIn

# 4. Brevets (2 min)
#   Google Patents / Espacenet

# 5. Marchés publics (2 min)
#   BOAMP / TED

# 6. Litiges (2 min)
#   Doctrine / Legifrance / PACER

# 7. Presse et réputation (2 min)
#   Google News / Mentions légales / Avis

# 8. Bénéficiaires effectifs (2 min)
#   OpenCorporates / ICIJ / OCCRP
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Données obsolètes** : Les registres de commerce peuvent être mis à jour avec des mois de retard. Toujours vérifier la date.
- **Homonymes** : Plusieurs entreprises peuvent partager le même nom. Utiliser le SIRET/SIREN pour l'identification unique.
- **Pays différents** : Les informations disponibles varient énormément selon les pays (transparence vs confidentialité).
- **Paradises fiscaux** : Les structures offshore sont conçues pour masquer la propriété réelle. Les données ICIJ sont un bon point de départ mais incomplètes.
- **Dirigeants de paille** : Les bénéficiaires effectifs peuvent utiliser des prête-noms. Vérifier les liens familiaux et les adresses.
- **API payantes** : Pappers, Societe.com, Infogreffe ont des API payantes ou limitées. Utiliser l'interface web pour les recherches ponctuelles.
- **RGPD** : Les données personnelles des dirigeants (adresse personnelle, téléphone) sont protégées. Ne pas diffuser sans base légale.
- **Contexte** : Un brevet ne signifie pas nécessairement une innovation réelle. Certains brevets sont défensifs ou stratégiques.

---

## 🔗 Références

- https://opencorporates.com
- https://offshoreleaks.icij.org
- https://www.societe.com
- https://pappers.fr
- https://patents.google.com
- https://www.boamp.fr
- https://ted.europa.eu
- https://github.com/jivoi/awesome-osint#corporate-records
- https://aleph.occrp.org
- https://littlesis.org