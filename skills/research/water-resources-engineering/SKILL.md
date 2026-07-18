---
name: water-resources-engineering
description: "Compétence niveau ingénieur/docteur en ressources en eau et hydrologie computationnelles. Couvre la modélisation hydrologique, la prévision des crues, les eaux souterraines, la gestion des bassins versants, les systèmes d'approvisionnement en eau, l'assainissement, la qualité de l'eau, l'hydraulique fluviale, le dessalement, l'irrigation de précision, et les water-energy-food nexus."
---

# Ressources en Eau et Hydrologie Computationnelles

## Présentation
Cette skill couvre l'application de l'intelligence artificielle, du machine learning et des méthodes computationnelles à l'hydrologie et à la gestion des ressources en eau. Elle s'adresse aux chercheurs et ingénieurs travaillant sur la modélisation hydrologique, la prévision des crues, les eaux souterraines, la qualité de l'eau, les systèmes d'approvisionnement et d'assainissement, l'irrigation de précision, et le nexus eau-énergie-alimentation.

## Modélisation Hydrologique
- **Rainfall-Runoff** : Modélisation pluie-débit, transformation pluie-débit, hydrogramme, modèles conceptuels, modèles à base physique, modèles empiriques, ML pour la modélisation, Random Forest, LSTM, GRU
- **SWAT** : Soil and Water Assessment Tool, modélisation de bassin versant, hydrologie, qualité de l'eau, sédiments, nutriments, pesticides, SWAT-CUP, calibration, validation, paramétrisation
- **HEC-HMS** : Hydrologic Modeling System, modélisation des précipitations, pertes, transformation, routage, calibration, optimisation, modèles de bassin, hydrogramme unitaire
- **MIKE SHE** : MIKE SHE (DHI), modélisation distribuée, écoulement de surface, zone non-saturée, zone saturée, interaction rivière-aquifère, évapotranspiration, irrigation, modèles intégrés
- **HBV** : Modèle HBV (Hydrologiska Byråns Vattenbalansavdelning), modèle conceptuel, zones d'altitude, snow routine, soil moisture routine, response function, modèles semi-distribués
- **Distributed Hydrological Modeling** : Modélisation hydrologique distribuée, maillage, topographie, pente, direction d'écoulement, accumulation, réseau de drainage, modèles physiques, modèles spatialisés
- **Data-Driven Hydrology** : Hydrologie basée sur les données, modèles de séries temporelles, LSTM, GRU, Transformers, modèles hybrides physique-ML, apprentissage profond pour l'hydrologie, NeuralHydrology

## Crues et Risques Hydrologiques
- **Flood Forecasting** : Prévision des crues, modèles de prévision, prévision d'ensemble, prévision probabilitée, modèles ML, réseaux de neurones, modèles hybrides, prévision à court terme, prévision saisonnière
- **Early Warning** : Systèmes d'alerte précoce, seuils de crue, évaluation de risque, alertes, dissemination, community-based early warning, prévision en temps réel, EFAS, GloFAS, NWS
- **HEC-RAS** : River Analysis System, modélisation hydraulique 1D/2D, écoulement permanent/non-permanent, analyse de crue, cartographie d'inondation, ponts, ouvrages, modèles de rupture de barrage
- **Inundation Mapping** : Cartographie d'inondation, zones inondables, profondeur d'eau, étendue, modèles de terrain, modèles hydrodynamiques, modèles ML, random forest, LSTM, U-Net pour l'inondation
- **Urban Flooding** : Inondation urbaine, drainage urbain, ruissellement urbain, modèles 1D/2D, SWMM, MIKE URBAN, pluvial flooding, surcharge, modèles ML pour l'urban flood
- **Pluvial Flood ML** : Inondation pluviale par ML, modèles de prévision de pluie, nowcasting, radar, modèles ML pour l'intensité, modèles de submersion, urban pluvial flood prediction
- **AgroFlux** : AgroFlux — modèles de flux agro-hydrologiques, intégration agriculture-hydrologie, bilan hydrique agricole, flux de nutriments, modèles de pollution diffuse, AI pour le nexus agriculture-eau

