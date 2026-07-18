---
name: energy-monitoring
description: "Collecter des données énergétiques et calculer des KPIs."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [energy, iso-50001, power-metering, modbus, grafana, influxdb, enpi, industrial-automation]
    related_skills: [plc-connectivity, industrial-edge, industrial-analytics-grafana, oee-performance]
---

# Gestion Énergétique Industrielle & ISO 50001

## Vue d'ensemble

La **gestion énergétique industrielle** consiste à mesurer, surveiller et optimiser la consommation d'énergie (électricité, gaz, eau, air comprimé, vapeur) d'un site de production. La norme **ISO 50001** fournit le cadre méthodologique pour un Système de Management de l'Énergie (SMÉ) structuré.

Cette compétence guide l'agent Helios pour :
1. Collecter des données de compteurs d'énergie via **Modbus TCP** (Schneider PM5xxx, Siemens PAC3200, Janitza UMG).
2. Calculer les **indicateurs de performance énergétique (EnPI)** : kWh/tonne, kWh/pièce, coût/lot.
3. Concevoir des **dashboards Grafana** de suivi énergétique temps réel alimentés par InfluxDB.
4. Détecter les **dérives de consommation** à l'aide de l'algorithme CUSUM (Cumulative Sum).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De collecter des données depuis des compteurs d'énergie industriels (Schneider, Siemens, Janitza).
- De calculer des KPIs énergétiques normalisés (ISO 50001 EnPI, ligne de base énergétique).
- De concevoir un dashboard de supervision énergétique temps réel.
- D'analyser des courbes de charge ou de détecter des surconsommations anormales.
- D'optimiser la facture énergétique d'un site (effacement, décalage de charges).

**Ne pas utiliser pour :**
- La programmation de régulation PID sur des équipements de chauffage/ventilation (utiliser `pid-tuning-control` ou `hvac-industrial-ventilation`).
- La conception de schémas électriques de tableaux de distribution (utiliser `electrical-schematics-eplan`).

---

## 1. Collecte de Données Modbus TCP depuis un Compteur Schneider PM5xxx

Les compteurs Schneider PowerLogic PM5xxx exposent leurs mesures via des registres Modbus Holding Registers. Voici un script de collecte robuste :

```python
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
import time
import json

# Configuration du compteur
METER_IP = "192.168.1.50"
METER_PORT = 502
UNIT_ID = 1

# Registres Schneider PM5xxx (Holding Registers)
REGISTERS = {
    "voltage_L1_N":    {"address": 3027, "count": 2, "unit": "V"},
    "voltage_L2_N":    {"address": 3029, "count": 2, "unit": "V"},
    "voltage_L3_N":    {"address": 3031, "count": 2, "unit": "V"},
    "current_L1":      {"address": 2999, "count": 2, "unit": "A"},
    "current_L2":      {"address": 3001, "count": 2, "unit": "A"},
    "current_L3":      {"address": 3003, "count": 2, "unit": "A"},
    "active_power":    {"address": 3059, "count": 2, "unit": "kW"},
    "reactive_power":  {"address": 3067, "count": 2, "unit": "kVAR"},
    "power_factor":    {"address": 3083, "count": 2, "unit": ""},
    "frequency":       {"address": 3109, "count": 2, "unit": "Hz"},
    "total_energy":    {"address": 3203, "count": 4, "unit": "kWh"},
}


def read_float32(client, address, count=2, unit_id=1):
    """Lit un registre Modbus et décode un Float32 (Big-Endian, Word-swap).

    Args:
        client: Instance du client Modbus TCP.
        address: Adresse du premier registre Holding Register.
        count: Nombre de registres à lire (2 pour un Float32).
        unit_id: Adresse esclave Modbus.

    Returns:
        float: Valeur décodée, ou None en cas d'erreur.
    """
    result = client.read_holding_registers(address, count, slave=unit_id)
    if result.isError():
        return None
    decoder = BinaryPayloadDecoder.fromRegisters(
        result.registers, byteorder=Endian.BIG, wordorder=Endian.BIG
    )
    return round(decoder.decode_32bit_float(), 3)


def collect_meter_data(ip=METER_IP, port=METER_PORT, unit_id=UNIT_ID):
    """Collecte complète des mesures d'un compteur Schneider PM5xxx.

    Args:
        ip: Adresse IP du compteur.
        port: Port Modbus TCP (502 par défaut).
        unit_id: Identifiant d'unité Modbus.

    Returns:
        dict: Dictionnaire contenant toutes les mesures horodatées.
    """
    client = ModbusTcpClient(ip, port=port, timeout=5)

    if not client.connect():
        raise ConnectionError(f"Impossible de se connecter au compteur {ip}:{port}")

    try:
        data = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

        for name, reg in REGISTERS.items():
            value = read_float32(client, reg["address"], reg["count"], unit_id)
            data[name] = {"value": value, "unit": reg["unit"]}

        return data
    finally:
        client.close()


if __name__ == "__main__":
    reading = collect_meter_data()
    print(json.dumps(reading, indent=2, ensure_ascii=False))
```

