---
name: osint-cyber-tools-platforms
description: "Compétence niveau ingénieur/docteur en outils et plateformes OSINT et cybersécurité. Couvre Shodan, Censys, VirusTotal, Maltego, TheHarvester, Recon-ng, SpiderFoot, Nmap, Wireshark, Metasploit, BurpSuite, AI pentesting (Strix 38k stars), GitHub OSINT, Telegram OSINT, geolocation OSINT, forensic tools, et plateformes de threat intelligence."
category: research
tags: [osint, cybersecurite, threat-intelligence, pentesting, forensics, reseau, securite]
---

# Outils et Plateformes OSINT/Cybersécurité — Référence Ingénieur/Docteur

## Présentation

Ce skill couvre l'ensemble des outils, plateformes et méthodologies pour l'OSINT (Open Source Intelligence) et la cybersécurité offensive/défensive. Conçu pour un niveau ingénieur/docteur nécessitant une maîtrise de l'infrastructure de collecte de renseignement, d'analyse de menaces, et de tests d'intrusion.

---

## 1. Moteurs de Recherche OSINT

### Shodan
- **Moteur** : IoT, CCTV, SCADA, serveurs, routeurs, caméras
- **Recherche** : Filtres par port, protocole, pays, ville, organisation, vulnérabilité
- **Filtres clés** : `port:`, `protocol:`, `country:`, `city:`, `org:`, `os:`, `product:`, `vuln:`
- **API** : REST JSON, gratuit (100 req/mois), API payant (1M+ req)
- **Shodan CLI** : `shodan search` + filtres
- **Shodan Maps** : Carte géographique des appareils
- **Usage** : Audit d'exposition, recherche de vulnérabilités, cartographie réseau

### Censys
- **Moteur** : Certificats TLS, hôtes, services, ports
- **Données** : Scans Internet complets (IPv4 + IPv6)
- **Filtres** : `services.port`, `services.service_name`, `location.country`
- **API** : REST + Python SDK, gratuit (250 req/mois), pro ($74/mois)
- **Censys Search** : Recherche de certificats, hôtes, sous-domaines
- **Particularité** : Certificats TLS historiques, dates de validité

### ZoomEye
- **Moteur** : Dispositifs réseau, services, protocoles
- **Recherche** : Similaire Shodan, focus Asie
- **API** : REST, quotas gratuits limités
- **Usage** : Complément à Shodan/Censys pour couverture globale

### FOFA
- **Moteur** : Recherche de dispositifs, services, actifs exposés
- **Spécificité** : Forte couverture Asie-Pacifique
- **API** : REST, payant, plans par volume de requêtes
- **Usage** : OSINT, cartographie, reconnaissance

### Criminal IP
- **Moteur** : Cyber threat intelligence, asset discovery
- **Données** : IP, domain, URL, SSL, IoT, OT
- **API** : REST, plans gratuits et payants
- **Spécificité** : Score de risque, détection de menace

---

## 2. Analyse de Menaces (Threat Intelligence)

### VirusTotal
- **Analyse** : Fichiers, URLs, IPs, domaines — 70+ antivirus engines
- **API** : REST JSON, gratuit (4 req/min, 500 req/jour)
- **Premium** : API publique, intelligence, hunts, retrohunt
- **Fonctionnalités** : YARA rules, Sigma rules, crowdsourced YARA, file behavior
- **VirusTotal Graph** : Graphe de relations (IP → domain → file → URL)
- **Community** : Commentaires, votes, tags

### AlienVault OTX (Open Threat Exchange)
- **Communauté** : Threat intelligence partagée, 100k+ pulses
- **Pulses** : Indicateurs de compromission (IOCs) — IP, domain, hash, CVE
- **API** : REST, gratuit
- **OTX Endpoint** : Collecte automatisée d'IOCs
- **Intégration** : SIEM, IDS, firewall

### MISP (Malware Information Sharing Platform)
- **Plateforme** : Open-source, partage d'IOCs structurés
- **Taxonomie** : ATT&CK, DML, kill chain, MISP taxonomies
- **API** : REST, PyMISP SDK
- **Fonctionnalités** : Correlation, warning lists, feed, export
- **Usage** : SOC, CERT, équipe bleue, partage entre organisations

### Pulsedive
- **Plateforme** : Threat intelligence, score de risque
- **Données** : IP, domain, URL, hash, CVE
- **API** : REST, gratuit (30 req/jour), pro ($49/mois)
- **Particularité** : Indicateurs géopolitiques, acteurs, campagnes

### URLScan.io
- **Analyse** : Screenshot + metadata de sites web
- **API** : REST, gratuit (50 req/mois), pro ($20-100/mois)
- **Données** : DOM, requests, cookies, headers, certificats
- **Usage** : Phishing, malvertising, site analysis

### GreyNoise
- **Analyse** : Bruit Internet (scanners, bots, mass-scan)
- **API** : REST, gratuit (10K req/mois), pro ($99/mois)
- **Données** : IP, tags (RDP scanner, SSH brute, etc.), dates
- **Usage** : Filter le bruit des scanners, prioriser les alertes

