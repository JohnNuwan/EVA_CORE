---
name: dcs-engineering
description: "Configurer, programmer et maintenir les systèmes DCS des industries de procédé."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - dcs
      - distributed-control-system
      - emerson-deltav
      - yokogawa-centum
      - honeywell-experion
      - abb-800xa
      - siemens-pcs7
      - pcs-neo
      - process-control
      - batch-control
      - apc
      - advanced-process-control
      - control-loops
      - cascade-control
      - feedforward
      - ratio-control
      - override-control
      - split-range
      - industrie-de-procédé
      - isa-106
      - isa-18-alarm-management
    related_skills:
      - mes-integration
      - batch-process-isa88
      - pid-tuning-control
      - pid-instrumentation
      - historian-timeseries
---

# Ingénierie des Systèmes de Contrôle Distribué (DCS)

## Vue d'ensemble

Un **DCS (Distributed Control System)** est un système de contrôle-commande dédié aux industries de procédé continu (pétrochimie, raffinage, chimie, pharmaceutique, agroalimentaire, eau, énergie). Contrairement aux automates (PLC) qui excellent dans le contrôle discret/logique, le DCS est optimisé pour :

- Le contrôle de procédé continu — PID, cascade, ratio, feedforward
- La gestion de lots batch (ISA-88)
- La haute disponibilité — Redondance totale (CPU, réseau, E/S, alimentation)
- Les centaines/milliers de boucles de régulation centralisées
- L'intégration native des fonctions de sécurité (SIS)

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer une architecture DCS pour une nouvelle installation
- De programmer des blocs de contrôle (control modules, CFC, SFC)
- De concevoir une stratégie de contrôle de procédé (PID cascade, ratio, override)
- De gérer les recettes batch (ISA-88) sur un DCS
- De diagnostiquer des problèmes de communication ou de régulation
- De planifier une migration d'un ancien système DCS vers un nouveau
- De dimensionner l'infrastructure DCS (réseau, E/S, redondance)

---

## 1. Architecture Générale d'un DCS

