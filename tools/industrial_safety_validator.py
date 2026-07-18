#!/usr/bin/env python3
"""Module Industrial Safety Validator - Calcul SIL, PFD, PFH selon IEC 61508/61511 et PL selon EN ISO 13849-1."""
import json
import logging
import math

logger = logging.getLogger(__name__)


def _pfd_1oo1(lam_du: float, ti_hours: float, beta: float = 0.0) -> float:
    """Calcule la PFDavg pour une architecture 1oo1.

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune (non utilisé pour 1oo1).

    Returns:
        float: Valeur de la PFDavg.
    """
    return lam_du * ti_hours / 2.0


def _pfd_1oo2(lam_du: float, ti_hours: float, beta: float = 0.05) -> float:
    """Calcule la PFDavg pour une architecture 1oo2 avec CCF.

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune.

    Returns:
        float: Valeur de la PFDavg.
    """
    indep = (lam_du * ti_hours) ** 2 / 3.0
    ccf = beta * lam_du * ti_hours / 2.0
    return indep + ccf


def _pfd_2oo3(lam_du: float, ti_hours: float, beta: float = 0.05) -> float:
    """Calcule la PFDavg pour une architecture 2oo3.

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune.

    Returns:
        float: Valeur de la PFDavg.
    """
    indep = (lam_du * ti_hours) ** 2
    ccf = beta * lam_du * ti_hours / 2.0
    return indep + ccf


def _pfd_2oo2(lam_du: float, ti_hours: float, beta: float = 0.0) -> float:
    """Calcule la PFDavg pour une architecture 2oo2.

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune (non utilisé pour 2oo2).

    Returns:
        float: Valeur de la PFDavg.
    """
    return lam_du * ti_hours


def _pfd_1oo2D(lam_du: float, ti_hours: float, beta: float = 0.05, dc: float = 0.9) -> float:
    """Calcule la PFDavg pour une architecture 1oo2D (1oo2 avec diagnostic).

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune.
        dc: Taux de couverture de diagnostic.

    Returns:
        float: Valeur de la PFDavg.
    """
    indep = 2.0 * (1.0 - dc) * (lam_du * ti_hours) ** 2 / 3.0
    ccf = beta * lam_du * ti_hours / 2.0
    return indep + ccf


def _pfd_2oo2D(lam_du: float, ti_hours: float, beta: float = 0.05, dc: float = 0.9) -> float:
    """Calcule la PFDavg pour une architecture 2oo2D (2oo2 avec diagnostic).

    Args:
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune.
        dc: Taux de couverture de diagnostic.

    Returns:
        float: Valeur de la PFDavg.
    """
    indep = (lam_du * ti_hours) ** 2 * (1.0 - dc)
    ccf = beta * lam_du * ti_hours / 2.0
    return indep + ccf


def _sil_from_pfd(pfd: float) -> int:
    """Détermine le niveau SIL en fonction de la PFDavg.

    Args:
        pfd: Valeur de la PFDavg.

    Returns:
        int: Niveau SIL (0 à 4).
    """
    if pfd >= 1e-1: return 0
    if pfd >= 1e-2: return 1
    if pfd >= 1e-3: return 2
    if pfd >= 1e-4: return 3
    if pfd >= 1e-5: return 4
    return 4


_SIL_RANGES = {1: (1e-2, 1e-1), 2: (1e-3, 1e-2), 3: (1e-4, 1e-3), 4: (1e-5, 1e-4)}


