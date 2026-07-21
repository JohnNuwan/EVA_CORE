---
name: d3-js
description: "D3.js (Data-Driven Documents) : bibliothèque JavaScript de visualisation de données par manipulation directe du DOM — SVG, Canvas, transitions, force layout, géo, hiérarchies, échelles, axes, brush, zoom, drag."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [d3, d3js, data-visualization, svg, javascript, dataviz, interactive-viz, web]
    homepage: https://d3js.org/
    related_skills: [observable, chart-js, plotly, dashboard-design]
prerequisites:
  commands: [node, npm]
  npm_packages: [d3]
---

# Compétence D3.js — Visualisation de Données par Manipulation du DOM

## Vue d'ensemble

**D3.js** (Data-Driven Documents) est la bibliothèque de référence pour les visualisations de données sur le web. Contrairement aux librairies "boîte noire" (Chart.js, Highcharts), D3 opère directement sur le DOM : l'utilisateur manipule des éléments SVG/Canvas en liant des données, ce qui offre un contrôle total sur chaque pixel de la visualisation.

Philosophie D3 : *"Penser en données, dessiner en DOM."*

**Points forts :** flexibilité totale, SVG/Canvas/WebGL, animations fluides, écosystème riche (geo, hiérarchies, réseaux, layouts).
**Points faibles :** courbe d'apprentissage raide, pas de graphiques prêts à l'emploi, verbose pour des charts simples.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut créer une visualisation de données interactive pour le web.
- A besoin d'un contrôle pixel-parfait sur l'apparence d'un graphique.
- Souhaite des animations de transition entre états de données.
- Travaille sur des visualisations géospatiales (carte choroplèthe, projections).
- Veut des graphiques en réseau, arbres, treemaps, sunbursts.
- A besoin d'interactions avancées : zoom, brush, drag, tooltips personnalisés.

---

## Prérequis

```bash
npm install d3
# Ou via CDN
# <script src="https://d3js.org/d3.v7.min.js"></script>
```

---

## 1. Sélections et Liaison de Données (Data Join)

### 1.1 Le Pattern d'Entrée-Sortie (Enter/Update/Exit)

```javascript
const data = [10, 25, 50, 75, 100];

const circles = d3.select("svg")
  .selectAll("circle")
  .data(data);

// ENTER : nouveaux éléments
circles.enter()
  .append("circle")
  .attr("r", d => d)
  .attr("cx", (d, i) => i * 100 + 50)
  .attr("cy", 100)
  .attr("fill", "steelblue");

// UPDATE : éléments existants (liaison)
circles.attr("r", d => d);

// EXIT : éléments orphelins
circles.exit().remove();
```

### 1.2 La Méthode Générale `.join()` (D3 v7+)

```javascript
svg.selectAll("circle")
  .data(data)
  .join("circle")
    .attr("r", d => d)
    .attr("cx", (d, i) => i * 100 + 50)
    .attr("cy", 100)
    .attr("fill", "steelblue");
```

---

## 2. Échelles (Scales)

Les échelles transforment le domaine des données en plage visuelle.

```javascript
// Linéaire
const xScale = d3.scaleLinear()
  .domain([0, 100])     // données d'entrée
  .range([0, 800]);     // pixels

// Temporelle
const timeScale = d3.scaleTime()
  .domain([new Date("2024-01-01"), new Date("2024-12-31")])
  .range([0, 800]);

// Catégorielle (couleurs)
const colorScale = d3.scaleOrdinal()
  .domain(["A", "B", "C"])
  .range(d3.schemeCategory10);

// Sequentielle (dégradé)
const tempScale = d3.scaleSequential()
  .domain([20, 100])
  .interpolator(d3.interpolateReds);  // ou interpolateViridis, interpolateCool, etc.

// Log (pour données exponentielles)
const logScale = d3.scaleLog()
  .domain([1, 1000])
  .range([0, 800]);

// Seuil (bandes discrètes)
const thresholdScale = d3.scaleThreshold()
  .domain([50, 75, 90])
  .range(["#e74c3c", "#f39c12", "#2ecc71", "#27ae60"]);
```

