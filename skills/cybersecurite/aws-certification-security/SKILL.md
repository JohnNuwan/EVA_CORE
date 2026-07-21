---
name: aws-certification-security
description: Guide complet des certifications AWS liées à la sécurité — AWS Certified Security - Specialty, Solutions Architect, Cloud Practitioner, et parcours de certification AWS.
---

# Certifications AWS — Guide Complet Volet Sécurité

> **Organisme :** Amazon Web Services (AWS)
> > **Certifications sécurité :** AWS Certified Security - Specialty, AWS Certified Solutions Architect, AWS Certified Cloud Practitioner
> **Niveau :** Débutant à Expert
> **Durée de validité :** 3 ans

---

## 1. Vue d'ensemble des certifications AWS

### Pyramide des certifications AWS

```
                    ┌──────────────────────┐
                    │  AWS Certified        │
                    │  Security - Specialty │  ← Sécurité pure
                    ├──────────────────────┤
                    │  AWS Certified        │
                    │  Solutions Architect  │
                    │  - Professional       │  ← Architecture sécurisée
                    ├──────────────────────┤
                    │  AWS Certified        │
                    │  Solutions Architect  │
                    │  - Associate          │  ← Volet sécurité
                    ├──────────────────────┤
                    │  AWS Certified        │
                    │  Cloud Practitioner   │  ← Fondamentaux sécurité
                    └──────────────────────┘
```

---

## 2. AWS Certified Cloud Practitioner (CLF-C02)

> **Prérequis :** Aucun
> **Coût :** $100 USD
> **Durée :** 90 minutes
> **Questions :** 65 (QCM, réponses multiples)
> **Seuil :** 700/1000

### Contenu lié à la sécurité

- **Domaine 4 :** Sécurité et conformité (30%)
- Concepts de base : Shared Responsibility Model
- AWS Artifact, AWS Shield, AWS WAF
- AWS KMS, CloudHSM
- AWS Config, CloudTrail, GuardDuty
- AWS IAM (Identity and Access Management)
- AWS Compliance Programs (HIPAA, SOC, PCI-DSS)
- AWS Well-Architected Framework (Security Pillar)

### Préparation

| Ressource | Prix |
|-----------|------|
| AWS Skill Builder (Digital) | Gratuit |
| AWS Cloud Practitioner Essentials | Gratuit (6h) |
| Tutorials Dojo Practice Tests | ~$15 |
| Neal Davis — Udemy | ~$25 |
| Maarek — Udemy | ~$25 |

---

## 3. AWS Certified Solutions Architect — Associate (SAA-C03)

> **Prérequis :** Cloud Practitioner ou expérience
> **Coût :** $150 USD
> **Durée :** 130 minutes
> **Questions :** 65
> **Seuil :** 720/1000

### Contenu sécurité (30% de l'examen)

- **IAM** : Policies, roles, trust relationships, IAM Identity Center
- **Réseau sécurisé** : VPC, Security Groups, NACL, VPC endpoints, PrivateLink
- **Chiffrement** : KMS, CloudHSM, S3 encryption (SSE-S3, SSE-KMS, SSE-C)
- **Monitoring** : CloudTrail, CloudWatch, Config, GuardDuty, Security Hub
- **Protection** : AWS WAF, AWS Shield, AWS Firewall Manager
- **Gestion des secrets** : AWS Secrets Manager, Parameter Store
- **Compliance** : AWS Artifact, Config Rules
- **Design sécurisé** : Least privilege principle, defense in depth

### Sécurité dans les 4 piliers

| Pilier | Exemples sécurité |
|--------|------------------|
| Secure Access | IAM, roles, policies, MFA |
| Secure Infrastructure | VPC, SG, NACL, WAF |
| Data Protection | KMS, S3 replication, encryption |
| Detective Controls | CloudTrail, GuardDuty, Security Hub |

### Préparation

| Ressource | Prix |
|-----------|------|
| AWS Skill Builder (SAA) | Gratuit |
| Stephane Maarek (Udemy) | ~$25 |
| Tutorials Dojo Practice Exams | ~$15 |
| AWS Well-Architected Lab | Gratuit |
| AWS Workshops (Security) | Gratuit |
| Jon Bonso — SAA Tests | ~$15 |

---

## 4. AWS Certified Solutions Architect — Professional (SAP-C02)

> **Prérequis :** SAA-C03 ou expérience avancée
> **Coût :** $300 USD
> **Durée :** 180 minutes
> **Questions :** 75
> **Seuil :** 750/1000

### Contenu sécurité avancé

