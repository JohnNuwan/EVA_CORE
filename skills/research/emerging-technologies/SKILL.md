---
name: emerging-technologies
description: >-
  Compétence de recherche en technologies émergentes en informatique (cs.ET).
  Couvre l'ordinateur neuromorphique, le calcul quantique (NISQ, correction
  d'erreur, gates, algorithmes variés), le biocomputing et ADN computing, le
  calcul optique et photonique, les memristors et circuits neuromorphiques,
  les approches au-delà de von Neumann (in-memory computing, near-data
  processing), les technologies cryogéniques pour le calcul, la microfluidique
  computationnelle, les matériaux 2D pour l'électronique, ReRAM/PCM/STT-MRAM,
  la spintronique, l'ordinateur à réservoir, les systèmes auto-organisants et
  le matériel biologique. Inclus la veille sur IRDS roadmap, DARPA programmes
  et NIST.
category: research
---

# Compétence en Recherche en Technologies Émergentes (cs.ET)

## Présentation

La catégorie cs.ET (Emerging Technologies) sur arXiv couvre les technologies informatiques
émergentes qui repoussent les limites des architectures conventionnelles de von Neumann.
Elle rassemble environ 100 à 200 nouvelles soumissions par mois, avec des intersections
fortes avec quant-ph (calcul quantique), physics.app-ph (physique appliquée), cond-mat.mes-hall
(physique mésoscopique), et cs.AR (architecture matérielle).

Cette compétence fournit une structure complète pour naviguer dans le paysage des
technologies de rupture en informatique : des paradigmes de calcul entièrement nouveaux
aux innovations matérielles concrètes qui façonnent la prochaine génération de systèmes
informatiques.

## Domaines de Recherche

### 1. Calcul Neuromorphique

#### 1.1 Circuits Neuromorphiques et Memristors
- **Memristors** : dispositifs à résistance variable (TiO₂, HfO₂, TaOₓ) ; plasticité
  synaptique via modulation de conductance
- **Circuits neuromorphiques** : puces qui imitent l'architecture neuronale biologique
  (TrueNorth d'IBM, Loihi d'Intel, BrainScaleS, SpiNNaker)
- **Neuromorphic engineering** : conception VLSI de neurones et synapses artificiels,
  circuits à spikes (SNN — Spiking Neural Networks)
- **Poids analogiques** : stockage de poids synaptiques en mémoire non volatile
- **Approches mixed-signal** : circuits analogiques/numériques hybrides pour
  l'accélération neuromorphique
- **CROSS** : dispositifs crossbar arrays pour la multiplication matrice-vecteur in-situ

#### 1.2 Réseaux de Neurones à Impulsions (SNN)
- **Codage temporel (temporal coding)** : information encodée dans le timing des spikes
- **Plasticité STDP** (Spike-Timing Dependent Plasticity) : apprentissage non supervisé
  biologique
- **Conversion ANN→SNN** : conversion de réseaux profonds conventionnels en SNN
- **Apprentissage sur SNN** : surrogate gradients, backpropagation through time,
  direct training
- **Architectures SNN profondes** : Spiking ResNet, Spiking Transformer, SEW ResNet
- **Hardware SNN** : puces neuromorphiques dédiées, accélérateurs événementiels
- **Applications** : vision événementielle (event cameras), traitement audio à faible
  consommation, contrôle robotique en temps réel, edge AI ultra-low-power

### 2. Calcul Quantique

#### 2.1 Algorithmes Quantiques
- **Algorithme de Shor** : factorisation en temps polynomial, logarithme discret
- **Algorithme de Grover** : recherche non structurée en O(√N)
- **Algorithme de Deutsch-Jozsa, Bernstein-Vazirani, Simon** : premiers algorithmes
  démontrant la supériorité quantique
- **Algorithme de Grover adaptatif** : variantes pour optimisation combinatoire
- **HHL** (Harrow-Hassidim-Lloyd) : résolution de systèmes linéaires en temps logarithmique
- **QSVT** (Quantum Singular Value Transformation) : cadre unifié pour une large
  classe d'algorithmes quantiques
- **Quantum walks** : marches aléatoires quantiques pour la recherche sur graphes
- **Amplitude amplification** et **estimation de phase quantique**
- **Quantum signal processing** : boîte à outils pour le traitement de signaux
  quantiques

#### 2.2 Calcul Quantique NISQ (Noisy Intermediate-Scale Quantum)
- **Circuits variationnels (VQE)** : Variational Quantum Eigensolver pour la chimie
  quantique
- **QAOA** (Quantum Approximate Optimization Algorithm) : optimisation combinatoire
  sur machines NISQ
- **Quantum Machine Learning variationnel** : circuits paramétrés pour l'apprentissage
- **Atténuation d'erreur (error mitigation)** : zero-noise extrapolation, probabilistic
  error cancellation, Clifford data regression
- **Mesures tomographiques** : tomography par paquets de circuits
- **Compilation adaptée NISQ** : optimisation de profondeur, routage de qubits,
  insertion de barrières
- **Échantillonnage de circuits aléatoires** : démonstrations de suprématie quantique
  (Google Sycamore, Zuchongzhi)
- **Plateformes NISQ** : IBM Q (superconducting), Rigetti, IonQ (ion traps),
  Quantinuum (trapped ions), Xanadu (photonique)

#### 2.3 Correction d'Erreur Quantique (QEC)
- **Codes de stabilisation** : codes CSS, [[n,k,d]] stabilizer codes
- **Code de Shor et code de Steane** : premiers codes correcteurs
- **Surface codes** et **color codes** : codes topologiques 2D
- **Code de Bacon-Shor** : code de sous-système
- **Codes LDPC quantiques** : codes de parité à faible densité pour haute performance
- **Protocoles de mesure et de correction** : syndrome extraction, fault-tolerant
  measurement
- **Portes tolérantes aux fautes (fault-tolerant gates)** : transversalité,
  magic state distillation
