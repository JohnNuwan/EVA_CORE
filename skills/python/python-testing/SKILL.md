---
name: python-testing
description: Guide complet des tests Python avec pytest — fixtures, paramétrage, mocks, couverture, TDD, et bonnes pratiques. En français, compatible avec pytest 7+.
---

# Tests Python avec Pytest — Guide Complet (Français)

Ce skill couvre toutes les pratiques de test Python avec le framework pytest. À charger pour toute tâche d'écriture, de débogage, ou de validation de code.

---

## 1. Installation et Configuration

```bash
# Installation
pip install pytest pytest-cov pytest-mock pytest-xdist

# Configuration pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
]
```

---

## 2. Structure des Tests

### Organisation des fichiers

```
projet/
├── src/
│   ├── __init__.py
│   ├── calculatrice.py
│   └── service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures partagées
│   ├── test_calculatrice.py
│   ├── test_service.py
│   └── integration/
│       ├── __init__.py
│       └── test_api.py
├── pyproject.toml
```

### Fonction de test simple

```python
# tests/test_calculatrice.py
"""Tests pour le module calculatrice."""

from src.calculatrice import additionner, diviser


def test_additionner_nombres_positifs() -> None:
    """Vérifie l'addition de deux nombres positifs."""
    resultat = additionner(2, 3)
    assert resultat == 5


def test_additionner_avec_negatifs() -> None:
    """Vérifie l'addition avec des nombres négatifs."""
    assert additionner(-1, 1) == 0
    assert additionner(-5, -3) == -8
```

---

## 3. Fixtures

### Fixture de base

```python
# tests/conftest.py
"""Fixtures partagées pour tous les tests."""

import pytest
from pathlib import Path
from typing import Iterator, Any


@pytest.fixture
def donnees_test() -> list[dict[str, Any]]:
    """Fournit un jeu de données standard pour les tests.
    
    Returns:
        Une liste de dictionnaires représentant des utilisateurs.
    """
    return [
        {"id": 1, "nom": "Alice", "age": 30},
        {"id": 2, "nom": "Bob", "age": 25},
        {"id": 3, "nom": "Charlie", "age": 35},
    ]


@pytest.fixture
def fichier_temp(tmp_path: Path) -> Path:
    """Crée un fichier temporaire pour les tests.
    
    Args:
        tmp_path: Fixture pytest intégrée pour un répertoire temporaire.
    
    Returns:
        Chemin du fichier temporaire créé.
    """
    fichier = tmp_path / "test.json"
    fichier.write_text('{"cle": "valeur"}')
    return fichier
```

### Fixture avec setup/teardown

```python
import pytest
from typing import Iterator


@pytest.fixture
def connexion_bd() -> Iterator[dict[str, Any]]:
    """Ouvre une connexion à la base de test et la ferme après.
    
    Yields:
        Un objet de connexion simulé.
    """
    # Setup : avant le test
    connexion = {"ouverte": True, "tables": []}
    print("\n→ Connexion BD ouverte")
    
    yield connexion  # Le test s'exécute ici
    
    # Teardown : après le test
    connexion["ouverte"] = False
    print("→ Connexion BD fermée")


@pytest.fixture
async def client_http() -> Iterator[dict]:
    """Fixture asynchrone pour un client HTTP de test."""
    # Setup
    client = {"base_url": "http://test.local"}
    yield client
    # Teardown
    await client.get("fermer")  # fictif
```

### Fixtures paramétrées

```python
@pytest.fixture(params=["json", "yaml", "toml"])
def format_fichier(request) -> str:
    """Teste le même comportement sur différents formats de fichier.
    
    Args:
        request: Objet pytest contenant le paramètre courant.
    
    Returns:
        Le format de fichier à tester.
    """
    return request.param


def test_lecture_par_format(
    format_fichier: str,
    fichier_temp: Path,
) -> None:
    """Vérifie la lecture pour chaque format supporté."""
    lecteur = creer_lecteur(format_fichier)
    assert lecteur.peut_lire(fichier_temp)
```

---

## 4. Paramétrage de Tests

### @pytest.mark.parametrize