- **Architecture multi-comptes** : AWS Organizations, SCP, OU, Guardrails
- **Sécurité cross-account** : Cross-account roles, resource-based policies, VPC sharing
- **Chiffrement avancé** : KMS multi-region, HSM, envelope encryption, key rotation
- **Réseau complexe** : Transit Gateway, Direct Connect, VPN, PrivateLink, Network Firewall
- **Sécurité des données** : S3 Object Lock, Macie, Lake Formation
- **Incident response** : Automated remediation, GuardDuty → Lambda → Remediation
- **Compliance automation** : Config rules, Service Catalog, Security Hub

---

## 5. AWS Certified Security — Specialty (SCS-C02)

> **La certification sécurité pure d'AWS**
> **Prérequis :** 5 ans d'expérience IT + 2 ans en sécurité AWS
> **Coût :** $300 USD
> **Durée :** 170 minutes
> **Questions :** 65
> **Seuil :** 750/1000

### Domaines de l'examen

| Domaine | Poids |
|---------|-------|
| Domaine 1 : Threat Detection and Incident Response | 14% |
| Domaine 2 : Security Logging and Monitoring | 18% |
| Domaine 3 : Infrastructure Security | 20% |
| Domaine 4 : Identity and Access Management | 20% |
| Domaine 5 : Data Protection | 20% |
| Domaine 6 : Management and Security Governance | 8% |

### Détail par domaine

#### Domaine 1 : Threat Detection & Incident Response (14%)

- **Détection** : GuardDuty, Security Hub, Detective, Inspector
- **Réponse** : Automated response avec Lambda + Step Functions
- **Forensic** : AWS EC2 forensics (snapshot analysis), EBS direct API
- **Playbooks** : Incident Response Plan, AWS Incident Response Playbook
- **AWS Config** : Rules, conformance packs, remediation

#### Domaine 2 : Security Logging & Monitoring (18%)

- **CloudTrail** : Logging management, data events, Insights
- **CloudWatch Logs** : Log groups, metrics filters, alarms
- **VPC Flow Logs** : Network traffic logging
- **ELB Access Logs** : Application traffic logging
- **S3 Access Logs** : Object-level logging (server access, CloudTrail data events)
- **Centralized logging** : Cross-account log aggregation (S3, OpenSearch)
- **SIEM integration** : Splunk, ELK, Sumo Logic

#### Domaine 3 : Infrastructure Security (20%)

- **VPC Design** : Subnets, route tables, NAT, IGW, VPC peering, Transit Gateway
- **Security Groups & NACL** : Stateful vs stateless, ingress/egress rules
- **AWS WAF** : Web ACLs, rate-based rules, managed rules, Bot Control
- **AWS Shield** : Standard vs Advanced, DDoS protection, mitigations
- **AWS Network Firewall** : Stateful inspection, intrusion prevention
- **AWS Firewall Manager** : Centralized policy management
- **PrivateLink & VPC Endpoints** : Secure access to AWS services
- **Direct Connect** : Private connectivity, encryption, MACsec
- **AWS VPN** : Site-to-Site, Client VPN, encryption

#### Domaine 4 : Identity and Access Management (20%)

- **IAM Policies** : Customer-managed, AWS-managed, inline, resource-based
- **IAM Roles** : Trust policies, service-linked roles, passRole
- **IAM Policy Evaluation** : Deny override, SCP, permissions boundary
- **AWS Organizations** : SCP, OU, delegated administration
- **IAM Identity Center (SSO)** : Federation, SCIM provisioning
- **Cognito** : User pools, identity pools, federation
- **Federation** : SAML 2.0, OIDC, AWS IAM Identity Center
- **Access Analyzer** : IAM Access Analyzer, S3 Access Analyzer
- **Least privilege** : Policy generation, credential analysis

#### Domaine 5 : Data Protection (20%)

- **S3 Security** : Block Public Access, bucket policies, Object Lock, Macie
- **Encryption at rest** : KMS (CMK, automatic key rotation, multi-Region keys)
- **Encryption in transit** : TLS, mTLS, ACM, VPN
- **KMS** : Key policies, grants, key rotation, custom key stores (CloudHSM)
- **CloudHSM** : FIPS 140-2 Level 3, PKCS#11, JCE
- **Secrets Manager** : Secret rotation, RDS Proxy integration
- **Parameter Store** : SecureString parameter, tiered pricing
- **Certificate Manager (ACM)** : Public/private certificates, integration
- **Macie** : Sensitive data discovery, classification, automated remediation
- **Data Lifecycle Manager** : EBS snapshot management, AMI policies

#### Domaine 6 : Management & Security Governance (8%)

- **AWS Config** : Rules, conformance packs, compliance history
- **Security Hub** : Consolidated findings, security standards (CIS, PCI-DSS)
- **AWS Artifact** : Compliance reports, agreements
- **Well-Architected Framework** : Security Pillar review
- **Service Catalog** : Security-approved products, portfolio management
- **CloudFormation Guard** : Policy-as-code
- **AWS Control Tower** : Landing zone, OU, Guardrails
- **Trusted Advisor** : Security checks, best practices

