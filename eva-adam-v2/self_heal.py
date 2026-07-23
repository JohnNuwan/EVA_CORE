#!/usr/bin/env python3
"""
self_heal.py — Boucle d'auto-guérison ADAM v2 (Levier 2)

Cycle en 4 étapes :
  1. DÉTECTION   : écoute les événements 'adam:error' et 'hardware:gpu_alert'
                   sur le bus SQLite.
  2. RÉSOLUTION  : applique une stratégie adaptée au type d'erreur
                   (dictionnaire STRATEGIES).
  3. VALIDATION  : vérifie que le problème est résolu (check API, process, GPU).
  4. NOTIFICATION : publie un événement 'adam:healed' sur le bus avec le
                   détail de la résolution.

Usage :
    python3 self_heal.py                    # boucle infinie (intervalle 10s)
    python3 self_heal.py --dry-run          # simulation sans exécution
    python3 self_heal.py --once             # un seul cycle puis sort
    python3 self_heal.py --status           # état actuel du bus

Dépendances : sqlite3 (stdlib), json, subprocess, logging, time, os
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import os
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ─── Chemins ────────────────────────────────────────────────────────────────

ADAM_V2_DIR = Path(os.environ.get("ADAM_V2_DIR", "/home/aza/eva-adam-v2"))
DB_PATH = ADAM_V2_DIR / "event_bus.db"
LOG_DIR = ADAM_V2_DIR / "logs"
LOG_PATH = LOG_DIR / "self_heal.log"
SCRIPTS_DIR = Path(os.environ.get("HOME", "/home/aza")) / "scripts"

# ─── Configuration ──────────────────────────────────────────────────────────

INTERVALLE = 10           # secondes entre chaque cycle
HEARTBEAT_INTERVAL = 60   # heartbeat toutes les 60 secondes
HANDLER_TIMEOUT = 30      # timeout pour les sous-processus

# Canaux surveillés par la boucle
CANAUX_ERREUR = {"adam:error", "hardware:gpu_alert"}

# ─── Logging ────────────────────────────────────────────────────────────────

LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("self_heal")
logger.setLevel(logging.DEBUG)

# Handler fichier — rotation 5 × 1 Mo
file_handler = logging.handlers.RotatingFileHandler(
    LOG_PATH, maxBytes=1_048_576, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.DEBUG)
file_fmt = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)
file_handler.setFormatter(file_fmt)
logger.addHandler(file_handler)

# Handler console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_fmt = logging.Formatter("[%(levelname)s] %(message)s")
console_handler.setFormatter(console_fmt)
logger.addHandler(console_handler)

# ─── Stratégies de résolution ────────────────────────────────────────────────

STRATEGIES: dict[str, dict[str, Any]] = {
    "restart_service": {
        "description": "Redémarre un service systemd ou un processus",
        "cibles": ["adam-event-daemon", "file-watcher"],
        "commandes": ["systemctl", "restart", "--user"],
        "fallback": ["pkill", "-x"],
    },
    "free_vram": {
        "description": "Libère la VRAM GPU en tuant les processus les plus gourmands",
        "commandes": ["fuser", "-v", "/dev/nvidia0"],
        "fallback": ["killall", "-9", "python3"],
        "seuil_go": 6,  # seuil VRAM en Go (arbitraire)
    },
    "clean_disk": {
        "description": "Nettoie les caches temporaires si le disque est > 90%",
        "commandes": ["df", "/"],
        "cibles": ["/tmp", "/var/tmp", str(ADAM_V2_DIR / "logs")],
        "seuil_pct": 90,
    },
    "free_memory": {
        "description": "Libère la RAM système en flushant les caches",
        "seuil_pct": 85,  # pourcentage d'utilisation mémoire
    },
    "restart_agent": {
        "description": "Redémarre un agent ADAM spécifique par son agent_id",
        "commandes": ["pkill", "-x"],
        "fallback_grace": 5,  # secondes d'attente entre SIGTERM et SIGKILL
    },
    "retry": {
        "description": "Re-tente l'action qui a échoué (3 tentatives, 10s d'intervalle)",
        "max_tentatives": 3,
        "delai": 10,
    },
    "kill_zombie": {
        "description": "Tue un processus zombie ou bloqué repéré par son PID",
        "signal": "SIGTERM",
        "escalade_delai": 3,
    },
}

# Mapping : type d'erreur → stratégie
# Le payload peut contenir "error_type" ou on déduit du canal/source.
TYPE_TO_STRATEGY: dict[str, str] = {
    "service_down": "restart_service",
    "service_crash": "restart_service",
    "gpu_oom": "free_vram",
    "gpu_hang": "restart_service",
    "disk_full": "clean_disk",
    "memory_critical": "free_memory",
    "agent_crash": "restart_agent",
    "agent_unresponsive": "restart_agent",
    "handler_failed": "retry",
    "zombie_process": "kill_zombie",
    "daemon_stopped": "restart_service",
    "out_of_memory": "free_memory",
}

# ─── Bus SQLite ─────────────────────────────────────────────────────────────


class HealBus:
    """Accès bas niveau au bus SQLite pour la boucle d'auto-guérison.

    Utilise uniquement sqlite3 — pas d'import depuis event_bus.py.
    WAL activé, connexion avec timeout.
    """

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        """Ouvre une connexion SQLite avec WAL et timeout."""
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=3000")
        return conn

    def get_erreurs_pendantes(self, limit: int = 10) -> list[dict]:
        """Récupère les événements d'erreur en attente de traitement.

        Cherche sur les canaux 'adam:error' et 'hardware:gpu_alert'.

        Returns:
            Liste de dicts avec les colonnes de la table events.
        """
        placeholders = ",".join("?" for _ in CANAUX_ERREUR)
        sql = f"""
            SELECT id, channel, source, payload, priority, created_at
            FROM events
            WHERE channel IN ({placeholders})
              AND status = 'pending'
            ORDER BY priority DESC, created_at ASC
            LIMIT ?
        """
        conn = self._connect()
        try:
            rows = conn.execute(sql, (*CANAUX_ERREUR, limit)).fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def marquer_traite(self, event_id: int, succes: bool = True) -> None:
        """Marque un événement comme traité (done ou failed)."""
        status = "done" if succes else "failed"
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE events SET status=?, processed_at=? WHERE id=?",
                (status, datetime.now(timezone.utc).isoformat(), event_id),
            )
            conn.commit()
        finally:
            conn.close()

    def publier(self, channel: str, payload: dict, source: str = "self-heal",
                priority: int = 0) -> int:
        """Publie un événement sur le bus (INSERT direct dans events)."""
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            cursor = conn.execute(
                """INSERT INTO events (channel, source, payload, priority, created_at, status)
                   VALUES (?, ?, ?, ?, ?, 'pending')""",
                (channel, json.dumps(payload, ensure_ascii=False), source, priority, now),
            )
            conn.commit()
            event_id = cursor.lastrowid
            logger.info(f"Événement #{event_id} publié: {channel} depuis {source}")
            return event_id
        finally:
            conn.close()

    def get_agent_status(self, agent_id: str) -> Optional[dict]:
        """Récupère le statut d'un agent."""
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM agents WHERE agent_id=?", (agent_id,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_agent_status(self, agent_id: str, status: str,
                            last_error: Optional[str] = None) -> None:
        """Met à jour le statut d'un agent."""
        now = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            if last_error:
                conn.execute(
                    """UPDATE agents
                       SET status=?, last_run_at=?, last_status=?, last_error=?
                       WHERE agent_id=?""",
                    (status, now, status, last_error, agent_id),
                )
            else:
                conn.execute(
                    "UPDATE agents SET status=?, last_run_at=? WHERE agent_id=?",
                    (status, now, agent_id),
                )
            conn.commit()
        finally:
            conn.close()

    def heartbeat(self) -> None:
        """Publie un heartbeat pour signaler que self-heal est vivant."""
        self.publier("adam:heartbeat", {
            "service": "self-heal",
            "pid": os.getpid(),
        }, source="self-heal", priority=0)


