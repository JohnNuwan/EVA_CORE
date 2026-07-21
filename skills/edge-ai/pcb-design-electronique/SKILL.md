---
name: pcb-design-electronique
description: "Concevoir des circuits imprimés (PCB) multicouches avec KiCad, Altium Designer et Eagle — schématique, routage, règles de conception, fabrication et assemblage."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [pcb, circuit-imprime, kicad, altium, eagle, gerber, routing, emc, signal-integrity, power-integrity, dfm, smd, through-hole, via, stackup]
    related_skills: [electrical-schematics-eplan, pcb-design-altium, embedded-systems-firmware, fpga-verilog-vhdl]
---

# Conception de Circuits Imprimés (PCB Design)

## Vue d'ensemble

La conception de circuits imprimés (PCB — Printed Circuit Board) transforme un schéma électronique en un substrat physique qui relie mécaniquement et électriquement les composants. Cette compétence couvre l'ensemble du flux de conception : de la capture de schématique et du choix des composants jusqu'à la génération des fichiers de fabrication (Gerber, Drill, Pick-and-Place) et la qualification de l'assemblage.

### Flux de conception typique

```
┌─────────────────┐    ┌──────────────┐    ┌───────────────┐    ┌──────────────┐
│   Cahier des    │───▶│   Schéma     │───▶│  Placement    │───▶│   Routage    │
│   charges       │    │  (Capture)   │    │  Composants   │    │  (Routing)   │
└─────────────────┘    └──────────────┘    └───────────────┘    └──────┬───────┘
                                                                       │
┌─────────────────┐    ┌──────────────┐    ┌───────────────┐          │
│    Retour       │◀───│   Fabrication│◀───│    Vérif.     │◀─────────┘
│   d'expérience  │    │   (Gerber)   │    │   (DRC/ERC)   │
└─────────────────┘    └──────────────┘    └───────────────┘
```

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Capturer un schéma électrique et le transformer en PCB (placement + routage).
- Dimensionner les largeurs de pistes pour un courant donné et choisir les couches du stackup.
- Appliquer les règles de conception (DRC) pour une fabrication fiable (DFM — Design for Manufacturing).
- Résoudre des problèmes d'intégrité de signal (terminaisons, adaptation d'impédance, cross-talk).
- Concevoir l'empilement (stackup) pour un PCB multicouche (4, 6, 8 couches) avec plans de masse et d'alimentation.
- Générer les fichiers de sortie (Gerber X2, Drill, IPC-356 netlist) et les transmettre à un fabricant (JLCPCB, PCBWay, Eurocircuits).

Ne pas utiliser pour : la conception de schémas électriques industriels (utiliser `electrical-schematics-eplan`), la simulation de circuits (SPICE) purement théorique sans PCB.

---

## 1. Capture de Schématique

### 1.1 Choix du logiciel CAO

| Logiciel | Licence | Points forts | Limites |
|:---|---:|:---|:---|
| **KiCad 8** | Open source (GPL) | Gratuit, communauté active, push&shove router, 3D viewer | Interface moins polie qu'Altium |
| **Altium Designer** | Commercial ($) | Intégration complète, règles de conception avancées, simulation intégrée | Coût élevé, Linux via VM |
| **EAGLE** | Freemium (Autodesk) | Large bibliothèque, intégration Fusion 360 | Limité en couches sur version gratuite |
| **OrCAD / Allegro** | Commercial ($$) | Standard industriel, simulation PSpice | Courbe d'apprentissage raide |

### 1.2 Règles de schématique

```text
R1  RÈGLES GÉNÉRALES DE SCHÉMATIQUE
- Chaque composant a une référence unique (R1, C3, U2) et une valeur.
- Les nœuds d'alimentation sont nommés : VCC_3V3, GND, VIN_12V.
- Les signaux critiques sont étiquetés : SPI_CLK, I2C_SDA, ADC_IN0.
- Les condensateurs de découplage (100 nF) sont placés à côté de chaque pin d'alimentation de CI.
- Les résistances de pull-up I²C (4k7) sont indiquées avec leur valeur.
- Les connecteurs ont des broches numérotées et nommées ; le brochage est vérifié avec la datasheet.
```

### 1.3 Hiérarchie de schématique (KiCad)

