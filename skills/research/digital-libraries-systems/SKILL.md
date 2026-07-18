---
name: digital-libraries-systems
description: "Bibliothèques numériques, archivage, métadonnées, identifiants pérennes, science ouverte et humanités numériques (cs.DL)"
category: research
---

# Bibliothèques Numériques & Digital Libraries (cs.DL)

## Présentation

Ce skill couvre le domaine **cs.DL (Digital Libraries)** — l'ensemble des systèmes, standards, formats et protocoles qui permettent la création, la gestion, la préservation et la diffusion de collections numériques. Il sert de guide pour la recherche et l'ingénierie autour des bibliothèques numériques, de l'archivage pérenne, des métadonnées structurées, du linked open data, de l'OCR, et des infrastructures de science ouverte.

---

## Domaines

### 1. Systèmes de bibliothèques numériques

| Système | Description | Langage | Dépôt |
|---------|-------------|---------|-------|
| **DSpace** | Plateforme open-source de référence pour dépôts institutionnels (MIT, HP) | Java | https://github.com/DSpace/DSpace |
| **Fedora** | Flexible Extensible Digital Object Repository Architecture | Java | https://github.com/fcrepo/fcrepo |
| **Greenstone** | Suite de création de bibliothèques numériques (UNESCO, Waikato) | C++/Perl | https://www.greenstone.org |
| **Invenio** | Framework pour dépôts de recherche (CERN) | Python | https://inveniosoftware.org |
| **Samvera/Hyrax** | Écosystème de gestion de collections (ex-Hydra) | Ruby/Rails | https://samvera.org |
| **Omeka** | Plateforme pour expositions virtuelles et DH | PHP | https://omeka.org |
| **Islandora** | Solution intégrée Fedora + Drupal | PHP/Java | https://islandora.ca |

### 2. Schémas de métadonnées

| Standard | Usage | Spécification |
|----------|-------|---------------|
| **Dublin Core (DC)** | Métadonnées génériques (15 éléments de base + DC Terms) | ISO 15836 |
| **MARC21** | Catalogage bibliothécaire (format machine) | https://www.loc.gov/marc |
| **MODS** | Metadata Object Description Schema (XML, LC) | https://www.loc.gov/standards/mods |
| **METS** | Metadata Encoding & Transmission Standard (structure) | https://www.loc.gov/standards/mets |
| **PREMIS** | Preservation Metadata (événements, droits) | https://www.loc.gov/standards/premis |
| **BIBFRAME** | Modèle de données bibliographique (Linked Data, LC) | https://www.loc.gov/bibframe |
| **CIDOC-CRM** | Modèle conceptuel pour le patrimoine culturel (ICOM) | ISO 21127 |
| **TEI** | Text Encoding Initiative (textes littéraires/scientifiques) | https://tei-c.org |

### 3. Archivage numérique et préservation

| Technologie | Rôle |
|-------------|------|
| **OAIS (ISO 14721)** | Modèle de référence Open Archival Information System — architecture fonctionnelle (SIP, AIP, DIP) |
| **LOCKSS** | Lots of Copies Keep Stuff Safe — préservation distribuée pair-à-pair |
| **CLOCKSS** | Controlled LOCKSS — archive de sauvegarde mondiale, coopérative |
| **Archivematica** | Pipeline automatisé de préservation numérique (basé sur OAIS) |
| **BagIt** | Format de paquetage pour le transfert de contenu numérique (IETF RFC 8493) |
| **DuraCloud** | Service cloud de préservation et d'accès |

### 4. OCR et extraction de texte

| Outil | Description |
|-------|-------------|
| **Tesseract** | Moteur OCR open-source (Google), support >100 langues, LSTM |
| **GROBID** | Extraction et structuration de publications scientifiques (XML TEI) |
| **OCR-D** | Framework allemand pour OCR de documents historiques |
| **Kraken** | Moteur d'OCR avec support de transcription pour documents historiques |
| **eScriptorium** | Interface web de transcription manuscrite (basée Kraken) |
| **Transkribus** | Plateforme de reconnaissance d'écriture manuscrite (HTR) |
| **ABBYY FineReader** | OCR commercial, haute précision, documents complexes |

### 5. Indexation et recherche

| Technologie | Description |
|-------------|-------------|
| **Elasticsearch** | Moteur de recherche distribué (RESTful, JSON, temps réel) |
| **Solr** | Plateforme de recherche open-source (Apache, Lucene sous-jacent) |
| **Apache Lucene** | Bibliothèque Java d'indexation et recherche full-text |
| **Vecteur + Recherche sémantique** | Embeddings, hybrid search (kNN + BM25), RAG |

### 6. Identifiants pérennes

