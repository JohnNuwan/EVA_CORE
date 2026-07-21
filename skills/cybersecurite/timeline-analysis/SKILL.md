---
name: timeline-analysis
description: Guide complet de reconstruction chronologique forensique — Plaso/log2timeline, Super Timeline, MFT, Event Logs Windows, journal Linux, MAC times, corrélation d'événements, timeline explorer, et reconstruction de scénarios
tags: [forensics, timeline, plaso, log2timeline, mft, event-logs, mac-times, super-timeline]
version: 1.0
---

# Analyse de Timeline — Reconstruction Chronologique

Guide exhaustif des techniques de reconstruction temporelle en investigation numérique.

---

## 1. Fondamentaux des Timelines Forensiques

### Pourquoi une Timeline ?

```txt
Une timeline permet de :
- Reconstruire la séquence des événements
- Identifier les actions avant/pendant/après un incident
- Corréler les événements (réseau ↔ fichier ↔ processus)
- Détecter les anomalies temporelles
- Présenter les preuves chronologiquement
- Contredire un alibi
```

### Types de Timelines

```txt
Timeline Simple (Body File)
  Format Sleuth Kit : mtime | atime | ctime | crtime | inode | nom
  Générée par : fls, icat, mactime
  Utile pour : analyse rapide d'un disque

Timeline Super (Plaso)
  Agrège TOUS les artefacts : FS, Registry, Event Logs, Web, Email
  Générée par : log2timeline
  Utile pour : investigation complète

Timeline Spécifique (Artefact)
  Un seul type d'artefact : Prefetch, ShimCache, UserAssist
  Générée par : Volatility, EZ Tools
  Utile pour : focus sur un aspect particulier
```

### Artefacts Temporels

```txt
SYSTÈME DE FICHIERS :
- MFT (Master File Table) : MACE / $STANDARD_INFORMATION / $FILE_NAME
- MAC times : Modified, Accessed, Changed, Created
- USN Journal : changements du volume
- $LogFile : journal NTFS transactionnel

REGISTRE :
- UserAssist : exécution de programmes GUI
- ShimCache (AppCompatCache) : .exe exécutés
- AmCache : applications installées
- ShellBags : navigation dans les dossiers

LOGS :
- Event Logs (.evtx) : Security, System, Application, PowerShell
- syslog/journald : Linux events
- auth.log : connexions SSH

APPLICATIONS :
- Web : historique, cookies, downloads, bookmarks
- Email : envoi/réception
- Messagerie : SMS, WhatsApp, Telegram
```

---

## 2. Plaso / log2timeline — Super Timeline

### Installation

```bash
# pip
pip install plaso

# Ubuntu/Debian
sudo apt install plaso-tools

# Vérification
log2timeline.py --version
psort.py --version
pinfo.py --version
```

### Création d'une Timeline

```bash
# Workflow de base
# 1. Créer le storage file (base de données SQLite)
log2timeline.py --storage-file /evidence/case.plaso /evidence/disk.dd

# Options importantes
log2timeline.py \
   --storage-file /evidence/case.plaso \
   --status-view window \        # Affichage de progression
   --partitions all \            # Analyser toutes les partitions
   --vss-stores all \            # Volume Shadow Copies
   --hashers md5,sha256 \         # Hash des fichiers
   /evidence/disk.dd

# Timezone (important pour l'analyse)
log2timeline.py --storage-file case.plaso \
   --timezone "Europe/Paris" \
   disk.dd
```

### Analyse du Storage

```bash
# Résumé du storage file
pinfo.py /evidence/case.plaso
# Affiche :
# - Sessions (combien d'analyses)
# - Parsers utilisés
# - Nombre d'events par parser
# - Timeline complète : début → fin

# Export en CSV
psort.py -o l2tcsv -w /evidence/timeline.csv /evidence/case.plaso

# Export en JSON (analyse programmatique)
psort.py -o json -w /evidence/timeline.json /evidence/case.plaso

# Export dynamique (filtrage)
psort.py -o dynamic -w filtered.csv /evidence/case.plaso \
   --slice '2024-07-20T00:00:00' '2024-07-21T00:00:00'
```

### Filtrage Avancé

