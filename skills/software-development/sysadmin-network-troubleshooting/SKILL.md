---
name: sysadmin-network-troubleshooting
description: "Diagnostic réseau Linux avancé : tcpdump, Wireshark/tshark, ss, iproute2, tc (traffic control), nmap, mtr, iperf3, ethtool, conntrack, ARP, MTU path discovery et résolution de pannes."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [network, tcpdump, wireshark, tshark, ss, iproute2, tc, nmap, mtr, iperf3, ethtool, conntrack, troubleshooting, latency]
    related_skills: [os-linux-admin, sysadmin-kernel-tuning, sysadmin-monitoring, network-diagnostics-troubleshooting]
---

# Diagnostic Réseau Linux Avancé

## Vue d'ensemble

Le diagnostic réseau est une compétence essentielle pour tout administrateur système. Ce skill couvre la boîte à outils complète : de l'analyse de paquets avec tcpdump à la mesure de bande passante avec iperf3, en passant par la configuration avancée via iproute2 et le traffic control (tc).

## Principes de Base du Diagnostic

**Méthodologie OSI : Toujours commencer par la couche la plus basse.**

| Étape | Commande | Couche OSI |
|-------|----------|-----------|
| 1. Interface physique | `ethtool`, `ip link` | 1 (Physique) |
| 2. Connexion L2 | `ip neigh`, `arping`, `bridge` | 2 (Liaison) |
| 3. Connectivité IP | `ping`, `mtr` | 3 (Réseau) |
| 4. Routage | `ip route get`, `traceroute` | 3 (Réseau) |
| 5. Port/Service | `ss`, `nmap` | 4 (Transport) |
| 6. DNS | `dig`, `nslookup` | 7 (Application) |
| 7. Application | `curl -v`, `openssl s_client` | 7 (Application) |

## Quand l'utiliser

- Un service est inaccessible ou lent
- Des paquets sont perdus (latence anormale, timeouts)
- Besoin de capturer le traffic pour analyse forensique
- Configurer QoS, shaping ou limitation de bande passante
- Diagnostiquer des problèmes MTU/fragmentation
- Vérifier les connexions actives et les ports ouverts

## 1. iproute2 (Suite de Commandes Moderne)

### ip (remplace ifconfig, route, arp)

```bash
# Interfaces
ip link show                        # toutes les interfaces
ip link set eth0 up/down            # activer/désactiver
ip addr show eth0                   # adresses IP
ip addr add 192.168.1.10/24 dev eth0   # ajouter IP
ip addr del 192.168.1.10/24 dev eth0   # supprimer IP

# Routage
ip route show                       # table de routage
ip route get 8.8.8.8               # route empruntée vers une destination
ip route add default via 192.168.1.1 dev eth0  # ajouter route par défaut
ip route del 10.0.0.0/8            # supprimer une route

# ARP / Neighbors
ip neigh show                       # table ARP
ip neigh del 192.168.1.1 dev eth0  # supprimer une entrée ARP

# VRF / Network Namespaces
ip netns add blue                   # créer un namespace réseau
ip netns exec blue ip addr          # exécuter dans le namespace
```

### ss (remplace netstat)

```bash
# Toutes les sockets d'écoute
ss -tulpn                           # -t TCP, -u UDP, -l listening, -p process, -n numeric

# Connexions établies vers un port spécifique
ss -tanp 'sport = :80 or dport = :80'

# Connexions dans un état spécifique
ss -tan state time-wait
ss -tan state established

# Statistiques réseau compactes
ss -s                               # résumé (total TCP, UDP, etc.)

# Voir les sockets UNIX
ss -lx                              # sockets UNIX locales
```

## 2. Tcpdump — Capture de Paquets

### Syntaxes Essentielles

```bash
# Capture de base (interface, nombre de paquets)
sudo tcpdump -i eth0 -c 100        # 100 paquets
sudo tcpdump -i eth0 -n            # pas de résolution DNS
sudo tcpdump -i any                # toutes les interfaces

# Filtres
sudo tcpdump -i eth0 host 192.168.1.100           # traffic vers/depuis une IP
sudo tcpdump -i eth0 src 10.0.0.1                 # source IP
sudo tcpdump -i eth0 dst 10.0.0.1                 # destination IP
sudo tcpdump -i eth0 port 80                       # port 80
sudo tcpdump -i eth0 portrange 8000-9000           # range de ports
sudo tcpdump -i eth0 tcp                           # TCP uniquement
sudo tcpdump -i eth0 udp                           # UDP uniquement
sudo tcpdump -i eth0 icmp                          # ICMP (ping)

# Combinaisons
sudo tcpdump -i eth0 'tcp and port 443'                         # HTTPS
sudo tcpdump -i eth0 'host 10.0.0.1 and not port 22'            # sauf SSH
sudo tcpdump -i eth0 'tcp[tcpflags] & (tcp-syn) != 0'           # SYN flags

# Sauvegarder dans un fichier
sudo tcpdump -i eth0 -w capture.pcap -C 100 -W 5   # rotation 100MB x 5
# -C: taille max par fichier (Mo)
# -W: nombre de fichiers max

# Lire un fichier de capture
tcpdump -r capture.pcap -n
tcpdump -r capture.pcap -X             # hex + ASCII
tcpdump -r capture.pcap -A             # ASCII seulement
```

