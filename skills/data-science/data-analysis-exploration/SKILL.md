---
name: data-analysis-exploration
description: "Analyser, nettoyer et visualiser des données tabulaires avec Pandas, NumPy, Polars, Matplotlib et Seaborn pour l'exploration de données (EDA) en Python."
version: 2.0.0
author: Actemium & communauté Helios
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [pandas, numpy, polars, matplotlib, seaborn, data-science, analyse-de-données, visualisation, python, EDA]
    homepage: https://pandas.pydata.org/
    related_skills: [jupyter-live-kernel, industrial-analytics-grafana, huggingface-hub]
prerequisites:
  commands: [python3, pip]
  pip_packages: [pandas, numpy, polars, matplotlib, seaborn, pyarrow]
---

# Compétence Analyse et Exploration de Données en Python (Pandas, NumPy, Polars, Matplotlib)

## Vue d'ensemble

L'analyse exploratoire de données (EDA — *Exploratory Data Analysis*) et le nettoyage sont les étapes fondamentales de tout projet de science des données, d'analyse industrielle ou d'intelligence artificielle. Cette compétence fournit un guide structuré pour manipuler des structures de données tabulaires avec **Pandas**, effectuer des calculs statistiques avec **NumPy**, traiter de grands volumes avec **Polars** (moteur en Rust, bien plus rapide que Pandas sur les fichiers volumineux), et produire des visualisations claires avec **Matplotlib** et **Seaborn**.

Chaque section présente des blocs de code prêts à l'emploi, accompagnés d'explications sur les bonnes pratiques, les pièges à éviter, et des conseils de performance.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Demande de charger et d'analyser des fichiers de données (CSV, Excel, JSON, Parquet, Arrow).
- Souhaite nettoyer et manipuler un jeu de données (valeurs manquantes, doublons, agrégations, transformations).
- A besoin de calculer des corrélations, des distributions ou des indicateurs statistiques sur des séries temporelles.
- Demande de visualiser des distributions physiques ou temporelles (température, pression, vibration, trafic).
- Veut optimiser le temps d'exécution et la consommation mémoire de scripts sur des fichiers volumineux (> 1 Go).
- A besoin d'exporter des données nettoyées vers un format adapté à l'apprentissage automatique ou au reporting.

---

## Prérequis

### Installation des Dépendances

```bash
pip install pandas numpy polars matplotlib seaborn pyarrow
```

Vérification :

```python
import pandas as pd
import numpy as np
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
print("Toutes les dépendances sont installées.")
```

### Structure de Données Recommandée

Pour des performances optimales, organisez vos fichiers de données avec :

- Une ligne d'en-tête avec des noms de colonnes en minuscules et sans espaces (`temperature_celsius`, `pression_bar`).
- Des types de données cohérents (pas de mélange de `str` et `float` dans une même colonne).
- Des timestamps au format ISO 8601 (`2025-03-15T14:30:00Z`) pour les séries temporelles.

---

## 1. Chargement et Nettoyage des Données avec Pandas

Pandas est la bibliothèque standard pour la manipulation de données tabulaires en Python. Voici les opérations les plus courantes, organisées de manière progressive.

### 1.1 Chargement Robuste

```python
import pandas as pd

# CSV avec gestion avancée des types
df = pd.read_csv(
    "data/production_logs.csv",
    parse_dates=["timestamp"],
    infer_datetime_format=True,
    low_memory=False  # Évite les warnings de types mixtes
)

# Excel (toutes les feuilles)
xl = pd.ExcelFile("data/rapport_mensuel.xlsx")
df_ventes = pd.read_excel(xl, sheet_name="Ventes")
df_stock = pd.read_excel(xl, sheet_name="Stock")

# JSON (lignes ou tableau)
df_json = pd.read_json("data/sensors.json", lines=True)

# Parquet (format colonne ultra-rapide)
df_parquet = pd.read_parquet("data/captures.parquet")
```

### 1.2 Inspection Rapide

```python
# Aperçu structurel
print("=== INFOS ===")
print(df.info())

# Statistiques descriptives
print("\n=== STATISTIQUES ===")
print(df.describe(percentiles=[0.05, 0.25, 0.5, 0.75, 0.95]))

# Valeurs manquantes
print("\n=== VALEURS MANQUANTES ===")
print(df.isnull().sum())

# Aperçu des 5 premières et dernières lignes
print("\n=== HEAD ===")
print(df.head())
print("\n=== TAIL ===")
print(df.tail())
```

### 1.3 Nettoyage

