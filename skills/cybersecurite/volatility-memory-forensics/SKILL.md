---
name: volatility-memory-forensics
description: Guide complet de Volatility 3 — analyse mémoire volatile, processus cachés, rootkits, réseau, registry, credentials, MFT, kernel objects, et plugins avancés
tags: [forensics, memory, volatility, volatility3, ram-analysis, rootkit-detection, credentials]
version: 1.0
---

# Volatility 3 — Analyse Forensique Mémoire Complète

Guide exhaustif de Volatility 3 (ex-Volatility Foundation) pour l'analyse de la mémoire volatile (RAM).

---

## 1. Installation et Configuration

### Installation

```bash
# Volatility 3 (Python 3.8+)
git clone https://github.com/volatilityfoundation/volatility3.git
cd volatility3
pip install -r requirements.txt
python3 vol.py

# Ou via pip
pip install volatility3
python3 -m volatility

# Symbol Tables (ISF)
# Windows : téléchargement automatique via internet
# Linux/macOS : nécessite génération (dwarf2json)
```

### Symbol Tables (ISF)

```bash
# Windows : auto-download depuis https://downloads.volatilityfoundation.org/
# Les symboles sont chargés automatiquement selon la version de l'OS

# Linux : génération des symboles
git clone https://github.com/volatilityfoundation/dwarf2json.git
cd dwarf2json && go build
sudo dwarfdump /boot/vmlinuz-$(uname -r) | sudo tee /tmp/kernel.dwarf
./dwarf2json linux --elf /tmp/kernel.dwarf > /tmp/kernel.json
cp /tmp/kernel.json /path/to/volatility3/volatility3/framework/symbols/linux/

# macOS : génération depuis le kernelcache
./dwarf2json mac --macho /System/Library/Kernels/kernel.release.t8101 > mac.json
```

### Vérification

```bash
python3 vol.py -f memory.dmp windows.info
# Si OK : version OS + KDBG + CPU count + date
# Si FAIL : mauvais profile / image corrompue
```

---

## 2. Profilage et Information Système

### Déterminer l'OS et la version

```bash
# Windows
python3 vol.py -f memory.dmp windows.info
# Résultat :
#   Image Type : Windows 10 22H2 (19045)
#   KDBG : 0xf8000280c0a0
#   CPU : 8 cores
#   Time : 2024-07-22 14:30:00

# Linux
python3 vol.py -f mem.lime linux.banner      # Kernel version
python3 vol.py -f mem.lime linux.info        # Système info
python3 vol.py -f mem.lime linux.check_syslog # Logs noyau

# macOS
python3 vol.py -f mem.raw mac.banner         # Version macOS
python3 vol.py -f mem.raw mac.version        # Build number
```

---

## 3. Analyse des Processus

### Process Listing

```bash
# Standard (EPROCESS doubly linked list)
python3 vol.py -f mem.raw windows.pslist
# Colonnes : PID, PPID, ImageFileName, Offset(V), Threads, Handles, SessionId, Wow64, CreateTime, ExitTime

# Pool Scanner (détecte les processus cachés)
python3 vol.py -f mem.raw windows.psscan
# Scanne les pools mémoire pour trouver des EPROCESS orphelins

# Arbre des processus (relations parent-enfant)
python3 vol.py -f mem.raw windows.pstree
# Permet de détecter les processus orphelins (parent supprimé)

# Cross-View Detection
python3 vol.py -f mem.raw windows.psxview
# Compare 5 sources : PsActiveProcessHead, PspCidTable, Csrss, Session, Desktop
# Les processus présents dans psscan mais PAS dans pslist = CACHÉS
```

### Détection de Rootkits par Cross-View

```bash
# Principe : un rootkit hooke PsActiveProcessHead pour cacher un processus
# Mais ne peut pas le supprimer de PspCidTable (table des handles)

# Interprétation psxview :
# False = processus NON trouvé dans cette source
# True = processus trouvé

# Si un processus est :
# - PsActiveProcessHead : False  ← Caché de la liste standard
# - PspCidTable : True           ← Mais toujours dans la table
# → PROCESSUS CACHÉ (rootkit probable)

# Les "faux positifs" normaux :
# - System (PID 4) : csrss=False, session=False
# - smss.exe : csrss=False, session=False, desktop=False
# - Processus en cours de terminaison
```

### Process Détail

