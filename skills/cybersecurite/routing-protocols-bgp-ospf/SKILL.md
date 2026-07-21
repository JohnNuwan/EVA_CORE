---
name: routing-protocols-bgp-ospf
description: Guide complet des protocoles de routage — BGP, OSPF, route-maps, redistribution, attributs BGP, zones OSPF, configuration Cisco/FRR, troubleshooting.
tags: [bgp, ospf, routing, route-map, redistribution, frr, cisco, network-protocols]
---

# Protocoles de Routage — BGP & OSPF

## Présentation

Guide complet des protocoles de routage dynamique utilisés dans les réseaux d'entreprise, data center et opérateurs. Couvre OSPF (IGP) et BGP (EGP) avec configurations, attributs, zones, redistribution et troubleshooting.

---

## OSPF — Open Shortest Path First

### Principes de Base

- **Type** : IGP (Interior Gateway Protocol), link-state
- **Algorithme** : Dijkstra (SPF) — Shortest Path First
- **Métrique** : Coût = 10^8 / bandwidth (Cisco), cumulative
- **AD** : 110 (Cisco)
- **Transport** : IP protocol 89

### Hiérarchie OSPF

```
        +----------AS---------+
        |                     |
   +----+----+          +-----+-----+
   | Area 0  |          | Area 1    |
   | (Backbone)|         |           |
   +----+----+          +-----+-----+
        |                     |
   +----+----+          +-----+-----+
   | ABR     |----------| ABR       |
   +----+----+          +-----+-----+
        |                     |
   +----+----+          +-----+-----+
   | Area 2  |          | Area 3    |
   | (Stub)  |          | (NSSA)    |
   +---------+          +-----------+
```

### Types de Routes et LSAs

| Type LSA | Nom | Propagation | Description |
|----------|-----|-------------|-------------|
| Type 1 | Router LSA | Intrazone | Liens du routeur |
| Type 2 | Network LSA | Intrazone | Réseau DR |
| Type 3 | Summary LSA | Interzone | Routes résumées |
| Type 4 | ASBR Summary LSA | Interzone | Routes vers ASBR |
| Type 5 | External LSA | Tout sauf stub | Routes externes |
| Type 7 | NSSA LSA | NSSA | Routes externes en NSSA |

### Zones OSPF

```text
Area 0 (Backbone)
    └── Routeur ABR obligatoire
        ├── Area normale
        ├── Stub Area — Pas de LSA Type 5, défaut par ABR
        ├── Totally Stub Area — Pas de LSA 3/4/5
        └── NSSA — Pas de LSA Type 5 mais Type 7 autorisé
```

### Configuration OSPF (FRR / Cisco)

```bash
# FRR (Free Range Routing) — /etc/frr/frr.conf
!
router ospf
  router-id 10.0.0.1
  passive-interface default
  no passive-interface eth0
  network 10.0.0.0/24 area 0
  network 192.168.1.0/24 area 1
  area 1 stub
  area 2 nssa
  default-information originate always
  redistribute connected metric-type 1
  redistribute static metric-type 2
  maximum-paths 4
!
interface eth0
  ip ospf cost 10
  ip ospf hello-interval 10
  ip ospf dead-interval 40
  ip ospf network point-to-point
  ip ospf authentication message-digest
  ip ospf message-digest-key 1 md5 secret
!
```

```bash
# Cisco IOS
router ospf 1
 router-id 10.0.0.1
 network 10.0.0.0 0.0.0.255 area 0
 network 192.168.1.0 0.0.0.255 area 1
 area 1 stub
 area 2 nssa
 default-information originate always
 redistribute connected subnets metric-type 1
 redistribute static subnets metric-type 2
 maximum-paths 4
!
interface GigabitEthernet0/0
 ip ospf cost 10
 ip ospf hello-interval 10
 ip ospf dead-interval 40
 ip ospf network point-to-point
 ip ospf authentication message-digest
 ip ospf message-digest-key 1 md5 0 secret
!
```

### Commandes de Troubleshooting OSPF

