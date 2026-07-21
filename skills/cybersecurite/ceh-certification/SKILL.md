---
name: ceh-certification
description: Guide complet de la certification CEH (Certified Ethical Hacker) v13 AI d'EC-Council — contenu, modules, préparation, ressources, coûts, et conseils d'examen.
---

# Certification CEH (Certified Ethical Hacker) — Guide Complet

> **Organisme :** EC-Council
> **Version actuelle :** CEH v13 AI (2025)
> **Niveau :** Intermédiaire / Avancé
> **Durée de validité :** 3 ans (CPE requis)

---

## 1. Présentation

La **Certified Ethical Hacker (CEH)** est la certification n°1 mondiale en ethical hacking, reconnue par le **DoD américain (ANSI 17024, DoDM 8140.03)**. La version **v13 AI** intègre désormais l'IA dans les modules et les labs pratiques.

### Chiffres clés

- **4 millions+** de professionnels certifiés dans le monde
- **400 000+** professionnels certifiés actifs
- **20 modules** d'apprentissage
- **550+** techniques d'attaque couvertes
- **221 labs** pratiques (dont labs cloud + IA)
- **4.7/5** satisfaction apprenants

---

## 2. Modules CEH v13 AI

### Module 1 : Introduction à l'Ethical Hacking
- Menaces, attaques, vecteurs
- Types de hackers (white/grey/black hat)
- Phases d'une attaque (Cyber Kill Chain, MITRE ATT&CK)
- Cadre légal et éthique
- Concept de « hacker mindset »

### Module 2 : Footprinting et Reconnaissance
- OSINT passif : WHOIS, DNS, Google Dorking, Shodan, Censys
- Reconnaissance active : Nmap, masscan
- Certificats SSL (crt.sh), Social Media, blogs
- Outils : Maltego, Recon-ng, theHarvester

### Module 3 : Scanning Networks
- Scan de ports (TCP/UDP)
- Détection d'OS et services (Nmap -sV -O)
- Évasion de firewall/IDS (fragmentation, timing, spoofing)
- Énumération de bannières

### Module 4 : Enumeration
- Enum4linux / crackmapexec (SMB, LDAP)
- SNMPwalk, DNS zone transfer
- LDAP, NFS, SMTP, RPC
- Vol de mots de passe via /etc/passwd et /etc/shadow

### Module 5 : Vulnerability Analysis
- Scanners : Nessus, OpenVAS, Qualys
- Analyse de CVSS et CVE
- Recherche d'exploits avec searchsploit
- Priorisation des vulnérabilités

### Module 6 : System Hacking
- Élévation de privilèges (Linux/Windows)
- Vol de mots de passe (Mimikatz, hash dumping)
- Keylogging, backdoors, stéganographie
- Dissimulation de traces (effacer logs, timestamps)

### Module 7 : Malware Threats
- Types de malwares : virus, worm, trojan, RAT, ransomware
- Construction de reverse shell (msfvenom)
- Packing et obfuscation (UPX, Veil, Shellter)
- Anti-Virus evasion

### Module 8 : Sniffing
- ARP spoofing, MAC flooding
- DHCP starvation
- Interception réseau : Wireshark, tcpdump, ettercap
- SSL/TLS interception et MiTM

### Module 9 : Social Engineering
- Phishing, spear-phishing, whaling
- Vishing, SMiShing, pretexting
- Outils : Gophish, SET (Social Engineering Toolkit), EvilGinx
- OSINT pré-attaque social engineering

### Module 10 : Denial of Service (DoS)
- Types DoS/DDoS : SYN flood, UDP flood, HTTP flood
- Outils : hping3, LOIC, HOIC, Slowloris
- Amplification DNS/NTP
- Contre-mesures DDoS

### Module 11 : Session Hijacking
- Vol de session via XSS, CSRF
- TCP session hijacking
- Interception de cookies
- Protection : HttpOnly, Secure, SameSite

### Module 12 : Evading IDS, Firewalls & Honeypots
- Détection de signature vs anomalie
- Techniques d'évasion (fragmentation, encodage)
- Outils : Fragmenter, ADMmutate, Nikto
- Honeypots : Dionaea, Cowrie

### Module 13 : Hacking Web Servers
- Attaques : Directory traversal, HTTP verb tampering
- Serveurs vulnérables : Apache, Nginx, IIS, Tomcat
- WebDAV exploitation
- Server-Side Request Forgery (SSRF)

### Module 14 : Hacking Web Applications
- OWASP Top 10 complet
- SQLi, XSS (reflected/stored/DOM), CSRF
- File upload bypass, command injection
- Outils : Burp Suite, OWASP ZAP, sqlmap, Nuclei

### Module 15 : SQL Injection
- In-band, blind boolean/time-based
- SQLi via out-of-band (DNS, HTTP)
- Contournement WAF
- sqlmap avancé (—os-shell, —read-file)

### Module 16 : Hacking Wireless Networks
- WPA2/WPA3, WPS, KRACK
- Evil Twin, PMKID attack
- Attaques : deauth, handshake capture, cracking (hashcat)
- Airgeddon, Aircrack-ng

### Module 17 : Hacking Mobile Platforms
- Android root, iOS jailbreak
- Décompilation APK (jadx, apktool)
- Mobile app pentesting (Frida, Objection)
- Vulnérabilités mobiles : insecure storage, root detection bypass

