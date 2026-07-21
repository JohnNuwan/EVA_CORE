---
name: vxlan-evpn-networking
description: Guide complet de virtualisation réseau — VXLAN, EVPN (MP-BGP EVPN), VTEP, VNI, tunnellisation overlay, configuration Cisco/Nexus, FRR, et déploiement data center.
tags: [vxlan, evpn, network-virtualization, overlay, vxlan-gateway, vtep, nvo, bgp-evpn]
---

# VXLAN & EVPN — Virtualisation Réseau Avancée

## Présentation

Technologies de superposition réseau (overlay) permettant de créer des réseaux virtuels de couche 2 sur une infrastructure de couche 3. VXLAN (VLAN eXtension) + EVPN (Ethernet VPN) sont le standard moderne des data centers.

### Concepts Clés

| Terme | Description |
|-------|-------------|
| **VXLAN** | Encapsulation MAC-in-UDP (RFC 7348) |
| **VTEP** | VXLAN Tunnel Endpoint — point d'encapsulation/décapsulation |
| **VNI** | VXLAN Network Identifier (24-bit) — segment virtuel (1-16M) |
| **EVPN** | MP-BGP pour distribuer les informations MAC/VTEP |
| **NVE** | Network Virtualization Edge — interface VTEP |
| **VXLAN Gateway** | Pont entre VXLAN et VLAN/VRF |

---

## Architecture VXLAN

### Encapsulation VXLAN

```
+-------------------------------+-------+-----+
| Paquet Original (Ethernet)    |       |     |
| +----------+------+--------+  |       |     |
| | MAC_dst | MAC_src | Payload| | UDP  | IP  |
| +----------+------+--------+  | 4789  |     |
+-------------------------------+-------+-----+
         |                            |
  Encapsulation VXLAN          Port VXLAN
         |
+----------------------------+-------+-----+----+
| VXLAN Header (VNI=10000)   | UDP   | IP  | MAC |
| Outer Ethernet Header      | 4789  | Out | Out |
+----------------------------+-------+-----+----+
```

### Modes de Déploiement

```text
Mode 1: VXLAN Multicast
    ┌────────┐       ┌────────┐
    │ VTEP-1 │───────│ VTEP-2 │
    └───┬────┘       └───┬────┘
        │               │
    ┌───┴────┐       ┌───┴────┐
    │ VTEP-3 │───────│ VTEP-4 │
    └────────┘       └────────┘
    Flux BUM via groupe multicast (239.1.1.x)

Mode 2: VXLAN EVPN (Control Plane)
    ┌────────┐       ┌────────┐
    │ VTEP-1 │───────│ VTEP-2 │
    └───┬────┘       └───┬────┘
        │               │
    ┌───┴────┐       ┌───┴────┐
    │ Spine  │───────│ Spine   │
    └───┬────┘       └───┬────┘
        │               │
    ┌───┴────┐       ┌───┴────┐
    │ VTEP-3 │───────│ VTEP-4 │
    └────────┘       └────────┘
    BUM via ingress replication (Head-end)
    Apprentissage MAC via MP-BGP EVPN
```

---

## Configuration VXLAN (FRR / Linux)

### Linux Native VXLAN (iproute2)

```bash
# Créer un VTEP local
ip link add vxlan10 type vxlan \
  id 10000 \
  dstport 4789 \
  local 10.0.0.1 \
  remote 10.0.0.2 \
  dev eth0 \
  ttl 64

# Activer
ip link set vxlan10 up
ip addr add 192.168.100.1/24 dev vxlan10

# Mode multicast
ip link add vxlan20 type vxlan \
  id 10001 \
  group 239.1.1.1 \
  dev eth0 \
  ttl 4

# Mode EVPN (apprentissage noyau)
ip link add vxlan30 type vxlan \
  id 10002 \
  local 10.0.0.1 \
  dstport 4789 \
  dev eth0 \
  nolearning \
  proxy_arp \
  l2miss l3miss

# Bridge VXLAN
ip link add br0 type bridge
ip link set vxlan10 master br0
ip link set eth1 master br0
ip link set br0 up
```

### FRR — VXLAN + EVPN

```bash
# /etc/frr/frr.conf
!
router bgp 65001
  bgp router-id 10.0.0.1
  neighbor 10.0.1.1 remote-as 65001
  neighbor 10.0.1.1 update-source lo
  !
  address-family l2vpn evpn
    neighbor 10.0.1.1 activate
    neighbor 10.0.1.1 route-reflector-client
    advertise-all-vni
  exit-address-family
!

# Associer VNI à l'EVPN
router bgp 65001
  address-family l2vpn evpn
    vni 10000
      rd 65001:10000
      rt import 65001:10000
      rt export 65001:10000
    exit-vni
    vni 10001
      rd 65001:10001
      rt import 65001:10001
      rt export 65001:10001
    exit-vni
  exit-address-family
!
```

---

## MP-BGP EVPN — Routes Network Layer

### Types de Routes EVPN

| Type | NLRI | Usage |
|------|------|-------|
| 1 | Ethernet Auto-Discovery | Détection multi-homing |
| 2 | MAC/IP Advertisement | Annonce MAC + IP |
| 3 | Inclusive Multicast | Arbre multicast/ingress replication |
| 4 | Ethernet Segment | Multi-homing ESI |
| 5 | IP Prefix Route | Routes IP (type-5) — L3VNI |

### Route Type-2 — MAC/IP Advertisement

```
NLRI:
  Route Distinguisher: 65001:10000
  Ethernet Segment ID: 0000.0000.0000.0000.0000
  Ethernet Tag ID: 0
  MAC Address: 00:1a:2b:3c:4d:5e
  IP Address: 192.168.100.10
  MPLS Label 1: 10000 (VNI)
  MPLS Label 2: 0
```

