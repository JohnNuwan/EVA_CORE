---
name: robot-path-planning
description: Planification de trajectoires robotiques — A*, RRT, PRM, Dijkstra, D*, trajectory optimization, time parameterization, collision avoidance
---

# Robot Path Planning — Planification de Chemins et Trajectoires

## Quand l'utilisateur
Quand l'utilisateur demande de planifier un chemin pour robot mobile ou manipulateur, d'implémenter A*/RRT/Dijkstra, de lisser une trajectoire, d'optimiser le temps de parcours, ou d'éviter des obstacles.

## Taxonomie des Planificateurs

| Algorithme | Graphe | Optimal | Complet | Espace | Usage |
|-----------|--------|---------|---------|--------|-------|
| **Dijkstra** | Oui | Oui | Oui | Discret | Chemin le plus court (poids positifs) |
| **A*** | Oui | Oui | Oui | Discret | Standard navigation (avec heuristique) |
| **D* / D* Lite** | Oui | Oui | Oui | Dynamique | Replanification (environnement changeant) |
| **PRM** | Routage | Non | Probable | Continu | Multi-requêtes, environnements statiques |
| **RRT** | Arbre | Non | Probable | Continu | Haute dimension, temps réel |
| **RRT*** | Arbre | Oui asymptotique | Probable | Continu | Converge vers optimal |
| **FMT*** | Arbre | Oui asymptotique | Probable | Continu | Convergence plus rapide |
| **CHOMP** | Optimisation | Local | Gradient | Continu | Lissage trajectoire |
| **STOMP** | Optimisation | Local | Stochastique | Continu | Robustesse bruit |
| **TrajOpt** | SQP | Local | Contraintes | Continu | Industrie, contraintes strictes |

## A* — Recherche Heuristique (Grid)

```python
import heapq
import numpy as np

class AStar:
    """A* sur grille d'occupation binaire"""
    def __init__(self, grid, resolution=0.05):
        self.grid = grid  # np.array: 0=libre, 1=occupé
        self.res = resolution
        self.h, self.w = grid.shape

    def heuristic(self, a, b):
        """Distance euclidienne (admissible, donc optimale)"""
        return np.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

    def get_neighbors(self, node):
        """8-connectivité pour grille"""
        x, y = node
        neighbors = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1),
                       (-1,-1),(-1,1),(1,-1),(1,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.h and 0 <= ny < self.w:
                if self.grid[nx, ny] == 0:  # libre
                    # Coût : 1 pour orthogonal, √2 pour diagonal
                    cost = 1.0 if dx==0 or dy==0 else np.sqrt(2)
                    neighbors.append(((nx, ny), cost))
        return neighbors

    def plan(self, start, goal):
        """start, goal : (x, y) en mètres → conversion en indices grille"""
        start_idx = (int(start[0]/self.res), int(start[1]/self.res))
        goal_idx = (int(goal[0]/self.res), int(goal[1]/self.res))

        open_set = []
        heapq.heappush(open_set, (0.0, start_idx))
        came_from = {}
        g_score = {start_idx: 0.0}
        f_score = {start_idx: self.heuristic(start_idx, goal_idx)}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal_idx:
                # Reconstruction du chemin
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_idx)
                path.reverse()
                # Conversion indices → mètres
                path_meters = [
                    (p[0]*self.res, p[1]*self.res) for p in path
                ]
                return path_meters

            for neighbor, cost in self.get_neighbors(current):
                tentative_g = g_score[current] + cost
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.heuristic(neighbor, goal_idx)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return None  # Aucun chemin trouvé
```

### A* avec JPS (Jump Point Search)
Accélération de 10-100× sur grilles uniformes : saute les régions sans décision via symétries.

