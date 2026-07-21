---
name: macro-indicateurs
description: >-
  Analyser les indicateurs macroéconomiques (PIB, inflation CPI/PCE, emploi NFP,
  PMI, taux directeurs Fed/BCE/BOJ, ventes au détail, confiance consommateur) 
  et évaluer leur impact sur les marchés actions, forex, obligations et matières
  premières. Synthèse de calendrier économique, calcul de surprises, corrélation
  actifs-indicateurs.
category: finance
---

# Analyse Macroéconomique — Indicateurs Clés

## Présentation

Ce skill couvre l'analyse des principaux indicateurs macroéconomiques publiés
par les banques centrales et agences statistiques, ainsi que leur impact sur
les classes d'actifs. L'objectif est d'identifier les régimes de marché
(inflationniste, récessif, expansion) et d'en déduire des biais directionnels
pour les décisions de trading / allocation.

**Déclencheurs :** "macroéconomie", "PIB", "inflation", "CPI", "NFP",
"emploi US", "Fed", "BCE", "PMI", "indicateurs macro", "calendrier éco",
"taux directeur", "récession".

## Sources de données (ordre de fiabilité)

| Source | Accès | Couverture |
|---|---|---|
| **FRED (St. Louis Fed)** | `fredapi` Python, API REST gratuite | US + séries historiques longues |
| **Investing.com** | Web scraping / RSS | Calendrier économique mondial, consensus |
| **TradingEconomics** | API payante, scrape partiel | 200+ pays, ~20M séries |
| **Bloomberg / Reuters** | Terminal (payant) | Temps réel, données propriétaires |
| **Yahoo Finance** | `yfinance` Python | Indices, taux, commodités, crypto |

Pour un agent automatisé : FRED (séries US historiques) + Investing.com
(calendrier + consensus + surprise) + Yahoo Finance (prix temps réel).

## Indicateurs par catégorie

### ① Croissance & Production

| Indicateur | Fréquence | Source | Impact Marché |
|---|---|---|---|
| **PIB (GDP)** | Trimestriel | BEA (US), INSEE (FR) | Fort — valide/réfute le cycle |
| **Ventes au détail** | Mensuel | Census Bureau | Moyen — consommation driver #1 |
| **Production industrielle** | Mensuel | Fed | Fort — corrélé commodités |
| **Commandes de biens durables** | Mensuel | Census Bureau | Moyen — indicateur avancé |
| **PMI Manufacturing / Services** | Mensuel | S&P Global / ISM | Très fort — avance le PIB de 1-3 mois |

### ② Inflation

| Indicateur | Fréquence | Source | Impact Marché |
|---|---|---|---|
| **CPI (indice des prix)** | Mensuel | BLS | Très fort — influence directe Fed |
| **Core CPI (hors alimentation/énergie)** | Mensuel | BLS | Très fort — mesure sous-jacente |
| **PCE (dépenses conso)** | Mensuel | BEA | Fort — mesure préférée de la Fed |
| **Core PCE** | Mensuel | BEA | Très fort — cible officielle Fed |
| **PPI (prix production)** | Mensuel | BLS | Moyen — avance le CPI |
| **Expectations d'inflation (Michigan / NY Fed)** | Mensuel | U.Michigan / NY Fed | Moyen — anticipations = autoréalisatrices |

### ③ Emploi

