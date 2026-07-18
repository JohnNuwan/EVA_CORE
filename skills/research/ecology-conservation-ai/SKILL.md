---
name: ecology-conservation-ai
description: "Compétence niveau ingénieur/docteur en écologie et biologie de la conservation computationnelles. Couvre les modèles de distribution d'espèces SDM, l'écologie des communautés ML, la télédétection pour la conservation, le suivi de la biodiversité, l'écologie du paysage, la biologie des invasions, le camera trapping ML, l'écologie acoustique, et le animal tracking."
---

# Écologie et Biologie de la Conservation Computationnelles

## Présentation
Cette skill couvre l'application de l'intelligence artificielle, du machine learning et des méthodes computationnelles à l'écologie et à la biologie de la conservation. Elle s'adresse aux chercheurs et ingénieurs travaillant sur la modélisation de la distribution des espèces, le suivi de la biodiversité, la télédétection environnementale, l'écologie acoustique, le tracking animalier et la planification de la conservation.

## Modèles de Distribution d'Espèces (SDM)
- **MaxEnt** : Maximum Entropy Modeling, modélisation de niche écologique, présence-only, variables environnementales, sélection de features, régularisation, réponse aux variables
- **BIOCLIM** : Modèle bioclimatique, enveloppe climatique, modèles de niche, BIOCLIM variables, seuils de percentile, modèles de bioclimat, classification climatique
- **SDM ML** : Modèles de distribution par ML, Random Forest, Boosted Regression Trees (BRT), Artificial Neural Networks (ANN), Deep Learning pour SDM, SVM, ensemble models
- **Species Distribution** : Distribution d'espèces sous changement climatique, projection de niche, évaluation de modèle (AUC, TSS, Kappa), évaluation de transfert, parametrization de modèles
- **Climate Envelope / Niche Modeling** : Enveloppe climatique, modélisation de niche écologique, axes de niche, hypervolume, niche Grinnellienne, niche Eltonienne, chevauchement de niche
- **Range Shifts** : Déplacements d'aires de répartition, migration assistée, modélisation de dispersion, connectivité, barrières, corridors climatiques, climate velocity

## Biodiversité et Communautés
- **Alpha/Beta Diversity** : Diversité alpha (Shannon, Simpson, Chao1), diversité beta (Bray-Curtis, Jaccard, UniFrac), partition de diversité, rarefaction, Hill numbers
- **Community Ecology ML** : Écologie des communautés par ML, modèles de réseaux d'espèces, modèles de coexistence, prédiction de composition, joint species distribution models (JSDM)
- **Ordination** : Analyse multivariée, NMDS (Non-Metric Multidimensional Scaling), PCA, CA, DCA, RDA, CCA, dbRDA, analyse de gradient
- **NMDS** : Métrique de dissimilarité, stress, interprétation d'axes, permutation tests, envfit, vecteurs de variables environnementales, graphes de contrainte
- **Gradient Analysis** : Analyse de gradients environnementaux, modèles de réponse, courbes de réponse unimodale, GLM, GAM, quantile regression, gradient forest
- **Phylogenetics** : Phylogénie computationnelle, maximum likelihood, Bayesian inference, diversification, phylodiversity, PD (Phylogenetic Diversity), phylobetadiversity, nettoyage phylogénétique

## Télédétection pour la Conservation
- **Land Cover Classification** : Classification de l'occupation du sol, Random Forest, CNN, U-Net, DeepLab, Sentinel-2, Landsat, classification supervisée/non-supervisée
- **Deforestation Detection** : Détection de déforestation, change detection, time series analysis, LandTrendr, BFAST, CCDC, Global Forest Watch, PRODES, DETER
- **Fire Scar Mapping** : Cartographie des cicatrices de brûlis, indices de brûlis (NBR, dNBR), sévérité de feu, MODIS, VIIRS, active fire detection, burned area mapping
- **Habitat Fragmentation** : Fragmentation d'habitat, métriques de paysage, patch analysis, connectivité, edge effects, modèles de percolation, FRAGSTATS, Guidos
- **NDVI Time Series** : Séries temporelles NDVI, EVI, LAI, phénologie, détection de tendances, MODIS, AVHRR, Sentinel, Landsat, anomalies, greenness, productivité primaire

