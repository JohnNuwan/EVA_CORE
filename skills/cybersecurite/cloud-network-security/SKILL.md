---
name: cloud-network-security
description: Guide complet de sécurité réseau multi-cloud — VPC, security groups, NACL, WAF, CDN, DDoS protection, PrivateLink, VPC peering, Cloud VPN, service mesh, Zero Trust network
category: cybersecurite
---

# Cloud Network Security — AWS / GCP / Azure

---

## 1. AWS — Network Security

### VPC Architecture
```bash
# VPC de base
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --instance-tenancy default

# Subnets (public/private)
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.1.0/24 --availability-zone us-east-1a  # public
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.2.0/24 --availability-zone us-east-1a  # private

# Internet Gateway
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --internet-gateway-id igw-xxx --vpc-id vpc-xxx

# NAT Gateway
aws ec2 create-nat-gateway --subnet-id subnet-public --allocation-id eipalloc-xxx
aws ec2 create-nat-gateway --subnet-id subnet-public2 --allocation-id eipalloc-yyy  # HA

# Route Tables
aws ec2 create-route-table --vpc-id vpc-xxx
aws ec2 create-route --route-table-id rtb-public --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx
aws ec2 create-route --route-table-id rtb-private --destination-cidr-block 0.0.0.0/0 --nat-gateway-id nat-xxx
```

### Security Groups (Stateful)
```bash
# Créer un SG
aws ec2 create-security-group --group-name web-sg --description "Web tier" --vpc-id vpc-xxx

# Règles inbound
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-xxx --protocol tcp --port 80 --source-group sg-app  # traffic from app tier only
aws ec2 authorize-security-group-ingress --group-id sg-xxx --ip-permissions IpProtocol=tcp,FromPort=22,ToPort=22,IpRanges=[{CidrIp=10.0.0.0/8},{CidrIp=192.168.0.0/16}]

# Règles egress
aws ec2 authorize-security-group-egress --group-id sg-xxx --protocol tcp --port 443 --cidr 0.0.0.0/0  # allow outbound HTTPS only

# Analyser les SG trop permissifs
aws ec2 describe-security-groups --query 'SecurityGroups[?IpPermissions[?IpRanges[?CidrIp==`0.0.0.0/0`]]]'

# SG Reference (traffic entre SG)
aws ec2 authorize-security-group-ingress --group-id sg-web --protocol tcp --port 8080 --source-group sg-app
```

### Network ACLs (Stateless)
```bash
# NACL — stateless, évaluée avant SG
aws ec2 create-network-acl --vpc-id vpc-xxx

# Inbound rules (permit HTTP + ephemeral ports)
aws ec2 create-network-acl-entry --network-acl-id acl-xxx --rule-number 100 --protocol tcp --port-range From=80,To=80 --cidr-block 0.0.0.0/0 --rule-action allow --egress false
aws ec2 create-network-acl-entry --network-acl-id acl-xxx --rule-number 200 --protocol tcp --port-range From=443,To=443 --cidr-block 0.0.0.0/0 --rule-action allow --egress false
# Ephemeral ports pour le trafic retour
aws ec2 create-network-acl-entry --network-acl-id acl-xxx --rule-number 300 --protocol tcp --port-range From=1024,To=65535 --cidr-block 0.0.0.0/0 --rule-action allow --egress false
```

### AWS WAF
```bash
# Web ACL
aws wafv2 create-web-acl --name waf-prod --scope REGIONAL --default-action Allow={} --rules file://waf-rules.json

# Règles managées AWS
cat > waf-rules.json << 'EOF'
[
  {
    "Name": "AWS-AWSManagedRulesCommonRuleSet",
    "Priority": 0,
    "Statement": { "ManagedRuleGroupStatement": { "VendorName": "AWS", "Name": "AWSManagedRulesCommonRuleSet" } },
    "OverrideAction": { "None": {} },
    "VisibilityConfig": { "SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWS-AWSManagedRulesCommonRuleSet" }
  },
  {
    "Name": "AWS-AWSManagedRulesSQLiRuleSet",
    "Priority": 1,
    "Statement": { "ManagedRuleGroupStatement": { "VendorName": "AWS", "Name": "AWSManagedRulesSQLiRuleSet" } },
    "OverrideAction": { "None": {} },
    "VisibilityConfig": { "SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWS-AWSManagedRulesSQLiRuleSet" }
  },
  {
    "Name": "RateBasedRule",
    "Priority": 2,
    "Statement": { "RateBasedStatement": { "Limit": 2000, "AggregateKeyType": "IP" } },
    "Action": { "Block": {} },
    "VisibilityConfig": { "SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "RateBasedRule" }
  }
]
EOF

# IP Blocks
aws wafv2 create-ip-set --name blocklist --scope REGIONAL --ip-address-version IPV4 --addresses 1.2.3.4/32,5.6.7.0/24
```

