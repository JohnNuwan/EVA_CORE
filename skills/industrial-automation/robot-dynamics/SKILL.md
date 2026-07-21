---
name: robot-dynamics
description: Dynamique des robots — Newton-Euler, Lagrange, Featherstone's RBDA, simulation, friction, contact, flexible dynamics, identification paramétrique
---

# Robot Dynamics — Dynamique des Robots

## Quand l'utilisateur
Quand l'utilisateur demande de modéliser la dynamique d'un robot, de calculer les couples nécessaires pour un mouvement, de simuler un bras robotique, d'identifier les paramètres dynamiques, ou de traiter des contraintes de contact.

## Formalisme de Newton-Euler

### Algorithme Récursif de Newton-Euler (RNEA)
Complexité O(n) pour un robot série n-DOF.

#### Phase Forward (vitesses/accélérations propagées)
```
Pour i = 1 → n (référentiel inertiel → effecteur) :
  ω_i     = R_i^{i-1}^T (ω_{i-1} + q̇_i · z_0)
  ω̇_i     = R_i^{i-1}^T (ω̇_{i-1} + q̈_i · z_0 + ω_{i-1} × q̇_i · z_0)
  v̇_i     = R_i^{i-1}^T (v̇_{i-1}) + ω̇_i × r_i + ω_i × (ω_i × r_i)
  v̇_c_i   = v̇_i + ω̇_i × c_i + ω_i × (ω_i × c_i)   (accélération du COM)
```

#### Phase Backward (forces/couples propagés)
```
Pour i = n → 1 (effecteur → base) :
  f_i     = m_i · v̇_c_i
  n_i     = I_i · ω̇_i + ω_i × (I_i · ω_i)
  F_i     = R_{i+1}^i · F_{i+1} + [f_i; n_i + c_i × f_i]
  τ_i     = F_i · z_0 + q̇_i · f_v_i + sign(q̇_i) · f_c_i
```

```python
import numpy as np

class NewtonEulerDynamics:
    """Dynamique récursive Newton-Euler pour robot série"""
    def __init__(self, links):
        """
        links : liste de dict
          - mass: float (kg)
          - inertia: np.array(3,3) — tenseur d'inertie au COM
          - com: np.array(3) — centre de masse dans repère link
          - joint_axis: np.array(3) — axe du joint dans repère parent
          - parent_transform: np.array(4,4) — T fixe parent→link
        """
        self.links = links
        self.n = len(links)
        self.gravity = np.array([0, 0, -9.81])  # gravité

    def compute_torques(self, q, qd, qdd, F_ext=None):
        """
        Calcule les couples nécessaires pour réaliser q, qd, qdd
        Retourne τ (n,) — couples articulaires
        """
        n = self.n
        omega = np.zeros((n+1, 3))   # vitesses angulaires
        omega_d = np.zeros((n+1, 3)) # accélérations angulaires
        v_d = np.zeros((n+1, 3))     # accélérations linéaires
        v_d[0] = -self.gravity        # gravité dans repère base

        # Forward pass
        for i in range(n):
            # Transformation du joint i (rotative)
            R = self.links[i]['parent_transform'][:3, :3]
            r = self.links[i]['parent_transform'][:3, 3]
            z = self.links[i]['joint_axis']

            omega[i+1] = R.T @ omega[i]
            omega_d[i+1] = R.T @ omega_d[i]

            # Ajout de l'effet du joint
            omega[i+1] += qd[i] * z
            omega_d[i+1] += qdd[i] * z + np.cross(omega[i], qd[i] * z)

            # Accélération linéaire du repère du joint
            v_d[i+1] = R.T @ (v_d[i] + np.cross(omega_d[i], r) +
                               np.cross(omega[i], np.cross(omega[i], r)))

        # Backward pass
        f = np.zeros((n+1, 3))
        n_torque = np.zeros((n+1, 3))
        tau = np.zeros(n)

        for i in range(n-1, -1, -1):
            link = self.links[i]
            m = link['mass']
            I = link['inertia']
            c = link['com']

            # Inertiel au COM
            v_c_d = v_d[i+1] + np.cross(omega_d[i+1], c) + \
                    np.cross(omega[i+1], np.cross(omega[i+1], c))

            # Force et moment d'inertie
            f_i = m * v_c_d
            n_i = I @ omega_d[i+1] + np.cross(omega[i+1], I @ omega[i+1])

            # Transmission vers le parent
            R = self.links[i]['parent_transform'][:3, :3]
            f[i] = f_i
            n_torque[i] = n_i

            # Si c'est un joint rotoïde
            z = self.links[i]['joint_axis']
            tau[i] = n_torque[i].T @ z + qd[i] * link.get('fv', 0.0) + \
                     np.sign(qd[i]) * link.get('fc', 0.0)

        return tau
```

