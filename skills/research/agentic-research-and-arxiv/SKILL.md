---
name: agentic-research-and-arxiv
description: "Veille scientifique et extraction d'insights sur arXiv."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
tags: [arxiv, recherche, veille-scientifique, extraction-connaissances, agentic-skills]
keywords: [arXiv API, crawling académique, synthèse de littérature, skill-generation]
---

# Recherche Agentique à partir de Sources Académiques

## Vue d'ensemble

La recherche agentique désigne la capacité d'un agent IA à conduire de manière autonome une revue de littérature scientifique, à en extraire les concepts clés, et à les transformer en compétences réutilisables (skills). Cette compétence formalise un pipeline complet allant de la formulation de requêtes ciblées sur des dépôts comme arXiv jusqu'à la génération de nouvelles capacités agentiques.

L'objectif est double :

1. **Automatiser la veille** : remplacer les recherches manuelles répétitives par un agent capable d'interroger des API, de filtrer les résultats et de hiérarchiser les articles pertinents.
2. **Capitaliser les découvertes** : convertir les résultats de recherche en fichiers `SKILL.md` opérationnels, intégrés au catalogue de l'agent.

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Vous devez suivre l'état de l'art sur un domaine en évolution rapide (ex. systèmes multi-agents, RLHF, agents LLM) | Élevée |
| Vous souhaitez générer automatiquement des fiches de compétences à partir de papiers de recherche | Élevée |
| Vous explorez un nouveau champ de recherche et avez besoin d'une synthèse structurée | Moyenne |
| Vous cherchez un article spécifique dont vous connaissez déjà l'identifiant | Faible (préférer une requête directe) |

---

## Architecture du pipeline de recherche

```
[Requête] → [API arXiv] → [Filtrage & Extraction] → [Synthèse] → [Génération SKILL.md]
    ↑                                                                       |
    └────────────── Boucle d'itération (affinement des mots-clés) ──────────┘
```

---

## 1. Identification des domaines cibles

### 1.1 Catégories arXiv pertinentes

| Catégorie | Sous-catégories recommandées | Domaine |
|---|---|---|
| `cs.AI` | Intelligence Artificielle | Généraliste |
| `cs.MA` | Multi-Agent Systems | Systèmes multi-agents |
| `cs.LG` | Machine Learning | Apprentissage automatique |
| `cs.CL` | Computation and Language | NLP, LLM |
| `cs.RO` | Robotics | Robotique |
| `stat.ML` | Machine Learning (statistique) | Méthodes bayésiennes |
| `math.OC` | Optimization and Control | Optimisation |

### 1.2 Affinage par domaine spécifique

Pour les recherches ciblées, combinez une catégorie avec des mots-clés :

```python
# Exemple de sélection de catégories cibles
CATEGORIES_CIBLES = {
    "systemes_multi_agents": ["cs.MA", "cs.AI"],
    "planification_taches": ["cs.AI", "cs.RO"],
    "apprentissage_renforcement": ["cs.LG", "stat.ML"],
    "industrie_4.0": ["cs.AI", "cs.SY", "eess.SY"],
}
```

---

## 2. Interrogation des API de dépôts académiques

### 2.1 API arXiv — Requêtes avancées

L'API arXiv expose une interface REST simple. La construction de la requête respecte le format :

```
https://export.arxiv.org/api/query?search_query=QUERY&start=0&max_results=N&sortBy=relevance&sortOrder=descending
```

#### Opérateurs booléens

| Opérateur | Rôle | Exemple |
|---|---|---|
| `AND` | Intersection stricte | `all:multi-agent AND all:reinforcement+learning` |
| `OR` | Union large | `all:transformer OR all:attention+mechanism` |
| `ANDNOT` | Exclusion | `all:robot ANDNOT all:hardware` |

#### Exemple complet avec `curl`

```bash
curl -s "https://export.arxiv.org/api/query?search_query=\
(all:\"multi-agent+systems\"+AND+all:\"task+planning\")+\
AND+cat:cs.AI&start=0&max_results=15&sortBy=submittedDate&sortOrder=descending" \
| grep -oP '<id>https?://arxiv\.org/abs/\K[^<]+'
```

