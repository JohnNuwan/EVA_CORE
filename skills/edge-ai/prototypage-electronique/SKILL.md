---
name: prototypage-electronique
description: "Prototyper des circuits électroniques — breadboard, soudure, oscilloscope, multimètre, alimentation, analyseur logique, debug de signaux, mesures et instrumentation."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [prototypage, breadboard, soudure, oscilloscope, multimètre, alimentation, analyseur-logique, gbw, sonde, trigger, mesure, instrumentation, labo, bench, debug, signal, probe, multimetre, pince-mesure]
    related_skills: [pcb-design-electronique, electronique-analogique, signal-processing-digital, embedded-systems-firmware]
---

# Prototypage Électronique et Instrumentation

## Vue d'ensemble

Le prototypage électronique transforme un schéma ou une idée en un circuit fonctionnel sur une platine d'essai (breadboard) ou une plaque à souder. Cette compétence couvre l'utilisation des instruments de laboratoire (oscilloscope, multimètre, alimentation stabilisée, générateur de fonctions, analyseur logique), les techniques de soudure, le débogage de signaux et les bonnes pratiques de mesure.

### Équipement minimal d'un banc de prototypage

```
┌─────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ Alim.   │──│ Breadboard / │──│ Oscillo  │──│ Multimètre   │
│ DC (±30V│  │ Plaque à    │  │ 2-4 voies │  │ (TRMS, 4½)   │
│  3-5A)  │  │ souder       │  │ 50-200 MHz│  │ cat III/II   │
└─────────┘  └──────────────┘  └──────────┘  └──────────────┘
┌─────────┐  ┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ GBF     │  │ Analyseur    │  │ Fer à   │ │ Pince        │
│ (sin/car/│──│ logique (8-  │──│ souder   │──│ ampèremétrique│
│ rampe,   │  │ 16 canaux,   │  │ 30-80 W  │  │ AC/DC 60A   │
│ 20 MHz)  │  │ 100 MSa/s)  │  │ à régler  │  │              │
└─────────┘  └──────────────┘  └──────────┘  └──────────────┘
```

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Câbler un circuit électronique sur breadboard (alimentation, capteurs, microcontrôleur, actionneurs).
- Souder des composants traversants (THT) ou montage en surface (SMD 1206, 0805, 0603, SOIC) sur plaque à souder ou PCB.
- Diagnostiquer un signal avec un oscilloscope (mesure de fréquence, amplitude, temps de montée, bruit, overshoot).
- Utiliser un multimètre pour des mesures de tension, courant, résistance, continuité, capacité, diode.
- Configurer une alimentation de laboratoire (limitation de courant, protection OVP/OCP, séquence de démarrage).
- Déboguer un bus de communication (UART, I²C, SPI) avec un analyseur logique ou un oscilloscope.
- Isoler un défaut (court-circuit, composant défectueux, soudure froide, piste coupée) sur un circuit.
- Mettre à la masse les instruments et le circuit pour éviter les boucles de masse.

Ne pas utiliser pour : la conception de PCB (utiliser `pcb-design-electronique`), le design de circuits analogiques complexes (utiliser `electronique-analogique`).

---

## 1. Techniques de Prototypage

### 1.1 Breadboard (Platine d'essai)

```text
Structure d'une breadboard :

    ┌──────────────────────────────────────────────┐
    │ [+] [+]                                     │ ← Rails d'alim. (rouge = +)
    │ [-] [-]                                     │ ← Rails de masse (bleu = GND)
    ├──────┬──────┬──────┬──────┬──────┬──────┬───┤
    │ a b c d e │ a b c d e │ a b c d e │       │
    │           │           │           │        │  ← Rows (lignes)
    │ f g h i j │ f g h i j │ f g h i j │       │
    ├──────┴──────┴──────┴──────┴──────┴──────┴───┤
    │ [+] [+]                                     │ ← Rails d'alim. (bas)
    │ [-] [-]                                     │ ← Rails de masse (bas)
    └──────────────────────────────────────────────┘

Règles de câblage :
- Chaque row (ligne a-e ou f-j) est connectée horizontalement.
- Les rails (+) et (-) sont connectés verticalement sur toute la longueur.
- Utiliser des fils de couleurs : ROUGE = VCC, NOIR = GND, JAUNE/ORANGE = signaux.
- Ne pas insérer de composants de puissance (> 0,5 A) — la breadboard chauffe.
- Les connexions haute fréquence (> 10 MHz) souffrent de capacité parasite (2-5 pF par point).
```

