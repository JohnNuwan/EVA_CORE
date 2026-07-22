# Référence : curl Healthcheck — Reproduction du bug "000000"

## Reproduction exacte du bug

```bash
#!/usr/bin/env bash
# Simuler un port fermé sur le port 19999

# ❌ MAUVAIS : curl + || echo "000"
http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:19999/health 2>/dev/null || echo "000")
echo "Code: '$http_code'"          # '000000' — 6 caractères !
echo "Longueur: ${#http_code}"     # 6

# ✅ BON : capture dans variable, puis fallback
local code
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 http://localhost:19999/health 2>/dev/null) || code="000"
echo "Code: '$code'"               # '000' — 3 caractères
echo "Longueur: ${#code}"          # 3
```

## Pourquoi ça arrive

`curl -w "%{http_code}"` a deux comportements selon le résultat :

| Cas | `-w "%{http_code}"` | exit code |
|-----|---------------------|-----------|
| Connexion réussie → HTTP 200 | écrit "200" | 0 |
| Connexion réussie → HTTP 404 | écrit "404" | 0 |
| **Connexion refusée** | **écrit "000"** | **7** |
| Timeout | écrit "000" | 28 |
| Résolution DNS échouée | écrit "000" | 6 |

Quand curl ne peut **pas** se connecter, il **produit déjà "000"** via `-w` **ET** exit avec un code non-zéro. Le `||` bash se déclenche et ajoute un second "000" → "000000".

## Correction dans le code réel (praetor-watch.sh)

**Fichier** : `/home/aza/scripts/praetor-watch.sh`

**Ligne corrigée** (check_http function) :

```bash
# Avant (bug)
curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "http://localhost:${port}${path}" 2>/dev/null || echo "000"

# Après (fixé)
local code; code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$timeout" "http://localhost:${port}${path}" 2>/dev/null) || code="000"
echo "$code"
```

## Conséquence du bug

Le watchdog ADAM-PRAETOR ne **détectait pas** les serveurs tombés comme "down" :

- `check_server()` teste `case "$http_code" in 000)` — mais le code réel est "000000"
- Le code tombait dans le `*)` catch-all qui enregistre un statut "unknown" (pas "down")
- Le `*)` catch-all n'appelle **pas** `restart_local_server()` (pas de correction automatique)
- L'alerte n'était pas créée via `record_alert()`
- Le serveur restait down jusqu'à une intervention manuelle

## Leçons pour tout script de healthcheck HTTP

1. **Toujours utiliser le pattern `capture || fallback`** pour les commandes qui peuvent produire une sortie partielle avant d'échouer
2. **Tester avec un port fermé** pour valider le comportement d'erreur
3. **Vérifier la longueur du code retour** : `echo "${#http_code}"` peut révéler des bugs silencieux
4. **Le `case` doit tester les bons patterns** : `000)` pour "pas de réponse", `200|20[0-9])` pour OK, `404|50[0-9])` pour erreur applicative