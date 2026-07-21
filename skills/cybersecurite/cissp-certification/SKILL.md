---
name: cissp-certification
description: Guide complet de la certification CISSP (Certified Information Systems Security Professional) d'ISC2 — 8 domaines, préparation, examen, ressources et conseils.
---

# Certification CISSP (Certified Information Systems Security Professional) — Guide Complet

> **Organisme :** ISC2
> **Version actuelle :** CISSP 2024 (révision annuelle des domaines)
> **Niveau :** Avancé (management + technique)
> **Durée de validité :** 3 ans (CPE requis)
> **Accréditation :** ANSI ISO/IEC 17024, DoDM 8140.03

---

## 1. Présentation

Le **CISSP** est la certification de référence pour les professionnels de la cybersécurité expérimentés. Contrairement au CEH ou OSCP (techniques), le CISSP couvre la **gestion de la sécurité** à un niveau stratégique : politique de sécurité, architecture, risk management, IAM, sécurité des opérations, développement sécurisé, etc.

### Surnom : « Le Golden Gate » de la cybersécurité

- Considérée comme la **certification la plus prestigieuse** du secteur
- Requise par de nombreux postes de **CISO, RSSI, Security Architect**
- Reconnue mondialement comme le standard pour les **décideurs sécurité**
- **Salaire moyen** : $125K–200K+ (varie selon région)

---

## 2. Les 8 Domaines CISSP (CBK — Common Body of Knowledge)

### Domaine 1 : Security and Risk Management (15%)

- **Confidentialité, Intégrité, Disponibilité (CIA Triad)**
- Gouvernance de la sécurité (ISO 27001, NIST CSF, COBIT)
- Compliance et aspects légaux (RGPD, HIPAA, SOX, PCI-DSS)
- Risk management (NIST SP 800-30, ISO 31000, FAIR)
- Business Continuity (BCP) & Disaster Recovery (DRP)
- Ethique professionnelle (ISC2 Code of Ethics)
- Sécurité des fournisseurs et tierces parties

### Domaine 2 : Asset Security (10%)

- **Classification des données et des actifs**
- Gestion du cycle de vie des données (création → destruction)
- Protection des données au repos, en transit, en utilisation
- Data Loss Prevention (DLP)
- Gestion des supports (sanitization, destruction)
- Privacy et protection des données à caractère personnel

### Domaine 3 : Security Architecture and Engineering (13%)

- **Modèles de sécurité** (Bell-LaPadula, Biba, Clark-Wilson, Brewer-Nash)
- **Architecture de sécurité** : systèmes d'exploitation, virtualisation, cloud
- Cryptographie (symétrique, asymétrique, hachage, PKI, TLS)
- **Principes de conception sécurisée** (defense-in-depth, least privilege, zero trust)
- Sécurité physique (périmètre, accès, surveillance)
- Évaluation et certification de la sécurité des systèmes

### Domaine 4 : Communication and Network Security (13%)

- **Modèle OSI et TCP/IP** (sécurité par couche)
- Architectures réseau sécurisées (DMZ, VLAN, VPN, SD-WAN)
- Protocoles sécurisés (TLS, IPsec, SSH, HTTPS)
- **Segmentation réseau et micro-segmentation**
- Sécurité des accès distants et télétravail
- Contrôle d'accès réseau (NAC, 802.1X)

### Domaine 5 : Identity and Access Management (IAM) (13%)

- **Contrôle d'accès** (DAC, MAC, RBAC, ABAC)
- Authentification (MFA, SSO, Kerberos, RADIUS, LDAP)
- **Fédération d'identité** (SAML, OAuth 2.0, OIDC)
- Provisioning et déprovisioning des comptes
- Gestion des sessions et des accès privilégiés (PAM)
- Cycle de vie des identités

### Domaine 6 : Security Assessment and Testing (12%)

- **Audit et évaluation de la sécurité**
- Test d'intrusion (méthodologies, portée)
- Vulnerability assessment (scanning, reporting)
- **Log management et SIEM**
- Test de sécurité des applications (SAST, DAST, IAST)
- Security Control Testing (SOC 2, ISO 27001 audits)

