---
name: network-diagnostics-troubleshooting
description: Guide complet du diagnostic et troubleshooting réseau — ping, traceroute, mtr, iperf, tcpdump, ss, nmap, tc (traffic control), pathMTU, latence, jitter, perte de paquets, et résolution de pannes.
tags: [troubleshooting, tcpdump, traceroute, mtr, iperf, nmap, ss, tc, network-diagnostics, packet-loss, latency]
---

# Diagnostic et Troubleshooting Réseau

## Présentation

Guide complet des outils et techniques de diagnostic réseau : de la couche physique à l'application, en passant par la détection des goulots d'étranglement, pertes de paquets, latence, et problèmes de routage.

---

## Outils Essentiels

### Stack de Diagnostic

```text
Couche 1-2 (Physique/Liaison)
  ├── ethtool — Vitesse, duplex, statistiques carte
  ├── mii-tool — État liaison
  ├── ip link — État interface
  └── lldpctl — Voisins LLDP/CDP

Couche 3 (Réseau)
  ├── ping — ICMP reachability
  ├── traceroute — Chemin réseau
  ├── mtr — Trace continu
  ├── ip route — Table de routage
  └── nmap — Scan de ports

Couche 4 (Transport)
  ├── ss — Socket statistics
  ├── netstat — (legacy) connexions réseau
  ├── iperf3 — Bandwidth test
  └── tc — Traffic control

Couche 5-7 (Application)
  ├── curl/wget — HTTP tests
  ├── dig/nslookup — DNS
  ├── openssl — TLS handshake
  └── tcpdump/Wireshark — Capture de paquets
```

---

## tcpdump — Capture et Analyse de Paquets

### Commandes Essentielles

```bash
# Capture de base
tcpdump -i eth0 -nn              # Interface + pas de résolution DNS
tcpdump -i eth0 -c 1000          # Limiter à 1000 paquets
tcpdump -i eth0 -s 0 -w capture.pcap  # Capture complète vers fichier

# Filtres par protocole
tcpdump -i eth0 icmp             # Ping uniquement
tcpdump -i eth0 tcp              # TCP uniquement
tcpdump -i eth0 udp              # UDP uniquement
tcpdump -i eth0 arp              # ARP uniquement

# Filtres par IP
tcpdump -i eth0 host 192.168.1.1
tcpdump -i eth0 src 10.0.0.1
tcpdump -i eth0 dst 10.0.0.1
tcpdump -i eth0 net 192.168.1.0/24

# Filtres par port
tcpdump -i eth0 port 22          # SSH
tcpdump -i eth0 port 80 or port 443
tcpdump -i eth0 portrange 1-1024
tcpdump -i eth0 src port 53     # DNS queries sortantes

# Filtres combinés
tcpdump -i eth0 'host 10.0.0.1 and port 80'
tcpdump -i eth0 'not arp and not icmp'
tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'  # SYN packets

# Sortie détaillée
tcpdump -i eth0 -v               # Verbose
tcpdump -i eth0 -vv              # Very verbose
tcpdump -i eth0 -X               # Hex + ASCII
tcpdump -i eth0 -A               # ASCII seulement

# Analyse avancée
tcpdump -i eth0 'tcp[13] & 4 != 0'  # RST packets
tcpdump -i eth0 'tcp[13] & 16 != 0' # ACK
tcpdump -i eth0 'icmp[icmptype] != 8 and icmp[icmptype] != 0'  # ICMP errors

# Seuils de taille
tcpdump -i eth0 'len > 1000'     # Paquets > 1000 bytes
tcpdump -i eth0 'less 64'        # Paquets < 64 bytes (petits)

# Timestamps
tcpdump -i eth0 -tttt            # Human-readable timestamps
tcpdump -i eth0 -ttt             # Delta entre paquets (microsecondes)
```

### Cas Pratiques tcpdump

