# Pièges et limites — Retours d'expérience terrain

Ce document compile les patterns et pièges découverts lors d'investigations
OSINT réelles — choses qu'aucun tuto ne mentionne.

---

## ⛔ Instagram — VERROUILLÉ sans authentification

**Depuis 2024, Meta a verrouillé TOUS les accès sans compte :**

| Méthode | Résultat |
|---------|----------|
| instaloader | `403 Forbidden — GraphQL query` |
| oEmbed API | Pas de thumbnail sans auth |
| dumpor.com / imginn | Sites morts ou bloqués |
| Browser tool | Login wall obligatoire |

**Solution** : soit exporter les cookies d'un Firefox où on est connecté,
soit utiliser une clé API Facebook Graph (développeur). Sans ça, **zéro
photo Instagram** n'est récupérable automatiquement.

---

## ☁️ Cloudflare — Bloque tous les sites de breach check

Tous les sites de vérification de brèches sont derrière Cloudflare anti-bot :

| Site | Bloqué ? |
|------|----------|
| haveibeenpwned.com | Oui |
| breachdirectory.org | Oui (API + web) |
| dehashed.com | Oui |
| leakcheck.io | Oui |

**Contournements** :
- HudsonRock API (PAS derrière Cloudflare — prioritaire)
- Vérification manuelle dans un vrai navigateur
- Clé API HIBP payante (pour l'API v3)

---

## 🐦 Sherlock — Pièges

- `--output` ne fonctionne qu'avec **UN seul pseudo** à la fois (sinon `IsADirectoryError`)
- `--csv` sans `--output` → pas de fichier sauvé
- Les chaînes YouTube trouvées par Sherlock peuvent être **404** quand on y accède (yt-dlp échoue)
- Format de sortie : `[+]` = trouvé, rien = pas trouvé (pas de `[-]`)

## 🧅 Maigret — Pièges

- `--no-recursive-scan` n'existe pas comme flag
- `-o` n'est pas un flag valide (utiliser `--html` et `--pdf`)
- `--pdf` nécessite `pip install 'maigret[pdf]'`
- Extrait automatiquement le **fullname** quand disponible (info critique !)

## ✉️ Holehe — Pièges

- **Un seul email par exécution** — les arguments multiples sont ignorés
- Rate-limiting **80%+** sans proxies rotatifs → résultats très partiels
- Résultats : `[+]` utilisé, `[-]` non utilisé, `[x]` rate limité

---

## 🎭 Homonymes de pseudo — Le piège HudsonRock

HudsonRock associe un **pseudo** à une machine infectée. Mais un pseudo peut
être utilisé par **plusieurs personnes différentes** dans le monde.

**Workflow de vérification :**
1. Extraire l'IP (`102.176.94.176`) depuis la réponse HudsonRock
2. Géolocaliser : `curl "http://ip-api.com/json/102.176.94.176"`
3. Lire le `computer_name` — ex: "Nutifafa Collins"
4. Rechercher ce nom sur le web → souvent un vrai nom de personne
5. Si le pays (Ghana) ne correspond pas à la cible (France) → **faux positif**

Exemple réel : `korosife` → machine "Nutifafa Collins" à Accra, Ghana.
La cible française n'a jamais eu cette machine → alerte ignorée.

---

## 📸 Photos — Ce qui marche et ce qui ne marche pas

**⚠️ RÈGLE : toujours vérifier avec `ls -la` ou `find` que les fichiers ont bien été téléchargés. Ne jamais annoncer "photos récupérées" sans avoir vérifié le contenu des dossiers.**

### ✅ Fonctionne sans auth
- **GitHub** : `curl https://avatars.githubusercontent.com/u/<ID>` — fiable, téléchargement immédiat
- **SoundCloud** : grep `i1.sndcdn.com/avatars-` dans le HTML de la page, puis curl
- **YouTube** : `yt-dlp --write-thumbnail --skip-download` (⚠️ si la chaîne est 404, yt-dlp échoue silencieusement ou télécharge une miniature cassée)
- **TikTok** : `gallery-dl` + oEmbed API (`thumbnail_url`)

### ❌ Ne fonctionne PAS sans auth
- **Instagram** : tout est bloqué (cf. section dédiée). Ne pas perdre de temps avec instaloader/oEmbed/dumpor.
- **Facebook** : login wall
- **Twitter/X** : nécessite tokens API

### Workflow de vérification post-téléchargement
```bash
# Après chaque tentative de téléchargement, VÉRIFIER :
find ~/lab/data/osint/<cible>/avatars -type f -exec ls -lh {} \;
find ~/lab/data/osint/<cible>/photos -type f -exec ls -lh {} \;
# Si le dossier est vide → le téléchargement a échoué → ne pas annoncer de succès
```

---

## 🔢 Téléphone — Ce qui est vraiment utile

### Sources fiables (France)
- **tellows.fr** — score de réputation, opérateur, commentaires
- **telephoneannuaire.fr** — association nom/adresse (parfois obsolète)
- **lannuaire.fr** — annuaire inversé

### Sources non fiables
- **numverify** — nécessite clé API, données peu fiables
- **twilio lookup** — payant, orienté entreprise

### Pièges
- Numéros **réattribués** (portabilité) : l'ancien titulaire reste dans les annuaires
- 06 03 / 06 27 = anciens indicatifs Orange/SFR, pas fiables depuis la portabilité
