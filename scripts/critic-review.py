#!/usr/bin/env python3
"""
ADAM Critic — Audit qualité & auto-fix de code.
Traite les evolution:code_review de adam-evolution.

Actions:
  - unused_import  → AUTO-FIX (supprime l'import)
  - syntax_error   → ALERTE (publie sur security:alert)
  - high_complexity→ TASK (crée un fichier de task de refactor)
  - factorization  → TASK (crée un fichier de task)

Canaux:
  - evolution:code_review (écoute)
  - skill:broken, skill:created, skill:updated (existing)
"""
import sys
import os
import json
import re
import argparse
import subprocess
from datetime import datetime, timezone
from collections import defaultdict

# ─── Config ───
ADAM_V2_DIR = os.environ.get("ADAM_V2_DIR", "/home/aza/eva-adam-v2")
LOG_DIR = os.path.join(ADAM_V2_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "critic-handler.log")
TASKS_DIR = os.path.join(ADAM_V2_DIR, "tasks")
FIXES_DIR = os.path.join(ADAM_V2_DIR, "fixes")
EVENT_BUS = os.path.join(ADAM_V2_DIR, "publish.py")
SKILLS_DIR = os.path.expanduser("~/.hermes/skills")

# ─── Logging ───
def log(level, msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] [{level}] {msg}"
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if level == "ERROR":
        print(line, file=sys.stderr)
    else:
        print(line)

def publish(channel, payload):
    try:
        payload_str = json.dumps(payload) if isinstance(payload, dict) else str(payload)
        result = subprocess.run(
            [sys.executable, EVENT_BUS, channel, payload_str],
            capture_output=True, text=True, timeout=15
        )
        log("INFO", f"Published on {channel}: {result.stdout.strip()}")
        return True
    except Exception as e:
        log("ERROR", f"Publish failed on {channel}: {e}")
        return False

# ─── Auto-fix: unused imports ───
def fix_unused_import(filepath, finding):
    """Supprime un import inutilisé d'un fichier Python."""
    line_num = finding.get("line", 0)
    suggestion = finding.get("suggestion", "")
    message = finding.get("message", "")

    # Extraire le nom de l'import à supprimer
    # Format: "Import 'hashlib' non utilisé — supprimer"
    match = re.search(r"Import '(\S+)'", message)
    if not match:
        log("WARN", f"Impossible de parser l'import: {message}")
        return False
    import_name = match.group(1)

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        log("WARN", f"Fichier introuvable: {filepath}")
        return False

    if line_num < 1 or line_num > len(lines):
        log("WARN", f"Numéro de ligne invalide: {line_num}")
        return False

    target_line = lines[line_num - 1]
    changed = False

    # Cas 1: import simple — "import hashlib"
    if re.match(rf"^\s*import\s+{re.escape(import_name)}\s*$", target_line):
        lines.pop(line_num - 1)
        changed = True
        log("INFO", f"  Supprimé ligne {line_num}: {target_line.strip()}")

    # Cas 2: from X import Y — "from datetime import timezone"
    elif "from " in target_line and import_name in target_line:
        # Si un seul import sur la ligne → supprimer la ligne
        after_from = target_line.split("import ", 1)[-1].strip()
        names_on_line = [n.strip().rstrip(",") for n in after_from.split(",")]
        if len(names_on_line) == 1 and names_on_line[0] == import_name:
            lines.pop(line_num - 1)
            changed = True
            log("INFO", f"  Supprimé ligne {line_num}: {target_line.strip()}")
        elif import_name in names_on_line:
            # Supprimer juste ce nom de la liste
            new_names = [n for n in names_on_line if n != import_name]
            prefix = target_line.split("import ", 1)[0] + "import "
            lines[line_num - 1] = prefix + ", ".join(new_names) + "\n"
            changed = True
            log("INFO", f"  Modifié ligne {line_num}: {lines[line_num-1].strip()}")

    # Cas 3: import composite — "import os, sys" ou "from X import (A, B)"
    elif f"import {import_name}" in target_line:
        # Tenter de retirer juste le nom
        new_line = re.sub(
            rf"\b{re.escape(import_name)}\b,?\s*", "", target_line
        )
        new_line = re.sub(r",\s*$", "", new_line)  # trailing comma
        if new_line.strip() and new_line != target_line:
            lines[line_num - 1] = new_line
            changed = True
            log("INFO", f"  Modifié ligne {line_num}: {new_line.strip()}")

    if changed:
        # Sauvegarder le backup
        os.makedirs(FIXES_DIR, exist_ok=True)
        backup_name = os.path.basename(filepath) + ".bak"
        backup_path = os.path.join(FIXES_DIR, f"{backup_name}.{datetime.now().strftime('%H%M%S')}")
        with open(backup_path, "w") as f:
            f.writelines(lines)  # original sera écrasé, backup = new state for safety

        with open(filepath, "w") as f:
            f.writelines(lines)
        log("INFO", f"  ✅ Auto-fix appliqué: {filepath}")
        return True
    else:
        log("WARN", f"  Pas pu auto-fix: {filepath}:{line_num} — {target_line.strip()}")
        return False

