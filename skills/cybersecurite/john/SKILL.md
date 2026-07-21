---
name: john
description: John the Ripper — cracking de mots de passe CPU, formats de hash, modes d'attaque (single/wordlist/incremental), règles de mutation, unshadow, zip2john, et workflows de pentest.
---

# John the Ripper — Guide Complet

## Présentation

John the Ripper (JtR) est un cracker de mots de passe open-source optimisé pour le CPU. Complémentaire à Hashcat (GPU).

**Éditions :**
- **Community** (`john`) — version open-source standard
- **Pro** (`john-pro`) — version commerciale (plus de formats)
- **Jumbo** (`john-jumbo`) — version communauté avec tous les formats

**Installation :**
```bash
sudo apt install john              # Version standard
sudo apt install john-data         # Données additionnelles
# Jumbo version
git clone https://github.com/openwall/john.git
cd john/src && ./configure && make -s clean && make -sj4
```

---

## Modes d'attaque

### Mode Single (crack simple)
```bash
# Utilise le nom d'utilisateur comme base + variations
john --single hash.txt

# Très rapide — crack les mots de passe triviaux
# ex: user "admin" → password "admin123", "Admin!", "ADMIN"
```

### Mode Dictionnaire (wordlist)
```bash
# Standard
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt

# Avec règles (mutations)
john --wordlist=rockyou.txt --rules hash.txt

# Règles spécifiques
john --wordlist=rockyou.txt --rules=best64 hash.txt
john --wordlist=rockyou.txt --rules=KoreLogicRules hash.txt
john --wordlist=rockyou.txt --rules=Jumbo hash.txt

# Multiples wordlists
john --wordlist=dict1.txt hash.txt
john --wordlist=dict2.txt hash.txt  # Continuation
```

### Mode Incremental (bruteforce)
```bash
# Toutes les combinaisons possibles
john --incremental hash.txt

# Avec un charset spécifique
john --incremental=LowerNum hash.txt    # minuscules + chiffres
john --incremental=All hash.txt         # tous les caractères

# Limiter la longueur
john --incremental --min-length=6 --max-length=8 hash.txt
```

### Mode Markow (probabiliste)
```bash
# Utilise des chaînes de Markov (plus efficace que brute-force pur)
john --markov hash.txt
```

### Mode masque (comme Hashcat)
```bash
john --mask='?l?l?l?l?l?d?d' hash.txt
john --mask='?u?l?l?l?l?d?d?d' hash.txt
# Les mêmes masques que Hashcat (?l, ?u, ?d, ?s, ?a)
```

---

## Formats de hash

### Formats courants
```bash
# Lister les formats
john --list=formats | tr ',' '\n' | grep -i nt
john --list=formats | tr ',' '\n' | grep -i md5

# Formats importants
raw-md5          # MD5 générique
raw-sha1         # SHA1 générique
raw-sha256       # SHA256 générique
nt              # NTLM (Windows)
lm              # LM hash (Windows legacy)
descrypt        # DES crypt (Unix)
bsdicrypt       # BSDi crypt
md5crypt        # MD5 crypt (/etc/shadow)
sha256crypt     # SHA256 crypt (/etc/shadow)
sha512crypt     # SHA512 crypt (/etc/shadow modernes)
bcrypt          # Blowfish (très lent)
krb5tgs         # Kerberos TGS (kerberoasting)
krb5asrep       # Kerberos AS-REP
mscash2         # MS Cache v2
```

### Spécifier le format
```bash
john --format=raw-md5 hash.txt
john --format=nt hash.txt
john --format=krb5tgs hash.txt
john --format=sha512crypt hash.txt
```

---

## Outils de conversion (2john)

