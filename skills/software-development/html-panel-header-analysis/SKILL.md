---
name: html-panel-header-analysis
description: "Analyser et extraire la structure HTML des en-têtes de panneaux, leurs styles CSS et attributs associés."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - html
      - css
      - frontend
      - panel-header
      - analysis
      - tailwind
      - alpinejs
      - web-development
      - ui-structure
    related_skills:
      - prompt-engineering
      - python-pep8
---

# Analyse Structurelle d'En-têtes de Panneaux HTML

## Vue d'ensemble

Cette compétence permet d'analyser systématiquement la structure HTML des en-têtes (headers) de panneaux d'interface utilisateur — qu'il s'agisse de panneaux latéraux, de fenêtres modales ou de sections de tableau de bord. L'analyse couvre :

- **La structure DOM** : hiérarchie des éléments, imbrication, rôles ARIA.
- **Les styles CSS** : classes utilitaires (Tailwind, Bootstrap), dimensions (`height`, `width`, `padding`), bordures et espacements.
- **Les attributs dynamiques** : liaisons Alpine.js (`x-data`, `x-text`, `x-show`, `@click`), attributs de données personnalisées (`data-*`).
- **Les commentaires structurels** : repères de navigation dans le code source (`<!-- Header Name -->`).

### Cas d'usage typiques

- Vérifier la cohérence structurelle des en-têtes dans un projet web en cours de développement.
- Inspecter les classes CSS pour garantir la conformité avec une charte graphique (taille, couleurs, espacements).
- Localiser des composants d'interface utilisateur spécifiques (ex : panneau de chat, explorateur de fichiers) dans des templates HTML complexes.
- Documenter l'architecture des composants d'une application web existante (reverse-engineering UI).

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Analyser la structure HTML d'un en-tête de panneau spécifique (ex : « Trouve le header du panneau de droite »).
- Inspecter les classes CSS et les styles d'un élément d'interface.
- Localiser des composants d'interface dans un fichier HTML volumineux (plusieurs milliers de lignes).
- Vérifier la présence et la configuration d'attributs dynamiques (Alpine.js, Vue.js, etc.).
- Extraire la hiérarchie DOM d'une section de page à des fins de documentation.
- Comparer la structure des en-têtes entre différentes pages d'une application.

### Ne pas utiliser pour :

- La modification directe du code HTML (utiliser les outils `patch` ou `write_file` avec une compétence frontend dédiée).
- L'analyse de rendu visuel (captures d'écran, tests visuels) — cette compétence travaille sur le code source uniquement.
- L'audit de performance ou d'accessibilité complet (utiliser Lighthouse, axe-core, WAVE).
- L'analyse de pages web distantes (préférer `web_read` pour charger le HTML à analyser).

---

## 1. Méthodologie d'Analyse

### 1.1 Localisation de l'en-tête cible

#### Par recherche de commentaire structurel

```html
<!-- Right Panel Header -->
<div class="h-[52px] px-4 flex items-center justify-between border-b border-gray-200">
    <span class="font-semibold text-gray-700">Chat Console</span>
    <div class="flex items-center gap-2">
        <button @click="toggleSessionList"
                class="p-1 hover:bg-gray-100 rounded"
                x-tooltip="Sessions">
            <svg><!-- icône --></svg>
        </button>
    </div>
</div>
```

```bash
# Recherche du commentaire de section
search_files --pattern "<!-- Right Panel Header -->" --path ./web/templates/
```

#### Par contenu textuel

```html
<!-- Sans commentaire, chercher le texte visible -->
<span class="font-semibold">Chat Console</span>
```

```bash
# Recherche par texte de l'en-tête
search_files --pattern "Chat Console" --file-glob "*.html" --path ./web/templates/
```

### 1.2 Inspection des classes CSS

Une fois l'élément localisé, analyser les classes pour déterminer :

| Classe utilitaire | Propriété CSS correspondante | Valeur typique |
| :--- | :--- | :--- |
| `h-[52px]` | `height` | 52 pixels |
| `px-4` | `padding-left/right` | 1rem (16px) |
| `py-2` | `padding-top/bottom` | 0.5rem (8px) |
| `border-b` | `border-bottom` | 1px solid |
| `border-gray-200` | `border-color` | `#e5e7eb` |
| `flex` | `display` | flex |
| `items-center` | `align-items` | center |
| `justify-between` | `justify-content` | space-between |
| `gap-2` | `gap` | 0.5rem (8px) |

### 1.3 Repérage des liaisons dynamiques

Les frameworks JavaScript modernes ajoutent des attributs de liaison directement dans le HTML :