```bash
# 1. Vérifier si un serveur répond sur un port
tcpdump -i eth0 -nn 'host 10.0.0.50 and port 8080' -c 10

# 2. Détecter des retransmissions TCP
tcpdump -i eth0 -nn 'tcp[tcpflags] & (tcp-syn|tcp-ack) == (tcp-syn|tcp-ack)' 
tcpdump -i eth0 -nn 'tcp[tcpflags] & tcp-syn != 0 and tcp[tcpflags] & tcp-ack == 0'

# 3. Analyser un handshake TCP complet
tcpdump -i eth0 -nn 'host 10.0.0.1 and host 10.0.0.50'
# SYN → SYN-ACK → ACK (3-way handshake)

# 4. DNS troubleshooting
tcpdump -i eth0 -nn port 53 -X

# 5. Détecter du multicast/broadcast storm
tcpdump -i eth0 -nn 'broadcast or multicast' -c 1000

# 6. Suivre une connexion spécifique (port+IP)
tcpdump -i eth0 -nn 'src 10.0.0.1 and dst 10.0.0.50 and port 3306'
```

---

## MTR — Traceroute Amélioré

### Utilisation

```bash
# MTR combine traceroute + ping continu
mtr 8.8.8.8
mtr -n 8.8.8.8              # Pas de résolution DNS
mtr -r -c 100 8.8.8.8      # Rapport (100 ping par hop)
mtr -r -c 10 -n google.com --report  # Rapport rapide
mtr -i 0.5 8.8.8.8         # Intervalle 500ms
mtr -P 443 10.0.0.1        # TCP sur port 443 (au lieu d'ICMP)

# Sortie rapport
mtr -r -c 30 -n 1.1.1.1
```

### Interprétation MTR

```text
                          My traceroute  [v0.95]
Keys: Loss%  Snt   Last   Avg  Best  Wrst  StDev
 1. 192.168.1.1      0.0%   30   0.5   0.6   0.4   1.2   0.2
 2. 10.0.0.1         0.0%   30   1.2   1.5   1.0   3.1   0.4
 3. 203.0.113.1      5.0%   30  15.2  16.1  14.8  22.3   1.5  ← Perte anormale
 4. 198.51.100.1    40.0%   30  18.5  19.2  17.5  25.1   2.0  ← PROBLÈME !
 5. 1.1.1.1          0.0%   30  20.1  21.0  19.5  28.2   2.1
```

### Analyse des Patterns

```text
Pattern 1: Perte à un hop, recovery ensuite
  → Le hop ignore ICMP (rate limiting) — pas un problème réel

Pattern 2: Perte qui s'aggrave et ne récupère pas
  → Problème sur ce lien ou équipement

Pattern 3: Latence qui double soudain
  → Changement de chemin (routage asymétrique)

Pattern 4: Latence croissante régulièrement
  → Congestion, buffer bloat

Pattern 5: Perte intermittente (> 1%)
  → Problème physique (fibre, SFP, câble Ethernet)
```

---

## iperf3 — Tests de Bande Passante

### Tests de Base

```bash
# Serveur
iperf3 -s -p 5201

# Client (test TCP)
iperf3 -c 192.168.1.10 -p 5201 -t 30

# Test UDP (débit + perte + jitter)
iperf3 -c 192.168.1.10 -u -b 1000M -t 30

# Test bidirectionnel simultané
iperf3 -c 192.168.1.10 -d -t 30

# Reverse (server → client)
iperf3 -c 192.168.1.10 -R -t 30

# Test parallèle (multi-flux)
iperf3 -c 192.168.1.10 -P 4 -t 30

# Test avec bande passante spécifique
iperf3 -c 192.168.1.10 -b 100M -t 30

# JSON output (pour scripting)
iperf3 -c 192.168.1.10 -J -t 10
```

### Interprétation iperf3

```bash
# Test TCP (bon)
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-30.00  sec  3.45 GBytes  987 Mbits/sec    → 1Gbps full

# Test UDP avec perte
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total
[  5]   0.00-30.00  sec  1.20 GBytes  343 Mbits/sec   0.124ms  350000/1000000 (35%)

# Test UDP sans perte
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total
[  5]   0.00-30.00  sec  3.50 GBytes  1000 Mbits/sec  0.050ms  0/1000000 (0%)
```

### Script de Benchmark

```bash
#!/bin/bash
# benchmark.sh — Test complet de performance réseau
echo "=== Test TCP ==="
iperf3 -c $1 -t 10 -P 4 | tail -3

echo "=== Test UDP (1Gbps) ==="
iperf3 -c $1 -u -b 1000M -t 10 | tail -5

echo "=== Test UDP (100Mbps) ==="
iperf3 -c $1 -u -b 100M -t 10 | tail -5

echo "=== Latence (ping) ==="
ping -c 30 $1 | tail -1

echo "=== MTR ==="
mtr -r -c 30 -n $1 | tail -20
```

