---
name: api-openapi-documentation
description: "Use when concevoir, rédiger, valider ou générer la documentation d'une API REST via OpenAPI/Swagger. Couvre l'OpenAPI Specification 3.1, la structure du fichier, les paths, schemas, paramètres, réponses, security schemes, code generation, et les outils de validation (Spectral, Redocly, Swagger UI)."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, openapi, swagger, documentation, specification, rest, backend]
    related_skills: [api-rest-best-practices, api-versioning, api-security]
---

# Documentation OpenAPI

## Vue d'ensemble

OpenAPI (anciennement Swagger) est la spécification standard (ISO) pour décrire les APIs REST. Un fichier OpenAPI (YAML ou JSON) est à la fois la **documentation** et le **contrat** de l'API — il peut être utilisé pour générer des clients, des serveurs, des tests, et de la documentation interactive. La version actuelle est OpenAPI 3.1.0 (alignée sur JSON Schema Draft 2020-12).

## Quand l'utiliser

- Dès qu'une API REST est publique ou utilisée par des clients externes
- Pour générer automatiquement des clients SDK (Python, TypeScript, Go, etc.)
- Pour valider les requêtes/réponses côté serveur
- Pour alimenter une documentation interactive (Swagger UI, Redoc, Stoplight)
- Pour tester une API (Postman, Insomnia importent OpenAPI)
- Pour CI/CD : valider que l'API ne fait pas de breaking changes

