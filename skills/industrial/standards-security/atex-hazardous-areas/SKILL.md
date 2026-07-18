---
name: atex-hazardous-areas
description: "Appliquer la réglementation ATEX (Atmosphères Explosives) : classifier les zones (0, 1, 2, 20, 21, 22), sélectionner le matériel certifié (Ex d, Ex i, Ex e, Ex p), et respecter les règles d'installation électrique EN 60079-14 et le Document Relatif à la Protection contre les Explosions (DRPEX)."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [atex, safety, explosion-proof, hazardous-areas, en-60079, ex-d, ex-i, ex-e, ex-p, compliance, drpex, zone-classification, gas-explosion, dust-explosion, seveso]
    related_skills: [industrial-risk-analysis-hazop, electrical-schematics-eplan, iso-45001]
    difficulty: advanced
    industry_sectors: [chemical, petrochemical, pharmaceutical, oil-gas, mining, wood-processing, grain-storage, water-treatment, paint-coating]
---

# Atmosphères Explosives (ATEX) — Classification et Protection

## Vue d'ensemble

Cette compétence guide le dimensionnement, la sélection d'équipements et la validation d'installations électriques et mécaniques dans les zones à risque d'explosion, régies par la réglementation européenne **ATEX** (ATmosphères EXplosibles) et les normes internationales **CEI/EN 60079** et **CEI/EN 80079**.

### Contexte Réglementaire

Deux directives européennes encadrent la réglementation ATEX :

| Directive | Cible | Objet |
|:---|:---|---|
| **Directive 2014/34/UE** (ex-94/9/CE) | **Fabricants** d'équipements | Règles de fabrication et de certification des matériels destinés aux zones explosibles |
| **Directive 1999/92/CE** (ex-ATEX 137) | **Utilisateurs** (exploitants de sites) | Protection des travailleurs, classification des zones, obligations documentaires (DRPEX) |

### Principes Physiques de l'Explosion

Une explosion nécessite la réunion simultanée de trois éléments (triangle du feu) :

```text
                    ┌──────────────┐
                    │  Comburant   │
                    │  (Oxygène)   │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────┴──────┐       ┌──────────┴───────┐
    │   Combustible  │       │ Source           │
    │  (Gaz, vapeur, │       │ d'Inflammation   │
    │   poussière)   │       │ (étincelle,      │
    └────────────────┘       │  point chaud)    │
                             └──────────────────┘
```

L'ATEX vise à éviter la formation d'une atmosphère explosive (dilution, ventilation) ou à supprimer toute source d'inflammation dans les zones où une atmosphère explosive peut apparaître.

### Secteurs Concernés