```python
class JumpPointSearch(AStar):
    """A* + JPS : ignore les nœuds redondants dans les espaces ouverts"""
    def get_neighbors(self, node, parent):
        """JPS : successeurs = seuls les Jump Points"""
        neighbors = []
        for dx, dy in self.prune_directions(node, parent):
            jp = self.jump(node, dx, dy, goal_idx)
            if jp is not None:
                # Coût Manhattan du nœud au jump point
                cost = abs(jp[0]-node[0]) + abs(jp[1]-node[1])
                neighbors.append((jp, cost))
        return neighbors

    def jump(self, node, dx, dy, goal):
        """Saute récursivement jusqu'à trouver un Jump Point"""
        nx, ny = node[0]+dx, node[1]+dy
        if not (0 <= nx < h and 0 <= ny < w) or grid[nx, ny] != 0:
            return None
        if (nx, ny) == goal:
            return (nx, ny)
        # Forced neighbor check — condition de Jump Point
        if dx != 0 and dy != 0:  # diagonale
            if (grid[nx-dx, ny] == 1 and grid[nx, ny-dy] == 0) or \
               (grid[nx, ny-dy] == 1 and grid[nx-dx, ny] == 0):
                return (nx, ny)
        # Récursion
        return self.jump((nx, ny), dx, dy, goal)
```

## RRT (Rapidly-exploring Random Tree)

```python
class RRT:
    """Rapidly-exploring Random Tree — espace continu"""
    class Node:
        def __init__(self, x, y, parent=None):
            self.x = x
            self.y = y
            self.parent = parent

    def __init__(self, obstacle_check, bounds, max_steps=500, step_size=0.5):
        self.obstacle_free = obstacle_check  # fn(x,y) → bool
        self.bounds = bounds  # [x_min, x_max, y_min, y_max]
        self.max_steps = max_steps
        self.step_size = step_size

    def plan(self, start, goal):
        self.tree = [self.Node(start[0], start[1])]

        for _ in range(self.max_steps):
            # Échantillonnage aléatoire (biased vers goal)
            if np.random.random() < 0.1:
                rand_node = self.Node(goal[0], goal[1])
            else:
                rand = np.random.uniform(
                    [self.bounds[0], self.bounds[2]],
                    [self.bounds[1], self.bounds[3]]
                )
                rand_node = self.Node(rand[0], rand[1])

            # Nœud le plus proche dans l'arbre
            nearest = self.nearest(rand_node)

            # Steer : avancer du step_size vers rand_node
            dx = rand_node.x - nearest.x
            dy = rand_node.y - nearest.y
            dist = np.sqrt(dx**2 + dy**2)
            if dist < 1e-6:
                continue
            theta = np.arctan2(dy, dx)
            new_x = nearest.x + self.step_size * np.cos(theta)
            new_y = nearest.y + self.step_size * np.sin(theta)

            if not self.obstacle_free(new_x, new_y):
                continue
            # Vérifier que le segment nearest→new est sans obstacle
            if not self.segment_free(nearest.x, nearest.y, new_x, new_y):
                continue

            new_node = self.Node(new_x, new_y, nearest)
            self.tree.append(new_node)

            # Vérifier si on a atteint le goal (dans un rayon)
            if dist_to_goal(new_x, new_y, goal) < self.step_size:
                if self.segment_free(new_x, new_y, goal[0], goal[1]):
                    goal_node = self.Node(goal[0], goal[1], new_node)
                    return self.extract_path(goal_node)

        return None

    def nearest(self, node):
        """Plus proche voisin dans l'arbre"""
        return min(self.tree,
                   key=lambda n: (n.x-node.x)**2 + (n.y-node.y)**2)

    def segment_free(self, x1, y1, x2, y2, N=10):
        """Vérifie que le segment [p1, p2] est libre (discrétisé)"""
        for t in np.linspace(0, 1, N):
            x = x1 + t*(x2-x1)
            y = y1 + t*(y2-y1)
            if not self.obstacle_free(x, y):
                return False
        return True

    def extract_path(self, goal_node):
        path = []
        node = goal_node
        while node is not None:
            path.append((node.x, node.y))
            node = node.parent
        path.reverse()
        return path
```

