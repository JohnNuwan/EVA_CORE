---
name: research-multi-agent-complex-tasks
description: "Stratégies avancées pour rechercher, analyser et synthétiser la littérature académique sur les systèmes multi-agents appliqués à la planification et l'exécution de tâches complexes."
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, windows, macos]
tags: [multi-agent systems, task planning, arxiv, collaboration, complex tasks, planification, recherche-académique]
keywords: [multi-agent, task decomposition, collaborative planning, complex task execution, literature survey]
---

# Recherche sur les Systèmes Multi-Agents et la Planification de Tâches Complexes

## Vue d'ensemble

Les systèmes multi-agents (MAS) appliqués à la planification de tâches complexes représentent un domaine de recherche actif à l'intersection de l'intelligence artificielle, de la robotique et de l'orchestration de systèmes. Cette compétence guide la **recherche systématique** de publications académiques sur ce thème, avec un accent particulier sur arXiv et Semantic Scholar.

La planification de tâches complexes dans un contexte multi-agents soulève des défis spécifiques :

1. **Décomposition** : Comment découper une tâche globale en sous-tâches assignables à chaque agent ?
2. **Coordination** : Comment synchroniser les actions des agents sans conflit ?
3. **Communication** : Quel protocole pour partager l'état d'avancement ?
4. **Réallocation dynamique** : Comment réattribuer les tâches en cas de défaillance d'un agent ?

---

## Quand utiliser cette compétence

| Scénario | Pertinence |
|---|---|
| Exploration de l'état de l'art sur les MAS pour la planification | Élevée |
| Recherche de nouvelles méthodes de décomposition de tâches (Task Decomposition) | Élevée |
| Identification de benchmarks et environnements de test pour MAS | Élevée |
| Veille sur les publications récentes (architectures LLM-based agents) | Élevée |
| Recherche rapide d'un article spécifique (arXiv ID connu) | Faible |

---

## 1. Stratégies de recherche sur arXiv

### 1.1 Requêtes ciblées par sous-domaine

| Sous-domaine | Requête arXiv recommandée |
|---|---|
| Planification multi-agents | `all:"multi-agent" AND all:"task planning"` |
| Coordination | `all:"multi-agent coordination" AND all:"complex"` |
| Décomposition de tâches | `all:"task decomposition" AND all:"multi-agent"` |
| Collaboration LLM | `all:"large language model" AND all:"multi-agent collaboration"` |
| Planification hiérarchique | `all:"hierarchical planning" AND all:"multi-agent"` |

### 1.2 Requêtes avancées avec opérateurs

```bash
# Recherche combinée : planification + décomposition en MAS
curl -s "https://export.arxiv.org/api/query?\
search_query=(all:\"multi-agent\"+AND+all:\"planning\")+\
AND+cat:cs.AI&\
start=0&max_results=30&\
sortBy=relevance&sortOrder=descending" > resultats.xml

# Recherche focalisée : agents LLM pour tâches complexes
curl -s "https://export.arxiv.org/api/query?\
search_query=(all:\"LLM+agent\"+OR+all:\"language+agent\")+\
AND+(all:\"task+decomposition\"+OR+all:\"tool+use\")+\
AND+cat:cs.AI&\
start=0&max_results=20&\
sortBy=submittedDate&sortOrder=descending" > resultats_llm.xml
```

### 1.3 Extraction automatique depuis arXiv

