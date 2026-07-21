---
name: dns-dhcp-ipam
description: Guide complet des services réseau fondamentaux — DNS (BIND, Unbound, CoreDNS), DHCP (ISC DHCP, dnsmasq), IPAM (NetBox, phpIPAM, Infoblox), DNSSEC, et automatisation.
tags: [dns, bind, unbound, coredns, dhcp, dnsmasq, ipam, netbox, dnssec, ip-address-management]
---

# DNS, DHCP et IPAM

## Présentation

Guide complet des services réseau fondamentaux : résolution de noms (DNS), attribution d'adresses (DHCP) et gestion du plan d'adressage (IPAM). Couvre les serveurs, la sécurité, l'automatisation et les outils de gestion.

---

## DNS — Domain Name System

### Architecture DNS

```text
+------------------+
| Root DNS Servers |
| 13 root (a-m)    |
+--------+---------+
         |
+--------+---------+
| TLD Name Servers |
| .com, .org, .fr  |
+--------+---------+
         |
+--------+---------+
| Authoritative    |
| example.com      |
+--------+---------+
         |
+--------+---------+
| Récursive        |
| Resolver         |
| (BIND, Unbound)  |
+------------------+
```

### BIND9 — Configuration Complète

```bash
# Installation
sudo apt-get install bind9 bind9utils bind9-doc

# /etc/bind/named.conf
include "/etc/bind/named.conf.options";
include "/etc/bind/named.conf.local";
include "/etc/bind/named.conf.default-zones";
```

```bash
# /etc/bind/named.conf.options
options {
    directory "/var/cache/bind";
    
    # Écouter sur les interfaces
    listen-on { 192.168.1.10; 127.0.0.1; };
    listen-on-v6 { none; };
    
    # Forwarders
    forwarders {
        1.1.1.1;     # Cloudflare
        8.8.8.8;     # Google
        9.9.9.9;     # Quad9
    };
    forward only;
    
    # Sécurité
    recursion yes;
    allow-query { 192.168.0.0/16; 127.0.0.0/8; localhost; };
    allow-recursion { 192.168.0.0/16; 127.0.0.0/8; };
    allow-transfer { none; };
    allow-update { none; };
    
    # DNSSEC
    dnssec-validation auto;
    dnssec-enable yes;
    
    # Rate limiting
    rate-limit {
        responses-per-second 10;
        window 5;
    };
    
    # Logging
    querylog yes;
};

# Logging
logging {
    channel query_log {
        file "/var/log/bind/queries.log" versions 3 size 20m;
        severity info;
        print-time yes;
    };
    category queries { query_log; };
};
```

```bash
# /etc/bind/named.conf.local — Zone file
zone "internal.example.com" {
    type master;
    file "/etc/bind/zones/db.internal.example.com";
    allow-update { key rndc-key; };
    allow-transfer { 192.168.1.11; };
    also-notify { 192.168.1.11; };
};

zone "home.arpa" {
    type master;
    file "/etc/bind/zones/db.1.168.192";
};

zone "." {
    type hint;
    file "/etc/bind/db.root";
};
```

```bash
# /etc/bind/zones/db.internal.example.com
$TTL    604800
@       IN      SOA     ns1.internal.example.com. admin.internal.example.com. (
                      2024071501  ; Serial (YYYYMMDDNN)
                          604800  ; Refresh
                           86400  ; Retry
                         2419200  ; Expire
                          604800  ; Negative Cache TTL
)

; Name servers
@       IN      NS      ns1.internal.example.com.
@       IN      NS      ns2.internal.example.com.

; A records
ns1     IN      A       192.168.1.10
ns2     IN      A       192.168.1.11
mail    IN      A       192.168.1.20
        IN      MX 10   mail.internal.example.com.

; SRV records (LDAP, Kerberos)
_ldap._tcp     IN SRV 10 0 389 ldap1.internal.example.com.
_kerberos._udp IN SRV 10 0 88 kdc1.internal.example.com.

; CNAME records
www     IN      CNAME   web-server.internal.example.com.
api     IN      CNAME   web-server.internal.example.com.

; TXT records (SPF, DKIM, DMARC)
@       IN      TXT     "v=spf1 mx ip4:192.168.1.0/24 -all"
mail    IN      TXT     "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC..."
_dmarc  IN      TXT     "v=DMARC1; p=reject; rua=mailto:dmarc@example.com"
```

```bash
# /etc/bind/zones/db.1.168.192 (reverse DNS)
$TTL    604800
@       IN      SOA     ns1.internal.example.com. admin.internal.example.com. (
                      2024071501  ; Serial
                          604800  ; Refresh
                           86400  ; Retry
                         2419200  ; Expire
                          604800  ; Negative Cache TTL
)

@       IN      NS      ns1.internal.example.com.
@       IN      NS      ns2.internal.example.com.

10      IN      PTR     ns1.internal.example.com.
11      IN      PTR     ns2.internal.example.com.
20      IN      PTR     mail.internal.example.com.
100     IN      PTR     web-server.internal.example.com.
```

