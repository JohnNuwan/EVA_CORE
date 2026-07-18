"""Horloge consciente des fuseaux horaires (timezone-aware) pour EVA.

Fournit une fonction d'aide ``now()`` unique qui renvoie un objet datetime
conscient du fuseau horaire configuré par l'utilisateur (ex: ``Europe/Paris``).

Ordre de résolution :
  1. Variable d'environnement ``HERMES_TIMEZONE``
  2. Clé ``timezone`` dans le fichier ``~/.hermes/config.yaml``
  3. Par défaut, l'heure locale du serveur (``datetime.now().astimezone()``)

Les fuseaux horaires invalides génèrent un avertissement dans les logs et se
rabattent sur l'heure système du serveur — EVA ne plante pas en cas de mauvaise valeur.
"""

import logging
import os
from datetime import datetime
from hermes_constants import get_config_path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Rétrocompatibilité Python 3.8 (non requise pour EVA car python >= 3.9)
    from backports.zoneinfo import ZoneInfo  # type: ignore[no-redef]

# État mis en cache — résolu une seule fois, réutilisé à chaque appel.
# Appeler reset_cache() pour forcer une nouvelle résolution.
_cached_tz: Optional[ZoneInfo] = None
_cached_tz_name: Optional[str] = None
_cache_resolved: bool = False


def _resolve_timezone_name() -> str:
    """Lit la chaîne du fuseau horaire IANA configurée (ou vide).

    Cette fonction effectue des opérations d'E/S fichiers lors de la lecture
    de config.yaml, son résultat doit donc être mis en cache.

    Returns:
        La chaîne de fuseau horaire configurée ou une chaîne vide.
    """
    # 1. Variable d'environnement (priorité la plus haute)
    tz_env = os.getenv("HERMES_TIMEZONE", "").strip()
    if tz_env:
        return tz_env

    # 2. Clé ``timezone`` dans config.yaml
    try:
        try:
            from hermes_cli.config import read_raw_config
            cfg = read_raw_config() or {}
        except Exception:
            import yaml
            config_path = get_config_path()
            if config_path.exists():
                with open(config_path, encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
            else:
                cfg = {}
        if cfg:
            try:
                from hermes_cli import managed_scope
                cfg = managed_scope.apply_managed_overlay(cfg)
            except Exception:
                pass
            tz_cfg = cfg.get("timezone", "")
            if isinstance(tz_cfg, str) and tz_cfg.strip():
                return tz_cfg.strip()
    except Exception:
        pass

    return ""


def _get_zoneinfo(name: str) -> Optional[ZoneInfo]:
    """Valide et renvoie un fuseau horaire ZoneInfo.

    Args:
        name: Le nom du fuseau horaire IANA.

    Returns:
        Un objet ZoneInfo valide ou None en cas d'erreur ou d'absence de nom.
    """
    if not name:
        return None
    try:
        return ZoneInfo(name)
    except (KeyError, Exception) as exc:
        logger.warning(
            "Fuseau horaire invalide '%s': %s. Utilisation de l'heure du serveur par défaut.",
            name, exc,
        )
        return None


def get_timezone() -> Optional[ZoneInfo]:
    """Renvoie le ZoneInfo configuré de l'utilisateur.

    Le résultat est résolu une seule fois et mis en cache.

    Returns:
        Le fuseau horaire ZoneInfo configuré, ou None (heure système du serveur).
    """
    global _cached_tz, _cached_tz_name, _cache_resolved
    if not _cache_resolved:
        _cached_tz_name = _resolve_timezone_name()
        _cached_tz = _get_zoneinfo(_cached_tz_name)
        _cache_resolved = True
    return _cached_tz


def reset_cache() -> None:
    """Vide le cache pour forcer une nouvelle résolution du fuseau horaire.

    À appeler après chaque modification de configuration ou mise à jour de
    ``HERMES_TIMEZONE``.
    """
    global _cached_tz, _cached_tz_name, _cache_resolved
    _cached_tz = None
    _cached_tz_name = None
    _cache_resolved = False


def now() -> datetime:
    """Renvoie l'heure actuelle sous forme de datetime conscient du fuseau horaire.

    Returns:
        L'heure courante convertie dans le fuseau configuré, ou l'heure
        système locale du serveur si aucun fuseau n'est configuré.
    """
    tz = get_timezone()
    if tz is not None:
        return datetime.now(tz)
    # Aucun fuseau configuré — heure locale du serveur
    return datetime.now().astimezone()
