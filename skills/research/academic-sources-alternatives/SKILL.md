---
name: academic-sources-alternatives
description: >-
  Compétence en recherche académique multi-sources au-delà d'arXiv. Couvre
  Google Scholar, Semantic Scholar, SSRN, ResearchGate, PubMed Central,
  OpenAlex, CORE, DOAJ, HAL, JSTOR, IEEE Xplore, ACL Anthology, PubMed,
  Crossref, Unpaywall, et les API académiques ouvertes pour la veille
  scientifique exhaustive.
category: research
---

# Compétence en Sources Académiques Alternatives

## Présentation

La recherche académique ne se limite pas à arXiv. De nombreuses autres plateformes complètent l'écosystème. Cette compétence fournit une cartographie complète des sources, des API, et des stratégies de veille multi-sources.

## Sources Académiques Primaires

### arXiv.org
- **Domaine** : Physique, maths, CS, stats, finance, économie, biologie
- **URL** : https://arxiv.org
- **API** : https://export.arxiv.org/api/query
- **Format** : XML via API REST
- **Volume** : ~2,4M articles, ~10 000/mois
- **Accès** : Gratuit, sans compte

### Google Scholar
- **Domaine** : Toutes disciplines
- **URL** : https://scholar.google.com
- **API** : APIs Without Limits / Scholar API (tiers)
- **Particularité** : Indexation large, citations, profil chercheurs
- **Stratégie** : Utiliser des APIs tierces (SerpAPI, ScraperAPI) pour l'accès programmatique
- **Limite** : Bloque les scrapers, nécessite contournement

### Semantic Scholar
- **Domaine** : CS, biomédecine, sciences dures
- **URL** : https://www.semanticscholar.org
- **API** : https://api.semanticscholar.org (gratuite, rate-limited)
- **Particularité** : IA pour extraire citations, TLDRs, influent citations
- **Endpoint** : `https://api.semanticscholar.org/graph/v1/paper/search?query=...`
- **Avantage** : API REST gratuite, pas de clé requise pour accès de base

### SSRN (Social Science Research Network)
- **Domaine** : Économie, finance, droit, sciences sociales
- **URL** : https://papers.ssrn.com
- **Particularité** : Prépublications en économie/finance, racheté par Elsevier
- **Accès** : Gratuit, Cloudflare protège l'accès

### PubMed / PubMed Central
- **Domaine** : Médecine, biologie, santé publique
- **URL** : https://pubmed.ncbi.nlm.nih.gov
- **API** : https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
- **Format** : E-utilities (ESearch, EFetch, ESummary)
- **Volume** : ~35M+ citations, ~7M articles texte intégral PMC
- **Accès** : API ouverte sans clé (rate limit 3 req/sec)

### ResearchGate
- **Domaine** : Toutes disciplines
- **URL** : https://www.researchgate.net
- **Particularité** : Réseau social académique, tracking de lectures/téléchargements
- **Accès** : Sur inscription

## API et Accès Programmés

### OpenAlex
- **Domaine** : Catalogue ouvert de la recherche mondiale
- **URL** : https://openalex.org
- **API** : `https://api.openalex.org/works?search=...`
- **Particularité** : Successeur de Microsoft Academic Graph, open source
- **Volume** : ~250M+ travaux, ~90M auteurs, ~160K institutions
- **Filtres** : Année, concepts, auteurs, institutions, revues
- **Avantage** : Gratuit, pas de clé, bien documenté, rate limit généreux

### CORE
- **Domaine** : Agrégateur de publications en accès ouvert
- **URL** : https://core.ac.uk
- **API** : `https://api.core.ac.uk/v3/search/works?q=...`
- **Volume** : ~250M+ articles de 11K+ fournisseurs
- **Accès** : Clé API gratuite requise

### DOAJ (Directory of Open Access Journals)
- **Domaine** : Revues en accès ouvert toutes disciplines
- **URL** : https://doaj.org
- **API** : `https://api.doaj.org/`
- **Volume** : ~20K revues, ~10M articles

### Crossref
- **Domaine** : Métadonnées de publications via DOI
- **URL** : https://www.crossref.org
- **API** : `https://api.crossref.org/works?query=...`
- **Particularité** : Enregistrement central des DOI
- **Volume** : ~150M+ enregistrements

