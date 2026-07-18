---
name: industrial-risk-analysis-hazop
description: "Appliquer les méthodologies d'analyse de risques industriels de procédés : HAZOP (Hazard and Operability), AMDEC / FMEA, LOPA (Layer of Protection Analysis), et concevoir les barrières de sécurité (SIS, vannes de sécurité, alarmes) conformément à la réglementation SEVESO et à la norme IEC 61511."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [risk-analysis, hazop, amdec, fmea, lopa, safety, chemical-process, industrial-safety, sis, sil, pfd, bowtie, barriers, seveso, iec-61511, process-safety]
    related_skills: [pid-instrumentation, systems-engineering-sysml, atex-hazardous-areas]
    difficulty: advanced
    industry_sectors: [chemical, petrochemical, pharmaceutical, energy, oil-gas, water-treatment, food-beverage, metallurgy]
---

# Analyse des Risques Industriels de Procédés (HAZOP, AMDEC, LOPA)

## Vue d'ensemble

Cette compétence guide la mise en œuvre de méthodologies structurées pour identifier, évaluer et atténuer les risques technologiques majeurs dans les procédés industriels (usines chimiques, pharmaceutiques, pétrochimiques, énergie, métallurgie). L'analyse de risques permet de concevoir des barrières de protection fiables — physiques (soupapes de sécurité, disques de rupture) ou logiques (boucles d'arrêt d'urgence programmées dans un automate de sécurité SIS, alarmes critiques).

Les trois piliers méthodologiques sont :

1. **L'HAZOP (Hazard and Operability study)** : Analyse des dérives de procédés par l'application de mots-guides à des variables de procédé, réalisée sur la base des schémas P&ID.
2. **L'AMDEC / FMEA (Failure Mode and Effects Analysis)** : Analyse de défaillance des composants (vannes, pompes, capteurs) pour évaluer la criticité (Fréquence × Gravité × Détection).
3. **La LOPA (Layer of Protection Analysis)** : Évaluation semi-quantitative de l'efficacité des barrières de protection existantes pour déterminer si des couches de protection supplémentaires sont nécessaires.

### Contexte Réglementaire

| Réglementation / Norme | Portée | Exigence clé |
|:---|---|:---|
| **Directive SEVESO 3 (2012/18/UE)** | Sites à risques (seuils haut et bas) | Rapport de dangers, étude de sécurité, PPI |
| **IEC 61511** | Sécurité fonctionnelle des SIS (Safety Instrumented Systems) | Cycle de vie de sécurité, SIL targets, PFDavg |
| **IEC 61508** | Sécurité fonctionnelle générique | FPGA, microcontrôleurs, software safety |
| **Arrêté du 10 mai 2000 (France)** | ICPE — Prévention des accidents majeurs | Étude de dangers, maîtrise de l'urbanisation |
| **Code du Travail (France) R.4222-1** | Valeurs limites d'exposition (VLEP) atmosphériques | Protection des travailleurs |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Mener ou participer à une **étude de sécurité de procédé** sur la base de schémas P&ID (Piping & Instrumentation Diagrams).
- Identifier les **dérives potentielles** d'un fluide (surpression, absence de débit, température excessive, niveau trop haut/bas) à l'aide de mots-guides HAZOP.
- Réaliser une **analyse AMDEC (FMEA)** sur une machine ou un système pour en évaluer la criticité.
- Dimensionner des **barrières de sécurité** et évaluer leur probabilité de défaillance à la demande (**PFD**) via la méthode LOPA.
- Définir les **niveaux d'intégrité de sécurité (SIL)** requis pour les boucles d'arrêt d'urgence instrumentées (SIF).
- Rédiger un **Rapport de Dangers** ou une **Étude de Dangers** pour une installation classée (ICPE).

**Ne pas utiliser pour :**
- L'analyse des risques liés aux atmosphères explosives (utiliser `atex-hazardous-areas`).
- La gestion de la sécurité au travail (postes de travail, TMS) — utiliser `iso-45001`.
- L'analyse des risques cyber OT (utiliser `cybersecurity-iec62443`).

## 1. Méthodologie HAZOP (Hazard and Operability Study)

### Principe et Déroulement

