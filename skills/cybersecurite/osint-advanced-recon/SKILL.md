---
name: osint-advanced-recon
description: Reconnaissance OSINT avancée — footprinting de cibles, inventaire d'actifs, analyse d'infrastructure et découverte d'informations.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, reconnaissance, footprinting, infrastructure, enumération]
---

# Reconnaissance OSINT Avancée

## 🎯 Description

Techniques avancées de reconnaissance OSINT pour le footprinting de cibles (personnes, organisations, infrastructures). Couvre l'énumération de sous-domaines, la découverte d'actifs, l'analyse de surfaces d'attaque et la collecte d'informations à partir de sources ouvertes.

---

## 📋 Outils Essentiels

### Moteurs de Recherche Spécialisés
| Outil | URL | Usage |
|-------|-----|-------|
| Shodan | https://shodan.io | Recherche d'appareils IoT, serveurs, webcams |
| Censys | https://search.censys.io | Analyse de certificats SSL, appareils réseaux |
| FOFA | https://en.fofa.info | Moteur de recherche d'actifs internet |
| ZoomEye | https://www.zoomeye.ai | Découverte de périphériques réseau |
| Criminal IP | https://www.criminalip.io | CTI et gestion de surface d'attaque |
| FullHunt | https://fullhunt.io | Identification et protection d'actifs exposés |
| ONYPHE | https://search.onyphe.io | Indexation d'actifs exposés |
| Netlas | https://app.netlas.io | Recherche d'infrastructures |
| Hunter | https://hunter.how | Recherche d'actifs exposés, répertoires ouverts |
| GreyNoise | https://viz.greynoise.io | Recherche d'IP malveillantes |

### Certificats SSL et Transparence
| Outil | URL | Usage |
|-------|-----|-------|
| crt.sh | https://crt.sh | Recherche de certificats SSL publics |
| CertKit | https://www.certkit.io/tools/ct-logs/ | Recherche rapide dans les CT logs |
| CertSpotter | https://certspotter.com | Surveillance de certificats |

### DNS et Sous-domaines
| Outil | URL | Usage |
|-------|-----|-------|
| DNSDumpster | https://dnsdumpster.com | Découverte d'hôtes liés à un domaine |
| SecurityTrails | https://securitytrails.com | DNS historiques et courants |
| DNSViz | https://dnsviz.net | Visualisation DNS |
| Domain Tools | https://whois.domaintools.com | WHOIS et données historiques |
| ViewDNS | https://viewdns.info | Ensemble d'outils DNS |
| digga | https://digga.dev | DNS, RDAP, WHOIS, sous-domaines |

### BGPs et ASNs
| Outil | URL | Usage |
|-------|-----|-------|
| BGP.he.net | https://bgp.he.net | Analyse BGP et ASN |
| BGP.tools | https://bgp.tools | Toolkit BGP moderne |
| Bgpview.io | https://bgpview.io | Détails sur ASN, IP, routes BGP |

---

## 🔧 Méthodologie

### Phase 1 : Collecte Passive
```bash
# WHOIS
whois example.com

# Dig DNS
dig example.com ANY +noall +answer
dig example.com AAAA +short
dig example.com MX +short
dig example.com TXT +short

# DNS History
nslookup example.com 8.8.8.8
host -a example.com

# Certificats SSL
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq '.[].name_value' | sort -u
```

### Phase 2 : Énumération de Sous-domaines
```bash
# DNS Bruteforce (nécessite une wordlist)
for sub in $(cat subdomains.txt); do host "$sub.example.com" 2>/dev/null; done

# Utilisation de SecurityTrails (API gratuite limitée)
# curl -s "https://api.securitytrails.com/v1/domain/example.com/subdomains?apikey=KEY"

# DNSDumpster (scraping)
# Naviguer sur https://dnsdumpster.com - entrer le domaine
```

### Phase 3 : Analyse d'Infrastructure
```bash
# Shodan CLI
shodan search hostname:example.com
shodan search org:"Organization Name"
shodan domain example.com

# Censys
# Naviguer sur https://search.censys.io/ -> chercher par domaine/IP

# whois ASN
whois -h whois.arin.net "AS12345"
```

### Phase 4 : Historique et Archives
```bash
# Internet Archive
curl -s "https://web.archive.org/cdx/search/cdx?url=example.com/*&output=text&fl=original,timestamp"

# Google Cache
# Naviguer vers cache:https://example.com

# PageGlimpse
curl -s "https://www.pageglimpse.com/api/v1/example.com"
```

---

## 📊 Google Dorks Avancés

```text
# Fichiers exposés
site:example.com filetype:pdf OR filetype:docx OR filetype:xlsx
site:example.com intitle:"index of" (pdf|doc|sql|backup|conf)

# Répertoires exposés
site:example.com intitle:"Directory Listing"
inurl:example.com inurl:wp-content/uploads
inurl:example.com inurl:admin OR inurl:backup

# Informations sensibles
site:example.com ext:log OR ext:env OR ext:yml
site:example.com "password" OR "credentials" ext:txt
site:example.com "BEGIN RSA PRIVATE KEY"
site:example.com "DB_PASSWORD" OR "API_KEY"

# Emails et contacts
site:example.com "@example.com" OR "contact"
```

---

## 🛠️ Commandes Utiles

### Analyse Technologique
```bash
# Wappalyzer (CLI avec l'API)
curl -s "https://api.wappalyzer.com/lookup/v1/?url=https://example.com"

# BuiltWith
curl -s "https://api.builtwith.com/free1/api.json?KEY=API&LOOKUP=example.com"

# Web-Check
# Naviguer vers https://web-check.as93.net/
```

### Réseau et Connectivité
```bash
# Traceroute visuel
curl -s "https://kriztalz.sh/traceroute-visualizer/"

# Test SSL
curl -s "https://www.ssllabs.com/ssltest/analyze.html?d=example.com"

# Détection CloudFlare
dig example.com CNAME +short
```

### Scan de Buckets S3
```bash
# GrayhatWarfare
curl -s "https://grayhatwarfare.com/api/buckets?accessToken=APIKEY"
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Rate Limiting** : Beaucoup d'API (crt.sh, Shodan) limitent le nombre de requêtes. Utiliser des délais entre les appels.
- **Détection** : L'énumération DNS agressive peut être détectée. Préférer les sources passives (CT logs, certificats) en premier.
- **Anonymat** : Utiliser Tor ou un VPN pour les recherches qui pourraient alerter la cible.
- **Validation** : Toujours vérifier les résultats avec plusieurs sources (DNS historique + certs + WHOIS).
- **Stockage** : Les changements DNS peuvent prendre 24-48h. Les certificats restent dans les logs CT pour des années.

---

## 🔗 Références

- https://osintframework.com
- https://github.com/jivoi/awesome-osint
- https://search.censys.io
- https://www.shodan.io
- https://crt.sh