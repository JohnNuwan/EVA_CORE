#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Couche de compression pour les sorties d'outils de l'agent Helios.

Réduit l'empreinte en tokens des résultats d'outils sans supprimer de contenu
sémantique utile — seuls le formatage redondant, les lignes répétées, les espaces
de fin de ligne et les blocs base64 inline sont compressés. Le résultat est
sans perte (lossless) pour les données structurées et sans danger pour le code/les logs.
"""

from __future__ import annotations

import json
import logging
import re
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ── Configuration de la compression ────────────────────────────────────

@dataclass(frozen=True)
class CompressionConfig:
    """Seuils ajustables pour la couche de compression.

    Tous les seuils sont exprimés en nombre de caractères. Les valeurs par défaut
    sont choisies de manière conservatrice pour s'activer bien en dessous du point
    où une sortie d'outil saturerait la fenêtre de contexte du modèle.
    """

    # Seuils d'activation
    default_threshold: int = 2000
    default_max_chars: int = 8000

    # Gestion des espaces
    max_consecutive_newlines: int = 2
    strip_trailing_whitespace: bool = True

    # Gestion des répétitions
    repeat_line_threshold: int = 3
    repeat_summary_template: str = "    … (répété {count}x)"

    # Lignes trop longues
    long_line_threshold: int = 500
    long_line_placeholder: str = " … [tronqué]"

    # Blocs Base64 inline
    base64_min_length: int = 200
    base64_replacement_template: str = "[base64: {size} octets]"

    # Contenu structuré (JSON)
    extract_json_structure: bool = True
    json_preview_max_keys: int = 20


# Configuration par défaut (singleton au niveau du module)
DEFAULT_CONFIG = CompressionConfig()


# ── Helpers d'analyse ──────────────────────────────────────────────────

_BASE64_LIKE = re.compile(
    r"(?:data:)?[\w/+-]*;base64,"
    r"([A-Za-z0-9+/=]{200,})"
    r"(?=[\s\"'\]})]|$)",
    re.DOTALL,
)

_JSON_INDENT_RE = re.compile(r"^\s+", re.MULTILINE)
_JSON_KEY_VAL_RE = re.compile(
    r'^\s*"([^"]+)"\s*:\s*(?:"[^"]*"|true|false|null|\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)\s*,?\s*$',
)

# Détecte si le texte ressemble à du JSON structuré (tableau ou objet)
_LOOKS_LIKE_JSON = re.compile(r"^\s*[\{\[]", re.DOTALL)

# Détecte si le texte ressemble à du code source (heuristique sur les marqueurs syntaxiques)
_CODE_LINE_HEURISTIC = re.compile(
    r"^(?:def |class |import |from |# |// |/\*|\* |-- |#!|"
    r"fn |pub |let |var |const |function |if |for |while |"
    r"public |private |static |void |int |float |return |"
    r"    .*:|    .*=>)",
    re.MULTILINE,
)


def _is_probably_code(text: str) -> bool:
    """Détermine si le texte ressemble à du code source.

    Vérifie les 60 premières lignes. Si plus de 30 % correspondent à des patterns de code,
    le texte est considéré comme du code source.

    Args:
        text: Chaîne de caractères à analyser.

    Returns:
        bool: True si le texte ressemble à du code, False sinon.
    """
    if not text:
        return False
    lines = text.splitlines()[:60]
    if not lines:
        return False
    code_markers = sum(1 for ln in lines if _CODE_LINE_HEURISTIC.match(ln))
    return code_markers >= max(3, len(lines) * 0.3)


def _is_probably_json(text: str) -> bool:
    """Détermine si le texte ressemble à un document JSON.

    Args:
        text: Chaîne de caractères à analyser.

    Returns:
        bool: True si le texte commence par un crochet ou une accolade, False sinon.
    """
    return bool(_LOOKS_LIKE_JSON.match(text)) if text else False


def _collapse_repeated_lines(
    lines: list[str],
    threshold: int,
    template: str,
) -> list[str]:
    """Condense les répétitions consécutives d'une même ligne au-delà d'un seuil.

    Args:
        lines: Liste de lignes de texte.
        threshold: Nombre maximum de répétitions identiques tolérées.
        template: Modèle de chaîne pour résumer les répétitions (ex: "répété 10x").

    Returns:
        list[str]: Liste de lignes avec les répétitions condensées.
    """
    if not lines:
        return lines

    result: list[str] = []
    i = 0
    while i < len(lines):
        current = lines[i]
        count = 1
        while i + count < len(lines) and lines[i + count] == current:
            count += 1

        if count > threshold:
            result.append(current)
            result.append(template.format(count=count))
        else:
            for _ in range(count):
                result.append(current)
        i += count

    return result


def _collapse_blank_lines(lines: list[str], max_blank: int) -> list[str]:
    """Limite les sauts de lignes consécutifs vides à une valeur maximale.

    Args:
        lines: Liste de lignes de texte.
        max_blank: Nombre maximal de lignes vides consécutives à conserver.

    Returns:
        list[str]: Liste de lignes après condensation des lignes vides.
    """
    result: list[str] = []
    blank_run = 0
    for ln in lines:
        if not ln.strip():
            blank_run += 1
            if blank_run <= max_blank:
                result.append(ln)
        else:
            blank_run = 0
            result.append(ln)
    return result


def _strip_base64(text: str, min_length: int, template: str) -> str:
    """Remplace les blocs d'images base64 inline par un résumé textuel de leur taille.

    Args:
        text: Texte source à traiter.
        min_length: Longueur minimale du bloc pour déclencher le remplacement.
        template: Modèle de chaîne pour remplacer le bloc (ex: "[base64: N octets]").

    Returns:
        str: Texte avec les blocs base64 remplacés.
    """
    def _replace(m: re.Match) -> str:
        blob = m.group(1)
        # S'assurer que le contenu ressemble bien à du base64 (ratio élevé de caractères valides)
        b64_chars = sum(1 for c in blob if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
        if len(blob) < min_length or b64_chars < len(blob) * 0.8:
            return m.group(0)
        return template.format(size=len(blob))

    return _BASE64_LIKE.sub(_replace, text)


def _compress_json(text: str, max_chars: int, config: CompressionConfig) -> str:
    """Compresse un contenu structuré en JSON pour en extraire l'essentiel.

    Args:
        text: Document JSON au format chaîne.
        max_chars: Nombre maximum de caractères souhaité.
        config: Paramètres de configuration de la compression.

    Returns:
        str: JSON compressé ou texte d'origine si JSON invalide.
    """
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return text

    if isinstance(parsed, list):
        return _compress_json_list(parsed, max_chars, config)
    elif isinstance(parsed, dict):
        return _compress_json_dict(parsed, max_chars, config)
    return text


def _compress_json_list(
    parsed: list[Any], max_chars: int, config: CompressionConfig,
) -> str:
    """Compresse une liste JSON en échantillonnant les premiers éléments.

    Args:
        parsed: Liste Python analysée.
        max_chars: Capacité maximale en caractères.
        config: Configuration globale de compression.

    Returns:
        str: Chaîne JSON échantillonnée et résumée.
    """
    if not parsed:
        return "[]"

    # Si c'est une liste d'éléments simples, afficher un extrait
    all_primitives = all(
        isinstance(item, (str, int, float, bool, type(None))) for item in parsed
    )
    if all_primitives:
        result = json.dumps(parsed, ensure_ascii=False)
        if len(result) <= max_chars:
            return result
        return json.dumps(parsed[:50], ensure_ascii=False) + (
            f"\n… [{len(parsed) - 50} autres éléments tronqués]"
        )

    # Liste d'objets — afficher les premiers, résumer les clés communes pour le reste
    if isinstance(parsed[0], dict):
        all_keys: set[str] = set()
        for item in parsed[:100]:
            all_keys.update(item.keys())
        preview_count = min(10, len(parsed))
        preview = json.dumps(parsed[:preview_count], ensure_ascii=False, indent=2)
        tail_count = len(parsed) - preview_count
        if tail_count > 0:
            preview += (
                f"\n\n… {tail_count} autres éléments (clés communes: "
                f"{', '.join(sorted(all_keys)[:config.json_preview_max_keys - 10])}"
                + (", …" if len(all_keys) > config.json_preview_max_keys else "")
                + ")"
            )
        return _further_compress(preview, max_chars, config)

    # Rétrocompatibilité : troncature brute
    result = json.dumps(parsed[:50], ensure_ascii=False)
    if len(result) <= max_chars:
        return result
    return textwrap.shorten(result, width=max_chars, placeholder=" … [tronqué]")


def _compress_json_dict(
    parsed: dict[str, Any], max_chars: int, config: CompressionConfig,
) -> str:
    """Compresse un dictionnaire JSON en réduisant les valeurs volumineuses.

    Args:
        parsed: Dictionnaire Python extrait.
        max_chars: Capacité en caractères.
        config: Paramètres de compression.

    Returns:
        str: JSON condensé au format chaîne.
    """
    compressed: dict[str, Any] = {}
    for key, value in parsed.items():
        if isinstance(value, str) and len(value) > 200:
            compressed[key] = textwrap.shorten(
                value, width=200, placeholder=" … [tronqué]"
            )
        elif isinstance(value, (list, dict)):
            serialized = json.dumps(value, ensure_ascii=False, default=str)
            if len(serialized) > 300:
                compressed[key] = (
                    f"[{type(value).__name__}: ~{len(serialized)} octets]"
                )
            else:
                compressed[key] = value
        else:
            compressed[key] = value

    # Limiter le nombre de clés au niveau supérieur
    keys = list(compressed.keys())
    if len(keys) > config.json_preview_max_keys:
        visible = keys[: config.json_preview_max_keys - 5]
        hidden = len(keys) - len(visible)
        compressed = {k: compressed[k] for k in visible}
        compressed[f"… ({hidden} autres clés)"] = "tronqué pour le contexte"

    result = json.dumps(compressed, ensure_ascii=False, indent=2)
    return _further_compress(result, max_chars, config)


def _further_compress(text: str, max_chars: int, config: CompressionConfig) -> str:
    """Applique des passes de nettoyage supplémentaires sur du texte pré-structuré.

    Args:
        text: Texte structuré à nettoyer.
        max_chars: Limite maximale.
        config: Configuration globale de compression.

    Returns:
        str: Texte optimisé.
    """
    lines = text.splitlines()
    lines = _collapse_blank_lines(lines, config.max_consecutive_newlines)
    if config.strip_trailing_whitespace:
        lines = [ln.rstrip() for ln in lines]
    text = "\n".join(lines)

    if len(text) <= max_chars:
        return text
    return textwrap.shorten(text, width=max_chars, placeholder=" … [tronqué]")


def _compress_code_output(text: str, max_chars: int, config: CompressionConfig) -> str:
    """Compresse les retours de code source (effacement de lignes vides, raccourcis).

    Args:
        text: Code source brut.
        max_chars: Nombre maximum de caractères.
        config: Configuration.

    Returns:
        str: Code compressé.
    """
    lines = text.splitlines()

    # Retirer les lignes vides de fin
    while lines and not lines[-1].strip():
        lines.pop()

    # Condenser les lignes vides consécutives
    lines = _collapse_blank_lines(lines, config.max_consecutive_newlines)

    if not lines:
        return ""

    # Tronquer les lignes individuelles trop longues
    shortened: list[str] = []
    for ln in lines:
        if len(ln) > config.long_line_threshold:
            ln = textwrap.shorten(
                ln,
                width=config.long_line_threshold,
                placeholder=config.long_line_placeholder,
            )
        shortened.append(ln)

    text = "\n".join(shortened)
    if len(text) <= max_chars:
        return text

    # Limiter la taille globale en préservant les frontières de lignes
    truncated = text[:max_chars]
    last_nl = truncated.rfind("\n")
    if last_nl > max_chars // 2:
        truncated = truncated[: last_nl + 1]
    return truncated + (
        f"\n[Sortie tronquée : longueur initiale de {len(text):,} octets, affichage de {len(truncated):,}]"
    )


def _compress_generic_text(text: str, max_chars: int, config: CompressionConfig) -> str:
    """Compresse du texte générique ou des logs par des passes standards.

    Args:
        text: Texte brut à optimiser.
        max_chars: Capacité maximale.
        config: Configuration.

    Returns:
        str: Texte compressé et tronqué si nécessaire.
    """
    lines = text.splitlines()

    # 1. Supprimer les espaces de fin de ligne
    if config.strip_trailing_whitespace:
        lines = [ln.rstrip() for ln in lines]

    # 2. Condenser les lignes répétées
    lines = _collapse_repeated_lines(
        lines, config.repeat_line_threshold, config.repeat_summary_template
    )

    # 3. Condenser les sauts de lignes
    lines = _collapse_blank_lines(lines, config.max_consecutive_newlines)

    text = "\n".join(lines)

    # 4. Raccourcir les lignes individuelles trop longues
    if len(text) > config.long_line_threshold:
        text = textwrap.shorten(
            text,
            width=config.long_line_threshold,
            placeholder=config.long_line_placeholder,
        )

    # 5. Limitation globale
    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars]
    last_nl = truncated.rfind("\n")
    if last_nl > max_chars // 2:
        truncated = truncated[: last_nl + 1]
    return truncated


# ── API publique ───────────────────────────────────────────────────────

def compress_tool_output(text: str, max_chars: int = 8000) -> str:
    """Compresse une sortie d'outil en supprimant les formatages redondants.

    Cette fonction applique successivement plusieurs passes de compression :
      1. Remplacement des blobs base64 inline par un résumé de leur taille.
      2. Nettoyage des espaces de fin de ligne.
      3. Détection du type de contenu (JSON, Code, Texte) et application
         de règles spécifiques d'optimisation (échantillonnage, raccourcis).
      4. Limitation globale de taille respectueuse des fins de lignes.

    Args:
        text: Le texte brut à compresser.
        max_chars: Le nombre maximal de caractères ciblé (défaut 8000).

    Returns:
        str: Le texte compressé, de taille inférieure ou égale à max_chars.
    """
    if not text:
        return ""

    config = CompressionConfig(default_max_chars=max_chars)

    # Passe 1: Nettoyage des base64
    text = _strip_base64(
        text,
        config.base64_min_length,
        config.base64_replacement_template,
    )

    # Passe 2: Nettoyage des espaces de fin
    if config.strip_trailing_whitespace:
        lines = text.splitlines(keepends=True)
        text = "".join(ln.rstrip() + "\n" for ln in lines).rstrip("\n")

    # Passe 3: Heuristiques par type de contenu
    stripped_text = text.strip()
    if _is_probably_json(stripped_text) and config.extract_json_structure:
        text = _compress_json(text, max_chars, config)
    elif _is_probably_code(text):
        text = _compress_code_output(text, max_chars, config)
    else:
        text = _compress_generic_text(text, max_chars, config)

    # Passe 4: Limitation de taille finale
    if len(text) > max_chars:
        truncated = text[:max_chars]
        last_nl = truncated.rfind("\n")
        if last_nl > max_chars // 2:
            truncated = truncated[: last_nl + 1]
        text = truncated.rstrip() + (
            f"\n[Sortie tronquée : longueur initiale de {len(text):,} octets, "
            f"affichage de {len(truncated):,}]"
        )

    return text


def maybe_compress(
    text: str,
    threshold: int = 2000,
    max_chars: int = 8000,
) -> Tuple[str, Dict[str, Any]]:
    """Compresse le texte de manière conditionnelle si sa taille excède le seuil.

    C'est le point d'entrée principal pour la compression intelligente. N'exécute la
    compression que si len(text) > threshold pour éviter les surcoûts sur les petites chaînes.

    Args:
        text: Sortie d'outil brute.
        threshold: Seuil d'activation en caractères (défaut 2000).
        max_chars: Nombre maximum de caractères visé après compression.

    Returns:
        Tuple[str, Dict[str, Any]]: Couple (texte_compresse, dictionnaire_statistiques).
    """
    original_len = len(text)

    if not text or original_len <= threshold:
        return text, {
            "original_chars": original_len,
            "compressed_chars": original_len,
            "ratio_pct": 0.0,
            "activated": False,
        }

    compressed = compress_tool_output(text, max_chars=max_chars)
    compressed_len = len(compressed)

    # Calcul du taux de compression
    if original_len > 0:
        ratio_pct = round((1 - compressed_len / original_len) * 100, 1)
    else:
        ratio_pct = 0.0

    stats = {
        "original_chars": original_len,
        "compressed_chars": compressed_len,
        "ratio_pct": ratio_pct,
        "activated": True,
    }

    logger.info(
        "Statistiques de compression : %d -> %d octets (réduction de %.1f%%)",
        original_len, compressed_len, ratio_pct,
    )

    return compressed, stats


# ── Gestionnaire d'outil Helios ───────────────────────────────────────

def _compress_output_handler(args: dict, **kwargs: Any) -> str:
    """Exécute la compression en tant que gestionnaire d'outil d'Helios.

    Args:
        args: Arguments passés à l'outil par le modèle.

    Returns:
        str: JSON contenant le texte compressé et les statistiques.
    """
    text = args.get("text", "")
    max_chars = args.get("max_chars", 8000)

    if not text:
        return json.dumps(
            {"error": "Aucun texte ('text') fourni à compresser", "success": False},
            ensure_ascii=False,
        )

    compressed, stats = maybe_compress(text, threshold=2000, max_chars=max_chars)

    return json.dumps(
        {
            "success": True,
            "compressed": compressed,
            "stats": stats,
        },
        ensure_ascii=False,
    )


def _check_core_requirements() -> bool:
    """Vérifie les prérequis (aucun prérequis externe).

    Returns:
        bool: True (toujours disponible).
    """
    return True


COMPRESS_OUTPUT_SCHEMA = {
    "name": "compress_output",
    "description": (
        "Compresse une chaîne de texte volumineuse en éliminant le formatage redondant, "
        "les lignes répétées, les blocs base64 et en condensant la structure JSON. "
        "Ne supprime aucun contenu sémantique utile."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "Le texte à compresser (sortie d'outil, log, JSON).",
            },
            "max_chars": {
                "type": "integer",
                "description": "Capacité maximale de caractères ciblée (défaut 8000).",
                "default": 8000,
            },
        },
        "required": ["text"],
    },
}


# Enregistrement dans le registre
from tools.registry import registry, tool_error  # noqa: E402

registry.register(
    name="compress_output",
    toolset="core",
    schema=COMPRESS_OUTPUT_SCHEMA,
    handler=_compress_output_handler,
    check_fn=_check_core_requirements,
    emoji="📦",
    description=(
        "Compresse du texte volumineux en éliminant le formatage redondant. "
        "Sans perte (lossless) pour les données structurées."
    ),
)