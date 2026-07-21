# OSINT : Retours d'expérience terrain

Journal des découvertes et patterns issus d'investigations réelles.

---

## Audit de sécurité email — le 14 juillet 2026

### HudsonRock — signal infostealer ☠️
L'API HudsonRock a détecté que le pseudo `korosife` était associé à une machine
compromise par le malware **Lumma Stealer** le 19 octobre 2023.

Détails extraits :
```
Date : 2023-10-19T09:52:40.000Z
Malware : Lumma Stealer
Machine : Nutifafa Collins (Windows 10 build 19045)
IP : 102.176.**.***
Services compromis : 56
Top passwords (masqués) : C**********8, [******N, a****t, Y******8, 2********8
Top logins (masqués) : n*************@yahoo.com, k***************@gmail.com
```

**Leçon** : HudsonRock est LA source à consulter systématiquement pour détecter
des infections passées par infostealer. L'API est gratuite et accessible :
```
curl -s "https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-username?username=<pseudo>"
```

### HIBP et BreachDirectory — bloqués par Cloudflare
Toutes les tentatives curl + Firefox headless ont échoué. HIBP nécessite une clé
API payante depuis la v3. BreachDirectory, DeHashed, LeakCheck : tous derrière
Cloudflare anti-bot. **Pour un audit automatisé, il faut soit une clé API payante,
soit passer par le navigateur de l'utilisateur en mode GUI.**

### h8mail — inutilisable sans clés API
L'installation pip fonctionne, mais sans fichier de configuration avec des clés
(Dehashed, Snusbase, etc.), l'outil ne produit aucun résultat.

### Holehe — rate-limiting massif
Sur 121 sites, 80%+ retournent `[x] rate limit` sans proxy. Le résultat est
inutilisable pour confirmer/infirmer une inscription. Utilisable uniquement
avec des proxies rotatifs ou une connexion résidentielle.

### Socialscan — mêmes limitations que Holehe
API des plateformes sociales (Twitter, GitHub, Instagram) bloque rapidement
les requêtes non authentifiées. Résultat : `QueryError`, `KeyError`, `ServerDisconnectedError`.

### Synthèse : stack d'audit email recommandée
```
1. HudsonRock API — gratuit, immédiat, critique (infostealer)
2. HIBP manuel via navigateur — gratuit, fiable, mais manuel
3. h8mail avec clés API payantes — si budget disponible
4. Holehe/Socialscan — uniquement avec proxies
```
### Résumé

Investigation complète d'un individu à partir de son nom complet
et numéro de téléphone. Utilisation de Sherlock (350+ sites), Maigret (509 sites),
Holehe (121 sites), Socialscan, HudsonRock, et recherche web manuelle.

### Résultats quantifiés
- **5 pseudos testés** : johnnuwan, jaymoncel, John_Nuwan, jnmcreation, korosife
- **22 plateformes uniques** trouvées (dédupliquées)
- **5 comptes** pour johnnuwan, **8** pour jaymoncel, **9** pour korosife
- **Maigret** a extrait : nom complet, avatar GitHub, user ID GitHub (15447738),
  première activité (2015-10-30), tags (coding, social, photo, porn, webcam, sharing)

### Patterns découverts

#### 1. Pseudos dérivés du nom réel — pattern récurrent
```
John Nuwan Moncel →
  johnnuwan     (fusion prénom 1 + prénom 2)
  jaymoncel     (diminutif Jay + nom)
  John_Nuwan    (prénom 1 + prénom 2)
  jnmcreation   (initiales J.N.M. + creation)
  korosife      (pseudo gaming, sans lien évident)
```

**Leçon** : toujours tester les variantes : fusion de prénoms, initiales,
diminutifs, pseudos gaming sans lien apparent.

#### 2. Sherlock per-username obligatoire
`--output` ne fonctionne pas avec plusieurs pseudos → lancer N exécutions.
`--print-found` suffit pour le stdout si le CSV n'est pas critique.

#### 3. Rate-limiting Holehe sans proxies = 80%+ de perte
Sur 121 sites, seuls ~15 répondent sans proxy. Résultat : quasi impossible
de confirmer une inscription sans proxies rotatifs.

#### 4. HudsonRock — toujours vérifier l'IP avant de conclure ☠️⚡
Le pseudo `korosife` a été détecté dans HudsonRock (Lumma Stealer, 56 credentials).
**Mais** : l'IP 102.176.94.176 est géolocalisée à Accra, Ghana (Vodafone MBB),
sur une machine nommée "Nutifafa Collins" (étudiant ghanéen).
→ **Faux positif dû au partage de pseudo**. Le sujet n'a jamais eu cette machine.

**Règle d'or** : quand HudsonRock signale un infostealer, TOUJOURS :
1. Extraire l'IP du log (partiellement masquée : 102.176.**.***)
2. Géolocaliser l'IP (ip-api.com, ipapi.co)
3. Vérifier le nom de la machine (`computer_name`)
4. Croiser avec les infos connues du sujet (localisation, machines possédées)
5. Rechercher le nom du propriétaire de la machine dans les sources académiques/réseaux sociaux

