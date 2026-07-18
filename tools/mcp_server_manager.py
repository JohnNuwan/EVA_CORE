#!/usr/bin/env python3
"""Module MCP Server Manager - Lister, installer et gérer les serveurs MCP."""
import json, logging, subprocess, os, signal
from pathlib import Path
from typing import Dict, List, Optional
logger = logging.getLogger(__name__)

_HELIOS_HOME = Path.home() / ".helios"
_MCP_DIRS = [Path("optional-mcps"), _HELIOS_HOME / "mcps"]


def _find_manifests() -> List[Path]:
    """Trouve tous les manifests MCP disponibles."""
    manifests = []
    for d in _MCP_DIRS:
        if d.exists():
            for f in d.glob("*/manifest.yaml"):
                manifests.append(f)
    return manifests


def list_servers() -> str:
    """Liste les serveurs MCP disponibles."""
    servers = []
    for manifest_path in _find_manifests():
        try:
            import yaml
            with open(manifest_path) as f:
                data = yaml.safe_load(f)
            servers.append({
                "name": data.get("name", manifest_path.parent.name),
                "description": data.get("description", ""),
                "command": data.get("command", ""),
                "path": str(manifest_path),
                "args": data.get("args", []),
                "env": list(data.get("env", {}).keys()) if data.get("env") else [],
            })
        except Exception as e:
            servers.append({"name": manifest_path.parent.name, "error": str(e)})

    return json.dumps({"servers": servers, "count": len(servers),
                        "search_paths": [str(d) for d in _MCP_DIRS]},
                       indent=2, ensure_ascii=False)


from tools.registry import registry

registry.register(
    name="mcp_list_servers", toolset="industrial",
    schema={"name": "mcp_list_servers",
            "description": "Liste les serveurs MCP disponibles (scanne optional-mcps/ et ~/.helios/mcps/).",
            "parameters": {"type": "object", "properties": {}}},
    handler=lambda a, **kw: list_servers(), is_async=False,
    description="Lister les serveurs MCP disponibles.", emoji="🔌",
)