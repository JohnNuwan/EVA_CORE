---
name: network-architectures-design
description: Guide des architectures réseau — spine-leaf, DMZ, haute disponibilité, VPC, multi-AZ, topologies data center, campus, WAN, et bonnes pratiques de conception.
tags: [network-design, spine-leaf, dmz, high-availability, vpc, data-center, network-topology, campus]
---

# Architectures et Conception Réseau

## Présentation

Méthodologies et patterns de conception réseau pour data center, campus, WAN, et cloud. Couvre les topologies, la redondance, le dimensionnement, et les bonnes pratiques d'architecture.

---

## Spine-Leaf (Clos Network)

### Architecture

```text
                    +-----+-----+        +-----+-----+
                    | Spine 1  |        | Spine 2  |
                    +-----+-----+        +-----+-----+
                     /   |   \            /   |   \
                    /    |    \          /    |    \
            +----+---+ +----+---+ +----+---+ +----+---+
            | Leaf 1 | | Leaf 2 | | Leaf 3 | | Leaf 4 |
            +----+---+ +----+---+ +----+---+ +----+---+
                 |           |           |           |
               [Servers]   [Servers]   [Servers]   [Servers]
```

### Propriétés du Spine-Leaf

```text
Avantages :
  • Bande passante égale (any-to-any)
  • Latence prévisible (2 hops max)
  • Scalabilité horizontale (ajouter des spines/leafs)
  • Redondance N+1 ou N+N
  • ECMP entre leaf et spine

Design Rules :
  • Chaque leaf se connecte à TOUS les spines
  • Chaque spine se connecte à TOUS les leafs
  • Pas de connexion leaf-leaf
  • Pas de connexion spine-spine
  • Underlay : EBGP ou OSPF/IS-IS unnumbered
  • Overlay : VXLAN EVPN
```

### Dimensionnement

```bash
# Exemple: DC 3 spines, 10 leafs (40 ports)
# Surcharge = 3:1 (oversubscription)

# Liens leaf → spine : 2x100G par leaf
# Capacité leaf uplink : 2 * 100G = 200G
# Capacité serveurs par leaf : 48 * 25G = 1200G
# Surcharge leaf : 1200G / 200G = 6:1

# Capacité spine : 10 * 200G = 2000G
# Surcharge totale : 10 * 1200G / 3 * 200G = 20:1
```

---

## Architecture Data Center

### Zones DC

```text
Internet
    |
+---+----+   +----+----+
| Internet|   |  DDoS   |
| Edge    |   |  Scrubbing
+----+----+   +----+----+
     |              |
+----+----+   +----+----+
| Border  |   | Firewall |
| Router  |   | Cluster  |
+----+----+   +----+----+
     |              |
+----+----+   +----+----+
| Spine   |   |  LB      |
| Layer   |   |  Cluster |
+----+----+   +----+----+
     |
+----+---------+---------+----+
| Leaf 1   | Leaf 2   | Leaf 3   |
+----+----+ +----+----+ +----+----+
|  |  |  | |  |  |  | |  |  |  |
Web  App  DB  Web  App  DB  Web  App  DB
```

### Exigences par Zone

```text
ZONE DMZ (Internet-facing)
  ├── ACLs restrictives, WAF, IDS/IPS
  ├── Rate limiting, DDoS protection
  ├── Certificats TLS automatisés
  └── BGP multi-homing

ZONE APPLICATION
  ├── Micro-segmentation par workload
  ├── L7 load balancing (HAProxy, Nginx)
  ├── Service mesh (Istio, Consul)
  └── Mutual TLS entre services

ZONE DONNÉES
  ├── Réseau de stockage dédié (SAN/NVMe-oF)
  ├── Backup et replication isolés
  ├── Encryption at rest + in transit
  └── Air-gap pour les sauvegardes

ZONE ADMIN
  ├── Bastion host (jumpbox)
  ├── Accès VPN/ZTNA obligatoire
  ├── Logging centralisé
  └── PAM (Privileged Access Management)
```

---

## Architecture Campus (Hierarchique)

