---
name: agrifood-norms-haccp
description: "Appliquer les normes agroalimentaires : HACCP (Codex Alimentarius), BRC Food, IFS Food, FSSC 22000, GlobalGAP, traçabilité et plans de maîtrise sanitaire (PMS)."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [agrifood, haccp, brc-food, ifs-food, fssc-22000, globalgap, traceability, pms, food-safety, certification, codex-alimentarius]
    related_skills: [iso-22000, iso-quality, gmp-pharmaceutical, industrial-risk-analysis-hazop, logistics-wms-inventory]
    difficulty: intermediate
    industry_sectors: [food-beverage, agrifood, meat-processing, dairy, bakery, beverages, ingredients, seafood, animal-feed, packaging]
---

# Normes Agroalimentaires — HACCP, BRC, IFS, FSSC 22000, GlobalGAP

## Vue d'ensemble

Le secteur agroalimentaire est encadré par un ensemble de **normes et référentiels** qui garantissent la sécurité sanitaire des denrées alimentaires, la qualité des produits et la transparence de la chaîne d'approvisionnement. Cette compétence couvre les principaux référentiels au-delà de l'ISO 22000 : les standards privés (BRC Food, IFS, FSSC 22000) et les référentiels spécifiques (GlobalGAP, Organic/Bio, MSC, etc.).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'implémenter un plan HACCP complet selon le Codex Alimentarius.
- De préparer une certification BRC Food (British Retail Consortium) ou IFS Food.
- D'auditer un site de production agroalimentaire selon FSSC 22000.
- De structurer un Plan de Maîtrise Sanitaire (PMS) réglementaire.
- De répondre aux exigences GlobalGAP pour les exploitations agricoles.
- De mettre en place un système de traçabilité des lots (farm-to-fork).
- De préparer un audit client (grande distribution, marques propres).

**Ne pas utiliser pour :**
- La pharmacie / GMP (utiliser `gmp-pharmaceutical`).
- La qualité uniquement (goût, texture) sans sécurité sanitaire.

---

## 1. Panorama des Référentiels Agroalimentaires

| Référentiel | Type | Domaine | Exigences Clés | Organisme |
|:---|:---|:---|:---|:---|
| **Codex Alimentarius HACCP** | Base réglementaire | Analyse des dangers — tous secteurs | 7 principes HACCP, PRP | FAO / OMS |
| **BRC Food (Issue 9)** | Standard privé — Grande distribution | Transformation alimentaire | HACCP + SQF + Culture sécurité + Food Fraud | BRCGS |
| **IFS Food (v8)** | Standard privé — Grande distribution | Transformation, logistique | HACCP + Quality Management + Food Defense | IFS |
| **FSSC 22000 (v6)** | Standard GFSI reconnu | Toute la chaîne | ISO 22000 + PRP ISO/TS 22002-1 | Foundation FSSC |
| **GlobalGAP** | Standard production primaire | Agriculture, élevage, aquaculture | Bonnes pratiques agricoles (BPA) | FoodPLUS |
| **SQF (Safe Quality Food)** | Standard GFSI reconnu | Transformation, distribution | HACCP + Quality + Food Safety Culture | FMI |
| **Bio / AB** | Réglementaire | Agriculture biologique | Pas d'intrants chimiques de synthèse | ECOCERT, FR-BIO |
| **MSC (Marine Stewardship Council)** | Standard pêche durable | Pêche et produits de la mer | Traçabilité, pêche durable | MSC |
| **IFS Logistics** | Standard privé | Logistique et transport | Bonnes pratiques logistiques | IFS |

### 1.1 Standards GFSI vs Non-GFSI

Les standards **reconnus GFSI** (Global Food Safety Initiative) sont acceptés par tous les grands distributeurs mondiaux :

```
Standards GFSI : 
  - FSSC 22000
  - BRC Food
  - IFS Food
  - SQF
  - GlobalGAP (optionnelle)
```

---

## 2. Structure d'un Plan HACCP Complet (Codex Alimentarius)

### 2.1 Les 12 Étapes du Codex Alimentarius

```
Étape  1 : Constituer l'équipe HACCP
Étape  2 : Décrire le produit
Étape  3 : Définir l'utilisation prévue
Étape  4 : Établir le diagramme de fabrication
Étape  5 : Confirmer le diagramme sur site
                  ⬇
Étape  6 : Analyser les dangers (Principe 1)
Étape  7 : Déterminer les CCP (Principe 2)
Étape  8 : Établir les limites critiques (Principe 3)
Étape  9 : Mettre en place la surveillance (Principe 4)
Étape 10 : Définir les actions correctives (Principe 5)
Étape 11 : Vérifier le système HACCP (Principe 6)
Étape 12 : Documenter et archivage (Principe 7)
```

### 2.2 Exemple : Fiche HACCP — Détection Métaux (CCP)

```yaml
CCP_ID: CCP-02
Étape_procédé: Détection métaux — Lot 3
Danger: Physique (métal ferreux, inox, aluminium)
Limite_critique: Fe ≥ 1.0 mm / Inox ≥ 1.5 mm / Al ≥ 2.0 mm
Surveillance: Détecteur de métaux Loma IQ3 en continu
Fréquence_surveillance: Chaque produit (100%)
Méthode_surveillance: 
  - Rejet automatique par éjecteur pneumatique
  - Test de bon fonctionnement toutes les 2h (témoin Fe, Inox, Al)
Responsable: Opérateur L3, Technicien maintenance
Action_corrective:
  - Isolation des produits depuis le dernier test OK
  - Nettoyage du détecteur
  - Nouveau test — si échec → arrêt ligne + maintenance
Enregistrement: Rapport de détection (SCADA ou papier)
```