```html
<!-- Alpine.js -->
<div x-data="{ open: false }">
    <button @click="open = !open"
            :class="{ 'bg-blue-500': open }">
        <span x-text="open ? 'Fermer' : 'Ouvrir'"></span>
    </button>
    <div x-show="open"
         x-transition:enter="transition ease-out duration-300">
        Contenu du panneau
    </div>
</div>
```

| Attribut | Framework | Rôle |
| :--- | :--- | :--- |
| `x-data` | Alpine.js | Déclaration d'un composant réactif |
| `x-text` | Alpine.js | Liaison de texte |
| `x-show` | Alpine.js | Affichage conditionnel |
| `x-transition` | Alpine.js | Animation d'entrée/sortie |
| `@click` | Alpine.js/Vue | Gestionnaire d'événement clic |
| `:class` | Alpine.js/Vue | Liaison de classe conditionnelle |
| `v-if` / `v-show` | Vue.js | Rendu/affichage conditionnel |

### 1.4 Analyse de la hiérarchie DOM

Pour les fichiers HTML complexes, reconstituer la hiérarchie :

```html
<div class="flex h-screen">                    <!-- Conteneur principal -->
    <aside class="w-64 border-r">              <!-- Panneau gauche -->
        <!-- Left Panel Header -->
        <div class="h-[52px] px-4 flex ...">   <!-- En-tête -->
            <span>Files Explorer</span>
        </div>
        <nav class="flex-1 overflow-y-auto">   <!-- Contenu -->
            ...
        </nav>
    </aside>
    <main class="flex-1">                       <!-- Zone principale -->
        ...
    </main>
    <aside class="w-80">                        <!-- Panneau droit -->
        <!-- Right Panel Header -->
        <div class="h-[52px] px-4 flex ...">   <!-- En-tête -->
            <span>Chat Console</span>
        </div>
    </aside>
</div>
```

**Arbre DOM extrait :**

```
div.flex.h-screen
├── aside.w-64.border-r                  (Panneau gauche)
│   ├── div.h-[52px].px-4.flex           (En-tête)
│   │   └── span → "Files Explorer"
│   └── nav.flex-1.overflow-y-auto       (Contenu)
└── aside.w-80                           (Panneau droit)
    └── div.h-[52px].px-4.flex           (En-tête)
        └── span → "Chat Console"
```

---

## 2. Exemples d'Analyse

### 2.1 Cas 1 : En-tête du panneau de droite (Chat Console)

**Objectif :** Inspecter la hauteur et les interactions du panneau de chat.

```html
<!-- Right Panel Header -->
<div class="h-[52px] px-4 flex items-center justify-between border-b border-gray-200 bg-white"
     x-data="{ sessionInfo: null }">
    <span class="font-semibold text-gray-700 flex items-center gap-2">
        <span x-text="sessionInfo ? sessionInfo.name : 'Chat Console'"></span>
        <span x-show="sessionInfo"
              class="text-xs text-gray-400"
              x-text="`(${sessionInfo.messages.length} messages)`"></span>
    </span>
    <div class="flex items-center gap-1">
        <button @click="clearChat()"
                class="p-1.5 hover:bg-gray-100 rounded"
                x-tooltip="Effacer la conversation">
            <svg class="w-4 h-4 text-gray-500"><!-- icône --></svg>
        </button>
    </div>
</div>
```

**Résultats de l'analyse :**

