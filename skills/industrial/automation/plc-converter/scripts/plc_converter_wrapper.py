#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PLC Converter Wrapper - Wrapper de compétence pour la conversion de code automate.
Fait le pont vers le convertisseur central tools/plc_converter.py.
"""

import sys
import os
import argparse
from pathlib import Path

def find_workspace_root() -> Path:
    """Recherche le répertoire racine du projet en remontant l'arborescence."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "tools" / "plc_converter.py").exists():
            return parent
    # Fallback par défaut si non trouvé
    return current.parents[5]

# Ajouter le dossier racine au sys.path pour pouvoir importer tools.plc_converter
workspace_root = find_workspace_root()
sys.path.insert(0, str(workspace_root))

try:
    from tools.plc_converter import PLCConverter
except ImportError as e:
    print(f"Erreur : Impossible d'importer le convertisseur central. Assurez-vous d'exécuter le script depuis l'environnement du projet. (Erreur : {e})", file=sys.stderr)
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Wrapper pour le convertisseur de code automate central.")
    parser.add_argument("--input", required=True, help="Chemin du fichier d'entrée (.L5X, .scl, .xml)")
    parser.add_argument("--output", required=True, help="Chemin du fichier de sortie généré")
    parser.add_argument("--from-format", required=True, choices=["rockwell", "siemens", "plcopen"], help="Format d'origine")
    parser.add_argument("--to-format", required=True, choices=["rockwell", "siemens", "plcopen"], help="Format de destination")
    
    args = parser.parse_args()
    
    # Valider l'existence du fichier d'entrée
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erreur : Le fichier d'entrée '{input_path}' n'existe pas.", file=sys.stderr)
        sys.exit(1)
        
    # Créer le dossier de sortie si nécessaire
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Lancement de la conversion de '{args.from_format}' vers '{args.to_format}'...")
    
    converter = PLCConverter()
    
    try:
        if args.from_format == "rockwell" and args.to_format == "siemens":
            converter.l5x_to_siemens_xml(str(input_path), str(output_path))
        elif args.from_format == "rockwell" and args.to_format == "plcopen":
            converter.l5x_to_plcopen_xml(str(input_path), str(output_path))
        elif args.from_format == "siemens" and args.to_format == "rockwell":
            with open(input_path, "r", encoding="utf-8") as f:
                code = f.read()
            converted = converter.convert_st_siemens_to_rockwell(code)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(converted)
            print(f"Conversion Siemens SCL -> Rockwell ST réussie : {output_path}")
        else:
            print(f"Erreur : Conversion depuis '{args.from_format}' vers '{args.to_format}' non supportée par le convertisseur central.", file=sys.stderr)
            sys.exit(1)
            
        print("Opération de conversion terminée avec succès.")
    except Exception as e:
        print(f"Erreur lors de la conversion : {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
