---
name: bloodhound
description: BloodHound — cartographie et analyse des relations Active Directory, collecteurs (SharpHound, AzureHound), requêtes Cypher personnalisées, attaque des chemins de privilèges, ACL abuse, ACE abusives, et optimisation des attaques AD.
---

# BloodHound — Analyse des Chemins d'Attaque AD

## Présentation

BloodHound (BH) est un outil de cartographie des relations Active Directory. Il identifie les chemins d'attaque cachés entre les objets du domaine.

**Composants :**
- **Collecteur** (SharpHound.exe / AzureHound.ps1) → collecte les données AD
- **Interface** (bloodhound GUI) → visualisation des graphes
- **Base** (Neo4j) → stockage des données de graphe

**Installation :**
```bash
# Kali
sudo apt install bloodhound
sudo neo4j console            # Démarrer Neo4j
# OU
sudo systemctl start neo4j    # Démarrer Neo4j

# Dernière version
git clone https://github.com/BloodHoundAD/BloodHound.git
cd BloodHound && npm install && npm run build

# Credentials Neo4j par défaut
# http://localhost:7474
# Login: neo4j
# Password: neo4j (changé au premier login)
```

---

## Collecteurs

### SharpHound.exe (Windows — .NET)
```bash
# Collecte complète
SharpHound.exe -c All

# Collecte spécifique
SharpHound.exe -c Group          # Groupes seulement
SharpHound.exe -c LocalGroup     # Groupes locaux
SharpHound.exe -c Session        # Sessions
SharpHound.exe -c ACL            # ACLs
SharpHound.exe -c Container      # Containers
SharpHound.exe -c ObjectProps    # Propriétés des objets
SharpHound.exe -c DCOM          # DCOM users
SharpHound.exe -c PSRemote      # PSRemote users
SharpHound.exe -c RDP           # RDP users

# Avec authentification
SharpHound.exe --domain DOMAIN --ldapuser admin --ldappass Password123

# Collecte via DCOnly (moins bruyant)
SharpHound.exe -c All --CollectionMethod DCOnly

# Collecte pour un grand domaine (10000+ utilisateurs)
SharpHound.exe -c Group,LocalGroup,Session --throttle 500

# Avec certificat LDAP (collecte furtive)
SharpHound.exe --LdapPassword Password123 --CertificatePath cert.pfx

# Sortie dans un dossier spécifique
SharpHound.exe -c All --OutputDirectory C:\temp\
```

### SharpHound.ps1 (PowerShell)
```powershell
# Charger le script
Import-Module .\SharpHound.ps1

# Collecte complète
Invoke-BloodHound -CollectionMethod All

# Avec credentials
$cred = Get-Credential
Invoke-BloodHound -CollectionMethod All -Credential $cred

# DC Only (moins bruyant)
Invoke-BloodHound -CollectionMethod DCOnly

# Options :
#   -Stealth : Skip ping et connexions SMB
#   -Loop : Collecte continue (boucle)
#   -Interval N : Intervalle entre collectes (minutes)
#   -Threads N : Threads (augmenter pour les grands domaines)
#   -SearchForest : Rechercher dans toute la forêt
```

### AzureHound (Azure AD)
```bash
# Collecter les données Azure AD
azh.exe -u admin@domain.com -p Password123
# Export JSON des relations Azure AD
```

### BloodHound.py (Linux)
```bash
# Collecteur Python (depuis Linux)
impacket-bloodhound -c all -u admin -d DOMAIN -dc-ip 192.168.1.10

# Ou via impacket-getTGT + export
impacket-getTGT DOMAIN/user:Password123
export KRB5CCNAME=/path/to/ticket.ccache
bloodhound-python -c All -d DOMAIN -dc DC -k
```

---

## Import des données dans BloodHound

