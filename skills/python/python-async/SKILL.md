---
name: python-async
description: Programmation asynchrone Python — asyncio, async/await, coroutines, Tasks, synchronisation, patterns concurrents, et bonnes pratiques. En français.
---

# Programmation Asynchrone Python — Guide Complet (Français)

Ce skill couvre la programmation asynchrone en Python avec `asyncio`, le modèle `async`/`await`, et les patterns concurrents modernes.

---

## 1. Concepts Fondamentaux

### Modèle de concurrence Python

```
Synchrone (bloquant) :   ──A── ──B── ──C──     (séquentiel)
Threads (préemptif)   :   ══A══
                            ══B══
                              ══C══               (parallèle, GIL)
Asynchrone (coopératif):  ──A──
                            ──B──
                              ──C──               (concurrent, 1 thread)
```

- **Coroutine** : fonction définie avec `async def`, peut être suspendue avec `await`
- **Event Loop** : boucle d'événements qui orchestre l'exécution des coroutines
- **Task** : coroutine planifiée pour exécution par l'event loop
- **Future** : résultat futur d'une opération asynchrone (abstraction bas niveau)

---

## 2. Bases async/await

```python
import asyncio


async def saluer(nom: str) -> str:
    """Coroutine simple : salue après un délai.
    
    Args:
        nom: Nom de la personne à saluer.
    
    Returns:
        Message de salutation.
    """
    await asyncio.sleep(1)  # Simule une opération I/O
    return f"Bonjour {nom}!"


# Exécution
async def principale() -> None:
    """Point d'entrée asynchrone."""
    message = await saluer("Alice")
    print(message)


# Lancement (Python 3.7+)
asyncio.run(principale())
```

### Exécution concurrente

```python
async def telecharger(url: str) -> str:
    """Simule le téléchargement d'une URL.
    
    Args:
        url: L'URL à télécharger.
    
    Returns:
        Contenu de la page.
    """
    print(f"→ Début {url}")
    await asyncio.sleep(1)
    print(f"← Fin {url}")
    return f"Contenu de {url}"


async def telecharger_tout(urls: list[str]) -> list[str]:
    """Télécharge plusieurs URLs en parallèle.
    
    Args:
        urls: Liste des URLs.
    
    Returns:
        Liste des contenus téléchargés.
    """
    taches = [telecharger(url) for url in urls]
    resultats = await asyncio.gather(*taches)
    return resultats
```

---

## 3. Tasks et Gestion des Tâches

### Créer et gérer des Tasks

```python
import asyncio
from typing import Any


async def tache_longue(id: int, duree: float) -> str:
    """Simule une tâche de durée variable.
    
    Args:
        id: Identifiant de la tâche.
        duree: Durée en secondes.
    
    Returns:
        Message de fin.
    """
    await asyncio.sleep(duree)
    return f"Tâche {id} terminée en {duree}s"


async def orchestrateur() -> None:
    """Orchestre plusieurs tâches avec gestion d'erreurs."""
    # Créer des tasks (démarrage immédiat)
    tache1 = asyncio.create_task(tache_longue(1, 2.0))
    tache2 = asyncio.create_task(tache_longue(2, 0.5))
    tache3 = asyncio.create_task(tache_longue(3, 1.0))
    
    # Attendre la première qui termine
    faites, en_attente = await asyncio.wait(
        [tache1, tache2, tache3],
        return_when=asyncio.FIRST_COMPLETED,
    )
    
    for tache in faites:
        print(tache.result())


# Timeout
async def avec_timeout() -> None:
    """Exécute une coroutine avec un délai maximal."""
    try:
        resultat = await asyncio.wait_for(
            tache_longue(1, 5.0),
            timeout=2.0,
        )
    except asyncio.TimeoutError:
        print("→ Timeout : la tâche a pris trop de temps")


# Annuler une tâche
async def avec_annulation() -> None:
    """Démontre l'annulation d'une tâche."""
    tache = asyncio.create_task(tache_longue(1, 10.0))
    await asyncio.sleep(0.1)
    tache.cancel()
    
    try:
        await tache
    except asyncio.CancelledError:
        print("→ Tâche annulée proprement")
```

---

## 4. Synchronisation

### Lock (mutex asynchrone)