```
Projet/
├── Projet.kicad_sch           # Schéma racine
├── Projet.kicad_pcb           # PCB
├── Modules/                   # Sous-schémas hiérarchiques
│   ├── PowerSupply.kicad_sch  # Alimentation
│   ├── MCU_Core.kicad_sch     # Microcontrôleur
│   └── Sensor.kicad_sch       # Capteur
└── Libraries/                 # Bibliothèques locales
    ├── custom-components.pretty/   # Empreintes
    └── custom-symbols.kicad_sym    # Symboles
```

---

## 2. Empilement (Stackup) et Plans

### 2.1 PCB 2 couches (projets simples, <100 MHz)

```
┌─────────────────────┐ Couche 1 : Signaux + Alimentation
│       ████████       │
├─────────────────────┤
│ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ │ Couche 2 : Plan de masse (GND)
└─────────────────────┘
```

**Épaisseur typique :** 1,6 mm (standard), cuivre 1 oz (35 µm) pour courant ≤ 1 A par mm de largeur.

### 2.2 PCB 4 couches (signaux rapides, >100 MHz, CEM)

```
┌─────────────────────┐ Couche 1 : Signaux (Top)
├─────────────────────┤ Couche 2 : Plan de masse (GND) — retour de courant propre
├─────────────────────┤ Couche 3 : Plan d'alimentation (VCC)
└─────────────────────┘ Couche 4 : Signaux (Bottom)
```

**Avantages :** Impédance contrôlée, boucles de courant minimisées, blindage naturel entre couches.

### 2.3 PCB 6 couches (complexe, haute densité, RF)

```
Couche 1 : Signaux haute vitesse
Couche 2 : Plan de masse (GND)
Couche 3 : Signaux + Alimentation stripline
Couche 4 : Plan de masse (GND)
Couche 5 : Signaux
Couche 6 : Plan de masse (GND) + signaux lents
```

### 2.4 Règles d'empilement

```text
R2  RÈGLES DE STACKUP
- Les plans de masse adjacents aux couches de signaux assurent un plan de référence propre.
- Éviter les fentes (slots) dans le plan de masse — elles forment des antennes.
- Signaux haute vitesse (RF, Ethernet, USB) sur une couche adjacente à un plan GND.
- Utiliser des microstrip (couche externe) ou stripline (couche interne) pour le contrôle d'impédance.
- Distance minimale entre cuivre et bord du PCB ≥ 0,3 mm (sauf si chanfrein).
```

---

## 3. Dimensionnement des Pistes

### 3.1 Largeur de piste en fonction du courant (IPC-2221, cuivre 1 oz, 10°C d'élévation)

| Courant (A) | Largeur externe (mm) | Largeur interne (mm) |
|:---:|---:|---:|
| 0,5 | 0,25 | 0,50 |
| 1,0 | 0,50 | 1,00 |
| 2,0 | 1,00 | 2,00 |
| 3,0 | 1,80 | 3,60 |
| 5,0 | 4,00 | 8,00 |
| 10,0 | 12,00 | — |

**Formule simplifiée (externe, 1 oz) :**
$$W = \frac{I}{0.048 \times \Delta T^{0.44}}$$

Où $W$ = largeur en mm, $I$ = courant en A, $\Delta T$ = élévation de température en °C.

### 3.2 Espacement entre pistes

| Tension (V) | Espacement minimal (mm) |
|:---:|---:|
| < 50 | 0,15 |
| 50–150 | 0,40 |
| 150–300 | 0,80 |
| 300–600 | 1,50 |
| > 600 | selon norme IPC-2221B |

---

## 4. Placement des Composants

### 4.1 Ordre de placement prioritaire

```text
R3  RÈGLES DE PLACEMENT
1. Connecteurs (alimentation, signaux, programmation).
2. Alimentations (régulateurs, convertisseurs DC-DC) — au plus près de l'entrée.
3. Microcontrôleur / FPGA — au centre du PCB.
4. Condensateurs de découplage — à moins de 3 mm de chaque pin d'alimentation.
5. Quartz / oscillateurs — à moins de 10 mm du CI, piste la plus courte possible.
6. Composants analogiques sensibles — éloignés des sources de bruit (DC-DC, horloges).
7. Éléments de réglage (boutons, LEDs, trimmers) — en bordure selon l'ergonomie.
```