### Domaine 7 : Security Operations (13%)

- **SOC — Security Operations Center**
- **Gestion des incidents** (NIST SP 800-61, SANS PICERL)
- **Forensic investigation** (acquisition, préservation, analyse)
- Disaster Recovery (DR) et continuité des opérations
- Gestion des changements et des configurations
- **Durcissement des systèmes** (CIS Benchmarks, STIGs)

### Domaine 8 : Software Development Security (11%)

- **SDLC sécurisé** (Secure SDLC, DevSecOps)
- Modèles de maturité (BSIMM, OWASP SAMM)
- Sécurité des architectures logicielles (microservices, API)
- **OWASP Top 10** et mitigation
- Gestion des vulnérabilités logicielles
- Sécurité des pipelines CI/CD et IaC

---

## 3. Examen CISSP

### Format

| Critère | Détail |
|---------|--------|
| Durée | **3 heures** (format CAT adaptatif) |
| Questions | 100–150 questions (variable selon performance) |
| Format | **CAT** (Computerized Adaptive Testing) — s'adapte au niveau |
| Typologie | QCM, drag-and-drop, hotspot |
| Seuil | Variable (algorithmique, environ 700/1000) |
| Langues | Anglais, français, allemand, espagnol, etc. |
| Lieu | **Pearson VUE** (centre ou surveillé en ligne) |

### Particularité du CAT

Le CISSP utilise un système adaptatif :
- Commence par des questions de difficulté moyenne
- Si bonnes réponses → questions plus difficiles
- Si mauvaises réponses → questions plus faciles
- L'algorithme arrête l'examen une fois que la certitude statistique est atteinte
- On peut avoir **100 questions** (excellent) ou **150 questions** (limite)

### Règle importante : « Think like a manager »

Le CISSP teste la **prise de décision managériale**, pas l'exécution technique. Même si la question décrit un problème technique, la **bonne réponse est souvent managériale** : politique, procédure, processus, sensibilisation — plutôt que le correctif technique immédiat.

---

## 4. Prérequis

**5 ans d'expérience professionnelle** dans au moins 2 des 8 domaines CISSP.

Ou **4 ans** si l'on possède :
- Diplôme universitaire (licence ou master)
- Autre certification ISC2
- Autre certification reconnue (CISA, CISM, CEH, etc.)

**Sans expérience** : Possibilité de passer l'examen et obtenir le titre **Associate of ISC2** (4 ans pour acquérir l'expérience).

---

## 5. Préparation

### Parcours recommandé

| Phase | Durée | Activité |
|-------|-------|----------|
| 0. Expérience requise | 5 ans (ou 4+ diplôme) | Expérience pro sécurité |
| 1. Apprentissage | 3–6 mois | Lectures, vidéos, notes |
| 2. Practice tests | 1–2 mois | 1000+ questions |
| 3. Révision ciblée | 2–4 sem | Domaines faibles |
| 4. Examen blanc | 1–2 sem | Simulateurs |
| 5. Examen | 3h | Le jour J |

### Ressources clés

| Ressource | Type | Prix |
|-----------|------|------|
| Official ISC2 CISSP CBK (5th Ed.) | Manuel | ~$150 |
| OSG (Official Study Guide) — Mike Chapple | Livre | ~$60 |
| Sybex CISSP Study Guide (11th Ed.) | Livre | ~$55 |
| Sybex CISSP Practice Tests | Tests | ~$40 |
| Destination Certification CISSP (MasterClass) | Cours vidéo | ~$300 |
| Kelly Handerhan — Cybrary CISSP | Vidéos (gratuit) | Gratuit |
| Mike Chapple — LinkedIn Learning | Vidéos | Abonnement |
| Boson CISSP Practice Exams | Tests | ~$99 |
| LearnZapp CISSP App | Mobile + tests | ~$15/mois |
| ISC2 Official Training | Cours | $895–$2,995 |

### Meilleures ressources gratuites

