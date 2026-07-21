---
name: api-rest
description: "Guide complet des API REST : principes RESTful, design endpoints, versioning, pagination, HATEOAS, sécurité, documentation OpenAPI, testing."
tags: [rest, api, http, openapi, swagger, endpoints, versioning, pagination, hateoas, sécurité, testing]
---

# API REST — Conception et Implémentation

## Principes REST (Fielding, 2000)
1. **Client-Server** — séparation UI/données
2. **Stateless** — chaque requête contient toutes les infos nécessaires
3. **Cacheable** — réponses explicitement cacheables (Cache-Control, ETag)
4. **Uniform Interface** — ressources, manipulations via représentations, HATEOAS
5. **Layered System** — proxies, load balancers, caches
6. **Code on Demand** (optionnel)

## Conception d'Endpoints

### Nommage
```
GET    /users              → Liste
POST   /users              → Créer
GET    /users/{id}         → Un élément
PUT    /users/{id}         → Remplacer
PATCH  /users/{id}         → Modifier partiellement
DELETE /users/{id}         → Supprimer
GET    /users/{id}/orders  → Relation
```

### Conventions
- **Noms au pluriel** : `/users` pas `/user`
- **kebab-case** : `/order-items`
- **Pas de verbes** : pas de `/getUsers`
- **Versioning** : `/v1/users` ou header `Accept: application/vnd.api.v1+json`

## Statuts HTTP

| Code | Usage |
|------|-------|
| 200 OK | GET, PUT, PATCH réussis |
| 201 Created | POST (inclure Location header) |
| 204 No Content | DELETE réussi |
| 400 Bad Request | Validation échouée |
| 401 Unauthorized | Auth manquante |
| 403 Forbidden | Pas autorisé |
| 404 Not Found | Ressource inexistante |
| 409 Conflict | Conflit (doublon) |
| 422 Unprocessable | Validation métier |
| 429 Too Many | Rate limiting |
| 500 Server Error | Erreur générique |

## Corps de Réponse

### Succès
```json
{
  "data": { "id": "42", "type": "users", "attributes": { "name": "Alice" } },
  "meta": { "requestId": "req-abc-123" }
}
```

### Erreur
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Le champ email est invalide",
    "details": [{ "field": "email", "rule": "format", "value": "invalid" }]
  }
}
```

## Pagination

### Cursor-based (recommandé)
```
GET /users?cursor=eyJpZCI6NDJ9&limit=20
→ { "data": [...], "meta": { "nextCursor": "eyJpZCI6NzN9", "hasMore": true } }
```

### Offset-based
```
GET /users?page=2&per_page=20
→ { "data": [...], "meta": { "page": 2, "perPage": 20, "total": 150 } }
```

## HATEOAS
```json
{
  "data": { "id": "42", "name": "Alice" },
  "links": {
    "self": "/users/42",
    "orders": "/users/42/orders",
    "update": { "href": "/users/42", "method": "PATCH" }
  }
}
```

## Sécurité
- **Bearer Token** — `Authorization: Bearer <jwt>`
- **API Key** — `X-API-Key: <key>`
- **OAuth 2.0** — Authorization Code + PKCE
- **Rate Limiting** — headers `X-RateLimit-*`
- **CORS** — `Access-Control-Allow-Origin`

## Documentation OpenAPI 3.1
```yaml
openapi: 3.1.0
info:
  title: Users API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Liste des utilisateurs
      responses:
        '200':
          description: Succès
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
```

## Testing
- **Contrat** — Pact (fournisseur/consommateur)
- **Intégration** — Supertest + Jest/Vitest
- **E2E** — Postman, Bruno, Hoppscotch

## Frameworks par Langage
| Langage | Framework |
|---------|-----------|
| Node.js | Express, Fastify, Hono, NestJS |
| Python | FastAPI, Django REST Framework |
| Go | Gin, Echo, Chi |
| Rust | Axum, Actix-web |
| Java | Spring Boot, Quarkus |
| .NET | ASP.NET Core Minimal API |

## Pièges Courants
- **Nested trop profonds** — préférer des ressources plates
- **Pas de pagination** — toujours paginer les listes
- **PUT vs PATCH** — PUT = remplacement, PATCH = partiel
- **Sérialisation circulaire** — gérer les références ORM

## Références
- [RESTful API](https://restfulapi.net)
- [OpenAPI 3.1](https://spec.openapis.org/oas/v3.1.0)
- [JSON:API](https://jsonapi.org)
- [Microsoft REST Guidelines](https://github.com/microsoft/api-guidelines)
- [Pact](https://pact.io)
- [Bruno](https://www.usebruno.com)