| Secteur | Substance explosive | Type de zone |
|:---|---|:---:|
| Chimie / Pétrochimie | Gaz (méthane, éthylène, hydrogène), solvants | Zone 0 / 1 / 2 |
| Pharmaceutique | Poudres fines (principes actifs), solvants | Zone 20 / 21 / 22 |
| Meunerie / Céréales | Poussières de blé, farine, grains | Zone 20 / 21 / 22 |
| Bois | Poussières de bois, sciure | Zone 21 / 22 |
| Peinture / Vernis | COV (composés organiques volatils), aérosols | Zone 1 / 2 |
| Stations d'épuration | Biogaz (méthane), gaz de digestion | Zone 1 / 2 |
| Hydrogène | H₂ (électrolyse, stockage) | Zone 0 / 1 / 2 |
| Mines | Grisou (méthane), poussières de charbon | Zone 0 / 1 / 20 |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Identifier et classer les **zones ATEX** sur un site industriel (zones 0, 1, 2 pour les gaz/vapeurs ; zones 20, 21, 22 pour les poussières).
- Déchiffrer et valider le **marquage ATEX** d'un capteur, d'un moteur, d'un éclairage ou d'une armoire électrique.
- Choisir le **mode de protection** adapté à la zone (enveloppe antidéflagrante **Ex d**, sécurité intrinsèque **Ex i**, sécurité augmentée **Ex e**, surpression interne **Ex p**, immersion dans l'huile **Ex o**).
- Appliquer les règles de **raccordement et de câblage** dans ces zones selon la norme **EN 60079-14**.
- Rédiger ou mettre à jour le **Document Relatif à la Protection contre les Explosions (DRPEX)**.
- Vérifier la conformité ATEX d'une installation existante ou d'une modification d'installation.

**Ne pas utiliser pour :**
- Les études de sécurité de procédé HAZOP / LOPA (utiliser `industrial-risk-analysis-hazop`).
- La gestion de la sécurité au travail (SST) hors explosion (utiliser `iso-45001`).

## 1. Classification des Zones ATEX

### Grille de Classification

| Type de Combustible | Présence Permanente ou Longue Durée (> 1000 h/an) | Présence Occasionnelle (10 h à 1000 h/an) | Présence Rare ou Courte Durée (< 10 h/an) |
|:---|:---:|:---:|:---:|
| **Gaz, Vapeurs, Brouillards** | **Zone 0** (ex : intérieur d'une cuve de solvant) | **Zone 1** (ex : abords d'une vanne de soutirage) | **Zone 2** (ex : local de stockage de produits inflammables, ventilation normale) |
| **Poussières Combustibles** | **Zone 20** (ex : intérieur d'un broyeur, d'un filtre à poussières) | **Zone 21** (ex : abords d'un ensacheur, zone de déchargement) | **Zone 22** (ex : local de stockage de poudre, traces de poussières) |

### Étendue des Zones

L'étendue (rayon) d'une zone est déterminée par :
- La nature et la densité du gaz/vapeur (lourd ou léger).
- La ventilation du local (naturelle, forcée, degré de dilution).
- La présence de sources de fuite (brides, vannes, pompes, joints).
- Les obstacles et la géométrie du local.

**Règles empiriques (valeurs par défaut à adapter par l'analyse de risque) :**

| Source de fuite | Zone | Rayon typique |
|:---|---|:---:|
| Bride ou vanne en zone extérieure (gaz naturel) | Zone 1 / 2 | 1 – 3 m |
| Bride ou vanne en local fermé (solvant) | Zone 1 | Toute la pièce si ventilation insuffisante |
| Pompe centrifuge (garniture mécanique) | Zone 1 / 2 | 3 – 5 m |
| Évent de soupape de sécurité | Zone 0 / 1 | 5 – 10 m selon le débit |
| Goulotte de remplissage de poudre | Zone 21 / 22 | 1 – 3 m |
| Filtre à manches (poussières) | Zone 20 / 21 | Intérieur du filtre + 1 m autour |

## 2. Modes de Protection et Marquage ATEX

### Tableau des Modes de Protection

| Mode | Symbole | Principe | Zone autorisée | Application typique |
|:---|:---:|:---|---|:---|
| **Enveloppe antidéflagrante** | **Ex d** | Confinement de l'explosion à l'intérieur de l'enveloppe. Les flammes sont refroidies en traversant les joints ajustés (chemin de flamme). | Zone 1, 2 | Moteurs électriques, boîtes de jonction, capteurs, éclairages |
| **Sécurité intrinsèque** | **Ex i** (ia / ib / ic) | Limitation de l'énergie électrique ($U_o, I_o, P_o$) en dessous du seuil d'inflammation. | Zone 0 (ia), 1 (ib), 2 (ic) | Capteurs de pression/température, transmetteurs, vannes électropneumatiques |
| **Sécurité augmentée** | **Ex e** | Mesures constructives renforcées (pas d'arc, d'étincelle ou de point chaud en fonctionnement normal). | Zone 1, 2 | Boîtes à bornes, moteurs (bagues bobinées), éclairages |
| **Surpression interne** | **Ex p** | Maintien d'une surpression interne de gaz protecteur (air ou gaz inerte) empêchant l'entrée de l'atmosphère explosive. | Zone 1, 2 | Armoires électriques d'instrumentation, analyseurs |
| **Immersion dans l'huile** | **Ex o** | Immersion des pièces sous tension dans l'huile. | Zone 1, 2 | Transformateurs, démarreurs |
| **Remplissage pulvérulent** | **Ex q** | Remplissage de l'enveloppe avec un matériau pulvérulent (sable de quartz) qui empêche l'inflammation. | Zone 1, 2 | Appareillages fixes |
| **Encapsulage** | **Ex m** | Encapsulage des composants dans une résine inhibant l'amorçage. | Zone 1 (ma), 2 (mb) | Petits capteurs, sondes, électronique embarquée |

### Décodage d'un Marquage ATEX Complet

Exemple : `CE 0081 II 2 G Ex db IIB T4 Gb`

| Élément | Signification | Détail |
|:---|:---|---|
| `CE 0081` | Marquage CE et numéro de l'organisme notifié | 0081 = LCIE (Laboratoire Central des Industries Électriques) |
| `II` | Groupe II (industries de surface, hors mines) | Groupe I = mines de charbon (grisou) |
| `2` | Catégorie d'équipement | 1 = Zone 0/20 ; 2 = Zone 1/21 ; 3 = Zone 2/22 |
| `G` | Atmosphère Gaz | D = Poussière (Dust) ; GD = mixte gaz + poussière |
| `Ex db` | Mode de protection "Enveloppe antidéflagrante" | (notation EN 60079-1 révisée : `db` = Ex d, `eb` = Ex e, `ia` = Ex i niveau a) |
| `IIB` | Groupe de gaz | IIA (propane, méthane) → IIB (éthylène) → IIC (hydrogène, acétylène) — IIC est le plus contraignant |
| `T4` | Classe de température | T1 (450 °C) → T6 (85 °C) — La température maximale de surface de l'appareil ne doit pas dépasser la température d'auto-inflammation du gaz présent |
| `Gb` | EPL (Equipment Protection Level) | Ga = Zone 0 ; Gb = Zone 1 ; Gc = Zone 2 |

### Classes de Température ATEX

| Classe | Température maximale de surface | Gaz dont la température d'auto-inflammation est supérieure à |
|:---:|:---:|:---|
| T1 | 450 °C | Méthane, hydrogène (560 °C) |
| T2 | 300 °C | Éthylène, propane |
| T3 | 200 °C | Essence, gazole |
| T4 | 135 °C | Acétaldéhyde, éther éthylique |
| T5 | 100 °C | – |
| T6 | 85 °C | Disulfure de carbone |

**Règle fondamentale :** La classe de température de l'équipement doit être strictement inférieure à la température d'auto-inflammation de la substance présente.

## 3. Règles d'Installation EN 60079-14

### Câblage et Raccordements en Zone ATEX

| Aspect | Règle | Référence |
|:---|---|:---:|
| **Presse-étoupes** | Uniquement des presse-étoupes métalliques certifiés ATEX. Pas de presse-étoupe plastique en zone Ex d. | EN 60079-14 §9.3 |
| **Joints de câbles (chemin de flamme)** | Les filetages doivent avoir au moins 5 filets pleins de contact pour maintenir le chemin de flamme Ex d. | EN 60079-1 §5.2 |
| **Barrière Ex i** | Un isolateur galvanique ou une barrière Zener doit être interposé entre la zone sûre et le capteur Ex i en zone explosive. Vérifier la compatibilité : $U_o \leq U_i$, $I_o \leq I_i$, $P_o \leq P_i$. | EN 60079-11 §5.1 |
| **Mise à la terre** | Toutes les masses métalliques (armoires, câbles armés, conduits) doivent être reliées à la terre équipotentielle. En zone ATEX, le maillage de terre doit être dimensionné pour éviter toute différence de potentiel. | EN 60079-14 §8.4 |
| **Câbles non armés** | Interdits en zone 1 ou 20 sauf s'ils sont protégés mécaniquement (goulotte métallique, conduit). | EN 60079-14 §9.2 |
| **Distance minimale** | Les câbles des circuits Ex i doivent être séparés des autres câbles (chemin de câble dédié ou distance > 50 mm). | EN 60079-11 §7.1 |

### Documentation Obligatoire : le DRPEX

Le **Document Relatif à la Protection contre les Explosions (DRPEX)** est exigé par la Directive 1999/92/CE. Il doit contenir :

1. **Le plan de classement des zones** (plan d'atelier avec zones colorées : rouge Zone 0/20, orange Zone 1/21, jaune Zone 2/22).
2. **La liste des substances présentes** (nom, composition, température d'auto-inflammation, limite inférieure/supérieure d'explosivité LIE/LSE, densité).
3. **L'inventaire des équipements** en zone ATEX (type, certificat, classe de température, groupe de gaz, mode de protection).
4. **Les mesures de protection** collectives (ventilation, détection de gaz) et individuelles (EPI antistatiques).
5. **Les procédures** : permis de travail par points chauds, consignes de sécurité pour les intervenants extérieurs.
6. **Le plan de maintenance** des équipements ATEX (fréquence des vérifications des barrières Ex i, des presse-étoupes, des détecteurs de gaz).

## Pièges Courants (Common Pitfalls)

1. **Rupture de la barrière de Sécurité Intrinsèque (Zener / Isolateur) :**
   - *Erreur :* Câbler un capteur "Ex i" situé en Zone 0 directement sur une carte d'entrées analogiques automate standard située en zone sûre, sans ajouter de barrière Zener ou d'isolateur galvanique. En cas de défaut électrique dans l'automate (court-circuit 230 V), une forte énergie sera transmise en zone ATEX, créant une étincelle destructrice.
   - *Correction :* Intercaler systématiquement une barrière isolante certifiée (barrière de sécurité intrinsèque) entre la zone sûre et la zone ATEX pour limiter le courant et la tension à des niveaux incapables de déclencher une étincelle. Vérifier la compatibilité électrique ($U_o, I_o, P_o$) de la barrière avec les paramètres d'entrée du capteur ($U_i, I_i, P_i$).

2. **Perte de l'étanchéité Ex d lors de la maintenance ou de l'installation :**
   - *Erreur :* Utiliser un presse-étoupe standard en plastique ou ne pas serrer complètement les vis du couvercle d'une boîte de jonction Ex d. Le chemin de flamme (joint plat ajusté) n'est plus garanti. En cas d'explosion interne du gaz, l'enveloppe ne retiendra pas la flamme, qui se propagera à l'extérieur.
   - *Correction :* Utiliser uniquement des presse-étoupes métalliques certifiés ATEX Ex d. S'assurer que tous les filetages et joints de couvercles respectent les tolérances du fabricant lors du serrage (couple de serrage spécifié). Les joints endommagés doivent être remplacés, pas réparés.

3. **Confusion entre groupe de gaz et classe de température :**
   - *Erreur :* Installer un équipement marqué `Ex d IIC T3` (hydrogène, T3 = 200 °C) dans une zone contenant du disulfure de carbone (température d'auto-inflammation = 100 °C). L'équipement peut atteindre 200 °C en surface, ce qui déclenchera l'explosion.
   - *Correction :* Vérifier simultanément le groupe de gaz (l'équipement IIC convient pour IIA/IIB/IIC) ET la classe de température (T6 est compatible avec toutes les classes inférieures ; T3 n'est pas compatible avec une substance qui nécessite T4, T5 ou T6). Règle : **T6 ≥ T5 ≥ T4 ≥ T3 ≥ T2 ≥ T1** (T6 est le plus sûr).

4. **Absence de mise à jour du DRPEX après modification :**
   - *Erreur :* Modifier l'installation (ajout d'une pompe, nouvelle vanne, changement de fluide pour un produit plus volatil) sans revoir la classification des zones ni mettre à jour le DRPEX.
   - *Correction :* Toute modification du procédé (changement de substance, ajout de source de fuite, modification de ventilation) doit déclencher une revue de la classification ATEX et une mise à jour du DRPEX. Désigner un référent ATEX sur le site.

## Références

- **Directive 2014/34/UE** : Appareils et systèmes de protection destinés à être utilisés en atmosphères explosibles.
- **Directive 1999/92/CE** : Prescriptions minimales visant à améliorer la protection des travailleurs susceptibles d'être exposés au risque d'atmosphères explosives.
- **EN 60079-10-1** : Classification des zones — Atmosphères de gaz (zones 0, 1, 2).
- **EN 60079-10-2** : Classification des zones — Atmosphères de poussières (zones 20, 21, 22).
- **EN 60079-14** : Conception, sélection et construction des installations électriques.
- **EN 60079-17** : Inspection et maintenance des installations électriques.
- **EN 60079-29-1** : Détecteurs de gaz — Prescriptions de fonctionnement.
- **INERIS — Guide ATEX** : Guide pratique pour le classement des zones et la rédaction du DRPEX.

## Liste de vérification (Checklist)

- [ ] La **classification de zone** (0, 1, 2, 20, 21, 22) de chaque local, zone extérieure et équipement est clairement définie sur un plan d'atelier à jour.
- [ ] Le **groupe de gaz** (IIA, IIB, IIC) ou de poussière (IIIA, IIIB, IIIC) de l'appareil est compatible avec les substances présentes dans la zone.
- [ ] La **classe de température** de l'appareil (T1 à T6) est inférieure à la température d'auto-inflammation du fluide présent dans la zone.
- [ ] Les **équipements Ex i** sont associés à des barrières de sécurité intrinsèque dont les caractéristiques électriques ($U_o \leq U_i$, $I_o \leq I_i$, $P_o \leq P_i$) sont compatibles et documentées.
- [ ] La **mise à la terre équipotentielle** de toutes les structures métalliques, armoires, câbles armés et équipements en zone ATEX est assurée et mesurée (résistance < 10 Ω).
- [ ] Les **presse-étoupes** sont certifiés ATEX, métalliques (pas de plastique en zone Ex d), correctement serrés, et les câbles non utilisés sont obturés par des bouchons certifiés.
- [ ] Le **DRPEX** (Document Relatif à la Protection contre les Explosions) est complet, daté, signé par le responsable du site, et accessible à tout moment.
- [ ] Les **détecteurs de gaz** (qualitatifs ou quantitatifs) sont installés selon l'étude de risque, testés et étalonnés selon les préconisations du fabricant et un registre de maintenance est tenu.
- [ ] Les **interventions par points chauds** (soudure, meulage, perçage) en zone ATEX ou à proximité sont soumises à un permis de feu avec analyse de risques préalable.
- [ ] Les **vérifications périodiques** des installations ATEX sont réalisées (inspection visuelle, rapprochée, approfondie) selon les échéances définies dans le plan d'inspection EN 60079-17.

