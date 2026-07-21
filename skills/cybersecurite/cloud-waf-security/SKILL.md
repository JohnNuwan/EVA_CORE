---
name: cloud-waf-security
description: Guide complet des Web Application Firewalls (WAF) Cloud — AWS WAF, GCP Cloud Armor, Azure WAF v2 / Front Door, règle personnalisées, bot control, rate limiting, OWASP Top 10, intégration CI/CD, et contournement WAF
domain: [cybersecurite, cloud, waf]
tags: [waf, aws-waf, cloud-armor, azure-waf, front-door, owasp, bot-control, rate-limiting, waf-rules, web-application-firewall]
priority: haute
---

# 🌐 Cloud WAF Security — Guide Multi-Cloud Complet

Guide exhaustif des Web Application Firewalls sur AWS, GCP et Azure : règles, automatisation, monitoring, contournements et bonnes pratiques.

---

## 1. Architecture WAF et Concepts Généraux

### 1.1 Placement du WAF dans l'Architecture

```
Utilisateur → WAF → CDN/Load Balancer → Application
                │
         Règles évaluées :
         1. Rate limiting
         2. IP reputation
         3. Geo-blocking
         4. OWASP Top 10
         5. Custom rules
         6. Bot control
                │
         Actions : ALLOW | BLOCK | COUNT | CAPTCHA
```

### 1.2 Types de Règles WAF

| Type | Description | Provider Support |
|------|-------------|------------------|
| **Managed Rules** | Règles pré-définies par le provider | AWS✓ GCP✓ Azure✓ |
| **Custom Rules** | Règles définies par l'utilisateur | AWS✓ GCP✓ Azure✓ |
| **Rate-based** | Limitation de débit | AWS✓ GCP✓ Azure✓ |
| **IP Set** | Liste IPs autorisées/bloquées | AWS✓ GCP✓ Azure✓ |
| **Geo-match** | Filtrage géographique | AWS✓ GCP✓ Azure✓ |
| **Regex** | Pattern matching | AWS✓ GCP✓ Azure✓ |
| **Size constraint** | Limite de taille requête | AWS✗ GCP✗ Azure✓ |
| **Bot Control** | ML-based bot detection | AWS✓ GCP✓ Azure✓ |
| **CAPTCHA** | Challenge utilisateur | AWS✓ GCP✓ Azure✗ |

---

## 2. AWS WAF

### 2.1 Managed Rule Groups

```bash
# AWS Managed Rules par catégorie
# Core rule set (OWASP Top 10)
aws wafv2 list-available-managed-rule-groups --scope REGIONAL

cat > waf-managed-rules.json << 'EOF'
[
  {
    "Name": "AWS-AWSManagedRulesCommonRuleSet",
    "Priority": 0,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesCommonRuleSet",
        "ExcludedRules": [
          {"Name": "SizeRestrictions_BODY"},
          {"Name": "NoUserAgent_HEADER"}
        ]
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWSCommon"}
  },
  {
    "Name": "AWS-AWSManagedRulesSQLiRuleSet",
    "Priority": 1,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesSQLiRuleSet"
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWSSQLi"}
  },
  {
    "Name": "AWS-AWSManagedRulesKnownBadInputsRuleSet",
    "Priority": 2,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesKnownBadInputsRuleSet"
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWSBadInputs"}
  },
  {
    "Name": "AWS-AWSManagedRulesAmazonIpReputationList",
    "Priority": 3,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesAmazonIpReputationList"
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWSIPRep"}
  },
  {
    "Name": "AWS-AWSManagedRulesAnonymousIpList",
    "Priority": 4,
    "Statement": {
      "ManagedRuleGroupStatement": {
        "VendorName": "AWS",
        "Name": "AWSManagedRulesAnonymousIpList"
      }
    },
    "OverrideAction": {"None": {}},
    "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "AWSAnonIP"}
  }
]
EOF

# Créer la Web ACL
aws wafv2 create-web-acl \
  --name waf-prod \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-managed-rules.json \
  --visibility-config '{"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "waf-prod"}'
```

### 2.2 Règles Personnalisées Avancées

