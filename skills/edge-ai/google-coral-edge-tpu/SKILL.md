---
name: google-coral-edge-tpu
description: "Google Coral Edge TPU — compilation de modèles (edgetpu-compiler), PyCoral API, inférence accélérée TPU, modèles pipeline (multi-TPU), transfer learning intégré, profiling et déploiement sur Dev Board et USB Accelerator."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - google-coral
      - edge-tpu
      - tpu
      - tensorflow-lite
      - pycoral
      - edgetpu
      - ml-acceleration
      - computer-vision
      - edge-ai
    related_skills:
      - tensorflow-lite-deep-dive
      - model-optimization-edge
      - nvidia-jetson-deployment
---

# Google Coral Edge TPU

## Vue d'ensemble

Le **Google Coral Edge TPU** est un ASIC (Application-Specific Integrated Circuit) dédié à l'inférence de réseaux de neurones sur dispositifs Edge. Il délivre jusqu'à **4 TOPS (Tera-Operations Per Second)** pour seulement **2 W** — un ratio performance/watt imbattable pour la vision par ordinateur temps réel.

### Matériel Coral disponible

| Produit | Interface | Performances | Cas d'usage |
|:--------|:---------|:------------:|:-----------|
| **USB Accelerator** | USB 3.0 (Gen 1) | 4 TOPS | Plug-and-play sur Pi, PC |
| **Dev Board** | Module Système (SoM) | 4 TOPS (+ i.MX8M) | Standalone, full Linux |
| **Dev Board Micro** | MCU + TPU | 4 TOPS (Edge TPU) | Ultra low-power, embarqué |
| **M.2 Accelerator** | M.2 A+E key | 4 TOPS | Intégration serveur/robot |
| **Mini PCIe** | PCIe Gen 2 | 4 TOPS | Applications industrielles |

### Architecture Edge TPU

```
┌─────────────────────────────────────────────┐
│              Hôte (CPU Linux)                │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐  │
│  │ PyCoral  │  │ C++ API  │  │ gstreamer │  │
│  │ (Python) │  │ (libedgetpu)│ │ (video)  │  │
│  └────┬─────┘  └────┬─────┘  └─────┬─────┘  │
│       │              │              │         │
└───────┼──────────────┼──────────────┼─────────┘
        │              │              │
        ▼              ▼              ▼
┌──────────────────────────────────────────────┐
│           Edge TPU (Coral ASIC)              │
│  ┌──────────────────────────────────────┐   │
│  │    8× Systolic Array (MAC units)     │   │
│  │    ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐ ┌──┐  │   │
│  │    │MA│ │MA│ │MA│ │MA│ │MA│ │MA│  │   │
│  │    └──┘ └──┘ └──┘ └──┘ └──┘ └──┘  │   │
│  │      ... (8 PE arrays total)        │   │
│  └──────────────────────────────────────┘   │
│  Mémoire : 8 MB SRAM (interne)              │
│  Poids : chargés en cache SRAM              │
│  Activations : streamed via DDR              │
└──────────────────────────────────────────────┘
```

---

## 1. Compilation de Modèles

### 1.1 Préparation du modèle

```python
# ÉTAPE CRITIQUE : le modèle DOIT être en TFLite INT8 quantifié
# L'Edge TPU ne supporte QUE INT8 (poids et activations)
# Pas de FP32, pas de FP16 !

import tensorflow as tf
import numpy as np

def preparer_modele_coral(model_path: str, calib_data: np.ndarray):
    """Prépare un modèle Keras pour la compilation Coral."""
    
    model = tf.keras.models.load_model(model_path)
    
    # Conversion TFLite INT8 avec calibration
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    # Dataset de calibration (obligatoire)
    def representative_dataset():
        for i in range(min(200, len(calib_data))):
            yield [calib_data[i:i+1].astype(np.float32)]
    
    converter.representative_dataset = representative_dataset
    
    tflite_model = converter.convert()
    
    # Sauvegarde
    with open("model_coral.tflite", "wb") as f:
        f.write(tflite_model)
    
    return "model_coral.tflite"
```

