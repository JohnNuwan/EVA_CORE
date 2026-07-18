---
name: osint-pratique
description: >-
  Guide pratique OSINT avec tous les outils opérationnels dans Docker.
  PhoneInfoga, Sherlock, Holehe, TheHarvester, Nmap, ExifTool, Google Dorks.
  Méthodologie de recherche par numéro, email, username, domaine.
category: research
---

# OSINT Pratique — Guide Opérationnel

## Présentation

Ce skill documente les outils OSINT installés et opérationnels dans le conteneur
Docker `osint-trainer`, les workflows de recherche, et les limites légales/éthiques.
Complète les skills `osint-recherche` (théorie arXiv) et `osint-cyber-tools-platforms`
(référence outils).

## Conteneur Docker

```bash
# Build (si pas déjà fait)
docker build -t osint-trainer /tmp/osint-trainer/

# Outils disponibles
docker run --rm --entrypoint phoneinfoga osint-trainer scan -n "+336xxxxxxxx"
docker run --rm --entrypoint sherlock osint-trainer username
docker run --rm --entrypoint holehe osint-trainer email@example.com
docker run --rm --entrypoint theharvester osint-trainer -d example.com -b google
docker run --rm osint-trainer 0603625116  # script OSINT complet
```

### Outils installés

| Outil | Usage | Commande dans Docker |
|-------|-------|---------------------|
| PhoneInfoga v2 | Scan numéro téléphone | `--entrypoint phoneinfoga ... scan -n "+33..."` |
| Sherlock v0.16 | Recherche username (400+ sites) | `--entrypoint sherlock ... username` |
| Holehe | Vérification email (100+ sites) | `--entrypoint holehe ... email` |
| TheHarvester | Collecte emails/sous-domaines | `--entrypoint theharvester ... -d domain` |
| Nmap | Scan réseau | `--entrypoint nmap ...` |
| ExifTool | Métadonnées fichiers | `--entrypoint exiftool ...` |
| Instaloader | Extraction Instagram | `--entrypoint instaloader ...` |
| Dig/Whois | DNS/WHOIS | `--entrypoint dig ...` |

## Workflow OSINT Complet

### Par numéro de téléphone

1. **PhoneInfoga** : pays, opérateur d'origine, footprint OVH/VoIP
2. **Google Dorks** : `"0603625116" site:facebook.com`, `site:leboncoin.fr`, `filetype:pdf`
3. **API lookup** (si dispo) : numverify, twilio lookup
4. **Breach check** : haveibeenpwned.com, dehashed.com
5. **Messagerie** : WhatsApp, Signal, Telegram — vérifier si le numéro est enregistré
   → WhatsApp : `curl -sI "https://wa.me/+33..."` → HTTP 302 = enregistré
   → Telegram : `curl -sI "https://t.me/+33..."` → HTTP 200 = probablement

### Techniques de vérification des messageries

**WhatsApp** : WhatsApp confirme l'enregistrement SANS envoyer de message.
Une redirection HTTP 302 vers `api.whatsapp.com/send/` = compte actif.
Une erreur = pas de compte. Technique passive, sans interaction.

```bash
curl -sI "https://wa.me/+336xxxxxxxx" | grep -E "^HTTP|location"
# HTTP/2 302 → location: https://api.whatsapp.com/send/... → ENREGISTRÉ
# HTTP/2 404 → pas de compte WhatsApp
```

**Telegram** : Moins fiable. HTTP 200 peut signifier compte existant OU lien
public désactivé. À croiser avec d'autres sources.

**Limites Google** : Google bloque les requêtes curl/wget après 2-3 appels.
Même avec un User-Agent réaliste, les CAPTCHA apparaissent. Les outils
comme PhoneInfoga ne font que GÉNÉRER les URLs — ils ne les exécutent pas.

**Workarounds pour Google** :
- SerpAPI (100 req/mois gratuites)
- Navigateur headless (Playwright) avec cookies persistants
- Proxies résidentiels rotatifs
- `googlesearch-python` (pip) — limité à ~10 req avant CAPTCHA

## Limites et Éthique

1. **Holehe** : `holehe email@example.com` — vérifie 100+ sites
2. **HaveIBeenPwned** : API breaches
3. **Gravatar** : avatar public si configuré
4. **Google Dorks** : `"email@example.com" filetype:pdf`
5. **TheHarvester** : `theharvester -d domain.com -b google`

### Par username

1. **Sherlock** : `sherlock username` — vérifie 400+ réseaux sociaux
2. **WhatsMyName** : alternative à Sherlock
3. **Google Images** : photo de profil → reverse image search
4. **Wayback Machine** : archive.org pour anciens profils

### Par domaine

1. **Whois** : `whois domain.com`
2. **TheHarvester** : `theharvester -d domain.com -b all`
3. **DNSdumpster** : carte DNS
4. **Shodan** : `shodan host $(dig +short domain.com)`

## Limites et Éthique

- **Ne pas utiliser** pour du harcèlement, stalking, usurpation d'identité
- **Respecter** le RGPD : les données personnelles publiques restent protégées
- **Pas d'accès** aux bases de données privées (opérateurs, banques, état civil)
- **Portabilité** : depuis 2007, le préfixe mobile français n'indique plus l'opérateur actuel
- **Numéros non-indexés** : la plupart des mobiles français ne sont pas sur Google

## Cas concret : 0603625116 (session 2026-07-10)

- Pays : France
- Type : Mobile
- Opérateur d'origine : Orange (préfixe 0603)
- OVH/VoIP : Non (numéro mobile réel)
- **WhatsApp** : ✅ Enregistré (HTTP 302 confirmé)
- **Telegram** : ✅ Probable (HTTP 200)
- Indexé Google : Non (normal pour un mobile)
- Pastebin/LeakCheck : Aucune fuite trouvée
- Réseaux sociaux : Non trouvé (Google CAPTCHA)

Pour aller plus loin :
- Vérifier WhatsApp/Telegram/Signal si le numéro est enregistré
- Recherche manuelle Google avec les URLs générées
- Si email associé trouvé → holehe + breach lookup