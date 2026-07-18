---
name: machine-vision-industrial
description: "Configurer et programmer des systèmes de vision industrielle pour le contrôle qualité."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - cognex
      - keyence
      - halcon
      - machine-vision
      - vision-inspection
      - openmv
      - defect-detection
      - barcode-reading
      - ocr-industrial
      - dimensional-inspection
      - presence-detection
      - smart-camera
      - pattern-matching
      - blob-analysis
      - edge-detection
      - deep-learning-vision
      - vision-guided-robotics
      - deep-learning
      - quality-control
      - vision-system
      - image-processing
      - faro
    related_skills:
      - computer-vision-quality
      - ai-industrial-vision
      - cobot-human-collaboration
      - robotics-abb
---

# Vision Industrielle Automatisée

## Vue d'ensemble

La **vision industrielle** est une technologie clé de l'inspection qualité automatisée. Contrairement à la vision par ordinateur classique, elle impose :

- **Déterminisme** — Temps de cycle garanti (souvent < 100 ms)
- **Répétabilité** — Même résultat pour la même pièce dans les mêmes conditions
- **Robustesse** — Résistance aux variations d'éclairage, vibrations, poussière
- **Intégration** — Communication directe avec PLC (EtherNet/IP, PROFINET, I/O)

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer une caméra intelligente Cognex ou Keyence pour l'inspection
- De développer un programme de vision pour la détection de défauts
- De mettre en place une lecture de code-barres ou OCR industriel
- D'intégrer un système de vision avec un robot
- De choisir l'éclairage et les optiques pour une application donnée
- De migrer un système de vision existant vers une nouvelle plateforme

---

## 1. Architectures de Vision

### 1.1 Smart Camera (caméra intelligente)

```
┌──────────────────────────────────────┐
│         Caméra Intelligente           │
│  ┌─────┐ ┌──────────┐ ┌──────────┐  │
│  │     │ │  Traite- │ │  Comm    │  │
│  │Opt. │ │  ment    │ │  (E/IP)  │──┼──→ PLC
│  │ +   │ │  d'image │ │  PROF.   │  │
│  │Capt.│ └──────────┘ └──────────┘  │
│  └─────┘                             │
│         ┌──────────────┐             │
│         │  Éclairage   │             │
│         │  intégré     │             │
│         └──────────────┘             │
└──────────────────────────────────────┘
```

### 1.2 PC-based Vision

```
┌───────────┐
│   Camera  │  ─── GigE / USB3 / CoaXPress ──┐
│   (GenICam)│                                 │
└───────────┘                                  │
┌───────────┐                                  │
│   Camera  │  ─── GigE / USB3 / CoaXPress ────┤
│   (GenICam)│                                  │
└───────────┘                                  ▼
                                        ┌─────────────┐
                                        │  PC Vision  │
                                        │ (HALCON,    │───→ PLC
                                        │  OpenCV,    │───→ HMI
                                        │  VisionPro) │
                                        └─────────────┘
```

---

## 2. Plateformes Logicielles

### 2.1 Cognex In-Sight / Designer

```python
# Exemple : Configuration d'un outil PatternMatch dans In-Sight
insight_config = {
    "tool": "PatternMatch",
    "region": {
        "x": 100, "y": 150, "width": 300, "height": 200
    },
    "pattern": "reference_pattern.pat",
    "score_threshold": 0.85,
    "angle_range": (-10, 10),
    "output": {
        "x_offset": "Out_X",
        "y_offset": "Out_Y",
        "score": "Out_Score"
    }
}

# Communication avec In-Sight (TCP/IP)
response = send_cognex_command(
    ip="192.168.1.50",
    command="WriteCell",
    parameters={"cell": "PatternScore", "value": 0.70}
)
```

#### Outils Cognex courants :

| Outil | Fonction | Usage typique |
|:------|:---------|:--------------|
| **PatMax / PatQuick** | Pattern matching (géométrique, gris) | Localisation, alignement |
| **Blob** | Analyse de blobs | Surface, présence défaut |
| **Edge** | Détection de bords | Mesure dimensionnelle |
| **IDMax** | Code DataMatrix | Lecture DPM |
| **OCRMax** | OCR / OCV | Marquage, packaging |
| **Fixture** | Calibration coordonnées | Robot guidance |

### 2.2 Keyence CV-X / XG-X

