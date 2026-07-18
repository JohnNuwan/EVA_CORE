---
name: python-pep572-pep634
description: "Utiliser l'opérateur Walrus et le Pattern Matching."
version: 1.0.0
author: EVA Agent (adapté de obra/superpowers)
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [python, pep572, pep634, walrus-operator, pattern-matching]
    related_skills: [python-pep8, python-pep257, python-pep20, simplify-code]
---

# Syntaxe Moderne Python (PEP 572 - Walrus & PEP 634 - Pattern Matching)

## Vue d'ensemble

Cette compétence décrit les règles d'utilisation et les bonnes pratiques pour deux fonctionnalités majeures de la syntaxe moderne de Python : l'opérateur d'assignation nommé **opérateur Walrus** (PEP 572) et le **Structural Pattern Matching** (PEP 634). Bien utilisées, elles réduisent la duplication de code et améliorent la clarté des embranchements complexes.

---

## 1. L'Opérateur Walrus (PEP 572)

L'opérateur Walrus (`:=`) permet d'assigner une valeur à une variable au sein même d'une expression plus large (comme une condition ou une boucle).

### 1.1 Cas d'usage principaux

*   **Boucles de lecture de flux :** Évite de répéter l'appel de fonction avant et pendant la boucle.
    ```python
    # Recommandé (Walrus)
    while (block := file.read(256)) != b"":
        process_block(block)
    ```

*   **Clauses conditionnelles de filtrage :** Récupère une valeur calculée et l'utilise directement dans la condition et son bloc associé.
    ```python
    # Recommandé (Walrus)
    if (match := pattern.search(text)) is not None:
        return match.group(1)
    ```

*   **Compréhensions de listes :** Réduit le double calcul d'une fonction coûteuse.
    ```python
    # Recommandé (Walrus)
    results = [y for x in data if (y := expensive_computation(x)) > 0]
    ```

### 1.2 Règle de bonne pratique
*   N'utilisez l'opérateur Walrus que lorsqu'il simplifie visiblement la lecture du code. Ne l'utilisez pas pour condenser du code au détriment de la clarté (les affectations simples classiques restent préférables pour la plupart des variables).

---

## 2. Structural Pattern Matching (PEP 634)

Introduit en Python 3.10, le pattern matching structurel utilise les mots-clés `match` et `case` pour valider et extraire des données selon des motifs structurels spécifiques.

### 2.1 Correspondance simple (comparable à un switch-case)
```python
def handle_status(status_code: int) -> str:
    match status_code:
        case 200 | 201:
            return "Succès"
        case 400:
            return "Requête invalide"
        case 404:
            return "Non trouvé"
        case _:  # Cas générique par défaut (wildcard)
            return "Erreur inconnue"
```

### 2.2 Extraction et validation de structures complexes
Le pattern matching excelle pour valider et extraire des valeurs à partir de dictionnaires ou de tuples :
```python
def process_message(message: dict) -> None:
    match message:
        # Correspond si 'type' vaut 'alert' et extrait le message sous 'text'
        case {"type": "alert", "text": str(body)}:
            show_alert(body)
        
        # Correspond si 'type' vaut 'status' et extrait une liste de deux entiers
        case {"type": "status", "data": [int(code), int(level)]}:
            update_status(code, level)
            
        case _:
            raise ValueError("Format de message non reconnu.")
```

### 2.3 Correspondance avec des Classes et des Clauses de Garde (Guards)
Vous pouvez inspecter les instances de classes et ajouter des conditions dynamiques à l'aide du mot-clé `if` :
```python
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

def locate_point(point: Point) -> None:
    match point:
        case Point(x=0, y=0):
            print("À l'origine.")
        case Point(x=x, y=y) if x == y:
            print(f"Sur la diagonale y = x = {x}.")
        case Point(x=x, y=y):
            print(f"Point libre à ({x}, {y}).")
```

### 2.4 Bonnes pratiques du Pattern Matching
*   Fournissez toujours un motif par défaut `case _:` si vos cas ne couvrent pas l'intégralité des possibilités, afin d'éviter les comportements imprévus.
*   Utilisez le pattern matching lorsque vous devez analyser la structure ou le type des données, et non pour remplacer des chaînes de simples comparaisons arithmétiques qui se lisent mieux avec des `if/elif`.

