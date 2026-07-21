---
name: chart-js
description: "Chart.js : bibliothèque JavaScript de graphiques responsives en Canvas — barres, lignes, radar, doughnut, scatter, bubble, mixed, animations, plugins (labels, zoom, annotation)."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [chart.js, chartjs, dataviz, javascript, canvas, charts, responsive]
    homepage: https://www.chartjs.org/
    related_skills: [d3-js, plotly, dashboard-design]
prerequisites:
  commands: [node, npm]
  npm_packages: [chart.js, chartjs-plugin-datalabels, chartjs-plugin-zoom]
---

# Compétence Chart.js — Graphiques Canvas Responsives

## Vue d'ensemble

**Chart.js** est la bibliothèque de graphiques en Canvas la plus populaire pour le web. Elle transforme des données en 8 types de graphiques prêts à l'emploi, responsives, animés et interactifs en une dizaine de lignes de JavaScript. Basée sur HTML5 Canvas, elle offre des performances élevées même avec des milliers de points.

Philosophie : *"Un graphique parfait en 5 lignes, personnalisable à l'infini."*

**Quand Chart.js plutôt que D3 ?** Chart.js est le bon choix quand on veut des graphiques standards (barres, lignes, radar) rapidement, sans re-inventer chaque pixel. D3 est nécessaire quand on a besoin d'un contrôle total (layouts custom, géo, force graphs).

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut intégrer un graphique rapidement dans une page web.
- A besoin de graphiques responsives (redimensionnement automatique).
- Souhaite des animations fluides sans configuration complexe.
- Veut un export en PNG/JPEG natif.
- A besoin de plugins : datalabels, zoom, annotation, crosshair.

---

## Prérequis

```bash
npm install chart.js
```

---

## 1. Configuration de Base

### 1.1 Premier Graphique

```html
<canvas id="myChart" width="400" height="400"></canvas>
```

```javascript
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

const ctx = document.getElementById('myChart').getContext('2d');

new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin'],
    datasets: [{
      label: 'Ventes 2024',
      data: [12, 19, 15, 25, 22, 30],
      borderColor: 'rgb(75, 192, 192)',
      tension: 0.3,
    }]
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: true,
        text: 'Ventes Mensuelles 2024'
      },
      legend: {
        position: 'bottom'
      }
    }
  }
});
```

### 1.2 Types de Graphiques Disponibles

| Type | Constructeur | Usage |
|------|-------------|-------|
| `line` | line / scatter | Tendances, séries temporelles |
| `bar` | bar / horizontalBar | Comparaisons catégorielles |
| `radar` | radar | Profils multidimensionnels |
| `doughnut` | doughnut | Proportions (trou central) |
| `pie` | pie | Proportions |
| `polarArea` | polarArea | Proportions radiales |
| `bubble` | bubble | Corrélations tri-dimensionnelles |
| `scatter` | scatter | Nuages de points |
| `mixed` | Combinaison | Plusieurs types sur le même canvas |

---

## 2. Types de Graphiques Détaillés

### 2.1 Bar Chart (Vertical & Horizontal)

```javascript
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Produit A', 'Produit B', 'Produit C', 'Produit D'],
    datasets: [
      {
        label: 'Ventes',
        data: [65, 59, 80, 81],
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
        ],
        borderWidth: 2,
      },
      {
        label: 'Objectif',
        data: [70, 70, 70, 70],
        type: 'line',  // Graphique mixte !
        borderColor: 'rgb(255, 99, 132)',
        borderDash: [5, 5],
        pointRadius: 0,
      }
    ]
  },
  options: {
    indexAxis: 'y',  // Barres horizontales
    scales: {
      x: { stacked: false },
      y: { stacked: false },
    }
  }
});
```

### 2.2 Line Chart (Série Temporelle)

