---
name: forensics-avance
description: Forensics avancé — analyse mémoire volatile (Volatility 3), timeline reconstruction, forensic mobile, cloud forensics, artifacts Windows/Linux/macOS, et carver de fichiers
tags: [forensics, memory, volatility, timeline, mobile, cloud, artifacts, carving]
version: 1.0
---

# Forensics Avancé

Guide d'investigation numérique avancée — acquisition, analyse mémoire, reconstruction temporelle, et extraction d'artefacts.

## 1. Acquisition Mémoire

### Windows
```bash
# Dump RAM (physique → fichier)
# Kernel access required :
winpmem.exe -o memory.raw    # Open source, signed driver
FTK Imager → File → Capture Memory   # GUI
DumpIt.exe                      # Simple + fast
```

### Linux
```bash
# LiME (Linux Memory Extractor)
insmod lime.ko "path=./mem.lime format=lime"
# fmem (ko + /dev/fmem)
insmod fmem.ko
dd if=/dev/fmem of=mem.raw bs=1M
```

### macOS
```bash
# OSXCFF / osxpmem
# macOS >= 10.12 : SIP bloque /dev/mem
# Utiliser : osxpmem.app → physical memory dump
```

### Hibernation & Swap
```bash
# Windows : C:\hiberfil.sys (hibernate)
# Analyse avec volatility -f hiberfil.sys --profile=Win10x64
# Swap : pagefile.sys — contient fragments mémoire
```

## 2. Volatility 3 Advanced

### Profiles & Symbols
```bash
# Volatility 3 : symbol tables automatiques (ISF)
# Windows : pdb symbols → .json ISF
# Linux : DWARF info → ISF
# macOS : DWARF → ISF

vol -f mem.raw windows.info       # OS + KDBG
vol -f mem.raw linux.banner       # Linux kernel version
```

### Analyse Processus
```bash
# Process listing (comparer multiples méthodes)
vol -f mem.raw windows.pslist     # EPROCESS list
vol -f mem.raw windows.psscan     # Pool scanner (hidden)
vol -f mem.raw windows.pstree     # Parent-child tree
vol -f mem.raw windows.psxview    # Cross-view (detect rootkits)

# Détection de processus cachés / rootkits
# Différence entre : PsActiveProcessHead, Csrss handles, PspCidTable
```

### Network
```bash
vol -f mem.raw windows.netscan    # TCP/UDP endpoints
vol -f mem.raw windows.netstat    # Legacy
# Détecter : beacon C2, reverse shells, listeners
```

### DLLs & Modules
```bash
vol -f mem.raw windows.dlllist    # DLL chargées par processus
vol -f mem.raw windows.modscan    # Kernel modules (LKM)
vol -f mem.raw windows.cmdline    # Command line arguments
vol -f mem.raw windows.envars     # Environment variables
```

### Registry Hives (Windows)
```bash
vol -f mem.raw windows.registry.hivelist
vol -f mem.raw windows.registry.printkey -o 0x...  # SAM
vol -f mem.raw windows.registry.printkey --key "ControlSet001\\Control\\ComputerName\\ComputerName"
vol -f mem.raw windows.registry.userassist   # UserAssist (program execution)
vol -f mem.raw windows.registry.shellbags    # Shellbags (directory access)
vol -f mem.raw windows.registry.amcache      # AmCache (installed apps)
```

### MFT & File System
```bash
vol -f mem.raw windows.mftparser    # Master File Table
vol -f mem.raw windows.filescan     # File objects (open/active)
vol -f mem.raw windows.dumpfiles    # Dump files à partir de mémoire
```

## 3. Timeline Analysis

### Super Timeline (Plaso / log2timeline)
```bash
# Créer une timeline super
log2timeline.py --storage-file case.plaso /evidence/

# Analyser la timeline
psort.py -o l2tcsv -w timeline.csv case.plaso

# Filtrer
psort.py -o dynamic -w filtered.csv case.plaso \
  --slice '2024-01-01T00:00:00' '2024-01-02T00:00:00'
```