### AbuseIPDB
- **Base** : IPs malveillantes signalées par la communauté
- **Vérification** : Catégorie d'abus, confiance, pays
- **API** : REST, gratuit (1000 req/jour), premium
- **Usage** : Blacklist IP, vérification de réputation

---

## 3. OSINT Automation

### SpiderFoot HX
- **Framework** : Reconnaissance automatisée OSINT
- **Modules** : 200+ modules (DNS, WHOIS, SHODAN, etc.)
- **Modes** : CLI, serveur web, API
- **Corrélations** : Graphe de relations entre entités
- **Scan Types** : IP, domain, email, ASN, name, bitcoin
- **Données** : Résultats exportables (CSV, JSON, HTML)

### TheHarvester
- **Outil** : Collecte d'emails, sous-domaines, IPs, hôtes
- **Sources** : Google, Bing, Baidu, Yahoo, Shodan, DNSDumpster, etc.
- **Usage** : Reconnaissance passive, test d'intrusion
- **Syntaxe** : `theharvester -d example.com -b google -l 500`

### Recon-ng
- **Framework** : Reconnaissance web modulaire
- **Modules** : 100+ modules (DNS, WHOIS, subdomain, geolocation)
- **API Keys** : Gestion centralisée des clés API
- **Workspace** : Organisation par cible
- **Recon-ng v5** : Interface améliorée, nouvelles API

### Maltego
- **Outil** : Analyse de liens, graphe de relations
- **Transforms** : 100+ transforms (DNS, WHOIS, social, etc.)
- **Hubs** : Maltego Hub, Paterva, commercial
- **Éditions** : CE (gratuite), XL (pro), Classic (payant)
- **Usage** : Enquête, cartographie d'infrastructure, attribution

### Sherlock
- **Outil** : Recherche de username sur 400+ réseaux sociaux
- **Usage** : OSINT humain, vérification d'identité
- **Syntaxe** : `sherlock username`
- **Sortie** : URLs valides, statut (présent/absent)

---

## 4. AI Pentesting

### Strix (usestrix/strix)
- **Stars** : ~38k GitHub (explosion récente)
- **Approche** : AI open-source pour pentesting automatisé
- **Capacités** : Reconnaissance, exploitation, post-exploitation, reporting
- **Tech** : LLM, agents autonomes, planification
- **Phases** :
  1. Reconnaissance passive/active
  2. Scanning de vulnérabilités
  3. Exploitation (web, réseau, social engineering)
  4. Post-exploitation (persistance, exfiltration)
  5. Rapport automatique

### OWASP ZAP (Zed Attack Proxy)
- **Outil** : Proxy d'interception, scanner de vulnérabilités web
- **Modes** : Automated scan, manual explore, authenticated scan
- **Plugins** : 100+ règles de scan passif/actif
- **API** : REST, Java, Python
- **Usage** : CI/CD pipeline, DAST, pentest web

### Burp Suite
- **Outil** : Proxy d'interception complet pour pentest web
- **Éditions** : Community (gratuit), Professional ($399/an), Enterprise
- **Fonctionnalités** : Repeater, Intruder, Scanner, Decoder, Sequencer
- **Extensions** : BApp Store (200+ extensions)
- **API** : REST (Enterprise), GraphQL

### Nuclei
- **Outil** : Scanner de vulnérabilités basé sur templates YAML
- **Templates** : 8000+ templates (CVE, expositions, configurations)
- **Moteur** : Rapide, multi-thread, protocoles multiples (HTTP, DNS, TCP, etc.)
- **Intégration** : CI/CD, automatisation
- **Nuclei Cloud** : Scan cloud managed

---

## 5. Réseau & Forensics

### Nmap / Masscan
- **Nmap** : Scanner réseau, découverte, OS fingerprint, version detection
- **NSE (Nmap Scripting Engine)** : 600+ scripts de scan
- **Masscan** : Scanner ultra-rapide (10M pps), idéal pour Internet-scale
- **Syntaxe** : `nmap -sV -sC -O target`, `masscan 0.0.0.0/0 -p80`
- **Formats** : XML, grepable, JSON, interactive

### Wireshark / tshark
- **Wireshark** : Analyse de paquets réseau, UI graphique
- **tshark** : CLI équivalente pour scripts
- **Filtres** : Display filters, capture filters (BPF)
- **Protocoles** : 3000+ protocoles dissected
- **Usage** : Analyse de trafic, forensics réseau, reverse engineering protocole

### Aircrack-ng
- **Suite** : Wi-Fi security auditing
- **Outils** : airodump-ng, aircrack-ng, aireplay-ng, airmon-ng
- **Attaques** : WPA/WPA2 cracking, WEP, WPS, PMKID
- **Usage** : Pentest Wi-Fi, audit de sécurité sans fil

### Volatility
- **Framework** : Analyse de mémoire volatile (RAM forensics)
- **Profils** : Windows, Linux, macOS profiles
- **Plugins** : processes, connections, registry, cmdline, files
- **Volatility 3** : Python 3, symbol tables, multi-OS
- **Usage** : Post-exploitation, analyse de malware, memory dump

