<p align="center">
  <img src="assets/banner.jpg" alt="Agent EVA" width="100%">
</p>

# ☤ Agent EVA — Evolving Virtual Assistant

<p align="center">
  <a href="https://github.com/JohnNuwan/EVA_CORE">Agent EVA</a> •
  <em>Le système d'exploitation agentique industriel et financier</em>
</p>

<p align="center">
  <a href="https://discord.gg/NousResearch"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord"></a>
  <a href="https://github.com/JohnNuwan/EVA_CORE/blob/main/LICENSE"><img src="https://img.shields.io/badge/Licence-MIT-green?style=for-the-badge" alt="Licence: MIT"></a>
  <img src="https://img.shields.io/badge/domaines-60+-blue?style=for-the-badge" alt="60+ domaines">
  <img src="https://img.shields.io/badge/agents_Adam-12-orange?style=for-the-badge" alt="12 Adam agents">
  <img src="https://img.shields.io/badge/skills-1072+-brightgreen?style=for-the-badge" alt="1072+ skills">
  <img src="https://img.shields.io/badge/GPU-2×_RTX_3090-76B900?style=for-the-badge&logo=nvidia&logoColor=white" alt="2× RTX 3090">
</p>

**EVA, l'agent IA auto-améliorant basé sur Hermes Agent.** C'est le seul agent doté d'une boucle d'apprentissage intégrée : il crée des compétences (skills) à partir de son expérience, les améliore en cours d'utilisation, s'incite à conserver ses connaissances, recherche dans ses propres conversations passées et construit un modèle approfondi de qui vous êtes au fil des sessions. Lancez-le sur un VPS à 5 $, un cluster GPU ou une infrastructure serverless qui ne coûte presque rien lorsqu'elle est inactive. Il n'est pas lié à votre ordinateur : parlez-lui depuis Telegram pendant qu'il travaille sur une machine virtuelle dans le cloud.

---

## 🚀 Bibliothèque de Capacités EVA (Finance & Industrie)

EVA n'est pas un simple assistant de code ; c'est un **système d'exploitation agentique industriel et financier** doté d'une bibliothèque gigantesque :

