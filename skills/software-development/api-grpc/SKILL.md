---
name: api-grpc
description: "Use when concevoir, implémenter ou auditer une API gRPC. Couvre Protocol Buffers, services unaires et streaming, intégration HTTP/2, intercepteurs, load balancing, deadlines, TLS/mTLS, reflection, et gateway REST."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, grpc, protobuf, http2, microservices, backend]
    related_skills: [api-rest-best-practices, api-security, api-websocket]
---

# API gRPC

## Vue d'ensemble

gRPC (Google, 2015) est un framework RPC (Remote Procedure Call) haute performance basé sur HTTP/2 et Protocol Buffers (protobuf). Contrairement à REST/JSON où les données sont sérialisées en texte, gRPC utilise un format binaire compact, des connexions multiplexées, et supporte 4 types de communication (unaire, server streaming, client streaming, bidirectional streaming). Il est le choix standard pour les communications inter-microservices.

## Quand l'utiliser

- Communications internes entre microservices (haute performance, faible latence)
- Systèmes nécessitant du streaming bidirectionnel (chat, logs en temps réel, IoT)
- Applications polyglottes (gRPC génère des clients pour 10+ langages)
- Remplacement de REST pour des APIs internes où la performance compte
- Intégration avec des systèmes existants (gRPC gateway pour exposer en REST)

Ne pas utiliser pour : des APIs web publiques grand public (les navigateurs ne supportent pas nativement gRPC, préférer REST ou GraphQL), des APIs simples avec peu de trafic, des environnements où HTTP/2 est bloqué, ou quand le deboggage textuel est prioritaire (JSON est plus facile à inspecter).

## Concepts Fondamentaux

### 1. Protocol Buffers (protobuf)

Le langage IDL (Interface Definition Language) de gRPC. Définit les messages et services :

```protobuf
syntax = "proto3";

package eva.articles.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/field_mask.proto";

// === Messages ===

message Article {
  int64 id = 1;
  string title = 2;
  string content = 3;
  ArticleStatus status = 4;
  int64 author_id = 5;
  google.protobuf.Timestamp created_at = 6;
  google.protobuf.Timestamp updated_at = 7;
  repeated string tags = 8;
  map<string, string> metadata = 9;
}

enum ArticleStatus {
  ARTICLE_STATUS_UNSPECIFIED = 0;
  ARTICLE_STATUS_DRAFT = 1;
  ARTICLE_STATUS_PUBLISHED = 2;
  ARTICLE_STATUS_ARCHIVED = 3;
}

message CreateArticleRequest {
  string title = 1 [(validate.rules).string.min_len = 1];
  string content = 2;
  ArticleStatus status = 3;
  int64 author_id = 4;
  repeated string tags = 5;
}

message GetArticleRequest {
  int64 id = 1;
}

message ListArticlesRequest {
  int32 page = 1;       // Protobuf v3, 0 = valeur par défaut
  int32 page_size = 2;  // Max 100
  ArticleStatus status_filter = 3;
  string cursor = 4;    // Pour pagination cursor-based
}

message ListArticlesResponse {
  repeated Article articles = 1;
  string next_cursor = 2;
  int32 total_count = 3;
}

message DeleteArticleRequest {
  int64 id = 1;
}

message DeleteArticleResponse {
  bool success = 1;
}
```

**Règles de numérotation des champs :**

- Les champs 1-15 utilisent 1 byte, utiliser pour les champs fréquents
- Les champs 16-2047 utilisent 2 bytes
- Réserver les numéros pour backward compat : `reserved 2, 15, 9 to 11;`
- Ne jamais réutiliser un numéro supprimé

### 2. Types de Services gRPC

