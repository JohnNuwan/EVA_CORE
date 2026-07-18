---
name: market-analysis
category: finance
description: >
  Calcule les niveaux de support et résistance, les moyennes mobiles simples (SMA)
  et l'indice de force relative (RSI) d'un actif financier en utilisant les prix historiques.
  Génère des signaux de trading (Achat, Vente, Neutre) à partir de critères techniques.
triggers:
  - "calculer les supports et résistances d'un actif"
  - "analyser techniquement une action ou une crypto-monnaie"
  - "générer des signaux d'achat et de vente basés sur le RSI et les SMA"
  - "faire une analyse journalière des prix d'un symbole financier"
---

# Analyse Technique de Marché — Supports, Résistances, SMA et RSI

## Portée

Ce skill définit la méthodologie d'analyse technique d'EVA pour étudier les cours d'actifs financiers et identifier des opportunités de trading. Elle s'appuie sur quatre piliers techniques :
1. **Moyennes Mobiles Simples (SMA) :** Comparaison d'une moyenne rapide (ex: 30 jours) et d'une moyenne lente (ex: 60 jours) pour déterminer la direction de la tendance.
2. **Supports et Résistances :** Identification des niveaux de prix psychologiques où les forces acheteuses et vendeuses se sont précédemment affrontées (calculés sur des fenêtres glissantes de 5 bougies).
3. **Relative Strength Index (RSI) :** Mesure de la force du mouvement pour identifier les zones de survente (RSI < 30) et de surachat (RSI > 70).
4. **Génération de Signaux :** Combinaison de ces indicateurs pour générer des alertes de trading structurées.

## Logique de Signal de Trading (Algorithme d'Enzo)

Pour valider un signal d'achat ou de vente, les conditions suivantes doivent être réunies simultanément :

### 🟢 Signal d'Achat (Buy Signal = 1)
1. **Rebond ou Cassure de Résistance :** La clôture de la bougie précédente était inférieure à la résistance lissée, et la bougie actuelle casse cette résistance avec une marge de sécurité (`clôture > résistance * 1.005`).
2. **Tendance Haussière :** La moyenne mobile rapide (SMA 30) est supérieure à la moyenne mobile lente (SMA 60).
3. **Momentum Ascendant :** Le RSI actuel est inférieur au RSI de la bougie précédente (correction de momentum pour un point d'entrée optimal).

### 🔴 Signal de Vente (Sell Signal = -1)
1. **Rebond ou Cassure de Support :** La clôture de la bougie précédente était supérieure au support lissé, et la bougie actuelle casse ce support avec une marge de sécurité (`clôture < support * 1.005`).
2. **Tendance Baissière :** La moyenne mobile rapide (SMA 30) est inférieure à la moyenne mobile lente (SMA 60).
3. **Momentum Descendant :** Le RSI actuel est supérieur au RSI de la bougie précédente.

## Configuration requise pour l'outil

L'outil associé `finance_analyse_technique` doit être utilisé pour exécuter cette logique programmatique. Il accepte les paramètres suivants :
- `symbol` (str) : Le symbole de l'actif (ex: `GOLD`, `EURUSD`, `AAPL`).
- `timeframe` (str) : L'unité de temps (ex: `D1` pour journalier, `H4` pour 4 heures, `H1` pour 1 heure).
- `num_bars` (int) : Le nombre de bougies historiques à récupérer (par défaut `200`).

## Pièges à éviter

1. **Calcul des Supports/Résistances sur données insuffisantes :** Le calcul nécessite un décalage (shift) sur 5 bougies. Assurez-vous d'avoir au moins 15-20 bougies historiques pour éviter les valeurs `NaN`.
2. **Sensibilité du RSI :** Le RSI utilise une fenêtre de 10 périodes par défaut dans cette stratégie. Un mouvement brusque de prix peut saturer rapidement le RSI.
3. **Filtre de Tendance :** N'exécutez jamais d'achat si la SMA 30 is sous la SMA 60, car vous traderiez contre la tendance de fond.

## Verification

1. Lancer l'analyse sur un actif via le tool :
   ```python
   resultat = finance_analyse_technique(symbol="GOLD", timeframe="D1", num_bars=100)
   ```
2. Vérifier que la structure renvoie bien le dernier prix, les niveaux de supports/résistances calculés, et le signal final (`1`, `-1`, ou `0`).