### RRT* — Optimalité Asymptotique
```python
class RRTStar(RRT):
    """RRT* : avec rewiring pour convergence optimale"""
    def __init__(self, obstacle_check, bounds, step_size=0.5,
                 goal_radius=0.2, rewiring_radius=1.0):
        super().__init__(obstacle_check, bounds, step_size=step_size)
        self.goal_radius = goal_radius
        self.rewiring_radius = rewiring_radius
        self.nodes_in_radius = None

    def steer_and_rewire(self, nearest, rand_node):
        new_node = self.steer(nearest, rand_node)
        if not self.obstacle_free(new_node):
            return None

        # Trouver les nœuds dans le voisinage pour rewiring
        nearby = self.nearby_nodes(new_node)
        # Meilleur parent (coût minimal)
        best_parent = nearest
        best_cost = self.cost(nearest) + self.dist(nearest, new_node)
        for n in nearby:
            if self.segment_free(n.x, n.y, new_node.x, new_node.y):
                new_cost = self.cost(n) + self.dist(n, new_node)
                if new_cost < best_cost:
                    best_cost = new_cost
                    best_parent = n

        new_node.parent = best_parent
        new_node.cost = best_cost

        # Rewire : pour chaque voisin, vérifier si passer par new_node réduit son coût
        for n in nearby:
            if n == best_parent:
                continue
            if self.segment_free(new_node.x, new_node.y, n.x, n.y):
                new_cost = best_cost + self.dist(new_node, n)
                if new_cost < self.cost(n):
                    n.parent = new_node
                    n.cost = new_cost

        return new_node
```

## PRM (Probabilistic Roadmap) — Multi-query

```python
class PRM:
    """Probabilistic Roadmap Method — multi-query"""
    def __init__(self, obstacle_free, bounds, n_samples=500, k_neighbors=10):
        self.obstacle_free = obstacle_free
        self.bounds = bounds
        self.n_samples = n_samples
        self.k = k_neighbors
        self.graph = {}  # node_id → {neighbor_id: distance}
        self.nodes = {}  # node_id → (x, y)

    def build(self):
        """Construction du graphe de routes"""
        nodes = []
        # Échantillonnage aléatoire
        for i in range(self.n_samples):
            x = np.random.uniform(self.bounds[0], self.bounds[1])
            y = np.random.uniform(self.bounds[2], self.bounds[3])
            if self.obstacle_free(x, y):
                nodes.append((x, y))

        self.nodes = {i: n for i, n in enumerate(nodes)}

        # Connexion des k plus proches voisins
        from scipy.spatial import KDTree
        tree = KDTree(nodes)
        self.graph = {i: {} for i in range(len(nodes))}

        for i, (x, y) in enumerate(nodes):
            distances, indices = tree.query([(x, y)], k=min(self.k+1, len(nodes)))
            for dist, j in zip(distances[0], indices[0]):
                if i != j:
                    # Vérifier que le segment est libre
                    xj, yj = nodes[j]
                    if self.segment_free(x, y, xj, yj):
                        self.graph[i][int(j)] = float(dist)
                        self.graph[int(j)][i] = float(dist)

    def plan(self, start, goal):
        """Recherche A* sur le graphe PRM"""
        # Ajouter start et goal au graphe
        # ... (connecter aux plus proches voisins)
        # A* sur self.graph
        path = self.astar_on_graph(start_id, goal_id)
        return [(self.nodes[i][0], self.nodes[i][1]) for i in path]
```

## Planification pour Bras Manipulateur (Configuration Space)

### Sampling-based en C-Space
```python
def plan_manipulator_arm(start_q, goal_q, collision_fn, bounds):
    """
    Planifie dans l'espace de configuration du bras
    start_q, goal_q : vecteurs 6-DOF
    collision_fn(q) → bool (vrai si collision)
    """
    # RRT dans C-Space (articulaire)
    def obstacle_free_arm(q):
        # Forward kinematics → position des links
        # Vérifier self-collision + collision monde pour chaque link
        return not collision_fn(q)

    rrt = RRT(obstacle_free_arm, bounds, step_size=0.2)
    path_q = rrt.plan(start_q, goal_q)
    return path_q  # séquence de [q1, ..., q6]
```

### Pilz Industrial Planner (MoveIt)
```python
from pilz_industrial_motion import *

# PTP : Point-to-Point (mouvement articulaire rapide)
ptp = PTP()
ptp.set_target_joints([0.0, -1.57, 1.57, 0.0, 0.0, 0.0])

# LIN : Linear (trajectoire cartésienne en ligne droite)
lin = LIN()
lin.set_target_pose(Pose(0.5, 0.2, 0.3, 0, 0, 0))

# CIRC : Circular (interpolation circulaire)
circ = CIRC()
circ.set_goal(Pose(0.6, 0.3, 0.4, 0, 0, 0), Pose(0.55, 0.25, 0.35, 0, 0, 0))
```

