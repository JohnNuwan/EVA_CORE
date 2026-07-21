# Isolation réseau MT5 sous Wine — preuves, diagnostic, alternatives

Session 2026-07-18, The Hive (Debian 13, Wine 10.0, terminal FTMO build 6032, MetaTrader5 Python 5.0.5735).

## Protocole de diagnostic (réutilisable)

Pour vérifier si un terminal MT5 sous Wine s'est VRAIMENT connecté à son broker (les logs seuls ne suffisent pas) :

```bash
# 1. Logs terminal (UTF-16LE) : chercher login/connect/ping — absence = pas connecté
iconv -f UTF-16LE -t UTF-8 "$WINEPREFIX/drive_c/Program Files/FTMO Global Markets MT5 Terminal/logs/$(date +%Y%m%d).log" | grep -iE "login|connect|ping|authorized"

# 2. Historique téléchargé : seulement 4 paires + 2023.hcc = défauts MetaQuotes, JAMAIS connecté
ls "$WINEPREFIX/drive_c/Program Files/FTMO Global Markets MT5 Terminal/Bases/Default/History/"

# 3. Liste des symboles : 13 symboles forex MetaQuotes par défaut = pas de symboles broker
strings -e l "$WINEPREFIX/drive_c/Program Files/FTMO Global Markets MT5 Terminal/Bases/Default/Symbols/selected-0.dat" | grep -E "^[A-Z0-9]{3,10}$"

# 4. Fichiers modifiés depuis le dernier démarrage : si seulement Config/llm-agent/logs, rien de réseau
find "$WINEPREFIX/drive_c/Program Files/FTMO Global Markets MT5 Terminal/" -type f -newermt "YYYY-MM-DD HH:MM"
```

Critère de décision : si (2) montre seulement EURUSD/GBPUSD/USDCHF/USDJPY et (3) seulement 13 symboles par défaut, le terminal n'a JAMAIS authentifié un broker. L'IPC Python (-10005 IPC timeout) est muet pour cette raison, pas pour un problème de protocole.

## Résultat constaté

- Terminal démarre, MCP écoute sur 22346, compilation des 131 exemples OK au 1er boot.
- Zéro connexion TCP sortante vers FTMO malgré `/login /password /server` en ligne de commande.
- Historique : uniquement 4 paires, `2023.hcc` horodaté du 1er démarrage (7:41).
- Wine lui-même a le réseau : `wine cmd /c "ping ftmo.com"` répond (DNS + ICMP OK). Le blocage est au niveau de la couche socket/SSL du terminal, pas de la connectivité de base.
- `MetaEditor64.exe /compile:"...mq5"` sous Wine : silencieux, aucun .ex5 produit, aucune ligne de log — la compilation CLI ne fonctionne pas (seule la compilation complète au 1er démarrage du terminal a eu lieu).

## Alternatives évaluées (toutes écartées)

| Approche | Résultat | Détail |
|---|---|---|
| Wine + Xvfb local | ❌ | isolation réseau ci-dessus |
| Wine + GUI (X11 sur Xvfb, xhost +SI) | ❌ | terminal lancé, jamais de fenêtre de login utilisable en headless ; même isolation |
| Docker `gmag11/metatrader5_vnc` | ❌ | même Wine 10.0, même isolation (Bases/ identique). L'image embarque KasmVNC + install auto MT5 — réutilisable si on veut un VNC, mais ne résout pas Wine |
| MCP HTTP 22346/22345 | ❌ | 401 sur POST/GET/OPTIONS malgré Bearer frais d'`assistant.ini` — voir `ftmo-terminal-mcp.md` |
| `tanguy-pauwels/trading-sdk` | ⚠️ 1 astuce | seule la technique `common.ini [Experts] Enabled=1` (Piège 7) est réutilisable ; le reste appelle `mt5.initialize()` comme nous |
| `tanguy-pauwels/script-mt5-wine` | ❌ | .bat venv Windows, rien pour Linux |
| EA MQL5 → fichier CSV | non testé | bloqué par l'impossibilité de compiler (MetaEditor CLI silencieux) ; reste une piste si la compilation GUI fonctionne un jour |

Gotcha externe corroborant (theauheral/mt5-mac-bridge README) : « -10005 IPC timeout on a fresh terminal until you log into a broker once via the GUI — selecting the company alone isn't enough. » + « 10027 AutoTrading disabled until the Algo Trading toolbar button is green ». Même conclusion : le login GUI initial est obligatoire, et Wine ne le permet pas proprement.

## Setup VM Windows KVM (solution retenue)

État vérifié sur The Hive : `/dev/kvm` présent, 32 threads avec virtualisation, `kvm`, `qemu-system-x86_64`, `qemu-img`, `virt-install` installés, aucune VM existante, `/mnt/data` a 432G libres.

Plan validé avec l'utilisateur :
1. L'utilisateur dépose une ISO Windows 11 dans `~/vms/mt5/iso/` (l'agent ne peut pas la télécharger — téléchargement Microsoft bloqué côté sandbox).
2. Créer le disque : `qemu-img create -f qcow2 ~/vms/mt5/win11.qcow2 80G` (sur /mnt/data si on veut préserver /).
3. `virt-install --name win11-mt5 --ram 16384 --vcpus 8 --disk path=...,format=qcow2 --cdrom <iso> --os-variant win11 --network default --graphics spice` (ou RDP après install ; penser aux drivers VirtIO pour disque/réseau — ISO virtio-win).
4. Dans la VM : installer MT5 FTMO, Python Windows, MetaTrader5, puis exposer l'API au host Linux (socket/REST) ou partager les Parquet via virtiofs/smb.
5. Fallbacks si la VM échoue : cTrader (Open API cross-platform native), puis PC physique Windows.

Points d'attention : Windows 11 exige TPM 2.0 + Secure Boot → ajouter `--tpm backend.type=emulator,backend.version=2.0 --boot uefi` (swtpm à installer), ou contourner avec les clés de registre d'install. Windows non activé suffit pour du dev MT5.
