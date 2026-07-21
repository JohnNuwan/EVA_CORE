---
name: robot-kinematics
description: Cinématique des robots — paramètres DH, forward/inverse kinematics, Jacobien, singularités, workspace
---

# Robot Kinematics — Cinématique des Robots

## Quand l'utiliser
Quand l'utilisateur demande de calculer la cinématique directe/inverse, de modéliser un bras robotique, de paramétrer DH, d'analyser les singularités, ou de générer un espace de travail.

## Paramètres de Denavit-Hartenberg (DH)

### Convention DH Standard (Craig)
```
Paramètres pour chaque joint i :
  θ_i   : angle autour de l'axe z_{i-1}
  d_i   : translation le long de z_{i-1}
  a_i   : translation le long de x_i
  α_i   : angle autour de x_i

Matrice de transformation homogène T_i^{i-1} :
  T = | cosθ   -sinθ·cosα   sinθ·sinα   a·cosθ |
      | sinθ    cosθ·cosα  -cosθ·sinα   a·sinθ |
      |   0       sinα        cosα         d    |
      |   0         0           0          1    |
```

### Convention DH Modifié (Khalil-Kleinfinger)
```
Paramètres :
  α_{i-1} : angle autour de x_{i-1}
  a_{i-1} : translation le long de x_{i-1}
  θ_i     : angle autour de z_i
  d_i     : translation le long de z_i
```

## Cinématique Directe (Forward Kinematics)

Calcul séquentiel des matrices homogènes du repère base au repère effecteur.

```python
import numpy as np

def dh_transform(theta, d, a, alpha):
    """Matrice de transformation DH standard (Craig)"""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st*ca,  st*sa,  a*ct],
        [st,  ct*ca, -ct*sa,  a*st],
        [0,   sa,     ca,     d   ],
        [0,   0,      0,      1   ]
    ])

def forward_kinematics(joint_angles, dh_params):
    """
    dh_params : liste de tuples (theta_offset, d, a, alpha, joint_type)
    joint_angles : configuration angulaire des joints
    """
    T = np.eye(4)
    for i, (theta_off, d, a, alpha, jtype) in enumerate(dh_params):
        theta = joint_angles[i] + theta_off
        Ti = dh_transform(theta, d, a, alpha)
        T = T @ Ti
    return T  # T^0_n : pose de l'effecteur dans le repère base

# Exemple : robot 6-DOF type Fanuc/KUKA
DH_FANUC = [
    (0,           0.3425,  0.075,  -np.pi/2, 'R'),  # J1
    (np.pi/2,     0,       0.300,  0,        'R'),  # J2
    (0,           0,       0.075,  -np.pi/2, 'R'),  # J3
    (0,           0.320,   0,       np.pi/2, 'R'),  # J4
    (0,           0,       0,      -np.pi/2, 'R'),  # J5
    (0,           0.080,   0,       0,        'R')   # J6
]

# Cinématique directe
angles = np.array([0.0, -1.57, 1.57, 0.0, 0.0, 0.0])
T_ee = forward_kinematics(angles, DH_FANUC)
position = T_ee[:3, 3]
rotation = T_ee[:3, :3]  # matrice de rotation
```

## Cinématique Inverse (Inverse Kinematics, IK)

Problème : trouver q (angles joints) telle que FK(q) = T_desired (pose désirée).

### Méthodes Itératives

#### IK Jacobien (Damped Least Squares)
```python
def ik_jacobian(dh_params, T_target, q0, max_iter=100, tol=1e-6, lambda_=0.1):
    """IK par Jacobien pseudo-inverse avec damping"""
    q = q0.copy()

    for _ in range(max_iter):
        # Cinématique directe
        T_curr = forward_kinematics(q, dh_params)

        # Erreur de pose (translational + rotational)
        pos_err = T_target[:3, 3] - T_curr[:3, 3]

        # Erreur rotationnelle (axis-angle)
        R_err = T_target[:3, :3] @ T_curr[:3, :3].T
        axis_angle = np.array([
            R_err[2, 1] - R_err[1, 2],
            R_err[0, 2] - R_err[2, 0],
            R_err[1, 0] - R_err[0, 1]
        ]) / 2.0

        e = np.concatenate([pos_err, axis_angle])

        if np.linalg.norm(e) < tol:
            return q

        # Jacobien à la configuration courante
        J = compute_jacobian(q, dh_params)

        # Damped LS : q_dot = J^T (J J^T + λ²I)^{-1} e
        JJT = J @ J.T
        damped = JJT + lambda_**2 * np.eye(6)
        dq = J.T @ np.linalg.solve(damped, e)

        q = q + dq * 0.5  # step size

    return q
```

