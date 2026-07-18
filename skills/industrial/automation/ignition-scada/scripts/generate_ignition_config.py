#!/usr/bin/env python3
"""Générateur de Configuration de Tags et Scripts Jython pour Ignition SCADA.
Permet de convertir un rapport d'audit EPH/EPH-EM ou un JSON d'instances en structure
de tags importable (.json) dans Ignition, et de générer les scripts Jython de communication.
"""
import sys
import os
import json
import argparse
import re

def parse_audit_report(report_path):
    """Extrait les instances EPH-EM et EPH-EPH depuis un rapport d'audit Markdown."""
    eph_em_exchanges = []
    eph_to_eph_exchanges = []
    
    if not os.path.exists(report_path):
        return eph_em_exchanges, eph_to_eph_exchanges
        
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Extraction des lignes de tableau EPH-EM
    # Ex: | Fichier Source | Instance Source | AS Source | Instance Cible (Tag) | AS Cible | Type d'Échange |
    lines = content.splitlines()
    in_sec1 = False
    in_sec2 = False
    
    for line in lines:
        if "## 1. Échanges Externes" in line:
            in_sec1 = True
            in_sec2 = False
            continue
        elif "## 2. Communications EPH-EM" in line:
            in_sec1 = False
            in_sec2 = True
            continue
        elif line.startswith("##") or line.startswith("# "):
            in_sec1 = False
            in_sec2 = False
            
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 7:
            # Ignorer les en-têtes et lignes de séparation
            clean_part1 = parts[1].strip()
            if clean_part1.startswith("---") or clean_part1.startswith(":-") or clean_part1 == "Fichier Source" or clean_part1 == "N.A." or not clean_part1:
                continue
                
            row_data = {
                "filename": parts[1],
                "source_instance": parts[2],
                "source_as": parts[3],
                "target_instance": parts[4],
                "target_as": parts[5],
                "exchange_type": parts[6]
            }
            
            if in_sec1:
                eph_to_eph_exchanges.append(row_data)
            elif in_sec2:
                eph_em_exchanges.append(row_data)
                
    return eph_em_exchanges, eph_to_eph_exchanges

def generate_ignition_json(eph_em_exchanges, eph_to_eph_exchanges):
    """Génère un dictionnaire JSON structuré compatible avec l'import de tags d'Ignition."""
    # Créer les structures de dossiers par AS
    tags = []
    stations = {}
    
    # Regrouper les instances par AS Source
    for ex in eph_em_exchanges + eph_to_eph_exchanges:
        as_source = ex["source_as"] or "AS_Unknown"
        inst_source = ex["source_instance"]
        
        if as_source not in stations:
            stations[as_source] = {
                "eph_instances": set(),
                "em_instances": set()
            }
            
        stations[as_source]["eph_instances"].add(inst_source)
        
        # Si c'est un échange EPH-EM, la cible est un EM
        if ex["exchange_type"] == "EPH-EM":
            as_target = ex["target_as"] or "AS_Unknown"
            inst_target = ex["target_instance"]
            if as_target not in stations:
                stations[as_target] = {
                    "eph_instances": set(),
                    "em_instances": set()
                }
            stations[as_target]["em_instances"].add(inst_target)
            
    # Générer la liste finale de tags au format Ignition
    for station_name, data in stations.items():
        station_folder = {
            "name": station_name,
            "tagType": "Folder",
            "tags": []
        }
        
        # Dossier pour les instances EPH
        if data["eph_instances"]:
            eph_folder = {
                "name": "EPH",
                "tagType": "Folder",
                "tags": []
            }
            for inst in sorted(data["eph_instances"]):
                eph_folder["tags"].append({
                    "name": inst,
                    "tagType": "UdtInstance",
                    "typeId": "_types_/EPH_Template",
                    "parameters": {
                        "InstanceName": inst
                    }
                })
            station_folder["tags"].append(eph_folder)
            
        # Dossier pour les instances EM
        if data["em_instances"]:
            em_folder = {
                "name": "EM",
                "tagType": "Folder",
                "tags": []
            }
            for inst in sorted(data["em_instances"]):
                em_folder["tags"].append({
                    "name": inst,
                    "tagType": "UdtInstance",
                    "typeId": "_types_/EM_Template",
                    "parameters": {
                        "InstanceName": inst
                    }
                })
            station_folder["tags"].append(em_folder)
            
        tags.append(station_folder)
        
    return {
        "name": "Actemium_EPH_Import",
        "tagType": "Folder",
        "tags": tags
    }

