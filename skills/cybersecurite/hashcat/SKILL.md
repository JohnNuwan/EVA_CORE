---
name: hashcat
description: Hashcat — cracking de mots de passe par GPU, modes d'attaque (dictionnaire, masque, combinatoire, hybride, rule-based), optimisation performance, formats de hash (mode -m), rules, et scénarios de pentest.
---

# Hashcat — Cracking GPU Haute Performance

## Présentation

Hashcat est le cracker de mots de passe le plus rapide au monde, utilisant le GPU pour des vitesses de cracking massives.

**Modes** :
| Mode | Description |
|------|-------------|
| `-a 0` | Dictionnaire (wordlist) |
| `-a 1` | Combinaison (wordlist1 + wordlist2) |
| `-a 3` | Masque (bruteforce avec pattern) |
| `-a 6` | Hybride dictionnaire + masque |
| `-a 7` | Hybride masque + dictionnaire |

---

## Installation

```bash
# Kali/Ubuntu
sudo apt install hashcat

# Dernière version
git clone https://github.com/hashcat/hashcat.git
cd hashcat && make && sudo make install

# Drivers GPU
# NVIDIA : sudo apt install nvidia-driver nvidia-cuda-toolkit
# AMD : sudo apt install rocm-opencl-runtime
```

---

## Modes d'attaque détaillés

### Attaque par dictionnaire `-a 0`
```bash
# Basique
hashcat -m 1000 -a 0 hash.txt /usr/share/wordlists/rockyou.txt

# Avec rules
hashcat -m 1000 -a 0 hash.txt rockyou.txt -r /usr/share/hashcat/rules/best64.rule

# Multirules
hashcat -m 1000 -a 0 hash.txt rockyou.txt \
    -r /usr/share/hashcat/rules/best64.rule \
    -r /usr/share/hashcat/rules/d3ad0ne.rule \
    -r /usr/share/hashcat/rules/rockyou-30000.rule
```

### Attaque par combinaison `-a 1`
```bash
# Combine chaque ligne de dict1 avec chaque ligne de dict2
hashcat -m 1000 -a 1 hash.txt dict1.txt dict2.txt

# Combinaison à gauche (prefix)
hashcat -m 1000 -a 1 hash.txt prefix.txt common-passwords.txt

# Combinaison à droite (suffix)
hashcat -m 1000 -a 1 hash.txt common-passwords.txt suffix.txt
```

### Attaque par masque `-a 3`
```bash
# Masques prédéfinis
# ?l = minuscule (a-z)
# ?u = majuscule (A-Z)
# ?d = chiffre (0-9)
# ?s = spécial (!@#$%^&*)
# ?a = tous (?l?u?d?s)
# ?b = octet brut (0x00-0xff)
# ?h = hex minuscule (0-9, a-f)
# ?H = hex majuscule (0-9, A-F)

# Bruteforce : 8 chiffres
hashcat -m 1000 -a 3 hash.txt ?d?d?d?d?d?d?d?d

# Bruteforce : 8 lettres minuscules
hashcat -m 1000 -a 3 hash.txt ?l?l?l?l?l?l?l?l

# Mot de passe 6-10 caractères alphanumériques
hashcat -m 1000 -a 3 hash.txt ?a?a?a?a?a?a?a?a?a?a --increment \
    --increment-min 6 --increment-max 10

# Pattern spécifique : Maj+3digits+spécial
hashcat -m 1000 -a 3 hash.txt ?u?d?d?d?s

# Pattern : Mot + 2 chiffres (ex: password12)
hashcat -m 1000 -a 3 hash.txt ?l?l?l?l?l?l?l?l?d?d

# Masques personnalisés (fichier .hcmask)
hashcat -m 1000 -a 3 hash.txt masks/corporate.hcmask
```

### Attaque hybride `-a 6` (wordlist + mask)
```bash
# Mot de wordlist + suffixe de 3 chiffres
hashcat -m 1000 -a 6 hash.txt rockyou.txt ?d?d?d
# Teste : password000, password001, ... password999

# Mot de wordlist + 2 spéciaux
hashcat -m 1000 -a 6 hash.txt rockyou.txt ?s?s
```

### Attaque hybride `-a 7` (mask + wordlist)
```bash
# Prefixe de 2 majuscules + mot de wordlist
hashcat -m 1000 -a 7 hash.txt ?u?u rockyou.txt
# Teste : AApassword, ABpassword, ... ZZpassword
```

---

## Types de hash (modes) — Les plus importants

