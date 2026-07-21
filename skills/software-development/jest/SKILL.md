---
name: jest
description: "Tester du code JavaScript/TypeScript avec Jest — unit tests, mocks, snapshots, coverage, async, et intégration CI."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [jest, javascript, typescript, testing, unit-test, nodejs, coverage]
    related_skills: [cypress, playwright, test-driven-development]
---

# Jest — Tests JavaScript/TypeScript

## Overview

Jest est le framework de test le plus répandu pour JavaScript/TypeScript. Zero-config pour les projets React/Vue/Node, assertions intégrées, mocking puissant, snapshots, couverture de code, et mode watch.

## When to Use

- Tests unitaires et d'intégration pour du code JS/TS (Node, React, Vue, Angular, Next, Express)
- Toute tâche de test dans un projet JS/TS moderne
- Ne pas utiliser pour du testing E2E navigateur (préférer Cypress ou Playwright)

## Installation et Configuration

```bash
# Installation
npm install --save-dev jest @types/jest ts-jest

# Avec create-react-app / next / vue-cli : déjà inclus
npx jest --init
```

**Configuration `jest.config.js` :**
```js
module.exports = {
  testEnvironment: 'node',           // ou 'jsdom' pour React
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
  collectCoverageFrom: ['src/**/*.{js,jsx,ts,tsx}', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 },
  },
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
};
```

**Avec `package.json` :**
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2"
  }
}
```

## Structure des Tests

```
src/
├── utils/
│   ├── formatage.ts
│   └── __tests__/
│       └── formatage.test.ts
├── services/
│   ├── api.ts
│   └── __tests__/
│       └── api.test.ts
└── components/
    ├── Bouton.tsx
    └── __tests__/
        └── Bouton.test.tsx
```

## Assertions de Base

```typescript
import { formaterDate, calculerTVA } from '../utils/formatage';

test('formaterDate retourne JJ/MM/AAAA', () => {
  expect(formaterDate(new Date(2024, 0, 15))).toBe('15/01/2024');
});

test('calculerTVA applique 20%', () => {
  expect(calculerTVA(100)).toBe(20);
  expect(calculerTVA(0)).toBe(0);
  expect(calculerTVA(-50)).toBe(-10);
});

test('comparaison objets', () => {
  expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 2 });
  expect([1, 2, 3]).toContain(2);
  expect('hello world').toMatch(/hello/);
});

test('valeurs approchées (flottants)', () => {
  expect(0.1 + 0.2).toBeCloseTo(0.3, 5);
});
```

## Tests Asynchrones

```typescript
// Callback
test('données chargées', (done) => {
  chargerDonnees((data) => {
    expect(data).toBeDefined();
    done();
  });
});

// Promise
test('fetch utilisateur', async () => {
  const user = await fetchUtilisateur(1);
  expect(user.nom).toBe('Alice');
});

// Reject
test('erreur serveur', async () => {
  await expect(fetchUtilisateur(999)).rejects.toThrow('Not found');
});
```

## Mocks

### Mock de module

```typescript
import axios from 'axios';
import { fetchUtilisateur } from './api';

jest.mock('axios');

test('fetchUtilisateur retourne les données', async () => {
  const mockData = { id: 1, nom: 'Alice' };
  (axios.get as jest.Mock).mockResolvedValue({ data: mockData });

  const result = await fetchUtilisateur(1);
  expect(result).toEqual(mockData);
  expect(axios.get).toHaveBeenCalledWith('/api/users/1');
});

test('fetchUtilisateur gère l\'erreur réseau', async () => {
  (axios.get as jest.Mock).mockRejectedValue(new Error('Network error'));

  await expect(fetchUtilisateur(1)).rejects.toThrow('Network error');
});
```

### Mock de fonction

```typescript
test('callback appelé avec les bons args', () => {
  const mockFn = jest.fn();
  executer(mockFn);
  expect(mockFn).toHaveBeenCalledTimes(1);
  expect(mockFn).toHaveBeenCalledWith('donnée', expect.any(Number));
});
```

### Mock de timer (fake timers)

```typescript
jest.useFakeTimers();

test('setTimeout déclenché après 5s', () => {
  const callback = jest.fn();
  planifierRappel(callback, 5000);

  expect(callback).not.toHaveBeenCalled();

  jest.advanceTimersByTime(5000);
  expect(callback).toHaveBeenCalledTimes(1);
});
```

### Mock de `fetch` global

```typescript
global.fetch = jest.fn();

beforeEach(() => {
  (global.fetch as jest.Mock).mockClear();
});

test('fetchUser utilise fetch', async () => {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: true,
    json: async () => ({ id: 1, name: 'Alice' }),
  });

  const user = await fetchUser(1);
  expect(user.name).toBe('Alice');
});
```

## Tests de Snapshots (React/Vue)

```tsx
import { render } from '@testing-library/react';
import Bouton from '../Bouton';

test('Bouton rendu correctement', () => {
  const { container } = render(<Bouton label="Cliquez-moi" variant="primary" />);
  expect(container.firstChild).toMatchSnapshot();
});

// Mettre à jour : jest --updateSnapshot
```

## CI/CD Integration

**Fichier `.github/workflows/test.yml` :**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm test -- --ci --coverage --maxWorkers=2
```

**Scripts utiles :**
```bash
npm test                    # Tous les tests
npx jest --watch            # Mode watch
npx jest --coverage         # Rapport de couverture
npx jest --verbose          # Mode verbeux
npx jest --testPathPattern="utils"  # Filtrer par chemin
npx jest -t "formaterDate"  # Filtrer par nom de test
npx jest --onlyChanged      # Tests sur fichiers modifiés
```

## Common Pitfalls

1. **Tests qui passent sans assertions** — utiliser `expect.hasAssertions()` ou `--verbose` pour vérifier
2. **Snapshot trop gros** — diviser le composant, snapshot ciblé
3. **Mocks mal restaurés** — appeler `jest.clearAllMocks()` dans `beforeEach`
4. **Test asynchrone sans await** — Jest ne détecte pas toujours la promesse pendante, toujours `await` ou `done()`
5. **Config jsdom vs node** — si `document` n'existe pas, utiliser `testEnvironment: 'jsdom'`

## Verification Checklist

- [ ] `npm test` passe avec 0 erreurs, 0 warnings
- [ ] Couverture ≥ 80% (ou seuil configuré)
- [ ] Mocks restaurés entre les tests (pas de pollution inter-tests)
- [ ] Tests asynchrones utilisent `async/await` ou `done()`
- [ ] Snapshots vérifiés visuellement après `--updateSnapshot`
