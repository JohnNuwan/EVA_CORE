#!/usr/bin/env python3
"""
Module Time Series Analyzer - Analyse de séries temporelles industrielles.
Détection d'anomalies, statistiques, MTBF, OEE.
"""

import json, logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def _check_deps():
    try:
        import numpy, pandas  # noqa
        return True
    except ImportError:
        return False


def analyze_timeseries(file_path: str, timestamp_col: str = "timestamp",
                       value_cols: Optional[List[str]] = None,
                       output: str = "report") -> str:
    """Analyse un fichier CSV de séries temporelles."""
    if not _check_deps():
        return json.dumps({"error": "numpy/pandas non installés"})
    path = Path(file_path)
    if not path.exists():
        return json.dumps({"error": f"Fichier introuvable: {file_path}"})
    df = pd.read_csv(path)
    if timestamp_col in df.columns:
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df = df.set_index(timestamp_col)
    if value_cols is None:
        value_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    results = {"file": path.name, "rows": len(df), "columns": len(value_cols), "metrics": {}}
    for col in value_cols:
        if col not in df.columns:
            continue
        s = df[col].dropna()
        metrics = {"count": int(len(s)), "min": float(s.min()), "max": float(s.max()),
                    "mean": float(s.mean()), "median": float(s.median()), "std": float(s.std()),
                    "p25": float(s.quantile(0.25)), "p75": float(s.quantile(0.75)),
                    "missing": int(df[col].isna().sum())}
        results["metrics"][col] = metrics
    if output == "json":
        return json.dumps(results, indent=2, default=str)
    md = f"# Analyse Série Temporelle : {path.name}\n\n**Lignes :** {len(df)}\n\n"
    for col, m in results["metrics"].items():
        md += f"## {col}\n"
        for k, v in m.items():
            md += f"- **{k}** : {v}\n"
    return md


def detect_anomalies_stl(file_path: str, value_col: str, period: int = 24) -> str:
    """Détecte les anomalies via STL decomposition."""
    if not _check_deps():
        return json.dumps({"error": "numpy/pandas non installés"})
    try:
        from statsmodels.tsa.seasonal import STL
    except ImportError:
        return json.dumps({"error": "statsmodels non installé"})
    df = pd.read_csv(file_path)
    if value_col not in df.columns:
        return json.dumps({"error": f"Colonne {value_col} introuvable"})
    s = df[value_col].dropna().values[:period * 10]
    if len(s) < period * 2:
        return json.dumps({"error": f"Pas assez de données (min {period * 2})"})
    res = STL(s, period=period).fit()
    resid = res.resid
    threshold = 3 * float(np.std(resid))
    anomalies = np.abs(resid) > threshold
    n_anomalies = int(anomalies.sum())
    results = {"method": "STL", "total": len(s), "anomalies": n_anomalies,
               "rate": round(n_anomalies / len(s) * 100, 2), "threshold": threshold}
    return json.dumps(results, indent=2)


from tools.registry import registry  # noqa: E402

registry.register(
    name="time_series_analyze",
    toolset="industrial",
    schema={
        "name": "time_series_analyze",
        "description": "Analyse un fichier CSV de séries temporelles industrielles et retourne des statistiques descriptives.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Chemin CSV"},
                "timestamp_col": {"type": "string", "description": "Colonne timestamp"},
                "value_cols": {"type": "array", "items": {"type": "string"}, "description": "Colonnes à analyser"},
                "output": {"type": "string", "enum": ["report", "json"]}
            },
            "required": ["file_path"]
        }
    },
    handler=lambda args, **kw: analyze_timeseries(
        args["file_path"], args.get("timestamp_col", "timestamp"),
        args.get("value_cols"), args.get("output", "report")),
    is_async=False,
    description="Analyser des séries temporelles industrielles.",
    emoji="📈",
)

registry.register(
    name="time_series_anomaly_stl",
    toolset="industrial",
    schema={
        "name": "time_series_anomaly_stl",
        "description": "Détecte les anomalies dans une série temporelle via décomposition STL.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Chemin CSV"},
                "value_col": {"type": "string", "description": "Colonne valeurs"},
                "period": {"type": "integer", "description": "Période (défaut: 24)"}
            },
            "required": ["file_path", "value_col"]
        }
    },
    handler=lambda args, **kw: detect_anomalies_stl(args["file_path"], args["value_col"], int(args.get("period", 24))),
    is_async=False,
    description="Détecter des anomalies via STL.",
    emoji="🚨",
)