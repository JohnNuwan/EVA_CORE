---
name: nmap-avance
description: Nmap avancé — scans furtifs, NSE scripts, évasion firewall, détection OS/service, timing, formats de sortie, automatisation, et scénarios de pentest complets.
---

# Nmap Avancé — Guide Pentest

## Présentation

Nmap (Network Mapper) est le scanner de réseau de référence. Ce skill couvre les techniques avancées au-delà du scan de base.

**Installation** :
```bash
sudo apt install nmap
# Dernière version
git clone https://github.com/nmap/nmap.git && cd nmap && ./configure && make && sudo make install
```

---

## Types de scans avancés

### Scan SYN (furtif) — `-sS`
```bash
# Ne complète pas la poignée de main TCP — ne laisse pas de log applicatif
nmap -sS -p 1-65535 192.168.1.1
```

### Scan TCP Connect — `-sT`
```bash
# Complète la poignée de main — bruyant mais sans root
nmap -sT -p 80,443,8080 192.168.1.1
```

### Scan UDP — `-sU`
```bash
# Très lent — combiner avec --max-rtt-timeout et --min-hostgroup
nmap -sU --top-ports 100 192.168.1.1
```

### Scan FIN/Null/Xmas — évasion firewall
```bash
nmap -sF 192.168.1.1          # FIN scan (paquet FIN)
nmap -sN 192.168.1.1          # Null scan (aucun flag)
nmap -sX 192.168.1.1          # Xmas scan (FIN+PSH+URG)
```

### Scan ACK — cartographie des règles de firewall
```bash
nmap -sA 192.168.1.1          # Détermine si un port est filtré (stateless)
nmap -sW 192.168.1.1          # Window scan
```

### Scan SCTP — `-sY`
```bash
nmap -sY 192.168.1.1          # Stream Control Transmission Protocol
```

### Scan IP Protocol — `-sO`
```bash
nmap -sO 192.168.1.1          # Quels protocoles IP sont supportés (TCP, UDP, ICMP...)
```

---

## Détection OS — `-O`

### Détection OS agressive
```bash
nmap -O --osscan-guess 192.168.1.1     # Deviner même si non correspondance exacte
nmap -O --fuzzy 192.168.1.1            # Fuzzy matching
nmap -O --max-os-tries 3 192.168.1.1   # Plus de tentatives
```

### Limiter la détection OS
```bash
nmap -O --osscan-limit 192.168.1.0/24  # OS scan seulement si hôte UP
```

---

## Détection de versions — `-sV`

### Intensité de version (0-9)
```bash
nmap -sV --version-intensity 9 192.168.1.1  # Max (lent mais complet)
nmap -sV --version-intensity 2 192.168.1.1  # Rapide (services communs)
nmap -sV --version-light 192.168.1.1         # = --version-intensity 2
nmap -sV --version-all 192.168.1.1           # = --version-intensity 9
```

### Banner grabbing
```bash
nmap -sV --script=banner 192.168.1.1
# Alternative : nc -w 2 192.168.1.1 80 | strings
```

---

## NSE — Nmap Scripting Engine

### Catégories de scripts
```bash
# Lister toutes les catégories
nmap --script-help all | grep -i "^Category"

# Catégories principales
nmap --script=auth 192.168.1.1           # Vérification d'authentification
nmap --script=brute 192.168.1.1          # Bruteforce (services)
nmap --script=default 192.168.1.1        # = -sC
nmap --script=discovery 192.168.1.1      # Découverte d'informations
nmap --script=dos 192.168.1.1            # Test DoS (attention !)
nmap --script=exploit 192.168.1.1        # Exploitation (attention !)
nmap --script=external 192.168.1.1       # Requêtes externes (DNS, WHOIS)
nmap --script=fuzzer 192.168.1.1         # Fuzzing
nmap --script=intrusive 192.168.1.1      # Intrusif (peut crasher le service)
nmap --script=malware 192.168.1.1        # Détection de malware
nmap --script=safe 192.168.1.1           # Non intrusif (sûr)
nmap --script=version 192.168.1.1        # Détection de version
nmap --script=vuln 192.168.1.1           # Détection de vulnérabilités
```

