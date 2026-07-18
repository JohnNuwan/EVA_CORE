---
name: python-pep20
description: "Écrire du code idiomatique selon le Zen de Python (PEP 20)."
version: 1.0.0
author: EVA Agent (adapté de obra/superpowers)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [python, pep20, zen-of-python, clean-code, design-patterns]
    related_skills: [python-pep8, python-pep257, python-pep484, simplify-code]
---

# Le Zen de Python (PEP 20) et Code Idiomatique

## Vue d'ensemble

Le **Zen de Python** (PEP 20) est un ensemble de 19 principes directeurs guidant la conception du langage Python et l'écriture de programmes. Suivre ces principes permet d'écrire du code "pythonique" : un code simple, lisible, explicite et facile à maintenir.

---

## 1. Principes Clés et Applications Pratiques

### 1.1 L'explicite est meilleur que l'implicite (Explicit is better than implicit)
*   Ne masquez pas le comportement ou les données. Préfèrez la clarté à la magie.
    *   **Non-pythonique (implicite/magique) :**
        ```python
        # Import global masquant la provenance des fonctions
        from module import *
        ```
    *   **Pythonique (explicite) :**
        ```python
        import module
        # Ou
        from module import target_function
        ```

### 1.2 Le simple est meilleur que le complexe (Simple is better than complex)
*   Résolvez les problèmes de la manière la plus directe possible avant d'envisager des architectures lourdes.
    *   **Non-pythonique (sur-conception) :**
        ```python
        # Utilisation d'une classe complexe pour une simple fonction de calcul
        class Adder:
            def __init__(self, value):
                self.value = value
            def add(self, other):
                return self.value + other
        ```
    *   **Pythonique (simple) :**
        ```python
        def add(a, b):
            return a + b
        ```

### 1.3 Le plat est meilleur que l'imbriqué (Flat is better than nested)
*   Évitez d'accumuler de multiples niveaux d'indentation conditionnelle. Utilisez des clauses de garde (guard clauses) pour retourner rapidement.
    *   **Non-pythonique (imbrication profonde) :**
        ```python
        def process_user(user):
            if user is not None:
                if user.is_active:
                    if user.has_permission("write"):
                        # Logique principale (indentée de 24 espaces !)
                        ...
        ```
    *   **Pythonique (plat via des clauses de garde) :**
        ```python
        def process_user(user):
            if user is None or not user.is_active:
                return
            if not user.has_permission("write"):
                return
            # Logique principale (indentée de 4 espaces uniquement)
            ...
        ```

### 1.4 La lisibilité compte (Readability counts)
*   Écrivez du code lisible pour les humains. Utilisez des structures idiomatiques (comme les compréhensions de listes avec modération).
    *   **Non-pythonique (compréhension trop dense et illisible) :**
        ```python
        matrix = [[1, 2], [3, 4]]
        # Trop complexe à décoder mentalement
        flat = [x for sub in matrix for x in sub if x % 2 == 0]
        ```
    *   **Pythonique (aéré ou décomposé) :**
        ```python
        matrix = [[1, 2], [3, 4]]
        flat = []
        for sublist in matrix:
            for x in sublist:
                if x % 2 == 0:
                    flat.append(x)
        ```

### 1.5 Les erreurs ne devraient jamais passer sous silence (Errors should never pass silently)
*   Ne capturez pas silencieusement toutes les exceptions sans journalisation ou correction.
    *   **Non-pythonique (silence destructeur) :**
        ```python
        try:
            configure_system()
        except Exception:
            pass  # L'erreur est masquée, rendant le débogage impossible !
        ```
    *   **Pythonique (gestion explicite) :**
        ```python
        try:
            configure_system()
        except SystemConfigError as e:
            logger.error(f"Échec de configuration du système : {e}")
            raise
        ```

---

## 2. Accéder au Zen de Python dans le Terminal

Vous pouvez afficher à tout moment le texte original du Zen de Python depuis l'outil `` `terminal` `` en démarrant un interpréteur Python :

```bash
python -c "import this"
```

*Sortie abrégée (traduction) :*
> *Beautiful is better than ugly.* (Le beau est meilleur que le laid.)
> *Explicit is better than implicit.* (L'explicite est meilleur que l'implicite.)
> *Simple is better than complex.* (Le simple est meilleur que le complexe.)
> *Complex is better than complicated.* (Le complexe est meilleur que le compliqué.)
> *Flat is better than nested.* (Le plat est meilleur que l'imbriqué.)
> *Readability counts.* (La lisibilité compte.)
> *Special cases aren't special enough to break the rules.* (Les cas particuliers ne le sont pas assez pour enfreindre les règles.)

