---
name: sdn-networking-guide
description: Guide complet du Software-Defined Networking (SDN) — OpenFlow, contrôleurs SDN, Cisco ACI, VMware NSX, SD-WAN, API REST et automation réseau programmatique.
tags: [sdn, openflow, cisco-aci, vmware-nsx, sd-wan, network-virtualization, controller, netconf, yang, restconf]
---

# SDN — Software-Defined Networking

## Présentation

Le SDN dissocie le plan de contrôle (control plane) du plan de données (data plane), centralisant l'intelligence réseau dans un contrôleur logiciel. Architecture en trois couches :

```
┌──────────────────────────────────────┐
│      Application Layer               │
│  Orchestration  │  Analyse  │  Billing│
│  (OpenStack)    │  (ELK)    │  (OSS)  │
└────────┬─────────────────────────────┘
         │ API Northbound (REST, RESTCONF, gRPC)
┌────────v──────────────────────────────┐
│      Control Layer (SDN Controller)   │
│  OpenDaylight  │  ONOS  │  Ryu       │
│  Floodlight    │  Cisco APIC         │
└────────┬──────────────────────────────┘
         │ API Southbound (OpenFlow, NETCONF, SNMP)
┌────────v──────────────────────────────┐
│      Infrastructure Layer             │
│  [Switch] [Routeur] [FW] [AP]        │
│  (Plans de données programmables)     │
└───────────────────────────────────────┘
```

---

## OpenFlow — Le Protocole Fondateur

### Principe

OpenFlow (OF 1.0 → 1.5) permet au contrôleur d'écrire des **flow entries** dans la **flow table** du switch. Chaque entrée = match + instructions.

```
Paquet entrant
    │
    v
[Flow Table 0] ──miss──> [Table 1] ──miss──> [Table N]
    │   │                        │
    │   └── Action: forward      │
    │       (output:port1)       └── Packet-In au Controller
    │
    └── Goto-Table: 1
```

### Flow Entry (OpenFlow 1.3+)

| Champ | Description |
|-------|-------------|
| **Match Fields** | Ingress Port, ETH src/dst, ETH type, VLAN, IP src/dst, IP proto, TCP/UDP ports, MPLS, PBB, Tunnel ID |
| **Priority** | Plus haute priorité gagne (0-65535) |
| **Counters** | Paquets, bytes, durée |
| **Instructions** | Apply-Actions, Clear-Actions, Write-Actions, Goto-Table, Meter, Experimenter |
| **Timeouts** | Idle (supprime si inactif), Hard (supprime après durée) |
| **Cookie** | Identifiant opaque pour le contrôleur |
| **Flags** | OFPFF_SEND_FLOW_REM (notification de suppression) |

### Exemple de Flow (Ryu Controller — Python)

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3

class SimpleSwitchSDN(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mac_to_port = {}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, MAIN_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Flow par défaut : envoyer au contrôleur
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority,
            match=match, instructions=inst,
            idle_timeout=30, hard_timeout=0)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = msg.match['in_port']
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)]
        data = msg.data if msg.buffer_id == ofproto.OFP_NO_BUFFER else None
        out = parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id,
            in_port=msg.match['in_port'], actions=actions, data=data)
        datapath.send_msg(out)
```

### OpenFlow via ovs-ofctl (Open vSwitch)

```bash
# Créer un bridge openflow
ovs-vsctl add-br br-sdn
ovs-vsctl set bridge br-sdn protocols=OpenFlow13

# Connecter au contrôleur SDN
ovs-vsctl set-controller br-sdn tcp:192.168.1.100:6653

# Lister les flow tables
ovs-ofctl -O OpenFlow13 dump-flows br-sdn

# Ajouter une flow entry
ovs-ofctl -O OpenFlow13 add-flow br-sdn \
  "priority=100,ip,nw_src=10.0.1.0/24,nw_dst=10.0.2.0/24,actions=output:1"

# Flow avec timeout
ovs-ofctl -O OpenFlow13 add-flow br-sdn \
  "priority=200,tcp,tp_dst=80,idle_timeout=60,actions=output:2"

