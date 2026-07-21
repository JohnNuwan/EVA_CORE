# Photos et avatars — ce qui marche et ce qui ne marche pas

## ❌ Instagram — BLOQUÉ (depuis 2024)

Meta a verrouillé toutes les API publiques. Résultat : aucun outil ne
fonctionne sans authentification.

| Outil | Résultat |
|-------|----------|
| instaloader | 403 Forbidden — GraphQL bloqué |
| Instagram oEmbed API | Pas de thumbnail sans auth |
| dumpor.com / imginn | Plus fonctionnels |
| browser tool | Login wall |

**Contournement partiel** : exporter les cookies Firefox et les passer
à `gallery-dl` ou `instaloader`. Sans cela, **zéro photo Instagram**.

## ✅ GitHub

```bash
# Avatar (ID utilisateur trouvé via Maigret ou l'API)
curl -sL "https://avatars.githubusercontent.com/u/<USER_ID>" -o github_avatar.png

# Maigret extrait automatiquement l'ID GitHub (15447738 pour johnnuwan)
```

## ✅ YouTube

```bash
# Miniature de chaîne
yt-dlp --skip-download --write-thumbnail --convert-thumbnails jpg \
    -o "yt_%(uploader)s.%(ext)s" "https://www.youtube.com/@chaine"

# ⚠️ Certaines chaînes renvoient 404 même si elles existent
# Tester avec @handle plutôt que l'URL complète
```

## ✅ SoundCloud

```bash
# Avatar dans le HTML de la page
curl -sL "https://soundcloud.com/john-nuwan-moncel" | \
    grep -oP 'https://i1.sndcdn.com/avatars-[^"]+' | head -1

# Télécharger
curl -sL "<URL_AVATAR>" -o avatar.jpg
```

## ✅ TikTok

```bash
# oEmbed — thumbnail_url
curl -s "https://www.tiktok.com/oembed?url=https://www.tiktok.com/@savannahwolfcbs" | \
    python3 -c "import sys,json; print(json.load(sys.stdin).get('thumbnail_url',''))"

# gallery-dl — téléchargement massif
gallery-dl --directory ./tiktok "https://www.tiktok.com/@pseudo"
```

## Ordre de priorité pour la récupération de photos

1. GitHub (avatar → URL directe, pas de blocage)
2. SoundCloud (avatar → dans le HTML, pas de blocage)
3. TikTok (oEmbed → thumbnail, pas de blocage)
4. YouTube (yt-dlp → miniature, parfois 404)
5. Instagram (❌ bloqué sans cookies)
