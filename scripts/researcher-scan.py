#!/usr/bin/env python3
"""
ADAM Researcher — Veille scientifique biomédicale & pharma.
Identifie innovations brevetables, opportunités économiques, veille publications.

Channels:
  - research:finding   → résultat de veille (publication, brevet, innovation)
  - research:opportunity → opportunité économique identifiée (brevet, startup, partenariat)

CLI:
  python3 researcher-scan.py --scan       → scan périodique de sources ouvertes
  python3 researcher-scan.py --event <channel> '<json_payload>'  → handler event bus
"""
import sys
import os
import json
import re
import time
import hashlib
import argparse
import subprocess
from datetime import datetime, timezone

# ─── Config ───
RESEARCH_DIR = os.path.expanduser("~/eva-adam-v2/research")
SOURCES_DIR = os.path.join(RESEARCH_DIR, "sources")
FINDINGS_DIR = os.path.join(RESEARCH_DIR, "findings")
OPPORTUNITIES_DIR = os.path.join(RESEARCH_DIR, "opportunities")
LOG_DIR = os.path.expanduser("~/eva-adam-v2/logs")
LOG_FILE = os.path.join(LOG_DIR, "researcher-handler.log")
EVENT_BUS = os.path.expanduser("~/eva-adam-v2/publish.py")

# Sources de veille (Open Access, APIs gratuites)
SOURCES = [
    {"name": "PubMed", "url": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
     "base_params": "db=pubmed&retmax=10&sort=date&term=",
     "topics": ["CRISPR gene editing", "mRNA vaccine", "AI drug discovery",
                "protein folding", "senolytic therapy", "organoid"]},
    {"name": "bioRxiv", "url": "https://api.biorxiv.org/details/biorxiv/",
     "topics": ["synthetic biology", "gene therapy", "biomarker"]},
    {"name": "ClinicalTrials", "url": "https://clinicaltrials.gov/api/v2/studies",
     "topics": ["CAR-T cell therapy", "gene editing", "regenerative medicine"]},
]

# Mots-clés pour scoring d'opportunité
HIGH_VALUE_KEYWORDS = [
    "patent", "novel", "breakthrough", "first-in-class", "orphan drug",
    "fast track", "breakthrough therapy", "FDA approval", "phase 3",
    "proof of concept", "preclinical", "lead compound", "drug candidate"
]

BREEDING_GROUND_KEYWORDS = [
    "startup", "spin-off", " Series A", " Series B", "acquisition",
    "merger", "licensing deal", "exclusive license", "IPO"
]

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
    """Publie un event sur le bus."""
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

def fetch_url(url, timeout=10):
    """Fetch URL avec urllib (pas de dépendance externe)."""
    import urllib.request
    import urllib.error
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ADAM-Researcher/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        log("WARN", f"Fetch failed {url}: {e}")
        return None

