---
name: electrical-cabinet-3d
description: "Concevoir des armoires électriques en 3D sous EPLAN Pro Panel ou SolidWorks Electrical 3D, optimiser l'implantation des composants, simuler la dissipation thermique et router le câblage."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [cabinet-design, electrical, 3d-cad, pro-panel, solidworks-electrical, thermal-analysis, wire-routing, iec-60890, perforex]
    related_skills: [electrical-schematics-eplan, cad-bom-automation, cfd-fluid-dynamics]
---

# Conception 3D d'Armoires Électriques

## Vue d'ensemble

Cette compétence encadre la conception en trois dimensions d'enveloppes et d'armoires électriques industrielles — coffrets de commande, pupitres opérateur, baies de distribution, armoires de puissance MT/BT — à l'aide des outils de CAO 3D spécialisés comme **EPLAN Pro Panel**, **SolidWorks Electrical 3D**, **Rittal Therm** ou **AutoCAD MEP**. La modélisation 3D va bien au-delà du simple dessin d'implantation : elle permet de :

- **Valider l'agencement spatial** : éviter les collisions entre composants (rails DIN, disjoncteurs, automates, borniers, alimentations, variateurs) avant la fabrication.
- **Automatiser le routage des fils** : calcul de longueurs exactes de câblage entre les composants, génération de listes de coupe (wire cut lists), optimisation des chemins dans les goulottes.
- **Préparer les données d'usinage** : export de fichiers DXF pour les machines de perçage à commande numérique (Perforex, Rittal), incluant les perçages des plaques de montage, les découpes des portes et les rainures des goulottes.
- **Effectuer les calculs thermiques** : échauffement à l'intérieur de l'armoire selon la norme **IEC/TR 60890**, dimensionnement de la ventilation naturelle, forcée ou des climatiseurs industriels.
- **Générer la documentation d'assemblage** : plans d'implantation cotés, vues 3D filaires (isométriques) pour le montage, nomenclatures de câblage.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Réaliser l'implantation 3D de composants électriques (goulottes, rails DIN, disjoncteurs, automates, borniers, variateurs, alimentations de distribution) sur une plaque de montage.
- Calculer le taux de remplissage des goulottes de câblage pour s'assurer que les conducteurs électriques s'y insèrent sans contrainte mécanique excessive et avec une circulation d'air suffisante.
- Évaluer le bilan thermique complet d'une armoire électrique et déterminer le système de refroidissement adéquat (ventilation naturelle, filtration forcée, climatiseur industriel, échangeur air/air).
- Extraire les fichiers d'usinage (DXF, NC) pour le perçage de la plaque de montage, des portes ou des panneaux latéraux.
- Générer les listes de coupe (alezoirs, guides) pour le câblage automatisé — notamment pour les machines de coupe et dénudage de fils (Komax, Schleuniger).

## Calcul Thermique Simplifié selon la Norme IEC 60890

L'objectif est de garantir que la température interne de l'armoire reste sous une limite acceptable pour les composants électroniques (généralement $40°C$ ou $45°C$ maximum pour les automates et variateurs). Au-delà, les pannes prématurées (défaillance des condensateurs électrolytiques, dérive thermique des fusibles électroniques) deviennent très probables.

### Étape 1 : Calcul de la puissance dissipée totale ($P_{disp}$)

La puissance dissipée sous forme thermique est la somme des pertes individuelles de chaque composant :

$$P_{disp} = \sum_{i=1}^{n} P_{composant,i} + P_{câbles}$$

Ordres de grandeur des dissipations thermiques typiques en armoire :

| Composant | Puissance dissipée typique |
|:---|---:|
| API (automate programmable) — CPU | $10$ à $30\;W$ |
| API — Module d'entrées/sorties (8 canaux) | $2$ à $5\;W$ |
| Variateur de vitesse (5% de $P_n$) | $0.05 \times P_n$ |
| Alimentation de distribution 24 Vdc / 10 A | $15$ à $25\;W$ |
| Contacteur 9 A (bobine maintenue) | $2$ à $4\;W$ |
| Relais thermique | $1$ à $3\;W$ |
| Disjoncteur magnéto-thermique | $1$ à $2\;W$ par pôle |
| Bloc de jonction / bornier passif | $\approx 0\;W$ |
| Câbles de puissance (chute Joule) | $I^2 \cdot R$ |
| Ventilateur d'armoire | $5$ à $15\;W$ (moteur) |
| Climatiseur industriel | $200$ à $1000\;W$ (attention : chaleur extraite + dissipation du compresseur) |

### Étape 2 : Surface d'échange effective ($A$)

La surface d'échange $A$ dépend des dimensions de l'armoire (hauteur $H$, largeur $W$, profondeur $D$) et de son mode d'installation :

