---
name: plotly
description: "Plotly / Dash : bibliothèque de visualisation interactive Python et JavaScript — graphiques 3D, cartes, animations, Dashboards complets avec callbacks Python."
version: 1.0.0
author: EVA
license: Privée EVA
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [plotly, dash, plotly-express, interactive, dataviz, python, dashboard, 3d, geo]
    homepage: https://plotly.com/
    related_skills: [d3-js, chart-js, dashboard-design, data-analysis-exploration]
prerequisites:
  commands: [python3, pip]
  pip_packages: [plotly, dash, pandas, numpy]
---

# Compétence Plotly / Dash — Visualisations Interactives & Dashboards Python

## Vue d'ensemble

**Plotly** est une bibliothèque de visualisation interactive multi-langage (Python, R, Julia, JS) qui produit des graphiques prêts pour le web avec zoom, pan, tooltips, et animations intégrés. **Plotly Express** fournit une API concise (~20 fonctions) pour les graphiques courants. **Dash** est le framework de dashboarding Python construit sur Plotly, permettant de créer des applications web interactives entièrement en Python.

**Philosophie :** *"Du DataFrame au graphique interactif en une ligne de code."*

**Architecture :** Plotly convertit les données en JSON (spec `Figure`), qui est rendu en D3.js/React dans le navigateur. Tout est interactif par défaut.

---

## Quand l'utiliser

Activez cette compétence lorsque l'utilisateur :

- Veut explorer des données en Python avec des graphiques interactifs (zoom, pan, hover).
- A besoin de graphiques 3D (surface, scatter3d, mesh3d).
- Construit une application Dashboard Python avec Dash.
- Souhaite des animations temporelles (play/pause sur des frames).
- Veux exporter des graphiques vers HTML/PNG/SVG/PDF.
- A besoin de cartes interactives (scattergeo, choropleth, mapbox).

---

## Prérequis

```bash
pip install plotly dash pandas numpy
```

---

## 1. Plotly Express — API Haute-Niveau

### 1.1 Nuage de Points (Scatter)

```python
import plotly.express as px

df = px.data.iris()

fig = px.scatter(
    df,
    x="sepal_width",
    y="sepal_length",
    color="species",
    size="petal_length",
    hover_data=["petal_width"],
    title="Iris : Largeur vs Longueur des Sépales",
    labels={"sepal_width": "Largeur (cm)", "sepal_length": "Longueur (cm)"},
    trendline="ols",  # Régression linéaire
)
fig.show()
```

### 1.2 Ligne et Série Temporelle

```python
import pandas as pd

df = px.data.gapminder().query("country == 'France'")

fig = px.line(
    df,
    x="year",
    y="gdpPercap",
    title="PIB par Habitant — France",
    markers=True,
    line_shape="spline",  # Lissage des courbes
)
fig.update_traces(line=dict(width=3))
fig.show()
```

### 1.3 Barres

```python
df = px.data.tips()

# Barres groupées
fig = px.bar(
    df,
    x="day",
    y="total_bill",
    color="sex",
    barmode="group",  # "relative" pour empilé, "overlay" pour superposition
    title="Addition par Jour et Sexe",
    text_auto=".2s",  # Affiche les valeurs
)
fig.update_traces(textposition="outside")
fig.show()

# Barres horizontales
fig = px.bar(df, x="total_bill", y="day", orientation="h", color="time")
```

### 1.4 Histogramme, Boxplot, Violin

```python
# Histogramme
fig = px.histogram(df, x="total_bill", color="sex", nbins=30, marginal="box")

# Boxplot
fig = px.box(df, x="day", y="total_bill", color="sex", notched=True, points="all")

# Violin
fig = px.violin(df, x="day", y="total_bill", color="sex", box=True, points="all")
```

### 1.5 Matrice de Corrélation (Heatmap)

```python
import plotly.figure_factory as ff

corr = df.select_dtypes("number").corr()
fig = ff.create_annotated_heatmap(
    corr.values,
    x=list(corr.columns),
    y=list(corr.index),
    colorscale="RdBu_r",
    annotation_text=corr.round(2).values,
)
fig.update_layout(title="Matrice de Corrélations")
fig.show()
```

### 1.6 Carte Choroplèthe

```python
# Carte mondiale
df = px.data.gapminder().query("year == 2007")

fig = px.choropleth(
    df,
    locations="iso_alpha",
    color="gdpPercap",
    hover_name="country",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="PIB par Habitant (2007)",
    projection="natural earth",
)
fig.show()

# Carte USA (états)
fig = px.choropleth(
    df_states,
    locations="state",
    locationmode="USA-states",
    color="unemployment",
    scope="usa",
)
```

