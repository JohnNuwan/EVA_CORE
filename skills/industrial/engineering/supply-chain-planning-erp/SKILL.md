---
name: supply-chain-planning-erp
description: "Planifier la production via le calcul des besoins nets (MRP), concevoir le Plan Directeur de Production (PDP/MPS), ordonnancer la capacité et intégrer les données avec les modules de production ERP (SAP PP)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [supply-chain, erp, sap-pp, mrp, mps, planning, scheduling, capacity-planning, s-op, production-control]
  helios:
    related_skills: [lean-manufacturing-vsm, industrial-flow-simulation, materials-selection-metallurgy]
---

# Planification Industrielle & Intégration ERP (MRP / SAP)

## Vue d'ensemble

Cette compétence guide l'élaboration complète de la planification et de l'ordonnancement de la production dans une usine manufacturière ou de transformation. Elle couvre la chaîne logique de planification hiérarchique : le **Plan Industriel et Commercial (PIC / S&OP)** , le **Plan Directeur de Production (PDP / MPS)** , le **Calcul des Besoins Nets (MRP)** pour générer les ordres de fabrication et d'achat, l'**ordonnancement à capacité finie**, et l'intégration de ces flux de données avec le module de gestion de production d'un **ERP** tel que **SAP PP (Production Planning)** .

La planification industrielle repose sur un équilibre délicat entre la satisfaction de la demande client, l'optimisation des niveaux de stocks et la contrainte des capacités de production disponibles. Une erreur dans l'un des maillons de cette chaîne se répercute en cascade : stocks excédentaires, ruptures d'approvisionnement, heures supplémentaires non maîtrisées ou délais de livraison non tenus.

Cette compétence est conçue pour être actionnée par l'agent Helios lorsque l'utilisateur exprime un besoin lié à la configuration, l'optimisation ou l'analyse des flux planifiés de production dans un environnement industriel.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande explicitement ou implicitement de :

- Établir ou optimiser un Plan Directeur de Production (PDP / MPS) en fonction des prévisions de vente et des capacités d'usine.
- Effectuer ou configurer des calculs de besoins nets (MRP) basés sur la nomenclature des produits (BOM) et l'état des stocks.
- Résoudre des surcharges de capacité machine ou de main-d'œuvre à l'aide de techniques de lissage de charge (*load leveling*).
- Définir des flux d'intégration de données entre l'ERP (SAP) et le logiciel de supervision d'atelier (MES) pour le retour d'avancement des ordres de fabrication.
- Analyser des causes de rupture de stock ou d'encours excessifs.
- Dimensionner des stocks de sécurité ou optimiser les paramètres de gestion des approvisionnements (lots, délais, saisonnalité).
- Configurer un module SAP PP ou un système ERP équivalent pour un nouveau produit ou une nouvelle ligne de production.

---

## Architecture du processus MRP-II (Manufacturing Resource Planning)

La boucle MRP-II structure la planification en quatre niveaux hiérarchiques, chacun ayant son horizon temporel et sa granularité :

```text
    ┌──────────────────────────────────────────────────────┐
    │            PIC / S&OP (Sales & Operations Planning)   │
    │            Horizon : 1 à 3 ans   Pas : Mensuel        │
    │            Volume global par famille de produits       │
    └────────────────────────┬─────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────┐
    │          PDP / MPS (Master Production Schedule)       │
    │          Horizon : 1 à 6 mois   Pas : Hebdomadaire    │
    │          Produits finis ou options configurées        │
    └────────────────────────┬─────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────┐
    │    MRP (Material Requirements Planning)               │
    │    Horizon : 1 à 4 semaines   Pas : Quotidien         │
    │    Calcul des besoins en composants (BOM explosion)   │
    │    ┌─────────────┐            ┌──────────────────┐   │
    │    │ Ordres Achats│            │ Ordres Fabrication│  │
    │    └─────────────┘            └──────────────────┘   │
    └────────────────────────┬─────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────┐
    │ Ordonnancement & Lancement (Scheduling & Dispatching) │
    │ Horizon : 1 à 7 jours   Pas : Horaire / Continu      │
    │ Capacité finie, séquencement, règles de priorité     │
    └────────────────────────┬─────────────────────────────┘
                             │
                             ▼
    ┌──────────────────────────────────────────────────────┐
    │           Exécution Atelier (MES / Shop Floor)        │
    │           Déclaration de production, rebut, temps     │
    └──────────────────────────────────────────────────────┘
```

