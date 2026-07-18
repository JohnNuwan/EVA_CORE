---
name: lidar-3d-scanning
description: "Compétence niveau expert en technologie LiDAR et numérisation 3D computationnelles. Couvre les principes LiDAR (ToF, phase-shift, FMCW), LiDAR terrestre, mobile, aérien ALS, bathymétrique, drone LiDAR, le traitement de nuages de points, la classification, la segmentation 3D, la modélisation 3D, le SLAM LiDAR, l'extraction de caractéristiques, la forestry LiDAR, l'archéologie LiDAR, le corridor mapping, et les simulations LiDAR."
category: research
domain: lidar
---

# LiDAR & Numérisation 3D Computationnelles

## Présentation
Ce skill couvre l'application de l'intelligence artificielle et du deep learning au LiDAR et à la numérisation 3D. Il aborde les principes et capteurs, le traitement de nuages de points, la segmentation et classification 3D, la forestry et l'environnement, l'archéologie et le patrimoine, et le SLAM LiDAR mobile.

## 1. Principes et Capteurs
### Technologies LiDAR
- **Time-of-Flight (ToF)**: mesure directe du temps de vol, impulsion laser
- **Phase-shift**: modulation continue pour mesures haute précision courte distance
- **FMCW**: Frequency Modulated Continuous Wave, vitesse-distance simultanées
- **Geiger mode**: comptage de photons uniques, très longue portée
- **Single photon**: SPAD, efficacité énergétique, aéroporté

### Capteurs Terrestres et Aériens
- **Riegl**: LiDAR longue portée aéroporté et terrestre (VZ, LMS)
- **Leica**: BLK360, RTC360, ALS (ALS70, ALS80)
- **FARO**: Focus S, terrestrial scanning, industriel
- **DJI Zenmuse L2**: drone LiDAR compact, RGB intégré
- **Velodyne/Ouster**: spinning LiDAR pour mobile et autonome
- **Livox**: LiDAR à balayage non répétitif (Horizon, Mid)
- **Hesai**: LiDAR pour véhicules autonomes (AT128, Pandar)

### LiDAR Spatial et Bathymétrique
- **GEDI**: LiDAR spatial NASA, structure forestière globale
- **ICESat-2**: photon counting, glace/végétation/topographie
- **ALB (Airborne Laser Bathymetry)**: LiDAR bathymétrique, fonds marins

## 2. Traitement de Nuages de Points
### Prétraitement
- **Filtering**: filtrage de bruit (statistical outlier removal, radius filtering)
- **Noise removal**: suppression de points aberrants
- **Subsampling**: échantillonnage (voxel grid, random, FPS)
- **Georeferencing**: géoréférencement, transformation de coordonnées

### Registration
- **ICP (Iterative Closest Point)**: registration fine point-to-point, point-to-plane
- **NDT (Normal Distributions Transform)**: registration probabiliste
- **Global registration**: RANSAC, FPFH, TEASER
- **Multi-sensor registration**: fusion LiDAR-caméra-IMU

### Formats et Outils
- **LAS/LAZ**: formats standard de stockage
- **PDAL**: Processing of LiDAR data (pipeline)
- **CloudCompare**: visualisation, édition, comparaison
- **LAStools**: outils de traitement LiDAR
- **Classification ground/non-ground**: algorithms de classification du sol

## 3. Segmentation et Classification 3D
### Deep Learning 3D
- **PointNet++**: architecture pionnière pour classification segmentation nuages
- **RandLA-Net**: random sampling, efficace pour larges nuages
- **KPConv**: kernel point convolution
- **MinkowskiEngine**: sparse convolution 3D, efficace
- **Cylinder3D**: représentation cylindrique pour scènes larges

### Applications
- **Semantic segmentation**: classification sémantique point par point
- **Instance segmentation**: segmentation par instance
- **Object detection 3D**: détection d'objets (voitures, bâtiments, arbres)
- **Panoptic segmentation**: fusion sémantique + instance

## 4. Forestry et Environnement
### Canopée et Biomasse
- **CHM (Canopy Height Model)**: modèle de hauteur de canopée
- **Canopy height extraction**: hauteur des arbres par CHM
- **Biomass estimation**: estimation de biomasse forestière
- **Tree segmentation**: segmentation d'arbres individuels
- **Individual tree detection (ITD)**: détection de chaque arbre

### ALS Metrics
- **ALS metrics**: métriques LiDAR aéroporté (height percentiles, intensity, cover)
- **GEDI waveform**: analyse de formes d'onde GEDI
- **Forest structure**: structure verticale et horizontale de la forêt
- **Species classification**: classification d'essences forestières
- **Fuel mapping**: cartographie du combustible pour incendies

## 5. Archéologie et Patrimoine
### Découverte Sous Canopée
- **LiDAR archaeology**: détection de structures archéologiques sous couvert forestier
- **Ground filtering for hidden structures**: filtrage pour révéler structures au sol
- **Maya detection**: détection de sites mayas sous canopée
- **Palatium**: analyse de sites archéologiques palatiaux

### Sites et Monuments
- **Cultural heritage 3D**: numérisation 3D du patrimoine
- **Historical site scanning**: scanning de sites historiques
- **Building archaeology**: analyse architecturale par LiDAR
- **Underwater archaeology**: archéologie sous-marine par ALB

### Traitements Spécifiques
- **Hillshade analysis**: ombrage pour visualisation des micro-reliefs
- **Sky-view factor**: facteur de vision du ciel pour révélation
- **Local relief model**: modélisation du relief local
- **Slope analysis**: analyse de pentes pour structures anthropiques

## 6. SLAM LiDAR et Mobile
### SLAM 3D
- **LiDAR SLAM**: Simultaneous Localization and Mapping
- **LOAM (Lidar Odometry and Mapping)**: méthode fondatrice
- **LeGO-LOAM**: version légère optimisée
- **LIO-SAM**: tight coupling LiDAR-IMU
- **FAST-LIO**: efficace temps réel
- **LIVOX-LOAM**: SLAM adapté Livox

### Cartographie Mobile
- **3D mapping mobile**: cartographie mobile multi-capteurs
- **Autonomous driving LiDAR**: mapping HD pour conduite autonome
- **HD maps**: cartes haute définition, lane-level
- **Corridor mapping**: cartographie de corridors (routes, voies ferrées)
- **Railway LiDAR**: scanning ferroviaire pour inspection

## Catégories
- **cs.CV** (Computer Vision): segmentation, détection, registration
- **cs.LG** (Machine Learning): deep learning 3D, classification
- **cs.RO** (Robotics): SLAM, mapping mobile
- **physics.geo-ph** (Geophysics): ALS, bathymétrique, GEDI
- **cs.GR** (Graphics): modélisation 3D, rendu
- **eess.SP** (Signal Processing): waveform, filtrage

## Articles Notables
- **ELSA3D**: Enhanced Learning for Semantic Analysis in 3D
- **Lower Bounds on Vietoris-Rips Complexes**: fondations computationnelles
- PointNet++: Deep Hierarchical Feature Learning on Point Sets
