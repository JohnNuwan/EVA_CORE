---
name: iso-22000
description: "Implémenter et auditer un système de management de la sécurité des denrées alimentaires (SMSDA) conforme à ISO 22000 basé sur la méthodologie HACCP : analyse des dangers, CCP/PRPO, traçabilité des lots, plans de maîtrise sanitaire (PMS), gestion des allergènes."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [iso-22000, food-safety, haccp, agrifood-process, industrial-standards, smsda, ccp, prpo, traceability, allergen-management, hygeine, food-industry]
    related_skills: [process-agrifood, iso-quality, industrial-reporting, lean-manufacturing-vsm]
    difficulty: intermediate
    industry_sectors: [food-beverage, dairy, meat-processing, bakery, beverages, animal-feed, ingredients]
---

# Sécurité Alimentaire (HACCP) & Norme ISO 22000

## Vue d'ensemble

La norme **ISO 22000** (version actuelle : ISO 22000:2018) définit les exigences relatives à un système de management de la sécurité des denrées alimentaires (SMSDA). Elle s'applique à tous les organismes de la chaîne alimentaire, de la fourche à la fourchette (farm-to-fork), avec un accent particulier sur les usines de transformation agroalimentaire.

### Contexte : Pourquoi la Sécurité Alimentaire ?

Les crises sanitaires des dernières décennies (vache folle E.S.B., Listeria, Salmonella, produits laitiers contaminés, bisphénol A, fraudes à la viande de cheval) ont démontré la nécessité d'un contrôle rigoureux de la chaîne alimentaire. Les conséquences d'une défaillance sont :

- **Sanitaires** : Intoxications alimentaires pouvant entraîner des décès (Listeria : 20-30 % de mortalité chez les populations sensibles).
- **Économiques** : Rappels de produits coûtant des millions d'euros (perte du lot + destruction + tests + image de marque).
- **Juridiques** : Poursuites pénales, fermeture administrative du site.

### Les 5 Piliers de l'ISO 22000

1. **La communication interactive** : Assurer la traçabilité des lots en amont (fournisseurs, matières premières) et en aval (distributeurs, clients). Communication efficace avec les autorités réglementaires (DGCCRF, DDPP).
2. **Le management du système** : Alignement avec la structure de management de la qualité (ISO 9001) via la structure HLS commune.
3. **Les Programmes Prérequis (PRP)** : Règles d'hygiène de base (nettoyage en place NEP/CIP, lutte contre les nuisibles, hygiène du personnel principe de marche en avant, qualité de l'air et de l'eau).
4. **Les principes HACCP** (Hazard Analysis Critical Control Point) : Identifier les dangers biologiques, chimiques ou physiques à chaque étape du procédé et définir les points critiques à maîtriser (CCP) pour garantir la sécurité du produit final.
5. **La traçabilité et la gestion des incidents** : Capacité à retracer un lot de la matière première au produit fini (et inversement) en moins de 4 heures, et à gérer le retrait / rappel des produits non conformes.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :

- D'établir un **plan HACCP** complet pour une ligne de fabrication agroalimentaire (analyse des dangers, arbre de décision CCP, définition des limites critiques).
- De définir et documenter des **points critiques pour la maîtrise (CCP)** ou des **programmes prérequis opérationnels (PRPO)**.
- De rédiger des **procédures d'historisation** de données de pasteurisation, de stérilisation, de détection de métaux (métrologie et traçabilité).
- De concevoir un **plan de maîtrise sanitaire (PMS)** incluant les PRP, le HACCP, la traçabilité et la gestion des allergènes.
- D'accompagner la préparation d'un **audit de certification ISO 22000** ou d'un référentiel privé (BRC Food, IFS, FSSC 22000).
- De structurer un **plan de gestion des allergènes** (identification, séparation des flux, nettoyage validé).

**Ne pas utiliser pour :**
- Les procédés pharmaceutiques ou cosmétiques (Bonnes Pratiques de Fabrication — GMP — utiliser `process-pharma`).
- Les questions de qualité produit hors sécurité alimentaire (goût, texture, couleur) — utiliser `iso-quality`.

## 1. Analyse des Dangers et Définition des CCP