## Eaux Souterraines
- **Groundwater Modeling** : Modélisation des eaux souterraines, équation de Darcy, équation de Boussinesq, écoulement en milieu poreux, modèles 2D/3D, modèles déterministes, stochastiques
- **MODFLOW** : MODFLOW (USGS), modèle aux différences finies, aquifères, couches, stress packages, boundary conditions, modélisation de transport, MT3DMS, SEAWAT, calibration PEST
- **FEFLOW** : FEFLOW (DHI), éléments finis, écoulement saturé/non-saturé, transport de masse, transport de chaleur, densité variable, modèles 3D, interface d'eau salée
- **Transport** : Transport de solutés, advection, dispersion, diffusion, réaction, adsorption, dégradation, transport réactif, modèles de transport, MT3D, RT3D, PHT3D
- **Contamination** : Contamination des eaux souterraines, panaches, sources de contamination, nitrate, pesticides, métaux lourds, solvants chlorés, MTBE, modèles de contamination, PEST, MCMC
- **Aquifer Recharge** : Recharge des aquifères, recharge naturelle, MAR (Managed Aquifer Recharge), infiltration, bassins d'infiltration, puits d'injection, ASR (Aquifer Storage and Recovery), modèles ML pour la recharge
- **GW-SW Interaction** : Interaction eaux souterraines-eaux de surface, échange nappe-rivière, zones hyporhéiques, upwelling, downwelling, modèles couplés, GSFLOW, MODFLOW-SWA, modèles ML

## Qualité de l'Eau
- **Water Quality Modeling** : Modélisation de la qualité de l'eau, paramètres (DO, BOD, COD, TSS, N, P), modèles de qualité, modèles d'eutrophisation, modèles de bilan de masse, modèles cinétiques
- **WASP** : Water Quality Analysis Simulation Program (USEPA), modélisation de qualité de l'eau, eutrophisation, toxiques, sédiments, modèles 1D/2D, calibration, WASP8
- **QUAL2K** : QUAL2K (USEPA), modèle de qualité de l'eau de rivière, bilan d'oxygène, nutriments, algues, CBOD, nitrification, photosynthèse, respiration, réaération, modèles de rivière
- **Pollution Sources ML** : Sources de pollution par ML, modèles de sources, identification de sources, apportionment, PMF (Positive Matrix Factorization), PCA, modèles ML, régression
- **Eutrophication** : Eutrophisation, nutriments, azote, phosphore, algues, blooms, cyanobactéries, modèles d'eutrophisation, indices trophiques, modèles ML pour la prédiction de blooms, chlorophyll-a
- **Sediment Transport** : Transport de sédiments, érosion, dépôt, charriage, suspension, concentration, modèles de sédiments, HEC-RAS sediment, modèles ML, Universal Soil Loss Equation (USLE)
- **Turbidity** : Turbidité, matière en suspension, néphélométrie, turbidité en rivière, modèles de turbidité, modèles ML, prédiction de turbidité, qualité de l'eau potable, traitement

## Approvisionnement et Assainissement
- **Water Distribution Network** : Réseaux de distribution d'eau, modélisation hydraulique, analyse de réseaux, demande, pression, débit, réservoirs, pompes, vannes, modèles de calibration
- **EPANET** : EPANET (USEPA), modélisation de réseaux de distribution, analyse hydraulique, qualité de l'eau, âge de l'eau, modèles de pression, simulation de chlore, modèle de consommation
- **Leakage Detection** : Détection de fuites, acoustic, corrélation, FFT, modèles ML, smart water networks, district metered areas (DMA), minimum night flow, leak localization, AI pour la détection
- **Pressure Management** : Gestion de pression, PRV (Pressure Reducing Valves), réduction de pression, contrôle de pression, modèles d'optimisation, ML pour la gestion, smart valves
- **Wastewater Treatment ML** : Traitement des eaux usées par ML, modélisation de procédés, boues activées, MBR, SBR, UASB, optimisation de l'aération, dosage, prédiction de qualité effluent, soft sensors
- **UV-AOP** : Advanced Oxidation Processes UV, UV/H2O2, UV/Cl2, UV/O3, photo-Fenton, modèles de dégradation, cinétique UV-AOP, optimisation, ML pour la prédiction de performance, UV-LED

