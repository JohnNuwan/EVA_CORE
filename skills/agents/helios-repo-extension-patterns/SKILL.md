---
name: helios-repo-extension-patterns
description: "Guide pour étendre le dépôt Helios via des MCP et plugins."
version: 1.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [helios, repo, mcp, plugins, skills, extension, contribution]
    related_skills: [helios-agent, helios-agent-mcp-development, helios-agent-skill-authoring]
---

# Helios Repo Extension Patterns

## Vue d'ensemble

Cette compétence capture les patterns concrets pour étendre le dépôt Helios sans gonfler le noyau : ajouter d'abord des serveurs MCP et des plugins, puis compléter par des skills ciblées. Elle est utile lorsqu'un besoin révèle un trou de couverture outillée et qu'il faut enrichir la collection proprement, de manière reproductible.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- combler des manques de capabilities dans Helios ;
- ajouter plusieurs intégrations métier en lot ;
- créer des serveurs MCP repo-local ;
- ajouter un plugin Helios avec tools ou hooks ;
- compléter ensuite la bibliothèque de skills pour la partie méthodologie.

Ne pas utiliser pour :
- un simple patch d'une ligne dans un fichier existant ;
- une correction de bug localisée sans ajout de capability ;
- une contribution qui doit aller dans un skill utilisateur local au lieu du dépôt.

## Ordre de travail recommandé

Quand il faut corriger des "points faibles" de la collection, appliquer l'ordre suivant :
1. MCPs et plugins d'abord ;
2. skills ensuite ;
3. ne proposer un nouvel outil noyau qu'en dernier recours.

Ce séquencement colle à la footprint ladder du projet et à la préférence exprimée pendant les travaux d'enrichissement : traiter d'abord l'outillage exécutable, puis la couche méthodologique.

## Pattern MCP dans ce dépôt

### Structure attendue
- manifeste catalogue : `optional-mcps/<name>/manifest.yaml`
- implémentation : `projects/mcp-<name>/server.py`

### Contenu minimal du manifeste
- `manifest_version: 1`
- `name`, `description`, `source: local`
- transport stdio avec `command: "python"`
- chemin script sous `projects/.../server.py`
- bloc `post_install` court avec la dépendance principale (`pip install mcp` au minimum)

### Règles de conception serveur
- utiliser `FastMCP`
- exposer 2 à 4 tools ciblés, pas une surface énorme et floue
- gérer les formats partiellement supportés en mode dégradé plutôt qu'échec brutal
- renvoyer du JSON lisible et stable

## Pattern plugin dans ce dépôt

### Structure attendue
- `plugins/<name>/__init__.py`
- `plugins/<name>/plugin.yaml`
- `plugins/<name>/README.md` si le plugin n'est pas trivial

### Enregistrement
- point d'entrée : `def register(ctx) -> None:`
- tools : `ctx.register_tool(...)`
- hooks : `ctx.register_hook(...)`
- éviter les effets de bord au chargement ; garder l'initialisation légère

### Cas d'usage typiques
- audit de catalogue
- garde-fous transformant le résultat d'un outil
- intégration d'un service ou d'une capability transverse

## Skills du dépôt après l'outillage

Une fois les MCPs/plugins ajoutés, compléter avec des skills de classe :
- une skill par domaine réutilisable, pas une skill par incident du jour ;
- ajouter `references/` ou `templates/` quand une matrice, un canevas ou une checklist aide vraiment ;
- relier les nouvelles skills aux umbrellas existantes via `related_skills`.

## Pattern IDE Extension (VS Code)

Helios expose déjà un adapteur ACP (`acp_adapter/`) implémentant le protocole Agent Communication Protocol — le même standard utilisé par Claude Code et Codex pour l'intégration IDE. L'éditeur Zed s'y connecte nativement. Pour ajouter le support VS Code :

### Architecture
- **Processus enfant :** `helios-acp` (Python) spawné par l'extension VS Code (TypeScript)
- **Transport :** JSON-RPC sur stdin/stdout (stdio)
- **Dépendance :** `agent-client-protocol==0.9.0` (extra `acp` de pyproject.toml)

### Structure de l'extension
```
extensions/vscode/
├── package.json           # Manifest VS Code (activationEvents, contributes, keybindings)
├── tsconfig.json
├── src/
│   ├── extension.ts       # Point d'entrée : activation, spawn helios-acp
│   ├── acpClient.ts       # Client ACP stdio (JSON-RPC)
│   ├── chatPanel.ts       # Webview React/Vue pour le chat
│   ├── inlineEdit.ts      # Gestion des éditions inline avec diff preview
│   └── contextProvider.ts # Contexte éditeur (fichier courant, sélection, diagnostics LSP)
└── .vscodeignore
```

