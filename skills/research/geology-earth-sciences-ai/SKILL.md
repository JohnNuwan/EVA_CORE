---
name: geology-earth-sciences-ai
description: "Compétence niveau ingénieur/docteur en géologie et sciences de la Terre assistées par IA. Couvre sismologie ML, exploration minière AI, télédétection (remote sensing), géophysique computationnelle, risques naturels, hydrologie ML, imagerie satellite, GIS, et géomodélisation."
category: research
tags: [geology, earth-sciences, remote-sensing, seismology, mineral-exploration, hydrology, gis, natural-hazards, geophysics]
arxiv_categories: [physics.geo-ph, cs.CV, cs.LG, stat.AP, cs.CY]
---

# Compétence : Géologie et Sciences de la Terre Assistées par IA (Geology & Earth Sciences AI)

## Présentation

Cette compétence de niveau ingénieur/docteur couvre l'intégration de l'intelligence artificielle et de l'apprentissage automatique aux sciences de la Terre et à la géologie. Les domaines abordés incluent la télédétection et l'imagerie satellite, la sismologie et la géophysique computationnelles, l'exploration minière assistée par IA, la modélisation des risques naturels, l'hydrologie ML, ainsi que l'analyse spatiale et la géostatistique. L'objectif est de doter le praticien des outils modernes pour l'analyse multi-échelle (locale → globale) et multi-temporelle des systèmes terrestres.

---

## 1. Télédétection et Imagerie Satellite (Remote Sensing & Satellite Imagery)

### Capteurs et Plateformes
- **Sentinel (ESA — Copernicus)** : Sentinel-1 (SAR C-band), Sentinel-2 (MSI 13 bands, 10–60m), Sentinel-3 (OLCI/SLSTR océan et terre), Sentinel-5P (TROPOMI atmosphère).
- **Landsat (USGS/NASA)** : Landsat 8/9 (OLI/TIRS, 11 bands, 30m), archive 50+ ans, Collection 2 Level-2.
- **MODIS (Terra/Aqua)** : 36 bands spectrales, science products (NDVI, LST, albedo, evapotranspiration), résolution 250m–1km.
- **Autres** : SPOT, RapidEye, Planet (Dove/SuperDove 3–5m quotidien), WorldView-3 (30cm pan), IKONOS, GeoEye.

### SAR (Synthetic Aperture Radar) et InSAR
- **SAR Processing** : SLC, range-Doppler algorithm, backscattering (σ⁰, γ⁰), polarimetry.
- **InSAR (Interferometry)** : DEM generation, deformation mapping (mm-scale), DInSAR, PS-InSAR, SBAS.
- **PolSAR & PolInSAR** : decomposition de cibles (Pauli, Freeman-Durden, Yamaguchi), classification polarimétrique.
- **Deep Learning SAR** : despeckling CNN/GAN, segmentation SAR (bâtiments, glace, déforestation, pétrole).

### Deep Learning pour Classification et Segmentation
- **Classification supervisée** : ConvNeXt, ResNet, EfficientNet, Vision Transformer (ViT, Swin) pour land cover / land use.
- **Segmentation sémantique** : U-Net, DeepLabV3+, SegFormer, Mask2Former pour cartographie thématique.
- **Segmentation hyperspectrale** : 3D-CNN, Spectral-Spatial ResNet, HySpecNet, classification minérale.
- **Changement temporel (Change Detection)** : Siamese networks, difference maps, post-classification comparison, transformer-based temporal models.
- **Weakly/Semi-supervised** : pseudo-labels, contrastive learning (SimCLR + remote sensing), self-supervised pretraining sur data satellite.

---

## 2. Sismologie et Géophysique (Seismology & Geophysics)

### Prédiction des Séismes (Earthquake Prediction)
- **Approches ML** : classification précurseurs sismiques, forecasr probabilité (ETAS, SEISMOGEN), deep learning sur catalogs.
- **Features** : b-value, seismic quiescence, foreshock sequences, radon emission, ionospheric anomalies, GPS deformation.
- **Limitations** : prédiction déterministe vs probabiliste — *Nature* consensus qu'une prédiction fiable à court terme n'est pas encore atteinte.
- **State-of-the-art** : recurrent networks (LSTM, GRU) et Transformers pour séries temporelles sismiques, Earthquake Transformer, PhaseNet.

