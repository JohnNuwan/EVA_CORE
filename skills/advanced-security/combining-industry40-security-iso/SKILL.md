---
name: combining-industry40-security-iso
description: "Intégrer les normes ISO (9001, 14001, 45001) avec la cybersécurité OT (IEC 62443) et les systèmes connectés de l'Industrie 4.0 dans une méthodologie unifiée."
version: 1.1.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [security, iso, industry40, ot, cybersecurity, iec62443, compliance, integration]
    related_skills: [industrial-cybersecurity-guidelines, iso-standards-for-industry, interoperability-of-industrial-systems]
---

# Intégration Normes ISO, Sécurité OT et Industrie 4.0

## Vue d'ensemble

Cette compétence fournit une **méthodologie intégrée** pour combiner les exigences des normes ISO (systèmes de management) avec les pratiques de cybersécurité OT (IEC 62443) et les technologies connectées de l'Industrie 4.0 (IoT, jumeaux numériques, MES). L'objectif est de concevoir un **système de management unifié** où la qualité, l'environnement, la sécurité des personnes ET la sécurité numérique sont traités de manière cohérente.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- D'aligner la conformité ISO 9001/14001/45001 avec la cybersécurité OT.
- De concevoir une usine intelligente respectant à la fois les normes qualité et les standards de sécurité IEC 62443.
- D'auditer un système Industrie 4.0 existant sous l'angle combiné ISO + sécurité OT.
- De créer un tableau de bord de conformité unifié (qualité, environnement, sécurité, cybersécurité).

---

## 1. Cartographie des Exigences Croisées

### 1.1 Correspondance ISO / IEC 62443

| Norme | Clé | Équivalent IEC 62443 | Synergie |
|:---|:---|:---|:---|
| **ISO 9001** §7.5 | Informations documentées | 62443-2-1 §4.3 | Documentation de sécurité intégrée au système qualité |
| **ISO 9001** §8.1 | Maîtrise opérationnelle | 62443-2-1 §4.5 | Procédures qualité incluant les contrôles de sécurité OT |
| **ISO 14001** §6.1 | Aspects environnementaux | 62443-3-3 §5 | Risques environnementaux des incidents cyber (ex: fuite polluante suite à intrusion) |
| **ISO 45001** §6.1 | Dangers SST | 62443-3-3 §6.2 | Risques sécurité liés à la perte de contrôle des machines (ex: robot non sécurisé) |
| **ISO 27001** §A.12 | Sécurité des opérations | 62443-2-1 §4.6 | Mesures de sécurité IT/OT convergentes |

### 1.2 Matrice des Risques Combinés

Pour chaque actif industriel, évaluez les risques croisés :

| Actif | Risque Qualité (9001) | Risque SST (45001) | Risque Cyber (62443) | Risque Combiné |
|:---|:---|:---|:---|:---|
| Automate (PLC) de ligne | Perte de production → rebut | Mouvement intempestif → blessure | Intrusion → modification programme | **CRITIQUE** |
| Capteur IoT température | Mesure erronée → non-conformité | - | Falsification → fausse alerte incendie | **ÉLEVÉ** |
| SCADA supervision | Perte de traçabilité | - | Ransomware → perte de contrôle | **CRITIQUE** |

---

## 2. Architecture d'Intégration

### 2.1 Segmentation des Zones (IEC 62443) + Processus ISO

```
┌─────────────────────────────────────────────────┐
│                 ZONE ISO 9001                    │
│  (Processus qualité, documentation, audits)      │
├─────────────────────────────────────────────────┤
│          CONDUITE (IEC 62443-3-2)               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │Zone 1    │  │Zone 2    │  │Zone 3    │      │
│  │Prod. A   │  │Prod. B   │  │Qualité   │      │
│  └──────────┘  └──────────┘  └──────────┘      │
│              │              │                    │
│         ┌────┴────┐   ┌────┴────┐               │
│         │Pare-feu │   │Pare-feu │                │
│         │ OT      │   │ OT      │                │
│         └─────────┘   └─────────┘                │
├─────────────────────────────────────────────────┤
│    Monitoring Sécurité + Qualité + Environnement │
│    (SIEM + MES + GTB consolidés)                 │
└─────────────────────────────────────────────────┘
```

