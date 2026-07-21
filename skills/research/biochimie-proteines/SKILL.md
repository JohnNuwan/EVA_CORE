---
name: biochimie-proteines
description: "Compétence niveau ingénieur/docteur en biochimie des protéines. Couvre la structure, le repliement, les modifications post-traductionnelles et l'analyse des protéines."
arxiv_categories:
  - q-bio.BM
  - physics.bio-ph
---

# Compétence : Biochimie des Protéines

## Présentation

Compétence niveau ingénieur/docteur en biochimie des protéines : acides aminés, structures (I-IV), repliement, modifications post-traductionnelles, purification, analyse structurale.

---

## 1. Acides Aminés

### Les 20 AA standard
| Catégorie | AA | pKa | ε₂₈₀ (M⁻¹cm⁻¹) |
|---|---|---|---|
| **Non polaires** | G, A, V, L, I, P, F | — | W=5500, Y=1490 |
| **Polaires** | S, T, N, Q, C, M | — | Cystine=125 |
| **Chargés -** | D (3.9), E (4.1) | 3.9/4.1 | |
| **Chargés +** | K (10.5), R (12.5), H (6.0) | 10.5/12.5/6.0 | |

### Liaison peptidique
- Planaire, résonance (40% double liaison), trans (99.6%)
- Angles φ, ψ, ω → Ramachandran plot

---

## 2. Structure

### Secondaire
| Élément | Angles φ/ψ | Liaison H | Pas |
|---|---|---|---|
| **Hélice α** | -57°/-47° | i→i+4 | 5.4 Å (3.6 rés/tour) |
| **Feuillet β** | -135°/135° | entre brins | 3.5 Å |
| **Coudes β** | variable | Type I/II | 4 résidus |

### Tertiaire
| Interaction | Énergie (kcal/mol) |
|---|---|
| Hydrophobe | -0.5 à -1.5/résidu |
| Liaison H | -3 à -7 |
| Ionique | -1 à -5 |
| Pont disulfure | -1 à -5 |

### Repliement (folding funnel)
```
États dépliés → molten globule → état natif (minimum global ΔG)
Chaperones : Hsp70, GroEL/GroES, Hsp90
Maladies : Alzheimer (β-amyloïde), Parkinson (α-synucléine), Prion
```

---

## 3. Modifications Post-Traductionnelles

| Modification | AA | Masse (Da) |
|---|---|---|
| **Phosphorylation** | S, T, Y | +80 |
| **Glycosylation N** | N (N-X-S/T) | Variable |
| **Acétylation** | K | +42 |
| **Ubiquitination** | K | +8.5 kDa/Ub |
| **Méthylation** | K, R | +14 |
| **Sumoylation** | K | +12 kDa |
| **Palmitoylation** | C | +256 |

---

## 4. Purification

1. Lysat → centrifugation → précipitation (NH₄)₂SO₄ → dialyse
2. Chromatographies : échange ions, affinité (His-Ni²⁺), gel filtration
3. **Dosage** : Bradford (595 nm), BCA (562 nm), UV₂₈₀

### SDS-PAGE / Western blot
- Séparation par masse, réduction/alkylation
- Transfert → anticorps primaire → secondaire HRP → ECL

---

## 5. Analyse Structurale

| Méthode | Résolution | Info |
|---|---|---|
| **Cristallographie RX** | 1-3 Å | Structure 3D |
| **RMN** | 2-5 Å | Dynamique (<40 kDa) |
| **Cryo-EM** | 1.5-4 Å | Grands complexes |
| **AlphaFold2** | Prédiction | Séqu. → structure |

---

## 6. Références

- Voet D. & Voet J.G. — *Biochemistry* (5th ed.)
- Berg J.M., Stryer L. — *Biochemistry* (9th ed.)
- Anfinsen C.B. (1973) — Protein folding — *Science* (Nobel 1972)
- Jumper J. et al. (2021) — AlphaFold — *Nature* (Nobel 2024)