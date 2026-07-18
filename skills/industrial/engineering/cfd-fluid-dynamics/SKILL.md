---
name: cfd-fluid-dynamics
description: "Modéliser les écoulements de fluides et les transferts thermiques (CFD) sous ANSYS Fluent ou SolidWorks Flow Simulation, calculer les pertes de charge et dimensionner les pompes et échangeurs."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [cfd, fluid-dynamics, thermal, hydraulics, piping, pump-sizing, simulation, fluent, comsol, openfoam]
    related_skills: [fea-structural-analysis, pid-instrumentation, pid-tuning-control]
---

# Dynamique des Fluides (CFD) et Thermique

## Vue d'ensemble

Cette compétence encadre la modélisation complète des écoulements de fluides — liquides, gaz, fluides non-newtoniens — ainsi que les phénomènes de transfert thermique (conduction, convection forcée et naturelle, rayonnement) dans un contexte d'ingénierie industrielle. Elle couvre à la fois la simulation numérique des fluides (**CFD — Computational Fluid Dynamics**) via des solveurs volumiques comme **ANSYS Fluent**, **SolidWorks Flow Simulation**, **OpenFOAM** ou **COMSOL Multiphysics**, et les calculs analytiques de pertes de charge régulières et singulières pour dimensionner les organes de convoyage : pompes centrifuges et volumétriques, ventilateurs hélicoïdes et centrifuges, échangeurs de chaleur tubulaires et à plaques.

L'ingénieur hydraulicien ou thermicien doit maîtriser trois volets indissociables : la mécanique des fluides fondamentale (équations de Navier-Stokes, couche limite, nombres adimensionnels), les corrélations industrielles validées (Darcy-Weisbach, Colebrook, Churchill) et les bonnes pratiques de simulation CFD (maillage, modèles de turbulence, convergence). Cette compétence fournit les bases méthodologiques pour chacun de ces volets.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Calculer la perte de charge linéaire et singulière dans un réseau de tuyauterie complexe (coude, té, vanne, rétrécissement) pour sélectionner une pompe ou un ventilateur.
- Simuler l'écoulement d'un fluide autour ou à l'intérieur d'un équipement (vitesse, pression, lignes de courant, zones de recirculation, cisaillement pariétal).
- Modéliser les transferts de chaleur couplés fluide-structure : refroidissement d'une armoire électrique, efficacité d'un échangeur tubulaire ou à plaques, dissipation thermique d'un radiateur électronique.
- Évaluer le régime d'un écoulement (nombre de Reynolds, nombre de Prandtl) pour orienter le choix du modèle de turbulence.
- Dimensionner une pompe centrifuge : hauteur manométrique totale (HMT), point de fonctionnement, NPSH disponible, courbe de pompe.
- Vérifier la conformité d'un dimensionnement hydraulique existant (débit, vitesse, pertes, marge de cavitation).

## Nombres Adimensionnels Fondamentaux

L'analyse dimensionnelle est la clé de voûte de tout problème de mécanique des fluides. Les trois nombres ci-dessous permettent de caractériser le régime d'écoulement et les échanges thermiques sans recourir systématiquement à la simulation.

### 1. Nombre de Reynolds (Re)

Détermine le régime de l'écoulement dans une conduite de diamètre hydraulique $D_h$ :

$$Re = \frac{\rho \cdot v \cdot D_h}{\mu}$$

Avec :

- $\rho$ : Masse volumique du fluide ($kg/m^3$)
- $v$ : Vitesse moyenne débitante ($m/s$)
- $D_h$ : Diamètre hydraulique ($m$) ; pour une conduite circulaire $D_h = D$, pour une section rectangulaire $D_h = \frac{4 \cdot A}{P_{mouillé}}$
- $\mu$ : Viscosité dynamique ($Pa \cdot s$)

| Plage de Re | Régime | Caractéristiques |
|:---|:---|:---|
| $Re < 2300$ | Laminaire | Filets parallèles, profil parabolique, pertes linéaires en $v$ |
| $2300 \le Re \le 4000$ | Transitionnel | Instable, difficile à modéliser, éviter le dimensionnement dans cette zone |
| $Re > 4000$ | Turbulent | Mélange transverse, profil aplati, pertes en $v^2$ |

### 2. Nombre de Prandtl (Pr)

Relie la diffusion de quantité de mouvement à la diffusion thermique :

$$Pr = \frac{\mu \cdot c_p}{\lambda}$$

Avec $c_p$ la capacité thermique massique ($J/kg \cdot K$) et $\lambda$ la conductivité thermique ($W/m \cdot K$).

- $Pr \ll 1$ (métaux liquides) : la couche limite thermique est beaucoup plus épaisse que la couche limite dynamique.
- $Pr \approx 1$ (gaz) : les deux couches limites ont des épaisseurs comparables.
- $Pr \gg 1$ (huiles) : la couche limite dynamique domine.

### 3. Nombre de Nusselt (Nu)

Caractérise l'intensité des échanges convectifs à la paroi :

