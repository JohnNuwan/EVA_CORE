---
name: yolo-detection
description: Détection d'objets avec YOLO (You Only Look Once) — YOLOv5 à YOLOv11, Ultralytics, entraînement, export, inférence, benchmarks, et pipelines. En français.

---

# Détection d'Objets — YOLO (You Only Look Once)

Famille YOLO : détection temps réel la plus populaire. De YOLOv5 (Ultralytics) à YOLOv11, en passant par YOLOv8, YOLO-NAS et YOLO-World.

---

## 1. Architecture Fondamentale

### Principe
```
Image complète → Grille (S×S) → Chaque cellule prédit :
  - Bounding boxes (x, y, w, h, confiance)
  - Scores de classe (C probabilités)
```

### Évolution des architectures
| Version | Année | Backbone | Head | AP50-95 (COCO) | FPS (T4) |
|---------|-------|----------|------|----------------|----------|
| YOLOv3  | 2018  | Darknet53 | FPN  | 33.0           | 35       |
| YOLOv5  | 2020  | CSPDarknet | PANet | 50.7          | 140      |
| YOLOv8  | 2023  | CSPDarknet | C2f  | 53.3           | 220      |
| YOLOv9  | 2024  | GELAN    |     | 55.6           | 200      |
| YOLOv10 | 2024  | ELAN     | NMS-free | 55.5        | 230      |
| YOLOv11 | 2025  |         |      | 56.0+          | 250+     |

---

## 2. Installation et Setup

```bash
# Ultralytics (YOLOv5, v8, v9, v10, v11)
pip install ultralytics

# YOLOv5 original
git clone https://github.com/ultralytics/yolov5
cd yolov5 && pip install -r requirements.txt

# YOLOv6 (Meituan)
pip install yolov6

# YOLO-NAS (Deci AI)
pip install super-gradients
```

### Export ONNX/TensorRT

```bash
# ONNX
yolo export model=yolo11n.pt format=onnx

# TensorRT
yolo export model=yolo11n.pt format=engine device=0

# OpenVINO
yolo export model=yolo11n.pt format=openvino

# CoreML (Apple)
yolo export model=yolo11n.pt format=coreml
```

---

## 3. Modèles et Prétentraînés

```python
from ultralytics import YOLO

# Nano (rapide, mobile)
model = YOLO("yolo11n.pt")       # Nano  ~2.6M params
model = YOLO("yolo11s.pt")       # Small ~9.4M params

# Medium (bon équilibre)
model = YOLO("yolo11m.pt")       # Medium ~20.1M params

# Large (haute précision)
model = YOLO("yolo11l.pt")       # Large  ~25.3M params
model = YOLO("yolo11x.pt")       # XLarge ~56.9M params

# Tâches spécialisées
model = YOLO("yolo11n-seg.pt")   # Segmentation
model = YOLO("yolo11n-pose.pt")  # Pose estimation
model = YOLO("yolo11n-obb.pt")   # Oriented Bounding Boxes
model = YOLO("yolo11n-cls.pt")   # Classification
```

---

## 4. Inférence

```python
from ultralytics import YOLO
import cv2

model = YOLO("yolo11x.pt")

# Sur image
results = model("image.jpg")

# Sur vidéo
results = model("video.mp4", stream=True)  # Stream = générateur

# Sur webcam
results = model(0, stream=True)

# Avec options
results = model(
    "image.jpg",
    conf=0.25,        # Seuil de confiance
    iou=0.45,         # Seuil NMS IoU
    imgsz=640,        # Taille d'entrée
    max_det=300,      # Max détections
    device="cuda:0",  # GPU
    half=True,        # FP16
    agnostic_nms=True,# NMS agnostique aux classes
    classes=[0, 2],   # Filtrer par classe (personne, voiture)
)

# Résultats
for result in results:
    boxes = result.boxes                     # Boîtes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]        # Coordonnées
        conf = float(box.conf[0])            # Confiance
        cls = int(box.cls[0])                # Classe
        label = result.names[cls]            # Nom de la classe

    # Masques (segmentation)
    if result.masks:
        for mask in result.masks.data:
            # Masque binaire (H, W)
            pass

    # Keypoints (pose)
    if result.keypoints:
        for kpts in result.keypoints.data:
            # kpts: (17, 3) pour COCO keypoints
            pass

    # Image annotée
    annotated = result.plot()                # Image avec boîtes
    annotated = result.plot(line_width=2, font_size=10, conf=True)
```

### Détection et Tracking