```python
import xml.etree.ElementTree as ET
import requests
from typing import Any

class RechercheArxivMAS:
    """Moteur de recherche spécialisé pour les publications MAS sur arXiv."""

    URL_BASE = "https://export.arxiv.org/api/query"
    CATEGORIES_PRIORITAIRES = ["cs.AI", "cs.MA", "cs.LG", "cs.RO", "cs.SY"]

    def chercher(self, termes: str, max_resultats: int = 20,
                 tri: str = "relevance") -> list[dict[str, Any]]:
        """Recherche des articles sur arXiv avec paramètres optimisés pour MAS.

        Args:
            termes: Termes de recherche avec opérateurs.
            max_resultats: Nombre maximum de résultats (max 300).
            tri: 'relevance' ou 'submittedDate'.

        Returns:
            Liste d'articles avec métadonnées complètes.
        """
        params = {
            "search_query": f"({termes})",
            "start": 0,
            "max_results": min(max_resultats, 300),
            "sortBy": tri,
            "sortOrder": "descending",
        }

        try:
            reponse = requests.get(self.URL_BASE, params=params, timeout=30)
            reponse.raise_for_status()
            return self._extraire_articles(reponse.text)
        except requests.RequestException as e:
            print(f"Erreur de recherche arXiv : {e}")
            return []

    def _extraire_articles(self, xml_brut: str) -> list[dict[str, Any]]:
        """Extrait les articles du XML de réponse arXiv.

        Args:
            xml_brut: Réponse XML de l'API arXiv.

        Returns:
            Liste d'articles structurés.
        """
        namespace = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }
        root = ET.fromstring(xml_brut)
        articles = []

        for entry in root.findall("atom:entry", namespace):
            categories = [
                cat.attrib["term"]
                for cat in entry.findall("atom:category", namespace)
            ]

            # Filtrer par catégories prioritaires
            if not any(cat in self.CATEGORIES_PRIORITAIRES for cat in categories):
                continue

            resume = entry.find("atom:summary", namespace)
            resume_texte = resume.text.strip().replace("\n", " ") if resume is not None else ""

            articles.append({
                "id": entry.find("atom:id", namespace).text.strip(),
                "titre": entry.find("atom:title", namespace).text.strip().replace("\n", " "),
                "resume": resume_texte,
                "categories": categories,
                "date": entry.find("atom:published", namespace).text.strip(),
                "auteurs": [
                    a.find("atom:name", namespace).text
                    for a in entry.findall("atom:author", namespace)
                ],
                "lien_pdf": next(
                    (l.attrib["href"] for l in entry.findall("atom:link", namespace)
                     if l.attrib.get("title") == "pdf"),
                    "",
                ),
            })

        return articles
```

---

## 2. Enrichissement via Semantic Scholar

### 2.1 Récupération des métadonnées de citation

Semantic Scholar fournit des métriques d'impact (nombre de citations) et des recommandations :

```bash
# Récupérer les données de citation pour un arXiv ID spécifique
curl -s "https://api.semanticscholar.org/graph/v1/paper/arXiv:2305.12345?fields=title,citationCount,influentialCitationCount" | json_pp

# Recherche par titre
curl -s "https://api.semanticscholar.org/graph/v1/paper/search?query=multi-agent+task+planning&limit=10&fields=title,year,citationCount,abstract"
```

### 2.2 Implémentation Python

```python
class EnrichisseurSemanticScholar:
    """Enrichit les résultats arXiv avec les données de citation Semantic Scholar."""

    URL_RECHERCHE = "https://api.semanticscholar.org/graph/v1/paper/search"
    URL_PAPIER = "https://api.semanticscholar.org/graph/v1/paper/"

    def enrichir_articles(self, articles: list[dict]) -> list[dict]:
        """Ajoute les métriques de citation aux articles arXiv.

        Args:
            articles: Liste d'articles récupérés depuis arXiv.

        Returns:
            Articles enrichis avec citationCount, influentialCitationCount.
        """
        articles_enrichis = []
        for article in articles:
            # Extraire l'ID arXiv
            arxiv_id = article["id"].split("/")[-1]
            if arxiv_id.startswith("arXiv:"):
                arxiv_id = arxiv_id[6:]

            citations = self._recuperer_citations(arxiv_id)
            article["citation_count"] = citations.get("citationCount", 0)
            article["citations_influentes"] = citations.get("influentialCitationCount", 0)
            articles_enrichis.append(article)

        return sorted(
            articles_enrichis,
            key=lambda a: a.get("citation_count", 0),
            reverse=True,
        )

    def _recuperer_citations(self, arxiv_id: str) -> dict:
        """Récupère les métriques de citation pour un arXiv ID.

        Args:
            arxiv_id: Identifiant arXiv (ex. '2305.12345').

        Returns:
            Dictionnaire avec citationCount et influentialCitationCount.
        """
        try:
            reponse = requests.get(
                f"{self.URL_PAPIER}arXiv:{arxiv_id}",
                params={"fields": "citationCount,influentialCitationCount"},
                timeout=10,
            )
            if reponse.status_code == 200:
                return reponse.json()
        except requests.RequestException:
            pass

        return {"citationCount": 0, "influentialCitationCount": 0}
```

---