### Scénarios Typiques

```bash
# Voir tout le traffic HTTP (requêtes GET)
sudo tcpdump -i any -A 'tcp port 80 and (tcp[((tcp[12:1] & 0xf0) >> 2):4] = 0x47455420)'  # "GET "

# Diagnostiquer des retransmissions TCP
sudo tcpdump -i any 'tcp[tcpflags] & (tcp-retrans) != 0'

# Mesurer le temps de réponse DNS
sudo tcpdump -i any udp port 53 -c 50

# Capturer uniquement les SYN-ACK
sudo tcpdump -i any 'tcp[13] & 18 == 18'
```

## 3. Tshark (Wireshark CLI)

```bash
# Capture en direct avec affichage lisible
sudo tshark -i eth0

# Filtre d'affichage (plus puissant que BPF)
sudo tshark -i eth0 -Y "http.request.method == GET"
sudo tshark -i eth0 -Y "tcp.analysis.flags"

# Statistiques
sudo tshark -i eth0 -z io,phs          # Protocol Hierarchy Statistics
sudo tshark -r capture.pcap -z conv,tcp  # Conversations TCP

# Exporter des objets HTTP
tshark -r capture.pcap --export-objects http,/tmp/extracted/

# Suivre un flux TCP complet
tshark -r capture.pcap -z follow,tcp,ascii,0
```

## 4. Mesure de Performance Réseau

```bash
# iperf3 (test bande passante)
# Serveur (sur la machine réceptrice) :
iperf3 -s -p 5201

# Client (émetteur) :
iperf3 -c 192.168.1.100 -p 5201 -t 30 -P 4   # 4 flux parallèles, 30s
iperf3 -c 192.168.1.100 -u -b 100M             # UDP, 100 Mbps

# Reverse mode (mesurer le download)
iperf3 -c 192.168.1.100 -R

# Résultat typique :
# [ ID] Interval           Transfer     Bitrate         Retr
# [  5]   0.00-30.00  sec  3.46 GBytes  991 Mbits/sec    0    sender
# [  5]   0.00-30.00  sec  3.46 GBytes  990 Mbits/sec          receiver
# Retr=0 → pas de retransmission, lien sain
```

```bash
# mtr (traceroute continu avec statistiques)
mtr -r -c 100 8.8.8.8                # rapport après 100 probes
mtr -r -c 100 --report-wide 8.8.8.8  # largeur max
mtr -n google.com                    # pas de DNS

# Résultat : % Loss par hop → identifier le maillon faible
```

## 5. Configuration Avancée

### Traffic Control (tc) — QoS, Shaping, Limitation

```bash
# Limiter la bande passante sortante à 10 Mbps
tc qdisc add dev eth0 root tbf rate 10mbit burst 32kbit latency 400ms

# Ajouter de la latence (simulation réseau)
tc qdisc add dev eth0 root netem delay 100ms 20ms   # latence 100ms ± 20ms

# Simuler de la perte de paquets
tc qdisc add dev eth0 root netem loss 5%

# Voir les qdiscs configurés
tc qdisc show dev eth0

# Supprimer toutes les configurations
tc qdisc del dev eth0 root
```

### Ethtool (Informations et Configuration Interface)

```bash
# Informations de base
ethtool eth0                   # speed, duplex, auto-negociation
ethtool -i eth0                # driver et firmware
ethtool -S eth0                # statistiques détaillées (paquets TX/RX, drops)

# Vérifier les erreurs (important !)
ethtool -S eth0 | grep -E "error|drop|crc|miss"
# CRC errors → mauvais câble ou interface
# drops → buffer overflow (augmenter rx/tx ring buffer)

# Configurer le ring buffer
ethtool -g eth0                # voir la configuration actuelle
ethtool -G eth0 rx 4096 tx 4096  # augmenter les buffers

# Désactiver la segmentation offloading (pour capture)
ethtool -K eth0 tso off gso off gro off lro off
```

## 6. Conntrack (Connection Tracking)

