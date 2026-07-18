---
name: emc-protection-grounding
description: "Appliquer les règles de Compatibilité Électromagnétique (CEM/EMC), concevoir le réseau de terre (PE, masses HF), le blindage des câbles et sélectionner les filtres et parafoudres."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [emc, grounding, shielding, protection, electrical-noise, industrial-panels, surge-protection, lightning, filter]
    related_skills: [electrical-schematics-eplan, pcb-design-altium, pid-instrumentation]
---

# Compatibilité Électromagnétique (CEM) et Protection Électrique

## Vue d'ensemble

Cette compétence guide l'application des règles de **Compatibilité Électromagnétique (CEM / EMC)** et de mise à la terre dans les installations et armoires électriques industrielles. Les environnements d'usine concentrent de nombreuses sources de perturbations haute fréquence — variateurs de vitesse (drive), commutations de charges inductives (contacteurs, relais), soudeuses, fours à induction — et des récepteurs sensibles — capteurs analogiques (4-20 mA, thermocouples), réseaux de terrain (Profinet, EtherNet/IP, Modbus TCP), automates et contrôle-commandes.

La CEM a pour objectif de garantir que :

1. **L'équipement n'émet pas de perturbations** électromagnétiques au-delà des limites réglementaires (directive CEM 2014/30/UE, normes IEC 61000-6-x).
2. **L'équipement est immunisé contre les perturbations** électromagnétiques présentes dans son environnement.

Une mauvaise conception CEM se manifeste par des pannes intermittentes difficiles à diagnostiquer (communication réseau perdue aléatoirement, mesure de température erratique, déclenchement intempestif de protections), voire la destruction de composants électroniques.

Cette compétence est conçue pour être actionnée par l'agent EVA lorsque l'utilisateur exprime un besoin lié à la conception CEM, à la mise à la terre, au blindage ou à la protection des installations électriques industrielles.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Définir des règles de câblage et de séparation des goulottes dans une armoire pour limiter les couplages inductifs et capacitifs.
- Concevoir un système de mise à la terre (schéma TN-S, TT, IT) et distinguer la terre de protection (PE) de la terre fonctionnelle / masses HF.
- Spécifier les raccordements de blindages de câbles (colliers 360°, queues de cochon interdites).
- Sélectionner des dispositifs de protection contre les surtensions (parafoudres Type 1, 2, 3) et des filtres CEM d'alimentation.
- Diagnostiquer des perturbations électromagnétiques (relevé de spectre, boucle de masse, courant de mode commun).
- Définir des préconisations de câblage pour variateurs de vitesse (longueur de câble moteur, filtre de sortie, inductance de ligne).

---

## Principes de base de la CEM

### Modes de couplage

| Mode de couplage | Description | Atténuation |
|:----------------|:-----------|:------------|
| **Conductif** | Perturbations transmises par les câbles d'alimentation ou de signal | Filtre CEM, isolation galvanique |
| **Inductif** | Champ magnétique généré par un courant variable dans un conducteur voisin | Séparation spatiale, câbles torsadés, blindage magnétique |
| **Capacitif** | Champ électrique généré par une tension variable entre conducteurs voisins | Séparation spatiale, blindage électrostatique, écran |
| **Rayonné** | Onde électromagnétique se propageant dans l'air | Blindage d'armoire, atténuation par distance, filtres |

### Phénomène d'antenne

Tout conducteur non terminé sur un plan de masse se comporte comme une antenne au-dessus d'une certaine fréquence. La longueur du conducteur ne doit pas dépasser $\lambda / 20$, où $\lambda$ est la longueur d'onde de la fréquence maximale considérée.

$$\lambda = \frac{c}{f} \approx \frac{3 \times 10^8}{f}$$

| Fréquence $f$ | Longueur d'onde $\lambda$ | Longueur critique $\lambda/20$ |
|:-------------|:-------------------------|:------------------------------|
| 1 MHz | 300 m | 15 m |
| 10 MHz | 30 m | 1.5 m |
| 100 MHz | 3 m | 15 cm |
| 1 GHz | 0.3 m | 1.5 cm |

Ainsi, pour une perturbation à 100 MHz (fréquence de commutation typique des variateurs modernes), une queue de cochon de blindage de 15 cm est déjà une antenne efficace — c'est pourquoi le raccordement 360° est impératif.

---

## Règles de câblage CEM dans une armoire

### Classification des câbles (norme IEC 61000-5-2)

Les câbles doivent être regroupés par **classes** de signaux et séparés physiquement dans des goulottes distinctes :

