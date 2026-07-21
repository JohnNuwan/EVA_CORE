---
name: wireshark-avance
description: Wireshark avancé — filtres d'affichage complexes, statistiques réseau, analyse de protocoles (SMB, Kerberos, TLS), déchiffrement, extraction d'objets, analyse de malware, scripts Lua, tshark automatisé, et scénarios forensiques.
---

# Wireshark Avancé — Analyse Réseau Approfondie

## Complément au skill wireshark de base

Ce skill couvre les techniques avancées au-delà de l'utilisation courante : forensique réseau, analyse de malware, scripts Lua, déchiffrement TLS, et statistiques approfondies.

---

## Filtres d'affichage avancés

### Filtres booléens complexes
```bash
# Combinaisons logiques
ip.src==192.168.1.1 and tcp.port==80
http and (ip.src==10.0.0.1 or ip.dst==10.0.0.1)
!(arp or dns or icmp)
tcp and not (ip.addr==192.168.1.0/24)
```

### Expressions régulières dans les filtres
```bash
# http.host contient "admin"
http.host matches "admin"

# DNS query contient un pattern hex long (exfil)
dns.qry.name matches "[a-z0-9]{50,}\.(com|org|xyz)"

# HTTP URI avec pattern spécifique
http.request.uri matches "(admin|config|backup|\.env)"

# Recherche de shellcode dans le payload
tcp.payload matches "(wget|curl|bash|cmd|powershell)"

# User-Agent suspects
http.user_agent matches "(curl|python-requests|Go-http)"
```

### Filtres par champ présent/absent
```bash
# Paquets avec un champ spécifique
http.request          # Toutes les requêtes HTTP
tcp.flags.syn         # Paquets SYN
!_ws.expert           # Paquets sans alerte expert (bruit réduit)
```

### Filtres temporels
```bash
# Temps absolu
frame.time >= "Jan 1, 2024 00:00:00" and frame.time <= "Jan 2, 2024 23:59:59"

# Delta time (temps depuis le paquet précédent)
frame.time_delta > 1          # Plus d'une seconde d'écart
frame.time_delta_displayed > 5  # Dans l'affichage
```

### Filtres par taille
```bash
frame.len > 1500              # Paquets > MTU standard
frame.len < 64                # Paquets trop petits
tcp.len > 0                   # Paquets avec données
http.content_length > 10000   # Grosses réponses HTTP
```

### Filtres d'exclusion
```bash
# Exclure le bruit
!(arp or dns or icmpv6 or dhcp or dhcpv6 or mdns or llmnr or nbns or ssdp)
# Équivalent à "No broadcast/std protocols"

# Exclure les broadcast
not eth.dst == ff:ff:ff:ff:ff:ff

# Exclure le trafic local
not (ip.src==192.168.1.0/24 and ip.dst==192.168.1.0/24)
```

---

## Analyse SMB/CIFS

```bash
# Filtrer SMB
smb
smb2                           # SMB v2/v3
nbns                           # NetBIOS name service

# Commandes SMB
smb2.cmd == 0x00              # Negotiate protocol
smb2.cmd == 0x01              # Session setup
smb2.cmd == 0x02              # Session logout
smb2.cmd == 0x03              # Tree connect
smb2.cmd == 0x04              # Tree disconnect
smb2.cmd == 0x05              # Create
smb2.cmd == 0x06              # Close
smb2.cmd == 0x07              # Flush
smb2.cmd == 0x08              # Read
smb2.cmd == 0x09              # Write
smb2.cmd == 0x0E              # IOCTL
smb2.cmd == 0x10              # Set info

# Fichiers accédés
smb2.filename contains ".docx"
smb2.filename contains "password"
smb2.filename contains "confidential"

# Énumération des sessions SMB
nbns.name_type == 0x20        # Server name
nbdgm                           # NetBIOS datagram

# Exploitation
smb.nt_status == 0xC0000022   # STATUS_ACCESS_DENIED
smb.nt_status == 0x00000000   # STATUS_SUCCESS

# Détecter SMB relay
smb2 and ntlmssp
```

---

## Analyse Kerberos

