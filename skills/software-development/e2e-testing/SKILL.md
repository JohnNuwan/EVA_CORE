---
name: e2e-testing
description: "Stratégies de tests End-to-End — planification, flakyness, data management, reporting, multi-environnement, et guide de sélection d'outils."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [e2e, testing, strategy, flakyness, data-management, reporting, ci]
    related_skills: [cypress, playwright, selenium, integration-testing, test-driven-development]
---

# Tests End-to-End (E2E) — Stratégies et Patterns

## Overview

Un test E2E reproduit le parcours complet d'un utilisateur dans l'application. Il navigue, clique, saisit, attend, vérifie — sur une application réelle (ou une stack proche). Les tests E2E sont le sommet de la pyramide de test : les plus lents, les plus fragiles, mais les plus proches de l'expérience réelle.

## When to Use

- **Happy paths** des parcours utilisateur critiques (connexion, paiement, inscription)
- **Régression** avant chaque mise en production
- **Validation de release** (smoke tests en préprod)
- Ne pas utiliser pour : tester tous les edge cases (trop lent), tester du code qui change tous les jours, remplacer les tests unitaires

## Guide de Sélection d'Outils

| Critère | Cypress | Playwright | Selenium |
|---------|---------|------------|----------|
| Install | npm seul | npm + binaires | Driver + bindings |
| Navigateurs | Chromium, FF, Edge, WebKit* | Chromium, FF, WebKit | Tous (incl. IE11/Safari) |
| Vitesse | Très rapide (même processus) | Rapide (API asynchrone) | Modéré |
| Cross-browser | ✅ | ✅ | ✅ (le plus large) |
| Mobile | 📱 Viewport only | ✅ Devices natives | ✅ Appium |
| API/Network | ✅ Intercept | ✅ Route + Mock | ⚠️ CDP seulement |
| Component Tests | ✅ Cypress CT | ✅ Playwright CT | ❌ |
| Parallélisation | ✅ Cypress Cloud | ✅ Natif + sharding | ✅ Grid |
| Fiabilité | Élevée (auto-wait) | Très élevée (auto-wait) | ⚠️ Manuelle (Wait) |
| Debug | Time Travel + UI | Trace Viewer + UI | DevTools |

> *Cypress WebKit est en beta/bêta depuis la v12.

**Recommandation :** Nouveau projet → Playwright (meilleur rapport fiabilité/performance/cross-browser). Projet existant → l'outil déjà installé.

## Ce qu'il NE FAUT PAS Tester en E2E

```gherkin
❌ Tests d'email (formatage, contenu)        → Test unitaire
❌ Calculs métier (totaux, taxes)             → Test unitaire
❌ Schémas de base de données                 → Test d'intégration
❌ Pagination API sans UI                     → Test d'intégration
❌ Validation de formulaires côté backend     → Test d'intégration
❌ Tous les messages d'erreur possibles       → Test unitaire
❌ Timing d'animation                         → Test visuel/perf
❌ État scroll après navigation               → Test d'intégration UI
```

## Stratégie de Sélection des Tests

### Modèle RICE pour choisir quoi tester en E2E

| Critère | Poids | Exemple haut | Exemple bas |
|---------|-------|-------------|-------------|
| **R**evenu impacté | 5 | Tunnel de paiement | Page "À propos" |
| **I**mportance critique | 4 | Connexion, auth | Changement de thème |
| **C**omplexité technique | 3 | Upload + processing | Affichage liste |
| **E**rreurs fréquentes | 3 | Recherche, filtres | Footer, mentions |

**Score = R×5 + I×4 + C×3 + E×3. Seuil ≥ 30 → test E2E obligatoire.**

### Happy Paths Obligatoires

```
Pages d'auth                 : inscription, connexion, reset password, logout
Parcours d'achat             : ajout panier → checkout → confirmation
Création utilisateur         : formulaire → validation → redirection
Recherche & filtres          : recherche → résultats → pagination
Notification                 : action → notification visible → disparition
```

## Flakyness — Dompter les Tests Fragiles

### Causes Principales

| Cause | Fréquence | Solution |
|-------|-----------|----------|
| Timings / Asynchrone | 40% | Auto-wait, retry, attente explicite |
| Data pollution | 20% | Isolation totale des données de test |
| Ordre d'exécution | 15% | Tests indépendants, pas de state partagé |
| Environnement (réseau, DNS) | 10% | Mock des appels externes |
| Versions navigateur | 5% | WebDriverManager, pinned images |
| Sélecteurs CSS fragiles | 10% | data-attributes, getByRole/getByTestId |

### Anti-Flaky Patterns

```typescript
// ✅ Attendre l'élément (auto-retry)
await expect(page.locator('[data-test=success]')).toBeVisible();

// ❌ Sleep (à bannir)
await page.waitForTimeout(3000);
await expect(page.locator('.success')).toBeVisible();

// ✅ Intercepter les appels réseau
await page.route('**/api/orders/**', async route => {
  await route.fulfill({ status: 200, body: JSON.stringify(mockData) });
});

// ❌ Dépendre du vrai backend
// (peut être lent, down, ou avoir des données différentes)

// ✅ Re-tenter intelligemment (Playwright)
test.use({ retries: 2 });

// ✅ Nettoyer les données avant chaque test
test.beforeEach(async ({ page }) => {
  await apiClient.deleteTestData();
  await page.goto('/');
});
```

