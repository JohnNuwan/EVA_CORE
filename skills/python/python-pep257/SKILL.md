---
name: python-pep257
description: Guide PEP 257 pour les docstrings Python en style Google, rédigé en français. À charger avec python-pep8 pour toute écriture de code.
---

# PEP 257 — Conventions de Docstrings (Style Google, en Français)

Ce skill définit les règles de documentation du code Python selon la PEP 257, en utilisant le **style Google** pour la mise en forme. Toute fonction, classe, méthode ou module doit être documenté selon ces règles.

---

## 1. Principes Généraux (PEP 257)

### Règle d'or
Toute fonction, classe, méthode ou module **publique** doit avoir une docstring. Les fonctions/méthodes **privées** (préfixées par `_`) doivent avoir une docstring si leur comportement n'est pas évident.

### Format de base
- Utiliser `"""triples guillemets doubles"""`
- La première ligne est un résumé **en une phrase**, impératif, se terminant par un point
- Une ligne vide après le résumé
- Le corps détaillé suit

### Docstrings multi-lignes
```python
def fonction_exemple(param1: str, param2: int) -> bool:
    """Résumé concis de la fonction en une phrase.
    
    Explication détaillée du comportement, des cas particuliers,
    des algorithmes utilisés, etc. Peut s'étendre sur plusieurs
    lignes selon la complexité.
    """
    ...
```

---

## 2. Style Google — Structure Complète

Le style Google organise la docstring en sections clairement identifiées.

### 2.1 Fonctions et Méthodes

```python
def calculer_moyenne(
    notes: list[float],
    coefficients: list[float] | None = None,
    arrondir: bool = True,
) -> float:
    """Calcule la moyenne pondérée d'une série de notes.
    
    Si aucun coefficient n'est fourni, toutes les notes ont le même
    poids. Les notes négatives sont ignorées avec un avertissement.
    
    Args:
        notes: Liste des notes (sur 20). Les valeurs négatives
            sont ignorées.
        coefficients: Poids de chaque note. Si None, poids égaux.
            Doit avoir la même longueur que notes si fourni.
        arrondir: Si True, arrondit le résultat à 2 décimales.
    
    Returns:
        La moyenne pondérée calculée, arrondie si demandé.
    
    Raises:
        ValueError: Si `notes` est vide.
        TypeError: Si `coefficients` est fourni mais de longueur
            différente de `notes`.
    
    Example:
        >>> calculer_moyenne([15.0, 12.0, 18.0])
        15.0
        >>> calculer_moyenne([15.0, 12.0], [2.0, 1.0])
        14.0
    
    Note:
        Cette fonction suppose que les notes sont sur 20.
    """
    ...
```