---

## 3. Axes (Axes)

```javascript
const svg = d3.select("svg");
const margin = { top: 20, right: 30, bottom: 40, left: 50 };
const width = 800 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

const g = svg.append("g")
  .attr("transform", `translate(${margin.left},${margin.top})`);

const xScale = d3.scaleLinear().domain([0, 100]).range([0, width]);
const yScale = d3.scaleLinear().domain([0, 100]).range([height, 0]);

// Axe X en bas
g.append("g")
  .attr("transform", `translate(0,${height})`)
  .call(d3.axisBottom(xScale))
  .selectAll("text")
    .attr("transform", "rotate(-45)")
    .style("text-anchor", "end");

// Axe Y à gauche
g.append("g")
  .call(d3.axisLeft(yScale));

// Axe personnalisé (ticks spécifiques)
g.append("g")
  .call(d3.axisLeft(yScale)
    .ticks(10)
    .tickFormat(d => `${d}%`)
    .tickSizeOuter(0)
  );
```

---

## 4. Graphiques Fondamentaux

### 4.1 Bar Chart

```javascript
const data = [
  { name: "A", value: 30 },
  { name: "B", value: 80 },
  { name: "C", value: 45 },
  { name: "D", value: 60 },
  { name: "E", value: 20 },
];

const x = d3.scaleBand()
  .domain(data.map(d => d.name))
  .range([0, width])
  .padding(0.1);

const y = d3.scaleLinear()
  .domain([0, d3.max(data, d => d.value)])
  .range([height, 0]);

g.selectAll("rect")
  .data(data)
  .join("rect")
    .attr("x", d => x(d.name))
    .attr("y", d => y(d.value))
    .attr("width", x.bandwidth())
    .attr("height", d => height - y(d.value))
    .attr("fill", "steelblue");
```

### 4.2 Line Chart (Série Temporelle)

```javascript
const line = d3.line()
  .x(d => x(d.date))
  .y(d => y(d.value))
  .curve(d3.curveMonotoneX);  // Lissage

g.append("path")
  .datum(data)
  .attr("fill", "none")
  .attr("stroke", "steelblue")
  .attr("stroke-width", 2)
  .attr("d", line);

// Aire
const area = d3.area()
  .x(d => x(d.date))
  .y0(y(0))
  .y1(d => y(d.value))
  .curve(d3.curveMonotoneX);

g.append("path")
  .datum(data)
  .attr("fill", "steelblue")
  .attr("fill-opacity", 0.1)
  .attr("d", area);
```

### 4.3 Scatter Plot

```javascript
g.selectAll("circle")
  .data(data)
  .join("circle")
    .attr("cx", d => x(d.x))
    .attr("cy", d => y(d.y))
    .attr("r", d => d.r || 5)
    .attr("fill", d => colorScale(d.category))
    .attr("opacity", 0.7);
```

### 4.4 Pie / Donut Chart

```javascript
const pie = d3.pie().value(d => d.value);
const arc = d3.arc().innerRadius(0).outerRadius(200);
const donutArc = d3.arc().innerRadius(80).outerRadius(200);

const arcs = g.selectAll("path")
  .data(pie(data))
  .join("path")
    .attr("d", donutArc)  // donut : innerRadius > 0
    .attr("fill", d => colorScale(d.data.name))
    .attr("stroke", "white")
    .attr("stroke-width", 2);
```

---

## 5. Animations et Transitions