### 4.2 Condensateurs de découplage

```python
# Estimation du nombre de condensateurs de découplage
def decoupling_caps(n_pins_vcc: int, max_current_a: float) -> list:
    """
    Calcule la configuration de découplage typique.
    1 × 10 µF (tantale ou MLCC) par groupe de 4-6 pins VCC
    + 1 × 100 nF (MLCC 0402/0603) par pin VCC.
    """
    bulk_caps = max(1, n_pins_vcc // 4)
    bypass_caps = n_pins_vcc
    return {
        "bulk_capacitors": [{"value": "10 µF", "count": bulk_caps}],
        "bypass_capacitors": [{"value": "100 nF", "count": bypass_caps}],
        "total_mlcc": bulk_caps + bypass_caps,
    }

# Exemple : STM32F407 avec 8 pins VCC, 500 mA
caps = decoupling_caps(8, 0.5)
print(caps)
# {'bulk_capacitors': [{'value': '10 µF', 'count': 2}],
#  'bypass_capacitors': [{'value': '100 nF', 'count': 8}],
#  'total_mlcc': 10}
```

---

## 5. Routage

### 5.1 Stratégie de routage

```text
R4  RÈGLES DE ROUTAGE
1. Commencer par les pistes critiques : horloges, signaux haute vitesse, alimentations.
2. Signaux analogiques et numériques séparés — ne pas les mélanger dans le même canal.
3. Éviter les angles droits (90°) — utiliser des angles à 45° ou des courbes.
4. Paires différentielles (USB, Ethernet, LVDS, HDMI) :
   - Écart constant entre les deux pistes de la paire.
   - Longueurs appariées (length matching) à ±0,5 mm près pour USB 2.0.
5. Via stitching : placer des vias de masse régulièrement (tous les 5-10 mm) pour relier les plans GND.
6. Garder une distance minimale entre les vias et les pastilles SMD.
7. Aucune piste ne doit former une boucle fermée (antenne).
```

### 5.2 Paires différentielles — impédance et géométrie

| Standard | Impédance différentielle | Largeur piste (mm) | Écart (mm) |
|:---|---|---:|---:|
| USB 2.0 | 90 Ω | 0,35 | 0,20 |
| Ethernet 100BASE-TX | 100 Ω | 0,30 | 0,25 |
| HDMI | 100 Ω | 0,25 | 0,15 |
| LVDS | 100 Ω | 0,30 | 0,30 |
| RS-485 | 120 Ω | 0,40 | 0,40 |

### 5.3 Vias — types et dimensions

| Type | Perçage (mm) | Pad (mm) | Usage |
|:---|---|---:|:---|
| Via standard | 0,30 | 0,60 | Signaux, coût faible |
| Micro-via (HDI) | 0,10 | 0,25 | Haute densité, BGA fin pitch |
| Via borgne (blind) | 0,20 | 0,45 | Connexion couche externe → interne |
| Via noyé (buried) | 0,20 | 0,45 | Connexion entre couches internes |
| Via de masse thermique | 0,50 | 1,00 | Dissipation thermique, forte puissance |

**Rapport d'aspect :** Épaisseur du PCB / Diamètre du perçage ≤ 10 (idéal ≤ 8).

---

## 6. DFM (Design for Manufacturing)

### 6.1 Contraintes typiques de fabrication

| Paramètre | Standard | Avancé | Coût |
|:---|---:|---:|:---:|
| Taille minimale de piste | 0,15 mm (6 mil) | 0,10 mm (4 mil) | +20 % |
| Espacement minimal | 0,15 mm (6 mil) | 0,10 mm (4 mil) | +20 % |
| Perçage minimal | 0,30 mm | 0,20 mm | +30 % |
| Anneau annulaire minimal | 0,15 mm | 0,10 mm | +15 % |
| Taille minimale SMD | 0603 (1,6×0,8 mm) | 0201 (0,6×0,3 mm) | +50 % |
| Tolérance de perçage | ±0,08 mm | ±0,05 mm | +10 % |

### 6.2 Règles DFM essentielles

