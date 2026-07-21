---
name: biologie-moleculaire-techniques
description: "Compétence niveau ingénieur/docteur en techniques de biologie moléculaire. Couvre PCR, clonage, séquençage, électrophorèse, CRISPR."
arxiv_categories:
  - q-bio.GN
  - q-bio.OT
---

# Compétence : Techniques de Biologie Moléculaire

## Présentation

Compétence niveau ingénieur/docteur en techniques de biologie moléculaire : PCR, clonage, séquençage, électrophorèse, hybridation, CRISPR.

---

## 1. Enzymes de Restriction

| Enzyme | Site | Extrémité |
|---|---|---|
| **EcoRI** | G|AATTC | Collante 5' |
| **HindIII** | A|AGCTT | Collante 5' |
| **BamHI** | G|GATCC | Collante 5' |
| **SmaI** | CCC|GGG | Franche |
| **NotI** | GC|GGCCGC | Rare (8 pb) |

---

## 2. Électrophorèse

| Support | Gamme | Usage |
|---|---|---|
| **Agarose** | 100 pb-50 kb | ADN génomique, PCR |
| **Polyacrylamide** | 20-1000 pb | Séquençage |

---

## 3. PCR

### Cycle (×30-40)
```
1. Dénaturation : 94-98°C (30 s)
2. Hybridation : 50-65°C (30 s)
3. Élongation : 72°C (30 s/kb)
```
### Variantes
| Type | Usage |
|---|---|
| **RT-PCR** | ARNm → ADNc |
| **qPCR** | Quantification (SYBR Green/TaqMan) |
| **Nested** | Spécificité accrue |
| **Multiplex** | Plusieurs cibles |

---

## 4. Clonage

### Stratégie
```
Digestion (insert + vecteur) → Ligation (T4, ratio 3:1)
→ Transformation (choc thermique/électroporation)
→ Sélection (antibiotique + X-Gal/IPTG)
→ Vérification (PCR colonies, séquençage)
```
### Assemblage
- **Gibson** : exonucléase + polymérase + ligase
- **Golden Gate** : BsaI → digestion + ligation simultanée
- **TA Cloning** : A-tailing

---

## 5. Séquençage

### Sanger
- ddNTP terminateurs fluorescents → capillaire → 500-1000 pb

### NGS
| Plateforme | Technologie | Lecture |
|---|---|---|
| **Illumina** | Bridge amplification | 2×150 pb |
| **PacBio** | SMRT | 10-30 kb |
| **Nanopore** | Courant ionique | 100 kb+ |

---

## 6. Hybridation

| Technique | Cible | Détection |
|---|---|---|
| **Southern** | ADN | Sonde ³²P/DIG |
| **Northern** | ARN | Sonde |
| **Western** | Protéines | Anticorps + ECL |
| **FISH** | ADN in situ | Fluorescence |

---

## 7. CRISPR-Cas9

### Mécanisme
```
sgRNA + Cas9 → PAM (NGG) → DSB 3 pb avant PAM
→ NHEJ (indels → KO) ou HDR (template → KI)
```

### Variants
| Variant | Fonction |
|---|---|
| **Cas9 nickase** | Coupure simple brin |
| **dCas9-VP64** | CRISPRa (activation) |
| **dCas9-KRAB** | CRISPRi (répression) |
| **Base Editor** | C→T, A→G sans DSB |
| **Prime Editor** | Insertion/substitution |

---

## 8. Références

- Sambrook J. & Green M.R. — *Molecular Cloning* (4th ed.)
- Jinek M. et al. (2012) — CRISPR-Cas9 — *Science* (Nobel 2020)
- **Addgene** : www.addgene.org
- **NEB** : www.neb.com