---
name: network-security-hardening
description: Guide complet du durcissement réseau — ACLs, Firewalls (iptables/nftables, pfSense, NGFW), IDS/IPS (Snort, Suricata), Zero Trust Architecture (NIST 800-207), micro-segmentation, 802.1X NAC, et segmentation réseau.
tags: [firewall, ids, ips, snort, suricata, zero-trust, micro-segmentation, acl, nftables, iptables, nac, 802.1x, network-security, segmentation]
---

# Durcissement Sécurité Réseau

## Présentation

Stratégie de défense en profondeur pour le réseau. Pyramide de la sécurité réseau :

```
                    /\
                   /  \
                  / ZT \
                 /      \
                / Micro- \
               / segmente \
              /            \
             /  IDS/IPS     \
            /   (Snort,      \
           /    Suricata)     \
          /                   \
         /  Firewall (L4/L7)  \
        /     (iptables,       \
       /      pfSense, NGFW)   \
      /                        \
     /   ACLs + 802.1X (NAC)   \
    /____________________________\
```

---

## ACLs — Access Control Lists

### ACL Standards (Cisco IOS)

```bash
# ACL standard — filtre sur IP source
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any

# Appliquer sur interface
interface GigabitEthernet0/0
 ip access-group 10 in

# ACL étendue — filtre sur IP src/dst + ports
access-list 100 permit tcp 10.0.1.0 0.0.0.255 host 10.0.2.100 eq 80
access-list 100 permit tcp 10.0.1.0 0.0.0.255 host 10.0.2.100 eq 443
access-list 100 deny ip any any log

interface GigabitEthernet0/1
 ip access-group 100 in
```

### ACLs Cisco — Named et Reflexive

```bash
! ACL nommée
ip access-list extended BLOCK_MALICIOUS
 deny ip host 10.0.0.99 any
 permit tcp 10.0.1.0 0.0.0.255 any eq 80
 permit tcp 10.0.1.0 0.0.0.255 any eq 443
 deny ip any any log

! Appliquer
interface GigabitEthernet0/0
 ip access-group BLOCK_MALICIOUS in

! Reflective ACL (permet retours de connexions)
ip access-list extended OUTBOUND
 permit tcp 10.0.0.0 0.255.255.255 any reflect TCP_TRAFFIC
 permit udp 10.0.0.0 0.255.255.255 any reflect UDP_TRAFFIC

ip access-list extended INBOUND
 evaluate TCP_TRAFFIC
 evaluate UDP_TRAFFIC
 deny ip any any log

interface GigabitEthernet0/0
 ip access-group OUTBOUND out
 ip access-group INBOUND in
```

### ACLs sur Linux (iptables)

```bash
# Politique par défaut DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Loopback
iptables -A INPUT -i lo -j ACCEPT

# Connexions établies
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# SSH depuis management
iptables -A INPUT -p tcp --dport 22 -s 192.168.100.0/24 -j ACCEPT

# HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Rate limiting SSH
iptables -A INPUT -p tcp --dport 22 -m state --state NEW \
  -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m state --state NEW \
  -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP

# Bloquer ICMP flood
iptables -A INPUT -p icmp --icmp-type echo-request \
  -m limit --limit 1/second --limit-burst 5 -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP

# Log + drop
iptables -A INPUT -j LOG --log-prefix "FW-DROP: " --log-level 4
iptables -A INPUT -j DROP

# Sauvegarder
iptables-save > /etc/iptables/rules.v4
```

### ACLs nftables (moderne)

```bash
# /etc/nftables.conf
table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;

    # Loopback
    iif lo accept

    # Connexions établies
    ct state established,related accept

    # ICMP limité
    icmp type echo-request limit rate 1/second accept
    icmp type echo-request drop

    # Services
    tcp dport {http, https} accept
    tcp dport ssh ip saddr 192.168.100.0/24 accept

    # Log
    log prefix "NFT-DROP: " drop
  }

  chain forward {
    type filter hook forward priority filter; policy drop;

    # Forward LAN -> WAN
    ip saddr 10.0.0.0/8 oif wan0 accept
    ct state established,related iif wan0 accept

    log prefix "NFT-FWD-DROP: " drop
  }

  chain output {
    type filter hook output priority filter; policy accept
  }
}

# NAT
table inet nat {
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept
    oif wan0 masquerade
  }
}
```

