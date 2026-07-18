#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automation Linter - Analyseur statique étendu pour code d'automatisation.
Ajoute le support complet de la validation du Structured Text (ST) et Siemens SCL.
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Réutiliser les dataclasses et linters existants si possible
sys.path.insert(0, str(Path(__file__).parent))
try:
    from linter import LintIssue, AWLLinter, L5XLinter
except ImportError:
    # Définition locale si l'import échoue en dehors du contexte
    from dataclasses import dataclass, asdict
    
    @dataclass
    class LintIssue:
        file_path: str
        line: int
        rule_id: str
        severity: str
        message: str
        context: str = ""
        def to_dict(self): return asdict(self)
        
    class AWLLinter:
        def __init__(self, p): self.file_path = p
        def analyze(self): return []
    class L5XLinter:
        def __init__(self, p): self.file_path = p
        def analyze(self): return []

class STSCLinter:
    """Analyseur statique pour les fichiers Structured Text (ST / .st) et Siemens SCL (.scl)."""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.issues: List[LintIssue] = []
        
        # Regex pour détecter les divisions par zéro
        self.re_div_zero = re.compile(r"/\s*0(?:\.0+)?\b")
        # Regex pour les variables locales mal nommées (doivent respecter les standards)
        self.re_local_var = re.compile(r"\bvar\b", re.IGNORECASE)

    def analyze(self) -> List[LintIssue]:
        try:
            with open(self.file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            self.issues.append(
                LintIssue(
                    file_path=str(self.file_path),
                    line=0,
                    rule_id="ST-FILE-ERROR",
                    severity="ERROR",
                    message=f"Impossible de lire le fichier : {e}"
                )
            )
            return self.issues

        in_input_vars = False
        in_output_vars = False
        in_static_vars = False
        in_temp_vars = False
        
        open_ifs = 0
        open_cases = 0
        open_fors = 0
        open_whiles = 0
        
        for idx, raw_line in enumerate(lines):
            line_num = idx + 1
            line = raw_line.strip()
            
            # Ignorer les lignes vides et commentaires complets
            if not line or line.startswith("//") or line.startswith("(*") or line.endswith("*)"):
                continue

            # Retirer les commentaires de fin de ligne pour l'analyse syntaxique
            code_part = line.split("//")[0].split("(*")[0].strip()

            # 1. Gestion des déclarations de variables (Portées)
            upper_code = code_part.upper()
            if "VAR_INPUT" in upper_code:
                in_input_vars = True
                continue
            elif "VAR_OUTPUT" in upper_code:
                in_output_vars = True
                continue
            elif "VAR_IN_OUT" in upper_code:
                # Gérer InOut de la même manière
                in_input_vars = True
                continue
            elif "VAR_TEMP" in upper_code:
                in_temp_vars = True
                continue
            elif "VAR" in upper_code and not any(x in upper_code for x in ["VAR_INPUT", "VAR_OUTPUT", "VAR_TEMP", "VAR_IN_OUT"]):
                in_static_vars = True
                continue
            elif "END_VAR" in upper_code:
                in_input_vars = False
                in_output_vars = False
                in_static_vars = False
                in_temp_vars = False
                continue

            # 2. Vérification du nommage dans les blocs de variables
            if in_input_vars or in_output_vars or in_static_vars or in_temp_vars:
                # Match une déclaration simple : nom_var : TYPE;
                var_match = re.match(r"^(\w+)\s*:", code_part)
                if var_match:
                    var_name = var_match.group(1)
                    
                    if in_input_vars and not (var_name.startswith("i_") or var_name.startswith("in_") or var_name.startswith("iq_") or var_name.startswith("io_")):
                        self.issues.append(
                            LintIssue(
                                file_path=str(self.file_path),
                                line=line_num,
                                rule_id="ST-NAMING-INPUT",
                                severity="WARNING",
                                message=f"La variable d'entrée '{var_name}' devrait commencer par le préfixe 'i_' ou 'in_'.",
                                context=line
                            )
                        )
                    elif in_output_vars and not (var_name.startswith("q_") or var_name.startswith("out_")):
                        self.issues.append(
                            LintIssue(
                                file_path=str(self.file_path),
                                line=line_num,
                                rule_id="ST-NAMING-OUTPUT",
                                severity="WARNING",
                                message=f"La variable de sortie '{var_name}' devrait commencer par le préfixe 'q_' ou 'out_'.",
                                context=line
                            )
                        )
                    elif in_static_vars and not var_name.startswith("stat_"):
                        # Ignorer les instances de blocs standards comme TON, TOF
                        if not any(x in code_part for x in [": TON;", ": TOF;", ": TP;"]):
                            self.issues.append(
                                LintIssue(
                                    file_path=str(self.file_path),
                                    line=line_num,
                                    rule_id="ST-NAMING-STATIC",
                                    severity="INFO",
                                    message=f"La variable statique '{var_name}' devrait commencer par 'stat_'.",
                                    context=line
                                )
                            )
                    elif in_temp_vars and not var_name.startswith("temp_"):
                        self.issues.append(
                            LintIssue(
                                file_path=str(self.file_path),
                                line=line_num,
                                rule_id="ST-NAMING-TEMP",
                                severity="INFO",
                                message=f"La variable temporaire '{var_name}' devrait commencer par 'temp_'.",
                                context=line
                            )
                        )

            # 3. Détection des divisions par zéro
            if self.re_div_zero.search(code_part):
                self.issues.append(
                    LintIssue(
                        file_path=str(self.file_path),
                        line=line_num,
                        rule_id="ST-DIV-ZERO",
                        severity="ERROR",
                        message="Division par zéro critique détectée.",
                        context=line
                    )
                )

            # 4. Détection de boucles WHILE non sécurisées (sans compteur de sauvegarde)
            if "WHILE" in upper_code and "DO" in upper_code:
                open_whiles += 1
                # Vérifier si la condition est WHILE TRUE
                if "TRUE" in upper_code:
                    self.issues.append(
                        LintIssue(
                            file_path=str(self.file_path),
                            line=line_num,
                            rule_id="ST-INFINITE-LOOP",
                            severity="ERROR",
                            message="Boucle WHILE TRUE potentiellement infinie. Privilégiez des boucles FOR ou ajoutez un garde-fou de sécurité.",
                            context=line
                        )
                    )

            # 5. Comptage des ouvertures/fermetures de blocs de contrôle
            if "IF " in upper_code and " THEN" in upper_code:
                open_ifs += 1
            if "END_IF" in upper_code:
                open_ifs -= 1
                
            if "CASE " in upper_code and " OF" in upper_code:
                open_cases += 1
            if "END_CASE" in upper_code:
                open_cases -= 1
                
            if "FOR " in upper_code and " TO " in upper_code:
                open_fors += 1
            if "END_FOR" in upper_code:
                open_fors -= 1
                
            if "END_WHILE" in upper_code:
                open_whiles -= 1

        # 6. Alerte sur les blocs non fermés
        if open_ifs != 0:
            self.issues.append(LintIssue(file_path=str(self.file_path), line=0, rule_id="ST-UNCLOSED-IF", severity="ERROR", message=f"Structure IF/END_IF asymétrique ({open_ifs} blocs restants ouverts)."))
        if open_cases != 0:
            self.issues.append(LintIssue(file_path=str(self.file_path), line=0, rule_id="ST-UNCLOSED-CASE", severity="ERROR", message=f"Structure CASE/END_CASE asymétrique ({open_cases} blocs restants ouverts)."))
        if open_fors != 0:
            self.issues.append(LintIssue(file_path=str(self.file_path), line=0, rule_id="ST-UNCLOSED-FOR", severity="ERROR", message=f"Structure FOR/END_FOR asymétrique ({open_fors} blocs restants ouverts)."))
        if open_whiles != 0:
            self.issues.append(LintIssue(file_path=str(self.file_path), line=0, rule_id="ST-UNCLOSED-WHILE", severity="ERROR", message=f"Structure WHILE/END_WHILE asymétrique ({open_whiles} blocs restants ouverts)."))

        return self.issues

def main():
    parser = argparse.ArgumentParser(description="Linter étendu pour code automates (AWL, L5X, ST, SCL).")
    parser.add_argument("path", help="Fichier ou dossier à analyser")
    parser.add_argument("--json", action="store_true", help="Format de sortie JSON")
    parser.add_argument("--output", "-o", help="Enregistrer le rapport dans un fichier")
    
    args = parser.parse_args()
    target_path = Path(args.path)
    
    if not target_path.exists():
        print(f"Erreur : Le chemin '{target_path}' n'existe pas.", file=sys.stderr)
        sys.exit(1)
        
    files_to_lint = []
    if target_path.is_file():
        files_to_lint.append(target_path)
    else:
        for root, _, files in os.walk(target_path):
            for file in files:
                p = Path(root) / file
                if p.suffix.lower() in (".awl", ".l5x", ".st", ".scl"):
                    files_to_lint.append(p)
                    
    all_issues = []
    for fp in files_to_lint:
        suffix = fp.suffix.lower()
        if suffix == ".awl":
            linter = AWLLinter(fp)
            all_issues.extend(linter.analyze())
        elif suffix == ".l5x":
            linter = L5XLinter(fp)
            all_issues.extend(linter.analyze())
        elif suffix in (".st", ".scl"):
            linter = STSCLinter(fp)
            all_issues.extend(linter.analyze())
            
    # Sortie JSON
    if args.json:
        output_data = [iss.to_dict() for iss in all_issues]
        json_output = json.dumps(output_data, ensure_ascii=False, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(json_output)
            print(f"Rapport JSON enregistré dans '{args.output}'.")
        else:
            print(json_output)
        sys.exit(0)
        
    # Sortie Markdown
    report = []
    report.append("# Rapport d'analyse de Code Automate (Linter)")
    report.append(f"- **Chemin analysé** : `{target_path.resolve()}`")
    report.append(f"- **Fichiers analysés** : {len(files_to_lint)}")
    report.append(f"- **Nombre total d'anomalies** : {len(all_issues)}")
    report.append("")
    
    if not all_issues:
        report.append("🎉 **Aucune anomalie détectée.**")
    else:
        issues_by_file = {}
        for iss in all_issues:
            issues_by_file.setdefault(iss.file_path, []).append(iss)
            
        for fp, file_issues in issues_by_file.items():
            report.append(f"## Fichier : `{os.path.basename(fp)}`")
            report.append("")
            report.append("| Ligne | Sévérité | Règle | Description | Contexte |")
            report.append("| :--- | :--- | :--- | :--- | :--- |")
            for iss in file_issues:
                line_str = str(iss.line) if iss.line > 0 else "-"
                context_escaped = iss.context.replace("|", "\\|") if iss.context else ""
                report.append(f"| {line_str} | **{iss.severity}** | `{iss.rule_id}` | {iss.message} | `{context_escaped}` |")
            report.append("")
            
    report_text = "\n".join(report)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"Rapport Markdown enregistré dans '{args.output}'.")
    else:
        print(report_text)

if __name__ == "__main__":
    main()