### Unix/Linux
```
500      md5crypt, MD5 (Unix)           👑 /etc/shadow
3200     bcrypt, Blowfish               👑 /etc/shadow
1800     sha512crypt                    👑 /etc/shadow (moderne)
7400     sha256crypt                    👑 /etc/shadow
1600     Apache $apr1$ MD5
1411     SSHA-256 (OpenLDAP)
```

### Windows
```
1000     NTLM                           👑 Windows NT
3000     LM                             👑 Windows legacy
5500     NetNTLMv1                      👑 Réseau Windows
5600     NetNTLMv2                      👑 Réseau Windows
2100     Domain Cached Credentials (MSCache)
12100    DCC2 (MS Cache v2)
```

### Web / Application
```
0        MD5                            👑 Général
10       md5($pass.$salt)
20       md5($salt.$pass)
100      SHA1
110      sha1($pass.$salt)
120      sha1($salt.$pass)
1400     SHA256
1410     sha256($pass.$salt)
1700     SHA512
1710     sha512($pass.$salt)
25600    bcrypt(md5($pass))
```

### Database
```
200      MySQL323
300      MySQL4.1/MySQL5
400      MySQL challenge-response
8000     Sybase ASE
3100     Oracle H: Type (Oracle 7+)
112      Oracle S: Type (Oracle 11+)
8500     IBM DB2
```

### Active Directory / Kerberos
```
7500     Kerberos 5 AS-REP etype 23    👑 AS-REP roasting
13100    Kerberos 5 TGS-REP etype 23   👑 Kerberoasting
19600    Kerberos 5 TGS-REP etype 17   (AES128)
19700    Kerberos 5 TGS-REP etype 18   (AES256)
18200    Kerberos 5 AS-REP etype 23    (AS-REP)
11100    BitLocker
```

### WiFi
```
22000    WPA-PBKDF2-PMKID+EAPOL        👑 WPA/WPA2/WPA3
2500     WPA/WPA2 (hccapx)
16800    WPA-PMKID-PBKDF2 (PMKID)
```

### Documents
```
11600    7-Zip
12500    RAR3-hp (RAR5)
13000    RAR5
13600    WinZip
13200    AxCrypt
13711    VeraCrypt
11700    GOST R 34.11-2012 (Streebog)
17220    PKZIP
```

### Other
```
10700    PDF (PDF 1.4-1.6)
10400    PDF (PDF 1.1-1.3)
10500    PDF (PDF 1.7)
9600     Office 2010
9400     Office 2007
9500     MS Office 2013
9700     MS Office ⇐ 2003
9800     MS Office ⇐ 2011 (Mac)
6800     LastPass
8800     Android FDE
11300    Bitcoin/Litecoin wallet.dat
15200    Blockchain, My Wallet
```

---

## Rules (transformations de mots de passe)

### Règles intégrées
```bash
# Lister les règles disponibles
ls /usr/share/hashcat/rules/

# Règles courantes
best64.rule             # Top 64 règles les plus efficaces
rockyou-30000.rule      # 30000 règles (exhaustif)
d3ad0ne.rule            # Règles de d3ad0ne (populaire)
toggles1.rule / toggles2.rule / toggles3.rule / toggles4.rule / toggles5.rule
leetspeak.rule          # Leet speak (1337)
InsidePro-HashMaster.rule
```

### Appliquer des règles
```bash
# Single rule
hashcat -m 1000 -a 0 hash.txt rockyou.txt -r best64.rule

# Multiple rules (concaténation)
hashcat -m 1000 -a 0 hash.txt rockyou.txt \
    -r best64.rule -r d3ad0ne.rule -r rockyou-30000.rule

# Générer les candidates (vérifier les règles)
hashcat --stdout -a 0 rockyou.txt -r best64.rule | head -20
```

### Créer ses propres règles
```bash
# Syntaxe des règles :
$   Ajouter à la fin
^   Ajouter au début
s   Substitution (s/old/new/)
l   Tout en minuscule
u   Tout en majuscule
c   Première lettre en majuscule
r   Inverser
d   Dupliquer
{   Décaler à gauche
}   Décaler à droite
T   Toggle case (T3 = toggle les 3 premiers chars)
DN  Ajouter N chiffres au début (D3 = ajouter 3 chiffres)
[   Supprimer premier char
]   Supprimer dernier char

# Exemple : mon-super-rule.rule
# Ajouter 2 chiffres à la fin
$0$1
$1$2
$2$3
# Ajouter 1 spécial à la fin
$!$@$#
# Remplacer a→4, e→3, o→0
sa4
se3
so0
# Mettre en capitale + 2024
c$2$0$2$4
```