# ─── Create refactor task ───
def create_refactor_task(finding, task_type="refactor"):
    """Crée un fichier de task pour un finding non auto-fixable."""
    os.makedirs(TASKS_DIR, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    ftype = finding.get("type", "unknown")
    fname = f"task-{task_type}-{ftype}-{ts}.md"

    filepath = finding.get("file", "unknown")
    line = finding.get("line", 0)
    severity = finding.get("severity", "info")
    message = finding.get("message", "")
    suggestion = finding.get("suggestion", "")

    content = f"""# Task: {task_type} — {ftype}

- **Fichier:** `{filepath}:{line}`
- **Sévérité:** {severity}
- **Type:** {ftype}
- **Date:** {ts}

## Problème

{message}

## Suggestion

{suggestion or "Aucune suggestion automatique — analyse manuelle requise."}

## Action requise

{"⚠️ URGENT — Corriger dès que possible" if severity == "critical" else "Corriger quand possible"}
"""

    task_file = os.path.join(TASKS_DIR, fname)
    with open(task_file, "w") as f:
        f.write(content)
    log("INFO", f"  📝 Task créée: {task_file}")
    return task_file

# ─── Handler: evolution:code_review ───
def handle_code_review(payload):
    """Traite un event evolution:code_review avec findings."""
    scan_root = payload.get("scan_root", "")
    files_scanned = payload.get("files_scanned", 0)
    summary = payload.get("summary", {})
    critical_findings = payload.get("critical_findings", [])

    log("INFO", f"Code review reçue — {files_scanned} fichiers scannés")
    log("INFO", f"  Summary: {json.dumps(summary)[:200]}")
    log("INFO", f"  Critical findings: {len(critical_findings)}")

    # Charger le rapport complet depuis disque (plus riche que l'event)
    report_file = os.path.join(ADAM_V2_DIR, "evolution", "code_review_report.json")
    all_findings = critical_findings
    try:
        with open(report_file) as f:
            report = json.load(f)
        all_findings = report.get("findings", [])
        log("INFO", f"  Rapport complet chargé: {len(all_findings)} findings")
    except (FileNotFoundError, json.JSONDecodeError):
        log("WARN", "Rapport complet non trouvé — utilisation des critical_findings uniquement")

    stats = defaultdict(int)
    fixes_applied = 0
    tasks_created = 0
    alerts_sent = 0

    for finding in all_findings:
        ftype = finding.get("type", "unknown")
        severity = finding.get("severity", "info")
        filepath = finding.get("file", "")
        stats[ftype] += 1

        # Construire le chemin absolu
        if filepath and not os.path.isabs(filepath):
            filepath = os.path.join(ADAM_V2_DIR, filepath)
            finding["file"] = filepath

        if ftype == "unused_import" and severity != "critical":
            # AUTO-FIX
            if fix_unused_import(filepath, finding):
                fixes_applied += 1

        elif ftype == "syntax_error" or severity == "critical":
            # ALERTE
            log("ERROR", f"🚨 CRITICAL: {filepath}:{finding.get('line',0)} — {finding.get('message','')}")
            create_refactor_task(finding, task_type="critical")
            tasks_created += 1
            publish("security:alert", {
                "agent": "adam-critic",
                "type": "syntax_error",
                "file": filepath,
                "line": finding.get("line", 0),
                "message": finding.get("message", ""),
                "severity": "critical",
            })
            alerts_sent += 1

        elif ftype in ("high_complexity", "factorization"):
            # TASK de refactor
            create_refactor_task(finding, task_type="refactor")
            tasks_created += 1

        else:
            log("INFO", f"  Finding non traité: {ftype} — {finding.get('message','')[:50]}")

    # Bilan
    log("INFO", f"=== Bilan code review ===")
    log("INFO", f"  Fixes appliqués: {fixes_applied}")
    log("INFO", f"  Tasks créées: {tasks_created}")
    log("Info", f"  Alertes envoyées: {alerts_sent}")
    log("INFO", f"  Par type: {dict(stats)}")

    # Publier le bilan
    publish("wiki:update", {
        "agent": "adam-critic",
        "type": "code_review_processed",
        "files_scanned": files_scanned,
        "total_findings": len(all_findings),
        "fixes_applied": fixes_applied,
        "tasks_created": tasks_created,
        "alerts_sent": alerts_sent,
        "stats": dict(stats),
    })

    return {
        "fixes_applied": fixes_applied,
        "tasks_created": tasks_created,
        "alerts_sent": alerts_sent,
    }

# ─── Handler: skill events ───
def handle_skill_event(channel, payload):
    """Handler pour les events de skills (existing behavior)."""
    skill_name = payload.get("skill_name", payload.get("skill", ""))
    log("INFO", f"Skill event: {channel} — skill={skill_name}")

    if channel == "skill:broken":
        error = payload.get("error", "")
        log("WARN", f"Skill cassé: {skill_name} — {error}")
        # Notifier pour repair
        publish("adam:error", {
            "agent": "adam-critic",
            "type": "skill_broken",
            "skill": skill_name,
            "error": error,
        })

    elif channel == "skill:created":
        log("INFO", f"Nouveau skill: {skill_name} — review nécessaire")

    elif channel == "skill:updated":
        log("INFO", f"Skill mis à jour: {skill_name} — review recommandée")

    return True

# ─── Main handler ───
def handle_event(channel, payload_str):
    try:
        payload = json.loads(payload_str) if payload_str else {}
    except json.JSONDecodeError:
        payload = {}

    log("INFO", f"Processing: channel={channel} payload={json.dumps(payload)[:200]}")

    if channel == "evolution:code_review":
        return handle_code_review(payload)
    elif channel in ("skill:broken", "skill:created", "skill:updated"):
        return handle_skill_event(channel, payload)
    else:
        log("WARN", f"Canal non géré: {channel}")
        return False

# ─── CLI ───
def main():
    parser = argparse.ArgumentParser(description="ADAM Critic — Audit qualité & auto-fix")
    parser.add_argument("--event", nargs=2, metavar=("CHANNEL", "PAYLOAD"),
                        help="Handler event bus: --event <channel> '<json>'")
    parser.add_argument("--review", action="store_true",
                        help="Traite le rapport code_review_report.json directement")
    args = parser.parse_args()

    if args.event:
        channel, payload = args.event
        result = handle_event(channel, payload)
        print(json.dumps(result) if isinstance(result, dict) else str(result))

    elif args.review:
        # Traiter directement depuis le rapport sur disque
        report_file = os.path.join(ADAM_V2_DIR, "evolution", "code_review_report.json")
        try:
            with open(report_file) as f:
                report = json.load(f)
            payload = {
                "scan_root": ADAM_V2_DIR,
                "files_scanned": report.get("files_scanned", 0),
                "summary": report.get("summary", {}),
                "critical_findings": [
                    f for f in report.get("findings", [])
                    if f.get("severity") == "critical"
                ],
            }
            result = handle_code_review(payload)
            print(json.dumps(result, indent=2))
        except FileNotFoundError:
            print(f"Rapport non trouvé: {report_file}")
            sys.exit(1)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