# Supprimer une flow
ovs-ofctl -O OpenFlow13 del-flows br-sdn "priority=100"
```

---

## Contrôleurs SDN Open Source

### OpenDaylight (ODL)

Architecture modulaire (MD-SAL) avec support YANG/NETCONF.

```bash
# Installation ODL (distribution Oxygen +)
wget https://nexus.opendaylight.org/content/repositories/opendaylight.release/org/opendaylight/integration/karaf/0.11.0/karaf-0.11.0.tar.gz
tar xvf karaf-*.tar.gz && cd karaf-*/

# Démarrer Karaf
./bin/karaf

# Installer les features SDN
feature:install odl-restconf odl-l2switch-switch odl-mdsal-apidocs
feature:install odl-openflowplugin-flow-services odl-dluxapps-applications

# API REST — Ajouter un flow
curl -u admin:admin -X PUT \
  -H "Content-Type: application/json" \
  -d '{
    "flow": [{
      "id": "1",
      "match": {
        "ethernet-match": {"ethernet-type": {"type": 2048}},
        "ipv4-destination": "10.0.0.0/24"
      },
      "instructions": {
        "instruction": [{
          "order": 0,
          "apply-actions": {
            "action": [{"order": 0, "output-action": {"output-node-connector": "1"}}]
          }
        }]
      }
    }]
  }' \
  http://localhost:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/table/0/flow/1

# Voir les flows
curl -u admin:admin http://localhost:8181/restconf/operational/opendaylight-inventory:nodes/
```

### ONOS (Open Network Operating System)

Conçu pour les opérateurs, haute disponibilité, clustering.

```bash
# Installation
wget https://onosproject.org/release/onos-2.7.0.tar.gz
tar xvf onos-*.tar.gz && cd onos-*/
./bin/onos-service start

# CLI ONOS
./bin/onos localhost
# > apps -a | grep -i forwarding
# > flows -s
# > hosts
# > intents

# Ajouter un intent (host-to-host via REST)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "type": "HostToHostIntent",
    "appId": "org.onosproject.cli",
    "one": "00:00:00:00:00:01/None",
    "two": "00:00:00:00:00:02/None"
  }' \
  http://localhost:8181/onos/v1/intents
```

### Ryu — Framework SDN Python

```python
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp

class FirewallSDN(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.blocked_ips = {"10.0.0.99", "10.0.0.100"}

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, MAIN_DISPATCHER)
    def features_handler(self, ev):
        dp = ev.msg.datapath
        parser = dp.ofproto_parser
        # Bloquer les IP malveillantes
        for ip in self.blocked_ips:
            match = parser.OFPMatch(eth_type=0x0800, ipv4_src=ip)
            actions = []  # drop
            self._add_flow(dp, 100, match, actions)
        # Traffic normal -> controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(dp.ofproto.OFPP_CONTROLLER)]
        self._add_flow(dp, 0, match, actions)

    def _add_flow(self, dp, priority, match, actions):
        inst = [dp.ofproto_parser.OFPInstructionActions(
            dp.ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = dp.ofproto_parser.OFPFlowMod(
            datapath=dp, priority=priority, match=match, instructions=inst)
        dp.send_msg(mod)
```

---

## Cisco ACI (Application Centric Infrastructure)

### Architecture

```
┌────────────────────────────────────────┐
│         APIC Controller Cluster        │
│  (3 nœuds, active-active, 50-80ms RTT)│
└─────┬──────────────┬───────────────────┘
      │              │
┌─────v──────┐ ┌─────v──────┐ ┌─────v──────┐
│ Leaf 101   │ │ Spine 1    │ │ Leaf 102   │
│ (VTEP)     │─┤ (BGP RR)   ├─│ (VTEP)     │
└────────────┘ └────────────┘ └────────────┘
      │                            │
  [Serveurs]                  [Serveurs]
```

### Concepts ACI

| Terme | Description |
|-------|-------------|
| **Tenant** | Conteneur logique isolé (client, département) |
| **VRF** | Context de routage (L3) |
| **Bridge Domain (BD)** | Domaine L2 avec sous-réseau |
| **EPG** | Endpoint Group — groupe d'endpoints avec même politique |
| **Contract** | Règle de communication entre EPGs |
| **Filter** | Filtre L4 (TCP/80, ICMP, etc.) |
| **BD-FD** | Bridge Domain Forwarding — Forwarding Anycast GW MAC |

### Configuration ACI (via APIC REST API)

```bash
# Créer un Tenant
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "fvTenant": {
      "attributes": {"name": "Tenant-Prod", "descr": "Production"}
    }
  }' \
  https://apic-ip/api/node/mo/uni/tn-Tenant-Prod.json

# Créer un VRF
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "fvCtx": {
      "attributes": {
        "name": "VRF-Prod",
        "dn": "uni/tn-Tenant-Prod/ctx-VRF-Prod"
      }
    }
  }' \
  https://apic-ip/api/node/mo/uni/tn-Tenant-Prod/ctx-VRF-Prod.json

