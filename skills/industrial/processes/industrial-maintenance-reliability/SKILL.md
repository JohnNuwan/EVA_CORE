---
name: industrial-maintenance-reliability
description: "Appliquer l'ingénierie de fiabilité des équipements industriels, déployer la démarche TPM (Total Productive Maintenance), analyser les modes de défaillance via la RCM (Reliability Centered Maintenance) et calculer les indicateurs FMD (MTBF, MTTR, Disponibilité, Loi de Weibull)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [reliability, tpm, rcm, fmd, mtbf, mttr, availability, maintenance-engineering, weibull, reliability-analysis, fmeca, oee, asset-management]
  helios:
    related_skills: [industrial-maintenance-preventive, oee-performance, cmms-gmao-integration]
    difficulty: advanced
    industry_sectors: [manufacturing, chemical, pharmaceutical, energy, oil-gas, automotive, aerospace]
---

# Ingénierie de Maintenance & Fiabilité Industrielle (TPM / RCM / FMD)

## Vue d'ensemble

Cette compétence guide l'amélioration de la disponibilité et de la performance des équipements de production en s'appuyant sur les démarches structurées d'ingénierie de maintenance : la **TPM (Total Productive Maintenance)**, la **RCM (Reliability Centered Maintenance)** et l'analyse de la **Sûreté de Fonctionnement / FMD** (Fiabilité, Maintenabilité, Disponibilité, Sécurité). L'objectif fondamental est d'optimiser le plan de maintenance en se concentrant sur les équipements critiques et de maximiser le Taux de Rendement Synthétique (TRS / OEE) des lignes de production.

### Contexte : Pourquoi la Fiabilité ?

Dans l'industrie moderne, les objectifs de production (rendement, qualité, délais) sont directement liés à la disponibilité des équipements. Une approche purement corrective ou systématique ne suffit plus : il faut déployer une stratégie de maintenance **basée sur la criticité et la fiabilité** pour :

- Réduire les arrêts non planifiés (coût caché majeur).
- Prolonger la durée de vie des actifs.
- Optimiser les coûts de maintenance (ne pas sur-maintenir ni sous-maintenir).
- Anticiper les défaillances avant qu'elles n'affectent la production.
- Satisfaire aux exigences des certifications ISO 55001 (Asset Management).

### Les 4 Piliers de la Démarche Fiabilité

1. **La TPM (Total Productive Maintenance)** : Impliquer tous les métiers (production, maintenance, méthodes) dans l'amélioration continue de la performance des équipements.
2. **La RCM (Reliability Centered Maintenance)** : Déterminer les actions de maintenance optimales en fonction des modes de défaillance, de leur criticité et des conséquences sur la production et la sécurité.
3. **Le FMD (Fiabilité, Maintenabilité, Disponibilité)** : Mesurer objectivement la performance des équipements via des indicateurs statistiques.
4. **L'AMDEC (Analyse des Modes de Défaillance, de leurs Effets et de leur Criticité)** : Identifier systématiquement les défaillances potentielles pour prioriser les actions.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Calculer les **indicateurs FMD** : MTBF (Mean Time Between Failures), MTTR (Mean Time To Repair) et la Disponibilité opérationnelle à partir de données de GMAO.
- Structurer un **plan de maintenance basé sur la fiabilité (RCM)** en identifiant les modes de défaillance, leurs effets et les actions de maintenance appropriées.
- Déployer les **piliers de la TPM** (maintenance autonome par les opérateurs, amélioration ciblée, élimination des pertes, maintenance planifiée).
- Mener une **analyse statistique de durée de vie de composants** à l'aide de la loi de Weibull (estimation du $B_{10}$ life).
- Réaliser une **AMDEC Processus ou Machine** (FMEA / FMECA) pour évaluer la criticité des modes de défaillance.

