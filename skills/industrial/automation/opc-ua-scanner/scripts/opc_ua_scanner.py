#!/usr/bin/env python3
"""Script d'exploration OPC UA (Dynamic Scanner) pour Actemium Agent.
Permet d'explorer l'espace d'adressage d'un serveur OPC UA local ou distant
pour valider la présence de variables automates (Tags EPH / EM).
"""
import sys
import os
import asyncio
import argparse
import json

# Installation dynamique de asyncua si absent
try:
    import asyncua
except ImportError:
    print("Module 'asyncua' non détecté. Installation en cours...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncua"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import asyncua
    except Exception as e:
        print(f"Erreur d'installation de asyncua : {e}")
        sys.exit(1)

from asyncua import Client

async def browse_recursive(node, depth=0, max_depth=3, filter_str=None):
    """Parcourt récursivement l'espace d'adressage OPC UA."""
    nodes = []
    if depth > max_depth:
        return nodes
        
    try:
        children = await node.get_children()
        for child in children:
            name = await child.get_display_name()
            name_text = name.Text if name else ""
            node_id = str(child.nodeid)
            
            # Récupérer la classe du nœud (Variable, Object, Method...)
            node_class = await child.get_node_class()
            node_class_str = str(node_class.name) if node_class else "Unknown"
            
            val = None
            if node_class_str == "Variable":
                try:
                    val = await child.get_value()
                    # Rendre les objets non sérialisables JSON lisibles
                    if not isinstance(val, (int, float, str, bool, list, dict, type(None))):
                        val = str(val)
                except Exception:
                    pass
            
            match = True
            if filter_str:
                match = (filter_str.lower() in name_text.lower()) or (filter_str.lower() in node_id.lower())
                
            if match:
                nodes.append({
                    "name": name_text,
                    "node_id": node_id,
                    "class": node_class_str,
                    "value": val,
                    "depth": depth
                })
                
            # Parcourir les enfants si c'est un objet/dossier
            if node_class_str in ("Object", "Folder"):
                child_nodes = await browse_recursive(child, depth + 1, max_depth, filter_str)
                nodes.extend(child_nodes)
                
    except Exception:
        pass
        
    return nodes

async def run_scan(url, max_depth, filter_str):
    result = {
        "server_url": url,
        "connected": False,
        "nodes_found": [],
        "status": "Unknown"
    }
    
    client = Client(url=url)
    try:
        await client.connect()
        result["connected"] = True
        result["status"] = "Connected successfully"
        
        # Obtenir le nœud racine ou le nœud Objects
        objects_node = client.get_objects_node()
        nodes = await browse_recursive(objects_node, depth=0, max_depth=max_depth, filter_str=filter_str)
        result["nodes_found"] = nodes
        result["status"] += f". Browsed Objects node, found {len(nodes)} matches."
        
    except Exception as e:
        result["status"] = f"Connection / Scan failed: {str(e)}"
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass
            
    return result

def main():
    parser = argparse.ArgumentParser(description="Explorateur et validateur OPC UA.")
    parser.add_argument("--url", default="opc.tcp://localhost:4840", help="URL du serveur OPC UA (defaut: opc.tcp://localhost:4840)")
    parser.add_argument("--depth", type=int, default=3, help="Profondeur maximale d'exploration (defaut: 3)")
    parser.add_argument("--filter", help="Filtre (insensible à la casse) sur les noms de nœuds ou NodeID")
    
    args = parser.parse_args()
    
    # Exécution asynchrone
    try:
        report = asyncio.run(run_scan(args.url, args.depth, args.filter))
    except Exception as e:
        report = {
            "server_url": args.url,
            "connected": False,
            "nodes_found": [],
            "status": f"Execution error: {str(e)}"
        }
        
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
