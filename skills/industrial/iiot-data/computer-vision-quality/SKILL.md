---
name: computer-vision-quality
description: "Utiliser quand l'utilisateur demande d'implémenter ou d'optimiser des scripts de vision par ordinateur à l'Edge (OpenCV, TensorFlow/PyTorch) pour des applications industrielles de contrôle qualité, comptage ou de tri."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [computer-vision, opencv, tensorflow-lite, edge-computing, quality-control]
    related_skills: [industrial-edge, industrial-protocols]
---

# Vision Industrielle & Contrôle Qualité Edge

## Vue d'ensemble

L'intégration de la **Vision par Ordinateur** à la périphérie du réseau (Edge Computing) permet d'inspecter en temps réel des flux de production pour :
1.  **Le contrôle qualité :** Détection de défauts physiques (rayures, fissures, déformations), vérification de la présence d'un composant ou d'une étiquette.
2.  **Le tri et la manipulation :** Identifier la position et l'orientation de pièces pour guider un robot (Pick & Place).
3.  **Le comptage et la mesure :** Compter des produits sur un convoyeur, mesurer des dimensions physiques avec une précision millimétrique.

Les applications industrielles Edge s'exécutent généralement sur des passerelles équipées de processeurs d'accélération IA (ex: NVIDIA Jetson, Raspberry Pi avec accélérateur Hailo/Coral) utilisant **OpenCV** pour le traitement d'images et **TensorFlow Lite** ou **ONNX Runtime** pour l'inférence de modèles d'apprentissage profond (Deep Learning).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'écrire un script de traitement d'images en Python (OpenCV) pour analyser des pièces (filtrage, seuillage, détection de contours).
- De configurer l'acquisition vidéo depuis une caméra industrielle (via RTSP, GigE Vision, USB).
- D'optimiser l'exécution d'un modèle d'inférence (TensorFlow Lite, ONNX) pour limiter la latence sur un équipement Edge.
- D'interfacer le résultat de l'analyse d'image avec un automate (envoi de signaux OK/NOK via Modbus ou entrées/sorties physiques).

**Ne pas utiliser pour :**
- L'entraînement lourd de modèles d'IA sur serveurs cloud.
- Le paramétrage physique optique (choix des lentilles, filtres physiques de polarisation ou focales de caméras).

---

## 1. Exemple de Script OpenCV pour le Contrôle Qualité

Le script ci-dessous montre comment détecter la présence d'une étiquette sur un flacon en utilisant des techniques classiques de traitement d'images OpenCV (seuil de pixels non noirs dans une zone d'intérêt ROI) :

```python
import cv2
import numpy as np

def inspect_bottle(image_path, roi_coords, threshold_pixels=5000):
    """
    Inspecte une bouteille pour vérifier la présence d'une étiquette.
    roi_coords : tuple (x, y, w, h) définissant la zone de l'étiquette.
    """
    # 1. Charger l'image en niveaux de gris
    img = cv2.imread(image_path)
    if img is None:
        return {"success": False, "error": "Impossible de charger l'image"}
        
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Découper la zone d'intérêt (ROI)
    x, y, w, h = roi_coords
    roi = gray[y:y+h, x:x+w]
    
    # 3. Appliquer un filtre Gaussien et un seuillage binaire (Otsu)
    blurred = cv2.GaussianBlur(roi, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. Compter les pixels blancs (étiquette)
    white_pixels = cv2.countNonZero(thresh)
    
    # Détermination du statut
    is_ok = white_pixels >= threshold_pixels
    
    # Optionnel: dessiner les résultats pour le diagnostic de débogage
    output_img = img.copy()
    color = (0, 255, 0) if is_ok else (0, 0, 255)
    cv2.rectangle(output_img, (x, y), (x+w, y+h), color, 2)
    cv2.putText(output_img, f"Pixels: {white_pixels}", (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                
    cv2.imwrite("inspection_result.jpg", output_img)
    
    return {
        "success": True,
        "is_ok": is_ok,
        "measured_pixels": white_pixels,
        "status": "CONFORME" if is_ok else "NON-CONFORME"
    }

# Exemple d'appel :
# inspect_bottle("bottle_frame.jpg", roi_coords=(150, 200, 100, 150))
```

---

## 2. Inférence Edge avec TensorFlow Lite

Pour des contrôles plus complexes (ex: classification de type de défauts), on utilise des modèles légers. Voici comment charger et exécuter une inférence TFLite de façon optimisée :

```python
import numpy as np
try:
    import tflite_runtime.interpreter as tflite
except ImportError:
    from tensorflow import lite as tflite

def run_edge_inference(model_path, input_image_np):
    # Charger le modèle et allouer les tenseurs de manière optimisée
    interpreter = tflite.Interpreter(model_path=model_path, num_threads=4)
    interpreter.allocate_tensors()

    # Obtenir les détails d'entrée/sortie
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Prétraiter l'image (redimensionnement et normalisation)
    input_shape = input_details[0]['shape']
    # input_image_np doit avoir la dimension requise par le modèle (ex: 1, 224, 224, 3)
    
    interpreter.set_tensor(input_details[0]['index'], input_image_np)
    interpreter.invoke()

    # Récupérer la prédiction
    output_data = interpreter.get_tensor(output_details[0]['index'])
    prediction_idx = np.argmax(output_data[0])
    confidence = output_data[0][prediction_idx]

    return {"class_id": int(prediction_idx), "confidence": float(confidence)}
```

---

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Dérive de luminosité de l'environnement :**
    *   *Erreur :* Développer des algorithmes basés sur des seuils de couleur ou de luminosité fixes sans prendre en compte les variations de la lumière naturelle de l'atelier (soleil à midi vs nuit sous néon).
    *   *Correction :* Utiliser des éclairages artificiels industriels fermés (backlights, ring lights directionnels) pour isoler la zone de prise de vue, ou normaliser l'histogramme de l'image avant traitement.
2.  **Fuites de mémoire vidéo :**
    *   *Erreur :* Ouvrir le flux de la caméra à chaque image inspectée et oublier de libérer les ressources, entraînant un plantage par manque de RAM après quelques heures.
    *   *Correction :* Instancier la capture vidéo (`cv2.VideoCapture`) une seule fois au démarrage du script, puis lire en boucle fermée. Toujours appeler `.release()` à l'arrêt du programme.

---

## Liste de vérification (Checklist)

- [ ] L'éclairage de l'image est stabilisé ou compensé par logiciel (normalisation).
- [ ] Les flux vidéos et fichiers d'images sont correctement libérés après traitement (`release` et destruction des fenêtres).
- [ ] Le temps d'inférence ou de traitement d'image est compatible avec le temps de cycle de la machine (ex: < 200 ms pour une cadence de 300 pièces/min).
- [ ] Les seuils de décision (ex: pixels NOK) incluent une marge de sécurité tolérante au bruit d'acquisition de l'image.

