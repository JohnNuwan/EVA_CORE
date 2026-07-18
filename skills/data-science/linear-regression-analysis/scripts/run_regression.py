import json
import pandas as pd
import statsmodels.api as sm
from helios_tools import write_file

def run_regression_analysis(data_path: str, target: str, features: list) -> str:
    """Outil pour effectuer une régression linéaire statistique rigoureuse."""
    try:
        df = pd.read_csv(data_path)
        
        # Préparation des variables
        X = df[features]
        X = sm.add_constant(X)
        y = df[target]
        
        # Modélisation OLS
        model = sm.OLS(y, X).fit()
        
        # Préparation du résultat
        summary = model.summary().as_text()
        
        # Sauvegarde du rapport complet
        report_path = "output/regression_report.txt"
        write_file(path=report_path, content=summary)
        
        return json.dumps({
            "success": True, 
            "message": "Analyse réussie", 
            "report": report_path,
            "rsquared": model.rsquared
        })
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

# NOTE: Pour intégrer cet outil au noyau, il faudrait l'enregistrer dans tools/registry.py
# et l'ajouter à un toolset dans toolsets.py comme décrit dans AGENTS.md.