> **Note** : L'API arXiv limite chaque requête à `max_results=300` maximum. Pour les recherches volumineuses, utilisez le paramètre `start` pour paginer (`start=0`, `start=100`, ...).

### 2.2 API Semantic Scholar (complément)

Semantic Scholar fournit des métriques de citation et des recommandations :

```python
import requests, json

def chercher_semantic_scholar(requete: str, limite: int = 10) -> list[dict]:
    """Recherche des articles via l'API Semantic Scholar.

    Args:
        requete: Termes de recherche.
        limite: Nombre maximum de résultats.

    Returns:
        Liste de dictionnaires avec titre, résumé, année, nombre de citations.
    """
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {"query": requete, "limit": limite, "fields": "title,abstract,year,citationCount"}
    reponse = requests.get(url, params=params)
    reponse.raise_for_status()
    return reponse.json().get("data", [])
```

### 2.3 Parsing XML des réponses arXiv

Les réponses de l'API arXiv sont au format Atom XML. Voici un parseur robuste :

```python
import xml.etree.ElementTree as ET

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}

def extraire_articles(xml_brut: str) -> list[dict]:
    """Extrait les métadonnées des articles depuis une réponse XML arXiv.

    Args:
        xml_brut: Réponse XML brute de l'API arXiv.

    Returns:
        Liste d'articles avec titre, résumé, lien PDF, auteurs, catégories.
    """
    root = ET.fromstring(xml_brut)
    articles = []
    for entry in root.findall("atom:entry", NAMESPACES):
        article = {
            "id": entry.find("atom:id", NAMESPACES).text.strip(),
            "titre": entry.find("atom:title", NAMESPACES).text.strip().replace("\n", " "),
            "resume": entry.find("atom:summary", NAMESPACES).text.strip().replace("\n", " "),
            "pdf": entry.find("atom:link[@title='pdf']", NAMESPACES).attrib["href"],
            "auteurs": [a.find("atom:name", NAMESPACES).text for a in entry.findall("atom:author", NAMESPACES)],
            "categories": [c.attrib["term"] for c in entry.findall("atom:category", NAMESPACES)],
        }
        articles.append(article)
    return articles
```

---

## 3. Extraction et synthèse des insights

### 3.1 Critères de filtrage

Une fois les articles récupérés, appliquez une grille de notation pour hiérarchiser leur pertinence :

| Critère | Pondération | Description |
|---|---|---|
| Alignement sémantique | 40 % | Correspondance entre le résumé et le domaine cible |
| Nouveauté | 25 % | Date de soumission (< 6 mois = score max) |
| Impact | 20 % | Nombre de citations (via Semantic Scholar) |
| Applicabilité agentique | 15 % | Potentiel de transformation en compétence réutilisable |

### 3.2 Génération de compétence à partir d'un article

```python
def generer_skill_depuis_article(article: dict) -> str:
    """Génère un squelette de fichier SKILL.md à partir d'un article.

    Args:
        article: Dictionnaire contenant les métadonnées de l'article.

    Returns:
        Contenu markdown du fichier SKILL.md.
    """
    nom_skill = article["titre"].lower().replace(" ", "-")[:50]
    return f"""---
name: {nom_skill}
description: "Compétence générée depuis l'article : {article['titre']}"
version: 1.0.0
author: Généré automatiquement
license: Privée EVA St-Étienne
plateformes: [linux, macos, windows]
source: {article['id']}
---

# {article['titre']}

## Résumé de l'article

{article['resume'][:500]}

## Insights clés pour l'agent

<!-- Insights extraits automatiquement — à réviser manuellement -->

## Implémentation suggérée

<!-- À compléter avec des extraits de code ou des patrons d'appel outil -->

## Références

- PDF : {article['pdf']}
- Catégories : {', '.join(article['categories'])}
"""
```

---

## 4. Pièges courants (Pitfalls)

### 4.1 Requêtes trop spécifiques ou trop larges

> **Problème** : Une requête comme `all:"exact phrase with many words that never appears"` renvoie zéro résultat, tandis que `all:agent` renvoie des milliers d'articles non pertinents.

