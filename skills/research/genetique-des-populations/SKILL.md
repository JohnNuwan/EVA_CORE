---
name: genetique-des-populations
description: "Compétence niveau ingénieur/docteur en génétique des populations. Couvre Hardy-Weinberg, dérive, sélection, flux génique."
arxiv_categories:
  - q-bio.PE
  - q-bio.GN
---

# Compétence : Génétique des Populations

## Présentation

Compétence niveau ingénieur/docteur en génétique des populations : Hardy-Weinberg, dérive, sélection, flux génique, consanguinité, diversité.

---

## 1. Équilibre Hardy-Weinberg

### Conditions : ∞, pas de mutation/sélection/migration, panmixie

Pour 2 allèles A(p) et a(q) : p+q=1
- AA = p², Aa = 2pq, aa = q²

### Test χ² = Σ(O-E)²/E, ddℓ=1

---

## 2. Dérive Génétique

- Petites populations : fluctuations aléatoires
- **Perte H** : ΔH = -1/(2Ne) par génération
- **Goulot d'étranglement** → diversité réduite
- **Effet fondateur** → allèles rares enrichis

### Coalescence : TMRCA ≈ 2Ne générations

---

## 3. Sélection

| Type | Effet |
|---|---|
| **Positive** | Allèle avantageux → fixation |
| **Purifiante** | Délétère → éliminé |
| **Balancée** | Hétérozygote avantagé |
| **Fréq.-dépendante** | Rare = avantage |

### Coefficient de sélection (s)
- W_AA=1, W_Aa=1-hs, W_aa=1-s
- **Drépanocytose** : HbS/HbA fitness 1.0 (paludisme)

---

## 4. Flux Génique

### F-stats (Wright)
| Indice | Rôle |
|---|---|
| **Fis** | Consanguinité intra-pop |
| **Fst** | Différenciation inter-pop |
| **Fit** | Consanguinité totale |

### Fst interprétation
| Fst | Niveau |
|---|---|
| <0.05 | Faible |
| ~0.12 | Global humain |
| >0.25 | Espèces |

---

## 5. Consanguinité

- **F = probabilité IBD**
- Cousin 1er : F=1/16, Frère-sœur : F=1/4
- Dépression : δ = -2BF

---

## 6. Diversité Génétique

| Mesure | Rôle |
|---|---|
| **π** | Diversité nucléotidique moyenne |
| **θ** | 4Neμ (estimé par S) |
| **Hexp** | Hétérozygotie attendue |

### Tajima's D = (π - θ_S)/√Var
- D=0 : neutre ; D>0 : contraction, balancée ; D<0 : expansion, sweep

---

## 7. Détection Sélection

| Signal | Méthode |
|---|---|
| **Sweep** | Tajima's D, Fu's Fs |
| **Fst outlier** | Différenciation extrême |
| **iHS** | Haplotypes longs |
| **dN/dS** | Ratio non-syn/syn (PAML) |

### Exemple lactase : LCT -13910*T, iHS fort, ~7500 ans

---

## 8. Horloge Moléculaire

| Génome | Taux |
|---|---|
| Nucléaire humain | 1.1×10⁻⁸/site/gén |
| ADNmt humain | 2%/My |
| Virus ARN | ~10⁻⁵ |

---

## 9. Références

- Hartl D.L. & Clark A.G. — *Principles of Population Genetics* (4th ed.)
- Gillespie J.H. — *Population Genetics* (2nd ed.)
- Wright S. (1931) — Evolution in Mendelian populations — *Genetics*
- Kimura M. (1968) — Neutral theory — *Nature*
- Tajima F. (1989) — D test — *Genetics*