def _calculate_pl(category: str, mttfd_years: float, dcavg: float) -> str:
    """Détermine le Performance Level (PL) selon la norme EN ISO 13849-1.

    Args:
        category: Catégorie de sécurité (Cat B, Cat 1, Cat 2, Cat 3, Cat 4).
        mttfd_years: Mean Time To Dangerous Failure (années).
        dcavg: Taux moyen de couverture de diagnostic.

    Returns:
        str: Niveau PL (a, b, c, d, e ou 'N/A').
    """
    # Évaluation du niveau de MTTFd
    if mttfd_years < 3.0:
        mttfd_level = "Very Low"
    elif mttfd_years < 10.0:
        mttfd_level = "Low"
    elif mttfd_years < 30.0:
        mttfd_level = "Medium"
    else:
        mttfd_level = "High"

    # Évaluation du niveau de DCavg (forcé à None pour Cat B et Cat 1)
    if category in ("Cat B", "Cat 1") or dcavg < 0.60:
        dc_level = "None"
    elif dcavg < 0.90:
        dc_level = "Low"
    elif dcavg < 0.99:
        dc_level = "Medium"
    else:
        dc_level = "High"

    # Matrice simplifiée EN ISO 13849-1
    pl_matrix = {
        # Cat B
        ("Cat B", "Low", "None"): "a",
        ("Cat B", "Medium", "None"): "b",
        ("Cat B", "High", "None"): "b",
        # Cat 1
        ("Cat 1", "Low", "None"): "a",
        ("Cat 1", "Medium", "None"): "b",
        ("Cat 1", "High", "None"): "c",
        # Cat 2
        ("Cat 2", "Low", "None"): "a",
        ("Cat 2", "Low", "Low"): "a",
        ("Cat 2", "Low", "Medium"): "b",
        ("Cat 2", "Medium", "Low"): "b",
        ("Cat 2", "Medium", "Medium"): "c",
        ("Cat 2", "High", "Low"): "c",
        ("Cat 2", "High", "Medium"): "d",
        # Cat 3
        ("Cat 3", "Low", "Low"): "b",
        ("Cat 3", "Low", "Medium"): "c",
        ("Cat 3", "Medium", "Low"): "c",
        ("Cat 3", "Medium", "Medium"): "d",
        ("Cat 3", "High", "Low"): "d",
        ("Cat 3", "High", "Medium"): "e",
        # Cat 4
        ("Cat 4", "Low", "High"): "c",
        ("Cat 4", "Medium", "High"): "d",
        ("Cat 4", "High", "High"): "e",
    }

    # Fallbacks pour les combinaisons hors matrice standard
    key = (category, mttfd_level, dc_level)
    if key in pl_matrix:
        return pl_matrix[key]
    
    # Estimations par défaut
    if category == "Cat 4" and dc_level == "High" and mttfd_level in ("Medium", "High"):
        return "e"
    if category in ("Cat 3", "Cat 4") and dc_level in ("Low", "Medium"):
        return "d"
    if category == "Cat 2":
        return "c"
    return "b" if mttfd_level != "Low" else "a"


def _get_pfd_calculator(architecture: str, dc: float):
    """Retourne la fonction de calcul de PFDavg appropriée."""
    calc_fn = {
        "1oo1": _pfd_1oo1,
        "1oo2": _pfd_1oo2,
        "2oo3": _pfd_2oo3,
        "2oo2": _pfd_2oo2,
        "1oo2D": lambda l, t, b: _pfd_1oo2D(l, t, b, dc),
        "2oo2D": lambda l, t, b: _pfd_2oo2D(l, t, b, dc)
    }
    return calc_fn.get(architecture, _pfd_1oo1)


