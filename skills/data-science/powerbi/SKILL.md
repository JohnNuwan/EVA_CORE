---
name: powerbi
description: "Microsoft Power BI : Power Query (M), DAX, modélisation tabulaire, rapports paginés, service Power BI, Row-Level Security, Embedded, Deploy Pipelines, XMLA endpoints."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [powerbi, power-bi, microsoft, dax, power-query, bi, dashboard, analytics]
    homepage: https://powerbi.microsoft.com/
    related_skills: [tableau, dashboard-design, data-storytelling, dax]
prerequisites:
  commands: []
  pip_packages: [powerbiclient]
---

# Compétence Microsoft Power BI — Analytics & Business Intelligence

## Vue d'ensemble

**Microsoft Power BI** est la plateforme de Business Intelligence et d'analytics de Microsoft. Elle permet de connecter des centaines de sources de données, modéliser des données tabulaires, créer des rapports interactifs et les partager via le Service Power BI.

**Écosystème :**

- **Power BI Desktop** : outil de création de rapports (gratuit).
- **Power Query (M)** : langage de transformation et nettoyage de données.
- **DAX (Data Analysis Expressions)** : langage de formules pour mesures et colonnes calculées.
- **Power BI Service** : plateforme cloud de partage et collaboration.
- **Power BI Report Builder** : rapports paginés (format SSRS).
- **Power BI Mobile** : accès mobile aux rapports.
- **Power BI Embedded** : intégration dans des applications custom.
- **Power BI Premium / Fabric** : capacité dédiée, XMLA endpoints, AI.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Travaille dans un environnement Microsoft (Azure, Office 365, SQL Server).
- Crée des rapports et dashboards Power BI.
- A besoin de modélisation tabulaire avec des relations complexes.
- Écrit des mesures DAX avancées (Time Intelligence, semi-additives).
- Transforme et nettoie des données avec Power Query / M.
- Veut implémenter la sécurité (RLS) ou des pipelines de déploiement.

---

## 1. Power Query (Langage M)

### 1.1 Transformation Fondamentales

```powerquery
let
    // Chargement
    Source = Excel.Workbook(File.Contents("C:\data\ventes.xlsx"), null, true),
    Ventes_Table = Source{[Name="Ventes"]}[Data],
    
    // Promotion des en-têtes
    PromoteHeaders = Table.PromoteHeaders(Ventes_Table, [PromoteAllScalars=true]),
    
    // Typage des colonnes
    TypedTable = Table.TransformColumnTypes(PromoteHeaders, {
        {"Date", type date},
        {"Montant", type number},
        {"Quantité", Int64.Type},
        {"Produit", type text}
    }),
    
    // Filtrage des lignes
    Filtered = Table.SelectRows(TypedTable, each [Montant] > 0),
    
    // Suppression des colonnes inutiles
    RemoveColumns = Table.RemoveColumns(Filtered, {"ColonneInutile"}),
    
    // Renommage
    Renamed = Table.RenameColumns(RemoveColumns, {
        {"Montant", "Ventes"},
        {"Quantité", "Qté"}
    }),
    
    // Ajout d'une colonne conditionnelle
    AddCategory = Table.AddColumn(Renamed, "Catégorie", each
        if [Ventes] > 1000 then "Premium"
        else if [Ventes] > 500 then "Standard"
        else "Économique"
    ),
    
    // Group By (aggrégation)
    Grouped = Table.Group(AddCategory, {"Produit"}, {
        {"Total Ventes", each List.Sum([Ventes]), type number},
        {"Nb Transactions", each Table.RowCount(_), Int64.Type}
    })
in
    Grouped
```

### 1.2 Merge (Jointure) et Append (Union)

```powerquery
// Merge (Jointure comme SQL JOIN)
let
    Ventes = Excel.Workbook(...),
    Produits = Excel.Workbook(...),
    
    // Left Outer Join
    Merged = Table.NestedJoin(
        Ventes, {"ProductID"},
        Produits, {"ID"},
        "ProduitData",
        JoinKind.LeftOuter
    ),
    
    // Expansion des colonnes jointes
    Expanded = Table.ExpandTableColumn(Merged, "ProduitData", {"Nom", "Prix"})
in
    Expanded

// Append (Union) — fusionner plusieurs tables
Combined = Table.Combine({Table1, Table2, Table3})
```

### 1.3 Pivot / Unpivot