Sans cette vérification, on aurait annoncé une fausse compromission.

#### 5. Numéro de téléphone — piège de la réattribution
Le 06 03 62 51 16 est listé sous "COLOMES AMANDINE" à Gerzat (63 360)
dans un annuaire public. Soit une réattribution, soit une erreur.
Ne jamais considérer un numéro d'annuaire comme définitif.

#### 6. Pappers.fr — mine d'or pour les entreprises individuelles
SIRET, date de création, adresse du siège, tout est public.
Création le 24/03/2025 → moins de 18 mois d'existence.

---

## Investigation Savannah Combes (Sänh Wolf) — 14 juillet 2026

### Contexte
Investigation d'une artiste/auteure française à partir de son email (@mac.com),
nom, et numéro de téléphone. Profil OSINT nettement plus propre que le cas précédent.

### Résultats quantifiés
- **3 pseudos testés** (Sherlock) : savannahcombes, sanhwolf, savannahwolfcbs
- **11 comptes trouvés** via Sherlock, +3 Instagram/TikTok en manuel
- **HudsonRock** : 3 pseudos testés, **zéro infection** ✅
- **Holehe** : email confirmé sur Spotify et Twitter/X (2 hits positifs sur 121)
- **Téléphone** : aucune trace publique (très bon signe)

### Patterns découverts

#### 1. Séparation des personas — pattern pro
Savannah maintient **deux personas distincts** :
- **Artiste** (@sanhwolf, 4 326 followers) : chanteuse, cabaret, Gold Singers
- **Auteure** (@savannahcombes, 78 followers) : thriller psychologique, Amazon

Les deux comptes Instagram ne se cross-linkent pas → bonne pratique de cloisonnement.
La bio de l'un (CHANTEUSE ~ Monaco/Lyon) n'a aucun lien avec l'autre (Auteure ~ thriller).

**Leçon** : quand un sujet a plusieurs pseudos, vérifier s'il y a **cloisonnement
volontaire** (bonne pratique) ou **fragmentation involontaire** (fuite d'info).

#### 2. Email visible dans la bio TikTok — risque fréquent
Le TikTok @savannahwolfcbs (19K followers) affiche l'email en clair :
"Contact: savannahcombes@mac.com". C'est le seul point faible de son profil.
Pattern très courant chez les créateurs de contenu — à signaler systématiquement.

#### 3. Stage name vs civil name — email cohérent
L'email savannahcombes@mac.com est le nom civil, pas le nom de scène.
Utilisé partout (Spotify, Twitter, TikTok). Le nom de scène "Sänh Wolf"
apparaît UNIQUEMENT sur le compte artiste (@sanhwolf).

#### 4. Compte TikTok viral ≠ compte Instagram pro
19K followers sur TikTok vs 4 326 sur Instagram → le TikTok est le canal
principal d'acquisition. L'Instagram est plus "vitrine" pour les clients luxe.

#### 5. HudsonRock propre = bon indicateur de sécurité
Zéro infection sur 3 pseudos. Le sujet a probablement de bonnes pratiques
(numéros de tel propres, pas d'infostealer, email @mac.com sécurisé Apple).
Un profil OSINT "propre" est en soi une information utile.

#### 6. Pseudo homonyme intercontinental — toujours géolocaliser (rappel)
Même leçon que pour John : le pseudo "korosife" était partagé avec un étudiant
ghanéen → HudsonRock signalait une infection qui ne concernait pas John.
**Toujours croiser IP + nom de machine + localisation du sujet avant de conclure.**

### Résultats bruts Sherlock (extraits)

```
johnnuwan : GitHub, YouTube, Threads
jaymoncel : Behance, Duolingo, GitLab, LinkedIn, Snapchat, YouTube, Pinterest, Threads
korosife  : Chess.com, Discord, SoundCloud, TikTok, TradingView, YouTube, osu!, Pinterest, HudsonRock
John_Nuwan: Periscope, YouTube, omg.lol
jnmcreation: TikTok, YouTube
```

### Résultats bruts Maigret (extraits)

```
Fullname: John Nuwan Moncel
Interests: coding (2), social (2), photo (1), porn (1), webcam (1), sharing (1)
First seen: 2015-10-30T15:46:21Z
GitHub User ID: 15447738
Avatar: https://avatars.githubusercontent.com/u/15447738?v=4
```

### Structure du rapport final

Le rapport a suivi le gabarit `references/rapport-type.md` avec les sections :
1. Identité (nom, pseudos, first seen)
2. Localisation géographique (adresse, SIRET, zone d'activité)
3. Numéro de téléphone (analyse, association trouvée)
4. Présence réseaux sociaux (tableau par pseudo avec URLs)
5. Recherche d'emails (Holehe, résultats)
6. Activité professionnelle (LinkedIn, Pappers)
7. Projets techniques (GitHub repos)
8. Centres d'intérêt
9. Analyse chronologique
10. Cartographie d'exposition (matrice de risque)
11. Recommandations de sécurité
12. Sources et outils utilisés
13. Limites et pistes d'approfondissement
