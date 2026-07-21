---
name: sysadmin-advanced-bash
description: "Scripting Bash avancé : tableaux associatifs, traps, subshells, redirections, coprocesses, nom pipe, erreur handling, debug avec set -x, évitement des antipatterns."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [bash, shell, scripting, advanced, automation, traps, arrays, debugging, error-handling, pipes]
    related_skills: [os-linux-admin, sysadmin-systemd, sysadmin-backup-strategies]
---

# Scripting Bash Avancé

## Vue d'ensemble

Bash est le langage d'automatisation principal de tout système Linux. Au-delà des scripts linéaires simples, ce skill couvre les techniques avancées pour écrire des scripts robustes, maintenables et professionnels : gestion d'erreur, structures de données, programmation asynchrone, débogage et patterns éprouvés.

## Quand l'utiliser

- Écrire des scripts de production (backup, déploiement, monitoring)
- Automatiser des workflows complexes avec parallélisation
- Analyser des logs avec des structures de données avancées
- Gérer les signaux et le nettoyage (traps, exit handlers)
- Déboguer un script complexe qui échoue de manière intermittente

## 1. En-tête Obligatoire : Le Saint-Graal

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

| Option | Effet |
|--------|-------|
| `-e` | Arrête le script à la première erreur (exit non-zéro) |
| `-u` | Arrête le script si une variable non définie est utilisée |
| `-o pipefail` | Une commande qui échoue dans un pipe fait échouer tout le pipe |
| `IFS` | Internal Field Separator : évite les surprises avec les espaces |

> ⚠️ Attention : `set -e` peut être contourné par certaines constructions. Ajouter un `|| true` explicitement là où l'échec est acceptable.

```bash
# Pattern pour commande dont l'échec est acceptable
rm -f /tmp/lockfile || true   # exit 1 ignoré si fichier absent
grep "pattern" /var/log/syslog || [[ $? -eq 1 ]]  # grep retourne 1 si pas trouvé
```

## 2. Traps — Nettoyage et Gestion des Signaux

```bash
#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    local exit_code=$?
    echo "[CLEANUP] Nettoyage en cours... (exit: $exit_code)"
    rm -f /tmp/monfifo
    rm -rf /tmp/mon_travail
    echo "[CLEANUP] Terminé"
    exit "$exit_code"
}

# Trap multiples
trap cleanup EXIT          # appelé à la sortie (quelle qu'elle soit)
trap 'echo "Interrompu (SIGINT)"; exit 1' INT
trap 'echo "Signal SIGTERM reçu"; exit 1' TERM
trap 'echo "Signal SIGHUP reçu"' HUP

# Exemple d'utilisation
mkdir -p /tmp/mon_travail
echo "Travail en cours..."
sleep 100  # Si Ctrl+C, le trap EXIT nettoie
```

### Pattern : Stack de Traps

```bash
# Permet d'empiler les nettoyages (au lieu de les écraser)
_cleanup_handlers=()

push_cleanup() {
    _cleanup_handlers+=("$@")
}

run_cleanups() {
    local exit_code=$?
    for handler in "${_cleanup_handlers[@]}"; do
        eval "$handler" 2>/dev/null || true
    done
    exit "$exit_code"
}

trap run_cleanups EXIT

push_cleanup 'rm -f /tmp/lockfile'
push_cleanup 'echo "Nettoyage terminé"'
```

## 3. Tableaux et Structures de Données

### Tableaux Indexés

```bash
# Déclaration et initialisation
serveurs=("web01" "db01" "cache01")
serveurs+=("monitor01")              # ajout
echo "${serveurs[0]}"                # web01
echo "${#serveurs[@]}"               # taille = 4
echo "${!serveurs[@]}"               # indices: 0 1 2 3

# Boucle
for server in "${serveurs[@]}"; do
    echo "Ping $server..."
    ping -c 1 "$server" &>/dev/null || echo "   $server injoignable"
done
```

### Tableaux Associatifs (Bash 4+)

```bash
# Déclaration
declare -A utilisateurs
utilisateurs=(
    ["alice"]="/home/alice"
    ["bob"]="/home/bob"
    ["charlie"]="/backup/charlie"
)

# Accès
echo "${utilisateurs[alice]}"        # /home/alice
echo "${!utilisateurs[@]}"           # clés: alice bob charlie
echo "${#utilisateurs[@]}"           # taille: 3

# Parcours clé-valeur
for user in "${!utilisateurs[@]}"; do
    echo "Utilisateur: $user → Home: ${utilisateurs[$user]}"
done
```

