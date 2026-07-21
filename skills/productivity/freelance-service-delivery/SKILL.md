---
name: freelance-service-delivery
description: >-
  Monter une activité freelance de services IA/automation (ComeUp, Malt, Fiverr) :
  rédiger les gigs, préparer le profil plateforme, produire des livrables
  techniques paramétrables et testés (extraction PDF→Excel, automatisation
  fusion/rapport, chatbot RAG privé) prêts à adapter à chaque commande.
category: productivity
---

# Freelance — Prestations IA & Automation (ComeUp / Malt / Fiverr)

## Quand utiliser ce skill

- L'utilisateur veut gagner de l'argent en freelance avec de l'IA/automation.
- Il faut rédiger des gigs/annonces pour ComeUp, Malt, Fiverr, Upwork.
- Il faut produire le livrable technique d'une commande (extraction de données,
  automatisation, chatbot RAG) rapidement et proprement.

## Principe clé : l'agent produit, l'utilisateur vend

L'agent (moi) n'a pas d'identité légale : je ne peux NI créer de compte, NI
encaisser d'argent, NI m'inscrire sur les plateformes. La répartition est :

- **Utilisateur** : crée le compte, poste les gigs, gère la relation client,
  encaisse. C'est lui le freelance légal (micro-entreprise requise en France).
- **Agent** : rédige les gigs, prépare le profil, et surtout PRODUIT le
  livrable technique de chaque commande (code, scripts, docs).

Toujours clarifier cette répartition dès le départ pour éviter que l'utilisateur
attende que l'agent s'inscrive à sa place.

## Ordre de lancement recommandé (cash le plus rapide)

1. **ComeUp d'abord** (comeup.com) : inscription libre et immédiate (pas de
   validation de profil comme Malt), clients français, paiement sécurisé.
   Idéal pour récolter les premiers avis 5 étoiles.
2. Malt ensuite : paniers plus élevés mais profil soumis à validation.
3. Fiverr/Upwork en dernier : internationaux, plus de concurrence, en anglais.

Une seule plateforme bien tenue bat trois profils bâclés. Ne pas s'éparpiller.

## Les 4 services qui se vendent (et leurs livrables types)

Ces quatre services couvrent l'essentiel de la demande PME et ont des livrables
prêts à adapter. Voir `references/livrables-types.md` pour le détail technique
et les temps estimés.

1. **Extraction PDF/scans → Excel (OCR + IA)** — prix d'appel bas (~20 €).
   Sert à acheter des avis 5 étoiles rapidement (volume, livraison rapide).
   La vraie marge est dans les options (volume, pipeline réutilisable).
2. **Automatisation d'une tâche répétitive (Python/n8n)** — cœur de métier
   (~80 € base). Fusion Excel/CSV, nettoyage, rapport automatique, intégrations.
3. **Chatbot RAG sur documents privés** — panier élevé (~250 € base).
   Argument de vente clé : hébergement sur infra GPU locale = données 100%
   privées, conforme RGPD (différenciant fort face aux solutions OpenAI).
4. **Site vitrine premium (techniques "award")** — 300–1500 €. Template clé en
   main déjà construit et testé en navigateur :
   `~/revenus-alternatifs/livrables/04-template-vitrine-premium/`.
   Différencie immédiatement des concurrents qui livrent du Bootstrap générique.

## Sites "award" vendables (différenciation concurrence)

