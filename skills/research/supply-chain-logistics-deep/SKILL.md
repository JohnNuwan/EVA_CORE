---
name: supply-chain-logistics-deep
description: "Compétence niveau expert avancé en supply chain et logistique IA. Couvre demand forecasting ML, inventory optimization, network design, supplier risk, procurement AI, logistics optimization, warehouse automation, last-mile, reverse logistics, cold chain, blockchain supply chain, resilience, circular supply chain, et sustainable SCM."
keywords: [supply chain, logistics, demand forecasting, inventory optimization, procurement AI, warehouse automation, SCM]
categories: [math.OC, cs.AI, cs.LG, cs.RO, cs.MA, cs.DS]
---

# Compétence Supply Chain et Logistique

## Présentation

Cette compétence couvre l'ensemble des disciplines de la supply chain et logistique assistées par l'intelligence artificielle, de la prévision de la demande à l'optimisation des transports, en passant par la gestion des stocks et l'automatisation des entrepôts.

---

## Demand Forecasting

- **Time Series ML** : Modèles de séries temporelles (ARIMA, Prophet, LSTM, Transformers)
- **Causal Forecasting** : Prévision causale intégrant des variables exogènes (PIB, météo, promotions)
- **Promotion Planning** : Modélisation de l'impact des promotions sur la demande
- **New Product Forecasting** : Prévision pour nouveaux produits sans historique (look-alike, Bayesian)
- **Intermittent Demand (Croston)** : Méthode de Croston pour la demande intermittente et sporadique
- **Hierarchical Forecasting** : Prévision hiérarchique (SKU → catégorie → région → global)
- **Reconciliation** : Réconciliation des prévisions entre niveaux hiérarchiques
- **ML Ensembles** : Ensembles de modèles pour la robustesse des prévisions
- **Transformers Temporels** : Informer, Autoformer, PatchTST, TimesNet pour séries longues

## Inventory Optimization

- **Safety Stock** : Calcul du stock de sécurité basé sur la variabilité et le service level
- **Service Level Optimization** : Optimisation du taux de service par SKU
- **ROP (Reorder Point)** : Point de commande optimal
- **EOQ (Economic Order Quantity)** : Quantité économique de commande
- **Multi-Echelon Inventory Optimization (MEIO)** : Optimisation multi-échelon des stocks
- **DRP (Distribution Requirements Planning)** : Planification des besoins de distribution
- **VMI (Vendor Managed Inventory)** : Stock géré par le fournisseur
- **Inventory Turnover** : Rotation des stocks par catégorie
- **Days of Supply (DOS)** : Jours d'approvisionnement
- **ABC/XYZ Analysis ML** : Segmentation automatique des SKUs par valeur et volatilité
- **Slow Mover Detection** : Détection des articles à rotation lente via clustering ML

## Network Design

- **Facility Location** : Localisation optimale des entrepôts et centres de distribution
- **Supply Chain Network Optimization** : Optimisation du réseau logistique global
- **Greenfield Analysis** : Analyse greenfield pour la conception d'un réseau optimal
- **DC Footprint** : Empreinte des centres de distribution
- **Flow Optimization** : Optimisation des flux entre nœuds du réseau
- **Transportation Mode Selection** : Sélection du mode de transport optimal (air, mer, rail, route)
- **Nearshoring/Reshoring** : Analyse de rapprochement des sources d'approvisionnement
- **Multi-Echelon Network** : Conception de réseaux multi-échelons

## Procurement et Supplier

- **Supplier Risk Assessment** : Évaluation des risques fournisseurs (financier, géopolitique, ESG)
- **Spend Analytics** : Analyse des dépenses par catégorie, fournisseur, département
- **Category Management** : Gestion stratégique des catégories d'achat
- **Strategic Sourcing** : Sourcing stratégique (RFx, e-auctions, négociation)
- **Procurement Automation** : Automatisation des achats (PO, invoicing, matching)
- **Contract Analysis NLP** : Analyse de contrats fournisseurs par NLP
- **Supplier Diversity** : Diversité des fournisseurs et inclusion
- **Sustainability Scoring** : Scoring ESG des fournisseurs

## Warehousing

- **WMS (Warehouse Management System)** : Systèmes de gestion d'entrepôt
- **Slotting Optimization** : Optimisation de l'emplacement des articles
- **Putaway/Picking Path Optimization** : Optimisation des chemins de rangement et de prélèvement
- **Wave Planning** : Planification des vagues de picking
- **Labor Management** : Gestion de la main-d'œuvre entrepôt
- **Robotics** : Robots d'entrepôt (Locus, 6 River Systems, GreyOrange)
- **AS/RS (Automated Storage & Retrieval System)** : Systèmes automatisés de stockage/déstockage
- **AGV/AMR** : Véhicules/robots mobiles autonomes
- **Automated Picking** : Prélèvement automatisé (piece picking, case picking)
- **Voice Picking** : Prélèvement vocal
- **Goods-to-Person (G2P)** : Systèmes de type « marchandise vers l'opérateur »

## Logistics et Transport

- **TMS (Transportation Management System)** : Systèmes de gestion du transport
- **Route Optimization** : Optimisation de tournées (VRP, capacitated VRP)
- **Carrier Selection** : Sélection du transporteur optimal
- **Freight Audit** : Audit et validation des factures de fret
- **Dock Scheduling** : Ordonnancement des quais de chargement/déchargement
- **Intermodal/Multimodal** : Transport intermodal et multimodal
- **Parcel Shipping** : Expédition de colis (carrier negotiation, zone skipping)
- **LTL/FTL** : Less-than-truckload vs Full-truckload
- **Freight Rate Prediction** : Prédiction des taux de fret par ML
- **Fuel Optimization** : Optimisation de la consommation de carburant
- **Driver Retention** : Rétention des chauffeurs (analytics prédictifs)
- **Hours of Service (HOS)** : Conformité aux heures de service des chauffeurs
