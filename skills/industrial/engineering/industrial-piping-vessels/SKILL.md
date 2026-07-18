---
name: industrial-piping-vessels
description: "Concevoir des réseaux de tuyauterie 3D, tracer des isométriques, réaliser des calculs de flexibilité thermique et dimensionner des appareils de chaudronnerie sous pression selon le CODAP et l'ASME VIII."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [piping, pressure-vessels, codap, asme-viii, isometric, chaudronnerie, mechanical-engineering, pipe-stress, thermal-expansion]
  helios:
    related_skills: [cad-bom-automation, cfd-fluid-dynamics, materials-selection-metallurgy]
---

# Tuyauterie Industrielle & Chaudronnerie Sous Pression

## Vue d'ensemble

Cette compétence guide la conception complète des réseaux de tuyauterie industrielle (liquides, gaz, vapeur, fluides chimiques) et le dimensionnement des équipements de chaudronnerie sous pression (cuves, réacteurs, échangeurs, colonnes, ballons). Elle couvre les domaines suivants :

- La **modélisation 3D** de réseaux de tuyauterie (tracé, supports, accessoires) à l'aide d'outils CAO spécialisés (AVEVA E3D, PDMS, Plant 3D, SolidWorks Routing).
- L'**extraction de plans isométriques** pour la fabrication et le montage sur site.
- Les **calculs de flexibilité** par analyse par éléments finis (Caesar II, AutoPIPE, Rohr2) pour amortir les contraintes de dilatation thermique.
- L'application des **codes de calcul réglementaires** : le **CODAP** (Code français de construction des appareils à pression) et l'**ASME Section VIII Division 1** (norme américaine pour les appareils à pression).

La conception de tuyauterie et de chaudronnerie est un domaine fortement réglementé, où une erreur de dimensionnement peut entraîner une fuite, une rupture catastrophique ou une explosion. Chaque calcul doit être documenté et traçable conformément à la réglementation des équipements sous pression (DESP 2014/68/UE en Europe).

Cette compétence est conçue pour être actionnée par l'agent Helios lorsque l'utilisateur exprime un besoin lié à la conception, au dimensionnement ou à l'analyse de réseaux de tuyauterie ou d'équipements sous pression.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Concevoir le tracé en 3D d'une ligne de tuyauterie entre plusieurs équipements industriels.
- Analyser un plan isométrique de tuyauterie (identification des symboles, vannes, brides, soudures, pentes).
- Calculer l'épaisseur minimale de paroi d'une cuve sous pression (formules CODAP ou ASME).
- Dimensionner des supports de tuyauterie fixes (ancres, guides) ou flexibles (ressorts, lyres de dilatation).
- Définir la classe de tuyauterie (Piping Class / Material Class) adaptée à un fluide donné (corrosif, haute température, toxique).
- Analyser les efforts sur les buses d'équipements (pompes, échangeurs, réacteurs) pour éviter la déformation des raccordements.
- Rédiger un cahier des charges technique pour la fabrication d'un équipement sous pression.

---

## Dimensionnement d'équipements sous pression (CODAP / ASME VIII)

### Formule d'épaisseur de paroi (ASME Section VIII Div. 1)

Pour une **virole cylindrique** soumise à une pression interne $P$, l'épaisseur minimale requise $t$ est :

$$t = \frac{P \cdot R}{S \cdot E - 0.6 \cdot P} + C$$

Où :
- $t$ : Épaisseur minimale requise de la paroi ($\mathrm{mm}$).
- $P$ : Pression de conception interne ($\mathrm{MPa}$). Doit être au moins égale à la pression maximale de service majorée.
- $R$ : Rayon intérieur de la virole ($\mathrm{mm}$).
- $S$ : Valeur de contrainte maximale admissible du matériau ($\mathrm{MPa}$) à la température de conception. Donnée dans les tables ASME II Part D ou CODAP Annexe P.
- $E$ : Efficacité du joint soudé :
  - $E = 1.0$ : Joint radiographié à 100 % (contrôle intégral).
  - $E = 0.85$ : Joint soumis à un contrôle radiographique par points (spot).
  - $E = 0.70$ : Joint non radiographié (assemblage sans contrôle, sous conditions).
