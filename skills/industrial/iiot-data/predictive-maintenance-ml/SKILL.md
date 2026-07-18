---
name: predictive-maintenance-ml
description: "Développer des modèles ML/DL pour la maintenance prédictive sur séries temporelles industrielles."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - predictive-maintenance
      - deep-learning
      - time-series
      - tensorflow
      - pytorch
      - lstm
      - autoencoder
      - anomaly-detection
      - vibration-analysis
      - fft
      - stft
      - rul
      - remaining-useful-life
      - condition-monitoring
      - cmms
      - scikit-learn
      - mlops
      - mlflow
      - edge-ai
    related_skills:
      - predictive-maintenance
      - historian-timeseries
      - oee-performance
      - industrial-edge
      - computer-vision-quality
---

# Maintenance Prédictive par Machine Learning et Deep Learning

## Vue d'ensemble

La **maintenance prédictive** utilise des modèles ML/DL pour anticiper les défaillances des équipements industriels à partir de données capteurs, historiques de maintenance, et conditions opératoires. Cette compétence couvre :

- **Détection d'anomalies** — Identifier les comportements anormaux avant défaillance
- **RUL (Remaining Useful Life)** — Prédire la durée de vie restante d'un composant
- **Classification de défauts** — Diagnostiquer le type de défaillance
- **Détection de dérive** — Surveiller la dégradation progressive

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De développer un modèle de prédiction de défaillance pour un équipement
- D'analyser des données de vibration pour la détection de défauts de roulements
- De mettre en place un pipeline de maintenance prédictive
- D'entraîner un modèle LSTM/Autoencoder sur des données de capteurs
- De déployer un modèle de prédiction sur un edge device
- D'optimiser les intervalles de maintenance basés sur l'état réel (CBM)

---

## 1. Acquisition et Préparation des Données

### 1.1 Sources de données

| Source | Protocole | Type de données | Fréquence |
|:-------|:----------|:----------------|:----------|
| Capteurs IoT | OPC UA, MQTT | Température, pression, vibration, courant | 1 Hz – 10 kHz |
| Historien | Pi, Canary, InfluxDB | Aggrégations temps réel | 1 min – 1 h |
| CMMS/GMAO | REST, SQL | Interventions, pannes, pièces changées | Événementiel |
| PLC | S7, Modbus | Signaux machine (run, speed, load) | 100 ms – 1 s |
| Caméras | MQTT, FTP | Images, vidéos inspection | Minuteries |

### 1.2 Pipeline de préparation

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def prepare_timeseries(data: pd.DataFrame, target_col: str = "failure",
                       window_size: int = 100, stride: int = 10) -> tuple:
    """
    Prépare des séries temporelles pour l'apprentissage supervisé.

    Args:
        data: DataFrame avec timestamp en index, colonnes = signaux
        target_col: Colonne cible (0 = normal, 1 = défaillance)
        window_size: Taille de la fenêtre glissante
        stride: Pas entre fenêtres

    Returns:
        (X_train, X_test, y_train, y_test)
    """
    signals = data.drop(columns=[target_col])
    y = data[target_col]

    X_windows = []
    y_windows = []
    for start in range(0, len(data) - window_size, stride):
        X_windows.append(signals.iloc[start:start + window_size].values)
        # La cible est la valeur maximale dans la fenêtre
        y_windows.append(y.iloc[start:start + window_size].max())

    X = np.array(X_windows)
    y = np.array(y_windows)
    return train_test_split(X, y, test_size=0.2, random_state=42)
```

---

## 2. Feature Engineering pour Données Vibratoires

### 2.1 Features temporelles

```python
import numpy as np
from scipy import stats

