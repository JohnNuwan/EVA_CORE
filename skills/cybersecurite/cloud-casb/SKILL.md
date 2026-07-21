---
name: cloud-casb
description: Guide complet des Cloud Access Security Brokers (CASB) — Microsoft Defender for Cloud Apps, Netskope, Palo Alto Prisma, CASB use cases, Shadow IT discovery, DLP cloud, threat detection SaaS, et bonnes pratiques CASB
domain: [cybersecurite, cloud, casb]
tags: [casb, defender-for-cloud-apps, netskope, prisma-cloud, shadow-it, cloud-dlp, saas-security, access-control, cloud-discovery]
priority: haute
---

# ☁️ Cloud Access Security Broker (CASB) — Guide Complet

Guide exhaustif des CASB : déploiement, architecture, politiques, DLP cloud, découverte Shadow IT, et protection SaaS.

---

## 1. Qu'est-ce qu'un CASB ?

Un Cloud Access Security Broker (CASB) est un point d'application de politiques de sécurité entre les utilisateurs et les services cloud. Il agit comme un **proxy de sécurité** et un **gateway de contrôle** pour les applications SaaS.

### 1.1 Les 4 Piliers du CASB

| Pilier | Description | Exemples |
|--------|-------------|----------|
| **Visibility** | Découverte des applications SaaS utilisées | Shadow IT discovery, usage analytics |
| **Data Security** | Protection des données en transit et au repos | DLP, encryption, tokenization |
| **Threat Protection** | Détection des comportements anormaux | UEBA, malware detection, zero-day |
| **Compliance** | Conformité aux régulations | SOC2, HIPAA, GDPR, PCI-DSS |

### 1.2 Modes de Déploiement

```
Mode API (Recommandé)
┌─────────┐    API    ┌──────────┐    API    ┌─────────┐
│ Users   │ ←──────→ │ CASB    │ ←──────→ │ SaaS    │
│         │          │ (API)   │          │ (App)   │
└─────────┘          └──────────┘          └─────────┘
                     │ Audit, DLP, Classification
                     │ Pas de latence supplémentaire

Mode Proxy (Reverse)
┌─────────┐   Traffic   ┌──────────┐   Traffic   ┌─────────┐
│ Users   │ ←─────────→ │ CASB    │ ←─────────→ │ SaaS    │
│         │             │ (Proxy) │             │ (App)   │
└─────────┘             └──────────┘             └─────────┘
                        │ Inspection en temps réel
                        │ Latence ajoutée

Mode Forward Proxy (Agent)
┌─────────┐   Agent    ┌──────────┐   Traffic   ┌─────────┐
│ Device  │ ←────────→ │ CASB    │ ←─────────→ │ SaaS    │
│ +Agent  │            │ (Proxy) │             │ (App)   │
└─────────┘            └──────────┘             └─────────┘
                       │ Trafic redirigé via PAC/Agent
                       | Contrôle granular
```

| Mode | Latence | Visibilité | Contrôle | Déploiement |
|------|---------|------------|----------|-------------|
| **API** | Aucune | Post-facto | Modéré | Rapide (API keys) |
| **Reverse Proxy** | Faible | Temps réel | Élevé | Configuration DNS |
| **Forward Proxy** | Modérée | Temps réel | Total | Agent sur endpoint |

---

## 2. Microsoft Defender for Cloud Apps

### 2.1 Découverte Shadow IT

```bash
# Defender for Cloud Apps = CASB Microsoft (ex Microsoft Cloud App Security)

# Étape 1 : Snapshot Discovery (upload logs firewall)
# Uploader les logs des firewalls/proxies
# Formats supportés : Palo Alto, Zscaler, Fortinet, CheckPoint, Cisco, etc.

# Étape 2 : Continuous Discovery (via Defender for Endpoint)
# Intégration avec Defender for Endpoint → trafic cloud visible

# Étape 3 : Cloud Discovery Dashboard
# Applications identifiées, score de risque, utilisation
# Via le portail : security.microsoft.com → Cloud Apps → Cloud Discovery

# Étape 4 : Sanctionner/Unsanctionner les apps
# Sanctioned : Apps autorisées
# Unsanctioned : Apps bloquées
```

### 2.2 Configuration des API Connectors