**Ne pas utiliser pour :**
- Les diagnostics de maintenance opérationnelle de terrain (analyse vibratoire, thermographie) qui relèvent de la compétence `industrial-maintenance-preventive`.
- La gestion administrative des arrêts de maintenance (planning détaillé, ordonnancement).

## Calcul des Indicateurs FMD (Fiabilité, Maintenabilité, Disponibilité)

### Représentation des Temps

```text
       |<─────────────────────── Temps Total de Surveillance ───────────────────────>|
       │                                                                             │
       ├───────────────┤               ├───────────────────┤               ├─────────┤
       │   En marche   │   En Panne    │     En marche     │   En Panne    │En marche│
       │     (MUT)     │     (MDT)     │       (MUT)       │     (MDT)     │  (MUT)  │
       └───────────────┴───────────────┴───────────────────┴───────────────┴─────────┘
                       │<─────────────>|                   │<─────────────>│
                             TTR                                 TTR
```

### 1. MTBF (Mean Time Between Failures)

Indique la **Fiabilité** de l'équipement, c'est-à-dire le temps moyen de fonctionnement sans panne :

$$MTBF = \frac{\sum Temps\ de\ bon\ fonctionnement\ (MUT)}{Nombre\ de\ pannes}$$

- Un MTBF élevé indique un équipement fiable.
- Le MTBF n'inclut **pas** les arrêts programmés pour maintenance préventive.

### 2. MTTR (Mean Time To Repair)

Indique la **Maintenabilité**, c'est-à-dire la facilité et la rapidité de réparation :

