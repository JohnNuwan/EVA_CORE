---
name: python-poo
description: Programmation Orientée Objet en Python — classes, héritage, MRO, ABC, interfaces, composition vs héritage, encapsulation, SOLID. En français.
---

# Programmation Orientée Objet Python — Guide Complet (Français)

Ce skill couvre la POO en Python : classes, héritage, MRO, classes abstraites, protocoles, design patterns et principes SOLID.

---

## 1. Classes et Objets

### Structure de base

```python
from typing import ClassVar


class CompteBancaire:
    """Représente un compte bancaire avec dépôt et retrait.
    
    Attributes:
        titulaire: Nom du titulaire du compte.
        _solde: Solde actuel (privé, accès via propriété).
        _numero: Numéro unique du compte.
    """
    
    # Attribut de classe (partagé entre toutes les instances)
    _compteur: ClassVar[int] = 0
    TAUX_INTERET: ClassVar[float] = 0.02
    
    def __init__(self, titulaire: str, depot_initial: float = 0.0) -> None:
        """Initialise un nouveau compte.
        
        Args:
            titulaire: Nom du titulaire.
            depot_initial: Montant du dépôt initial.
        
        Raises:
            ValueError: Si le dépôt initial est négatif.
        """
        if depot_initial < 0:
            raise ValueError("Le dépôt initial ne peut pas être négatif")
        
        CompteBancaire._compteur += 1
        self.titulaire = titulaire
        self._solde = depot_initial
        self._numero = CompteBancaire._compteur
    
    # Méthodes d'instance
    def deposer(self, montant: float) -> float:
        """Dépose de l'argent sur le compte.
        
        Args:
            montant: Montant à déposer (doit être positif).
        
        Returns:
            Le nouveau solde.
        """
        if montant <= 0:
            raise ValueError("Le montant doit être positif")
        self._solde += montant
        return self._solde
    
    def retirer(self, montant: float) -> float:
        """Retire de l'argent du compte.
        
        Args:
            montant: Montant à retirer.
        
        Returns:
            Le nouveau solde.
        
        Raises:
            ValueError: Si le solde est insuffisant.
        """
        if montant > self._solde:
            raise ValueError("Solde insuffisant")
        self._solde -= montant
        return self._solde
    
    # Méthodes spéciales (dunder)
    def __str__(self) -> str:
        return f"Compte #{self._numero} de {self.titulaire}"
    
    def __repr__(self) -> str:
        return f"CompteBancaire('{self.titulaire}', {self._solde})"
    
    def __eq__(self, autre: object) -> bool:
        if not isinstance(autre, CompteBancaire):
            return NotImplemented
        return self._numero == autre._numero
    
    # Méthodes de classe
    @classmethod
    def depuis_csv(cls, ligne: str) -> "CompteBancaire":
        """Crée un compte depuis une ligne CSV.
        
        Args:
            ligne: Chaîne au format 'nom,montant'.
        
        Returns:
            Une nouvelle instance de CompteBancaire.
        """
        nom, montant = ligne.split(",")
        return cls(nom.strip(), float(montant))
    
    # Méthodes statiques
    @staticmethod
    def formater_montant(montant: float) -> str:
        """Formate un montant en euros.
        
        Args:
            montant: Le montant à formater.
        
        Returns:
            Chaîne formatée.
        """
        return f"{montant:,.2f} €"
    
    # Propriétés
    @property
    def solde(self) -> float:
        """float: Le solde actuel du compte."""
        return self._solde
    
    @property
    def numero(self) -> int:
        """int: Le numéro unique du compte (lecture seule)."""
        return self._numero
```

---

## 2. Héritage

### Héritage simple