### Classification des Dangers Alimentaires

| Catégorie de danger | Type | Exemples | Source possible |
|:---|---|---|:---|
| **Biologique** | Bactéries pathogènes | Salmonella, Listeria monocytogenes, E. coli O157:H7, Clostridium botulinum, Campylobacter | Matières premières crues, contamination croisée, défaut de cuisson |
| **Biologique** | Virus | Norovirus, Hépatite A | Personnel contaminé, eaux usées |
| **Biologique** | Moisissures / Mycotoxines | Aflatoxines, Ochratoxine A | Céréales, fruits secs, épices |
| **Chimique** | Allergènes | Arachide, gluten, lait, œuf, soja, fruits à coque, sulfites | Contamination croisée, étiquetage erroné |
| **Chimique** | Résidus de nettoyage | Détergents, désinfectants (NEP/CIP) | Rinçage insuffisant après nettoyage |
| **Chimique** | Contaminants industriels | Dioxines, PCB, métaux lourds (plomb, cadmium, mercure) | Environnement, matières premières |
| **Physique** | Corps étrangers | Métal, verre, plastique dur, bois, cailloux | Usure d'équipement, casse, matière première |
| **Physique** | Radiologique | Contamination radioactive | Environnement (Fukushima, Tchernobyl) |

### Arbre de Décision CCP (Codex Alimentarius)

Pour chaque danger identifié, appliquer l'arbre de décision suivant :

1. **Q1** : Existe-t-il une mesure de maîtrise pour ce danger ?
   - Oui → Aller à Q2.
   - Non → Modifier l'étape, le produit ou le procédé avant de continuer.
2. **Q2** : Cette étape est-elle spécifiquement conçue pour éliminer ou réduire le danger à un niveau acceptable ?
   - Oui → **CCP**.
   - Non → Aller à Q3.
3. **Q3** : Une contamination par le danger identifié peut-elle survenir à un niveau dépassant la limite acceptable ou peut-elle augmenter à un niveau inacceptable ?
   - Oui → Aller à Q4.
   - Non → Ce n'est pas un CCP. Gestion par PRP(O).
4. **Q4** : Une étape ultérieure (aval) éliminera-t-elle le danger identifié ou le réduira-t-elle à un niveau acceptable ?
   - Oui → Ce n'est pas un CCP. Gestion par PRP(O).
   - Non → **CCP**.

### Exemple de Fiche CCP : Pasteurisation du Lait

```text
ÉQUIPEMENT : Pasteurisateur Flash Ligne 2
PARAMÈTRE CRITIQUE (CCP-01) : Température de pasteurisation du flux.

1. LIMITES CRITIQUES :
   • Seuil de sécurité bas : 72,0 °C (température minimale requise).
   • Seuil de sécurité haut : 78,0 °C (ne pas dénaturer les protéines).
   • Temps de maintien minimal : 15 secondes dans la chambre de chambrage.

2. SURVEILLANCE TEMPS RÉEL (AUTOMATE / SCADA) :
   • Capteur TT-201 : Sonde double Pt100 (redondance) étalonnée.
   • Si TT-201 < 72,0 °C pendant le cycle :
     - Action Auto 1 : Commande de la vanne de dérivation (Diverter Valve YV-201)
       pour renvoyer le lait non conforme vers le bac de lancement.
     - Action Auto 2 : Activation de l'alarme sonore et visuelle de ligne.
     - Action Auto 3 : Blocage de l'enregistrement de l'Ordre de Fabrication (OF)
       comme "Non Conforme" dans le MES.

3. FRÉQUENCE DE SURVEILLANCE :
   • Mesure continue historisée toutes les 1 seconde dans la base de données SCADA.

4. ACTIONS CORRECTIVES EN CAS DE DÉRIVE :
   • Consigner le lot non conforme (isolement physique).
   • Analyser le produit (test microbiologique : absence de Listeria, Salmonella).
   • Déclasser ou détruire le lot si non conforme.
   • Rechercher la cause racine (défaut du régulateur de température, baisse de vapeur).

5. VÉRIFICATION :
   • Étalonnage du capteur PT100 tous les 6 mois (certificat d'étalonnage).
   • Test de la vanne de dérivation toutes les semaines.
   • Audit interne annuel du CCP.
```

