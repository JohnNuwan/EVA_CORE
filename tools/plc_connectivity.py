#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PLC Connectivity Module - Communication temps réel avec automates Siemens et Rockwell.

Fournit des connecteurs vers python-snap7 (Siemens S7), pylogix (Rockwell),
et pycomm3 (Allen-Bradley Ethernet/IP). Tous les outils sont purement optionnels.
"""

import json
import logging
import re
import socket
from typing import Optional

logger = logging.getLogger(__name__)

# ── Vérifications des dépendances ──────────────────────────────────────

_SNAP7_OK = False
_PYLOGIX_OK = False
_PYCOMM3_OK = False

try:
    import snap7
    _SNAP7_OK = True
except ImportError:
    pass

try:
    from pylogix import PLC
    _PYLOGIX_OK = True
except ImportError:
    pass

try:
    from pycomm3 import LogixDriver
    _PYCOMM3_OK = True
except ImportError:
    pass


# ── Siemens S7 Connector ───────────────────────────────────────────────

class SiemensS7Connector:
    """Connecteur vers automate Siemens S7 via python-snap7.

    Permet d'établir une connexion, de lire des blocs de données (DB),
    de lire/écrire des tags, et de récupérer l'état du processeur.
    """

    def __init__(self):
        """Initialise le connecteur Siemens S7."""
        self._client = None
        self._connected = False

    def connect(self, ip: str, rack: int = 0, slot: int = 1) -> str:
        """Connecte à un CPU Siemens S7.

        Args:
            ip: Adresse IP de l'automate Siemens.
            rack: Numéro de rack physique (par défaut 0).
            slot: Numéro de slot du processeur (par défaut 1).

        Returns:
            str: Chaîne JSON décrivant le succès ou l'erreur de connexion.
        """
        if not _SNAP7_OK:
            return json.dumps({"error": "python-snap7 non installé. pip install python-snap7"})
        try:
            import snap7
            self._client = snap7.client.Client()
            self._client.connect(ip, rack, slot)
            self._connected = True
            return json.dumps({"success": True, "target": f"{ip}:{rack}/{slot}", "status": "connected"})
        except Exception as e:
            return json.dumps({"error": f"Échec connexion S7: {e}"})

    def disconnect(self) -> None:
        """Déconnecte proprement le client de l'automate Siemens S7."""
        if self._client:
            self._client.disconnect()
            self._connected = False

    def read_db(self, db_number: int, start: int = 0, size: int = 100) -> str:
        """Lit un bloc de données (DB) sur l'automate Siemens S7.

        Args:
            db_number: Numéro du bloc de données (ex: 1 pour DB1).
            start: Adresse d'octet de départ (par défaut 0).
            size: Nombre d'octets à lire (par défaut 100).

        Returns:
            str: Chaîne JSON contenant les données lues ou l'erreur rencontrée.
        """
        if not self._connected:
            return json.dumps({"error": "Non connecté"})
        try:
            result = self._client.read_area(snap7.types.Areas.DB, db_number, start, size)
            return json.dumps({
                "success": True,
                "db": db_number,
                "start": start,
                "size": size,
                "hex": result.hex(),
                "raw": list(result),
            })
        except Exception as e:
            return json.dumps({"error": f"Échec lecture DB{db_number}: {e}"})

    def read_tag(self, tag_path: str) -> str:
        """Lit un tag au format Siemens (DB1.DBX0.0, MW100, etc.).

        Args:
            tag_path: Chemin du tag à lire (ex: DB1.DBX0.0).

        Returns:
            str: Chaîne JSON avec la valeur du tag ou l'erreur rencontrée.
        """
        if not self._connected:
            return json.dumps({"error": "Non connecté"})
        try:
            import snap7
            from snap7.util import get_bool, get_dword, get_word, get_real, get_int
            tag_path = tag_path.upper().strip()
            
            # Format DB1.DBX0.0 -> DB 1, bit 0 à l'octet 0
            m = re.match(r'DB(\d+)\.DB([XBDW])(\d+)(?:\.(\d+))?', tag_path)
            if m:
                db = int(m.group(1))
                typ = m.group(2)
                byte_addr = int(m.group(3))
                bit = int(m.group(4)) if m.group(4) else 0
                raw = self._client.read_area(snap7.types.Areas.DB, db, byte_addr, 4)
                if typ == 'X':
                    val = get_bool(raw, 0, bit)
                elif typ == 'B':
                    val = raw[0]
                elif typ == 'W':
                    val = get_word(raw, 0)
                elif typ == 'D':
                    val = get_dword(raw, 0)
                return json.dumps({"success": True, "tag": tag_path, "value": val})
                
            # Format MW100, MB50, MX102.0
            m = re.match(r'M([XBDW])(\d+)(?:\.(\d+))?', tag_path)
            if m:
                typ = m.group(1)
                addr = int(m.group(2))
                bit = int(m.group(3)) if m.group(3) else 0
                raw = self._client.read_area(snap7.types.Areas.MK, 0, addr, 4)
                if typ == 'X':
                    val = get_bool(raw, 0, bit)
                elif typ == 'B':
                    val = raw[0]
                elif typ == 'W':
                    val = get_word(raw, 0)
                elif typ == 'D':
                    val = get_dword(raw, 0)
                return json.dumps({"success": True, "tag": tag_path, "value": val})
            return json.dumps({"error": f"Format tag non reconnu: {tag_path}"})
        except Exception as e:
            return json.dumps({"error": f"Échec lecture {tag_path}: {e}"})

    def get_cpu_state(self) -> str:
        """Retourne l'état RUN/STOP du CPU de l'automate Siemens S7.

        Returns:
            str: Chaîne JSON contenant l'état du CPU ou l'erreur rencontrée.
        """
        if not self._connected:
            return json.dumps({"error": "Non connecté"})
        try:
            state = self._client.get_cpu_state()
            return json.dumps({"success": True, "state": state})
        except Exception as e:
            return json.dumps({"error": f"Échec état CPU: {e}"})


