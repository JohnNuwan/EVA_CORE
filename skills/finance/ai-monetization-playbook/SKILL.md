---
name: ai-monetization-playbook
description: >-
  Générer des revenus avec les compétences IA : freelance (ComeUp/Malt/Fiverr,
  gigs rédigés), influenceuse/creator IA (plateformes, réalité OnlyFans vs
  Fanvue), vidéo faceless. Ordre de priorité des pistes, pack ComeUp clé en
  main, répartition agent/humain.
category: finance
---

# Monétisation IA — Playbook revenus

## Présentation

Comment transformer les compétences IA + la stack locale (GPU, vLLM, ComfyUI)
en revenus. Trois pistes classées par rapidité de retour : freelance, vidéo
faceless, influenceuse IA. Ce skill capture l'ordre de priorité, la répartition
agent/humain, et les pièges de plateformes — pas un plan théorique, la méthode
validée avec le user.

**Déclencheurs :** "gagner de l'argent", "autre façon de gagner", "freelance",
"ComeUp", "Malt", "influenceuse IA", "OnlyFans", "Fanvue", "vidéo youtube",
"monétiser", "revenu".

## Ordre de priorité des pistes (par rapidité de cash)

1. **FREELANCE** — cash le plus rapide (première mission possible à 7 jours).
   Exige que le USER crée le compte et gère les clients (identité légale).
2. **VIDÉO FACELESS** — 2-6 mois (pubs après 1000 abos + 4000h vues), mais la
   machine (script→voix→visuel→MP4) peut être construite par l'agent tout de suite.
3. **INFLUENCEUSE IA** — le plus long (3-6 mois), marché saturé depuis 2024,
   exige cohérence de visage (LoRA) + niche + régularité quasi quotidienne.
4. **BUG BOUNTY** — voir skill `bug-bounty-hunting`. Zéro client mais revenu
   de compétence lent. Piste parallèle, pas principale.

Conseil validé : lancer le freelance AUJOURD'HUI (15 min de la part du user)
et construire le pipeline vidéo en parallèle. L'influenceuse vient après, une
fois la machinerie image/vidéo rodée — c'est la même qui sert aux deux.

## Répartition agent / humain (CRUCIAL)

- **AGENT** : rédige gigs, bio, services ; produit les livrables techniques
  (script OCR, automation n8n/Python, RAG) ; construit les pipelines.
- **HUMAIN (obligatoire)** : crée le compte (identité légale, KYC), poste les
  gigs, gère la relation client, encaisse. L'agent n'a pas d'existence légale :
  il ne peut ni créer de compte ni recevoir d'argent. Toujours être explicite
  là-dessus avec le user.

## Freelance — plateformes par ordre d'entrée

1. **ComeUp** (comeup.com) — inscription libre immédiate (pas de validation de
   profil comme Malt), clients FR, paiement sécurisé. Idéal premiers avis.
2. **Malt** — plus gros paniers mais profil validé + statut requis. 2e temps.
3. **Fiverr/Upwork** — international, concurrence, anglais. 3e temps.

Règle : UNE plateforme bien tenue bat trois profils bâclés. Prix d'appel bas
(ex 20 EUR) pour acheter les 5-10 premiers avis 5 étoiles, marge dans les
OPTIONS (+30 à +400 EUR). Répondre <1h (ComeUp met en avant les réactifs),
livrer en avance, demander un avis après chaque livraison acceptée.

Pack complet profil + 3 services au format exact ComeUp dans
`references/comeup-et-plateformes.md` (copie : ~/revenus-alternatifs/pack-comeup.md).

Services qui se vendent (exploitent la stack) : extraction PDF→Excel (OCR+IA),
automation de tâches (Python/n8n), chatbot RAG sur docs privés (argument RGPD :
hébergement sur GPU local, données non envoyées chez OpenAI).

## Influenceuse / creator IA — réalité des plateformes

- **OnlyFans : MAUVAISE option pour un modèle 100% IA.** Vérification d'identité
  d'une personne RÉELLE obligatoire ; les comptes de modèles purement IA qui ne
  représentent pas le créateur vérifié sont bannis (vagues de suspensions).
- **Fanvue** — politique officielle "AI Creator Friendly" : modèles IA autorisés
  ET promus. C'est le remplaçant d'OnlyFans pour ce cas (Aitana Lopez et co).
- Fansly / Unfiltrd — alternatives compatibles IA.
- Patreon — SFW uniquement (lifestyle/fashion).
- **Instagram/TikTok = vitrine gratuite obligatoire**, pas de la monétisation.
  On y attire, on monétise ailleurs (Fanvue/Patreon).

Règle d'or du milieu : attirer sur Insta/TikTok, monétiser sur Fanvue/Patreon.

## Pitfalls

- **Ne pas vendre du rêve.** Annoncer les délais honnêtes (freelance 7j, vidéo
  2-6 mois, influenceuse 3-6 mois, bug bounty 2-4 mois). Le user apprécie
  l'honnêteté sur les échecs/délais.
- **Statut légal** : en France, encaisser = micro-entreprise (gratuit, ~30 min
  sur autoentrepreneur.urssaf.fr). Vérifier si le user l'a déjà AVANT de le
  renvoyer la créer (il l'avait déjà — ne pas lui faire refaire).
- **Email dédié conseillé** (ProtonMail/Gmail) pour toutes les plateformes,
  mais le user peut utiliser l'existant.
- **Influenceuse IA = vrai travail de contenu**, pas de l'argent facile :
  identité forte + LoRA de cohérence + niche + quasi-quotidien. Minorité seulement
  dépasse quelques centaines d'EUR/mois.

## Références

- `references/comeup-et-plateformes.md` — pack ComeUp clé en main (profil + 3
  services au format exact) + tableau des plateformes creator IA.

## Skills liés

- `bug-bounty-hunting` — piste revenu sécurité (zéro client)
- `content-creation-guidelines` — exigence français pour tout contenu rédigé
