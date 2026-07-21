---
name: procedural-generation
description: Guide complet de génération procédurale — bruit de Perlin/Simplex, terrain heightmap, dungeon generation, L-systems, Wave Function Collapse (WFC), cellular automata, PCG pour textures/armes/quêtes, et optimisation.
---

# Procedural Generation — Guide Complet

Ce skill couvre la génération procédurale de contenu (PCG) pour jeux vidéo. À charger pour toute tâche impliquant des algorithmes de génération automatique de niveaux, terrains, textures, ou structures.

---

## 1. Bruit (Noise) — Fondations du PCG

### Bruit de Perlin (Classique)

```csharp
// Unity — Perlin Noise 2D
public static class Bruit
{
    public static float Perlin2D(float x, float y, float scale = 1.0f)
    {
        return Mathf.PerlinNoise(x * scale, y * scale);
    }
    
    // Octaves (multifractal)
    public static float OctaveNoise(float x, float y, int octaves = 4, float persistence = 0.5f)
    {
        float value = 0f;
        float amplitude = 1f;
        float frequency = 1f;
        float maxValue = 0f;
        
        for (int i = 0; i < octaves; i++)
        {
            value += Mathf.PerlinNoise(x * frequency, y * frequency) * amplitude;
            maxValue += amplitude;
            amplitude *= persistence;
            frequency *= 2f;
        }
        
        return value / maxValue;
    }
}
```

### Bruit de Simplex (Godot)

```gdscript
# Godot — Simplex Noise avec FastNoiseLite
extends Node

var noise := FastNoiseLite.new()

func _ready() -> void:
    noise.seed = randi()
    noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
    noise.fractal_type = FastNoiseLite.FRACTAL_FBM
    noise.fractal_octaves = 4
    noise.fractal_gain = 0.5
    noise.fractal_lacunarity = 2.0

func get_height(x: float, z: float) -> float:
    return noise.get_noise_2d(x, z) * 20.0 # scale
```

### Bruit de Voronoi (Worley)

```python
# Python — Voronoi Noise (cellules, utiles pour cavernes)
import numpy as np
from scipy.spatial import KDTree

def voronoi_noise(width: int, height: int, points_count: int = 50) -> np.ndarray:
    points = np.random.rand(points_count, 2) * [width, height]
    tree = KDTree(points)
    
    grid = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            dist, idx = tree.query([x, y])
            grid[y, x] = dist / max(width, height)  # normalize
    return grid
```

---

## 2. Génération de Terrain (Heightmap)

### Heightmap + Coloration par hauteur

```gdscript
# Godot — Génération de terrain procédural
extends MeshInstance3D

@export var taille := 100
@export var resolution := 128
@export var hauteur_max := 20.0
@export var seed := 42

func generer_terrain() -> void:
    var noise := FastNoiseLite.new()
    noise.seed = seed
    noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
    noise.fractal_octaves = 6
    noise.fractal_gain = 0.5
    
    var st = SurfaceTool.new()
    st.begin(Mesh.PRIMITIVE_TRIANGLES)
    
    var step := taille / float(resolution)
    
    for z in range(resolution):
        for x in range(resolution):
            var wx := x * step - taille / 2.0
            var wz := z * step - taille / 2.0
            var h := noise.get_noise_2d(wx, wz) * hauteur_max
            
            # Ajouter un lac au centre
            var dist_centre := Vector2(wx, wz).length()
            if dist_centre < 10.0:
                h = -1.0  # fond de lac
            
            # Vertex
            st.add_vertex(Vector3(wx, h, wz))
    
    # Triangles (quad mesh)
    for z in range(resolution - 1):
        for x in range(resolution - 1):
            var i0 := z * resolution + x
            var i1 := i0 + 1
            var i2 := (z + 1) * resolution + x
            var i3 := i2 + 1
            st.add_index(i0); st.add_index(i1); st.add_index(i2)
            st.add_index(i1); st.add_index(i3); st.add_index(i2)
    
    st.generate_normals()
    mesh = st.commit()
```

### Coloration par hauteur et pente

```gdscript
# Dans le même script, après generate_normals
func colorer_terrain(st: SurfaceTool, heightmap: PackedFloat32Array) -> void:
    for i in range(heightmap.size()):
        var h = heightmap[i]
        var color: Color
        
        if h < -1.0:      color = Color(0.2, 0.4, 0.8)  # Eau
        elif h < 2.0:     color = Color(0.6, 0.8, 0.3)  # Herbe
        elif h < 5.0:     color = Color(0.4, 0.6, 0.2)  # Forêt
        elif h < 10.0:    color = Color(0.5, 0.4, 0.3)  # Roche
        else:             color = Color(0.9, 0.9, 0.9)  # Neige
        
        st.set_color(color)
```

