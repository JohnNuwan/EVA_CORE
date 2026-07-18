---
name: hardware-security-firmware
description: "Sécuriser les équipements et micrologiciels industriels embarqués : Secure Boot, racine de confiance (Root of Trust), module HSM/TPM, signatures de firmware, mises à jour OTA sécurisées, et déploiement des versions sécurisées des protocoles (OPC UA Security, Modbus/TCP Security, CIP Security)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [hardware-security, firmware, secure-boot, opc-ua-security, modbus-security, cip-security, cryptography, industrial-security, hsm, tpm, root-of-trust, iot-security, ota-update]
    related_skills: [ot-security, cybersecurity-iec62443, embedded-systems-firmware]
    difficulty: advanced
    industry_sectors: [manufacturing, energy, oil-gas, water-treatment, critical-infrastructure, iot, defense, aerospace]
---

# Sécurisation Matérielle et Cryptographie Embarquée Industrielle

## Vue d'ensemble

Cette compétence guide la sécurisation physique et logique des équipements industriels embarqués : automates (PLC), passerelles IoT, capteurs intelligents, contrôleurs de mouvement, IHM, variateurs de vitesse, et tout dispositif connecté en environnement OT (Operational Technology).

### Contexte : Menaces sur le Matériel Industriel

Les attaquants ciblant le monde industriel cherchent de plus en plus à :

1. **Injecter des micrologiciels malveillants** (firmware tampering) dans les automates ou les passerelles IoT pour prendre le contrôle du process ou espionner les données.
2. **Intercepter et modifier les flux réseau** (Man-in-the-Middle) entre les automates et les systèmes de supervision (SCADA).
3. **Voler des clés cryptographiques** ou des certificats pour usurper l'identité d'équipements légitimes.
4. **Provoquer des dénis de service** (DDoS) sur les réseaux industriels en exploitant des vulnérabilités de protocole.

Des attaques célèbres illustrent ces menaces :
- **Stuxnet (2010)** : Modification du firmware des variateurs de fréquence Siemens S7-300 via des clés numériques volées.
- **TRITON (2017)** : Injection de code malveillant dans un automate de sécurité Schneider Triconex via le firmware de communication.
- **Industroyer (2016)** : Attaque ciblant les protocoles IEC 60870-5-104 et IEC 61850 sur des postes électriques.

### Piliers Fondamentaux de la Sécurisation Matérielle

1. **Racine de confiance matérielle (Hardware Root of Trust)** : Point de départ de toute chaîne de vérification cryptographique, ancré dans le matériel (firmware en ROM, clé publique en OTP).
2. **Démarrage sécurisé (Secure Boot)** : Vérification de l'intégrité et de l'authenticité de chaque étape du démarrage (bootloader → noyau OS → applications) avant exécution.
3. **Stockage sécurisé des clés** : Utilisation de modules matériels dédiés (HSM, TPM, élément sécurisé) pour protéger les clés cryptographiques.
4. **Communications sécurisées** : Versions sécurisées des protocoles industriels intégrant chiffrement, authentification et contrôle d'intégrité.
5. **Mise à jour sécurisée du firmware** (OTA) : Mécanismes de signature cryptographique pour empêcher l'injection de firmware malveillant.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Mettre en œuvre le **démarrage sécurisé (Secure Boot)** ou le **chiffrement de stockage** (TPM / HSM) sur une passerelle IoT, un automate ou un contrôleur embarqué.
- Configurer les **mécanismes de sécurité** d'un serveur ou client **OPC UA** (politiques de sécurité, échange de certificats X.509).
- Déployer des **protocoles sécurisés** comme **Modbus/TCP Security** (port 802/TLS), **CIP Security** (Rockwell), **Profinet Security**, **IEC 62351**.
- Concevoir un **mécanisme de mise à jour sécurisée du firmware (OTA)** avec signature cryptographique (ECDSA ou RSA) et vérification avant installation.
- Sécuriser les **ports de débogage physiques** (JTAG, SWD, UART) en production.
- Réaliser un **audit de sécurité du firmware** d'un équipement embarqué.