- $C$ : Surépaisseur de corrosion ($\mathrm{mm}$) ajoutée pour compenser la perte de métal dans le temps. Valeurs typiques :
  - Acier au carbone en milieu non corrosif : $1.5$ à $3\,\mathrm{mm}$.
  - Acier en milieu acide ou présentant du $H_2S$ : $3$ à $6\,\mathrm{mm}$.
  - Inox en milieu neutre : $0\,\mathrm{mm}$.

### Formule pour les fonds bombés (ASME VIII)

Pour un **fond bombé hémisphérique** (torisphérique) soumis à une pression interne :

$$t = \frac{P \cdot L \cdot M}{2 \cdot S \cdot E - 0.2 \cdot P} + C$$

Où $L$ est le rayon intérieur du bombement et $M$ un facteur dépendant du rapport $L/r$ (rayon intérieur / rayon de carre).

### Règle de pression d'épreuve (hydrotest)

Après fabrication, l'équipement doit subir une épreuve hydraulique à :

$$P_{test} = 1.43 \times P_{conception}$$

Sous cette pression, la contrainte dans la paroi ne doit pas dépasser $0.9 \times R_e$ (90 % de la limite élastique).

---

## Tuyauterie : Classification et spécification

### Piping Class (Classe de tuyauterie)

Une *Piping Class* est un document (tableau ou base de données) qui définit pour chaque diamètre nominal (DN) les composants standardisés utilisables : matériau du tube, type de brides (PN/Class), type de vannes, joints, visserie.

**Exemple de Piping Class simplifié (Acier au carbone / vapeur 16 bar) :**

| DN | Tube (OD × ép.) | Bride | Vanne | Joint | Visserie |
|:---|:---------------|:------|:------|:------|:---------|
| 25 | 33.7 × 2.6 | PN16 EN 1092-1 | Robinet à soupape A216 WCB | Spirale métallique | A2-70 |
| 50 | 60.3 × 2.9 | PN16 EN 1092-1 | Robinet à boisseau A216 WCB | Spirale métallique | A2-70 |
| 80 | 88.9 × 3.2 | PN16 EN 1092-1 | Vanne à opercule A216 WCB | Spirale métallique | A2-70 |
| 100 | 114.3 × 3.6 | PN16 EN 1092-1 | Vanne à opercule A216 WCB | Spirale métallique | A2-70 |

### Code de tuyauterie (ASME B31.3 / EN 13480)

| Code | Domaine | Application |
|:----|:--------|:------------|
| ASME B31.1 | Power Piping | Centrales électriques, vapeur, eau surchauffée |
| ASME B31.3 | Process Piping | Raffineries, usines chimiques, pharmaceutiques |
| ASME B31.8 | Gas Transmission | Gazoducs, canalisations de transport de gaz |
| EN 13480 | Tuyauteries industrielles métalliques | Norme européenne, équivalent à B31.3 |

---

## Flexibilité et dilatations thermiques

Les fluides chauds (vapeur à 200 °C, eau chaude à 120 °C, gaz chauds) provoquent la dilatation thermique du métal des tubes. La dilatation linéaire $\Delta L$ est :

$$\Delta L = L_0 \cdot \alpha \cdot \Delta T$$

Où $\alpha$ est le coefficient de dilatation linéaire ($\mathrm{m/m\cdot K}$) :
- Acier au carbone : $12 \times 10^{-6}$
- Inox 304L : $16 \times 10^{-6}$
- Aluminium : $23 \times 10^{-6}$

**Exemple :** Une ligne de vapeur en acier au carbone de $50\,\mathrm{m}$ de long, de $20$ à $200\,\mathrm{°C}$ se dilate de $\Delta L = 50 \times 12\times10^{-6} \times 180 = 0.108\,\mathrm{m} = 108\,\mathrm{mm}$.

Si la ligne est bloquée entre deux points fixes sans possibilité de déformation, les forces générées peuvent atteindre plusieurs dizaines de tonnes, détruisant les supports, les brides ou les raccordements sur les machines.

