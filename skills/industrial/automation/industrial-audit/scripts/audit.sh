#!/bin/bash

# Détermination du répertoire racine du projet
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$SCRIPT_DIR/../../../../../../"
cd "$ROOT_DIR" || exit 1

echo "========================================================"
echo "      LANCEMENT DE L'AUDIT INDUSTRIEL EPH"
echo "========================================================"
echo ""

# Création du timestamp une seule fois au début (Format: YYYY-MM-DD_HH)
TIMESTAMP=$(date +"%Y-%m-%d_%H")
OUTPUT_PATH="output/audit/${TIMESTAMP}/audit_report.md"

echo "Activation de l'environnement virtuel..."
if [ -f "./.venv/bin/activate" ]; then
    source "./.venv/bin/activate"
elif [ -f "./venv/bin/activate" ]; then
    source "./venv/bin/activate"
else
    echo "[WARNING] Environnement virtuel non détecté, utilisation du python global..."
fi

while true; do
    echo "Exécution du script Python (Dossier : ${TIMESTAMP})..."
    python3 skills/industrial/automation/industrial-audit/scripts/audit_pdf.py --time-limit 240 --output "${OUTPUT_PATH}" "$@"
    
    EXIT_CODE=$?
    if [ $EXIT_CODE -eq 100 ]; then
        echo ""
        echo "========================================================"
        echo "  Temps limite atteint. Sauvegarde automatique réussie."
        echo "  Pause de 5 secondes avant reprise - dossier ${TIMESTAMP}..."
        echo "========================================================"
        sleep 5
    else
        break
    fi
done

echo ""
echo "========================================================"
echo "L'audit est terminé."
