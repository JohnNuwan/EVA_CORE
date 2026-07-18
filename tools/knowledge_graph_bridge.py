#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Knowledge Graph Bridge - Transformation de codebase en graphe de connaissance.

Inspiré par Graphify. Transforme n'importe quel dossier de code, docs
ou fichiers plats en un graphe de connaissance consultable par l'agent.
Stocke le graphe en JSON dans ~/.helios/knowledge_graphs/.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ── Extractions de relations ───────────────────────────────────────────

def _extract_file_relations(file_path: Path, root: Path) -> List[Dict[str, str]]:
    """Extrait les relations d'un fichier avec son environnement.

    Les relations incluent l'extension de fichier, la catégorie de taille,
    les imports et les définitions de symboles détectées.

    Args:
        file_path: Chemin d'accès absolu ou relatif du fichier à analyser.
        root: Répertoire racine du projet pour calculer les chemins relatifs.

    Returns:
        List[Dict[str, str]]: Liste de dictionnaires représentant les arcs de relation.
    """
    relations = []
    rel_path = str(file_path.relative_to(root))
    ext = file_path.suffix.lower()
    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return relations

    # Relation: extension de fichier
    relations.append({
        "type": "has_extension",
        "source": rel_path,
        "target": ext,
    })

    # Relation: catégorie de taille
    size = len(source)
    if size < 1000:
        relations.append({"type": "size_category", "source": rel_path, "target": "small"})
    elif size < 10000:
        relations.append({"type": "size_category", "source": rel_path, "target": "medium"})
    else:
        relations.append({"type": "size_category", "source": rel_path, "target": "large"})

    # Relations spécifiques par type de fichier
    if ext == ".py":
        for m in re.finditer(r'^\s*from\s+(\S+)\s+import\s+(\S+)', source, re.MULTILINE):
            relations.append({
                "type": "python_import",
                "source": rel_path,
                "target": m.group(1),
                "detail": m.group(2),
            })
        for m in re.finditer(r'class\s+(\w+)', source):
            relations.append({
                "type": "defines_class",
                "source": rel_path,
                "target": m.group(1),
            })
        for m in re.finditer(r'def\s+(\w+)', source):
            relations.append({
                "type": "defines_function",
                "source": rel_path,
                "target": m.group(1),
            })

    elif ext in (".st", ".scl", ".awl"):
        for m in re.finditer(r'(FUNCTION_BLOCK|FUNCTION|PROGRAM|DATA_BLOCK)\s+(\w+)', source, re.IGNORECASE):
            relations.append({
                "type": "defines_block",
                "source": rel_path,
                "target": m.group(2),
                "detail": m.group(1).upper(),
            })
        for m in re.finditer(r'CALL\s+"?(\w+)"?', source, re.IGNORECASE):
            relations.append({
                "type": "calls",
                "source": rel_path,
                "target": m.group(1),
                "detail": "call",
            })

    elif ext == ".l5x":
        for m in re.finditer(r'Tag\s*=\s*"([^"]+)"', source):
            relations.append({
                "type": "references_tag",
                "source": rel_path,
                "target": m.group(1),
            })

    elif ext == ".md":
        for m in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', source):
            relations.append({
                "type": "marks_link",
                "source": rel_path,
                "target": m.group(2),
                "detail": m.group(1),
            })

    elif ext in (".yaml", ".yml", ".json", ".toml"):
        relations.append({
            "type": "config_file",
            "source": rel_path,
            "target": ext,
        })

    return relations


# ── KnowledgeGraph ─────────────────────────────────────────────────────

