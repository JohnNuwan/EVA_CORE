---
name: cycle-cellulaire-apoptose
description: "Compétence niveau ingénieur/docteur sur le cycle cellulaire et l'apoptose. Couvre les CDK/cyclines, la mitose, la méiose et la mort cellulaire."
arxiv_categories:
  - q-bio.CB
  - q-bio.SC
---

# Compétence : Cycle Cellulaire et Apoptose

## Présentation

Compétence niveau ingénieur/docteur sur le cycle cellulaire : phases, CDK-cyclines, mitose, méiose, apoptose, cancer.

---

## 1. Phases du Cycle

| Phase | Durée | Événements |
|---|---|---|
| G1 | 6-12 h | Croissance, signalisation |
| S | 8-10 h | Réplication ADN |
| G2 | 3-4 h | Préparation mitose |
| M | 1-2 h | Mitose + cytodiérèse |
| G0 | Variable | Quiescence |

### Point de restriction (R)
Rb hypo-P → lie E2F → arrêt
Rb hyper-P (CDK4/6-Cyc D) → E2F libre → transcription S

---

## 2. CDK-Cyclines

| CDK | Cycline | Phase |
|---|---|---|
| **CDK4/6** | Cyc D | G1 |
| **CDK2** | Cyc E | G1→S |
| **CDK2** | Cyc A | S |
| **CDK1** | Cyc A | G2 |
| **CDK1** | Cyc B | G2→M |

### Régulation
- CAK (CDK7-Cyc H) : active T161
- Wee1 : inh. Y15 ; Cdc25 : active Y15 déP
- p21/p27 (CIP/KIP) : inhibent CDK2
- p16 (INK4a) : inhibe CDK4/6 → suppresseur tumeur

---

## 3. Points de Contrôle

### G1/S
```
Dommages ADN → ATM → p53 → p21 → CDK2↓ → arrêt G1
```

### G2/M
```
ADN non répliqué → ATR → CHK1 → Cdc25 inactif → CDK1↓ → arrêt G2
```

### SAC (Mitose)
```
Kinétochores libres → Mad2 → Cdc20 inhibé → APC/C inactif
Tous attachés → APC/C → sécurine → séparase → anaphase
```

---

## 4. Mitose

| Phase | Événement |
|---|---|
| **Prophase** | Condensation, fuseau, NE fragmente |
| **Métaphase** | Alignement plaque équatoriale |
| **Anaphase** | Chromatides → pôles |
| **Télophase** | NE se reforme, décondensation |
| **Cytodiérèse** | Anneau actine-myosine |

---

## 5. Méiose

### Méiose I (réductionnelle)
- Prophase I : synapsis, crossing over (SPO11, DMC1)
- Métaphase I : bivalents, brassage indépendant
- Anaphase I : homologues séparés → 2 cellules n

### Méiose II (équationnelle)
- Comme mitose → 4 gamètes haploïdes

---

## 6. Apoptose

### Voie intrinsèque (mitochondriale)
```
Stress → BH3-only → Bax/Bak → MOMP → Cyt c + Apaf-1 → Apoptosome
→ Caspase 9 → Caspase 3 → Dégradation ADN
```

### Voie extrinsèque
```
FasL/TNFα → DISC → Caspase 8 → Caspase 3
Bid → tBid → mitochondrie (amplification)
```

### Régulation
- **Anti-apoptose** : Bcl-2, Bcl-xl, Mcl-1, IAPs (XIAP)
- **Pro-apoptose** : Bax, Bak, BH3-only (Bim, Bad, Puma)

---

## 7. Cancer

### Hallmarks
1. Ras/Myc → prolifération autonome
2. Rb/p16 perdus → insensibilité anti-croissance
3. p53 muté, Bcl-2 ↑ → évasion apoptose
4. Télomérase active
5. E-cadhérine ↓, MMP ↑ → métastases

### Thérapies
| Cible | Inhibiteur | Cancer |
|---|---|---|
| CDK4/6 | Palbociclib | Sein ER+ |
| Bcl-2 | Venetoclax | LLC |
| Mitose | Paclitaxel | Sein, poumon |

---

## 8. Références

- Morgan D.O. — *The Cell Cycle: Principles of Control*
- Weinberg R.A. — *The Biology of Cancer* (2nd ed.)
- Nurse P. (1975) — Cell cycle genetics — *Nature* (Nobel 2001)
- Kerr J.F.R. et al. (1972) — Apoptosis — *Br. J. Cancer*
- Hanahan D. & Weinberg R.A. (2011) — Hallmarks of cancer — *Cell*