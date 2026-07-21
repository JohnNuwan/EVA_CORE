---
name: osint-domain-infrastructure
description: Footprinting de domaine et d'infrastructure — DNS, WHOIS, certificats SSL, hébergement, technologies web et découverte d'actifs.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, domaine, DNS, WHOIS, infrastructure, footprinting, sous-domaines]
---

# Domain et Infrastructure Footprinting

## 🎯 Description

Analyse complète de l'infrastructure d'une cible via domaine : DNS, WHOIS, certificats SSL, technologies web, hébergement, sous-domaines, IPs, ASN, et historique. Fondamental pour la cartographie de surface d'attaque.

---

## 📋 Outils Essentiels

### WHOIS et Enregistrement
| Outil | URL | Usage |
|-------|-----|-------|
| Domain Tools | https://whois.domaintools.com | WHOIS complet + historique |
| ICANN Lookup | https://lookup.icann.org/en/lookup | WHOIS officiel |
| Whois.is | https://who.is/ | WHOIS rapide |
| Whoisology | https://whoisology.com | Historique WHOIS |
| WhoisMind | https://www.whoismind.com | WHOIS + autres données |
| ARIN WHOIS | https://whois.arin.net | WHOIS IP/ASN |
| SecurityTrails | https://securitytrails.com | WHOIS + DNS historiques |

### DNS et Sous-domaines
| Outil | URL | Usage |
|-------|-----|-------|
| DNSDumpster | https://dnsdumpster.com | Cartographie DNS |
| crt.sh | https://crt.sh | Certificats SSL → sous-domaines |
| SecurityTrails | https://securitytrails.com | DNS historiques |
| DNSViz | https://dnsviz.net | Visualisation DNS |
| ViewDNS | https://viewdns.info | Multi-outils DNS |
| digga | https://digga.dev | DNS, RDAP, WHOIS, sous-domaines |
| DNS History | https://completedns.com/dns-history/ | Historique DNS |
| Robtex | https://www.robtex.com | DNS + IP + ASN |
| SubDomainRadar | https://subdomainradar.io | Découverte de sous-domaines |

### Technologies Web
| Outil | URL | Usage |
|-------|-----|-------|
| BuiltWith | https://builtwith.com | Stack technologique complet |
| Wappalyzer | https://www.wappalyzer.com | Détection de technologies |
| Web-Check | https://web-check.as93.net/ | Méta-données complètes |
| urlscan | https://urlscan.io | Scan et analyse de sites |
| Netcraft | https://toolbar.netcraft.com/site_report | Rapport de site |
| WhatIsMyIP | https://whatismyipaddress.com | Infos IP |
| Browserling | https://www.browserling.com | Test sandbox de URLs |

### Certificats SSL
| Outil | URL | Usage |
|-------|-----|-------|
| crt.sh | https://crt.sh | Recherche certificats |
| CertKit | https://www.certkit.io/tools/ct-logs/ | CT logs |
| SSLLabs | https://www.ssllabs.com/ssltest/ | Test configuration SSL |

### Analyse de Réputation
| Outil | URL | Usage |
|-------|-----|-------|
| VirusTotal | https://www.virustotal.com | Analyse de domaines/IPs |
| URLVoid | https://www.urlvoid.com | Réputation multi-blacklists |
| AbuseIPDB | https://www.abuseipdb.com | Réputation IP |
| Talos Intelligence | https://talosintelligence.com/reputation_center | Réputation Cisco |
| BrightCloud | https://brightcloud.com/tools/url-ip-lookup.php | Catégorisation + réputation |
| GreyNoise | https://viz.greynoise.io | IP malveillantes |
| URLScan | https://urlscan.io | Scan de URLs |
| Pulsedive | https://pulsedive.com | Indicateurs de menace |

---

## 🔧 Commandes CLI Essentielles

### WHOIS
```bash
# WHOIS standard
whois example.com

# WHOIS IP
whois 8.8.8.8

# WHOIS via ARIN
whois -h whois.arin.net "n 8.8.8.0"
```

### DNS
```bash
# Enregistrements DNS
dig example.com ANY +noall +answer
dig example.com A +short
dig example.com AAAA +short
dig example.com MX +short
dig example.com NS +short
dig example.com TXT +short
dig example.com CNAME +short
dig example.com SOA +short

# DNS inversé
dig -x 8.8.8.8 +short

# Vérification DNSSEC
dig example.com DNSKEY +short

# SPF / DKIM / DMARC
dig example.com TXT | grep "v=spf1"
dig _dmarc.example.com TXT
dig _domainkey.example.com TXT

# Résolution
host example.com
nslookup example.com
```

