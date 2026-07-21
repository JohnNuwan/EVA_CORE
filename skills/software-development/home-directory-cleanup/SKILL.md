---
name: home-directory-cleanup
description: "Ranger un répertoire home (~) encombré de façon professionnelle et sûre : inventaire lecture seule d'abord, validation fichier par fichier AVANT toute action, archivage récupérable au lieu de suppression, regroupement par projet, sécurisation des clés sensibles. Distinct du nettoyage d'un projet codebase (pas de git)."
category: software-development
domain: devops
---

# Nettoyage de Répertoire Home

## Présentation
Méthode pour ranger un répertoire `~` encombré (mélange de projets légitimes,
scripts épars, artefacts, fichiers parasites, clés sensibles) SANS rien casser.
Distinct de `project-restructuring` (qui cible un projet codebase avec git) :
ici pas de git, et le risque est de casser des projets actifs ou des dotfiles.

## Déclencheurs
- "range mon dossier", "c'est le bordel", "trop de fichiers partout", "organise mon home".
- L'utilisateur veut un poste "propre, organisé, professionnel".

## Règle d'or n°1 — INVENTAIRE D'ABORD, ACTION ENSUITE
Ne JAMAIS déplacer/supprimer en aveugle un home. Séquence obligatoire :
1. Lister l'état réel : `ls -la --group-directories-first ~` (dossiers puis fichiers).
2. Produire un inventaire FICHIER PAR FICHIER avec la destination prévue de chacun.
3. ATTENDRE le feu vert explicite de l'utilisateur avant toute modification.
Le user qui demande le détail avant action a raison — c'est la démarche pro.

## Catégorisation
- **Projets légitimes** (ftmo_agent, ai-stack, venvs, ComfyUI...) → INTOUCHÉS.
- **Scripts épars** à la racine → regrouper dans `~/scripts/` ou leur dossier projet.
- **Artefacts** (logs, caches, `__pycache__` racine) → archiver/supprimer.
- **Fichiers parasites** → voir pitfall ci-dessous.
- **Fichiers sensibles** (clés, tokens) → sécuriser en priorité.

## Règle d'or n°2 — ARCHIVER, NE PAS SUPPRIMER
Tout ce qui part de la racine va dans `~/archives/AAAA-MM/` (récupérable).
Ne supprimer définitivement QUE les parasites confirmés explicitement.

## Structure cible sobre
Limiter les dossiers racine : projets (inchangés), `~/scripts/` (utilitaires),
`~/archives/AAAA-MM/` (ce qui sort), dossiers dédiés existants (ex: `~/wireguard/`,
`~/mt5_setup/`) qui absorbent leurs fichiers épars.

## Pitfalls (validés)
- **Fichiers "parasites"** : des redirections shell ratées créent des fichiers dont
  le NOM est du code (ex: `20, self.bars_since_last_trade`, `# 3. Inactivity...`,
  `compose.yml` de 0 octet, `toto.txt`, `nvim-...appimagechmod`). Candidats sûrs à
  la suppression, MAIS toujours après confirmation explicite.
- **Clés sensibles à la racine** : regrouper `*_private.key`, SSH, tokens dans leur
  dossier dédié + `chmod 600`. Vérifier si vides (0 octet = à régénérer, inutiles).
- **Doublons avant regroupement** : scripts quasi identiques (ex: `train_flux_lora.py`
  vs `train_lora_flux.py`) — `diff` avant de n'en garder qu'un.
- **Gros fichiers non extraits** : une archive volumineuse dont le dossier extrait est
  minuscule (ex: 447 Mo vs 20 Ko) = probablement PAS extraite → la CONSERVER.
- **Ne pas toucher les dotfiles système** (.bashrc, .gitconfig, .config, venvs) sauf
  demande explicite. Modifier `.bashrc` (PATH...) = toujours avec accord.
- **Fichiers appartenant à un projet** (ex: `arena_*.log/.pid`) : demander à quel
  projet ils appartiennent avant de les y ranger — ne pas deviner.
