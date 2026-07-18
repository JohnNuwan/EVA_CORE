---
name: business-financial-analytics
description: "Compétence niveau expert en analyse d'affaires et financière computationnelle. Couvre l'analyse financière fondamentale, le financial modeling, le valuation (DCF, comparables, LBO), le forecasting financier, l'analyse de rentabilité, l'analyse de scénarios, la modélisation de risques, l'audit analytics, la comptabilité IA, la détection de fraude comptable, le forensic accounting, et le reporting financier intelligent."
---

# Analyse d'Affaires et Financière Computationnelle

## Présentation

Compétence niveau expert en analyse financière computationnelle couvrant le financial modeling, la valorisation, l'audit analytics, la détection de fraude, la comptabilité assistée par IA, le forecasting, et la gestion des risques financiers.

---

## 1. Financial Modeling et Valuation

### Méthodes de Valorisation

- **DCF (Discounted Cash Flow)** : actualisation des flux de trésorerie libres — WACC, terminal value, growth rate
- **Trading Comps** : valorisation relative par multiples boursiers (EV/EBITDA, P/E, P/S, P/B)
- **Transaction Comps** : multiples de transactions comparables (premium de contrôle, synergies)
- **LBO (Leveraged Buyout)** : modélisation d'acquisition à effet de levier — IRR, MOIC, debt schedule
- **Sum-of-the-Parts** : valorisation par somme des parties (conglomérats)
- **NAV (Net Asset Value)** : valorisation d'actifs nets (immobilier, fonds)
- **Monte Carlo Simulation Financière** : simulation stochastique des valorisations
- **Sensitivity Analysis** : analyse de sensibilité — tornado charts, data tables
- **Scenario Manager** : scénarios best case / base case / worst case
- **3-Statement Model** : modèle intégré bilan / compte de résultat / cash flow

### Métriques Clés

- WACC, CAPM, Beta, Risk-Free Rate, Equity Risk Premium
- NOPAT, EBITDA ajusté, UFCF, LFCF
- ROIC, ROE, ROCE

---

## 2. Audit Analytics

### Audit Computationnel

- **Audit Sampling** : échantillonnage statistique pour tests de substance
- **Data Analytics** : analyse complète de populations (100% testing possible)
- **Journal Entry Testing** : détection d'écritures comptables anormales
- **Anomaly Detection** : isolation forest, autoencoders, Z-score, IQR sur données comptables
- **Benford's Law ML** : détection de manipulation via distribution de premier chiffre
- **Continuous Auditing** : audit en continu automatisé
- **Audit Intelligence** : recommandations et insights générés par IA

### Procédures

- Test of controls vs substantive procedures
- Materiality calculation et performance materiality
- Audit risk model : Inherent Risk × Control Risk × Detection Risk

---

## 3. Fraude et Forensic Accounting

### Détection de Fraude

- **Fraud Detection ML** : modèles supervisés (Random Forest, XGBoost) et non supervisés (autoencoders)
- **Benford Analysis** : test de conformité à la loi de Benford par premier, deuxième chiffre
- **Related Party Transactions** : détection de transactions avec parties liées
- **Revenue Recognition** : indicateurs de reconnaissance prématurée de revenus
- **Expense Manipulation** : anomalies dans les dépenses, capitalisations abusives
- **Asset Misappropriation** : détournement d'actifs — inventory shrinkage, ghost employees
- **Forensic Data Analytics** : investigation numérique et data mining forensique
- **Text analytics** : analyse de notes financières pour langage frauduleux

### Schémas de Fraude

- Triangle de la fraude (Pressure, Opportunity, Rationalization)
- Financial statement fraud (falsification de comptes)
- Corruption (kickbacks, conflits d'intérêt)

---

## 4. Comptabilité IA

### Automatisation Comptable

- **GL Coding** : classification automatique des écritures dans le grand livre
- **Invoice Classification** : catégorisation intelligente des factures
- **Account Reconciliation ML** : rapprochement bancaire et inter-comptes automatisé
- **Intercompany Matching** : matching des transactions inter-sociétés
- **Close Optimization** : optimisation du processus de clôture comptable
- **RPA Accounting** : robotic process automation pour tâches répétitives

### Applications

- OCR intelligent pour documents comptables
- 3-way matching (PO, GR, Invoice)
- Automated accruals and deferrals

---

## 5. Forecasting et Planification

### FP&A (Financial Planning & Analysis)

- **Financial Planning** : budget annuel et plan à moyen terme
- **Rolling Forecast** : prévisions glissantes mises à jour mensuellement
- **Driver-Based Planning** : planification pilotée par inducteurs opérationnels
- **What-if Analysis** : analyse de scénarios conditionnels
- **Capital Budgeting** : budgétisation d'investissements — NPV, IRR, payback, MIRR
- **Cash Flow Forecasting ML** : prévision de trésorerie par séries temporelles et ML
- **Tax Planning** : optimisation fiscale prévisionnelle

### Techniques

- Time series forecasting : ARIMA, Prophet, LSTM
- Régression drivers-based
- Sensibilité multi-variables

---

## 6. Risk Management Financier

### Scoring et Prédiction

- **Credit Risk Scoring** : score de crédit entreprise / particulier — logit, XGBoost, réseaux
- **Bankruptcy Prediction** : faillite d'entreprise — Altman Z-score, Ohlson O-score, ML
- **Covenant Monitoring** : suivi des covenants bancaires
- **Liquidity Risk** : risque de liquidité — gap analysis, stress testing
- **Counterparty Risk** : risque de contrepartie — CVA, DVA

### Modèles de Risque

- **Altman Z-Score** : Z = 1.2A + 1.4B + 3.3C + 0.6D + 1.0E (entreprises publiques)
- **Ohlson O-Score** : modèle logit de prédiction de faillite à 9 variables
- **Merton Model** : distance-to-default basé sur options

---

## 7. Références

### Catégories

- `q-fin.GN` — General Finance
- `q-fin.CP` — Computational Finance
- `q-fin.RM` — Risk Management
- `cs.LG` — Machine Learning
- `stat.AP` — Statistics (Applied)
- `cs.AI` — Artificial Intelligence