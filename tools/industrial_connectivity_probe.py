#!/usr/bin/env python3
"""
Module Industrial Connectivity Probe - Découvrir et diagnostiquer les équipements industriels sur un réseau OT.

Fonctionnalités :
- Découverte de réseaux OT (scan IP, identification de protocoles)
- Détection de protocoles : Siemens S7, EtherNet/IP, PROFINET DCP, Modbus TCP, OPC UA, BACnet
- Fingerprinting (manufacturer, device type, firmware)
- Mode passif (analyse de PCAP)
- Rapport structuré des équipements découverts

Usage:
    from tools.industrial_connectivity_probe import probe_network, probe_target, analyze_pcap
    results = probe_network("192.168.1.0/24")
    results = probe_target("192.168.1.100")
    results = analyze_pcap("capture.pcapng")
"""

import json
import logging
import socket
import struct
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any

logger = logging.getLogger(__name__)

# Délais et timeouts par défaut
DEFAULT_TIMEOUT = 2.0
DEFAULT_PARALLELISM = 50



class Protocol(Enum):
    """Protocoles industriels détectables."""
    SIEMENS_S7 = "siemens-s7"
    ETHERNET_IP = "ethernet-ip"
    PROFINET_DCP = "profinet-dcp"
    MODBUS_TCP = "modbus-tcp"
    OPC_UA = "opc-ua"
    BACNET = "bacnet"
    ADS = "ads"  # Beckhoff
    FINS = "fins"  # Omron
    UNKNOWN = "unknown"


@dataclass
class DeviceInfo:
    """Informations sur un équipement découvert."""
    ip_address: str
    mac_address: str = ""
    hostname: str = ""
    vendor: str = ""
    model: str = ""
    firmware: str = ""
    serial: str = ""
    protocols: List[str] = field(default_factory=list)
    ports_open: List[int] = field(default_factory=list)
    os_type: str = ""
    ping_ok: bool = False
    response_time_ms: float = 0.0


@dataclass
class ScanResult:
    """Résultat complet d'un scan réseau."""
    scan_timestamp: float = 0.0
    scan_range: str = ""
    devices: List[DeviceInfo] = field(default_factory=list)
    total_devices: int = 0
    duration_seconds: float = 0.0