def extract_time_domain_features(signal: np.ndarray) -> dict:
    """Extrait les features temporelles d'un signal vibratoire."""
    features = {
        "rms": np.sqrt(np.mean(signal ** 2)),                     # Root Mean Square
        "peak": np.max(np.abs(signal)),                            # Crête
        "peak_to_peak": np.ptp(signal),                            # Crête-à-crête
        "crest_factor": np.max(np.abs(signal)) / np.sqrt(np.mean(signal ** 2)),
        "kurtosis": stats.kurtosis(signal),                        # Aplatissement
        "skewness": stats.skew(signal),                            # Asymétrie
        "variance": np.var(signal),
        "std": np.std(signal),
        "form_factor": np.sqrt(np.mean(signal ** 2)) / np.mean(np.abs(signal)),
        "impulse_factor": np.max(np.abs(signal)) / np.mean(np.abs(signal)),
        "clearance_factor": np.max(np.abs(signal)) / (np.mean(np.sqrt(np.abs(signal))) ** 2),
    }
    return features
```

### 2.2 Features fréquentielles (FFT)

```python
from scipy.fft import fft, fftfreq

def extract_frequency_features(signal: np.ndarray, sampling_rate: float = 1000.0) -> dict:
    """Extrait les features fréquentielles via FFT."""
    n = len(signal)
    fft_vals = np.abs(fft(signal))[:n // 2]
    freqs = fftfreq(n, 1 / sampling_rate)[:n // 2]

    features = {
        "spectral_energy": np.sum(fft_vals ** 2) / n,
        "spectral_centroid": np.sum(freqs * fft_vals) / np.sum(fft_vals),
        "spectral_spread": np.sqrt(np.sum((freqs - np.average(freqs, weights=fft_vals)) ** 2) / np.sum(fft_vals)),
        "spectral_rolloff_90": np.min(np.where(np.cumsum(fft_vals) >= 0.9 * np.sum(fft_vals))[0]),
    }
    # Bande fréquentielle ISO 10816 (10–1000 Hz)
    mask_1x = (freqs >= sampling_rate * 0.9) & (freqs <= sampling_rate * 1.1)
    features["amplitude_1x"] = float(np.sum(fft_vals[mask_1x]))

    return features
```

### 2.3 Spectrogramme (STFT)

```python
from scipy.signal import spectrogram

def extract_spectrogram(signal: np.ndarray, fs: float = 1000.0,
                        nperseg: int = 256) -> np.ndarray:
    """Calcule le spectrogramme pour analyse temps-fréquence."""
    f, t, Sxx = spectrogram(signal, fs=fs, nperseg=nperseg)
    return Sxx  # Shape: (freq_bins, time_bins)
```

---

## 3. Modèles de Deep Learning

### 3.1 LSTM pour séries temporelles

```python
import tensorflow as tf
from tensorflow.keras import layers, models

def build_lstm_model(input_shape: tuple, lstm_units: list = [64, 32],
                     dropout: float = 0.2) -> tf.keras.Model:
    """Construit un modèle LSTM pour prédiction de séries temporelles.

    Args:
        input_shape: (window_size, n_features)
        lstm_units: Liste des unités LSTM par couche
        dropout: Taux de dropout

    Returns:
        Modèle Keras compilé
    """
    model = models.Sequential()
    model.add(layers.Input(shape=input_shape))

    for i, units in enumerate(lstm_units):
        return_seq = i < len(lstm_units) - 1
        model.add(layers.LSTM(units, return_sequences=return_seq))
        model.add(layers.Dropout(dropout))
        if return_seq:
            model.add(layers.BatchNormalization())

    model.add(layers.Dense(32, activation="relu"))
    model.add(layers.Dropout(dropout))
    model.add(layers.Dense(1, activation="sigmoid"))

    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=["accuracy", tf.keras.metrics.AUC()])
    return model
```

### 3.2 Autoencodeur pour détection d'anomalies

```python
def build_autoencoder(input_dim: int, encoding_dim: int = 16) -> tf.keras.Model:
    """Autoencodeur pour détection d'anomalies par reconstruction.

    L'erreur de reconstruction (MSE) sert de score d'anomalie.
    """
    input_layer = layers.Input(shape=(input_dim,))
    encoded = layers.Dense(encoding_dim * 2, activation="relu")(input_layer)
    encoded = layers.Dense(encoding_dim, activation="relu")(encoded)

    decoded = layers.Dense(encoding_dim * 2, activation="relu")(encoded)
    decoded = layers.Dense(input_dim, activation="linear")(decoded)

    autoencoder = models.Model(input_layer, decoded)
    autoencoder.compile(optimizer="adam", loss="mse")
    return autoencoder

def detect_anomalies(ae_model: tf.keras.Model, X: np.ndarray,
                     threshold: float = None) -> np.ndarray:
    """Détecte les anomalies avec un autoencodeur.

    Args:
        ae_model: Autoencodeur entraîné
        X: Données à évaluer
        threshold: Seuil (None = moyenne + 3*sigma)

    Returns:
        Array booléen (True = anomalie)
    """
    reconstructions = ae_model.predict(X)
    mse = np.mean((X - reconstructions) ** 2, axis=1)

    if threshold is None:
        threshold = np.mean(mse) + 3 * np.std(mse)

    return mse > threshold
```

### 3.3 Transformers pour séries temporelles (TimesNet / PatchTST)

```python
def build_timesnet_transformer(input_shape: tuple, num_classes: int = 1) -> tf.keras.Model:
    """Modèle basé sur TimesNet pour séries temporelles.

    Note: TimesNet utilise une architecture Inception-like avec FFT
    pour capturer les motifs temporels périodiques.
    """
    inputs = layers.Input(shape=input_shape)
    x = layers.Conv1D(64, kernel_size=3, padding="same", activation="relu")(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.Conv1D(128, kernel_size=3, padding="same", activation="relu")(x)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="sigmoid")(x)

    model = models.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="binary_crossentropy",
                  metrics=["accuracy"])
    return model