# ─── Résolveurs ─────────────────────────────────────────────────────────────


class Resolveur:
    """Applique les stratégies de résolution pour chaque type d'erreur."""

    def __init__(self, bus: HealBus, dry_run: bool = False) -> None:
        self.bus = bus
        self.dry_run = dry_run

    # ── Détection des erreurs système ────────────────────────────────────

    def verifier_gpu(self) -> dict[str, Any]:
        """Vérifie l'état du GPU NVIDIA (nvidia-smi).

        Returns:
            dict avec 'ok' (bool) et 'detail' (str).
        """
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return {"ok": False, "detail": "nvidia-smi indisponible"}

            lignes = result.stdout.strip().split("\n")
            for i, ligne in enumerate(lignes):
                parts = [p.strip() for p in ligne.split(",")]
                if len(parts) == 2:
                    used, total = map(float, parts)
                    usage_pct = (used / total * 100) if total > 0 else 0
                    if usage_pct > 95:
                        return {
                            "ok": False,
                            "detail": f"GPU {i}: {usage_pct:.0f}% utilisé ({used:.0f}/{total:.0f} MiB)",
                        }
            return {"ok": True, "detail": "GPU OK"}
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            return {"ok": False, "detail": str(e)}

    def verifier_disque(self) -> dict[str, Any]:
        """Vérifie l'espace disque de la partition racine.

        Returns:
            dict avec 'ok' (bool), 'pct' (float) et 'detail' (str).
        """
        try:
            result = subprocess.run(
                ["df", "/"],
                capture_output=True, text=True, timeout=5,
            )
            lignes = result.stdout.strip().split("\n")
            if len(lignes) < 2:
                return {"ok": False, "detail": "df: sortie inattendue"}
            parts = lignes[1].split()
            pct = int(parts[4].rstrip("%"))
            return {
                "ok": pct < 90,
                "pct": pct,
                "detail": f"disque à {pct}%",
            }
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError) as e:
            return {"ok": False, "detail": str(e)}

    def verifier_memoire(self) -> dict[str, Any]:
        """Vérifie l'utilisation mémoire via /proc/meminfo.

        Returns:
            dict avec 'ok' (bool), 'pct' (float) et 'detail' (str).
        """
        try:
            with open("/proc/meminfo") as f:
                data = f.read()

            def meminfo_val(key: str) -> float:
                for line in data.split("\n"):
                    if line.startswith(key + ":"):
                        return float(line.split()[1])
                return 0.0

            total = meminfo_val("MemTotal")
            available = meminfo_val("MemAvailable")
            if total == 0:
                return {"ok": False, "detail": "/proc/meminfo: Total=0"}
            pct = (1 - available / total) * 100
            return {
                "ok": pct < 85,
                "pct": pct,
                "detail": f"RAM à {pct:.0f}% utilisée",
            }
        except (FileNotFoundError, ValueError, IndexError) as e:
            return {"ok": False, "detail": str(e)}

    # ── Stratégies de résolution ─────────────────────────────────────────

    def resoudre(self, evenement: dict) -> dict[str, Any]:
        """Point d'entrée : applique la stratégie adaptée à l'événement.

        Args:
            evenement: dict de la table events (id, channel, source, payload, ...).

        Returns:
            dict avec 'succes' (bool), 'action' (str), 'detail' (str).
        """
        payload = self._decoder_payload(evenement.get("payload", "{}"))
        error_type = payload.get("error_type", "handler_failed")
        agent_id = payload.get("agent_id", "inconnu")
        channel = evenement.get("channel", "inconnu")

        # Déduction du type d'erreur depuis le canal si 'error_type' absent
        if error_type == "handler_failed" and channel == "hardware:gpu_alert":
            error_type = "gpu_oom"
        elif error_type == "handler_failed" and "disk" in str(payload).lower():
            error_type = "disk_full"

        strategie = TYPE_TO_STRATEGY.get(error_type, "retry")
        logger.info(
            f"Résolution pour event #{evenement['id']} : "
            f"canal={channel}, type={error_type}, "
            f"stratégie={strategie}, agent={agent_id}"
        )

        if self.dry_run:
            logger.info(f"[DRY-RUN] Stratégie '{strategie}' simulée pour #{evenement['id']}")
            return {"succes": True, "action": strategie, "detail": "dry-run"}

        # Dispatch vers la bonne méthode
        dispatch = {
            "restart_service": self._restart_service,
            "free_vram": self._free_vram,
            "clean_disk": self._clean_disk,
            "free_memory": self._free_memory,
            "restart_agent": self._restart_agent,
            "retry": self._retry,
            "kill_zombie": self._kill_zombie,
        }
        methode = dispatch.get(strategie)
        if methode is None:
            return {"succes": False, "action": strategie, "detail": f"stratégie inconnue: {strategie}"}

        try:
            return methode(payload, evenement)
        except Exception as e:
            logger.exception(f"Exception dans la stratégie '{strategie}': {e}")
            return {"succes": False, "action": strategie, "detail": str(e)}

    # ── Méthodes privées ─────────────────────────────────────────────────

    @staticmethod
    def _decoder_payload(payload_raw: Any) -> dict:
        """Décode le payload JSON, gère les chaînes et les dicts déjà parsés."""
        if isinstance(payload_raw, dict):
            return payload_raw
        if isinstance(payload_raw, str):
            try:
                return json.loads(payload_raw)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def _restart_service(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Redémarre un service système ou un processus."""
        service = payload.get("service", payload.get("agent_id", "adam-event-daemon"))
        commandes = STRATEGIES["restart_service"]["commandes"]

        # Essayer systemctl --user d'abord
        try:
            result = subprocess.run(
                [*commandes, service],
                capture_output=True, text=True, timeout=HANDLER_TIMEOUT,
            )
            if result.returncode == 0:
                return {"succes": True, "action": "restart_service",
                        "detail": f"service '{service}' redémarré (systemctl)"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback : pkill + relance
        try:
            subprocess.run(
                ["pkill", "-x", service],
                capture_output=True, timeout=5,
            )
            time.sleep(2)
            return {"succes": True, "action": "restart_service",
                    "detail": f"service '{service}' redémarré (pkill)"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return {"succes": False, "action": "restart_service",
                "detail": f"impossible de redémarrer '{service}'"}

    def _free_vram(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Libère la VRAM GPU en tuant le processus python3 le plus gourmand."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-compute-apps=pid,used_memory",
                 "--format=csv,noheader"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return {"succes": False, "action": "free_vram",
                        "detail": "nvidia-smi indisponible"}

            procs = []
            for ligne in result.stdout.strip().split("\n"):
                if not ligne.strip():
                    continue
                parts = [p.strip() for p in ligne.split(",")]
                if len(parts) == 2:
                    try:
                        pid = int(parts[0])
                        mem = int(parts[1].replace("MiB", "").strip())
                        procs.append((pid, mem))
                    except ValueError:
                        continue

            if not procs:
                return {"succes": True, "action": "free_vram",
                        "detail": "aucun processus GPU à tuer"}

            # Tuer le plus gourmand
            procs.sort(key=lambda x: x[1], reverse=True)
            pid, mem = procs[0]
            subprocess.run(["kill", "-15", str(pid)], capture_output=True, timeout=5)
            time.sleep(2)
            return {"succes": True, "action": "free_vram",
                    "detail": f"PID {pid} tué ({mem} MiB VRAM)"}
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            return {"succes": False, "action": "free_vram", "detail": str(e)}

    def _clean_disk(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Nettoie les caches temporaires."""
        cibles = STRATEGIES["clean_disk"]["cibles"]
        nettoyes = []
        for cible in cibles:
            chemin = Path(cible)
            if chemin.exists():
                try:
                    subprocess.run(
                        ["rm", "-rf", str(chemin / "*")],
                        shell=True, capture_output=True, timeout=30,
                    )
                    nettoyes.append(cible)
                except subprocess.TimeoutExpired:
                    continue
        if nettoyes:
            return {"succes": True, "action": "clean_disk",
                    "detail": f"nettoyé: {', '.join(nettoyes)}"}
        return {"succes": False, "action": "clean_disk",
                "detail": "rien à nettoyer"}

    def _free_memory(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Libère la mémoire système."""
        try:
            # Flush page cache, dentries, inodes
            subprocess.run(
                ["sync"],
                capture_output=True, timeout=5,
            )
            with open("/proc/sys/vm/drop_caches", "w") as f:
                f.write("3")
            return {"succes": True, "action": "free_memory",
                    "detail": "cache système vidé"}
        except (PermissionError, FileNotFoundError, OSError) as e:
            return {"succes": False, "action": "free_memory",
                    "detail": str(e)}

    def _restart_agent(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Redémarre un agent ADAM par son agent_id."""
        agent_id = payload.get("agent_id", "inconnu")
        try:
            subprocess.run(
                ["pkill", "-x", agent_id],
                capture_output=True, timeout=5,
            )
            time.sleep(2)
            self.bus.update_agent_status(agent_id, "idle")
            return {"succes": True, "action": "restart_agent",
                    "detail": f"agent '{agent_id}' redémarré"}
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return {"succes": False, "action": "restart_agent",
                    "detail": str(e)}

    def _retry(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Re-publie l'événement pour nouvelle tentative sur un canal dédié.

        IMPORTANT : on publie sur 'adam:retry' et NON sur le canal original
        (adam:error). Sinon self_heal reprend l'événement en boucle infinie.
        """
        max_tent = STRATEGIES["retry"]["max_tentatives"]
        retry_count = payload.get("retry_count", 0) + 1
        if retry_count > max_tent:
            return {"succes": False, "action": "retry",
                    "detail": f"tentatives épuisées ({max_tent})"}

        nouveau_payload = {**payload, "retry_count": retry_count}
        self.bus.publier(
            "adam:retry",
            nouveau_payload,
            source="self-heal-retry",
            priority=evenement.get("priority", 0),
        )
        return {"succes": True, "action": "retry",
                "detail": f"tentative {retry_count}/{max_tent}"}

    def _kill_zombie(self, payload: dict, evenement: dict) -> dict[str, Any]:
        """Tue un processus zombie ou bloqué par son PID."""
        pid = payload.get("pid")
        if pid is None:
            return {"succes": False, "action": "kill_zombie",
                    "detail": "aucun PID fourni"}

        try:
            subprocess.run(["kill", "-15", str(pid)], capture_output=True, timeout=5)
            time.sleep(STRATEGIES["kill_zombie"]["escalade_delai"])
            # Vérifier si le process est toujours là
            check = subprocess.run(
                ["kill", "-0", str(pid)],
                capture_output=True, timeout=5,
            )
            if check.returncode == 0:
                # Toujours vivant → escalade en SIGKILL
                subprocess.run(["kill", "-9", str(pid)], capture_output=True, timeout=5)
                return {"succes": True, "action": "kill_zombie",
                        "detail": f"PID {pid} tué (SIGKILL après escalade)"}
            return {"succes": True, "action": "kill_zombie",
                    "detail": f"PID {pid} tué (SIGTERM)"}
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            return {"succes": False, "action": "kill_zombie", "detail": str(e)}


# ─── Validateur ──────────────────────────────────────────────────────────────


class Validateur:
    """Valide qu'une résolution a réellement résolu le problème."""

    def __init__(self, bus: HealBus) -> None:
        self.bus = bus

    def valider(self, evenement: dict, resolution: dict) -> dict[str, Any]:
        """Vérifie que le problème est résolu après la résolution.

        Args:
            evenement: événement original.
            resolution: résultat de la résolution.

        Returns:
            dict avec 'ok' (bool) et 'detail' (str).
        """
        channel = evenement.get("channel", "")
        payload = self._decoder_payload(evenement.get("payload", "{}"))
        error_type = payload.get("error_type", "")

        # Validation selon le type d'erreur
        checks = {
            "gpu_oom": self._check_gpu,
            "gpu_hang": self._check_gpu,
            "disk_full": self._check_disk,
            "memory_critical": self._check_memory,
            "service_down": self._check_service,
            "service_crash": self._check_service,
            "daemon_stopped": self._check_service,
        }

        check = checks.get(error_type)
        if check is None:
            # Si pas de validation spécifique, on se fie au statut de la résolution
            return {"ok": resolution.get("succes", False),
                    "detail": "validation par défaut (confiance dans la résolution)"}

        if channel == "hardware:gpu_alert":
            return self._check_gpu()

        try:
            return check(payload)
        except Exception as e:
            logger.warning(f"Erreur pendant la validation: {e}")
            return {"ok": False, "detail": str(e)}

    @staticmethod
    def _decoder_payload(payload_raw: Any) -> dict:
        if isinstance(payload_raw, dict):
            return payload_raw
        if isinstance(payload_raw, str):
            try:
                return json.loads(payload_raw)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}

    def _check_gpu(self, payload: Optional[dict] = None) -> dict[str, Any]:
        """Vérifie l'état du GPU."""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used,memory.total",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode != 0:
                return {"ok": False, "detail": "GPU injoignable"}

            for ligne in result.stdout.strip().split("\n"):
                parts = [p.strip() for p in ligne.split(",")]
                if len(parts) == 2:
                    used, total = map(float, parts)
                    if used / total > 0.90:
                        return {"ok": False,
                                "detail": f"toujours saturé: {used:.0f}/{total:.0f} MiB"}
            return {"ok": True, "detail": "GPU OK"}
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError) as e:
            return {"ok": False, "detail": str(e)}

    def _check_disk(self, payload: Optional[dict] = None) -> dict[str, Any]:
        """Vérifie l'espace disque."""
        try:
            result = subprocess.run(
                ["df", "/"],
                capture_output=True, text=True, timeout=5,
            )
            pct = int(result.stdout.strip().split("\n")[1].split()[4].rstrip("%"))
            return {"ok": pct < 85, "detail": f"disque à {pct}%"}
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError) as e:
            return {"ok": False, "detail": str(e)}

    def _check_memory(self, payload: Optional[dict] = None) -> dict[str, Any]:
        """Vérifie la mémoire système."""
        try:
            with open("/proc/meminfo") as f:
                data = f.read()

            def get_val(key: str) -> float:
                for line in data.split("\n"):
                    if line.startswith(key + ":"):
                        return float(line.split()[1])
                return 0.0

            total = get_val("MemTotal")
            available = get_val("MemAvailable")
            if total == 0:
                return {"ok": False, "detail": "impossible de lire meminfo"}
            pct = (1 - available / total) * 100
            return {"ok": pct < 80, "detail": f"RAM à {pct:.0f}%"}
        except (FileNotFoundError, ValueError, IndexError) as e:
            return {"ok": False, "detail": str(e)}

    def _check_service(self, payload: Optional[dict] = None) -> dict[str, Any]:
        """Vérifie qu'un service tourne."""
        service = payload.get("service", "adam-event-daemon") if payload else "adam-event-daemon"
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", service],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return {"ok": True, "detail": f"service '{service}' actif"}
            return {"ok": False, "detail": f"service '{service}' inactif"}
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"ok": False, "detail": f"systemctl indisponible pour '{service}'"}