```javascript
// Transition simple (durée, délai, easing)
g.selectAll("rect")
  .data(newData)
  .join("rect")
  .transition()
    .duration(800)
    .delay((d, i) => i * 50)
    .ease(d3.easeElasticOut)
    .attr("height", d => height - y(d.value))
    .attr("y", d => y(d.value));

// Animation d'entrée (depuis le bas)
g.selectAll("rect")
  .data(data)
  .join("rect")
    .attr("y", height)          // état initial
    .attr("height", 0)
  .transition()
    .duration(600)
    .delay((d, i) => i * 30)
    .ease(d3.easeBounceOut)
    .attr("y", d => y(d.value))
    .attr("height", d => height - y(d.value));

// Tween personnalisé (interpolation sur attributs)
g.selectAll("circle")
  .transition()
  .duration(1000)
  .attrTween("cx", d => {
    const interpolate = d3.interpolate(0, x(d.x));
    return t => interpolate(t);
  });
```

---

## 6. Interactions

### 6.1 Tooltip

```javascript
const tooltip = d3.select("body")
  .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("background", "rgba(0,0,0,0.8)")
    .style("color", "white")
    .style("padding", "8px 12px")
    .style("border-radius", "4px")
    .style("font-size", "14px")
    .style("pointer-events", "none")
    .style("opacity", 0);

g.selectAll("circle")
  .on("mouseenter", (event, d) => {
    tooltip.transition().duration(200).style("opacity", 0.9);
    tooltip.html(`<strong>${d.name}</strong><br>Valeur : ${d.value}`)
      .style("left", `${event.pageX + 10}px`)
      .style("top", `${event.pageY - 28}px`);
  })
  .on("mouseleave", () => {
    tooltip.transition().duration(500).style("opacity", 0);
  });
```

### 6.2 Zoom & Pan

```javascript
const zoom = d3.zoom()
  .scaleExtent([0.5, 10])
  .translateExtent([[0, 0], [width, height]])
  .on("zoom", (event) => {
    g.attr("transform", event.transform);
  });

svg.call(zoom);

// Zoom sur un élément spécifique
svg.call(zoom.transform, d3.zoomIdentity.translate(200, 100).scale(2));
```

### 6.3 Brush (Sélection par Rectangle)

```javascript
const brush = d3.brush()
  .extent([[0, 0], [width, height]])
  .on("end", (event) => {
    if (!event.selection) return;
    const [[x0, y0], [x1, y1]] = event.selection;
    // Filtrer les données dans la zone sélectionnée
    const selected = data.filter(d =>
      x(d.x) >= x0 && x(d.x) <= x1 && y(d.y) >= y0 && y(d.y) <= y1
    );
    console.log("Points sélectionnés :", selected);
  });

g.append("g").call(brush);
```

### 6.4 Drag (Déplacement)

```javascript
const drag = d3.drag()
  .on("start", (event, d) => {
    d.fx = d.x; d.fy = d.y;
  })
  .on("drag", (event, d) => {
    d.fx = event.x; d.fy = event.y;
    redraw();  // fonction de mise à jour
  })
  .on("end", (event, d) => {
    d.fx = null; d.fy = null;  // relâche
  });

g.selectAll("circle").call(drag);
```

---

## 7. Layouts Avancés

### 7.1 Force Layout (Graphes / Réseaux)

```javascript
const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width / 2, height / 2))
  .force("collision", d3.forceCollide(30))
  .on("tick", ticked);

function ticked() {
  link.attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  node.attr("cx", d => d.x)
      .attr("cy", d => d.y);
}
```

### 7.2 Treemap

```javascript
const root = d3.hierarchy(data).sum(d => d.value);

d3.treemap()
  .size([width, height])
  .padding(2)
  .round(true)(root);

const cells = g.selectAll("rect")
  .data(root.leaves())
  .join("rect")
    .attr("x", d => d.x0)
    .attr("y", d => d.y0)
    .attr("width", d => d.x1 - d.x0)
    .attr("height", d => d.y1 - d.y0)
    .attr("fill", d => colorScale(d.parent.data.name));
```

### 7.3 Sunburst / Partition