- **Architectures FTQC** : ordinateurs quantiques tolérants aux fautes à grande échelle
- **Taux d'erreur physique → logique** : seuils de correction, overhead en qubits
- **Décodage en temps réel** : decoders (MWPM, Union-Find, neural decoders)
- **Démonstrations récentes** : Google Quantum AI (Sycamore), Harvard/QuEra (atomes neutres)

#### 2.4 Portes et Registres Quantiques
- **Portes à un qubit** : X, Y, Z, Hadamard, phase (S, T), rotation (Rx, Ry, Rz)
- **Portes à deux qubits** : CNOT, CZ, SWAP, iSWAP, CPHASE, Bell measurement
- **Portes à trois qubits** : Toffoli (CCNOT), Fredkin (CSWAP)
- **Fidélité des portes** : randomized benchmarking, gate set tomography
- **Cross-resonance gates** : portes sur processeurs supraconducteurs
- **Molmer-Sørensen gates** : portes sur ions piégés
- **Rydberg gates** : portes sur atomes neutres
- **Native gates** : jeu de portes natives d'une plateforme donnée
- **Compilation de circuits** : optimisation de séquences de portes, transpilation

#### 2.5 Paradigmes et Plateformes
- **Supraconducteurs** : qubits transmon, fluxonium, Xmon — IBM, Google, Rigetti
- **Ions piégés** : qubits hyperfins, portes laser — IonQ, Quantinuum, Honeywell
- **Atomes neutres** : qubits Rydberg, réseaux d'atomes — QuEra, Pasqal
- **Photonique quantique** : qubits de photons, portes linéaires — Xanadu, PsiQuantum
- **Points quantiques (spin qubits)** : qubits dans des boîtes quantiques semi-conductrices
- **Qubits topologiques** : anyons de Majorana, ordinateur topologique — Microsoft
- **Diamant NV-center** : centres azote-lacune pour l'informatique quantique
- **Kerr-cat qubits** : qubits à chat de Schrödinger pour la correction d'erreur
  autonome
- **Calcul quantique adiabatique** : annealing quantique — D-Wave
- **Calcul quantique mesure-based (MBQC)** : cluster states, téléportation de portes

#### 2.6 Quantum Machine Learning
- **Quantum neural networks (QNN)** : circuits paramétrés pour l'apprentissage
- **Quantum kernel methods** : noyaux quantiques pour SVM
- **Quantum generative models** : QGAN, quantum Boltzmann machines
- **Quantum reinforcement learning** : apprentissage par renforcement sur
  processeurs quantiques
- **Quantum natural language processing (QNLP)** : traitement du langage naturel
  quantique
- **Quantum chemistry on quantum computers** : simulation de Hamiltoniens moléculaires
- **Quantum optimization** : QUBO, Ising machines, quantum annealing pour optimisation
- **Barren plateaus** : problème des plateaux plats dans le QML variationnel
- **Expressivité et évolutivité** : avantage quantique en ML
- **Quantum neural architecture search** : recherche d'architectures neuronales
  quantiques

### 3. Biocomputing et ADN Computing

#### 3.1 ADN Computing (DNA Computing)
- **Principe d'Adleman** : résolution du problème du chemin hamiltonien via ADN (1994)
- **Encodage de données dans l'ADN** : stockage d'information via synthèse et
  séquençage d'ADN
- **Algorithmes moléculaires** : portes logiques ADN, circuits ADN, automates ADN
- **Strand displacement** : déplacement de brins comme mécanisme de calcul
  moléculaire
- **Réactions en chaîne** : amplification, ligation, clivage pour le calcul
- **Membranes et lipides** : compartiments pour réactions bio-informatiques
- **DNA origami** : nanorobots et nanostructures ADN pour le calcul spatial
- **Hybridation compétitive** : détection et résolution de problèmes combinatoires
- **Mémoire ADN** : stockage à ultra-haute densité (exaoctets/gramme)
- **Random Access Memory ADN** : adressage et accès aléatoire aux données ADN
- **ADN comme ordinateur universel** : Turing-complétude du calcul ADN
- **Démonstrations** : solveur SAT ADN, addition binaire ADN, oscillateurs ADN

#### 3.2 Biocomputing et Matériel Biologique
- **Biologie synthétique computationnelle** : circuits génétiques, réseaux de
  régulation synthétiques
- **Cell computing** : cellules bactériennes comme processeurs — E. coli reprogrammé
  pour le calcul
- **Bio-détection et senseurs moléculaires** : diagnostics computationnels in cellulo
- **Organoïdes et mini-cerveaux** : calcul biologique par tissus neuronaux
- **Neurophéromones et signalisation cellulaire** : communication inter-cellulaire
  pour le calcul distribué
- **Slime mold computing (Physarum polycephalum)** : calcul par réseaux de
  plasmodium, résolution de problèmes de graphes et chemins optimaux
- **Bacterial computing** : colonies bactériennes comme systèmes de calcul parallèle
- **Fungal networks** : réseaux de champignons pour l'informatique distribuée
- **Protocell computing** : protocellules artificielles pour le calcul
  moléculaire
- **Biomolecular neural networks** : réseaux de neurones biomoléculaires
- **Living materials** : matériaux vivants programmables combinant calcul et croissance

#### 3.3 Stockage et Mémoire Biologique
- **ADN comme support de stockage** : densité théorique de 10¹⁸ octets/mm³
- **Codage correcteur pour ADN** : codes détecteurs d'erreur pour la synthèse ADN
- **Encodage de fichiers numériques en ADN** : compression, redondance, adressage
- **DNA Fountain** : codage près de la capacité de Shannon pour l'ADN
- **Séquençage et lecture** : Nanopore, Illumina pour le décodage rapide
- **Archives ADN** : durabilité millénaire, coût décroissant
- **Intégration computation-stockage** : calcul in-storage biologique

### 4. Calcul Optique et Photonique

