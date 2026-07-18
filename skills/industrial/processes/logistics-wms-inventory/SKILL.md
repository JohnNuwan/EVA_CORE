---
name: logistics-wms-inventory
description: "Gérer et optimiser l'intralogistique d'entrepôt, intégrer les systèmes de gestion d'entrepôt (WMS / WES), structurer les stocks par analyse ABC et FIFO, concevoir les flux de picking efficaces, et implémenter la traçabilité automatique RFID/code-barres avec interfaçage ERP."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [logistics, wms, wes, inventory-management, picking, fifo, lifo, abc-analysis, rfid, barcode, supply-chain, warehouse-optimization, intralogistics, erp-integration]
  EVA:
    related_skills: [supply-chain-planning-erp, agv-amr-fleet-management, oee-performance]
    difficulty: intermediate
    industry_sectors: [manufacturing, distribution, ecommerce, automotive, pharmaceutical, food-beverage, retail]
---

# Intralogistique, WMS et Gestion des Stocks Industriels

## Vue d'ensemble

Cette compétence guide la conception, l'organisation, l'optimisation et l'automatisation des flux logistiques internes au sein d'une usine ou d'un centre de distribution. Elle couvre l'intégration des systèmes de gestion d'entrepôt (**WMS - Warehouse Management System**), la structuration des stocks par criticité ou rotation (méthodes **ABC**, règles **FIFO / LIFO**), l'optimisation des parcours de préparation de commandes (**Picking**), et le déploiement de technologies d'identification et de traçabilité automatique (codes-barres, codes 2D / DataMatrix, étiquettes **RFID**).

### Contexte Industriel

La performance logistique est un facteur clé de compétitivité :

- Le **coût logistique** représente en moyenne 8 à 12 % du chiffre d'affaires des entreprises industrielles (source : étude ASLOG / PwC).
- Les **erreurs de picking** (mauvaise référence, mauvaise quantité) génèrent des retours clients coûteux (de 15 à 50 € par erreur) et dégradent la satisfaction.
- Les **ruptures de stock** sur les lignes de production peuvent entraîner des arrêts de fabrication coûtant plusieurs milliers d'euros par heure.

Un WMS performant permet de :
- Réduire les stocks de 15 à 30 % grâce à une meilleure visibilité.
- Augmenter la productivité du picking de 20 à 40 %.
- Réduire les erreurs d'expédition à moins de 0,1 %.
- Garantir la traçabilité complète des lots (obligatoire en agroalimentaire, pharmacie, automobile).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Définir des **stratégies d'emplacement de stockage** (ex : stocker les références à forte rotation près des quais d'expédition, zone à température contrôlée pour les produits sensibles).
- Structurer ou analyser un **processus de préparation de commande** (Batch Picking, Zone Picking, Pick-and-Pack, Wave Picking).
- Modéliser ou concevoir l'**intégration de données** entre un WMS, un ERP (SAP S/4HANA WM/EWM, Microsoft Dynamics 365) et un système de convoyage automatisé.
- Sélectionner ou implémenter une **technologie de traçabilité automatique** (RFID UHF passive/active, scanner de codes-barres, caméras de lecture).
- Optimiser le **dimensionnement d'un stock** de matières premières ou de produits finis (calcul du point de commande, stock de sécurité, stock d'alerte).
- Réaliser un **audit logistique** d'entrepôt : taux de service, taux de rotation, taux de remplissage.

**Ne pas utiliser pour :**
- La gestion des flux de production internes (Kanban, flux tirés) qui relève de la compétence `lean-manufacturing-vsm`.
- La planification des transports et des tournées de livraison.

## Outils et Méthodes d'Optimisation des Stocks

### 1. Analyse ABC (Loi de Pareto)

Permet de classer le stock en 3 catégories en fonction de la valeur de consommation annuelle ou de la fréquence de rotation (méthode du taux de rotation ou de la valeur de consommation) :

| Classe | % des articles | % des mouvements / valeur | Stratégie de stockage |
|:---:|:---:|:---:|:---|
| **A** | ~ 10 – 20 % | ~ 70 – 80 % | Zone la plus accessible : niveau du sol, près des quais. Inventaire tournant fréquent (cycle counting). |
| **B** | ~ 20 – 30 % | ~ 15 – 20 % | Zones intermédiaires. Inventaire périodique (mensuel). |
| **C** | ~ 50 – 70 % | ~ 5 – 10 % | Zones les plus éloignées, hauteurs de rack. Réapprovisionnement par lots. |

**Calcul du point de commande ($S$)** :
$$S = D_{moy} \times L + SS$$

Où :
- $D_{moy}$ : Demande moyenne par unité de temps.
- $L$ : Délai d'approvisionnement (Lead Time).
- $SS$ : Stock de sécurité ($SS = z \times \sigma_{D+L}$ avec $z$ coefficient de service et $\sigma_{D+L}$ écart-type de la demande pendant le délai).

### 2. Règles de Rotation des Stocks

