---
name: edge-ai-for-industry40
description: "Déployer des modèles d'IA embarquée sur des dispositifs Edge pour l'Industrie 4.0 avec TensorFlow Lite, ONNX et exécution locale."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - edge-ai
      - industrie-4.0
      - tensorflow-lite
      - onnx
      - machine-learning
      - iot
      - embedded
      - predictive-maintenance
      - anomaly-detection
      - real-time
      - nvidia-jetson
      - raspberry-pi
    related_skills:
      - industrial-diagnostic
      - ot-audit
      - python-pep8
---

# IA Embarquée (Edge AI) pour l'Industrie 4.0

## Vue d'ensemble

L'IA embarquée (Edge AI) consiste à exécuter des modèles d'intelligence artificielle directement sur les équipements de terrain (capteurs, automates, passerelles IoT) plutôt que dans le cloud. Cette approche permet des temps de réponse inférieurs à la milliseconde, une confidentialité des données renforcée et une autonomie vis-à-vis de la connectivité réseau.

Cette compétence couvre l'ensemble du cycle de vie d'un modèle Edge AI industriel : de la préparation et l'optimisation du modèle jusqu'à son déploiement et sa surveillance sur le terrain.

### Architecture typique Edge AI industrielle

```
┌─────────────────────────────────────────────────────────────────┐
│                         Niveau IT (Cloud)                       │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Entraînement │    │  Validation  │    │  Optimisation│      │
│  │   (GPU/TPU)  │───▶│    & Test    │───▶│ (TFLite/     │      │
│  └──────────────┘    └──────────────┘    │  ONNX)      │      │
│                                          └──────┬───────┘      │
└─────────────────────────────────────────────────┼──────────────┘
                                                   │
                                          Déploiement OTA
                                                   │
┌──────────────────────────────────────────────────┼──────────────┐
│                     Niveau OT (Terrain)          ▼              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │        Dispositif Edge (Jetson / Raspberry / PLC)        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  │   │
│  │  │ Capteurs │─▶│ Inférence│─▶│ Décision │─▶│ Action │  │   │
│  │  │ (MQTT/   │  │ Modèle   │  │ & Alerte │  │ (API/  │  │   │
│  │  │ Modbus)  │  │ TFLite   │  │          │  │ Relais)│  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Quand l'utiliser

### À utiliser lorsque l'utilisateur demande de :

- Déployer un modèle d'IA sur un dispositif Edge (NVIDIA Jetson, Raspberry Pi, Google Coral).
- Convertir un modèle TensorFlow/PyTorch en format optimisé pour l'embarqué (TFLite, ONNX).
- Mettre en place une détection d'anomalies en temps réel sur des données capteurs.
- implémenter une maintenance prédictive avec inférence locale.
- Configurer un pipeline de données MQTT/Modbus vers un modèle Edge.
- Optimiser un modèle pour réduire sa latence d'inférence et sa consommation mémoire.
- Qualifier la performance d'un modèle déployé (FPS, précision, consommation).

### Ne pas utiliser pour :

- L'entraînement de modèles sur GPU cluster (utiliser une plateforme MLops dédiée).
- L'analyse de données historiques en batch (utiliser `data-analysis-exploration` ou une plateforme Big Data).
- La configuration de la couche réseau industrielle (switches, routeurs, firewalls).
- La gestion du cycle de vie des certificats TLS et de la sécurité IoT (compétence `ot-security`).

---

## 1. Préparation et Optimisation des Modèles

### 1.1 Entraînement du modèle

```python
import tensorflow as tf
import numpy as np

# Exemple : modèle de détection d'anomalies vibratoires
def train_anomaly_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation="relu", input_shape=(128,)),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(32, activation="relu"),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(1, activation="sigmoid"),
    ])

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )
    return model

model = train_anomaly_model()
model.summary()
```

### 1.2 Conversion vers TensorFlow Lite

```python
# Conversion du modèle entraîné en TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Optimisation pour l'embarqué (quantification INT8)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float16]