```python
import asyncio
from typing import Any


class CompteurPartage:
    """Compteur thread-safe pour usage asynchrone.
    
    Attributes:
        _valeur: Valeur actuelle.
        _verrou: Verrou asynchrone.
    """
    
    def __init__(self) -> None:
        self._valeur = 0
        self._verrou = asyncio.Lock()
    
    async def incrementer(self) -> int:
        """Incrémente le compteur de façon atomique.
        
        Returns:
            La nouvelle valeur.
        """
        async with self._verrou:
            self._valeur += 1
            return self._valeur
    
    async def obtenir(self) -> int:
        """Lit la valeur actuelle.
        
        Returns:
            La valeur du compteur.
        """
        async with self._verrou:
            return self._valeur
```

### Semaphore (limiter la concurrence)

```python
import asyncio


async def telecharger_avec_limite(
    urls: list[str],
    max_concurrent: int = 5,
) -> list[str]:
    """Télécharge avec un nombre maximal de requêtes simultanées.
    
    Args:
        urls: Liste des URLs à télécharger.
        max_concurrent: Nombre maximal de téléchargements en parallèle.
    
    Returns:
        Liste des résultats.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def telecharger_limite(url: str) -> str:
        async with semaphore:
            return await telecharger(url)
    
    return await asyncio.gather(*[
        telecharger_limite(url) for url in urls
    ])
```

### Event et Condition

```python
import asyncio


async def producteur_consommateur() -> None:
    """Pattern producteur-consommateur avec asyncio.Event."""
    evenement = asyncio.Event()
    donnee: list[int] = []
    
    async def producteur() -> None:
        print("Producteur : préparation des données...")
        await asyncio.sleep(1)
        donnee.extend([1, 2, 3])
        evenement.set()  # Signaler que c'est prêt
        print("Producteur : données prêtes !")
    
    async def consommateur() -> None:
        print("Consommateur : en attente...")
        await evenement.wait()  # Bloquer jusqu'au signal
        print(f"Consommateur : reçu {donnee}")
    
    await asyncio.gather(producteur(), consommateur())
```

### Queue (file asynchrone)

```python
import asyncio


async def producteurs_consommateurs() -> None:
    """Plusieurs producteurs, plusieurs consommateurs."""
    queue: asyncio.Queue[int] = asyncio.Queue(maxsize=10)
    
    async def producteur(id: int) -> None:
        for i in range(5):
            await asyncio.sleep(0.5)
            await queue.put(i)
            print(f"P{id} → {i}")
    
    async def consommateur(id: int) -> None:
        while True:
            try:
                item = await asyncio.wait_for(
                    queue.get(),
                    timeout=3.0,
                )
                print(f"C{id} ← {item}")
                queue.task_done()
            except asyncio.TimeoutError:
                print(f"C{id} : timeout, arrêt")
                break
    
    producteurs = [producteur(i) for i in range(2)]
    consommateurs = [consommateur(i) for i in range(3)]
    
    await asyncio.gather(*producteurs, *consommateurs)
```

---

## 5. Fonctions Synchrones dans du Code Async

### run_in_executor

```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def calcul_bloquant(n: int) -> int:
    """Fonction synchrone intensive CPU.
    
    Args:
        n: Valeur d'entrée.
    
    Returns:
        Résultat du calcul.
    """
    time.sleep(2)  # Simule un calcul lourd
    return n * n


async def utiliser_executeur() -> None:
    """Délègue du travail bloquant à un pool de threads."""
    loop = asyncio.get_running_loop()
    
    # Via le pool par défaut (ThreadPoolExecutor)
    resultat = await loop.run_in_executor(
        None,  # Pool par défaut
        calcul_bloquant,
        42,
    )
    print(f"Résultat : {resultat}")
    
    # Via un pool dédié
    with ProcessPoolExecutor(max_workers=4) as pool:
        taches = [
            loop.run_in_executor(pool, calcul_bloquant, i)
            for i in range(10)
        ]
        resultats = await asyncio.gather(*taches)
        print(f"Tous les résultats : {resultats}")
```

### to_thread (Python 3.9+)

```python
import asyncio


async def exemple_to_thread() -> None:
    """Version simplifiée de run_in_executor."""
    resultat = await asyncio.to_thread(calcul_bloquant, 42)
    print(resultat)
```

---

