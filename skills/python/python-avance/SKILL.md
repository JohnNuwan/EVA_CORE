---
name: python-avance
description: Concepts Python avancés — décorateurs, générateurs, context managers, descripteurs, métaclasses, properties, slots, dataclasses, énumérations. En français.
---

# Python Avancé — Guide Complet (Français)

Ce skill couvre les concepts avancés de Python pour écrire du code élégant, performant et pythonique.

---

## 1. Itérateurs et Générateurs

### Protocole Itérateur

```python
from typing import Iterator


class Compteur:
    """Itérateur qui compte de 0 à max.
    
    Attributes:
        max: Valeur maximale (exclusive).
        _courant: Compteur interne.
    """
    
    def __init__(self, max: int) -> None:
        """Initialise le compteur.
        
        Args:
            max: Valeur maximale (exclusive).
        """
        self.max = max
        self._courant = 0
    
    def __iter__(self) -> "Compteur":
        self._courant = 0
        return self
    
    def __next__(self) -> int:
        if self._courant >= self.max:
            raise StopIteration
        self._courant += 1
        return self._courant - 1
```

### Générateurs (yield)

```python
from typing import Generator, Iterator


def plage(a: int, b: int) -> Generator[int, None, None]:
    """Générateur équivalent à range(a, b).
    
    Args:
        a: Début (inclus).
        b: Fin (exclusive).
    
    Yields:
        Les entiers de a à b-1.
    """
    courant = a
    while courant < b:
        yield courant
        courant += 1


def fibonacci() -> Generator[int, None, None]:
    """Suite de Fibonacci infinie."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# Générateur avec send()
def accumulateur() -> Generator[float, float, list[float]]:
    """Accumule les valeurs envoyées via send().
    
    Yields:
        La somme courante après chaque valeur reçue.
    
    Returns:
        La liste de toutes les valeurs accumulées.
    """
    valeurs: list[float] = []
    total = 0.0
    while True:
        valeur = yield total
        if valeur is None:
            break
        valeurs.append(valeur)
        total += valeur
    return valeurs


# yield from (délégation)
def aplatir(
    listes: list[list[int]],
) -> Generator[int, None, None]:
    """Aplatit une liste de listes.
    
    Args:
        listes: Liste de listes d'entiers.
    
    Yields:
        Chaque entier, dans l'ordre.
    """
    for sous_liste in listes:
        yield from sous_liste
```

### Expressions Génératrices

```python
# Syntaxe compacte (comme une compréhension mais paresseuse)
carres = (x ** 2 for x in range(10))  # Ne calcule rien immédiatement

# Versus compréhension de liste (évaluée immédiatement)
carres_liste = [x ** 2 for x in range(10)]  # Tout en mémoire
```

---

## 2. Décorateurs

### Décorateur simple

```python
from typing import Callable, Any
from functools import wraps
import time


def chronometrer(
    fonction: Callable[..., Any],
) -> Callable[..., Any]:
    """Décorateur qui mesure le temps d'exécution d'une fonction.
    
    Args:
        fonction: La fonction à décorer.
    
    Returns:
        La fonction enrobée avec mesure de temps.
    """
    @wraps(fonction)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        debut = time.perf_counter()
        resultat = fonction(*args, **kwargs)
        duree = time.perf_counter() - debut
        print(f"{fonction.__name__} a pris {duree:.3f}s")
        return resultat
    return wrapper


@chronometrer
def calcul_lourd(n: int) -> int:
    """Calcule la somme de 0 à n."""
    return sum(range(n + 1))
```

### Décorateur avec paramètres

```python
from typing import Callable, Any


def repeter(
    fois: int = 2,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Décorateur paramétré qui répète l'exécution d'une fonction.
    
    Args:
        fois: Nombre de répétitions.
    
    Returns:
        Le décorateur configuré.
    """
    def decorateur(fonction: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fonction)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for i in range(fois):
                resultat = fonction(*args, **kwargs)
            return resultat
        return wrapper
    return decorateur


@repeter(fois=3)
def saluer(nom: str) -> str:
    """Saluer quelqu'un (répété 3 fois)."""
    print(f"Bonjour {nom}!")
    return nom
```

### Décorateurs de classe

```python
class Singleton:
    """Décorateur de classe qui implémente le patron Singleton."""
    
    def __init__(self, classe: type) -> None:
        self._classe = classe
        self._instance = None
    
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self._instance is None:
            self._instance = self._classe(*args, **kwargs)
        return self._instance


@Singleton
class Config:
    """Configuration globale de l'application."""
    def __init__(self) -> None:
        self.debug = False
```

---

## 3. Context Managers

### Via une classe (__enter__ / __exit__)

