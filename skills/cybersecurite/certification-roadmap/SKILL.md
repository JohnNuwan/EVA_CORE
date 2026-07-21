---
name: certification-roadmap
description: Roadmap des certifications cybersécurité — arbre décisionnel, parcours par rôle (pentester, SOC, management, cloud, OSINT, devsecops), progression débutant → expert, et tableaux comparatifs.
---

# Roadmap des Certifications Cybersécurité — Guide Stratégique

> **Objectif :** Donner une vision claire des parcours de certification possibles, du débutant à l'expert, par spécialité et par rôle.

---

## 1. Arbre Décisionnel Principal

```
Tu débutes en cybersécurité (0-2 ans d'expérience) ?
│
├── OUI
│   ├── Tu veux faire du technique ?
│   │   ├── OUI → Parcours Pentest
│   │   │   ├── CompTIA Security+ → CEH → OSCP → OSEP
│   │   │   └── LPIC-1 → GPEN → OSCP → CRTO
│   │   ├── OUI (Cloud) → Parcours Cloud
│   │   │   └── AWS CCP → SAA → Security Specialty
│   │   └── OUI (SOC) → Parcours Défense
│   │       ├── Security+ → CySA+ → GCIA → CISSP
│   │       └── LPIC-1 → RHCSA → GSEC → CISSP
│   │
│   ├── Tu veux faire du management ?
│   │   └── Parcours Management
│   │       ├── Security+ → CISSP → CCISO
│   │       └── CISA → CISM → CISSP → CRISC
│   │
│   ├── Tu veux faire de l'OSINT ?
│   │   └── Parcours OSINT
│   │       ├── IntelTechniques → SEC487 (GOSI) → FOR578 (GCTI)
│   │       └── OSINT-FR → MCSI OSINT → CTIA
│   │
│   └── Tu veux faire du DevSecOps ?
│       └── Parcours DevSecOps
│           ├── LPIC-1 → RHCE → CKS → AWS Security
│           └── CompTIA Secure → CKS → CCSK → CISSP
│
└── NON (déjà de l'expérience)
    ├── Technique pur → OSCP → OSEP → CRT
    ├── Management → CISSP → CISM → CRISC
    ├── Cloud → AWS Security → CCSK → CISSP
    └── Expert → SANS (GXPN, GCIH) → OSCE3 → CISSP
```

---

## 2. Parcours Pentest / Red Team

### Niveau Débutant (0-1 an)

| Certification | Contenu | Coût | Durée | Prérequis |
|--------------|---------|------|-------|-----------|
| **CompTIA Security+** | Fondamentaux cybersécurité | ~$350 | 2 mois | Aucun |
| **CEH** | Ethical hacking, 550 techniques | ~$1,200 | 3-4 mois | Security+ recommandé |
| **eJPT** | Pentest pratique (INE) | ~$400 | 1-2 mois | Réseaux + Linux |

**Recommandation** : eJPT > CEH (plus pratique, moins cher)

### Niveau Intermédiaire (1-3 ans)

| Certification | Contenu | Coût | Durée | Priorité |
|--------------|---------|------|-------|----------|
| **OSCP** | Pentest pratique 24h | ~$1,500 | 6 mois | ⭐⭐⭐ |
| **PNPT** | Practical Network Pentesting | ~$400 | 2-3 mois | ⭐⭐ |
| **CRTP** | Certified Red Team Pro | ~$400 | 1-2 mois | ⭐⭐ |
| **GPEN** | SANS Pentest | ~$6,000 | 5 jours | ⭐ |

### Niveau Avancé (3-5 ans)

| Certification | Contenu | Coût | Spécialité |
|--------------|---------|------|------------|
| **OSEP** | Advanced Evasion, AV bypass | ~$1,500 | Red Team avancé |
| **CRTO** | Red Team Operations | ~$500 | C2 frameworks |
| **OSED** | Windows Exploitation | ~$1,500 | Exploit dev |
| **CRTE** | Red Team Expert | ~$500 | AD exploitation |

### Niveau Expert (5+ ans)

| Certification | Contenu |
|--------------|---------|
| **OSCE3** | Expert (OSEP + OSEP + OSED) |
| **GXPN** | SANS Exploit Research |
| **LPT** | Licensed Penetration Tester (EC-Council) |
| **CISSP** | Management + technique (complément) |

---

## 3. Parcours Défense / Blue Team / SOC

### Niveau Débutant

