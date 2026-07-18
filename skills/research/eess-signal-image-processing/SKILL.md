---
name: eess-signal-image-processing
description: "Compétence en recherche en traitement du signal et des images suivie sur arXiv sous eess.SP, eess.IV et domaines connexes. Couvre le traitement du signal numérique, l'analyse spectrale, le filtrage adaptatif, la compression, la restauration d'images, la super-résolution, le débruitage et les méthodes parcimonieuses."
category: research
---

# Compétence en Recherche — Traitement du Signal et des Images (eess.SP & eess.IV)

## Présentation

Cette compétence assure une veille scientifique sur le **traitement du signal** et le **traitement d'images** via arXiv, principalement sous **eess.SP** (Signal Processing) et **eess.IV** (Image and Video Processing). Elle couvre les méthodes fondamentales et avancées : filtrage numérique, analyse temps-fréquence, compression, restauration, super-résolution, débruitage, ainsi que les méthodes parcimonieuses et leurs applications biomédicales.

---

## Traitement du Signal Numérique

- **Filtrage numérique** — Filtres RIF (FIR), RII (IIR), Butterworth, Chebyshev, Elliptique, filtrage adaptatif (LMS, NLMS, RLS)
- **Transformées** — Fourier (FFT, DFT, STFT), cosinus (DCT), Hilbert, Hilbert-Huang, Karhunen-Loève (KLT)
- **Analyse temps-fréquence** — Spectrogramme, Wigner-Ville, Gabor, transformée en ondelettes continues et discrètes
- **Ondelettes** — Ondelette de Haar, Daubechies, Symlets, Coiflets, paquets d'ondelettes, ondelettes biorthogonales
- **Échantillonnage et quantification** — Théorème de Nyquist-Shannon, sur-échantillonnage, quantification, bruit de quantification, sigma-delta modulation
- **Analyse multirésolution** — Banques de filtres, sous-échantillonnage, interpolation, transformée en ondelettes rapide

---

## Traitement d'Images

- **Restauration d'images** — Déconvolution, Richardson-Lucy, Wiener filter, régularisation de Tikhonov, dégradation et restauration
- **Débruitage** — Filtre médian, filtre bilateral, Non-Local Means (NL-means), BM3D, débruitage par diffusion anisotrope, débruitage par réseaux de neurones (DnCNN, Noise2Noise, Noise2Void)
- **Super-résolution** — Interpolation (bicubic, Lanczos), super-résolution par patchs, super-résolution par apprentissage profond (SRCNN, ESRGAN, SwinIR, Real-ESRGAN)
- **Défloutage** — Déconvolution aveugle et non-aveugle, estimation de noyau de flou, motion deblurring, défocalisation
- **Amélioration d'images** — Correction de contraste, histogramme equalization, CLAHE, retinex, HDR tone mapping
- **Segmentation d'images** — Seuillage, watershed, level sets, k-means, graph cut, segmentation par deep learning (U-Net, Mask R-CNN)

---

## Analyse Spectrale et Parcimonieuse

- **Compressed Sensing** — Théorie de l'échantillonnage compressé, RIP (Restricted Isometry Property), cohérence, reconstruction parcimonieuse
- **Représentation parcimonieuse** — Sparse coding, pursuit matching, OMP (Orthogonal Matching Pursuit), basis pursuit, décomposition atomique
- **Dictionnaires** — Dictionnaires analytiques (DCT, ondelettes), dictionnaires appris (K-SVD, MOD), dictionnaires hiérarchiques
- **Reconstruction parcimonieuse** — Basis Pursuit (BP), Dantzig selector, reconstruction sous contrainte de parcimonie
- **Application au traitement d'images** — Inpainting parcimonieux, compression parcimonieuse, séparation de sources par morphologie parcimonieuse

---

## Compression

- **Compression d'images** — JPEG, JPEG 2000, HEIF, compression par ondelettes, EZW, SPIHT, compression fractale
- **Compression vidéo** — H.264/AVC, H.265/HEVC, H.266/VVC, MPEG, motion estimation, compensation de mouvement, GOP
- **Codecs neuronaux** — Compression par autoencodeurs, réseaux génératifs pour compression, codecs neuronaux end-to-end (Ballé et al., Minnen et al.), compression conditionnelle
- **Compression avec pertes et sans pertes** — Codage entropique, Huffman, arithmetic coding, Lempel-Ziv, context modeling
- **Standards et formats** — AVIF, WebP, JPEG XL, compression pour streaming, évaluation de qualité (PSNR, SSIM, MS-SSIM, VMAF)

---

## Méthodes Parcimonieuses

- **LASSO (Least Absolute Shrinkage and Selection Operator)** — Régression L1, sélection de variables, régularisation parcimonieuse, coordinate descent
- **ISTA (Iterative Shrinkage-Thresholding Algorithm)** — Algorithme de seuillage itératif, FISTA (Fast ISTA), convergence, proximal gradient
- **LISTA (Learned ISTA)** — Apprentissage des paramètres d'ISTA par réseaux de neurones, unfolding algorithmique, deep unfolding
- **Sparse Coding pour l'apprentissage automatique** — Dictionary learning, sparse autoencoders, sparse convolutional networks, proximal operators
- **Applications** — Sparse PCA, sparse dictionary learning, feature selection parcimonieuse, interprétabilité parcimonieuse

---

## Signaux Biomédicaux

- **ECG (Électrocardiogramme)** — Détection d'ondes P-QRS-T, analyse d'arythmies, compression ECG, débruitage, détection d'ischémie
- **EEG (Électroencéphalogramme)** — Analyse de rythmes cérébraux (alpha, beta, theta, delta), potentiels évoqués, BCI (Brain-Computer Interfaces), détection de crises
- **EMG (Électromyogramme)** — Analyse de signaux musculaires, filtrage, reconnaissance de mouvements, prothèses myoélectriques
- **Analyse de signaux physiologiques** — PPG (photopléthysmographie), SpO2, pression artérielle, respiration, signaux fœtaux
- **IA pour le signal biomédical** — Deep learning pour ECG (detection d'infarctus), EEG (classification d'états mentaux), analyse multimodale

---

## Catégories arXiv surveillées

| Catégorie | Description |
|-----------|-------------|
| **eess.SP** | Signal Processing |
| **eess.IV** | Image and Video Processing |
| **cs.LG** | Machine Learning |
| **cs.CV** | Computer Vision and Pattern Recognition |
| **math.NA** | Numerical Analysis |
| **eess.SY** | Systems and Control |

---

## Articles notables et tendances

- **End-to-End Optimized Image Compression** (Ballé et al.) — Compression d'image neuronale avec optimisation différentiable
- **BM3D** — Algorithme de débruitage par bloc-matching et transformée 3D
- **DnCNN** — Débruitage d'images par réseaux de neurones convolutionnels profonds
- **Noise2Noise** — Apprentissage de débruitage sans données propres
- **SwinIR** — Super-résolution par transformeur hiérarchique
- **Deep Unfolding** — Déploiement d'algorithmes itératifs (LISTA, ADMM-Net) pour traitement de signal neuronal

---

## Requêtes arXiv recommandées

```bash
# Traitement du signal
# cat:eess.SP

# Traitement d'images
# cat:eess.IV

# Compression d'images/vidéo
# cat:eess.IV AND (compression OR codec OR encoding)

# Débruitage
# cat:eess.IV AND (denoising OR restoration)

# Méthodes parcimonieuses
# cat:eess.SP AND (sparse OR compressed sensing OR LASSO)

# Signaux biomédicaux
# cat:eess.SP AND (ECG OR EEG OR biomedical)
```
