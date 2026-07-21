---
name: video-analysis
description: Analyse vidéo — reconnaissance d'actions, pose estimation, video understanding, I3D, VideoMAE, TimeSformer, X3D, SlowFast, MediaPipe, Pose, OpenPose, VAD. En français.

---

# Analyse Vidéo — Actions, Pose, Compréhension Vidéo

Vision vidéo : reconnaître des actions, estimer des poses humaines, comprendre des séquences temporelles. Du classique (optical flow) aux transformers spatio-temporels (VideoMAE, TimeSformer).

---

## 1. Taxonomie de l'Analyse Vidéo

```
Analyse Vidéo
├── Reconnaissance d'Actions
│   ├── Two-Stream (RGB + Optical Flow)    — I3D, Two-Stream
│   ├── 3D CNNs                             — C3D, I3D, X3D
│   ├── Video Transformers                  — TimeSformer, VideoMAE
│   └── Efficient (Mobile)                  — X3D, TSM
│
├── Pose Estimation Humaine
│   ├── Top-Down                            — HRNet, ViTPose
│   ├── Bottom-Up                           — OpenPose, DEKR
│   └── Lightweight                         — MediaPipe, MoveNet
│
├── Détection d'Anomalies Vidéo
│   ├── Reconstruction                      — AE, VAE, videoMAE
│   └── Prédiction                          — Future frame prediction
│
└── Video Understanding
    ├── Video Captioning                    — Texte → vidéo
    ├── Video QA                            — Questions sur vidéo
    └── Temporal Action Detection (TAD)     — Où/quand/quelles actions
```

---

## 2. Reconnaissance d'Actions

### I3D (Inflated 3D ConvNets)

```python
import torch
import torch.nn as nn

class InceptionI3D(nn.Module):
    """I3D : Inflated 3D Inception (pré-entraîné ImageNet inflaté vers vidéo)"""
    def __init__(self, num_classes=400):
        super().__init__()
        # Architecture : InceptionV1 3D-inflaté
        # (remplace 2D Conv par 3D Conv)
        
        # Entrée : (B, 3, T, H, W) — T = 64 frames
        self.conv1 = nn.Conv3d(3, 64, kernel_size=(7, 7, 7), stride=(2, 2, 2), padding=(3, 3, 3))
        
    def forward(self, x):
        # x.shape = (B, 3, T, H, W)
        return self.features(x)

# Utilisation
# pip install pytorchvideo
from pytorchvideo.models import hub

# Modèles pré-entraînés Kinetics-400
i3d = hub.i3d_r50(pretrained=True)          # I3D ResNet50
slowfast = hub.slowfast_r50(pretrained=True)  # SlowFast
x3d_xs = hub.x3d_xs(pretrained=True)          # X3D XS (léger)
x3d_m = hub.x3d_m(pretrained=True)            # X3D Medium

# SlowFast
model = slowfast.eval().cuda()
# Entrée : (B, 3, T, H, W) avec T = 32-64 frames
```

### X3D (Expanding 3D Networks)

```python
# X3D : Efficient Video Networks
# Extensible en profondeur/largeur/résolution/temporalité

# Modèles X3D (taille croissante)
x3d_xs = hub.x3d_xs(pretrained=True)  # 6.15M, 4.17 GFLOPs
x3d_s  = hub.x3d_s(pretrained=True)   # 7.66M, 8.91 GFLOPs
x3d_m  = hub.x3d_m(pretrained=True)   # 13.7M, 29.3 GFLOPs
x3d_l  = hub.x3d_l(pretrained=True)   # 23.7M, 86.4 GFLOPs

# X3D : meilleur rapport précision/vitesse
# Kinetics-400 : X3D-M = 79.4%, X3D-L = 81.6%
```

### TimeSformer (Video Transformer)

