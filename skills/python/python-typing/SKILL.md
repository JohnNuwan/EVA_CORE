---
name: python-typing
description: Guide complet des annotations de type Python (PEP 484, 526, 604, 585, etc.) — syntaxe, types génériques, protocoles, surcharges, et bonnes pratiques. En français.
---

# Annotations de Type Python — Guide Complet (Français)

Ce skill couvre l'ensemble du système de typage statique de Python moderne (3.10+). À utiliser avec Mypy/Pyright pour la vérification.

---

## 1. Types de Base

```python
# Scalaires
age: int = 25
nom: str = "Alice"
prix: float = 9.99
actif: bool = True
donnees: bytes = b"hello"

# None
resultat: None = None

# Any (désactive le typage)
from typing import Any
valeur: Any = "n'importe quoi"
```

---

## 2. Types de Conteneurs

```python
# Listes (PEP 585 — pas besoin de typing.List)
nombres: list[int] = [1, 2, 3]
chaines: list[str] = ["a", "b"]
mixtes: list[int | str] = [1, "deux"]

# Tuples
coordonnees: tuple[int, int] = (10, 20)
triplet: tuple[int, str, float] = (1, "a", 3.14)
suite: tuple[int, ...] = (1, 2, 3, 4, 5)  # longueur variable

# Dictionnaires
ages: dict[str, int] = {"Alice": 30, "Bob": 25}
config: dict[str, str | int | bool] = {"host": "localhost", "port": 8080}

# Ensembles
tags: set[str] = {"python", "typing", "mypy"}
```

---

## 3. Types Union et Optionnel

```python
# Union avec | (PEP 604, Python 3.10+)
identifiant: int | str = 42
identifiant = "abc123"

# Optionnel = Union avec None
nom_optionnel: str | None = None
nom_optionnel = "Alice"

# Dans une fonction
def trouver_utilisateur(id: int) -> dict[str, str] | None:
    """Recherche un utilisateur par son identifiant.
    
    Args:
        id: L'identifiant unique de l'utilisateur.
    
    Returns:
        Le profil utilisateur si trouvé, None sinon.
    """
    ...
```

---

## 4. Types Génériques Avancés

```python
from typing import TypeVar, Generic, Sequence, Callable

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

class Cache(Generic[K, V]):
    """Cache générique clé-valeur avec expiration."""
    
    def __init__(self) -> None:
        self._stockage: dict[K, V] = {}
    
    def obtenir(self, cle: K) -> V | None:
        return self._stockage.get(cle)
    
    def definir(self, cle: K, valeur: V) -> None:
        self._stockage[cle] = valeur


class FileAttente(Generic[T]):
    """File d'attente FIFO générique."""
    
    def __init__(self) -> None:
        self._elements: list[T] = []
    
    def enfiler(self, element: T) -> None:
        self._elements.append(element)
    
    def defiler(self) -> T:
        if not self._elements:
            raise IndexError("File vide")
        return self._elements.pop(0)
```

---

## 5. TypeVar avec Contraintes

```python
from typing import TypeVar

# Contrainte : uniquement ces types
Numerique = TypeVar("Numerique", int, float)

def multiplier(a: Numerique, b: Numerique) -> Numerique:
    return a * b

# Correct
multiplier(2, 3)      # int
multiplier(2.5, 3.0)  # float

# Lié : doit être une sous-classe de...
Comparable = TypeVar("Comparable", bound="Comparable")

class ArbreBinaire(Generic[Comparable]):
    def __init__(self, valeur: Comparable) -> None:
        self.valeur = valeur
        self.gauche: ArbreBinaire[Comparable] | None = None
        self.droite: ArbreBinaire[Comparable] | None = None
```

---

## 6. Callable (Fonctions)

```python
from typing import Callable

# Signature : (args) -> retour
Transformateur: type = Callable[[int], str]
Filtre: type = Callable[[str], bool]
Comparateur: type = Callable[[int, int], int]

def appliquer(
    valeurs: list[int],
    operation: Callable[[int], str],
) -> list[str]:
    """Applique une transformation à chaque élément."""
    return [operation(v) for v in valeurs]

# Avec **kwargs
Gestionnaire: type = Callable[..., None]  # n'importe quels arguments
```

---

## 7. Literal

```python
from typing import Literal

# Valeurs précises autorisées
Direction = Literal["nord", "sud", "est", "ouest"]
NiveauLog = Literal["debug", "info", "warning", "error", "critical"]
MethodeHTTP = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

def se_deplacer(direction: Direction) -> None:
    ...

def journaliser(message: str, niveau: NiveauLog = "info") -> None:
    ...

# Avec Union
CodeStatut: type = Literal[200, 201, 204] | Literal[400, 404, 500]
```

---

## 8. TypedDict

```python
from typing import TypedDict, NotRequired  # NotRequired en 3.11+

class ProfilUtilisateur(TypedDict):
    """Structure d'un profil utilisateur."""
    id: int
    nom: str
    email: str
    age: NotRequired[int]  # Optionnel (Python 3.11+)
    roles: NotRequired[list[str]]


class ConfigApplication(TypedDict, total=False):
    """Tous les champs sont optionnels avec total=False."""
    host: str
    port: int
    debug: bool
    log_level: str


def creer_profil(donnees: ProfilUtilisateur) -> str:
    return f"Profil créé : {donnees['nom']}"

# Usage
profil: ProfilUtilisateur = {
    "id": 1,
    "nom": "Alice",
    "email": "alice@exemple.com",
}
```