Analyse réelle des Sites of the Day Awwwards 2024-2026 (Izanami, Risk, Longbow,
Brunello Cucinelli AI, 21 Hrs on the Moon) : la stack gagnante est constante —
**GSAP + ScrollTrigger, Lenis (scroll fluide), SplitText (typo lettre par lettre),
Barba (transitions de page), Three.js/shaders GLSL**. Beaucoup sont faits en Webflow
(l'outil compte moins que le talent). Jamais Bootstrap/jQuery/thème générique.

6 signatures visuelles : scroll narratif (scrollytelling), typo héros animée,
WebGL/3D en fond, transitions de page fluides, curseur custom + boutons
magnétiques, dark/light + contraste fort + grain "film".

Vendre par NIVEAUX (honnêteté marché) :
- **Niveau 1 (300–1500 €, MAÎTRISÉ, template prêt)** : GSAP+Lenis+typo splittée+
  curseur custom+grain = ~80% de l'effet award pour ~20% de la difficulté.
  Personnalisation : 1 variable CSS `--accent` + textes = 30–60 min/client.
- Niveau 2 (1500–5000 €) : + Barba, canvas 2D custom, Lottie.
- Niveau 3 (5000 €+, studios) : Three.js + shaders custom. Pas le marché ComeUp.

CDNs : `gsap@3.12.5/dist/gsap.min.js`, `.../ScrollTrigger.min.js`,
`@studio-freight/lenis@1.0.42/dist/lenis.min.js` (jsdelivr).

Techniques additionnelles vues sur CSSDA (WOTD "Flowty", Nuxt), intégrées au
template : **compteur odomètre** (chiffres qui défilent verticalement style
machine, colonnes 0-9 + translateY), **bouton à lettres animées** (rolling text
au survol, clone + transitions en cascade), **bouton circulaire "scroll-next"**
dans le hero (guidage UX). Leçon CSSDA : un site primé = aussi une UX
irréprochable (une idée par section, preuve chiffrée), pas seulement du WebGL —
on peut atteindre un niveau "primé" sans 3D, avec rigueur UX + motion.

## Workflow de production d'un livrable

1. **Rédiger le gig AVANT de coder** : titre + accroche + description + offre
   de base + options payantes. Le prix d'appel est volontairement bas pour les
   premiers avis ; la marge est dans les options.
2. **Préparer un livrable "prêt à l'emploi" paramétrable** par service, TESTÉ
   en conditions réelles (générer des données de test, vérifier la sortie).
   Ne jamais livrer du code non exécuté.
3. **Le jour où une commande arrive** : adapter le livrable au besoin exact du
   client (regex, colonnes, config), tester sur ses fichiers d'exemple, livrer
   le résultat + une notice client claire (README-CLIENT.md).
4. **Documenter en français**, fournir le code source (le client n'est pas
   dépendant), inclure 14 jours de support.

## Conseils de lancement (2 premières semaines)

- Répondre aux contacts en moins d'1h : la plateforme met en avant les vendeurs
  réactifs, le client choisit souvent le premier qui répond.
- Livrer en avance sur les premières commandes → avis 5 étoiles "livré en avance".
- Après chaque livraison acceptée, demander explicitement un avis.
- Réponse client : reformuler son besoin en 1 phrase + dire comment on le résout
  + délai. Jamais de copier-coller générique.

## Pitfalls

- **Ne pas coder un livrable sans l'avoir testé.** Générer des données de test
  (PDF, Excel/CSV avec doublons, docs de démo) et vérifier la sortie réelle
  avant de dire "prêt". Le user exige du réel, pas du plausible.
- **Prix d'appel ≠ marge.** Le service 1 à ~20 € sert à acheter des avis, pas
  à gagner. La marge est dans les options payantes (+30 à +400 €). Le dire
  clairement à l'utilisateur pour qu'il ne sous-vende pas.
- **Statut légal.** En France : micro-entreprise (auto-entrepreneur) requise
  pour encaisser légalement. Création gratuite sur autoentrepreneur.urssaf.fr.
  Vérifier que l'utilisateur l'a AVANT de l'encourager à vendre.
- **Prévoir un venv dédié** pour les livrables (ne pas polluer le système) et
  noter la commande exacte du venv dans le README interne.
- **Honnêteté sur les limites.** Chaque livrable a des limites (regex à adapter
  par format de doc, TF-IDF qui ne comprend pas les synonymes, etc.). Les
  documenter dans un README interne pour que l'utilisateur ne survende pas.
- **Artefact de capture headless ≠ bug réel (vérification web).** Quand on
  vérifie un livrable HTML via un navigateur headless (screenshot), un texte
  peut apparaître "strié"/"chevauché"/dédoublé alors que le DOM est sain.
  Avant de "corriger" le code, vérifier le DOM réel via console
  (`childNodes.length`, `innerHTML`, `getBoundingClientRect().height`, erreurs
  console). Si le HTML est propre (1 nœud, hauteur normale, 0 erreur JS),
  l'artefact vient du moteur de rendu headless, pas du code — ne pas modifier
  le code pour un faux problème. Confirmer via console plutôt que via l'image.
- **Animation web : poser l'état initial.** Ne pas animer un élément vers
  `opacity:1`/`y:0` (GSAP) sans état de départ posé — utiliser `autoAlpha`
  (opacity+visibility) ou un état CSS initial explicite, sinon flash de contenu.
  Le clone d'un bouton "rolling text" doit être masqué par `overflow:hidden`.

## Références

- `references/livrables-types.md` — détail technique des 3 livrables types
  (extraction PDF→Excel, automatisation fusion/rapport, chatbot RAG), commandes
  exactes, points d'adaptation par client, limites honnêtes.
