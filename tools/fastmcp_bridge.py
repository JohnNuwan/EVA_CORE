#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FastMCP Bridge - Création simplifiée de serveurs MCP pour Helios.

Inspiré par PrefectHQ/fastmcp. Permet de créer un serveur MCP
en quelques lignes, d'exposer des outils Helios via MCP, et de
démarrer des sidecars MCP. Dépendance optionnelle: mcp.
"""

import json
import logging
import os
import sys
import threading
from typing import Any, Callable, Dict, List, Optional, get_type_hints

logger = logging.getLogger(__name__)

# ── Vérification dépendance MCP ────────────────────────────────────────

_MCP_AVAILABLE = False
try:
    import mcp.server.fastmcp as fastmcp
    _MCP_AVAILABLE = True
except ImportError:
    pass


# ── HeliosMCPServer ────────────────────────────────────────────────────

class HeliosMCPServer:
    """Wrapper simplifié autour de FastMCP.

    Usage:
        server = HeliosMCPServer("my-server", "Description")
        server.add_tool("hello", "Say hello", {"type": "object", ...}, lambda args: "Hi!")
        server.run_stdio()
    """

    def __init__(self, name: str, description: str = "", debug: bool = False):
        """Initialise le serveur MCP d'Helios.

        Args:
            name: Nom du serveur MCP.
            description: Description courte du serveur.
            debug: Activer le mode débogage.
        """
        self.name = name
        self.description = description
        self._debug = debug
        self._tools: Dict[str, Callable] = {}
        self._server = None
        self._http_server = None
        self._thread = None

        if not _MCP_AVAILABLE:
            logger.warning("Le paquet MCP n'est pas disponible. Installer avec : pip install mcp")
            return

        self._server = fastmcp.FastMCP(
            name,
            description=description or f"Serveur MCP Helios : {name}",
        )

    def add_tool(self, name: str, description: str, schema: Dict[str, Any],
                 handler: Callable) -> "HeliosMCPServer":
        """Ajoute un outil au serveur MCP avec un schéma explicite.

        Args:
            name: Nom de l'outil.
            description: Description de l'outil.
            schema: Dictionnaire décrivant le schéma des paramètres.
            handler: Callback à appeler lors de l'exécution de l'outil.

        Returns:
            HeliosMCPServer: L'instance du serveur lui-même.
        """
        if not _MCP_AVAILABLE:
            logger.warning("MCP indisponible, impossible d'ajouter l'outil %s", name)
            return self

        @self._server.tool(name=name, description=description)
        def _tool_wrapper(args: str = "{}") -> str:
            """Wrapper de fonction pour gérer les paramètres JSON entrants.

            Args:
                args: Arguments au format JSON brut.

            Returns:
                str: Résultat sous forme de chaîne de caractères.
            """
            parsed = json.loads(args) if isinstance(args, str) else args
            result = handler(parsed)
            return str(result) if not isinstance(result, str) else result

        self._tools[name] = _tool_wrapper
        return self

    def tool(self, fn: Callable = None, *, name: str = None, description: str = None,
             schema: Dict[str, Any] = None):
        """Décorateur pour enregistrer une fonction comme outil MCP.

        Args:
            fn: Fonction à décorer.
            name: Nom personnalisé de l'outil.
            description: Description personnalisée de l'outil.
            schema: Schéma de paramètres.

        Returns:
            Callable: Le décorateur ou la fonction décorée.
        """
        def _decorator(func):
            nonlocal name, description, schema
            tool_name = name or func.__name__
            tool_desc = description or func.__doc__ or f"Outil : {tool_name}"
            self.add_tool(tool_name, tool_desc, schema or {}, lambda args: func(**args))
            return func

        if fn is not None:
            return _decorator(fn)
        return _decorator

    def run_stdio(self) -> None:
        """Démarre le serveur sur le transport stdio pour l'intégration CLI.

        Raises:
            ImportError: Si la bibliothèque mcp n'est pas disponible.
        """
        if not _MCP_AVAILABLE:
            raise ImportError("Le paquet MCP est requis : pip install mcp")
        self._server.run(transport="stdio")

    def run_http(self, host: str = "0.0.0.0", port: int = 9876) -> None:
        """Démarre le serveur sur le transport HTTP Streamable.

        Args:
            host: Interface réseau d'écoute (par défaut '0.0.0.0').
            port: Port d'écoute (par défaut 9876).

        Raises:
            ImportError: Si la bibliothèque mcp n'est pas installée.
        """
        if not _MCP_AVAILABLE:
            raise ImportError("Le paquet MCP est requis : pip install mcp")
        import uvicorn
        app = self._server.create_app()
        uvicorn.run(app, host=host, port=port)

    def run_http_background(self, host: str = "0.0.0.0", port: int = 9876) -> None:
        """Démarre le serveur HTTP dans un thread d'arrière-plan.

        Args:
            host: Interface réseau.
            port: Port réseau.

        Raises:
            ImportError: Si mcp n'est pas disponible.
        """
        if not _MCP_AVAILABLE:
            raise ImportError("Le paquet MCP est requis : pip install mcp")

        def _run():
            self.run_http(host, port)

        self._thread = threading.Thread(target=_run, daemon=True, name=f"mcp-{self.name}")
        self._thread.start()
        logger.info("Serveur MCP '%s' démarré sur http://%s:%s", self.name, host, port)

    def list_tools(self) -> List[Dict[str, str]]:
        """Liste tous les outils enregistrés sur le serveur.

        Returns:
            List[Dict[str, str]]: Liste d'outils avec leur nom et description.
        """
        return [{"name": name, "description": tool.__doc__ or ""}
                for name, tool in self._tools.items()]


# ── Factory ────────────────────────────────────────────────────────────

def create_server(name: str, description: str = "") -> HeliosMCPServer:
    """Crée rapidement une nouvelle instance de serveur MCP.

    Args:
        name: Nom unique du serveur.
        description: Description courte.

    Returns:
        HeliosMCPServer: Nouvelle instance configurée.
    """
    return HeliosMCPServer(name, description)


# ── Exposer les outils Helios via MCP ──────────────────────────────────

def discover_helios_tools_as_mcp(filter_toolset: Optional[str] = None) -> HeliosMCPServer:
    """Expose tous les outils Helios d'un toolset comme serveur MCP.

    Permet à des clients MCP externes d'appeler les outils d'Helios.

    Args:
        filter_toolset: Nom du toolset à filtrer (ex: 'core', 'industrial').

    Returns:
        HeliosMCPServer: Serveur MCP contenant les outils découverts.
    """
    server = HeliosMCPServer("helios-tools", "Helios Agent tools exposed as MCP")

    try:
        from agent.model_tools import get_tool_definitions, handle_function_call
    except ImportError:
        # Fallback : importer depuis le module alternatif si nécessaire
        try:
            from agent.model_tools import get_tool_definitions
            from agent.tool_executor import _run_agent_tool_execution_middleware
        except ImportError:
            logger.warning("Impossible d'importer les définitions d'outils Helios")
            return server

    tool_defs = get_tool_definitions(
        enabled_toolsets={filter_toolset} if filter_toolset else None,
        disabled_toolsets=None,
    )

    for tool_def in tool_defs:
        func = tool_def.get("function", tool_def)
        name = func.get("name", "")
        desc = func.get("description", "") or f"Outil Helios : {name}"
        params = func.get("parameters", {"type": "object", "properties": {}})

        def _make_handler(tool_name):
            def _handler(args: dict) -> str:
                try:
                    return handle_function_call(tool_name, json.dumps(args), task_id="mcp")
                except Exception as e:
                    return json.dumps({"error": str(e)})
            return _handler

        server.add_tool(name, desc, params, _make_handler(name))

    return server


def start_mcp_sidecar(name: str = "helios-sidecar", port: int = 9876,
                      filter_toolset: Optional[str] = None) -> str:
    """Lance un serveur MCP Helios en arrière-plan (sidecar).

    Args:
        name: Nom unique du serveur.
        port: Port HTTP d'écoute.
        filter_toolset: Nom de la boîte à outils à exposer (optionnel).

    Returns:
        str: JSON détaillant le statut du sidecar lancé.
    """
    try:
        server = discover_helios_tools_as_mcp(filter_toolset)
        server.run_http_background(port=port)
        return json.dumps({
            "success": True,
            "server": name,
            "port": port,
            "tool_count": len(server.list_tools()),
            "url": f"http://localhost:{port}/mcp",
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Tool Handler ───────────────────────────────────────────────────────

def _handle_create_server(name: str = "", tool_list: str = "[]", port: int = 9876) -> str:
    """Crée et démarre un serveur MCP dynamique.

    Args:
        name: Nom du serveur.
        tool_list: Chaîne JSON contenant la liste des outils.
        port: Port d'écoute HTTP.

    Returns:
        str: Rapport JSON de l'exécution.
    """
    if not name:
        return json.dumps({"error": "name requis"})
    try:
        tools = json.loads(tool_list) if isinstance(tool_list, str) else tool_list
    except json.JSONDecodeError:
        return json.dumps({"error": "tool_list n'est pas du JSON valide"})

    server = create_server(name, f"Serveur MCP dynamique : {name}")
    for t in tools:
        tname = t.get("name", "unnamed")
        tdesc = t.get("description", "")
        tparams = t.get("parameters", {"type": "object", "properties": {}})
        thandler_code = t.get("handler", "return 'ok'")

        def _make_handler(code):
            def _handler(args):
                try:
                    exec_globals = {"args": args, "json": json}
                    exec(code, exec_globals)
                    return exec_globals.get("result", "ok")
                except Exception as e:
                    return json.dumps({"error": str(e)})
            return _handler

        server.add_tool(tname, tdesc, tparams, _make_handler(thandler_code))

    server.run_http_background(port=port)
    return json.dumps({
        "success": True,
        "server": name,
        "port": port,
        "tools": len(tools),
    }, indent=2)


# ── Registration ──────────────────────────────────────────────────────

from tools.registry import registry


def _check_mcp() -> bool:
    """Vérifie si le package mcp est disponible dans l'environnement.

    Returns:
        bool: True si mcp est installé, False sinon.
    """
    return _MCP_AVAILABLE


registry.register(
    name="mcp_create_server",
    toolset="core",
    schema={
        "name": "mcp_create_server",
        "description": "Crée et démarre un serveur MCP dynamique avec des outils personnalisés. "
                       "Utile pour exposer des fonctionnalités Helios via le Model Context Protocol.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom du serveur MCP"},
                "tool_list": {
                    "type": "string",
                    "description": "Liste JSON d'outils: [{\"name\":\"...\",\"description\":\"...\",\"handler\":\"code\"}]"
                },
                "port": {"type": "integer", "description": "Port HTTP", "default": 9876}
            },
            "required": ["name"]
        }
    },
    handler=lambda a, **kw: _handle_create_server(
        a.get("name", ""), a.get("tool_list", "[]"), a.get("port", 9876), **kw
    ),
    check_fn=_check_mcp,
    requires_env=[],
    description="Création de serveurs MCP dynamiques",
    emoji="🔌",
)


# ── CLI entry point ────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Helios FastMCP Bridge")
    parser.add_argument("--http", action="store_true", help="Mode d'exécution HTTP")
    parser.add_argument("--port", type=int, default=9876, help="Port HTTP")
    parser.add_argument("--toolset", type=str, default=None, help="Filtrer par toolset")
    parser.add_argument("--name", type=str, default="helios-bridge", help="Nom du serveur")
    args = parser.parse_args()

    if args.http:
        server = discover_helios_tools_as_mcp(args.toolset)
        print(f"Démarrage du serveur MCP '{args.name}' sur le port {args.port}...")
        print(f"Outils : {len(server.list_tools())}")
        server.run_http(port=args.port)
    else:
        server = discover_helios_tools_as_mcp(args.toolset)
        print(f"Démarrage du serveur MCP '{args.name}' sur stdio...")
        print(f"Outils : {len(server.list_tools())}")
        server.run_stdio()