```
┌─────────────────────────────────────────────────────────────────┐
│                Niveau 4 — MES / ERP (couche entreprise)         │
├─────────────────────────────────────────────────────────────────┤
│                Niveau 3 — Historien, APC, Reporting             │
├─────────────────────────────────┬───────────────────────────────┤
│   Stations Opérateur (HMI)      │  Stations Ingénierie          │
│   ┌─────────────────────────┐   │  ┌─────────────────────────┐  │
│   │  Emerson DeltaV Operate │   │  │  Control Studio / AMS   │  │
│   │  Yokogawa CENTUM HIS    │   │  │  Fieldbus Configurator  │  │
│   │  Honeywell Experion FX  │   │  │  Control Builder / CEE  │  │
│   └─────────┬───────────────┘   │  └───────────┬─────────────┘  │
├─────────────┼───────────────────┴───────────────┼────────────────┤
│             │          Ethernet (1 Gb Redundant) │                │
│  ┌──────────┴───────────────────────────────────┴──────────┐    │
│  │           Contrôleurs DCS                                │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌──────────────────┐    │    │
│  │  │  DeltaV Sx  │ │  Centum VP  │ │  Experion C300   │    │    │
│  │  │  (Emerson)  │ │ (Yokogawa)  │ │  (Honeywell)     │    │    │
│  │  └──────┬──────┘ └──────┬──────┘ └────────┬─────────┘    │    │
│  │  ┌──────┴──────┐ ┌──────┴──────┐ ┌────────┴─────────┐    │    │
│  │  │  I/O Cards  │ │  FIO Bus   │ │  CEE (Control     │    │    │
│  │  │  (CIOC)     │ │  (FCS)     │ │  Execution Env)   │    │    │
│  │  └─────────────┘ └────────────┘ └───────────────────┘    │    │
│  └───────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────┤
│             Fieldbus (FF, PA, Profibus DP, HART)                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │  Capteurs│ │  Vannes  │ │Analyseurs│ │ Safety Sys (SIS) │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

### 1.1 Comparaison DCS vs PLC/SCADA

| Caractéristique | DCS | PLC + SCADA |
|:----------------|:----|:------------|
| **Domaine** | Procédé continu / batch | Discret, fabrication, machine |
| **Boucles PID** | Centaines à milliers intégrés | Quelques dizaines max |
| **Redondance** | Native (contrôleur, réseau, I/O) | Optionnelle, coûteuse |
| **Configuration** | Bibliothèque de blocs fonctionnels | Langages IEC 61131-3 |
| **Base de données** | Centralisée (tags, tendances, alarmes) | Distribuée |
| **Batch (ISA-88)** | Native (recettes, phases) | Souvent via SCADA additionnel |
| **Historien** | Intégré | Via boîtier externe |

---

## 2. Emerson DeltaV

### 2.1 Architecture matérielle

- **Contrôleurs** : S-Series (MD, MQ, PK), PK Controller, CHARM I/O
- **E/S** : CIOC (CHARMS I/O Cards), S-series I/O, Electronic Marshalling (CHARM)
- **Réseau** : Control Network (1 Gb redundant), Plantweb Ethernet APL

### 2.2 Configuration logicielle

#### Control Studio — Blocs de contrôle

Le CFC (Continuous Function Chart) est le langage visuel principal. Les blocs sont organisés par catégorie :

- **AI / AO** — Analog Input/Output with signal conditioning
- **DI / DO** — Discrete Input/Output
- **PID** — PID control avec auto-tuning, gain scheduling
- **PIDFF** — PID with feedforward
- **RATIO** — Ratio control
- **SPLTRNG** — Split range
- **SIGSEL** — Signal selector (low, high, median)
- **M/A** — Manual/Auto station
- **LLAG** — Lead/Lag
- **INTEG** — Integrator / Totalizer
- **CALC** — Calculator block (expression mathématique)

```python
# Configuration d'un bloc PID dans Control Studio (API OPC)
# 1. Ajouter le bloc PID à un module de contrôle
module.add_block("PID", "PIC-101")
# 2. Configurer les paramètres
PIC_101.set_attribute("MODE_TARGET", "Auto")
PIC_101.set_attribute("SP", 150.0)
PIC_101.set_attribute("GAIN", 2.5)
PIC_101.set_attribute("RESET", 1.0)  # Minutes per repeat
PIC_101.set_attribute("RATE", 0.0)   # Derivative
PIC_101.set_attribute("PV_SCALE.EU_100", 300.0)
PIC_101.set_attribute("PV_SCALE.EU_0", 0.0)
# 3. Connecter les entrées/sorties
PIC_101.set_attribute("IN", "FT-101.OUT")
PIC_101.set_attribute("OUT_D", "FV-101.CAS_IN")
```

#### Configuration batch (ISA-88)

```python
# Structure de recette batch
recette_1 = Recipe("POLYPROPYLENE_GRADE_A")
recette_1.add_phase("REACTOR", "HEAT_UP", {"target_temp": 180.0, "ramp_rate": 5.0})
recette_1.add_phase("REACTOR", "HOLD", {"hold_time": 30.0})
recette_1.add_phase("REACTOR", "COOL_DOWN", {"target_temp": 50.0, "ramp_rate": 3.0})
```

### 2.3 AMS Device Manager

- Configuration HART / Fieldbus des instruments de terrain
- Calibration, diagnostic, signature des vannes
- Historique des alerts devices

---

## 3. Yokogawa CENTUM VP

### 3.1 Architecture

- **FCS** (Field Control Station) — Contrôleur redondant
- **FIO** (Flexible I/O) — Bus E/S avec redondance
- **HIS** (Human Interface Station) — Postes opérateur
- **Vnet/IP** — Réseau de contrôle (1 Gb, redondant, temps réel)
- **Exaquantum** — Historien temps réel

### 3.2 Control Drawing

Le Control Drawing (ST-2 / ST-4) est l'éditeur de blocs fonctionnels Yokogawa.

```python
# Exemple : paramétrage d'un bloc PID-L
PID_L.set_parameter("PV", "FT-101.PV")
PID_L.set_parameter("SV", 150.0)
PID_L.set_parameter("PID.MODE", "AUTO")
PID_L.set_parameter("PID.P", 250.0)
PID_L.set_parameter("PID.I", 120.0)  # Seconds
PID_L.set_parameter("PID.D", 0.0)
PID_L.set_parameter("PID.DL", 0.0)   # Derivative lag
PID_L.set_parameter("MH", 100.0)     # Output high limit
PID_L.set_parameter("ML", 0.0)       # Output low limit
```

### 3.3 SEBOL (Sequence + Batch)

Sebol est le langage de séquence de Centum pour le batch et les séquences procédé.

```python
# Exemple de séquence Sebol conceptuelle
SEQ01:
  STEP 10: MV-101 → OPEN
  STEP 20: WAIT TI-101 ≥ 80.0
  STEP 30: START PUMP P-101
  STEP 40: WAIT LS-201 → ON
  STEP 50: MV-101 → CLOSE
  STEP 60: STOP PUMP P-101
  END
