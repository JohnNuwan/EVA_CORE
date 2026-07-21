---
name: github-pr-automation
description: "Automatisation complète du cycle de vie PR : fork, branche, commit, push, PR via ~/pr-bot/auto-pr.sh"
version: 1.0.0
author: E.V.A — The Hive
license: MIT
platforms: [linux, macos]
metadata:
  eva:
    tags: [github, pr, automation, pipeline, git]
    related_skills: [github-auth, github-pr-workflow, code-review-bot, merge-conflict-resolver]
---

# GitHub PR Automation

Pipeline automatisé pour créer des Pull Requests GitHub sans intervention manuelle. Utilise `git` + `curl` (pas besoin de `gh` CLI).

## Prérequis

- Git configuré avec `credential.helper = store`
- Token GitHub dans `~/.git-credentials` (scopes : `repo`, `workflow`)
- Script installé : `~/pr-bot/auto-pr.sh`

```bash
# Vérification rapide
if command -v ~/pr-bot/auto-pr.sh &>/dev/null; then
    echo "✓ auto-pr.sh disponible"
else
    echo "auto-pr.sh non trouvé — lancer ~/pr-bot/setup-github-env.sh d'abord"
fi
```

## Installation

```bash
# Le script et le setup sont déjà en place si vous êtes dans The Hive
chmod +x ~/pr-bot/auto-pr.sh
~/pr-bot/setup-github-env.sh   # vérifie/configure git + token
```

Le script `setup-github-env.sh` ajoute aussi l'export automatique de `GITHUB_TOKEN` dans `~/.bashrc`.

## Commandes

### Pipeline complet (init → fork → branch → commit → push → PR)

```bash
cd ~/pr-bot
./auto-pr.sh full upstream/owner/repo \
  --title "feat: ajout système d'authentification JWT" \
  --body "## Résumé\nAjoute login/register avec JWT.\n\n## Détails\n- Middleware auth\n- Tests unitaires\n- Closes #42" \
  --branch "feat/jwt-auth" \
  --base main
```

### Étapes individuelles

```bash
# 1. Fork + clone du repo upstream
./auto-pr.sh init upstream/owner/repo

# 2. Créer une branche de feature
./auto-pr.sh branch feat/mon-changement

# 3. Commiter (après avoir fait les modifications avec write_file/patch)
git add -A
./auto-pr.sh commit -m "feat: description du changement"

# 4. Push
./auto-pr.sh push

# 5. Créer la PR
./auto-pr.sh pr --title "feat: mon changement" \
  --body "Description complète" \
  --base main
```

### Draft PR

```bash
./auto-pr.sh pr --title "WIP: ajout feature X" \
  --body "En cours de développement" --draft
```

### Statut

```bash
./auto-pr.sh status
```

## Structure du script

```
~/pr-bot/
├── auto-pr.sh              # Pipeline PR (point d'entrée)
└── setup-github-env.sh     # Configuration environnement
```

## Notes importantes

- **Token GitHub** : le script lit `GITHUB_TOKEN` de l'environnement ou l'extrait de `~/.git-credentials`
- **Sécurité** : le token n'est jamais loggé — seule la courte empreinte `XXXX...` apparaît dans status
- **API REST** : le script utilise `curl` vers l'API GitHub — pas besoin de `gh`
- **Fork** : la commande `init` crée le fork si nécessaire et configure `upstream` et `origin`
- **Le repo de test** : `~/test-pr-repo/` est un dépôt local de test pour valider le pipeline sans réseau
