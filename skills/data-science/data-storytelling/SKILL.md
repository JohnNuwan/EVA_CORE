---
name: data-storytelling
description: "Data Storytelling : narration par les données — structure narrative (contexte, conflit, résolution), visualisation persuasive, annotations, flow de présentation, rapports exécutifs, pitch data-driven."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [data-storytelling, narration, dataviz, presentation, analytics, communication, persuasion]
    homepage: https://www.storytellingwithdata.com/
    related_skills: [dashboard-design, plotly, d3-js, chart-js, content-strategy]
prerequisites:
  commands: []
  pip_packages: []
---

# Compétence Data Storytelling — Raconter une Histoire avec les Données

## Vue d'ensemble

Le **Data Storytelling** est l'art de communiquer des insights à travers une narration structurée, combinant données, visualisations et récit. Ce n'est pas un simple rapport — c'est une histoire qui guide l'audience vers une conclusion et une action.

> *"Les données sont les faits. La visualisation est la preuve. L'histoire est le sens."*

**Les 3 piliers :**
1. **Données** (Data) : les faits, les chiffres, les analyses.
2. **Récit** (Narrative) : la structure qui relie les points.
3. **Visuels** (Visuals) : les graphiques qui rendent l'abstrait concret.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Présente des résultats d'analyse à une direction ou un client.
- Construit une présentation data-driven (slide deck, rapport).
- Veut convaincre avec des données (pitch, proposition de valeur).
- Souhaite améliorer l'impact de ses dashboards.
- A besoin de transformer un rapport technique en histoire compréhensible.
- Prépare un rapport annuel ou un executive summary.

---

## 1. La Structure Narrative en 3 Actes

### 1.1 Le Modèle Universel

```yaml
ACTE 1 : CONTEXTE (Setup)
  - Où en sommes-nous ?
  - Quelle est la situation actuelle ?
  - Quel est l'enjeu ?
  - → "Nos ventes sont en croissance régulière depuis 3 ans..."

ACTE 2 : CONFLIT (Insight)
  - Qu'est-ce qui a changé ?
  - Quel est le problème ou l'opportunité ?
  - Pourquoi c'est important ?
  - → "...mais un segment clé montre un ralentissement inquiétant."

ACTE 3 : RÉSOLUTION (Action)
  - Que faire ?
  - Quelle est la recommandation ?
  - Quel est l'impact attendu ?
  - → "En investissant 20% de plus sur ce segment, nous pouvons inverser la tendance."
```

### 1.2 Application Concrète

```yaml
Exemple : Dashboard Ventes

AVANT (pas de storytelling):
  Graphique montrant les ventes par région.
  "Voici les ventes par région. La région A est à 12M€, la B à 8M€..."
  → Aucune prise de décision possible.

APRÈS (storytelling):
  Acte 1 : "Notre croissance annuelle est de 15%, tirée par les régions historiques."
  Acte 2 : "Mais la région Sud perd 5% depuis 3 mois — 3 clients majeurs sont passés chez un concurrent."
  Acte 3 : "Recommandation : déployer un account manager dédié pour reconquérir ces 3 comptes clés. Impact estimé : +2.5M€ annuels."
  → Décision claire, action immédiate.
```

---

## 2. Le Cycle de Narration

### 2.1 Les 6 Étapes

```yaml
1. EXPLORER — Comprendre les données
   - Analyse exploratoire multidimensionnelle
   - Quels patterns, outliers, tendances ?
   - Qu'est-ce qui est surprenant ?

2. IDENTIFIER — Trouver l'histoire
   - Quel est le message central ?
   - Quelle est la question stratégique ?
   - Quel changement ou insight est le plus important ?

3. CONDENSER — Simplifier sans simplifier
   - Réduire à 1 message principal
   - 2-3 messages secondaires de support
   - Éliminer le bruit, garder le signal

4. STRUCTURER — Construire l'arc narratif
   - Acte 1 : Où étions-nous ? Où sommes-nous ?
   - Acte 2 : Pourquoi ce changement ?
   - Acte 3 : Que faire maintenant ?

5. VISUALISER — Créer les visuels qui soutiennent l'histoire
   - Chaque graphique = une idée
   - Annoter ce qui est important
   - Guider l'œil vers la conclusion

6. LIVRER — Présenter avec impact
   - Adapter le ton au public
   - Anticiper les questions
   - Appeler à l'action
```

### 2.2 La Question à laquelle Chaque Étape Répond

