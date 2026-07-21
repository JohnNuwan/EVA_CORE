---
name: linux-certification
description: Guide complet des certifications Linux — LPIC (Linux Professional Institute), RHCSA/RHCE (Red Hat), CompTIA Linux+, et parcours de certification Linux pour la cybersécurité.
---

# Certifications Linux — Guide Complet

> **Linux est le socle de la cybersécurité.** Tout pentester, analyste SOC, ou ingénieur sécurité doit maîtriser Linux. Les certifications Linux valident cette maîtrise de manière structurée.

---

## 1. Vue d'ensemble des certifications Linux

| Certification | Organisme | Niveau | Prix | Pratique | Reconnaissance |
|--------------|-----------|--------|------|----------|---------------|
| LPIC-1 | LPI | Débutant | $200 | Mixte | Internationale |
| LPIC-2 | LPI | Intermédiaire | $200 | Mixte | Internationale |
| LPIC-3 | LPI | Expert | $200 | Mixte | Internationale |
| RHCSA | Red Hat | Intermédiaire | $400 | 100% pratique | **Très élevée** |
| RHCE | Red Hat | Avancé | $400 | 100% pratique | **Très élevée** |
| CompTIA Linux+ | CompTIA | Débutant | $358 | Mixte | Large |
| LFCS | Linux Foundation | Intermédiaire | $200 | 100% pratique | Open source |
| LFCE | Linux Foundation | Avancé | $200 | 100% pratique | Open source |

---

## 2. CompTIA Linux+ (XK0-005)

