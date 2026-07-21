# Architecture du Lab — Style DeepMind

## Arborescence

```
~/lab/
├── README.md
├── activate.sh                          # source ~/lab/activate.sh → tout activer
├── tools/
│   ├── bin/                             # Binaires isolés (obsidian, wrappers)
│   ├── go/                              # Go toolchain (auto-installé)
│   ├── go-workspace/bin/                # Binaires Go compilés
│   │   ├── amass (50 MB)
│   │   ├── nuclei (178 MB)
│   │   ├── subfinder (32 MB)
│   │   ├── httpx (54 MB)
│   │   ├── naabu (34 MB)
│   │   └── age
│   ├── radare2/                         # Compilé depuis GitHub
│   ├── spiderfoot/                      # Cloné depuis GitHub
│   └── venvs/
│       └── osint/                       # Python + 15+ outils OSINT
├── data/
│   └── osint/
│       ├── john/                        # Données par cible
│       │   ├── avatars/
│       │   ├── donnees_brutes/
│       │   ├── photos/
│       │   └── rapports/
│       └── savannah/
├── knowledge/
│   └── obsidian-cybersecurite/          # Vault Obsidian
│       ├── 00-MOC/
│       ├── 01-OSINT/ .. 08-Methodologie/
│       ├── 09-Rapports/
│       ├── 10-Datapackages/
│       └── 99-Templates/
├── projects/                            # Projets en cours
├── configs/                             # Fichiers de configuration
└── scripts/
    └── sync-skills-obsidian.py          # Sync skills → vault
```

## Activation

```bash
source ~/lab/activate.sh
# Définit : PATH, GOROOT, GOPATH, VIRTUAL_ENV, OBSIDIAN_VAULT_PATH
```

## Serveur déporté (TheHive — 192.168.1.5)

Serveur LAN 32 cœurs, 125 GB RAM, 2× RTX 3090, Debian 13.
Utilisable pour : entraînement ML, délégation de tâches lourdes,
hashcat GPU, sandboxes Docker, Ollama LLM local.
SSH : `aza@192.168.1.5`

## Règles de nommage

- `data/osint/<cible>/` — une cible par dossier
- `rapports/XX_nom.md` — numérotés (01, 02...)
- `donnees_brutes/<outil>_vN.txt` — versionné si relancé
- `avatars/<plateforme>_<pseudo>.jpg` — traçable