L'HAZOP est une méthode d'analyse systématique, inductive et qualitative. Elle consiste à découper le procédé (sur schéma P&ID) en **Nœuds d'étude** (Node) — portions de l'installation (ex : ligne de transfert de réactif, réacteur, colonne de distillation) — et à appliquer des combinaisons de mots-guides et de paramètres de procédé pour imaginer toutes les dérives possibles.

### Mots-Guides et Paramètres HAZOP

| Paramètre / Variable | Pas de (No) | Plus de (More) | Moins de (Less) | Inversion (Reverse) | Autre que (Other) | Aussi bien que (As well as) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Débit** | Pas de débit | Débit excessif | Débit insuffisant | Débit inverse | Débit d'un autre fluide | Débit avec impuretés |
| **Pression** | Vide / Dépression | Surpression | Sous-pression (dépression) | – | Changement de phase | Pression non contrôlée |
| **Température** | Température ambiante | Surchauffe | Sous-refroidissement | – | Échauffement réactionnel | Dilatation anormale |
| **Niveau** | Niveau vide | Niveau trop haut | Niveau trop bas | – | Émulsion / Mousse | Condensation / Vaporisation |
| **Concentration** | Absence de réactif | Concentration excessive | Concentration insuffisante | – | Produit non conforme | Impureté / Catalyseur |
| **Réaction** | Pas de réaction | Emballement thermique | Réaction incomplète | Réaction inverse | Réaction parasite | Diffusion non contrôlée |

### Exemple d'Analyse HAZOP d'un Réacteur

| Nœud | Mots-guides | Dérive | Causes possibles | Conséquences | Barrières existantes | Actions recommandées |
|:---|---|:---|:---|---|:---|:---|
| Réacteur R-101 | Plus de + Pression | Surpression dans le réacteur | Blocage en position fermée de la vanne d'eau de refroidissement TCV-101 | Emballement thermique, rupture du réacteur, explosion, rejet toxique | Alarme haute température (TAH-101) + Soupape de sécurité PSV-102 dimensionnée | Ajouter une boucle d'arrêt de sécurité (SIS) avec capteur de pression redondant, logique de sécurité, vanne d'arrêt d'urgence |
| Réacteur R-101 | Moins de + Niveau | Niveau trop bas dans le réacteur | Fuite en pied de cuve (brèche sur piquage vidange), pompe d'alimentation défaillante | Évaporation du produit, surchauffe de la paroi (coke), réaction non maîtrisée | Alarme niveau bas (LAL-101) + consigne opérateur | Capteur de pression du manteau de refroidissement + arrêt automatique du chauffage si niveau bas |
| Ligne alimentation A-101 | Pas de + Débit | Absence d'alimentation en réactif A | Pompe P-101 arrêtée (défaut moteur), vanne manuelle fermée, ligne bouchée | Arrêt de réaction, perte de production, dérive qualité | Alarme débit bas (FAL-101) | Redondance de pompe P-101B + détection de colmatage |

### Informations Requises pour une Session HAZOP

- P&ID à jour de l'installation (schémas tuyauterie et instrumentation).
- Description du procédé (PFD — Process Flow Diagram).
- Fiches de données de sécurité des substances (FDS).
- Rapport des études de sécurité antérieures.
- Plan de masse et d'implantation des équipements.
- Liste des alarmes et des consignes opératoires.

## 2. Méthode LOPA (Layer of Protection Analysis)

La LOPA est une approche semi-quantitative qui permet d'évaluer si les barrières de protection existantes (telles que définies dans la méthode de l'**oignon de protection** / Layer of Protection Onion) sont suffisantes pour réduire la fréquence d'un événement redouté ($f_{event}$) en dessous d'un seuil tolérable.

### Principe de Calcul

$$f_{event} = f_{cause} \times \prod_{i=1}^{n} PFD_{barrière\ i}$$

Où :
- $f_{cause}$ : Fréquence annuelle d'initiation de la cause (ex : 1 panne/an pour une vanne régulatrice standard).
- $PFD$ : Probabilité de Défaillance à la demande de la barrière (Probability of Failure on Demand).
- L'objectif est que $f_{event} < f_{tolérable}$ (déterminée par la grille d'acceptabilité du site).

### Exemple de Dimensionnement LOPA : Surpression du Réacteur R-101

