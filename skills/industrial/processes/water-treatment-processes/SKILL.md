---
name: water-treatment-processes
description: "Concevoir, dimensionner et piloter des procédés de traitement d'eau industrielle (filtration, osmose inverse, déminéralisation, adoucissement, désinfection UV) et gérer les stations d'épuration (STEP) pour effluents industriels."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [water-treatment, step, osmosis, filtration, effluents, chemical-processes, demineralization, softening, reverse-osmosis, water-quality, coagulation, floculation]
  helios:
    related_skills: [pid-instrumentation, process-chemical-water, industrial-maintenance-preventive]
    difficulty: intermediate
    industry_sectors: [chemical, pharmaceutical, food-beverage, energy, paper, metallurgy, semiconductor]
---

# Traitement de l'Eau Industrielle & Procédés Environnementaux

## Vue d'ensemble

Cette compétence guide la conception, le dimensionnement et le pilotage opérationnel des procédés de traitement de l'eau en milieu industriel. L'eau est utilisée à la fois comme matière première (eau purifiée pharmaceutique, eau pour chaudière haute pression), comme fluide de procédé (boucles de refroidissement, tours aéroréfrigérantes TAR) et génère des rejets pollués qui doivent être traités avant rejet dans le milieu naturel ou le réseau d'assainissement.

La gestion de l'eau en industrie s'articule autour de trois grands axes :

1. **Traitement de l'eau de process** : Produire une eau de qualité adaptée à l'usage industriel (adoucie, déminéralisée, osmosée, ultrapure) à partir d'eau de ville ou d'eau de forage.
2. **Traitement des effluents** : Dépolluer les rejets industriels via des stations d'épuration (STEP) avant rejet conforme aux valeurs limites d'émission (VLE).
3. **Gestion des circuits de refroidissement** : Prévenir l'entartrage, la corrosion et les développements biologiques dans les tours aéroréfrigérantes et les échangeurs thermiques.

### Contexte Industriel et Réglementaire

Les contraintes réglementaires sont de plus en plus strictes en matière de rejets industriels (directive européenne IED 2010/75/UE, arrêté ministériel français du 2 février 1998, règlement REACH). La maîtrise des consommations d'eau et la qualité des rejets sont devenues des enjeux stratégiques pour les industriels. Les principales filières concernées sont :

| Secteur | Utilisation principale | Contrainte réglementaire clé |
|:---|---|:---:|
| Chimie / Pétrochimie | Eau de refroidissement, eau de procédé | REACH, IED, rejets de COV/métaux lourds |
| Pharmacie | Eau Purifiée (PW), Eau pour Préparation Injectable (WFI) | Pharmacopée (USP, EP) |
| Agroalimentaire | Lavage, rinçage, eau ingrédient | Règlement CE 852/2004, HACCP |
| Papeterie | Eau de process, recyclage | Directive IPPC |
| Électronique / Semi-conducteurs | Eau ultrapure (UPW) | Normes ASTM D5127 |

## Technologies de Purification de l'Eau

### 1. Adoucissement par Échange d'Ions

L'adoucissement consiste à remplacer les ions calcium ($Ca^{2+}$) et magnésium ($Mg^{2+}$) responsables de la dureté de l'eau (tartre) par des ions sodium ($Na^+$) à l'aide d'une résine échangeuse de cations.