$$Nu = \frac{h \cdot L_c}{\lambda}$$

Où $h$ est le coefficient d'échange convectif ($W/m^2 \cdot K$) et $L_c$ une longueur caractéristique ($m$). Des corrélations empiriques relient $Nu$ à $Re$ et $Pr$ selon la géométrie (ex : corrélation de Dittus-Boelter pour un écoulement turbulent interne).

## Pertes de Charge en Réseau Hydraulique

### Pertes de charge régulières (Darcy-Weisbach)

$$\Delta P_{reg} = \lambda \cdot \frac{L}{D_h} \cdot \frac{\rho \cdot v^2}{2}$$

Le coefficient de frottement $\lambda$ s'obtient :

- **Régime laminaire** ($Re < 2300$) : $\lambda = \frac{64}{Re}$ (formule de Poiseuille).
- **Régime turbulent** ($Re > 4000$) : équation de **Colebrook-White** (résolution implicite) :

$$\frac{1}{\sqrt{\lambda}} = -2 \cdot \log_{10}\left( \frac{\epsilon}{3.7 \cdot D_h} + \frac{2.51}{Re \cdot \sqrt{\lambda}} \right)$$

Où $\epsilon$ est la rugosité absolue de la paroi interne ($m$). Valeurs typiques : acier étiré $\epsilon \approx 0.05\;mm$, acier soudé $\epsilon \approx 0.15\;mm$, PVC/PEHD $\epsilon \approx 0.01\;mm$.

Pour éviter la résolution itérative, on peut utiliser l'approximation explicite de **Swamee-Jain** (valable pour $10^{-6} \le \epsilon/D \le 10^{-2}$ et $5000 \le Re \le 10^8$) :

$$\lambda = \frac{0.25}{\left[ \log_{10}\left( \frac{\epsilon}{3.7 \cdot D_h} + \frac{5.74}{Re^{0.9}} \right) \right]^2}$$

### Pertes de charge singulières

$$\Delta P_{sing} = K_s \cdot \frac{\rho \cdot v^2}{2}$$

Le coefficient $K_s$ dépend du type de singularité :

| Singularité | $K_s$ (approximatif) |
|:---|:---:|
| Coude 90° standard | $0.5 - 1.5$ |
| Coude 45° | $0.2 - 0.5$ |
| Té (passage direct) | $0.2 - 0.6$ |
| Té (dérivation) | $1.0 - 2.0$ |
| Vanne à opercule (pleine ouverture) | $0.1 - 0.2$ |
| Vanne à papillon (pleine ouverture) | $0.3 - 1.0$ |
| Rétrécissement brusque ($A_{petite}/A_{grande}=0.5$) | $0.3$ |
| Élargissement brusque ($A_{petite}/A_{grande}=0.5$) | $0.5$ |

## Dimensionnement des Pompes Centrifuges

### Hauteur Manométrique Totale (HMT)

$$HMT = (z_{ref} - z_{asp}) + \frac{\Delta P_{total}}{\rho \cdot g} + \frac{P_{ref} - P_{asp}}{\rho \cdot g}$$

Où $\Delta P_{total} = \Delta P_{reg,asp} + \Delta P_{sing,asp} + \Delta P_{reg,ref} + \Delta P_{sing,ref}$.

### NPSH (Net Positive Suction Head)

Le **NPSH disponible** ($NPSH_a$) est la charge nette à l'aspiration au-dessus de la pression de vapeur saturante :

$$NPSH_a = \frac{P_{asp}}{\rho \cdot g} + \frac{v_{asp}^2}{2g} - \frac{P_{vap}(T_{max})}{\rho \cdot g}$$

Condition impérative : $NPSH_a \ge NPSH_r + 0.5\;m$ où $NPSH_r$ est fourni par le constructeur de la pompe. Si la condition n'est pas respectée, le fluide se vaporise localement dans la turbine : c'est le phénomène de **cavitation**, destructeur pour les aubages.

### Point de fonctionnement

Le point de fonctionnement d'une pompe est l'intersection de sa courbe caractéristique $H(Q)$ (fournie par le constructeur) avec la courbe de réseau $H_{res}(Q) = HMT + K_{res} \cdot Q^2$. La résistance du réseau $K_{res}$ se calcule à partir des pertes de charge totales à débit nominal.

## Bonnes Pratiques de Maillage en CFD

La qualité du maillage détermine la précision et la stabilité de toute simulation CFD.

### Couche limite (Inflation)

Pour capturer correctement les gradients de vitesse et de température à la paroi, la première maille doit satisfaire $y^+ \approx 1$ pour un modèle de turbulence résolvant la couche limite (type $k-\omega$ SST). La hauteur de la première maille $\Delta y$ se calcule par :

$$\Delta y = \frac{y^+ \cdot \mu}{\rho \cdot u_\tau}$$

Où $u_\tau = \sqrt{\frac{\tau_{paroi}}{\rho}}$ est la vitesse de frottement.

### Qualité des éléments