---

## Firewalls — De l'Étatful au NGFW

### Architecture Firewall

```
+----------+     +----------+     +----------+
| Internet |---->| FW Ext   |---->| DMZ      |
|          |     | (NGFW)   |     | Web/Mail  |
+----------+     +----+-----+     +----------+
                      |
                 +----+-----+     +----------+
                 | FW Int   |---->| LAN      |
                 | (Étatful) |     | Users     |
                 +----------+     +----------+
```

### Stateful Firewall avec iptables

```bash
# Conntrack — Table des connexions actives
cat /proc/net/nf_conntrack
conntrack -L
conntrack -E  # Événements en temps réel

# Paramètres conntrack
sysctl -w net.netfilter.nf_conntrack_max=1048576
sysctl -w net.netfilter.nf_conntrack_tcp_timeout_established=432000

# iptables stateful complet
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -i lan0 -o wan0 -j ACCEPT
iptables -A FORWARD -i wan0 -o lan0 -m conntrack \
  --ctstate ESTABLISHED,RELATED -j ACCEPT

# NAT Stateful (masquerade)
iptables -t nat -A POSTROUTING -o wan0 -j MASQUERADE
```

### pfSense / OPNsense

```bash
# CLI pfSense
pfctl -s rules        # Voir les règles
pfctl -s states       # Voir les connexions actives
pfctl -s nat          # Règles NAT
pfctl -F states -k 192.168.1.100  # Kill états d'une IP
pfctl -e              # Activer pf
pfctl -d              # Désactiver pf

# Exemple de règles pf
# /etc/pf.conf
ext_if = "em0"
int_if = "em1"
dmz_net = "10.0.10.0/24"

# Options
set block-policy drop
set loginterface $ext_if
set skip on lo

# NAT
nat on $ext_if from $int_if:network to any -> ($ext_if)

# Règles
block log all
pass quick on lo all

# Trafic entrant
block in on $ext_if
pass in on $ext_if proto tcp to ($ext_if) port {80,443} keep state

# Trafic interne
pass in on $int_if from $int_if:network to any keep state

# DMZ
pass in on $ext_if proto tcp to $dmz_net port 80
pass out on $int_if proto tcp from $dmz_net to any
```

### NGFW — Next-Gen Firewall (pfSense + Suricata)

```bash
# Suricata sur pfSense
# Services > Suricata > Interfaces > WAN > Enable
# Configuration Suricata
/etc/ping-suricata/suricata.yaml

# Règles ET/Pro (Emerging Threats)
# https://rules.emergingthreats.net/

# Blocage automatique
# Suricata extrahe les alertes vers pfBlock
# pfSense > Services > pfBlockerNG

# Exemple de règle Suricata custom
# /usr/local/etc/suricata/rules/custom.rules
alert tcp $HOME_NET any -> $EXTERNAL_NET 8443 \
  (msg:"Trafic suspect port 8443"; \
   flow:to_server,established; \
   classtype:unknown; sid:1000001; rev:1;)
```

### Palo Alto NGFW (PanOS CLI)

```bash
# CLI PanOS
show interface all
show routing route
show session all
show session id 12345
show system info
show jobs all

# Configuration via XML API
curl -k -X POST \
  'https://panos-ip/api/?type=config&action=set&key=API_KEY&element=
    <security>
      <rules>
        <entry name="Allow-HTTP">
          <from>
            <member>trust</member>
          </from>
          <to>
            <member>untrust</member>
          </to>
          <source>
            <member>10.0.1.0/24</member>
          </source>
          <destination>
            <member>any</member>
          </destination>
          <application>
            <member>web-browsing</member>
            <member>ssl</member>
          </application>
          <service>
            <member>application-default</member>
          </service>
          <action>allow</action>
          <profile-setting>
            <profiles>
              <profile-group>
                <member>strict-security-profiles</member>
              </profile-group>
            </profiles>
          </profile-setting>
        </entry>
      </rules>
    </security>'

# Voir les logs
show log traffic | match 10.0.1.100
show log threat
```

