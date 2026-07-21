---
name: python-modules
description: Modules, packages, environnements virtuels, gestion de dépendances, et structure de projet Python. En français, couvre uv, pip, pyproject.toml, et bonnes pratiques.
---

# Modules, Packages et Projets Python — Guide Complet (Français)

Ce skill couvre l'organisation du code Python : modules, packages, imports, environnements virtuels, dépendances et structure de projet.

---

## 1. Modules

Un module est simplement un fichier `.py`. Son nom est le nom du fichier sans l'extension.

### Créer un module

```python
# mon_module.py
"""Module d'utilitaires mathématiques.

Ce module fournit des fonctions de calcul courantes.

Example:
    >>> from mon_module import additionner
    >>> additionner(2, 3)
    5
"""

__version__ = "1.0.0"
__all__ = ["additionner", "multiplier"]  # Exporte seulement ces noms


def additionner(a: float, b: float) -> float:
    """Additionne deux nombres."""
    return a + b


def multiplier(a: float, b: float) -> float:
    """Multiplie deux nombres."""
    return a * b


def _fonction_privee() -> str:
    """Fonction interne, pas exportée."""
    return "privé"


# Code exécuté seulement si le module est lancé directement
if __name__ == "__main__":
    print("Module exécuté directement")
    print(additionner(1, 2))
```

### Imports

```python
# Import du module entier
import mon_module
mon_module.additionner(1, 2)

# Import avec alias
import mon_module as mm
mm.additionner(1, 2)

# Import de fonctions spécifiques
from mon_module import additionner, multiplier
additionner(1, 2)

# Import de tout (déconseillé)
from mon_module import *  # Respecte __all__

# Import avec alias de fonction
from mon_module import additionner as add

# Import relatif (dans un package)
from . import module_voisin
from .module_voisin import fonction
from .. import module_parent
from ..sous_package import module
```

### Chemins d'import

```python
import sys
from pathlib import Path

# Voir où Python cherche les modules
print(sys.path)

# Ajouter un chemin de recherche
sys.path.insert(0, str(Path.cwd() / "lib"))

# PYTHONPATH (variable d'environnement)
# export PYTHONPATH=/chemin/vers/modules:$PYTHONPATH
```

---

## 2. Packages

Un package est un dossier contenant `__init__.py` et des modules.

### Structure d'un package

```
mon_package/
├── __init__.py          # Initialise le package
├── module_a.py
├── module_b.py
├── sous_package/
│   ├── __init__.py
│   └── module_c.py
└── _interne/
    └── utils.py
```

### __init__.py

```python
# mon_package/__init__.py
"""Package de traitement de données.

Ce package fournit des outils pour charger, transformer
et analyser des données tabulaires.
"""

__version__ = "2.1.0"

# Contrôler ce qui est importé avec 'from package import *'
__all__ = ["Charger", "Transformer", "Analyser"]

# Réexporter les classes principales pour une API simplifiée
from .chargeur import Charger
from .transformateur import Transformer
from .analyseur import Analyser

# Initialisation paresseuse (optionnel)
def __getattr__(name: str):
    """Import paresseux des sous-modules lourds."""
    if name == "visualisation":
        from . import visualisation
        return visualisation
    raise AttributeError(f"module {name!r} non trouvé")
```

---

## 3. Imports Relatifs

```python
# mon_package/module_b.py
"""Module B avec imports relatifs."""

# Depuis le même package
from .module_a import ClasseA

# Depuis un sous-package
from .sous_package.module_c import fonction_c

# Depuis le package parent (si module_b était dans un sous-package)
from ..module_a import autre_fonction

# Depuis un package "oncle"
from ..autre_sous_package.module_d import ClasseD
```

---

## 4. Environnements Virtuels

### Avec uv (recommandé, rapide)

```bash
# Installation de uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Créer un projet
uv init mon-projet
cd mon-projet

# Créer un venv et installer des dépendances
uv venv
source .venv/bin/activate  # Linux/Mac
uv pip install requests pandas

# Ajouter des dépendances au projet
uv add requests pandas
uv add --dev pytest pytest-cov  # Dépendances de développement
```

### Avec venv (standard)

```bash
# Créer
python -m venv .venv

# Activer (Linux/Mac)
source .venv/bin/activate

# Activer (Windows)
.venv\Scripts\activate

# Désactiver
deactivate
```

---

## 5. pyproject.toml — Configuration Moderne

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "mon-projet"
version = "1.0.0"
description = "Description concise du projet"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.11"
authors = [
    { name = "Nom Auteur", email = "email@exemple.com" },
]
keywords = ["data", "analysis", "python"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "requests>=2.31",
    "pandas>=2.1",
    "pydantic>=2.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "pytest-mock>=3.12",
    "ruff>=0.4",
    "mypy>=1.9",
]
docs = [
    "sphinx>=7.2",
    "myst-parser>=3.0",
]
all = [
    "mon-projet[dev,docs]",
]

