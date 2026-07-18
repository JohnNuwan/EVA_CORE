---
name: measurement-uncertainty-analysis
description: "Calculer les incertitudes de mesure selon le guide GUM (Type A et B, incertitude élargie) et évaluer la capabilité des systèmes de mesure par des études MSA R&R (Répétabilité & Reproductibilité)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  tags: [uncertainty-analysis, gum, msa, r-and-r, metrology, statistics, quality-control, measurement-system]
  helios:
    related_skills: [industrial-metrology-calibration, systems-engineering-sysml, pcb-design-altium]
---

# Analyse d'Incertitudes & Capabilité de Mesure (GUM / MSA)

## Vue d'ensemble

Cette compétence guide l'évaluation statistique rigoureuse de la qualité des systèmes de mesure industriels. Elle repose sur deux cadres méthodologiques complémentaires, largement reconnus dans l'industrie :

1. **Le GUM** (Guide to the Expression of Uncertainty in Measurement — JCGM 100:2008) : Cadre international pour le calcul mathématique des incertitudes de mesure, avec les évaluations de **Type A** (statistique, à partir de séries de mesures répétées) et de **Type B** (a priori, à partir de données constructeur, certificats d'étalonnage, spécifications). Le GUM fournit la **loi de propagation des variances** pour combiner les différentes sources d'incertitude et calculer l'**incertitude élargie** $U$ avec un niveau de confiance donné (généralement 95 %).

2. **Le MSA** (Measurement Systems Analysis — AIAG / IATF 16949) : Méthodologie issue du secteur automobile pour évaluer l'aptitude d'un système de mesure à discriminer correctement les pièces bonnes des pièces mauvaises. L'étude **Gage R&R** (Répétabilité et Reproductibilité) quantifie la part de variabilité apportée respectivement par l'instrument de mesure ($EV$ — Equipment Variation) et par les opérateurs ($AV$ — Appraiser Variation).

Ces deux approches sont complémentaires : le GUM calcule l'incertitude d'une mesure spécifique, tandis que le MSA évalue la capabilité globale du *système de mesure* (instrument + opérateur + procédure).

Cette compétence est conçue pour être actionnée par l'agent Helios lorsque l'utilisateur exprime un besoin lié au calcul d'incertitude, à la validation d'un système de mesure, ou à l'interprétation d'études statistiques de mesure.

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de façon explicite ou implicite de :

- Calculer l'incertitude composée et l'incertitude élargie d'une chaîne de mesure complexe (capteur + transmetteur + convertisseur A/N + alimentation).
- Réaliser une analyse d'incertitude de Type A (estimation statistique à partir de mesures répétées) ou de Type B (certificats d'étalonnage, données constructeurs, conditions environnementales).
- Mener une étude MSA Gage R&R par la méthode de la moyenne et de l'étendue (Range Method) ou par ANOVA.
- Interpréter les indicateurs $\%R\&R$, $ndc$ (Number of Distinct Categories) et le rapport signal/bruit pour décider de l'acceptation ou du rejet d'un système de mesure.
- Rédiger un budget d'incertitude complet pour un rapport d'étalonnage ou de validation d'un moyen de contrôle.
- Former ou assister une équipe qualité dans la mise en place d'études MSA selon la norme IATF 16949.

---

## Évaluation des incertitudes selon le GUM

### Modèle mathématique de la mesure

Toute mesure physique $Y$ est une fonction de plusieurs grandeurs d'entrée $X_i$ :

$$Y = f(X_1, X_2, \dots, X_n)$$

L'incertitude-type composée $u_c(Y)$ est obtenue par la **loi de propagation des variances** :

$$u_c^2(Y) = \sum_{i=1}^{n} \left( \frac{\partial f}{\partial X_i} \right)^2 \cdot u^2(X_i) + 2 \sum_{i=1}^{n-1} \sum_{j=i+1}^{n} \frac{\partial f}{\partial X_i} \cdot \frac{\partial f}{\partial X_j} \cdot u(X_i, X_j)$$