---

## IDS/IPS — Snort & Suricata

### Suricata — Architecture

```
+--------+    +-----------+    +----------+
| Packets |-->| Capture   |-->| Detect   |
| (AF_PACKET|  | (DPDK/    |   | (Règles   |
|  PCAP)  |   |  AF_PACKET)|   |  Signature|
+--------+    +-----------+    +-----+----+
                                      |
                               +------v-----+
                               | Output     |
                               | (JSON,     |
                               |  Syslog,   |
                               |  Alert)    |
                               +------------+
```

### Installation et Configuration

```bash
# Installation Suricata
sudo apt-get install suricata
# ou source
wget https://www.openinfosecfoundation.org/download/suricata-7.0.6.tar.gz
./configure --enable-af-packet --enable-dpdk
make && make install

# Configuration
# /etc/suricata/suricata.yaml
af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

# Règles Emerging Threats
suricata-update update-source et/open
suricata-update enable-source et/open
suricata-update

# Démarrer en mode IDS
suricata -c /etc/suricata/suricata.yaml -i eth1 --init-errors-fatal

# Démarrer en mode IPS (inline)
suricata -c /etc/suricata/suricata.yaml -q 0
```

### Règles Suricata / Snort

```
# Règles de base
# Structure: action proto src_ip src_port -> dst_ip dst_port (msg; content; sid;)

# Détection de scan
alert tcp $EXTERNAL_NET any -> $HOME_NET any \
  (msg:"Port Scan"; \
   flow:to_server; \
   detection_filter:track by_src, count 20, seconds 10; \
   classtype:attempted-recon; sid:1000001; rev:1;)

# Détection SQL injection
alert tcp $EXTERNAL_NET any -> $HTTP_SERVERS $HTTP_PORTS \
  (msg:"SQL Injection - Union Select"; \
   flow:to_server,established; \
   content:"union"; nocase; http_uri; \
   content:"select"; nocase; http_uri; \
   distance:1; within:10; \
   classtype:web-application-attack; \
   sid:1000002; rev:1;)

# Détection C2 beaconing
alert tcp $HOME_NET any -> $EXTERNAL_NET $HTTP_PORTS \
  (msg:"C2 Beacon - Periodic Check-in"; \
   flow:to_server,established; \
   content:"GET /"; http_method; \
   content:"Host|3a| "; http_header; \
   threshold:type both, track by_src, count 10, seconds 300; \
   classtype:trojan-activity; sid:1000003; rev:1;)

# Détection brute-force SSH
alert tcp $EXTERNAL_NET any -> $HOME_NET 22 \
  (msg:"SSH Brute Force"; \
   flow:to_server,established; \
   detection_filter:track by_dst, count 10, seconds 60; \
   classtype:attempted-dos; sid:1000004; rev:1;)
```

### Suricata — Eve JSON Output

```bash
# Logs JSON structurés
# /var/log/suricata/eve.json

# Analyser avec jq
tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert")'

# Alertes par IP source
cat /var/log/suricata/eve.json | jq -r \
  'select(.event_type=="alert") | .src_ip' | sort | uniq -c | sort -rn

# Alertes par signature
cat /var/log/suricata/eve.json | jq -r \
  'select(.event_type=="alert") | .alert.signature' | sort | uniq -c | sort -rn

# Statistiques
cat /var/log/suricata/eve.json | jq \
  'select(.event_type=="stats") | .stats.decoder.ipv4'

# Flow log
cat /var/log/suricata/eve.json | jq \
  'select(.event_type=="flow") | {src: .src_ip, dst: .dst_ip, proto: .proto, bytes: .bytes_toclient + .bytes_toserver}'
```

### Suricata en Mode IPS (Inline)

```bash
# Nécessite NFQUEUE
iptables -I FORWARD -j NFQUEUE --queue-num 0
iptables -I INPUT -j NFQUEUE --queue-num 0

# Démarrer en mode IPS
suricata -c /etc/suricata/suricata.yaml -q 0

# Ou via netmap/af-packet inline
# suricata.yaml
af-packet:
  - interface: eth0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    mode: inline
    use-mmap: yes
  - interface: eth1
    cluster-id: 98
    cluster-type: cluster_flow
    defrag: yes
    mode: inline
    use-mmap: yes
```

