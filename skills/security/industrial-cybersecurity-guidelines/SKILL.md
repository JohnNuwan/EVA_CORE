---
name: industrial-cybersecurity-guidelines
description: "Sécuriser les réseaux industriels et les systèmes OT/IT connectés : segmentation IEC 62443, authentification forte, monitoring IDS/IPS, plans de réponse aux incidents."
version: 1.1.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [security, ot, cybersecurity, iec62443, nist, iso27001, ids, ips, scada, industrial]
    related_skills: [combining-industry40-security-iso, iso-standards-for-industry, cybersecurity-iec62443]
---

# Cybersécurité Industrielle — Guide de Sécurisation OT/IT

## Vue d'ensemble

Cette compétence fournit des **lignes directrices complètes** pour la sécurisation des systèmes industriels (OT) et leur interconnexion avec les systèmes informatiques (IT). Elle couvre l'implémentation des normes IEC 62443, la gestion des risques OT, la segmentation réseau, l'authentification, le monitoring IDS/IPS, et la planification de réponse aux incidents de cybersécurité.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De sécuriser un réseau OT existant ou de concevoir une architecture sécurisée.
- D'implémenter la norme IEC 62443 (zones et conduits).
- De configurer un IDS/IPS pour le trafic industriel.
- D'auditer la maturité cyber d'un site de production.
- De préparer un plan de réponse aux incidents OT.

---

## 1. Normes et Standards Clés

| Norme | Domaine | Points Clés |
|:---|:---|:---|
| **IEC 62443** | Sécurité IACS (Industrial Automation & Control Systems) | Zones et conduits, niveaux de sécurité (SL1–SL4), cycle de vie sécurisé |
| **NIST CSF** | Cybersécurité générale | Identify, Protect, Detect, Respond, Recover |
| **ISO 27001** | Sécurité de l'information (IT) | SMSI, annexe A contrôles |
| **CIS Controls** | Sécurité opérationnelle | 18 contrôles prioritaires |
| **ANSSI (France)** | Sécurité OT nationale | Guide de sécurisation des systèmes industriels |

---

## 2. Stratégies de Sécurité

### 2.1 Segmentation Réseau selon IEC 62443

Le principe fondamental est la **défense en profondeur** avec des zones et des conduits :

```
┌─────────────────────────────────────────┐
│         ZONE IT (Bureau)                │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │ERP  │ │AD   │ │File │               │
│  └─────┘ └─────┘ └─────┘               │
└──────────────┬──────────────────────────┘
               │ Pare-feu IT/OT (conduit)
┌──────────────┴──────────────────────────┐
│        ZONE OT DE CONTRÔLE              │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │SCADA│ │MES  │ │Hist.│               │
│  └─────┘ └─────┘ └─────┘               │
└──────────────┬──────────────────────────┘
               │ Pare-feu OT
┌──────────────┴──────────────────────────┐
│        ZONE OT DE TERRAIN               │
│  ┌─────┐ ┌─────┐ ┌─────┐               │
│  │PLC  │ │VSD  │ │HMI  │               │
│  └─────┘ └─────┘ └─────┘               │
└─────────────────────────────────────────┘
```

### 2.2 Authentification et Contrôle d'Accès

```yaml
Mesures d'authentification recommandées:
  Accès distant:
    - VPN (OpenVPN, WireGuard) avec certificats X.509
    - Jump host / bastion avec MFA
    - Session logging obligatoire
  
  Accès local:
    - Authentification forte sur les HMIs (MFA si possible)
    - Comptes individuels (pas de compte partagé "admin")
    - Rotation des mots de passe tous les 90 jours
    - Verrouillage de session après 5 minutes d'inactivité

  Machines (M2M):
    - Certificats pour OPC-UA et MQTTS
    - Clés pré-partagées pour Modbus (VPN obligatoire)
```

## 3. Monitoring et Détection d'Intrusion

