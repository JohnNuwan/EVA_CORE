---
name: forensics
description: Guide complet d'analyse forensique — Volatility, Autopsy, FTK Imager, binwalk, foremost, exiftool, dd, analyse mémoire, analyse disque, carver de fichiers, et investigation numérique.
---

# Analyse Forensique Numérique — Guide Complet

---

## 1. Volatility — Analyse mémoire (RAM)

### Déterminer le profil
```bash
# Volatility 2
volatility -f memory.dmp imageinfo
volatility -f memory.dmp --profile=Win10x64_18362 pslist

# Volatility 3 (plus récent)
vol -f memory.dmp windows.info
vol -f memory.dmp windows.pslist
```

### Commandes Volatility 3 essentielles

#### Processus
```bash
vol -f memory.dmp windows.pslist           # Liste des processus
vol -f memory.dmp windows.pstree           # Arbre des processus
vol -f memory.dmp windows.cmdline          # Lignes de commande
vol -f memory.dmp windows.dlllist --pid=X  # DLLs d'un processus
vol -f memory.dmp windows.malfind          # Détection code injecté
```

#### Analyse réseau
```bash
vol -f memory.dmp windows.netscan          # Connexions réseau
vol -f memory.dmp windows.netstat          # Netstat
```

#### Credentials
```bash
vol -f memory.dmp windows.hashdump         # Extraire les hashes NTLM
vol -f memory.dmp windows.lsadump          # LSA secrets
vol -f memory.dmp windows.registry.hivelist  # Ruches registre
```

#### Fichiers
```bash
vol -f memory.dmp windows.filescan         # Fichiers ouverts
vol -f memory.dmp windows.dumpfiles --pid X  # Extraire fichiers
vol -f memory.dmp windows.memmap --pid X --dump  # Dump processus
```

### Volatility 2 (legacy)
```bash
volatility -f memory.dmp --profile=Win7SP1x64 psxview
volatility -f memory.dmp --profile=Win7SP1x64 consoles   # Historique cmd
volatility -f memory.dmp --profile=Win7SP1x64 timeliner   # Timeline
volatility -f memory.dmp --profile=Win7SP1x64 iehistory   # IE historique
```

---

## 2. Autopsy — Analyse de disque

### Workflow
```
1. New Case → nom du cas
2. Add Data Source → Disk Image or VM File
3. Modules : Recent Activity, File Type Detection, Hash Lookup
4. Explorer : File Views → voir tous les fichiers
5. Keyword Search → rechercher des termes
6. Timeline → chronologie des événements
```

### Fonctionnalités clés
- **File Types** → Filtre par type MIME
- **Deleted Files** → Fichiers supprimés récupérables
- **Web History** → Navigateurs (Chrome, Firefox, Edge)
- **Email** → PST, MBOX
- **EXIF** → Métadonnées images
- **Hash sets** → Comparaison avec bases de hash connues

---

## 3. FTK Imager — Imagerie forensique

### Créer une image disque
```bash
# Linux (via wine ou VM Windows)
# FTK Imager → File → Create Disk Image
# Formats : E01 (forensic), DD (raw), AFF

# Équivalent Linux
dd if=/dev/sda of=/mnt/image.dd bs=4M status=progress
dcfldd if=/dev/sda of=/mnt/image.dd hash=sha256 hashlog=hash.txt

# Image format E01 (forensic) - via guymager (GUI) ou ewfacquire
ewfacquire /dev/sda
```

---

## 4. Carving — Extraction de fichiers

### Foremost
```bash
# Extraire tous les types de fichiers
foremost -i image.dd -o /sortie/
foremost -t jpg,png,doc,pdf,exe -i image.dd -o /sortie/
```

### Binwalk — Analyse de firmware
```bash
binwalk firmware.bin                        # Scanner
binwalk -e firmware.bin                     # Extraire
binwalk -Me firmware.bin                    # Extraire récursivement
binwalk -A firmware.bin                     # Détecter instructions CPU
binwalk -E firmware.bin                     # Entropie (sections compressées)
```

### Scalpel
```bash
# Modifier /etc/scalpel/scalpel.conf (décommenter les types)
scalpel -o /sortie/ image.dd
```

