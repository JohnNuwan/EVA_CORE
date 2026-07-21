# Design "award" — synthèse des plateformes & techniques NIVEAU 1

Condensé des enseignements des plateformes de design primées, pour produire des
sites vitrines qui se démarquent du Bootstrap générique. Analyse basée sur les
lauréats réels (Awwwards SOTD, CSSDA WOTD "Flowty", Httpster).

## Plateformes (ce qu'elles récompensent)
- **Awwwards** (awwwards.com) → innovation technique (WebGL, 3D, expérimental).
- **CSS Design Awards** (cssdesignawards.com) → note explicitement UI/UX/INNOVATION ;
  plus "beau + utilisable". WOTD analysé : Flowty (Nuxt).
- **CSS Winner / Godly.website** → vitrines de tendances quotidiennes.
- **FWA** (thefwa.com) → gros budgets (WebGL+3D+vidéo), inspiration, pas actionnable
  à l'échelle freelance. Contenu 100 % JS-dynamique.
- **Httpster** (httpster.net) → minimalisme typographique ; preuve qu'un site sobre
  et typo peut être primé SANS animation complexe. Accessible à l'analyse.
- **Lapa Ninja / Land-book** → galeries de landing pages (structure vendeuse) mais
  protégées par Cloudflare (bot detection) → à consulter manuellement.
- SiteInspire/Behance : rate-limités (429) à l'analyse auto. Dribbble : design "shot"
  isolé, pas des sites fonctionnels.

## Stack technique dominante (constat réel)
- Animation : **GSAP + ScrollTrigger** (n°1), **Lenis** (scroll fluide — fait par
  Studio Freight, qui l'utilise avec Nuxt), SplitText (texte lettre par lettre),
  Barba.js (transitions de page).
- 3D/WebGL : Three.js + shaders GLSL — SEULEMENT sur gros budgets.
- Structure : Next.js/React ou Nuxt/Vue. Webflow prouve qu'on peut être primé en no-code.
- Jamais : Bootstrap, jQuery, thèmes WordPress génériques.

## 6 signatures visuelles award
1. Scroll narratif (scrollytelling, sections pinées) — GSAP ScrollTrigger.
2. Typographie héros animée (la typo EST le design) — SplitText.
3. WebGL/3D immersif (gros budgets).
4. Transitions de page fluides (Barba).
5. Curseur custom + boutons magnétiques/rolling-text.
6. Dark/light + contraste fort + grain "film".

## NIVEAU 1 (vendable 300–1500 €, ~80 % de l'effet / 20 % de la difficulté)
Tout réalisable en HTML/CSS/JS vanilla + CDN GSAP/ScrollTrigger/Lenis :
- Titre animé lettre par lettre ; révélations au scroll (titres ligne par ligne,
  éléments en cascade) ; manifeste dont les mots s'illuminent (scrub).
- Compteur ODOMÈTRE (colonnes 0-9 + translateY, style machine — vu sur Flowty).
- Bouton ROLLING-TEXT (lettres qui montent en cascade au survol, via clone + délais).
- Bouton circulaire "scroll-next" dans le hero (guidage UX).
- Curseur custom (point + anneau magnétique avec inertie).
- Grain "film" (feTurbulence SVG animé) ; dark mode ; UN accent vif unique.
- Typo serif éditorial (Fraunces) + grotesk (Space Grotesk), XXL, line-height ~1.0.

## Synthèse transversale (ce qui revient partout)
- Typo = facteur n°1 (serif éditorial ou grotesk condensé, tailles XXL, tracking serré).
- Couleur : fond sombre (#0e0e10) ou blanc cassé (#f4f2ec), JAMAIS de gris fade ;
  1 accent vif unique ; grain subtil.
- Layout : aligné GAUCHE, espace vide assumé, une idée par section.
- Motion : Lenis quasi-obligatoire ; micro-interactions soignées.

## Anti-slop (tics IA/générique à éviter — disqualifiant)
Gradient bleu/violet partout ; glassmorphism immotivé ; grille de 3 cartes
icône+titre+phrase uniformes ; bordure gauche déco (accent rail) ; Inter par défaut ;
hero centré générique ; fausses métriques décoratives. DIAGNOSTIQUER avant de
réparer : problème de composition → re-layout (pas recolor) ; palette/typo → recolor/
re-typeset ; décoration → remplacer par vraie hiérarchie (scale/poids/espacement).
Nota : un "chevauchement" de texte sur screenshot headless est souvent un artefact
de capture (vérifier le HTML : 1 nœud texte, hauteur normale) — pas un bug réel.

## Veille (15 min/semaine, manuelle)
Awwwards SOTD (innovation), CSSDA WOTD (équilibre UI/UX), Httpster (minimalisme),
Lapa Ninja/Land-book (landing), Godly.website (moderne). Noter ce qui revient.