---

## 3. Génération de Donjons (BSP + Rooms)

### BSP (Binary Space Partition) Dungeon

```python
import random
from dataclasses import dataclass

@dataclass
class Room:
    x: int; y: int; w: int; h: int

@dataclass
class BSPNode:
    x: int; y: int; w: int; h: int
    left: 'BSPNode' = None
    right: 'BSPNode' = None
    room: Room = None

def split_node(node: BSPNode, min_size: int = 8):
    if node.w < min_size * 2 or node.h < min_size * 2:
        return
    
    split_h = random.choice([True, False])
    if split_h and node.w >= min_size * 2:
        split = random.randint(min_size, node.w - min_size)
        node.left = BSPNode(node.x, node.y, split, node.h)
        node.right = BSPNode(node.x + split, node.y, node.w - split, node.h)
    elif node.h >= min_size * 2:
        split = random.randint(min_size, node.h - min_size)
        node.left = BSPNode(node.x, node.y, node.w, split)
        node.right = BSPNode(node.x, node.y + split, node.w, node.h - split)
    else:
        return
    
    split_node(node.left, min_size)
    split_node(node.right, min_size)

def create_rooms(node: BSPNode, padding: int = 1):
    if node.left or node.right:
        if node.left: create_rooms(node.left, padding)
        if node.right: create_rooms(node.right, padding)
    else:
        # Room dans la feuille
        margin = 2
        w = random.randint(margin, node.w - margin * 2)
        h = random.randint(margin, node.h - margin * 2)
        x = node.x + random.randint(margin, node.w - w - margin)
        y = node.y + random.randint(margin, node.h - h - margin)
        node.room = Room(x, y, w, h)

def connect_rooms(node: BSPNode) -> list[tuple]:
    """Connecte les pièces avec des couloirs"""
    corridors = []
    if node.left and node.right:
        l_rooms = get_rooms(node.left)
        r_rooms = get_rooms(node.right)
        if l_rooms and r_rooms:
            r1 = random.choice(l_rooms)
            r2 = random.choice(r_rooms)
            # L-corridor
            cx = (r1.x + r1.w // 2 + r2.x + r2.w // 2) // 2
            corridors.append((r1.x + r1.w // 2, r1.y + r1.h // 2, cx, r1.y + r1.h // 2))
            corridors.append((cx, r1.y + r1.h // 2, cx, r2.y + r2.h // 2))
            corridors.append((cx, r2.y + r2.h // 2, r2.x + r2.w // 2, r2.y + r2.h // 2))
        if node.left: corridors.extend(connect_rooms(node.left))
        if node.right: corridors.extend(connect_rooms(node.right))
    return corridors

def get_rooms(node: BSPNode) -> list[Room]:
    if node.room: return [node.room]
    rooms = []
    if node.left: rooms.extend(get_rooms(node.left))
    if node.right: rooms.extend(get_rooms(node.right))
    return rooms
```

---

## 4. Wave Function Collapse (WFC)

### WFC — Algorithme de base

```python
import random
from collections import Counter

class WFC:
    """Wave Function Collapse — génération de tuiles contrainte"""
    
    def __init__(self, width: int, height: int, tiles: list[str], rules: dict):
        self.width = width
        self.height = height
        self.tiles = tiles  # ['A', 'B', 'C', ...]
        self.rules = rules  # {'A': {'up': ['B', 'C'], 'down': ['A'], ...}}
        self.grid = [[set(tiles) for _ in range(width)] for _ in range(height)]
    
    def run(self) -> list[list[str]]:
        while not self.is_collapsed():
            x, y = self.find_lowest_entropy()
            if x is None:
                break  # Contradiction → reset
            self.collapse(x, y)
            self.propagate(x, y)
        return self.extract_grid()
    
    def find_lowest_entropy(self) -> tuple[int, int] | None:
        min_entropy = float('inf')
        result = None
        for y in range(self.height):
            for x in range(self.width):
                entropy = len(self.grid[y][x])
                if entropy > 1 and entropy < min_entropy:
                    # Sous-pondérer les cases avec peu de voisins
                    neighbors = self.count_neighbors(x, y)
                    score = entropy - 0.1 * neighbors
                    if score < min_entropy:
                        min_entropy = score
                        result = (x, y)
        return result
    
    def collapse(self, x: int, y: int) -> None:
        # Choisir une tuile pondérée par les voisins déjà placés
        options = list(self.grid[y][x])
        weights = [self.get_weight(x, y, t) for t in options]
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
            self.grid[y][x] = {random.choices(options, weights=weights)[0]}
        else:
            self.grid[y][x] = {random.choice(options)}
    
    def propagate(self, x: int, y: int) -> None:
        stack = [(x, y)]
        while stack:
            cx, cy = stack.pop()
            current = self.grid[cy][cx]
            if len(current) == 1:
                tile = list(current)[0]
                for dx, dy, direction in [(0, -1, 'up'), (0, 1, 'down'), (-1, 0, 'left'), (1, 0, 'right')]:
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        allowed = self.rules.get(tile, {}).get(direction, self.tiles)
                        before = len(self.grid[ny][nx])
                        self.grid[ny][nx] &= set(allowed)
                        if len(self.grid[ny][nx]) < before:
                            stack.append((nx, ny))
    
    def is_collapsed(self) -> bool:
        return all(len(cell) == 1 for row in self.grid for cell in row)
    
    def count_neighbors(self, x: int, y: int) -> int:
        count = 0
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if len(self.grid[ny][nx]) == 1:
                    count += 1
        return count
    
    def get_weight(self, x: int, y: int, tile: str) -> float:
        # Poids basé sur la fréquence d'apparition des voisins
        weight = 1.0
        for dx, dy, direction in [(0, -1, 'up'), (0, 1, 'down'), (-1, 0, 'left'), (1, 0, 'right')]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                neighbors = self.grid[ny][nx]
                allowed = self.rules.get(tile, {}).get(direction, [])
                overlap = len(neighbors & set(allowed))
                if overlap == 0:
                    weight *= 0.1
        return weight
    
    def extract_grid(self) -> list[list[str]]:
        return [[list(cell)[0] for cell in row] for row in self.grid]
```

