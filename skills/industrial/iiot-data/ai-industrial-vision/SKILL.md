---
name: ai-industrial-vision
description: "Déployer des pipelines de vision IA sur ligne."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [computer-vision, opencv, yolo, onnx, quality-control, gige-vision, industrial-camera, defect-detection]
    related_skills: [computer-vision-quality, plc-connectivity, industrial-edge, predictive-maintenance]
---

# Vision Industrielle & IA pour le Contrôle Qualité

## Vue d'ensemble

La **vision industrielle** est un pilier de l'Industrie 4.0 pour l'inspection automatique, la détection de défauts et la lecture de codes sur les lignes de production. L'intégration de modèles d'intelligence artificielle (YOLO, ONNX Runtime) permet de dépasser les limites des algorithmes classiques (seuillage, template matching) sur des défauts visuels complexes.

Cette compétence guide l'agent Helios pour :
1. Configurer des **caméras industrielles** (GigE Vision, USB3 Vision) via Python.
2. Développer des **pipelines de prétraitement** OpenCV (binarisation, détection de contours, calibration).
3. Intégrer des **modèles de détection de défauts** YOLO/ONNX pour le contrôle qualité en ligne.
4. Communiquer les **résultats OK/NOK** à l'automate PLC (trigger → acquisition → résultat).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De développer un système de contrôle qualité visuel automatisé.
- D'intégrer un modèle YOLO ou ONNX pour la détection de défauts en production.
- De configurer une caméra industrielle GigE Vision ou USB3 Vision avec Python.
- De communiquer les résultats d'inspection (OK/NOK/classification) à un automate PLC.
- D'effectuer de l'OCR industriel (lecture de numéros de lot, dates de péremption).

**Ne pas utiliser pour :**
- La conception CAO 3D de pièces mécaniques (utiliser `cad-bom-automation`).
- L'analyse de données capteurs sans composante visuelle (utiliser `predictive-maintenance`).

---

## 1. Pipeline d'Inspection Visuelle Complet

```text
[Automate PLC]                [Caméra GigE]             [PC Vision / Edge]
     │                              │                          │
     │  Trigger d'acquisition       │                          │
     │  (sortie TOR / OPC-UA)       │                          │
     ├─────────────────────────────▶│  Capture image           │
     │                              ├─────────────────────────▶│
     │                              │  Image brute (Bayer/RGB) │
     │                              │                          │
     │                              │           ┌──────────────┴──────────────┐
     │                              │           │  1. Prétraitement OpenCV    │
     │                              │           │  2. Inférence YOLO/ONNX    │
     │                              │           │  3. Post-traitement        │
     │                              │           │  4. Verdict OK / NOK       │
     │                              │           └──────────────┬──────────────┘
     │                              │                          │
     │◀────────────────────────────────────────────────────────┤
     │  Résultat (Bool OK/NOK +     │                          │
     │  code défaut + confiance)    │                          │
     │  via Snap7 / OPC-UA          │                          │
```

---

## 2. Acquisition Caméra GigE Vision avec Harvesters

```python
from harvesters.core import Harvester
import cv2
import numpy as np


def capture_gige_image(cti_path: str, camera_index: int = 0) -> np.ndarray:
    """Capture une image depuis une caméra GigE Vision.

    Args:
        cti_path: Chemin vers le fichier GenTL Producer (.cti) du fabricant.
        camera_index: Index de la caméra dans la liste des périphériques détectés.

    Returns:
        np.ndarray: Image capturée au format numpy BGR.
    """
    h = Harvester()
    h.add_file(cti_path)
    h.update()

    if len(h.device_info_list) == 0:
        raise RuntimeError("Aucune caméra GigE Vision détectée sur le réseau.")

    print(f"Caméra détectée : {h.device_info_list[camera_index].model}")

    ia = h.create(camera_index)
    ia.start()

    with ia.fetch() as buffer:
        component = buffer.payload.components[0]
        image = component.data.reshape(component.height, component.width)

        # Conversion Bayer → BGR si nécessaire
        if len(image.shape) == 2:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_BayerBG2BGR)
        else:
            image_bgr = image.copy()

    ia.stop()
    ia.destroy()
    h.reset()

    return image_bgr
```

---

## 3. Détection de Défauts avec YOLO / ONNX Runtime

