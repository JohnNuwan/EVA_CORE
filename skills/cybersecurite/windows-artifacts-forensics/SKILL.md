---
name: windows-artifacts-forensics
description: Guide complet des artefacts forensiques Windows — Prefetch, AmCache, ShimCache, Jump Lists, Registry Hives, MFT, Event Logs, SRUM, BAM/DAM, LNK files, USN Journal, Timeline Browser, et EZ Tools
tags: [forensics, windows, artifacts, registry, prefetch, amcache, shimcache, jumplist, srum, lnk]
version: 1.0
---

# Artefacts Forensiques Windows — Guide Complet

Guide exhaustif des artefacts laissés par le système d'exploitation Windows lors de l'exécution de programmes, l'ouverture de fichiers, la connexion réseau, etc.

---

## 1. Prefetch

### Emplacement

```txt
C:\Windows\Prefetch\
Format : .pf (nommé : <PROGRAMME>-<HASH>.pf)
Exemple : NOTEPAD.EXE-ABC12345.pf
Conservé : 128 fichiers (Windows 10) / 1024 (Windows 10 1809+)
```

### Analyse

```txt
Contenu du Prefetch :
- Nom du .exe
- Chemin complet du programme
- Compteur d'exécution
- Dernière exécution
- Première exécution (Windows 10)
- Liste des DLLs chargées
- Liste des fichiers lus (I/O traces)
- Fragments de chemin (30 max)

Utilité forensique :
- QUEL programme a été exécuté
- COMBIEN de fois
- QUAND (dernière + première exécution)
- DEPUIS OÙ (chemin original)
- QUELLES DLL/fichiers touchés
```

### Extraction

```bash
# Avec PECmd (EZ Tools)
PECmd.exe -d "C:\Windows\Prefetch" --csv prefetch_output.csv

# Analyse d'un fichier spécifique
PECmd.exe -f "C:\Windows\Prefetch\CMD.EXE-12345.pf" --csv details.csv

# Options
PECmd.exe -d "C:\Windows\Prefetch" --csv output.csv \
   --json json_output.json \
   --html html_report

# Depuis une image forensique
PECmd.exe -f "E:\Windows\Prefetch\*.pf" --csv /evidence/prefetch.csv

# Depuis la mémoire (Volatility)
vol -f memory.raw windows.registry.printkey --key "ControlSet001\Control\Session Manager\Prefetch"
```

### Interprétation

```txt
Prefetch TIMESTAMPS :
┌────────────────────────────────────────────────────────────┐
│ Créé (fichier .pf) = PREMIÈRE EXÉCUTION                     │
│ Modifié = DERNIÈRE EXÉCUTION                                │
│ Accédé = peut-être pas mis à jour                          │
└────────────────────────────────────────────────────────────┘

Compteur (run count) :
1 exécution → lancement unique, possiblement malware
100+ exécutions → programme légitime, usage quotidien

Fichiers dans le Prefetch :
- Fichiers système dans un Prefetch de processus système = normal
- DLL non MS dans un Prefetch de processus critique = indicateur de DLL hijacking
- Chemins : Temp, Downloads, AppData → programmes potentiellement malveillants

PROGRAMMES SUSPECTS DANS PREFETCH :
- rundll32.exe (légitime mais souvent abusé)
- regsvr32.exe (abuse par malware)
- mshta.exe (HTA malveillant)
- cscript.exe, wscript.exe (scripts)
- powershell.exe (scripts)
- cmd.exe (commandes)
- wmic.exe (WMIC abuse)
```

---

## 2. AmCache

### Emplacement

```txt
C:\Windows\appcompat\Programs\Amcache.hve
Format : Ruche de registre (Registry hive)
Conserve : Applications installées, avec version, chemin, dates
```

### Analyse

```txt
Contenu de l'AmCache :
- Nom du programme
- Version
- Chemin d'installation
- Chemin de l'exécutable principal
- Date d'installation
- Date de dernière exécution
- SHA1 du fichier (Windows 10+)
- Taille du fichier
- Product name, publisher
- MSI / non-MSI

Utilité forensique :
- QUELS programmes sont installés (même désinstallés !)
- QUAND ils ont été installés
- VERSION exacte
- SHA1 → lookup VirusTotal
- Applications portables (pas dans Uninstall)
```

