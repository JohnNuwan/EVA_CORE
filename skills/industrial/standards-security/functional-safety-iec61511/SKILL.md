---
name: functional-safety-iec61511
description: "Concevoir et vérifier des architectures de sécurité SIL conformes IEC 61508/61511 et EN 13849."
version: 1.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags:
      - iec-61508
      - iec-61511
      - sil
      - safety-plc
      - safety-instrumented-system
      - sif
      - pfdavg
      - pfh
      - sff
      - hft
      - en-13849
      - performance-level
      - pl
      - category
      - mttfd
      - dcavg
      - ccf
      - functional-safety
      - sécurité-fonctionnelle
      - industrie-de-procédé
      - machine-safety
      - sis
      - proof-test
    related_skills:
      - cybersecurity-iec62443
      - industrial-risk-analysis-hazop
      - industrial-safety-sistema
      - iso-safety
---

# Sécurité Fonctionnelle — SIL selon IEC 61508 / IEC 61511 et EN 13849

## Vue d'ensemble

La **sécurité fonctionnelle** est la partie de la sécurité globale qui dépend du bon fonctionnement d'un système pour réduire les risques à un niveau acceptable. Cette compétence couvre la conception, la vérification et la validation des architectures de sécurité conformes aux normes :

| Norme | Domaine | Application |
|:------|:--------|:------------|
| **IEC 61508** | Générique | Tous les secteurs — norme fondamentale |
| **IEC 61511** | Industrie de procédé | Pétrochimie, chimie, pharma, raffinage, gaz |
| **EN 13849** | Machine | Fabrication, emballage, robotique, machines-outils |
| **EN 62061** | Machine | Équipements électriques de machines |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande :
- De vérifier un niveau SIL (Safety Integrity Level) pour une boucle SIF
- De calculer PFDavg ou PFH pour une architecture safety
- De concevoir une architecture redondante (1oo1, 1oo2, 2oo3, 1oo2D)
- De valider une matrice de sécurité
- De déterminer le Performance Level (PL) selon EN 13849
- D'optimiser l'intervalle de proof test

---

## 1. Concepts Fondamentaux

### 1.1 Définitions clés

| Terme | Définition |
|:------|:-----------|
| **SIS** (Safety Instrumented System) | Système instrumenté de sécurité : capteurs, logique, actionneurs |
| **SIF** (Safety Instrumented Function) | Fonction de sécurité spécifique avec un SIL cible |
| **SIL** (Safety Integrity Level) | Niveau d'intégrité de sécurité (1 à 4, SIL4 étant le plus élevé) |
| **PFDavg** | Probability of Failure on Demand (moyenne) — pour mode basse demande |
| **PFH** | Probability of dangerous Failure per Hour — pour mode haute demande |
| **SFF** | Safe Failure Fraction |
| **HFT** | Hardware Fault Tolerance |
| **PL** | Performance Level (a à e, PL e étant le plus élevé) — EN 13849 |
| **MTTFd** | Mean Time To dangerous Failure |
| **DCavg** | Average Diagnostic Coverage |
| **CCF** | Common Cause Failure |

### 1.2 Relation SIL ↔ PFDavg ↔ PFH (IEC 61508)

| SIL | PFDavg (Low Demand) | PFH (High Demand) | SFF (1oo1) | SFF (1oo2) |
|:---|:--------------------|:-------------------|:-----------|:-----------|
| 1 | ≥ 10⁻² à < 10⁻¹ | ≥ 10⁻⁶ à < 10⁻⁵ | < 60 % | < 60 % |
| 2 | ≥ 10⁻³ à < 10⁻² | ≥ 10⁻⁷ à < 10⁻⁶ | 60 % – 90 % | 60 % – 90 % |
| 3 | ≥ 10⁻⁴ à < 10⁻³ | ≥ 10⁻⁸ à < 10⁻⁷ | 90 % – 99 % | N/A (Route 2H) |
| 4 | ≥ 10⁻⁵ à < 10⁻⁴ | ≥ 10⁻⁹ à < 10⁻⁸ | ≥ 99 % | N/A |

---

## 2. SIL Verification — IEC 61508 / IEC 61511

### 2.1 Architecture 1oo1 (One out of One)

```
┌─────────────────────────────────────────────────────────────┐
│  Capteur ─── Logique ─── Actionneur                          │
│  (1 voie)     (1 voie)    (1 voie)                           │
└─────────────────────────────────────────────────────────────┘
```