```python
import pytest


@pytest.mark.parametrize(
    "a, b, attendu",
    [
        (2, 3, 5),
        (-1, 1, 0),
        (0, 0, 0),
        (100, 200, 300),
    ],
    ids=["positifs", "negatif_positif", "zeros", "grands_nombres"],
)
def test_additionner(a: int, b: int, attendu: int) -> None:
    """Vérifie l'addition avec plusieurs jeux de données.
    
    Args:
        a: Premier opérande.
        b: Deuxième opérande.
        attendu: Résultat attendu.
    """
    assert additionner(a, b) == attendu


# Paramétrage combiné
@pytest.mark.parametrize("operation", [additionner, multiplier])
@pytest.mark.parametrize("x", [0, 1, 5])
def test_element_neutre(operation, x: int) -> None:
    """Vérifie l'élément neutre pour différentes opérations."""
    assert operation(x, 0) == x if operation == additionner else 0
```

---

## 5. Exceptions

```python
import pytest


def test_diviser_par_zero() -> None:
    """Vérifie que la division par zéro lève ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        diviser(10, 0)


def test_diviser_par_zero_message() -> None:
    """Vérifie le message d'erreur de la division par zéro."""
    with pytest.raises(ZeroDivisionError, match="division par zéro"):
        diviser(10, 0)


def test_diviser_par_zero_detail() -> None:
    """Vérifie les détails de l'exception levée."""
    with pytest.raises(ZeroDivisionError) as exc_info:
        diviser(10, 0)
    
    assert exc_info.type is ZeroDivisionError
    assert "zéro" in str(exc_info.value)
```

---

## 6. Mocks et Monkeypatch

### Mock avec pytest-mock

```python
import pytest
from unittest.mock import Mock, MagicMock, patch


def test_appel_api(mocker) -> None:
    """Vérifie le comportement avec une API mockée.
    
    Args:
        mocker: Fixture pytest-mock.
    """
    # Mocker une fonction
    mock_get = mocker.patch("src.service.requests.get")
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"status": "ok"}
    
    from src.service import verifier_statut
    
    resultat = verifier_statut()
    assert resultat == "ok"
    mock_get.assert_called_once()


def test_appel_api_erreur(mocker) -> None:
    """Vérifie la gestion d'une erreur API."""
    mocker.patch(
        "src.service.requests.get",
        side_effect=ConnectionError("Serveur injoignable"),
    )
    
    from src.service import verifier_statut
    
    with pytest.raises(ConnectionError):
        verifier_statut()
```

### Mock d'attributs et propriétés

```python
def test_mock_propriete(mocker) -> None:
    """Mock une propriété d'un objet."""
    mock_obj = mocker.MagicMock()
    type(mock_obj).temperature = mocker.PropertyMock(return_value=42.0)
    
    assert mock_obj.temperature == 42.0


def test_mock_asynchrone(mocker) -> None:
    """Mock une fonction asynchrone."""
    mock_async = mocker.AsyncMock(return_value={"data": "ok"})
    
    # Usage dans un test async
    # resultat = await mock_async()
```

### Monkeypatch (modification directe)

```python
def test_variable_environnement(monkeypatch) -> None:
    """Test avec variable d'environnement modifiée."""
    monkeypatch.setenv("API_KEY", "test-key-123")
    
    from src.config import charger_api_key
    
    assert charger_api_key() == "test-key-123"


def test_heure_simulee(monkeypatch) -> None:
    """Test avec une date/heure fixe."""
    from datetime import datetime
    
    date_fixe = datetime(2024, 1, 1, 12, 0, 0)
    
    class DatetimeMock:
        @classmethod
        def now(cls):
            return date_fixe
    
    monkeypatch.setattr("src.service.datetime", DatetimeMock)
```

---

## 7. Tests de Snapshots

```python
def test_formatage_sortie(snapshot) -> None:
    """Vérifie que la sortie formatée ne change pas.
    
    Utilise pytest-snapshot (pip install pytest-snapshot).
    """
    from src.rapport import generer_rapport
    
    rapport = generer_rapport([1, 2, 3])
    assert rapport == snapshot()
```

---

## 8. Marqueurs Personnalisés

