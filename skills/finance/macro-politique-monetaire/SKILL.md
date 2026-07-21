---
name: macro-politique-monetaire
description: >-
  Analyser et anticiper les décisions de politique monétaire (Fed, BCE, BOJ,
  BOE, PBoC) : forward guidance, dot plot, QT/QE, taux directeurs, opérations
  de refinancement, yield curve control. Modélisation de l'impact sur les
  courbes de taux, changes, indices.
category: finance
---

# Politique Monétaire — Banques Centrales & Impact Marchés

## Présentation

Les banques centrales sont les acteurs les plus influents des marchés
financiers. Leurs décisions de taux, bilans et forward guidance déterminent
le prix de l'argent, la liquidité disponible et le risque systémique.
Ce skill fournit les outils pour analyser, anticiper et trader chaque
banque centrale majeure.

**Déclencheurs :** "Fed", "BCE", "BOJ", "BOE", "banque centrale",
"politique monétaire", "taux directeur", "QT", "QE", "assouplissement",
"resserrement", "hawkish", "dovish", "FOMC", "dot plot".

## Les 5 Banques Centrales Majeures

### ① Federal Reserve (Fed) — US

| Élément | Détail |
|---|---|
| **Réunions** | 8/an (jan, mars, mai, juin, juil, sep, nov, déc) |
| **Mandat** | Maximum employment + price stability (2% PCE) |
| **Taux pilote** | Fed Funds Rate (4.25-4.50% en 2026) |
| **Outils** | Taux directeur, QT/QE, forward guidance, IORB, ON RRP |
| **SEP / Dot Plot** | Trimestriel (mars, juin, sep, déc) — projections taux + PIB + chômage |
| **Communiqué** | Mercredi 14h ET (16h30 conférence Powell) |

**Key phrases decoder :**
- "Patient" / "Data-dependent" → statu quo probable
- "Warrant further increases" / "Ongoing hikes" → hausses à venir
- "Appropriate to ease" → baisse imminente
- "Transitory" → l'inflation va se résorber seule (historiquement faux)

**Outils Python :**
```python
from fredapi import Fred
fred = Fred(api_key="KEY")
# Taux Fed Funds effectif
fed_rate = fred.get_series("FEDFUNDS")
# Bilan Fed (total assets)
balance = fred.get_series("WALCL")
# IOER
ioer = fred.get_series("IORB")
```

### ② Banque Centrale Européenne (BCE) — Zone Euro

| Élément | Détail |
|---|---|
| **Réunions** | 8/an (rythme similaire Fed depuis 2015) |
| **Mandat** | Price stability (2% HICP) |
| **Taux pilote** | Deposit Facility Rate, Main Refinancing Rate |
| **Outils** | TLTRO (prêts long terme aux banques), APP/PEPP (achats actifs) |
| **Spécificité** | Forward guidance + "data-dependence" Lagarde |

**TLTRO** : opérations de refinancement à 3-4 ans qui injectent de la
liquidité dans le système bancaire européen. Quand la BCE les rembourse
massivement (2023-2025), c'est un QE inversé — contraction de liquidité.

### ③ Banque du Japon (BOJ) — Japon

| Élément | Détail |
|---|---|
| **Réunions** | 8/an |
| **Mandat** | Price stability (+2% CPI) |
| **Taux pilote** | Short-term policy rate |
| **Spécificité** | Yield Curve Control (YCC) jusqu'en mars 2024 |
| **Impact** | Carry trade JPY (emprunter JPY 0% → investir ailleurs) |

Le **carry trade JPY** est LE trade macro le plus important : des centaines
de milliards empruntés en yen à 0% et investis en USD/EUR/EM. Quand la BOJ
monte ses taux, ce trade se déboucle → appréciation massive du JPY, vente
d'actifs USD/EUR (le "carry unwind" d'août 2024 a fait -10% sur le SPX en
2 jours).

**Surveiller :**
- Taux BOJ vs taux US (spread JPY/USD)
- Positions nettes spéculatives JPY (COT report)
- Inflation japonaise (CPI core, CPI services)

### ④ Banque d'Angleterre (BOE) — UK

| Élément | Détail |
|---|---|
| **Réunions** | 8/an |
| **Mandat** | Price stability (2% CPI) + financial stability |
| **Taux pilote** | Bank Rate |
| **Spécificité** | QT actif (trésorerie + gilt sales), plus agressive que la Fed |

### ⑤ Banque Populaire de Chine (PBoC) — Chine

| Élément | Détail |
|---|---|
| **Réunions** | Pas de calendrier fixe — décisions discrétionnaires |
| **Taux pilote** | LPR (Loan Prime Rate), MLF (Medium-term Lending Facility) |
| **Spécificité** | Politique macroprudentielle forte, contrôle des changes |
| **Impact** | Influence directe sur les commodités (cuivre, minerai de fer, pétrole) |

La PBoC annonce souvent ses décisions le 20 de chaque mois pour le LPR,
et les changements de RRR (reserve requirement ratio) de façon imprévue.