### Snort Basics

```bash
# Installation
sudo apt-get install snort

# Configuration
# /etc/snort/snort.conf
ipvar HOME_NET 10.0.0.0/8
ipvar EXTERNAL_NET !$HOME_NET

# Règles custom
# /etc/snort/rules/local.rules
alert tcp any any -> $HOME_NET 23 (msg:"Telnet attempt"; sid:1000000;)

# Démarrer
snort -A console -q -c /etc/snort/snort.conf -i eth0
snort -A fast -l /var/log/snort -c /etc/snort/snort.conf

# Analyse de pcap
snort -r capture.pcap -c /etc/snort/snort.conf -l /tmp/snort-out
```

---

## Zero Trust Architecture (NIST SP 800-207)

### Principes Fondamentaux

```
┌────────────────────────────────────────────┐
│        Zero Trust (NIST 800-207)            │
├────────────────────────────────────────────┤
│ 1. Never trust, always verify              │
│ 2. Least privilege access                  │
│ 3. Assume breach                            │
│ 4. Micro-segmentation                       │
│ 5. Continuous monitoring                    │
│ 6. Dynamic policies                         │
│ 7. All sources untrusted until verified    │
└────────────────────────────────────────────┘
```

### Architecture ZT

```
                    ┌──────────────────┐
                    │   Policy Engine  │
                    │   (PDP)          │
                    └───────┬──────────┘
                            │
┌────────┐   ┌──────────────v──────────────┐   ┌────────┐
│ User   │   │      Policy Enforcement     │   │Resource│
│ Device │──>│      Point (PEP)            │──>│        │
│        │   │  (Gateway / Proxy / FW)     │   │  App   │
└────────┘   └─────────────────────────────┘   └────────┘
     │                    │
     v                    v
┌─────────┐        ┌──────────┐
│ Identity │       │ Threat   │
│ Provider │       │ Intel    │
└─────────┘        └──────────┘
```

### Implémentation Zero Trust

```bash
# 1. Micro-segmentation avec nftables

table inet microseg {
  # Segment: WEB (10.0.1.0/24)
  chain fwd_web {
    type filter hook forward priority filter; policy drop;

    # Web -> App (port 8080 uniquement)
    ip saddr 10.0.1.0/24 ip daddr 10.0.2.0/24 tcp dport 8080 accept

    # Web -> DB (interdit)
    ip saddr 10.0.1.0/24 ip daddr 10.0.3.0/24 drop

    # Web -> Internet (HTTP/HTTPS seulement)
    ip saddr 10.0.1.0/24 oif wan0 tcp dport {80, 443} accept
  }

  chain fwd_app {
    type filter hook forward priority filter; policy drop;

    # App -> DB (port 3306 uniquement, depuis app uniquement)
    ip saddr 10.0.2.0/24 ip daddr 10.0.3.0/24 tcp dport 3306 accept

    # App -> Internet (API uniquement)
    ip saddr 10.0.2.0/24 oif wan0 tcp dport 443 accept
  }
}

# 2. Just-in-Time Access avec SSH
# /etc/ssh/sshd_config.d/zt.conf
Match User admin
  AuthenticationMethods publickey
  AuthorizedKeysCommand /usr/local/bin/verify_jit_token.sh
  AuthorizedKeysCommandUser nobody
```

### Zero Trust avec Wireguard + Sidecar

```bash
# Sidecar proxy pour chaque service
# Chaque service a sa propre interface Wireguard
# Seulement les ports autorisés sont exposés

# Service Web
ip link add wg-web type wireguard
ip addr add 10.99.1.1/32 dev wg-web
wg setconf wg-web /etc/wireguard/web.conf

# Service DB
ip link add wg-db type wireguard
ip addr add 10.99.2.1/32 dev wg-db
wg setconf wg-db /etc/wireguard/db.conf

# iptables : uniquement service->db:3306
iptables -A FORWARD -i wg-web -o wg-db \
  -p tcp --dport 3306 -j ACCEPT
iptables -A FORWARD -j DROP
```