#### 4.1 Calcul Optique Analogique
- **Multiplication matrice-vecteur optique** : réalisée via réseaux de diffraction,
  interféromètres Mach-Zehnder
- **Transformée de Fourier optique** : réalisée physiquement par une simple lentille
- **Corrélation optique** : reconnaissance de motifs et filtrage spatial
- **Réseaux de neurones optiques** : neurones et synapses photoniques
- **On-chip optical neural networks** : circuits intégrés photoniques (PIC)
  pour l'inférence
- **Photonic tensor cores** : cœurs de multiplication tensorielle optiques
- **Optical reservoir computing** : ordinateur à réservoir photonique
- **Diffractive Deep Neural Networks (D²NN)** : couches diffractives pour
  la classification optique
- **Optical computing pour l'IA** : inférence ML ultra-rapide et économe

#### 4.2 Plateformes Photoniques
- **Silicon photonics** : circuits intégrés photoniques sur SOI (silicon-on-insulator)
- **Lithium niobate (LiNbO₃)** : modulateurs électro-optiques rapides
- **III-V photonics** : InP, GaAs pour sources lasers intégrées
- **Micro-résonateurs en anneau** : filtres, modulateurs, commutateurs
- **Interféromètres Mach-Zehnder** : portes optiques reconfigurables
- **Réseaux de diffraction** : matrices de phase programmables (LCOS, MEMS)
- **Photonic integrated circuits (PIC)** : intégration monolithique de composants
  optiques
- **Hybrid integration** : co-intégration électronique-photonique

#### 4.3 Optical Interconnects et Communication
- **Interconnexions optiques pour datacenters** : fibre optique pour
  l'interconnexion haute vitesse
- **Optical switching** : commutateurs optiques pour réseaux reconfigurables
- **Co-packaged optics** : optique intégrée au package du processeur
- **Cohérence et détection** : modulation cohérente, détection directe
- **Wavelength Division Multiplexing (WDM)** : multiplexage en longueur d'onde
  pour la bande passante
- **Silicon photonics pour HPC** : liens optiques pour supercalculateurs

#### 4.4 Nouveaux Paradigmes Photoniques
- **Ising machines optiques** : solveurs d'optimisation combinatoire photoniques
- **Simulation quantique photonique** : simulateurs quantiques basés sur l'optique
- **Computing with spatial light modulators (SLM)** : calcul par modulation
  spatiale de lumière
- **Frequency combs pour le calcul** : calcul parallèle en fréquence
- **Nonlinear optical computing** : calcul utilisant des effets optiques non linéaires
- **Optical memristors** : memristors photoniques pour neuromorphique optique
- **Quantum optical computing** : portes logiques quantiques optiques à photons uniques

### 5. Memristors et Circuits Neuromorphiques

#### 5.1 Physique et Matériaux des Memristors
- **Mécanismes de commutation** : filamentaire (CF), interfacial, uniforme
- **Oxydes de métaux de transition** : HfO₂, TaOₓ, TiO₂, NiO, SrTiO₃
- **Matériaux 2D pour memristors** : MoS₂, hBN, graphène
- **Electrochemical metallization (ECM)** : cellules CBRAM à pont métallique
- **Valence change mechanism (VCM)** : commutation par migration d'oxygène
- **Thermochemical mechanism (TCM)** : commutation par effet Joule
- **Memristors polymères et organiques** : films minces flexibles
- **Ferroelectric memristors** : FeFET, FTJ à ferroélectrique
- **Analog switching** : conductance multi-niveaux pour poids synaptiques
- **Endurance et rétention** : cycles d'écriture, stabilité temporelle

#### 5.2 Architectures et Circuits
- **Crossbar arrays** : matrices de memristors pour multiplication matrice-vecteur
- **One-transistor-one-resistor (1T1R)** : architecture avec transistor sélecteur
- **Passive crossbars** : matrices sans sélecteur, problèmes de sneak-path
- **NAND-like et NOR-like arrays** : organisations mémoire alternatives
- **Sense amplifiers pour memristors** : lecture de conductance multi-niveaux
- **Drivers et séquenceurs** : circuits de contrôle d'écriture et de lecture
- **Integration CMOS-memristor** : co-intégration BEOL (back-end-of-line)
- **Memristive Processing-In-Memory (PIM)** : exécution de calcul dans la mémoire
- **Multiply-Accumulate (MAC) in-situ** : calcul MAC directement dans le crossbar
- **Memristive neural network accelerators** : accélérateurs SNN et DNN à memristors

#### 5.3 Applications Memristives
- **Accélérateurs d'inférence IA** : calcul MAC massivement parallèle
- **SNN sur memristors** : implémentation de STDP et réseaux à spikes
- **Logique memristive** : portes logiques matérielles (IMP, MAGIC, stateful logic)
- **Memcomputing** : calcul universel avec memristors
- **Brouillard et chaos memristif** : génération de nombres aléatoires, cryptographie
- **Mémoire non volatile de masse** : remplacement potentiel de Flash/NAND
- **Compute-in-memory** : réduction du bottleneck mémoire-computation
- **Hadware security** : PUF (Physical Unclonable Functions) à memristors

### 6. Approches au-delà de von Neumann

#### 6.1 In-Memory Computing (IMC)
- **Processing-in-Memory (PIM)** : intégration d'unités de calcul dans les bancs
  mémoire (près des cellules)
- **Compute-in-Memory (CIM)** : exécution de calculs dans les cellules mémoire
  elles-mêmes
- **Near-Data Processing (NDP)** : unités de calcul placées près de la mémoire
  (dans le hub mémoire, le DIMM, ou la couche logique du HBM)
- **PIM architectures** : Samsung HBM-PIM, UPMEM, AXDIMM
- **ISA PIM (Processing-In-Memory)** : jeux d'instructions pour exécution in-memory
- **Logic-in-Memory (LIM)** : portes logiques intégrées dans les cellules mémoire
- **Charge-domain computing** : calcul dans le domaine de la charge électrique
  dans les DRAM