### 1.2 Soudure THT (Through-Hole Technology)

```text
Matériel :
- Fer à souder : 30-40 W pour THT, température réglable 300-350 °C.
- Panne : forme biseau (1,6 mm) pour usage général, cône fin (0,5 mm) pour CMS.
- Étain : 60/40 Sn/Pb ou sans plomb SAC305, diamètre 0,5-0,8 mm.
- Flux : pâte de flux (no-clean) pour les soudures difficiles.
- Accessoires : pompe à dessouder, tresse à dessouder, troisième main (helping hand).

Procédure :
1. Chauffer la panne à 320 °C (THT) ou 350 °C (SAC sans plomb).
2. Étamer la panne (fine couche d'étain).
3. Chauffer simultanément le pad et la patte du composant (2-3 secondes).
4. Amener l'étain sur l'interface pad-patte (NE PAS sur la panne).
5. Retirer l'étain, puis la panne après ~1 seconde.
6. Vérifier : joint conique, brillant, bonne angulation (≤ 45°).

Défauts courants :
- Soudure froide : aspect mat et granuleux → re-chauffer avec flux.
- Pont d'étain (court-circuit) → retirer avec tresse à dessouder.
- Excès d'étain → utiliser la pompe à dessouder.
- Manque d'étain → recommencer avec flux.
```

### 1.3 Soudure CMS (SMD — Surface Mount Device)

```text
Outils recommandés :
- Pince fine (courbée) pour placer les composants.
- Microscope ou loupe binoculaire (×5-×20) pour les 0402 et QFN.
- Station de soudure à air chaud (250-350 °C réglable).
- Paste à souder (syringe) pour le dépôt de crème à souder.

Procédure manuelle (résistance 0603, condensateur) :
1. Déposer une petite quantité de crème à souder sur les pads.
2. Placer le composant (alignement correct) avec la pince.
3. Souder à l'air chaud : 300 °C, flux d'air moyen, 5-10 secondes.
4. La crème fond et le composant s'aligne par tension de surface (self-alignment).

Procédure manuelle (QFP/TQFP) :
1. Étamer tous les pads du circuit avec l'étain fin.
2. Étamer la panne, puis appliquer une traînée d'étain sur toutes les pattes.
3. Retirer l'excès avec tresse à dessouder et flux.
4. Vérifier les ponts à la loupe.
```

---

## 2. Instrumentation et Mesures

### 2.1 Multimètre numérique