| Étape | Question | Output |
|-------|----------|--------|
| Explorer | "Que disent les données ?" | Insights bruts |
| Identifier | "Quelle est l'histoire principale ?" | Message clé |
| Condenser | "Quel est l'essentiel ?" | Storyline concise |
| Structurer | "Comment raconter ?" | Plan narratif |
| Visualiser | "Comment montrer ?" | Slides / visuels |
| Livrer | "Comment convaincre ?" | Présentation |

---

## 3. Techniques de Narration Visuelle

### 3.1 L'Annotation Stratégique

```yaml
Technique : Guider l'œil vers l'insight

AVANT (graphique nu):
  Line chart avec 12 mois de ventes.
  "Voici l'évolution..." → le public doit chercher l'info.

APRÈS (graphique annoté):
  Line chart avec :
  - 👉 Flèche pointant le mois d'inflexion ("Lancement produit")
  - 🔴 Cercle autour du pic de juin ("Campagne marketing")
  - 📊 Zone ombrée pour la période de croissance exceptionnelle
  - Text box : "+32% en 3 mois après le lancement"
  → L'insight est immédiat, même sans lire le titre.
```

### 3.2 Le "Before / After" (Avant / Après)

```yaml
Structure puissante pour montrer l'impact :

ACTE 1 : AVANT
  - "Situation initiale : 35% de taux d'attrition client"
  - Graphique : ligne descendante
  - Contexte : "3 ans de baisse continue, perte estimée à 2M€"

ACTE 2 : L'INTERVENTION
  - "Nous avons lancé le programme de fidélisation Q3 2023"
  - Marqueur vertical sur la timeline

ACTE 3 : APRÈS
  - "Résultat : le taux d'attrition est passé à 12% en 9 mois"
  - Graphique : ligne ascendante après l'intervention
  - ROI : "Chaque € investi en a rapporté 3.40€"
```

### 3.3 La Réduction Progressive (Progressive Disclosure)

```yaml
Principe : Montrer l'information par couches, pas tout en même temps.

Slide 1 : "En un coup d'œil"
  Un seul chiffre : "Ventes 2024 : 52.4M€ (+18%)"
  → Capture l'attention

Slide 2 : "La composition"
  3 barres : "Par segment : Grand compte (+25%), PME (+12%), Pro (-3%)"
  → Montre la structure

Slide 3 : "Le détail qui fait la différence"
  Focus sur Grand compte : "Le segment Grand compte représente 60% de la croissance"
  → Révèle l'insight principal

Slide 4 : "L'action"
  "Recommandation : doubler l'effort commercial sur les Grands Comptes"
  → Appelle à l'action
```

### 3.4 La Carte de Score (Scorecard)

```yaml
Présenter un résumé exécutif en quelques chiffres :

┌──────────────────────────────────────────────┐
│        📊 RÉSULTATS Q1 2024                  │
├──────────────────────────────────────────────┤
│ CA     52.4M€  ▲ +18%  vs Q1 2023   [✓]     │
│ Marge  42.3%   ▲ +2.1pp          [✓]         │
│ NPS    72      ▶ 0pt vs Q4 2023   [→]        │
│ Stock  18.2M€  ▼ +5% (surstock)   [⚠]       │
└──────────────────────────────────────────────┘

Légende : [✓] Objectif atteint  [→] Stable  [⚠] Attention  [✗] Critique
```

---

## 4. Data Storytelling par Audience

### 4.1 Pour les Dirigeants (Executive Summary)

```yaml
Besoins :
  - Temps limité (30 secondes pour capter l'attention)
  - Vision macro, pas de détails techniques
  - Décision rapide

Format :
  - 1 slide = 1 message
  - KPI principal visible sans lire
  - 3-4 slides maximum
  - Recommandation explicite

Exemple :
  Slide 1 : "Le chiffre : CA en hausse de 18%, mais marge sous pression"
  Slide 2 : "Pourquoi : hausse des coûts matières premières (+8%)"
  Slide 3 : "Action : négocier les contrats fournisseurs et ajuster les prix de vente de 3%"
  Slide 4 : "Impact : maintien de la marge à 42%, gain net estimé : 1.2M€"
```

### 4.2 Pour les Analystes (Rapport Technique)

```yaml
Besoins :
  - Accès aux données brutes
  - Méthodologie transparente
  - Possibilité de reproduire les calculs

Format :
  - Contexte et objectifs
  - Méthodologie et sources
  - Résultats (graphiques + tableaux)
  - Annexes et données détaillées
  - Code / notebooks en lien

Exemple :
  "Analyse de la cohorte des clients acquis en Q3 2023.
  Méthodologie : analyse de survie (Kaplan-Meier) avec intervalle de confiance à 95%.
  Résultat : le taux de rétention à 12 mois est de 68% (IC 95% : 65%-71%).
  Voir notebook : analysis/retention_cohort.ipynb"
```

