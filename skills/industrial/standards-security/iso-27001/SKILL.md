---
name: iso-27001
description: "Concevoir, documenter et auditer un système de management de la sécurité de l'information (SMSI) conforme à ISO 27001, avec un focus sur la convergence IT/OT : politique de sécurité, analyse de risques, gestion des accès, segmentation réseau, télémaintenance sécurisée."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [iso-27001, information-security, smsi, cybersecurity, it-ot-convergence, industrial-standards, risk-analysis, access-control, network-segmentation, dmz, pssi]
    related_skills: [cybersecurity-iec62443, ot-security, industrial-networks-ot]
    difficulty: advanced
    industry_sectors: [manufacturing, energy, chemical, pharmaceutical, defense, aerospace, critical-infrastructure]
---

# Cybersécurité IT/OT & Norme ISO 27001

## Vue d'ensemble

La norme **ISO 27001** (version actuelle : ISO/IEC 27001:2022) spécifie les exigences pour la mise en place, la mise en œuvre, la tenue à jour et l'amélioration continue d'un système de management de la sécurité de l'information (SMSI). Historiquement axée sur l'informatique d'entreprise (IT), elle englobe désormais pleinement la sécurité des systèmes industriels (OT — Operational Technology).

### Contexte : La Convergence IT/OT

