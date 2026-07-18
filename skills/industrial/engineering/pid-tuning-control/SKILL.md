---
name: pid-tuning-control
description: "Modéliser des systèmes asservis, paramétrer et optimiser des boucles de régulation industrielles (PID, cascade, feedforward, split-range) et appliquer les méthodes de réglage théoriques et empiriques."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [control, automation, pid, tuning, regulation, feedforward, ziegler-nichols, cohen-coon, lambda-tuning, industrial-control, dcs, plc]
    related_skills: [pid-instrumentation, embedded-systems-firmware]
---

# Régulation Industrielle et Réglage de Boucles PID

## Vue d'ensemble

Cette compétence encadre l'analyse, la modélisation et le réglage des boucles de régulation de procédé industriel. Le régulateur **PID** (Proportionnel-Intégral-Dérivé) est le standard universel pour contrôler une grandeur physique — température, pression, niveau, débit, pH, vitesse — à une valeur de consigne (Setpoint).

Une boucle de régulation bien réglée est essentielle pour la qualité du produit, la sécurité de l'installation et l'efficacité énergétique. Un mauvais réglage des paramètres ($K_p$, $T_i$, $T_d$) peut provoquer :

- Des oscillations entretenues qui dégradent la qualité du produit.
- Une usure prématurée des vannes de régulation (cycles excessifs).
- Une consommation énergétique accrue (overshoot et undershoot répétés).
- Dans les cas graves, l'instabilité complète du procédé (runaway thermique, variation de pression incontrôlée).

Cette compétence couvre à la fois les méthodes de réglage théoriques à partir de la réponse temporelle (Broïda, Ziegler-Nichols en boucle ouverte, Cohen-Coon) et les méthodes empiriques en boucle fermée (Ziegler-Nichols en oscillation, Lambda Tuning), ainsi que les architectures avancées (cascade, feedforward, split-range, ratio, override).

### Structure d'un régulateur PID

L'équation du PID parallèle (la plus courante dans les API Schneider, Rockwell et Siemens) est :

$$u(t) = K_p \cdot e(t) + \frac{K_p}{T_i} \int_0^t e(\tau) \, d\tau + K_p \cdot T_d \cdot \frac{de(t)}{dt}$$

Où :