### Unbound — Résolveur DNSSEC

```bash
# Installation
sudo apt-get install unbound unbound-anchor

# /etc/unbound/unbound.conf
server:
    interface: 0.0.0.0
    port: 53
    do-ip4: yes
    do-ip6: no
    do-udp: yes
    do-tcp: yes
    
    # Access control
    access-control: 127.0.0.0/8 allow
    access-control: 192.168.0.0/16 allow
    access-control: ::1 allow
    
    # DNSSEC
    auto-trust-anchor-file: "/var/lib/unbound/root.key"
    val-log-level: 2
    val-clean-additional: yes
    
    # Performance
    num-threads: 4
    msg-cache-slabs: 8
    rrset-cache-slabs: 8
    infra-cache-slabs: 8
    key-cache-slabs: 8
    rrset-cache-size: 100m
    msg-cache-size: 50m
    
    # Privacy
    hide-identity: yes
    hide-version: yes
    qname-minimisation: yes
    rrset-roundrobin: yes
    
    # Rate limiting
    ratelimit: 1000
    ratelimit-slabs: 8
    ratelimit-size: 100k
    
    # Cache
    prefetch: yes
    prefetch-key: yes
    serve-expired: yes
    serve-expired-ttl: 86400

# Forward DNS
stub-zone:
    name: "internal.example.com"
    stub-addr: 192.168.1.10
    stub-addr: 192.168.1.11

# Block malware domains
local-zone: "malware.example.com" always_null
```

### CoreDNS — DNS Moderne pour Kubernetes

```bash
# Corefile
.:53 {
    # Cache
    cache 30
    
    # Health check
    health
    
    # Prometheus metrics
    prometheus :9153
    
    # Forward to upstream
    forward . 1.1.1.1 8.8.8.8 {
        max_concurrent 1000
        policy random
        health_check 5s
    }
    
    # Logging
    log
    errors
}

internal.example.com {
    file /etc/coredns/zones/db.internal.example.com
    prometheus
    log
}

# Kubernetes plugin
.:53 {
    kubernetes cluster.local in-addr.arpa ip6.arpa {
        pods insecure
        fallthrough in-addr.arpa ip6.arpa
    }
    prometheus :9153
    forward . /etc/resolv.conf
    cache 30
}
```

### DNSSEC

```bash
# Générer les clés DNSSEC
cd /etc/bind/zones
dnssec-keygen -a ECDSAP256SHA256 -n ZONE internal.example.com
dnssec-keygen -f KSK -a ECDSAP256SHA256 -n ZONE internal.example.com

# Signer la zone
dnssec-signzone -A -3 $(head -c 16 /dev/random | od -An -tx1 | tr -d ' \n') \
    -N INCREMENT -o internal.example.com -t db.internal.example.com

# Dans named.conf
zone "internal.example.com" {
    type master;
    file "/etc/bind/zones/db.internal.example.com.signed";  # Zone signée
    auto-dnssec maintain;
    inline-signing yes;
};

# Vérifier
delv +multiline example.com SOA
dig example.com +dnssec
```

---

## DHCP — Dynamic Host Configuration Protocol

### ISC DHCP Server

```bash
# Installation
sudo apt-get install isc-dhcp-server

# /etc/dhcp/dhcpd.conf
option domain-name "internal.example.com";
option domain-name-servers 192.168.1.10, 192.168.1.11;
option ntp-servers 192.168.1.30;
default-lease-time 86400;
max-lease-time 172800;
authoritative;

# VLAN 10 — Admin
subnet 192.168.10.0 netmask 255.255.255.0 {
    option routers 192.168.10.1;
    option subnet-mask 255.255.255.0;
    option broadcast-address 192.168.10.255;
    range 192.168.10.100 192.168.10.200;
    default-lease-time 3600;
    max-lease-time 7200;
}

# VLAN 20 — Users
subnet 192.168.20.0 netmask 255.255.255.0 {
    option routers 192.168.20.1;
    option domain-name-servers 1.1.1.1, 8.8.8.8;
    range 192.168.20.100 192.168.20.254;
}

# Réservations statiques
host web-server {
    hardware ethernet 00:1a:2b:3c:4d:5e;
    fixed-address 192.168.10.100;
    option host-name "web-server";
}

# DHCP Relay via IP helper
# Sur le routeur L3 :
interface Vlan10
  ip helper-address 192.168.1.10  # DHCP server
```

### dnsmasq — Léger et Intégré

