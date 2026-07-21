---
name: api-security
description: "Use when sécuriser, auditer ou durcir une API. Couvre l'authentification (JWT, OAuth2, API Keys), l'autorisation (RBAC, ABAC, ACL), la validation des entrées, la protection contre les attaques (injection, CSRF, XSS, SSRF), TLS, CORS, rate limiting, logging de sécurité, et le stockage des secrets."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, security, authentication, authorization, oauth2, jwt, backend, web]
    related_skills: [api-rest-best-practices, api-rate-limiting, api-openapi-documentation]
---

# Sécurité des API

## Vue d'ensemble

La sécurité d'une API est un problème multi-couche : chaque requête traverse le réseau, le TLS, l'authentification, l'autorisation, la validation, et le backend. Une faille dans une seule couche expose l'ensemble. Ce guide couvre les 8 piliers de la sécurité API : authentification, autorisation, validation, transport, CORS, rate limiting, audit, et gestion des secrets.

## Quand l'utiliser

- Avant de mettre une API en production
- Lors d'un audit de sécurité d'une API existante
- Pour implémenter l'authentification et l'autorisation
- Pour configurer TLS, CORS, et les en-têtes de sécurité HTTP
- Pour se protéger contre les attaques courantes (injection, CSRF, SSRF)

## 1. Authentification

### JWT (JSON Web Token)

Le standard le plus courant pour les APIs REST modernes :

```python
import jwt
from datetime import datetime, timedelta

SECRET_KEY = "clé ultra-secrète"  # À mettre dans .env, PAS dans le code
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE = timedelta(minutes=30)
REFRESH_TOKEN_EXPIRE = timedelta(days=7)

def create_access_token(user_id: int, roles: list[str]) -> str:
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + ACCESS_TOKEN_EXPIRE,
        "iss": "eva-api",
        "aud": "eva-client",
        "jti": secrets.token_hex(16),  # ID unique pour blacklist
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM],
            issuer="eva-api", audience="eva-client",
        )
        # Vérifier si le token n'est pas blacklisté
        if is_blacklisted(payload["jti"]):
            raise InvalidToken("Token révoqué")
        return payload
    except jwt.ExpiredSignatureError:
        raise InvalidToken("Token expiré")
    except jwt.InvalidTokenError:
        raise InvalidToken("Token invalide")
```

**Bonnes pratiques JWT :**

- Toujours vérifier `iss` (issuer) et `aud` (audience)
- Utiliser `jti` (JWT ID) pour blacklister les tokens
- Tokens courts (15-30 min) + refresh tokens longs
- Ne JAMAIS mettre de secrets dans le payload (il est base64, pas chiffré)
- Utiliser des algorithmes asymétriques (RS256, ES256) pour les APIs publiques

### OAuth 2.0

Pour les APIs qui délèguent l'authentification à un fournisseur tiers :

```python
# Flow Authorization Code (le plus sécurisé pour les applications web)
@app.get("/auth/callback")
async def oauth_callback(code: str):
    # 1. Échanger le code contre un token
    token = await exchange_code(code)

    # 2. Récupérer les infos utilisateur
    user_info = await get_user_info(token["access_token"])

    # 3. Créer notre propre session/token
    our_token = create_access_token(user_info["id"], user_info["roles"])

    return {"access_token": our_token, "token_type": "bearer"}
```

**Flux OAuth2 :**

| Flow | Usage | Sécurité |
|------|-------|----------|
| Authorization Code | App web avec backend | ★★★★★ |
| Authorization Code + PKCE | SPA / Mobile | ★★★★★ |
| Client Credentials | Service-to-service | ★★★★☆ |
| Resource Owner Password | Legacy (déprécié) | ★★☆☆☆ |
| Implicit Flow | Legacy (déprécié) | ★☆☆☆☆ |

### API Keys

Pour les services machine-to-machine :

```python
from hashlib import sha256
import secrets

API_KEY_PREFIX = "eva_"

def generate_api_key() -> tuple[str, str]:
    """Génère une paire (clé brute, hash à stocker)."""
    raw = API_KEY_PREFIX + secrets.token_urlsafe(32)
    hashed = sha256(raw.encode()).hexdigest()
    return raw, hashed

def verify_api_key(raw_key: str, stored_hash: str) -> bool:
    return sha256(raw_key.encode()).hexdigest() == stored_hash
```

