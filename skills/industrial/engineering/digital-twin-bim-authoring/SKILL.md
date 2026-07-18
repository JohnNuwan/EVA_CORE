---
name: digital-twin-bim-authoring
description: "Créer et maintenir des jumeaux numériques industriels avec BIM, Unity et modélisation 3D."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - digital-twin
      - bim
      - unity-3d
      - ifc
      - revit
      - tekla-structures
      - point-cloud
      - scan-to-bim
      - unreal-engine
      - omniverse
      - industry-foundation-classes
      - usd
      - lidar
      - 3d-scan
      - navisworks
      - clash-detection
      - digital-thread
    related_skills:
      - digital-twins
      - virtual-commissioning
      - cad-bom-automation
      - industrial-flow-simulation
---

# Jumeau Numérique et BIM Industriel

## Vue d'ensemble

Le **jumeau numérique** (Digital Twin) est une réplique virtuelle d'un actif physique (usine, ligne, machine) connectée aux données temps réel pour la simulation, le monitoring et l'optimisation.

Cette compétence couvre : BIM (Building Information Modeling), modélisation 3D industrielle, scan 3D (LiDAR), jumeau numérique temps réel (Unity/Unreal), et standards IFC/USD.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De créer un jumeau numérique d'une ligne de production
- De modéliser une usine en BIM (Revit, Tekla)
- De connecter un modèle 3D aux données temps réel (OPC UA, MQTT)
- De faire un scan-to-BIM (LiDAR → modèle 3D)
- De développer une visualisation 3D interactive pour opérateurs

---

## 1. BIM Industriel (Building Information Modeling)

### 1.1 Standards IFC (Industry Foundation Classes)

IFC est le format ouvert d'échange BIM (ISO 16739). Structure clé :

| Concept IFC | Équivalent industriel |
|:------------|:---------------------|
| **IfcBuilding** | L'usine |
| **IfcBuildingStorey** | Niveau / étage |
| **IfcSpace** | Zone / hall / atelier |
| **IfcEquipmentElement** | Machine, équipement |
| **IfcFlowSegment** | Pipeline, goulotte, convoyeur |
| **IfcSensor** | Capteur |
| **IfcDistributionControlElement** | PLC, DCS, automate |

### 1.2 Workflow BIM Industriel

```
Scan LiDAR → Point Cloud → Registration → Classification → Modèle BIM → Jumeau Numérique
   (FARUS)    (CloudCompare)   (SCENE)     (Revit)        (Unity / Omniverse)
```

---

## 2. Jumeau Numérique Temps Réel

### 2.1 Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Données     │     │  Plateforme  │     │  Jumeau      │
│  Temps réel  │────▶│  Data Hub    │────▶│  3D          │
│              │     │              │     │              │
│ OPC UA       │     │ InfluxDB     │     │ Unity 3D     │
│ MQTT         │     │ Node-RED     │     │ Omniverse    │
│ Historien    │     │ Kafka        │     │ Unreal Engine│
└──────────────┘     └──────────────┘     └──────────────┘
```

### 2.2 Data Binding (Unity + MQTT)

```csharp
// Exemple : binding MQTT vers objet 3D dans Unity
void Start()
{
    mqttClient.Subscribe("factory/line1/motor101/speed");
}

void OnMessage(string topic, string payload)
{
    if (topic.EndsWith("/speed"))
    {
        float rpm = float.Parse(payload);
        motorObject.transform.rotation *= Quaternion.Euler(0, rpm * Time.deltaTime * 6, 0);
    }
}
```

---

## 3. Scan-to-BIM

1. **Acquisition** — Scanner laser (Leica BLK, FARUS Focus)
2. **Registration** — Alignement des scans (SCENE, Cyclone REGISTER)
3. **Classification** — Segmentation des éléments (CloudCompare, Revit)
4. **Modélisation** — Création d'actifs BIM à partir du nuage
5. **Validation** — Vérification dimensionnelle, gap analysis
6. **Export** — IFC, RVT, FBX, USD

---

## 4. Références

- [buildingSMART IFC](https://www.buildingsmart.org)
- [Autodesk Revit API](https://www.autodesk.com/revit)
- [Unity Industrial Collection](https://unity.com/solutions/industrial)
- [NVIDIA Omniverse](https://www.nvidia.com/omniverse)
- [ISO 19650 BIM](https://www.iso.org)
- [CloudCompare](https://www.cloudcompare.org)