## Formalisme de Lagrange

### Équations d'Euler-Lagrange
```
L(q, q̇) = T(q, q̇) - U(q)   ← Lagrangien (énergie cinétique - potentielle)

d/dt(∂L/∂q̇) - ∂L/∂q = τ     ← Équations de mouvement

Forme matricielle :
M(q) q̈ + C(q, q̇) q̇ + G(q) = τ
```

```python
class LagrangeDynamics:
    """Dynamique par formalisme de Lagrange (symbolique)"""
    def symbolic_dynamics(self, dh_params, masses, inertias):
        """Construction symbolique de M, C, G"""
        import sympy as sp

        n = len(dh_params)
        q = sp.symbols(f'q0:{n}')
        qd = sp.symbols(f'qd0:{n}')

        # Énergie cinétique T = 1/2 q̇^T M(q) q̇
        # Énergie potentielle U = Σ m_i g^T p_com_i

        T_total = 0
        U_total = 0
        g = sp.Matrix([0, 0, -9.81])

        T_world = sp.eye(4)
        for i in range(n):
            # Transformation homogène jusqu'au link i
            theta = q[i] + dh_params[i][0]
            Ti = sp.Matrix(dh_transform(theta, *dh_params[i][1:4]))
            T_world = T_world * Ti

            # Position du COM (dans repère link)
            p_com = T_world[:3, :3] * sp.Matrix(inertias[i]['com']) + T_world[:3, 3]

            # Énergie potentielle
            U_total += masses[i] * g.dot(p_com)

            # Jacobien du COM (pour énergie cinétique linéaire + rotationnelle)
            # ...

        # Lagrangien
        L = T_total - U_total

        # Équations d'Euler-Lagrange
        # d/dt(∂L/∂q̇) - ∂L/∂q = 0
        tau = []
        for i in range(n):
            dL_dqdot = sp.diff(L, qd[i])
            d_dt_dL_dqdot = sum(
                sp.diff(dL_dqdot, q[j]) * qd[j] + sp.diff(dL_dqdot, qd[j]) * qdd[j]
                for j in range(n)
            )
            dL_dq = sp.diff(L, q[i])
            tau.append(sp.simplify(d_dt_dL_dqdot - dL_dq))

        return sp.Matrix(tau)
```

## Algorithme de Featherstone (RBDA)

### Articulated Body Algorithm (ABA) — O(n)
```python
class ArticulatedBodyAlgorithm:
    """
    Featherstone's Articulated Body Algorithm
    Calcule q̈ à partir de τ (inverse de RNEA)
    Complexité : O(n) — le plus rapide pour simulation
    """
    def aba(self, tau, q, qd, links):
        n = len(links)
        # Forward pass — calcul des vitesses
        v = [np.zeros(6)]  # vitesse spatiale 6D
        for i in range(n):
            S = self.motion_subspace(q[i], links[i])  # 6×1
            v_next = self.XT(links[i]) @ v[-1] + S * qd[i]
            v.append(v_next)

        # Backward pass — inertie articulée + biais
        IA = [self.I_spatial(links[i]) for i in range(n)]
        pA = [np.zeros(6) for _ in range(n)]

        for i in range(n-1, -1, -1):
            X = self.X(links[i+1])  # transformation
            S = self.motion_subspace(q[i], links[i])

            # Biais
            c = self.calculate_bias(v[i+1], IA[i], links[i])

            # Inertie articulée projetée
            U[i] = IA[i] @ S
            D[i] = S.T @ U[i]  # scalaire : masse apparente
            u[i] = tau[i] - S.T @ pA[i]

            # Transférer vers parent
            if i > 0:
                IA[i-1] = IA[i-1] + X.T @ (IA[i] - U[i] @ U[i].T / D[i]) @ X
                pA[i-1] = pA[i-1] + X.T @ (pA[i] + IA[i] @ c - U[i] * u[i] / D[i])

        # Forward pass — accélérations
        a = [np.zeros(6)]
        qdd = np.zeros(n)
        for i in range(n):
            S = self.motion_subspace(q[i], links[i])
            X = self.X(links[i+1])
            a_next = X @ a[-1] + self.calculate_bias(v[i+1], IA[i], links[i])
            qdd[i] = (u[i] - U[i].T @ a_next) / D[i]
            a.append(a_next + S * qdd[i])

        return qdd
```