---

## ss — Socket Statistics

### Commandes Essentielles

```bash
# Toutes les connexions TCP
ss -t
ss -tan         # + numériques + listening
ss -tup         # + process
ss -tanp        # Tout: TCP, numérique, all, process

# Statistiques par état
ss -t state established
ss -t state listening
ss -t state time-wait
ss -t state fin-wait-1
ss -t state close-wait
ss -t state syn-recv

# Filtres
ss -t dst 10.0.0.50
ss -t src :80
ss -t 'sport = :22'
ss -t 'dport = :443'
ss -an sport = :80

# Statistiques mémoire
ss -t -m          # Mem info (buffer sizes)
ss -t -i          # TCP info (cwnd, rtt, rto)

# Connexions par adresse locale
ss -t src 10.0.0.1:443

# Temps d'écoute
ss -tlnp 'sport = :80'

# Résumé par état
ss -t | awk '{print $1}' | sort | uniq -c | sort -rn

# IPs les plus connectées
ss -t | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10
```

### Interprétation

```bash
# Trop de TIME_WAIT
ss -t state time-wait | wc -l
# > 10000 → besoin de tcp_tw_reuse

# SYN_RECV élevé (possible SYN flood)
ss -t state syn-recv | wc -l
# > 1000 → possible attaque ou serveur sous-dimensionné

# Half-open connections (CLOSE_WAIT)
ss -t state close-wait | wc -l
# > 0 → bug application (ne ferme pas les sockets)

# Buffer overflow
ss -t -m | grep -c skmem
# Regarder les valeurs rcvbuf/sndbuf
```

---

## tc — Traffic Control

### Visualisation des Files d'Attente

```bash
# Voir les qdiscs
tc -s qdisc show dev eth0
tc -s qdisc show dev eth0 | grep -A5 "qdisc pfifo"

# Statistiques détaillées
tc -s qdisc show dev eth0

# Exemple de sortie
qdisc pfifo_fast 0: root bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
 Sent 472537624 bytes 456789 pkt (dropped 0, overlimits 0 requeues 0)
 backlog 0b 0p requeues 0
```

### Détection de Bufferbloat

```bash
# Bufferbloat = latence élevée sous charge
# 1. Mesurer la latence de base
ping -c 10 8.8.8.8 | tail -1

# 2. Mettre le lien sous charge
iperf3 -c 192.168.1.10 -t 30 &
sleep 5

# 3. Mesurer la latence pendant la charge
ping -c 10 8.8.8.8 | tail -1

# Si la latence passe de 5ms à 500ms → bufferbloat détecté !
# Solution : fq_codel ou cake
tc qdisc replace dev eth0 root fq_codel
tc qdisc replace dev eth0 root cake bandwidth 100mbit
```

### Simulation de Pannes (pour tests)

```bash
# Ajouter de la latence (100ms)
tc qdisc add dev eth0 root netem delay 100ms

# Ajouter de la perte (5%)
tc qdisc add dev eth0 root netem loss 5%

# Ajouter les deux
tc qdisc add dev eth0 root netem delay 100ms 10ms loss 5% 25%

# Limiter la bande passante (pour simuler un lien lent)
tc qdisc add dev eth0 root tbf rate 1mbit burst 32kbit limit 10000

# Corruption de paquets
tc qdisc add dev eth0 root netem corrupt 2%

# Duplication
tc qdisc add dev eth0 root netem duplicate 1%

# Reorder
tc qdisc add dev eth0 root netem delay 10ms reorder 25% 50%

# Supprimer les simulations
tc qdisc del dev eth0 root
```

---

## nmap — Scan de Réseau et Découverte

### Commandes de Diagnostic