- **Memristive PIM** : in-memory computing via crossbars de memristors
- **Analogue in-memory computing** : calcul analogique dans les mémoires non volatiles
- **Application-specific PIM** : PIM pour IA, recommandation, base de données

#### 6.2 Near-Data Processing (NDP)
- **Bottleneck mémoire (Memory Wall)** : divergence de vitesse CPU-mémoire
- **Logic-in-HBM** : unités de calcul dans les couches logiques du HBM2/3
- **3D-stacked NDP** : empilement 3D de mémoire DRAM sur logique de calcul
- **Active Memory Cube** : cubes mémoire avec logique embarquée
- **Processing using Memory (PuM)** : exécution d'opérations dans les sous-tableaux
- **NDP pour bases de données** : filtrage, agrégation, projection in-situ
- **NDP pour ML** : GEMM, convolution, embedding lookup dans la mémoire
- **NDP pour graph processing** : opérations sur graphes dans la mémoire proche
- **NDP pour analyse de données** : scan et réduction dans les bancs mémoire

#### 6.3 Nouveaux Paradigmes Architecturaux
- **Non-von Neumann architectures** : tout modèle de calcul ne séparant pas
  strictement mémoire et unité de calcul
- **Disaggregated computing** : calcul désagrégé avec mémoires et processeurs
  séparés dans le datacenter
- **Computational RAM (C-RAM)** : DRAM avec capacités de calcul embarquées
- **Dataflow architectures** : calcul piloté par les données (Systolic arrays,
  spatial architectures)
- **Coarse-Grained Reconfigurable Arrays (CGRA)** : matrices reconfigurables
  pour le calcul de flux
- **Systolic arrays** : matrices systoliques (Google TPU, etc.) pour GEMM
- **Storage-class memory (SCM)** : hiérarchie mémoire repensée autour de
  nouvelles technologies non volatiles
- **Unified memory architectures** : architectures à mémoire unifiée CPU-GPU

### 7. Technologies Cryogéniques pour le Calcul

#### 7.1 Cryo-CMOS et Électronique à Basse Température
- **Cryogenic CMOS (Cryo-CMOS)** : conception de transistors CMOS fonctionnant
  à 4K et 77K
- **Low-temperature electronics** : amélioration des performances à froid
  (mobilité, résistance de canal)
- **Cryo-memories** : mémoires cryogéniques (SRAM, DRAM, MRAM)
- **Single-flux quantum (SFQ) logic** : logique supraconductrice rapide
  (RSFQ, AQFP, eSFQ)
- **Rapid Single Flux Quantum (RSFQ)** : commutation à ps, consommation ~10⁸
  inférieure au CMOS
- **Adiabatic Quantum Flux Parametron (AQFP)** : logique supraconductrice
  ultra-faible puissance
- **Refrigeration pour HPC** : cryoréfrigérateurs pour datacenters cryogéniques
- **Interfaces thermiques** : gestion de la chaleur à des températures cryogéniques
- **Voltage references et bandgap en cryogénie** : circuits de référence à 4K

#### 7.2 Contrôle et Interface avec Qubits
- **Cryo-CMOS pour contrôle de qubits** : ASICs cryogéniques pour la génération
  d'impulsions, le filtrage, et l'amplification
- **DAC/ADC cryogéniques** : conversion numérique-analogique à 4K pour le
  pilotage de qubits
- **Amplificateurs paramétriques Josephson (JPA)** : amplification ultra-bruit
  à 20 mK
- **Quantum-classical interface** : interconnexion entre l'étage cryogénique
  (10-20 mK) et l'électronique à température ambiante
- **Cryogenic interconnects** : câbles coaxiaux, flexibles, fibres optiques
  pour la transmission d'impulsions et la lecture
- **Multiplexage fréquentiel** : lecture massive de qubits via multiplexage
  en fréquence (flux ramp, microwave readout)
- **FPGA cryogéniques** : logique reconfigurable en environnement cryogénique
- **Contrôleur sur puce** : full-stack sur puce cryogénique

### 8. Microfluidique Computationnelle

#### 8.1 Microfluidic Logic and Computing
- **Microfluidic circuits** : canaux et valves microfluidiques contrôlés pour
  le calcul
- **Logic microfluidic gates** : portes logiques basées sur l'écoulement de
  fluides/bulles
- **Fluid-based Boolean logic** : AND, OR, NOT microfluidiques par pression
- **Droplet-based computing** : gouttelettes comme bits d'information,
  microfluidique digitale
- **Electrowetting-on-dielectric (EWOD)** : déplacement de gouttelettes
  par champ électrique pour la logique
- **Microfluidic memory** : stockage de gouttelettes/bulles comme bits mémoire
- **Clock microfluidique** : horloge fluide pour circuits microfluidiques
- **Sequential logic microfluidique** : bascules, registres microfluidiques

#### 8.2 Applications
- **Laboratoires sur puce intelligents** : lab-on-chip computationnel
  pour diagnostics autonomes
- **Microfluidic sorting and routing** : tri de cellules ou molécules
  assisté par logique microfluidique
- **Chemical computing** : réactions chimiques guidées pour le calcul
- **Microfluidic oscillators** : oscillateurs pour le timing et le contrôle
- **Integrated fluidic control** : microprocesseurs fluidiques pour
  l'expérimentation automatisée
- **Bio-screening microfluidique** : criblage à haut débit assisté par
  logique microfluidique

### 9. Matériaux 2D pour l'Électronique

#### 9.1 Matériaux et Synthèse
- **Graphène** : monocouche de carbone, mobilité record, absence de bandgap
- **TMDs (Transition Metal Dichalcogenides)** : MoS₂, WS₂, WSe₂, MoSe₂ —
  semi-conducteurs 2D avec bandgap
