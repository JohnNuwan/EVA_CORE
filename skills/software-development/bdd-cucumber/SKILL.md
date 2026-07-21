---
name: bdd-cucumber
description: "Behavior-Driven Development avec Cucumber et Gherkin — syntaxe Given/When/Then, step definitions, hooks, rapports, et intégration Playwright/Selenium/pytest."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [bdd, cucumber, gherkin, testing, behavior-driven-development, acceptance-testing]
    related_skills: [playwright, selenium, test-driven-development, integration-testing]
---

# BDD — Behavior-Driven Development avec Cucumber & Gherkin

## Overview

Le BDD (Behavior-Driven Development) comble le fossé entre spécifications métier et tests automatisés. Avec le langage Gherkin (Given/When/Then/And/But), les scénarios deviennent lisibles par les non-techniciens tout en étant directement exécutables par Cucumber.

## When to Use

- Projets où les tests doivent être **lisibles par les PO, testeurs, clients**
- **Critères d'acceptation formalisés** en langage naturel
- **Tests de régression** documentés comme spécifications vivantes
- **Documentation vivante** — la spec = le test
- Ne pas utiliser pour : tests unitaires purs, tests d'API simples, projets solo sans interlocuteur métier

## Architecture du BDD

```
┌─────────────────────────────────────────────────────┐
│  Feature File (.feature)          ← Spec métier      │
│  "Given un utilisateur connecté"                     │
│     ↓                                                 │
│  Step Definitions (Python/JS/Java)  ← Code glue      │
│  @Given("un utilisateur connecté")                    │
│     ↓                                                 │
│  Code applicatif / API / Navigateur  ← Infrastructure│
└─────────────────────────────────────────────────────┘
```

## Gherkin — Syntaxe

### Structure de base

```gherkin
# language: fr
Fonctionnalité: Connexion utilisateur
  En tant qu'utilisateur
  Je veux me connecter à mon compte
  Afin d'accéder à mon tableau de bord

  Contexte:
    Étant donné un utilisateur existant "alice@example.com"
    Et son mot de passe "secret"

  Scénario: Connexion réussie
    Quand je me connecte avec "alice@example.com" et "secret"
    Alors je suis redirigé vers le tableau de bord
    Et je vois "Bienvenue Alice"

  Scénario: Mot de passe incorrect
    Quand je me connecte avec "alice@example.com" et "wrong"
    Alors je vois un message d'erreur "Identifiants invalides"
```

### Tableaux et exemples

```gherkin
Scénario: Inscription avec plusieurs rôles
  Quand je crée un utilisateur avec les informations suivantes:
    | champ   | valeur              |
    | nom     | Alice               |
    | email   | alice@example.com   |
    | rôle    | administrateur      |
  Alors l'utilisateur a le rôle "administrateur"

# Scenario Outline (Data-Driven)
Scénario: Calcul du montant TVA
  Soit un produit au prix de <prix_ht> €
  Quand j'applique la TVA à <taux>%
  Alors le montant TTC est <montant_ttc> €

  Exemples:
    | prix_ht | taux | montant_ttc |
    | 100     | 20   | 120.00      |
    | 50      | 10   | 55.00       |
    | 200     | 5.5  | 211.00      |
```

### Tags

```gherkin
@smoke @connexion
Fonctionnalité: Connexion
  ...

@régression
Scénario: Connexion avec email invalide
  ...

# Exécution sélective
# cucumber --tags "@smoke"
# cucumber --tags "@connexion and not @lent"
```

## Cucumber avec Python (behave/pytest-bdd)

### Installation

```bash
# Option 1 — behave
pip install behave behave-html-formatter

# Option 2 — pytest-bdd (intégration pytest)
pip install pytest-bdd
```

### behave — Structure

```
features/
├── login.feature
├── steps/
│   └── login_steps.py
└── environment.py         # Hooks (before/after)
```

### Step Definitions (behave)

```python
# features/steps/login_steps.py
from behave import given, when, then, use_step_matcher
from selenium import webdriver
from selenium.webdriver.common.by import By

@given('un utilisateur existant "{email}"')
def step_impl(context, email):
    """Préparer l'utilisateur en base de test."""
    context.email = email
    context.driver = webdriver.Chrome()
    context.driver.get('https://example.com')

@given('son mot de passe "{password}"')
def step_impl(context, password):
    context.password = password

@when('je me connecte avec "{email}" et "{password}"')
def step_impl(context, email, password):
    context.driver.find_element(By.ID, 'email').send_keys(email)
    context.driver.find_element(By.ID, 'password').send_keys(password)
    context.driver.find_element(By.ID, 'submit').click()

@then('je suis redirigé vers le tableau de bord')
def step_impl(context):
    assert '/dashboard' in context.driver.current_url

@then('je vois "{message}"')
def step_impl(context, message):
    assert message in context.driver.page_source
```

### Hooks (behave environment.py)

```python
# features/environment.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def before_all(context):
    """Exécuté avant tous les scénarios."""
    context.config.setup_logging()

def before_scenario(context, scenario):
    """Exécuté avant chaque scénario."""
    options = Options()
    options.add_argument('--headless=new')
    context.driver = webdriver.Chrome(options=options)

def after_scenario(context, scenario):
    """Exécuté après chaque scénario."""
    if scenario.status == 'failed':
        context.driver.save_screenshot(f'reports/{scenario.name}.png')
    context.driver.quit()

def after_step(context, step):
    """Exécuté après chaque step."""
    if step.status == 'failed':
        print(f"  ⛔ Échec: {step.name}")
```

### pytest-bdd (intégration pytest)