```bash
# Découverte d'hôtes sur le réseau
nmap -sn 192.168.1.0/24

# Scan de ports rapide
nmap -F 192.168.1.1

# Scan de services
nmap -sV 192.168.1.1

# OS detection
nmap -O 192.168.1.1

# Scan complet (tous ports)
nmap -p- 192.168.1.1

# Détection de firewall
nmap -sA 192.168.1.1  # ACK scan (détecte etat filtré/non filtré)

# Scan UDP
nmap -sU -p 53,67,68,123,161 192.168.1.1

# Détection de scripts vulnérabilités
nmap --script vuln 192.168.1.1

# Traceroute intégré
nmap --traceroute 8.8.8.8

# Sortie pour analyse
nmap -oX scan.xml 192.168.1.0/24  # XML
nmap -oN scan.txt 192.168.1.0/24  # Normal
```

---

## Path MTU Discovery

### Test de Path MTU

```bash
# Tester MTU progressivement
ping -M do -s 1472 8.8.8.8  # 1500 - 28 (IP+ICMP header)
ping -M do -s 1400 8.8.8.8
ping -M do -s 1300 8.8.8.8
ping -M do -s 1200 8.8.8.8

# Détection de fragmentation
tcpdump -i eth0 -nn 'icmp[icmptype] == 3 and icmp[icmpcode] == 4'
# "Fragmentation needed but DF set" → MTU trop grand

# Définir MSS sur les connexions
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN \
  -j TCPMSS --set-mss 1400

# Afficher le MTU des interfaces
ip link show | grep mtu

# Changer le MTU
ip link set dev eth0 mtu 9000
```

---

## Résolution de Pannes — Checklist

### Panne Réseau

```text
1. Vérifier la couche physique
   ├── ethtool eth0 → Speed/Duplex/Link detected
   ├── ip link show → UP/DOWN/state
   └── cable test / SFP diagnostics

2. Vérifier la couche IP
   ├── ip addr show → Adresse IP configurée
   ├── ip route show → Route par défaut
   ├── ping 127.0.0.1 → Loopback OK
   ├── ping <gateway> → Gateway reachable
   └── ping 8.8.8.8 → Internet OK

3. Vérifier la résolution DNS
   ├── dig @1.1.1.1 example.com
   ├── nslookup example.com
   └── host example.com

4. Vérifier les connexions applicatives
   ├── ss -tlnp → Services en écoute
   ├── nmap -p 80 localhost → Port local OK
   ├── curl -I http://example.com → HTTP OK
   └── openssl s_client -connect example.com:443 → TLS OK

5. Vérifier le chemin
   ├── mtr -r -c 30 8.8.8.8
   └── traceroute -n 8.8.8.8
```

### Panne Performance

```text
1. Identifier le goulot
   ├── iperf3 → Bande passante disponible
   ├── ping → Latence base
   ├── ping + iperf3 → Bufferbloat
   └── ss -ti → TCP RTT, cwnd, ssthresh

2. Vérifier la congestion
   ├── tc -s qdisc → Drops, overlimits
   ├── ss -t state time-wait → Connexions TIME_WAIT
   └── netstat -s → TCP retransmits, out-of-order

3. Vérifier le matériel
   ├── ethtool -S eth0 → Interface errors, CRC
   ├── ifconfig eth0 → RX errors, dropped
   └── dmesg | tail → Kernel network errors
```

---

## Pièges et Bonnes Pratiques

- **tcpdump** : Toujours utiliser `-nn` pour éviter la résolution DNS qui ralentit et peut planter
- **MTR** : Laisser tourner 30+ secondes pour un diagnostic fiable
- **iperf3** : Utiliser -P 4 (parallel streams) pour saturer les liens modernes
- **MTU** : Vérifier le MTU de bout en bout, surtout avec VXLAN (50 octets d'overhead)
- **Bufferbloat** : Cause majeure de latence, remplacer pfifo par fq_codel ou cake
- **SYN Flood** : Ne pas confondre avec un vrai pic de trafic
- **Logs** : Toujours logguer les diagnostics pour analyse comparative
- **Monitoring** : Mettre en place Prometheus + blackbox_exporter pour des métriques continues

## Ressources

- tcpdump man : https://www.tcpdump.org/manpages/tcpdump.1.html
- iperf3 : https://iperf.fr/
- MTR : https://www.bitwizard.nl/mtr/
- Bufferbloat : https://www.bufferbloat.net/
- nmap : https://nmap.org/docs.html
- ss man : https://man7.org/linux/man-pages/man8/ss.8.html