```javascript
const root = d3.hierarchy(data).sum(d => d.value);

d3.partition()
  .size([2 * Math.PI, radius])(root);

const arcs = g.selectAll("path")
  .data(root.descendants())
  .join("path")
    .attr("d", d3.arc()
      .startAngle(d => d.x0)
      .endAngle(d => d.x1)
      .innerRadius(d => d.y0)
      .outerRadius(d => d.y1)
    )
    .attr("fill", d => colorScale(d.depth));
```

### 7.4 Sankey (Diagramme de Flux)

```javascript
const sankey = d3.sankey()
  .nodeWidth(20)
  .nodePadding(10)
  .extent([[0, 0], [width, height]]);

const { nodes, links } = sankey({
  nodes: [...],
  links: [...]
});

// Liens avec dégradé
g.selectAll("path")
  .data(links)
  .join("path")
    .attr("d", d3.sankeyLinkHorizontal())
    .attr("fill", "none")
    .attr("stroke", d => d.color)
    .attr("stroke-width", d => d.width)
    .attr("opacity", 0.4);
```

---

## 8. Cartographie (Geo)

```javascript
// Projection
const projection = d3.geoMercator()
  .fitSize([width, height], geojson);

const path = d3.geoPath().projection(projection);

// Fonds de carte
g.selectAll("path")
  .data(topojson.feature(world, world.objects.countries).features)
  .join("path")
    .attr("d", path)
    .attr("fill", "#ddd")
    .attr("stroke", "#fff")
    .attr("stroke-width", 0.5);

// Choroplèthe (couleur par valeur)
g.selectAll("path")
  .data(geoData)
  .join("path")
    .attr("d", path)
    .attr("fill", d => colorScale(d.properties.value))
    .attr("stroke", "#fff");

// Autres projections
const projections = {
  equirectangular: d3.geoEquirectangular(),
  albers: d3.geoAlbers(),
  conicConformal: d3.geoConicConformal(),
  orthographic: d3.geoOrthographic(),
  stereographic: d3.geoStereographic(),
  naturalEarth: d3.geoNaturalEarth1(),
};
```

---

## 9. Modulaires (Modules D3 Individuels)

D3 est modulaire : importez uniquement ce dont vous avez besoin.

```javascript
// npm : import individuel
import { select, selectAll } from "d3-selection";
import { scaleLinear, scaleOrdinal } from "d3-scale";
import { line, area } from "d3-shape";
import { axisBottom, axisLeft } from "d3-axis";
import { transition } from "d3-transition";
import { easeElasticOut } from "d3-ease";
import { geoMercator, geoPath } from "d3-geo";

// Ou tout d'un coup
import * as d3 from "d3";
```

**Modules principaux :**

| Module | Utilité |
|--------|---------|
| `d3-selection` | Sélection DOM, data join |
| `d3-scale` | Échelles (lin, log, time, ordinal, band) |
| `d3-shape` | Lignes, aires, arcs, symboles |
| `d3-axis` | Axes de graphique |
| `d3-transition` | Animations, transitions |
| `d3-ease` | Fonctions d'easing |
| `d3-array` | Statistiques, tris, groupBy |
| `d3-format` | Formatage de nombres |
| `d3-time-format` | Formatage de dates |
| `d3-geo` | Projections cartographiques |
| `d3-force` | Simulation de forces (graphes) |
| `d3-hierarchy` | Treemap, sunburst, dendrogram |
| `d3-sankey` | Diagrammes de flux Sankey (module externe) |
| `d3-brush` | Sélection rectangulaire |
| `d3-zoom` | Zoom/Pan |
| `d3-drag` | Glisser-déposer |
| `d3-color` | Manipulation de couleurs |
| `d3-interpolate` | Interpolation de valeurs |
| `d3-timer` | Boucle d'animation `requestAnimationFrame` |

---

## 10. Patterns de Performance