class KnowledgeGraph:
    """Graphe de connaissance construit à partir d'un dossier.

    Chaque fichier est un nœud, chaque relation (import, définition,
    tag, lien) est une arête. Le graphe peut être interrogé pour
    trouver des connexions entre entités.
    """

    def __init__(self):
        """Initialise le gestionnaire de graphe de connaissance."""
        self._graphs: Dict[str, Dict] = {}
        # Résolution du dossier utilisateur portable pour les graphes de connaissance
        from agent.helios_constants import get_helios_home
        self._index_dir = get_helios_home() / "knowledge_graphs"
        self._index_dir.mkdir(parents=True, exist_ok=True)

    def build(self, folder_path: str, recursive: bool = True, file_pattern: str = "*") -> str:
        """Construit un graphe de connaissance à partir d'un dossier.

        Args:
            folder_path: Chemin du dossier source à analyser.
            recursive: Explorer les sous-dossiers récursivement.
            file_pattern: Liste de glob patterns séparés par des virgules pour filtrer les fichiers.

        Returns:
            str: Chaîne JSON avec les statistiques de l'indexation.
        """
        root = Path(folder_path).resolve()
        if not root.exists():
            return json.dumps({"error": f"Dossier introuvable: {folder_path}"})

        patterns = [p.strip() for p in file_pattern.split(",")]

        nodes = {}  # format: nom -> {type, metadata}
        relations = []

        if recursive:
            iterator = root.rglob("*")
        else:
            iterator = root.glob("*")

        for file_path in sorted(iterator):
            if not file_path.is_file():
                continue

            # Filtrer par pattern
            if patterns and patterns != ["*"]:
                matched = any(file_path.match(p) for p in patterns if p)
                if not matched:
                    continue

            # Ignorer les dossiers système ou cachés
            rel = file_path.relative_to(root)
            if any(p.startswith(".") or p == "__pycache__" or p == ".git"
                   or p == "node_modules" for p in rel.parts):
                continue

            rel_path = str(rel)

            # Ajouter le nœud du fichier
            nodes[rel_path] = {
                "type": "file",
                "path": rel_path,
                "extension": file_path.suffix.lower(),
                "size": file_path.stat().st_size,
            }

            # Extraire et fusionner les relations
            file_relations = _extract_file_relations(file_path, root)
            for rel_info in file_relations:
                relations.append(rel_info)
                target = rel_info["target"]
                if target not in nodes:
                    nodes[target] = {"type": "symbol", "name": target}

        graph = {
            "root": str(root),
            "nodes": list(nodes.values()),
            "relations": relations,
            "node_count": len(nodes),
            "relation_count": len(relations),
            "built_at": time.time(),
            "file_pattern": file_pattern,
        }

        self._graphs[str(root)] = graph
        self._save(str(root), graph)

        return json.dumps({
            "success": True,
            "root": str(root),
            "nodes": graph["node_count"],
            "relations": graph["relation_count"],
        }, indent=2)

    def query(self, folder_path: str, entity: str = "",
              relation_type: str = "", depth: int = 1) -> str:
        """Interroge le graphe de connaissance.

        Args:
            folder_path: Chemin racine du graphe.
            entity: Nom de l'entité à filtrer (substring).
            relation_type: Type exact de relation à filtrer.
            depth: Profondeur de recherche (par défaut 1).

        Returns:
            str: Résultats de la recherche au format JSON.
        """
        root = str(Path(folder_path).resolve())
        graph = self._graphs.get(root)

        if not graph:
            graph = self._load(root)
            if not graph:
                return json.dumps({"error": f"Graphe non trouvé: {folder_path}. Lancez d'abord build()."})
            self._graphs[root] = graph

        result = {"root": root, "entity_filter": entity, "relation_type": relation_type}

        if entity:
            # Trouver les relations associées
            entity_lower = entity.lower()
            related_nodes = set()
            related_relations = []

            for rel in graph["relations"]:
                if entity_lower in rel["source"].lower() or entity_lower in rel["target"].lower():
                    if relation_type and rel["type"] != relation_type:
                        continue
                    related_relations.append(rel)
                    related_nodes.add(rel["source"])
                    related_nodes.add(rel["target"])

            result["entity"] = entity
            result["related_nodes"] = sorted(related_nodes)
            result["relations"] = related_relations
            result["count"] = len(related_relations)
        else:
            # Statistiques générales
            result["stats"] = {
                "total_nodes": graph["node_count"],
                "total_relations": graph["relation_count"],
                "built_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(graph["built_at"])),
            }

            # Top relations par type
            type_counts = {}
            for rel in graph["relations"]:
                t = rel["type"]
                type_counts[t] = type_counts.get(t, 0) + 1

            result["relation_types"] = dict(sorted(
                type_counts.items(), key=lambda x: x[1], reverse=True
            ))

        return json.dumps(result, ensure_ascii=False, indent=2)

    def _save(self, key: str, graph: Dict) -> None:
        """Sauvegarde le graphe de connaissance dans un fichier JSON.

        Args:
            key: Identifiant unique du graphe.
            graph: Le dictionnaire représentant le graphe.
        """
        path = self._index_dir / f"{key.replace('/', '_').replace(':', '')}.json"
        try:
            path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("Erreur sauvegarde graphe: %s", e)

    def _load(self, key: str) -> Optional[Dict]:
        """Charge un graphe de connaissance sauvegardé.

        Args:
            key: Identifiant unique du graphe.

        Returns:
            Optional[Dict]: Dictionnaire représentant le graphe ou None.
        """
        path = self._index_dir / f"{key.replace('/', '_').replace(':', '')}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None


