---
name: vpn-tunneling-protocols
description: Guide complet des VPN et tunnels réseau — WireGuard, OpenVPN, IPsec/IKEv2, GRE, L2TP, SSTP, tunnellisation site-to-site, remote access, split tunneling, et performance.
tags: [vpn, wireguard, openvpn, ipsec, ikev2, gre, l2tp, tunneling, site-to-site, remote-access, strongswan]
---

# VPN et Tunnelling — Protocoles et Déploiement

## Présentation

Guide complet des technologies de réseau privé virtuel (VPN) et de tunnellisation : protocoles, déploiement site-to-site et remote access, optimisation des performances, et sécurité.

---

## WireGuard — VPN Moderne et Performant

### Architecture

```text
  +----------------+       UDP/51820       +----------------+
  | Peer A         |───────────────────────| Peer B         |
  | 10.0.0.1/32   |                       | 10.0.0.2/32   |
  | 192.168.1.10   |                       | 192.168.2.10   |
  +----------------+                       +----------------+
         |                                        |
    [Réseau local]                          [Réseau local]
    192.168.1.0/24                          192.168.2.0/24
```

### Installation

```bash
# Installation (noyau Linux 5.6+)
sudo apt-get install wireguard wireguard-tools

# Générer les clés
wg genkey | tee /etc/wireguard/private.key | wg pubkey > /etc/wireguard/public.key
chmod 600 /etc/wireguard/private.key
```

### Configuration Serveur

```bash
# /etc/wireguard/wg0.conf
[Interface]
PrivateKey = <serveur-privkey>
Address = 10.0.0.1/24
ListenPort = 51820

# NAT / Firewall
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

# Client 1 — Accès complet
[Peer]
PublicKey = <client1-pubkey>
PresharedKey = <client1-psk>
AllowedIPs = 10.0.0.2/32

# Client 2 — Accès limité
[Peer]
PublicKey = <client2-pubkey>
AllowedIPs = 10.0.0.3/32

# Site-to-site (réseau complet)
[Peer]
PublicKey = <site2-pubkey>
AllowedIPs = 10.0.0.0/24, 192.168.2.0/24
Endpoint = site2.example.com:51820
PersistentKeepalive = 25
```

### Configuration Client

```bash
# /etc/wireguard/wg0.conf (client)
[Interface]
PrivateKey = <client-privkey>
Address = 10.0.0.2/32
DNS = 10.0.0.1, 1.1.1.1

[Peer]
PublicKey = <serveur-pubkey>
PresharedKey = <psk>  # Protection post-quantique optionnelle
AllowedIPs = 0.0.0.0/0  # Full tunnel (tout via VPN)
# AllowedIPs = 10.0.0.0/24, 192.168.0.0/16  # Split tunnel
Endpoint = vpn.example.com:51820
PersistentKeepalive = 25
```

### Gestion et Monitoring

```bash
# Activer/Désactiver
wg-quick up wg0
wg-quick down wg0

# Status
sudo wg show
sudo wg show wg0 transfer
sudo wg show wg0 endpoints

# Statistiques
ip -s link show wg0
ip -stats link show wg0

# Systemd
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

# Script de monitoring
watch -n 1 'wg show wg0; echo "---"; ip -s link show wg0 | grep RX'
```

### Performance WireGuard

```bash
# Benchmarks
iperf3 -c 10.0.0.1 -t 30 -P 4
# Résultat typique : ~2-3 Gbps sur CPU moderne, > 800 Mbps sur Raspberry Pi

# Kernel vs userspace
# WireGuard dans le noyau Linux (5.6+) : performance maximale
# wireguard-go (userspace) : utilisable mais 2-3x moins performant
```

---

## OpenVPN — VPN Flexible et Mature

### Architecture

```text
  +----------------+       UDP/1194       +----------------+
  | Client         |───────────────────────| Serveur        |
  | tun0           |                       | tun0           |
  | 10.8.0.2/24   |                       | 10.8.0.1/24   |
  +----------------+                       +----------------+
         |                                        |
    [Internet]                               [Réseau local]
                                             192.168.1.0/24
```

### Configuration Serveur OpenVPN

```bash
# Génération des certificats
git clone https://github.com/OpenVPN/easy-rsa.git
cd easy-rsa/easyrsa3
./easyrsa init-pki
./easyrsa build-ca nopass
./easyrsa build-server-full server nopass
./easyrsa build-client-full client1 nopass
./easyrsa gen-dh
```