### Module 18 : IoT & OT Hacking
- Vulnérabilités IoT (firmware extraction, default credentials)
- Protocoles industriels : Modbus TCP, MQTT
- Shodan pour les devices IoT/OT
- Firmware analysis (binwalk, Firmwalker)

### Module 19 : Cloud Computing
- Cloud Security : AWS, Azure, GCP
- Buckets S3 publics, IAM enumeration
- Container security : Docker escape, Kubernetes RBAC
- Serverless security (Lambda, Cloud Functions)

### Module 20 : Cryptography
- Chiffrement symétrique et asymétrique
- Hachage (MD5, SHA, bcrypt, argon2)
- Attaques : padding oracle, hash length extension
- PKI, certificats, TLS/SSL
- Outils : Hashcat, John, OpenSSL, GPG

---

## 3. Labs Pratiques (221 labs)

- **Labs fondamentaux** : Nmap, Wireshark, Metasploit
- **Labs web** : SQLi, XSS, Burp Suite
- **Labs réseaux** : Sniffing, MiTM, évasion firewall
- **Labs cloud** : AWS/Azure/GCP pentesting
- **Labs IA** : Utilisation de l'IA pour la cybersécurité (nouveau v13)
- **Cyber Range** : Machines réelles dédiées (EC-Council iLabs)

---

## 4. Préparation

### Parcours recommandé

1. **Prérequis** : Connaissances de base en réseaux (TCP/IP, DNS, HTTP) et Linux
2. **Formation officielle** (5 jours) — Recommandée mais pas obligatoire
3. **Self-study** : Guide officiel EC-Council CEH v13 + labs
4. **Labs** : Compléter les 221 labs iLabs
5. **Practice tests** : EC-Council Exam Prep, Boson, ITProTV

### Ressources

| Ressource | Type | Prix |
|-----------|------|------|
| Formation officielle EC-Council | Cours (5j) | ~$1,199–2,599 |
| CEH v13 AI Official Book | Manuel | ~$80 |
| iLabs (6 mois) | Labs cloud | Inclus avec formation |
| EC-Council Exam Prep | Tests blancs | ~$99 |
| Boson CEH Practice Exams | Tests blancs | ~$99 |
| ITProTV / A Cloud Guru | Vidéos | Abonnement |
| Matt Walker — CEH Certified Guide | Livre | ~$50 |
| Jason Dion CEH (Udemy) | Cours | ~$30 |

### Conseils de préparation

- **Durée recommandée** : 2–4 mois
- **Prioriser** : SQLi, XSS, session hijacking, system hacking, malware
- **Ne pas négliger** : Cryptographie, Cloud computing (nouveaux modules)
- **Labs** : Faire tous les labs iLabs au moins une fois
- **Mémorisation** : Beaucoup de questions portent sur les outils et leurs flags exacts

---

## 5. Examen CEH (ANSI)

### Format

| Critère | Détail |
|---------|--------|
| Durée | 4 heures |
| Questions | 125 QCM, réponses multiples |
| Seuil de réussite | Variable (60–85%, typiquement ~70%) |
| Format | En ligne (surveillé) ou centre Pearson VUE |
| Langues | Anglais, français, allemand, espagnol, chinois, japonais, coréen, arabe |

### CEH Practical (examen pratique additionnel)

| Critère | Détail |
|---------|--------|
| Durée | 6 heures |
| Format | 20 challenges pratiques (machines réelles) |
| Contenu | Nmap, Metasploit, sqlmap, Wireshark, hydra, etc. |
| Seuil | 70% (14/20) |

**Recommandation :** Passer le CEH ANSI + Practical pour la certification complète.

---

## 6. Coûts Totaux

| Élément | Prix (USD) |
|---------|-----------|
| Exam ANSI | ~$1,199 |
| Exam Practical | ~$500 |
| Formation (optionnelle) | $850–2,599 |
| Labs iLabs (si solo) | ~$400 |
| Total estimé (solo) | ~$1,600–2,600 |
| Total estimé (formé) | ~$2,500–4,200 |

---

## 7. Maintien de la certification

- **Valide** : 3 ans
- **CPE requis** : 120 CPE (40 CPE/an)
- **EC-Council Continuing Education (ECE)**

Sources de CPE :
- Conférences (DEF CON, BlackHat)
- Webinaires EC-Council
- Publications d'articles
- Mentorat / enseignement
- Autres certifications

---

## 8. Avantages et Inconvénients

### ✅ Avantages
- Certification la plus reconnue pour l'ethical hacking
- Large couverture (20 modules, 550+ techniques)
- Format ANSI accrédité par le DoD
- Labs pratiques en nombre
- Nouvelle version IA (v13) très actuelle

### ❌ Inconvénients
- Coût élevé
- Beaucoup de mémorisation (flags d'outils, commandes exactes)
- Parfois critiquée pour être « trop théorique » (par rapport à OSCP)
- Moins technique que l'OSCP en pratique
- Nécessite renouvellement CPE

---

## 9. Liens Utiles

- Site officiel : https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/
- Syllabus CEH v13 : https://www.eccouncil.org/cybersecurity-exchange/ethical-hacking/ceh-syllabus/
- EC-Council Store : https://cert.eccouncil.org/
- CEH Practical : https://www.eccouncil.org/programs/ceh-practical/
- EC-Council Exam Prep : https://www.eccouncil.org/exam-preparation/
