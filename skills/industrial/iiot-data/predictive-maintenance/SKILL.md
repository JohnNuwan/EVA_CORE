---
name: predictive-maintenance
description: "Analyser des capteurs et détecter des anomalies."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [predictive-maintenance, machine-learning, vibration-analysis, fft, anomaly-detection, python]
    related_skills: [digital-twins, industrial-edge, oee-performance, industrial-analytics-grafana]
---

# Maintenance Prédictive & Traitement de Données Capteurs

## Exemple Python : Modèle Basique pour des Données Simulées
```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Simuler des données de capteur
np.random.seed(42)
time = np.linspace(0, 100, 1000)
vibration = np.sin(time) + np.random.normal(scale=0.1, size=time.shape)
failure = (vibration > 0.8).astype(int)  # Panne lorsqu'une vibration dépasse un seuil

# Préparer les données d'entraînement
X = np.array([vibration[:-1], np.gradient(vibration)]).T  # Gradient comme caractéristique
Y = failure[1:]
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Modèle : Forêt aléatoire
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, Y_train)

# Évaluer le modèle
predictions = model.predict(X_test)
print(classification_report(Y_test, predictions))

# Visualisation
def plot_data():
    plt.plot(time, vibration, label="Vibration")
    plt.scatter(time[failure == 1], vibration[failure == 1], color='r', label="Défaillance")
    plt.legend()
    plt.show()

plot_data()
```
Cet exemple montre comment développer un modèle de classification supervisé pour prédire des défaillances à partir de signaux de capteurs.

La **maintenance prédictive** consiste à anticiper les pannes des machines industrielles en analysant en temps réel leurs indicateurs physiques (vibrations, température, courant consommé). Contrairement à la maintenance préventive (qui se base sur un calendrier fixe), la maintenance prédictive réagit à la dégradation réelle des performances de la machine.

Cette compétence guide l'agent Helios pour écrire des scripts d'analyse de données de capteurs, notamment :
- L'analyse fréquentielle de signaux vibratoires (Transformée de Fourier Rapide - FFT) avec `scipy`.
- La détection d'anomalies de comportement avec l'algorithme `Isolation Forest` de `scikit-learn`.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'extraire les fréquences caractéristiques d'un signal de capteur de vibration.
- D'écrire un script de détection de dérives de température ou de surconsommation électrique.
- D'implémenter un modèle léger d'apprentissage automatique (Machine Learning) pour classifier des états de marche machine (sain vs dégradé).

**Ne pas utiliser pour :**
- La programmation d'automates PLC de sécurité (Safety) gérant les arrêts d'urgence physiques.

---

## 1. Analyse Vibratoire avec la FFT (Fast Fourier Transform)

L'analyse de vibrations permet de détecter des défauts mécaniques (balourd, désalignement, usure de roulement) sur les moteurs tournants. On transforme le signal temporel en spectre fréquentiel :

```python
import numpy as np
from scipy.fft import fft, fftfreq

def analyze_vibration(signal: np.ndarray, sampling_rate: float):
    """Calcule le spectre fréquentiel d'un signal temporel.
    
    Args:
        signal: Tableau numpy contenant les mesures d'accélération (m/s²).
        sampling_rate: Fréquence d'échantillonnage du capteur en Hz.
    """
    n = len(signal)
    
    # Calcul de la FFT
    yf = fft(signal)
    # Calcul des fréquences associées
    xf = fftfreq(n, 1 / sampling_rate)
    
    # On ne conserve que les fréquences positives (première moitié du tableau)
    frequencies = xf[:n//2]
    amplitudes = (2.0/n) * np.abs(yf[:n//2])
    
    # Recherche de la fréquence dominante (pic d'amplitude)
    dominant_idx = np.argmax(amplitudes)
    dominant_freq = frequencies[dominant_idx]
    
    return {
        "frequencies": frequencies.tolist(),
        "amplitudes": amplitudes.tolist(),
        "dominant_frequency_hz": float(dominant_freq),
        "max_amplitude": float(amplitudes[dominant_idx])
    }
```

---

## 2. Détection d'Anomalies de Production avec Isolation Forest

Pour détecter des dérives sur un équipement (ex: surchauffe lente combinée à une hausse de pression), l'algorithme d'apprentissage non supervisé *Isolation Forest* isole les points de données atypiques.

```python
import pandas as pd
from sklearn.ensemble import IsolationForest

def train_anomaly_detector(historical_data: pd.DataFrame, features: list):
    """Entraîne un modèle de détection d'anomalies sur les données de fonctionnement nominales.
    
    Args:
        historical_data: DataFrame contenant les historiques de capteurs.
        features: Liste des colonnes de capteurs à analyser (ex: ['temp', 'pressure']).
    """
    X = historical_data[features]
    
    # Initialisation du modèle
    # contamination = 0.01 signifie qu'on estime qu'environ 1% des données historiques peuvent être des anomalies
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X)
    
    return model

def check_for_anomalies(model, current_readings: pd.DataFrame, features: list):
    """Vérifie si les mesures actuelles contiennent des anomalies."""
    X = current_readings[features]
    # predict() renvoie 1 pour une valeur normale, et -1 pour une anomalie
    predictions = model.predict(X)
    
    anomalies_detected = current_readings[predictions == -1]
    return anomalies_detected
```

---

## Pièges Courants

1. **Données historiques polluées pendant l'entraînement :**
   * *Erreur :* Entraîner un modèle de détection d'anomalies sur une période historique contenant déjà des pannes ou des phases d'arrêt de maintenance. Le modèle considérera ces phases de panne comme "normales".
   * *Correction :* Nettoyer les données d'entraînement pour ne conserver que les phases de fonctionnement sain et de production active.

2. **Échantillonnage de signal insuffisant (Théorème de Shannon-Nyquist) :**
   * *Erreur :* Essayer de détecter un défaut de roulement haute fréquence (ex: 2000 Hz) avec un capteur échantillonné à 1000 Hz.
   * *Correction :* La fréquence d'échantillonnage doit être au moins double de la fréquence maximale que l'on souhaite analyser (ex: échantillonner à 4000 Hz minimum pour capter du 2000 Hz).

---

## Liste de vérification (Checklist)

- [ ] La fréquence d'échantillonnage spécifiée pour la FFT respecte la règle de Shannon-Nyquist (au moins double de la fréquence cible).
- [ ] Les données d'apprentissage pour la détection d'anomalies ont été filtrées pour exclure les périodes d'arrêt et de maintenance.
- [ ] L'extraction de caractéristiques (Features) gère les valeurs manquantes (`NaN`) pour éviter des plantages de modèles de Machine Learning.
- [ ] Les alertes de détection d'anomalies intègrent un filtre de persistance pour éviter les fausses alertes sur des pics isolés et transitoires.

