#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
idor_test.py — détecteur d'IDOR (Insecure Direct Object Reference).

Principe : pour une URL contenant un identifiant numérique, on demande
plusieurs valeurs (id, id+1, id+2...) et on compare les réponses.
Si des IDs différents renvoient des contenus DIFFÉRENTS et valides (HTTP 200),
c'est un indice fort d'IDOR — surtout si on y voit des données d'autres users.

Usage :
    python3 idor_test.py "https://site.com/profil?id=123" 123 130
      -> teste id=123..130
    python3 idor_test.py "https://site.com/order/1001/details" 1001 1010
      -> teste le nombre dans le chemin

ATTENTION : à n'utiliser QUE sur des cibles dans le scope d'un programme
de bug bounty auquel tu participes, ou sur des sites de démo autorisés
(ex. testphp.vulnweb.com).
"""
import sys
import hashlib
import urllib.request
import urllib.error
import ssl

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (recon autorisée bug bounty)"}


def fetch(url):
    """Retourne (status, taille, hash_contenu, extrait)."""
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=15, context=CTX) as r:
            body = r.read()
            return r.status, len(body), hashlib.md5(body).hexdigest()[:10], body
    except urllib.error.HTTPError as e:
        return e.code, 0, "-", b""
    except Exception as e:  # réseau, DNS...
        return f"ERR:{type(e).__name__}", 0, "-", b""


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    template, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

    if str(start) not in template:
        print(f"[!] '{start}' introuvable dans l'URL. Indique l'ID présent dans l'URL.")
        sys.exit(1)

    print(f"[*] Gabarit : {template}")
    print(f"[*] Variation de l'ID {start} -> {end}\n")
    print(f"{'ID':>6} | {'HTTP':>5} | {'octets':>8} | hash")
    print("-" * 45)

    seen = {}
    for i in range(start, end + 1):
        url = template.replace(str(start), str(i), 1)
        status, size, h, _ = fetch(url)
        print(f"{i:>6} | {str(status):>5} | {size:>8} | {h}")
        seen.setdefault((status, h), []).append(i)

    print("\n=== Analyse ===")
    distinct = {k: v for k, v in seen.items() if k[0] == 200}
    if len(distinct) > 1:
        print(f"[!] {len(distinct)} contenus HTTP 200 DIFFÉRENTS selon l'ID.")
        print("    -> IDOR probable si ces pages exposent des données par utilisateur.")
        print("    -> Vérifie MANUELLEMENT qu'un ID montre les données d'un AUTRE compte.")
    elif len(seen) == 1:
        print("[i] Toutes les réponses sont identiques : pas d'IDOR évident ici")
        print("    (même contenu quel que soit l'ID, ou redirection uniforme).")
    else:
        codes = {}
        for (st, _), ids in seen.items():
            codes.setdefault(st, 0)
            codes[st] += len(ids)
        print(f"[i] Réponses par code HTTP : {codes}")
        print("    Des 401/403/404 uniformes = contrôle d'accès probablement en place.")


if __name__ == "__main__":
    main()