```bash
# Ligne de commande
python3 vol.py -f mem.raw windows.cmdline
# PID    Process    Args
# 1234   malware    C:\Users\suspect\AppData\Local\Temp\svchost.exe -n 10 -c C2

# Variables d'environnement
python3 vol.py -f mem.raw windows.envars --pid 1234
# TEMP, PATH, USERNAME, APPDATA → confirmer le contexte

# Handles (ressources ouvertes)
python3 vol.py -f mem.raw windows.handles --pid 1234
# File, Key, Thread, Process, Desktop, Event, Mutant, Token, etc.

# DLLs chargées
python3 vol.py -f mem.raw windows.dlllist --pid 1234
# Détecter le DLL injection :
# DLL chargée depuis un dossier temporaire ou non-standard
# DLL non signée dans un processus système
```

### Détection de Malware par Processus

```bash
# Malfind (détection de code injecté)
python3 vol.py -f mem.raw windows.malfind
# Scanne les régions mémoire privées pour des droits d'exécution suspects
# Indicateurs :
# - PAGE_EXECUTE_READWRITE (RWX)
# - MZ/PE header dans une heap ou stack
# - Shellcode visible

# Dump du processus pour analyse
python3 vol.py -f mem.raw windows.memmap --pid 1234 --dump
# Crée un dump complet du processus → analyse statique

# GetSIDs (SID du processus)
python3 vol.py -f mem.raw windows.getservicesids --pid 1234
python3 vol.py -f mem.raw windows.privileges --pid 1234
# Vérifier si le malware a des privilèges excessifs (SeDebugPrivilege, SeTcbPrivilege)
```

---

## 4. Analyse Réseau

### Connexions réseau

```bash
# Scan des connexions TCP/UDP (NETIO driver)
python3 vol.py -f mem.raw windows.netscan
# Colonnes : Type, LocalAddr, RemoteAddr, State, PID, Offset, CreateTime

# Interprétation :
# ESTABLISHED + RemoteAddr ≠ LAN → exfiltration ou C2
# LISTENING + Port élevé → backdoor
# CLOSE_WAIT → connexion fermée

# Netstat legacy (TcpIp)
python3 vol.py -f mem.raw windows.netstat
# Moins fiable que netscan, peut manquer certaines connexions
```

### Analyse de Beacons C2

```bash
# Détecter des patterns de communication réguliers :
# 1. Connexions ESTABLISHED vers une IP externe
# 2. Requêtes DNS répétées vers un même domaine
# 3. Protocole non standard (port inhabituel)

# Vérification :
python3 vol.py -f mem.raw windows.netscan | grep ESTABLISHED
# Analyser le timestamps des connexions
# Calculer l'intervalle entre les connexions → périodicité du beacon

# DNS caché
python3 vol.py -f mem.raw windows.dnscache  # DNS cache resolver
# Voir les résolutions DNS qui ne correspondent pas à la navigation
```

### Sockets Linux

```bash
python3 vol.py -f mem.lime linux.netstat        # Sockets + connexions
python3 vol.py -f mem.lime linux.arp            # Table ARP
python3 vol.py -f mem.lime linux.ifconfig       # Interfaces réseau
python3 vol.py -f mem.lime linux.route_cache    # Cache de routage
```

---

## 5. Extraction de Credentials

### Windows

```bash
# Hashdump (SAM + SYSTEM)
python3 vol.py -f mem.raw windows.hashdump
# Extrait les hash NTLM du registre SAM

# LSA Secrets
python3 vol.py -f mem.raw windows.lsadump
# Extrait les secrets LSA (mots de passe service, cache domain)

# Cached Domain Credentials (MSCash)
python3 vol.py -f mem.raw windows.cachedump
# Hash MSCashV2 des credentials domaine mis en cache

# DPAPI
python3 vol.py -f mem.raw windows.dpapiscan
# Localise les blobs DPAPI (Master Key files)
python3 vol.py -f mem.raw windows.dpapi --masterkeyfile /path/to/masterkey
```

### Linux

```bash
python3 vol.py -f mem.lime linux.bash                 # Bash history from RAM
python3 vol.py -f mem.lime linux.psaux                 # Arguments processus
python3 vol.py -f mem.lime linux.check_creds          # Credentials structure
```

---

## 6. Analyse du Registre Windows

### Hive Listing

```bash
python3 vol.py -f mem.raw windows.registry.hivelist
# Liste toutes les ruches du registre avec leurs offsets
# SAM, SYSTEM, SOFTWARE, SECURITY, NTUSER.DAT
```

### PrintKey (lire une clé)

