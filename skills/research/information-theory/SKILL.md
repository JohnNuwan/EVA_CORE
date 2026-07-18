---
name: information-theory
description: >-
  Compétence de recherche en théorie de l'information couvrant cs.IT et math.IT
  — théorie de Shannon, codage source et canal, compression, capacité de canal,
  entropie, information mutuelle, crypto-théorie, codes correcteurs (LDPC,
  Turbo, Polaires), apprentissage avec information, théorie de l'information
  quantique, complexité de Kolmogorov et inférence bayésienne.
category: research
---

# Compétence en Recherche en Théorie de l'Information (cs.IT, math.IT)

## Présentation

La théorie de l'information, fondée par Claude Shannon en 1948, est le cadre mathématique qui sous-tend les communications modernes, la compression de données, la cryptographie et l'apprentissage automatique. Les catégories arXiv **cs.IT** (Information Theory) et **math.IT** (Information Theory) reçoivent environ 150 à 200 nouvelles soumissions par semaine, couvrant à la fois les fondements théoriques et les applications émergentes à l'intersection de l'apprentissage, de la physique quantique et de la complexité algorithmique.

Cette compétence fournit une structure de veille et de navigation pour l'ensemble du domaine.

## Domaines de Recherche Principaux

### 1. Théorie de Shannon et Fondements

- **Entropie et information mutuelle** : Entropie de Shannon, entropie jointe, entropie conditionnelle, information mutuelle, divergence de Kullback-Leibler, divergence de Jensen-Shannon
- **Capacité de canal** : Capacité des canaux discrets sans mémoire (DMC), canaux à entrée continue (AWGN, fading), théorème de codage de canal, théorème de Shannon-Hartley
- **Théorème de codage source** : Compression sans perte (entropie), compression avec perte (distorsion-rate), théorème de Shannon sur le codage source, fonction rate-distortion
- **Loi forte des grands nombres asymptotiquement équipartition (AEP)** : Propriété d'équipartition asymptotique, typical sets, convergence en probabilité
- **Codage conjoint source-canal** : Théorème de séparation de Shannon, codage conjoint source-canal, compromis pratiques

### 2. Codage Source et Compression

- **Compression sans perte** : Code de Huffman, codage arithmétique, codage Lempel-Ziv (LZ77, LZ78), codage par dictionnaire, codage par plages (RLE)
- **Compression avec perte** : Quantification scalaire et vectorielle (VQ), transformée en cosinus discrète (DCT), transformée en ondelettes, compression d'images (JPEG, JPEG2000), compression audio (MP3, AAC), compression vidéo (HEVC/H.265, VVC/H.266, AV1)
- **Codage distribué** : Théorème de Slepian-Wolf (codage distribué de sources corrélées), théorème de Wyner-Ziv (codage avec information adjacente au décodeur)
- **Distorsion-rate (RD)** : Fonction de distorsion-rate, théorème de Shannon sur le taux de distorsion, bornes supérieures et inférieures, algorithmes de Blahut-Arimoto
- **Codage universel** : Codes universels, adaptation en ligne, famille LZ, codes de Fano

### 3. Théorie des Canaux et Capacité

- **Canaux classiques** : Canal binaire symétrique (BSC), canal d'effacement binaire (BEC), canal à bruit additif gaussien blanc (AWGN), canal à évanouissement (fading)
- **Canaux à mémoire** : Canaux à état fini (FSC), capacité des canaux à mémoire, algorithmes de calcul de capacité
- **Canaux à accès multiple** : Canal d'accès multiple (MAC), région de capacité, codage superposé, CDMA, OFDMA, NOMA
- **Canaux de diffusion** : Canal de diffusion (BC), région de capacité, codage par superposition, codage par annulation
- **Canaux à relais** : Canal à relais, capacité, codage par compression et retransmission
- **Canaux à interférence** : Canal à interférence, région de capacité, gestion des interférences, alignment d'interférence
- **Communications sans fil** : Massive MIMO, mmWave, THz, communications optiques sans fil, codage de réseau

### 4. Codes Correcteurs d'Erreurs

