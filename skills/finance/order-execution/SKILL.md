---
name: order-execution
category: finance
description: >
  Gère l'exécution sécurisée d'ordres de trading (Achat, Vente) sur MetaTrader 5
  avec des règles strictes de gestion du risque (Stop Loss, Take Profit, taille de lot).
triggers:
  - "exécuter un ordre d'achat ou de vente sur MetaTrader 5"
  - "ouvrir une position de trading sur GOLD ou une action"
  - "calculer la taille de lot et le stop loss pour un trade"
  - "gérer les positions de trading en cours d'EVA"
---

# Exécution d'Ordres de Trading — MetaTrader 5 & Gestion du Risque

## Portée

Ce skill définit les règles opérationnelles d'EVA pour interagir avec la plateforme MetaTrader 5 (soit via l'API locale soit via la passerelle REST API) pour passer et gérer des ordres de trading. L'accent est mis sur la préservation du capital et la gestion du risque.

## Règles de Gestion du Risque (Money Management)

Avant d'ouvrir une position, les critères suivants doivent être validés :
1. **Risque Maximum par Trade :** Ne jamais risquer plus de **1% à 2%** du capital total disponible sur le compte pour un seul trade.
2. **Calcul de la taille du lot :** La taille du lot doit être calculée dynamiquement à partir de la distance au Stop Loss :
   `Lot = (Capital * Risque%) / (Distance_SL_en_points * Valeur_du_point)`.
3. **Marge de Sécurité :** Toujours définir un **Stop Loss (SL)** et un **Take Profit (TP)** dès la soumission de l'ordre. Aucun trade "à découvert" sans protection n'est toléré.
4. **Calcul du SL et TP par défaut :**
   - Pour un **Achat (Buy) :**
     - Le Stop Loss est placé juste en dessous du dernier support majeur calculé.
     - Le Take Profit est placé juste en dessous de la prochaine résistance majeure.
     - Le ratio Risque/Rendement (Risk/Reward) doit être d'au moins **1:1.5** (le gain potentiel doit être 1.5 fois supérieur au risque).

## Actions opérationnelles (via l'outil finance_order_execution)

L'outil associé `finance_order_execution` expose les fonctions nécessaires :
- `action` (str) : `'buy'` pour acheter, `'sell'` pour vendre, `'close'` pour fermer, `'status'` pour obtenir l'état du compte.
- `symbol` (str) : Nom du symbole (ex: `GOLD`, `EURUSD`).
- `lot` (float) : Volume de transaction calculé (ex: `0.1`, `1.0`).
- `stop_loss` (float, optionnel) : Niveau de prix du Stop Loss.
- `take_profit` (float, optionnel) : Niveau de prix du Take Profit.

## Pièges à éviter

1. **Trade pendant les annonces économiques majeures :** Éviter d'ouvrir des positions 30 minutes avant et après des annonces à fort impact (ex: NFP, décisions de taux d'intérêt de la Fed).
2. **Glissement de prix (Slippage) :** Utiliser un écart (deviation) raisonnable (ex: 10 points) pour éviter que l'ordre ne soit exécuté à un prix défavorable.
3. **Erreur d'initialisation MT5 :** Si le terminal MT5 n'est pas démarré ou n'est pas connecté à un compte de démonstration/réel, l'outil échouera proprement et informera l'agent.

## Vérification

1. Récupérer le solde du compte :
   ```python
   statut = finance_order_execution(action="status")
   ```
2. Ouvrir un trade d'achat de démonstration avec Stop Loss et Take Profit :
   ```python
   trade = finance_order_execution(
       action="buy",
       symbol="EURUSD",
       lot=0.01,
       stop_loss=1.0800,
       take_profit=1.0950
   )
   ```
3. Valider que la plateforme renvoie un code de retour de transaction réussi (`retcode = 10009` pour l'exécution).