### Extraction

```bash
# Avec AmcacheParser (EZ Tools)
AmcacheParser.exe -f "C:\Windows\appcompat\Programs\Amcache.hve" \
   --csv /evidence/amcache.csv \
   --json /evidence/amcache.json

# Depuis la mémoire
vol -f memory.raw windows.registry.amcache

# Depuis une image (offline)
# Monter l'image → extraire Amcache.hve → parser
AmcacheParser.exe -f "E:\Windows\appcompat\Programs\Amcache.hve" --csv output/
```

### Interprétation

```txt
DÉTECTION DE MALWARE :
- Application installée dont le publisher est inconnu
- SHA1 inconnu (VS VirusTotal)
- Chemin dans Temp, AppData, Downloads
- Programme sans version / product name
- Installation hors heures de travail (ex: 3h du matin)

APPLICATIONS PORTABLES :
- N'apparaissent PAS dans Uninstall
- MAIS apparaissent souvent dans AmCache
- Si SHA1 présent → identification possible
```

---

## 3. ShimCache (AppCompatCache)

### Emplacement

```txt
Registry : SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache
Format : Binaire dans la ruche SYSTEM
Conserve : Dernière exécution de chaque .exe (même fichiers supprimés)
```

### Analyse

```txt
Contenu (limité à 1024 entrées) :
- Chemin complet du fichier (s'il est encore présent)
- Taille du fichier
- Date de modification (dernière modif, PAS exécution)
- Flags (est-ce présent ?)

LIMITATIONS :
- Date de modification, PAS date d'exécution
- Limité à 1024 entrées
- Seulement les .exe
- La date est celle du fichier, pas de l'exécution
```

### Extraction

```bash
# Windows natif (aucun outil)
# Pas d'accès direct sans EZ Tools ou Volatility

# AppCompatCacheParser (EZ Tools)
AppCompatCacheParser.exe -f "SYSTEM" --csv shimcache_output.csv
# Ex: le fichier SYSTEM extrait depuis une image

# Depuis la mémoire (Volatility)
vol -f memory.raw windows.shimcache

# Depuis une image
# 1. Monter l'image
# 2. Extraire SYSTEM du registre
# 3. Parser
reg export "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\AppCompatCache" shimcache.txt
```

### Interprétation

```txt
USAGE FORENSIQUE :
- Voir quels .exe ont existé sur le système (même supprimés)
- Corroborer les informations Prefetch
- Si un fichier est dans ShimCache mais pas Prefetch :
    → exécuté depuis un support externe ?
    → ou Prefetch effacé ?

INDICATEURS :
- .exe avec dates de modification suspects
- Chemins depuis Temp, AppData
- Programmes qui ne sont plus présents (supprimés après exécution)
- Plusieurs entrées du même fichier (tailles différentes = versions)
```

---

## 4. Jump Lists

### Emplacement

```txt
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\CustomDestinations\

Format : OLE2 (fichiers .automaticDestinations-ms / .customDestinations-ms)
Contenu : Liste des fichiers récents par application
```

### Analyse

```txt
AutomaticDestinations (créés automatiquement) :
- Fichiers récents de chaque application
- Application identifié par AppID (GUID)
- Format OLE2 → contient des LNK files
- Timestamps : créé, modifié, accédé

CustomDestinations (créés par l'utilisateur) :
- Épinglage à la taskbar
- Historique manuel

AppIDs connus :
{90dd34b0-3e4e-4f5e-9a7c-8f7b7b7b7b7b}  → Notepad
{00021401-0000-0000-c000-000000000046}    → Explorer
{1b5b0c15-1f6c-4f2b-8d4a-5a8d2b8a0b6d}  → Chrome
{ec9b7f8c-1e8e-4b0a-8d4e-5b5f2b9a0c6d}  → Firefox
{b1b1b1b1-1e1e-4b0a-8d4e-5b5f2b9a0c6d}  → Adobe Reader
```

### Extraction

```bash
# Avec JLECmd (EZ Tools)
JLECmd.exe -d "C:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent" \
   --csv /evidence/jumplists.csv

# Analyse d'un fichier spécifique
JLECmd.exe -f "C:\Users\suspect\AppData\Roaming\...\.automaticDestinations-ms" \
   --csv /evidence/jumplist_detail.csv

# Depuis une image
JLECmd.exe -d "E:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent" --csv /

# Explorer les LNK contenus
# Les Jump Lists contiennent des fichiers .lnk → analyser avec LECmd
```