```bash
# Filtrer Kerberos
kerberos
krb5                           # Version 5

# Types de messages
kerberos.msg_type == 10       # AS-REQ (Authentication request)
kerberos.msg_type == 11       # AS-REP (Authentication reply) 
kerberos.msg_type == 12       # TGS-REQ (Ticket request)
kerberos.msg_type == 13       # TGS-REP (Ticket reply)
kerberos.msg_type == 14       # AP-REQ (Application request)
kerberos.msg_type == 15       # AP-REP (Application reply)

# Kerberoasting detection
kerberos.msg_type == 13 and kerberos.cname contains "service" or kerberos.cname contains "svc_"

# AS-REP roasting
kerberos.msg_type == 11 and kerberos.error_code == 0

# Golden ticket / forged PAC
kerberos.pac                     # PAC present
kerberos.pac_type == 2           # PAC_LOGON_INFO

# Encryption type
kerberos.etype == 23            # RC4-HMAC (kerberoastable)
kerberos.etype == 17            # AES128
kerberos.etype == 18            # AES256

# Ticket brute-force
kerberos.etype == 23 and kerberos.msg_type == 13

# Détection DCSync
kerberos.CNameString contains "192.168"  # Utilisateur inhabituel
kerberos.SNameString contains "krbtgt" and kerberos.msg_type == 13
```

---

## Analyse TLS/SSL

### Filtres TLS
```bash
tls                               # Tout TLS
tls.handshake.type == 1          # Client Hello
tls.handshake.type == 2          # Server Hello
tls.handshake.type == 11         # Certificate
tls.handshake.type == 16         # Encrypted Extensions

# Ciphers
tls.handshake.ciphersuite == 0x1301  # TLS_AES_128_GCM_SHA256 (TLS 1.3)
tls.handshake.ciphersuite == 0x1303  # TLS_CHACHA20_POLY1305_SHA256
tls.handshake.ciphersuite == 0x009F  # AES256-GCM (TLS 1.2)

# ALPN
tls.handshake.extensions_alpn_str contains "h2"    # HTTP/2
tls.handshake.extensions_alpn_str contains "http/1.1"

# SNI (Server Name Indication)
tls.handshake.extensions_server_name contains "admin"
tls.handshake.extensions_server_name contains "internal"

# Certificate info
tls.handshake.certificate
tls.handshake.certificate_issuer
tls.handshake.certificate_subject
tls.handshake.certificate_valid_from
tls.handshake.certificate_valid_to

# Weak SSL/TLS
tls.handshake.version == 0x0300      # SSL 3.0
tls.handshake.version == 0x0301      # TLS 1.0
tls.handshake.version == 0x0302      # TLS 1.1
tls.handshake.version == 0x0303      # TLS 1.2
tls.handshake.version == 0x0304      # TLS 1.3

# Failed handshake
tls.alert_message
tls.handshake.failure
```

### Déchiffrement TLS avec SSLKEYLOGFILE
```bash
# 1. Configurer la capture des clés
export SSLKEYLOGFILE=/tmp/sslkeys.log
# Lancer l'application/le navigateur dans ce terminal

# 2. Dans Wireshark
# Edit → Preferences → Protocols → TLS
# (Pre)-Master-Secret log filename: /tmp/sslkeys.log

# 3. Les flux deviennent lisibles
# Le filtre tls.handshake.type == 1 montre encore les handshakes
# Mais le corps est déchiffré

# Déchiffrer avec tshark
tshark -r capture.pcap -o tls.keylog_file:/tmp/sslkeys.log -Y "http2"
```

### Déchiffrement avec clé privée RSA
```bash
# Configuration
# Edit → Preferences → Protocols → TLS → RSA keys list
# Add → IP:port:protocol:key_file

# Ou en ligne de commande
tshark -r capture.pcap \
    -o "tls.keys_list:10.0.0.5,443,http,/path/server.key" \
    -Y "http"
```

---

## Analyse de malware et C2