# Créer un Bridge Domain
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "fvBD": {
      "attributes": {
        "name": "BD-Web",
        "dn": "uni/tn-Tenant-Prod/BD-BD-Web",
        "arpFlood": "yes"
      },
      "children": [{
        "fvSubnet": {
          "attributes": {
            "ip": "10.0.1.1/24",
            "scope": "public",
            "preferred": "yes",
            "virtual": "yes"
          }
        }
      }]
    }
  }' \
  https://apic-ip/api/node/mo/uni/tn-Tenant-Prod/BD-BD-Web.json

# Créer un EPG et le lier au Contract
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "fvAEPg": {
      "attributes": {
        "name": "EPG-Web",
        "dn": "uni/tn-Tenant-Prod/ap-App-Prod/epg-EPG-Web"
      },
      "children": [{
        "fvRsBd": {"attributes": {"tnFvBDName": "BD-Web"}}
      }]
    }
  }' \
  https://apic-ip/api/node/mo/uni/tn-Tenant-Prod/ap-App-Prod/epg-EPG-Web.json
```

### Vérifications ACI

```bash
# CLI APIC (ssh ou console)
moquery -c fvTenant
moquery -c fvBD -p 'uni/tn-Tenant-Prod/'
moquery -c fvCEp -p 'uni/tn-Tenant-Prod/'
moquery -c fvRsProv -p 'uni/tn-Tenant-Prod/'

# Vérifier les EPG endpoints
icurl -k 'https://apic/api/class/fvCEp.json'

# Voir les endpoints appris
icurl -k 'https://apic/api/node/class/fvCEp.json?query-target-filter=eq(fvCEp.ip,"10.0.1.10")'
```

---

## VMware NSX — Virtualisation Réseau

### Architecture NSX-T (v4.x)

```
┌────────────────────────────────────────────┐
│           NSX Manager Cluster              │
│   (3 nœuds, API REST, UI, Policy)         │
└────┬────────────┬─────────────┬────────────┘
     │            │             │
┌────v────┐ ┌────v────┐ ┌─────v──────┐
│ Edge-1  │ │ Edge-2  │ │ Transport  │
│ (ECMP)  │ │ (ECMP)  │ │ Zones      │
└────┬────┘ └────┬────┘ └─────┬──────┘
     │            │             │
     └────────────┴─────────────┘
                     │
             ┌───────v────────┐
             │    ESXi / KVM   │
             │ (VDS / N-VDS)  │
             │  ┌──────────┐   │
             │  │ TEP 10/1 │   │
             │  │ Geneve   │   │
             │  └──────────┘   │
             └─────────────────┘
```

### Concepts NSX-T

| Terme | Description |
|-------|-------------|
| **TEP** | Tunnel Endpoint — IP de transport pour Geneve |
| **Geneve** | Protocole de tunnel NSX (over UDP, remplace VXLAN) |
| **Segment** | Réseau L2 virtuel (équivaut à VNI) |
| **Segment Profile** | Politique QoS, sécurité, MTU par segment |
| **Tier-0 Gateway** | Router L3 frontière (BGP vers physique) |
| **Tier-1 Gateway** | Router L3 locataire (connecté à T0) |
| **DFW** | Distributed Firewall — au niveau hyperviseur |
| **LB** | Load Balancer (L4/L7, intégré) |
| **VPN** | IPSec VPN, L2VPN |

### Configuration NSX-T (via API REST)

```bash
# Créer un Segment
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "display_name": "segment-web",
    "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/zone-uuid",
    "subnets": [{
      "gateway_address": "10.0.1.1/24",
      "dhcp_ranges": ["10.0.1.100-10.0.1.200"]
    }]
  }' \
  https://nsx-manager/policy/api/v1/infra/segments/segment-web

# Créer un Tier-1 Gateway
curl -X PUT -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "display_name": "tier1-web",
    "tier0_path": "/infra/tier-0s/tier0-dc",
    "route_advertisement_types": ["STATIC_ROUTES", "CONNECTED"]
  }' \
  https://nsx-manager/policy/api/v1/infra/tier-1s/tier1-web

