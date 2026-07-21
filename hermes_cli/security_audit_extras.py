"""Extensions de sécurité pour l'audit au démarrage d'EVA.

BLUE TEAM PATCH — 2026-07-22
Checks supplémentaires : VNC sans auth, pare-feu inactif, containers exposés.
"""

from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger("hermes.security_audit_extras")


def _vnc_no_auth() -> Optional[str]:
    """Vérifie si un processus VNC tourne sans authentification.

    Un VNC avec -SecurityTypes None est un RCE ouvert sur le réseau.
    """
    try:
        result = subprocess.run(
            ["pgrep", "-f", "Xvnc.*SecurityTypes.*None"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            return (
                "VNC détecté SANS authentification (SecurityTypes None). "
                "Tout le réseau peut prendre le contrôle du bureau. "
                "Correction : ajouter -SecurityTypes VncAuth et un PasswordFile."
            )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _firewall_inactive() -> Optional[str]:
    """Vérifie si ufw OU iptables est actif.

    Un serveur sans firewall expose tous ses services au réseau local.
    """
    try:
        result = subprocess.run(
            ["ufw", "status"],
            capture_output=True, text=True, timeout=5,
        )
        if "inactive" in result.stdout.lower():
            return (
                "UFW (pare-feu) est INACTIF. Aucune protection réseau. "
                "Activez : sudo ufw enable && sudo ufw default deny incoming"
            )
    except FileNotFoundError:
        pass
    except (subprocess.TimeoutExpired, OSError):
        pass

    # Fallback : vérifier iptables
    try:
        result = subprocess.run(
            ["iptables", "-L", "-n"],
            capture_output=True, text=True, timeout=5,
        )
        lines = result.stdout.splitlines()
        # Si la chaîne INPUT n'a pas de règles (juste la politique ACCEPT)
        has_rules = any(
            line.startswith("ACCEPT") or line.startswith("DROP") or line.startswith("REJECT")
            for line in lines
        )
        if not has_rules:
            return (
                "iptables semble inactif ou sans règles. Aucune restriction réseau. "
                "Appliquez une politique DROP par défaut : sudo iptables -P INPUT DROP"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def _docker_exposed_ports() -> Optional[str]:
    """Vérifie les containers Docker exposés sur 0.0.0.0.

    Les containers bindés sur 0.0.0.0 sont accessibles depuis tout le réseau.
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}} {{.Ports}}"],
            capture_output=True, text=True, timeout=5,
        )
        exposed = []
        for line in result.stdout.splitlines():
            if "0.0.0.0:" in line:
                exposed.append(line.strip())
        if exposed:
            names = ", ".join(e.split()[0] for e in exposed[:5])
            return (
                f"Containers Docker exposés sur 0.0.0.0 détectés ({len(exposed)}): "
                f"{names}. "
                "Les ports sur 0.0.0.0 sont accessibles depuis tout le réseau. "
                "Correction : docker run -p 127.0.0.1:PORT:PORT ..."
            )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None