#### 4.1 Codes en blocs linéaires
- **Codes de Hamming** : Codes parfaits, distance minimale, correction d'erreur unique
- **Codes de Reed-Solomon** : Codes BCH, codes cycliques, décodage algébrique (Berlekamp-Massey)
- **Codes LDPC (Low-Density Parity-Check)** : Codes de Gallager (1963), matrices de parité creuses, décodage par propagation de croyance (sum-product algorithm), codes LDPC irréguliers, densification, codes LDPC protograph-based, LDPC pour 5G NR, codes LDPC spatiaux (SC-LDPC)
- **Codes polaires (Polar Codes)** : Construction d'Arikan (2009), polarisation des canaux, construction des ensembles d'information, décodage par annulation successive (SC), décodage SCL (Successive Cancellation List), CRC-aided polar codes, polar codes pour 5G NR, polar codes quantiques
- **Codes de Reed-Muller** : Structure récursive, décodage par transformée de Fourier, codes RM vs polar

#### 4.2 Codes convolutifs et Turbo
- **Codes convolutifs** : Codes convolutifs récursifs systématiques (RSC), diagramme en treillis, algorithme de Viterbi, algorithme BCJR (MAP)
- **Turbo codes** : Berrou et al. (1993), entrelaceur, décodage itératif, MAP itératif, Turbo codes pour 3G/4G
- **Turbo product codes** : Produit de codes, décodage itératif par syndromes

#### 4.3 Codes modernes avancés
- **Codes à contrôle de parité spatialement couplés (SC-LDPC)** : Convolutional LDPC, coupling de chaîne
- **Codes polaires généralisés** : Codes PA (Polarization-Adjusted), codes de Reed-Muller polaires
- **Staircase codes, Grid codes** : Codes pour la fibre optique à très haut débit
- **Codes de réseau (Lattice codes)** : Réseaux en dimension infinie, codage pour canaux gaussiens, modulations codées
- **Codes de réseau physiques (Physical-Layer Network Coding)** : PNC, décodage conjoint, codage analogique

### 5. Théorie de l'Information et Apprentissage (Learning with Information)

- **Information bottleneck (IB)** : Principe de goulot d'étranglement informationnel, IB variationnel, échanges précision-complexité
- **Théorie de l'information pour l'apprentissage profond** : Entropie dans les réseaux de neurones, information plane hypothesis, compromis généralisation-mémorisation, complexité de Rademacher et VC informationnelle
- **Généralisation et information** : Information mutuelle entre données et paramètres, bornes de généralisation basées sur l'information, PAC-Bayes et information, stabilité informationnelle
- **Apprentissage par compression** : Minimum Description Length (MDL), principe de Kolmogorov appliqué, théorie de l'information pour l'induction
- **Sélection de caractéristiques avec information** : Sélection basée sur l'information mutuelle, critère d'information de Akaike (AIC), Bayesian Information Criterion (BIC)
- **Apprentissage avec contraintes informationnelles** : Optimisation du taux de code pour l'apprentissage, identifiabilité et information
- **Entropie et complexité neuronale** : Information processing dans les systèmes biologiques, codage neural, information neuronale

### 6. Théorie de l'Information Quantique

- **Entropie quantique** : Entropie de von Neumann, entropie relative quantique, information mutuelle quantique, mesures d'intrication (entropie d'intrication)
- **Capacité des canaux quantiques** : Capacité quantique, capacité classique des canaux quantiques, capacité privée, canaux quantiques à mémoire, capacité de Holevo, théorème de Holevo-Schumacher-Westmoreland
- **Codage et correction d'erreurs quantiques** : Codes stabilisateurs, codes de surface, codes topologiques, codes LDPC quantiques, codes polaires quantiques, codes de Kitaev, seuil de correction
- **Cryptographie quantique** : Distribution quantique de clés (QKD), BB84, E91, MDI-QKD, mesure d'information mutuelle quantique, secrecy capacity quantique
- **Théorie de l'information quantique unifiée** : Ressources quantiques, distillation d'intrication, théorie des ressources quantiques
- **Complexité quantique et information** : Complexité de Kolmogorov quantique, information quantique et algorithmes

### 7. Complexité de Kolmogorov et Théorie Algorithmique de l'Information

