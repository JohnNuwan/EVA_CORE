#!/usr/bin/env python3
"""
ADAM-EVOLUTION — Agent d'évolution des règles Praetor.

Écoute le canal `adam:healed` publié par self_heal.py après chaque guérison
réussie. Transforme chaque guérison en règle Praetor réutilisable, puis
applique une sélection naturelle (inspirée d'AlphaEvolve de DeepMind) :

  1. CRÉATION — Chaque guérison réussie génère une règle Praetor.
     Si une règle similaire existe déjà, son compteur d'occurrences augmente.
  2. ÉVALUATION — Chaque règle a un score de fitness basé sur son taux de
     succès glissant (20 dernières exécutions). Les règles qui marchent
     voient leur score augmenter, les échecs le diminuent.
  3. SÉLECTION — Les règles dont le score tombe sous un seuil (0.3) sont
     marquées "deprecated" et supprimées après une période de grâce.
  4. MUTATION — Si une règle échoue plusieurs fois, sa correction peut être
     mutée (variante générée à partir des stratégies self_heal connues).

Boucle cible :
  Erreur → adam:error → self_heal → praetor → evolution → auto-résolu
                                        ↑ règle créée ici ↑

Usage :
  python3 adam-evolution.py              # boucle continue (daemon)
  python3 adam-evolution.py --once       # un seul cycle puis exit
  python3 adam-evolution.py --status     # affiche l'état des règles
  python3 adam-evolution.py --dry-run    # simulation sans écriture
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import signal
import sqlite3
import sys
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Configuration ──────────────────────────────────────────────────────────

ADAM_V2_DIR = Path(os.environ.get("ADAM_V2_DIR", Path.home() / "eva-adam-v2"))
DB_PATH = ADAM_V2_DIR / "event_bus.db"

# Fichiers Praetor
PRAETOR_DIR = Path.home() / ".praetor"
LEARNED_RULES_FILE = PRAETOR_DIR / "learned_rules.json"
BUILTIN_RULES_FILE = PRAETOR_DIR / "rules.json"

# Fichier de fitness des règles d'évolution
EVOLUTION_DIR = ADAM_V2_DIR / "evolution"
EVOLUTION_DIR.mkdir(parents=True, exist_ok=True)
RULE_FITNESS_FILE = EVOLUTION_DIR / "rule_fitness.json"

# Paramètres d'évolution
HISTORY_LEN = 20          # Historique glissant par règle
DEPRECATION_THRESHOLD = 0.3   # Score < 0.3 → deprecated
GRACE_PERIOD_SEC = 300    # 5 min de grâce avant suppression définitive
POLL_INTERVAL = 10        # Secondes entre chaque cycle
HEARTBEAT_INTERVAL = 60   # Secondes entre chaque heartbeat
AGENT_ID = "adam-evolution"
CHANNEL_LISTEN = "adam:healed"

# Mapping canal → pattern d'erreur praetor
CANAL_PATTERN_MAP = {
    "hardware:gpu_alert": r"gpu_alert|vram_high|gpu_\w+",
    "adam:error": r"error|crash|fail|panic|exception",
    "service:down": r"service_down|process_not_found|timeout",
    "disk:full": r"disk_full|no_space|enospc",
    "file:changed": r"file_changed|config_modified",
}

# Mapping stratégies self_heal → corrections praetor connues
STRATEGIE_CORRECTION_MAP = {
    "restart_service": "systemctl restart SERVICE || pkill -f PROCESS && sleep 2 && python3 SCRIPT &",
    "clean_disk": "find /tmp /var/log -type f -mtime +7 -delete; journalctl --vacuum-size=100M",
    "free_vram": "nvidia-smi --query-compute-apps=pid --format=csv,noheader | xargs -r kill -9",
    "retry": "sleep 5 && RETRY_COMMAND",
    "restart_docker": "docker restart CONTAINER",
    "kill_zombie": "kill -9 PID",
    "clear_cache": "sync && echo 3 > /proc/sys/vm/drop_caches",
}

# ─── Logging ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [evolution] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("adam-evolution")

# ─── Détecteur d'arrêt propre ───────────────────────────────────────────────

_running = True


def _signal_handler(signum: int, frame: Any) -> None:
    global _running
    _running = False
    logger.info(f"Signal {signum} reçu — arrêt en cours...")


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ─── Gestion du fichier de fitness des règles ───────────────────────────────


def _load_rule_fitness() -> dict[str, Any]:
    """Charge les scores de fitness des règles d'évolution."""
    default: dict[str, Any] = {}
    if RULE_FITNESS_FILE.exists():
        try:
            data = json.loads(RULE_FITNESS_FILE.read_text(encoding="utf-8"))
            return data
        except (json.JSONDecodeError, OSError) as e:
            logger.warning(f"Impossible de charger rule_fitness.json: {e}")
    return default


