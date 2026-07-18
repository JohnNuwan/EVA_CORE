---
name: project-output-organization
description: "Organiser la sortie des projets, scripts et fichiers dans une arborescence standardisée pour une gestion professionnelle et maintenable."
version: 1.1.0
author: EVA Agent
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [organization, output, files, projects, directory-structure, best-practices, clean-code]
    related_skills: [plan, simplify-code, python-pep8]
---

# Organisation des Sorties de Projet

## Vue d'ensemble

Cette compétence définit les **conventions d'organisation des fichiers de sortie** pour tous les projets, scripts et workflows générés. Une structure standardisée garantit la maintenabilité, la reproductibilité et la lisibilité des livrables, que ce soit pour des scripts Python, des rapports, des assets ou des templates.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'exécuter un script ou un projet qui produit des fichiers de sortie.
- De générer un rapport, des assets ou des templates organisés.
- De standardiser la structure des sorties d'un projet existant.
- De créer un nouveau projet ou workflow nécessitant une arborescence claire.

---

## 1. Structure de Répertoire Standard

### 1.1 Arborescence Racine

Toute sortie de projet doit être placée sous un répertoire `output/` à la racine du projet, organisé par catégorie :

```
output/
├── scripts_python/        # Scripts Python générés
│   ├── data_processing/
│   ├── api_clients/
│   └── utils/
├── scripts_typescript/     # Scripts TypeScript / JavaScript
├── scripts_rust/           # Scripts Rust
├── scripts_cpp/            # Scripts C++
├── scripts_csharp/         # Scripts C#
├── scripts_go/             # Scripts Go
├── reports/                # Rapports (PDF, HTML, MD)
│   ├── analyses/
│   └── syntheses/
├── assets/                 # Fichiers statiques
│   ├── images/             # PNG, JPG, SVG
│   ├── diagrams/           # Drawio, Excalidraw, Mermaid
│   └── fonts/              # Polices
├── templates/              # Templates de code ou de configuration
│   ├── configs/            # YAML, JSON, TOML
│   └── boilerplates/       # Squelettes de projet
├── data/                   # Données de sortie
│   ├── csv/
│   ├── json/
│   └── parquet/
└── docs/                   # Documentation générée
    ├── api/
    └── guides/
```

### 1.2 Convention de Nommage des Fichiers

| Type | Convention | Exemple |
|:---|:---|:---|
| **Scripts** | `snake_case` descriptif | `geolocation_phone.py` |
| **Rapports** | `kebab-case` avec date | `audit-securite-2026-06.md` |
| **Assets** | `snake_case` court | `logo_EVA.png` |
| **Templates** | `snake_case` avec suffixe `.template` | `config.template.yaml` |
| **Données** | `snake_case` avec date si temporel | `sensor_data_2026-06.csv` |

---

## 2. Règles d'Organisation

### 2.1 Principes Généraux

1. **Un répertoire = un langage ou un type** : Ne mélangez pas Python et Rust dans le même dossier.
2. **Un fichier = une responsabilité** : Chaque fichier de sortie doit avoir un rôle unique et clairement identifiable.
3. **Nom descriptif** : Le nom du fichier doit suffire à comprendre son contenu sans l'ouvrir.
4. **Versionnement** : Utilisez des sous-dossiers par version si plusieurs itérations coexistent.

### 2.2 Exemples Concrets

```python
# Exemple : script qui génère plusieurs types de sorties
import os

# Organisation des sorties
output_root = "output/scripts_python"
os.makedirs(f"{output_root}/data_processing", exist_ok=True)
os.makedirs(f"{output_root}/api_clients", exist_ok=True)
os.makedirs("output/data/csv", exist_ok=True)

# Sauvegarde du script
script_path = f"{output_root}/data_processing/clean_sensor_data.py"

# Sauvegarde des données générées
data_path = "output/data/csv/cleaned_sensors_2026-06.csv"

print(f"Script : {script_path}")
print(f"Données : {data_path}")
```

### 2.3 Anti-patrons à Éviter

```
❌ MAUVAISE ORGANISATION :

output/
├── script1.py
├── script2.rs
├── data.csv
├── logo.png
├── quelque_chose.js
└── template.yaml

✅ BONNE ORGANISATION :

output/
├── scripts_python/
│   └── script1.py
├── scripts_rust/
│   └── script2.rs
├── data/
│   └── csv/
│       └── data.csv
├── assets/
│   └── images/
│       └── logo.png
├── templates/
│   └── config.template.yaml
└── scripts_typescript/
    └── quelque_chose.js
```

---

## 3. Processus de Génération

### 3.1 Workflow Type

1. **Création de l'arborescence** : Avant toute génération de sortie, créez les répertoires nécessaires avec `os.makedirs()` ou `mkdir -p`.
2. **Placement des fichiers** : Déposez chaque fichier dans le sous-répertoire correspondant à son type.
3. **Validation** : Vérifiez que tous les fichiers sont dans `output/` et dans le bon sous-dossier.
4. **Nettoyage** : Supprimez les fichiers temporaires ou intermédiaires qui ne font pas partie du livrable final.

### 3.2 Script d'Organisation Automatique

```python
import os
import shutil
from pathlib import Path

EXTENSION_MAP = {
    '.py': 'scripts_python',
    '.ts': 'scripts_typescript',
    '.js': 'scripts_typescript',
    '.rs': 'scripts_rust',
    '.cpp': 'scripts_cpp',
    '.cs': 'scripts_csharp',
    '.go': 'scripts_go',
    '.png': 'assets/images',
    '.jpg': 'assets/images',
    '.svg': 'assets/images',
    '.drawio': 'assets/diagrams',
    '.excalidraw': 'assets/diagrams',
    '.pdf': 'reports',
    '.html': 'reports',
    '.csv': 'data/csv',
    '.json': 'data/json',
    '.yaml': 'templates/configs',
    '.toml': 'templates/configs',
}

def organize_output(source_dir: str, output_root: str = "output"):
    """Organise les fichiers générés dans l'arborescence standard.

    Args:
        source_dir: Répertoire source contenant les fichiers à organiser.
        output_root: Répertoire racine de sortie (défaut: output/).
    """
    for file_path in Path(source_dir).glob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            subdir = EXTENSION_MAP.get(ext, "other")
            target = Path(output_root) / subdir / file_path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(target))
            print(f"Déplacé : {file_path.name} → {target}")
```

---

## Liste de vérification

- [ ] Le répertoire `output/` existe à la racine du projet.
- [ ] Chaque fichier de sortie est placé dans le sous-répertoire correspondant à son type.
- [ ] Les noms de fichiers sont descriptifs et suivent la convention de nommage.
- [ ] Il n'y a pas de fichiers orphelins directement dans `output/` (tous sont dans un sous-dossier).
- [ ] Les fichiers temporaires ou intermédiaires sont nettoyés.
- [ ] L'arborescence est cohérente avec les conventions de l'équipe ou du projet.