```python
class CompteEpargne(CompteBancaire):
    """Compte d'épargne avec taux d'intérêt personnalisé.
    
    Attributes:
        taux_interet: Taux d'intérêt annuel du compte.
        _retraits_mensuels: Nombre de retraits ce mois-ci.
    """
    
    MAX_RETRAITS_MENSUELS: ClassVar[int] = 3
    
    def __init__(
        self,
        titulaire: str,
        depot_initial: float = 0.0,
        taux_interet: float = 0.02,
    ) -> None:
        """Initialise un compte épargne.
        
        Args:
            titulaire: Nom du titulaire.
            depot_initial: Dépôt initial.
            taux_interet: Taux d'intérêt annuel.
        """
        super().__init__(titulaire, depot_initial)
        self.taux_interet = taux_interet
        self._retraits_mensuels = 0
    
    def retirer(self, montant: float) -> float:
        """Retire de l'argent, limité à MAX_RETRAITS_MENSUELS.
        
        Args:
            montant: Montant à retirer.
        
        Returns:
            Le nouveau solde.
        
        Raises:
            ValueError: Si la limite de retraits est atteinte.
        """
        if self._retraits_mensuels >= self.MAX_RETRAITS_MENSUELS:
            raise ValueError("Limite de retraits mensuels atteinte")
        self._retraits_mensuels += 1
        return super().retirer(montant)
    
    def appliquer_interets(self) -> float:
        """Applique les intérêts mensuels au solde.
        
        Returns:
            Le montant des intérêts ajoutés.
        """
        interets = self._solde * (self.taux_interet / 12)
        self._solde += interets
        return interets
```

### Héritage multiple et MRO

```python
class Journalisable:
    """Mixin qui ajoute des capacités de journalisation."""
    
    def journaliser(self, message: str) -> None:
        """Enregistre un message dans le journal.
        
        Args:
            message: Message à journaliser.
        """
        print(f"[{self.__class__.__name__}] {message}")


class Exportable:
    """Mixin qui ajoute des capacités d'export."""
    
    def exporter(self) -> dict[str, Any]:
        """Exporte l'objet en dictionnaire.
        
        Returns:
            Dictionnaire représentant l'objet.
        """
        return {
            k: v for k, v in self.__dict__.items()
            if not k.startswith("_")
        }


class ComptePremium(CompteEpargne, Journalisable, Exportable):
    """Compte premium avec journalisation et export.
    
    MRO (Method Resolution Order) :
    ComptePremium → CompteEpargne → Journalisable → Exportable
    → CompteBancaire → object
    """
    
    def __init__(
        self,
        titulaire: str,
        depot_initial: float = 0.0,
        conseiller: str = "",
    ) -> None:
        super().__init__(titulaire, depot_initial, taux_interet=0.03)
        self.conseiller = conseiller
        self.journaliser("Compte premium créé")


# Voir le MRO
print(ComptePremium.__mro__)
# ComptePremium, CompteEpargne, Journalisable, Exportable,
# CompteBancaire, object
```

---

## 3. Classes Abstraites (ABC)

```python
from abc import ABC, abstractmethod, abstractproperty


class Forme(ABC):
    """Classe abstraite représentant une forme géométrique.
    
    Toute sous-classe doit implémenter aire() et perimetre().
    """
    
    @abstractmethod
    def aire(self) -> float:
        """Calcule l'aire de la forme.
        
        Returns:
            L'aire en unités carrées.
        """
        ...
    
    @abstractmethod
    def perimetre(self) -> float:
        """Calcule le périmètre de la forme.
        
        Returns:
            Le périmètre en unités.
        """
        ...
    
    def rapport_aire_perimetre(self) -> float:
        """Calcule le rapport aire/périmètre (méthode concrète).
        
        Returns:
            Le rapport, ou infini si le périmètre est nul.
        """
        p = self.perimetre()
        return self.aire() / p if p != 0 else float("inf")


class Cercle(Forme):
    """Cercle défini par son rayon.
    
    Attributes:
        rayon: Rayon du cercle.
    """
    
    def __init__(self, rayon: float) -> None:
        """Initialise le cercle.
        
        Args:
            rayon: Rayon du cercle (positif).
        """
        self.rayon = rayon
    
    def aire(self) -> float:
        import math
        return math.pi * self.rayon ** 2
    
    def perimetre(self) -> float:
        import math
        return 2 * math.pi * self.rayon


class Rectangle(Forme):
    """Rectangle défini par sa largeur et hauteur.
    
    Attributes:
        largeur: Largeur du rectangle.
        hauteur: Hauteur du rectangle.
    """
    
    def __init__(self, largeur: float, hauteur: float) -> None:
        self.largeur = largeur
        self.hauteur = hauteur
    
    def aire(self) -> float:
        return self.largeur * self.hauteur
    
    def perimetre(self) -> float:
        return 2 * (self.largeur + self.hauteur)
    
    @property
    def est_carre(self) -> bool:
        """bool: True si le rectangle est un carré."""
        return self.largeur == self.hauteur
```