| Classe | Type de signaux | Exemples |
|:------|:---------------|:---------|
| **Classe 1 (Très sensibles)** | Réseaux de terrain, signaux analogiques, TOR haute vitesse | Ethernet, Profinet, CANopen, 4-20 mA, PT100, encodeurs |
| **Classe 2 (Sensibles)** | Alimentations DC, signaux logiques basse vitesse | 24 VDC capteurs, sorties TOR PLC |
| **Classe 3 (Perturbateurs)** | Alimentation AC, sorties relais | 230 VAC / 400 VAC, contacteurs de puissance |
| **Classe 4 (Très perturbateurs)** | Câbles variateurs → moteurs, soudeuses | Câbles moteurs blindés (commutation HF), câbles de puissance haché |

**Règle impérative :** Les câbles de classes différentes ne doivent **jamais** cheminer parallèlement dans la même goulotte sans cloison séparatrice métallique reliée à la masse. En cas de croisement nécessaire, les câbles doivent se croiser à **90°** (angle droit).

### Distances de séparation minimales recommandées

| Entre classes | Sans séparation | Avec cloison métallique |
|:------------|:---------------|:----------------------|
| 1 ↔ 2 | 1 cm | 0 cm |
| 1 ↔ 3 | 10 cm | 0 cm |
| 1 ↔ 4 | 30 cm | 5 cm |
| 2 ↔ 3 | 5 cm | 0 cm |
| 2 ↔ 4 | 20 cm | 5 cm |
| 3 ↔ 4 | 10 cm | 0 cm |

---

## Mise à la terre et équipotentialité

### Schémas de liaison à la terre (IEC 60364)

| Schéma | Description | Usage industriel |
|:-------|:-----------|:----------------|
| **TN-S** | Neutre et PE séparés sur toute l'installation | Standard usine, bon pour CEM |
| **TN-C** | Neutre et PE combinés (PEN) | Interdit en CEM à cause des courants de retour |
| **TN-C-S** | TN-C en amont, TN-S en aval (séparation au TGBT) | Compromis économique |
| **TT** | Terre d'installation indépendante du neutre | Postes non industriels |
| **IT** | Neutre isolé ou impédant | Continuité de service, salles blanches, chimie |

### Terre de protection PE vs. Terre fonctionnelle HF

- **Terre de protection (PE)** : Conducteur jaune/vert de section calibrée (IEC 60364). Assure la protection des personnes à 50 Hz. Son impédance est faible à 50 Hz mais devient élevée à haute fréquence ($> 1 \mu H/m pour les fils ronds).

- **Masse HF / Terre fonctionnelle** : Connexions larges et courtes réalisées avec des tresses de masse plates (rapport largeur/épaisseur $> 10$) pour minimiser l'impédance haute fréquence (effet de peau, inductance minimale). La plaque de montage arrière doit être non peinte (acier zingué/galvanisé) pour servir de plan de masse équipotentiel à haute fréquence.

**Règle :** La distance entre un équipement et le point de raccordement à la plaque de masse ne doit pas dépasser 1/20 de la longueur d'onde de la perturbation maximale. En dessous de 10 MHz, limiter à 1,5 m.

---

## Blindage des câbles

### Types de blindage

| Type de blindage | Atténuation (10 MHz – 1 GHz) | Usage |
|:----------------|:---------------------------|:------|
| Tresse cuivre | 30 – 40 dB | Câbles moteur, signaux généraux, bon rapport coût/efficacité |
| Feuillard aluminium + drain | 40 – 70 dB | Câbles de données, Ethernet FTP/STP |
| Tresse + feuillard double | 60 – 90 dB | Environnements très perturbés, câbles d'encodeur |
| Blindage magnétique (acier) | 10 – 30 dB (champ H) | Câbles d'alimentation, protection basses fréquences |

### Raccordement 360° (obligatoire)

**Erreur fatale :** Le raccordement du blindage par un fil torsadé (queue de cochon, *pigtail*) de quelques centimètres. Cette configuration présente une inductance élevée à haute fréquence (1 nH/mm), rendant le blindage inefficace dès 1 MHz. La longueur de la queue de cochon est critique : au-delà de $\lambda/20$, elle devient une antenne.

**Correction :** Raccorder le blindage sur 360° en utilisant des colliers de blindage métalliques (EMC cable glands ou EMC clamps) fixés directement sur la plaque de montage métallique non peinte ou sur un rail collecteur de blindage relié au châssis.

