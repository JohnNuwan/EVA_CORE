# 🎯 Guide des Compétences (*Skills*) dans EVA

Dans EVA, les **Compétences (*Skills*)** représentent la couche de connaissances et de procédures métier. Contrairement aux outils (*Tools*) qui sont du code exécutable Python, les *Skills* sont des déclarations structurées en Markdown + YAML qui guident les décisions et le raisonnement de l'agent.

EVA embarque plus de **1072+ Skills** réparties dans 50+ catégories métiers (Automatisme industriel, Trading MetaTrader 5, Cybersécurité OT/IT, RAG, DevOps, etc.).

---

## 📁 Anatomie d'un Fichier `SKILL.md`

Chaque compétence vit dans son propre sous-dossier et contient obligatoirement un fichier `SKILL.md`.

```
skills/
└── industrial-automation/
    └── modbus-tcp/
        ├── SKILL.md            # Directives principales et YAML frontmatter
        ├── scripts/            # Scripts d'aide ou utilitaires optionnels
        └── references/         # Documentation étendue (> 500 lignes)
```

### Structure du Fichier `SKILL.md`

Un fichier `SKILL.md` se compose de deux parties :

```markdown
---
name: industrial-modbus-tcp
description: Directives d'interrogation et de diagnostic pour les automates communiquant via Modbus TCP/IP.
---

# Directives Modbus TCP/IP

Lors de l'analyse d'un réseau Modbus TCP :

1. **Vérification des Registres** :
   - Holding Registers : Adresse `40001` (Offset 0x00).
   - Input Registers : Adresse `30001`.

2. **Consignes de Sécurité** :
   - Ne jamais exécuter de commande d'écriture (`0x06` ou `0x10`) sans confirmation préalable de l'opérateur en environnement de production.
```

---

## 🔄 Chargement & Découverte Automatique

Les compétences sont découvertes automatiquement par EVA selon l'ordre de priorité suivant :

1. **Racine Locale du Projet** : `.agents/skills/<skill_name>/SKILL.md`
2. **Racine Globale de l'Utilisateur** : `~/.hermes/skills/<skill_name>/SKILL.md`
3. **Bibliothèque Intégrée** : `skills/<domaine>/<skill_name>/SKILL.md`

### Inscription Personnalisée (`skills.json`)
Pour ajouter un répertoire de compétences partagé en équipe, créez ou modifiez `skills.json` à la racine de votre dossier de configuration :

```json
{
  "entries": [
    { "path": "/opt/team-shared-skills" }
  ]
}
```

---

## ⚡ Règle d'Or : Stabilité du Prompt Cache

Afin de préserver la **mise en cache des invites (prompt caching)** de vos modèles LLM :

> [!IMPORTANT]
> Ne jamais injecter de variables dynamiques changeantes à chaque tour (dates, timestamps précis, GUIDs aléatoires) dans l'en-tête système d'un `SKILL.md`. Toute donnée dynamique doit passer par les messages de conversation ou des blocs pré-alloués.

---

## 📚 Principales Catégories de Compétences

| Domaine | Nombre de Skills | Exemples de Compétences |
| --- | --- | --- |
| **Automatisme Industriel** | 184+ | Siemens S7, Rockwell Allen-Bradley, Beckhoff ADS, Modbus, OPC UA. |
| **Cybersécurité & OT** | 140+ | Pentest OT, analyse PCAP, audit SIL, reverse-engineering, forensics. |
| **Recherche & Veille** | 160+ | arXiv parser, synthèse scientifique, scraping structuré. |
| **Finance & Trading** | 12+ | MetaTrader 5 API, RSI & Moving Averages, Paper Trading local. |
| **DevOps & Infrastructure** | 22+ | Docker, Kubernetes, CI/CD, GPU Allocation vLLM. |
| **Prompt Engineering** | 22 | 22 méthodes avancées d'optimisation de prompts. |
