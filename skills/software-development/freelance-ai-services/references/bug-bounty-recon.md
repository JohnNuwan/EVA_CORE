# Bug bounty — chaîne de recon opérationnelle (piste revenu cybersécurité)

Méthodologie bug bounty validée en conditions réelles, en marge du freelance.
Zéro client ; revenu par primes. Placée ici car c'est une piste de revenu ; le
skill `advanced-pentesting-redteam` (packagé/protégé) couvre le pentest avancé
théorique mais pas cette entrée pratique.

## Installation (Go requis)
- Go : extraire l'archive officielle dans `/usr/local/go` (PAS dans ~/go, sinon
  conflit GOPATH=GOROOT : "both GOPATH and GOROOT are the same directory").
  Vérifier `go env GOPATH` (doit être ~/go, distinct de GOROOT).
- PATH : `export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH` (à persister dans ~/.bashrc).
- Outils : `go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest`
  `.../httpx/cmd/httpx@latest` `.../nuclei/v3/cmd/nuclei@latest`
  `github.com/lc/gau/v2/cmd/gau@latest`
- Prérequis réseau : la chaîne EXIGE des requêtes sortantes (recon + scans).
  Valider la connectivité (DNS + HTTPS) avant de diagnostiquer un outil "cassé".

## Chaîne de recon (ordre)
1. **subfinder** -d cible -silent -all → sous-domaines passifs (ex: 180 sur une démo).
2. **httpx** -l subs.txt -status-code -title -tech-detect → hôtes vivants + versions
   serveur/PHP (versions EOL = CVEs connues). Nota : `-silent` masque la bannière ;
   une cible HTTP-only peut renvoyer HTTP:000 (serveur force HTTPS) — tester sur une
   cible connue (google) pour valider l'outil.
3. **gau** -subs cible → URLs historiques Wayback/CommonCrawl. Repérer les `?id=`,
   `admin`, `api`, `upload`, `redirect`. Les archives contiennent parfois des payloads
   SQLi déjà tentés (`or 1=1--`, `waitfor delay`) = endpoints intéressants.
4. **nuclei** -l live.txt -severity low..critical -tags exposure,config,cve,misconfig
   → CVEs exposés. Sur cible de démo patchée, sortie vide = normal (moteur OK).

## Cibles débutant (ordre effort/récompense)
1. **XSS** (100–1000 €) — injecter `<script>alert(1)</script>` / `"><img src=x onerror=alert(1)>`
   dans chaque paramètre d'URL et champ de formulaire.
2. **IDOR** (200–2000 €) — LE meilleur ratio. Faire varier un ID dans l'URL
   (`?id=123`→`124`, `/order/1001`→`1002`) et comparer les réponses. Signal :
   contenus HTTP 200 DISTINCTS selon l'ID. Confirmer MANUELLEMENT qu'un ID montre
   les données d'un AUTRE compte. Outil : pour une URL gabarit avec un ID, boucler
   sur id..id+N, afficher status/taille/hash, alerter si >1 contenu 200 distinct.
3. Exposition de fichiers sensibles (`/.git/`, `/.env`, `/backup.zip`) — nuclei aide.

## Plateformes
YesWeHack (FR, paie en EUR, moins de concurrence), Intigriti (EU), HackerOne,
Bugcrowd. Commencer par un scope LARGE (*.domaine.com) + faible concurrence.

## Règles anti-bannissement
Rester dans le scope ; impact MINIMAL (lire 1 enregistrement, pas 10000) ; pas de
destruction/spam ; scans en mode safe ; rapport clair et reproductible (titre,
sévérité, étapes, impact, preuve) — un bon rapport est accepté ~2× plus vite.

## Revenus réalistes
Mois 1–2 : apprentissage, rapports "informative/duplicate" (normal). Mois 2–4 :
premières primes 100–500 € si régulier. Chasseurs réguliers : 500–5000 €/mois.
C'est un revenu de compétence : démarre lent, scale avec l'expérience.