### AWS Shield
```bash
# Shield Standard (gratuit)
# Protection L3/L4 incluse

# Shield Advanced (3000$/mois)
aws shield create-subscription
# Protection DDoS améliorée, WAF gratuit, cost protection
# AWS Shield Response Team (SRT) 24/7
```

### VPC Security Features
```bash
# VPC Flow Logs
aws ec2 create-flow-logs --resource-type VPC --resource-id vpc-xxx --traffic-type ALL --log-group-name vpc-logs --deliver-logs-permission-arn arn:aws:iam::...:role/flow-logs

# Network Firewall
aws network-firewall create-firewall --firewall-name nfw-prod --firewall-policy-arn <policy> --vpc-id vpc-xxx --subnet-mappings SubnetId=subnet-xxx

# Traffic Mirroring (pour inspection)
aws ec2 create-traffic-mirror-session --network-interface-id eni-xxx --session-number 1 --traffic-mirror-target-id tmt-xxx --traffic-mirror-filter-id tmf-xxx

# PrivateLink
aws ec2 create-vpc-endpoint --vpc-id vpc-xxx --service-name com.amazonaws.region.s3 --route-table-ids rtb-xxx
aws ec2 create-vpc-endpoint-service-configuration --network-load-balancer-arn <nlb-arn> --acceptance-required false

# VPC Peering / Transit Gateway
aws ec2 create-vpc-peering-connection --vpc-id vpc-xxx --peer-vpc-id vpc-yyy
aws ec2 create-transit-gateway --description "Central TGW"
```

---

## 2. GCP — Network Security

### VPC Design
```bash
# VPC mode auto (default)
gcloud compute networks create prod-vpc --subnet-mode custom

# Subnets
gcloud compute networks subnets create prod-us-east --network prod-vpc --region us-east1 --range 10.0.1.0/24 --enable-private-ip-google-access
gcloud compute networks subnets create prod-europe --network prod-vpc --region europe-west1 --range 10.0.2.0/24

# Firewall Rules (stateful)
gcloud compute firewall-rules create allow-whitelist-https --network prod-vpc --priority 1000 --direction INGRESS --action ALLOW --rules tcp:443 --source-ranges <ip-whitelist>
gcloud compute firewall-rules create deny-all-ingress --network prod-vpc --priority 65535 --direction INGRESS --action DENY --rules all

# Cloud NAT
gcloud compute routers create nat-router --network prod-vpc --region us-east1
gcloud compute routers nats create nat-config --router nat-router --region us-east1 --nat-all-subnet-ip-ranges --auto-allocate-nat-external-ips
```

### VPC Service Controls
```bash
# Perimeter — empêche l'exfiltration de données
gcloud access-context-manager perimeters create prod-perimeter \
  --perimeter-type regular \
  --resources projects/<project-id> \
  --restricted-services storage.googleapis.com,bigquery.googleapis.com \
  --access-levels accessPolicies/<policy>/accessLevels/corp_access

# Ingress/Egress rules
gcloud access-context-manager perimeters create prod-perimeter \
  --perimeter-type regular \
  --resources projects/<project-id> \
  --restricted-services storage.googleapis.com \
  --ingress-policies '{"ingressFrom": {"sources": [{"accessLevel": "accessPolicies/.../accessLevels/corp_access"}]}}'
```

