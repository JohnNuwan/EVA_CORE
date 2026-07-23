#!/usr/bin/env python3
"""
ADAM Treasurer — Suit les coûts, revenus, budget tokens et rentabilité de The Hive.

Channels:
  - finance:report   → génère un bilan périodique (coûts tokens, infra, revenus)
  - finance:alert    → alerte si budget dépassé ou coût anormal
  - adam:heartbeat   → reçoit les heartbeats pour estimer l'activité
  - evolution:code_review → estime le coût/benef des refactorings proposés

Usage:
  python3 treasurer-track.py                    # foreground loop (60s interval)
  python3 treasurer-track.py --once             # un seul cycle
  python3 treasurer-track.py --report           # affiche le bilan actuel
  python3 treasurer-track.py --event CHANNEL JSON  # traite un event manuellement

Env vars:
  ADAM_EVENT_CHANNEL, ADAM_EVENT_PAYLOAD, ADAM_EVENT_SOURCE  (from event_daemon)
"""

import sys
import os
import json
import time
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

ADAM_V2_DIR = Path(os.environ.get("ADAM_V2_DIR", os.path.expanduser("~/eva-adam-v2")))
DB_PATH = ADAM_V2_DIR / "event_bus.db"
LOG_DIR = ADAM_V2_DIR / "logs"
LOG_FILE = LOG_DIR / "treasurer-handler.log"
FINANCE_DB = ADAM_V2_DIR / "finance.db"
REPORT_DIR = ADAM_V2_DIR / "reports"

LOG_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# --- Estimation des coûts (USD) ---
# Ces taux sont des estimations; ajuster selon les vraies factures.
COST_PER_TOKEN_IN = 0.00000175    # ~$1.75/1M tokens (mix de modèles)
COST_PER_TOKEN_OUT = 0.000007     # ~$7/1M tokens output
VPS_COST_PER_HOUR = 0.08           # VPS ~$60/mo
GPU_COST_PER_HOUR = 0.45           # GPU spot pricing
ELECTRICITY_PER_HOUR = 0.02        # estimation électricité

INTERVAL = 60  # seconds between cycles


def log(msg, level="INFO"):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    line = f"[{ts}] [{level}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def get_db():
    conn = sqlite3.connect(str(DB_PATH), timeout=5)
    return conn


def init_finance_db():
    """Initialise la DB finance si elle n'existe pas."""
    conn = sqlite3.connect(str(FINANCE_DB), timeout=5)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,          -- 'cost' or 'revenue'
            category TEXT NOT NULL,      -- 'tokens', 'vps', 'gpu', 'electricity', 'service', 'other'
            amount_usd REAL NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS budget_limits (
            category TEXT PRIMARY KEY,
            daily_limit_usd REAL NOT NULL,
            monthly_limit_usd REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_snapshots (
            date TEXT PRIMARY KEY,
            total_cost_usd REAL,
            total_revenue_usd REAL,
            net_usd REAL,
            events_processed INTEGER,
            tokens_estimated INTEGER
        );
    """)
    # Limites par défaut
    defaults = [
        ("tokens", 5.0, 150.0),
        ("vps", 2.0, 60.0),
        ("gpu", 10.0, 300.0),
        ("electricity", 0.5, 15.0),
    ]
    for cat, daily, monthly in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO budget_limits (category, daily_limit_usd, monthly_limit_usd) VALUES (?, ?, ?)",
            (cat, daily, monthly)
        )
    conn.commit()
    conn.close()


def estimate_token_cost():
    """Estime le coût en tokens depuis les events traités aujourd'hui."""
    conn = get_db()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    row = conn.execute(
        "SELECT COUNT(*) FROM events WHERE created_at >= ? AND status IN ('done','skipped')",
        (today,)
    ).fetchone()
    events_today = row[0] if row else 0
    conn.close()

    # Estimation: ~2000 tokens in + 500 tokens out par event traité
    tokens_in = events_today * 2000
    tokens_out = events_today * 500
    cost = tokens_in * COST_PER_TOKEN_IN + tokens_out * COST_PER_TOKEN_OUT
    return cost, events_today, tokens_in + tokens_out


def estimate_infra_cost():
    """Estime le coût d'infrastructure pour aujourd'hui."""
    now = datetime.now(timezone.utc)
    hours_elapsed = now.hour + now.minute / 60.0

    vps = VPS_COST_PER_HOUR * hours_elapsed
    electricity = ELECTRICITY_PER_HOUR * hours_elapsed

    # GPU: vérifier si nvidia-smi est dispo
    gpu_hours = 0
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            gpu_util = int(result.stdout.strip().split("\n")[0])
            if gpu_util > 5:  # GPU actif
                gpu_hours = hours_elapsed
    except Exception:
        pass

    gpu = GPU_COST_PER_HOUR * gpu_hours
    return vps, gpu, electricity


def record_transaction(tx_type, category, amount, description=""):
    conn = sqlite3.connect(str(FINANCE_DB), timeout=5)
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO transactions (type, category, amount_usd, description, created_at) VALUES (?, ?, ?, ?, ?)",
        (tx_type, category, amount, description, now)
    )
    conn.commit()
    conn.close()


