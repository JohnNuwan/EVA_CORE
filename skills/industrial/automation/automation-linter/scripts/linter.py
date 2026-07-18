#!/usr/bin/env python3
"""Linter de code automate industriel pour Siemens STEP7 (AWL) et Rockwell Automation (L5X).

Ce script effectue une analyse statique des fichiers sources pour remonter les
anomalies de structure, de nommage, d'adressage physique (hardcodé) et de
documentation manquante selon les standards d'Actemium.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LintIssue:
    file_path: str
    line: int
    rule_id: str
    severity: str  # "ERROR" | "WARNING" | "INFO"
    message: str
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AWLLinter:
    """Analyseur statique pour les fichiers Siemens AWL (STL)."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: list[LintIssue] = []

        # Expressions régulières pour la détection d'adresses absolues
        # ex: M10.0, I0.5, Q1.2
        self.re_bit_mem = re.compile(r"\b[mIqM][0-9]+\.[0-7]\b", re.IGNORECASE)
        # ex: MW20, MD40, IB0, QD4
        self.re_word_mem = re.compile(r"\b[mIqM][wWdDbB][0-9]+\b", re.IGNORECASE)
        # ex: PIW256, PQW512, PEW10
        self.re_periph_mem = re.compile(r"\b(PIW|PQW|PEW|PAW|PIB|PQB|PID|PQD)[0-9]+\b", re.IGNORECASE)
        # ex: DB10.DBX0.0, DB5.DBW10
        self.re_db_mem = re.compile(r"\bDB\d+\.DB[X|B|W|D]\d+(?:\.[0-7])?\b", re.IGNORECASE)

    def analyze(self) -> list[LintIssue]:
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=0,
                    rule_id="AWL-FILE-ERROR",
                    severity="ERROR",
                    message=f"Impossible de lire le fichier: {str(e)}",
                )
            )
            return self.issues

        in_network = False
        network_line_idx = -1
        network_title_found = False
        network_comment_found = False
        current_block_name = ""
        network_count = 0

        for idx, raw_line in enumerate(lines):
            line_num = idx + 1
            line = raw_line.strip()

            # 1. Détection du début de bloc (FB, FC, DB)
            block_match = re.match(
                r"^(FUNCTION_BLOCK|FUNCTION|DATA_BLOCK|ORGANIZATION_BLOCK)\s+([a-zA-Z0-9_\"\-]+)",
                line,
                re.IGNORECASE,
            )
            if block_match:
                block_type = block_match.group(1).upper()
                current_block_name = block_match.group(2).replace('"', "")
                # Vérification de nommage du bloc (UPPER_SNAKE_CASE conseillé)
                if not re.match(r"^[A-Z0-9_]+$", current_block_name):
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="AWL-NAMING-BLOCK",
                            severity="WARNING",
                            message=f"Le nom du bloc {block_type} '{current_block_name}' devrait être en UPPER_SNAKE_CASE.",
                            context=line,
                        )
                    )

            # 2. Gestion de la structure NETWORK
            if line.upper().startswith("NETWORK"):
                # Si on entrait déjà dans un network sans avoir fini l'autre (rare en AWL propre)
                if in_network:
                    self._check_network_rules(network_line_idx, network_title_found, network_comment_found, network_count)

                in_network = True
                network_line_idx = line_num
                network_title_found = False
                network_comment_found = False
                network_count += 1
                continue

            if in_network:
                # Vérification du titre du network
                if line.upper().startswith("TITLE ="):
                    title_content = line[7:].strip()
                    if title_content:
                        network_title_found = True
                        # Vérification de longueur ou format du titre
                        if len(title_content) < 3:
                            self.issues.append(
                                LintIssue(
                                    file_path=str(self.file_path),
                                    line=line_num,
                                    rule_id="AWL-SHORT-TITLE",
                                    severity="INFO",
                                    message=f"Titre de réseau très court dans le réseau {network_count} : '{title_content}'.",
                                    context=line,
                                )
                            )
                    else:
                        self.issues.append(
                            LintIssue(
                                file_path=str(self.file_path),
                                line=line_num,
                                rule_id="AWL-EMPTY-TITLE",
                                severity="WARNING",
                                message=f"Le titre du réseau {network_count} est déclaré vide.",
                                context=line,
                            )
                        )

                # Détection de commentaires
                if line.startswith("//"):
                    comment_content = line[2:].strip()
                    if len(comment_content) > 3:
                        network_comment_found = True

                # Détection de fin de fonction / bloc
                if line.upper().startswith("END_FUNCTION_BLOCK") or line.upper().startswith("END_FUNCTION"):
                    self._check_network_rules(network_line_idx, network_title_found, network_comment_found, network_count)
                    in_network = False

            # 3. Détection d'adressage absolu (hardcoded)
            # Ignorer les lignes de commentaires
            if not line.startswith("//"):
                # Retirer les commentaires en bout de ligne pour l'analyse d'adresses
                code_part = line.split("//")[0].strip()

                # Recherche d'adresses absolues dans la partie code
                bit_match = self.re_bit_mem.findall(code_part)
                for addr in bit_match:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="AWL-HARDCODED-BIT",
                            severity="WARNING",
                            message=f"Adresse mémoire absolue détectée : '{addr}'. Utilisez des variables symboliques.",
                            context=line,
                        )
                    )

                word_match = self.re_word_mem.findall(code_part)
                for addr in word_match:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="AWL-HARDCODED-WORD",
                            severity="WARNING",
                            message=f"Adresse registre absolue détectée : '{addr}'. Utilisez des variables symboliques.",
                            context=line,
                        )
                    )

                periph_match = self.re_periph_mem.findall(code_part)
                for addr in periph_match:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="AWL-HARDCODED-IO",
                            severity="WARNING",
                            message=f"Accès direct E/S périphérique détecté : '{addr}'. Utilisez des symboles de cartes.",
                            context=line,
                        )
                    )

                db_match = self.re_db_mem.findall(code_part)
                for addr in db_match:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="AWL-HARDCODED-DB",
                            severity="WARNING",
                            message=f"Accès absolu à un DB détecté : '{addr}'. Privilégiez les DB symboliques.",
                            context=line,
                        )
                    )

        # Vérification finale au cas où le fichier se termine sans END_
        if in_network:
            self._check_network_rules(network_line_idx, network_title_found, network_comment_found, network_count)

        return self.issues

    def _check_network_rules(self, line_num: int, title_found: bool, comment_found: bool, network_idx: int):
        """Vérifie si les règles obligatoires d'un réseau sont respectées."""
        if not title_found:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=line_num,
                    rule_id="AWL-MISSING-TITLE",
                    severity="WARNING",
                    message=f"Le réseau {network_idx} ne contient aucun titre défini (TITLE =).",
                )
            )
        if not comment_found:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=line_num,
                    rule_id="AWL-MISSING-COMMENT",
                    severity="INFO",
                    message=f"Le réseau {network_idx} manque de commentaires explicatifs (//).",
                )
            )