def generate_jython_script(eph_em_exchanges):
    """Génère un script Jython standardisé pour la communication inter-tags."""
    script_lines = [
        "# -*- coding: utf-8 -*-",
        "\"\"\"Script de synchronisation généré automatiquement par l'Agent Actemium.",
        "Met en œuvre des lectures et écritures groupées conformes à Ignition 8.x.",
        "\"\"\"",
        "import sys",
        "",
        "def sync_eph_em_communications():",
        "    logger = system.util.getLogger(\"Actemium_EPH_Sync\")",
        "    logger.info(\"Début de la synchronisation EPH-EM...\")",
        "    ",
        "    # 1. Regrouper les chemins pour la lecture bloquante",
        "    # (Lecture de l'état des phases EPH source)",
        "    read_paths = ["
    ]
    
    # Extraire des chemins de lecture uniques
    unique_sources = sorted(list(set(ex["source_instance"] for ex in eph_em_exchanges)))
    for src in unique_sources:
        # Résoudre le dossier AS heuristique de la source
        m = re.match(r'^(\d+)', src.split('_')[0])
        as_dir = f"AS{m.group(1)}" if m else "AS_Unknown"
        script_lines.append(f"        \"[default]{as_dir}/EPH/{src}/Status\",")
        
    script_lines.extend([
        "    ]",
        "    ",
        "    results = system.tag.readBlocking(read_paths)",
        "    eph_status_map = {}",
        "    for idx, path in enumerate(read_paths):",
        "        # Extraire le nom d'instance depuis le chemin",
        "        inst_name = path.split('/')[-2]",
        "        if results[idx].quality.isGood():",
        "            eph_status_map[inst_name] = results[idx].value",
        "        else:",
        "            eph_status_map[inst_name] = None",
        "            logger.warn(\"Échec de lecture pour le tag : \" + path)",
        "            ",
        "    # 2. Regrouper les écritures vers les équipements cibles (EM)",
        "    write_paths = []",
        "    write_values = []",
        ""
    ])
    
    # Établir les écritures basées sur les corrélations d'audit
    for ex in eph_em_exchanges:
        src = ex["source_instance"]
        target = ex["target_instance"]
        as_tgt = ex["target_as"]
        
        script_lines.extend([
            f"    # Liaison : {src} -> {target}",
            f"    val_{src} = eph_status_map.get(\"{src}\")",
            f"    if val_{src} is not None:",
            f"        write_paths.append(\"[default]{as_tgt}/EM/{target}/Command\")",
            f"        write_values.append(val_{src})",
            ""
        ])
        
    script_lines.extend([
        "    # 3. Écriture groupée des commandes vers les EM cibles",
        "    if write_paths:",
        "        status = system.tag.writeBlocking(write_paths, write_values)",
        "        for idx, stat in enumerate(status):",
        "            if not stat.isGood():",
        "                logger.warn(\"Échec d'écriture pour l'équipement : \" + write_paths[idx])",
        "                ",
        "    logger.info(\"Fin de la synchronisation EPH-EM.\")"
    ])
    
    return "\n".join(script_lines)

def main():
    parser = argparse.ArgumentParser(description="Générateur de configurations Ignition SCADA.")
    parser.add_argument("--audit-report", required=True, help="Chemin vers le rapport d'audit MD consolidé")
    parser.add_argument("--out-tags", help="Fichier de sortie pour l'import JSON de tags (ex: tags.json)")
    parser.add_argument("--out-script", help="Fichier de sortie pour le script Jython (ex: sync_script.py)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.audit_report):
        print(f"Erreur: Rapport d'audit introuvable à l'adresse : {args.audit_report}")
        sys.exit(1)
        
    print(f"Analyse du rapport d'audit : {args.audit_report}...")
    eph_em, eph_to_eph = parse_audit_report(args.audit_report)
    print(f"Trouvé {len(eph_em)} relations EPH-EM et {len(eph_to_eph)} relations EPH-EPH.")
    
    if args.out_tags:
        tags_config = generate_ignition_json(eph_em, eph_to_eph)
        with open(args.out_tags, "w", encoding="utf-8") as f:
            json.dump(tags_config, f, ensure_ascii=False, indent=2)
        print(f"Configuration d'import de tags créée avec succès dans : {args.out_tags}")
        
    if args.out_script:
        jython_script = generate_jython_script(eph_em)
        with open(args.out_script, "w", encoding="utf-8") as f:
            f.write(jython_script)
        print(f"Script de synchronisation Jython créé avec succès dans : {args.out_script}")

if __name__ == "__main__":
    main()