- **hBN (nitrure de bore hexagonal)** : isolant 2D, substrat pour graphène et TMDs
- **Phosphore noir (black phosphorus)** : semi-conducteur 2D à bandgap
  ajustable, anisotropie
- **Silicène et germanène** : analogues 2D du silicium/germanium
- **MXenes** : carbures/nitrures de métaux de transition 2D
- **Antimonène, bismuthène** : matériaux 2D du groupe V
- **Hétérostructures van der Waals** : empilement de matériaux 2D par vdW
- **CVD, MBE, exfoliation mécanique** : méthodes de synthèse et dépôt
- **Grande surface et transfert** : production wafer-scale et transfert
  de films 2D

#### 9.2 Dispositifs et Applications Électroniques
- **Transistors 2D (FETs)** : TMD-FET à haute mobilité, faible SS
- **Logique 2D** : portes logiques complètes en matériaux 2D
- **Circuit intégrés 2D** : processeurs et circuits élémentaires en TMD
- **Photodétecteurs 2D** : détection de lumière de l'UV à l'IR
- **Émetteurs lumineux 2D (LED)** : émission à partir de TMDs
- **Capteurs 2D** : gaz, pression, biosenseurs à haute sensibilité
- **Flexible electronics 2D** : électronique flexible, transparente,
  pliable en matériaux 2D
- **Valleytronics** : exploitation de la vallée électronique comme
  degré de liberté dans les TMDs
- **Matériaux 2D memristifs** : memristors en hBN, MoS₂, graphène
- **Hétérostructures 2D pour la photonique** : modulateurs, détecteurs
  intégrés
- **2D pour l'interconnexion** : électrodes et interconnexions en graphène

### 10. ReRAM / PCM / STT-MRAM

#### 10.1 Resistive RAM (ReRAM / RRAM)
- **Principe de fonctionnement** : changement réversible de résistance dans
  un oxyde sous tension
- **Mécanismes** : filamentary switching, interfacial switching
- **Oxydes typiques** : HfO₂, TaOₓ, TiO₂, NiO, Al₂O₃
- **Performances** : endurance (>10¹² cycles), rétention (>10 ans à 85°C),
  vitesse (<10 ns)
- **Multi-level cell (MLC)** : stockage multi-niveaux, poids analogiques
  pour neuromorphique
- **Selector devices** : OTS (Ovonic Threshold Switch), MIS, MIEC, SOT
- **Integration 3D crossbar** : matrices 3D pour ultra-haute densité
- **Applications** : stockage de masse, mémoire de travail, compute-in-memory,
  neuromorphique
- **ReRAM biocompatible** : memristors pour implants, bio-neuromorphique

#### 10.2 Phase-Change Memory (PCM)
- **Principe** : transition entre phase amorphe (haute résistance) et
  cristalline (basse résistance) d'un chalcogénure
- **Matériaux** : GST (Ge₂Sb₂Te₅), GST-225, alliages dopés, superlattices
  interfaciales
- **Fonctionnement** : RESET (fusion + trempe → amorphe), SET (recuit → cristal),
  READ (lecture à faible tension)
- **Propriétés** : endurance (10⁶-10⁹), rétention, MLC
- **PCM orienté stockage** : Optane (Intel/Micron, discontinué), prototypes
  3D XPoint
- **PCM pour compute-in-memory** : accumulation analogique, MAC dans le
  poids en phase
- **Multi-states PCM** : niveaux de conductance multiples pour réseaux
  de neurones
- **Projected PCM** : découplage lecture/écriture pour la rétention

#### 10.3 STT-MRAM (Spin-Transfer Torque MRAM)
- **Principe** : magnétorésistance tunnel (TMR), retournement de
  l'aimantation par courant polarisé en spin
- **Structure** : MTJ (Magnetic Tunnel Junction) — couche de référence,
  barrière MgO, couche libre
- **STT switching** : retournement de l'aimantation de la couche libre
  via STT
- **Performances** : endurance quasi-infinie (>10¹⁵), vitesse (ns),
  faible consommation
- **Variantes** : in-plane MTJ, perpendicular MTJ (p-MTJ), double MTJ
- **Standalone STT-MRAM** : mémoire embarquée et cache (eMRAM)
- **Industrialisation** : Samsung, TSMC, GlobalFoundries, Everspin
- **STT-MRAM pour cache** : remplacement de SRAM/eDRAM en dernière génération
- **STT-MRAM embarquée** : eMRAM en Foundry nodes (28nm, 22nm)
- **Spin-Orbit Torque MRAM (SOT-MRAM)** : commutation plus rapide via
  effet Hall de spin
- **Voltage-Controlled Magnetic Anisotropy (VCMA-MRAM)** : commutation
  assistée par tension

### 11. Spintronique

#### 11.1 Fondements de la Spintronique
- **Spin de l'électron** : degré de liberté pour le transport et le stockage
  de l'information
- **Magnétorésistance géante (GMR)** : prix Nobel 2007 (Fert, Grünberg)
- **Magnétorésistance tunnel (TMR)** : effet tunnel magnétique dans MTJs
- **Courant polarisé en spin** : génération et injection de spin
- **Spin injection** : injection de spin depuis un ferromagnétique dans
  un semi-conducteur ou métal
- **Diffusion de spin** : longueur de diffusion, temps de relaxation
- **Effet Hall de spin et Hall de spin inverse** : conversion courant-spin
  et spin-courant
- **Effet Rashba** : couplage spin-orbite pour la manipulation de spin
- **Effet Edelstein** : génération de spin par courant dans des systèmes
  à couplage spin-orbite

#### 11.2 Dispositifs et Logique Spintronique
- **Spin valves** : structures métalliques à GMR pour capteurs et mémoire
- **Spin transistors** : transistors à spin pour logique reprogrammable
- **Spin logic devices** : portes logiques magnétiques (pNML, All-spin logic)
- **Domain wall logic** : logique à parois de domaines magnétiques
- **Skyrmions magnétiques** : textures de spin topologiques comme
  porteurs d'information
