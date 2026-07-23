#!/bin/bash
# adam-cicd — Handler CI/CD pour ADAM v2 event daemon
# Traite: file:changed, git:push, test:failed
# Toujours exit 0 pour ne pas planter le bus d'événements.

set -uo pipefail

CHANNEL="${ADAM_EVENT_CHANNEL:-unknown}"
PAYLOAD="${ADAM_EVENT_PAYLOAD:-}"
if [ -z "$PAYLOAD" ]; then PAYLOAD='{}'; fi
SOURCE="${ADAM_EVENT_SOURCE:-unknown}"
LOGFILE="${ADAM_V2_DIR:-/home/aza/eva-adam-v2}/logs/cicd-handler.log"
TIMESTAMP=$(date -Iseconds)

# Ensure log directory exists
mkdir -p "$(dirname "$LOGFILE")"

log() {
    local level="${1:-INFO}"
    local msg="${2:-}"
    echo "[${TIMESTAMP}] [${level}] [${CHANNEL}] ${msg}" >> "$LOGFILE"
}

# Safe JSON extraction via python3 — uses env vars to avoid shell escaping issues
extract_json() {
    local key="$1"
    local default="${2:-}"
    echo "$PAYLOAD" | ADAM_KEY="$key" python3 -c '
import json, sys, os
try:
    raw = sys.stdin.read().strip()
    while raw.count("{") < raw.count("}"):
        raw = raw.rstrip("}")
    d = json.loads(raw)
    val = d.get(os.environ.get("ADAM_KEY", ""), "")
    print(val)
except Exception:
    print("")
' 2>/dev/null || echo "${2:-}"
}

# Detect if a path is inside a git repo with a remote
is_git_repo_with_remote() {
    local path="$1"
    local dir
    dir="$(dirname "$path")"
    # Walk up to find the git root
    local git_root
    git_root=$(cd "$dir" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null) || return 1
    # Check if repo has at least one remote
    (cd "$git_root" && git remote -v 2>/dev/null | grep -q .) || return 1
    echo "$git_root"
    return 0
}

# Check if file is tracked by git (not ignored, not untracked)
is_git_tracked() {
    local path="$1"
    local dir
    dir="$(dirname "$path")"
    (cd "$dir" 2>/dev/null && git ls-files --error-unmatch "$path" 2>/dev/null | grep -q .) 2>/dev/null
}

# ─── Dispatch ───────────────────────────────────────────────────────────────
log "INFO" "Processing event: source=${SOURCE} payload=${PAYLOAD}"