```bash
# Règle : Bloquer les User-Agents suspects
cat > rule-block-ua.json << 'EOF'
{
  "Name": "BlockBadUserAgents",
  "Priority": 10,
  "Statement": {
    "OrStatement": {
      "Statements": [
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "user-agent"}}, "PositionalConstraint": "CONTAINS", "SearchString": "sqlmap", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "user-agent"}}, "PositionalConstraint": "CONTAINS", "SearchString": "nikto", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "user-agent"}}, "PositionalConstraint": "CONTAINS", "SearchString": "nmap", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "user-agent"}}, "PositionalConstraint": "CONTAINS", "SearchString": "masscan", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "user-agent"}}, "PositionalConstraint": "CONTAINS", "SearchString": "curl/", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}}
      ]
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "BadUA"}
}
EOF

# Règle : Bloquer les tentatives SSRF via metadata
cat > rule-block-ssrf.json << 'EOF'
{
  "Name": "BlockSSRFMetadata",
  "Priority": 20,
  "Statement": {
    "OrStatement": {
      "Statements": [
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "host"}}, "PositionalConstraint": "CONTAINS", "SearchString": "169.254.169.254", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"SingleHeader": {"Name": "host"}}, "PositionalConstraint": "CONTAINS", "SearchString": "metadata.google.internal", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}},
        {"ByteMatchStatement": {"FieldToMatch": {"UriPath": {}}, "PositionalConstraint": "CONTAINS", "SearchString": "/metadata/", "TextTransformations": [{"Priority": 0, "Type": "LOWERCASE"}]}}
      ]
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "SSRFBlock"}
}
EOF

# Règle : Limitation par pays
cat > rule-geo-block.json << 'EOF'
{
  "Name": "GeoBlockExceptEU",
  "Priority": 30,
  "Statement": {
    "NotStatement": {
      "Statement": {
        "GeoMatchStatement": {
          "CountryCodes": ["FR", "DE", "GB", "ES", "IT", "NL", "BE", "CH", "PT", "IE", "AT", "SE", "DK", "FI", "NO", "PL"]
        }
      }
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "GeoBlock"}
}
EOF

# Règle : Rate limiting par IP (2000 req/min)
cat > rule-rate-limit.json << 'EOF'
{
  "Name": "RateLimit",
  "Priority": 40,
  "Statement": {
    "RateBasedStatement": {
      "Limit": 2000,
      "AggregateKeyType": "IP"
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "RateLimit"}
}
EOF

# Règle : Bloquer les requêtes avec query string suspecte
cat > rule-block-xss.json << 'EOF'
{
  "Name": "BlockXSSQueryString",
  "Priority": 50,
  "Statement": {
    "ByteMatchStatement": {
      "FieldToMatch": {"SingleQueryArgument": {"Name": "search"}},
      "PositionalConstraint": "CONTAINS",
      "SearchString": "<script>",
      "TextTransformations": [{"Priority": 0, "Type": "NONE"}]
    }
  },
  "Action": {"Block": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "XSSBlock"}
}
EOF
```

### 2.3 Bot Control

```bash
# AWS WAF Bot Control (Managed Rule Group)
# Catégories :
# - CategoryVerified (Googlebot, Bingbot, etc.)
# - CategoryMonitoring (Pingdom, StatusCake, etc.)
# - CategorySecurity (Qualys, Acunetix, etc.)
# - CategoryHttpLibrary (Python-urllib, Go-http, etc.)

cat > bot-control.json << 'EOF'
{
  "Name": "BotControl",
  "Priority": 5,
  "Statement": {
    "ManagedRuleGroupStatement": {
      "VendorName": "AWS",
      "Name": "AWSManagedRulesBotControlRuleSet",
      "ManagedRuleGroupConfigs": [
        {"AWSManagedRulesBotControlRuleSet": {"InspectionLevel": "TARGETED"}}
      ]
    }
  },
  "OverrideAction": {"None": {}},
  "VisibilityConfig": {"SampledRequestsEnabled": true, "CloudWatchMetricsEnabled": true, "MetricName": "BotControl"}
}
EOF

# ⚠️ Avec Targeted : bloque les scrapers, bots malveillants et impersonation
# ⚠️ Coût supplémentaire (~10$/mois par million de requêtes)
```

### 2.4 WAF sur CloudFront vs ALB/API GW

| Aspect | CloudFront (Global) | ALB/API GW (Regional) |
|--------|---------------------|----------------------|
| Scope | CLOUD_FRONT | REGIONAL |
| Prix | ~0.60$/mois + requêtes | ~5$/mois + requêtes |
| Latence | Edge (faible) | Régional (modérée) |
| Rule limit | 100 rules | 100 rules |
| WAF Capacity | 1500 WCU | 1500 WCU |
| Bot Control | ✓ | ✓ |
| Rate limit global | ✓ | Par IP régionale |

