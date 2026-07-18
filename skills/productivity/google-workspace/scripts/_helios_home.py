"""Resolve HELIOS_HOME for standalone skill scripts.

Skill scripts may run outside the Helios process (e.g. system Python,
nix env, CI) where ``helios_constants`` is not importable.  This module
provides the same ``get_helios_home()`` and ``display_helios_home()``
contracts as ``helios_constants`` without requiring it on ``sys.path``.

When ``helios_constants`` IS available it is used directly so that any
future enhancements (profile resolution, Docker detection, etc.) are
picked up automatically.  The fallback path replicates the core logic
from ``helios_constants.py`` using only the stdlib.

All scripts under ``google-workspace/scripts/`` should import from here
instead of duplicating the ``HELIOS_HOME = Path(os.getenv(...))`` pattern.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from agent.helios_constants import display_helios_home as display_helios_home
    from agent.helios_constants import get_helios_home as get_helios_home
except (ModuleNotFoundError, ImportError):

    def get_helios_home() -> Path:
        """Return the Helios home directory (default: ~/.helios).

        Mirrors ``helios_constants.get_helios_home()``."""
        val = os.environ.get("HELIOS_HOME", "").strip()
        return Path(val) if val else Path.home() / ".helios"

    def display_helios_home() -> str:
        """Return a user-friendly ``~/``-shortened display string.

        Mirrors ``helios_constants.display_helios_home()``."""
        home = get_helios_home()
        try:
            return "~/" + str(home.relative_to(Path.home()))
        except ValueError:
            return str(home)