## Trajectory Optimization (CHOMP / TrajOpt)

### CHOMP (Covariant Hamiltonian Optimization for Motion Planning)
```python
class CHOMP:
    """
    Minimise : U(ξ) = η_cost * U_obst(ξ) + λ * U_smooth(ξ)
    ξ : trajectoire discrétisée (N × n_dof)
    """
    def __init__(self, robot, n_waypoints=100, eta=100.0, lam=1.0):
        self.robot = robot
        self.N = n_waypoints
        self.eta = eta      # poids obstacles
        self.lam = lam      # poids lissage

    def smoothness_cost(self, xi):
        """∑ ||ξ_{i+1} - ξ_i||² + ||ξ_{i-1} - ξ_i||² (finite differences)"""
        diff = xi[1:] - xi[:-1]
        accel = xi[2:] - 2*xi[1:-1] + xi[:-2]
        return np.sum(diff**2) / 2.0 + np.sum(accel**2) / 2.0

    def obstacle_cost(self, xi):
        """Coût basé sur la distance aux obstacles"""
        cost = 0.0
        for i in range(xi.shape[0]):
            FK = self.robot.forward_kinematics(xi[i])
            # Somme des distances minimales de chaque link aux obstacles
            # c(d) = η * exp(-d²/σ²) pour d < seuil
            cost += self.obstacle_distance_cost(FK)
        return cost

    def optimize(self, xi_init, max_iter=50):
        """Gradient descent sur la trajectoire complète"""
        xi = xi_init.copy()
        for _ in range(max_iter):
            grad_obs = self.obstacle_gradient(xi)
            grad_smooth = self.smoothness_gradient(xi)
            gradient = self.eta * grad_obs + self.lam * grad_smooth
            # Step size backtracking line search
            xi = xi - 0.1 * gradient
        return xi
```

## Time Parameterization (Trajectory Timing)

```python
class TimeParameterization:
    """
    Ajoute le temps à un chemin géométrique pour former une trajectoire
    Respecte les limites de vélocité, accélération, jerk
    """
    def __init__(self, max_vel, max_acc, max_jerk=None):
        self.v_max = max_vel
        self.a_max = max_acc
        self.j_max = max_jerk

    def trapezoidal_profile(self, path, v_max, a_max):
        """
        Profil de vitesse trapézoïdal (accélération constante)
        Retourne : temps, position, vitesse
        """
        # Distance totale du chemin
        total_dist = sum(np.linalg.norm(path[i+1]-path[i]) for i in range(len(path)-1))

        # Temps d'accélération
        t_acc = v_max / a_max
        d_acc = 0.5 * a_max * t_acc**2

        if 2 * d_acc <= total_dist:
            # Phase de croisière
            t_cruise = (total_dist - 2*d_acc) / v_max
            t_total = 2*t_acc + t_cruise
        else:
            # Pas d'atteinte de v_max (triangle)
            t_acc = np.sqrt(total_dist / a_max)
            t_total = 2*t_acc

        return t_total

    def cubic_spline(self, waypoints, times):
        """Interpolation cubique par morceaux"""
        from scipy.interpolate import CubicSpline
        # Pour chaque joint (n_dof)
        trajectories = []
        for j in range(waypoints.shape[1]):
            cs = CubicSpline(times, waypoints[:, j], bc_type='clamped')
            # Dérivées
            q = cs  # position
            v = cs.derivative(1)  # vélocité
            a = cs.derivative(2)  # accélération
            trajectories.append({
                'joint': j,
                'position': lambda t, cs=cs: cs(t),
                'velocity': lambda t, v=v: v(t),
                'acceleration': lambda t, a=a: a(t),
            })
        return trajectories
```

## Collision Avoidance — Méthodes

