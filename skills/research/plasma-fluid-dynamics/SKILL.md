---
name: plasma-fluid-dynamics
description: >-
  Compétence niveau ingénieur/docteur en physique des plasmas et mécanique
  des fluides. Couvre physics.plasm-ph (Plasma Physics) et physics.flu-dyn
  (Fluid Dynamics) : fusion magnétique (Tokamak, Stellarator), fusion
  inertielle, MHD idéale et résistive, instabilités, turbulence plasma,
  Navier-Stokes, turbulence fluide, CFD (OpenFOAM, SU2), rhéologie, SPH,
  multiphysique, MHD astrophysique.
category: research
---

# Compétence en Dynamique des Plasmas et des Fluides

## Présentation

Cette compétence couvre l'ensemble des domaines de la **physique des plasmas** (catégorie arXiv `physics.plasm-ph`) et de la **mécanique des fluides** (catégorie arXiv `physics.flu-dyn`), à un niveau ingénieur/docteur. Elle intègre les aspects fondamentaux, les méthodes numériques avancées, les codes de simulation industriels et académiques, ainsi que les applications en fusion thermonucléaire, astrophysique, aérodynamique et génie des procédés.

La maîtrise conjointe de ces deux disciplines est essentielle pour la **magnétohydrodynamique (MHD)**, la **turbulence** (plasma et fluide), les **écoulements multiphasiques** et la **simulation multiphysique** qui constituent le cœur des défis scientifiques actuels dans ces domaines.

## Domaines de Recherche

### 1. Physique des Plasmas et Fusion Thermonucléaire

#### Fusion Magnétique
- **Tokamaks** : configurations magnétiques, équilibre MHD (Grad-Shafranov), stabilité, chauffage (ICH, ECH, NBI), divertor, modes H/L, ELMs, scénarios avancés (steady-state, advanced tokamak)
- **Stellarators** : Wendelstein 7-X, LHD, HSX — optimisation 3D, transport néoclassique, îlots magnétiques, configurations à cisaillement faible
- **Codes** : **METIS**, **JINTRAC**, **ASTRA** (intégrés) ; **M3D-C1**, **JOREK**, **BOUT++** (MHD non-linéaire) ; **GENE**, **GYRO**, **CGYRO**, **GS2** (gyrocinétique) ; **SOLPS-ITER**, **EDGE2D** (plasma de bord)

#### Fusion Inertielle
- Confinement inertiel (ICF) : NIF, LMJ, OMEGA, GEKKO XII
- Allumage rapide, cibles directes/indirectes, instabilités hydrodynamiques (Rayleigh-Taylor, Richtmyer-Meshkov)
- Codes : **HYDRA**, **LASNEX**, **DUED**, **CHIC**, **ARWEN**
- Fusion par confinement magnéto-inertiel (MTF) : MagLIF (Z Machine)

#### Chauffage et Diagnostics
- **Chauffage** : résonance cyclotronique ionique (ICH/ICRF), électronique (ECH/ECRH), injection de neutres (NBI), chauffage par ondes hybrides (LHCD)
- **Diagnostics** : réflectométrie, interférométrie (FIR, CO₂), diffusion Thomson (cohérente/incohérente), spectroscopie (X, visible, UV), bolométrie, sondes de Langmuir, CXRS, MSE, diagnostiques de neutres

### 2. Magnétohydrodynamique (MHD)

#### MHD Idéale
- Équations de la MHD idéale, théorème d'Alfvén, théorème de frozen-flux
- Ondes MHD : Alfvén, magnéto-soniques rapide et lente
- Équilibre 3D, surfaces magnétiques, transformée rotationnelle, cisaillement magnétique
- Stabilité MHD idéale : critère de Suydam, Mercier, ballonnement (ballooning), kink, tearing, interchange

#### MHD Résistive
- Équations de la MHD résistive, diffusion de champ magnétique
- Reconnection magnétique : Sweet-Parker, Petschek, reconnection collisionnelle et sans collision
- Instabilités résistives : tearing mode, Rutherford, mode néoclassique (NTM)
- **Codes** : **JOREK** (non-linéaire MHD plasma de bord), **M3D-C1** (MHD étendu), **NIMROD** (MHD 3D), **PIXIE3D** (MHD Hall)

