#!/usr/bin/env bash
# recon.sh — chaîne de recon bug bounty (subfinder → httpx → gau → nuclei)
# Usage : ./recon.sh domaine.com
# Prérequis : subfinder httpx gau nuclei installés (voir SKILL.md §2)
# --------------------------------------------------------------------
set -euo pipefail

TARGET="${1:?Usage: $0 domaine.com}"
OUT="recon-$TARGET-$(date +%Y%m%d-%H%M)"
mkdir -p "$OUT"
echo "[*] Cible : $TARGET  |  sortie : $OUT"

# 1) Énumération de sous-domaines (passif)
echo "[1/4] subfinder (sous-domaines passifs)..."
subfinder -d "$TARGET" -silent -all -o "$OUT/subs.txt" || true
wc -l < "$OUT/subs.txt" | xargs echo "    sous-domaines trouvés :"

# 2) Sonde HTTP — quels hôtes sont vivants
echo "[2/4] httpx (hôtes vivants, ports, technos, titres)..."
httpx -l "$OUT/subs.txt" -silent -threads 50 \
      -status-code -title -tech-detect -web-server \
      -o "$OUT/live.txt" || true
wc -l < "$OUT/live.txt" | xargs echo "    hôtes vivants :"

# 3) URLs historiques (Wayback, Common Crawl, AlienVault)
echo "[3/4] gau (URLs historiques / endpoints cachés)..."
gau --threads 5 --subs "$TARGET" > "$OUT/urls.txt" || true
# endpoints intéressants : params, admin, api, upload, redirect
grep -Ei '\?|admin|api|upload|redirect|token|auth|debug|backup|config' \
     "$OUT/urls.txt" | sort -u > "$OUT/urls-interessantes.txt" || true
wc -l < "$OUT/urls-interessantes.txt" | xargs echo "    URLs à creuser :"

# 4) Scan de vulnérabilités connu (nuclei, templates communautaires)
echo "[4/4] nuclei (CVEs exposés, mauvaises configs, technos vulnérables)..."
nuclei -l "$OUT/live.txt" -silent \
       -severity low,medium,high,critical \
       -tags exposure,config,cve,misconfig \
       -o "$OUT/nuclei.txt" || true

echo ""
echo "[✓] Terminé. Résultats dans $OUT/"
echo "    → $OUT/nuclei.txt            (vulnérabilités détectées)"
echo "    → $OUT/urls-interessantes.txt (endpoints à tester manuellement)"
echo "    → $OUT/live.txt              (surface d'attaque vivante)"
echo ""
echo "PROCHAINE ÉTAPE (manuelle) : tester les URLs de $OUT/urls-interessantes.txt"
echo "pour IDOR / XSS / injection — c'est là que sont les primes."
