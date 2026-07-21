---
name: genie-genetique
description: "Compétence niveau ingénieur/docteur en génie génétique. Couvre les vecteurs, systèmes hôtes, transgenèse, KO, OGM et thérapie génique."
arxiv_categories:
  - q-bio.GN
  - q-bio.OT
---

# Compétence : Génie Génétique et Biotechnologie

## Présentation

Compétence niveau ingénieur/docteur en génie génétique : vecteurs, systèmes hôtes, transgenèse, KO, OGM, anticorps, thérapie génique.

---

## 1. Vecteurs d'Expression

### Plasmides (pET)
```
T7 promoter → lacO → RBS → His6 → MCS → T7 terminator
+ lacI, KanR/Ampr, pBR322 ori
```
Induction : IPTG ; Tags : His6 (Ni-NTA), GST, MBP

### Vecteurs eucaryotes
| Type | Promoteur | Sélection | Usage |
|---|---|---|---|
| **pcDNA3** | CMV | G418 | Stable |
| **pAAV** | CMV/EF1α | GFP | In vivo |
| **Lentiviral** | CMV | Puromycine | Cellules primaires |

---

## 2. Systèmes Hôtes

### E. coli
| Souche | Spécificité |
|---|---|
| **BL21(DE3)** | T7, faible protéases |
| **Rosetta** | Codons rares |
| **SHuffle** | Ponts disulfure |

### Levures : S. cerevisiae, P. pastoris (haut rendement)
### Mammifères : CHO (standard), HEK293 (haute transfectabilité)

---

## 3. Transgenèse

### Souris transgénique
```
ADN → pronoyau → implantation → F0 → lignée germinale
```

### Souris KO
```
Vecteur ciblage → ES → sélection → blastocyste → chimère → KO
```

### Cre-LoxP (KO conditionnel)
```
Gène floxé (LoxP) × Cre tissu-spécifique → KO dans tissu cible
```
### Autres : zebrafish, drosophile (UAS-Gal4), C. elegans (RNAi)

---

## 4. Édition Génomique

| Technologie | Facilité | Spécificité | Coût |
|---|---|---|---|
| **ZFN** | ★☆☆ | ★★★ | Élevé |
| **TALEN** | ★★☆ | ★★★ | Moyen |
| **CRISPR-Cas9** | ★★★ | ★★☆ | Faible |

### CRISPR variants
- **CRISPRa** : dCas9-VP64 → activation
- **CRISPRi** : dCas9-KRAB → répression
- **Base Editor** : C→T, A→G sans DSB
- **Prime Editor** : insertion/substitution

---

## 5. Biothérapeutiques

| Type | Exemple | Hôte |
|---|---|---|
| **Insuline** | Humalog | E. coli |
| **EPO** | Époétine | CHO |
| **Anticorps** | Adalimumab | CHO |
| **Facteur VIII** | Kogenate | CHO |

### Formats anticorps
| Format | Masse | Usage |
|---|---|---|
| **IgG** | 150 kDa | Standard |
| **ScFv** | 28 kDa | Ciblage |
| **BiTE** | 55 kDa | Immunothérapie |
| **ADC** | 165 kDa | Chimiothérapie ciblée |

---

## 6. Thérapie Génique

### Stratégies
```
In vivo : vecteur administré directement
Ex vivo : cellules → transduites → réinjectées
```

### Approbations
| Thérapie | Vecteur | Maladie | Année |
|---|---|---|---|
| **Luxturna** | AAV | Amaurose Leber | 2017 |
| **Zolgensma** | AAV9 | SMA | 2019 |
| **Kymriah** | LV (CAR-T) | Leucémie B | 2017 |
| **Strimvelis** | LV | ADA-SCID | 2016 |

### CAR-T : scFv-4-1BB-CD3ζ → CD19 → lyse cellules B

---

## 7. OGM

| Caractère | Exemple |
|---|---|
| **Bt (Cry1Ab)** | Maïs résistant insectes |
| **EPSPS** | Soja tolérant glyphosate |
| **Golden Rice** | Riz β-carotène |

---

## 8. Références

- Green M.R. & Sambrook J. — *Molecular Cloning* (4th ed.)
- Glick B.R. et al. — *Molecular Biotechnology* (6th ed.)
- Cohen S.N. et al. (1973) — First plasmid cloning — *PNAS*
- Goeddel D.V. et al. (1979) — Human insulin — *PNAS*
- **Addgene** : www.addgene.org