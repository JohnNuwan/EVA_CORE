---
title: Accessibilité Web — WCAG 2.2 & ARIA
description: Accessibilité web — WCAG 2.2 niveaux A/AA/AAA, ARIA, navigation clavier, contrastes, lecteurs d'écran, tests automatisés, semantic HTML
category: creative
author: E.V.A
tags: [accessibilite, wcag, aria, a11y, contraste, lecteur-ecran, keyboard-navigation, semantic-html]
version: 1.0
---

# Accessibilité Web — WCAG 2.2 & ARIA

## Principes Fondamentaux (POUR)

WCAG 2.2 repose sur 4 principes :

| Principe | Description |
|----------|-------------|
| **P**erceivable | L'utilisateur doit pouvoir percevoir l'information |
| **O**perable | L'utilisateur doit pouvoir interagir |
| **U**nderstandable | L'utilisateur doit pouvoir comprendre |
| **R**obust | Le contenu doit fonctionner sur tous les outils |

## Niveaux de Conformité

```yaml
Niveau A (Minimum):
  - 30 critères indispensables
  - Alternatives textuelles, navigation clavier
  - Obligatoire légal dans beaucoup de pays

Niveau AA (Recommandé):
  - 20 critères supplémentaires
  - Contraste 4.5:1, focus visible
  - Standard cible pour la plupart des projets
  - Obligatoire RGAA en France

Niveau AAA (Excellence):
  - 28 critères supplémentaires
  - Contraste 7:1, langue des signes
  - Ideal mais pas toujours réalisable
```

## Critères WCAG 2.2 Essentiels

### 1. Perceivable

#### 1.1.1 Non-text Content (A)
```html
<!-- Image décorative → alt vide -->
<img src="decoration.jpg" alt="" role="presentation">

<!-- Image informative → alt descriptif -->
<img src="chart.png" alt="Graphique montrant +15% de ventes en Q3">

<!-- Image lien → alt décrit la destination -->
<a href="/download">
  <img src="icon-download.png" alt="Télécharger le rapport PDF">
</a>
```

#### 1.4.1 Use of Color (A)
```css
/* Ne PAS utiliser la couleur seule pour transmettre une info */
.error { color: red; }  /* ❌ Illisible pour daltoniens */

/* ✅ Ajouter un symbole ou texte */
.error { color: red; }
.error::before { content: "⚠️ "; }
```

#### 1.4.3 Contrast Minimum (AA)
```yaml
Ratio minimum:
  Text normal (<18px ou <14px bold): 4.5:1
  Text large (≥18px ou ≥14px bold): 3:1
  UI components: 3:1
  Logos: exemptés
  Text décoratif: exempté
```

### 2. Operable

#### 2.1.1 Keyboard (A)
```jsx
// Tous les éléments interactifs doivent être accessibles au clavier
<div onClick={handleClick} role="button" tabIndex={0}
     onKeyDown={(e) => e.key === 'Enter' && handleClick()}>
  Cliquer
</div>

// ✅ Mieux : utiliser un <button> natif
<button onClick={handleClick}>Cliquer</button>
```

#### 2.4.7 Focus Visible (AA)
```css
/* Focus ring visible obligatoire */
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* Ne JAMAIS faire */
:focus { outline: none; }  /* ❌ Inaccessible */

/* ✅ OK si remplacé par un style visible */
:focus:not(:focus-visible) { outline: none; }
:focus-visible { outline: 2px solid blue; }
```

#### 2.4.11 Focus Not Obscured (AA - Nouveau WCAG 2.2)
Le focus ne doit pas être caché par d'autres éléments (sticky headers, modals...).

### 3. Understandable

#### 3.3.2 Labels or Instructions (A)
```html
<!-- Chaque champ doit avoir un label -->
<label for="email">Adresse email</label>
<input id="email" type="email" required>

<!-- Alternative avec aria-label -->
<input aria-label="Rechercher" type="search">

<!-- Placeholder ne suffit PAS -->
<input placeholder="Email">  <!-- ❌ Disparaît à la saisie -->
```

#### 3.3.4 Error Prevention (AA)
```html
<!-- Messages d'erreur clairs et liés au champ -->
<label for="password">Mot de passe</label>
<input id="password" type="password" required
       aria-describedby="password-error"
       aria-invalid="true">
<span id="password-error" role="alert">
  Le mot de passe doit contenir au moins 8 caractères
</span>
```

