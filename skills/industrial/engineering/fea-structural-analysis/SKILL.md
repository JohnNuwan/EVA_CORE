---
name: fea-structural-analysis
description: "Réaliser des simulations structurales par éléments finis (FEA) sous ANSYS ou SolidWorks Simulation pour valider la tenue mécanique des structures, l'analyse en fatigue et les coefficients de sécurité."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [fea, mechanical, simulation, structural, stress-analysis, cad, ansys, abaqus, finite-element, fatigue, vibration]
    related_skills: [cad-bom-automation, cfd-fluid-dynamics, electrical-cabinet-3d]
---

# Calcul Mécanique et Analyse par Éléments Finis (FEA)

## Vue d'ensemble

Cette compétence encadre la mise en œuvre de simulations structurales numériques par la méthode des éléments finis (**FEA — Finite Element Analysis**), utilisée avec les principaux solveurs du marché : **ANSYS Mechanical**, **SolidWorks Simulation** (basé sur le solveur Abaqus), **Abaqus/CAE**, **NASTRAN**, ou **CalculiX** en open source. L'analyse par éléments finis permet de s'assurer qu'une pièce ou un assemblage mécanique résiste aux sollicitations physiques prévues — efforts mécaniques statiques et dynamiques, couples, pression, gravité, accélérations — sans déformation plastique excessive, sans rupture, et sans résonance dommageable.

La discipline couvre quatre grandes familles d'analyses :

- **Analyse statique linéaire** : calcul des contraintes et déformations sous charges permanentes.
- **Analyse fréquentielle (modale)** : recherche des fréquences et modes propres de vibration.
- **Analyse de fatigue** : estimation de la durée de vie sous cycles de chargement répétés.
- **Analyse non-linéaire** : plasticité, grands déplacements, contacts avec frottement.

Un résultat de simulation FEA n'a de valeur que si le modèle est correctement construit et que les hypothèses simplificatrices sont maîtrisées. Cette compétence fournit la méthodologie pour y parvenir.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Calculer les contraintes de Von Mises et les déformations sur une pièce mécanique, un châssis, une platine de montage ou un support.
- Valider le coefficient de sécurité d'une structure selon les règles de l'art ou des normes spécifiques (Eurocodes, CODAP, ASME VIII, FEM).
- Réaliser une analyse fréquentielle pour éviter la résonance avec une source d'excitation (moteur, pompe, variateur).
- Analyser la tenue à la fatigue d'un équipement soumis à des cycles d'efforts répétés (pont roulant, vérin, suspension).
- Dimensionner des pièces en matériaux composites ou en alliages métalliques sous chargement multi-axial.
- Vérifier la tenue au séisme ou aux chocs d'un équipement industriel (analyse spectrale ou transitoire).

## Étapes Méthodologiques d'une Simulation FEA

Une simulation rigoureuse suit toujours le flux méthodologique suivant :

```
                         ┌──────────────────────┐
                         │   CAO 3D native ou    │
                         │   étape d'import      │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Simplification      │
                         │   géométrique         │
                         │  (congés, chanfreins, │
                         │   petits trous)       │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Affectation du      │
                         │   matériau (E, ν, ρ,  │
                         │   Re, Rm)             │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Maillage            │
                         │  (tétraèdres,         │
                         │   hexaèdres, taille   │
                         │   locale)             │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Conditions limites   │
                         │  & chargements        │
                         │  (appuis, forces,     │
                         │   pressions, couples) │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Résolution          │
                         │  (calcul matriciel    │
                         │   [K]{u} = {F})       │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Post-traitement     │
                         │  (Von Mises,         │
                         │   déplacement,       │
                         │   coefficient         │
                         │   de sécurité)        │
                         └──────────────────────┘
```

### Paramètres critiques

**Contrainte de Von Mises ($\sigma_{VM}$)** : Contrainte équivalente combinant les six composantes du tenseur des contraintes selon le critère de plasticité de Von Mises (distorsion) :

