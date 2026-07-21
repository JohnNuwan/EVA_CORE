---
name: data-science
description: Guide complet de Data Science — pandas, NumPy, visualisation, statistiques, ETL, feature engineering, time series, et workflow data. En français.

---

# Data Science — Guide Complet (Français)

Pipeline data de bout en bout : acquisition, nettoyage, analyse, visualisation.

---

## 1. NumPy — Calcul Numérique

```python
import numpy as np

# Création
arr = np.array([1, 2, 3])
zeros = np.zeros((3, 4))
ones = np.ones((2, 3))
identite = np.eye(4)
aleatoire = np.random.randn(100, 10)
sequence = np.arange(0, 1, 0.1)
espace = np.linspace(0, 100, 50)

# Indexation et filtrage
arr[arr > 0]                    # Filtrage booléen
arr[np.where(arr > 0)]          # where
arr[0, :]                       # Première ligne
arr[:, 1:3]                     # Colonnes 1 à 2

# Opérations vectorisées (pas de boucles !)
resultat = arr * 2 + 1
carres = arr ** 2
masque = (arr > 0) & (arr < 10)

# Agrégations
arr.sum(), arr.mean(), arr.std()
arr.max(), arr.min(), arr.argmax()
np.percentile(arr, 95)
np.quantile(arr, [0.25, 0.5, 0.75])

# Algèbre linéaire
np.dot(A, B)              # Produit matriciel
A @ B                     # Équivalent
np.linalg.inv(A)          # Inverse
np.linalg.eigvals(A)      # Valeurs propres
np.linalg.svd(A)          # SVD

# Reshape
arr.reshape(10, 10)
arr.T                     # Transposée
arr.flatten()             # Aplatir
np.concatenate([a, b])    # Concaténer
np.stack([a, b])          # Empiler

# NaN handling
np.isnan(arr)
np.nanmean(arr)           # Moyenne ignorant NaN
np.nan_to_num(arr)        # NaN → 0
```

---

## 2. Pandas — Manipulation de Données

```python
import pandas as pd

# Chargement / Sauvegarde
df = pd.read_csv("data.csv")
df = pd.read_excel("data.xlsx", sheet_name="Feuil1")
df = pd.read_parquet("data.parquet")        # Rapide !
df = pd.read_sql("SELECT * FROM table", conn)
df.to_csv("output.csv", index=False)
df.to_parquet("output.parquet")

# Exploration rapide
df.head(10)
df.info()
df.describe()
df.shape, df.columns, df.dtypes
df.isnull().sum()                           # NaN par colonne
df.nunique()                                # Valeurs uniques
df.corr()                                   # Matrice de corrélation
df['colonne'].value_counts()                # Fréquences

# Sélection et filtrage
df['colonne']                               # Une colonne (Series)
df[['col1', 'col2']]                        # Plusieurs colonnes
df.loc[5:10, 'col1':'col3']                 # Par label
df.iloc[0:5, 0:3]                           # Par position
df[df['age'] > 30]                          # Filtrage
df[(df['age'] > 30) & (df['ville'] == 'Paris')]
df[df['nom'].isin(['Alice', 'Bob'])]

# Opérations sur colonnes
df['age_cat'] = pd.cut(df['age'], bins=[0, 18, 65, 120], labels=['jeune', 'adulte', 'senior'])
df['annee_naissance'] = 2024 - df['age']
df['nouvelle'] = df.apply(lambda row: row['a'] + row['b'], axis=1)

# Tri
df.sort_values('colonne', ascending=False)
df.sort_values(['col1', 'col2'], ascending=[True, False])

# GroupBy
df.groupby('categorie')['valeur'].mean()
df.groupby('categorie').agg({
    'valeur': ['mean', 'std', 'count'],
    'score': 'sum',
})
df.groupby('categorie')['valeur'].transform('mean')  # Même forme que df

# Pivot et reshape
df.pivot_table(values='valeur', index='categorie', columns='annee', aggfunc='mean')
df.melt(id_vars=['id'], value_vars=['jan', 'fev'], var_name='mois', value_name='valeur')

# Merge / Join
pd.merge(df1, df2, on='id', how='inner')    # inner, left, right, outer
pd.concat([df1, df2], axis=0)               # Empiler verticalement
pd.concat([df1, df2], axis=1)               # Côte à côte
df1.join(df2, on='id')

# Séries temporelles
df['date'] = pd.to_datetime(df['date'])
df.set_index('date', inplace=True)
df.resample('M').mean()                    # Agrégation mensuelle
df.rolling(window=7).mean()                # Moyenne mobile

# Nettoyage
df.dropna(subset=['colonne'])              # Supprimer NaN
df.fillna({'col1': 0, 'col2': 'inconnu'}) # Remplacer NaN
df.drop_duplicates(subset=['id'])
df['colonne'] = df['colonne'].str.lower().str.strip()
```

---

## 3. Visualisation

### Matplotlib / Seaborn

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_theme(style="whitegrid", palette="muted")

