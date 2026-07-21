---
name: wireshark
description: Guide complet Wireshark — analyse de paquets, filtres d'affichage et de capture, déchiffrement TLS/SSL, suivi de flux, tshark, GeoIP, extraction de fichiers, et antisèche de filtres.
---

# Wireshark — Analyse de Paquets Réseau

## Présentation

Wireshark est l'analyseur de paquets réseau le plus utilisé au monde.
Open-source, il permet de capturer et d'inspecter le trafic réseau
en temps réel au niveau le plus fin.

**Composants** :
- **Wireshark** (GUI) — Interface graphique d'analyse
- **Tshark** (CLI) — Version ligne de commande
- **Dumpcap** — Capture de paquets
- **Editcap** — Édition de fichiers PCAP
- **Mergecap** — Fusion de captures

---

## Installation

```bash
# Debian / Ubuntu
sudo apt update && sudo apt install wireshark tshark

# Dernière version (PPA Ubuntu)
sudo add-apt-repository ppa:wireshark-dev/stable
sudo apt update && sudo apt install wireshark

# Fedora / CentOS
sudo dnf install wireshark

# macOS
brew install wireshark

# Permissions de capture (Linux)
sudo usermod -aG wireshark $USER
# Déconnexion/reconnexion nécessaire
```

---

## Interface — Les 3 panneaux

1. **Liste des paquets** (haut) — Résumé de chaque paquet
2. **Détails du paquet** (milieu) — Décodage arborescent par couche
3. **Données brutes** (bas) — Hexadécimal + ASCII

---

## Filtres de capture (Capture Filters)

Définis AVANT la capture. Syntaxe BPF (Berkeley Packet Filter).

```bash
# Capturer uniquement le trafic d'une IP
host 192.168.1.100

# Capturer un réseau
net 192.168.1.0/24

# Capturer un port spécifique
port 80
port 443

# Plage de ports
portrange 1-1024

# Protocole
tcp
udp
icmp

# Combinaisons
host 192.168.1.1 and port 80
tcp port 443 and not host 10.0.0.1
(host 192.168.1.1 or host 192.168.1.2) and port 80

# Exclure
not arp and not (udp.port == 53)

# Par adresse MAC
ether host aa:bb:cc:dd:ee:ff
```

---

## Filtres d'affichage (Display Filters)

Appliqués APRÈS la capture. Syntaxe Wireshark.

### Filtres IP
```
ip.addr == 192.168.0.5                # IP source OU destination
ip.src == 192.168.1.1                 # IP source uniquement
ip.dst == 10.0.0.1                    # IP destination uniquement
!(ip.addr == 192.168.0.0/24)          # Exclusion de réseau
ip.src == 192.168.1.0/24              # Réseau source
```

### Filtres par protocole
```
tcp                                   # Tout le trafic TCP
udp                                   # Tout le trafic UDP
http / http2 / http3                  # HTTP
dns                                   # DNS
arp                                   # ARP
icmp                                  # ICMP (ping)
dhcp                                  # DHCP
smb / smb2                            # Partage Windows
tls / ssl                             # TLS/SSL
ssh                                   # SSH
ftp                                   # FTP
telnet                                # Telnet
```

### Filtres par port
```
tcp.port == 80                        # Port TCP 80
udp.port == 53                        # Port UDP 53
tcp.port == 80 || udp.port == 53      # OU
tcp.port >= 1024 and tcp.port <= 2048 # Plage
tcp.dstport == 443                    # Port destination TCP
```

### Filtres HTTP
```
http.request.method == "GET"          # Requêtes GET
http.request.method == "POST"         # Requêtes POST
http.response.code == 200             # Réponses 200
http.response.code >= 400             # Erreurs client/serveur
http.host contains "example"          # Domaine dans l'hôte
http.user_agent contains "Chrome"     # User-Agent spécifique
http.cookie                            # Paquets avec cookies
http.request.uri contains "login"     # URI spécifique
```

