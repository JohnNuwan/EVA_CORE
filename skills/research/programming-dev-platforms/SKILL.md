---
name: programming-dev-platforms
description: "Compétence niveau ingénieur/docteur sur les plateformes de programmation et développement logiciel. Couvre les IDE (VS Code, Cursor, Windsurf, JetBrains), les outils de code (GitHub Copilot, Claude Code, Codex CLI), CI/CD (GitHub Actions, GitLab CI), les registres de packages, les cloud dev (GitHub Codespaces), et les plateformes de code review."
category: research
tags: [ide, devtools, cicd, code-review, cloud-dev, agents-de-code, programmation]
---

# Plateformes de Programmation et Développement — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des plateformes, outils et environnements de développement logiciel moderne. Conçu pour un niveau ingénieur/docteur nécessitant une maîtrise de l'écosystème IDE, des agents de code, de l'intégration continue, de la qualité logicielle, et du déploiement cloud-native.

---

## 1. IDEs et Éditeurs

### VS Code (Visual Studio Code)
- **Base** : Electron, TypeScript, extensions
- **Extensions clés** :
  - Langages : Python, JavaScript/TypeScript, Rust, Go, C++, Java
  - AI : GitHub Copilot, Continue.dev, Cline, Supermaven
  - DevOps : Docker, Kubernetes, Terraform, GitHub Actions
  - Debug : Python Debugger, JavaScript Debugger, Live Share
  - Productivité : GitLens, Prettier, ESLint, Error Lens, Path Intellisense
- **Remote Development** : SSH, WSL, Containers (Dev Containers)
- **Tunnels** : VS Code Server, vscode.dev
- **Settings Sync** : Comptes GitHub/Microsoft, profiles

### Cursor (AI-first IDE)
- **Base** : Fork VS Code, optimisé pour l'IA
- **Fonctionnalités** :
  - Cursor Tab : Auto-complétion intelligente, multi-line, edit
  - Cursor Chat : Chat contextuel, Apply, Edit, Agent mode
  - CMD+K : Édition inline, refactoring, generation
  - Composer : Multi-file editing, project-wide changes
  - Agent : Autonomous coding, terminal, search, web
- **Modèles** : Claude Sonnet 4, GPT-4o, Gemini 2.5 Pro, Custom
- **Rules** : .cursorrules, global rules, project rules
- **Privacy** : Privacy mode, local models
- **Pricing** : Hobby (gratuit), Pro ($20/mois), Business ($40/mois)

### Windsurf (Codeium)
- **Base** : Fork VS Code, AI-native
- **Fonctionnalités** :
  - Cascade : IA agentic, auto-suggestions multi-file
  - Tab autocomplete : prédictions contextuelles
  - Chat : @-mentions, context-aware
  - Supercomplete : superposé, diff
- **Modèles** : Windsurf AI (propriétaire), Claude, GPT
- **Pricing** : Free (Windsurf AI), Pro ($15/mois), Pro Ultimate ($35/mois)

### JetBrains Suite
- **IDEs** : IntelliJ IDEA (Java), PyCharm (Python), CLion (C/C++), GoLand (Go), WebStorm (JS/TS), Rider (.NET), RubyMine (Ruby)
- **Fonctionnalités** :
  - Smart completion, refactoring, navigation
  - Debugger, profiler, test runner, VCS
  - Database tools, HTTP client, terminal
  - AI Assistant (JetBrains AI) : chat, completion, test generation
  - Remote Development : JetBrains Gateway, Code With Me
- **Pricing** : Community (gratuit), Ultimate ($199-649/an)
- **Ecosystem** : Space, TeamCity, YouTrack, Upsource

### Zed
- **Base** : Rust, GPUI, multi-threaded
- **Fonctionnalités** : Vim mode, LSP natif, collaboration, AI
- **Performance** : Démarrage instantané, zéro lag
- **Modèles** : Assistant IA intégré (Claude, GPT)
- **Pricing** : Gratuit (open-source)

### Neovim (LSP-Native)
- **Base** : Vim fork, Lua scripting
- **LSP** : `nvim-lspconfig`, `mason`, `cmp`, `telescope`
- **Plugins** : `lazy.nvim`, `which-key`, `telescope`, `oil.nvim`
- **AI** : `continue.nvim`, `copilot.lua`, `codeium.nvim`
- **Usage** : Puissance, personnalisation totale, vim motions

---

## 2. Agents de Code

### Claude Code (Anthropic)
- **Type** : Terminal-native, agentic
- **CLI** : `claude` command, explorateur de code
- **Capacités** : Édition, terminal, recherche, web, git
- **Modèle** : Claude Opus 4 / Sonnet 4
- **Intégration** : MCP (Model Context Protocol), tools
- **Fonctionnalités** : Plan, bash, edit, glob, grep, web fetch
- **Pricing** : API-based (pay-per-token)

