---
name: api-rest-best-practices
description: "Use when concevoir, implémenter, auditer ou documenter une API REST. Couvre la modélisation des ressources, les codes HTTP, la pagination, le filtrage, le tri, HATEOAS, la négociation de contenu, et les conventions d'URI."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, rest, http, web, architecture, backend]
    related_skills: [api-openapi-documentation, api-security, api-rate-limiting]
---

# API REST — Bonnes Pratiques

## Vue d'ensemble

REST (Representational State Transfer) est un style d'architecture défini par Roy Fielding (2000). Une API RESTful exploite le protocole HTTP comme couche d'application universelle, en utilisant ses méthodes, codes et en-têtes comme une interface standardisée. La clé est la **modélisation des ressources**, pas des actions.

## Quand l'utiliser

- Concevoir une nouvelle API web publique ou interne
- Auditer une API existante pour la conformité REST
- Implémenter un backend HTTP sans framework lourd (FastAPI, Express, Gin, ASP.NET Core)
- Documenter des endpoints REST pour une équipe

Ne pas utiliser pour : des systèmes temps réel (préférer WebSocket), des requêtes complexes avec sélection de champs précis (préférer GraphQL), ou des communications internes haute performance (préférer gRPC).

## Principes Fondamentaux

### 1. Modélisation par Ressources

Les URI représentent des **noms** (ressources), pas des **verbes** (actions).

```
BON  : GET /utilisateurs/42
BON  : POST /commandes
MAUVAIS : GET /getUser?id=42
MAUVAIS : POST /createOrder
```

Structure canonique d'une URI REST :

| Composant | Convention | Exemple |
|-----------|------------|---------|
| Collection | `/ressources` | `/articles` |
| Élément | `/ressources/{id}` | `/articles/42` |
| Sous-collection | `/ressources/{id}/sous` | `/articles/42/comments` |
| Action | `/ressources/{id}/actions` | `/articles/42/publish` |

### 2. Codes de Statut HTTP

Utiliser les bons codes — chaque code a une sémantique précise.

**Succès (2xx) :**

| Code | Usage | Quand |
|------|-------|-------|
| 200 OK | GET, PUT, PATCH réussis | Requête traitée, corps présent |
| 201 Created | POST réussi | Ressource créée, en-tête `Location:` |
| 202 Accepted | Traitement asynchrone | Accepté, pas encore fait |
| 204 No Content | DELETE, PUT vides | Succès, pas de corps de réponse |

**Redirection (3xx) :**

| Code | Usage |
|------|-------|
| 301 Moved Permanently | Ressource déplacée définitivement |
| 302 Found | Redirection temporaire |
| 304 Not Modified | Cache validé (ETag/If-None-Match) |

**Erreur Client (4xx) :**

| Code | Usage |
|------|-------|
| 400 Bad Request | Payload invalide, validation échouée |
| 401 Unauthorized | Authentification manquante ou invalide |
| 403 Forbidden | Authentifié mais pas autorisé |
| 404 Not Found | Ressource inexistante |
| 405 Method Not Allowed | Méthode HTTP non supportée |
| 409 Conflict | Conflit d'état (versioning optimiste) |
| 422 Unprocessable Entity | Erreur sémantique (validation métier) |
| 429 Too Many Requests | Rate limiting dépassé |

**Erreur Serveur (5xx) :**

| Code | Usage |
|------|-------|
| 500 Internal Server Error | Erreur générique serveur |
| 502 Bad Gateway | Amont défaillant |
| 503 Service Unavailable | Maintenance / surcharge |

### 3. Méthodes HTTP et Sémantique

| Méthode | Collection | Élément | Idempotent | Safe |
|---------|------------|---------|------------|------|
| GET | Lister les ressources | Récupérer la ressource | Oui | Oui |
| POST | Créer une ressource | — (utiliser PUT/PATCH) | Non | Non |
| PUT | Remplacer la collection | Remplacer la ressource | Oui | Non |
| PATCH | — | Mise à jour partielle | Non* | Non |
| DELETE | Supprimer la collection | Supprimer la ressource | Oui | Non |

*PATCH peut être rendu idempotent si le document de patch est lui-même idempotent (JSON Patch RFC 6902).

### 4. Pagination, Filtrage, Tri

**Pagination :**

```
GET /articles?page=2&per_page=50
```

Réponse avec métadonnées :

```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "per_page": 50,
    "total": 1234,
    "total_pages": 25,
    "next": "/articles?page=3&per_page=50",
    "prev": "/articles?page=1&per_page=50"
  }
}
```

Alternative cursor-based (préférable pour les grands volumes) :

```
GET /articles?cursor=eyJpZCI6NDJ9&limit=50
```

**Filtrage :**

