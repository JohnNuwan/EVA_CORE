---
name: archaeology-anthropology-ai
description: "Compétence niveau ingénieur/docteur en archéologie et anthropologie computationnelles. Couvre la télédétection archéologique (LiDAR, satellite), la classification de poterie/fossiles ML, l'analyse de sites, la prospection géophysique, l'archéologie des paysages, la paléoanthropologie computationnelle, l'analyse ADN ancien, et la datation assistée par IA."
category: research
tags: [archaeology, anthropology, computational-archaeology, remote-sensing, paleoanthropology]
---

# Archéologie & Anthropologie Computationnelles — Compétence Recherche

## Présentation

Cette compétence couvre l'état de l'art en archéologie et anthropologie computationnelles assistées par IA, à destination d'ingénieurs et chercheurs. Domaines clés : télédétection, classification ML de vestiges, paléoanthropologie computationnelle, ADN ancien, datation, anthropologie culturelle.

## Télédétection Archéologique

- **LiDAR aérien** — détection de structures cachées sous couvert végétal (Maya, Angkor, Amazonie)
- **Satellite multispectral** — indices spectraux, detection de crop marks, soil marks
- **Drone photogrammetry** — modèles 3D de sites, orthophotos haute résolution
- **Site detection ML** — segmentation sémantique d'images satellites / LiDAR pour détection de sites
- **Crop marks / Soil marks** — indices de végétation, anomalies spectrales
- **InSAR / SAR** — interférométrie radar pour détection de structures enfouies
- **DeepLearning for remote sensing** — U-Net, DeepLab, Mask R-CNN adaptés à l'archéologie
- **Geophysical prospection** — GPR (Ground Penetrating Radar), magnétométrie, électrique, tomographie

## Classification de Vestiges

- **Pottery classification** — typologie automatisée de céramiques par forme + décor
- **Lithic analysis** — analyse de taille de pierre, classification d'outils
- **Typology ML** — clustering, deep metric learning pour établir des typologies
- **Ancient coin recognition** — identification de monnaies antiques, style, atelier
- **Style attribution** — attribution de style / époque par features visuelles
- **3D artifact analysis** — mesh CNN, point cloud classification pour artefacts 3D
- **Ceramic petrography** — analyse de lames minces par ML

## Paléoanthropologie

- **Fossil reconstruction** — reconstruction virtuelle de fossiles endommagés par IA générative
- **Hominin classification** — classification d'espèces d'hominines (Homo, Australopithecus, Paranthropus)
- **Morphometrics** — analyse de forme par landmarks, géométrie morphométrique, PCA
- **Dental analysis** — analyse de dents fossiles, microCT, enamel thickness
- **CT scan ML** — segmentation automatique de CT scans de fossiles
- **Cranial reconstruction** — reconstruction crânienne virtuelle, estimation de capacité crânienne
- **3D morphometrics** — GMM (Geometric Morphometrics), sliding landmarks

## ADN Ancien et Archéogénétique

- **aDNA analysis** — extraction et analyse de l'ADN ancien, damage patterns
- **Population genetics** — modèles de mélange, f-statistics, ADMIXTURE, PCA génétique
- **Migration ML** — reconstruction de migrations humaines, modèles de diffusion
- **Paleoproteomics** — analyse de protéines anciennes (collagène, dental calculus)
- **Phylogenetics ML** — arbres phylogénétiques, phylogénomique
- **Radiocarbon calibration** — calibration Bayésienne de dates radiocarbone (OxCal, Bronk Ramsey)

## Datation

- **Radiocarbon calibration ML** — calibration avancée des dates 14C par Gaussian processes
- **OSL (Optically Stimulated Luminescence)** — datation par luminescence stimulée optiquement
- **Dendrochronology** — cross-dating automatisé, chronologies de référence
- **Bayesian modeling** — modèles chronologiques Bayésiens, séquences stratigraphiques
- **TL / ESR** — thermoluminescence, résonance de spin électronique
- **Uranium-series dating** — datation U/Th, U/Pb

## Anthropologie Culturelle

- **Ethnographic text mining** — analyse NLP de textes ethnographiques, ontologies culturelles
- **Kinship networks** — reconstruction de réseaux de parenté à partir de données généalogiques
- **Cultural evolution** — modèles de transmission culturelle, évolution des techniques
- **Agent-based modeling societies** — simulation de sociétés anciennes, emergence de complexité
- **Spatial analysis** — analyse spatiale des sites, territoires, réseaux d'échange
- **Network analysis** — réseaux sociaux préhistoriques, routes commerciales

## Catégories arXiv

- cs.CV (Computer Vision and Pattern Recognition)
- cs.CY (Computers and Society)
- cs.LG (Machine Learning)
- q-bio.GN (Genomics)
- physics.geo-ph (Geophysics)
- stat.AP (Statistics Applications)

## Conférences et Journaux Clés

- Journal of Archaeological Science
- PLOS ONE (archaeology)
- Antiquity
- Nature Ecology & Evolution
- PNAS (archaeology)
- CAA (Computer Applications and Quantitative Methods in Archaeology)
- SAA Archaeological Record
- Archaeological Prospection

## Ressources et Datasets

- **OpenAthens / Google Earth Engine** — données satellites
- **3DHOP / Potree** — visualisation 3D de sites
- **OxCal / ChronoModel** — calibration Bayésienne
- **ADMIXTURE / TREEMIX** — analyse génétique des populations
- **Pymol / MorphoJ** — morphométrie
- **GPR-SLICE / ReflexW** — traitement GPR
- **Ancient DNA Repository** — base de données aDNA

## Outils et Plateformes

- **TensorFlow / PyTorch** — segmentation d'images satellites, classification d'artefacts
- **GRASS GIS / QGIS** — analyse spatiale archéologique
- **Meshlab / CloudCompare** — traitement de nuages de points 3D
- **R (archaeology packages)** — ArchaeoPhases, Bchron, rcarbon
- **Python (OpenCV / scikit-image)** — prétraitement d'images de fouilles
- **ORB-SLAM / COLMAP** — reconstruction 3D de sites et artefacts