---

## 2. Calcul des Indicateurs de Performance Énergétique (EnPI)

Les EnPI permettent de normaliser la consommation par rapport à un facteur de production (tonnes, pièces, heures de marche) :

```python
import pandas as pd


def calculate_enpi(energy_data: pd.DataFrame, production_column: str,
                   energy_column: str = "kwh") -> pd.DataFrame:
    """Calcule l'indicateur de performance énergétique (EnPI) et la ligne de base.

    Args:
        energy_data: DataFrame contenant les colonnes de temps, énergie et production.
        production_column: Nom de la colonne de production (ex: 'tonnes', 'pieces').
        energy_column: Nom de la colonne d'énergie consommée en kWh.

    Returns:
        pd.DataFrame: DataFrame enrichi avec les colonnes EnPI et ligne de base.
    """
    df = energy_data.copy()

    # Calcul de l'EnPI brut : kWh par unité de production
    df["enpi"] = df[energy_column] / df[production_column].replace(0, float("nan"))

    # Ligne de base énergétique (régression linéaire simple)
    valid = df.dropna(subset=["enpi"])
    if len(valid) >= 2:
        coeffs = pd.np.polyfit(valid[production_column], valid[energy_column], 1)
        df["baseline_kwh"] = coeffs[0] * df[production_column] + coeffs[1]
        df["savings_kwh"] = df["baseline_kwh"] - df[energy_column]
        df["savings_pct"] = (df["savings_kwh"] / df["baseline_kwh"]) * 100
    else:
        df["baseline_kwh"] = df[energy_column]
        df["savings_kwh"] = 0.0
        df["savings_pct"] = 0.0

    return df
```

---

## 3. Détection de Dérives de Consommation (Algorithme CUSUM)

L'algorithme **CUSUM (Cumulative Sum)** détecte les changements progressifs de moyenne dans une série temporelle de consommation :

```python
import numpy as np


def cusum_detection(values: np.ndarray, threshold: float = 5.0,
                    drift: float = 1.0) -> dict:
    """Applique l'algorithme CUSUM pour détecter les dérives de consommation.

    Args:
        values: Série de mesures de consommation.
        threshold: Seuil de déclenchement d'alerte (sensibilité).
        drift: Tolérance de dérive acceptable autour de la moyenne.

    Returns:
        dict: Résultat contenant les indices de dérive détectés et les cumuls.
    """
    mean_val = np.mean(values)
    cumsum_pos = np.zeros(len(values))
    cumsum_neg = np.zeros(len(values))
    alarms_high = []
    alarms_low = []

    for i in range(1, len(values)):
        deviation = values[i] - mean_val
        cumsum_pos[i] = max(0, cumsum_pos[i - 1] + deviation - drift)
        cumsum_neg[i] = max(0, cumsum_neg[i - 1] - deviation - drift)

        if cumsum_pos[i] > threshold:
            alarms_high.append(i)
            cumsum_pos[i] = 0  # Réinitialisation après alarme

        if cumsum_neg[i] > threshold:
            alarms_low.append(i)
            cumsum_neg[i] = 0

    return {
        "mean_baseline": float(mean_val),
        "high_drift_indices": alarms_high,
        "low_drift_indices": alarms_low,
        "cumsum_positive": cumsum_pos.tolist(),
        "cumsum_negative": cumsum_neg.tolist(),
    }
```

