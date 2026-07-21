---
name: python-pep8
description: Guide de style PEP 8 pour Python — règles de formatage, nommage, imports, espacement, et bonnes pratiques. À charger avant toute écriture ou revue de code Python.
---

# Guide de Style PEP 8 (Français)

Ce skill couvre l'intégralité de la PEP 8 — le guide officiel de style du code Python. À respecter impérativement pour tout code produit.

---

## 1. Indentation

- **4 espaces** par niveau d'indentation. Jamais de tabulations.
- Les espaces sont préférés aux tabulations.
- Python 3 interdit le mélange tabulations/espaces.

### Continuation de ligne

Pour une ligne qui dépasse 79 caractères, deux styles acceptés :

**Style 1 : Alignement vertical avec la parenthèse ouvrante**
```python
foo = fonction_longue(nom_var1, nom_var2,
                      nom_var3, nom_var4)
```

**Style 2 : Indentation supplémentaire (suspendue)**
```python
foo = fonction_longue(
    nom_var1, nom_var2,
    nom_var3, nom_var4,
)
```

```python
def fonction_longue(
        nom_var1, nom_var2,
        nom_var3, nom_var4):
    print(nom_var1)
```

**Règle :** La première ligne ne doit pas contenir d'argument. Le niveau d'indentation supplémentaire distingue clairement le corps de la fonction des arguments.

### Opérateurs de continuation

Le saut de ligne doit se faire **avant** l'opérateur binaire (PEP 8 moderne) :
```python
revenu = (prix_brut
          + taxes
          - remise
          + frais_livraison)
```

### Parenthèses fermantes

La parenthèse fermante peut être :
- Alignée avec le premier caractère non-blanc de la dernière ligne
- Alignée avec le premier caractère de la ligne qui commence la construction

```python
ma_liste = [
    1, 2, 3,
    4, 5, 6,
]

resultat = une_fonction_qui_prend_des_arguments(
    'a', 'b', 'c',
    'd', 'e', 'f',
)
```

---

## 2. Longueur Maximale des Lignes

- **79 caractères** pour le code
- **72 caractères** pour les docstrings et commentaires
- Les longues lignes d'import (`from module import ...`) et les URLs dans les commentaires peuvent dépasser.

### Coupure de longues lignes

Utiliser les parenthèses, crochets, accolades implicites :
```python
if (condition_longue_1
    and condition_longue_2
    and condition_longue_3):
    faire_action()
```

---

## 3. Lignes Vides

- **2 lignes vides** avant les définitions de classe et de fonction au niveau module
- **1 ligne vide** avant les méthodes d'une classe
- **1 ligne vide** pour séparer des groupes logiques dans une fonction (avec parcimonie)
- Les lignes vides supplémentaires peuvent séparer des groupes de fonctions liées

---

## 4. Encodage et Imports

### Encodage
- Les fichiers en Python 3 utilisent **UTF-8**
- Pas besoin de `# -*- coding: utf-8 -*-`

### Imports
Les imports doivent être sur des **lignes séparées** :
```python
# Correct
import os
import sys

# Incorrect
import os, sys
```

L'ordre des imports :
```python
# 1. Imports de la bibliothèque standard
import os
import sys
from pathlib import Path

# 2. Imports de bibliothèques tierces
import numpy as np
import requests

# 3. Imports locaux / du projet
from . import module_local
from .module_local import ClasseLocale
```

- Les imports doivent être en **haut du fichier**, après les commentaires/docstring du module
- Éviter les imports avec wildcard (`from module import *`)

---

## 5. Guillemets

- Les guillemets simples et doubles sont acceptables
- Rester **cohérent** dans un même fichier
- Pour les docstrings : **triples guillemets doubles** `"""`
- Pour les chaînes contenant des guillemets : alterner pour éviter l'échappement

---

## 6. Espaces dans les Expressions

### Opérateurs binaires
Un espace de chaque côté :
```python
x = 1
y = x + 5
z = x*2 + y*3  # Priorité : espaces autour de la plus basse priorité
```