## Modélisation des décisions de taux

### Probabilités FedWatch / WIRP

Utiliser les **fed funds futures** (contrat ZQ au CME) pour extraire la
probabilité de hausse/baisse implicite :

```python
# Exemple : probabilité de baisse de 25bp à la prochaine réunion
prix_futur = 95.50
taux_implicite = 100 - prix_futur  # = 4.50%
taux_actuel = 4.50
proba_baisse = 1.0  # 100% si taux_implicite < taux_actuel
```

Approximation simple :
```
P(change) = (taux_futur - taux_actuel) / amplitude_change
```

Pour des probabilités précises → scraper CME FedWatch Tool
(`https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html`)
via `ai_scrape`.

### Réaction type par actif (Fed)

| Décision | USD | SPX | BTC | Or | Obligations 2Y |
|---|---|---|---|---|---|
| **Hike 25bp (attendu)** | ↗ modéré | ↘ modéré | ↘ | →/↘ | ↗ |
| **Hike 50bp (hawkish surprise)** | ↗↗ fort | ↘↘ fort | ↘↘ | ↘ fort | ↗↗ fort |
| **Hold (attendu)** | → | → | → | → | → |
| **Cut 25bp (attendu)** | ↘ modéré | ↗ modéré | ↗ | ↗ | ↘ |
| **Cut 50bp (dovish surprise)** | ↘↘ fort | ↗↗ fort | ↗↗ | ↗ fort | ↘↘ fort |

**Attention :** une baisse de taux en urgence (inter-meeting cut) ou en
contexte de crise = risque extrême, pas bullish. Exemple : mars 2020.

## Forward Guidance — Décoder le langage

### Fed (Powell)

Les communiqués FOMC ont un paragraphe standardisé. Les modifications d'un
mot changent tout :

| Phrase | Signal |
|---|---|
| "The Committee judges that risks remain" → neutre |
| "The Committee is highly attentive to inflation risks" → hawkish |
| "The Committee is prepared to adjust the stance" → prêt à bouger |
| "Ongoing reductions in the balance sheet" → QT continue |
| "Gradual pace" → changement lent |
| "Considered appropriate" → l'engagement est faible |

### BCE (Lagarde)

Le langage BCE est plus codé :
- "Determined" → engagement fort
- "Gradual" / "incremental" → hausses lentes
- "Acknowledged the risks" → pas d'action immédiate
- "Data-dependence remains" → aucune guidance ferme

## QT (Quantitative Tightening) — L'outil silencieux

Le QT est la réduction du bilan des banques centrales. Il agit comme
un "hike fantôme" :

```
Bilan Fed (2022) = ~9T → (2025) = ~7T → cible (2027) = ~5.5T
```

**Impact QT :**
- Réduit les réserves bancaires → serre la liquidité
- Les obligations que la Fed ne rachète plus doivent être absorbées par le
  marché → pression haussière sur les yields
- Corrélé négativement avec BTC et actifs risqués
- Le QT peut être arrêté sans hausse des taux (2019 repo crisis)

**Surveiller :**
```
Fed balance sheet : FRED série WALCL (hebdo, jeudi)
ON RRP facility   : FRED série RRPONTSYD (réserves excédentaires)
Reverse repo use  : descendre = less liquidity
```

## Pièges à éviter

1. **"Buy the rumor, sell the fact"** : Une hausse de taux anticipée à 95%
   est déjà dans le prix. Le mouvement important est souvent sur l'écart
   entre la décision et l'anticipation, pas la décision elle-même.
2. **Conférence de presse ≠ communiqué** : Le communiqué est écrit, pesé.
   La conférence de presse est improvisée — c'est là que les vraies surprises
   arrivent (volatilité maximale pendant 30 min).
3. **Forward guidance non contraignante** : "Higher for longer" peut changer
   en un mois si les données dévient. Ne pas trader la guidance seule.
4. **Interdépendance des banques centrales** : La BOJ monte → carry trade
   unwind → USD/JPY chute → le dollar se raffermit → les EM souffrent.
   Tout est connecté.
5. **Les décisions unanimes vs divisées** : Un vote 9-1 ou 8-2 est un
   signal fort de division interne. Le dissident est souvent plus important
   que la décision majoritaire.
6. **L'effet calendrier :** Ne pas trader 30 min avant et 60 min après
   les annonces des banques centrales — le spread explose, le slippage est
   maximal et les liquidations en chaîne faussent les prix.

## Vérification

- [ ] Calendrier des réunions Fed/BCE/BOJ/BOE importé et cross-référencé
- [ ] Probabilités FedWatch extraites avant chaque réunion
- [ ] Positions ajustées si probabilité de surprise >30%
- [ ] Langage du communiqué analysé (hawkish/dovish shift)
- [ ] Bilan banque centrale surveillé (QT/QE status)
- [ ] Carry trade JPY surveillé via COT + spread BOJ-Fed

## Skills liés

- `macro-indicateurs` — données qui alimentent les décisions des banques centrales
- `value-at-risk` — intégrer le risque de politique monétaire