| Règle | Principe | Application typique | Condition requise |
|:---|:---|---|:---:|
| **FIFO** (First-In, First-Out) | Le premier entré est le premier sorti | Produits périssables (agroalimentaire, chimie), pharmaceutiques, composants électroniques avec date de code | Gestion par date de lot / date de réception dans le WMS |
| **FEFO** (First Expired, First Out) | Le premier qui expire est le premier sorti | Produits avec date de péremption critique (médicaments, réactifs) | Traçabilité par date de péremption |
| **LIFO** (Last-In, First-Out) | Le dernier entré est le premier sorti | Produits en vrac non périssables (sable, minerai, granulés plastiques) | Stockage en silo ou en tas |
| **FPFO** (First Produced, First Out) | Le premier fabriqué est le premier sorti | Produits semi-finis avec suivi de lot de fabrication | Gestion par numéro de lot de production |

## Stratégies de Préparation de Commandes (Picking)

| Méthode | Description | Productivité | Précision | Adapté pour |
|:---|---|---|:---:|:---:|---:|
| **Picking par article** | Un préparateur prélève un article pour plusieurs commandes simultanément | Élevée | Moyenne | Petits articles, forte similarité |
| **Batch Picking** | Picking par lots de commandes regroupées | Très élevée | Bonne | E-commerce, distribution |
| **Zone Picking** | Chaque préparateur est affecté à une zone fixe | Élevée | Bonne | Grands entrepôts multi-références |
| **Pick-and-Pack** | Le préparateur prélève et emballe directement | Moyenne | Excellente | Petites commandes, colis standards |
| **Goods-to-Person (GTP)** | Le produit est acheminé vers le préparateur (AS/RS, AGV) | Maximale | Excellente | Haute cadence, forte valeur ajoutée |

### Optimisation des Parcours de Picking

Les algorithmes d'optimisation de tournées (Routing) les plus courants dans les WMS :

| Algorithme | Principe | Gain par rapport à un parcours aléatoire |
|:---|---|:---:|
| **S-Shape (Serpentin)** | Parcours en serpentin dans les allées | 20 – 30 % |
| **Return Routing** | Aller-retour dans chaque allée | 10 – 20 % |
| **Largest Gap** | Pénètre dans l'allée jusqu'au plus grand écart entre deux emplacements | 25 – 35 % |
| **Aisle-by-Aisle** | Parcours allée par allée | 15 – 25 % |
| **Optimal (DP / Heuristique)** | Algorithme de plus court chemin dynamique | 30 – 40 % |

## Traçabilité Automatique : Barcode vs RFID vs Vision

