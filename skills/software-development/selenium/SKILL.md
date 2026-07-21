---
name: selenium
description: "Automatisation de navigateur avec Selenium WebDriver — Java, Python, JS, WebDriverManager, Grid, Remote WebDriver, et bonnes pratiques."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [selenium, webdriver, testing, browser, automation, java, python]
    related_skills: [playwright, cypress, e2e-testing]
---

# Selenium WebDriver — Automation de Navigateur

## Overview

Selenium est le standard historique d'automatisation de navigateur Web. Supporte Chrome, Firefox, Safari, Edge — et les environnements headless. Selenium 4 apporte le support natif du Chrome DevTools Protocol (CDP), les relative locators, et une meilleure gestion des fenêtres/tabs.

## When to Use

- Tests E2E existants à maintenir (legacy)
- Grid distribuée multi-navigateur/multi-OS
- Environnements où Playwright/Cypress ne sont pas disponibles (IE11, anciens Safari)
- Scraping complexe nécessitant l'exécution de JS
- Ne pas utiliser pour : nouveaux projets greenfield — préférer Playwright (plus moderne, fiable, rapide)

## Installation

### Python (recommandé pour scraping/tests rapides)
```bash
pip install selenium webdriver-manager
```

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install())
)
```

### Java (recommandé pour tests enterprise)
```xml
<dependency>
    <groupId>org.seleniumhq.selenium</groupId>
    <artifactId>selenium-java</artifactId>
    <version>4.27.0</version>
</dependency>
<dependency>
    <groupId>io.github.bonigarcia</groupId>
    <artifactId>webdrivermanager</artifactId>
    <version>5.9.0</version>
</dependency>
```

### JavaScript
```bash
npm install selenium-webdriver
npm install -D @types/selenium-webdriver  # TypeScript
```

## Configuration

### Python — Options Chrome
```python
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.add_argument('--headless=new')  # Headless mode (Chrome 112+)
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('--disable-notifications')
options.add_argument('--lang=fr')

# Préférences utilisateur
prefs = {
    'download.default_directory': '/tmp/downloads',
    'download.prompt_for_download': False,
}
options.add_experimental_option('prefs', prefs)

# Proxy
options.add_argument('--proxy-server=http://proxy:8080')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options,
)
```

### Python — Firefox
```python
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.set_preference('intl.accept_languages', 'fr')

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options,
)
```

### Selenium Grid (Remote)
```python
from selenium import webdriver
from selenium.webdriver.common.options import Options

options = Options()
options.browser_version = 'latest'
options.platform_name = 'Linux'

driver = webdriver.Remote(
    command_executor='http://selenium-hub:4444/wd/hub',
    options=options,
)
```

## API WebDriver — Commandes Essentielles

### Navigation
```python
driver.get('https://example.com')
driver.current_url              # str
driver.title                    # str
driver.back()
driver.forward()
driver.refresh()
driver.close()                  # Ferme l'onglet courant
driver.quit()                   # Ferme complètement le navigateur
```

### Localisation d'Éléments

```python
from selenium.webdriver.common.by import By

# Stratégies de localisation
driver.find_element(By.ID, 'email')
driver.find_element(By.NAME, 'password')
driver.find_element(By.CLASS_NAME, 'btn-primary')
driver.find_element(By.TAG_NAME, 'h1')
driver.find_element(By.CSS_SELECTOR, '[data-test=submit]')
driver.find_element(By.XPATH, '//button[text()="Valider"]')
driver.find_element(By.LINK_TEXT, 'Cliquez ici')
driver.find_element(By.PARTIAL_LINK_TEXT, 'Cliquez')

# Multiples éléments
elements = driver.find_elements(By.CLASS_NAME, 'item')
len(elements)  # Nombre d'éléments trouvés
```

### Actions sur les Éléments

```python
element = driver.find_element(By.ID, 'email')
element.send_keys('user@example.com')     # Taper du texte
element.clear()                           # Effacer
element.click()                           # Cliquer
element.submit()                          # Soumettre le formulaire parent