| Niveau de l'oignon | Barrière | Type | $PFD$ (typique) | Contribution à la réduction |
|:---:|:---|---|:---:|:---:|
| 1 | Conception intrinsèque (facteurs de sécurité, section des canalisations) | Passive | 0,1 | ×10 |
| 2 | Contrôle de base (régulation PID, alarmes opérateur) | Logicielle / Humaine | 0,1 | ×10 |
| 3 | Alarmes critiques et intervention opérateur (avec procédure) | Humaine (procédurale) | 0,1 | ×10 |
| 4 | Système Instrumenté de Sécurité (SIS) — Boucle SIL 2 | Automate de sécurité | 0,01 | ×100 |
| 5 | Protection physique passive (soupape PSV, disque de rupture) | Mécanique | 0,01 | ×100 |
| 6 | Protection physique active (évents, murs anti-souffle, confinement) | Mécanique / Civil | 0,1 – 0,01 | ×10–100 |
| 7 | Intervention d'urgence (pompiers, évacuation, plan d'urgence) | Organisationnelle | 0,1 | ×10 |

**Résultat de l'exemple :** Si $f_{cause} = 0,1$ /an (une cause tous les 10 ans) et que les barrières 1 à 5 sont en place :
$$f_{event} = 0,1 \times 0,1 \times 0,1 \times 0,1 \times 0,01 \times 0,01 = 1 \times 10^{-8} \text{ / an}$$
Ce niveau de risque est généralement acceptable pour un événement de type surpression / explosion.

### Représentation Graphique (Bow-Tie / Nœud Papillon)

```text
  [Événement Initiateur : Fuite de solvant dans le réacteur]
                     │
                     ▼
   ════ Barrière 1 : Conduite d'opérations (alarmes IHM, consignes) [PFD ~ 0.1] ════
                     │ (si échec)
                     ▼
   ════ Barrière 2 : SIS — Automate de sécurité (redondant 2oo3) [PFD ~ 0.001] ════
                     │ (si échec)
                     ▼
   ════ Barrière 3 : Sécurité mécanique (Soupape PSV, Disque de rupture) [PFD ~ 0.01] ════
                     │ (si échec)
                     ▼
          [Accident Majeur : Explosion avec projection]
```

## 3. AMDEC / FMEA (Analyse des Modes de Défaillance et de leurs Effets)

### Grille de Cotation

| Indice de Gravité ($G$) | Critère | Indice de Fréquence ($F$) | Occurrence | Indice de Détection ($D$) | Détectabilité |
|:---:|---|:---:|---|:---:|---|
| 1 | Négligeable (aucun effet) | 1 | Très rare (> 5 ans) | 1 | Très facile à détecter (alarme directe) |
| 2 | Mineure (intervention simple) | 2 | Rare (1 – 5 ans) | 2 | Facile (test visuel quotidien) |
| 3 | Significative (arrêt < 1h) | 3 | Occasionnelle (6 mois – 1 an) | 3 | Moyennement facile (test hebdomadaire) |
| 4 | Critique (arrêt > 1h, sécurité) | 4 | Fréquente (1 – 6 mois) | 4 | Difficile (détection indirecte) |
| 5 | Catastrophique (explosion, blessure) | 5 | Très fréquente (< 1 mois) | 5 | Indétectable (pas de moyen de détection) |

**Criticité $C = F \times G \times D$** :
- $C \geq 100$ : Action corrective immédiate (redesign nécessaire).
- $50 \leq C < 100$ : Action planifiée dans l'année.
- $20 \leq C < 50$ : Surveillance renforcée, maintenance préventive.
- $C < 20$ : Acceptable, suivi normal.

## Pièges Courants (Common Pitfalls)

1. **Prise en compte de barrières non indépendantes (Non-IPL) :**
   - *Erreur :* Compter la boucle de régulation de niveau standard et la boucle de sécurité de niveau haut comme deux barrières indépendantes dans la LOPA, alors qu'elles partagent le même capteur physique. Si ce capteur tombe en panne, les deux barrières échouent en même temps (défaillance de mode commun).
   - *Correction :* Pour être classée comme **IPL** (Independent Protection Layer), une barrière doit être totalement indépendante du scénario initiateur et des autres barrières : capteur séparé, logique séparée, actionneur dédié, alimentation distincte. Vérifier l'indépendance à chaque étape de la LOPA.

