---
name: multimedia-systems
description: >-
  Compétence en recherche sur les systèmes multimédia suivie sur arXiv sous
  cs.MM et les domaines cross-listés. Couvre le codage vidéo et audio, le
  streaming adaptatif, le traitement d'images, le son spatial, le multimédia
  distribué, la QoE/QoS, le streaming VR/AR, les métadonnées MPEG-7/MPEG-21,
  les systèmes de conférence et la synchronisation inter-media.
category: research
tags: [arxiv, multimedia, codage-vidéo, streaming, QoE, VR, MPEG, conférence, audio-spatial]
---

# Systèmes Multimédia — Recherche sur arXiv (cs.MM)

## Présentation

La catégorie cs.MM (Multimedia) sur arXiv couvre l'ensemble des technologies de traitement, compression, transport et présentation de contenus multimédia. Les systèmes multimédia modernes intègrent le codage vidéo et audio, le streaming adaptatif sur réseaux hétérogènes, la qualité d'expérience (QoE), les métadonnées de contenu, et les expériences immersives (VR/AR). Cette compétence fournit une structure pour naviguer dans la recherche en systèmes multimédia publiée sur arXiv, avec des liens forts vers cs.NI (Networking), eess.IV (Image/Video), et cs.CV (Computer Vision).

## Domaines de Recherche

### 1. Codage Vidéo

**Standards de compression vidéo :**
- **H.264/AVC (MPEG-4 Part 10)** — standard dominant, prediction intra/inter, transformée DCT entière, déblocage adaptatif
- **H.265/HEVC (MPEG-H Part 2)** — codage efficace à haut débit, CTU/CU quadtree, prediction intra 35 modes, SAO (Sample Adaptive Offset), DST pour blocs 4×4
- **H.266/VVC (MPEG-I Part 3, Versatile Video Coding)** — partition QT/MTT, MIP (Matrix-based Intra Prediction), LFNST (Low-Frequency Non-Separable Transform), ALF (Adaptive Loop Filter), IBC (Intra Block Copy)
- **AV1 (AOMedia Video 1)** — codec ouvert et libre, partitionnement flexible 10-way, warped motion compensation, CDEF (Constrained Directional Enhancement Filter)
- **VP9** — prédécesseur libre d'AV1, partitionnement superblocks 64×64, prediction intra 10 modes
- **MPEG-2 / H.262** — standard historique, profiles MP@ML, MP@HL
- **EVC (MPEG-5 Part 1, Essential Video Coding)** — codage à complexité réduite
- **LCEVC (MPEG-5 Part 2, Low Complexity Enhancement Video Coding)** — couche d'amélioration sur tout codec existant

**Concepts avancés :**
- Prédiction inter-image : compensation de mouvement (MV precision sub-pixel, affine, BIO/DMVR)
- Transformées : DCT/DST, KLT, transformée en ondelettes, transformée sinusoïdale
- Contrôle de débit : CBR, VBR, CRF, ABR, taux-distortion optimization (RDO)
- Codage à description multiple (MDC) — robustesse à la perte de paquets
- Codage scalable (SVC, SHVC) — couches spatiales, temporelles, SNR
- Codage vidéo neuronale : réseaux autoencodeurs, flows de compression end-to-end
- Régulation de débit perceptuel : masquage spatial et temporel, attention visuelle

### 2. Codage Audio

**Standards de compression audio :**
- **AAC (Advanced Audio Coding)** — MPEG-2/4 AAC, HE-AAC (SBR + Parametric Stereo), LD/LD-AAC pour latence réduite
- **Opus** — codec libre IETF, hybride SILK + CELT, commutation prédictif/transformée
- **MP3 (MPEG-1/2 Audio Layer III)** — standard historique, psychoacoustique par bandes critiques, filtre hybride
- **FLAC (Free Lossless Audio Codec)** — compression sans perte, prédiction linéaire, Rice coding
- **Dolby Atmos** — audio spatial orienté objet, rendu basé sur la position (bed + objects), rendu binaural/transaural
- **MPEG-H Audio** — codage audio spatial 3D, scène audio complète
- **AC-4 (Dolby)** — codage audio basé sur la perception, metadata immersif
- **DTS:X** — audio spatial concurrent à Dolby Atmos

