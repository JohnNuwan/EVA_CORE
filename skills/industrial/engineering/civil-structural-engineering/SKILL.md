---
name: civil-structural-engineering
description: "Dimensionner les structures métalliques (charpentes, supports de tuyauterie, passerelles) et les dalles de fondation pour machines industrielles selon les Eurocodes."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [civil-engineering, structural, eurocodes, steel-structure, concrete, foundation, structural-analysis, buckling, steel-design]
  EVA:
    related_skills: [fea-structural-analysis, cad-bom-automation, industrial-piping-vessels]
---

# Génie Civil & Calcul de Structures Métalliques

## Vue d'ensemble

Cette compétence guide le calcul, le dimensionnement et la validation des structures porteuses métalliques et des fondations en béton armé pour les installations industrielles. Elle couvre les éléments suivants :

- **Structures métalliques** : Charpentes de bâtiments industriels, passerelles d'accès et de service, racks de tuyauterie (pipe racks), potences portiques, mezzanines.
- **Fondations industrielles** : Dalles de fondation pour équipements lourds et vibrants, massifs de réception pour machines tournantes, semelles et pieux pour poteaux de charpente.
- **Ouvrages en béton armé** : Murs de soutènement, cuves enterrées, dallages industriels, fosses techniques.

L'ensemble des calculs s'appuie sur les **Eurocodes**, le référentiel normatif européen unifié pour la conception et le calcul des structures de construction :

| Domaine | Eurocode | Désignation |
|:-------|:---------|:------------|
| Actions sur les structures | EN 1990 + EN 1991 | EC 0 — Bases de calcul + EC 1 — Actions |
| Structures en béton | EN 1992 | EC 2 |
| Structures en acier | EN 1993 | EC 3 |
| Structures mixtes acier-béton | EN 1994 | EC 4 |
| Structures en aluminium | EN 1999 | EC 9 |

Cette compétence est conçue pour être actionnée par l'agent EVA lorsque l'utilisateur exprime un besoin lié au dimensionnement, à la vérification ou à l'optimisation d'ouvrages de génie civil industriel.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Dimensionner des poutres de charpente métallique (profilés IPE, HEA, HEB, IPN) pour supporter une charge donnée (descente de charges).
- Concevoir ou vérifier le supportage de lignes de tuyauterie lourdes sur un rack métallique.
- Calculer le ferraillage et l'épaisseur d'une dalle de fondation en béton pour une machine tournante générant des vibrations.
- Appliquer les coefficients de pondération des charges aux États Limites Ultimes (ELU) et États Limites de Service (ELS).
- Dimensionner des assemblages boulonnés ou soudés structurels (plaques de continuité, goussets, pieds de poteaux).
- Vérifier la stabilité globale d'une structure au vent et aux séismes (contreventements).
- Analyser le comportement au flambement de poteaux comprimés.

---

## Notions fondamentales : États Limites et combinaisons d'actions

### États Limites Ultimes (ELU)

L'ELU vérifie que la structure ne s'effondre pas et ne subit pas de ruine : résistance mécanique, stabilité de forme, fatigue, équilibre statique.

**Combinaison d'actions fondamentale (ELU — STR/GEO) :**

$$S_d = 1.35 \cdot G_{sup} + 1.0 \cdot G_{inf} + 1.5 \cdot Q_{k,1} + \sum_{i>1} 1.5 \cdot \psi_{0,i} \cdot Q_{k,i}$$