```

---

## 4. Détection de Dérive (Concept Drift)

### 4.1 Data Drift Detection

```python
from scipy.stats import ks_2samp, wasserstein_distance

def detect_drift(reference: np.ndarray, current: np.ndarray,
                 method: str = "ks") -> dict:
    """Détecte le drift entre deux distributions.

    Args:
        reference: Distribution de référence (normal)
        current: Distribution actuelle
        method: "ks" (Kolmogorov-Smirnov) ou "wasserstein"

    Returns:
        Dict avec p-value, statistic, warning
    """
    if method == "ks":
        stat, p_value = ks_2samp(reference, current)
        drift = p_value < 0.05
        return {
            "method": "KS test",
            "statistic": float(stat),
            "p_value": float(p_value),
            "drift_detected": bool(drift),
            "severity": "CRITICAL" if stat > 0.3 else "WARNING" if stat > 0.15 else "OK"
        }
    elif method == "wasserstein":
        distance = float(wasserstein_distance(reference, current))
        drift = distance > (3 * np.std(reference) / 10)
        return {
            "method": "Wasserstein distance",
            "distance": distance,
            "drift_detected": bool(drift),
        }
```

---

## 5. RUL Prediction

### 5.1 Modèle de régression pour RUL

```python
def build_rul_model(input_shape: tuple) -> tf.keras.Model:
    """Modèle pour prédire le RUL (Remaining Useful Life).

    Sortie : nombre de jours/heures restants avant défaillance.
    """
    inputs = layers.Input(shape=input_shape)
    x = layers.Conv1D(64, 3, padding="same", activation="relu")(inputs)
    x = layers.Conv1D(128, 3, padding="same", activation="relu")(x)
    x = layers.LSTM(64, return_sequences=True)(x)
    x = layers.LSTM(32)(x)
    x = layers.Dense(16, activation="relu")(x)
    outputs = layers.Dense(1, activation="linear")(x)  # RUL en heures

    model = models.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model

