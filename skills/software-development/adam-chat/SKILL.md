---
name: adam-chat
description: Serveur de messagerie sécurisé auto-hébergé (Signal-like) avec Flask + WebSocket + AES-256-GCM + pont EVA
---

# ADAM-CHAT — Messagerie Sécurisée

Serveur de messagerie temps réel auto-hébergé dans `~/chat/` avec chiffrement AES-256-GCM, WebSocket et pont vers EVA.

## Structure

```
~/chat/
├── server.py          # Flask + Flask-SocketIO (port 8085)
├── models.py          # SQLite + AES-256-GCM + bcrypt
├── eva-bridge.py      # Pont EVA (relie #eva → hermes CLI)
├── start.sh           # Script de démarrage/arrêt
├── static/
│   └── chat.js        # Client JS (WebSocket + chiffrement)
├── templates/
│   └── chat.html      # Interface dark cyberpunk
├── uploads/           # Fichiers uploadés
└── .venv/             # Environnement virtuel
```

## Canaux par défaut

- `#general` — Discussions générales
- `#eva` — Canal relié à EVA
- `#adam` — Développement
- `#cybersec` — CyberSécurité
- `#dev` — Projets techniques

## Démarrage

```bash
cd ~/chat
source .venv/bin/activate
python3 server.py
# Ou: ./start.sh all
```

Accès : http://192.168.1.5:8085

## Compte admin

- Username: `admin`
- Password: `admin123`

## API REST

| Méthode | Route | Description |
|---------|-------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/login` | Connexion |
| POST | `/api/register` | Inscription |
| GET | `/api/channels` | Liste des canaux |
| POST | `/api/channels` | Créer un canal |
| GET | `/api/messages/<id>` | Messages d'un canal |
| POST | `/api/messages/<id>` | Envoyer un message |
| PUT | `/api/messages/<id>/edit` | Modifier un message |
| DELETE | `/api/messages/<id>` | Supprimer un message |
| GET | `/api/users` | Liste des utilisateurs |
| POST | `/api/upload` | Upload fichier |

## Pont EVA

Le `eva-bridge.py` écoute les messages du canal `#eva` (channel_id=2) et les relaye à EVA via `hermes chat -q`. Les réponses sont renvoyées dans le canal.

```bash
python3 eva-bridge.py
```

## Sécurité

- Mots de passe hashés avec bcrypt
- Sessions JWT (72h d'expiration)
- Chiffrement AES-256-GCM des messages (PBKDF2 600k itérations)
- Rate limiting (30 req/10s)
- Uploads sécurisés (werkzeug secure_filename)
- CORS configuré
- XSS protection via template escaping

## Dépendances

```
flask flask-socketio flask-cors bcrypt pyjwt cryptography python-dotenv eventlet
```