## 2. Autorisation

### RBAC (Role-Based Access Control)

```python
ROLES = {
    "admin": {"articles:read", "articles:write", "articles:delete", "users:manage"},
    "editor": {"articles:read", "articles:write"},
    "viewer": {"articles:read"},
}

class AuthMiddleware:
    def require_permission(self, permission: str):
        def decorator(func):
            async def wrapper(request: Request, *args, **kwargs):
                user = request.state.user
                if permission not in ROLES.get(user.get("role", ""), set()):
                    raise HTTPException(403, "Permission insuffisante")
                return await func(request, *args, **kwargs)
            return wrapper
        return decorator

# Usage
@app.get("/articles/{id}")
@require_permission("articles:read")
async def get_article(id: int):
    ...
```

### ABAC (Attribute-Based Access Control)

Plus fin que RBAC : les permissions dépendent des attributs de la ressource, de l'utilisateur, et du contexte :

```python
class ABACPolicy:
    def can_read_article(self, user: dict, article: dict) -> bool:
        # Règles : l'utilisateur peut lire si
        # - il est admin, OU
        # - il est l'auteur, OU
        # - l'article est publié
        if user.get("role") == "admin":
            return True
        if article.get("author_id") == user.get("id"):
            return True
        if article.get("status") == "published":
            return True
        return False

    def can_delete_article(self, user: dict, article: dict) -> bool:
        # Seul l'admin ou l'auteur peut supprimer
        if user.get("role") == "admin":
            return True
        if article.get("author_id") == user.get("id"):
            return True
        return False
```

## 3. Validation des Entrées

### Validation des Schémas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import html

class CreateArticleInput(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="Titre de l'article")
    content: str = Field(..., min_length=1, description="Contenu")
    status: Optional[str] = "draft"
    author_id: int = Field(..., gt=0)

    @validator("title")
    def sanitize_title(cls, v):
        # Anti-XSS basique
        return html.escape(v.strip())

    @validator("status")
    def validate_status(cls, v):
        allowed = {"draft", "published", "archived"}
        if v not in allowed:
            raise ValueError(f"Status invalide. Choisir parmi {allowed}")
        return v
```

### Content-Type Validation

```python
@app.middleware("http")
async def validate_content_type(request: Request, call_next):
    if request.method in ("POST", "PUT", "PATCH"):
        content_type = request.headers.get("content-type", "")
        if "application/json" not in content_type:
            return JSONResponse(
                status_code=415,
                content={"error": "Content-Type doit être application/json"},
            )
    return await call_next(request)
```

## 4. Sécurité du Transport

### TLS (HTTPS)

```python
# FastAPI avec TLS
import ssl
import uvicorn

ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
ssl_context.load_cert_chain("cert.pem", keyfile="key.pem")
ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3

# Redirection HTTP → HTTPS
@app.middleware("http")
async def redirect_to_https(request: Request, call_next):
    if request.headers.get("x-forwarded-proto", "http") != "https":
        url = request.url.replace(scheme="https")
        return RedirectResponse(url, status_code=301)
    return await call_next(request)
