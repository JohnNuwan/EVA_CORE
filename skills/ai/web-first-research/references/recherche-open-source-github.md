# Méthodologie : Recherche Open-Source sur GitHub pour Amélioration d'Agent

> Session : Juillet 2026 — Découverte de projets open-source pour enrichir les capacités d'EVA Agent.
> Méthode : Systematic multi-category GitHub API search + structuration en fichier .md.

## Vue d'ensemble

Contrairement à la recherche concurrentielle (qui compare des produits), cette méthode vise à **découvrir des projets open-source tiers** qui pourraient être intégrés, forkés, ou servir d'inspiration architecturale pour améliorer un agent AI (nouvelles capacités, réduction de coûts, patterns).

---

## Phase 0 : Pré-filtrage par licence

**IMPORTANT** — Avant toute analyse détaillée, filtrer les projets par licence.

Pour un agent sous licence propriétaire (EVA), ne garder QUE les licences permissives :

| Licence | Statut | Compatible propriétaire |
|---------|--------|------------------------|
| **MIT** | ✅ Garder | Oui — aucune restriction |
| **Apache-2.0** | ✅ Garder | Oui — brevet + attribution |
| **BSD (2/3-clause)** | ✅ Garder | Oui — très permissive |
| **Unlicense / CC0** | ✅ Garder | Oui — domaine public |
| **LGPL** | ⚠️ Borderline | Peut être compatible si usage en bibliothèque non modifiée |
| **GPL / AGPL** | ❌ Supprimer | Non — copyleft forte, incompatible |
| **EPL / MPL** | ⚠️ Borderline | Copyleft faible — vérification recommandée |
| **NOASSERTION** | 🔍 Vérifier | Absence de licence explicite → risque legal |

**Règle pratique** : API GitHub retourne `license.spdx_id`. Filtrer avec un script :
```python
RESTRICTED = {"GPL", "AGPL", "LGPL", "EUPL", "CC-BY-NC", "NOASSERTION"}
if repo_license in RESTRICTED:
    skip = True
```

**Ne jamais recommander** un projet AGPL/GPL à intégrer dans un logiciel propriétaire — même partiellement — sans avertir explicitement du risque de contaminations.

---

## Phase 1 : Définir les catégories de recherche

Lister les domaines de capacités cibles. Exemple pour un agent AI :

```
1. Mémoire & contexte persistant
2. Optimisation des tokens / compression
3. RAG & recherche documentaire
4. MCP (Model Context Protocol)
5. Cadres multi-agents
6. Web scraping & extraction
7. Recherche & analyse autonome
8. Qualité, tests & revue de code
9. Skills & plugins écosystème
10. Sécurité & audit
11. Industriel, SCADA & automatisme
12. Voix, audio & multimodal
13. Anomalies, time series & prédiction
14. Auto-évolution & apprentissage
15. Interfaces & CLI
```

Adapter au domaine de l'agent (OT → industriel/SCADA/PLC/OPC-UA, etc.)

---

## Phase 2 : Requêtage GitHub API systématique

Utiliser l'API REST GitHub — plus fiable que le browser qui souffre d'erreurs d'encodage UTF-8 sur certains sites.

**Pattern de requête :**

```bash
curl -s "https://api.github.com/search/repositories?q=stars%3A%3E{seuil}+language%3Apython+topic%3A{categorie}&sort=stars&order=desc&per_page=20" \
  -H "Accept: application/vnd.github.v3+json"
```

**Variantes de filtres :**

| Critère | Syntaxe | Exemple |
|---------|---------|---------|
| Stars minimum | `stars:>2000` | `stars:>3000` pour les gros projets |
| Langage | `language:python` | `language:rust` pour niches |
| Topic | `topic:ai-agent` | `topic:plc` pour industriel |
| Multiple topics | `+topic:ai+topic:mcp` | Combine via `+` |
| Date | `pushed:>2026-01-01` | Pour fraîcheur |
| Licence (API GitHub ne filtre pas directement — post-filtrer) | — | Post-analyse via `license.spdx_id` |

**Seuils recommandés par catégorie :**
- Catégories populaires (AI, agent, MCP, memory) : `>3000` stars
- Catégories matures (RAG, scraping, test) : `>2000` stars
- Niches (PLC, SCADA, OPC-UA, industriel) : `>500` stars

---

## Phase 3 : Analyse et enrichissement