```python
# Configuration Keyence CV-X via Ethernet
keyence_config = {
    "program": "Inspection_01",
    "steps": [
        {
            "type": "search",
            "name": "Trouver_Ref",
            "pattern": "ref_img",
            "position": (320, 240),
            "score_min": 0.8
        },
        {
            "type": "edge_width",
            "name": "Mesure_Largeur",
            "edge1": "OUT_A",
            "edge2": "OUT_B",
            "tolerance": (49.5, 50.5)  # mm
        }
    ]
}
```

#### Outils Keyence :

| Outil | Fonction |
|:------|:---------|
| **Trouver** | Pattern search (corrélation) |
| **Caliber** | Mesure dimensionnelle |
| **Correct** | Correction de perspective |
| **Check** | Présence / absence |
| **OCR2** | OCR intelligent |
| **Deep Learning** | Classification par IA |

### 2.3 MVTec HALCON

```python
import halcon as ha

# Exemple de script HALCON
def inspect_surface(image_path: str) -> dict:
    """Inspecte la surface d'une pièce pour défauts."""
    image = ha.read_image(image_path)

    # Prétraitement
    image_gray = ha.rgb1_to_gray(image)
    image_gauss = ha.gauss_filter(image_gray, 5)

    # Segmentation de défauts
    regions = ha.threshold(image_gauss, 0, 80)

    # Analyse des défauts
    features = ha.region_features(regions, ["area", "circularity", "width", "height"])

    result = {
        "n_defects": len(features),
        "defects": [
            {"area": f["area"], "circularity": f["circularity"],
             "x": f["width"], "y": f["height"],
             "ok": f["area"] < 500}  # Seuil de défaut
            for f in features
        ],
        "overall_ok": all(f["area"] < 500 for f in features)
    }
    return result
```

---

## 3. Éclairage

### 3.1 Types d'éclairage

| Type | Schéma | Usage | Effet |
|:-----|:-------|:------|:------|
| **Backlight** (rétroéclairage) | Capteur ← Pièce ← Lumière | Mesure dimensionnelle | Silhouette nette |
| **Ring Light** (anneau) | Lumière autour de l'objectif | Inspection surface | Éclairage uniforme |
| **Dome Light** (dôme) | Lumière diffusée par dôme | Surfaces réfléchissantes | Sans ombre |
| **Darkfield** (champ sombre) | Lumière rasante | Gravure, marquage | Contraste des reliefs |
| **Structured Light** | Projection de motifs | 3D, mesures de hauteur | Profilométrie |
| **Coaxial** (lumière coaxiale) | Lumière à travers l'objectif | Surfaces miroir | Pas de reflet |

### 3.2 Couleurs d'éclairage

| Couleur | Longueur d'onde | Usage |
|:--------|:-----------------|:------|
| **Blanc** | 450–650 nm | Usage général |
| **Rouge** | 625 nm | Traversée matière, contraste défauts |
| **Bleu** | 470 nm | Contraste métal/marquage |
| **Vert** | 530 nm | Contraste PCB, verre |
| **IR (infrarouge)** | 850–940 nm | Traversée plastiques, opaque visible |
| **UV (ultraviolet)** | 365–395 nm | Fluorescence, adhésifs |

---

## 4. Optiques

### 4.1 Choix de l'objectif

```python
def calculate_lens_focal_length(working_distance: float, field_of_view: float,
                                sensor_width: float = 6.4) -> float:
    """Calcule la focale nécessaire.

    Args:
        working_distance: Distance de travail (mm)
        field_of_view: Champ de vue désiré (mm)
        sensor_width: Largeur du capteur (mm) — 6.4 pour 1/2", 8.8 pour 1"

    Returns:
        Focale recommandée (mm)
    """
    f = (working_distance * sensor_width) / field_of_view
    return round(f, 1)

# Exemple : WD=200mm, FOV=50mm, capteur 1/2"
f = calculate_lens_focal_length(200, 50, 6.4)  # → 25.6 mm
```

### 4.2 Résolution et précision

```python
def calculate_accuracy(fov_mm: float, image_width_px: int,
                       pixel_tolerance: float = 0.5) -> dict:
    """Calcule les métriques de précision.

    Returns:
        resolution: mm/pixel
        accuracy: Précision atteignable avec sub-pixel
    """
    resolution = fov_mm / image_width_px
    accuracy = resolution * pixel_tolerance
    return {
        "resolution_mm_per_pixel": resolution,
        "accuracy_mm": accuracy,
        "accuracy_um": accuracy * 1000
    }

# Exemple : 50mm FOV, 2448px wide, sub-pixel 0.3
acc = calculate_accuracy(50, 2448, 0.3)  # → resolution=0.020mm, accuracy=6µm
```