# Distributions
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
sns.histplot(data=df, x='valeur', kde=True, ax=axes[0])
sns.boxplot(data=df, x='categorie', y='valeur', ax=axes[1])
sns.violinplot(data=df, x='categorie', y='valeur', ax=axes[2])

# Relations
sns.scatterplot(data=df, x='x', y='y', hue='categorie', size='taille')
sns.lmplot(data=df, x='x', y='y', hue='categorie')
sns.pairplot(df, hue='cible')

# Catégoriel
sns.barplot(data=df, x='categorie', y='valeur')
sns.countplot(data=df, x='categorie')
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)

# Séries temporelles
plt.figure(figsize=(12, 4))
plt.plot(df.index, df['valeur'], linewidth=1)
plt.fill_between(df.index, df['min'], df['max'], alpha=0.3)
plt.title("Évolution temporelle")
plt.xlabel("Date")

# Sauvegarde
plt.savefig('graphique.png', dpi=300, bbox_inches='tight')
```

### Plotly (interactif)

```python
import plotly.express as px
import plotly.graph_objects as go

# Express (rapide)
fig = px.scatter(df, x='x', y='y', color='cat', size='z',
                 hover_data=['nom'], title='Titre')
fig = px.line(df, x='date', y='valeur', color='serie')
fig = px.bar(df, x='categorie', y='moyenne', error_y='std')
fig = px.histogram(df, x='valeur', marginal='box')
fig = px.imshow(df.corr(), text_auto='.2f')

# Graph Objects (contrôle fin)
fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers'))
fig.update_layout(title='Titre', xaxis_title='X', yaxis_title='Y')
fig.write_html('graphique.html')
```

---

## 4. Feature Engineering

```python
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    OneHotEncoder, LabelEncoder, OrdinalEncoder,
    PolynomialFeatures, PowerTransformer,
)

# Normalisation / Standardisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)  # PAS de fit sur le test !

# Encodage catégoriel
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = ohe.fit_transform(X_cat)

# Features polynomiales
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X)

# Gestion des outliers
from scipy import stats
z_scores = np.abs(stats.zscore(df['valeur']))
df_clean = df[z_scores < 3]

# IQR
Q1, Q3 = df['valeur'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[(df['valeur'] >= Q1 - 1.5*IQR) & (df['valeur'] <= Q3 + 1.5*IQR)]
```

---

## 5. Statistiques

```python
from scipy import stats

# Tests d'hypothèses
t_stat, p_value = stats.ttest_ind(groupe_a, groupe_b)
t_stat, p_value = stats.ttest_rel(avant, apres)
f_stat, p_value = stats.f_oneway(a, b, c)
chi2, p_value = stats.chi2_contingency(table_contingence)

# Corrélations
r, p = stats.pearsonr(x, y)
rho, p = stats.spearmanr(x, y)
tau, p = stats.kendalltau(x, y)

# Distributions
stats.norm.pdf(x, mu, sigma)        # Densité
stats.norm.cdf(x, mu, sigma)        # Cumulative
stats.norm.ppf(0.95, mu, sigma)     # Quantile

# Bootstrap
def bootstrap_ci(data, n_bootstrap=10000, ci=95):
    means = [np.mean(np.random.choice(data, len(data))) for _ in range(n_bootstrap)]
    return np.percentile(means, [(100-ci)/2, 50, 100-(100-ci)/2])

# Régression statsmodels
import statsmodels.api as sm
X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())  # R², p-values, coefficients
```

---

## 6. Séries Temporelles

```python
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet

# Décomposition
decomposition = seasonal_decompose(serie, model='additive', period=12)
decomposition.trend, decomposition.seasonal, decomposition.resid

# Stationnarité (ADF test)
resultat = adfuller(serie)
print(f"p-value: {resultat[1]}")  # < 0.05 = stationnaire

# ARIMA
model = ARIMA(serie, order=(1, 1, 1))
model_fit = model.fit()
previsions = model_fit.forecast(steps=30)

# Prophet (Facebook)
model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
model.fit(df)
future = model.make_future_dataframe(periods=365)
forecast = model.predict(future)
model.plot(forecast)
model.plot_components(forecast)
```

---

## 7. Pipelines ETL

```python
# Extraction
import requests
import sqlalchemy

# Depuis une API
response = requests.get("https://api.exemple.com/data", headers={"Authorization": "Bearer ..."})
data = response.json()

# Depuis une base SQL
engine = sqlalchemy.create_engine("postgresql://user:pass@host/db")
df = pd.read_sql("SELECT * FROM table WHERE date > '2024-01-01'", engine)

# Transformation (feature engineering, nettoyage)

# Chargement
df.to_parquet("data/processed/dataset.parquet")
df.to_csv("data/processed/output.csv")
df.to_sql("table_clean", engine, if_exists='replace')
```

---

## Références
- Pandas : https://pandas.pydata.org/docs/
- Seaborn : https://seaborn.pydata.org/
- Plotly : https://plotly.com/python/
- Statsmodels : https://www.statsmodels.org/