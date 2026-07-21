---
name: tableau
description: "Tableau Desktop / Prep / Server / Public : connexions de données, calculs tableaux, LOD, paramètres, dashboards, histoires, API REST, Hyper, Tableau Extensions, Embedded Analytics."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [tableau, dataviz, bi, dashboard, lod, calculated-fields, etl, analytics]
    homepage: https://www.tableau.com/
    related_skills: [powerbi, dashboard-design, data-storytelling, plotly]
prerequisites:
  commands: []
  pip_packages: []
---

# Compétence Tableau — Business Intelligence & Visualisation de Données

## Vue d'ensemble

**Tableau** est la plateforme de Business Intelligence et visualisation de données la plus utilisée en entreprise. Elle permet de connecter, préparer, analyser et partager des données à travers des dashboards interactifs sans écrire de code (bien que des calculs avancés soient possibles avec des formules Tableau).

**Écosystème :**

- **Tableau Desktop** : outil de création de visualisations (licence Creator).
- **Tableau Prep** : outil de préparation/nettoyage des données.
- **Tableau Server / Cloud** : plateforme de partage et collaboration.
- **Tableau Public** : version gratuite pour données publiques.
- **Tableau Bridge** : connecteur vers bases de données on-premise.
- **Tableau Mobile** : accès aux dashboards sur mobile.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Travaille sur un projet de BI d'entreprise (Tableau Server/Cloud).
- Crée des dashboards interactifs avec des sources de données multiples.
- A besoin de calculs avancés : LOD expressions, table calculations, sets, parameters.
- Veut préparer/nettoyer des données avec Tableau Prep.
- Cherche à intégrer Tableau dans une application web (Embedded Analytics).
- Souhaite automatiser des tâches via l'API REST Tableau.

---

## 1. Connexion aux Sources de Données

### 1.1 Types de Connexions

| Type | Connexion | Usage |
|------|-----------|-------|
| **Fichier** | Excel, CSV, PDF, Spatial (Shapefile, GeoJSON) | Fichiers locaux ou partagés |
| **Base relationnelle** | SQL Server, PostgreSQL, MySQL, Oracle, Snowflake | Connexion directe ou extraction |
| **Cloud** | Google BigQuery, AWS Athena, Azure Synapse, Databricks | Requêtes pay-per-query |
| **Cube OLAP** | SAP HANA, Essbase, Microsoft Analysis Services | Données multidimensionnelles |
| **Web** | Google Sheets, OData, REST API | Sources en ligne |
| **Autres** | Splunk, Cloudera, Hortonworks, MongoDB (via BI Connector) | Sources spécialisées |

### 1.2 Live vs Extraction (Hyper)

```python
# Mode Live : Requêtes en temps réel sur la base
# Avantage : données toujours à jour
# Inconvénient : performance dépend du serveur de base

# Mode Extract : Copie locale en format .hyper (colonnaire)
# Avantage : performances ultra-rapides, fonctions supplémentaires
# Inconvénient : nécessite un rafraîchissement

# Génération d'extract en ligne de commande (tabcmd)
tabcmd refreshextracts --datasource "Ventes" --workbook "Dashboard_Ventes"
```

### 1.3 Tableau Prep — Préparation des Données

Tableau Prep Builder permet de nettoyer et structurer les données visuellement :

- **Nettoyage** : suppression des NULL, correction des types, split de colonnes.
- **Agrégation** : groupement, pivot, rollup.
- **Jointure / Union** : fusion de tables.
- **Aggrégation** : cumuls, moyennes glissantes.
- **Prédiction** : remplissage de valeurs manquantes.

```python
# Via l'API Hyper (Python/TableauHyperAPI)
from tableauhyperapi import HyperProcess, Connection, TableDefinition, SqlType, Telemetry

with HyperProcess(Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
    with Connection(endpoint=hyper.endpoint, database="extract.hyper") as conn:
        conn.execute_command("""
            CREATE TABLE ventes AS
            SELECT region, SUM(montant) as total
            FROM source_data
            GROUP BY region
        """)
```

---

## 2. Concepts Fondamentaux Tableau

### 2.1 Dimensions vs Mesures