```bash
# Filtrer par timestamp
psort.py -o l2tcsv -w timeline.csv case.plaso \
   --slice '2024-07-20T10:00:00' '2024-07-20T14:00:00'

# Filtrer par parser
psort.py -o l2tcsv -w webanalysis.csv case.plaso \
   --parsers winreg,webhist

# Filtrer par type d'event (data type)
psort.py -o l2tcsv -w filesystem.csv case.plaso \
   --query 'data_type is "fs:stat"'

# Filtrer par fichier spécifique
psort.py -o l2tcsv -w malware_file.csv case.plaso \
   --query 'filename contains "malware.exe"'

# Filtrer par utilisateur
psort.py -o l2tcsv -w user_suspect.csv case.plaso \
   --query 'username is "suspect"'

# Combinaison de filtres
psort.py -o l2tcsv -w incident_window.csv case.plaso \
   --slice '2024-07-20T09:30:00' '2024-07-20T10:30:00' \
   --query 'data_type is "pe:compilation" or data_type contains "mft"'
```

### Parsers Disponibles

```bash
# Lister les parsers
log2timeline.py --parsers list

# Parsers par catégorie :
# fs:*       — Système de fichiers (stat, mft, ntfs, etc.)
# winreg:*   — Registre Windows (sam, software, system, userassist, etc.)
# winevt:*   — Event Logs Windows (security, system, application, etc.)
# webhist:*  — Navigation web (chrome, firefox, safari, ie)
# olecf:*    — OLE (Office documents)
# pe:*       — Portable Executables (exe, dll)
# skydrive:* — OneDrive logs
# custom:*   — Plugins personnalisés
```

---

## 3. MFT (Master File Table) Timeline

### Structure MFT

```txt
Chaque fichier/dossier a 2 entrées temporelles distinctes :

┌────────────────────────────────────────────────┐
│ $STANDARD_INFORMATION ($SI)                     │
│   - Modifié : quand l'explorateur modifie       │
│   - Accédé : lecture/ouverture                  │
│   - Créé : création du fichier                  │
│   - MFT modifié : changement attributs MFT      │
│   Modifiable par l'utilisateur (API)            │
├────────────────────────────────────────────────┤
│ $FILE_NAME ($FN)                                │
│   - Mêmes 4 timestamps                          │
│   - MAIS mis à jour SEULEMENT par le FS          │
│   - Impossible à modifier via API               │
│   → SI vs FN différent = timestamp modifié !     │
└────────────────────────────────────────────────┘
```

### Analyse MFT avec MFTECmd (EZ Tools)

```bash
# Télécharger EZ Tools
# https://ericzimmerman.github.io

# Extraction MFT
MFTECmd.exe -f "C:\$MFT" --csv mft_output.csv

# Filtres temporels
MFTECmd.exe -f "C:\$MFT" --csv mft.csv \
   --de 2024-07-20 --dt 2024-07-22  # Date range

# Recherche de fichiers supprimés
MFTECmd.exe -f "C:\$MFT" --csv deleted.csv --deleted

# Recherche de fichiers par nom
MFTECmd.exe -f "C:\$MFT" --csv malware_search.csv \
   --body "malware" --body "backdoor"

# Détection de timestamp modification ($SI vs $FN)
MFTECmd.exe -f "C:\$MFT" --csv anomaly.csv --anomaly
# Résultat : lignes où $SI_diffère de $FN
```

### Analyse MFT avec Volatility

```bash
# Depuis la mémoire
vol -f memory.raw windows.mftparser --output csv > mft_from_mem.csv

# Depuis une image disque montée
# Aucun outil direct → via sleep walker

# sleep walker — MFT offline analysis
sudo pip install sleuthkit
sudo mmls disk.dd
sudo fls -o 2048 -rp disk.dd > fls_list.txt

# MFT extrac
icat -o 2048 disk.dd 0 > mft.raw  # MFT entry 0 = $MFT
# Parser MFT
analyzeMFT.py -f mft.raw -o mft_analysis.csv
```

### Timestamps Anormaux — Détection

```bash
# 1. Timestamps futurs
grep -E "2025|2026|2030" timeline.csv

# 2. Timestamps epoch (1970-01-01)
grep "1970-01-01" timeline.csv

# 3. Mismatch $SI vs $FN
# Un outil anti-forensic fait concorder SI et FN
# Normal : tous les timestamps FN ≤ SI
# Suspect : SI modifié mais FN inchangé → altération

# 4. Timestamps de suppression avant création
# Indique un effacement intentionnel suivi d'une recréation

# 5. Cluster gap
# Fichier qui existe dans MFT mais sans cluster alloué
```