### Détection de beaconing
```bash
# Connexions régulières = beacon C2
# 1. Statistiques → IO Graph
#    Filtre : ip.dst == 185.130.5.10
#    Interval : 1 sec → voir les patterns

# 2. Analyse temporelle
frame.time_delta_displayed > 10 and frame.time_delta_displayed < 60

# 3. Requêtes DNS vers domaines suspects
dns.qry.name matches "[a-z0-9]{20,}\.com"
dns.qry.name matches "\.xyz|\.top|\.club|\.gdn"

# 4. HTTP User-Agent suspects
http.user_agent matches "^(curl|wget|python|Go|Mozilla/4\.0)"

# 5. Payload non-HTTP sur port 80
tcp.port==80 and not http

# 6. Trafic vers IPs récentes (nouveau domaine)
# Vérifier l'âge du domaine : whois
!(dns or http) and tcp.dstport==443 and !tls.handshake
```

### Détection d'exfiltration
```bash
# DNS exfiltration
dns.qry.name matches "[a-z0-9]{30,}\.(com|net|org)"

# Tunneling HTTP
http.request and http.content_length > 10000
http.request.uri matches "/(upload|submit|data)"

# ICMP tunneling
icmp and frame.len > 100

# Tunneling DNS (trop de requêtes)
dns and frame.len > 300

# Trafic sortant vers IP inhabituelles
ip.dst != 192.168.0.0/16 and ip.dst != 10.0.0.0/8 and ip.dst != 172.16.0.0/12
```

### Recherche d'IOCs
```bash
# Rechercher des IP connues
ip.addr == 185.130.5.10 or ip.addr == 5.188.62.10

# Rechercher des hash de malwares (dans les téléchargements)
http contains "e1105070ba828007508566e28a2b8d4c"

# Rechercher des patterns de commandes
tcp.payload contains "Invoke-Mimikatz"
tcp.payload contains "cmd.exe /c"
tcp.payload contains "powershell -enc"
tcp.payload contains "wget"
tcp.payload contains "curl -o"

# VBS/JS macro patterns
tcp.payload contains "CreateObject("
tcp.payload contains "WScript.Shell"
tcp.payload contains "ActiveXObject"
tcp.payload contains "ShellExecute"

# Metasploit / Cobalt Strike patterns
tcp.payload contains "Meterpreter"
tcp.payload contains "ReflectiveLoader"
tcp.payload contains "beacon"
```

---

## Extraction d'objets

### CLI avec tshark
```bash
# Extraire tous les fichiers HTTP
tshark -r capture.pcap --export-objects http,/tmp/extracted/

# Extraire les fichiers SMB
tshark -r capture.pcap --export-objects smb,/tmp/extracted/

# Extraire les fichiers SMTP (Pièces jointes)
tshark -r capture.pcap --export-objects smtp,/tmp/extracted/

# Extraire les certificats TLS
tshark -r capture.pcap -Y "tls.handshake.certificate" -T fields \
    -e tls.handshake.certificate > certs.raw
```

### Fichiers extraits — analyse
```bash
# Analyser les fichiers extraits
file /tmp/extracted/* | grep -v "ASCII text"
scp -r /tmp/extracted/ /analyse/

# Calculer les hashs des fichiers extraits
for f in /tmp/extracted/*; do
    echo "$(md5sum $f) $f"
done
```

---

## Statistiques avancées

### Conversations
```bash
# TCP conversations
tshark -r capture.pcap -z conv,tcp
tshark -r capture.pcap -z conv,tcp -o "gui.column.format:\"Src\",\"%us\",\"Dst\",\"%ud\""

# UDP conversations
tshark -r capture.pcap -z conv,udp

# Top talkers
tshark -r capture.pcap -z endpoints,ip
```

### IO Graphs
```bash
# IO Graph avec plusieurs filtres
tshark -r capture.pcap -z io,stat,1,\
    "COUNT(tcp.port==80) http",\
    "COUNT(tcp.port==443) https",\
    "COUNT(dns) dns",\
    "BYTES() total"

# Dans Wireshark GUI :
# Statistics → IO Graph → Filter + color per protocol
```

### Protocol Hierarchy
```bash
# Utilisation des protocoles
tshark -r capture.pcap -z io,phs

# Exemple de sortie :
# Protocol                % Bytes    Packets
# Ethernet                100%       50000
# IP                      95%        47500
# TCP                     80%        40000
# HTTP                    30%        15000
# TLS                     25%        12500
# DNS                     10%        5000
```