### Solutions pour absorber la dilatation

1. **Lyres de dilatation en U** (ou U-bends) : Insertion volontaire d'un coude en forme de U qui se déforme élastiquement lors de la dilatation.
2. **Changements de direction naturels** : Utilisation des coudes à 90° existants dans le tracé pour créer de la flexibilité.
3. **Compensateurs de dilatation** : Soufflets métalliques (bellows) insérés dans la ligne pour absorber les déplacements axiaux, latéraux ou angulaires.
4. **Boucles coulissantes** : Supports à rouleaux ou glissières permettant le mouvement longitudinal du tube.

### Représentation d'une lyre en U

```text
    Point fixe A ───────┐                   ┌─────── Point fixe B
                        │                   │
                        │    ┌─────────┐    │
                        │    │         │    │
                        └────┘         └────┘
                             │         │
                             │         │
                             │         │
                             ▼         ▼
                        (Mouvement libre)
```

---

## Plans isométriques de tuyauterie

Un plan isométrique (isometric drawing) est une représentation 3D en perspective cavalière d'une ligne de tuyauterie, utilisée pour la fabrication et le montage. Il contient :

- Tous les **tronçons de tube** avec leurs dimensions (longueurs, diamètres, épaisseurs).
- Les **coudes**, **tés**, **réductions**, **brides**, **vannes** avec leurs références.
- Les **soudures** numérotées avec leur type (bout à bout, à recouvrement, d'angle).
- Les **supports** (ancres, guides, ressorts) et leurs localisations.
- Les **pentes** et les points hauts/bas (vents, purges).
- Le **nuancier** des matériaux (spécification du tube, des vannes, des joints).

**Symboles normalisés (ISO 10628 / ANSI/ISA S5.1) :**

```text
Vanne à opercule ────┤├────      (vue ouverte)
Vanne à boisseau ────⟨⟩────
Clapet anti-retour ────⟩────
Robinet à soupape ────∩∩────
Bride ────┬┬──── ou ────╥╥────
Coude 90° ────└┘────
Réduction concentrique ────>│<────
Soudure ────••──── ou ────∥∥────
```

---

## Supportage de tuyauterie

### Types de supports

| Type | Fonction | Exemple |
|:----|:---------|:--------|
| **Ancre (Anchor)** | Bloque tout mouvement (axial, latéral, vertical) | Point fixe au raccordement d'une machine |
| **Guide** | Autorise le mouvement axial, bloque le mouvement latéral | Rail de guidage pour ligne vapeur |
| **Support à ressort** | Supporte une charge variable (dilatation verticale) | Compensateur à ressort hélicoïdal |
| **Support coulissant** | Autorise le glissement longitudinal | Plaque PTFE sur longeron métallique |
| **Élingue / Berceau** | Support suspendu (plafond, structure) | Tige filetée + collier de tuyau |

### Règle de placement des supports

- Distance entre supports : consultez les abaques de portée maximale (span tables ASME B31.1 ou EN 13480).
- Placer un support à moins de $300\,\mathrm{mm}$ de chaque bride lourde (vanne, filtre, clapet).
- Ne pas supporter une ligne sur une bride de machine (pompe, réacteur) sans support dédié adjacent.

---

## Pièges Courants (Common Pitfalls)

### 1. Ignorer l'épaisseur de corrosion dans les calculs d'épaisseur

**Erreur :** Calculer l'épaisseur de paroi théorique d'une cuve en acier au carbone transportant un fluide acide (pH 4) sans ajouter de surépaisseur de corrosion. L'acier se corrode à une vitesse de $0.2$ à $0.5\,\mathrm{mm/an}$ dans ce milieu ; après 10 ans, la paroi peut perdre $3$ à $5\,\mathrm{mm}$, réduisant sa résistance mécanique et créant un risque de rupture catastrophique.

**Correction :** Toujours vérifier l'agressivité chimique du fluide avec un tableau de compatibilité chimique (ex : guide de résistance chimique des matériaux). Ajouter la valeur de surépaisseur de corrosion $C$ (conformément à l'ASME VIII Div. 1 ou au CODAP) à l'épaisseur calculée. Pour les milieux très corrosifs, envisager un revêtement intérieur (ébonite, PTFE, émail) ou un matériau noble.

