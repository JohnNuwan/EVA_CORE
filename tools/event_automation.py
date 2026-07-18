#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Event-Driven Automation Module - Règles d'auto-remediation pour contextes OT.

Inspiré par StackStorm. Permet de définir des règles de type
"SI événement ALORS action" pour l'automatisation des réponses
aux incidents OT (PLC stop, température haute, perte comms).
"""

import json
import logging
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from agent.helios_constants import get_helios_home

logger = logging.getLogger(__name__)


# ── Structures de données ──────────────────────────────────────────────

@dataclass
class EventRule:
    """Une règle d'automatisation événementielle.

    Attributes:
        name: Nom unique de la règle.
        trigger_pattern: Pattern regex pour matcher les événements.
        action: Action à exécuter (template string ou dotted-path).
        cooldown_seconds: Temps minimum en secondes entre deux déclenchements.
        description: Description lisible de la règle.
        builtin: True si c'est une règle interne/intégrée par défaut.
    """
    name: str
    trigger_pattern: str
    action: str
    cooldown_seconds: int = 300
    description: str = ""
    builtin: bool = False


# ── Règles intégrées (built-in) OT ─────────────────────────────────────

_BUILTIN_RULES = [
    EventRule(
        name="PLC_STOP",
        trigger_pattern=r"plc\.(cpu|status)\.(stop|fault|error)",
        action="NOTIFY:maintenance+LOG:Arrêt PLC détecté sur {device_id}",
        cooldown_seconds=120,
        description="Détecte l'arrêt d'un automate PLC. Recommande backup du programme + notification.",
        builtin=True,
    ),
    EventRule(
        name="HIGH_TEMP",
        trigger_pattern=r"(temperature|temp)\.(high|alarm|exceeded|critical)",
        action="NOTIFY:maintenance+LOG:Alarme température haute sur {device_id}: {value}",
        cooldown_seconds=300,
        description="Température excessive détectée. Recommande vérification du process.",
        builtin=True,
    ),
    EventRule(
        name="COMMS_FAIL",
        trigger_pattern=r"(comms|communication|connection)\.(fail|lost|timeout|down)",
        action="NOTIFY:technician+LOG:Perte de communication avec {device_id}",
        cooldown_seconds=180,
        description="Perte de communication avec un équipement. Recommande diagnostic réseau.",
        builtin=True,
    ),
]


# ── Rule Engine ────────────────────────────────────────────────────────

class RuleEngine:
    """Moteur de règles d'automatisation.

    Charge les règles depuis ~/.helios/rules.yaml (priorité utilisateur
    sur les règles intégrées). Évalue les événements entrants et déclenche
    les actions correspondantes avec respect des cooldowns.
    """

    def __init__(self):
        """Initialise le moteur de règles et charge la configuration."""
        self._rules: Dict[str, EventRule] = {}
        self._last_fired: Dict[str, float] = {}
        # Import local tardif pour éviter les dépendances circulaires
        try:
            import threading
            self._lock = threading.Lock()
        except ImportError:
            self._lock = None
        self._log_dir = get_helios_home() / "logs"
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._load()

    # ── Gestion des verrous de threads ───────────────────────────────

    def _acquire(self) -> None:
        """Acquiert le verrou si le module threading est chargé."""
        if self._lock:
            self._lock.acquire()

    def _release(self) -> None:
        """Libère le verrou si le module threading est chargé."""
        if self._lock:
            self._lock.release()

    # ── Chargement de la configuration ───────────────────────────────

    def _load(self) -> None:
        """Charge les règles intégrées et les règles utilisateur depuis rules.yaml."""
        # D'abord les règles intégrées
        for rule in _BUILTIN_RULES:
            self._rules[rule.name] = rule

        # Puis les règles utilisateur (surchargent les règles intégrées)
        rules_path = get_helios_home() / "rules.yaml"
        if rules_path.exists():
            try:
                import yaml
                with open(rules_path, "r", encoding="utf-8") as f:
                    user_rules = yaml.safe_load(f) or {}
                for name, cfg in user_rules.get("rules", {}).items():
                    self._rules[name] = EventRule(
                        name=name,
                        trigger_pattern=cfg.get("trigger", ""),
                        action=cfg.get("action", ""),
                        cooldown_seconds=cfg.get("cooldown", 300),
                        description=cfg.get("description", ""),
                        builtin=False,
                    )
            except Exception as e:
                logger.warning("Erreur chargement rules.yaml: %s", e)

    # ── Logging d'automatisation ─────────────────────────────────────

    def _log_trigger(self, rule_name: str, event_type: str, status: str, detail: str = "") -> None:
        """Écrit un événement de déclenchement dans le log d'automatisation.

        Args:
            rule_name: Nom de la règle concernée.
            event_type: Type de l'événement traité.
            status: Statut final ('fired', 'cooldown_blocked', 'no_match').
            detail: Chaîne descriptive additionnelle.
        """
        log_path = self._log_dir / "automation.log"
        timestamp = datetime.now().isoformat()
        line = f"[{timestamp}] RULE={rule_name} EVENT={event_type} STATUS={status} {detail}\n"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(line)
        except Exception as e:
            logger.debug("Erreur écriture log automation: %s", e)

    # ── API publique ──────────────────────────────────────────────────

    def add_rule(self, name: str, trigger_pattern: str, action: str,
                 cooldown: int = 300, description: str = "") -> str:
        """Ajoute une règle d'automatisation programmatiquement.

        Args:
            name: Nom unique de la règle.
            trigger_pattern: Expression régulière filtrant l'événement.
            action: Action à exécuter.
            cooldown: Délai d'attente (cooldown) en secondes.
            description: Commentaire descriptif.

        Returns:
            str: Chaîne JSON confirmant l'ajout de la règle.
        """
        rule = EventRule(
            name=name,
            trigger_pattern=trigger_pattern,
            action=action,
            cooldown_seconds=cooldown,
            description=description,
            builtin=False,
        )
        self._acquire()
        self._rules[name] = rule
        self._release()
        return json.dumps({"success": True, "rule": name}, ensure_ascii=False)

    def list_rules(self) -> str:
        """Liste toutes les règles configurées avec leur statut de disponibilité.

        Returns:
            str: Chaîne JSON formatée listant les règles.
        """
        now = time.time()
        rules_list = []
        self._acquire()
        for name, rule in self._rules.items():
            last = self._last_fired.get(name, 0)
            since_last = max(0, int(now - last)) if last > 0 else None
            rules_list.append({
                "name": rule.name,
                "pattern": rule.trigger_pattern,
                "action": rule.action,
                "cooldown": rule.cooldown_seconds,
                "builtin": rule.builtin,
                "seconds_since_last_fire": since_last,
                "status": "ready" if (since_last is None or since_last >= rule.cooldown_seconds) else "cooldown",
            })
        self._release()
        rules_list.sort(key=lambda r: (r["builtin"], r["name"]))
        return json.dumps({"rules": rules_list, "count": len(rules_list)}, ensure_ascii=False, indent=2)

    def evaluate(self, event_type: str, event_data: Optional[Dict[str, str]] = None) -> str:
        """Évalue un événement contre toutes les règles.

        Args:
            event_type: Type d'événement (ex: "plc.cpu.stop").
            event_data: Données de contexte (ex: {"device_id": "PLC-01", "value": "85"}).

        Returns:
            str: Rapport JSON contenant les règles déclenchées.
        """
        event_data = event_data or {}
        triggered = []
        now = time.time()

        self._acquire()
        for name, rule in self._rules.items():
            # Vérifier la correspondance de motif regex
            if not re.search(rule.trigger_pattern, event_type, re.IGNORECASE):
                continue

            # Vérifier si l'outil est en cooldown
            last = self._last_fired.get(name, 0)
            if now - last < rule.cooldown_seconds:
                triggered.append({
                    "rule": name,
                    "status": "cooldown_blocked",
                    "seconds_remaining": max(0, int(rule.cooldown_seconds - (now - last))),
                })
                continue

            # Exécuter l'action correspondante
            action_result = self._resolve_action(rule.action, event_type, event_data)

            # Mettre à jour l'état de cooldown
            self._last_fired[name] = now
            triggered.append({
                "rule": name,
                "status": "fired",
                "action_result": action_result,
            })

            self._log_trigger(name, event_type, "fired", f"action={rule.action}")
        self._release()

        if not triggered:
            self._log_trigger("(none)", event_type, "no_match")

        return json.dumps({
            "event": event_type,
            "triggered_rules": triggered,
            "count": len(triggered),
        }, ensure_ascii=False, indent=2)

    def fire_rule(self, name: str, context: Optional[Dict[str, str]] = None) -> str:
        """Déclenche manuellement une règle d'automatisation par son nom.

        Args:
            name: Nom unique de la règle à forcer.
            context: Dictionnaire de contexte pour l'action.

        Returns:
            str: Résultat de l'activation forcée en JSON.
        """
        context = context or {}
        self._acquire()
        rule = self._rules.get(name)
        self._release()

        if not rule:
            return json.dumps({"error": f"Règle '{name}' introuvable"}, ensure_ascii=False)

        now = time.time()
        last = self._last_fired.get(name, 0)
        if now - last < rule.cooldown_seconds:
            remaining = int(rule.cooldown_seconds - (now - last))
            return json.dumps({
                "status": "cooldown_blocked",
                "rule": name,
                "seconds_remaining": remaining,
            }, ensure_ascii=False)

        action_result = self._resolve_action(rule.action, f"manual.{name}", context)
        self._acquire()
        self._last_fired[name] = now
        self._release()
        self._log_trigger(name, f"manual.{name}", "fired", f"action={rule.action}")

        return json.dumps({
            "status": "fired",
            "rule": name,
            "action_result": action_result,
        }, ensure_ascii=False, indent=2)

    def _resolve_action(self, action_template: str, event_type: str,
                        context: Dict[str, str]) -> str:
        """Résout une action à partir de son modèle et de son contexte.

        Formats supportés:
        - "NOTIFY:chanel+LOG:message" -> notification + écriture log.
        - Simple chaîne -> rendu de template basique.

        Args:
            action_template: Gabarit textuel d'action.
            event_type: Type de l'événement déclencheur.
            context: Dictionnaire d'arguments contextuels.

        Returns:
            str: Résultat textuel des actions évaluées et résolues.
        """
        # Remplacer les variables de template
        rendered = action_template.format(**context, event_type=event_type)

        # Analyser les actions chaînées combinées par le caractère "+"
        parts = rendered.split("+")
        results = []
        for part in parts:
            part = part.strip()
            if part.startswith("NOTIFY:"):
                results.append(f"notification: {part[7:]}")
            elif part.startswith("LOG:"):
                results.append(f"logged: {part[4:]}")
            else:
                results.append(part)

        return "; ".join(results)


# ── Singleton global ───────────────────────────────────────────────────

_engine = RuleEngine()


# ── Gestionnaires d'outils ─────────────────────────────────────────────

def _handle_evaluate(event_type: str = "", event_data: str = "") -> str:
    """Évalue un événement contre les règles d'automation.

    Args:
        event_type: Type de l'événement.
        event_data: Données de contexte (format JSON).

    Returns:
        str: Résultat JSON de l'évaluation de règles.
    """
    if not event_type:
        return json.dumps({"error": "event_type requis"})
    data = {}
    if event_data:
        try:
            data = json.loads(event_data)
        except json.JSONDecodeError:
            data = {"raw": event_data}
    return _engine.evaluate(event_type, data)


def _handle_add_rule(name: str = "", trigger_pattern: str = "", action: str = "",
                     cooldown: int = 300, description: str = "") -> str:
    """Ajoute une règle d'automation.

    Args:
        name: Nom unique de la règle.
        trigger_pattern: Expression régulière matchant l'événement.
        action: Chaîne décrivant l'action.
        cooldown: Cooldown en secondes.
        description: Commentaire ou description textuelle.

    Returns:
        str: Confirmation d'ajout en JSON.
    """
    if not name or not trigger_pattern or not action:
        return json.dumps({"error": "name, trigger_pattern et action requis"})
    return _engine.add_rule(name, trigger_pattern, action, cooldown, description)


def _handle_list_rules() -> str:
    """Liste toutes les règles d'automation actives.

    Returns:
        str: Liste JSON des règles configurées.
    """
    return _engine.list_rules()


# ── Enregistrement dans le registre Helios ──────────────────────────────

from tools.registry import registry


def _check_yaml() -> bool:
    """Vérifie si la bibliothèque PyYAML est disponible.

    Returns:
        bool: True si yaml est importable, False sinon.
    """
    try:
        import yaml
        return True
    except ImportError:
        return False


registry.register(
    name="automation_rule_evaluate",
    toolset="industrial",
    schema={
        "name": "automation_rule_evaluate",
        "description": "Évalue un événement OT contre les règles d'automation. "
                       "Déclenche les actions correspondantes (notification, log, etc.) "
                       "avec respect des cooldowns. Règles built-in: PLC_STOP, HIGH_TEMP, COMMS_FAIL.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "description": "Type d'événement (ex: 'plc.cpu.stop', 'temperature.high.alarm')"
                },
                "event_data": {
                    "type": "string",
                    "description": "Données JSON contextuelles (ex: '{\"device_id\":\"PLC-01\",\"value\":\"85\"}')"
                }
            },
            "required": ["event_type"]
        }
    },
    handler=lambda a, **kw: _handle_evaluate(a.get("event_type", ""), a.get("event_data", ""), **kw),
    check_fn=_check_yaml,
    requires_env=[],
    description="Évaluation d'événements OT contre les règles d'automation",
    emoji="⚡",
)

registry.register(
    name="automation_rule_add",
    toolset="industrial",
    schema={
        "name": "automation_rule_add",
        "description": "Ajoute une règle d'automation personnalisée. "
                       "Le trigger_pattern est une regex matching sur event_type. "
                       "L'action peut contenir NOTIFY:... et LOG:... séparés par +.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nom unique de la règle"},
                "trigger_pattern": {"type": "string", "description": "Pattern regex (ex: 'pressure\\.(high|critical)')"},
                "action": {"type": "string", "description": "Action (ex: 'NOTIFY:maintenance+LOG:Alarme pression')"},
                "cooldown": {"type": "integer", "description": "Cooldown en secondes", "default": 300},
                "description": {"type": "string", "description": "Description de la règle"}
            },
            "required": ["name", "trigger_pattern", "action"]
        }
    },
    handler=lambda a, **kw: _handle_add_rule(
        a.get("name", ""), a.get("trigger_pattern", ""), a.get("action", ""),
        a.get("cooldown", 300), a.get("description", ""), **kw
    ),
    check_fn=_check_yaml,
    requires_env=[],
    description="Ajout de règles d'automation personnalisées",
    emoji="➕",
)

registry.register(
    name="automation_rule_list",
    toolset="industrial",
    schema={
        "name": "automation_rule_list",
        "description": "Liste toutes les règles d'automation avec leur statut "
                       "(ready/cooldown) et le temps depuis le dernier déclenchement.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda a, **kw: _handle_list_rules(**kw),
    check_fn=_check_yaml,
    requires_env=[],
    description="Liste des règles d'automation",
    emoji="📋",
)