---
name: satellite-remote-sensing
description: "Compétence niveau expert en technologie satellite et télédétection computationnelles. Couvre les plateformes satellite (LEO/GEO/SAR/optique), le traitement d'images satellite, la photogrammétrie, la classification supervisée/non-supervisée, la détection de changement, le pansharpening, la fusion multi-capteurs, la mission planning, le tasking satellite, et le edge computing spatial."
category: research
domain: remote-sensing
---

# Technologie Satellite & Télédétection Computationnelles

## Présentation
Ce skill couvre l'application de l'intelligence artificielle et du deep learning aux technologies satellite et à la télédétection. Il aborde les plateformes et capteurs, le traitement d'images, la classification et segmentation, la photogrammétrie et 3D, le deep learning spatial, et le edge computing spatial.

## 1. Plateformes et Capteurs Satellites
### Optique
- **Sentinel 2** (ESA): 13 bandes spectrales, 10-60m résolution
- **Landsat 8/9** (NASA/USGS): 11 bandes, 30m, archive depuis 1972
- **Planet Dove**: constellation 200+ cubesats, 3-5m, revisite quotidienne
- **Maxar (WorldView)**: très haute résolution (30-50cm), imagerie commerciale
- **SPOT**: 1.5-6m, stéréoscopie, revisite haute fréquence
- **Pléiades**: 50cm panchromatique, 2m multispectral

### SAR (Radar à Synthèse d'Ouverture)
- **Sentinel 1** (ESA): bande C, 5-40m, interférométrie InSAR
- **RADARSAT**: bande C, Constellation canadienne 3 satellites
- **SAOCOM**: bande L, pénétration canopée
- **ICEYE**: constellation SAR microsatellites, revisite sub-quotidienne
- **Capella Space**: très haute résolution SAR (50cm)

### Hyperspectral et Autres
- **PRISMA** (ASI): 239 bandes hyperspectrales, 30m
- **EnMAP** (DLR): 242 bandes, 30m
- **MODIS**: 36 bandes, 250-1000m, quotidien
- **VIIRS**: 22 bandes, 375-750m
- **GEDI**: LiDAR spatial pour structure forestière
- **ICESat-2**: altimètre photon-counting, glace et végétation

## 2. Traitement d'Images
### Corrections et Prétraitement
- **Orthorectification**: correction géométrique, MNE, RPC
- **Atmospheric correction**: 6S, Sen2Cor, FLAASH, ACOLITE
- **Pansharpening**: Gram-Schmidt, Brovey, CNNS, IHS, PCA
- **BRDF correction**: correction de réflectance bidirectionnelle

### SAR Processing
- **Speckle filtering**: Lee, Frost, Kuan, non-local means, deep despeckling
- **InSAR interferometry**: DEM generation, deformation mapping, DInSAR
- **PolSAR**: polarimétrie SAR, decomposition target, classification
- **PolInSAR**: SAR interférométrique polarimétrique

## 3. Classification et Segmentation
### Land Cover Deep Learning
- **Semantic segmentation satellite**: pixel-wise classification
- **U-Net**: architecture classique pour segmentation satellite
- **DeepLabV3+**: atrous convolution, ASPP
- **SwinUNet**: transformer-based pour segmentation
- **SegFormer**: transformers hiérarchiques

### Applications
- **Change detection**: Siamese networks, change transformers
- **Deforestation tracking**: surveillance forestière par deep learning
- **Crop classification**: classification des cultures, phenology ML
- **Flood mapping**: cartographie rapide des inondations par SAR
- **Urban mapping**: classification urbaine, impervious surfaces

## 4. Photogrammétrie et 3D
### Reconstruction Stéréo
- **Stereo satellite**: corrélation dense, matching semi-global (SGM)
- **DSM/DTM**: génération de modèles numériques de surface et de terrain
- **Point cloud**: clouds de points photogrammétriques
- **3D reconstruction**: reconstruction 3D multi-vues satellite

### LiDAR Spatial
- **GEDI**: formes d'onde LiDAR, hauteur de canopée, biomasse
- **ICESat-2**: ATL03, ATL08, photon counting, classification sol/végétation
- **Fusion optique-LiDAR**: intégration données optiques et LiDAR pour 3D

### Structure from Motion
- **SfM satellite**: incrémentation automatique à partir d'images
- **Multi-view stereo**: MVS pour scènes satellitaires
- **Time series 3D**: nuages de points temporels

## 5. Deep Learning Spatial
### Fondations Models
- **Remote sensing foundation models**: modèles pré-entraînés sur données satellite
- **Self-supervised learning (SSL)**: SSL pour données satellite (MAE, SimCLR, BYOL)
- **Prithvi**: foundation model NASA/IBM pour télédétection
- **SatMAE**: Masked Autoencoder spécifique satellite
- **SpectralGPT**: modèle spectral large

### Architectures Temporelles
- **Spatiotemporal transformers**: transformer spatio-temporels (Video Swin, TimeSformer)
- **3D CNNs**: convolutions 3D pour séries temporelles satellite
- **LSTM/ConvLSTM**: modèles récurrents pour analyse temporelle
- **Multi-modal fusion**: fusion optique-SAR-LiDAR par deep learning

## 6. Edge Computing et Tasking
### Onboard ML
- **Onboard ML**: inférence ML à bord du satellite
- **Satellite edge computing**: calcul embarqué spatial
- **Model compression**: quantification, pruning pour contraintes spatiales
- **FPGA in space**: accélération matérielle embarquée

### Mission Planning
- **Mission planning**: planification de missions par optimisation
- **AI tasking**: tasking intelligent des satellites
- **Constellation optimization**: optimisation de constellations
- **Downlink scheduling**: planification de téléchargement données
- **Image prioritization**: priorisation automatique de l'acquisition et transmission

## Catégories
- **cs.CV** (Computer Vision): classification, segmentation, 3D
- **cs.LG** (Machine Learning): foundation models, SSL
- **eess.IV** (Image and Video Processing): traitement d'image satellite
- **physics.geo-ph** (Geophysics): SAR, InSAR, altimétrie
- **cs.AI** (Artificial Intelligence): edge computing, tasking

## Articles Notables
- **Unbox Responsible GeoAI**: cadre pour une géo-IA responsable
- SpectralGPT: Spectral Foundation Model
- Foundation models for remote sensing