### OpenAI Codex CLI
- **Type** : Terminal-native, agentic
- **CLI** : `codex` command, sandbox sécurisé
- **Capacités** : Édition, bash, web, recherche
- **Modèle** : GPT-4o, o-series
- **Fonctionnalités** : Sandbox, plan, explain, test
- **Pricing** : API-based (pay-per-token)

### Cursor Agent
- **Type** : IDE intégré, agentic
- **Activation** : Cmd+I (Agent mode)
- **Capacités** : Édition multi-file, terminal, recherche, web
- **Modèle** : Claude, GPT, Custom
- **Fonctionnalités** : Plan, read, edit, search, bash, web

### GitHub Copilot
- **Copilot Chat** : VS Code, JetBrains, Neovim, GitHub.com
- **Copilot Workspace** : Agent de développement orienté PR
- **Copilot Edits** : Multi-file edits, agent mode
- **Copilot Code Review** : PR review automatisée
- **Copilot CLI** : `gh copilot` — commandes shell
- **Modèles** : GPT-4o, Claude, Gemini, DeepSeek
- **Pricing** : Free (Chat), Individual ($10/mois), Business ($19/mois), Enterprise ($39/mois)

### Autres Agents
- **Continue.dev** : Open-source AI code assistant, multi-IDE
- **Aider** : AI pair programming, terminal, git-aware
- **OpenDevin** : Autonomous software dev agent (79k stars)
- **Cline** : VS Code extension, autonomous agent, MCP
- **Tabby** : Self-hosted AI code assistant, open-source

---

## 3. CI/CD & DevOps

### GitHub Actions
- **Runner** : GitHub-hosted (Linux/Windows/Mac), self-hosted
- **Workflows** : YAML, events, jobs, steps, matrix
- **Marketplace** : 20k+ actions, community
- **Fonctionnalités** :
  - CI/CD, tests, build, deploy, release
  - Environments, secrets, variables, cache
  - Service containers, artifacts, pages
  - Composite actions, reusable workflows, OIDC
- **Pricing** : Free (2000 min/mois), Team, Enterprise

### GitLab CI/CD
- **Runner** : GitLab-hosted, shared, specific, group, self-hosted
- **Pipelines** : Stages, jobs, artifacts, cache
- **GitLab CI YAML** : `include`, `rules`, `needs`, `parallel`
- **Fonctionnalités** :
  - Auto DevOps, review apps, container registry
  - DAST, SAST, Dependency Scanning, Secret Detection
  - Pages, environments, releases, approvals
- **Pricing** : Free (400 min/mois), Premium ($29/mois), Ultimate

### Jenkins
- **Type** : Pipeline automatisé, auto-hébergé
- **Pipelines** : Declarative (YAML) et Scripted (Groovy)
- **Fonctionnalités** : Plugins, agents, webhooks, schedule
- **Usage** : Entreprise, customisation maximale

### ArgoCD
- **Type** : GitOps, Kubernetes-native
- **Fonctionnalités** : Sync, diff, rollback, auto-healing
- **Intégration** : Helm, Kustomize, Jsonnet, plain YAML
- **Usage** : Déploiement Kubernetes, GitOps workflow

### Docker & Kubernetes
- **Docker** : Build, ship, run — containers, images, compose
- **Kubernetes** : Orchestration, scaling, service discovery
- **Fonctionnalités** : Pods, deployments, services, ingress, configmaps
- **Ecosystem** : Helm, Kustomize, Istio, Prometheus, Grafana
- **Cloud** : EKS (AWS), AKS (Azure), GKE (GCP), DOKS

### Terraform / OpenTofu
- **Type** : Infrastructure as Code (IaC)
- **Providers** : AWS, GCP, Azure, K8s, Cloudflare, GitHub
- **Fonctionnalités** : State, modules, workspaces, plan/apply
- **OpenTofu** : Fork open-source, Linux Foundation, OSS licence

---

## 4. Code Review & Qualité

### SonarQube / SonarCloud
- **Analyse** : Code quality, security, maintainability
- **Métriques** : Duplication, coverage, complexity, smells
- **Qualité Gates** : Seuils, conditions, blocage de merge
- **Langages** : 30+ langages supportés
- **SonarCloud** : Cloud SaaS, gratuit pour projets open-source

### CodeQL (GitHub)
- **Analyse** : Semantic code analysis, security queries
- **Langages** : C/C++, C#, Go, Java, JavaScript, Python, Ruby, TypeScript
- **Intégration** : GitHub Actions, CI/CD
- **Usage** : Sécurité, vulnerabilities, supply chain

### ESLint / Prettier / Ruff / mypy
- **ESLint** : JavaScript/TypeScript linting, règles configurables
- **Prettier** : Formateur de code, standardisé
- **Ruff** : Python linter, 10-100x plus rapide que Flake8
- **mypy** : Type checking statique Python
- **Typage** : TypeScript, Pyright, mypy, Hack

### Git Hooks (pre-commit)
- **Framework** : pre-commit, hooks automatiques
- **Hooks** : lint, format, types, secrets, security
- **Config** : `.pre-commit-config.yaml`
- **Usage** : Qualité à chaque commit, validation CI