```

---

## 4. Honeywell Experion PKS

### 4.1 Architecture

- **C300 Controller** — Redondant, execution de control modules
- **CEE** (Control Execution Environment) — Runtime des stratégies de contrôle
- **EPKS** nodes — Serveurs FTE (Fault Tolerant Ethernet), SCADA, HMI
- **FTE** — Redundant control network (1 Gb, fault-tolerant, ring)
- **Safety Manager** — Système de sécurité intégré (SIL 2 / 3)

### 4.2 Control Module Programming

```python
# Configuration d'un Control Module (CM) Experion
CM_PIC_101 = ControlModule("PIC101", "PIDLoop")
CM_PIC_101.set_attribute("PV_SOURCE", "AI-101.PV_CV")
CM_PIC_101.set_attribute("SP", 200.0)
CM_PIC_101.set_attribute("MODE", "AUTO")
CM_PIC_101.set_attribute("PID_GAIN", 1.8)
CM_PIC_101.set_attribute("PID_RESET", 80.0)  # Seconds
CM_PIC_101.set_attribute("PID_RATE", 0.0)
CM_PIC_101.set_attribute("OUTPUT_TRACK", True)
CM_PIC_101.set_attribute("OUTPUT_TRACK_VALUE", "FV-101.OUT")
```

---

## 5. ABB 800xA

### 5.1 Architecture

- **AC 800M Controller** — Contrôleur avec execution IEC 61131-3
- **Control Builder** — Environnement de développement
- **800xA Operations** — Stations opérateur
- **Aspect Objects** — Modèle d'objet de l'usine
- **Advant Master / Melody** — Historiques et migration

### 5.2 Control Builder (IEC 61131-3)

```iecst
(* Exemple : Bloc Analog Alarm dans Control Builder *)
FUNCTION_BLOCK FB_AnalogAlarm
VAR_INPUT
    PV : REAL;
    PV_Low : REAL := 10.0;
    PV_High : REAL := 90.0;
    Hyst : REAL := 1.0;
END_VAR
VAR_OUTPUT
    ALARM_Low : BOOL;
    ALARM_High : BOOL;
END_VAR

ALARM_High := PV >= (PV_High + Hyst);
ALARM_Low := PV <= (PV_Low - Hyst);

IF NOT (PV >= PV_Low AND PV <= PV_High) THEN
    ALARM_High := PV > (PV_High + Hyst);
    ALARM_Low := PV < (PV_Low - Hyst);
END_IF;