---

## 5. LNK Files (Raccourcis)

### Emplacement

```txt
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Recent\
C:\Users\<user>\Desktop\
C:\Users\<user>\AppData\Roaming\Microsoft\Internet Explorer\Quick Launch\
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\Start Menu\

Aussi :
- Dans les Jump Lists
- Dans les MRU du registre
```

### Analyse

```txt
Contenu d'un fichier .lnk :
- Chemin complet du fichier cible
- Arguments de ligne de commande
- Répertoire de travail
- Timestamps (créé, modifié, accédé, cible)
- Volume (serial number)
- Taille du fichier
- NetBIOS name (machine source)
- MAC address (network share !)
- Fenêtre (normale/minimisée/maximisée)
- Hotkey
- Icon index
```

### Extraction

```bash
# Avec LECmd (EZ Tools)
LECmd.exe -f "C:\Users\suspect\Recent\document.lnk" --csv /evidence/lnk_output.csv

# Extraction récursive
LECmd.exe -d "C:\Users\suspect\Recent" --csv /evidence/lnk_batch.csv

# Depuis une image
LECmd.exe -d "E:\Users\suspect\AppData\Roaming\Microsoft\Windows\Recent" --csv /

# Analyse réseau — trouve les MAC address des machines visitées
LECmd.exe -f shortcut.lnk --csv out.csv | grep "Mac\|MAC\|mac"
```

### Interprétation

```txt
MAC ADDRESS DANS LNK :
Quand un fichier est ouvert depuis un partage réseau,
le LNK contient l'adresse MAC de la machine source !
→ Permet de relier deux machines sur un réseau

TIMESTAMPS :
- Création du LNK = première ouverture du fichier
- Modification du LNK = ouverture récente
- Timestamps de la cible = dernière modification du fichier

ARGUMENTS :
- Présence d'arguments de command line dans un LNK
  → ex: "malware.exe -silent -install" (indicateur)
```

---

## 6. Registry Hives — Analyse Approfondie

### Emplacements

```txt
Hives système :
C:\Windows\System32\config\
├── SAM          → Comptes utilisateurs, hash NTLM
├── SECURITY     → Politiques, Logon sessions
├── SOFTWARE     → Programmes, configuration système
├── SYSTEM       → Drivers, services, configuration générale
└── DEFAULT      → Profil par défaut

Hives utilisateur (NTUSER.DAT) :
C:\Users\<user>\NTUSER.DAT
C:\Users\<user>\AppData\Local\Microsoft\Windows\UsrClass.dat
```

### Clés Forensiques Essentielles

```txt
SYSTEM :
  └─ ControlSet001\Control\ComputerName\ComputerName    → Nom de la machine
  └─ ControlSet001\Control\TimeZoneInformation           → Timezone
  └─ ControlSet001\Enum\USBSTOR                         → Clés USB connectées
  └─ ControlSet001\Enum\USB                              → Périphériques USB (VID/PID)
  └─ ControlSet001\Services                              → Services installés
  └─ ControlSet001\Control\Session Manager\BootExecute   → Autoruns avant logon
  └─ Select\Current                                       → Dernier ControlSet utilisé

SOFTWARE :
  └─ Microsoft\Windows\CurrentVersion\Run               → Programmes au démarrage
  └─ Microsoft\Windows\CurrentVersion\RunOnce           → Exécution unique
  └─ Microsoft\Windows NT\CurrentVersion\NetworkList     → Réseaux WiFi connus
  └─ Microsoft\Windows NT\CurrentVersion\Prefetcher      → État Prefetch
  └─ Microsoft\Windows\CurrentVersion\Uninstall          → Liste des programmes installés

SAM :
  └─ SAM\Domains\Account\Users\Names                     → Liste des utilisateurs
  └─ SAM\Domains\Account\Users\000003E9\F                → Hash NTLM admin

NTUSER.DAT (Utilisateur) :
  └─ Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs  → Documents récents
  └─ Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU      → Menu Exécuter
  └─ Software\Microsoft\Windows\CurrentVersion\Explorer\ComDlg32    → Dialogs d'ouverture
  └─ Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist  → GUI programs count
  └─ Software\Microsoft\Windows\Shell\BagMRU                        → ShellBags (dossiers)
  └─ Software\Microsoft\Internet Explorer\TypedURLs                 → URLs tapées IE
  └─ Software\Microsoft\Windows\CurrentVersion\Applets\Regedit      → Regedit history
  └─ Software\Microsoft\Office\*\User MRU                          → Office files
  └─ Network\x (partages réseau)                                    → Lettres de lecteurs

UsrClass.dat :
  └─ Local Settings\Software\Microsoft\Windows\CurrentVersion\AppContainer\...
  └─ ShellBags (pour les dossiers de la bibliothèque)
```