## 4. Subshells et Groupement

```bash
# Subshell ( ) — exécution dans un sous-processus, variables isolées
(cd /tmp && ls -la)   # ne modifie pas le pwd du parent
var="outside"
(var="inside"; echo "$var")  # "inside"
echo "$var"                  # "outside"

# Groupement { } — dans le même shell, pour la redirection
{
    echo "=== INFO SYSTÈME ==="
    date
    uptime
    free -h
} > /var/log/sysinfo.log

# Async avec & (attention au piège)
long_task &
pid=$!
echo "PID du background: $pid"
wait $pid
echo "Tâche terminée"

# Parallélisation simple
task1() { sleep 2; echo "Task 1 done"; }
task2() { sleep 1; echo "Task 2 done"; }

task1 &
task2 &
wait
echo "Toutes les tâches terminées"
```

## 5. Redirections Avancées

```bash
# Rediriger stdout ET stderr vers des fichiers différents
cmd > stdout.log 2> stderr.log

# Rediriger les deux vers le même fichier
cmd &> all.log              # syntaxe moderne
cmd > all.log 2>&1          # syntaxe POSIX (portable)

# Discarder stdout, garder stderr
cmd > /dev/null

# Pipe du stderr uniquement
cmd 2>&1 >/dev/null | grep "ERREUR"

# File descriptors personnalisés
exec 3> /var/log/monapp.log
echo "Début du traitement" >&3
curl -s http://api.example.com >&3
exec 3>&-  # fermer FD 3

# Process Substitution (très utile)
diff <(ls /dir1) <(ls /dir2)  # comparer deux listes
while IFS= read -r line; do
    echo "Ligne: $line"
done < <(tail -f /var/log/syslog &)  # lire sans subshell
```

## 6. Coprocess et FIFO

### Coprocess (Bash 4+)

```bash
# Lancer une commande en background avec pipe bidirectionnel
coproc BC { bc -l; }

# Écrire dans le coprocess
echo "scale=2; 5/3" >&${BC[1]}
# Lire le résultat
read -u ${BC[0]} result
echo "Résultat: $result"
```

### Named Pipe (FIFO)

```bash
# Créer un pipe nommé
mkfifo /tmp/mypipe

# Terminal 1 : écrire dans le pipe
echo "hello from process 1" > /tmp/mypipe

# Terminal 2 : lire depuis le pipe
cat /tmp/mypipe

# Communication bidirectionnelle entre deux processus
mkfifo /tmp/pipe_in /tmp/pipe_out

process_server() {
    while true; do
        read request < /tmp/pipe_in
        echo "Réponse à: $request" > /tmp/pipe_out
    done
}

process_server &
echo "requête1" > /tmp/pipe_in
read response < /tmp/pipe_out
echo "Réponse reçue: $response"
```

## 7. Manipulation de Chaînes

```bash
string="/home/user/documents/file.txt"

# Extraction par pattern
echo "${string#*/}"                 # home/user/documents/file.txt  (enlève le plus court préfixe)
echo "${string##*/}"               # file.txt  (enlève le plus long préfixe)
echo "${string%.*}"                 # /home/user/documents/file   (enlève le plus court suffixe)
echo "${string%%.*}"               # /home/user/documents/file   (enlève le plus long suffixe)

# Substitution
echo "${string/file/doc}"           # /home/user/documents/doc.txt (première occurrence)
echo "${string//file/doc}"          # /home/user/docdocuments/doc.txt (toutes)

# Longueur
echo "${#string}"                   # 34

# Valeur par défaut
echo "${user:-default_user}"        # si $user est vide, affiche "default_user"
echo "${user:=default_user}"        # si $user est vide, assigne et affiche

# Majuscule/minuscule
echo "${string,,}"                  # tout en minuscule
echo "${string^^}"                  # tout en majuscule
```

## 8. Fonctions Avancées