## 2. Programmes Prérequis (PRP) et PRP Opérationnels (PRPO)

### Grille PRP / PRPO

| Catégorie | Sujet | Exigences clés | PRP ou PRPO |
|:---|---|---|:---:|
| Infrastructures | Conception des locaux | Marche en avant (propre ↔ sale), sols/parois lavables, ventilation | PRP |
| Nettoyage / Désinfection | NEP/CIP | Plan de nettoyage, concentration/débit/température, rinçage validé | PRPO (si CCP pas atteignable) |
| Lutte contre les nuisibles | Insectes, rongeurs, oiseaux | Plan de dératisation/désinsectisation, pièges, registre des captures | PRP |
| Hygiène du personnel | Tenue, lavage des mains | Sas d'hygiène, lavabos, désinfectant, contrôle microbiologique des mains | PRP |
| Eau / Air comprimé | Qualité | Plan de contrôle de la qualité de l'eau (microbio + physico-chimie), filtration air | PRP |
| Formation / Compétences | Personnel | Plan de formation HACCP/hygiène, évaluation des compétences | PRP |
| Gestion des allergènes | Séparation des flux | Stockage séparé, lignes dédiées, nettoyage validé, test ELISA | PRPO |
| Traçabilité | Lots | Lot fournisseur → lot production → lot client, test de traçabilité biannuel | PRP |
| Gestion des corps étrangers | Détection | Détecteur de métaux (X) + aimant + tamis, test de validation périodique | PRPO / CCP |

## 3. Traçabilité et Gestion des Rappels

### Exigences de Traçabilité

1. **Unité de traçabilité** : Chaque lot de matière première, de production et de produit fini doit être identifié de manière unique (numéro de lot, date de production + code produit).
2. **Enregistrements obligatoires** : Volumes/dates des réceptions fournisseurs, OF de production, résultats des CCP, résultats des contrôles qualité, expéditions clients.
3. **Test de traçabilité** : Réaliser un test au moins deux fois par an :
   - **Trace avant** (ascendante) : À partir d'un produit fini, retrouver tous les lots de matières premières en moins de 4 heures.
   - **Trace arrière** (descendante) : À partir d'un lot de matière première, retrouver tous les produits finis concernés en moins de 4 heures.
4. **Gestion des rappels** : Procédure documentée pour le retrait (produit encore dans la chaîne de distribution) et le rappel (produit déjà chez le consommateur).

### Matrice de Décision de Rappel

| Type de danger | Niveau de risque | Action |
|:---|---|:---|
| Corps étranger métallique > 7 mm | Critique | Rappel immédiat, notification DDPP |
| Allergène non déclaré (ex : arachide non mentionné) | Élevé | Rappel immédiat, communication publique |
| Dépassement de température de conservation (< +4 °C pendant > 2h) | Moyen | Retrait, analyse microbiologique avant décision |
| Défaut d'étiquetage mineur (date de durabilité erronée) | Faible | Retrait, ré-étiquetage |

## Pièges Courants (Common Pitfalls)

1. **Absence de contrôle de dérivation de flux (bypass de sécurité) :**
   - *Erreur :* Autoriser la production à continuer même si la température de pasteurisation est descendue sous le seuil critique (ex : 70 °C au lieu de 72 °C) sans dérivation automatique. Cela peut contaminer tout un lot de production avec des bactéries pathogènes (Listeria, Salmonella).
   - *Correction :* Câbler une vanne de dérivation de sécurité physique pilotée par l'automate (sortie TOR ou analogique). La logique de l'automate doit forcer la dérivation sans possibilité de bypass par l'opérateur en mode automatique. La vanne doit être normalement fermée sur position dérivation (fail-safe).

