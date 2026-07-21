---
name: observable
description: "Observable Framework & Observable Plot : notebooks réactifs, visualisation déclarative Plot, déploiement de dashboards statiques, cellules réactives JavaScript."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [observable, observable-plot, dataviz, javascript, notebooks, reactive, dashboard]
    homepage: https://observablehq.com/
    related_skills: [d3-js, plotly, dashboard-design, data-storytelling]
prerequisites:
  commands: [node, npm]
  npm_packages:
    - "@observablehq/plot"
    - "@observablehq/framework"
---

# Compétence Observable — Notebooks Réactifs & Observable Plot

## Vue d'ensemble

**Observable** est une plateforme de notebooks réactifs pour la visualisation de données et l'exploration analytique. Contrairement aux notebooks Jupyter (exécution linéaire), les cellules Observable se re-calculent automatiquement quand leurs dépendances changent — c'est le paradigme **réactif**.

Deux produits complémentaires :

1. **Observable Framework** : générateur de sites statiques pour dashboards et rapports de données. Combine Markdown, JavaScript réactif et déploiement one-command.
2. **Observable Plot** : bibliothèque de visualisation déclarative sur SVG/Canvas, haut niveau, propulsée par D3 sous le capot. Conçue pour l'exploration rapide et les graphiques reproductibles.

Philosophie : *"Des graphiques aussi simples qu'une ligne de code, aussi puissants que D3."*

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut explorer des données de manière interactive avec re-calcul automatique.
- Construit un dashboard ou un rapport de données statique (Framework).
- Cherche une API concise pour des graphiques en une ligne (`Plot.lineY(data)`).
- A besoin de combiner D3 et Plot dans le même notebook.
- Souhaite publier/déployer un rapport de données avec Observable HQ ou en autohébergement.

---

## Prérequis

```bash
# Observable Plot (dans n'importe quel projet JS)
npm install @observablehq/plot

# Observable Framework (CLI dashboard)
npm create @observablehq/framework
cd mon-dashboard && npm run dev
```

---

## 1. Observable Plot — API Déclarative

### 1.1 Principe Fondamental

```javascript
import * as Plot from "@observablehq/plot";

Plot.plot({
  marks: [
    Plot.dot(data, { x: "x", y: "y" })
  ]
});
```

**Concepts clés :** `marks`, `options`, `scales`, `facets`.

### 1.2 Graphiques Fondamentaux

```javascript
const data = [
  { date: "2024-01", value: 30 },
  { date: "2024-02", value: 45 },
  { date: "2024-03", value: 38 },
  { date: "2024-04", value: 60 },
];

// Nuage de points
Plot.dot(data, { x: "date", y: "value" }).plot();

// Ligne
Plot.lineY(data, { x: "date", y: "value" }).plot();

// Barres
Plot.barY(data, { x: "date", y: "value" }).plot();

// Ligne + points
Plot.plot({
  marks: [
    Plot.lineY(data, { x: "date", y: "value", stroke: "steelblue" }),
    Plot.dot(data, { x: "date", y: "value", fill: "steelblue" }),
  ]
});

// Aire
Plot.areaY(data, { x: "date", y: "value", fillOpacity: 0.2 }).plot();
```

### 1.3 Graphiques Statistiques

```javascript
// Histogramme
Plot.rectY(data, Plot.binX({ y: "count" }, { x: "value" })).plot();

// Boxplot
Plot.boxY(data, { x: "category", y: "value" }).plot();

// Densité (KDE)
Plot.density(data, { x: "value", y: "group" }).plot();

// Ecdf (distribution cumulative)
Plot.ecdf(data, { x: "value", stroke: "category" }).plot();
```

### 1.4 Graphiques Hiérarchiques

```javascript
// Treemap
Plot.treemap(data, {
  path: "name",
  value: "value",
  fill: "group",
  width: 800,
  height: 600
}).plot();

// Sunburst
Plot.sunburst(data, {
  path: "name",
  value: "value",
  fill: "depth"
}).plot();
```

### 1.5 Graphiques Géographiques