| Concept | Icône | Description | Exemples |
|---------|-------|-------------|----------|
| **Dimension** | 📗 (bleu) | Données catégorielles, discrètes | Produit, Région, Date (à grain jour) |
| **Mesure** | 📘 (vert) | Données numériques, continues | Ventes, Quantité, Marge |
| **Continu** | Axe vert | Échelle infinie (ligne, points) | Axe des Y |
| **Discret** | Axe bleu | En-têtes, catégories | Axe des X, lignes/colonnes |

### 2.2 Étagères (Shelves)

Les 4 étagères principales dans Tableau :

```
📊 COLONNES          📊 LIGNES
┌─────────────────┐  ┌─────────────────┐
│ [Date] (MONTH)  │  │ SUM([Ventes])   │
├─────────────────┤  ├─────────────────┤
│ Couleurs : Catégorie                          │
│ Taille : SUM(Quantité)                        │
│ Détail : Produit                              │
│ Tooltip : Marge %                             │
│ Filtres : Année = 2024                        │
└───────────────────────────────────────────────┘
```

### 2.3 Cartes (Marks)

Les types de cartes disponibles :

| Carte | Type de données | Usage |
|-------|----------------|-------|
| Automatic | Auto-détection | Tableau choisit le meilleur type |
| Barre | 1D + 1M | Comparaisons |
| Ligne | 1T + 1M | Tendances temporelles |
| Point | 2M+ | Corrélations |
| Carte | Géographie | Analyse spatiale |
| Cercle | 2M | Distribution |
| Forme | Catégorie | Pictogrammes |
| Zone | 1D + 1M | Proportions (aire) |
| Gantt | 2T + 1M | Calendriers, durées |
| Polygone | Spatial | Formes custom |

---

## 3. Calculs Tableau

### 3.1 Champs Calculés de Base

```tableau
// Pourcentage du total
SUM([Ventes]) / TOTAL(SUM([Ventes]))

// Marge brute
SUM([Ventes]) - SUM([Coût])

// Classification (IF/ELSE)
IF SUM([Ventes]) > 100000 THEN "Élevé"
ELSEIF SUM([Ventes]) > 50000 THEN "Moyen"
ELSE "Faible"
END

// Cloisonnement (CASE/WHEN)
CASE [Région]
  WHEN "Île-de-France" THEN "Nord"
  WHEN "PACA" THEN "Sud"
  ELSE "Autre"
END

// Formatage conditionnel
IF SUM([Ventes]) > 100000 THEN "💰 Haut"
ELSE "⬇ Bas"
END
```

### 3.2 Calculs de Table

```tableau
// Rang
RANK(SUM([Ventes]))

// Percentile
PERCENTILE([Ventes], 0.95)

// Écart à la moyenne
SUM([Ventes]) - WINDOW_AVG(SUM([Ventes]))

// Variation % (YoY)
(ZN(SUM([Ventes])) - LOOKUP(ZN(SUM([Ventes])), -12)) / ABS(LOOKUP(ZN(SUM([Ventes])), -12))

// Cumul (Running Total)
RUNNING_SUM(SUM([Ventes]))

// Moyenne mobile 4 semaines
WINDOW_AVG(SUM([Ventes]), -4, 0)

// Différence par rapport au précédent
ZN(SUM([Ventes])) - LOOKUP(ZN(SUM([Ventes])), -1)
```

### 3.3 LOD Expressions (Level of Detail)

Les LOD permettent de calculer à un niveau de détail différent de celui du graphique.

```tableau
// FIXED : Calcul indépendant des dimensions dans la vue
// Ventes totales (même valeur partout)
{FIXED : SUM([Ventes])}

// Ventes par catégorie (indépendant du filtre Région)
{FIXED [Catégorie] : SUM([Ventes])}

// INCLUDE : Ajoute un niveau de détail
// Moyenne des ventes par produit, quel que soit l'affichage
{INCLUDE [Produit] : AVG([Ventes])}

// EXCLUDE : Supprime un niveau de détail
// Total sans tenir compte du mois
{EXCLUDE [Mois] : SUM([Ventes])}

// Usage concret : % du total par catégorie
SUM([Ventes]) / SUM({FIXED : SUM([Ventes])})

// Meilleur vendeur par région
{FIXED [Région] : MAX([Ventes])}

// Écart à la moyenne générale
SUM([Ventes]) - AVG({FIXED : SUM([Ventes])})

// Ratio vs top performer
SUM([Ventes]) / MAX({EXCLUDE [Produit] : SUM([Ventes])})
```

