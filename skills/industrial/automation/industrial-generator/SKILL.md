---
name: industrial-generator
description: "Générer du code Siemens/Rockwell et SCADA pour automates."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows, linux, macos]
metadata:
  EVA:
    tags: [industrial, plc, scada, generation, siemens, rockwell, ignition, intouch, wincc, grafcet]
    related_skills: [siemens-scl, rockwell-studio5000, ignition-scada, plc-converter]
---

# Génération Industrielle Automate & SCADA

## Vue d'ensemble

Cette compétence permet à l'agent d'gérer et d'automatiser l'importation de listes d'organes (Excel ou JSON), de les valider/modifier en lot, de générer du code Siemens (SCL, AWL) ou Rockwell, de compiler des diagrammes Grafcet (Mermaid) en séquenceurs SCL, et de produire des fichiers de supervision (Ignition Perspective, InTouch, WinCC Unified).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De charger ou d'importer une liste d'équipements depuis un fichier Excel ou JSON.
- De générer des blocs fonctionnels automate pour des catégories d'organes (ex: MVAR, MTOR, VMONO, etc.).
- De générer des configurations SCADA (Ignition Perspective, InTouch CSV, WinCC Unified XML).
- De traduire ou compiler un diagramme de Grafcet écrit en Mermaid (flowcharts ou stateDiagrams) en code Siemens SCL.
- De faire des modifications sur un ensemble de moteurs, vannes ou autres organes.
- De générer des programmes spécifiques pour un nombre défini de moteurs/vannes.

---

## Instructions d'Utilisation

Toutes les opérations s'appuient sur le script d'assistance `generate_plc_scada.py`. Comme le répertoire de travail du terminal est configuré sur `./output`, vous devez exécuter ce script via l'outil `terminal` en le ciblant via le chemin relatif `../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py`.

### 1. Importer un fichier de configuration (Excel ou JSON)

Pour charger un fichier de configuration et l'enregistrer dans l'état local du générateur :
```bash
python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py import "chemin/vers/fichier"
```

### 2. Lister les équipements chargés

Pour voir le résumé des équipements en mémoire :
```bash
python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py list
```

### 3. Modifier des équipements

- **Mise à jour individuelle** :
  ```bash
  python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py update <catégorie> <mnémonique> --desc "Nouvelle desc" --props clé=valeur
  ```
- **Mise à jour en lot (batch)** :
  ```bash
  python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py update-batch <catégorie> --prefix <préfixe> --desc "Description pour {mnemo}" --props intensite=2.5
  ```

### 4. Générer du code automate (PLC)

Pour générer le fichier de code pour une catégorie (Siemens SCL/AWL) :
```bash
python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py generate-plc <catégorie> "chemin/de/sortie" [--automate-type Siemens_TIA/Siemens_STEP7]
```

### 5. Générer des configurations SCADA

Pour générer les fichiers de supervision :
- **Ignition Perspective** :
  ```bash
  python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py generate-scada ignition "chemin/de/sortie.json"
  ```
- **InTouch CSV** :
  ```bash
  python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py generate-scada intouch "chemin/de/sortie.csv"
  ```
- **WinCC Unified XML** :
  ```bash
  python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py generate-scada wincc "chemin/de/sortie.xml"
  ```

### 6. Convertir un diagramme Grafcet Mermaid en SCL

Pour compiler un Grafcet au format Mermaid (flowchart ou stateDiagram) en bloc fonctionnel SCL :
```bash
python ../skills/industrial/automation/industrial-generator/scripts/generate_plc_scada.py convert-grafcet "chemin/vers/grafcet_mermaid.txt" "chemin/de/sortie.scl"
```

---

## Intégration Rockwell

Pour convertir ou manipuler du code Rockwell, utilisez en complément l'outil `plc_converter` ou le script `../skills/industrial/automation/plc-converter/scripts/plc_converter_wrapper.py`.