Ne pas utiliser pour : des APIs GraphQL (schéma intégré), gRPC (protobuf est l'IDL), ou des APIs purement internes sans client externe.

## Structure du Fichier OpenAPI

### Structure Racine

```yaml
openapi: "3.1.0"
info:
  title: "EVA API"
  description: "API REST de l'assistant EVA — gestion des articles, utilisateurs, et commentaires."
  version: "2.0.0"
  contact:
    name: "Équipe EVA"
    url: "https://eva.dev/support"
    email: "api@eva.dev"
  license:
    name: "MIT"
    url: "https://opensource.org/licenses/MIT"

servers:
  - url: "https://api.eva.dev/v2"
    description: "Production"
  - url: "https://staging.api.eva.dev/v2"
    description: "Staging"

tags:
  - name: "Articles"
    description: "Gestion des articles de blog"
    externalDocs:
      url: "https://docs.eva.dev/articles"
  - name: "Utilisateurs"
    description: "Gestion des comptes utilisateurs"

externalDocs:
  description: "Documentation complète"
  url: "https://docs.eva.dev"
```

### Paths et Opérations

```yaml
paths:
  /articles:
    get:
      tags: [Articles]
      summary: "Liste paginée des articles"
      description: "Retourne une liste paginée d'articles avec filtrage optionnel par statut."
      operationId: listArticles
      parameters:
        - name: page
          in: query
          description: "Numéro de page (défaut: 1)"
          schema:
            type: integer
            minimum: 1
            default: 1
        - name: per_page
          in: query
          description: "Nombre d'éléments par page (max: 100)"
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 50
        - name: status
          in: query
          description: "Filtrer par statut"
          schema:
            $ref: "#/components/schemas/ArticleStatus"
      responses:
        "200":
          description: "Liste paginée"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/PaginatedArticles"
        "401":
          $ref: "#/components/responses/Unauthorized"
        "429":
          $ref: "#/components/responses/TooManyRequests"
      security:
        - bearerAuth: []

    post:
      tags: [Articles]
      summary: "Créer un article"
      operationId: createArticle
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: "#/components/schemas/CreateArticleInput"
      responses:
        "201":
          description: "Article créé"
          headers:
            Location:
              schema:
                type: string
                format: uri
              description: "URI du nouvel article"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Article"
      security:
        - bearerAuth: []

  /articles/{articleId}:
    get:
      tags: [Articles]
      summary: "Récupérer un article"
      operationId: getArticle
      parameters:
        - name: articleId
          in: path
          required: true
          schema:
            type: integer
      responses:
        "200":
          description: "Article trouvé"
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Article"
        "404":
          $ref: "#/components/responses/NotFound"
```

### Schemas (Composants)

```yaml
components:
  schemas:
    Article:
      type: object
      description: "Article de blog"
      required: [id, title, content, status, author_id, created_at]
      properties:
        id:
          type: integer
          description: "Identifiant unique"
          example: 42
        title:
          type: string
          description: "Titre de l'article"
          maxLength: 200
          example: "Introduction à OpenAPI"
        content:
          type: string
          description: "Contenu Markdown"
          example: "# OpenAPI\n\nOpenAPI est une spécification..."
        status:
          $ref: "#/components/schemas/ArticleStatus"
        author_id:
          type: integer
          description: "ID de l'auteur"
        tags:
          type: array
          items:
            type: string
          description: "Tags de l'article"
          example: ["api", "documentation"]
        created_at:
          type: string
          format: date-time
          example: "2026-07-22T12:00:00Z"
        updated_at:
          type: string
          format: date-time
          nullable: true
          example: "2026-07-22T14:30:00Z"

    PaginatedArticles:
      type: object
      required: [data, pagination]
      properties:
        data:
          type: array
          items:
            $ref: "#/components/schemas/Article"
        pagination:
          $ref: "#/components/schemas/Pagination"

    Pagination:
      type: object
      properties:
        page:
          type: integer
        per_page:
          type: integer
        total:
          type: integer
        total_pages:
          type: integer
        next:
          type: string
          format: uri
          nullable: true
        prev:
          type: string
          format: uri
          nullable: true

    ArticleStatus:
      type: string
      description: "Statut de l'article"
      enum: [draft, published, archived]

    CreateArticleInput:
      type: object
      required: [title, content, author_id]
      properties:
        title:
          type: string
          maxLength: 200
        content:
          type: string
        status:
          $ref: "#/components/schemas/ArticleStatus"
          default: draft
        author_id:
          type: integer

    Error:
      type: object
      description: "Erreur standard (RFC 7807)"
      properties:
        type:
          type: string
          format: uri
        title:
          type: string
        status:
          type: integer
        detail:
          type: string
        instance:
          type: string

  responses:
    NotFound:
      description: "Ressource introuvable"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    Unauthorized:
      description: "Non authentifié"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
    TooManyRequests:
      description: "Rate limit dépassé"
      content:
        application/json:
          schema:
            $ref: "#/components/schemas/Error"
      headers:
        Retry-After:
          schema:
            type: integer
        X-RateLimit-Remaining:
          schema:
            type: integer

  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "Token JWT d'authentification"
    apiKey:
      type: apiKey
      in: header
      name: X-API-Key
      description: "Clé API pour les services internes"
```

## Génération de Code

### Python (FastAPI — génération automatique)

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="EVA API",
    version="2.0.0",
    description="API REST de l'assistant EVA",
    docs_url="/docs",       # Swagger UI
    redoc_url="/redoc",     # Redoc
    openapi_url="/openapi.json",
)

class Article(BaseModel):
    id: int
    title: str
    # ... FastAPI génère le schéma OpenAPI automatiquement
```

### Génération de Client SDK

```bash
# openapi-generator (Java)
openapi-generator generate -i openapi.yaml -g python -o gen/client-python
openapi-generator generate -i openapi.yaml -g typescript-axios -o gen/client-ts
openapi-generator generate -i openapi.yaml -g go -o gen/client-go

# Option alternative : orval (TypeScript)
npx orval --input openapi.yaml --output ./src/api
```

## Validation et Linting

### Spectral (linting OpenAPI)

```bash
# Installation
npm install -g @stoplight/spectral-cli

# Lint
spectral lint openapi.yaml

# Règles personnalisées (.spectral.yaml)
extends: spectral:oas
rules:
  operation-description: error
  operation-operationId: error
  path-params: error
  my-custom-rule:
    description: "Tous les endpoints doivent avoir un tag"
    given: $.paths[*][*]
    then:
      field: tags
      function: truthy
```

### Redocly CLI

```bash
# Installation
npm install -g @redocly/cli

# Lint
redocly lint openapi.yaml

# Bundle (fusionner les $refs en un seul fichier)
redocly bundle openapi.yaml -o bundled.yaml

