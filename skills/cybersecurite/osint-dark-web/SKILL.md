---
name: osint-dark-web
description: OSINT sur le Dark Web et le Deep Web — Tor, Onion services, marchés noirs, forums clandestins et surveillance de menaces.
category: cybersecurite
author: EVA
version: 1.0
tags: [osint, dark-web, deep-web, tor, onion, menace, surveillance]
---

# Dark Web et Deep Web OSINT

## 🎯 Description

Techniques d'investigation sur le dark web et le deep web : navigation Tor, recherche sur les services onion, surveillance de forums clandestins, identification de marchés noirs, collecte de renseignements sur les acteurs de menace et analyse de données illicites.

---

## 📋 Outils Essentiels

### Navigation et Recherche
| Outil | URL | Usage |
|-------|-----|-------|
| Tor Browser | https://www.torproject.org | Navigation anonyme .onion |
| Tails OS | https://tails.net | OS anonyme complet |
| Ahmia | https://ahmia.fi | Moteur de recherche .onion (clearnet) |
| Aleph Open Search | https://open-search.aleph-networks.eu | Recherche dark web |
| OnionScan | https://github.com/s-rah/onionscan | Scan de services onion |
| onion-lookup | https://onion.ail-project.org/ | Vérification d'adresses .onion |

### Analyse de Menaces
| Outil | URL | Usage |
|-------|-----|-------|
| Dark Web Informer | https://darkwebinformer.com/threat-actor-database/ | 854+ acteurs de menace |
| IntelX | https://intelx.io | Dark web + fuites |
| VoidAccess | https://github.com/KatrielMoses/voidaccess | Platforme CTI dark web |
| OnionScan | https://github.com/s-rah/onionscan | Investigation de sites .onion |

### Cryptomonnaies et Blockchain
| Outil | URL | Usage |
|-------|-----|-------|
| Blockchair | https://blockchair.com | Explorateur multi-blockchain |
| OXT | https://oxt.me | Analyse transactionnelle BTC |
| WalletExplorer | https://www.walletexplorer.com | Identification wallets BTC |
| Chainalysis | https://www.chainalysis.com | Analyse blockchain (pro) |
| EyeTON (Telegram) | https://telegram.me/istoneyebot | TON wallet graph |

---

## 🔧 Méthodologie

### Phase 1 : Configuration de l'Environnement
```bash
# Installation Tor
sudo apt install tor torsocks -y

# Démarrer Tor
sudo systemctl start tor

# Test de connexion
curl --socks5-hostname localhost:9050 https://check.torproject.org

# Tor Browser (GUI)
# Télécharger depuis https://www.torproject.org/download/
```

### Phase 2 : Recherche d'Adresses .onion
```bash
# Ahmia - recherche de sites .onion (via clearnet)
# Naviguer sur https://ahmia.fi

# onion-lookup - vérification
curl -s "https://onion.ail-project.org/api/lookup?address=example.onion"

# Scan d'un service onion
# OnionScan (nécessite Tor)
# git clone https://github.com/s-rah/onionscan
# onionscan example.onion
```

### Phase 3 : Surveillance de Forums
```bash
# Utiliser des alerts sur les forums publics
# - IntelX: configurer des monitorings
# - RSS feeds des forums (quand disponibles)
# - Télégram bots de surveillance

# Vérification de fuites
# Naviguer sur https://intelx.io -> rechercher par email/username
```

### Phase 4 : Analyse de Cryptomonnaies
```bash
# Recherche d'adresse BTC
# Naviguer sur https://www.blockchain.com/explorer

# Analyse de wallet
# Naviguer sur https://oxt.me

# Wallet clustering
# Naviguer sur https://www.walletexplorer.com
```

---

## 📊 Moteurs de Recherche Spécialisés

### Clearnet (sans Tor)
| Outil | URL | Usage |
|-------|-----|-------|
| Ahmia | https://ahmia.fi | Indexe les sites .onion |
| IntelX | https://intelx.io | Dark web + breaches |
| Dark Web Informer | https://darkwebinformer.com | Base de données d'acteurs |
| BreachHQ | https://breach-hq.com/threat-actors | Acteurs de menace |
| Malpedia | https://malpedia.caad.fkie.fraunhofer.de | Malware + acteurs |