### Unpaywall
- **Domaine** : Accès ouvert aux articles
- **URL** : https://unpaywall.org
- **API** : `https://api.unpaywall.org/v2/`
- **Particularité** : Trouve les versions gratuites des articles payants
- **Outil** : Extension navigateur + API REST

## Dépôts Institutionnels et Thématiques

| Dépôt | Domaine | URL |
|-------|---------|-----|
| **HAL** | Recherche française toutes disciplines | https://hal.science |
| **Zenodo** | Multi-disciplinaire (CERN) | https://zenodo.org |
| **Figshare** | Multi-disciplinaire | https://figshare.com |
| **BioRxiv** | Biologie (préprints) | https://biorxiv.org |
| **MedRxiv** | Médecine (préprints) | https://medrxiv.org |
| **ChemRxiv** | Chimie (préprints) | https://chemrxiv.org |
| **SocArXiv** | Sciences sociales | https://socarxiv.org |
| **PsyArXiv** | Psychologie | https://psyarxiv.com |
| **EdArXiv** | Éducation | https://edarxiv.org |
| **EngrXiv** | Ingénierie | https://engrxiv.org |
| **LawArXiv** | Droit | https://lawarxiv.info |
| **AgriRxiv** | Agriculture | https://agrirxiv.org |

## Revues et Conférences Clés par Domaine

### Finance et Économie
- **Journal of Finance**, **Journal of Financial Economics**, **Review of Financial Studies**
- **Quantitative Finance** (Taylor & Francis)
- **Journal of Financial and Quantitative Analysis**
- **Journal of Risk**, **Journal of Derivatives**
- **Journal of Financial Econometrics**
- **SSRN Financial Economics Network**

### IA et ML
- **NeurIPS**, **ICML**, **ICLR**, **AISTATS**, **COLT**
- **JMLR**, **Machine Learning Journal**, **IEEE TPAMI**
- **Nature Machine Intelligence**, **PNAS**

### Médecine
- **The Lancet**, **NEJM**, **JAMA**, **BMJ**
- **Nature Medicine**, **Cell**, **Science Translational Medicine**
- **MICCAI**, **RSNA**, **SPIE Medical Imaging**

## Stratégie de Veille Multi-Sources

### Quotidienne
1. **arXiv** : `/list/<cat>/recent` pour les catégories cibles
2. **Semantic Scholar** : API pour suggestions personnalisées
3. **OpenAlex** : Flux par concepts

### Hebdomadaire
1. **PubMed** : Recherche par mots-clés avec filtres date
2. **Crossref** : Nouveaux DOI par domaine
3. **CORE** : Agrégation open access

### Mensuelle
1. **DOAJ** : Nouveaux journaux en accès ouvert
2. **Unpaywall** : Vérification d'accès ouvert
3. **Zenodo** : Nouveaux dépôts par communauté

## Requêtes API Prêtes à l'Emploi

```bash
# OpenAlex — recherche finance
curl "https://api.openalex.org/works?search=fiancial+deep+learning&filter=publication_year:2025,2026"

# Semantic Scholar — recherche trading RL
curl "https://api.semanticscholar.org/graph/v1/paper/search?query=reinforcement+learning+trading&year=2025-2026&limit=10"

# Crossref — recherche finance quantitative
curl "https://api.crossref.org/works?query=quantitative+finance+deep+learning&filter=from-pub-date:2025-01-01&rows=10"

# PubMed — IA en finance (via E-utilities)
curl "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=finance+AI&retmax=10"
```

## Sources de Données Financières Académiques
- **WRDS** (Wharton Research Data Services) : Données de marché, CRSP, Compustat — accès institutionnel
- **Kenneth French Data Library** : Facteurs de risque, portefeuilles — gratuit
- **FRED** (Federal Reserve Economic Data) : Macroéconomie, taux — gratuit
- **Yahoo Finance API** : Données de marché historiques et temps réel — gratuit
- **CoinGecko / CoinMarketCap API** : Données crypto
- **Quandl / Nasdaq Data Link** : Données financières alternatives

## Comment Effectuer la Veille
- **Recherche principale** : OpenAlex (`https://api.openalex.org/works?search=...`)
- **Finance** : SSRN + Semantic Scholar + arXiv q-fin.*
- **Médecine** : PubMed + medRxiv
- **Veille généraliste** : CORE + Unpaywall + CrossRef
- **Alertes** : Configurer des alertes Google Scholar, PubMed, arXiv