---
name: public-health-epidemiology
description: "Compétence niveau ingénieur/docteur en santé publique et épidémiologie computationnelle. Couvre modélisation épidémiologique (SIR, agent-based), surveillance ML, bio-surveillance, pharmacoépidémiologie, santé mondiale, analyse de données de santé, et préparation aux pandémies."
category: research
tags: [public-health, epidemiology, disease-modeling, surveillance-ml, pharmacoepidemiology, global-health, pandemic-preparedness, health-data]
arxiv_categories: [stat.AP, cs.LG, q-bio.QM, cs.CY, physics.soc-ph]
---

# Compétence : Santé Publique et Épidémiologie Computationnelle (Public Health & Computational Epidemiology)

## Présentation

Cette compétence de niveau ingénieur/docteur couvre l'application des méthodes computationnelles, de l'intelligence artificielle et de l'apprentissage automatique à la santé publique et à l'épidémiologie. Elle intègre la modélisation mathématique des maladies infectieuses, les systèmes de surveillance ML, la pharmacoépidémiologie, l'analyse des données de santé à grande échelle, et la préparation aux pandémies. Le practitioner est outillé pour concevoir, implémenter et valider des modèles épidémiologiques et des systèmes de surveillance pour la prise de décision en santé publique.

---

## 1. Modélisation Épidémiologique (Epidemiological Modeling)

### Modèles Compartimentaux SIR/SEIR
- **SIR classique** : équations différentielles ordinaires (ODE), taux de reproduction R₀, seuil épidémique, équilibre endémique.
- **Extensions** : SEIR (latence), SEIRS (perte immunité), SIRV (vaccination), MSEIR (maternelle), SIDARTHE (interventions).
- **Modèles stochastiques** : processus de naissance-mort, chaînes de Markov en temps continu (CTMC), simulation individuelle (Gillespie).
- **Calibration & Inference** : MCMC (Metropolis-Hastings, NUTS), ABC (Approximate Bayesian Computation), particle filtering, ensemble adjustment Kalman filter.

### Agent-Based Modeling (ABM)
- **Framework** : agents individuels avec attributs (âge, mobilité, statut épidémiologique), règles de comportement, interactions (contact networks).
- **Plateformes** : NetLogo, Repast Simphony, GAMA, MASON, FluTE, Covasim.
- **Paramètres** : réseaux de contacts (sociaux, familiaux, professionnels, scolaires), mixing patterns (POLYMOD), mobility data (GTFS, CDRs).
- **Validation** : calibration, sensitivity analysis, pattern-oriented modeling, synthetic population generation.

### Réseaux de Contacts (Contact Networks)
- **Modèles de graphes** : configuration model, small-world (Watts-Strogatz), scale-free (Barabási-Albert), random geometric.
- **Data-driven networks** : enquêtes POLYMOD, BBC Pandemic, SafeGraph, Facebook Data for Good.
- **Épidémiologie sur réseaux** : percolation, SIS/SIR sur graphes, threshold models, superspreading events (k-paramètre de dispersion).

### Simulation Stochastique
- **Gillespie Algorithm (SSA)** : τ-leaping, exact stochastic simulation, hybrid ODE/SSA.
- **Spatial models** : lattice-based (cellular automata), metapopulation (patches, mobilité), gravity/radiation models.
- **Multi-patch & Multi-scale** : interaction échelle locale ↔ régionale ↔ globale, aviation, transportation network.

---

## 2. Surveillance ML (ML-based Surveillance)

### Surveillance Syndromique (Syndromic Surveillance)
- **Définition** : détection précoce d'épidémies via des indicateurs non spécifiques (fièvre, ventes de médicaments, absences, consultation web).
- **Algorithmes** : CUSUM, EWMA, Holt-Winters, Shewhart control charts — améliorés par deep learning pour séries temporelles.
- **Sources de données** : Google Trends (GT), séjours urgences (ICD triage), ventes pharmacie, appels SOS médecins, réseaux sociaux (Twitter).
- **Nowcasting** : DeepGLEAM, ARGO, ARGO2, Gaussian processes pour prédire incidence en temps réel.

### Détection d'Épidémies (Outbreak Detection)
- **Early Warning Systems** : WHO Epidemic Intelligence from Open Sources (EIOS), ProMED-mail, HealthMap, GPHIN (Global Public Health Intelligence Network).
- **ML pour détection** : anomalie temporelle (LSTM, Transformers), anomalie spatiale (scan statistics, Kulldorff, Bayesian spatial models).
- **Multi-source fusion** : fusion de données hétérogènes (clinique, laboratoire, environnement, One Health vectorielle).

### Surveillance par Eaux Usées (Wastewater Monitoring)
- **Wastewater-Based Epidemiology (WBE)** : quantification ARN viral (SARS-CoV-2, polio, mpox) dans les eaux usées.
- **ML pour WBE** : normalisation, correction biais (population, débit, dégradation), prédiction incidence, early warning (lead time 4–7 jours).
- **Modélisation** : back-calculation (viral load → infected prevalence), Bayesian hierarchical models, spatial smoothing.

---

## 3. Pharmacoépidémiologie (Pharmacoepidemiology)

### Drug Safety & Adverse Events ML
- **Détection de signaux** : disproportionnalité (PRR, ROR, BCPNN, MGPS), tree-based scan statistic, IC (Information Component).
- **ML pour signal detection** : random forest, XGBoost, deep learning sur FAERS (FDA Adverse Event Reporting System), VigiBase (WHO).
- **Causal Inference** : target trial emulation, difference-in-differences, instrumental variables, propensity score matching, directed acyclic graphs (DAGs).

