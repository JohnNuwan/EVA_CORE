---
name: godot-engine
description: Guide complet du moteur Godot 4 — GDScript, C#, scènes/nœuds, ShaderMaterial, tilesets, système de signaux, multiplayer (ENet/WebRTC), optimisation et export multiplateforme.
---

# Godot Engine — Guide Complet

Ce skill couvre le développement avec Godot Engine 4.x. À charger pour toute tâche impliquant Godot, GDScript, C# dans Godot, ou le déploiement de jeux Godot.

---

## 1. Structure du Projet Godot

```
MonJeu/
├── project.godot              # Fichier projet
├── .godot/                    # Cache généré (ignorer dans .gitignore)
├── assets/                    # Ressources brutes (sprites, sons, modèles)
├── scenes/                    # Fichiers .tscn (scènes)
│   ├── Main.tscn
│   ├── Player/
│   │   ├── Player.tscn
│   │   └── Player.gd
├── scripts/                   # Scripts .gd et .cs
├── shaders/                   # Shaders (.gdshader)
├── autoload/                  # Singletons (scènes autoload)
├── addons/                    # Plugins éditeur Godot
└── exports/                   # Builds de sortie
```

### .gitignore Godot
```
.godot/
*.import
export.cfg
exports/
```

---

## 2. GDScript — Patterns Essentiels

### Nœud de base

```gdscript
extends CharacterBody2D

@export var vitesse := 300.0
@export var force_saut := -500.0
@export var acceleration := 0.2

func _physics_process(delta: float) -> void:
    # Mouvement
    var direction := Input.get_axis("gauche", "droite")
    if direction:
        velocity.x = move_toward(velocity.x, direction * vitesse, acceleration * 60)
    else:
        velocity.x = move_toward(velocity.x, 0, acceleration * 60)
    
    # Saut
    if Input.is_action_just_pressed("sauter") and is_on_floor():
        velocity.y = force_saut
    
    move_and_slide()
```

### Signaux (Signals) — Le pattern clé Godot

```gdscript
# Émetteur : ObjetCollectible.gd
extends Area2D

signal objet_collecte(type: String, valeur: int)

@export var type_objet := "pièce"
@export var valeur := 10

func _on_body_entered(body: Node2D) -> void:
    if body is CharacterBody2D:
        objet_collecte.emit(type_objet, valeur)
        queue_free()

# Récepteur : Joueur.gd
func _ready() -> void:
    var collectible := $ZoneCollectible as Area2D
    collectible.objet_collecte.connect(_sur_collecte)

func _sur_collecte(type: String, valeur: int) -> void:
    print("Collecté: ", type, " +", valeur)
```

### Autoload (Singleton)

```gdscript
# autoload/GestionnaireJeu.gd
extends Node

var score := 0
var vies := 3

func ajouter_score(points: int) -> void:
    score += points
    print("Score: ", score)

func reset() -> void:
    score = 0
    vies = 3
```

---

## 3. Système de Nœuds et Scènes

### Héritage de scène

```gdscript
# Créer une scène Ennemi.tscn, puis EnnemiAvance.tscn en héritant
# Dans EnnemiAvance.gd :
extends preload("res://scenes/Ennemi.tscn").node_type

func _ready() -> void:
    # Surcharger les valeurs par défaut
    vitesse = 150.0
    points_vie = 2
```

### Instanciation

```gdscript
# Charger et instancier une scène
var ennemi_scene := preload("res://scenes/Ennemi.tscn")
var ennemi := ennemi_scene.instantiate()
add_child(ennemi)
ennemi.position = Vector2(100, 100)
```

---

## 4. Shaders Godot (ShaderMaterial)

```glsl
// shaders/effet_vague.gdshader
shader_type canvas_item;

uniform float amplitude : hint_range(0.0, 50.0) = 10.0;
uniform float frequence : hint_range(0.0, 20.0) = 5.0;
uniform float vitesse : hint_range(0.0, 5.0) = 1.0;

void fragment() {
    vec2 uv = UV;
    uv.y += sin(uv.x * frequence + TIME * vitesse) * amplitude / TEXTURE_PIXEL_SIZE.y;
    COLOR = texture(TEXTURE, uv);
}
```

### Shader 3D

```glsl
shader_type spatial;

uniform float emission_intensity : hint_range(0.0, 2.0) = 0.5;

void fragment() {
    ALBEDO = vec3(0.2, 0.6, 1.0);
    EMISSION = ALBEDO * emission_intensity;
    ROUGHNESS = 0.3;
    METALLIC = 0.8;
}
```

---

## 5. Tilesets et Tilemaps

```gdscript
# Créer un tilemap procédural
extends TileMap

@export var taille_carte := Vector2i(50, 50)

func _ready() -> void:
    generer_terrain()

func generer_terrain() -> void:
    clear()
    
    # Tile source ID (dans le TileSet)
    var tuile_herbe := Vector2i(0, 0)
    var tuile_mur := Vector2i(1, 0)
    
    for x in range(taille_carte.x):
        for y in range(taille_carte.y):
            if y < 3:
                set_cell(Vector2i(x, y), 0, tuile_herbe)
            else:
                set_cell(Vector2i(x, y), 0, tuile_mur)
```

