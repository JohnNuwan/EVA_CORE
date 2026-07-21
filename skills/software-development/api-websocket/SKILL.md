---
name: api-websocket
description: "Use when concevoir, implémenter ou auditer une API WebSocket. Couvre le protocole RFC 6455, le handshake HTTP Upgrade, les frames, les patterns de communication (pub/sub, notifications, chat), la reconnexion, le heartbeat/ping-pong, l'authentification, la scalabilité, et les implémentations Python/Node.js/Go."
version: 1.0.0
author: EVA
license: MIT
metadata:
  hermes:
    tags: [api, websocket, realtime, streaming, http2, backend]
    related_skills: [api-rest-best-practices, api-grpc, api-security, api-rate-limiting]
---

# API WebSocket

## Vue d'ensemble

WebSocket (RFC 6455, 2011) est un protocole qui établit une connexion full-duplex persistante entre un client et un serveur sur une seule connexion TCP. Après un handshake HTTP Upgrade, la connexion passe du protocole HTTP au protocole WebSocket, permettant l'envoi de messages dans les deux sens sans la surcharge des requêtes HTTP. Idéal pour les applications temps réel : notifications, chat, mises à jour de prix, collaboration, jeux.

## Quand l'utiliser

- Notifications en temps réel (alertes, événements)
- Chat et messagerie instantanée
- Mises à jour de données fréquentes (prix boursiers, cryptos, scores sportifs)
- Applications collaboratives (éditeurs, tableaux blancs)
- Tableaux de bord live (monitoring, logs)
- Jeux multijoueurs temps réel
- IoT avec flux de données continu

Ne pas utiliser pour : des requêtes API classiques requête-réponse (REST/GraphQL suffisent), des transferts de fichiers volumineux (préférer HTTP range requests), des communications nécessitant une fiabilité transactionnelle (WebSocket n'a pas de garantie de livraison), ou quand le nombre de connexions simultanées dépasse les capacités du serveur.

## Concepts Fondamentaux

### 1. Handshake HTTP Upgrade

Le client initie la connexion :

```http
GET /ws/chat HTTP/1.1
Host: api.eva.dev
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://eva.dev
```

Réponse du serveur :

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 2. Structure des Frames

Chaque message WebSocket est encapsulé dans une frame :

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-------+-+-------------+-------------------------------+
|F|R|R|R| opcode|M| Payload len |    Extended payload length    |
|I|S|S|S|  (4)  |A|     (7)     |             (16/64)           |
|N|V|V|V|       |S|             |                               |
| |1|2|3|       |K|             |                               |
+-+-+-+-+-------+-+-------------+-------------------------------+
```

**Opcodes :**

| Code | Type | Usage |
|------|------|-------|
| 0x0 | Continuation | Suite d'un message fragmenté |
| 0x1 | Text | Message texte (UTF-8) |
| 0x2 | Binary | Données binaires |
| 0x8 | Close | Fermeture de connexion |
| 0x9 | Ping | Heartbeat (côté serveur) |
| 0xA | Pong | Réponse au Ping |

### 3. Patterns de Communication

**Pub/Sub :**

```json
// Client → Serveur : s'abonner à un canal
{"type": "subscribe", "channel": "articles:new"}

// Serveur → Client : notification
{"type": "event", "channel": "articles:new", "data": {"id": 42, "title": "..."}}

// Client → Serveur : se désabonner
{"type": "unsubscribe", "channel": "articles:new"}
```

**Protocole de requête-réponse (avec correlation ID) :**

```json
// Client → Serveur
{"type": "request", "id": "req-001", "method": "get_article", "params": {"id": 42}}

// Serveur → Client
{"type": "response", "id": "req-001", "result": {"id": 42, "title": "..."}}
```

**Notifications push :**

```json
// Serveur → Client (sans requête préalable)
{"type": "notification", "event": "order_shipped", "order_id": 1234, "status": "shipped"}
```

### 4. Heartbeat et Reconnexion

**Ping/Pong (automatique dans la plupart des librairies) :**

```javascript
// Côté client (vanilla JS)
const ws = new WebSocket('wss://api.eva.dev/ws');
ws.onopen = () => console.log('Connecté');
ws.onclose = (event) => {
  // Reconnexion avec backoff exponentiel
  setTimeout(() => connect(), Math.min(1000 * 2 ** retries, 30000));
};
ws.onerror = (err) => console.error('WebSocket error:', err);
```

```python
# Côté serveur (FastAPI WebSocket)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Attendre un message avec timeout (heartbeat)
            data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
            await process_message(websocket, data)
    except asyncio.TimeoutError:
        # Envoyer un ping, si pas de pong → fermer
        await websocket.close(1000, "Inactif")
    except WebSocketDisconnect:
        logger.info("Client déconnecté")
```

### 5. Authentification

**Via le handshake (query param ou cookie) :**

```javascript
const ws = new WebSocket(`wss://api.eva.dev/ws?token=${jwt}`);
```

Ou via le cookie de session HTTP :

```python
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket, token: str = Query(...)):
    user = verify_jwt(token)
    if not user:
        await websocket.close(4001, "Non authentifié")
        return
    await websocket.accept()
```

**Authentification post-connexion :**

```json
// Premier message après la connexion
{"type": "auth", "token": "eyJhbGciOiJIUzI1NiJ9..."}
```

### 6. Gestion des Pièces/Rooms

```python
class RoomManager:
    def __init__(self):
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def join(self, room: str, ws: WebSocket):
        self.rooms[room].add(ws)

    async def leave(self, room: str, ws: WebSocket):
        self.rooms[room].discard(ws)
        if not self.rooms[room]:
            del self.rooms[room]

    async def broadcast(self, room: str, message: str, exclude: WebSocket = None):
        for ws in self.rooms.get(room, set()):
            if ws != exclude and ws.client_state == WebSocketState.CONNECTED:
                try:
                    await ws.send_text(message)
                except WebSocketDisconnect:
                    self.rooms[room].discard(ws)