```bash
# /etc/openvpn/server.conf
port 1194
proto udp
dev tun

# Certificats
ca /etc/openvpn/pki/ca.crt
cert /etc/openvpn/pki/issued/server.crt
key /etc/openvpn/pki/private/server.key
dh /etc/openvpn/pki/dh.pem
tls-crypt /etc/openvpn/pki/ta.key  # Protection contre les attaques TLS

# Réseau VPN
server 10.8.0.0 255.255.255.0
topology subnet
push "route 192.168.1.0 255.255.255.0"
push "dhcp-option DNS 192.168.1.10"
push "dhcp-option DOMAIN internal.example.com"

# Sécurité
cipher AES-256-GCM
auth SHA256
tls-version-min 1.2
tls-cipher TLS-ECDHE-RSA-WITH-AES-256-GCM-SHA384
ecdh-curve prime256v1

# Performances
keepalive 10 60
max-clients 100
compress lz4-v2
push "compress lz4-v2"

# Logging
status /var/log/openvpn/status.log
log-append /var/log/openvpn/openvpn.log
verb 3
mute 20

# Options avancées
sndbuf 0
rcvbuf 0
push "sndbuf 0"
push "rcvbuf 0"
txqueuelen 1000
```

### Configuration Client OpenVPN

```bash
# client.ovpn
client
dev tun
proto udp
remote vpn.example.com 1194
resolv-retry infinite
nobind

# Certificats inline
<ca>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</ca>
<cert>
-----BEGIN CERTIFICATE-----
...
-----END CERTIFICATE-----
</cert>
<key>
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
</key>
<tls-crypt>
#
# 2048 bit OpenVPN static key
#
-----BEGIN OpenVPN Static key V1-----
...
-----END OpenVPN Static key V1-----
</tls-crypt>

# Sécurité
cipher AES-256-GCM
auth SHA256
tls-version-min 1.2

# Routes
route-nopull  # Ne pas utiliser les routes pushées
# route 192.168.1.0 255.255.255.0  # Split tunnel manuel

# Logging
verb 3
```

---

## IPsec / IKEv2 — VPN Standard Industriel

### StrongSwan (IKEv2)

```bash
# Installation
sudo apt-get install strongswan strongswan-pki libcharon-extra-plugins

# Génération des certificats
pki --gen --type rsa --size 4096 --outform pem > ca.key.pem
pki --self --in ca.key.pem --dn "CN=VPN CA" --ca --outform pem > ca.cert.pem
pki --gen --type rsa --size 2048 --outform pem > server.key.pem
pki --pub --in server.key.pem | pki --issue --cacert ca.cert.pem \
  --cakey ca.key.pem --dn "CN=vpn.example.com" \
  --san vpn.example.com --flag serverAuth --flag ikeIntermediate \
  --outform pem > server.cert.pem
```

```bash
# /etc/ipsec.conf
config setup
    charondebug="ike 2, knl 2, cfg 2, net 2, esp 2, dmn 1, mgr 1"
    strictcrlpolicy=no
    uniqueids=yes

conn %default
    ikelifetime=24h
    lifetime=8h
    rekeymargin=3m
    keyingtries=1
    keyexchange=ikev2
    authby=pubkey
    mobike=yes

conn ikev2-vpn
    left=%any
    leftid=@vpn.example.com
    leftcert=server.cert.pem
    leftsubnet=0.0.0.0/0
    leftfirewall=yes
    right=%any
    rightid=%any
    rightauth=pubkey
    rightsourceip=10.0.2.0/24
    rightdns=1.1.1.1, 8.8.8.8
    auto=add

    # Chiffrement fort
    ike=aes256gcm16-prfsha384-ecp384!
    esp=aes256gcm16-ecp384!
```

```bash
# /etc/strongswan.d/charon.conf
charon {
    load_modular = yes
    plugins {
        include strongswan.d/charon/*.conf
    }
    
    # Performance
    threads = 16
    half_open_timeout = 30
    retransmit_timeout = 5
    
    # DPD
    keep_alive = 20
}

# /etc/strongswan.d/charon/kernel-netlink.conf
kernel-netlink {
    # Empêcher les fuites de trafic
    charon.install_routes = yes
    charon.install_virtual_ip = yes
}
```

### IPsec Site-to-Site

```bash
# /etc/ipsec.conf — Site A (HQ)
conn hq-to-branch
    left=192.168.1.1
    leftsubnet=192.168.1.0/24
    leftid=@hq.example.com
    leftcert=hq.cert.pem
    right=203.0.113.10
    rightsubnet=192.168.2.0/24
    rightid=@branch.example.com
    auto=start
    ike=aes256-sha256-modp2048!
    esp=aes256-sha256!
    dpdaction=restart
    dpddelay=10
    dpdtimeout=60

# /etc/ipsec.conf — Site B (Branch)
conn branch-to-hq
    left=192.168.2.1
    leftsubnet=192.168.2.0/24
    leftid=@branch.example.com
    leftcert=branch.cert.pem
    right=198.51.100.1
    rightsubnet=192.168.1.0/24
    rightid=@hq.example.com
    auto=start
    ike=aes256-sha256-modp2048!
    esp=aes256-sha256!
```

### IPsec + NAT Traversal