---

## Micro-segmentation

### Stratégie de Segmentation

```
┌──────────────────────────────────────────────────┐
│                  Data Center                       │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐       │
│  │ WEB Tier │   │ APP Tier │   │ DB Tier  │       │
│  │  10.0.1  │   │  10.0.2  │   │  10.0.3  │       │
│  │ :80/443  │──>│ :8080    │──>│ :3306    │       │
│  └──────────┘   └──────────┘   └──────────┘       │
│       │              │              │              │
│       └──────────────┴──────────────┘              │
│                        │                           │
│                  ┌─────v─────┐                     │
│                  │ Management │                    │
│                  │ 10.0.100  │                     │
│                  │ :22/443   │                     │
│                  └───────────┘                     │
└──────────────────────────────────────────────────┘
```

### Micro-segmentation via OVS + Flow Rules

```bash
# Open vSwitch micro-segmentation
ovs-ofctl add-flow br-int "priority=100, \
  in_port=web-port,ip,nw_src=10.0.1.0/24,nw_dst=10.0.2.0/24,\
  tcp,tp_dst=8080,actions=output:app-port"

ovs-ofctl add-flow br-int "priority=100, \
  in_port=app-port,ip,nw_src=10.0.2.0/24,nw_dst=10.0.3.0/24,\
  tcp,tp_dst=3306,actions=output:db-port"

# Drop tout autre trafic entre segments
ovs-ofctl add-flow br-int "priority=10, \
  ip,nw_src=10.0.1.0/24,nw_dst=10.0.3.0/24,actions=drop"

ovs-ofctl add-flow br-int "priority=1, \
  actions=normal"
```

### Micro-segmentation avec Cilium (Kubernetes)

```yaml
# CiliumNetworkPolicy: micro-segmentation
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "web-to-app-only"
spec:
  endpointSelector:
    matchLabels:
      app: web
  ingress: []
  egress:
  - toEndpoints:
    - matchLabels:
        app: app
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
---
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: "app-to-db-only"
spec:
  endpointSelector:
    matchLabels:
      app: app
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: web
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
  egress:
  - toEndpoints:
    - matchLabels:
        app: db
    toPorts:
    - ports:
      - port: "3306"
        protocol: TCP
```

---

## 802.1X — Network Access Control (NAC)

### Architecture 802.1X

```
┌─────────┐  EAPoL  ┌──────────┐  RADIUS  ┌──────────┐
│ Client  │<-------->│ Switch   │<--------->│ RADIUS   │
| (Supplicant)│      | (Authenticator)|    | Server   │
└─────────┘         └──────────┘          └──────────┘
                                                 │
                                           ┌─────v─────┐
                                           │ LDAP / AD │
                                           └───────────┘
```

### Configuration Switch (Cisco IOS)

```bash
! Activer AAA
aaa new-model
aaa authentication dot1x default group radius
aaa authorization network default group radius
aaa accounting dot1x default start-stop group radius

! RADIUS server
radius server RADIUS-MASTER
 address ipv4 192.168.100.10 auth-port 1812 acct-port 1813
 key radius_secret_key

! Activer 802.1X globalement
dot1x system-auth-control

! Interface avec 802.1X
interface GigabitEthernet0/1
 description Port Utilisateur
 switchport mode access
 switchport access vlan 10
 authentication port-control auto
 authentication periodic
 authentication timer reauthenticate 86400
 dot1x pae authenticator
 dot1x timeout tx-period 30
 dot1x max-reauth-req 3
 dot1x timeout quiet-period 60
 spanning-tree portfast
!
! Port de confiance (serveurs, imprimantes)
interface GigabitEthernet0/24
 description Serveur
 switchport mode access
 switchport access vlan 20
 authentication port-control force-authorized
 spanning-tree portfast
!

! VLAN dynamique via RADIUS (retour attribut)
! Sur le RADIUS : Tunnel-Private-Group-Id = VLAN ID
```

