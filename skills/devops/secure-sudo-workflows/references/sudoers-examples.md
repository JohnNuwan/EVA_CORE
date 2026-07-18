# Exemples de configuration Sudoers

Fichier : `/etc/sudoers` (éditer avec `sudo visudo`)

## Syntaxe de base

```
utilisateur ALL=(ALL:ALL) ALL                    # Tous les droits, avec mot de passe
utilisateur ALL=(ALL) NOPASSWD: ALL              # Tous les droits, sans mot de passe
utilisateur ALL=(ALL) NOPASSWD: /chemin/commande # Commande spécifique sans mot de passe
```

## Exemples pratiques

### 1. Gestion Docker sans sudo

```
# Autoriser l'utilisateur à gérer Docker
aza ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose

# Ou mieux : ajouter au groupe docker (pas besoin de sudoers)
# sudo usermod -aG docker aza
```

### 2. Gestion des services systemd

```
# Autoriser start/stop de services spécifiques
aza ALL=(ALL) NOPASSWD: /bin/systemctl start vllm-small, /bin/systemctl stop vllm-small, /bin/systemctl restart vllm-small
```

### 3. Montage de disques

```
# Autoriser le montage de partitions spécifiques
aza ALL=(ALL) NOPASSWD: /bin/mount /dev/sda1, /bin/mount /dev/sda2, /bin/umount /dev/sda1, /bin/umount /dev/sda2

# Ou avec des options spécifiques
aza ALL=(ALL) NOPASSWD: /bin/mount -t ntfs-3g -o ro /dev/sda1 /mnt/win_c
```

### 4. Gestion des paquets (limitée)

```
# Autoriser apt update et install seulement
aza ALL=(ALL) NOPASSWD: /usr/bin/apt update, /usr/bin/apt install -y *

# Plus restrictif : liste blanche de paquets
aza ALL=(ALL) NOPASSWD: /usr/bin/apt install -y wine64, /usr/bin/apt install -y wine32:i386
```

### 5. Gestion des processus GPU

```
# Autoriser kill des processus utilisateur
aza ALL=(ALL) NOPASSWD: /bin/kill, /usr/bin/pkill

# Ou plus spécifique
aza ALL=(ALL) NOPASSWD: /usr/bin/pkill -f terminal64, /usr/bin/pkill Xvfb
```

### 6. Exécution de scripts spécifiques

```
# Autoriser des scripts dans un répertoire spécifique
aza ALL=(ALL) NOPASSWD: /home/aza/scripts/*.sh

# Avec vérification que c'est bien l'utilisateur qui les a créés
aza ALL=(ALL) NOPASSWD: /home/aza/scripts/install_mt5.sh, /home/aza/scripts/setup_gpu.sh
```

## Bonnes pratiques

### 1. Principe du moindre privilège

N'accorder que les permissions nécessaires :

```
# MAUVAIS : trop permissif
aza ALL=(ALL) NOPASSWD: ALL

# BON : limité aux commandes nécessaires
aza ALL=(ALL) NOPASSWD: /usr/bin/apt update, /usr/bin/apt install -y *, /usr/bin/docker *
```

### 2. Utiliser des alias pour grouper

```
# Définir des alias
Cmnd_Alias DOCKER_CMDS = /usr/bin/docker, /usr/bin/docker-compose, /usr/bin/docker-machine
Cmnd_Alias GPU_CMDS = /usr/bin/nvidia-smi, /usr/bin/pkill -f python, /usr/bin/pkill -f terminal64

# Utiliser les alias
aza ALL=(ALL) NOPASSWD: DOCKER_CMDS, GPU_CMDS
```

### 3. Restreindre par répertoire

```
# Autoriser seulement dans certains répertoires
aza ALL=(ALL) NOPASSWD: /bin/mount /dev/sd[ab][0-9] /mnt/*
```

### 4. Logging des commandes sudo

```
# Activer le logging détaillé
Defaults logfile="/var/log/sudo.log"
Defaults log_input, log_output
```

## Vérification de la configuration

```bash
# Vérifier la syntaxe sudoers
sudo visudo -c

# Voir les permissions de l'utilisateur actuel
sudo -l

# Tester une commande spécifique
sudo -l /usr/bin/docker ps
```

## Dépannage

### "Sorry, user aza is not allowed to execute..."

**Cause** : La commande n'est pas dans sudoers ou le chemin est incorrect.

**Solution** :
```bash
# Trouver le chemin complet
which docker
# /usr/bin/docker

# Vérifier sudoers
sudo visudo
# Ajouter le chemin complet
```

### "sudo: no tty present and no askpass program specified"

**Cause** : sudo essaie de demander un mot de passe mais il n'y a pas de terminal.

**Solution** : Utiliser NOPASSWD ou `-A` (askpass) :
```bash
# Dans un script
sudo -A apt update

# Ou avec NOPASSWD dans sudoers
aza ALL=(ALL) NOPASSWD: /usr/bin/apt
```