### Potential Fields (Champs de Potentiel)
```python
class PotentialField:
    """Champ de potentiel : attractif (goal) + répulsif (obstacles)"""
    def __init__(self, K_att=1.0, K_rep=100.0, d0=0.5):
        self.K_att = K_att
        self.K_rep = K_rep
        self.d0 = d0  # distance influence répulsion

    def attractive(self, robot, goal):
        """F_att = -K_att * (robot - goal)"""
        return -self.K_att * (robot - goal)

    def repulsive(self, robot, obstacles):
        """F_rep = K_rep * (1/d - 1/d0) * (1/d²) * (x - x_obs)/d """
        F = np.zeros(2)
        for obs in obstacles:
            d = np.linalg.norm(robot - obs)
            if d < self.d0 and d > 0.01:
                direction = (robot - obs) / d
                F += self.K_rep * (1/d - 1/self.d0) * (1/d**2) * direction
        return F

    def total_force(self, robot, goal, obstacles):
        return self.attractive(robot, goal) + self.repulsive(robot, obstacles)
```

### VO (Velocity Obstacles) — Dynamique multi-agent
```python
class VelocityObstacle:
    """Évitemment de collision basé sur les cônes de vélocité"""
    def compute_vo(self, robot_pos, robot_vel, robot_radius,
                   obstacle_pos, obstacle_vel, obstacle_radius):
        """Calcule le cône de vélocités interdites"""
        rel_pos = obstacle_pos - robot_pos
        rel_vel = obstacle_vel - robot_vel
        combined_radius = robot_radius + obstacle_radius

        # Angle du cône
        dist = np.linalg.norm(rel_pos)
        if dist < 1e-6:
            return np.pi  # tout est interdit

        angle_to_obs = np.arctan2(rel_pos[1], rel_pos[0])
        cone_half_angle = np.arcsin(combined_radius / dist)

        return angle_to_obs - cone_half_angle, angle_to_obs + cone_half_angle
```

## Pièges et Bonnes Pratiques

- **A* sur grille trop fine** : 1000×1000 → 10⁶ nœuds → A* lent. Utiliser JPS (Jump Point Search) pour les grilles uniformes, ou multi-resolution A*.
- **RRT dans des couloirs étroits** : RRT standard a du mal avec les passages étroits (narrow passages). Solution : RRT avec bridge test, Gaussian sampling, ou PRM.
- **Planification articulaire vs cartésien** : préférer la planification dans l'espace articulaire (C-Space) pour les bras — elle évite les singularités et les collisions de manière naturelle. Le cartésien (task space) est utile pour l'usinage (maintien de l'orientation).
- **Collision checking coûteux** : chaque validation de collision = FK + intersection géométrique → bottleneck. Utiliser des arbres BVH (FCL, OBB) et des approximations de collision (bounding spheres). Precompute C-Space.
- **Trajectoire non-Continue** : sans time parameterization, la vitesse/accélération peut être infinie aux waypoints. Toujours ajouter un profil de vitesse (trapèze, cubic spline, quintic).
- **Local minima (potentiel fields)** : les champs de potentiel peuvent être bloqués dans des minima locaux. Solution : utiliser la navigation function (NF1, harmonic potential) qui garantit zéro minimum local.
- **Replanification** : pour environnements dynamiques, D* Lite > A* recomplet. RRT peut être réparé avec ERRT (error detection and recovery).

## Références

- LaValle, S.M. (2006). *Planning Algorithms*. Cambridge University Press. ISBN 978-0521862059. Disponible en ligne : http://planning.cs.uiuc.edu/
- Choset, H. et al. (2005). *Principles of Robot Motion*. MIT Press. ISBN 978-0262033275
- Karaman, S. & Frazzoli, E. (2011). Sampling-based Algorithm for Optimal Motion Planning. *Int. J. Robotics Research*, 30(7), 846-894.
- Ratliff, N. et al. (2009). CHOMP: Gradient Optimization Techniques for Efficient Motion Planning. *IEEE ICRA 2009*.
- Schulman, J. et al. (2014). Motion Planning with Sequential Convex Optimization and Convex Collision Checking. *Int. J. Robotics Research*, 33(9), 1251-1270.
- Harabor, D. & Grastien, A. (2011). Online Graph Pruning for Pathfinding On Grid Maps. *AAAI 2011*.
- Quinlan, S. & Khatib, O. (1993). Elastic Bands: Connecting Path Planning and Control. *IEEE ICRA 1993*.