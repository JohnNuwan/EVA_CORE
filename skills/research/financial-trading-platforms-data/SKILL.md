---
name: financial-trading-platforms-data
description: "Compétence niveau ingénieur/docteur sur les plateformes financières et sources de données de trading. Couvre Bloomberg Terminal, Reuters Eikon, APIs de trading (Alpaca, IBKR, Binance, FTX), données de marché (FRED, Yahoo Finance, Alpha Vantage, Polygon, Quandl), backtesting (Backtrader, Zipline, VectorBT, QuantConnect), crypto analytics (Dune, Nansen, Glassnode, CoinGecko, CoinMarketCap), DeFi data (TheGraph, DeFiLlama, DexScreener), et ML financier open-source."
category: research
tags: [finance, trading, quant, backtesting, crypto, ml-financier, bloomberg, donnees-marche]
---

# Plateformes Financières et Données de Trading — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des plateformes, APIs et sources de données pour la recherche en finance quantitative, le trading algorithmique, l'analyse on-chain crypto, et le machine learning financier. Conçu pour un niveau ingénieur/docteur nécessitant une compréhension approfondie de l'infrastructure de données financières.

---

## 1. Terminaux Professionnels (TIER 1 — Payant, Institutionnel)

### Bloomberg Terminal
- **Prix** : ~$24,000/an/terminal
- **Données** : Marchés actions, fixed income, FX, commodities, derivatives
- **Fonctionnalités** : Screener, charting, news, analytics, chat
- **API** : Bloomberg API (COM, .NET, Java, Python)
- **Excel** : Bloomberg Add-in (BDP, BDH, BDS)
- **Alternatives** : Bloomberg Anywhere (web), Bloomberg Terminal App
- **Forces** : Standard de l'industrie, couverture complète
- **Faiblesses** : Coût prohibitif, interface vieillissante, courbe d'apprentissage raide

### Reuters Eikon / Refinitiv Workspace
- **Prix** : ~$20,000-$25,000/an
- **Données** : Marchés globaux, news Reuters, analyse fondamentale
- **API** : Eikon Data API (Python, R, .NET)
- **Intégration** : Excel, Power BI, Databricks
- **Particularité** : Contenu propriétaire Reuters, données ESG
- **Successeur** : LSEG Workspace (post-fusion LSEG)

### FactSet
- **Prix** : ~$15,000-$20,000/an
- **Données** : Screening, analyse de portefeuille, risk analytics
- **API** : FactSet API (Python, Java, .NET)
- **Spécialité** : Buy-side, gestion de portefeuille, performance attribution
- **Open FactSet Marketplace** : apps et data partners

### Capital IQ (S&P Global)
- **Prix** : ~$15,000-$20,000/an
- **Spécialité** : Comptes financiers, M&A, transactions, screening
- **Excel** : CIQ Excel Add-in
- **API** : S&P Global Market Intelligence API
- **Forces** : Données fondamentales, transcripts earnings calls

### S&P Global Market Intelligence
- **Platform** : S&P Capital IQ Pro
- **Données** : Credit ratings, supply chain, energy, maritime
- **API** : Market Intelligence API, Platts API
- **Spécialité** : Analyse sectorielle, données ESG, indices

---

## 2. APIs de Trading (TIER 2 — Commissions/Payant)

### Alpaca
- **Commission-free** : Trading actions et crypto US
- **API** : REST + WebSocket, Polygon.io intégré
- **Pricing** : API gratuit, frais de routage (0.005-0.03$/action)
- **Paper Trading** : Sandbox complet
- **Particularité** : Trading API-first, crypto 24/7
- **SDK** : Python, JavaScript, Go, Rust