# Quantification avec calibration sur un échantillon représentatif
def representative_dataset():
    for _ in range(100):
        yield [np.random.randn(1, 128).astype(np.float32)]

converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]

tflite_model = converter.convert()

# Sauvegarde du modèle optimisé
with open("models/anomaly_detection_v2.tflite", "wb") as f:
    f.write(tflite_model)

print(f"Taille du modèle TFLite : {len(tflite_model) / 1024:.1f} KB")
```

### 1.3 Conversion vers ONNX

```python
import torch
import torch.onnx

# Modèle PyTorch vers ONNX
model = torch.load("models/anomaly_detection_v2.pt")
model.eval()

dummy_input = torch.randn(1, 128)
torch.onnx.export(
    model,
    dummy_input,
    "models/anomaly_detection_v2.onnx",
    input_names=["sensor_input"],
    output_names=["prediction", "confidence"],
    dynamic_axes={"sensor_input": {0: "batch_size"}},
    opset_version=17,
)
```

### 1.4 Comparaison des formats

| Format | Taille | Latence (CPU) | Précision | Usage recommandé |
| :--- | :--- | :--- | :--- | :--- |
| TensorFlow (.h5) | 100% | 1x (référence) | Référence | Développement / Validation |
| TFLite FP16 | ~50% | 2-3x plus rapide | Quasi-identique | Jetson, Raspberry Pi 4+ |
| TFLite INT8 | ~25% | 4-5x plus rapide | Légère perte (<2%) | Microcontrôleurs, Google Coral |
| ONNX (FP32) | ~100% | 1-2x plus rapide | Identique | Multi-plateforme, Windows ML |
| ONNX (INT8) | ~25% | 3-5x plus rapide | Légère perte | Qualcomm, AMD, Intel OpenVINO |

---

## 2. Déploiement sur Dispositif Edge

### 2.1 NVIDIA Jetson (Nano / Orin / Xavier)

```bash
# Installation des dépendances sur Jetson
sudo apt update
sudo apt install -y python3-pip libopenblas-dev libjpeg-dev
pip3 install numpy onnxruntime-gpu

# Copie du modèle optimisé
scp models/anomaly_detection_v2.tflite user@jetson-ip:/opt/edge-models/

# Exécution de l'inférence
python3 edge_inference.py --model /opt/edge-models/anomaly_detection_v2.tflite \
                          --source mqtt://broker.local:1883/vibrations \
                          --threshold 0.85
```

### 2.2 Raspberry Pi (3B+ / 4 / 5)

```python
import tflite_runtime.interpreter as tflite
import numpy as np

class EdgeInference:
    def __init__(self, model_path: str):
        self.interpreter = tflite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, sensor_data: np.ndarray) -> dict:
        """Exécute l'inférence sur des données capteur."""
        # Redimensionnement si nécessaire
        if sensor_data.shape != self.input_details[0]["shape"]:
            sensor_data = sensor_data.reshape(self.input_details[0]["shape"])

        self.interpreter.set_tensor(self.input_details[0]["index"],
                                    sensor_data.astype(np.float32))
        self.interpreter.invoke()

        prediction = self.interpreter.get_tensor(self.output_details[0]["index"])
        confidence = float(prediction[0][0])

        return {
            "anomaly": confidence > 0.85,
            "confidence": confidence,
            "timestamp": time.time(),
        }

# Utilisation
model = EdgeInference("models/anomaly_detection_v2.tflite")
# Données simulées (128 échantillons de vibration)
sensor_data = np.random.randn(128)
result = model.predict(sensor_data)
print(f"Anomalie détectée : {result['anomaly']} (confiance: {result['confidence']:.2%})")
```

### 2.3 Google Coral (TPU Edge)

```python
from pycoral.adapters import common, classify
from pycoral.utils.edgetpu import make_interpreter