### Exécution de scripts spécifiques
```bash
# Par nom
nmap --script=http-title 192.168.1.1
nmap --script=ssl-heartbleed 192.168.1.1

# Par wildcard
nmap --script=smb* 192.168.1.1           # Tous les scripts SMB
nmap --script=http* 192.168.1.1          # Tous les scripts HTTP

# Plusieurs scripts
nmap --script=http-title,ssl-enum-ciphers,http-headers 192.168.1.1

# Scripts + arguments
nmap --script=http-brute --script-args userdb=users.txt,passdb=rockyou.txt 192.168.1.1
nmap --script=http-sql-injection --script-args=http-sql-injection.path=/login.php 192.168.1.1
```

### Scripts NSE avancés
```bash
# SMB vuln check (EternalBlue etc.)
nmap -p445 --script=smb-vuln-* 192.168.1.1

# Enumération DNS
nmap --script=dns-brute --script-args dns-brute.domain=example.com,dns-brute.threads=10

# Enumération MySQL
nmap -p3306 --script=mysql-* 192.168.1.1

# RDP vuln check (BlueKeep CVE-2019-0708)
nmap -p3389 --script=rdp-vuln-ms12-020 192.168.1.1

# VNC brute + auth bypass
nmap -p5900 --script=vnc-* 192.168.1.1

# FTP anon + bounce
nmap -p21 --script=ftp-* 192.168.1.1

# HTTP enumeration
nmap -p80,443 --script=http-enum,http-webdav-scanenums,http-shellshock 192.168.1.1
```

### Créer un script NSE personnalisé
```lua
-- ~/.nmap/scripts/http-test.nse
description = [[Test personnalisé HTTP]]
author = "EVA"
categories = {"safe", "discovery"}

local http = require "http"
local shortport = require "shortport"

portrule = shortport.http

action = function(host, port)
  local response = http.get(host, port, "/")
  if response and response.body then
    if response.body:match("admin") then
      return "[ALERTE] Page admin détectée !"
    end
  end
  return nil
end
```

---

## Évasion de pare-feu / IDS

### Fragmentation
```bash
nmap -f 192.168.1.1                     # Fragmenter en paquets de 8 octets
nmap --mtu 16 192.168.1.1               # MTU personnalisé (multiple de 8)
nmap -f -f 192.168.1.1                  # Double fragmentation
```

### Leurres (Decoys)
```bash
nmap -D RND:10 192.168.1.1              # 10 IPs aléatoires
nmap -D 10.0.0.1,192.168.1.5,8.8.8.8 192.168.1.1  # IPs spécifiques
nmap -D decoy1.com,decoy2.com 192.168.1.1           # Noms de domaine
```

### Usurpation d'adresse source
```bash
nmap -S 10.0.0.1 192.168.1.1            # IP source falsifiée
nmap -e eth0 -S 10.0.0.1 192.168.1.1    # Forcer l'interface
```

### Port source
```bash
nmap --source-port 53 192.168.1.1        # DNS (souvent autorisé)
nmap --source-port 20 192.168.1.1        # FTP data (parfois autorisé)
```

### Timing
```bash
nmap -T0 192.168.1.1           # Paranoïd (très lent, contourne IDS)
nmap -T1 192.168.1.1           # Sneaky
nmap -T2 192.168.1.1           # Polite
nmap -T3 192.168.1.1           # Normal (défaut)
nmap -T4 192.168.1.1           # Aggressive
nmap -T5 192.268.1.1           # Insane (bruyant, perte de précision)
```

### Délais personnalisés
```bash
nmap --scan-delay 1s 192.168.1.1        # Attendre 1s entre chaque paquet
nmap --max-scan-delay 5s 192.168.1.1    # Délai max
nmap --min-rtt-timeout 100ms 192.168.1.1
nmap --max-rtt-timeout 1000ms 192.168.1.1
nmap --min-parallelism 1 192.168.1.1    # Forcer un seul scan à la fois
nmap --max-parallelism 1 192.168.1.1    # Pas de parallélisme
```