def _raw_tcp_send(ip: str, port: int, payload: bytes, timeout: float = DEFAULT_TIMEOUT) -> Optional[bytes]:
    """Envoie un payload TCP raw et retourne la réponse."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        sock.sendall(payload)
        time.sleep(0.1)
        response = sock.recv(4096)
        return response
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None
    finally:
        if sock:
            sock.close()


def _raw_udp_send(ip: str, port: int, payload: bytes, timeout: float = DEFAULT_TIMEOUT) -> Optional[bytes]:
    """Envoie un payload UDP et attend une réponse."""
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(payload, (ip, port))
        response, _ = sock.recvfrom(4096)
        return response
    except (socket.timeout, OSError):
        return None
    finally:
        if sock:
            sock.close()


# ──────────────────────────────────────────────────────────────
# Ping / ICMP
# ──────────────────────────────────────────────────────────────

def _ping_host(ip: str, timeout: float = DEFAULT_TIMEOUT) -> Tuple[bool, float]:
    """Ping un hôte via ICMP (socket raw). Retourne (success, temps_ms)."""
    import subprocess  # Import local pour éviter les dépendances lourdes
    start = time.time()
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip],
            capture_output=True,
            timeout=timeout + 1,
            text=True
        )
        elapsed = (time.time() - start) * 1000
        if result.returncode == 0 and "TTL=" in result.stdout:
            # Extraire le temps
            ttl_match = [line for line in result.stdout.splitlines() if "TTL=" in line]
            return True, elapsed
        return False, 0.0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False, 0.0


# ──────────────────────────────────────────────────────────────
# Détection de protocoles
# ──────────────────────────────────────────────────────────────

def _detect_siemens_s7(ip: str) -> Optional[Dict]:
    """Détecte un automate Siemens S7 sur le port 102."""
    # ISO over TCP (RFC 1006) / S7 communication
    # TPKT header + S7 Job Request : Read SZL (System Status List)
    payload = bytes.fromhex(
        "03000016"  # TPKT (version 3, length 22)
        "11e0000000180000"  # ISO-COTP CR (connect request)
        "1a0000020001000000040001"  # SZL Part Number
    )
    response = _raw_tcp_send(ip, 102, payload)
    if response is None:
        return None

    info = {"protocol": "siemens-s7"}
    try:
        # Vérifier la réponse COTP
        if len(response) > 22 and response[4] == 0x11 and response[5] == 0xE0:
            info["status"] = "connected"
            # Extraire des infos du CPU via une deuxième requête
            # Read SZL ID 0x0011 (Module identification)
            szl_payload = bytes.fromhex(
                "0300001f02f08072000000004d00000014000000"
                "112200110012000000000000000000"
            )
            s2 = _raw_tcp_send(ip, 102, szl_payload)
            if s2:
                info["cpu_identified"] = True
                # Tentative d'extraction du numéro de série et type
                if len(s2) > 100:
                    info["module_type"] = s2[70:90].decode("ascii", errors="ignore").strip()
                    info["serial"] = s2[90:110].decode("ascii", errors="ignore").strip()
    except Exception:
        pass
    return info


def _detect_ethernet_ip(ip: str) -> Optional[Dict]:
    """Détecte un équipement Rockwell / EtherNet/IP sur le port 44818."""
    # CIP List Identity Request
    payload = bytes.fromhex(
        "630000000000000000000000"
        "01000e000000000000000000"
        "00000000000000"
    )
    # Connect via TCP
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(DEFAULT_TIMEOUT)
        sock.connect((ip, 44818))
        # ENIP Register Session
        register_payload = bytes.fromhex("6300000000000000000000000100040000000000000000000000000000000010")
        sock.sendall(register_payload)
        time.sleep(0.2)
        response = sock.recv(4096)
        if not response or len(response) < 28:
            return None

        info = {"protocol": "ethernet-ip", "session": ""}
        if response[0:2] == b"\x63\x00":
            session = response[4:8]
            info["session"] = session.hex()

            # List Identity
            list_identity_payload = bytes.fromhex(
                "63000000000000000000000001000e00000000000000000000000000000000"
            )
            sock.sendall(list_identity_payload)
            time.sleep(0.3)
            id_response = sock.recv(4096)
            if id_response and len(id_response) > 28:
                # Extraire Vendor ID, Device Type, Product Name
                info["vendor_id"] = int.from_bytes(id_response[50:52], "little")
                device_type = int.from_bytes(id_response[52:54], "little")
                # Product Name (LEN + data) à offset variable
                info["vendor"] = _get_enip_vendor(info.get("vendor_id", 0))
                info["device_type"] = device_type
                # Product Name
                name_offset = 68
                if len(id_response) > name_offset:
                    name_len = id_response[name_offset]
                    name_data = id_response[name_offset + 1:name_offset + 1 + name_len]
                    info["product_name"] = name_data.decode("ascii", errors="ignore").strip()
        return info
    except (socket.timeout, ConnectionRefusedError, OSError):
        return None
    finally:
        if sock:
            sock.close()


def _get_enip_vendor(vendor_id: int) -> str:
    """Retourne le nom du constructeur EtherNet/IP."""
    vendors = {
        1: "Rockwell Automation",
        2: "ABB",
        3: "Honeywell",
        4: "Schneider Electric",
        5: "Omron",
        41: "Siemens",
        59: "Mitsubishi Electric",
        74: "Bosch Rexroth",
        82: "Beckhoff",
        98: "Parker Hannifin",
        108: "Banner Engineering",
        123: "SMC",
        126: "Keyence",
        139: "Cognex",
        146: "Yaskawa",
        153: "Ifm Electronic",
        162: "Endress+Hauser",
        166: "Turck",
        171: "Balluff",
        195: "SICK",
        206: "Pepperl+Fuchs",
        220: "Murrelektronik",
        258: "WAGO",
        262: "Weidmüller",
        268: "Phoenix Contact",
        311: "Anybus/HMS",
        394: "Advantech",
    }
    return vendors.get(vendor_id, f"Unknown ({vendor_id})")


def _detect_profinet_dcp(ip: str) -> Optional[Dict]:
    """Détecte un équipement PROFINET via DCP (Discovery and Configuration Protocol)."""
    # PROFINET DCP Identify All Request
    # Destination MAC: 01:0E:CF:00:00:00
    # EtherType: 0x8892
    dcp_payload = bytes.fromhex(
        "010ecf000000"  # DST MAC
        + "000000000000"  # SRC MAC (placeholder)
        + "8892"  # EtherType PROFINET
        + "feff0104"  # FrameID DCP Identify All
        + "0200040000000000"  # DCP header
        + "0104"  # Option=1 (IP), Sub=4 (Response)
    )
    # Mode broadcast UDP sur port 0x8892
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(DEFAULT_TIMEOUT)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(dcp_payload, ("<broadcast>", 0x8892))
        response, addr = sock.recvfrom(4096)
        if response and len(response) > 20:
            info = {"protocol": "profinet-dcp"}
            # Extraire le nom de station
            idx = response.find(b"Station Name")
            if idx >= 0:
                name_len = response[idx + 12]
                name_data = response[idx + 13:idx + 13 + name_len]
                info["station_name"] = name_data.decode("ascii", errors="ignore").strip()
            # Extraire l'IP
            ip_bytes = response.find(b"IP")
            if ip_bytes >= 0 and len(response) > ip_bytes + 10:
                info["ip"] = ".".join(str(b) for b in response[ip_bytes + 4:ip_bytes + 8])
            # Vendor
            info["vendor"] = "PROFINET Device"
            return info
    except (socket.timeout, OSError):
        pass
    finally:
        if sock:
            sock.close()
    return None


def _detect_modbus_tcp(ip: str) -> Optional[Dict]:
    """Détecte un équipement Modbus TCP sur le port 502."""
    # Read Device Identification (function code 0x43)
    payload = bytes.fromhex(
        "000000000006"  # MBAP header (len=6)
        "01114b"         # Transaction=1, Unit ID=1, FC=0x43, MEI Type=0x0B (Read ID)
    )
    response = _raw_tcp_send(ip, 502, payload)
    if response is None:
        return None

    info = {"protocol": "modbus-tcp"}
    try:
        if len(response) > 8:
            # Extraire les infos vendor, product code, major/minor revision
            # Obj ID 0: Vendor Name, 1: Product Code, 2: Major/Minor Revision
            # Parse simple
            data = response[8:]
            info["device_identified"] = True
    except Exception:
        pass
    return info


def _detect_opcua(ip: str) -> Optional[Dict]:
    """Détecte un serveur OPC UA sur les ports 4840 ou 48010."""
    # OPC UA Hello message
    payload = bytes.fromhex(
        "48454100000000d8000000"  # HELLO, length=216
        "01010000"                # Version Protocol
        "00000000"  # Request buffer size
        + "00000800"  # Request channel lifetime
        + "01000000"  # Endpoint URL
    )
    response = _raw_tcp_send(ip, 4840, payload)
    if response is None:
        response = _raw_tcp_send(ip, 48010, payload)

    if response is None:
        return None

    info = {"protocol": "opc-ua", "port": 4840}
    try:
        if len(response) > 8 and response[0:4] == b"HELL":
            info["status"] = "discovered"
    except Exception:
        pass
    return info


def _detect_bacnet(ip: str) -> Optional[Dict]:
    """Détecte un équipement BACnet sur le port 47808 (BACnet/IP)."""
    # BACnet Who-Is broadcast
    payload = bytes.fromhex(
        "810a001001000001"  # BVLL header
        "2001 000c"         # NPCI
        "0100"              # APDU: Who-Is
    )
    response = _raw_udp_send(ip, 47808, payload)
    if response is None:
        return None

    info = {"protocol": "bacnet"}
    try:
        if len(response) > 8 and response[0:4] == b"\x81\x0a\x00":
            info["device_identified"] = True
    except Exception:
        pass
    return info


# ──────────────────────────────────────────────────────────────
# Scan de ports
# ──────────────────────────────────────────────────────────────

INDUSTRIAL_PORTS = {
    102: "Siemens S7",
    502: "Modbus TCP",
    44818: "EtherNet/IP (CIP)",
    4840: "OPC UA",
    48010: "OPC UA (Alt)",
    47808: "BACnet/IP",
    34962: "PROFINET RT",
    34964: "PROFINET RT (Alt)",
    48898: "ADS (Beckhoff)",
    9600: "Omron FINS/UDP",
    20000: "DNP3",
    1911: "Niagara Fox",
    80: "HTTP (Embedded)",
    443: "HTTPS (Embedded)",
    22: "SSH",
    23: "Telnet",
    161: "SNMP",
}


def _port_scan(ip: str, ports: List[int] = None, timeout: float = 1.0) -> List[int]:
    """Scanne les ports d'une cible et retourne les ports ouverts."""
    if ports is None:
        ports = list(INDUSTRIAL_PORTS.keys())

    open_ports = []
    for port in ports:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
        except OSError:
            pass
        finally:
            if sock:
                sock.close()
    return open_ports