def calculate_sil(architecture: str = "1oo1", lam_du: float = 1e-6,
                  ti_hours: float = 8760, beta: float = 0.05, dc: float = 0.9,
                  include_report: bool = True) -> str:
    """Calcule SIL / PFDavg / PFH pour une architecture donnée et PL EN ISO 13849-1.

    Args:
        architecture: Architecture safety (1oo1, 1oo2, 2oo3, 2oo2, 1oo2D, 2oo2D).
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        ti_hours: Proof Test Interval (heures).
        beta: Facteur de défaillance de cause commune.
        dc: Couverture de diagnostic moyenne.
        include_report: Indique si un rapport Markdown doit être généré.

    Returns:
        str: Rapport de calcul SIL et PL au format JSON.
    """
    fn = _get_pfd_calculator(architecture, dc)
    pfd = fn(lam_du, ti_hours, beta)

    pfd_rounded = round(pfd, 8)
    pfh = pfd / ti_hours if ti_hours > 0 else 0
    sil = _sil_from_pfd(pfd)

    # Calcul PL (EN ISO 13849-1)
    mttfd_hours = 1.0 / lam_du if lam_du > 0 else float('inf')
    mttfd_years = min(100.0, mttfd_hours / 8760.0)  # Capping à 100 ans par canal

    # Déterminer la catégorie théorique à partir de l'architecture
    category_map = {
        "1oo1": "Cat 1" if mttfd_years >= 30.0 else "Cat B",
        "2oo2": "Cat 2",
        "1oo2": "Cat 3",
        "2oo3": "Cat 4",
        "1oo2D": "Cat 4",
        "2oo2D": "Cat 4"
    }
    category = category_map.get(architecture, "Cat B")
    pl = _calculate_pl(category, mttfd_years, dc)

    result = {
        "architecture": architecture,
        "lam_du": lam_du,
        "lam_du_str": f"{lam_du:.2e} /h",
        "proof_test_interval_hours": ti_hours,
        "proof_test_interval_years": round(ti_hours / 8760, 2),
        "beta_ccf": beta,
        "dc": dc,
        "pfdavg": pfd_rounded,
        "pfh": round(pfh, 12),
        "sil_level": sil,
        "sil_target_achieved": False,
        "mttfd_years": round(mttfd_years, 1),
        "iso13849_category": category,
        "iso13849_pl": pl
    }

    # Vérification pour chaque SIL
    for sil_level, (pfd_min, pfd_max) in _SIL_RANGES.items():
        if pfd_min <= pfd < pfd_max:
            result["sil_target_achieved"] = True
            result["achieved_sil"] = sil_level
            break

    # Recommandation PTI optimal
    for target_sil in [3, 2, 1]:
        target_pfd_max = 10 ** (-target_sil) if target_sil > 0 else 0.1
        max_ti = target_pfd_max * 2 / lam_du if lam_du > 0 else 0
        if max_ti > 0:
            result[f"optimal_pti_sil{target_sil}_hours"] = round(max_ti)

    if include_report:
        md = f"""# Rapport de Vérification de Sécurité Fonctionnelle (SIL & PL)

## Configuration d'Entrée
- **Architecture :** {architecture}
- **λDU :** {lam_du:.2e} /h
- **Proof Test Interval :** {ti_hours}h ({ti_hours/8760:.2f} ans)
- **β (CCF) :** {beta}
- **Couverture Diagnostic (DC) :** {dc * 100:.1f}%

## Résultats IEC 61508 / IEC 61511 (Sécurité des Procédés)
- **PFDavg :** {pfd_rounded:.2e}
- **PFH :** {pfh:.2e} /h
- **Niveau SIL Atteint :** SIL {sil}
- **Validation Cible SIL :** {'✅ Atteint' if result['sil_target_achieved'] else '❌ Non Atteint'}

## Résultats EN ISO 13849-1 (Sécurité des Machines)
- **MTTFd (par canal) :** {result['mttfd_years']} ans
- **Catégorie :** {category}
- **Performance Level (PL) Atteint :** PL {pl}
"""
        return json.dumps({"markdown_report": md, "data": result}, indent=2, ensure_ascii=False)

    return json.dumps(result, indent=2, ensure_ascii=False)