---

## 4. Composition vs Héritage

```python
# ❌ Mauvais : héritage forcé
class PileHeritee(list):
    """Pile qui hérite de list (mauvaise idée)."""
    
    def empiler(self, element: Any) -> None:
        self.append(element)
    
    def depiler(self) -> Any:
        return self.pop()


# ✅ Bon : composition
class Pile:
    """Pile FIFO par composition d'une liste."""
    
    def __init__(self) -> None:
        self._elements: list[Any] = []
    
    def empiler(self, element: Any) -> None:
        """Ajoute un élément au sommet de la pile."""
        self._elements.append(element)
    
    def depiler(self) -> Any:
        """Retire et retourne l'élément au sommet.
        
        Returns:
            L'élément retiré.
        
        Raises:
            IndexError: Si la pile est vide.
        """
        if not self._elements:
            raise IndexError("Pile vide")
        return self._elements.pop()
    
    def __len__(self) -> int:
        return len(self._elements)
    
    def __bool__(self) -> bool:
        return bool(self._elements)


# ✅ Bon : composition avec stratégie
class StrategieTaxe(ABC):
    """Stratégie de calcul de taxe."""
    
    @abstractmethod
    def calculer(self, montant: float) -> float:
        ...


class TaxeFrance(StrategieTaxe):
    def calculer(self, montant: float) -> float:
        return montant * 0.20


class TaxeBelgique(StrategieTaxe):
    def calculer(self, montant: float) -> float:
        return montant * 0.21


class Facture:
    """Facture avec stratégie de taxe composée."""
    
    def __init__(
        self,
        articles: list[dict[str, float]],
        strategie_taxe: StrategieTaxe,
    ) -> None:
        self.articles = articles
        self.strategie_taxe = strategie_taxe
    
    def total_ttc(self) -> float:
        """Calcule le total TTC."""
        total_ht = sum(a["prix"] for a in self.articles)
        return total_ht + self.strategie_taxe.calculer(total_ht)
```

---

## 5. Encapsulation en Python

```python
class AccesDonnees:
    """Démontre les niveaux d'encapsulation en Python."""
    
    def __init__(self) -> None:
        self.publique = "Accessible partout"
        self._protege = "Accessible, convention interne"
        self.__prive = "Name mangling : _AccesDonnees__prive"
    
    def methode_publique(self) -> str:
        return "Appelable depuis l'extérieur"
    
    def _methode_protegee(self) -> str:
        return "Usage interne, mais techniquement accessible"
    
    def __methode_privee(self) -> str:
        """Vraiment privée via name mangling, 
        accessible seulement depuis la classe."""
        return "Name mangling"


# Name mangling en action
obj = AccesDonnees()
# obj.__prive            → AttributeError
# obj._AccesDonnees__prive  → Fonctionne mais ne le faites pas !
```

---

## 6. Principes SOLID en Python

### S — Single Responsibility (Responsabilité Unique)
```python
# ❌ Mauvaise : une classe fait tout
class RapportUtilisateur:
    def generer(self, user): ...    # Génération du rapport
    def sauvegarder(self, rapport): ...  # Persistence
    def envoyer_email(self, to): ...   # Envoi email

# ✅ Bonne : responsabilités séparées
class GenerateurRapport:
    def generer(self, user) -> str: ...

class StockageRapport:
    def sauvegarder(self, rapport: str) -> None: ...

class EnvoyeurEmail:
    def envoyer(self, destinataire: str, contenu: str) -> None: ...
```