- $u(t)$ : Commande de sortie (ex : $0-100\%$ d'ouverture de vanne).
- $e(t) = SP - PV$ : Écart entre la consigne (Setpoint) et la mesure (Process Variable).
- $K_p$ : Gain proportionnel.
- $T_i$ : Temps d'intégration ou reset time ($s$ ou $min$).
- $T_d$ : Temps de dérivation ou rate time ($s$ ou $min$).

> **⚠️ Attention** : Les constructeurs n'implémentent pas tous la même équation PID. Siemens (TIA Portal) utilise une forme série/mixte, Rockwell (Logix) utilise une forme parallèle avec des gains indépendants, Schneider (EcoStruxure) utilise une forme à paramètres $K_p$, $T_i$, $T_d$. Toujours vérifier la documentation du régulateur cible avant d'implémenter les paramètres calculés.

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Choisir les actions nécessaires pour réguler une grandeur physique : P, PI, PID, ou structure avancée (cascade, feedforward).
- Calculer les paramètres PID théoriques à partir de la réponse temporelle du système identifiée (courbe de réponse à un échelon).
- Mettre en œuvre des structures avancées : régulation en cascade (maître/esclave), correction par anticipation (Feedforward), ou régulation à échelle partagée (Split-Range).
- Résoudre un problème d'oscillation, de dépassement excessif (overshoot), d'instabilité ou de dérive lente sur une boucle en production.
- Diagnostiquer une boucle défaillante : bruit excessif, saturation, windup, actionneurs bloqués.
- Optimiser des boucles existantes par analyse des tendances historiques (dossier de performance de boucle).

## Méthodes de Réglage Fondamentales

### 1. Identification en boucle ouverte (Méthode de Broïda / Réaction curve)

Principe : appliquer un échelon de commande $\Delta U$ sur le régulateur en mode manuel (boucle ouverte) et enregistrer la réponse de la mesure $PV(t)$. La courbe de réaction permet d'identifier un modèle du **premier ordre avec retard pur (FOPDT)** :

$$G(s) = \frac{K}{\tau \cdot s + 1} \cdot e^{-\theta \cdot s}$$

Où :

- $K = \frac{\Delta PV}{\Delta U}$ : Gain statique.
- $\tau$ : Constante de temps ($s$) — temps pour atteindre $63\%$ de la valeur finale.
- $\theta$ : Retard pur ($s$) — temps mort entre l'échelon et le début de la réponse visible.

```text
PV(t)
│
│         ┌─────────────────────────── Valeur finale
│        ↗│
│      ↗  │                            63% de la variation
│    ↗    │
│  ↗      │
│ ↗      ─┼──── τ ────┐
│┌┘       │            │
││ θ      │            │
│└────────┴────────────┴──────────→ t
  ↑       ↑
  t=0   début réponse
```

#### Formules de Broïda pour un régulateur PI :

$$K_p = \frac{0.8 \cdot \tau}{K \cdot \theta} \quad \quad T_i = \tau$$

#### Pour un régulateur PID complet :

$$K_p = \frac{1.2 \cdot \tau}{K \cdot \theta} \quad \quad T_i = 2 \cdot \theta \quad \quad T_d = 0.5 \cdot \theta$$

Ces formules sont valables pour $\tau/\theta > 3$. Pour des retards purs prédominants ($\tau/\theta < 3$), préférer la méthode de Cohen-Coon.

### 2. Méthode de Cohen-Coon (Boucle ouverte)

Adaptée aux procédés avec retard pur important ($\tau / \theta$ faible) :

$$K_p = \frac{1}{K} \cdot \frac{\tau}{\theta} \cdot \left(\frac{1}{3} + \frac{\tau}{4 \cdot \theta}\right)$$

$$T_i = \theta \cdot \frac{32 + 6 \cdot (\tau/\theta)}{13 + 8 \cdot (\tau/\theta)} \quad \quad T_d = \theta \cdot \frac{4}{11 + 2 \cdot (\tau/\theta)}$$

### 3. Réglage empirique en boucle fermée (Ziegler-Nichols)

Cette méthode ne nécessite pas de modèle préalable mais consiste à amener la boucle en oscillation entretenue :

1. Passer le régulateur en mode manuel.
2. Désactiver les actions Intégrale ($T_i = \infty$ ou $9999$) et Dérivée ($T_d = 0$).
3. Remettre en mode automatique (boucle fermée).
4. Augmenter progressivement le gain proportionnel $K_p$ jusqu'à obtenir des oscillations auto-entretenues d'amplitude stable.
5. Noter ce gain critique $K_{cr}$ (ou $K_u$) et la période d'oscillation critique $P_{cr}$ (ou $T_u$).
6. Revenir en mode manuel immédiatement après avoir relevé les valeurs.
7. Calculer les paramètres selon la table de Ziegler-Nichols :

| Type | $K_p$ | $T_i$ | $T_d$ |
|:---|:---:|:---:|:---:|
| **P** | $0.5 \cdot K_{cr}$ | $\infty$ | $0$ |
| **PI** | $0.45 \cdot K_{cr}$ | $0.83 \cdot P_{cr}$ | $0$ |
| **PID** | $0.6 \cdot K_{cr}$ | $0.5 \cdot P_{cr}$ | $0.125 \cdot P_{cr}$ |

> **⚠️ Avertissement** : La méthode de Ziegler-Nichols en boucle fermée produit souvent un **overshoot agressif** ($> 50\%$). Elle est utile comme point de départ, mais doit être affinée (détuning) par la suite. Ne pas utiliser sur des procédés où les oscillations mettraient en danger l'installation ou dégraderaient la qualité produit.

## Structures Avancées

### 1. Régulation en Cascade

Deux régulateurs en série : le **maître** (primaire) dont la sortie devient la consigne de l'**esclave** (secondaire). Ce dernier réagit plus rapidement aux perturbations internes.

- **Avantage** : Le régulateur esclave compense rapidement les perturbations avant qu'elles n'affectent la variable primaire.
- **Exemple typique** : Maître = température d'un réacteur ; Esclave = débit de fluide caloporteur.
- **Condition** : La dynamique de l'esclave doit être au moins $3$ à $5$ fois plus rapide que celle du maître ($\tau_{esclave} < 0.3 \cdot \tau_{maître}$).

### 2. Correction par Anticipation (Feedforward)

Compense une perturbation mesurable avant qu'elle n'affecte la sortie. Utilisée en complément d'un feedback PID.

$$u_{FF}(t) = K_{FF} \cdot d(t)$$

Où $d(t)$ est la perturbation mesurée et $K_{FF}$ le gain de compensation (déterminé par modèle de procédé). Le résultat $u_{FF}$ s'ajoute à la sortie du PID.

- **Application** : Chauffage d'un échangeur dont le débit d'entrée varie ; la mesure de débit permet d'anticiper la correction de puissance.
- **Avantage** : Réduit l'overshoot et le temps de réponse du feedback seul.

### 3. Régulation à Échelle Partagée (Split-Range)

Un seul signal de commande $u(t)$ contrôle deux actionneurs différents sur des plages complémentaires.

- **Exemple** : $0-50\%$ = ouverture de vanne de chauffage (vapeur), $50-100\%$ = ouverture de vanne de refroidissement (eau glacée).
- **Mise en œuvre** : Configurer l'échelle de sortie sur chaque actionneur pour que leurs plages se chevauchent ou se complètent (avec une zone neutre possible au point de changement).

### 4. Régulation de Rapport (Ratio Control)

Maintient un rapport constant entre deux débits :

$$\frac{Q_2}{Q_1} = R$$

Le débit $Q_1$ est la variable maîtresse (wild flow). La consigne du régulateur de $Q_2$ est $R \times Q_1$.

- **Application** : Mélange de deux réactifs chimiques (acide + base), combustion (air/fuel ratio).

## Pièges Courants (Common Pitfalls)

1. **Saturation de l'intégrale (Integral Windup) :**
   - *Erreur :* Le régulateur reste en saturation (ex : vanne ouverte à $100\%$ mais la consigne n'est pas atteinte à cause d'une limitation physique). L'action intégrale continue d'accumuler l'erreur. Lorsque la consigne est enfin franchie, le système dépasse largement la cible (overshoot géant) car l'intégrale doit se « vider ».
   - *Correction :* Activer impérativement l'algorithme **Anti-Windup** qui fige la somme intégrale dès que la sortie physique atteint ses limites (par exemple $0\%$ ou $100\%$). Dans les API, cela se configure généralement par une option « Enable Anti-Windup » ou « Limit Integrator ».

2. **Bruit de mesure amplifié par la Dérivée :**
   - *Erreur :* Utiliser une action dérivée directe sur un signal de mesure brut (ex : débit bruité, niveau turbulent). Les variations rapides du bruit créent des pics de commande violents qui fatiguent la vanne et peuvent la faire osciller.
   - *Correction :* Appliquer un filtre passe-bas du premier ordre sur la mesure avant l'action dérivée, ou appliquer la dérivée **sur la mesure uniquement** (et non sur l'erreur $SP-PV$) en configurant $D_{mode} = PV$. Le coefficient de filtrage $T_f$ doit être de l'ordre de $0.1 \times T_d$.