```bash
# Lire une clé complète
python3 vol.py -f mem.raw windows.registry.printkey -o <hive_offset>
python3 vol.py -f mem.raw windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
python3 vol.py -f mem.raw windows.registry.printkey --key "ControlSet001\Control\ComputerName\ComputerName"

# Exemples de clés forensiques :
python3 vol.py -f mem.raw windows.registry.printkey --key "Microsoft\Windows NT\CurrentVersion\Prefetcher"
python3 vol.py -f mem.raw windows.registry.printkey --key "ControlSet001\Enum\USBSTOR"
python3 vol.py -f mem.raw windows.registry.printkey --key "ControlSet001\Services"
```

### UserAssist

```bash
# Trace des programmes exécutés par l'utilisateur (GUI)
python3 vol.py -f mem.raw windows.registry.userassist
# Colonnes : Identifiant GUID, Nom du programme, Compteur, Date
# Permet de savoir quels programmes ont été exécutés et combien de fois
```

### ShellBags

```bash
# Historique des dossiers ouverts dans l'Explorateur
python3 vol.py -f mem.raw windows.registry.shellbags
# Révèle l'exploration de dossiers même supprimés
# Taille, vue, position de la fenêtre
```

### AmCache

```bash
# Base de données des programmes installés (Application Compatibility Cache)
python3 vol.py -f mem.raw windows.registry.amcache
# Contient : nom, version, chemin, date d'installation, exécutable
# Meilleure source pour les applications installées
```

### ShimCache (AppCompatCache)

```bash
# Cache de compatibilité des exécutables
python3 vol.py -f mem.raw windows.shimcache
# Liste des .exe qui ont été exécutés (même si supprimés)
# Attention : ne conserve que le dernier timestamp d'exécution
```

---

## 7. Analyse du Système de Fichiers

### MFT (Master File Table)

```bash
# Parser la MFT depuis la mémoire
python3 vol.py -f mem.raw windows.mftparser
# Extrait les entrées MFT (fichiers, dossiers, attributs)
# Contient : noms, timestamps, tailles, flags

# Options :
python3 vol.py -f mem.raw windows.mftparser --output csv > mft.csv
python3 vol.py -f mem.raw windows.mftparser --name-only   # Noms seulement
python3 vol.py -f mem.raw windows.mftparser --no-name     # Sans les noms
```

### File Scan

```bash
# Fichiers ouverts/actifs (File Object)
python3 vol.py -f mem.raw windows.filescan
# Liste les File Objects dans la mémoire
# Inclut les fichiers supprimés mais encore ouverts

# Utile pour :
# - Voir les fichiers ouverts par un malware
# - Détecter des fichiers temporaires suspects
```

### Dump de fichiers

```bash
# Dump tous les fichiers d'un processus
python3 vol.py -f mem.raw windows.dumpfiles --pid 1234
# Extrait les fichiers mappés en mémoire par le processus

# Dump d'un fichier spécifique (par offset)
python3 vol.py -f mem.raw windows.dumpfiles --physaddr 0x1234567890

# Dump complet de la mémoire du processus
python3 vol.py -f mem.raw windows.memmap --pid 1234 --dump
```

### TrueCrypt / VeraCrypt Detection

```bash
python3 vol.py -f mem.raw windows.truecrypt       # Détection conteneurs
python3 vol.py -f mem.raw windows.truecryptsummary # Résumé
# Détecte les volumes chiffrés montés et les passphrases en mémoire
```

---

## 8. Analyse du Noyau

### Kernel Objects

```bash
# Modules noyau chargés
python3 vol.py -f mem.raw windows.modscan
# Détection de rootkit kernel-mode

# Driver IRP Hooks
python3 vol.py -f mem.raw windows.driverirp
# Vérifie si les IRP (I/O Request Packets) sont hookés
# Un rootkit peut intercepter les appels vers le disque/réseau

# SSDT (System Service Descriptor Table)
python3 vol.py -f mem.raw windows.ssdt
# Détecte les hooks dans la table des appels système

# IDT (Interrupt Descriptor Table)
python3 vol.py -f mem.raw windows.idt
# Détecte les hooks d'interruptions (keyloggers, etc.)
```

### Callbacks

```bash
# Kernel callbacks (notifications)
python3 vol.py -f mem.raw windows.callbacks
# Types :
# - Process creation callback (NotifyRoutine)
# - Thread creation callback
# - Image load callback (DLL injection detection)
# - Registry callback
# - Object callback
# - BugCheck callback (blue screen capture)

# Un rootkit installe ses propres callbacks
# Vérifier les adresses des callbacks contre les modules connus
```

### Timers et DPC

```bash
# Kernel timers
python3 vol.py -f mem.raw windows.timers
# Détection de rootkit via des timers périodiques suspects
python3 vol.py -f mem.raw windows.dpcs   # Deferred Procedure Calls
```

---