### O — Open/Closed (Ouvert à l'extension, Fermé à la modification)
```python
class CalculateurRemise:
    def calculer(self, commande, type_client: str) -> float:
        if type_client == "standard":
            return commande.total * 0.05
        elif type_client == "premium":
            return commande.total * 0.10
        elif type_client == "vip":
            return commande.total * 0.20
        # ❌ Ajouter un type = modifier la classe


class StrategieRemise(ABC):
    @abstractmethod
    def appliquer(self, total: float) -> float: ...

class RemiseStandard(StrategieRemise):
    def appliquer(self, total: float) -> float:
        return total * 0.05

class RemiseVIP(StrategieRemise):
    def appliquer(self, total: float) -> float:
        return total * 0.20

# ✅ Ajouter un nouveau type = nouvelle classe, pas de modification
```

### L — Liskov Substitution
```python
# ❌ Violation : Carré n'est pas un Rectangle substituable
class Rectangle:
    def __init__(self, largeur: float, hauteur: float):
        self.largeur = largeur
        self.hauteur = hauteur
    
    def definir_largeur(self, l: float) -> None:
        self.largeur = l
    
    def definir_hauteur(self, h: float) -> None:
        self.hauteur = h


class Carre(Rectangle):
    def definir_largeur(self, l: float) -> None:
        self.largeur = l
        self.hauteur = l  # Violation : modifie hauteur !
    
    def definir_hauteur(self, h: float) -> None:
        self.hauteur = h
        self.largeur = h  # Violation : modifie largeur !
```

### I — Interface Segregation
```python
# ❌ Interface trop grosse
class Imprimante(ABC):
    @abstractmethod
    def imprimer(self, doc): ...
    @abstractmethod
    def scanner(self, doc): ...
    @abstractmethod
    def faxer(self, doc): ...

# ✅ Interfaces séparées
class Imprimable(ABC):
    @abstractmethod
    def imprimer(self, doc): ...

class Scannable(ABC):
    @abstractmethod
    def scanner(self, doc): ...

class Faxable(ABC):
    @abstractmethod
    def faxer(self, doc): ...
```

### D — Dependency Inversion
```python
# ❌ Dépendance directe au concret
class ServiceNotification:
    def __init__(self):
        self.smtp = ServeurSMTP()  # Dépendance concrète


# ✅ Dépendance vers l'abstraction
class ExpediteurMessage(ABC):
    @abstractmethod
    def envoyer(self, message: str, destinataire: str) -> None: ...

class ExpediteurSMTP(ExpediteurMessage):
    def envoyer(self, message: str, destinataire: str) -> None: ...

class ExpediteurSMS(ExpediteurMessage):
    def envoyer(self, message: str, destinataire: str) -> None: ...

class ServiceNotification:
    def __init__(self, expediteur: ExpediteurMessage) -> None:
        self.expediteur = expediteur  # Injection de dépendance
```

---

## 7. Design Patterns Courants

### Singleton
```python
class ConfigSingleton:
    _instance: "ConfigSingleton | None" = None
    
    def __new__(cls) -> "ConfigSingleton":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialiser()
        return cls._instance
    
    def _initialiser(self) -> None:
        self.debug = False
```

### Factory
```python
class FabriqueForme:
    @staticmethod
    def creer(type_forme: str, **kwargs) -> Forme:
        if type_forme == "cercle":
            return Cercle(rayon=kwargs["rayon"])
        elif type_forme == "rectangle":
            return Rectangle(kwargs["largeur"], kwargs["hauteur"])
        raise ValueError(f"Forme inconnue : {type_forme}")
```

### Observer
```python
class Observateur(ABC):
    @abstractmethod
    def notifier(self, evenement: str, donnees: Any) -> None: ...

class Sujet:
    def __init__(self) -> None:
        self._observateurs: list[Observateur] = []
    
    def attacher(self, obs: Observateur) -> None:
        self._observateurs.append(obs)
    
    def notifier(self, evenement: str, donnees: Any) -> None:
        for obs in self._observateurs:
            obs.notifier(evenement, donnees)
```

---

## Références
- Python Classes : https://docs.python.org/3/tutorial/classes.html
- SOLID Python : https://realpython.com/solid-principles-python/
- Design Patterns : https://refactoring.guru/design-patterns/python