```text
+====================================+
|         CORE LAYER                 |
|   Routeurs de cœur (IS-IS/BGP)     |
|   10G/100G — Redondance complète   |
+====================================+
           |     |     |
     +-----+-----+-----+-----+
     |     |     |     |     |
+==========+ +==========+ +==========+
|DISTRIBUTION| |DISTRIBUTION| |DISTRIBUTION|
| L3 L3 L3   | | L3 L3 L3  | | L3 L3 L3  |
| VRRP/HSRP  | | VRRP/HSRP | | VRRP/HSRP |
+============+ +==========+ +============+
     |            |            |
+========+   +========+   +========+
| ACCESS  |   | ACCESS  |   | ACCESS |
| L2 VLAN |   | L2 VLAN |   | L2 VLAN|
| PoE     |   | PoE     |   | PoE    |
+=========+   +=========+   +=========+
```

### Design Campus

```text
Core Layer
  ├── Routage L3 uniquement
  ├── Redondance complète (N+N)
  ├── Protocole : IS-IS ou OSPF
  └── ECMP pour bande passante

Distribution Layer
  ├── First-hop redundancy (VRRP/HSRP/vPC)
  ├── Summarization L3
  ├── QoS mark/trust boundary
  └── Policy enforcement (ACL, PBR)

Access Layer
  ├── VLAN de bout en bout (ou local)
  ├── 802.1x (NAC) authentication
  ├── MAB (MAC Authentication Bypass)
  ├── Storm control, BPDU guard, PortFast
  └── PoE/PoE+ pour téléphones, APs
```

### Configuration Exemplaire

```bash
# Cisco — Access Layer
interface GigabitEthernet1/0/1
  description PC-User-1
  switchport mode access
  switchport access vlan 100
  switchport port-security maximum 3
  switchport port-security violation restrict
  switchport port-security aging time 5
  spanning-tree portfast
  spanning-tree bpduguard enable
  ip verify source
  dot1x port-control auto
  mab
  authentication order dot1x mab
  authentication priority dot1x mab
  storm-control broadcast level 10

# HSRP — Distribution Layer
interface Vlan100
  ip address 192.168.100.2 255.255.255.0
  standby 100 ip 192.168.100.1
  standby 100 priority 110
  standby 100 preempt
  standby 100 track GigabitEthernet0/1 20
```

---

## Réseau WAN (SD-WAN / MPLS)

### Topologies WAN

```text
Hub-and-Spoke (1 hub central, N branches)
  ┌──────────┐
  │  Hub DC  │
  └──┬───┬───┘
     │   │   │
   ┌─┴─┐ ┌─┴─┐ ┌─┴─┐
   │B1 │ │B2 │ │B3 │
   └───┘ └───┘ └───┘

Full Mesh (N*(N-1)/2 circuits)
  ┌───┐───┌───┐
  │S1 │───│S2 │
  └───┘   └───┘
    │\     /│
    │ \   / │
    │  \ /  │
  ┌───┐   ┌───┐
  │S3 │───│S4 │
  └───┘   └───┘

Partial Mesh (SD-WAN overlay)
  ┌──────────┐
  │  DC1     │────┐
  └──────────┘    │     ┌──────────┐
                   ├─────│  DC2     │
  ┌──────────┐    │     └──────────┘
  │  BRANCH  │────┘
  └──────────┘
```

### SD-WAN Design

```bash
# Cisco SD-WAN (vManage)
# Template de configuration circuit
vpn 0
  interface ge0/0
    ip address 10.0.1.1/24
    tunnel-interface
      encapsulation ipsec
      color biz-internet
      allow-service all
    !
  interface ge0/1
    ip address 10.0.2.1/24
    tunnel-interface
      encapsulation ipsec
      color lte
      allow-service all
  !
vpn 10
  interface vlan10
    ip address 192.168.10.1/24
    nat-pool 203.0.113.1/32
  !
  ip route 0.0.0.0/0 vpn 0
!
policy
  app-route-policy BEST-PATH
    vpn-list ALL
      sequence 10
        match
          app-list CRITICAL-APPS
        action
          backup-preferred-color biz-internet
          preferred-color lte
```

---

## Haute Disponibilité (HA)

### Redondance L2