```python
# pyproject.toml
# [tool.pytest.ini_options]
# markers = [
#     "lent: tests qui prennent plus d'une seconde",
#     "integration: tests qui nécessitent des services externes",
#     "unitaire: tests unitaires rapides",
# ]

@pytest.mark.lent
def test_calcul_intensif() -> None:
    """Test de performance sur un gros volume de données."""
    ...

@pytest.mark.integration
def test_connexion_base_donnees() -> None:
    """Test d'intégration avec une vraie base de données."""
    ...

# Exécution sélective :
# pytest -m "not lent"          # sauf les lents
# pytest -m "unitaire"          # seulement les unitaires
```

---

## 9. Couverture de Code

```bash
# Lancer avec couverture
pytest --cov=src --cov-report=html --cov-report=term

# Rapport minimal : 90% de couverture
pytest --cov=src --cov-fail-under=90
```

```python
# Ignorer certaines lignes
def fonction_complexe() -> str:
    if condition_rare:  # pragma: no cover
        return "cas_impossible_en_test"
    return "normal"
```

---

## 10. Tests Paramétrés depuis un Fichier

```python
import json
from pathlib import Path


def charger_cas_test(fichier: str) -> list[tuple]:
    """Charge les cas de test depuis un fichier JSON.
    
    Args:
        fichier: Nom du fichier JSON.
    
    Returns:
        Liste de tuples (entrée, attendu).
    """
    chemin = Path(__file__).parent / "fixtures" / fichier
    with open(chemin) as f:
        donnees = json.load(f)
    return [(cas["entree"], cas["attendu"]) for cas in donnees]


@pytest.mark.parametrize(
    "entree, attendu",
    charger_cas_test("cas_addition.json"),
)
def test_addition_depuis_fichier(entree: list[int], attendu: int) -> None:
    assert sum(entree) == attendu
```

---

## 11. Assertions Utiles

```python
# Égalité
assert resultat == 42
assert resultat != 0

# Contenu
assert "erreur" in message
assert "succès" not in message
assert texte.startswith("Début")
assert texte.endswith("Fin")

# Types
assert isinstance(valeur, int)
assert type(valeur) is dict

# Conteneurs
assert len(liste) == 3
assert 5 in ensemble
assert "cle" in dictionnaire

# Approximation (flottants)
assert resultat == pytest.approx(3.14, rel=0.01)

# Avertissements
with pytest.warns(DeprecationWarning):
    fonction_depreciee()

# Logs (avec pytest-catchlog ou caplog)
def test_journalisation(caplog) -> None:
    fonction_qui_log()
    assert "Traitement terminé" in caplog.text
```

---

## 12. Bonnes Pratiques TDD (Test-Driven Development)

1. **RED** : Écrire un test qui échoue (la fonctionnalité n'existe pas)
2. **GREEN** : Écrire le minimum de code pour que le test passe
3. **REFACTOR** : Améliorer le code sans casser les tests

### Convention de nommage AAA (Arrange, Act, Assert)

```python
def test_envoi_email() -> None:
    """Vérifie l'envoi d'un email de bienvenue."""
    # Arrange (préparer)
    utilisateur = {"email": "alice@exemple.com", "nom": "Alice"}
    mock_smtp = Mock()
    
    # Act (agir)
    envoyer_email_bienvenue(utilisateur, smtp=mock_smtp)
    
    # Assert (vérifier)
    mock_smtp.envoyer.assert_called_once()
    appel = mock_smtp.envoyer.call_args[1]
    assert "Bienvenue Alice" in appel["sujet"]
```

---

## 13. Tests Asynchrones

```python
import pytest
import asyncio


@pytest.mark.asyncio
async def test_fonction_async() -> None:
    """Teste une coroutine directement."""
    from src.async_service import obtenir_donnees
    
    resultat = await obtenir_donnees("endpoint")
    assert resultat["status"] == "ok"


@pytest.mark.asyncio
async def test_timeout_async() -> None:
    """Vérifie qu'une opération async respecte le timeout."""
    from src.async_service import operation_lente
    
    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(operation_lente(), timeout=0.1)
```

---

## Commandes Utiles

```bash
pytest                          # Tous les tests
pytest -v                       # Mode verbeux
pytest -x                       # Arrêter à la première erreur
pytest -k "addition"            # Filtrer par nom
pytest --lf                     # Rejouer les derniers échecs
pytest --ff                     # Échecs d'abord, puis le reste
pytest -n auto                  # Parallèle (pytest-xdist)
pytest --durations=10           # Top 10 des tests les plus lents
pytest --cov=src --cov-report=html  # Couverture HTML
```