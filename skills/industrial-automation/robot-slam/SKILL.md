---
name: robot-slam
description: SLAM (Simultaneous Localization and Mapping) — filtres particulaires, graph SLAM, EKF, FastSLAM, loop closure, ROS2 Cartographer, GTSAM
---

# SLAM — Localisation et Cartographie Simultanées

## Quand l'utilisateur
Quand l'utilisateur demande de faire de la localisation de robot mobile, de la cartographie SLAM, du loop closure, de configurer Cartographer, GMapping, ou CORB-SLAM.

## Fondements Mathématiques

### Problème SLAM
Estimer conjointement :
- **x₁:T** : trajectoire du robot (poses)
- **m** : carte de l'environnement (landmarks / grille d'occupation)

À partir de :
- **u₁:T** : odométrie (mesures de commande)
- **z₁:T** : observations (LiDAR, caméra, sonar)

```
P(x₁:T, m | z₁:T, u₁:T)   ← distribution conjointe
```

### Modèles
```
Mouvement : x_t = f(x_{t-1}, u_t) + w_t    w_t ~ N(0, Q_t)
Observation : z_t = h(x_t, m) + v_t         v_t ~ N(0, R_t)
```

## Classification des Approches SLAM

| Approche | Représentation | Complexité | Robustesse | Usage |
|----------|---------------|------------|------------|-------|
| **EKF-SLAM** | Gaussienne | O(n²) | Faible | Petits espaces, peu de landmarks |
| **FastSLAM** | PF + EKF | O(n log n) | Moyenne | Robotique indoor |
| **Graph SLAM** | Graphe factoriel | O(n²)~O(n³) | Haute | Standard moderne |
| **iSAM2** | Graphe incrémental | O(n) | Très haute | SLAM temps réel |
| **Visual SLAM** | ORB features | O(n) | Variable | Drones, voitures |

## EKF SLAM (Extended Kalman Filter)

### Algorithme
```python
import numpy as np

class EKFSLAM:
    """
    État : x = [x_r, y_r, θ_r, m₁_x, m₁_y, m₂_x, m₂_y, ...]^T
    """
    def __init__(self, initial_pose):
        # État initial : pose robot + 0 landmarks
        self.mu = np.array([initial_pose[0], initial_pose[1], initial_pose[2]])
        self.Sigma = np.eye(3) * 0.01  # covariance initiale
        self.n_landmarks = 0

    def predict(self, u, dt, Q):
        """u = [v, ω]^T (vitesse linéaire, angulaire)"""
        # Modèle de vélocité (unicycle)
        x, y, theta = self.mu[0], self.mu[1], self.mu[2]
        v, omega = u[0], u[1]

        if abs(omega) > 1e-6:
            x_new = x + v/omega * (np.sin(theta + omega*dt) - np.sin(theta))
            y_new = y + v/omega * (-np.cos(theta + omega*dt) + np.cos(theta))
            theta_new = theta + omega*dt
        else:
            x_new = x + v*dt * np.cos(theta)
            y_new = y + v*dt * np.sin(theta)
            theta_new = theta

        # Jacobienne G_t (3×3)
        G = np.eye(3)
        if abs(omega) > 1e-6:
            G[0, 2] = v/omega * (np.cos(theta + omega*dt) - np.cos(theta))
            G[1, 2] = v/omega * (np.sin(theta + omega*dt) - np.sin(theta))
        else:
            G[0, 2] = -v*dt * np.sin(theta)
            G[1, 2] = v*dt * np.cos(theta)

        # Propagation
        self.mu[:3] = [x_new, y_new, theta_new]
        self.Sigma[:3, :3] = G @ self.Sigma[:3, :3] @ G.T + Q
        # Les landmarks ne bougent pas (covariance inchangée)

    def update(self, z, R, landmark_idx):
        """
        z = [distance, bearing] : observation d'un landmark
        landmark_idx : index du landmark dans l'état (-1 si nouveau)
        """
        x_r, y_r, theta = self.mu[0], self.mu[1], self.mu[2]

        if landmark_idx == -1:
            # Nouveau landmark : initialiser
            r, phi = z[0], z[1]
            mx = x_r + r * np.cos(theta + phi)
            my = y_r + r * np.sin(theta + phi)
            self.mu = np.append(self.mu, [mx, my])
            new_cov = R  # covariance initiale du landmark
            self.Sigma = np.block([
                [self.Sigma, np.zeros((self.Sigma.shape[0], 2))],
                [np.zeros((2, self.Sigma.shape[0])), new_cov]
            ])
            self.n_landmarks += 1
            return

        # Observation d'un landmark existant
        l_idx = 3 + 2 * landmark_idx  # position dans l'état
        mx, my = self.mu[l_idx], self.mu[l_idx+1]

        # Observation prédite
        dx = mx - x_r
        dy = my - y_r
        q = dx**2 + dy**2
        r_pred = np.sqrt(q)
        phi_pred = np.arctan2(dy, dx) - theta

        # Innovation
        z_pred = np.array([r_pred, phi_pred])
        innovation = z - z_pred
        # Normaliser angle
        innovation[1] = np.arctan2(np.sin(innovation[1]), np.cos(innovation[1]))

        # Jacobienne H (2×N)
        H = np.zeros((2, len(self.mu)))
        H[:3, :3] = 0  # dérivée par rapport au robot
        H[0, 0] = -dx/np.sqrt(q)
        H[0, 1] = -dy/np.sqrt(q)
        H[1, 0] = dy/q
        H[1, 1] = -dx/q
        H[1, 2] = -1

        # Dérivée par rapport au landmark
        H[0, l_idx] = dx/np.sqrt(q)
        H[0, l_idx+1] = dy/np.sqrt(q)
        H[1, l_idx] = -dy/q
        H[1, l_idx+1] = dx/q

        # Kalman update
        S = H @ self.Sigma @ H.T + R
        K = self.Sigma @ H.T @ np.linalg.inv(S)
        self.mu = self.mu + K @ innovation
        self.Sigma = (np.eye(len(self.mu)) - K @ H) @ self.Sigma
```

