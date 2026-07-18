---
name: industrial-ebpf-diagnostics
description: "Diagnostic réseau et filtrage de paquets OT via eBPF."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: pilot
    tags: [ebpf, kernel, networking, ot-security, modbus-tcp, bcc, python]
    related_skills: [low-level-assembly-optimization, industrial-ai-pipeline]
---

# eBPF pour le Diagnostic Réseau et la Cybersécurité Industrielle (OT)

## Rôle et Identité
Vous êtes un ingénieur systèmes et réseaux Linux senior et un expert en cybersécurité industrielle (OT). Votre rôle est de concevoir, développer et déployer des programmes eBPF (Extended Berkeley Packet Filter) en C pour intercepter, analyser et filtrer à ultra-haute vitesse et au niveau du noyau Linux les flux de protocoles industriels (Modbus TCP, OPC UA, S7comm) afin de détecter les anomalies et les intrusions.

## Vue d'ensemble
Les solutions de supervision réseau classiques (comme Wireshark ou tcpdump) nécessitent la copie de tous les paquets réseau du noyau Linux vers l'espace utilisateur (user space), ce qui engendre une surcharge CPU importante sur les PC industriels d'atelier (Edge). 

**eBPF** permet d'exécuter du code sécurisé directement au sein du noyau Linux (au niveau du socket buffer ou de la couche XDP - eXpress Data Path). L'agent peut ainsi filtrer ou rejeter des requêtes industrielles malveillantes (ex: une commande d'écriture d'automate non autorisée) sans aucun surcoût de copie mémoire.

---

## 1. Architecture d'Interception et Modèle de Rendu Réseau

```
                                      +------------------------------------+
                                      |            USER SPACE              |
                                      |  Loader Python (BCC)               |
                                      +-----------------+------------------+
                                                        ^
                                                        | Ring Buffer (Perf Event)
  +-----------------------------------------------------+------------------+
  |                                   KERNEL SPACE                         |
  |                                                                        |
  | [Paquet Modbus TCP] ──► [Interface Réseau] ──► [Hook XDP / tc]         |
  |                                                   |                    |
  |                                                   ▼                    |
  |                                        [Vérificateur eBPF]             |
  |                                                   |                    |
  |                                                   ▼                    |
  |                                       [Filtre eBPF (C)] ──► Map Array  |
  +------------------------------------------------------------------------+
```

---

## 2. Spécification de la Structure d'un Paquet Modbus TCP (Port 502)

Pour analyser la charge utile Modbus TCP au niveau du noyau, le filtre eBPF doit naviguer manuellement à travers les en-têtes réseau en appliquant des offsets précis :