# Attacher le segment au Tier-1
curl -X PATCH -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "display_name": "segment-web-connect",
    "connectivity_path": "/infra/tier-1s/tier1-web"
  }' \
  https://nsx-manager/policy/api/v1/infra/segments/segment-web

# Créer une règle DFW
curl -X POST -k \
  -H "Content-Type: application/json" \
  -u admin:password \
  -d '{
    "display_name": "Allow-HTTP-to-Web",
    "source_groups": ["/infra/domains/default/groups/group-web"],
    "destination_groups": ["/infra/domains/default/groups/group-app"],
    "services": ["/infra/services/HTTP"],
    "action": "ALLOW",
    "scope": ["/infra/domains/default/groups/group-web"]
  }' \
  https://nsx-manager/policy/api/v1/infra/domains/default/security-policies/allow-http/rules/rule-1
```

### CLI NSX (via nsxcli ou API)

```bash
# Vérifier les overlay
nsxcli -c get logical-switches
nsxcli -c get logical-routers
nsxcli -c get transport-nodes

# Vérifier BGP
nsxcli -c get bgp neighbor
nsxcli -c get bgp routes

# Voir les flux DFW
nsxcli -c get firewall rule-stats
nsxcli -c get flow trace --src-ip 10.0.1.10 --dst-ip 10.0.2.10
```

---

## SD-WAN

### Architecture Cisco SD-WAN (Viptela)

```
┌─────────────────────────────────────────────┐
│           vManage (Orchestrateur)            │
├─────────────────────────────────────────────┤
│           vBond (Authentication)             │
├─────────────────────────────────────────────┤
│           vSmart (Contrôleur de routes)       │
├──────────┬──────────┬──────────┬────────────┤
│  vEdge   │  vEdge   │  cEdge   │  cEdge     │
│  (site)  │  (site)  │  (site)  │  (site)    │
└──────────┴──────────┴──────────┴────────────┘
         │          │           │
    --- MPLS --- Internet --- LTE --- (Transport)
```

### Concepts SD-WAN Cisco

| Terme | Description |
|-------|-------------|
| **vEdge** | Routeur SD-WAN physique/virtuel |
| **cEdge** | Routeur ISR/ASR Catalyst avec SD-WAN |
| **TLOC** | Transport Location (IP + couleur) |
| **OMP** | Overlay Management Protocol — routes, TLOCs, services |
| **vSmart** | Contrôleur distribuant les policies OMP |
| **vBond** | Authentification et NAT traversal |
| **vManage** | Dashboard centralisé de gestion |

### Configuration SD-WAN (CLI vEdge)

```bash
# Configuration système
system
 host-name site-paris-01
 system-ip 10.0.0.1
 site-id 101
 organization-name "EVA-Networks"
 vbond 192.168.200.1 port 12346
 vbootstrap
!
# Interface de transport
vpn 0
 interface ge0/0
  ip address 203.0.113.1/30
  no shutdown
  tunnel-interface
   encapsulation ipsec
   color public-internet
   allow-service all
   allow-service dhcp
   allow-service dns
   no allow-service icmp
  !
  nat-peer
   respond-to-vpn 0
  !
 !
 ip route 0.0.0.0/0 203.0.113.2
!
# Interface LAN (VPN 10)
vpn 10
 interface ge0/1
  ip address 192.168.10.1/24
  no shutdown
 !
 router
  ospf
   redistribute omp
   redistribute connected
   network 192.168.10.0/24 area 0
  !
 ip route 0.0.0.0/0 vpn 0
!
# Politique OMP : priorité MPLS sur Internet
policy
 lists
  color internet
   color internet
  color mpls
   color mpls
 !
 control-policy PREFER_MPLS
  sequence 10
   match tloc color internet
    action reject
   !
  !
  default-action accept
 !
 apply-policy
  site-list ALL_SITES control-policy PREFER_MPLS out
 !
!
```

### SD-WAN via API vManage

```bash
# Authentification
TOKEN=$(curl -sk -X POST \
  -H "Content-Type: application/json" \
  -d '{"j_username":"admin","j_password":"password"}' \
  https://vmanage-ip/j_security_check \
  -c /tmp/cookies.txt -D - | grep XSRF | sed 's/.* //')

