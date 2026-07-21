---
name: performance-testing
description: "Tests de performance, charge et stress — k6, Locust, JMeter, ab, Artillery, métriques, analyse des bottlenecks, et CI/CD."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [performance-testing, load-testing, stress-testing, k6, locust, jmeter, benchmarking]
    related_skills: [integration-testing, e2e-testing, security-testing]
---

# Tests de Performance — Charge, Stress et Benchmark

## Overview

Les tests de performance mesurent comment un système se comporte sous différentes conditions de charge. Ils détectent les régressions de performance, dimensionnent l'infrastructure, valident les SLAs, et préviennent les outages.

## Types de Tests de Performance

| Type | Objectif | Charge | Durée |
|------|----------|--------|-------|
| **Load Test** | Comportement sous charge normale attendue | 50-80% du pic | 15-30 min |
| **Stress Test** | Point de rupture | 150-200%+ du pic | Jusqu'à rupture |
| **Spike Test** | Réaction à une montée brutale | ×10 en 1-2s | Quelques minutes |
| **Soak Test** | Fuites mémoire / dégradation lente | Charge normale | 2-24h |
| **Endurance Test** | Stabilité long terme | 50-70% | 24-72h |

## Indicateurs Clés

| Métrique | Seuil typique | Outil |
|----------|--------------|-------|
| P95/P99 Latency | < 500ms / < 2s | k6, JMeter |
| TPS (Throughput) | Objectif métier | Tous |
| Error Rate | < 0.1% | Tous |
| CPU / Memory | < 80% | htop, Prometheus |
| GC Pause (JVM) | < 200ms P99 | JFR, GC logs |
| DB Connection Pool | < 80% utilisé | pg_stat_activity |
| Disk I/O | < 80% iowait | iostat |

## k6 — Outil Moderne (JavaScript/Go)

### Installation et Configuration

```bash
# Installation
sudo apt install k6
# ou
docker pull grafana/k6
# macOS
brew install k6
```

### Script de Load Test

```javascript
// tests/performance/load-test.js
import http from 'k6/http';
import { sleep, check, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Métriques personnalisées
const errorRate = new Rate('errors');
const loginDuration = new Trend('login_duration');
const loginFailures = new Counter('login_failures');

export const options = {
  // Phases de charge progressive
  stages: [
    { duration: '1m', target: 10 },    // Montée
    { duration: '3m', target: 50 },    // Palier
    { duration: '1m', target: 100 },   // Pic
    { duration: '2m', target: 100 },   // Maintien
    { duration: '1m', target: 0 },     // Descente
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<2000'],
    http_req_failed: ['rate<0.01'],
    errors: ['rate<0.05'],
    login_duration: ['p(95)<1000'],
  },
  // Simuler des utilisateurs réalistes
  user_agent: 'k6-performance-test/1.0',
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000';

export default function () {
  group('Parcours Connexion', () => {
    const payload = JSON.stringify({
      email: `user${__VU}@test.com`,
      password: 'test123',
    });

    const start = Date.now();
    const res = http.post(`${BASE_URL}/api/login`, payload, {
      headers: { 'Content-Type': 'application/json' },
      tags: { name: 'login' },
    });

    loginDuration.add(Date.now() - start);
    errorRate.add(res.status !== 200);

    check(res, {
      'login status 200': (r) => r.status === 200,
      'login response time < 1s': (r) => r.timings.duration < 1000,
      'has token': (r) => JSON.parse(r.body).token !== undefined,
    });

    if (res.status !== 200) {
      loginFailures.add(1);
    }

    sleep(1); // 1 seconde de pause entre actions
  });

  group('Parcours Dashboard', () => {
    const res = http.get(`${BASE_URL}/api/dashboard`, {
      headers: { Authorization: `Bearer mock-token` },
      tags: { name: 'dashboard' },
    });

    check(res, {
      'dashboard status 200': (r) => r.status === 200,
      'dashboard size < 50KB': (r) => r.body.length < 50000,
    });
    sleep(2);
  });
}
```

### Stress Test (point de rupture)

