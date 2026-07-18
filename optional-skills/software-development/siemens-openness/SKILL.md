---
name: siemens-openness
description: "Automatiser TIA Portal avec Openness via C# et Python."
version: 1.0.0
author: EVA
license: MIT
platforms: [windows]
metadata:
  tags: [siemens, openness, tia-portal, plc, pythonnet, dotnet, csharp]
  related_skills: [siemens-scl, plc-connectivity]
---

# Automatisation TIA Portal avec Siemens Openness

## Vue d'ensemble

**TIA Portal Openness** est l'interface de programmation d'application (API) fournie par Siemens pour automatiser les tâches d'ingénierie dans l'environnement TIA Portal. Elle permet de créer ou de modifier des projets, de générer du matériel, d'importer/exporter des blocs de code SCL/LAD/FBD au format XML, et de générer automatiquement des tables de variables API.

Cette compétence guide l'agent EVA pour écrire des scripts d'automatisation en Python exploitant Openness à l'aide de la bibliothèque `pythonnet` (qui permet d'appeler les DLLs .NET de Siemens directement en Python).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Générer automatiquement des projets TIA Portal à partir d'une liste de matériel ou d'entrées/sorties (I/O).
- Exporter les blocs de programme (FB, FC, DB, OB) sous forme de fichiers XML pour en faire un audit ou du versionnage (Git).
- Importer des blocs SCL générés dynamiquement dans un automate Siemens dans TIA Portal.
- Générer, modifier ou importer en masse des tables de variables API (PLC Tags) et des types de données utilisateur (UDT).
- Automatiser les étapes de compilation ou de génération d'un projet Siemens dans une chaîne de CI/CD.

---

## 1. Initialisation de la Connexion via Pythonnet

L'accès à l'API Openness nécessite de charger la bibliothèque d'ingénierie Siemens (`Siemens.Engineering.dll`) installée avec TIA Portal.

> [!IMPORTANT]
> Pour éviter les blocages de threads liés au modèle d'appartement COM de Windows (Single Threaded Apartment - STA), il est indispensable de configurer `sys.coinit_flags = 2` avant d'importer le module `clr`.

```python
import sys
# Configurer COM en mode Multi-Threaded Apartment (MTA)
sys.coinit_flags = 2  

import clr
import os

# 1. Chemin d'accès vers les DLLs Openness (à adapter selon la version installée)
dll_path = r"C:\Program Files\Siemens\Automation\Portal V17\PublicAPI\V17\Siemens.Engineering.dll"

if os.path.exists(dll_path):
    clr.AddReference(dll_path)
    # Import des namespaces Siemens
    import Siemens.Engineering as engineering
    from Siemens.Engineering import TiaPortal, TiaPortalMode
else:
    raise FileNotFoundError("DLL Siemens Openness introuvable. TIA Portal doit être installé.")

# 2. Démarrage de TIA Portal (ou connexion à une instance en cours)
# Mode.WithUserInterface affiche l'application graphique. Mode.WithoutUserInterface s'exécute en arrière-plan.
mode = TiaPortalMode.WithUserInterface
mytia = TiaPortal(mode)

# Optionnel : S'attacher à une instance existante
# mytia = engineering.TiaPortal.GetProcesses()[0].Attach()
```

---

## 2. Navigation dans la Structure du Projet

L'arborescence de TIA Portal est strictement hiérarchisée. Le script doit naviguer à travers les objets pour cibler la CPU de l'automate :