### Debug des rules
```bash
# Voir l'effet d'une règle sur un mot
echo "password" | hashcat --stdout -r best64.rule
# Sortie : Password, PASSWORD, password1, password!, password123, ...
```

---

## Optimisation des performances

### Informations GPU
```bash
hashcat -I                            # Devices disponibles
hashcat -I --backend-devices          # Détail
```

### Workload profile
```bash
-w 1  # Faible (conserver le desktop utilisable)
-w 2  # Normal
-w 3  # Agressif (GPU à fond)
-w 4  # Insane (tout le GPU, peut freeze l'écran)
```

### Optimisation par type de hash
```bash
# NTLM (très rapide : 100GH/s+ sur RTX 4090)
hashcat -m 1000 -a 0 -w 3 hash.txt rockyou.txt -O

# bcrypt (très lent : 50KH/s max — optimizer peu utile)
hashcat -m 3200 -a 3 -w 3 hash.txt ?l?l?l?l?l?l?l?l

# SHA512 (moyen : 1GH/s)
hashcat -m 1700 -a 0 -w 3 hash.txt rockyou.txt -O
```

### Options d'optimisation
```bash
-O     # Optimisation du noyau (réduit la mémoire utilisée)
-w 4   # Workload profile max
--force    # Forcer l'exécution (même avec drivers legacy)
--status   # Afficher le statut en temps réel
--status-timer 1   # Rafraîchir le statut toutes les 1s
--potfile-disable  # Désactiver le fichier pot (pas de cache)
--backend-devices 1,2  # Utiliser des GPUs spécifiques
--opencl-device-types GPU  # GPU seulement
--self-test-disable  # Skip self test (gagne du temps)
```

### Multi-GPU
```bash
# Utiliser tous les GPUs
hashcat -m 1000 -a 0 hash.txt rockyou.txt -d 1,2,3,4

# Segmenter le hashlist sur N GPUs
hashcat -m 1000 -a 0 hash.txt rockyou.txt -S

# Multi-GPU segmenté
hashcat -m 1000 -a 0 hash.txt -S rockyou.txt -d 1,2
```

---

## Mode show / left

```bash
# Afficher les mots de passe trouvés
hashcat -m 1000 --show hash.txt

# Afficher les hashes non crackés
hashcat -m 1000 --left hash.txt

# Formater la sortie
hashcat -m 1000 --show hash.txt --username | cut -d: -f2-
```

---

## Fichier Pot (cache)

```bash
# Emplacement du potfile
~/.local/share/hashcat/hashcat.potfile

# Désactiver le pot
hashcat --potfile-disable ...

# Utiliser un potfile personnalisé
hashcat --potfile-path /tmp/custom.pot ...

# Voir le contenu
cat ~/.local/share/hashcat/hashcat.potfile | sort -u
```

---

## Outils de conversion

### Préparation des hashes
```bash
# /etc/shadow → hashcat
unshadow /etc/passwd /etc/shadow > unshadowed.txt
# Format : username:hash:uid:gid:gecos:home:shell

# NTLM depuis SAM (avec secretsdump.py)
impacket-secretsdump -hashes aad3b435b51404eeaad3b435b51404ee:hash DOMAIN/user@target
# Récupérer les hash NTLM

# Kerberos
impacket-GetNPUsers -request DOMAIN/ -dc-ip 192.168.1.10 -format hashcat

# WiFi PMKID
hcxpcapngtool -o hash.22000 capture.pcapng

# ZIP
zip2john archive.zip | cut -d: -f2- > zip.hash

# RAR
rar2john archive.rar | cut -d: -f2- > rar.hash

# PDF
pdf2john document.pdf > pdf.hash

# KeePass
keepass2john database.kdbx > keepass.hash
```

### Script de formatage
```bash
# hash_extract.py : extraire les hashes dans le bon format
cat hash.txt | awk -F: '{print $NF}' > clean_hashes.txt
```

---

## Création de wordlists

### Avec Hashcat-utils
```bash
# Rle processor (expressions régulières)
rli rockyou.txt     # Lire la wordlist
rep -c "e" ...      # Compter les occurences

# Combinator
combinator dict1.txt dict2.txt > combined.txt
combinator3 dict1.txt dict2.txt dict3.txt > triple.txt
```

