---
name: pcb-design-altium
description: "Concevoir des circuits imprimés (CAO PCB : schématique et routage multicouches) sous Altium Designer ou KiCad, respecter les règles de CEM et de fabrication (DFM) et générer les dossiers industriels."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [pcb, electronics, altium, kicad, hardware, cad, signal-integrity, circuit-design, dfm, gerber, cem, emc]
    related_skills: [embedded-systems-firmware, electrical-cabinet-3d, electrical-schematics-eplan]
---

# Conception de Cartes Électroniques (PCB Design)

## Vue d'ensemble

Cette compétence encadre la conception complète des circuits imprimés (**PCB — Printed Circuit Board**), depuis la saisie du schéma électrique jusqu'au routage physique des pistes et la génération des fichiers de fabrication. Les outils de CAO électronique couverts incluent **Altium Designer** (environnement professionnel), **KiCad** (open source très complet), **OrCAD/Allegro** et **EAGLE**.

La conception d'un PCB industriel ne se limite pas à connecter des broches entre elles. Elle doit intégrer des contraintes pluridisciplinaires :

- **DFM (Design for Manufacturing)** : respect des règles de fabrication du fournisseur (jeux minimaux, tolérances de perçage, rapport d'aspect des trous métallisés).
- **CEM (Compatibilité ÉlectroMagnétique)** : limitation des émissions rayonnées et conduites, immunité aux perturbations externes, intégrité du signal.
- **Gestion thermique** : dissipation des pertes par conduction, convection, et éventuellement via des dissipateurs ou des vias thermiques.
- **Intégrité du signal** : adaptation d'impédance, contrôle des réflexions sur les lignes haute fréquence, diaphonie entre pistes adjacentes.
- **DFA (Design for Assembly)** : orientation des composants pour la soudure automatique (pick-and-place, wave soldering), espacement suffisant pour les têtes de vissage.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Dessiner le schéma fonctionnel d'un circuit électronique : alimentation à découpage (flyback, buck, boost), microcontrôleur avec ses périphériques, conditionnement de signal analogique, interface de puissance.
- Définir l'empilement des couches (Stackup) pour un PCB multicouches (4, 6, 8 couches ou plus) et les impédances caractéristiques cibles.
- Router les pistes et placer les composants en respectant les contraintes CEM : séparation des domaines analogiques/numériques/puissance.
- Générer les livrables pour le fabricant de PCB : fichiers Gerber RS-274X (ou ODB++), fichier de perçage (NC Drill), nomenclature (BOM) et fichier de placement (Pick and Place).
- Analyser un design existant pour identifier des pistes non conformes (DRC errors), des problèmes CEM ou des violations de règles de fabrication.

## Empilement des Couches (Stackup) et Impédance

### Empilement typique d'un PCB 4 couches

```text
  ┌────────────────────────────────────┐  ── Couche 1 (Top / Signal / Composants)
  │  Cuivre 35 µm (1 oz)               │     ✦ Pistes haute vitesse et composants CMS
  ├────────────────────────────────────┤
  │  Préimprégné (PP)  →  εr ≈ 4.2     │     Épaisseur : variable selon l'impédance cible
  ├────────────────────────────────────┤
  │  Cuivre 35 µm (1 oz)               │  ── Couche 2 (GND — Plan de masse continu)
  │  (Plan de masse GND)               │     ★ Retour de courant propre pour tous les signaux
  ├────────────────────────────────────┤
  │  Noyau (Core)  →  εr ≈ 4.5         │     Épaisseur : typiquement 0.8 à 1.2 mm
  ├────────────────────────────────────┤
  │  Cuivre 35 µm (1 oz)               │  ── Couche 3 (Power — Plans d'alimentation)
  │  (3V3, 5V0, GND, etc.)             │     ★ Découpage en plusieurs îlots de tension
  ├────────────────────────────────────┤
  │  Préimprégné (PP)                  │
  ├────────────────────────────────────┤
  │  Cuivre 35 µm (1 oz)               │  ── Couche 4 (Bottom / Signal / Composants)
  └────────────────────────────────────┘
```

### Calcul de l'impédance caractéristique

Une piste microruban (microstrip) en surface a une impédance caractéristique $Z_0$ approximée par :

$$Z_0 \approx \frac{87}{\sqrt{\varepsilon_r + 1.41}} \cdot \ln\left(\frac{5.98 \cdot h}{0.8 \cdot w + t}\right) \quad [\Omega]$$

Où $h$ est l'épaisseur du diélectrique sous la piste ($mm$), $w$ la largeur de la piste ($mm$), $t$ l'épaisseur du cuivre ($mm$).

Pour une piste différentielle (100 $\Omega$ typique pour USB/Ethernet), les outils CAO comme Altiment Designer intègrent un calculateur d'impédance intégré qui tient compte de la géométrie exacte du stackup.

| Standard | Impédance | Couple différentiel |
|:---|:---:|:---:|
| USB 2.0 / 3.0 | $90\;\Omega$ différentiel | Oui |
| Ethernet 100BASE-TX | $100\;\Omega$ différentiel | Oui |
| HDMI | $100\;\Omega$ différentiel | Oui |
| Antenne RF (GPS, Wi-Fi) | $50\;\Omega$ asymétrique | Non |
| LVDS | $100\;\Omega$ différentiel | Oui |
| Signal numérique standard (SPI, I²C) | $50\;\Omega$ asymétrique | Non |

## Dimensionnement des Pistes et Gestion Thermique

La largeur d'une piste dépend du courant qu'elle doit transporter sans échauffement excessif. La norme **IPC-2152** (remplaçant l'IPC-2221) fournit des abaques et une calculatrice en ligne.

### Ordres de grandeur pour cuivre 35 µm (1 oz) en couche externe (élévation ΔT ≈ 10°C)

| Courant ($A$) | Largeur minimale ($mm$) |
|:---:|:---:|
| $0.5$ | $0.25$ |
| $1.0$ | $0.50$ |
| $2.0$ | $1.15$ |
| $3.0$ | $2.00$ |
| $5.0$ | $4.00$ |
| $10.0$ | $10.00$ |

### Vias thermiques

Pour évacuer la chaleur des composants à forte dissipation (régulateurs linéaires, MOSFET de puissance), utiliser des réseaux de **vias thermiques** sous le plot du composant :

- Diamètre de perçage : $0.3$ à $0.5\;mm$.
- Pas (pitch) des vias : $0.8$ à $1.2\;mm$.
- Relier le plot thermique au plan de masse de la couche interne via des vias non masqués (tented) ou remplis de résine thermoconductrice.

## Règles de Conception CEM pour le Routage

### Séparation des domaines

Ne pas mélanger les retours de courant des signaux analogiques, numériques et de puissance. L'idéal est d'avoir :

1. **Un plan de masse continu sous toute la carte** (couche 2 ou plan de masse dédié).
2. **Des zones distinctes** pour l'analogique, le numérique et la puissance avec des fentes (slots) dans le plan de masse **uniquement** si la séparation galvanique est nécessaire. En règle générale, un plan de masse continu unique est meilleur que des plans fractionnés.

### Routage des signaux haute vitesse

- Éviter les angles à $90°$ (préférer $45°$) pour réduire la discontinuité d'impédance et les émissions.
- Garder les pistes différentielles symétriques et couplées sur toute leur longueur.
- Placer les terminaisons (résistances de $22\;\Omega$ à $33\;\Omega$ en série) le plus près possible de la broche source.
- Longueur maximale de piste non terminée : $L_{max} \approx \frac{t_r}{2 \cdot T_{pd}}$ où $t_r$ est le temps de montée ($ns$) et $T_{pd}$ le délai de propagation par unité de longueur ($\approx 6\;ps/mm$ pour une microstrip).

### Découplage des alimentations

Chaque circuit intégré actif doit avoir des condensateurs de découplage placés le plus près possible de ses broches d'alimentation :

- **Électrolytique / tantale** ($10\;\mu F$ à $100\;\mu F$) : réserve d'énergie basse fréquence.
- **Céramique MLCC** ($100\;nF$ + $10\;nF$) : découplage haute fréquence immédiat (le $100\;nF$ à moins de $3\;mm$ de la broche).
- Vias de retour de masse placés **entre** le condensateur de découplage et le circuit intégré pour minimiser la boucle de courant HF.

## Génération des Fichiers de Fabrication (Gerber)

Le jeu de fichiers Gerber RS-274X standard comprend :

| Fichier | Extension Altium | Contenu |
|:---|:---|:---|
| Top Copper | `.GTL` | Pistes de la couche supérieure |
| Bottom Copper | `.GBL` | Pistes de la couche inférieure |
| Top Solder Mask | `.GTS` | Masque de soudure supérieur (ouvertures) |
| Bottom Solder Mask | `.GBS` | Masque de soudure inférieur |
| Top Silk Screen | `.GTO` | Sérigraphie supérieure (références, logos) |
| Bottom Silk Screen | `.GBO` | Sérigraphie inférieure |
| NC Drill | `.TXT` ou `.DRR` | Coordonnées de perçage et tailles de forets |
| Board Outline | `.GKO` | Contour de la carte (découpe) |
| Paste Mask | `.GTP` / `.GBP` | Pochoir à souder (facultatif) |

**Vérification** : Toujours visualiser les Gerbers dans un visionneur indépendant (ex : **GerbV** ou **ViewMate**) avant d'envoyer au fabricant pour détecter :

- Pistes manquantes ou mal connectées.
- Courts-circuits entre pistes adjacentes.
- Masque de soudure mal positionné (masqué sur des pastilles à souder ou inversement).

## Pièges Courants (Common Pitfalls)

1. **Condensateurs de découplage mal positionnés :**
   - *Erreur :* Placer les condensateurs de découplage à plus de $10\;mm$ des broches d'alimentation des composants numériques (MCU, FPGA, mémoire DDR). L'inductance de la liaison cuivre entre le condensateur et la broche annule l'effet de filtrage HF : la réserve d'énergie locale n'est plus efficace contre les transitoires rapides.
   - *Correction :* Placer chaque condensateur de découplage à moins de $3\;mm$ de la broche d'alimentation correspondante. Le flux de courant doit passer du plan d'alimentation au condensateur, puis du condensateur à la broche (et non l'inverse). Utiliser des vias de retour de masse immédiatement à côté des vias d'alimentation.

2. **Coupures dans le plan de masse (Retour de courant perturbé) :**
   - *Erreur :* Router un signal haute fréquence au-dessus d'une fente, d'une découpe ou d'une zone de cuivre différente dans le plan de masse adjacent. Le courant de retour ne pouvant pas suivre une ligne droite en-dessous du signal, il fait un grand détour, créant une boucle inductive rayonnante qui émet des parasites et dégrade l'intégrité du signal.
   - *Correction :* Ne jamais créer de fentes dans le plan de masse sous des pistes de signaux rapides. Si des îlots d'alimentation fractionnée sont inévitables, placer un pont de cuivre (GND bridge) ou un condensateur de pontage HF entre les deux portions de plan de masse.

3. **Vias non dimensionnés pour le courant de puissance :**
   - *Erreur :* Utiliser un seul via de $0.3\;mm$ pour faire passer $3\;A$ entre deux couches. La section de cuivre dans le via est insuffisante : le via chauffe, se dilate et peut se rompre.
   - *Correction :* Multiplier les vias en parallèle (4 à 6 vias par ampère) ou utiliser des vias de plus grand diamètre ($0.6$ à $1.0\;mm$). La section de cuivre totale des vias doit être au moins égale à la section de la piste qui les alimente.

4. **Angles à $90°$ sur les pistes haute fréquence :**
   - *Erreur :* Router un signal d'horloge (clock) à $50\;MHz$ avec un angle vif à $90°$. L'angle crée une discontinuité capacitive et un point d'émission local.
   - *Correction :* Utiliser des angles à $45°$ ou des courbes en arc de cercle pour les signaux haute vitesse. Pour les fréquences radio (RF, $> 1\;GHz$), utiliser exclusivement des courbes en arc avec un rayon $R \ge 3 \times w$ (où $w$ est la largeur de piste).

5. **Absence de vérification DRC avant envoi au fabricant :**
   - *Erreur :* Exporter les Gerber sans avoir exécuté la Design Rule Check (DRC) dans l'outil CAO. Des erreurs évitables passent en fabrication : court-circuits détectés trop tard, espacements insuffisants pour la tension de claquage, trous trop petits pour le rapport d'aspect.
   - *Correction :* Exécuter la DRC avec les règles de conception paramétrées selon les capacités du fabricant (jeu minimal, espacement cuivre, distance au bord, diamètre minimal de perçage). Corriger toutes les violations avant export. Vérifier visuellement les Gerbers dans un visionneur indépendant.

## Liste de vérification (Checklist)

- [ ] L'empilement des couches (Stackup) et l'épaisseur du cuivre (35 µm, 70 µm) sont définis et validés avec le fabricant de PCB.
- [ ] Les impédances caractéristiques cibles ($50\;\Omega$, $90\;\Omega$, $100\;\Omega$) sont calculées et reportées dans le dossier de fabrication.
- [ ] Les condensateurs de découplage sont placés à moins de $3\;mm$ des broches d'alimentation des composants actifs.
- [ ] La largeur des pistes transportant de la puissance est correctement dimensionnée selon IPC-2152 pour la température ambiante et l'élévation admissible.
- [ ] Le plan de masse est continu sous toutes les pistes de signaux haute vitesse (pas de fentes ni de découpes).
- [ ] Les vias de puissance sont multipliés (plusieurs vias en parallèle) pour supporter le courant sans échauffement excessif.
- [ ] Les règles de conception (DRC — Design Rule Check) ont été exécutées et ne renvoient aucune erreur critique (court-circuit, écartement insuffisant, via non connecté).
- [ ] Les fichiers Gerber (toutes les couches), le fichier de perçage (NC Drill), la nomenclature (BOM) et le fichier Pick & Place sont générés et vérifiés dans un visionneur indépendant.
- [ ] Les composants sont orientés de manière à faciliter la soudure automatique (même direction pour les CMS similaires, espacement suffisant entre les plots pour les pointes de test).
- [ ] Le plan thermique est traité : réseaux de vias thermiques sous les composants dissipant plus de $0.5\;W$.

