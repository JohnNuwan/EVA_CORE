#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-Evolution System - Amélioration continue de l'agent par patterns.

Inspiré par EvoAgentX. Analyse les sessions passées pour identifier
des patterns d'amélioration: skills à créer, mémoire à consolider,
outils à optimiser. S'exécute en arrière-plan.
"""

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.helios_constants import get_helios_home

logger = logging.getLogger(__name__)


# ── Analyse de sessions ────────────────────────────────────────────────

class EvolutionAnalyzer:
    """Analyse les sessions pour proposer des améliorations.

    Patterns détectés:
    - Tâches répétitives: même type de tâche 3x+ sans skill dédié
    - Erreurs récurrentes: même erreur 2x+ indique un gap de connaissance
    - Outils sous-utilisés: outils jamais appelés dans les N dernières sessions
    - Mémoire fragmentée: entrées mémoire redondantes ou trop longues
    - Skills obsolètes: skills non utilisés depuis >30 jours
    """

    def __init__(self):
        """Initialise l'analyseur d'auto-évolution."""
        self._evolution_dir = get_helios_home() / "evolution"
        self._evolution_dir.mkdir(parents=True, exist_ok=True)
        self._state_path = self._evolution_dir / "state.json"
        self._state = self._load_state()

    def _load_state(self) -> Dict:
        """Charge l'état d'évolution depuis le fichier de persistance.

        Returns:
            Dict: Dictionnaire d'état ou état par défaut s'il est manquant ou corrompu.
        """
        if self._state_path.exists():
            try:
                return json.loads(self._state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "task_history": [],
            "error_history": [],
            "tool_usage": {},
            "skills_used": {},
            "last_analysis": 0,
            "improvements_made": 0,
        }

    def _save_state(self) -> None:
        """Sauvegarde l'état d'évolution actuel sur le disque."""
        try:
            self._state_path.write_text(
                json.dumps(self._state, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.warning("Erreur sauvegarde état evolution: %s", e)

    def record_task(self, task_type: str, tools_used: List[str], success: bool, duration: float) -> None:
        """Enregistre l'exécution d'une tâche.

        Args:
            task_type: Le type générique de la tâche.
            tools_used: Liste des noms d'outils appelés au cours de la tâche.
            success: Flag indiquant si la tâche a réussi.
            duration: Temps d'exécution en secondes.
        """
        self._state["task_history"].append({
            "type": task_type,
            "tools": tools_used,
            "success": success,
            "duration": duration,
            "timestamp": time.time(),
        })
        # Limiter l'historique
        if len(self._state["task_history"]) > 200:
            self._state["task_history"] = self._state["task_history"][-200:]

        # Mettre à jour l'usage des outils
        for t in tools_used:
            self._state["tool_usage"][t] = self._state["tool_usage"].get(t, 0) + 1

        self._save_state()

    def record_error(self, error_type: str, context: str) -> None:
        """Enregistre une erreur survenue pour une analyse ultérieure.

        Args:
            error_type: Catégorie ou type de l'erreur.
            context: Explication ou contexte raccourci de l'erreur.
        """
        self._state["error_history"].append({
            "type": error_type,
            "context": context[:200],
            "timestamp": time.time(),
        })
        if len(self._state["error_history"]) > 100:
            self._state["error_history"] = self._state["error_history"][-100:]
        self._save_state()

    def record_skill_use(self, skill_name: str) -> None:
        """Enregistre la date et l'utilisation d'un skill.

        Args:
            skill_name: Nom du skill exécuté.
        """
        now = time.time()
        self._state["skills_used"][skill_name] = now
        self._save_state()

    def analyze(self) -> str:
        """Lance une analyse complète et retourne les recommandations sous forme de JSON.

        Returns:
            str: Chaîne JSON contenant le rapport d'analyse et les recommandations de réusinage.
        """
        recommendations = []

        now = time.time()
        day_ago = now - 86400
        week_ago = now - 604800
        month_ago = now - 2592000

        # 1. Tâches répétitives sans skill
        recent_tasks = [t for t in self._state["task_history"] if t["timestamp"] > week_ago]
        task_types = {}
        for t in recent_tasks:
            task_types[t["type"]] = task_types.get(t["type"], 0) + 1

        for task_type, count in task_types.items():
            if count >= 3:
                recommendations.append({
                    "type": "skill_suggestion",
                    "priority": "high" if count >= 5 else "medium",
                    "message": f"Tâche '{task_type}' répétée {count}x cette semaine. "
                                f"Envisagez de créer un skill dédié.",
                })

        # 2. Erreurs récurrentes
        recent_errors = [e for e in self._state["error_history"] if e["timestamp"] > week_ago]
        error_types = {}
        for e in recent_errors:
            error_types[e["type"]] = error_types.get(e["type"], 0) + 1

        for err_type, count in error_types.items():
            if count >= 2:
                recommendations.append({
                    "type": "knowledge_gap",
                    "priority": "high" if count >= 3 else "medium",
                    "message": f"Erreur '{err_type}' répétée {count}x. "
                                f"Un skill ou une entrée mémoire pourrait prévenir cette erreur.",
                })

        # 3. Outils jamais utilisés
        total_tools = len(self._state["tool_usage"])
        if total_tools > 0:
            unused = [t for t, c in self._state["tool_usage"].items() if c == 0]
            if unused:
                recommendations.append({
                    "type": "tool_discovery",
                    "priority": "low",
                    "message": f"{len(unused)} outils disponibles non utilisés: {', '.join(unused[:5])}{'...' if len(unused)>5 else ''}",
                })

        # 4. Skills non utilisés
        stale_skills = []
        for skill_name, last_used in self._state["skills_used"].items():
            if last_used < month_ago:
                stale_skills.append(skill_name)

        if stale_skills:
            recommendations.append({
                "type": "skill_maintenance",
                "priority": "low",
                "message": f"{len(stale_skills)} skills non utilisés depuis >30 jours: {', '.join(stale_skills[:5])}",
            })

        # 5. Mémoire fragmentée
        mem_dir = get_helios_home() / "memories"
        memory_entry_count = 0
        for f in mem_dir.glob("*.md"):
            if f.exists():
                content = f.read_text(encoding="utf-8")
                memory_entry_count += content.count("§")

        if memory_entry_count > 20:
            recommendations.append({
                "type": "memory_consolidation",
                "priority": "medium",
                "message": f"Mémoire fragmentée: ~{memory_entry_count} entrées. "
                           f"Envisagez une consolidation des entrées redondantes.",
            })

        # Mettre à jour le timestamp de dernière analyse
        self._state["last_analysis"] = now
        self._save_state()

        result = {
            "analyzed_at": datetime.now().isoformat(),
            "period": "7 jours",
            "stats": {
                "tasks_analyzed": len(recent_tasks),
                "errors_analyzed": len(recent_errors),
                "tools_tracked": total_tools,
                "skills_tracked": len(self._state["skills_used"]),
            },
            "recommendations": recommendations,
            "count": len(recommendations),
        }

        return json.dumps(result, ensure_ascii=False, indent=2)

    def get_stats(self) -> str:
        """Retourne les statistiques d'évolution au format JSON.

        Returns:
            str: Chaîne JSON contenant les métriques d'auto-évolution.
        """
        return json.dumps({
            "tasks_recorded": len(self._state["task_history"]),
            "errors_recorded": len(self._state["error_history"]),
            "tools_used": len(self._state["tool_usage"]),
            "skills_used": len(self._state["skills_used"]),
            "improvements_made": self._state["improvements_made"],
            "last_analysis": datetime.fromtimestamp(self._state["last_analysis"]).isoformat()
            if self._state["last_analysis"] > 0 else "never",
        }, indent=2)


# ── Suggestion de skills basée sur l'usage ─────────────────────────────

def suggest_skills_from_history() -> str:
    """Analyse l'historique des tâches et propose des skills à créer.

    Returns:
        str: Liste JSON de candidats skills avec description et priorité.
    """
    analyzer = EvolutionAnalyzer()
    return analyzer.analyze()


def record_evolution_event(event_type: str = "", detail: str = "") -> str:
    """Enregistre un événement d'évolution manuellement.

    Args:
        event_type: Type d'événement ('task', 'error', ou 'skill_use').
        detail: Détails JSON supplémentaires décrivant l'événement.

    Returns:
        str: Chaîne JSON de confirmation de l'enregistrement.
    """
    analyzer = EvolutionAnalyzer()
    try:
        details = json.loads(detail) if detail else {}
    except json.JSONDecodeError:
        details = {"raw": detail}

    if event_type == "task":
        analyzer.record_task(
            details.get("type", "unknown"),
            details.get("tools", []),
            details.get("success", True),
            details.get("duration", 0),
        )
    elif event_type == "error":
        analyzer.record_error(details.get("type", "unknown"), details.get("context", ""))
    elif event_type == "skill_use":
        analyzer.record_skill_use(details.get("name", "unknown"))
    else:
        return json.dumps({"error": f"Type d'événement inconnu: {event_type}"})

    return json.dumps({"success": True, "event": event_type})


# ── Registration ──────────────────────────────────────────────────────

from tools.registry import registry


registry.register(
    name="evolution_analyze",
    toolset="core",
    schema={
        "name": "evolution_analyze",
        "description": "Analyse l'historique des tâches, erreurs et usage pour proposer "
                       "des améliorations: création de skills, consolidation mémoire, "
                       "découverte d'outils sous-utilisés.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    handler=lambda a, **kw: suggest_skills_from_history(**kw),
    check_fn=None,
    requires_env=[],
    description="Analyse d'auto-évolution de l'agent",
    emoji="🧬",
)

registry.register(
    name="evolution_record",
    toolset="core",
    schema={
        "name": "evolution_record",
        "description": "Enregistre un événement d'évolution (tâche, erreur, utilisation de skill) "
                       "pour l'analyse future. Types: 'task', 'error', 'skill_use'.",
        "parameters": {
            "type": "object",
            "properties": {
                "event_type": {
                    "type": "string",
                    "enum": ["task", "error", "skill_use"],
                    "description": "Type d'événement"
                },
                "detail": {
                    "type": "string",
                    "description": "Détails au format JSON (ex: '{\"type\":\"analyse_PLC\",\"success\":true}')"
                }
            },
            "required": ["event_type"]
        }
    },
    handler=lambda a, **kw: record_evolution_event(a.get("event_type", ""), a.get("detail", ""), **kw),
    check_fn=None,
    requires_env=[],
    description="Enregistrement d'événement pour l'auto-évolution",
    emoji="📝",
)