### Extraction Registre depuis Image

```bash
# Depuis une image forensique montée
# Utiliser regripper ou Registry Explorer (EZ Tools)

# Avec Python (python-registry)
pip install python-registry

python3 << 'EOF'
from Registry import Registry
reg = Registry.Registry('/evidence/Windows/System32/config/SOFTWARE')
key = reg.open('Microsoft/Windows/CurrentVersion/Run')
for v in key.values():
    print(f"{v.name()} = {v.value()}")
EOF

# Avec RegRipper (CLI)
rip.exe -r "E:\Windows\System32\config\SYSTEM" -f all > system_all.txt

# Avec Registry Explorer (EZ Tools)
RegistryExplorer.exe -f "E:\Windows\System32\config\SOFTWARE" --csv output.csv
```

### USB History (USBSTOR)

```bash
# Extraction des périphériques USB connectés
# Clé : SYSTEM\CurrentControlSet\Enum\USBSTOR

# Avec Registry Explorer
RegistryExplorer.exe -f "E:\Windows\System32\config\SYSTEM" \
   -k "ControlSet001\Enum\USBSTOR" --csv usb.csv

# Interprétation :
# Venus & Venus&Prod_1234&Rev_0100
# ├── SerialNumber_XYZ123
# │   ├── FriendlyName : "Kingston DataTraveler 2.0 USB Device"
# │   ├── ParentIdPrefix : 7&1a2b3c4d&0
# │   └── Properties\{83da6326-97a6-4088-9453-a1923f573b29}\0064
# │       → FirstInstall Date

# Informations récupérées :
# - Manufacturer (Kingston, SanDisk, etc.)
# - Product (DataTraveler, Cruzer, etc.)
# - Serial number (unique)
# - Date de première connexion
# - Dernière connexion (via SetupAPI.dev.log)
# - Drive letter (via MountedDevices)

# MountedDevices (partitions assignées)
SYSTEM\MountedDevices
# \??\Volume{guid} → \DosDevices\C:
```

---

## 7. SRUM (System Resource Usage Monitor)

### Emplacement

```txt
C:\Windows\System32\sru\SRUDB.dat
Format : ESE (Extensible Storage Engine) Database
Contenu : Données d'utilisation des ressources pour chaque application
```

### Analyse

```txt
Données collectées toutes les heures :
- CPU Time par application (temps processeur)
- Réseau (bytes envoyés/reçus par application)
- Utilisation de la mémoire
- Données en lecture/écriture disque
- Durée de fonctionnement
- Push notifications (Windows Store apps)

Utilité forensique :
- APPERCEVOIR les applications qui ont utilisé le réseau
  (même si le pare-feu est désactivé)
- IDENTIFIER les logiciels malveillants par leur consommation
- DÉTECTER une exfiltration (volume de réseau sortant)
- CORRÉLER avec les heures d'activité
```

### Extraction

```bash
# Avec SrumECmd (EZ Tools)
SrumECmd.exe -f "C:\Windows\System32\sru\SRUDB.dat" \
   --csv /evidence/srum_output.csv

# Depuis une image
SrumECmd.exe -f "E:\Windows\System32\sru\SRUDB.dat" --csv /evidence/

# Analyse réseau par application
# Dans le CSV :
# AppId, Timestamp, BytesSent, BytesRecvd
# Ex: malware.exe → 10MB sortant → exfiltration

# Analyse CPU
# AppId, Timestamp, CPUTime (ms)
# Ex: miner.exe → CPU: 86400000ms (24h) → minage
```

---

## 8. BAM / DAM (Background Activity Moderator)

### Emplacement