### 3.4 Paramètres

Les paramètres permettent d'ajouter de l'interactivité.

```tableau
// Création : Paramètre "Seuil Ventes" (entier, 0-100000)
// Utilisation dans un champ calculé
IF SUM([Ventes]) > [Seuil Ventes] THEN "Au-dessus"
ELSE "En-dessous"
END

// Paramètre pour basculer de mesure
// Créer : CASE [Mesure Sélectionnée]
CASE [Paramètre Mesure]
  WHEN "Ventes" THEN SUM([Ventes])
  WHEN "Quantité" THEN SUM([Quantité])
  WHEN "Marge" THEN SUM([Marge])
END
```

---

## 4. Fonctionnalités Avancées

### 4.1 Sets (Ensembles)

```tableau
// Créer un set Top N par ventes
// Set : Top 10 Produits
{RANK(SUM([Ventes])) <= 10}

// Utilisation : couleur, filtre, combinaison
// Set combiné
[Top 10 Ventes] AND [Produit Rentable]

// Condition IN/OUT
IF [Top 10 Ventes] THEN "Top 10" ELSE "Autres" END
```

### 4.2 Groupes et Hiérarchies

```tableau
// Hiérarchie : Catégorie → Sous-Catégorie → Produit
// Groupe : Fusionner "Paris", "Lyon", "Marseille" → "Grandes Villes"
// Groupes manuels ou par alias
```

### 4.3 Dual Axis (Double Axe)

Combiner deux types de graphiques sur le même axe :

```
Axe 1 : Barres = SUM(Ventes)
Axe 2 : Ligne = SUM(Marge) %
→ Synchroniser les axes pour une comparaison cohérente
```

### 4.4 Dashboard Actions

```tableau
// Filter Action : Cliquer sur une région filtre les autres graphiques
// Highlight Action : Survoler un produit surligne les occurrences
// URL Action : Cliquer ouvre une page web avec les paramètres
// Go to Sheet : Navigation vers une autre feuille

// Exemple URL Action avec paramètres :
https://site.com/produit?nom=[Produit]&region=[Région]
```

### 4.5 Animations

```tableau
// Activer les pages (pages shelf)
// Page : [Mois]
// → Animation temporelle avec lecture/pause
// Durée de transition : 0.5s (réglable dans Format > Animations)
```

---

## 5. Administration Tableau Server / Cloud

### 5.1 Commandes tabcmd

```bash
# Authentification
tabcmd login -s https://tableau.monentreprise.com -u admin -p password

# Publier une source de données
tabcmd publish "Ventes.hyper" --project "Projet Ventes" --overwrite

# Publier un classeur
tabcmd publish "Dashboard_Ventes.twbx" --project "Projet Ventes"

# Rafraîchir un extract
tabcmd refreshextracts --datasource "Ventes"

# Exporter un dashboard en image/PDF
tabcmd export "Dashboard_Ventes" --pdf -f rapport.pdf

# Gérer les utilisateurs
tabcmd createusers users.csv
tabcmd removeusers users.csv

# Planifier des tâches
tabcmd createschedule "Rafraîchissement Quotidien" --type extract --frequency daily --start-time "06:00"
tabcmd addschedule "Ventes" --schedule "Rafraîchissement Quotidien"
```

### 5.2 API REST Tableau

```python
import requests

TABLEAU_SERVER = "https://tableau.monentreprise.com"
SITE_ID = "monsite"
TOKEN = "votre_token"

# Obtenir la liste des workbooks
response = requests.get(
    f"{TABLEAU_SERVER}/api/3.18/sites/{SITE_ID}/workbooks",
    headers={"X-Tableau-Auth": TOKEN}
)

# Publier un workbook
with open("dashboard.twbx", "rb") as f:
    response = requests.put(
        f"{TABLEAU_SERVER}/api/3.18/sites/{SITE_ID}/workbooks",
        files={"file": f},
        data={"overwrite": "true"},
        headers={"X-Tableau-Auth": TOKEN}
    )

# Créer un utilisateur
response = requests.post(
    f"{TABLEAU_SERVER}/api/3.18/sites/{SITE_ID}/users",
    json={
        "user": {
            "name": "nouvel_utilisateur",
            "siteRole": "Viewer",
            "authSetting": "SAML"
        }
    },
    headers={"X-Tableau-Auth": TOKEN}
)
```