## FastSLAM (Rao-Blackwellized Particle Filter)

```python
class FastSLAM2Particle:
    """Un particule FastSLAM 2.0 : pose robot + N EKF landmarks"""
    def __init__(self, pose, weight=1.0):
        self.pose = pose  # [x, y, θ]
        self.weight = weight
        self.landmarks = {}  # {id: (mu, Sigma)}  # EKF 2×1 + 2×2

class FastSLAM2:
    """
    FastSLAM 2.0 : Rao-Blackwellized PF
    - M particules pour la pose
    - Chaque particule a N EKF indépendants (1 par landmark)
    Complexité : O(M log N) vs O(N²) pour EKF-SLAM
    """
    def __init__(self, n_particles=100):
        self.particles = [FastSLAM2Particle(np.zeros(3)) for _ in range(n_particles)]
        self.n_particles = n_particles

    def motion_update(self, u, dt, Q):
        """Propagation de chaque particule"""
        for p in self.particles:
            # Ajout bruit
            v, omega = u[0] + np.random.normal(0, np.sqrt(Q[0,0])), \
                       u[1] + np.random.normal(0, np.sqrt(Q[1,1]))
            # Modèle unicycle
            if abs(omega) > 1e-6:
                p.pose[0] += v/omega * (np.sin(p.pose[2] + omega*dt) - np.sin(p.pose[2]))
                p.pose[1] += v/omega * (-np.cos(p.pose[2] + omega*dt) + np.cos(p.pose[2]))
                p.pose[2] += omega * dt
            else:
                p.pose[0] += v*dt * np.cos(p.pose[2])
                p.pose[1] += v*dt * np.sin(p.pose[2])

    def observation_update(self, z, R, landmark_id):
        """Mise à jour de chaque particule avec observation"""
        for p in self.particles:
            if landmark_id not in p.landmarks:
                # Nouveau landmark
                r, phi = z[0], z[1]
                mx = p.pose[0] + r * np.cos(p.pose[2] + phi)
                my = p.pose[1] + r * np.sin(p.pose[2] + phi)
                p.landmarks[landmark_id] = (np.array([mx, my]), R)
                p.weight *= 1.0  # poids uniforme
            else:
                # EKF update sur le landmark
                mu_l, Sigma_l = p.landmarks[landmark_id]
                dx = mu_l[0] - p.pose[0]
                dy = mu_l[1] - p.pose[1]
                q = dx**2 + dy**2
                z_pred = np.array([np.sqrt(q), np.arctan2(dy, dx) - p.pose[2]])

                # Innovation
                innovation = z - z_pred
                innovation[1] = np.arctan2(np.sin(innovation[1]), np.cos(innovation[1]))

                # Jacobienne
                H = np.array([
                    [dx/np.sqrt(q), dy/np.sqrt(q)],
                    [-dy/q, dx/q]
                ])
                S = H @ Sigma_l @ H.T + R
                K = Sigma_l @ H.T @ np.linalg.inv(S)

                # Mise à jour poids (importance sampling)
                p.weight *= np.exp(-0.5 * innovation.T @ np.linalg.inv(S) @ innovation)

                # EKF update
                mu_l = mu_l + K @ innovation
                Sigma_l = (np.eye(2) - K @ H) @ Sigma_l
                p.landmarks[landmark_id] = (mu_l, Sigma_l)

    def resample(self):
        """Ré-échantillonnage des particules (systématique)"""
        weights = np.array([p.weight for p in self.particles])
        weights /= np.sum(weights)

        # Échantillonnage systématique (low variance)
        new_particles = []
        N = self.n_particles
        r = np.random.uniform(0, 1/N)
        c = weights[0]
        i = 0
        for j in range(N):
            u = r + j/N
            while u > c:
                i += 1
                c += weights[i]
            # Copie de la particule
            new_particles.append(copy.deepcopy(self.particles[i]))
            new_particles[-1].weight = 1.0/N

        self.particles = new_particles
```