Pour des grandeurs d'entrée non corrélées (cas le plus fréquent), le deuxième terme (covariance) est nul :

$$u_c(Y) = \sqrt{ \sum_{i=1}^{n} \left( c_i \cdot u(X_i) \right)^2 }$$

Où $c_i = \partial f / \partial X_i$ est le **coefficient de sensibilité** de la grandeur $X_i$ sur le résultat $Y$.

### 1. Incertitude de Type A ($u_A$)

L'incertitude de Type A est calculée à partir de **séries d'observations répétées** ($n$ mesures indépendantes du même mesurande, dans les mêmes conditions) :

$$u_A = \frac{s}{\sqrt{n}}$$

Où $s$ est l'écart-type expérimental :

$$s = \sqrt{\frac{1}{n-1} \sum_{i=1}^{n} (x_i - \bar{x})^2}$$

**Nombre de mesures recommandé :** $n \ge 10$ pour une estimation fiable de $s$, $n \ge 20$ pour une incertitude de Type A prédominante.

**Degrés de liberté :** $\nu_A = n - 1$ (utilisé dans le calcul du facteur d'élargissement $k$ via la distribution de Student).

### 2. Incertitude de Type B ($u_B$)

L'incertitude de Type B est évaluée à partir d'informations **a priori**, sans mesures supplémentaires. Les sources typiques sont :

| Source | Information disponible | Loi de distribution | $u_B$ |
|:-------|:---------------------|:-------------------|:------|
| Certificat d'étalonnage | Incertitude élargie $U_{cert}$ avec $k_{cert}$ | Normale (par défaut) | $u_B = U_{cert} / k_{cert}$ |
| Résolution d'affichage | Demi-résolution $a$ | Rectangulaire (uniforme) | $u_B = a / \sqrt{3}$ |
| Tolérance constructeur | Demi-tolérance $\pm a$ | Rectangulaire | $u_B = a / \sqrt{3}$ |
| Tolérance constructeur | Demi-tolérance $\pm a$ | Triangulaire | $u_B = a / \sqrt{6}$ |
| Dérive entre étalonnages | Limite de dérive $\pm a$ | Rectangulaire | $u_B = a / \sqrt{3}$ |
| Condition environnementale (ex : T ambiante $\pm \Delta T$) | Variation $\pm a$ autour de la référence | Rectangulaire | $u_B = a / \sqrt{3}$ |

### 3. Incertitude élargie ($U$)

L'incertitude élargie $U$ définit un intervalle $y \pm U$ contenant la valeur vraie avec un niveau de confiance donné :

$$U = k \cdot u_c(Y)$$

| Niveau de confiance | Facteur d'élargissement $k$ | Condition |
|:-------------------|:--------------------------|:----------|
| 95 % | $k = 2$ | Valeur par défaut (GUM), $\nu_{eff} \to \infty$ |
| 99 % | $k \approx 2.58$ | $\nu_{eff} \to \infty$ |
| 95 % | $k = t_{0.975}(\nu_{eff})$ | Si $\nu_{eff}$ fini (formule de Welch-Satterthwaite) |

### 4. Budget d'incertitude — Exemple complet

**Mesure :** Température d'un bain d'étalonnage à l'aide d'une sonde PT100 + transmetteur 4-20 mA + entrée automate.

| Source | Symbole | Valeur | Loi | $u(X_i)$ | Coefficient $c_i$ | Contribution $c_i \cdot u(X_i)$ |
|:-------|:--------|:-------|:----|:---------|:-----------------|:------------------------------|
| Répétabilité (Type A) | $u_A$ | $s=0.05$, $n=10$ | Normale | $0.05 / \sqrt{10} = 0.016$ | 1 | $0.016$ |
| Résolution du transmetteur | $s_{res}$ | $0.01\,\mathrm{°C}$ | Rectangulaire | $0.01 / \sqrt{3} = 0.006$ | 1 | $0.006$ |
| Linéarité du transmetteur (certificat) | $s_{lin}$ | $U_{cert} = 0.05$, $k=2$ | Normale | $0.05 / 2 = 0.025$ | 1 | $0.025$ |
| Précision convertisseur A/N automate | $s_{conv}$ | $\pm 0.1\%$ de la pleine échelle | Rectangulaire | $(0.001 \times 200) / \sqrt{3} = 0.115$ | 1 | $0.115$ |
| Dérive du transmetteur sur 1 an | $s_{drift}$ | $\pm 0.02\,\mathrm{°C}$ | Rectangulaire | $0.02 / \sqrt{3} = 0.012$ | 1 | $0.012$ |

$$u_c = \sqrt{0.016^2 + 0.006^2 + 0.025^2 + 0.115^2 + 0.012^2} = 0.119\,\mathrm{°C}$$

$$U = 2 \times 0.119 = 0.238\,\mathrm{°C} \quad (95\,\%)$$

**Analyse des contributions :** Le convertisseur A/N de l'automate est ici le principal contributeur (93 % de la variance totale). L'amélioration du système de mesure passe par le remplacement de l'entrée automate standard par une carte de mesure de précision dédiée.

---

## Capabilité de mesure : Études MSA Gage R&R

Une étude R&R décompose la variabilité totale d'un système de mesure en trois composantes :

$$\sigma_{totale}^2 = \sigma_{produit}^2 + \sigma_{R\&R}^2 = \sigma_{produit}^2 + \sigma_{répétabilité}^2 + \sigma_{reproductibilité}^2$$

### Protocole standard (AIAG)

- **Pièces** : 10 pièces (ou échantillons) représentatives de l'étendue de variation réelle du processus.
- **Opérateurs** : Au moins 3 opérateurs.
- **Essais** : Chaque opérateur mesure chaque pièce 2 à 3 fois, dans un ordre aléatoire.

### Méthode de la moyenne et de l'étendue

1. **Répétabilité (EV — Equipment Variation)** : Variabilité du même opérateur mesurant la même pièce plusieurs fois.
   $$EV = \bar{R} \cdot K_1$$

   où $\bar{R}$ est la moyenne des étendues des mesures de chaque opérateur pour chaque pièce, et $K_1$ une constante dépendant du nombre d'essais ($K_1 = 4.56$ pour 2 essais, $3.05$ pour 3 essais).

2. **Reproductibilité (AV — Appraiser Variation)** : Variabilité entre les moyennes des différents opérateurs mesurant les mêmes pièces.
   $$AV = \sqrt{ (\bar{X}_{diff} \cdot K_2)^2 - \frac{EV^2}{n \cdot r} }$$

   où $\bar{X}_{diff}$ est l'étendue des moyennes des opérateurs, $K_2$ une constante ($K_2 = 2.70$ pour 2 opérateurs, $2.08$ pour 3 opérateurs), $n$ le nombre de pièces, $r$ le nombre d'essais.

3. **R&R total :** $R\&R = \sqrt{EV^2 + AV^2}$

### Critères d'acceptation $\%R\&R$

Le $\%R\&R$ est le rapport entre la variabilité du système de mesure et la variabilité totale (ou la tolérance) :

$$\%R\&R_{tolérance} = \frac{R\&R}{USL - LSL} \times 100$$

$$\%R\&R_{processus} = \frac{R\&R}{\sigma_{totale}} \times 100$$

| $\%R\&R$ | Décision | Action |
|:---------|:---------|:-------|
| $< 10\%$ | **Excellent** — Acceptable sans réserve | Aucune |
| $10\%$ à $20\%$ | **Bon** — Acceptable sous conditions | Valable pour la plupart des applications |
| $20\%$ à $30\%$ | **Marginal** — Acceptable selon la criticité | Peut nécessiter une amélioration ou une révision des tolérances |
| $> 30\%$ | **Inacceptable** | Le système de mesure doit être amélioré ou remplacé |

### Nombre de catégories distinctes ($ndc$)

L'indicateur $ndc$ (Number of Distinct Categories) mesure la capacité du système de mesure à distinguer différentes classes de pièces :

$$ndc = \sqrt{2} \cdot \frac{\sigma_{produit}}{\sigma_{R\&R}}$$

- **$ndc \ge 5$** : Acceptable (le système peut discriminer au moins 5 niveaux distincts).
- **$ndc < 5$** : Le système de mesure n'est pas assez sensible pour les besoins de contrôle.

---

## Analyse de l'étude R&R par ANOVA

La méthode ANOVA (analyse de variance) est plus précise que la méthode des moyennes et étendues, car elle peut détecter une **interaction opérateur × pièce** (certains opérateurs mesurent systématiquement certaines pièces différemment des autres opérateurs).

**Tableau ANOVA type (3 opérateurs, 10 pièces, 2 essais) :**

| Source de variation | Somme des carrés ($SS$) | Degrés de liberté ($df$) | Carré moyen ($MS$) | $F$ | $p$-value |
|:--------------------|:----------------------|:-----------------------|:-------------------|:----|:----------|
| Pièce | $SS_{pièce}$ | 9 | $MS_{pièce}$ | $MS_{pièce}/MS_{int}$ | ... |
| Opérateur | $SS_{op}$ | 2 | $MS_{op}$ | $MS_{op}/MS_{int}$ | ... |
| Interaction (pièce × op) | $SS_{int}$ | 18 | $MS_{int}$ | $MS_{int}/MS_{rep}$ | ... |
| Répétabilité | $SS_{rep}$ | 30 | $MS_{rep}$ | — | — |
| **Total** | $SS_{tot}$ | 59 | | | |

Si l'interaction est significative ($p < 0.05$), l'effet de l'opérateur dépend de la pièce mesurée, ce qui indique un besoin de formation spécifique ou de clarification de la procédure de mesure.

---

## Pièges Courants (Common Pitfalls)

### 1. Sommer les incertitudes de manière linéaire

**Erreur :** Additionner directement les erreurs maximales individuelles pour obtenir l'incertitude globale : $U_{tot} = U_1 + U_2 + \dots + U_n$. Par exemple, pour une mesure de température : $1.0\,\mathrm{°C} + 0.5\,\mathrm{°C} = 1.5\,\mathrm{°C}$. Cette méthode **surestime** considérablement l'incertitude réelle (parfois de 40 % à 100 %), car elle suppose que toutes les erreurs individuelles s'additionnent dans le même sens simultanément — ce qui est statistiquement très improbable.

**Correction :** Appliquer la **loi de propagation des variances** (sommation quadratique) du GUM :

$$u_c = \sqrt{u_1^2 + u_2^2 + \dots + u_n^2}$$

Pour l'exemple ci-dessus avec $u_1 = 1.0 / \sqrt{3} = 0.577$ (loi rectangulaire) et $u_2 = 0.5 / \sqrt{3} = 0.289$ :

$$u_c = \sqrt{0.577^2 + 0.289^2} = 0.645 \quad \Rightarrow \quad U = 2 \times 0.645 = 1.29\,\mathrm{°C}$$

L'incertitude élargie est de $1.29\,\mathrm{°C}$, non $1.5\,\mathrm{°C}$ comme dans la sommation linéaire.

### 2. Mener une étude R&R avec des pièces non représentatives de la production

**Erreur :** Utiliser des pièces de test parfaitement identiques (même dimension, même dureté, même état de surface) pour mener l'étude Gage R&R. La variabilité réelle des pièces ($\sigma_{produit}$) est sous-estimée (proche de zéro), donc le rapport $\frac{\sigma_{R\&R}}{\sigma_{totale}}$ devient très grand, et le $\%R\&R$ semble inacceptable même pour un excellent système de mesure. À l'inverse, des pièces trop différentes sans représentativité de la plage de tolérance faussent aussi l'analyse.

**Correction :** Sélectionner soigneusement un échantillon de **10 pièces** (selon AIAG) qui couvre **au moins 80 %** de la plage de tolérance $[LSL, USL]$, avec une répartition aussi uniforme que possible. Si la variation naturelle du processus ($6\sigma_{processus}$) est inférieure à la tolérance, sélectionner des pièces représentatives de toute la plage de variation du processus (y compris les pièces hors tolérance, si disponibles et autorisées).

### 3. Confondre précision et résolution

**Erreur :** Considérer qu'un instrument avec une résolution de $0.001\,\mathrm{mm}$ (3 décimales sur l'afficheur) est nécessairement "précis" avec une incertitude de $0.001\,\mathrm{mm}$. La résolution n'est qu'une des nombreuses composantes de l'incertitude (Type B). Un pied à coulisse digital de résolution $0.001\,\mathrm{mm}$ a en réalité une incertitude élargie typique de $\pm 0.02\,\mathrm{mm}$ à cause des défauts de géométrie des becs, de la force de mesure et de la température.