### Timeline Analysis Workflow
```bash
# 1. Identifier time windows suspects
# 2. Corréler : fichiers créés ⇔ processus ⇔ réseau
# 3. Pattern : malware télécharge → écriture → exécution → suppression
# 4. Trier par : Prefetch, ShimCache, UserAssist, Registry, Event Logs

# Timeline Explorer (MITRE)
# https://github.com/mandiant/flare-vm
```

### Event Logs
```bash
# Windows Event Logs (.evtx)
wevtutil.exe qe Security /f:text /c:5 /q:"*[EventData[Data[@Name='ProcessId']='1234']]"

# Événements clés
# 4624 : Logon success (type 2=interactive, 3=network, 10=remote)
# 4625 : Logon failure → brute force
# 4688 : Process creation
# 4656 : Handle to object
# 4648 : Logon using explicit credentials (runas)
# 1102 : Security log cleared
```

## 4. Linux Forensics

### Acquisition Disk
```bash
# DD style (physique)
dd if=/dev/sda of=/mnt/evidence/disk.dd bs=4M conv=noerror,sync

# EWF (Expert Witness Format)
ewfacquire /dev/sda -t case_drive

# AFF (Advanced Forensic Format)
affconvert -i /dev/sda -o case.aff
```

### Linux Artifact Analysis
```bash
# /var/log/* : auth.log, syslog, kern.log
# .bash_history, .ssh/known_hosts, authorized_keys
# /var/log/wtmp / lastlog / btmp
# /var/log/journal/ (systemd journal)

# Dernières connexions
last -f /var/log/wtmp -100

# Journal analysis
journalctl --since "2024-01-01" --until "2024-01-10"
journalctl -u sshd.service --output=json
```

### Linux Volatility
```bash
vol -f mem.raw linux.bash               # Bash history from mem
vol -f mem.raw linux.psaux              # Process args
vol -f mem.raw linux.check_tty          # TTY processes
vol -f mem.raw linux.mount              # Mounted filesystems
vol -f mem.raw linux.dmesg              # Kernel ring buffer
```

## 5. Browser Forensics

### Chrome/Chromium
```bash
# History, Bookmarks, Cookies, Passwords
# SQLite databases in C:\Users\<user>\AppData\Local\Google\Chrome\User Data\Default\

sqlite3 History "SELECT url, title, visit_count, datetime(last_visit_time/1000000-11644473600,'unixepoch') FROM urls ORDER BY last_visit_time DESC LIMIT 100;"
sqlite3 Cookies "SELECT host_key, name, path, datetime(expires_utc/1000000-11644473600,'unixepoch') FROM cookies;"

# Download artifacts
sqlite3 History "SELECT tab_url, target_path, start_time FROM downloads;"

# Chrome 80+ : SameSite=Lax cookies (forensics implications)
```

### Firefox
```bash
# places.sqlite (history + bookmarks)
sqlite3 places.sqlite "SELECT url, title, datetime(visit_date/1000000,'unixepoch') FROM moz_places JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id;"
```

## 6. Mobile Forensics

### Android
```bash
# ADB backup
adb backup -f backup.ab -apk -shared -all -system

# Analyse .ab
dd if=backup.ab bs=1 skip=24 | openssl zlib -d > backup.tar
tar xvf backup.tar

# Extraction manuelle (root)
adb pull /data/data/   # App data
adb pull /sdcard/      # External storage
adb pull /data/system/gesture.key  # Screen lock
```

### iOS
```bash
# Logical acquisition (iTunes backup)
# Tools : libimobiledevice, iBackupBot, ALEAPP

# Analyse keychain
# iOS 12+ : forensics difficulty increasing
# Tools : Elcomsoft Phone Breaker, GrayKey, Cellebrite

# SQLite WAL files : last activity timestamp in WAL header
```

## 7. Cloud Forensics

### AWS
```bash
# CloudTrail : user activity, API calls
# GuardDuty : threats
# S3 access logs
# VPC Flow Logs

aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=attacker
aws s3api get-bucket-logging --bucket target-bucket
aws ec2 describe-snapshots --owner-ids self  # EBS snapshots
```