### Cloud Armor (WAF + DDoS)
```bash
# Security Policy
gcloud compute security-policies create arm-waf-policy

# Preconfigured rules (OWASP Top 10)
gcloud compute security-policies rules create 1000 \
  --security-policy arm-waf-policy \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('xss-v33-stable')"

gcloud compute security-policies rules create 1001 \
  --security-policy arm-waf-policy \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('sqli-v33-stable')"

# Rate limiting
gcloud compute security-policies rules create 1002 \
  --security-policy arm-waf-policy \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 100 \
  --rate-limit-threshold-interval-sec 60 \
  --conform-action "allow" \
  --exceed-action "deny(429)" \
  --enforce-on-key IP

# Adaptive Protection (ML-based)
gcloud compute security-policies update arm-waf-policy --enable-adaptive-protection

# Associer à un backend
gcloud compute backend-services update <backend> --security-policy arm-waf-policy
```

### Cloud Interconnect / VPN
```bash
# HA VPN
gcloud compute vpn-tunnels create tunnel-1 --region us-east1 --peer-gcp-gateway <gw> --shared-secret <secret> --ike-version 2
gcloud compute vpn-tunnels create tunnel-2 --region us-east1 --peer-gcp-gateway <gw> --shared-secret <secret> --ike-version 2  # second tunnel for HA

# Dedicated Interconnect (10/100 Gbps)
gcloud compute interconnects attachments create vlan-attachment --region us-east1 --interconnect <ic> --vlan-tag 100

# Partner Interconnect
gcloud compute interconnects attachments create partner-attachment --region us-east1 --partner-metadata '{"partnerName":"Equinix","circuitId":"XYZ"}'
```

### Packet Mirroring
```bash
# Mirroir de paquets (pour IDS/IPS)
gcloud compute packet-mirrorings create mirror \
  --collector-ilb <ilb> \
  --network prod-vpc \
  --filter direction=INGRESS,IPProtocols=tcp \
  --mirrored-subnet prod-us-east
```

---

## 3. Azure — Network Security

### VNet Architecture
```bash
# Virtual Network
az network vnet create --name prod-vnet --resource-group <RG> --address-prefixes 10.0.0.0/16

# Subnets
az network vnet subnet create --name web-subnet --resource-group <RG> --vnet-name prod-vnet --address-prefixes 10.0.1.0/24
az network vnet subnet create --name app-subnet --resource-group <RG> --vnet-name prod-vnet --address-prefixes 10.0.2.0/24
az network vnet subnet create --name data-subnet --resource-group <RG> --vnet-name prod-vnet --address-prefixes 10.0.3.0/24

# Bastion
az network bastion create --name bastion --resource-group <RG> --vnet-name prod-vnet --public-ip-address <pip-id>
```

### NSG (Network Security Groups)
```bash
# Créer un NSG
az network nsg create --name web-nsg --resource-group <RG>

# Règles
az network nsg rule create --nsg-name web-nsg --resource-group <RG> --name Allow-HTTPS --priority 100 --direction Inbound --access Allow --protocol Tcp --destination-port-ranges 443 --source-address-prefixes Internet
az network nsg rule create --nsg-name web-nsg --resource-group <RG> --name Deny-All --priority 4096 --direction Inbound --access Deny --protocol * --source-address-prefixes *

# Application Security Groups (ASG)
az network asg create --name web-asg --resource-group <RG>
az network asg create --name app-asg --resource-group <RG>
az network nic ip-config update --nic-name <nic> --resource-group <RG> --application-security-groups web-asg

# NSG Flow Logs
az network watcher flow-log create --name nsg-flow --nsg web-nsg --resource-group <RG> --workspace <ws-id> --traffic-analytics true --interval 10
```

### Azure Firewall
```bash
# Déploiement
az network firewall create --name fw-prod --resource-group <RG> --sku AZFW_VNet --vnet-name prod-vnet

# Public IP
az network public-ip create --name fw-pip --resource-group <RG> --sku Standard
az network firewall ip-config create --firewall fw-prod --resource-group <RG> --name fw-config --vnet-name prod-vnet --public-ip-address fw-pip

# Rules
az network firewall application-rule create --collection-name allowed-apps --firewall-name fw-prod --name allow-google --protocols Https=443 --source-addresses 10.0.0.0/8 --target-fqdns *.google.com --action Allow --priority 100

# Threat Intelligence
az network firewall update --name fw-prod --resource-group <RG> --threat-intel-mode Alert
```

