#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script d'assistance pour le gestionnaire OKF (Open Knowledge Format).

Fournit des utilitaires en ligne de commande pour vérifier, convertir,
importer et exporter des documents de connaissances conformes au format Google OKF.
"""

import os
import sys
import argparse
import re
import zipfile
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

# Force standard streams to use UTF-8 to prevent UnicodeEncodeError on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except (AttributeError, IOError):
        pass


def parse_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extrait l'en-tête YAML frontmatter et le corps d'un fichier Markdown.

    Args:
        content: Le contenu textuel brut du fichier Markdown.

    Returns:
        Un tuple (metadata, body) contenant le dictionnaire de métadonnées
        et le reste du document.
    """
    lines = content.splitlines()
    if not lines or not lines[0].strip() == "---":
        return {}, content

    frontmatter_lines = []
    body_lines = []
    in_frontmatter = True

    for line in lines[1:]:
        if in_frontmatter:
            if line.strip() == "---":
                in_frontmatter = False
            else:
                frontmatter_lines.append(line)
        else:
            body_lines.append(line)

    # Analyse des paires clé-valeur YAML simplifiées
    metadata = {}
    current_key = None
    for line in frontmatter_lines:
        if not line.strip():
            continue
        # Ligne de commentaire
        if line.strip().startswith("#"):
            continue

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            if val.startswith("[") and val.endswith("]"):
                # Liste de valeurs inline [val1, val2]
                val_list = [item.strip().strip("'\"") for item in val[1:-1].split(",") if item.strip()]
                metadata[key] = val_list
            else:
                metadata[key] = val.strip("'\"")
            current_key = key
        elif line.strip().startswith("-") and current_key:
            # Ligne de liste YAML sous forme de tiret
            item = line.strip()[1:].strip().strip("'\"")
            if not isinstance(metadata[current_key], list):
                metadata[current_key] = []
            metadata[current_key].append(item)

    return metadata, "\n".join(body_lines)


def serialize_frontmatter(metadata: Dict[str, Any]) -> str:
    """Sérialise un dictionnaire en en-tête YAML frontmatter.

    Args:
        metadata: Dictionnaire contenant les métadonnées.

    Returns:
        Une chaîne de caractères formatée en frontmatter YAML entourée de ---.
    """
    lines = ["---"]
    for k, v in metadata.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(v)}]")
        else:
            val_str = str(v)
            if ":" in val_str or "#" in val_str or "@" in val_str or val_str.startswith('"'):
                lines.append(f'{k}: "{val_str}"')
            else:
                lines.append(f"{k}: {val_str}")
    lines.append("---")
    return "\n".join(lines)


def check_skill_compliance(skill_md_path: Path) -> Dict[str, Any]:
    """Analyse un fichier de compétence pour évaluer sa conformité Google OKF.

    Args:
        skill_md_path: Le chemin absolu vers le fichier SKILL.md.

    Returns:
        Un dictionnaire résumant l'état de conformité et les champs manquants.
    """
    try:
        content = skill_md_path.read_text(encoding="utf-8")
        metadata, _ = parse_frontmatter(content)
    except Exception as e:
        return {"compliant": False, "error": f"Impossible de lire le fichier: {e}"}

    missing_fields = []
    # Champs requis par la norme Google OKF v0.1
    required = ["type", "title", "description", "tags"]
    
    for field in required:
        if field not in metadata:
            missing_fields.append(field)

    # Validation additionnelle du type
    type_val = metadata.get("type", "")
    if "type" not in missing_fields and type_val != "skill":
        missing_fields.append("type (valeur incorrecte, doit être 'skill')")

    return {
        "compliant": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "metadata": metadata,
    }


def resolve_workspace(orig_cwd_str: str) -> Tuple[Path, Path, Path]:
    """Résout le répertoire d'origine, la racine de l'espace de travail et le dossier des compétences.

    Args:
        orig_cwd_str: Le répertoire courant passé en argument.

    Returns:
        Un tuple (orig_cwd, workspace_root, skills_dir) de type Path.
    """
    orig_cwd = Path(orig_cwd_str)
    skills_dir = orig_cwd / "skills"
    workspace_root = orig_cwd
    if not skills_dir.exists():
        script_workspace = Path(__file__).resolve().parents[4]
        if (script_workspace / "skills").exists():
            skills_dir = script_workspace / "skills"
            workspace_root = script_workspace
    return orig_cwd, workspace_root, skills_dir