```python
# tests/test_login.py
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from selenium import webdriver

# Lier le fichier feature
scenarios('features/login.feature')

@pytest.fixture
def browser():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@given(parsers.parse('un utilisateur existant "{email}"'))
def user_exists(browser, email):
    # Créer l'utilisateur en base
    pass

@when(parsers.parse('je me connecte avec "{email}" et "{password}"'))
def login(browser, email, password):
    browser.get('https://example.com/login')
    browser.find_element(By.ID, 'email').send_keys(email)
    browser.find_element(By.ID, 'password').send_keys(password)
    browser.find_element(By.ID, 'submit').click()

@then(parsers.parse('je suis redirigé vers le tableau de bord'))
def check_dashboard(browser):
    assert '/dashboard' in browser.current_url
```

## Cucumber avec JavaScript

### Installation

```bash
npm install --save-dev @cucumber/cucumber @cucumber/cucumber-expressions
```

### Step Definitions

```typescript
// features/step_definitions/login.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from '@playwright/test';
import { Page } from '@playwright/test';

Given('un utilisateur existant {string}', async function (email: string) {
  this.email = email;
  // this.page est partagée via World
});

When('je me connecte avec {string} et {string}', async function (email: string, password: string) {
  await this.page.goto('/login');
  await this.page.fill('#email', email);
  await this.page.fill('#password', password);
  await this.page.click('#submit');
});

Then('je suis redirigé vers le tableau de bord', async function () {
  await expect(this.page).toHaveURL(/\/dashboard/);
});

Then('je vois {string}', async function (message: string) {
  await expect(this.page.locator('body')).toContainText(message);
});
```

### Custom World

```typescript
// features/support/world.ts
import { setWorldConstructor, World } from '@cucumber/cucumber';
import { Browser, Page, chromium } from '@playwright/test';

interface CustomWorld extends World {
  page: Page;
  browser: Browser;
  email: string;
}

class TestWorld extends World implements CustomWorld {
  page!: Page;
  browser!: Browser;
  email = '';
}

setWorldConstructor(TestWorld);
```

### Hooks

```typescript
// features/support/hooks.ts
import { Before, After, BeforeAll, AfterAll } from '@cucumber/cucumber';
import { chromium } from '@playwright/test';

let browser: Browser;

BeforeAll(async () => {
  browser = await chromium.launch({ headless: true });
});

Before(async function () {
  this.browser = browser;
  this.page = await browser.newPage();
});

After(async function (scenario) {
  if (scenario.result?.status === 'FAILED') {
    await this.page.screenshot({
      path: `reports/screenshots/${scenario.pickle.name}.png`,
    });
  }
  await this.page.close();
});

AfterAll(async () => {
  await browser.close();
});
```

## Cucumber avec Java (JUnit 5 + Spring)

```xml
<dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-java</artifactId>
    <version>7.20.0</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>io.cucumber</groupId>
    <artifactId>cucumber-junit-platform-engine</artifactId>
    <version>7.20.0</version>
    <scope>test</scope>
</dependency>
```

```java
import io.cucumber.java.fr.*;
import org.openqa.selenium.*;
import org.springframework.beans.factory.annotation.Autowired;

public class LoginSteps {

    @Autowired
    private WebDriver driver;

    @Étantdonné("un utilisateur existant {string}")
    public void unUtilisateurExistant(String email) {
        // Création en base
    }

    @Quand("je me connecte avec {string} et {string}")
    public void connexion(String email, String password) {
        driver.findElement(By.id("email")).sendKeys(email);
        driver.findElement(By.id("password")).sendKeys(password);
        driver.findElement(By.id("submit")).click();
    }

    @Alors("je suis redirigé vers le tableau de bord")
    public void verificationDashboard() {
        assert driver.getCurrentUrl().contains("/dashboard");
    }
}
```

## Rapports

```bash
# behave — rapport HTML
behave -f html -o reports/rapport.html

# cucumber-js — rapports
npx cucumber-js --format json:reports/cucumber-report.json
npx cucumber-js --format @cucumber/pretty-formatter

# Cucumber JVM — rapports intégrés
# Voir : https://reports.cucumber.io
```

## Bonnes Pratiques

1. **Un scénario = un comportement** — pas de longs scénarios de 15 étapes
2. **Langage métier** — pas de termes techniques (CSS, API, DB) dans les .feature
3. **Contexte partagé** — `Background` / `Contexte:` pour les préconditions communes
4. **Données de test explicites** — utiliser les tableaux Gherkin plutôt que des fixtures cachées
5. **Éviter de chaîner les scénarios** — chaque scénario doit être indépendant
6. **Ne pas tester les détails d'implémentation** — tester le comportement visible
7. **Tags pour l'organisation** — `@smoke`, `@régression`, `@lent`, `@wip`

## Common Pitfalls

1. **Steps trop génériques** — `je clique sur un bouton` ne veut rien dire, préciser `@when('je clique sur le bouton "Valider"')`
2. **Logique conditionnelle dans les .feature** — Gherkin n'a pas de if/else, créer des scénarios séparés
3. **Maintenance lourde** — trop de scénarios identiques avec des données différentes → utiliser Scenario Outline
4. **Expressions régulières fragiles** — préférer les paramètres nommés `{string}` aux regex custom
5. **Partage d'état via variables globales** — utiliser le Context/World Pattern

## Verification Checklist

- [ ] Les fichiers `.feature` sont lisibles par un non-technicien
- [ ] Chaque `Given/When/Then` a une step definition correspondante
- [ ] Les scénarios Outline utilisent des exemples représentatifs
- [ ] Contexte partagé via `Background` (pas de duplication)
- [ ] `before_scenario` réinitialise l'état (pas de pollution inter-scénarios)
- [ ] Screenshots générés sur échec