```javascript
// tests/performance/stress-test.js
export const options = {
  scenarios: {
    stress: {
      executor: 'ramping-arrival-rate',
      startRate: 10,
      timeUnit: '1s',
      preAllocatedVUs: 100,
      maxVUs: 500,
      stages: [
        { duration: '5m', target: 50 },     // 50 req/s
        { duration: '5m', target: 100 },    // 100 req/s
        { duration: '5m', target: 200 },    // 200 req/s
        { duration: '5m', target: 400 },    // 400 req/s
        { duration: '5m', target: 600 },    // 600 req/s → rupture attendue
      ],
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],  // Tolérant : on cherche le point de rupture
  },
};
```

### Soak Test (24h)

```javascript
export const options = {
  stages: [
    { duration: '5m', target: 50 },
    { duration: '24h', target: 50 },
    { duration: '5m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01'],
  },
};
```

### Test de l'API en Mode Brouillon

```javascript
// tests/performance/spike-test.js
export const options = {
  scenarios: {
    spike: {
      executor: 'constant-arrival-rate',
      rate: 10,
      duration: '30s',
      preAllocatedVUs: 20,
      maxVUs: 200,
    },
  },
};
```

### Tests avec k6 Browser (E2E Performance)

```javascript
import { browser } from 'k6/browser';

export const options = {
  scenarios: {
    ui: {
      executor: 'shared-iterations',
      options: { browser: { type: 'chromium' } },
    },
  },
};

export default async function () {
  const page = await browser.newPage();

  try {
    await page.goto('https://example.com/login', { waitUntil: 'networkidle' });

    // Mesurer le LCP (Largest Contentful Paint)
    const lcp = await page.evaluate(() =>
      performance.getEntriesByType('paint').pop()?.startTime
    );

    // Interaction
    await page.fill('#email', 'user@test.com');
    await page.fill('#password', 'test123');
    await Promise.all([
      page.waitForNavigation(),
      page.click('#submit'),
    ]);

    // Métriques Web Vitals
    const metrics = await page.metrics();
    console.log(`LCP: ${lcp}ms, CLS: ${metrics.cls || 0}`);
  } finally {
    await page.close();
  }
}
```

## Locust — Outil Python

### Installation

```bash
pip install locust
```

### Script de Test

```python
# locustfile.py
from locust import HttpUser, task, between, tag
import json


class WebsiteUser(HttpUser):
    """Simule un utilisateur du site web."""

    wait_time = between(1, 5)  # Pause aléatoire réaliste

    def on_start(self):
        """Connexion au début de la session."""
        response = self.client.post('/api/login', json={
            'email': f'user{self.environment.runner.user_count}@test.com',
            'password': 'test123',
        })
        if response.status_code == 200:
            self.token = response.json().get('token')
        else:
            self.token = None

    @tag('login')
    @task(3)  # Poids relatif : ce scénario s'exécute 3× plus souvent
    def view_dashboard(self):
        if self.token:
            self.client.get(
                '/api/dashboard',
                headers={'Authorization': f'Bearer {self.token}'},
            )

    @tag('search')
    @task(2)
    def search_products(self):
        self.client.get('/api/products?q=chaise&page=1')

    @tag('order')
    @task(1)  # Moins fréquent (1/6 des requêtes)
    def create_order(self):
        """Scénario complet de commande."""
        with self.client.post('/api/orders', json={
            'product_id': 'P001', 'qty': 1,
        }, catch_response=True) as response:
            if response.status_code != 201:
                response.failure('Échec création commande')
                return
            order_id = response.json().get('id')

            self.client.get(f'/api/orders/{order_id}', name='/api/orders/[id]')
```

### Exécution

```bash
# Web UI (recommandé)
locust --host=http://localhost:3000 --web-port=8089

# Headless (CI)
locust --host=http://localhost:3000 --headless \
  -u 100 --run-time 10m --spawn-rate 10 \
  --csv=reports/locust

# Avec tags
locust --host=http://localhost:3000 --tags login search
```

## JMeter — Outil Java

### Installation

```bash
# Télécharger et extraire
wget https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-5.6.3.tgz
tar xzf apache-jmeter-*.tgz
./apache-jmeter-5.6.3/bin/jmeter.sh

# Mode non-graphique (CI)
./apache-jmeter-5.6.3/bin/jmeter.sh -n -t test-plan.jmx -l results.jtl
```

### Test Plan Élémentaire (CLI via Taurus)