2. **Études HAZOP trop vagues ou globales :**
   - *Erreur :* Prendre l'intégralité d'un atelier de distillation comme un unique nœud HAZOP, ce qui conduit à oublier de nombreux scénarios de dérive sur les lignes de recirculation, de purge, de soutirage ou d'évent.
   - *Correction :* Découper rigoureusement le système en nœuds élémentaires basés sur des fonctions physiques simples (ex : alimentation en réactif, chauffe, condensation, reflux, soutirage de fond, purge de gaz incondensables). Chaque nœud doit correspondre à une fonction unique.

3. **Oubli des scénarios de démarrage et d'arrêt :**
   - *Erreur :* Se concentrer uniquement sur les situations de fonctionnement normal (régime établi) dans l'étude HAZOP, sans analyser les phases transitoires (démarrage à froid, arrêt d'urgence, reprise après arrêt).
   - *Correction :* L'étude HAZOP doit inclure explicitement les modes de fonctionnement **normal**, **anormal** (démarrage, arrêt, dégradé) et **urgence** (perte d'utilités : électricité, air comprimé, vapeur, eau de refroidissement).

4. **Données PFD / fiabilité insuffisantes dans la LOPA :**
   - *Erreur :* Affecter une valeur PFD arbitraire optimiste à une barrière sans données de fiabilité solides (ex : supposer un PFD de 0,001 pour une soupape de sécurité sans connaître son historique de maintenance ni sa date de certification).
   - *Correction :* Utiliser les données PFD des bases de données de fiabilité industrielles reconnues (OREDA, exida, SINTEF) ou les valeurs par défaut conservatrices de la norme IEC 61511. Prendre en compte les intervalles de test périodique (Proof Test) dans le calcul du PFDavg.

## Références

- **IEC 61511:2016** (Ed. 2) : Sécurité fonctionnelle — Systèmes instrumentés de sécurité pour le secteur des industries de procédé.
- **IEC 61508:2010** (Ed. 2) : Sécurité fonctionnelle des systèmes électriques/électroniques/électroniques programmables.
- **CCPS (Center for Chemical Process Safety)** — *Guidelines for Hazard Evaluation Procedures* (3e édition, 2008).
- **CCPS — Layer of Protection Analysis* (LOPA), 2001.
- **Directive SEVESO 3** (2012/18/UE) : Maîtrise des dangers liés aux accidents majeurs impliquant des substances dangereuses.
- **INERIS** — Guides techniques pour la réalisation des études de dangers.
- **OREDA** (Offshore Reliability Data) — Base de données de fiabilité pour les équipements de procédé.
- **exida SIL Suite** — Outil logiciel de calcul SIL et PFD.

## Liste de vérification (Checklist)

- [ ] **L'étude HAZOP** couvre l'intégralité des lignes de procédé représentées sur les schémas P&ID, y compris les utilités, les purges, les évents, les lignes de recirculation et les by-pass.
- [ ] Les **barrières de protection** comptabilisées dans l'analyse LOPA sont des IPL (Independent Protection Layers) : capteurs séparés, logique séparée, actionneurs dédiés, pas de mode commun de défaillance.
- [ ] La **probabilité de défaillance à la demande (PFD)** affectée à chaque barrière est étayée par des données de fiabilité fiables (bases OREDA, exida) ou des certifications (SIL) et les intervalles de proof test sont documentés.
- [ ] Des **alarmes critiques** ont été définies pour chaque scénario HAZOP identifié. Chaque alarme nécessite une action opérateur claire avec un temps de réaction documenté et suffisant (> 10-15 minutes pour les alarmes de procédé).
- [ ] Les **phases de démarrage** et d'arrêt ont été incluses dans l'étude (scénarios transitoires).
- [ ] Les **modes de défaillance** (AMDEC / FMEA) sont identifiés pour les composants critiques : pompes, vannes de régulation, capteurs redondants, actionneurs de sécurité.
- [ ] Les **scénarios de perte d'utilités** (électricité, air comprimé, vapeur, eau de refroidissement, azote) ont été analysés.
- [ ] Le **niveau SIL (Safety Integrity Level)** a été déterminé pour chaque fonction instrumentée de sécurité (SIF) selon la méthode LOPA ou la grille de risque.
- [ ] Les **intervalles de test** (Proof Test Interval) des barrières SIL sont définis et intégrés au plan de maintenance préventive.
- [ ] Les **conclusions et actions** de l'étude HAZOP sont tracées, suivies jusqu'à leur clôture (fiche d'action avec responsable, échéance, statut) et une revue de suivi est programmée dans l'année.