def _save_rule_fitness(data: dict[str, Any]) -> None:
    """Sauvegarde les scores de fitness des règles."""
    try:
        RULE_FITNESS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning(f"Impossible de sauvegarder rule_fitness.json: {e}")


def _init_rule_fitness(rule_id: str) -> dict[str, Any]:
    """Initialise le fitness pour une nouvelle règle."""
    return {
        "score": 1.0,
        "history": [],
        "total": 0,
        "successes": 0,
        "failures": 0,
        "deprecated": False,
        "deprecated_at": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used": None,
        "occurrences": 0,
    }


def _update_rule_fitness(
    rule_id: str, succes: bool, fitness_data: dict[str, Any]
) -> dict[str, Any]:
    """Met à jour le score de fitness d'une règle après utilisation.

    Calcul inspiré d'AlphaEvolve :
    - Score = moyenne de l'historique glissant (20 dernières exécutions)
    - Succès = 1.0, Échec = 0.0
    - Si score < DEPRECATION_THRESHOLD → deprecated
    """
    if rule_id not in fitness_data:
        fitness_data[rule_id] = _init_rule_fitness(rule_id)

    entry = fitness_data[rule_id]
    entry["history"].append(1 if succes else 0)
    if len(entry["history"]) > HISTORY_LEN:
        entry["history"].pop(0)

    entry["total"] += 1
    if succes:
        entry["successes"] += 1
    else:
        entry["failures"] += 1

    entry["last_used"] = datetime.now(timezone.utc).isoformat()
    entry["score"] = sum(entry["history"]) / len(entry["history"])

    # Vérifier la dépréciation
    if entry["score"] < DEPRECATION_THRESHOLD and not entry["deprecated"]:
        entry["deprecated"] = True
        entry["deprecated_at"] = datetime.now(timezone.utc).isoformat()
        logger.warning(
            f"Règle {rule_id} dépréciée (score={entry['score']:.2f})"
        )

    # Si la règle était dépréciée mais s'améliore, la réactiver
    if entry["deprecated"] and entry["score"] >= DEPRECATION_THRESHOLD:
        entry["deprecated"] = False
        entry["deprecated_at"] = None
        logger.info(
            f"Règle {rule_id} réactivée (score remonté à {entry['score']:.2f})"
        )

    return entry


# ─── Gestion des règles Praetor ─────────────────────────────────────────────


def _load_learned_rules() -> dict[str, Any]:
    """Charge les règles apprises de Praetor."""
    if LEARNED_RULES_FILE.exists():
        try:
            return json.loads(LEARNED_RULES_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"version": "2.0", "rules": []}


def _save_learned_rules(data: dict[str, Any]) -> None:
    """Sauvegarde les règles apprises de Praetor."""
    PRAETOR_DIR.mkdir(parents=True, exist_ok=True)
    LEARNED_RULES_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _load_builtin_rules() -> list[dict[str, Any]]:
    """Charge les règles builtin pour éviter les doublons."""
    if BUILTIN_RULES_FILE.exists():
        try:
            data = json.loads(BUILTIN_RULES_FILE.read_text(encoding="utf-8"))
            return data.get("rules", [])
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _find_existing_rule(
    rules: list[dict[str, Any]], pattern: str
) -> dict[str, Any] | None:
    """Cherche une règle existante par pattern (match exact ou regex)."""
    for rule in rules:
        if rule.get("pattern") == pattern:
            return rule
        # Match aussi si le pattern existant contient le nouveau
        try:
            if re.search(rule.get("pattern", ""), pattern):
                return rule
        except re.error:
            continue
    return None