## 6. Gestion des Groupes de Tâches

### TaskGroup (Python 3.11+)

```python
import asyncio


async def avec_taskgroup() -> None:
    """Gère un groupe de tâches avec annulation automatique."""
    try:
        async with asyncio.TaskGroup() as groupe:
            tache1 = groupe.create_task(tache_longue(1, 1.0))
            tache2 = groupe.create_task(tache_longue(2, 5.0))
            tache3 = groupe.create_task(tache_longue(3, 0.5))
            # Si une tâche échoue, toutes sont annulées
    except ExceptionGroup as eg:
        print(f"Erreurs : {eg.exceptions}")
```

### as_completed (traiter au fur et à mesure)

```python
import asyncio


async def traiter_au_fur_et_a_mesure(
    urls: list[str],
) -> list[str]:
    """Traite les résultats dès qu'ils sont disponibles.
    
    Args:
        urls: Liste des URLs.
    
    Returns:
        Résultats dans l'ordre d'arrivée.
    """
    resultats: list[str] = []
    taches = [telecharger(url) for url in urls]
    
    for coro in asyncio.as_completed(taches):
        resultat = await coro
        print(f"→ Reçu : {resultat}")
        resultats.append(resultat)
    
    return resultats
```

---

## 7. Clients/Serveurs Réseau avec asyncio

### Client TCP asynchrone

```python
import asyncio


async def client_tcp(
    host: str,
    port: int,
    message: str,
) -> str:
    """Client TCP asynchrone simple.
    
    Args:
        host: Adresse du serveur.
        port: Port du serveur.
        message: Message à envoyer.
    
    Returns:
        Réponse du serveur.
    """
    reader, writer = await asyncio.open_connection(host, port)
    
    writer.write(message.encode())
    await writer.drain()
    
    donnees = await reader.read(1024)
    reponse = donnees.decode()
    
    writer.close()
    await writer.wait_closed()
    
    return reponse
```

### Serveur TCP asynchrone

```python
import asyncio


async def gerer_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """Gère une connexion client.
    
    Args:
        reader: Flux de lecture.
        writer: Flux d'écriture.
    """
    addr = writer.get_extra_info('peername')
    print(f"→ Connexion de {addr}")
    
    while True:
        donnees = await reader.read(1024)
        if not donnees:
            break
        
        message = donnees.decode()
        print(f"Reçu de {addr}: {message}")
        
        reponse = f"Echo: {message}"
        writer.write(reponse.encode())
        await writer.drain()
    
    print(f"← Déconnexion de {addr}")
    writer.close()
    await writer.wait_closed()


async def serveur_tcp(host: str = "127.0.0.1", port: int = 8888) -> None:
    """Démarre un serveur TCP echo.
    
    Args:
        host: Adresse d'écoute.
        port: Port d'écoute.
    """
    serveur = await asyncio.start_server(
        gerer_client,
        host,
        port,
    )
    
    addr = serveur.sockets[0].getsockname()
    print(f"Serveur démarré sur {addr}")
    
    async with serveur:
        await serveur.serve_forever()
```

---

## 8. Patterns de Concurrence Avancés

### Pattern Fan-Out / Fan-In

```python
import asyncio
from typing import Any


async def fan_out_fan_in(
    elements: list[Any],
    traiter: callable,
    max_concurrent: int = 10,
) -> list[Any]:
    """Distribue le travail sur plusieurs workers et collecte les résultats.
    
    Args:
        elements: Éléments à traiter.
        traiter: Fonction de traitement asynchrone.
        max_concurrent: Nombre maximal de workers simultanés.
    
    Returns:
        Liste des résultats dans l'ordre original.
    """
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def worker(element: Any, index: int) -> tuple[int, Any]:
        async with semaphore:
            resultat = await traiter(element)
            return index, resultat
    
    taches = [
        worker(elem, i) for i, elem in enumerate(elements)
    ]
    
    resultats_tries = sorted(
        await asyncio.gather(*taches),
        key=lambda x: x[0],
    )
    
    return [r for _, r in resultats_tries]
```

### Pattern Retry avec Backoff Exponentiel