### 4. Robust

#### 4.1.2 Name, Role, Value (A)
```html
<!-- Composant custom doit exposer name, role, value -->
<div role="slider" aria-valuemin="0" aria-valuemax="100"
     aria-valuenow="50" tabindex="0">
  Volume: 50%
</div>
```

## ARIA (Accessible Rich Internet Applications)

### Règles d'or ARIA
```yaml
1. Ne pas utiliser ARIA si un élément HTML natif existe
   ❌ <div role="button"> → ✅ <button>
2. Ne pas altérer la sémantique native
   ❌ <h1 role="button"> → utiliser <button> avec aria-label
3. Tous les éléments interactifs ARIA doivent être keyboard-accessible
4. role="presentation" ou aria-hidden="true" uniquement pour décoratif
5. Tester avec un vrai lecteur d'écran
```

### Rôles ARIA
```yaml
Landmarks (navigation):
  role="banner"        → <header> (site)
  role="navigation"    → <nav>
  role="main"          → <main>
  role="complementary" → <aside>
  role="contentinfo"   → <footer> (site)

Widgets:
  role="button"        → Actions déclenchables
  role="tab"           → Onglets
  role="tabpanel"      → Panneau d'onglet
  role="dialog"        → Modale
  role="alertdialog"   → Alerte critique
  role="progressbar"   → Progression
  role="slider"        → Curseur
  role="switch"        → Toggle
```

### Propriétés ARIA
```yaml
States:
  aria-expanded="true/false"      → Menu déroulant
  aria-pressed="true/false"       → Toggle button
  aria-selected="true/false"      → Tab sélectionné
  aria-disabled="true/false"      → Élément désactivé
  aria-hidden="true/false"        → Cacher du lecteur d'écran
  aria-busy="true/false"          → Chargement en cours

Relations:
  aria-labelledby="id"            → Label par un autre élément
  aria-describedby="id"           → Description
  aria-controls="id"              → Contrôle un autre élément
  aria-owns="id"                  → Parenté explicite
  aria-flowto="id"                → Ordre de lecture alternatif

Live Regions:
  aria-live="polite"              → Message non urgent
  aria-live="assertive"           → Message urgent
  role="alert"                    → Message d'erreur
  aria-atomic="true/false"        → Lire tout ou partie
```

### Pattern : Modale accessible
```html
<div role="dialog" aria-modal="true"
     aria-labelledby="modal-title"
     aria-describedby="modal-desc">
  <h2 id="modal-title">Confirmer la suppression</h2>
  <p id="modal-desc">Cette action est irréversible.</p>
  <button>Annuler</button>
  <button>Confirmer</button>
</div>
```

```js
// Focus trap pour la modale
const handleKeyDown = (e) => {
  if (e.key === 'Escape') closeModal();
  if (e.key === 'Tab') trapFocus(e);
};
```

## Navigation Clavier

### Ordre de navigation naturel
```yaml
Tab:      Élément suivant (focusable)
Shift+Tab: Élément précédent
Enter:    Activer un lien/bouton
Space:    Activer, cocher, scroll
Escape:   Fermer (modale, menu, dropdown)
Arrow:    Navigation dans un groupe (tabs, select, menu)
Home/End: Premier/dernier élément d'une liste
```

### Tabindex
```html
<!-- Ordre naturel (recommandé) -->
<input tabindex="0">   <!-- Ordre DOM normal -->
<button tabindex="0">  <!-- Ordre DOM normal -->

<!-- À éviter -->
<input tabindex="1">   <!-- ❌ Ordre personnalisé fragile -->
<button tabindex="5">  <!-- ❌ -->

<!-- Rendre focusable un élément non-interactif -->
<div tabindex="0" role="button">Click</div>

<!-- Enlever du tab order -->
<div tabindex="-1">    <!-- Accessible via JS mais pas Tab -->
```

### Skip Link
```html
<!-- Lien d'évitement — premier élément focusable -->
<a href="#main-content" class="skip-link">
  Aller au contenu principal
</a>

<style>
.skip-link {
  position: absolute;
  top: -40px;  /* Caché par défaut */
}
.skip-link:focus {
  top: 0;      /* Visible au focus */
}
</style>
```