---

## 3. BRC Food (Issue 9) — Exigences Spécifiques

### 3.1 Les 9 Clauses BRC Food

| Clause | Titre | Focus |
|:---|:---|:---|
| 1 | Engagement de la direction | Culture sécurité, plan d'action, réunions |
| 2 | Plan HACCP / Food Safety Plan | 12 étapes Codex, Food Fraud, Food Defense |
| 3 | Système de management qualité | Documentation, traçabilité, audit interne |
| 4 | Standards des sites | Building fabric, zonage, flux, utilities |
| 5 | Contrôle des produits | Spécifications, étiquetage, allergènes |
| 6 | Contrôle des procédés | CCP, PRPO, contrôle température |
| 7 | Personnel | Formation, hygiène, tenue, visiteurs |
| 8 | Zones à haut risque | High Care, High Risk, Ambient High Care |
| 9 | Exigences commerce | Produits sous marque distributeur |

### 3.2 Exigences Cleanroom / Zonage (Clause 8)

```yaml
Zones BRC Food:
  High Risk (HR):
    - Produits prêts à consommer, sensibles (salades, plats cuisinés)
    - Pression positive, filtration HEPA H13
    - Sas personnel + matériel
    - Nettoyage CIP/COP validé
  
  High Care (HC):
    - Produits cuits puis manipulés
    - Pression positive, filtration min. EU7
    - Séparation physique
  
  Ambient High Care (AHC): 
    - Produits secs sensibles (poudres)
    - Contrôle humidité et nuisibles
```

---

## 4. FSSC 22000 (v6) — Spécificités

Le FSSC 22000 combine l'ISO 22000 avec des PRP sectoriels :

| Secteur | Référentiel PRP | Domaines couverts |
|:---|:---|:---|
| Agroalimentaire | ISO/TS 22002-1 | Toute transformation alimentaire |
| Catering | ISO/TS 22002-2 | Restauration collective |
| Emballage | ISO/TS 22002-4 | Fabrication d'emballages alimentaires |
| Logistique | ISO/TS 22002-5 | Transport et entreposage |
| Bio | NEN-EN 15593 | Complément bio |

---

## 5. Traçabilité et Gestion des Allergènes

### 5.1 Exigences de Traçabilité

```yaml
Exigences:
  Traçabilité amont: Origine matière première, fournisseur, date réception
  Traçabilité process: Lot process, ligne, équipement, opérateur
  Traçabilité aval: Client, date expédition, transporteur

Tests de traçabilité:
  Fréquence: ≥ 2 fois par an
  Méthode: Simulation d'alerte sanitaire
  Cible: Lot retracé en < 4h (farm-to-fork)
  Résultat: Rapport de test + actions correctives si délai dépassé
```

### 5.2 Plan de Gestion des Allergènes

```yaml
Matrice allergènes (RGAA / INCO) :
  Obligatoires (UE 1169/2011):
    - Gluten (blé, seigle, orge, avoine)
    - Arachide
    - Fruits à coque (amande, noisette, noix, cajou, etc.)
    - Lait (dont lactose)
    - Œuf
    - Poissons
    - Crustacés
    - Soja
    - Céleri
    - Moutarde
    - Sésame
    - Sulfites (> 10 mg/kg)
    - Lupin
    - Mollusques

  Mesures:
    - Analyse des risques de contamination croisée
    - Nettoyage validé entre productions (ELISA swab)
    - Déclaration « peut contenir » si risque résiduel
```

---

## 6. Pièges Courants

1. **HACCP théorique non vérifié sur site :**
   - *Erreur* : Diagramme de fabrication créé en salle de réunion jamais vérifié sur le terrain.
   - *Correction* : L'étape 5 du Codex (confirmation sur site) est obligatoire et doit être tracée.

2. **Allergènes non maîtrisés :**
   - *Erreur* : Pas de séparation physique des flux contenant des allergènes.
   - *Correction* : Zonage dédié ou nettoyage validé entre campagnes + analyse ELISA.

3. **BRC Food — Culture sécurité négligée :**
   - *Erreur* : Pas de plan d'amélioration de la culture sécurité (exigence clause 1.1.2 BRC v9).
   - *Correction* : Enquête annuelle employés, plan d'actions, formation.

4. **FSSC 22000 — PRP non à jour :**
   - *Erreur* : Utiliser des PRP génériques sans adaptation sectorielle.
   - *Correction* : Appliquer ISO/TS 22002-1 (ou -2/-4/-5 selon le secteur).

5. **Food Fraud / Food Defense non traités :**
   - *Erreur* : Pas d'analyse de vulnérabilité aux fraudes alimentaires.
   - *Correction* : Réaliser une VACCP (Vulnerability Assessment) et TACCP (Threat Assessment).

---

## Liste de vérification

- [ ] Le référentiel cible est identifié (BRC, IFS, FSSC 22000, GlobalGAP, etc.).
- [ ] Le plan HACCP suit les 12 étapes du Codex Alimentarius.
- [ ] Les limites critiques des CCP sont définies et validées scientifiquement.
- [ ] Les PRP sont conformes aux exigences sectorielles (ISO/TS 22002-X).
- [ ] Le plan de gestion des allergènes est documenté (analyse + contrôles).
- [ ] Le test de traçabilité est réalisé (≥ 2 fois/an, objectif < 4h).
- [ ] L'analyse Food Fraud (VACCP) est réalisée et documentée.
- [ ] Le plan Food Defense (TACCP) est en place.
- [ ] La culture sécurité alimentaire est évaluée (enquête, plan d'actions).
- [ ] Les plans d'audit interne et de certification sont programmés.
