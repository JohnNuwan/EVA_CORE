# Obsidian Vault & Standards OKF pour l'OSINT

> Architecture de connaissance pour investigations OSINT et pentest.
> Vault : `~/lab/knowledge/obsidian-cybersecurite/`

---

## Structure du vault

```
00-MOC/              → Maps of Content (Accueil, Arsenal-Outils)
01-OSINT/            → Méthodologie, SOCMINT, email, téléphone, scanners
02-Pentest/          → Nmap, Burp, Hydra, John, Hashcat, sqlmap
03-Exploitation/     → Metasploit, Web Attacks, Active Directory
04-PostExploit/      → PrivEsc, Pivoting, Wireshark
05-Forensics/        → Volatility, Autopsy, binwalk
06-Reverse/          → Ghidra, Radare2, GDB
07-Cloud/            → AWS, Azure, GCP, Kubernetes
08-Methodologie/     → Standards OKF, workflow, template rapport
09-Rapports/         → Dossiers d'investigation par cible
10-Datapackages/     → Données structurées (CSV + JSON)
99-Templates/        → Gabarits réutilisables
```

---

## Architecture ~/lab/ (style DeepMind)

```
~/lab/
├── tools/           → venv, Go, binaires
├── data/osint/      → données brutes par cible
├── knowledge/       → vault Obsidian
├── projects/        → projets en cours
├── configs/         → fichiers de config
└── scripts/         → utilitaires
```

Activation :
```bash
source ~/lab/tools/venvs/osint/bin/activate
export PATH=$HOME/lab/tools/bin:$HOME/lab/tools/go/bin:$HOME/lab/tools/go-workspace/bin:$PATH
```

---

## Standards OKF — Frictionless Data

Data Package : `datapackage.json` avec `resources` (CSV + JSON).
Validation : `frictionless validate datapackage.json`

---

## Wikilinks

```markdown
[[NomNote]]               → lien simple
[[NomNote|Texte]]         → alias
[[../Dossier/Note]]       → relatif
```

## Installation Obsidian (sans sudo)

```bash
curl -s https://api.github.com/repos/obsidianmd/obsidian-releases/releases/latest | \
  python3 -c "import sys,json;d=json.load(sys.stdin);[print(a['browser_download_url']) for a in d['assets'] if 'AppImage' in a['name'] and 'arm64' not in a['name']]" | \
  xargs curl -sL -o /tmp/Obsidian.AppImage
chmod +x /tmp/Obsidian.AppImage
cp /tmp/Obsidian.AppImage ~/lab/tools/bin/obsidian
~/lab/tools/bin/obsidian --vault ~/lab/knowledge/obsidian-cybersecurite
```