#### MHD Astrophysique
- Disques d'accrétion, magnétorotationnelle (MRI), jets astrophysiques
- Vent solaire, magnétosphères stellaires et planétaires
- Dynamo, reconnexion dans la couronne solaire, éruptions (CME)
- Codes MHD astrophysiques : **PLUTO**, **ATHENA++**, **ZEUS-MP**, **ENZO**, **FLASH**, **AREPO**, **GIZMO**

### 3. Turbulence Plasma et Fluide

#### Turbulence Plasma
- Turbulence gyrocinétique et fluide dans les plasmas de fusion
- Transport turbulent : modes ITG, TEM, ETG, KBM
- Cascade d'énergie, zones de transport (zonal flows, GAMs, structures cohérentes)
- Interactions turbulence — MHD, intermittence, turbulence de bord
- **Codes** : **GENE**, **GYRO**, **CGYRO**, **GS2**, **ORB5**, **ELMFIRE**

#### Turbulence Fluide
- Turbulence homogène isotrope, spectre de Kolmogorov (k⁻⁵/³), dissipation
- Turbulence de paroi : couche limite turbulente, loi logarithmique, structures cohérentes (streaks, bursts, sweep-ejection)
- Turbulence en écoulement libre : jets, sillages, couches de mélange
- Turbulence compressible, turbulence multiphasique
- Simulation des grandes échelles (LES), simulation directe (DNS), modèles RANS (k-ε, k-ω SST, Reynolds Stress)

### 4. Mécanique des Fluides Fondamentale et Appliquée

#### Équations de Navier-Stokes
- Formulations incompressible et compressible
- Écoulements potentiels, visqueux, de Stokes
- Couche limite : Blasius, Falkner-Skan, séparation, transition laminaire-turbulent
- Aérodynamique : profils, ailes, corps élancés, ondes de choc, écoulements hypersoniques
- Convection naturelle et forcée, échangeurs de chaleur, transfert thermique

#### Rhéologie
- Fluides non-newtoniens : Bingham, Herschel-Bulkley, Carreau-Yasuda, Oldroyd-B, FENE-P
- Viscoélasticité, thixotropie, rhéofluidification, rhéoépaississement
- Écoulements en géométries complexes : extrusion, injection, filage
- **Codes** : **OpenFOAM** (viscoelasticFluidFoam), **RheoTool**, **Polyflow**

### 5. Dynamique des Fluides Numérique (CFD)

#### OpenFOAM
- Architecture, mailleurs (snappyHexMesh, blockMesh, cfMesh)
- Solveurs principaux : `simpleFoam`, `pimpleFoam`, `pisoFoam`, `rhoCentralFoam`, `reactingFoam`, `interFoam`, `multiphaseEulerFoam`
- Modèles de turbulence RANS/LES/DES
- Méthodes : volumes finis, schémas numériques (Gauss, TVD, ENO/WENO)
- Parallélisation MPI, décomposition de domaine (scotch, metis)

#### SU2 (Stanford University Unstructured)
- Solveur CFD open-source pour écoulements compressibles/incompressibles
- Aérodynamique, optimisation de forme, adjoint continu/discret
- Écoulements multiphysiques : aérothermique, FSI (Fluid-Structure Interaction)
- Couche limite, transition, écoulements turbulents RANS/LES
- Parallélisation MPI, GPU via Kokkos

#### Autres Codes CFD
- **ANSYS Fluent / CFX** : industrie — solveurs coupled/pressure-based, multiphasique (VOF, Euler-Euler, DPM), combustion
- **Code_Saturne** (EDF) : open-source, volumes finis, maillages non-structurés, écoulement incompressible/compressible
- **COMSOL Multiphysics** : éléments finis, CFD, MHD, transport de chaleur, plasma froid
- **NEK5000 / Neko** : éléments spectraux, DNS/LES haute performance, scalabilité extrême
- **deal.II** : éléments finis, solveurs adaptatifs, multiphysique

### 6. Méthodes sans Maillage (SPH et autres)