```javascript
new Chart(ctx, {
  type: 'line',
  data: {
    labels: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05'],
    datasets: [
      {
        label: 'Revenus',
        data: [3000, 4500, 3800, 5200, 6100],
        borderColor: '#36a2eb',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
      {
        label: 'Dépenses',
        data: [2500, 2800, 3000, 3100, 3300],
        borderColor: '#ff6384',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
      }
    ]
  },
  options: {
    interaction: {
      mode: 'index',     // Tooltip tous les points sur la même x
      intersect: false,
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y} €`,
        }
      }
    }
  }
});
```

### 2.3 Doughnut / Pie

```javascript
new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ['Facebook', 'Google', 'Direct', 'Email', 'Autres'],
    datasets: [{
      data: [35, 25, 20, 12, 8],
      backgroundColor: [
        '#4267B2', '#4285F4', '#34A853', '#EA4335', '#ccc'
      ],
      borderWidth: 2,
      cutout: '70%',  // Doughnut fin (0 = pie)
    }]
  },
  options: {
    plugins: {
      legend: { position: 'right' },
      title: {
        display: true,
        text: 'Trafic par Source'
      }
    }
  }
});
```

### 2.4 Scatter & Bubble

```javascript
// Scatter Plot
new Chart(ctx, {
  type: 'scatter',
  data: {
    datasets: [{
      label: 'Clients',
      data: [
        { x: 25, y: 30000 },
        { x: 35, y: 45000 },
        { x: 45, y: 55000 },
        { x: 55, y: 42000 },
      ],
      backgroundColor: 'rgba(54, 162, 235, 0.6)',
    }]
  },
  options: {
    scales: {
      x: {
        title: { display: true, text: 'Âge' }
      },
      y: {
        title: { display: true, text: 'Revenu (€)' }
      }
    }
  }
});

// Bubble Chart (3 dimensions : x, y, r)
new Chart(ctx, {
  type: 'bubble',
  data: {
    datasets: [{
      label: 'Produits',
      data: [
        { x: 20, y: 30, r: 15 },
        { x: 40, y: 10, r: 10 },
        { x: 30, y: 50, r: 25 },
        { x: 10, y: 20, r: 8 },
      ],
      backgroundColor: 'rgba(255, 99, 132, 0.6)',
    }]
  }
});
```

### 2.5 Radar (Profils Multi-Dimensions)

```javascript
new Chart(ctx, {
  type: 'radar',
  data: {
    labels: ['Vitesse', 'Précision', 'Robustesse', 'UX', 'Coût', 'Scalabilité'],
    datasets: [
      {
        label: 'Produit A',
        data: [85, 70, 90, 75, 60, 80],
        borderColor: '#36a2eb',
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        pointBackgroundColor: '#36a2eb',
      },
      {
        label: 'Produit B',
        data: [70, 90, 65, 85, 80, 60],
        borderColor: '#ff6384',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        pointBackgroundColor: '#ff6384',
      }
    ]
  },
  options: {
    scales: {
      r: {
        beginAtZero: true,
        max: 100,
        ticks: { stepSize: 20 }
      }
    }
  }
});
```

---

## 3. Options Avancées

### 3.1 Échelles et Axes

```javascript
options: {
  scales: {
    x: {
      type: 'time',  // Échelle temporelle (nécessite chartjs-adapter-date-fns)
      time: {
        unit: 'month',
        displayFormats: { month: 'MMM yyyy' }
      },
      title: { display: true, text: 'Date' },
      grid: { display: false },
      ticks: {
        maxRotation: 45,
        maxTicksLimit: 12,
      }
    },
    y: {
      type: 'linear',  // ou 'logarithmic'
      beginAtZero: true,
      title: { display: true, text: 'Valeur (€)' },
      grid: { color: 'rgba(0,0,0,0.05)' },
      ticks: {
        callback: (value) => `${value} €`,
        stepSize: 1000,
      }
    },
    y1: {  // Axe Y secondaire
      type: 'linear',
      position: 'right',
      grid: { drawOnChartArea: false },
      title: { display: true, text: 'Pourcentage (%)' },
    }
  }
}
```

### 3.2 Animations

```javascript
options: {
  animation: {
    duration: 1500,
    easing: 'easeOutQuart',  // 'linear', 'easeInOutCubic', 'easeOutBounce'...
  },
  animations: {
    colors: {
      duration: 800,
      type: 'color',
    },
    y: {  // Animation par propriété
      duration: 1000,
      from: (ctx) => ctx.chart.scales.y.getPixelForValue(0),
    }
  },
  transitions: {
    active: { animation: { duration: 200 } },
    resize: { animation: { duration: 0 } },  // Pas d'animation au resize
  }
}
```

### 3.3 Plugins

```javascript
import ChartDataLabels from 'chartjs-plugin-datalabels';
import zoomPlugin from 'chartjs-plugin-zoom';
import annotationPlugin from 'chartjs-plugin-annotation';