```yaml
# bzt.yml — Taurus wrapper pour JMeter
execution:
  - executor: jmeter
    scenario:
      script: test-plan.jmx
    concurrency: 50
    ramp-up: 60s
    hold-for: 5m
    iterations: 100

reporting:
  - module: final-stats
  - module: console
```

```bash
pip install bzt
bzt bzt.yml
```

## Tests de Performance API (ab, wrk, hey)

### Apache Bench

```bash
# Simple
ab -n 1000 -c 10 http://localhost:3000/api/health

# Avec headers + POST
ab -n 5000 -c 50 -T 'application/json' \
  -p payload.json \
  -H 'Authorization: Bearer token123' \
  http://localhost:3000/api/login
```

### WRK

```bash
wrk -t12 -c400 -d30s http://localhost:3000/api/health

# Avec script Lua personnalisé
wrk -t4 -c100 -d60s -s tests/perf/wrk-script.lua http://localhost:3000
```

### Hey

```bash
# Simple
hey -n 10000 -c 50 http://localhost:3000/api/health

# Avec headers
hey -n 5000 -c 20 -H 'Authorization: Bearer token' \
  -m POST -d '{"email":"test@test.com","pass":"test"}' \
  http://localhost:3000/api/login
```

## Analyse des Résultats

### Que chercher dans les métriques ?

```
P95 Latency :  Responsive ? La majorité des utilisateurs perçoit-elle la lenteur ?
P99 Latency :  Queue ? Y a-t-il des utilisateurs bloqués ?
Error Rate :   Stable ? Le système échoue-t-il sous charge ?
Throughput :   Capable ? Le TPS atteint-il l'objectif ?
```

### Seuils Communs

| Application | P95 | P99 | Taux Erreur |
|-------------|-----|-----|-------------|
| API REST standard | < 500ms | < 2s | < 0.1% |
| Page web SSR | < 1s | < 3s | < 0.1% |
| Base de données | < 50ms | < 200ms | < 0.01% |
| Streaming vidéo | < 200ms start | < 1s | < 1% |
| Paiement | < 2s | < 5s | < 0.01% |

## CI/CD — Performance Gates

```yaml
# .github/workflows/perf-tests.yml
name: Performance Tests
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Tous les matins

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Start services
        run: docker compose up -d
      - name: Run k6 tests
        run: |
          k6 run tests/performance/load-test.js \
            -e BASE_URL=http://localhost:3000 \
            --out json=reports/k6-report.json
      - name: Check thresholds
        run: |
          # Analyser si les seuils ont été respectés
          jq '.metrics.http_req_duration"p(95)".passes' reports/k6-report.json
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: k6-report
          path: reports/
```

## Bonnes Pratiques

1. **Toujours tester sur un environnement de préprod** — jamais en production sauf smoke test
2. **Isoler l'infra** — un serveur de test dédié ou conteneur isolé
3. **Métriques système + applicatives** — CPU/RAM/IO sans l'app ne suffit pas
4. **Répéter 3 fois** — une mesure isolée n'est pas significative
5. **Warm-up** — laisser 1-2 minutes de montée avant de mesurer
6. **Monitorer le backend** — les métriques frontend sans observabilité backend sont aveugles
7. **Comparer avec un baseline** — toujours garder un résultat de référence

## Common Pitfalls

1. **Tester en local** — résultats non-représentatifs (latence réseau, ressources partagées)
2. **Ignorer le warm-up** — JIT, caches, connections pools non initialisés
3. **Un seul run** — les résultats varient, faire 3 runs consécutifs
4. **Pas de metrics système** — 99% des goulots sont CPU, RAM, IO, réseau
5. **Charge trop simple** — le même GET sur le même endpoint = pas réaliste
6. **Pas d'arrêt progressif** — couper 500 connections d'un coup peut cacher des fuites
7. **Tester sur le même serveur que l'application** — les résultats sont faussés

## Verification Checklist

- [ ] Scénario réaliste (pas juste 1 seul endpoint répété)
- [ ] Phases de montée progressive
- [ ] Seuils (thresholds) définis et vérifiés
- [ ] Métriques système collectées (CPU, RAM, IO, réseau)
- [ ] Warm-up intégré avant la mesure
- [ ] Environnement isolé (pas de concurrence avec d'autres processus)
- [ ] Rapport généré et exportable
- [ ] Baseline de référence pour comparer les runs