## 1. Protocoles Industriels Sécurisés vs Standards

| Protocole | Standard | Sécurisé | Port (Std → Sec) | Mécanisme de Sécurisation |
|:---|---|:---|:---:|:---|
| **OPC UA** | UA-TCP binaire | OPC UA Security | 4840 → 4843 | TLS 1.3 + Certificats X.509 PKI, Signature + Chiffrement AES-256-GCM |
| **Modbus/TCP** | Modbus/TCP | Modbus/TCP Security | 502 → 802 | TLS 1.3, Authentification par certificat |
| **EtherNet/IP (CIP)** | EtherNet/IP | CIP Security | 44818 → 2221/2222 | TLS / DTLS, protection anti-spoofing |
| **Profinet IO** | Profinet RT | Profinet Security (Option M) | Natif | Authentification + Intégrité + Chiffrement (IEC 62443) |
| **IEC 61850** | MMS/GOOSE | IEC 62351 | Natif | TLS + Signatures numériques GOOSE, anti-replay |
| **MQTT** | MQTT | MQTTS | 1883 → 8883 | TLS + Token d'authentification |

### Configuration Recommandée OPC UA

| SecurityPolicy | Description | Recommandation |
|:---|---|:---:|
| `None` | Aucune sécurité | Jamais en production |
| `Basic128Rsa15` | AES-128, RSA-15 | Minimum acceptable (obsolète) |
| `Basic256Sha256` | AES-256, SHA-256, RSA-OAEP | Recommandé |
| `Aes256Sha256RsaPss` | AES-256, SHA-256, RSA-PSS | Maximum — Haute sécurité |

## 2. Architecture de Démarrage Sécurisé (Secure Boot)

### Chaîne de Confiance (Chain of Trust)

```text
┌─────────────────────────────────────────────────────────────────────┐
│                   HARDWARE ROOT OF TRUST (ROT)                     │
│       Clé publique du fabricant gravée en ROM / OTP (one-time)    │
│       Immuable après la fabrication, infalsifiable                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│             BOOTLOADER (1er étage — immuable ROM)                  │
│   • Vérifie la signature du bootloader secondaire                   │
│   • Utilise la clé publique ROT (RSA-4096 ou ECDSA P-384)          │
│   • Si signature invalide → BLOCK (arrêt, LED erreur)             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              BOOTLOADER (2ème étage — signé)                       │
│   • Vérifie la signature du noyau (kernel) Linux / RTOS              │
│   • Vérifie la signature du filesystem racine (rootfs)             │
│   • Vérifie la signature de chaque application avant exécution     │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│              APPLICATIONS & FIRMWARE                                │
│   • Signé avec la clé privée du fabricant                             │
│   • Vérifié avant chaque exécution (Signed Executables)             │
│   • Mesure de l'état (attestation) via TPM PCR registers           │
└─────────────────────────────────────────────────────────────────────┘
```

### Composants Matériels de Sécurité

| Composant | Technologie | Rôle |
|:---|---|:---|
| **ROT** (Root of Trust) | ROM + OTP fuses | Stocke la clé publique racine. Impossible à modifier après programmation |
| **TPM 2.0** (Trusted Platform Module) | Puce dédiée (Infineon SLB9670, Nuvoton NPCT75X) | Mesure d'intégrité (PCR), génération et stockage de clés, attestation à distance |
| **HSM** (Hardware Security Module) | Module dédié (nCipher, Thales, Utimaco) | Génération/stockage de clés haute sécurité, signature accélérée |
| **Élément sécurisé** (SE) | Puce dédiée (Microchip ATECC608A, Infineon OPTIGA) | Stockage de clés inviolable, authentification matérielle, anti-clonage |