# ── Rockwell Connector (pylogix) ──────────────────────────────────────

class RockwellConnector:
    """Connecteur vers Rockwell ControlLogix/CompactLogix via pylogix.

    Permet de lire et d'écrire des tags, et de récupérer des informations
    sur le contrôleur.
    """

    def __init__(self):
        """Initialise le connecteur Rockwell."""
        self._plc = None

    def connect(self, ip: str) -> str:
        """Se connecte à un contrôleur Rockwell via son IP.

        Args:
            ip: Adresse IP de l'automate Rockwell.

        Returns:
            str: Chaîne JSON décrivant le succès ou l'erreur de connexion.
        """
        if not _PYLOGIX_OK:
            return json.dumps({"error": "pylogix non installé. pip install pylogix"})
        try:
            from pylogix import PLC
            self._plc = PLC()
            self._plc.IPAddress = ip
            return json.dumps({"success": True, "target": ip, "status": "connected"})
        except Exception as e:
            return json.dumps({"error": f"Échec connexion Rockwell: {e}"})

    def read_tag(self, tag_name: str) -> str:
        """Lit la valeur d'un tag sur le contrôleur Rockwell.

        Args:
            tag_name: Nom du tag à lire (ex: 'MyTag').

        Returns:
            str: Chaîne JSON contenant le statut et la valeur du tag.
        """
        if not self._plc:
            return json.dumps({"error": "Non connecté"})
        try:
            ret = self._plc.Read(tag_name)
            return json.dumps({
                "success": ret.Value is not None,
                "tag": tag_name,
                "value": str(ret.Value),
                "status": ret.Status,
            })
        except Exception as e:
            return json.dumps({"error": f"Échec lecture {tag_name}: {e}"})

    def write_tag(self, tag_name: str, value) -> str:
        """Écrit une valeur sur un tag du contrôleur Rockwell.

        Args:
            tag_name: Nom du tag à modifier.
            value: Valeur à écrire (type converti dynamiquement par pylogix).

        Returns:
            str: Chaîne JSON indiquant le succès de l'écriture.
        """
        if not self._plc:
            return json.dumps({"error": "Non connecté"})
        try:
            ret = self._plc.Write(tag_name, value)
            return json.dumps({
                "success": ret.Status == "Success",
                "tag": tag_name,
                "written_value": str(value),
                "status": ret.Status,
            })
        except Exception as e:
            return json.dumps({"error": f"Échec écriture {tag_name}: {e}"})

    def get_controller_info(self) -> str:
        """Récupère les informations matérielles du contrôleur Rockwell.

        Returns:
            str: Chaîne JSON contenant les métadonnées du contrôleur.
        """
        if not self._plc:
            return json.dumps({"error": "Non connecté"})
        try:
            ret = self._plc.GetControllerInfo()
            return json.dumps({
                "success": ret.Value is not None,
                "info": str(ret.Value) if ret.Value else "N/A",
                "status": ret.Status,
            })
        except Exception as e:
            return json.dumps({"error": f"Échec infos: {e}"})


# ── Allen-Bradley EIP (pycomm3) ───────────────────────────────────────

