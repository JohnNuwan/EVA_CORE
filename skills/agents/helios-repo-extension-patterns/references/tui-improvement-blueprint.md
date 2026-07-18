# Blueprint Amelioration TUI EVA

> Analyse des gaps vs Claude Code et plan d'implementation — session 2026-07-03.

## Architecture actuelle

```
Node.js (Ink/React/TypeScript) ←→ Python (tui_gateway) ←→ AIAgent
     Rendu ecran                      JSON-RPC stdio/WS        Boucle agent
```

La TUI existe deja dans `tui_gateway/` (serveur Python) avec un frontend Ink (TypeScript). La CLI standalone utilise Rich + prompt_toolkit.

## Gap 1 — Visualisation du contexte (`/context`)

**Manque :** Claude Code a une grille coloree montrant l'utilisation du contexte par categorie. EVA a `/usage` mais c'est textuel.

**Solution :**
- Ajouter un handler `context.visualize` dans `tui_gateway/server.py` qui renvoie les donnees structurees
- Exposer le calcul de token usage par categorie depuis `agent/prompt_builder.py`
- Cote Ink : composant `<ContextGauge>` avec barre coloree
  - Vert : < 50%
  - Jaune : 50-70%
  - Orange : 70-85%
  - Rouge : > 85% (suggestion automatique de `/compress`)

**Fichiers a modifier :**
- `tui_gateway/server.py` : handler `context.visualize`
- `agent/prompt_builder.py` : methode `get_context_usage_breakdown()`
- Fichiers Ink : composant `<ContextGauge>`

**Effort :** 1 semaine

## Gap 2 — Raccourcis clavier avances

**Manque :** `!` shell direct, `#` memoire rapide, `Shift+Tab` cycle modes, `Ctrl+O` thinking toggle.

### 2a. `!` — Shell direct
Intercepter les messages commencant par `!` dans `cli.py`, executer via `terminal()` sans appel LLM.
```
> !git status
[output direct de git status]
```
**Fichier :** `cli.py` — hook dans la boucle de lecture prompt_toolkit

### 2b. `#` — Quick memory
Intercepter `# message` → ecriture dans AGENTS.md local ou `.EVA/rules/`.
```
> # Toujours utiliser 4 espaces pour l'indentation Python
[ajoute au AGENTS.md du projet]
```
**Fichier :** `cli.py` — hook prompt_toolkit

### 2c. `Shift+Tab` — Cycle modes permission
Cycler entre Default → Accept Edits → Don't Ask → Default.
Les modes sont deja implementes dans `acp_adapter/permissions.py`.
Ajouter le cycling dans `cli.py` avec feedback visuel (couleur barre statut).

### 2d. `Ctrl+O` — Thinking toggle
Deja supporte via `/reasoning show|hide`. Ajouter le raccourci clavier.
**Fichier :** `cli.py` — keybinding prompt_toolkit

**Effort :** 2 semaines

## Gap 3 — Mode Plan (lecture seule)

**Manque :** L'agent ne peut que lire/analyser sans modifier.

**Solution :**
- Creer un toolset `plan` dans `toolsets.py` avec uniquement les outils de lecture :
  - `read_file`, `search_files`, `browser_navigate`, `browser_snapshot`, `web_search`
  - PAS de `write_file`, `patch`, `terminal` (sauf commandes non destructrices)
- Commande `/plan [description]` dans `cli.py` qui active ce toolset
- Barre de statut indiquant "[PLAN MODE]"

**Fichiers a modifier :**
- `toolsets.py` : nouveau toolset `plan`
- `cli.py` : handler `/plan`
- `EVA_cli/commands.py` : CommandDef pour `/plan`

**Effort :** 3 jours

## Gap 4 — Hooks sur outils

**Manque :** Pas de hook PreToolUse/PostToolUse comme Claude Code.

**Architecture proposee :**
```python
# agent/tool_hooks.py (nouveau)
class ToolHookManager:
    def __init__(self, config: dict):
        self._hooks: dict[str, list[tuple[Pattern, str]]] = {}

    def register(self, event: str, matcher: str, command: str) -> None:
        """event: pre_tool | post_tool | session_start | agent_stop"""

    def fire(self, event: str, tool_name: str, tool_args: dict) -> list[str]:
        """Execute les hooks correspondants, retourne les sorties stdout."""

    def _match(self, pattern: str, tool_name: str, tool_args: dict) -> bool:
        """Pattern matching: Write(*.py), Bash(git *), Bash(rm *)"""
```

**Configuration dans config.yaml :**
```yaml
hooks:
  post_tool:
    - matcher: "write_file(*.py)"
      command: "ruff check --fix $EVA_FILE_PATH"
    - matcher: "write_file(*.py)"
      command: "ruff format $EVA_FILE_PATH"
  pre_tool:
    - matcher: "terminal(*rm -rf*)"
      command: "echo 'BLOCKED: destructive rm command' && exit 2"
  session_start:
    - matcher: "*"
      command: "git status --short"
```

**Variables d'environnement exposees aux hooks :**
- `EVA_TOOL_NAME` — nom de l'outil
- `EVA_FILE_PATH` — chemin du fichier (pour write_file/patch)
- `EVA_TOOL_ARGS` — arguments JSON
- `EVA_PROJECT_DIR` — repertoire du projet
- `EVA_SESSION_ID` — ID de session

**Fichiers a creer/modifier :**
- `agent/tool_hooks.py` : moteur de hooks (nouveau)
- `model_tools.py` : `fire('pre_tool', ...)` avant execution, `fire('post_tool', ...)` apres
- `EVA_cli/config.py` : ajouter `hooks` dans `DEFAULT_CONFIG`

**Effort :** 2 semaines

## Gap 5 — Barre de statut enrichie

**Manque :** Informations de session peu visibles.

**Solution CLI (Rich) :**
Footer permanent avec :
```
[deepseek-v4-pro] [openrouter] | [Default] | [12.4K/200K tokens] | [00:23:45]
```
Mise a jour apres chaque tour, couleur du mode (vert=default, jaune=accept-edits, rouge=dont-ask).

**Solution TUI (Ink) :**
Composant `<StatusBar>` avec les memes informations + indicateur de mode colore.

**Fichiers a modifier :**
- `cli.py` : footer Rich
- Fichiers Ink TUI : composant `<StatusBar>`

**Effort :** 1 semaine

## Roadmap

| Priorite | Fonctionnalite | Effort | Impact |
|----------|---------------|--------|--------|
| P0 | `/context` visuel | 1 sem | Tres eleve |
| P0 | Mode Plan | 3 jours | Eleve |
| P1 | Hooks systeme | 2 sem | Tres eleve |
| P1 | Raccourcis (`!`, `#`, `Shift+Tab`) | 2 sem | Eleve |
| P2 | Barre de statut enrichie | 1 sem | Moyen |
| P2 | `Ctrl+O` thinking toggle | 2 jours | Moyen |
| **Total** | | **~7 semaines** | |

## Points d'attention

1. **Preservation du cache de prompt** — tout changement de toolset ou de system prompt en cours de session invalide le cache. Les changements de mode doivent se faire via `/reset` ou au demarrage de session.

2. **Hooks et securite** — les hooks `pre_tool` avec `exit 2` bloquent l'execution. Ne pas permettre de hooks qui modifient le flux de l'agent (pas de modification des messages).

3. **Mode Plan et delegation** — en mode Plan, les sous-agents heritent-ils du mode Plan ? Proposition : oui, le toolset est herite.

4. **Raccourcis `!` et securite** — `!rm -rf /` doit toujours declencher l'approbation (respecter `approvals.mode`).