### Inversion Géophysique
- **Inversion sismique** : full-waveform inversion (FWI) avec deep learning (physics-informed neural networks — PINNs).
- **Inversion magnétotellurique** : imagerie conductivité sous-sol, ML pour initial model, uncertainty quantification.
- **Gravity & Magnetic Inversion** : inversion 3D avec réseaux de neurones, forward modelling sur maillage voxel.
- **Joint Inversion** : multi-physics (sismique + MT + gravité) avec contraintes partagées, multi-task learning.

### Imagerie du Sous-Sol (Subsurface Imaging)
- **Traitement sismique** : déconvolution, migration (Kirchhoff, RTM, LSRTM), stacking velocity analysis, Full Waveform Inversion.
- **Attribute Analysis** : coherence, curvature, spectral decomposition, AVO/AVA analysis, deep learning pour facies classification.
- **Seismic Interpretation** : fault detection (CNN 3D), horizon tracking (active learning, graph-based), channel/reef/salt detection.
- **Microseismic Monitoring** : event detection, location, focal mechanism, hydraulic fracturing monitoring.

---

## 3. Exploration Minière (Mineral Exploration)

### Prospection Assistée par IA
- **Mineral Prospectivity Mapping (MPM)** : logistic regression, random forest, SVM, neural networks, gradient boosting.
- **Data Fusion** : géologie, géochimie, géophysique, altération (Aster/SWIR), télédétection.
- **Target Generation** : unsupervised clustering (k-means, SOM, GMM) pour reconnaissance de motifs minéralisateurs.

### Géochimie et Machine Learning
- **Geochemical Signature Analysis** : anomaly detection, background/above-background discrimination, element association, pathfinder elements.
- **Multi-element Analysis** : random forest, XGBoost, autoencoders pour outliers géochimiques, PCA/ICA pour réduction dimensionnelle.
- **Rare Earth Elements (REE)** : ML pour lithologie prédictive, vectorisation vers dépôts de terres rares.

### Resource Estimation & Drilling Optimization
- **Geostatistics vs ML** : kriging, cokriging, simulation séquentielle gaussienne — alternatives ML (Gaussian processes regression, deep kriging).
- **Drilling Target Optimization** : Bayesian optimization, multi-arm bandit, exploration vs exploitation balance, value of information.
- **Geological Modelling** : implicit modelling (Radial Basis Functions), 3D structural modelling, block model ML.

---

## 4. Risques Naturels (Natural Hazards)

### Glissements de Terrain (Landslide Prediction)
- **Susceptibility Mapping** : weights-of-evidence, logistic regression, random forest, deep learning (CNN + topography).
- **Temporal Prediction** : rainfall thresholds (I-D curves), early warning, real-time monitoring (IoT + ML).
- **Spatial Models** : SHALSTAB, TRIGRS, SCOOPS 3D — améliorés par deep learning pour résolution et précision.

### Inondations (Flood Mapping)
- **SAR-based Flood Detection** : seuillage, change detection, U-Net pour classification eau/terre, Sentinel-1 GRD.
- **Flood Risk Modelling** : HEC-RAS, LISFLOOD-FP, CaMa-Flood, avec ML pour calibrage, emulation, réduction d'incertitude.
- **Nowcasting & Forecasting** : LSTM hydrologique sur réseau pluviométrique, ensemble precipitation forecasts.

### Volcans (Volcanic Activity)
- **Deformation Monitoring** : InSAR + ML pour détection automatique du déplacement, classification de sources pressurisées.
- **Thermal Anomaly Detection** : MODIS, VIIRS, Sentinel-3 — ML pour early warning d'activité thermique.
- **Eruption Forecasting** : Poisson models, failure forecast method, pattern recognition sur séries temporelles sismiques et d'émission (SO₂).