### FreeRADIUS Configuration

```bash
# /etc/freeradius/3.0/clients.conf
client switch-1 {
  ipaddr = 192.168.100.1
  secret = radius_secret_key
  require_message_authenticator = no
  nas_type = cisco
}

# /etc/freeradius/3.0/users
# Utilisateurs 802.1X
"user1" Cleartext-Password := "pass1"
  Tunnel-Type = VLAN,
  Tunnel-Medium-Type = IEEE-802,
  Tunnel-Private-Group-Id = "10"

# Machine authentication
"host/machine1.domain.local" Cleartext-Password := "machine_pass"
  Tunnel-Type = VLAN,
  Tunnel-Medium-Type = IEEE-802,
  Tunnel-Private-Group-Id = "20"

# Guest VLAN (échec d'auth)
DEFAULT Auth-Type := Reject
  Reply-Message = "Accès refusé"
```

### FreeRADIUS avec Active Directory

```bash
# /etc/freeradius/3.0/mods-enabled/ntlm_auth
ntlm_auth {
  program = "/usr/bin/ntlm_auth --request-nt-key \
    --username=%{ms-chap:User-Name} \
    --domain=DOMAIN.LOCAL \
    --challenge=%{ms-chap:Challenge} \
    --nt-response=%{ms-chap:NT-Response}"
}

# /etc/freeradius/3.0/sites-enabled/default
authenticate {
  Auth-Type MS-CHAP {
    ntlm_auth
  }
}
```

---

## Détection et Prévention

### Fail2Ban

```bash
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port    = ssh
filter  = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 3600
findtime = 600

[nginx-http-auth]
enabled = true
port    = http,https
filter  = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3
bantime = 86400

[suricata]
enabled = true
filter  = suricata
logpath = /var/log/suricata/eve.json
maxretry = 10
bantime = 3600
```

### Port Knocking

```bash
# Knockd — Séquence de ports pour ouvrir SSH
# /etc/knockd.conf
[openSSH]
  sequence    = 7000,8000,9000
  seq_timeout = 10
  command     = /sbin/iptables -A INPUT -p tcp --dport 22 \
                 -s %IP% -j ACCEPT
  tcpflags    = syn

[closeSSH]
  sequence    = 9000,8000,7000
  seq_timeout = 10
  command     = /sbin/iptables -D INPUT -p tcp --dport 22 \
                 -s %IP% -j ACCEPT
  tcpflags    = syn
```

---

## Pièges et Bonnes Pratiques

- **ACL Order** : Les ACLs sont évaluées séquentiellement. Toujours mettre les refus génériques en dernier.
- **Default Deny** : Toujours terminer une ACL par `deny any` ou `deny ip any any log`.
- **Stateful Inspection** : Utiliser `conntrack`/`state` plutôt que des ACLs statiques pour le trafic de retour.
- **Suricata Ruleset** : Commencer avec ET Open, puis ajouter des règles custom progressivement.
- **IPS False Positives** : Démarrer en mode IDS (alert), analyser les logs 1-2 semaines, puis passer en mode IPS (drop).
- **Zero Trust** : Commencer par cartographier tous les flux nécessaires (TLS/application), pas par bloquer.
- **802.1X Fail-open** : Toujours tester le mode `critical` (VLAN de secours) avant déploiement complet.
- **Performance** : Compter ~1-2 Gbps par coeur CPU pour Suricata en mode IDS (taille de paquet 1500 bytes).
- **Logs centralisés** : Envoyer les logs (eve.json, syslog) vers un SIEM central (Wazuh, ELK, Splunk).

## Ressources

- NIST SP 800-207 Zero Trust : https://csrc.nist.gov/publications/detail/sp/800-207/final
- Suricata : https://suricata.io/
- Snort : https://www.snort.org/
- pfSense : https://www.pfsense.org/
- FreeRADIUS : https://freeradius.org/
- nftables : https://wiki.nftables.org/
- Palo Alto Docs : https://docs.paloaltonetworks.com/
- Cilium : https://cilium.io/
- Fail2Ban : https://www.fail2ban.org/
- Emerging Threats : https://rules.emergingthreats.net/