3. **Mauvaise correspondance entre les paramètres du régulateur et ceux du constructeur :**
   - *Erreur :* Calculer $K_p$, $T_i$, $T_d$ avec les formules de Broïda/Ziegler-Nichols puis les saisir comme des gains indépendants dans une API Siemens qui utilise une structure série avec des constantes de temps de reset et rate différentes.
   - *Correction :* Toujours vérifier si le régulateur cible implémente une forme **parallèle** (gains indépendants : $K_p$, $K_i = K_p/T_i$, $K_d = K_p \cdot T_d$) ou **série** (interaction entre $T_i$ et $T_d$). Les gains $K_p$ diffèrent d'un facteur $(1 + T_d/T_i)$ entre les formes parallèle et série.

4. **Temps d'échantillonnage inapproprié :**
   - *Erreur :* Un temps d'échantillonnage $T_s$ trop grand manque les variations rapides du procédé ; un $T_s$ trop petit charge inutilement le CPU de l'API.
   - *Correction :* Respecter $T_s \le \frac{\tau}{10}$ pour les procédés lents (température, niveau) et $T_s \le \frac{\theta}{4}$ pour les procédés rapides. Un temps d'échantillonnage de $100\;ms$ est un bon compromis pour la majorité des boucles industrielles.

5. **Confusion entre les signaux d'entrée des vannes de régulation :**
   - *Erreur :* Configurer la sortie du PID en $0-100\%$ mais l'entrée de la vanne attend un signal $4-20\;mA$. Sans mise à l'échelle (scaling) correcte, la vanne n'atteint ni la pleine ouverture ni la pleine fermeture.
   - *Correction :* Vérifier la correspondance entre l'échelle du régulateur et l'échelle de l'actionneur. Pour un signal $4-20\;mA$ : $0\% \to 4\;mA$, $100\% \to 20\;mA$. Configurer les limites de sortie du PID pour qu'elles correspondent exactement à la plage exploitable de l'actionneur.

## Liste de vérification (Checklist)

- [ ] L'algorithme Anti-Windup est activé et correctement configuré sur les bornes de sortie physiques ($0\%$ et $100\%$).
- [ ] Le temps d'échantillonnage de la boucle ($T_s$) est au moins $10$ fois inférieur à la constante de temps du système ($\tau$).
- [ ] Un filtre passe-bas de premier ordre est placé sur les mesures bruitées si l'action Dérivée est active (coefficient $T_f \approx 0.1 \cdot T_d$).
- [ ] La structure du PID (parallèle, série ou mixte) est identifiée et documentée pour le constructeur cible (Siemens, Rockwell, Schneider, etc.).
- [ ] Les limites de sortie du PID ($0\%$ et $100\%$) sont correctement mises à l'échelle avec le signal de l'actionneur ($4-20\;mA$, $0-10\;V$, $3-15\;psi$).
- [ ] Une identification en boucle ouverte a été réalisée pour obtenir les paramètres $K$, $\tau$, $\theta$ du procédé.
- [ ] Au moins deux méthodes de réglage ont été comparées (Broïda/Cohen-Coon pour l'open-loop, Ziegler-Nichols/Lambda Tuning pour le closed-loop).
- [ ] Les régulateurs en cascade respectent le ratio de dynamique : $\tau_{esclave} \le 0.3 \cdot \tau_{maître}$.
- [ ] La réponse du système après application des paramètres est stable, sans overshoot excessif ($< 20\%$ visé) et sans oscillation résiduelle.
- [ ] Les tendances (Setpoint, PV, Output) sont enregistrées pour documenter le réglage et faciliter le diagnostic futur.