**Sections disponibles pour les fonctions (dans l'ordre) :**
1. **Résumé** (obligatoire) — une ligne
2. **Corps** (optionnel) — paragraphes détaillés
3. **Args** (si paramètres) — chaque paramètre sur sa ligne
4. **Returns** (si retour) — type et description
5. **Yields** (si générateur) — type et description de ce qui est généré
6. **Raises** (si exceptions) — chaque exception documentée
7. **Example** (optionnel) — exemples d'utilisation en style doctest
8. **Note** / **Warning** / **See Also** (optionnel)

### 2.2 Classes

```python
class GestionnaireFichiers:
    """Gère la lecture et l'écriture de fichiers de configuration.
    
    Cette classe fournit une interface unifiée pour manipuler
    des fichiers JSON, YAML et TOML avec mise en cache.
    
    Attributes:
        chemin: Chemin absolu du fichier géré.
        format: Format du fichier ('json', 'yaml', 'toml').
        _cache: Dictionnaire interne de cache des valeurs lues.
    
    Example:
        >>> gestionnaire = GestionnaireFichiers('/etc/config.json')
        >>> gestionnaire.lire('database.host')
        'localhost'
    """
    
    def __init__(self, chemin: str, format: str | None = None):
        """Initialise le gestionnaire avec le chemin du fichier.
        
        Args:
            chemin: Chemin absolu ou relatif du fichier.
            format: Format du fichier. Si None, déduit de
                l'extension.
        
        Raises:
            FileNotFoundError: Si le fichier n'existe pas.
            ValueError: Si le format n'est pas supporté.
        """
        ...
```

**Sections disponibles pour les classes (dans l'ordre) :**
1. **Résumé** (obligatoire)
2. **Corps** (optionnel)
3. **Attributes** (attributs publics d'instance)
4. **Example** (optionnel)
5. **Note** / **Warning** (optionnel)

### 2.3 Modules

```python
"""Module de gestion des connexions réseau.
    
Ce module fournit des classes et fonctions pour établir, configurer
et surveiller des connexions TCP et UDP avec reconnexion automatique.

Example:
    >>> from reseau import ConnexionTCP
    >>> connexion = ConnexionTCP('localhost', 8080)
    >>> connexion.envoyer(b'Hello')
    
Attributes:
    TIMEOUT_DEFAUT (int): Délai d'attente par défaut en secondes.
    MAX_RECONNEXIONS (int): Nombre maximal de tentatives de reconnexion.
"""
```

---

## 3. Règles de Formatage Précises

### 3.1 Types dans les docstrings

Utiliser les **annotations de type Python** dans la signature, ET documenter les types dans la docstring :
```python
def traiter_donnees(
    entrees: list[dict[str, Any]],
    seuil: float = 0.5,
) -> list[str]:
    """Filtre les entrées selon un seuil de pertinence.
    
    Args:
        entrees: Liste de dictionnaires contenant les champs
            'texte' (str) et 'score' (float).
        seuil: Score minimum pour inclure une entrée.
    
    Returns:
        Liste des textes dont le score dépasse le seuil.
    """
```

### 3.2 Paramètres avec valeurs par défaut

```python
def creer_utilisateur(
    nom: str,
    age: int = 18,
    admin: bool = False,
) -> dict:
    """Crée un profil utilisateur.
    
    Args:
        nom: Nom complet de l'utilisateur.
        age: Âge de l'utilisateur. 18 par défaut.
        admin: Droits administrateur. Désactivé par défaut.
    
    Returns:
        Dictionnaire représentant le profil.
    """
```

### 3.3 Paramètres *args et **kwargs

```python
def journaliser(
    message: str,
    *args: Any,
    **kwargs: Any,
) -> None:
    """Enregistre un message dans le journal.
    
    Args:
        message: Message à journaliser avec placeholders {}.
        *args: Arguments positionnels pour le formatage du message.
        **kwargs: Arguments nommés additionnels :
            - niveau (str): Niveau de log ('info', 'warn', 'error').
            - fichier (Path): Fichier de sortie.
    """
```

### 3.4 Retours multiples (tuples)

```python
def diviser_avec_reste(a: int, b: int) -> tuple[int, int]:
    """Effectue une division entière et retourne quotient et reste.
    
    Args:
        a: Le dividende.
        b: Le diviseur (non nul).
    
    Returns:
        Un tuple (quotient, reste) de la division entière.
    
    Raises:
        ZeroDivisionError: Si b vaut 0.
    """
```

### 3.5 Générateurs

```python
def paginer(
    elements: list[Any],
    taille_page: int = 10,
) -> Generator[list[Any], None, None]:
    """Pagine une liste d'éléments par lots.
    
    Args:
        elements: Liste complète à paginer.
        taille_page: Nombre d'éléments par page.
    
    Yields:
        Des sous-listes de `taille_page` éléments.
    
    Example:
        >>> list(paginer([1, 2, 3, 4, 5], taille_page=2))
        [[1, 2], [3, 4], [5]]
    """
```

---

## 4. Cas Particuliers

### 4.1 Fonction qui ne retourne rien
```python
def afficher_menu() -> None:
    """Affiche le menu principal dans la console.
    
    Le menu est formaté avec des bordures et adapté à la largeur
    du terminal.
    """
```

### 4.2 Méthode __init__
```python
class ClientAPI:
    def __init__(
        self,
        url_base: str,
        timeout: int = 30,
    ) -> None:
        """Initialise le client HTTP.
        
        Args:
            url_base: URL racine de l'API (ex: 'https://api.exemple.com/v1').
            timeout: Délai maximal par requête en secondes.
        """
```

### 4.3 Propriétés
```python
class CompteBancaire:
    @property
    def solde(self) -> float:
        """float: Le solde actuel du compte, toujours positif."""
        return self._solde
```

### 4.4 Fonctions privées
```python
def _valider_email(adresse: str) -> bool:
    """Vérifie qu'une adresse email est syntaxiquement valide.
    
    Args:
        adresse: L'adresse email à valider.
    
    Returns:
        True si l'adresse est valide, False sinon.
    """
```

---

## 5. Règles Syntaxiques Strictes

### Indentation
- La docstring est indentée au même niveau que la définition
- Le contenu après `Args:`, `Returns:`, etc. est indenté de 4 espaces supplémentaires
- Les retours à la ligne dans les descriptions sont indentés pour alignement

### Ponctuation
- Le résumé se termine par un **point**
- Les descriptions de paramètres commencent par une **majuscule** et se terminent par un **point**
- Utiliser le **mode impératif** dans le résumé : "Calcule", "Retourne", "Vérifie"

### Types
- Utiliser les **types Python natifs** pour les annotations : `str`, `int`, `float`, `bool`, `list[str]`, `dict[str, int]`, `tuple[int, ...]`, `Path`
- Pour les types complexes, utiliser `Any` de `typing` ou les types concrets
- `Optional[X]` → `X | None`
- `Union[X, Y]` → `X | Y`

---

## 6. Anti-Patterns à Éviter

❌ Docstring absente sur une fonction publique
❌ Docstring qui répète le nom de la fonction
❌ Résumé de plus d'une ligne
❌ Sections Args/Returns absentes quand il y a des paramètres/retours
❌ Types uniquement dans la signature, pas dans la docstring
❌ Docstrings en anglais quand le projet est en français
❌ Utiliser `:param:` ou `:return:` (style Sphinx) — ici on utilise le style Google

---

## 7. Exemple Complet

```python
"""Module de calcul de statistiques descriptives.

Ce module fournit des fonctions pour calculer moyenne, médiane,
écart-type et autres indicateurs statistiques sur des séries
de données numériques.

Example:
    >>> from statistiques import calculer_moyenne, calculer_mediane
    >>> donnees = [1.0, 2.0, 3.0, 4.0, 5.0]
    >>> calculer_moyenne(donnees)
    3.0

Attributes:
    PRECISION (int): Nombre de décimales pour l'arrondi par défaut.
"""

from typing import Any

PRECISION = 4


class SerieStatistique:
    """Encapsule une série de données avec ses indicateurs statistiques.
    
    Calcule et met en cache les principaux indicateurs : moyenne,
    médiane, variance, écart-type, min, max.
    
    Attributes:
        donnees: Liste des valeurs numériques de la série.
        est_vide: True si la série ne contient aucune donnée.
    """
    
    def __init__(self, donnees: list[float]) -> None:
        """Initialise la série statistique.
        
        Args:
            donnees: Liste de valeurs numériques. Les NaN sont ignorés.
        
        Raises:
            TypeError: Si les valeurs ne sont pas numériques.
        """
        self.donnees = [v for v in donnees if not _est_nan(v)]
    
    @property
    def moyenne(self) -> float | None:
        """float ou None: La moyenne arithmétique, ou None si la série est vide."""
        if not self.donnees:
            return None
        return sum(self.donnees) / len(self.donnees)
    
    def resume(self) -> dict[str, Any]:
        """Produit un résumé statistique complet.
        
        Returns:
            Un dictionnaire contenant les clés 'moyenne', 'mediane',
            'ecart_type', 'min', 'max' et 'taille'. Les valeurs sont
            None si la série est vide.
        """
        ...


def calculer_moyenne(
    donnees: list[float],
    ponderation: list[float] | None = None,
) -> float:
    """Calcule la moyenne (simple ou pondérée) d'une série.
    
    Args:
        donnees: Série de valeurs numériques. Ne doit pas être vide.
        ponderation: Poids de chaque valeur. Si None, moyenne simple.
    
    Returns:
        La moyenne calculée.
    
    Raises:
        ValueError: Si `donnees` est vide ou si `ponderation` ne
            correspond pas à la taille de `donnees`.
    
    Example:
        >>> calculer_moyenne([2.0, 4.0, 6.0])
        4.0
        >>> calculer_moyenne([2.0, 4.0], [0.25, 0.75])
        3.5
    """
    ...


def _est_nan(valeur: float) -> bool:
    """Vérifie si une valeur est NaN (Not a Number).
    
    Args:
        valeur: Valeur à tester.
    
    Returns:
        True si la valeur est NaN.
    """
    return valeur != valeur
```

---

## Références
- PEP 257 : https://peps.python.org/pep-0257/
- Google Python Style Guide : https://google.github.io/styleguide/pyguide.html
- Ce skill est le complément obligatoire de `python-pep8`