```txt
Registry :
SYSTEM\CurrentControlSet\Services\bam\UserSettings\{SID}
SYSTEM\CurrentControlSet\Services\dam\UserSettings\{SID}

Windows 10 1703+
Conserve : Date/heure de début d'exécution des programmes
```

### Analyse

```txt
BAM (Foreground) :
- Applications lancées en premier plan
- Timestamp de début d'exécution
- Très précis (secondes)

DAM (Background) :
- Applications en arrière-plan
- Plus large, moins précis

Utilité :
- Alternative à Prefetch (Windows 10+)
- Timestamp DE DÉBUT d'exécution
- Contient aussi des applications non-Prefetch (scripts, exécutables sans .exe)
```

### Extraction

```bash
# Avec Registry Explorer
RegistryExplorer.exe -f "E:\Windows\System32\config\SYSTEM" \
   -k "ControlSet001\Services\bam\UserSettings" --csv bam_output.csv

# Ou directement en mémoire
vol -f memory.raw windows.registry.printkey \
   --key "ControlSet001\Services\bam\UserSettings"
```

---

## 9. Timeline Browser (Chrome/Firefox/Edge)

### Chrome

```bash
# Emplacements (Windows) :
C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\

# History (SQLite)
sqlite3 History "
SELECT url, title, visit_count,
       datetime(last_visit_time/1000000-11644473600, 'unixepoch') as last_visit
FROM urls ORDER BY last_visit_time DESC LIMIT 50;
"

# Downloads
sqlite3 History "
SELECT tab_url, target_path, state,
       datetime(start_time/1000000-11644473600, 'unixepoch') as start,
       datetime(end_time/1000000-11644473600, 'unixepoch') as end
FROM downloads;
"

# Cookies
sqlite3 Cookies "
SELECT host_key, name, path, encrypted_value,
       datetime(expires_utc/1000000-11644473600, 'unixepoch') as expires
FROM cookies;
"

# Login Data (mots de passe — AES encrypté)
sqlite3 "Login Data" "
SELECT origin_url, username_value
FROM logins;
"

# Bookmarks
sqlite3 Bookmarks "
SELECT DISTINCT url, title, date_added
FROM bookmarks;
"
```

### Firefox

```bash
# Emplacements :
C:\Users\<user>\AppData\Roaming\Mozilla\Firefox\Profiles\*.default-release\

# places.sqlite (history + bookmarks)
sqlite3 places.sqlite "
SELECT url, title,
       datetime(visit_date/1000000, 'unixepoch') as visit_time
FROM moz_places
JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
ORDER BY visit_date DESC LIMIT 50;
"

# favicons.sqlite (sites visités)
sqlite3 favicons.sqlite "
SELECT url, datetime(expire_time/1000000, 'unixepoch')
FROM favicons;
"
```

---

## 10. EZ Tools — Guide de Référence

### Installation

```bash
# Télécharger depuis ericzimmerman.github.io
# Tous les outils en un clic : Get-ZimmermanTools.ps1

# Installation via PowerShell
Set-ExecutionPolicy Bypass -Scope Process
iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/EricZimmerman/Get-ZimmermanTools/master/Get-ZimmermanTools.ps1'))
Get-ZimmermanTools -Destination C:\Tools\EZTools
```

### Tableau des Outils

```txt
┌──────────────────────┬──────────────────────────────────────────────────────┐
│ OUTIL                │ ANALYSE                                               │
├──────────────────────┼──────────────────────────────────────────────────────┤
│ PECmd                │ Prefetch (.pf parser)                                 │
│ AmcacheParser        │ AmCache.hve parser                                   │
│ AppCompatCacheParser │ ShimCache parser (AppCompatCache)                     │
│ JLECmd               │ Jump Lists parser (.automaticDestinations-ms)         │
│ LECmd                │ LNK (shortcut) files parser                          │
│ MFTECmd              │ $MFT parser + USN Journal                            │
│ RegistryExplorer     │ Registry hive viewer + export                         │
│ SrumECmd             │ SRUDB.dat parser (SRUM)                              │
│ RECmd                │ Registry batch commands (RegRipper-like)             │
│ PECmd                │ Prefetch parser                                      │
│ SBECmd               │ ShellBags parser                                     │
│ WxTCmd               │ Windows Timeline (ActivitiesCache.db)                │
│ EvtxECmd             │ Windows Event Log parser (.evtx → CSV)               │
│ TimelineExplorer     │ CSV timeline viewer                                  │
│ Hasher               │ File hasher (MD5, SHA1, SHA256)                      │
│ bstrings             │ Strings extractor (encodings support)                │
└──────────────────────┴──────────────────────────────────────────────────────┘
```