---

## 5. Cellular Automata (Cavernes)

```python
import numpy as np

def generate_cave(width: int, height: int, fill_prob: float = 0.45, 
                  iterations: int = 5, wall_threshold: int = 5) -> np.ndarray:
    """Génère des cavernes style Spelunky via automates cellulaires"""
    
    # Initialisation aléatoire
    grid = np.random.rand(height, width) < fill_prob
    
    for _ in range(iterations):
        new_grid = grid.copy()
        for y in range(height):
            for x in range(width):
                # Compter les murs voisins (Moore neighborhood)
                walls = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if grid[ny, nx]:
                                walls += 1
                        else:
                            walls += 1  # Bord = mur
                
                # Règle: mur devient vide si < 4 voisins murs
                # Vide devient mur si >= 5 voisins murs
                if grid[y, x]:
                    new_grid[y, x] = walls >= wall_threshold - 1
                else:
                    new_grid[y, x] = walls >= wall_threshold
        
        grid = new_grid
    
    return grid
```

---

## 6. L-Systems (Plantes Procédurales)

```python
import turtle
import random

class LSystem:
    """L-System pour génération de plantes et fractales"""
    
    def __init__(self, axiom: str, rules: dict, angle: float = 25.0):
        self.axiom = axiom
        self.rules = rules
        self.angle = angle
    
    def generate(self, iterations: int) -> str:
        result = self.axiom
        for _ in range(iterations):
            result = ''.join(self.rules.get(c, c) for c in result)
        return result
    
    def draw(self, instructions: str, segment_length: int = 10) -> None:
        stack = []
        turtle.speed(0)
        turtle.left(90)
        
        for cmd in instructions:
            if cmd == 'F':  # Avancer
                turtle.forward(segment_length)
            elif cmd == 'f':  # Avancer sans tracer
                turtle.penup()
                turtle.forward(segment_length)
                turtle.pendown()
            elif cmd == '+':  # Tourner à gauche
                turtle.left(self.angle + random.uniform(-5, 5))
            elif cmd == '-':  # Tourner à droite
                turtle.right(self.angle + random.uniform(-5, 5))
            elif cmd == '[':  # Push
                stack.append((turtle.position(), turtle.heading()))
            elif cmd == ']':  # Pop
                pos, heading = stack.pop()
                turtle.penup()
                turtle.goto(pos)
                turtle.setheading(heading)
                turtle.pendown()

# Exemple: Arbre fractal
axiom = "F"
rules = {
    "F": "FF+[+F-F-F]-[-F+F+F]"
}
lsys = LSystem(axiom, rules, angle=22.5)
instructions = lsys.generate(5)  # 5 itérations
```

---

## 7. PCG pour Textures (Material Generation)