| Identifiant | Usage | Organisation |
|-------------|-------|-------------|
| **DOI** | Digital Object Identifier — publications, datasets | Crossref, DataCite |
| **Handle** | Handle System — identifiants génériques | CNRI |
| **ARK** | Archival Resource Key — bibliothèques, archives | California Digital Library |
| **ORCID** | Identifiant chercheur — auteurs, contributeurs | ORCID Inc. |
| **ISSN/ISBN** | Publications en série / livres | ISSN IC, ISBN Agency |
| **SWHID** | Software Heritage Identifier — code source | Software Heritage |
| **RAiD** | Research Activity Identifier — projets | ARDC |

### 7. Linked Open Data (LOD)

| Technologie | Rôle |
|-------------|------|
| **RDF** | Resource Description Framework — graphe de données |
| **SPARQL** | Langage de requête RDF (endpoints) |
| **SKOS** | Simple Knowledge Organization System — thesaurii, taxonomies |
| **IIIF** | International Image Interoperability Framework — images, manifests, APIs |
| **OAI-PMH** | Open Archives Initiative — Protocol for Metadata Harvesting |
| **JSON-LD** | Encodage JSON de RDF pour APIs Web |
| **Triplestores** | Fuseki, Virtuoso, Blazegraph, GraphDB |

### 8. Science ouverte

| Infrastructure | Description |
|---------------|-------------|
| **arXiv** | Prépublications (physique, maths, CS) — Cornell |
| **HAL** | Archive ouverte française — multi-disciplinaire |
| **Zenodo** | Dépôt généraliste (CERN) — datasets, posters, software |
| **OpenAire** | Infrastructure européenne de science ouverte |
| **Plan S / cOAlition S** | Accès immédiat et ouvert aux publications |
| **Software Heritage** | Archive du code source (Inria, UNESCO) |
| **PKP/Open Journal Systems** | Gestion et publication de revues open access |

### 9. Digital Humanities (Humanités Numériques)

| Domaine | Exemples d'outils et méthodes |
|---------|-------------------------------|
| **Édition numérique** | TEI Publisher, Edition Visualization Technology (EVT) |
| **Analyse textuelle** | Voyant Tools, TXM, AntConc, stylométrie (stylo) |
| **Cartographie historique** | GIS historique, Neatline (Omeka), Palladio |
| **Réseaux sociaux historiques** | Gephi, Palladio, Nodegoat |
| **Corpus et linguistique** | SketchEngine, CLARIN, DARIAH |
| **Visualisation** | D3.js, Vega-Lite, RAWGraphs |
| **Reconnaissance d'écriture** | Kraken + eScriptorium, Transkribus |

---

## Articles et conférences

### Revues majeures
- **International Journal on Digital Libraries (IJDL)** — Springer
- **Journal of the Association for Information Science and Technology (JASIST)** — Wiley
- **Library Hi Tech** — Emerald
- **Digital Scholarship in the Humanities (DSH)** — Oxford
- **Code4Lib Journal** — open-access

### Conférences
- **JCDL** — ACM/IEEE Joint Conference on Digital Libraries
- **TPDL** — International Conference on Theory and Practice of Digital Libraries
- **iConference** — sociale, technique, curation
- **DH** — Digital Humanities (ADHO)
- **Open Repositories** — dépôts institutionnels
- **IDCC** — International Digital Curation Conference

### Requêtes arXiv (cs.DL)

Recherche de papiers sur arXiv dans la catégorie Digital Libraries :

```
# Recherche générale cs.DL (bibliothèque arXiv)
web_search("arXiv cs.DL digital libraries survey 2024 2025")

# Recherche par sujet
web_search("arXiv cs.DL metadata schema BIBFRAME linked data")
web_search("arXiv cs.DL OAIS preservation digital curation")
web_search("arXiv cs.DL IIIF image interoperability framework")
web_search("arXiv cs.DL open science repositories Zenodo HAL")
web_search("arXiv cs.DL OCR historical documents deep learning")
web_search("arXiv cs.DL digital humanities text mining corpus")
```

### Papiers de référence
- Lagoze, C., & Van de Sompel, H. (2001). *The Open Archives Initiative: Building a low-barrier interoperability framework*
- Arms, W. Y. (2000). *Digital Libraries* — MIT Press (ouvrage fondateur)
- Borgman, C. L. (2007). *Scholarship in the Digital Age* — MIT Press
- Candela, L. et al. (2007). *Setting the Foundations of Digital Libraries: The DELOS Manifesto*

---

## Veille

