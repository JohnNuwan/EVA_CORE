#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PLC Code Converter - Outil de conversion multi-plateforme bidirectionnel.
Permet de traduire du code Structured Text et des structures XML entre :
- Rockwell Automation (L5X / Logix Designer)
- Siemens (SCL / TIA Portal)
- PLCopen XML (CODESYS / TwinCAT)

Utilise la bibliothèque partagée ``actemium-l5x-core``.
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

from actemium.l5x.converter.st_converter import STConverter
from actemium.l5x.converter.type_mapper import TypeMapper
from actemium.l5x.converter.plcopen import PLCopenConverter
from actemium.l5x.parser.aoi import AOIParser


class PLCConverter:
    """Convertisseur bidirectionnel de code PLC multi-plateforme.

    Délègue les opérations à la bibliothèque ``actemium-l5x-core``
    tout en conservant l'API publique existante.
    """

    def __init__(self):
        self.st_converter = STConverter()
        self.type_mapper = TypeMapper()
        # Mapping de types préservé pour compatibilité ascendante
        self.type_mapping = {
            "rockwell_to_siemens": self.type_mapper.ROCKWELL_TO_SIEMENS,
            "siemens_to_rockwell": self.type_mapper.SIEMENS_TO_ROCKWELL,
        }

    def convert_st_rockwell_to_siemens(self, st_code: str, local_vars: list = None) -> str:
        """Convertit du Structured Text Rockwell vers Siemens SCL.

        Args:
            st_code: Code Structured Text Rockwell.
            local_vars: Liste des variables locales à préfixer avec '#'.

        Returns:
            Code Siemens SCL converti.
        """
        return self.st_converter.rockwell_to_siemens(st_code, local_vars or [])

    def convert_st_siemens_to_rockwell(self, scl_code: str) -> str:
        """Convertit du Siemens SCL vers Rockwell Structured Text.

        Args:
            scl_code: Code Siemens SCL.

        Returns:
            Code Rockwell ST converti.
        """
        return self.st_converter.siemens_to_rockwell(scl_code)

    def l5x_to_siemens_xml(self, l5x_path: str, output_path: str):
        """Convertit un fichier L5X Rockwell en format Siemens SCL source.

        Args:
            l5x_path: Chemin du fichier L5X.
            output_path: Chemin du fichier SCL de sortie.
        """
        parser = AOIParser(l5x_path)
        if not parser.parse():
            raise ValueError(f"Impossible de parser {l5x_path}")

        aois = parser.parse_aois()
        scl_blocks = []

        for aoi in aois:
            scl_blocks.append(f'FUNCTION_BLOCK "{aoi.name}"')
            scl_blocks.append("{ S7_Optimized_Access := 'TRUE' }")
            scl_blocks.append(f"VERSION : {aoi.revision}")

            inputs = [p for p in aoi.parameters if p.usage.name == "INPUT"]
            outputs = [p for p in aoi.parameters if p.usage.name == "OUTPUT"]

            if inputs:
                scl_blocks.append("   VAR_INPUT")
                for p in inputs:
                    mapped = self.type_mapper.map_to_siemens(p.data_type)
                    scl_blocks.append(f"      {p.name} : {mapped};")
                scl_blocks.append("   END_VAR")

            if outputs:
                scl_blocks.append("   VAR_OUTPUT")
                for p in outputs:
                    mapped = self.type_mapper.map_to_siemens(p.data_type)
                    scl_blocks.append(f"      {p.name} : {mapped};")
                scl_blocks.append("   END_VAR")

            if aoi.local_tags:
                scl_blocks.append("   VAR")
                for t in aoi.local_tags:
                    mapped = self.type_mapper.map_to_siemens(t.data_type)
                    scl_blocks.append(f"      {t.name} : {mapped};")
                scl_blocks.append("   END_VAR")

            scl_blocks.append("BEGIN")
            if aoi.st_content:
                local_names = [p.name for p in inputs + outputs] + [t.name for t in aoi.local_tags]
                converted = self.st_converter.rockwell_to_siemens(aoi.st_content, local_names)
                scl_blocks.append(converted)
            scl_blocks.append("END_FUNCTION_BLOCK")
            scl_blocks.append("")

        output_path = Path(output_path)
        output_path.write_text("\n".join(scl_blocks), encoding="utf-8")
        print(f"Successfully converted L5X to Siemens SCL: {output_path}")

    def l5x_to_plcopen_xml(self, l5x_path: str, output_path: str):
        """Convertit un fichier Rockwell L5X en format universel PLCopen XML.

        Délègue à ``PLCopenConverter.l5x_to_plcopen()``.

        Args:
            l5x_path: Chemin du fichier L5X.
            output_path: Chemin du fichier PLCopen XML de sortie.
        """
        converter = PLCopenConverter()
        converter.l5x_to_plcopen(l5x_path, output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Convertisseur bidirectionnel de code et fichiers XML automate."
    )
    parser.add_argument("--input", required=True, help="Chemin du fichier d'entree (.L5X, .scl, .xml)")
    parser.add_argument("--output", required=True, help="Chemin du fichier de sortie genere")
    parser.add_argument("--from-format", required=True,
                        choices=["rockwell", "siemens", "plcopen"],
                        help="Format de depart")
    parser.add_argument("--to-format", required=True,
                        choices=["rockwell", "siemens", "plcopen"],
                        help="Format de destination")

    args = parser.parse_args()
    converter = PLCConverter()

    if args.from_format == "rockwell" and args.to_format == "siemens":
        converter.l5x_to_siemens_xml(args.input, args.output)
    elif args.from_format == "rockwell" and args.to_format == "plcopen":
        converter.l5x_to_plcopen_xml(args.input, args.output)
    elif args.from_format == "siemens" and args.to_format == "rockwell":
        try:
            code = Path(args.input).read_text(encoding="utf-8")
            converted = converter.convert_st_siemens_to_rockwell(code)
            Path(args.output).write_text(converted, encoding="utf-8")
            print(f"Successfully converted Siemens SCL to Rockwell ST: {args.output}")
        except Exception as e:
            print(f"Error converting SCL: {e}")
            sys.exit(1)
    else:
        print(f"Error: Conversion from '{args.from_format}' to '{args.to_format}' not yet implemented.")
        sys.exit(1)


if __name__ == "__main__":
    main()