**Concepts avancés :**
- Psychoacoustique : seuil d'audition, masquage fréquentiel et temporel, bandes critiques (Bark scale)
- Codage perceptuel : quantification non-uniforme, allocation de bits par bande
- Codage paramétrique : SBR (Spectral Band Replication), PS (Parametric Stereo)
- Codage spatial : Ambisonics (FOA/HOA), VBAP, binauralisation HRTF
- Séparation de sources musicales : démixage par deep learning
- Audio neuronal : diffusion audio, génération vocale, codecs neuronaux (EnCodec, DAC, SoundStream)

### 3. Streaming Adaptatif

**Protocoles et formats :**
- **HLS (HTTP Live Streaming)** — Apple, segments .ts/.fmp4, playlist M3U8, variantes multivideo
- **DASH (Dynamic Adaptive Streaming over HTTP)** — ISO/IEC 23009-1, MPD (Media Presentation Description), segments ISO-BMFF
- **MGP (Multiple GPAC)** — infrastructure DASH/MGP pour streaming scalable
- **CMAF (Common Media Application Format)** — format unique fMP4 pour HLS et DASH, chunks fragmentés
- **LL-HLS (Low-Latency HLS)** — parties pré-initialisées, segments partiels, delta playlists, latence < 3s
- **LL-DASH (Low-Latency DASH)** — chunks HTTP/1.1 chunked transfer, CMAF chunks, CTE (Chunked Transfer Encoding)
- **WebRTC** — streaming temps réel P2P, codecs VP8/VP9/H.264/AV1, DTLS/SRTP, ICE/STUN/TURN

**Concepts avancés :**
- Logique d'adaptation de débit (ABR) : basée sur le débit (rate-based), buffer (buffer-based), hybride, MPC (Model Predictive Control)
- BOLA — adaptation par Lyapunov optimization
- Pseudo-streaming : byte-range requests, seek sur contenu partiel
- Segment duration tuning : compromis latence/efficacité
- CDN multiorigine : serveurs edge pour distribution massive
- Multi-bitrate encoding : transcodage en direct, per-title encoding
- Serveur push HTTP/2 : notifications proactives de segments

### 4. Traitement d'Images et Son Spatial

**Traitement d'images :**
- Compression d'images : JPEG, JPEG 2000 (ondelettes), JPEG XL, HEIF/HEIC (HEVC intra), AVIF (AV1 intra)
- Amélioration d'images : super-résolution (SRCNN, ESRGAN, SwinIR), débruitage, défloutage
- Rééchantillonnage : interpolation bilinéaire, bicubique, lanczos, deep upscaling
- Traitement HDR : tonemapping (Reinhard, ACES), PQ/HLG transfer functions, HDR10/10+, Dolby Vision
- Couleur : espaces colorimétriques (RGB, YUV, ICtCp), gamut mapping

**Son spatial :**
- Ambisonics : ordre 1 (FOA) à ordre élevé (HOA), B-format, encodage/décodage
- HRTF (Head-Related Transfer Functions) : synthèse binaurale personnalisée, mesures acoustiques
- VBAP (Vector-Based Amplitude Panning) — placement de sources virtuelles
- Rendus binaural et transaural : cross-talk cancellation
- Audio objet (object-based audio) : position 3D + métadonnées de rendu (Atmos, MPEG-H)
- Room acoustics modeling : réverbération par convolution, FDN, ray-tracing
- Audio 6DoF (Six Degrees of Freedom) — rotation et translation, listening zones

### 5. Multimédia Distribué