**Indicateur** : Titre Hydrotimétrique (TH) exprimé en degrés français (°f). Une eau adoucie vise un $TH \approx 0^\circ\text{f}$.
**Formule de dimensionnement** : Capacité de résine nécessaire $C_{résine}$ (en $m^3$ d'eau adoucie entre deux régénérations) :
$$C_{résine} = \frac{V_{résine} \times C_{échange}}{TH_{entrée} - TH_{sortie}}$$

Où $C_{échange}$ est la capacité d'échange de la résine (généralement 1,4 à 2,0 eq/L).

| Paramètre | Valeur typique |
|:---|---|
| TH eau de ville entrante | 20 – 40 °f |
| TH eau adoucie visé | 0 – 5 °f |
| Fréquence de régénération | 1 à 3 fois par semaine |
| Consommation de sel (NaCl) par régénération | 150 – 250 g/L de résine |
| Perte de charge maximale | 1,5 bar |

### 2. Osmose Inverse (OI)

Filtration membranaire tangentielle très fine sous haute pression pour retenir 98 % à 99 % des sels dissous, des bactéries, des virus et des matières organiques.

**Paramètres de dimensionnement clés :**

| Paramètre | Symbole | Formule | Valeur typique |
|:---|:---:|:---|:---:|
| Taux de conversion | $Y$ | $Y = \frac{Q_{perméat}}{Q_{alimentation}}$ | 70 – 75 % |
| Taux de rejet salin | $R$ | $R = \left(1 - \frac{C_{perméat}}{C_{alimentation}}\right) \times 100$ | 98 – 99 % |
| Pression nette d'alimentation | $P_{net}$ | $P_{alim} - \frac{\Delta P}{2} - \pi_{moy}$ | 10 – 15 bar |
| Flux de perméat | $J$ | $J = A \times (P_{net} - \pi)$ | 15 – 30 L/h/m² |
| Indice de colmatage (SDI) | SDI | Mesure normalisée ASTM D4189 | < 3 (objectif) |

**Pré-traitement obligatoire avant OI :**
1. Adoucisseur ou injection d'antiscalant (protection contre le tartre).
2. Filtre à charbon actif ou injection de bisulfite de sodium (élimination du chlore libre qui détruit les membranes polyamide).
3. Filtration sur cartouche 5 µm (protection contre les particules en suspension).

**Nettoyage des membranes (CIP - Cleaning In Place) :**
- Nettoyage acide (pH 2-3, acide citrique ou chlorhydrique) : élimination du tartre et des oxydes métalliques.
- Nettoyage basique (pH 11-12, soude + détergent) : élimination des biofilms et des matières organiques.
- Fréquence typique : 3 à 6 mois selon la qualité de l'eau d'alimentation.

### 3. Déminéralisation Totale (DM)

Combinaison de résines cationiques fortes (élimination des cations : $Ca^{2+}, Mg^{2+}, Na^+, K^+$) et de résines anioniques fortes (élimination des anions : $Cl^-, SO_4^{2-}, HCO_3^-, NO_3^-$) pour produire une eau dont la conductivité est inférieure à 1 µS/cm.

$$R-H^+ + Na^+ + Cl^- \rightarrow R-Na^+ + H^+ + Cl^-$$
$$R-OH^- + H^+ + Cl^- \rightarrow R-Cl + H_2O$$

La régénération se fait à l'acide chlorhydrique (HCl) pour la cationique et à la soude (NaOH) pour l'anionique.

### 4. Désinfection UV

Utilisation de rayonnements ultraviolets (longueur d'onde 254 nm) pour inactiver les micro-organismes en endommageant leur ADN. Alternative sans produit chimique au chlore ou à l'ozone.

| Type de micro-organisme | Dose UV requise (mJ/cm²) |
|:---|---:|
| Bactéries (E. coli, Legionella) | 10 – 40 |
| Virus (Rotavirus, Adénovirus) | 40 – 160 |
| Protozoaires (Cryptosporidium, Giardia) | 10 – 20 |
| Moisissures (Aspergillus) | 50 – 250 |

## Traitement des Effluents Industriels (STEP)

### Filière physico-chimique

Utilisée pour les effluents contenant des polluants particulaires ou colloïdaux (industries chimiques, traitement de surface, métallurgie) :

1. **Dégrillage / Tamisage** : Élimination des grosses particules (> 1 mm).
2. **Déshuilage / Déssablage** : Séparation gravitaire des huiles libres et des sables.
3. **Homogénéisation** : Bassin tampon pour lisser les variations de débit et de charge polluante.
4. **Coagulation** : Neutralisation des charges négatives des colloïdes par injection d'un coagulant métallique (chlorure ferrique $FeCl_3$, sulfate d'alumine $Al_2(SO_4)_3$).
   - pH optimal de coagulation : 5,5 – 6,5 pour le fer, 6,0 – 7,5 pour l'aluminium.
5. **Floculation** : Agrégation des particules déstabilisées en flocs volumineux par un polymère (polyélectrolyte anionique ou cationique). Vitesse de gradient $G$ typique : 20 – 80 s⁻¹.
6. **Décantation** : Séparation gravitaire des flocs dans un décanteur lamellaire ou circulaire. Charge surfacique typique : 1 – 3 m³/m²/h.
7. **Neutralisation du pH** : Ajustement final du pH entre 5,5 et 8,5 avant rejet.

### Filière biologique

Utilisée pour les effluents à forte charge organique (agroalimentaire, papeterie, chimie fine) :

| Paramètre | Boues activées | MBR (Bioréacteur à membranes) | Lit bactérien |
|:---|---|:---:|:---:|
| Charge massique (kg DBO5/kg MV/j) | 0,1 – 0,4 | 0,05 – 0,2 | 0,2 – 0,6 |
| Concentration en boues (g/L) | 3 – 5 | 8 – 15 | – |
| Rendement DBO5 | 90 – 95 % | 95 – 99 % | 80 – 90 % |
| Emprise au sol | Importante | Faible | Moyenne |
| Production de boues | Élevée | Très élevée | Faible |

### Indicateurs de qualité d'eau

| Paramètre | Abréviation | Unité | Valeur limite de rejet typique |
|:---|:---:|:---:|:---:|
| Demande Chimique en Oxygène | DCO | mg O₂/L | < 125 |
| Demande Biochimique en Oxygène (5 jours) | DB05 | mg O₂/L | < 30 |
| Matières En Suspension | MES | mg/L | < 35 |
| Azote global (Kjeldahl) | NTK | mg N/L | < 15 |
| Phosphore total | Pt | mg P/L | < 2 |
| pH | – | – | 5,5 – 8,5 |
| Hydrocarbures totaux | HCT | mg/L | < 5 |
| Métaux (ex : Zinc, Cuivre) | – | mg/L | < 0,5 – 2 (selon métal) |

## Pièges Courants (Common Pitfalls)

1. **Colmatage prématuré des membranes d'osmose inverse :**
   - *Erreur :* Envoyer de l'eau brute calcaire ou contenant du chlore libre directement sur des membranes d'osmose inverse en polyamide. Les membranes seront détruites par oxydation chimique ou colmatées par précipitation de carbonate de calcium en quelques jours.
   - *Correction :* Toujours concevoir un pré-traitement adapté en amont : adoucisseur (élimination du calcaire), filtre à charbon actif ou injection de bisulfite de sodium (élimination du chlore libre) et filtration de sécurité à 5 microns. Surveiller le SDI toutes les semaines.

2. **Surdosage ou sous-dosage des produits chimiques en STEP :**
   - *Erreur :* Doser le coagulant ou le polymère de floculation à débit fixe sans tenir compte des variations de débit ou de pollution de l'effluent d'entrée, provoquant des dépassements de rejets polluants ou un gaspillage de réactifs.
   - *Correction :* Asservir les pompes doseuses proportionnellement au débit d'entrée (asservissement 4-20 mA) et piloter les consignes de pH de neutralisation en boucle fermée avec régulation PID. Installer un analyseur en ligne (turbidité, COT) pour ajuster le dosage en temps réel.

3. **Dépassement des VLE en heures de pointe de production :**
   - *Erreur :* Dimensionner la STEP sur le débit moyen sans tenir compte des pointes de production (ex : lavage des cuves en fin de poste). Le bassin tampon est sous-dimensionné et la station déborde en charge hydraulique.
   - *Correction :* Dimensionner le bassin d'homogénéisation sur un temps de séjour d'au moins 4 à 8 heures, avec une agitation lente pour éviter les dépôts.

4. **Dérive des sondes de pH et conductivité :**
   - *Erreur :* Faire confiance aux mesures de pH et de conductivité sans étalonnage régulier. Les électrodes de pH se colmatent et dérivent, entraînant un pilotage erroné de la neutralisation et des rejets non conformes.
   - *Correction :* Installer un système de nettoyage automatique des sondes (ultrasons ou jet d'eau) et programmer un étalonnage hebdomadaire. Utiliser des sondes redondantes (2 capteurs avec contrôle de cohérence).

## Références

- **Directive IED 2010/75/UE** : Émissions industrielles (prévention et réduction intégrées de la pollution).
- **NF EN 12566** : Stations d'épuration pour effluents industriels.
- **ASTM D4189** : Standard Test Method for Silt Density Index (SDI) of Water.
- **Pharmacopée Européenne (Ph. Eur.)** : Monographie sur les eaux pour usage pharmaceutique.
- **Guide technique ASTEE / INERIS** : Traitement des effluents industriels.
- **Norme NF T90-210** : Qualité de l'eau — Guide pour l'évaluation des méthodes d'analyses.

## Liste de vérification (Checklist)

- [ ] L'**indice de colmatage (SDI)** de l'eau d'alimentation de l'osmoseur est mesuré et inférieur à 3 (cible) ou 4 (maximum toléré).
- [ ] Le **pré-traitement** de l'osmose inverse protège efficacement les membranes contre le chlore libre (résiduel nul) et le calcaire (TH < 5 °f).
- [ ] Le **dimensionnement des bassins** de décantation de la STEP garantit un temps de séjour suffisant pour la séparation des flocs (charge surfacique < 3 m³/m²/h).
- [ ] Les **capteurs de pH et de conductivité** en rejet de STEP sont équipés de dispositifs de nettoyage automatique et d'un étalonnage hebdomadaire programmé.
- [ ] Les **rejets finaux** respectent les valeurs limites d'émission (VLE) réglementaires pour la DCO, DBO5, les métaux lourds et les MES (au moins 4 analyses par an par un laboratoire agréé).
- [ ] Les **produits chimiques** (coagulants, polymères, acides, bases) sont stockés dans des bacs de rétention dimensionnés selon la réglementation (100% plus grand contenant).
- [ ] Un **registre de suivi des consommations** d'eau est tenu à jour avec un compteur dédié par atelier ou procédé critique.
- [ ] Les **plans des réseaux d'eau** (eaux claires, eaux usées, eaux pluviales) sont à jour et accessibles.
- [ ] Les **pompes doseuses** sont étalonnées périodiquement et leur débit est vérifié par des mesures en ligne ou des tests de jaugeage.
- [ ] Les **fiches de données de sécurité (FDS)** des produits chimiques utilisés sont disponibles et à jour à proximité des points de stockage.