### Configuration EVPN Type-5 (L3VNI)

```bash
# Routeur configuré pour le routage entre VNI
!
vrf BLUE
  vni 50000
  rd 65001:50000
  rt both 65001:50000
!
router bgp 65001
  address-family ipv4 unicast
    vrf BLUE
      redistribute connected
      redistribute static
    exit-vrf
  !
  address-family l2vpn evpn
    vni 50000
      rd 65001:50000
      rt import 65001:50000
      rt export 65001:50000
    exit-vni
  exit-address-family
!
```

---

## Cisco Nexus — VXLAN EVPN (NX-OS)

### Configuration NX-OS

```bash
feature ospf
feature bgp
feature interface-vlan
feature vn-segment-vlan-based
feature nv overlay

# Anycast Gateway
ip arp prefix-advertisement
ipv6 nd prefix-advertisement

# Interface loopback (VTEP)
interface loopback0
  ip address 10.0.0.1/32
  ip router ospf 1 area 0

# NVE (Network Virtualization Edge)
interface nve1
  no shutdown
  source-interface loopback0
  host-reachability protocol bgp
  member vni 10000 mcast-group 239.1.1.1
    suppress-arp
  member vni 20000

# VLAN -> VNI mapping
vlan 100
  vn-segment 10000
vlan 200
  vn-segment 20000

# SVI (Anycast Gateway)
interface vlan100
  no shutdown
  vrf member TENANT-A
  ip address 192.168.100.1/24
  fabric forwarding anycast-gateway

# VRF
vrf context TENANT-A
  rd 65001:100
  address-family ipv4 unicast
    route-target both 65001:100
    route-target both 65001:100 evpn

# BGP EVPN
router bgp 65001
  router-id 10.0.0.1
  neighbor 10.0.1.1 remote-as 65001
  neighbor 10.0.1.1 update-source loopback0
  address-family l2vpn evpn
    neighbor 10.0.1.1 activate
    send-community extended
  vrf TENANT-A
    address-family ipv4 unicast
      advertise l2vpn evpn
```

### Vérifications NX-OS

```bash
show nve peers
show nve vni
show l2route evpn mac
show l2route evpn mac vni 10000
show l2route evpn ip
show bgp l2vpn evpn summary
show bgp l2vpn evpn route-type 2
show fabric forwarding ip 192.168.100.10
show vxlan
```

---

## Cas d'Usage Avancés

### Virtual Distributed Switch (VXLAN + EVPN Multi-tenant)

```text
+-----------+     +-----------+     +-----------+
| Tenant A  |     | Tenant B  |     | Tenant C  |
| VNI 10000 |     | VNI 20000 |     | VNI 30000 |
| VLAN 100  |     | VLAN 200  |     | VLAN 300  |
| 10.0.1.0/24|    | 10.0.2.0/24|    | 10.0.3.0/24|
+-----+-----+     +-----+-----+     +-----+-----+
      |                 |                 |
      +-----------------+-----------------+
                        |
                 +------+------+
                 |  Spine 1/2  |
                 | (RR EVPN)   |
                 +------+------+
                        |
          +-------------+-------------+
          |             |             |
    +-----+------+ +---+-----+ +-----+------+
    | Leaf 1     | | Leaf 2  | | Leaf 3     |
    | VTEP 1     | | VTEP 2  | | VTEP 3     |
    +-----+------+ +----+----+ +----+-------+
          |              |            |
    [Web1] [App1]   [DB1] [Web2]  [App2] [DB2]
```

### Symétrie Anycast VTEP

```bash
# Même adresse IP VTEP sur deux leaves (Active/Active)
interface nve1
  source-interface anycast1
!
interface anycast1
  ip address 10.0.0.100/32
  ip router ospf 1 area 0
```

### Gateway Bridging VXLAN-VLAN

```bash
# Pont entre VXLAN (overlay) et réseau physique
ip link add vxlan100 type vxlan id 10000 local 10.0.0.1 dstport 4789 dev eth0 nolearning
ip link set vxlan100 master br-vlan-vxlan
ip link set eth1 master br-vlan-vxlan
ip link set br-vlan-vxlan up
```

---

## Pièges et Bonnes Pratiques

- **MTU** : VXLAN ajoute 50 octets (ETH 14 + IP 20 + UDP 8 + VXLAN 8). Avoir MTU = 9000 (jumbo frames) sur l'underlay ou configurer TCP MSS clamping.
- **ECMP** : L'encapsulation UDP VXLAN avec entropie (src port hash) permet l'équilibrage de charge sur l'underlay.
- **ARP Suppression** : Activer sur le VTEP pour réduire le trafic ARP inondé.
- **Ingress Replication** : Mode EVPN sans multicast — plus scalable pour les petits/grands déploiements.
- **Control-plane learning** : Utiliser `nolearning` sur l'interface VXLAN en mode EVPN.
- **Route-target** : Utiliser une RT différente par VNI pour l'import et l'export si nécessaire.
- **Dual-homing** : ESI (Ethernet Segment Identifier) avec mode All-Active ou Single-Active.

## Ressources

- RFC 7348 (VXLAN) : https://datatracker.ietf.org/doc/rfc7348/
- RFC 8365 (VXLAN EVPN) : https://datatracker.ietf.org/doc/rfc8365/
- RFC 7432 (BGP MPLS EVPN) : https://datatracker.ietf.org/doc/rfc7432/
- Linux VXLAN doc : https://www.kernel.org/doc/html/latest/networking/vxlan.html
- Cisco Nexus VXLAN : https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-739559.html