### Étapes de Mise en Œuvre

1. **Génération des clés** : Paire RSA-4096 ou ECDSA P-384. La clé privée est stockée dans un HSM ou un coffre-fort hautement sécurisé (pas de fichier sur poste de développement).
2. **Programmation OTP** : Graver la clé publique dans les OTP fuses du microcontrôleur lors de la fabrication.
3. **Signature du firmware** : Tous les binaires (bootloader, noyau, rootfs, applications) signés avant déploiement.
4. **Activation du Secure Boot** : Configurer le bootloader pour vérifier chaque signature.
5. **Désactivation des ports de débogage** : JTAG, SWD, UART debug désactivés ou protégés par mot de passe en production.

## 3. Mise à Jour Sécurisée du Firmware (OTA)

### Processus de Mise à Jour Type

```text
1. SERVEUR OTA → ÉQUIPEMENT : Annonce de mise à jour disponible
   (version, taille, hash SHA-256, URL de téléchargement)

2. ÉQUIPEMENT → SERVEUR OTA : Téléchargement du firmware via TLS
   (HTTPS ou MQTTS)

3. VÉRIFICATION INTERNE :
   a. Hash SHA-256 reçu == SHA-256 annoncé ?
   b. Signature vérifiée : openssl dgst -verify pubkey.pem -signature fw.sig firmware.bin ?
   c. Version > version courante (pas de downgrade sous version minimale de sécurité) ?

4. INSTALLATION :
   a. Copie du nouveau firmware dans la partition inactive (A/B swap)
   b. Mise à jour de la table de démarrage

5. REDÉMARRAGE sur la nouvelle partition

6. ATTESTATION POST-DÉMARRAGE :
   a. Le Secure Boot vérifie la signature du nouveau firmware
   b. Rapport d'attestation envoyé au serveur OTA (TPM quote)
```

### Anti-Rollback Protection

Pour empêcher un attaquant de rejouer une ancienne version vulnérable du firmware, la version minimale autorisée (Minimum Security Version / MSV) est stockée en mémoire OTP. Le bootloader vérifie que la version installée ≥ MSV avant d'autoriser le démarrage.

## Pièges Courants (Common Pitfalls)

1. **Génération de clés cryptographiques faibles ou prévisibles :**
   - *Erreur :* Utiliser une fonction de génération de nombres aléatoires standard (ex : `rand()` en C ou `random` en Python) pour créer des clés de session ou des clés cryptographiques. Les clés générées sont prévisibles, ce qui permet à un attaquant de casser la liaison.
   - *Correction :* Utiliser exclusivement le générateur de nombres aléatoires matériels (**TRNG — True Random Number Generator**) intégré au microcontrôleur (ex : RNG du STM32, du i.MX8) ou fourni par le module de sécurité matériel (TPM/HSM). En environnement de développement, utiliser `/dev/urandom` (Linux) ou `CryptGenRandom` (Windows).

2. **Certificats X.509 expirés ou non surveillés :**
   - *Erreur :* Déployer des connexions OPC UA chiffrées avec des certificats auto-signés d'une validité de 10 ans sans mécanisme de révocation (CRL/OCSP) ou de renouvellement automatique. Si la clé privée d'un équipement est compromise, la liaison reste valide jusqu'à l'expiration du certificat (10 ans).
   - *Correction :* Mettre en place une infrastructure à clé publique (PKI) industrielle avec un serveur de gestion des certificats (ex : EJBCA, Smallstep CA, Microsoft ADCS). Utiliser des protocoles d'enrôlement automatique (EST RFC 7030, SCEP pour les équipements légers) pour renouveler régulièrement les certificats (validité recommandée : 1 à 2 ans). Planifier la révocation immédiate en cas de compromission connue.

