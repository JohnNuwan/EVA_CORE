---
name: api-graphql
description: "Use when concevoir, implémenter ou auditer une API GraphQL. Couvre le schéma et les types, les resolvers, les mutations, les subscriptions, le DataLoader (N+1), l'authentification, la pagination (cursor-based), la fédération, et l'optimisation des performances."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, graphql, backend, schema, query, web]
    related_skills: [api-rest-best-practices, api-security, api-rate-limiting]
---

# API GraphQL

## Vue d'ensemble

GraphQL (spécification 2015, Facebook/Meta) est un langage de requête et un runtime côté serveur. Contrairement à REST où le serveur détermine la forme de la réponse, c'est le client qui spécifie exactement les données dont il a besoin via un seul endpoint (généralement `/graphql`). Cela élimine le sur-fetching et le sous-fetching, problèmes courants des APIs REST.

## Quand l'utiliser

- Applications avec des besoins de données complexes et variés (dashboards, apps mobiles)
- Produits où plusieurs clients (web, mobile, IoT) accèdent aux mêmes données avec des besoins différents
- Équipes qui veulent un contrat fort entre frontend et backend via le schéma
- Microservices qu'on veut agréger derrière une seule API (GraphQL Federation)

Ne pas utiliser pour : des APIs simples CRUD (REST est plus simple et plus idiomatique), des transferts de fichiers volumineux, des communications internes haute performance (gRPC est plus efficace), ou quand la simplicité prime sur la flexibilité.

## Concepts Fondamentaux

### 1. Schéma et Système de Types

Le schéma est le contrat. Il est écrit en **SDL** (Schema Definition Language) :

```graphql
type Query {
  articles(page: Int, perPage: Int): ArticleConnection!
  article(id: ID!): Article
  search(query: String!): [SearchResult!]!
}

type Mutation {
  createArticle(input: CreateArticleInput!): Article!
  updateArticle(id: ID!, input: UpdateArticleInput!): Article!
  deleteArticle(id: ID!): Boolean!
}

type Subscription {
  articleCreated: Article!
  articleUpdated(id: ID!): Article!
}

type Article {
  id: ID!
  title: String!
  content: String!
  status: ArticleStatus!
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

enum ArticleStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}

input CreateArticleInput {
  title: String!
  content: String!
  status: ArticleStatus = DRAFT
  authorId: ID!
}

type User {
  id: ID!
  name: String!
  email: String!
}

type Comment {
  id: ID!
  content: String!
  author: User!
}

interface SearchResult {
  id: ID!
  type: String!
  score: Float!
}

type ArticleResult implements SearchResult {
  id: ID!
  type: String!
  score: Float!
  title: String!
  excerpt: String!
}

union SearchResultUnion = Article | User | Comment
```

### 2. Resolvers

Chaque champ du schéma est résolu par une fonction (resolver) :

```python
# Ariadne / Strawberry (Python)
from ariadne import QueryType, MutationType

query = QueryType()

@query.field("article")
async def resolve_article(_, info, id: str):
    return await db.get_article(id)

@query.field("articles")
async def resolve_articles(_, info, page=1, perPage=50):
    items = await db.list_articles(page, perPage)
    total = await db.count_articles()
    return {
        "edges": [{"cursor": encode(a.id), "node": a} for a in items],
        "pageInfo": {
            "hasNextPage": total > page * perPage,
            "endCursor": encode(items[-1].id) if items else None,
        }
    }
```

```javascript
// Apollo Server (Node.js)
const resolvers = {
  Query: {
    articles: async (_, { page = 1, perPage = 50 }, { db }) => {
      const [items, total] = await Promise.all([
        db.articles.find().skip((page - 1) * perPage).limit(perPage),
        db.articles.countDocuments(),
      ]);
      return {
        edges: items.map(a => ({ cursor: encode(a.id), node: a })),
        pageInfo: { hasNextPage: total > page * perPage, endCursor: encode(items.at(-1)?.id) },
      };
    },
  },
  Article: {
    author: async (article, _, { loaders }) => loaders.userLoader.load(article.authorId),
  },
};
```

### 3. Problème N+1 et DataLoader

Le problème classique de GraphQL : une requête qui liste 50 articles et demande l'auteur pour chacun génère 1 + 50 requêtes SQL.

**Solution : DataLoader** (batching + caching par requête) :

```javascript
const DataLoader = require('dataloader');

const userLoader = new DataLoader(async (ids) => {
  const users = await db.users.find({ _id: { $in: ids } }).toArray();
  const map = new Map(users.map(u => [u._id.toString(), u]));
  return ids.map(id => map.get(id.toString()) || null);
});
```

### 4. Pagination (Cursor-Based)