## Graph SLAM

### Formalisme
```
θ* = argmin_θ Σ_t ||g(θ_t, u_t) - θ_{t-1}||²_Qt + Σ_t ||h(θ_t) - z_t||²_Rt
```
Où θ = [x₁, x₂, ..., x_T, m₁, m₂, ..., m_N] est le vecteur de tous les paramètres.

### Construction du Graphe Factoriel
```python
import gtsam  # GTSAM 4.x

class GraphSLAM:
    """
    GTSAM : Georgia Tech Smoothing and Mapping
    Utilise iSAM2 (incremental) ou Levenberg-Marquardt (batch)
    """
    def __init__(self):
        self.graph = gtsam.NonlinearFactorGraph()
        self.initial_estimate = gtsam.Values()
        self.params = gtsam.LevenbergMarquardtParams()
        self.isam = gtsam.ISAM2()

        # Prior sur la première pose
        self.prior_noise = gtsam.noiseModel.Diagonal.Sigmas(np.array([0.01, 0.01, 0.001]))

    def add_odometry(self, pose_key_i, pose_key_j, odometry, noise):
        """Ajoute un facteur d'odométrie entre deux poses"""
        # Odométrie : différence (dx, dy, dθ)
        odom = gtsam.Pose2(odometry[0], odometry[1], odometry[2])
        noise_model = gtsam.noiseModel.Diagonal.Sigmas(noise)
        factor = gtsam.BetweenFactorPose2(pose_key_i, pose_key_j, odom, noise_model)
        self.graph.add(factor)

    def add_landmark_observation(self, pose_key, landmark_key, bearing, range_, noise):
        """Ajoute un facteur d'observation (bearing-range)"""
        noise_model = gtsam.noiseModel.Diagonal.Sigmas(noise)
        # BearingRangeFactor(pose_key, landmark_key, measured_bearing, measured_range, noise)
        factor = gtsam.BearingRangeFactor2D(
            pose_key, landmark_key,
            gtsam.Rot2(np.cos(bearing), np.sin(bearing)),
            range_, noise_model
        )
        self.graph.add(factor)

    def add_loop_closure(self, pose_key_i, pose_key_j, relative_pose, noise):
        """Ajoute une contrainte de boucle fermée"""
        odom = gtsam.Pose2(relative_pose[0], relative_pose[1], relative_pose[2])
        noise_model = gtsam.noiseModel.Diagonal.Sigmas(noise)
        factor = gtsam.BetweenFactorPose2(pose_key_i, pose_key_j, odom, noise_model)
        self.graph.add(factor)

    def optimize(self, initial_estimates=None):
        """Optimisation du graphe (batch LM)"""
        if initial_estimates is None:
            initial_estimates = self.initial_estimate

        optimizer = gtsam.LevenbergMarquardtOptimizer(self.graph,
                                                       initial_estimates,
                                                       self.params)
        result = optimizer.optimize()
        return result

    def incremental_update(self, new_factors, new_values):
        """Mise à jour incrémentale (iSAM2)"""
        self.isam.update(new_factors, new_values)
        result = self.isam.calculateEstimate()
        return result
```