```text
    × Queue de cochon (PIGTAIL) — INTERDIT      ✓ Collier 360° — OBLIGATOIRE

    Fil blindé ──────╲                ╱────     Fil blindé ──────╮
                      ╲  Fil de      ╱                            │ Collier métallique
                       ╲  blindage   ╱                             │   ┌───┐
                        ╲ torsadé   ╱                              ├───┤   │
                         ╲  (3 cm) ╱                               │   └───┘
                          ╲       ╱                                │
                           ╲─────╱                                 │ Plaque de masse
                            │                                      │
                         Borne de terre                          ──┴─────
```

### Raccordement aux deux extrémités

- **Câbles de données (Ethernet, Profinet, bus de terrain)** : Blindage raccordé aux **deux extrémités** (armoire A et armoire B) via des connecteurs blindés métalliques.
- **Câbles analogiques (4-20 mA, thermocouple)** : Blindage raccordé à une seule extrémité (côté récepteur) pour éviter les boucles de masse basses fréquences. Raccorder l'autre extrémité via un condensateur 10 nF / 100 V si la fréquence est élevée.
- **Câbles moteur variateur** : Blindage raccordé aux **deux extrémités** (armoire et moteur). Le blindage doit être raccordé à la terre du moteur via le presse-étoupe métallique.

---

## Filtres CEM et parafoudres

### Filtres CEM d'alimentation

Un filtre CEM est composé de condensateurs ($C_X$ entre phases, $C_Y$ entre phase et terre) et d'inductances de mode commun ($L_{CM}$). Il atténue les perturbations conduites dans la gamme 150 kHz – 30 MHz.

**Règles d'installation :**

- Placer le filtre **à l'entrée** de l'armoire, au plus proche du point de pénétration des câbles d'alimentation.
- **Séparer physiquement** le câble d'entrée (avant filtre) du câble de sortie (après filtre) pour éviter le couplage capacitif/inductif qui contournerait le filtre.
- Relier la masse du filtre directement à la plaque de masse par une tresse large et courte.

### Parafoudres (Surge Protective Devices — SPD)

| Type | Classe IEC 61643-11 | Capacité de décharge | Emplacement |
|:-----|:-------------------|:---------------------|:------------|
| Type 1 | Classe I | $I_{imp} \ge 25\,\mathrm{kA}$ (10/350 µs) | TGBT, entrée bâtiment — foudroiement direct |
| Type 2 | Classe II | $I_n \ge 20\,\mathrm{kA}$ (8/20 µs) | Armoires de distribution secondaires |
| Type 3 | Classe III | $U_{oc} \ge 1\,\mathrm{kV}$ (1.2/50 µs) | Au plus près de l'équipement sensible (PLC, automate) |

**Règle de coordination :** La distance entre deux étages de parafoudres doit être $\ge 10\,\mathrm{m}$ de câble (ou utiliser une inductance de découplage) pour que l'étage aval ne soit pas sollicité au-delà de sa capacité.

### Protection des charges inductives

Toute charge inductive (bobine de contacteur, relais, électrovanne, frein) pilotée par une sortie électronique (PLC, relais statique) doit être protégée contre la surtension de coupure :

| Type de courant | Composant de protection | Montage |
|:---------------|:----------------------|:--------|
| DC (bobine 24 VDC) | Diode de roue libre 1N4007 (ou équivalente) | En parallèle sur la bobine, cathode côté + |
| AC (bobine 230 VAC) | Varistance MOV (ex : S20K275) | En parallèle sur la bobine |
| AC ou DC | Circuit RC (cellule RC snubber, 100 Ω + 100 nF) | En parallèle sur la charge |

---

## Pièges Courants (Common Pitfalls)

### 1. Raccordement du blindage par un fil torsadé (queue de cochon / pigtail)

**Erreur :** Dénuder un câble blindé sur quelques centimètres et tordre le blindage en un fin conducteur jaune-vert pour le connecter à un bornier de terre. Cette pratique, bien que courante, détruit complètement l'efficacité du blindage haute fréquence. L'inductance de ce fil (environ 1 µH pour 10 cm) crée une impédance de $Z = L\omega \approx 6\,\mathrm{k\Omega}$ à 100 MHz — le blindage est transparent pour les parasites RF.

**Correction :** Utiliser systématiquement des presse-étoupes CEM (EMC cable glands) avec contact 360° sur la tresse de blindage. Fixer le presse-étoupe sur une plaque de montage métallique non peinte, ou sur un rail collecteur de blindage dédié. Pour les armoires existantes, utiliser des colliers de blindage (EMC clamps) ou des barrettes de blindage.