```bash
# Unix passwords
unshadow /etc/passwd /etc/shadow > hashes_unshadowed.txt

# Archives ZIP
zip2john archive.zip > zip_hash.txt

# Archives RAR
rar2john archive.rar > rar_hash.txt
# RAR5
rar2john -5 archive.rar > rar5_hash.txt

# PDF
pdf2john document.pdf > pdf_hash.txt

# SSH private key
ssh2john id_rsa > ssh_hash.txt

# KeePass
keepass2john database.kdbx > keepass_hash.txt

# Office documents
d2john office.docx > office_hash.txt
office2john office.docx > office_hash.txt

# BitLocker
bitlocker2john image.dd > bitlocker_hash.txt

# TrueCrypt/VeraCrypt
truecrypt_volume2john volume.tc > tc_hash.txt

# macOS
keychain2john login.keychain > keychain_hash.txt

# Android (FDE)
androidfde2john footer.bin > android_hash.txt

# PFX/P12
pfx2john certificate.pfx > pfx_hash.txt

# Liste tous les 2john scripts
ls /usr/share/john/*2john*
ls /opt/john/run/*2john*   # Jumbo version
```

---

## Règles de mutation

### Règles intégrées
```bash
# Lister les règles
john --list=rules | head -20

# Appliquer une règle
john --wordlist=rockyou.txt --rules=best64 hash.txt
john --wordlist=rockyou.txt --rules=d3ad0ne hash.txt
john --wordlist=rockyou.txt --rules=T9X hash.txt
john --wordlist=rockyou.txt --rules=Jumbo hash.txt
```

### Syntaxe des règles
```bash
# Créer ~/.john/john.conf avec des règles custom
[List.Rules:monRule]
# Ajouter "123" à la fin
$1$2$3
# Mettre en majuscule puis ajouter "!"
c$!
# Remplacer a→4, e→3, o→0, s→5
sa4
se3
so0
ss5
# Dupliquer le mot
d
# Toggle case du premier caractère
T1
# Ajouter "2024"
$2$0$2$4
```

### Tester les règles
```bash
john --wordlist=test.txt --rules=monRule --stdout
```

---

## Gestion des sessions

### Sauvegarde et restauration
```bash
# La session est automatiquement sauvegardée dans ~/.john/john.pot
# et ~/.john/john.log

# Restaurer la session interrompue
john --restore

# Restaurer une session spécifique
john --restore=monNomDeSession

# Afficher le statut
john --status

# Nommer une session
john --session=projet1 --wordlist=rockyou.txt hash.txt
```

### Fichier POT (résultats trouvés)
```bash
john --show hash.txt           # Afficher les mots de passe trouvés
john --show --format=nt hash.txt  # Format spécifique
john --pot=/path/potfile.txt ...  # Pot file custom

# Voir les hash non crackés
john --show=left hash.txt
```

---

## Optimisation CPU

### Options de performance
```bash
# Nombre de forks (processus parallèles — CPU multicœur)
john --fork=8 hash.txt

# Limiter la mémoire
john --max-memory=2048 hash.txt

# Wordlist + fork
john --wordlist=rockyou.txt --fork=$(nproc) hash.txt
```

### Profilage
```bash
# Tester la vitesse
john --test=0
john --test --format=raw-md5

# Ajuster le mode incrémental
john --incremental --max-candidates=1000000 hash.txt
```

---

## Wordlist mangling (Loopback)

```bash
# Mode double crack : cracker avec wordlist, puis réutiliser les résultats
john --wordlist=rockyou.txt hash.txt
# Les résultats sont dans le .pot

# Puis boucler avec des règles
john --loopback --rules hash.txt
# John prend les mots déjà crackés et applique des règles
```

---

## External Mode (scripts custom)

```bash
# Créer un mode externe dans john.conf
[List.External:FilterNumbers]
void filter()
{
    int i, c;
    i = 0;
    while (c = word[i++]) {
        if (c >= '0' && c <= '9')
            return;  // Skip words with numbers
    }
}

# Utiliser le filtre
john --external=FilterNumbers hash.txt
```

---

## Unicode / Non-ASCII

```bash
# Crack avec charset UTF-8
john --encoding=utf8 hash.txt

# Avec règles spécifiques aux caractères accentués
john --wordlist=rockyou.txt --rules --encoding=utf8 hash.txt
```

---

## Scénarios de pentest