```powerquery
// Unpivot : colonnes → lignes (le plus utile dans Power BI)
Unpivoted = Table.UnpivotOtherColumns(
    Source, {"Date", "Produit"},
    "Mois", "Valeur"
)

// Pivot : lignes → colonnes
Pivoted = Table.Pivot(
    Source,
    List.Distinct(Source[Mois]),
    "Mois", "Valeur",
    List.Sum
)
```

### 1.4 Paramètres et Fonctions M

```powerquery
// Paramètre (créé dans Power Query Editor > Manage Parameters)
// CheminFichier = "C:\data\"

let
    Source = Excel.Workbook(File.Contents(CheminFichier & "ventes.xlsx"), null, true)
in
    Source

// Fonction personnalisée
(Table as table, MinDate as date) as table =>
let
    Filtered = Table.SelectRows(Table, each [Date] >= MinDate)
in
    Filtered
```

---

## 2. Modélisation Tabulaire

### 2.1 Relations et Cardinalité

| Type | Description | Exemple |
|------|-------------|---------|
| **1:N** | Une valeur dans la table de dimension = plusieurs dans la table de faits | Un produit → plusieurs ventes |
| **1:1** | Correspondance exacte | Un employé → une fiche de paie |
| **N:N** | Plusieurs-à-plusieurs (via table de pont) | Produits × Magasins |

**Bonne pratique :** Table de faits (étroite, longue) + Tables de dimensions (larges, courtes)

### 2.2 Star Schema (Modèle en Étoile)

```
                  ┌─────────────┐
                  │   DimDate   │
                  │ Date         │
                  │ Jour         │
                  │ Mois         │──┐
                  │ Année        │  │
                  └─────────────┘  │
                                   │
┌──────────┐    ┌──────────────────┴──┐    ┌────────────┐
│ DimProd  │────│     FactVentes      │────│   DimCli   │
│ ProduitID│    │ ProduitID     Date   │    │ ClientID   │
│ Nom      │    │ ClientID    Montant │    │ Nom        │
│ Catégorie│    │ Quantité      Marge │    │ Segment    │
└──────────┘    └─────────────────────┘    └────────────┘
                        │
                        │
                  ┌─────┴──────┐
                  │   DimGeo   │
                  │ GeoID       │
                  │ Région      │
                  │ Ville       │
                  └────────────┘
```

### 2.3 Calendrier de Dates (Date Table)

Obligatoire pour les fonctions Time Intelligence DAX.

```dax
Calendrier = 
CALENDARAUTO(12)  -- Toutes les dates des autres tables, clôture fiscale en décembre

-- Alternativement avec plage explicite
Calendrier = 
CALENDAR(
    MIN(FactVentes[Date]),
    MAX(FactVentes[Date])
)

// Ajouter des colonnes de dates
Date = 'Calendrier'[Date]
Année = YEAR('Calendrier'[Date])
Mois = FORMAT('Calendrier'[Date], "YYYY-MM")
Mois Nom = FORMAT('Calendrier'[Date], "MMMM")
Trimestre = QUARTER('Calendrier'[Date])
Jour de Semaine = WEEKDAY('Calendrier'[Date], 2)  -- Lundi = 1
Jour Nom = FORMAT('Calendrier'[Date], "dddd")
Numéro Semaine = WEEKNUM('Calendrier'[Date], 2)
Est Ouvré = NOT WEEKDAY('Calendrier'[Date], 2) IN {6, 7}
```

---

## 3. DAX (Data Analysis Expressions)

### 3.1 Mesures Fondamentales

```dax
-- Total des ventes
Total Ventes = SUM(FactVentes[Montant])

-- Quantité totale
Total Quantité = SUM(FactVentes[Quantité])

-- Nombre de transactions
Nb Transactions = COUNTROWS(FactVentes)

-- Nombre de clients distincts
Clients Uniques = DISTINCTCOUNT(FactVentes[ClientID])

-- Prix moyen (vente / quantité)
Prix Moyen = DIVIDE([Total Ventes], [Total Quantité])

-- Marge brute (mesure calculée)
Marge Brute = SUM(FactVentes[Montant]) - SUM(FactVentes[Coût])

-- Taux de marge
Taux Marge = DIVIDE([Marge Brute], [Total Ventes])

-- Pourcentage du total
% Total = DIVIDE([Total Ventes], CALCULATE([Total Ventes], ALL(DimProduit)))
```

### 3.2 Time Intelligence (Intelligence Temporelle)

