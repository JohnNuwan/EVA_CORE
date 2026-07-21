---
name: network-security-firewall-ids
description: Guide complet de la sécurité réseau — ACLs, pare-feux (iptables, nftables, pfSense), IDS/IPS (Snort, Suricata), Zero Trust Network Architecture (ZTNA), segmentation, et micro-segmentation.
tags: [firewall, iptables, nftables, snort, suricata, zero-trust, idps, micro-segmentation, acl, pfSense]
---

# Sécurité Réseau — ACLs, Firewall, IDS/IPS, Zero Trust

## Présentation

Guide complet des technologies de sécurité réseau : filtrage par paquets, inspection profonde, détection d'intrusion, architecture Zero Trust, segmentation, et micro-segmentation. Couvre la défense en profondeur du périmètre au workload.

---

## ACLs — Access Control Lists

### ACLs Standards vs Étendues

```text
Standard ACL (1-99, 1300-1999)
  └── Filtre sur IP source uniquement
  └── Placer au plus près de la destination

Extended ACL (100-199, 2000-2699)
  └── Filtre sur IP src + dst + port + protocole
  └── Placer au plus près de la source
```

### Configuration Cisco ACL

```bash
# ACL Standard
access-list 10 permit 10.0.1.0 0.0.0.255
access-list 10 deny any

# Appliquer sur interface
interface GigabitEthernet0/0
  ip access-group 10 out

# ACL Étendue
access-list 110 permit tcp 10.0.1.0 0.0.0.255 host 10.0.2.100 eq www
access-list 110 permit udp any any eq domain
access-list 110 deny ip any any log

# ACL réflexive (stateful)
ip access-list extended INBOUND
  permit tcp any host 10.0.1.100 established
  permit udp any eq domain any
  deny ip any any log

ip access-list extended OUTBOUND-FILTER
  dynamic OUTBOUND-DYNAMIC permit tcp any any

# Object Groups — ACL moderne
object-group network SERVERS
  host 10.0.2.100
  host 10.0.2.101
  10.0.2.0/24

object-group service WEB_SERVICES
  tcp eq www
  tcp eq https

ip access-list extended MODERN_ACL
  permit tcp 10.0.1.0/24 object-group SERVERS object-group WEB_SERVICES
  deny ip any any log
```

### ACLs Juniper (filter)

```bash
set firewall family inet filter PROTECT-V4 term ALLOW-SSH from source-address 10.0.0.0/24
set firewall family inet filter PROTECT-V4 term ALLOW-SSH from protocol tcp
set firewall family inet filter PROTECT-V4 term ALLOW-SSH from destination-port ssh
set firewall family inet filter PROTECT-V4 term ALLOW-SSH then accept
set firewall family inet filter PROTECT-V4 term DENY-ALL then discard
set interfaces lo0 unit 0 family inet filter input PROTECT-V4
```

---

## Pare-Feux Linux : iptables / nftables

### iptables — Chaînes et Tables

```text
Tables :
  filter : FORWARD, INPUT, OUTPUT (filtrage)
  nat    : PREROUTING, POSTROUTING, OUTPUT (NAT)
  mangle : PREROUTING, INPUT, FORWARD, OUTPUT, POSTROUTING (modification TOS/MSS)
  raw    : PREROUTING, OUTPUT (conntrack bypass)
  security: FORWARD, INPUT, OUTPUT (SELinux)
```

### iptables — Configuration Complète

```bash
# Politique par défaut : tout bloquer
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Autoriser loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Connexions établies
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# SSH depuis réseau admin
iptables -A INPUT -s 10.0.0.0/24 -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT

# Services exposés
iptables -A INPUT -p tcp -m multiport --dports 80,443 -m conntrack --ctstate NEW -j ACCEPT
iptables -A INPUT -p udp --dport 53 -m conntrack --ctstate NEW -j ACCEPT
iptables -A INPUT -p tcp --dport 53 -m conntrack --ctstate NEW -j ACCEPT

# Forwarding VLAN → VLAN
iptables -A FORWARD -i vlan10 -o vlan20 -p tcp --dport 80 -j ACCEPT
iptables -A FORWARD -i vlan20 -o vlan10 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Rate limiting (anti-DoS)
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW \
  -m recent --set --name HTTP
iptables -A INPUT -p tcp --dport 80 -m conntrack --ctstate NEW \
  -m recent --update --seconds 10 --hitcount 20 --name HTTP -j DROP

# Protection SYN flood
iptables -A INPUT -p tcp --syn -m limit --limit 100/s --limit-burst 200 -j ACCEPT
iptables -A INPUT -p tcp --syn -j DROP

# Logging pour debugging
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "FW DROP: "
```