| Certification | Contenu | Coût | Durée |
|--------------|---------|------|-------|
| **CompTIA Security+** | Fondamentaux | ~$350 | 2 mois |
| **CompTIA CySA+** | Cybersecurity Analyst | ~$380 | 2-3 mois |
| **GSEC** | SANS Security Essentials | ~$6,000 | 5 jours |

### Niveau Intermédiaire

| Certification | Contenu | Coût |
|--------------|---------|------|
| **GCIA** | SANS Intrusion Analyst | ~$6,000 |
| **GCIH** | SANS Incident Handling | ~$6,000 |
| **GCFA** | SANS Forensic Analysis | ~$6,000 |
| **CCNA** | Cisco Certified Network Associate | ~$300 |

### Niveau Avancé

| Certification | Contenu |
|--------------|---------|
| **GNFA** | SANS Network Forensics |
| **GCFA** | Advanced Forensic Analysis |
| **CISSP** | Security Management |
| **CISA** | Information Systems Auditor |

---

## 4. Parcours Management / Gouvernance

### Progression recommandée

```
Année 1-3              Année 3-5              Année 5-8              Année 8+
──────────────────────────────────────────────────────────────────────────────
Security+       →     CISSP          →     CISM            →     CCISO
                          ↓                     ↓
                       CISA                    CRISC
```

### Détail

| Certification | Focus | Coût | Prérequis |
|--------------|-------|------|-----------|
| **CompTIA Security+** | Fondamentaux sécurité | $350 | Aucun |
| **CISSP** | CSO/CISO level — 8 domains | $749 | 5 ans expérience |
| **CISA** | Audit, contrôle, compliance | $575 | 5 ans |
| **CISM** | Security management | $575 | 5 ans |
| **CRISC** | Risk management | $575 | 5 ans |
| **CCISO** | Executive CISO | $1,200 | 5 ans management |
| **CGEIT** | IT Governance | $575 | 5 ans |

### Pourquoi ces certifications ensemble ?

```
CISSP = « Je sais comment sécuriser »
CISA  = « Je sais auditer la sécurité »
CISM  = « Je sais gérer un programme sécurité »
CRISC = « Je sais gérer les risques IT »
CCISO = « Je suis CISO »
```

---

## 5. Parcours Cloud (AWS / Azure / GCP)

### Progression AWS Sécurité

```
Cloud Practitioner (CLF-C02)
        ↓
Solutions Architect Associate (SAA-C03)
        ↓
Security Specialty (SCS-C02)    ← Objectif principal
        ↓
Solutions Architect Professional (SAP-C02)

Autres certifications cloud importantes :
├── AWS Certified DevOps Engineer — Professional
├── AWS Certified Advanced Networking — Specialty
└── AWS Certified Machine Learning — Specialty
```

### Progression Azure Sécurité

```
AZ-900 (Azure Fundamentals)
        ↓
AZ-500 (Azure Security Engineer)    ← Objectif principal
        ↓
SC-900  (Security, Compliance, Identity)
SC-100  (Cybersecurity Architect)

Autres : SC-200 (Security Operations), MS-500 (Information Protection)
```

### Progression GCP Sécurité

```
Cloud Digital Leader
        ↓
Associate Cloud Engineer
        ↓
Professional Cloud Security Engineer  ← Objectif principal
        ↓
Professional Cloud Architect
```

### Comparatif Cloud

| Critère | AWS Security | Azure Security | GCP Security |
|---------|-------------|----------------|--------------|
| Prix | $300 | $165 | $200 |
| Difficile | Intermédiaire | Intermédiaire | Intermédiaire |
| Reconnaissance | Très haute | Haute | Moyenne-Haute |
| Demande marché | Très forte | Forte | Moyenne |
| Exam | 170min, 65q | 120min, 40-60q | 2h, 50-60q |

---

## 6. Parcours OSINT

### Progression

```
Niveau 1 : Fondamentaux (gratuit)
├── OSINT-FR Initiation (€200)
└── IntelTechniques Online Course ($500)

Niveau 2 : Intermédiaire
├── SANS SEC487 (OSINT) → GOSI ($6,000)
└── EC-Council CTIA ($1,200)

Niveau 3 : Avancé
├── SANS FOR578 (CTI) → GCTI ($6,000)
└── MCSI OSINT Expert ($50/mois)

Niveau 4 : Expert
├── MCSI OSINT Master ($50/mois)
└── SANS FOR585 (Smartphone Forensic) → GASF ($6,000)
```

### Parcours complémentaires