### 2. Raccorder des tuyauteries directement sur des buses de machines sans supportage proche

**Erreur :** Laisser le poids d'une ligne de tuyauterie lourde (remplie de liquide, calorifugée) reposer entièrement sur les brides de raccordement d'une pompe centrifuge ou d'un réacteur. Le poids et les contraintes thermiques déforment les buses, provoquent un désalignement de l'arbre de la pompe (vibrations, usure prématurée des roulements), et peuvent fissurer la tubulure de l'équipement.

**Correction :** Placer un support de tuyauterie rigide (ancre) à moins de $300\,\mathrm{mm}$ de la bride de raccordement de chaque machine. Sur les lignes chaudes ($\Delta T > 150\,\mathrm{°C}$), installer un support à ressort calibré pour suivre le mouvement vertical de dilatation sans transmettre d'effort excessif à la buse.

### 3. Oublier les pentes de vidange et les points de purge

**Erreur :** Concevoir un réseau de tuyauterie vapeur sans pente directionnelle (ni montante ni descendante). La vapeur se condense en eau dans les points bas du réseau ; l'eau stagnante crée des coups de bélier violents (water hammer) qui peuvent rompre les canalisations, les supports et les appareils raccordés.

**Correction :** Prévoir une pente minimale de $1\%$ (1 cm par mètre) dans le sens de l'écoulement de la vapeur. Installer des purgeurs de vapeur (thermostatiques, mécaniques ou thermodynamiques) à tous les points bas du réseau, ainsi que des chasses de vidange pour la maintenance.

### 4. Négliger l'analyse des charges sur les buses (Nozzle Loads)

**Erreur :** Fixer des lignes de tuyauterie sur un échangeur à calandre sans vérifier les efforts transmis aux buses. L'ASME VIII / CODAP imposent des limites d'efforts admissibles sur les tubulures des appareils à pression. Si ces limites sont dépassées, la tubulure se fissure en fatigue sous l'effet des cycles thermiques.

**Correction :** Réaliser une analyse de flexibilité (calculs Caesar II, AutoPIPE) incluant les charges sur les buses. Vérifier les résultats par rapport aux charges admissibles fournies par le fabricant de l'équipement (nozzle load tables). Si dépassement, ajouter de la flexibilité dans la ligne (lyre, compensateurs) ou renforcer la buse (pad de renfort).

---

## Liste de vérification (Checklist)

- [ ] L'épaisseur calculée de la paroi de l'équipement sous pression intègre les tolérances de fabrication de la tôle et la surépaisseur de corrosion.
- [ ] L'efficacité de joint soudé ($E$) choisie correspond au taux de contrôle non destructif (radiographie, ultrasons) spécifié sur le plan de soudage.
- [ ] Les lignes de tuyauterie chaude ($\Delta T > 100\,\mathrm{°C}$) intègrent des lyres de dilatation ou des coudes suffisants pour absorber les déplacements thermiques.
- [ ] Les pentes de tuyauterie nécessaires à la vidange (ex : $1\%$ pour les lignes vapeur et condensats) sont représentées sur les isométriques.
- [ ] Le matériau choisi pour la visserie de serrage des brides est compatible avec la température et la pression de service.
- [ ] Une analyse de flexibilité (Caesar II ou équivalent) a été réalisée pour les lignes critiques (haute température, grands diamètres, raccordement sur machines).
- [ ] Les supports de tuyauterie sont dimensionnés et positionnés conformément aux portées maximales (span tables) du code applicable.
- [ ] La Piping Class (spécification de ligne) est définie pour chaque service (fluide, pression, température, corrosivité).
- [ ] Les points de purge, de vent, et de drainage sont identifiés et accessibles pour la maintenance.
- [ ] Les dossiers de fabrication sont conformes à la DESP (Directive Équipements Sous Pression 2014/68/UE) avec les attestations de conformité appropriées.