```dax
-- Ventes de l'année en cours (YTD)
Ventes YTD = TOTALYTD([Total Ventes], 'Calendrier'[Date])

-- Ventes du trimestre en cours (QTD)
Ventes QTD = TOTALQTD([Total Ventes], 'Calendrier'[Date])

-- Ventes du mois en cours (MTD)
Ventes MTD = TOTALMTD([Total Ventes], 'Calendrier'[Date])

-- Même période l'année précédente
Ventes N-1 = CALCULATE([Total Ventes], SAMEPERIODLASTYEAR('Calendrier'[Date]))

-- Variation YoY (en montant)
Variation YoY = [Total Ventes] - [Ventes N-1]

-- Variation YoY (en %)
Variation YoY % = DIVIDE([Variation YoY], [Ventes N-1])

-- Moyenne mobile 30 jours
Moy Mobile 30J = 
CALCULATE(
    AVERAGEX(
        DATESINPERIOD('Calendrier'[Date], LASTDATE('Calendrier'[Date]), -30, DAY),
        [Total Ventes]
    )
)

-- Cumul mensuel (Running Total)
Cumul Mensuel = 
CALCULATE(
    [Total Ventes],
    DATESMTD('Calendrier'[Date])
)

-- Même jour de la semaine N-1 (ventes comparables)
Même Jour N-1 = 
CALCULATE([Total Ventes], DATEADD('Calendrier'[Date], -364, DAY))
```

### 3.3 Fonctions de Filtre et CALCULATE

```dax
-- Ventes d'une catégorie spécifique
Ventes Électronique = 
CALCULATE([Total Ventes], DimProduit[Catégorie] = "Électronique")

-- Ventes des meilleurs clients (Top 20%)
Ventes Top 20% = 
CALCULATE(
    [Total Ventes],
    FILTER(
        DimClient,
        RANKX(ALL(DimClient), [Total Ventes],, DESC) <= COUNTROWS(ALL(DimClient)) * 0.2
    )
)

-- Ventes hors région Île-de-France
Ventes Hors IDF = 
CALCULATE([Total Ventes], DimGeo[Région] <> "Île-de-France")

-- Ventes du produit le plus vendu
Ventes Top Produit = 
CALCULATE(
    [Total Ventes],
    TOPN(1, ALL(DimProduit), [Total Ventes])
)

-- Ventes avec plusieurs conditions
Ventes Segmentées = 
CALCULATE(
    [Total Ventes],
    DimClient[Segment] = "Premium",
    DimProduit[Catégorie] IN {"Électronique", "Informatique"},
    'Calendrier'[Année] = 2024
)

-- Ventes par rapport à la moyenne de la catégorie
Écart Moyenne Catégorie = 
[Total Ventes] - 
CALCULATE([Total Ventes], ALLEXCEPT(DimProduit, DimProduit[Catégorie]))
```

### 3.4 Mesures Semi-Additives

```dax
-- Stock en fin de période (ne s'additionne pas dans le temps)
Stock Fin Mois = 
CALCULATE(
    SUM(Stock[Quantité]),
    LASTNONBLANK(
        'Calendrier'[Date],
        CALCULATE(SUM(Stock[Quantité]))
    )
)

-- Solde bancaire moyen sur la période
Solde Moyen = AVERAGEX(Valeurs('Calendrier'[Date]), [Solde Quotidien])

-- Nombre de jours ouvrés dans la période
Jours Ouvrés = 
CALCULATE(
    COUNTROWS('Calendrier'),
    'Calendrier'[Est Ouvré] = TRUE
)
```

### 3.5 Mesures de Classement

```dax
-- Top N Produits Dynamique (avec paramètre)
Top N Produits = 
VAR TopN = [Paramètre TopN Value]
VAR Ranked = 
    TOPN(TopN, ALL(DimProduit), [Total Ventes])
RETURN
    CALCULATE([Total Ventes], Ranked)

-- Classement des produits
Rang Produit = RANKX(ALL(DimProduit), [Total Ventes],, DESC, Dense)
```

### 3.6 Nouvelles Fonctions DAX (Power BI 2024+)

```dax
-- EVALUATE AND LOG (debug)
EVALUATE SUMMARIZE(FactVentes, DimProduit[Nom], "Ventes", [Total Ventes])
ORDER BY [Ventes] DESC

-- window functions (comme SQL)
Top 3 = 
CALCULATE([Total Ventes],
    WINDOW(1, ABS, 3, ABS, ALL(DimProduit), ORDERBY([Total Ventes], DESC))
)

-- INDEX / OFFSET
Produit Précédent = 
CALCULATE([Total Ventes],
    OFFSET(-1, ALL(DimProduit), ORDERBY([Total Ventes], DESC))
)
```

---

## 4. Power BI Service

### 4.1 Pipelines de Déploiement