| Installation | Surface d'échange $A$ ($m^2$) |
|:---|:---:|
| Armoire isolée (libre sur toutes les faces) | $A = 1.8 \cdot H \cdot (W + D) + 1.4 \cdot W \cdot D$ |
| Adossée au mur | $A = 1.4 \cdot H \cdot (W + D) + 1.4 \cdot W \cdot D$ |
| En angle (deux faces contre mur) | $A = 1.4 \cdot H \cdot W + 1.4 \cdot W \cdot D$ |
| En batterie (armoires côte à côte) | $A = 1.8 \cdot H \cdot (W + D) + 1.4 \cdot W \cdot D$ — soustraire les faces latérales adjacentes |

### Étape 3 : Augmentation de température sans ventilation

$$\Delta T = T_{interne} - T_{externe} = \frac{P_{disp}}{k \cdot A}$$

Où $k$ est le coefficient de transmission thermique de la paroi de l'enveloppe ($W/m^2 \cdot K$) :

| Matériau de l'enveloppe | $k$ ($W/m^2 \cdot K$) |
|:---|---:|
| Acier peint (standard) | $5.5$ |
| Acier inoxydable | $5.0$ |
| Polyester (armoire composite) | $4.0$ |
| Aluminium | $7.0$ |

### Étape 4 : Décision de refroidissement