**Solution** : Utilisez la méthode de la pyramide. Commencez large (`all:reinforcement+learning`), puis ajoutez des filtres un par un (`AND all:multi-agent`, `AND cat:cs.MA`).

### 4.2 Ignorer les limites de taux de l'API

> **Problème** : L'API arXiv bloque les requêtes excessives (plus d'une requête toutes les 3 secondes).

**Solution** : Implémentez un délai entre les requêtes :

```python
import time

def requete_avec_backoff(url: str, tentatives: int = 3) -> str:
    """Effectue une requête HTTP avec backoff exponentiel."""
    for i in range(tentatives):
        try:
            reponse = requests.get(url, timeout=30)
            reponse.raise_for_status()
            return reponse.text
        except requests.RequestException:
            if i == tentatives - 1:
                raise
            time.sleep(2 ** i)
    return ""
```

### 4.3 Oublier les préférences de tri

> **Problème** : Par défaut, arXiv trie par **pertinence**, pas par date. Les articles les plus récents peuvent être noyés.

**Solution** : Spécifiez toujours `sortBy=submittedDate&sortOrder=descending` pour la veille chronologique.

### 4.4 Confondre résumé et contenu intégral

> **Problème** : Le résumé (abstract) ne contient pas toujours les détails d'implémentation nécessaires pour créer une compétence.

**Solution** : Après filtrage sur résumé, téléchargez le PDF (`web_extract` ou `browser`) pour une analyse approfondie des sections "Method" et "Experiments".

---

## 5. Checklist de validation

- [ ] La requête arXiv utilise-t-elle des opérateurs booléens appropriés (`AND` / `OR`) ?
- [ ] La catégorie arXiv est-elle spécifiée (`cat:cs.MA`) pour réduire le bruit ?
- [ ] Le tri par date est-il activé pour les recherches de veille ?
- [ ] Les limites de taux de l'API sont-elles respectées (délai ≥ 3 s) ?
- [ ] Les résultats sont-ils filtrés par seuil de pertinence (alignement sémantique ≥ 50 %) ?
- [ ] Les articles retenus ont-ils été analysés au-delà du résumé (PDF ou HTML) ?
- [ ] Une fiche SKILL.md a-t-elle été générée pour chaque article retenu ?
- [ ] Les métadonnées (DOI, arXiv ID, catégories) sont-elles conservées dans le frontmatter ?
- [ ] Les dépendances logicielles (BeautifulSoup, requests, lxml) sont-elles installées ?
- [ ] Le pipeline est-il reproductible (script paramétré, pas d'étapes manuelles) ?

---

## 6. Extensions et intégrations

### 6.1 Veille automatisée (cron)

Combinez cette compétence avec le planificateur cron d'EVA pour une exécution périodique :

```yaml
# Configuration cron pour veille hebdomadaire
veille_arxiv:
  schedule: "0 9 * * 1"         # Tous les lundis à 9h
  skill: agentic-research-and-arxiv
  params:
    categories: ["cs.MA", "cs.AI"]
    mots_cles: ["multi-agent", "task planning", "coordination"]
    max_results: 20
    generer_skills: true
```

### 6.2 Combinaison avec d'autres compétences

- **`research-multi-agent-complex-tasks`** : pour approfondir les aspects planification de tâches.
- **`rag-retrieval-augmented-generation`** : pour intégrer les articles récupérés dans un pipeline RAG.
- **`semantic-scholar-queries`** : pour enrichir les données de citation.

---

## 7. Ressources associées

- `references/arxiv_search_patterns.md` : Catalogue de requêtes pré-construites par domaine.
- `references/research-first-approach.md` : Règle comportementale : toujours chercher sur le web avant d'improviser quand les compétences sont absentes.
- `scripts/arxiv_bulk_search.py` : Script pour la recherche par lots avec pagination automatique.
- `scripts/generate_skill_from_papers.py` : Générateur de squelettes SKILL.md.

---

*Documentation maintenue par EVA Agent — Dernière mise à jour : 2025*