```python
# TimeSformer : Divided Space-Time Attention
# Attention séparée : spatiale puis temporelle

# pip install timesformer
from timesformer.models.vit import TimeSformer

model = TimeSformer(
    img_size=224,
    patch_size=16,
    num_classes=400,
    num_frames=8,          # 8 frames suffisent
    attention_type='divided_space_time',
    pretrained_model='TimeSformer_divST_8x32_224_K400.pyth',
)

# Variantes d'attention :
# - divided_space_time : attention spatiale + temporelle (efficace)
# - space_only : seulement spatiale
# - joint_space_time : conjointe (coûteuse)
```

### VideoMAE (Masked Autoencoders Video)

```python
# VideoMAE : Masked Autoencoding pour vidéo
# Masque 90% des patches vidéo, reconstruit les patches manquants
from transformers import VideoMAEForVideoClassification, VideoMAEImageProcessor

processor = VideoMAEImageProcessor.from_pretrained("MCG-NJU/videomae-base-finetuned-kinetics")
model = VideoMAEForVideoClassification.from_pretrained(
    "MCG-NJU/videomae-base-finetuned-kinetics"
)

# Entrée : 16 frames
inputs = processor(list(video_frames[:16]), return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits
predicted_class = logits.argmax(-1).item()
```

---

## 3. Pose Estimation Humaine

### MediaPipe (Lightweight, Temps Réel)

```python
import mediapipe as mp

# Pose (33 landmarks)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=True,
    model_complexity=2,        # 0=léger, 1=full, 2=heavy
    enable_segmentation=True,
    min_detection_confidence=0.5,
)

results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

if results.pose_landmarks:
    for idx, landmark in enumerate(results.pose_landmarks.landmark):
        # idx 0-32 : 33 landmarks
        # 0=nez, 11-12=épaules, 13-16=coudes/poignets
        # 23-24=hanches, 25-28=genoux/chevilles
        h, w, _ = frame.shape
        x, y = int(landmark.x * w), int(landmark.y * h)
        cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

# Hands (21 landmarks)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)

# Face Mesh (468 landmarks)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1)

# Holistic (Pose + Hands + Face)
mp_holistic = mp.solutions.holistic
holistic = mp_holistic.Holistic(min_detection_confidence=0.5)
```

### OpenPose (Multi-Person)

```python
# OpenPose : Bottom-Up (Part Affinity Fields)
# Détecte les keypoints de TOUTES les personnes en une passe

# pip install opencv-python openpose (depuis source)

# Clé OpenPose : PAF (Part Affinity Fields)
# Carte vectorielle qui encode l'association entre les keypoints
# ex : coude → poignet

# Format COCO keypoints (17)
# 0=nez, 1=ceil_g, 2=ceil_d, 3=oreille_g, 4=oreille_d,
# 5=épaule_g, 6=épaule_d, 7=coude_g, 8=coude_d,
# 9=poignet_g, 10=poignet_d, 11=hanche_g, 12=hanche_d,
# 13=genou_g, 14=genou_d, 15=cheville_g, 16=cheville_d
```

### ViTPose (Vision Transformer Pose)

```python
# ViTPose : State-of-the-Art (ViT pour pose estimation)
# Top-Down : détecte les personnes, puis estime leur pose

from transformers import VitPoseForPoseEstimation

model = VitPoseForPoseEstimation.from_pretrained("ViTPose-base")
# Top-1 AP sur COCO : 75.8 (base), 78.5 (large)

# HRNet (CNN alternative)
# pip install torchvision
# HRNet-W48 : 76.3 AP sur COCO
```

---

## 4. Pipeline Vidéo Complet