**PFDavg** = PFDavg(S) + PFDavg(L) + PFDavg(A)
**HFT** = 0

### 2.2 Architecture 1oo2 (One out of Two)

```
┌─────────────────────────────────────────────────────────────┐
│  Capteur1 ─── Logique1 ─── Actionneur1                       │
│  Capteur2 ─── Logique2 ─── Actionneur2                       │
│  Vote : 1oo2 → un seul chemin doit fonctionner               │
└─────────────────────────────────────────────────────────────┘
```

**PFDavg** ≈ (λDU × TI / 2)² / 3 (pour deux voies identiques)
**HFT** = 1

### 2.3 Architecture 2oo3 (Two out of Three)

```
┌─────────────────────────────────────────────────────────────┐
│  Capteur1 ─ Logique1 ─ Actionneur1                           │
│  Capteur2 ─ Logique2 ─ Actionneur2                           │
│  Capteur3 ─ Logique3 ─ Actionneur3                           │
│  Vote : 2oo3 → deux des trois voies doivent fonctionner      │
└─────────────────────────────────────────────────────────────┘
```

**PFDavg** ≈ (λDU × TI)² / 3 (pour trois voies identiques)
**HFT** = 1

### 2.4 Formules de calcul

#### PFDavg pour différentes architectures :

| Architecture | PFDavg (approximation) |
|:-------------|:-----------------------|
| 1oo1 | λDU × TI / 2 |
| 1oo2 | (λDU × TI)² / 3 |
| 2oo2 | λDU × TI |
| 2oo3 | (λDU × TI)² |
| 1oo2D | (λDU × TI)² / 3 + β × λD (CCF) |

Où :
- λDU = Taux de défaillance dangereuse non détectée (par heure)
- TI = Proof Test Interval (heures)
- β = Common Cause Failure factor

#### SFF (Safe Failure Fraction) :

SFF = (λS + λDD) / (λS + λDD + λDU)

Où :
- λS = Taux de défaillance sûre
- λDD = Taux de défaillance dangereuse détectée
- λDU = Taux de défaillance dangereuse non détectée

### 2.5 Contraintes Architecturales (Route 1H)

| SIL | HFT = 0 (SFF min) | HFT = 1 (SFF min) | HFT = 2 (SFF min) |
|:---|:-------------------|:-------------------|:-------------------|
| 1 | < 60 % | — | — |
| 2 | 60 % – 90 % | < 60 % | — |
| 3 | 90 % – 99 % | 60 % – 90 % | < 60 % |
| 4 | ≥ 99 % | 90 % – 99 % | 60 % – 90 % |

---

## 3. Performance Level — EN 13849 (Machine)

### 3.1 Échelle PL

| PL | PFDavg (par demande) | PFHd (par heure) |
|:---|:---------------------|:------------------|
| a | ≥ 10⁻⁵ à < 10⁻⁴ | — |
| b | ≥ 3 × 10⁻⁶ à < 10⁻⁵ | — |
| c | ≥ 10⁻⁶ à < 3 × 10⁻⁶ | — |
| d | ≥ 10⁻⁷ à < 10⁻⁶ | — |
| e | ≥ 10⁻⁸ à < 10⁻⁷ | — |

### 3.2 Catégories de sécurité (EN 13849-1)

| Cat. | Description | HFT | Comportement aux défauts |
|:-----|:------------|:----|:------------------------|
| **B** | Circuit simple | 0 | Une défaillance → perte de la fonction de sécurité |
| **1** | Circuit simple + composants fiables | 0 | Même que B, mais MTTFd élevé |
| **2** | Circuit + test périodique | 0 | Défaut détecté par test → arrêt |
| **3** | Redondance sans accumulation | 1 | Un défaut → la fonction est maintenue |
| **4** | Redondance avec détection | 1 | Un défaut → la fonction est maintenue, défaut détecté |

### 3.3 PL = f(Category, MTTFd, DCavg, CCF)

Pour déterminer le PL :

1. **Choisir la catégorie** (B, 1, 2, 3, 4) selon l'architecture
2. **Évaluer MTTFd** par canal :
   - Low : 3 à 10 ans
   - Medium : 10 à 30 ans
   - High : 30 à 100 ans
3. **Évaluer DCavg** (Average Diagnostic Coverage) :
   - None : < 60 %
   - Low : 60 % – 90 %
   - Medium : 90 % – 99 %
   - High : ≥ 99 %
4. **Vérifier CCF** (Common Cause Failure) — Score ≥ 65 points requise pour Cat. 2, 3, 4

