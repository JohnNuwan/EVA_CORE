# Blueprint Extension VS Code pour EVA

> Plan d'implémentation détaillé — session 2026-07-03, analyse concurrentielle Claude Code.

## Contexte

EVA possède déjà un adapteur ACP (`acp_adapter/`) qui implémente le protocole Agent Communication Protocol (JSON-RPC stdio), utilisé par Zed pour se connecter à EVA. L'enjeu est de créer le client VS Code manquant.

## Architecture

```
VS Code Extension (TypeScript)
  ├── Chat Panel (Webview React)
  ├── Inline Edit (WorkspaceEdit + diff preview)
  ├── Diagnostics Provider
  └── ACP Client (spawn EVA-acp)
         │ stdio JSON-RPC
Processus enfant: EVA-acp (Python, acp_adapter/entry.py)
```

## Phase 1 — Squelette (Semaines 1-3)

### 1. Initialisation du projet
- Créer `extensions/vscode/` avec package.json, tsconfig.json
- `activationEvents`: `onStartupFinished`, `onCommand:EVA.*`
- `contributes.commands`: `EVA.startChat`, `EVA.sendSelection`, `EVA.explainCode`, `EVA.reviewFile`
- `contributes.keybindings`: `Ctrl+Shift+H` → ouvre le chat
- `contributes.configuration`: `EVA.model`, `EVA.provider`, `EVA.autoApprove`
- `contributes.viewsContainers`: icône EVA dans la barre d'activité

### 2. Client ACP (acpClient.ts)
```typescript
// Spawn EVA-acp comme processus enfant
const childProcess = spawn('EVA-acp', [], {
  env: { ...process.env, EVA_HOME: homeDir }
});
// Communication JSON-RPC sur stdin/stdout
```

### 3. Panel de chat (chatPanel.ts)
- Webview avec rendu Markdown + coloration syntaxique
- Streaming des réponses (AgentMessageChunk)
- Affichage des outils utilisés (read_file, write_file, terminal...)
- Barre d'état : modèle, tokens, mode permission

### 4. Gestion des ressources ACP
- Attacher le fichier courant + sélection comme `ResourceContentBlock`
- Supporter les images inline (captures d'écran)
- Gérer les ressources `resource_link` et `embedded_resource`

## Phase 2 — Fonctionnalités Code (Semaines 4-6)

### 1. Contexte éditeur automatique
- Fichier courant → `@file` dans le chat
- Sélection → `@selection`
- Diagnostics LSP du fichier → contexte pour corrections
- Fichiers ouverts dans l'onglet → suggérés comme contexte

### 2. Éditions inline avec diff preview
- Quand EVA propose `write_file` ou `patch` → diff VS Code natif
- Boutons "Accept" / "Reject" / "Modify"
- Appliquer via `WorkspaceEdit` et `TextDocumentEdit`
- Utiliser `edit_approval.py` de l'ACP pour le workflow d'approbation

### 3. Diagnostics intégrés
- Résultats d'analyse EVA → `vscode.DiagnosticCollection`
- Affichage dans le panneau "Problems"
- Code actions : "Fix with EVA" sur les erreurs
- Severity mapping : erreur → Error, warning → Warning, info → Information

### 4. Raccourcis clavier
- `Ctrl+K H` → "EVA, explique ce code"
- `Ctrl+K Shift+H` → "EVA, review ce fichier"
- `Ctrl+K Alt+H` → "EVA, corrige cette erreur"
- `Ctrl+Shift+H` → ouvre/ferme le panel de chat

### 5. Sessions ACP
- Gérer `session/create`, `session/load`, `session/resume`
- Persistance des conversations via `session_id`
- `/reset`, `/compact`, `/branch` exposés comme commandes VS Code

## Phase 3 — Polish & Publication (Semaines 7-8)

### 1. Configuration workspace
- Fichier `.EVA/vscode.json` pour config par projet
- Détection automatique de `AGENTS.md` du workspace
- Intégration avec `EVA config` pour le modèle/provider

### 2. Tests
- Tests unitaires TypeScript (Vitest/Mocha)
- Tests d'intégration avec `@vscode/test-electron`
- Tests ACP avec mock du processus `EVA-acp`
- Tests E2E : spawn EVA-acp réel, envoyer une requête, vérifier la réponse

### 3. CI/CD
- `npm run compile` → vérifie la compilation TypeScript
- `npm run lint` → eslint
- `npm run test` → tests unitaires + intégration
- `vsce package` → génération du .vsix
- Pipeline GitHub Actions pour build + publication

### 4. Publication Marketplace
- Package VSIX → Microsoft Marketplace
- `README.md` avec captures d'écran et instructions
- Page de documentation sur le site EVA
- Gestion des versions alignée sur les releases EVA

## Fichiers clés côté EVA existants

| Fichier | Rôle pour l'extension |
|---------|----------------------|
| `acp_adapter/server.py` | EVAACPAgent — 2095 lignes, cœur ACP |
| `acp_adapter/entry.py` | Point d'entrée CLI `EVA-acp` |
| `acp_adapter/session.py` | SessionManager, SessionState |
| `acp_adapter/tools.py` | Conversion outils EVA ↔ ACP |
| `acp_adapter/permissions.py` | Modes (default/accept-edits/dont-ask) |
| `acp_adapter/events.py` | Streaming, callbacks, plan updates |
| `acp_adapter/edit_approval.py` | Approbation des éditions de fichiers |

## Dépendance

```toml
# pyproject.toml
[project.optional-dependencies]
acp = ["agent-client-protocol==0.9.0"]
```

## Estimation d'effort

| Phase | Contenu | Effort |
|-------|---------|--------|
| 1.1 — Squelette | Init projet, ACP client, chat panel webview | 3 semaines |
| 1.2 — Code | Contexte éditeur, inline edit, diagnostics | 3 semaines |
| 1.3 — Polish | Configuration, tests, publication Marketplace | 2 semaines |
| **Total** | | **8 semaines (1 dev full-time)** |

## Risques

1. **Spec ACP évolutive** — le protocole `agent-client-protocol` évolue rapidement ; nécessite une veille sur les versions
2. **Parsing streaming** — le streaming JSON-RPC sur stdio peut être complexe à parser côté TypeScript (messages fragmentés)
3. **Installation utilisateur** — `EVA-acp` nécessite Python + EVA installé ; prévoir un setup wizard dans l'extension
4. **Sécurité** — le spawn de processus avec accès fichiers doit respecter les permissions VS Code (workspace trust)
5. **Windows** — le spawning de processus Python sur Windows a des particularités (PATH, venv activation)