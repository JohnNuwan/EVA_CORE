---
title: Design Systems — Architecture & implémentation
description: Design systems — tokens, composants, documentation, Storybook, Figma ↔ code, versioning, gouvernance, testing
category: creative
author: E.V.A
tags: [design-system, design-tokens, storybook, figma, composants, documentation, specs, gouvernance]
version: 1.0
---

# Design Systems — Architecture & Implémentation

## Qu'est-ce qu'un Design System ?

Un design system est un ensemble cohérent de **règles**, **composants**, **tokens** et **patterns** qui garantissent la cohérence visuelle et fonctionnelle à travers tous les produits d'une organisation.

### Anatomie
```
Design System
├── Foundations (Design Tokens)
│   ├── Couleurs (primaires, neutres, sémantiques)
│   ├── Typographie (familles, échelles, poids)
│   ├── Espacements (4px grid, 8px grid)
│   ├── Ombres (élévation, focus)
│   ├── Rayons (borders, radius)
│   └── Animations (durées, easings)
├── Components
│   ├── Atomes (Button, Input, Icon, Label)
│   ├── Molécules (TextField, Card, Modal)
│   └── Organismes (Header, Sidebar, DataTable)
├── Patterns
│   ├── Navigation
│   ├── Formulaires
│   ├── Feedback (toast, alert, progress)
│   └── Layouts (grid, sidebar, dashboard)
└── Guidelines
    ├── Accessibilité (WCAG)
    ├── Voice & Tone
    ├── Motion
    └── Platform-specific
```

## Design Tokens

### Hiérarchie des tokens
```yaml
# 1. Global tokens (valeurs brutes)
global:
  color-blue-500: '#0066FF'
  spacing-4: 4px
  font-size-16: 1rem

# 2. Alias tokens (sémantique)
alias:
  color-primary: '{global.color-blue-500}'
  spacing-sm: '{global.spacing-4}'
  font-body: '{global.font-size-16}'

# 3. Component tokens (spécifiques)
component:
  button-bg: '{alias.color-primary}'
  button-padding: '{alias.spacing-sm}'
```

### Formats d'export
```json
// tokens.json (standard W3C Design Tokens)
{
  "color": {
    "primary": {
      "$value": "#0066FF",
      "$type": "color"
    }
  },
  "spacing": {
    "md": {
      "$value": "16px",
      "$type": "dimension"
    }
  }
}
```

### Plateformes cibles
```yaml
Web (CSS Custom Properties):
  :root { --color-primary: #0066FF; }
iOS (Swift):
  static let primary = Color(hex: "#0066FF")
Android (Compose):
  val Primary = Color(0xFF0066FF)
Flutter:
  static const primary = Color(0xFF0066FF)
```

## Gouvernance & Workflow

### Contribution Model
```
1. Request → Issue dans le repo du design system
2. Review → Design Review + Code Review
3. Approve → Design lead + Engineering lead
4. Publish → Nouvelle version (semver)
5. Adopt → Migration plan + documentation
```

### Versioning (Semantic Versioning)
```yaml
MAJOR: Breaking changes (suppression composant, token renommé)
MINOR: Nouveautés (nouveau composant, token ajouté)
PATCH: Corrections (bug fix, accessibilité)
```

### RACI
| Rôle | Responsabilité |
|------|----------------|
| Design Lead | Vision, qualité visuelle, consistency |
| Engineering Lead | Architecture, performance, testabilité |
| Product Manager | Priorités, roadmap, adoption |
| Contributor | Implémentation, documentation, tests |
| Consumer | Feedback, bugs, feature requests |

## Storybook

### Installation
```bash
npx storybook@latest init
pnpm dlx storybook@latest init --type react
```

### Structure
```
.storybook/
├── main.js          # Configuration (addons, stories)
├── preview.js       # Global decorators, themes
└── manager.js       # UI customization
```

### Story exemple
```jsx
// Button.stories.jsx
import { Button } from './Button';

export default {
  title: 'Atoms/Button',
  component: Button,
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
  },
};

export const Primary = {
  args: {
    variant: 'primary',
    label: 'Click me',
    size: 'md',
  },
};

export const Disabled = {
  args: {
    ...Primary.args,
    disabled: true,
  },
};
```

### Addons essentiels
```yaml
@storybook/addon-a11y:         Tests d'accessibilité
@storybook/addon-actions:      Voir les events
@storybook/addon-controls:     Modifier les props en live
@storybook/addon-viewport:     Responsive preview
@storybook/addon-interactions: Tests d'interactions
storybook-dark-mode:           Thème dark/light
@storybook/test-runner:        Tests automatisés
```

## Figma ↔ Code Sync