---

## 2. Graphiques 3D

```python
# Scatter 3D
fig = px.scatter_3d(
    df,
    x="sepal_length",
    y="sepal_width",
    z="petal_length",
    color="species",
    size="petal_width",
    opacity=0.7,
    title="Iris — 3 Dimensions",
)

# Surface 3D
import numpy as np
x = np.arange(-5, 5, 0.1)
y = np.arange(-5, 5, 0.1)
X, Y = np.meshgrid(x, y)
Z = np.sin(np.sqrt(X**2 + Y**2))

fig = go.Figure(data=[go.Surface(z=Z, x=x, y=y, colorscale="Viridis")])
fig.update_layout(title="Surface sin(r)/r", scene=dict(
    xaxis_title="X", yaxis_title="Y", zaxis_title="Z"
))

# Line 3D
fig = px.line_3d(df, x="x", y="y", z="z", color="trajectory")
```

---

## 3. Graphiques Avancés (API Graph Objects)

Pour un contrôle fin, utiliser `plotly.graph_objects` :

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Graphiques multiples en grille
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=("Scatter", "Barres", "Carte", "3D"),
    specs=[
        [{"type": "scatter"}, {"type": "bar"}],
        [{"type": "scattergeo"}, {"type": "scene"}],
    ],
)

fig.add_trace(go.Scatter(x=[1,2,3], y=[4,5,6], mode="lines+markers"), row=1, col=1)
fig.add_trace(go.Bar(x=["A","B","C"], y=[10,20,15]), row=1, col=2)
fig.add_trace(go.Scattergeo(lon=[2.35], lat=[48.85], mode="markers"), row=2, col=1)
fig.add_trace(go.Scatter3d(x=[0,1,2], y=[0,1,2], z=[0,1,2]), row=2, col=2)

fig.update_layout(title="Dashboard Multi-Graphiques", showlegend=False)
fig.show()
```

### 3.1 Candlestick (Finance)

```python
fig = go.Figure(data=[go.Candlestick(
    x=df["date"],
    open=df["open"], high=df["high"],
    low=df["low"], close=df["close"],
)])
fig.update_layout(
    title="OHLC — BTC/USD",
    xaxis_rangeslider_visible=False,
    yaxis_title="Prix (USD)",
)
```

### 3.2 Sankey (Diagramme de Flux)

```python
fig = go.Figure(data=[go.Sankey(
    node=dict(
        label=["Source A", "Source B", "Étape 1", "Étape 2", "Final"],
        color=["blue", "green", "gray", "gray", "red"],
    ),
    link=dict(
        source=[0, 0, 1, 2, 2, 3],
        target=[2, 3, 3, 3, 4, 4],
        value=[8, 4, 6, 5, 7, 9],
    )
)])
fig.update_layout(title="Diagramme Sankey — Flux de Données")
```

### 3.3 Funnel (Entonnoir)

```python
fig = go.Figure(go.Funnel(
    y=["Visiteurs", "Inscrits", "Actifs", "Payants"],
    x=[10000, 2500, 800, 120],
    textinfo="value+percent initial",
    marker=dict(color=["#636efa", "#ef553b", "#00cc96", "#ab63fa"]),
))
fig.update_layout(title="Entonnoir de Conversion")
```

### 3.4 Waterfall

```python
fig = go.Figure(go.Waterfall(
    name="P&L",
    orientation="v",
    measure=["relative", "relative", "total", "relative", "total"],
    x=["Revenus", "Coûts", "Marge Brute", "Taxes", "Bénéfice Net"],
    y=[100000, -40000, None, -15000, None],
    connector={"line": {"color": "rgb(63, 63, 63)"}},
))
fig.update_layout(title="Compte de Résultat")
```

---

## 4. Animations

### 4.1 Animation par Frames (Temporal)

```python
df = px.data.gapminder()

fig = px.scatter(
    df,
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    color="continent",
    animation_frame="year",   # Une frame par année
    animation_group="country",
    log_x=True,
    size_max=60,
    range_x=[100, 100000],
    range_y=[25, 90],
    title="Développement Mondial (1952-2007)",
)
fig.show()
```

### 4.2 Animation avec Slider Personnalisé

```python
import numpy as np

frames = []
for t in np.linspace(0, 2*np.pi, 50):
    x = np.cos(t + np.linspace(0, 2*np.pi, 20))
    y = np.sin(t + np.linspace(0, 2*np.pi, 20))
    frames.append(go.Frame(data=[go.Scatter(x=x, y=y, mode="markers")]))