```

### HSTS (HTTP Strict Transport Security)

```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    return response
```

## 5. En-Têtes de Sécurité HTTP

```python
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers.update({
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "0",  # Désactivé car basé sur un navigateur déprécié
        "Content-Security-Policy": "default-src 'self'; script-src 'self'; object-src 'none'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    })
    return response
```

## 6. CORS (Cross-Origin Resource Sharing)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://eva.dev",
        "https://app.eva.dev",
        "https://admin.eva.dev",
    ],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-RateLimit-Remaining", "X-RateLimit-Reset"],
    allow_credentials=True,
    max_age=600,  # 10 minutes
)
```

**Règle d'or :** ne jamais utiliser `allow_origins=["*"]` avec `allow_credentials=True`. Soit tout est ouvert, soit les credentials sont sécurisés.

## 7. Protection Contre les Attaques

### SQL Injection

```python
# MAUVAIS : concaténation
cursor.execute(f"SELECT * FROM articles WHERE id = {id}")

# BON : paramètres
cursor.execute("SELECT * FROM articles WHERE id = %s", (id,))
```

### NoSQL Injection (MongoDB)

```python
# MAUVAIS : query brute
collection.find({"username": username, "password": password})

# BON : validation et typage
from bson.objectid import ObjectId
collection.find({
    "username": {"$eq": str(username)},
    "password": {"$eq": str(password)},
})
```

### SSRF (Server-Side Request Forgery)

```python
import ipaddress
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    try:
        # Bloquer les IPs privées
        ip = ipaddress.ip_address(parsed.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise ValueError("URL interne bloquée")
    except ValueError:
        if parsed.hostname in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
            raise ValueError("URL locale bloquée")
    return True
```

### CSRF (pour les APIs basées sur cookies)

```python
from fastapi import Header, HTTPException

@app.post("/api/articles")
async def create_article(
    request: CreateArticleInput,
    x_csrf_token: str = Header(None),
):
    if not x_csrf_token or not verify_csrf_token(x_csrf_token):
        raise HTTPException(403, "CSRF token invalide")
    ...
```

## 8. Logging de Sécurité

```python
import logging
from datetime import datetime

security_logger = logging.getLogger("security")

class SecurityLogMiddleware:
    async def __call__(self, request: Request, call_next):
        # Avant
        ip = request.client.host
        method = request.method
        path = request.url.path
        user_agent = request.headers.get("user-agent", "")

        start = datetime.utcnow()

        try:
            response = await call_next(request)
            status = response.status_code
        except Exception as e:
            status = 500
            raise
        finally:
            duration = (datetime.utcnow() - start).total_seconds()
            # Logger les événements de sécurité
            if status in (401, 403, 429):
                security_logger.warning(
                    f"Événement sécurité: {ip} {method} {path} → {status} "
                    f"({duration}s) UA: {user_agent}"
                )
            elif status >= 500:
                security_logger.error(
                    f"Erreur serveur: {ip} {method} {path} → {status} "
                    f"({duration}s)"
                )
        return response
```

## 9. Gestion des Secrets

```python
# .env (jamais commité !)
# SECRET_KEY=super-secret-key-à-32-caractères-minimum
# DATABASE_URL=postgresql://user:pass@localhost:5432/db
# JWT_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...
# SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Chargement
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = Field(min_length=32, alias="SECRET_KEY")
    database_url: str = Field(alias="DATABASE_URL")
    jwt_private_key: str = Field(alias="JWT_PRIVATE_KEY")
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

## Pièges Courants

1. **JWT sans expiration** — un token volé est valide indéfiniment. Toujours expirer (15-30 min).
2. **CORS trop permissif** — `Access-Control-Allow-Origin: *` avec credentials ouvre la porte aux attaques cross-site.
3. **Validation côté client uniquement** — la validation doit TOUJOURS exister côté serveur.
4. **Secrets dans le code** — jamais de clés API, mots de passe ou tokens dans le code source. Utiliser `.env`, Vault, ou AWS Secrets Manager.
5. **Pas de rate limiting** — sans limite, un attaquant peut bruteforcer l'authentification ou faire du DoS.
6. **Logging insuffisant** — sans logs de sécurité, impossible de détecter ou investiguer une attaque.
7. **TLS configuré mais pas forcé** — si le serveur écoute aussi en HTTP, les clients peuvent être downgradés.
8. **IDOR (Insecure Direct Object Reference)** — l'utilisateur 1 peut accéder aux données de l'utilisateur 2. Toujours vérifier l'appartenance.

## Checklist de Vérification

- [ ] Authentification implémentée (JWT, OAuth2, ou API Keys)
- [ ] Autorisation appliquée à chaque endpoint (RBAC ou ABAC)
- [ ] Validation des entrées (Pydantic, marshmallow, ou équivalent)
- [ ] TLS 1.2+ configuré et forcé (redirection HTTP → HTTPS)
- [ ] HSTS activé
- [ ] En-têtes de sécurité HTTP présents (X-Content-Type-Options, CSP, etc.)
- [ ] CORS configuré avec une liste d'origines autorisées (pas `*`)
- [ ] Rate limiting implémenté
- [ ] Protection contre les injections (SQL, NoSQL, command)
- [ ] Protection SSRF (blocage des IPs privées)
- [ ] Logs de sécurité (401, 403, 429, 5xx)
- [ ] Secrets gérés via variables d'environnement ou secret manager
- [ ] Tests de sécurité : auth invalide, permissions manquantes, injection