Chart.register(ChartDataLabels, zoomPlugin, annotationPlugin);

options: {
  plugins: {
    // Data Labels (étiquettes sur les barres/points)
    datalabels: {
      anchor: 'end',
      align: 'end',
      color: '#444',
      font: { weight: 'bold', size: 11 },
      formatter: (value) => value + '€',
    },

    // Zoom & Pan
    zoom: {
      pan: { enabled: true, mode: 'xy' },
      zoom: {
        wheel: { enabled: true, modifierKey: 'ctrl' },
        pinch: { enabled: true },
        drag: { enabled: true, mode: 'x' },
        mode: 'x',
      },
      limits: {
        x: { minRange: 1000 * 60 * 60 * 24 },  // 1 jour minimum
      }
    },

    // Annotations (lignes de référence)
    annotation: {
      annotations: {
        line1: {
          type: 'line',
          xMin: '2024-06',
          xMax: '2024-06',
          borderColor: 'red',
          borderWidth: 2,
          borderDash: [6, 3],
          label: {
            display: true,
            content: 'Événement',
            position: 'start',
          }
        },
        box1: {
          type: 'box',
          xMin: '2024-03',
          xMax: '2024-05',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          borderWidth: 0,
        }
      }
    },

    // Légende
    legend: {
      position: 'top',
      labels: {
        usePointStyle: true,
        padding: 20,
        font: { size: 12 },
      },
      onClick: (e, legendItem, legend) => {
        // Comportement custom au clic
        const index = legendItem.datasetIndex;
        // ...
      }
    },

    // Tooltip
    tooltip: {
      enabled: true,
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0,0,0,0.8)',
      titleFont: { size: 14 },
      bodyFont: { size: 12 },
      padding: 12,
      cornerRadius: 4,
      callbacks: {
        title: (items) => `Période : ${items[0].label}`,
        label: (item) => `${item.dataset.label}: ${item.parsed.y} unités`,
        afterLabel: (item) => `---\nTendance: ${item.parsed.y > 50 ? '↑' : '↓'}`,
      }
    },

    // Barre de progression de chargement
    // subtitle: { display: true, text: '(Données mises à jour le 15/06/2024)' },
  }
}
```

---

## 4. Graphiques Mixtes (Mixed)

```javascript
new Chart(ctx, {
  type: 'bar',  // Type par défaut
  data: {
    labels: ['Jan', 'Fév', 'Mar', 'Avr'],
    datasets: [
      {
        label: 'Revenus',
        data: [3000, 4500, 3800, 5200],
        backgroundColor: 'rgba(54, 162, 235, 0.7)',
        order: 2,
      },
      {
        label: 'Marge (%)',
        data: [30, 35, 32, 38],
        type: 'line',
        borderColor: '#ff6384',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        fill: true,
        yAxisID: 'y1',  // Axe Y secondaire
        order: 1,
      }
    ]
  },
  options: {
    scales: {
      y: {
        beginAtZero: true,
        position: 'left',
        title: { display: true, text: 'Revenus (€)' },
      },
      y1: {
        beginAtZero: true,
        position: 'right',
        title: { display: true, text: 'Marge (%)' },
        grid: { drawOnChartArea: false },
        ticks: { callback: (v) => `${v}%` },
      }
    }
  }
});
```

---

## 5. Performance et Grands Volumes

```javascript
// Optimisations pour +10k points
options: {
  elements: {
    point: {
      radius: 0,          // Pas de points
      hitRadius: 5,       // Zone de clic simulée
      hoverRadius: 3,     // Visible seulement au hover
    },
    line: {
      borderWidth: 1,     // Trait fin
      tension: 0,         // Pas de lissage (coûteux)
    }
  },
  animation: {
    duration: 0,          // Désactiver les animations
  },
  parsing: false,         // Désactiver le parsing auto (données pré-traitées)
  normalized: true,
  datasets: {
    // Décimation (Chart.js v4+)
    // Automatique via le plugin decimation
  }
}

