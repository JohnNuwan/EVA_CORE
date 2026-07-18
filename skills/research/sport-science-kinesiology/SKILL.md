---
name: sport-science-kinesiology
description: "Compétence niveau ingénieur/docteur en science du sport et kinésiologie computationnelles. Couvre la biomécanique ML, la physiologie de l'exercice, l'analyse de mouvement, la prévention de blessures, la rééducation, la performance sportive, la charge d'entraînement, la nutrition sportive, la psychologie du sport, et la technologie wearable pour le sport."
---

# Science du Sport et Kinésiologie Computationnelles

## Présentation
Cette skill couvre l'application de l'intelligence artificielle, du machine learning et des méthodes computationnelles à la science du sport et à la kinésiologie. Elle s'adresse aux chercheurs et ingénieurs travaillant sur la biomécanique, l'analyse de mouvement, la prévention des blessures, la physiologie de l'exercice, la psychologie du sport, et les technologies wearables pour la performance sportive.

## Biomécanique Computationnelle
- **Motion Capture** : Capture de mouvement, marqueurs réfléchissants, systèmes optoélectroniques (Vicon, OptiTrack, Qualisys), mocap sans marqueur (pose estimation), calibration, filtrage, gap filling, c3d format
- **Inverse Dynamics** : Dynamique inverse, calcul des moments articulaires, forces de réaction au sol, Newton-Euler, Lagrange, modèles musculo-squelettiques, résolution de forces, optimisation
- **EMG ML** : Électromyographie, EMG de surface, EMG intramusculaire, traitement de signal EMG, extraction de features, classification de mouvements, prédiction de force, modèles ANN/CNN/RNN pour EMG
- **Joint Moments** : Moments articulaires, puissances articulaires, moments d'extension/flexion, abduction/adduction, rotation interne/externe, analyse de moments sous charge, normalisation
- **Gait Analysis** : Analyse de la marche, paramètres spatio-temporels, cinématique, cinétique, phases de marche, running gait, analyse de la course, analyse de la marche pathologique, modèles ML pour la détection
- **AnyBody** : Logiciel AnyBody Modeling System, modèles musculo-squelettiques, simulation de forces musculaires, optimisation de recrutement, modèles personnalisés, scaling morphologique
- **OpenSim** : OpenSim, simulation musculo-squelettique open-source, modèles de membres inférieurs/supérieurs, computation de forces, analyse de sensibilité, CMC (Computed Muscle Control), RRA (Residual Reduction Algorithm)

## Analyse de Mouvement
- **Pose Estimation** : Estimation de pose humaine, OpenPose, MediaPipe Pose, PoseNet, AlphaPose, HRNet, ViTPose, MMPose, 2D/3D pose, keypoint detection, estimation de pose multi-personne
- **Action Recognition** : Reconnaissance d'actions, classification de mouvements sportifs, TimeSformer, I3D, SlowFast, ST-GCN, VAT, action segmentation, temporal action detection, sports action recognition
- **SportCV** : Computer Vision pour le sport, tracking de joueurs, analyse de formation, détection d'événements sportifs, ball tracking, court/field line detection, broadcast augmentation, Hawk-Eye, TRACAB
- **Sequential Pattern** : Patterns séquentiels dans le mouvement, détection de motifs, séquence d'actions, analyse de stratégie, alignement temporel, DTW (Dynamic Time Warping), modèles séquentiels
- **Skill Assessment** : Évaluation de compétence, scoring de performance, analyse de technique, évaluation de qualité de mouvement, feedback automatisé, coaching assisté par IA, skill classification
- **Form Correction** : Correction de forme, feedback en temps réel, détection d'erreurs de technique, correction de posture, form guidance, modèles de form check, coaching interface

## Prévention et Rééducation
- **Injury Risk ML** : Prédiction de risque de blessure, modèles de risque, classification des facteurs de risque, load management, screening, modèles ML pour la prévention (Random Forest, XGBoost, LSTM)
- **Return-to-Sport** : Retour au sport, protocoles RTS, critères de décision, évaluation fonctionnelle, readiness testing, modèles de prédiction, RTS after ACL, RTS after concussion
- **Rehabilitation Monitoring** : Monitoring de rééducation, progression de rééducation, modèles de suivi, compliance, adherence, téléréhabilitation, capteurs pour la rééducation, exergames
- **Concussions Assessment** : Évaluation des commotions cérébrales, SCAT5, BESS, ImPACT, King-Devick, modèles ML pour la détection, baseline testing, return-to-play, head impact sensors
- **ACL Prediction** : Prédiction de blessure du LCA, modèles de risque, analyse de mouvement, landing mechanics, valgus collapse, quad dominance, ligament dominance, trunk control, screening