#### SPH (Smoothed Particle Hydrodynamics)
- Fondements : kernel smoothing, équations SPH, conservation
- Solveurs : **DualSPHysics**, **PySPH**, **SPHinXsys**, **SPH-flow**
- Applications : impacts d'ondes, sloshing, free surface, fluides multiphasiques, MHD-SPH
- Couplage SPH-FEM, SPH-DEM, SPH-OpenFOAM

#### Autres Méthodes sans Maillage
- Méthodes des éléments finis étendus (XFEM/GFEM)
- Méthodes vortex (Vortex Particle Methods)
- Lattice Boltzmann (LBM) : **Palabos**, **OpenLB**, **waLBerla**

### 7. Méthodes Multiphysiques

#### Couplages Fluide-Structure (FSI)
- Méthodes monolithiques, partitionnées, ALE (Arbitrary Lagrangian-Eulerian)
- Codes : **preCICE** (couplage multiphysique), **deal.II**, **OpenFOAM + solids4Foam**

#### Couplages Plasma-Paroi
- Interaction plasma-surface, érosion, dépôt, redéposition
- Modèles de bord, modèles de divertor, couche de gaine (sheath)
- Codes : **EIRENE** (transport de neutres), **DIVIMP**, **RENATE**

#### Couplages Fluide-Thermique-Électrique
- Induction électromagnétique en écoulements, MHD industrielle (pompes, freins MHD)
- Plasma froid, décharges, plasmas de procédé
- Codes : **COMSOL Plasma Module**, **PLASIMO**, **ZDPlasKin**

## Catégories arXiv

| ID | Catégorie | Description |
|----|-----------|-------------|
| physics.plasm-ph | Physique des Plasmas | Fusion, MHD, ondes, instabilités, diagnostics, plasmas de laboratoire, plasmas de procédé, interaction laser-plasma |
| physics.flu-dyn | Dynamique des Fluides | Navier-Stokes, turbulence, couche limite, CFD, rhéologie, écoulements multiphasiques, convection, aérodynamique |
| physics.space-ph | Physique Spatiale | MHD spatiale, vent solaire, magnétosphères, plasmas astrophysiques |
| astro-ph.HE | Astrophysique des Hautes Énergies | Disques d'accrétion, jets, sursauts gamma, pulsars |
| astro-ph.SR | Physique Solaire et Stellaire | MHD solaire, couronne, éruptions, dynamo stellaire |
| astro-ph.CO | Cosmologie | Milieu interstellaire, MHD galactique |
| physics.class-ph | Physique Classique | Mécanique des fluides fondamentale, oscillateurs non-linéaires |
| physics.chem-ph | Physique Chimique | Rhéologie, fluides complexes, polymères |
| physics.comp-ph | Physique Computationnelle | Méthodes numériques, HPC, SPH, LBM, simulation multiphysique |
| math.NA | Analyse Numérique | Schémas volumes finis, éléments finis, préconditionneurs, multigrilles |
| nlin.CD | Dynamique Chaotique | Turbulence, transition, instabilités, attracteurs |
| nlin.PS | Solitons et Patrons | Ondes non-linéaires en plasmas, structures cohérentes |

## Conférences et Revues Clés

### Conférences
- **APS-DPP** (American Physical Society — Division of Plasma Physics) — la plus grande conférence annuelle en physique des plasmas
- **EPS-PPP** (European Physical Society — Plasma Physics and Controlled Fusion)
- **IAEA FEC** (Fusion Energy Conference) — fusion magnétique et inertielle
- **SOFE** (Symposium on Fusion Engineering)
- **TTF** (Transport Task Force Workshop)
- **APS-DFD** (Division of Fluid Dynamics) — mécanique des fluides
- **ETC** (European Turbulence Conference)
- **ICCFD** (International Conference on Computational Fluid Dynamics)
- **OpenFOAM Conference** & **SU2 Conference**
- **SPHERIC** (SPH European Research Interest Community)