## 3. Synthèse et priorisation des articles

### 3.1 Grille de notation MAS

| Critère | Pondération | Questions d'évaluation |
|---|---|---|
| **Pertinence MAS** | 30 % | L'article traite-t-il explicitement de systèmes multi-agents ? |
| **Qualité planification** | 25 % | La méthode de planification est-elle détaillée et reproductible ? |
| **Tâches complexes** | 20 % | Les tâches étudiées sont-elles non-triviales (≥ 3 sous-tâches) ? |
| **Évaluation** | 15 % | Y a-t-il des benchmarks, environnements de test, métriques claires ? |
| **Reproductibilité** | 10 % | Le code source ou les données sont-ils disponibles ? |

### 3.2 Exemple d'analyse d'article

```python
class AnalyseurArticleMAS:
    """Analyse et note un article selon la grille MAS."""

    def analyser(self, article: dict) -> dict:
        """Analyse un article et produit une fiche structurée.

        Args:
            article: Article avec métadonnées (titre, résumé, catégories, etc.).

        Returns:
            Fiche d'analyse complète avec score et recommandation.
        """
        resume = article.get("resume", "").lower()
        titre = article.get("titre", "").lower()

        # Analyse heuristique du résumé
        mots_mas = {"multi-agent", "agent", "coordination", "cooperative"}
        mots_planification = {"planning", "plan", "scheduling", "decomposition"}
        mots_complexite = {"complex", "hierarchical", "large-scale"}

        score_mas = sum(1 for m in mots_mas if m in resume) / len(mots_mas)
        score_planification = sum(1 for m in mots_planification if m in resume) / len(mots_planification)
        score_complexite = sum(1 for m in mots_complexite if m in resume) / len(mots_complexite)

        score_total = (score_mas * 0.30 + score_planification * 0.25 +
                       score_complexite * 0.20)

        # Bonus pour les articles cités
        if article.get("citation_count", 0) > 50:
            score_total += 0.15
        elif article.get("citation_count", 0) > 10:
            score_total += 0.10

        note = min(score_total * 100, 100)

        return {
            "titre": article.get("titre", ""),
            "score": round(note, 1),
            "categorie_domaine": self._classifier(article.get("categories", [])),
            "mots_cles_extraits": self._extraire_mots_cles(resume),
            "recommendation": "À lire" if note >= 70 else "Référence secondaire" if note >= 40 else "Faible priorité",
        }

    def _classifier(self, categories: list[str]) -> str:
        """Classe l'article dans un sous-domaine MAS."""
        if "cs.MA" in categories:
            return "Systèmes multi-agents"
        elif "cs.AI" in categories:
            return "IA générale"
        elif "cs.RO" in categories:
            return "Robotique"
        return "Domaine connexe"

    def _extraire_mots_cles(self, resume: str) -> list[str]:
        """Extrait les mots-clés caractéristiques du résumé."""
        mots_cles_cibles = [
            "task decomposition", "coordination", "communication",
            "reinforcement learning", "hierarchical", "emergence",
            "consensus", "negotiation", "distributed", "collaborative",
        ]
        return [mc for mc in mots_cles_cibles if mc in resume]
```

---

## 4. Veille continue et mise à jour

### 4.1 Script de veille hebdomadaire

```bash
#!/bin/bash
# Veille hebdomadaire : Systèmes multi-agents et planification

RAPPORT="veille_mas_$(date +%Y-%m-%d).md"

echo "# Veille MAS — $(date)" > "$RAPPORT"

# 1. Nouveautés arXiv
for QUERY in \
    '"multi-agent" AND "task planning"' \
    '"multi-agent" AND "coordination"' \
    '"LLM agent" AND "decomposition"'; do

    echo -e "\n## Requête : $QUERY\n" >> "$RAPPORT"
    ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")

    curl -s "https://export.arxiv.org/api/query?\
search_query=${ENCODED}+AND+cat:cs.AI&\
start=0&max_results=5&\
sortBy=submittedDate&sortOrder=descending" \
    | python3 -c "
import sys, xml.etree.ElementTree as ET
ns = {'atom': 'http://www.w3.org/2005/Atom'}
root = ET.fromstring(sys.stdin.read())
for e in root.findall('atom:entry', ns):
    title = e.find('atom:title', ns).text.strip().replace('\n', ' ')
    arxiv_id = e.find('atom:id', ns).text.split('/')[-1]
    print(f'- [{title}](https://arxiv.org/abs/{arxiv_id})')
" >> "$RAPPORT"
done

echo -e "\n---\n_Veille générée le $(date)_" >> "$RAPPORT"
```