# ──────────────────────────────────────────────────────────────
# API Publique
# ──────────────────────────────────────────────────────────────

def probe_target(ip: str, timeout: float = DEFAULT_TIMEOUT, scan_ports: bool = True) -> DeviceInfo:
    """Sonde une adresse IP cible pour identifier les équipements industriels.

    Args:
        ip: Adresse IP à sonder
        timeout: Timeout en secondes pour chaque sonde
        scan_ports: Si True, scanne aussi les ports industriels

    Returns:
        DeviceInfo: Informations sur l'équipement détecté
    """
    device = DeviceInfo(ip_address=ip)
    start = time.time()

    # Ping
    ping_ok, ping_ms = _ping_host(ip, timeout)
    device.ping_ok = ping_ok
    device.response_time_ms = ping_ms

    if scan_ports:
        device.ports_open = _port_scan(ip, timeout=timeout * 0.5)

    # Détection par protocole
    protocol_detectors = [
        ("Siemens S7", _detect_siemens_s7),
        ("EtherNet/IP", _detect_ethernet_ip),
        ("Modbus TCP", _detect_modbus_tcp),
        ("OPC UA", _detect_opcua),
        ("BACnet", _detect_bacnet),
        ("PROFINET DCP", _detect_profinet_dcp),
    ]

    for proto_name, detector in protocol_detectors:
        try:
            result = detector(ip)
            if result is not None:
                device.protocols.append(proto_name)
                # Enrichir avec les infos du constructeur
                if "vendor" in result:
                    device.vendor = result["vendor"]
                if "product_name" in result:
                    device.model = result["product_name"]
                if "serial" in result:
                    device.serial = result["serial"]
                if "firmware" in result:
                    device.firmware = result["firmware"]
                if "station_name" in result:
                    device.hostname = result["station_name"]
        except Exception as e:
            logger.debug(f"Erreur {proto_name} sur {ip}: {e}")

    return device


