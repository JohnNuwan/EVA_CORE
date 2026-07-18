---
name: industrial-audit
description: "Faire un audit de spécifications EPH à partir de PDF."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [industrial, audit, siemens, eph, em, pdf, layout-preservation]
    related_skills: [virtual-commissioning, isa95-modelling, plc-connectivity]
---

# Audit Industriel des Spécifications EPH et EPH-EM

## Vue d'ensemble

L'objectif de cette compétence est d'analyser les cahiers des charges d'automatisme et spécifications techniques au format PDF pour en extraire de manière structurée les corrélations de communication de type **EPH (Equipment Phase)** et **EM (Equipment Module)**.

Dans les projets d'automatisme d'envergure, ces informations permettent de cartographier les liaisons inter-automates (liaisons physiques *eph to/from eph*) et de lier les phases logiques aux modules physiques de vannes, moteurs et capteurs.

Cette compétence s'appuie sur le script [audit_pdf.py](scripts/audit_pdf.py) pour :
1. Extraire les métadonnées (nom de fichier standard, titre de document d'équipement). Note : les sessions longue durée exigent une augmentation significative des délais de timeout pour éviter les interruptions répétées lors du traitement en lots. Par exemple, utiliser un délai de 900 secondes ou plus lorsque le script gère des lots de 50 fichiers.
2. Parcourir la **Section 1.5 (EQUIPMENT)** pour relever les liaisons EPH-EM.
3. Parcourir la **Section 2.5 (EXTERNAL EXCHANGES)** pour relever les liaisons EPH-EPH.
4. Associer chaque instance à son automate cible (AS) via des heuristiques de préfixes.
5. Générer un rapport consolidé en Markdown.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Lancer un audit de cohérence documentaire sur les phases logiques (EPH) d'un projet d'automatisme.
- Extraire les liaisons physiques inter-phases ou les tags d'instances d'équipement depuis des spécifications stockées dans [client_data/EPH/](../../../../../client_data/EPH).
- Reconstruire la cartographie d'échange de données entre les stations d'automatisme (AS).

---

## Règles d'Extraction et de Résolution Heuristique (AS)

L'agent doit veiller à respecter scrupuleusement les règles métiers suivantes lors de la validation des données d'entrée ou de la ré-exécution du script :

### 1. Structure de la Section 1.5 (EPH-EM)
- **Source** : L'instance source est le titre exact du document (ex. : `705C3_EPH_AgitCtrl`).
- **Cible (Instance Tag)** : Le tag de l'équipement (ex. : `664C6_E_B_INLET`). Le tag doit être extrait **littéralement**, sans aucun reformatage.
- **Filtres de Matrice** :
  - Extraire l'entrée uniquement si une colonne "Index Matrix" ou "EMT" contient une affectation valide (souvent signalée par un astérisque `*` ou un marquage de cellule `(*)`).
  - Si le fichier contient `IDS666`, appliquer la règle stricte : extraire uniquement les lignes où la colonne `EMT` contient un astérisque et le `Instance Tag` est valide.

### 2. Structure de la Section 2.5 (EPH-EPH)
- **Focus** : Extraire uniquement les liaisons de type `eph to / from eph`.
- **Résolution des notes** : Si le tableau spécifie "See note below" ou "See note 1", l'LLM doit impérativement lire le paragraphe de texte qui suit immédiatement le tableau pour y trouver le nom d'instance EPH réel (ex. : `610C5_P_PCIP_BTL_2`).
- **Cas bidirectionnel** : Si un lien bidirectionnel est mentionné entre Instance A et Instance B, générer deux entrées distinctes pour documenter le flux aller et retour.

### 3. Résolution des Stations d'Automatisme (AS - Automation Station)
L'affectation d'une instance à son automate physique est résolue de manière heuristique en fonction du préfixe numérique du nom de l'instance :
- Si l'instance commence par un nombre (ex. : `660C1_...`), elle appartient à la station **AS660** (format: `AS` + nombre).
- Si l'instance commence par un préfixe textuel (ex. : `CIP22_...`), elle appartient à la station **AS_CIP** (format: `AS_` + préfixe).
- En cas d'échec de résolution, la station par défaut est **AS_Unknown**.

---

## Utilisation et Commandes

**INSTRUCTION CRITIQUE POUR L'AGENT HELIOS :**
INSTRUCTION CRITIQUE POUR L'AGENT HELIOS :\n- Lorsque l'environnement `.venv` est valide, privilégier l'exécution directe sous Git Bash ou une autre interface de terminal compatible Windows.\n- Si la commande inclut un timeout supérieur à 600 secondes, utilisez impérativement un processus en tâche de fond avec `background=true` et `notify_on_complete=true`.\n- Normalisez tous les chemins de fichier en utilisant `os.path.normpath()` avant leur usage et vérifiez qu'ils ne contiennent pas d'espaces non échappés dans les motifs ou arguments.\n- Ajoutez des validations préalables pour s'assurer de l'existence des fichiers nécessaires (`audit_pdf.py`, dossier source PDF) avant exécution.
- N'écrivez jamais votre propre script d'audit et n'utilisez pas d'outil de modification système pour désactiver les scripts existants. Utilisez toujours le script batch [audit.bat](scripts/audit.bat) qui pilote l'ensemble. 

Pour exécuter le script de manière sécurisée et asynchrone dans votre processus, utilisez l'appel Python suivant :

```python
import subprocess
import os

# Le script batch gère les relances automatiques et les timeouts
print("Lancement de l'audit automatique...")
result = subprocess.run(["cmd.exe", "/c", "skills\\industrial\\automation\\industrial-audit\\scripts\\audit.bat"], capture_output=True, text=True, timeout=600)
print("Standard Output :")
print(result.stdout)

if result.stderr:
    print("Standard Error :")
    print(result.stderr)
```

### Paramètres Avancés en Ligne de Commande
Si vous devez lancer l'audit sur un sous-ensemble ou pour du débogage rapide, vous pouvez appeler directement le script Python sous-jacent :
```bash
# Limiter le traitement aux 5 premiers PDF pour vérification rapide
.venv\Scripts\python.exe skills\industrial\automation\industrial-audit\scripts\audit_pdf.py --limit 5

# Filtrer par motif de fichier (ex : uniquement les spécifications du Skid 625)
.venv\Scripts\python.exe skills\industrial\automation\industrial-audit\scripts\audit_pdf.py --pattern "*_IDS625_*.pdf"

# Activer le mode verbeux pour inspecter les appels API LLM
.venv\Scripts\python.exe skills\industrial\automation\industrial-audit\scripts\audit_pdf.py --verbose
```

---

## Gestion des Erreurs et Anti-Fragilité

- **Gestion des Timeouts (Checkpointing)** :
  Le script enregistre sa progression au fil de l'eau dans un fichier de checkpoint JSONL (portant le nom `{rapport}_checkpoint.jsonl`). En cas d'interruption du processus, le fait de relancer le script (ou le batch `skills/industrial/automation/industrial-audit/scripts/audit.bat`) reprendra exactement là où il s'est arrêté en ignorant les fichiers déjà traités.
- **Réparation de JSON LLM** :
  Si l'LLM renvoie un format JSON légèrement mal formé (virgule traînante, délimiteurs de bloc de code ` ```json ` restants), le script applique un processus de nettoyage et de réparation automatique (`_clean_and_repair_json`) pour éviter de rejeter la réponse.

---

## Liste de vérification (Checklist)

- [ ] Tous les PDF à analyser sont déposés dans le dossier [client_data/EPH/](../../../../../client_data/EPH).
- [ ] L'environnement virtuel `.venv` est activé et contient `pypdf` et `pdfplumber`.
- [ ] Le script batch `skills/industrial/automation/industrial-audit/scripts/audit.bat` s'exécute à la racine du projet et le fichier de checkpoint se met à jour.
- [ ] Le rapport final est généré dans `output/audit/{Timestamp}/audit_report.md` et présente des tableaux d'échanges triés et complets.
- [ ] Toutes les cibles d'instances cibles (Section 1.5 & 2.5) ont été correctement résolues en termes d'AS.