### 4.2 Configuration cron

Ajoutez cette tâche au planificateur Helios ou au cron système :

```yaml
# Exemple de configuration cron pour la veille MAS
veille_mas_hebdo:
  schedule: "0 8 * * 1"  # Tous les lundis à 8h
  skill: research-multi-agent-complex-tasks
  params:
    requetes:
      - '"multi-agent" AND "planning" AND cat:cs.AI'
      - '"task decomposition" AND cat:cs.AI'
      - '"LLM agent" AND cat:cs.MA'
    max_resultats: 10
    stocker_dans: "veille/"
```

---

## 5. Pièges courants (Pitfalls)

### 5.1 Confusion entre agentification et agentivité

> **Problème** : De nombreux articles utilisent le terme "agent" pour désigner n'importe quel composant logiciel, pas un véritable agent autonome.

**Solution** : Vérifiez la présence de mécanismes d'autonomie : prise de décision, communication, apprentissage. Un agent purement réactif (règle si-alors) n'est pas un "agent" au sens MAS.

### 5.2 Benchmark non standardisé

> **Problème** : Chaque article utilise ses propres métriques et environnements, rendant les comparaisons impossibles.

**Solution** : Privilégiez les articles utilisant des benchmarks reconnus :
- **SMAC** (StarCraft Multi-Agent Challenge)
- **Overcooked-AI** (coordination humaine-IA)
- **MetaWorld** / **ALFRED** (tâches robotiques)
- **MULTI-BENCH** (benchmark unification)

### 5.3 Sur-spécialisation des requêtes

> **Problème** : Des mots-clés trop spécifiques (ex. `"hierarchical task network AND multi-agent AND auction-based"`) renvoient zéro résultats.

**Solution** : Utilisez la méthode **large → narrow** : commencez par `all:"multi-agent" AND all:"planning"` (large), puis affinez en ajoutant des filtres un par un.

### 5.4 Ignorer les articles de référence (seminal papers)

> **Problème** : Les articles récents manquent de contexte sur les travaux fondateurs du domaine.

**Solution** : Cherchez aussi avec `sortBy=relevance` et examinez les articles les plus cités. Semantic Scholar est idéal pour identifier les papiers influents.

---

## 6. Checklist de validation

- [ ] Les requêtes arXiv utilisent-elles des opérateurs booléens et des catégories ?
- [ ] Les catégories cibles incluent-elles `cs.AI`, `cs.MA`, `cs.RO` ?
- [ ] Les résultats sont-ils filtrés par date (priorité aux 12 derniers mois) ?
- [ ] Un enrichissement par Semantic Scholar (citations) a-t-il été effectué ?
- [ ] La grille de notation MAS a-t-elle été appliquée aux articles ?
- [ ] Les articles retenus utilisent-ils des benchmarks standardisés (SMAC, etc.) ?
- [ ] Les articles fondateurs (seminal papers, citations > 100) sont-ils identifiés ?
- [ ] Une veille continue est-elle configurée (cron, script automatisé) ?
- [ ] Les dépendances (requests, lxml) sont-elles installées ?
- [ ] Les résultats sont-ils consolidés dans un rapport structuré (markdown) ?

---

## 7. Compétences complémentaires

- **`agentic-research-and-arxiv`** : pour la recherche académique généraliste (arXiv, crawling).
- **`multi-agent-reinforcement-learning`** : pour approfondir les aspects MARL (entraînement, coordination).
- **`creative-problem-solving-ai`** : pour les méthodes de résolution créative appliquées aux MAS.
- **`exploration-industry4-ai`** : pour l'application des MAS dans le contexte Industrie 4.0.

---

## 8. Références

- `references/mas_arxiv_queries.md` : catalogue de 50+ requêtes pré-construites pour arXiv.
- `scripts/mas_literature_survey.py` : pipeline complet d'enquête de littérature MAS.
- `templates/mas_paper_review_template.md` : template de fiche de lecture d'article MAS.

---

*Documentation maintenue par Helios Agent — Dernière mise à jour : 2025*
