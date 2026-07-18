#!/usr/bin/env python3
"""Génère un mapping PLC ↔ SCADA ↔ MES à partir d'un contrat standard simple."""

import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: generate_mapping.py <input.json> <output.md>")
        return 1

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    data = json.loads(input_path.read_text(encoding="utf-8"))

    lines = ["# Mapping PLC ↔ SCADA ↔ MES", ""]
    for eq in data.get("equipment", []):
        name = eq.get("name", "Equipment")
        lines.append(f"## {name}")
        lines.append("")
        lines.append("| Domaine | Champ | Valeur |")
        lines.append("|---|---|---|")
        for domain in ("plc", "scada", "mes"):
            for key, value in eq.get(domain, {}).items():
                lines.append(f"| {domain.upper()} | {key} | {value} |")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