### Évasion avancée
```bash
nmap --data-length 50 192.168.1.1       # Ajouter des données aléatoires
nmap --ip-options "L" 192.168.1.1       # Options IP (L=loose routing)
nmap --ttl 128 192.168.1.1              # TTL personnalisé
nmap --badsum 192.168.1.1               # Checksum invalide (contourne certains firewalls)
nmap --spoof-mac Dell 192.168.1.1       # MAC spoofing
nmap --proxies http://proxy:8080,http://proxy2:8080 192.168.1.1  # Via proxy HTTP
```

---

## Formats de sortie et parsing

### Tous les formats
```bash
nmap -oA mon_scan 192.168.1.1           # .nmap + .gnmap + .xml
nmap -oN scan.nmap 192.168.1.1          # Normal (lisible)
nmap -oX scan.xml 192.168.1.1           # XML (parsable)
nmap -oG scan.gnmap 192.168.1.1         # Grepable (grep-friendly)
nmap -oS scan.txt 192.168.1.1           # Script kiddie (style l33t)
nmap -oH scan.html 192.168.1.1          # HTML (--stylesheet optionnel)
```

### Parsing XML
```bash
# Extraire les IPs avec port 80 ouvert
grep "portid=\"80\"" scan.xml | grep -oP 'address addr="\K[^"]+'

# Avec xmlstarlet
xmlstarlet sel -t -v "//address/@addr" -n scan.xml

# Avec python
python3 -c "
import xml.etree.ElementTree as ET
root = ET.parse('scan.xml')
for host in root.findall('.//host'):
    addr = host.find('address').get('addr')
    ports = host.findall('.//port')
    for p in ports:
        state = p.find('state').get('state')
        if state == 'open':
            print(f'{addr}:{p.get(\"portid\")}/{p.get(\"protocol\")}')
"

# Avec xsltproc (tableau HTML)
xsltproc /usr/share/nmap/nmap.xsl scan.xml -o scan.html
```

---

## Optimisation de performance

### Contrôle du parallélisme
```bash
nmap --min-hostgroup 64 192.168.1.0/24    # Minimum d'hôtes en parallèle
nmap --max-hostgroup 256 192.168.1.0/24   # Maximum
nmap --min-parallelism 10 192.168.1.0/24  # Minimum de sondes parallèles
nmap --max-parallelism 100 192.168.1.0/24 # Maximum
```

### Contrôle du timing RTT
```bash
nmap --initial-rtt-timeout 100ms 192.168.1.0/24
nmap --min-rtt-timeout 50ms 192.168.1.0/24
nmap --max-rtt-timeout 500ms 192.168.1.0/24
```

### Accélération des scans
```bash
# Scan TOP 1000 ports + versions → 30 secondes
nmap -T4 -sV --top-ports 1000 192.168.1.1

# Scan rapide de /24
nmap -T5 -sn 192.168.1.0/24              # Ping sweep (30 secondes)

# Scan complet avec exclusion
nmap -p- -T4 --exclude 192.168.1.1,192.168.1.254 192.168.1.0/24

# Scan de masse (plusieurs /24)
nmap -sn -T5 -iL subnets.txt
```

---

## Scénarios de pentest

### 1. Reconnaissance initiale complète
```bash
nmap -sS -sV -sC -O -p- -T4 -oA full_scan 192.168.1.1
# -sS: SYN stealth
# -sV: versions
# -sC: scripts par défaut
# -O: OS detection
# -p-: tous les ports
# -T4: timing agressif
# -oA: tous les formats
```

### 2. Scan web ciblé (OWASP Top 10)
```bash
nmap -p80,443,8080,8443 --script=http-* \
     --script-args http-enum.basepath=/uploads/ \
     -oA web_scan 192.168.1.1
```