La norme **Relay Connection** (paginations basées sur curseur, pas de pages numériques) :

```graphql
type ArticleConnection {
  edges: [ArticleEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type ArticleEdge {
  cursor: String!
  node: Article!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

Requête :

```graphql
query {
  articles(first: 10, after: "Y3Vyc29yOjQy") {
    edges { cursor, node { id, title } }
    pageInfo { hasNextPage, endCursor }
  }
}
```

### 5. Authentification et Autorisation

**Au niveau du resolver :**

```javascript
const resolvers = {
  Query: {
    account: async (_, __, { user }) => {
      if (!user) throw new AuthenticationError('Non authentifié');
      return user;
    },
  },
  Article: {
    __resolveReference: (article, { user }) => {
      // Autorisation par champ
      if (article.status === 'DRAFT' && article.authorId !== user?.id) {
        return null; // ou throw ForbiddenError
      }
      return article;
    },
  },
};
```

**Directives d'autorisation (schéma) :**

```graphql
directive @auth(requires: Role = ADMIN) on OBJECT | FIELD_DEFINITION

type Query {
  adminPanel: AdminData @auth(requires: ADMIN)
}
```

### 6. Fédération (Apollo Federation)

Pour unifier plusieurs microservices en un seul graphe :

```graphql
# Service Utilisateurs
extend type Query {
  me: User
}

type User @key(fields: "id") {
  id: ID! @external
  name: String!
}

# Service Articles
type Article @key(fields: "id") {
  id: ID!
  title: String!
  author: User!
}

extend type User @key(fields: "id") {
  id: ID! @external
  articles: [Article!]!
}
```

### 7. Subscriptions (WebSocket)

Notifications temps réel via le protocole graphql-ws :

```graphql
subscription {
  articleCreated {
    id
    title
    author { name }
  }
}
```

## Implémentation Référence

### FastAPI + Strawberry (Python)

```python
import strawberry
from strawberry.types import Info

@strawberry.type
class Article:
    id: strawberry.ID
    title: str
    content: str
    author: 'User'

    @strawberry.field
    async def comments(self, info: Info) -> list['Comment']:
        return await info.context['loaders'].comment_loader.load(self.id)

@strawberry.type
class Query:
    @strawberry.field
    async def article(self, id: strawberry.ID) -> Article | None:
        return await db.get_article(id)

schema = strawberry.Schema(query=Query)

# Dans FastAPI
from strawberry.fastapi import GraphQLRouter
router = GraphQLRouter(schema, context_getter=get_context)
app.include_router(router, prefix="/graphql")
```

### Apollo Server (Node.js)

```javascript
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  csrfPrevention: true,
  introspection: process.env.NODE_ENV === 'development',
});

await server.start();
app.use('/graphql', expressMiddleware(server, {
  context: async ({ req }) => ({ user: await authenticate(req), loaders: createLoaders() }),
}));
```

## Pièges Courants

1. **N+1 Query** — ne pas oublier DataLoader. Sans batching, une requête innocente peut générer des centaines de requêtes SQL.
2. **Introspection en production** — désactiver l'introspection en production si l'API n'est pas publique. Sinon, l'attaquant a le schéma complet.
3. **Depth limiting** — une requête récursive `{ user { posts { author { posts { author ... } } } } }` peut planter le serveur. Toujours limiter la profondeur (max 8-10 niveaux).
4. **Pas de pagination** — les clients peuvent demander 10000 articles d'un coup. Forcer `first`/`last` avec un maximum.
5. **Resolvers bloquants** — chaque resolver doit être asynchrone. Un resolver qui bloque sur I/O ralentit tout le pipeline.
6. **Mutations non-idempotentes** — contrairement à REST, GraphQL ne définit pas l'idempotence. Le client doit gérer les retries de son côté.
7. **Pas de rate limiting par champ** — un client peut coûteusement interroger un champ lent. Envisager un cost analysis.
8. **Schéma instable** — ajouter des champs, ne jamais en supprimer sans dépréciation. Utiliser `@deprecated(reason: "use X")`.

## Checklist de Vérification

- [ ] Schéma SDL complet : Query, Mutation, Subscription (si nécessaire)
- [ ] DataLoader installé pour tous les champs relationnels (N+1 éliminé)
- [ ] Pagination cursor-based sur toutes les listes
- [ ] `max_depth` configuré (sécurité)
- [ ] `max_complexity` ou `cost analysis` configuré
- [ ] Authentification + autorisation implémentées via directives ou resolvers
- [ ] Introspection désactivée en production (sauf API publique)
- [ ] Subscriptions via WebSocket configurées si besoin
- [ ] Tests : chaque query et mutation, cas d'erreur, authorization
- [ ] Fédération documentée si multi-services