### TileSets avancés — Terrains connectés (3x3 minimal)

```
# Configuration dans l'éditeur TileSet:
# - Taille de tuile: 16x16
# - Règle de terrain: bits de connexion (NE, NW, SE, SW)
# Bitmask: 4 bits → 16 patterns de tuiles
```

---

## 6. Animation et State Machine

### AnimationPlayer

```gdscript
extends AnimatedSprite2D

func _ready() -> void:
    animation = "marche"
    play()

func changer_animation(etat: String) -> void:
    if animation != etat:
        animation = etat
```

### State Machine maison

```gdscript
# PlayerStateMachine.gd
extends Node

enum Etat { IDLE, MARCHE, SAUT, ATTAQUE }
var etat_courant := Etat.IDLE

func transition(etat: Etat) -> void:
    if etat == etat_courant:
        return
    
    sortir(etat_courant)
    etat_courant = etat
    entrer(etat)

func entrer(etat: Etat) -> void:
    match etat:
        Etat.IDLE:   _anim.play("idle")
        Etat.MARCHE: _anim.play("marche")
        Etat.SAUT:   _anim.play("saut")

func sortir(etat: Etat) -> void:
    # Nettoyage si nécessaire
    pass
```

---

## 7. Réseau et Multiplayer

```gdscript
# Serveur/Client dédié
extends Node

@export var port := 8080
@export var max_joueurs := 8

func demarrer_serveur() -> void:
    var peer := ENetMultiplayerPeer.new()
    peer.create_server(port, max_joueurs)
    multiplayer.multiplayer_peer = peer
    multiplayer.peer_connected.connect(_joueur_connecte)
    print("Serveur démarré sur :", port)

func connecter_client(ip: String) -> void:
    var peer := ENetMultiplayerPeer.new()
    peer.create_client(ip, port)
    multiplayer.multiplayer_peer = peer

@rpc("any_peer", "call_local")
func deplacer_joueur(position: Vector2) -> void:
    # Appelé sur tous les pairs
    pass
```

### WebRTC (alternative basse latence)
```gdscript
# WebRTC via plugin / addon WebRTC
var webrtc := WebRTCPeerConnection.new()
webrtc.initialize()
```

---

## 8. Export et Déploiement

```bash
# Export CLI
godot --headless --export-release "Linux/X11" ./exports/MonJeu.x86_64
godot --headless --export-release "Windows Desktop" ./exports/MonJeu.exe
godot --headless --export-release "Android" ./exports/MonJeu.apk
godot --headless --export-release "Web" ./exports/index.html

# Export templates: Editor → Editor Settings → Export → Gérer les templates
# Téléchargement: https://godotengine.org/download/archive/4.x/
```

### Configuration export Android
```gdscript
# export_presets.cfg remplissage:
# keystore: /chemin/mon.keystore
# package_name: com.monstudio.monjeu
# version_code: 1
# permissions: internet, vibration, wake_lock
```

---

## 9. Optimisation Godot

```
# Profiler: Debugger → Profiler
# Moniteur: Debugger → Monitors (FPS, mémoire, draw calls)

# Paramètres de performance
rendering/quality/driver/driver_name opengl3  # fallback Vulkan→OGL
rendering/quality/shader_compilation/async_shader_compilation_enabled true
rendering/quality/2d/gles_over_gl_es_2_3 true
physics/common/physics_ticks_per_second 30     # 60 par défaut, baisser pour mobile
```

### Checklist perf Godot
1. **Canvas Item** : limiter les CanvasItem modifiés → utiliser tilemaps pour fonds
2. **Light2D** : shadows seulement si nécessaire (très coûteux en 2D)
3. **Object pooling** : réutiliser les nœuds via un pool, pas d'instanciation/destruction
4. **AnimationPlayer** : supprimer les tracks inutilisées
5. **Signaux** : éviter de connecter/déconnecter en masse (préférer groups)
6. **Physics** : layers de collision bien séparés (éviter les checks superflus)

---

## 10. Pièges Courants

- **Reference cycles** → fuite mémoire Godot (préférer weakref)
- **free() vs queue_free()** : queue_free() diffère la suppression à la fin de la frame
- **@export sans type** → Godot ne peut pas sérialiser (toujours typer)
- **Physics interpolation** : désactiver si des artefacts de mouvement apparaissent
- **GDScript typé vs dynamique** : toujours utiliser `-> Type` pour la perf du compilateur
- **Shader compilation stutter** : activer `async_shader_compilation` dans ProjectSettings
- **Android export** : SDK/NDK path dans `Editor → Editor Settings → Export → Android`
- **Web export** : pas de threading sans WASM threading flags dans le navigateur