```bash
# Connecteurs API pour la protection en temps réel
# Chaque connecteur donne un accès API au CASB

# Connecteurs supportés :
# - Microsoft 365 (Exchange, SharePoint, OneDrive, Teams)
# - Salesforce
# - Box
# - Dropbox
# - Google Workspace
# - AWS (CloudTrail)
# - ServiceNow
# - GitHub
# - Slack
# - Zoom
# - Okta
# - Workday

# Via le portail : Cloud Apps → Connected apps → App connectors
# Nécessite un compte admin de l'application SaaS
# Configure les webhooks CASB → SaaS pour les alertes
```

### 2.3 Politiques CASB

**Politiques de Détection :**
```json
{
  "name": "Anomalous Download (Mass Download)",
  "type": "Activity Policy",
  "filter": "File download FROM OneDrive/SharePoint",
  "conditions": {
    "activity": "Download multiple files",
    "threshold": "> 50 files in 10 minutes",
    "users": ["All users except excluded groups"]
  },
  "alerts": {
    "severity": "High",
    "notify": ["security@company.com"]
  },
  "actions": [
    "Suspend user",
    "Require MFA again"
  ]
}
```

**Politiques OAuth :**
```json
{
  "name": "Block OAuth apps with excessive permissions",
  "type": "OAuth App Policy",
  "conditions": {
    "permissions": "Read all mail + Read all files",
    "community_rating": "Not verified",
    "publisher": "Unverified"
  },
  "actions": [
    "Revoke app permission",
    "Notify admin"
  ]
}
```

**Politiques de Session (Proxy) :**
```json
{
  "name": "Protect sensitive documents in browser",
  "type": "Session Policy",
  "conditions": {
    "app": "Salesforce",
    "label": "Highly Confidential",
    "device": "Non-corporate managed"
  },
  "session_controls": {
    "monitor_only": false,
    "block_download": true,
    "block_copy": true,
    "block_print": true,
    "block_upload": true,
    "watermark_show": "Confidential - ${user.email}"
  }
}
```

### 2.4 DLP Cloud

```bash
# Microsoft Purview Information Protection + Cloud Apps
# Détection et protection des données sensibles dans le cloud

# Types de données détectables
# - Informations financières (IBAN, carte de crédit)
# - PII (SSN, email, téléphone)
# - Credentials (API keys, mots de passe)
# - Documents confidentiels (labels Azure Information Protection)

# Actions DLP :
# 1. Audit only (log l'événement)
# 2. Quarantine (déplacer le fichier)
# 3. Block (empêcher le partage)
# 4. Encrypt (appliquer une protection)
# 5. Governance (notifier l'utilisateur)

# Exemple : Détection de carte de crédit dans OneDrive
# 1. Scan des fichiers OneDrive via API
# 2. Si carte de crédit détectée → Quarantine + Notify Compliance
# 3. Audit log dans Sentinel
```

### 2.5 UEBA (User and Entity Behavior Analytics)

```bash
# Defender for Cloud Apps utilise le ML pour :
# - Établir une baseline de comportement par utilisateur
# - Détecter les anomalies :
#   • Impossible travel (connexion depuis 2 pays distants en < 1h)
#   • Activité depuis un IP Tor
#   • Volume de téléchargement inhabituel
#   • Partage massif de fichiers
#   • Tentatives d'accès échouées
#   • Nouveau type d'appareil
#   • Connexion depuis un nouveau pays
```

---

## 3. Netskope CASB

### 3.1 Architecture Netskope

```
┌──────────────┐     ┌───────────────┐     ┌─────────────┐
│  Endpoint    │────→│ Netskope      │────→│ SaaS/IaaS   │
│  +Agent      │     │ Cloud (NPA)   │     │ (Salesforce, │
│  (Netskope   │     │ Edge Proxy    │     │ GWS, AWS…)  │
│   Client)    │     │ + API Mode    │     │             │
└──────────────┘     └───────────────┘     └─────────────┘
                     │
                     ├── CASB (API + Proxy)
                     ├── SWG (Web Security)
                     ├── ZTNA (Private Access)
                     └── DLP (Data Protection)
```

### 3.2 Netskope CASB Features

| Feature | Description | CLI/API |
|---------|-------------|---------|
| **App Discovery** | 65,000+ apps identifiées | API REST |
| **Cloud Confidence Index** | Score de risque par app | API REST |
| **Real-time Protection** | Proxy reverse/inline | Steering config |
| **DLP Cloud** | 1,000+ data identifiers | DLP policies |
| **UEBA** | ML-based anomaly detection | Automation |
| **CSPM** | IaaS configuration audit | API scanning |
| **Zero Trust** | App access control | Private Access |

