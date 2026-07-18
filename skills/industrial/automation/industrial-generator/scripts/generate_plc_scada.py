#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'assistance pour le Générateur d'Automates Actemium.
Permet d'exécuter l'analyse et la génération de code Siemens/Rockwell/SCADA/Grafcet depuis la ligne de commande.
"""

import os
import sys
import argparse
import json
from pathlib import Path

ORIG_CWD = os.getcwd()

# Définir le chemin absolu de Projet_Automate et changer le répertoire de travail
PROJET_DIR = Path("C:/Users/john.moncel/Desktop/Damien_Programme/DevAuomate/DevAutomate/Projet_Automate")
if not PROJET_DIR.exists():
    print(f"Erreur : Le répertoire {PROJET_DIR} n'existe pas.", file=sys.stderr)
    sys.exit(1)

# Se placer dans le répertoire du projet pour la résolution des templates
os.chdir(str(PROJET_DIR))
sys.path.insert(0, str(PROJET_DIR))

try:
    from app.parser import parse_full_excel, parse_json_equipments
    from app.generator import generate_plc_block
    from app.persistence import save_state, load_state
    from app.models.engine import Equipment, PLCConfig
except ImportError as e:
    print(f"Erreur d'importation des modules de Projet_Automate : {e}", file=sys.stderr)
    sys.exit(1)


def cmd_import(args):
    """Charge un fichier Excel ou JSON et sauvegarde son état."""
    path = Path(args.file)
    if not path.is_absolute():
        # Si le chemin n'est pas absolu, on le cherche par rapport au dossier d'origine
        path = Path(args.orig_cwd) / path

    if not path.exists():
        print(f"Erreur : Le fichier {path} n'existe pas.", file=sys.stderr)
        return 1

    print(f"Analyse du fichier {path}...")
    try:
        if path.suffix.lower() == ".json":
            config, equipments = parse_json_equipments(str(path))
        else:
            config, equipments = parse_full_excel(str(path))

        save_state(config, equipments)
        print(f"Succès : {len(equipments)} équipements chargés.")
        print(f"Type Automate : {config.automate_type}")
        return 0
    except Exception as e:
        print(f"Erreur lors de l'analyse : {e}", file=sys.stderr)
        return 1


def cmd_list(args):
    """Affiche la liste des équipements chargés."""
    config, equipments = load_state()
    if not config:
        print("Aucun projet chargé en mémoire. Utilisez d'abord la commande 'import'.")
        return 0

    print(f"--- Projet PLC : {config.project_name} ---")
    print(f"Automate : {config.automate_type} | Supervision : {config.supervision_type}")
    print(f"Total équipements : {len(equipments)}")

    by_cat = {}
    for eq in equipments:
        by_cat[eq.category] = by_cat.get(eq.category, 0) + 1

    print("\nÉquipements par catégorie :")
    for cat, count in sorted(by_cat.items()):
        print(f"  - {cat} : {count}")
    return 0


def cmd_update(args):
    """Met à jour un équipement spécifique."""
    config, equipments = load_state()
    if not config:
        print("Erreur : Aucun projet chargé.", file=sys.stderr)
        return 1

    target = None
    for eq in equipments:
        if eq.category.upper() == args.category.upper() and eq.mnemo.lower() == args.mnemo.lower():
            target = eq
            break

    if not target:
        print(f"Erreur : Équipement '{args.mnemo}' introuvable dans '{args.category}'.", file=sys.stderr)
        return 1

    # Appliquer les modifications
    if args.desc:
        target.description = args.desc
    if args.version:
        target.version = args.version

    # Propriétés additionnelles
    if args.props:
        for p in args.props:
            if "=" in p:
                k, v = p.split("=", 1)
                # Tenter de convertir en float/int si possible
                try:
                    if "." in v:
                        val = float(v)
                    else:
                        val = int(v)
                except ValueError:
                    val = v
                target.properties[k] = val

    save_state(config, equipments)
    print(f"Équipement {args.mnemo} mis à jour avec succès.")
    return 0


def cmd_update_batch(args):
    """Met à jour une liste d'équipements en lot."""
    config, equipments = load_state()
    if not config:
        print("Erreur : Aucun projet chargé.", file=sys.stderr)
        return 1

    updated_count = 0
    for eq in equipments:
        if eq.category.upper() == args.category.upper():
            if not args.prefix or eq.mnemo.lower().startswith(args.prefix.lower()):
                if args.desc:
                    # Remplacement de pattern si désiré, ou description générique
                    eq.description = args.desc.replace("{mnemo}", eq.mnemo)
                if args.version:
                    eq.version = args.version
                if args.props:
                    for p in args.props:
                        if "=" in p:
                            k, v = p.split("=", 1)
                            # Remplacement de pattern de valeur
                            v_resolved = v.replace("{mnemo}", eq.mnemo)
                            try:
                                if "." in v_resolved:
                                    val = float(v_resolved)
                                else:
                                    val = int(v_resolved)
                            except ValueError:
                                val = v_resolved
                            eq.properties[k] = val
                updated_count += 1

    if updated_count > 0:
        save_state(config, equipments)
        print(f"Succès : {updated_count} équipements de type '{args.category}' mis à jour.")
    else:
        print("Aucun équipement ne correspond aux critères de mise à jour.", file=sys.stderr)
    return 0


