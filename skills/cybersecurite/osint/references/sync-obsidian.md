# Workflow de Synchronisation Skills ↔ Obsidian

Ce fichier documente le mécanisme de synchronisation entre les skills
Hermes (`.hermes/skills/`) et le vault Obsidian (`~/lab/knowledge/`).

## Architecture

```
.hermes/skills/<categorie>/<nom>/SKILL.md   (agent - procédural)
         │
         │  sync-skills-obsidian.py
         │
         ▼
lab/knowledge/obsidian-cybersecurite/       (humain - navigation)
  └── <dossier>/<note>.md
```

## Script de synchronisation

```bash
python3 ~/lab/scripts/sync-skills-obsidian.py [--dry-run] [-s <skill>]
```

Le script :
1. Nettoie le frontmatter YAML (inutile dans Obsidian)
2. Ajoute des `[[wikilinks]]` vers l'Accueil et l'Arsenal
3. Écrit dans le dossier vault correspondant
4. Cherche les skills dans `cybersecurite/`, `business/`, `mlops/`

## Activation de l'environnement

```bash
source ~/lab/tools/venvs/osint/bin/activate
export PATH=$HOME/lab/tools/bin:$HOME/lab/tools/go/bin:$HOME/lab/tools/go-workspace/bin:$PATH
```

## Règle

Toute modification d'un skill DOIT être suivie de la synchronisation Obsidian.