La convergence IT/OT (liaison des automates, SCADA et capteurs aux bases de données d'entreprise, aux ERP et aux réseaux bureautiques) expose l'usine à des cyber-risques majeurs : ransomwares, sabotages industriels, espionnage, déni de service. De nombreuses attaques récentes (NotPetya (2017) sur Maersk/Mondelez, Colonial Pipeline (2021), groupe industriel français (2022)) ont démontré que la sécurité OT n'est plus une option.

L'intégration de l'ISO 27001 en milieu industriel repose sur les piliers suivants :

1. **L'inventaire des actifs industriels (Asset Inventory)** : Connaître tous les automates, IHM, PC de supervision, commutateurs réseau, serveurs SCADA, passerelles IoT et leurs versions de firmware.
2. **La gestion des accès (Access Control)** : Restreindre l'accès physique et logique aux équipements critiques (armoires électriques, salles serveurs, consoles de programmation).
3. **La segmentation réseau (Network Segmentation)** : Séparer le réseau de bureau (IT) du réseau de production (OT) via une DMZ (Zone Démilitarisée) conforme au modèle Purdue (ISA-95).
4. **La gestion des connexions à distance** : Sécuriser les accès de télémaintenance des prestataires externes (intégrateurs, constructeurs) via des VPNs avec authentification multifacteur (MFA).
5. **La gestion des vulnérabilités** : Suivi des CVE affectant les équipements industriels et plan de correction adapté au contexte OT.

### Structure de l'ISO 27001:2022

La version 2022 de la norme repose sur :

- **4 thèmes de l'Annexe A** : Organisation (37 contrôles), Personnes (8 contrôles), Physique (14 contrôles), Technologique (34 contrôles).
- **93 contrôles** au total (contre 114 dans la version 2013).
- **Structure HLS** (High Level Structure) commune à toutes les normes ISO de système de management (ISO 9001, ISO 14001, ISO 45001).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :

- De structurer une **politique de sécurité des systèmes d'information (PSSI)** applicable au réseau d'usine (OT) comme au réseau d'entreprise (IT).
- De concevoir des **règles de pare-feu** ou des **architectures de DMZ industrielle** conformes à la norme.
- De rédiger des **procédures de gestion des mots de passe** des automates, IHM et serveurs SCADA (suppression des identifiants par défaut, rotation).
- D'aligner la sécurité des données industrielles avec les **93 contrôles de l'annexe A de l'ISO 27001:2022**.
- De réaliser une **analyse de risques** (Risk Assessment) pour un système industriel (méthode EBIOS RM, ISO 27005, ou méthode simplifiée).
- De préparer un **audit de certification ISO 27001** pour un site ou un groupe industriel.

**Ne pas utiliser pour :**
- La configuration détaillée d'un pare-feu spécifique (comme Cisco ASA, Fortinet, ou MGuard) — utiliser `industrial-networks-ot`.
- Les aspects de cybersécurité purement OT (IEC 62443) — utiliser `cybersecurity-iec62443`.

## 1. Architecture Réseau Sécurisée IT/OT (DMZ Industrielle)

Conformément à l'ISO 27001 (contrôle A.8.22 : Séparation des réseaux) et aux modèles industriels (Purdue Model / ISA-95), les flux de données ne doivent jamais passer directement de l'automate (Niveau 1/2) au réseau d'entreprise (Niveau 4). On implémente une DMZ (Niveau 3.5).

```text
         [ RÉSEAU ENTREPRISE - IT (Niveau 4) ]
         ┌─────────────────────────────────────┐
         │  • Serveur ERP (SAP, Dynamics)      │
         │  • Annuaire Active Directory        │
         │  • Serveur de messagerie            │
         │  • Postes bureautiques              │
         └──────────────────┬──────────────────┘
                            │
                    [ PARE-FEU IT/OT ]
                    • Règles restrictives (allow-list)
                    • Inspection stateful
                    • Journalisation des connexions
                            │
         [ DMZ INDUSTRIELLE — Niveau 3.5 ]
         ┌─────────────────────────────────────┐
         │  • Serveur Historian (réplication)  │
         │  • Serveur OPC-UA Gateway            │
         │  • Serveur VPN télémaintenance (MFA)│
         │  • Serveur d'authentification local │
         └──────────────────┬──────────────────┘
                            │
                    [ PARE-FEU OT ]
                    • ACL par adresse IP source
                    • Ports industriels seulement
                    • Détection d'intrusion IDS
                            │
         [ RÉSEAU DE PRODUCTION - OT (Niveau 2/3) ]
         ┌─────────────────────────────────────┐
         │  • PC de supervision SCADA          │
         │  • Serveur MES                       │
         │  • Bases de données locales          │
         │  • Automates API (Niveau 1)          │
         └─────────────────────────────────────┘
```

### Règle Fondamentale d'Échange de Données dans la DMZ

Les bases de données d'usine poussent leurs données (Push) vers la DMZ par un mécanisme de réplication unidirectionnelle. Les serveurs IT interrogent uniquement la base répliquée dans la DMZ. **Aucun serveur IT n'a le droit d'initier une connexion directe vers le réseau de production (OT).**

| Sens de flux | Source | Destination | Protocole autorisé | Port |
|:---|:---|:---|---:|:---:|
| Push | Historien OT | DMZ Historien | ODBC / SQL | 1433 |
| Pull | Serveur IT | DMZ Historien | ODBC / SQL | 1433 |
| Accès distant | VPN client | Jump Host DMZ | RDP / SSH | 3389 / 22 |
| Mise à jour firmware | DMZ Patch | Serveur OT | SMB / HTTPS | 445 / 443 |

## 2. Analyse de Risques selon ISO 27005 / EBIOS RM

L'analyse de risques est le cœur du SMSI. La méthode recommandée pour les environnements industriels est **EBIOS Risk Manager** (ANSSI) ou la méthode simplifiée ci-dessous :

### Grille de Cotation des Risques

| Niveau de Gravité ($G$) | Description | Niveau de Probabilité ($P$) | Description |
|:---:|---|:---:|---|
| 1 | Impact négligeable (ex : arrêt < 30 min) | 1 | Très improbable (jamais observé) |
| 2 | Impact mineur (arrêt < 4h, perte limitée) | 2 | Improbable (une fois en 5 ans) |
| 3 | Impact significatif (arrêt < 24h) | 3 | Possible (une fois par an) |
| 4 | Impact majeur (arrêt > 1 semaine, dommage matériel) | 4 | Probable (plusieurs fois par an) |
| 5 | Impact catastrophique (arrêt définitif, explosion, perte de vie) | 5 | Très probable (chaque mois) |

**Niveau de risque $R = P \times G$ :**
- $R \leq 6$ : Risque faible — acceptable sous surveillance.
- $7 \leq R \leq 12$ : Risque moyen — action planifiée dans les 6 mois.
- $R \geq 13$ : Risque élevé — action prioritaire immédiate.

### Exemple d'Analyse de Risques OT

| Actif | Menace | Vulnérabilité | $P$ | $G$ | $R$ | Traitement |
|:---|---|---|:---:|:---:|:---:|---|
| Automate ligne 1 | Ransomware propagé via IT | Absence de segmentation IT/OT | 3 | 5 | 15 | Mettre en place une DMZ et un pare-feu IT/OT |
| SCADA | Accès non autorisé distant | Mot de passe par défaut, pas de MFA | 4 | 4 | 16 | Changer les mots de passe, activer MFA |
| PC supervision | Mise à jour non contrôlée | Windows Update automatique activé | 3 | 3 | 9 | Grouper les mises à jour, tester en pré-prod |
| Switch OT | Accès physique non maîtrisé | Armoire électrique non fermée à clé | 3 | 2 | 6 | Cadenasser les armoires, contrôle d'accès badge |
| Firmware PLC | Injection de code malveillant | Pas de signature de firmware | 2 | 5 | 10 | Mettre en place Secure Boot et signature |

## 3. Contrôle d'Accès et Gestion des Identités (Annexe A — Thème Personnes)

En milieu industriel, la gestion des accès est critique. Les opérateurs, techniciens de maintenance et prestataires externes ont besoin d'accès différents.

| Rôle | Accès réseau | Accès aux automates | Accès SCADA | Accès physique |
|:---|---|:---:|:---:|:---:|
| Opérateur de production | Poste opérateur uniquement | Aucun | Visualisation (lecture seule) | Atelier, ligne |
| Technicien maintenance | Poste maintenance + console portable | Programmation (TIA, Studio 5000) | Visualisation + modification paramètres | Armoires, automates |
| Ingénieur production | Poste ingénieur | Visualisation programme | Configuration SCADA | Salle serveur (sur validation) |
| Prestataire externe | VPN + Jump Host uniquement | Session temporaire monitorée | Aucun | Accompagné |
| Administrateur système | Tous | Tous | Lecture seule + maintenance | Salle serveur |

### Règles de Gestion des Mots de Passe

1. **Changement systématique** des mots de passe par défaut sur tous les équipements (automates, IHM, switches, caméras) avant mise en service.
2. **Complexité minimale** : 12 caractères, majuscules + minuscules + chiffres + caractères spéciaux.
3. **Rotation** : Tous les 90 jours pour les comptes administrateurs, tous les 180 jours pour les comptes utilisateurs.
4. **Stockage sécurisé** : Utiliser un coffre-fort de mots de passe (KeePass, Bitwarden, CyberArk) — pas de fichier Excel non protégé.

## Pièges Courants (Common Pitfalls)

1. **Identifiants par défaut conservés sur les équipements d'usine :**
   - *Erreur :* Laisser les mots de passe par défaut (ex : `admin`/`admin`, `1234`, `root`/`root`, `Siemens`) sur des commutateurs industriels, des caméras IP, des IHM tactiles ou des automates. Un attaquant connecté au réseau local peut prendre le contrôle total du process en quelques secondes en utilisant des listes de mots de passe par défaut publiques (ex : CIRT.net, Scada StrangeLove).
   - *Correction :* Désactiver les comptes par défaut au démarrage et imposer une politique de mots de passe robustes. Utiliser un coffre-fort de mots de passe centralisé avec traçabilité des accès.

2. **Mises à jour automatiques sur les PC de supervision :**
   - *Erreur :* Autoriser Windows Update (ou tout autre mécanisme de mise à jour automatique) à redémarrer un PC de supervision SCADA en pleine production. Un redémarrage non planifié peut interrompre la surveillance d'un procédé critique pendant plusieurs heures.
   - *Correction :* Désactiver les mises à jour automatiques directes via GPO ou registre. Centraliser la gestion des mises à jour via un serveur WSUS / SCCM en mode manuel. Valider et installer les correctifs de sécurité (patches) pendant les arrêts de production planifiés, après test en pré-production.

3. **Absence de DMZ et flux directs IT → OT :**
   - *Erreur :* Permettre à un serveur ERP d'interroger directement une base de données d'historien située sur le réseau OT, ou autoriser un ingénieur à se connecter depuis un poste IT directement en RDP sur un PC SCADA.
   - *Correction :* Implémenter une DMZ industrielle. Tous les flux inter-réseaux doivent transiter par la DMZ et être filtrés par un pare-feu. Aucun flux direct IT vers OT n'est autorisé.

4. **Documentation de sécurité absente ou obsolète :**
   - *Erreur :* Disposer d'une PSSI qui date de 5 ans, d'un inventaire des actifs jamais mis à jour, et d'aucun schéma réseau documenté. En cas d'incident, personne ne sait quel équipement est critique ni où se trouvent les sauvegardes.
   - *Correction :* Mettre en place un processus de revue annuelle de toute la documentation de sécurité. L'inventaire des actifs doit être maintenu en continu (outil de découverte de réseau type Lansweeper, ou scan régulier).

## Références

- **ISO/IEC 27001:2022** : Exigences pour un SMSI.
- **ISO/IEC 27002:2022** : Code de bonnes pratiques pour les mesures de sécurité (93 contrôles détaillés).
- **ISO/IEC 27005:2022** : Gestion des risques de sécurité de l'information.
- **EBIOS Risk Manager (ANSSI)** : Méthode d'analyse de risques française.
- **NIST SP 800-53 Rev.5** : Security and Privacy Controls for Information Systems.
- **NIST Cybersecurity Framework (CSF) 2.0** : Framework for Improving Critical Infrastructure Cybersecurity.
- **Guide ANSSI pour la sécurisation des systèmes industriels** : https://www.ssi.gouv.fr/guide/cybersecurite-des-systemes-industriels/

## Liste de vérification (Checklist)

- [ ] Un **pare-feu** sépare physiquement ou logiquement le réseau de bureau (IT) du réseau de production (OT) conformément à l'annexe A.8.22.
- [ ] **Aucun équipement** de la DMZ ou du réseau IT ne peut initier une connexion directe vers un automate (principe de flux unidirectionnel).
- [ ] Les **connexions à distance** des techniciens externes passent par une passerelle VPN sécurisée avec authentification multifacteur (MFA) et session journalisée.
- [ ] **L'inventaire des actifs** (matériels, logiciels, firmware) est complet, horodaté et mis à jour au moins une fois par an.
- [ ] Les **mots de passe par défaut** des équipements OT sont changés et les comptes par défaut désactivés.
- [ ] Une **analyse de risques** (Risk Assessment) formelle a été réalisée pour le périmètre OT et IT selon une méthode reconnue (EBIOS RM, ISO 27005).
- [ ] La **PSSI** (Politique de Sécurité des Systèmes d'Information) est approuvée par la direction, communiquée et accessible à tous les utilisateurs.
- [ ] Les **sauvegardes** des configurations et données critiques sont réalisées automatiquement, stockées hors ligne et testées (restauration) au moins une fois par an.
- [ ] Un **plan de réponse aux incidents** (PRI / Incident Response Plan) couvrant les scénarios OT (ransomware, déni de service, sabotage) est documenté.
- [ ] Les **audits internes** ISO 27001 sont programmés selon un cycle annuel et les non-conformités sont suivies jusqu'à leur clôture.