fig = go.Figure(
    data=[go.Scatter(x=[], y=[], mode="markers")],
    layout=go.Layout(
        title="Animation Sinusoïdale",
        updatemenus=[{
            "type": "buttons",
            "buttons": [{"label": "▶", "method": "animate", "args": [None]},
                        {"label": "⏸", "method": "animate", "args": [[None], {"mode": "immediate"}]}],
        }],
        sliders=[{
            "steps": [{"args": [[f.name]], "label": f.name, "method": "animate"}
                      for f in frames],
        }]
    ),
    frames=frames,
)
```

---

## 5. Dash — Applications Web

### 5.1 Application Minimale

```python
from dash import Dash, html, dcc, Input, Output
import plotly.express as px

app = Dash(__name__)
df = px.data.iris()

app.layout = html.Div([
    html.H1("Dashboard Iris", style={"textAlign": "center"}),
    dcc.Dropdown(
        id="x-variable",
        options=[{"label": c, "value": c} for c in df.columns[:4]],
        value="sepal_length",
    ),
    dcc.Graph(id="scatter-plot"),
])

@app.callback(
    Output("scatter-plot", "figure"),
    Input("x-variable", "value"),
)
def update_chart(x_var):
    fig = px.scatter(df, x=x_var, y="petal_length", color="species")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
```

### 5.2 Layouts et Composants

```python
app.layout = html.Div([
    # En-tête
    html.Header([
        html.H1("Dashboard Ventes"),
        html.Nav([
            dcc.Link("Accueil", href="/"),
            dcc.Link("Analyse", href="/analyse"),
        ])
    ]),

    # Contenu
    html.Main([
        # Row
        html.Div([
            # Colonne gauche : filtres
            html.Div([
                html.H3("Filtres"),
                dcc.Dropdown(id="region", options=[...], multi=True),
                dcc.DatePickerRange(id="date-range"),
                dcc.RangeSlider(id="amount-range", min=0, max=10000),
                html.Button("Réinitialiser", id="reset-btn"),
            ], className="sidebar"),

            # Colonne droite : graphiques
            html.Div([
                dcc.Graph(id="line-chart"),
                dcc.Graph(id="bar-chart"),
            ], className="main-content"),
        ], className="row"),
    ]),

    # Footer avec mise à jour
    html.Footer(id="last-update"),
])

# Tabs / Onglets
dcc.Tabs([
    dcc.Tab(label="Vue d'ensemble", children=[...]),
    dcc.Tab(label="Analyse détaillée", children=[...]),
    dcc.Tab(label="Export", children=[...]),
])

# Store (données en session)
dcc.Store(id="filtered-data", storage_type="memory")  # memory, session, local
```

### 5.3 Callbacks Avancés

```python
# Callback multi-sorties
@app.callback(
    Output("line-chart", "figure"),
    Output("bar-chart", "figure"),
    Output("kpi-text", "children"),
    Input("region", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    prevent_initial_call=False,
)
def update_dashboard(regions, start_date, end_date):
    df_filtered = df.copy()
    if regions:
        df_filtered = df_filtered[df_filtered["region"].isin(regions)]
    if start_date:
        df_filtered = df_filtered[df_filtered["date"] >= start_date]

    line_fig = px.line(df_filtered, x="date", y="sales", color="region")
    bar_fig = px.bar(df_filtered, x="product", y="sales")
    kpi = f"Ventes totales : {df_filtered['sales'].sum():,.0f} €"

    return line_fig, bar_fig, kpi

# Callback en cascade (dépendances entre outputs)
@app.callback(
    Output("sub-product", "options"),
    Input("product", "value"),
)
def update_sub_products(product):
    return [{"label": p, "value": p} for p in df[df["product"] == product]["sub_product"].unique()]

# Pattern-Matching Callbacks (composants dynamiques)
@app.callback(
    Output({"type": "graph", "index": MATCH}, "figure"),
    Input({"type": "dropdown", "index": MATCH}, "value"),
)
def update_dynamic_graph(variable):
    return px.histogram(df, x=variable)

# Clientside Callback (JS côté navigateur pour performances)
app.clientside_callback(
    """
    function(value) {
        return document.title = "Dashboard - " + value;
    }
    """,
    Output("page-title", "children"),
    Input("region", "value"),
)
```

### 5.4 Composants Avancés

```python
# DataTable interactive
from dash import dash_table

dash_table.DataTable(
    id="table",
    columns=[{"name": c, "id": c, "type": "numeric" if df[c].dtype in ["int64", "float64"] else "text"} for c in df.columns],
    data=df.to_dict("records"),
    page_size=20,
    sort_action="native",
    filter_action="native",
    row_selectable="multi",
    style_table={"overflowX": "auto"},
    style_cell={"textAlign": "left", "padding": "8px"},
    style_header={"fontWeight": "bold", "backgroundColor": "#f8f9fa"},
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "#f8f9fa"},
    ],
)