Où :
- $G$ : Charges permanentes (poids propre de la structure, des équipements fixes, des tuyauteries remplies).
- $Q_{k,1}$ : Charge variable dominante (exploitation, vent, neige — prendre la plus défavorable).
- $\psi_{0,i}$ : Facteur de simultanéité pour les autres charges variables (ex : $\psi_0 = 0.7$ pour l'exploitation, $\psi_0 = 0.6$ pour le vent).
- $1.35$ et $1.5$ : Coefficients de sécurité partiels.

### États Limites de Service (ELS)

L'ELS vérifie le confort d'utilisation, l'esthétique et la durabilité : déformations, vibrations, fissuration.

**Combinaison caractéristique (ELS) :**

$$S_d = G + Q_{k,1} + \sum_{i>1} \psi_{0,i} \cdot Q_{k,i}$$

**Flèche maximale admissible :**

| Type de structure | Flèche limite sous $Q$ | Flèche limite totale |
|:-----------------|:----------------------|:-------------------|
| Poutre de toiture (charpente) | $L/200$ | — |
| Poutre de plancher industriel | $L/300$ | $L/250$ |
| Poutre de pont roulant chemin de roulement | $L/600$ | — |
| Passerelle piétonne | $L/400$ | $L/300$ |
| Rack de tuyauterie | $L/300$ | $L/250$ |

---

## Dimensionnement des structures métalliques (Eurocode 3)

### Vérification d'une poutre fléchie

Pour une poutre simplement appuyée de portée $L$ soumise à une charge linéique $q$ :

**Moment fléchissant maximal :** $M_{Ed} = \frac{q \cdot L^2}{8}$

**Effort tranchant maximal :** $V_{Ed} = \frac{q \cdot L}{2}$

**Vérification ELU :** $M_{Ed} \le M_{c,Rd} = \frac{W_{pl} \cdot f_y}{\gamma_{M0}}$

Où :
- $M_{c,Rd}$ : Moment résistant de la section.
- $W_{pl}$ : Module de flexion plastique de la section ($\mathrm{cm^3}$).
- $f_y$ : Limite d'élasticité de l'acier ($\mathrm{MPa}$).
- $\gamma_{M0}$ : Coefficient partiel de sécurité ($1.0$ pour l'acier selon EC 3).

### Vérification au déversement (instabilité latérale)

Pour les poutres non maintenues latéralement sur leur longueur compressée, vérifier :

$$M_{Ed} \le M_{b,Rd} = \chi_{LT} \cdot W_y \cdot \frac{f_y}{\gamma_{M1}}$$

Où $\chi_{LT}$ est le coefficient de réduction pour déversement, fonction de l'élancement $\bar{\lambda}_{LT}$ et de la courbe de flambement (courbe a, b, c, d selon le type de section).

### Vérification d'un poteau comprimé (flambement)

$$N_{Ed} \le N_{b,Rd} = \chi \cdot A \cdot \frac{f_y}{\gamma_{M1}}$$

Où $\chi$ est le coefficient de réduction pour flambement, fonction de l'élancement réduit $\bar{\lambda}$ et de la courbe de flambement :

$$\bar{\lambda} = \sqrt{\frac{A \cdot f_y}{N_{cr}}}$$

avec $N_{cr} = \frac{\pi^2 \cdot E \cdot I}{L_{cr}^2}$ (charge critique d'Euler).

**Longueur de flambement $L_{cr}$ selon les conditions aux extrémités :**

| Condition d'appui | $L_{cr}$ |
|:-----------------|:---------|
| Articulé-articulé | $1.0 \cdot L$ |
| Encastré-articulé | $0.7 \cdot L$ |
| Encastré-encastré | $0.5 \cdot L$ |
| Encastré-libre | $2.0 \cdot L$ |

---

## Fondations de machines vibrantes

Les machines lourdes générant des vibrations (compresseurs alternatifs, concasseurs, ventilateurs, moteurs, pompes haute puissance) nécessitent des fondations dimensionnées spécifiquement pour contrôler les vibrations transmises au sol et aux structures adjacentes.

### Règles de dimensionnement

1. **Rapport de masse** : La masse du massif de fondation en béton doit être au moins **3 à 5 fois** la masse de la machine tournante pour amortir suffisamment l'énergie vibratoire. Pour les machines alternatives, ce rapport monte à 5-10 fois.

2. **Fréquence propre** : Éviter la résonance en s'assurant que la fréquence propre verticale du système massif-sol $f_n$ est très différente de la fréquence d'excitation $f_{exc}$ de la machine :
   $$f_n = \frac{1}{2\pi} \sqrt{\frac{k_S}{m}} \qquad \text{avec } \frac{|f_{exc} - f_n|}{f_n} > 30\%$$

   où $k_S$ est le coefficient de raideur du sol (module de réaction) et $m$ la masse totale du massif + machine.

3. **Épaisseur minimale** : La dalle du massif doit avoir une épaisseur $\ge 500\,\mathrm{mm}$ pour les machines de puissance moyenne, $\ge 800\,\mathrm{mm}$ pour les machines lourdes.

4. **Isolation vibratoire** : Placer des joints résilients ou des plots antivibratiles (silentblocs) entre la machine et le massif pour réduire la transmission des vibrations. Les isolateurs sont dimensionnés avec un rapport de transmission $TR < 0.1$ pour $f_{exc} > 2 \cdot f_n$.

5. **Désolidarisation** : La dalle de fondation de la machine doit être **totalement désolidarisée** de la dalle générale du bâtiment par un joint de dilatation périphérique ($20$ à $50\,\mathrm{mm}$) rempli d'un matériau compressible (liège, mousse polyuréthane), pour éviter la transmission des vibrations à la structure environnante.

### Vérification d'un assemblage boulonné structurel

Un assemblage boulonné en acier (ex : attache poutre-poteau par platine) doit vérifier simultanément :

- **Résistance au cisaillement des boulons** : $F_{v,Rd} = \frac{\alpha_v \cdot f_{ub} \cdot A_s}{\gamma_{M2}}$ (par boulon).
- **Résistance au matage de la plaque** : $F_{b,Rd} = \frac{k_1 \cdot \alpha_b \cdot f_u \cdot d \cdot t}{\gamma_{M2}}$.
- **Résistance en traction des boulons** : $F_{t,Rd} = \frac{0.9 \cdot f_{ub} \cdot A_s}{\gamma_{M2}}$.

Où $f_{ub}$ est la résistance en traction du boulon, $A_s$ la section résistante, $d$ le diamètre, $t$ l'épaisseur de la plaque, $\gamma_{M2}$ le coefficient partiel ($1.25$ pour les boulons).

---

## Pièges Courants (Common Pitfalls)

### 1. Oublier le flambement sur les poteaux élancés

**Erreur :** Dimensionner un poteau vertical en acier en ne considérant que la contrainte normale ($\sigma = Force / Section$). Sous une charge axiale importante, un poteau élancé fléchira latéralement brutalement et s'effondrera bien avant d'atteindre sa limite élastique en compression pure (phénomène de flambement d'Euler).

**Exemple :** Un poteau HEA 200 en S355 ($A = 53.8\,\mathrm{cm^2}$, $f_y = 355\,\mathrm{MPa}$, $I_y = 3690\,\mathrm{cm^4}$, $L = 6\,\mathrm{m}$, articulé-articulé).

- Compression pure : $N_{pl,Rd} = 53.8\times10^2 \times 355 / 1.0 = 1910\,\mathrm{kN}$.
- Flambement : $N_{cr} = \pi^2 \times 210000 \times 3690\times10^4 / (6000^2) = 2126\,\mathrm{kN}$.
- Élancement réduit : $\bar{\lambda} = \sqrt{1910 / 2126} = 0.95$.
- Coefficient $\chi$ (courbe b) : $\chi \approx 0.65$.
- Résistance au flambement : $N_{b,Rd} = 0.65 \times 1910 = 1240\,\mathrm{kN}$ — soit **35 % de moins** que la résistance en compression pure.

**Correction :** Appliquer systématiquement la vérification au flambement selon l'EC 3 pour tous les éléments comprimés. Utiliser les courbes de flambement appropriées (a, b, c, d) selon la section et l'axe de flambement.

### 2. Ignorer les efforts horizontaux sur les structures (contreventement)

**Erreur :** Concevoir un rack métallique de tuyauterie avec uniquement des poteaux et poutres formant des portiques simples (nœuds articulés), sans modéliser de contreventements verticaux (croix de Saint-André) ou de portiques rigides. La structure est incapable de reprendre les efforts horizontaux du vent, des séismes ou de la dilatation thermique des tuyaux, et peut se "coucher" latéralement.

**Correction :** Ajouter des contreventements structurels dans les deux directions (longitudinale et transversale) pour transférer les efforts horizontaux vers les fondations. Les contreventements peuvent être :

- **Croix de Saint-André** (palées de stabilité) : Barres tendues uniquement, simples et économiques.
- **Portiques rigides** (nœuds encastrés) : Plus coûteux mais n'obstruent pas le passage.
- **Voiles de béton** : Rigides, utilisés dans les cages d'escalier ou d'ascenseur.

### 3. Négliger la fatigue des assemblages sous charges cycliques

**Erreur :** Concevoir un chemin de roulement de pont roulant (grues de 10 t, 200 cycles/jour) avec des assemblages boulonnés ordinaires non précontraints et des soudures d'angle discontinues. Après plusieurs années de fonctionnement, les assemblages se fissurent par fatigue sous l'effet des contraintes cycliques répétées, pouvant conduire à l'effondrement du chemin de roulement.

**Correction :** Pour les structures soumises à la fatigue (ponts roulants, passerelles vibrantes, machines), réaliser une vérification en fatigue selon l'EC 3 partie 1-9. Utiliser des boulons HR (haute résistance, précontraints), des soudures à pleine pénétration avec meulage des pieds de cordon, et des détails constructifs de catégorie de détail élevée (FAT class 90+).

### 4. Mauvaise évaluation des charges de neige et de vent

**Erreur :** Appliquer une charge de neige uniforme sur une toiture industrielle à deux versants sans tenir compte de l'accumulation due au redoux (neige mouillée) ou du glissement sur les versants pentus. En France, la carte des zones de neige (A1, A2, B1, B2, C1, C2, D, E) définit des charges de base $s_k$ allant de $0.45$ à $1.75\,\mathrm{kN/m^2}$ selon l'altitude et la région.

**Correction :** Appliquer correctement l'EC 1 partie 1-3 pour la neige et 1-4 pour le vent. Considérer les coefficients de forme ($\mu_i$) pour les accumulations (noues, décrochements de toitures, barrières à neige). Pour le vent, utiliser la pression dynamique de base $q_p(z_e)$ tenant compte de la hauteur, de la catégorie de terrain et de la topographie.

---

## Liste de vérification (Checklist)

- [ ] Les combinaisons de charges à l'ELU et à l'ELS sont correctement implémentées et pondérées selon les Eurocodes (EC 0).
- [ ] La flèche maximale calculée sous charge à l'ELS respecte les critères de déformation admissible ($L/300$ pour les planchers, $L/200$ pour les toitures).
- [ ] La stabilité globale aux efforts horizontaux (vent, séismes, dilatation des tuyaux) est assurée par des contreventements dans les deux directions.
- [ ] Les poteaux comprimés sont vérifiés vis-à-vis du risque de flambement (élancement critique, courbe de flambement adaptée).
- [ ] Les poutres non maintenues latéralement sont vérifiées au déversement.
- [ ] La dalle de fondation de la machine tournante est désolidarisée de la dalle générale du bâtiment (joint de dilatation périphérique).
- [ ] Les vérifications à la fatigue (EC 3-1-9) sont effectuées pour les éléments soumis à des charges cycliques (ponts roulants, passerelles).
- [ ] Les charges climatiques (vent, neige) sont déterminées selon la carte des zones et les coefficients de forme de l'EC 1.
- [ ] Les assemblages boulonnés et soudés sont calculés avec les coefficients $\gamma_{M2}$ appropriés.
- [ ] Les notes de calcul sont structurées, datées et signées pour constituer un dossier d'exécution opposable.