| Critère | Valeur acceptable | Valeur idéale |
|:---|:---:|:---:|
| Aspect Ratio | $< 100$ | $< 10$ |
| Skewness | $< 0.9$ | $< 0.5$ |
| Orthogonal Quality | $> 0.1$ | $> 0.7$ |

## Modèles de Turbulence

| Modèle | Usage recommandé | Limites |
|:---|:---|:---|
| $k-\epsilon$ standard | Écoulements turbulents en cœur, géométries simples | Performance médiocre près des parois et en écoulements tourbillonnaires |
| $k-\omega$ SST | Écoulements avec décollement, profils aérodynamiques, échangeurs | Plus coûteux en temps de calcul |
| RSM (Reynolds Stress Model) | Écoulements fortement anisotropes (cyclones, swirl) | Très coûteux, convergence difficile |
| LES (Large Eddy Simulation) | Écoulements institutionnaires, acoustique, combustion | Temps de calcul prohibitif pour les géométries industrielles |

## Pièges Courants (Common Pitfalls)

1. **Mauvais choix de modèle de turbulence en CFD :**
   - *Erreur :* Utiliser le modèle laminaire pour simuler un écoulement à haute vitesse dans un tuyau ou un échangeur, ce qui conduit à des calculs de pertes de charge et de transfert thermique complètement faux.
   - *Correction :* Calculer le nombre de Reynolds en entrée de domaine. Si $Re > 4000$, activer un modèle de turbulence adapté. Pour la majorité des applications industrielles, le modèle **$k-\omega$ SST** offre le meilleur compromi précision-temps de calcul. Le modèle standard **$k-\epsilon$** est acceptable pour les écoulements cœurs.

2. **Maillage insuffisant dans la couche limite :**
   - *Erreur :* Utiliser un maillage grossier sans couche limite (prismes/inflation) près des parois. Les gradients de vitesse et de température ne sont pas résolus, ce qui fausse le coefficient de frottement et le nombre de Nusselt.
   - *Correction :* Générer au moins 10 à 15 couches de prismes avec un ratio de croissance de 1.2 et une première maille vérifiant $y^+ \le 1$ pour les modèles bas-Reynolds.

3. **NPSH insuffisant à l'aspiration des pompes (Cavitation) :**
   - *Erreur :* Placer la pompe trop haut au-dessus du réservoir ou sous-dimensionner la ligne d'aspiration, provoquant l'apparition de bulles de vapeur qui détruisent la turbine.
   - *Correction :* S'assurer que le **NPSH disponible** calculé est supérieur au **NPSH requis** par le fabricant de la pompe avec une marge de sécurité d'au moins $0.5\;m$. En cas de fluide à température élevée, la pression de vapeur $P_{vap}(T_{max})$ doit être évaluée avec précision.

4. **Non-respect des critères de convergence :**
   - *Erreur :* Arrêter la simulation dès que les résidus atteignent $10^{-3}$ sans vérifier les bilans de masse et d'énergie.
   - *Correction :* En plus du suivi des résidus RMS, vérifier que le déséquilibre de bilan de masse global est inférieur à $1\%$ et que les grandeurs d'intérêt (pression, température, débit) sont stabilisées depuis au moins 100 itérations.

5. **Conditions aux limites incohérentes en entrée/sortie :**
   - *Erreur :* Imposer une condition de sortie « Outflow » pour un écoulement compressible ou avec contre-pression connue.
   - *Correction :* Utiliser une condition **Pressure Outlet** avec la pression statique réelle (ou atmosphérique) en sortie, et une condition **Mass Flow Inlet** ou **Velocity Inlet** avec le profil de vitesse pleinement développé en entrée.

## Liste de vérification (Checklist)

- [ ] Le nombre de Reynolds a été vérifié pour valider le modèle d'écoulement (laminaire vs turbulent) et le choix du modèle de turbulence.
- [ ] Le maillage de couche limite (Inflation en CFD) est suffisant : $y^+ \le 1$ pour les modèles bas-Reynolds, au moins 10 couches de prismes.
- [ ] La qualité du maillage a été vérifiée (Skewness $< 0.9$, Orthogonal Quality $> 0.1$).
- [ ] La marge de cavitation ($NPSH_a > NPSH_r + 0.5\;m$) a été calculée et vérifiée à la température maximale du fluide.
- [ ] Les bilans de masse et d'énergie entrée/sortie sont équilibrés (déséquilibre $< 1\%$).
- [ ] Les grandeurs d'intérêt sont stabilisées sur au moins 100 itérations avant de déclarer la convergence.
- [ ] Les conditions aux limites d'entrée et de sortie sont cohérentes avec la physique de l'écoulement (type de condition, profil de vitesse).
- [ ] La rugosité des parois ($\epsilon$) a été renseignée pour les conduites métalliques, plastiques ou en béton.
- [ ] Pour les simulations thermiques, le nombre de Prandtl et la corrélation de Nusselt adaptée à la géométrie ont été identifiés.
- [ ] Les unités du solveur (SI, mm, etc.) sont cohérentes avec les données d'entrée.

