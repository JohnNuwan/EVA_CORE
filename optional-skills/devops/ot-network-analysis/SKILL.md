---
name: ot-network-analysis
description: "Analyser des captures de paquets réseau industriels (PCAP)."
version: 1.0.0
author: EVA
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [network, pcap, scapy, wireshark, modbus, profinet, ethernet-ip, industrial-automation, cybersecurity]
  related_skills: [plc-connectivity, industrial-protocols]
---

# Analyse de Trames Réseau OT (Wireshark & Scapy)

## Vue d'ensemble

Le diagnostic des réseaux industriels (OT) nécessite souvent d'analyser des captures de paquets (fichiers `.pcap` ou `.pcapng` générés par Wireshark ou tcpdump). Ces fichiers contiennent l'historique exact des échanges entre les automates (PLC), les supervisions (SCADA) et les capteurs.

Cette compétence guide l'agent EVA pour écrire des scripts d'analyse de paquets réseau en Python en utilisant la bibliothèque **Scapy**. Elle permet d'identifier les pannes intermittentes, les latences excessives, les erreurs de communication et les requêtes suspectes.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Analyser un fichier de capture réseau `.pcap` pour identifier la cause d'une perte de connexion.
- Calculer le temps de réponse d'un automate (temps entre une requête SCADA et la réponse PLC).
- Détecter des erreurs réseau (retransmissions TCP, paquets dupliqués, rejets de connexion).
- Décoder et analyser des payloads industriels spécifiques (Modbus TCP, EtherNet/IP, CIP, PROFINET).
- Extraire des statistiques de trafic (débit par équipement, topologie de communication).

---

## 1. Lecture Optimisée de Gros Fichiers PCAP

Charger un fichier PCAP de plusieurs centaines de mégaoctets avec la méthode standard `rdpcap()` de Scapy charge l'intégralité du fichier en RAM, ce qui peut provoquer un crash mémoire (OOM).

### Recette de lecture en flux (Streaming) avec `PcapReader` :
```python
from scapy.all import PcapReader, IP, TCP

def analyze_large_pcap(file_path):
    """
    Parcourt un fichier PCAP ligne à ligne à l'aide d'un générateur
    pour maintenir une empreinte mémoire minimale (taille de guêpe).
    """
    total_packets = 0
    modbus_packets = 0
    
    # PcapReader renvoie un itérateur sur les paquets
    with PcapReader(file_path) as pcap_reader:
        for packet in pcap_reader:
            total_packets += 1
            
            # Vérification de la couche IP et TCP
            if packet.haslayer(IP) and packet.haslayer(TCP):
                ip_layer = packet[IP]
                tcp_layer = packet[TCP]
                
                # Filtrage sur le port Modbus TCP (standard : 502)
                if tcp_layer.sport == 502 or tcp_layer.dport == 502:
                    modbus_packets += 1
                    
                    # Traiter le paquet
                    src_ip = ip_layer.src
                    dst_ip = ip_layer.dst
                    
    return {
        "total_packets": total_packets,
        "modbus_packets": modbus_packets
    }
```

---

## 2. Décodage de Protocoles OT : Cas de Modbus-TCP

Les protocoles industriels ont des en-têtes binaires structurés. Modbus-TCP utilise un en-tête MBAP (Modbus Application Protocol) de 7 octets suivi du PDU (Protocol Data Unit).

```
Structure de l'en-tête MBAP Modbus TCP :
┌─────────────────────┬─────────────────────┬─────────────────────┬──────────┐
│   Transaction ID    │     Protocol ID     │       Length        │ Unit ID  │
│      (2 octets)     │   (2 octets = 0)    │     (2 octets)      │ (1 oct.) │
└─────────────────────┴─────────────────────┴─────────────────────┴──────────┘
```

