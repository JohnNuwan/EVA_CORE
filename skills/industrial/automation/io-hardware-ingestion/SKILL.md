---
name: io-hardware-ingestion
description: "Ingérer des listes E/S pour générer des variables."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [industrial, automation, io-list, eplan, plc, hardware-architecture]
    related_skills: [rockwell-studio5000, siemens-scl]
---

# Ingestion de l'Architecture Matérielle et des Listes d'E/S

## Vue d'ensemble

L'ingestion de listes d'E/S (Input/Output lists) et de configurations matérielles (comme les exports de logiciels de CAO électrique type EPLAN) est une étape cruciale pour générer du code automate sans erreur. Cette compétence guide l'agent pour lire ces données d'entrée, structurer les liens matériels, et assigner correctement les adresses physiques aux variables logiques de l'automate (Control Modules).

Le script d'ingestion `io_ingester.py` permet d'automatiser cette tâche en lisant des fichiers CSV ou Excel et en exportant des déclarations de variables directement importables dans les IDE d'automatisation Siemens (SCL), Schneider (XMY) ou CODESYS/TwinCAT (PLCopen XML).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'analyser un fichier de câblage, une liste d'E/S issue d'un tableur Excel ou d'un export CSV d'EPLAN.
- De mapper des adresses physiques d'E/S automates à des structures logiques.
- De générer des déclarations de variables globales (GVL, DB, Taglists) basées sur la configuration matérielle réelle.

---

## 1. Exécution du Script d'Ingestion en Ligne de Commande

Le script `io_ingester.py` s'exécute à l'aide de l'outil système `terminal`.

### Génération de variables Siemens SCL
```bash
python skills/industrial/automation/io-hardware-ingestion/scripts/io_ingester.py <chemin_liste_io.csv> -o variables.scl -f scl
```

### Génération de variables Schneider XMY (Unity Pro / Control Expert)
```bash
python skills/industrial/automation/io-hardware-ingestion/scripts/io_ingester.py <chemin_liste_io.xlsx> -o variables.xmy -f xmy
```

### Génération de variables PLCopen XML (CODESYS, TwinCAT)
```bash
python skills/industrial/automation/io-hardware-ingestion/scripts/io_ingester.py <chemin_liste_io.csv> -o variables.xml -f plcopen
```

---

## 2. Structure et Détection des Données

Le script s'attend à un tableau contenant les colonnes clés suivantes (la détection des colonnes est insensible à la casse et gère les synonymes) :

1. **Tag/Mnémonique** (Synonymes : `tag`, `mnemonique`, `nom`, `name`, `symbole`, `identifier`) : Identifiant de l'instrument ou de l'actionneur (ex: `120_XV_01`).
2. **Adresse Physique** (Synonymes : `address`, `adresse`, `addr`, `physical`, `physique`, `loc`) : L'adresse câblée (ex: `%I1.0` ou `Local:1:I.Data[0]`).
3. **Type de Signal** (Synonymes : `type`, `signal`, `datatype`, `format`) : DI, DO, AI, AO ou types standard (BOOL, INT, etc.).
4. **Description/Fonction** (Synonymes : `desc`, `description`, `fonction`, `comment`, `commentaire`, `libelle`) : Rôle physique du signal.

---

## 3. Rapprochement et Mappage vers les Control Modules (CM)

Pour éviter les hallucinations de variables et assurer l'intégrité de la programmation, appliquez ces règles strictes lors du rapprochement :

### 3.1 Regroupement par Équipement Parent (Control Module)
Regroupez tous les signaux physiques individuels appartenant à un même composant logique (le Control Module parent) :
- **Vanne Tout-ou-Rien (VALVE)** : Doit réunir ses deux retours physiques (Feedback Open/Close) et sa commande physique.
- **Moteur (MOTOR)** : Doit réunir le retour de marche, le défaut disjoncteur (Trip), et la sortie commande de marche.

### 3.2 Table de Correspondance Matérielle / Logicielle

| Type de Signal | Usage Matériel | Variable Logique dans le CM (Standard EVA) |
| :--- | :--- | :--- |
| **DI** | Retour physique (contact sec) | `i_FB_Open`, `i_FB_Run`, `i_Trip`, `i_Local` |
| **DO** | Commande physique (bobine relais) | `q_Cmd_Open`, `q_Cmd_Run`, `q_Cmd_Speed` |
| **AI** | Mesure capteur (4-20mA, PT100) | `i_Raw_Value` (à convertir en unité physique via mise à l'échelle) |
| **AO** | Consigne actionneur (0-10V, 4-20mA)| `q_Raw_Output` (consigne convertie vers la carte analogique) |

---

## Liste de vérification (Checklist)

- [ ] Le script python `io_ingester.py` est appelé pour effectuer les conversions automatiquement.
- [ ] Toutes les adresses physiques utilisées existent réellement dans le fichier d'E/S source.
- [ ] Il n'y a aucun doublon d'adresses physiques affectées à des variables différentes.
- [ ] Les types de données automates correspondent aux types de signaux physiques (ex. `BOOL` pour DI/DO, `INT` ou `WORD` pour AI/AO).
- [ ] Les commentaires associés aux variables reprennent textuellement la description physique du schéma électrique.
- [ ] Les variables non câblées (réserves) sont identifiées et documentées comme telles dans le code automate.