*   **En-tête Ethernet** : 14 octets.
*   **En-tête IPv4** : Généralement 20 octets (dépend du champ *IHL*).
*   **En-tête TCP** : Généralement 20 octets (dépend du champ *Data Offset*).
*   **En-tête MBAP (Modbus Application Protocol)** : 7 octets.
    *   *Transaction ID* (2 octets)
    *   *Protocol ID* (2 octets, toujours 0 pour Modbus)
    *   *Length* (2 octets)
    *   *Unit ID* (1 octet, adresse de l'esclave)
*   **PDU Modbus** : 
    *   *Function Code* (1 octet) - C'est cet octet que nous cherchons à analyser (ex: 5 = Write Single Coil, 6 = Write Single Register).

---

## 3. Code de Référence : Programme C eBPF (Kernel Space)

Ce programme se charge de lire les paquets, de valider de manière sécurisée les accès mémoire (exigence stricte du vérificateur Linux), et d'isoler les commandes d'écriture industrielle.

```c
#include <uapi/linux/ptrace.h>
#include <net/sock.h>
#include <bcc/proto.h>
#include <linux/ip.h>
#include <linux/tcp.h>

// Structure envoyée au user space lors d'une détection
struct modbus_alert_t {
    u32 src_ip;
    u32 dst_ip;
    u16 src_port;
    u8 function_code;
    u8 unit_id;
};

// Map de type Ring Buffer pour transmettre les alertes
BPF_PERF_OUTPUT(modbus_alerts);

// Compteur global des écritures interceptées
BPF_ARRAY(write_counter, u64, 1);

int monitor_modbus(struct __sk_buff *skb) {
    // 1. Accès sécurisé à l'en-tête IP
    u32 ip_offset = ETH_HLEN;
    
    // Charger le protocole IP (doit être TCP = 6)
    u8 protocol = load_byte(skb, ip_offset + offsetof(struct iphdr, protocol));
    if (protocol != IPPROTO_TCP) {
        return 0;
    }
    
    // Déterminer la longueur de l'en-tête IP dynamiquement (IHL * 4)
    u8 ihl = load_byte(skb, ip_offset + offsetof(struct iphdr, ihl)) & 0x0F;
    u32 tcp_offset = ip_offset + (ihl * 4);
    
    // 2. Accès à l'en-tête TCP
    // Port de destination (Modbus = 502)
    u16 dport = load_half(skb, tcp_offset + offsetof(struct tcphdr, dest));
    if (dport != 502) {
        return 0;
    }
    
    // Déterminer la longueur de l'en-tête TCP (Data Offset * 4)
    u8 data_offset = (load_byte(skb, tcp_offset + offsetof(struct tcphdr, doff)) & 0xF0) >> 4;
    u32 payload_offset = tcp_offset + (data_offset * 4);
    
    // 3. Extraction de l'en-tête MBAP Modbus
    // L'identifiant de l'unité (Unit ID) est à l'offset +6 du MBAP
    u8 unit_id = load_byte(skb, payload_offset + 6);
    
    // Le Function Code est le premier octet du PDU Modbus (offset +7 du MBAP)
    u8 function_code = load_byte(skb, payload_offset + 7);
    
    // 4. Filtrage des écritures critiques sur l'automate
    // 5 = Write Single Coil, 6 = Write Single Register, 15 = Write Multiple Coils, 16 = Write Multiple Registers
    if (function_code == 5 || function_code == 6 || function_code == 15 || function_code == 16) {
        
        // Incrémenter le compteur statistique global
        int index = 0;
        u64 *value = write_counter.lookup(&index);
        if (value) {
            __sync_fetch_and_add(value, 1);
        }
        
        // Remplir et envoyer la structure d'alerte
        struct modbus_alert_t alert = {};
        alert.src_ip = load_word(skb, ip_offset + offsetof(struct iphdr, saddr));
        alert.dst_ip = load_word(skb, ip_offset + offsetof(struct iphdr, daddr));
        alert.src_port = load_half(skb, tcp_offset + offsetof(struct tcphdr, source));
        alert.function_code = function_code;
        alert.unit_id = unit_id;
        
        modbus_alerts.perf_submit(skb, &alert, sizeof(alert));
    }
    
    return 0;
}
```

---

## 4. Code de Référence : Chargeur Python (BCC - User Space)

Ce chargeur compile le code eBPF, l'injecte dans le noyau, et résout les adresses réseaux IP et ports (conversion Network Byte Order).

```python
from bcc import BPF
import socket
import struct

# Initialisation du compilateur BCC à la volée
b = BPF(src_file="modbus_filter.c")

# Attachement au raw socket sur l'interface de rebouclage ou Ethernet industrielle
fn = b.load_func("monitor_modbus", BPF.SOCKET_FILTER)
BPF.attach_raw_socket(fn, "eth0")

def network_to_ip(ip_network_order):
    """Convertit un entier 32-bit réseau en chaîne IP standard."""
    return socket.inet_ntoa(struct.pack("<I", ip_network_order))

def handle_event(cpu, data, size):
    """Callback recevant les données binaires du noyau."""
    # Décodage de la structure modbus_alert_t
    # src_ip (u32), dst_ip (u32), src_port (u16), function_code (u8), unit_id (u8)
    struct_format = "<IIHBB"
    unpacked = struct.unpack(struct_format, data[:struct.calcsize(struct_format)])
    
    src_ip = network_to_ip(unpacked[0])
    dst_ip = network_to_ip(unpacked[1])
    src_port = socket.ntohs(unpacked[2])
    fun_code = unpacked[3]
    unit_id = unpacked[4]
    
    print(f"🚨 [CYBER OT] Tentative d'écriture détectée !")
    print(f"   IP Source : {src_ip}:{src_port} ──► IP Automate : {dst_ip}:502")
    print(f"   Modbus Unit ID : {unit_id} | Code Fonction : {fun_code}")

# Ouvrir la map d'événements et démarrer l'écoute cyclique
b["modbus_alerts"].open_perf_buffer(handle_event)
print("eBPF Industrial Network Analyzer démarré sur 'eth0'...")

while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        # Lire les statistiques globales avant de quitter
        stats = b["write_counter"]
        print(f"\nStatistiques : Nombre d'écritures rejetées/bloquées = {stats[0].value}")
        break
```

---

## 5. XDP (eXpress Data Path) vs Socket Filter

Pour un déploiement de type Cybersécurité, il est crucial de comprendre où attacher le code eBPF selon le besoin :

*   **Socket Filter (Attachement Socket)** : S'exécute après le traitement IP/TCP du noyau Linux. Idéal pour de l'**observation passive** (audit de réseau), car les paquets ne peuvent pas être facilement rejetés par l'appel.
*   **XDP (eXpress Data Path - Attachement Driver)** : S'exécute directement dans le pilote de la carte réseau, avant même l'allocation mémoire système (sk_buff). Idéal pour la **sécurité active**, car le programme eBPF peut renvoyer un code `XDP_DROP` pour rejeter instantanément un paquet d'écriture malveillant en moins d'une microseconde.

---

## 6. Pièges Courants (Common Pitfalls)
*   **Rejet par le Vérificateur (eBPF Verifier)** : Le vérificateur de code eBPF du noyau Linux rejette tout programme contenant des boucles infinies ou des accès mémoire non vérifiés. Toujours borner vos boucles et valider vos offsets avant de lire des données réseau.
*   **Absence de calcul flottant (FPU)** : Le noyau eBPF ne supporte pas les calculs sur nombres flottants (`float` ou `double`). Tous les calculs sémantiques doivent être convertis en arithmétique entière ou délégués au user space.
*   **Débordement d'offset variable** : Tenter d'utiliser des pointeurs réseaux directs sans vérifier que l'adresse calculée est strictement inférieure à `skb->data_end`. Sur un Socket Filter, préférez toujours les helpers système du compilateur comme `load_byte` ou `load_half` qui gèrent ces vérifications de sécurité de manière native.

---

## 7. Liste de vérification (Checklist)
- [ ] Identifier l'interface réseau industrielle cible (ex: `eth0`, `enp0s3`).
- [ ] Valider que le noyau Linux de l'hôte supporte eBPF (version >= 4.18 recommandée).
- [ ] Écrire le code de filtrage C en s'assurant de borner strictement tous les offsets de paquets.
- [ ] Compiler et charger avec BCC en tant que `root` (privilèges d'exécution noyau).
- [ ] Configurer un Ring Buffer ou Map pour le passage des alertes vers l'espace utilisateur.