---

## Détail des niveaux de planification

### 1. PIC / S&OP (Sales & Operations Planning)

Le PIC constitue le niveau stratégique de la planification. Il établit un consensus entre les directions commerciale, industrielle et financière sur les volumes à produire par famille de produits sur un horizon glissant de 1 à 3 ans.

**Étapes clés du cycle S&OP (mensuel) :**

1. **Collecte des données commerciales** : Prévisions de vente (historique + intelligence marché), commandes fermes en portefeuille.
2. **Analyse de la capacité globale** : Comparaison du volume prévu avec la capacité théorique de l'usine (lignes, équipes, maintenance).
3. **Réunion de pré-S&OP** : Arbitrage entre demande excédentaire et capacité (sous-traitance, heures sup', investissements).
4. **Réunion exécutive S&OP** : Décisions engageant l'entreprise (approbation du plan, ajustements budgétaires).
5. **Diffusion du plan directeur** : Alimentation du PDP/MPS avec les volumes consolidés.

**Indicateurs clés :**

| Indicateur | Formule | Cible |
|:---|:---|:---|
| Taux de service client | $\frac{\text{Commandes livrées à temps}}{\text{Total commandes}}$ | $> 95\%$ |
| Rotation des stocks | $\frac{\text{Coût des ventes annuel}}{\text{Stock moyen}}$ | $> 6$ (selon secteur) |
| Précision des prévisions | $1 - \frac{|Réel - Prévision|}{Réel}$ | $> 80\%$ |

### 2. PDP / MPS (Master Production Schedule)

Le PDP détaille le PIC en un programme de production par **produit fini individuel** (ou variante/configurateur), par semaine, sur 1 à 6 mois.

**Règles de construction d'un PDP valide :**

- La quantité cumulée programmée ne doit pas dépasser la capacité cumulée disponible (vérification RCCP - *Rough Cut Capacity Planning*).
- Les ordres prévisionnels sont affichés dans une zone "gelée" (période où les modifications sont interdites ou très coûteuses) et une zone "libre" (ajustements possibles).
- Chaque ligne PDP est exprimée en **quantité disponible à promettre** (ATP - *Available To Promise*) pour les engagements commerciaux.

**Structure typique d'une table PDP :**

```text
Produit : MOTEUR-2000     Unité : pièces     Zone gelée : S1-S4
┌────────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ Semaine│ S1 │ S2 │ S3 │ S4 │ S5 │ S6 │ S7 │ S8 │
├────────┼────┼────┼────┼────┼────┼────┼────┼────┤
│Prévision│100 │100 │120 │120 │130 │130 │150 │150 │
│Fermes   │ 80 │ 90 │ 60 │ 40 │ 20 │ 10 │  0 │  0 │
│PDP plan │100 │100 │120 │120 │130 │130 │150 │150 │
│Stock proj│ 20 │ 20 │ 20 │ 20 │ 20 │ 20 │ 20 │ 20 │
│ATP      │ 20 │ 10 │ 60 │ 80 │110 │120 │150 │150 │
└────────┴────┴────┴────┴────┴────┴────┴────┴────┘
```

### 3. MRP (Material Requirements Planning)

Le MRP constitue le cœur du calcul logistique. Il **explose** la nomenclature (BOM) de chaque produit fini programmé au niveau PDP pour déterminer les quantités et les dates de besoin de chaque composant (matières premières, sous-ensembles, consommables).

**Logique de calcul :**

$$Besoins\ Nets = Besoins\ Bruts - Stock\ Disponible - Réceptions\ Attendues + Stock\ de\ Sécurité$$

Les paramètres clés du calcul MRP sont :

- **Gross Requirements (Besoins bruts)** : Quantité totale requise par le PDP et les ordres de maintenance/pièces de rechange.
- **Scheduled Receipts (Réceptions attendues)** : Ordres de fabrication ou d'achat déjà lancés, en cours de fabrication ou de livraison.
- **On Hand (Stock disponible)** : Quantité physique actuellement en stock (mise à jour par les mouvements de stock ERP).
- **Lead Time (Délai d'obtention)** : Délai entre le lancement de l'ordre et la réception en magasin.
- **Safety Stock (Stock de sécurité)** : Tampon pour absorber la variabilité de la demande ou des approvisionnements.
- **Lot Size (Taille de lot)** : Quantité minimale à commander (lot économique, périodique, ou *lot-for-lot*).

**Algorithme MRP simplifié (par composant) :**

```pseudo
POUR CHAQUE composant c DE LA BOM :
    besoin_net_c = 0
    POUR CHAQUE période p (de S1 à Sn) :
        besoin_brut = somme_des_besoins_descendants(c, p)
        disponibilité = stock_physique[p-1] + réceptions[p]
        besoin_net_p = max(0, besoin_brut - disponibilité)
        SI besoin_net_p > 0 :
            ordre = lancer_ordre(besoin_net_p, lot_size(c), lead_time(c))
            ordre.date_lancement = p - lead_time(c)
            stock_physique[p] = disponibilité - besoin_brut + ordre.quantité_arrivée
        SINON :
            stock_physique[p] = disponibilité - besoin_brut
```

### 4. Ordonnancement à capacité finie

L'ordonnancement affine les ordres MRP en affectant chaque opération à une ressource (centre de travail, ligne, poste) sur une échelle horaire, en respectant les contraintes de capacité.

**Méthodes d'ordonnancement :**

- **Forward Scheduling** : Planification au plus tôt ; utile pour les commandes urgentes.
- **Backward Scheduling** : Planification au plus tard à partir de la date d'échéance ; minimise les encours.
- **Optimisation séquentielle** : Utilisation de règles de priorité (FIFO, EDD, SPT, CR) pour départager les files d'attente.

**Indicateurs de performance ordonnancement :**

| Métrique | Définition |
|:---|:---|
| Taux de charge machine | $\frac{Temps\ de\ production\ alloué}{Temps\ disponible} \times 100$ |
| Retard moyen | Moyenne des écarts entre date de fin réelle et date due |
| Taux de respect des délais | $ \frac{OF\ terminés\ à\ temps}{OF\ total} \times 100$ |

---

## Intégration ERP / MES

La boucle de planification est alimentée en temps réel par les données de l'atelier via l'interface ERP-MES :

```text
ERP (SAP PP)
    │
    │ Transfert des OF (IDoc / RFC / BAPI)
    ▼
MES (Manufacturing Execution System)
    │
    │ Acquisition : déclaration de production, temps d'arrêt, rebuts, consommations
    ▼
Retour vers ERP : Stock réel, encours, TRS, main-d'œuvre passée
```

**Quatre flux de données essentiels à configurer :**

1. **Ordres de fabrication → MES** : Données d'OF (nomenclature, gamme, quantité, date due, lots matières premières).
2. **Déclarations de production → ERP** : Quantités produites, rebutées, temps passé par opération.
3. **Consommations de matière → ERP** : Sorte de stock automatique des composants utilisés.
4. **Retour d'avancement → Planning** : Mise à jour du statut OF (libre, lancé, en cours, terminé, clôturé) pour recalcul MRP.

---

## Pièges Courants (Common Pitfalls)

### 1. Données de stocks et de nomenclatures obsolètes dans l'ERP

**Erreur :** Lancer un calcul MRP automatique alors que les stocks réels physiques diffèrent de plus de 10 % des stocks informatiques enregistrés dans SAP, ou que les nomenclatures (BOM) contiennent des pièces remplacées depuis longtemps sans mise à jour. Le MRP générera des ordres d'achat erronés, bloquant la production par manque de pièces ou créant du sur-stockage coûteux.

**Correction :** Mettre en place des inventaires tournants fréquents (comptage cyclique) pour maintenir une précision des stocks supérieure à 98 %. Coupler l'ERP aux nomenclatures CAO via des workflows PLM (Product Lifecycle Management) stricts avec validation obligatoire avant publication.

### 2. L'effet coup de fouet (Bullwhip Effect)

**Erreur :** Réagir de manière disproportionnée à une petite variation de la demande client finale en commandant des lots massifs de composants en amont, ce qui amplifie les fluctuations de stocks à chaque échelon de la chaîne logistique (fournisseur → usine → distribution → client).

**Correction :** Partager les données de consommation réelles (point-of-sale) tout au long de la chaîne logistique (VMI - Vendor Managed Inventory). Réduire la taille des lots de commande en favorisant des livraisons fréquentes de petits lots. Limiter les délais de réapprovisionnement par des accords cadres.

### 3. Planification sans prise en compte de la capacité réelle

**Erreur :** Lancer un PDP et un MRP en capacité infinie (sans vérifier si les postes de charge peuvent absorber les volumes programmés). Le planning affiche des centaines d'OF, mais les ateliers saturés ne peuvent pas suivre, créant des encours monstrueux et une perte de visibilité.

**Correction :** Exécuter systématiquement un RCCP (Rough Cut Capacity Planning) après chaque mise à jour du PDP, puis un CRP (Capacity Requirements Planning) au niveau MRP, pour valider la faisabilité avant diffusion des ordres.

### 4. Périodes gelées trop longues ou trop courtes

**Erreur :** Définir une zone gelée de 12 semaines (aucun changement de programme possible) qui rend l'usine incapable de réagir à une commande urgente d'un client stratégique. À l'inverse, une zone gelée de 1 semaine expose l'atelier à des changements incessants qui perturbent les approvisionnements.

**Correction :** Adopter une règle de *time fencing* ajustée au cycle de fabrication : gel à J+1 pour les approvisionnements longs, modifiable à J+2 et prévisionnel à J+3. Réviser la durée gelée trimestriellement avec l'équipe logistique.

---

## Liste de vérification (Checklist)

- [ ] La nomenclature (BOM) et la gamme opératoire (Routing) sont synchronisées entre l'ERP et les outils de CAO/méthodes.
- [ ] Le calcul du MRP intègre les délais de livraison (*Lead Times*) réels des fournisseurs pour chaque composant critique.
- [ ] La planification à capacité finie a été vérifiée pour éviter toute surcharge sur les postes de travail goulets.
- [ ] Les ordres de fabrication (OF) générés contiennent les liens de traçabilité nécessaires (numéros de lots de matières premières).
- [ ] L'interfaçage ERP/MES assure une remontée d'information en temps réel (déclarations de pièces produites et rebutées).
- [ ] Les paramètres MRP (stock de sécurité, délai, lot size) sont configurés pour chaque article dans SAP / ERP.
- [ ] Un processus S&OP mensuel est formalisé et documenté avec les participants identifiés (commercial, production, achats, finance).
- [ ] Le calcul ATP (Available To Promise) est opérationnel et utilisé par l'équipe commerciale pour les engagements clients.
- [ ] Les inventaires tournants cycliques sont en place avec une fréquence adaptée à la criticité des articles (classes ABC).
- [ ] Un tableau de bord de suivi MRP est édité quotidiennement listant les anomalies (besoins non couverts, réceptions en retard, engorgements).