### Détection et Monitoring

```bash
# Analyser la flakyness — relire les 10 dernières runs CI
gh run list --workflow "E2E" --limit 10 --json conclusion,databaseId
# Identifier les tests qui échouent sur au moins 1 run mais pas tous
```

**Marquer un test flaky connu :**
```typescript
test.describe('Paiement', () => {
  test('paiement CB réussi', { tag: '@flaky' }, async ({ page }) => {
    test.fixme(); // Désactiver temporairement
    // ... ou retry plus généreux
    test.info().annotations.push({
      type: 'issue',
      description: 'https://github.com/org/repo/issues/42',
    });
  });
});
```

## Gestion des Données de Test

### Stratégies

```typescript
// 1. API Setup (recommandé) — nettoyer + créer via API avant chaque test
test.beforeEach(async ({ request }) => {
  await request.post('/api/test/clean');
  await request.post('/api/test/seed', {
    data: {
      users: [{ email: 'alice@test.com', role: 'admin' }],
      products: [{ sku: 'P001', name: 'Chaise', price: 99 }],
    },
  });
});

// 2. Fixtures statiques — données connues insérées en DB avant la CI
// (utile mais fragile si d'autres tests modifient ces données)

// 3. Gherkin Tables (BDD) — données inline dans le feature file
// Given les produits suivants:
//   | sku  | name    | price |
//   | P001 | Chaise  | 99    |

// 4. Factory Boy / Faker — génération aléatoire reproductible
```

### Tags de Données

```typescript
// data-test attributes pour identifier les lignes de données
<tr data-test="user-row" data-user-id="42">
  <td>Alice</td>
  <td><button data-test="delete-user">Supprimer</button></td>
</tr>
```

```typescript
await page.locator('[data-test=user-row][data-user-id="42"]')
  .locator('[data-test=delete-user]').click();
```

## Tests Multi-Environnements

```typescript
// playwright.config.ts — profiles
export default defineConfig({
  projects: [
    {
      name: 'staging',
      use: { baseURL: 'https://staging.example.com' },
    },
    {
      name: 'prod-smoke',
      use: { baseURL: 'https://example.com' },
    },
  ],
});

// Exécution
npx playwright test --project=staging
npx playwright test --project=prod-smoke --grep '@smoke'
```

```yaml
# CI — déploiement puis test
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh staging
  e2e:
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npx playwright test --project=staging
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: e2e-report
          path: playwright-report/
```

## Parallélisation et Sharding

```bash
# Par fichiers (recommandé) — chaque worker prend un fichier
npx playwright test --workers=4

# Sharding pour CI multi-machine
npx playwright test --shard=1/4  # Machine 1
npx playwright test --shard=2/4  # Machine 2
```

```yaml
# CI Matrix Sharding
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npx playwright test --shard=${{ matrix.shard }}/4
```

## Reporting et Debug

```bash
# Rapports
npx playwright show-report      # Rapport HTML
npx playwright show-trace trace.zip  # Playwright Trace Viewer
npx playwright test --reporter=html,json,list

# Screenshots sur échec
# Config : screenshot: 'only-on-failure'
```

### Dashboard E2E (métriques à suivre)

| Métrique | Cible | Alerte |
|----------|-------|--------|
| Taux de réussite | > 99% | < 95% |
| Durée totale | < 15 min | > 30 min |
| Tests flaky (dernier run) | 0 | > 5 |
| Couverture des parcours critiques | > 90% | < 80% |

## Bonnes Pratiques

1. **10% de la suite totale** — pas plus, les E2E sont lents
2. **Nettoyer avant, pas après** — si le test échoue, le cleanup ne s'exécute pas
3. **Un seul `describe` par feature** — regrouper les scénarios par fonctionnalité
4. **Ne pas tester les états impossibles** — l'utilisateur ne peut pas cliquer sur un bouton invisible
5. **Mock des services tiers** — Stripe, Auth0, SendGrid — pas de vrais appels
6. **Tags pour la segmentation** — `@smoke`, `@regression`, `@slow`, `@prod`
7. **Tests en lecture + écriture séparés** — ne pas mélanger clean/create dans le même test

## Common Pitfalls

1. **Tout tester en E2E** — la suite devient trop lente, instable, coûteuse
2. **Pas de cleanup** — les données s'accumulent, les tests s'influencent
3. **Tests dépendants de l'ordre** — le test B suppose que le test A a créé des données
4. **Timings codés en dur** — `waitForTimeout(5000)` → brittle dès que le réseau ralentit
5. **Absence de retry** — un test qui échoue 1 fois sur 20 doit retry, pas être ignoré
6. **Screenshots non configurés** — sans capture, un échec E2E est dur à diagnostiquer

## Verification Checklist

- [ ] Les tests E2E couvrent les happy paths critiques (RICE ≥ 30)
- [ ] Aucun `sleep()` ou `waitForTimeout()` sans attente explicite
- [ ] Les données de test sont isolées (nettoyage avant chaque test)
- [ ] Les services externes sont mockés
- [ ] Screenshots/vidéos configurés sur échec
- [ ] Suite parallélisée avec sharding pour les grosses CI
- [ ] Flakyness < 5% et monitoring en place
- [ ] Ratio E2E/unitaires ≤ 10%