---

## 5. Applications Types

### 5.1 Détection de défauts

```python
def detect_surface_defects(image: np.ndarray, method: str = "threshold") -> dict:
    """Détecte les défauts de surface sur une image.

    Args:
        image: Image en niveaux de gris (HxW)
        method: 'threshold', 'contour', 'blob'

    Returns:
        Dict avec coordonnées et caractéristiques des défauts
    """
    import cv2
    import numpy as np

    if method == "threshold":
        _, binary = cv2.threshold(image, 50, 255, cv2.THRESH_BINARY_INV)
    elif method == "contour":
        edges = cv2.Canny(image, 30, 100)
        binary = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    defects = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > 10:  # Filtrer le bruit
            x, y, w, h = cv2.boundingRect(c)
            defects.append({
                "area_px": int(area),
                "center": (int(x + w // 2), int(y + h // 2)),
                "bbox": (int(x), int(y), int(w), int(h)),
            })

    return {
        "n_defects": len(defects),
        "defects": defects,
        "pass": len(defects) == 0
    }
```

### 5.2 Lecture DataMatrix (DPM)

```python
import libdmtx  # pylibdmtx

def read_datamatrix(image: np.ndarray) -> list:
    """Lit les codes DataMatrix dans une image.

    Args:
        image: Image OpenCV (BGR ou niveaux de gris)

    Returns:
        Liste des codes lus avec leur contenu
    """
    results = []
    decoded = libdmtx.decode(image, timeout=200)
    for d in decoded:
        results.append({
            "data": d.data.decode("utf-8", errors="ignore"),
            "quality": d.quality,
            "position": {
                "x_min": d.rect.left,
                "y_min": d.rect.top,
                "x_max": d.rect.left + d.rect.width,
                "y_max": d.rect.top + d.rect.height,
            }
        })
    return results
```

### 5.3 Robot Guidance

```python
def calibrate_hand_eye(robot_poses: list, camera_poses: list) -> dict:
    """Calibration Hand-Eye (caméra montée sur robot).

    Args:
        robot_poses: Liste des poses du robot [(x,y,z,rx,ry,rz)]
        camera_poses: Liste des poses détectées de la cible [(x,y,z,rx,ry,rz)]

    Returns:
        Transformation caméra → robot
    """
    import numpy as np
    from scipy.spatial.transform import Rotation as R

    # Méthode Tsai-Lenz pour résoudre AX = XB
    # (Simplifié — utiliser OpenCV calibrateHandEye pour le calcul complet)
    from cv2 import calibrateHandEye  # noqa: F401

    # Voir : cv2.calibrateHandEye(robot_rotations, robot_translations,
    #                            camera_rotations, camera_translations)
    return {"status": "use_cv2.calibrateHandEye for actual calculation"}
```

---

## 6. Communication avec PLC

### 6.1 Via EtherNet/IP

```python
def send_vision_result_to_plc(ip: str, result: dict, tag_prefix: str = "Vision_") -> bool:
    """Envoie les résultats d'inspection vers un PLC via EtherNet/IP.

    Args:
        ip: IP du PLC
        result: Dict avec champs (pass, n_defects, score, etc.)
        tag_prefix: Préfixe des tags PLC
    """
    try:
        from pycomm3 import LogixDriver

        with LogixDriver(ip) as plc:
            plc.write(f"{tagPrefix}Result", 1 if result.get("pass") else 0)
            plc.write(f"{tagPrefix}Score", result.get("score", 0.0))
            plc.write(f"{tagPrefix}Defects", result.get("n_defects", 0))
        return True
    except ImportError:
        logger.warning("pycomm3 non installé, communication simulée")
        return False
```

---

## 7. Références

- [Cognex In-Sight Explorer](https://www.cognex.com/products/machine-vision/in-sight-vision-systems)
- [Keyence CV-X Series](https://www.keyence.com/products/vision/)
- [MVTec HALCON Documentation](https://www.mvtec.com/halcon)
- [OpenCV Documentation](https://docs.opencv.org)
- [OpenMV Cam](https://openmv.io)
- [OpenCV Calibration Hand-Eye](https://docs.opencv.org/master/d9/d0c/group__calib3d.html)
- [ISO 19138 Machine Vision Standards](https://www.iso.org)
- [pylibdmtx sur PyPI](https://pypi.org/project/pylibdmtx/)