### nftables — Successeur Moderne

```bash
# /etc/nftables.conf
#!/usr/sbin/nft -f
table inet filter {
  chain input {
    type filter hook input priority 0; policy drop;
    
    # Loopback
    iif lo accept
    ct state established,related accept
    
    # SSH depuis admin
    ip saddr 10.0.0.0/24 tcp dport 22 accept
    
    # HTTP/HTTPS
    tcp dport {80, 443} accept
    
    # ICMP limité
    ip protocol icmp icmp type {echo-request} limit rate 10/second accept
    
    # Log drops
    log prefix "nft-drop: " limit rate 5/minute
    
    counter drop
  }
  
  chain forward {
    type filter hook forward priority 0; policy drop;
    
    ct state established,related accept
    
    # Forward VLAN 10 → 20 (HTTP only)
    iif "vlan10" oif "vlan20" tcp dport 80 accept
    
    counter drop
  }
  
  chain output {
    type filter hook output priority 0; policy accept;
  }
}

# NAT (table dédiée)
table ip nat {
  chain prerouting {
    type nat hook prerouting priority -100;
    tcp dport {80, 443} redirect to :8080
  }
  
  chain postrouting {
    type nat hook postrouting priority 100;
    oif "eth0" masquerade
  }
}
```

---

## pfSense / OPNsense — Pare-Feu Open Source

### Installation et Configuration

```bash
# Installation ISO
# Télécharger : https://www.pfsense.org/download/
# Installer sur VM/bare metal (minimum 2 interfaces)

# Configuration initiale via console
Option 1: Assign Interfaces
  WAN = vtnet0 (DHCP)
  LAN = vtnet1 (192.168.1.1/24)
  OPT1 = vtnet2 (DMZ: 10.0.0.1/24)

# Accès Web : https://192.168.1.1
# User: admin / Password: pfsense
```

### Règles pfSense

```text
WAN Rules:
  ┌───┬──────────┬──────┬──────────┬──────────────┬─────────────┬─────────┐
  │ # │ Protocol │ Src  │ Src Port │ Dest         │ Dest Port   │ Gateway │
  ├───┼──────────┼──────┼──────────┼──────────────┼─────────────┼─────────┤
  │ 1 │ TCP      │ *    │ *        │ WAN Address  │ 443 (HTTPS) │ *       │
  │ 2 │ UDP      │ *    │ *        │ WAN Address  │ 1194 (OVPN) │ *       │
  └───┴──────────┴──────┴──────────┴──────────────┴─────────────┴─────────┘

LAN Rules:
  ┌───┬──────────┬────────────┬──────────┬──────┬─────────────┬─────────┐
  │ # │ Protocol │ Src        │ Port     │ Dest │ Dest Port   │ Gateway │
  ├───┼──────────┼────────────┼──────────┼──────┼─────────────┼─────────┤
  │ 1 │ *        │ LAN Net    │ *        │ *    │ *           │ *       │
  │ 2 │ TCP      │ LAN Net    │ *        │ DMZ  │ 443         │ *       │
  └───┴──────────┴────────────┴──────────┴──────┴─────────────┴─────────┘

DMZ Rules:
  ┌───┬──────────┬──────┬──────────┬──────────────┬─────────────┬─────────┐
  │ # │ Protocol │ Src  │ Port     │ Dest         │ Dest Port   │ Gateway │
  ├───┼──────────┼──────┼──────────┼──────────────┼─────────────┼─────────┤
  │ 1 │ TCP      │ *    │ *        │ DMZ Address  │ 80,443      │ *       │
  └───┴──────────┴──────┴──────────┴──────────────┴─────────────┴─────────┘
```

### Configuration pfSense avancée

```bash
# HA (CARP) sur deux pfSense
# Interfaces synchronisées en pfsync

# VLAN Configuration
vtnet1 → VLAN 10 (Admin: 192.168.10.1/24)
         VLAN 20 (Users: 192.168.20.1/24)
         VLAN 30 (VoIP: 192.168.30.1/24)

# Traffic Shaper pour QoS
# Firewall → Traffic Shaper
# Limiter le P2P, prioritiser VoIP

# Captive Portal pour WiFi guest
# Services → Captive Portal
```