# Attributs et propriétés
element.get_attribute('href')             # Attrbut HTML
element.text                              # Texte visible
element.is_displayed()                    # Visible ?
element.is_enabled()                      # Activé ?
element.is_selected()                     # Sélectionné (checkbox/radio)

# Valeur d'un input
element.get_attribute('value')
```

### Wait (Attentes)

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Attente explicite (toujours préférer aux sleep)
wait = WebDriverWait(driver, 10)

element = wait.until(
    EC.presence_of_element_located((By.ID, 'monElement'))
)

element = wait.until(
    EC.visibility_of_element_located((By.CLASS_NAME, 'result'))
)

element = wait.until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test=submit]'))
)

# Attendre que l'élément disparaisse
wait.until(
    EC.invisibility_of_element_located((By.ID, 'loading'))
)

# Attendre le texte
wait.until(
    EC.text_to_be_present_in_element((By.ID, 'status'), 'Terminé')
)

# Attendre une URL
wait.until(EC.url_contains('/dashboard'))

# Attendre une alerte
wait.until(EC.alert_is_present())
driver.switch_to.alert.accept()
```

### Interaction Formulaires

```python
from selenium.webdriver.support.ui import Select

# Select (dropdown)
select = Select(driver.find_element(By.ID, 'country'))
select.select_by_visible_text('France')
select.select_by_value('FR')
select.select_by_index(1)

# Checkbox/Radio
checkbox = driver.find_element(By.ID, 'accept-terms')
if not checkbox.is_selected():
    checkbox.click()

# Upload fichier
driver.find_element(By.NAME, 'file').send_keys('/home/user/document.pdf')
```

### JavaScript Execution

```python
# Exécuter JS dans la page
driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
driver.execute_script('arguments[0].scrollIntoView(true);', element)

# Retourner des données
title = driver.execute_script('return document.title')

# Manipuler le DOM
driver.execute_script("document.querySelector('#loading').remove()")

# Performance
timings = driver.execute_script("""
    return window.performance.getEntries().map(e => ({
        name: e.name,
        duration: e.duration
    }))
""")
```

### Navigation Multi-Onglets

```python
# Ouvrir un nouvel onglet
driver.switch_to.new_window('tab')
driver.get('https://autre-site.com')

# Changer d'onglet
original_window = driver.current_window_handle
for window_handle in driver.window_handles:
    if window_handle != original_window:
        driver.switch_to.window(window_handle)
        break

# Fermer l'onglet et revenir
driver.close()
driver.switch_to.window(original_window)

# Attendre qu'un nouvel onglet s'ouvre
wait.until(EC.number_of_windows_to_be(2))
driver.switch_to.window(driver.window_handles[-1])
```

### Alertes et Popups

```python
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 5)

# Attendre une alerte
alert = wait.until(EC.alert_is_present())
print(alert.text)
alert.accept()          # OK
# alert.dismiss()      # Annuler
# alert.send_keys('texte')  # Saisir dans un prompt

# Authentification de base (via URL)
driver.get('https://user:password@example.com')
```

### Captures d'écran

```python
# Pleine page
driver.save_screenshot('/tmp/screenshot.png')

# Élément spécifique
element.screenshot('/tmp/element.png')

# PDF (Chrome uniquement)
pdf_data = driver.execute_cdp_cmd('Page.printToPDF', {
    'printBackground': True,
    'format': 'A4',
})
with open('/tmp/page.pdf', 'wb') as f:
    import base64
    f.write(base64.b64decode(pdf_data['data']))
```

## Selenium 4 — Relative Locators

```python
from selenium.webdriver.support.relative_locator import locate_with

# Trouver les éléments proches
password_field = driver.find_element(By.ID, 'password')
submit_button = driver.find_element(
    locate_with(By.TAG_NAME, 'button').below(password_field)
)

# Au dessus, à gauche, à droite
login_form = driver.find_element(By.ID, 'login')
nearby = driver.find_element(
    locate_with(By.CLASS_NAME, 'help-text').to_left_of(login_form)
)
```

