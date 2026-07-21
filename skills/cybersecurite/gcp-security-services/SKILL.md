---
name: gcp-security-services
description: Guide complet des services de sécurité GCP — Security Command Center, Cloud IDS, reCAPTCHA, Web Security Scanner, Cloud Armor, VPC Service Controls, Access Transparency, Assured Workloads, et architecture défensive GCP
domain: [cybersecurite, cloud, gcp]
tags: [gcp, security-command-center, cloud-ids, recaptcha, web-security-scanner, cloud-armor, vpc-service-controls, access-transparency, assured-workloads]
priority: haute
---

# 🛡️ GCP Security Services — Guide Défensif Complet

Guide exhaustif des services de sécurité natifs GCP, leur configuration, intégration et bonnes pratiques défensives.

---

## 1. Security Command Center (SCC)

### 1.1 Activation et Architecture

Security Command Center est le hub central de sécurité GCP. Deux niveaux : Standard (gratuit) et Premium (payant).

```bash
# Activer SCC Premium au niveau org
gcloud scc settings enable --organization <ORG_ID> --service SECURITY_HEALTH_ANALYTICS
gcloud scc settings enable --organization <ORG_ID> --service WEB_SECURITY_SCANNER
gcloud scc settings enable --organization <ORG_ID> --service VULNERABILITY_SCANNER

# Niveau Standard (gratuit)
gcloud scc settings enable --organization <ORG_ID> --service SECURITY_HEALTH_ANALYTICS_SERVICE

# Ajouter des sources de menaces
gcloud scc settings enable --organization <ORG_ID> --service EVENT_THREAT_DETECTION
gcloud scc settings enable --organization <ORG_ID> --service CONTAINER_THREAT_DETECTION
gcloud scc settings enable --organization <ORG_ID> --service VIRTUAL_MACHINE_THREAT_DETECTION
```

### 1.2 Types de Findings SCC

| Catégorie | Finding | Sévérité |
|-----------|---------|----------|
| **IAM** | Bucket policy public | CRITICAL |
| **Storage** | Bucket without uniform access | HIGH |
| **Compute** | VM with public IP + default SA | HIGH |
| **Network** | Firewall rule 0.0.0.0/0 on SSH | HIGH |
| **K8s** | GKE cluster with legacy auth | HIGH |
| **K8s** | GKE cluster with default SA | MEDIUM |
| **Data** | Cloud SQL without SSL | MEDIUM |
| **Logging** | Audit logging disabled | HIGH |
| **Crypto** | Crypto mining detected | CRITICAL |
| **IAM** | Service account key created | MEDIUM |

### 1.3 Automatisation des Réponses

```bash
# SCC → Pub/Sub → Cloud Function → Remediation
gcloud scc notifications create scc-critical \
  --organization <ORG_ID> \
  --pubsub-topic projects/<PROJECT>/topics/scc-alerts \
  --filter 'severity="CRITICAL" AND state="ACTIVE"'

# Cloud Function de remediation
cat > index.js << 'EOF'
const {SecurityCenterClient} = require('@google-cloud/security-center');
const client = new SecurityCenterClient();

exports.remediateFinding = async (pubsubEvent) => {
  const finding = JSON.parse(Buffer.from(pubsubEvent.data, 'base64').toString());
  
  if (finding.category === 'BUCKET_POLICY_ONLY_DISABLED') {
    const bucket = finding.resourceName.split('/').pop();
    // Activer uniform bucket-level access
    const {Storage} = require('@google-cloud/storage');
    const storage = new Storage();
    await storage.bucket(bucket).setMetadata({
      iamConfiguration: {uniformBucketLevelAccess: {enabled: true}}
    });
    console.log(`Remediated bucket ${bucket}`);
  }
};
EOF
```

### 1.4 Détection de Menaces Événementielles (ETD)

```bash
# Activer Event Threat Detection
gcloud services enable eventthreatdetection.googleapis.com \
  --organization <ORG_ID>

# Types de détection ETD
# - Token volés (Google Workspace)
# - Service Account anormal
# - Cryptomining
# - Exfiltration de données
# - Reconnaissance
# - Accès depuis Tor

# Exporter les findings vers BigQuery
gcloud scc export findings --organization <ORG_ID> \
  --bigquery-table <PROJECT>:scc_dataset.findings \
  --export-timeout 600
```

---