---

## 4. Windows Event Logs (.evtx)

### Événements Clés

```txt
┌──────────────────────────────────────────────────────────────┐
│ Événements de Sécurité (Security.evtx)                       │
├──────────────────────────────────────────────────────────────┤
│ 4624 — Logon réussi                                          │
│    Type : 2=interactif, 3=réseau, 7=déverrouillage,         │
│           8=NetworkCleartext, 9=NewCredentials,              │
│           10=RemoteInteractive(RDP)                          │
│    Attributs : LogonID, TargetUser, SourceIP                 │
│                                                              │
│ 4625 — Logon échoué (brute force)                            │
│    Status : 0xC000006D (bad password)                        │
│             0xC0000064 (user not found)                      │
│             0xC0000072 (account locked)                      │
│                                                              │
│ 4672 — Logon avec privilèges admin (SeTcbPrivilege)          │
│ 4648 — Logon avec credentials explicites (runas)             │
│                                                              │
│ 4688 — Création de processus                                 │
│    Attributs : CreatorProcessID, ProcessName,                │
│                CreatorToken (IsAdmin?)                       │
│                                                              │
│ 4689 — Fin de processus                                      │
│ 4656 — Handle ouvert vers un objet                           │
│                                                              │
│ 4698 — Tâche planifiée créée                                 │
│ 4699 — Tâche planifiée supprimée                             │
│ 4702 — Tâche planifiée mise à jour                           │
│                                                              │
│ 4719 — Politique d'audit modifiée                            │
│ 1102 — Journal de sécurité effacé (ALERTE !)                 │
│                                                              │
│ 5156 — Connexion sortante autorisée (Firewall)               │
│ 5157 — Connexion sortante bloquée                            │
│                                                              │
│ Événements Système (System.evtx)                             │
│ 1001 — BugCheck (BSOD / Crash dump)                          │
│ 7036 — Service started/stopped                               │
│ 7045 — Nouveau service installé                              │
│                                                              │
│ PowerShell (PowerShell.evtx)                                 │
│ 4103 — PowerShell script execution (module logging)          │
│ 4104 — PowerShell script block logging                       │
│ 40961 — PowerShell console startup                          │
└──────────────────────────────────────────────────────────────┘
```

### Extraction avec wevtutil

```batch
:: Windows natif
:: Exporter les logs
wevtutil epl Security C:\evidence\security.evtx
wevtutil epl System C:\evidence\system.evtx
wevtutil epl Application C:\evidence\app.evtx
wevtutil epl "Windows PowerShell" C:\evidence\powershell.evtx

:: Filtrage par date
wevtutil epl Security C:\evidence\security_filtered.evtx /q:"*[System[TimeCreated[timediff(@SystemTime) <= 86400000]]]"
:: 86400000 ms = 24h

:: Filtrage par EventID
wevtutil epl Security C:\evidence\sec_4624.evtx /q:"*[System[EventID=4624]]"
```

### Extraction avec PowerShell

```powershell
# Événements locaux
Get-WinEvent -LogName Security | Where-Object {$_.Id -eq 4624} | Export-Csv sec_4624.csv

# Événements d'un .evtx exporté
Get-WinEvent -Path "C:\evidence\security.evtx" -MaxEvents 1000

# Filtrage temporel
$start = Get-Date "2024-07-20"
$end = Get-Date "2024-07-22"
Get-WinEvent -FilterHashtable @{LogName='Security'; StartTime=$start; EndTime=$end} | Export-Csv timeline.csv

# Recherche de processus suspects
Get-WinEvent -FilterHashtable @{LogName='Security'; ID=4688} | Where-Object {$_.Properties[5].Value -match "powershell|cmd|rundll32|mshta"} | Format-Table TimeCreated, Properties
```

### Extraction avec Plaso