def compute_rul(degradation_curve: np.ndarray, threshold: float = 0.8,
                max_rul: float = 8760.0) -> float:
    """Calcule le RUL à partir d'une courbe de dégradation.

    Args:
        degradation_curve: Série temporelle de l'indice de dégradation
        threshold: Seuil de défaillance
        max_rul: RUL maximum en heures (1 an par défaut)

    Returns:
        RUL estimé en heures
    """
    if np.max(degradation_curve) < threshold:
        # Extrapolation linéaire
        recent_slope = np.polyfit(
            np.arange(min(10, len(degradation_curve))),
            degradation_curve[-10:], 1
        )[0]
        if recent_slope > 0:
            remaining = (threshold - degradation_curve[-1]) / recent_slope
            return min(remaining * 8760, max_rul)  # Convertir en heures
        return max_rul

    # Trouver l'instant où le seuil est atteint
    crossing = np.where(degradation_curve >= threshold)[0]
    if len(crossing) > 0:
        return float(crossing[0])  # Heures restantes
    return max_rul
```

---

## 6. Normes et Standards

### 6.1 ISO 10816 / ISO 20816

**Mesures de vibration pour machines tournantes :**

| Type de machine | Zone A (Bon) | Zone B (Alerte) | Zone C (Danger) | Zone D (Critique) |
|:----------------|:------------|:----------------|:----------------|:------------------|
| Groupe 1 (> 300 kW) | < 1.8 mm/s | 1.8 – 4.5 mm/s | 4.5 – 11.2 mm/s | > 11.2 mm/s |
| Groupe 2 (15–300 kW) | < 0.7 mm/s | 0.7 – 1.8 mm/s | 1.8 – 4.5 mm/s | > 4.5 mm/s |
| Pompes centrifuge | < 1.1 mm/s | 1.1 – 2.3 mm/s | 2.3 – 4.5 mm/s | > 4.5 mm/s |

### 6.2 ISO 13373 — Condition Monitoring

- ISO 13373-1: General guidelines
- ISO 13373-2: Processing, analysis and presentation of vibration data
- ISO 13373-3: Envelope analysis for diagnostics

---

## 7. MLOps et Déploiement

### 7.1 Pipeline complet

```python
def train_predictive_model(data_path: str, model_type: str = "lstm",
                           experiment_name: str = "pdm_experiment") -> dict:
    """Pipeline d'entraînement complet avec MLflow tracking."""
    import mlflow
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        # Chargement
        data = pd.read_csv(data_path)
        mlflow.log_param("samples", len(data))

        # Feature engineering
        features = []
        for col in ["vibration", "temperature", "current"]:
            time_features = extract_time_domain_features(data[col].values)
            features.extend(list(time_features.values()))
        mlflow.log_param("n_features", len(features))

        # Entraînement
        X_train, X_test, y_train, y_test = prepare_timeseries(data)
        model = build_lstm_model((X_train.shape[1], X_train.shape[2]))
        history = model.fit(X_train, y_train, epochs=50, batch_size=32,
                            validation_split=0.2, verbose=0)

        # Métriques
        test_loss = model.evaluate(X_test, y_test, verbose=0)
        mlflow.log_metric("test_loss", float(test_loss[0]))
        mlflow.log_metric("test_accuracy", float(test_loss[1]))

        # Sauvegarde
        mlflow.keras.log_model(model, "model")
        return {"status": "success", "test_loss": float(test_loss[0])}
```

### 7.2 Déploiement Edge

```python
def convert_to_tflite(model_path: str, output_path: str = "model.tflite") -> str:
    """Convertit un modèle Keras en TensorFlow Lite pour déploiement edge."""
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    converter.target_spec.supported_types = [tf.float16]
    tflite_model = converter.convert()

    with open(output_path, "wb") as f:
        f.write(tflite_model)
    return output_path
```

---

## 8. Références

- [TensorFlow Time Series Guide](https://www.tensorflow.org/tutorials/structured_data/time_series)
- [PyTorch Forecasting](https://pytorch-forecasting.readthedocs.io/)
- [ISO 10816 Evaluation of machine vibration](https://www.iso.org)
- [ISO 13373 Condition monitoring](https://www.iso.org)
- [Scikit-learn User Guide on Time Series](https://scikit-learn.org/stable/modules/cross_validation.html#time-series-split)
- [MLflow Time Series Tracking](https://mlflow.org/docs/latest/deep-learning/index.html)