# ── Singleton global ───────────────────────────────────────────────────

_kg = KnowledgeGraph()


# ── Gestionnaires d'outils ─────────────────────────────────────────────

def kg_build(folder_path: str = "", file_pattern: str = "*", recursive: bool = True) -> str:
    """Construit le graphe de connaissance pour un dossier.

    Args:
        folder_path: Chemin absolu vers le dossier à analyser.
        file_pattern: Pattern de filtrage de fichiers.
        recursive: Explorer récursivement les sous-dossiers.

    Returns:
        str: Rapport d'indexation JSON.
    """
    if not folder_path:
        return json.dumps({"error": "folder_path requis"})
    return _kg.build(folder_path, recursive, file_pattern)


def kg_query(folder_path: str = "", entity: str = "", relation_type: str = "") -> str:
    """Interroge un graphe de connaissance.

    Args:
        folder_path: Chemin du projet indexé.
        entity: Optionnel, nom de l'entité recherchée.
        relation_type: Optionnel, type exact de relation recherchée.

    Returns:
        str: JSON contenant les relations trouvées.
    """
    if not folder_path:
        return json.dumps({"error": "folder_path requis"})
    return _kg.query(folder_path, entity, relation_type)


# ── Enregistrement dans le registre Helios ──────────────────────────────

from tools.registry import registry


registry.register(
    name="kg_build",
    toolset="core",
    schema={
        "name": "kg_build",
        "description": "Construit un graphe de connaissance à partir d'un dossier de fichiers. "
                       "Analyse les relations entre fichiers: imports, définitions de symboles, tags, "
                       "liens markdown. Supporte Python, IEC 61131-3 (ST/SCL), Rockwell L5X, Markdown, JSON/YAML.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Chemin du dossier à analyser"},
                "file_pattern": {"type": "string", "description": "Glob patterns (ex: '*.py,*.md')", "default": "*"},
                "recursive": {"type": "boolean", "description": "Parcourir récursivement", "default": True}
            },
            "required": ["folder_path"]
        }
    },
    handler=lambda a, **kw: kg_build(
        a.get("folder_path", ""), a.get("file_pattern", "*"), a.get("recursive", True), **kw
    ),
    check_fn=None,
    requires_env=[],
    description="Construction de graphe de connaissance",
    emoji="🕸️",
)

registry.register(
    name="kg_query",
    toolset="core",
    schema={
        "name": "kg_query",
        "description": "Interroge un graphe de connaissance par entité ou type de relation. "
                       "Retourne les nœuds et relations autour d'une entité, ou les statistiques "
                       "globales du graphe si aucun filtre n'est spécifié.",
        "parameters": {
            "type": "object",
            "properties": {
                "folder_path": {"type": "string", "description": "Chemin racine du graphe"},
                "entity": {"type": "string", "description": "Filtrer par nom d'entité (substring)"},
                "relation_type": {"type": "string", "description": "Filtrer par type de relation"}
            },
            "required": ["folder_path"]
        }
    },
    handler=lambda a, **kw: kg_query(
        a.get("folder_path", ""), a.get("entity", ""), a.get("relation_type", ""), **kw
    ),
    check_fn=None,
    requires_env=[],
    description="Interrogation de graphe de connaissance",
    emoji="🔍",
)