```bash
# État OSPF
vtysh -c "show ip ospf"
vtysh -c "show ip ospf interface"
vtysh -c "show ip ospf neighbor"
vtysh -c "show ip ospf database"
vtysh -c "show ip ospf route"

# Cisco
show ip ospf
show ip ospf interface
show ip ospf neighbor detail
show ip ospf database
show ip route ospf
debug ip ospf adj
debug ip ospf events
```

### Types de Réseaux OSPF

```text
broadcast      → DR/BDR election, hello 10s, dead 40s (Ethernet)
non-broadcast  → DR/BDR, neighbors manuels (Frame Realy)
point-to-point → Pas de DR/BDR, hello 10s, dead 40s (PPP)
point-to-multipoint → Pas de DR/BDR, hello 30s, dead 120s
```

### Optimisations OSPF

```bash
# Élagage SPF
timers throttle spf 200 1000 10000
# 200ms délai initial, 1s incrément, 10s max

# Résumé de routes interzone
area 1 range 192.168.0.0/22

# Virtual link (zone 0 disjointe)
area 1 virtual-link 10.0.0.2

# Filter-list
area 1 filter-list prefix OUT_PREFIX in
```

---

## BGP — Border Gateway Protocol

### Principes de Base

- **Type** : EGP (Exterior Gateway Protocol), path-vector
- **Algorithme** : Best Path Selection (attributs)
- **Métrique** : Multi-exit discriminator (MED)
- **AD** : 20 (eBGP), 200 (iBGP)
- **Transport** : TCP port 179
- **Version** : BGP-4 (RFC 4271)

### Types de Sessions

```text
eBGP (External BGP)
  ├── Entre différents AS
  ├── TTL=1 par défaut
  ├── Next-hop change (par défaut)
  └── Routes redistribuées par défaut

iBGP (Internal BGP)
  ├── Même AS
  ├── TTL=255 (loopback)
  ├── Next-hop préservé
  └── Full-mesh requis (ou route-reflector)
```

### Attributs BGP et Best Path Selection

| # | Attribut | Description | Type |
|---|----------|-------------|------|
| 1 | **Weight** | Cisco propriétaire, local au routeur | Optionnel |
| 2 | **Local Preference** | Préférence sortie de l'AS | Well-known |
| 3 | **Originate locally** | Route générée localement | Well-known |
| 4 | **AS Path** | Longueur du chemin d'AS | Well-known |
| 5 | **Origin** | IGP > EGP > Incomplete | Well-known |
| 6 | **MED** | Métrique entrante dans l'AS | Optionnel |
| 7 | **eBGP > iBGP** | Chemin externe prioritaire | — |
| 8 | **Next hop** | Métrique IGP vers next-hop | — |
| 9 | **RID le plus bas** | Tie-break final | — |

### Configuration BGP (FRR)

```bash
# /etc/frr/frr.conf
!
router bgp 65001
  bgp router-id 10.0.0.1
  bgp bestpath as-path multipath-relax
  bgp log-neighbor-changes
  no bgp default ipv4-unicast
  !
  neighbor 192.168.1.2 remote-as 65002
  neighbor 192.168.1.2 description eBGP-AS65002
  neighbor 192.168.1.2 ebgp-multihop 2
  neighbor 192.168.1.2 update-source 10.0.0.1
  neighbor 192.168.1.2 password secureBGPpass
  neighbor 192.168.1.2 timers 3 9
  !
  neighbor 10.0.0.2 remote-as 65001
  neighbor 10.0.0.2 description iBGP-R2
  neighbor 10.0.0.2 update-source 10.0.0.1
  !
  address-family ipv4 unicast
    network 10.0.1.0/24
    network 10.0.2.0/24 route-map ADVERTISE_MAP
    neighbor 192.168.1.2 activate
    neighbor 192.168.1.2 route-map INGRESS_FILTER in
    neighbor 192.168.1.2 route-map EGRESS_FILTER out
    neighbor 192.168.1.2 prefix-list ALLOWED in
    neighbor 192.168.1.2 maximum-prefix 10000 90 restart 30
    neighbor 10.0.0.2 activate
    neighbor 10.0.0.2 route-reflector-client
    neighbor 10.0.0.2 next-hop-self
  exit-address-family
  !
  address-family ipv6 unicast
    network 2001:db8::/32
    neighbor 2001:db8::1 activate
  exit-address-family
!
ip prefix-list ALLOWED seq 5 permit 10.0.0.0/8 le 24
ip prefix-list ALLOWED seq 10 deny 0.0.0.0/0 le 32
!
route-map INGRESS_FILTER permit 10
  match ip address prefix-list ALLOWED
  set local-preference 150
  set metric 50
!
route-map EGRESS_FILTER permit 10
  match ip address prefix-list CUSTOMER
  set as-path prepend 65001 65001
  set community 65001:100
!
```