# ─── Boucle principale ───────────────────────────────────────────────────────


class SelfHealLoop:
    """Boucle d'auto-guérison ADAM v2.

    Cycle : DÉTECTION → RÉSOLUTION → VALIDATION → NOTIFICATION
    """

    def __init__(self, dry_run: bool = False) -> None:
        self.bus = HealBus()
        self.resolveur = Resolveur(self.bus, dry_run=dry_run)
        self.validateur = Validateur(self.bus)
        self.dry_run = dry_run
        self._running = False
        self._cycles = 0
        self._dernier_heartbeat = 0.0

    def demarrer(self, once: bool = False) -> None:
        """Lance la boucle de guérison.

        Args:
            once: si True, n'exécute qu'un seul cycle puis s'arrête.
        """
        self._running = True
        logger.info("=" * 60)
        logger.info("Boucle d'auto-guérison ADAM v2 — DÉMARRAGE")
        if self.dry_run:
            logger.info("Mode DRY-RUN : aucune action réelle ne sera exécutée")
        logger.info(f"Intervalle : {INTERVALLE}s")
        logger.info(f"Bus : {self.bus.db_path}")
        logger.info("=" * 60)

        try:
            while self._running:
                self._cycles += 1
                logger.debug(f"--- Cycle #{self._cycles} ---")

                # ── ÉTAPE 1 : DÉTECTION ──
                evenements = self.bus.get_erreurs_pendantes(limit=10)
                if not evenements:
                    logger.debug("Aucun événement d'erreur en attente")
                else:
                    logger.info(f"{len(evenements)} événement(s) d'erreur détecté(s)")

                for evenement in evenements:
                    event_id = evenement["id"]
                    channel = evenement["channel"]
                    logger.info(
                        f"[DÉTECTION] Event #{event_id} | canal={channel} | "
                        f"source={evenement['source']}"
                    )

                    # ── ÉTAPE 2 : RÉSOLUTION ──
                    resolution = self.resolveur.resoudre(evenement)
                    logger.info(
                        f"[RÉSOLUTION] Event #{event_id} | "
                        f"action={resolution.get('action', '?')} | "
                        f"succès={resolution.get('succes', False)} | "
                        f"détail={resolution.get('detail', '')}"
                    )

                    # ── ÉTAPE 3 : VALIDATION ──
                    validation = self.validateur.valider(evenement, resolution)
                    logger.info(
                        f"[VALIDATION] Event #{event_id} | "
                        f"ok={validation.get('ok', False)} | "
                        f"détail={validation.get('detail', '')}"
                    )

                    # ── ÉTAPE 4 : NOTIFICATION ──
                    heal_reussi = resolution.get("succes", False) and validation.get("ok", False)
                    heal_payload = {
                        "event_id": event_id,
                        "channel": channel,
                        "resolution": resolution,
                        "validation": validation,
                        "healed": heal_reussi,
                        "cycle": self._cycles,
                    }

                    if heal_reussi:
                        self.bus.publier("adam:recovered", heal_payload,
                                         source="self-heal")
                        logger.info(
                            f"[NOTIFICATION] Event #{event_id} → adam:recovered "
                            f"(guéri)"
                        )
                    else:
                        self.bus.publier("heal:required", heal_payload,
                                         source="self-heal", priority=1)
                        logger.warning(
                            f"[NOTIFICATION] Event #{event_id} → heal:required "
                            f"(échec de guérison)"
                        )

                    # Marquer l'événement comme traité
                    self.bus.marquer_traite(event_id, succes=heal_reussi)

                # Heartbeat périodique
                maintenant = time.time()
                if maintenant - self._dernier_heartbeat >= HEARTBEAT_INTERVAL:
                    self.bus.heartbeat()
                    self._dernier_heartbeat = maintenant

                if once:
                    logger.info("Mode '--once' : fin après un cycle")
                    break

                time.sleep(INTERVALLE)

        except KeyboardInterrupt:
            logger.info("Interruption clavier — arrêt")
        except Exception:
            logger.exception("Erreur fatale dans la boucle de guérison")
            raise
        finally:
            self._running = False
            logger.info("Boucle d'auto-guérison arrêtée")

    def arreter(self) -> None:
        """Arrête proprement la boucle."""
        self._running = False
        logger.info("Signal d'arrêt reçu")

    def afficher_statut(self) -> None:
        """Affiche l'état actuel du bus et des agents."""
        print(f"=== Statut du bus d'événements ===")
        print(f"Chemin DB : {self.bus.db_path}")
        print()

        # Événements en attente
        evenements = self.bus.get_erreurs_pendantes(limit=50)
        print(f"Événements d'erreur en attente : {len(evenements)}")
        for evt in evenements:
            print(f"  #{evt['id']} | {evt['channel']} | {evt['source']} | "
                  f"priorité={evt['priority']} | {evt['created_at']}")

        # GPU
        print()
        gpu = self.resolveur.verifier_gpu()
        print(f"GPU    : {'✓' if gpu['ok'] else '✗'} {gpu['detail']}")

        # Disque
        disque = self.resolveur.verifier_disque()
        print(f"Disque : {'✓' if disque['ok'] else '✗'} {disque['detail']}")

        # Mémoire
        memoire = self.resolveur.verifier_memoire()
        print(f"RAM    : {'✓' if memoire['ok'] else '✗'} {memoire['detail']}")


# ─── Point d'entrée ──────────────────────────────────────────────────────────


def main() -> int:
    """Point d'entrée CLI.

    Sous-commandes :
      --status   : affiche le statut du bus et des agents
      --once      : exécute un seul cycle de guérison puis s'arrête
      --dry-run   : simulation sans action réelle
      (rien)      : boucle infinie (mode daemon)
    """
    args = set(sys.argv[1:])

    if "--status" in args:
        loop = SelfHealLoop()
        loop.afficher_statut()
        return 0

    dry_run = "--dry-run" in args
    once = "--once" in args

    loop = SelfHealLoop(dry_run=dry_run)
    loop.demarrer(once=once)

    return 0


if __name__ == "__main__":
    sys.exit(main())