### Flow Graph (visualisation de flux)
```bash
# Wireshark → Statistics → Flow Graph
# Affiche les flux TCP de manière temporelle
```

---

## Tshark — Automatisation avancée

### Champs personnalisés
```bash
# Extraire des champs spécifiques vers CSV
tshark -r capture.pcap -T fields \
    -e frame.number \
    -e frame.time \
    -e ip.src \
    -e ip.dst \
    -e tcp.srcport \
    -e tcp.dstport \
    -e tcp.len \
    -e http.request.uri \
    -e http.response.code \
    -e dns.qry.name \
    -E header=y -E separator=, > output.csv
```

### Templates de rapport
```bash
# Rapport texte structuré
tshark -r capture.pcap -z io,stat,1 -z conv,tcp -z endpoints,ip

# Export en JSON
tshark -r capture.pcap -T json > output.json

# Export en PDML (XML détaillé)
tshark -r capture.pcap -T pdml > output.pdml

# Champs pour Elasticsearch
tshark -r capture.pcap -T ek > output.ek
```

### Script d'analyse automatisé
```bash
#!/bin/bash
# analyze_pcap.sh - Script d'analyse complète
PCAP=$1
BASENAME=$(basename $PCAP .pcap)

echo "=== Analyse de $PCAP ==="

# 1. Résumé
echo "--- Résumé ---"
capinfos $PCAP

# 2. Top conversations
echo "--- Top IP conversations ---"
tshark -r $PCAP -z conv,ip | head -20

# 3. Services HTTP
echo "--- Requêtes HTTP ---"
tshark -r $PCAP -Y "http.request" -T fields -e http.host -e http.request.uri | sort -u | head -50

# 4. DNS queries
echo "--- DNS Queries ---"
tshark -r $PCAP -Y "dns.qry.name" -T fields -e dns.qry.name | sort -u | head -50

# 5. Hosts suspects
echo "--- Hosts suspects (DNS lookup) ---"
tshark -r $PCAP -Y "dns.qry.name matches \"[a-z0-9]{30,}\.com\"" -T fields -e dns.qry.name

# 6. Objets HTTP
mkdir -p /tmp/extracted_$BASENAME
tshark -r $PCAP --export-objects http,/tmp/extracted_$BASENAME/
echo "--- Fichiers extraits ---"
ls -la /tmp/extracted_$BASENAME/

# 7. Credentials
echo "--- Credentials potentiels ---"
tshark -r $PCAP -Y "http.request.method==POST" -T fields -e http.file_data | grep -i "password\|user\|login"

echo "=== Analyse terminée ==="
```

---

## Scripts Lua Wireshark

### Dissector personnalisé
```lua
-- myproto.lua — Dissector pour un protocole custom
local myproto = Proto("myproto", "Mon Protocole Personnalisé")

-- Définition des champs
local f_version = ProtoField.uint8("myproto.version", "Version", base.DEC)
local f_type = ProtoField.uint8("myproto.type", "Type", base.HEX)
local f_payload = ProtoField.bytes("myproto.payload", "Payload")
myproto.fields = {f_version, f_type, f_payload}

-- Fonction de dissector
function myproto.dissector(buffer, pinfo, tree)
    if buffer:len() < 2 then return false end
    
    pinfo.cols.protocol = "MYPROTO"
    local subtree = tree:add(myproto, buffer(), "Protocole Custom")
    
    subtree:add(f_version, buffer(0,1))
    subtree:add(f_type, buffer(1,1))
    if buffer:len() > 2 then
        subtree:add(f_payload, buffer(2))
    end
    
    if f_type.value == 0x01 then
        pinfo.cols.info = "Request"
    elseif f_type.value == 0x02 then
        pinfo.cols.info = "Response"
    end
    
    return true
end

-- Enregistrer sur le port TCP 9000
DissectorTable.get("tcp.port"):add(9000, myproto)
```