### 2. Absence de protection contre les surtensions induites (diodes de roue libre)

**Erreur :** Commander un relais ou une électrovanne 24 VDC directement depuis une sortie d'automate (transistor NPN/PNP ou relais statique) sans aucune protection parallèle. Lors de l'ouverture du circuit, la bobine inductive génère une surtension $V = L \cdot dI/dt$ pouvant atteindre plusieurs centaines de volts (la polarité s'inverse), qui détruit le transistor de sortie de l'automate par claquage.

**Correction :** Placer systématiquement une diode de roue libre en parallèle sur chaque bobine DC :
- Diode de redressement rapide (1N4007, 1N4148 pour les faibles courants).
- Cathode côté $+$ 24 V : la diode est bloquée en fonctionnement normal, conductrice à l'ouverture pour absorber l'énergie de la bobine.
- Pour les bobines AC, utiliser une varistance MOV ou un circuit RC (snubber).

### 3. Boucles de masse (Ground Loops)

**Erreur :** Connecter la terre de protection (PE) et la terre fonctionnelle de deux armoires distantes par plusieurs conducteurs parallèles formant une boucle fermée. Une différence de potentiel (ddp) entre les deux points de terre (due aux courants de fuite des variateurs, aux harmoniques de neutre) génère un courant circulant dans la boucle, qui induit des tensions parasites dans les câbles de signaux partagés entre les armoires (communication réseau, mesure analogique). Symptôme typique : la communication par bus de terrain fonctionne quand on débranche le PE d'une armoire, mais pas quand il est branché.

**Correction :** Utiliser une topologie de terre en **étoile** (star grounding) :
- Un point de terre central unique (barre de terre générale du bâtiment).
- Chaque armoire est reliée à ce point unique par un conducteur dédié.
- Les tresses de masse entre armoires sont interdites (sauf si spécifiquement conçues pour la CEM avec des isolateurs en série).

### 4. Oublier le chemin de retour HF des courants de mode commun

**Erreur :** Utiliser un câble moteur non blindé entre un variateur et un moteur, ou un câble blindé mal raccordé. Les fréquences de commutation élevées des IGBT modernes (2 – 16 kHz) génèrent des courants de mode commun importants qui circulent via les capacités parasites moteur → terre. Si le chemin de retour (blindage) n'est pas excellent, le courant de mode commun emprunte les câbles de capteurs ou les blindages de communication, créant des perturbations.

**Correction :** Toujours utiliser des câbles moteur blindés avec section du blindage $\ge 50\%$ de la section des conducteurs de phase. Raccorder le blindage aux deux extrémités (variateur et moteur) avec des presse-étoupes CEM. Limiter la longueur du câble moteur selon les préconisations du fabricant du variateur (souvent $\le 50\,\mathrm{m}$ sans filtre de sortie). En cas de longueur dépassée, ajouter un filtre de sortie (filtre sinus ou dV/dt) et/ou une self de mode commun.

---

## Liste de vérification (Checklist)

- [ ] Les câbles de puissance moteurs (variateurs) sont blindés et physiquement séparés des câbles de réseaux et de capteurs analogiques (goulottes distinctes ou cloison métallique).
- [ ] Les blindages de câbles réseau/mesure sont raccordés sur 360° à l'entrée de l'armoire (pas de queues de cochon).
- [ ] La plaque de montage de l'armoire est conductrice en surface (acier galvanisé ou zingué, pas de peinture sous les équipements).
- [ ] Des dispositifs d'écrêtage de surtension sont installés sur toutes les charges inductives (diodes de roue libre sur bobines DC, varistances/circuits RC sur AC).
- [ ] Les tresses de masse plates (largeur > épaisseur) sont utilisées pour relier la porte de l'armoire au châssis principal.
- [ ] L'alimentation de l'armoire est filtrée (filtre CEM en entrée) avec une séparation physique avant/après le filtre.
- [ ] Les distances de séparation entre classes de câbles sont respectées (min 10 cm entre classe 1 et classe 3, 30 cm entre classe 1 et classe 4).
- [ ] Les parafoudres sont coordonnés (distance $\ge 10\,\mathrm{m}$ entre Type 1 et Type 2, sauf inductance de découplage).
- [ ] Les câbles moteur ont une longueur conforme aux préconisations du fabricant du variateur (ou filtre de sortie installé si dépassement).
- [ ] Le schéma de mise à la terre est en étoile (pas de boucle de masse entre armoires distantes).