$$\sigma_{VM} = \sqrt{\frac{(\sigma_{xx} - \sigma_{yy})^2 + (\sigma_{yy} - \sigma_{zz})^2 + (\sigma_{zz} - \sigma_{xx})^2 + 6 \cdot (\tau_{xy}^2 + \tau_{yz}^2 + \tau_{zx}^2)}{2}}$$

**Coefficient de sécurité ($s$)** basé sur la limite élastique $R_e$ :

$$s = \frac{R_e}{\sigma_{VM}}$$

Valeurs de référence pour l'industrie :

| Application | $s$ minimal recommandé | Norme de référence |
|:---|:---:|:---:|
| Structures générales (acier) | $1.5$ | Eurocode 3 |
| Équipements sous pression | $1.5 - 2.0$ | ASME VIII / CODAP |
| Levage et manutention | $2.0 - 3.0$ | FEM 1.001 |
| Structures soumises à la fatigue | $2.0 - 4.0$ | FKM Guideline |

## Analyse Fréquentielle (Modale)

L'analyse modale résout le problème aux valeurs propres $( [K] - \omega_i^2 [M] ) \cdot \{\phi_i\} = 0$ pour extraire les fréquences propres $f_i = \omega_i / 2\pi$ et les modes de vibration $\{\phi_i\}$ de la structure.

**Règle de non-résonance** : La fréquence d'excitation $f_{exc}$ (ex : vitesse de rotation d'un moteur à 1500 tr/min $\rightarrow$ 25 Hz) doit être éloignée d'au moins $20\%$ des fréquences propres de la structure :

$$\frac{|f_{exc} - f_i|}{f_i} \ge 0.20$$

Si une fréquence propre se trouve dans la plage de fonctionnement, deux solutions : raidir la structure (augmenter $f_i$) ou ajouter de la masse (diminuer $f_i$), voire ajouter des amortisseurs dynamiques.

## Analyse de Fatigue

L'analyse en fatigue est indispensable pour les pièces soumises à des chargements cycliques. La démarche générale suit la **méthode des contraintes nominales** :

1. Déterminer le spectre de chargement (amplitude $\sigma_a$, contrainte moyenne $\sigma_m$).
2. Corriger par les facteurs d'influence : $k_f$ (concentration de contrainte en fatigue), $k_s$ (taille), $k_{surf}$ (état de surface), $k_{rel}$ (fiabilité).
3. Appliquer la règle de cumul de dommage de **Palmgren-Miner** :

$$D = \sum_{i=1}^{n} \frac{N_i}{N_{f,i}} \le 1$$

Où $N_i$ est le nombre de cycles appliqués au niveau $i$ et $N_{f,i}$ le nombre de cycles à rupture à ce même niveau (lu sur la courbe $S-N$ du matériau).

## Types d'Éléments et Maillage

| Type d'élément | Forme | Usage recommandé |
|:---|:---:|:---|
| Tétraèdre linéaire (C3D4) | 4 nœuds | Discrétisation automatique, pièces complexes ; peu précis, utilisé pour les pré-études |
| Tétraèdre quadratique (C3D10) | 10 nœuds | Standard pour pièces moulées, forge, géométries complexes |
| Hexaèdre linéaire (C3D8) | 8 nœuds | Très précis, maillage structuré ; difficile à générer automatiquement |
| Coque linéaire (S4R) | 4 nœuds | Structures minces (tôles, carrosseries, réservoirs) où l'épaisseur $\ll$ les autres dimensions |
| Poutre (B31) | 2 nœuds | Ossatures, châssis, structures filaires |

## Pièges Courants (Common Pitfalls)

1. **Singularités de contrainte (Stress Concentrations artificiels) :**
   - *Erreur :* Appliquer une force ponctuelle sur un seul nœud, modéliser un angle vif parfait sans congé de raccordement, ou bloquer un nœud ponctuel isolé. Le solveur calcule une contrainte asymptotique qui tend vers l'infini à mesure que le maillage est affiné, ce qui empêche toute convergence de la contrainte maximale.
   - *Correction :* Modéliser des congés de raccordement réalistes sur la CAO (rayon $R \ge 1\;mm$). Répartir les forces ponctuelles sur des surfaces d'application réalistes (rondelles, platine) en utilisant une pression équivalente. Utiliser des liaisons « remote force » avec distribution surfacique plutôt que des forces nodales.