def cmd_check(args):
    """Exécute l'analyse de conformité sur toutes les compétences du dépôt."""
    orig_cwd, workspace_root, skills_dir = resolve_workspace(args.orig_cwd)
    if not skills_dir.exists():
        print(f"Erreur : Le répertoire des compétences {skills_dir} n'existe pas.", file=sys.stderr)
        return 1

    print(f"Lancement de l'audit de conformité Google OKF dans: {skills_dir}\n")
    compliant_count = 0
    non_compliant_count = 0

    for root, _, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_path = Path(root) / "SKILL.md"
            rel_path = skill_path.relative_to(workspace_root)
            result = check_skill_compliance(skill_path)
            
            if result.get("error"):
                print(f"❌ {rel_path} : Erreur d'analyse ({result['error']})")
                non_compliant_count += 1
            elif result["compliant"]:
                print(f"✅ {rel_path} : Conforme")
                compliant_count += 1
            else:
                fields_str = ", ".join(result["missing_fields"])
                print(f"⚠️ {rel_path} : Non conforme (Champs manquants: {fields_str})")
                non_compliant_count += 1

    print(f"\n--- Bilan de l'audit ---")
    print(f"Compétences conformes   : {compliant_count}")
    print(f"Compétences non-conformes : {non_compliant_count}")
    return 0 if non_compliant_count == 0 else 1


def cmd_convert(args):
    """Met en conformité automatique les en-têtes de compétences."""
    orig_cwd, workspace_root, skills_dir = resolve_workspace(args.orig_cwd)
    if not skills_dir.exists():
        print(f"Erreur : Le répertoire des compétences {skills_dir} n'existe pas.", file=sys.stderr)
        return 1

    updated_count = 0
    for root, _, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_path = Path(root) / "SKILL.md"
            result = check_skill_compliance(skill_path)
            
            if not result.get("compliant") and not result.get("error"):
                metadata = result["metadata"]
                # Remplir les champs manquants
                if "type" not in metadata or metadata["type"] != "skill":
                    metadata["type"] = "skill"
                if "title" not in metadata:
                    # Titre par défaut basé sur le dossier parent
                    metadata["title"] = skill_path.parent.name.replace("-", " ").capitalize()
                if "description" not in metadata:
                    # Utiliser le nom comme description par défaut
                    metadata["description"] = f"Compétence de gestion {skill_path.parent.name}."
                if "tags" not in metadata:
                    # Récupérer les tags depuis helios metadata si présents
                    helios_meta = metadata.get("metadata", {})
                    if isinstance(helios_meta, dict) and "helios" in helios_meta:
                        metadata["tags"] = helios_meta["helios"].get("tags", ["general"])
                    else:
                        metadata["tags"] = ["general"]

                if args.write:
                    # Lire le corps original du markdown
                    content = skill_path.read_text(encoding="utf-8")
                    _, body = parse_frontmatter(content)
                    
                    # Sérialiser le nouveau frontmatter et écrire
                    new_frontmatter = serialize_frontmatter(metadata)
                    skill_path.write_text(f"{new_frontmatter}\n{body}", encoding="utf-8")
                    print(f"💾 Mis à jour : {skill_path.relative_to(workspace_root)}")
                    updated_count += 1
                else:
                    print(f"🔍 [Simulation] Devrait mettre à jour : {skill_path.relative_to(workspace_root)}")

    if updated_count > 0:
        print(f"\nSuccès : {updated_count} fichiers SKILL.md mis en conformité.")
    elif not args.write:
        print("\nSimulation terminée. Utilisez l'option --write pour appliquer les modifications.")
    else:
        print("\nToutes les compétences sont déjà conformes ou aucun fichier n'a été modifié.")
    return 0