```python
# Tracking (ByteTrack par défaut)
results = model.track("video.mp4", persist=True, tracker="bytetrack.yaml")

# Boîtes avec ID
for result in results:
    for box in result.boxes:
        track_id = int(box.id[0]) if box.id is not None else None
```

---

## 5. Entraînement Personnalisé

### Format de Dataset (COCO / YOLO)

```
dataset/
├── images/
│   ├── train/    # 80% des images
│   └── val/      # 20% des images
├── labels/
│   ├── train/    # Fichiers .txt (1 par image)
│   └── val/      # Fichiers .txt (1 par image)
└── dataset.yaml  # Config
```

**Format label YOLO** (1 ligne par objet) :
```
<class_id> <x_center> <y_center> <width> <height>
```
Toutes les valeurs normalisées [0, 1] par rapport à la taille de l'image.

**dataset.yaml** :
```yaml
path: /path/to/dataset
train: images/train
val: images/val

nc: 3
names: ['personne', 'voiture', 'vélo']
```

### Lancement de l'Entraînement

```python
from ultralytics import YOLO

model = YOLO("yolo11m.pt")  # Pré-entraîné COCO

results = model.train(
    data="dataset.yaml",
    epochs=300,
    patience=50,           # Early stopping
    batch=16,
    imgsz=640,
    
    # Optimisation
    optimizer="AdamW",
    lr0=0.001,             # Learning rate initial
    lrf=0.01,              # LR final = lr0 * lrf
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    warmup_momentum=0.8,
    warmup_bias_lr=0.1,
    
    # Augmentation
    hsv_h=0.015,           # Hue
    hsv_s=0.7,             # Saturation
    hsv_v=0.4,             # Value
    degrees=0.0,           # Rotation
    translate=0.1,         # Translation
    scale=0.5,             # Scale
    shear=0.0,             # Shear
    perspective=0.0,       # Perspective
    flipud=0.0,            # Flip vertical
    fliplr=0.5,            # Flip horizontal
    mosaic=1.0,            # Mosaic augmentation
    mixup=0.0,             # Mixup
    copy_paste=0.0,        # Copy-paste
    
    # Régularisation
    dropout=0.0,
    label_smoothing=0.0,
    
    # Infrastructure
    device="cuda:0",       # GPU
    workers=8,
    project="yolo_project",
    name="experiment_1",
    exist_ok=True,
    pretrained=True,
    resume=False,
    
    # Validation
    val=True,
    plots=True,
    save_period=10,
)
```

### Résumé et Suivi

```python
# Résultats accessibles
results = model.train(...)
print(results.results_dict)  # {'metrics/precision(B)': 0.92, ...}
print(results.best)           # Chemin vers le meilleur modèle

# Wandb
model.train(..., project="mon_projet", name="mon_exp", exist_ok=True)

# TensorBoard
# Les logs sont dans runs/detect/exp/
```

---

## 6. Fine-Tuning et Transfer Learning

```python
# Geler les couches du backbone
model = YOLO("yolo11m.pt")
model.model.model[0].requires_grad_(False)  # Geler le backbone

# Ou geler les N premières couches
for i, layer in enumerate(model.model.model[:10]):
    layer.requires_grad_(False)

# Fine-tune seulement la tête de détection
model.train(
    data="dataset.yaml",
    epochs=100,
    freeze=10,  # Geler les 10 premières couches
)

# Learning rate plus bas pour le fine-tuning
model.train(
    data="dataset.yaml",
    epochs=100,
    lr0=0.0001,  # 10x plus bas que pour un entraînement complet
    warmup_epochs=1,
)
```

---

## 7. Export et Déploiement

```python
# Charger le meilleur modèle
model = YOLO("runs/detect/exp/weights/best.pt")

# Exports
model.export(format="onnx")          # ONNX
model.export(format="engine")        # TensorRT
model.export(format="openvino")      # OpenVINO
model.export(format="coreml")        # CoreML
model.export(format="tflite")        # TFLite
model.export(format="tfjs")          # TensorFlow.js
model.export(format="torchscript")   # TorchScript

# TensorRT avec optimisation
model.export(
    format="engine",
    half=True,           # FP16
    int8=False,          # INT8
    dynamic=True,        # Shape dynamique
    batch=1,
    workspace=4,         # GB
)
```
```

### Inférence avec ONNX Runtime

```python
import onnxruntime as ort
import numpy as np
import cv2

# Charger
session = ort.InferenceSession("model.onnx")
input_name = session.get_inputs()[0].name

# Prétraitement
img = cv2.imread("image.jpg")
img = cv2.resize(img, (640, 640))
img = img.transpose(2, 0, 1)  # HWC → CHW
img = np.expand_dims(img, axis=0).astype(np.float32)
img /= 255.0

