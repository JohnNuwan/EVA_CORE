"""Couche de sécurité et de contrôle d'accès (RBAC) pour les serveurs MCP.

Ce module intercepte les appels d'outils MCP pour valider la conformité aux politiques
de sécurité locales définies dans `mcp_policies.yaml`.
"""

import os
import yaml
from pathlib import Path
from agent.helios_constants import get_helios_home

def load_mcp_policies() -> dict:
    """Charge les règles de sécurité MCP depuis mcp_policies.yaml."""
    policy_path = get_helios_home() / "mcp_policies.yaml"
    if not policy_path.exists():
        return {}
    try:
        with open(policy_path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def validate_mcp_call(server_name: str, tool_name: str, arguments: dict) -> tuple[bool, str]:
    """Valide si l'appel d'outil MCP respecte la politique RBAC.

    Args:
        server_name: Nom du serveur MCP.
        tool_name: Nom de l'outil appelé.
        arguments: Arguments fournis à l'outil.

    Returns:
        Un tuple (autorisé, message_erreur).
    """
    policies = load_mcp_policies()
    if not policies:
        return True, ""

    # Extraction des politiques du serveur
    server_policy = policies.get("servers", {}).get(server_name)
    if not server_policy:
        return True, ""

    # 1. Vérification de la liste blanche d'outils
    allowed_tools = server_policy.get("allowed_tools")
    if allowed_tools is not None and tool_name not in allowed_tools:
        return False, f"L'outil '{tool_name}' n'est pas autorisé par la politique de sécurité pour le serveur '{server_name}'."

    # 2. Vérification d'accès aux chemins pour les outils de fichiers
    allowed_paths = server_policy.get("allowed_paths")
    if allowed_paths is not None:
        for arg_name, arg_val in arguments.items():
            if "path" in arg_name.lower() and isinstance(arg_val, str):
                # Normalisation pour comparaison
                resolved_path = os.path.normpath(os.path.abspath(arg_val))
                authorized = False
                for auth_path in allowed_paths:
                    resolved_auth = os.path.normpath(os.path.abspath(auth_path))
                    # Autoriser si le chemin est égal ou est un sous-répertoire du chemin autorisé
                    if resolved_path == resolved_auth or resolved_path.startswith(resolved_auth + os.sep):
                        authorized = True
                        break
                if not authorized:
                    return False, f"Accès au chemin '{arg_val}' refusé par la politique de sécurité du serveur MCP '{server_name}'."

    return True, ""