#### IK Numérique (SciPy)
```python
from scipy.optimize import minimize

def ik_numerique(T_target, q0, dh_params):
    def f(q):
        T = forward_kinematics(q, dh_params)
        # Erreur = position + rotation (quaternion)
        pos_err = np.linalg.norm(T_target[:3, 3] - T[:3, 3])
        # Frobenius norm sur rotation
        rot_err = np.linalg.norm(T_target[:3, :3] - T[:3, :3], 'fro')
        return pos_err + 0.1 * rot_err

    res = minimize(f, q0, method='BFGS', options={'maxiter': 200})
    return res.x if res.success else None
```

### IK Analytique (closed-form)

Pour robots avec sphère de poignet (3 derniers axes concourants, ex: PUMA 560, KUKA KR, ABB IRB).

```python
def ik_pieper(dh_params, T_target):
    """
    Solution IK analytique pour robots avec poignet sphérique
    (3 derniers axes concourants - Pieper's solution)
    """
    # Étape 1 : Extraire position poignet = T_06 * [0,0,0,1]^T
    # Pour poignet sphérique : position poignet déterminée par J1,J2,J3
    # J4,J5,J6 : orientent seulement l'effecteur

    # Position du poignet dans repère base
    d6 = dh_params[5][1]  # d dernier joint
    d = T_target[:3, :3] @ np.array([0, 0, -d6]) + T_target[:3, 3]

    # J1 : projection dans plan xy
    theta1_1 = np.arctan2(d[1], d[0])
    theta1_2 = np.arctan2(-d[1], -d[0])

    solutions = []
    for theta1 in [theta1_1, theta1_2]:
        # J2, J3 : géométrie du plan sagittal
        # ... (géométrie du triangle formé par base-épaule-coude-poignet)
        pass

    return solutions
```

## Jacobien Géométrique

Le Jacobien J(q) relie vitesses articulaires aux vitesses cartésiennes :
```
v = J(q) · q_dot
où v = [v_x, v_y, v_z, ω_x, ω_y, ω_z]^T
```

```python
def compute_jacobian(q, dh_params):
    """Jacobien géométrique (6 × n)"""
    n = len(q)
    J = np.zeros((6, n))
    T = np.eye(4)

    for i in range(n):
        # Transformation jusqu'au joint i
        theta = q[i] + dh_params[i][0]
        Ti = dh_transform(theta, dh_params[i][1],
                          dh_params[i][2], dh_params[i][3])
        T = T @ Ti

        # Axe z_i dans repère base
        z_i = T[:3, 2]

        # Origine O_i dans repère base
        o_i = T[:3, 3]

        # Position de l'effecteur
        T_ee = forward_kinematics(q, dh_params)
        o_n = T_ee[:3, 3]

        # Pour joint prismatique (P) : v = z_i, ω = 0
        # Pour joint rotoïde (R) : v = z_i × (o_n - o_i), ω = z_i
        J[:3, i] = np.cross(z_i, o_n - o_i)  # translation
        J[3:, i] = z_i                        # rotation

    return J
```

### Analyse du Jacobien

```python
# Singularités : det(J(q)) = 0
def check_singularity(J, threshold=1e-6):
    JTJ = J.T @ J
    if np.linalg.matrix_rank(J) < min(J.shape):
        return True
    # Condition number
    cond = np.linalg.cond(J)
    return cond > 1.0 / threshold  # mal conditionné → proche singularité

# Manipulabilité (Yoshikawa)
def manipulability(J):
    JTJ = J @ J.T
    return np.sqrt(np.linalg.det(JTJ))

# Élasticité du Jacobien
# Plus manipulabilité → grande, plus le robot est agile à cette configuration
```

## Espace de Travail (Workspace)