---

## 9. Protocol (Typage Structurel)

```python
from typing import Protocol, runtime_checkable

class Ouvrable(Protocol):
    """Tout objet qui peut être ouvert."""
    def ouvrir(self) -> str: ...
    def fermer(self) -> None: ...

class Connexion:
    def ouvrir(self) -> str:
        return "Connecté"
    def fermer(self) -> None:
        print("Fermé")

class Fichier:
    def ouvrir(self) -> str:
        return "Fichier ouvert"
    def fermer(self) -> None:
        print("Fichier fermé")

# Les deux sont compatibles avec Ouvrable sans héritage !
def utiliser(ressource: Ouvrable) -> str:
    resultat = ressource.ouvrir()
    ressource.fermer()
    return resultat

utiliser(Connexion())  # OK
utiliser(Fichier())    # OK


# Protocole avec @runtime_checkable
@runtime_checkable
class Iterable(Protocol):
    def __iter__(self) -> object: ...

isinstance([1, 2, 3], Iterable)  # True
```

---

## 10. Annotations pour Fonctions Avancées

### Surcharge (@overload) — PEP 484

```python
from typing import overload

@overload
def rechercher(id: int) -> dict[str, str]: ...

@overload
def rechercher(nom: str) -> list[dict[str, str]]: ...

def rechercher(id_nom: int | str) -> dict[str, str] | list[dict[str, str]]:
    """Recherche un utilisateur par ID ou par nom.
    
    Args:
        id_nom: Identifiant numérique ou nom à rechercher.
    
    Returns:
        Un profil unique si recherche par ID, une liste si par nom.
    """
    if isinstance(id_nom, int):
        return {"id": str(id_nom), "nom": "Trouvé"}
    return [{"id": "1", "nom": id_nom}]
```

### ParamSpec (typage de décorateurs)

```python
from typing import Callable, TypeVar
from typing import ParamSpec  # Python 3.10+

P = ParamSpec("P")
R = TypeVar("R")

def journaliser(
    fonction: Callable[P, R],
) -> Callable[P, R]:
    """Décorateur qui journalise les appels de fonction.
    
    Conserve la signature originale grâce à ParamSpec.
    """
    from functools import wraps
    
    @wraps(fonction)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"Appel : {fonction.__name__}({args}, {kwargs})")
        return fonction(*args, **kwargs)
    return wrapper

@journaliser
def additionner(a: int, b: int) -> int:
    return a + b

# Le type est conservé : (int, int) -> int
```

---

## 11. Final et ClassVar

```python
from typing import Final, ClassVar

# Constantes (PEP 591)
MAX_CONNEXIONS: Final[int] = 100
PI: Final[float] = 3.14159

class Compteur:
    # Variable de classe (pas d'instance)
    total: ClassVar[int] = 0
    
    def __init__(self) -> None:
        Compteur.total += 1
        self.valeur: int = 0
```

---

## 12. TypeGuard et TypeIs (Python 3.10+ / 3.13+)

```python
from typing import TypeGuard, TypeIs

def est_liste_entiers(valeur: object) -> TypeGuard[list[int]]:
    """Vérifie qu'une valeur est une liste d'entiers."""
    return isinstance(valeur, list) and all(isinstance(x, int) for x in valeur)


def est_entier(valeur: object) -> TypeIs[int]:
    """Affine le type : si True, c'est un int. Si False, ce n'est PAS un int."""
    return isinstance(valeur, int)


def traiter(valeur: int | str) -> str:
    if est_entier(valeur):
        # Ici valeur est int
        return str(valeur * 2)
    else:
        # Ici valeur est str (grâce à TypeIs)
        return valeur.upper()
```

---

## 13. Types pratiques pour Cas Courants

```python
from pathlib import Path
from datetime import datetime
from collections.abc import Sequence, Mapping, Iterable, Iterator
from typing import Any

# Fichiers
chemin_config: Path = Path("/etc/config.json")

# Temps
date_creation: datetime = datetime.now()

# Séquences (plus génériques que list)
def traiter_sequence(elements: Sequence[int]) -> int:
    """Accepte list, tuple, range, etc."""
    return sum(elements)

# Mappings (plus génériques que dict)
def lire_config(source: Mapping[str, Any]) -> str:
    return source.get("nom", "inconnu")

# Itérateurs
def generer_ids() -> Iterator[int]:
    i = 1
    while True:
        yield i
        i += 1
```

---

## 14. Bonnes Pratiques

1. **Activer la vérification stricte** : `mypy --strict` ou `pyright` en mode strict
2. **Éviter `Any`** — c'est une échappatoire, pas une solution
3. **Préférer `X | None` à `Optional[X]`** (PEP 604)
4. **Préférer `list[X]` à `typing.List[X]`** (PEP 585)
5. **Utiliser `collections.abc.Sequence`** plutôt que `list` pour les paramètres (plus flexible)
6. **TypedDict > dict[str, Any]** pour les structures connues
7. **Ne pas annoter `self`** dans les méthodes
8. **Ne pas annoter `cls`** dans `@classmethod`
9. **Les variables de classe se distinguent avec `ClassVar`**

---

## Références
- PEP 484 : https://peps.python.org/pep-0484/
- PEP 526 : https://peps.python.org/pep-0526/
- PEP 585 : https://peps.python.org/pep-0585/
- PEP 604 : https://peps.python.org/pep-0604/