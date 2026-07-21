---
name: enzymologie-cinetique
description: "Compétence niveau ingénieur/docteur en enzymologie. Couvre la cinétique Michaelis-Menten, l'inhibition, l'allostérie et les mécanismes catalytiques."
arxiv_categories:
  - q-bio.BM
  - physics.bio-ph
---

# Compétence : Enzymologie et Cinétique Enzymatique

## Présentation

Compétence niveau ingénieur/docteur en enzymologie : cinétique, inhibition, allostérie, mécanismes catalytiques, classes EC.

---

## 1. Cinétique Michaelis-Menten

### Modèle
```
E + S ⇌ ES → E + P     (k₁, k₋₁, kcat)
```
- **Km** = (k₋₁ + kcat)/k₁
- **Vmax** = kcat × [E]t
- **kcat/Km** : efficacité catalytique (limite ~10⁸-10⁹ M⁻¹s⁻¹)
- **v** = Vmax × [S] / (Km + [S])

### Lineweaver-Burk
```
1/v = (Km/Vmax) × 1/[S] + 1/Vmax
```

---

## 2. Inhibition

| Type | Vmax | Km | Fonction |
|---|---|---|---|
| **Compétitive** | Inchangé | ↑ | I au site actif |
| **Non-compétitive** | ↓ | Inchangé | I ailleurs |
| **Incompétitive** | ↓ | ↓ | I lie ES |
| **Mixte** | ↓ | Variable | |

### Irréversible
- Inactivateurs suicide (kinact/KI)
- Ex : Aspirine (COX), Pénicilline (DD-transpeptidase)

---

## 3. Allostérie

### Équation de Hill
```
v = Vmax × [S]ⁿ / (K₀.₅ⁿ + [S]ⁿ)
```
- **n_H = 1** : non coopératif
- **n_H > 1** : coopérativité positive (Hb O₂ ~2.8)
- **n_H < 1** : coopérativité négative

### Modèles
- **MWC** : T (faible affinité) ⇌ R (haute), symétrie
- **KNF** : séquentiel, induit

### Enzymes allostériques clés
| Enzyme | Effecteur + | Effecteur - |
|---|---|---|
| PFK-1 | AMP, F-2,6-BP | ATP, Citrate |
| ATCase | ATP | CTP |
| Glycogène phosphorylase | AMP | ATP, G6P |

---

## 4. Mécanismes Catalytiques

### Classes EC
| Classe | Réaction | Exemple |
|---|---|---|
| **1 Oxydoréductases** | Transfert e⁻ | ADH, Cyt P450 |
| **2 Transférases** | Transfert groupe | Kinases |
| **3 Hydrolases** | Hydrolyse | Sérine protéases |
| **4 Lyases** | Coupure sans H₂O | Décarboxylases |
| **5 Isomérases** | Réarrangement | TIM |
| **6 Ligases** | Liaison (+ATP) | ARNt synthétases |

### Mécanisme sérine protéase
```
Acylation : Ser-OH + R-CO-NH-R' → acyl-enzyme + R'-NH₂
Désacylation : acyl-enzyme + H₂O → R-COOH + Ser-OH
```

---

## 5. Évolution Dirigée

1. Error-prone PCR → DNA shuffling → sélection
2. **Design rationnel** : mutations ciblées (stabilité, spécificité)
3. **Outils** : Rosetta, PROSS, HotSpot Wizard

---

## 6. Références

- Fersht A. — *Structure and Mechanism in Protein Science*
- Segel I.H. — *Enzyme Kinetics*
- Michaelis L. & Menten M.L. (1913) — *Biochem. Z.*
- Monod J. et al. (1965) — Allosteric transitions — *J. Mol. Biol.*
- **BRENDA** : brenda-enzymes.org
- **M-CSA** : ebi.ac.uk/thornton-srv/m-csa/