def _generer_pattern(canal: str, resolution: dict[str, Any]) -> str:
    """Génère un pattern d'erreur praetor à partir du canal et de la résolution.

    Le pattern doit matcher les futures erreurs similaires pour que praetor
    puisse appliquer la correction automatiquement.
    """
    # Pattern de base selon le canal
    base_pattern = CANAL_PATTERN_MAP.get(canal, r"error|crash|fail")

    # Affiner selon l'action de résolution
    action = resolution.get("action", "")
    if action == "free_vram":
        return r"vram_high|gpu_alert|out_of_memory|cuda.*error"
    elif action == "restart_service":
        return r"service_down|process_not_found|connection_refused|timeout"
    elif action == "clean_disk":
        return r"disk_full|no_space|enospc|disk_space"
    elif action == "retry":
        return r"timeout|connection_reset|temporary_failure|retry"
    elif action == "restart_docker":
        return r"docker.*unhealthy|container.*restart|docker.*error"
    elif action == "kill_zombie":
        return r"zombie|defunct|process.*stale"
    elif action == "clear_cache":
        return r"cache.*full|memory.*pressure|oom"

    return base_pattern


def _generer_correction(resolution: dict[str, Any]) -> str:
    """Génère une commande de correction praetor à partir de la résolution."""
    action = resolution.get("action", "retry")
    return STRATEGIE_CORRECTION_MAP.get(action, "ANALYZE")


def _generer_description(
    canal: str, resolution: dict[str, Any], fitness: dict[str, Any]
) -> str:
    """Génère une description lisible pour la règle."""
    action = resolution.get("action", "inconnu")
    detail = resolution.get("detail", "")
    score = fitness.get("score", 1.0)
    total = fitness.get("total", 0)

    desc = f"Auto-générée par adam-evolution (canal={canal}, stratégie={action})"
    if detail:
        desc += f" — {detail}"
    desc += f" [fitness={score:.2f}, n={total}]"
    return desc


def creer_regle_praetor(
    event_id: int,
    canal: str,
    resolution: dict[str, Any],
    fitness: dict[str, Any],
    dry_run: bool = False,
) -> str | None:
    """Crée ou met à jour une règle Praetor à partir d'un event adam:healed.

    Returns:
        L'ID de la règle créée/mise à jour, ou None si ignoré.
    """
    # Ignorer les guérisons sans succès
    if not resolution.get("succes", False):
        logger.debug(
            f"Event #{event_id} ignoré (guérison sans succès)"
        )
        return None

    pattern = _generer_pattern(canal, resolution)
    correction = _generer_correction(resolution)
    description = _generer_description(canal, resolution, fitness)
    action = resolution.get("action", "inconnu")
    rule_id_base = f"evo-{action}-{canal.replace(':', '_')}"

    # Charger les règles existantes
    data = _load_learned_rules()
    rules = data.get("rules", [])

    # Vérifier les règles builtin pour éviter les doublons
    builtin_rules = _load_builtin_rules()
    for br in builtin_rules:
        try:
            if re.search(br.get("pattern", ""), pattern):
                logger.info(
                    f"Règle builtin '{br.get('id')}' couvre déjà ce pattern "
                    f"— skip"
                )
                return None
        except re.error:
            continue

    # Chercher une règle existante
    existing = _find_existing_rule(rules, pattern)
    if existing:
        # Mettre à jour les occurrences et le last_seen
        existing["occurrences"] = existing.get("occurrences", 0) + 1
        existing["last_seen"] = datetime.now(timezone.utc).isoformat().split("T")[0]
        existing["description"] = description  # Mettre à jour avec le fitness
        rule_id = existing["id"]
        logger.info(
            f"Règle existante {rule_id} mise à jour "
            f"(occurrences={existing['occurrences']})"
        )
    else:
        # Créer une nouvelle règle
        rule_id = rule_id_base
        # S'assurer de l'unicité de l'ID
        existing_ids = {r.get("id") for r in rules}
        if rule_id in existing_ids:
            rule_id = f"{rule_id_base}-{len(rules) + 1:03d}"

        new_rule = {
            "id": rule_id,
            "pattern": pattern,
            "description": description,
            "severity": "warning",
            "correction": correction,
            "source": "adam-evolution",
            "first_seen": datetime.now(timezone.utc).isoformat().split("T")[0],
            "last_seen": datetime.now(timezone.utc).isoformat().split("T")[0],
            "occurrences": 1,
            "strategie": action,
            "fitness_score": fitness.get("score", 1.0),
            "event_origin": event_id,
        }
        rules.append(new_rule)
        data["rules"] = rules
        data["version"] = "2.0"
        data["last_evolution"] = datetime.now(timezone.utc).isoformat()

        logger.info(
            f"NOUVELLE RÈGLE créée : {rule_id} "
            f"(pattern='{pattern}', correction='{correction[:50]}...')"
        )

    if not dry_run:
        _save_learned_rules(data)

    return rule_id