```python
# Suppression des doublons (toutes colonnes ou sous-ensemble)
df = df.drop_duplicates(subset=["machine_id", "timestamp"])

# Imputation des valeurs manquantes
df["temperature"] = df["temperature"].fillna(df["temperature"].median())
df["pression"] = df["pression"].interpolate(method="linear")  # Interpolation temporelle
df["statut"] = df["statut"].fillna("INCONNU")

# Correction des types
df["machine_id"] = df["machine_id"].astype(str)
df["vibration"] = pd.to_numeric(df["vibration"], errors="coerce")

# Suppression des lignes avec trop de valeurs manquantes
seuil = len(df.columns) * 0.5
df = df.dropna(thresh=seuil)
```

### 1.4 Filtrage et Transformation

```python
# Filtrage avec .copy() pour éviter les SettingWithCopyWarning
df_clean = df[df["cycle_time"] > 0].copy()

# Création de colonnes calculées
df_clean["speed_efficiency"] = df_clean["target_speed"] / df_clean["actual_speed"]
df_clean["date"] = df_clean["timestamp"].dt.date
df_clean["heure"] = df_clean["timestamp"].dt.hour

# Agrégation par groupe
summary = df_clean.groupby("machine_id").agg(
    duree_moyenne=("cycle_time", "mean"),
    duree_ecart_type=("cycle_time", "std"),
    rendement_moyen=("speed_efficiency", "mean"),
    nb_erreurs=("statut", lambda x: (x == "ERREUR").sum())
)

# Triage et reset de l'index pour un DataFrame propre
summary = summary.sort_values("nb_erreurs", ascending=False).reset_index()
```

---

## 2. Analyse Statistique Descriptive avec NumPy

NumPy fournit les fondations mathématiques pour les calculs sur tableaux multidimensionnels. Il est particulièrement utile pour les opérations qui sortent du cadre de haut niveau de Pandas.

### 2.1 Statistiques Fondamentales

```python
import numpy as np

# Extraction d'un tableau NumPy depuis une colonne Pandas
temperatures = df_clean["temperature"].to_numpy()

# Statistiques descriptives
moyenne = np.mean(temperatures)
mediane = np.median(temperatures)
ecart_type = np.std(temperatures, ddof=1)  # ddof=1 pour échantillon (vs population)
variance = np.var(temperatures, ddof=1)
minimum = np.min(temperatures)
maximum = np.max(temperatures)

# Centiles et quartiles
q1, q2, q3 = np.percentile(temperatures, [25, 50, 75])
print(f"Min: {minimum:.2f}, Q1: {q1:.2f}, Médiane: {q2:.2f}, Q3: {q3:.2f}, Max: {maximum:.2f}")
```

### 2.2 Détection d'Anomalies (Outliers) par Z-Score

```python
# Calcul du Z-score
z_scores = (temperatures - moyenne) / ecart_type

# Seuil standard : |Z| > 3
seuil_z = 3.0
masque_outliers = np.abs(z_scores) > seuil_z
outliers = temperatures[masque_outliers]

print(f"Valeurs totales : {len(temperatures)}")
print(f"Anomalies détectées (|Z| > {seuil_z}) : {len(outliers)}")
print(f"Plage normale : [{moyenne - seuil_z*ecart_type:.2f}, {moyenne + seuil_z*ecart_type:.2f}]")
```

### 2.3 Matrice de Corrélation

```python
# Sélection des colonnes numériques
colonnes_numeriques = ["temperature", "pression", "vibration", "cycle_time"]
variables = df_clean[colonnes_numeriques].to_numpy()

# Matrice de corrélation
corr_matrix = np.corrcoef(variables, rowvar=False)

# Affichage lisible
noms = colonnes_numeriques
print("Matrice de corrélation :")
for i, nom_i in enumerate(noms):
    for j, nom_j in enumerate(noms):
        if i < j:
            print(f"  {nom_i} ↔ {nom_j} : {corr_matrix[i, j]:+.3f}")
```

---

## 3. Traitement Haute Performance avec Polars

### 3.1 Pourquoi Polars ?

Polars est un moteur de traitement de données écrit en **Rust**, spécialement conçu pour :

- **Parallélisation native** : utilise tous les cœurs CPU disponibles sans configuration.
- **Évaluation paresseuse (Lazy)** : optimise le plan d'exécution avant de le matérialiser.
- **Streaming hors-mémoire (out-of-core)** : traite des fichiers plus grands que la RAM.
- **Interopérabilité Arrow** : partage le format mémoire Apache Arrow, permettant des transferts zéro-copie avec Pandas.

### 3.2 Pipeline Paresseux (Lazy) avec Streaming