---

## IDS/IPS — Snort & Suricata

### Suricata — IDS/IPS Haute Performance

```bash
# Installation
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt-get update && sudo apt-get install suricata

# Configuration
# /etc/suricata/suricata.yaml
vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16,10.0.0.0/8]"
    EXTERNAL_NET: "!$HOME_NET"
    HTTP_SERVERS: "$HOME_NET"
    SMTP_SERVERS: "$HOME_NET"
    DNS_SERVERS: "any"

af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

app-layer:
  protocols:
    http:
      enabled: yes
      libhtp:
        default-config:
          request-body-limit: 4096
          response-body-limit: 4096
    tls:
      enabled: yes
      ja3-fingerprints: yes

# Activer IPS mode (inline)
# /etc/default/suricata
LISTENMODE=af-packet
```

### Règles Suricata / Snort

```bash
# Installer Emerging Threats Open
sudo suricata-update
sudo suricata-update enable-source oisf/trafficid
sudo suricata-update enable-source et/open
sudo suricata-update update-source

# Lister les règles
suricata-update list-sources
```

```bash
# Règles personnalisées /etc/suricata/rules/local.rules

# ICMP Flood detection
alert icmp $EXTERNAL_NET any -> $HOME_NET any \
  (msg:"ICMP Flood detected"; \
   threshold:type threshold, track by_src, count 100, seconds 10; \
   classtype:attempted-dos; sid:1000001; rev:1;)

# SSH Bruteforce
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 \
  (msg:"SSH Bruteforce Attempt"; \
   flags:S; \
   detection_filter:track by_src, count 10, seconds 5; \
   classtype:attempted-user; sid:1000002; rev:1;)

# DNS Tunneling detection
alert udp $HOME_NET any -> any 53 \
  (msg:"DNS Query Over Length - Possible Tunneling"; \
   dns_query; content:"|01|"; offset:2; depth:1; \
   dns_query_len:>50; \
   classtype:protocol-command-decode; sid:1000003; rev:1;)

# Drive-by download
alert http $EXTERNAL_NET any -> $HOME_NET any \
  (msg:"Drive-by download - Suspicious File Download"; \
   flow:established,to_client; \
   fileext:"exe"; fileext:"scr"; fileext:"jar"; \
   classtype:trojan-activity; sid:1000004; rev:1;)

# SQL Injection
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS \
  (msg:"SQL Injection Attempt - UNION"; \
   flow:to_server,established; \
   http_uri; content:"UNION"; nocase; \
   content:"SELECT"; nocase; distance:0; \
   classtype:web-application-attack; sid:1000005; rev:1;)

# Crypto miner detection
alert tcp $HOME_NET any -> $EXTERNAL_NET 3333 \
  (msg:"Crypto Miner - Stratum Protocol"; \
   flow:to_server; \
   content:"|01|mining"; depth:100; \
   classtype:policy-violation; sid:1000006; rev:1;)
```

### Mode IPS avec Suricata (nfqueue)

```bash
# Mode IPS (inline blocking via nfqueue)
# /etc/suricata/suricata.yaml
af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes
    mode: inline
    copy-iface: eth1

# Ou utiliser nfqueue
iptables -I FORWARD -j NFQUEUE --queue-num 0
suricata -c /etc/suricata/suricata.yaml -q 0
```

### Analyse des Logs Suricata

```bash
# Logs JSON (eve.json)
jq 'select(.alert != null) | .timestamp, .alert.signature, .src_ip, .dest_ip' \
  /var/log/suricata/eve.json

# Statistiques
suricata -i eth0 --stats

# Stats via eve.stats
jq 'select(.event_type == "stats") | .stats.decoder.ipv4' \
  /var/log/suricata/eve.json
```

---

## Zero Trust Network Architecture (ZTNA)

### Principes ZTNA

```text
1. NE JAMAIS FAIRE CONFIANCE, TOUJOURS VÉRIFIER
   └── Aucune entité n'est fiée par défaut
   └── Authentification + autorisation à chaque accès

2. MICRO-SEGMENTATION
   └── Segmentation au niveau du workload
   └── Politiques allow-list (tout interdit sauf exceptions)

3. ACCÈS LEAST-PRIVILEGE
   └── Accès minimum nécessaire
   └── Just-in-time et just-enough

4. CONTINUOUS VERIFICATION
   └── Vérification permanente de l'état de sécurité
   └── Revocation immédiate des accès compromis
```