```text
R5  RÈGLES DFM
- Placer des fiduciaires (3 points, coins opposés) pour l'assemblage automatique.
- Pas de pastilles isolées (rappel : anneau annulaire minimum).
- Tous les composants sont espacés d'au moins 0,5 mm les uns des autres.
- Les vias ne sont pas placés sous les composants SMD (sauf vias-in-pad spécifiés).
- Sérigraphie : traits ≥ 0,15 mm, texte ≥ 0,6 mm de hauteur, orientation lisible.
- Plan de coupure (routage) : largeur minimum 2 mm (fraise ou V-cut).
- Ajouter des points de test (TP) pour chaque nœud critique : alimentations, signaux de debug.
```

### 6.3 Fichiers de sortie (Gerber X2)

```bash
# Structure des fichiers Gerber X2 pour un PCB 4 couches
Projet/
├── Projet.GTL      # Top cuivre
├── Projet.GTO      # Top sérigraphie
├── Projet.GTS      # Top masque de soudure
├── Projet.GTP      # Top pâte à souder
├── Projet.GL2      # Couche interne 2 (GND)
├── Projet.GL3      # Couche interne 3 (VCC)
├── Projet.GBL      # Bottom cuivre
├── Projet.GBO      # Bottom sérigraphie
├── Projet.GBS      # Bottom masque de soudure
├── Projet.GBP      # Bottom pâte à souder
├── Projet.GKO      # Contour
├── Projet.TXT      # Forages (Excellon)
└── Projet.IPC-356  # Netlist pour test électrique
```

---

## 7. Simulation et Vérification

### 7.1 DRC (Design Rule Check)

```python
# Exemple de règles DRC personnalisées (KiCad Python API)
drc_rules = {
    "clearance": {"min_track_track": 0.15,   # mm
                  "min_track_pad": 0.15,
                  "min_pad_pad": 0.15,
                  "min_track_via": 0.15},
    "track_width": {"min": 0.15, "max": 10.0},
    "via": {"min_drill": 0.3, "min_diameter": 0.6},
    "hole_size": {"min": 0.3},
    "silk_to_solder": {"min": 0.2},
    "copper_to_board_edge": {"min": 0.3},
    "micro_vias": {"allowed": True,
                   "min_drill": 0.1,
                   "max_stack": 2},
}
```

### 7.2 Vérification de l'intégrité de signal (SI)

```python
# Estimation du temps de montée et de la longueur critique
def signal_integrity_check(freq_mhz: float, er: float = 4.5) -> dict:
    """
    Calcule les paramètres d'intégrité de signal.

    Paramètres :
        freq_mhz : fréquence du signal (MHz)
        er       : constante diélectrique du substrat (FR-4 ≈ 4,5)

    Retourne :
        temps de montée, vitesse de propagation, longueur critique
    """
    c = 3e8  # Vitesse de la lumière (m/s)
    t_rise = 0.35 / (freq_mhz * 1e6)  # Loi du 10-90 %
    v_prop = c / (er ** 0.5)          # Vitesse dans le substrat (m/s)
    critical_length = t_rise * v_prop  # Longueur critique (m)

    return {
        "frequence_mhz": freq_mhz,
        "temps_montee_ns": t_rise * 1e9,
        "vitesse_propagation_m_s": v_prop,
        "longueur_critique_mm": critical_length * 1000,
        "terminaison_necessaire": critical_length * 1000 < 150,  # Si longueur piste > 150 mm
    }

# Vérification pour un signal SPI à 20 MHz
check = signal_integrity_check(20)
print(f"Longueur critique : {check['longueur_critique_mm']:.1f} mm")
# Longueur critique : 1312.0 mm — pas besoin de terminaison pour SPI
```

---

## 8. Gestion Thermique

### 8.1 Dissipation par vias thermiques