### 4.3 Pour les Clients (Proposition Commerciale)

```yaml
Besoins :
  - Compréhension rapide de la valeur
  - Cas d'usage concret
  - Preuve de l'impact

Format :
  - Situation actuelle (leur douleur)
  - Solution proposée (votre approche)
  - Résultats attendus (chiffrés)
  - Cas client similaire (preuve sociale)

Exemple :
  "Situation : Vous perdez 15% de clients chaque année.
  Solution : Notre modèle prédictif identifie les clients à risque 3 mois à l'avance.
  Résultat chez un client similaire : réduction de 40% de l'attrition, ROI 4.2x en 18 mois.
  Proposition : pilote de 3 mois sur votre segment Grands Comptes."
```

---

## 5. Guide de Design des Slides

### 5.1 Slide Type pour une Histoire

```yaml
┌───────────────────────────────────────────────┐
│  TITRE : Le message principal (1 ligne)        │
│  Sous-titre : le contexte (optionnel)          │
├───────────────────────────────────────────────┤
│                                               │
│         [VISUEL : Graphique/Image]            │
│         - Annoté, un insight par slide        │
│         - Légende claire, unités visibles     │
│         - Palette cohérente                   │
│                                               │
├───────────────────────────────────────────────┤
│  💡 Insight : 1 ligne explicative             │
│  📊 Données : source et date                 │
└───────────────────────────────────────────────┘
```

### 5.2 Règles de Présentation

```yaml
Police :    Sans-serif, ≥24pt pour le titre, ≥18pt pour le texte
Couleurs :  Neutre (gris, bleu foncé) + 1 couleur d'accent + rouge/vert si tendances
Contraste : Texte sombre sur fond clair (lisibilité projecteur)
Images :    Haute résolution, éviter les cliparts
Animation : Subtiles (apparitions, transitions), jamais de rotations 3D
Temps :     max 1 slide par minute de présentation

Règle des tiers visuels :
  1/3 supérieur : titre + message clé
  1/3 milieu : visualisation principale
  1/3 inférieur : insight + source
```

---

## 6. Pièges et Anti-Patterns

### 6.1 Pièges Narratifs

```yaml
❌ "Data dump" — Lancer 50 graphiques sans histoire
   → Le public se noie, aucune décision

❌ "Cherry picking" — Montrer uniquement les chiffres qui arrangent
   → Perte de crédibilité à la première question

❌ "Corrélation = causalité" — "Les ventes de glace augmentent avec les noyades"
   → Ne pas confondre corrélation et causalité (variable cachée : la météo)

❌ "Overclaiming" — "Notre solution augmente les ventes de 300% !"
   → Sans contexte ni benchmark, ça sonne faux

❌ "Le graphique mystère" — Graphique complexe sans explication
   → Perte de l'audience dès les premières slides

❌ "Slide encombrée" — 5 graphiques + 3 paragraphes par slide
   → L'œil ne sait pas où regarder, charge cognitive maximale
```

### 6.2 Pièges Visuels

```yaml
❌ 3D pie chart avec 12 parts
❌ Double échelle Y non annoncée
❌ Légende qui oblige à faire des allers-retours
❌ Trop de décimales (12.34567 → 12.3 suffit)
❌ Palettes arc-en-ciel
❌ Axe Y tronqué qui exagère les tendances
❌ Barres qui ne commencent pas à zéro
```

---

## 7. Exemples de Structures Complètes

### 7.1 Analyse de Performance Commerciale

```yaml
TITRE : "Comment nous avons doublé notre CA en 2 ans"

ACTE 1 — CONTEXTE
  "Il y a 2 ans, nous étions en perte de vitesse"
  📉 Graphique : CA en baisse (-5% / an)
  "Notre portefeuille client vieillissait, les renouvellements s'effondraient"

ACTE 2 — CONFLIT/INSIGHT
  "En analysant les données, nous avons découvert un segment inexploité"
  🔍 Graphique : Segmentation client → "Moyennes entreprises, secteur tech"
  "Ces clients avaient un potentiel 3x supérieur aux autres segments"

ACTE 3 — ACTION
  "Nous avons pivoté notre stratégie vers ce segment"
  📊 Graphique : CA post-pivot → "+40% en 6 mois"
  "Résultat : 52M€ de CA à fin 2024, objectif 80M€ en 2026"

CONCLUSION
  "Notre recommandation : doubler l'effort commercial sur ce segment"
  "Investissement : 500k€ → ROI projeté : 6x à 18 mois"
```