### Filtres DNS
```
dns.qry.name == "google.com"          # Requête DNS spécifique
dns.resp.name contains "malware"      # Réponse DNS spécifique
dns.qry.type == 1                     # Type A
dns.qry.type == 28                    # Type AAAA
dns.flags.response == 0               # Requêtes uniquement
dns.flags.response == 1               # Réponses uniquement
dns contains "exfil"                   # Recherche texte
```

### Filtres TCP avancés
```
tcp.flags.syn == 1 and tcp.flags.ack == 0    # Paquets SYN (début connexion)
tcp.flags.reset == 1                          # Paquets RST
tcp.analysis.retransmission                   # Retransmissions
tcp.analysis.duplicate_ack                    # ACK dupliqués
tcp.analysis.lost_segment                     # Segments perdus
tcp.window_size < 1000                        # Fenêtre TCP petite
tcp.len > 0                                   # Paquets avec données
```

### Filtres par adresse MAC
```
eth.addr == aa:bb:cc:dd:ee:ff         # MAC source OU destination
eth.src == aa:bb:cc:dd:ee:ff          # MAC source
eth.dst == ff:ff:ff:ff:ff:ff          # Broadcast
```

### Filtres de recherche textuelle
```
frame contains "password"              # Recherche dans tout le paquet
tcp.payload contains "GET"             # Recherche dans le payload TCP
udp contains "exfil"                   # Recherche dans le payload UDP
http contains "login"                  # Recherche dans HTTP
```

### Combinaisons
```
ip.addr==10.0.0.5 and http             # IP spécifique + HTTP
tcp.port==80 or tcp.port==443          # HTTP ou HTTPS
http and !(ip.addr==192.168.1.0/24)    # HTTP hors réseau local
not arp and not dns and not icmp       # Exclure le bruit
```

---

## Fonctionnalités clés

### Suivre un flux (Follow Stream)
- Clic droit sur un paquet → **Follow** → **TCP Stream** / **HTTP Stream**
- Reconstruit la conversation complète
- Permet de voir tout l'échange client-serveur
- Filtres automatiquement pour ce flux : `tcp.stream eq 0`

### Statistiques
```
Statistics → Summary              # Résumé de la capture
Statistics → Protocol Hierarchy   # Hiérarchie des protocoles
Statistics → Conversations        # Conversations réseau
Statistics → Endpoints            # Hôtes communicants
Statistics → IO Graph             # Graphe de trafic dans le temps
Statistics → HTTP → Requests      # Requêtes HTTP
Statistics → DNS                  # Statistiques DNS
```

### Géolocalisation (GeoIP)
```bash
# Prérequis : bases MaxMind GeoLite2
# Télécharger les bases (gratuites, inscription requise) :
# https://dev.maxmind.com/geoip/geolite2-free-geolocation-data

# Dans Wireshark :
Edit → Preferences → Name Resolution → Geolocation → dossier des bases
```

Une fois activé :
- `Statistics → Endpoints → IPv4` montre pays/ville/ASN
- Filtre `ip.geoip.country == "France"`
- Filtre `ip.geoip.asnum == 12345`

### Déchiffrement TLS/SSL

Prérequis : avoir la clé privée du serveur.

```bash
Edit → Preferences → Protocols → TLS
→ RSA keys list → Add
→ IP: <IP serveur>, Port: 443, Protocol: http
→ Key File: <chemin vers la clé privée>
```

Alternative avec les clés de session (SSLKEYLOGFILE) :
```bash
export SSLKEYLOGFILE=/chemin/sslkeys.log
# Lancer le navigateur depuis ce terminal
# Dans Wireshark : Edit → Preferences → TLS → (Pre)-Master-Secret log filename
```

### Extraction de fichiers
- `File → Export Objects → HTTP` — Extraire fichiers transférés via HTTP
- `File → Export Objects → SMB/SMB2` — Extraire fichiers transférés via SMB

### Génération de règles de pare-feu
- Clic droit sur un paquet → `Tools → Firewall ACL Rules`
- Génère automatiquement des règles pour : iptables, pf, Cisco IOS, etc.

