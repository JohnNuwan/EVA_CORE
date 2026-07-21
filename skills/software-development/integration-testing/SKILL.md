---
name: integration-testing
description: "Tests d'intégration — bases de données, API REST, files de messages, microservices, containers, strategies et patterns de déploiement CI."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [integration-testing, api, database, microservices, testing, ci, containers]
    related_skills: [playwright, test-driven-development, e2e-testing, performance-testing]
---

# Tests d'Intégration — Stratégies et Patterns

## Overview

Les tests d'intégration vérifient que les différents modules d'une application fonctionnent correctement ensemble : base de données, API, files de messages, services externes. Contrairement aux tests unitaires, ils sollicitent les vrais composants (ou des substituts proches).

## When to Use

- Vérifier les interactions entre couches (ORM ↔ DB, API ↔ Service, Publisher ↔ Queue)
- Valider les contrats d'API REST/gRPC/GraphQL
- Tester les pipelines de données (ETL, transformations)
- Après chaque test unitaire, avant les tests E2E (Test Pyramid)
- Ne pas utiliser pour : tester l'UI (préférer E2E), tester les régressions métier complexes

## Pyramide des Tests

```
         /\           E2E (peu, lents)
        /  \          Tests d'intégration (moyen, ciblés)
       /    \
      /      \        Tests unitaires (nombreux, rapides)
     /________\
```

Ratio cible (Google/Twitter recommandent) : 70% unitaires, 20% intégration, 10% E2E.

## Stratégies par Type d'Intégration

### 1. Tests d'Intégration Base de Données

```python
# tests/integration/test_user_repository.py
"""Tests d'intégration du repository utilisateur avec une vraie BD."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from myapp.models import Base, User
from myapp.repositories import UserRepository

@pytest.fixture
def db_session():
    """Fixture avec une BD PostgreSQL de test (via Testcontainers)."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer('postgres:16-alpine') as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
        Base.metadata.drop_all(engine)


class TestUserRepository:
    """Tests du repository User avec vraie BD."""

    def test_create_user(self, db_session):
        """Vérifie la création d'un utilisateur en base."""
        repo = UserRepository(db_session)
        user = repo.create(email='alice@example.com', name='Alice')
        assert user.id is not None
        assert user.email == 'alice@example.com'

    def test_find_by_email(self, db_session):
        """Vérifie la recherche par email."""
        repo = UserRepository(db_session)
        repo.create(email='alice@example.com', name='Alice')

        found = repo.find_by_email('alice@example.com')
        assert found is not None
        assert found.name == 'Alice'

    def test_email_unique_constraint(self, db_session):
        """Vérifie la contrainte d'unicité sur l'email."""
        repo = UserRepository(db_session)
        repo.create(email='alice@example.com', name='Alice')

        with pytest.raises(IntegrityError):
            repo.create(email='alice@example.com', name='Bob')
```

### 2. Tests d'Intégration API REST (FastAPI)

```python
# tests/integration/test_api.py
"""Tests d'intégration de l'API REST FastAPI avec BD réelle."""

import pytest
from httpx import AsyncClient, ASGITransport
from myapp.main import app
from myapp.database import get_db

@pytest.fixture
async def client(db_session):
    """Client HTTP asynchrone branché sur la vraie app + vraie BD."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
class TestUserAPI:
    async def test_create_user_via_api(self, client):
        """Vérifie la création d'utilisateur via l'API REST."""
        response = await client.post('/api/users', json={
            'email': 'bob@example.com',
            'name': 'Bob',
        })
        assert response.status_code == 201
        data = response.json()
        assert data['email'] == 'bob@example.com'
        assert 'id' in data

    async def test_get_user_not_found(self, client):
        """Vérifie le code 404 pour un utilisateur inexistant."""
        response = await client.get('/api/users/99999')
        assert response.status_code == 404
        assert 'not found' in response.json()['detail'].lower()

    async def test_create_duplicate_email(self, client):
        """Vérifie le code 409 pour email dupliqué."""
        await client.post('/api/users', json={
            'email': 'dup@example.com', 'name': 'First'
        })
        response = await client.post('/api/users', json={
            'email': 'dup@example.com', 'name': 'Second'
        })
        assert response.status_code == 409
```

### 3. Tests d'Intégration avec Conteneurs (Testcontainers)

```python
# tests/integration/test_microservice.py
"""Tests d'intégration avec dépendances conteneurisées."""

import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope='module')
def postgres():
    with PostgresContainer('postgres:16-alpine') as pg:
        yield pg

@pytest.fixture(scope='module')
def redis():
    with RedisContainer('redis:7-alpine') as r:
        yield r

@pytest.fixture(scope='module')
def kafka():
    with KafkaContainer('confluentinc/cp-kafka:7.6') as k:
        yield k


class TestOrderProcessing:
    """Tests du service de commandes avec vraies dépendances."""

    def test_create_order_publishes_event(
        self, postgres, redis, kafka
    ):
        """Vérifie que créer une commande publie un événement Kafka."""
        # Configurer les clients avec les vrais endpoints des containers
        db_url = postgres.get_connection_url()
        redis_url = redis.get_connection_url()
        kafka_broker = kafka.get_bootstrap_server()

        service = OrderService(
            db_url=db_url,
            cache_url=redis_url,
            broker=kafka_broker,
        )

        order = service.create_order(
            user_id=1,
            items=[{'product_id': 'P001', 'qty': 2}],
        )

        assert order.id is not None
        assert order.status == 'pending'

        # Vérifier que l'événement a été publié
        consumer = KafkaConsumer(
            'order.created',
            bootstrap_servers=kafka_broker,
        )
        messages = list(consumer)
        assert len(messages) == 1
        assert messages[0].value['order_id'] == order.id
```