- **Architectures client-serveur et P2P** pour diffusion multimédia
- **CDN (Content Delivery Networks)** — Akamai, CloudFront, Fastly, edge computing
- **Traitements distribués** — MapReduce pour transcodage, GPU cluster pour rendu
- **Cache et proxy** — segment caching, predictive prefetching, LRU/LFU
- **Load balancing** — répartition de charge serveur, DNS-based, anycast
- **Edge computing** — traitement au plus proche de l'utilisateur (MEC, fog computing)
- **Blockchain et multimedia** — droits numériques (DRM), traçabilité de contenu
- **Multicast** — IP multicast, IGMP, PIM, ALM (Application Layer Multicast)
- **Cloud gaming** — GeForce Now, Stadia, Xbox Cloud Gaming, latence critique

### 6. Qualité d'Expérience et Qualité de Service (QoE/QoS)

**Métriques objectives :**
- **SSIM (Structural Similarity Index)** — luminance, contraste, structure ; MSSIM, SSIMplus
- **VMAF (Video Multimethod Assessment Fusion)** — Netflix, fusion VIF + DLM + motion, modèles SVM
- **PSNR** — rapport signal/bruit de crête, YUV-PSNR, PSNR-HVS
- **VIF (Visual Information Fidelity)** — fidélité informationnelle visuelle
- **MS-SSIM** — SSIM multi-échelle pour corrélation perceptuelle améliorée
- **PESQ (Perceptual Evaluation of Speech Quality)** — ITU-T P.862, évaluation audio perceptuelle
- **POLQA (Perceptual Objective Listening Quality Assessment)** — ITU-T P.863, successeur de PESQ
- **ViSQOL** — évaluation objective de qualité audio/vidéo
- **STOI (Short-Time Objective Intelligibility)** — intelligibilité de la parole

**Standards ITU-T :**
- **ITU-T P.1203** — modèle de qualité de streaming vidéo, régressif vs paramétrique
- **ITU-T P.1204** — modèles ML-based pour qualité vidéo
- **ITU-T P.800** — évaluation subjective de la qualité vocale (ACR, DCR, CCR)
- **ITU-T P.910** — évaluation subjective de la qualité vidéo
- **ITU-T P.913** — méthodes pour évaluation subjective de vidéo sur mobile

**Évaluation subjective :**
- Protocoles ACR, DCR, SSCQE, DSIS, SAMVIQ
- Crowdsourcing de qualité (Amazon Mechanical Turk, Toloka)
- Méthodes de déploiement : labo contrôlé, domicile, mobile
- Analyse statistique : MOS (Mean Opinion Score), intervalles de confiance
- ANOVA, corrélation Pearson/Spearman, RMSE, OR (Outlier Ratio)

### 7. Streaming VR/AR

**Streaming immersif :**
- **360° video streaming** — projection équirectangulaire, cubemap, ERP, EAP
- **6DoF (Six Degrees of Freedom)** — translation + rotation spatiale, navigation libre
- **Tile-based streaming** — découpage en tuiles, sélection par viewport
- **Foveated rendering** — résolution variable selon le focus visuel (ocular, foveal, peripheral layers)
- **Viewport prediction** — prédiction de la direction du regard par CNN/RNN
- **Volumetric video** — nuages de points, voxels, geometry-based streaming
- **Light field streaming** — champs lumineux, plénoptique
- **MPEG-I (Immersive)** — ISO/IEC 23090 : OMAF (Omnidirectional Media Format), V3C (Visual Volumetric Video-based Coding)
- **Point cloud compression** — MPEG V-PCC, G-PCC (Geometry-based PCC)
- **Haptic feedback** — retour tactile, kinesthésique, rendu vibrotactile