```python
def thermal_vias(power_w: float, temp_rise_c: float = 20) -> dict:
    """
    Calcule le nombre de vias thermiques nécessaires.

    Un via de 0,3 mm de perçage dans un PCB standard conduit
    environ 0,2 W de chaleur par 10 °C d'élévation.
    """
    thermal_resistance_via = 50  # °C/W pour un via standard 0,3 mm
    required_conductance = power_w / temp_rise_c
    n_vias = int(required_conductance * thermal_resistance_via) + 1

    return {
        "puissance_w": power_w,
        "elevation_temp_c": temp_rise_c,
        "vias_necessaires": max(n_vias, 4),  # Au moins 4 vias
        "motif": "grille 4×4 avec pas de 1,0 mm",
        "diametre_via_mm": 0.3,
    }

# Régulateur 3,3 V dissipant 1,5 W
vias = thermal_vias(1.5, 15)
print(f"Vias thermiques : {vias['vias_necessaires']}")
```

### 8.2 Copper pour (cuivre massif)

```text
R6  RÈGLES THERMIQUES
- Les zones de cuivre massif (copper pour) sont utilisées pour les composants dissipant > 0,5 W.
- Relier le plan de masse au copper pour par au moins 4 vias thermiques.
- Éviter les îlots de cuivre flottants — les connecter à GND ou VCC.
- La température maximale du PCB ne doit pas dépasser la Tg du substrat :
  - FR-4 standard : Tg ≈ 130-140 °C.
  - FR-4 haute Tg : Tg ≈ 170-180 °C (recommandé pour assembler des composants > 100 °C).
  - Polyimide : Tg > 260 °C (haute température, coût élevé).
```

---

## Pièges Courants

1. **Condensateurs de découplage mal placés :** Un condensateur 100 nF placé à > 5 mm de la broche d'alimentation d'un CI rapide perd toute efficacité à cause de l'inductance de la piste. Placer au plus près avec un via de masse directement sur la pastille GND.

2. **Plan de masse fragmenté :** Une fente (slot) dans le plan GND sous une piste haute vitesse force le courant de retour à faire un détour, créant une boucle rayonnante. Ne jamais fendre le plan GND sous les signaux rapides.

3. **Angles droits à 90° :** Bien que l'effet soit souvent exagéré pour les signaux lents, les angles droits créent une variation d'impédance et un point de concentration de contrainte chimique. Toujours utiliser des angles à 45° ou des courbes.

4. **Empilement asymétrique :** Un stackup asymétrique (différentes épaisseurs de cuivre ou de préimprégné de chaque côté du cœur) provoque un cintrage du PCB lors de la fabrication et du refroidissement. Toujours symétriser le stackup.

5. **Anneau annulaire insuffisant :** Un perçage trop proche du bord de la pastille laisse un anneau annulaire < 0,05 mm et le trou casse la pastille à la fabrication. Respecter l'anneau annulaire minimum.

6. **Vias non bouchés sous les composants BGA :** Les vias non remplis sous un BGA créent des vides de soudure et des courts-circuits. Utiliser des vias bouchés (filled & capped) ou décaler les vias hors de la zone BGA.

7. **Mélange des retours de courant analogiques et numériques :** Les courants de retour numériques qui traversent la zone analogique injectent du bruit haute fréquence. Séparer les plans GND analogique et numérique avec un pont (0 Ω ou ferrite) et placer tous les signaux cross-domain sur ce pont.

---

## Liste de vérification (Checklist)

- [ ] Le schéma est revu et chaque composant a une référence unique avec valeur.
- [ ] L'empilement (stackup) est symétrique et adapté au nombre de couches.
- [ ] Les largeurs de piste sont dimensionnées pour le courant de chaque signal.
- [ ] Les condensateurs de découplage sont placés à moins de 3 mm de chaque pin VCC.
- [ ] Les paires différentielles ont une impédance contrôlée et des longueurs appariées.
- [ ] Le DRC (Design Rule Check) passe sans erreur (clearance, largeur, perçage).
- [ ] Aucun angle droit à 90° dans le routage.
- [ ] Les vias thermiques sont dimensionnés pour la puissance dissipée.
- [ ] Les fichiers Gerber X2 et Drill sont générés et validés avec un visualiseur (Gerbv, ZofzPCB).
- [ ] La sérigraphie est lisible et orientée correctement.
- [ ] Les plans de masse sont continus sous les signaux haute vitesse.
- [ ] Séparation nette entre zones analogiques et numériques.
- [ ] Points de test (TP) pour chaque nœud critique.
- [ ] Le fabricant cible (JLCPCB, PCBWay) peut fabriquer les contraintes définies.