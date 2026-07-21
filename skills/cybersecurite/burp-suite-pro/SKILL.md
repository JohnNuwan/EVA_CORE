---
name: burp-suite-pro
description: Burp Suite Pro — proxy d'interception, scanner automatisé, Intruder avancé, Repeater, Sequencer, Decoder, Comparer, Extensions (BApp Store), workflows OWASP, et automatisation d'audit web.
---

# Burp Suite Pro — Guide Complet

## Présentation

Burp Suite est la plateforme de test d'intrusion web la plus utilisée. La version Pro ajoute le scanner de vulnérabilités automatisé, le crawling avancé, et des fonctionnalités d'entreprise.

**Éditions** : Community (gratuite) | Pro ($449/an) | Enterprise (scan DAST CI/CD)

**Installation** :
```bash
# Java requis (Java 17+)
java -jar burpsuite_pro_*.jar

# Via Kali
sudo apt install burpsuite

# Script de lancement (avec JVM tuning)
java -Xmx4G -jar burpsuite_pro_*.jar
```

---

## Proxy — Interception du trafic

### Configuration navigateur
```bash
# Proxy Burp : 127.0.0.1:8080
# Dans Firefox : Settings → Network → Proxy → 127.0.0.1:8080
# OU utiliser FoxyProxy (extension)
```

### Certificat HTTPS
```bash
# Naviguer vers http://burpsuite
# Télécharger cacert.der
# Firefox : Preferences → Privacy → Certificates → Import
# Chrome : chrome://settings/security → Manage Certificates → Import
```

### Interception sélective
```
# Proxy → Intercept → Intercept is on/off (bascule avec Ctrl+T)
# Options d'interception :
#   - Intercept requests based on rules
#   - Intercept responses based on rules

# Règles typiques :
# Ne pas intercepter les ressources statiques
# ^.*\.(js|css|png|jpg|gif|ico|svg|woff|ttf)$
```

### Filtres d'affichage (Proxy → HTTP History)
```
# Filtrer par :
#   - Méthode (GET, POST, PUT, DELETE)
#   - Code HTTP (1xx, 2xx, 3xx, 4xx, 5xx)
#   - Type MIME (HTML, JSON, XML, JS, CSS, images)
#   - Extension de fichier
#   - Requêtes par défaut
#   - Taille (plus grand que / plus petit que)

# Bouton Filter → Show only :
#   - Items with params
#   - Items with cookies
#   - 4xx responses
#   - 5xx responses
```

### WebSocket interception
```bash
# Burp capture les WebSockets automatiquement
# Onglet WebSocket History dans Proxy
# Possibilité de modifier les messages WebSocket
```

---

## Scanner (Pro) — Scan automatisé

### Types de scan
```bash
# Crawl + Audit complet
#   → Découvre TOUTES les pages + teste TOUTES les vulnérabilités

# Crawl uniquement
#   → Découvre les pages, sans test de vulnérabilité

# Audit sélectif
#   → Teste les requêtes déjà capturées (pas de crawl)

# Live scanning
#   → Pendant que vous naviguez, scanne en temps réel
```

### Configuration du scanner
```
# New Scan → Configuration :
# 1. Target URL : https://app.cible.com
# 2. Application login : credentials + URL de login
# 3. Crawl Strategy :
#    - Fastest (moins de pages, plus rapide)
#    - Faster (compromis)
#    - Thorough (toutes les pages, toutes les actions)
# 4. Audit Strategy :
#    - Light (tests rapides)
#    - Default (équilibré)
#    - Deep (tous les tests)
# 5. Scope : ce qui est dans / hors scope
```

### Vulnérabilités détectées (Pro)
```bash
# Injection : SQL, NoSQL, OS Command, LDAP, XPath
# XSS : Reflected, Stored, DOM-based
# SSRF : Server-Side Request Forgery
# XXE : XML External Entity
# Path Traversal : LFI/RFI
# File Upload : Toutes les variantes
# Deserialization : Java, PHP, Python, .NET
# Prototype Pollution
# HTTP Request Smuggling
# JWT attacks
# OAuth misconfiguration
# CORS misconfiguration
# Cache poisoning/deception
```

### Insertion points (où le scanner injecte)
```bash
# Paramètres URL (GET)
# Paramètres Body (POST/PUT)
# Headers (Cookie, User-Agent, Referer, X-Forwarded-For)
# JSON/XML body
# Multipart form parameters
# File upload names/content
# Custom defined insertion points
```

---

## Intruder — Automatisation d'attaques