Pour chaque projet trouvé, extraire :
- Nom + propriétaire (full_name)
- ★ Stars (indique adoption/maturité)
- Description (premiers 120 chars suffisent)
- Topics (tags GitHub — fiabilité du domaine)
- **Licence** (compatibilité — CRITIQUE, voir Phase 0)
- Date de création (age du projet)

**Script de parsing avec filtre licence :**
```bash
curl -s "https://api.github.com/search/repositories?q=stars%3A%3E2000+language%3Apython+topic%3A{mcp}&sort=stars&order=desc" \
  -H "Accept: application/vnd.github.v3+json" 2>&1 | python3 -c "
import json,sys
data=json.load(sys.stdin)
RESTRICTED = ('AGPL','GPL','LGPL','EUPL','NOASSERTION')
for i in data.get('items',[]):
    lic = i.get('license',{})
    lic_id = lic.get('spdx_id','') if lic else ''
    if lic_id in RESTRICTED:
        continue  # ← FILTRE LICENCE
    print(f\"{i['stargazers_count']:>6} ★ | {i['full_name']:45s} | {lic_id:12s} | {i['description'][:100] if i['description'] else ''}\")
"
```

Pour les projets intéressants, creuser en détail via l'API :
```bash
curl -s "https://api.github.com/repos/{owner}/{repo}"
```

---

## Phase 4 : Structuration et livraison

Le document final doit être organisé par catégories avec, pour chaque entrée :
- Lien GitHub cliquable
- ★ Stars
- Description courte (≤ 120 chars)
- Licence
- Recommandation "💡 Pour [nom agent]" : 2-3 phrases d'analyse

Terminer par un **Top 10 synthétique** (projets avec le plus fort impact potentiel, TOUS à licence permissive) et une section **Méthodologie** décrivant les paramètres de recherche.

---

## Phase 5 : Intégration sélective (post-recherche)

Après sélection des projets, **ne pas tout importer en bloc**. Pour chaque projet retenu :

1. **Analyser le codebase EVA** — comprendre la structure existante (tools/, registry, config)
2. **Extraire les parties utiles** — pas le projet complet, seulement les fonctions/classes pertinentes
3. **Adapter au pattern EVA** — registry.register(), schemas JSON, handlers, check_fn optionnelle
4. **Tester** — `python3 -c "from tools.module import *"`, vérifier l'enregistrement dans `get_all_tool_names()`
5. **Documenter** — fichier dans output/docs/ avec l'arborescence créée

**Exemple de structure d'intégration :**
```
tools/core/       → fonctionnalités transverses (compression, automation)
tools/agent/      → mémoire, évolution
tools/integrations/ → scraping, graphes, connectivité
skills/imported/  → skills portés depuis l'écosystème
```

**Règle** : ajouter uniquement, jamais modifier les fichiers existants. 0 dépendances obligatoires (try/except ImportError).

---

## Pièges courants

1. **Erreur d'encodage UTF-8** : `browser_navigate` sur l'API GitHub peut échouer avec `'utf-8' codec can't decode byte`. Utiliser `terminal()` avec `curl` directement — l'API REST n'a pas ce problème.

2. **Recherche vide sur niches (PLC, SCADA, industriel)** : Les topics GitHub sont souvent absents sur les projets industriels. Chercher avec `topic:plc`, `topic:opcua`, `topic:mqtt`, `topic:scada`, `topic:iot`. Certains projets utilisent `topic:automation` au lieu de tags spécifiques.

3. **Seuils trop hauts** : Ajuster le seuil de stars par catégorie. Un projet PLC avec 500★ peut être le leader de sa niche.

4. **Catégories manquantes** : Ne pas se limiter aux topics évidents de l'agent. Chercher aussi orthogonalement : monitoring, timeseries, embedding, knowledge-graph, documentation, evaluation, vision, image-generation, voice, security.

5. **Oubli du filtre licence** : Toujours vérifier `license.spdx_id` avant de recommander un projet. Un projet AGPL semble gratuit mais contamine tout le codebase propriétaire.

6. **Top 10 contaminé** : Vérifier que TOUS les projets du Top 10 ont une licence permissive avant livraison.

7. **Intégration partielle mal testée** : Après avoir extrait des parties d'un projet, tester l'import + registry avant de déclarer terminé.

## Exemple concret

Voir `output/docs/projets_open_source_pour_EVA.md` pour le résultat complet de l'application de cette méthode (15 catégories, ~80 projets, Top 10 priorisé, toutes licences permissives).

Voir `output/docs/integration_10_projets.md` pour l'intégration réelle de 10 projets dans EVA (19 nouveaux outils, 14 fichiers).