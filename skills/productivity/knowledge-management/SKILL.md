---
name: knowledge-management
description: "Use when designing or maintaining knowledge management systems — wikis, knowledge bases, Zettelkasten, note-taking architectures, and organizational memory."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [knowledge-management, wiki, knowledge-base, zettelkasten, obsidian, notes, second-brain]
    related_skills: [information-architecture, markdown-systems, documentation-systems]
---

# Knowledge Management

## Overview

Le Knowledge Management (KM) est la discipline qui transforme l'information individuelle en mémoire organisationnelle réutilisable. Ce skill fournit les modèles, structures et workflows pour concevoir un système de gestion des connaissances — du wiki d'équipe au second-brain personnel — en maximisant la trouvabilité, la maintenabilité et l'évolutivité.

## When to Use

- L'utilisateur demande de structurer un wiki, une base de connaissances ou un vault Obsidian
- Vous devez auditer ou restructurer un référentiel de documentation existant
- Création d'un système de notes interconnectées (Zettelkasten, PARA, etc.)
- Définition de taxonomies, tags et conventions pour un dépôt de connaissances
- Planification d'une migration de connaissances (outil A vers outil B)

**Ne pas utiliser pour :** la rédaction de contenu spécifique (utiliser technical-writing), la documentation d'API (api-documentation).

## Architecture d'un Système de Connaissances

### Les 3 Couches d'un KM

```
1. ATOMIQUE (notes / fragments)
   └─ Idéal : notes fugaces, concepts atomiques, sources brutes
2. STRUCTURÉE (pages / articles)
   └─ Synthèses, guides, procédures — contenu réutilisable
3. NAVIGATION (index / MOC / tags)
   └─ Maps of Content, catégories, taxonomies — portes d'entrée
```

### Principes Fondamentaux

1. **Atomicité** — Une note = un concept. Si une note peut être divisée, divisez-la.
2. **Connexion explicite** — Chaque note a des liens sortants vers au moins 2 autres notes.
3. **Source de vérité unique** — Un concept est défini à un seul endroit ; les autres notes y font référence.
4. **Gradualité** — Commencer petit, laisser la structure émerger de l'usage. Ne pas sur-modéliser au départ.
5. **Rétro-trouvabilité** — Une note doit pouvoir être retrouvée par au moins 3 chemins différents (tag/titre/lien/plein-texte).

## Méthodologies de KM

### Zettelkasten (Luhmann)

- Notes atomiques (idées uniques) avec identifiant horodaté
- Liens bidirectionnels entre notes
- Notes d'index (hub notes) qui organisent des clusters
- Notes de structure (MOC — Maps of Content) qui remplacent les catégories rigides

### PARA (Tiago Forte)

| Type | Contenu | Action |
|------|---------|--------|
| **P**rojects | Résultats avec deadline | Actif / terminé / gelé |
| **A**reas | Responsabilités continues | Sans deadline, standard à maintenir |
| **R**esources | Sujets d'intérêt | Référence, veille, apprentissage |
| **A**rchives | Inactif | Tout ce qui n'est plus actif |

### DIKW Pyramid

Données → Information → Connaissance → Sagesse
- Chaque niveau ajoute du **contexte** et de la **relation**

## Taxonomie et Tags

### Règles pour un Système de Tags Sain

1. **Tags hiérarchiques limités** — `#devops/kubernetes`, `#lang/python` (max 2 niveaux)
2. **Pas de tags redondants avec la structure** — si le dossier s'appelle `API/`, pas besoin de tag `#api`
3. **Tags de statut** — `#status/draft`, `#status/approved`, `#status/stale`
4. **Tags de type** — `#type/tutorial`, `#type/reference`, `#type/concept`, `#type/glossary`
5. **Tags de public** — `#audience/dev`, `#audience/ops`, `#audience/pm`

### Frontmatter Standard pour Notes de Connaissances

```yaml
---
title: "Titre de la Note"
created: 2026-07-22
updated: 2026-07-22
tags: [tag1, tag2/ss]
status: draft | approved | stale
type: concept | tutorial | reference | glossary
sources:
  - url: https://...
    title: "Article source"
related:
  - "[[Note liée A]]"
  - "[[Note liée B]]"
---
```

## Workflow de Capture → Révision → Publication

1. **Capture** — Note brute (idée, citation, lien). Pas de structure, juste le contenu.
2. **Clarification** — Reformulation personnelle. Ajout de contexte et de liens.
3. **Classification** — Tags, type, status, relations
4. **Intégration** — Liens entrants/sortants, mise à jour des MOC concernés
5. **Révision** — Relecture, cohérence, exactitude (périodique)
6. **Publication** — Si applicable, transformation en documentation publique

## Maintenance et Hygiène

- **Revue trimestrielle** — Identifier les notes orphelines (sans liens entrants ni sortants)
- **Linting automatique** — Vérifier les liens brisés, les tags inutilisés, les doublons
- **Consolidation** — Notes trop proches fusionnées ; notes trop larges fractionnées
- **Date de péremption** — Les notes techniques > 6 mois non révisées reçoivent un flag `#status/stale`

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Vault personnel | Obsidian |
| Wiki d'équipe | Wiki.js, Gollum, DokuWiki |
| Base de connaissances | Confluence, BookStack |
| Linting notes | obsidian-linter, markdownlint |
| Graphe navigation | Obsidian Graph View, Foam (VS Code) |
| Backup | Git (toute base textuelle) |

## Common Pitfalls

1. **Sur-structuration précoce.** Définir trop de catégories et tags avant d'avoir du contenu mène à un système vide. Laissez la structure émerger des 50 premières notes.
2. **Notes orphelines.** Une note sans lien sortant est un silo. Une note sans lien entrant est une île. Les deux sont à corriger.
3. **Duplication involontaire.** Sans recherche avant d'écrire, on recrée des notes qui existent déjà. Toujours chercher d'abord.
4. **Collectionnite.** Capturer sans réviser crée un cimetière de notes. Le ratio capture/révision devrait être ~3:1.
5. **Absence de standards.** Sans frontmatter et conventions de tags, le système devient chaotique au-delà de 200 notes.

## Verification Checklist

- [ ] Toute note a ≥ 2 liens sortants
- [ ] Chaque note a un type (concept/tutorial/reference/glossary) et un statut
- [ ] Tags hiérarchiques limités à 2 niveaux max
- [ ] Aucune note orpheline (sans lien entrant) dans la zone active
- [ ] Un MOC (Map of Content) couvre chaque cluster de ≥ 10 notes
- [ ] Frontmatter YAML complet (title, created, updated, tags, type, status)
- [ ] Revue de maintenance planifiée (récurrence définie)