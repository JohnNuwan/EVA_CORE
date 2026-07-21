---
name: analytics-marketing
description: Analytics Marketing — mesure, analyse et optimisation des performances marketing via GA4, Mixpanel, attribution, cohortes, funnel et tableaux de bord
category: business
---

# Analytics Marketing

Compétence de niveau expert en analyse marketing — mesure de la performance, attribution, segmentation, analyse de cohortes, modélisation prédictive et data storytelling.

## 1. Fondamentaux de la Mesure Marketing

### Cadres de Mesure
- **Modèle AIDA** : Attention → Interest → Desire → Action
- **Modèle RACE** : Reach → Act → Convert → Engage
- **Pirate Metrics (AARRR)** : Acquisition → Activation → Retention → Revenue → Referral
- **Modèle MMM (Media Mix Modeling)** : Analyse macro des canaux publicitaires agrégés
- **Attribution multi-touch** : Comprendre la contribution de chaque touchpoint dans le parcours

### Frameworks de KPIs
- **HEART Framework** (Google) : Happiness, Engagement, Adoption, Retention, Task success
- **PULSE** : Page views, Uptime, Latency, Seven-day active users, Earnings
- **GSM** : Goals → Signals → Metrics (Design Thinking)
- **OKRs** : Objectives and Key Results alignés marketing/business
- **Balanced Scorecard** : Financier, Client, Processus internes, Apprentissage

## 2. Google Analytics 4 (GA4)

### Architecture GA4
- **Events** : `page_view`, `scroll`, `click`, `purchase` — événements riches avec paramètres
- **Dimensions & Metrics** : Dimensions personnalisées, métriques calculées
- **Users** : Identifiants utilisateur (User-ID), Google Signals (données cross-device)
- **Properties** : Propriétés GA4, sous-propriétés, roll-up properties (GA4 360)
- **BigQuery Export** : Export brut des événements vers BigQuery pour analyses avancées

### Rapports Essentiels
- **Acquisition** : Trafic organique, payant, social, direct, referral, email
- **Engagement** : Pages vues, temps moyen, engagement rate, événements
- **Monétisation** : Achats, revenus, objets consultés, LTV prédictive
- **Rétention** : Rétention J1, J7, J30, retour des utilisateurs
- **E-commerce** : Entonnoir d'achat (view item → add to cart → checkout → purchase), revenu par article
- **Explorations** : Rapports ad-hoc (funnel, segment overlap, cohort, path, user lifetime)

### Configuration Avancée
- **Enhanced Measurement** : Scrolls, outbound clicks, site search, video engagement, file downloads
- **Conversions** : Marquer des événements comme conversions (purchase, sign_up, lead, submit_form)
- **Audiences** : Segments utilisateurs exportables vers Google Ads (remarketing)
- **Custom Events & Parameters** : Événements métier spécifiques avec paramètres personnalisés
- **DebugView** : Tester les événements en temps réel

### Intégrations
- **Google Ads** : Import de conversions, remarketing, bid adjustments
- **Google Search Console** : Requêtes, impressions, clics, position
- **BigQuery** : SQL brut, jointures avec données CRM, modèles ML
- **Google Optimize** (fin mars 2024) : Google Optimize disparu — alternatives : AB Tasty, VWO, Optimizely

## 3. Analyse d'Attribution

### Modèles d'Attribution
- **First Touch** : 100% du crédit au premier point de contact
- **Last Touch** : 100% au dernier point de contact avant conversion (modèle par défaut GA4)
- **Last Non-Direct Click** : Ignore les visites directes, crédite le dernier canal non direct
- **Linear** : Distribution égale entre tous les touchpoints
- **Time Decay** : Plus de poids aux interactions récentes (attribution temporelle)
- **Position Based (U-Shaped)** : 40% first, 40% last, 20% middle
- **Data Driven** : Modèle algorithmique de Google (apprentissage automatique)

### Analyse Multi-Canal
- **Cross-channel paths** : Parcours utilisateur multi-canal (ex: Email → Organic → Social → Paid Search)
- **Assisted conversions** : Conversions assistées par un canal sans être le dernier
- **Conversion paths** : Rapport GA4 > Advertising > Conversion Paths
- **Time lag** : Temps entre le premier touchpoint et la conversion
- **Attribution gaps** : Canaux non trackés (hors ligne, dark social, messageries)

### Outils d'Attribution
- **GA4 Model Comparison Tool** : Comparer les modèles d'attribution
- **Google Ads Attribution** : Modèles d'attribution pour les campagnes Ads
- **Mixpanel / Amplitude** : Attribution comportementale
- **Rockerbox / Northbeam / Triple Whale** : Attribution multi-touch avancée
- **MMM** : Media Mix Modeling (Meta Robyn, Google Lightweight MMM, Recast)

## 4. Analyse de Cohorte et Funnel

### Cohorte Analysis
- **Time cohorts** : Utilisateurs groupés par date d'acquisition (semaine, mois)
- **Behaviour cohorts** : Utilisateurs groupés par action (sign_up, first_purchase)
- **Size cohorts** : Taille de la cohorte, rétention absolue et relative
- **Rétention curve** : % d'utilisateurs revenant à J1, J7, J30, J90
- **Revenue cohorts** : ARPU par cohorte, LTV cumulé