### Autopsy / Sleuth Kit
- **Autopsy** : Plateforme forensics numérique, UI graphique
- **Sleuth Kit** : CLI tools (fls, icat, mmls, fsstat)
- **Fonctionnalités** : File system analysis, keyword search, timeline, hash lookup
- **Formats** : Images disque (DD, E01, AFF)
- **Usage** : Forensics disque, récupération de fichiers

### FTK Imager (AccessData)
- **Outil** : Acquisition d'images disque (forensiques)
- **Fonctionnalités** : Preview, export, hash verification
- **Formats** : DD, E01, AFF, SMART
- **Usage** : Acquisition légale, montage d'image en lecture seule

---

## 6. OSINT Humain

### Telegram OSINT
- **Telegram Scraper** : Extraction de messages, membres, métadonnées
- **Outils** : `telegram-osint`, `tg-searcher`, `Telegram-Message-Analyzer`
- **API** : Telethon (Python), Telegram Bot API
- **Cibles** : Groupes, channels, bots, user metadata
- **Usage** : Enquête, monitoring, collecte de renseignement

### Discord OSINT
- **Outils** : `discord-osint`, `DScord`
- **Données** : User info, server info, messages, voice channels
- **API** : Discord API (bot token requis)
- **Usage** : Investigations, modération, analyse de communauté

### Holehe
- **Outil** : Vérification d'email sur 100+ sites web
- **Méthode** : Tentative d'inscription, réponse du serveur
- **Syntaxe** : `holehe email@example.com`
- **Usage** : OSINT email, vérification de compte

### WhatsMyName
- **Outil** : Recherche de username sur 300+ sites
- **Base** : `webbreacher/whatsmy name` — liste de sites
- **Usage** : OSINT username, cross-platform identity

### Social Links
- **Plateforme** : OSINT professionnel, 400+ sources
- **Fonctionnalités** : Recherche par email, téléphone, username, nom
- **API** : Social Links API (payant)
- **UI** : Interface graphique, export, dashboard

---

## 7. Catégories d'Outils

| Catégorie | Outils | Usage Principal |
|-----------|--------|-----------------|
| Moteurs OSINT | Shodan, Censys, ZoomEye, FOFA, Criminal IP | Découverte d'actifs exposés |
| Threat Intel | VirusTotal, OTX, MISP, Pulsedive, GreyNoise | Analyse de menaces, IOCs |
| Automation | SpiderFoot, TheHarvester, Recon-ng, Maltego | Reconnaissance automatisée |
| AI Pentest | Strix, OWASP ZAP, Burp Suite, Nuclei | Tests d'intrusion autonomes |
| Réseau | Nmap, Wireshark, Aircrack-ng, Masscan | Scan réseau, protocoles |
| Forensics | Volatility, Autopsy, FTK Imager, Sleuth Kit | Analyse mémoire, disque |
| OSINT Humain | Sherlock, Holehe, Telegram OSINT, Discord OSINT | Identité, réseaux sociaux |

---

## 8. Workflow de Reconnaissance OSINT

### Phase 1 : Passive Reconnaissance
```
1. Domain → WHOIS, DNS (dig, dnsrecon), SSL/TLS (Censys)
2. Email → Holehe, TheHarvester, Hunter.io
3. Username → Sherlock, WhatsMyName, Social Links
4. IP/ASN → Shodan, Censys, GreyNoise
5. Web → URLScan.io, Wayback Machine, Google dorking
```

### Phase 2 : Active Reconnaissance
```
1. Port scan → Nmap, Masscan
2. Vulnerability scan → Nuclei, ZAP, Nikto
3. Web enumeration → Dirb, Gobuster, FFUF
4. Service enumeration → Enum4linux, SMTP, SNMP
5. Screenshot → EyeWitness, Aquatone
```

### Phase 3 : Exploitation & AI
```
1. AI-assisted pentesting → Strix (autonomous)
2. Manual exploitation → Burp Suite, Metasploit
3. Web apps → SQLMap, XSSer, Commix
4. Post-exploitation → Empire, Covenant, Cobalt Strike
```

### Phase 4 : Forensics & Reporting
```
1. Memory dump → Volatility
2. Disk forensics → Autopsy, Sleuth Kit
3. Network traffic → Wireshark, tshark
4. Threat intelligence → MISP, OTX, VirusTotal
5. Rapport → Dradis, Faraday, CherryTree
```

---

## Ressources

- [Shodan API](https://developer.shodan.io)
- [Censys Docs](https://docs.censys.io)
- [VirusTotal API](https://docs.virustotal.com)
- [SpiderFoot HX](https://www.spiderfoot.net)
- [OWASP ZAP](https://www.zaproxy.org)
- [Strix GitHub](https://github.com/usestrix/strix)
- [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates)
- [Volatility 3](https://github.com/volatilityfoundation/volatility3)
- [MISP Project](https://www.misp-project.org)