- **Complexité de Kolmogorov (C(x))** : Complexité descriptive, complexité de prefix (K(x)), théorème d'invariance, complexité conditionnelle
- **Théorie de la complexité algorithmique** : Complexité de Solomonoff-Levin, complexité de Chaitin, nombre Ω de Chaitin
- **Principe de MDL (Minimum Description Length)** : MDL à deux parties, MDL à parties normalisées, applications à la sélection de modèles
- **Information algorithmique mutuelle** : I(x:y) = K(x) + K(y) − K(x,y), information mutuelle algorithmique
- **Distance de similarité** : Distance de similarité de complexité de Kolmogorov (NCD — Normalized Compression Distance), classification via compression
- **Applications en apprentissage** : Complexité de Kolmogorov pour la généralisation, inférence inductive, complexité de sample

### 8. Inférence Bayésienne et Théorie de l'Information

- **Principes bayésiens** : Théorème de Bayes, inférence bayésienne, distributions a priori et a posteriori, vraisemblance
- **Théorie de l'information et inférence** : Entropie croisée, divergence KL entre a priori et a posteriori, gain d'information bayésien
- **Maximum d'entropie (MaxEnt)** : Principe du maximum d'entropie de Jaynes, distributions a priori non informatives, distributions de référence
- **Sélection de modèles** : Bayesian Information Criterion (BIC), Akaike Information Criterion (AIC), Minimum Message Length (MML)
- **Méthodes variationnelles** : Inférence variationnelle (VI), famille moyenne-field, ELBO, lien avec l'information bottleneck
- **Bayésien et compression** : Codage arithmétique bayésien, MDL bayésien, a priori de Kolmogorov
- **Tests d'hypothèses** : Théorème de Stein, divergence de Chernoff, exponentielle de taux d'erreur, informations de Fisher et de Shannon

### 9. Crypto-théorie et Sécurité de l'Information

- **Secrecy capacity** : Capacité de secret, théorème de Wiretap Channel (Wyner, 1975), canal d'écoute
- **Cryptographie basée sur l'information** : Partage de secret (Shamir), codes d'authentification, codes de hachage universels
- **Théorie de l'information pour la sécurité** : Entropie conditionnelle pour la sécurité, information mutuelle fuite, identification et authenticité
- **Physique et sécurité** : Distribution quantique de clés (QKD), attaques informationnelles
- **Identification via canaux** : Capacité d'identification, construction de codes d'identification

## Catégories Principales sur arXiv

| Catégorie | Description | Volume Hebdomadaire |
|-----------|-------------|---------------------|
| **cs.IT** | Information Theory — communications, codage, théorie | ~120–150 |
| **math.IT** | Information Theory (mathématiques) | ~30–50 (cross-list cs.IT) |
| **quant-ph** | Quantum Physics — information quantique, canaux quantiques | ~80–100 (dont un sous-ensemble IT) |
| **cs.LG** | Machine Learning — information bottleneck, généralisation | ~300–400 (dont IT cross-listé) |
| **stat.ML** | Machine Learning (statistique) — MDL, PAC-Bayes | ~100–150 |
| **cs.CC** | Computational Complexity — complexité de Kolmogorov | ~10–20 |

## Articles Notables Récents (Mi-2026)