### 3. Scan vulnérabilités critiques
```bash
nmap -p- --script vuln --script-args unsafely=1 -T4 -oA vuln_scan 192.168.1.1
```

### 4. Scan furtif (contournement IDS)
```bash
nmap -sS -T2 -f --ttl 64 --data-length 30 \
     --source-port 53 -D RND:5 \
     -p 22,80,443,445,3389 \
     -oA stealth_scan 192.168.1.1
```

### 5. Énumération Active Directory
```bash
nmap -p 53,88,135,139,389,445,464,593,636,3268,3269,3389 \
     -sC -sV -T4 -oA ad_scan 192.168.1.0/24
```

### 6. Scan IoT / industriel
```bash
nmap -sT -Pn -p 80,443,161,502,102,20000,44818,4840 \
     --script=modbus-*,enip-*,s7-*,bacnet-*,iec-* \
     -oA iot_scan 10.0.0.0/24
```

### 7. Scan externe (depuis internet)
```bash
nmap -sS -Pn -n --top-ports 1000 \
     --script http-title,ssl-enum-ciphers,whois* \
     -oA external_scan example.com
```

### 8. Scan avec résilience réseau
```bash
# Scan avec retry et timeouts adaptés
nmap -sS --max-retries 5 --max-rtt-timeout 2000ms \
     --min-rtt-timeout 100ms --host-timeout 30m \
     -p- -T3 -oA resilient_scan 192.168.1.1
```

---

## Automatisation

### Boucle Bash
```bash
#!/bin/bash
for ip in $(seq 1 254); do
    nmap -sS -p80,443,22 -T4 -oG - 192.168.1.$ip | grep "open"
done
```

### Parallel avec xargs
```bash
seq 1 254 | xargs -P10 -I{} nmap -sS -p80 --open -T4 -oG - 192.168.1.{} | grep "open"
```

### Utilisation avec Masscan + Nmap
```bash
# Phase 1 : masscan rapide pour découvrir les ports ouverts
masscan -p1-65535 192.168.1.0/24 --rate=1000 -oJ masscan.json

# Phase 2 : nmap détaillé sur les ports découverts
masscan --readscan masscan.json | awk '{print $4, $6}' > ports.txt
while read ip port; do
    nmap -sV -sC -p$port $ip -oA "scan_${ip}_${port}"
done < ports.txt
```

---

## Scripts NSE custom — exemples

### Détection de logiciel personnalisé
```lua
-- http-software-detect.nse
local http = require "http"
local shortport = require "shortport"

description = "Détection de logiciels personnalisés"
author = "EVA"
categories = {"safe", "discovery"}

portrule = shortport.http

action = function(host, port)
  local paths = {"/version", "/api/status", "/health", "/info", "/server-status", "/.env"}
  local results = {}
  for _, path in ipairs(paths) do
    local resp = http.get(host, port, path)
    if resp and resp.status == 200 then
      table.insert(results, path)
    end
  end
  if #results > 0 then
    return "Chemins exposés : " .. table.concat(results, ", ")
  end
end
```

---

## Antisèche rapide

```bash
# Scan complet standard
nmap -sS -sV -sC -O -p- -T4 -oA scan 192.168.1.1

# Ping sweep /24
nmap -sn 192.168.1.0/24

# Scan rapide TOP 1000
nmap -T4 --top-ports 1000 192.168.1.1

# Scan vulnérabilités
nmap -p- --script vuln 192.168.1.1

# Scan furtif
nmap -sS -T2 -f --source-port 53 -D RND:5 192.168.1.1

# Web enumeration
nmap -p80,443 --script=http-* 192.168.1.1

# SMB enumeration
nmap -p445 --script=smb-* 192.168.1.1

# Scan UDP (TOP 100)
nmap -sU --top-ports 100 192.168.1.1

# Live hosts only
nmap -sS -Pn -oA scan 192.168.1.1

# Exclure des hôtes
nmap --exclude 192.168.1.1,192.168.1.254 192.168.1.0/24

# Depuis une liste
nmap -iL targets.txt -oA batch_scan
```