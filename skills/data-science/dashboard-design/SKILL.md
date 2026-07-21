---
name: dashboard-design
description: "Conception de tableaux de bord (Dashboards) : UX, sélection de KPIs, layout, hiérarchie visuelle, couleurs, typographie, accessibilité, performance cognitive, patterns de dashboarding (opérationnel, stratégique, analytique)."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [dashboard, design, ux, kpi, layout, dataviz, information-design, ui]
    homepage: https://www.tableau.com/learn/whitepapers/dashboard-design-principles
    related_skills: [tableau, powerbi, plotly, data-storytelling, award-winning-dashboards]
prerequisites:
  commands: []
  pip_packages: []
---

# Compétence Conception de Dashboards — Design, UX, KPIs & Patterns

## Vue d'ensemble

Un dashboard est une interface visuelle qui condense les indicateurs clés d'une activité sur un seul écran, permettant une prise de décision rapide et éclairée. Contrairement à un rapport, un dashboard est conçu pour être **lu en un coup d'œil** (scan), pas pour être lu comme un document.

**Les 3 types de dashboards :**

| Type | Cadence | Audience | Contenu |
|------|---------|----------|---------|
| **Opérationnel** | Temps réel / Horaire | Opérateurs, managers terrain | KPIs actuels, alertes, flux |
| **Stratégique** | Hebdo / Mensuel | Direction, executives | Tendances, objectifs, santé globale |
| **Analytique** | À la demande | Analystes, data scientists | Exploration, drill-down, corrélations |

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Conçoit ou critique un tableau de bord (quel que soit l'outil).
- Veut structurer des KPIs par priorité et pertinence.
- Cherche les bonnes pratiques de layout, couleurs et typographie.
- Souhaite rendre ses dashboards accessibles et non-ambigus.
- A besoin de choisir le bon type de visualisation pour chaque KPI.
- Veut appliquer les principes de la charge cognitive et de la hiérarchie visuelle.

---

## 1. Fondamentaux du Design de Dashboard

### 1.1 Les 5 Principes Fondamentaux

1. **Clarté avant tout** — Un dashboard ne doit pas nécessiter d'explications. 5 secondes suffisent pour comprendre le message principal.
2. **Hiérarchie visuelle** — L'œil doit être guidé : KPI principal → sous-KPIs → détails → données brutes.
3. **Contexte pertinent** — Un chiffre sans contexte n'est pas interprétable (période précédente, objectif, seuil).
4. **Un écran, un objectif** — Si vous avez besoin de scroller, créez un second dashboard.
5. **Performance** — Un dashboard qui met 10 secondes à charger échoue (max 3s).

### 1.2 Le Pattern Z de Lecture

```
┌──────────────────────────────────────────────┐
│  ZONE 1 : En-tête                            │
│  Titre, période, filtres principaux          │
│  ═══════════════════════════════════════════  │
├──────────────┬───────────────────────────────┤
│              │                               │
│  ZONE 2 :    │  ZONE 3 :                     │
│  KPI #1      │  KPI #2                       │
│  (chiffre    │  (graphique tendance)         │
│  clé)        │                               │
│              │                               │
├──────────────┴───────────────────────────────┤
│  ZONE 4 : Détail / Tableau / Drill-down     │
│  ═══════════════════════════════════════════  │
└──────────────────────────────────────────────┘
```

---

## 2. Sélection des KPIs

### 2.1 Le Framework SMART

| Critère | Question | Exemple |
|---------|----------|---------|
| **S**pécifique | Mesure-t-il exactement ce qu'on veut ? | "Taux de conversion" pas "Performance" |
| **M**esurable | Est-il quantifiable ? | % ou €, pas "satisfaction client vague" |
| **A**tteignable | La donnée est-elle disponible ? | Source fiable, fréquence OK |
| **R**elevant | Est-il pertinent pour la décision ? | Impact direct sur l'objectif métier |
| **T**emporel | A-t-il une dimension temporelle ? | Comparaison N/N-1, tendance |

### 2.2 Catégories de KPIs

```yaml
Financiers:
  - Chiffre d'affaires
  - Marge brute / nette
  - EBITDA
  - Cash flow
  - ROI / ROAS

Opérationnels:
  - OEE (Overall Equipment Effectiveness)
  - Temps de cycle
  - Taux de rebut
  - Productivité (pièces/heure)
  - Taux de service

Clients:
  - NPS (Net Promoter Score)
  - Taux de rétention
  - Coût d'acquisition (CAC)
  - Valeur à vie (LTV)
  - CSAT (satisfaction)

RH:
  - Turnover
  - Taux d'absentéisme
  - Heures de formation
  - Engagement score

Marketing:
  - Taux de conversion
  - Coût par lead (CPL)
  - ROI campagne
  - Trafic / sessions
```

### 2.3 La Règle des 5-7 KPIs

Un dashboard efficace = **5 à 7 KPIs maximum**. Au-delà, l'utilisateur est en surcharge cognitive.

**Priorisation :**
1. **KPI Principal** — le chiffre qui résume tout (ex: "Ventes du jour").
2. **3-4 KPIs secondaires** — qui expliquent le principal.
3. **1-2 KPIs contextuels** — benchmark, objectif, alerte.

---

## 3. Choix des Visualisations

### 3.1 Guide de Sélection

```
QUELLE HISTOIRE RACONTEZ-VOUS ?
│
├── Comparaison → Barres (groupées/empilées) ou Radar
├── Composition → Pie/Doughnut (peu d'items) ou Stacked Bar/Area (≥5 items)
├── Distribution → Histogramme, Boxplot, Violin
├── Corrélation → Scatter Plot
├── Tendance → Line Chart (time series) ou Area
├── Flux → Sankey, Sunburst, Treemap
├── Partie-de-Tout → Pie (2-3 catégories) ou Treemap (beaucoup de catégories)
├── Géographie → Carte choroplèthe, Points, Heatmap
├── Rang → Barres horizontales triées
└── Hiérarchie → Treemap, Sunburst, Dendrogram
```

### 3.2 Anti-Patterns (À éviter)

```yaml
❌ Pie chart 3D : angles impossibles à comparer
❌ Radar > 5 dimensions : illisible
❌ Barres verticales avec labels inclinés : cou cassé
❌ Trop de couleurs (> 6) : confusion
❌ Dual axis trompeur : échelles différentes sur le même graphique
❌ 3D inutile : ne fait pas passer plus d'information, rend la lecture difficile
❌ Graphique beignet redondant : pie + barres pour la même chose
❌ Trop de décimales : 12.34567% vs 12.3% — la lisibilité prime
```

### 3.3 Raccourcis Visuels

```yaml
Trend arrows:
  ↑ ↗ → ↘ ↓ : tendance sans graphique pour les KPIs simples
  → Vert stable, orange alerte, rouge critique

Sparklines:
  Mini-graphique dans une cellule de tableau
  Montre la tendance sur 30 jours sans prendre de place

Bullet chart:
  Alternative compacte aux jauges
  Affiche : valeur actuelle | objectif | plages (bon/acceptable/mauvais)

Heatmap:
  Tableau avec intensité de couleur
  Parfait pour : jour × heure, produit × région
```

---

## 4. Layout et Structure

### 4.1 Grille et Alignement

```yaml
Grille recommandée:
  - Mobile: 4 colonnes (stack)
  - Desktop: 12 ou 16 colonnes
  - Gouttière: 16-24px entre les éléments
  - Padding: 24-32px autour du dashboard

Tailles de cartes:
  - KPI principal: 1/3 ou 1/2 de la largeur
  - KPI secondaires: 1/4 ou 1/6
  - Graphiques principaux: 2/3 ou pleine largeur
  - Tableau de détail: pleine largeur

Zones prioritaires (Pattern F ou Z):
  Coin supérieur gauche → KPI le plus important
  Les yeux balayent en F (occi-dental) ou Z (selon culture)
```

### 4.2 Modèles de Layout

**Layout 1 : Opérationnel (haut débit)**

```
┌──────────────────────────────────────────────────┐
│  [KPI A]  [KPI B]  [KPI C]  [KPI D]  [KPI E]   │  ← KPIs en une rangée
├─────────────────────┬────────────────────────────┤
│                     │                            │
│  Graphique Tendance │  Pie / Barres              │
│  (Line chart)       │  (Composition)             │
│                     │                            │
├─────────────────────┴────────────────────────────┤
│  Tableau de données / Détail                     │
└──────────────────────────────────────────────────┘
```

**Layout 2 : Stratégique (focus executive)**

```
┌──────────────────────────────────────────────────┐
│           [KPI PRINCIPAL — GROS CHIFFRE]         │
│           Objectif: XXXX  |   Réalisé: XXXX     │
├────────────────┬────────────────┬────────────────┤
│  [KPI A]       │  [KPI B]       │  [KPI C]       │
│  +15% YoY      │  -3% Vs obj    │  12.3% taux    │
│  ▲ tendance    │  ▼ alerte      │  → stable      │
├────────────────┴────────────────┴────────────────┤
│  [Graphique Principal — Tendance des KPIs]      │
├────────────────────┬────────────────────────────┤
│  [Répartition]     │  [Top 5 / Bottom 5]        │
└────────────────────┴────────────────────────────┘
```

**Layout 3 : Analytique (exploration)**

```
┌───────────────┬──────────────────────────────────┐
│               │    [Graphique Principal]          │
│  [Filtres]    │    Zoom/Pan/Drill-down            │
│               │                                   │
│  --           ├──────────────────────────────────┤
│  Catégorie    │    [Tableau Détail avec tri]      │
│  Période      │                                   │
│  Région       │                                   │
└───────────────┴──────────────────────────────────┘
```

---

## 5. Couleurs et Typographie

### 5.1 Palettes Recommandées

```yaml
Palette fonctionnelle:
  🔵 Primaire (info/neutre):  #2c7fb8  #253494
  🟢 Positif (hausse, bon):    #2ecc71  #27ae60
  🟡 Alerte (attention):       #f39c12  #f1c40f
  🔴 Négatif (baisse, critique): #e74c3c  #c0392b
  ⚪ Neutre:                   #95a5a6  #bdc3c7

Palettes catégorielles (max 6 couleurs):
  - Tableau 10: bleu, orange, vert, rouge, violet, marron
  - Category10 (D3): #1f77b4 #ff7f0e #2ca02c #d62728 #9467bd #8c564b
  - Viridis (séquentiel): du violet au jaune
  - Couleurs Corporate: adapter à la charte de l'entreprise

Accessibilité:
  - Contraste min WCAG AA: 4.5:1 (texte normal), 3:1 (grand texte)
  - Éviter rouge+vert (daltonisme 8% des hommes)
  - Tester en niveaux de gris
  - Ajouter des textures/patterns en complément des couleurs
  - Outils: ColorBrewer, Coolors, WebAIM Contrast Checker
```

### 5.2 Typographie

```yaml
Police:
  - Sans-serif (Inter, Roboto, Open Sans, Lato) — meilleure lisibilité écran
  - Éviter les polices serif pour les titres et chiffres
  - Police à chasse fixe pour les nombres (tableaux)

Hiérarchie:
  - Titre dashboard: 28-36px, Bold
  - Titre de carte: 16-20px, Semi-bold
  - Valeur KPI: 36-48px, Bold
  - Étiquette KPI: 12-14px, Regular
  - Données tableau: 11-13px
  - Axes/légendes: 11-12px

Espacement:
  - Hauteur de ligne: 1.4-1.6x la taille de police
  - Espace entre sections: 24-32px
  - Padding interne des cartes: 16-24px
```

---

## 6. Interactivité

### 6.1 Types d'Interaction

```yaml
Filter Action:
  - Cliquer sur une valeur filtre les autres graphiques
  - Essentiel pour l'exploration
  - Indiquer visuellement l'élément sélectionné (highlight)

Highlight Action:
  - Survol d'une valeur → surligne les occurrences associées
  - Pas de modification des autres graphiques

Drill-down / Drill-through:
  - Double-clic → niveau de détail plus fin (An → Mois → Jour)
  - Navigation vers une page dédiée (drill-through)

Tooltip:
  - Afficher valeur exacte, variation, contribution
  - Ajouter un mini sparkline dans le tooltip si pertinent

URL Actions:
  - Navigation vers un rapport externe, une fiche produit, etc.
  - Passer les paramètres de contexte dans l'URL

Reset / Clear:
  - Bouton pour réinitialiser tous les filtres
  - Indispensable pour revenir à la vue par défaut
```

### 6.2 Bonnes Pratiques d'UX

```yaml
Filtres:
  - Placer en haut du dashboard (zone de contrôle)
  - Utiliser des presets (7 jours, 30 jours, Ce mois-ci)
  - Limiter à 3-4 filtres simultanés
  - Afficher le nombre d'éléments sélectionnés

Feedback:
  - Indiquer le chargement (spinner/skeleton)
  - Afficher "Aucune donnée" au lieu d'un graphique vide
  - Montrer quand les données ont été mises à jour
  - Feedback visuel au clic (état actif, hover)

Mobile:
  - Single column layout
  - KPIs les plus importants en haut
  - Toucher ≥ 44px pour les cibles tactiles
  - Éviter les interactions complexes (drag, hover)
```

---

## 7. Performance Cognitive

### 7.1 Principes de la Charge Cognitive

1. **Effet de supériorité du pictural** — Un graphique est compris plus vite qu'un tableau de chiffres.
2. **Loi de l'économie gestalt** — L'œil organise visuellement les éléments proches en groupes logiques.
3. **Principe de prégnance** — La forme la plus simple est perçue en premier.
4. **Effet de récence** — Les éléments placés en fin de lecture sont mieux mémorisés (dernier KPI).

### 7.2 Réduire la Charge Cognitive

```yaml
À FAIRE:
  - Un message principal par dashboard
  - Couleurs cohérentes (rouge = problème partout)
  - Annotations sur les points clés (flèches, textes)
  - Pré-calculer et afficher les insights (pas juste les données)
  - Utiliser des titres qui résument (ex: "Les ventes sont en hausse de 15%")

À ÉVITER:
  - Changer d'échelle entre deux graphiques comparables
  - Utiliser des légendes quand les labels directs suffisent
  - Afficher toutes les décimales
  - Mettre plusieurs objectifs sur le même dashboard
```

---

## 8. Tests et Validation

### 8.1 Protocole de Test

```yaml
Test du 5-secondes:
  1. Montrer le dashboard 5 secondes
  2. Demander : quel est le message principal ?
  3. Si la réponse n'est pas immédiate → redesign

Test du hall de gare:
  1. Une personne qui passe dans le couloir voit-elle l'info essentielle ?
  2. Le KPI principal doit être visible de loin

Checklist d'audit:
  [ ] Le titre est explicite ("Ventes Q1 2024" pas "Dashboard")
  [ ] L'unité de chaque mesure est visible
  [ ] La période est indiquée
  [ ] Les couleurs ont une signification cohérente
  [ ] Les graphiques ont un titre
  [ ] Les axes sont étiquetés
  [ ] Les comparaisons sont contextualisées (vs N-1, vs budget)
  [ ] Le dashboard fonctionne sans défilement (above the fold)
  [ ] Les tooltips sont utiles (pas de répétition du titre)
  [ ] Les valeurs aberrantes ou seuils critiques sont annotés
```

---

## Pièges Courants (Pitfalls)

1. **Dashboard fourre-tout.**
   - *Erreur :* Mettre tous les KPIs disponibles sur un seul écran par peur d'en oublier.
   - *Correction :* Un dashboard = un objectif. Les KPIs non essentiels vont dans un rapport dédié.

2. **Absence de hiérarchie visuelle.**
   - *Erreur :* Tous les éléments ont la même taille et la même couleur.
   - *Correction :* Le KPI principal doit être 2-3x plus grand que les secondaires.

3. **Chiffres sans contexte.**
   - *Erreur :* Afficher "125 000 €" sans rien d'autre.
   - *Correction :* "125 000 € ↑ +15% vs N-1 (objectif : 110 000 € ✓)".

4. **Surcharge de couleurs.**
   - *Erreur :* Chaque catégorie a une couleur différente, rendant le dashboard criard.
   - *Correction :* 2-3 couleurs fonctionnelles (positif, neutre, négatif) + 1 couleur d'accent.

5. **Dashboard non maintenu.**
   - *Erreur :* Les sources de données changent mais les KPIs ne sont pas mis à jour.
   - *Correction :* Programmer une revue trimestrielle des dashboards.

6. **Mauvais choix de visualisation.**
   - *Erreur :* Pie chart avec 12 catégories, ou barres pour une tendance temporelle.
   - *Correction :* Consulter le guide de sélection (section 3.1).

---

## Ressources

- [Stephen Few — Information Dashboard Design](https://www.stephen-few.com/)
- [Tufte — The Visual Display of Quantitative Information](https://www.edwardtufte.com/)
- [Tableau — Dashboard Design Guidelines](https://www.tableau.com/learn/articles/dashboard-design-principles)
- [UX Planet — Dashboard Design Patterns](https://uxplanet.org/dashboard-design-patterns-3c3b6e8d8b5f)
- [Google Material Design — Data Visualization](https://material.io/design/communication/data-visualization.html)

---

## Checklist

- [ ] Le dashboard répond à UN objectif métier précis.
- [ ] Les 5-7 KPIs les plus importants sont sélectionnés.
- [ ] La hiérarchie visuelle guide l'œil (taille, couleur, position).
- [ ] Chaque chiffre a un contexte (comparaison, objectif, seuil).
- [ ] La palette de couleurs est fonctionnelle et accessible (WCAG AA).
- [ ] Les filtres sont en haut et les interactions sont cohérentes.
- [ ] Le layout tient sur un écran (pas de scroll nécessaire).
- [ ] Les axes et unités sont étiquetés sur tous les graphiques.
- [ ] Le test des 5 secondes est passé.
- [ ] Un bouton de réinitialisation des filtres est présent.