```text
STP (802.1D) → RSTP (802.1w) → MSTP (802.1s)
├── Root bridge placement
├── PortFast pour les ports d'accès
├── BPDU Guard pour bloquer les bridges non autorisés
└── Loop Guard / UDLD pour fibres

Stacking (Cisco StackWise, Arista MLAG)
├── Gestion unique
├── Spanning-tree simplifié
└── Bandwidth aggégée

vPC / MLAG (multi-chassis LAG)
├── Active-Active sur deux switches
├── Pas de STP nécessaire
├── Utilisation complète de la bande passante
└── Bascule en sous-seconde
```

### Redondance L3

```bash
# VRRP (RFC 5798)
vrrp 100
  virtual-ip 192.168.100.1
  priority 110
  preempt
  track interface GigabitEthernet0/0/1 20

# First Hop Redundancy Protocol
# HSRP (Cisco) / VRRP (RFC) / GLBP (Cisco)

# ECMP (Equal Cost Multi-Path)
# OSPF maximum-paths 4
# BGP maximum-paths 4
# BGP bestpath as-path multipath-relax

# BFD (Bidirectional Forwarding Detection)
# Détection de panne < 50ms
interface GigabitEthernet0/0
  bfd interval 50 min_rx 50 multiplier 3
!
router ospf 1
  bfd all-interfaces
```

### N+1 / 2N Redundancy

```text
N+1:
  ├── Un équipement de plus que nécessaire
  ├── Maintenance sans interruption
  └── Perte d'un seul équipement supportée

2N:
  ├── Deux fois la capacité nécessaire
  ├── A/B indépendants
  ├── Maintenance complète d'un côté
  └── Perte de tout un côté supportée

2N+1:
  ├── Trois fois la capacité minimale
  └── A/B/C avec maintenance + panne simultanée
```

---

## Virtual Private Cloud (VPC) — Cloud

### AWS VPC Design

```hcl
# Terraform — AWS VPC Multi-AZ
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "prod-vpc" }
}

# Public subnets (AZ-A, AZ-B, AZ-C)
resource "aws_subnet" "public" {
  count                   = 3
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = element(["eu-west-1a", "eu-west-1b", "eu-west-1c"], count.index)
  map_public_ip_on_launch = true
}

# Private subnets (AZ-A, AZ-B, AZ-C)
resource "aws_subnet" "private" {
  count             = 3
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = element(["eu-west-1a", "eu-west-1b", "eu-west-1c"], count.index)
}

# NAT Gateway
resource "aws_nat_gateway" "main" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id
}

# VPC Flow Logs
resource "aws_flow_log" "main" {
  iam_role_arn    = aws_iam_role.flow_logs.arn
  log_destination = aws_cloudwatch_log_group.flow_logs.arn
  traffic_type    = "ALL"
  vpc_id          = aws_vpc.main.id
}
```

### GCP / Azure

```bash
# GCP VPC Shared VPC
gcloud compute shared-vpc enable host-project
gcloud compute shared-vpc associate-subnets \
  host-project vpc-host \
  service-project dev-project \
  --regions europe-west1

# Azure VNet Peering
az network vnet peering create \
  --name hub-to-spoke1 \
  --resource-group hub-rg \
  --vnet-name hub-vnet \
  --remote-vnet spoke1-vnet \
  --allow-vnet-access \
  --allow-forwarded-traffic
```

---

## Pièges et Bonnes Pratiques

- **Oversubscription** : DC 3:1 à 6:1, Campus 10:1 à 20:1 selon les besoins
- **MTU** : 9000 (jumbo frames) sur l'underlay DC, 1500 sur le campus/WAN
- **STP** : Toujours MSTP ou RSTP, jamais STP classique
- **VLAN** : Limiter à 256 VLANs par arbre STP, utiliser VXLAN pour plus
- **ARP** : Ne pas laisser les tables ARP exploser (> 1000 entrées par SVI)
- **QoS** : Trust boundary sur les ports d'accès, marquer au niveau distribution
- **Logging** : Centraliser tous les logs réseau (syslog, netflow, telemetry)
- **Documentation** : Diagrammes + IPAM + cabling toujours à jour

## Ressources

- Cisco Data Center Design : https://www.cisco.com/c/en/us/solutions/data-center-virtualization/
- AWS VPC Design : https://docs.aws.amazon.com/vpc/latest/userguide/
- OpenStack Networking : https://docs.openstack.org/neutron/latest/
- STP Optimization : https://www.cisco.com/c/en/us/support/docs/lan-switching/spanning-tree-protocol/