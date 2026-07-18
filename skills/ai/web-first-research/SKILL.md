---
name: web-first-research
description: "Recherche web prioritaire de nouvelles compétences."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: production
    tags: [web-research, search, information-retrieval, acquisition]
    related_skills: [agent-knowledge-gap-resolution, experiential-self-improvement, jepa-joint-embedding-predictive]
---

# Recherche Web Prioritaire (Web-First Research)

## Rôle et Identité
Vous êtes un agent d'acquisition cognitive et d'ingénierie de recherche documentaire. Lorsque vous êtes confronté à un manque de compétences locales ou de documentation sur une technologie/architecture, vous devez appliquer le protocole de recherche prioritaire sur le web ("Web-First Research") pour acquérir des informations fiables avant toute tentative de conception.

## Vue d'ensemble
Les agents IA ont tendance à improviser ou à halluciner des syntaxes d'API lorsqu'ils manquent d'informations à jour. Cette compétence formalise un processus structuré de recherche et d'acquisition de connaissances en ligne. Au lieu de démarrer le codage d'une bibliothèque inconnue ou d'un protocole complexe, l'agent suspend son exécution, interroge des sources web faisant autorité (arXiv, Siemens Support, documentations officielles), et distille l'information sous forme de spécification technique locale réutilisable.

---

## 1. Processus de Recherche et d'Acquisition (Retrieval Flow)

```
[Suget Inconnu] ──► Évaluation du Besoin ──► Formulation de Requêtes Cibles
                                                    │
    ┌───────────────────────────────────────────────┘
    ▼
[Recherche Multi-Sources] (arXiv, GitHub, Siemens, OPC)
    │
    ▼
[Extraction Propre via BeautifulSoup] (Conversion HTML en Markdown épuré)
    │
    ▼
[Synthèse et Archivage] (Mise à jour de sources.md ou création de skill)
```

### Directives d'Interrogation
*   **Filtrage par opérateur de domaine** : Limiter la recherche aux domaines officiels en utilisant les opérateurs de recherche.
    *   Exemple : `site:github.com/facebookresearch "jepa"` pour les dépôts originaux.
    *   Exemple : `site:support.industry.siemens.com "LHTTP_Post"` pour les blocs fonctionnels Siemens.
*   **Échantillonnage Temporel** : Inclure l'année en cours (ex: "2026") pour éviter de récupérer de la documentation obsolète ou dépréciée.

---

## 2. Directives Techniques de Programmation
*   **User-Agent Réaliste** : Toujours utiliser des en-têtes HTTP valides lors des requêtes HTTP pour éviter les blocages de sécurité (403 Forbidden).
*   **Élagage sémantique immédiat** : Convertir le HTML en Markdown épuré à l'aide de filtres BeautifulSoup (décomposition de `script`, `style`, `nav`, `footer`).
*   **Gestion des Erreurs robuste** : Capturer les exceptions de timeouts réseau ou de certificat SSL défectueux.

---

## 3. Exemple d'Écriture de Code : Pipeline de Recherche et d'Extraction

```python
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

class WebFirstSearchEngine:
    """Moteur de recherche et d'extraction documentaire épuré."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def execute_and_extract(self, url: str) -> str:
        """Télécharge la page et extrait le contenu textuel structuré."""
        req = urllib.request.Request(url, headers=self.headers)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                html = response.read().decode('utf-8', errors='ignore')
                soup = BeautifulSoup(html, 'html.parser')
                
                # Suppression du bruit
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                    
                body = soup.body if soup.body else soup
                return body.get_text(separator='\n').strip()
        except Exception as e:
            return f"Erreur de téléchargement : {e}"

```

---