### Types d'attaque
```bash
# Sniper (1 payload position, 1 wordlist)
#   → Teste chaque mot de passe pour UN champ
#   Utile pour : brute-force login simple

# Battering Ram (1 payload, plusieurs positions identiques)
#   → Même valeur injectée partout
#   Utile pour : même username/password

# Pitchfork (N positions, N wordlists — parallèle)
#   → 1ère wordlist = position 1, 2ème = position 2
#   Utile pour : paires username:password

# Cluster Bomb (N positions, N wordlists — combinatoriel)
#   → Toutes les combinaisons possibles
#   Utile pour : multi-champs brute-force
```

### Configuration payload
```bash
# Payload sets :
# Set 1 : usernames → /usr/share/wordlists/users.txt
# Set 2 : passwords → /usr/share/wordlists/rockyou.txt

# Payload processing (avant envoi) :
#   - Add prefix/suffix
#   - Encode URL-encode, Base64, HTML
#   - Hash (MD5, SHA1, SHA256)
#   - Case transformation
#   - Regex substitution
#   - Reverse substring

# Payload encoding :
#   - URL-encode specific characters
#   - Base64-encode
#   - Skip encoding for specific positions
```

### Analyse des résultats Intruder
```bash
# Colonnes de résultats :
#   - Request #    : numéro
#   - Payload      : payload utilisé
#   - Status       : code HTTP
#   - Length       : taille de la réponse
#   - RTT          : temps de réponse
#   - Comment      : note personnelle

# Stratégies d'analyse :
#   - Trier par Length (réponses différentes = intéressant)
#   - Trier par Status (200 vs 302 vs 403)
#   - Trier par RTT (temps différent = traitement différent)
#   - Regex grep : chercher "error", "success", "admin"

# Attaque par grep :
#   - Extract : extraire des regex de la réponse
#   - Grep Match : marquer si une regex correspond
```

### Grep Extract — Extraction avancée
```bash
# Configuration :
#   Intruder → Options → Grep Extract
#   Extract CSRF tokens, session IDs, etc.
#   Ajouter des regex : name="csrf" value="([^"]+)"

# Utilisation : bruteforce avec rotation de token CSRF
#   1. Grep-Extract le token CSRF de la page de login
#   2. Redéfinir les positions de payload
#   3. Lancer Pitchfork : username / password / csrf_token
```

### Intruder — Ressource pool
```bash
# Gestion des threads :
#   1 thread pour les formulaires avec CSRF (éviter dé-synchro)
#   5-10 threads pour les API sans état
#   20+ threads pour les attaques réseau simples
```

---

## Repeater — Manipulation de requêtes

### Fonctionnalités
```bash
# Envoyer une requête → modifier → renvoyer (Ctrl+R)
# Historique des requêtes/réponses
# Comparer les réponses (Ctrl+D + Send to Comparer)

# Sessions :
#   1. Créer un tab par endpoint
#   2. Nommer les tabs (double-clic sur l'onglet)
#   3. Grouper par vulnérabilité testée
#   Exemple : login_SSRF, login_SQLi, login_XSS

# Repeater avancé :
#   - Modifier l'ordre des paquets (TCP reordering)
#   - Changer le protocole (HTTP/1.1 ↔ HTTP/2)
#   - Forcer Content-Length différent (smuggling)
#   - Injecter des headers personnalisés
```

### Repeater — Hotkeys
```bash
Ctrl+R      Envoyer vers Repeater (depuis Proxy/Intruder)
Ctrl+Shift+R  Envoyer vers Repeater (depuis n'importe où)
Ctrl+E      Focus sur le body de la requête
Ctrl+U      URL-encode la sélection
Ctrl+Shift+U  URL-decode la sélection
Ctrl+B      Base64-encode
Ctrl+Shift+B  Base64-decode
Ctrl+H      HTML-encode
Ctrl+Shift+H  HTML-decode
```

---

## Extension (BApp Store)

### Extensions indispensables
```bash
# === RECONNAISSANCE ===
# Autorize         → Tester les autorisations (ACL bypass)
# Param Miner      → Découvrir des paramètres cachés
# Headers Analyzer → Analyser les en-têtes HTTP
# Software Version Reporter → Identifier les versions de logiciels

# === SCANNER ===
# Active Scan++           → Améliorer le scanner intégré
# Backslash Powered Scanner → Détection de bugs d'encodage
# Error Message Checking  → Recherche de messages d'erreur
# CSP Auditor             → Analyser Content-Security-Policy

# === EXPLOITATION ===
# SQLiPy         → SQL injection avancée
# Java Deserialization Scanner → Désérialisation Java
# JWT Editor     → Éditer/forger des tokens JWT
# JSON Web Tokens → Analyser les JWT
# OpenAPI Parser  → Importer des spécifications OpenAPI

# === AUTRE ===
# Collaborator Everywhere → Forcer les interactions Collaborator
# Content Type Converter  → Changer les Content-Type
# Copy As Python Requests → Copier en format Python
# Flow         → Visualiser les flux HTTP
# Reqable      → Automatisation avancée
# Turbo Intruder → Intruder ultra-rapide (Python)
# HTTP Request Smuggler   → Détection de smuggling
# Upload Scanner          → Test d'upload de fichiers
# WebSocket Editor        → Éditer les WebSockets
```