## Chrome DevTools Protocol (CDP) — Selenium 4

```python
import trio  # Nécessite pip install trio

async def cdp_example():
    async with driver.devtools() as devtools:
        # Intercepter les requêtes
        await devtools.send('Network.enable')
        async with devtools.event_listener('Network.requestWillBeSent') as events:
            async for event in events:
                print(f"Requête: {event['request']['url']}")

# Bloquer les images
driver.execute_cdp_cmd('Network.setBlockedURLs', {
    'urls': ['*.jpg', '*.png', '*.gif']
})
driver.execute_cdp_cmd('Network.enable', {})

# Simuler la géolocalisation
driver.execute_cdp_cmd('Emulation.setGeolocationOverride', {
    'latitude': 48.8566,
    'longitude': 2.3522,
    'accuracy': 100,
})

# Simuler l'empreinte (user-agent, résolution)
driver.execute_cdp_cmd('Emulation.setUserAgentOverride', {
    'userAgent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
    'platform': 'iPhone',
})
```

## Page Object Model (POM)

```python
# pages/login_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LoginPage:
    URL = 'https://example.com/login'

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    EMAIL_INPUT = (By.ID, 'email')
    PASSWORD_INPUT = (By.ID, 'password')
    SUBMIT_BUTTON = (By.CSS_SELECTOR, '[data-test=submit]')
    ERROR_MESSAGE = (By.CSS_SELECTOR, '[data-test=error]')

    def open(self):
        self.driver.get(self.URL)
        return self

    def login(self, email: str, password: str):
        self.driver.find_element(*self.EMAIL_INPUT).send_keys(email)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.SUBMIT_BUTTON).click()
        return self

    def get_error_message(self) -> str:
        return self.wait.until(
            EC.visibility_of_element_located(self.ERROR_MESSAGE)
        ).text


# tests/test_login.py
def test_login_success(driver):
    login_page = LoginPage(driver).open()
    login_page.login('admin@test.com', 'secret')
    wait.until(EC.url_contains('/dashboard'))

def test_login_invalid_credentials(driver):
    login_page = LoginPage(driver).open()
    login_page.login('bad@test.com', 'wrong')
    assert 'Identifiants invalides' in login_page.get_error_message()
```

## Exécution avec Pytest

```python
# conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    driver.implicitly_wait(5)
    yield driver
    driver.quit()
```

## CI/CD

```yaml
name: Selenium Tests
on: [push]
jobs:
  selenium:
    runs-on: ubuntu-latest
    services:
      selenium:
        image: selenium/standalone-chrome:latest
        ports: ['4444:4444']
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ -v --headed --hub http://localhost:4444
```

## Common Pitfalls

1. **`sleep()` au lieu de `WebDriverWait`** — toujours préférer les attentes explicites
2. **`StaleElementReferenceException`** — élément rafraîchi, re-chercher avant d'interagir
3. **Ne pas quitter le driver** — toujours appeler `driver.quit()` en fin de test (ou utiliser context manager)
4. **Sélecteurs XPath fragiles** — préférer CSS/ID/data-attributes
5. **Fenêtres/popups non gérées** — bien utiliser `switch_to.window()` / `switch_to.alert`
6. **Browser driver incompatible** — toujours utiliser WebDriverManager pour la gestion des versions

## Verification Checklist

- [ ] `WebDriverWait` utilisé systématiquement (pas de `time.sleep()`)
- [ ] `driver.quit()` appelé à la fin (ou fixture pytest avec yield)
- [ ] Page Object Model appliqué pour les pages réutilisées
- [ ] Mode headless validé pour CI
- [ ] Aucun `NoSuchElementException` non géré dans les scénarios d'erreur