### Recette de décodage binaire brut d'un paquet Modbus :
```python
from scapy.all import Raw

def decode_modbus_packet(packet):
    """
    Décode les informations clés de l'en-tête Modbus TCP à partir de la couche Raw.
    """
    if not packet.haslayer(Raw):
        return None
        
    payload = packet[Raw].load
    
    # Modbus TCP requiert au minimum 8 octets (7 pour le MBAP + 1 pour le code fonction)
    if len(payload) < 8:
        return None
        
    # Extraction des champs du MBAP (Big Endian)
    transaction_id = int.from_bytes(payload[0:2], byteorder='big')
    protocol_id = int.from_bytes(payload[2:4], byteorder='big')
    length = int.from_bytes(payload[4:6], byteorder='big')
    unit_id = payload[6]
    
    # Extraction du PDU
    function_code = payload[7]
    
    # Si le code fonction a son bit de poids fort à 1 (>= 128 / 0x80), c'est une exception/erreur Modbus
    is_exception = function_code >= 0x80
    exception_code = payload[8] if is_exception and len(payload) > 8 else None
    
    return {
        "transaction_id": transaction_id,
        "unit_id": unit_id,
        "function_code": function_code,
        "is_exception": is_exception,
        "exception_code": exception_code
    }
```

---

## 3. Diagnostic de Performances et Latences

Mesurer le temps de réponse d'un automate (temps entre une commande et sa réponse) permet de détecter les saturations de CPU d'automates.

```python
def compute_plc_latencies(pcap_path, plc_ip):
    transactions = {} # clé : transaction_id, valeur : timestamp de la requête
    latencies = []
    
    with PcapReader(pcap_path) as pcap_reader:
        for packet in pcap_reader:
            if not (packet.haslayer(IP) and packet.haslayer(Raw)):
                continue
                
            ip_layer = packet[IP]
            payload = packet[Raw].load
            
            if len(payload) < 8:
                continue
                
            # Décodage rapide de transaction ID
            tx_id = int.from_bytes(payload[0:2], byteorder='big')
            
            # Si la source est le client (SCADA) -> C'est une requête
            if ip_layer.dst == plc_ip:
                transactions[tx_id] = packet.time
                
            # Si la source est l'automate (PLC) -> C'est la réponse
            elif ip_layer.src == plc_ip:
                if tx_id in transactions:
                    request_time = transactions[tx_id]
                    # Calcul de la latence (temps écoulé en millisecondes)
                    latency_ms = (packet.time - request_time) * 1000
                    latencies.append(latency_ms)
                    del transactions[tx_id] # Nettoyage de la transaction traitée
                    
    # Statistiques
    import numpy as np
    return {
        "avg_latency_ms": np.mean(latencies) if latencies else 0.0,
        "max_latency_ms": np.max(latencies) if latencies else 0.0,
        "total_queries": len(latencies)
    }
```

---

## Pièges Courants (Common Pitfalls)

1. **Saturation de la mémoire avec `rdpcap()` :**
   * *Erreur* : Charger un gros fichier PCAP en entier avec `packets = rdpcap("capture.pcap")`. Le script crash immédiatement sur manque de mémoire RAM.
   * *Correction* : Utiliser le générateur `PcapReader` pour traiter les paquets un par un de manière itérative.

2. **Désalignement lors du décodage binaire :**
   * *Erreur* : Essayer de décoder les données de charge utile Modbus en utilisant des index fixes sans vérifier la taille réelle du paquet (`len(payload)`). Cela lève des erreurs d'index hors limites (`IndexError`).
   * *Correction* : Toujours vérifier la longueur minimale de la charge utile brute (`Raw.load`) avant d'accéder aux octets.

3. **Retransmissions et pertes réseau ignorées :**
   * *Erreur* : Calculer les temps de réponse sans filtrer les paquets TCP dupliqués ou les retransmissions, ce qui fausse les moyennes de latence.
   * *Correction* : Ignorer les paquets dont le flag TCP indique une retransmission ou dont le numéro de séquence a déjà été rencontré.

---

## Liste de Vérification (Checklist)

- [ ] La lecture de fichiers PCAP de grande taille utilise `PcapReader` sous forme de générateur (pas de chargement global en mémoire).
- [ ] Les fonctions d'analyse vérifient systématiquement la présence des couches réseau (`haslayer(IP)`) et de données (`haslayer(Raw)`) avant traitement.
- [ ] La taille du payload brut est vérifiée avant d'effectuer des conversions de tranches d'octets.
- [ ] Le script de diagnostic calcule les temps de réponse en faisant correspondre les identifiants de transactions de requêtes et de réponses.
- [ ] Les fichiers de captures volumineux sont traités par filtrage d'IP/ports au plus tôt dans la boucle de lecture pour accélérer le traitement.