### 4. Tests de Contrats (Pact)

```python
# tests/contracts/provider_pact.py
"""Test de contrat côté fournisseur (provider) avec Pact."""

from pact import Verifier

def test_provider_meets_consumer_contract():
    """Vérifie que l'API fournisseur respecte le contrat du consommateur."""
    verifier = Verifier(provider='UserService', provider_base_url='http://localhost:8000')

    output, logs = verifier.verify_pacts(
        './pacts/consumer-UserService.json',
        verbose=True,
        provider_states_setup_url='http://localhost:8000/_pact/provider-states',
    )

    assert output == 0, f"Pact verification failed: {logs}"
```

### 5. Tests d'Intégration Async (RabbitMQ / Redis)

```python
"""Tests d'intégration avec une file de messages."""

import asyncio
import aio_pika
import pytest

@pytest.mark.asyncio
async def test_message_published_to_queue_is_consumed():
    """Vérifie le cycle complet publish → consume sur RabbitMQ."""
    connection = await aio_pika.connect_robust('amqp://guest:guest@localhost:5672/')
    channel = await connection.channel()

    # Déclarer une file temporaire
    queue = await channel.declare_queue('test.queue', auto_delete=True)

    # Publier
    await channel.default_exchange.publish(
        aio_pika.Message(body=b'{"action": "test"}'),
        routing_key='test.queue',
    )

    # Consommer
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                body = message.body.decode()
                assert '"action": "test"' in body
                break  # Un seul message suffit

    await connection.close()
```

## Tests d'Intégration avec Docker Compose

```yaml
# docker-compose.test.yml
services:
  app:
    build: .
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
      kafka: { condition: service_healthy }
    environment:
      DATABASE_URL: postgresql://test:test@db:5432/test
      REDIS_URL: redis://redis:6379/0
      KAFKA_BROKER: kafka:9092

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: test
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U test']
      interval: 2s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine

  kafka:
    image: confluentinc/cp-kafka:7.6
    environment:
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
```

```bash
# Lancer et exécuter les tests
docker compose -f docker-compose.test.yml up -d
docker compose -f docker-compose.test.yml run app pytest tests/integration/ -v
docker compose -f docker-compose.test.yml down -v
```

## Fichiers Utilitaires

```makefile
# Makefile
.PHONY: test-integration

test-integration:
	docker compose -f docker-compose.test.yml up -d --wait
	poetry run pytest tests/integration/ -v --timeout=60
	docker compose -f docker-compose.test.yml down -v
```

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on: [push]
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        ports: ['5432:5432']
        options: >-
          --health-cmd pg_isready
          --health-interval 2s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine
        ports: ['6379:6379']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -e ".[dev]"
      - run: pytest tests/integration/ -v --timeout=60
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
```

## Isolation et Nettoyage

```python
"""Fixtures pour l'isolation des tests d'intégration."""

import pytest
from sqlalchemy import text

@pytest.fixture(autouse=True)
def cleanup_database(db_session):
    """Nettoie toutes les tables après chaque test (transaction rollback)."""
    yield
    db_session.rollback()  # Option 1: rollback transaction

    # Option 2: truncate toutes les tables
    tables = ['users', 'orders', 'products']
    for table in tables:
        db_session.execute(text(f'TRUNCATE TABLE {table} CASCADE'))
    db_session.commit()

@pytest.fixture(autouse=True)
def flush_redis(redis_client):
    """Nettoie Redis après chaque test."""
    yield
    redis_client.flushdb()

@pytest.fixture(autouse=True)
def reset_kafka_topics(kafka_admin):
    """Supprime les topics Kafka créés pendant le test."""
    yield
    topics = kafka_admin.list_topics()
    for topic in topics:
        if topic.startswith('test.'):
            kafka_admin.delete_topics([topic])
```

## Bonnes Pratiques

1. **Une vraie BD** (ou Testcontainers) — jamais de BD en mémoire à moins que la prod n'en utilise une
2. **Nettoyage systématique** — chaque test part d'un état connu
3. **Transactions rollback** plutôt que recreate database pour la vitesse
4. **Tester les cas d'erreur** — timeouts, connexions refusées, données corrompues
5. **Nommer les tests par contrat** — `test_create_order_email_notification_sent`
6. **Éviter les mocks** — l'intégration teste la vraie interaction
7. **Timeout global** — les tests d'intégration peuvent pendre si un service est down

## Common Pitfalls

1. **Base de données en mémoire (SQLite)** — comportement différent de PostgreSQL en prod (contraintes, types, transactions)
2. **Pas de nettoyage entre tests** — pollution des données, tests qui passent par hasard
3. **Fixtures scope='session' sans isolation** — mutabilité partagée entre tests
4. **Docker Compose trop lent** — Testcontainers ne démarre les conteneurs qu'une fois par session
5. **Tests qui dépendent de l'ordre d'exécution** — toujours randomiser ou paralléliser pour le détecter

## Verification Checklist

- [ ] Chaque test d'intégration utilise une vraie instance du service (BD, queue, cache)
- [ ] Les données de test sont isolées (transaction rollback ou truncate)
- [ ] Les cas d'erreur sont testés (timeout, 404, 409, 500)
- [ ] Temps d'exécution acceptable (< 30s pour la suite complète)
- [ ] CI utilise des services GitHub ou Docker pour les dépendances
