#!/usr/bin/env python3
"""
Module OPC UA Browser - Naviguer, lire et écrire dans un serveur OPC UA depuis l'agent.

Usage:
    from tools.opcua_browser import browse_server, read_nodes, write_node
    nodes = browse_server("opc.tcp://192.168.1.100:4840")
"""

import json, logging, asyncio
from typing import List, Any

logger = logging.getLogger(__name__)
_OPCUA_AVAILABLE = False
try:
    import asyncua
    _OPCUA_AVAILABLE = True
except ImportError:
    pass


def browse_server(server_url: str, timeout: int = 10) -> str:
    """Parcourt l'arbre d'adressage d'un serveur OPC UA."""
    if not _OPCUA_AVAILABLE:
        return json.dumps({"error": "asyncua non installé. pip install asyncua"})
    async def _browse():
        from asyncua import Client
        client = Client(server_url, timeout=timeout)
        try:
            await client.connect()
            objects = client.get_objects_node()
            result = {"server_url": server_url, "nodes": []}
            children = await objects.get_children()
            for child in children:
                info = {
                    "node_id": (await child.read_node_id()).to_string(),
                    "browse_name": (await child.read_browse_name()).to_string(),
                    "display_name": (await child.read_display_name()).Text or "",
                }
                result["nodes"].append(info)
            await client.disconnect()
            return json.dumps(result, indent=2, ensure_ascii=False)
        except Exception as e:
            await client.disconnect()
            return json.dumps({"error": str(e)})
    return asyncio.run(_browse())


def read_nodes(server_url: str, node_ids: List[str], timeout: int = 10) -> str:
    """Lit les valeurs de nœuds OPC UA."""
    if not _OPCUA_AVAILABLE:
        return json.dumps({"error": "asyncua not installed"})
    async def _read():
        from asyncua import Client
        client = Client(server_url, timeout=timeout)
        try:
            await client.connect()
            results = []
            for nid in node_ids:
                try:
                    node = client.get_node(nid)
                    val = await node.read_value()
                    results.append({"node_id": nid, "value": str(val), "status": "ok"})
                except Exception as e:
                    results.append({"node_id": nid, "error": str(e), "status": "error"})
            await client.disconnect()
            return json.dumps({"results": results}, indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})
    return asyncio.run(_read())


def get_sandbox_mode() -> str:
    """Récupère le mode de sandboxing depuis la configuration globale.

    Returns:
        str: Le mode configuré (simulation, read_only, production).
    """
    try:
        from helios_cli.config import load_config
        cfg = load_config()
        return cfg.get("industrial", {}).get("sandbox_mode", "simulation")
    except Exception:
        return "simulation"


def write_node(server_url: str, node_id: str, value: Any, timeout: int = 10) -> str:
    """Écrit une valeur sur un nœud OPC UA en validant le sandboxing.

    Args:
        server_url: URL du serveur OPC UA.
        node_id: Identifiant du nœud à écrire.
        value: Valeur à écrire.
        timeout: Délai d'attente maximum en secondes.

    Returns:
        str: Résultat de l'écriture sérialisé en JSON.
    """
    if not _OPCUA_AVAILABLE:
        return json.dumps({"error": "asyncua not installed"})

    sandbox = get_sandbox_mode()
    if sandbox in ("simulation", "read_only"):
        logger.warning(
            f"[AUDIT TRAIL] Refus d'écriture OPC UA en mode sandboxed ({sandbox}). "
            f"Serveur: {server_url}, Nœud: {node_id}, Valeur: {value}"
        )
        return json.dumps({
            "error": f"Accès écriture refusé : le mode de sandboxing actuel est '{sandbox}'."
        }, ensure_ascii=False)

    logger.info(
        f"[AUDIT TRAIL] Tentative d'écriture OPC UA en mode '{sandbox}'. "
        f"Serveur: {server_url}, Nœud: {node_id}, Valeur: {value}"
    )

    async def _write():
        from asyncua import Client
        client = Client(server_url, timeout=timeout)
        try:
            await client.connect()
            node = client.get_node(node_id)
            await node.write_value(value)
            await client.disconnect()
            logger.info(f"[AUDIT TRAIL] Écriture OPC UA réussie sur le nœud {node_id}")
            return json.dumps({"status": "ok", "node_id": node_id, "value": value})
        except Exception as e:
            logger.error(f"[AUDIT TRAIL] Écriture OPC UA échouée sur le nœud {node_id} : {e}")
            return json.dumps({"error": str(e)})
    return asyncio.run(_write())


from tools.registry import registry  # noqa: E402

def _check_opcua() -> bool:
    return _OPCUA_AVAILABLE

registry.register(
    name="opcua_browse",
    toolset="industrial",
    schema={
        "name": "opcua_browse",
        "description": "Parcourt l'arbre d'adressage d'un serveur OPC UA pour découvrir les nœuds disponibles.",
        "parameters": {
            "type": "object",
            "properties": {
                "server_url": {"type": "string", "description": "URL du serveur OPC UA (ex: opc.tcp://192.168.1.100:4840)"},
                "timeout": {"type": "integer", "description": "Timeout (s), défaut: 10"}
            },
            "required": ["server_url"]
        }
    },
    handler=lambda args, **kw: browse_server(args["server_url"], int(args.get("timeout", 10))),
    check_fn=_check_opcua,
    is_async=False,
    description="Parcourir l'arbre d'adressage d'un serveur OPC UA.",
    emoji="🔎",
)

registry.register(
    name="opcua_read",
    toolset="industrial",
    schema={
        "name": "opcua_read",
        "description": "Lit les valeurs de nœuds OPC UA spécifiés par leurs identifiants.",
        "parameters": {
            "type": "object",
            "properties": {
                "server_url": {"type": "string", "description": "URL du serveur OPC UA"},
                "node_ids": {"type": "array", "items": {"type": "string"}, "description": "Liste des IDs"}
            },
            "required": ["server_url", "node_ids"]
        }
    },
    handler=lambda args, **kw: read_nodes(args["server_url"], args["node_ids"]),
    check_fn=_check_opcua,
    is_async=False,
    description="Lire les valeurs de nœuds OPC UA.",
    emoji="📖",
)

registry.register(
    name="opcua_write",
    toolset="industrial",
    schema={
        "name": "opcua_write",
        "description": "Écrit une valeur sur un nœud OPC UA.",
        "parameters": {
            "type": "object",
            "properties": {
                "server_url": {"type": "string", "description": "URL du serveur OPC UA"},
                "node_id": {"type": "string", "description": "ID du nœud à écrire"},
                "value": {"type": "string", "description": "Valeur à écrire"}
            },
            "required": ["server_url", "node_id", "value"]
        }
    },
    handler=lambda args, **kw: write_node(args["server_url"], args["node_id"], args["value"]),
    check_fn=_check_opcua,
    is_async=False,
    description="Écrire une valeur sur un nœud OPC UA.",
    emoji="✏️",
)