## 2. Cloud IDS (Intrusion Detection System)

### 2.1 Architecture

Cloud IDS est un service de détection d'intrusion réseau managé, basé sur Palo Alto Networks.

```
Internet → Cloud NAT → VPC → Cloud IDS Endpoint → Protected VMs
                              ↓
                    Inspection de tout le trafic
                    (Threat signatures, anomalies)
```

### 2.2 Déploiement

```bash
# Créer un endpoint IDS
gcloud ids endpoints create ids-prod \
  --network prod-vpc \
  --zone us-central1-a \
  --severities CRITICAL HIGH MEDIUM \
  --threat-exceptions '[
    {"threatId": "12345", "description": "False positive internal scanner"}
  ]'

# Lister les menaces détectées
gcloud ids threats list --endpoint ids-prod \
  --filter "severity=CRITICAL"

# Créer des exceptions de menace
gcloud ids threats create-exception \
  --endpoint ids-prod \
  --threat-id 67890 \
  --description "Internal app scanning" \
  --action ALLOW_WITH_LOG
```

### 2.3 Logs vers SIEM

```bash
# Cloud IDS → Cloud Logging → BigQuery
gcloud logging sinks create ids-sink \
  bigquery.googleapis.com/projects/<PROJECT>/datasets/ids_logs \
  --log-filter 'resource.type="ids.googleapis.com/Endpoint"'
```

---

## 3. reCAPTCHA Enterprise

### 3.1 Mise en Place

```bash
# Activer l'API
gcloud services enable recaptchaenterprise.googleapis.com

# Créer une clé reCAPTCHA pour site web
gcloud recaptcha keys create \
  --display-name "Site Web Principal" \
  --web-allowed-domains example.com,app.example.com \
  --integration-type SCORE \
  --testing-score 0.5

# Créer une clé pour WAF (Cloud Armor)
gcloud recaptcha keys create \
  --display-name "WAF Protection" \
  --web-allowed-domains * \
  --integration-type WAF \
  --waf-feature "challenge-page" \
  --waf-service "cloud-armor"
```

### 3.2 Assessment API

```bash
# Évaluer une action utilisateur
cat > assessment.json << 'EOF'
{
  "event": {
    "token": "USER_TOKEN",
    "siteKey": "RECAPTCHA_KEY",
    "userAgent": "Mozilla/5.0...",
    "userIpAddress": "1.2.3.4",
    "expectedAction": "login",
    "hashedAccountId": "HASHED_USER_ID"
  }
}
EOF

curl -X POST https://recaptchaenterprise.googleapis.com/v1/projects/<PROJECT>/assessments \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d @assessment.json
```

### 3.3 Intégration Cloud Armor

```bash
# Associer reCAPTCHA à une security policy Cloud Armor
gcloud compute security-policies rules create 1000 \
  --security-policy waf-policy \
  --action "allow" \
  --expression "token.recaptcha_session.score >= 0.7 && request.path.matches('/api/login')"
```

---

## 4. Web Security Scanner

### 4.1 Configuration

```bash
# Scanner une application App Engine
gcloud web-security-scanner scan-configs create \
  --display-name "App Scan" \
  --starting-urls https://app.example.com \
  --max-qps 10 \
  --schedule interval-days=7,start-time=2026-01-01T00:00:00Z

# Scanner une Compute Engine (via URL Group)
gcloud web-security-scanner scan-configs create \
  --display-name "VM Scan" \
  --starting-urls https://app.example.com \
  --target-platform COMPUTE \
  --export-to-security-command-center
```

### 4.2 Types de Vulnérabilités Détectées

| Type | Description |
|------|-------------|
| XSS | Stored, Reflected, DOM-based |
| SQLi | SQL Injection |
| CSRF | Cross-Site Request Forgery |
| Info Leak | Directory listing, backup files |
| Mixed Content | HTTP/HTTPS mix |
| Outdated Library | JavaScript libs with CVEs |
| Header injection | CRLF, Host header |
| Open redirect | URL redirection |

### 4.3 Intégration CI/CD

```bash
# Scan dans Cloud Build
cat > cloudbuild.yaml << 'EOF'
steps:
  - name: gcr.io/cloud-builders/gcloud
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        gcloud web-security-scanner scan-configs create \
          --display-name "Build Scan ${BUILD_ID}" \
          --starting-urls https://staging.${PROJECT_ID}.appspot.com \
          --export-to-security-command-center
EOF
```