| Propriété | Valeur |
| :--- | :--- |
| Hauteur | `52px` (fixe, `h-[52px]`) |
| Padding horizontal | `16px` (`px-4`) |
| Fond | `bg-white` |
| Bordure basse | `border-b border-gray-200` (#e5e7eb) |
| Disposition | `flex items-center justify-between` |
| État réactif | `sessionInfo` (objet ou null) |
| Interactions | `@click=clearChat()`, `x-tooltip` |
| Affichage conditionnel | `x-show="sessionInfo"` |

### 2.2 Cas 2 : En-tête du panneau gauche (Explorateur de fichiers)

```html
<!-- Left Panel Header -->
<div class="h-12 px-3 flex items-center border-b border-gray-200">
    <span class="text-sm font-medium text-gray-600 flex items-center gap-2">
        <svg class="w-4 h-4"><!-- icône dossier --></svg>
        Files Explorer
    </span>
    <div class="ml-auto flex items-center gap-1">
        <button @click="refreshFileList"
                class="p-1 hover:bg-gray-100 rounded">
            <svg class="w-4 h-4"><!-- icône refresh --></svg>
        </button>
        <button @click="createNewFile"
                class="p-1 hover:bg-gray-100 rounded">
            <svg class="w-4 h-4"><!-- icône plus --></svg>
        </button>
    </div>
</div>
```

**Différences clés entre panneaux gauche et droit :**

| Propriété | Panneau gauche (Files) | Panneau droit (Chat) |
| :--- | :--- | :--- |
| Hauteur | `h-12` (48px) | `h-[52px]` (52px) |
| Padding | `px-3` (12px) | `px-4` (16px) |
| Fond | Transparent | `bg-white` |
| Texte | `text-sm font-medium` | `font-semibold` |
| État réactif | Aucun | `sessionInfo` |

---

## 3. Génération de Documentation

Produire une fiche de documentation pour chaque composant d'en-tête analysé :

```markdown
## Composant : [Nom du panneau]

**Fichier :** `web/templates/partials/[fichier].html`
**Ligne :** 42

### Structure DOM

```
div.h-[52px].px-4.flex.items-center.justify-between
├── span.font-semibold → Texte du titre
│   └── span.x-show → Compteur conditionnel
└── div.flex.gap-1
    └── button[@click][x-tooltip] → Bouton d'action
```

### Propriétés CSS

| Propriété | Valeur | Classe |
| :--- | :--- | :--- |
| Hauteur | 52px | `h-[52px]` |
| Padding X | 16px | `px-4` |
| Bordure basse | 1px solid #e5e7eb | `border-b border-gray-200` |

### États et Interactions

| Événement | Action | Condition |
| :--- | :--- | :--- |
| `@click` | `clearChat()` | Toujours actif |
| `x-show` | Texte conditionnel | `sessionInfo != null` |

### Dépendances

- Alpine.js (composant réactif)
- Icônes SVG inline
- Directive `x-tooltip` (plugin Alpine.js)
```

---

## 4. Détection des Anomalies Courantes

Lors de l'analyse, identifier les incohérences potentielles :

```python
anomalies = {
    "hauteur_incoherente": "Tous les en-têtes devraient faire 52px (h-[52px])",
    "padding_incoherent": "Padding horizontal incohérent entre panneaux",
    "classe_inutilisee": "Classes CSS présentes mais non définies dans la feuille de style",
    "accesibilite_manquante": "Attributs ARIA manquants (role, aria-label)",
    "binding_casse": "Référence à une variable x-data inexistante",
}
```

---

## Pièges Courants (Common Pitfalls)

1. **Numéros de ligne incorrects** : Les fichiers HTML volumineux changent fréquemment. Toujours vérifier le contexte autour de la ligne cible avant d'éditer.

2. **Attributs cachés dans les commentaires ou liaisons** : Ne pas se fier uniquement aux classes visibles ; inspecter les attributs `x-*`, `v-*`, `data-*`, `:class` pour les liaisons dynamiques.

3. **Hiérarchie DOM imbriquée** : Un élément d'en-tête peut être encapsulé dans plusieurs `div` ou `template` avant d'apparaître dans le rendu. Suivre la hiérarchie depuis le conteneur principal.

4. **Propriétés CSS héritées** : Une hauteur peut être définie via `min-height` sur le parent plutôt que `height` sur l'élément. Vérifier les deux niveaux.

5. **Frameworks à composants** : Dans React/Vue, le HTML peut être généré par du JSX ou des templates `.vue`. Chercher dans les fichiers `.tsx`, `.vue` ou `.js` si le HTML n'est pas dans les templates.

6. **Classes conditionnelles** : `:class="{ 'h-14': isExpanded, 'h-12': !isExpanded }"` — l'en-tête peut avoir plusieurs états avec des dimensions différentes.

7. **Commentaires trompeurs** : Un commentaire `<!-- Header -->` peut être décalé par rapport à l'élément réel. Toujours vérifier le contenu immédiatement après le commentaire.

---

## Liste de vérification (Checklist)

- [ ] L'emplacement de l'en-tête est localisé via commentaire, texte ou classe spécifique.
- [ ] La hauteur explicite de l'en-tête est identifiée et documentée (classe `h-*` ou propriété CSS).
- [ ] Les classes CSS utilitaires sont analysées et comprises (Tailwind, Bootstrap, etc.).
- [ ] Les liaisons dynamiques (Alpine.js, Vue.js) sont identifiées et documentées.
- [ ] La hiérarchie DOM est extraite et structurée visuellement.
- [ ] Les différences entre panneaux (gauche/droite) sont relevées et expliquées.
- [ ] Les attributs d'accessibilité (ARIA) sont vérifiés et signalés si absents.
- [ ] Les dépendances (bibliothèques JS, plugins) sont listées.
- [ ] Une fiche de documentation est générée pour chaque composant d'en-tête.
- [ ] Les anomalies structurelles sont identifiées et rapportées.
