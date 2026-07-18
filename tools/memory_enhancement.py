#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Memory Enhancement Module - Recherche vectorielle dans les entrées mémoire.

Inspiré par mem0. Ajoute des capacités de recherche sémantique vectorielle
PAR-DESSUS le système de mémoire existant sans le remplacer.
Stocke un index embeddings dans ~/.helios/memory_index/.
"""

import json
import logging
import os
import math
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.helios_constants import get_helios_home

logger = logging.getLogger(__name__)

# Cache d'embeddings en mémoire
_EMBEDDING_CACHE: Dict[str, List[float]] = {}
_EMBEDDING_CACHE_TTL = 300  # Durée de vie de 5 minutes


# ── Embedding via OpenAI-compatible API ────────────────────────────────

def _get_api_config() -> tuple:
    """Récupère la configuration de l'API pour les embeddings.

    Returns:
        tuple: Un triplet (api_key, base_url, model) pour requêter l'API.
    """
    api_key = (os.environ.get("HELIOS_LLM_API_KEY")
               or os.environ.get("OPENTERAI_API_KEY")
               or os.environ.get("OPENAI_API_KEY")
               or "")
    base_url = (os.environ.get("HELIOS_LLM_BASE_URL")
                or os.environ.get("OPENAI_BASE_URL")
                or "https://api.openai.com/v1")
    model = os.environ.get("HELIOS_EMBEDDING_MODEL", "text-embedding-ada-002")
    return api_key, base_url.rstrip("/"), model


def _get_embedding(text: str) -> Optional[List[float]]:
    """Calcule l'embedding d'un texte via une API compatible OpenAI.

    Args:
        text: Texte dont on veut calculer le vecteur d'embedding.

    Returns:
        Optional[List[float]]: Le vecteur d'embedding sous forme de liste de floats,
        ou None si l'API n'est pas configurée ou en cas d'erreur.
    """
    # Vérification du cache
    cache_key = f"{hash(text)}"
    now = time.time()
    if cache_key in _EMBEDDING_CACHE:
        return _EMBEDDING_CACHE[cache_key]

    api_key, base_url, model = _get_api_config()
    if not api_key:
        return None

    try:
        import httpx
        resp = httpx.post(
            f"{base_url}/embeddings",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"input": text, "model": model},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        embedding = data["data"][0]["embedding"]

        # Mettre en cache
        _EMBEDDING_CACHE[cache_key] = embedding
        return embedding
    except Exception as e:
        logger.debug("Échec du calcul d'embedding (non bloquant) : %s", e)
        return None


# ── Cosine Similarity (sans numpy) ─────────────────────────────────────

def _cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calcule la similarité cosinus entre deux vecteurs.

    Args:
        a: Premier vecteur (liste de floats).
        b: Deuxième vecteur (liste de floats).

    Returns:
        float: Score de similarité cosinus compris entre -1.0 et 1.0.
    """
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


# ── Entry et Index ─────────────────────────────────────────────────────

@dataclass
class MemoryEntry:
    """Une entrée dans l'index mémoire vectoriel.

    Contient le texte d'origine, le namespace ciblé, la date de création,
    les tags associés, et éventuellement le vecteur d'embedding associé.
    """
    id: str
    content: str
    target: str  # "memory" ou "user"
    created_at: float
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None