## Couleurs et Contraste

### Calcul du ratio de contraste
```javascript
function getContrastRatio(hex1, hex2) {
  const luminance = (hex) => {
    const [r, g, b] = hex.match(/[A-Fa-f0-9]{2}/g).map(c => {
      const v = parseInt(c, 16) / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };
  const L1 = luminance(hex1);
  const L2 = luminance(hex2);
  const lighter = Math.max(L1, L2);
  const darker = Math.min(L1, L2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

### Palette accessible (exemple)
```yaml
Text sur fond clair:
  Fond: #FFFFFF (L=1.0)
  Text: #1A1A1A → ratio 15.3:1 ✅
  Text: #595959 → ratio 7.0:1 ✅ (AAA)
  Text: #767676 → ratio 4.5:1 ✅ (AA)
  Text: #999999 → ratio 2.8:1 ❌

Text sur fond bleu:
  Fond: #0066FF (L=0.14)
  Text: #FFFFFF → ratio 5.5:1 ✅ (AA)
  Text: #E6F0FF → ratio 3.8:1 ❌ (AA échoué)
```

## Lecteurs d'écran

### Principaux
| Lecteur | Plateforme | Notes |
|---------|------------|-------|
| **NVDA** | Windows | Gratuit, open-source, ~30% usage |
| **JAWS** | Windows | Commercial, ~40% usage |
| **VoiceOver** | macOS/iOS | Intégré, ~10% usage |
| **TalkBack** | Android | Intégré |
| **Orca** | Linux | Intégré Gnome |

### Commandes de test
```yaml
VoiceOver (macOS):
  Cmd+F5:   Activer/désactiver
  Ctrl+Option+A:  Lire la page
  Ctrl+Option+Space:  Activer élément
  Ctrl+Option+Flèches:  Naviguer

NVDA (Windows):
  Ins+Space:  Mode navigation
  Ins+F7:     Liste des éléments
  Flèches:    Naviguer
  Enter:      Activer
```

## Tests Automatisés

### axe-core (Deque)
```js
// npm install @axe-core/playwright
import { injectAxe, checkA11y } from '@axe-core/playwright';

test('page should have no violations', async ({ page }) => {
  await page.goto('/');
  await injectAxe(page);
  const results = await checkA11y(page);
  expect(results.violations.length).toBe(0);
});
```

### Lighthouse CI
```bash
# lighthouse-ci
npx lhci autorun --collect.url=http://localhost:3000
```

### Pa11y CI
```yaml
# .pa11yci
{
  "defaults": {
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"]
  },
  "urls": [
    "http://localhost:3000/",
    "http://localhost:3000/search",
    "http://localhost:3000/checkout"
  ]
}
```

## HTML Sémantique

### Structure de page
```html
<header role="banner">
  <nav aria-label="Navigation principale">
    <ul>
      <li><a href="/">Accueil</a></li>
      <li><a href="/products">Produits</a></li>
    </ul>
  </nav>
</header>

<main>
  <h1>Titre de la page</h1>
  <section aria-labelledby="section-title">
    <h2 id="section-title">Section</h2>
    <article>
      <h3>Article</h3>
      <p>Contenu...</p>
    </article>
  </section>
</main>

<footer role="contentinfo">
  <p>&copy; 2026 Company</p>
</footer>
```

### Contenu masqué accessible
```css
/* Visually hidden — accessible aux lecteurs d'écran */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Pièges
- ⚠️ `outline: none` sans alternative → invisible pour keyboard users
- ⚠️ Placeholder comme seul label → disparaît à la saisie
- ⚠️ Contraste 4.5:1 minimum oublié sur les états hover/active
- ⚠️ Modale sans focus trap → focus piégé derrière
- ⚠️ `aria-hidden="true"` sur un parent → tous les enfants invisibles aux lecteurs
- ⚠️ `role="alert"` sur un élément déjà présent → pas annoncé
- ⚠️ Couleur seule pour indiquer erreur → inaccessible aux daltoniens
- ⚠️ Images décoratives sans `alt=""` → lues par le lecteur d'écran
- ⚠️ Lien "Cliquez ici" → pas descriptif hors contexte
- ⚠️ Tableaux sans `<th>` et `scope` → pas navigables aux lecteurs d'écran