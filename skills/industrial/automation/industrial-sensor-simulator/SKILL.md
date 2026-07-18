---
name: industrial-sensor-simulator
description: "Simuler des capteurs et protocoles pour l'Industrie 4.0."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industrial, simulator, modbus, opc-ua, plc, sensor-simulation, virtual-commissioning]
    related_skills: [plc-connectivity, opc-ua-scanner, historian-timeseries, sparkplug-b]
---

# Simulateur Virtuel de Capteurs Industriels

## Vue d'ensemble

Le développement d'applications pour l'**Industrie 4.0** et l'IIoT exige souvent de valider la connectivité des bases de données de séries temporelles (Historians), des clients OPC UA ou des passerelles d'UNS (MQTT Sparkplug B) sans accès physique à des automates (PLC) en fonctionnement réel.

Cette compétence permet à l'agent EVA de configurer et de lancer un **serveur virtuel multi-protocoles** (Modbus TCP et OPC UA) émulant les variables et signaux physiques d'une machine industrielle (chaudière, pompe, cuve) avec des fluctuations réalistes, du bruit de mesure et des pannes simulées.

Le script d'assistance associé à cette compétence est disponible sous [sensor_simulator.py](scripts/sensor_simulator.py).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Simuler localement un automate pour tester la connectivité réseau ou valider un script d'acquisition client.
- Générer des jeux de données de télémétrie complexes (températures oscillantes, pressions) pour entraîner des algorithmes d'IA (maintenance prédictive, détection d'anomalies).
- Tester la robustesse des systèmes de supervision (SCADA/HMI) en cas de défauts ou de surcharges de signaux.

---

## 1. Table d'Adressage des Signaux Simulés (Mapping)

Le simulateur expose l'état d'une chaudière (`Boiler01`) contenant 3 variables à la fois en Modbus TCP et en OPC UA :

### Cartographie OPC UA (Namespace URI: `http://EVA.com/sensor/simulator`) :
- **NodeID :** `ns=1;s=Boiler01.Temperature` (Type: `Float`, Unité: °C)
- **NodeID :** `ns=1;s=Boiler01.Pressure` (Type: `Float`, Unité: Bar)
- **NodeID :** `ns=1;s=Boiler01.Fault_Active` (Type: `Boolean`, 0 = Nominal, 1 = Alarme)

### Cartographie Modbus TCP (Holding Registers) :
- **Registre 40001 (adresse 0) :** Température (multipliée par 100 pour préserver 2 décimales. Ex: `7524` = 75.24 °C).
- **Registre 40002 (adresse 1) :** Pression (multipliée par 100. Ex: `152` = 1.52 Bar).
- **Registre 40003 (adresse 2) :** État de défaut (0 = OK, 1 = Alarme de dépassement).

---

## 2. Utilisation du Script d'Assistance (Lancement du Simulateur)

Pour démarrer les serveurs de simulation Modbus TCP et OPC UA en arrière-plan, utilisez l'outil d'exécution de code (`execute_code`) avec la commande suivante :

```python
import subprocess

cmd = [
    ".venv/Scripts/python.exe", 
    "skills/industrial/automation/industrial-sensor-simulator/scripts/sensor_simulator.py",
    "--opcua-port", "4840",  # Port standard OPC UA
    "--modbus-port", "5020", # Port 5020 (évite les droits d'administration requis pour le port 502)
    "--rate", "1.0"          # Mise à jour des calculs toutes les secondes
]

print("Démarrage du simulateur industriel...")
# Démarrer en arrière-plan
try:
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
except subprocess.TimeoutExpired:
    print("Le simulateur de capteurs fonctionne correctement en arrière-plan.")
```

---

## Pièges Courants (Common Pitfalls)

1. **Privilèges d'administration requis pour les ports inférieurs à 1024 :**
   * *Erreur :* Tenter de lancer le simulateur Modbus TCP sur le port standard `502` sous un utilisateur non-administrateur. Le script se ferme immédiatement avec une erreur de liaison de socket (`Permission Denied`).
   * *Correction :* Utiliser le port alternatif `5020` et configurer la redirection ou adapter les paramètres de connexion du client de test.

2. **Perte de corrélation temporelle en mode simulation accélérée :**
   * *Erreur :* Augmenter la fréquence de calcul de la simulation sans ajuster le temps d'échantillonnage de l'historien, ce qui génère des courbes déformées.
   * *Correction :* Coordonner le paramètre `--rate` du simulateur avec l'intervalle de collecte des ingesteurs de données.

---

## Liste de vérification (Checklist)

- [ ] La description frontmatter YAML fait moins de 60 caractères et se termine par un point.
- [ ] Les ports spécifiés (`4840` et `5020`) ne sont pas occupés par d'autres services locaux.
- [ ] Les variables entières Modbus TCP sont décodées et divisées par 100 côté client pour restituer la virgule flottante.
- [ ] Le simulateur tourne de manière asynchrone sans bloquer la boucle d'événements principale.
- [ ] La simulation intègre des comportements réalistes (oscillations, bruit) et des cas de test aux limites (fausses alarmes).

