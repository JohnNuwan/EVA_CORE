---
name: astronomy-astrophysics-ai
description: "Compétence niveau ingénieur/docteur en astronomie et astrophysique computationnelles. Couvre le ML pour la cosmologie, la classification de galaxies, la détection d'exoplanètes, l'analyse de relevés astronomiques (SDSS, LSST, JWST), la simulation astrophysique, le weak lensing, la radioastronomie, la time-domain astronomy, et l'inférence astrophysique."
---

# Astronomie et Astrophysique Computationnelles

## Présentation
Cette skill couvre l'application de l'intelligence artificielle, du machine learning et des méthodes computationnelles à l'astronomie et à l'astrophysique. Elle s'adresse aux chercheurs et ingénieurs travaillant sur la cosmologie computationnelle, la classification de galaxies, la détection d'exoplanètes, l'analyse de grands relevés astronomiques, la simulation astrophysique et l'inférence bayésienne en astrophysique.

## Cosmologie ML
- **Weak Lensing** : Cisaillement gravitationnel faible, convergence, shear-to-mass inversion, cosmic shear, tomographie, halo model, probabilité de cisaillement, modèles ML pour la reconstruction de masse
- **Baryon Acoustic Oscillations (BAO)** : Oscillations acoustiques baryoniques, pic de BAO dans la fonction de corrélation, scale de ruler standard, reconstruction de BAO, modèles de clustering, extraction de BAO par ML
- **Cosmic Microwave Background (CMB)** : Fond diffus cosmologique, anisotropies, power spectrum CMB, paramètres cosmologiques, Planck, ACT, SPT, delensing, component separation, CNN pour CMB
- **Power Spectrum** : Spectre de puissance de matière, spectre de puissance de galaxies, bispectre, polyspectre, estimation de spectre, modèles d'émulateurs, ML pour likelihood-free inference
- **Emulators** : Émulateurs de simulations cosmologiques, Gaussian process emulators, modèles de substitution, BACCO, CosmicEmu, EMCEE, accélération de modèles cosmologiques
- **N-body Simulations** : Simulations à N-corps, dark matter only, hydrodynamiques, GADGET, Arepo, Enzo, RAMSES, Swift, illustris, eagle, simba, modèles ML pour l'approximation de simulations

## Classification Galactique
- **Morphological Classification** : Classification morphologique de galaxies, séquence de Hubble, elliptiques, spirales, irrégulières, Galaxy Zoo, morphologie par ML, classification automatique, Morpheus, Zoobot
- **CNN for Galaxies** : Réseaux de neurones convolutifs pour la classification de galaxies, architectures CNN, transfer learning, Galaxy Zoo CNN, Deep Learning pour la morphologie, galaxy color-magnitude, Galaxy10
- **Spectral Classification** : Classification spectrale, types spectraux (OBAFGKM), indices spectraux, modèles de synthèse spectrale, inversion spectrale, sourcils spectraux, ML pour spectroscopie
- **Merger Detection** : Détection de fusions de galaxies, signes de fusion, queues de marée, coquilles, ponts, classification merger/non-merger, CNN pour fusions, détection d'anomalies, major/minor mergers
- **Anomaly Detection** : Détection d'anomalies dans les relevés astronomiques, outliers, nouvelles classes d'objets, autoencoders, isolation forest, VAEs, GANs pour l'astronomie, rare object detection, active anomaly detection

## Détection d'Exoplanètes
- **Transit Detection** : Détection de transits planétaires, méthode du transit, Kepler, TESS, PLATO, courbes de lumière, Box Least Squares (BLS), transit timing variations (TTV), modèles ML pour transits, detrending
- **Radial Velocity ML** : Détection de vélocité radiale, spectroscopie RV, HARPS, ESPRESSO, RV fitting, modèles ML pour la réduction de bruit RV, détection planétaire, RV trend, RV activity
- **Direct Imaging** : Imagerie directe d'exoplanètes, coronagraphie, imagerie à haut contraste, SPHERE, GPI, post-traitement ADI/SDI, modèles ML pour l'imagerie directe, PSF subtraction
- **Atmospheric Characterization** : Caractérisation atmosphérique, spectroscopie de transmission, spectroscopie d'émission, phase curves, retrieval atmosphérique, modèles ML pour retrieval, JWST exoplanet science
- **Habitability** : Habitabilité planétaire, zone habitable, indices d'habitabilité, Earth Similarity Index (ESI), surface habitability, habitability ML, modèles de climat planétaire