## Frottements (Friction Models)

```python
class FrictionModel:
    """Modèles de frottement pour joints robotiques"""

    @staticmethod
    def viscous_coulomb(qd, fv, fc, fs=0, vs=0.01, sigma=100):
        """
        Modèle combiné : visqueux + Coulomb + Stribeck
        τ_f = fv*qd + fc*tanh(σ*qd) + (fs-fc)*exp(-(qd/vs)²)
        """
        stribeck = (fs - fc) * np.exp(-(qd/vs)**2)
        return fv * qd + fc * np.tanh(sigma * qd) + stribeck

    @staticmethod
    def luGre(z, qd, sigma0, sigma1, sigma2, fc):
        """Modèle LuGre (dynamique) : ż = qd - sigma0*|qd|/fc * z"""
        z_dot = qd - sigma0 * abs(qd) / fc * z
        tau_f = sigma0 * z + sigma1 * z_dot + sigma2 * qd
        return tau_f, z_dot
```

## Contact et Impact

### Modèle de Contact (Spring-Damper Non-Linéaire)
```python
class ContactModel:
    """Modèle de contact pour simulation robotique"""
    def __init__(self, stiffness=1e6, damping=1e3, friction=0.5):
        self.k = stiffness   # raideur de contact (N/m)
        self.b = damping     # amortissement (Ns/m)
        self.mu = friction   # coefficient frottement

    def compute_contact_force(self, penetration_depth, penetration_vel,
                              tangent_vel, normal):
        """
        Calcule la force de contact 3D
        penetration_depth > 0 = en contact
        """
        if penetration_depth <= 0:
            return np.zeros(3)

        # Force normale (Hunt-Crossley)
        fn = (self.k * penetration_depth + self.b * penetration_vel) * normal

        # Force tangentielle (frottement de Coulomb)
        if np.linalg.norm(tangent_vel) > 1e-6:
            direction = tangent_vel / np.linalg.norm(tangent_vel)
            ft = -self.mu * np.linalg.norm(fn) * direction
        else:
            ft = np.zeros(3)

        return fn + ft

    def compute_impulse(self, relative_velocity, restitution=0.3):
        """Modèle d'impact (impulsionnel) — coefficient de restitution"""
        vn = np.dot(relative_velocity, normal)
        if vn >= 0:
            return np.zeros(3)  # séparation

        # Impulsion normale
        jn = -(1 + restitution) * vn / (1/m1 + 1/m2)
        impulse = jn * normal

        # Impulsion tangentielle (frottement)
        vt = relative_velocity - vn * normal
        if np.linalg.norm(vt) > 0:
            jt = min(self.mu * abs(jn), np.linalg.norm(vt) / (1/m1 + 1/m2))
            impulse -= jt * vt / np.linalg.norm(vt)

        return impulse
```

## Identification des Paramètres Dynamiques

