---
name: drive-motion-control
description: "Configurer et programmer des variateurs de vitesse, servodrives et axes motion."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - vfd
      - variable-frequency-drive
      - servo-drive
      - motion-control
      - siemens-sinamics
      - rockwell-powerflex
      - abb-acs
      - sew-movifit
      - sercos
      - cia-402
      - electronic-cam
      - positioning
      - homing
      - camming
      - gearing
      - servo-motion
      - drive-engineering
      - profidrive
      - cip-motion
      - ethercat-drive
    related_skills:
      - pid-tuning-control
      - industrial-protocols
      - plc-connectivity
      - industrial-network-design
      - robotics-abb
---

# Entraînements et Motion Control

## Vue d'ensemble

Le **motion control** couvre la configuration, la programmation et le diagnostic des variateurs de vitesse (VFD), servodrives et axes motion. Domaines clés :

- **VFD (Variable Frequency Drive)** — Contrôle de vitesse/ couple pour moteurs asynchrones
- **Servodrive** — Positionnement précis avec moteurs synchrones (PM)
- **Motion coordonnée** — Axes interpolés, cames électroniques, gearing
- **Safety intégré** — STO, SS1, SLS, SOS

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De configurer un variateur Siemens Sinamics ou Rockwell PowerFlex
- De programmer des axes motion avec cames électroniques
- De paramétrer les boucles de régulation courant, vitesse, position
- De diagnostiquer des défauts de variateur
- D'optimiser des performances motion (autotuning)
- De migrer un parc de variateurs

---

## 1. CiA 402 — Profile Drive

### 1.1 Modes de fonctionnement

| Mode | Code | Usage |
|:-----|:-----|:------|
| **Profile Position** (pp) | 1 | Positionnement point-à-point avec rampe |
| **Profile Velocity** (pv) | 3 | Contrôle de vitesse |
| **Profile Torque** (tq) | 4 | Contrôle de couple |
| **Homing** (hm) | 6 | Référencement |
| **Interpolated Position** (ip) | 7 | Interpolation multi-axes |
| **Cyclic Sync Position** (csp) | 8 | Position synchrone cyclique |
| **Cyclic Sync Velocity** (csv) | 9 | Vitesse synchrone cyclique |
| **Cyclic Sync Torque** (cst) | 10 | Couple synchrone cyclique |

---

## 2. Références

- [CiA 402 Drive Profile](https://www.can-cia.org/can-knowledge/canopen/cia-402/)
- [Siemens Sinamics S120 Startdrive](https://www.siemens.com/startdrive)
- [Rockwell PowerFlex 520/750](https://www.rockwellautomation.com/powerflex)
- [SERCOS III Specification](https://www.sercos.org)
- [Pi Profile PROFIdrive](https://www.profibus.com/technology/profidrive)
- [ODVA CIP Motion](https://www.odva.org/technology/cip)
- [EtherCAT Drive Profile](https://www.ethercat.org)