```protobuf
service ArticleService {
  // Unary (RPC classique requête-réponse)
  rpc GetArticle(GetArticleRequest) returns (Article);

  // Server streaming (le serveur envoie un flux de messages)
  rpc ListArticles(ListArticlesRequest) returns (stream Article);

  // Client streaming (le client envoie un flux, le serveur répond une fois)
  rpc BulkCreateArticles(stream CreateArticleRequest) returns (BulkCreateResponse);

  // Bidirectional streaming (les deux flux sont indépendants)
  rpc WatchArticles(stream WatchRequest) returns (stream ArticleEvent);
}
```

### 3. Messages Standard

```protobuf
import "google/protobuf/empty.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/duration.proto";
import "google/protobuf/struct.proto";
import "google/protobuf/field_mask.proto";
import "google/protobuf/wrappers.proto";  // StringValue, Int64Value, etc.
```

### 4. Deadline et Timeout

Le client définit une deadline, le serveur la propage :

```python
# Client Python
with grpc.insecure_channel('localhost:50051') as channel:
    stub = ArticleServiceStub(channel)
    try:
        article = stub.GetArticle(GetArticleRequest(id=42), timeout=5.0)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
            print("Timeout dépassé")
```

```go
// Client Go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
article, err := client.GetArticle(ctx, &pb.GetArticleRequest{Id: 42})
```

### 5. Interceptors (Middleware)

**Python (côté serveur) :**

```python
class AuthInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # Extraire le token du metadata
        metadata = dict(handler_call_details.invocation_metadata)
        token = metadata.get("authorization", "")

        # Valider le token
        payload = verify_jwt(token)
        if not payload:
            return self._deny(grpc.StatusCode.UNAUTHENTICATED, "Token invalide")

        # Propager le contexte utilisateur
        return continuation(handler_call_details)
```

**Go :**

```go
func UnaryAuthInterceptor(ctx context.Context, req interface{},
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {

    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "Missing metadata")
    }

    token := strings.TrimPrefix(md.Get("authorization")[0], "Bearer ")
    claims, err := validateJWT(token)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, err.Error())
    }

    newCtx := context.WithValue(ctx, "user", claims)
    return handler(newCtx, req)
}
```

### 6. Load Balancing

gRPC supporte le load balancing côté client (contrairement à HTTP/1.1) :

```go
// Client-side load balancing avec gRPC resolver
conn, err := grpc.Dial(
    "dns:///articles.service.consul:50051",
    grpc.WithDefaultServiceConfig(`{
        "loadBalancingConfig": [{"round_robin": {}}]
    }`),
    grpc.WithInsecure(),
)
```

### 7. Health Check Protocol

gRPC définit un protocole standard de health check :

```protobuf
service Health {
  rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
  rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
}

message HealthCheckRequest {
  string service = 1;
}

message HealthCheckResponse {
  enum ServingStatus {
    UNKNOWN = 0;
    SERVING = 1;
    NOT_SERVING = 2;
    SERVICE_UNKNOWN = 3;
  }
  ServingStatus status = 1;
}
```

### 8. gRPC Gateway (REST ↔ gRPC)

Exposer une API gRPC en REST/JSON via `grpc-gateway` (protoc-gen-grpc-gateway) :

```protobuf
import "google/api/annotations.proto";

service ArticleService {
  rpc GetArticle(GetArticleRequest) returns (Article) {
    option (google.api.http) = {
      get: "/v1/articles/{id}"
    };
  }
  rpc ListArticles(ListArticlesRequest) returns (ListArticlesResponse) {
    option (google.api.http) = {
      get: "/v1/articles"
    };
  }
  rpc CreateArticle(CreateArticleRequest) returns (Article) {
    option (google.api.http) = {
      post: "/v1/articles"
      body: "*"
    };
  }
}
```

### 9. Reflection et gRPCurl

Le service de reflection permet d'inspecter l'API sans protos :

```protobuf
import "google/protobuf/descriptor.proto";

// À activer côté serveur :
reflection.Register(grpcServer)
```

