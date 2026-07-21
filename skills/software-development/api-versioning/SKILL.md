---
name: api-versioning
description: "Use when planifier, implémenter ou migrer le versioning d'une API. Couvre URI versioning, Accept header, query param, contract-first, calendric versioning, deprecation policy, backward compatibility, breaking changes, et migration strategies."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, versioning, rest, graphql, backward-compatibility, architecture]
    related_skills: [api-rest-best-practices, api-openapi-documentation, api-security]
---

# API Versioning

## Vue d'ensemble

Le versioning d'API est la stratégie permettant de faire évoluer une API sans casser les clients existants. Il n'existe pas de solution universelle — chaque approche a des compromis entre simplicité, maintenabilité et expérience développeur. L'objectif est de permettre l'ajout de fonctionnalités et la correction de bugs tout en garantissant que les clients non mis à jour continuent de fonctionner.

## Quand l'utiliser

- Dès qu'une API est publique et utilisée par des clients tiers
- Quand plusieurs versions d'un client coexistent (mobile, web, IoT)
- Avant de déployer un breaking change (changement de champ, suppression d'endpoint)
- Lors de la planification d'une API (choisir la stratégie dès le début)

Ne pas utiliser pour : des APIs internes mono-client (préférer l'évolution continue), des prototypes, ou quand le coût du versioning dépasse l'impact des breaking changes.

## Stratégies de Versioning

### 1. URI Path Versioning (`/v1/`, `/v2/`)

La plus courante et la plus simple :

```
GET /v1/articles
GET /v2/articles
GET /v1.2/articles
```

**Avantages :** Simple, évident, facile à router (nginx, API gateway), facile à cacher.

**Inconvénients :** Encombre les URI, encourage le copy-paste du code, pas de granularité fine.

```python
from fastapi import APIRouter

v1 = APIRouter(prefix="/v1")
v2 = APIRouter(prefix="/v2")

@v1.get("/articles")
async def list_articles_v1(skip: int = 0, limit: int = 50):
    # Version 1 : pagination offset-based
    ...

@v2.get("/articles")
async def list_articles_v2(cursor: str = None, limit: int = 50):
    # Version 2 : pagination cursor-based
    ...
```

### 2. Header Versioning (`Accept: application/vnd.api.v2+json`)

Le versioning est dans l'en-tête de négociation de contenu :

```
Accept: application/vnd.eva.v1+json
Accept: application/vnd.eva.v2+json
Accept: application/vnd.eva.article+json; version=2
```

**Avantages :** URI propres, RESTful (le versioning est un aspect de la négociation de contenu), granularité par ressource possible.

**Inconvénients :** Moins visible, plus difficile à tester dans un navigateur, nécessite une logique de routage personnalisée.

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.get("/articles")
async def list_articles(request: Request):
    accept = request.headers.get("accept", "")
    version = 1
    if "application/vnd.eva.v2+json" in accept:
        version = 2
    # ...
```

### 3. Query Parameter Versioning (`?version=2`)

```
GET /articles?version=1
GET /articles?version=2
```

**Avantages :** Simple à implémenter, visible dans les logs, facile à tester.

**Inconvénients :** Encombre les query strings, un client peut oublier de le passer, pas standardisé.

### 4. Content Negotiation (Media Type)

```
GET /articles
Accept: application/vnd.eva.article.v2+json
```

**Avantages :** RESTful pur, peut être combiné avec le versioning de représentation (JSON vs XML).

**Inconvénients :** Complexe à configurer côté serveur.

### 5. CalVer (Calendric Versioning)

Pas de numéro de version, mais des dates :

```
# api.eva.dev/2025-01-01/articles
# api.eva.dev/2025-06-15/articles
```

**Avantages :** Clarté sur la date de changement, bon pour des APIs qui changent fréquemment.

**Inconvénients :** Lourd à maintenir, pas de mapping clair entre versions.

## Compatibilité et Breaking Changes

### Changements Non-Breaking (peuvent être déployés sans version)

- Ajouter un champ optionnel dans une réponse
- Ajouter un endpoint
- Ajouter un paramètre optionnel à un endpoint existant
- Étendre une enum (si le client gère les valeurs inconnues)
- Réduire le taux d'erreur (améliorer la robustesse)
- Ajouter des en-têtes de réponse optionnels

### Breaking Changes (nécessitent une nouvelle version)

- Supprimer ou renommer un champ
- Changer le type d'un champ (string → int, int → float)
- Rendre un champ optionnel → requis
- Supprimer un endpoint
- Changer le format de date (ISO 8601 → timestamp)
- Réduire les garanties de performance
- Changer le comportement d'un endpoint (ce qu'il retourne)
- Modifier le format d'erreur
- Supprimer des en-têtes de réponse existants

### Règle des 3 Points de Vue

Avant un changement, évaluer :

1. **Stockage** : les données changent-elles ?
2. **Sérialisation** : le format wire change-t-il ?
3. **Sémantique** : le comportement change-t-il ?

Si un seul des trois change et que le client peut le détecter, ce n'est pas un breaking change. Si les trois changent, c'est un breaking change.

## Politique de Dépréciation

### Cycle de Vie d'une Version

```python
# 1. Annoncer la dépréciation (en-tête de réponse)
Deprecation: true
Sunset: Sat, 01 Jan 2027 00:00:00 GMT
Link: </v2/articles>; rel="successor-version"

# 2. Période de transition (minimum 6 mois pour les APIs publiques)
# 3. Arrêt (Sunset)
```

**Bonnes pratiques :**

```python
class DeprecationMiddleware:
    def __init__(self, sunset_dates: dict[str, str]):
        self.sunset = sunset_dates  # {"v1": "2027-01-01", "v2": "2028-06-01"}

    async def __call__(self, request: Request, call_next):
        version = extract_version(request)
        if version and version in self.sunset:
            response = await call_next(request)
            response.headers["Deprecation"] = "true"
            response.headers["Sunset"] = self.sunset[version]
            response.headers["Link"] = f'</v{int(version[1:])+1}/>; rel="successor-version"'
            return response
        return await call_next(request)
```

### Documentation de Dépréciation

```yaml
# openapi.yaml
paths:
  /v1/articles:
    get:
      deprecated: true
      x-sunset: "2027-01-01"
      x-migration: "/v2/articles"
      description: "DÉPRÉCIÉ — Utiliser /v2/articles. Migration: ..."
```

## Stratégies de Migration

### 1. Coexistence (la plus simple)

Deux versions tournent simultanément :

```nginx
location /api/ {
  if ($request_uri ~ "^/v1/") {
    proxy_pass http://backend-v1;
  }
  if ($request_uri ~ "^/v2/") {
    proxy_pass http://backend-v2;
  }
}
```

### 2. Adapter/Transformer (une seule backend, plusieurs versions)

```python
class ArticleTransformer:
    @staticmethod
    def to_v1(article: dict) -> dict:
        return {
            "id": article["id"],
            "title": article["title"],
            "author": article["author_name"],  # v1 : un seul champ
        }

    @staticmethod
    def to_v2(article: dict) -> dict:
        return {
            "id": article["id"],
            "title": article["title"],
            "author": {
                "id": article["author_id"],
                "name": article["author_name"],
            },  # v2 : objet imbriqué
        }
```

### 3. Compatibilité Prospect (evolve the contract)

La nouvelle version est un **sur-ensemble** de l'ancienne : les clients anciens ignorent les nouveaux champs, les clients nouveaux exploitent les nouveaux champs.

```json
// Version 1
{"id": 1, "title": "Article"}

// Version 2 (compatible, ajout de champs)
{"id": 1, "title": "Article", "tags": ["tech"], "views": 150}
```

## Versioning en GraphQL

GraphQL gère le versioning différemment — pas de versioning d'API, mais **évolution du schéma** :

- Ajouter des champs et types : toujours safe
- Déprécier des champs avec `@deprecated`
- Ne jamais supprimer un champ sans dépréciation préalable

```graphql
type Article {
  id: ID!
  title: String!
  content: String!
  author: String! @deprecated(reason: "Utiliser 'authors' à la place")
  authors: [Author!]!
}
```

## Versioning en gRPC

Avec Protocol Buffers, le versioning est géré par les règles de compatibilité protobuf :

- Ne jamais réutiliser un numéro de champ (`reserved`)
- Ne jamais changer le type d'un champ existant
- Ajouter des champs : toujours safe (les clients anciens ignorent les champs inconnus)
- Supprimer des champs : utiliser `reserved`
- Utiliser des enums avec `UNSPECIFIED = 0` par défaut

## Pièges Courants

1. **Pas de date de sunset** — une version v1 qui reste ad vitam aeternam devient un legacy sans fin. Toujours documenter une date de fin.
2. **Versioning par défaut implicite** — si le client ne spécifie pas de version, quelle version reçoit-il ? Toujours définir un comportement (dernière version, ou version la plus stable).
3. **Trop de versions simultanées** — maintenir v1, v2, v3, v4 en parallèle multiplie la complexité. Max 2-3 versions actives.
4. **Breaking change sans notification** — les clients découvrent le changement à la prochaine requête. Envoyer un email, un blog post, et les en-têtes `Deprecation`/`Sunset`.
5. **Copy-paste entre versions** — v1 et v2 sont des copies presque identiques. Utiliser des transformers ou des paramètres de compatibilité.
6. **Pas de stratégie de migration** — `/v1/` → `/v2/` sans guide. Fournir un guide de migration détaillé.
7. **Versioning sur des APIs internes** — si le client est le même, l'évolution continue sans versioning est plus efficace.

## Checklist de Vérification

- [ ] Stratégie de versioning choisie et documentée (URI/Header/Query)
- [ ] Politique de dépréciation définie (durée de vie, sunset)
- [ ] En-têtes `Deprecation` et `Sunset` implémentés
- [ ] Version par défaut configurée pour les clients sans version
- [ ] Breaking changes identifiés (champs, types, sémantique)
- [ ] Guide de migration écrit pour chaque version
- [ ] Tests : clients v1 continuent de fonctionner après déploiement v2
- [ ] Nombre de versions actives limité (≤ 3)
- [ ] Documentation OpenAPI mise à jour pour chaque version