### Configuration BGP (Cisco IOS)

```bash
router bgp 65001
 bgp router-id 10.0.0.1
 bgp log-neighbor-changes
 no bgp default ipv4-unicast
 neighbor 192.168.1.2 remote-as 65002
 neighbor 192.168.1.2 ebgp-multihop 2
 neighbor 192.168.1.2 update-source Loopback0
 neighbor 192.168.1.2 password BGPpass
 neighbor 192.168.1.2 timers 3 9
 neighbor 10.0.0.2 remote-as 65001
 neighbor 10.0.0.2 update-source Loopback0
 !
 address-family ipv4
  network 10.0.0.0 mask 255.255.255.0
  neighbor 192.168.1.2 activate
  neighbor 192.168.1.2 route-map FILTER_IN in
  neighbor 192.168.1.2 prefix-list ALLOW out
  neighbor 192.168.1.2 maximum-prefix 10000 80
  neighbor 10.0.0.2 activate
  neighbor 10.0.0.2 next-hop-self
  neighbor 10.0.0.2 route-reflector-client
 exit-address-family
!
ip prefix-list ALLOW seq 5 permit 10.0.0.0/8 le 24
!
route-map FILTER_IN permit 10
 match ip address prefix-list ALLOW
 set local-preference 200
 set community 65001:100
```

### Route-Reflector et Confederation

```text
Route-Reflector (RR)
    ├── Client RR → reçoit et envoie à tous les clients
    ├── Non-client → full mesh requis
    ├── Cluster-list → prévention de boucle
    └── Originator-id → identifie le routeur d'origine

BGP Confederation
    ├── AS subdivisé en sous-AS
    ├── eBGP entre sous-AS
    ├── MED et LP préservés
    └── Next-hop non modifié
```

### Communities BGP

```bash
# Communities well-known
NO_EXPORT (0xFFFFFF01)  # Pas d'export hors confederation
NO_ADVERTISE (0xFFFFFF02) # Pas d'annonce à aucun voisin
NO_EXPORT_SUBCONFED (0xFFFFFF03) # Pas d'export hors sous-AS

# Configuration
route-map SET_COMMUNITY permit 10
 set community 65001:100 65001:200
 set large-community 65001:1:1000
!

# Filtrage par community
ip community-list standard MY_COMMUNITY permit 65001:100
!
route-map COMMUNITY_FILTER permit 10
 match community MY_COMMUNITY
!
neighbor 192.168.1.2 route-map COMMUNITY_FILTER in
```

### Multihoming BGP

```bash
# Bascule actif/passif
route-map SET_PREF permit 10
  set as-path prepend 65001 65001 65001  # Allonger AS-PATH pour désavantager
!
route-map SET_MED permit 10
  set metric 100  # MED plus élevé = moins préféré
!

# Load balancing
maximum-paths 4  # Équilibrage eBGP multipath
bgp bestpath as-path multipath-relax  # AS-PATH de longueur différente OK
```

### Troubleshooting BGP