### 1. Unix /etc/shadow complet
```bash
# 1. Extraire les hashes
unshadow /etc/passwd /etc/shadow > unshadowed.txt

# 2. Crack — commencer simple
john --single unshadowed.txt

# 3. Puis wordlist
john --wordlist=rockyou.txt unshadowed.txt

# 4. Puis wordlist + rules
john --wordlist=rockyou.txt --rules unshadowed.txt

# 5. Afficher les résultats
john --show unshadowed.txt
```

### 2. Windows NTLM
```bash
# 1. Extraire via secretsdump.py ou mimikatz
impacket-secretsdump DOMAIN/user:password@192.168.1.10
# Récupérer les hash NTLM

# 2. Crack
john --format=nt --wordlist=rockyou.txt ntlm_hashes.txt

# 3. LM hash (si présent)
john --format=lm lm_hashes.txt
john --show --format=lm lm_hashes.txt
```

### 3. Kerberoasting (AD)
```bash
# 1. Récupérer les tickets TGS
impacket-GetUserSPNs DOMAIN/user:password@dc.local -outputfile kerb_hashes.txt

# 2. Crack
john --format=krb5tgs --wordlist=rockyou.txt kerb_hashes.txt

# 3. Avec rules
john --format=krb5tgs --wordlist=rockyou.txt --rules kerb_hashes.txt
```

### 4. AS-REP Roasting
```bash
# 1. AS-REP hash
impacket-GetNPUsers DOMAIN/ -dc-ip 192.168.1.10 -request -format john

# 2. Crack
john --format=krb5asrep --wordlist=rockyou.txt asrep_hashes.txt
```

### 5. Document protégé
```bash
# ZIP
zip2john document.zip > zip.hash
john --wordlist=rockyou.txt zip.hash

# PDF
pdf2john document.pdf > pdf.hash
john --wordlist=rockyou.txt pdf.hash

# KeePass
keepass2john database.kdbx > kp.hash
john --wordlist=rockyou.txt kp.hash
```

### 6. SSH Private Key
```bash
ssh2john id_rsa > ssh.hash
john --wordlist=rockyou.txt ssh.hash
john --show ssh.hash  # Affiche la passphrase trouvée
```

---

## Différences clés Hashcat vs John

| Fonctionnalité | Hashcat | John |
|---------------|---------|------|
| **Hardware** | GPU (très rapide) | CPU (optimisé) |
| **Format output** | Format spécifique | 2john scripts |
| **Rules** | Fichier .rule distinct | Config john.conf |
| **Sessions** | --session | --restore |
| **Loopback** | --loopback | --loopback |
| **Incremental** | Masque -a 3 | --incremental |
| **Unicode** | Bof | Bon support |
| **Format 2john** | Outils séparés | Intégré (jumbo) |
| **Performance NTLM** | 100 GH/s (RTX 4090) | 100 MH/s (32 cores) |
| **bcrypt** | 50 KH/s | 5 KH/s |

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "No password hashes loaded" | Vérifier le format : `--format=nt` |
| "Unknown format" | Utiliser la version Jumbo (plus de formats) |
| "Too few characters" | Réduire min-length |
| "Session expired" | `john --restore` pour reprendre |
| Décès / Ctrl+C | La session est automatiquement sauvegardée |

---

## Antisèche rapide

```bash
# Crack basique
john hash.txt

# Avec wordlist
john --wordlist=rockyou.txt hash.txt

# Wordlist + rules
john --wordlist=rockyou.txt --rules hash.txt

# Afficher les résultats
john --show hash.txt

# Extraction courante
unshadow passwd shadow > unshadowed.txt
zip2john archive.zip > hash.txt
ssh2john id_rsa > hash.txt

# Format spécifique
john --format=nt --wordlist=rockyou.txt hashes.txt

# Performance (fork)
john --fork=$(nproc) --wordlist=rockyou.txt hash.txt

# Mode incrememental (6-8 chars)
john --incremental --min-length=6 --max-length=8 hash.txt

# Boucle sur les résultats
john --loopback --rules hash.txt
```