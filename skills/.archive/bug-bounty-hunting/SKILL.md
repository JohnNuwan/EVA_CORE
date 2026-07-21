---
name: bug-bounty-hunting
description: "Chasse aux vulnérabilités web en bug bounty (YesWeHack, Intigriti, HackerOne). Chaîne de recon automatisée subfinder→httpx→gau→nuclei, détection IDOR/XSS, méthode de rapport, règles anti-bannissement. Pour générer des revenus par primes sur programmes autorisés."
category: security
domain: cybersecurity
---

# Bug Bounty — Chasse aux Vulnérabilités Web

## Présentation
Ce skill couvre la chasse aux vulnérabilités web dans un cadre bug bounty LÉGAL
(programmes autorisés uniquement). Il documente la chaîne de recon automatisée,
la détection IDOR/XSS, la méthode de rapport, et les règles anti-bannissement.
Objectif : générer des revenus par primes, sans client, en capitalisant compétence.

⚖️ CADRE LÉGAL : ne tester QUE des cibles dans le scope explicite d'un programme
auquel tu es inscrit. Toute cible hors scope = illégal. Voir references/bug-bounty-recon.md.

## Quand utiliser ce skill
- L'utilisateur veut gagner de l'argent via le bug bounty / la sécurité offensive.
- Lancer une recon sur un domaine autorisé, trier la surface d'attaque.
- Détecter IDOR, XSS, exposition de fichiers, mauvaises configs.
- Rédiger un rapport de vulnérabilité accepté rapidement.

## Setup (une fois)
Go + 4 outils ProjectDiscovery/gau. Commandes exactes et pièges validés dans
references/bug-bounty-recon.md. Points critiques :
- Installer Go dans `/usr/local/go`, JAMAIS `~/go` (sinon conflit GOPATH==GOROOT).
- Tester httpx SANS `-silent` d'abord pour valider la connectivité.
- HTTP:000 sur une cible = forcer `https://` explicite, vérifier DNS+HTTPS d'abord.

## Chaîne de recon (automatisable par l'agent)
Ordre : subfinder → httpx → gau → nuclei.
1. subfinder : sous-domaines passifs.
2. httpx : hôtes vivants + tech-detect (versions EOL = CVEs connues).
3. gau : URLs historiques + filtrage des endpoints à paramètres (`?id=`, admin, api...).
4. nuclei : CVEs exposés, mauvaises configs, technos vulnérables.
Script prêt : `~/revenus-alternatifs/outils/recon.sh CIBLE`.

## Détection IDOR (script : ~/revenus-alternatifs/outils/idor_test.py)
Faire varier un ID numérique, comparer status/taille/hash. IDs différents → contenus
HTTP 200 DIFFÉRENTS = signal IDOR. Valider MANUELLEMENT qu'un ID expose les données
d'un AUTRE compte (c'est ça la vulnérabilité, pas juste un contenu différent).

## Répartition agent / humain
- AGENT : recon, tri endpoints, détection IDOR automatisée, rédaction du rapport.
- HUMAIN : tests manuels XSS/IDOR dans Burp Suite Community (navigateur + compte),
  validation que l'IDOR expose bien des données d'autrui.

## Cibles débutant (effort/récompense)
1. IDOR (200-2000 EUR, peu testé, le plus accessible).
2. XSS reflété/stocké (100-1000 EUR, le plus courant) — injecter dans CHAQUE param/champ.
3. Exposition fichiers sensibles (/.git/ /.env /backup.zip) — détecté par nuclei.
4. Open redirect, SSRF basique, directory listing.

## Règles d'or (anti-bannissement)
- Scope strict, jamais de destruction/modification, prouver avec le MINIMUM,
  pas de scan agressif, rapport clair et reproductible.

## Revenu réaliste
Démarre lent (mois 1-2 = apprentissage), primes 100-500 EUR ensuite, chasseurs
réguliers 500-5000 EUR/mois. Revenu de compétence qui scale. Plateformes :
YesWeHack (FR, priorité), Intigriti (EU), HackerOne (gros, concurrence).

## Références et scripts
- references/bug-bounty-recon.md — setup détaillé, pièges validés, méthode complète.
- scripts/recon.sh — chaîne recon subfinder→httpx→gau→nuclei (syntaxe validée).
- scripts/idor_test.py — détecteur IDOR par variation d'ID (validé sur démo).
- Copies locales validées : ~/revenus-alternatifs/outils/{recon.sh, idor_test.py}