# Lister les vEdges
curl -sk \
  -H "X-XSRF-TOKEN: $TOKEN" \
  -b /tmp/cookies.txt \
  https://vmanage-ip/dataservice/device

# Voir les tunnels OMP
curl -sk \
  -H "X-XSRF-TOKEN: $TOKEN" \
  -b /tmp/cookies.txt \
  https://vmanage-ip/dataservice/device/omp/tunnels

# Appliquer une politique
curl -sk -X POST \
  -H "X-XSRF-TOKEN: $TOKEN" \
  -H "Content-Type: application/json" \
  -b /tmp/cookies.txt \
  -d '{
    "policyName": "QoS_Voice",
    "policyType": "qos",
    "policyDescription": "Priorité voix sur MPLS",
    "sequences": [{
      "seqId": 1,
      "seqName": "Match-Voice",
      "seqType": "qos",
      "match": [{"type": "app", "value": ["voice"]}],
      "actions": [{"type": "set", "parameter": "forwardingClass", "value": "EF"}]
    }]
  }' \
  https://vmanage-ip/dataservice/template/policy/qos
```

---

## NETCONF / YANG / RESTCONF

### Modélisation YANG

```yang
module eva-sdn {
  yang-version 1.1;
  namespace "urn:eva:params:xml:ns:yang:eva-sdn";
  prefix eva-sdn;

  import ietf-interfaces { prefix if; }
  import ietf-inet-types { prefix inet; }

  description "Modèle YANG EVA pour configuration SDN";

  container sdn-config {
    leaf controller-ip {
      type inet:ipv4-address;
      default "192.168.1.100";
    }
    leaf controller-port {
      type inet:port-number;
      default 6653;
    }
    leaf openflow-version {
      type enumeration {
        enum "1.0";
        enum "1.3";
        enum "1.4";
        enum "1.5";
      }
      default "1.3";
    }
    list flow-rules {
      key "flow-id";
      leaf flow-id {
        type uint16;
      }
      leaf priority {
        type uint16;
        default 100;
      }
      leaf idle-timeout {
        type uint16;
        default 30;
      }
      container match {
        leaf src-ip {
          type inet:ipv4-prefix;
        }
        leaf dst-ip {
          type inet:ipv4-prefix;
        }
        leaf dst-port {
          type inet:port-number;
        }
        leaf ip-proto {
          type enumeration {
            enum "tcp";
            enum "udp";
            enum "icmp";
          }
        }
      }
      container action {
        leaf output-port {
          type uint8;
        }
        leaf drop {
          type empty;
        }
      }
    }
  }
}
```

### Configuration via NETCONF (yc/ncclient)

```bash
# Via yc (YANG CLI)
yc --server 192.168.1.1 --user admin --password pass \
  --edit-config running < /tmp/sdn-config.xml

# Exemple XML
```
```xml
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>GigabitEthernet0/0/0</name>
      <type xmlns:ianaif="urn:ietf:params:xml:ns:yang:iana-if-type">
        ianaif:ethernetCsmacd
      </type>
      <enabled>true</enabled>
      <ipv4 xmlns="urn:ietf:params:xml:ns:yang:ietf-ip">
        <address>
          <ip>10.0.0.1</ip>
          <netmask>255.255.255.0</netmask>
        </address>
      </ipv4>
    </interface>
  </interfaces>
</config>
```

```python
# ncclient Python
from ncclient import manager

with manager.connect(
    host="192.168.1.1",
    port=830,
    username="admin",
    password="pass",
    hostkey_verify=False,
    device_params={'name': 'csr'}
) as m:
    # Récupérer la configuration
    result = m.get_config(source='running')
    print(result.xml)

    # Éditer la configuration
    config = '''
    <config>
      <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
        <interface>
          <GigabitEthernet>
            <name>0/0/0</name>
            <description>SDN Managed Port</description>
          </GigabitEthernet>
        </interface>
      </native>
    </config>
    '''
    m.edit_config(target='running', config=config)

    # Valider
    m.validate(source='candidate')

    # Committer
    m.commit()
```

### RESTCONF (HTTP sur YANG)

```bash
# RESTCONF sur Cisco IOS-XE
curl -k -u admin:pass \
  https://192.168.1.1/restconf/data/ietf-interfaces:interfaces

# GET spécifique
curl -k -u admin:pass \
  https://192.168.1.1/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F0