### 3.1 IDS Industriels

Déployez un **IDS réseau** capable d'analyser les protocoles industriels :

- **Suricata** avec règles personnalisées pour Modbus, OPC-UA, DNP3.
- **Zeek (ex-Bro)** pour l'analyse de trafic OT.
- **OT-Base** (Dragos, Nozomi, Claroty) pour la détection spécifique OT.

**Configuration Suricata pour Modbus :**

```bash
# Règle Suricata pour détecter une écriture Modbus non autorisée
alert modbus any any -> $PLC_NETWORK 502 \
  (msg:"Écriture Modbus non autorisée sur PLC"; \
   content:"|00 00 00 00 00 06 01 06|"; depth:8; \
   sid:1000001; rev:1;)
```

### 3.2 SIEM Centralisé

```yaml
Architecture SIEM OT:
  Collecteurs:
    - Logs pare-feu (IT/OT)
    - Logs PLC (Syslog via OPC-UA)
    - Alertes IDS (Suricata, Zeek)
    - Logs d'authentification (VPN, AD)
  Corrélation:
    - Règles de corrélation spécifiques OT
    - Détection d'anomalies comportementales
    - Alertes de sécurité + qualité (pipeline combiné)
  Tableau de bord:
    - État des zones IEC 62443
    - Nombre d'alertes par niveau de criticité
    - Temps moyen de détection (MTTD) et de réponse (MTTR)
```

---

## 4. Plan de Réponse aux Incidents OT

### 4.1 Phases de Réponse

1. **Détection** : Alerte via IDS/SIEM ou signalement opérateur.
2. **Confinement** : Isoler la zone compromise (coupe réseau logique ou physique).
3. **Éradication** : Analyse forensique, retrait du malware, restauration de la configuration sûre.
4. **Rétablissement** : Remise en service après validation de la non-contamination.
5. **Retour d'expérience** : Mise à jour des règles, correctifs, formation.

### 4.2 Procédure d'Urgence Type

```
[ALERTE] Anomalie détectée sur le réseau OT
    ↓
1. Confirmer l'alerte avec l'opérateur (faux positif ?)
    ↓ si confirmé
2. Basculer le système en mode dégradé (manuel si possible)
3. Isoler la zone suspecte (coupe réseau)
4. Contacter l'équipe cyber OT + responsable de production
5. Analyse forensique (logs, captures réseau)
6. Décision : reprise ou arrêt prolongé
7. Retour d'expérience sous 48h
```

---

## 5. Pièges Courants

1. **Dépendance à un seul mot de passe :**
   - *Erreur* : Un mot de passe partagé pour tout le site (ex: mot de passe par défaut du constructeur).
   - *Correction* : Comptes individuels + MFA + gestionnaire de mots de passe.

2. **Patching OT sans validation :**
   - *Erreur* : Appliquer les correctifs de sécurité Windows Update directement sur un poste SCADA.
   - *Correction* : Test sur jumeau numérique ou bac à sable, validation avec le fournisseur.

3. **Absence de logs OT :**
   - *Erreur* : Pas de collecte de logs sur les équipements OT (PLC, HMI, variateurs).
   - *Correction* : Activez le syslog ou OPC-UA alarms sur tous les équipements critiques.

---

## Liste de vérification

- [ ] Les zones IEC 62443 sont définies et les pare-feux (conduits) sont en place.
- [ ] L'authentification forte (MFA, certificats) est déployée pour l'accès distant.
- [ ] Un IDS (Suricata, Zeek) analyse le trafic OT en continu.
- [ ] Les logs OT sont centralisés dans un SIEM avec corrélation.
- [ ] Un plan de réponse aux incidents OT est documenté et testé (exercice annuel).
- [ ] Les correctifs de sécurité sont testés sur un environnement non critique avant déploiement.
- [ ] Une sauvegarde validée des configurations PLC/SCADA est disponible hors ligne.