- **Current-induced domain wall motion** : déplacement de parois par
  courant pour la logique
- **Spin-wave computing** : calcul par ondes de spin (magnonique)
- **Magnonique** : logique à magnons, interféromètres à ondes de spin
- **Spin-orbit logic** : logique basée sur l'effet Hall de spin
- **Magnetic tunnel junction logic** : logique non volatile

#### 11.3 Applications Spintroniques
- **Capteurs spintroniques** : capteurs de champ magnétique, de courant,
  de position
- **Têtes de lecture HDD** : lecture magnétique à GMR/TMR
- **Spintronic oscillators** : oscillateurs à transfert de spin (STO)
  et oscillateurs à couplage spin-orbite
- **Ising machines spintroniques** : solveurs d'optimisation à oscillateurs
  couplés et skyrmions
- **Hardware security** : PUF spintroniques, TRNG (True Random Number
  Generator) à STO
- **Spintronics neural networks** : réseaux de neurones à oscillateurs
  spintroniques
- **Spintronic reservoir computing** : ordinateur à réservoir spintronique
- **Antiferromagnetic spintronics** : spintronique antiferromagnétique
  pour mémoires ultrarapides
- **Spintronic neuromorphic computing** : synapses et neurones magnétiques

### 12. Ordinateur à Réservoir (Reservoir Computing)

#### 12.1 Principes du Reservoir Computing
- **Approche** : projection non linéaire d'entrées dans un espace de haute
  dimension (le réservoir) → lecture linéaire
- **Réservoir fixe** : les poids internes du réservoir sont aléatoires et
  non entraînés
- **Entraînement uniquement de la sortie** : simple régression linéaire
  ou ridge regression
- **Echo State Property** : condition de stabilité du réservoir —
  l'état doit être une fonction des entrées passées
- **Mémoire à court terme** : capacité du réservoir à retenir l'historique
  des entrées
- **Non-linéarité** : fonction d'activation interne (tanh, sigmoid) du réservoir
- **Avantages** : entraînement très rapide (pas de retropropagation),
  adapté au matériel

#### 12.2 Implémentations Matérielles
- **Reservoir optique/photonique** : temps de réponse ultra-rapide,
  multiplexage en longueur d'onde
- **Reservoir électronique** : circuits analogiques non linéaires,
  oscillateurs couplés
- **Reservoir memristif** : réseaux de memristors comme réservoirs
  physiques
- **Reservoir spintronique** : oscillateurs à transfert de spin comme
  nœuds du réservoir
- **Reservoir à délais** : un seul nœud non linéaire + ligne à retard
  (time-multiplexed reservoir)
- **Reservoir mécanique** : systèmes mécaniques non linéaires
- **Reservoir biologique** : réseaux de neurones biologiques, colonies
  bactériennes, moisissure
- **Reservoir moléculaire** : réservoir à base de réactions chimiques

#### 12.3 Applications
- **Prédiction de séries temporelles** : chaotiques (Lorenz, Mackey-Glass),
  financières, météorologiques
- **Reconnaissance de parole** : classification de signaux audio en temps réel
- **Reconnaissance de chiffres écrits** : MNIST, classification de motifs
  temporels
- **Contrôle robotique** : contrôle en boucle fermée, apprentissage
  de séquences motrices
- **Communication non linéaire** : égalisation de canaux, détection
  non linéaire
- **Traitement de signaux temps réel** : filtrage adaptatif, prédiction
- **Diagnostic médical** : classification d'EEG, ECG
- **Reservoir computing pour l'edge** : inférence à très faible consommation
- **Reservoir computing quantique** : réservoirs quantiques à NISQ

### 13. Systèmes Auto-Organisants et Matériel Biologique

#### 13.1 Systèmes Auto-Organisés
- **Auto-organisation en informatique** : émergence de comportements
  globaux à partir de règles locales
- **Algorithmes distribués auto-organisés** : consensus, synchronisation,
  partitionnement sans coordinateur central
- **Intelligence en essaim (swarm intelligence)** : colonies de fourmis,
  bancs de poissons, essaims de drones — résolution distribuée de problèmes
- **Cellular automata (automates cellulaires)** : Jeu de la Vie (Conway),
  Rule 110 (Turing-complet), automates à gaz
- **Self-assembly computationnel** : assemblage de nanostructures ADN
  et moléculaires pour le calcul
- **Self-* systems** : self-configuration, self-healing, self-optimization,
  self-protection en systèmes distribués
- **Morphogenesis computationnelle** : calcul par développement et
  différenciation cellulaire simulée
- **Reconfigurable computing** : FPGAs auto-reconfigurables, arrays
  de portes adaptatives
- **Bio-inspired self-organization** : algorithmes inspirés du
  comportement collectif biologique

#### 13.2 Matériel Biologique et Systèmes Hybrides
- **Systèmes hybrides bio-numériques** : intégration de composants
  biologiques dans des circuits électroniques
- **Neurones sur puce (MEA)** : réseaux de neurones biologiques sur
  Multi-Electrode Arrays pour le calcul
- **Cultured neural networks** : calcul par réseaux de neurones
  cultivés in vitro
- **Brain-on-chip (organoïdes cérébraux)** : mini-cerveaux pour
  l'informatique neuromorphique biologique
- **Cyborg computing** : hybrides biologie-électronique
- **Bacterial computing en réseau** : biofilms computationnels
- **Slime mold computing** : calcul par Physarum polycephalum
- **Computational fungi** : calcul distribué via réseaux fongiques
- **Swarm robotics bio-hybride** : robots contrôlés par des signaux
  biologiques
- **Living sensors et senseurs auto-réparants** : biocapteurs
  intégrés dans le matériel

## Veille Organisationnelle et Institutionnelle

### Programme DARPA

Le DARPA finance des programmes transformateurs en technologies émergentes :

- **DARPA IMPAQT** (Intelligent Memory and Processing Accelerating
  Quantum Technologies) : optimisation des systèmes de contrôle quantiques