class L5XLinter:
    """Analyseur statique pour les fichiers Rockwell Automation L5X (XML)."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: list[LintIssue] = []

    def analyze(self) -> list[LintIssue]:
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
        except ET.ParseError as pe:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=0,
                    rule_id="L5X-PARSE-ERROR",
                    severity="ERROR",
                    message=f"Erreur de syntaxe XML: {str(pe)}",
                )
            )
            return self.issues
        except Exception as e:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=0,
                    rule_id="L5X-FILE-ERROR",
                    severity="ERROR",
                    message=f"Impossible de lire le fichier: {str(e)}",
                )
            )
            return self.issues

        # Parcours des tags (Tags globaux et locaux)
        # Les tags se trouvent généralement sous Controller/Tags/Tag ou Program/Tags/Tag
        tags = root.findall(".//Tag")
        for tag in tags:
            tag_name = tag.attrib.get("Name", "")
            data_type = tag.attrib.get("DataType", "")
            tag_class = tag.attrib.get("Class", "")

            # 1. Vérification du nommage du Tag (Standard UPPER_SNAKE_CASE pour les constantes / variables globales)
            if tag_name:
                # Règle de longueur maximale de Rockwell (40 caractères)
                if len(tag_name) > 40:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=0,
                            rule_id="L5X-TAG-LENGTH",
                            severity="WARNING",
                            message=f"Le tag '{tag_name}' dépasse la limite de longueur recommandée de Rockwell (40 caractères). Longueur : {len(tag_name)}.",
                            context=f"DataType: {data_type}",
                        )
                    )

                # Naming standard (conseillé UPPER_SNAKE_CASE ou camelCase, évite les caractères bizarres)
                if not re.match(r"^[a-zA-Z0-9_]+$", tag_name):
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=0,
                            rule_id="L5X-TAG-INVALID-CHAR",
                            severity="ERROR",
                            message=f"Le tag '{tag_name}' contient des caractères non autorisés (uniquement alphanumérique et tiret bas).",
                        )
                    )
                elif not re.match(r"^[A-Z0-9_]+$", tag_name) and not re.match(r"^[a-z][a-zA-Z0-9_]*$", tag_name):
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=0,
                            rule_id="L5X-TAG-NAMING",
                            severity="INFO",
                            message=f"Le tag '{tag_name}' ne respecte pas les conventions recommandées (UPPER_SNAKE_CASE ou camelCase).",
                        )
                    )

            # 2. Vérification de la présence d'une description
            desc_elem = tag.find("Description")
            if desc_elem is None or not desc_elem.text or not desc_elem.text.strip():
                # Ignorer certains tags systèmes ou temporaires
                if not tag_name.startswith("__") and not tag_name.startswith("tmp"):
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=0,
                            rule_id="L5X-MISSING-DESC",
                            severity="WARNING",
                            message=f"Le tag '{tag_name}' (DataType: {data_type}) manque de description/documentation.",
                        )
                    )

        # 3. Parcours des routines pour analyser la logique de programmation
        # Les routines peuvent contenir des rungs (échelons) en RLL (Ladder) ou du texte structuré (ST)
        rungs = root.findall(".//Rung")
        for idx, rung in enumerate(rungs):
            rung_number = rung.attrib.get("Number", str(idx))
            comment = rung.find("Comment")
            if comment is None or not comment.text or not comment.text.strip():
                self.issues.append(
                    LintIssue(
                        file_path=str(self.file_path),
                        line=0,
                        rule_id="L5X-RUNG-MISSING-COMMENT",
                        severity="INFO",
                        message=f"L'échelon (Rung) numéro {rung_number} ne comporte aucun commentaire.",
                    )
                )

        return self.issues


def lint_file(file_path: Path) -> list[LintIssue]:
    """Détermine le type de fichier et appelle le linter correspondant."""
    suffix = file_path.suffix.lower()
    if suffix == ".awl":
        linter = AWLLinter(file_path)
        return linter.analyze()
    elif suffix == ".l5x":
        linter = L5XLinter(file_path)
        return linter.analyze()
    else:
        return []


def main():
    parser = argparse.ArgumentParser(description="Linter pour fichiers STEP7 (AWL) et Rockwell (L5X).")
    parser.add_argument("path", help="Chemin vers le fichier ou dossier à analyser.")
    parser.add_argument("--json", action="store_true", help="Sortie au format JSON.")
    parser.add_argument("--severity", choices=["ERROR", "WARNING", "INFO"], default="INFO", help="Filtrer par sévérité minimale.")
    parser.add_argument("--output", "-o", help="Enregistrer le rapport dans un fichier.")

    args = parser.parse_args()
    target_path = Path(args.path)

    if not target_path.exists():
        print(f"Erreur: Le chemin '{target_path}' n'existe pas.", file=sys.stderr)
        sys.exit(1)

    files_to_lint: list[Path] = []
    if target_path.is_file():
        files_to_lint.append(target_path)
    else:
        # Recherche récursive de tous les fichiers .awl et .l5x
        for root, _, files in os.walk(target_path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in (".awl", ".l5x"):
                    files_to_lint.append(file_path)

    severity_weights = {"INFO": 1, "WARNING": 2, "ERROR": 3}
    min_weight = severity_weights.get(args.severity, 1)

    all_issues: list[LintIssue] = []
    for fp in files_to_lint:
        issues = lint_file(fp)
        for issue in issues:
            issue_weight = severity_weights.get(issue.severity, 1)
            if issue_weight >= min_weight:
                all_issues.append(issue)

    # 1. Sortie au format JSON
    if args.json:
        output_data = [iss.to_dict() for iss in all_issues]
        json_output = json.dumps(output_data, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"Rapport sauvegardé sous format JSON dans '{args.output}'.")
        else:
            print(json_output)
        sys.exit(0)

    # 2. Sortie au format Markdown (ou texte lisible standard)
    report_lines = []
    report_lines.append("# Rapport d'analyse de Code Automate (Linter)")
    report_lines.append(f"- **Chemin analysé** : `{target_path.resolve()}`")
    report_lines.append(f"- **Fichiers analysés** : {len(files_to_lint)}")
    report_lines.append(f"- **Nombre total d'anomalies** : {len(all_issues)}")
    report_lines.append("")

    if not all_issues:
        report_lines.append("🎉 **Félicitations ! Aucune anomalie n'a été détectée.**")
    else:
        # Regrouper par fichier
        issues_by_file: dict[str, list[LintIssue]] = {}
        for issue in all_issues:
            issues_by_file.setdefault(issue.file_path, []).append(issue)

        for filepath, file_issues in issues_by_file.items():
            report_lines.append(f"## Fichier : `{os.path.basename(filepath)}`")
            report_lines.append(f"*(Chemin complet : `{filepath}`)*")
            report_lines.append("")
            report_lines.append("| Ligne | Sévérité | Règle | Description | Contexte |")
            report_lines.append("| :--- | :--- | :--- | :--- | :--- |")
            for iss in file_issues:
                line_str = str(iss.line) if iss.line > 0 else "-"
                context_escaped = iss.context.replace("|", "\\|") if iss.context else ""
                report_lines.append(
                    f"| {line_str} | **{iss.severity}** | `{iss.rule_id}` | {iss.message} | `{context_escaped}` |"
                )
            report_lines.append("")

    report_text = "\n".join(report_lines)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Rapport de linting écrit dans '{args.output}'.")
    else:
        print(report_text)

    # Exit code en fonction de la présence d'erreurs (sécurité CI)
    has_errors = any(iss.severity == "ERROR" for iss in all_issues)
    if has_errors:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