### Revues Scientifiques
| Revue | Domaine | Facteur d'Impact |
|-------|---------|-----------------|
| Nuclear Fusion | Fusion contrôlée | ~3.5 |
| Plasma Physics and Controlled Fusion | Physique des plasmas | ~2.5 |
| Physics of Plasmas | Physique des plasmas | ~2.0 |
| Journal of Plasma Physics | Plasmas, MHD, ondes | ~1.8 |
| Journal of Fluid Mechanics | Mécanique des fluides | ~3.5 |
| Physics of Fluids | Dynamique des fluides | ~4.0 |
| Journal of Computational Physics | Méthodes numériques en physique | ~3.5 |
| Computer Physics Communications | Codes en physique | ~3.0 |
| Fusion Engineering and Design | Ingénierie de la fusion | ~1.8 |
| Plasma Sources Science and Technology | Plasmas de procédé, décharges | ~3.5 |
| High Temperature Plasma Physics | Plasmas chauds | ~1.5 |
| Physical Review Fluids | Dynamique des fluides | ~2.5 |
| Physical Review E — Statistical, Nonlinear, and Soft Matter Physics | Fluides, plasmas, non-linéaire | ~2.5 |
| Journal of Rheology | Rhéologie | ~3.0 |
| Computers & Fluids | CFD | ~3.0 |

## Articles Notables Récents (2023–2026)

### Fusion Magnétique
- A. J. Creely et al., *Overview of the SPARC tokamak*, Journal of Plasma Physics, 2023 — conception du premier tokamak à fusion nette (DT)
- H. Zohm et al., *EU DEMO design and R&D roadmap*, Fusion Engineering and Design, 2023
- M. Greenwald et al., *20-year plan for magnetic fusion energy*, Nature, 2024
- A. Kendl et al., *Edge turbulence in tokamak and stellarator geometries*, Nuclear Fusion, 2024

### MHD et Stabilité
- S. C. Jardin et al., *Extended MHD simulations of disruptions in ITER*, Physics of Plasmas, 2024
- F. Porcelli et al., *Resistive tearing mode dynamics in burning plasmas*, Plasma Physics and Controlled Fusion, 2023
- T. S. Pedersen et al., *First results from Wendelstein 7-X stellarator*, Nature Physics, 2023

### Turbulence Plasma
- F. Jenko et al., *Gyrokinetic turbulence at reactor-relevant parameters*, Journal of Plasma Physics, 2024
- T. Görler et al., *Multiscale gyrokinetic turbulence simulation*, Physics of Plasmas, 2025
- P. H. Diamond et al., *Zonal flows and transport bifurcations*, Nuclear Fusion, 2023

### Fusion Inertielle
- A. B. Zylstra et al., *Burning plasma achieved in inertial fusion*, Nature, 2023
- H. Abu-Shawareb et al., *Achievement of target gain >1 in inertial confinement fusion*, Physical Review Letters, 2024
- R. Betti et al., *Inertial confinement fusion: progress and pathways*, Nature Reviews Physics, 2023

### Mécanique des Fluides et Turbulence
- B. Eckhardt et al., *Dynamical systems approach to turbulence in pipe flow*, Journal of Fluid Mechanics, 2023
- J. Jiménez et al., *Wall turbulence at high Reynolds numbers*, Annual Review of Fluid Mechanics, 2024
- K. R. Sreenivasan et al., *Turbulence, fractals, and scaling*, Physics of Fluids, 2024

### CFD et Méthodes Numériques
- T. D. Economon et al., *SU2: an open-source suite for multiphysics simulation*, AIAA Journal, 2023 (révision)
- H. Jasak et al., *OpenFOAM: advances in unstructured CFD*, Computers & Fluids, 2024
- P. K. Yeung et al., *Direct numerical simulation of turbulent flows*, Annual Review of Fluid Mechanics, 2023

### SPH et Méthodes sans Maillage
- M. Gómez-Gesteira et al., *DualSPHysics: open-source SPH solver*, Computer Physics Communications, 2023
- X. Zhang et al., *SPH methods for multiphase flows*, Journal of Computational Physics, 2024
- R. Vacondio et al., *SPH for free-surface flows: advances and challenges*, Computer Methods in Applied Mechanics and Engineering, 2024

### Rhéologie
- G. H. McKinley et al., *Rheology of complex fluids in confined geometries*, Journal of Rheology, 2024
- A. N. Morozov et al., *Instabilities in viscoelastic flows* , Annual Review of Fluid Mechanics, 2023