### Script de détection de malwares
```lua
-- malware_detect.lua
local malware = Proto("malware", "Détection de Malware")

function malware.dissector(buffer, pinfo, tree)
    local has_malware = false
    local info = ""
    
    -- Recherche de patterns
    if buffer:find("Invoke-Mimikatz") then
        has_malware = true
        info = info .. " [MIMIKATZ]"
    end
    
    if buffer:find("powershell -enc") then
        has_malware = true
        info = info .. " [POWERSHELL_ENC]"
    end
    
    if buffer:find("cmd.exe /c") then
        has_malware = true
        info = info .. " [CMD_EXEC]"
    end
    
    if has_malware then
        pinfo.cols.info = pinfo.cols.info .. info
        pinfo.cols.protocol = "MALWARE"
    end
end

-- S'enregistrer sur tous les flux TCP
DissectorTable.get("tcp"):add(0, malware)
```

### Script de suivi de flux personnalisé
```lua
-- follow_stream.lua — suivi de flux amélioré
local follow = Proto("follow", "Suivi de Flux")

function follow.init()
    -- Initialiser les tables de flux
    follow.streams = {}
end

function follow.dissector(buffer, pinfo, tree)
    local stream_id = tostring(pinfo.src) .. "→" .. tostring(pinfo.dst)
    if not follow.streams[stream_id] then
        follow.streams[stream_id] = {
            start_time = pinfo.abs_ts,
            packets = 0,
            bytes = buffer:len()
        }
    end
    
    follow.streams[stream_id].packets = follow.streams[stream_id].packets + 1
    follow.streams[stream_id].bytes = follow.streams[stream_id].bytes + buffer:len()
    
    local subtree = tree:add(follow, buffer(),
        "Flux " .. stream_id .. " [" .. 
        follow.streams[stream_id].packets .. " paquets, " ..
        follow.streams[stream_id].bytes .. " octets]")
end
```

---

## Analyse forensique

### Timeline d'événements
```bash
# Extraire tous les événements avec timestamp
tshark -r capture.pcap -T fields \
    -e frame.time \
    -e ip.src \
    -e ip.dst \
    -e _ws.col.Protocol \
    -e _ws.col.Info \
    -E separator='|' > timeline.csv
```

### Reconstruction de session
```bash
# Session TCP complète
tshark -r capture.pcap -z follow,tcp,ascii,0

# Session HTTP
tshark -r capture.pcap -z follow,http,ascii,0

# Session TLS (si déchiffrée)
tshark -r capture.pcap -z follow,tls,ascii,0
```

### Recherche de mots de passe en clair
```bash
# FTP
tshark -r capture.pcap -Y "ftp.request.command==USER or ftp.request.command==PASS"

# HTTP POST
tshark -r capture.pcap -Y "http.request.method==POST" \
    -T fields -e http.file_data | grep -i "password\|user\|login\|email"

# telnet
tshark -r capture.pcap -Y "telnet" \
    -T fields -e telnet.data

# SMTP auth
tshark -r capture.pcap -Y "smtp.req.command==AUTH" \
    -T fields -e smtp.req.parameter
```

---

## Antisèche rapide

```bash
# Filtres avancés
ip.addr==X and tcp.port==80            # IP + port
http.request.uri matches "admin"        # Regex URI
dns.qry.name matches "\\.(xyz|top)$"    # TLD suspects
tcp.payload contains "cmd"              # Shell command
tls.handshake.extensions_server_name contains "internal"  # SNI

# Statistiques
tshark -r capture.pcap -z conv,tcp     # Conversations
tshark -r capture.pcap -z io,phs       # Protocol hierarchy
tshark -r capture.pcap -z io,stat,1    # IO graph 1s

# Extraction
tshark -r capture.pcap --export-objects http,/tmp/extract/

# Malware detection
tcp.payload contains "Invoke-" or tcp.payload contains "powershell -enc"
dns.qry.name matches "[a-z0-9]{40,}\\.(com|net)"

# TLS decrypt
tshark -r capture.pcap -o tls.keylog_file:/tmp/keys.log -Y "http2"

# Custom fields CSV
tshark -r capture.pcap -T fields -e ip.src -e ip.dst -e tcp.port -E separator=,
```