```yaml
# Development → Test → Production
# 3 étapes :

# Dev : Espace de travail dédié au développement
# Test : Copie automatique, tests utilisateurs
# Prod : Version officielle

# Règles de déploiement : préserver les paramètres de source de données,
# les connexions de passerelle, et les rôles RLS
```

### 4.2 Row-Level Security (RLS)

```dax
-- Rôle : Manager Région
[Email] = USERPRINCIPALNAME()
-- Dans la table DimGeo : filtrer par région du manager

-- Rôle : Direction (tout voir)
-- Pas de filtre → TRUE() = tout visible

-- Test RLS dans Power BI Desktop
-- View as Roles → Sélectionner le rôle
```

### 4.3 Automatisation avec l'API

```python
# Python avec powerbiclient
from powerbiclient import Report, models
from powerbiclient.authentication import DeviceCodeLoginAuthentication

# Authentification
device_auth = DeviceCodeLoginAuthentication()

# Liste des rapports
from powerbiclient import PowerBI
powerbi = PowerBI(auth=device_auth)
reports = powerbi.reports.get_reports()

# API REST Power BI (HTTPS)
POST https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports
GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets
```

---

## 5. XMLA Endpoints (Premium)

```xml
<!-- Connexion via SSMS ou tabular editor -->
<DataSource>
    <ConnectionString>
        Data Source=powerbi://api.powerbi.com/v1.0/myorg/WorkspaceName;
        Initial Catalog=DatasetName
    </ConnectionString>
</DataSource>

<!-- Script TMSL (Tabular Model Scripting Language) -->
{
  "refresh": {
    "type": "full",
    "objects": [
      { "database": "Ventes", "table": "FactVentes" }
    ]
  }
}
```

---

## Pièges Courants (Pitfalls)

1. **Time Intelligence qui ne fonctionne pas.**
   - *Erreur :* Les fonctions `TOTALYTD`, `SAMEPERIODLASTYEAR` retournent des blancs.
   - *Correction :* Vérifier que la table de dates est marquée comme table de dates (Date Table) et liée à la table de faits.

2. **Mesure qui s'additionne mal.**
   - *Erreur :* `SUM(FactVentes[Prix Moyen])` additionne des moyennes — résultat absurde.
   - *Correction :* Une mesure de ratio ne s'additionne pas. Utiliser `AVERAGE` ou `DIVIDE(SUM(...), SUM(...))`.

3. **Power Query lent à rafraîchir.**
   - *Erreur :* Des transformations coûteuses (pivot, merge) sur de gros volumes.
   - *Correction :* Pousser les transformations vers la source (SQL), réduire le nombre d'étapes, activer le Query Folding.

4. **Filtres croisés qui s'ignorent.**
   - *Erreur :* Un graphique filtré par date ne filtre pas un autre graphique.
   - *Correction :* Vérifier que la direction du filtre croisé est bidirectionnelle ou qu'il y a une table de pont.

5. **RLS contourné par des mesures avec ALL().**
   - *Erreur :* `CALCULATE([Total Ventes], ALL(DimGeo))` ignore les filtres RLS.
   - *Correction :* Utiliser `ALL()` seulement si vous voulez explicitement passer outre la sécurité.

6. **Dataset qui ne se rafraîchit pas dans le service.**
   - *Erreur :* La passerelle de données n'est pas configurée ou les credentials ont expiré.
   - *Correction :* Vérifier la passerelle (On-premises Data Gateway) et les credentials dans Paramètres du dataset.

---

## Ressources

- [Documentation DAX](https://docs.microsoft.com/fr-fr/dax/)
- [Power Query M Reference](https://docs.microsoft.com/powerquery-m/)
- [DAX Patterns](https://www.daxpatterns.com/) — patterns réutilisables
- [SQLBI](https://www.sqlbi.com/) — formations DAX (Alberto Ferrari, Marco Russo)
- [Power BI Community](https://community.powerbi.com/)

---

## Checklist

- [ ] Une table de dates distincte est créée et marquée comme Date Table.
- [ ] Les relations (1:N) sont correctes et le filtre croisé est dans le bon sens.
- [ ] Les mesures sont dans un dossier de mesures (Measure Table), pas dans la table de données.
- [ ] Les calculs Time Intelligence sont testés avec des données de différentes périodes.
- [ ] Les colonnes calculées sont évitées quand une mesure suffit (performances).
- [ ] Le Query Folding est vérifié pour les transformations Power Query.
- [ ] La sécurité RLS est testée avec "View as Roles".
- [ ] Les pipelines de déploiement (Dev → Test → Prod) sont configurés.