### Stratégies de synchronisation
```yaml
1. Manual: Design → Token export → PR → Review
   - Simple, peu d'outillage
   - Risque de dérive

2. Semi-automated: Plugin → Token JSON → Commit
   - Tokens sync automatiques
   - Composants encore manuels

3. Full sync: Figma API → GitHub Action → Storybook
   - CI/CD pipeline complet
   - Complexe à mettre en place
```

### Outils de sync
| Outil | Usage |
|-------|-------|
| **Design Tokens (plugin)** | Export Figma → JSON |
| **Specify** | Tokens → code pipeline |
| **Supernova** | Design system manager |
| **Figma API** | Custom sync scripts |
| **Backlight** | Design system platform |

### GitHub Action exemple
```yaml
name: Sync Design Tokens
on:
  workflow_dispatch:
  schedule:
    - cron: '0 6 * * 1'  # weekly

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Fetch tokens from Figma
        run: |
          curl -H "X-Figma-Token: ${{ secrets.FIGMA_TOKEN }}" \
            "https://api.figma.com/v1/files/$FILE_KEY/variables/local" \
            > tokens.json
      - name: Transform tokens
        run: node scripts/transform-tokens.js
      - name: Create PR
        uses: peter-evans/create-pull-request@v5
```

## Composants : Critères de qualité

### Checklist composant
```yaml
Fonctionnel:
  [ ] States: default, hover, active, focus, disabled
  [ ] Loading / Empty / Error / Success states
  [ ] Keyboard navigation (Tab, Enter, Escape, Arrow)
  [ ] Screen reader support (aria-*)
  [ ] RTL support

Visuel:
  [ ] Responsive (mobile, tablet, desktop)
  [ ] Dark mode + Light mode
  [ ] Focus ring visible
  [ ] Motion réduit (prefers-reduced-motion)
  [ ] Zoom jusqu'à 200% sans perte

Technique:
  [ ] Tests unitaires (Jest + Testing Library)
  [ ] Tests visuels (Chromatic, Percy)
  [ ] Tests accessibilité (axe-core, Pa11y)
  [ ] Bundle size budget
  [ ] Tree-shakeable
  [ ] TypeScript typings
```

### Documentation composant
```markdown
## Button

### Usage
```jsx
import { Button } from '@company/ui'
<Button variant="primary" size="md">Click</Button>
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'primary'|'secondary'|'ghost' | 'primary' |
| size | 'sm'|'md'|'lg' | 'md' |
| disabled | boolean | false |
| loading | boolean | false |
| onClick | () => void | - |

### Accessibility
- WAI-ARIA: button role
- Focus visible outline
- Loading state: aria-busy="true"
- Disabled: aria-disabled="true"

### Examples
[Interactive Storybook examples]
```

## Testing

### Visual Regression (Chromatic)
```bash
npx chromatic --project-token=CHROMATIC_TOKEN
```

### Accessibility
```jsx
// Test avec axe-core
import { axe } from 'jest-axe';

it('should have no accessibility violations', async () => {
  const { container } = render(<Button>Click</Button>);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Interaction tests (Storybook test runner)
```js
// Button.test.js
import { test } from '@storybook/test-runner';
import { within } from '@storybook/testing-library';

test('Button click triggers action', async () => {
  await test.story('Primary');
  const button = within(document.body).getByRole('button');
  await button.click();
});
```

## Adoption & Migration

### Stratégie d'adoption
```yaml
Phase 1: Audit (2-4 semaines)
  - Inventaire des composants existants
  - Gap analysis
  - Priorisation

Phase 2: Foundations (4-6 semaines)
  - Tokens
  - Typographie, couleurs, espacements
  - Migration CSS

Phase 3: Core Components (6-8 semaines)
  - Button, Input, Select, Card
  - Tests + documentation

Phase 4: Patterns (8-12 semaines)
  - Formulaires, navigation, data display
  - Templates page

Phase 5: Scale (continu)
  - Adoption metrics
  - Feedback loops
  - Versioning
```

### Métriques d'adoption
```yaml
- Components usage / total components
- % of pages using design system
- Time to ship new feature
- Accessibility violations count
- Design → Dev handoff time
- Cross-product consistency score
```

## Pièges
- ⚠️ Design system ≠ component library — inclure guidelines, tokens, patterns
- ⚠️ Trop de composants → vélocité ralentie, maintenabilité réduite
- ⚠️ Pas de gouvernance → chaos, dérive, forks non officiels
- ⚠️ Ignorer l'accessibilité → exclusion, risques légaux
- ⚠️ Sync Figma ↔ Code manuelle → dérive, désynchronisation
- ⚠️ Comité de validation trop lent → contournement, Shadow DS
- ⚠️ Documenter en anglais → inaccessible aux équipes non-anglophones
- ⚠️ Pas de versioning → impossible de savoir quelle version est utilisée