### Fonctionnalités clés
- **Chat panel** avec streaming temps réel, rendu Markdown, affichage outils
- **Contexte éditeur** automatique : fichier courant + sélection → pièce jointe ACP
- **Inline edit** : diff preview avant application via `WorkspaceEdit`
- **Diagnostics** : résultats d'analyse Helios → panneau "Problems" VS Code
- **Modes de permission** : Default / Accept Edits / Don't Ask (déjà dans l'ACP)

### Plan détaillé
Voir `references/ide-extension-blueprint.md` pour le plan complet en 3 phases (8 semaines), les commandes clavier, la configuration workspace, et les pièges d'intégration.

## Pattern Amélioration TUI

La TUI Helios utilise une architecture Node.js (Ink/React) ↔ Python (tui_gateway) en JSON-RPC. Pour ajouter des fonctionnalités de type Claude Code :

### Gaps prioritaires
1. **Visualisation contexte (`/context`)** — grille colorée token usage par catégorie
2. **Raccourcis clavier** — `!` shell direct, `#` mémoire rapide, `Shift+Tab` cycle modes
3. **Mode Plan** — lecture seule (outils d'écriture désactivés)
4. **Hooks sur outils** — PreToolUse/PostToolUse avec commandes shell
5. **Barre de statut enrichie** — modèle, provider, mode, tokens, durée session

### Plan détaillé
Voir `references/tui-improvement-blueprint.md` pour l'analyse complète des gaps, l'architecture des hooks, les fichiers à modifier, et la roadmap 7 semaines.

## Vérification recommandée

1. Compiler les nouveaux modules Python avec `py_compile`.
2. Faire un smoke test de fonctions internes via import contrôlé ou `exec(compile(...))` quand le module a un `if __name__ == "__main__": mcp.run()`.
3. Pour les extracteurs/validateurs, fabriquer un mini jeu de données synthétique et vérifier un résultat concret.
4. Vérifier la présence réelle des nouveaux manifestes/plugins par inspection de l'arborescence.
5. Si le travail porte aussi sur les skills du dépôt, auditer ensuite la famille concernée pour identifier les skills les plus faibles avant de les enrichir.

## Boucle d'enrichissement des skills après l'outillage

Quand plusieurs skills d'une même famille restent trop courtes ou trop légères après l'ajout des MCPs/plugins, appliquer cette boucle :
1. lister les `SKILL.md` de la famille ;
2. classer les plus faibles par signaux simples : faible nombre de lignes, sections minimales absentes, absence de `references/` / `templates/` / `scripts/` ;
3. enrichir d'abord les skills coeur de plateforme (motion, safety, interface standard, supervision) ;
4. ajouter au moins un support file quand une matrice de validation ou une checklist réutilisable apporte une vraie valeur ;
5. rerun un mini audit pour vérifier que les skills renforcées ne figurent plus parmi les plus faibles.

Cette étape évite de s'arrêter après la seule création de nouvelles skills alors que les umbrellas existantes du même cluster restent sous-développées.

## Piège important sur les chemins

Dans ce dépôt, lors d'écritures de fichiers via les outils Helios, préférer des chemins explicitement ancrés au dépôt avec un préfixe `./` quand on crée des fichiers repo-relatifs. Cela évite les résolutions ambiguës qui peuvent créer des doublons de dossiers au mauvais endroit lors d'ajouts en lot.

## Pièges Courants (Common Pitfalls)

1. **Créer directement une skill alors qu'un MCP ou un plugin apporterait une vraie capability exécutable.**
   Commencer par l'outillage, puis documenter avec les skills.

2. **Disperser les fichiers MCP hors du pattern dépôt.**
   Garder `optional-mcps/<name>/manifest.yaml` et `projects/mcp-<name>/server.py`.

3. **Enregistrer un plugin sans point d'entrée `register(ctx)`.**
   Suivre le pattern des plugins existants (`ctx.register_tool`, `ctx.register_hook`).

4. **Écrire des chemins repo-relatifs sans ancrage explicite.**
   Préférer `./skills/...`, `./plugins/...`, `./optional-mcps/...` pour éviter les surprises de résolution.

5. **Déclarer le travail terminé sans exécution réelle.**
   Compiler et faire au moins un smoke test synthétique des nouvelles capacités.

## Liste de vérification (Checklist)

- [ ] Les besoins ont été traités d'abord par MCP/plugin avant d'ajouter des skills.
- [ ] Chaque MCP suit le pattern `optional-mcps/<name>` + `projects/mcp-<name>`.
- [ ] Chaque plugin suit le pattern `plugins/<name>` avec `register(ctx)`.
- [ ] Les nouvelles skills sont de niveau classe et non liées à une seule session.
- [ ] Les nouveaux fichiers Python compilent.
- [ ] Un smoke test synthétique a été exécuté.
- [ ] Les chemins d'écriture ont été ancrés explicitement au dépôt.