# ─── Sélection naturelle ────────────────────────────────────────────────────


def selection_naturelle(
    dry_run: bool = False
) -> dict[str, list[str]]:
    """Évalue toutes les règles et supprime les obsolètes.

    Parcourt les règles apprises, vérifie leur fitness, et supprime
    celles qui sont dépréciées depuis plus de GRACE_PERIOD_SEC.

    Returns:
        Dict avec 'supprimees' et 'depreciees' (listes d'IDs).
    """
    fitness_data = _load_rule_fitness()
    rules_data = _load_learned_rules()
    rules = rules_data.get("rules", [])

    now = datetime.now(timezone.utc)
    supprimees: list[str] = []
    depreciees: list[str] = []
    gardez: list[dict[str, Any]] = []

    for rule in rules:
        rule_id = rule.get("id", "")
        fitness = fitness_data.get(rule_id)

        if not fitness:
            # Pas de fitness tracking → garder la règle
            gardez.append(rule)
            continue

        if fitness.get("deprecated", False):
            deprecated_at = fitness.get("deprecated_at")
            if deprecated_at:
                try:
                    dep_time = datetime.fromisoformat(deprecated_at)
                    age = (now - dep_time).total_seconds()
                    if age > GRACE_PERIOD_SEC:
                        supprimees.append(rule_id)
                        logger.info(
                            f"SÉLECTION: Règle {rule_id} supprimée "
                            f"(dépréciée depuis {int(age)}s, "
                            f"score={fitness.get('score', 0):.2f})"
                        )
                        continue
                    else:
                        depreciees.append(rule_id)
                        gardez.append(rule)
                        continue
                except (ValueError, TypeError):
                    pass
        else:
            # Mettre à jour le fitness_score dans la règle
            rule["fitness_score"] = fitness.get("score", 1.0)
            gardez.append(rule)

    # Sauvegarder si des changements
    if supprimees:
        rules_data["rules"] = gardez
        rules_data["last_selection"] = datetime.now(timezone.utc).isoformat()
        if not dry_run:
            _save_learned_rules(rules_data)
        logger.info(
            f"SÉLECTION NATURELLE: {len(supprimees)} supprimée(s), "
            f"{len(depreciees)} dépréciée(s), {len(gardez)} conservée(s)"
        )

    return {"supprimees": supprimees, "depreciees": depreciees}


# ─── Wrapper de bus d'events (similaire à HealBus de self_heal) ──────────────


class EvolutionBus:
    """Wrapper d'accès au bus d'events pour adam-evolution."""

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def get_healed_events(
        self, last_id: int = 0
    ) -> list[sqlite3.Row]:
        """Récupère les events adam:healed non traités par l'évolution.

        Cherche les events sur le canal adam:healed avec status 'pending'
        ou 'done' (car ils sont publiés par self_heal et déjà marqués done).
        On utilise un curseur last_id pour ne traiter chaque event qu'une fois.
        """
        conn = self._get_conn()
        rows = conn.execute(
            """SELECT id, source, payload, created_at, status
               FROM events
               WHERE channel = ? AND id > ?
               ORDER BY id ASC""",
            (CHANNEL_LISTEN, last_id),
        ).fetchall()
        return rows

    def marquer_traite(self, event_id: int, succes: bool = True) -> None:
        """Marque un event comme traité par l'évolution."""
        conn = self._get_conn()
        now = datetime.now(timezone.utc).isoformat()
        status = "done" if succes else "failed"
        conn.execute(
            """UPDATE events SET processed_at = ?, status = ?
               WHERE id = ?""",
            (now, status, event_id),
        )
        conn.commit()

    def publier(
        self, channel: str, payload: dict, source: str = AGENT_ID
    ) -> int:
        """Publie un event sur le bus."""
        conn = sqlite3.connect(str(self.db_path))
        now = datetime.now(timezone.utc).isoformat()
        cursor = conn.execute(
            """INSERT INTO events (channel, source, payload, priority, created_at, status)
               VALUES (?, ?, ?, 0, ?, 'pending')""",
            (channel, source, json.dumps(payload, ensure_ascii=False), now),
        )
        conn.commit()
        event_id = cursor.lastrowid
        conn.close()
        return event_id

    def heartbeat(self) -> None:
        """Publie un heartbeat sur le bus."""
        self.publier("adam:heartbeat", {
            "agent_id": AGENT_ID,
            "pid": os.getpid(),
            "status": "running",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })


