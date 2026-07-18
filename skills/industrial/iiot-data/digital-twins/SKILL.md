---
name: digital-twins
description: "Modéliser des jumeaux numériques et des AAS."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [digital-twin, aas, asset-administration-shell, websockets, fastapi, api, industrial-automation]
    related_skills: [industrial-uns, predictive-maintenance, industrial-edge, opc-ua-scanner]
---

# Jumeaux Numériques & Asset Administration Shell (AAS)

## Vue d'ensemble

Un **jumeau numérique (Digital Twin)** est la réplique virtuelle d'un actif physique (une machine, un moteur, un outil de production complet). Le jumeau numérique agrège toutes les données de l'actif (modèles 3D, documentation technique, historique des pannes, et flux de mesures en temps réel).

Dans l'Industrie 4.0, l'**Asset Administration Shell (AAS)** est le standard d'échange de données visant à donner une structure numérique unifiée à n'importe quel équipement industriel. La synchronisation dynamique se fait via des APIs REST et des **WebSockets** pour le flux continu.

Cette compétence guide l'agent Helios pour modéliser des jumeaux numériques et concevoir des services de synchronisation temps réel.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De modéliser la fiche technique ou le modèle de données numérique (AAS) d'un équipement.
- De concevoir une API REST (FastAPI) pour lire/écrire l'état d'un jumeau numérique.
- De développer un serveur ou un client WebSockets pour diffuser en temps réel les changements de capteurs d'un automate vers un modèle 3D / Dashboard IHM.

**Ne pas utiliser pour :**
- Réaliser la conception CAO 3D brute d'une pièce mécanique (SolidWorks, AutoCAD).

---

## 1. Structure Simplifiée d'un Asset Administration Shell (AAS) en Python

Un AAS se compose de sous-modèles (Submodels) décrivant des facettes de l'équipement (Identification, Paramètres techniques, Données temps réel).

```python
# Exemple de structure de données représentant un AAS de machine
class AssetAdministrationShell:
    def __init__(self, id_short: str, global_id: str):
        self.id_short = id_short
        self.global_id = global_id
        self.submodels = {}

    def add_submodel(self, submodel_id: str, submodel_data: dict):
        self.submodels[submodel_id] = submodel_data

# Création du jumeau numérique d'une Pompe Industrielle
pump_twin = AssetAdministrationShell(
    id_short="Pump_Line1", 
    global_id="urn:actemium:paris:assets:pump_line1"
)

# Sous-modèle de caractéristiques techniques (Statique)
pump_twin.add_submodel("TechnicalProperties", {
    "manufacturer": "Grundfos",
    "max_flow_rate": {
        "value": 150.0,
        "unit": "m3/h"
    },
    "max_pressure": {
        "value": 10.0,
        "unit": "bar"
    }
})

# Sous-modèle d'état opérationnel (Dynamique)
pump_twin.add_submodel("OperationalData", {
    "current_flow": 124.5,
    "temperature": 38.6,
    "vibration_level": "NORMAL"
})
```

---

## 2. API de Synchronisation en Temps Réel avec WebSockets (FastAPI)

Pour mettre à jour instantanément les représentations virtuelles 3D (ex: Unity, Unreal Engine ou dashboards web) sans surcharger le serveur de requêtes HTTP répétitives, les WebSockets sont privilégiés.

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

class ConnectionManager:
    """Gère les connexions WebSockets des clients du jumeau numérique (interfaces IHM/3D)."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Envoie la mise à jour à toutes les interfaces connectées."""
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/digital-twin")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Attente de messages éventuels des clients (ex: commandes de forçage)
            data = await websocket.receive_json()
            # Logique de traitement des commandes
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## Pièges Courants

1. **Désynchronisation de temps réel (Lag) :**
   * *Erreur :* Envoyer chaque mise à jour de tag (ex: 500 tags mis à jour à 10ms) directement via WebSockets sans filtrage. Cela sature le navigateur du client ou l'application 3D.
   * *Correction :* Envoyer uniquement des deltas de changements (Change-of-State) ou regrouper les variables dans un envoi groupé (Buffer) à intervalle régulier (ex: toutes les 200ms).

2. **Absence d'historique dans le Jumeau Numérique :**
   * *Erreur :* Concevoir un jumeau numérique qui ne dispose que de la valeur instantanée présente en RAM. Si le client veut analyser le comportement précédent, il doit faire des requêtes complexes à l'historiseur de données.
   * *Correction :* Associer le jumeau numérique à une passerelle vers la base de données temporelle (ex: InfluxDB) pour charger automatiquement le contexte historique récent.

---

## Liste de vérification (Checklist)

- [ ] Les connexions WebSockets gèrent proprement les déconnexions de clients (`WebSocketDisconnect`) pour éviter les fuites de mémoire.
- [ ] Les données envoyées par WebSockets sont optimisées (regroupement ou détection de changement) pour ne pas saturer l'affichage client.
- [ ] La structure AAS sépare nettement les données statiques (propriétés techniques) et dynamiques (valeurs de capteurs en temps réel).
- [ ] Les APIs REST du jumeau numérique fournissent des schémas de validation stricts (ex: modèles `Pydantic` dans FastAPI).