class MemoryIndex:
    """Index vectoriel persistant pour les entrées mémoire.

    Stocké dans ~/.helios/memory_index/ sous forme de JSON.
    Ne remplace PAS le MemoryStore existant — le complète.
    """

    def __init__(self):
        """Initialise l'index mémoire avec ses verrous d'accès."""
        self._entries: Dict[str, MemoryEntry] = {}
        self._lock = threading.Lock()
        self._index_dir = get_helios_home() / "memory_index"
        self._index_dir.mkdir(parents=True, exist_ok=True)

    def _namespace_path(self, target: str) -> Path:
        """Résout le chemin d'accès au fichier JSON d'un namespace.

        Args:
            target: Le nom du namespace ("memory" ou "user").

        Returns:
            Path: Le chemin absolu vers le fichier JSON correspondant.
        """
        return self._index_dir / f"{target}.json"

    def load(self, target: str = "memory") -> None:
        """Charge l'index mémoire depuis le disque.

        Args:
            target: Le namespace à charger (par défaut "memory").
        """
        path = self._namespace_path(target)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            with self._lock:
                for item in data.get("entries", []):
                    entry = MemoryEntry(**item)
                    self._entries[entry.id] = entry
        except Exception as e:
            logger.warning("Erreur de chargement de l'index mémoire : %s", e)

    def save(self, target: str = "memory") -> None:
        """Sauvegarde l'index mémoire sur le disque.

        Args:
            target: Le namespace à sauvegarder (par défaut "memory").
        """
        with self._lock:
            entries = [asdict(e) for e in self._entries.values() if e.target == target]
        path = self._namespace_path(target)
        try:
            path.write_text(
                json.dumps({"namespace": target, "entries": entries}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("Erreur de sauvegarde de l'index mémoire : %s", e)

    def add(self, content: str, target: str = "memory", tags: Optional[List[str]] = None) -> str:
        """Ajoute une entrée à l'index avec son embedding.

        Args:
            content: Le texte de l'entrée mémoire.
            target: Le namespace cible ("memory" ou "user").
            tags: Liste optionnelle de tags associés.

        Returns:
            str: L'identifiant unique généré pour cette entrée.
        """
        entry_id = str(uuid.uuid4())[:8]
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            target=target,
            created_at=time.time(),
            tags=tags or [],
        )
        # Calculer l'embedding (non-bloquant si l'API n'est pas disponible)
        entry.embedding = _get_embedding(content)

        with self._lock:
            self._entries[entry_id] = entry
        self.save(target)
        return entry_id

    def search(self, query: str, target: str = "memory", top_k: int = 5) -> List[Dict[str, Any]]:
        """Recherche par similarité sémantique dans l'index.

        Utilise les embeddings quand disponibles, avec fallback substring.

        Args:
            query: La requête textuelle.
            target: Le namespace ciblé ("memory" ou "user").
            top_k: Nombre maximal de résultats (par défaut 5).

        Returns:
            List[Dict[str, Any]]: Liste des entrées pertinentes triées par score.
        """
        query_emb = _get_embedding(query)
        results: List[Dict[str, Any]] = []

        with self._lock:
            candidates = [e for e in self._entries.values() if e.target == target]

        if query_emb and any(e.embedding for e in candidates):
            # Recherche vectorielle
            scored = []
            for entry in candidates:
                if entry.embedding:
                    score = _cosine_similarity(query_emb, entry.embedding)
                    scored.append((score, entry))
            scored.sort(key=lambda x: x[0], reverse=True)

            for score, entry in scored[:top_k]:
                results.append({
                    "id": entry.id,
                    "content": entry.content,
                    "tags": entry.tags,
                    "score": round(score, 4),
                    "method": "vector",
                })

            # Si pas assez de résultats, compléter avec substring
            if len(results) < top_k:
                existing_ids = {r["id"] for r in results}
                for entry in candidates:
                    if entry.id in existing_ids:
                        continue
                    if query.lower() in entry.content.lower():
                        results.append({
                            "id": entry.id,
                            "content": entry.content,
                            "tags": entry.tags,
                            "score": 0.0,
                            "method": "substring",
                        })
                        if len(results) >= top_k:
                            break
        else:
            # Fallback: substring matching uniquement
            query_lower = query.lower()
            for entry in candidates:
                if query_lower in entry.content.lower():
                    results.append({
                        "id": entry.id,
                        "content": entry.content,
                        "tags": entry.tags,
                        "score": 0.0,
                        "method": "substring",
                    })
                    if len(results) >= top_k:
                        break

        return results

    def remove(self, entry_id: str) -> bool:
        """Supprime une entrée de l'index.

        Args:
            entry_id: L'identifiant de l'entrée à supprimer.

        Returns:
            bool: True si la suppression a eu lieu, False si l'ID n'a pas été trouvé.
        """
        with self._lock:
            if entry_id not in self._entries:
                return False
            target = self._entries[entry_id].target
            del self._entries[entry_id]
        self.save(target)
        return True

    def list_entries(self, target: str = "memory") -> List[Dict[str, Any]]:
        """Liste toutes les entrées d'un namespace.

        Args:
            target: Le namespace ("memory" ou "user").

        Returns:
            List[Dict[str, Any]]: La liste des métadonnées des entrées du namespace.
        """
        with self._lock:
            return [
                {"id": e.id, "content": e.content[:100], "tags": e.tags, "created_at": e.created_at}
                for e in self._entries.values() if e.target == target
            ]

    def get_tags(self, target: str = "memory") -> List[str]:
        """Retourne tous les tags uniques d'un namespace.

        Args:
            target: Le namespace ciblé ("memory" ou "user").

        Returns:
            List[str]: Liste triée des tags existants.
        """
        tags: set = set()
        with self._lock:
            for e in self._entries.values():
                if e.target == target:
                    tags.update(e.tags)
        return sorted(tags)


# ── Index global (singleton) ───────────────────────────────────────────

_index = MemoryIndex()
_index.load("memory")
_index.load("user")


# ── Fonctions d'intégration ────────────────────────────────────────────

def vector_search(query: str, target: str = "memory", top_k: int = 5) -> str:
    """Recherche sémantique dans les entrées mémoire.

    Combine recherche vectorielle (via embeddings) et substring matching.
    Retourne résultats triés par pertinence.

    Args:
        query: Texte de recherche.
        target: "memory" ou "user" (par défaut "memory").
        top_k: Nombre max de résultats (par défaut 5).

    Returns:
        str: Rapport JSON avec les résultats trouvés.
    """
    results = _index.search(query, target, top_k)
    return json.dumps({
        "query": query,
        "target": target,
        "results": results,
        "count": len(results),
    }, ensure_ascii=False, indent=2)


def memory_tag(tags: str = "", action: str = "list") -> str:
    """Gère les tags dans l'index mémoire.

    Args:
        tags: Tags à ajouter (séparés par des virgules, inutilisé pour 'list').
        action: Action à effectuer ('list' uniquement).

    Returns:
        str: Chaîne JSON contenant la liste des tags disponibles.
    """
    if action == "list":
        memory_tags = _index.get_tags("memory")
        user_tags = _index.get_tags("user")
        return json.dumps({
            "memory_tags": memory_tags,
            "user_tags": user_tags,
        }, ensure_ascii=False, indent=2)

    return json.dumps({"error": f"Action inconnue: {action}. Utilisez 'list'."})


# ── Registration ──────────────────────────────────────────────────────

from tools.registry import registry


def _check_requirements() -> bool:
    """Vérifie si httpx est disponible pour les requêtes réseau.

    Returns:
        bool: True si httpx est installé, False sinon.
    """
    try:
        import httpx
        return True
    except ImportError:
        return False


registry.register(
    name="memory_search",
    toolset="core",
    schema={
        "name": "memory_search",
        "description": "Recherche sémantique vectorielle dans les entrées mémoire. "
                       "Combine embeddings et substring matching. Plus pertinent que "
                       "memory(action=read) pour retrouver une information spécifique.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Texte à rechercher"},
                "target": {
                    "type": "string",
                    "enum": ["memory", "user"],
                    "description": "Namespace: memory (notes agent) ou user (profil utilisateur)"
                },
                "top_k": {"type": "integer", "description": "Nombre max de résultats", "default": 5}
            },
            "required": ["query"]
        }
    },
    handler=lambda a, **kw: vector_search(
        a.get("query", ""), a.get("target", "memory"), a.get("top_k", 5), **kw
    ),
    check_fn=_check_requirements,
    requires_env=[],
    description="Recherche sémantique vectorielle dans la mémoire",
    emoji="🧠",
)

registry.register(
    name="memory_tag",
    toolset="core",
    schema={
        "name": "memory_tag",
        "description": "Liste les tags disponibles dans l'index mémoire vectoriel. "
                       "Les tags sont des mots-clés associés aux entrées mémoire.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list"],
                    "description": "Action à effectuer (seulement 'list' pour l'instant)"
                }
            },
            "required": ["action"]
        }
    },
    handler=lambda a, **kw: memory_tag(a.get("tags", ""), a.get("action", "list"), **kw),
    check_fn=_check_requirements,
    requires_env=[],
    description="Gestion des tags de l'index mémoire vectoriel",
    emoji="🏷️",
)