```python
from types import TracebackType
from typing import Any


class ConnexionBD:
    """Gère une connexion à une base de données."""
    
    def __init__(self, url: str) -> None:
        """Initialise avec l'URL de connexion.
        
        Args:
            url: Chaîne de connexion à la base.
        """
        self.url = url
        self._connexion = None
    
    def __enter__(self) -> "ConnexionBD":
        print(f"→ Connexion à {self.url}")
        self._connexion = {"ouverte": True}
        return self
    
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        print("→ Fermeture de la connexion")
        self._connexion = None
        return False  # Ne pas supprimer l'exception
```

### Via contextmanager (générateur)

```python
from contextlib import contextmanager
from typing import Iterator, Any
from pathlib import Path


@contextmanager
def fichier_ouvert(
    chemin: Path,
    mode: str = "r",
) -> Iterator[Any]:
    """Ouvre un fichier et garantit sa fermeture.
    
    Args:
        chemin: Chemin du fichier.
        mode: Mode d'ouverture ('r', 'w', 'a').
    
    Yields:
        L'objet fichier ouvert.
    """
    f = open(chemin, mode)
    try:
        yield f
    finally:
        f.close()


# Usage
with fichier_ouvert(Path("/tmp/test.txt"), "w") as f:
    f.write("Bonjour")
```

### Context managers utiles de contextlib

```python
from contextlib import suppress, redirect_stdout, ExitStack
import io

# Ignorer une exception spécifique
with suppress(FileNotFoundError):
    Path("/inexistant").unlink()

# Rediriger stdout
buffer = io.StringIO()
with redirect_stdout(buffer):
    print("Ceci va dans le buffer")

print(buffer.getvalue())  # "Ceci va dans le buffer\n"

# ExitStack : combiner plusieurs context managers dynamiquement
with ExitStack() as pile:
    fichiers = [
        pile.enter_context(open(f"fichier_{i}.txt", "w"))
        for i in range(5)
    ]
    for f in fichiers:
        f.write("données")
    # Tous les fichiers sont fermés automatiquement
```

---

## 4. Properties et Descripteurs

### @property

```python
class Temperature:
    """Représente une température avec validation.
    
    Attributes:
        _celsius: Valeur en Celsius (interne).
    """
    
    def __init__(self, celsius: float = 0) -> None:
        """Initialise la température.
        
        Args:
            celsius: Température en degrés Celsius.
        """
        self._celsius = celsius
    
    @property
    def celsius(self) -> float:
        """float: Température en Celsius."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, valeur: float) -> None:
        if valeur < -273.15:
            raise ValueError("Température sous le zéro absolu !")
        self._celsius = valeur
    
    @property
    def fahrenheit(self) -> float:
        """float: Température en Fahrenheit (calculée)."""
        return self._celsius * 9 / 5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, valeur: float) -> None:
        self.celsius = (valeur - 32) * 5 / 9


# Propriété mise en cache
from functools import cached_property  # Python 3.8+

class Analyseur:
    """Analyse un fichier de données."""
    
    def __init__(self, chemin: Path) -> None:
        self.chemin = chemin
    
    @cached_property
    def donnees(self) -> list[dict]:
        """Charge et parse les données (une seule fois)."""
        print("→ Chargement des données...")
        return [{"ligne": i} for i in range(1000)]
```

### Descripteurs

```python
from typing import Any


class Valide:
    """Descripteur qui valide que la valeur est positive.
    
    Attributes:
        nom: Nom de l'attribut (défini via __set_name__).
    """
    
    def __set_name__(self, owner: type, nom: str) -> None:
        self.nom = f"_{nom}"
    
    def __get__(self, obj: Any, objtype: type | None = None) -> Any:
        if obj is None:
            return self
        return getattr(obj, self.nom)
    
    def __set__(self, obj: Any, valeur: float) -> None:
        if valeur < 0:
            raise ValueError(f"{self.nom[1:]} doit être positif")
        setattr(obj, self.nom, valeur)


class Produit:
    """Produit avec prix et quantité validés."""
    
    prix = Valide()
    quantite = Valide()
    
    def __init__(self, nom: str, prix: float, quantite: int) -> None:
        """Initialise le produit.
        
        Args:
            nom: Nom du produit.
            prix: Prix unitaire (doit être positif).
            quantite: Quantité en stock (doit être positive).
        """
        self.nom = nom
        self.prix = prix
        self.quantite = quantite
```

---

## 5. Métaclasses

```python
# Métaclasse simple : journaliser la création de classes
class MetaJournal(type):
    """Métaclasse qui journalise la création de toute classe."""
    
    def __new__(
        mcs,
        nom: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> type:
        print(f"→ Création de la classe : {nom}")
        return super().__new__(mcs, nom, bases, namespace)
    
    def __init__(
        cls,
        nom: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
    ) -> None:
        print(f"→ Initialisation de : {nom}")
        super().__init__(nom, bases, namespace)


class Base(metaclass=MetaJournal):
    """Classe de base avec métaclasse."""
    pass


class MaClasse(Base):
    """Cette classe sera journalisée."""
    pass
```

---

## 6. Data Classes