# ─── Scan ───
def scan_pubmed(topic, retmax=5):
    """Recherche PubMed via E-utilities API."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    # Search
    search_url = f"{base}esearch.fcgi?db=pubmed&retmax={retmax}&sort=date&term={urllib_quote(topic)}"
    data = fetch_url(search_url)
    if not data:
        return []
    pmids = re.findall(r"<Id>(\d+)</Id>", data)
    if not pmids:
        return []
    # Fetch summaries
    ids_str = ",".join(pmids)
    summary_url = f"{base}esummary.fcgi?db=pubmed&id={ids_str}&retmode=json"
    summary_data = fetch_url(summary_url)
    if not summary_data:
        return []
    results = []
    try:
        parsed = json.loads(summary_data)
        for pmid in pmids:
            entry = parsed.get("result", {}).get(pmid, {})
            if entry:
                results.append({
                    "source": "PubMed",
                    "pmid": pmid,
                    "title": entry.get("title", ""),
                    "authors": [a.get("name", "") for a in entry.get("authors", [])],
                    "journal": entry.get("fulljournalname", ""),
                    "pubdate": entry.get("pubdate", ""),
                    "articleids": entry.get("articleids", []),
                    "topic": topic,
                })
    except json.JSONDecodeError:
        pass
    return results

def urllib_quote(s):
    import urllib.parse
    return urllib.parse.quote(s)

def score_finding(finding):
    """Score une finding: 0-100 sur potentiel de valorisation."""
    text = (finding.get("title", "") + " " + finding.get("abstract", "")).lower()
    score = 0
    reasons = []

    # Haute valeur scientifique
    for kw in HIGH_VALUE_KEYWORDS:
        if kw.lower() in text:
            score += 10
            reasons.append(f"HV: {kw}")

    # Business / breeding ground
    for kw in BREEDING_GROUND_KEYWORDS:
        if kw.lower() in text:
            score += 15
            reasons.append(f"BG: {kw}")

    # Bonus récent (< 30 jours)
    pubdate = finding.get("pubdate", "")
    if pubdate:
        try:
            year = int(pubdate[:4])
            if year >= 2025:
                score += 10
                reasons.append("Recent (2025+)")
        except ValueError:
            pass

    return min(score, 100), reasons

def scan_sources():
    """Scan toutes les sources pour tous les topics."""
    os.makedirs(FINDINGS_DIR, exist_ok=True)
    all_findings = []

    for source in SOURCES:
        for topic in source.get("topics", []):
            log("INFO", f"Scanning {source['name']} for '{topic}'...")
            if source["name"] == "PubMed":
                results = scan_pubmed(topic)
            else:
                # Pour les autres sources: on log mais ne fetch pas
                # (les APIs nécessitent des clés ou ont des formats complexes)
                log("INFO", f"  {source['name']} non implémenté en fetch direct, skip")
                results = []

            for r in results:
                score, reasons = score_finding(r)
                r["score"] = score
                r["score_reasons"] = reasons
                r["scanned_at"] = datetime.now(timezone.utc).isoformat()

                # Sauvegarder la finding
                finding_id = hashlib.md5(
                    f"{r.get('pmid','')}:{r.get('title','')}".encode()
                ).hexdigest()[:12]
                r["id"] = finding_id
                finding_file = os.path.join(FINDINGS_DIR, f"finding-{finding_id}.json")
                with open(finding_file, "w") as f:
                    json.dump(r, f, indent=2, ensure_ascii=False)

                all_findings.append(r)

                # Publier la finding
                publish("research:finding", {
                    "agent": "adam-researcher",
                    "finding_id": finding_id,
                    "source": r["source"],
                    "topic": topic,
                    "title": r["title"],
                    "score": score,
                    "reasons": reasons,
                    "timestamp": r["scanned_at"],
                })

                # Si score élevé → opportunité
                if score >= 30:
                    log("INFO", f"  🎯 Opportunité! score={score} — {r['title'][:60]}")
                    os.makedirs(OPPORTUNITIES_DIR, exist_ok=True)
                    opp_file = os.path.join(OPPORTUNITIES_DIR, f"opp-{finding_id}.json")
                    opp_data = {
                        **r,
                        "type": "potential_patent_or_startup",
                        "estimated_value": "TBD",
                        "recommended_action": "Analyse approfondie + vérification brevetabilité",
                    }
                    with open(opp_file, "w") as f:
                        json.dump(opp_data, f, indent=2, ensure_ascii=False)

                    publish("research:opportunity", {
                        "agent": "adam-researcher",
                        "finding_id": finding_id,
                        "title": r["title"],
                        "score": score,
                        "reasons": reasons,
                        "source": r["source"],
                        "recommended_action": "Analyse approfondie + vérification brevetabilité",
                        "timestamp": r["scanned_at"],
                    })
                else:
                    log("INFO", f"  📄 Finding score={score} — {r['title'][:60]}")

    return all_findings

# ─── Handler event bus ───
def handle_event(channel, payload_str):
    """Handler pour les events du bus."""
    try:
        payload = json.loads(payload_str) if payload_str else {}
    except json.JSONDecodeError:
        payload = {}

    log("INFO", f"Processing event: channel={channel} payload={json.dumps(payload)[:200]}")

    if channel == "evolution:code_review":
        # Le researcher peut suggérer des domaines de recherche basés sur les findings du code scan
        findings = payload.get("findings", [])
        log("INFO", f"Code review reçue: {len(findings)} findings")
        # Pas d'action directe, juste log
        log("INFO", "evolution:code_review noté — pas d'action recherche directe")

    elif channel == "research:finding":
        # Une finding a été publiée par une autre source
        log("INFO", f"Finding reçue: {payload.get('title', 'unknown')[:60]}")

    elif channel == "research:opportunity":
        # Une opportunité a été identifiée
        score = payload.get("score", 0)
        log("INFO", f"Opportunité reçue: score={score}")
        if score >= 50:
            log("INFO", "Haute opportunité — notification au treasurer")
            publish("finance:report", {
                "agent": "adam-researcher",
                "type": "opportunity_notification",
                "title": payload.get("title", ""),
                "score": score,
                "message": "Opportunité de valorisation détectée — impact financier potentiel",
            })

    elif channel == "osint:finding":
        # adam-red a trouvé quelque chose — le researcher peut corréler
        log("INFO", f"OSINT finding reçue — corrélation possible avec recherche biomédicale")

    else:
        log("WARN", f"Canal non géré: {channel}")

    return True

# ─── CLI ───
def main():
    parser = argparse.ArgumentParser(description="ADAM Researcher — Veille scientifique biomédicale")
    parser.add_argument("--scan", action="store_true", help="Scan périodique des sources")
    parser.add_argument("--event", nargs=2, metavar=("CHANNEL", "PAYLOAD"),
                        help="Handler event bus: --event <channel> '<json>'")
    args = parser.parse_args()

    if args.scan:
        log("INFO", "=== Début scan veille scientifique ===")
        findings = scan_sources()
        log("INFO", f"=== Scan terminé: {len(findings)} findings ===")

        # Bilan
        high_score = [f for f in findings if f.get("score", 0) >= 30]
        log("INFO", f"  Total: {len(findings)} findings, {len(high_score)} opportunités (score≥30)")

    elif args.event:
        channel, payload = args.event
        handle_event(channel, payload)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