```javascript
// 1. Canvas au lieu de SVG pour > 5000 éléments
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const render = () => {
  ctx.clearRect(0, 0, width, height);
  data.forEach(d => {
    ctx.beginPath();
    ctx.arc(xScale(d.x), yScale(d.y), 3, 0, Math.PI * 2);
    ctx.fillStyle = colorScale(d.category);
    ctx.fill();
  });
};

// 2. Data join immutable (D3 v7)
svg.selectAll("circle")
  .data(data, d => d.id)  // clé d'identité
  .join("circle")
    .attr("cx", d => x(d.x));

// 3. Éviter les recalculs d'échelles
const xScale = d3.scaleLinear().domain(...).range(...);

// 4. Utiliser selection.raise() / lower() pour l'ordre z
selection.raise();
selection.lower();
```

---

## Pièges Courants (Pitfalls)

1. **Mutation accidentelle des données dans le data join.**
   - *Erreur :* D3 stocke les données en place sur l'élément DOM via `__data__`. Modifier `d.x` dans un callback modifie l'objet original.
   - *Correction :* Faites une copie des données si vous devez les transformer : `data.map(d => ({...d}))`.

2. **Axes tronqués ou illisibles.**
   - *Erreur :* Les étiquettes d'axes débordent du groupe SVG car le margin n'est pas assez large.
   - *Correction :* Toujours définir des `margin` explicites et traduire le groupe conteneur.

3. **Transitions en conflit (torn tearing).**
   - *Erreur :* Plusieurs transitions sur le même élément s'interrompent mutuellement.
   - *Correction :* Utilisez `selection.interrupt()` avant une nouvelle transition, ou gérez avec `selection.transition().on("end", ...)`.

4. **Force layout infini.**
   - *Erreur :* La simulation de forces ne converge pas (nœuds qui s'éloignent à l'infini).
   - *Correction :* Équilibrer les forces : `forceManyBody().strength(-300)` + `forceCenter()` + `forceCollide()`. Ajuster `alphaDecay`.

5. **Carte géo incomplète ou déformée.**
   - *Erreur :* Le fichier TopoJSON/GeoJSON n'est pas correctement lié à la projection.
   - *Correction :* Vérifiez que `topojson.feature()` est bien appelé, et que la projection utilise `.fitSize()` ou `.fitExtent()`.

6. **Sélecteurs réutilisés sans vidage préalable.**
   - *Erreur :* Appeler `svg.selectAll("circle").data(nouveauxData)` sur un SVG qui contient déjà des cercles — les anciens persistent si mal gérés.
   - *Correction :* Utiliser le pattern enter/update/exit complet ou `.join()`.

7. **Oubli de la fonction de clé dans le data join.**
   - *Erreur :* D3 lie par index (pas par identité), ce qui cause des animations incorrectes lors de réorganisations.
   - *Correction :* Toujours fournir une fonction de clé : `.data(data, d => d.id)`.

---

## Ressources

- [Documentation officielle D3](https://d3js.org/)
- [Observable D3 Notebooks](https://observablehq.com/@d3)
- [D3 Graph Gallery](https://d3-graph-gallery.com/) — exemples pratiques
- [bl.ocks.org](https://bl.ocks.org/) — exemples historiques (Mike Bostock)
- [D3 in Depth](https://www.d3indepth.com/) — tutoriel approfondi

---

## Checklist

- [ ] D3 est installé (`npm install d3` ou CDN).
- [ ] Le margin pattern est utilisé (top/right/bottom/left) pour les axes.
- [ ] Les échelles sont définies avant les éléments graphiques.
- [ ] Le data join utilise `.join()` ou le pattern enter/update/exit complet.
- [ ] Les transitions ont une durée et un easing adaptés.
- [ ] Les interactions (tooltip, zoom, brush) ne fuient pas d'écouteurs.
- [ ] Pour > 5000 éléments, Canvas est privilégié sur SVG.
- [ ] Les données mutables sont clonées avant liaison D3.