```bash
# Voir les connexions actives suivies par le noyau
sudo conntrack -L                      # toutes les connexions
sudo conntrack -L -p tcp --dport 80   # connexions HTTP

# Statistiques
sudo conntrack -S                      # count, max, found, invalid

# Nombre max de connexions simultanées
sysctl net.netfilter.nf_conntrack_max
# Si les logs montrent "nf_conntrack: table full, dropping packet"
sysctl -w net.netfilter.nf_conntrack_max=524288
```

## 7. Résolution MTU et Fragmentation

```bash
# Découverte du MTU du chemin (Path MTU Discovery)
# 1. Tester des pings avec différents MTU
ping -M do -s 1472 8.8.8.8    # ICMP avec MTU=1500 (1472 + 28 header)
ping -M do -s 1400 8.8.8.8    # ICMP avec MTU=1428

# Si le ping échoue avec "Message too long", le path a un MTU plus petit
# Réduire jusqu'à trouver le MTU max

# Voir le MTU sur l'interface
ip link show eth0 | grep mtu

# Changer le MTU
sudo ip link set dev eth0 mtu 9000  # Jumbo frames

# Tester le débit avec différents MTU
iperf3 -c serveur -M 1500
iperf3 -c serveur -M 9000
```

## 8. Script de Diagnostic Rapide

```bash
#!/usr/bin/env bash
# /usr/local/bin/net-diag.sh
set -euo pipefail

TARGET="${1:-8.8.8.8}"

echo "=== 1. INTERFACE ==="
ip -br addr show | grep UP

echo -e "\n=== 2. ROUTE ==="
ip route get "$TARGET"

echo -e "\n=== 3. PING ==="
ping -c 4 -W 2 "$TARGET" | tail -1

echo -e "\n=== 4. PORTS OUVERTS ==="
ss -tulpn | head -20

echo -e "\n=== 5. CONNEXIONS ÉTABLIES ==="
ss -tan state established | wc -l
echo "connexions actives"

echo -e "\n=== 6. DNS ==="
dig +short "$TARGET" 2>/dev/null || host "$TARGET" 2>/dev/null || nslookup "$TARGET"

echo -e "\n=== 7. MTR (10 probes) ==="
mtr -r -c 10 "$TARGET"

echo -e "\n=== 8. ERREURS INTERFACE ==="
for iface in $(ip -br link show | awk '{print $1}' | grep -v lo); do
    errors=$(ethtool -S "$iface" 2>/dev/null | grep -E "error|drop|crc|miss" | grep -v ": 0" || true)
    if [ -n "$errors" ]; then
        echo "--- $iface ---"
        echo "$errors"
    fi
done

echo -e "\n=== 9. STATUT CONNTRACK ==="
sudo conntrack -S 2>/dev/null || echo "conntrack non disponible"
```

## Pièges Courants

1. **Oublier `-n` sur tcpdump** : Sans `-n`, tcpdump fait des résolutions DNS pour chaque paquet, ralentissant la capture et pouvant causer des délais.

2. **Buffer overflow tcpdump** : Sur un lien 10 Gbps, tcpdump peut perdre des paquets. Utiliser `tcpdump -B 4096` (buffer 4 Mo).

3. **Offloading qui cache les paquets** : TSO/GRO/gso déplacent la segmentation vers le NIC. Les paquets capturés par tcpdump peuvent être plus gros que ce qui est réellement transmis. Désactiver avec `ethtool -K`.

4. **MTU path incohérent** : Un routeur intermédiaire avec MTU plus petit provoque des timeouts silencieux pour les connexions TCP (PMTUD). Symptôme : ping OK mais connexions TCP bloquées.

5. **Firewall qui drop ICMP** : Si les administrateurs réseau bloquent ICMP "Destination Unreachable (Fragmentation Needed)", Path MTU Discovery ne fonctionne pas → connexions TCP bloquées.

## Liste de vérification (Checklist)

- [ ] Vérification couche 1 : câble, lien `ethtool eth0` (Speed, Duplex, Link detected)
- [ ] Vérification couche 2 : `ip neigh show` (ARP résolu ?)
- [ ] Vérification couche 3 : `ping` (latence, perte)
- [ ] Vérification couche 4 : `ss -tulpn` (ports en écoute)
- [ ] Vérification DNS : `dig +trace` (résolution complète)
- [ ] Vérification route : `ip route get <dest>` (bonne interface ?)
- [ ] Performance : `iperf3` (bande passante réelle)
- [ ] Qualité : `mtr` (perte par hop)
- [ ] Conntrack : `conntrack -S` (table pas pleine)
- [ ] MTU : `ping -M do -s 1472` (PMTUD fonctionnel)
