---
name: oceanography-marine-science
description: "Compétence niveau ingénieur/docteur en océanographie et sciences marines computationnelles. Couvre l'océanographie physique ML, la biologie marine, la modélisation climatique océanique, la prévision de vagues/courants, l'acoustique sous-marine, la détection de déversements pétroliers, la cartographie des fonds marins, l'observation satellite des océans, et les AUV/ROV autonomes."
category: research
tags: [oceanography, marine-science, remote-sensing, AUV, acoustics, climate-modeling]
---

# Océanographie & Sciences Marines Computationnelles — Compétence Recherche

## Présentation

Cette compétence couvre l'état de l'art en océanographie et sciences marines computationnelles assistées par ML et IA, à destination d'ingénieurs et chercheurs. Domaines clés : océanographie physique, biologie marine, acoustique sous-marine, observation satellite, AUV/ROV autonomes, pollution marine.

## Océanographie Physique

- **Ocean circulation models** — ROMS, NEMO, MITgcm, FVCOM, MOM6
- **ML emulators** — émulateurs de modèles océaniques par deep learning (U-Net, Fourier Neural Operators)
- **Eddy detection** — détection de tourbillons océaniques, mesoscale eddies, automated eddy tracking
- **Mixed layer depth** — estimation de la profondeur de couche de mélange par ML
- **Sea surface temperature (SST)** — prévision SST, SST anomaly, ENSO prediction
- **Ocean heat content** — estimation du contenu thermique océanique
- **Thermohaline circulation** — circulation thermohaline, overturning circulation (AMOC)
- **Wave modeling** — SWAN, WAVEWATCH-III, prédiction de vagues par ML
- **Tide modeling** — TPXO, FES, harmonic analysis, prediction de marées
- **Ocean reanalysis** — assimilation de données, ORAS5, GLORYS, SODA

## Biologie Marine

- **Species distribution ML** — SDM, MaxEnt, random forests pour distribution d'espèces marines
- **Coral reef monitoring** — imagerie hyperspectrale, classification de coraux par DL
- **Fish stock assessment** — estimation de stocks halieutiques, surplus production models
- **Plankton identification** — FlowCam, ZooScan, classification de plancton par CNN
- **eDNA analysis** — metabarcoding, métagénomique, bioinformatics
- **Marine mammal detection** — détection acoustique et visuelle de mammifères marins
- **Fisheries management** — modèles population dynamiques, Maximum Sustainable Yield
- **Ocean acidification** — modélisation du pH, calcification, impact écosystèmes
- **Blue carbon** — séquestration carbone océanique, mangroves, herbiers, marais

## Acoustique Sous-Marine

- **SONAR** — sidescan, multibeam, sonar à balayage latéral, bathymétrique
- **Passive acoustics** — écoute passive, détection de signatures acoustiques
- **Marine mammal detection** — détection de vocalisations (baleines, dauphins), classification
- **Ambient noise** — bruit ambiant océanique, shipping noise, impact anthropique
- **Underwater acoustic communications** — communications acoustiques, modems
- **Acoustic tomography** — tomographie acoustique océanique, température, courants
- **Acoustic seabed classification** — classification des fonds marins par acoustique
- **Noise mapping** — cartographie du bruit sous-marin, shipping noise prediction

## Observation Satellite

- **Sea surface temperature (SST)** — AVHRR, MODIS, VIIRS, OSTIA
- **Ocean color** — MODIS Aqua, Sentinel-3 OLCI, SeaWiFS, chlorophyll-a
- **Altimetry** — Jason-3, Sentinel-6, SWOT, sea surface height, geostrophic currents
- **Chlorophyll** — concentration de chlorophylle-a, phytoplankton, blooms
- **SAR oil spill detection** — Sentinel-1 SAR, détection de nappes d'hydrocarbures
- **Bathymetry from space** — estimation bathymétrique par satellite, SDB (Satellite Derived Bathymetry)
- **Sea ice** — glace de mer, concentration, épaisseur, Sentinel-2/3
- **Coastal monitoring** — érosion côtière, turbidité, eutrophisation
- **SAR wind** — vent de surface par diffusion radar

## AUV/ROV Autonomes

- **Underwater robotics** — AUV (autonomous), ROV (téléopéré), gliders, ASV
- **Autonomous navigation** — localisation sous-marine, INS, DVL, USBL/LBL
- **SLAM underwater** — visual SLAM, sonar SLAM, bathymetric SLAM
- **Obstacle avoidance** — sonar 3D, collision avoidance autonome
- **Adaptive sampling** — échantillonnage adaptatif, front tracking, plume tracking
- **Multi-vehicle coordination** — coordination de flotte, formation control
- **Sampling** — CTD, water sampling, sediment coring, eDNA sampling
- **Underwater manipulation** — bras manipulateur sous-marin, intervention autonome
- **Underwater computer vision** — image dehazing, color correction, SLAM visuel

## Catastrophes et Pollution

- **Oil spill tracking** — trajectoire de nappes, GNOME, MEDSLIK, ML prediction
- **Harmful algal blooms (HABs)** — blooms toxiques, détection satellite + in situ
- **Marine debris** — macro and microplastiques, détection satellite + ML
- **Deep sea mining impact** — environmental impact assessment, sediment plumes
- **Coastal erosion** — modélisation de l'érosion, shoreline change ML
- **Hypoxia / Dead zones** — zones hypoxiques, anoxia, Gulf of Mexico
- **Coral bleaching** — détection du blanchissement, SST anomalies
- **Marine heatwaves** — vagues de chaleur marines, MHW detection

## Catégories arXiv

- physics.ao-ph (Atmospheric and Oceanic Physics)
- physics.geo-ph (Geophysics)
- cs.RO (Robotics)
- cs.CV (Computer Vision and Pattern Recognition)
- cs.LG (Machine Learning)
- stat.AP (Statistics Applications)
- eess.IV (Image and Video Processing)

## Conférences et Journaux Clés

- Journal of Physical Oceanography
- Journal of Geophysical Research: Oceans
- Ocean Modelling
- IEEE Journal of Oceanic Engineering
- Marine Ecology Progress Series
- Ocean Sciences Meeting (AGU/ASLO)
- IEEE OES / OCEANS Conference
- Underwater Technology (UT)
- Frontiers in Marine Science
- Limnology & Oceanography

## Ressources et Datasets

- **CMEMS (Copernicus Marine Service)** — données océaniques globales
- **HYCOM / GOFS** — ocean forecast products
- **GODAE / OSTIA** — SST analysis
- **Argo Floats** — profils T/S globaux
- **MBARI / MB-System** — bathymétrie et cartographie
- **EMODnet** — European Marine Observation Data Network
- **OBIS / GBIF** — données biodiversité marine
- **SWOT satellite** — haute résolution altimétrique
- **NOAA CoastWatch** — données satellite côtières

## Outils et Plateformes

- **Pyroms / xmitgcm / xarray** — Python pour modèles océaniques
- **Ocetrac / py-eddy-tracker** — eddy tracking
- **OceanParcels** — lagrangian particle tracking
- **Pangeo / Dask** — big data geoscience
- **CMG (GMT)** — cartographie océanique
- **ROS / Gazebo (UUV Simulator)** — simulation AUV
- **ArduSub / BlueROV** — plateformes AUV open source
- **Vapor / ParaView** — visualisation océanographique 3D