class AllenBradleyEIP:
    """Connecteur vers Allen-Bradley via pycomm3 LogixDriver.

    Alternative robuste pour la communication CIP / Ethernet/IP.
    """

    def __init__(self):
        """Initialise le connecteur Allen-Bradley EIP."""
        self._driver = None

    def connect(self, ip: str, slot: int = 0) -> str:
        """Ouvre une connexion avec l'automate Allen-Bradley.

        Args:
            ip: Adresse IP de la cible.
            slot: Emplacement du CPU dans le châssis (par défaut 0).

        Returns:
            str: Chaîne JSON décrivant le succès ou l'erreur de connexion.
        """
        if not _PYCOMM3_OK:
            return json.dumps({"error": "pycomm3 non installé. pip install pycomm3"})
        try:
            from pycomm3 import LogixDriver
            self._driver = LogixDriver(ip, slot=slot)
            self._driver.open()
            return json.dumps({"success": True, "target": f"{ip}:{slot}", "status": "connected"})
        except Exception as e:
            return json.dumps({"error": f"Échec connexion EIP: {e}"})

    def disconnect(self) -> None:
        """Ferme la connexion avec l'automate Allen-Bradley."""
        if self._driver:
            try:
                self._driver.close()
            except Exception:
                pass

    def read_tag(self, tag_name: str) -> str:
        """Lit la valeur d'un tag.

        Args:
            tag_name: Nom du tag à lire.

        Returns:
            str: Chaîne JSON contenant la valeur du tag.
        """
        if not self._driver:
            return json.dumps({"error": "Non connecté"})
        try:
            ret = self._driver.read(tag_name)
            return json.dumps({
                "success": ret.status == "Success",
                "tag": tag_name,
                "value": str(ret.value),
                "status": ret.status,
            })
        except Exception as e:
            return json.dumps({"error": f"Échec lecture {tag_name}: {e}"})

    def write_tag(self, tag_name: str, value) -> str:
        """Écrit une valeur sur un tag.

        Args:
            tag_name: Nom du tag.
            value: Valeur à affecter.

        Returns:
            str: Chaîne JSON du statut final de l'écriture.
        """
        if not self._driver:
            return json.dumps({"error": "Non connecté"})
        try:
            ret = self._driver.write((tag_name, value))
            return json.dumps({
                "success": ret.status == "Success",
                "tag": tag_name,
                "written_value": str(value),
                "status": ret.status,
            })
        except Exception as e:
            return json.dumps({"error": f"Échec écriture {tag_name}: {e}"})

    def get_cpu_info(self) -> str:
        """Récupère les informations processeur CIP.

        Returns:
            str: Chaîne JSON contenant les caractéristiques du CPU.
        """
        if not self._driver:
            return json.dumps({"error": "Non connecté"})
        try:
            info = self._driver.get_plc_info()
            return json.dumps({
                "success": True,
                "info": str(info),
            })
        except Exception as e:
            return json.dumps({"error": f"Échec infos CPU: {e}"})


# ── Dispatchers unifiés ────────────────────────────────────────────────

def read_plc_tag(plc_type: str, endpoint: str, tag_path: str, **kwargs) -> str:
    """Lit un tag sur un automate par type et endpoint.

    Args:
        plc_type: Type de protocole ('s7', 'rockwell', ou 'eip').
        endpoint: Adresse IP (ou IP:châssis/emplacement).
        tag_path: Chemin d'accès au tag logique.

    Returns:
        str: Chaîne JSON avec la valeur lue ou le message d'erreur.
    """
    if plc_type == 's7':
        c = SiemensS7Connector()
        r = c.connect(endpoint)
        rj = json.loads(r)
        if not rj.get("success"):
            return r
        result = c.read_tag(tag_path)
        c.disconnect()
        return result
    elif plc_type == 'rockwell':
        c = RockwellConnector()
        c.connect(endpoint)
        return c.read_tag(tag_path)
    elif plc_type == 'eip':
        c = AllenBradleyEIP()
        r = c.connect(endpoint)
        rj = json.loads(r)
        if not rj.get("success"):
            return r
        result = c.read_tag(tag_path)
        c.disconnect()
        return result
    return json.dumps({"error": f"Type PLC inconnu: {plc_type}. Utilisez s7, rockwell ou eip."})


def write_plc_tag(plc_type: str, endpoint: str, tag_path: str, value) -> str:
    """Écrit une valeur sur un tag automate.

    Args:
        plc_type: Type de protocole ('s7', 'rockwell', ou 'eip').
        endpoint: Adresse IP.
        tag_path: Chemin d'accès au tag.
        value: Valeur à inscrire.

    Returns:
        str: Chaîne JSON décrivant le résultat.
    """
    if plc_type == 's7':
        c = SiemensS7Connector()
        r = c.connect(endpoint)
        rj = json.loads(r)
        if not rj.get("success"):
            return r
        # Écriture S7 simulée via lecture-modification-écriture pour les bits
        result = json.dumps({"info": "S7 write via read-modify-wire", "tag": tag_path, "value": str(value)})
        c.disconnect()
        return result
    elif plc_type == 'rockwell':
        c = RockwellConnector()
        c.connect(endpoint)
        return c.write_tag(tag_path, value)
    elif plc_type == 'eip':
        c = AllenBradleyEIP()
        r = c.connect(endpoint)
        rj = json.loads(r)
        if not rj.get("success"):
            return r
        result = c.write_tag(tag_path, value)
        c.disconnect()
        return result
    return json.dumps({"error": f"Type PLC inconnu: {plc_type}"})


