---
type: skill
title: OKF Manager
description: Gérer la conformité des compétences au format Google OKF.
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [windows, linux, macos]
tags: [okf, documentation, formatting, management, compliance]
---

# Gestion des Connaissances OKF (Open Knowledge Format)

## Vue d'ensemble
Cette compétence permet à l'agent d'auditer et de mettre en conformité les en-têtes de documentation du dépôt selon la norme Google OKF. Elle permet également d'exporter le savoir de l'agent sous forme de bundle portable (ZIP) et d'importer des répertoires de documentation externes.

## Instructions d'Utilisation
Toutes les opérations de gestion s'appuient sur le script d'assistance `skills/productivity/okf-manager/scripts/manage_okf.py`.

Comme le terminal démarre son exécution dans le dossier `output/`, vous devez exécuter ce script en le ciblant via le chemin relatif :
`../skills/productivity/okf-manager/scripts/manage_okf.py`.

### 1. Diagnostiquer la conformité OKF des compétences actives
Pour analyser la conformité des fichiers Markdown par rapport à la spécification Google OKF v0.1 :
```bash
python ../skills/productivity/okf-manager/scripts/manage_okf.py check
```

### 2. Convertir les compétences au format Google OKF
Pour mettre à jour automatiquement les en-têtes YAML des compétences détectées non conformes :
```bash
python ../skills/productivity/okf-manager/scripts/manage_okf.py convert --write
```

### 3. Exporter toutes les connaissances actives sous forme de Bundle OKF
Pour créer une archive ZIP standardisée contenant les fiches de connaissances :
```bash
python ../skills/productivity/okf-manager/scripts/manage_okf.py export "bundle_okf.zip"
```

### 4. Importer un wiki de documentation externe au format OKF
Pour ingérer un dossier de fiches Markdown structurées comme compétences temporaires :
```bash
python ../skills/productivity/okf-manager/scripts/manage_okf.py import "chemin/vers/dossier_okf"
```

### 5. Provenance Cryptographique & Gouvernance ACS (Agent Control Standard)
Lors de l'exportation d'un bundle ZIP, la commande `export` effectue des vérifications avancées de provenance et de gouvernance :
* **Détection des Enveloppes ACS** : Elle parcourt l'espace de travail pour localiser les enveloppes d'autorisation `acs_envelope.json` générées lors des délégations de tâches à des sous-agents.
* **Filiation d'Auteurs** : Elle détermine pour chaque fichier de connaissance s'il a été rédigé par un sous-agent collaborateur particulier en remontant l'arborescence jusqu'à une enveloppe ACS valide.
* **Génération du Lignage** : Elle produit un fichier `provenance_okf.json` au sein de l'archive ZIP, décrivant la liste des fichiers, leurs signatures SHA256 individuelles, l'ID de leur sous-agent rédacteur respectif (`written_by`) et l'arbre de délégation de filiation (`lineage`) contenant les signatures ACS d'autorisation.
* **Signature Globale de Provenance** : Le manifeste et le lignage de délégation sont sérialisés et signés avec une somme de contrôle SHA256 globale chiffrée à l'aide d'un sel cryptographique sécurisé pour en assurer l'intégrité infalsifiable.