# Chargement du modèle compilé pour Edge TPU
interpreter = make_interpreter("models/anomaly_detection_v2_edgetpu.tflite")
interpreter.allocate_tensors()

# Inférence
common.set_input(interpreter, sensor_data_flattened)
interpreter.invoke()
result = classify.get_classes(interpreter, top_k=1)
```

---

## 3. Intégration aux Flux Industriels

### 3.1 Connexion aux capteurs via MQTT

```python
import paho.mqtt.client as mqtt
import json

class EdgeMQTTClient:
    def __init__(self, broker: str, port: int = 1883, model: EdgeInference = None):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.model = model
        self.broker = broker
        self.port = port

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connecté au broker MQTT (code: {rc})")
        # Souscription aux topics capteurs
        client.subscribe("factory/ligne1/+/vibration")
        client.subscribe("factory/ligne1/+/temperature")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            # Prétraitement et inférence
            sensor_data = np.array(payload["values"], dtype=np.float32)
            result = self.model.predict(sensor_data)

            if result["anomaly"]:
                # Envoi d'une alerte
                alert = {
                    "machine": msg.topic.split("/")[2],
                    "type": "anomaly_detected",
                    "confidence": result["confidence"],
                    "timestamp": result["timestamp"],
                }
                client.publish("factory/alerts", json.dumps(alert))
                print(f"⚠️ Alerte envoyée : {alert}")

        except Exception as e:
            print(f"Erreur de traitement : {e}")

    def start(self):
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

# Démarrage
client = EdgeMQTTClient(broker="mqtt.factory.local", model=model)
client.start()
```

### 3.2 Connexion via Modbus TCP

```python
from pymodbus.client import ModbusTcpClient

def read_modbus_sensors(plc_ip: str, registers: list[int]) -> np.ndarray:
    """Lit des registres Modbus et retourne un tableau numpy."""
    client = ModbusTcpClient(plc_ip, port=502)
    client.connect()

    values = []
    for reg in registers:
        result = client.read_holding_registers(reg, count=4)  # 4 registres = 1 float32
        if not result.isError():
            # Conversion IEEE 754 (32 bits)
            import struct
            bytes_val = b"".join([r.to_bytes(2, "big") for r in result.registers])
            values.append(struct.unpack(">f", bytes_val)[0])

    client.close()
    return np.array(values)

# Utilisation
sensor_data = read_modbus_sensors("192.168.1.100", [40001, 40005, 40009])
```

---

## 4. Benchmark et Surveillance

### 4.1 Métriques de performance

```python
import time

def benchmark_model(model_path: str, iterations: int = 1000):
    """Mesure les performances d'un modèle Edge."""
    interpreter = tflite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()

    input_data = np.random.randn(1, 128).astype(np.float32)
    latencies = []

    for _ in range(iterations):
        start = time.perf_counter()
        interpreter.set_tensor(interpreter.get_input_details()[0]["index"], input_data)
        interpreter.invoke()
        _ = interpreter.get_tensor(interpreter.get_output_details()[0]["index"])
        latencies.append((time.perf_counter() - start) * 1000)  # ms

    return {
        "latence_moyenne_ms": np.mean(latencies),
        "latence_p99_ms": np.percentile(latencies, 99),
        "fps": 1000 / np.mean(latencies),
        "model_size_kb": os.path.getsize(model_path) / 1024,
    }
