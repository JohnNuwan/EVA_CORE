# Intégration de Projets Open-Source dans EVA Agent

> Session : Juillet 2026 — Intégration de 10 projets open-source (19 outils, 14 fichiers, 5 skills).
> Méthode : Analyse → extraction partielle → adaptation au pattern EVA → test → documentation.

## Principe

**Ne pas importer les projets en bloc.** Pour chaque projet open-source retenu :

1. Analyser le codebase EVA existant pour comprendre l'architecture
2. Extraire UNIQUEMENT les parties utiles (pas le projet complet)
3. Adapter au pattern EVA : `registry.register()`, schémas JSON, handlers
4. Optionnel : ajouter une `check_fn` pour les dépendances optionnelles
5. Tester import + registry avant de déclarer terminé

## Structure d'accueil

| Dossier | Type de fonctionnalité | Exemples |
|---------|----------------------|----------|
| `tools/core/` | Transverses, compression, automation | `compression_layer.py`, `event_automation.py` |
| `tools/agent/` | Mémoire, évolution, sous-agents | `memory_enhancement.py` |
| `tools/integrations/` | Connecteurs externes, scraping, graphes | `ai_scraper.py`, `code_intelligence_graph.py` |
| `tools/integrations/industrial/` | Industriel, PLC, SCADA | `plc_connectivity.py` |
| `skills/imported/` | Skills portés depuis l'écosystème | `code-reviewer/`, `plc-diagnostics/` |

## Pattern d'enregistrement

Chaque module doit suivre le pattern standard :

```python
from tools.registry import registry

def _check_requirements() -> bool:
    try:
        import httpx
        return True
    except ImportError:
        return False

registry.register(
    name="mon_outil",
    toolset="core",  # ou "industrial", "web", etc.
    schema={...},    # Schema JSON OpenAI-compatible
    handler=lambda a, **kw: mon_handler(a.get("param"), ...),
    check_fn=_check_requirements,  # optionnel
    requires_env=[],
    description="Description courte",
    emoji="🔧",
)
```

## Règles

1. **0 dépendances obligatoires** — tout en try/except ImportError
2. **Ajout uniquement** — jamais de modification des fichiers existants
3. **Découverte automatique** — `discover_builtin_tools()` scanne les modules .py avec `registry.register()`
4. **Tester** — `python3 -c "from module import *"` + vérifier `get_all_tool_names()`
5. **Documenter** — fichier output/docs/ avec arborescence + comptage d'outils

## Exemple

Voir `output/docs/integration_10_projets.md` — 19 outils, 14 fichiers, 5 skills créés sans modifier une ligne existante.