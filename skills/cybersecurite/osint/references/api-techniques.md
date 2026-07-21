# APIs et techniques OSINT approfondies

Ces endpoints et techniques ont été validés en conditions réelles.
À utiliser pour passer d'un OSINT superficiel à une investigation approfondie.

---

## ☠️ HudsonRock — Infostealer check (PRIORITAIRE, gratuit)

```
GET https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=<PSEUDO>
```

Marche aussi avec emails et numéros de téléphone. Pas de clé API, pas de rate-limiting connu.

### Réponse si compromission

```json
{
  "message": "This username is associated with a computer that was infected...",
  "stealers": [{
    "date_compromised": "2023-10-19T09:52:40.000Z",
    "stealer_family": "Lumma",
    "computer_name": "Nutifafa Collins",
    "operating_system": "Windows 10 (10.0.19045)",
    "ip": "102.176.**.***",
    "top_passwords": ["C**********8", "[******N"],
    "top_logins": ["n*************@yahoo.com", "k***************@gmail.com"],
    "total_user_services": 56
  }]
}
```

### Workflow de validation — ÉVITER LES FAUX POSITIFS

Un pseudo peut être partagé par plusieurs personnes. NE PAS conclure avant vérification :

```
1. Extraire l'IP partiellement masquée (ex: 102.176.**.***)
2. Géolocaliser : curl "http://ip-api.com/json/102.176.0.0"
3. Vérifier le computer_name (ex: "Nutifafa Collins")
4. Rechercher ce nom sur le web → origine ethnique, pays probable
5. Croiser avec la localisation connue du sujet
6. Si divergence → homonyme de pseudo → faux positif
```

**Exemple documenté** : HudsonRock alerte sur "korosife" → machine "Nutifafa Collins",
IP 102.176.x.x à Accra, Ghana. Sujet français. → Étudiant ghanéen Nutifafa Collins Adzadi
utilise le même pseudo.

---

## Géolocalisation IP (gratuit, pas de clé)

```
GET http://ip-api.com/json/<IP>          → country, regionName, city, lat, lon, isp, as
GET https://ipapi.co/<IP>/json/          → rate-limité mais gratuit
```

Exemple : `102.176.94.176` → Ghana, Accra, Vodafone Ghana MBB, AS29614

---

## WordPress REST API

```
GET https://<site>.wordpress.com/wp-json/wp/v2/posts    → articles publiés
GET https://<site>.wordpress.com/wp-json/wp/v2/pages    → pages
GET https://<site>.wordpress.com/feed/                   → flux RSS
```

Blog vide découvert : savannahcombes.wordpress.com → site ID 62446530, créé 2013, 0 posts.

---

## TikTok oEmbed

```
GET https://www.tiktok.com/oembed?url=https://www.tiktok.com/@<USERNAME>
```

Retourne : `author_name` (nom affiché), `author_url`, `title`. Sans authentification.

Découvert : @savannahwolfcbs → "Real_ArcaneWolfdog", bio contient savannahcombes@mac.com en clair.

---

## Deezer — API artiste publique

```
GET https://api.deezer.com/search/artist?q=S%C3%A4nh   → recherche
GET https://api.deezer.com/artist/5533048               → détail (albums, fans, photo)
```

---

## Apple Music / MusicBrainz

```
GET https://itunes.apple.com/search?term=<ARTISTE>&entity=musicArtist&limit=5
GET https://musicbrainz.org/ws/2/artist/?query=artist:<NOM>&fmt=json
```

---

## Annuaires téléphoniques (France)

| Source | Format | Fiabilité |
|--------|--------|-----------|
| telephoneannuaire.fr | Nom + ville si listé | Variable |
| tellows.fr | Score de réputation, opérateur, commentaires | Bonne |
| lannuaire.fr | Annuaire inversé | Moyenne |
| aquiestcenumero.com | Avis communautaires | Faible |

### Interprétation tellows
- Score 1-3 : Fiable
- Score 4-6 : Neutre / mitigé
- Score 7-9 : Indésirable/arnaque

Cas réel : 0603625116 → score 5/9, classé "Arnaque", opérateur SFR.

---

## Sites de brèches — TOUS protégés par Cloudflare

Inaccessibles par curl/headless sans bypass :
- haveibeenpwned.com (API v3 nécessite clé payante $3.50/mois)
- breachdirectory.org, dehashed.com, leakcheck.io, intelx.io

→ Vérification manuelle obligatoire.
→ HudsonRock est la seule API gratuite et accessible pour les infostealers.

---

## Extraction de contenu JS (Linktree, Wix, React)

```bash
# Extraire le JSON inline des sites Wix/React
curl -sL URL | python3 -c "
import re, sys
html = sys.stdin.read()
matches = re.findall(r'\"description\":\"([^\"]+)\"', html)
for m in matches:
    print(m.replace('\\\\n', '\n'))
"
```

**Cas Wix/idspectacle** : les données de la fiche artiste sont dans du JSON inline.
Extraction par regex sur le champ "description" → parcours, formation, styles musicaux.

---

## Investigation artiste / personne publique (France)

Sources spécifiques :
- **idspectacle.com** — fiches d'artistes (bio, formation, contacts pro, affiche)
- **Deezer** — discographie, artiste ID
- **Spotify** — via holehe (confirmation d'inscription)
- **La1ere / France Info** — articles sur artistes ultramarins
- **Amazon** — livres auto-édités (auteur, résumé)

---

## Quirks et pièges des outils

| Outil | Problème | Workaround |
|-------|---------|------------|
| Sherlock | `--output` ne marche qu'avec UN pseudo | Scanner 1 à la fois |
| Maigret | `--no-recursive-scan` et `-o` n'existent pas | `--timeout 15 --html` |
| Maigret | PDF = `pip install 'maigret[pdf]'` | Installer l'extra |
| Holehe | UN seul email par exécution | Boucler |
| Holehe | 80%+ rate-limiting sans proxies | Accepter la perte |
| theHarvester | PyPI v0.0.1 vide | `git clone && pip install -e .` |
| h8mail | Inutilisable sans config | Créer config avec clés API |

---

## Signaux faibles

- **@mac.com** : ancien format Apple (pré-2012) → early adopter
- **Blog WordPress vide** : la date de création reste un signal (site ID séquentiel)
- **Instagram 0 followers / 800+ following** : compte "veille" passif
- **Pseudos dérivés** : "jaymoncel" = Jay + Moncel, "johnnuwan" = fusion prénoms
- **Initiales** : "jnm-creation" = John Nuwan Moncel
- **Âge dans bio** : "32 yo" → confirme année de naissance
- **Émojis drapeau** : 🇯🇵🗾⛩️ → lien avec le Japon (confirmé par tournée Club Med Hokkaido)
- **Tags géo** : "📍Gard" → localisation précise
- **Nom de machine Windows** : "Nutifafa Collins" + IP Ghana → étudiant ghanéen, pas le sujet français