- **DARPA OQN** (Optimization with Noisy Qubits) : algorithmes NISQ
- **DARPA DRINQS** (Distributed Quantum Computing) : réseaux de
  processeurs quantiques
- **DARPA QBI** (Quantum Benchmarking Initiative) : benchmarking et
  standardisation des performances quantiques
- **DARPA UHPC, ERI** : programmes en architecture au-delà de von Neumann
- **DARPA UPSIDE** (Unconventional Processing of Signals for
  Intelligent Data Exploitation) : traitement de signaux non conventionnel
- **DARPA FRANC** (Foundations of Neural Computing) : fondements du
  calcul neuromorphique
- **DARPA N-ZERO** : calcul quasi-consommation nulle pour l'IoT
  et les capteurs
- **DARPA PhENOMS** : photonique pour le calcul à haute performance
- **DARPA MTO** (Microsystems Technology Office) : programmes en
  spintronique, 2D materials, memristors
- **DARPA MMEC** : calcul en mémoire et au-delà de von Neumann
- **DARPA QLAM** : Quantum Logic and Algorithms for Materials
- **DARPA Imagining Practical Quantum Computing** : feuille de route
  vers le calcul quantique pratique

### IRDS Roadmap

L'IRDS (International Roadmap for Devices and Systems) définit la
feuille de route technologique mondiale remplaçant l'ITRS :

- **IRDS More Moore** : scaling des technologies CMOS (FinFET, GAA FET,
  CFET, 2D FET)
- **IRDS Beyond CMOS** : technologies émergentes post-CMOS — électronique
  à spin, à matériaux 2D, neuromorphique, computationnelle non conventionnelle
- **IRDS More than Moore** : hétéro-intégration, capteurs, MEMS, RF,
  technologies de puissance, microfluidique, bioélectronique
- **IRDS Emerging Research Devices** : ReRAM, PCM, STT-MRAM, FeFET,
  à tube de carbone, interconnexions optiques, memristors
- **IRDS Emerging Research Materials** : matériaux 2D, TMD, hBN,
  multiferroïques, matériaux à changement de phase, oxydes à
  lacunes d'oxygène
- **IRDS Systems and Architectures** : architectures non von Neumann,
  PIM, CIM, architecture neuromorphique
- **IRDS Quantum Information** : roadmap pour les technologies
  d'information quantique — qubits, correction d'erreur, plateformes
- **Publish years** : rapports bisannuels — 2023, 2025, 2027
  (dernier : 2024 White Papers)

### NIST — National Institute of Standards and Technology

Le NIST joue un rôle central dans la standardisation et la métrologie
des technologies émergentes :

- **NIST Quantum Information** : métrologie des qubits, benchmarking
  des portes, standardisation des algorithmes
- **NIST Post-Quantum Cryptography (PQC)** : sélection et standardisation
  des algorithmes cryptographiques résistants aux ordinateurs quantiques
  (CRYSTALS-Kyber/ML-KEM, CRYSTALS-Dilithium/ML-DSA, SPHINCS+/SLH-DSA, FALCON/FN-DSA)
- **NIST AI Safety Institute** : sécurité de l'IA, mais aussi évaluation
  des technologies neuromorphiques et non conventionnelles
- **NIST CHIPS R&D** : métrologie des matériaux 2D, mesure de la
  fiabilité des mémoires émergentes
- **NIST Quantum Economic Development Consortium (QED-C)** : consortium
  industriel pour l'économie quantique
- **NIST Nanotechnology** : mesures et standards pour les nanomatériaux
  (matériaux 2D, nanotubes, nanoparticules)
- **NIST On a Chip** : standardisation des laboratoires sur puce
- **NIST Standards** : IEEE 1650 (Standard for ReRAM), normes
  sur les technologies de mémoire, métrologie TMR pour spintronique

## Stratégie de Veille

### Flux arXiv
- **Primaire** : `/list/cs.ET/recent` — noyau des technologies émergentes
- **Cross-listés clés** :
  - `quant-ph` — calcul quantique, correction d'erreur, algorithmes
  - `physics.app-ph` — physique appliquée (dispositifs, matériaux)
  - `physics.optics` — optique, photonique, dispositifs
  - `cond-mat.mes-hall` — mésoscopique, spintronique, 2D, memristors
  - `cond-mat.mtrl-sci` — science des matériaux
  - `cs.AR` — architecture matérielle, PIM, NDP
  - `cs.NE` — réseaux de neurones, réservoir computing
  - `q-bio.MN` — biologie moléculaire, ADN computing
  - `eess.SP` — traitement du signal pour capteurs et circuits
  - `physics.bio-ph` — biophysique pour biocomputing
  - `nlin.AO` — systèmes adaptatifs et auto-organisation

### Mots-clés de veille par domaine
- **Neuromorphique** : "neuromorphic computing", "spiking neural network",
  "STDP", "Loihi", "memristive crossbar", "event-driven"
- **Quantique** : "quantum computing", "NISQ", "error correction",
  "surface code", "VQE", "QAOA", "fault-tolerant", "transmon", "quantum advantage"
- **ADN/Bio** : "DNA computing", "DNA storage", "DNA origami",
  "molecular computing", "biocomputing", "synthetic biology computing"
- **Optique** : "optical computing", "photonic neural network",
  "silicon photonics", "diffractive network", "optical interconnect"
- **Post-von Neumann** : "in-memory computing", "near-data processing",
  "processing-in-memory", "compute-in-memory", "non-von Neumann"
- **Memristors** : "memristor", "RRAM", "crossbar array",
  "analog synapse", "neuromorphic memristor"
- **Matériaux 2D** : "2D materials", "graphene", "MoS2",
  "transition metal dichalcogenide", "van der Waals heterostructure"
- **Spintronique** : "spintronics", "STT-MRAM", "skyrmion",
  "magnonics", "spin-orbit torque", "magnetic tunnel junction"
