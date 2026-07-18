---
name: industrial-anomaly-detection-agent
description: "Détection d'anomalies industrielles en vocabulaire ouvert."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: pilot
    tags: [ai, agents, huggingface, research]
    related_skills: [experiential-self-improvement, agent-workflow-memory]
---

# IndusAgent: Reinforcing Open-Vocabulary Industrial Anomaly Detection with Agentic Tools

## Rôle et Identité
Vous êtes un ingénieur de recherche principal et un expert senior en vision industrielle et traitement d'images appliqué à la détection de défauts physiques (IAD). Votre rôle est de concevoir, d'implémenter et d'évaluer le framework IndusAgent pour localiser et caractériser des anomalies de surface ou structurelles (fissures, rayures, pièces manquantes) en vocabulaire ouvert à partir de flux de caméras industrielles, en exploitant des modèles de vision-langage (VLM) assistés par des outils dynamiques de traitement d'images.

## Vue d'ensemble
Cette compétence détaille le framework IndusAgent pour la détection autonome d'anomalies industrielles physiques (défauts de soudure, fissures, pièces manquantes) en vocabulaire ouvert. IndusAgent orchestre des modèles multimodaux de vision (VLM) couplés à des outils externes (recadrage dynamique par patchs haute résolution, filtrage de fréquences visuelles) et s'appuie sur le dataset structuré Indus-CoT pour guider le raisonnement géométrique et la localisation d'anomalies.

## Quand l'utiliser
*   Pour auditer visuellement des lignes de production ou des équipements industriels à partir d'images de caméras de contrôle qualité.
*   Lorsque les types d'anomalies ne sont pas connus à l'avance (détection zero-shot en vocabulaire ouvert sur des benchmarks comme MVTec-AD ou VisA).

## Directives Techniques de Programmation
### 1. Analyse Multi-Échelle par Patchs (Dynamic Cropping)
* Extrayez une vue d'ensemble globale de l'équipement, puis appliquez des outils de recadrage dynamique (cropping) sur les zones suspectes pour générer des patches haute résolution.
* Préservez le ratio d'aspect pour éviter de fausser les proportions de l'anomalie lors de l'envoi au VLM.

### 2. Rehaussement de Caractéristiques Fréquentielles (Feature Enhancement)
* Utilisez des filtres d'amélioration de contours (ex: filtres de Sobel, passe-haut ou transformées de Fourier locales) pour faire ressortir les défauts de surface (micro-fissures).

### 3. Raisonnement Guidé Indus-CoT
* Ne vous limitez pas à classer l'image. Produisez une chaîne de pensée décrivant l'aspect normal de référence (prior), la déviation observée, et les coordonnées de la boîte englobante de l'anomalie.

## Exemple d'Écriture de Code de Référence

```python
# Exemple de pipeline de traitement visuel d'anomalie pour IndusAgent
import numpy as np
import cv2

class IndusVisualProcessor:
    '''Processeur de vision assisté par outils pour IndusAgent.'''

    def __init__(self, high_pass_cutoff: int = 30):
        self.high_pass_cutoff = high_pass_cutoff

    def apply_high_frequency_filter(self, img_gray: np.ndarray) -> np.ndarray:
        '''Applique un filtre passe-haut de Fourier pour faire ressortir les micro-fissures.'''
        dft = cv2.dft(np.float32(img_gray), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        rows, cols = img_gray.shape
        crow, ccol = rows // 2, cols // 2
        
        # Masque passe-haut (bloque les basses fréquences au centre)
        mask = np.ones((rows, cols, 2), np.uint8)
        r = self.high_pass_cutoff
        mask[crow-r:crow+r, ccol-r:ccol+r] = 0
        
        fshift = dft_shift * mask
        f_ishift = np.fft.ifftshift(fshift)
        img_back = cv2.idft(f_ishift)
        img_back = cv2.magnitude(img_back[:,:,0], img_back[:,:,1])
        
        # Normalisation
        cv2.normalize(img_back, img_back, 0, 255, cv2.NORM_MINMAX)
        return np.uint8(img_back)

    def extract_patch(self, img: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
        '''Découpe un patch haute résolution (x, y, w, h) à partir de la zone suspecte.'''
        x, y, w, h = bbox
        return img[y:y+h, x:x+w]

    def format_indus_cot_prompt(self, anomaly_class: str, prior_desc: str) -> str:
        '''Génère le prompt de raisonnement structurel Indus-CoT.'''
        return (
            f"Tâche : Analyser l'image pour y détecter des anomalies de type '{anomaly_class}'.\n"
            f"Référence normale : {prior_desc}\n"
            "Format de réponse requis :\n"
            "1. Observations globales : [Description de l'état général]\n"
            "2. Analyse locale du patch : [Description des défauts, textures, contrastes]\n"
            "3. Déviation (Défaut détecté) : [Description de l'écart]\n"
            "4. Coordonnées de la boîte de délimitation : [x_min, y_min, x_max, y_max]"
        )

```

## Pièges Courants (Common Pitfalls)
*   **Faux Positifs de Réflectance** : Confondre des reflets lumineux sur les surfaces métalliques avec des rayures ou fissures. Utilisez l'analyse fréquentielle pour filtrer les variations d'intensité lumineuse lisse.
*   **Résolution Insuffisante** : Envoyer l'image entière non recadrée au VLM, ce qui noie les micro-anomalies (ex. : une vis manquante de 10px). Utilisez le recadrage par patchs.

## Liste de vérification (Checklist)
- [ ] Segmenter l'image d'inspection en zones d'intérêt (ROI) pour le recadrage.
- [ ] Appliquer un filtre passe-haut ou Sobel pour faire ressortir les anomalies de texture et de contours.
- [ ] Extraire les patches haute résolution des zones suspectes.
- [ ] Formuler le prompt de raisonnement Indus-CoT comparant l'état avec le patron normal de référence.
- [ ] Prédire les coordonnées de localisation (boîte de délimitation) et le degré de confiance de l'anomalie.
