# Installation complète de l'arsenal OSINT — sans Docker ni sudo

Procédure testée sur Debian 13 (trixie) x86_64, Python 3.13, juillet 2026.

---

## Phase 1 — Environnement Python

```bash
# Créer le venv sans pip (Debian PEP 668)
python3 -m venv ~/osint-env --without-pip
source ~/osint-env/bin/activate

# Installer pip manuellement
curl -sL https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
python3 /tmp/get-pip.py
```

## Phase 2 — Outils Python (pip)

```bash
source ~/osint-env/bin/activate

# Pseudos + email (prioritaires)
pip install sherlock-project    # → 0.16.0
pip install maigret             # → 0.6.3
pip install holehe              # → 1.61
pip install socialscan          # → 2.0.1

# theHarvester — PAS via PyPI (v0.0.1 est cassé), depuis GitHub :
git clone --depth 1 https://github.com/laramies/theHarvester.git /tmp/theHarvester
cd /tmp/theHarvester && pip install -e . && cd ~
# → v4.11.1 installé

# Réseaux sociaux
pip install instaloader         # → 4.15.2
pip install snscrape            # → 0.7.0
pip install toutatis            # → 1.31

# Google OSINT
pip install ghunt               # → 2.3.4 (⚠️ conflit httpx possible)

# Automatisation
pip install bbot                # → 3.0.0 (50+ dépendances, ~200 Mo)

# SpiderFoot — depuis GitHub (pip échoue sur Python 3.13)
git clone --depth 1 https://github.com/smicallef/spiderfoot.git ~/osint-env/spiderfoot
pip install -r ~/osint-env/spiderfoot/requirements.txt
# ⚠️ lxml peut échouer — le core fonctionne quand même

# Recon-ng — depuis GitHub
git clone --depth 1 https://github.com/lanmaster53/recon-ng.git ~/osint-env/recon-ng
pip install -r ~/osint-env/recon-ng/REQUIREMENTS
```

## Phase 3 — Installer Go localement (sans sudo)

```bash
GO_VERSION="1.23.5"
curl -sL "https://go.dev/dl/go${GO_VERSION}.linux-amd64.tar.gz" -o /tmp/go.tar.gz
rm -rf ~/go-local ~/go-workspace
tar -C ~/ -xzf /tmp/go.tar.gz && mv ~/go ~/go-local

# Configurer l'environnement (à ajouter dans ~/.bashrc pour persistance)
export GOROOT=$HOME/go-local
export GOPATH=$HOME/go-workspace
export PATH=$GOROOT/bin:$GOPATH/bin:$PATH
```

## Phase 4 — Compiler les binaires Go

```bash
# Ces commandes téléchargent et compilent automatiquement
go install -v github.com/owasp-amass/amass/v4/...@latest                     # 50 MB
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest         # 178 MB

# Ces binaires existent aussi en releases GitHub (zip précompilé) si la compilation échoue
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest
```

### Alternative : binaires Go précompilés (si la compilation échoue)

```bash
# Exemple pour subfinder
VER=$(curl -s https://api.github.com/repos/projectdiscovery/subfinder/releases/latest | grep tag_name | cut -d'"' -f4)
curl -sL "https://github.com/projectdiscovery/subfinder/releases/download/${VER}/subfinder_${VER#v}_linux_amd64.zip" -o /tmp/tool.zip
unzip -o /tmp/tool.zip -d ~/go-workspace/bin/
chmod +x ~/go-workspace/bin/subfinder
```

## Phase 5 — Binaires additionnels

```bash
# PhoneInfoga — le pip (phoneinfoga==0.1) est obsolète, prendre le binaire Go :
VER=$(curl -s https://api.github.com/repos/sundowndev/phoneinfoga/releases/latest | grep tag_name | cut -d'"' -f4)
curl -sL "https://github.com/sundowndev/phoneinfoga/releases/download/${VER}/phoneinfoga_Linux_x86_64.tar.gz" -o /tmp/phoneinfoga.tar.gz
tar -xzf /tmp/phoneinfoga.tar.gz -C ~/go-workspace/bin/
chmod +x ~/go-workspace/bin/phoneinfoga
```

## Vérification finale

```bash
source ~/osint-env/bin/activate
export PATH=$HOME/go-workspace/bin:$PATH

echo "=== Python ==="
for tool in sherlock maigret holehe theHarvester instaloader snscrape toutatis bbot; do
    which $tool 2>/dev/null && echo "✅ $tool" || echo "❌ $tool"
done

echo "=== Go ==="
for tool in amass nuclei subfinder httpx naabu phoneinfoga; do
    ls ~/go-workspace/bin/$tool 2>/dev/null && echo "✅ $tool" || echo "❌ $tool"
done
```

---

## Pièges rencontrés

1. **theHarvester sur PyPI** : version 0.0.1, totalement cassée. Toujours installer depuis GitHub.
2. **Holehe multi-emails** : n'accepte qu'UN seul email par exécution. Les arguments multiples sont ignorés silencieusement.
3. **Sherlock --output** : ne fonctionne qu'avec UN pseudo à la fois. `--csv` + `--output /chemin/fichier.csv` (pas un dossier).
4. **Maigret arguments** : `--no-recursive-scan` et `-o` n'existent pas. Utiliser `--timeout 15 --html` pour un rapport.
5. **SpiderFoot pip** : pas de wheel pour Python 3.13. Installer depuis git.
6. **GHunt httpx** : conflit de version avec theHarvester (ghunt veut httpx<0.28, theHarvester veut httpx>=0.28). Cohabitation possible malgré l'avertissement.
7. **lxml** : échoue souvent à la compilation. Le core de SpiderFoot fonctionne quand même sans.
8. **Go install** : la première compilation de nuclei peut prendre 3-4 minutes (téléchargement + compilation de centaines de dépendances).