```bash
# Plaso parse automatiquement les .evtx
log2timeline.py --storage-file case.plaso /evidence/windows/

# Filtrage des events EVTX seulement
psort.py -o l2tcsv -w evtx_events.csv case.plaso \
   --query 'data_type is "windows:evtx:record"'

# Recherche d'EventIDs spécifiques
psort.py -o l2tcsv -w logon_events.csv case.plaso \
   --query 'event_identifier is 4624 or event_identifier is 4625'

# Recherche de command lines
psort.py -o l2tcsv -w processes.csv case.plaso \
   --query 'data_type contains "process" and parser contains "evtx"'
```

---

## 5. Timeline Linux

### Journal systemd

```bash
# Journal systemd — format binaire (journalctl)

# Exporter en texte
journalctl --since "2024-07-20 00:00:00" --until "2024-07-22 23:59:59" > journal.txt

# Exporter en JSON
journalctl -o json-pretty --since "-7 days" > journal.json

# Exporter le journal binaire
journalctl --flush
sudo cp /var/log/journal/ /evidence/journal/ -r

# Filtres
journalctl -u sshd.service                  # SSH uniquement
journalctl -u apache2.service               # Apache
journalctl _PID=1234                        # Process spécifique
journalctl _COMM=sshd                       # Commande spécifique
journalctl -p err                           # Priorité erreur

# Analyser avec Plaso
log2timeline.py --storage-file case.plaso /evidence/journal/
```

### Logs Textes Linux

```bash
# Logs standards (textes)
/var/log/
├── auth.log        # Authentifications
├── syslog          # Syslog général
├── kern.log        # Noyau
├── dpkg.log        # Paquets installés
├── apt/            # APT
│   ├── history.log
│   └── term.log
├── apache2/        # Apache access/error
├── mysql/           # MySQL
├── nginx/           # Nginx
├── fail2ban.log    # Fail2ban
├── ufw.log         # Firewall UFW
└── samba/          # Samba

# Commandes utiles
grep "Accepted" auth.log | awk '{print $1, $2, $9, $11, $13}' > ssh_logins.txt
grep "Failed password" auth.log | awk '{print $1, $2, $9, $11, $13}' > ssh_failures.txt
zcat auth.log.*.gz | grep "Accepted" >> ssh_logins_old.txt  # Logs compressés

# Bash history
cat ~/.bash_history >> bash_history.txt
# Attention : .bash_history n'est écrit qu'à la fermeture de session
# Mieux : chercher dans la RAM avec Volatility
```

### Linux Timestamps MAC

```bash
# MAC times Linux
# mtime — modification content
# atime — access time (souvent désactivé noatime)
# ctime — changement métadonnées (permissions, owner)

stat /path/to/file
# Résultat :
#   Access: 2024-07-20 10:00:00
#   Modify: 2024-07-20 10:05:00
#   Change: 2024-07-20 10:05:00

# Rechercher fichiers modifiés récemment
find / -mmin -60 -ls                  # Dernière heure
find / -newer /tmp/reference.txt -ls  # Après un événement
find / -not -atime -7                 # Non accédé depuis 7 jours
```

---

## 6. Super Timeline avec Plaso — Workflow Complet

```bash
#!/bin/bash
# plaso_timeline.sh — Super Timeline automatisée

EVIDENCE="$1"
OUTDIR="/evidence/timeline_$(date +%Y%m%d)"
mkdir -p "$OUTDIR"

STORAGE="$OUTDIR/case.plaso"
CSV="$OUTDIR/timeline_full.csv"

echo "=== PLAZO SUPER TIMELINE ==="
echo "Source: $EVIDENCE"

# 1. Créer la timeline
echo "[1] Creating storage..."
log2timeline.py --storage-file "$STORAGE" "$EVIDENCE" --status-view window

# 2. Résumé
echo "[2] Summary..."
pinfo.py "$STORAGE" > "$OUTDIR/summary.txt"

# 3. Export complet
echo "[3] Exporting full timeline..."
psort.py -o l2tcsv -w "$CSV" "$STORAGE"

# 4. Timeline filtrée — fenêtre temporelle suspecte
echo "[4] Filtered timelines..."
psort.py -o l2tcsv -w "$OUTDIR/timeline_suspicious_7d.csv" "$STORAGE" \
   --slice '2024-07-15' '2024-07-22'

# 5. Événements spécifiques
echo "[5] Specific events..."
psort.py -o l2tcsv -w "$OUTDIR/timeline_evtx.csv" "$STORAGE" \
   --query 'data_type is "windows:evtx:record"'

psort.py -o l2tcsv -w "$OUTDIR/timeline_mft.csv" "$STORAGE" \
   --query 'data_type is "fs:stat" or data_type is "fs:mft_entry"'

psort.py -o l2tcsv -w "$OUTDIR/timeline_web.csv" "$STORAGE" \
   --query 'data_type contains "webhist" or data_type contains "cookie"'

# 6. Timeline pour Timeline Explorer
echo "[6] Exporting for Timeline Explorer..."
# TimelineExplorer (EZ Tools) lit les CSV Plaso
cp "$CSV" "$OUTDIR/timeline_explorer.csv"

# 7. Stats
echo "[7] Statistics..."
psort.py -o l2tcsv -w "$OUTDIR/timeline_stats.csv" "$STORAGE" \
   --query 'data_type is "fs:stat"'

echo ""
echo "=== DONE ==="
echo "Output: $OUTDIR"
```