```python
import cv2
import torch
import numpy as np
from collections import deque

class VideoActionDetector:
    """Détection d'actions en temps réel avec sliding window"""
    def __init__(self, model, num_frames=16, stride=4):
        self.model = model.eval().cuda()
        self.num_frames = num_frames
        self.stride = stride
        self.frame_buffer = deque(maxlen=num_frames)
        self.transform = ...  # Transformations vidéo
    
    def process_frame(self, frame):
        # Ajouter au buffer
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.frame_buffer.append(frame_rgb)
        
        if len(self.frame_buffer) < self.num_frames:
            return None, frame
        
        # Échantillonner le buffer
        indices = np.linspace(0, len(self.frame_buffer)-1, self.num_frames, dtype=int)
        clip = [self.frame_buffer[i] for i in indices]
        
        # Prétraitement
        clip_tensor = self.transform(clip).unsqueeze(0).cuda()
        
        # Inférence
        with torch.no_grad():
            logits = self.model(clip_tensor)
            probs = torch.softmax(logits, dim=1)
            top_k = torch.topk(probs, k=3, dim=1)
        
        return top_k, frame

# Utilisation
cam = cv2.VideoCapture(0)
detector = VideoActionDetector(model, num_frames=16, stride=4)
while True:
    ret, frame = cam.read()
    predictions, annotated = detector.process_frame(frame)
    if predictions:
        for i in range(3):
            cls = predictions.indices[0][i].item()
            prob = predictions.values[0][i].item()
            label = f"{class_names[cls]}: {prob:.2f}"
            cv2.putText(annotated, label, (10, 30 + i*30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.imshow("Video Analysis", annotated)
```

---

## 5. Détection d'Anomalies Vidéo (VAD)

```python
import torch
import torch.nn as nn

class VideoAnomalyDetector(nn.Module):
    """
    Détection d'anomalies par prédiction de frame future.
    Une grande erreur de reconstruction = anomalie.
    """
    def __init__(self):
        super().__init__()
        # Encodeur spatio-temporel
        self.encoder = nn.Sequential(
            nn.Conv3d(3, 64, 3, 1, 1),
            nn.ReLU(),
            nn.MaxPool3d((1, 2, 2)),
            nn.Conv3d(64, 128, 3, 1, 1),
            nn.ReLU(),
            nn.MaxPool3d((2, 2, 2)),
            nn.Conv3d(128, 256, 3, 1, 1),
            nn.ReLU(),
        )
        # Décodeur
        self.decoder = nn.Sequential(
            nn.ConvTranspose3d(256, 128, 3, 1, 1),
            nn.ReLU(),
            nn.ConvTranspose3d(128, 64, 3, 1, 1),
            nn.ReLU(),
            nn.ConvTranspose3d(64, 3, 3, 1, 1),
            nn.Sigmoid(),
        )
    
    def forward(self, x):
        return self.decoder(self.encoder(x))
    
    def anomaly_score(self, x, reconstructed):
        # PSNR-like
        mse = F.mse_loss(x, reconstructed, reduction='none')
        score = mse.mean(dim=[1, 2, 3, 4])  # (B,)
        return score  # Plus haut = plus anormal

# Seuil : score > μ + 3σ → anomalie
```

---

## 6. Temporal Action Detection (TAD)

```python
# Détection temporelle : quand commence/finit une action dans la vidéo

# ActionFormer (SOTA TAD)
# pip install git+https://github.com/happy-lhq/actionformer

# Format : [t_start, t_end, class_id, score]

# Exemple de post-traitement TAD
def nms_temporal(proposals, iou_threshold=0.5):
    """Non-Maximum Suppression temporel"""
    proposals = sorted(proposals, key=lambda x: x[3], reverse=True)
    kept = []
    while proposals:
        best = proposals.pop(0)
        kept.append(best)
        proposals = [
            p for p in proposals
            if temporal_iou(best[:2], p[:2]) < iou_threshold
        ]
    return kept

def temporal_iou(a, b):
    """IoU temporel entre deux segments [t1, t2]"""
    inter = max(0, min(a[1], b[1]) - max(a[0], b[0]))
    union = max(a[1], b[1]) - min(a[0], b[0])
    return inter / union if union > 0 else 0
```

---

## 7. Datasets Vidéo