**Correction :** Les données constructeur fournissent la précision (ou erreur maximale tolérée) qui est généralement bien supérieure à la résolution. Dans le budget d'incertitude, inclure à la fois la résolution (petite contribution) et la précision constructeur (contribution principale) comme sources distinctes de Type B. La résolution contribue via $a/\sqrt{3}$ où $a$ est la demi-résolution.

### 4. Oublier d'inclure les conditions environnementales dans le budget d'incertitude

**Erreur :** Réaliser un budget d'incertitude pour une mesure dimensionnelle sans tenir compte de la **température ambiante**. Une variation de $5\,\mathrm{°C}$ sur une pièce en acier de $500\,\mathrm{mm}$ provoque une dilatation de $\Delta L = 500 \times 12\times10^{-6} \times 5 = 0.030\,\mathrm{mm}$, ce qui peut être supérieur à la tolérance de la pièce.

**Correction :** Inclure dans le budget d'incertitude au moins les sources environnementales suivantes :

- **Température ambiante** : $\Delta T$ autour de $20\,\mathrm{°C}$ de référence, coefficient de dilatation du matériau.
- **Hygrométrie** : Impact sur les matériaux hygroscopiques (bois, polymères).
- **Pression atmosphérique** : Pour les mesures de longueur d'onde (interférométrie) ou les mesures de force.
- **Vibrations** : Pour les mesures de précision (microscopie, profilométrie).

