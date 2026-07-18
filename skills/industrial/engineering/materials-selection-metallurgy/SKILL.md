---
name: materials-selection-metallurgy
description: "Sélectionner les matériaux industriels (aciers, inox, alliages d'aluminium, plastiques) selon les contraintes de fonctionnement (corrosion, usure, température) et préconiser les traitements thermiques."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [materials, metallurgy, steel, corrosion, heat-treatment, mechanical-engineering, industrial-materials, material-science]
    related_skills: [fea-structural-analysis, cad-bom-automation, industrial-piping-vessels]
---

# Choix des Matériaux et Métallurgie Appliquée

## Vue d'ensemble

Cette compétence guide la sélection rationnelle des matériaux métalliques et polymères en ingénierie industrielle. Le choix d'un matériau pour une pièce ou un équipement engage durablement les performances, la sécurité et le coût total de possession d'une installation.

Le processus de sélection doit concilier des **propriétés mécaniques** (limite d'élasticité $R_e$, résistance à la traction $R_m$, ténacité $K_{IC}$, dureté), des **propriétés physiques** (densité $\rho$, conductivité thermique $\lambda$, coefficient de dilatation $\alpha$), des **contraintes environnementales** (résistance à la corrosion chimique, tenue en température, abrasion, fatigue), et des **critères de fabricabilité** (usinabilité, soudabilité, formabilité) — le tout sous contrainte de **coût** et de **disponibilité** sur le marché.

Cette compétence est conçue pour être actionnée par l'agent Helios lorsque l'utilisateur exprime un besoin lié à la spécification, l'analyse, le diagnostic ou l'optimisation du choix de matériaux dans un contexte industriel.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Sélectionner un type d'acier ou d'alliage pour une pièce mécanique subissant de fortes contraintes (arbre de transmission, engrenage, cuve sous pression).
- Choisir un matériau résistant à la corrosion dans un environnement donné (inox 304L vs 316L, Hastelloy, titane, PTFE, PVDF).
- Recommander un traitement thermique de durcissement (trempe, revenu, cémentation, nitruration, carbonitruration) ou de recuit.
- Analyser un cas de rupture en service (rupture fragile, fatigue, corrosion sous contrainte, usure adhésive ou abrasive).
- Dimensionner ou vérifier l'adéquation matière / procédé dans un contexte de modification de ligne ou de changement de fournisseur.
- Rédiger un cahier des charges matière pour un équipement neuf.

---

## Fondamentaux de la métallurgie

### Diagramme Fer-Carbone et microstructures

Le comportement des aciers est régi par leur teneur en carbone et les traitements thermiques appliqués :

| % Carbone | Désignation usuelle | Microstructure typique (état recuit) | Propriétés |
|:---------|:--------------------|:-----------------------------------|:----------|
| 0.05 – 0.25 % | Acier doux (bas carbone) | Ferrite + perlite | Très ductile, soudable, faible résistance |
| 0.25 – 0.60 % | Acier mi-dur (moyen carbone) | Ferrite + perlite (proportion croissante) | Bon équilibre résistance/ductilité |
| 0.60 – 1.50 % | Acier dur (haut carbone) | Perlite + cémentite | Haute résistance, faible ductilité |
| > 0.10 % + Cr/Mo | Acier allié | Martensite après trempe | Très haute résistance, ténacité contrôlée |

### Notions essentielles :

- **Limite d'élasticité ($R_e$)** : Contrainte à partir de laquelle la déformation devient permanente. Critère de dimensionnement principal (règle des 2/3 de $R_e$ pour les contraintes admissibles).
- **Résilience ($K_V$)** : Énergie absorbée lors d'un choc, mesurée par essai Charpy. Critique pour les structures exposées aux chocs ou au froid (transition ductile-fragile).
- **Dureté** : Résistance à la pénétration (échelles Brinell HB, Rockwell HRC, Vickers HV). Corrélée à la résistance à l'usure.
- **Ténacité ($K_{IC}$)** : Résistance à la propagation d'une fissure. Essentielle pour les pièces sous pression ou en fatigue.

---

## Guide de sélection rapide des matériaux industriels

### Aciers de construction et de traitement

| Désignation | Norme EN | Propriétés clés | Applications typiques |
|:-----------|:---------|:----------------|:---------------------|
| S235 / S355 | EN 10025 | Bon marché, soudable, $R_e$ = 235/355 MPa | Châssis, charpentes, supports statiques |
| S460 / S690QL | EN 10025 / EN 10083 | Haute résistance soudable | Structures mobiles, grues, engins de chantier |
| 42CrMo4 | EN 10083-3 | $R_e$ > 900 MPa après trempe/revenu | Arbres de transmission, engrenages, bielles |
| 16MnCr5 | EN 10084 | Acier de cémentation | Pignons, bagues, pièces cémentées-trempées |
| C45E (XC45) | EN 10083-2 | Acier mi-dur non allié | Vis, axes, pièces d'usure générale |
| 100Cr6 | EN ISO 683-17 | Acier à roulements | Billes, rouleaux, bagues de roulements |

### Aciers inoxydables

| Désignation | Norme EN | Propriétés clés | Applications typiques |
|:-----------|:---------|:----------------|:---------------------|
| 304L (1.4307) | EN 10088-2 | Bonne tenue corrosion générale, alimentaire | Cuves, tuyauteries d'eau, agroalimentaire |
| 316L (1.4404) | EN 10088-2 | Excellente tenue aux chlorures (Mo 2%) | Milieux marins, chimie, pharmacie |
| 904L (1.4539) | EN 10088-2 | Très haute résistance aux acides | Usines chimiques, pétrochimie |
| 2205 (1.4462) | EN 10088-2 | Duplex : haute résistance + bonne tenue corrosion | Structures offshore, papeterie, chlore |
| 17-4PH (1.4542) | EN 10088-3 | Inox martensitique durci par précipitation | Pièces de vannes, arbres de pompes |

### Alliages non ferreux et spéciaux

| Matériau | Propriétés clés | Applications typiques |
|:---------|:----------------|:---------------------|
| Aluminium 6061-T6 | Bonne usinabilité, soudable, léger | Châssis mobiles, outillages |
| Aluminium 7075-T6 | Très haute résistance (aéronautique) | Pièces très sollicitées, moules rapides |
| Bronze CuSn10 | Résistance à la corrosion + bon glissement | Bagues, paliers, engrenages |
| Hastelloy C-276 | Résistance exceptionnelle aux acides chauds | Réacteurs chimiques, scrubbers |
| Titane Ti-6Al-4V | Très haute résistance spécifique, biocompatible | Aéronautique, implants, chimie agressive |
| PTFE (Téflon) | Inerte chimiquement, glissant, haute température | Joints, garnitures, cuves acides |
| PVDF | Résistant aux UV et aux solvants | Revêtements chimiques, gaines de câbles |

---

## Traitements thermiques des aciers

### Trempe + Revenu

**Principe :** Chauffage au-dessus de la température d'austénitisation ($A_3$) suivi d'un refroidissement rapide (dans l'eau ou l'huile) pour former de la martensite, structure très dure mais fragile. Le revenu (réchauffage contrôlé entre 150 °C et 650 °C) restitue de la ténacité.

| Revenu | Température | Effet |
|:------|:-----------|:------|
| Bas (150-300 °C) | Grande dureté, faible ductilité | Outils de coupe |
| Moyen (350-500 °C) | Bon équilibre résistance/ténacité | Arbres, bielles |
| Haut (550-650 °C) | Ductilité élevée, résistance modérée | Pièces de structure épaisses |

**Paramètres critiques :** vitesse de refroidissement (milieu de trempe), dimension de la pièce (trempabilité), maintien en température uniforme.

### Cémentation et Nitruration

**Principe :** Durcissement **superficiel** uniquement par enrichissement en carbone (cémentation) ou en azote (nitruration) de la peau de la pièce. Le cœur reste tenace pour absorber les chocs, tandis que la surface résiste à l'usure.

| Traitement | Profondeur de couche | Dureté HRC | Application |
|:-----------|:-------------------|:-----------|:------------|
| Cémentation (925 °C) + trempe | 0.3 – 1.5 mm | 58 – 62 HRC | Engrenages, pignons, arbres à cames |
| Nitruration gazeuse (520 °C) | 0.1 – 0.6 mm | > 65 HRC (nitrures) | Chemises de cylindres, vannes |
| Carbonitruration | 0.2 – 0.8 mm | 58 – 64 HRC | Petites pièces de transmission |

**Avantage de la nitruration :** pas de refroidissement brutal, donc pas de déformation de la pièce.

### Recuit

| Type de recuit | Température | Effet |
|:--------------|:-----------|:------|
| Recuit complet | $A_3$ + 50 °C | Supprime toute l'écrouissage, structure équilibrée |
| Recuit de normalisation | $A_3$ + 50 °C | Affine le grain, homogénéise la structure |
| Recuit de détensionnement | 550 – 650 °C | Élimine les contraintes résiduelles de soudage ou d'usinage |
| Recuit de globulisation | $A_1$ ± 20 °C | Améliore l'usinabilité des aciers à haut carbone |

---

## Modes de défaillance liés aux matériaux

### Rupture fragile

**Caractéristiques :** Rupture brutale sans déformation plastique préalable, surface plane et cristalline (sans striction). Favorisée par : basses températures ($T < T_{transition}$), concentrations de contraintes (entailles), épaisseurs fortes, matériaux fragiles.

**Correction :** Choisir un acier avec une température de transition ductile-fragile inférieure à la température minimale de service. Utiliser des aciers calmés à grains fins (ex : S355NL).

### Fatigue

**Caractéristiques :** Rupture progressive sous l'effet de contraintes cycliques inférieures à la limite élastique. La surface de rupture montre des *stries de fatigue* puis une zone de rupture finale brutale.

**Correction :** Éliminer les entailles et les rayures (concentration de contrainte), appliquer une précontrainte de compression superficielle (grenaillage de précontrainte). Choisir un matériau avec une limite d'endurance élevée ($\sigma_D \approx 0.5 R_m$ pour les aciers).

### Corrosion sous contrainte (CSC / SCC)

**Caractéristiques :** Fissuration intergranulaire ou transgranulaire en présence simultanée d'une contrainte de traction et d'un environnement corrosif spécifique (ex : chlorures sur inox 304). Phénomène dangereux car difficilement détectable avant rupture.

**Correction :** Supprimer la contrainte résiduelle (détensionnement), choisir une nuance résistante à la CSC (904L, duplex), abaisser la température, réduire la concentration d'espèces agressives.

### Corrosion galvanique

Voir section Pièges Courants ci-dessous.

---

## Pièges Courants (Common Pitfalls)

### 1. Le couple galvanique (corrosion bimétallique)

**Erreur :** Assembler directement des pièces en aluminium (ou acier au carbone) et en acier inoxydable dans un milieu humide. La différence de potentiel électrique (jusqu'à 0,5 V) provoque un courant galvanique qui corrode accélérée du métal le moins noble (anode). La corrosion peut atteindre plusieurs mm/an en milieu salin.

**Correction :** Insérer un isolant électrique entre les deux métaux : rondelles plastiques, gaines isolantes, mastic d'étanchéité, ou traitement de surface (anodisation, phosphatation). Si l'isolation est impossible, remplacer l'un des métaux par un alliage compatible ou prévoir une anode sacrificielle.

### 2. Utilisation d'inox non "L" pour le soudage

**Erreur :** Souder de l'inox 304 ou 316 standard (teneur en carbone $> 0,03\%$). La chaleur de la soudure dans la zone affectée thermiquement (ZAT, de 450 à 850 °C) provoque la précipitation de carbures de chrome aux joints de grains. La zone autour des carbures se retrouve appauvrie en chrome libre (passivation perdue), rendant la soudure vulnérable à la corrosion intergranulaire.

**Correction :** Utiliser exclusivement des nuances à bas carbone marquées **"L"** (Low Carbon, ex : 304L, 316L) ou stabilisées au titane (321) ou au niobium (347) pour toutes les structures soudées. Respecter les recommandations de vitesse de refroidissement post-soudure.

### 3. Négliger la température de transition ductile-fragile

**Erreur :** Installer une structure en acier standard (ex : S235JR) en extérieur dans une région froide ($T < -20 °C$). Sous l'effet d'un choc mécanique (chute de charge, séisme modéré), la rupture fragile survient à une contrainte bien inférieure à la limite élastique, pouvant provoquer la ruine de l'ouvrage.

**Correction :** Spécifier des aciers avec une résilience Charpy garantie à basse température : nuance **NL** (ex : S355NL, garanti à -50 °C) ou **ML** (garanti à -20 °C). Vérifier la température minimale de service dans le cahier des charges.

### 4. Oublier l'usinabilité dans le coût global

**Erreur :** Choisir un acier inoxydable 316L pour une pièce complexe nécessitant un usinage intensif (fraisage 3D, perçages profonds). L'inox 316L s'écrouit rapidement, colle à l'outil et nécessite des vitesses de coupe réduites de moitié par rapport à un acier au carbone, multipliant le temps d'usinage par 3.

**Correction :** Évaluer l'indice d'usinabilité du matériau. Pour les pièces très usinées, préférer les aciers de décolletage (11SMnPb30 ou 1.0718) avec ajout de plomb/soufre, ou les inox de décolletage (430F, 416). Le surcoût matière est inférieur au gain en temps d'usinage.

---

## Liste de vérification (Checklist)

- [ ] La nuance de matériau choisie est adaptée à la température maximale et minimale d'utilisation (vérifier la transition ductile-fragile en froid).
- [ ] Les métaux en contact direct ne présentent pas d'incompatibilité galvanique majeure (vérifier la série galvanique).
- [ ] Les traitements thermiques préconisés sont compatibles avec la nuance d'acier (teneur en carbone suffisante pour la trempe, trempabilité adaptée à la section).
- [ ] L'usinabilité et/ou la soudabilité du matériau ont été intégrées dans les coûts de fabrication.
- [ ] Les nuances inoxydables utilisées dans les zones soudées sont des nuances "L" ou stabilisées (321, 347).
- [ ] La résistance à la corrosion du matériau a été vérifiée pour l'environnement exact (pH, température, concentration de chlorures, présence de H₂S).
- [ ] Les traitements de surface (peinture, galvanisation, anodisation, revêtement) sont spécifiés en fonction de l'environnement.
- [ ] La disponibilité de la nuance sur le marché (délais fournisseurs, quantité minimale de commande) est confirmée avant finalisation.
- [ ] Les critères de résistance à l'usure (abrasion, adhésion, érosion) ont été évalués selon le type de contact et la dureté relative.