```python
# 1. Ouverture d'un projet existant
project_path = r"C:\Automation\Projets\Usine_Assembly\Usine_Assembly.ap17"
project = mytia.Projects.Open(engineering.FileInfo(project_path))

# 2. Recherche du contrôleur (Device) dans le projet
plc_device = None
for device in project.Devices:
    if "PLC" in device.Name:
        plc_device = device
        break

# 3. Accès au conteneur de logiciels (PlcSoftware) pour la CPU cible
# Il faut chercher l'élément PlcSoftware dans le DeviceItem matériel de la CPU
plc_software = None
for item in plc_device.DeviceItems:
    # TIA Portal structure la CPU comme un sous-item matériel du Device
    software_container = item.GetService[engineering.SoftwareContainer]()
    if software_container is not None:
        plc_software = software_container.Software
        break

if plc_software is not None:
    print(f"Connexion réussie à la CPU : {plc_software.Name}")
```

---

## 3. Import et Export de Blocs en XML

Openness permet d'exporter et d'importer des blocs au format XML (conforme au schéma XML Siemens). C'est la méthode privilégiée pour injecter ou analyser du code.

### Recette d'exportation d'un bloc de code (ex : FB1) :
```python
# Cible le bloc dans le dossier des blocs du programme
block_group = plc_software.BlockGroup
target_block = block_group.Blocks.Find("FB_Moteur")

if target_block is not None:
    export_file = r"C:\Automation\Exports\FB_Moteur.xml"
    # Option.WithDefaults inclut toutes les valeurs par défaut
    option = engineering.ExportOptions.WithDefaults
    target_block.Export(engineering.FileInfo(export_file), option)
    print("Bloc exporté avec succès.")
```

### Recette d'importation d'un bloc généré :
```python
xml_import_file = r"C:\Automation\Imports\FB_NouveauMoteur.xml"
# Règle de collision : écraser le bloc s'il existe déjà
collision_option = engineering.ImportOptions.Override

plc_software.BlockGroup.Blocks.Import(
    engineering.FileInfo(xml_import_file),
    collision_option
)
print("Nouveau bloc XML importé dans TIA Portal.")
```

---

## Pièges Courants (Common Pitfalls)

1. **Erreur d'accès refusé (Security Exception) :**
   * *Erreur :* Le script lève une exception de sécurité lors du démarrage de TIA Portal.
   * *Correction :* L'utilisateur exécutant le script doit obligatoirement faire partie du groupe Windows local `"Siemens TIA Openness"`. Il est également recommandé d'exécuter le script dans un terminal lancé en mode Administrateur.

2. **Verrouillage de thread par TIA Portal :**
   * *Erreur :* Le script Python se bloque indéfiniment lors d'appels de méthodes lourdes (ex: compilation de projet).
   * *Correction :* TIA Portal s'exécute sur un thread d'appartement unique (STA). Il faut impérativement s'assurer que `sys.coinit_flags = 2` est positionné avant tout import de `clr` pour forcer Python à s'exécuter en mode MTA (Multi-Threaded Apartment), permettant aux threads de communiquer de manière asynchrone sans blocage.

3. **Incompatibilité de Schéma XML selon la version de TIA Portal :**
   * *Erreur :* L'importation d'un XML échoue avec une erreur de validation de schéma.
   * *Correction :* Le format XML change d'une version de TIA Portal à l'autre. Il faut vérifier la balise racine `<Document>` et ses attributs de version dans le fichier XML généré pour s'assurer qu'elle correspond à la version exacte de la DLL PublicAPI chargée par le script.

---

## Liste de Vérification (Checklist)

- [ ] L'utilisateur actuel appartient au groupe d'utilisateurs Windows local `Siemens TIA Openness`.
- [ ] Le script configure bien `sys.coinit_flags = 2` avant d'importer `clr` pour éviter les blocages de thread.
- [ ] Les chemins de fichiers passés à l'API Siemens sont encapsulés dans des objets `.NET` `engineering.FileInfo` (et non de simples chaînes de caractères Python).
- [ ] Les options de collision (ex: `ImportOptions.Override`) sont explicitement définies pour éviter les blocages en mode interactif lors des imports de blocs.
- [ ] Toutes les instances de TIA Portal ouvertes par le script sont correctement fermées en fin de traitement (`mytia.Dispose()`).