| Technologie | Principe | Portée de lecture | Avantages | Limites |
|:---|---|---|:---:|:---:|
| **Code-barres 1D** | Code linéaire optique | Contact – 30 cm | Très économique, standard mondial | Ligne de visée requise, lecture unitaire |
| **Code 2D / DataMatrix** | Matrice de points optique | 5 – 50 cm | Peut contenir des données (lot, date, n° série), tolérant aux marquages dégradés | Ligne de visée requise |
| **RFID UHF Passive** | Communication radio (860 – 960 MHz) | 0 – 10 m | Lecture multiple simultanée (jusqu'à 200 tags/s), sans visée directe, travers cartons | Coût de l'étiquette (~0,05 – 0,20 €), sensibilité aux métaux/liquides |
| **RFID UHF Active** | Tag avec batterie intégrée | 0 – 100 m | Longue portée, localisation temps réel (RTLS) | Coût élevé (> 10 € par tag), maintenance batterie |
| **Vision industrielle (OCR / Deep Learning)** | Caméra + IA | 20 – 50 cm | Peut lire tout type de marquage, vérification qualitative | Coût matériel, complexité d'intégration |

### Règle de déploiement RFID en entrepôt

Pour un inventaire automatisé de palettes au passage des portes (Dock Door Portal) :

1. Prévoir une **porte RFID** avec antennes latérales et plafond pour couvrir toute la section de passage.
2. Utiliser des **tags RFID UHF passifs** (norme ISO 18000-6C / EPC Global Class 1 Gen 2) montés sur les palettes ou les contenants.
3. Le WMS doit pouvoir associer le **EPC** (Electronic Product Code) du tag au **numéro de palette** et à la **référence article**.
4. Taux de lecture attendu : > 99,5 % dans des conditions normales (palettes standards, carton sec).

## Architecture d'Intégration WMS / ERP

```text
                       ┌──────────────┐
                       │    ERP       │
                       │ (SAP, D365,  │
                       │  JD Edwards) │
                       └──────┬───────┘
                              │ IDoc / API / XML
                       ┌──────┴───────┐
                       │    WMS       │
                       │ (Manhattan,   │
                       │  Blue Yonder, │
                       │  Hardis, SAP  │
                       │  EWM)         │
                       └──────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌──────┴──────┐   ┌───────┴──────┐   ┌────────┴────────┐
   │ Terminaux   │   │ Convoyage /  │   │ RFID / Codes-   │
   │ RF (scanners)│  │ AGV / AS/RS  │   │ barres / Voice  │
   └─────────────┘   └──────────────┘   └─────────────────┘
```

**Messages de transaction standards (ERP → WMS) :**
- Commande d'achat (réception fournisseur anticipée).
- Ordre de fabrication (OF) généré par le MES/ERP.
- Commande client (préparation et expédition).
- Transfert de stock inter-entrepôts.

**Messages de transaction standards (WMS → ERP) :**
- Confirmation de réception fournisseur (GR) avec numéro de lot.
- Confirmation de préparation / expédition client (GI/GE).
- Ajustements de stock suite à inventaire.
- Mouvements de transfert inter-emplacements.

## Pièges Courants (Common Pitfalls)

1. **Désynchronisation physique et informatique du WMS :**
   - *Erreur :* Déplacer manuellement une palette de produits d'un emplacement A à un emplacement B dans l'entrepôt pour faire de la place, sans enregistrer ce mouvement sur le terminal du WMS. Le préparateur de commande perdra ensuite du temps à chercher la palette "perdue" informatiquement.
   - *Correction :* Imposer l'utilisation systématique de terminaux mobiles de flashage (scanners portables) pour valider informatiquement chaque mouvement de stock en temps réel (scannage de l'emplacement source, du produit et de l'emplacement cible). Former les caristes et les opérateurs logistiques.

2. **Chemins de picking croisés et inefficaces :**
   - *Erreur :* Laisser les préparateurs de commandes effectuer des allers-retours désordonnés dans les allées parce que la liste de picking n'est pas triée par ordre d'emplacement géographique.
   - *Correction :* Configurer le moteur d'ordonnancement du WMS pour trier les listes de picking selon un parcours optimisé (S-Shape ou Largest Gap) minimisant la distance totale parcourue. Ré-analyser la disposition des emplacements ABC.

3. **Stock de sécurité calculé sans données historiques fiables :**
   - *Erreur :* Fixer un stock de sécurité arbitraire (ex : "deux semaines de consommation") sans analyse de la variabilité de la demande ni des délais de livraison.
   - *Correction :* Utiliser la formule $SS = z \times \sqrt{L \times \sigma_D^2 + D_{moy}^2 \times \sigma_L^2}$ avec $z$ basé sur le niveau de service souhaité (ex : $z = 1,64$ pour 95 % ; $z = 2,33$ pour 99 %).

4. **Multiplicité des bases de données de stock (ERP + WMS + Excel) :**
   - *Erreur :* Disposer de trois sources de vérité (stock ERP, stock WMS et fichier Excel de suivi des inventaires) qui ne sont jamais synchronisées. Les écarts se creusent au fil du temps.
   - *Correction :* Le WMS doit être l'unique source de vérité pour les stocks physiques (principe du "Single Source of Truth"). L'ERP est mis à jour par le WMS via des interfaces en temps réel ou quasi-réel.

## Références

- **Norme ISO 28000** : Systèmes de management de la sûreté pour la chaîne d'approvisionnement.
- **EPC Global / GS1** : Standards de codification RFID et codes-barres.
- **NF EN 62056** : Échange de données pour la comptabilité de l'électricité (modèle de données logistiques).
- **VDA 5004** : Standard pour les messages logistiques dans l'industrie automobile (Allemagne).
- **ODETTE** : Standard logistique pour l'industrie automobile européenne.
- **GS1 General Specifications** : Règles de codification des articles, palettes et expéditions.

## Liste de vérification (Checklist)

- [ ] L'**analyse ABC** des stocks est mise à jour au moins **annuellement** (voire trimestriellement pour les articles à forte rotation) pour réajuster les emplacements de stockage physique.
- [ ] Le **principe de rotation** (FIFO, FEFO, LIFO) est garanti par le WMS via des instructions de prélèvement basées sur les dates de réception / production / péremption.
- [ ] **Chaque emplacement physique** de l'entrepôt possède un étiquetage d'identification unique (code-barres ou tag RFID) lisible par les terminaux.
- [ ] L'**interfaçage WMS / ERP** gère correctement les transactions de mouvement de stock (réception, transfert, expédition, ajustement) en quasi-temps réel.
- [ ] Le **stock de sécurité** est calculé et documenté en intégrant la variabilité de la demande ($\sigma_D$) et les délais de livraison ($\sigma_L$).
- [ ] Les **inventaires tournants** (cycle counting) sont réalisés selon la classification ABC : Classe A tous les mois, B tous les trimestres, C tous les semestres.
- [ ] Les **équipements de manutention** (chariots, AGV, transpalettes) sont compatibles avec les largeurs d'allées et la hauteur de stockage de l'entrepôt.
- [ ] Un **plan de continuité logistique** est défini en cas de panne du WMS (procédure dégradée avec bordereaux papier).
- [ ] Les **indicateurs clés** (taux de service, taux de rotation des stocks, productivité picking, taux d'erreur expédition) sont suivis mensuellement.
- [ ] Les **formations des utilisateurs** sur le terminal WMS et les consignes de sécurité logistique sont à jour.