```text
Utilisation du multimètre :

Mesure de TENSION CONTINUE (V⎓) :
- Plage : mV à 1000 V DC.
- Pointer sur V avec trait continu (───).
- Brancher : rouge sur V/Ω, noir sur COM.
- Mesurer en parallèle du circuit.

Mesure de TENSION ALTERNATIVE (V~) :
- Plage : mV à 750 V AC.
- Pointer sur V~ (ondulation).
- Pour les signaux non sinusoïdaux,
  un multimètre TRMS (True RMS) est nécessaire.

Mesure de RÉSISTANCE (Ω) :
- Pointer sur Ω (ohmmètre).
- COUPER L'ALIMENTATION du circuit avant la mesure.
- Mesurer le composant seul (hors circuit si possible).

Mesure de CONTINUITÉ (buzzer) :
- Pointer sur le symbole ►/)) (diode + ondes).
- Si R < ~50 Ω : le buzzer sonne → continuité.
- Si R > 50 Ω ou circuit ouvert → silence.
- Utiliser pour : vérifier les pistes, les soudures, les fusibles.

Mesure de COURANT (A⎓/A~) :
- Brancher le multimètre EN SÉRIE dans le circuit.
- Pointer sur A (déplacer le fil rouge sur le bornier A si > 200 mA).
- ATTENTION : ne jamais brancher l'ampèremètre en parallèle (court-circuit).

Mesure de CAPACITÉ (F) :
- Pointer sur le symbole –|(– (capacimètre).
- Décharger le condensateur avant la mesure.
- Plage typique : pF à mF.

Pince ampèremétrique :
- Mesure de courant sans couper le circuit.
- Placer le conducteur au centre de la pince.
- DC : nécessite une pince à effet Hall. AC : pince à transformateur.
```

### 2.2 Oscilloscope numérique

```text
Réglages de base :

1. SONDES :
   - Compensation de la sonde : connecter à la sortie 1 kHz/1V de l'oscillo,
     régler le trimmer sur la sonde pour un carré parfait (pas d'overshoot ni d'arrondi).
   - Rapport : ×1 (bande passante limitée), ×10 (bande passante nominale, 10 MΩ).
   - Sonde ×10 : la tension mesurée est divisée par 10 (l'oscillo compense).

2. ÉCHELLES :
   - Volts/div : ajuster pour que le signal occupe 2 à 6 divisions verticales.
   - Temps/div : ajuster pour voir 2-3 cycles du signal.
   - Base de temps : commencer par 1 ms/div, ajuster selon la fréquence.

3. DÉCLENCHEMENT (TRIGGER) :
   - Mode : Auto (affichage continu), Normal (attente de déclenchement), Single (un coup).
   - Source : CH1, CH2, EXT (externe), Line (secteur 50 Hz).
   - Pente : Front montant, front descendant.
   - Niveau : régler au milieu de l'amplitude du signal.
   - Alternative : utiliser le trigger sur un canal stable (horloge) pour visualiser d'autres signaux.

4. MESURES AUTOMATIQUES :
   - Vpp : tension crête-à-crête.
   - Vmax, Vmin : valeurs extrêmes.
   - Vavg : moyenne (niveau DC).
   - Fréquence (Hz) : 1/période.
   - Temps de montée (tr) : 10 %-90 % de l'amplitude.
   - Overshoot : dépassement au-delà de la valeur finale.

Mesures avancées :
   - Curseurs : mesurer manuellement différence de temps ou de tension.
   - FFT : analyser le contenu spectral du signal.
   - Persistance infinie : visualiser les variations lentes.
   - Décodage de bus série : UART, I²C, SPI, CAN (sur oscillos récents).
```

### 2.3 Analyseur logique

```text
Usage typique (8-16 canaux, échantillonnage 50-200 MHz) :

1. Brancher le fil de masse (GND) sur le point de référence du circuit.
2. Brancher les canaux (CH0-CH7) sur les signaux à analyser :
   - CH0 : CLK (horloge SPI/I²C)
   - CH1 : MOSI/SDA
   - CH2 : MISO/SCL
   - CH3 : CS (chip select)
3. Régler l'échantillonnage : ≥ 10× la fréquence maximale du bus.
4. Lancer l'acquisition (déclenchement sur front du signal CS ou sur un motif).
5. Décoder le bus (sélectionner le protocole) : la trame est affichée en hexadécimal.

Exemple : décodage I²C avec un analyseur logique
   - Attendre le start condition (SDA ↓ pendant SCL HIGH)
   - Lire l'adresse 7 bits + R/W
   - Lire l'ACK
   - Lire les octets de données + ACK/NACK
   - Attendre le stop condition (SDA ↑ pendant SCL HIGH)

Logiciels open source : sigrok/PulseView, Saleae Logic (gratuit limité).
```