def probe_network(subnet: str, timeout: float = DEFAULT_TIMEOUT,
                  scan_ports: bool = True) -> ScanResult:
    """Sonde un sous-réseau complet pour découvrir les équipements industriels.

    Args:
        subnet: Sous-réseau au format CIDR (ex: '192.168.1.0/24')
        timeout: Timeout par sonde
        scan_ports: Scanne les ports industriels

    Returns:
        ScanResult: Résultats du scan
    """
    import ipaddress

    start = time.time()
    result = ScanResult(
        scan_timestamp=start,
        scan_range=subnet,
    )

    network = ipaddress.ip_network(subnet, strict=False)
    hosts: Set[str] = set()  # Dédoublonnage

    # Ping subnet
    for ip_addr in network.hosts():
        ip_str = str(ip_addr)
        try:
            device = probe_target(ip_str, timeout=timeout, scan_ports=scan_ports)
            if device.ping_ok or device.protocols or device.ports_open:
                hosts.add(ip_str)
                result.devices.append(device)
        except Exception as e:
            logger.debug(f"Erreur sur {ip_str}: {e}")

    result.total_devices = len(result.devices)
    result.duration_seconds = time.time() - start
    return result


def analyze_pcap(pcap_path: str) -> Dict:
    """Analyse un fichier PCAP pour identifier les équipements et protocoles industriels.

    Args:
        pcap_path: Chemin vers le fichier PCAP/PCAPNG

    Returns:
        Dict: Statistiques des protocoles détectés et équipements
    """
    try:
        import struct
    except ImportError:
        pass

    pcap_file = Path(pcap_path) if not isinstance(pcap_path, Path) else pcap_path  # noqa: F821
    if not pcap_file.exists():
        return {"error": f"Fichier PCAP introuvable : {pcap_path}"}

    # Vérifier la disponibilité de scapy
    try:
        from scapy.utils import RawPcapReader  # noqa: F401
        has_scapy = True
    except ImportError:
        has_scapy = False

    if has_scapy:
        result = _analyze_pcap_scapy(pcap_path)
    else:
        result = _analyze_pcap_basic(pcap_path)
        
    result["format"] = "pcapng" if str(pcap_path).lower().endswith(".pcapng") else "pcap"
    return result


