---
name: codex
description: "Déléguer des tâches de code à OpenAI Codex CLI."
version: 2.0.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [coding-agent, codex, openai, code-review, refactoring, ai-assisted-development, batch-processing, Pull-Request]
    related_skills: [claude-code, EVA-agent, EVA-agent-mcp-development]
---

# Délégation de tâches de code avec OpenAI Codex CLI

## Vue d'ensemble

Cette compétence permet à EVA de déléguer des tâches de développement logiciel à **[Codex](https://github.com/openai/codex)**, l'agent autonome de codage en ligne de commande d'OpenAI. Au lieu qu'EVA exécute directement du code ou écrive lui-même des fichiers, il peut confier à Codex des sous-tâches complètes (développement de fonctionnalités, refactoring, revue de code, correction de bugs) et en récupérer le résultat.

### Principe de fonctionnement

```
EVA Agent ──terminal(pty=true)──> Codex CLI
    │                                       │
    │  Prompt : "Ajouter un mode sombre"     │
    │───────────────────────────────────────►│
    │                                       │
    │                              Codex exécute :
    │                              - Analyse du code existant
    │                              - Modification des fichiers
    │                              - Tests (optionnel)
    │                              - Commit Git
    │                                       │
    │◄───────────────────────────────────────│
    │  Résultat : modifications appliquées   │
```

---

## Quand l'utiliser

### Cas d'usage

- **Développement de fonctionnalités** : Ajout de nouvelles fonctionnalités dans un projet existant.
- **Refactoring** : Réorganisation de code, extraction de modules, amélioration de l'architecture.
- **Revue de code (PR Review)** : Analyse de Pull Requests et génération de commentaires.
- **Correction par lots** : Correction simultanée de plusieurs issues (bugs) via des worktrees Git.
- **Projets scratch** : Création de projets complets à partir de zéro (ex: « Crée un jeu Snake en Python »).

### Prérequis

| Prérequis | Détail |
|-----------|--------|
| Codex CLI installé | `npm install -g @openai/codex` |
| Authentification OpenAI | `OPENAI_API_KEY` ou OAuth Codex |
| Dépôt Git | Codex refuse de travailler hors d'un dépôt Git |
| PTY activé | Codex est une application interactive — nécessite `pty=true` |

### Authentification

Pour EVA, le fournisseur `model.provider: openai-codex` utilise l'OAuth géré par EVA depuis `~/.EVA/auth.json` après `EVA auth add openai-codex`. Pour la CLI Codex autonome, une session OAuth peut résider sous `~/.codex/auth.json`.

> **Important :** Ne pas traiter l'absence de `OPENAI_API_KEY` comme une preuve d'absence d'authentification Codex. Vérifier d'abord `~/.codex/auth.json`.

---

## 1. Tâches unitaires (One-Shot)

### 1.1 Exécution simple

```text
terminal(command="codex exec 'Ajouter un bouton de bascule du mode sombre dans les paramètres utilisateur'", 
         workdir="~/mon-projet", pty=true)
```

### 1.2 Projet scratch (sans dépôt existant)

```text
# Créer un dépôt temporaire, initialiser Git, puis lancer Codex
terminal(command="cd $(mktemp -d) && git init && codex exec 'Créer un jeu Snake en Python avec Pygame'", 
         pty=true)
```

### 1.3 Avec contexte spécifique

```text
terminal(command="codex exec 'Ajouter une validation JWT dans le middleware Express. 
         Le token est stocké dans req.headers.authorization sous le format Bearer <token>'", 
         workdir="~/mon-api", pty=true)
```

---

## 2. Mode arrière-plan (tâches longues)

Pour les tâches longues (plusieurs minutes), utiliser le mode **background** :

```text
# 1. Lancer Codex en arrière-plan
terminal(command="codex exec --full-auto 'Refactoriser le module d'authentification pour utiliser des classes de service'", 
         workdir="~/mon-projet", background=true, pty=true)
# Retourne un session_id

# 2. Surveiller la progression
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# 3. Envoyer une réponse si Codex pose une question
process(action="submit", session_id="<id>", data="oui, continue")

# 4. Arrêter si nécessaire
process(action="kill", session_id="<id>")
```

### Gestion des questions interactives

Codex peut parfois poser des questions pendant l'exécution. Utiliser `process(action="log")` pour détecter ces questions, puis `process(action="submit")` pour répondre.

---

## 3. Drapeaux (Flags) essentiels

| Drapeau | Effet | Risque |
|---------|-------|--------|
| `exec "<prompt>"` | Exécution unique, se termine automatiquement | Faible |
| `--full-auto` | Sandboxé + approbation automatique des changements dans le workspace | Moyen |
| `--yolo` | Pas de sandbox, pas d'approbation. Exécution la plus rapide | **Élevé** |
| `--sandbox danger-full-access` | Désactive le sandbox Codex (utile quand bubblewrap échoue) | Élevé |

> **Recommandation :** Privilégier `--full-auto` pour la plupart des tâches. Réserver `--yolo` pour les environnements de confiance ou les tâches de correction rapide.

---

## 4. Revue de Pull Requests (PR Reviews)

### 4.1 Revue dans un répertoire temporaire

```text
# Cloner le dépôt dans un répertoire temporaire
terminal(command="REVIEW=$(mktemp -d) && \
         git clone https://github.com/utilisateur/depot.git $REVIEW && \
         cd $REVIEW && gh pr checkout 42 && \
         codex exec 'Review this PR. Check for security issues, performance problems, and adherence to best practices'",
         pty=true)
```

### 4.2 Revue de PRs multiples en parallèle

```text
# Récupérer toutes les références de PR
terminal(command="git fetch origin '+refs/pull/*/head:refs/remotes/origin/pr/*'", workdir="~/mon-projet")

# Lancer des revues en parallèle
terminal(command="codex exec 'Review PR #86. git diff origin/main...origin/pr/86. Suggest improvements.'", 
         workdir="~/mon-projet", background=true, pty=true)
terminal(command="codex exec 'Review PR #87. git diff origin/main...origin/pr/87. Check for regressions.'", 
         workdir="~/mon-projet", background=true, pty=true)

# Publier les résultats
terminal(command="gh pr comment 86 --body '<revue>'", workdir="~/mon-projet")
terminal(command="gh pr comment 87 --body '<revue>'", workdir="~/mon-projet")
```

---

## 5. Correction parallèle d'issues avec Worktrees

La fonctionnalité `git worktree` permet de travailler sur plusieurs branches simultanément :

```text
# Créer des worktrees pour chaque issue
terminal(command="git worktree add -b fix/issue-78 /tmp/issue-78 main", workdir="~/mon-projet")
terminal(command="git worktree add -b fix/issue-99 /tmp/issue-99 main", workdir="~/mon-projet")

# Lancer Codex dans chaque worktree
terminal(command="codex exec --yolo 'Fix issue #78: Le formulaire de connexion ne valide pas les champs vides.'", 
         workdir="/tmp/issue-78", background=true, pty=true)
terminal(command="codex exec --yolo 'Fix issue #99: Le timer de session expire trop tôt.'", 
         workdir="/tmp/issue-99", background=true, pty=true)

# Surveiller les deux processus
process(action="list")

# Après complétion : push et création de PRs
terminal(command="cd /tmp/issue-78 && git push -u origin fix/issue-78")
terminal(command="gh pr create --repo user/repo --head fix/issue-78 --title 'fix: validation champs vides' --body 'Corrige le ticket #78'")

# Nettoyage
terminal(command="git worktree remove /tmp/issue-78", workdir="~/mon-projet")
terminal(command="git worktree remove /tmp/issue-99", workdir="~/mon-projet")
```

---

## 6. Contournement du sandbox (Gateway Caveat)

### 6.1 Problème connu

Quand Codex CLI est invoqué depuis un contexte **gateway EVA** (ex: session Telegram), le sandbox `workspace-write` peut échouer même si la même commande fonctionne dans le shell interactif de l'utilisateur.

**Symptômes typiques :**

```
setting up uid map: Permission denied
loopback: Failed RTM_NEWADDR: Operation not permitted
```

### 6.2 Solution

```text
codex exec --sandbox danger-full-access "<tâche>"
```

**Mesures de sécurité compensatoires :**

1. `workdir` explicite (ne pas utiliser le répertoire courant).
2. État Git propre avant le lancement (`git status` doit être clean).
3. Prompts de tâche étroits et précis.
4. Revue `git diff` après exécution.
5. Tests ciblés avant validation.
6. Confirmation humaine/agent avant de commit des changements importants.

---

## Règles essentielles

1. **Toujours utiliser `pty=true`** — Codex est une application interactive et se bloque sans PTY.
2. **Dépôt Git requis** — Codex refuse de s'exécuter en dehors d'un répertoire Git. Utiliser `mktemp -d && git init` pour les projets scratch.
3. **Utiliser `exec` pour les tâches unitaires** — `codex exec "<prompt>"` s'exécute et se termine proprement.
4. **`--full-auto` pour le développement** — Approuve automatiquement les changements dans le sandbox.
5. **Arrière-plan pour les tâches longues** — Utiliser `background=true` et surveiller avec `process(action="poll")`.
6. **Ne pas interférer** — Surveiller avec `poll`/`log`, être patient avec les tâches longues.
7. **Le parallélisme est possible** — Plusieurs processus Codex peuvent s'exécuter simultanément.
8. **Toujours nettoyer** — Supprimer les worktrees temporaires après utilisation.

---

## Pièges Courants (Common Pitfalls)

1. **Oubli de `pty=true` :**
   * *Erreur :* Codex se bloque immédiatement au démarrage sans produire de sortie.
   * *Correction :* Toujours ajouter `pty=true` à l'appel `terminal`.

2. **Absence de dépôt Git :**
   * *Erreur :* Codex refuse avec `"Not a git repository"`.
   * *Correction :* Initialiser Git : `git init` ou cloner un dépôt existant.

3. **Sandbox qui échoue en gateway :**
   * *Erreur :* Erreur bubblewrap (`Permission denied`) dans les sessions gateway.
   * *Correction :* Utiliser `--sandbox danger-full-access` avec les précautions de sécurité décrites ci-dessus.

4. **Tâche trop large :**
   * *Erreur :* Codex part dans une direction non prévue ou ne termine pas.
   * *Correction :* Découper la tâche en sous-tâches plus petites et plus précises. Ex: « Ajouter le modèle User » plutôt que « Créer toute l'app ».

5. **Modifications non commitées avant le lancement :**
   * *Erreur :* Codex modifie des fichiers qui étaient en cours de modification, provoquant des conflits.
   * *Correction :* S'assurer que `git status` est propre avant de lancer Codex.

---

## Liste de vérification (Checklist)

- [ ] Codex CLI est installé globalement : `npm install -g @openai/codex`.
- [ ] L'authentification OpenAI est configurée (clé API ou OAuth Codex).
- [ ] `pty=true` est spécifié dans l'appel `terminal`.
- [ ] Le répertoire de travail est un dépôt Git valide.
- [ ] `git status` est propre avant le lancement de Codex.
- [ ] Les worktrees temporaires sont nettoyés après utilisation.
- [ ] Pour les tâches en gateway, `--sandbox danger-full-access` est utilisé si nécessaire.
- [ ] Les résultats de Codex sont vérifiés (`git diff`) avant validation.
- [ ] Les prompts sont précis et découpés en sous-tâches si nécessaire.

