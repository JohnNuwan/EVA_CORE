#!/usr/bin/env bash
# recon.sh — chaîne de recon bug bounty (subfinder → httpx → gau → nuclei)
# Usage : ./recon.sh domaine.com   (domaine DANS LE SCOPE d'un programme autorisé)
# Prérequis : subfinder httpx gau nuclei (voir references/bug-bounty-recon.md)
set -euo pipefail

TARGET="${1:?Usage: $0 domaine.com}"
OUT="recon-$TARGET-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"
echo "[*] Cible : $TARGET  |  sortie : $OUT"

echo "[1/4] subfinder (sous-domaines passifs)..."
subfinder -d "$TARGET" -silent -all -o "$OUT/subs.txt" || true
wc -l < "$OUT/subs.txt" | xargs echo "    sous-domaines trouvés :"

echo "[2/4] httpx (hôtes vivants, ports, technos, titres)..."
httpx -l "$OUT/subs.txt" -silent -threads 50 \
      -status-code -title -tech-detect -web-server \
      -o "$OUT/live.txt" || true
wc -l < "$OUT/live.txt" | xargs echo "    hôtes vivants :"

echo "[3/4] gau (URLs historiques / endpoints cachés)..."
gau --threads 5 --subs "$TARGET" > "$OUT/urls.txt" || true
grep -Ei '\?|admin|api|upload|redirect|token|auth|debug|backup|config' \
     "$OUT/urls.txt" | sort -u > "$OUT/urls-interessantes.txt" || true
wc -l < "$OUT/urls-interessantes.txt" | xargs echo "    URLs à creuser :"

echo "[4/4] nuclei (CVEs exposés, mauvaises configs, technos vulnérables)..."
nuclei -l "$OUT/live.txt" -silent \
       -severity low,medium,high,critical \
       -tags exposure,config,cve,misconfig \
       -o "$OUT/nuclei.txt" || true

echo ""
echo "[OK] Terminé. Résultats dans $OUT/"
echo "    -> nuclei.txt (vulnérabilités) | urls-interessantes.txt (à tester) | live.txt (surface)"
echo "PROCHAINE ÉTAPE (manuelle) : tester les URLs de urls-interessantes.txt pour IDOR/XSS."