| Rôle | Certifications OSINT |
|------|---------------------|
| Analyste CTI | SANS FOR578, CTIA, MCSI CTI |
| Journaliste d'investigation | IntelTechniques, OSINT-FR |
| Enquêteur privé | OSINT-FR Expert, MCSI OSINT |
| Pentester OSINT | SANS SEC487, OSCP |
| Police / Gendarme | OSINT-FR, SANS SEC487 |

---

## 7. Parcours Linux

### Pour la cybersécurité

```
Débutant (Linux basics)
├── CompTIA Linux+ ($358)
└── LPIC-1 ($400)

Intermédiaire (Administration)
├── RHCSA ($400) — Pratique, recommandé
└── LPIC-2 ($400)

Avancé (Sécurité + Automation)
├── RHCE ($400) — Ansible
├── LPIC-3 Security ($200)
└── LFCS ($200) — Ubuntu/Debian
```

### Importance par rôle

| Rôle | Certification recommandée | Pourquoi |
|------|--------------------------|----------|
| Pentester | RHCSA | Exploitation Linux, PE |
| SOC Analyst | LPIC-1 | Logs, services, audit |
| DevOps Sec | RHCE | Automation sécurisée |
| Security Engineer | LPIC-2 | Hardening, SElinux |
| CTI / Forensics | LFCS | Volatile, disk forensics |

---

## 8. Parcours DevSecOps

### Pipeline recommandé

```
Niveau 1 : Fondations
├── CompTIA Security+
├── LPIC-1
└── AWS Cloud Practitioner

Niveau 2 : Développement sécurisé
├── Certified Kubernetes Administrator (CKA)
├── Certified Kubernetes Security (CKS)
├── AWS Security Specialty
└── CISSP (Domaine 8 + Risk)

Niveau 3 : DevSecOps avancé
├── RHCE (Ansible automation)
├── CKS (Kubernetes security)
├── AWS DevOps Engineer Professional
└── CCSK (Cloud Security)
```

### Certifications DevSecOps clés

| Certification | Focus | Prix | Durée |
|--------------|-------|------|-------|
| **CKA** | Kubernetes Administration | $395 | 2-3 mois |
| **CKAD** | Kubernetes Development | $395 | 2-3 mois |
| **CKS** | Kubernetes Security | $395 | 3-4 mois |
| **CCSK** | Cloud Security | $400 | 1-2 mois |
| **CISSP** | General Security | $749 | 6 mois |
| **AWS SCS** | AWS Security | $300 | 3-4 mois |
| **RHCE** | RHEL Automation | $400 | 3-4 mois |
| **CSSLP** | Secure Software Lifecycle | $599 | 3-6 mois |

---

## 9. Tableau Récapitulatif Complet

| Certification | Coût | Durée | Pratique | Reconnaissance | DoD Approved |
|--------------|------|-------|----------|---------------|--------------|
| Security+ | $350 | 2 mois | Non | Large | Oui (IAT II) |
| CEH | $1,200 | 3 mois | Labs | Corporate | Oui |
| OSCP | $1,500 | 6 mois | **100%** | Technique | Non |
| CISSP | $749 | 6 mois | Non | **Maximale** | Oui (IAM III) |
| CISA | $575 | 4 mois | Non | Audit | Oui |
| CISM | $575 | 4 mois | Non | Management | Oui |
| AWS SCS | $300 | 3 mois | Labs | Cloud | Non |
| RHCSA | $400 | 3 mois | **100%** | Linux | Non |
| LPIC-1 | $400 | 2 mois | Non | Linux | Non |
| SANS (1 exam) | $6,000 | 5 jours | Mixte | **Élite** | Oui |
| OSINT-FR | €200 | 2 sem | Oui | Francophonie | Non |
| eJPT | $400 | 1 mois | **100%** | Junior | Non |
| PNPT | $400 | 2 mois | **100%** | Intermédiaire | Non |
| CKA | $395 | 2 mois | Oui | Kubernetes | Non |
| CKS | $395 | 3 mois | Oui | K8s Security | Non |

---

## 10. Budget Total par Parcours

| Parcours | Certifications | Coût total (examen) | Avec prépa |
|----------|---------------|-------------------|-----------|
| **Pentest** | Security+ → CEH → OSCP → OSEP | ~$3,500 | ~$5,000 |
| **Pentest (alternatif)** | eJPT → PNPT → OSCP → CRTO | ~$2,800 | ~$4,000 |
| **Management** | Security+ → CISSP → CISM → CRISC | ~$2,250 | ~$3,500 |
| **Cloud** | AWS CCP → SAA → SCS → SAP | ~$850 | ~$1,500 |
| **SOC** | Security+ → CySA+ → GCIA → CISSP | ~$1,500 | ~$8,000 |
| **DevSecOps** | LPIC-1 → CKA → CKS → AWS SCS | ~$1,500 | ~$2,500 |
| **OSINT** | IntelTechniques → GOSI → GCTI | ~$12,500 | ~$15,000 |

