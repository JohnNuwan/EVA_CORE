---
name: cypress
description: "Tests E2E et composants avec Cypress — installation, API, custom commands, CI, mocks réseau, component testing, et bonnes pratiques."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [cypress, e2e, testing, javascript, web, component-testing, ci]
    related_skills: [playwright, selenium, jest, e2e-testing]
---

# Cypress — Tests E2E et Component Testing

## Overview

Cypress est un framework de test E2E nouvelle génération (pas basé sur Selenium). Architecture en boucle interne : le test et l'application tournent dans le même processus. Time Travel, débogage natif, captures d'écran/vidéo automatiques.

## When to Use

- Tests E2E d'applications web (React, Vue, Angular, Next.js, Nuxt)
- Tests de composants d'UI modernes
- Tests d'intégration frontend avec API mockées
- Ne pas utiliser pour : crawling/scraping lourd, tests backend purs, tests multi-onglets ou multi-domaines (Cypress ne gère qu'un seul domaine visité)

## Installation

```bash
npm install --save-dev cypress @cypress/react @cypress/vite-dev-server

# Ou npx
npx cypress install

# Ouvrir l'interface
npx cypress open

# Mode headless (CI)
npx cypress run
```

**Structure générée :**
```
cypress/
├── e2e/              # Tests E2E (.cy.js / .cy.ts)
├── component/        # Tests composants
├── fixtures/         # Données mock (JSON, images)
├── support/
│   ├── commands.ts   # Commandes personnalisées
│   └── e2e.ts        # Configuration globale E2E
└── downloads/        # Fichiers téléchargés pendant les tests
```

**Configuration `cypress.config.ts` :**
```typescript
import { defineConfig } from 'cypress';

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    video: true,
    screenshotOnRunFailure: true,
    // Exclure les appels XHR des logs (moins de bruit)
    excludeXHRInNetworkLogs: true,
    setupNodeEvents(on, config) {
      // Implémenter des tâches Node personnalisées
      on('task', {
        log(message) { console.log(message); return null; },
      });
    },
  },
  component: {
    devServer: { framework: 'react', bundler: 'vite' },
  },
  env: {
    apiUrl: 'http://localhost:4000/api',
  },
});
```

## API Cypress — Commandes Essentielles

### Navigation et Interaction

```typescript
describe('Page d\'accueil', () => {
  beforeEach(() => {
    cy.visit('/');                // Naviguer (relatif à baseUrl)
  });

  it('affiche le titre', () => {
    cy.get('h1').should('contain', 'Bienvenue');
    cy.title().should('eq', 'Mon App');
  });

  it('soumet le formulaire de connexion', () => {
    cy.get('[data-cy=email]').type('user@example.com');
    cy.get('[data-cy=password]').type('password123');
    cy.get('[data-cy=submit]').click();

    cy.url().should('include', '/dashboard');
    cy.get('[data-cy=welcome]').should('be.visible');
  });
});
```

### Sélecteurs — Toujours utiliser `data-cy`

```html
<!-- Dans le code source -->
<button data-cy="submit-btn" class="btn btn-primary">
  Valider
</button>
```

```typescript
// ✅ Recommandé : data-cy
cy.get('[data-cy=submit-btn]').click();

// ❌ Fragile : classes CSS
cy.get('.btn.btn-primary').click();

// ❌ Fragile : texte (change selon locale)
cy.contains('Valider').click();
```

### Assertions (Chaînes Should)

```typescript
cy.get('.alerte')
  .should('be.visible')
  .and('have.class', 'alerte-erreur')
  .and('contain', 'Erreur de connexion');

// État des éléments
cy.get('button').should('be.disabled');
cy.get('input').should('be.focused');
cy.get('.spinner').should('not.exist');

// Nombre d'éléments
cy.get('li').should('have.length', 5);
cy.get('li').its('length').should('be.gte', 1);
```

### Aliases et Requêtes Interdépendantes

```typescript
it('crée puis modifie un élément', () => {
  // Requête aliasée
  cy.get('[data-cy=user-list]').as('userList');
  cy.get('@userList').should('contain', 'Alice');

  // Alias de requête réseau
  cy.intercept('GET', '/api/users').as('getUsers');
  cy.wait('@getUsers').its('response.statusCode').should('eq', 200);
});
```

## Mocks et Interceptions Réseau

```typescript
it('affiche les utilisateurs depuis l\'API mockée', () => {
  cy.intercept('GET', '/api/users', {
    statusCode: 200,
    body: [
      { id: 1, name: 'Alice' },
      { id: 2, name: 'Bob' },
    ],
  }).as('getUsers');

  cy.visit('/users');
  cy.wait('@getUsers');
  cy.get('[data-cy=user-item]').should('have.length', 2);
});

it('teste la gestion d\'erreur 500', () => {
  cy.intercept('POST', '/api/login', {
    statusCode: 500,
    body: { error: 'Serveur indisponible' },
  });

  cy.get('[data-cy=email]').type('test@test.com');
  cy.get('[data-cy=password]').type('test');
  cy.get('[data-cy=submit]').click();

  cy.get('[data-cy=error-message]').should('be.visible')
    .and('contain', 'Serveur');
});

it('vérifie que l\'appel API a été envoyé', () => {
  cy.intercept('POST', '/api/login').as('loginRequest');
  // ... remplir formulaire et cliquer
  cy.wait('@loginRequest').then((interception) => {
    expect(interception.request.body).to.deep.equal({
      email: 'user@example.com',
      password: 'password123',
    });
  });
});

// Retarder ou faire échouer des requêtes
cy.intercept('GET', '/api/slow-endpoint', (req) => {
  req.reply(res => {
    res.delay(2000); // Simuler latence
    res.send({ status: 'ok' });
  });
});
```

## Tests de Composants

```typescript
import { mount } from 'cypress/react';
import Bouton from './Bouton';

it('affiche le libellé', () => {
  mount(<Bouton label="Cliquez" />);
  cy.get('button').should('contain', 'Cliquez');
});

it('émet un événement click', () => {
  const onClick = cy.spy().as('clickSpy');
  mount(<Bouton label="Go" onClick={onClick} />);
  cy.get('button').click();
  cy.get('@clickSpy').should('have.been.calledOnce');
});
```

## Commandes Personnalisées

```typescript
// cypress/support/commands.ts

// Réutilisable : se connecter
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('[data-cy=email]').type(email);
    cy.get('[data-cy=password]').type(password);
    cy.get('[data-cy=submit]').click();
    cy.url().should('contain', '/dashboard');
  });
});

// Utilisation dans les tests
beforeEach(() => {
  cy.login('admin@test.com', 'secret');
});
```

## Plugins et Tasks

```typescript
// cypress.config.ts — task personnalisée pour lire un fichier
import { defineConfig } from 'cypress';
import * as fs from 'fs';

export default defineConfig({
  e2e: {
    setupNodeEvents(on) {
      on('task', {
        readFileMaybe(filename) {
          if (fs.existsSync(filename)) {
            return fs.readFileSync(filename, 'utf8');
          }
          return null;
        },
      });
    },
  },
});
```

## CI/CD — GitHub Actions

```yaml
name: Cypress Tests
on: [push]
jobs:
  cypress-run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - uses: cypress-io/github-action@v6
        with:
          build: npm run build
          start: npm start
          wait-on: 'http://localhost:3000'
          browser: chrome
          record: true       # Nécessite Cypress Cloud (Dashboard)
      - uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: cypress-screenshots
          path: cypress/screenshots
```

```bash
# CLI
npx cypress run --browser chrome --headed --spec 'cypress/e2e/**/*.cy.ts'
npx cypress run --record --key <record-key>   # Cypress Cloud
npx cypress run --parallel                     # Parallélisation dans le Cloud
```

## Bonnes Pratiques

1. **Utiliser `data-cy`** plutôt que CSS/texte pour les sélecteurs
2. **`cy.session()` pour le login** — met en cache le cookie/session entre tests
3. **Un test = un comportement** — pas de longs scénarios tout-en-un
4. **Intercepter les appels API** — ne pas dépendre d'un backend réel en CI
5. **Ne pas chaîner plus de 5-7 commandes** — extraire en commande personnalisée
6. **Éviter `cy.wait(ms)`** — préférer `cy.wait('@alias')` ou assertions
7. **Tester ce que l'utilisateur voit** — pas l'implémentation interne

## Common Pitfalls

1. **Tests qui échouent sur CI mais pas en local** — souvent un timeout (`defaultCommandTimeout: 10000`)
2. **`cy.visit()` sans `baseUrl`** — fournir l'URL complète ou configurer `baseUrl`
3. **Mélanger tests E2E et composants** — deux dossiers séparés (`e2e/` et `component/`)
4. **Sélecteurs trop larges** — `cy.get('div')` attrape trop d'éléments, être spécifique
5. **Ignorer les requêtes non interceptées** — `cy.intercept('GET', '/api/**', ...).as('every')`

## Verification Checklist

- [ ] `npx cypress run` passe en mode headless
- [ ] Tous les sélecteurs utilisent `data-cy`
- [ ] Aucun `cy.wait(ms)` sans raison valide
- [ ] Screenshots uniquement sur échec (ou explicitement demandés)
- [ ] Les appels API sont interceptés (pas de dépendance externe en CI)
- [ ] Le login est mis en cache via `cy.session()`