### Least Squares pour Identification
```python
class DynamicParameterIdentification:
    """
    Identifie les paramètres inertiels par moindres carrés
    Modèle : τ = Y(q, q̇, q̈) Θ
    Y : matrice de régression (n_observations × n_params)
    Θ : [m₁, m₁c₁, I₁, fv₁, fc₁, ..., m_n, m_nc_n, I_n, fv_n, fc_n]
    """
    def __init__(self, robot):
        self.robot = robot

    def excitation_trajectory(self, duration=20, n_joints=6):
        """
        Génère une trajectoire d'excitation (somme de sinus)
        Optimisée pour maximiser le conditionnement de Y^T Y
        """
        # Trajectoire de Fourier (Swevers et al.)
        # q_i(t) = q0_i + Σ_k a_k/(ω_f*k) * sin(ω_f*k*t) - b_k/(ω_f*k) * cos(ω_f*k*t)
        # Au moins 2×N sinus par joint
        t = np.linspace(0, duration, duration*100)
        q_traj = np.zeros((len(t), n_joints))

        for j in range(n_joints):
            for k in range(1, 6):  # 5 harmoniques
                ak = np.random.uniform(-1, 1)
                bk = np.random.uniform(-1, 1)
                omega_f = 2*np.pi / duration
                q_traj[:, j] += ak/(omega_f*k) * np.sin(omega_f*k*t) - \
                                bk/(omega_f*k) * np.cos(omega_f*k*t)
        return t, q_traj

    def identify(self, q_meas, qd_meas, qdd_meas, tau_meas):
        """
        Identification par moindres carrés pondérés
        Θ = (Y^T W Y)^{-1} Y^T W τ
        """
        Y = self.build_regressor(q_meas, qd_meas, qdd_meas)
        W = np.eye(len(tau_meas))  # pondération

        # Moindres carrés
        YTY = Y.T @ W @ Y
        YTtau = Y.T @ W @ tau_meas

        # Résolution
        Theta = np.linalg.pinv(YTY) @ YTtau

        # Covariance
        residuals = tau_meas - Y @ Theta
        sigma2 = np.var(residuals)
        cov = sigma2 * np.linalg.inv(YTY)

        # Indicateurs de qualité
        cond_number = np.linalg.cond(YTY)

        return Theta, cond_number, residuals
```

### Base Parameters (Paramètres Identifiables)

Tous les paramètres ne sont pas identifiables séparément. Les **base parameters** sont les combinaisons linéaires identifiables (regroupement inertiel).

```
Base Parameters (6+6+5n pour manipulateur plan) :
  - Somme masses
  - Moments d'inertie combinés
  - Produits d'inertie regroupés

Exemple pour robot 2-DOF plan :
  Θ_base = [I₁ + m₁c₁² + m₂(l₁² + 2l₁c₂cos(q₂) + c₂²),
            I₂ + m₂c₂²,
            m₂c₂cos(q₂), ...]
```

## Simulation Dynamique

### Intégrateur Numérique (RK4)
```python
def simulate_robot(dynamics_fn, q0, qd0, tau_fn, dt=0.001, T=5.0):
    """Simulation dynamique d'un robot avec RK4"""
    t = 0.0
    states = [(q0, qd0)]

    while t < T:
        q, qd = states[-1]

        def f(state):
            q, qd = state[:n], state[n:]
            tau = tau_fn(t, q, qd)
            qdd = dynamics_fn(q, qd, tau)
            return np.concatenate([qd, qdd])

        # RK4
        k1 = f(np.concatenate([q, qd]))
        k2 = f(np.concatenate([q + dt/2 * k1[:n], qd + dt/2 * k1[n:]]))
        k3 = f(np.concatenate([q + dt/2 * k2[:n], qd + dt/2 * k2[n:]]))
        k4 = f(np.concatenate([q + dt * k3[:n], qd + dt * k3[n:]]))

        q_next = q + dt/6 * (k1[:n] + 2*k2[:n] + 2*k3[:n] + k4[:n])
        qd_next = qd + dt/6 * (k1[n:] + 2*k2[n:] + 2*k3[n:] + k4[n:])

        states.append((q_next, qd_next))
        t += dt

    return states
```

### Simulation avec Contrainte de Contact
```python
def simulate_with_contact(robot, q, qd, tau, dt, ground_plane):
    """Simulation avec contact au sol"""
    # Étape 1 : intégration libre
    qdd_free = solve_dynamics(robot, q, qd, tau)
    q_temp = q + qd * dt
    qd_temp = qd + qdd_free * dt

    # Étape 2 : détection de contact
    contact_points = detect_contacts(robot.forward_kinematics(q_temp), ground_plane)

    if len(contact_points) > 0:
        # Étape 3 : résolution des contraintes (LCP — Linear Complementarity Problem)
        # M q̈ + J^T λ = τ + Cq̇ + G
        # J q̈ ≥ 0   (pas de pénétration)
        # λ ≥ 0      (forces normales uniquement répulsives)
        # λ^T (J q̈) = 0

        J = compute_contact_jacobian(robot, contact_points)
        M = robot.inertia_matrix(q)
        tau_bias = tau - robot.coriolis(q, qd) - robot.gravity(q)

        # Solveur LCP
        A = J @ np.linalg.inv(M) @ J.T
        b = J @ np.linalg.solve(M, tau_bias)
        lambda_contact = solve_lcp(A, b)  # forces de contact

        # Accélération avec contraintes
        qdd_corrected = np.linalg.solve(M, tau_bias + J.T @ lambda_contact)

        # Intégration avec correction
        q_next = q + qd * dt
        qd_next = qd + qdd_corrected * dt
    else:
        q_next = q_temp
        qd_next = qd_temp

    return q_next, qd_next
```

