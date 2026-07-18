# -*- coding: utf-8 -*-
"""Serveur MCP de Connectivité Industrielle (OPC-UA / Beckhoff ADS).

Ce module implémente un serveur MCP local s'appuyant sur FastMCP pour simuler
les interactions de lecture, écriture et exploration de variables sur des
automates industriels via OPC-UA ou Beckhoff ADS.
"""

from mcp.server.fastmcp import FastMCP
import json
import time
import re
from typing import Dict, Any

mcp = FastMCP("mcp-industrial-connectivity")

# Base de données d'état simulée pour le PLC
_PLC_STATE: Dict[str, Any] = {
    "connected_plc": None,
    # Tags simulés par défaut (valeurs initiales)
    "tags": {
        "AS6/EPH/660C1_EPH_AgitCtrl/Status": 0,
        "AS6/EPH/660C1_EPH_AgitCtrl/PhaseActive": False,
        "AS6/EM/664C6_E_B_INLET/Command": 0,
        "AS6/EM/664C6_E_B_INLET/Status": 0,
        "AS7/EPH/701C1_EPH_AgitCtrl/Status": 0,
        "AS7/EM/701C1_E_B_INLET/Command": 0,
    }
}


@mcp.tool()
def plc_connect(plc_type: str, endpoint: str) -> str:
    """Établit une connexion simulée avec un automate industriel.

    Args:
        plc_type: Le type de protocole à utiliser ('opc-ua' ou 'ads').
        endpoint: L'adresse réseau (ex: 'opc.tcp://192.168.1.10:4840') ou l'AMS Net ID (ex: '192.168.1.10.1.1:851').

    Returns:
        str: Une chaîne JSON décrivant le statut de la connexion.

    Raises:
        ValueError: Si le type de protocole n'est pas supporté.
    """
    plc_type_lower = plc_type.strip().lower()
    if plc_type_lower not in ("opc-ua", "opcua", "ads"):
        raise ValueError("Protocole non supporté. Utiliser 'opc-ua' ou 'ads'.")

    _PLC_STATE["connected_plc"] = {
        "type": plc_type_lower,
        "endpoint": endpoint,
        "connected_at": time.time()
    }
    
    return json.dumps({
        "success": True,
        "message": "Connexion établie avec succès",
        "plc_type": plc_type_lower,
        "endpoint": endpoint
    }, ensure_ascii=False)


@mcp.tool()
def plc_browse(node_id: str = "") -> str:
    """Parcourt les variables et répertoires de l'automate connecté.

    Args:
        node_id: Le chemin du nœud parent à explorer (ex: 'AS6', 'AS6/EPH'). Si vide, explore la racine.

    Returns:
        str: Une chaîne JSON contenant la liste des nœuds enfants et leur type (Folder/Variable).
    """
    clean_node = node_id.replace("\\", "/").strip().strip("/")
    
    # Construction de l'arborescence à partir des tags définis dans _PLC_STATE
    children = {}
    
    for tag_path in _PLC_STATE["tags"].keys():
        if not clean_node:
            # Exploration de la racine (ex: AS6, AS7)
            root_part = tag_path.split("/")[0]
            children[root_part] = "Folder"
        elif tag_path.startswith(clean_node + "/"):
            # Extraction du sous-élément immédiatement après le node_id
            sub_path = tag_path[len(clean_node) + 1:]
            parts = sub_path.split("/")
            name = parts[0]
            if len(parts) > 1:
                children[name] = "Folder"
            else:
                children[name] = "Variable"
                
    result_list = [{"name": name, "type": n_type} for name, n_type in children.items()]
    
    return json.dumps({
        "success": True,
        "parent_node": clean_node or "Root",
        "nodes": sorted(result_list, key=lambda x: (x["type"], x["name"]))
    }, ensure_ascii=False)


@mcp.tool()
def plc_read(tag_path: str) -> str:
    """Lit la valeur d'une variable spécifique sur l'automate.

    Args:
        tag_path: Le chemin complet de la variable (ex: 'AS6/EPH/660C1_EPH_AgitCtrl/Status').

    Returns:
        str: Une chaîne JSON contenant la valeur lue, sa qualité et son horodatage.
    """
    clean_path = tag_path.replace("\\", "/").strip().strip("/")
    
    if clean_path in _PLC_STATE["tags"]:
        value = _PLC_STATE["tags"][clean_path]
        return json.dumps({
            "success": True,
            "tag": clean_path,
            "value": value,
            "quality": "Good",
            "timestamp": time.time()
        }, ensure_ascii=False)
    else:
        # Simulation d'une valeur dynamique pour les variables non définies
        # pour éviter d'échouer sur des requêtes génériques
        simulated_value = 0
        if "active" in clean_path.lower() or "ok" in clean_path.lower():
            simulated_value = False
        return json.dumps({
            "success": True,
            "tag": clean_path,
            "value": simulated_value,
            "quality": "Good_Simulated",
            "timestamp": time.time()
        }, ensure_ascii=False)


@mcp.tool()
def plc_write(tag_path: str, value: str) -> str:
    """Écrit une valeur sur une variable spécifique de l'automate.

    Args:
        tag_path: Le chemin complet de la variable.
        value: La valeur à écrire sous forme de chaîne de caractères (sera convertie dans le type approprié).

    Returns:
        str: Une chaîne JSON confirmant le succès de l'écriture.
    """
    clean_path = tag_path.replace("\\", "/").strip().strip("/")
    
    # Conversion du type heuristique
    converted_value: Any = value
    val_strip = value.strip().lower()
    
    if val_strip in ("true", "1", "active"):
        converted_value = True
    elif val_strip in ("false", "0", "inactive"):
        converted_value = False
    else:
        try:
            if "." in value:
                converted_value = float(value)
            else:
                converted_value = int(value)
        except ValueError:
            # Conserver sous forme de chaîne si ce n'est pas convertible
            pass
            
    _PLC_STATE["tags"][clean_path] = converted_value
    
    return json.dumps({
        "success": True,
        "tag": clean_path,
        "written_value": converted_value,
        "status": "Success"
    }, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run()