```
GET /articles?status=published&author_id=42
GET /articles?created_at[gte]=2026-01-01&created_at[lte]=2026-06-30
```

**Tri :**

```
GET /articles?sort=created_at&order=desc
GET /articles?sort=-created_at,title    # tri multiple, desc/asc
```

### 5. HATEOAS (Hypermedia as the Engine of Application State)

Les réponses contiennent des liens qui guident le client vers les actions possibles :

```json
{
  "id": 42,
  "title": "Article",
  "_links": {
    "self": { "href": "/articles/42" },
    "author": { "href": "/utilisateurs/7" },
    "comments": { "href": "/articles/42/comments" },
    "delete": { "href": "/articles/42", "method": "DELETE" }
  }
}
```

### 6. Négociation de Contenu

Utiliser les en-têtes `Accept` et `Content-Type` :

```
Accept: application/json
Accept: application/vnd.eva.v2+json    # versioning par media type
```

Réponse conditionnelle :

```
ETag: "33a64df551425fcc55e4d42a148795d9f25f89d4"
Last-Modified: Wed, 22 Jul 2026 12:00:00 GMT
```

### 7. Format de Réponse d'Erreur

Format standardisé (RFC 7807 Problem Details) :

```json
{
  "type": "https://api.eva.dev/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "Le champ 'email' est requis",
  "instance": "/articles",
  "errors": {
    "email": ["Ce champ est requis", "Format invalide"]
  }
}
```

### 8. Conventions d'URI

- **Pluriel** pour les collections : `/utilisateurs`, pas `/user`
- **kebab-case** : `/ordre-de-achat`, pas `/ordreDeAchat` ni `/ordre_de_achat`
- **Pas d'extensions** : `/articles/42`, pas `/articles/42.json`
- **Pas de verbes** : `/articles/42/publish`, pas `/articles/42/publishArticle`
- **Versioning** : préférer l'en-tête `Accept` ou le préfixe `/v1/`

## Implémentation Référence

### FastAPI (Python)

```python
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="EVA API", version="1.0.0")

class Article(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=200)
    content: str
    status: str = "draft"

    model_config = {"from_attributes": True}

@app.get("/articles", response_model=list[Article])
async def list_articles(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
):
    """Liste paginée des articles avec filtrage."""
    ...

@app.post("/articles", status_code=201)
async def create_article(article: Article):
    """Crée un article, retourne l'URI via Location."""
    ...
```

### Express (Node.js)

```javascript
const express = require('express');
const router = express.Router();

router.get('/articles', async (req, res) => {
  const { page = 1, per_page = 50, status } = req.query;
  // ...
  res.json({ data, pagination: { page, per_page, total } });
});

router.post('/articles', async (req, res) => {
  const article = await create(req.body);
  res.status(201).location(`/articles/${article.id}`).json(article);
});
```

## Pièges Courants

1. **Verbes dans l'URI** — ne pas écrire `/getUser` ou `/createOrder`. Utiliser GET /users/{id}, POST /orders.
2. **200 pour tout** — retourner le code exact (201 pour création, 204 pour suppression, etc.). Un client qui reçoit 200 sur un DELETE ne sait pas si c'est un succès ou un stub.
3. **Ignorer ETag/If-None-Match** — les clients ne peuvent pas faire de cache conditionnel, causant des transferts inutiles.
4. **Pas de pagination** — une collection de 100k+ éléments sans pagination tue le serveur et le client. Toujours paginer, même avec une valeur par défaut modeste.
5. **Nested resources trop profonds** — `/a/b/c/d/e` est illisible. Max 3 niveaux, puis utiliser des query params.
6. **Mélanger les versions** — ne pas avoir `/v1/users` et `/api/getUsers` dans la même API.
7. **Pas de rate limiting headers** — les clients ne peuvent pas s'adapter. Voir `api-rate-limiting`.
8. **PUT pour modification partielle** — PUT remplace TOUTE la ressource. Utiliser PATCH pour les mises à jour partielles.

## Checklist de Vérification

- [ ] URI = noms, pas verbes ; collections au pluriel
- [ ] Codes HTTP corrects pour chaque endpoint (201, 204, 4xx, 5xx)
- [ ] Pagination obligatoire sur les collections
- [ ] Filtrage et tri via query params standardisés
- [ ] Format d'erreur uniforme (RFC 7807)
- [ ] ETag et/ou Last-Modified sur les ressources
- [ ] En-têtes CORS configurés (`Access-Control-Allow-Origin`, etc.)
- [ ] Rate limiting implémenté avec en-têtes `Retry-After`, `X-RateLimit-*`
- [ ] Versioning choisi et documenté (URI ou Accept header)
- [ ] Documentation OpenAPI/Swagger générée et accessible
- [ ] Tests : au moins un test par code de statut attendu