| $\Delta T$ calculé ($K$) | Action recommandée |
|:---:|:---|
| $< 10$ | Ventilation naturelle suffisante (grilles d'aération) |
| $10$ à $15$ | Ventilation forcée (filtre-ventilateur en porte + grille de sortie) |
| $15$ à $25$ | Deux ventilateurs en série + grilles de sortie dimensionnées |
| $> 25$ | Climatiseur industriel ou échangeur air/air obligatoire |

**Exemple de calcul** : Armoire adossée de $2.0\;m$ (H) $\times 0.8\;m$ (W) $\times 0.4\;m$ (D) contenant un automate ($30\;W$), trois variateurs de $5.5\;kW$ ($3 \times 0.05 \times 5500 = 825\;W$) et une alimentation ($25\;W$) :

$$P_{disp} = 30 + 825 + 25 = 880\;W$$
$$A = 1.4 \times 2.0 \times (0.8 + 0.4) + 1.4 \times 0.8 \times 0.4 = 3.36 + 0.45 = 3.81\;m^2$$
$$\Delta T = \frac{880}{5.5 \times 3.81} \approx 42\;K$$

Résultat : $T_{interne} \approx 35°C + 42°C = 77°C$ → **Climatiseur industriel impératif** (température de consigne $30°C$).

## Routage de Câblage 3D

Le routage 3D automatique dans EPLAN Pro Panel ou SolidWorks Electrical 3D permet de :

- Calculer la longueur exacte de chaque fil entre sa borne de départ et sa borne d'arrivée, en suivant les goulottes définies dans le modèle.
- Générer une **liste de coupe** (wire cut list) pour les machines de câblage automatisé.
- Vérifier que le rayon de courbure minimal des câbles est respecté (surtout pour les gros câbles de puissance).
- Détecter les chemins impossibles (goulotte trop courte, angle trop serré, composant obstruant le passage).

### Rayons de courbure minimaux

| Type de câble | Rayon de courbure minimal (multiples du diamètre extérieur $D_{ext}$) |
|:---|---:|
| Câble de commande (H05VK, 1.5 mm²) | $4 \times D_{ext}$ |
| Câble de puissance (H07RN-F, 4-16 mm²) | $6 \times D_{ext}$ |
| Câble blindé instrument (type LIYCY) | $8 \times D_{ext}$ |
| Câble fibre optique | $10 \times D_{ext}$ (sans traction) |

### Taux de remplissage des goulottes

$$Remplissage(\%) = \frac{\sum_{i=1}^{n} A_{câble,i}}{A_{goulotte}} \times 100$$

Où $A_{câble,i} = \frac{\pi \cdot D_{ext,i}^2}{4}$ (section totale du câble en incluant l'isolant).

| Type de câbles | Taux de remplissage maximal recommandé |
|:---|---:|
| Câbles de commande | $70\%$ |
| Câbles de puissance | $50\%$ |
| Câbles mélangés (commande + puissance) | $50\%$ |
| Goulottes avec angle à $90°$ | $40\%$ (ajouter une marge pour les contraintes de courbure) |

## Pièges Courants (Common Pitfalls)

1. **Sous-estimation des rayons de courbure des gros câbles de puissance :**
   - *Erreur :* Placer un variateur de $30\;kW$ trop près de la goulotte inférieure de la plaque de montage. Lors du câblage réel, les câbles d'alimentation de section $16\;mm^2$ (diamètre extérieur $D_{ext} \approx 18\;mm$) ne peuvent pas être courbés à $90°$ en descendant verticalement sans dépasser le rayon de courbure minimal ($6 \times D_{ext} = 108\;mm$). Le câble sort de la goulotte et rend le montage impossible.
   - *Correction :* Respecter les distances minimales de raccordement préconisées par le constructeur du variateur (page d'encombrement du catalogue). Utiliser un écartement minimum de $6 \times D_{ext}$ entre la sortie de la goulotte et les bornes du variateur. En 3D, ces vérifications se font automatiquement avec les règles de routage paramétrées.

2. **Goulottes de câblage saturées à plus de $100\%$ :**
   - *Erreur :* Choisir des dimensions de goulottes insuffisantes (par exemple $40 \times 40\;mm$ au lieu de $60 \times 80\;mm$) pour gagner de la place sur la plaque de montage. Au montage, les fils électriques ne rentrent pas tous dans la goulotte, ou ils sont tellement serrés que la circulation d'air est nulle, provoquant un point chaud local.
   - *Correction :* Utiliser les outils de calcul de taux de remplissage intégrés aux logiciels de CAO 3D. En conception, viser un taux de remplissage **maximal de $70\%$** pour les câbles de commande et **$50\%$** pour les câbles de puissance. Si le taux dépasse ces seuils, augmenter la section de goulotte ou ajouter une goulotte parallèle supplémentaire.

3. **Absence de zones de dégagement thermique autour des composants actifs :**
   - *Erreur :* Placer un variateur de vitesse immédiatement à côté d'un autre variateur, sans espace libre pour la circulation d'air. Les dissipateurs thermiques des variateurs chauffent mutuellement leurs entrées d'air, causant des déclenchements thermiques intempestifs en été.
   - *Correction :* Respecter les distances de dégagement thermique préconisées par chaque fabricant (généralement $100$ à $200\;mm$ au-dessus et en dessous du variateur pour l'entrée/sortie d'air). En 3D, vérifier que les flux d'air ascendants ne sont pas obstrués par des goulottes ou d'autres composants.

4. **Non-respect des séparations fonctionnelles ELV / LV :**
   - *Erreur :* Acheminer les fils $24\;Vdc$ (ELV) dans la même goulotte que les fils $230\;Vac$ ou $400\;Vac$ (LV). En cas de défaut d'isolation d'un fil de puissance, la tension secteur se retrouve sur le bus $24\;Vdc$ et détruit les cartes électroniques (automate, variateurs, alimentations).
   - *Correction :* S'assurer que la conception 3D respecte la séparation physique : goulottes distinctes pour ELV (bleues ou grises claires) et LV (rouges ou grises foncées), avec un espacement minimal de $50\;mm$ entre elles ou une cloison métallique de séparation.

5. **Fichiers d'usinage (DXF) non vérifiés avant fabrication :**
   - *Erreur :* Exporter le fichier DXF de perçage de la plaque de montage sans vérifier les collisions. La machine Perforex perce à travers un composant 3D mal positionné ou crée un trou qui interrompt une goulotte de câblage.
   - *Correction :* Après export, visualiser le fichier DXF dans un logiciel de DAO (DraftSight, QCAD). Vérifier que tous les perçages et découpes correspondent exactement aux pièces réelles. Exécuter une simulation de l'usinage si l'outil le permet (Perforex Simulate).

## Liste de vérification (Checklist)

- [ ] L'espace d'accès autour des composants de puissance (variateurs, alimentations redondantes, transformateurs) respecte les zones de dégagement thermique recommandées par le fabricant (hauteur libre au-dessus et en dessous).
- [ ] Le taux de remplissage de toutes les goulottes de câblage est inférieur aux limites recommandées ($70\%$ pour commande, $50\%$ pour puissance).
- [ ] Le bilan thermique selon la norme IEC 60890 a été calculé ($P_{disp}$, $A$, $\Delta T$) et le système de ventilation/climatisation est dimensionné en conséquence.
- [ ] Les distances minimales de raccordement et les rayons de courbure des câbles (en particulier pour la puissance) sont respectés.
- [ ] Les circuits ELV (24 Vdc) et LV (230/400 Vac) sont physiquement séparés par des goulottes différentes avec un espacement suffisant.
- [ ] Les fichiers CN/Perforex (Commande Numérique) de perçage de la plaque de montage et des portes sont exportés et exempts de collisions.
- [ ] Les listes de coupe (wire cut lists) et les longueurs de câbles calculées sont cohérentes avec le câblage réel.
- [ ] Une nomenclature 3D complète (BOM) est exportée, incluant les références de l'armoire, de la plaque, des goulottes, des rails DIN et des accessoires de fixation.
- [ ] Le poids total de l'armoire (composants + câbles + porte) est estimé pour vérifier la capacité du socle / de l'ancrage au sol.
- [ ] L'accès aux composants pour la maintenance (dépose des cartes, changement de fusibles, serrage des borniers) est vérifié en 3D (CEM).