---

## 7. USN Journal

### Structure USN Journal

```txt
Le USN Journal (Update Sequence Number) enregistre TOUS les changements
sur un volume NTFS. Plus granulaire que MFT.

Format (FSCTL_READ_USN_JOURNAL) :
- USN : numéro de séquence
- Timestamp : date du changement
- Reason : MASQUES DE CAUSE
  - 0x01 : USN_REASON_DATA_OVERWRITE
  - 0x02 : USN_REASON_DATA_EXTEND
  - 0x04 : USN_REASON_DATA_TRUNCATION
  - 0x10 : USN_REASON_NAMED_DATA_EXTEND
  - 0x20 : USN_REASON_NAMED_DATA_TRUNCATION
  - 0x40 : USN_REASON_FILE_CREATE
  - 0x80 : USN_REASON_FILE_DELETE
  - 0x100 : USN_REASON_EA_CHANGE
  - 0x200 : USN_REASON_SECURITY_CHANGE
  - 0x400 : USN_REASON_RENAME_OLD_NAME
  - 0x800 : USN_REASON_RENAME_NEW_NAME
  - 0x1000 : USN_REASON_INDEXABLE_CHANGE
  - 0x2000 : USN_REASON_BASIC_INFO_CHANGE
  - 0x4000 : USN_REASON_HARD_LINK_CHANGE
  - 0x8000 : USN_REASON_COMPRESSION_CHANGE
  - 0x10000 : USN_REASON_ENCRYPTION_CHANGE
  - 0x20000 : USN_REASON_OBJECT_ID_CHANGE
  - 0x40000 : USN_REASON_REPARSE_POINT_CHANGE
  - 0x80000 : USN_REASON_STREAM_CHANGE
  - 0x100000 : USN_REASON_CLOSE
```

### Extraction USN

```bash
# Windows natif
fsutil usn readdata C: > usn_journal.txt

# Avec MFTECmd (EZ Tools)
MFTECmd.exe -f "C:\$Extend\$UsnJrnl\$J" --csv usn_output.csv
# Filtre par date
MFTECmd.exe -f "C:\$Extend\$UsnJrnl\$J" --csv usn.csv --de 2024-07-20

# Depuis la mémoire (Volatility)
vol -f memory.raw windows.mftparser > mft_with_usn.txt
```

---

## 8. Corrélation d'Événements

### Reconstruction de Scénario

```txt
EXEMPLE : Infection par malware
═══════════════════════════════════════

Étape 1 : Téléchargement
  10:00:00 — Web history : visite de malicious-site.com/malware.exe
  10:00:01 — Event 5156 : connexion sortante vers 185.x.x.x:443
  10:00:02 — Chrome.download complété → fichier téléchargé dans Downloads

Étape 2 : Exécution
  10:00:05 — ShimCache : malware.exe apparaît
  10:00:05 — Prefetch : malware.exe créé
  10:00:05 — Event 4688 : cmd.exe /c .\malware.exe
  10:00:06 — UserAssist : compteur +1 pour malware.exe

Étape 3 : Installation
  10:00:10 — Registry : Run key ajoutée
  10:00:12 — Event 4698 : tâche planifiée créée
  10:00:15 — Event 7045 : service installé (si persistant)

Étape 4 : C2 Communication
  10:00:20 — Event 5156 : connexion sortante vers C2:4443
  10:00:20 — DNS query pour evil-c2.com
  10:00:45 — Event 4624 : logon suspect (tokens volés ?)

Étape 5 : Effacement des traces
  10:05:00 — MFT : malware.exe marqué supprimé
  10:05:05 — Event 1102 : Security log effacé !
  10:05:10 — USN : $UsnJrnl modifié (effacement de traces)
```

