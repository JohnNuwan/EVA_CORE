---
name: merge-conflict-resolver
description: "Détection, analyse et résolution automatisée des conflits de fusion Git."
version: 1.0.0
author: E.V.A — The Hive
license: MIT
platforms: [linux, macos]
metadata:
  eva:
    tags: [github, git, merge, conflict, resolution]
    related_skills: [github-pr-automation, code-review-bot, github-pr-workflow]
---

# Merge Conflict Resolver

Détecte, analyse et résout automatiquement les conflits de fusion Git. Conçu pour s'intégrer avec le pipeline `auto-pr.sh`.

## Détection des conflits

```bash
# Vérifier si la branche actuelle a des conflits avec main
git merge-tree $(git merge-base HEAD main) HEAD main | grep -A 3 "^@@.*@@.*CONFLICT" || echo "Aucun conflit détecté"

# Test de merge à blanc (sans commit)
git merge --no-commit --no-ff main 2>&1 || true
git merge --abort 2>/dev/null || true
```

## Analyse des conflits

Quand un conflit est détecté, suivre cette procédure :

### 1. Lister les fichiers en conflit

```bash
git diff --name-only --diff-filter=U
# ou
git status --short | grep "^UU"
```

### 2. Analyser chaque conflit

```bash
# Voir les marqueurs de conflit
grep -n "^<<<<<<<\\|^=======\\|^>>>>>>>" chemin/vers/fichier.conflictuel

# Comprendre le conflit
# Les marqueurs :
#   <<<<<<< HEAD        →  notre version (la branche courante)
#   =======             →  séparation
#   >>>>>>> main        →  leur version (la branche cible)
```

### 3. Stratégies de résolution

#### Résolution manuelle assistée

```bash
# Lire le fichier en conflit
read_file "chemin/fichier.conflictuel"

# Utiliser les outils standards :
# - patch(old_string, new_string) pour remplacer les blocs entiers
# - write_file pour réécrire le fichier si nécessaire
```

#### Stratégies automatiques

| Situation | Stratégie | Commande |
|-----------|-----------|----------|
| Notre code + leur code = OK | Prendre les deux | `git checkout --ours -- path` NE FONCTIONNE PAS — voir ci-dessous |
| Notre changement écrase le leur | Prendre le nôtre | `git checkout --ours chemin/fichier` |
| Leur changement écrase le nôtre | Prendre le leur | `git checkout --theirs chemin/fichier` |
| Changements complémentaires | Fusion manuelle | Voir Résolution contextuelle |

#### Prendre uniquement notre version

```bash
git checkout --ours chemin/vers/fichier
git add chemin/vers/fichier
```

#### Prendre uniquement leur version

```bash
git checkout --theirs chemin/vers/fichier
git add chemin/vers/fichier
```

#### Résolution contextuelle (recommandée)

```bash
# 1. Ouvrir le fichier en conflit
read_file "chemin/vers/fichier"

# 2. Identifier les blocs conflictuels
#    <<<<<<< HEAD
#    notre code
#    =======
#    leur code
#    >>>>>>> main

# 3. Utiliser patch() pour remplacer
#    le bloc entier par la version fusionnée correcte
```

### 4. Valider après résolution

```bash
# Marquer comme résolu
git add chemin/vers/fichier

# Vérifier qu'il ne reste plus de conflits
git diff --name-only --diff-filter=U | wc -l
# Devrait être 0

# Tester que le code compile toujours
git diff --cached --name-only -- '*.py' | xargs python3 -m py_compile 2>/dev/null || echo "⚠️ Erreur syntaxe Python"

# Committer le merge
git commit -m "merge: résolution conflit avec main"
```

## Pipeline de résolution automatique

Script intégré au cas où la résolution humaine n'est pas possible :

```bash
# Dans ~/pr-bot/resolve-conflicts.sh
# 1. Détection
CONFLICT_FILES=$(git diff --name-only --diff-filter=U)
echo "Fichiers en conflit: $CONFLICT_FILES"

# 2. Résolution contextuelle par l'agent
for file in $CONFLICT_FILES; do
    read_file "$file"
    # → analyse des blocs, décision de résolution
    # → patch() ou write_file() pour appliquer
    git add "$file"
done

# 3. Finalisation
git commit -m "merge: résolution automatique des conflits dans $(echo $CONFLICT_FILES | wc -w) fichier(s)"
```

## Anti-patterns

- **NE PAS** utiliser `git merge -X theirs` (trop agressif — ignore notre logique)
- **NE PAS** utiliser `git merge --abort` après avoir commencé la résolution
- **NE PAS** utiliser `git reset --hard` avant d'avoir sauvegardé les changements
- **TOUJOURS** faire `git diff --check` après résolution (trailing whitespace)
- **TOUJOURS** re-tester (`pytest`, `npm test`, etc.) après résolution