| Indicateur | Fréquence | Source | Impact Marché |
|---|---|---|---|
| **NFP (Non-Farm Payrolls)** | Mensuel (1er vendredi) | BLS | Très fort — "le" chiffre du mois |
| **Taux de chômage** | Mensuel | BLS | Fort |
| **JOLTS (offres d'emploi)** | Mensuel | BLS | Moyen — tension marché du travail |
| **Salaires horaires moyens** | Mensuel | BLS | Fort — pousse l'inflation |
| **Initial Jobless Claims** | Hebdomadaire | DOL | Moyen — avance le NFP |

### ④ Taux & Politique monétaire

| Indicateur | Fréquence | Source | Impact Marché |
|---|---|---|---|
| **Fed Funds Rate** | 8 réunions/an | Fed | Très fort — tout l'acte |
| **Dot Plot / SEP** | Trimestriel (mars/juin/sep/déc) | Fed | Très fort — forward guidance |
| **Balance sheet (QT/QE)** | Mensuel | Fed | Fort — liquidité |
| **Taux BCE / BOJ / BOE** | Mensuel / 8 réunions | Banques centrales | Fort pour EUR/JPY/GBP |
| **Obligations à 2-10 ans (pente)** | Quotidien | Trésor US | Très fort — prédit récession |

### ⑤ Confiance & Sentiment

| Indicateur | Fréquence | Source | Impact Marché |
|---|---|---|---|
| **Conference Board Consumer Confidence** | Mensuel | Conference Board | Moyen |
| **U.Michigan Consumer Sentiment** | Mensuel (2 fois) | U.Michigan | Moyen |
| **Ifo Business Climate (Allemagne)** | Mensuel | Ifo Institute | Fort pour EUR |
| **ZEW Economic Sentiment** | Mensuel | ZEW | Moyen — avance |

## Calendrier économique automatisé

1. **Scraper** le calendrier Investing.com des 7 prochains jours via
   `ai_scrape(url="https://www.investing.com/economic-calendar/")`.
2. **Classer** les événements par impact : 1 à 3 étoiles.
3. **Cross-référencer** avec les positions ouvertes (si trading actif).
4. **Alerte** sur les événements 3 étoiles 15 min avant publication :
   ```python
   # Pseudo-code : cronjob qui scrape et compare au consensus
   avant = get_consensus("NFP")     # ex: 200K
   publié = get_actual("NFP")       # ex: 287K
   surprise = (publié - avant) / std_dev(prévisions)
   if abs(surprise) > 1.5:
       # Impact fort — adapter positions
   ```

## Calcul de surprise

La **surprise macro** est l'écart entre le chiffre publié et le consensus
Bloomberg/Reuters, normalisé par l'écart-type des prévisions :

```
ZS = (publié - consensus) / σ(prévisions)
```

- |ZS| < 0.5 = dans les attentes
- |ZS| 0.5–1.5 = surprise modérée
- |ZS| > 1.5 = surprise forte → mouvement >1σ sur l'actif

Utiliser `macro-citigroup-surprise-index` (CSI) comme agrégateur : CESI
(Europe), CSUS (US), CSEA (Asie).

## Corrélations actifs vs macro (règles empiriques)

| Régime | Actions | Obligations | Or | USD | BTC |
|---|---|---|---|---|---|
| **Croissance forte + inflation basse** | ↗ Fort | ↗ (courte) | ↘ | → | ↗ |
| **Croissance forte + inflation haute** | ↘ | ↗ longue (douleur) | ↗ | ↗ | →/↘ |
| **Récession + désinflation** | ↘ Fort | ↗ Fort | →/↘ | ↗ (safe haven) | ↘ |
| **Récession + stagflation** | ↘ Fort | ↘ Fort | ↗ Fort | ↗ | → |
| **Choc de liquidité (QT)** | ↘ | ↘ | ↘ | ↗ | ↘ Fort |

## Pièges à éviter

1. **Révisions** : Le PIB et l'emploi sont souvent révisés 2 fois. Ne pas
   trader une seule publication, attendre 2-3 confirmations.
2. **Forward guidance** : Les banques centrales télégraphient leurs décisions
   des semaines à l'avance — le jour J, le mouvement peut être inverse
   ("buy the rumor, sell the fact").
3. **Effet de base** : La variation YoY de l'inflation peut être trompeuse
   si l'année précédente était extrême (base effect). Toujours regarder MoM
   annualisé et trimestre annualisé.
4. **Calendrier US centre le monde** : Le NFP, CPI, FOMC dominent tout.
   Les publications chinoises (PIB, PMI Caixin) comptent aussi pour les
   commodités mais sont moins suivies → opportunité d'arbitrage.
5. **Fréquence = bruit** : Les indicateurs hebdomadaires (jobless claims)
   sont volatils. Utiliser une moyenne mobile 4 semaines.

## Skills liés

- `macro-politique-monetaire` — analyse des banques centrales
- `backtesting-strategies` — backtester des stratégies macro
- `value-at-risk` — intégrer les chocs macro dans le risk model

## Vérification

- [ ] Le calendrier économique est scrapé et filtré par impact
- [ ] Les positions ouvertes sont cross-référencées avec les publications à venir
- [ ] Le calcul de surprise est fonctionnel (Z-score)
- [ ] Les corrélations de régime sont appliquées au portefeuille