### 1.2 Compilation avec edgetpu-compiler

```bash
# Installation du compilateur
# Version compatible avec votre hardware
wget https://github.com/google-coral/edgetpu-compiler/releases/download/v16.0/edgetpu_compiler_16.0_linux.tar.gz
tar -xzf edgetpu_compiler_16.0_linux.tar.gz

# Compilation basique
./edgetpu_compiler model_coral.tflite

# Sortie :
# model_coral_edgetpu.tflite ← modèle compilé pour Edge TPU
# model_coral_edgetpu.log   ← log de compilation

# Options avancées
./edgetpu_compiler \
    --out_dir ./compiled/ \
    --search_delegate \
    --num_segments 2 \          # Modèle multi-TPU (2 dongles)
    model_coral.tflite

# Vérifier la compilation :
# Le log indique le nombre d'ops déléguées au TPU
# 100% des ops doivent être "Delegate" (pas "CPU")
```

### 1.3 Vérification de la couverture TPU

```python
def verifier_couverture_tpu(tflite_path: str) -> dict:
    """Vérifie quelles ops sont exécutées sur l'Edge TPU."""
    import re
    
    log_path = tflite_path.replace(".tflite", "_edgetpu.log")
    
    try:
        with open(log_path) as f:
            log = f.read()
        
        # Statistiques de couverture
        ops_del = len(re.findall(r'Delegate', log))
        ops_cpu = len(re.findall(r'CPU', log))
        ops_total = ops_del + ops_cpu
        
        return {
            "ops_tpu": ops_del,
            "ops_cpu": ops_cpu,
            "couverture_pct": (ops_del / ops_total * 100) if ops_total else 0,
            "compatible": ops_cpu == 0,
        }
    except FileNotFoundError:
        return {"erreur": "Log de compilation non trouvé"}
```

### 1.4 Opérateurs supportés par l'Edge TPU

| Opérateur | Support | Notes |
|:---------|:-------:|:------|
| **Conv2D** | ✅ | Toutes tailles, padding SAME/VALID |
| **DepthwiseConv2D** | ✅ | Optimal avec stride=1 ou 2 |
| **FullyConnected** | ✅ | |
| **AveragePool2D** | ✅ | Kernel ≤ 4×4 |
| **MaxPool2D** | ✅ | Kernel ≤ 4×4 |
| **Concat** | ✅ | |
| **Add** | ✅ | |
| **ReLU / ReLU6** | ✅ | Fusionnés dans Conv |
| **Softmax** | ⚠️ | Taille limitée (max 1024 classes) |
| **Reshape** | ✅ | Pas de coût |
| **Squeeze** | ✅ | |
| **Pad** | ✅ | CONSTANT uniquement |
| **TransposeConv** | ❌ | CPU fallback |
| **LSTM** | ❌ | CPU fallback |
| **Split** | ⚠️ | Limité |
| **LeakyReLU** | ❌ | CPU fallback |
| **BatchNorm** | ✅ | Fusionné dans Conv |

> **Règle :** si une op tombe sur CPU, toute la chaîne est ralentie. Utiliser `--search_delegate` pour minimiser.

---

## 2. PyCoral API

### 2.1 Inférence basique

```python
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import common, classify, detect
import numpy as np
from PIL import Image

# Chargement du modèle compilé
interpreter = make_interpreter("model_coral_edgetpu.tflite")
interpreter.allocate_tensors()

# Préparation de l'image
image = Image.open("test.jpg")
image = image.resize(common.input_size(interpreter))

# Inférence (entrée automatiquement INT8)
common.set_input(interpreter, image)
interpreter.invoke()

# Résultat
result = classify.get_classes(interpreter, top_k=3)
for r in result:
    print(f"Classe {r.id} : {r.score:.3f}")
```

### 2.2 Détection d'objets