### MHD Astrophysique
- S. Fromang et al., *Magnetorotational instability in accretion disks*, Astronomy & Astrophysics Review, 2023
- J. A. Stone et al., *ATHENA++: MHD for astrophysics*, The Astrophysical Journal Supplement Series, 2023
- C. Gammie et al., *Black hole accretion and jet launching*, Annual Review of Astronomy and Astrophysics, 2024

## Laboratoires et Centres de Recherche

### Fusion et Plasmas
| Institution | Pays | Installations Clés |
|-------------|------|--------------------|
| ITER Organization | France (Cadarache) | ITER (en construction) |
| CEA / IRFM | France | Tore Supra/WEST, LMJ |
| Max-Planck-Institut für Plasmaphysik (IPP) | Allemagne | ASDEX Upgrade, Wendelstein 7-X |
| MIT PSFC | USA | SPARC (en construction), Alcator C-Mod (arrêté) |
| General Atomics (DIII-D) | USA | DIII-D Tokamak |
| PPPL (Princeton) | USA | NSTX-U, ITER contributions |
| EUROfusion Consortium | Europe (multi-site) | JET (arrêté), DEMO roadmap |
| KSTAR / KFE | Corée du Sud | KSTAR |
| EAST / ASIPP | Chine | EAST |
| JT-60SA (QST) | Japon | JT-60SA |
| LLNL | USA | NIF (fusion inertielle) |
| LLE (Rochester) | USA | OMEGA (fusion inertielle) |
| Sandia National Laboratories | USA | Z Machine (MagLIF) |

### Mécanique des Fluides et CFD
| Institution | Domaines |
|-------------|----------|
| Stanford (CTR) | Turbulence, LES, DNS |
| TU München | Aérodynamique, CFD, high-order methods |
| Imperial College London | CFD, multiphase, rhéologie |
| CNRS (LEGI, IMFT, IRPHE) | Turbulence, hydraulique, magnétohydrodynamique |
| ONERA | Aérodynamique, aérothermique, supersonique/hypersonique |
| DLR (Deutsches Zentrum für Luft- und Raumfahrt) | CFD, TAU, SU2 contributions |
| NASA Ames / Langley | CFL3D, FUN3D, LAURA, aérodynamique spatiale |

## Logiciels et Outils

### Fusion et Physique des Plasmas
| Logiciel | Domaine | Site |
|----------|---------|------|
| **JINTRAC** | Suite intégrée plasma de fusion | euro-fusion.org |
| **METIS** | Modélisation intégrée rapide | cea.fr |
| **JOREK** | MHD non-linéaire plasma de bord | jorek.eu |
| **M3D-C1** | MHD étendu non-linéaire | pppl.gov |
| **NIMROD** | MHD 3D non-linéaire | nimrodteam.org |
| **GENE** | Turbulence gyrocinétique | genecode.org |
| **GYRO** | Gyrocinétique flux-tube | generalatomtics.com |
| **CGYRO** | Gyrocinétique globale | generalatomtics.com |
| **BOUT++** | Simulation plasma de bord | bout.dev |
| **SOLPS-ITER** | Plasma de bord + neutres | iter.org |
| **EIRENE** | Transport de neutres | eirene.de |
| **ORB5** | Gyrocinétique global | orb5.org |
| **HYDRA** | ICF multi-physics | llnl.gov |
| **CHIC** | ICF hydrodynamique | cea.fr |
| **PLASIMO** | Plasma froid, procédé | plasimo.phys.tue.nl |
| **ZDPlasKin** | Cinétique plasmas | zdplaskin.laplace.univ-tlse.fr |