### Azure DDoS Protection
```bash
# DDoS Protection Plan
az network ddos-protection create --name ddos-plan --resource-group <RG> --vnets prod-vnet

# Metrics
az monitor metrics list --resource <pip-id> --metric DDoSProtectionTriggeredTCPPackets
```

### Private Link / Endpoints
```bash
# Private Endpoint
az network private-endpoint create --name pe-storage --resource-group <RG> --vnet-name prod-vnet --subnet data-subnet --private-connection-resource-id <storage-account-id> --group-id blob

# Private DNS Zone
az network private-dns zone create --resource-group <RG> --name privatelink.blob.core.windows.net
az network private-dns link vnet create --resource-group <RG> --zone-name privatelink.blob.core.windows.net --name prod-link --virtual-network prod-vnet --registration-enabled false
```

### Azure WAF v2
```bash
# Application Gateway with WAF
az network application-gateway waf-policy create --name waf-policy --resource-group <RG>
az network application-gateway waf-policy policy-setting update --policy-name waf-policy --resource-group <RG> --state Enabled --mode Prevention

# Managed rules
az network application-gateway waf-policy managed-rule update --policy-name waf-policy --resource-group <RG> --managed-rule-set type=OWASP,version=3.2

# Custom rules
az network application-gateway waf-policy custom-rule create --policy-name waf-policy --resource-group <RG> --name block-bad-bots --priority 1 --rule-type MatchRule --match-condition RemoteAddr 1.2.3.4/32 --action Block

# Front Door + WAF (global)
az network front-door waf-policy create --name fd-waf --resource-group <RG> --sku Standard_AzureFrontDoor
```

---

## 4. Multi-Cloud Networking

### Cloud VPN Interconnect
```bash
# AWS → GCP VPN
# AWS: Virtual Private Gateway + VPN Connection
# GCP: HA VPN Gateway + Tunnel
# IPSec IKEv2 entre les deux

# AWS → Azure VPN
# AWS: Virtual Private Gateway
# Azure: Local Network Gateway + Virtual Network Gateway
```

### Service Mesh (Istio / Consul)
```yaml
# Istio — mTLS entre services multi-cloud
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: prod
spec:
  mtls:
    mode: STRICT  # mTLS obligatoire
---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-web-to-app
  namespace: prod
spec:
  selector:
    matchLabels:
      app: app-service
  action: ALLOW
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/prod/sa/web-sa"]
```

### Zero Trust Network
```bash
# BeyondCorp (Google)
# Accès basé sur l'identité, pas sur l'IP
# IAP (Identity-Aware Proxy)

# AWS Verified Access
aws verifiedaccess create-instance --description "Zero Trust Access"

# Azure AD Application Proxy
# Publier des apps on-prem sans VPN
```

---

## 5. Outils d'Audit Réseau Cloud

| Outil | Cloud | Usage |
|-------|-------|-------|
| **ScoutSuite** | Multi | Audit config réseau |
| **Prowler** | Multi | Checks CIS réseau |
| **CloudSploit** | Multi | Règles de sécurité réseau |
| **nmap** | Tous | Scan ports cloud |
| **masscan** | Tous | Scan massif |
| **CloudMapper** | AWS | Visualisation réseau |
| **Cartography** | Multi | Graphe de dépendances |
| **Network-Tracker** | Azure | Analyse NSG |

## Ressources

- **AWS Networking Best Practices**: https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-best-practices.html
- **GCP Network Security**: https://cloud.google.com/architecture/framework/security/network-security
- **Azure Network Security**: https://docs.microsoft.com/en-us/azure/security/fundamentals/network-overview
- **CIS AWS Foundations Network**: https://www.cisecurity.org/benchmark/amazon_web_services
- **OWASP Cloud Network Security**: https://owasp.org/www-project-cloud-security/
- **HackTricks Cloud Network**: https://cloud.hacktricks.wiki/