### 2.5 Monitoring WAF AWS

```bash
# CloudWatch Metrics AWS WAF
aws cloudwatch list-metrics --namespace AWS/WAFV2 \
  --metric-name AllowedRequests --dimensions Name=WebACL,Value=waf-prod,Name=Rule,Value=ALL

# Alertes sur les BlockedRequests
aws cloudwatch put-metric-alarm \
  --alarm-name waf-blocked-spike \
  --metric-name BlockedRequests \
  --namespace AWS/WAFV2 \
  --statistic Sum --period 300 \
  --threshold 1000 --comparison-operator GreaterThanThreshold \
  --dimensions Name=WebACL,Value=waf-prod \
  --evaluation-periods 2

# Logs AWS WAF vers S3/CloudWatch
aws wafv2 put-logging-configuration \
  --logging-configuration '{
    "ResourceArn": "arn:aws:wafv2:us-east-1:...regional/webacl/waf-prod/...",
    "LogDestinationConfigs": ["arn:aws:firehose:us-east-1:...:deliverystream/aws-waf-logs-prod"],
    "RedactedFields": [{"SingleHeader": {"Name": "authorization"}}, {"SingleHeader": {"Name": "cookie"}}]
  }'
```

---

## 3. GCP Cloud Armor

### 3.1 Managed Rules OWASP Top 10

```bash
# Créer une security policy avec toutes les règles OWASP
gcloud compute security-policies create prod-waf

# XSS Detection (OWASP A7)
gcloud compute security-policies rules create 1000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "XSS Protection" \
  --expression "evaluatePreconfiguredExpr('xss-v33-stable')"

# SQL Injection (OWASP A3)
gcloud compute security-policies rules create 1001 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "SQLi Protection" \
  --expression "evaluatePreconfiguredExpr('sqli-v33-stable')"

# LFI/RFI (OWASP A5)
gcloud compute security-policies rules create 1002 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "LFI/RFI Protection" \
  --expression "evaluatePreconfiguredExpr('lfi-v33-stable')"

# Remote Code Execution (OWASP A8)
gcloud compute security-policies rules create 1003 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "RCE Protection" \
  --expression "evaluatePreconfiguredExpr('rce-v33-stable')"

# Protocol Attacks (HTTP smuggling, etc.)
gcloud compute security-policies rules create 1004 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "Protocol Attack Protection" \
  --expression "evaluatePreconfiguredExpr('protocolattack-v33-stable')"

# Scanner Detection
gcloud compute security-policies rules create 1005 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --description "Scanner Detection" \
  --expression "evaluatePreconfiguredExpr('scannerdetection-v33-stable')"

# PHP/CMS Attacks (si WordPress/Drupal)
gcloud compute security-policies rules create 1006 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('php-v33-stable')"
```

### 3.2 Règles Personnalisées Cloud Armor

```bash
# Expression CEL (Common Expression Language)

# Bloquer User-Agent vide
gcloud compute security-policies rules create 2000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "!has(request.headers['user-agent'])"

# Bloquer les IPs Tor (via threat intelligence)
gcloud compute security-policies rules create 2001 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "origin.IP in ['1.2.3.4', '5.6.7.8']"

# Rate limiting avancé
gcloud compute security-policies rules create 2002 \
  --security-policy prod-waf \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 500 \
  --rate-limit-threshold-interval-sec 60 \
  --conform-action "allow" \
  --exceed-action "deny(429)" \
  --enforce-on-key IP

# Bloquer les requêtes avec body trop grand
gcloud compute security-policies rules create 2003 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "has(request.body) && size(request.body) > 1000000"

# Bloquer SQLi dans les headers
gcloud compute security-policies rules create 2004 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "request.headers['x-forwarded-for'].contains('1=1')"

# Cookie hijacking detection
gcloud compute security-policies rules create 2005 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "!has(request.headers['cookie']) && request.path.matches('/api/protected')"

# Limiter les méthodes HTTP autorisées
gcloud compute security-policies rules create 2006 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "request.method != 'GET' && request.method != 'POST' && request.method != 'PUT' && request.method != 'DELETE'"
```

### 3.3 Adaptive Protection (ML-based)