### 3.3 Politiques Netskope

```json
{
  "name": "Block Upload to Unsanctioned Apps",
  "type": "Real-time Protection Policy",
  "criteria": [
    {
      "field": "app",
      "operator": "in",
      "value": ["Dropbox", "WeTransfer", "Google Drive Personal"]
    },
    {
      "field": "category",
      "operator": "equals",
      "value": "Cloud Storage"
    },
    {
      "field": "instance",
      "operator": "not_equals",
      "value": "corporate"
    }
  ],
  "action": "block",
  "alert": true
}
```

### 3.4 DLP Config Netskope

```json
{
  "policy": {
    "name": "GDPR Data Protection",
    "action": "block_upload",
    "data_identifiers": [
      {"id": "EMAIL", "min_count": 10},
      {"id": "CREDIT_CARD", "min_count": 1},
      {"id": "EU_PERSONAL_INFO", "min_count": 5}
    ],
    "apps": ["All Cloud Storage", "All Email"],
    "users": ["All"],
    "notification": {
      "user": "Your upload contains personal data and has been blocked",
      "admin": true
    }
  }
}
```

---

## 4. Palo Alto Prisma Cloud CASB

### 4.1 Prisma Cloud CASB

```bash
# Prisma Cloud (ex RedLock) intègre :
# - CSPM (configuration audit)
# - CWPP (runtime protection)
# - CIEM (cloud entitlements)
# - CASB (SaaS app security)

# Déploiement API :
# Connecter les apps SaaS via API connectors
# 1. Google Workspace
# 2. Microsoft 365
# 3. Salesforce
# 4. ServiceNow
# 5. Box
# 6. Dropbox

# API Prisma Cloud pour CASB
curl -X POST https://api.prismacloud.io/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# Lister les apps SaaS connectées
curl -H "x-redlock-auth: <TOKEN>" \
  https://api.prismacloud.io/casb/v2/app_instances

# Obtenir les alertes CASB
curl -H "x-redlock-auth: <TOKEN>" \
  https://api.prismacloud.io/alert/v2 \
  -d '{"timeRange": {"type": "relative", "value": {"amount": 24, "unit": "hour"}}, "policy.scope": ["casb"]}'
```

---

## 5. Use Cases CASB par Scénario

### 5.1 Scénario 1 : Shadow IT Discovery

```yaml
Problème: 200 apps SaaS non autorisées utilisées par les équipes
Solution CASB:
  1. Discovery: Upload des logs proxy (Zscaler, Palo Alto)
  2. Analyse: 65 apps à risque (score < 5/10)
  3. Sanction: 10 apps autorisées avec policies restrictives
  4. Unsanction: 55 apps bloquées via proxy/agent
  5. Monitoring: Réévaluation hebdomadaire
  6. Résultat: -75% d'exposition Shadow IT en 30 jours
```

### 5.2 Scénario 2 : DLP Cloud

```yaml
Problème: Données sensibles (cartes bleues, PII) dans Google Drive
Solution CASB:
  1. Scan API: Détection de 5,000 fichiers avec données sensibles
  2. Classification: Confidential, Highly Confidential
  3. Quarantine: 200 fichiers Highly Confidential déplacés
  4. Notification: Email aux propriétaires
  5. Policy: Block tout nouveau partage externe de fichiers labellisés
  6. Résultat: -90% d'exposition de données sensibles
```

### 5.3 Scénario 3 : OAuth App Governance

```yaml
Problème: 1,400 apps OAuth connectées à GWS/Office 365
Solution CASB:
  1. Discovery: Lister toutes les apps OAuth
  2. Risk Assessment: Vérifier permissions, publisher, community rating
  3. Revoke: 800 apps avec permissions excessives révoquées
  4. Policy: Auto-revoke toute nouvelle app avec permissions "read all mail"
  5. Approval: Workflow pour demande d'installation d'app
  6. Résultat: Surface d'attaque OAuth réduite de 60%
```

### 5.4 Scénario 4 : Accès Conditionnel Cloud

```yaml
Problème: Accès à Salesforce depuis des appareils non managés
Solution CASB:
  1. Session Control: Reverse proxy avec inspection
  2. Conditional Access: Block download depuis device non conformes
  3. Watermark: Affichage "Confidential" overlay
  4. Copy/Paste: Bloqué pour les documents sensibles
  5. Print: Désactivé en session
  6. Audit: Log complet des sessions
```

---