```bash
# /etc/ipsec.conf
conn ikev2-nat
    left=%defaultroute
    leftid=@vpn.example.com
    leftcert=server.cert.pem
    leftsubnet=0.0.0.0/0
    right=%any
    rightsourceip=10.0.3.0/24
    rightdns=1.1.1.1
    auto=add
    
    # NAT traversal
    nat-traversal=yes
    forceencaps=yes
    fragmentation=yes
    dpdaction=clear
```

---

## GRE — Generic Routing Encapsulation

### Configuration GRE

```bash
# Tunnel GRE simple
ip link add gre0 type gre local 192.168.1.1 remote 203.0.113.10 ttl 64
ip addr add 10.0.100.1/30 dev gre0
ip link set gre0 up

# Tunnel GRE avec clé (multi-tunnel)
ip link add gre1 type gre local 192.168.1.1 remote 203.0.113.20 key 12345 ttl 64
ip addr add 10.0.100.5/30 dev gre1
ip link set gre1 up

# GRE over IPsec (encryption)
# 1. Créer IPsec tunnel
# 2. Créer GRE par-dessus IPsec
# 3. Router le trafic entre GRE et IPsec

# Vérification
ip tunnel show
ip -s link show gre0
ping -c 3 10.0.100.2
```

---

## L2TP/IPsec

```bash
# xl2tpd + strongswan
# /etc/xl2tpd/xl2tpd.conf
[lac vpn-connection]
lns = vpn.example.com
ppp debug = yes
pppoptfile = /etc/ppp/options.l2tpd.client
length bit = yes

# /etc/ppp/options.l2tpd.client
ipcp-accept-local
ipcp-accept-remote
refuse-eap
require-mschap-v2
name "vpn-user"
password "password"
```

---

## Split Tunneling

### Configuration Split Tunnel

```bash
# WireGuard — Split tunnel
# Dans AllowedIPs, ne mettre que les sous-réseaux qui doivent passer par le VPN
[Peer]
PublicKey = <serveur-pubkey>
AllowedIPs = 10.0.0.0/8, 192.168.0.0/16, 172.16.0.0/12

# OpenVPN — Split tunnel
# Dans server.conf
push "route 10.0.0.0 255.0.0.0"
push "route 192.168.0.0 255.255.0.0"
# Et dans client.ovpn
route-nopull  # Ne pas accepter les routes pushées
route 10.0.0.0 255.0.0.0  # Route manuelle vers le VPN

# StrongSwan — Split tunnel
# Dans ipsec.conf
conn ikev2-split
    leftsubnet=10.0.0.0/8,192.168.0.0/16
    rightsourceip=10.0.2.0/24
```

---

## Performance et Optimisation

### Benchmarking

```bash
# Tests de performance
# WireGuard
iperf3 -c 10.0.0.1 -t 30 -P 4
# Résultat: 2-3 Gbps (AES-NI + CPU moderne)

# OpenVPN
iperf3 -c 10.8.0.1 -t 30 -P 4
# Résultat: 500-800 Mbps (chiffrement userspace)

# IPsec
# Utiliser les compteurs du noyau
ipsec stats
cat /proc/net/xfrm_stat
```

### Optimisation

```bash
# TCP MSS clamping
iptables -t mangle -A FORWARD -p tcp --tcp-flags SYN,RST SYN -j TCPMSS --clamp-mss-to-pmtu

# Tuning noyau
cat >> /etc/sysctl.conf << 'EOF'
# VPN performance
net.core.rmem_default = 262144
net.core.wmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq
net.ipv4.tcp_notsent_lowat = 16384
EOF

# Multi-threading (OpenVPN)
# config server.conf
sndbuf 0
rcvbuf 0
push "sndbuf 0"
push "rcvbuf 0"
txqueuelen 1000
```

---

## Pièges et Bonnes Pratiques

- **Choix du protocole** : WireGuard pour la simplicité/performance, OpenVPN pour la flexibilité, IPsec pour la compatibilité
- **MTU** : Les tunnels ajoutent de l'overhead, réduire le MTU à 1400-1450 sur l'interface tunnel
- **Kill Switch** : Toujours configurer un kill switch (firewall rules) pour éviter les fuites de trafic si le VPN tombe
- **DNS Leak** : Configurer explicitement les DNS pour éviter les fuites
- **Preshared Key** : Toujours utiliser PSK en plus des clés publiques WireGuard (protection quantique)
- **Logging** : Ne pas logger les clés privées ou les mots de passe
- **Monitoring** : Mettre en place une alerte si le tunnel VPN tombe (Prometheus + blackbox_exporter)
- **Rotation des clés** : Planifier une rotation régulière des certificats/clés (90 jours recommandé)

## Ressources

- WireGuard : https://www.wireguard.com/
- OpenVPN : https://openvpn.net/community/
- StrongSwan : https://www.strongswan.org/
- Linux VPN/IPsec : https://wiki.strongswan.org/projects/strongswan/wiki
- iperf3 : https://github.com/esnet/iperf