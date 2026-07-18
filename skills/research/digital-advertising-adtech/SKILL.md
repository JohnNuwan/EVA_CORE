---
name: digital-advertising-adtech
description: "Compétence niveau expert en publicité numérique et adtech computationnelles. Couvre le programmatic advertising, DSP/SSP/AdExchanges, RTB, header bidding, audience targeting ML, creative optimization, attribution, fraud detection ad, brand safety, identity resolution, contextual targeting, CTV advertising, retail media, et GDPR compliance."
---

# Publicité Numérique et AdTech Computationnelle

## Présentation

Compétence niveau expert en publicité numérique et technologies publicitaires couvrant l'écosystème programmatique, le ciblage d'audience, l'optimisation créative, les enchères programmatiques, l'attribution, la fraude publicitaire, la privacy, et la conformité réglementaire.

---

## 1. Écosystème AdTech

### Acteurs et Plateformes

- **DSP (Demand-Side Platforms)** :
  - The Trade Desk (TTD) : leader indépendant du programmatique
  - DV360 (Display & Video 360) : Google Marketing Platform
  - Amazon Ads : DSP intégré à l'écosystème Amazon
  - Xandr (Microsoft) : plateforme programmatique premium
- **SSP (Supply-Side Platforms)** :
  - Magnite (anciennement Rubicon Project + Telaria)
  - PubMatic : SSP indépendant
  - Index Exchange
- **Ad Exchanges** : marchés programmatiques (AdX Google, Xandr Exchange, Magnite)
- **RTB (Real-Time Bidding)** : enchères en temps réel — protocole **OpenRTB 2.6**
- **Header Bidding** : enchères simultanées via **Prebid.js**
- **Ad Servers** : Google Campaign Manager, Sizmek, AdForm
- **Ad Networks** : Google AdSense, Meta Audience Network
- **Supply Path Optimization** : optimisation du chemin d'approvisionnement

### Protocole OpenRTB

- **Bid Request / Bid Response** : structure standardisée d'enchères
- **Bid Object, Imp Object, Device Object, User Object, Site/App Object**
- **Deals** : offres programmatiques garanties (PMP, Preferred Deals)

---

## 2. Audience Targeting

### Données et Plateformes

- **First-Party Data** : données propriétaires (CRM, site, app)
- **Second-Party Data** : données de partenaires (data partnerships)
- **Third-Party Data** : données externes agrégées (DMPs, data brokers)
- **DMP (Data Management Platform)** : gestion et segmentation des audiences
- **CDP (Customer Data Platform)** : plateforme de données client unifiée

### Modélisation

- **Lookalike Modeling** : extension d'audience par similarité ML
- **Propensity Modeling** : scoring de propension à l'achat
- **Segmentation ML** : clustering d'audience (RFM, comportemental, démographique)
- **Predictive Audiences** : audiences prédictives basées sur ML
- **Identity Graphs** : graphes d'identité probabilistes et déterministes
- **Probabilistic Matching** : appariement par similarité de comportements
- **Deterministic Matching** : appariement par identifiants uniques (email, login)

---

## 3. Creative Optimization

### Optimisation Créative

- **DCO (Dynamic Creative Optimization)** : créations dynamiques personnalisées
- **Ad Personalization** : personnalisation des messages publicitaires
- **Creative Scoring** : score de performance créative par ML
- **A/B Testing** : tests de créations (variantes contrôlées)
- **Multivariate Testing** : tests multi-variantes d'éléments créatifs

### Génération par IA

- **Generative Ad Creative** : création publicitaire par DALL-E, Stable Diffusion, Midjourney
- **Copy Personalization** : copywriting personnalisé par LLM
- **Video Creative** : génération de vidéos publicitaires

---

## 4. Programmatic et Auction

### Mécanismes d'Enchères

- **First-Price Auction** : l'annonceur paie son propre prix
- **Second-Price Auction** : (historique) l'annonceur paie le second prix
- **Floor Price Optimization** : optimisation du prix de réserve
- **Bid Shading** : réduction stratégique des enchères en first-price
- **Bid Optimization** : optimisation du montant d'enchère

### Gestion de Campagne

- **Budget Pacing** : répartition optimale du budget dans le temps
- **Frequency Capping ML** : limitation de fréquence optimisée par ML
- **RTB Fraud Detection** : détection de fraude dans les enchères temps réel

---

## 5. Attribution et Measurement

### Modèles d'Attribution

- **Multi-Touch Attribution (MTA)** : attribution multi-canal avec ML
  - Shapley Value, Markov Chains, Data-Driven Attribution
- **Marketing Mix Modeling (MMM)** : modélisation économétrique des médias
  - Régression, Bayesian structural time series, Robyn (Meta)
- **Incremental Lift** : mesure de l'incrémentalité par expérimentation
- **Geo Experimentation** : expériences géographiques contrôlées
- **Brand Lift** : mesure d'impact sur la notoriété et perception de marque

### Métriques

- **Viewability** : visibilité des impressions (MRC standard : 50% pixels, 1s display / 2s video)
- **IVT Detection** : invalid traffic — GIVT (crawlers) et SIVT (bots sophistiqués)
- **Attribution Windows** : fenêtres d'attribution (view-through, click-through)

---

## 6. Privacy et Compliance

### Post-Cookie

- **Cookie Deprecation** : dépréciation des cookies tiers (Chrome 2024-2025)
- **Google Privacy Sandbox** :
  - **Topics API** : ciblage par centres d'intérêt préservant la vie privée
  - **FLEDGE** : remarketing et audiences personnalisées sans cookie
- **Identity Resolution sans Cookie** : UID2 (Trade Desk), RampID (LiveRamp), ID5
- **Contextual Targeting Post-Cookie** : ciblage contextuel avancé (NLP, CV)

### Réglementation

- **GDPR** : Règlement Général sur la Protection des Données
- **TCF (Transparency & Consent Framework)** : cadre de consentement IAB
- **Cookie Consent Management** : gestion des consentements cookies
- **CCPA** : California Consumer Privacy Act
- **COPPA** : protection des enfants en ligne

---

## 7. Catégories

- `cs.LG` — Machine Learning
- `cs.AI` — Artificial Intelligence
- `cs.IR` — Information Retrieval
- `q-fin.PM` — Portfolio Management
- `cs.CY` — Computers and Society
- `econ.GN` — General Economics