### 5.3 Tableau Embedded Analytics

```html
<!-- Intégration JavaScript via Tableau Embedding API -->
<script src="https://tableau.monentreprise.com/javascripts/api/viz_v1.js"></script>

<div id="tableauViz"></div>
<script>
  const viz = new tableau.Viz(
    document.getElementById('tableauViz'),
    'https://tableau.monentreprise.com/t/monsite/views/DashboardVentes/Overview',
    {
      width: '100%',
      height: '800px',
      hideTabs: false,
      hideToolbar: false,
      device: 'desktop',
      onFirstInteractive: () => console.log('Dashboard chargé'),
    }
  );

  // API de filtrage
  viz.getWorkbook().getActiveSheet().applyFilterAsync(
    "Région", ["Île-de-France"], tableau.FilterUpdateType.REPLACE
  );
</script>
```

---

## 6. Performance & Optimisation

```tableau
// 1. Extraits au lieu de Live pour les sources lentes
// 2. Agrégation au plus tôt
// 3. Limiter les LOD computations inutiles
// 4. Éviter les calculs de table sur de grands datasets
// 5. Utiliser des index en base
// 6. Context filters pour les filtres prioritaires

// Context Filter (filtrer avant les calculs)
// → Convertir un filtre en contexte : clic droit > Add to Context
// → Améliore les performances des TOP N

// Data Extracts Optimization
// - Aggregate data for specific use cases
// - Hide unused fields
// - Set appropriate refresh schedules
```

---

## Pièges Courants (Pitfalls)

1. **LOD qui ne fait pas ce qu'on attend.**
   - *Erreur :* `{FIXED : SUM([Ventes])}` sans comprendre qu'il ignore TOUS les filtres de dimensions.
   - *Correction :* Utiliser `{INCLUDE}` ou `{EXCLUDE}` pour mieux contrôler le niveau de détail.

2. **Calculs de table qui changent avec le tri.**
   - *Erreur :* `RANK(SUM([Ventes]))` donne des résultats différents selon l'ordre des dimensions.
   - *Correction :* Utiliser `INDEX()` ou spécifier l'ordre avec `LOOKUP()`.

3. **Performance dégradée avec des extracts volumineux.**
   - *Erreur :* Extract .hyper non optimisé contenant des champs inutiles.
   - *Correction :* Masquer les champs non utilisés, agréger les données à la source.

4. **Filtres qui ne s'appliquent pas aux LOD FIXED.**
   - *Erreur :* Un `{FIXED : SUM()}` ignore les filtres de dimensions par défaut.
   - *Correction :* Si le filtre doit s'appliquer, le placer dans "Context Filter" ou utiliser `{INCLUDE}`.

5. **Double Axe mal synchronisé.**
   - *Erreur :* Barres et lignes avec des échelles différentes trompent la lecture.
   - *Correction :* Synchroniser les axes via clic droit > Synchroniser l'axe.

6. **Publishing qui échoue avec des permissions.**
   - *Erreur :* `tabcmd publish` échoue car le projet a des permissions restrictives.
   - *Correction :* Vérifier le rôle (Creator/Explorer) et les permissions du projet.

---

## Ressources

- [Tableau Community](https://community.tableau.com/)
- [Tableau Public Gallery](https://public.tableau.com/gallery/)
- [Documentation Tableau Desktop](https://help.tableau.com/current/pro/desktop/fr-fr/default.htm)
- [Tableau API REST](https://help.tableau.com/current/api/rest_api/fr-fr/index.html)
- [Tableau Embedding API](https://help.tableau.com/current/api/embedding_api/fr-fr/index.html)

---

## Checklist

- [ ] La source de données est correctement configurée (Live ou Extract).
- [ ] Les dimensions et mesures ont les bons types assignés.
- [ ] Les champs calculés sont testés sur un sous-ensemble de données.
- [ ] Les LOD expressions sont vérifiées pour leur comportement attendu.
- [ ] Les paramètres sont liés à des champs calculés ou des filtres.
- [ ] Les dashboard actions (filter/highlight/URL) sont testées.
- [ ] Les extraits sont planifiés avec une fréquence adaptée.
- [ ] Le classeur est optimisé pour la performance (context filters, champs masqués).