### CFD et Mécanique des Fluides
| Logiciel | Domaine | Licence |
|----------|---------|---------|
| **OpenFOAM** | CFD polyvalent | GPL (open-source) |
| **SU2** | Aérodynamique, optimisation | LGPL (open-source) |
| **Code_Saturne** | CFD industriel | GPL (open-source) |
| **NEK5000 / Neko** | DNS/LES spectral | BSD (open-source) |
| **deal.II** | Éléments finis multiphysique | LGPL (open-source) |
| **preCICE** | Couplage multiphysique | BSD (open-source) |
| **DualSPHysics** | SPH | LGPL (open-source) |
| **PySPH** | SPH Python | MIT (open-source) |
| **Palabos** | Lattice Boltzmann | AGPL (open-source) |
| **OpenLB** | Lattice Boltzmann | GPL (open-source) |
| **ANSYS Fluent** | CFD industriel | Commercial |
| **ANSYS CFX** | CFD turbomachines | Commercial |
| **COMSOL** | Multiphysique éléments finis | Commercial |
| **STAR-CCM+** | CFD industriel polyvalent | Commercial |

### Visualisation et Post-Traitement
| Outil | Usage |
|-------|-------|
| **ParaView** | Visualisation CFD et plasma (VTK, XDMF, HDF5) |
| **VisIt** | Visualisation données massives HPC |
| **Matplotlib / Mayavi** | Python pour post-traitement |
| **XDMF / HDF5** | Formats de données pour simulation |
| **yt** | Visualisation astrophysique et plasma |
| **Gnuplot** | Tracés 2D, séries temporelles |

## Standards et Normes

### CFD et Validation
- **ASME V&V 20** : Standard for Verification and Validation in CFD
- **AIAA G-077** : Guide for Verification and Validation of Computational Fluid Dynamics Simulations
- **ERCOFTAC** : Best Practice Guidelines for CFD (European Research Community on Flow, Turbulence and Combustion)
- **CFD General Notation System (CGNS)** : Standard de stockage de données CFD

### Fusion
- **ITER Design Integration Standards** : Normes de conception ITER
- **ISO 10656** : Normes pour composants de fusion
- **Nuclear Safety Standards (RCC-MRx)** : Codes de construction nucléaire pour composants de fusion
- **EFDA / EUROfusion Design Codes** : Codes de conception pour DEMO

## Veille

### Suivi Quotidien/Hebdomadaire
```bash
# Dernières soumissions en physique des plasmas
https://arxiv.org/list/physics.plasm-ph/recent

# Dernières soumissions en dynamique des fluides
https://arxiv.org/list/physics.flu-dyn/recent

# MHD et plasmas spatiaux
https://arxiv.org/list/physics.space-ph/recent

# MHD astrophysique
https://arxiv.org/list/astro-ph.HE/recent
https://arxiv.org/list/astro-ph.SR/recent

# Méthodes numériques
https://arxiv.org/list/math.NA/recent
https://arxiv.org/list/physics.comp-ph/recent
```

### Mots-Clés de Recherche par Thème
- **Fusion magnétique** : tokamak, stellarator, MHD equilibrium, plasma disruption, ELM, H-mode, pedestal, divertor, burning plasma, gyrokinetic turbulence
- **Fusion inertielle** : ICF, ignition, hot spot, DT capsule, Rayleigh-Taylor, shock ignition, fast ignition
- **MHD** : ideal MHD, resistive MHD, magnetic reconnection, tearing mode, Alfvén wave, dynamo, MRI
- **Turbulence plasma** : ITG, TEM, ETG, gyrokinetic, zonal flow, transport, intermittency, GAM
- **CFD** : OpenFOAM, SU2, finite volume, finite element, LES, DNS, RANS, immersed boundary, high-order methods
- **Turbulence fluide** : Kolmogorov, boundary layer, wall turbulence, coherent structures, DNS, isotropic turbulence, Reynolds number
- **Rhéologie** : viscoelastic, non-Newtonian, Carreau, Oldroyd-B, shear-thinning, extensional rheology, polymer
- **SPH** : smoothed particle hydrodynamics, particle method, free surface, multiphase, GPU
- **MHD astrophysique** : accretion disk, magnetorotational instability, jet, corona, solar wind, star formation
- **Multiphysique** : fluid-structure interaction, conjugate heat transfer, plasma-wall interaction, FSI, preCICE