---

## 3. Débogage et Dépannage

### 3.1 Procédure systématique de débogage

```text
ÉTAPE 1 — Vérifier l'alimentation
  1. Tension présente sur les rails VCC/GND ? (multimètre DC)
  2. Polarité correcte ? (inversion = destruction possible)
  3. Tension stable ? (oscilloscope, pas de ripple > 100 mV)
  4. Courant consommé compatible avec l'alimentation ?

ÉTAPE 2 — Vérifier les signaux de base
  1. Horloge du microcontrôleur présente ? (oscillo, sonde ×10)
  2. Reset : niveau correct (H ou L) et pas de glitch ?
  3. LED de power-on allumée ?
  4. JTAG/SWD détecté par le débogueur ?

ÉTAPE 3 — Vérifier les communications
  1. UART : activité sur TX ? (oscillo/analyseur logique)
  2. I²C : start condition + ACK ?
  3. SPI : clock + CS correct ?
  4. Niveaux logiques compatibles (3.3 V ↔ 5 V) ?

ÉTAPE 4 — Vérifier les capteurs / actionneurs
  1. Tension d'alimentation du capteur correcte ?
  2. Sortie du capteur : analogique (ADC) ou numérique (I²C/SPI) ?
  3. Pour un actionneur (relais, moteur) : commande + retour ?
  4. Test en isolant le composant (hors circuit).

ÉTAPE 5 — Test de continuité
  - Vérifier les soudures suspectes.
  - Vérifier les pistes (coupures, micro-fissures).
  - Vérifier les connecteurs (broches pliées, mauvais contact).
```

### 3.2 Mesure de signaux haute fréquence

```text
Problème : Le signal mesuré à l'oscilloscope est différent du signal réel.
Cause : La sonde + le câble forment une capacité parasite (8-12 pF pour ×10).

Règles :
- Toujours utiliser la sonde en ×10 pour les signaux > 5 MHz.
- Garder le fil de masse de la sonde le plus court possible (utiliser la bague de masse).
- NE PAS utiliser le fil de masse standard pour les signaux > 20 MHz
  (utiliser un ressort de masse ou un adaptateur microtip).
- La bande passante de la sonde doit être ≥ la bande passante de l'oscilloscope.

Calcul du temps de montée mesuré vs réel :
  t_mesuré = √(t_réel² + t_oscillo² + t_sonde²)
  Où t_oscillo = 0.35 / BW_oscillo et t_sonde = 0.35 / BW_sonde
```

### 3.3 Boucles de masse (Ground Loops)

```text
SYMPTÔME : Bruit 50 Hz (ou 60 Hz) sur la mesure.
CAUSE : Différence de potentiel entre les masses des instruments.

SOLUTION :
1. Utiliser une seule prise secteur (multiprise) pour tous les instruments.
2. NE PAS retirer la fiche de terre (c'est dangereux).
3. Connecter toutes les masses des instruments au même point (étoile).
4. Utiliser un transformateur d'isolement pour le circuit testé (optionnel).
5. Si le bruit persiste : sonde différentielle (isolement galvanique).
```

---

## 4. Tests et Mesures Spécifiques

### 4.1 Mesure de la consommation d'un circuit

```text
Méthode avec multimètre :
  - Brancher le multimètre en série sur l'alimentation.
  - Pointer sur mA (débuter sur la plage la plus haute).
  - Pour la consommation en veille (µA), utiliser la plage µA.
  - ATTENTION : la chute de tension du shunt peut faire dysfonctionner le circuit.

Méthode avec résistance shunt :
  - Insérer une résistance de 1 Ω (puissance 0,5 W) en série.
  - Mesurer la tension aux bornes (1 mV = 1 mA).
  - Oscilloscope : visualiser le courant dynamique en mode différentiel.

Méthode avec pince ampèremétrique à effet Hall :
  - Mesure du courant sans coupure.
  - Résolution typique : 10 mA (pour pince 30 A).
  - Bon pour la mesure du courant d'un actionneur (moteur).
```