```python
from dataclasses import dataclass, field, asdict, astuple
from typing import ClassVar


@dataclass(frozen=True)
class Point:
    """Point 2D immuable."""
    
    x: float
    y: float
    
    def distance_origine(self) -> float:
        """Calcule la distance à l'origine."""
        return (self.x ** 2 + self.y ** 2) ** 0.5


@dataclass
class Utilisateur:
    """Profil utilisateur avec champs optionnels."""
    
    nom: str
    email: str
    age: int = 0
    roles: list[str] = field(default_factory=list)
    _id: int = field(default=0, repr=False)  # Caché du repr
    MAX_AGE: ClassVar[int] = 150  # Variable de classe, pas un champ
    
    @property
    def est_majeur(self) -> bool:
        """bool: True si l'utilisateur est majeur."""
        return self.age >= 18
```

---

## 7. Énumérations (Enum)

```python
from enum import Enum, auto, IntEnum, StrEnum, Flag


class StatutTache(StrEnum):
    """Statuts possibles d'une tâche (valeurs en chaînes)."""
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"


class Priorite(IntEnum):
    """Niveaux de priorité (ordonnés numériquement)."""
    BASSE = 1
    NORMALE = 2
    HAUTE = 3
    CRITIQUE = 4


class Permission(Flag):
    """Permissions combinables avec |."""
    LECTURE = 1
    ECRITURE = 2
    EXECUTION = 4
    TOUT = LECTURE | ECRITURE | EXECUTION


# Usage
class Tache:
    """Représente une tâche avec statut et priorité."""
    
    def __init__(
        self,
        titre: str,
        statut: StatutTache = StatutTache.A_FAIRE,
        priorite: Priorite = Priorite.NORMALE,
    ) -> None:
        self.titre = titre
        self.statut = statut
        self.priorite = priorite
```

---

## 8. __slots__

```python
class PointOptimise:
    """Point 2D optimisé en mémoire avec __slots__.
    
    Réduit la consommation mémoire d'environ 50% et accélère
    l'accès aux attributs. À utiliser quand on crée beaucoup
    d'instances.
    """
    
    __slots__ = ("x", "y")
    
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
```

---

## 9. Opérateurs Surchargés

```python
from typing import Self


class Vecteur:
    """Vecteur 2D avec opérations arithmétiques."""
    
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"Vecteur({self.x}, {self.y})"
    
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"
    
    def __add__(self, autre: "Vecteur") -> "Vecteur":
        return Vecteur(self.x + autre.x, self.y + autre.y)
    
    def __sub__(self, autre: "Vecteur") -> "Vecteur":
        return Vecteur(self.x - autre.x, self.y - autre.y)
    
    def __mul__(self, scalaire: float) -> "Vecteur":
        return Vecteur(self.x * scalaire, self.y * scalaire)
    
    def __rmul__(self, scalaire: float) -> "Vecteur":
        return self * scalaire  # 3 * vecteur
    
    def __eq__(self, autre: object) -> bool:
        if not isinstance(autre, Vecteur):
            return NotImplemented
        return self.x == autre.x and self.y == autre.y
    
    def __hash__(self) -> int:
        return hash((self.x, self.y))
    
    def __abs__(self) -> float:
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def __bool__(self) -> bool:
        return self.x != 0 or self.y != 0
    
    def __neg__(self) -> "Vecteur":
        return Vecteur(-self.x, -self.y)
```

---

## 10. Walrus Operator (:=)

```python
# Affectation dans une expression (Python 3.8+)

# Dans une condition
if (n := len(liste)) > 10:
    print(f"Grande liste de {n} éléments")

# Dans une compréhension
resultats = [y for x in range(10) if (y := x ** 2) > 20]

# Dans une boucle while
while (ligne := fichier.readline().strip()):
    traiter(ligne)
```

---

## 11. Pattern Matching (match/case) — Python 3.10+

```python
def analyser_commande(commande: str | list[str] | dict) -> str:
    """Analyse une commande selon sa structure.
    
    Args:
        commande: La commande à analyser.
    
    Returns:
        Description de la commande.
    """
    match commande:
        case "aide" | "help" | "?":
            return "Aide demandée"
        
        case ["quitter" | "exit", *reste]:
            return f"Quitter avec arguments: {reste}"
        
        case ["creer", nom, *attributs]:
            return f"Création de '{nom}' avec {attributs}"
        
        case {"action": "supprimer", "id": id_utilisateur}:
            return f"Suppression de l'utilisateur {id_utilisateur}"
        
        case str() if commande.startswith("/"):
            return f"Commande slash: {commande}"
        
        case _:
            return "Commande inconnue"
```

---

## Références
- Python Data Model : https://docs.python.org/3/reference/datamodel.html
- Descriptor HowTo : https://docs.python.org/3/howto/descriptor.html
- PEP 557 (dataclasses) : https://peps.python.org/pep-0557/
- PEP 636 (pattern matching) : https://peps.python.org/pep-0636/