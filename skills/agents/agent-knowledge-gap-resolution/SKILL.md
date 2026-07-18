---
name: agent-knowledge-gap-resolution
description: "Combler les lacunes de connaissance par recherche web."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
metadata:
  helios:
    tags: [agents, web-search, knowledge, behavior, browser]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# Agent Knowledge Gap Resolution

## Rôle et Identité
Vous êtes un agent qui, face à une question pour laquelle il ne possède ni skill ni connaissance fiable, doit **obligatoirement** chercher l'information sur internet au lieu d'improviser.

## Vue d'ensemble
Le modèle de l'agent a une date de cutoff fixe. De nombreux sujets techniques (nouveaux automates, normes mises à jour, APIs récentes, frameworks émergents) lui sont inconnus. Plutôt que d'improviser une réponse plausible mais potentiellement fausse, l'agent doit utiliser ses outils de navigation web pour trouver la documentation officielle, les spécifications techniques, ou les sources autoritatives, puis synthétiser une réponse basée sur ces sources.

## Quand l'utiliser
- Lorsque l'agent ne trouve **aucun skill** correspondant au sujet demandé.
- Lorsque les skills existants sont manifestement **obsolètes ou incomplets**.
- Lorsque l'utilisateur demande une information sur un **produit, une norme, ou une technologie sortis après la date de cutoff** de l'agent.
- Lorsque l'agent s'apprête à répondre avec des formulations comme « je pense que », « probablement », « il me semble » sur un sujet non couvert par ses skills.

## Workflow Obligatoire

```
Question utilisateur
        │
        ▼
┌─────────────────────────────┐
│ Skill existant et fiable ?  │
└──────────────┬──────────────┘
       OUI    │    NON
       ▼      │      ▼
  Utiliser    │  ┌──────────────────────────┐
  le skill    │  │ browser_navigate() ou    │
              │  │ recherche web            │
              │  └──────────┬───────────────┘
              │             ▼
              │  ┌──────────────────────────┐
              │  │ Extraire l'info          │
              │  │ (doc officielle, specs,  │
              │  │ datasheets, RFC, normes) │
              │  └──────────┬───────────────┘
              │             ▼
              │  ┌──────────────────────────┐
              │  │ Synthétiser → Répondre   │
              │  │ Créer/Patch un skill     │
              │  └──────────────────────────┘
```

## Directives de Recherche

### 1. Sources Prioritaires
1. Documentation officielle du constructeur/éditeur
2. Normes et standards (IEC, ISO, ISA, etc.)
3. Data sheets et manuels techniques
4. RFCs, specifications techniques, white papers
5. Forums techniques reconnus (Stack Overflow, Reddit spécialisé) — en dernier recours

### 2. Ce qu'il faut extraire
- Spécifications techniques précises (pas de paraphrases vagues)
- Schémas, tableaux, diagrammes pertinents
- Code d'exemple et bonnes pratiques documentées
- Limitations et contraintes officielles

### 3. Actions post-recherche
- **Créer un nouveau skill** si le sujet est récurrent et n'existait pas
- **Patcher un skill existant** si l'information le complète ou le corrige
- **Stocker en mémoire** les faits ponctuels (URLs, versions, dates de cutoff)

## Pièges Courants

1. **Improviser au lieu de chercher :**
   - *Erreur* : Répondre « je pense que le Sinamics S210 supporte... » sans avoir vérifié.
   - *Correction* : Naviguer sur `siemens.com`, chercher la fiche technique, extraire les specs réelles.

2. **Chercher trop superficiellement :**
   - *Erreur* : Lire le premier paragraphe d'une page et synthétiser.
   - *Correction* : Parcourir la page complète, les sections techniques, les tableaux de specs.

3. **Ne pas capitaliser après la recherche :**
   - *Erreur* : Fournir la réponse sans créer de skill → la prochaine session repart de zéro.
   - *Correction* : Créer ou patcher un skill avec les informations trouvées.

4. **Sources non autoritatives :**
   - *Erreur* : Citer un blog personnel ou un thread de forum comme source fiable.
   - *Correction* : Toujours remonter à la source officielle (constructeur, éditeur de la norme).

5. **Recherche non-exhaustive des variantes :**
   - *Erreur* : Trouver le dépôt principal d'une technologie et s'arrêter, sans vérifier les sous-projets, forks officiels, ou variantes dans la même organisation.
   - *Correction* : Explorer l'organisation GitHub complète (`github.com/orgs/<org>/repositories?q=<topic>`), chercher les papiers dérivés, vérifier les dépôts liés. Exemple concret : JEPA = 7 repos facebookresearch, pas uniquement le principal.

## Checklist
- [ ] Vérifier qu'aucun skill existant ne couvre le sujet
- [ ] Naviguer vers la documentation officielle ou la source la plus autoritative
- [ ] Extraire les informations techniques précises (pas de paraphrase)
- [ ] Synthétiser la réponse avec citations des sources
- [ ] Créer ou patcher un skill pour capitaliser la connaissance acquise