def calculate_sha256(file_path: Path) -> str:
    """Calcule le checksum SHA256 d'un fichier.

    Args:
        file_path: Le chemin du fichier.

    Returns:
        Le hash SHA256 sous forme de chaîne hexadécimale.
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def cmd_export(args):
    """Exporte toutes les fiches de connaissances au format ZIP bundle OKF."""
    orig_cwd, workspace_root, skills_dir = resolve_workspace(args.orig_cwd)
    out_path = Path(args.output)
    if not out_path.is_absolute():
        out_path = orig_cwd / out_path

    if not skills_dir.exists():
        print(f"Erreur : Le répertoire des compétences {skills_dir} n'existe pas.", file=sys.stderr)
        return 1

    print(f"Exportation des connaissances au format ZIP vers: {out_path}...")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Récolter toutes les enveloppes ACS présentes dans l'espace de travail
        delegations = []
        for root, _, files in os.walk(workspace_root):
            # Éviter de parcourir les répertoires d'outils, virtuels ou de cache
            if any(ignored in root for ignored in [".git", ".venv", ".pytest_cache", "__pycache__"]):
                continue
            if "acs_envelope.json" in files:
                acs_path = Path(root) / "acs_envelope.json"
                try:
                    acs_data = json.loads(acs_path.read_text(encoding="utf-8"))
                    if acs_data.get("protocol") == "ACS/1.0" and "envelope" in acs_data:
                        delegations.append({
                            "path": acs_path,
                            "data": acs_data["envelope"]
                        })
                except Exception:
                    pass

        def find_writer_agent(file_path: Path) -> Optional[str]:
            """Trouve l'ID du sous-agent rédacteur en remontant l'arborescence."""
            current = file_path.parent
            while current != current.parent and current.parts:
                for dl in delegations:
                    if dl["path"].parent == current:
                        return dl["data"]["delegate"]["subagent_id"]
                current = current.parent
            return None

        manifest = []
        with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(skills_dir):
                for f in files:
                    if f.endswith(".md") or f.endswith(".py"):
                        file_path = Path(root) / f
                        arcname = file_path.relative_to(skills_dir)
                        zipf.write(file_path, arcname)
                        
                        # Calculer le SHA256 pour la provenance
                        sha256_val = calculate_sha256(file_path)
                        entry = {
                            "file": str(arcname).replace("\\", "/"),
                            "sha256": sha256_val
                        }
                        
                        # Déterminer le sous-agent rédacteur si présent
                        writer_id = find_writer_agent(file_path)
                        if writer_id:
                            entry["written_by"] = writer_id
                            
                        manifest.append(entry)
            
            # Reconstruire la liste de filiations
            lineage_delegations = []
            for dl in delegations:
                env = dl["data"]
                lineage_delegations.append({
                    "issuer": env["issuer"],
                    "delegate": env["delegate"],
                    "signature": env["signature"],
                    "timestamp": env["authorization"]["timestamp"]
                })

            # Générer le fichier de provenance signé
            provenance_payload = {
                "format": "Google OKF v0.1 Provenance",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
                "agent": {
                    "name": "Helios DevAssist",
                    "version": "1.0.0"
                },
                "manifest": sorted(manifest, key=lambda x: x["file"])
            }
            
            if lineage_delegations:
                provenance_payload["lineage"] = {
                    "delegations": sorted(lineage_delegations, key=lambda x: x["delegate"]["subagent_id"])
                }

            # Signature cryptographique globale (englobant manifest et lineage)
            payload_to_sign = {
                "manifest": provenance_payload["manifest"],
                "lineage": provenance_payload.get("lineage", {})
            }
            serialized_payload = json.dumps(payload_to_sign, sort_keys=True)
            secret = "helios_okf_secure_salt_2026"
            signature_input = serialized_payload + secret
            provenance_payload["signature"] = hashlib.sha256(signature_input.encode("utf-8")).hexdigest()
            
            provenance_json = json.dumps(provenance_payload, indent=2, ensure_ascii=False)
            zipf.writestr("provenance_okf.json", provenance_json)

        print(f"Bundle OKF exporté avec succès.")
        return 0
    except Exception as e:
        print(f"Erreur lors de l'exportation ZIP: {e}", file=sys.stderr)
        return 1


def cmd_import(args):
    """Importe un dossier OKF externe sous forme de compétences locales."""
    orig_cwd, workspace_root, skills_dir = resolve_workspace(args.orig_cwd)
    import_src = Path(args.folder)
    if not import_src.is_absolute():
        import_src = orig_cwd / import_src

    if not import_src.exists() or not import_src.is_dir():
        print(f"Erreur : Le répertoire source {import_src} n'existe pas ou n'est pas un dossier.", file=sys.stderr)
        return 1

    import_dest = skills_dir / "imported" / import_src.name
    print(f"Importation du dossier OKF {import_src} vers {import_dest}...")
    import_dest.mkdir(parents=True, exist_ok=True)

    import_count = 0
    for root, _, files in os.walk(import_src):
        for f in files:
            if f.endswith(".md") or f.endswith(".py"):
                src_file = Path(root) / f
                dest_file = import_dest / src_file.relative_to(import_src)
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_bytes(src_file.read_bytes())
                import_count += 1

    print(f"Importation terminée. {import_count} fichiers importés avec succès.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="CLI Helper pour la gestion du format Google OKF.")
    parser.add_argument("--orig-cwd", default=os.getcwd(), help=argparse.SUPPRESS)
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Command: check
    subparsers.add_parser("check", help="Diagnostique la conformité des compétences existantes.")

    # Command: convert
    parser_convert = subparsers.add_parser("convert", help="Met en conformité les en-têtes YAML.")
    parser_convert.add_argument("--write", action="store_true", help="Applique réellement les modifications sur le disque.")

    # Command: export
    parser_export = subparsers.add_parser("export", help="Exporte les connaissances en bundle ZIP.")
    parser_export.add_argument("output", help="Chemin du fichier ZIP de sortie.")

    # Command: import
    parser_import = subparsers.add_parser("import", help="Importe un répertoire OKF externe.")
    parser_import.add_argument("folder", help="Chemin du dossier contenant la documentation OKF.")

    args = parser.parse_args()
    sys.exit(args.func(args) if hasattr(args, "func") else (
        cmd_check(args) if args.command == "check" else (
            cmd_convert(args) if args.command == "convert" else (
                cmd_export(args) if args.command == "export" else (
                    cmd_import(args) if args.command == "import" else 1
                )
            )
        )
    ))


if __name__ == "__main__":
    main()