# ─── Agent principal ────────────────────────────────────────────────────────


class AdamEvolution:
    """Agent adam-evolution : écoute adam:healed, crée et fait évoluer les règles."""

    def __init__(
        self,
        dry_run: bool = False,
        once: bool = False,
    ) -> None:
        self.dry_run = dry_run
        self.once = once
        self.bus = EvolutionBus()
        self._last_id = self._load_cursor()  # Curseur persistant
        self._cycles = 0
        self._dernier_heartbeat = 0.0
        self._regle_stats = {"creees": 0, "mises_a_jour": 0, "supprimees": 0}

    def _load_cursor(self) -> int:
        """Charge le curseur du dernier event traité."""
        cursor_file = EVOLUTION_DIR / "evolution_cursor.txt"
        if cursor_file.exists():
            try:
                return int(cursor_file.read_text().strip())
            except (ValueError, OSError):
                pass
        return 0

    def _save_cursor(self) -> None:
        """Sauvegarde le curseur du dernier event traité."""
        cursor_file = EVOLUTION_DIR / "evolution_cursor.txt"
        try:
            cursor_file.write_text(str(self._last_id))
        except OSError as e:
            logger.warning(f"Impossible de sauvegarder le curseur: {e}")

    def _process_healed_event(self, row: sqlite3.Row) -> None:
        """Traite un event adam:healed individuel."""
        event_id = row["id"]
        raw_payload = row["source"]  # Le JSON est dans 'source' (format HealBus)

        try:
            payload = json.loads(raw_payload) if raw_payload else {}
        except json.JSONDecodeError:
            logger.warning(f"Event #{event_id} : payload JSON invalide — skip")
            self.bus.marquer_traite(event_id, succes=False)
            return

        # Vérifier que c'est bien une guérison réussie
        healed = payload.get("healed", False)
        resolution = payload.get("resolution", {})
        canal_origine = payload.get("channel", "unknown")
        strategie = payload.get("strategie", "inconnu")
        fitness_payload = payload.get("fitness", {})

        if not healed:
            logger.debug(
                f"Event #{event_id} : healed=False — skip"
            )
            self.bus.marquer_traite(event_id, succes=True)
            return

        logger.info(
            f"Traitement event #{event_id} : canal_origine={canal_origine}, "
            f"stratégie={strategie}, fitness_score={fitness_payload.get('score', '?')}"
        )

        # Créer ou mettre à jour la règle praetor
        rule_id = creer_regle_praetor(
            event_id=event_id,
            canal=canal_origine,
            resolution=resolution,
            fitness=fitness_payload,
            dry_run=self.dry_run,
        )

        if rule_id:
            # Mettre à jour le fitness de la règle
            fitness_data = _load_rule_fitness()
            _update_rule_fitness(rule_id, succes=True, fitness_data=fitness_data)
            if not self.dry_run:
                _save_rule_fitness(fitness_data)

            self._regle_stats["creees"] += 1
            logger.info(
                f"Règle {rule_id} créée/mise à jour "
                f"(fitness={fitness_data[rule_id]['score']:.2f})"
            )

            # Publier un event praetor:rule_created pour notification
            if not self.dry_run:
                self.bus.publier("praetor:rule_created", {
                    "rule_id": rule_id,
                    "pattern": _generer_pattern(canal_origine, resolution),
                    "strategie": strategie,
                    "fitness_score": fitness_data[rule_id]["score"],
                    "source_event": event_id,
                })
        else:
            logger.debug(
                f"Event #{event_id} : aucune règle créée (doublon ou skip)"
            )

        self.bus.marquer_traite(event_id, succes=True)

    def run_cycle(self) -> None:
        """Exécute un cycle de traitement."""
        self._cycles += 1

        # 1. Récupérer les nouveaux events adam:healed
        rows = self.bus.get_healed_events(last_id=self._last_id)
        if rows:
            logger.info(
                f"Cycle {self._cycles} : {len(rows)} event(s) adam:healed à traiter"
            )
        for row in rows:
            self._last_id = max(self._last_id, row["id"])
            self._process_healed_event(row)

        # Sauvegarder le curseur si on a traité des events
        if rows and not self.dry_run:
            self._save_cursor()

        # 2. Sélection naturelle (toutes les 5 cycles)
        if self._cycles % 5 == 0:
            result = selection_naturelle(dry_run=self.dry_run)
            if result["supprimees"]:
                self._regle_stats["supprimees"] += len(result["supprimees"])
            if result["supprimees"] or result["depreciees"]:
                logger.info(
                    f"Sélection: {len(result['supprimees'])} supprimée(s), "
                    f"{len(result['depreciees'])} dépréciée(s)"
                )

        # 3. Heartbeat
        maintenant = time.time()
        if maintenant - self._dernier_heartbeat >= HEARTBEAT_INTERVAL:
            self.bus.heartbeat()
            self._dernier_heartbeat = maintenant

    def run(self) -> int:
        """Boucle principale de l'agent."""
        logger.info(
            f"Démarrage adam-evolution "
            f"(dry_run={self.dry_run}, once={self.once}) — "
            f"DB={DB_PATH}"
        )

        # Heartbeat initial
        self.bus.heartbeat()
        self._dernier_heartbeat = time.time()

        while _running:
            try:
                self.run_cycle()
            except Exception as e:
                logger.error(f"Erreur cycle {self._cycles}: {e}", exc_info=True)

            if self.once:
                break

            time.sleep(POLL_INTERVAL)

        # Résumé final
        logger.info(
            f"Arrêt adam-evolution — "
            f"{self._cycles} cycles, "
            f"{self._regle_stats['creees']} règle(s) créées, "
            f"{self._regle_stats['supprimees']} supprimée(s)"
        )
        return 0

    def status(self) -> int:
        """Affiche l'état des règles d'évolution."""
        rules_data = _load_learned_rules()
        rules = rules_data.get("rules", [])
        fitness_data = _load_rule_fitness()

        # Filtrer les règles créées par adam-evolution
        evo_rules = [r for r in rules if r.get("source") == "adam-evolution"]

        print(f"\n{'='*70}")
        print(f"ADAM-EVOLUTION — État des règles")
        print(f"{'='*70}")
        print(f"Total règles apprises : {len(rules)}")
        print(f"Règles adam-evolution : {len(evo_rules)}")
        print(f"Règles dépréciées     : "
              f"{sum(1 for v in fitness_data.values() if v.get('deprecated'))}")
        print()

        if evo_rules:
            print(f"{'ID':<35} {'Pattern':<30} {'Fitness':<10} {'Occ':<5} {'Dépr'}")
            print(f"{'-'*35} {'-'*30} {'-'*10} {'-'*5} {'-'*5}")
            for rule in evo_rules:
                rid = rule["id"]
                fit = fitness_data.get(rid, {})
                score = fit.get("score", rule.get("fitness_score", 1.0))
                occ = rule.get("occurrences", 0)
                dep = "⚠️" if fit.get("deprecated") else "✅"
                pattern = rule.get("pattern", "")[:30]
                print(f"{rid:<35} {pattern:<30} {score:<10.2f} {occ:<5} {dep}")
        else:
            print("(Aucune règle adam-evolution pour le moment)")

        print()
        return 0


# ─── CLI ────────────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ADAM-EVOLUTION — Agent d'évolution des règles Praetor"
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Exécute un seul cycle puis quitte"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Simulation — aucune écriture sur disque"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Affiche l'état des règles et quitte"
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Active les logs de debug"
    )
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.status:
        return AdamEvolution().status()

    agent = AdamEvolution(dry_run=args.dry_run, once=args.once)
    return agent.run()


if __name__ == "__main__":
    sys.exit(main())