### Funnel Analysis
- **Entonnoir de conversion** : Étapes du parcours client (visite → inscription → activation → achat)
- **Drop-off points** : Où les utilisateurs abandonnent — optimiser les étapes faibles
- **Abandonment rate** : Taux d'abandon entre chaque étape
- **Step-by-step analysis** : Comparaison des taux de passage d'une étape à l'autre
- **Funnel segmentation** : Comparer des segments (mobile vs desktop, payant vs organique)

### Path Analysis
- **User flow** : Chemins les plus fréquents dans le site/app
- **Sankey diagram** : Visualisation des flux entre pages/actions
- **Most common paths** : Chemins les plus courants vers la conversion
- **Drop-off before conversion** : Dernière page/action avant l'abandon
- **Loop counter** : Cycles dans les parcours (retour à une étape antérieure)

## 5. Segmentation Client

### Approches
- **Démographique** : Âge, sexe, revenu, localisation, éducation
- **Comportementale** : Fréquence d'achat, type de produit, engagement, canal préféré
- **Psychographique** : Personnalité, valeurs, style de vie, intérêts
- **Firmographique (B2B)** : Taille entreprise, secteur, chiffre d'affaires, décideur
- **Lifecycle stage** : Prospect, lead, MQL, SQL, client actif, client perdu
- **RFM** : Récence, Fréquence, Montant — segment par valeur client

### Analyse de Segments
- **Segment comparison** : Comparer KPIs entre segments (taux de conversion, AOV, rétention)
- **Segment overlap** : Chevauchement de segments, hiérarchie
- **Lookalike / Similar segments** : Audiences similaires pour acquisition (Facebook, Google)
- **Segment profitability** : Marge par segment, CAC, LTV
- **Personalization** : Contenu, offre, canal adapté à chaque segment

## 6. Tableaux de Bord et Data Storytelling

### Conception de Dashboard
- **Principes de Tufte** : Data-ink ratio, chartjunk, small multiples
- **Hiérarchie visuelle** : KPIs en haut, détails en bas
- **Couleurs** : Palette limitée, utilisation sémantique (vert = bon, rouge = mauvais)
- **Interactivité** : Filtres, drill-down, date picker (Looker Studio, Metabase, Tableau)
- **Performance** : Temps de chargement < 3s, agrégation par jour/semaine/mois

### Outils de Dashboard
- **Google Looker Studio** : Gratuit, connecteurs Google (GA4, Ads, GSC, Sheets)
- **Tableau / Power BI** : Entreprise, SQL, connecteurs multiples
- **Metabase / Superset** : Open source, SQL-based
- **Mixpanel / Amplitude** : SaaS analytics avec dashboards natifs
- **Custom dashboards** : React + D3.js, Grafana, Plotly Dash

### Data Storytelling
- **Narrative structure** : Contexte → Problème → Analyse → Recommandation → Impact
- **Visualisation** : Choisir le bon chart (barres pour comparaison, lignes pour tendances, scatter pour corrélation)
- **Annotations** : Marquer les événements clés (campagnes, changements produit)
- **Key takeaway** : Un seul message principal par slide
- **Call to action** : Recommandation claire et chiffrée

## 7. Modélisation Avancée

### Marketing Mix Modeling (MMM)
- **Objectif** : Mesurer l'impact de chaque canal publicitaire sur les ventes à un niveau agrégé
- **Variables** : Dépenses pub (TV, radio, print, digital), saisonnalité, économie
- **Modèle** : Régression linéaire, Bayesian MMM (Robyn de Meta, Lightweight MMM de Google)
- **Output** : ROI par canal, saturation curves, elasticité
- **Limites** : Données agrégées, pas d'attribution individuelle, besoin de 2-3 ans de données

### Customer Lifetime Value (LTV)
- **Méthode simple** : ARPU × Durée de vie moyenne
- **Méthode cohorte** : Revenue cumulé par cohorte à T+N mois
- **Méthode prédictive** : Modèle ML (RFM, régression, survie, BG/NBD, Gamma-Gamma)
- **Segmentation LTV** : High value vs low value, stratégies différenciées
- **Incremental LTV** : LTV incrémental dû au marketing vs croissance organique

### Churn Prediction
- **Features** : Fréquence d'utilisation, support tickets, NPS, temps depuis dernière action, pagination
- **Modèles** : Régression logistique, Random Forest, XGBoost, Survival Analysis
- **Métriques** : AUC-ROC, Precision-Recall, F1-score, lift
- **Intervention** : Campagne de rétention ciblée, offres personnalisées
- **Early warning** : Détection précoce des signaux de churn

## 8. Pièges et Bonnes Pratiques

- **Vanity metrics** : Ne pas confondre volume (pages vues) avec valeur (conversions)
- **Corrélation ≠ Causalité** : Valider avec A/B tests, causal inference
- **Tracking gaps** : Checker les événements manquants, doublons, fuites de données
- **Données non nettoyées** : Bots, spam, trafic invalide — filtrer avec GA4 + IP exclusions
- **Sampling** : GA4 standard = pas de sampling, GA4 360 = sampling possible sur gros volumes
- **Time zone** : Cohérence des fuseaux horaires entre sources de données
- **Cohorte trop petite** : Minimum 100 utilisateurs par cohorte pour significativité
- **Surveiller les changements** : Mises à jour GA4, nouvelles régulations RGPD, évolution des cookies tiers