| Dataset | Clips | Classes | Tâche |
|---------|-------|---------|-------|
| Kinetics-400 | 300k | 400 | Action |
| Kinetics-700 | 650k | 700 | Action |
| UCF-101 | 13k | 101 | Action |
| HMDB-51 | 7k | 51 | Action |
| Something-Something v2 | 220k | 174 | Action fine |
| AVA | 430k | 80 | Action + localisation |
| Charades | 10k | 157 | Action maison |
| COCO Keypoints | 250k | 17 | Pose |
| MPII Human Pose | 25k | 16 | Pose |
| Penn Action | 2.3k | 15 | Pose action |

---

## 8. Optical Flow

```python
import cv2
import numpy as np

# Farneback (OpenCV)
prev_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
curr_gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

flow = cv2.calcOpticalFlowFarneback(
    prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0,
)
# flow.shape = (H, W, 2) → (dx, dy)

# Visualisation
mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
hsv = np.zeros((flow.shape[0], flow.shape[1], 3), dtype=np.uint8)
hsv[..., 0] = ang * 180 / np.pi / 2          # Teinte = direction
hsv[..., 1] = 255                             # Saturation
hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)  # Valeur = magnitude
flow_vis = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# RAFT (Deep Learning)
# pip install raft-pytorch
# raft = RAFT(args)
# flow = raft(frame1, frame2)
```

---

## 9. Datasets et Préparation

```python
from torch.utils.data import Dataset
import decord  # Lecteur vidéo rapide

class VideoDataset(Dataset):
    """Dataset vidéo optimisé (decord + memmap)"""
    def __init__(self, video_paths, labels, num_frames=32, frame_size=224):
        self.video_paths = video_paths
        self.labels = labels
        self.num_frames = num_frames
        self.frame_size = frame_size
        self.transform = T.Compose([
            T.Resize(frame_size),
            T.CenterCrop(frame_size),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
    
    def __getitem__(self, idx):
        # Decord : chargement rapide de frames
        vr = decord.VideoReader(self.video_paths[idx])
        total_frames = len(vr)
        
        # Uniform sampling
        indices = np.linspace(0, total_frames-1, self.num_frames, dtype=int)
        frames = vr.get_batch(indices).asnumpy()  # (T, H, W, 3)
        
        # Transformation
        frames = torch.stack([self.transform(f) for f in frames])
        # frames.shape = (T, 3, H, W)
        
        return frames.permute(1, 0, 2, 3), self.labels[idx]  # (3, T, H, W)
    
    def __len__(self):
        return len(self.video_paths)
```

---

## 10. Évaluation

```python
# Métriques action
# Top-1 Accuracy
# Top-5 Accuracy
# Mean Per-Class Accuracy

# Métriques pose
# AP (Average Precision) par keypoint
# PCK (Percentage of Correct Keypoints)
# OKS (Object Keypoint Similarity)
# mAP@OKS (COCO)

# Métriques VAD
# AUC ROC
# AUC PR
# FAR / FRR (False Alarm / False Reject)
```

### Benchmarks

| Modèle | Dataset | Métrique | Score |
|--------|---------|----------|-------|
| SlowFast R50 | Kinetics-400 | Top-1 | 79.1% |
| X3D-M | Kinetics-400 | Top-1 | 79.4% |
| TimeSformer-L | Kinetics-400 | Top-1 | 80.7% |
| VideoMAE-H | Kinetics-400 | Top-1 | 86.6% |
| ViTPose-B | COCO | mAP | 75.8 |
| HRNet-W48 | COCO | mAP | 76.3 |
| MediaPipe Pose | COCO | mAP | 69.3 |

---

## Références
- PyTorchVideo : https://pytorchvideo.org/
- MediaPipe : https://mediapipe.dev/
- OpenPose : https://github.com/CMU-Perceptual-Computing-Lab/openpose
- VideoMAE : https://github.com/MCG-NJU/VideoMAE
- TimeSformer : https://github.com/facebookresearch/TimeSformer
- Decord : https://github.com/dmlc/decord
- PapersWithCode : https://paperswithcode.com/task/action-recognition