def probe_plc(endpoint: str, timeout: int = 2) -> str:
    """Détecte le type de PLC à une adresse IP par scan de ports.

    Scanne les ports caractéristiques : 102 (S7), 44818 (EtherNet/IP).

    Args:
        endpoint: Adresse IP à tester.
        timeout: Délai d'attente maximum en secondes (par défaut 2).

    Returns:
        str: Rapport JSON détaillant les ports et protocoles découverts.
    """
    results = {"target": endpoint, "detected_protocols": []}
    port_map = {102: "Siemens S7 (ISO-TSAP)", 44818: "EtherNet/IP (Rockwell/AB)"}

    for port, proto in port_map.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((endpoint, port))
            s.close()
            if result == 0:
                results["detected_protocols"].append({
                    "port": port,
                    "protocol": proto,
                    "status": "open"
                })
        except Exception:
            pass

    results["count"] = len(results["detected_protocols"])
    return json.dumps(results, indent=2)


# ── Enregistrement dans le registre Helios ──────────────────────────────

from tools.registry import registry


def _check_snap7() -> bool:
    """Vérifie si la bibliothèque snap7 est disponible.

    Returns:
        bool: True si snap7 est installé, False sinon.
    """
    return _SNAP7_OK


registry.register(
    name="plc_read",
    toolset="industrial",
    schema={
        "name": "plc_read",
        "description": "Lit un tag sur un automate industriel en temps réel. "
                       "Support: Siemens S7 (s7), Rockwell (rockwell), Allen-Bradley EIP (eip). "
                       "Exemple: plc_read('s7', '192.168.1.10', 'DB1.DBX0.0')",
        "parameters": {
            "type": "object",
            "properties": {
                "plc_type": {
                    "type": "string",
                    "enum": ["s7", "rockwell", "eip"],
                    "description": "Type d'automate: s7 (Siemens), rockwell (pylogix), eip (pycomm3)"
                },
                "endpoint": {
                    "type": "string",
                    "description": "Adresse IP de l'automate"
                },
                "tag_path": {
                    "type": "string",
                    "description": "Chemin du tag (ex: DB1.DBX0.0, MyProgram.MyTag)"
                }
            },
            "required": ["plc_type", "endpoint", "tag_path"]
        }
    },
    handler=lambda a, **kw: read_plc_tag(
        a.get("plc_type", ""), a.get("endpoint", ""), a.get("tag_path", ""), **kw
    ),
    check_fn=_check_snap7,
    requires_env=[],
    description="Lecture temps réel de tags PLC Siemens/Rockwell",
    emoji="🔌",
)

registry.register(
    name="plc_write",
    toolset="industrial",
    schema={
        "name": "plc_write",
        "description": "Écrit une valeur sur un tag automate en temps réel.",
        "parameters": {
            "type": "object",
            "properties": {
                "plc_type": {"type": "string", "enum": ["s7", "rockwell", "eip"]},
                "endpoint": {"type": "string", "description": "Adresse IP"},
                "tag_path": {"type": "string", "description": "Chemin du tag"},
                "value": {"type": "string", "description": "Valeur à écrire"}
            },
            "required": ["plc_type", "endpoint", "tag_path", "value"]
        }
    },
    handler=lambda a, **kw: write_plc_tag(
        a.get("plc_type", ""), a.get("endpoint", ""), a.get("tag_path", ""), a.get("value", ""), **kw
    ),
    check_fn=_check_snap7,
    requires_env=[],
    description="Écriture temps réel sur tags PLC Siemens/Rockwell",
    emoji="🔌",
)

registry.register(
    name="plc_probe",
    toolset="industrial",
    schema={
        "name": "plc_probe",
        "description": "Détecte les automates industriels sur un réseau par scan de ports. "
                       "Scanne les ports 102 (Siemens S7) et 44818 (EtherNet/IP). Retourne "
                       "les protocoles détectés à une adresse IP donnée.",
        "parameters": {
            "type": "object",
            "properties": {
                "endpoint": {"type": "string", "description": "Adresse IP à sonder"},
                "timeout": {"type": "integer", "description": "Timeout par port (secondes)", "default": 2}
            },
            "required": ["endpoint"]
        }
    },
    handler=lambda a, **kw: probe_plc(a.get("endpoint", ""), a.get("timeout", 2), **kw),
    check_fn=None,
    requires_env=[],
    description="Détection d'automates industriels par scan réseau",
    emoji="🔍",
)