## 4. Pièges Courants (Common Pitfalls)
*   **Bruit publicitaire et UI** : Charger et traiter l'intégralité d'un document HTML sans élagage préalable. Cela sature inutilement le contexte de l'agent.
*   **Interprétation hors contexte** : Récupérer des bribes d'exemples de code sur des forums (StackOverflow) sans les valider contre la documentation officielle de l'API.
*   **Snapshot navigateur vide sur les pages statiques** : Les pages raw (raw.githubusercontent.com, fichiers .md servis en texte brut) renvoient un snapshot vide dans le navigateur intégré. Utiliser `browser_console` avec `document.body.innerText` ou `document.querySelector('article')?.innerText` pour extraire le contenu textuel.
*   **Blocage des moteurs de recherche** : Google, Semantic Scholar et arXiv bloquent fréquemment les requêtes automatisées (CAPTCHA, erreurs d'encodage UTF-8). Privilégier les APIs directes (GitHub REST API, Hugging Face Hub, arXiv export API) plutôt que le parsing HTML des pages de résultats.
*   **Erreurs d'encodage UTF-8 du navigateur intégré** : Le snapshot navigateur peut échouer avec des `UnicodeDecodeError` sur certains sites (Reddit, GitHub, DuckDuckGo). Contournement : une fois sur UNE page qui a chargé (même partiellement), utiliser `browser_console` avec `fetch()` pour interroger des APIs JSON directement depuis le contexte de la page (ex: `fetch('https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=...&format=json').then(r=>r.json())`). Les APIs JSON ne souffrent pas des problèmes d'encodage du parser HTML. Autre variante : utiliser `browser_console` avec `Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('mot-clé')).map(a => a.href)` pour extraire des URLs depuis une page déjà chargée (ex: page de résultats TechCrunch), puis naviguer directement vers l'article.
*   **Fallback vers les agrégateurs de news tech** : Quand les moteurs de recherche généralistes échouent (Google CAPTCHA, Bing Cloudflare), aller directement sur des sites d'actualité tech qui ont leurs propres moteurs de recherche internes et une détection anti-bot moins agressive : TechCrunch (`techcrunch.com/?s=<query>`), The Verge, Ars Technica. Ces sites acceptent mieux le trafic automatisé que Google/Bing.
*   **Contenu tronqué par le snapshot** : Les articles longs (blogs Meta AI, documentation) sont tronqués à ~250 lignes dans le snapshot navigateur. `browser_scroll` + `browser_snapshot(full=true)` ne suffit pas toujours. Utiliser `browser_console` avec `document.body.innerText.substring(0, N)` pour extraire de larges portions de texte.
*   **Recherche non-exhaustive des variantes** : Se contenter du premier résultat ou du dépôt principal sans vérifier les projets dérivés, sous-projets, ou variantes au sein de la même organisation. Toujours rechercher l'organisation GitHub complète (`github.com/orgs/<org>/repositories?q=<topic>`) pour découvrir TOUS les repos liés. Exemple : JEPA compte 7 repos facebookresearch (ijepa, jepa, eb_jepa, jepa-wms, jepa-intuitive-physics, td_jepa, locate-3d), pas uniquement le principal.

---

## 5. Liste de vérification (Checklist)
- [ ] Déterminer précisément le sujet ou l'API manquante.
- [ ] Formuler une requête avec filtres de domaine (`site:`).
- [ ] Lancer l'extraction et nettoyer le HTML.
- [ ] Valider la fraîcheur des données (dates, versions).
- [ ] Archiver les résultats de manière structurée dans `sources.md`.

## 6. Exemple Concret d'Application

Voir [`references/session-example-jepa.md`](references/session-example-jepa.md) pour le récit complet d'une session où le protocole Web-First a permis de découvrir et documenter les 7 variantes de l'architecture JEPA (Meta AI) en partant de zéro skill local. Ce document détaille les techniques de contournement utilisées face aux blocages Google, Semantic Scholar et arXiv.

Voir [`references/recherche-concurrentielle-agents.md`](references/recherche-concurrentielle-agents.md) pour la méthodologie de recherche concurrentielle (agents IA coding, industriels) avec les sources qui fonctionnent (TechCrunch) et les pièges d'encodage UTF-8 rencontrés sur GitHub, Reddit, Bing et DuckDuckGo.

Voir [`references/recherche-open-source-github.md`](references/recherche-open-source-github.md) pour la méthodologie de recherche systématique de projets open-source sur GitHub via API REST multi-catégories — découverte de bibliothèques, frameworks et outils pouvant enrichir les capacités d'un agent AI, avec paramètres de requête, seuils de stars, parsing et structuration en fichier .md.

Voir [`references/integration-open-source.md`](references/integration-open-source.md) pour la méthodologie d'intégration de projets open-source sélectionnés dans EVA — extraction partielle, adaptation au pattern registry, règles de structuration.
