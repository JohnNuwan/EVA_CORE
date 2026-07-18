#!/usr/bin/env python3
"""Module L5X Editor - Délègue à la bibliothèque ``actemium-l5x-core``.

Ce module sert de pont entre l'agent Helios et la bibliothèque partagée
``actemium-l5x-core`` pour l'analyse, la validation et la transformation
de fichiers L5X (Rockwell Studio 5000 / Logix Designer).

Les dataclasses ``L5XTag``, ``L5XRoutine``, etc. sont réexportées depuis
``actemium.l5x.model`` pour préserver la compatibilité descendante.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from actemium.l5x import L5XProject as ActemiumL5XProject

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Réexport des dataclasses pour compatibilité descendante
# Les imports ci-dessous sont résolus via actemium-l5x-core
# ---------------------------------------------------------------------------
def __getattr__(name):
    """Réexporte les symboles depuis ``actemium.l5x.model``.

    Permet aux anciens consumers de continuer à utiliser ``from tools.l5x_editor import L5XTag``
    sans changement, tout en déléguant au core.
    """
    import actemium.l5x.model as _model

    _compat_map = {
        "L5XTag": _model.Tag,
        "L5XRoutine": _model.Routine,
        "L5XTask": _model.Task,
        "L5XProgram": _model.Program,
        "L5XAOI": _model.AddOnInstruction,
        "L5XProject": ActemiumL5XProject,
        "L5XDocument": _model.L5XDocument,
    }
    if name in _compat_map:
        return _compat_map[name]
    raise AttributeError(f"module 'tools.l5x_editor' has no attribute {name!r}")


# ---------------------------------------------------------------------------
# Fonctions Helios Tools (API publique utilisée par le registre)
# ---------------------------------------------------------------------------


def l5x_editor_analyze(file_path: str, output_format: str = "report") -> str:
    """Analyse un fichier L5X et retourne un rapport ou JSON.

    Délègue à :func:`actemium.l5x.L5XProject.from_file` pour le parsing,
    puis à :meth:`~actemium.l5x.L5XProject.to_json` ou
    :meth:`~actemium.l5x.L5XProject.to_markdown_report` pour la sortie.

    Args:
        file_path: Chemin vers le fichier .L5X.
        output_format: "report" pour Markdown, "json" pour JSON.

    Returns:
        Rapport Markdown ou JSON.
    """
    project = ActemiumL5XProject.from_file(file_path)
    if output_format == "json":
        return project.to_json()
    return project.to_markdown_report()


def l5x_editor_rename_tags(file_path: str, old_prefix: str, new_prefix: str,
                           scope: str = "all", output_path: Optional[str] = None) -> str:
    """Renomme les tags par préfixe dans un fichier L5X.

    Délègue à :meth:`~actemium.l5x.L5XProject.rename_tag_prefix` et
    :meth:`~actemium.l5x.L5XProject.to_file`.

    Args:
        file_path: Chemin vers le fichier .L5X.
        old_prefix: Ancien préfixe à remplacer.
        new_prefix: Nouveau préfixe.
        scope: "all" ou nom de programme.
        output_path: Chemin de sortie (sinon ``<nom>_renamed.L5X``).

    Returns:
        Rapport des changements.
    """
    project = ActemiumL5XProject.from_file(file_path)
    count = project.rename_tag_prefix(old_prefix, new_prefix,
                                      scope if scope != "all" else None)
    out = output_path or str(
        Path(file_path).parent / f"{Path(file_path).stem}_renamed.L5X"
    )
    project.to_file(out)
    return f"Renommage effectué : {count} tags modifiés. Fichier : {out}"


def l5x_editor_validate(file_path: str) -> str:
    """Valide un fichier L5X et retourne les problèmes.

    Délègue à :meth:`~actemium.l5x.L5XProject.validate`.

    Args:
        file_path: Chemin vers le fichier .L5X.

    Returns:
        Rapport de validation Markdown.
    """
    project = ActemiumL5XProject.from_file(file_path)
    issues = project.validate()
    md = f"# Validation L5X : {project.doc.controller.name}\n\n"
    for severity in ["errors", "warnings", "info"]:
        items = issues.get(severity, [])
        if items:
            emoji = "❌" if severity == "errors" else "⚠️" if severity == "warnings" else "ℹ️"
            md += f"## {severity.upper()} ({len(items)})\n"
            for item in items:
                md += f"- {emoji} {item}\n"
    return md


# ---------------------------------------------------------------------------
# Enregistrement dans le registre des outils Helios
# ---------------------------------------------------------------------------
from tools.registry import registry  # noqa: E402

registry.register(
    name="l5x_editor_analyze",
    toolset="industrial",
    schema={
        "name": "l5x_editor_analyze",
        "description": "Analyse un fichier L5X Rockwell Studio 5000 et retourne un rapport structuré (tags, AOIs, UDTs, programmes, tâches).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin complet vers le fichier .L5X"
                },
                "output_format": {
                    "type": "string",
                    "enum": ["report", "json"],
                    "description": "Format de sortie : 'report' (Markdown) ou 'json'"
                }
            },
            "required": ["file_path"]
        }
    },
    handler=lambda args, **kw: l5x_editor_analyze(
        file_path=args.get("file_path", ""),
        output_format=args.get("output_format", "report")
    ),
    is_async=False,
    description="Analyser un fichier L5X Rockwell et générer un rapport structuré.",
    emoji="📋",
)

registry.register(
    name="l5x_editor_validate",
    toolset="industrial",
    schema={
        "name": "l5x_editor_validate",
        "description": "Valide un fichier L5X Rockwell et détecte les problèmes (tags orphelins, types manquants, alias invalides).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin complet vers le fichier .L5X"
                }
            },
            "required": ["file_path"]
        }
    },
    handler=lambda args, **kw: l5x_editor_validate(
        file_path=args.get("file_path", "")
    ),
    is_async=False,
    description="Valider un fichier L5X et détecter les incohérences.",
    emoji="✅",
)

registry.register(
    name="l5x_editor_rename_tags",
    toolset="industrial",
    schema={
        "name": "l5x_editor_rename_tags",
        "description": "Renomme les tags dans un fichier L5X par préfixe (scope-aware).",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Chemin complet vers le fichier .L5X"
                },
                "old_prefix": {
                    "type": "string",
                    "description": "Ancien préfixe à remplacer (ex: 'PLC1_')"
                },
                "new_prefix": {
                    "type": "string",
                    "description": "Nouveau préfixe (ex: 'PLC2_')"
                },
                "scope": {
                    "type": "string",
                    "description": "Scope : 'all' ou nom de programme spécifique"
                },
                "output_path": {
                    "type": "string",
                    "description": "Chemin de sortie pour le fichier modifié"
                }
            },
            "required": ["file_path", "old_prefix", "new_prefix"]
        }
    },
    handler=lambda args, **kw: l5x_editor_rename_tags(
        file_path=args.get("file_path", ""),
        old_prefix=args.get("old_prefix", ""),
        new_prefix=args.get("new_prefix", ""),
        scope=args.get("scope", "all"),
        output_path=args.get("output_path")
    ),
    is_async=False,
    description="Renommer les tags par préfixe dans un fichier L5X.",
    emoji="🏷️",
)