3. **Ports de débogage (JTAG/SWD) laissés actifs en production :**
   - *Erreur :* Laisser les ports JTAG ou SWD du microcontrôleur actifs sur le produit final livré chez le client. Un attaquant ayant un accès physique peut lire la mémoire flash (vol d'algorithme, extraction de clés), modifier le firmware, ou arrêter le processeur.
   - *Correction :* Activer les fusibles de déconnexion JTAG/SWD (ex : RDP Level 2 sur STM32, eFuse sur i.MX) après la programmation en usine. Vérifier que la désactivation est irréversible. Pour les équipements qui nécessitent un débogage ponctuel en maintenance, protéger l'accès par un mot de passe (ex : méthode de verrouillage JTAG de la norme IEEE 1149.1).

4. **Chiffrement asymétrique utilisé pour le chiffrement des données :**
   - *Erreur :* Utiliser le chiffrement asymétrique (RSA directement) pour chiffrer les données du firmware en vol. Le chiffrement asymétrique est bien trop lent pour de grandes quantités de données et les opérations de signature/chiffrement sont différentes.
   - *Correction :* Utiliser une approche hybride : chiffrer le firmware avec un algorithme symétrique (AES-256-GCM) et chiffrer la clé symétrique avec la clé publique RSA (hybrid encryption). Pour la signature, utiliser une paire de clés asymétrique **différente** de celle utilisée pour le chiffrement (séparation des usages : signature ≠ chiffrement).

## Références

- **IEC 62443-4-1** : Secure Product Development Lifecycle Requirements (inclut Secure Boot, key management).
- **IEC 62443-4-2** : Technical Security Requirements for IACS Components.
- **OPC UA Specification Part 2** : Security Model (OPC 10000-2).
- **NIST SP 800-57** : Recommendation for Key Management.
- **NIST SP 800-193** : Platform Firmware Resiliency Guidelines.
- **GlobalPlatform TEE** : Spécifications pour l'exécution sécurisée.
- **TPM 2.0 Library Specification (ISO/IEC 11889)** : Trusted Platform Module.
- **IETF RFC 7030** : Enrollment over Secure Transport (EST) pour les certificats.

## Liste de vérification (Checklist)

- [ ] Les **micrologiciels** envoyés aux équipements possèdent une **signature cryptographique valide** vérifiée par le Secure Boot avant exécution (chaîne complète ROT → bootloader → kernel → applications).
- [ ] **Aucun mot de passe ou clé privée** n'est stocké en texte brut dans la mémoire flash générale. Utiliser des zones OTP protégées, un TPM, ou un élément sécurisé externe (ATECC608A, OPTIGA).
- [ ] Les **ports de débogage physique** (JTAG / SWD / UART) sont désactivés définitivement (fusible de sécurité) ou protégés par mot de passe en production.
- [ ] Les **liaisons OPC UA ou CIP Security** utilisent des algorithmes de chiffrement robustes (AES-256-GCM, RSA-3072 ou courbes elliptiques P-384) et rejettent explicitement les connexions avec la politique `None`.
- [ ] Le **Watchdog temporel** de communication de sécurité est activé sur les connexions OT pour détecter les attaques par déni de service.
- [ ] Les **certificats X.509** ont une durée de validité ≤ 2 ans et sont renouvelés via une PKI interne (EST/SCEP). Un mécanisme de révocation (CRL/OCSP) est en place.
- [ ] La **mise à jour OTA** est sécurisée : téléchargement par TLS, vérification de signature et de hash, anti-rollback (MSV en OTP), partition A/B redondante.
- [ ] Les **clés privées** du fabricant sont stockées exclusivement dans un HSM (Hardware Security Module) certifié FIPS 140-2 Level 3 ou supérieur.
- [ ] Les **mises à jour de sécurité** du firmware sont planifiées et testées en pré-production avant déploiement sur le parc.
- [ ] Une **analyse de vulnérabilités** du firmware (analyse statique + dynamique) est réalisée au moins une fois par an ou à chaque version majeure.