```python
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import detect
from pycoral.adapters.common import input_size
from PIL import Image, ImageDraw

class DetecteurCoral:
    """Détection d'objets temps réel avec Edge TPU."""
    
    def __init__(self, model_path: str, threshold: float = 0.5):
        self.interpreter = make_interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.threshold = threshold
    
    def detecter(self, image_path: str) -> list:
        """Détecte les objets dans une image."""
        image = Image.open(image_path)
        return self._detecter(image)
    
    def _detecter(self, image: Image.Image) -> list:
        """Détection avec image PIL."""
        _, scale = common.set_resized_input(
            self.interpreter, image.resize(
                input_size(self.interpreter), Image.LANCZOS
            )
        )
        self.interpreter.invoke()
        
        objects = detect.get_objects(self.interpreter, self.threshold, scale)
        return objects
    
    def dessiner_boites(self, image_path: str, output_path: str):
        """Dessine les boîtes de détection sur l'image."""
        image = Image.open(image_path)
        objects = self._detecter(image)
        
        draw = ImageDraw.Draw(image)
        for obj in objects:
            bbox = obj.bbox
            draw.rectangle(bbox, outline="red", width=3)
            draw.text(
                (bbox[0], bbox[1] - 15),
                f"{obj.score:.2%}",
                fill="red",
            )
        
        image.save(output_path)
        print(f"Résultat sauvegardé : {output_path}")
        return objects


# Utilisation
detecteur = DetecteurCoral("ssd_mobilenet_v2_coco_edgetpu.tflite")
objets = detecteur.detection("scene.jpg")
print(f"{len(objets)} objets détectés")
```

### 2.3 Classification avec labels

```python
# Classification avec fichier de labels
from pycoral.utils.dataset import read_label_file
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import classify
from PIL import Image

# Labels COCO
labels = read_label_file("coco_labels.txt")

interpreter = make_interpreter("model_coral_edgetpu.tflite")
interpreter.allocate_tensors()

image = Image.open("image.jpg")
_, scale = common.set_resized_input(
    interpreter, image.resize(input_size(interpreter), Image.LANCZOS)
)

interpreter.invoke()
results = classify.get_classes(interpreter, top_k=5)

for i, result in enumerate(results):
    label = labels.get(result.id, f"Classe {result.id}")
    print(f"{i+1}. {label}: {result.score:.2%}")
```

---

## 3. Modèles Pipeline (Multi-TPU)

### 3.1 Segmentation pipeline : détection + classification

```python
# Workflow : détection d'abord → crop → classification
# Chaque modèle peut tourner sur un TPU différent

from pycoral.utils.edgetpu import make_interpreter
from PIL import Image
import numpy as np

class PipelineTPU:
    """Pipeline multi-modèle sur Edge TPU."""
    
    def __init__(self, model_detection: str, model_classification: str):
        self.interp_detect = make_interpreter(model_detection)
        self.interp_detect.allocate_tensors()
        
        self.interp_class = make_interpreter(model_classification)
        self.interp_class.allocate_tensors()
    
    def traiter_image(self, image_path: str) -> list:
        """Détecte puis classifie chaque objet."""
        image = Image.open(image_path)
        
        # Étape 1 : Détection
        _, scale = common.set_resized_input(
            self.interp_detect,
            image.resize(input_size(self.interp_detect), Image.LANCZOS)
        )
        self.interp_detect.invoke()
        objects = detect.get_objects(self.interp_detect, 0.5, scale)
        
        resultats = []
        for obj in objects:
            # Étape 2 : Crop et classification
            crop = image.crop(obj.bbox)
            crop = crop.resize(input_size(self.interp_class), Image.LANCZOS)
            
            common.set_input(self.interp_class, crop)
            self.interp_class.invoke()
            
            classes = classify.get_classes(self.interp_class, top_k=1)
            resultats.append({
                "bbox": obj.bbox,
                "objet_principal": classes[0].id if classes else None,
                "score": obj.score,
            })
        
        return resultats
```