```python
import numpy as np
from PIL import Image

def generate_marble_texture(width: int, height: int, seed: int = 42) -> Image:
    """Génération procédurale de texture marbre"""
    np.random.seed(seed)
    x = np.linspace(0, 6, width)
    y = np.linspace(0, 6, height)
    X, Y = np.meshgrid(x, y)
    
    # Bruit de base
    noise = np.sin(X * 3 + Y * 2 + np.sin(X * 5 + Y * 3) * 2)
    
    # Veines de marbre
    veins = np.sin(noise * 4 + X * 0.5)
    veins = (veins - veins.min()) / (veins.max() - veins.min())
    
    # Couleur (blanc/gris/beige)
    r = (200 + veins * 55).astype(np.uint8)
    g = (190 + veins * 50).astype(np.uint8)
    b = (170 + veins * 45).astype(np.uint8)
    
    return Image.fromarray(np.stack([r, g, b], axis=2), 'RGB')

def generate_wood_texture(width: int, height: int) -> Image:
    """Génération procédurale de texture bois"""
    x = np.arange(width)
    y = np.arange(height)
    X, Y = np.meshgrid(x, y)
    
    # Cercles concentriques bruités
    rings = np.sqrt((X - width/2)**2 + (Y - height/2)**2) / 20
    rings += np.random.randn(height, width) * 2  # bruit
    rings = np.sin(rings * np.pi * 2)
    rings = (rings - rings.min()) / (rings.max() - rings.min())
    
    r = (80 + rings * 100).astype(np.uint8)
    g = (50 + rings * 80).astype(np.uint8)
    b = (20 + rings * 40).astype(np.uint8)
    
    return Image.fromarray(np.stack([r, g, b], axis=2), 'RGB')
```

---

## 8. Génération de Quêtes et Contenu Narratif

```python
import random

class QuestGenerator:
    """Génération procédurale de quêtes RPG"""
    
    TEMPLATES = {
        "kill": [
            "{count} {monster} infestent {location}. Tue-les pour {reward}.",
            "Un {monster} terrorise {location}. Élimine-le pour {reward}.",
        ],
        "fetch": [
            "Rapporte {item} de {location} pour {npc}.",
            "{item} a été perdu dans {location}. Retrouve-le pour {reward}.",
        ],
        "escort": [
            "Escorte {npc} à travers {location} jusqu'à {destination}.",
        ],
        "delivery": [
            "Livraison urgente: apporte {item} à {npc} à {location}.",
        ]
    }
    
    def __init__(self):
        self.monsters = ["gobelins", "loups", "squelettes", "bandits", "rats géants", "araignées"]
        self.locations = ["la forêt sombre", "les ruines antiques", "la caverne oubliée", 
                          "le marais empoisonné", "le donjon maudit", "les montagnes brumeuses"]
        self.npcs = ["le vieux sage", "le forgeron", "la prêtresse", "le marchand", "le capitaine"]
        self.items = ["un artefact ancien", "une potion rare", "un parchemin scellé", 
                      "une gemme enchantée", "des provisions"]
    
    def generate(self, quest_type: str = None) -> dict:
        if not quest_type:
            quest_type = random.choice(list(self.TEMPLATES.keys()))
        
        template = random.choice(self.TEMPLATES[quest_type])
        quest = {
            "type": quest_type,
            "monster": random.choice(self.monsters),
            "location": random.choice(self.locations),
            "npc": random.choice(self.npcs),
            "item": random.choice(self.items),
            "count": random.randint(3, 12),
            "reward": f"{random.randint(50, 500)} pièces d'or",
            "destination": random.choice(self.locations),
            "description": "",
        }
        
        quest["description"] = template.format(**quest)
        quest["difficulty"] = random.choice(["facile", "moyen", "difficile"])
        quest["xp_reward"] = quest["count"] * random.randint(10, 50)
        
        return quest
```

---

## 9. Optimisation du PCG

### Caching et Seed Control

```python
# Toujours exposer la seed pour reproductibilité
class PCGManager:
    def __init__(self, seed: int = None):
        self.seed = seed or random.randint(0, 2**32 - 1)
        self._rng = random.Random(self.seed)
    
    def generate_terrain(self, region: str) -> np.ndarray:
        # Seed stable par région (même terrain à chaque fois)
        region_seed = hash(f"{self.seed}:{region}") % 2**32
        return self._generate_heightmap(region_seed)
    
    def generate_dungeon(self, seed: int) -> dict:
        rng = random.Random(seed)
        # ... génération avec rng au lieu de random
```

### LOD pour terrains procéduraux
- **Low res** : 32x32 heightmap pour la minimap
- **Medium res** : 128x128 pour le lointain
- **High res** : 512x512 pour le proche (streaming par chunks)

---

## 10. Pièges Courants

- **Seed non reproductible** : `random.seed(time.time())` → toujours exposer un seed fixe
- **Terrain trop lisse** : trop d'octaves de bruit → landscape plat
- **Donjons sans connexion** : BSP rooms non connectées → inaccessible
- **WFC contradiction** : règles de tuiles impossibles → reset et retry
- **Performance PCG runtime** : générer au chargement, pas en temps réel
- **Contenu vide** : PCG sans contraintes de design → boring maps
- **Seed identique** : hash collision → mêmes donjons à chaque partie