```bash
# gRPCurl — l'équivalent de curl pour gRPC
grpcurl -plaintext localhost:50051 list
grpcurl -plaintext localhost:50051 describe eva.articles.v1.ArticleService
grpcurl -plaintext -d '{"id": 42}' localhost:50051 eva.articles.v1.ArticleService/GetArticle
```

## Implémentation Référence

### Serveur Python (grpcio + aio)

```python
import asyncio
import grpc
from grpc import aio

class ArticleService(article_pb2_grpc.ArticleServiceServicer):
    async def GetArticle(self, request, context):
        article = await db.get_article(request.id)
        if not article:
            await context.abort(grpc.StatusCode.NOT_FOUND, "Article introuvable")
        return article

    async def ListArticles(self, request, context):
        async for article in db.list_articles(request.page, request.page_size):
            yield article  # Server streaming

    async def BulkCreateArticles(self, request_iterator, context):
        count = 0
        async for req in request_iterator:
            await db.create_article(req)
            count += 1
        return BulkCreateResponse(count=count)

async def serve():
    server = aio.server()
    article_pb2_grpc.add_ArticleServiceServicer_to_server(ArticleService(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()
```

### Serveur Go

```go
type articleServer struct {
    pb.UnimplementedArticleServiceServer
    db *sql.DB
}

func (s *articleServer) GetArticle(ctx context.Context, req *pb.GetArticleRequest) (*pb.Article, error) {
    var article pb.Article
    err := s.db.QueryRowContext(ctx, "SELECT id, title, content FROM articles WHERE id = $1", req.Id).
        Scan(&article.Id, &article.Title, &article.Content)
    if err == sql.ErrNoRows {
        return nil, status.Error(codes.NotFound, "article not found")
    }
    return &article, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer(
        grpc.UnaryInterceptor(UnaryAuthInterceptor),
        grpc.StreamInterceptor(StreamAuthInterceptor),
        grpc.MaxRecvMsgSize(4 * 1024 * 1024), // 4MB
    )
    pb.RegisterArticleServiceServer(s, &articleServer{db: connectDB()})
    reflection.Register(s)
    log.Fatal(s.Serve(lis))
}
```

## Pièges Courants

1. **Messages trop gros** — gRPC a une limite par défaut de 4MB. Pour les fichiers, utiliser du streaming.
2. **Oublier les deadlines** — sans deadline, un client peut rester bloqué indéfiniment. Toujours les définir.
3. **Numérotation de champs mal gérée** — réutiliser un numéro de champ supprimé casse la compatibilité. Utiliser `reserved`.
4. **Pas de load balancing** — gRPC crée des connexions HTTP/2 persistantes. Sans LB, tout le trafic va sur un seul backend.
5. **Métriques oubliées** — prometheus, tracing (OpenTelemetry) ne sont pas automatiques. Ajouter des intercepteurs.
6. **gRPC-Web** — les navigateurs ne supportent pas gRPC nativement. Utiliser gRPC-Web avec Envoy ou un proxy.
7. **Enum sans valeur par défaut** — protobuf v3, le champ 0 est la valeur par défaut. Toujours définir `UNSPECIFIED = 0`.
8. **Sécurité** — gRPC ne chiffre pas par défaut. Utiliser TLS/mTLS pour la production (`.add_secure_port`).

## Checklist de Vérification

- [ ] Schémas `.proto` compilés avec `protoc` (générer les stubs)
- [ ] Services définis : unaire, streaming si nécessaire
- [ ] TLS/mTLS configuré en production
- [ ] Intercepteurs : auth, logging, métriques, recovery
- [ ] Deadlines configurées côté client
- [ ] Health check service implémenté
- [ ] Load balancing configuré (client-side ou proxy)
- [ ] Limites de messages configurées (`MaxRecvMsgSize`, `MaxSendMsgSize`)
- [ ] gRPC-Web ou gateway REST si exposition navigateur
- [ ] Tests unitaires et d'intégration (stubs mockés)