### Interactive Brokers (IBKR)
- **API** : TWS API (Python, Java, C++, C#, ActiveX)
- **IB Gateway** : Headless, sans UI
- **IBKR API v2** : REST API moderne (2024+)
- **Client Portal API** : Web-based, OAuth2
- **Pricing** : Fixed ($0.005/action) ou tiered
- **Accès** : Marchés globaux, options, futures, forex, bonds
- **IB Datasource** : Données historiques et temps réel

### Binance / Coinbase (Crypto)
- **Binance API** : REST + WebSocket, spot/futures/margin
- **Coinbase Pro API** (Advanced Trade) : REST + WebSocket
- **SDK** : Python (ccxt, python-binance, coinbase-advanced-py)
- **Pricing** : Maker/taker ~0.1%, volume discounts
- **WebSocket** : Order book, trades, ticker, klines

### OANDA (FX)
- **API** : v20 REST API (forex, CFDs, indices, commodities)
- **Pricing** : Spread variable, commission sur comptes pro
- **Particularité** : SLA 99.99%, Data Center co-location
- **SDK** : Python, Java, Node.js, .NET

### Trade Republic (Unofficial — Read-Only Only)
- **Librairie** : `trade_republic` (v0.1.1+, PyPI : `pip install trade_republic`)
- **⚠️ Non-officielle** : Reverse-engineered de l'API mobile, pas de support officiel Trade Republic
- **⚠️ Risques** : Techniquement contre les CGU — usage **lecture seule uniquement**, jamais de trading
- **Authentification** :
  1. POST `api.traderepublic.com/api/v1/auth/web/login` avec `phoneNumber` + `pin`
  2. Code 2FA reçu par SMS → POST avec le code
  3. Token de session récupéré dans le cookie `tr_session` (Set-Cookie)
- **Token** : À persister dans `~/.hermes/.tr_token.json` (chmod 600) — ne pas stocker le PIN
- **Connexion** : WebSocket (`wss://api.traderepublic.com`), nécessite token
- **Services disponibles (lecture)** :
  - `account_service` : Comptes, cash disponible, infos
  - `portfolio_service` : Positions (ISIN, quantité, prix d'achat, valeur, P&L)
  - `transaction_service` : Historique des transactions
  - `order_service` : Ordres en cours (lecture seule)
  - `market_data_service` : Données marché
  - `search_service` : Recherche d'instruments
  - `instrument_service` : Infos instruments
- **Première connexion** : Interactive (nécessite code 2FA par SMS) — exécuter en PTY
- **Venv dédié** : Créer un venv (`python3 -m venv ~/.trade-republic-venv`) pour éviter PEP 668
- **Token expiré** : Reconnexion complète nécessaire (run init script again)
- **Exemple d'init** : Voir `references/automated-market-monitoring.md`

### Autres APIs
- **Tradier** : API brokerage $10/mois, options/actions
- **Schwab API** (ex-TD Ameritrade) : API REST gratuite
- **E*TRADE API** : REST, OAuth, actions/options
- **TradeStation** : API REST + WebSocket, strategy backtesting
- **LMAX** : API forex/crypto, exchange régulé UK

---

## 3. Données de Marché Gratuites/Abordables (TIER 3 — Gratuit/Bas-coût)

### FRED (Federal Reserve Economic Data, St. Louis Fed)
- **860,000+ séries** : PIB, inflation, emploi, taux, monnaie
- **API** : REST JSON, gratuit
- **SDK** : `fredapi` Python, `fredr` R
- **Catégories** : National, international, régional, industrie
- **Fréquence** : Quotidien, hebdomadaire, mensuel, trimestriel, annuel

### Yahoo Finance (yfinance)
- **API** : Bibliothèque Python `yfinance` (non-officielle)
- **Données** : Prix historiques, fondamentaux, news, dividendes
- **Limitations** : Pas de données temps réel, rate limiting, fiabilité variable
- **Usage** : Prototypage, analyse personnelle, backtesting simple
- **Alternatives** : `yfinance` with `investpy`, `yahooquery`

### Alpha Vantage
- **API** : REST JSON, gratuit (5 req/min, 500 req/jour)
- **Données** : Actions, FX, crypto, indicatifs, sector performance
- **Indicateurs** : 50+ indicateurs techniques
- **Premium** : $49.99/mois (75 req/min)
- **SDK** : `alpha_vantage` Python

### Polygon.io
- **API** : Actions, options, crypto, forex, indices
- **Gratuit** : API key de base, données quot historiques
- **Payant** : Temps réel, fundamental, options, websocket
- **Pricing** : Starter $29/mois, Pro $199/mois
- **Forces** : Qualité données, websocket temps réel, splits/dividends

### Intrinio
- **Pricing** : $19-299/mois selon niveau
- **Données** : Marchés US, fondamentaux, SEC filings, ESG
- **SDK** : Python, R, Node.js
- **API** : REST, WebSocket, batch download
- **Particularité** : Données alternatives, SEC filings, news sentiment

### Quandl / Nasdaq Data Link
- **Gratuit** : 200+ datasets (Wiki EOD, macro, commodities)
- **Premium** : Données propriétaires (Shiller, CoreLogic, Zillow)
- **API** : REST JSON, Python/R/Julia SDK
- **Migration** : Acquired par Nasdaq, renommé Nasdaq Data Link
- **Usage** : Data science, ML, recherche académique

---

## 4. Backtesting et Trading Algorithmique

### Backtrader
- **Framework** : Python, open-source
- **Fonctionnalités** : Multi-data, multi-timeframe, live trading
- **Brokers** : IB, Alpaca, OANDA, Binance (via custom)
- **Analytics** : Sharpe, drawdown, CAGR, trades report
- **Forces** : Mature, documentation riche, communauté active
- **Faiblesses** : Monothread, pas de parallélisme

### Zipline Reloaded (Quantopian Successor)
- **Framework** : Python, événementiel
- **Origine** : Quantopian → open-source → Zipline Reloaded
- **Pipeline API** : Factor computation, data filtering
- **Data Bundle** : Bundles personnalisables
- **Usage** : Recherche, backtesting, factor investing

### VectorBT
- **Framework** : Python, vectorisé (pas de boucle)
- **Performance** : Analyse de 10k+ portefeuilles en < 1s
- **Spécificités** : Portfolio optimization, factor analysis, indicators
- **Pro** : Temps réel, options, crypto
- **Usage** : Screening, walk-forward, hyperparameter optimization

### QuantConnect (LEAN Engine)
- **Cloud** : IDE web, backtesting, live trading
- **LEAN** : C# engine open-source, Python/C# API
- **Brokers** : 15+ brokers intégrés (IB, Binance, OANDA, GDAX)
- **Datasets** : 100+ datasets (quotes, fundamentals, alternative)
- **Research** : Jupyter Notebooks intégrés
- **Alpha Stream** : Marketplace d'alpha

### FreqTrade (Crypto)
- **Framework** : Python, open-source, crypto-focused
- **Stratégies** : Custom Python, indicators, ML
- **Exchanges** : 20+ exchanges (Binance, Kraken, Coinbase, Bybit)
- **Backtesting** : Historique, hyperopt, walk-forward
- **Features** : Telegram bot, web UI, dry-run, portfolio management

### Autres Frameworks
- **bt** (Python) : Backtesting flexible, portfolio-oriented
- **QuantLib** : Pricing dérivés, risk (C++/Python)
- **vnpy** : Trading platform Python, futures/forex/crypto
- **Blankly** : Multi-exchange, algo trading, events
- **Hummingbot** : Market making, crypto native

---

## 5. Crypto Analytics

### Dune Analytics
- **On-chain SQL** : Query blockchain data (Ethereum, Solana, L2s)
- **Datasets** : Transfers, DEX, lending, NFT, stablecoins
- **Visualisations** : Dashboards, charts, embeddings
- **Gratuit** : Requêtes publiques, limitations
- **Premium** : Dune Plus, Dune API ($)
- **Communauté** : 100k+ dashboards, 100M+ queries

### Nansen
- **Wallet Labels** : Smart money, VCs, whales, insiders
- **Analytics** : Token flows, protocol health, NFT analytics
- **API** : Nansen API (payant)
- **Dashboards** : Portfolio tracking, wallet monitoring
- **Pricing** : Enterprise, pas de plan gratuit

### Glassnode
- **On-chain Metrics** : Réserve échange, SOPR, MVRV, NUPL
- **Studio** : Dashboard personnalisé, alertes
- **API** : Glassnode API (payant, 200+ metrics)
- **Fréquence** : 1min, 1h, 24h, weekly
- **Spécialité** : Bitcoin dominance, data science crypto

### CoinGecko / CoinMarketCap
- **API** : REST JSON, gratuit (rate limit: 10-50 req/min)
- **Données** : Prix, volume, market cap, exchanges, pairs
- **CoinGecko Premium** : WebSocket, 1000+ endpoints
- **CoinMarketCap API** : Pro tiers ($79-999/mois)
- **Usage** : Base de tout projet crypto, token listing

### DeFiLlama
- **TVL** : Total Value Locked par protocole, chaîne, catégorie
- **Yields** : APY sur lending/farming, historique
- **API** : REST JSON, gratuit
- **Données** : Volume DEX, stablecoins, airdrops, fees
- **Spécialité** : Données DeFi les plus complètes

### DexScreener
- **DEX Pairs** : Prix, liquidité, volume, transactions
- **Multi-chain** : Ethereum, Solana, BSC, Arbitrum, Base, etc.
- **API** : REST + WebSocket (payant)
- **Usage** : Sniper bot, token discovery, charting
- **Pricing** : $0.5/1M req (WebSocket)

### The Graph
- **Indexing Protocol** : Query blockchain via GraphQL
- **Subgraphs** : 1000+ subgraphs déployés
- **Hosted Service** : Gratuit pour subgraphs publics
- **Network** : Décentralisé, GRT token
- **Usage** : Custom on-chain data, analytics, dApps

---

## 6. Machine Learning Financier Open-Source

### TradingAgents
- **Stars** : ~91k GitHub
- **Approche** : Multi-agent LLM pour trading
- **Architecture** : Agents spécialisés (analyse, risk, execution)
- **Tech** : LLM, RAG, mémoire, outils
- **Usage** : Trading algorithmique augmenté par IA

### ai-berkshire
- **Stars** : ~11k GitHub
- **Approche** : Value investing assisté par IA
- **Fonctionnalités** : Screening, analyse fondamentale, rapports
- **Tech** : LLM, web scraping, NLP
- **Usage** : Analyse fondamentale automatisée

### FinRL
- **Framework** : RL pour trading financier
- **Bibliothèques** : Stable-Baselines3, RLlib, ElegantRL
- **Environnements** : DJIA 30, S&P 500, crypto, FX
- **Algorithmes** : PPO, DQN, A2C, SAC, TD3
- **Intégration** : Yahoo Finance, OpenAI Gym, QuantConnect

### FinGPT
- **LLM financier** : Fine-tuning LLaMA/ChatGLM sur données financières
- **Données** : News, SEC filings, earnings calls, analyst reports
- **Tâches** : Sentiment, NER, summarization, QA
- **Framework** : Low-rank adaptation (LoRA), data curation
- **Approche** : Open-source, auto-hébergé

### FinBERT
- **BERT financier** : Pre-trained sur données financières
- **Tâches** : Sentiment analysis, NER, relation extraction
- **Données** : TRC2-financial, Financial PhraseBank
- **Usage** : Analyse de sentiment, news, rapports

### Autres Outils
- **Alphalens** : Factor analysis, performance attribution
- **pyfolio** : Portfolio performance, risk, tearsheet
- **empyrical** : Risk metrics, ratios (Sharpe, Sortino, etc.)
- **QuantLib** : Pricing, Greeks, yield curves
- **TA-Lib** : Technical indicators, pattern recognition
- **Prophet** (Meta) : Time series forecasting

---

## 7. Catégories et TIERS

### Par Tiers de Coût

| Tiers | Coût | Plateformes |
|-------|------|-------------|
| TIER 1 | $15k-25k/an | Bloomberg, Eikon, FactSet, CapIQ, S&P Global |
| TIER 2 | $0-500/mois | Alpaca, IBKR, Polygon Pro, Intrinio, Binance API |
| TIER 3 | Gratuit | FRED, Yahoo Finance, Alpha Vantage, CoinGecko, Dune (base) |
| Open-Source | Gratuit | Backtrader, Zipline, VectorBT, FreqTrade, FinRL, FinGPT |

### Par Type de Données

| Type | Sources |
|------|---------|
| Marchés Traditionnels | Bloomberg, Eikon, Yahoo Finance, Polygon, IBKR |
| Crypto On-Chain | Dune, Nansen, Glassnode, The Graph |
| Crypto Prix | CoinGecko, CoinMarketCap, Binance API |
| DeFi | DeFiLlama, DexScreener, Dune, The Graph |
| Macroéconomiques | FRED, Alpha Vantage, Quandl |
| Fondamentales | CapIQ, FactSet, Intrinio, SEC EDGAR |
| Données Alternatives | Intrinio, Quandl, Earnings Transcripts |

---

## 8. Workflow de Recherche Quantitative

### Pipeline Type
1. **Data Acquisition** : Polygon/IBKR (market) + FRED (macro) + Dune (on-chain)
2. **Feature Engineering** : TA-Lib, Pandas, custom indicators
3. **Backtesting** : VectorBT (screening) → Backtrader/Zipline (validation)
4. **ML** : FinRL (RL) ou FinGPT (NLP) ou custom PyTorch
5. **Risk Management** : pyfolio, empyrical, QuantLib
6. **Execution** : IBKR (tradFi) ou Binance (crypto)
7. **Monitoring** : W&B, Grafana, custom dashboard

### Exemple de Stack
```python
# Stack type pour un bot de trading crypto
import ccxt          # Exchange API abstract
import pandas_ta     # Technical indicators
from backtesting import Backtest, Strategy  # Backtesting
from freqtrade import FreqTrade  # Live trading
from duneanalytics import DuneAnalytics  # On-chain data
```

---

## Ressources

- [Alpaca API Docs](https://docs.alpaca.markets)
- [IBKR API Docs](https://www.interactivebrokers.com/api/doc)
- [FRED API](https://fred.stlouisfed.org/docs/api)
- [Dune Analytics](https://dune.com/docs)
- [FinRL GitHub](https://github.com/AI4Finance-Foundation/FinRL)
- [QuantConnect LEAN](https://www.quantconnect.com/docs)
- [VectorBT](https://vectorbt.dev)
- [CCXT](https://docs.ccxt.com)

## Fichiers Liés

- `references/automated-market-monitoring.md` — Guide pour créer des cron jobs de monitoring de portefeuille avec yfinance (pattern Trade Republic)