### 7.2 Rapport d'Impact d'une Campagne Marketing

```yaml
TITRE : "Campagne Automne 2024 — Résultats et Recommandations"

ACTE 1 — OBJECTIF
  "Objectif : générer 10 000 leads qualifiés en 8 semaines"
  "Budget : 150 000€ — ROI cible : 4x"

ACTE 2 — RÉSULTATS
  "12 500 leads générés (+25% vs objectif)"
  📊 Graphique : lead gen par semaine (courbe + objectif en pointillé)
  "Coût par lead : 8.50€ vs budget 15€ (-43%)"
  "Top 3 canaux : LinkedIn Ads (45%), SEO (30%), Email (15%)"

ACTE 3 — INSIGHT
  "Le canal 'influenceurs tech' a sous-performé : 500 leads pour 25k€"
  "En revanche, les webinaires techniques ont un taux de conversion 3x supérieur"
  📊 Graphique : ROI par canal

ACTE 4 — RECOMMANDATION
  "Pour Q1 2025 : réallouer 30% du budget influenceurs vers les webinaires"
  "Impact estimé : +20% leads à budget constant"
```

---

## 8. Outils et Frameworks de Support

```yaml
Outils de création :
  - Présentations : PowerPoint / Google Slides / Keynote / Canva
  - Visualisation : Tableau, Power BI, Plotly, Observable, D3.js
  - Narration interactive : Observable Framework, Streamlit, Dash

Frameworks narratifs (empruntés au cinéma/journalisme) :
  - Pyramide inversée (journalisme) : conclusion → détails
  - Hero's Journey (monomythe) : situation → défi → triomphe
  - STAR (Situation, Task, Action, Result)
  - SCQA (Situation, Complication, Question, Answer)

Métriques de succès d'une présentation :
  - Taux de rétention du message principal (rappel à J+7)
  - Nombre de questions posées
  - Actions décidées suite à la présentation
```

---

## Pièges Courants (Pitfalls)

1. **Commencer par la solution, pas par le problème.**
   - *Erreur :* "Voici notre recommandation" sans avoir établi le contexte.
   - *Correction :* Toujours commencer par "Où en sommes-nous ? Quel est le problème ?"

2. **Trop de données tue la donnée.**
   - *Erreur :* Vouloir montrer toute l'analyse dans la peur de "manquer quelque chose".
   - *Correction :* 1 slide = 1 message. Le reste va en annexe.

3. **Oublier l'appel à l'action.**
   - *Erreur :* Finir sur un graphique sans conclusion claire.
   - *Correction :* Toujours terminer par "Donc nous devons...".

4. **Jargon technique avec des non-initiés.**
   - *Erreur :* "Le p-value du test A/B est de 0.023 avec un intervalle de confiance à 95%."
   - *Correction :* "Le test A/B montre que la version B performe 15% mieux, avec 95% de certitude."

5. **Négliger le design visuel.**
   - *Erreur :* Données parfaites mais slide moche → crédibilité diminuée.
   - *Correction :* Appliquer au moins les bases : bonne typo, palette limitée, aération.

6. **Ignorer l'audience.**
   - *Erreur :* Utiliser le même support pour la direction générale et les analystes.
   - *Correction :* Adapter le niveau de détail, le ton, et les visuels à chaque audience.

---

## Ressources

- **Livres :** *Storytelling with Data* (Cole Nussbaumer Knaflic), *The Visual Display of Quantitative Information* (Edward Tufte)
- **Blog :** [storytellingwithdata.com](https://www.storytellingwithdata.com/)
- **Newsletter :** [Nightingale (Data Visualization Society)](https://nightingaledvs.com/)
- **Conférences :** Tapestry Conference, Outlier, Data Visualization Summit
- **Inspiration :** [FlowingData](https://flowingdata.com/), [Information is Beautiful](https://informationisbeautiful.net/)

---

## Checklist

- [ ] L'histoire suit une structure en 3 actes (contexte → conflit → résolution).
- [ ] Il y a UN message principal par slide / par dashboard.
- [ ] Chaque graphique illustre EXACTEMENT un point de la narration.
- [ ] Les axes, unités et légendes sont clairs pour le non-initié.
- [ ] Les insights importants sont annotés (flèches, textes, surlignage).
- [ ] L'appel à l'action est explicite ("Donc nous devons...").
- [ ] Le design visuel est sobre (palette limitée, police lisible, aération).
- [ ] L'audience cible est identifiée (ton, niveau de détail, format adapté).
- [ ] Les sources des données sont citées.
- [ ] La présentation a été testée (5 secondes rule, relecture par un pair).