### Azure
```bash
# Activity Log (subscription level)
# Azure AD sign-ins (identity)
# Storage analytics logs

az monitor activity-log list --resource-id /subscriptions/...
az vm list --query "[?storageProfile.osDisk.managedDisk.id]"  # VM disks
```

### GCP
```bash
# Cloud Audit Logs : admin, data access, system events
gcloud logging read "resource.type=gce_instance AND protoPayload.methodName=compute.instances.delete"
```

## 8. File Carving

### Foremost
```bash
foremost -t jpeg,png,doc,pdf,zip -i disk.img -o carved/
foremost -c foremost.conf -i memory.raw -o mem_carved/
```

### Scalpel
```bash
# Config : /etc/scalpel/scalpel.conf
scalpel disk.img -o recovered -c custom.conf
```

### Bulk Extractor
```bash
bulk_extractor -o output/ memory.raw
# Extrait : emails, URLs, credit cards, phone numbers
# Aucune dépendance filesystem

# Scanners spécifiques
bulk_extractor -e net -e email -e zip -e base64 -o out/ disk.raw
```

### Photorec / TestDisk
```bash
# Multi-format (500+ signatures)
photorec /d recovered/ /log disk.img
# Interactive : sélectionner partition → type files
```

## 9. Anti-Forensics Detection

### Timestamp Manipulation
```bash
# Detection : USN journal trace modif timestamp
# MACE times mismatch (Modified/Accessed/Created/Entry)
# $STANDARD_INFORMATION vs $FILE_NAME difference
# MFT entry sequence number jump
```

### Data Wiping
```bash
# Detect : 
# - MFT entries zeroed vs. deleted (0x00 vs. 0xE5)
# - SSD TRIM → unable to recover (no slac)
# - S.M.A.R.T. data : reallocated sectors
# - Artifacts in pagefile.sys / swap / hibernate
```

### Encryption Detection
```bash
# Volume headers : TrueCrypt, VeraCrypt, BitLocker, FileVault
# High entropy analysis (chi-test, Shannon)
# Tools : bulk_extractor entropy scan, binwalk entropy
```

## 10. Tools Compendium

### Autopsy / Sleuth Kit
```bash
# CLI : mmls, fsstat, fls, icat, mactime
tsk_loaddb /evidence/disk.img -d case.db
mactime -b case.body -d > timeline.csv

# Autopsy GUI : ingest modules, keyword search, timeline
```

### Plaso / log2timeline
```bash
# Install
pip install plaso
# Use
log2timeline.py --storage-file case.plaso /evidence/
pinfo.py case.plaso  # Summary
psort.py -o l2tcsv -w timeline.csv case.plaso
```

### EZ Tools (Eric Zimmerman)
```bash
# MFTECmd : $MFT parser
MFTECmd.exe -f "C:\$MFT" --csv mft_output.csv

# AppCompatCacheParser (ShimCache)
AppCompatCacheParser.exe -f SYSTEM --csv output.csv

# AmcacheParser
AmcacheParser.exe -f Amcache.hve --csv output.csv

# SBECmd (Shellbags)
SBECmd.exe -d "C:\Users\user" --csv output.csv

# TimelineExplorer (.csv viewer with filters)
```

## 11. Chain of Custody

```bash
# Hashing
sha256sum disk.img > disk.hash
md5sum disk.img >> disk.hash

# Documentation
# - Date/heure d'acquisition
# - Méthode utilisée
# - Hash + signature
# - Description du système
# - People présents
```

## 12. Ressources

- **13Cubed** : https://www.youtube.com/@13Cubed (excellent video series)
- **SANS SIFT Workstation** : Forensic Linux distro
- **Volatility 3** : https://github.com/volatilityfoundation/volatility3
- **Plaso** : https://github.com/log2timeline/plaso
- **Eric Zimmerman Tools** : https://ericzimmerman.github.io
- **DFIR Wizard** : https://www.dfirwizard.com
- **ForensicArtifacts.com** : artifact database
- **HackTheBox Forensics** : lab practice