---

## 11. Roadmap Temporelle

### Année 1 : Débutant

```
Mois 1-2 : CompTIA Security+ (fondamentaux)
Mois 3-4 : LPIC-1 OU Linux+ (Linux)
Mois 5-6 : AWS Cloud Practitioner (cloud)
Mois 7-8 : eJPT OU CEH (ethical hacking intro)
Mois 9-10 : Labs Hack The Box / TryHackMe
Mois 11-12 : Choisir sa spécialité
```

### Année 2-3 : Intermédiaire

```
Parcours Pentest : OSCP (6 mois) → CRTP (1 mois) → HTB CTFs
Parcours Cloud    : AWS SAA (3 mois) → AWS Security (3 mois) → Labs
Parcours SOC      : CySA+ (2 mois) → GCIA/GCIH (5 jours SANS)
Parcours OSINT    : IntelTechniques (1 mois) → CTIA (3 mois)
```

### Année 4-5 : Avancé

```
Pentest : OSEP → CRTO → OSCE3
Cloud   : AWS SAP → CCSK → CISSP
Management : CISSP → CISM → CRISC
OSINT   : SANS FOR578 (GCTI) → MCSI OSINT
```

### Année 6+ : Expert

```
Pentest : GXPN → LPT → CRT
Management : CCISO
OSINT   : MCSI OSINT Master
Cloud   : Toutes Specialty AWS
```

---

## 12. Combinaisons Puissantes

| Combo | Pour quel poste | Coût total | ROI |
|-------|-----------------|-----------|-----|
| **OSCP + CISSP** | Consultant sécurité | $2,250 | ⭐⭐⭐⭐⭐ |
| **AWS SCS + CISSP** | Cloud Security Architect | $1,050 | ⭐⭐⭐⭐⭐ |
| **OSCP + CRTO + OSCE3** | Pentester sénior | $3,500 | ⭐⭐⭐⭐ |
| **CISSP + CISA + CISM** | RSSI / CISO | $1,900 | ⭐⭐⭐⭐⭐ |
| **RHCSA + RHCE + LPIC-3** | Linux security engineer | $1,000 | ⭐⭐⭐⭐ |
| **CKA + CKS + AWS SCS** | Cloud DevSecOps | $1,100 | ⭐⭐⭐⭐ |
| **SANS SEC487 + FOR578** | CTI Analyst | $12,000 | ⭐⭐⭐ |
| **OSCP + PNPT + CRTP** | AD pentester | $2,400 | ⭐⭐⭐⭐ |

---

## 13. Conseils Stratégiques

### Ne PAS faire

- **Tout en même temps** : une certification à la fois
- **Les certifications inutiles** : certaines sont des attrape-touristes (vérifier la reconnaissance)
- **SANS trop tôt** : $6,000 pour un débutant n'a pas de sens
- **Négliger l'expérience** : la certification sans pratique ne vaut rien

### À FAIRE

1. **Commencer par Security+ ou LPIC-1** (bon marché, bien reconnu)
2. **Choisir une spécialité après la 1ère certification**
3. **Préférer le pratique au théorique** (OSCP > CEH)
4. **Valider chaque certification par un projet réel**
5. **Cibler les certifications DoD approved** pour les postes gouvernementaux
6. **Mettre à jour LinkedIn/CV dès l'obtention**
7. **Enchaîner les certifications complémentaires** (combo power)

---

## 14. Liens Utiles

- DoD Approved 8140/8570 : https://public.cyber.mil/cw/ecm/
- Credly (badges) : https://www.credly.com
- Acclaim (badges) : https://www.youracclaim.com
- Reddit r/cybersecurity : https://reddit.com/r/cybersecurity
- Paul Jerimy's Sec Cert Roadmap : https://pauljerimy.com/security-certification-roadmap/
- r/cybersecurity — Career Questions : https://reddit.com/r/cybersecurity/wiki/certifications
- IAPP (Privacy) : https://iapp.org/certify/
- MITRE ATT&CK : https://attack.mitre.org
- NIST CSF : https://www.nist.gov/cyberframework