```bash
# Fonction avec arguments et valeurs par défaut
log() {
    local level="${1:-INFO}"        # défaut: INFO
    local message="$2"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message"
}

log "ERREUR" "Connexion échouée"

# Fonction retournant une valeur (via printf -v)
get_config() {
    local key="$1"
    local file="${2:-/etc/monapp/config.ini}"
    grep "^${key}=" "$file" | cut -d= -f2
}

db_host=$(get_config "db_host")
log "INFO" "DB host = $db_host"

# Fonction avec validation des arguments
require_root() {
    if [[ $EUID -ne 0 ]]; then
        echo "ERREUR: Ce script doit être exécuté en root" >&2
        exit 1
    fi
}

require_file() {
    local file="$1"
    if [[ ! -f "$file" ]]; then
        echo "ERREUR: Fichier '$file' introuvable" >&2
        return 1
    fi
}
```

## 9. Patterns pour Scripts Robustes

### Parse d'Arguments avec getopts

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 [-v] [-o output] [-n count] <input>"
    exit 1
}

# Initialiser les options
verbose=false
output=""
count=10

while getopts "vo:n:h" opt; do
    case $opt in
        v) verbose=true ;;
        o) output="$OPTARG" ;;
        n) count="$OPTARG" ;;
        h) usage ;;
        ?) usage ;;
    esac
done
shift $((OPTIND - 1))

# Arguments positionnels
input="${1:-}"
[[ -z "$input" ]] && usage
```

### Lock File Évitement de Concurrence

```bash
LOCKFILE="/tmp/monscript.lock"

acquire_lock() {
    # Utiliser flock (atomique, même sur NFS)
    exec 200>"$LOCKFILE"
    if ! flock -n 200; then
        echo "ERREUR: Une autre instance est en cours d'exécution" >&2
        exit 1
    fi
}

release_lock() {
    flock -u 200
    rm -f "$LOCKFILE"
}

acquire_lock
trap release_lock EXIT

# ... travail ...
```

### Progress Bar Simple

```bash
progress_bar() {
    local current="$1"
    local total="$2"
    local width=50
    local percent=$(( current * 100 / total ))
    local filled=$(( current * width / total ))
    local empty=$(( width - filled ))

    printf "\r["
    printf "%${filled}s" | tr ' ' '#'
    printf "%${empty}s" | tr ' ' '-'
    printf "] %3d%%" "$percent"
}
```

## 10. Débogage

```bash
# Débogage pas à pas
bash -x script.sh          # exécution trace
set -x                     # activer le mode debug dans le script
set +x                     # désactiver

# Debug partiel (uniquement une section)
echo "=== DÉBUT DEBUG ==="
set -x
# code à tracer
set +x
echo "=== FIN DEBUG ==="

# PS4 personnalisé (prompt de debug)
export PS4='+[${BASH_SOURCE}:${LINENO}]: ${FUNCNAME[0]:+${FUNCNAME[0]}() }'

# Vérification syntaxique sans exécuter
bash -n script.sh          # shellcheck intégré

# Linting externe (toujours utiliser)
# shellcheck myscript.sh
```

## Pièges Courants

1. **`set -e` et subshells** : Un `(cmd)` qui échoue ne stoppe PAS le script parent. Vérifier le code de retour du subshell.

2. **Variables sans guillemets** : `if [ $var == "oui" ]` échoue si `$var` est vide ou contient plusieurs mots. Toujours `[ "$var" = "oui" ]`.

3. **Pipes et `set -o pipefail`** : Oublié → une commande qui échoue au milieu d'un pipe est silencieusement ignorée.

4. **Lecture de fichiers avec espaces** : `for line in $(cat file)` échoue sur les lignes avec espaces. Utiliser `while IFS= read -r line; do`.

5. **Variables exportées** : Les variables Bash ne sont pas automatiquement transmises aux sous-processus. Utiliser `export VAR=value`.

## Liste de vérification (Checklist)

- [ ] `set -euo pipefail` + `IFS=$'\n\t'` en en-tête
- [ ] Toutes les variables entre guillemets : `"$var"`
- [ ] Trap EXIT pour le nettoyage
- [ ] `shellcheck` passé sans erreur
- [ ] Arguments validés (getopts ou vérification manuelle)
- [ ] Lock file pour les scripts concurrents
- [ ] Messages d'erreur vers stderr (`>&2`)
- [ ] Codes de retour explicites (`exit 0`, `exit 1`)
- [ ] `read` avec `IFS=` et `-r` pour les fichiers
- [ ] Tableaux associatifs plutôt que `eval` pour les structures de données
