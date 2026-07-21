---
name: playwright
description: "Tests cross-navigateur et automation avec Playwright — Chromium, Firefox, WebKit, API, fixtures, Component Testing, Codegen, et CI."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [playwright, e2e, testing, browser, automation, chromium, firefox, webkit]
    related_skills: [cypress, selenium, e2e-testing, integration-testing]
---

# Playwright — Tests Cross-Navigateur

## Overview

Playwright (Microsoft) est un framework d'automation navigateur multi-navigateur (Chromium, Firefox, WebKit). Une seule API pour les 3 moteurs, support natif des shadow DOM, des iframes, des popups, des téléchargements, des network intercepts, et des screenshots/vidéos.

## When to Use

- Tests E2E cross-navigateur (Chromium + Firefox + WebKit)
- Automatisation de tâches navigateur (scraping, screenshots, PDF)
- Tests de composants (React, Vue, Svelte, Solid)
- Tests d'API + UI dans le même framework
- Ne pas utiliser pour : tests purement backend, tests mobiles natifs (utiliser Appium/Detox)

## Installation

```bash
npm init playwright@latest
# ou
npm install --save-dev @playwright/test
npx playwright install
npx playwright install-deps    # Dépendances système (Linux)
```

**Structure :**
```
e2e/
├── playwright.config.ts
├── tests/
│   ├── login.spec.ts
│   └── dashboard.spec.ts
├── fixtures/
│   └── test-data.ts
└── utils/
    └── helpers.ts
```

## Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results.json' }],
    ['list'],
  ],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',          // Trace Playwright si échec
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 14'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120000,
  },
});
```

## Écrire des Tests

```typescript
import { test, expect } from '@playwright/test';

test('affiche la page d\'accueil', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/Mon App/);
  await expect(page.locator('h1')).toContainText('Bienvenue');
});

test('connexion réussie', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-test=email]', 'user@example.com');
  await page.fill('[data-test=password]', 'secret123');
  await page.click('[data-test=submit]');

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.locator('[data-test=welcome]')).toBeVisible();
});

test('vérifie message d\'erreur connexion', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[data-test=email]', 'wrong@test.com');
  await page.fill('[data-test=password]', 'bad');
  await page.click('[data-test=submit]');

  await expect(page.locator('[data-test=error]')).toBeVisible();
  await expect(page.locator('[data-test=error]')).toContainText('Identifiants invalides');
});
```

## Sélecteurs

```typescript
// CSS et texte (combinés)
page.locator('button:has-text("Valider")');
page.locator('[data-test=submit]');

// Sélecteur texte uniquement
page.getByText('Bienvenue');
page.getByRole('button', { name: 'Valider' });
page.getByLabel('Email');
page.getByPlaceholder('Entrez votre email');
page.getByTestId('submit-btn');        // data-testid

// Sélécteurs par rôle ARIA (recommandé)
await page.getByRole('heading', { name: 'Mon Profil' }).click();
await page.getByRole('button', { name: 'Sauvegarder' }).click();

// Chaînage et filtrage
page.locator('.user-list').filter({ hasText: 'Alice' }).locator('.edit-btn');

// Attendre un élément
await page.waitForSelector('[data-test=loading]');
await page.waitForFunction(() => !document.querySelector('.spinner'));
```

## Actions

```typescript
// Types
await page.fill('input#email', 'user@test.com');
await page.type('input#name', 'Alice', { delay: 50 });  // Tape lettre par lettre

// Clics
await page.click('button#submit');
await page.dblclick('.item');
await page.click('.menu-item', { button: 'right' });

// Checkbox / Select / Radio
await page.check('#accept-terms');
await page.selectOption('#country', 'FR');
await page.selectOption('#country', { label: 'France', value: 'FR' });

// Upload
await page.setInputFiles('input[type=file]', 'path/to/file.pdf');
await page.setInputFiles('input[type=file]', []); // Effacer

// Scroll
await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
await page.locator('#submit').scrollIntoViewIfNeeded();
```

## Assertions

```typescript
// Assertions auto-retrying (réessayent jusqu'à timeout)
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle(/Mon App/);
await expect(page.locator('h1')).toHaveText('Bienvenue');
await expect(page.locator('.alerte')).toBeVisible();
await expect(page.locator('#loading')).toBeHidden();
await expect(page.locator('button')).toBeEnabled();
await expect(page.locator('input')).toHaveValue('test');
await expect(page.locator('li')).toHaveCount(5);
await expect(page.locator('table')).toContainText('Alice');