## 9. Analyse de la Navigation / Internet

```bash
# Cookies Internet Explorer
python3 vol.py -f mem.raw windows.ie.cookies

# Historique IE
python3 vol.py -f mem.raw windows.ie.history

# WebCacheV30.dat (EDGE/Chrome cache dans Win 8+)
# Pas de plugin direct → dumpfiles puis analyse SQLite

# Chrome/Firefox
# Les données de navigation sont rarement en mémoire persistante
# → Extraire les processus et chercher les URL avec strings
strings chrome.dmp | grep -E "https?://" | sort -u
```

---

## 10. Plugins Volatility 3 Avancés

### Windows

```bash
# BigPools (analyse des allocations mémoire noyau)
python3 vol.py -f mem.raw windows.bigpools
# Utile pour détecter les fragments de malware dans le noyau

# CMD History
python3 vol.py -f mem.raw windows.cmdline   # Command lines
# (Volatility 3 n'a pas de dédié cmdline history comme V2)

# Registry Hive diff
python3 vol.py -f mem.raw windows.registry.hivescan  # Scan des ruches

# Event Logs
python3 vol.py -f mem.raw windows.evtxs       # Extraire les logs
python3 vol.py -f mem.raw windows.evtxs --dump # Dump des evtx
```

### Linux

```bash
python3 vol.py -f mem.lime linux.check_modules       # Modules noyau chargés
python3 vol.py -f mem.lime linux.check_idt            # IDT hooks
python3 vol.py -f mem.lime linux.check_syslog         # Kernel log
python3 vol.py -f mem.lime linux.check_afinfo         # Network hooks
python3 vol.py -f mem.lime linux.check_creds          # Credentials checks
python3 vol.py -f mem.lime linux.list_system_call     # Système calls
python3 vol.py -f mem.lime linux.tty_check            # TTY processes
python3 vol.py -f mem.lime linux.proc_maps            # Memory maps
python3 vol.py -f mem.lime linux.lsmod                # Loaded modules
python3 vol.py -f mem.lime linux.mount                # Mounts
python3 vol.py -f mem.lime linux.kmsg                # Kernel messages
```

### macOS

```bash
python3 vol.py -f mem.raw mac.pslist                  # Process list
python3 vol.py -f mem.raw mac.psxview                 # Cross-view
python3 vol.py -f mem.raw mac.malfind                 # Code injection
python3 vol.py -f mem.raw mac.netstat                 # Network
python3 vol.py -f mem.raw mac.lsmod                   # Kernel modules
python3 vol.py -f mem.raw mac.check_syscall           # Syscall table
python3 vol.py -f mem.raw mac.check_trap_table        # Trap table
python3 vol.py -f mem.raw mac.trustcache               # macOS trust cache
python3 vol.v -f mem.raw mac.filecheck                # File checks
```

---

## 11. Automation et Scripting

### Script Volatility Automatisé