def cmd_generate_plc(args):
    """Génère le code PLC d'une catégorie."""
    config, equipments = load_state()
    if not config:
        print("Erreur : Aucun projet chargé.", file=sys.stderr)
        return 1

    # Surcharger temporairement le type d'automate si spécifié
    auto_type = args.automate_type or config.automate_type or "Siemens_STEP7"

    print(f"Génération du code PLC pour la catégorie '{args.category}' ({auto_type})...")
    code = generate_plc_block(args.category.upper(), equipments, auto_type)
    if not code:
        print(f"Erreur : Aucun équipement ou template trouvé pour '{args.category}'.", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = Path(args.orig_cwd) / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8-sig") as f:
        f.write(code)

    print(f"Fichier de code généré avec succès : {out_path}")
    return 0


def cmd_generate_scada(args):
    """Génère les configurations SCADA (Ignition, InTouch, WinCC Unified)."""
    config, equipments = load_state()
    if not config:
        print("Erreur : Aucun projet chargé.", file=sys.stderr)
        return 1

    fmt = args.format.lower()
    content = ""
    print(f"Génération SCADA au format {fmt}...")

    if fmt == "ignition":
        from app.scada_generator import generate_ignition_perspective
        content = generate_ignition_perspective(equipments)
    elif fmt == "intouch":
        from app.scada_generator import generate_intouch_csv
        content = generate_intouch_csv(equipments, config)
    elif fmt == "wincc":
        from app.scada_generator import generate_wincc_unified_tags
        content = generate_wincc_unified_tags(equipments, config)
    else:
        print(f"Format SCADA inconnu : {fmt}. Choisissez parmi: ignition, intouch, wincc", file=sys.stderr)
        return 1

    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = Path(args.orig_cwd) / out_path

    out_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "w"
    encoding = "utf-8-sig" if fmt in ["intouch", "wincc"] else "utf-8"
    
    with open(out_path, mode, encoding=encoding) as f:
        f.write(content)

    print(f"Fichier SCADA généré avec succès : {out_path}")
    return 0


def cmd_convert_udt(args):
    """Convertit un UDT Ignition JSON en type Siemens (AWL ou SCL)."""
    path = Path(args.file)
    if not path.is_absolute():
        path = Path(args.orig_cwd) / path

    if not path.exists():
        print(f"Erreur : Le fichier {path} n'existe pas.", file=sys.stderr)
        return 1

    try:
        with open(path, "r", encoding="utf-8") as f:
            udt_data = json.load(f)

        from app.udt_converter import convert_udt_to_siemens
        code = convert_udt_to_siemens(udt_data, args.format)

        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = Path(args.orig_cwd) / out_path

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8-sig") as f:
            f.write(code)

        print(f"UDT converti avec succès : {out_path}")
        return 0
    except Exception as e:
        print(f"Erreur lors de la conversion UDT : {e}", file=sys.stderr)
        return 1


def cmd_convert_grafcet(args):
    """Convertit un diagramme Grafcet Mermaid (flowchart ou stateDiagram) en code Siemens SCL."""
    path = Path(args.file)
    if not path.is_absolute():
        path = Path(args.orig_cwd) / path

    if not path.exists():
        print(f"Erreur : Le fichier {path} n'existe pas.", file=sys.stderr)
        return 1

    try:
        with open(path, "r", encoding="utf-8") as f:
            mermaid_code = f.read()

        from app.grafcet_parser import convert_mermaid_to_scl
        scl_code = convert_mermaid_to_scl(mermaid_code)

        out_path = Path(args.output)
        if not out_path.is_absolute():
            out_path = Path(args.orig_cwd) / out_path

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8-sig") as f:
            f.write(scl_code)

        print(f"Grafcet converti avec succès en SCL : {out_path}")
        return 0
    except Exception as e:
        print(f"Erreur lors de la conversion du Grafcet : {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description="CLI Helper pour le Générateur d'Automates.")
    parser.add_argument("--orig-cwd", default=ORIG_CWD, help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: import
    parser_import = subparsers.add_parser("import", help="Charge une configuration Excel ou JSON.")
    parser_import.add_argument("file", help="Chemin du fichier Excel (.xlsm/.xlsx) ou JSON (.json).")
    parser_import.set_defaults(func=cmd_import)

    # Command: list
    parser_list = subparsers.add_parser("list", help="Affiche la liste des équipements chargés.")
    parser_list.set_defaults(func=cmd_list)

    # Command: update
    parser_update = subparsers.add_parser("update", help="Met à jour un équipement spécifique.")
    parser_update.add_argument("category", help="Catégorie (ex: MVAR).")
    parser_update.add_argument("mnemo", help="Mnémonique unique (ex: 110101-BLP).")
    parser_update.add_argument("--desc", help="Nouvelle description.")
    parser_update.add_argument("--version", help="Nouvelle version.")
    parser_update.add_argument("--props", nargs="+", help="Clé=Valeur additionnelles.")
    parser_update.set_defaults(func=cmd_update)

    # Command: update-batch
    parser_batch = subparsers.add_parser("update-batch", help="Met à jour des équipements en lot.")
    parser_batch.add_argument("category", help="Catégorie (ex: MVAR).")
    parser_batch.add_argument("--prefix", default="", help="Optionnel: Préfixe du mnémonique pour filtrer.")
    parser_batch.add_argument("--desc", help="Nouvelle description (utilise {mnemo} pour le mnémonique).")
    parser_batch.add_argument("--version", help="Nouvelle version.")
    parser_batch.add_argument("--props", nargs="+", help="Clé=Valeur additionnelles (accepte {mnemo}).")
    parser_batch.set_defaults(func=cmd_update_batch)

    # Command: generate-plc
    parser_gplc = subparsers.add_parser("generate-plc", help="Génère le code source automate.")
    parser_gplc.add_argument("category", help="Catégorie (ex: MVAR).")
    parser_gplc.add_argument("output", help="Chemin du fichier de sortie généré.")
    parser_gplc.add_argument("--automate-type", choices=["Siemens_STEP7", "Siemens_TIA"], help="Surcharge du type d'automate.")
    parser_gplc.set_defaults(func=cmd_generate_plc)

    # Command: generate-scada
    parser_gscada = subparsers.add_parser("generate-scada", help="Génère le fichier de configuration SCADA.")
    parser_gscada.add_argument("format", choices=["ignition", "intouch", "wincc"], help="Format de sortie.")
    parser_gscada.add_argument("output", help="Chemin du fichier de sortie généré.")
    parser_gscada.set_defaults(func=cmd_generate_scada)

    # Command: convert-udt
    parser_udt = subparsers.add_parser("convert-udt", help="Convertit un UDT Ignition JSON en type Siemens.")
    parser_udt.add_argument("file", help="Chemin du fichier JSON UDT.")
    parser_udt.add_argument("output", help="Chemin du fichier Siemens généré.")
    parser_udt.add_argument("--format", choices=["scl", "awl"], default="scl", help="Format de sortie (default: scl).")
    parser_udt.set_defaults(func=cmd_convert_udt)

    # Command: convert-grafcet
    parser_grafcet = subparsers.add_parser("convert-grafcet", help="Convertit un Grafcet Mermaid en code Siemens SCL.")
    parser_grafcet.add_argument("file", help="Chemin du fichier Mermaid (.txt/.mmd).")
    parser_grafcet.add_argument("output", help="Chemin du fichier Siemens SCL généré.")
    parser_grafcet.set_defaults(func=cmd_convert_grafcet)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
