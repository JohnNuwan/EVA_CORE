#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Code Intelligence Graph - Graphe de code local pour agents.

Inspiré par code-review-graph (tirth8205). Construit un graphe
persistant des symboles, dépendances et relations dans un codebase.
Accessible via MCP ou CLI. Stockage local-first en JSON.
"""

import json
import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


# ── Parsers symboles par langage ───────────────────────────────────────

def _parse_python_symbols(source: str) -> List[Dict[str, Any]]:
    """Extrait les symboles (classes, fonctions, imports) d'un fichier source Python.

    Args:
        source: Contenu textuel du fichier source Python.

    Returns:
        List[Dict[str, Any]]: Liste des symboles identifiés avec leur localisation.
    """
    symbols = []
    # Expressions régulières pour matcher les classes et fonctions
    class_pattern = re.compile(r'^\s*class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:', re.MULTILINE)
    func_pattern = re.compile(r'^\s*(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*[^:]+)?\s*:', re.MULTILINE)

    for m in class_pattern.finditer(source):
        bases = [b.strip() for b in m.group(2).split(",") if b.strip()] if m.group(2) else []
        symbols.append({
            "type": "class",
            "name": m.group(1),
            "bases": bases,
            "line": source[:m.start()].count("\n") + 1,
        })

    for m in func_pattern.finditer(source):
        symbols.append({
            "type": "function",
            "name": m.group(1),
            "params": [p.strip() for p in m.group(2).split(",") if p.strip()],
            "line": source[:m.start()].count("\n") + 1,
        })

    # Expressions régulières pour matcher les imports (dépendances)
    import_pattern = re.compile(r'^\s*(?:from\s+(\S+)\s+import\s+(\S+)|import\s+(\S+))', re.MULTILINE)
    for m in import_pattern.finditer(source):
        symbols.append({
            "type": "import",
            "source": m.group(1) or m.group(3),
            "name": m.group(2) or m.group(3),
            "line": source[:m.start()].count("\n") + 1,
        })

    return symbols


def _parse_iec61131_symbols(source: str, lang: str = "st") -> List[Dict[str, Any]]:
    """Extrait les symboles (blocs de fonctions, variables) d'un fichier IEC 61131-3 (ST, SCL, AWL).

    Args:
        source: Contenu du code source IEC 61131-3.
        lang: Langage source ('st' par défaut).

    Returns:
        List[Dict[str, Any]]: Liste des blocs et variables déclarées.
    """
    symbols = []

    # Blocs: FUNCTION_BLOCK, FUNCTION, PROGRAM
    fb_pattern = re.compile(
        r'(FUNCTION_BLOCK|FUNCTION|PROGRAM)\s+(\w+)',
        re.IGNORECASE | re.MULTILINE,
    )
    for m in fb_pattern.finditer(source):
        symbols.append({
            "type": m.group(1).upper(),
            "name": m.group(2),
            "line": source[:m.start()].count("\n") + 1,
        })

    # Blocs VAR .. END_VAR (déclarations de variables)
    var_pattern = re.compile(
        r'(?:VAR|VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR_TEMP)\s+(.*?)END_VAR',
        re.IGNORECASE | re.DOTALL,
    )
    for m in var_pattern.finditer(source):
        block = m.group(1)
        for line in block.split("\n"):
            line = line.strip()
            if line and not line.startswith("//") and not line.startswith("(*"):
                var_match = re.match(r'(\w+)\s*:\s*(\w+)', line)
                if var_match:
                    symbols.append({
                        "type": "variable",
                        "name": var_match.group(1),
                        "data_type": var_match.group(2),
                        "line": source[:m.start()].count("\n") + 1 + block[:block.index(line)].count("\n"),
                    })

    # Méthodes (METHOD)
    method_pattern = re.compile(r'METHOD\s+(\w+)', re.IGNORECASE | re.MULTILINE)
    for m in method_pattern.finditer(source):
        symbols.append({
            "type": "METHOD",
            "name": m.group(1),
            "line": source[:m.start()].count("\n") + 1,
        })

    return symbols


def _parse_scl_symbols(source: str) -> List[Dict[str, Any]]:
    """Extrait les symboles d'un fichier source SCL Siemens.

    Args:
        source: Contenu du fichier SCL.

    Returns:
        List[Dict[str, Any]]: Liste des blocs de données, fonctions et variables SCL.
    """
    symbols = []

    # Blocs: FUNCTION_BLOCK, FUNCTION, DATA_BLOCK, CLASS, PROGRAM
    block_pattern = re.compile(
        r'(FUNCTION_BLOCK|FUNCTION|DATA_BLOCK|CLASS|PROGRAM)\s+(\w+)',
        re.IGNORECASE | re.MULTILINE,
    )
    for m in block_pattern.finditer(source):
        symbols.append({
            "type": m.group(1).upper(),
            "name": m.group(2),
            "line": source[:m.start()].count("\n") + 1,
        })

    # Déclaration de variables (VAR .. END_VAR, STAT)
    var_pattern = re.compile(
        r'(?:VAR|VAR_INPUT|VAR_OUTPUT|VAR_IN_OUT|VAR_TEMP|STAT)\s+(.*?)END_VAR',
        re.IGNORECASE | re.DOTALL,
    )
    for m in var_pattern.finditer(source):
        block = m.group(1)
        for line in block.split("\n"):
            line = line.strip()
            if line and not line.startswith("//") and not line.startswith("(*"):
                v = re.match(r'(\w+)\s*:\s*(\w+)', line)
                if v:
                    symbols.append({"type": "variable", "name": v.group(1), "data_type": v.group(2)})

    return symbols


# ── CodeGraph ──────────────────────────────────────────────────────────

SUPPORTED_EXTENSIONS = {
    ".py": _parse_python_symbols,
    ".st": _parse_iec61131_symbols,
    ".scl": _parse_scl_symbols,
    ".awl": _parse_iec61131_symbols,
    ".L5X": None,  # XML, parsing spécialisé
}


class CodeGraph:
    """Graphe de code persistant.

    Stocke les symboles, les dépendances entre fichiers,
    et les relations d'appel. Indexé par projet (racine).
    """

    def __init__(self):
        """Initialise le gestionnaire de graphe de code."""
        self._graphs: Dict[str, Dict] = {}
        # Résolution du dossier utilisateur portable pour les graphes de code
        from agent.helios_constants import get_helios_home
        self._index_dir = get_helios_home() / "code_graphs"
        self._index_dir.mkdir(parents=True, exist_ok=True)

    def build(self, project_path: str, recursive: bool = True) -> str:
        """Construit le graphe de code pour un projet donné.

        Args:
            project_path: Chemin racine du projet.
            recursive: Explorer récursivement les sous-dossiers.

        Returns:
            str: Chaîne JSON avec les statistiques de l'indexation.
        """
        root = Path(project_path).resolve()
        if not root.exists():
            return json.dumps({"error": f"Chemin introuvable: {project_path}"})

        graph = {
            "root": str(root),
            "files": [],
            "symbols": [],
            "dependencies": [],
            "built_at": time.time(),
        }

        pattern = "**/*" if recursive else "*"
        total_files = 0
        total_symbols = 0

        for ext, parser in SUPPORTED_EXTENSIONS.items():
            for file_path in root.glob(f"{pattern}{ext}"):
                if any(p.startswith(".") or p == "__pycache__" or p == ".git"
                       for p in file_path.relative_to(root).parts):
                    continue
                try:
                    source = file_path.read_text(encoding="utf-8", errors="replace")
                    rel_path = str(file_path.relative_to(root))

                    # Pour L5X (XML), parsing spécialisé
                    if ext == ".L5X":
                        symbols = self._parse_l5x(source)
                    elif parser:
                        symbols = parser(source)
                    else:
                        symbols = []

                    file_info = {
                        "path": rel_path,
                        "size": len(source),
                        "lines": source.count("\n"),
                        "symbol_count": len(symbols),
                    }
                    graph["files"].append(file_info)
                    for s in symbols:
                        s["file"] = rel_path
                        graph["symbols"].append(s)

                    # Extraire les dépendances inter-fichiers (pour Python)
                    if ext == ".py":
                        imports = [s for s in symbols if s["type"] == "import"]
                        for imp in imports:
                            graph["dependencies"].append({
                                "from_file": rel_path,
                                "import_target": imp["source"],
                                "imported_name": imp["name"],
                            })

                    total_files += 1
                    total_symbols += len(symbols)
                except Exception as e:
                    logger.warning("Erreur parsing %s: %s", file_path, e)

        self._graphs[str(root)] = graph
        self._save(str(root), graph)

        return json.dumps({
            "success": True,
            "project": str(root),
            "files": total_files,
            "symbols": total_symbols,
            "dependencies": len(graph["dependencies"]),
        }, indent=2)

    def _parse_l5x(self, source: str) -> List[Dict[str, Any]]:
        """Parse un fichier L5X Rockwell pour en extraire les tags déclarés.

        Args:
            source: Contenu XML brut du fichier L5X.

        Returns:
            List[Dict[str, Any]]: Liste des tags Rockwell découverts.
        """
        symbols = []
        rungs = re.findall(r'<Rung.*?>(.*?)</Rung>', source, re.DOTALL)
        for i, rung in enumerate(rungs):
            tags = re.findall(r'Tag\s*=\s*\"([^\"]+)\"', rung)
            for tag in tags:
                symbols.append({
                    "type": "tag",
                    "name": tag,
                    "rung": i + 1,
                })
        return symbols

    def query(self, project_path: str, query_type: str = "symbols",
              name_filter: str = "") -> str:
        """Interroge le graphe de code du projet.

        Args:
            project_path: Chemin racine du projet.
            query_type: Type de requête ('stats', 'files', 'symbols', ou 'dependencies').
            name_filter: Filtre de recherche textuelle optionnel (substring).

        Returns:
            str: Résultats de la requête au format JSON.
        """
        root = str(Path(project_path).resolve())
        graph = self._graphs.get(root)

        if not graph:
            # Charger depuis le stockage persistant
            graph = self._load(root)
            if not graph:
                return json.dumps({"error": f"Projet non indexé: {project_path}. Lancez d'abord build()."})
            self._graphs[root] = graph

        if query_type == "stats":
            return json.dumps({
                "root": graph["root"],
                "total_files": len(graph["files"]),
                "total_symbols": len(graph["symbols"]),
                "total_dependencies": len(graph["dependencies"]),
                "built_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(graph["built_at"])),
            }, indent=2)

        elif query_type == "files":
            files = graph["files"]
            if name_filter:
                files = [f for f in files if name_filter.lower() in f["path"].lower()]
            return json.dumps({"files": files, "count": len(files)}, indent=2)

        elif query_type == "symbols":
            symbols = graph["symbols"]
            if name_filter:
                symbols = [s for s in symbols if name_filter.lower() in s["name"].lower()]
            return json.dumps({"symbols": symbols, "count": len(symbols)}, indent=2)

        elif query_type == "dependencies":
            deps = graph["dependencies"]
            if name_filter:
                deps = [d for d in deps if name_filter.lower() in str(d).lower()]
            return json.dumps({"dependencies": deps, "count": len(deps)}, indent=2)

        return json.dumps({"error": f"Type de requête inconnu: {query_type}"})

    def _save(self, key: str, graph: Dict) -> None:
        """Sauvegarde un graphe de code au format JSON.

        Args:
            key: Clé d'identification (chemin du projet).
            graph: Dictionnaire du graphe à sérialiser.
        """
        path = self._index_dir / f"{key.replace('/', '_').replace(':', '')}.json"
        try:
            path.write_text(json.dumps(graph, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning("Erreur sauvegarde graphe: %s", e)

    def _load(self, key: str) -> Optional[Dict]:
        """Charge un graphe de code stocké.

        Args:
            key: Clé du projet d'origine.

        Returns:
            Optional[Dict]: Dictionnaire du graphe restauré, ou None s'il n'existe pas.
        """
        path = self._index_dir / f"{key.replace('/', '_').replace(':', '')}.json"
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None


# ── Singleton global ───────────────────────────────────────────────────

_graph = CodeGraph()


# ── Gestionnaires d'outils ─────────────────────────────────────────────

def codegraph_build(project_path: str = "", recursive: bool = True) -> str:
    """Construit le graphe de code pour un projet.

    Args:
        project_path: Chemin absolu ou relatif vers le dossier du projet.
        recursive: Explorer récursivement ou non.

    Returns:
        str: Rapport JSON de l'indexation.
    """
    if not project_path:
        return json.dumps({"error": "project_path requis"})
    return _graph.build(project_path, recursive)


def codegraph_query(project_path: str = "", query_type: str = "stats", name_filter: str = "") -> str:
    """Interroge un graphe de code pré-construit.

    Args:
        project_path: Chemin vers le dossier racine du projet.
        query_type: Type de données demandées ('stats', 'files', 'symbols', 'dependencies').
        name_filter: Motif de recherche pour filtrer les symboles.

    Returns:
        str: JSON des résultats de l'interrogation.
    """
    if not project_path:
        return json.dumps({"error": "project_path requis"})
    return _graph.query(project_path, query_type, name_filter)


# ── Enregistrement dans le registre Helios ──────────────────────────────

from tools.registry import registry


registry.register(
    name="codegraph_build",
    toolset="core",
    schema={
        "name": "codegraph_build",
        "description": "Construit un graphe persistant des symboles et dépendances d'un projet. "
                       "Support: Python (classes, fonctions, imports), IEC 61131-3 ST/SCL (FB, FC, VAR), "
                       "Rockwell L5X (tags). Stocké localement pour requêtes ultérieures.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Chemin racine du projet"},
                "recursive": {"type": "boolean", "description": "Parcourir récursivement", "default": True}
            },
            "required": ["project_path"]
        }
    },
    handler=lambda a, **kw: codegraph_build(a.get("project_path", ""), a.get("recursive", True), **kw),
    check_fn=None,
    requires_env=[],
    description="Construction de graphe de code",
    emoji="📊",
)

registry.register(
    name="codegraph_query",
    toolset="core",
    schema={
        "name": "codegraph_query",
        "description": "Interroge un graphe de code pré-construit. "
                       "Types: 'stats' (statistiques), 'files' (fichiers), 'symbols' (symboles), "
                       "'dependencies' (dépendances). Peut filtrer par nom.",
        "parameters": {
            "type": "object",
            "properties": {
                "project_path": {"type": "string", "description": "Chemin racine"},
                "query_type": {
                    "type": "string",
                    "enum": ["stats", "files", "symbols", "dependencies"],
                    "description": "Type de requête"
                },
                "name_filter": {"type": "string", "description": "Filtre par nom (substring)"}
            },
            "required": ["project_path", "query_type"]
        }
    },
    handler=lambda a, **kw: codegraph_query(
        a.get("project_path", ""), a.get("query_type", "stats"), a.get("name_filter", ""), **kw
    ),
    check_fn=None,
    requires_env=[],
    description="Interrogation de graphe de code",
    emoji="🔍",
)