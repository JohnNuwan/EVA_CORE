---
name: ldapdomaindump
description: LDAPDomainDump — dump des informations Active Directory via LDAP (utilisateurs, groupes, ordinateurs, GPO, confiance, politiques de mot de passe, DNS), scripts d'analyse post-dump, et workflow de reconnaissance AD complet.
---

# LDAPDomainDump — Énumération Active Directory par LDAP

## Présentation

LDAPDomainDump est un outil qui interroge l'annuaire Active Directory via LDAP pour extraire toutes les informations du domaine : utilisateurs, groupes, ordinateurs, GPO, policies, et relations de confiance.

**Installation :**
```bash
# Kali
sudo apt install ldapdomaindump

# Dernière version
git clone https://github.com/dirkjanm/ldapdomaindump.git
cd ldapdomaindump && pip3 install .
```

---

## Connexion de base

### Avec mot de passe
```bash
# Simple — dump complet
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' 192.168.1.10

# Domaine + DC
ldapdomaindump -u 'DOMAIN\\Administrator' -p 'Password123' dc01.example.com

# Avec un dossier de sortie
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' -o /tmp/domain_dump/ 192.168.1.10
```

### Pass-the-Hash (NTLM)
```bash
ldapdomaindump -u 'DOMAIN\user' -p '' -hashes :NTHASH 192.168.1.10
```

### Avec authentification Kerberos
```bash
# Obtenir un TGT
impacket-getTGT DOMAIN/user:Password123

# Utiliser le ticket
export KRB5CCNAME=/path/to/user.ccache
ldapdomaindump -k -u 'DOMAIN\user' dc01.example.com
```

### Connexion LDAP simple (SSL)
```bash
# LDAP simple port 389
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' ldap://192.168.1.10

# LDAPS (LDAP SSL port 636)
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' ldaps://192.168.1.10
```

---

## Fichiers générés

```bash
# Tous les fichiers HTML
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' -o /tmp/domain_dump/ 192.168.1.10

# Fichiers produits :
/tmp/domain_dump/
├── domain_users.html        # Utilisateurs (tableau HTML)
├── domain_users_by_group.html  # Users par groupe
├── domain_computers.html    # Ordinateurs
├── domain_groups.html       # Groupes
├── domain_trusts.html       # Confiances de domaine
├── domain_policy.html       # Politiques (password, lockout, etc.)
├── domain_dns.html          # DNS (si activé)
├── domain_forest_trusts.html # Confiances de forêt

# Fichiers JSON (machine-readable)
├── domain_users.json
├── domain_computers.json
├── domain_groups.json
├── domain_trusts.json
├── domain_policy.json
├── domain_dns.json

# Fichiers grep
├── domain_users.grep
├── domain_computers.grep
├── domain_groups.grep
```

---

## Analyse des fichiers HTML

### Utilisateurs (`domain_users.html`)
```bash
# Colonnes :
#   - username (sAMAccountName)
#   - displayname
#   - description (parfois contient des mots de passe !)
#   - title
#   - department
#   - email
#   - enabled (True/False)
#   - locked (True/False)
#   - pwdlastset (date)
#   - lastlogon
#   - memberof (groupes)
#   - admincount (True si membre de groupes protégés)
#   - badpwdcount
#   - useraccountcontrol (flags)

# Points d'intérêt :
#   - Utilisateurs avec description non vide (souvent contient des mots de passe)
#   - Dernière connexion (comptes inactifs → takeover possible)
#   - admincount = False mais membre de groupes sensibles
```

### Groupes (`domain_groups.html`)
```bash
# Colonnes :
#   - groupname
#   - type (Global, Domain Local, Universal)
#   - membercount
#   - members (liste)
#   - description
#   - admincount (True = groupe protégé)

# Points d'intérêt :
#   - Groupes avec "protection contre suppression" (admincount)
#   - Groupes avec des noms suspects (svc_, service_, admin_, backup_)
```

### Ordinateurs (`domain_computers.html`)
```bash
# Colonnes :
#   - computername
#   - operatingsystem
#   - enabled
#   - lastlogon
#   - pwdlastset
#   - memberof

# Points d'intérêt :
#   - OS non supportés (Windows 7, Server 2008, etc.)
#   - Machines inactives
#   - Computer accounts avec des groupes inhabituels
```

### Politiques (`domain_policy.html`)
```bash
# Informations :
#   - Password policy : min length, complexity, history, age
#   - Account lockout : threshold, duration, observation window
#   - Kerberos policy : max lifetime, renewal, clock skew

# Interprétation :
#   - Password length < 8 = très faible
#   - Pas de complexity = wordlist viable
#   - Lockout threshold élevé = brute-force possible
```

### Relations de confiance (`domain_trusts.html`)
```bash
# Informations :
#   - Trusted domain name
#   - Trust direction (inbound, outbound, bidirectional)
#   - Trust type (external, forest, realm)
#   - Trust attributes

# Points d'intérêt :
#   - Parent-child relationships
#   - Bidirectional trusts → attaque possible
#   - SID Filtering désactivé (SIDHistory attack)
```

---

## Analyse avancée

### Extraction des descriptions (mots de passe potentiels)
```bash
# Les administrateurs mettent parfois des mots de passe dans la description
cat /tmp/domain_dump/domain_users.json | jq '.[] | select(.description != "") | {username, description}'
```