```bash
#!/bin/bash
# auto_volatility.sh — Analyse mémoire automatisée

DUMP=$1
OUTDIR="./volatility_report_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTDIR"

echo "=== VOLATILITY AUTOMATED ANALYSIS ==="
echo "Target : $DUMP"
echo "Output : $OUTDIR"

# 1. INFO
echo "[1/10] System info..."
python3 vol.py -f "$DUMP" windows.info > "$OUTDIR/01_system_info.txt"

# 2. PROCESSES
echo "[2/10] Process listing..."
python3 vol.py -f "$DUMP" windows.pslist > "$OUTDIR/02_pslist.txt"
python3 vol.py -f "$DUMP" windows.psscan > "$OUTDIR/02_psscan.txt"
python3 vol.py -f "$DUMP" windows.pstree > "$OUTDIR/02_pstree.txt"
python3 vol.py -f "$DUMP" windows.psxview > "$OUTDIR/02_psxview.txt"

# 3. NETWORK
echo "[3/10] Network analysis..."
python3 vol.py -f "$DUMP" windows.netscan > "$OUTDIR/03_netscan.txt"

# 4. MALWARE
echo "[4/10] Malware detection..."
python3 vol.py -f "$DUMP" windows.malfind > "$OUTDIR/04_malfind.txt"
python3 vol.py -f "$DUMP" windows.modscan > "$OUTDIR/04_modscan.txt"
python3 vol.py -f "$DUMP" windows.driverirp > "$OUTDIR/04_driverirp.txt"
python3 vol.py -f "$DUMP" windows.ssdt > "$OUTDIR/04_ssdt.txt"

# 5. CREDENTIALS
echo "[5/10] Credentials..."
python3 vol.py -f "$DUMP" windows.hashdump > "$OUTDIR/05_hashdump.txt"
python3 vol.py -f "$DUMP" windows.lsadump > "$OUTDIR/05_lsadump.txt"
python3 vol.py -f "$DUMP" windows.cachedump > "$OUTDIR/05_cachedump.txt"

# 6. REGISTRY
echo "[6/10] Registry..."
python3 vol.py -f "$DUMP" windows.registry.hivelist > "$OUTDIR/06_hivelist.txt"
python3 vol.py -f "$DUMP" windows.registry.userassist > "$OUTDIR/06_userassist.txt"
python3 vol.py -f "$DUMP" windows.registry.shellbags > "$OUTDIR/06_shellbags.txt"
python3 vol.py -f "$DUMP" windows.shimcache > "$OUTDIR/06_shimcache.txt"
python3 vol.py -f "$DUMP" windows.registry.amcache > "$OUTDIR/06_amcache.txt"

# 7. FILES
echo "[7/10] File system..."
python3 vol.py -f "$DUMP" windows.mftparser > "$OUTDIR/07_mft.txt"
python3 vol.py -f "$DUMP" windows.filescan > "$OUTDIR/07_filescan.txt"

# 8. CALLBACKS
echo "[8/10] Kernel callbacks..."
python3 vol.py -f "$DUMP" windows.callbacks > "$OUTDIR/08_callbacks.txt"
python3 vol.py -f "$DUMP" windows.timers > "$OUTDIR/08_timers.txt"

# 9. NETWORK CACHE
echo "[9/10] DNS cache..."
python3 vol.py -f "$DUMP" windows.dnscache > "$OUTDIR/09_dnscache.txt"

# 10. SUMMARY
echo "[10/10] Generating summary..."
{
  echo "=== ANALYSIS SUMMARY ==="
  echo "File: $DUMP"
  echo "Date: $(date)"
  echo ""
  echo "--- SUSPICIOUS PROCESSES ---"
  grep -E "CMD|PowerShell|mshta|rundll32|wscript|cscript|regsvr32" "$OUTDIR/02_pslist.txt"
  echo ""
  echo "--- NETWORK CONNECTIONS ---"
  grep ESTABLISHED "$OUTDIR/03_netscan.txt"
  echo ""
  echo "--- MALFIND HITS ---"
  wc -l "$OUTDIR/04_malfind.txt"
} > "$OUTDIR/99_summary.txt"

echo "Done. Report in $OUTDIR"
```

---

## 12. Dépannage Volatility

### Problèmes Courants

```bash
# "No suitable kernel address space mapping"
# Image corrompue ou format non supporté
file memory.dmp           # Vérifier le format
# WinPMEM, FTK Imager, DumpIt → RAW MEM
# Hiberfil.sys → compressé, volatile

# "Symbol table not found"
# Windows trop récent ou inconnu
python3 vol.py -f mem.raw windows.info    # Voir le banner
# Télécharger les symboles manuellement
# ou générer ISF

# "Address space failed to instantiate"  
# Image 32-bit sur 64-bit / problème d'offset
# Essayer --single-state / -vv pour debug

# Out of memory
# Images RAM > 16GB
# Utiliser --output-file pour écrire directement
# Limiter les plugins gourmands (mftparser, malfind)
```

### Comparaison Volatility 2 vs 3

```bash
# Volatility 2 (legacy) :
volatility -f mem.dmp --profile=Win10x64_19041 pslist
volatility -f mem.dmp --profile=Win7SP1x64 timeliner
volatility -f mem.dmp --profile=Win10x64_19041 consoles

# Volatility 3 (recommandé) :
python3 vol.py -f mem.raw windows.pslist
python3 vol.py -f mem.raw windows.cmdline   # Remplace consoles
python3 vol.py -f mem.raw windows.registry.userassist  # Timeliner-like

# V2 → V3 mapping :
# malfind   → windows.malfind
# hivelist  → windows.registry.hivelist
# hashdump  → windows.hashdump
# netscan   → windows.netscan
# linux_psaux → linux.psaux
```

---

## 13. Ressources

- **Volatility 3 GitHub** : https://github.com/volatilityfoundation/volatility3
- **Volatility Foundation** : https://volatilityfoundation.org/
- **Symbol Tables** : https://downloads.volatilityfoundation.org/
- **dwarf2json** : https://github.com/volatilityfoundation/dwarf2json
- **Windows KDBG** : https://volatility3.readthedocs.io/
- **13Cubed Volatility Tutorials** : https://www.youtube.com/@13Cubed
- **Malapi** : https://malapi.io/ (malware API reference)