```python
import asyncio
from typing import TypeVar, Callable, Awaitable
import random

T = TypeVar("T")


async def retry_async(
    operation: Callable[[], Awaitable[T]],
    max_tentatives: int = 3,
    delai_base: float = 1.0,
    max_delai: float = 30.0,
) -> T:
    """Réessaie une opération asynchrone avec backoff exponentiel.
    
    Args:
        operation: L'opération asynchrone à réessayer.
        max_tentatives: Nombre maximal de tentatives.
        delai_base: Délai initial entre les tentatives (secondes).
        max_delai: Délai maximal entre les tentatives.
    
    Returns:
        Le résultat de l'opération.
    
    Raises:
        Exception: Si toutes les tentatives échouent.
    """
    derniere_exception: Exception | None = None
    
    for tentative in range(max_tentatives):
        try:
            return await operation()
        except Exception as e:
            derniere_exception = e
            if tentative == max_tentatives - 1:
                raise
            
            delai = min(
                delai_base * (2 ** tentative) + random.uniform(0, 1),
                max_delai,
            )
            print(f"Tentative {tentative + 1} échouée, "
                  f"nouvelle tentative dans {delai:.1f}s")
            await asyncio.sleep(delai)
    
    raise derniere_exception  # type: ignore
```

---

## 9. Clients HTTP Asynchrones

### Avec aiohttp

```python
# pip install aiohttp
import aiohttp
import asyncio


async def obtenir_json(
    session: aiohttp.ClientSession,
    url: str,
) -> dict:
    """Récupère du JSON depuis une API.
    
    Args:
        session: Session HTTP partagée.
        url: URL de l'endpoint.
    
    Returns:
        Données JSON parsées.
    """
    async with session.get(url) as reponse:
        reponse.raise_for_status()
        return await reponse.json()


async def requetes_par_lots(
    urls: list[str],
    taille_lot: int = 10,
) -> list[dict]:
    """Exécute des requêtes par lots pour limiter la charge.
    
    Args:
        urls: URLs à interroger.
        taille_lot: Nombre de requêtes simultanées par lot.
    
    Returns:
        Liste des résultats.
    """
    resultats: list[dict] = []
    
    async with aiohttp.ClientSession() as session:
        for i in range(0, len(urls), taille_lot):
            lot = urls[i:i + taille_lot]
            taches = [obtenir_json(session, url) for url in lot]
            resultats_lot = await asyncio.gather(
                *taches,
                return_exceptions=True,
            )
            resultats.extend([
                r for r in resultats_lot
                if not isinstance(r, Exception)
            ])
    
    return resultats
```

---

## 10. Débogage

```python
import asyncio
import logging

# Activer le mode debug asyncio
# PYTHONASYNCIODEBUG=1 python mon_script.py

# Logger toutes les coroutines lentes
logging.basicConfig(level=logging.DEBUG)
asyncio.get_event_loop().slow_callback_duration = 0.1  # 100ms


# Détecter les coroutines non attendues
import warnings

async def coroutine_oubliee() -> str:
    await asyncio.sleep(1)
    return "fait"


async def principale() -> None:
    tache = asyncio.create_task(coroutine_oubliee())
    # Oublié : await tache → avertissement en mode debug
```

---

## 11. Bonnes Pratiques

1. **Ne jamais bloquer la boucle d'événements** — pas de `time.sleep()`, utiliser `await asyncio.sleep()`
2. **Utiliser `asyncio.run()`** comme unique point d'entrée au niveau module
3. **Partager une `ClientSession` aiohttp**, ne pas en créer une par requête
4. **Toujours gérer `CancelledError`** dans les tâches longues pour un arrêt propre
5. **Limiter la concurrence** avec `Semaphore` pour ne pas surcharger les services externes
6. **Préférer `asyncio.gather()`** pour l'exécution parallèle de coroutines
7. **Utiliser `asyncio.as_completed()`** pour traiter les résultats dès qu'ils arrivent
8. **Timeout systématique** sur les opérations réseau (`asyncio.wait_for()`)
9. **Pas d'appels bloquants SQL** — utiliser des drivers asynchrones (asyncpg, aiomysql, aiosqlite)
10. **Tester avec `pytest-asyncio`** — marquer les tests `@pytest.mark.asyncio`

---

## Références
- Documentation asyncio : https://docs.python.org/3/library/asyncio.html
- aiohttp : https://docs.aiohttp.org/
- PEP 492 (async/await) : https://peps.python.org/pep-0492/