## Physiologie de l'Exercice
- **VO2max ML** : Prédiction de VO2max, estimation de consommation d'oxygène, modèles de performance aérobie, test de Cooper, test de Bruce, prediction ML, maximal oxygen uptake, modèles physiologiques
- **Lactate Threshold** : Seuil lactique, seuil anaérobie, OBLA, MLSS, Dmax, modèles de lactate, prédiction de seuil, estimation de zones d'entraînement, modèles de cinétique de lactate
- **HRV Analysis** : Analyse de variabilité de fréquence cardiaque, HRV time-domain, frequency-domain, nonlinear, RMSSD, SDNN, LF/HF, Poincaré, modèles ML pour stress/recovery, HRV biofeedback
- **Fatigue Modeling** : Modélisation de la fatigue, fatigue neuromusculaire, fatigue centrale/périphérique, modèles de fatigue (Banister, TSB, P:TE), modèles ML prédictifs, recovery curves
- **Training Load** : Charge d'entraînement, acute-chronic workload ratio (ACWR), TRIMP, EPOC, session RPE, TSS, monotony, strain, modèles de charge, relation charge-blessure
- **Periodization** : Périodisation de l'entraînement, mesocycles, macrocycles, microcycles, tapering, peaks, block periodization, linear vs nonlinear, optimisation de la période, modèles ML

## Psychologie du Sport
- **Mental Performance** : Performance mentale, imagerie mentale, visualisation, routines, préparation mentale, concentration, flow state, mental toughness, resilience, optimisation cognitive
- **Team Dynamics** : Dynamique d'équipe, cohésion, communication, leadership, rôles, interactions sociales, modèles de réseaux sociaux, sociométrie, analyse de coordination
- **Motivation** : Motivation intrinsèque/extrinsèque, théorie de l'autodétermination (SDT), goal setting, achievement goal theory, mindset, grit, modèles ML de prédiction motivationnelle
- **Attention ML** : Attention et concentration, attention sélective, attention divisée, vigilance, focus sous pression, modèles ML d'attention, eye tracking, quiet eye, attention training
- **Decision-Making Under Pressure** : Prise de décision sous pression, anticipation, perception-action coupling, modèles de décision en sport, naturalistic decision making, recognition-primed decision, ML pour l'analyse

## Wearables et Capteurs
- **IMU** : Inertial Measurement Units, accéléromètres, gyroscopes, magnétomètres, IMU fusion, calibration, orientation estimation, quaternions, Euler angles, Madgwick, Mahony, sensor fusion
- **GPS** : GPS sportif, Catapult, STATSports, GPSports, position tracking, vitesse, accélération, distance, PlayerLoad, métriques de demande physique, heat maps, GPS accuracy
- **Accelerometer Data** : Données d'accéléromètre, counts, vector magnitude, activity classification, comptage de pas, estimation de dépense énergétique, modèles ML pour l'activité
- **Smart Clothing** : Vêtements intelligents, textiles connectés, sensors intégrés, ECG textile, EMG textile, respiration, température, smart shoes, smart socks, compression garments
- **Smart Insoles** : Semelles connectées, capteurs de pression, distribution de pression plantaire, analyse de la marche, balance, landing patterns, force sensing, in-shoe sensors
- **PlayerLoad** : Métrique de charge de joueur, accélérations triaxiales, PlayerLoad per minute, 2D/3D PlayerLoad, différences par sport, monitoring, fatigue index, workload management

## Catégories arXiv
- cs.CV (Computer Vision), cs.LG (Machine Learning), stat.AP (Statistics Applications), q-bio.QM (Quantitative Methods), cs.HC (Human-Computer Interaction)

## Articles Clés
- **FootsiesGym RLC 2026** : Reinforcement Learning Competition for Fighting Games — référence en apprentissage par renforcement pour l'analyse de jeux de combat/sport

## Références Clés
- Winter (2009) — "Biomechanics and Motor Control of Human Movement"
- Robertson et al. (2014) — "Research Methods in Biomechanics"
- Bompa & Buzzichelli (2019) — "Periodization: Theory and Methodology of Training"
- Journal of Biomechanics, Gait & Posture, Sports Biomechanics
- Medicine & Science in Sports & Exercise, Journal of Sports Sciences
- International Journal of Sports Physiology and Performance
- IEEE Transactions on Neural Systems and Rehabilitation Engineering
- Sensors, Frontiers in Sports and Active Living, Journal of Strength and Conditioning Research