## Camera Trapping et Bioacoustique
- **Animal Identification ML** : Identification d'espèces par caméra, classification d'images, détection d'animaux, comptage, MegaDetector, CameraTrapDetectoR, MLWIC, Animal Identifier
- **MegaDetector** : Détection d'animaux, personnes, véhicules dans les images de camera traps, modèle YOLO-based, TensorFlow, AI for camera trap, triage automatisé, empty image filtering
- **Acoustic Classification** : Classification acoustique, BirdNET, Merlin, arbimon, identify species, bioacoustic indices, spectrogram classification, CNN-based, audio event detection
- **Eco-acoustics** : Éco-acoustique, paysages sonores, acoustic indices (ACI, ADI, NDSI, H), soundscape ecology, monitoring acoustique passif, ecoacoustic events
- **Passive Acoustic Monitoring (PAM)** : Monitoring acoustique passif, déploiement de capteurs, analyse de longues séquences, détection d'espèces rares, vocalizations, echolocation, AIS (Acoustic Indices)

## Animal Tracking (GPS Telemetry)
- **GPS Telemetry** : Télémétrie GPS, colliers GPS, tags, UHF, Argos, GSM, Iridium, ICARUS, accuracy, fix rate, acquisition scheduling
- **Movement Ecology ML** : Écologie du mouvement par ML, modèles de mouvement, random walk, Lévy walk, correlated random walk, ML pour classification de comportement
- **Step Selection** : Step Selection Functions (SSF), resource selection, integrated step selection (iSSF), habitat selection, movement-based models, availability domain
- **Home Range** : Home range, kernel density estimation (KDE), minimum convex polygon (MCP), autocorrelated kernel density (AKDE), Brownian bridge, T-LoCoH
- **Migration Patterns** : Modèles de migration, routes migratoires, stopover sites, timing, connectivité migratoire, dynamic Brownian bridge, Net Squared Displacement (NSD), phenology

## Conservation Planning
- **Marxan** : Logiciel de planification systématique de la conservation, optimisation de sélection de sites, simulated annealing, boundary length modifier, cost penalties, BLM
- **Systematic Conservation Planning** : Planification systématique, représentation, persistance, complémentarité, irremplaçabilité, cibles de conservation, prioritization, Zonation, prioritizr
- **Protected Area Design** : Conception d'aires protégées, réseau écologique, représentativité, gap analysis, efficacité de gestion, PAME, IUCN categories, OECMs
- **Connectivity** : Connectivité écologique, corridors, stepping stones, least-cost paths, circuit theory, Circuitscape, graph theory, omni-directional connectivity, linkage mapper
- **Corridor Mapping** : Cartographie de corridors, ecological networks, green infrastructure, espèces parapluies, zones de dispersion, modèles de connectivité fonctionnelle, connectivity planning

## Catégories arXiv
- q-bio.QM (Quantitative Methods), cs.CV (Computer Vision), cs.LG (Machine Learning), stat.AP (Statistics Applications), physics.geo-ph (Geophysics)

## Références Clés
- Elith & Leathwick (2009) — "Species Distribution Models" Annual Review of Ecology
- Phillips et al. (2006) — "Maximum Entropy Modeling of Species Geographic Distributions"
- Ball, Possingham & Watts (2009) — "Marxan and Relatives" in Spatial Conservation Prioritization
- MacKenzie et al. (2017) — "Occupancy Estimation and Modeling"
- Burnham & Anderson (2002) — "Model Selection and Multimodel Inference"
- Methods in Ecology and Evolution, Ecological Monographs, Conservation Biology
- Biological Conservation, Ecology, Journal of Applied Ecology
- Remote Sensing of Environment, Ecological Applications