### Implémentation ZTNA (CloudFlare / Tailscale / Wireguard)

```bash
# Tailscale — Mesh VPN Zero Trust
# Installation
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --auth-key tskey-xxx

# ACLs Tailscale (tailnet policy)
cat > /tmp/acl.json << 'EOF'
{
  "acls": [
    // Développeurs → SSH uniquement vers dev-servers
    {"action": "accept", "src": ["tag:dev"], "dst": ["tag:dev-server:22"]},
    // Admin → tous les serveurs
    {"action": "accept", "src": ["tag:admin"], "dst": ["*:*"]},
    // CI/CD → API seulement
    {"action": "accept", "src": ["tag:ci"], "dst": ["tag:api-server:443"]},
  ],
  "groups": {
    "group:dev":    ["alice@example.com", "bob@example.com"],
    "group:admin":  ["ops@example.com"],
  },
  "tagOwners": {
    "tag:dev-server":  ["group:admin"],
    "tag:api-server":  ["group:admin"],
    "tag:ci":          ["group:admin"],
  }
}
EOF
sudo tailscale configure --json-file /tmp/acl.json

# Cloudflare Zero Trust (tunnel)
cloudflared tunnel create my-tunnel
cloudflared tunnel route dns my-tunnel app.example.com
```

### WireGuard + Zero Trust

```bash
# /etc/wireguard/ztna.conf
[Interface]
PrivateKey = <server-privkey>
Address = 10.100.0.1/24
ListenPort = 51820
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -A FORWARD -o %i -j ACCEPT
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -D FORWARD -o %i -j ACCEPT

# Chaque client → ACL spécifique
[Peer]
# Client Dev1 — Accès SSH uniquement
PublicKey = <dev1-pubkey>
AllowedIPs = 10.100.0.10/32
# nftables: only SSH allowed for this IP
# nft add rule inet filter forward ip saddr 10.100.0.10 tcp dport 22 accept

[Peer]
# Client API Server
PublicKey = <api-pubkey>
AllowedIPs = 10.100.0.20/32
# nftables: only port 443 for this IP
```

---

## Micro-segmentation (VMware NSX / OVS)

```bash
# OVS - Micro-segmentation par flux
# Chaque VM ne peut parler qu'à des VM spécifiques

# VM1 (WEB) → VM2 (APP) port 8080 seulement
ovs-ofctl add-flow br-int \
  "table=0,priority=100, \
   in_port=1,dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:02, \
   tcp,tp_dst=8080,actions=output:2"

# VM2 (APP) → VM1 (WEB) established seulement
ovs-ofctl add-flow br-int \
  "table=0,priority=100, \
   in_port=2,dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:01, \
   tcp,tp_src=8080,actions=output:1"

# Tout autre trafic bloqué
ovs-ofctl add-flow br-int "table=0,priority=1,actions=drop"
```

---

## Pièges et Bonnes Pratiques

- **ACLs** : Toujours mettre les ACLs étendues au plus près de la source pour limiter le trafic inutile
- **Logging** : Logguer les drops (avec rate limiting pour éviter de saturer les logs)
- **Conntrack** : Toujours autoriser `ESTABLISHED,RELATED` avant les règles de NEW
- **Fail2ban** : Combiner avec fail2ban pour bloquer les IP malveillantes dynamiquement
- **Suricata vs Snort** : Préférer Suricata pour les environnements multi-cœurs (multi-threaded)
- **IPS inline** : Tester en mode IDS (alert only) avant de passer en mode IPS (block)
- **Zero Trust** : Commencer par cartographier tous les flux existants avant d'écrire les politiques
- **Micro-segmentation** : Commencer par allow-list DNS/DHCP (infra critique) avant les blocs stricts

## Ressources

- Suricata : https://suricata.io/documentation/
- Snort : https://www.snort.org/documents
- nftables : https://wiki.nftables.org/wiki-nftables/index.php/Main_Page
- pfSense Docs : https://docs.netgate.com/pfsense/en/latest/
- Zero Trust (NIST SP 800-207) : https://csrc.nist.gov/publications/detail/sp/800-207/final
- Tailscale Docs : https://tailscale.com/kb/
- OVS Security : https://docs.openvswitch.org/en/latest/tutorials/ovs-conntrack/