### API arXiv pour Requêtes Programmées
```python
# Exemple de requête Python pour la veille automatique
import urllib.request, xml.etree.ElementTree as ET

def fetch_arxiv(cat, max_results=10):
    url = (f"http://export.arxiv.org/api/query?"
           f"search_query=cat:{cat}&"
           f"sortBy=submittedDate&sortOrder=descending&"
           f"max_results={max_results}")
    with urllib.request.urlopen(url) as f:
        return ET.parse(f)

# Utilisation
# fetch_arxiv("physics.plasm-ph")  # Plasmas
# fetch_arxiv("physics.flu-dyn")   # Fluides
```

### Flux RSS à Surveiller
- **arXiv RSS** : `https://rss.arxiv.org/rss/physics.plasm-ph` et `https://rss.arxiv.org/rss/physics.flu-dyn`
- **Nuclear Fusion** : suivi via site IOP Science
- **Journal of Fluid Mechanics** : suivi via Cambridge Core
- **Physics of Plasmas** : suivi via AIP Publishing

## Compétences Associées

- **astronomy-astrophysics-ai** : MHD astrophysique, disques d'accrétion, plasmas stellaires
- **arvix** : Usage général de l'API arXiv
- **arvix-research-competence** : Méthodologie de recherche sur arXiv

## Références Bibliographiques Essentielles

### Physique des Plasmas
- J. P. Freidberg, *Ideal MHD*, Cambridge University Press (2014)
- J. P. Freidberg, *Plasma Physics and Fusion Energy*, Cambridge University Press (2007)
- J. Wesson, *Tokamaks* (4th ed.), Oxford University Press (2011)
- R. Hazeltine & J. Meiss, *Plasma Confinement*, Dover (2003)
- P. Helander & D. Sigmar, *Collisional Transport in Magnetized Plasmas*, Cambridge (2005)
- T. J. M. Boyd & J. J. Sanderson, *The Physics of Plasmas*, Cambridge (2003)
- F. Chen, *Introduction to Plasma Physics and Controlled Fusion*, Springer (2016)

### Magnétohydrodynamique
- D. Biskamp, *Magnetohydrodynamic Turbulence*, Cambridge (2003)
- D. Biskamp, *Nonlinear Magnetohydrodynamics*, Cambridge (1997)
- E. Priest & T. Forbes, *Magnetic Reconnection*, Cambridge (2000)
- H. Goedbloed & S. Poedts, *Principles of Magnetohydrodynamics*, Cambridge (2004)

### Mécanique des Fluides
- L. D. Landau & E. M. Lifshitz, *Fluid Mechanics* (2nd ed.), Butterworth-Heinemann (1987)
- G. K. Batchelor, *An Introduction to Fluid Dynamics*, Cambridge (2000)
- P. Kundu, I. Cohen & D. Dowling, *Fluid Mechanics* (6th ed.), Academic Press (2015)
- S. B. Pope, *Turbulent Flows*, Cambridge (2000)
- H. Schlichting & K. Gersten, *Boundary-Layer Theory* (9th ed.), Springer (2017)

### CFD et Méthodes Numériques
- J. H. Ferziger, M. Perić & R. L. Street, *Computational Methods for Fluid Dynamics* (4th ed.), Springer (2020)
- H. K. Versteeg & W. Malalasekera, *An Introduction to Computational Fluid Dynamics* (2nd ed.), Pearson (2007)
- C. Hirsch, *Numerical Computation of Internal and External Flows* (2nd ed.), Butterworth-Heinemann (2007)
- F. Moukalled, L. Mangani & M. Darwish, *The Finite Volume Method in Computational Fluid Dynamics*, Springer (2016)
- R. J. LeVeque, *Finite Volume Methods for Hyperbolic Problems*, Cambridge (2002)

### Rhéologie
- R. B. Bird, R. C. Armstrong & O. Hassager, *Dynamics of Polymeric Liquids* (2nd ed.), Wiley (1987)
- F. A. Morrison, *Understanding Rheology*, Oxford (2001)
- R. Larson, *The Structure and Rheology of Complex Fluids*, Oxford (1999)

### SPH
- G. R. Liu & M. B. Liu, *Smoothed Particle Hydrodynamics: A Meshfree Particle Method*, World Scientific (2003)
- J. Monaghan, *Smoothed Particle Hydrodynamics*, Annual Review of Astronomy and Astrophysics, 1992 (article fondateur)