$$MTTR = \frac{\sum Temps\ d'arrêt\ pour\ dépannage\ (TTR)}{Nombre\ de\ pannes}$$

- Un MTTR faible indique un équipement facile à réparer (bonne accessibilité, pièces de rechange disponibles, documentation claire).
- Le MTTR inclut le temps de diagnostic, de démontage, de remplacement, de remontage et de test.

### 3. Disponibilité

La **Disponibilité Intrinsèque** ($D_i$) ne prend en compte que les pannes fortuites :

$$D_i = \frac{MTBF}{MTBF + MTTR}$$

La **Disponibilité Opérationnelle** ($D_o$) prend en compte **tous** les arrêts (pannes + maintenance préventive + logistiques + organisationnels) :

$$D_o = \frac{Temps\ Total\ d'Exploitation - Temps\ d'Arrêt\ Total}{Temps\ Total\ d'Exploitation}$$

| Valeur de $D$ | Niveau de performance |
|:---:|:---:|
| > 98 % | Excellence |
| 95 – 98 % | Bon |
| 90 – 95 % | Acceptable |
| < 90 % | Critique (actions nécessaires) |

## Analyse de Durée de Vie par la Loi de Weibull

La loi de Weibull à 2 ou 3 paramètres est l'outil statistique le plus utilisé pour modéliser les défaillances d'équipements mécaniques et électroniques.

$$R(t) = e^{-(t/\eta)^\beta}$$

Où :
- $R(t)$ : Probabilité de survie (fiabilité) à l'instant $t$.
- $\eta$ (Eta) : Paramètre d'échelle (durée de vie caractéristique, correspondant à 63,2 % de défaillances).
- $\beta$ (Beta) : Paramètre de forme qui décrit le comportement de défaillance :
  - $\beta < 1$ : Mortalité infantile (défauts de jeunesse).
  - $\beta = 1$ : Défaillances aléatoires (période de vie utile).
  - $\beta > 1$ : Défaillances par usure (fin de vie).

**Interprétation du $B_{10}$ Life :** Temps au bout duquel 10 % de la population d'un composant a défailli. Utilisé pour définir les intervalles de maintenance préventive optimale.

| Application | $\beta$ typique | $B_{10}$ Life (exemple) |
|:---|---:|:---|
| Roulements à billes standard | 1,5 – 2,5 | 20 000 heures |
| Moteurs électriques asynchrones | 2,0 – 3,0 | 40 000 heures |
| Composants électroniques (alimentation) | 0,8 – 1,2 (période utile) | 80 000 heures |
| Courroies de transmission | 2,5 – 4,0 | 5 000 heures |

## Méthodologie RCM (Reliability Centered Maintenance)

La RCM est une approche structurée en 7 étapes :

1. **Sélection du système et collecte des données** : Identifier l'équipement, recueillir les schémas, les données de fiabilité, l'historique des pannes.
2. **Définition des fonctions** : Lister les fonctions principales et secondaires de l'équipement (ex : fonction = transférer un fluide à 10 m³/h, pression 5 bar).
3. **Identification des défaillances fonctionnelles** : Comment l'équipement peut cesser de remplir ses fonctions.
4. **Analyse des modes de défaillance (AMDEC / FMECA)** : Pour chaque défaillance, identifier les causes et les effets potentiels (grille de criticité Fréquence x Gravité x Détection).
5. **Évaluation des conséquences** : Classer les conséquences (sécurité, environnement, production, coûts).
6. **Sélection des tâches de maintenance** : Choisir la stratégie (préventive systématique, conditionnelle, détective, corrective) en fonction du type de défaillance.
7. **Implémentation et optimisation** : Déployer le plan de maintenance RCM et optimiser les intervalles sur la base du retour d'expérience.

### Grille de Criticité AMDEC (FMEA)

| Indice de Gravité ($G$) | Indice de Fréquence ($F$) | Indice de Détection ($D$) |
|:---:|:---:|:---:|
| 1 = Négligeable | 1 = Très rare (> 5 ans) | 1 = Très facile à détecter |
| 2 = Mineure | 2 = Rare (1 – 5 ans) | 2 = Facile |
| 3 = Significative | 3 = Occasionnelle (6 mois – 1 an) | 3 = Moyennement facile |
| 4 = Critique | 4 = Fréquente (1 – 6 mois) | 4 = Difficile |
| 5 = Catastrophique | 5 = Très fréquente (< 1 mois) | 5 = Indétectable |

La **Criticité** $C = F \times G \times D$. Seuils typiques d'action :
- $C > 60$ : Action corrective immédiate requise.
- $30 < C \leq 60$ : Action planifiée dans l'année.
- $C \leq 30$ : Surveillance simple.

## Les 8 Piliers de la TPM

| Pilier | Description | Indicateur clé |
|:---|---|:---:|
| 1. Amélioration ciblée | Élimination des 16 grandes pertes (pannes, réglages, micro-arrêts, défauts qualité) | TRS / OEE |
| 2. Maintenance autonome | Nettoyage, inspection, serrage, lubrification par les opérateurs de production | Taux de participation |
| 3. Maintenance planifiée | Organisation des interventions préventives et prévisionnelles | Respect du planning |
| 4. Formation et compétences | Développement des compétences techniques des équipes | Plan de formation |
| 5. Gestion de la conception | Prise en compte de la maintenabilité et de la fiabilité dès la conception | AMDEC conception |
| 6. Gestion de la qualité | Réduction des défauts qualité liés aux équipements | Taux de rebut |
| 7. TPM administratif | Optimisation des processus supports (logistique, approvisionnements) | Productivité administrative |
| 8. Sécurité, santé, environnement | Zéro accident, zéro pollution liés aux équipements | Taux de fréquence |

## Pièges Courants (Common Pitfalls)

1. **Calculer la disponibilité sans exclure les arrêts programmés :**
   - *Erreur :* Inclure les temps d'arrêt pour maintenance préventive planifiée ou les arrêts de production (ex : week-ends, nettoyage) dans le calcul du MTTR. Cela fausse complètement l'analyse de la maintenabilité des équipements.
   - *Correction :* Distinguer la **Disponibilité Intrinsèque** (qui ne prend en compte que les pannes fortuites) de la **Disponibilité Opérationnelle** (qui prend en compte tous les arrêts). Le MTTR et le MTBF doivent s'appuyer uniquement sur les arrêts non programmés.

2. **TPM imposée sans impliquer les opérateurs de production :**
   - *Erreur :* Rédiger des fiches de maintenance autonome (inspections quotidiennes, serrages, nettoyage) et les imposer aux opérateurs de production sans formation préalable. Les inspections seront mal faites et perçues comme une contrainte.
   - *Correction :* Co-construire les standards de nettoyage et d'inspection avec les opérateurs lors de chantiers pilotes TPM pour favoriser l'appropriation de leur machine. Désigner des leaders TPM par secteur.

3. **Confondre RCM et AMDEC :**
   - *Erreur :* Considérer que faire une AMDEC (analyse de défaillances) équivaut à faire une RCM complète. La RCM inclut l'AMDEC mais va beaucoup plus loin en intégrant la sélection des tâches de maintenance et l'analyse des conséquences sur la production.
   - *Correction :* Utiliser l'AMDEC comme un outil d'entrée de la démarche RCM, pas comme un résultat final. Compléter chaque mode de défaillance par une décision de maintenance explicite.

4. **Données de pannes insuffisantes pour les calculs statistiques :**
   - *Erreur :* Tenter de calculer un MTBF ou une loi de Weibull avec seulement 2 ou 3 événements de panne. Les résultats ne sont pas statistiquement significatifs.
   - *Correction :* Un minimum de 10 à 15 événements de défaillance est recommandé pour une analyse Weibull fiable. En deçà, utiliser des données constructeur ou des retours d'expérience de sites similaires.

## Références

- **NF EN 13306** : Terminologie de la maintenance.
- **IEC 60300-3-11** : Gestion de la sûreté de fonctionnement — Guide d'application de la RCM.
- **SAE JA1011** : Evaluation Criteria for Reliability-Centered Maintenance (RCM) Processes.
- **ISO 55000 / 55001** : Gestion des actifs (Asset Management).
- **AIAG & VDA FMEA Handbook** (edition 1, 2019) : Référence pour l'AMDEC.
- **Loi de Weibull** : Norme IEC 61649 (Goodness-of-fit tests and confidence intervals for Weibull distributed data).

## Liste de vérification (Checklist)

- [ ] Les calculs de **MTBF et MTTR** excluent bien les temps d'arrêt programmés (changement d'équipe, maintenance préventive planifiée).
- [ ] Les **modes de défaillance** identifiés en RCM sont associés à des actions de maintenance explicites (préventive, conditionnelle, corrective ou modification de conception).
- [ ] Les **données de pannes** (date de début, date de fin, cause racine codifiée) sont enregistrées rigoureusement dans la GMAO pour alimenter les calculs FMD.
- [ ] Le calcul de la **disponibilité opérationnelle** est cohérent avec le calcul du Taux de Disponibilité utilisé dans le TRS (OEE).
- [ ] L'**analyse AMDEC** (FMEA) est réalisée avec une grille de criticité homogène sur l'ensemble du site.
- [ ] Les **intervalles de maintenance** préventive sont justifiés par des données statistiques (MTBF, Weibull $B_{10}$) ou des préconisations constructeur validées par l'expérience.
- [ ] La **maintenance autonome** TPM est déployée avec des standards visuels, une formation des opérateurs et un suivi d'audit périodique.
- [ ] Les **coûts de maintenance** (main d'œuvre + pièces + sous-traitance) sont suivis par équipement et rapportés au coût de remplacement à neuf (ratio $Maintenance / Valeur\ à\ Neuf$).
- [ ] Un **retour d'expérience (RETEX)** structuré est organisé annuellement pour réviser les plans de maintenance RCM.
- [ ] Les **outils de fiabilité** (Weibull, AMDEC, analyse des causes racines) sont maîtrisés par au moins un référent technique par atelier.