---

## 5. Cloud Armor — WAF et DDoS

### 5.1 Règles Avancées

```bash
# Créer une security policy
gcloud compute security-policies create prod-waf

# OWASP Top 10 rules
gcloud compute security-policies rules create 1000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('xss-v33-stable')"

gcloud compute security-policies rules create 1001 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('sqli-v33-stable')"

gcloud compute security-policies rules create 1002 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('lfi-v33-stable')"

gcloud compute security-policies rules create 1003 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('rce-v33-stable')"

# Rate limiting
gcloud compute security-policies rules create 2000 \
  --security-policy prod-waf \
  --action "rate-based-ban" \
  --rate-limit-threshold-count 1000 \
  --rate-limit-threshold-interval-sec 60 \
  --conform-action "allow" \
  --exceed-action "deny(429)" \
  --enforce-on-key IP

# Geo-based blocking
gcloud compute security-policies rules create 3000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "origin.region_code == 'RU' || origin.region_code == 'CN'"

# Bot management
gcloud compute security-policies rules create 4000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "evaluatePreconfiguredExpr('cve-canary')"

# Custom headers
gcloud compute security-policies rules create 5000 \
  --security-policy prod-waf \
  --action "deny(403)" \
  --expression "has(request.headers['X-Forwarded-For']) && request.headers['X-Forwarded-For'].contains('127.0.0.1')"
```

### 5.2 Adaptive Protection (ML-based)

```bash
# Activer l'Adaptive Protection
gcloud compute security-policies update prod-waf \
  --enable-adaptive-protection

# L'Adaptive Protection apprend le trafic normal pendant 3 jours
# Puis suggère des règles automatiques
# Examiner les suggestions
gcloud compute security-policies list-preconfigured-expressions
```

### 5.3 Cloud Armor avec Backend

```bash
# Associer à un backend service
gcloud compute backend-services update web-backend \
  --security-policy prod-waf

# Associer à un External HTTPS Load Balancer
gcloud compute target-https-proxies update web-https-proxy \
  --security-policy prod-waf
```

---

## 6. VPC Service Controls

### 6.1 Architecture

VPC Service Controls créent un périmètre de sécurité autour des services GCP managés, empêchant l'exfiltration de données.

```bash
# Créer un access level
gcloud access-context-manager access-levels create corp_network \
  --access-policy <POLICY_ID> \
  --title "Corporate Network" \
  --basic-level-spec '{
    "conditions": [{
      "ipSubnetworks": ["192.168.0.0/16", "10.0.0.0/8"],
      "devicePolicy": {"requireScreenLock": true}
    }]
  }'

# Créer un périmètre
gcloud access-context-manager perimeters create prod-perimeter \
  --access-policy <POLICY_ID> \
  --perimeter-type regular \
  --resources projects/<PROJECT> \
  --restricted-services \
    storage.googleapis.com,bigquery.googleapis.com,bigtable.googleapis.com \
  --access-levels accessPolicies/<POLICY_ID>/accessLevels/corp_network

# Périmètre en mode dry-run (audit avant enforcement)
gcloud access-context-manager perimeters create prod-dry-run \
  --access-policy <POLICY_ID> \
  --perimeter-type dry-run \
  --resources projects/<PROJECT> \
  --restricted-services storage.googleapis.com
```

### 6.2 Ingress/Egress Rules

```bash
# Ingress — autoriser l'accès depuis Cloud Functions
gcloud access-context-manager perimeters update prod-perimeter \
  --access-policy <POLICY_ID> \
  --add-ingress-policies '[
    {
      "ingressFrom": {
        "sources": [{"accessLevel": "accessPolicies/<POLICY_ID>/accessLevels/corp_network"}],
        "identityType": "ANY_IDENTITY"
      },
      "ingressTo": {
        "resources": ["projects/<PROJECT>"],
        "operations": [{
          "serviceName": "storage.googleapis.com",
          "methodSelectors": [{"method": "google.storage.objects.get"}]
        }]
      }
    }
  ]'

# Egress — autoriser l'export BigQuery vers un bucket spécifique
gcloud access-context-manager perimeters update prod-perimeter \
  --access-policy <POLICY_ID> \
  --add-egress-policies '[
    {
      "egressFrom": {"identityType": "ANY_USER_ACCOUNT"},
      "egressTo": {
        "resources": ["projects/<EXPORT_PROJECT>"],
        "operations": [{
          "serviceName": "bigquery.googleapis.com",
          "methodSelectors": [{"method": "google.cloud.bigquery.v2.JobService.InsertJob"}]
        }]
      }
    }
  ]'
```