# Inférence
outputs = session.run(None, {input_name: img})

# Post-traitement (décodage des boîtes YOLO)
# output[0] shape: (1, 84, 8400) pour YOLOv8
```

---

## 8. YOLO-World (Zero-shot)

```python
from ultralytics import YOLO

# Modèle zero-shot
model = YOLO("yolo_world_v2_xl_vlms.pt")

# Détection avec prompts texte
results = model.predict("image.jpg", text=["personne", "casque", "extincteur"])

# OU définir les classes
model.set_classes(["voiture rouge", "camion bleu", "piéton"])
results = model("image.jpg")
```

---

## 9. OBB (Oriented Bounding Boxes)

```python
# YOLOv8 OBB pour objets orientés (aérien, satellite)
model = YOLO("yolo11n-obb.pt")

# Entraînement
model.train(data="dota8.yaml", epochs=100)

# Inférence
results = model("image_aerienne.jpg")
for result in results:
    obb = result.obb
    for box in obb:
        # xywhr: x, y, w, h, rotation (radians)
        x, y, w, h, r = box.xywhr[0]
```

---

## 10. Métriques et Évaluation

```python
# Validation après entraînement
model = YOLO("best.pt")
metrics = model.val(
    data="dataset.yaml",
    batch=16,
    imgsz=640,
    conf=0.001,
    iou=0.6,
)

# Métriques
print(metrics.box.map)          # mAP@50-95
print(metrics.box.map50)        # mAP@50
print(metrics.box.map75)        # mAP@75
print(metrics.box.maps)         # mAP par classe

# Matrice de confusion
print(metrics.confusion_matrix)
```

### Benchmarks

```bash
# Benchmark YOLO sur GPU
yolo benchmark model=yolo11n.pt imgsz=640 device=0

# Résultat typique :
# YOLO11n : 640x640, 39.5 mAP, 1.5ms, 6.3 GFLOPs
# YOLO11s : 640x640, 47.0 mAP, 2.5ms, 21.5 GFLOPs
# YOLO11m : 640x640, 51.5 mAP, 4.7ms, 68.0 GFLOPs
# YOLO11l : 640x640, 53.4 mAP, 6.2ms, 86.9 GFLOPs
# YOLO11x : 640x640, 54.7 mAP, 11.3ms, 194.9 GFLOPs
```

---

## 11. Intégration Pipeline

```python
import cv2
from ultralytics import YOLO
from collections import defaultdict
import numpy as np

class DetectionPipeline:
    def __init__(self, model_path="yolo11x.pt", conf=0.25):
        self.model = YOLO(model_path)
        self.conf = conf
        self.track_history = defaultdict(list)
    
    def process_frame(self, frame, track=False):
        if track:
            results = self.model.track(frame, conf=self.conf, persist=True)
        else:
            results = self.model(frame, conf=self.conf)
        
        detections = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                det = {
                    "bbox": box.xyxy[0].tolist(),
                    "conf": float(box.conf[0]),
                    "class": int(box.cls[0]),
                    "label": result.names[int(box.cls[0])],
                }
                if box.id is not None:
                    det["track_id"] = int(box.id[0])
                detections.append(det)
        
        return detections, results[0].plot() if results else frame
    
    def process_video(self, video_path, output_path=None):
        cap = cv2.VideoCapture(video_path)
        out = None
        if output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            detections, annotated = self.process_frame(frame, track=True)
            if out:
                out.write(annotated)
        
        cap.release()
        if out:
            out.release()
```

---

## 12. Problèmes Courants et Solutions

| Problème | Cause | Solution |
|----------|-------|----------|
| Overfitting | Dataset trop petit | Augmentation, dropout, pretrained léger |
| Underfitting | Pas assez d'epochs | Augmenter epochs, réduire patience |
| Faux positifs | Seuil conf trop bas | Augmenter conf à 0.5+ |
| Objets manqués | Occlusion | Augmenter imgsz, mosaïque |
| Performances GPU | Batch size | Ajuster, utiliser half=True |
| Précision faible | Annotation incorrectes | Vérifier les labels, labelliser proprement |
| RAM insuffisante | Trop d'images | Réduire batch, workers |

---

## Références
- Ultralytics Docs : https://docs.ultralytics.com/
- YOLO GitHub : https://github.com/ultralytics/ultralytics
- YOLOv5 : https://github.com/ultralytics/yolov5
- Roboflow Universe : https://universe.roboflow.com/
- Papers With Code : https://paperswithcode.com/task/object-detection