[project.scripts]
mon-cli = "mon_projet.cli:main"

[project.urls]
Homepage = "https://github.com/user/mon-projet"
Documentation = "https://mon-projet.readthedocs.io"
Repository = "https://github.com/user/mon-projet.git"

[tool.ruff]
line-length = 79
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
strict = true
python_version = "3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = ["-v", "--strict-markers", "--tb=short"]
```

---

## 6. Structure de Projet Recommandée

```
mon_projet/
├── src/
│   └── mon_projet/         # Code source principal
│       ├── __init__.py
│       ├── __main__.py     # Point d'entrée : python -m mon_projet
│       ├── cli.py          # Interface en ligne de commande
│       ├── config.py       # Configuration
│       ├── core/           # Logique métier
│       │   ├── __init__.py
│       │   ├── models.py
│       │   └── services.py
│       ├── api/            # API REST / routes
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── db/             # Accès aux données
│       │   ├── __init__.py
│       │   └── repository.py
│       └── utils/          # Utilitaires
│           ├── __init__.py
│           └── helpers.py
├── tests/                  # Tests unitaires et intégration
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_services.py
│   └── integration/
│       └── test_api.py
├── docs/                   # Documentation
│   ├── index.md
│   └── api.md
├── scripts/                # Scripts utilitaires
│   └── deploy.sh
├── .github/                # CI/CD
│   └── workflows/
│       └── tests.yml
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
└── .env.example
```

### .gitignore Python

```gitignore
# Bytecode
__pycache__/
*.py[cod]
*$py.class

# Environnement virtuel
.venv/
venv/
env/

# Distribution
dist/
build/
*.egg-info/

# Tests et couverture
.pytest_cache/
.coverage
htmlcov/
.coverage.*

# IDE
.vscode/
.idea/

# Variables d'environnement
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# uv
uv.lock
```

---

## 7. Gestion des Dépendances

### Avec uv (moderne)

```bash
uv add requests               # Ajouter une dépendance
uv add --dev pytest           # Dépendance de dev
uv remove requests            # Supprimer
uv lock                       # Mettre à jour le lockfile
uv sync                       # Installer depuis le lockfile
uv tree                       # Arbre des dépendances
```

### Avec pip (classique)

```bash
pip install package
pip install package==1.2.3
pip install "package>=1.0,<2.0"
pip install -r requirements.txt
pip freeze > requirements.txt
pip uninstall package
```

### requirements.txt vs pyproject.toml

```txt
# requirements.txt (simple, pas de metadata projet)
requests>=2.31.0
pandas>=2.1.0,<3.0

# requirements-dev.txt
-r requirements.txt
pytest>=8.0
ruff>=0.4
```

---

## 8. Entry Points et Scripts

```python
# src/mon_projet/cli.py
"""Interface en ligne de commande du projet."""

import argparse
import sys
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Point d'entrée principal.
    
    Args:
        argv: Arguments de la ligne de commande.
    
    Returns:
        Code de sortie (0 = succès).
    """
    parser = argparse.ArgumentParser(
        description="Mon outil CLI",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mode verbeux",
    )
    args = parser.parse_args(argv)
    
    print("Hello!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Dans `pyproject.toml` :
```toml
[project.scripts]
mon-cli = "mon_projet.cli:main"
```

---

## 9. Namespace Packages (Packages Distribués)

Permet de diviser un package sur plusieurs distributions :

```
# Paquet A
organisation_package/
└── module_a/
    └── __init__.py   # (sans __init__.py = namespace package implicite)

# Paquet B
organisation_package/
└── module_b/
    └── __init__.py

# Usage
from organisation_package.module_a import ClasseA
from organisation_package.module_b import ClasseB
```

---

## 10. Bonnes Pratiques

1. **Un package = un dossier avec `__init__.py`** (même vide)
2. **Nommer les modules en snake_case** : `mon_module.py`
3. **Éviter les imports circulaires** — extraire dans un module partagé
4. **`__all__`** pour contrôler l'export `from package import *`
5. **Utiliser `__main__.py`** pour `python -m mon_package`
6. **Imports absolus** pour le code externe, **relatifs** pour l'interne
7. **Jamais `sys.path` hack** dans du code de production — utiliser un install editable
8. **Versionner le lockfile** pour la reproductibilité (sauf `uv.lock` pour les bibliothèques)
9. **Séparer src/ du reste** (layout `src/`) — évite les imports accidentels
10. **`if __name__ == "__main__"`** protège le code d'exécution à l'import

---

## Références
- Modules Python : https://docs.python.org/3/tutorial/modules.html
- Packaging Python : https://packaging.python.org/tutorials/packaging-projects/
- uv : https://docs.astral.sh/uv/
- PEP 621 (pyproject.toml) : https://peps.python.org/pep-0621/