## 6. Implémentation CASB par Plateforme

### 6.1 Microsoft Defender for Cloud Apps — Guide Rapide

```bash
# Étape 1 : Activer le CASB
# Portail Azure → Security Center → Cloud Apps → Enable

# Étape 2 : Intégrer Defender for Endpoint
# Découverte automatique des apps cloud

# Étape 3 : Connecter les apps SaaS
# Cloud Apps → Connected Apps → API Connectors
# Connecter : Office 365, GWS, Salesforce, Box

# Étape 4 : Configurer les politiques
# 4.1 Anomaly detection policies (UEBA)
# 4.2 Activity policies (mass download, impossible travel)
# 4.3 OAuth app policies (permissions excessives)
# 4.4 Session policies (reverse proxy control)

# Étape 5 : Intégrer Sentinel
# Forward Cloud Apps alerts → Sentinel
# Analytics rules pour investigation
```

### 6.2 CASB API — Script d'Audit

```bash
#!/bin/bash
# casb-audit.sh — Audit des apps SaaS via API CASB

TOKEN=$(curl -s -X POST https://<tenant>.us.portal.cloudappsecurity.com/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "..."}' | jq -r '.token')

# 1. Apps non sanctionnées
echo "=== Shadow IT Apps ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us.portal.cloudappsecurity.com/api/v1/activities/discovery/applications/?type=unsanctioned" \
  | jq '.data[] | {App: .app_name, Score: .cloud_app_score, Users: .users_count}'

# 2. Alertes actives
echo "=== Active Alerts ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us.portal.cloudappsecurity.com/api/v1/alerts/?resolution=Open" \
  | jq '.data[] | {Title: .title, Severity: .severity, Created: .created}'

# 3. Apps OAuth à risque
echo "=== High Risk OAuth Apps ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://<tenant>.us.portal.cloudappsecurity.com/api/v1/sub_auth_tokens/?type=high_risk" \
  | jq '.data[] | {App: .app_name, Permissions: .permissions, Publisher: .publisher}'
```

---

## 7. Comparatif CASB

| Critère | Defender Cloud Apps | Netskope | Prisma Cloud |
|---------|--------------------|----------|--------------|
| **Type** | SaaS | SaaS + On-prem | SaaS |
| **Découverte** | Snapshot + Continuous | Proxy log + Agent | API + Agent |
| **Apps identifiées** | 30,000+ | 65,000+ | 40,000+ |
| **DLP** | ✓ O365+GWS | ✓ 1000+ identifiers | ✓ Unified |
| **UEBA** | ✓ | ✓ | ✓ |
| **Session control** | ✓ Reverse proxy | ✓ Inline/Reverse | ✓ Inline |
| **CSPM** | ✗ | ✓ | ✓ (natif) |
| **Zero Trust** | Partiel (Entra ID) | ✓ ZTNA | ✓ Prisma Access |
| **Prix** | Inclus E5 | Élevé | Très élevé |
| **Intégration SIEM** | Sentinel, Splunk | Splunk, ELK | Splunk, ELK |
| **Cloud Provider** | Azure | Multi-cloud | Multi-cloud |

## Pitfalls

- **Ne PAS** déployer un CASB en mode proxy sans tester la latence sur les apps critiques
- **Ne PAS** connecter les apps SaaS sans comprendre le scope des permissions API
- **TOUJOURS** commencer par le mode Discovery/Audit avant d'activer le blocage
- **TOUJOURS** exclure les comptes de service et break-glass des politiques restrictives
- Les CASB en mode API ne voient que les actions passées (pas de contrôle temps réel)
- Les connecteurs API nécessitent des droits admin étendus — évaluer le risque
- Les politiques de session peuvent altérer le rendu des applications web
- Les CASB ajoutent des points de défaillance uniques — prévoir HA
- Le coût CASB est souvent basé sur le nombre d'utilisateurs — budgétiser

## Ressources

- **Microsoft Defender for Cloud Apps**: https://docs.microsoft.com/en-us/defender-cloud-apps/
- **Netskope**: https://www.netskope.com/documentation
- **Prisma Cloud CASB**: https://docs.paloaltonetworks.com/prisma/prisma-cloud
- **Gartner CASB Magic Quadrant**: https://www.gartner.com/en/documents/3996076
- **CSA CASB Guidance**: https://cloudsecurityalliance.org/research/guidance/casb/
- **OWASP Cloud Security**: https://owasp.org/www-project-cloud-security/