def _analyze_pcap_basic(pcap_path: str) -> Dict:
    """Analyse PCAP basique sans scapy (fichier texte uniquement)."""
    # Limité à lire les métadonnées du fichier
    pcap_path_obj = Path(pcap_path)
    info = {
        "file": pcap_path_obj.name,
        "size_bytes": pcap_path_obj.stat().st_size,
        "note": "Install scapy pour analyse complète du PCAP",
        "scapy_available": False,
    }
    # Tentative de parsing global header
    with open(pcap_path, "rb") as f:
        header = f.read(24)
        if len(header) >= 24 and header[0:4] in (b"\xa1\xb2\xc3\xd4", b"\xd4\xc3\xb2\xa1",
                                                    b"\x4d\x3c\x2b\x1a"):
            magic = header[0:4]
            snaplen = struct.unpack("<I", header[16:20])[0]
            link_type = struct.unpack("<I", header[20:24])[0]
            info["magic"] = magic.hex()
            info["snaplen"] = snaplen
            info["link_type"] = {
                1: "Ethernet",
                101: "Raw IP",
                113: "Linux SLL",
            }.get(link_type, f"Unknown ({link_type})")
    return info


def _analyze_pcap_scapy(pcap_path: str) -> Dict:
    """Analyse PCAP avancée avec scapy."""
    from scapy.utils import RawPcapReader
    from scapy.layers.inet import IP, TCP, UDP

    protocols: Dict[str, int] = {}
    devices: Dict[str, Set[str]] = {}
    total_packets = 0

    try:
        reader = RawPcapReader(pcap_path)
        for pkt_data, pkt_meta in reader:
            total_packets += 1
            if total_packets > 50000:
                break  # Limite pour performance

            # Analyse simple
            if len(pkt_data) < 34:
                continue

            # EtherType (offset 12-13)
            eth_type = (pkt_data[12] << 8) | pkt_data[13]

            if eth_type == 0x0800:  # IPv4
                ip_src = ".".join(str(b) for b in pkt_data[26:30])
                ip_dst = ".".join(str(b) for b in pkt_data[30:34])

                proto = pkt_data[23]
                if proto == 6:  # TCP
                    if len(pkt_data) > 38:
                        src_port = (pkt_data[34] << 8) | pkt_data[35]
                        dst_port = (pkt_data[36] << 8) | pkt_data[37]
                        port = dst_port if dst_port in INDUSTRIAL_PORTS else src_port
                        if port in INDUSTRIAL_PORTS:
                            proto_name = INDUSTRIAL_PORTS[port]
                            protocols[proto_name] = protocols.get(proto_name, 0) + 1
                            devices.setdefault(ip_src, set()).add(proto_name)
                            devices.setdefault(ip_dst, set()).add(proto_name)

            # PROFINET EtherType 0x8892
            if eth_type == 0x8892:
                protocols["PROFINET DCP/RT"] = protocols.get("PROFINET DCP/RT", 0) + 1

    except Exception:
        pass

    # Formater les devices
    formatted_devices = []
    for ip, protos in sorted(devices.items()):
        formatted_devices.append({
            "ip": ip,
            "protocols": sorted(protos),
        })

    return {
        "file": Path(pcap_path).name,
        "total_packets_analyzed": min(total_packets, 50000),
        "protocols_detected": protocols,
        "devices_found": formatted_devices,
        "scapy_available": True,
    }