### Tor uniquement (proxy SOCKS5 requis)
```bash
# Recherche Ahmia via Tor
curl --socks5-hostname localhost:9050 http://juhanurmihxlp77nkq76byazcldy2hlmovfu2epvl5ankdibsot4csyd.onion

# Facebook via Tor
# http://facebookcorewwwi.onion
```

---

## 🛠️ Scripts et Commandes

### Scan Automatisé de Services Onion
```bash
#!/bin/bash
# onion_check.sh
ONION="$1"

echo "=== Vérification: $ONION ==="

# Test de disponibilité
curl --socks5-hostname localhost:9050 \
  --connect-timeout 30 \
  -sI "http://$ONION" 2>/dev/null && \
  echo "✓ Accessible" || echo "✗ Inaccessible"

# Récupération du titre
curl --socks5-hostname localhost:9050 \
  --connect-timeout 30 \
  -s "http://$ONION" 2>/dev/null | \
  grep -oP '(?<=<title>)[^<]+' || echo "Pas de titre"

# onion-lookup (via clearnet)
curl -s "https://onion.ail-project.org/api/lookup?address=$ONION" | python3 -m json.tool
```

### Surveillance d'Alertes
```bash
# Utilisation de cron pour la surveillance
# cat /etc/cron.d/onion_monitor
# 0 */6 * * * /home/user/scripts/check_onion.sh >> /var/log/onion_monitor.log
```

---

## 📝 Identification d'Acteurs de Menace

### Bases de Données
```text
Sources pour identifier des acteurs :

- APT Groups: https://docs.google.com/spreadsheets/d/1H9_xaxQHpWaa4O_Son4Gx0YOIzlcBWMsdvePFX68EKU/
- Bi.Zone: https://gti.bi.zone/ (148 groupes)
- Malpedia: https://malpedia.caad.fkie.fraunhofer.de/actors
- MISP Galaxy: https://www.misp-galaxy.org/360net/
- Threat Actor Usernames: https://threatactorusernames.com/ (3M+ usernames)
- FortiGuard: https://www.fortiguard.com/threat-actor
```

### Indicateurs de Compromission (IOCs)
```bash
# Recherche d'IOCs dans les sources du dark web
# - Adresses IP malveillantes
# - Hashes de malwares
# - URLs de C2
# - Adresses de wallets crypto
# - Noms d'utilisateurs d'acteurs
```

---

## ⚠️ Sécurité et Anonymat

### Règles Essentielles
```text
1. **TOUJOURS utiliser Tor** pour accéder aux services .onion
2. **Ne JAMAIS télécharger** de fichiers depuis le dark web
3. **Ne JAMAIS entrer** d'informations personnelles
4. **Désactiver JavaScript** dans Tor Browser (niveau sécurité: Safest)
5. **Utiliser Tails OS** pour les investigations sensibles
6. **Ne JAMAIS connecter** son identité réelle au dark web
7. **Isoler** les sessions d'investigation
8. **Documenter** sans stocker de contenu illégal
```

### Recommandations Techniques
```bash
# Tor Browser - niveau sécurité maximum
# Preferences → Security → Safest

# Tails OS (recommandé)
# https://tails.net/install/

# VPN + Tor (bridge)
# Tor Bridges: https://bridges.torproject.org/
```

---

## ⚠️ Pièges et Bonnes Pratiques

- **Légalité** : L'accès à certains contenus du dark web est illégal. Connaître les lois locales.
- **Pièges** : Les sites d'application de la loi (honeypots) sont courants.
- **Malware** : Les sites .onion peuvent contenir des exploits. Ne pas cliquer sur des liens suspects.
- **Exit nodes** : Tor exit nodes peuvent être surveillés. Utiliser .onion direct quand possible.
- **Anonymat** : Tor seul ne suffit pas. Combiner avec Tails, VPN, et bonnes pratiques.
- **Preuves** : Documenter les découvertes sans stocker de contenu illégal. Captures d'écran du navigateur uniquement.

---

## 🔗 Références

- https://www.torproject.org
- https://github.com/jivoi/awesome-osint#dark-web-search-engines
- https://github.com/s-rah/onionscan
- https://intelx.io/
- https://github.com/KatrielMoses/voidaccess