### Technique du "Time Gap"

```txt
Un "time gap" (trou temporel) est suspect :
- Période sans événements : logs effacés, système éteint
- Jump dans la timeline : heure système modifiée
- Désynchronisation : heures entre 2 sources différentes

DÉTECTION :
- Calculer l'intervalle moyen entre événements
- Marquer les gaps > 3× l'intervalle moyen
- Vérifier Windows Event Log 4616 (system time change)
```

---

## 9. Timeline Explorer (EZ Zimmerman)

```bash
# TimelineExplorer — Visualisation des timelines CSV
# Téléchargement : https://ericzimmerman.github.io

# Usage :
TimelineExplorer.exe /evidence/timeline.csv
# Interface :
# - Filtre par date (calendar)
# - Filtre par type d'event
# - Recherche par mots-clés
# - Tags et bookmarks
# - Export en HTML / CSV

# Fonctionnalités clés :
# - Group by : minute, heure, jour
# - Description tooltips
# - Color coding par type
# - Highlight des périodes suspectes
```

---

## 10. Script d'Analyse de Timeline

```python
#!/usr/bin/env python3
"""analyze_timeline.py — Analyse rapide de timeline CSV"""

import csv
import sys
from collections import Counter
from datetime import datetime, timedelta

def analyze_timeline(csv_file):
    events = []
    
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    
    print(f"Analyse de {len(events)} événements\n")
    
    # Top 10 types d'événements
    types = Counter(e.get('data_type', 'unknown') for e in events)
    print("TOP 10 EVENT TYPES:")
    for t, count in types.most_common(10):
        print(f"  {t}: {count}")
    
    # Fenêtre temporelle
    timestamps = [e['datetime'] for e in events if 'datetime' in e]
    if timestamps:
        print(f"\nPÉRIODE: {min(timestamps)} à {max(timestamps)}")
    
    # Événements suspects
    print("\nÉVÉNEMENTS SUSPECTS:")
    for e in events:
        desc = e.get('description', '').lower()
        if any(kw in desc for kw in ['malware', 'virus', 'backdoor', 'delete', 'anomaly']):
            print(f"  [{e.get('datetime','?')}] {e.get('description','?')}")
    
    # Fichiers supprimés
    print("\nFICHIERS SUPPRIMÉS:")
    for e in events:
        if 'delete' in e.get('data_type', '').lower():
            print(f"  [{e.get('datetime','?')}] {e.get('filename','?')}")

if __name__ == '__main__':
    analyze_timeline(sys.argv[1])
```

---

## 11. Dépannage

```bash
PROBLÈME : Plaso out of memory
SOLUTION : 
   - Utiliser --worker-memory-limit 2048
   - Désactiver le hash (--no-hash)
   - Traiter partition par partition

PROBLÈME : Timeline trop grande (>1M events)
SOLUTION :
   - Filtrer par timestamp (--slice)
   - Exporter en JSON (plus compact)
   - Utiliser TimelineExplorer (gère les grands fichiers)

PROBLÈME : Timestamps inconsistent (UTC vs local)
SOLUTION :
   - Plaso stocke en UTC
   - Définir le fuseau à l'export avec --timezone
   - Vérifier le fuseau du système source

PROBLÈME : Événements manquants
SOLUTION :
   - Le log a été effacé (Event 1102)
   - Volume Shadow Copy peut contenir des versions passées
   - Utiliser --vss-stores all dans Plaso
```

---

## 12. Ressources

- **Plaso (log2timeline)** : https://github.com/log2timeline/plaso
- **EZ Tools (Zimmerman)** : https://ericzimmerman.github.io
- **TimelineExplorer** : https://ericzimmerman.github.io
- **MFTECmd** : https://ericzimmerman.github.io
- **analyzeMFT** : https://github.com/dkovar/analyzeMFT
- **SANS SIFT** : https://www.sans.org/tools/sift-workstation/
- **Event Log Explorer** : https://eventlogxp.com/