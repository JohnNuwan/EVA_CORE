---
name: voies-metaboliques
description: "Compétence niveau ingénieur/docteur sur les voies métaboliques détaillées. Couvre la gluconéogenèse, la synthèse des acides gras, le cycle de l'urée, la biosynthèse des nucléotides et de l'hème."
arxiv_categories:
  - q-bio.MN
  - q-bio.BM
---

# Compétence : Voies Métaboliques Détaillées

## Présentation

Compétence niveau ingénieur/docteur sur les voies métaboliques détaillées : gluconéogenèse, lipogenèse, cycle de l'urée, biosynthèse des acides aminés, nucléotides, hème, fer.

---

## 1. Gluconéogenèse

### Localisation : foie (cytosol + mitochondrie)

### Bypass des réactions irréversibles de la glycolyse
| Glycolyse | Gluconéogenèse | Enzyme |
|---|---|---|
| Hexokinase (G→G6P) | G6P→G | G6Pase |
| PFK-1 (F6P→F1,6BP) | F1,6BP→F6P | FBPase-1 |
| Pyruvate kinase (PEP→Pyr) | Pyr→OAA→PEP | PC+PEPCK |

### Bilan
```
2 Pyruvate + 4 ATP + 2 GTP + 2 NADH → Glucose + 4 ADP + 2 GDP + 6 Pi
```

### Régulation
↑ Glucagon → PKA → PEPCK↑, FBPase-1↑ → ↑ gluconéogenèse
F-2,6-BP ↓ → PFK-1↓, FBPase-1↑

---

## 2. Synthèse des Acides Gras (Lipogenèse)

### Localisation : foie, tissu adipeux (cytosol)

### ACC (Acétyl-CoA Carboxylase)
```
Acétyl-CoA + HCO₃⁻ + ATP → Malonyl-CoA
```
Régulation : ↑ Citrate, ↓ Palmitoyl-CoA, AMPK inh.

### FAS (Fatty Acid Synthase)
```
7 cycles : Condensation → Réduction → Déshydratation → Réduction
→ Palmitate (C16:0)
Bilan : Acétyl-CoA + 7 Malonyl-CoA + 14 NADPH → Palmitate + 7 CO₂
```

### Élongation/désaturation
| Enzyme | Produit | Localisation |
|---|---|---|
| **ELOVL** | C18-C26 | RE |
| **Δ9-désaturase** | C16:1, C18:1 | RE |
| **Δ5/Δ6-désaturase** | C20:4 (AA) | RE |

---

## 3. Cycle de l'Urée

### Foie (mitochondrie + cytosol)
```
NH₄⁺ + HCO₃⁻ → Carbamoyl-P (CPS-I, NAG activé)
    + Ornithine → Citrulline
    + Aspartate → Argininosuccinate → Arginine + Fumarate
    → Urée + Ornithine
```
Bilan : NH₄⁺ + CO₂ + Aspartate + 3 ATP → Urée + Fumarate

### Déficits
| Déficit | Maladie |
|---|---|
| **OTC** | X-linked, hyperammoniémie |
| **Argininosuccinate synthétase** | Citrullinémie |
| **Arginase** | Hyperargininémie |

---

## 4. Biosynthèse des Nucléotides

### Purines (de novo)
```
PRPP → 10 étapes → IMP → AMP ou GMP
Inhibiteurs : Mycophénolate (IMPDH), 6-MP (HGPRT)
Déficit HGPRT → Lesch-Nyhan
```

### Pyrimidines (de novo)
```
Carbamoyl-P + Aspartate → Orotate → UMP → UDP → UTP → CTP
Inhibiteur : Leflunomide (DHODH)
```

---

## 5. Synthèse de l'Hème

```
Glycine + Succinyl-CoA → ALA → PBG → Uroporphyrinogène III → Copro → Proto → Hème
ALAS1/2 : enzyme limitante (feedback hème)
Ferrochélatase : Fe²⁺ insère
```
**Porphyries** : AIP (PBG désaminase), PCT (Uroporphyrinogène décarboxylase)

---

## 6. Métabolisme du Fer

```
Fer alimentaire → DMT1 → Ferritine (stockage) ou Transferrine (transport)
→ Moelle (Hb) → Rate (recyclage)
Hepcidine : régule ferroportine (export)
```

---

## 7. Acides Aminés Essentiels

```
PVT TIM HALL : Phe, Val, Thr, Trp, Ile, Met, His, Arg, Leu, Lys
```
- **Glucoformateurs** : Ala, Arg, Asn, Asp, Cys, Gln, Glu, Gly, His, Met, Pro, Ser, Thr, Val
- **Cétogènes** : Leu, Lys
- **Mixtes** : Ile, Phe, Trp, Tyr

---

## 8. Références

- Nelson D.L. & Cox M.M. — *Lehninger Principles of Biochemistry* (8th ed.)
- Voet D. & Voet J.G. — *Biochemistry* (5th ed.)
- Krebs H.A. (1932) — Cycle de l'urée — *Z. Physiol. Chem.*
- **KEGG PATHWAY** : genome.jp/kegg
- **HMDB** : hmdb.ca