```python
import polars as pl

# Construction du plan d'exécution paresseux
lazy_query = (
    pl.scan_csv("data/huge_sensor_logs.csv")
    # Filtres et projections : poussés au plus tôt dans le graphe d'optimisation
    .filter(pl.col("cycle_time") > 0)
    .with_columns([
        (pl.col("target_speed") / pl.col("actual_speed")).alias("speed_efficiency"),
        pl.col("temperature").fill_null(pl.col("temperature").median()),
        pl.col("timestamp").str.to_datetime("%Y-%m-%dT%H:%M:%S"),
    ])
    .group_by("machine_id")
    .agg([
        pl.col("cycle_time").mean().alias("duree_moyenne"),
        pl.col("cycle_time").std().alias("duree_std"),
        pl.col("speed_efficiency").mean().alias("rendement_moyen"),
        pl.col("temperature").min().alias("temp_min"),
        pl.col("temperature").max().alias("temp_max"),
    ])
    .sort("duree_moyenne", descending=True)
)

# Exécution avec streaming (out-of-core) — ne charge jamais tout le fichier en RAM
df_result = lazy_query.collect(streaming=True)
print(df_result)
```

### 3.3 Interopérabilité Zéro-Copie (Apache Arrow)

```python
# Polars → Pandas (zéro-copie via PyArrow)
pandas_df = df_result.to_pandas()

# Pandas → Polars
polars_df = pl.from_pandas(pandas_df)

# Vérification : la conversion est quasi-instantanée
# car la mémoire sous-jacente est partagée via Arrow
```

### 3.4 Expressions Natives et Performance

```python
# BON : Expressions natives Polars (parallélisées en Rust)
df_filtered = df.with_columns(
    pl.when(pl.col("temperature") > 100)
    .then(pl.lit("CRITIQUE"))
    .otherwise(pl.lit("NORMAL"))
    .alias("alerte")
)

# MAUVAIS : Lambda Python (séquentiel, interprété ligne par ligne)
# df = df.with_columns(
#     pl.col("temperature").map_elements(lambda x: "CRITIQUE" if x > 100 else "NORMAL")
# )

print(f"Temps d'exécution : les expressions natives sont 10x–100x plus rapides")
```

---

## 4. Visualisation avec Matplotlib et Seaborn

### 4.1 Configuration Globale

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Thème professionnel
sns.set_theme(
    style="whitegrid",
    palette="viridis",
    font_scale=1.1,
    rc={
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    }
)
```

### 4.2 Distribution avec Histogramme et KDE

```python
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogramme avec courbe KDE
sns.histplot(
    data=df_clean, x="temperature", hue="machine_id",
    kde=True, multiple="stack", palette="viridis", ax=axes[0]
)
axes[0].set_title("Distribution des Températures par Machine", fontweight="bold")
axes[0].set_xlabel("Température (°C)")
axes[0].set_ylabel("Nombre d'observations")

# Boxplot
sns.boxplot(
    data=df_clean, x="machine_id", y="temperature",
    palette="viridis", ax=axes[1]
)
axes[1].set_title("Boxplot des Températures par Machine", fontweight="bold")
axes[1].set_xlabel("Machine")
axes[1].set_ylabel("Température (°C)")

plt.tight_layout()
plt.savefig("assets/temperature_distribution.png", dpi=300)
plt.close()
```

### 4.3 Série Temporelle

```python
fig, ax = plt.subplots(figsize=(14, 6))

# Agrégation horaire
df_clean["hour"] = df_clean["timestamp"].dt.hour
hourly_avg = df_clean.groupby("hour")["temperature"].agg(["mean", "std"]).reset_index()

# Tracé avec intervalle de confiance
ax.plot(hourly_avg["hour"], hourly_avg["mean"], marker="o", linewidth=2, color="#2c7fb8")
ax.fill_between(
    hourly_avg["hour"],
    hourly_avg["mean"] - hourly_avg["std"],
    hourly_avg["mean"] + hourly_avg["std"],
    alpha=0.2, color="#2c7fb8"
)
ax.set_title("Évolution Horaires des Températures (moyenne ± écart-type)", fontweight="bold")
ax.set_xlabel("Heure de la journée")
ax.set_ylabel("Température moyenne (°C)")
ax.set_xticks(range(0, 24))

plt.tight_layout()
plt.savefig("assets/temperature_hourly.png", dpi=300)
plt.close()
```

### 4.4 Matrice de Corrélation (Heatmap)

```python
fig, ax = plt.subplots(figsize=(10, 8))

# Calcul des corrélations
corr = df_clean[colonnes_numeriques].corr()

# Heatmap avec annotations
sns.heatmap(
    corr,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    vmin=-1,
    vmax=1,
    center=0,
    square=True,
    linewidths=0.5,
    ax=ax
)
ax.set_title("Matrice de Corrélation des Variables", fontweight="bold")