- **Réservoir** : "reservoir computing", "echo state network",
  "physical reservoir", "photonic reservoir", "spintronic reservoir"
- **Cryogénie** : "cryogenic computing", "cryo-CMOS",
  "single flux quantum", "superconducting logic", "AQFP"

### Conférences et publications clés
- **IEDM** (International Electron Devices Meeting) — dispositifs et
  technologies mémoires
- **VLSI Symposium** — circuits et technologies
- **ISSCC** (International Solid-State Circuits Conference) — circuits
  intégrés émergents
- **NANOARCH** (IEEE International Symposium on Nanoscale Architectures)
- **ICRC** (IEEE International Conference on Rebooting Computing)
- **IEEE NANO** — nanotechnologies
- **AICAS** (IEEE International Conference on Artificial Intelligence
  Circuits and Systems) — circuits neuromorphiques et IA
- **QEC** (Quantum Error Correction) — correction d'erreur quantique
- **IEEE Quantum Week** — conférence annuelle IEEE sur le calcul quantique
- **DNA Computing and Molecular Programming** (DNA conference)
- **SPIE Photonics West** — photonique
- **MRS Fall/Spring** — matériaux émergents
- **INTERMAG / MMM** — magnétisme, spintronique
- **Nature Electronics**, **Nature Nanotechnology**, **Nature Photonics**,
  **Nature Computational Science**, **Nature Physics**
- **Science Advances**, **PNAS** — publications généralistes
- **IEEE Transactions on Electron Devices**, **IEEE Journal
  on Exploratory Solid-State Computational Devices and Circuits**
- **Advanced Functional Materials**, **Advanced Materials**
- **PRX Quantum**, **Quantum**, **npj Quantum Information**
- **ACS Nano**, **Nano Letters**, **2D Materials**
- **Neuromorphic Computing and Engineering** (IOP)

### Acteurs industriels et académiques clés
- **IBM Research** : calcul quantique (cond. supra), neuromorphique
  (TrueNorth, NorthPole)
- **Intel Labs** : neuromorphique (Loihi 1/2/3), calcul quantique
  (Tunnel Falls), cryo-CMOS
- **Google Quantum AI** : calcul quantique (Sycamore, Willow),
  correction d'erreur
- **Microsoft Azure Quantum** : qubits topologiques (Majorana),
  atomes neutres, IonQ
- **IMEC** : 2D materials, neuromorphic devices, ReRAM, cryo-CMOS,
  IRDS roadmap contributor
- **CEA-Leti** : circuits neuromorphiques, ReRAM, technologies
  quantiques, microfluidique
- **MIT (EECS, Media Lab)** : ADN computing, neuromorphique,
  calcul optique, matériaux 2D, spintronique
- **Stanford (Nanoelectronics Group)** : matériaux 2D, memristors,
  circuits neuromorphiques, PIM
- **ETH Zurich (IIS, D-MAVT)** : au-delà de von Neumann,
  neuromorphique, microfluidique computationnelle
- **University of Chicago (PME)** : spintronique, memristors,
  ordinateur à réservoir
- **Purdue University** : matériaux 2D, spintronique, logique au-delà
  de CMOS
- **Tokyo Institute of Technology** : AQFP (supraconducteur logique),
  matériaux 2D, spintronique
- **Tohoku University (CSIS, RIEC)** : spintronique, STT-MRAM,
  SOT-MRAM, VCMA
- **LMU Munich / TU Munich** : ADN computing, biocomputing
- **Caltech** : ADN computing, DNA origami, nanophotonique
- **Harvard** : atomes neutres (QuEra), matériaux 2D, biologie
  synthétique computationnelle

## Articles Représentatifs Récents (Mi-2026)

1. **Willow: A 105-qubit superconducting quantum processor with error
   correction below threshold** — Google Quantum AI (Nature, 2025)
2. **Loihi 3: Advances in Neuromorphic Computing Chips** — Intel Labs
3. **Large-scale optical neural network based on frequency combs
   and microresonators** — Nature Photonics, 2025
4. **DNA storage with random access and in-storage computation** —
   Nature Nanotechnology, 2025
5. **ReRAM-based analog in-memory computing for transformer
   acceleration** — IEDM 2025
6. **SOT-MRAM for last-level cache: 22nm demonstrator with
   <1ns write** — VLSI Symposium, 2025
7. **Neuromorphic computing with 2D materials: MoS2 memristive
   crossbar arrays** — Nature Electronics, 2025
8. **Photonic reservoir computing for real-time chaotic time-series
   prediction** — Optica, 2025
9. **Near-data processing for graph analytics: 3D-stacked
   HBM-PIM evaluation** — ISCA, 2025
10. **Cryo-CMOS controller for 100+ qubits at 4K** — ISSCC, 2025
11. **Programmable DNA origami circuits for molecular computation** —
    Nature Computational Science, 2025
12. **Physical reservoir computing with spin-torque nano-oscillators** —
    Nature Communications, 2025
13. **Non-von Neumann architectures: A comprehensive survey
    of processing-in-memory** — ACM Computing Surveys, 2025
14. **Quantum error correction below surface code threshold** —
    Nature, 2025 (Harvard/QuEra neutral atoms)
15. **Microfluidic logic arrays for automated laboratory-on-chip
    computation** — Lab on a Chip, 2025
16. **Self-organizing bio-hybrid computing systems: slime mold
    and fungal networks for distributed computation** —
    Science Advances, 2025
17. **IRDS 2025 Update: Beyond CMOS Devices and Emerging
    Research Materials** — IRDS White Papers, 2025
18. **Stochastic computing with spin-orbit torque nanodevices
    for probabilistic inference** — Nature Nanotechnology, 2025
19. **Magnonic reservoir computing for speech recognition** —
    Nature Communications, 2025
20. **Skyrmion-based artificial synapses for neuromorphic
    computing** — Advanced Materials, 2025