### Analyse Discrète (Monte Carlo)
```python
def workspace_monte_carlo(dh_params, N=10000):
    """Échantillonne aléatoirement l'espace de configuration"""
    points = []
    for _ in range(N):
        q_random = np.random.uniform(
            [-np.pi]*6, [np.pi]*6
        )
        T = forward_kinematics(q_random, dh_params)
        points.append(T[:3, 3])  # position x,y,z
    points = np.array(points)

    # Bounding box
    bb_min = points.min(axis=0)
    bb_max = points.max(axis=0)

    # Volume (enveloppe convexe)
    from scipy.spatial import ConvexHull
    hull = ConvexHull(points)
    volume = hull.volume

    return points, bb_min, bb_max, volume
```

## Singularités — Types et Détection

| Type | Cause | Cartographie |
|------|-------|-------------|
| Singularité de bord | Bras complètement étendu | J1,J2,J3 : rang perdu |
| Singularité intérieure | Axes alignés (ex: J4 = 0 → J6 coaxial J4) | Alignement z_i |
| Singularité d'épaule | Centre poignet dans axe J1 | Dégénérescence sphérique |
| Singularité de coude | Épaule-coude aligné (J3 = 0) | Perte de mobilité radiale |

### Résolution en Singularité
```python
# DLS (Damped Least Squares) — préféré
def damped_pseudo_inverse(J, lambda_=0.1):
    """Pseudo-inverse amortie"""
    U, s, Vt = np.linalg.svd(J, full_matrices=False)
    s_damped = s / (s**2 + lambda_**2)
    J_dls = Vt.T @ np.diag(s_damped) @ U.T
    return J_dls

# SVD with task-priority framework
def svd_nullspace(J, J_nullspace_priority=True):
    U, s, Vt = np.linalg.svd(J, full_matrices=True)
    rank = np.sum(s > 1e-6)
    return U, s, Vt, rank
```

## Transformations et Représentations d'Attitude

```python
from scipy.spatial.transform import Rotation as R

# Matrice de rotation → quaternion
r = R.from_matrix(T_ee[:3, :3])
quat = r.as_quat()        # [x, y, z, w]
euler = r.as_euler('zyx') # roulis, tangage, lacet
rotvec = r.as_rotvec()    # rotation axis-angle

# Angle-axis (θ, u) où θ = angle, u = axe unitaire
theta = np.linalg.norm(rotvec)
axis = rotvec / theta if theta > 0 else np.array([1, 0, 0])

# Composition de translations + rotations
# T = | R  t |
#     | 0  1 |
```

## Pièges et Bonnes Pratiques

- **Singularité vs précision** : ne pas utiliser IK Jacobien pur près des singularités ; toujours utiliser DLS (damped least squares) ou SVD filtering.
- **DH modifié vs standard** : vérifier la convention utilisée dans la librairie — un mélange produit des résultats erronés. KDL utilise DH modifié (Craig 2005) ; PyBot utilise DH standard.
- **Tolérance IK** : en industrie, tolérance de position < 0.1 mm et orientation < 0.1° pour l'usinage ; pour le pick-and-place, < 1 mm et 1° suffisent.
- **Analyse de workspace** : l'échantillonnage Monte Carlo sous-estime les régions de volume. Utiliser > 10^5 points pour une bonne couverture ; améliorer avec importance sampling près des singularités.
- **DFKI / ROS IK** : préférer TRAC-IK à KDL pour l'IK industrielle — TRAC-IK combine IK numérique et analytique avec meilleur taux de convergence (10-30% supérieur).
- **Limites articulaires** : toujours contraindre IK dans les limites physiques (`lower ≤ q_i ≤ upper`). Utiliser des fonctions de coût quadratiques dans l'optimisation.

## Références

- Craig, J. (2005). *Introduction to Robotics: Mechanics and Control*. Pearson. ISBN 978-0201543612
- Siciliano, B. et al. (2009). *Robotics: Modelling, Planning and Control*. Springer. ISBN 978-1846286414
- Spong, M. et al. (2005). *Robot Modeling and Control*. Wiley. ISBN 978-0471649908
- TRAC-IK : https://traclabs.com/projects/trac-ik/
- OpenRAVE IKFast : https://openrave.org/docs/latest_stable/ikfast/
