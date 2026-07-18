---
name: chemical-engineering-ai
description: "Compétence niveau ingénieur/docteur en génie chimique computationnel. Couvre CFD réactif, optimisation de procédés, génie des réactions, séparation ML, contrôle de procédés, PSE, scale-up, safety analysis, et IA pour la simulation de procédés chimiques."
---

# Génie Chimique Computationnel et IA

## Présentation
Cette skill couvre l'application de l'intelligence artificielle, du machine learning et des méthodes computationnelles avancées au génie chimique. Elle s'adresse aux chercheurs et ingénieurs travaillant sur la simulation de procédés, la CFD réactive, le contrôle avancé, l'optimisation des procédés chimiques, la sécurité industrielle et le scale-up assisté par IA.

## Simulation de Procédés
- **Aspen Plus / Aspen HYSYS** : Simulation de procédés industriels, modélisation thermodynamique (NRTL, UNIQUAC, Peng-Robinson), colonnes de distillation, réacteurs, échangeurs, séparation
- **gPROMS** : Simulation orientée équation, modélisation de procédés dynamiques, optimisation multidisciplinaire, intégration avec models de procédés
- **DWSIM / CHEMCAD** : Simulateurs open-source et commerciaux, validation de modèles, analyse de sensibilité, flowsheet integration
- **Flowsheet Optimization ML** : Optimisation de flowsheet par apprentissage automatique, optimisation de procédés chimiques, surrogate modeling, optimisation multi-objectifs, reinforcement learning pour procédés batch
- **Thermodynamics ML** : Prédiction de propriétés thermodynamiques par ML, modèles UNIFAC améliorés par IA, estimation de paramètres d'équation d'état, prédiction de données de phase

## CFD pour Génie Chimique
- **OpenFOAM Réactif** : Simulation de réacteurs chimiques, écoulements réactifs, modèles de combustion, cinétique chimique détaillée, flames, réacteurs tubulaires
- **Multiphase Flow** : Écoulements gaz-liquide, liquide-liquide, solide-liquide, modèles Euler-Euler, Euler-Lagrange, VOF (Volume of Fluid), DPM (Discrete Phase Model)
- **Packed Bed** : Simulation de lits fixes, écoulement à travers des milieux poreux, distribution de température, catalyse hétérogène, réacteurs à lit fixe avec CFD
- **Stirred Tank** : Réacteurs agités, hydrodynamique, mélange, distribution de taille de gouttes, optimisation de géométrie d'agitateur, power consumption, suspension de solides
- **Mixing Optimization** : Optimisation du mélange par ML, modèles de micromélange, macromélange, temps de mélange, mélange réactif, intensification du mélange

## Contrôle de Procédés
- **MPC (Model Predictive Control)** : Commande prédictive multivariable, DMC, QDMC, MPC non-linéaire, MPC robuste, application aux colonnes de distillation, réacteurs
- **PID Auto-Tuning** : Réglage automatique de PID, méthodes de Ziegler-Nichols, optimisation par IA, adaptation en ligne, IMC-based tuning, Lambda tuning
- **Plant-Wide Control** : Contrôle intégré d'usine, décomposition de procédés, contrôle de bilan matière/énergie, inventory control, régulation de qualité
- **Alarm Management** : Gestion des alarmes, rationalisation, flood analysis, alarm prioritization, nuisance alarm reduction, ISA-18.2, EEMUA-191
- **Fault Detection / FDIFormer** : Détection et diagnostic de défauts, analyse de composantes principales (PCA), PLS, modèles de détection profonde, FDIFormer (transformers pour détection de défauts), isolation de défauts, statistical process control (SPC)

## Optimisation de Procédés
- **Process Integration** : Intégration de procédés, analyse pinch, optimisation des réseaux d'échangeurs de chaleur (HEN), integration massique, water pinch
- **Heat Exchanger Networks** : Synthèse et optimisation de HEN, modèles MILP/MINLP, optimisation par gradient, metaheuristiques, intégration de pompes à chaleur, retrofit
- **Distillation Optimization ML** : Optimisation de colonnes de distillation, séquences de distillation, intensification, colonnes divisées (DWC), distillation réactive, optimisation par ML
- **Reactive Distillation** : Distillation réactive, modélisation, optimisation, design, catalyse, couplage réaction-séparation, intensification de procédés

## Sécurité des Procédés
- **HAZOP Automation** : Automatisation de l'analyse HAZOP, extraction de scénarios par NLP, analyse de risques assistée par IA, HAZOP-LOPA intégré
- **SIL (Safety Integrity Level)** : Détermination de SIL, IEC 61508/61511, analyse de fiabilité, probabilité de défaillance, architectures redondantes
- **Layer of Protection Analysis (LOPA)** : Analyse de couches de protection, calcul de réduction de risque, quantification de probabilité, LOPA automatisé
- **Consequence Modeling** : Modélisation des conséquences, dispersion de gaz, modèles d'explosion (TNT, TNO, Baker-Strehlow), incendie de pool, jet fire, BLEVE, analyse de risques quantifiée (QRA)

## Scale-up et Intensification
- **Scale-up ML** : Scale-up de procédés chimiques par ML, facteurs de scale-up, modèles de similarité, corrélation de données pilote-industrie, incertitude de scale-up
- **Microreactors** : Microréacteurs, génie chimique microfluidique, intensification du transfert de chaleur/matière, scale-out, numbering-up, synthèse en continu
- **Process Intensification** : Intensification de procédés, réacteurs multifonctionnels, échangeurs-réacteurs, champs ultrasoniques, microndes, plasma, sonochimie
- **Continuous Manufacturing** : Fabrication continue de produits pharmaceutiques/chimiques, PAT (Process Analytical Technology), QbD (Quality by Design), modélisation de procédés continus, contrôle de qualité en continu

## Catégories arXiv
- physics.chem-ph (Chemical Physics), cs.CE (Computational Engineering, Finance, and Science), cs.LG (Machine Learning), cs.AI (Artificial Intelligence), eess.SY (Systems and Control)

## Références Clés
- Aspen Plus / HYSYS Documentation
- OpenFOAM User Guide, SU2 Documentation
- IEC 61508 / IEC 61511 Functional Safety Standards
- ISA-18.2 Alarm Management Standard
- Seider et al., "Product and Process Design Principles"
- Turton et al., "Analysis, Synthesis and Design of Chemical Processes"
- Chemical Engineering Science, AIChE Journal, Computers & Chemical Engineering
- Journal of Loss Prevention in the Process Industries