```bash
# Vérifications FRR
vtysh -c "show bgp summary"
vtysh -c "show bgp neighbors 192.168.1.2"
vtysh -c "show bgp neighbors 192.168.1.2 received-routes"
vtysh -c "show bgp neighbors 192.168.1.2 advertised-routes"
vtysh -c "show bgp ipv4 unicast"
vtysh -c "show bgp ipv4 unicast 10.0.1.0/24"
vtysh -c "show bgp community 65001:100"
vtysh -c "debug bgp updates"
vtysh -c "debug bgp keepalives"

# Cisco
show ip bgp summary
show ip bgp neighbors 192.168.1.2
show ip bgv neighbors 192.168.1.2 received-routes
show ip bgp
show ip bgp 10.0.1.0/24
show ip route bgp
debug ip bgp updates
```

### RPKI et BGPsec

```bash
# RPKI — Validation des origines AS
# Config côté FRR
router bgp 65001
  bgp rpki server 192.168.1.100 port 323 tcp
  bgp rpki server rpki.ripe.net port 323 tcp
  !
  address-family ipv4 unicast
    bgp rpki table
    neighbor 192.168.1.2 rpki table
    route-map RPKI_FILTER in
  exit-address-family
!
route-map RPKI_FILTER permit 10
  match rpki valid
  set local-preference 200
!
route-map RPKI_FILTER deny 20
  match rpki invalid
!

# Vérification
show bgp rpki table
show bgp ipv4 unicast 10.0.1.0/24 rpki
```

### BGP Flowspec

```bash
# Mitigation DDoS via BGP Flowspec
router bgp 65001
  address-family ipv4 flowspec
    neighbor 192.168.1.2 activate
    neighbor 192.168.1.2 route-map FLOWSPEC in
  exit-address-family
!
# Annonce Flowspec
ip bgp flowspec destination 10.0.0.0/24 source 192.0.2.0/24
  action drop-rate 100
```

---

## Redistribution entre OSPF et BGP

```bash
router bgp 65001
  address-family ipv4 unicast
    redistribute ospf metric 100
    redistribute connected route-map CONN_TO_BGP
  exit-address-family
!
router ospf
  redistribute bgp metric-type 1 subnets
  default-information originate always
  distance ospf external 110
!
route-map CONN_TO_BGP permit 10
  match interface lo
  set metric 100
!
route-map CONN_TO_BGP deny 20
  match interface docker*
!
```

---

## Pièges et Bonnes Pratiques

### OSPF
- **Router-ID** : Toujours définir manuellement (basé sur loopback)
- **Passive interface** : Mettre les interfaces LAN en passive
- **Network type** : Utiliser point-to-point sur les liens point-à-point
- **MTU mismatch** : Cause fréquente de voisinage bloqué à ExStart
- **Authentication** : Toujours activer MD5 ou SHA sur les messages OSPF
- **Stub areas** : Ne pas redistribuer de routes externes dans une stub

### BGP
- **Maximum prefix** : Toujours configurer pour éviter les fuites
- **TTL Security** : Utiliser `ebgp-multihop` avec GTSM (Generalized TTL Security Mechanism)
- **Route-map par défaut** : Ne pas utiliser `neighbor default-originate` sans filtre
- **Peer groups** : Grouper les voisins pour configuration cohérente
- **BGP timers** : 3/9s pour DC, 30/90s pour WAN
- **Next-hop-self** : Nécessaire en iBGP si next-hop non accessible
- **Add-path** : Activer `bgp addpath-tx all-paths` pour visibilité multi-path

## Ressources

- RFC 4271 (BGP-4) : https://datatracker.ietf.org/doc/rfc4271/
- RFC 2328 (OSPFv2) : https://datatracker.ietf.org/doc/rfc2328/
- FRR Documentation : https://docs.frrouting.org/
- BGP Best Practices (Cisco) : https://www.cisco.com/c/en/us/support/docs/ip/border-gateway-protocol-bgp/26619-best-bgp.html
- RIPE RPKI : https://www.ripe.net/manage-ips-and-asns/resource-management/rpki
- BGP Security (MANRS) : https://www.manrs.org/