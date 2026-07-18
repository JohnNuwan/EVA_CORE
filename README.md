<p align="center">
  <img src="assets/banner.png" alt="Agent EVA" width="100%">
</p>

# Agent EVA ☤
<p align="center">
  <a href="https://github.com/JohnNuwan/EVA_CORE">Agent EVA</a>
</p>
<p align="center">
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/JohnNuwan/EVA_CORE/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="Licence: MIT"></a>
</p>

**EVA, l'agent IA auto-améliorant basé sur Hermes Agent.** C'est le seul agent doté d'une boucle d'apprentissage intégrée : il crée des compétences (skills) à partir de son expérience, les améliore en cours d'utilisation, s'incite à conserver ses connaissances, recherche dans ses propres conversations passées et construit un modèle approfondi de qui vous êtes au fil des sessions. Lancez-le sur un VPS à 5 $, un cluster GPU ou une infrastructure serverless qui ne coûte presque rien lorsqu'elle est inactive. Il n'est pas lié à votre ordinateur : parlez-lui depuis Telegram pendant qu'il travaille sur une machine virtuelle dans le cloud.

Utilisez le modèle que vous souhaitez : Portal, OpenRouter, OpenAI, votre propre endpoint, et bien d'autres. Changez avec `eva model` — aucun changement de code, aucun verrouillage.

<table>
<tr><td><b>Une véritable interface terminal</b></td><td>TUI complet avec édition multiligne, saisie semi-automatique des commandes slash, historique des conversations, interruption et redirection, et sortie d'outil en streaming.</td></tr>
<tr><td><b>Vit là où vous vivez</b></td><td>Telegram, Discord, Slack, WhatsApp, Signal et CLI — le tout depuis un seul processus passerelle. Transcription de mémos vocaux, continuité des conversations multiplateformes.</td></tr>
<tr><td><b>Une boucle d'apprentissage fermée</b></td><td>Mémoire organisée par l'agent avec des rappels périodiques. Création autonome de compétences après des tâches complexes. Les compétences s'auto-améliorent en cours d'utilisation. Recherche de session FTS5 avec résumé LLM pour le rappel inter-sessions. Modélisation de l'utilisateur par dialectique <a href="https://github.com/plastic-labs/honcho">Honcho</a>. Compatible avec le standard ouvert <a href="https://agentskills.io">agentskills.io</a>.</td></tr>
<tr><td><b>Automatisations planifiées</b></td><td>Planificateur cron intégré avec livraison sur n'importe quelle plateforme. Rapports quotidiens, sauvegardes nocturnes, audits hebdomadaires — le tout en langage naturel, fonctionnant de manière autonome.</td></tr>
<tr><td><b>Délègue et parallélise</b></td><td>Lancez des sous-agents isolés pour des flux de travail parallèles. Écrivez des scripts Python qui appellent des outils via RPC, réduisant les pipelines multi-étapes à des tours à coût de contexte nul.</td></tr>
<tr><td><b>Fonctionne partout, pas seulement sur votre ordinateur</b></td><td>Six backends de terminal — local, Docker, SSH, Singularity, Modal et Daytona. Daytona et Modal offrent une persistance serverless — l'environnement de votre agent hiberne lorsqu'il est inactif et se réveille à la demande, ne coûtant presque rien entre les sessions. Lancez-le sur un VPS à 5 $ ou un cluster GPU.</td></tr>
<tr><td><b>Prêt pour la recherche</b></td><td>Génération de trajectoires par lots, compression de trajectoires pour l'entraînement de la prochaine génération de modèles d'appel d'outils (tool-calling).</td></tr>
</table>

---

## Installation Rapide

### Linux, macOS, WSL2, Termux

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

### Windows (natif, PowerShell)

> **Attention :** Windows natif exécute EVA sans WSL — l'interface CLI, la passerelle, la TUI et les outils fonctionnent tous nativement. Si vous préférez utiliser WSL2, la commande d'une ligne pour Linux/macOS ci-dessus fonctionne également. Vous avez trouvé un bug ? N'hésitez pas à [signaler des problèmes](https://github.com/NousResearch/hermes-agent/issues).

Exécutez ceci dans PowerShell :

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

L'installateur s'occupe de tout : uv, Python 3.11, Node.js, ripgrep, ffmpeg, **et un Git Bash portable** (MinGit, décompressé dans `%LOCALAPPDATA%\hermes\git` — sans privilèges administrateur requis, totalement isolé). EVA utilise ce Git Bash fourni pour exécuter les commandes du terminal.

Si vous avez déjà Git installé, l'installateur le détecte et l'utilise. Sinon, le téléchargement de ~45 Mo de MinGit suffit — cela n'interférera pas avec d'autres installations Git du système.

Après l'installation :

```bash
source ~/.bashrc    # recharger le terminal (ou : source ~/.zshrc)
hermes              # démarrer la conversation !
```

---

## Démarrage Rapide

```bash
hermes              # CLI Interactive — démarrer une conversation
hermes model        # Choisir votre fournisseur LLM et votre modèle
hermes tools        # Configurer les outils activés
hermes config set   # Définir des valeurs de configuration individuelles
hermes gateway      # Démarrer la passerelle de messagerie (Telegram, Discord, etc.)
hermes setup        # Lancer l'assistant de configuration complet
hermes update       # Mettre à jour vers la dernière version
hermes doctor       # Diagnostiquer les problèmes éventuels
```

📖 **[Documentation complète →](https://hermes-agent.nousresearch.com/docs/)**

---

## Raccourcis CLI vs Messagerie

EVA a deux points d'entrée : démarrer l'interface du terminal (TUI) avec `hermes`, ou lancer la passerelle (gateway) et lui parler depuis Telegram, Discord, Slack, WhatsApp, Signal ou par e-mail. Une fois dans une conversation, de nombreuses commandes slash sont partagées entre les deux interfaces.

| Action | CLI | Plateformes de messagerie |
| :--- | :--- | :--- |
| Commencer à discuter | `hermes` | Lancer `hermes gateway setup` + `hermes gateway start`, puis envoyer un message au bot |
| Commencer une nouvelle discussion | `/new` ou `/reset` | `/new` ou `/reset` |
| Changer de modèle | `/model [fournisseur:modèle]` | `/model [fournisseur:modèle]` |
| Définir une personnalité | `/personality [nom]` | `/personality [nom]` |
| Réessayer ou annuler le dernier tour | `/retry`, `/undo` | `/retry`, `/undo` |
| Compresser le contexte / vérifier l'usage | `/compress`, `/usage`, `/insights [--days N]` | `/compress`, `/usage`, `/insights [jours]` |
| Parcourir les compétences (skills) | `/skills` ou `/<nom-de-skill>` | `/<nom-de-skill>` |
| Interrompre le travail en cours | `Ctrl+C` ou envoyer un nouveau message | `/stop` ou envoyer un nouveau message |
| Statut spécifique à la plateforme | `/platforms` | `/status`, `/sethome` |

Pour les listes complètes de commandes, consultez le [guide de la CLI](https://hermes-agent.nousresearch.com/docs/user-guide/cli) et le [guide de la passerelle de messagerie](https://hermes-agent.nousresearch.com/docs/user-guide/messaging).

---

## Licence

MIT — voir [LICENSE](LICENSE).

Basé sur Hermes Agent par [Nous Research](https://nousresearch.com).