### Workflow Complet EZ Tools

```bash
@echo off
REM ez_forensics.cmd — Analyse complète des artefacts Windows

set CASEDIR=C:\evidence\%COMPUTERNAME%_%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%
mkdir %CASEDIR%

echo === WINDOWS ARTIFACTS COLLECTION ===
echo Output: %CASEDIR%

:: 1. Prefetch
echo [1] Prefetch...
PECmd.exe -d "C:\Windows\Prefetch" --csv "%CASEDIR%\prefetch"

:: 2. AmCache
echo [2] AmCache...
AmcacheParser.exe -f "C:\Windows\appcompat\Programs\Amcache.hve" --csv "%CASEDIR%\amcache"

:: 3. ShimCache (extraire SYSTEM d'abord)
echo [3] ShimCache...
reg export "HKLM\SYSTEM" "%CASEDIR%\SYSTEM.reg" /y
AppCompatCacheParser.exe -f "%CASEDIR%\SYSTEM.reg" --csv "%CASEDIR%\shimcache"

:: 4. Jump Lists
echo [4] Jump Lists...
JLECmd.exe -d "C:\Users" --csv "%CASEDIR%\jumplists"

:: 5. LNK files
echo [5] LNK files...
LECmd.exe -d "C:\Users" --csv "%CASEDIR%\lnk"

:: 6. MFT
echo [6] MFT...
MFTECmd.exe -f "C:\$MFT" --csv "%CASEDIR%\mft"

:: 7. SRUM
echo [7] SRUM...
SrumECmd.exe -f "C:\Windows\System32\sru\SRUDB.dat" --csv "%CASEDIR%\srum"

:: 8. Event Logs
echo [8] Event Logs...
EvtxECmd.exe -d "C:\Windows\System32\winevt\Logs" --csv "%CASEDIR%\evtx"

echo === DONE ===
```

---

## 11. Timeline Windows (ActivitiesCache)

### Emplacement

```txt
C:\Users\<user>\AppData\Local\ConnectedDevicesPlatform\L.<user>\ActivitiesCache.db
Format : SQLite
Contenu : Activités Windows Timeline (cortana, cross-device)
```

### Extraction

```bash
# Avec WxTCmd (EZ Tools)
WxTCmd.exe -f "C:\Users\suspect\AppData\Local\ConnectedDevicesPlatform\L.suspect\ActivitiesCache.db" \
   --csv /evidence/timeline.csv

# Contenu :
# - Applications utilisées (avec timestamps)
# - Activités cross-device
# - Cortana activities
# - Web searches
```

---

## 12. Recherche de Malware par Artefacts

### Checklist des Artefacts à Vérifier

```txt
□ 1. Prefetch → programmes inconnus
□ 2. AmCache → applications installées
□ 3. ShimCache → exécutables présents/supprimés
□ 4. Event Logs 4688 → création de processus
□ 5. Event Logs 7045 → nouveau service
□ 6. Event Logs 4698 → tâche planifiée
□ 7. Registry Run Keys → persistance
□ 8. Registry Services → persistance service
□ 9. MFT → fichiers créés/modifiés/supprimés
□ 10. USN Journal → changements de fichiers
□ 11. SRUM → utilisation réseau par app
□ 12. BAM/DAM → exécutions
□ 13. Jump Lists + LNK → ouverture de fichiers
□ 14. EVTX Security 4624/4625 → logons
□ 15. PowerShell EVTX 4104 → scripts
```

---

## 13. Ressources

- **Eric Zimmerman Tools** : https://ericzimmerman.github.io
- **Windows Forensics Artifacts** : https://forensikgadget.com/artifacts/
- **SANS Windows Forensics Poster** : https://www.sans.org/posters/
- **DFIR Windows Artifacts** : https://dfir.ru/
- **MalAPI** : https://malapi.io/ (malware API reference)
- **MITRE ATT&CK Windows** : https://attack.mitre.org/techniques/windows/