### Turbo Intruder (extension Python)
```python
# Turbo Intruder permet des attaques très rapides
# Exemple : race condition single-packet attack

def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=10,
                           requestsPerConnection=100,
                           pipeline=False)
    
    for i in range(1000):
        engine.queue(target.req, i)
        # Single-packet : envoyer toutes les requêtes en simultané
        if i == 999:
            engine.flush()

def handleResponse(req, interesting):
    if 'success' in req.response:
        table.add(req)
```

### Autorize — Test d'autorisation
```bash
# Détection de l'IDOR/Broken Access Control
# 1. Configurer les en-têtes (Cookie, Basic Auth, Bearer)
# 2. Activer Auto-Compare
# 3. Naviguer avec le compte admin
# 4. Autorize renvoie automatiquement avec le compte user
# 5. Coloration :
#    - Vert : même réponse (autorisation OK)
#    - Rouge : réponses différentes (potentiel IDOR)
```

### Collaborator Everywhere
```bash
# Injecte automatiquement des URL Collaborator
# dans chaque paramètre et en-tête
# Détecte : SSRF, XXE, Blind XSS, SQLi, Template Injection
# Out-of-band exfiltration
```

---

## Decoder & Comparer

### Decoder
```bash
# Encodages supportés :
#   URL, HTML, Base64, ASCII hex, Octals, Binary
#   GZip, Deflate, PEM (X.509), JSON Web Token (JWT)
#   Smart decode : détection automatique de l'encodage

# Hashing :
#   MD2, MD4, MD5, SHA1, SHA256, SHA512
#   SHA3-256, SHA3-512, RIPEMD-160, HMAC

# Use cases :
#   1. Décoder les cookies (Base64 → JSON)
#   2. Analyser les JWT (Header.Payload.Signature)
#   3. Décoder les paramètres URL-encodés
#   4. Déchiffrer les tokens d'authentification
```

### Comparer
```bash
# Comparer deux réponses (visuel ou texte)
# Utile pour :
#   1. Comparer login réussi vs échoué
#   2. Comparer accès autorisé vs non autorisé
#   3. Analyser les variations de réponse (SQLi aveugle)
#   4. Détecter les différences subtiles
#   5. Analyser les erreurs selon les inputs
```

---

## Session Handling — Gestion de session

### Règles de session
```bash
# Session Handling Rules → Add
# 1. URL Scope → restreindre à la cible
# 2. Rule Actions :
#    a. Check session is valid
#       → Vérifier si la session est encore valide
#       → Si non, exécuter l'action de re-login
#    b. Run a macro (re-login automatisé)
#       → Enregistrer une séquence de requêtes de login
#    c. Update cookies
#       → Mettre à jour les cookies après re-login
```

### Macros
```bash
# Enregistrement de macro :
#   1. Proxy → HTTP History → clic droit → Macro → Add
#   2. Selectionner les requêtes de login
#   3. Configurer les tokens CSRF
#   4. Tester la macro

# Utilisation avec Intruder :
#   Intruder → Options → Session Handling
#   → Vérifier la session avant chaque payload
#   → Auto-re-login si session expirée
```

---

## Workflow OWASP Top 10 (Pro)

### 1. Reconnaissance (Crawl)
```bash
# 1. Configurer le proxy navigateur
# 2. Naviguer manuellement (10-15 minutes)
# 3. Activer : Spider → Scope → Application login
# 4. Clic droit → Scan → Crawl (Thorough)
# 5. Pendant ce temps : analyser l'historique HTTP
```

### 2. Identification des endpoints
```bash
# 1. Site Map → Toutes les pages découvertes
# 2. Filter par paramètres (paramètres = potentiel d'injection)
# 3. Identifier les points d'entrée :
#    - Formulaires de login
#    - API endpoints (/api/, /v1/, /graphql)
#    - Upload de fichiers
#    - Paramètres URL
```

### 3. Authentification (A1/A2/A7)
```bash
# 1. Envoyer le login à Intruder (Sniper/Battering ram)
# 2. Tester les injections SQL : admin'--
# 3. Tester NoSQL : {"$gt": ""}
# 4. Tester les contournements 2FA
# 5. Tester OAuth/SSO misconfiguration
```