> **Prérequis :** Aucun (recommandé : 9-12 mois d'expérience Linux)
> **Coût :** $358 USD
> **Durée :** 90 minutes
> **Questions :** 90
> **Seuil :** 720/900
> **Valide :** 3 ans

### Domaines

| Domaine | Poids |
|---------|-------|
| Hardware and System Configuration | 18% |
| Systems Operation and Maintenance | 20% |
| Security | 24% |
| Linux Troubleshooting and Diagnostics | 20% |
| Automation and Scripting | 18% |

### Contenu sécurité (24% — le plus gros domaine)

- Gestion des utilisateurs (useradd, usermod, groupadd, sudo)
- Permissions UNIX (chmod, chown, ACL, setuid, setgid, sticky bit)
- AppArmor, SELinux (modes, contextes, audit)
- Firewall (iptables, nftables, ufw, firewalld)
- SSH (key-based auth, config, hardening)
- Pluggable Authentication Modules (PAM)
- GPG, OpenSSL, gestion de certificats
- Audit (auditd, /var/log/)
- Gestion des logs (rsyslog, journalctl)
- Durcissement (CIS Benchmarks, STIGs)

### Préparation

| Ressource | Prix |
|-----------|------|
| CompTIA Linux+ Study Guide (Chapple) | ~$50 |
| Pearson IT Certification Practice Tests | ~$40 |
| CBT Nuggets Linux+ | $60/mois |
| ITProTV Linux+ | Abonnement |
| Jason Dion Linux+ (Udemy) | ~$30 |

---

## 3. LPIC-1 (Linux Administrator — 101-500 + 102-500)

> **Organisme :** Linux Professional Institute (LPI)
> **Prérequis :** Aucun
> **Coût :** $200 par examen (2 examens = $400)
> **Durée :** 90 minutes par examen
> **Questions :** 60 par examen
> **Seuil :** 500/800
> **Valide :** Sans expiration (LPI ne nécessite pas de renouvellement)

### Examen 101-500

| Topic | Poids |
|-------|-------|
| System Architecture | 14% |
| Linux Installation & Package Management | 18% |
| GNU & Unix Commands | 43% |
| Devices, Linux Filesystems, Filesystem Hierarchy | 25% |

### Examen 102-500

| Topic | Poids |
|-------|-------|
| Shell, Scripting & Data Management | 22% |
| User Interfaces & Desktops | 8% |
| Administrative Tasks | 20% |
| Essential System Services | 22% |
| Networking Fundamentals | 18% |
| Security | 10% |

### Contenu sécurité (LPIC-1)

- sudo, su, root privileges
- PAM configuration
- Gestion des utilisateurs/groupes
- Permissions de base et avancées (ACL, sticky bit)
- iptables/nftables basics
- SSH server configuration
- GPG basics
- Log management (syslog, logrotate)

### Préparation

| Ressource | Prix |
|-----------|------|
| LPI Learning Materials (official) | Gratuit |
| LPIC-1 Study Guide (Roderick W. Smith) | ~$50 |
| Linux Academy LPIC-1 | Abonnement |
| CBT Nuggets LPIC-1 | $60/mois |
| O'Reilly LPIC-1 Learning Path | ~$40/mois |

---

## 4. LPIC-2 (Linux Engineer — 201-450 + 202-450)

> **Prérequis :** LPIC-1
> **Coût :** $200 par examen (2 examens = $400)
> **Durée :** 90 minutes par examen
> **Questions :** 60 par examen
> **Seuil :** 500/800

### Examen 201-450

| Topic | Poids |
|-------|-------|
| Capacity Planning | 6% |
| Linux Kernel | 10% |
| System Startup | 8% |
| Filesystem & Devices | 12% |
| Advanced Storage (LVM, RAID, iSCSI) | 13% |
| Network Configuration | 14% |
| System Maintenance | 11% |
| DNS & Web Services | 18% |
| File Sharing (NFS, Samba) | 8% |

### Examen 202-450

| Topic | Poids |
|-------|-------|
| Network Client Management (DHCP, PAM, LDAP) | 18% |
| System Security (firewall, encryption, PKI) | 20% |
| Mail Services (Postfix, Dovecot) | 10% |
| System Monitoring (Prometheus, Grafana, Nagios) | 12% |
| Troubleshooting | 20% |
| Automation (Ansible, bash) | 20% |

### Contenu sécurité (LPIC-2 — 20%)

- iptables/nftables avancé (nat, mangle, raw, conntrack)
- OpenVPN, IPsec, WireGuard
- OpenSSL, CA, certificats, TLS
- SELinux, AppArmor avancé
- Auditd, aide, chkrootkit, rkhunter
- Kerberos, LDAP security
- Gestion des incidents (log analysis, forensics basics)

---

## 5. LPIC-3 (Mixed Environments / Security / High Availability)

> **Prérequis :** LPIC-2
> **Coût :** $200 par examen
> **Durée :** 90 minutes
> **Seuil :** 500/800

### 3 spécialisations

1. **LPIC-3 300 — Mixed Environments** (Samba, LDAP, Kerberos, AD integration)
2. **LPIC-3 303 — Security** (2018+)
   - Cryptographie avancée (LUKS, dm-crypt, GPG, PKI)
   - Host hardening, kernel hardening
   - SELinux, AppArmor avancé
   - Firewall avancé (nftables, conntrack)
   - IDS/IPS (Snort, Suricata, AIDE)
   - OpenVPN, IPsec, WireGuard
   - Vulnerability scanning & remediation
3. **LPIC-3 304 — High Availability & Virtualization**
   - Pacemaker, DRBD, Keepalived
   - KVM, Xen, LXC, Docker

---

## 6. RHCSA (Red Hat Certified System Administrator — EX200)

> **La certification pratique la plus reconnue pour Linux**
> **Organisme :** Red Hat
> **Prérequis :** Aucun (recommandé : expérience Linux)
> **Coût :** $400 USD
> **Durée :** 2h30
> **Format :** **100% pratique** (pas de QCM)
> **Seuil :** 210/300
> **Valide :** 3 ans

### Contenu

- **Gestion des utilisateurs et groupes** : useradd, usermod, groupadd, sudoers
- **Permissions** : chmod, chown, ACL, setfacl, getfacl
- **Stockage** : LVM, ext4, xfs, resizing, RAID
- **Boot** : GRUB, systemd, kernel parameters
- **Réseau** : nmcli, nmtui, NetworkManager, hostname, DNS
- **SELinux** : contextes, modes, booleans, audit
- **Firewall** : firewalld, zones, services
- **Containers** : Podman, Skopeo, multi-container (pod)
- **Services** : Apache, NFS, Samba, MariaDB, chrony
- **Automation** : Bash scripting, systemd units
- **Scheduling** : cron, at, systemd timers
- **Logging** : rsyslog, journalctl, logrotate

### Contenu sécurité (RHCSA)

- SELinux (chcon, semanage, restorecon, audit2allow)
- Firewalld (zones, rules, masquerade)
- SSH hardening (key-based auth, PermitRootLogin no)
- sudoers configuration
- Container security (read-only, user namespace, audit)
- Password policies (chage, /etc/login.defs, /etc/pam.d/)

### Préparation

| Ressource | Prix |
|-----------|------|
| RHCSA Official Course (RH124) | ~$3,600 |
| Sander van Vugt — RHCSA (Pearson) | ~$50 |
| Sander van Vugt — RHCSA (Udemy) | ~$30 |
| Linux Academy RHCSA | Abonnement |
| Killercoda RHCSA Labs | Gratuit |
| AWS CloudFormation + RHEL | Gratuit (AWS) |

---

## 7. RHCE (Red Hat Certified Engineer — EX294)

> **Prérequis :** RHCSA
> **Coût :** $400 USD
> **Durée :** 3h30
> **Format :** **100% pratique**
> **Seuil :** 210/300
> **Valide :** 3 ans

### Contenu

- **Ansible automation** (inventories, playbooks, roles, modules)
- **Ansible Tower / AWX**
- **Gestion de configuration** : packages, services, files, firewall
- **SELinux** : policy management, booleans, file contexts
- **LVM avancé** : thin provisioning, snapshots, resizing
- **Haute disponibilité** : Pacemaker, Corosync
- **Advanced networking** : network bonding, teaming, bridges
- **Containers** : multi-container Podman, systemd integration

---

## 8. Linux Foundation Certified System Administrator (LFCS)

> **Organisme :** Linux Foundation
> **Prérequis :** Aucun
> **Coût :** $200 USD
> **Durée :** 2h
> **Format :** **100% pratique** (laboratoire virtuel)
> **Valide :** 2 ans

### Contenu

- Commandes essentielles Linux
- Operations sur les fichiers et stockage
- Gestion des services (systemd)
- Réseaux et firewall
- Gestion des paquets (apt, yum, dnf)
- Sécurité (users, permissions, SELinux basics)
- Conteneurs (Docker, conteneurisation)

### Avantages

- **Prix très abordable** ($200 pour pratique)
- **Basé sur Ubuntu/Debian** (alternative à RHCSA/RHEL)
- **Reconnaissance large** (Linux Foundation)
- **Renouvellement** : repasser l'examen (pas de CPE)

---

## 9. Comparatif détaillé

| Critère | RHCSA | LPIC-1 | LFCS | CompTIA Linux+ |
|---------|-------|--------|------|----------------|
| Prix | $400 | $400 (2x) | $200 | $358 |
| Format | 100% pratique | QCM | 100% pratique | QCM + PBQ |
| OS | RHEL | Ubuntu/Debian/RHEL | Ubuntu/RHEL | Linux générique |
| Durée | 2h30 | 90 min/exam | 2h | 90 min |
| Difficile | Oui | Moyen | Oui | Moyen |
| Reconnaissance | Très haute | Internationale | Haute | Large |
| Idéal pour | Admin RHEL | Linux général | Flexible | Débutants |

---

## 10. Parcours recommandé pour la cybersécurité

### Parcours sécurité Linux

```
Niveau 1 : Fondamentaux (2-3 mois)
├── CompTIA Linux+ OU LPIC-1
├── Commandes de base, permissions, users, shell
├── bash scripting, awk, sed, grep
└── SSH, sudo, firewall

Niveau 2 : Administration (3-4 mois)
├── RHCSA OU LPIC-2
├── Systemd, LVM, RAID, SELinux
├── Réseaux, DNS, services
└── Containerisation (Podman/Docker)

Niveau 3 : Expert (3-6 mois)
├── RHCE (Ansible) OU LPIC-3 Security
├── Automation, configuration management
├── Hardening, PKI, cryptographie
└── IDS/IPS, audit, forensics
```

### Importance des certifications Linux pour la cybersécurité

| Rôle | Certification recommandée |
|------|-------------------------|
| Pentester | RHCSA, LPIC-1 |
| SOC Analyst | LPIC-1, CompTIA Linux+ |
| DevOps Sec | RHCE, LPIC-2 |
| Security Engineer | RHCSA, LPIC-2 |
| Forensics Analyst | LPIC-1, LFCS |
| Security Architect | RHCE, LPIC-3 Security |

---

## 11. Ressources Linux gratuites

- **Linux Journey** : https://linuxjourney.com
- **Ryan's Tutorials** : https://ryanstutorials.net
- **Efficient Linux at the Command Line** (livre gratuit)
- **The Linux Documentation Project** : https://tldp.org
- **OverTheWire Bandit** : https://overthewire.org/wargames/bandit/
- **Linux Survival** : https://linuxsurvival.com
- **Killercoda** : https://killercoda.com (Labs interactifs)
- **Katacoda** : https://www.katacoda.com (Labs gratuits)

---

## 12. Maintien des certifications

| Certification | Validité | Renouvellement |
|--------------|----------|---------------|
| LPIC-1/2/3 | À vie | Aucun (pas de CPE) |
| RHCSA/RHCE | 3 ans | Repasser l'examen mis à jour |
| CompTIA Linux+ | 3 ans | CPE (50 CEU/3 ans) ou repasser |
| LFCS | 2 ans | Repasser l'examen |

---

## 13. Liens Utiles

- LPI (LPIC) : https://www.lpi.org
- Red Hat Training : https://www.redhat.com/en/services/training-and-certification
- CompTIA Linux+ : https://www.comptia.org/certifications/linux
- Linux Foundation LFCS : https://training.linuxfoundation.org/certification/lfcs/
- RHCSA Exam Objectives : https://www.redhat.com/en/services/training/ex200-red-hat-certified-system-administrator-rhcsa-exam
- LPIC-1 Exam Objectives : https://www.lpi.org/our-certifications/lpic-1-overview