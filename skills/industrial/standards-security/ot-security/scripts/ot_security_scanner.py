#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OT Security Scanner - Script asynchrone d'audit non-intrusif de ports industriels.
Permet d'identifier les protocoles OT actifs (Modbus, S7Comm, OPC UA, EtherNet/IP) sur une plage IP.
"""

import sys
import time
import socket
import asyncio
import json
import argparse
import ipaddress
from typing import List, Dict

# Mappage des ports standards industriels
OT_PORT_MAP = {
    102: "Siemens S7Comm",
    502: "Modbus TCP",
    4840: "OPC UA",
    44818: "EtherNet/IP / CIP",
    18245: "GE SRTP",
    9600: "Omron FINS",
    5007: "Mitsubishi MC Protocol",
    47808: "BACnet/IP",
    1883: "MQTT",
    8883: "MQTT TLS"
}

async def scan_port(ip: str, port: int, timeout: float) -> Dict:
    """Tente de se connecter à une adresse IP et un port donnés pour valider l'ouverture du service."""
    result = {"port": port, "service": OT_PORT_MAP.get(port, "Unknown"), "open": False}
    try:
        # Utilisation de asyncio.open_connection pour un scan asynchrone non-intrusif (pas de payload envoyé)
        conn = asyncio.open_connection(ip, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)
        result["open"] = True
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        pass
    return result

async def scan_host(ip: str, ports: List[int], timeout: float) -> Dict:
    """Scanne un hôte pour l'ensemble des ports spécifiés."""
    tasks = [scan_port(ip, port, timeout) for port in ports]
    port_results = await asyncio.gather(*tasks)
    
    open_services = [r for r in port_results if r["open"]]
    return {
        "ip": ip,
        "scanned_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "active": len(open_services) > 0,
        "services": open_services
    }

async def main_async(targets: List[str], ports: List[int], timeout: float, max_concurrency: int):
    """Orchestre le scan d'une liste d'adresses IP avec une limite de concurrence."""
    sem = asyncio.Semaphore(max_concurrency)
    
    async def worker(ip: str):
        async with sem:
            return await scan_host(ip, ports, timeout)
            
    tasks = [worker(ip) for ip in targets]
    results = await asyncio.gather(*tasks)
    
    # Filtrer pour n'afficher que les hôtes qui ont au moins un service ouvert
    active_hosts = [r for r in results if r["active"]]
    
    report = {
        "scan_summary": {
            "total_hosts_scanned": len(targets),
            "active_hosts_found": len(active_hosts),
            "ports_audited": ports
        },
        "hosts": active_hosts
    }
    
    print(json.dumps(report, indent=2, ensure_ascii=False))

def parse_ip_targets(target_str: str) -> List[str]:
    """Parse une chaîne contenant des IPs séparées par des virgules ou des blocs CIDR (ex: 192.168.1.0/24)."""
    ips = []
    for part in target_str.split(","):
        part = part.strip()
        if not part:
            continue
        if "/" in part:
            try:
                network = ipaddress.ip_network(part, strict=False)
                for host in network.hosts():
                    ips.append(str(host))
            except ValueError as e:
                print(f"Erreur de format CIDR : '{part}' ({e})", file=sys.stderr)
        else:
            try:
                ip = ipaddress.ip_address(part)
                ips.append(str(ip))
            except ValueError as e:
                print(f"Erreur de format IP : '{part}' ({e})", file=sys.stderr)
    return ips

def main():
    parser = argparse.ArgumentParser(description="Scanner de sécurité non-intrusif pour protocoles industriels (OT).")
    parser.add_argument("--targets", required=True, help="IPs séparées par virgules ou plage CIDR (ex: 192.168.1.50,192.168.2.0/24)")
    parser.add_argument("--ports", default="102,502,4840,44818,1883", help="Ports à scanner séparés par virgules (défaut: 102,502,4840,44818,1883)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Timeout de connexion en secondes (défaut: 1.0)")
    parser.add_argument("--concurrency", type=int, default=50, help="Nombre maximum de connexions simultanées (défaut: 50)")
    
    args = parser.parse_args()
    
    # Parser les cibles et les ports
    targets = parse_ip_targets(args.targets)
    if not targets:
        print("Aucune adresse IP cible valide à scanner.", file=sys.stderr)
        sys.exit(1)
        
    try:
        ports = [int(p.strip()) for p in args.ports.split(",") if p.strip()]
    except ValueError:
        print("Erreur : La liste des ports doit contenir uniquement des nombres entiers.", file=sys.stderr)
        sys.exit(1)
        
    # Lancer le scan asynchrone
    asyncio.run(main_async(targets, ports, args.timeout, args.concurrency))

if __name__ == "__main__":
    main()