### Real-World Evidence (RWE)
- **Sources** : claims databases (Medicare, Medicaid, MarketScan, CPRD, IQVIA), EHR, registries, mobile health data.
- **Study Designs** : cohort studies, case-control, self-controlled case series (SCCS), interrupted time series.
- **Data Quality** : missing data (MICE, multiple imputation), misclassification, confounding by indication, immortal time bias.

### FDA Adverse Event Database
- **FAERS** : structure, deduplication, stratification, signal management, data mining.
- **Post-Marketing Surveillance** : pharmacovigilance, risk management plans (RMP), REMS, periodic safety update reports (PSUR).

---

## 4. Santé Mondiale (Global Health)

### Burden of Disease
- **GBD (Global Burden of Disease Study)** : DALYs (Disability-Adjusted Life Years), YLL (Years of Life Lost), YLD (Years Lived with Disability).
- **IHME (Institute for Health Metrics)** : modèles spatio-temporels, DisMod-MR (meta-regression), CODEm (Cause of Death Ensemble model).
- **Indicateurs** : mortalité infanto-juvénile, mortalité maternelle, espérance de vie, HALE (Healthy Life Expectancy).

### Health Metrics
- **Spatial Epidemiology** : smoothing Bayesien (BYM model), INLA (Integrated Nested Laplace Approximations), geostatistical models.
- **Health Inequalities** : Gini coefficient, concentration index, slope index of inequality, ML pour détection de disparités.
- **Universal Health Coverage (UHC)** : tracer indicators, service coverage index, financial risk protection.

### Analyse Comparative
- **Cross-country modeling** : multilevel models, meta-analysis, network meta-analysis, ML pour comparaison de systèmes de santé.
- **Disease-specific** : malaria, TB, HIV, NTDs, NCDs — modélisation de l'impact des interventions.

---

## 5. Analyse de Données de Santé (Health Data Analysis)

### ICD Coding & Classification
- **ICD-10/11** : structure (chapitres, blocs, catégories, codes), hiérarchie, coding guidelines, clinical modification (ICD-10-CM/PCS).
- **ML for ICD Coding** : automated ICD coding from clinical text (CNN, LSTM, BERT, ICD coding transformer), hierarchical classification.
- **SNOMED CT, LOINC, RxNorm** : terminologies standards, mapping cross-walks, ontology-based ML.

### Données Hospitalières & Claims
- **Hospital Data** : PMSI (France) / HES (UK) / HCUP (US) — séjours, diagnostics, actes, GHM.
- **Claims Data Analysis** : Charlson/Deyo comorbidity index, episode grouper, cost prediction ML, readmission prediction.
- **Electronic Health Records (EHR) Mining** : structured data (lab, medication, diagnosis) + unstructured (clinical notes, NLP).

### Clinical NLP
- **Named Entity Recognition (NER)** : extraction de diagnostics, médicaments, procédures, dates (cTAKES, CLAMP, SparkNLP, HaNLP).
- **Relation Extraction** : drug-drug interactions, adverse events, temporal relations.
- **Clinical BERT** : BioBERT, ClinicalBERT, PubMedBERT, RadBERT, negation/uncertainty detection (NegEx, ConText).

---

## 6. Préparation aux Pandémies (Pandemic Preparedness)

### Mobility Data & Non-Pharmaceutical Interventions (NPIs)
- **Mobility Data Sources** : Google COVID-19 Community Mobility Reports, Apple Mobility Trends, SafeGraph, Meta Data for Good.
- **NPI Modeling** : social distancing, mask mandates, school closures, travel restrictions, lockdown effectiveness (difference-in-differences, synthetic control).
- **Causal Impact** : Bayesian structural time series, CausalImpact (Google), interrupted time series analysis.

### Vaccine Distribution Optimization
- **Supply Chain** : allocation optimale (age-based, risk-based, geospatial), equity-efficiency trade-off.
- **Vaccine Prioritization** : multi-criteria decision analysis, optimization under uncertainty, dynamic programming, reinforcement learning.
- **Herd Immunity Threshold** : Vc = (1 - 1/R₀) / E, waning immunity, booster strategies, variant-specific modelling.

### Genomic Surveillance
- **Phylodynamics** : BEAST, Nextstrain, Phylogeography, phylodynamics ML (phylogenetic tree + epidemiological).
- **Variant Detection** : lineage classification (Pangolin), mutation calling, spike protein changes, fitness estimation.
- **Real-time genomic** : GISAID, GenBank, sequencing platforms (Illumina, Nanopore), wastewater variant detection.

---

## Références et Lectures

- **ArXiv** : stat.AP (Statistics & Applications), cs.LG, q-bio.QM (Quantitative Methods), cs.CY, physics.soc-ph.
- **WHO** : *Global Influenza Surveillance and Response System (GISRS)*, *International Health Regulations (IHR 2005)*.
- **CDC** : *MMWR, Epi Info, ESSENCE, BioSense, National Syndromic Surveillance Program (NSSP)*.
- **ECDC** : *European Surveillance System (TESSy)*, *Threat Tracking Tool (TTT)*.
- **Lancet Digital Health, PLOS Computational Biology, Epidemics, BMC Infectious Diseases**.
- **MIDAS (Models of Infectious Disease Agent Study)** : Network for epidemic modeling, COVID-19 models.
- **ISPOR / ICPE** : conférences en pharmacoépidémiologie et outcomes research.
- **Nextstrain** : *Real-time pathogen evolution tracking* (nextstrain.org).