### 6.3 VPC SC + Cloud Logging

```bash
# Exporter les violations de périmètre
gcloud logging metrics create perimeter-violations \
  --description "VPC SC violations" \
  --log-filter 'protoPayload.methodName:"vpcsc" AND severity>=WARNING'
```

---

## 7. Access Transparency

### 7.1 Activation

Access Transparency journalise les accès des employés Google à vos données.

```bash
# Activer Access Transparency au niveau org
gcloud alpha access-transparency settings enable \
  --organization <ORG_ID>

# Activer pour un projet spécifique
gcloud alpha access-transparency settings enable \
  --project <PROJECT_ID>
```

### 7.2 Logs d'Accès

```bash
# Query les logs d'Access Transparency
gcloud logging read 'protoPayload.serviceName="accessapproval.googleapis.com"' \
  --limit 10 \
  --format json

# Logs d'approbation de support
gcloud logging read 'protoPayload.serviceName="cloudsupport.googleapis.com"'
```

---

## 8. Assured Workloads

Pour les charges de travail réglementées (HIPAA, FedRAMP, PCI-DSS, ITAR).

```bash
# Créer un workload FedRAMP
gcloud assured workloads create fedramp-workload \
  --organization <ORG_ID> \
  --compliance-regime FEDRAMP_MODERATE \
  --display-name "FedRAMP Workload" \
  --billing-account <BILLING_ID>

# Créer un workload HIPAA
gcloud assured workloads create hipaa-workload \
  --organization <ORG_ID> \
  --compliance-regime HIPAA \
  --display-name "HIPAA Data" \
  --billing-account <BILLING_ID>
```

---

## 9. Cloud Key Management Service (KMS) Avancé

### 9.1 Protection HSM

```bash
# Créer une clé HSM (FIPS 140-2 Level 3)
gcloud kms keyrings create hsm-prod --location global
gcloud kms keys create hsm-key --keyring hsm-prod \
  --location global --purpose encryption \
  --protection-level hsm \
  --rotation-period 30d \
  --next-rotation-time "2026-01-01T00:00:00Z"

# Clé asymétrique pour signature
gcloud kms keys create signing-key --keyring hsm-prod \
  --location global \
  --purpose asymmetric-signing \
  --default-algorithm rsa-sign-pkcs1-2048-sha256 \
  --protection-level hsm
```

### 9.2 External Key Manager (EKM)

```bash
# Connecter un HSM on-premise (Thales, Fortanix)
gcloud kms ekm-connections create prod-ekm \
  --location us-central1 \
  --service-resolvers '[
    {
      "hostname": "hsm.internal.corp",
      "port": 443,
      "serverCertificates": [{ "rawDer": "$(base64 -w0 cert.pem)" }],
      "serviceDirectoryService": "projects/<PROJECT>/locations/us-central1/namespaces/<NS>/services/<SVC>"
    }
  ]'
```

---

## 10. Organisation Policies

### 10.1 Policies Essentielles

```bash
# Liste des politiques d'organisation
# Ces politiques s'appliquent à tous les projets de l'organisation

# 1. Bloquer les comptes de service par défaut
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/iam.automaticIamGrantsForDefaultServiceAccounts
listPolicy:
  deny: all
EOF

# 2. Domain Restricted Sharing
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/iam.allowedPolicyMemberDomains
listPolicy:
  allowedValues:
  - C0xxxxxxx  # Google Workspace Customer ID
EOF

# 3. Bloquer les IP publiques sur les VMs
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/compute.vmExternalIpAccess
listPolicy:
  deny: all
EOF

# 4. Uniform bucket-level access obligatoire
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/storage.uniformBucketLevelAccess
booleanPolicy:
  enforced: true
EOF

# 5. Require OS Login
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/compute.requireOsLogin
booleanPolicy:
  enforced: true
EOF

# 6. Bloquer les SKUs GPU non autorisés
gcloud resource-manager org-policies set-policy --organization <ORG_ID> \
  --policy-file /dev/stdin << 'EOF'
constraint: constraints/compute.restrictNonCompliantMachineTypes
listPolicy:
  allow: all
EOF
```