### 3.2 Modèle multi-segments (plusieurs TPU)

```bash
# Compilation pour plusieurs dongles TPU
# --num_segments N répartit le modèle sur N TPU

# Exemple : MobileNetV2 segmenté sur 2 TPU
./edgetpu_compiler \
    --num_segments 2 \
    --out_dir ./multi_tpu/ \
    mobilenet_v2_edgetpu.tflite

# Sortie :
# mobilenet_v2_edgetpu_segment_0.tflite
# mobilenet_v2_edgetpu_segment_1.tflite
```

```python
# Inférence multi-TPU
from pycoral.utils.edgetpu import list_edge_tpus

# Lister les TPU connectés
tpus = list_edge_tpus()
for tpu in tpus:
    print(f"TPU: {tpu['type']} - {tpu['path']} - {tpu['speed']}")
```

---

## 4. Transfer Learning sur Coral

### 4.1 Fine-tuning avec le modèle de base

```coral
# Google fournit des modèles pré-entraînés pour transfer learning
# Téléchargement : https://coral.ai/models/

# Modèles recommandés pour le transfer :
# - MobileNetV1 SSD (détection)
# - MobileNetV2 (classification)
# - EfficientNet-Lite (classification)
# - YOLOv5 (détection) — conversion manuelle
```

```bash
# Fine-tuning avec le script Coral :
python3 examples/classify_image.py \
    --model mobilenet_v2_1.0_224_quant_edgetpu.tflite \
    --labels imagenet_labels.txt \
    --input test.jpg
```

### 4.2 Entraînement personnalisé avec TensorFlow

```python
# 1. Charger un modèle pré-entraîné sans la tête de classification
import tensorflow as tf
import tensorflow_hub as hub

# Modèle de base MobileNetV2 (sans top)
base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3),
    include_top=False,
    weights="imagenet",
)
base_model.trainable = False  # Freeze

# 2. Ajouter une nouvelle tête de classification
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(256, activation="relu"),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(5, activation="softmax"),  # 5 classes custom
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
)

# 3. Entraînement
model.fit(train_ds, validation_data=val_ds, epochs=20)

# 4. Conversion pour Coral
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8

# Calibration (dataset d'entraînement)
converter.representative_dataset = lambda: [
    [train_ds[i:i+1]] for i in range(100)
]

tflite_model = converter.convert()
with open("custom_model.tflite", "wb") as f:
    f.write(tflite_model)

# 5. Compilation pour Edge TPU
# ./edgetpu_compiler custom_model.tflite
```

---

## 5. Benchmarking et Profilage

### 5.1 Benchmark de performance

```python
import time
from pycoral.utils.edgetpu import make_interpreter
from pycoral.adapters import common

def bench_coral(model_path: str, iterations: int = 500) -> dict:
    """Benchmark complet d'un modèle Coral Edge TPU."""
    
    interpreter = make_interpreter(model_path)
    interpreter.allocate_tensors()
    
    # Entrée factice
    input_shape = common.input_size(interpreter)
    dummy_input = np.random.randint(0, 255, 
        (*input_shape, 3), dtype=np.uint8)
    common.set_input(interpreter, dummy_input)
    
    # Warmup
    for _ in range(20):
        interpreter.invoke()
    
    # Mesure
    latences = []
    for _ in range(iterations):
        start = time.perf_counter()
        interpreter.invoke()
        elapsed = (time.perf_counter() - start) * 1000
        latences.append(elapsed)
    
    # Taille du modèle
    import os
    model_size = os.path.getsize(model_path)
    
    return {
        "latence_moyenne_ms": float(np.mean(latences)),
        "latence_p50_ms": float(np.percentile(latences, 50)),
        "latence_p99_ms": float(np.percentile(latences, 99)),
        "fps": 1000 / float(np.mean(latences)),
        "modele_kb": model_size / 1024,
        "tpu": True,
    }

# Exemple :
# bench = bench_coral("ssd_mobilenet_v2_coco_edgetpu.tflite")
# SSD MobileNetV2 → ~100-200 FPS sur Dev Board
```

