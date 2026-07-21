---
name: overthewire-bandit
description: Résolution automatisée des challenges OverTheWire Bandit via SSH. Du niveau 0 au niveau 34.
category: research
---

# OverTheWire Bandit — Wargame automatisé

## Connexion
- **Hôte :** `bandit.labs.overthewire.org`
- **Port :** `2220`
- **Commande :** `sshpass -p '<password>' ssh -o StrictHostKeyChecking=no bandit<N>@... -p 2220 '<cmd>'`
- **Outil requis :** `sshpass` (`sudo apt-get install -y sshpass`)

## Structure des niveaux

| Niveaux | Thème | Technique clé |
|---------|-------|---------------|
| 0-4 | Intro | `cat`, fichiers cachés, noms avec espaces, `file` |
| 5-9 | Recherche | `find`, `grep`, `sort`, `uniq`, `strings` |
| 10-12 | Encodage | `base64`, `tr (rot13)`, `xxd`, décompression chaînée |
| 13-16 | Réseau | clés SSH, `nc`, `openssl s_client`, `nmap` |
| 17-20 | Permissions | `diff`, bypass `.bashrc` (ssh -t), setuid, `suconnect` |
| 21-26 | Cron & jobs | `/etc/cron.d/`, `md5sum`, `cut`, `ps`, `more` |
| 27-30 | Git & SCM | `git clone`, `git log`, `git show`, `git branch` |
| 31-34 | Avancé | `wget`, `nc` upload, RCE, break out |

## Techniques par niveau

### Niveau 0-4 : Lecture de fichiers
```bash
# Fichier normal
cat readme

# Fichier nommé '-' (dash)
cat ./-

# Fichier avec espaces
cat "./--spaces in this filename--"
# ou
cat ./--spaces\ in\ this\ filename--

# Fichier caché (commence par .)
ls -la inhere/   # pour voir
cat inhere/...Hiding-From-You

# Fichier non-ASCII (file + grep)
file inhere/* | grep ASCII | cut -d: -f1 | xargs cat
```

### Niveau 5-9 : Recherche système
```bash
# Fichier par taille exacte
find inhere -type f -size 1033c -exec cat {} \;

# Fichier par propriétaire/groupe
find / -type f -user bandit7 -group bandit6 -size 33c 2>/dev/null -exec cat {} \;

# Grep dans un fichier
grep millionth data.txt

# Ligne unique (après sort)
sort data.txt | uniq -u

# Strings dans un binaire
strings data.txt | grep -E "=+[a-zA-Z0-9]+"
strings -n 10 data.txt | grep -E '[a-zA-Z0-9]{20,}'
```

### Niveau 10-12 : Encodage & compression
```bash
# Base64
base64 -d data.txt

# Rot13
cat data.txt | tr a-zA-Z n-za-mN-ZA-M

# Chaîne de décompression (xxd → gzip → bzip2 → tar → ...)
xxd -r data.txt > out
file out  # vérifier le type
# Boucle automatique :
while true; do
  f=$(file out | cut -d: -f2)
  case "$f" in
    *gzip*) mv out out.gz; gzip -d out.gz;;
    *bzip2*) mv out out.bz2; bzip2 -d out.bz2;;
    *tar*) mv out out.tar; tar xf out.tar; out=$(ls -t | head -1);;
    *ASCII*) cat out; break;;
    *) echo "Unknown: $f"; break;;
  esac
done
```

### Niveau 13-16 : Réseau & SSL
```bash
# Utiliser une clé SSH privée
chmod 600 key
ssh -i key bandit14@... -p 2220 'cat /etc/bandit_pass/bandit14'

# Netcat (envoi de texte)
echo "password" | nc localhost 30000

# SSL/TLS
echo "password" | openssl s_client -connect localhost:30001 -quiet

# Scan de ports
nmap -p 31000-32000 localhost

# Test SSL sur plusieurs ports
for p in 31046 31518 31691 31790 31960; do
  echo "password" | timeout 3 openssl s_client -connect localhost:$p -quiet 2>/dev/null
done
```

### Niveau 17-20 : Permissions
```bash
# Diff entre deux fichiers
diff passwords.new passwords.old

# Bypass .bashrc qui logout
ssh -t bandit18@... -p 2220 'cat ~/readme'

# Setuid binary
./bandit20-do cat /etc/bandit_pass/bandit20

# Suconnect (écouter + envoyer)
echo "password" | nc -l -p 12345 &
./suconnect 12345
```

### Niveau 21-26 : Cron & Process
```bash
# Lire cron jobs
cat /etc/cron.d/cronjob_bandit22
cat /usr/bin/cronjob_bandit22.sh

# Script cron avec md5sum
echo -n "bandit23" | md5sum | cut -d' ' -f1
# ou avec printf
printf "bandit23" | md5sum | cut -d' ' -f1
cat /tmp/$(echo -n "bandit23" | md5sum | cut -d' ' -f1)

# Examiner les processus
# (cron, at, etc.)

# More avec bypass
# Redimensionner le terminal, puis !/bin/sh
```

### Niveau 27-30 : Git
```bash
# Cloner un dépôt
git clone ssh://bandit27-git@localhost:2220/home/bandit27-git/repo /tmp/repo
# Mot de passe = mot de passe niveau actuel

# Explorer l'historique
git log --oneline
git show <hash>

# Branches
git branch -a
git show <branch>
```

### Niveau 31-34 : Avancé
```bash
# Télécharger un fichier
wget http://localhost:8080/xxx

# Upload via netcat
# (serveur qui écoute + envoi)

# RCE / break out
# via git push, scripts, etc.
```

## Pièges & erreurs fréquentes
- **Clé SSH :** Always `chmod 600` la clé, et enlever les lignes "Correct!" du début
- **Fichiers avec `-` :** Utiliser `./` devant, `cat ./--fichier--`
- **Espaces :** Quotes ou backslash escaping
- **Bypass .bashrc :** Utiliser `ssh -t` au lieu de `ssh` simple
- **Anubis (RootMe) :** Pas applicable ici — OverTheWire n'a pas d'anti-bot
- **Noms de fichiers qui changent :** Toujours faire `ls -la` d'abord pour confirmer

## Progression
- **Niveaux complétés :** 0-22 dans cette session
- **Password pour niveau 22 :** `RYVux2rHEm9tiXHmLFzuR7Vhx6AZQMEz`
- **Continuer avec :** `sshpass -p '<password>' ssh bandit<N>@bandit.labs.overthewire.org -p 2220`