---

## 4. Architecture de Référence : Compteurs → InfluxDB → Grafana

```text
[Compteur PM5xxx]  ──Modbus TCP──▶  [Script Python / Telegraf]
[Compteur PAC3200] ──Modbus TCP──▶  [sur passerelle Edge IOT2050]
[Compteur Janitza] ──Modbus TCP──▶         │
                                           ▼
                                    [InfluxDB 2.x]
                                    (Bucket: energy)
                                    (Retention: 1 an)
                                           │
                                           ▼
                                    [Grafana Dashboard]
                                    - Courbe de charge 24h
                                    - EnPI temps réel
                                    - Alertes CUSUM
                                    - Répartition par atelier
```

### Requête Flux pour InfluxDB (consommation horaire) :

```flux
from(bucket: "energy")
  |> range(start: -24h)
  |> filter(fn: (r) => r._measurement == "power_meter")
  |> filter(fn: (r) => r._field == "active_power")
  |> aggregateWindow(every: 1h, fn: mean, createEmpty: false)
  |> yield(name: "hourly_avg_power")
```

---

## Pièges Courants

1. **Ordonnancement des octets (Byte Order) incorrect lors de la lecture Modbus :**
   * *Erreur :* Le compteur renvoie des valeurs Float32 absurdes (ex: `1.5e+38` ou `NaN`).
   * *Correction :* Vérifier l'ordre des octets (Endianness) dans la documentation du compteur. Schneider utilise Big-Endian/Big-Endian, Siemens utilise Big-Endian/Little-Endian (word-swap). Tester les 4 combinaisons possibles (`BB`, `BL`, `LB`, `LL`).

2. **Compteur d'énergie totale qui redémarre à zéro après une coupure :**
   * *Erreur :* Le compteur d'énergie cumulée (`total_energy`) se réinitialise lors d'un redémarrage du compteur, entraînant un pic négatif dans les calculs de consommation horaire.
   * *Correction :* Calculer la consommation par différence entre deux lectures consécutives et ignorer les différences négatives (rollover).

3. **Facteur de puissance (cos φ) mal interprété :**
   * *Erreur :* Confondre la puissance active (kW) et la puissance apparente (kVA) lors du calcul des EnPI. Les factures EDF se basent sur la puissance active mais pénalisent un mauvais facteur de puissance.
   * *Correction :* Toujours utiliser la puissance active (`active_power` en kW) pour les calculs d'EnPI et surveiller séparément le facteur de puissance pour la compensation réactive.

---

## Références

- **ISO 50001:2018** — Systèmes de management de l'énergie (exigences et recommandations).
- **Schneider Electric PM5xxx** — Modbus Register Map (doc. EAV15109).
- **Siemens PAC3200** — Manuel de communication Modbus TCP.
- **CUSUM (Page's Test)** — Algorithme de détection séquentielle de changement de moyenne.

---

## Liste de vérification (Checklist)

- [ ] L'ordre des octets (Endianness) du décodeur Modbus correspond à la documentation du compteur.
- [ ] Le script de collecte gère les compteurs d'énergie cumulée avec détection de rollover.
- [ ] Les EnPI sont normalisés par un facteur de production pertinent (tonnes, pièces, heures de marche) et non par le temps calendaire seul.
- [ ] Le dashboard Grafana affiche la courbe de charge, les EnPI temps réel et les alertes CUSUM.
- [ ] La fréquence de collecte est adaptée (1s pour la puissance instantanée, 15min pour l'historisation longue durée).

