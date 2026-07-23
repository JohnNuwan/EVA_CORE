#!/usr/bin/env bash
# =============================================================================
# git-sync.sh — Script de synchronisation automatique EVA (ADAM-GIT)
# =============================================================================
# Usage : ./git-sync.sh [message]
#   - Sans argument : commit auto avec description des changements
#   - Avec argument  : utilise le message fourni
#
# Comportement :
#   1. Se place dans le dépôt EVA_CORE (~/.hermes/hermes-agent)
#   2. Vérifie que le remote SSH est fonctionnel
#   3. Fetch les dernières modifications depuis origin
#   4. Détecte les conflits avant de commit
#   5. Ajoute les fichiers modifiés/nouveaux (hors .env, logs, secrets)
#   6. Commit avec message descriptif
#   7. Push sur origin/main
# =============================================================================

set -euo pipefail

REPO_DIR="$HOME/.hermes/hermes-agent"
REMOTE_NAME="origin"
BRANCH="main"
COMMIT_MSG="${1:-}"

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[ADAM-GIT]${NC} $1"; }
ok()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
err()   { echo -e "${RED}[✗]${NC} $1"; }

# ---- Étape 1 : Vérifications préalables ----
cd "$REPO_DIR"
info "Dépôt : $(basename $(git rev-parse --show-toplevel))"
info "Branche : $(git branch --show-current)"

# Vérifier que le remote est bien en SSH
REMOTE_URL=$(git remote get-url "$REMOTE_NAME" 2>/dev/null)
if [[ "$REMOTE_URL" != git@* ]]; then
    warn "Le remote $REMOTE_NAME n'est pas en SSH ($REMOTE_URL)"
    info "Configuration du remote en SSH..."
    git remote set-url "$REMOTE_NAME" "git@github.com:JohnNuwan/EVA_CORE.git"
    ok "Remote SSH configuré"
fi

# Vérifier que la clé SSH fonctionne (ignorer le code retour 1 de GitHub qui veut dire "auth OK mais pas de shell")
SSH_TEST=$(ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1) || true
if ! echo "$SSH_TEST" | grep -q "successfully authenticated"; then
    err "Authentification SSH GitHub échouée — $SSH_TEST"
    exit 1
fi
ok "Authentification SSH GitHub validée"

# ---- Étape 2 : Fetch des dernières modifications ----
info "Récupération des dernières modifications depuis origin..."
git fetch origin 2>&1 || {
    err "Fetch échoué — vérifie la connectivité"
    exit 1
}
ok "Fetch effectué"

# ---- Étape 3 : Vérification des conflits potentiels ----
BEHIND=$(git rev-list --count HEAD..origin/$BRANCH 2>/dev/null || echo 0)
AHEAD=$(git rev-list --count origin/$BRANCH..HEAD 2>/dev/null || echo 0)

if [ "$BEHIND" -gt 0 ]; then
    warn "Le dépôt local a $BEHIND commit(s) de retard sur origin/$BRANCH"
    warn "Un rebase ou merge est nécessaire avant de push"
    info "Tentative de rebase automatique..."
    if git rebase origin/$BRANCH; then
        ok "Rebase réussi"
    else
        err "Rebase échoué — conflits détectés !"
        err "Résous les conflits manuellement, puis :"
        err "  git rebase --continue"
        err "  $0"
        exit 1
    fi
else
    ok "Aucun conflit — HEAD est à jour (avance de $AHEAD commit(s))"
fi

# ---- Étape 4 : Vérifier s'il y a des changements à commit ----
if git diff --quiet HEAD && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    info "Aucun changement à commit — dépôt propre"
    info "Rien à push non plus (HEAD = origin/$BRANCH)"
    exit 0
fi

# ---- Étape 5 : Construction du message de commit ----
if [ -z "$COMMIT_MSG" ]; then
    # Générer un message automatique basé sur les fichiers modifiés
    MODIFIED=$(git diff --name-only HEAD 2>/dev/null | head -20)
    UNTRACKED=$(git ls-files --others --exclude-standard | head -20)
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    
    # Compter les changements
    N_MOD=$(git diff --name-only HEAD 2>/dev/null | wc -l)
    N_NEW=$(git ls-files --others --exclude-standard | wc -l)
    N_DEL=$(git diff --diff-filter=D --name-only HEAD 2>/dev/null | wc -l)
    
    COMMIT_MSG="[EVA] Sync automatique — $TIMESTAMP"
    
    # Ajouter un résumé des changements
    CHANGES=""
    [ "$N_MOD" -gt 0 ] && CHANGES="${CHANGES}${N_MOD} modifié(s), "
    [ "$N_NEW" -gt 0 ] && CHANGES="${CHANGES}${N_NEW} nouvel(s), "
    [ "$N_DEL" -gt 0 ] && CHANGES="${CHANGES}${N_DEL} supprimé(s), "
    CHANGES="${CHANGES%, }"  # Enlever la dernière virgule
    
    COMMIT_MSG="$COMMIT_MSG — $CHANGES"
else
    COMMIT_MSG="[EVA] $COMMIT_MSG"
fi

# ---- Étape 6 : Add et Commit ----
info "Ajout des fichiers modifiés et nouveaux..."
git add -A 2>/dev/null || git add --all 2>/dev/null
ok "Fichiers stagés"

info "Message de commit : $COMMIT_MSG"
git commit -m "$COMMIT_MSG" || {
    warn "Commit vide ou échoué"
    exit 1
}
ok "Commit effectué"

# ---- Étape 7 : Push ----
info "Push vers origin/$BRANCH..."
git push "$REMOTE_NAME" "$BRANCH" 2>&1 || {
    err "Push échoué"
    err "Vérifie : git push origin $BRANCH"
    exit 1
}
ok "Push réussi ! Les $AHEAD commit(s) sont synchronisés"

# ---- Bilan final ----
echo ""
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Synchronisation terminée avec succès  ${NC}"
echo -e "${GREEN}══════════════════════════════════════════${NC}"
echo "  Dépôt   : $(basename $(git rev-parse --show-toplevel))"
echo "  Branche : $BRANCH"
echo "  Commit  : $(git rev-parse --short HEAD)"
echo "  Date    : $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

exit 0