### 2.2 Boucle de Contrôle Unifiée

```yaml
Cycle PDCA intégré (Qualité + Sécurité OT + Environnement) :
  Plan:
    - Identifier les risques qualité, SST, environnementaux ET cyber.
    - Définir les objectifs et indicateurs combinés.
    - Planifier les contrôles techniques (IEC 62443) et documentaires (ISO).
  Do:
    - Implémenter les mesures (segmentation réseau, MFA, procédures qualité).
    - Former le personnel aux aspects qualité ET sécurité OT.
  Check:
    - Audits internes ISO + tests de pénétration OT.
    - Revue des indicateurs combinés en réunion de direction.
  Act:
    - Actions correctives sur les non-conformités ISO ET les vulnérabilités OT.
    - Amélioration continue du SMI (Système de Management Intégré).
```

---

## 3. Mise en Œuvre Pratique

### 3.1 Étapes Clés

1. **Diagnostic croisé** : Comparez vos processus existants avec les exigences des normes visées et l'IEC 62443.
2. **Identification des points de convergence** : Listez les doublons documentaires potentiels (ex: un même document peut servir pour ISO 9001 §7.5 ET 62443-2-1 §4.3).
3. **Conception du SMI numérique** : Utilisez un MES ou un ERP pour centraliser les enregistrements qualité, les logs de sécurité OT et les indicateurs environnementaux.
4. **Déploiement des contrôles techniques** : Segmentez le réseau OT, déployez l'authentification forte, sécurisez les accès distants.
5. **Audit combiné** : Formez les auditeurs qualité aux spécificités OT, et les auditeurs sécurité aux exigences ISO.

### 3.2 Indicateurs de Performance Combinés (KPI)

| KPI | Formule | Cible | Fréquence |
|:---|:---|:---|:---|
| **Taux de conformité combiné** | (NC qualité + NC sécurité + NC environnement) / Total | ≥ 90% | Mensuel |
| **Temps de réponse aux incidents** | Délai entre détection et correction (qualité + cyber) | < 4h | Par incident |
| **Couverture documentaire SMI** | Documents SMI / Documents totaux requis | 100% | Trimestriel |
| **Score de maturité OT-ISO** | Auto-évaluation sur grille combinée | ≥ 3/5 | Annuel |

---

## 4. Pièges Courants

1. **Surcharge documentaire :**
   - *Erreur* : Maintenir des systèmes documentaires distincts pour ISO et pour la sécurité OT.
   - *Correction* : Fusionnez dans un SMI unique avec des politiques transverses.

2. **Conflit disponibilité (OT) vs confidentialité (IT) :**
   - *Erreur* : Appliquer des mises à jour de sécurité automatiques (IT) sans validation OT.
   - *Correction* : Établissez un processus de patch management spécifique OT avec validation sur jumeau numérique.

3. **Absence de formation croisée :**
   - *Erreur* : Les équipes qualité ne comprennent pas les enjeux OT, et vice-versa.
   - *Correction* : Formations communes sur les fondamentaux ISO + IEC 62443.

---

## Liste de vérification

- [ ] La matrice des risques combinés (qualité, SST, environnement, cyber) est établie.
- [ ] Les zones IEC 62443 sont définies et alignées sur les processus ISO.
- [ ] Les documents qualité incluent les procédures de sécurité OT (et inversement).
- [ ] Un plan de formation croisée (ISO + OT) est déployé.
- [ ] Les indicateurs de performance combinés sont suivis mensuellement.
- [ ] Un audit combiné ISO + test de pénétration OT est programmé annuellement.