```javascript
// Points sur une carte
Plot.plot({
  projection: "mercator",
  marks: [
    Plot.geo(world, { fill: "#ddd", stroke: "#fff" }),
    Plot.dot(cities, { x: "longitude", y: "latitude", fill: "red", r: 3 }),
  ]
});

// Carte choroplèthe
Plot.plot({
  projection: "albers-usa",
  marks: [
    Plot.geo(usStates, {
      fill: d => d.properties.unemployment,
      stroke: "#fff",
      title: d => `${d.properties.name}\n${d.properties.unemployment}%`
    }),
  ]
});
```

### 1.6 Facettes (Petits Multiples / Small Multiples)

```javascript
// Facette par catégorie (grille)
Plot.plot({
  facet: { data, x: "category", y: "year" },
  marks: [
    Plot.lineY(data, { x: "date", y: "value", strokeOpacity: 0.5 }),
  ],
});
```

### 1.7 Marques Composées

```javascript
// Boxplot + jitter (points superposés)
Plot.plot({
  marks: [
    Plot.boxY(data, { x: "group", y: "value" }),
    Plot.dot(data, {
      x: "group", y: "value",
      jitter: 1, fill: "group", fillOpacity: 0.3, r: 2,
    }),
  ],
});

// Ligne avec intervalle de confiance
Plot.plot({
  marks: [
    Plot.areaY(avgData, { x: "date", y1: "ci_low", y2: "ci_high", fillOpacity: 0.2 }),
    Plot.lineY(avgData, { x: "date", y: "mean", stroke: "steelblue" }),
  ],
});

// Barres empilées 100%
Plot.barY(data, {
  x: "category", y: "value", fill: "subcategory",
  normalize: "sum",
}).plot();
```

### 1.8 Options de Style

```javascript
Plot.plot({
  style: {
    background: "#1a1a2e",
    color: "#e0e0e0",
    fontFamily: "system-ui, sans-serif",
  },
  color: {
    scheme: "Viridis",
    legend: true,
    type: "linear",
  },
  x: { label: "Date →", grid: true, ticks: 10, tickFormat: "%b %Y" },
  y: { label: "Valeur ↑", grid: true, nice: true, zero: true },
  marks: [
    Plot.lineY(data, { x: "date", y: "value", stroke: "group" }),
  ],
});
```

---

## 2. Observable Framework — Dashboards Statiques

### 2.1 Structure d'un Projet

```
mon-dashboard/
├── src/
│   ├── index.md          # Page d'accueil (Markdown + JS réactif)
│   ├── data/
│   │   └── sales.csv     # Fichiers de données
│   ├── components/
│   │   └── chart.js      # Modules réutilisables
│   └── imports/
│       └── ...           # Transformations de données (parquet, duckdb)
├── observablehq.config.js  # Configuration du framework
└── package.json
```

### 2.2 Cellules Réactives

```markdown
# Mon Dashboard de Ventes

```js
// Cellule 1 : chargement des données (se re-calcule si le fichier change)
const data = FileAttachment("data/sales.csv").csv({ typed: true });
```

```js
// Cellule 2 : transformation (se re-calcule si data change)
const byProduct = d3.group(data, d => d.product);
const totals = Array.from(byProduct, ([key, values]) => ({
  product: key,
  total: d3.sum(values, v => v.amount),
}));
```

```js
// Cellule 3 : graphique (se re-calcule si totals ou la sélection change)
Plot.barY(totals, { x: "product", y: "total", sort: { x: "-y" } }).plot()
```
```

### 2.3 Fichier de Configuration

```javascript
// observablehq.config.js
export default {
  root: "src",
  output: "dist",
  title: "Dashboard Ventes 2024",
  theme: ["dark", "light"],
  sidebar: true,
  toc: true,
  cleanUrls: true,
};
```

### 2.4 Composants Réutilisables

```javascript
// src/components/chart.js
import * as Plot from "npm:@observablehq/plot";

export function salesChart(data, { width } = {}) {
  return Plot.plot({
    width,
    marks: [
      Plot.lineY(data, { x: "date", y: "value", stroke: "product" }),
    ],
  });
}
```

```markdown
```js
import { salesChart } from "./components/chart.js";
```

```js
salesChart(monthlyData, { width })
```
```

### 2.5 Data Loaders

Les data loaders transforment des données à la construction (pas au runtime).

```javascript
// src/data/sales.json.js (Node.js loader)
import { csvParse } from "d3-dsv";
import { readFileSync } from "fs";

const csv = readFileSync("src/data/sales.csv", "utf-8");
const data = csvParse(csv);

const monthly = d3.rollup(data, v => d3.sum(v, d => d.amount), d => d.month);
process.stdout.write(JSON.stringify(
  Array.from(monthly, ([month, total]) => ({ month, total }))
));
```

