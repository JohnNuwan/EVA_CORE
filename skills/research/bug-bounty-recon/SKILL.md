---
name: bug-bounty-recon
description: "Méthodologie et chaîne d'outils pour la reconnaissance bug bounty (subfinder, httpx, gau, nuclei) et la chasse aux vulnérabilités web débutant (XSS, IDOR, exposition). Couvre l'installation Go, le script de recon automatisée, les plateformes (YesWeHack, Intigriti, HackerOne), la méthode de test manuel, la rédaction de rapports, et les pièges d'environnement."
category: research
tags: [bug-bounty, recon, osint, pentest, web-security, xss, idor, nuclei, subfinder]
---

# Bug Bounty — Reconnaissance & Premières Primes

Méthodologie opérationnelle pour démarrer en bug bounty (France/Europe) : installation de la chaîne de recon, scan automatisé, ciblage des vulnérabilités à fort taux d'acceptation pour débutant (XSS, IDOR), et rédaction de rapports. Niveau : pratique, orienté premières primes.

---

## 1. Plateformes & stratégie d'entrée

- **YesWeHack** (https://yeswehack.com) — française, programmes EU/FR, paie en EUR. **Commencer ici** : moins de chasseurs, programmes FR peu concurrencés. **NOTE : l'inscription peut être fermée temporairement pour maintenance** — dans ce cas, basculer immédiatement sur Intigriti (la chaîne de recon fonctionne pareil sur leurs programmes) plutôt que d'abandonner la piste.
- **Intigriti** (https://intigriti.com) — européenne, bons programmes retail/SaaS.
- **HackerOne** (https://hackerone.com) — la plus grosse, plus de concurrence.

Stratégie : créer un compte sur les 3, mais concentrer l'effort sur YesWeHack au début. Choisir un programme au **scope large** (`*.domaine.com`) avec **peu de hackers** actifs.

---

## 2. Installation de la chaîne de recon (Go)

Prérequis : Go. Les 4 outils ProjectDiscovery + gau se compilent via `go install`.

### Installer Go proprement (éviter le piège GOPATH==GOROOT)
Ne JAMAIS extraire Go dans `$HOME/go` (c'est le GOPATH par défaut → warning "both GOPATH and GOROOT are the same directory"). Extraire hors GOPATH :
```bash
# Récupérer la dernière version stable
curl -s "https://go.dev/dl/?mode=json" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['version'])"
# Télécharger + extraire hors GOPATH (système ou user-local)
sudo tar -C /usr/local -xzf go.tgz            # GOROOT=/usr/local/go  (recommandé)
# ou sans sudo : tar -C $HOME/.local -xzf go.tgz
export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH
echo 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' >> ~/.bashrc
go version   # doit s'afficher SANS warning GOPATH/GOROOT
```

### Installer les outils de recon
```bash
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/lc/gau/v2/cmd/gau@latest
```
Binaires produits dans `$HOME/go/bin/`. Versions confirmées fonctionnelles : subfinder v2.14.0, nuclei v3.11.0.

---

## 3. Chaîne de recon automatisée

Script prêt à l'emploi : `scripts/recon.sh CIBLE` (et sa référence commentée `references/recon-script.md`). Détecteur IDOR : `scripts/idor_test.py "URL?id=N" N N+10`.

Principe (4 étapes) :
```bash
subfinder -d CIBLE -silent -all -o subs.txt            # sous-domaines passifs
httpx -l subs.txt -silent -status-code -title -tech-detect -o live.txt   # hôtes vivants
gau --threads 5 --subs CIBLE > urls.txt                # URLs historiques (Wayback, etc.)
nuclei -l live.txt -silent -severity low,medium,high,critical -o nuclei.txt  # CVEs/misconfig
```
Sorties à analyser ensuite : `nuclei.txt` (vulnérabilités détectées) et les URLs "juteuses" (avec paramètres, IDs, admin, upload) pour tests manuels.

---

## 4. Par quoi commencer (primes les plus accessibles débutant)

Ordre de difficulté croissant — rester sur les 2 premiers au début :

### XSS (Cross-Site Scripting)
- Payload de test : `<script>alert(1)</script>` ou `"><img src=x onerror=alert(1)>`
- Injecter dans CHAQUE paramètre d'URL et champ de formulaire.
- Prime typique : 100–1000 EUR. Rapport le plus couramment accepté.

### IDOR (Insecure Direct Object Reference) — meilleur ratio effort/récompense
- Changer un ID dans une URL : `/user/123` → `/user/124`, `?doc_id=5` → `?doc_id=6`
- Si on voit les données d'un AUTRE utilisateur = vulnérabilité.
- Prime typique : 200–2000 EUR. Très fréquent, peu testé rigoureusement.

### Autres (progression)
Exposition de fichiers sensibles (`/.git/`, `/.env`, `/backup.zip`, `/phpinfo.php` — nuclei les détecte en partie), open redirect, SSRF basique, directory listing.

Outil manuel indispensable : **Burp Suite Community** (gratuit) pour intercepter/rejouer les requêtes pendant les tests.

---

## 5. Règles d'or (éviter le bannissement)

- Toujours lire le **scope** du programme : ne toucher qu'aux domaines autorisés.
- Jamais de destruction/modification de données réelles, jamais de spam.
- Prouver l'impact avec le MINIMUM (lire 1 enregistrement, pas 10000).
- Pas de scan agressif (nuclei en mode "safe", pas de brute force massif).
- Un rapport clair et reproductible = triage rapide = paiement rapide.

---

## 6. Rédaction de rapport (ce qui fait accepter)

Structure attendue : **titre, sévérité, étapes de reproduction numérotées, impact, preuve** (screenshot/PoC). Un rapport bien écrit est accepté ~2x plus vite. L'assistant peut rédiger le rapport ; l'utilisateur fournit la preuve (tests navigateur via Burp).

---

## 7. Revenu réaliste

- Mois 1–2 : apprentissage, quelques rapports "informative/duplicate" (normal).
- Mois 2–4 : premières primes 100–500 EUR si régulier (quelques h/semaine).
- Chasseurs réguliers YesWeHack/Intigriti : 500–5000 EUR/mois. Revenu de compétence : démarre lent, scale avec l'expérience.

---

## 8. Pièges d'environnement (appris en session)

### Garde-fou de sécurité : commandes réseau/install/dotfile
Dans l'environnement Hermes, les commandes qui (a) installent des paquets / modifient le système, (b) font des appels réseau sortants (curl externe, DNS), ou (c) écrivent dans un dotfile (~/.bashrc) peuvent être BLOQUÉES par le garde-fou ou nécessiter une approbation explicite de l'utilisateur.
- Prévenir l'utilisateur AVANT de lancer ; proposer la commande pour approbation.
- Si une commande réseau est refusée, NE PAS retenter ni reformuler : livrer ce qui est possible hors-ligne (scripts, docs) et expliquer clairement ce qui reste à valider.
- Pour tester un outil réseau, utiliser une cible légale (ex. `testphp.vulnweb.com`, site de démo conçu pour) et le dire explicitement.
- Distinguer "l'outil est cassé" (à débugger) de "la commande n'est pas autorisée" (à escalader) — le refus d'une commande n'est PAS un échec de l'outil.

### Répartition des rôles (assistant / utilisateur)
- **Assistant** : recon automatisée, tri des endpoints, rédaction des rapports.
- **Utilisateur** : tests manuels navigateur (Burp), création des comptes plateformes, publication des gigs/rapports.
C'est un travail d'équipe : l'assistant ne peut ni cliquer sur les plateformes ni faire les tests navigateur authentifiés.