### Certificats SSL
```bash
# Vérification SSL
openssl s_client -connect example.com:443 -servername example.com 2>/dev/null | openssl x509 -text

# Extraire les sous-domaines des certificats
curl -s "https://crt.sh/?q=%25.example.com&output=json" | jq -r '.[].name_value' | sort -u

# Vérifier la date d'expiration
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## 📊 API et Scripts

### API crt.sh (Certificats → Sous-domaines)
```bash
# Récupérer tous les sous-domaines
curl -s "https://crt.sh/?q=%25.example.com&output=json" | \
  jq -r '.[].name_value' | \
  sort -u | \
  grep -v "\*" > subdomains.txt

# Format JSON
curl -s "https://crt.sh/?q=example.com&output=json" | python3 -m json.tool
```

### API SecurityTrails
```bash
# DNS historiques
curl -s -H "APIKEY: YOUR_KEY" \
  "https://api.securitytrails.com/v1/domain/example.com/history/dns/a"

# Sous-domaines
curl -s -H "APIKEY: YOUR_KEY" \
  "https://api.securitytrails.com/v1/domain/example.com/subdomains"
```

### API Shodan
```bash
# Recherche par domaine
shodan search hostname:example.com

# Recherche par organisation
shodan search org:"Example Corp"

# Informations IP
shodan host 8.8.8.8
```

---

## 🛠️ Script de Recon Automatisé

```bash
#!/bin/bash
# domain_recon.sh
DOMAIN="$1"

echo "=== Reconnaissance pour: $DOMAIN ==="

# 1. WHOIS
echo "--- WHOIS ---"
whois "$DOMAIN" | grep -E "Registrar|Creation|Expiry|Name Server|Registrant"

# 2. DNS
echo "--- DNS Records ---"
for type in A AAAA MX NS TXT CNAME; do
    result=$(dig "$DOMAIN" "$type" +short)
    [ -n "$result" ] && echo "$type: $result"
done

# 3. Sous-domaines via crt.sh
echo "--- Sous-domaines (crt.sh) ---"
curl -s "https://crt.sh/?q=%25.$DOMAIN&output=json" | \
  jq -r '.[].name_value' | sort -u | grep -v "\*" | head -20

# 4. HTTP Headers
echo "--- HTTP Headers ---"
curl -sI "https://$DOMAIN" | head -20

# 5. Technologies
echo "--- Technologies ---"
curl -s "https://builtwith.com/$DOMAIN" | grep -oP '(?<=<h2>)[^<]+' | head -10
```

---

## 📝 Analyse d'Infrastructure

### Cartographie des Actifs
```text
1. Domaine principal → IP(s)
2. IP(s) → ASN, hébergeur, géolocalisation
3. Sous-domaines → IPs additionnelles
4. Certificats SSL → Domaines additionnels
5. MX records → Serveurs email
6. NS records → DNS providers
7. SPF/DKIM/DMARC → Politiques email
8. Technologies → CMS, frameworks, versions
```

### Vérification de Sécurité
```bash
# SSL Labs Test
# Naviguer vers https://www.ssllabs.com/ssltest/analyze.html?d=example.com

# DNSSEC Debugger
# Naviguer vers https://dnssec-debugger.verisignlabs.com

# Détection de pare-feu
curl -sI "https://example.com" | grep -i "server\|cf-ray\|x-sucuri"
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **DNS caching** : Les résultats DNS peuvent être mis en cache. Utiliser `+noall +answer` pour ignorer les données d'autorité.
- **CDN** : Beaucoup de sites utilisent CloudFlare, Akamai, etc. L'IP réelle peut être masquée.
- **WHOIS privacy** : De nombreux domaines ont le WHOIS masqué. Vérifier l'historique WHOIS pour trouver les vraies données.
- **Rate limiting** : crt.sh, SecurityTrails et autres limitent les appels. Espacer les requêtes.
- **Validation** : Toujours vérifier les sous-domaines découverts : `curl -sI https://sub.example.com`.
- **Certificats wildcard** : `*.example.com` dans crt.sh peut générer beaucoup de faux positifs. Filtrer avec `grep -v "\*"`.

---

## 🔗 Références

- https://github.com/jivoi/awesome-osint#domain-and-ip-research
- https://crt.sh
- https://dnsdumpster.com
- https://github.com/indianajohn/domain-recon