### Photorec (récupération de fichiers supprimés)
```bash
photorec image.dd
# Interface interactive : sélectionner partition, type de fichier, destination
```

---

## 5. Analyse de fichiers

### Métadonnées
```bash
exiftool document.docx
exiftool image.jpg
exiftool -gps* image.jpg       # Données GPS
exiftool -a -u image.jpg        # Toutes les métadonnées
```

### Analyse de PDF
```bash
pdfinfo document.pdf            # Infos
pdfid.py document.pdf           # Détecter éléments suspects (/JS, /OpenAction)
pdf-parser.py -s /OpenAction document.pdf  # Analyser un objet spécifique
peepdf document.pdf             # Analyse interactive
```

### Analyse de documents Office
```bash
# Oletools
oleid document.docm             # Détecter macros
olevba document.docm            # Extraire et analyser les macros VBA
mraptor document.docm           # Détection heuristique de malveillance
```

### Analyse d'exécutables
```bash
# Fingerprinting
file malware.exe
strings malware.exe | less
objdump -d malware.exe

# Signatures
md5sum malware.exe
sha256sum malware.exe

# YARA — détection par patterns
yara -r rules.yar /dossier/analyse/
```

---

## 6. Hash et intégrité

```bash
# Calculer des hash
md5sum fichier
sha1sum fichier
sha256sum fichier
sha512sum fichier

# Vérifier l'intégrité
sha256sum -c checksums.txt

# Comparer avec bases de hash
# NSRL (National Software Reference Library)
# VirusTotal API
```

---

## 7. Timeline — Reconstruction chronologique

```bash
# Linux
stat fichier                    # Timestamps (access, modify, change)
find / -newer reference.txt     # Fichiers modifiés après une date
ls -la --time=atime             # Tri par temps d'accès

# Logs
cat /var/log/auth.log | grep "Accepted"
cat /var/log/syslog
journalctl

# Autopsy : Timeline view
# Plaso/log2timeline (CLI) :
log2timeline.py timeline.plaso image.dd
psort.py timeline.plaso -o l2tcsv -w timeline.csv
```

---

## 8. Outils réseau

### Capture et analyse
```bash
# tcpdump
tcpdump -i eth0 -w capture.pcap
tcpdump -r capture.pcap -nn

# Tshark
tshark -r capture.pcap -Y "http"
tshark -r capture.pcap -z http,tree

# NetworkMiner (GUI, Windows) — Reconstruction de fichiers et sessions
```

---

## 9. Analyse de registre Windows

```bash
# Outils Linux pour analyser le registre Windows
# registry-tools :
reglookup -p /chemin/vers/SOFTWARE
reglookup-recover /chemin/vers/ruche

# Clés intéressantes
# NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Run
# NTUSER.DAT\Software\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs
# SYSTEM\CurrentControlSet\Services
```

### Eric Zimmerman Tools (Windows)
```
Registry Explorer  →  Analyser les ruches registre
ShellBags Explorer →  Analyser l'historique des dossiers
Timeline Explorer  →  Visualiser une timeline
```

---

## 10. Cheatsheet forensique rapide

```bash
# 1. Créer une image disque
dd if=/dev/sda of=image.dd bs=4M status=progress

# 2. Analyser la mémoire (RAM)
vol -f memory.dmp windows.pslist
vol -f memory.dmp windows.netscan
vol -f memory.dmp windows.malfind

# 3. Analyser le disque
# Autopsy (GUI) : File → New Case → Add Data Source

# 4. Extraire les fichiers
foremost -i image.dd -o /sortie/
binwalk -Me firmware.bin

# 5. Analyser les métadonnées
exiftool image.jpg
olevba document.docm
strings malware.exe | less

# 6. Chronologie
find / -newer reference.txt
log2timeline.py timeline.plaso image.dd
```

### Ressources
- **Volatility** : https://volatilityfoundation.org
- **Autopsy** : https://www.autopsy.com
- **SIFT Workstation** : https://www.sans.org/tools/sift-workstation/
- **dfir.training** : Ressources DFIR gratuites
- **Eric Zimmerman Tools** : https://ericzimmerman.github.io