```

### 4.2 Surveillance continue

```python
# Remonter les métriques vers un dashboard
metrics = {
    "fps": 45.2,
    "latence_moyenne": 22.1,  # ms
    "anomalies_detectees": 12,
    "confiance_moyenne": 0.93,
    "uptime_hours": 168,
    "temperature_cpu": 65.4,
    "utilisation_memoire_pct": 72,
}
# Publier sur MQTT pour Grafana/InfluxDB
client.publish("factory/edge/metrics", json.dumps(metrics))
```

### Performance attendue par plateforme

| Plateforme | Modèle | TFLite FP16 | TFLite INT8 | ONNX |
| :--- | :--- | :--- | :--- | :--- |
| **Jetson Orin NX** | Anomaly (128 entrées) | ~2000 FPS | ~3500 FPS | ~1800 FPS |
| **Raspberry Pi 5** | Anomaly (128 entrées) | ~120 FPS | ~250 FPS | ~100 FPS |
| **Google Coral** | MobileNetV2 | N/A | ~400 FPS | N/A |
| **ESP32-S3** | TinyML (8KB) | N/A | ~50 FPS | N/A |

---

## 5. Sécurité et Maintenance

### 5.1 Bonnes pratiques de sécurité

- Signer les modèles déployés (vérification de l'intégrité via checksum SHA256).
- Isoler le processus d'inférence (conteneur Docker ou namespace systemd).
- Chiffrer les communications MQTT/Modbus (TLS 1.3, certificats mutuels).
- Mettre à jour les modèles par OTA (Over-The-Air) avec validation de version.
- Logger toutes les anomalies de prédiction pour audit.

### 5.2 Cycle de mise à jour

```bash
# Vérification de version et mise à jour OTA
curl -s https://ml-registry.factory.local/v2/models/anomaly-detection/versions
# Téléchargement du nouveau modèle
wget https://ml-registry.factory.local/v2/models/anomaly-detection/v3/anomaly_detection_v3.tflite
# Validation du checksum
sha256sum -c anomaly_detection_v3.tflite.sha256
# Activation (rechargement à chaud via signal)
kill -USR1 $(pgrep -f edge_inference.py)
```

---

## Pièges Courants (Common Pitfalls)

1. **Quantification sans calibration** : La quantification INT8 sans `representative_dataset` dégrade fortement la précision. Toujours fournir un échantillon représentatif de données réelles.

2. **Décalage de distribution (data drift)** : Les données capteurs évoluent dans le temps (usure mécanique, changement de saison). Mettre en place une surveillance de la dérive et un ré-entraînement périodique.

3. **Latence réseau Modbus** : Les bus Modbus RS-485 peuvent ajouter 10-50ms de latence. Ne pas inclure le temps de lecture des capteurs dans le budget temps réel de l'inférence.

4. **Surchauffe du dispositif Edge** : L'inférence intensive sur Jetson/Raspberry peut faire monter la température >85°C. Implémenter un throttling et une ventilation adaptée.

5. **Consommation mémoire des modèles** : Un modèle TFLite de 50MB peut saturer la RAM d'un Raspberry Pi 3B+ (1GB). Utiliser la quantification et le profiling mémoire avant déploiement.

6. **Version des runtime incompatibles** : `tflite_runtime` et `onnxruntime` ont des versions spécifiques selon la plateforme. Tester la compatibilité en environnement cible.

7. **Absence de fallback** : En cas d'échec de l'inférence, le système doit pouvoir basculer en mode dégradé (seuils fixes, alarme directe). Ne jamais bloquer la supervision.

---

## Liste de vérification (Checklist)

- [ ] Le modèle est entraîné et validé sur des données industrielles représentatives.
- [ ] La conversion TFLite/ONNX inclut une optimisation (FP16 ou INT8 avec calibration).
- [ ] Le modèle déployé est testé sur la plateforme cible (Jetson, Pi, Coral).
- [ ] La latence d'inférence est mesurée et inférieure au budget temps réel requis.
- [ ] La connectivité MQTT/Modbus est configurée avec TLS si le réseau l'expose.
- [ ] Les métriques de performance (FPS, latence, confiance) sont remontées à un dashboard.
- [ ] Un mécanisme de détection de dérive (data drift) est en place.
- [ ] La mise à jour OTA est testée (téléchargement, validation, activation).
- [ ] Le mode dégradé (fallback) est implémenté et documenté.
- [ ] La température et l'utilisation mémoire du dispositif Edge sont surveillées.
- [ ] Le modèle signé et son checksum SHA256 sont vérifiés après déploiement.