```

### 7. Scalabilité (Multi-Process)

WebSocket est stateful — un message ne peut pas être routé à un autre serveur sans couche de transport :

```python
# Architecture avec Redis Pub/Sub
import redis.asyncio as redis

class ScalableRoomManager:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.local_rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def start(self):
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe("ws:events")
        asyncio.create_task(self._listen_redis())

    async def _listen_redis(self):
        async for msg in self.pubsub.listen():
            if msg['type'] == 'message':
                data = json.loads(msg['data'])
                # Diffuser aux clients locaux de cette room
                for ws in self.local_rooms.get(data['room'], set()):
                    await ws.send_text(data['payload'])

    async def broadcast(self, room: str, message: str):
        # Publier sur Redis → tous les serveurs reçoivent
        await self.redis.publish("ws:events", json.dumps({
            "room": room,
            "payload": message,
        }))
```

## Implémentation Référence

### FastAPI WebSocket (Python)

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from typing import Dict, Set
import json

app = FastAPI()
rooms: Dict[str, Set[WebSocket]] = {}

@app.websocket("/ws/{room}")
async def websocket_room(websocket: WebSocket, room: str, token: str = Query(...)):
    user = await verify_token(token)
    if not user:
        await websocket.close(4001, "Non authentifié")
        return

    await websocket.accept()
    rooms.setdefault(room, set()).add(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg["type"] == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg["type"] == "message":
                # Diffuser à tous les clients de la room
                payload = json.dumps({
                    "type": "message",
                    "user": user["name"],
                    "content": msg["content"],
                    "timestamp": msg.get("timestamp"),
                })
                for ws in rooms[room]:
                    if ws != websocket:
                        await ws.send_text(payload)
            elif msg["type"] == "typing":
                await websocket.send_text(json.dumps({
                    "type": "typing", "user": user["name"]
                }))
    except WebSocketDisconnect:
        rooms[room].discard(websocket)
        if not rooms[room]:
            del rooms[room]
```

### ws (Node.js)

```javascript
const WebSocket = require('ws');
const server = new WebSocket.Server({ port: 8080 });

const rooms = new Map();

server.on('connection', (ws, req) => {
  const url = new URL(req.url, 'http://localhost');
  const room = url.pathname.split('/').pop();
  const token = url.searchParams.get('token');

  // Auth
  const user = verifyJWT(token);
  if (!user) { ws.close(4001, 'Unauthorized'); return; }

  if (!rooms.has(room)) rooms.set(room, new Set());
  rooms.get(room).add(ws);

  ws.on('message', (data) => {
    const msg = JSON.parse(data);
    // Broadcast à la room
    for (const client of rooms.get(room)) {
      if (client !== ws && client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify({ user: user.name, content: msg.content }));
      }
    }
  });

  ws.on('close', () => {
    rooms.get(room)?.delete(ws);
    if (rooms.get(room)?.size === 0) rooms.delete(room);
  });
});
```

### Gorilla WebSocket (Go)

```go
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
    ReadBufferSize:  1024,
    WriteBufferSize: 1024,
}

type Client struct {
    conn *websocket.Conn
    room string
    send chan []byte
}

var rooms = make(map[string]map[*Client]bool)

func handleWS(w http.ResponseWriter, r *http.Request) {
    conn, _ := upgrader.Upgrade(w, r, nil)
    token := r.URL.Query().Get("token")
    user, _ := validateJWT(token)

    client := &Client{conn: conn, send: make(chan []byte, 256)}
    rooms[client.room][client] = true

    go client.writePump()
    client.readPump()
}
```

## Pièges Courants

1. **Pas de heartbeat** — un client peut être déconnecté silencieusement. Toujours envoyer des ping/pong (30s est un bon intervalle).
2. **Reconnexion sans backoff** — 1000 clients qui se reconnectent en même temps submergent le serveur. Implémenter un exponential backoff avec jitter.
3. **Pas de gestion des rooms** — envoyer à tous les clients connectés est un anti-pattern. Utiliser des rooms/canaux.
4. **Scalabilité oubliée** — un seul processus ne peut pas gérer des milliers de connexions. Utiliser Redis/pub-sub pour la scalabilité horizontale.
5. **Messages non structurés** — envoyer du texte brut sans protocole rend le client fragile. Toujours structurer en JSON avec un champ `type`.
6. **Authentification WebSocket uniquement** — l'URL peut être loggée. Ne pas mettre le token dans l'URL si les logs sont sensibles (préférer le premier message).
7. **Pas de rate limiting** — un client peut envoyer 10k messages/seconde. Implémenter un throttling par connexion.
8. **Fuite mémoire** — un client déconnecté mais non retiré de la room reste en mémoire. Toujours gérer `onclose`.

## Checklist de Vérification

- [ ] Handshake sécurisé (wss://, pas ws:// en production)
- [ ] Authentification (query param, cookie, ou premier message)
- [ ] Heartbeat ping/pong configuré (côté serveur)
- [ ] Reconnexion client avec exponential backoff + jitter
- [ ] Gestion des rooms/ canaux avec nettoyage onclose
- [ ] Rate limiting par connexion (messages/seconde)
- [ ] Scalabilité : Redis pub/sub ou équivalent
- [ ] Validation des messages (schéma JSON ou protobuf)
- [ ] Fermeture propre des connexions (code 1000, 1001, etc.)
- [ ] Tests : connexion, reconnexion, broadcast, auth invalide