### Semgrep
- **Analyse** : Static analysis, pattern matching
- **Règles** : 2000+ règles sécurité, custom patterns
- **Langages** : 30+ langages, generic AST
- **Usage** : SAST, security, code review automatisé

---

## 5. Cloud Development

### GitHub Codespaces
- **Base** : VM cloud, VS Code dans le navigateur
- **Dev Container** : `.devcontainer/devcontainer.json`
- **Spécifications** : 2-32 cores, 4-64 GB RAM, 32-256 GB SSD
- **Intégration** : GitHub repos, dotfiles, secrets
- **Pricing** : Free (60h/mois/2-core), Pro ($4/mois, 180h)

### GitPod
- **Base** : Workspaces cloud, VS Code/Theia
- **Config** : `.gitpod.yml` (tasks, ports, env)
- **Fonctionnalités** : Prebuilds, snapshots, teams
- **Pricing** : Free (50h/mois)

### DevContainer Specification
- **Standard** : Containers de développement, VS Code + GitHub Codespaces
- **Config** : `devcontainer.json`, `Dockerfile`, `docker-compose.yml`
- **Features** : Langages, outils, services, extensions
- **Usage** : Environnement reproductible, collaboration

### AWS Cloud9
- **Base** : Cloud IDE, EC2-backed
- **Fonctionnalités** : Terminal, debug, pair programming
- **Intégration** : AWS SAM, Lambda, CDK
- **Pricing** : Gratuit (EC2 t2.micro 1 an)

---

## 6. PaaS & Déploiement

### Vercel
- **Type** : Frontend cloud, serverless functions, edge
- **Framework** : Next.js, Svelte, Astro, Nuxt, Remix
- **Fonctionnalités** : Edge Functions, ISR, SSR, Analytics
- **Pricing** : Hobby (gratuit), Pro ($20/mois)

### Netlify
- **Type** : Jamstack, serverless, edge functions
- **Fonctionnalités** : Forms, Identity, Functions, Large Media
- **Pricing** : Free (100GB/mois), Pro ($19/mois)

### Railway
- **Type** : Full-stack deployment, templates
- **Fonctionnalités** : Private networking, volumes, cron
- **Pricing** : Free ($5 crédits), $5+/mois

### Fly.io
- **Type** : Edge compute, global deployment
- **Fonctionnalités** : Anycast, volumes, private networking
- **Pricing** : Free (3 VMs), usage-based

### Cloudflare Workers
- **Type** : Edge computing, serverless
- **Runtime** : V8 isolates, JavaScript/WASM
- **Fonctionnalités** : KV, D1, R2, Queues, Durable Objects
- **Pricing** : Free (100k req/jour), Paid ($5/mois, 10M req)

---

## 7. Catégories et Tableau Comparatif

| Catégorie | Outils | Type |
|-----------|--------|------|
| IDEs | VS Code, Cursor, Windsurf, JetBrains, Zed, Neovim | Édition de code |
| Agents IA | Claude Code, Codex CLI, Cursor Agent, Copilot, Continue | Génération autonome |
| CI/CD | GitHub Actions, GitLab CI, Jenkins, ArgoCD | Intégration continue |
| Qualité | SonarQube, CodeQL, Semgrep, pre-commit, Ruff | Review, lint, sécurité |
| Cloud Dev | Codespaces, GitPod, DevContainer, Cloud9 | Dev cloud |
| PaaS | Vercel, Netlify, Railway, Fly.io, Cloudflare Workers | Déploiement |
| IaC | Terraform, OpenTofu, Pulumi, CDK | Infrastructure |
| Package | npm, PyPI, cargo, crates.io, Docker Hub, GitHub Packages | Registres |

---

## 8. Workflow de Développement Moderne

### Pipeline Type
1. **Dev Environment** : Codespaces/Docker DevContainer
2. **Code Editing** : Cursor/VS Code + Claude Code/Codex CLI
3. **Code Review** : pre-commit hooks → SonarQube → GitHub Review
4. **CI/CD** : GitHub Actions (test, lint, build, deploy)
5. **Deployment** : Vercel (frontend) / Railway (backend) / K8s (infra)
6. **Monitoring** : Sentry, Datadog, Grafana, CloudWatch

### Stack Type pour Agent Development
```bash
# Stack moderne de développement
# IDE: Cursor with Claude Sonnet 4
# Agent: Claude Code / Codex CLI
# CI: GitHub Actions
# Deploy: Vercel + Railway
# Quality: pre-commit, Ruff, mypy, Semgrep
```

---

## Ressources

- [VS Code Docs](https://code.visualstudio.com/docs)
- [Cursor Docs](https://docs.cursor.com)
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [JetBrains IDE Guide](https://www.jetbrains.com/guide)
- [DevContainer Spec](https://containers.dev)
- [Vercel Docs](https://vercel.com/docs)
- [Cloudflare Workers](https://developers.cloudflare.com/workers)