### 4.2 Test d'intégrité d'alimentation (Power Integrity)

```text
1. Mesure du ripple (ondulation résiduelle) :
   - Oscilloscope : 50 mV/div, AC coupling (découplage DC).
   - Sonde ×10, fil de masse court.
   - Ripple acceptable : < 50 mVpp pour 3.3 V numérique.
   - Si ripple > 100 mVpp : ajouter des condensateurs de découplage.

2. Réponse transitoire (step load) :
   - Connecter une charge qui varie brusquement (0 → Imax en 1 µs).
   - Observer la chute de tension à l'oscilloscope.
   - Chute acceptable : < 5 % de Vout pour un changement de 50 % de la charge.
   - Si chute excessive : augmenter la capacité de sortie (bulk caps).

3. Bruit haute fréquence (> 100 MHz) :
   - Boucle de masse : minimiser la surface de la boucle de retour.
   - Ajouter des ferrites (perles de ferrite) sur les alimentations.
   - Vérifier le découplage local : 100 nF (MLCC 0402) + 10 µF (MLCC 0805).
```

---

## Pièges Courants

1. **Sonde d'oscilloscope non compensée :** Un carré d'1 kHz apparaît arrondi (sur-compensation) ou avec des pointes (sous-compensation). Toujours compenser avant une mesure critique.

2. **Fil de masse long de l'oscilloscope :** Le clip de masse standard forme une antenne de 5-10 cm, qui capte les parasites et ajoute de l'overshoot au signal mesuré. Utiliser un ressort de masse pour les signaux > 20 MHz.

3. **Alimentation non découplée sur breadboard :** Un microcontrôleur qui commute 50 mA en 5 ns génère un pic de courant qui fait chuter la tension de la breadboard. Placer un condensateur 100 nF MLCC à chaque point d'alimentation du chip.

4. **Connexions flottantes sur breadboard :** Une patte de composant mal insérée ou une connexion desserrée crée des intermittences difficiles à diagnostiquer. Appuyer fermement chaque composant et vérifier la continuité.

5. **Surchauffe des composants CMS à l'air chaud :** Un flux d'air trop fort ou une température trop élevée déplace les petits composants (0402) ou endommage le circuit (plastique, connecteurs). Utiliser un flux d'air moyen et une température de 300-320 °C.

6. **Tension de référence flottante :** Mesurer une tension sans référencer la masse de l'instrument à celle du circuit. L'oscilloscope (qui est relié à la terre) ajoute une boucle de masse si le circuit n'est pas relié à la terre. Utiliser un transformateur d'isolement ou une sonde différentielle.

---

## Liste de vérification (Checklist)

- [ ] L'alimentation est configurée avec la bonne tension et la limitation de courant.
- [ ] La polarité de l'alimentation est vérifiée (pas d'inversion).
- [ ] Les rails GND et VCC de la breadboard sont reliés à l'alimentation.
- [ ] Les condensateurs de découplage (100 nF) sont présents sur chaque circuit intégré.
- [ ] La sonde d'oscilloscope est compensée (carré parfait sur le 1 kHz).
- [ ] Le fil de masse de l'oscilloscope est le plus court possible.
- [ ] Les soudures sont brillantes et coniques (pas de soudure froide).
- [ ] Aucun pont d'étain n'est visible (vérifier à la loupe).
- [ ] Le multimètre est réglé sur la bonne fonction et plage avant la mesure.
- [ ] Les instruments partagent une seule multiprise (pas de boucle de masse).
- [ ] Les fils de câblage sur breadboard sont rangés par couleur (VCC=rouge, GND=noir).
- [ ] Le circuit est testé par étapes (alimentation → micro → périphériques → capteurs/actionneurs).