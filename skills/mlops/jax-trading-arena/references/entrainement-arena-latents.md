# Entraînement Arène E.V.A sur latents réels + Champion Registry

Session 2026-07-19 — pipeline complet validé sur The Hive (2× RTX 3090).

## Chaîne complète validée

```
data/XAUUSD_m15.csv (50 000 barres MT5)
  → precompute_latents.py  (encodeur JEPA figé, chunk ≤512)
  → latents/XAUUSD_m15_latents.npz  (prix 50000 + latents 50000×128)
  → train_arena.py  (JaxGeneticArena 64 agents, multi-générations)
  → registry_arena/XAUUSD_registry.jsonl  (champions promus)
```

## Fichiers produits

- `~/ftmo_agent/precompute_latents.py` — encode tout l'historique avec
  l'encodeur figé. **Chunk à 512 barres** (position embedding = 512 ; un
  chunk 4096 lève `ValueError: Séquence 4096 > position embedding 512`).
- `~/ftmo_agent/train_arena.py` — boucle multi-générations. Évalue 64
  agents sur segment aléatoire de la zone d'entraînement (80% des barres),
  évolution, promotion des champions. CLI : `--generations 100 --segment 512`.
- `~/ftmo_agent/latents/XAUUSD_m15_latents.npz` — prix (50000,) + latents
  (50000, 128), std 1.53, finis.
- `~/ftmo_agent/registry_arena/XAUUSD_registry.jsonl` — JSONL des champions.

## ChampionRegistry (Pattern #15)

Critères de promotion multi-critères (constants de classe) :
`MIN_WIN_RATE=55.0`, `MIN_PROFIT_FACTOR=1.3`, `MAX_DRAWDOWN=5.0`,
`MIN_TRADES=30`. Méthode `promotion_digne(metriques)` exige TOUS les
critères ; `enregistrer(generation, metriques)` append en JSONL.

**LIMITE ACTUELLE (honnête)** : l'arène simule une position continue
mark-to-market, PAS des trades discrets avec SL/TP. Donc `win_rate`,
`profit_factor`, `nb_trades` = 0 dans le registry — la promotion utilise
seulement `fitness + drawdown`. Pour une promotion complète Pattern #15,
il faut enrichir l'arène pour suivre les trades discrets (ouverture/SL/TP/
fermeture) et compter win_rate/PF/nb_trades réels.

## Bug simulation corrigé (à ne pas réintroduire)

Avant : rendement depuis `prix_entree` figé → composition du drift →
net_profit +3308%, sortino 13829 (artefact de levier non borné). Fitness
oscillait -181 → +2293 entre générations (segment aléatoire + explosion).

Après (mark-to-market) : rendement = position × variation prix barre-à-barre,
`prix_entree = prix` de la barre précédente, init `prix_seq[0]`. Résultats
réalistes : record fitness 3.41 (np +4.03%, dd 0.81% sur 512 barres),
progression par paliers 0.21→0.83→1.56→2.08→2.67→3.41 en 100 générations
(signature d'une vraie évolution, ~8 gen/s).

## Prochaine étape (non faite)

1. Sauvegarder les POIDS du champion (pas juste les métriques) pour
   rejouer/backtester le meilleur agent sur la période de validation (20%
   jamais vus, barres 40000+).
2. Enrichir l'arène pour trades discrets (win_rate/PF/nb_trades réels).
3. Entraîner le world model GRU (prédire H_{t+1} depuis H_t+action) pour
   que le CEM planifie sur des transitions apprises plutôt qu'aléatoires.