# PATCH (modification partielle)
curl -k -X PATCH \
  -u admin:pass \
  -H "Content-Type: application/yang-data+json" \
  -d '{
    "ietf-interfaces:interface": {
      "name": "GigabitEthernet0/0/0",
      "description": "SDN-Managed",
      "enabled": true,
      "ietf-ip:ipv4": {
        "address": [{"ip": "10.0.0.1", "netmask": "255.255.255.0"}]
      }
    }
  }' \
  https://192.168.1.1/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet0%2F0%2F0
```

---

## Cas d'Usage Avancés

### QoE Monitoring via SDN

```python
# Ryu — Collecte de statistiques de flux
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
import threading
import time

class SdnMonitor(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.start()

    @set_ev_cls(ofp_event.EventOFPStateChange, MAIN_DISPATCHER)
    def state_change(self, ev):
        self.datapaths[ev.datapath.id] = ev.datapath

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            time.sleep(10)

    def _request_stats(self, dp):
        parser = dp.ofproto_parser
        req = parser.OFPFlowStatsRequest(dp)
        dp.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def flow_stats_reply(self, ev):
        for stat in ev.msg.body:
            print(f"Flow: match={stat.match} "
                  f"packets={stat.packet_count} "
                  f"bytes={stat.byte_count} "
                  f"duration={stat.duration_sec}s")
```

### Network Slicing (5G + SDN)

```bash
# Créer un slice réseau via OVS
ovs-vsctl add-br br-slice-1
ovs-vsctl set bridge br-slice-1 \
  other_config:datapath_type=netdev

# VLAN tagging pour isolation
ovs-ofctl add-flow br-slice-1 \
  "priority=100,in_port=1,actions=mod_vlan_vid:100,output:2"

# QoS par slice (min=100Mbps, max=1Gbps)
ovs-vsctl set port vxlan-slice-1 qos=@qos -- \
  --id=@qos create qos type=linux-htb \
    other-config:max-rate=1000000000 \
    queues:0=@queue0 -- \
  --id=@queue0 create queue \
    other-config:min-rate=100000000 \
    other-config:max-rate=1000000000

# Meter OpenFlow pour limiter débit
ovs-ofctl add-meter br-slice-1 \
  "meter=1 kbps stats bands=type=drop rate=50000"
ovs-ofctl add-flow br-slice-1 \
  "priority=200,ip,nw_src=10.0.0.0/24,actions=meter:1,output:2"
```

---

## Pièges et Bonnes Pratiques

- **OpenFlow tables** : Les switches ont un nombre limité de flow entries (TCAM). Surveiller avec `ovs-ofctl dump-tables`.
- **Latency Controller** : Ne pas excéder 30ms RTT entre contrôleur et switches.
- **Security Control Channel** : Toujours activer TLS entre contrôleur et switches OpenFlow.
- **ACI EPG Scale** : Limiter à ~200 EPGs par tenant (au-delà, complexité d'administration croît).
- **NSX RIB/FIB** : Surveiller la mémoire des transport nodes — trop de routes BGP peut saturer.
- **SD-WAN OMP** : Éviter plus de 3000 routes OMP par vSmart.
- **YANG Model Design** : Toujours versionner les modèles YANG (namespace avec date).
- **NETCONF Session** : Limiter à 5 sessions simultanées par équipement.

## Ressources

- OpenFlow Switch Specification 1.5.1 : https://opennetworking.org/wp-content/uploads/2014/10/openflow-switch-v1.5.1.pdf
- OpenDaylight : https://www.opendaylight.org/
- ONOS : https://onosproject.org/
- Ryu SDN Framework : https://ryu-sdn.org/
- Cisco ACI Docs : https://www.cisco.com/c/en/us/support/cloud-systems-management/application-policy-infrastructure-controller-apic/products-installation-and-configuration-guides-list.html
- VMware NSX Docs : https://docs.vmware.com/en/VMware-NSX-T-Data-Center/index.html
- Cisco SD-WAN : https://sdwan-docs.cisco.com/
- RFC 6241 (NETCONF) : https://datatracker.ietf.org/doc/rfc6241/
- RFC 8040 (RESTCONF) : https://datatracker.ietf.org/doc/rfc8040/
- RFC 6020 (YANG) : https://datatracker.ietf.org/doc/rfc6020/
- Open vSwitch : https://www.openvswitch.org/