# Graphique avec zoom/pan
dcc.Graph(id="main-chart", config={
    "scrollZoom": True,
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["sendDataToCloud"],
    "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
})

# Intervalle de rafraîchissement
dcc.Interval(id="refresh-interval", interval=60*1000, n_intervals=0)  # 60 secondes
```

### 5.5 Thèmes et Style

```python
# Dash Bootstrap Components
import dash_bootstrap_components as dbc

app = Dash(external_stylesheets=[dbc.themes.DARKLY])  # ou SLATE, SOLAR, CYBORG, MINTY, FLATLY

# Layout avec Bootstrap
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard"), width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filtres"),
                dbc.CardBody([...]),
            ]),
        ], width=3),
        dbc.Col([
            dcc.Graph(id="chart"),
        ], width=9),
    ]),
])
```

---

## 6. Export et Déploiement

```python
# Export HTML (autonome, pas de serveur nécessaire)
fig.write_html("graphique.html", include_plotlyjs="cdn", full_html=False)

# Export PNG (nécessite kaleido ou orca)
fig.write_image("graphique.png", width=1200, height=800, scale=2)

# Export SVG
fig.write_image("graphique.svg")

# Export PDF via Plotly Orca
fig.write_image("graphique.pdf")

# Déploiement Dash
# 1. Gunicorn + Nginx (production)
gunicorn app:server -b 0.0.0.0:8050 -w 4

# 2. Docker
FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8050
CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8050"]

# 3. Railway / Render / Heroku (Procfile)
web: gunicorn app:server
```

---

## Pièges Courants (Pitfalls)

1. **Graphique vide dans Dash.**
   - *Erreur :* Le callback retourne `None` accidentellement.
   - *Correction :* Toujours retourner une figure Plotly valide, jamais `None`. Utiliser `return dash.no_update` pour éviter un reset.

2. **Callbacks en boucle infinie.**
   - *Erreur :* Output A dépend de Input B, et Output B dépend de Input A.
   - *Correction :* Vérifier les dépendances croisées. Utiliser `prevent_initial_call=True` si nécessaire.

3. **Lenteur avec de gros DataFrames.**
   - *Erreur :* Passer un DataFrame de 100 000 lignes dans un callback — il est sérialisé en JSON à chaque appel.
   - *Correction :* Utiliser `dcc.Store` côté client, ou agréger les données avant de les passer à Plotly.

4. **Carte vide sans erreur.**
   - *Erreur :* Les codes pays dans `locations` ne correspondent pas au format attendu (`iso_alpha` vs `country names`).
   - *Correction :* Vérifier le paramètre `locationmode` : `ISO-3` (défaut), `USA-states`, `country names`.

5. **Dash qui ne marche pas en production.**
   - *Erreur :* `app.run_server(debug=True)` utilisé en prod.
   - *Correction :* Utiliser Gunicorn/WSGI : `gunicorn app:server`. En développement, `debug=True` est OK.

6. **Export PNG qui échoue.**
   - *Erreur :* `write_image` nécessite `kaleido` ou `orca` installé.
   - *Correction :* `pip install -U kaleido` ou `conda install -c plotly plotly-orca`.

---

## Ressources

- [Documentation Plotly Python](https://plotly.com/python/)
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Express Gallery](https://plotly.com/python/plotly-express/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Plotly Chart Studio](https://chart-studio.plotly.com/)

---

## Checklist

- [ ] Plotly est installé (`pip install plotly dash`).
- [ ] Les graphiques utilisent Plotly Express pour les cas simples, Graph Objects pour le contrôle fin.
- [ ] Les callbacks Dash sont bien chaînés (pas de boucles infinies).
- [ ] Les DataFrames sont filtrés avant d'être passés aux graphiques.
- [ ] Les cartes ont le bon `locationmode`.
- [ ] L'export HTML/PNG est fonctionnel.
- [ ] En production, le serveur utilise Gunicorn (pas `run_server`).
- [ ] Les animations ont des frames correctement structurées.