**Concepts avancés :**
- Latence MTP (Motion-to-Photon) < 20ms pour éviter le motion sickness
- Asynchronous timewarp / spacewarp — interpolation d'images pour fluidité
- Reprojection 6DoF — correction de pose post-rendu
- Réseau 5G/6G pour VR — URLLC (Ultra-Reliable Low-Latency Communications)
- Split rendering : rendu partagé entre serveur et casque VR

### 8. Métadonnées MPEG-7 et MPEG-21

**MPEG-7 (ISO/IEC 15938) — Description du contenu multimédia :**
- Descripteurs visuels : couleur (DCD, SCD, CLD, CSD), texture (HTD, TTD, EDGE), forme (RSD, SSD, 3DSD), mouvement (MTD, CTD)
- Descripteurs audio : spectral (SC, SS, SF), timbral (harmonic, percussive), speech (LSF, SSD)
- Schémas de description (DS) : segment, région, frame, video/audio decomposition
- DDL (Description Definition Language) — basé sur XML Schema
- Query format : MPEG-7 Query Format (QF) pour recherche multimédia

**MPEG-21 (ISO/IEC 21000) — Cadre multimédia :**
- DID (Digital Item Declaration) : déclaration d'items numériques
- DIA (Digital Item Adaptation) : adaptation contextuelle aux terminaux et réseaux
- REL (Rights Expression Language) : gestion des droits numériques (DRM)
- IPMP (Intellectual Property Management and Protection) : protection de propriété intellectuelle
- Event Reporting : suivi des événements de consommation
- Media Contract Ontology : modélisation des contrats média

### 9. Systèmes de Conférence

- **Audio conferencing** : AEC (Acoustic Echo Cancellation), AGC, VAD, NS (Noise Suppression), mixage de flux audio
- **Video conferencing** : MCU (Multipoint Control Unit), SFU (Selective Forwarding Unit), cascading
- **WebRTC-based conferencing** : serveurs TURN/STUN, simulcast, SVC, bandwidth estimation (GCC, REMB, transport-cc)
- **Standards** : SIP/SDP, H.323, H.264 SVC, BFCP (far-end camera control)
- **Screen sharing** : codage d'écran (H.264/AVC avec intra-frame périodique), VNC, RDP
- **VAD (Voice Activity Detection)** — détection de parole active, gestion de mixage
- **Noise suppression** — débruitage temps réel par RNNoise, Krisp, DeepFilterNet
- **Salles immersives** : caméras panoramiques, beamforming microphonique, speaker tracking

### 10. Synchronisation Inter-Média

- **Synchronisation lip-sync (labial)** : alignement audio-vidéo, fenêtre de tolérance < 80ms
- **Skew inter-flux** : décalage temporel entre flux (audio/vidéo/sous-titres)
- **Inter-destination media synchronization (IDMS)** — synchronisation entre récepteurs multiples (Multi-View, social TV)
- **RTP/RTCP** : timestamps RTP, RTCP SR (Sender Report) pour synchronisation inter-flux
- **NTP-based synchronization** — horloge réseau pour alignement multi-terminal
- **Media timelines** : SMPTE timecode, Presentation Timestamp (PTS), composition units
- **Group synchronization** : scénarios multi-écran, second screen, companions devices
- **Haploche** : retard temporel entre plusieurs systèmes de lecture
- **Video wall synchronization** : synchronisation d'affichages multiples par genlock/frame lock

## Catégories arXiv

- `cs.MM` — Multimedia
- `cs.NI` — Networking and Internet Architecture
- `eess.IV` — Image and Video Processing
- `eess.AS` — Audio and Speech Processing
- `cs.CV` — Computer Vision and Pattern Recognition
- `cs.LG` — Machine Learning
- `cs.GR` — Graphics
- `cs.IR` — Information Retrieval
- `cs.HC` — Human-Computer Interaction
- `cs.SD` — Sound
- `cs.IT` — Information Theory

## Articles Notables

