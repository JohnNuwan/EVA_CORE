---
name: cryptographie
description: Guide complet de cryptographie pratique — OpenSSL, GnuPG, age, VeraCrypt, chiffrement symétrique/asymétrique, hachage, PKI, certificats, et cracking.
---

# Cryptographie Pratique — Guide Complet

---

## 1. Hachage

```bash
# Calculer des hashs
md5sum fichier
sha1sum fichier
sha256sum fichier
sha512sum fichier

# HMAC (Hash-based Message Authentication Code)
echo -n "message" | openssl dgst -sha256 -hmac "clé_secrète"

# Comparer des hashs
sha256sum -c checksums.txt

# Générer un sel aléatoire
openssl rand -hex 16
```

---

## 2. OpenSSL — Chiffrement symétrique

```bash
# Chiffrer un fichier (AES-256-CBC)
openssl enc -aes-256-cbc -salt -in fichier.txt -out fichier.enc
# → demande un mot de passe

# Déchiffrer
openssl enc -aes-256-cbc -d -in fichier.enc -out fichier.txt

# Avec mot de passe en argument (base64)
echo -n "secret" | openssl enc -aes-256-cbc -a -pbkdf2 -pass pass:motdepasse

# Chiffrement rapide avec clé hex
openssl enc -aes-256-ctr -K $(openssl rand -hex 32) -iv $(openssl rand -hex 16) \
  -in fichier -out fichier.enc

# Encodage base64
openssl base64 -in fichier.bin -out fichier.b64
openssl base64 -d -in fichier.b64 -out fichier.bin
```

## 3. OpenSSL — Chiffrement asymétrique (RSA)

```bash
# Générer une clé privée RSA 4096 bits
openssl genrsa -out private.pem 4096

# Extraire la clé publique
openssl rsa -in private.pem -pubout -out public.pem

# Chiffrer avec la clé publique
openssl rsautl -encrypt -pubin -inkey public.pem -in fichier.txt -out fichier.enc

# Déchiffrer avec la clé privée
openssl rsautl -decrypt -inkey private.pem -in fichier.enc -out fichier.txt

# Chiffrement moderne (RSA-OAEP avec padding)
openssl pkeyutl -encrypt -pubin -inkey public.pem \
  -pkeyopt rsa_padding_mode:oaep -pkeyopt rsa_oaep_md:sha256 \
  -in fichier.txt -out fichier.enc
```

---

## 4. GnuPG (GPG) — Chiffrement PGP

```bash
# Générer une paire de clés
gpg --full-generate-key

# Lister les clés
gpg --list-keys
gpg --list-secret-keys

# Chiffrer pour un destinataire
gpg --encrypt --recipient destinataire@email.com fichier.txt
# → fichier.txt.gpg

# Chiffrer symétrique (mot de passe)
gpg --symmetric --cipher-algo AES256 fichier.txt

# Déchiffrer
gpg --decrypt fichier.txt.gpg > fichier.txt

# Signer un fichier
gpg --sign fichier.txt

# Vérifier une signature
gpg --verify fichier.txt.sig

# Exporter une clé publique
gpg --export -a "Nom" > ma_cle_publique.asc

# Importer une clé
gpg --import cle.asc
```

---

## 5. age — Chiffrement moderne simple

```bash
# Installer
go install filippo.io/age/cmd/...@latest

# Générer une clé
age-keygen -o key.txt

# Chiffrer avec une clé publique
age -r age1... -o fichier.age fichier.txt

# Déchiffrer
age -d -i key.txt -o fichier.txt fichier.age

# Chiffrer avec mot de passe
age -p -o fichier.age fichier.txt
```

---

## 6. VeraCrypt — Chiffrement de volumes

```bash
# Créer un volume chiffré
veracrypt -c volume.tc

# Monter un volume
veracrypt volume.tc /mnt/point

# Démonter
veracrypt -d /mnt/point

# Créer un conteneur fichier (taille en MB)
veracrypt -c --size 100M --password motdepasse conteneur.tc
```

---

## 7. Certificats SSL/TLS

```bash
# Afficher le certificat d'un site
openssl s_client -connect exemple.com:443 -servername exemple.com </dev/null 2>/dev/null | openssl x509 -text -noout

# Extraire le common name
openssl s_client -connect exemple.com:443 2>/dev/null | openssl x509 -noout -subject

# Vérifier la date d'expiration
openssl s_client -connect exemple.com:443 2>/dev/null | openssl x509 -noout -enddate

# Générer un certificat auto-signé
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

---

## 8. Cracking de protections

```bash
# ZIP protégé
zip2john archive.zip > zip.hash
john zip.hash --wordlist=rockyou.txt

# RAR protégé
rar2john archive.rar > rar.hash
john rar.hash --wordlist=rockyou.txt

# PDF protégé
pdf2john document.pdf > pdf.hash
john pdf.hash --wordlist=rockyou.txt

# VeraCrypt / TrueCrypt
# Extraire le hash des 512 premiers octets
dd if=volume.tc of=hash bs=1 count=512
hashcat -m 13721 hash rockyou.txt   # VeraCrypt
hashcat -m 6211 hash rockyou.txt    # TrueCrypt

# GPG protégé
gpg2john private.asc > gpg.hash
john gpg.hash --wordlist=rockyou.txt

# SSH protégé
ssh2john id_rsa > ssh.hash
john ssh.hash --wordlist=rockyou.txt
```

---

## Cheatsheet rapide

```bash
# Hachage
sha256sum fichier

# Chiffrer AES
openssl enc -aes-256-cbc -salt -in f.txt -out f.enc

# Déchiffrer AES
openssl enc -aes-256-cbc -d -in f.enc -out f.txt

# Chiffrer GPG (destinataire)
gpg --encrypt --recipient x@y.com f.txt

# Déchiffrer GPG
gpg --decrypt f.txt.gpg

# Chiffrer age (moderne)
age -r age1... -o f.age f.txt

# Cracker ZIP/RAR/PDF
zip2john f.zip | john --wordlist=rockyou.txt
```