### 5.2 Comparaison CPU vs TPU

```python
def comparer_cpu_vs_tpu(coral_model_path: str, cpu_model_path: str):
    """Compare les performances CPU vs TPU."""
    from edgetpu.basic.basic_engine import BasicEngine
    
    # Bench TPU
    tpu_result = bench_coral(coral_model_path)
    
    # Bench CPU (TFLite standard, même modèle)
    import tensorflow.lite as tflite
    interpreter = tflite.Interpreter(model_path=cpu_model_path)
    interpreter.allocate_tensors()
    
    input_details = interpreter.get_input_details()
    dummy = np.random.randint(0, 255, 
        input_details[0]["shape"], dtype=np.uint8)
    interpreter.set_tensor(input_details[0]["index"], dummy)
    
    import time
    latences = []
    for _ in range(200):
        start = time.perf_counter()
        interpreter.invoke()
        latences.append((time.perf_counter() - start) * 1000)
    
    cpu_result = {
        "latence_moyenne_ms": float(np.mean(latences)),
        "fps": 1000 / float(np.mean(latences)),
    }
    
    print(f"=== CPU vs TPU ===")
    print(f"CPU: {cpu_result['fps']:.1f} FPS (lat: {cpu_result['latence_moyenne_ms']:.1f} ms)")
    print(f"TPU: {tpu_result['fps']:.1f} FPS (lat: {tpu_result['latence_moyenne_ms']:.1f} ms)")
    print(f"Accélération: {tpu_result['fps']/cpu_result['fps']:.1f}×")
    
    return {"cpu": cpu_result, "tpu": tpu_result}
```

---

## 6. Déploiement sur Dev Board

### 6.1 Installation et configuration

```bash
# Sur la Dev Board (Linux Mendel) ou un Raspberry Pi

# 1. Installer PyCoral
echo "deb https://packages.cloud.google.com/coral/packages buster main" | \
    sudo tee /etc/apt/sources.list.d/coral.list
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt update
sudo apt install python3-pycoral

# 2. Vérifier l'installation
python3 -c "from pycoral.utils.edgetpu import make_interpreter; print('OK')"

# 3. Tester le TPU
python3 -c "
from pycoral.utils.edgetpu import list_edge_tpus
tpus = list_edge_tpus()
print(f'{len(tpus)} TPU(s) trouvés')
"

# 4. Test de démonstration
git clone https://github.com/google-coral/examples-camera.git
cd examples-camera
bash install_requirements.sh
python3 detect_image.py --model mobilenet_v2_edgetpu.tflite
```

### 6.2 Service d'inférence en production

```python
#!/usr/bin/env python3
"""
Service d'inférence Coral Edge TPU — mode serveur (gRPC ou HTTP).
"""

import grpc
import concurrent.futures as cf
from pycoral.utils.edgetpu import make_interpreter
from PIL import Image
import io

class ServiceInferenceCoral:
    """Service d'inférence via API REST (Flask) ou gRPC."""
    
    def __init__(self, model_path: str, label_path: str = None):
        self.interpreter = make_interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.input_size = common.input_size(self.interpreter)
        
        self.labels = None
        if label_path:
            from pycoral.utils.dataset import read_label_file
            self.labels = read_label_file(label_path)
    
    def inferer_image(self, image_bytes: bytes) -> dict:
        """Inférence à partir d'image JPEG bytes."""
        image = Image.open(io.BytesIO(image_bytes))
        image = image.resize(self.input_size, Image.LANCZOS)
        
        common.set_input(self.interpreter, image)
        self.interpreter.invoke()
        
        results = classify.get_classes(self.interpreter, top_k=3)
        
        return {
            "predictions": [
                {
                    "label": self.labels.get(r.id, str(r.id)) if self.labels else str(r.id),
                    "score": float(r.score),
                }
                for r in results
            ]
        }


# Serveur Flask
from flask import Flask, request, jsonify

app = Flask(__name__)
service = ServiceInferenceCoral(
    "mobilenet_v2_edgetpu.tflite",
    "imagenet_labels.txt"
)

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "Image requise"}), 400
    
    image_data = request.files["image"].read()
    result = service.inferer_image(image_data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### 6.3 Intégration dans pipeline GStreamer

```bash
# Pipeline GStreamer pour vidéo avec inférence Edge TPU
# Utilise le plugin gst-edgetpu