**Loaders supportés :** `.js`, `.ts`, `.py`, `.R`, `.sh`, `.go`, `.duckdb`

### 2.6 Interactive Inputs

```markdown
```js
const selectedProduct = view(Inputs.select(
  Array.from(new Set(data.map(d => d.product))),
  { label: "Produit :", value: "Tous" }
));
```

```js
const filtered = selectedProduct === "Tous"
  ? data
  : data.filter(d => d.product === selectedProduct);
```

```js
Plot.lineY(filtered, { x: "date", y: "value", stroke: "product" }).plot()
```
```

**Inputs disponibles :** `Inputs.select()`, `Inputs.checkbox()`, `Inputs.radio()`, `Inputs.range()`, `Inputs.date()`, `Inputs.text()`, `Inputs.search()`, `Inputs.table()`, `Inputs.button()`, `Inputs.color()`, `Inputs.number()`

### 2.7 Table de Données Interactive

```javascript
Inputs.table(data, {
  columns: ["date", "product", "amount", "region"],
  sort: "date",
  format: {
    amount: d3.format("$,.2f"),
    date: d3.utcFormat("%b %Y"),
  },
  maxHeight: "400px",
  multiple: true,
  filter: true,
});
```

---

## 3. Intégration D3 + Plot

Observable Plot est construit sur D3. Vous pouvez mélanger les deux :

```javascript
// Plot pour la structure rapide
const plot = Plot.lineY(data, { x: "date", y: "value" });

// Customisation D3 après rendu
const svg = plot;
const lastPoint = d3.select(svg).select(".dot:last-child");
lastPoint.attr("r", 8).attr("fill", "red");
```

Ou utiliser D3 directement pour des visualisations non couvertes par Plot.

---

## 4. Performance & Optimisation

```javascript
// Grands jeux de données (> 100k points) : Canvas
Plot.dot(data, { x: "x", y: "y", render: "canvas" }).plot();

// Échantillonnage pour l'exploration
Plot.dot(data.slice(0, 5000), { x: "x", y: "y" }).plot();

// Web Workers pour les data loaders (DuckDB WASM)
```

---

## 5. Déploiement

```bash
# Build statique
npm run build
# → dist/ prêt pour déploiement (Netlify, Vercel, GitHub Pages, S3)

# Preview local
npm run dev

# Déploiement Observable HQ
npx observable deploy
```

---

## Pièges Courants (Pitfalls)

1. **Graphique vide sans erreur.**
   - *Correction :* Vérifier les noms exacts des colonnes (casse, espaces) avec `console.log(data.columns)`.

2. **Perte de réactivité avec des mutations d'objets.**
   - *Correction :* Toujours créer une nouvelle référence : `data = [...data, newPoint]`.

3. **Data loaders qui échouent silencieusement.**
   - *Correction :* Tester le loader en ligne de commande : `node src/data/sales.json.js`.

4. **Trop de cellules réactives (lenteur).**
   - *Correction :* Utiliser `mutable` pour les états locaux, ou `generator` pour les flux.

5. **Plot surchargé de points (performance).**
   - *Correction :* Activer le rendu Canvas : `render: "canvas"`. Ou échantillonner.

---

## Ressources

- [Observable Plot Documentation](https://observablehq.com/plot/)
- [Observable Framework Docs](https://observablehq.com/framework/)
- [Observable HQ (plateforme)](https://observablehq.com/)
- [Plot Gallery (exemples)](https://observablehq.com/@observablehq/plot-gallery)
- [D3 + Plot : quand utiliser quoi](https://observablehq.com/@d3/d3-vs-plot)

---

## Checklist

- [ ] Observable Plot installé (`npm install @observablehq/plot`).
- [ ] Les noms de champs dans `x:`, `y:`, `fill:` correspondent exactement aux données.
- [ ] Les graphiques utilisent `Plot.plot({ marks: [...] })` pour les compositions.
- [ ] Les facettes sont utilisées pour les small multiples (évite les boucles manuelles).
- [ ] Les data loaders sont testés indépendamment.
- [ ] Les inputs réactifs sont liés via `view()`.
- [ ] Le déploiement produit un dossier `dist/` statique.