### 4. Injection (A3)
```bash
# SQLi :
#   1. Envoyer à Intruder (Cluster bomb)
#   2. Payloads : sqlmap wordlist + erreurs SQL
#   3. Analyser les réponses avec Grep Match

# Command Injection :
#   1. Tester ; ls, && whoami, | id, `id`
#   2. Time-based : ; sleep 5

# SSTI :
#   1. Tester {{7*7}}, ${7*7}, #{7*7}
#   2. Analyser si 49 apparaît dans la réponse
```

### 5. IDOR & Broken Access (A1)
```bash
# 1. Two accounts (admin + user)
# 2. Capturer une requête admin
# 3. Envoyer à Repeater
# 4. Changer le cookie/session pour user
# 5. Si la réponse est identique → IDOR

# Utiliser Autorize (extension) :
#   Configurer les deux tokens
#   Activer → naviguer avec admin
#   Analyser les requêtes en rouge
```

### 6. XSS (A7)
```bash
# 1. Envoyer chaque paramètre à Intruder
# 2. Payloads :
#    <script>alert(1)</script>
#    <img src=x onerror=alert(1)>
#    "><script>alert(1)</script>
#    javascript:alert(1)
# 3. Regarder : les réponses avec >, <, " non encodés

# XSS stored :
#   1. Poster un commentaire avec <script>
#   2. Naviguer vers la page de commentaires
#   3. Vérifier dans l'historique proxy
```

### 7. CSRF (A1)
```bash
# 1. Capturer une requête sensible (changement email)
# 2. Vérifier les en-têtes anti-CSRF :
#    - X-CSRF-Token
#    - Referer validation
#    - SameSite cookies
# 3. Envoyer depuis Repeater SANS les tokens
# 4. Si ça fonctionne → CSRF

# Générer le payload CSRF via Burp :
#   Clic droit → Engagement tools → Generate CSRF PoC
```

### 8. SSRF (A10)
```bash
# 1. Tester les endpoints qui fetch des URLs :
#    - ?url=
#    - ?file=
#    - ?webhook=
#    - ?callback=
# 2. Payloads :
#    http://169.254.169.254/    (AWS metadata)
#    http://127.0.0.1:8080/
#    file:///etc/passwd
# 3. Avec Collaborator Everywhere (extension)
```

---

## Scan automatisé — Recommandations

### Configuration optimale
```bash
# Scan complet (Pro) :
#   Target URL : https://app.cible.com
#   Crawl Strategy : Thorough
#   Audit Strategy : Deep
#   Max crawl depth : 10
#   Max links : 5000
#   Application login : OUI (via macro)
#   Session handling : OUI
#   Activer HTTP/2
#   Activer WebSocket testing
```

### Scan par API
```bash
# Importer une spécification OpenAPI/Swagger
# Dashboard → New Scan → Scan type → API scan
# Importer le fichier OpenAPI (JSON/YAML)
# Configurer les paramètres d'authentification
# Lancer le scan
```

### Scan GraphQL
```bash
# Burp détecte automatiquement les endpoints GraphQL
# Fonctionnalités :
#   - Introspection (découverte des query/mutation)
#   - Batching analysis
#   - CSRF via GraphQL
#   - Query depth analysis
#   - Injection dans les arguments

# Extension recommandée : InQL
```

---

## Rapport d'audit

### Génération de rapport
```bash
# Burp → Target → Site Map → clic droit → Report
# Options :
#   - Vulnerabilities (base/high/critical)
#   - Inclusion/exclusion de vulnérabilités
#   - Screenshots (Pro)
#   - Request/Response details
#   - Remediation advice
# Formats : HTML, XML, PDF (Pro)
```

### Rapport personnalisé
```bash
# Sélectionner les vulnérabilités confirmées
# Ajouter des notes (issue notes)
# Configurer le template du rapport
# Ajouter des screenshots de preuve
# Exporter → HTML (avec images)
```

---

## Antisèche rapide

```bash
# Raccourcis essentiels
Ctrl+R         → Envoyer à Repeater
Ctrl+I         → Envoyer à Intruder
Ctrl+Shift+S   → Envoyer au Scanner (Pro)
Ctrl+Shift+D   → Envoyer à Decoder
Ctrl+Shift+X   → Envoyer à Comparer
Ctrl+T         → Basculer l'interception
Ctrl+F         → Rechercher
Ctrl+Shift+F   → Rechercher dans toutes les réponses

# Workflow standard
1. Proxy → Intercept ON → Naviguer
2. Capturer les requêtes → Send to Repeater/Intruder
3. Modifier/rejouer → Analyser la réponse
4. Intruder → Configurer positions + wordlist
5. Scanner Pro → Crawl + Audit complet
6. Confirmer les vulnérabilités manuellement
7. Rapporter

# Extensions BApp indispensables
Param Miner, Active Scan++, Turbo Intruder
JWT Editor, JSON Web Tokens, Collaborator Everywhere
Autorize, Headers Analyzer, Flow
```