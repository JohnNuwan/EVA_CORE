---
name: industrial-maintenance-preventive
description: "Planifier et exécuter les opérations de maintenance préventive et corrective sur les équipements industriels, mener des diagnostics physiques (analyse vibratoire, thermographie infrarouge, ultrasons) et résoudre les pannes selon une approche systématique."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [maintenance, preventive-maintenance, corrective-maintenance, troubleshooting, vibration-analysis, thermography, diagnostics, cmms, gmao, lubrication, loto]
  EVA:
    related_skills: [cmms-gmao-integration, industrial-maintenance-reliability, oee-performance]
    difficulty: intermediate
    industry_sectors: [manufacturing, chemical, pharmaceutical, energy, food-beverage, automotive]
---

# Maintenance Opérationnelle Industrielle (Préventive & Corrective)

## Vue d'ensemble

Cette compétence couvre l'intégralité du cycle de vie de la maintenance opérationnelle sur site industriel : de la planification des interventions préventives à la résolution des pannes correctives, en passant par les techniques de diagnostic physique non destructif. Elle s'adresse aux techniciens de maintenance, aux responsables d'atelier et aux ingénieurs fiabilistes.

La maintenance industrielle se décompose en trois grandes familles :

1. **Maintenance Préventive Systématique** : Interventions planifiées à intervalles réguliers (calendaires ou horaires) indépendamment de l'état de l'équipement. Elle inclut la lubrification, le remplacement de pièces d'usure, les inspections visuelles et les contrôles fonctionnels.
2. **Maintenance Préventive Conditionnelle** : Interventions déclenchées par des seuils prédéfinis mesurés via des techniques de surveillance (vibrations, température, analyse d'huile). Permet d'optimiser les intervalles d'intervention au plus proche du besoin réel.
3. **Maintenance Corrective** : Réparation après panne. Elle doit être organisée selon des procédures standardisées pour minimiser le temps d'arrêt (MTTR) et garantir la sécurité des intervenants.

### Contexte Industriel

Dans une usine de production, les équipements critiques (moteurs, pompes, compresseurs, convoyeurs) représentent un enjeu économique majeur. Un arrêt non planifié peut coûter de 5 000 € à plus de 100 000 € par heure selon le secteur. La maintenance préventive vise à réduire ces arrêts en anticipant les défaillances. Les données de maintenance sont historisées dans un système GMAO (Gestion de Maintenance Assistée par Ordinateur) qui permet de suivre la traçabilité des interventions et d'alimenter les analyses de fiabilité.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Rédiger une **gamme de maintenance préventive** détaillée (procédure de lubrification, vérification d'alignement d'arbres, contrôle de serrage) avec les consignes de sécurité associées.
- Établir une **méthodologie de diagnostic** pour identifier la cause racine d'une défaillance physique (arbre cassé, moteur en surchauffe, roulement détruit).
- Analyser des **relevés de mesures vibratoires** (spectres fréquentiels de roulements, FFT) ou des **clichés thermographiques** d'armoires électriques ou de machines tournantes.
- Rédiger des **fiches d'intervention corrective** complètes (rapports de panne, étapes de remplacement de composants, essais de bon fonctionnement).
- Définir des **plans de maintenance** basés sur les préconisations constructeur et les historiques de pannes.

**Ne pas utiliser pour :**
- Les calculs avancés de fiabilité (MTBF, MTTR, Weibull) qui relèvent de la compétence `industrial-maintenance-reliability`.
- La gestion des stocks de pièces de rechange ou l'optimisation des approvisionnements (compétence dédiée logistique).

## Techniques de Diagnostic Physique Non Destructif

### 1. Analyse Vibratoire

Permet de diagnostiquer l'état de santé des machines tournantes (moteurs, pompes, ventilateurs, compresseurs, centrifugeuses) en mesurant les vibrations générées par les composants en rotation.

| Défaut Mécanique | Signature Fréquentielle | Harmoniques | Direction de Mesure |
|:---|---|:---:|:---:|
| **Balourd (Déséquilibre)** | Pic dominant à $1 \times f$ (fréquence de rotation) | Faibles harmoniques | Radiale |
| **Désalignement d'arbre** | Pics à $1 \times f$ et $2 \times f$ (voire $3 \times f$) | Harmonica 2 élevé | Axiale et radiale |
| **Défaut de roulement (bague externe)** | Fréquences BPFO (Ball Pass Frequency Outer) | Bande latérale à $1 \times f$ | Radiale |
| **Défaut de roulement (bague interne)** | Fréquences BPFI (Ball Pass Frequency Inner) | Bande latérale à $1 \times f$ | Radiale |
| **Lubrification insuffisante** | Bruit de fond large bande élevé | Aucune harmonique distincte | Toutes directions |
| **Jeu mécanique excessif** | Multiples sous-harmoniques à $0.5 \times f$ | Harmoniques paires et impaires | Radiale |

**Matériel nécessaire :** Accéléromètre piézoélectrique (sensibilité typique 100 mV/g), collecteur de données vibrant, logiciel d'analyse FFT (Fast Fourier Transform). Les mesures sont généralement réalisées en vitesse (mm/s RMS) pour les fréquences moyennes et en accélération (g) pour les hautes fréquences.

**Seuils d'alerte typiques (ISO 10816-3) pour machines de catégorie II (pompes, moteurs ≤ 300 kW) :**

| Zone | Vitesse vibratoire (mm/s RMS) | Évaluation |
|:---:|:---:|---|
| A | ≤ 1.8 | Bon état (nouvelle machine) |
| B | 1.8 – 4.5 | Acceptable (usure normale) |
| C | 4.5 – 11.2 | Alarme (planifier une intervention) |
| D | > 11.2 | Danger (arrêt immédiat requis) |

### 2. Thermographie Infrarouge

Technique d'imagerie thermique sans contact permettant de détecter les anomalies thermiques sur les équipements électriques et mécaniques.

**Applications en électricité :**
- Point chaud sur une borne de disjoncteur ou un contacteur → mauvais serrage (résistance de contact élevée) ou surcharge de phase.
- Échauffement dissymétrique sur les trois phases d'un moteur → déséquilibre de tension ou défaut d'isolation.
- Fusible chaud côté aval → surcharge ou court-circuit partiel en aval.

**Applications en mécanique :**
- Échauffement anormal sur un palier → manque de lubrification, frottement excessif ou désalignement.
- Température élevée d'un réducteur → niveau d'huile insuffisant ou détérioration des dentures.
- Chauffe localisée sur une courroie → glissement ou mauvais alignement des poulies.

**Critères d'évaluation thermographique :**

| Delta T (ΔT) par rapport à l'ambiante | Gravité | Action recommandée |
|:---:|:---:|---|
| < 10 °C | Normal | Aucune |
| 10 °C – 30 °C | Douteux | Planifier une inspection détaillée |
| 30 °C – 60 °C | Anormal | Intervention programmée sous 1 semaine |
| > 60 °C | Critique | Arrêt et intervention immédiate |

### 3. Analyse d'Huile et Lubrification

L'analyse d'huile permet de détecter l'usure anormale des composants internes (engrenages, roulements, cylindres) par la quantification des particules métalliques en suspension dans le lubrifiant.

| Paramètre mesuré | Indication | Seuil d'alerte typique |
|:---|---|:---:|
| Viscosité à 40 °C | Dégradation thermique ou contamination | ± 10 % de la valeur nominale |
| Taux d'eau (Karl Fischer) | Contamination par condensation ou fuite | > 0.2 % (selon application) |
| Indice d'acide (TAN) | Oxydation du lubrifiant | > 2.0 mg KOH/g |
| Particules ferreuses (PQ Index) | Usure anormale des engrenages/roulements | > 50 ppm (selon historique) |
| Comptage particulaire (ISO 4406) | Contamination solide | Code > 20/18/15 |

## Méthodologie de Résolution de Pannes (8D / 5 Pourquoi)

Face à une panne récurrente, appliquer la méthode structurée suivante :

1. **Décrire le problème** : Quoi, où, quand, ampleur, tendance. Recueillir les données objectives (alarmes, paramètres process, relevés physiques).
2. **Contenir le problème** : Action immédiate pour protéger le process (bypass, redondance, réglage dégradé) et assurer la sécurité des personnes.
3. **Analyser la cause racine** : Utiliser l'arbre des causes, les 5 Pourquoi ou le diagramme d'Ishikawa (M.O.I.S.T.E. : Méthode, Ouvrier, Inspection, Surface, Technol., Énergie).
4. **Définir et mettre en œuvre les actions correctives** : Modification du plan de maintenance, remplacement de composant, modification de conception.
5. **Vérifier l'efficacité** : Suivi des indicateurs sur une période définie (généralement 3 à 6 mois).
6. **Standardiser** : Mettre à jour les gammes de maintenance et les plans de formation.

## Pièges Courants (Common Pitfalls)

1. **Remplacement de pièces sans analyse de la cause racine :**
   - *Erreur :* Remplacer un fusible ou un relais grillé en boucle sans chercher pourquoi il a surchauffé. Le composant neuf grillera à nouveau au bout de quelques heures.
   - *Correction :* Appliquer des méthodes de diagnostic systématiques comme les **5 Pourquoi** ou le diagramme d'**Ishikawa** pour trouver la cause d'origine (ex : court-circuit sur une bobine d'électrovanne en aval, pointe de courant due à un démarrage fréquent).

2. **Surcharges de lubrification (Sur-graissage) :**
   - *Erreur :* Injecter trop de graisse dans un roulement haute vitesse lors des opérations de maintenance préventive. L'excès de graisse augmente le frottement interne, provoque une surchauffe et la destruction rapide du roulement.
   - *Correction :* Respecter scrupuleusement les quantités (en grammes, calculables via $Q = D \times B \times 0.005$ où $D$ est le diamètre extérieur et $B$ la largeur du roulement en mm) et les fréquences de graissage recommandées par le fabricant de la machine ou le logiciel de GMAO.

3. **Interventions sans consignation préalable des énergies :**
   - *Erreur :* Travailler sur un équipement en se contentant de couper le disjoncteur général sans vérifier l'absence de tension et sans purger les énergies résiduelles (pneumatique, hydraulique, gravitationnelle).
   - *Correction :* Appliquer systématiquement la procédure LOTO (Lockout/Tagout) avant toute intervention : arrêt → isolation → vérification d'absence de tension (VAT) → cadenassage → étiquetage → test de redémarrage impossible.

4. **Gammes de maintenance trop génériques :**
   - *Erreur :* Utiliser la même gamme de maintenance pour des équipements de marques ou de technologies différentes (ex : même procédure pour une pompe centrifuge et une pompe à vis).
   - *Correction :* Adapter chaque gamme en fonction des spécificités techniques de l'équipement (type de roulements, lubrifiant préconisé, couples de serrage, fréquences d'inspection).

5. **Absence de retour d'expérience (RETEX) dans la GMAO :**
   - *Erreur :* Ne pas renseigner la cause réelle de la panne et le temps passé dans la fiche d'intervention GMAO. Les données de fiabilité (MTBF, MTTR) sont alors faussées et les analyses statistiques inexploitables.
   - *Correction :* Standardiser les champs obligatoires dans les fiches de travail GMAO : code panne normalisé, cause racine (via une liste déroulante standardisée), actions réalisées, pièces changées, temps passé.

## Indicateurs Clés de Performance (KPIs)

| Indicateur | Formule | Cible typique | Fréquence de suivi |
|:---|---|:---:|:---:|
| Taux de conformité préventif | $\frac{Nb\ interventions\ réalisées}{Nb\ interventions\ planifiées} \times 100$ | > 90 % | Mensuelle |
| MTTR (Mean Time To Repair) | $\frac{\sum Temps\ de\ réparation}{Nb\ de\ pannes}$ | < 4 h (selon criticité) | Trimestrielle |
| Taux d'urgence corrective | $\frac{Nb\ interventions\ urgentes}{Nb\ total\ interventions} \times 100$ | < 15 % | Mensuelle |
| Coût de maintenance par unité produite | $\frac{Coût\ total\ maintenance}{Volume\ de\ production}$ | Référence site | Annuelle |

## Références

- **NF EN 13306** : Terminologie de la maintenance (norme européenne de référence).
- **ISO 10816-3** : Évaluation des vibrations mécaniques par mesurage sur les machines non rotatives.
- **NF EN 1593** : Essais non destructifs — Contrôle par thermographie infrarouge.
- **ISO 55000** : Management des actifs (Asset Management).
- **GMAO / CMMS** : Référentiel fonctionnel pour les systèmes informatisés de gestion de maintenance.

## Liste de vérification (Checklist)

- [ ] Les **gammes de maintenance** définissent clairement les consignes de sécurité (consignation LOTO, équipements de protection individuelle EPI requis).
- [ ] Les fréquences de rotation des machines sont renseignées et accessibles pour corréler les mesures vibratoires aux défauts mécaniques.
- [ ] Les **seuils de température admissibles** (delta T par rapport à l'ambiant) sont documentés et respectés lors des analyses thermographiques.
- [ ] Le **plan de lubrification** est à jour : références des lubrifiants, quantités, fréquences, outillage nécessaire.
- [ ] Les **instruments de mesure** (analyseur de vibrations, caméra thermique) sont étalonnés et leurs certificats de validation sont disponibles.
- [ ] Le **compte-rendu d'intervention** renseigne la cause de la panne (codifiée), les pièces changées (références et quantités) et les essais de bon fonctionnement réalisés avant remise en service.
- [ ] Les **pièces de rechange critiques** sont identifiées et leur disponibilité en stock est vérifiée périodiquement (stock de sécurité).
- [ ] Les **formations techniques** des équipes de maintenance sont à jour sur les équipements récents ou modifiés.
- [ ] Les **historiques de maintenance** dans la GMAO sont complets et permettent une analyse de tendance sur 12 mois glissants.
- [ ] Les **plans de maintenance préventive** sont revus annuellement sur la base du retour d'expérience et des évolutions réglementaires.