```bash
# 1. Démarrer Neo4j
sudo neo4j console
# OU
sudo systemctl start neo4j

# 2. Démarrer BloodHound
bloodhound

# 3. Connexion Neo4j
#   http://localhost:7474
#   browser → connect to bolt://localhost:7687
#   user: neo4j
#   pass: <mot de passe>

# 4. Upload des fichiers JSON
#   Dans BloodHound GUI : Upload Data → Sélectionner les fichiers .json
#   Les fichiers sont dans le dossier courant du collecteur :
#     20240101120000_BloodHound.zip  # Fichier zip contenant les JSON
#   OU directement les JSON :
#     users.json
#     groups.json
#     computers.json
#     sessions.json
#     acls.json
```

---

## Requêtes pré-construites (GUI)

### Analyse rapide — Les 5 questions essentielles
```bash
# 1. Trouver les administrateurs du domaine
#   → "Find all Domain Admins"

# 2. Chemin le plus court vers Domain Admins
#   → "Shortest Paths to Domain Admins from <user>"

# 3. Utilisateurs avec des sessions sensibles
#   → "Find all users with sessions on admin computers"

# 4. Groupes avec des permissions étendues
#   → "Find all groups with admin rights"

# 5. Chemins d'attaque GPO
#   → "Find all paths from Group Policy Objects to Domain Admins"
```

### Requêtes de recherche de privilèges
```bash
# Trouver les utilisateurs avec des droits d'admin local
"Find Computers where Domain Users are Local Admin"

# Trouver les utilisateurs avec RDP access
"Find Computers where Domain Users have RDP access"

# Trouver les utilisateurs avec SQL admin
"Find Computers where Domain Users have SQL Admin access"

# Lister les sessions actives
"Find all Active Sessions"

# Maps de toutes les relations
"Node Mapper"
```

---

## Requêtes Cypher — Le cœur de BloodHound

### Concepts Cypher
```cypher
// Syntaxe de base
MATCH (n:User) RETURN n LIMIT 10                    // 10 users
MATCH (n:Computer) RETURN n LIMIT 10                 // 10 computers
MATCH (n:Group) RETURN n.name LIMIT 10                // Noms des groupes
MATCH (n:User {name:"ADMIN@DOMAIN.LOCAL"}) RETURN n  // User spécifique
```

### Requêtes d'analyse avancées

#### 1. Chemin le plus court vers DA
```cypher
// D'un utilisateur spécifique vers Domain Admins
MATCH (u:User {name:"USER@DOMAIN.LOCAL"}), 
      (g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})
MATCH p = shortestPath((u)-[*1..]->(g))
RETURN p

// D'un groupe vers DA
MATCH (g1:Group {name:"GROUPE@DOMAIN.LOCAL"}),
      (g2:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})
MATCH p = shortestPath((g1)-[*1..]->(g2))
RETURN p
```

#### 2. Trouver tous les chemins vers DA
```cypher
// Tous les chemins (pas seulement le plus court)
MATCH (u:User {name:"USER@DOMAIN.LOCAL"}), 
      (g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})
MATCH p = allShortestPaths((u)-[*1..]->(g))
RETURN p
```

#### 3. Utilisateurs avec GenericAll sur des groupes privilégiés
```cypher
MATCH (u:User), (g:Group)
WHERE g.highvalue = true
MATCH p = (u)-[r:GenericAll]->(g)
RETURN u.name, g.name, r.isacl
```

#### 4. Chercher les ACL abusives (GenericAll, WriteOwner, etc.)
```cypher
// GenericAll sur un objet
MATCH (u:User)-[r:GenericAll]->(obj)
WHERE NOT obj:Domain
RETURN u.name, type(r), labels(obj), obj.name

// WriteDACL (modification des permissions)
MATCH (u:User)-[r:WriteDacl]->(obj)
RETURN u.name, type(r), labels(obj), obj.name

// WriteOwner (changement de propriétaire)
MATCH (u:User)-[r:WriteOwner]->(obj)
RETURN u.name, type(r), labels(obj), obj.name

// ForceChangePassword
MATCH (u:User)-[r:ForceChangePassword]->(obj:User)
RETURN u.name, obj.name

// AllExtendedRights (souvent inclus DCSync)
MATCH (u:User)-[r:AllExtendedRights]->(obj)
RETURN u.name, type(r), labels(obj), obj.name
```