case "${CHANNEL}" in
    file:changed)
        FILE_PATH=$(extract_json "path" "")
        log "INFO" "file:changed → path=${FILE_PATH}"

        if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
            log "WARN" "Invalid or missing file path, skipping"
            exit 0
        fi

        # Check if file is inside a git repo with a remote
        GIT_ROOT=$(is_git_repo_with_remote "$FILE_PATH") || {
            log "INFO" "File not in a git repo with remote, skipping auto-commit"
            exit 0
        }

        # Check if file is tracked (not .gitignore'd)
        if ! is_git_tracked "$FILE_PATH"; then
            log "INFO" "File not tracked by git (ignored or untracked), skipping"
            exit 0
        fi

        # Relative path within repo for commit message
        REL_PATH="${FILE_PATH#$GIT_ROOT/}"

        log "INFO" "Auto-committing ${REL_PATH} in ${GIT_ROOT}"

        # Timeout guard: 30s total for git operations
        if timeout 25 bash -c "
            cd '$GIT_ROOT'
            git add '$FILE_PATH' 2>/dev/null
            if git diff --cached --quiet 2>/dev/null; then
                echo 'no_changes'
                exit 0
            fi
            git commit -m 'auto: ${REL_PATH}' 2>/dev/null || true
            git push 2>&1
        "; then
            log "INFO" "Auto-commit+push successful for ${REL_PATH}"
        else
            log "WARN" "Git operation failed or timed out for ${REL_PATH}"
        fi
        ;;

    git:push)
        GIT_SOURCE=$(extract_json "source" "$SOURCE")
        BRANCH=$(extract_json "branch" "unknown")
        COMMIT_COUNT=$(extract_json "commit_count" "?")
        log "INFO" "git:push — source=${GIT_SOURCE} branch=${BRANCH} commits=${COMMIT_COUNT}"
        # Notification via log (stderr goes to daemon's journal)
        echo "[adam-cicd] Push détecté: source=${GIT_SOURCE} branch=${BRANCH} commits=${COMMIT_COUNT}" >&2
        ;;

    git:pull)
        # Synchronise le dépôt local avec le distant (origin/<branch>)
        # Payload attendu: {"repo": "/path/to/repo", "branch": "Dev"}
        # Si repo absent, utilise REPO_DIR par défaut (~/test-pr-repo)
        REPO_DIR=$(extract_json "repo" "${ADAM_REPO_DIR:-/home/aza/test-pr-repo}")
        BRANCH=$(extract_json "branch" "Dev")
        log "INFO" "git:pull — repo=${REPO_DIR} branch=${BRANCH}"

        if [ ! -d "$REPO_DIR/.git" ]; then
            log "WARN" "${REPO_DIR} n'est pas un dépôt git, abandon"
            exit 0
        fi

        # Vérifier qu'il y a un remote
        if ! (cd "$REPO_DIR" && git remote -v 2>/dev/null | grep -q .); then
            log "WARN" "${REPO_DIR} n'a pas de remote configuré"
            exit 0
        fi

        # Sauvegarder les changements locaux non commités (stash) avant pull
        STASHED=0
        if ! (cd "$REPO_DIR" && git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null); then
            log "INFO" "Changements locaux détectés, stash avant pull"
            (cd "$REPO_DIR" && git stash push -m "auto-stash before git:pull $(date +%s)" 2>/dev/null) && STASHED=1
        fi

        # Fetch + pull avec timeout 30s
        PULL_OUTPUT=$(cd "$REPO_DIR" && timeout 30 git pull origin "$BRANCH" 2>&1) || {
            log "WARN" "git pull origin ${BRANCH} échoué ou timeout: ${PULL_OUTPUT}"
            # Restaurer le stash si on l'a fait
            [ "$STASHED" = "1" ] && (cd "$REPO_DIR" && git stash pop 2>/dev/null)
            exit 0
        }

        log "INFO" "git pull origin ${BRANCH}: ${PULL_OUTPUT}"

        # Compter les fichiers mis à jour
        UPDATED=$(echo "$PULL_OUTPUT" | grep -cE "files? changed|file changed" 2>/dev/null || echo "0")
        log "INFO" "Pull terminé: ${UPDATED} fichier(s) mis à jour sur ${BRANCH}"

        # Restaurer le stash si nécessaire
        if [ "$STASHED" = "1" ]; then
            STASH_POP_OUT=$(cd "$REPO_DIR" && git stash pop 2>&1) || {
                log "WARN" "git stash pop échoué: ${STASH_POP_OUT}"
            }
            [ -n "$STASH_POP_OUT" ] && log "INFO" "Stash restauré"
        fi
        ;;

    test:failed)
        TEST_NAME=$(extract_json "test" "")
        TEST_FILE=$(extract_json "file" "")
        ERROR_MSG=$(extract_json "error" "")
        log "INFO" "test:failed — test=${TEST_NAME} file=${TEST_FILE} error=${ERROR_MSG}"

        if [ -n "$TEST_FILE" ] && [ -f "$TEST_FILE" ]; then
            log "INFO" "Extracting pytest error output for ${TEST_FILE}..."
            # Try to run pytest on the test file with short traceback, 15s timeout
            PYTHON_OUTPUT=$(timeout 15 python3 -m pytest "$TEST_FILE" --tb=short -q 2>&1 || true)
            echo "[${TIMESTAMP}] [PYTEST] ${PYTHON_OUTPUT}" >> "$LOGFILE"
        elif [ -n "$TEST_NAME" ]; then
            # Try as a test name pattern (e.g., "tests/test_foo.py::test_bar")
            PYTHON_OUTPUT=$(timeout 15 python3 -m pytest "$TEST_NAME" --tb=short -q 2>&1 || true)
            echo "[${TIMESTAMP}] [PYTEST] ${PYTHON_OUTPUT}" >> "$LOGFILE"
        else
            log "WARN" "No test file/name provided, skipping pytest extraction"
        fi
        ;;

    *)
        log "WARN" "Unknown channel: ${CHANNEL}"
        ;;
esac

exit 0