```bash
# Active après 3 jours d'apprentissage du trafic de base
gcloud compute security-policies update prod-waf \
  --enable-adaptive-protection

# L'Adaptive Protection :
# 1. Apprend le trafic normal (baseline)
# 2. Détecte les anomalies statistiques
# 3. Génère des suggestions de règles
# 4. Applications : Auto-deploy ou manuel

# Voir les suggestions
gcloud compute security-policies list-preconfigured-expressions

# Configurer les seuils
gcloud compute security-policies update prod-waf \
  --adaptive-protection-auto-deploy \
  --adaptive-protection-auto-deploy-load-threshold 0.8 \
  --adaptive-protection-auto-deploy-confidence-threshold 0.9 \
  --adaptive-protection-auto-deploy-impacted-baseline-threshold 0.2
```

### 3.4 Cloud Armor avec reCAPTCHA

```bash
# Créer une clé reCAPTCHA WAF
gcloud recaptcha keys create \
  --display-name "WAF CAPTCHA" \
  --web-allowed-domains * \
  --integration-type WAF \
  --waf-feature "challenge-page" \
  --waf-service "cloud-armor"

# Règle Cloud Armor avec reCAPTCHA
gcloud compute security-policies rules create 3000 \
  --security-policy prod-waf \
  --action "allow" \
  --expression "token.recaptcha_session.score >= 0.5 && request.path.matches('/api/checkout')"
```

### 3.5 Monitoring Cloud Armor

```bash
# Cloud Monitoring metrics
gcloud logging metrics create waf-blocked \
  --description "WAF Blocked Requests" \
  --log-filter 'resource.type="http_load_balancer" AND httpRequest.status=403 AND jsonPayload.enforcedSecurityPolicy.name="prod-waf"'

# Alertes
gcloud alpha monitoring policies create \
  --display-name "WAF Block Spike" \
  --condition-display-name "High block rate" \
  --condition-filter 'metric.type="loadbalancing.googleapis.com/https/request_count" AND resource.label.security_policy="prod-waf"' \
  --condition-threshold-value 1000 \
  --condition-threshold-duration 300s
```

---

## 4. Azure WAF v2 (Application Gateway + Front Door)

### 4.1 Application Gateway avec WAF v2

```bash
# Créer une WAF Policy
az network application-gateway waf-policy create \
  --name waf-policy \
  --resource-group <RG> \
  --type OWASP \
  --version 3.2

# Configurer le mode (Prevention / Detection)
az network application-gateway waf-policy policy-setting update \
  --policy-name waf-policy \
  --resource-group <RG> \
  --state Enabled \
  --mode Prevention \
  --max-request-body-size 128 \
  --file-upload-limit-in-mb 100 \
  --request-body-check true

# Managed Rules OWASP
az network application-gateway waf-policy managed-rule update \
  --policy-name waf-policy \
  --resource-group <RG> \
  --managed-rule-set type=OWASP,version=3.2

# Exclure des règles OWASP spécifiques (si faux positifs)
az network application-gateway waf-policy managed-rule rule-set add \
  --policy-name waf-policy \
  --resource-group <RG> \
  --type OWASP \
  --version 3.2 \
  --group-name REQUEST-942-APPLICATION-ATTACK-SQLI \
  --rule-ids 942100 942110

# Personnaliser l'action par défaut
az network application-gateway waf-policy policy-setting update \
  --policy-name waf-policy \
  --resource-group <RG> \
  --custom-block-response-status-code 403 \
  --custom-block-response-body "<html><body><h1>Blocked by WAF</h1></body></html>"
```

### 4.2 Règles Personnalisées Azure WAF