- **Kelly Handerhan — Why You Will Pass the CISSP** (YouTube)
- **Larry Greenblatt — CISSP Exam Tips** (YouTube)
- **Prabh Nair — Coffee Shots CISSP** (YouTube)
- **Destination Certification Mind Maps** (YouTube)
- **IT Dojo — CISSP Questions** (YouTube)
- **11th Hour CISSP** (livre, ~$30)

### Flashcards par domaine

Utiliser Anki ou Quizlet pour créer des flashcards sur :
- Modèles de sécurité (Bell-LaPadula, Biba, Clark-Wilson)
- Types de contrôles (préventif, détectif, correctif, dissuasif, compensatoire)
- Standards (ISO 27001/2, NIST SP 800, PCI-DSS)
- Concepts cryptographiques (AES, RSA, ECC, DH, TLS)
- Processus de gestion des incidents (PICERL, NIST)

---

## 6. Coûts Totaux

| Élément | Prix (USD) |
|---------|-----------|
| Examen CISSP | $749 |
| ISC2 Annual Membership | $135/an |
| ISC2 Official Training (5 jours) | $2,395–2,995 |
| Sybex OSG + Practice Tests | ~$100 |
| Boson Practice Exams | ~$99 |
| LearnZapp (3 mois) | ~$45 |
| **Total estimé (auto-study)** | **~$950** |
| **Total estimé (formation)** | **~$3,200** |

---

## 7. Maintien de la certification

- **Valide** : 3 ans
- **CPE requis** : 120 CPE (40 CPE/an)
- **Frais** : $135/an cotisation ISC2
- **Sanction** : Suspension si CPE non atteints

Sources de CPE :
- Conférences (BlackHat, RSA, DEF CON) — 1 CPE/heure
- Webinaires ISC2 — jusqu'à 7 CPE/session (max 20/an)
- Cours de formation — 1 CPE/heure (max 30/an)
- Publications (articles, livres) — 10 CPE/article (max 30/an)
- Enseignement, mentorat — jusqu'à 10 CPE/session
- Participation à des chapitres ISC2

---

## 8. Profils types qui passent le CISSP

| Poste | Pourquoi le CISSP |
|-------|------------------|
| RSSI / CISO | Valide la vision stratégique de la sécurité |
| Security Architect | Valide la conception de solutions sécurisées |
| Security Manager | Valide la gestion des programmes de sécurité |
| IT Director | Reconnaissance globale pour la direction |
| Consultant | Crédibilité auprès des clients |
| Military/Government | Obligatoire pour DoDM 8140/IAT Level III |

---

## 9. Conseils pour l'examen

### Avant l'examen
1. **Lire la question 2 fois** — identifier le PIÈGE (mots comme LE, MOST, BEST, FIRST, LAST)
2. **Penser management, pas technique** — la réponse correcte est souvent la politique ou le processus
3. **Éliminer** : 2 réponses sont généralement clairement fausses
4. **Ne pas hésiter** sur les réponses — le CAT s'adapte, inutile de stresser
5. **Dormir 8h la veille** — fatigué = moins bon au CAT

### Pendant l'examen
- Ne pas rush : l'adaptatif est plus long si vous répondez vite et mal
- Si ça s'arrête à 100 questions → bonne chance (vous avez probablement réussi)
- Si ça continue jusqu'à 150 → serré mais possible
- Même entre 130 et 150, rester concentré
- Utiliser le scratchpad fourni (feuille plastifiée)

### Après l'examen
- Résultat IMMÉDIAT à l'écran (impression officielle à demander)
- Endorsement : un membre ISC2 existant doit vous parrainer (ou ISC2 le fait)
- L'endorsement peut prendre 4–6 semaines

---

## 10. Liens Utiles

- ISC2 CISSP : https://www.isc2.org/certifications/cissp
- CISSP Exam Outline : https://www.isc2.org/-/media/ISC2/Certifications/Exam-Outlines/CISSP-Exam-Outline.ashx
- ISC2 Endorsement : https://www.isc2.org/Membership/Endorsement
- Destination Certification : https://destcert.com/
- Cybrary CISSP : https://www.cybrary.it/course/cissp/
- Prabh Nair Coffee Shots : https://www.youtube.com/@PrabhNair