def optimize_pti(target_sil: int, lam_du: float, architecture: str = "1oo1", beta: float = 0.05, dc: float = 0.9) -> str:
    """Optimise le Proof Test Interval pour atteindre un SIL cible.

    Args:
        target_sil: Niveau SIL cible (1, 2, 3).
        lam_du: Taux de défaillance dangereuse non détectée (/h).
        architecture: Architecture safety.
        beta: Facteur de défaillance de cause commune.
        dc: Couverture de diagnostic moyenne.

    Returns:
        str: Résultat de l'optimisation au format JSON.
    """
    target_pfd_max = 10 ** (-target_sil)
    fn = _get_pfd_calculator(architecture, dc)
    opt_fn = lambda ti: fn(lam_du, ti, beta)

    # Recherche binaire
    lo, hi = 1.0, 100.0 * 8760.0  # 1h à 100 ans
    best_ti = hi
    for _ in range(50):
        mid = (lo + hi) / 2.0
        if fn(mid) <= target_pfd_max:
            best_ti = mid
            lo = mid
        else:
            hi = mid

    return json.dumps({
        "target_sil": target_sil,
        "architecture": architecture,
        "lam_du": lam_du,
        "optimal_pti_hours": round(best_ti),
        "optimal_pti_years": round(best_ti / 8760.0, 1),
        "pfdavg_at_optimal": round(fn(best_ti), 8),
    }, indent=2)


from tools.registry import registry

registry.register(
    name="safety_calculate_sil", toolset="industrial",
    schema={
        "name": "safety_calculate_sil",
        "description": "Calcule SIL, PFDavg, PFH pour une architecture de sécurité (IEC 61508/61511).",
        "parameters": {
            "type": "object",
            "properties": {
                "architecture": {"type": "string", "enum": ["1oo1", "1oo2", "2oo3", "2oo2", "1oo2D", "2oo2D"],
                                  "description": "Architecture (1oo1, 1oo2, 2oo3, 2oo2, 1oo2D, 2oo2D)"},
                "lam_du": {"type": "number", "description": "Taux défaillance dangereuse non détectée (/h)"},
                "ti_hours": {"type": "number", "description": "Proof Test Interval (heures, défaut: 8760 = 1 an)"},
                "beta": {"type": "number", "description": "Common Cause Failure factor (défaut: 0.05)"},
                "dc": {"type": "number", "description": "Diagnostic Coverage (défaut: 0.90)"}
            },
            "required": ["architecture", "lam_du"]
        }
    },
    handler=lambda a, **kw: calculate_sil(
        architecture=a.get("architecture", "1oo1"),
        lam_du=float(a.get("lam_du", 1e-6)),
        ti_hours=float(a.get("ti_hours", 8760)),
        beta=float(a.get("beta", 0.05)),
        dc=float(a.get("dc", 0.90)),
    ),
    is_async=False,
    description="Calculer SIL et PFDavg pour une architecture safety.",
    emoji="🛡️",
)

registry.register(
    name="safety_optimize_pti", toolset="industrial",
    schema={
        "name": "safety_optimize_pti",
        "description": "Optimise le Proof Test Interval pour atteindre un SIL cible.",
        "parameters": {
            "type": "object",
            "properties": {
                "target_sil": {"type": "integer", "enum": [1, 2, 3],
                                "description": "SIL cible (1, 2, 3)"},
                "lam_du": {"type": "number", "description": "λDU (/h)"},
                "architecture": {"type": "string", "enum": ["1oo1", "1oo2", "2oo3", "2oo2", "1oo2D", "2oo2D"],
                                  "description": "Architecture"},
                "beta": {"type": "number", "description": "Common Cause Failure factor (défaut: 0.05)"},
                "dc": {"type": "number", "description": "Diagnostic Coverage (défaut: 0.90)"}
            },
            "required": ["target_sil", "lam_du"]
        }
    },
    handler=lambda a, **kw: optimize_pti(
        target_sil=int(a.get("target_sil", 2)),
        lam_du=float(a.get("lam_du", 1e-6)),
        architecture=a.get("architecture", "1oo1"),
        beta=float(a.get("beta", 0.05)),
        dc=float(a.get("dc", 0.90)),
    ),
    is_async=False,
    description="Optimiser le Proof Test Interval pour un SIL cible.",
    emoji="⏱️",
)