#### 5. Sessions actives sur des machines sensibles
```cypher
// Utilisateurs ayant une session sur un server DA
MATCH (u:User)-[:HasSession]->(c:Computer)
MATCH (c)-[:AdminTo]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})
RETURN u.name, c.name

// Utilisateurs avec sessions multiples
MATCH (u:User)-[:HasSession]->(c:Computer)
WITH u, count(DISTINCT c) as sessionCount
WHERE sessionCount > 1
RETURN u.name, sessionCount
ORDER BY sessionCount DESC
```

#### 6. Machines avec contraintes de délégation
```bash
# Unconstrained Delegation
MATCH (c:Computer {unconstraineddelegation:true})
RETURN c.name, c.operatingsystem

# Constrained Delegation
MATCH (c:Computer)-[:AllowedToDelegate]->(c2:Computer)
RETURN c.name, c2.name

# Resource-based Constrained Delegation
MATCH (c:Computer)-[:AllowedToDelegate]->(c2:Computer)
WHERE c.primarygroupSID =~ "S-1-5-21-.*-512"
RETURN c.name, c2.name
```

#### 7. Propriétaires des ordinateurs
```cypher
// Qui peut modifier les propriétés des ordinateurs ?
MATCH (u:User)-[:Owns]->(c:Computer)
RETURN u.name, c.name
```

#### 8. Groupes locaux administrateurs
```cypher
// Groupes et utilisateurs qui sont admin local sur plusieurs machines
MATCH (u)-[:AdminTo]->(c:Computer)
WITH u, count(DISTINCT c) as adminCount
WHERE adminCount > 10
RETURN u.name, labels(u), adminCount
ORDER BY adminCount DESC
```

#### 9. Utilisateurs avec DCSync rights
```cypher
// DCSync = Replication-Getting-Changes + Replication-Getting-Changes-All
MATCH (u:User)
WHERE u.name =~ "(?i).*admin.*"
MATCH p = (u)-[:DS-Replication-Get-Changes|DS-Replication-Get-Changes-All*1..]->(d:Domain)
RETURN u.name, p
```

#### 10. Chemins d'attaque GPO
```cypher
// GPO appliquées à des machines sensibles
MATCH (gpo:GPO)-[:GpLink]->(ou)-[:Contains*1..]->(c:Computer)
MATCH (c)-[:AdminTo]->(g:Group)
WHERE g.highvalue = true
RETURN gpo.name, g.name, c.name
```

#### 11. Kerberoastable users
```cypher
// Utilisateurs avec un SPN (Kerberoastable)
MATCH (u:User {hasspn:true})
RETURN u.name, u.displayname, u.title
```

#### 12. AS-REP Roastable users
```cypher
// Utilisateurs sans pré-authentification
MATCH (u:User {dontreqpreauth:true})
RETURN u.name
```

#### 13. Certificates vulnérables (ESC1-ESC8)
```cypher
// ESC1 : Certificats avec SAN (Subject Alternative Name) non contrôlé
MATCH (n:GPO)-[:GpLink]->(ou:OU)
OPTIONAL MATCH (n)-[:Contains*]->(c:Computer)
RETURN n.name, count(DISTINCT c)
```

---

## Analyse avancée

### Trouver des chemins non documentés
```cypher
// Chemins > 3 sauts (long mais possible)
MATCH p = shortestPath((u:User)-[*1..10]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"}))
WHERE length(p) > 3
RETURN p
LIMIT 20
```

### Objets avec des permissions non standard
```cypher
// Objets avec ACL modifiées (potentiellement dangereuses)
MATCH (n)-[r]->(m)
WHERE type(r) IN ["GenericAll", "WriteDacl", "WriteOwner", "ForceChangePassword",
                   "GenericWrite", "AddMember", "AddSelf", "AllExtendedRights"]
  AND NOT n.name =~ ".*DOMAIN USERS.*"
  AND NOT m.name =~ ".*DOMAIN ADMINS.*"
RETURN n.name, type(r), labels(m), m.name
```

