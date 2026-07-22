---
name: self-healing-watchdog
description: "Concevoir et maintenir un watchdog auto-correcteur pour services HTTP — checks de santé, auto-restart, état persistant, rapports et pièges bash."
category: devops
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    tags: [watchdog, self-healing, monitoring, http-healthcheck, bash, auto-repair, ha]
    related_skills: [sysadmin-advanced-bash, sysadmin-monitoring, local-ai-stack]
---

# Watchdog Auto-Correcteur (Self-Healing)

## Vue d'ensemble

Un watchdog auto-correcteur surveille des services HTTP (API, serveurs web, conteneurs Docker) et tente de les redémarrer automatiquement quand ils tombent. Contrairement à un monitoring passif (Prometheus + alertes), le watchdog **agit** — il exécute des commandes de réparation et tient un état persistant des corrections et alertes.

Ce skill documente les patterns, pièges et bonnes pratiques pour construire ou maintenir ce type de système.

## Quand l'utiliser

- L'utilisateur demande de surveiller des services web/API avec auto-réparation
- Un système de watchdog existant (ADAM-PRAETOR, sentinel, etc.) a besoin de maintenance
- Implémenter un healthcheck HTTP avec restart automatique
- Déboguer un script de monitoring qui ne détecte pas correctement les pannes

## Architecture de référence

```
┌─────────────────────────────────────────────────────────┐
│              Watchdog (bash, cron)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │ Check    │  │ Auto-    │  │ State    │  │ Report  │ │
│  │ HTTP     │──▶ Repair   │──▶ Persist  │──▶ Wiki    │ │
│  │ endpoints│  │ (restart)│  │ (JSON)   │  │ (MD)    │ │
│  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Composants clés

1. **Définition des services** : liste de `nom:port`, URL de health, commande de restart
2. **Check HTTP** : `curl -w "%{http_code}"` vers chaque endpoint
3. **Auto-repair** : `fuser -k PORT/tcp` + `nohup bash -c "cmd" > log &`
4. **État persistant** : fichier JSON avec historique des corrections et alertes
5. **Rapport** : page wiki/dashboard mise à jour chaque cycle

## Piège n°1 : curl + `|| echo` produit "000000" au lieu de "000"

### ❌ Mauvais (produit 6 caractères)

```bash
http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8083/health 2>/dev/null || echo "000")
```

**Pourquoi** : Quand curl ne peut pas se connecter :
1. `-w "%{http_code}"` écrit **"000"** sur stdout
2. curl exit avec code 7 (connection refused)
3. `|| echo "000"` ajoute un deuxième **"000"**
4. Résultat : **"000000"** — qui ne match **jamais** le pattern `case ... 000)`

### ✅ Bon (capture avant fallback)

```bash
local code
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "http://localhost:${port}${path}" 2>/dev/null) || code="000"
```

**Pourquoi** : `$()` capture la sortie avant que le `||` ne soit évalué. Le `|| code="000"` ne s'exécute que si la capture échoue complètement.

### Pattern général

```bash
# ❌ MAUVAIS
output=$(cmd_that_fails || echo "fallback")

# ✅ BON
output=$(cmd_that_fails 2>/dev/null) || output="fallback"
```

## Piège n°2 : `bash -lic` dans nohup (contexte cron)

### ❌ Mauvais

```bash
nohup bash -lic "python server.py" > /tmp/log 2>&1 &
```

**Pourquoi** : `-l` (login shell) et `-i` (interactive) échouent silencieusement en cron :
- Pas de terminal → `-i` bloque ou ignore la commande
- `.bash_profile`/`.bashrc` peuvent ne pas être lus
- Les alias/fonctions interactives sont indisponibles

### ✅ Bon

```bash
nohup bash -c "cd /home/user/project && /path/to/venv/bin/python server.py" > /tmp/log 2>&1 &
```

Ou encore plus simple (pas de `bash -c` wrapper) :

```bash
/path/to/venv/bin/python /path/to/server.py >> /tmp/log 2>&1 &
```

## Piège n°3 : Port non libéré après kill

```bash
fuser -k "${port}/tcp" 2>/dev/null || true
sleep 1  # Attendre que le système d'exploitation libère le port
```

Si `fuser -k` est suivi immédiatement du redémarrage, le port peut encore être en état `TIME_WAIT`. Toujours attendre au moins 1 seconde.

## Piège n°4 : Ne pas revérifier après correction

```bash
# ❌ La correction est tentée mais le résultat n'est pas vérifié
check_server "rag:8083"  # HTTP 000 → lance restart
# Le script continue sans vérifier si le restart a réellement fonctionné
```

**Bon pattern** : Revérifier l'état après correction, ou au moins reporter dans l'état si le restart a réussi.

## Structure de fichier d'état (state.json)

```json
{
  "servers": {
    "mon-api:8080": {
      "status": "ok",
      "http_code": "200",
      "last_check": 1700000000
    }
  },
  "corrections": [
    {
      "timestamp": 1700000000,
      "server": "mon-api:8080",
      "action": "restart",
      "result": "success",
      "time": "2026-07-22 01:34:30"
    }
  ],
  "alerts": [],
  "last_check": 1700000000,
  "uptime_start": 1700000000
}
```

## Checklist de conception

- [ ] Les services surveillés sont définis avec port, URL de health, commande de restart
- [ ] `check_http()` utilise le pattern `capture || fallback` (pas de double "000")
- [ ] Le redémarrage en cron utilise `bash -c` (pas `bash -lic`)
- [ ] Un `sleep 1` est présent entre `fuser -k` et le redémarrage
- [ ] L'état persistant est mis à jour après chaque cycle
- [ ] Les corrections échouées génèrent une alerte explicite
- [ ] Le rapport/wiki est généré après chaque cycle
- [ ] Les logs de correction sont stockés séparément des logs applicatifs