---
name: python-pep8
description: "Respecter le guide de style PEP 8 pour le code Python."
version: 1.0.0
author: Helios Agent (adapté de obra/superpowers)
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [python, pep8, style-guide, formatting, clean-code]
    related_skills: [python-pep257, python-pep484, python-pep20, simplify-code]
---

# Guide de Style de Code Python (PEP 8)

## Vue d'ensemble

Cette compétence décrit les règles et conventions de mise en forme et de style définies dans la **PEP 8** (Style Guide for Python Code). Son respect garantit un code lisible, homogène et facilement maintenable par d'autres développeurs ou agents IA.

---

## 1. Mise en page du code (Layout)

### 1.1 Indentation
*   **Utilisez exclusivement 4 espaces par niveau d'indentation.** Ne mélangez jamais les tabulations et les espaces.
*   **Alignement des lignes de continuation :**
    ```python
    # Alignement correct avec le délimiteur d'ouverture
    foo = long_function_name(var_one, var_two,
                             var_three, var_four)

    # Indentation supplémentaire (double indentation de 8 espaces) pour séparer les arguments du corps de la fonction
    def long_function_name(
            var_one, var_two, var_three,
            var_four):
        print(var_one)
    ```

### 1.2 Longueur maximale des lignes
*   **Limitez toutes les lignes de code à un maximum de 79 caractères.**
*   Pour les docstrings et les commentaires, limitez la longueur à **72 caractères**.
*   Utilisez le pliage de ligne implicite de Python entre parenthèses, crochets et accolades plutôt que l'anti-slash `\`.

### 1.3 Coupure de ligne avant un opérateur binaire
*   Coupez la ligne **avant** l'opérateur binaire pour une meilleure lisibilité :
    ```python
    # Recommandé (PEP 8 moderne)
    income = (gross_wages
              + taxable_interest
              + (dividends - qualified_dividends)
              - ira_deduction)
    ```

### 1.4 Lignes vides
*   Séparez les fonctions de premier niveau et les définitions de classes par **deux lignes vides**.
*   Séparez les définitions de méthodes à l'intérieur d'une classe par **une seule ligne vide**.

### 1.5 Encodage du fichier source
*   Le code dans les fichiers sources Python doit toujours utiliser l'encodage **UTF-8**.

---

## 2. Imports

### 2.1 Structuration
*   Chaque import doit être sur une ligne distincte :
    ```python
    # Recommandé
    import os
    import sys

    # Autorisé pour les sous-composants
    from subprocess import Popen, PIPE
    ```
*   Groupez toujours vos imports dans l'ordre suivant, séparés par une ligne vide :
    1.  Bibliothèques standards (ex: `os`, `sys`, `json`).
    2.  Bibliothèques tierces (ex: `requests`, `numpy`, `pytest`).
    3.  Imports locaux propres au projet.

### 2.2 Recommandations
*   Privilégiez les imports absolus (`from mypkg.sibling import foo`).
*   Évitez absolument les imports globaux avec caractère générique (`from module import *`), car ils polluent l'espace de noms.

---

## 3. Espaces dans les expressions

*   **Évitez les espaces superflus** dans les situations suivantes :
    *   Immédiatement à l'intérieur des parenthèses, crochets ou accolades : `spam(ham[1], {eggs: 2})` (pas `spam( ham[ 1 ], { eggs: 2 } )`).
    *   Immédiatement avant une virgule, un point-virgule ou deux-points : `if x == 4: print(x, y); x, y = y, x`
    *   Immédiatement avant la parenthèse d'ouverture d'un appel de fonction ou d'un index de liste : `dct['key'] = list[index]` (pas `dct ['key'] = list [index]`).
*   Entourez toujours les opérateurs binaires (ex: `=`, `+=`, `==`, `<`, `>`, `and`, `or`) d'un seul espace de chaque côté.
*   N'utilisez **pas d'espaces** autour du signe `=` lors du passage d'arguments mot-clé ou de valeurs par défaut :
    ```python
    # Recommandé
    def complex_function(arg1, default_val=0):
        return spam(arg1, key=default_val)
    ```

---

## 4. Règles de Nommage (Naming Conventions)

| Élément | Format de Nommage | Exemple |
| :--- | :--- | :--- |
| **Packages / Modules** | Lettres minuscules, tirets bas autorisés si nécessaire. | `my_package`, `utils.py` |
| **Classes** | PascalCase (Capitalisation de chaque mot). | `UserProfile`, `SessionManager` |
| **Fonctions** | snake_case (minuscules séparées par des tirets bas). | `calculate_total()`, `get_user()` |
| **Variables** | snake_case. | `user_id`, `retry_count` |
| **Méthodes** | snake_case. | `update_status()`, `_internal_reset()` |
| **Constantes** | UPPER_CASE (capitales séparées par des tirets bas). | `MAX_RETRIES`, `TIMEOUT_SECONDS` |
| **Exceptions** | PascalCase, doit se terminer par `Error`. | `DatabaseConnectionError` |

*   **Attributs protégés :** Utilisez un seul tiret bas en préfixe (`_protected_attr`) pour les variables et fonctions internes.
*   **Attributs privés :** Utilisez un double tiret bas (`__private_attr`) pour déclencher le masquage de nom (name mangling) et éviter les conflits dans les sous-classes.

---

## 5. Recommandations de programmation

*   Comparez toujours les singletons (comme `None`) avec `is` ou `is not`, jamais avec des opérateurs d'égalité (`==`).
*   Utilisez `is not` plutôt que `not ... is` :
    ```python
    # Recommandé
    if foo is not None:
        pass
    ```
*   Ne liez pas de fonctions anonymes `lambda` à un identifiant avec un opérateur d'assignation. Utilisez une définition `def` classique :
    ```python
    # Recommandé
    def f(x): return 2 * x

    # À éviter
    f = lambda x: 2 * x
    ```
*   Dérivez vos exceptions de la classe intégrée `Exception` plutôt que de `BaseException`.
*   Soyez explicite lors de la capture d'exceptions. Évitez les clauses `except:` nues ; interceptez la classe d'exception spécifique :
    ```python
    # Recommandé
    try:
        value = int(data)
    except ValueError as e:
        logger.error(f"Invalid integer format: {e}")
    ```

---

## 6. Outils d'analyse et de validation automatique

Pour forcer et vérifier la conformité avec la PEP 8 sur votre espace de travail, vous pouvez appeler les commandes suivantes via l'outil `` `terminal` `` :

*   **Vérification de style avec `flake8` ou `ruff` :**
    ```bash
    flake8 my_script.py
    # Ou avec ruff (plus rapide et moderne)
    ruff check my_script.py
    ```
*   **Formatage automatique avec `black` ou `ruff format` :**
    ```bash
    black my_script.py
    # Ou avec ruff
    ruff format my_script.py
    ```