# Preview
redocly preview-docs openapi.yaml
```

### Diffing (détection de breaking changes)

```bash
# Vérifier qu'une nouvelle version ne casse pas l'ancienne
openapi-diff old.yaml new.yaml

# Avec Redocly
redocly lint openapi-v2.yaml --compare-with openapi-v1.yaml
```

## Intégration CI/CD

```yaml
# .github/workflows/api-lint.yml
name: API Lint
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm install -g @redocly/cli
      - run: redocly lint openapi.yaml
      - name: Check breaking changes
        run: |
          redocly lint openapi.yaml \
            --compare-with openapi-main.yaml \
            --format stylish
```

## Implémentation Référence

### FastAPI (auto-documentation)

FastAPI expose automatiquement `/docs` (Swagger UI), `/redoc` (Redoc), et `/openapi.json` (fichier OpenAPI brut).

```python
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI(
    title="EVA API",
    description="API REST documentée via OpenAPI",
    version="2.0.0",
    contact={"name": "Équipe EVA", "email": "api@eva.dev"},
    license_info={"name": "MIT", "identifier": "MIT"},
    servers=[{"url": "https://api.eva.dev/v2", "description": "Production"}],
)

class ArticleOut(BaseModel):
    id: int = Field(..., description="Identifiant unique")
    title: str = Field(..., max_length=200, description="Titre")
    model_config = {"json_schema_extra": {"example": {"id": 1, "title": "Article test"}}}

class PaginatedResponse(BaseModel):
    data: List[ArticleOut]
    pagination: dict

@app.get(
    "/articles",
    response_model=PaginatedResponse,
    summary="Liste paginée des articles",
    description="Retourne une liste paginée avec filtrage optionnel.",
    tags=["Articles"],
    responses={
        401: {"description": "Non authentifié"},
        429: {"description": "Trop de requêtes"},
    },
)
async def list_articles(
    page: int = Query(1, ge=1, description="Numéro de page"),
    per_page: int = Query(50, ge=1, le=100, description="Éléments par page"),
    status: Optional[str] = Query(None, description="Filtrer par statut"),
):
    """Endpoint listant les articles avec pagination."""
    ...
```

## Pièges Courants

1. **Description vide** — chaque endpoint doit avoir `summary` et `description`. Sans ça, la documentation générée est vide.
2. **Pas de `operationId`** — la génération de client SDK en dépend. Sans lui, les noms de fonctions sont aléatoires.
3. **Schemas trop génériques** — `type: object` sans `properties` ne sert à rien. Toujours définir la structure exacte.
4. **Oublier les codes d'erreur** — 200 et 201 ne suffisent pas. Documenter 400, 401, 403, 404, 422, 429, 500.
5. **Pas d'exemples** — `example:` ou `examples:` sur chaque champ et chaque requête améliorent considérablement l'expérience.
6. **Fichier trop gros** — un seul fichier OpenAPI de 10k+ lignes est illisible. Utiliser `$ref` pour morceler.
7. **Breaking changes non détectés** — intégrer un diff OpenAPI dans la CI pour détecter les changements cassants.
8. **Sécurité exposée** — ne pas documenter les endpoints internes d'administration dans le fichier public.

## Checklist de Vérification

- [ ] Fichier OpenAPI valide (`redocly lint` ou `spectral lint`)
- [ ] `info.title`, `info.version`, `info.description` renseignés
- [ ] `servers` configurés (prod, staging)
- [ ] Tous les endpoints ont `summary`, `operationId`, `tags`
- [ ] Tous les paramètres ont `description` et `schema` avec `example`
- [ ] Tous les codes de réponse documentés (succès + erreurs)
- [ ] `components/responses` utilisés pour les réponses réutilisables
- [ ] `components/securitySchemes` défini (bearer, API key, OAuth2)
- [ ] `security` appliqué aux endpoints qui le nécessitent
- [ ] Exemples fournis pour chaque schéma (`example:` ou `examples:`)
- [ ] Validation en CI (lint + diff des breaking changes)
- [ ] Documentation générée accessible (Swagger UI, Redoc)