---

## Liste de vérification (Checklist)

- [ ] Les calculs d'incertitude de Type B spécifient la loi de distribution utilisée (rectangulaire, triangulaire, normale) et justifient ce choix.
- [ ] La loi de propagation des variances (sommation quadratique) est appliquée pour combiner les incertitudes-types individuelles, non la sommation linéaire.
- [ ] Le facteur d'élargissement $k$ (généralement $k=2$ pour un niveau de confiance de 95 %) est clairement documenté dans le rapport final.
- [ ] L'étude Gage R&R implique au moins 3 opérateurs mesurant 10 pièces différentes à 2 ou 3 reprises chacun (protocole AIAG).
- [ ] Les pièces sélectionnées pour l'étude R&R couvrent >= 80 % de la plage de tolérance ou de la variation du processus.
- [ ] Le $\%R\&R$ et le $ndc$ sont calculés et interprétés selon les critères AIAG/IATF 16949.
- [ ] Les conditions environnementales (température, hygrométrie, pression) sont intégrées dans le budget d'incertitude.
- [ ] Les coefficients de sensibilité partiels ($c_i = \partial f / \partial X_i$) sont identifiés pour chaque grandeur d'entrée.
- [ ] Le rapport d'incertitude ou d'étude MSA est daté, signé et approuvé par le responsable métrologie/qualité.
- [ ] Les actions correctives sont définies si $\%R\&R > 30\%$ ou si $ndc < 5$.