### Délégation dangereuse
```cypher
// Délégation d'admin local à des groupes non privilégiés
MATCH (g:Group)-[:AdminTo]->(c:Computer)
MATCH (u:User)-[:MemberOf*1..]->(g)
WHERE NOT g.name =~ "DOMAIN ADMINS@.*|ENTERPRISE ADMINS@.*|BUILTIN.*"
RETURN g.name, count(DISTINCT c) as computers, count(DISTINCT u) as users
ORDER BY computers DESC
```

---

## BloodHound Custom Queries (JSON)

```json
// ~/.config/bloodhound/customqueries.json
[
  {
    "name": "ACL Abuse - GenericAll",
    "category": "ACL Abuse",
    "query": "MATCH (u:User)-[r:GenericAll]->(obj) WHERE NOT obj:Domain RETURN u.name, type(r), labels(obj), obj.name"
  },
  {
    "name": "Kerberoastable + Description",
    "category": "Kerberos",
    "query": "MATCH (u:User {hasspn:true}) RETURN u.name, u.description, u.title, u.displayname"
  },
  {
    "name": "High-Value Sessions",
    "category": "Sessions",
    "query": "MATCH (u:User)-[:HasSession]->(c:Computer) MATCH (c)-[:AdminTo]->(g:Group {highvalue:true}) RETURN u.name, c.name, g.name"
  }
]
```

---

## BloodHound CE (Community Edition)

```bash
# BloodHound CE (nouvelle version)
# Interface web + plus de fonctionnalités
# Utilise toujours Neo4j

# Installation
docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/bloodhound \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:5-enterprise

# BloodHound CE UI
docker run -d --name bhce -p 8080:8080 \
    ghcr.io/s0lst1c3/bloodhound-ce:latest
```

---

## Scénarios complets

### 1. Audit AD complet
```bash
# 1. Collecte (depuis une machine Windows du domaine)
SharpHound.exe -c All

# 2. Import dans BloodHound GUI

# 3. Analyse :
#   - Shortest Paths to Domain Admins
#   - Find all Kerberoastable Users
#   - Find all AS-REP Roastable Users
#   - Find Computers with Unconstrained Delegation
#   - ACL Abuse paths
```

### 2. Élévation de privilèges via ACL
```bash
# BloodHound montre un chemin :
# USER → GenericAll → GROUP1 → MemberOf → DOMAIN ADMINS

# Exploitation :
# 1. Ajouter USER à GROUP1 (GenericAll permet addmember)
net group GROUP1 USER /add /domain

# 2. USER hérite des droits de GROUP1
# 3. Si GROUP1 a des droits DA → USER devient DA
```

### 3. Kerberoasting guidé par BloodHound
```bash
# BloodHound liste les utilisateurs avec hasSPN=true
# → Utiliser GetUserSPNs sur ces comptes seulement

impacket-GetUserSPNs DOMAIN/user:Password@DC -usersfile kerberoast_users.txt
```

---

## Dépannage

| Problème | Solution |
|----------|----------|
| Neo4j ne démarre pas | java --version, vérifier JAVA_HOME |
| "Unable to connect" | Vérifier bolt://localhost:7687 |
| Données vides | Vérifier la collecte (SharpHound.exe -c All) |
| Collecte lente | Réduire les threads (--throttle) |
| Trop de nœuds | Filtrer par type dans la GUI |
| BloodHound CE lourd | Préférer BloodHound original (python) |

---

## Antisèche rapide

```bash
# Collecte (Windows)
SharpHound.exe -c All

# Collecte (Linux)
bloodhound-python -c All -d DOMAIN -u admin -p Password -dc DC

# Lancer Neo4j
sudo systemctl start neo4j
# -> http://localhost:7474

# Lancer BloodHound
bloodhound

# Upload → Glisser les fichiers JSON dans BloodHound

# Requêtes essentielles (GUI)
#   "Find all Domain Admins"
#   "Shortest Paths to Domain Admins"
#   "Find all Kerberoastable Users"

# Cypher rapide
MATCH (u:User {hasspn:true}) RETURN u.name
MATCH (n)-[r:GenericAll]->(m) WHERE NOT n:Domain RETURN n.name, labels(m), m.name
MATCH (c:Computer {unconstraineddelegation:true}) RETURN c.name
```