### Avec Kernel/Generator
```bash
# Créer une wordlist basée sur un fichier PDF (mots-clés)
pdftotext document.pdf - | tr ' ' '\n' | sort -u > custom_words.txt

# Basée sur les informations de la cible
cat > target_dict.txt << EOF
Company2024
Company123
Company@2024
Paris2024
Summer2024
Winter2024
Admin2024
EOF
```

---

## Attaque par boucle d'itération

```bash
# Boucle sur plusieurs wordlists
for wl in /usr/share/wordlists/*.txt; do
    echo "=== $wl ==="
    hashcat -m 1000 -a 0 hash.txt "$wl"
done

# Itération sur différentes règles
hashcat -m 1000 -a 0 hash.txt rockyou.txt \
    -r best64.rule \
    -r d3ad0ne.rule \
    -r rockyou-30000.rule \
    --loopback
```

---

## Scénarios de pentest

### 1. NTLM (Windows) — Rapide
```bash
# Hashcat -w 3 -O pour la vitesse
hashcat -m 1000 -a 0 -w 3 -O hash_ntlm.txt rockyou.txt

# Puis with rules
hashcat -m 1000 -a 0 -w 3 -O hash_ntlm.txt rockyou.txt \
    -r best64.rule

# Puis masque (8 chiffres)
hashcat -m 1000 -a 3 -w 3 -O hash_ntlm.txt ?d?d?d?d?d?d?d?d
```

### 2. Kerberoasting (TGS hash)
```bash
# Mode 13100 (Kerberos 5 TGS-REP)
hashcat -m 13100 -a 0 kerberos.txt rockyou.txt -r best64.rule

# Puis increment + rules
hashcat -m 13100 -a 0 kerberos.txt rockyou.txt \
    -r best64.rule -r d3ad0ne.rule
```

### 3. /etc/shadow (SHA-512)
```bash
# Mode 1800
hashcat -m 1800 -a 0 shadow.txt rockyou.txt
# SHA-512 est lent (~500KH/s) — prioriser les modes rapides d'abord
```

### 4. WiFi WPA/WPA2
```bash
# Mode 22000
hashcat -m 22000 -a 0 wifi_hash.txt rockyou.txt

# Rules
hashcat -m 22000 -a 0 wifi_hash.txt rockyou.txt -r best64.rule

# Masque (8 caractères hex)
hashcat -m 22000 -a 3 wifi_hash.txt ?h?h?h?h?h?h?h?h
```

### 5. bcrypt — Stratégie spéciale
```bash
# bcrypt est très lent (~50KH/s sur RTX 4090)
# Prioriser les attaques les plus probables

hashcat -m 3200 -a 3 bcrypt.txt ?l?l?l?l?l?l?l?l --increment \
    --increment-min 6 --increment-max 8

# Combinaison rule-based seulement
hashcat -m 3200 -a 0 bcrypt.txt rockyou.txt -r best64.rule
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "CL_OUT_OF_RESOURCES" | Réduire le workload `-w 2` |
| "Hash-mode not found" | Vérifier le mode `-m` |
| "No devices found" | Vérifier les drivers GPU `hashcat -I` |
| "Token length exception" | Vérifier le format du hash |
| "Line-length exception" | Hash trop long → vérifier l'extraction |
| Skip hash (excluded) | Dans potfile déjà, utiliser `--show` |
| "Integer overflow" | Trop de candidates → segmenter la wordlist |

---

## Antisèche rapide

```bash
# Dictionnaire simple
hashcat -m 1000 -a 0 hash.txt rockyou.txt

# Dictionnaire + rules
hashcat -m 1000 -a 0 hash.txt rockyou.txt -r best64.rule

# Combinaison
hashcat -m 1000 -a 1 hash.txt dict1.txt dict2.txt

# Masque (8 chiffres)
hashcat -m 1000 -a 3 hash.txt ?d?d?d?d?d?d?d?d

# Hybride (wordlist + 3 chiffres)
hashcat -m 1000 -a 6 hash.txt rockyou.txt ?d?d?d

# Show cracked
hashcat -m 1000 --show hash.txt

# Voir les devices
hashcat -I

# Avec optimisation GPU
hashcat -m 1000 -a 0 hash.txt rockyou.txt -w 3 -O

# Multi-rule
hashcat -m 1000 -a 0 hash.txt rockyou.txt \
    -r best64.rule -r d3ad0ne.rule -r rockyou-30000.rule

# Masque avec increment
hashcat -m 1000 -a 3 hash.txt ?a?a?a?a?a?a?a?a \
    --increment --increment-min 6 --increment-max 8
```