// Négation
await expect(page.locator('.error')).not.toBeVisible();
```

## Interception Réseau

```typescript
// Bloquer ressources inutiles (accélère les tests)
test.use({
  blockURLs: ['*.google-analytics.com', '*.doubleclick.net'],
});

// Mocker une API
test('utilisateurs mockés', async ({ page }) => {
  await page.route('**/api/users', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ]),
    });
  });
  await page.goto('/users');
  await expect(page.locator('.user-card')).toHaveCount(2);
});

// Attendre une requête
test('attend la fin du chargement', async ({ page }) => {
  const responsePromise = page.waitForResponse('**/api/data');
  await page.click('[data-test=load]');
  const response = await responsePromise;
  expect(response.status()).toBe(200);
});

// Simuler des erreurs réseau
await page.route('**/api/paiement', async (route) => {
  await route.abort('connectionrefused');
});
```

## Tests API (sans navigateur)

```typescript
import { test, expect } from '@playwright/test';

test('API santé', async ({ request }) => {
  const response = await request.get('http://localhost:4000/api/health');
  expect(response.status()).toBe(200);
  expect(await response.json()).toEqual({ status: 'ok' });
});

test('créer un utilisateur', async ({ request }) => {
  const response = await request.post('http://localhost:4000/api/users', {
    data: { name: 'Alice', email: 'alice@test.com' },
  });
  expect(response.status()).toBe(201);
  const body = await response.json();
  expect(body.id).toBeDefined();
});
```

## Fixtures Personnalisées

```typescript
// e2e/fixtures/myFixtures.ts
import { test as base, expect } from '@playwright/test';

type MyFixtures = {
  authPage: any; // Page déjà connectée
};

export const test = base.extend<MyFixtures>({
  authPage: async ({ page }, use) => {
    await page.goto('/login');
    await page.fill('[data-test=email]', 'admin@test.com');
    await page.fill('[data-test=password]', 'admin123');
    await page.click('[data-test=submit]');
    await page.waitForURL('/dashboard');
    await use(page);
  },
});

export { expect };
```

## Trace Viewer et Débogage

```bash
# Lancer le viewer de trace après exécution
npx playwright show-report   # Rapport HTML
npx playwright show-trace trace.zip  # Trace détaillée

# Mode débogage (inspector)
npx playwright test --debug
PWDEBUG=1 npx playwright test

# UI mode (explorateur de tests interactif)
npx playwright test --ui
```

## Codegen (Génération de Tests)

```bash
# Ouvrir le navigateur et enregistrer les actions
npx playwright codegen http://localhost:3000
npx playwright codegen --viewport-size=390,844 http://localhost:3000  # Mobile
```

## Test Mobile et Emulation

```typescript
test.use({ ...devices['iPhone 14'] });
test.use({
  viewport: { width: 390, height: 844 },
  isMobile: true,
  userAgent: 'Mozilla/5.0 (iPhone; ...)',
});
```

## Parallélisation

```typescript
// playwright.config.ts
export default defineConfig({
  fullyParallel: true,     // Tous les fichiers en parallèle
  workers: 4,              // 4 workers simultanés
  // workers: '50%'        // 50% des CPU
});
```

```bash
npx playwright test --workers=6
npx playwright test --shard=1/3  # Sharding pour CI multi-machine
```

## CI/CD

```yaml
name: Playwright Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        project: [chromium, firefox, webkit]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npx playwright install --with-deps
      - run: npx playwright test --project=${{ matrix.project }}
      - uses: actions/upload-artifact@v4
        if: ${{ !cancelled() }}
        with:
          name: playwright-report-${{ matrix.project }}
          path: playwright-report/
          retention-days: 30
```

## Common Pitfalls

1. **Tests flaky sur CI** — ajouter `retries: 2` et toujours garder les traces sur échec
2. **Oubli de `await`** — Playwright lance l'action et continue, sans `await` le test part avant la fin
3. **Sélecteurs fragiles** — préférer `getByRole()`, `getByTestId()` aux sélecteurs CSS profonds
4. **Pas assez de timeout dans webServer** — certains builds prennent > 60s
5. **Bloquer les analytics/tiers** — accélère les tests ×2

## Verification Checklist

- [ ] `npx playwright test` passe sur Chromium + Firefox + WebKit
- [ ] Pas de tests flaky (retries = 0 sur 3 runs consécutives)
- [ ] Traces et screenshots générés uniquement sur échec
- [ ] Routes API mockées (pas de dépendance externe)
- [ ] Tests parallélisés (sans conflits d'état partagé)
