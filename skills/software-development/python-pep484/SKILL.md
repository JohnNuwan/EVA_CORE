---
name: python-pep484
description: "Appliquer le typage statique selon la PEP 484 en Python."
version: 1.0.0
author: EVA Agent (adapté de obra/superpowers)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [python, pep484, typing, mypy, static-analysis]
    related_skills: [python-pep8, python-pep257, python-pep20, simplify-code]
---

# Typage Statique en Python (PEP 484, PEP 585 & PEP 604)

## Vue d'ensemble

Cette compétence détaille l'utilisation des annotations de type (Type Hints) introduites par la **PEP 484**, complétées par les syntaxes modernes de la **PEP 585** (génériques intégrés dans les collections standards) et de la **PEP 604** (opérateur d'union de type `|`). L'usage du typage statique améliore la robustesse du code, évite de nombreuses erreurs d'exécution et optimise l'autocomplétion dans les éditeurs de code.

---

## 1. Syntaxe de base

### 1.1 Variables et Fonctions
*   **Variables :** Indiquez le type après deux-points `:` :
    ```python
    retry_count: int = 3
    timeout_seconds: float = 30.5
    agent_name: str = "EVA"
    ```
*   **Fonctions :** Indiquez le type des arguments après deux-points, et le type de retour après la flèche `->` :
    ```python
    def get_greeting(name: str) -> str:
        return f"Bonjour {name}"
    ```

---

## 2. Types Complexes et Syntaxe Moderne

### 2.1 Collections Génériques (PEP 585)
*   Depuis Python 3.9+, utilisez directement les classes intégrées en minuscules (ex: `list`, `dict`, `set`, `tuple`) au lieu d'importer `List`, `Dict`, `Set` depuis le module `typing` :
    ```python
    # Recommandé (Python 3.9+)
    users: list[str] = ["Alice", "Bob"]
    configurations: dict[str, int] = {"port": 8080, "timeout": 30}
    coordinates: tuple[float, float] = (48.8566, 2.3522)
    ```

### 2.2 Unions de Types et Optional (PEP 604)
*   Depuis Python 3.10+, remplacez `Union` et `Optional` du module `typing` par le caractère pipe `|` :
    ```python
    # Recommandé (Python 3.10+) : Union de types
    def process_id(identifier: int | str) -> bool:
        ...

    # Recommandé (Python 3.10+) : Optionnel (équivalent à int | None)
    def find_user(user_id: int) -> str | None:
        ...
    ```

### 2.3 Utilisation de `Any`
*   `typing.Any` indique qu'aucun contrôle de type statique n'est appliqué à cette variable. Utilisez-le avec parcimonie, uniquement lorsque le type est dynamique ou inconnu :
    ```python
    from typing import Any

    def parse_payload(raw_json: str) -> dict[str, Any]:
        ...
    ```

---

## 3. Types Avancés

### 3.1 Callables (Fonctions en argument)
*   Utilisez `collections.abc.Callable` ou `typing.Callable` pour typer des fonctions ou des callbacks :
    ```python
    from collections.abc import Callable

    # Signature : Callable[[TypeArg1, TypeArg2], TypeRetour]
    def execute_callback(callback: Callable[[str, int], bool]) -> None:
        callback("success", 200)
    ```

### 3.2 Protocoles (Sous-typage Structurel / Duck Typing)
*   Utilisez `typing.Protocol` (PEP 544) pour définir une interface implicite. Une classe implémente le protocole dès lors qu'elle possède les méthodes requises, sans héritage explicite :
    ```python
    from typing import Protocol

    class Renderable(Protocol):
        def render(self) -> str:
            ...

    # N'importe quelle classe avec une méthode render() satisfait ce protocole
    def display(widget: Renderable) -> None:
        print(widget.render())
    ```

---

## 4. Outils de validation statique des types

L'interpréteur Python classique ignore les annotations de type lors de l'exécution. Vous devez utiliser un linter de type statique externe pour détecter les anomalies :

*   **Vérification de type avec `mypy` :**
    Exécutez la commande suivante via l'outil `` `terminal` `` :
    ```bash
    mypy my_script.py
    ```
*   Configuration recommandée dans `pyproject.toml` :
    ```toml
    [tool.mypy]
    python_version = "3.10"
    warn_return_any = true
    warn_unused_configs = true
    disallow_untyped_defs = true
    ```
*   **Vérification rapide avec `pyright` ou `ruff` :**
    Certains éditeurs exécutent également des outils de validation en arrière-plan comme `pyright` pour une réactivité instantanée.