### 3.4 Exemple : Catégorie 3

```
Cat. 3 + MTTFd(High) + DCavg(Medium) + CCF(OK) → PL d
Cat. 3 + MTTFd(Medium) + DCavg(Medium) + CCF(OK) → PL c
Cat. 3 + MTTFd(Low) → PL impossible
```

---

## 4. Matrice de Sécurité

### 4.1 Structure typique

La matrice de sécurité est un tableau croisant les entrées (capteurs, commandes) avec les sorties (actionneurs, relais) pour définir les combinaisons valides et interdites.

```csv
État Machine, Porte Fermée, BP Urgence, Light Curtain, Moteur Avant, Moteur Arrière
Arrêt, 1, 1, 1, 0, 0
Marche auto, 1, 1, 0, 1, 1
Marche manuelle, 1, 1, 1, 1, 0
Défaut, 0, 0, 0, 0, 0
Marche avec BG ouvert, 0, 1, 1, 0, 0
```

### 4.2 Règles de validation

- **Aucune cellule vide** — chaque intersection doit avoir une valeur booléenne
- **Aucun conflit** — deux demandes contradictoires sur le même actionneur dans le même état
- **State Safety** — un état "défaut" doit mettre tous les actionneurs à OFF
- **Cross-check** — toute condition dangereuse doit être exclue par au moins un composant de sécurité

---

## 5. Proof Test Interval (PTI)

### 5.1 Optimisation

Le PTI est l'intervalle entre deux tests fonctionnels complets d'une SIF.

**Impact sur PFDavg** :
- PTI court → PFDavg bas → SIL plus élevé
- PTI long → Coûts d'arrêt réduits → PFDavg plus élevé

### 5.2 Exemple de calcul d'optimisation

Données :
- λDU = 1.5 × 10⁻⁷ / h
- Architecture 1oo1
- PFDavg cible pour SIL 2 : < 0.01

PFDavg(1oo1) = λDU × TI / 2

TI max = 2 × PFDavg_cible / λDU = 2 × 0.01 / (1.5 × 10⁻⁷) = 133 333 h ≈ 15.2 ans

---

## 6. Safety PLC Programming

### 6.1 Siemens F-S7

- Safety Matrix dans TIA Portal
- F-FB (Fail-safe Function Blocks) standard : F_CHKREP, F_CHKVAL, F_LOOPTIME
- F-CPU — Wakeup time, AC (Acceptance) check, PROFIsafe

```iecst
// Exemple : Safe Stop F-FB in SCL (TIA Portal)
FUNCTION_BLOCK FB_SafeStop
TITLE := 'Safe Stop Control'
AUTHOR : Actemium
FAMILY : Safety
VERSION : 1.0

VAR_INPUT
    EnableSafety : BOOL;
    StopRequest : BOOL := FALSE;
    ResetSafety : BOOL;
END_VAR

VAR_IN_OUT
    SafeOutput : BOOL;
END_VAR

SafeOutput := EnableSafety AND NOT StopRequest;

IF StopRequest THEN
    SafeOutput := FALSE;
ELSIF ResetSafety AND NOT StopRequest THEN
    SafeOutput := TRUE;
END_IF;

END_FUNCTION_BLOCK
```

### 6.2 Rockwell GuardLogix

- GuardLogix Safety Instruction Set
- Safety I/O with CIP Safety over EtherNet/IP
- Safety Partner — Redundant execution
- Safety Tasks — Periodic safety task, watchdog

### 6.3 HIMA / Triconex

- HIMA HIMax — SIL 3, TÜV-certified
- Triconex — Triple Modular Redundancy (TMR)
- Safety-related fieldbus communication

---

## 7. Références

- [IEC 61508:2010 - Functional safety of electrical/electronic/programmable electronic safety-related systems](https://www.iec.ch/functional-safety)
- [IEC 61511:2016 - Functional safety - Safety instrumented systems for the process industry sector](https://www.iec.ch)
- [EN ISO 13849-1:2015 - Safety of machinery - Safety-related parts of control systems](https://www.iso.org)
- [EN 62061:2005 - Safety of machinery - Functional safety of safety-related electrical, electronic and programmable electronic control systems](https://www.iec.ch)
- [IEC 61508-6:2010 - Guidelines on the application of IEC 61508-2 and IEC 61508-3](https://www.iec.ch)
- [Namur NE 130 - SIL estimation for process industry](https://www.namur.net)

