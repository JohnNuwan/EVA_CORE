---
name: robot-control-theory
description: Théorie du contrôle pour la robotique — PID, LQR, MPC, computed torque, force control, impedance, passivity-based
---

# Robot Control Theory — Théorie du Commande pour Robots

## Quand l'utiliser
Quand l'utilisateur demande de concevoir un contrôleur pour un bras robotique, un robot mobile, un drone, ou d'implémenter PID/LQR/MPC, commande en force, commande hybride, ou contrôle par impédance.

## Modèle Dynamique du Robot

### Équation Générale
```
M(q) q̈ + C(q, q̇) q̇ + G(q) + τ_f(q̇) + τ_ext = τ
```
Où :
- `M(q)` ∈ ℝⁿˣⁿ : matrice d'inertie (symétrique, définie positive)
- `C(q, q̇)` : matrice de Coriolis/centrifuge (Ṁ - 2C est antisymétrique)
- `G(q)` : vecteur des couples gravitationnels
- `τ_f(q̇)` : frottements (visqueux + Coulomb)
- `τ_ext` : couples externes (interaction)
- `τ` : couples moteurs (entrée de commande)

### Propriétés
1. **M(q) > 0** : matrice d'inertie définie positive
2. **Ṁ(q) - 2C(q, q̇)** : antisymétrique (conservation d'énergie)
3. **Linéarité dans les paramètres** (LIP) : séparable en Y(q, q̇, q̈) Θ

```python
import numpy as np
from scipy.integrate import solve_ivp

class RobotDynamics:
    """Modèle dynamique pour un robot série n-DOF"""
    def __init__(self, n_dof, masses, links, dh_params):
        self.n = n_dof
        self.masses = masses
        self.links = links
        self.dh = dh_params

    def inertia_matrix(self, q):
        """M(q) — matrice d'inertie"""
        M = np.zeros((self.n, self.n))
        # Algorithme composite-rigid-body (Featherstone)
        for i in range(self.n):
            for j in range(i, self.n):
                # Calcul de M[i,j] via tenseurs d'inertie propagés
                pass
        M = M + M.T - np.diag(np.diag(M))  # symétrisation
        return M

    def coriolis(self, q, qd):
        """C(q, q̇) — via Christoffel symbols"""
        C = np.zeros((self.n, self.n))
        M = self.inertia_matrix(q)
        # M_ijk = ∂M_ij/∂q_k
        # C_ij = Σ_k M_ijk * qd_k + 0.5 * Σ_k (∂M_ik/∂q_j - ∂M_jk/∂q_i) * qd_k
        return C

    def gravity(self, q):
        """G(q) — couples gravitationnels"""
        G = np.zeros(self.n)
        # Somme des couples générés par chaque link
        return G

    def forward_dynamics(self, t, state, tau):
        """M(q) q̈ = τ - C q̇ - G - τ_f"""
        q = state[:self.n]
        qd = state[self.n:]

        M = self.inertia_matrix(q)
        C = self.coriolis(q, qd)
        G = self.gravity(q)
        friction = self.friction(qd)

        qdd = np.linalg.solve(M, tau - C @ qd - G - friction)
        return np.concatenate([qd, qdd])
```

## Contrôle PID

### PID Classique (Espace Articulaire)
```python
class PIDController:
    """PID simple avec anti-windup"""
    def __init__(self, Kp, Ki, Kd, sat=10.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.sat = sat
        self.integral = 0.0
        self.prev_error = 0.0

    def compute(self, q_des, q, qd_des=None, qd=None, dt=0.001):
        """q_des=q_target pour régulation, q_des(t) pour tracking"""
        if qd_des is None:
            qd_des = 0.0
        if qd is None:
            qd = 0.0

        e = q_des - q
        ed = qd_des - qd

        # PID
        self.integral += e * dt
        # Anti-windup (clamping)
        self.integral = np.clip(self.integral, -self.sat/self.Ki, self.sat/self.Ki)

        u = self.Kp * e + self.Ki * self.integral + self.Kd * ed
        u = np.clip(u, -self.sat, self.sat)
        self.prev_error = e

        return u

# Tuning PID — méthode Ziegler-Nichols
# K_u = gain critique, T_u = période d'oscillation
# P: Kp=0.5 K_u
# PI: Kp=0.45 K_u, Ki=Kp/(0.85 T_u)
# PID: Kp=0.6 K_u, Ki=Kp/(0.5 T_u), Kd=Kp*(0.125 T_u)
```

### PID Computed Torque (Feedback Linearization)
```python
class ComputedTorqueController:
    """
    τ = M(q) [q̈_des + Kp e + Kd ė] + C(q,q̇)q̇ + G(q)
    Résulte en : ë + Kd ė + Kp e = 0  → convergence exponentielle
    """
    def __init__(self, robot, Kp, Kd):
        self.robot = robot
        self.Kp = np.diag(Kp)
        self.Kd = np.diag(Kd)

    def compute(self, q_des, qd_des, qdd_des, q, qd):
        M = self.robot.inertia_matrix(q)
        C = self.robot.coriolis(q, qd)
        G = self.robot.gravity(q)

        e = q_des - q
        ed = qd_des - qd

        # Compensation + erreur linéarisée
        v = qdd_des + self.Kd @ ed + self.Kp @ e
        tau = M @ v + C @ qd + G

        return tau
```

## LQR (Linear Quadratic Regulator)

### LQR Continu (Infinite Horizon)
```python
def lqr_solve(A, B, Q, R):
    """Résout l'équation de Riccati : A^T P + P A - P B R^{-1} B^T P + Q = 0"""
    from scipy.linalg import solve_continuous_are
    P = solve_continuous_are(A, B, Q, R)
    K = np.linalg.inv(R) @ B.T @ P  # LQR gain : u = -K x
    return K, P

# Linéarisation du robot à un point d'équilibre q0
# x = [Δq; Δq̇], u = Δτ
# ẋ = [0, I; -M^{-1} ∂G/∂q, 0] x + [0; M^{-1}] u
def linearize_robot(robot, q0):
    M0 = robot.inertia_matrix(q0)
    M_inv = np.linalg.inv(M0)
    dGdq = robot.gravity_jacobian(q0)  # ∂G/∂q

    A = np.block([
        [np.zeros((robot.n, robot.n)), np.eye(robot.n)],
        [-M_inv @ dGdq, np.zeros((robot.n, robot.n))]
    ])
    B = np.vstack([np.zeros((robot.n, robot.n)), M_inv])
    return A, B
```

### LQR avec Servo (Integral Action)
Pour rejeter les perturbations statiques :
```python
def lqr_with_integral(A, B, Q, R, Qi):
    """LQR servo avec action intégrale sur l'erreur"""
    # État augmenté : x_aug = [x; ∫e dt]
    A_aug = np.block([[A, np.zeros((A.shape[0], A.shape[0]))],
                      [-np.eye(A.shape[0]), np.zeros((A.shape[0], A.shape[0]))]])
    B_aug = np.vstack([B, np.zeros(B.shape)])

    Q_aug = np.block([[Q, np.zeros((Q.shape[0], Qi.shape[0]))],
                      [np.zeros((Qi.shape[0], Q.shape[0])), Qi]])

    K_aug, P = lqr_solve(A_aug, B_aug, Q_aug, R)
    return K_aug  # [K_state, Ki]
```

## MPC (Model Predictive Control)

### MPC Discrete pour Robots
```python
from scipy.optimize import minimize

class RobotMPC:
    """MPC pour robot avec optimisation en temps réel"""
    def __init__(self, robot, dt=0.01, horizon=50):
        self.robot = robot
        self.dt = dt
        self.N = horizon  # horizon de prédiction
        self.n = robot.n

        # Pondérations
        self.Q = np.eye(self.n) * 100.0    # position error
        self.R = np.eye(self.n) * 0.01     # contrôle
        self.Qf = np.eye(self.n) * 1000.0  # terminal cost

    def compute(self, x0, x_des_traj):
        """x0 = [q; q̇], x_des_traj = séquence d'états désirés"""
        n_vars = self.N * self.n  # seulement les contrôles (optimisation réduite)

        def cost(U_flat):
            U = U_flat.reshape(self.N, self.n)
            x = x0.copy()
            J = 0

            for k in range(self.N):
                tau = U[k]
                # Simulation du robot (RK4)
                x_next = self.simulate_step(x, tau)
                x_des = x_des_traj[k]

                # Erreur
                e = x[:self.n] - x_des[:self.n]
                ed = x[self.n:] - x_des[self.n:]

                J += e.T @ self.Q @ e + tau.T @ self.R @ tau
                x = x_next

            # Terminal cost
            e_f = x[:self.n] - x_des_traj[-1][:self.n]
            J += e_f.T @ self.Qf @ e_f
            return J

        def constraint(U_flat):
            """Contraintes : limites articulaires et couples max"""
            U = U_flat.reshape(self.N, self.n)
            x = x0.copy()
            g = []

            for k in range(self.N):
                x = self.simulate_step(x, U[k])
                # Limites : |q| ≤ q_max, |τ| ≤ τ_max
                g.extend([
                    x[0] - np.pi,     # q ≤ π (upper)
                    -np.pi - x[0],     # -π ≤ q (lower)
                    U[k] - 10.0,       # τ ≤ 10 Nm
                    -10.0 - U[k]       # -10 ≤ τ
                ])
            return np.array(g)

        # Optimisation initiale (zéro ou warm-start)
        U0 = np.zeros(n_vars)

        bounds = [(-10.0, 10.0)] * n_vars  # limites couple
        res = minimize(cost, U0, method='SLSQP',
                       bounds=bounds,
                       constraints={'type': 'ineq', 'fun': constraint},
                       options={'maxiter': 100})

        return res.x[:self.n]  # premier contrôle uniquement (receding horizon)

    def simulate_step(self, x, tau, dt=None):
        """RK4 — intégration du modèle dynamique"""
        if dt is None:
            dt = self.dt

        def f(state):
            q = state[:self.n]
            qd = state[self.n:]
            M = self.robot.inertia_matrix(q)
            C = self.robot.coriolis(q, qd)
            G = self.robot.gravity(q)
            qdd = np.linalg.solve(M, tau - C @ qd - G)
            return np.concatenate([qd, qdd])

        # RK4
        k1 = f(x)
        k2 = f(x + dt/2 * k1)
        k3 = f(x + dt/2 * k2)
        k4 = f(x + dt * k3)
        return x + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
```

## Commande en Force et Impédance

### Commande en Force Directe
```python
class ForceController:
    """
    τ = J(q)^T F_des + C(q,q̇)q̇ + G(q)
    F_des : force désirée à l'effecteur dans le repère base
    """
    def __init__(self, robot, K_f=0.1):
        self.robot = robot
        self.K_f = K_f  # Compliance force

    def compute(self, q, qd, F_des, J):
        M = self.robot.inertia_matrix(q)
        C = self.robot.coriolis(q, qd)
        G = self.robot.gravity(q)

        # τ = J^T F_des + dynamique compensée
        tau = J.T @ F_des + C @ qd + G
        return tau
```

### Contrôle par Impédance
```python
class ImpedanceController:
    """
    M_d ë + D_d ė + K_d e = F_ext
    τ = M(q) u + C(q,q̇)q̇ + G(q) + τ_ext
    où u = q̈_d - M_d^{-1}(D_d ė + K_d e - F_ext)
    """
    def __init__(self, robot, Md, Dd, Kd):
        self.robot = robot
        self.Md = Md  # inertie désirée
        self.Dd = Dd  # amortissement désiré
        self.Kd = Kd  # raideur désirée

    def compute(self, q_des, q, qd, qd_des, J, F_ext):
        M = self.robot.inertia_matrix(q)
        C = self.robot.coriolis(q, qd)
        G = self.robot.gravity(q)

        e = q - q_des
        ed = qd - qd_des

        # Loi d'impédance
        Md_inv = np.linalg.inv(self.Md)
        u = qdd_des - Md_inv @ (self.Dd @ ed + self.Kd @ e - F_ext)

        tau = M @ u + C @ qd + G
        return tau
```

### Commande Hybride Force/Pose (Mason)
```python
class HybridForcePositionController:
    """
    Partitionne l'espace de tâche en directions force et position
    S : matrice de sélection (diag, 1=position, 0=force)
    I-S : directions en force
    """
    def __init__(self, Kp_pose, Kd_pose, Kf_force):
        self.Kp = Kp_pose   # raideur position
        self.Kd = Kd_pose   # amortissement position
        self.Kf = Kf_force  # gain force

    def compute(self, q, qd, F_des, x_des, x, xd, J):
        S = np.diag([1, 1, 0, 1, 1, 1])  # axe Z en force

        # Force → couple : τ_f = J^T S F_des + J^T (I-S) K_f (F_des - F_meas)
        # Position → couple : τ_p = J^T K_p (x_des - x) + J^T K_d (x_des - x_d)
        # τ = τ_p + τ_f

        return tau
```

## Commande Adaptative

### Model Reference Adaptive Control (MRAC)
```python
class MRAC:
    """
    τ = Y(q, q̇, q̈_r) Θ̂ + K_d s
    où s = ė + Λ e  (sliding surface)
    Θ̂ ajusté par loi adaptative : Θ̂̇ = -Γ Y^T s
    """
    def __init__(self, robot, Lambda, Gamma, Kd):
        self.robot = robot
        self.Lambda = np.diag(Lambda)
        self.Gamma = Gamma  # gain d'adaptation
        self.Kd = np.diag(Kd)
        self.Theta_hat = np.zeros(robot.param_count)

    def regressor(self, q, qd, qd_r, qdd_r):
        """Y(q, q̇, q̇_r, q̈_r) — matrice de régression"""
        # Construction à partir des équations dynamiques
        # YΘ = M q̈_r + C q̇_r + G
        return Y  # n × p

    def compute(self, q, qd, qd_des, q_des):
        e = q - q_des
        ed = qd - qd_des
        qd_r = qd_des - self.Lambda @ e
        qdd_r = qdd_des - self.Lambda @ ed

        Y = self.regressor(q, qd, qd_r, qdd_r)
        s = ed + self.Lambda @ e

        # Loi de commande
        tau = Y @ self.Theta_hat - self.Kd @ s

        # Adaptation
        self.Theta_hat += self.Gamma @ Y.T @ s
        return tau
```

## Contrôleur pour Robots Mobiles

### Differential Drive — P(i)D avec Saturation
```python
class MobileBaseController:
    """
    q = [x, y, θ]^T  (pose du robot)
    u = [v, ω]^T      (vitesse linéaire, angulaire)
    """
    def __init__(self, Kp_lin=0.5, Kp_ang=1.0, max_v=1.0, max_omega=2.0):
        self.Kp_lin = Kp_lin
        self.Kp_ang = Kp_ang
        self.max_v = max_v
        self.max_omega = max_omega

    def compute(self, x_goal, x_robot):
        # Erreur dans repère du robot
        dx = x_goal[0] - x_robot[0]
        dy = x_goal[1] - x_robot[1]
        theta = x_robot[2]

        # Transformation dans le repère robot (équation unicycle)
        e_x = dx * np.cos(theta) + dy * np.sin(theta)
        e_y = -dx * np.sin(theta) + dy * np.cos(theta)

        # Distance + angle
        dist = np.sqrt(dx**2 + dy**2)
        angle_to_goal = np.arctan2(dy, dx) - theta
        angle_to_goal = np.arctan2(np.sin(angle_to_goal), np.cos(angle_to_goal))

        # Contrôleurs
        v = np.clip(self.Kp_lin * dist, -self.max_v, self.max_v)
        omega = np.clip(self.Kp_ang * angle_to_goal, -self.max_omega, self.max_omega)

        return v, omega
```

## Pièges et Bonnes Pratiques

- **PID pur sur robot** : sans compensation de gravité G(q), le robot chute ou dérive. Toujours ajouter G(q) (feedforward) en complément du PID (feedback).
- **Choisir LQR vs MPC** : LQR pour régulation autour d'un point fixe (calcul fermé, temps réel) ; MPC pour tracking de trajectoire avec contraintes (optimisation, horizon). MPC 10-100× plus coûteux.
- **Anti-windup** : toujours inclure un mécanisme anti-windup sur l'intégral du PID. L'intégral qui sature est la cause #1 des overshoots en robotique.
- **MPC temps réel** : pour robots rapides (ΔT=1ms), utiliser iLQR (iterative LQR) ou SQP avec code généré (ACADO, CasADi). Pas de solveur Python générique.
- **Commande en force** : nécessite un capteur de force à l'effecteur (FT sensor). Sans mesure de τ_ext, la commande en force boucle ouverte (sans feedback) n'est pas robuste.
- **Passivité** : Ṁ - 2C antisymétrique garantit la passivité. Les contrôleurs par impédance doivent préserver cette propriété pour la stabilité en contact.
- **Collision sans capteur** : estimer τ_ext via observateur d'état (observateur de moment, Luenberger) : τ̂_ext = g (τ - M(q)q̈ - Cq̇ - G).

## Références

- Slotine, J.E. & Li, W. (1991). *Applied Nonlinear Control*. Prentice Hall. ISBN 978-0130408907
- Siciliano, B. et al. (2009). *Robotics: Modelling, Planning and Control*. Springer. ISBN 978-1846286414
- Sciavicco, L. & Siciliano, B. (2000). *Modelling and Control of Robot Manipulators*. Springer. ISBN 978-1852332211
- Maciejowski, J. (2002). *Predictive Control with Constraints*. Prentice Hall. ISBN 978-0201398236
- Hogan, N. (1985). Impedance Control: An Approach to Manipulation. *J. Dynamic Systems, Measurement, and Control*, 107(1), 1-24.
- Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer. ISBN 978-1489981710