### Loop Closure Detection

```python
class LoopClosureDetector:
    """
    Détection de boucle via scan matching ou descripteurs visuels
    """
    def __init__(self, distance_threshold=1.0, angle_threshold=0.3):
        self.distance_thresh = distance_threshold
        self.angle_thresh = angle_threshold
        self.pose_history = []  # [(x, y, θ, scan)]

    def detect_loop(self, current_scan, current_pose):
        """Vérifie si le scan courant correspond à un historique"""
        for i, (x_old, y_old, θ_old, scan_old) in enumerate(self.pose_history):
            # Distance géométrique
            dx = current_pose[0] - x_old
            dy = current_pose[1] - y_old
            dist = np.sqrt(dx**2 + dy**2)

            if dist < self.distance_thresh:
                # Scan matching (ICP ou correlative)
                icp = ICPMatcher()
                T_rel, score = icp.match(scan_old, current_scan,
                                         initial_guess=np.array([dx, dy, 0]))

                if score < threshold:  # bon match
                    return i, T_rel, score
        return None, None, None

class ICPMatcher:
    """Iterative Closest Point pour scan matching"""
    def match(self, scan_ref, scan_curr, initial_guess, max_iter=50):
        T = initial_guess.copy()
        for _ in range(max_iter):
            # 1. Association des points (plus proche voisin)
            associations = self.associate(scan_ref, scan_curr, T)

            # 2. Calcul de la transformation optimale
            T_new = self.estimate_transform(scan_ref, scan_curr, associations)

            # 3. Convergence ?
            if np.linalg.norm(T_new - T) < 1e-6:
                break
            T = T_new
        return T, self.compute_score(scan_ref, scan_curr, T)
```

## Cartographer (ROS2) — Configuration

### Configuration
```lua
-- cartographer.lua
include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  map_builder = MAP_BUILDER,
  trajectory_builder = TRAJECTORY_BUILDER,
  map_frame = "map",
  tracking_frame = "base_link",
  published_frame = "base_link",
  odom_frame = "odom",
  provide_odom_frame = true,
  publish_frame_projected_to_2d = false,
  use_pose_extrapolator = true,
  use_odometry = false,
  use_nav_sat = false,
  use_landmarks = false,
  num_laser_scans = 1,
  num_multi_echo_laser_scans = 0,
  num_subdivisions_per_laser_scan = 1,
  num_point_clouds = 0,
  lookup_transform_timeout_sec = 0.2,
  submap_publish_period_sec = 0.3,
  pose_publish_period_sec = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio = 1.,
  sensor_identifier = "scan",
  submaps = { -- 2D local SLAM
    resolution = 0.05,
    num_range_data = 100,
  },
  ceres_scan_matcher = {
    occupied_space_weight = 1.,
    translation_weight = 10.,
    rotation_weight = 40.,
    ceres_solver_options = {
      use_nonmonotonic_steps = false,
      max_num_iterations = 20,
      num_threads = 1,
    },
  },
  ceres_pose = {
    optimize_every_n_scans = 20,
    ceres_solver_options = {
      use_nonmonotonic_steps = false,
      max_num_iterations = 50,
      num_threads = 1,
    },
  },
}

return options
```

### Lancement ROS2
```bash
# Cartographer 2D
ros2 launch cartographer_ros cartographer.launch.py \
  configuration_basename:=cartographer.lua

# Occupancy grid → navigation
ros2 run cartographer_ros cartographer_occupancy_grid_node \
  -resolution 0.05 \
  -publish_period_sec 1.0
```

## LiDAR SLAM vs Visual SLAM

| Aspect | LiDAR SLAM | Visual SLAM |
|--------|-----------|-------------|
| Capteur | LiDAR 2D/3D | Caméra monoculaire/stéréo |
| Précision | 1-5 cm | 5-50 cm (mono), 1-10 cm (stéréo) |
| Robustesse | Excellente (indépendant lumière) | Moyenne (lumière/texture) |
| Coût capteur | 500-5000€ | 50-500€ |
| Dérive | Faible | Plus élevée (sauf stéréo) |
| Temps réel | Oui (Cartographer, Karto) | Oui (ORB-SLAM3, DSO) |
| Cartographie | Grille d'occupation | Sparse feature map / dense |