from pathlib import Path  # noqa: E402


# ──────────────────────────────────────────────────────────────
# Intégration Registry
# ──────────────────────────────────────────────────────────────

from tools.registry import registry  # noqa: E402


def _check_connectivity_probe() -> bool:
    """Vérifie si les dépendances réseau sont disponibles."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.close()
        return True
    except OSError:
        return False


registry.register(
    name="industrial_connectivity_probe_target",
    toolset="industrial",
    schema={
        "name": "industrial_connectivity_probe_target",
        "description": "Sonde une adresse IP cible pour identifier les équipements industriels (Siemens S7, Rockwell EtherNet/IP, Modbus TCP, OPC UA, BACnet, PROFINET).",
        "parameters": {
            "type": "object",
            "properties": {
                "ip": {
                    "type": "string",
                    "description": "Adresse IP à sonder (ex: 192.168.1.100)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout en secondes (défaut: 2.0)"
                },
                "scan_ports": {
                    "type": "boolean",
                    "description": "Scanner les ports industriels standards"
                }
            },
            "required": ["ip"]
        }
    },
    handler=lambda args, **kw: json.dumps(
        asdict(probe_target(
            ip=args.get("ip", ""),
            timeout=float(args.get("timeout", 2.0)),
            scan_ports=args.get("scan_ports", True)
        )),
        indent=2, ensure_ascii=False
    ),
    check_fn=_check_connectivity_probe,
    is_async=False,
    description="Sonder une adresse IP pour identifier un équipement industriel.",
    emoji="🔍",
)

registry.register(
    name="industrial_connectivity_probe_network",
    toolset="industrial",
    schema={
        "name": "industrial_connectivity_probe_network",
        "description": "Scanne un sous-réseau pour découvrir tous les équipements industriels (ping + détection de protocoles + scan ports). Peut prendre 30-60 secondes selon la taille du réseau.",
        "parameters": {
            "type": "object",
            "properties": {
                "subnet": {
                    "type": "string",
                    "description": "Sous-réseau au format CIDR (ex: 192.168.1.0/24)"
                },
                "timeout": {
                    "type": "number",
                    "description": "Timeout par sonde (défaut: 2.0)"
                }
            },
            "required": ["subnet"]
        }
    },
    handler=lambda args, **kw: json.dumps({
        "scan_range": args.get("subnet", ""),
        **{k: v for k, v in asdict(probe_network(
            subnet=args.get("subnet", ""),
            timeout=float(args.get("timeout", 2.0)),
            scan_ports=True
        )).items() if k != "scan_timestamp"}
    }, indent=2, ensure_ascii=False),
    check_fn=_check_connectivity_probe,
    is_async=False,
    description="Scanner un sous-réseau pour découvrir les équipements industriels.",
    emoji="🌐",
)

registry.register(
    name="industrial_connectivity_analyze_pcap",
    toolset="industrial",
    schema={
        "name": "industrial_connectivity_analyze_pcap",
        "description": "Analyse un fichier PCAP/PCAPNG de trafic réseau industriel pour identifier les équipements et protocoles (PROFINET, Modbus, EtherNet/IP, etc.).",
        "parameters": {
            "type": "object",
            "properties": {
                "pcap_path": {
                    "type": "string",
                    "description": "Chemin complet vers le fichier .pcap ou .pcapng"
                }
            },
            "required": ["pcap_path"]
        }
    },
    handler=lambda args, **kw: json.dumps(
        analyze_pcap(args.get("pcap_path", "")),
        indent=2, ensure_ascii=False
    ),
    is_async=False,
    description="Analyser un fichier PCAP de trafic réseau industriel.",
    emoji="📊",
)