2. **Conditions aux limites hyperstatiques ou irréalistes :**
   - *Erreur :* Bloquer complètement tous les six degrés de liberté d'une face de la pièce alors que dans la réalité elle est boulonnée sur un châssis flexible. Cela surestime la rigidité de plusieurs ordres de grandeur et sous-estime les contraintes réelles.
   - *Correction :* Modéliser la flexibilité de la structure support (même partiellement), utiliser des ressorts équivalents de rigidité $k_{boulon}$, ou appliquer des conditions de type « compression only support » pour les appuis unilatéraux.

3. **Absence d'étude de convergence de maillage :**
   - *Erreur :* Accepter le premier résultat sans avoir vérifié que la contrainte maximale (hors singularités) est indépendante de la taille de maille. Un maillage trop grossier sous-estime systématiquement les contraintes réelles.
   - *Correction :* Mener une étude avec au moins trois tailles de maille différentes ($h$, $h/2$, $h/4$). Si la contrainte d'intérêt varie de plus de $5\%$ entre $h/2$ et $h/4$, poursuivre l'affinement. Utiliser un estimateur d'erreur a posteriori (type Zienkiewicz-Zhu) si disponible.

4. **Mauvais type d'élément pour le problème traité :**
   - *Erreur :* Discrétiser une tôle mince avec des éléments volumiques (briques/tétraèdres) en ne mettant qu'un seul élément dans l'épaisseur. Le comportement en flexion sera complètement erroné (verrouillage en cisaillement, raideur excessive).
   - *Correction :* Utiliser des éléments **coque** dès que le rapport épaisseur sur longueur caractéristique $t/L < 0.1$. Un élément coque à 4 nœuds (type S4R) avec 5 points d'intégration dans l'épaisseur donne des résultats fiables en flexion.

5. **Négliger la non-linéarité de contact :**
   - *Erreur :* Utiliser une liaison rigide (bonded) entre deux pièces qui sont en réalité simplement posées l'une sur l'autre. Les contraintes sont mal réparties et le comportement global est inexact.
   - *Correction :* Utiliser des contacts avec frottement (coefficient $\mu = 0.1$ à $0.3$ selon les matériaux) et vérifier que la pénétration entre les surfaces est négligeable (inférieure à $1\%$ de la taille de maille locale).

## Liste de vérification (Checklist)

- [ ] Le matériau appliqué possède ses propriétés élastiques à jour (Module de Young $E$, Coefficient de Poisson $\nu$, Masse volumique $\rho$, Limite élastique $R_e$, Résistance à la rupture $R_m$).
- [ ] Une étude de convergence de maillage a été menée sur au moins trois niveaux d'affinement ($h$, $h/2$, $h/4$), avec une variation de la contrainte maximale inférieure à $5\%$.
- [ ] Les singularités de contrainte (forces ponctuelles, angles vifs) ont été identifiées et écartées de l'analyse.
- [ ] Les conditions aux limites reflètent fidèlement les appuis physiques réels de la structure (flexibilité, jeux, précharge).
- [ ] Le coefficient de sécurité calculé est supérieur à la limite de conception recommandée pour l'application (cf. tableau).
- [ ] L'analyse modale a vérifié que les fréquences propres sont éloignées des fréquences d'excitation de plus de $20\%$.
- [ ] Pour les pièces en fatigue, un cumul de dommage de Palmgren-Miner a été effectué avec $D \le 1$.
- [ ] Le type d'élément utilisé (volumique, coque, poutre) est adapté au rapport d'épaisseur de la pièce.
- [ ] Les contacts entre pièces sont définis avec le type correct (bondé, glissement, frottement) et sans pénétration excessive.
- [ ] Les résultats sont exprimés avec les unités cohérentes du système SI (MPa pour les contraintes, mm ou m pour les déplacements).

