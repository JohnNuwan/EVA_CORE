"""Vérifie la calibration du sizer : perte au SL ≈ risque cible par symbole.

Réutilisable : python scripts/verify-sizer.py
Sortie : tableau lot_max + perte au SL pour SL=5 sur chaque classe d'actif.
Doit afficher perte ≈ 1 % equity (1000 $ pour 100 k$). Sinon, mauvaise
calibration de taille_contrat (Pattern trading-action-layer).
"""

from dataclasses import dataclass

RISQUE_PCT = 1.0
EQUITY = 100_000.0
DISTANCE_SL = 5.0


@dataclass(frozen=True)
class SpecSymbole:
    nom: str
    taille_contrat: float
    prix: float


SPECS = [
    SpecSymbole("XAUUSD", 100.0, 2000.0),
    SpecSymbole("EURUSD", 100_000.0, 1.10),
    SpecSymbole("BTCUSD", 1.0, 90_000.0),
]


def lot_max_risque(equity: float, prix: float, distance_sl: float,
                   taille_contrat: float, levier: float = 100.0) -> float:
    """Lot max tel que perte au SL ≤ risque cible (1 % equity)."""
    risque = equity * (RISQUE_PCT / 100.0)
    lot_risque = risque / (distance_sl * taille_contrat)
    lot_marge = (equity * levier) / (prix * taille_contrat)
    return min(lot_risque, lot_marge)


def main() -> int:
    risque_cible = EQUITY * RISQUE_PCT / 100.0
    print(f"Risque cible : {risque_cible:.0f} $ (1 % de {EQUITY:.0f} $)\n")
    print(f"{'Symbole':10s} {'Contrat':>10s} {'lot_max':>10s} {'perte@SL':>12s}  OK?")
    tout_ok = True
    for s in SPECS:
        lot = lot_max_risque(EQUITY, s.prix, DISTANCE_SL, s.taille_contrat)
        perte = lot * s.taille_contrat * DISTANCE_SL
        ok = abs(perte - risque_cible) / risque_cible < 0.05
        tout_ok = tout_ok and ok
        print(f"{s.nom:10s} {s.taille_contrat:>10.0f} {lot:>10.2f} "
              f"{perte:>11.2f}$  {'OUI' if ok else 'NON — mauvaise calibration'}")
    print("\nTous les symboles calibrés." if tout_ok else
          "\nCALIBRATION FAUSSE sur ≥1 symbole (cf. ci-dessus).")
    return 0 if tout_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