def get_daily_totals():
    """Retourne les totaux du jour."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    conn = sqlite3.connect(str(FINANCE_DB), timeout=5)
    cost = conn.execute(
        "SELECT COALESCE(SUM(amount_usd), 0) FROM transactions WHERE type='cost' AND created_at >= ?",
        (today,)
    ).fetchone()[0]
    revenue = conn.execute(
        "SELECT COALESCE(SUM(amount_usd), 0) FROM transactions WHERE type='revenue' AND created_at >= ?",
        (today,)
    ).fetchone()[0]
    conn.close()
    return cost, revenue


def check_budget_alerts():
    """Vérifie si on dépasse les budgets et publie des alertes."""
    cost, revenue = get_daily_totals()
    conn = sqlite3.connect(str(FINANCE_DB), timeout=5)
    limits = conn.execute("SELECT category, daily_limit_usd FROM budget_limits").fetchall()
    conn.close()

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for cat, limit in limits:
        cat_cost = 0
        fc = sqlite3.connect(str(FINANCE_DB), timeout=5)
        row = fc.execute(
            "SELECT COALESCE(SUM(amount_usd), 0) FROM transactions WHERE type='cost' AND category=? AND created_at >= ?",
            (cat, today)
        ).fetchone()
        fc.close()
        cat_cost = row[0] if row else 0

        if cat_cost > limit:
            alert = json.dumps({
                "agent": "adam-treasurer",
                "category": cat,
                "spent": round(cat_cost, 4),
                "limit": limit,
                "message": f"Budget {cat} dépassé: ${cat_cost:.2f} / ${limit:.2f}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            publish_event("finance:alert", alert, priority=8)
            log(f"ALERT: Budget {cat} dépassé: ${cat_cost:.2f} / ${limit:.2f}", "WARN")


def publish_event(channel, payload, priority=5):
    conn = get_db()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO events (channel, source, payload, status, priority, created_at) VALUES (?, 'adam-treasurer', ?, 'pending', ?, ?)",
        (channel, payload, priority, now)
    )
    conn.commit()
    eid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return eid


def run_cycle():
    """Cycle principal: estime coûts, enregistre, vérifie budgets, publie rapport."""
    log("Cycle started")

    # 1. Estimer coûts
    token_cost, events_today, total_tokens = estimate_token_cost()
    vps_cost, gpu_cost, elec_cost = estimate_infra_cost()

    # 2. Enregistrer les transactions (une fois par cycle ~ hourly)
    now = datetime.now(timezone.utc)
    if now.minute < 5:  # Enregistrer une fois par heure (premieres 5 min)
        record_transaction("cost", "tokens", token_cost, f"Tokens: ~{total_tokens} sur {events_today} events")
        record_transaction("cost", "vps", vps_cost, "VPS hosting")
        if gpu_cost > 0:
            record_transaction("cost", "gpu", gpu_cost, "GPU compute")
        record_transaction("cost", "electricity", elec_cost, "Electricity")

    # 3. Bilan
    total_cost, total_revenue = get_daily_totals()
    net = total_revenue - total_cost

    log(f"Daily: cost=${total_cost:.4f} revenue=${total_revenue:.4f} net=${net:.4f} | tokens~{total_tokens} events={events_today}")

    # 4. Vérifier budgets
    check_budget_alerts()

    # 5. Snapshot quotidien
    today = now.strftime("%Y-%m-%d")
    fc = sqlite3.connect(str(FINANCE_DB), timeout=5)
    fc.execute(
        "INSERT OR REPLACE INTO daily_snapshots (date, total_cost_usd, total_revenue_usd, net_usd, events_processed, tokens_estimated) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (today, total_cost, total_revenue, net, events_today, total_tokens)
    )
    fc.commit()
    fc.close()

    # 6. Publier un rapport périodique (toutes les ~10 min)
    if now.minute % 10 == 0:
        report = json.dumps({
            "agent": "adam-treasurer",
            "daily_cost": round(total_cost, 4),
            "daily_revenue": round(total_revenue, 4),
            "net": round(net, 4),
            "events_today": events_today,
            "tokens_estimated": total_tokens,
            "breakdown": {
                "tokens": round(token_cost, 4),
                "vps": round(vps_cost, 4),
                "gpu": round(gpu_cost, 4),
                "electricity": round(elec_cost, 4)
            },
            "timestamp": now.isoformat()
        })
        publish_event("finance:report", report, priority=3)
        log("Rapport financier publié sur finance:report")

    # 7. Heartbeat
    hb = json.dumps({"agent": "adam-treasurer", "status": "active", "net": round(net, 4), "timestamp": now.isoformat()})
    publish_event("adam:heartbeat", hb, priority=1)


def handle_event(channel, payload):
    """Traite un event reçu depuis le bus."""
    log(f"Event reçu: {channel} payload={payload[:200]}")

    if channel == "finance:report":
        # Un autre agent demande un rapport
        run_cycle()

    elif channel == "finance:alert":
        # Alerte financière — logger et amplifier
        log(f"ALERT FINANCIÈRE: {payload}", "WARN")

    elif channel == "adam:heartbeat":
        # Tracker l'activité des agents
        try:
            data = json.loads(payload)
            agent = data.get("agent", "unknown")
            log(f"Heartbeat de {agent}")
        except Exception:
            pass

    elif channel == "evolution:code_review":
        # Estimer coût/bénéfice d'un refactoring
        try:
            data = json.loads(payload)
            findings = data.get("findings_count", 0)
            critical = data.get("critical", 0)
            # Coût estimé du refactoring: ~30 min de tokens
            est_cost = critical * 0.50  # ~$0.50 par issue critique
            benefit = critical * 2.0     # bénéfice estimé (maintenabilité)
            log(f"Code review: {findings} findings, {critical} critiques — coût refact~${est_cost:.2f} bénéfice~${benefit:.2f}")
            if est_cost > 0:
                record_transaction("cost", "tokens", est_cost, f"Refactoring {critical} issues critiques")
        except Exception:
            pass


def print_report():
    """Affiche le bilan financier actuel."""
    init_finance_db()
    cost, revenue = get_daily_totals()
    net = revenue - cost
    token_cost, events_today, total_tokens = estimate_token_cost()
    vps_cost, gpu_cost, elec_cost = estimate_infra_cost()

    print("=" * 60)
    print("💰 ADAM-TREASURER — Bilan Financier")
    print("=" * 60)
    print(f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print()
    print("📊 Coûts du jour:")
    print(f"  Tokens     : ${token_cost:.4f}  (~{total_tokens:,} tokens sur {events_today} events)")
    print(f"  VPS        : ${vps_cost:.4f}")
    print(f"  GPU        : ${gpu_cost:.4f}")
    print(f"  Électricité: ${elec_cost:.4f}")
    print(f"  ─────────────────────────")
    print(f"  Total coût : ${cost:.4f}")
    print()
    print(f"💵 Revenus   : ${revenue:.4f}")
    print(f"📈 Net       : ${net:+.4f}")
    print()

    # Budgets
    conn = sqlite3.connect(str(FINANCE_DB), timeout=5)
    limits = conn.execute("SELECT category, daily_limit_usd FROM budget_limits").fetchall()
    print("🎯 Budgets (quotidiens):")
    for cat, limit in limits:
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        spent = conn.execute(
            "SELECT COALESCE(SUM(amount_usd), 0) FROM transactions WHERE type='cost' AND category=? AND created_at >= ?",
            (cat, today)
        ).fetchone()[0]
        pct = (spent / limit * 100) if limit > 0 else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        status = "✅" if pct < 80 else "⚠️" if pct < 100 else "🔴"
        print(f"  {status} {cat:15s} ${spent:.2f}/${limit:.2f} [{bar}] {pct:.0f}%")
    conn.close()
    print()
    print("=" * 60)


def main():
    init_finance_db()

    if "--once" in sys.argv:
        run_cycle()
        return

    if "--report" in sys.argv:
        print_report()
        return

    if "--event" in sys.argv:
        idx = sys.argv.index("--event")
        channel = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else "unknown"
        payload = sys.argv[idx + 2] if idx + 2 < len(sys.argv) else "{}"
        handle_event(channel, payload)
        return

    # Foreground loop
    log("ADAM-TREASURER démarré (interval=60s)")
    while True:
        try:
            run_cycle()
        except Exception as e:
            log(f"Erreur cycle: {e}", "ERROR")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