```bash
# Bloquer par IP
az network application-gateway waf-policy custom-rule create \
  --policy-name waf-policy \
  --resource-group <RG> \
  --name block-bad-ips \
  --priority 1 \
  --rule-type MatchRule \
  --match-condition RemoteAddr 1.2.3.0/24 \
  --match-condition RemoteAddr 5.6.7.0/24 \
  --action Block

# Bloquer User-Agent
az network application-gateway waf-policy custom-rule create \
  --policy-name waf-policy \
  --resource-group <RG> \
  --name block-scan-tools \
  --priority 2 \
  --rule-type MatchRule \
  --match-condition RequestHeader User-Agent contains "sqlmap" \
  --match-condition RequestHeader User-Agent contains "nikto" \
  --action Block

# Geo-filtering (bloquer sauf pays autorisés)
az network application-gateway waf-policy custom-rule create \
  --policy-name waf-policy \
  --resource-group <RG> \
  --name geo-allow-eu \
  --priority 3 \
  --rule-type MatchRule \
  --match-condition GeoMatch "FR" \
  --action Allow

# Rate limiting (via Azure Front Door uniquement)
# Azure WAF v2 sur Application Gateway ne supporte PAS le rate limiting natif
# Utiliser Front Door + WAF pour le rate limiting

# Bloquer les méthodes HTTP dangereuses
az network application-gateway waf-policy custom-rule create \
  --policy-name waf-policy \
  --resource-group <RG> \
  --name block-unsafe-methods \
  --priority 4 \
  --rule-type MatchRule \
  --match-condition RequestMethod "TRACE" \
  --match-condition RequestMethod "OPTIONS" \
  --action Block
```

### 4.3 Azure Front Door + WAF (Global)

```bash
# Créer une WAF Policy pour Front Door
az network front-door waf-policy create \
  --name fd-waf \
  --resource-group <RG> \
  --sku Premium_AzureFrontDoor \
  --mode Prevention

# Ajouter des managed rules
az network front-door waf-policy managed-rules add \
  --policy-name fd-waf \
  --resource-group <RG> \
  --managed-rule-set type=Microsoft_DefaultRuleSet,version=2.1

# Rate limiting sur Front Door
az network front-door waf-policy custom-rule create \
  --policy-name fd-waf \
  --resource-group <RG> \
  --name rate-limit-api \
  --priority 100 \
  --rule-type RateLimitRule \
  --match-condition RemoteAddr * \
  --action Block \
  --rate-limit-duration 1 \
  --rate-limit-threshold 1000 \
  --group-by '{"customKeys": [{"name": "RemoteAddr"}]}'

# Bot Protection
az network front-door waf-policy custom-rule create \
  --policy-name fd-waf \
  --resource-group <RG> \
  --name bot-protect \
  --priority 200 \
  --rule-type RateLimitRule \
  --match-condition RequestHeader User-Agent matches "bot|crawler|spider" \
  --action Log \
  --rate-limit-duration 1 \
  --rate-limit-threshold 100
```

### 4.4 Monitoring Azure WAF

```bash
# Logs WAF vers Log Analytics
az monitor diagnostic-settings create \
  --name waf-logs \
  --resource /subscriptions/.../applicationGateways/... \
  --workspace sentinel-ws \
  --logs '[
    {"category": "ApplicationGatewayAccessLog", "enabled": true},
    {"category": "ApplicationGatewayFirewallLog", "enabled": true}
  ]'

# Métriques WAF
az monitor metrics list \
  --resource /subscriptions/.../applicationGateways/... \
  --metric "BlockedRequests"

# Alertes WAF
az monitor metrics alert create \
  --name "waf-blocks" \
  --resource-group <RG> \
  --scopes /subscriptions/.../applicationGateways/... \
  --condition "avg BlockedRequests > 100" \
  --window-size 5m
```

---

## 5. Stratégies WAF Multi-Cloud

### 5.1 OWASP Top 10 — Couverture par Provider

| OWASP | AWS WAF | Cloud Armor | Azure WAF |
|-------|---------|-------------|-----------|
| A1: Broken Access Control | Custom rules | CEL expressions | Custom rules |
| A2: Cryptographic Failures | Custom rules | Custom rules | Custom rules |
| A3: Injection (SQLi) | ✓ Managed | ✓ Preconfigured | ✓ OWASP 3.2 |
| A4: Insecure Design | Custom | Custom | Custom |
| A5: Security Misconfig | Custom | Custom | Custom |
| A6: Vulnerable Components | Custom (non-WAF) | Custom | Custom |
| A7: XSS | ✓ Managed | ✓ Preconfigured | ✓ OWASP 3.2 |
| A8: Insecure Deserialization | Custom | Custom | Custom |
| A9: Logging/Monitoring | Custom | Custom | Custom |
| A10: SSRF | ★ Custom rules | CEL expressions | Custom rules |

### 5.2 Pipeline CI/CD WAF