```python
import onnxruntime as ort
import cv2
import numpy as np


class DefectDetector:
    """Détecteur de défauts basé sur un modèle YOLO exporté en ONNX.

    Args:
        model_path: Chemin vers le fichier .onnx du modèle YOLO.
        confidence_threshold: Seuil de confiance minimum pour valider une détection.
        class_names: Liste des noms de classes (ex: ['OK', 'Scratch', 'Dent', 'Crack']).
    """

    def __init__(self, model_path: str, confidence_threshold: float = 0.5,
                 class_names: list = None):
        self.session = ort.InferenceSession(model_path)
        self.confidence_threshold = confidence_threshold
        self.class_names = class_names or ["OK", "Defaut"]
        self.input_name = self.session.get_inputs()[0].name
        self.input_shape = self.session.get_inputs()[0].shape  # ex: [1, 3, 640, 640]

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Prépare l'image pour l'inférence YOLO (resize, normalise, transpose).

        Args:
            image: Image BGR au format numpy.

        Returns:
            np.ndarray: Tensor d'entrée prêt pour le modèle.
        """
        h, w = self.input_shape[2], self.input_shape[3]
        resized = cv2.resize(image, (w, h))
        blob = resized.astype(np.float32) / 255.0
        blob = blob.transpose(2, 0, 1)  # HWC → CHW
        blob = np.expand_dims(blob, axis=0)  # Ajout batch dimension
        return blob

    def detect(self, image: np.ndarray) -> dict:
        """Exécute la détection de défauts sur une image.

        Args:
            image: Image BGR au format numpy.

        Returns:
            dict: Résultat contenant le verdict (OK/NOK), les défauts et la confiance.
        """
        input_tensor = self.preprocess(image)
        outputs = self.session.run(None, {self.input_name: input_tensor})

        detections = self._parse_yolo_output(outputs[0], image.shape)

        defects = [d for d in detections if d["class"] != "OK"]

        return {
            "verdict": "NOK" if defects else "OK",
            "defects_count": len(defects),
            "defects": defects,
            "max_confidence": max((d["confidence"] for d in defects), default=0.0),
        }

    def _parse_yolo_output(self, output: np.ndarray, original_shape: tuple) -> list:
        """Parse la sortie brute du modèle YOLO.

        Args:
            output: Tensor de sortie du modèle ONNX.
            original_shape: Dimensions de l'image originale (H, W, C).

        Returns:
            list: Liste de détections avec bbox, classe et confiance.
        """
        detections = []
        oh, ow = original_shape[:2]
        ih, iw = self.input_shape[2], self.input_shape[3]

        for detection in output[0]:
            confidence = float(detection[4])
            if confidence < self.confidence_threshold:
                continue

            class_scores = detection[5:]
            class_id = int(np.argmax(class_scores))
            class_confidence = float(class_scores[class_id]) * confidence

            if class_confidence < self.confidence_threshold:
                continue

            # Conversion des coordonnées vers l'image originale
            cx, cy, w, h = detection[:4]
            x1 = int((cx - w / 2) * ow / iw)
            y1 = int((cy - h / 2) * oh / ih)
            x2 = int((cx + w / 2) * ow / iw)
            y2 = int((cy + h / 2) * oh / ih)

            detections.append({
                "class": self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}",
                "confidence": round(class_confidence, 3),
                "bbox": [x1, y1, x2, y2],
            })

        return detections
```

---

## 4. Communication Résultat → Automate PLC

```python
import snap7
from snap7.util import set_bool, set_int


def send_result_to_plc(plc_ip: str, db_number: int, result: dict):
    """Envoie le résultat d'inspection visuelle à un automate Siemens S7.

    Args:
        plc_ip: Adresse IP de l'automate.
        db_number: Numéro du Data Block dédié à la vision.
        result: Dictionnaire résultat du détecteur de défauts.

    Structure du DB Vision (offsets) :
        Byte 0.0 : Bool  → Vision_ResultReady (le résultat est disponible)
        Byte 0.1 : Bool  → Vision_PartOK (TRUE = pièce conforme)
        Byte 2   : Int   → Vision_DefectCode (code du défaut principal)
        Byte 4   : Int   → Vision_DefectCount (nombre de défauts détectés)
    """
    client = snap7.client.Client()
    client.connect(plc_ip, 0, 1)

    try:
        buffer = bytearray(6)

        # Résultat prêt
        set_bool(buffer, 0, 0, True)
        # Pièce OK/NOK
        set_bool(buffer, 0, 1, result["verdict"] == "OK")
        # Code défaut principal (0 = pas de défaut)
        defect_code = 0 if result["verdict"] == "OK" else 1
        set_int(buffer, 2, defect_code)
        # Nombre de défauts
        set_int(buffer, 4, result["defects_count"])

        client.db_write(db_number, 0, buffer)
        print(f"Résultat envoyé au PLC : {result['verdict']} ({result['defects_count']} défauts)")

    finally:
        client.disconnect()
```

---

## Pièges Courants

1. **Éclairage non maîtrisé :**
   * *Erreur :* Le modèle fonctionne parfaitement en laboratoire mais échoue en production car l'éclairage ambiant varie (lumière du jour, reflets métalliques).
   * *Correction :* Utiliser un éclairage industriel dédié et stable (LED annulaire, rétro-éclairage, dôme diffusant). L'éclairage représente 70% de la qualité d'un système de vision.

2. **Temps d'inférence incompatible avec la cadence :**
   * *Erreur :* Le modèle YOLO met 200ms pour analyser une image alors que la cadence machine est de 10 pièces/seconde (100ms par pièce).
   * *Correction :* Optimiser le modèle (quantification INT8, TensorRT), réduire la résolution d'entrée, ou utiliser un GPU industriel (NVIDIA Jetson) dédié à l'inférence.

3. **Dataset d'entraînement non représentatif :**
   * *Erreur :* Entraîner le modèle sur 100 images de défauts en laboratoire, puis le déployer sur une ligne où les pièces sont sales, orientées différemment ou de couleurs variées.
   * *Correction :* Collecter les données d'entraînement **sur la ligne de production réelle**, avec les conditions d'éclairage, de salissure et de positionnement réels. Augmenter les données avec des rotations, flips et variations de luminosité.

---

## Références

- **OpenCV Documentation** — https://docs.opencv.org/
- **ONNX Runtime** — https://onnxruntime.ai/
- **Ultralytics YOLOv8** — https://docs.ultralytics.com/
- **GigE Vision Standard (AIA)** — https://www.visiononline.org/
- **Harvesters (GenTL)** — https://github.com/genicam/harvesters

---

## Liste de vérification (Checklist)

- [ ] L'éclairage industriel est stable, reproductible et adapté au type de défaut recherché.
- [ ] Le temps d'inférence du modèle est compatible avec la cadence de la ligne de production.
- [ ] Le dataset d'entraînement contient des images capturées dans les conditions réelles de production.
- [ ] La communication du résultat vers l'automate (OK/NOK) est synchronisée avec le trigger d'acquisition.
- [ ] Un mécanisme de secours est prévu en cas de défaillance du système de vision (ex: mode bypass avec alarme).

