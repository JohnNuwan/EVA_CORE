---
name: graphql
description: "Guide complet GraphQL : schéma, resolvers, mutations, subscriptions, Apollo, Relay, caching, pagination, sécurité, optimisation."
tags: [graphql, schema, resolver, mutation, subscription, apollo, relay, caching, pagination, dataloader, security]
---

# GraphQL — Langage de Requête API

## Architecture
GraphQL est un **langage de requête** pour API (Meta, 2012). Le client spécifie exactement les données dont il a besoin.

```graphql
query {
  user(id: "42") { name email posts(first: 5) { title } }
}
```

### vs REST
| Aspect | REST | GraphQL |
|--------|------|---------|
| Endpoints | Multiples (`/users`, `/users/42/posts`) | Un seul (`/graphql`) |
| Données | Fixed (over/under-fetching) | À la demande |
| Versioning | URL/Header | Évolution du schéma |
| Cache | HTTP natif | Couche dédiée |

## SDL (Schema Definition Language)
```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Query {
  user(id: ID!): User
  users(page: Int, limit: Int): [User!]!
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  deleteUser(id: ID!): Boolean!
}

type Subscription {
  userCreated: User!
}
```

### Types Scalaires
`ID`, `String`, `Int`, `Float`, `Boolean` — plus `DateTime`, `JSON`, `URL` via lib

### Input Types / Interfaces / Unions
```graphql
input CreateUserInput { name: String!; email: String! }
interface SearchResult { id: ID!; title: String! }
union Media = Image | Video | Audio
```

## Resolvers
```ts
const resolvers = {
  Query: { user: (_, { id }, { db }) => db.users.findUnique({ where: { id } }) },
  User: { posts: (parent, _, { db }) => db.posts.findMany({ where: { authorId: parent.id } }) },
  Mutation: { createUser: (_, { input }, { db }) => db.users.create({ data: input }) },
};
```

### Context
```ts
const server = new ApolloServer({
  typeDefs, resolvers,
  context: ({ req }) => ({ auth: await authenticate(req), db: prisma, dataloader: createLoaders() }),
});
```

## DataLoader — N+1 Problem
```ts
const userLoader = new DataLoader(async (ids) => {
  const users = await db.users.findMany({ where: { id: { in: ids } } });
  return ids.map(id => users.find(u => u.id === id) || null);
});
```

## Pagination (Relay Connection)
```graphql
type Query { users(first: Int, after: String): UserConnection! }
type UserConnection { edges: [UserEdge!]!; pageInfo: PageInfo! }
type PageInfo { hasNextPage: Boolean!; endCursor: String }
```

## Subscriptions (WebSocket)
```graphql
type Subscription { postUpdated(postId: ID!): Post! }
```
```ts
Subscription: { postUpdated: { subscribe: () => pubsub.asyncIterator(['POST_UPDATED']) } }
```

## Sécurité
- **Depth Limiting** — `depthLimit(5)` (empêche requêtes trop profondes)
- **Query Cost Analysis** — limiter le coût total des requêtes
- **Auth par champ** — vérifier les droits dans chaque resolver
- **Persisted Queries** — seules les requêtes pré-enregistrées acceptées
- **Introspection** — désactiver en production

## Caching (Apollo Client)
```ts
const cache = new InMemoryCache({
  typePolicies: {
    User: { keyFields: ['id'] },
    Query: { fields: { users: { merge: (_, i) => i } } },
  },
});
```

## Outils
| Outil | Usage |
|-------|-------|
| Apollo Studio | IDE, monitoring, tracing |
| GraphQL Codegen | Types TS depuis le schéma |
| Hasura | Auto-GraphQL sur PostgreSQL |
| Yoga | Serveur cross-platform |
| Pothos | Builder type-safe |

## Pièges Courants
- **N+1** — toujours DataLoader pour les relations
- **Requêtes trop profondes** — depth limit obligatoire
- **Subscriptions sans cleanup** — fermer les WebSocket
- **Schéma exposé** — désactiver l'introspection en production

## Références
- [GraphQL Spec](https://spec.graphql.org)
- [Apollo Server](https://www.apollographql.com/docs/apollo-server)
- [Relay](https://relay.dev)
- [GraphQL Codegen](https://the-guild.dev/graphql/codegen)
- [Hasura](https://hasura.io)
- [How to GraphQL](https://www.howtographql.com)