plt.tight_layout()
plt.savefig("assets/correlation_matrix.png", dpi=300)
plt.close()
```

---

## 5. Export des Données Nettoyées

```python
# Format Parquet (recommandé pour la réutilisabilité)
df_clean.to_parquet("data/donnees_nettoyees.parquet", compression="snappy")

# Format CSV (interopérabilité maximale)
df_clean.to_csv("data/donnees_nettoyees.csv", index=False)

# Format Excel (pour le reporting)
df_clean.to_excel("data/donnees_nettoyees.xlsx", sheet_name="Données", index=False)
```

---

## Pièges Courants (Pitfalls)

1. **SettingWithCopyWarning dans Pandas.**
   - *Erreur :* Modifier une sous-sélection de DataFrame directement, ex. `df[df['val'] > 10]['status'] = 'OK'`. Cela lève un avertissement car Pandas ne sait pas s'il modifie une copie ou la vue d'origine.
   - *Correction :* Toujours utiliser `.loc` ou faire une copie explicite avec `.copy()`. Exemple : `df.loc[df['val'] > 10, 'status'] = 'OK'`.

2. **Épuisement de la mémoire sur de gros fichiers.**
   - *Erreur :* Charger un fichier CSV de plusieurs gigaoctets avec `pd.read_csv()` sans précaution, provoquant un crash par manque de RAM.
   - *Correction :* Utilisez le paramètre `chunksize` dans Pandas, ou basculez sur Polars en mode paresseux : `pl.scan_csv("...").collect(streaming=True)`.

3. **Utilisation d'expressions lambda lentes dans Polars.**
   - *Erreur :* Utiliser `.map_elements(lambda x: ...)` dans Polars. Cela force l'interpréteur Python à exécuter la fonction ligne par ligne de façon séquentielle, détruisant les performances du parallélisme Rust.
   - *Correction :* Toujours privilégier les expressions natives de Polars : `pl.when(pl.col("a") > 0).then(pl.col("b")).otherwise(0)`.

4. **Accès par index absent dans Polars.**
   - *Erreur :* Écrire `df.loc[3]` ou tenter d'accéder à un index inexistant dans un DataFrame Polars.
   - *Correction :* Polars n'a pas de concept d'index. Utilisez des filtres (`df.filter(pl.col("id") == 3)`) ou des sélections par positions physiques (`df.row(3)` ou `df[3, :]`).

5. **Graphiques illisibles ou tronqués.**
   - *Erreur :* Les légendes sont coupées, les étiquettes des axes se chevauchent, ou le texte est trop petit.
   - *Correction :* Utilisez `plt.tight_layout()` avant `plt.savefig()`. Définissez `dpi=300` pour les exports. Ajustez `figsize` pour les graphiques complexes.

6. **Fusion de données avec des clés de types différents.**
   - *Erreur :* `pd.merge()` échoue car les colonnes de jointure ont des types différents (ex. `int` vs `str`).
   - *Correction :* Normalisez les types avant la fusion : `df1["id"] = df1["id"].astype(str)`.

7. **Oubli de la fermeture des figures Matplotlib.**
   - *Erreur :* Les figures s'accumulent en mémoire, provoquant des ralentissements dans les notebooks ou scripts longs.
   - *Correction :* Appelez `plt.close()` après chaque `plt.savefig()` pour libérer la mémoire.

---

## Liste de Vérification (Checklist)

- [ ] Les dépendances sont installées (`pandas`, `numpy`, `polars`, `matplotlib`, `seaborn`, `pyarrow`).
- [ ] Les DataFrames filtrés ou modifiés dans Pandas utilisent `.copy()` pour éviter les `SettingWithCopyWarning`.
- [ ] Les fichiers de plus de 1 Go sont traités avec Polars en mode paresseux et streaming (`streaming=True`).
- [ ] Le code Polars évite les expressions lambda Python (`map_elements`) et utilise les expressions natives (`pl.col`, `pl.when`).
- [ ] Les valeurs aberrantes sont détectées (Z-score, IQR) et traitées (suppression, winsorisation, imputation).
- [ ] Les valeurs manquantes sont explicitement traitées (imputation médiane/moyenne/interpolation, ou suppression après analyse).
- [ ] Les graphiques sauvegardés ont des axes étiquetés, des légendes claires, et sont enregistrés avec `plt.tight_layout()`.
- [ ] `plt.close()` est appelé après chaque `plt.savefig()` pour libérer la mémoire.
- [ ] Les types de données sont cohérents entre les colonnes avant les jointures ou les fusions.
- [ ] Les données nettoyées sont exportées dans un format pérenne (Parquet recommandé, CSV ou Excel si nécessaire).

