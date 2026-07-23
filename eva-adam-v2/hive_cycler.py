#!/usr/bin/env python3
"""
Adam Hive Cycler — Publie des events périodiques pour maintenir les agents actifs.

Cycle de 2 minutes:
  0:00  hardware:disk_alert, hardware:gpu_alert, hardware:ram_alert  → monitor + deploy
  0:20  security:permission_drift, security:suid_change              → blue
  0:40  osint:alert                                                   → red
  1:00  update:available                                               → sentinel
  1:20  skill:broken                                                    → critic
  1:40  service:down, service:unhealthy                                 → monitor + deploy

Usage:
  python3 hive_cycler.py              # foreground
  python3 hive_cycler.py --once       # un seul cycle
"""

import sys
import os
import time
import json
import sqlite3
import subprocess
import socket
from pathlib import Path
from datetime import datetime, timezone

ADAM_V2_DIR = Path(os.environ.get("ADAM_V2_DIR", os.path.expanduser("~/eva-adam-v2")))
DB_PATH = ADAM_V2_DIR / "event_bus.db"
LOG_DIR = ADAM_V2_DIR / "logs"
LOG_FILE = LOG_DIR / "hive_cycler.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    line = f"[{ts}] [CYCLER] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

def publish(channel, payload):
    """Publie un event directement dans event_bus.db."""
    try:
        conn = sqlite3.connect(str(DB_PATH), timeout=5)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT INTO events (channel, source, payload, status, priority, created_at) "
            "VALUES (?, 'hive_cycler', ?, 'pending', 5, ?)",
            (channel, json.dumps(payload), now)
        )
        conn.commit()
        eid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.close()
        log(f"Event #{eid} → {channel}")
        return eid
    except Exception as e:
        log(f"ERROR publishing {channel}: {e}")
        return None

def get_real_metrics():
    """Collecte de vraies métriques système pour des events réalistes."""
    metrics = {}
    try:
        # Disk
        result = subprocess.run(["df", "/"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            metrics["disk_pct"] = int(parts[4].replace("%", ""))
        
        # RAM
        with open("/proc/meminfo") as f:
            meminfo = {}
            for line in f:
                parts = line.split(":")
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].strip().split()[0])
        total = meminfo.get("MemTotal", 1)
        avail = meminfo.get("MemAvailable", 0)
        metrics["ram_pct"] = round((1 - avail / total) * 100, 1)
        metrics["ram_total_gb"] = round(total / 1024 / 1024, 1)
        
        # CPU load
        with open("/proc/loadavg") as f:
            metrics["load"] = float(f.read().split()[0])
        
        # GPU
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,temperature.gpu,utilization.gpu,memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            gpus = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = [p.strip() for p in line.split(",")]
                    if len(parts) >= 5:
                        gpus.append({
                            "id": int(parts[0]),
                            "temp": int(parts[1]),
                            "util": int(parts[2]),
                            "vram_used": int(parts[3]),
                            "vram_total": int(parts[4]),
                        })
            metrics["gpus"] = gpus
        except Exception:
            metrics["gpus"] = []
        
        # Uptime
        with open("/proc/uptime") as f:
            metrics["uptime_seconds"] = int(float(f.read().split()[0]))
        
        # Hostname
        metrics["hostname"] = socket.gethostname()
        
    except Exception as e:
        log(f"ERROR collecting metrics: {e}")
    
    return metrics

# ── Cycle definitions ──
# Chaque étape publie des events avec de vraies métriques
CYCLE_STEPS = [
    # (delay_seconds, [(channel, payload_fn), ...])
    (0, [
        ("hardware:disk_alert", lambda m: {"disk": "/", "usage_pct": m.get("disk_pct", 0), "hostname": m.get("hostname", "?"), "msg": "Periodic disk check"}),
        ("hardware:gpu_alert", lambda m: {"gpus": m.get("gpus", []), "msg": "Periodic GPU check"}),
        ("hardware:ram_alert", lambda m: {"ram_pct": m.get("ram_pct", 0), "ram_total_gb": m.get("ram_total_gb", 0), "msg": "Periodic RAM check"}),
    ]),
    (15, [
        ("security:permission_drift", lambda m: {"msg": "Periodic permission audit", "hostname": m.get("hostname", "?")}),
        ("security:suid_change", lambda m: {"msg": "Periodic SUID audit", "hostname": m.get("hostname", "?")}),
    ]),
    (30, [
        ("osint:alert", lambda m: {"msg": "Periodic OSINT scan", "load": m.get("load", 0), "uptime": m.get("uptime_seconds", 0)}),
    ]),
    (50, [
        ("update:available", lambda m: {"msg": "Periodic update check", "hostname": m.get("hostname", "?")}),
    ]),
    (70, [
        ("skill:broken", lambda m: {"msg": "Periodic skill audit"}),
    ]),
    (90, [
        ("service:down", lambda m: {"msg": "Health check ping", "hostname": m.get("hostname", "?")}),
        ("service:unhealthy", lambda m: {"msg": "Health check ping", "hostname": m.get("hostname", "?")}),
        ("service:restarted", lambda m: {"msg": "Periodic service restart check", "hostname": m.get("hostname", "?")}),
        ("dashboard:down", lambda m: {"msg": "Periodic dashboard health check", "hostname": m.get("hostname", "?")}),
    ]),
]

CYCLE_DURATION = 120  # 2 minutes total


def run_cycle(once=False):
    log(f"🐝 Démarrage cycle (once={once})")
    
    cycle_num = 0
    while True:
        cycle_num += 1
        log(f"📋 Cycle #{cycle_num} — collecte métriques...")
        metrics = get_real_metrics()
        log(f"  Disk: {metrics.get('disk_pct', '?')}% | RAM: {metrics.get('ram_pct', '?')}% | Load: {metrics.get('load', '?')} | GPUs: {len(metrics.get('gpus', []))}")
        
        for delay, events in CYCLE_STEPS:
            if delay > 0:
                time.sleep(delay)
                # Re-collecter les métriques fraîches
                metrics = get_real_metrics()
            
            for channel, payload_fn in events:
                payload = payload_fn(metrics)
                publish(channel, payload)
                time.sleep(0.5)  # Étaler légèrement
        
        log(f"✅ Cycle #{cycle_num} terminé — {sum(len(e) for _, e in CYCLE_STEPS)} events publiés")
        
        if once:
            break
        
        # Attendre avant le prochain cycle
        remaining = CYCLE_DURATION - sum(d for d, _ in CYCLE_STEPS)
        if remaining > 0:
            log(f"⏳ Prochain cycle dans {remaining}s...")
            time.sleep(remaining)


if __name__ == "__main__":
    once = "--once" in sys.argv
    try:
        run_cycle(once=once)
    except KeyboardInterrupt:
        log("🛑 Arrêt du cycler (KeyboardInterrupt)")
        sys.exit(0)
    except Exception as e:
        log(f"💥 FATAL: {e}")
        sys.exit(1)