## Irrigation et Agriculture
- **Precision Irrigation** : Irrigation de précision, irrigation localisée, goutte-à-goutte, aspersion, pivot, modèles de besoins en eau, ML pour l'optimisation, smart irrigation, scheduling
- **Soil Moisture ML** : Humidité du sol par ML, capteurs d'humidité, modèles de bilan hydrique, modèles de rétention, estimation spatiale, modèles ML, SMAP, SMOS, remote sensing soil moisture, satellites
- **Evapotranspiration** : Évapotranspiration, ET de référence (FAO-56 Penman-Monteith), ET de culture, modèles de ET, estimation par ML, modèles de bilan énergétique, eddy covariance, lysimètres
- **Crop Water Requirement** : Besoins en eau des cultures, coefficients culturaux (Kc), stades de croissance, modèles de demande, ML pour l'estimation, AquaCrop, DSSAT, CropWat, optimisation
- **Deficit Irrigation** : Irrigation déficitaire, stress hydrique contrôlé, régulation de stress, optimisation de l'irrigation, modèles de rendement, modèles ML, deficit irrigation strategies
- **Sensor Network** : Réseaux de capteurs, IoT pour l'irrigation, stations météorologiques, capteurs de sol, capteurs de plantes, communication LoRaWAN, modèles ML edge, cloud, smart farming

## Nexus Eau-Énergie-Alimentation (Water-Energy-Food Nexus)
- **Integrated Modeling** : Modélisation intégrée, systèmes couplés, WEF nexus, modèles d'optimisation, modèles de simulation, modèles de dynamique des systèmes, modèle d'équilibre général
- **System Dynamics** : Dynamique des systèmes, boucles de rétroaction, stocks, flux, modèles de causalité, modèles de simulation, Vensim, Stella, modèles WEF nexus, scénarios
- **Trade-off Analysis** : Analyse de compromis, optimisation multi-objectifs, front de Pareto, trade-offs WEF, analyse de sensibilité, modèles ML pour les compromis, analyse de décision multi-critères
- **Resource Optimization** : Optimisation des ressources, allocation eau-énergie, optimisation de l'irrigation, pompage, dessalement, énergie hydraulique, modèles ML, optimisation stochastique
- **Climate Adaptation** : Adaptation au changement climatique, scénarios climatiques, modèles d'impact, résilience, adaptation des infrastructures, gestion de la demande, stratégies d'adaptation ML

## Catégories arXiv
- physics.geo-ph (Geophysics), stat.AP (Statistics Applications), cs.LG (Machine Learning), cs.AI (Artificial Intelligence), eess.SY (Systems and Control), math.OC (Optimization and Control)

## Articles Clés
- **AgroFlux** : Modèles de flux agro-hydrologiques pour l'évaluation des impacts agricoles et environnementaux à l'échelle du bassin versant
- **UNCASExt** : Uncertainty-based Case Extraction for water quality modeling — extraction de cas basée sur l'incertitude pour la modélisation de la qualité de l'eau

## Références Clés
- Chow, Maidment, Mays (1988) — "Applied Hydrology"
- Anderson, Woessner, Hunt (2015) — "Applied Groundwater Modeling"
- Chapra (1997) — "Surface Water-Quality Modeling"
- USGS MODFLOW Documentation, SWAT Documentation
- Journal of Hydrology, Water Resources Research, Hydrology and Earth System Sciences
- Journal of Hydrologic Engineering, Hydrological Processes
- Water Research, Science of the Total Environment, Environmental Modelling & Software
- Irrigation Science, Agricultural Water Management, Journal of Water Resources Planning and Management