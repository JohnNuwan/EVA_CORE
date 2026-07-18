---
name: python-pep257
description: "Rédiger des docstrings PEP 257 au format Google Style."
version: 1.0.0
author: EVA Agent (adapté de obra/superpowers)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [python, pep257, docstrings, google-style, documentation]
    related_skills: [python-pep8, python-pep484, python-pep20, simplify-code]
---

# Conventions de Docstrings Python (PEP 257 & Google Style)

## Vue d'ensemble

Cette compétence décrit les règles et bonnes pratiques pour la rédaction de docstrings de qualité industrielle en Python. Elle combine les exigences structurelles de la **PEP 257** et le formatage sémantique **Google Style**, largement adopté pour sa clarté et sa compatibilité avec les générateurs automatiques de documentation (comme Sphinx ou MkDocs).

---

## 1. Règles Fondamentales de la PEP 257

*   **Syntaxe :** Entourez toujours vos docstrings de trois guillemets doubles (`"""Docstring."""`). N'utilisez pas de guillemets simples.
*   **Emplacement :** Placez la docstring immédiatement au début de la définition d'un module, d'une classe, d'une fonction ou d'une méthode.
*   **Phrase de résumé :** La première ligne doit être un résumé concis décrivant l'effet de l'élément (ex: « Calcule le montant total des ventes. », se terminant par un point). Utilisez une tournure impérative (« Fait ceci », pas « Cette fonction fait ceci »).

### 1.1 Docstrings sur une seule ligne (One-line Docstrings)
*   Les guillemets fermants doivent figurer sur la même ligne que les guillemets ouvrants :
    ```python
    def calculate_square(number: float) -> float:
        """Calcule le carré d'un nombre donné."""
        return number ** 2
    ```

### 1.2 Docstrings sur plusieurs lignes (Multi-line Docstrings)
*   Une ligne de résumé concise, suivie d'une ligne vide, puis d'une description détaillée. Les guillemets fermants doivent figurer seuls sur leur propre ligne :
    ```python
    def connect_database(uri: str) -> Connection:
        """Établit une connexion avec la base de données cible.

        Cette fonction initialise le pilote, vérifie la disponibilité
        du service réseau et retourne l'objet de connexion actif.
        """
        ...
    ```

---

## 2. Le Format Google Style (Recommandé)

Pour structurer la description détaillée des arguments, retours, exceptions et exemples, le format **Google Style** est standardisé et hautement lisible.

### 2.1 Structure Générale d'une Fonction/Méthode
```python
def process_data(data: list[int], threshold: int = 10) -> list[int]:
    """Filtre et traite une liste de valeurs selon un seuil.

    Description détaillée de la logique de traitement et de son utilité
    dans le flux applicatif général.

    Args:
        data (list[int]): La liste des entiers à traiter.
        threshold (int, optional): Seuil de filtrage minimal. Par défaut à 10.

    Returns:
        list[int]: La liste contenant uniquement les valeurs supérieures au seuil.

    Raises:
        ValueError: Si la liste `data` est vide.
        TypeError: Si `data` n'est pas une liste d'entiers.

    Examples:
        >>> process_data([5, 12, 8, 20], threshold=10)
        [12, 20]
    """
    if not data:
        raise ValueError("La liste de données ne peut pas être vide.")
    return [x for x in data if x > threshold]
```

### 2.2 Sections Spécifiques Google Style

*   **Args:**
    *   Listez chaque argument avec son nom, son type entre parenthèses, deux-points, et sa description.
    *   Indiquez `optional` si l'argument dispose d'une valeur par défaut.
*   **Returns (ou Yields pour les générateurs):**
    *   Le type de retour suivi d'une description du résultat retourné.
*   **Raises:**
    *   Listez toutes les exceptions explicitement levées par le code avec les conditions associées.
*   **Examples:**
    *   Des exemples interactifs au format doctest (précédés de `>>>`) pour illustrer le comportement de l'API.

---

## 3. Docstrings de Classes et Modules

### 3.1 Docstrings de Classes
*   Décrivez le rôle global de la classe. Si applicable, listez ses attributs publics dans une section **Attributes:** :
    ```python
    class UserProfile:
        """Représente les informations de profil d'un utilisateur.

        Attributes:
            username (str): Le nom d'utilisateur unique.
            email (str): L'adresse e-mail associée.
            is_active (bool): Statut d'activation du compte.
        """
        def __init__(self, username: str, email: str):
            self.username = username
            self.email = email
            self.is_active = True
    ```

### 3.2 Docstrings de Modules
*   Placée tout au début du fichier `.py` (avant les imports), elle présente le but du module et peut lister ses fonctionnalités majeures ou exemples globaux :
    ```python
    """Module de traitement des flux de données IoT.

    Ce module fournit des outils pour analyser les trames binaires issues des capteurs,
    les convertir en objets structurés et les pousser dans la file d'attente.
    """
    import os
    ...
    ```

---

## 4. Outils de validation et de formatage automatique

Pour assurer la conformité avec la PEP 257 et le style Google, vous pouvez appeler les commandes suivantes via l'outil `` `terminal` `` :

*   **Analyse statique avec `pydocstyle` :**
    ```bash
    pydocstyle my_script.py --convention=google
    ```
*   **Validation complète avec `ruff` (qui intègre le jeu de règles pydocstyle `D`) :**
    ```bash
    ruff check my_script.py --select D
    ```

