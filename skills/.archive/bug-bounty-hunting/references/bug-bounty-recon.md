# BUG BOUNTY — GUIDE OPÉRATIONNEL (France / EU)
# Validé en conditions réelles le 2026-07-18 sur vulnweb.com (cible de démo autorisée).

## SETUP OUTILS (testé et fonctionnel)

Go est requis pour compiler les 4 outils ProjectDiscovery + gau.

```bash
# 1. Go — installer dans /usr/local/go (PAS ~/go, sinon conflit GOPATH)
#    Récupère la version actuelle depuis https://go.dev/dl/?mode=json
cd /tmp && curl -sL -o go.tgz https://go.dev/dl/go1.26.5.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go.tgz
export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH
echo 'export PATH=/usr/local/go/bin:$HOME/go/bin:$PATH' >> ~/.bashrc

# 2. Les 4 outils (compilation parallèle, ~2-3 min)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest &
go install github.com/projectdiscovery/httpx/cmd/httpx@latest &
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest &
go install github.com/lc/gau/v2/cmd/gau@latest &
wait
```

### Pièges rencontrés (fixes validés)
- **GOPATH == GOROOT** : si tu extrais Go dans `~/go` (défaut), `go version` affiche
  "warning: both GOPATH and GOROOT are the same directory". FIX : déplacer Go vers
  `/usr/local/go` et laisser GOPATH=`~/go` séparé. Ne jamais installer Go dans `~/go`.
- **httpx `-silent` masque la bannière mais aussi les erreurs réseau** : tester d'abord
  SANS `-silent` sur une cible connue (google.com) pour valider la connectivité.
- **HTTP:000 sur une cible** = serveur qui force HTTPS ou filtre le HTTP. Tester en
  `https://` explicite. Vérifier la connectivité de base (DNS + HTTPS) avant d'incriminer
  l'outil.
- **gau** affiche un warning bénin "config /home/user/.gau.toml not found" — ignorable,
  il tourne avec la config par défaut.

## CHAÎNE DE RECON (script prêt : ~/revenus-alternatifs/outils/recon.sh)

Ordre : subfinder → httpx → gau → nuclei.

```bash
# 1) Sous-domaines passifs
subfinder -d CIBLE -silent -all -o subs.txt

# 2) Hôtes vivants + tech-detect (versions serveur = CVEs si EOL)
httpx -l subs.txt -silent -threads 50 -status-code -title -tech-detect -web-server -o live.txt

# 3) URLs historiques (Wayback/Common Crawl/AlienVault) + filtrage endpoints à params
gau --threads 5 --subs CIBLE > urls.txt
grep -Ei '\?|admin|api|upload|redirect|token|auth|debug|backup|config' urls.txt | sort -u > urls-interessantes.txt

# 4) Scan vulnérabilités connues
nuclei -l live.txt -silent -severity low,medium,high,critical -tags exposure,config,cve,misconfig -o nuclei.txt
```

Résultat réel sur vulnweb.com : 180 sous-domaines, 3 hôtes vivants (Apache 2.4.25/Debian,
IIS 8.5, PHP 7.1.26 — toutes EOL), 12 870 URLs à creuser.

## DÉTECTEUR IDOR (script prêt : ~/revenus-alternatifs/outils/idor_test.py)

Principe validé : faire varier un ID numérique dans l'URL, comparer status/taille/hash.
Si des IDs différents renvoient des HTTP 200 avec contenus DIFFÉRENTS → IDOR probable.

```bash
python3 idor_test.py "https://site.com/profil?id=123" 123 130   # teste id=123..130
python3 idor_test.py "https://site.com/order/1001/details" 1001 1010
```

Sur la démo : 5 contenus HTTP 200 distincts détectés (chaque ID = une donnée différente).
Le signal clé = IDs différents → contenus différents. Reste à vérifier MANUELLEMENT
qu'un ID montre les données d'un AUTRE compte utilisateur (c'est ça la vulnérabilité).

## PLATEFORMES (comptes gratuits)
1. **YesWeHack** (yeswehack.com) — FRANÇAISE, programmes EU/FR, paie en EUR. PRIORITÉ.
2. **Intigriti** (intigriti.com) — européenne, bons programmes retail/SaaS.
3. **HackerOne** (hackerone.com) — la plus grosse, plus de concurrence.

Commencer par YesWeHack : moins de chasseurs, programmes FR peu concurrencés.

## CIBLES DÉBUTANT (ordre effort/récompense)
1. **IDOR** — LE plus accessible. Change un ID dans une URL (/user/123→124, ?doc_id=5→6).
   Si tu vois les données d'un autre = vulnérabilité. Prime 200-2000 EUR. Peu testé.
2. **XSS** reflété/stocké — injecte `<script>alert(1)</script>` ou `"><img src=x onerror=alert(1)>`
   dans CHAQUE paramètre d'URL et champ de formulaire. Prime 100-1000 EUR. Le plus courant.
3. **Exposition fichiers sensibles** — /.git/ /.env /backup.zip /phpinfo.php (nuclei les détecte).
4. Open redirect, SSRF basique, directory listing.

## MÉTHODE DE TRAVAIL (répartition agent / humain)
- AGENT (automatisable) : recon (recon.sh), tri des endpoints à params, détection IDOR
  (idor_test.py), rédaction du rapport.
- HUMAIN (navigateur + compte) : tests manuels XSS/IDOR dans Burp Suite Community
  (gratuit) pour intercepter/rejouer, validation que l'IDOR expose bien des données d'autrui.

Un rapport bien écrit est accepté ~2x plus vite. Format : titre, sévérité, étapes de
reproduction numérotées, impact concret, preuve (capture/requête).

## RÈGLES D'OR (anti-bannissement)
- Lire TOUJOURS le scope : ne toucher qu'aux domaines autorisés.
- Jamais de destruction/modification de données réelles, jamais de spam.
- Prouver l'impact avec le MINIMUM (1 enregistrement, pas 10 000).
- Pas de scan agressif (nuclei en mode "safe", pas de brute force massif).
- Un rapport clair et reproductible = triage rapide = paiement rapide.

## REVENU RÉALISTE
- Mois 1-2 : apprentissage, quelques "informative/duplicate" (normal).
- Mois 2-4 : premières primes 100-500 EUR si régulier (quelques h/semaine).
- Chasseurs réguliers YesWeHack/Intigriti : 500-5000 EUR/mois. Revenu de compétence,
  démarre lent, scale avec l'expérience. Zéro client nécessaire.

## FICHIERS
- ~/revenus-alternatifs/outils/recon.sh        — chaîne recon complète (syntaxe validée)
- ~/revenus-alternatifs/outils/idor_test.py    — détecteur IDOR (validé sur démo)
- ~/revenus-alternatifs/bug-bounty-demarrage.md — guide utilisateur