### 10.2 Audit des Violations

```bash
# Voir violations de politique
gcloud asset search-all-resources \
  --scope organizations/<ORG_ID> \
  --asset-types compute.googleapis.com/Instance,storage.googleapis.com/Bucket \
  --query "state=RUNNING AND metadata.externalIPs.exists()"
```

---

## 11. Cloud Audit Logs

### 11.1 Configuration Complète

```bash
# Activer les Data Access Logs pour tous les services
cat > audit_config.yaml << 'EOF'
auditConfigs:
  - service: allServices
    auditLogConfigs:
      - logType: ADMIN_READ
      - logType: DATA_READ
      - logType: DATA_WRITE
EOF

gcloud projects set-iam-policy <PROJECT> audit_config.yaml

# Exporter vers BigQuery pour analyse
gcloud logging sinks create audit-bq \
  bigquery.googleapis.com/projects/<PROJECT>/datasets/audit_logs \
  --log-filter 'severity>=WARNING AND logName:"cloudaudit"'

# Exporter vers Pub/Sub pour SIEM
gcloud logging sinks create audit-pubsub \
  pubsub.googleapis.com/projects/<PROJECT>/topics/audit-alerts \
  --log-filter 'severity>=CRITICAL'
```

### 11.2 Alertes de Sécurité

```bash
# Créer une métrique basée sur les logs
gcloud logging metrics create iam-changes \
  --description "IAM policy changes" \
  --log-filter 'protoPayload.methodName:"SetIamPolicy"'

# Créer une alerte Cloud Monitoring
gcloud alpha monitoring policies create \
  --policy-from-file iam-alert.yaml
```

---

## 12. Architecture Défensive Complète GCP

```
                    ┌───────────────────────────────┐
                    │   Organization Policies        │
                    │   Domain Restriction + OS Login │
                    └───────────────┬───────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
    ┌───────▼──────────┐  ┌────────▼───────┐  ┌───────────▼───────┐
    │  Security Command │  │  VPC Service   │  │  Cloud Audit     │
    │  Center Premium   │  │  Controls      │  │  Logs + BigQuery │
    └───────┬──────────┘  └────────────────┘  └───────────────────┘
            │
    ┌───────▼───────────────────────────────────────┐
    │              Cloud Armor (WAF) + Cloud IDS    │
    │              Protection Réseau                 │
    └───────┬───────────────────────────────────────┘
            │
    ┌───────▼──────────┐  ┌────────▼───────┐  ┌───────────▼───────┐
    │  Assured Workloads│  │  Cloud KMS HSM │  │  reCAPTCHA        │
    │  (HIPAA/FedRAMP)  │  │  EKM           │  │  Enterprise       │
    └──────────────────┘  └────────────────┘  └───────────────────┘
```

## Pitfalls

- **Ne PAS** activer SCC Premium sans budget (coût par projet, peut exploser)
- **Ne PAS** configurer VPC Service Controls sans mode dry-run d'abord (risque de casser des apps)
- **Ne PAS** oublier d'exclure les IPs internes des règles de geo-blocking Cloud Armor
- **TOUJOURS** activer Data Access Logs pour les services critiques (coût modéré)
- **TOUJOURS** configurer les notifications Pub/Sub pour SCC findings
- L'Adaptive Protection Cloud Armor met 3 jours à apprendre — ne pas activer en urgence
- Les Organization Policies sont héritées — tester sur un projet sandbox avant le déploiement global
- Les EKM nécessitent Service Directory — coût supplémentaire

## Ressources

- **GCP Security Documentation**: https://cloud.google.com/security
- **Security Command Center**: https://cloud.google.com/security-command-center
- **Cloud Armor**: https://cloud.google.com/armor
- **VPC Service Controls**: https://cloud.google.com/vpc-service-controls
- **Cloud IDS**: https://cloud.google.com/ids
- **reCAPTCHA Enterprise**: https://cloud.google.com/recaptcha-enterprise
- **Web Security Scanner**: https://cloud.google.com/security-command-center/docs/web-security-scanner
- **Access Transparency**: https://cloud.google.com/access-transparency
- **Assured Workloads**: https://cloud.google.com/assured-workloads
- **GCP Security Foundations Blueprint**: https://cloud.google.com/security-foundations