### Résolution de noms
```
Edit → Preferences → Name Resolution
→ Enable Network Name Resolution (attention : génère du trafic DNS)
```

### Coloration
Wireshark colore automatiquement les paquets par défaut :
- **Noir** — Paquets TCP avec erreur (RST)
- **Rouge** — Paquets avec drapeau RST
- **Bleu clair** — DNS
- **Vert** — HTTP
- **Jaune** — Broadcast/multicast

---

## Tshark — Analyse en ligne de commande

### Commandes essentielles
```bash
# Capturer sur une interface
tshark -i eth0

# Capturer avec filtre
tshark -i eth0 -f "port 80"

# Lire un fichier PCAP
tshark -r capture.pcap

# Appliquer un filtre d'affichage
tshark -r capture.pcap -Y "http"

# Afficher des champs spécifiques
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e http.host

# Statistiques
tshark -r capture.pcap -z http,stat,          # Stats HTTP
tshark -r capture.pcap -z conv,tcp            # Conversations TCP
tshark -r capture.pcap -z io,stat,1           # Graphique I/O (1s)
tshark -r capture.pcap -z dns,tree            # Statistiques DNS

# Suivre un flux TCP
tshark -r capture.pcap -z follow,tcp,ascii,0  # Flux TCP 0 en ASCII

# Exporter les objets HTTP
tshark -r capture.pcap --export-objects http,/dossier/sortie

# Filtrer par IP avec affichage des champs
tshark -r capture.pcap -Y "ip.addr==10.0.0.5" -T fields -e frame.time -e ip.src -e ip.dst -e tcp.port
```

---

## Cas d'usage concrets

### Détection de malware / C2
```
# Repérer les beacons (connexions régulières)
Statistics → IO Graph → Filtre : ip.addr == <IP suspecte>

# Rechercher de gros paquets DNS (exfiltration)
dns.qry.name matches "[a-z0-9]{30,}"

# Repérer les domaines suspects
dns.qry.name contains ".xyz" or dns.qry.name contains ".top"

# Connexions vers ports inhabituels
not tcp.port in {80,443,53,22,25}

# Trafic sortant anormal
ip.dst != 192.168.0.0/16 and ip.dst != 10.0.0.0/8
```

### Analyse d'attaque
```
# Détecter un scan de ports
tcp.flags.syn == 1 and tcp.flags.ack == 0 and tcp.window_size <= 1024

# SSH bruteforce
ssh and tcp.flags.reset == 1

# Paquets fragmentés (évasion IDS)
ip.flags.mf == 1
ip.frag_offset > 0
```

### Débogage réseau
```
# Perte de paquets
tcp.analysis.lost_segment
tcp.analysis.retransmission

# Latence élevée
tcp.analysis.ack_rtt > 0.2

# Problèmes DHCP
bootp.option.dhcp == 1
```

---

## Antisèche rapide

```
===========================================================
FILTRES D'AFFICHAGE ESSENTIELS
===========================================================
http                              Tout HTTP
dns                               Tout DNS
tcp.port == 443                   Tout HTTPS/TLS
ip.addr == X.X.X.X                IP spécifique
ip.src == X.X.X.X                 IP source
ip.dst == X.X.X.X                 IP destination
!(arp or dns or icmp)             Exclure le bruit
tcp.flags.syn == 1                Paquets SYN
http.request.method == "GET"      Requêtes GET
http.response.code >= 400         Erreurs HTTP
tcp.analysis.retransmission       Retransmissions
frame contains "password"         Recherche texte
tcp.stream eq 0                   Flux TCP spécifique
===========================================================
```

## Ressources

- **Documentation officielle** : https://www.wireshark.org/docs/
- **Filtres d'affichage** : https://wiki.wireshark.org/DisplayFilters
- **Filtres de capture BPF** : https://wiki.wireshark.org/CaptureFilters
- **Bases MaxMind GeoIP** : https://dev.maxmind.com/geoip/
- **Exemples PCAP** : https://wiki.wireshark.org/SampleCaptures