### ORB-SLAM3 (Visual + Inertial)
```bash
# Monocular
ros2 run orbslam3 mono Vocabulary/ORBvoc.txt Monocular/TUM1.yaml

# Stereo
ros2 run orbslam3 stereo Vocabulary/ORBvoc.txt Stereo/EuRoC.yaml true

# RGB-D
ros2 run orbslam3 rgbd Vocabulary/ORBvoc.txt RGBD/TUM1.yaml

# IMU-stereo
ros2 run orbslam3 imu_stereo Vocabulary/ORBvoc.txt MyConfig.yaml
```

## Mesures d'Évaluation SLAM

| Métrique | Description |
|----------|-------------|
| **ATE** (Absolute Trajectory Error) | RMSE de la pose estimée vs vérité terrain |
| **RPE** (Relative Pose Error) | Erreur entre poses consécutives (dérive locale) |
| **RMSE** | Root Mean Square Error : √(1/N Σ ||x̂ - x||²) |
| **Consistency** | χ² normalisé de la covariance estimée |
| **Loop Closure Rate** | % de boucles correctement détectées |

```python
# ATE — évaluation de trajectoire
def compute_ate(estimated_poses, ground_truth_poses):
    # Alignement (Horn's method) : Sim(3) alignment
    T_aligned = sim3_alignment(estimated_poses, ground_truth_poses)
    aligned_poses = [T_aligned @ p for p in estimated_poses]

    errors = []
    for p_est, p_gt in zip(aligned_poses, ground_truth_poses):
        e = np.linalg.norm(p_est[:3, 3] - p_gt[:3, 3])
        errors.append(e)

    return {
        'rmse': np.sqrt(np.mean(np.array(errors)**2)),
        'mean': np.mean(errors),
        'std': np.std(errors),
        'max': np.max(errors),
        'min': np.min(errors)
    }
```

## Pièges et Bonnes Pratiques

- **EKF-SLAM ne scale pas** : O(N²) pour N landmarks → >100 landmarks, le temps de mise à jour explose. Préférer FastSLAM (O(M log N)) ou Graph SLAM.
- **Boucle fermée essentielle** : sans loop closure, SLAM dérive indéfiniment. Toujours activer loop closure (Cartographer, iSAM2). Le seuil de détection est critique — trop bas = faux positifs (corrompt la carte), trop haut = boucles manquées (dérive).
- **Cartographer sans odométrie** : sans odom (dead reckoning), le réalisme est plus lent. Si possible, fournir une odométrie (roues, IMU, ou LiDAR scan matching) pour réduire la dérive.
- **Visual SLAM en milieu industriel** : surfaces uniformes, métal brillant, faible luminosité → les features ORB dégénèrent. Préférer LiDAR SLAM pour les environnements industriels.
- **Consistance des filtres** : EKF-SLAM surestime la confiance (covariance trop petite) → le filtre devient inconsistant. Utiliser le test de consistance (χ² = innovation^T S^{-1} innovation) pour détecter la divergence.
- **Re-localisation** : après un échec (kidnapped robot problem), utiliser un emplacement global (global localization) avec Monte Carlo localisation (MCL) re-initialisé sur la carte.

## Références

- Thrun, S., Burgard, W. & Fox, D. (2005). *Probabilistic Robotics*. MIT Press. ISBN 978-0262201629
- Grisetti, G. et al. (2010). A Tutorial on Graph-Based SLAM. *IEEE Intelligent Transportation Systems Magazine*, 2(4), 31-43.
- Montemerlo, M. & Thrun, S. (2007). *FastSLAM: A Scalable Method for SLAM*. Springer. ISBN 978-3540463993
- Mur-Artal, R. & Tardós, J.D. (2017). ORB-SLAM2: An Open-Source SLAM System for Monocular, Stereo, and RGB-D Cameras. *IEEE Trans. Robotics*, 33(5), 1255-1262.
- Campos, C. et al. (2021). ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial and Multi-Map SLAM. *IEEE Trans. Robotics*, 37(6), 1874-1890.
- Hess, W. et al. (2016). Real-Time Loop Closure in 2D LiDAR SLAM. *IEEE ICRA 2016*.
- Kaess, M. et al. (2012). iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree. *Int. J. Robotics Research*, 31(2), 216-235.