END_FUNCTION_BLOCK
```

---

## 6. Siemens PCS 7 et PCS neo

### 6.1 PCS 7

- **AS 410/414** — Automation System avec CFC (Continuous Function Chart)
- **WinCC** — SCADA/opérateur
- **Industrial Ethernet / PROFIBUS** — Bus de terrain
- **CPM (Process Control Plant Model)** — Modèle de contrôle

### 6.2 PCS neo

- **Architecture web-native** — Sans poste ingénierie dédié
- **Simatic Automation Tool** — Configuration cloud-ready
- **IEC 61131-3 + SFC + CFC** — Multi-langage
- **Digital Twin natif** — Simulation intégrée

---

## 7. Stratégies de Contrôle Avancé (APC)

### 7.1 Stratégies courantes

| Stratégie | Description | Quand l'utiliser |
|:----------|:------------|:----------------|
| **Cascade** | PD secondaire + PID primaire | Longue inertie, perturbé |
| **Ratio** | Proportion entre deux débits | Mélanges, blending |
| **Feedforward** | Anticipation de perturbation | Mesurable avant effet |
| **Override** | Hiérarchie de consignes | Saturation / sécurité |
| **Split-range** | Deux actionneurs sur un signal | Pression, température |

### 7.2 Exemple de Cascade

```
┌─────────────────────────────────────────────────────────────┐
│  Consigne ─── PID(Temp) ─── PID(Pression) ─── Vanne        │
│  TIC-101      TIC-101.SP     PIC-101.SP         PV-101     │
│                ↓                               ↑           │
│            Température                       Pression       │
└─────────────────────────────────────────────────────────────┘
```

Configuration en DeltaV :
```python
TIC_101 = block("PID", "TIC-101")
PIC_101 = block("PID", "PIC-101")
PV_101 = block("AO", "PV-101")

# Cascade : TIC-101 sortie → PIC-101 consigne
TIC_101.set_attribute("MODE_TARGET", "Auto")
PIC_101.set_attribute("MODE_TARGET", "Cas")  # Cascade mode
PV_101.set_attribute("MODE_TARGET", "Auto")

# Signal routing
TIC_101.OUT → PIC_101.CAS_IN
PIC_101.OUT → PV_101.CAS_IN
```

---

## 8. Alarm Management (ISA-18.2)

### 8.1 Principes

- **Chaque alarme** doit avoir une justification documentée (rationalization)
- **Shelving** — Mise en veille temporaire avec retour automatique
- **Flood control** — Regroupement d'alarmes lors d'incidents
- **Key Performance Indicators** :
  - Nombre d'alarmes par heure (cible : < 6/h/opérateur)
  - Stall rate (taux d'alarmes non acquittées)
  - Flood ratio

### 8.2 Exemple de rationalization

```csv
Tag, Description, Type, Priorité, Seuil, Délai, Conséquence
TIC-101_HI, Température haute réacteur, HI_AUTO, HIGH, 200°C, 5s, Arrêt production
PIC-101_LO, Pression basse colonne, LO_AUTO, MEDIUM, 0.5 bar, 10s, Perte qualité
LI-201_AL, Niveau haut ballon, HI_AUTO, CRITICAL, 85%, 2s, Débordement - sécurité
```

---

## 9. Migration DCS

### 9.1 Stratégies de migration

| Stratégie | Approche | Risque | Coût |
|:----------|:---------|:-------|:-----|
| **Forklift** | Remplacement complet | Élevé | Très élevé |
| **Contrôleur hybride** | Nouveau contrôleur, I/O existant | Moyen | Élevé |
| **I/O marshalling** | Electronic marshalling, câblage conservé | Faible | Moyen |
| **Simulation** | Émulateur du système legacy | Minimal | Faible |

### 9.2 Checklist de migration

1. Inventaire complet des points I/O et des tags
2. Documentation des stratégies de contrôle existantes
3. Identification des SIF (Safety Instrumented Functions)
4. Test en environnement parallèle / simulation
5. Plan de cut-over (phase séquence par zone)
6. Formation des opérateurs sur le nouveau HMI
7. Validation de la redondance et du failover

---

## 10. Références

- [Emerson DeltaV Documentation](https://www.emerson.com/deltav)
- [Yokogawa CENTUM VP](https://www.yokogawa.com/solutions/products-platforms/control-system/centum-vp/)
- [Honeywell Experion PKS](https://www.honeywellprocess.com/experionpks)
- [ABB 800xA](https://new.abb.com/control-systems/system-800xa)
- [Siemens PCS neo](https://www.siemens.com/pcsneo)
- [ISA-88 Batch Control Standard](https://www.isa.org/isa88)
- [ISA-18.2 Alarm Management](https://www.isa.org/isa18)
- [IEC 61511 Functional Safety](https://www.iec.ch)