## Relevés Astronomiques
- **SDSS** : Sloan Digital Sky Survey, photométrie, spectroscopie, legacy survey, DR18, BOSS, eBOSS, imaging, fibres, catalogues
- **LSST / Rubin Observatory** : Legacy Survey of Space and Time (LSST), Vera C. Rubin Observatory, 10-year survey, deep drilling, alert stream, DC2, DP0, LSST Science Pipelines, LSST DM
- **JWST** : James Webb Space Telescope, NIRCam, MIRI, NIRSpec, NIRISS, observation modes, JWST data pipeline, calibration, STScI, MAST archive
- **Euclid** : Mission Euclid (ESA), dark energy, weak lensing, galaxy clustering, Euclid data products, NISP, VIS, pipeline Euclid
- **DESI** : Dark Energy Spectroscopic Instrument, spectroscopie de galaxies, survey protocol, targeting, redshift fitting, DESI data, BAO, RSD
- **GAIA** : Gaia (ESA), astrométrie, parallaxes, mouvements propres, DR3, BP/RP spectra, radial velocity, Gaia catalogue, open cluster, white dwarfs
- **Roman** : Nancy Grace Roman Space Telescope (WFIRST), exoplanet microlensing, wide field, coronagraph, HLS
- **Rubin Observatory Data Pipeline** : LSST data management, alert production, difference imaging, AP (Alert Production) pipeline, DRP (Data Release Production) pipeline

## Radioastronomie
- **Radio Interferometry** : Interférométrie radio, VLBI, ALMA, VLA, MeerKAT, ASKAP, visibilities, uv-coverage, imaging, CLEAN, self-calibration, CASA
- **Source Detection** : Détection de sources radio, selavy, PyBDSF, Aegean, source finding ML, CNN pour la détection, source extraction, SNR, Île-de-France survey
- **Fast Radio Bursts (FRBs)** : Sursauts radio rapides, CHIME, ASKAP, FRB detection, burst morphology, classification, host galaxies, FRB cosmology, dispersion measure, repeating FRBs
- **Pulsar Timing** : Timing de pulsars, EPTA, NANOGrav, PPTA, IPTA, pulsar timing array, gravitational waves à nanohertz, pulsar timing residuals, tempo2, PINT, detection de bruit
- **SKA** : Square Kilometre Array, SKA-Mid, SKA-Low, science goals, telescope, data rates, SKA data pipeline, SKA precursors, HI surveys, continuum, polarization, transient
- **LOFAR** : Low Frequency Array, LBA, HBA, LOFAR 2.0, surveys (LoLSS, LoTSS, LoFAR), Epoch of Reionization, cosmic rays, pulsars, transients, source detection

## Time-Domain Astronomy
- **Supernovae Detection** : Détection de supernovae, classification de SN (Ia, Ib, Ic, II), ZTF, Pan-STARRS, ASAS-SN, SN Ia cosmology, light curve fitting, SALT, models ML pour SN, early detection
- **Variable Stars** : Étoiles variables, RR Lyrae, Céphéides, Mira, éclipsantes, classification de variables, OGLE, ASAS, ZTF, ML pour la classification, périodogrammes, feature engineering
- **Gravitational Waves** : Ondes gravitationnelles, LIGO, Virgo, KAGRA, detection, parameter estimation, PE (Population Estimation), templates, ML pour GW, glitch classification, BNS, BBH, NSBH
- **Anomaly Detection in Alerts** : Détection d'anomalies dans les alertes transitoires, LSST alert stream, ZTF alert, broker, Fink, ANTARES, Lasair, ML pour la prioritisation, rare transients
- **Transient Classification** : Classification de transitoires, variables, SN, AGN, TDE, kilonovae, modèles CNN, random forest, features de courbes de lumière, multi-band, multi-epoch

## Inférence Astrophysique
- **Bayesian Inference** : Inférence bayésienne en astrophysique, MCMC, nested sampling, MultiNest, dynesty, emcee, PyMC, Bayes factor, prior/likelihood, HMC, SBI (Simulation-Based Inference)
- **Hierarchical Models** : Modèles hiérarchiques, population inference, hyperparameters, Bayesian hierarchical models, multi-level models, pooling, partial pooling, Bayesian supernovae cosmology
- **Population Synthesis** : Synthèse de populations, binary population synthesis, BPS, SeBa, COMPAS, COSMIC, BPASS, star formation history, IMF, metallicity, ML pour la synthèse
- **Stellar Parameter Estimation** : Estimation de paramètres stellaires, Teff, log g, [Fe/H], spectroscopie, photométrie, astérosismologie, modèles ML pour l'estimation, The Cannon, AstroNN, LAMOST, APOGEE, Gaia

## Catégories arXiv
- astro-ph.CO (Cosmology and Nongalactic Astrophysics), astro-ph.GA (Galaxy Astrophysics), astro-ph.HE (High Energy Astrophysical Phenomena), astro-ph.IM (Instrumentation and Methods for Astrophysics), cs.LG (Machine Learning), cs.CV (Computer Vision), stat.ML (Machine Learning)

## Références Clés
- Ivezić et al. (2014) — "Statistics, Data Mining, and Machine Learning in Astronomy"
- Feigelson & Babu (2012) — "Modern Statistical Methods for Astronomy"
- Planck Collaboration Results Series
- LSST Science Book, Euclid Science Book
- Hogg et al. (2010) — "Data Analysis Recipes" series
- The Astrophysical Journal, Monthly Notices of the Royal Astronomical Society
- Astronomy & Astrophysics, Publications of the Astronomical Society of the Pacific
- Journal of Cosmology and Astroparticle Physics