### Compétences pratiques nécessaires

- **CLI AWS** : aws-cli, jq, scripting bash
- **Terraform / CloudFormation** : Infrastructure as Code
- **Python** : Lambda functions, automation scripts
- **Linux** : OS hardening, auditing (CIS Benchmarks)
- **Réseaux** : TCP/IP, routing, VPN, TLS

### Préparation

| Ressource | Prix | Notes |
|-----------|------|-------|
| AWS Exam Readiness (Security) | Gratuit | 2h digital |
| Stephane Maarek — AWS Security Udemy | ~$25 | Excellente formation |
| Zeal Vora — AWS Security | ~$25 | Approfondi |
| Tutorials Dojo SCS Practice Exams | ~$15 | Meilleurs practice tests |
| Jon Bonso — Security Specialty | ~$15 | Quiz + cheat sheets |
| AWS Security Workshops | Gratuit | Workshops.aws/security |
| AWS Well-Architected Labs | Gratuit | Labs pratiques |
| Neal Davis — Digital Cloud Training | ~$25 | Vidéos + labs |

---

## 6. Parcours recommandé

### Parcours sécurité complet

```
Phase 1 : Fondamentaux (1 mois)
├── AWS Cloud Practitioner
├── Comprendre le Shared Responsibility Model
└── AWS Free Tier — créer un compte, tester

Phase 2 : Architecture (2-3 mois)
├── AWS Solutions Architect Associate
├── IAM, VPC, KMS, CloudTrail, S3 Security
└── Well-Architected Framework Security Pillar

Phase 3 : Sécurité approfondie (3-4 mois)
├── AWS Security Specialty (SCS-C02)
├── Labs : GuardDuty, WAF, Shield, Macie
├── Incident Response automation
└── Terraform/CloudFormation security

Phase 4 : Expert (2-3 mois)
├── AWS Solutions Architect Professional
├── Multi-compte, SCP, Organizations
├── Network Firewall, Transit Gateway
└── Compliance automation
```

---

## 7. Coûts Totaux

| Certification | Prix examen | Préparation (estimation) | Total |
|--------------|------------|-------------------------|-------|
| Cloud Practitioner | $100 | $50 | ~$150 |
| Solutions Architect Associate | $150 | $100 | ~$250 |
| Security Specialty | $300 | $150 | ~$450 |
| Solutions Architect Professional | $300 | $200 | ~$500 |
| **Parcours sécurité complet** | **$850** | **$500** | **~$1,350** |

---

## 8. Ressources gratuites

- **AWS Skill Builder** : https://explore.skillbuilder.aws
- **AWS Workshops** : https://workshops.aws/security
- **AWS Well-Architected Labs** : https://www.wellarchitectedlabs.com/security/
- **AWS Security Blog** : https://aws.amazon.com/blogs/security/
- **AWS Documentation** : https://docs.aws.amazon.com/security/
- **AWS Free Tier** : https://aws.amazon.com/free/
- **AWS Quick Starts** : https://aws.amazon.com/quickstart/
- **CloudFormation Guard** : https://github.com/aws-cloudformation/cloudformation-guard
- **AWS Security Reference** : https://docs.aws.amazon.com/security-reference-architecture/

---

## 9. Maintien des certifications

- **Toutes les certifications AWS** : valides **3 ans**
- **Recertification** : Repasser le même examen (version actualisée) ou un examen de niveau supérieur
- **AWS recertification** : 50% de réduction sur le nouvel examen
- Pas de CPE, pas de frais annuels

---

## 10. Conseils pour l'examen Security Specialty

1. **Maîtriser KMS** : key policies, grants, key rotation, envelope encryption, multi-Region
2. **Comprendre GuardDuty vs Inspector vs Macie** : savoir les différencier
3. **VPC endpoints** : Gateway vs Interface, PrivateLink, quand utiliser quoi
4. **SCP, IAM, permissions boundary** : exactement comment les policies sont évaluées
5. **CloudTrail Insights** : détection d'activités inhabituelles
6. **AWS Config rules** : managed rules, custom rules, conformance packs, remediation
7. **WAF vs Shield vs Firewall Manager** : cas d'usage de chaque service
8. **Shared Responsibility Model** : questions récurrentes

---

## 11. Liens Utiles

- AWS Certifications : https://aws.amazon.com/certification/
- AWS Security Specialty : https://aws.amazon.com/certification/certified-security-specialty/
- Exam Guide SCS-C02 : https://d1.awsstatic.com/training-and-certification/docs-security-spec/AWS-Certified-Security-Specialty_Exam-Guide.pdf
- AWS re:Post (community) : https://repost.aws
- AWS Security Blog : https://aws.amazon.com/blogs/security/
- AWS Well-Architected Framework Security Pillar : https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/