### Opérateurs unaires
Pas d'espace :
```python
i += 1
x = -5
```

### Appels de fonction et indexation
**Pas d'espace** avant la parenthèse ouvrante :
```python
# Correct
ma_fonction(x, y)
liste[0]

# Incorrect
ma_fonction (x, y)
liste [0]
```

### Virgules, deux-points, points-virgules
- Virgule : pas d'espace avant, **1 espace après**
- Deux-points (slices) : espace égal des deux côtés ou pas d'espace
- Deux-points (dict, lambda) : pas d'espace avant, 1 espace après

```python
# Dictionnaire
d = {'cle': 'valeur', 'autre_cle': 42}

# Slice
liste[2:5]
liste[2:5:2]

# Annotation de fonction
def ma_fonction(param: int = 0) -> str:
    ...
```

### Arguments par défaut
**Pas d'espace** autour du `=` pour les arguments par mot-clé :
```python
def fonction(param='defaut'):
    ...

appeler(param='valeur')
```

---

## 7. Commentaires

### Commentaires de bloc
- Commencent par `# ` (dièse + espace)
- Sont des phrases complètes avec majuscule (sauf identifiants)
- Alignés avec le code qu'ils décrivent

### Commentaires en ligne
- Au moins **2 espaces** avant le `#`
- Utilisés avec parcimonie

### Commentaires de documentation (docstrings)
- Voir le skill `python-pep257` pour le style Google

---

## 8. Conventions de Nommage

### Noms de modules
- `minuscules_avec_underscore`
- Courts et descriptifs
- `mon_module.py`

### Noms de classes
- `PascalCase` (CapitalizedWords)
- `MaClasse`, `ClientHTTP`

### Noms de fonctions et méthodes
- `minuscules_avec_underscore`
- `calculer_total()`, `obtenir_utilisateur()`

### Noms de variables
- `minuscules_avec_underscore`
- `nom_utilisateur`, `prix_total`

### Constantes
- `MAJUSCULES_AVEC_UNDERSCORE`
- `MAX_CONNEXIONS = 100`

### Noms de packages
- Courts, en minuscules, pas d'underscore (sauf si nécessaire)
- `monpackage`

### Variables protégées (non-publiques)
- Préfixées par `_` (underscore simple)
- `_methode_interne`, `_attribut_prive`

### Variables pseudo-privées (name mangling)
- Préfixées par `__` (double underscore)
- `__methode_manglee`

### Méthodes spéciales (magiques / dunder)
- Encadrées par `__double_underscore__`
- `__init__`, `__str__`, `__len__`

---

## 9. Conventions de Structure

### Définition des classes
```python
class MaClasse:
    """Docstring de la classe au style Google (voir python-pep257)."""
    
    def __init__(self, param: str):
        self.param = param
    
    def methode(self) -> str:
        return self.param
```

### Comparaisons avec None
Toujours utiliser `is` / `is not` :
```python
if x is None:
    ...

if x is not None:
    ...
```

### Booléens
```python
# Correct
if est_valide:
    ...

# Incorrect
if est_valide == True:
    ...
```

### Séquences vides
```python
# Correct
if not sequence:
    ...

if len(sequence) == 0:  # également correct
    ...

# Incorrect
if len(sequence):
    ...
```

---

## 10. Bonnes Pratiques Supplémentaires

- Utiliser `def` pour les fonctions, `lambda` pour les cas simples seulement
- Préférer `try/except` spécifique plutôt que `except:` nu
- Utiliser `.startswith()` et `.endswith()` plutôt que le slicing de chaînes
- Utiliser `isinstance()` plutôt que `type()` pour vérifier les types
- Pour les séquences de chaînes : utiliser `''.join()` plutôt que `+=`
- Context managers (`with`) pour la gestion des ressources

---

## Références
- PEP 8 officielle : https://peps.python.org/pep-0008/
- Ce skill est le standard à appliquer pour tout code Python généré