---
name: project-restructuring
description: >-
  Restructurer un projet existant : supprimer les fichiers obsolètes, renommer
  pour la cohérence, organiser les répertoires, créer README/.gitignore, et
  pousser sur GitHub proprement.
category: software-development
---

# Restructuration de Projet — Nettoyage & Organisation

## Présentation

Ce skill couvre la méthodologie pour nettoyer et réorganiser un projet
codebase existant — que ce soit après une phase de prototypage, une
accumulation de versions, ou une migration technique. L'objectif est de
passer d'un désordre de fichiers à une structure professionnelle, lisible
et maintenable.

**Déclencheurs typiques :**
- L'utilisateur dit "nettoie", "range", "fait le ménage", "supprime l'ancien"
- Le projet contient des versions multiples (V1, V2, V3) éparpillées
- Aucun README, .gitignore, ou structure de répertoires claire
- Des checkpoints volumineux (`.pt`, `.pth`, `.h5`) traînent dans la racine

## Processus

### Phase 1 — Audit de l'existant

Commence par lister tous les fichiers à la racine du projet :

```bash
ls -la .
```

Identifie les catégories :
- **Fichiers actifs** : ceux importés/utilisés par le code courant
- **Fichiers obsolètes** : versions antérieures, backups, scripts morts
- **Artefacts** : logs, checkpoints, caches, venv, `__pycache__`
- **Données** : CSV, parquet, HDF5 (souvent trop gros pour git)

Vérifie les dépendances entre fichiers :
```bash
grep -r "^from\|^import" *.py | sort
```

Cela montre quels fichiers sont réellement utilisés. Tout fichier non
importé est candidat à l'archivage ou la suppression.

### Phase 2 — Archivage des anciennes versions

NE SUPPRIME PAS directement — archive dans un dossier `legacy/` :

```bash
mkdir -p legacy/v1 legacy/v2 legacy/v3
mv agent.py legacy/v1/
mv train_v2.py agent_v2.py legacy/v2/
```

Règles :
- Garder l'historique dans `legacy/` (le user peut toujours y revenir)
- Structurer par version majeure (`v1/`, `v2/`, `v3/`) ou par approche obsolète (`dreamerv3_ppo_obsolete/`, `rl_v1/`)
- Les fichiers sans version dans le nom vont dans `legacy/` racine
- **Archiver (ne pas supprimer)** les logs (`.log`) et checkpoints (`.pt`) dans `legacy/` — le `.gitignore` les exclura automatiquement de git, mais on les garde localement

**Avant tout déplacement, vérifier `.gitignore`** pour anticiper ce que git suit :
```bash
cat .gitignore
```
Cela évite les surprises : si `checkpoints_*/` et `*.pt` sont ignorés, git ne verra pas les déplacements de ces fichiers (seul le déplacement physique compte).

### Phase 3 — Renommage cohérent

Supprimer les suffixes de version des fichiers actifs :

```bash
mv train_v4.py train.py
mv environment_v4.py environment.py
mv ftmo_diag_v4.py diag.py
```

Puis mettre à jour TOUS les imports dans les fichiers restants :

```bash
grep -r "ancien_nom" *.py
# Remplacer chaque import
```

Vérifier que tout compile :
```bash
python3 -c "from config import ...; from environment import ..."
```

### Phase 4 — Git & Documentation

Créer les fichiers de base :

**README.md** : architecture, utilisation, changements entre versions
**`.gitignore`** : ignorer `data/`, `checkpoints*/`, `*.log`, `venv/`, `__pycache__/`, `*.pt`

```gitignore
__pycache__/
*.pyc
checkpoints*/
*.log
data/
*.csv
venv/
.venv/
.env
.DS_Store
*.pt
*.pth
```

Configurer git et pusher :
```bash
git init
git remote add origin <url>
git add -A
git commit -m "Version X: description complète"
git push -u origin main
```

### Phase 5 — Vérification finale

1. Vérifier que tout compile (imports + syntaxe)
2. Vérifier que les tailles sont raisonnables (pas de fichiers > 100KB dans git)
3. Vérifier que le `.gitignore` couvre bien les gros fichiers
4. Lister la structure finale avec `find . -not -path '*/venv/*' -not -path '*/.git/*' -type f`

## Pitfalls

- **Ne pas supprimer sans vérifier les imports.** Un fichier peut être utilisé
  par un autre sans être importé directement (ex: `exec()`, `__import__()`,
  chemins dynamiques). Utilise `grep -r` plutôt que l'intuition.
- **Ne pas archiver les données (CSV).** Elles sont souvent trop volumineuses
  pour git. Les laisser dans `data/` et ajouter au `.gitignore`.
- **Les checkpoints `.pt` ne vont pas dans git.** Ils peuvent faire 70+ MB
  chacun. Les archiver localement ou sur un stockage externe.
- **Mettre à jour tous les imports après renommage.** Un oubli = un import
  cassé. Utilise `grep -r` sur tout le projet pour traquer les références.
- **Le token GitHub peut être un fine-grained PAT** sans droits d'écriture.
  Si `git push` retourne 403, vérifier que le token a la permission
  "Contents: Write" sur le repo, ou utiliser un classic PAT avec scope `repo`.
- **Éviter de commit les tokens.** Ne jamais mettre le token dans l'URL git
  de façon permanente. L'utiliser une fois pour le push, puis `git remote
  set-url origin https://github.com/user/repo.git` sans token.
- **Vérifier le `.gitignore` AVANT le commit.** Si des fichiers sensibles
  (`.env`, tokens, clés SSH) sont déjà suivis, les ajouter à `.gitignore`
  ne les désindexe pas. Utiliser `git rm --cached` d'abord.

## Références

Voir `references/ftmo-rl-analysis.md` pour un exemple concret d'analyse
d'environnement RL trading qui a motivé une restructuration complète de
projet — identification des problèmes de reward shaping, spreads,
slippage, et mise en place d'un curriculum learning.

## Skills Liés

- `simplify-code` : nettoyage de code au niveau des fonctions (complémentaire)
- `requesting-code-review` : revue de code pré-commit