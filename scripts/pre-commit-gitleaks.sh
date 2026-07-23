#!/usr/bin/env bash
# Pre-commit hook: scan secrets avec gitleaks
# Empêche de commiter des secrets/credentials dans le dépôt
# Installation: cp scripts/pre-commit-gitleaks.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

set -e

if ! command -v gitleaks &>/dev/null; then
    echo "⚠️  gitleaks non installé — scan ignoré"
    echo "   Installer: https://github.com/gitleaks/gitleaks/releases"
    exit 0
fi

echo "🔍 Scan gitleaks des fichiers staged..."

# Scan uniquement les fichiers staged (pas tout l'historique)
gitleaks protect --staged --no-banner --redact 2>&1 || {
    echo ""
    echo "🚨 GITLEAKS A DÉTECTÉ DES SECRETS DANS VOS FICHIERS STAGED !"
    echo "   Corrigez les fuites ci-dessus avant de committer."
    echo "   Si c'est un faux positif, ajoutez le fingerprint dans .gitleaksignore"
    echo ""
    exit 1
}

echo "✅ Aucun secret détecté — commit autorisé"
exit 0
