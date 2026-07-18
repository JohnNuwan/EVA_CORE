# Agent EVA - Guide de Développement

Instructions pour les assistants de codage IA et les développeurs travaillant sur la base de code d'EVA (hermes-agent).

**Ne renoncez jamais à la bonne solution.**

## Qu'est-ce qu'EVA ?

EVA est un agent IA personnel qui exécute le même cœur d'agent sur une CLI, une passerelle de messagerie (Telegram, Discord, Slack et environ 20 autres plateformes), une TUI et une application de bureau Electron. Il apprend d'une session à l'autre (mémoire + compétences), délègue à des sous-agents, exécute des tâches planifiées et pilote un terminal et un navigateur réels. Ses capacités s'étendent principalement via des **plug-ins et des compétences (skills)**, et non en faisant grossir le noyau central.

Deux propriétés fondamentales guident chaque décision de conception et doivent être le prisme de relecture de toute modification :

- **La mise en cache des invites (prompt caching) par conversation est sacrée.** Une conversation longue réutilise un préfixe mis en cache à chaque tour. Tout ce qui modifie le contexte passé, échange les ensembles d'outils ou reconstruit l'invite système au milieu de la conversation invalide ce cache et multiplie par 10 le coût des tokens pour l'utilisateur. Nous ne le faisons pas (la seule exception est la compression de contexte).
- **Le cœur est une taille étroite ; les capacités vivent aux extrémités.** Chaque outil de modèle que nous ajoutons est envoyé à chaque appel d'API, le seuil d'intégration d'un nouvel outil dans le *cœur* est donc extrêmement élevé. Presque toutes les nouvelles fonctionnalités doivent arriver sous forme de commande CLI + compétence, outil lié à un service ou plug-in — et non comme surface du noyau.

---

## Rubrique de Contribution — Ce que nous voulons / Ce que nous refusons

### Ce que nous voulons

- **Corriger de vrais bugs, correctement.** L'essentiel de ce qui est intégré est des correctifs (`fix(...)`) contre un symptôme réel signalé. Un bon correctif reproduit le symptôme sur la branche `main` actuelle, pointe vers la ligne exacte où il se manifeste et corrige toute la classe de bugs.
- **Étendre la portée aux extrémités.** De nouveaux adaptateurs de plateforme, canaux, fournisseurs, modèles et fonctionnalités de bureau/TUI sont les bienvenus, à condition qu'ils s'intègrent dans l'UX existante (`hermes tools`, `hermes setup`, auto-install).
- **Garder le cœur étroit.** Les nouveaux outils de modèle sont l'exception coûteuse. Préférez, dans l'ordre : étendre le code existant → commande CLI + skill → outil lié à un service → plugin → serveur MCP dans le catalogue → nouvel outil central (dernier recours).
- **Mocks E2E réalistes, pas seulement de simples tests unitaires.** Pour tout ce qui touche à la configuration, la sécurité, l'I/O réseau/fichier, testez le comportement réel dans un `HERMES_HOME` temporaire.

### Ce que nous ne voulons pas (rejeté même si bien codé)

- **Infrastructure spéculative.** Hooks ou points d'extension sans consommateur concret.
- **Variables d'environnement non documentées pour de la configuration.** `.env` est réservé uniquement aux secrets (clés API, tokens). Tout paramètre comportemental (timeout, drapeaux de fonctionnalités, préférences d'affichage) va dans `config.yaml`.
- **Produits tiers / projets d'autres personnes intégrés au cœur.** Les plugins spécifiques à des services tiers (observabilité, SaaS tiers, etc.) ne vont pas dans le dépôt central. Publiez-les sous forme de **dépôt de plug-in autonome** que les utilisateurs installent dans `~/.hermes/plugins/`.

---

## Structure du Projet

```
hermes-agent/
├── run_agent.py          # Classe AIAgent — boucle de conversation principale
├── model_tools.py        # Orchestration des outils, discover_builtin_tools()
├── toolsets.py           # Définitions des ensembles d'outils
├── cli.py                # Classe HermesCLI — CLI interactive
├── hermes_state.py       # SessionDB — Stockage SQLite des sessions (FTS5)
├── hermes_constants.py   # Chemins conscients des profils
├── hermes_logging.py     # Configuration des logs (agent.log, etc.)
├── agent/                # Internes de l'agent (fournisseurs, mémoire, cache, etc.)
├── hermes_cli/           # Sous-commandes CLI, assistant d'installation, skins
├── tools/                # Implémentations d'outils
├── gateway/              # Passerelle de messagerie (Telegram, Discord, Slack...)
├── plugins/              # Système de plugins
├── skills/               # Compétences intégrées (skills)
├── ui-tui/               # Interface terminal Ink (React) — `hermes --tui`
└── tests/                # Suite de tests Pytest
```

**Configuration de l'utilisateur :** `~/.hermes/config.yaml` (paramètres), `~/.hermes/.env` (clés API uniquement).
**Logs :** `~/.hermes/logs/` — `agent.log`, `errors.log`, `gateway.log`.

---

## Directives de Codage & Style

- **Ne changez jamais les signatures des outils existants** sans assurer une compatibilité ascendante stricte.
- **Tests robustes obligatoires** pour tout nouvel outil ou modification de logique d'agent.
- **Mise en cache du prompt stable** : évitez d'injecter des données dynamiques comme des dates ou des chemins changeant à chaque tour directement dans le prompt système principal ; utilisez les messages utilisateur ou des blocs système spécifiques pré-alloués.