2. **Ignorer la validation du détecteur de métaux / de l'aimant :**
   - *Erreur :* Laisser le détecteur de métaux en bout de ligne fonctionner pendant des jours sans tester sa capacité de détection. Si un fragment métallique traverse le process sans être détecté, le produit peut blesser le consommateur (poursuites pénales).
   - *Correction :* Imposer un test de validation périodique toutes les 2 à 4 heures (selon le risque) en faisant passer des éprouvettes témoins (Fer, Non-Fer, Inox AISI 316) de différents diamètres à travers le détecteur. Le système de rejet automatique (éjecteur) doit fonctionner correctement à chaque test.

3. **Marche en avant non respectée dans les locaux :**
   - *Erreur :* Concevoir l'usine avec des flux de circulation qui permettent à des produits finis (propres) de croiser des matières premières (sales) ou des déchets. Risque de contamination croisée élevé.
   - *Correction :* Appliquer strictement le principe de **marche en avant** (principe du SAS) : les matières premières entrent par une zone dédiée (zone sale), le process doit suivre un flux linéaire sans retour possible vers les zones précédentes, les produits finis sortent par une zone propre séparée. Les flux de personnel, d'air et de déchets doivent également suivre ce principe.

4. **Analyse HACCP non révisée après modification du procédé :**
   - *Erreur :* Modifier une recette, une ligne de production, un fournisseur ou un équipement sans revoir l'analyse HACCP. Un nouveau danger peut apparaître (ex : nouvel allergène dans une nouvelle matière première, température de stérilisation différente).
   - *Correction :* Toute modification (quel que soit son ampleur) doit déclencher une revue de l'analyse des dangers et une mise à jour du plan HACCP. Désigner un pilote HACCP qui valide les changements.

## Références

- **ISO 22000:2018** : Systèmes de management de la sécurité des denrées alimentaires — Exigences.
- **ISO 22002-1** : Programme prérequis pour la sécurité des denrées alimentaires (fabrication).
- **Codex Alimentarius** (CAC/RCP 1-1969) : Principes généraux d'hygiène alimentaire — HACCP.
- **Règlement CE n° 852/2004** : Hygiène des denrées alimentaires.
- **Règlement CE n° 178/2002** : Principes généraux de la législation alimentaire (traceability, RASFF).
- **DGCCRF** : Guide de gestion des alertes et des rappels de produits.
- **IFS Food** (International Featured Standards) : Standard privé de certification sécurité alimentaire.
- **BRC Global Standard for Food Safety** : Standard privé britannique de certification.
- **FSSC 22000** : Schéma de certification basé sur l'ISO 22000 + ISO 22002-1.

## Liste de vérification (Checklist)

- [ ] **L'analyse des dangers** (HACCP) couvre les risques physiques (métal, verre, plastique, bois), chimiques (allergènes, résidus de nettoyage, migrateurs) et biologiques (bactéries pathogènes, virus, moisissures) pour chaque étape du procédé.
- [ ] Les **limites critiques des CCP** (ex : température de pasteurisation, temps de maintien, pression de stérilisation, taille de maille de tamis) sont vérifiées, validées et étayées par des rapports de métrologie et de validation scientifique.
- [ ] Une **logique de dérivation ou de rejet automatique** inviolable est programmée dans l'automate pour chaque CCP. Le bypass opérateur est impossible en mode automatique.
- [ ] Les **rapports de traçabilité** associent le profil des CCP (température, pression, etc.) de chaque lot de production à son identifiant unique (numéro de lot / OF).
- [ ] Les **tests de traçabilité** (ascendante et descendante) sont réalisés au moins 2 fois par an et les résultats montrent un temps de réponse < 4 heures.
- [ ] Un **plan de gestion des allergènes** est documenté, affiché dans les zones de production concernées, et les procédures de nettoyage sont validées (tests ELISA / PCR).
- [ ] Les **détecteurs de métaux / X-ray** sont testés toutes les 2-4 heures avec des éprouvettes (Fe, Non-Fe, Inox) et les résultats sont enregistrés.
- [ ] Les **PRP** (programmes prérequis : hygiène, nuisibles, eau, air, personnel) sont audités au moins une fois par an.
- [ ] Les **formations HACCP / hygiène alimentaire** du personnel sont à jour (au moins un recyclage tous les 3 ans).
- [ ] La **revue de direction** du SMSDA est réalisée annuellement et les objectifs de sécurité alimentaire sont définis et suivis.

