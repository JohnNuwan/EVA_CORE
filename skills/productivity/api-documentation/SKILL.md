---
name: api-documentation
description: "Use when writing, structuring, or reviewing API documentation — OpenAPI/Swagger specs, endpoint reference docs, SDK guides, and API changelogs."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, documentation, openapi, swagger, rest, developer-relations]
    related_skills: [technical-writing, information-architecture, markdown-systems]
---

# API Documentation

## Overview

L'API documentation est le point d'entrée de toute intégration développeur. Un développeur juge la qualité d'une API en 30 secondes sur sa documentation. Ce skill couvre la rédaction de documentation d'API REST, GraphQL, WebSocket et bibliothèques SDK — des spécifications OpenAPI aux guides d'intégration.

## When to Use

- L'utilisateur demande de documenter une API REST, GraphQL ou WebSocket
- Vous devez écrire ou auditer une spécification OpenAPI (ex-Swagger)
- Création d'un guide développeur, d'un tutoriel d'intégration ou d'un SDK README
- Mise à jour d'un changelog ou d'une documentation de migration entre versions d'API

## OpenAPI / Swagger

### Structure Minimale d'une Spec

```yaml
openapi: 3.1.0
info:
  title: API Nom du Produit
  version: 1.0.0
  description: |
    Description complète : cas d'usage, audience, limitations.
    Liens vers guide développeur et support.
  contact:
    name: Support API
    url: https://example.com/support
    email: api@example.com
servers:
  - url: https://api.example.com/v1
    description: Production
paths:
  /ressources:
    get:
      summary: Lister les ressources
      description: >
        Retourne une liste paginée de ressources.
        Filtrable par `status`, triable par `created_at`.
      operationId: listRessources
      parameters:
        - name: limit
          in: query
          schema: { type: integer, maximum: 100, default: 20 }
          description: Nombre d'éléments par page
```

### Règles pour une Spec OpenAPI de Qualité

1. **Chaque endpoint a `summary` ET `description`.** Le summary (≤ 60 chars) sert dans les index ; la description détaille le comportement, les cas limites, les prérequis.
2. **Tous les paramètres sont documentés** (nom, type, valeur par défaut, plage valide, exemple).
3. **Tous les codes de réponse sont listés** explicitement (pas de `default` paresseux).
4. **Les schémas sont réutilisés** via `$ref`, pas dupliqués.
5. **Exemples de requêtes/réponses** pour chaque endpoint — au moins un cas nominal.
6. **`operationId`** est un identifiant unique, en camelCase — les SDK l'utilisent comme nom de fonction.

## Guide Développeur — Structure Type

```
README.md d'un SDK ou API
├── Quickstart (5 min, 10 lignes de code max)
│   ├── Installation (pip / npm / go get)
│   ├── Authentification (clé API / OAuth)
│   └── Première requête
├── Concepts fondamentaux (3-5 sections)
│   ├── Ressources, collections, pagination
│   ├── Gestion des erreurs
│   └── Rate limiting
├── Guides d'intégration (par cas d'usage)
│   ├── « Créer un utilisateur »
│   ├── « Importer des données en masse »
│   └── « Webhooks en production »
├── Référence API (générée depuis OpenAPI)
└── Ressources
    ├── Changelog
    ├── Migration guides
    └── Support
```

## Documentation par Type d'API

### REST
- Endpoint → Verbe HTTP → Paramètres → Réponse → Erreurs
- Exemples avec `curl`, Python `requests`, et langages populaires
- Tableau des codes HTTP : 200, 201, 400, 401, 403, 404, 409, 422, 429, 500

### GraphQL
- Schéma (types, queries, mutations, subscriptions)
- Exemples de queries avec variables
- Documentation des arguments, types de retour, resolvers
- Stratégies de pagination (connections Relay, simple offset)
- Restrictions de profondeur et coût de requête

### WebSocket
- URL de connexion
- Format des messages (JSON : `event` + `data`)
- Séquence de handshake et heartbeat
- Tableau des événements (nom, direction, payload, déclencheur)
- Gestion des reconnexions et backoff

## Changelog API

Format basé sur [Keep a Changelog](https://keepachangelog.com/) + [SemVer](https://semver.org/) :

```
## [1.2.0] - 2026-07-22
### Added
- Nouvel endpoint `POST /webhooks` pour créer des webhooks sans appel support
- Paramètre `sort` sur `GET /ressources`

### Changed
- `GET /ressources` retourne désormais la pagination cursor-based
- Champ `name` passé de 64 à 255 caractères max

### Deprecated
- `GET /ressources?page=N` — utiliser `?cursor=...` à partir de v2.0

### Fixed
- `PATCH /ressources/:id` retournait 500 pour corps vide
```

## Style pour Documentation API

1. **Exemples réels et exécutables** — chaque bloc de code doit pouvoir être copié-collé
2. **Consistance des verbes** — `create` / `list` / `get` / `update` / `delete` (pas de mélange `fetch`/`retrieve`)
3. **Descriptions comportementales** — « Retourne la ressource mise à jour » et non « Met à jour la ressource »
4. **Tous les cas d'erreur documentés** — jamais de « peut retourner une erreur » sans détails

## Workflow de Mise à Jour

1. Modifier la spec OpenAPI (source de vérité)
2. Régénérer la doc de référence (`redocly build-docs`, `swagger-codegen`)
3. Mettre à jour les guides d'intégration si le comportement change
4. Ajouter une entrée au changelog
5. Vérifier les liens brisés et exemples

## Common Pitfalls

1. **Exemples qui ne marchent pas.** Copier-coller l'exemple doit fonctionner. Testez chaque bloc.
2. **Documenter ce que l'API fait, pas ce qu'elle devrait faire.** Si un comportement est inattendu, documentez-le honnêtement et créez un ticket.
3. **Ignorer les réponses d'erreur.** Un développeur passe plus de temps à déboguer qu'à intégrer. Chaque code d'erreur doit être documenté avec cause et résolution.
4. **Version non synchronisée.** La version dans l'URL, dans le changelog et dans la spec doivent correspondre.

## Outils Recommandés

| Besoin | Outil |
|--------|-------|
| Spec OpenAPI | Stoplight, Redocly CLI, Swagger Editor |
| Génération doc | Redoc (HTML) , Widdershins (Markdown) |
| Mock API | Prism, WireMock |
| Tests doc | Dredd (spec vs implémentation) |
| Portail développeur | ReadMe.io, Mintlify, Stoplight |

## Verification Checklist

- [ ] Tous les endpoints ont summary + description + codes de réponse
- [ ] Exemples de requête/réponse pour chaque endpoint
- [ ] Schémas documentés (type, format, nullable, exemple, description)
- [ ] Codes d'erreur (400, 401, 403, 404, 409, 422, 429, 500) explicitement listés
- [ ] Guide quickstart testé bout en bout
- [ ] Changelog à jour avec version sémantique
- [ ] Liens valides, pas de fragments brisés
- [ ] Spec OpenAPI valide (lint avec `redocly lint`)