## Dynamique de Robots Mobiles

### Modèle Unicycle (Differential Drive)
```python
class UnicycleDynamics:
    """Dynamique d'un robot mobile à entraînement différentiel"""
    def __init__(self, mass=10.0, inertia=0.5, wheel_radius=0.05, wheel_base=0.3):
        self.m = mass
        self.I = inertia
        self.r = wheel_radius
        self.L = wheel_base
        self.friction_linear = 1.0
        self.friction_angular = 0.5

    def dynamics(self, state, u):
        """
        state = [x, y, θ, v, ω]
        u = [τ_left, τ_right]  (couples moteurs)
        """
        x, y, theta, v, omega = state
        tau_l, tau_r = u

        # Forces motrices
        F = (tau_l + tau_r) / self.r
        torque = (tau_r - tau_l) * (self.L / (2 * self.r))

        # Dynamique avec frottement
        v_dot = (F - self.friction_linear * v) / self.m
        omega_dot = (torque - self.friction_angular * omega) / self.I

        # Cinématique
        x_dot = v * np.cos(theta)
        y_dot = v * np.sin(theta)
        theta_dot = omega

        return np.array([x_dot, y_dot, theta_dot, v_dot, omega_dot])
```

## Pièges et Bonnes Pratiques

- **RNEA > Lagrange pour l'implémentation** : Newton-Euler récursif est O(n) et plus simple à coder. Lagrange est O(n⁴) sans simplification symbolique. Toujours préférer RNEA/Featherstone pour la simulation temps réel.
- **Inerties mal conditionnées** : si les paramètres d'inertie sont inconnus, le modèle dynamique peut diverger. L'identification expérimentale (excitation trajectory + LS) est cruciale pour la commande computed torque.
- **Frottement non modélisé** : le frottement de Coulomb non modélisé cause des erreurs de tracking basses vitesses. Utiliser LuGre ou au moins un modèle visqueux+Coulomb identifié. Gain Kd élevé en PID compense partiellement mais use les moteurs.
- **Singularité dynamique** : M(q) devient mal conditionné près des singularités cinématiques. L'inverse de M(q) peut exploser numériquement. Ajouter une régularisation (M + εI)⁻¹.
- **Intégration numérique** : RK4 avec dt=1ms pour robots rapides ; Semi-implicit Euler (symplectic) plus stable pour les systèmes mécaniques avec contacts. Pour les robots lents (industriels), dt=5ms suffit.
- **Contact instable** : raideur de contact trop élevée (k > 10⁷) → intégration instable. Solution : solver implicite (ODE15s) ou schéma de contact avec LCP (MuJoCo, Bullet).
- **Base parameters vs full** : n'identifier que les paramètres de base (regroupés). L'identification de tous les paramètres individuels est sous-déterminée et produit des covariances explosives.

## Références

- Featherstone, R. (2008). *Rigid Body Dynamics Algorithms*. Springer. ISBN 978-1489981710
- Craig, J. (2005). *Introduction to Robotics: Mechanics and Control*. Pearson. ISBN 978-0201543612
- Siciliano, B. et al. (2009). *Robotics: Modelling, Planning and Control*. Springer. ISBN 978-1846286414
- Swevers, J. et al. (2007). Optimal Robot Excitation and Identification. *IEEE Trans. Robotics*, 23(3), 484-496.
- Todorov, E. (2014). Convex and Analytically-Invertible Dynamics with Contacts (MuJoCo). *IEEE ICRA 2014*.
- Murray, R., Li, Z. & Sastry, S. (1994). *A Mathematical Introduction to Robotic Manipulation*. CRC Press. ISBN 978-0849379819