### Réseaux sociaux et blogs techniques
- **@code4lib** — communauté de développeurs de bibliothèques
- **@CLIRnews** — Council on Library and Information Resources
- **@OAIS_community** — archivage OAIS
- **@IIIF_io** — IIIF Community
- **Digital Preservation Coalition** — https://www.dpconline.org
- **The Signal (Library of Congress)** — blog préservation numérique
- **D-Lib Magazine** — (archivé, mais ressource historique majeure)

### Dépôts GitHub à suivre
- `DSpace/DSpace` — https://github.com/DSpace/DSpace
- `fcrepo/fcrepo` — https://github.com/fcrepo/fcrepo
- `samvera-labs/hyrax` — https://github.com/samvera/hyrax
- `inveniosoftware/invenio` — https://github.com/inveniosoftware
- `artefactual/archivematica` — https://github.com/artefactual/archivematica
- `kermitt2/grobid` — https://github.com/kermitt2/grobid
- `tesseract-ocr/tesseract` — https://github.com/tesseract-ocr/tesseract
- `OCR-D/core` — https://github.com/OCR-D/core
- `IIIF/api` — https://github.com/IIIF/api

### Hashtags pour suivis
- `#DigitalLibraries` `#OpenAccess` `#OAIS` `#Metadata` `#IIIF`
- `#DigitalPreservation` `#OCRs` `#LinkedData` `#SPARQL` `#BIBFRAME`
- `#OpenScience` `#PlanS` `#DigitalHumanities` `#DH` `#TEI`

### Recommandations méthodologiques

1. **Modélisation des données** : toujours partir d'un schéma de métadonnées existant (Dublin Core pour le minimal, MODS/METS pour le bibliographique complet, CIDOC-CRM pour le patrimoine)
2. **Stockage pérenne** : suivre le modèle OAIS (SIP → AIP → DIP), compatible BagIt
3. **Identifiants** : tout objet numérique doit avoir un identifiant pérenne (DOI ou ARK) résolvable via Handle
4. **Interopérabilité** : privilégier OAI-PMH, IIIF (flux images), APIs REST, et exports RDF/JSON-LD
5. **Recherche** : utiliser Elasticsearch ou Solr avec indexation full-text + facettes + métadonnées
6. **OCR** : pipeline optimal = Kraken/eScriptorium (documents historiques) ou Tesseract + GROBID (publications modernes)
7. **Science ouverte** : déposer dans une archive ouverte (HAL, arXiv, Zenodo) et attribuer un ORCID
8. **Humanités numériques** : adopter TEI pour les textes, IIIF pour les images, et visualisations interactives en D3.js/Vega-Lite

---

## Commandes utiles

### Installation rapide des outils CLI

```bash
# Tesseract OCR
sudo apt install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng

# GROBID (docker)
docker pull grobid/grobid:latest

# Elasticsearch (via apt ou docker)
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.x.x

# Outils de métadonnées
pip install pyoai oaipmh-scythe pybtex pandas

# Extraction et conversion
pip install pymarc pymods pdfplumber openpyxl
```

### Exemple : moissonnage OAI-PMH

```python
# Récupération de notices depuis une archive ouverte via OAI-PMH
from oaipmh_scythe import Scythe

client = Scythe("https://api.archives-ouvertes.fr/oai/hal/")
records = client.list_records(metadata_prefix="oai_dc", set="cs")
for record in records:
    header, metadata, about = record
    # Traiter les métadonnées Dublin Core
    print(metadata.getField("title"))
```

### Exemple : requête SPARQL sur un endpoint

```sparql
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
SELECT ?title ?creator ?date
WHERE {
  ?s dc:title ?title ;
     dc:creator ?creator ;
     dcterms:date ?date .
  FILTER(LANG(?title) = "fr")
}
LIMIT 20
```

### Exemple : extraction GROBID (XML → texte)

```bash
# Lancer le service
docker run -d --rm --name grobid -p 8070:8070 grobid/grobid:latest

# ENPOST: Envoyer un PDF vers GROBID pour extraction
curl -X POST -F "input=@/path/to/article.pdf" \
  http://localhost:8070/api/processFulltextDocument \
  -o article.tei.xml
```

---

## Références bibliographiques

- Térmens, M. (2023). *Digital Preservation in Libraries: Preparing for a Sustainable Future*. ALA Editions.
- Zeng, M. L., & Qin, J. (2024). *Metadata*. 3rd ed. ALA Neal-Schuman.
- Svenonius, E. (2009). *The Intellectual Foundation of Information Organization*. MIT Press.
- Besser, H. (2004). *Introduction to Digital Libraries*. UCLA.
- Preservation and Archiving Special Interest Group (PASIG) — rapports techniques.
- IFLA (International Federation of Library Associations and Institutions) — *Metadata Resources*.