```bash
# Infrastructure as Code — Terraform WAF

# AWS
resource "aws_wafv2_web_acl" "main" {
  name        = "waf-prod"
  scope       = "REGIONAL"
  default_action { allow {} }
  
  rule {
    name     = "AWSCommonRules"
    priority = 0
    override_action { none {} }
    statement {
      managed_rule_group_statement {
        vendor_name = "AWS"
        name        = "AWSManagedRulesCommonRuleSet"
      }
    }
    visibility_config {
      metric_name = "AWSCommonRules"
      sampled_requests_enabled = true
      cloudwatch_metrics_enabled = true
    }
  }
}

# GCP
resource "google_compute_security_policy" "main" {
  name = "prod-waf"
  
  rule {
    action   = "deny(403)"
    priority = 1000
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-v33-stable')"
      }
    }
  }
}

# Azure
resource "azurerm_web_application_firewall_policy" "main" {
  name                = "waf-policy"
  resource_group_name = azurerm_resource_group.main.name
  
  managed_rules {
    managed_rule_set {
      type    = "OWASP"
      version = "3.2"
    }
  }
  
  policy_settings {
    enabled = true
    mode    = "Prevention"
  }
}
```

### 5.3 Testing WAF — Bypass Techniques

```bash
# Contournement par encodage
# Double URL encoding
/redirect?url=%2568%2574%2574%2570%253a...
# (évite les règles qui matchent http:)

# Unicode bypass
<script> → \u003cscript\u003e
# Bypass WAF AWS — Unicode interprété différemment

# HTTP Parameter Pollution
?id=1&id=2&id=3

# Case manipulation
<Script>alert(1)</SCRIPT>

# Content-Type switching
# JSON → XML → multipart pour cacher les patterns

# Null byte injection
<script>%00alert(1)</script>

# Path normalization bypass
//api/../../../etc/passwd

# Headers manipulation
# X-Forwarded-For: 127.0.0.1 (spoofing IP interne)
```

### 5.4 Comparatif des WAF Cloud

| Critère | AWS WAF | GCP Cloud Armor | Azure WAF v2 |
|---------|---------|-----------------|--------------|
| **Type** | Cloud-native | Cloud-native | App Gateway / Front Door |
| **Managed Rules** | 10+ rulesets | 7 preconfigured | OWASP + Microsoft |
| **Custom Rules** | JSON rules | CEL expressions | Match conditions |
| **Bot Control** | ✓ (payant) | ✗ (reCAPTCHA) | ✓ (Front Door) |
| **Rate Limiting** | ✓ | ✓ | ✓ (Front Door) |
| **Geo-filtering** | ✓ | ✓ | ✓ |
| **ML Detection** | ✗ | ✓ (Adaptive) | ✗ |
| **CAPTCHA** | ✓ | ✓ (reCAPTCHA) | ✗ |
| **Logging** | Kinesis Firehose | Cloud Logging | Log Analytics |
| **Coût (approx)** | ~0.60$/ACL/mois | ~2$/policy/mois | ~30$/WAF/mois |
| **Limite Rules** | 100 (1500 WCU) | Sans limite | 100 custom |

## Pitfalls

- **Ne PAS** activer le WAF en mode Prevention directement — toujours commencer en COUNT/Detection pour valider les faux positifs
- **Ne PAS** utiliser les rate limits trop basses sur les endpoints API légitimes
- **TOUJOURS** exclure les IPs de monitoring et health checks des règles de rate limit
- **TOUJOURS** redacter les champs sensibles (Authorization, Cookie) dans les logs WAF
- Les managed rules peuvent bloquer du traffic légitime — maintenir une liste d'exclusions
- AWS WAF WCU (Web ACL Capacity Units) limite les règles complexes — surveiller
- GCP Adaptive Protection nécessite 3 jours d'apprentissage — ne pas activer en urgence
- Le coût des requêtes WAF s'ajoute au coût du load balancer — budgétiser

## Ressources

- **AWS WAF**: https://docs.aws.amazon.com/waf/latest/developerguide/
- **GCP Cloud Armor**: https://cloud.google.com/armor/docs
- **Azure WAF**: https://docs.microsoft.com/en-us/azure/web-application-firewall/
- **OWASP WAF Cheatsheet**: https://cheatsheetseries.owasp.org/cheatsheets/Web_Application_Firewall_Cheat_Sheet.html
- **Coraza WAF (Open Source)**: https://coraza.io/
- **ModSecurity**: https://modsecurity.org/
- **Awesome WAF Bypass**: https://github.com/0xInfection/Awesome-WAF