### Utilisateurs inactifs (takeover possible)
```bash
# Comptes avec lastlogon > 90 jours
cat /tmp/domain_dump/domain_users.json | jq '.[] | select(.lastlogon != "" and .enabled == true)'
```

### OS non supportés
```bash
cat /tmp/domain_dump/domain_computers.json | jq '.[] | select(.operatingsystem | contains("Windows 7") or contains("Server 2008") or contains("Windows XP"))'
```

### Analyse DNS
```bash
cat /tmp/domain_dump/domain_dns.json | jq '.[] | select(.type == "A") | {name, data}'
```

---

## LDAPDomainDump pour pentest AD

### Workflow typique
```bash
# 1. Dump complet
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' -o dump/ 192.168.1.10

# 2. Identifier les comptes Kerberoastable
grep -i "serviceprincipalname" dump/domain_users.html | head -20

# 3. Identifier les comptes AS-REP Roastable
grep -i "dontreqpreauth\|does not require" dump/domain_users.html

# 4. Vérifier la politique de mot de passe
xdg-open dump/domain_policy.html  # Ouvrir dans le navigateur

# 5. Voir les groupes sensibles
xdg-open dump/domain_groups.html
```

### Combinaison avec d'autres outils
```bash
# 1. Dump LDAP
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' -o dump/ 192.168.1.10

# 2. Kerberoasting
impacket-GetUserSPNs 'DOMAIN/user:Password123' -outputfile kerb_hashes.txt

# 3. AS-REP Roasting
impacket-GetNPUsers 'DOMAIN/' -dc-ip 192.168.1.10 -usersfile dump/domain_users.grep

# 4. Importer dans BloodHound
bloodhound-python -c All -u 'DOMAIN\user' -p 'Password123' \
    -dc DC01 -ns 192.168.1.10 -d domain.local
```

---

## Scripts d'analyse post-dump

```bash
#!/bin/bash
# analyze_dump.sh — Analyse du dump LDAP

DUMP_DIR="${1:-/tmp/domain_dump}"

echo "=== Analyse LDAPDomainDump ==="
echo ""

# Utilisateurs inactifs
echo "=== Utilisateurs inactifs (>90 jours) ==="
cat $DUMP_DIR/domain_users.json | jq -r '.[] | select(.lastlogon != "" and .enabled == true) | .username' | head -20

# Descriptions non vides
echo ""
echo "=== Utilisateurs avec description (mots de passe?) ==="
cat $DUMP_DIR/domain_users.json | jq -r '.[] | select(.description != "") | "\(.username): \(.description)"'

# OS non supportés
echo ""
echo "=== OS non supportés ==="
cat $DUMP_DIR/domain_computers.json | jq -r '.[] | select(.operatingsystem | contains("7") or contains("2008") or contains("XP")) | "\(.computername): \(.operatingsystem)"'

# Groupes avec beaucoup de membres
echo ""
echo "=== Top 10 groupes les plus grands ==="
cat $DUMP_DIR/domain_groups.json | jq -r '.[] | "\(.groupname): \(.membercount)"' | sort -t: -k2 -rn | head -10

# Politique de mot de passe
echo ""
echo "=== Politique de mot de passe ==="
cat $DUMP_DIR/domain_policy.json | jq -r '.'
```

---

## LDAPDomainDump sans credentials

```bash
# Si le DC autorise les requêtes LDAP anonymes
ldapdomaindump -u '' -p '' 192.168.1.10

# Avec un bind username seulement (sans password)
ldapdomaindump -u 'DOMAIN\guest' -p '' 192.168.1.10
```

---

## Analyse JSON avec jq

```bash
# Tous les noms d'utilisateur
cat domain_users.json | jq -r '.[].username'

# Utilisateurs actifs seulement
cat domain_users.json | jq -r '.[] | select(.enabled == true) | .username'

# Utilisateurs admin (admincount)
cat domain_users.json | jq -r '.[] | select(.admincount == true) | .username'

# Groupes de domaine
cat domain_groups.json | jq -r '.[].groupname'

# Ordinateurs par OS
cat domain_computers.json | jq -r '.[] | "\(.computername): \(.operatingsystem)"'

# Compter les utilisateurs
cat domain_users.json | jq 'length'

# Compter les ordinateurs
cat domain_computers.json | jq 'length'

# Compter les groupes
cat domain_groups.json | jq 'length'
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| "LDAP bind failed" | Vérifier credentials, protocole (LDAP vs LDAPS) |
| Pas de données DNS | DNS dans AD non configuré |
| Fichiers vides | Vérifier la connexion LDAP, les droits |
| HTML cassé | Vérifier que les fichiers JSON sont bien générés |
| Connexion refusée | Vérifier port 389 (LDAP) sur le DC |

---

## Antisèche rapide

```bash
# Dump complet
ldapdomaindump -u 'DOMAIN\user' -p 'Password123' -o /tmp/dump/ 192.168.1.10

# Analyser
xdg-open /tmp/dump/domain_users.html
xdg-open /tmp/dump/domain_groups.html
xdg-open /tmp/dump/domain_computers.html
xdg-open /tmp/dump/domain_policy.html

# Chercher des mots de passe dans les descriptions
cat /tmp/dump/domain_users.json | jq '.[] | select(.description != "") | {username, description}'

# OS non supportés
cat /tmp/dump/domain_computers.json | jq -r '.[] | select(.operatingsystem | contains("7") or contains("2008")) | .computername'

# Politique de mot de passe
cat /tmp/dump/domain_policy.json | jq '.'
```