### Systèmes d'Alerte Précoce
- **Earthquake Early Warning (EEW)** : P-wave detection, magnitude estimation, ground motion prediction (deep learning), Epicentral location, shaking intensity maps.
- **Multi-Hazard Early Warning** : AI intégré pour séismes, tsunamis, glissements, inondations, éruptions — plateformes UNESCO/IOC.

---

## 5. Hydrologie (Hydrology)

### Ressources en Eau
- **Groundwater ML** : niveau piézométrique prédiction (LSTM, NARX), recharge estimation, qualité eau (classification / régression).
- **Water Quality Monitoring** : turbidité, chlorophylle-a, matière organique dissoute (Sentinel-2 + ML), hyperspectral.
- **Water Balance Modelling** : Budyko framework, SWAT, MODFLOW — hybridé avec ML (physics-informed ML).

### Precipitation Nowcasting
- **Radar & Satellite nowcasting** : PySTEPS (optical flow), DeepRain, ConvLSTM, MetNet (Google), DGMR (DeepMind).
- **Multi-source fusion** : pluviomètres + radar + satellite + NWP blending, diffusion models pour probabilité.
- **Short-term Forecasts (<6h)** : transition des modèles physiques vers des approches purement data-driven (RainNet, U-Net radar).

### Streamflow Prediction
- **Fluvial Forecasting** : LSTM (Kratzert et al. — CAMELS dataset, multi-basin), GR4J + ML post-processing.
- **Low-flow & Drought** : SPI/SPEI indices, ML pour drought onset prediction, clustering de régions hydrologiques.
- **Ensemble Forecasting** : ECMWF, GEFS, multi-model blending, quantile regression neural networks (QRNN).

---

## 6. GIS et Analyse Spatiale (GIS & Spatial Analysis)

### Plateformes et Outils
- **QGIS** : open source, plugin Python, processing toolbox, GRASS GIS, SAGA GIS integration, Model Designer.
- **GDAL/OGR** : traduction raster/vecteur, warp, reprojection, mosaic, gdal_calc, gdalwarp, VRT.
- **PostGIS** : base spatiale PostgreSQL, requêtes spatiales (ST_*), index spatiaux (GIST), PostGIS Raster.
- **GeoPandas** : Python pour données vectorielles, spatial join (sjoin), overlay, choropleth, Fiona/Shapely.

### Analyse Raster et Vectorielle
- **Raster Processing** : terrain analysis (slope, aspect, hillshade, curvature), hydrology (flow accumulation, watershed, stream order).
- **Vector Analysis** : buffer, dissolve, intersect, clip, spatial join, nearest neighbor, network analysis.
- **Spatial ML** : geographically weighted regression (GWR), spatial autocorrelation (Moran's I, LISA), eigenvector spatial filtering.

### Spatial Machine Learning
- **Geostatistical Learning** : kriging, cokriging, Gaussian process regression, ensemble methods with spatial cross-validation.
- **Spatio-Temporal Models** : ST-GCN, ConvLSTM, PredRNN, graph neural networks sur graphes de station.
- **Feature Engineering Spatial** : distance-based features, zoning, landscape metrics, texture (GLCM), morphological operators.

---

## Références et Lectures

- **ArXiv** : physics.geo-ph (Geophysics), cs.CV (Computer Vision), cs.LG, stat.AP (Statistics Applications), cs.CY.
- **EGU General Assembly (European Geosciences Union)** : AI session, hazard, hydrology, geophysics.
- **AGU Fall Meeting (American Geophysical Union)** : Earth and space science conference, AI/ML sessions.
- **IEEE IGARSS** : International Geoscience and Remote Sensing Symposium.
- **Unbox Responsible GeoAI** (article) : geospatial AI trustworthiness, fairness, privacy, accountability.
- **AgroFlux** (article) : AI modeling of carbon and water fluxes in agriculture — spatial ML for carbon flux estimation.
- **GIScience** : International Conference on Geographic Information Science.