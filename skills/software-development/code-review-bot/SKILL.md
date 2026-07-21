---
name: code-review-bot
description: "Analyse et révision automatique de code : détection d'erreurs, sécurité, style, recommandations."
version: 1.0.0
author: E.V.A — The Hive
license: MIT
platforms: [linux, macos]
metadata:
  eva:
    tags: [github, code-review, quality, linting, security]
    related_skills: [github-pr-automation, github-code-review, merge-conflict-resolver]
---

# Code Review Bot

Pipeline de revue de code automatique utilisant les outils du système (git diff, grep, regex) + analyse contextuelle par l'agent.

## Pipeline de revue complet

### Étape 1 : Analyse statique automatisée

```bash
# Obtenir le diff complet
git diff main...HEAD --stat

# 1a. Détection des problèmes de sécurité
echo "=== 🔒 Problèmes de sécurité ==="
git diff main...HEAD | grep -in "print(\\|console\\.log\\|TODO\\|FIXME\\|HACK\\|XXX\\|debugger\\|password\\|secret\\|api_key\\|token.*=\\|private_key\\|-----BEGIN" || echo "  Aucun problème critique détecté"

# 1b. Marqueurs de conflit
echo "=== ⚠️  Marqueurs de conflit ==="
git diff main...HEAD | grep -n "<<<<<<\\|>>>>>>\\|=======" || echo "  Aucun conflit détecté"

# 1c. Fichiers volumineux suspects
echo "=== 📦 Fichiers les plus modifiés ==="
git diff main...HEAD --stat | sort -t'|' -k2 -rn | head -10
```

### Étape 2 : Vérification exécutable

```bash
# Linter Python (si ruff ou flake8)
if command -v ruff &>/dev/null; then
    ruff check $(git diff main...HEAD --name-only -- '*.py') 2>/dev/null
elif command -v flake8 &>/dev/null; then
    flake8 $(git diff main...HEAD --name-only -- '*.py') 2>/dev/null
fi

# Tests unitaires
if [ -f pytest.ini ] || [ -f pyproject.toml ] || [ -f setup.cfg ]; then
    python3 -m pytest --tb=short -x --no-header -q 2>&1 | tail -20
fi
```

### Étape 3 : Analyse contextuelle (agent)

Pour chaque fichier modifié, utiliser `read_file` pour obtenir le contexte complet (pas juste le diff) et chercher :

1. **Correction** : les changements résolvent-ils réellement le problème ?
2. **Chemins d'erreur** : que se passe-t-il si l'entrée est vide/nulle/inattendue ?
3. **Imports** : tous les nouveaux imports sont-ils nécessaires et présents ?
4. **Tests** : les nouveaux chemins de code sont-ils testés ?

## Grille de notation

| Niveau | Critères | Action |
|--------|----------|--------|
| 🔴 Critical | Injection, secret, data loss | Bloquer — PR doit être modifiée |
| 🟡 Warning | Style, perf, edge case | Suggérer une correction |
| 💡 Suggestion | Amélioration possible | Commenter sans bloquer |
| ✅ Looks Good | Tout correct | Approuver |

## Format de sortie standard

```
## Revue de Code — [branch-name]

### 🔴 Critique
- **fichier.py:42** — Injection possible : [description]
  Suggestion : [solution]

### 🟡 Avertissements
- **fichier2.py:15** — [description]
  Suggestion : [solution]

### 💡 Suggestions
- **fichier3.py:88** — [description]

### ✅ Approuvé
- Architecture propre, tests présents, bon nommage
```

## Intégration avec le pipeline PR

Utiliser en post-commit, pré-PR :

```bash
./auto-pr.sh commit -m "feat: mon changement"

# Lancer la review automatique avant de push
bash ~/.hermes/skills/software-development/code-review-bot/review.sh

# Si tout est vert → push + PR
./auto-pr.sh push
./auto-pr.sh pr --title "feat: mon changement" --body "Closes #X"
```

## Script de revue : review.sh

Un companion script `review.sh` dans ce même dossier (optionnel) exécute l'analyse automatisée.