// Données pré-parsées (gains de perf majeurs)
new Chart(ctx, {
  data: {
    labels: [],
    datasets: [{
      data: [/* Float64Array */],
      // Pas de parsing nécessaire
    }]
  },
  options: { parsing: false }
});
```

---

## 6. Export (Image/PDF)

```javascript
// Export PNG natif
document.getElementById('downloadBtn').addEventListener('click', () => {
  const link = document.createElement('a');
  link.download = 'graphique.png';
  link.href = myChart.toBase64Image('image/png', 1); // 1 = qualité (0-1)
  link.click();
});

// Export JPEG
const jpegUrl = myChart.toBase64Image('image/jpeg', 0.8);

// Export PDF (via jsPDF)
import jsPDF from 'jspdf';
const pdf = new jsPDF();
pdf.addImage(myChart.toBase64Image(), 'PNG', 10, 10, 190, 100);
pdf.save('graphique.pdf');
```

---

## Pièges Courants (Pitfalls)

1. **Canvas qui se dédouble ou rend mal.**
   - *Erreur :* Le `<canvas>` a une taille CSS différente de ses attributs width/height.
   - *Correction :* Utiliser `responsive: true` et ne PAS fixer de width/height fixes en CSS. Chart.js gère le ratio.

2. **Données qui ne s'affichent pas.**
   - *Erreur :* Les données contiennent des `undefined` ou `null` — Chart.js les ignore silencieusement.
   - *Correction :* Filtrer avant : `data.filter(d => d !== null && d !== undefined)`.

3. **Graphique qui saute au resize.**
   - *Erreur :* `maintainAspectRatio: false` sans conteneur parent dimensionné.
   - *Correction :* Mettre le canvas dans un conteneur avec hauteur fixe : `<div style="height: 400px"><canvas></canvas></div>`.

4. **Plugin qui ne fonctionne pas.**
   - *Erreur :* Import du plugin sans l'enregistrer avec `Chart.register()`.
   - *Correction :* `Chart.register(monPlugin)` avant d'instancier le graphique.

5. **Lenteur avec beaucoup de datasets.**
   - *Erreur :* 20+ datasets avec 10 000 points chacun.
   - *Correction :* Activer `parsing: false`, désactiver animations, réduire le nombre de datasets ou regrouper par agrégation.

6. **Dates non reconnues sur l'axe X.**
   - *Erreur :* L'échelle `time` nécessite un adaptateur de dates.
   - *Correction :* Installer et importer `chartjs-adapter-date-fns` ou `chartjs-adapter-luxon`.

---

## Ressources

- [Documentation officielle Chart.js](https://www.chartjs.org/docs/)
- [Chart.js Samples](https://www.chartjs.org/samples/)
- [Chart.js Awesome (plugins & intégrations)](https://github.com/chartjs/awesome)
- [Chart.js GitHub](https://github.com/chartjs/Chart.js)

---

## Checklist

- [ ] Chart.js est importé et enregistré (`Chart.register(...registerables)`).
- [ ] Les plugins additionnels sont enregistrés avant l'instanciation.
- [ ] Le canvas est dans un conteneur dimensionné si `maintainAspectRatio: false`.
- [ ] Les animations sont adaptées au volume de données.
- [ ] L'export PNG est fonctionnel (bouton download).
- [ ] Les tooltips sont configurés (mode, callbacks).
- [ ] Les axes ont des titres et des unités.
- [ ] Les jeux de données mixtes utilisent le bon `yAxisID`.