gst-launch-1.0 \
    v4l2src device=/dev/video0 ! \
    videoconvert ! \
    videoscale ! \
    video/x-raw,width=640,height=480 ! \
    edgetpu model=ssd_mobilenet_v2_coco_edgetpu.tflite labels=coco_labels.txt ! \
    videoconvert ! \
    autovideosink
```

---

## 7. Dépannage et Optimisation

### 7.1 Diagnostics

```python
def diagnostiquer_coral():
    """Diagnostic complet de la configuration Coral."""
    import os
    
    diagnostic = {}
    
    # 1. Vérifier le matériel
    try:
        from pycoral.utils.edgetpu import list_edge_tpus
        tpus = list_edge_tpus()
        diagnostic["tpus"] = [t["path"] for t in tpus]
        diagnostic["n_tpus"] = len(tpus)
    except Exception as e:
        diagnostic["erreur_materiel"] = str(e)
    
    # 2. Vérifier les permissions udev
    diagnostic["udev"] = os.path.exists("/etc/udev/rules.d/99-edgetpu-accelerator.rules")
    
    # 3. Vérifier la version du firmware
    try:
        from edgetpu.basic.basic_engine import BasicEngine
        engine = BasicEngine("")
        diagnostic["firmware"] = "OK" if engine else "ERROR"
    except Exception as e:
        diagnostic["firmware"] = f"Erreur: {e}"
    
    # 4. Température TPU
    try:
        thermal = os.popen("cat /sys/class/thermal/thermal_zone*/temp").read()
        diagnostic["temperature"] = thermal.strip()
    except:
        pass
    
    return diagnostic
```

---

## Pièges Courants

1. **Modèle FP32 sur Edge TPU** : l'Edge TPU ne supporte QUE INT8. Vérifier que le modèle a été compilé avec `edgetpu_compiler`.

2. **Ops CPU non supportées** : certaines ops (LSTM, TransposeConv, LeakyReLU) tombent sur CPU → latence ×10. Vérifier dans le log de compilation que 100% des ops sont "Delegate".

3. **Batch size > 1** : l'Edge TPU ne supporte que batch_size=1. Vérifier lors de la conversion.

4. **Image trop grande pour la mémoire TPU** : l'Edge TPU a 8 MB SRAM. Les modèles avec de grandes entrées (> 640×640) peuvent saturer. Réduire la résolution.

5. **Plusieurs TPU sur le même bus USB** : la bande passante USB 3.0 est partagée. 2 TPU = ~50% de bande passante chacun. Préférer les M.2 ou PCIe pour le multi-TPU.

6. **USB Accelerator sur Pi Zero** : la bande passante USB 2.0 (480 Mbps) est un goulot d'étranglement. Ajouter `--usb.early_wakeup` dans le boot config.

7. **Température élevée** : l'Edge TPU chauffe fort (> 80 °C) sous charge continue. Ajouter un dissipateur thermique. Au-delà de 95 °C, le throttling réduit la fréquence.

---

## Références

- **Coral AI** : https://coral.ai/
- **PyCoral API** : https://coral.ai/docs/reference/py-coral/
- **Edge TPU Compiler** : https://coral.ai/docs/edgetpu/compiler/
- **Coral Models** : https://coral.ai/models/
- **Coral Examples** : https://github.com/google-coral/examples-camera
- **Coral API Reference** : https://coral.ai/docs/reference/
- **GStreamer Coral** : https://coral.ai/docs/gstreamer/
