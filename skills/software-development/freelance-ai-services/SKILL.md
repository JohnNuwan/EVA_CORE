---
name: freelance-ai-services
description: "Vendre et produire des prestations freelance assistées par IA (ComeUp, Malt, Fiverr). Couvre la rédaction de gigs/services, le positionnement tarifaire, les livrables techniques paramétrables (extraction PDF/OCR, automation, chatbot RAG, sites vitrines), la relation client et le statut micro-entreprise en France."
category: software-development
domain: freelance
---

# Freelance IA — Vendre & Produire des prestations

Méthodologie pour gagner de l'argent en freelance avec un agent IA comme producteur
technique. L'humain gère l'identité, la relation client et la facturation ; l'IA
rédige les offres et produit les livrables. Tout le contenu est en FRANÇAIS
(exigence utilisateur).

## Prérequis / cadre légal (France)
- L'agent IA n'a PAS d'existence légale : c'est l'humain qui s'inscrit, facture et
  encaisse. Toujours clarifier ce rôle dès le départ.
- Statut : micro-entreprise (auto-entrepreneur), création gratuite sur
  autoentrepreneur.urssaf.fr, activité "prestation de services informatiques".
- Un email dédié est recommandé (ProtonMail/Gmail) pour les plateformes + clients.

## Plateformes (ordre conseillé)
1. **ComeUp** (comeup.com) — démarrage le plus simple en France : inscription libre
   immédiate, clients FR, paiement sécurisé. Idéal pour les premiers avis.
2. **Malt** — paniers plus élevés, mais profil soumis à validation + statut requis.
3. **Fiverr / Upwork** — internationaux, plus de concurrence, en anglais.
Règle : UNE plateforme bien tenue bat trois profils bâclés. Commencer par ComeUp.

## Stratégie de lancement (2 premières semaines)
- Publier 3 services. Les nouveautés sont mises en avant par la plateforme.
- Prix d'appel volontairement bas (ex: 20 €) sur UN service pour récolter des AVIS
  5 étoiles vite ; la marge est dans les OPTIONS payantes, pas l'offre de base.
- Répondre aux contacts en < 1h (la plateforme met en avant les vendeurs réactifs,
  et le client choisit souvent le premier qui répond).
- Reformuler le besoin du client en 1 phrase + dire comment on le résout + délai.
  Jamais de réponse copiée-collée générique.
- Livrer EN AVANCE sur les premières commandes ; demander un avis après livraison.

## Services qui se vendent (avec prix réalistes)
1. **Extraction PDF/scans → Excel (OCR + IA)** — 20 € d'appel (30 PDF), options
   +30/+80 € (volume), +25 € pipeline réutilisable. Le plus simple pour débuter.
2. **Automatisation d'une tâche (Python/n8n)** — 80 € base, options multi-étapes,
   intégration API, planification. Cœur de métier.
3. **Chatbot RAG sur documents privés** — 250 € base, options multi-sources, mémoire,
   déploiement. Différenciant fort : hébergement sur GPU local = données 100%
   privées = argument RGPD.
4. **Site vitrine premium** — 300–1500 €, base "NIVEAU 1 award" (voir ci-dessous).
   Options : mise en ligne, light mode, sections, formulaire, multilingue.

## Livrables techniques paramétrables (ne pas recoder from scratch)
Produire des livrables TESTÉS et paramétrables AVANT la première commande, pour
livrer en quelques heures. Voir `references/livrables-techniques.md` pour le détail
(architecture, limites honnêtes, temps par mission).
- **Extracteur PDF→Excel** : PDF natif + bascule OCR auto (Tesseract fra+eng),
  regex CHAMPS à ADAPTER à chaque format de doc client (~30 min d'ajustement),
  Excel 3 feuilles (Données / Contrôle qualité / Texte brut).
- **Automation fusion/rapport** : fusion Excel/CSV + dédoublonnage + rapport.
  Pour toute AUTRE tâche (mail, planification), coder la spécifique à la demande.
- **Chatbot RAG** : moteur TF-IDF pur Python (zéro dépendance ML lourde), interface
  web stdlib, 2 modes (extractif sans LLM / génération via vLLM local). Seuil de
  pertinence à calibrer (~0.1) pour rejeter le hors-sujet sans perdre les synonymes.

## Design "award" pour sites vitrines (se démarquer)
Les concurrents freelance livrent du Bootstrap générique. Se différencier avec le
"NIVEAU 1 award" (~80 % de l'effet pour ~20 % de la difficulté, sans 3D) :
- **Stack** : HTML/CSS/JS vanilla + GSAP + ScrollTrigger + Lenis (CDN). Lenis est
  fait par Studio Freight ; GSAP+ScrollTrigger+Lenis = le trio standard award.
- **Techniques** : titre animé lettre par lettre, révélations au scroll, manifeste
  qui s'illumine, compteur odomètre, bouton rolling-text, curseur custom magnétique,
  grain "film", dark mode + UN accent vif unique, typo serif éditorial (Fraunces).
- **Anti-slop** : éviter gradient bleu/violet générique, grille de 3 cartes
  icône+titre+phrase uniformes, glassmorphism immotivé, Inter par défaut, hero
  centré générique. Diagnostiquer AVANT de réparer (re-layout si problème de
  composition, pas recolor).
- Pour la synthèse complète des plateformes de design (Awwwards, CSSDA, FWA,
  Httpster) et le template, voir `references/design-award-synthese.md`.
- Nota : les skills `claude-design` et `popular-web-designs` (packagés) fournissent
  la méthodologie de design et 54 design systems — les utiliser en complément.

## Honnêteté commerciale (ne pas survendre)
- Ne JAMAIS prétendre que l'IA est "meilleure qu'un humain partout". Vendre la
  vitesse (24/7, livraison 48 h), le coût (itérations quasi gratuites), la
  confidentialité (GPU dédié), la régularité documentée. C'est plus crédible.
- Ne pas vendre de signaux de trading (illégal en France sans agrément AMF), ni
  passer des challenges de prop firm pour autrui (interdit par les TOS).
- Les livrables sont des bases à personnaliser, pas du 100 % clé-en-main : prévoir
  le temps d'ajustement dans le prix.

## Support fichiers
- `references/livrables-techniques.md` — architecture, commandes, limites des
  livrables (extracteur, automation, RAG) et temps par mission.
- `references/design-award-synthese.md` — synthèse des sites award (stack, 6
  signatures, anti-slop, techniques NIVEAU 1) et veille.
- `references/bug-bounty-recon.md` — chaîne de recon bug bounty opérationnelle
  (piste revenu alternative à la cybersécurité, en marge du freelance).