| Titre | Année | Conférence/Journal | Lien |
|-------|-------|--------------------|------|
| A Mathematical Theory of Communication (Shannon) | 1948 | Bell System Technical Journal | [DOI](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x) |
| Low-Density Parity-Check Codes (Gallager) | 1963 | MIT Press | [PDF](https://ieeexplore.ieee.org/book/6251352) |
| Channel Capacity (Shannon) | 1949 | Proc. IRE | — |
| The Wire-Tap Channel (Wyner) | 1975 | Bell System Technical Journal | [DOI](https://doi.org/10.1002/j.1538-7305.1975.tb02040.x) |
| Near Shannon Limit Error-Correcting Coding: Turbo Codes (Berrou, Glavieux, Thitimajshima) | 1993 | ICC'93 | [DOI](https://doi.org/10.1109/ICC.1993.397441) |
| Channel Polarization: A Method for Constructing Capacity-Achieving Codes (Arikan) | 2009 | IEEE Trans. Info. Theory | [arXiv:0807.3917](https://arxiv.org/abs/0807.3917) |
| The Information Bottleneck Method (Tishby, Pereira, Bialek) | 1999 | Allerton'99 | [arXiv:physics/0004057](https://arxiv.org/abs/physics/0004057) |
| Opening the Black Box of Deep Neural Networks via Information (Tishby, Zaslavsky) | 2015 | arXiv | [arXiv:1503.02406](https://arxiv.org/abs/1503.02406) |
| Kolmogorov Complexity and Related Concepts (Li, Vitányi) | 2008 | — | [Site](https://www.springer.com/gp/book/9780387339986) |
| Quantum Information Theory (Wilde) | 2013 | Cambridge Univ. Press | [arXiv:1106.1445](https://arxiv.org/abs/1106.1445) |
| The Capacities of Quantum Channels (Holevo) | 1998 | IEEE Trans. Info. Theory | [DOI](https://doi.org/10.1109/18.681317) |
| Statistical Inference with Maximum Entropy (Jaynes) | 1957 | Physical Review | [DOI](https://doi.org/10.1103/PhysRev.106.620) |
| Achievable Rates for LDPC Codes (Richardson, Urbanke) | 2001 | IEEE Trans. Info. Theory | [DOI](https://doi.org/10.1109/18.910562) |
| Polar Codes are Optimal for Lossy Source Coding (Korada, Urbanke) | 2010 | IEEE Trans. Info. Theory | [arXiv:0903.0307](https://arxiv.org/abs/0903.0307) |
| A Mathematical Theory of Communication (Shannon 1948) | 1997 | arXiv reprint | [arXiv:cs/9709101](https://arxiv.org/abs/cs/9709101) |

## Comment Effectuer la Veille

- **Flux arXiv principal** : `/list/cs.IT/recent` (~150 nouvelles soumissions/semaine)
- **Surveillance cross-list** : cs.IT cross-listé avec math.IT, quant-ph, cs.LG, cs.CR, cs.NI, stat.ML
- **Mots-clés généraux** : `"channel capacity"`, `"polar codes"`, `"LDPC"`, `"information bottleneck"`, `"mutual information"`, `"entropy"`, `"rate-distortion"`, `"Kolmogorov complexity"`, `"quantum channel"`, `"PAC-Bayes"`, `"compressed sensing"`, `"wiretap"`, `"secrecy capacity"`
- **Mots-clés pour les avancées récentes** : `"beyond 5G"`, `"semantic communication"`, `"task-oriented communication"`, `"information-theoretic generalization"`, `"diffusion models and information theory"`, `"LLM and compression"`, `"unsourced random access"`, `"massive MIMO"`, `"reconfigurable intelligent surfaces`
- **Conférences majeures** : IEEE International Symposium on Information Theory (ISIT), IEEE Global Communications Conference (GLOBECOM), IEEE International Conference on Communications (ICC), Allerton Conference on Communication, Control, and Computing
- **Journaux majeurs** : IEEE Transactions on Information Theory, Entropy (MDPI), IEEE Journal on Selected Areas in Information Theory, Problems of Information Transmission

### Flux RSS / Alertes Recommandées
- **arXiv cs.IT** : https://rss.arxiv.org/rss/cs.IT
- **arXiv math.IT** : https://rss.arxiv.org/rss/math.IT
- **Google Scholar Alert** : Recherche personnalisée sur `"information theory"` avec filtres temporels
- **Semantic Scholar** : Research Feed sur cs.IT avec suivi des auteurs clés

### Auteurs Clés à Suivre
- E. Arikan (polar codes)
- G.D. Forney Jr. (coding theory, trellis)
- R.G. Gallager (LDPC codes, information theory)
- T.J. Richardson & R. Urbanke (modern coding theory, LDPC)
- D. Tse (fundamentals of wireless, MIMO)
- N. Tishby (information bottleneck)
- A. El Gamal (network information theory)
- M. Wilde (quantum information theory)
- A. Renyi (Renyi entropy and applications)
- M. Mézard (statistical physics and information theory)