```bash
# /etc/dnsmasq.conf
# DNS + DHCP en un seul service
port=53
domain-needed
bogus-priv
expand-hosts
domain=internal.example.com

# Interfaces
interface=eth0
bind-interfaces

# DHCP
dhcp-range=192.168.1.100,192.168.1.200,12h
dhcp-option=3,192.168.1.1     # Gateway
dhcp-option=6,192.168.1.10    # DNS
dhcp-option=42,192.168.1.30   # NTP
dhcp-host=00:1a:2b:3c:4d:5e,web-server,192.168.1.100
dhcp-leasefile=/var/lib/dnsmasq/leases

# DNS local
address=/internal.example.com/192.168.1.10
server=/google.com/8.8.8.8
server=1.1.1.1

# Block domains
address=/doubleclick.net/0.0.0.0
address=/tracker.example.com/0.0.0.0

# Cache
cache-size=10000
dns-forward-max=150
```

---

## IPAM — IP Address Management

### NetBox — IPAM Open Source

```bash
# Installation Docker
git clone https://github.com/netbox-community/netbox-docker.git
cd netbox-docker
docker compose up -d

# Accès : http://localhost:8000
# admin/admin
```

```bash
# API REST NetBox
# Créer un préfixe
curl -X POST https://netbox.example.com/api/ipam/prefixes/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prefix": "10.0.0.0/16",
    "status": "active",
    "site": 1,
    "role": 1,
    "description": "Production DC prefix"
  }'

# Créer une adresse IP
curl -X POST https://netbox.example.com/api/ipam/ip-addresses/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "10.0.1.100/24",
    "status": "active",
    "dns_name": "web-server.internal.example.com",
    "description": "Web server primary IP"
  }'

# Lister les adresses libres
curl -X GET https://netbox.example.com/api/ipam/prefixes/1/available-ips/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json"

# Ajouter un VLAN
curl -X POST https://netbox.example.com/api/ipam/vlans/ \
  -H "Authorization: Token $TOKEN" \
  -d '{"vid": 100, "name": "INTRANET", "site": 1, "status": "active"}'
```

### phpIPAM — Alternative Web

```bash
# Installation Docker
docker run -d --name phpipam \
  -p 80:80 \
  -e MYSQL_HOST=db \
  -e MYSQL_USER=phpipam \
  -e MYSQL_PASSWORD=secret \
  -e MYSQL_DB=phpipam \
  phpipam/phpipam-www:latest

# Accès : http://localhost
# User: admin / Password: ipamadmin
```

### Automatisation IPAM

```bash
# Script d'automatisation NetBox + Nornir
#!/usr/bin/env python3
import pynetbox
import requests
from nornir import InitNornir

NB_URL = "https://netbox.example.com"
NB_TOKEN = "your-token"

nb = pynetbox.api(NB_URL, NB_TOKEN)

def get_free_ip(prefix, description=""):
    """Obtenir une IP libre depuis NetBox"""
    prefix_obj = nb.ipam.prefixes.get(prefix=prefix)
    if not prefix_obj:
        raise ValueError(f"Prefix {prefix} not found")
    available = prefix_obj.available_ips.list()
    if not available:
        raise ValueError("No free IPs")
    ip = available[0]
    ip.description = description
    ip.save()
    return str(ip.address).split('/')[0]

def update_dns(hostname, ip_address):
    """Mettre à jour DNS via BIND RNDC"""
    requests.post(f"{NB_URL}/api/extras/scripts/DNSUpdate.py/",
        headers={"Authorization": f"Token {NB_TOKEN}"},
        json={"hostname": hostname, "ip_address": ip_address})

# Utilisation
ip = get_free_ip("10.0.1.0/24", "Web server #42")
update_dns("web-server-42", ip)
print(f"IP: {ip} allouée")
```

---

## Pièges et Bonnes Pratiques

- **DNS** : Toujours configurer 2+ serveurs DNS, zone primaire + secondaire
- **DNSSEC** : Activer validation coté résolveur + signer les zones autoritaires
- **TTL** : 300s pour les records critiques, 86400s pour les records stables
- **DHCP failover** : Configurer deux serveurs DHCP en load balancing (50/50 split)
- **IPAM** : Toujours utiliser IPAM avant d'allouer une IP, jamais manuellement
- **Sécurité** : Limiter les transferts de zone aux serveurs secondaires autorisés
- **Monitoring** : Surveiller les taux de résolution DNS, les temps de réponse, les erreurs NXDOMAIN
- **Logs** : Archiver les logs DHCP (preuve légale de l'attribution d'IP)

## Ressources

- BIND 9 : https://bind9.readthedocs.io/
- Unbound : https://nlnetlabs.nl/projects/unbound/about/
- CoreDNS : https://coredns.io/manual/toc/
- ISC DHCP : https://www.isc.org/dhcp/
- NetBox : https://netbox.readthedocs.io/
- phpIPAM : https://phpipam.net/documents/
- DNSSEC (Cloudflare) : https://www.cloudflare.com/dns/dnssec/how-dnssec-works/