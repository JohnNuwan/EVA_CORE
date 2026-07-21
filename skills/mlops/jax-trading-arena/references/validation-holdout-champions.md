# Validation holdout + champions rejouables (E.V.A)

Détail des 3 correctifs qui rendent une arène génétique exploitable et
anti-overfitting. Session : pipeline E.V.A (dépôt `~/jepa_eva`, remote
github.com/JohnNuwan/jepa_eva). Référence maîtresse : `jax-trading-arena`.

## 1. Trades discrets (win_rate / profit_factor réels)

L'arène de base simule une position continue mark-to-market — elle ne suit
PAS les trades individuels, donc win_rate / profit_factor / nb_trades = 0
dans le registry et la promotion n'utilise que fitness+DD.

**Correctif** : étendre `EtatSimulation` avec 5 champs scalaires
(`nb_trades`, `trades_gagnants`, `profit_brut`, `perte_brute`,
`pnl_trade_courant`) et détecter la fermeture d'un trade à chaque pas :

```python
pnl_trade = etat.pnl_trade_courant + retour_net
changement_signe = (
    (etat.position != 0.0) & (signal != 0.0)
    & (jnp.sign(signal) != jnp.sign(etat.position))
)
retour_neutre = (etat.position != 0.0) & (signal == 0.0)
trade_ferme = changement_signe | retour_neutre
gagne = trade_ferme & (pnl_trade > 0.0)
perd = trade_ferme & (pnl_trade <= 0.0)
# profit_brut += pnl_trade si gagne ; perte_brute += -pnl_trade si perd
# pnl_trade_courant = 0 si trade_ferme sinon pnl_trade
```

Puis dans le calcul de fitness :

```python
win_rate = trades_gagnants / max(nb_trades, 1) * 100  # si nb_trades > 0
profit_factor = profit_brut / max(perte_brute, 1e-9)
```

Résultat réel (gen23) : wr 25 %, pf 28.1, 12 trades — métriques réelles
exploitables pour la promotion multi-critères (Pattern #15 : WR>55 %,
PF>1.3, DD<5 %, >30 trades).

## 2. Sauvegarde des poids du champion (rejouable)

Le registry ne trace que des métriques — sans les poids, impossible de
rejouer/backtester/déployer le champion. **Bloquant** pour toute la suite.

```python
poids = jax.tree.map(lambda p: np.asarray(p[idx]), population)
aplati, _ = jax.tree.flatten(poids)
donnees = {f"p{i}": np.asarray(f) for i, f in enumerate(aplati)}
donnees["generation"] = np.asarray(gen)
donnees["fitness"] = np.asarray(metriques["fitness"])
np.savez_compressed(dossier / f"champion_gen{gen}.npz", **donnees)
```

Rechargement : reconstruire le `ParametresWorldModel` NamedTuple dans
l'ordre des 6 feuilles (w_ih, w_hh, b_ih, b_hh, w_recompense, w_valeur),
puis `arene.population = jax.tree.map(lambda p: p[None], params)` pour une
arène à population 1.

## 3. Backtest holdout + promotion conditionnelle

**Anti-overfitting clé** : l'arène s'entraîne sur barres [0 : 80 %], mais
le champion n'a de valeur que s'il généralise sur le holdout [80 % : 100 %].

- `backtest_validation.py` : recharge un champion, l'évalue sur le
  holdout, émet un verdict GÉNÉRALISE (np>0 et dd≤5 %) ou SURAPPRENTISSAGE.
- `train_arena_validated.py` : boucle train→backtest→promotion. À chaque
  génération, le champion est évalué sur le holdout toutes les N gens ; il
  n'est promu+sauvegardé QUE s'il généralise.

**Résultat réel (200 gens, XAUUSD M15, pop=64)** :
- 1 champion généralise sur 40 validations : gen4 (+5.06 % holdout,
  dd 0.08 %, pf 17.15, 70 trades) — alors que son fitness_train n'était
  que 0.545. La sélection par généralisation trouve des perles que la
  fitness train seule rate.
- La boucle détecte la dérive : après gen ~50, l'arène surapprend
  (holdout −13 %, dd 26 %) — preuve que la validation holdout est
  indispensable.

**Verdicts sur 4 champions (backtest_validation.py)** :
gen0 +2.31 % (généralise), gen1 +8.15 % (généralise), gen9 −1.44 %
(surapprend), gen23 −8.14 % (surapprend).

**Leçon** : ne jamais promouvoir sur la seule fitness train. Prochaine
amélioration : injecter le score holdout dans la fitness d'évolution
(sélectionner les parents sur leur capacité à généraliser).

## Dépôt git

`/home/aza/jepa_eva` (isolé de ftmo_agent), remote
github.com/JohnNuwan/jepa_eva (branche main). Commits : base E.V.A,
correctifs trades/champions/backtest, boucle validée. Push via token dans
l'URL puis retrait du token de la config remote (`git remote set-url`).