* 🎯 **1072+ Skills (Compétences Métiers) :** Des directives de haut niveau écrites en français pour guider les décisions de l'agent, couvrant 60+ domaines.
* 🛠️ **118+ Tools (Outils d'Exécution) :** Des scripts Python modulaires auto-enregistrés permettant à EVA d'agir directement sur son environnement.
* 🤖 **12 Agents Adam :** Une équipe d'agents spécialisés en CI/CD, QA, documentation, backup, et plus encore.

### 📈 Capacités de Finance & Trading (MetaTrader 5)

EVA intègre une suite de trading modulaire et sécurisée (architecture *Narrow Waist* : 1 Skill + 1 Tool par capacité) :
* **Analyse de Marché :** Calcul en temps réel des supports, résistances (fenêtre glissante de 5 bougies), RSI 10 et moyennes mobiles SMA 30/60.
* **Exécution d'Ordres :** Passage d'ordres d'achat, de vente, clôture et modification des niveaux de Stop Loss/Take Profit.
* **Double Mode :**
  1. **Paper Trading (Simulation) :** Bac à sable local persistant dans `~/.hermes/finance_positions.json` valorisé avec des cours réels (via `yfinance`).
  2. **Passage d'Ordres Réels :** Connexion HTTP vers l'API REST de MetaTrader 5.

### 🏭 Capacités d'Automatisation Industrielle (Industrie 4.0)

EVA dispose d'une suite complète pour piloter et diagnostiquer les systèmes automatisés physiques :
* **Protocoles Réseau :** Lecture/Écriture en OPC UA, Modbus TCP/IP, pilotes d'automates Rockwell, Siemens S7 et Beckhoff ADS.
* **Analyse PCAP :** Analyse passive et détection d'anomalies sur les réseaux opérationnels (OT).
* **Génération de Code & RAG :** Génération de code API automate et consultation de schémas/manuels via RAG industriel.
* **Sécurité Fonctionnelle :** Évaluation et optimisation de la sécurité opérationnelle (niveaux de performance SIL).

---

## 🏗️ Architecture — The Hive

```
┌─────────────────────────────────────────────────────────┐
│                    ☤ E.V.A (The Hive)                    │
│              2× RTX 3090 · AMD EPYC 32C · 125 GB        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │  vLLM    │  │  vLLM    │  │  vLLM    │  │ComfyUI │ │
│  │  :8001   │  │  :8002   │  │  :8003   │  │ :8188  │ │
│  │ DeepSeek 14B  │  │ -           │  │ -          │  │ Image  │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │Monitoring│  │   Wiki   │  │ RAG API  │  │Portainer│ │
│  │  :8081   │  │  :8082   │  │  :8083   │  │ :9443  │ │
│  │ Dashboard│  │  D3.js   │  │Actemium  │  │ Docker │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │  JEPA_EVA    │  │ ADAM-CI/CD   │  │  FTMO Agent    │ │
│  │  Trading RL  │  │  12 Agents   │  │  DreamerV3     │ │
│  │  GPU 0: entr │  │  Autonomes   │  │  FTMO Defi     │ │
│  └──────────────┘  └──────────────┘  └────────────────┘ │
│                                                         │
│  ┌─────────────────────────────────────────────────────┐ │
│  │         Gateway Messagerie (Telegram, Discord...)    │ │
│  │         CLI · TUI · Desktop Electron                │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 📊 Allocation GPU

| GPU | Usage | Services |
|-----|-------|---------|
| **GPU 0** | Entraînement | JEPA_EVA, FTMO DreamerV3, ADAM-LORA |
| **GPU 1** | Inférence | vLLM (3 profils), ComfyUI |

---

## 🤖 Adam Agents — L'Équipe Autonome

EVA orchestre une équipe de **12 agents spécialisés** (les Adam) qui travaillent en parallèle :

| Agent | Mission | Statut |
|-------|---------|--------|
| **ADAM-CICD** | Pipeline CI/CD, hooks git, auto-PR, déploiement | ✅ Actif |
| **ADAM-DOCS** | Génération et mise à jour de la documentation | ✅ Actif |
| **ADAM-LORA** | Fine-tuning QLoRA, extraction datasets, push HF | ✅ Actif |
| **ADAM-GIT** | Workflow git, synchronisation, gestion de branches | ✅ Actif |
| **ADAM-BACKUP** | Sauvegarde et récupération des données critiques | ✅ Actif |
| **ADAM-TEST** | Tests automatisés, validation de structure, rapports | ✅ Actif |
| **ADAM-RED** | Pentest, red team, audit de sécurité OT | ✅ Actif |
| **ADAM-BLUE** | Hardening, correctifs de sécurité, blue team | ✅ Actif |
| **ADAM-MONITOR** | Surveillance système, alertes, métriques | ✅ Actif |
| **ADAM-RAG** | Mise à jour du RAG industriel, indexation | ✅ Actif |
| **ADAM-DEPLOY** | Déploiement continu, rollback, validation | ✅ Actif |
| **ADAM-CURATOR** | Organisation des skills, dédoublonnage, catégorisation | ✅ Actif |

---

## 📊 Live Dashboard

Le monitoring en temps réel de The Hive est accessible via les dashboards suivants :

| Service | Port | Description |
|---------|------|-------------|
| **Monitoring Cybersec** | `http://192.168.1.5:8081` | Métriques CPU, RAM, GPU, réseau, alertes |
| **Wiki OKF (D3.js)** | `http://192.168.1.5:8082` | Graphe de connaissances, index des pages |
| **RAG Actemium** | `http://192.168.1.5:8083` | API de recherche RAG, stats `/api/rag/stats` |
| **Portainer** | `http://192.168.1.5:9443` | Gestion des conteneurs Docker |

---

## 📚 OKF Wiki — Open Knowledge Format

Le wiki EVA suit le format **OKF (Open Knowledge Format)** — un système de connaissances interconnectées :

- **60+ pages** organisées en entités, concepts et comparaisons
- **Graphe de connaissances D3.js** visualisé sur :8082
- **1072 skills** documentées en 52 catégories
- **Liens [[wikilinks]]** pour la navigation inter-pages
- **Frontmatter YAML** structuré sur chaque page

Le wiki vit dans `~/wiki/` et suit le schéma défini dans `~/wiki/SCHEMA.md`.

---

## 🔍 RAG Stack — Retrieval-Augmented Generation

EVA intègre un pipeline RAG industriel complet :

- **ChromaDB** — Base vectorielle locale pour la recherche sémantique
- **HippoRAG 2** — Indexation avancée avec graphe de connaissances
- **API REST** sur :8083 pour l'interrogation
- **Domaine :** Automatisme industriel (Actemium, manuels, schémas)

---

## 🛡️ Monitoring Cybersec

Suite de surveillance système et cybersécurité :

- **hardware-mon.sh** — CPU, RAM, GPU, disques, températures
- **network-mon.sh** — Bande passante, connexions, ARP spoofing
- **packet-capture.sh** — Capture de paquets avec rotation automatique
- **master-dashboard.sh** — Tableau de bord unifié toutes les 5s

Les scripts se trouvent dans `~/monitoring-cybersec/` et sont configurés via `config.ini`.

---

## 🧠 Bibliothèque de Connaissances

| Domaine | Skills | Description |
|---------|--------|-------------|
| Automatisme industriel | 184+ | Multi-constructeurs (Siemens, Rockwell, Beckhoff...) |
| Recherche scientifique | 160+ | arXiv, domaines académiques, veille |
| Cybersécurité | 140+ | Pentest, OSINT, reverse, forensics, OT |
| Prompt engineering | 22 | 22 méthodes avancées |
| DevOps / MLOPs | 22+ | Docker, Kubernetes, CI/CD, GPU training |
| Développement | 25+ | Python, test, GitHub, refactoring |
| Finance / Trading | 12+ | DéFi, analyse technique, options, DeFi |
| Création / Média | 14+ | ASCII art, design, audio, vidéo |
| Systèmes | 11+ | Linux, Windows AD, BSD, AIX, Solaris |
| Productivité | 13+ | Freelance, Notion, Airtable, PowerPoint |
| Edge AI / IoT | 14+ | TinyML, ESP32, FPGA, ARM embarqué |

---

## 💻 Utilisation

```
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

## Licence

MIT — voir [LICENSE](LICENSE).

Basé sur Hermes Agent par [Nous Research](https://nousresearch.com).