| Article | Domaine |
|---------|---------|
| DASH: Dynamic Adaptive Streaming over HTTP (ISO/IEC 23009-1) | Streaming adaptatif DASH |
| AV1 Bitstream & Decoding Process (AOMedia) | Codage vidéo AV1 |
| VVC (H.266) : Versatile Video Coding (ISO/IEC 23090-3) | Codage vidéo VVC |
| Opus: Interactive Audio Codec (IETF RFC 6716) | Codage audio Opus |
| VMAF: Video Multimethod Assessment Fusion (Netflix) | Évaluation QoE/VMAF |
| ITU-T P.1203 (Parametric bitstream-based quality assessment) | QoE streaming vidéo |
| OMAF: Omnidirectional Media Format (MPEG-I 23090-2) | Streaming VR 360° |
| WebRTC: Web Real-Time Communication (W3C/IETF) | Conférence temps réel |
| EnCodec: High Fidelity Neural Audio Compression (Meta) | Codage audio neuronal |
| 3D Gaussian Splatting for Real-Time Radiance Field Rendering | Rendu immersif 3D |
| Neural Rate-Distortion Compression (Ballé et al.) | Compression vidéo neuronale |
| BOLA: Near-Optimal Bitrate Adaptation for Online Videos (Spiteri et al.) | Adaptation ABR |
| Foveated Rendering: A Survey (Patney et al.) | Rendu fovéal VR |
| MPEG-7: Multimedia Content Description Interface | Métadonnées multimédia |
| MPEG-21: Multimedia Framework | Gestion de droits et adaptation |

## Utilisation

### Recherche hebdomadaire
```bash
# Codage vidéo / compression
arxiv_search query="video coding VVC AV1 neural compression" categories=cs.MM,eess.IV max_results=10

# Streaming adaptatif / DASH / HLS
arxiv_search query="adaptive bitrate ABR streaming DASH CMAF" categories=cs.MM,cs.NI max_results=10

# QoE / qualité vidéo
arxiv_search query="VMAF SSIM video quality assessment QoE" categories=cs.MM,eess.IV max_results=10

# Streaming VR / AR immersif
arxiv_search query="360 video omnidirectional streaming tiled viewport VR" categories=cs.MM,cs.GR max_results=10

# Audio spatial / codage audio
arxiv_search query="spatial audio Ambisonics neural audio codec" categories=cs.MM,eess.AS max_results=10

# WebRTC / conférence
arxiv_search query="WebRTC video conferencing SFU MCU real-time communication" categories=cs.MM,cs.NI max_results=10

# Métadonnées MPEG-7/MPEG-21
arxiv_search query="MPEG-7 MPEG-21 multimedia description metadata" categories=cs.MM,cs.IR max_results=10
```

### Veille continue
- Surveiller `cs.MM` quotidiennement pour les nouvelles soumissions en codage vidéo, streaming et QoE
- Suivre les conférences : ACM Multimedia (MM), IEEE ICME, ACM MMSys, VCIP, PCS, DCC, ICASSP, ISM
- Consulter les groupes MPEG (ISO/IEC JTC 1/SC 29) pour les nouveaux standards (VVC, EVC, MPEG-I)
- Suivre les laboratoires : Netflix (VMAF, per-title), Meta (AV1, neural codecs), Apple (HLS, HEVC), Google (VP9, AV1, WebRTC)
- Configurer des alertes pour : "VVC", "neural video compression", "360 video streaming", "viewport prediction", "point cloud compression", "audio coding", "spatial audio"
- Surveiller les implémentations open source : FFmpeg, x264/x265/x266, libaom-av1, Dav1d, GPAC, SRS, OWT

## Mise à Jour

Cette compétence doit être mise à jour mensuellement avec les nouveaux standards de codage (VVC profiles, AV2, ECM), les avancées en compression neuronale vidéo et audio, les nouveaux modèles d'ABR et de QoE, les évolutions du streaming immersif (MPEG-I, 6DoF), et les innovations dans les systèmes de conférence et de téléprésence.
