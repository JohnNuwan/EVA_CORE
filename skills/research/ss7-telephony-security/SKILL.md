---
name: ss7-telephony-security
description: Compétence niveau expert en sécurité téléphonique — SS7, LTE/5G core, IMSI catchers, interception, VoIP, et OSINT téléphonique.
category: research
---

# Sécurité Téléphonique & SS7 — Interception, Localisation, Spoofing

## Architecture SS7 / SIGTRAN
- **SS7 (Signaling System 7)** : MTP (1-3), SCCP, TCAP, MAP, ISUP, INAP, CAP
- **Points du réseau** : SSP (central), STP (routage), SCP (base données), HLR, VLR, MSC, GMSC, SMSC
- **SIGTRAN** : SS7 over IP (M3UA, M2PA, SUA, SCTP)
- **Global Title (GT)** : Routage par numéro, adresse de point de signalisation
- **Vulnérabilité** : Aucune authentification dans le réseau SS7 — tout point du réseau est intrinsèquement fiable

## Attaques SS7 classiques
- **SMS Interception** : MAP_SEND_ROUTING_INFO_FOR_SM → SMS intercepté
- **Localisation** : MAP_ANY_TIME_INTERROGATION, MAP_PROVIDE_SUBSCRIBER_INFO → position GPS + cellule
- **Détournement d'appel** : MAP_INSERT_SUBSCRIBER_DATA → modification du HLR pour rediriger les appels
- **Déni de service** : MAP_CANCEL_LOCATION → déconnexion forcée du réseau
- **Fraude roaming** : Fake MSC → appels aux frais de la victime
- **Écoute passive** : Routage via un point d'interception

## Attaques GTP (2G/3G/4G)
- **Fake MSC** : Usurpation d'un MSC pour intercepter le roaming
- **GTP-C/GTP-U** : Injection de messages de contrôle, redirection de données
- **Attaque par tunnel** : Interception entre SGSN et GGSN

## IMSI Catchers
- **Principe** : Fausse station de base BTS (2G) → force le téléphone à s'y connecter (puissance signal)
- **Stingray (Harris)** : IMSI catcher commercial, intercepte appels/SMS, localise
- **USRP (Ettus)** : SDR (Software Defined Radio) pour implémenter un IMSI catcher
- **BladeRF** : SDR petit format, programmable
- **YateBTS** : Logiciel BTS open-source avec USRP/BladeRF
- **OsmocomBB** : Pile protocolaire GSM open-source
- **OpenBSC** : Contrôleur de station de base open-source
- **Protection** : 4G/5G (mutual auth), A5/4 encryption, signalement d'IMSI catcher

## 5G Sécurité
- **Améliorations vs 4G** : Chiffrement intégral (AS + NAS), mutual auth plus forte, SUPI (IMSI chiffré en SUCI), SEPP (protection edge)
- **Failles restantes** : SS7 toujours accessible (interop 5G→4G→2G), downgrade attacks, GTP encore présent pour roaming
- **5G SA** : Core natif, NRF (Network Repository Function), SBI (Service Based Interface)
- **Attaques 5G** : N32 inter-roaming, SEPP bypass, fake gNB, AKA bypass

## VoIP & SIP
- **SIP attacks** : Registration hijacking, call hijacking, INVITE flooding, BYE injection, RTP injection
- **Vishing** : Voice phishing automatisé, caller ID spoofing
- **SPIT** : Spam over Internet Telephony
- **SBC** : Session Border Controller, protection anti-spoofing
- **Protocoles** : SIP, SDP, RTP, SRTP, ZRTP, WebRTC, MGCP, H.323

## OSINT Téléphonique
- **PhoneInfoga** : Scan international, formatage, Google dorks, footprinting — 17k★ GitHub
- **Truecaller** : Reverse lookup, base communautaire, API officielle (payante)
- **Alternatives** : Sync.me, Hiya, Numverify, Twilio Lookup, AbstractAPI
- **Messageries** : WhatsApp (302 = compte actif), Telegram, Signal, Viber, Messenger
- **Cross-ref réseaux sociaux** : Facebook, LinkedIn, Instagram, Twitter, Snapchat, Telegram
- **Détection fraude** : signal-arnaques.com, Bloctel (France), Have I Been Pwned, Dehashed
- **Numéros jetables** : 25+ plateformes détectables (TextNow, Burner, Google Voice, etc.)
- **Workflow** : Reconnaissance → recherche formatage → lookup → cross-ref → vérification

## Outils & Références
- **OsmocomBB** : osmocom.org, code source GitHub
- **YateBTS** : yatebts.com, projet Yate + YateBTS
- **OpenBSC** : openbsc.osmocom.org
- **PhoneInfoga** : github.com/sundowndev/phoneinfoga
- **Shodan** : Recherche d'équipements SS7/SIGTRAN exposés
- **Protocoles** : 3GPP TS 23.003 (numérotation), 3GPP TS 29.002 (MAP), 3GPP TS 33.501 (5G)