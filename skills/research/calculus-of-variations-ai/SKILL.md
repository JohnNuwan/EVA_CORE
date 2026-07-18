---
name: calculus-of-variations-ai
title: Calcul Variationnel Appliqué à l'IA
description: >-
  Implémenter des techniques de calcul variationnel pour optimiser des systèmes
  dynamiques dans l'IA, la robotique et le contrôle optimal.
version: 2.0.0
author: Helios Agent
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
dependencies:
  - numpy>=1.24
  - scipy>=1.11
  - matplotlib>=3.7
  - sympy>=1.12
metadata:
  helios:
    tags:
      - calculus-of-variations
      - euler-lagrange
      - optimal-control
      - trajectory-optimization
      - dynamical-systems
      - mathematical-optimization
    category: research
    related_skills:
      - optimization-with-graph-theory
      - multi-agent-systems-research
      - ai-foundations-exploration
    requires_toolsets: [terminal, files, execute_code]
---

# Calcul Variationnel Appliqué à l'IA

## Vue d'Ensemble

Le **calcul des variations** est une branche des mathématiques qui généralise le calcul différentiel à des espaces de fonctions. Au lieu de trouver un scalaire $x$ qui minimise $f(x)$, on cherche une **fonction** $y(x)$ qui minimise une **fonctionnelle** $J[y]$. Cette discipline est au cœur de nombreux problèmes d'IA et de robotique :

- **Optimisation de trajectoires** : trouver le chemin optimal d'un bras robotique ou d'un drone avec contraintes énergétiques.
- **Apprentissage par renforcement** : les équations de Hamilton-Jacobi-Bellman sont issues du calcul variationnel.
- **Régularisation de modèles** : les pénalités de lissage (Sobolev, TV) sont des fonctionnelles.
- **Contrôle optimal** : minimiser une fonction de coût sur un horizon temporel.
- **Systèmes multi-agents** : coordination et formation optimale de groupes d'agents.

Cette compétence fournit les fondements théoriques, les implémentations numériques et les patrons de résolution pour appliquer le calcul variationnel dans des contextes d'IA.

---

## Quand l'utiliser

| Situation | Exemple |
|-----------|---------|
| Optimiser une trajectoire sous contrainte | Chemin d'un drone avec budget énergétique limité |
| Résoudre un problème de contrôle optimal | Commande d'un bras robotique avec coût quadratique |
| Régulariser un modèle d'apprentissage | Contrainte de lissage sur une fonction de potentiel |
| Planifier un mouvement multi-agents | Formation optimale d'un essaim de robots |
| Résoudre un problème isopérimétrique | Maximiser l'aire sous une contrainte de périmètre |

---

## 1. Fondements Théoriques

### 1.1 Fonctionnelle et Première Variation

Une **fonctionnelle** est une application d'un espace de fonctions vers $\mathbb{R}$ :

$$
J[y] = \int_a^b L(x, y(x), y'(x)) \, dx
$$

La **première variation** $\delta J[y, \eta]$ généralise la dérivée directionnelle :

$$
\delta J[y, \eta] = \left. \frac{d}{d\varepsilon} J[y + \varepsilon\eta] \right|_{\varepsilon=0}
$$

Si $y^*$ est un extremum de $J$, alors $\delta J[y^*, \eta] = 0$ pour toute variation admissible $\eta$.

### 1.2 Équation d'Euler-Lagrange

La condition nécessaire d'optimalité est donnée par l'**équation d'Euler-Lagrange** :

$$
\frac{\partial L}{\partial y} - \frac{d}{dx}\left( \frac{\partial L}{\partial y'} \right) = 0
$$

**Dérivation intuitive :** En intégrant par parties la première variation, on obtient :

$$
\delta J = \int_a^b \left( \frac{\partial L}{\partial y} - \frac{d}{dx}\frac{\partial L}{\partial y'} \right) \eta \, dx + \left[ \frac{\partial L}{\partial y'} \eta \right]_a^b = 0
$$

Comme $\eta$ est arbitraire (sauf aux bornes où $\eta(a) = \eta(b) = 0$ pour des conditions fixes), le terme intégral doit être nul, d'où Euler-Lagrange.

### 1.3 Contraintes Isopérimétriques

Une contrainte de la forme :

$$
\int_a^b G(x, y, y') \, dx = C
$$

est traitée avec un **multiplicateur de Lagrange** $\lambda$ :

$$
\tilde{J}[y] = \int_a^b \big( L(x, y, y') + \lambda G(x, y, y') \big) \, dx
$$

L'équation d'Euler-Lagrange modifiée devient :

$$
\frac{\partial L}{\partial y} + \lambda \frac{\partial G}{\partial y} - \frac{d}{dx}\left( \frac{\partial L}{\partial y'} + \lambda \frac{\partial G}{\partial y'} \right) = 0
$$

### 1.4 Conditions aux Limites Naturelles

Si les extrémités ne sont pas fixées, on impose les **conditions de transversalité** :

$$
\left. \frac{\partial L}{\partial y'} \right|_{x=a} = 0, \quad
\left. \frac{\partial L}{\partial y'} \right|_{x=b} = 0
$$

---

## 2. Exemples Classiques Résolus

### 2.1 Plus Courte Distance Entre Deux Points

La fonctionnelle est la longueur d'arc :

$$
J[y] = \int_a^b \sqrt{1 + y'(x)^2} \, dx
$$

Le lagrangien $L = \sqrt{1 + y'^2}$ ne dépend pas explicitement de $y$. La première intégrale d'Euler-Lagrange donne :

$$
L - y' \frac{\partial L}{\partial y'} = \text{constante}
$$

Soit $\frac{1}{\sqrt{1 + y'^2}} = C$, donc $y'$ est constant. La solution est une **droite** $y(x) = mx + c$.

### 2.2 Problème de la Brachistochrone

Trouver la courbe reliant deux points $A$ et $B$ telle qu'une masse glissant sans frottement sous la gravité aille de $A$ à $B$ dans le **temps minimal**.

$$
J[y] = \int_a^b \sqrt{\frac{1 + y'(x)^2}{2 g y(x)}} \, dx
$$

La solution est une **cycloïde** paramétrée par :

$$
\begin{cases}
x(\theta) = R(\theta - \sin\theta) \\
y(\theta) = R(1 - \cos\theta)
\end{cases}
$$

### 2.3 Problème Isopérimétrique : Surface Minimale

Minimiser l'aire de révolution engendrée par une courbe $y(x)$ entre deux points, avec une longueur d'arc fixée $L$ :

$$
J[y] = 2\pi \int_a^b y \sqrt{1 + y'^2} \, dx, \quad
\int_a^b \sqrt{1 + y'^2} \, dx = L
```

La solution est une **caténaire** $y(x) = c \cosh((x - x_0)/c)$.

### 2.4 Contrôle Optimal Linéaire-Quadratique (LQR)

Pour un système dynamique $\dot{x} = Ax + Bu$ avec coût :

\[
J = \int_0^T (x^T Q x + u^T R u) \, dt + x(T)^T S x(T)
$$

L'équation d'Euler-Lagrange sur le Hamiltonien $H = x^T Q x + u^T R u + p^T(Ax + Bu)$ donne :

$$
\dot{p} = -\frac{\partial H}{\partial x} = -2Qx - A^T p, \quad
\frac{\partial H}{\partial u} = 2Ru + B^T p = 0
$$

Soit la loi de commande optimale $u^* = -\frac{1}{2}R^{-1}B^T p$.

---

## 3. Implémentation Numérique

### 3.1 Discrétisation par Différences Finies

La méthode la plus simple consiste à discrétiser la fonction $y(x)$ sur une grille et à utiliser `scipy.optimize` :

```python
import numpy as np
from scipy.optimize import minimize
from scipy.integrate import quad

def solve_covariation(L_func, a, b, n=100, constraints=None):
    """Résout un problème variationnel par discrétisation.

    Args:
        L_func: Fonction L(x, y, dy) représentant le lagrangien.
        a, b: Bornes de l'intervalle.
        n: Nombre de points de discrétisation.
        constraints: Liste de contraintes isopérimétriques optionnelles.

    Returns:
        tuple: (x_grille, y_optimale)
    """
    x = np.linspace(a, b, n)
    dx = x[1] - x[0]

    def objective(y):
        dy = np.gradient(y, dx)
        integrand = np.array([L_func(x[i], y[i], dy[i]) for i in range(n)])
        return np.trapz(integrand, x)

    # Conditions aux limites fixes
    bounds = [(None, None)] * n

    # Contrainte isopérimétrique optionnelle
    cons = []
    if constraints is not None:
        for G_func, C_val in constraints:
            def constraint(y, G=G_func, C=C_val):
                dy = np.gradient(y, dx)
                vals = np.array([G(x[i], y[i], dy[i]) for i in range(n)])
                return np.trapz(vals, x) - C
            cons.append({'type': 'eq', 'fun': constraint})

    y0 = np.ones(n)  # Devine initiale
    result = minimize(objective, y0, method='SLSQP',
                      bounds=bounds, constraints=cons,
                      options={'maxiter': 1000, 'ftol': 1e-8})

    return x, result.x


# Exemple : minimiser J = ∫(½y'² - f(x)y)dx sous contrainte ∫y'²dx = C
def lagrangian(x, y, dy):
    f = np.cos(x)
    return 0.5 * dy**2 - f * y

x_opt, y_opt = solve_covariation(
    lagrangian, 0, 10, n=100,
    constraints=[(lambda x, y, dy: dy**2, 1.0)]
)

print(f"Solution optimale : {y_opt[:5]}...")
```

### 3.2 Méthode de Tir (Shooting) pour Conditions aux Limites

Pour les problèmes avec conditions aux limites aux deux extrémités :

```python
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve

def shooting_method(euler_lagrange_ode, a, b, ya, yb, guess, n=100):
    """Méthode de tir pour résoudre l'équation d'Euler-Lagrange.

    Args:
        euler_lagrange_ode: Fonction f(x, y, y') pour l'ODE du second ordre.
        a, b: Bornes.
        ya, yb: Valeurs aux limites.
        guess: Estimation initiale de y'(a).
        n: Nombre de points.

    Returns:
        tuple: (x, y)
    """
    def ode_system(x, state):
        y, dy = state
        ddy = euler_lagrange_ode(x, y, dy)
        return [dy, ddy]

    def boundary_residual(dy_a):
        sol = solve_ivp(ode_system, (a, b), [ya, dy_a[0]],
                        t_eval=np.linspace(a, b, n))
        return [sol.y[0, -1] - yb]

    dy_a_opt = fsolve(boundary_residual, [guess])
    sol = solve_ivp(ode_system, (a, b), [ya, dy_a_opt[0]],
                    t_eval=np.linspace(a, b, n))

    return sol.t, sol.y[0]
```

### 3.3 Méthode Symbolique avec SymPy

Pour les cas où une solution analytique est accessible :

```python
import sympy as sp

def euler_lagrange_symbolic(L_expr, y_sym, x_sym):
    """Calcule l'équation d'Euler-Lagrange de manière symbolique.

    Args:
        L_expr: Expression sympy du lagrangien L(x, y, y').
        y_sym: Fonction symbole y(x).
        x_sym: Variable indépendante x.

    Returns:
        Expression sympy de l'équation d'Euler-Lagrange.
    """
    yp = sp.diff(y_sym, x_sym)
    dL_dy = sp.diff(L_expr, y_sym)
    dL_dyp = sp.diff(L_expr, yp)
    euler_eq = sp.simplify(dL_dy - sp.diff(dL_dyp, x_sym))
    return sp.Eq(euler_eq, 0)


# Exemple : brachistochrone
x = sp.symbols('x')
y = sp.Function('y')
g = sp.symbols('g', positive=True)
L = sp.sqrt((1 + sp.diff(y(x), x)**2) / (2 * g * y(x)))

eq = euler_lagrange_symbolic(L, y(x), x)
sp.pprint(eq)
```

### 3.4 Optimisation de Trajectoire avec Contrôle Optimal Direct

Pour des problèmes de robotique avec commande $u(t)$ :

```python
import numpy as np
from scipy.optimize import minimize

def trajectory_optimization(dynamics, cost_func, x0, xf, T, n_steps=50):
    """Optimise une trajectoire avec commande.

    Args:
        dynamics: Fonction f(x, u) → dx/dt.
        cost_func: Fonction de coût instantané L(x, u).
        x0, xf: États initial et final.
        T: Horizon temporel.
        n_steps: Nombre de pas de temps.

    Returns:
        tuple: (temps, états optimaux, commandes optimales)
    """
    dt = T / n_steps
    n_states = len(x0)
    n_controls = 2  # Exemple : acceleration angulaire, force

    def objective(z):
        states = z[:n_states * n_steps].reshape(n_steps, n_states)
        controls = z[n_states * n_steps:].reshape(n_steps, n_controls)

        # Coût terminal (atteindre xf)
        terminal_cost = 1000 * np.sum((states[-1] - xf)**2)

        # Coût instantané
        running_cost = sum(
            cost_func(states[i], controls[i]) * dt
            for i in range(n_steps)
        )
        return terminal_cost + running_cost

    def constraint(z):
        states = z[:n_states * n_steps].reshape(n_steps, n_states)
        controls = z[n_states * n_steps:].reshape(n_steps, n_controls)

        # Dynamique : x_{k+1} = x_k + f(x_k, u_k) * dt
        cons = []
        for i in range(1, n_steps):
            dx = dynamics(states[i-1], controls[i-1])
            cons.extend(states[i] - states[i-1] - dx * dt)
        return np.array(cons)

    # Devine initiale : interpolation linéaire
    guess_states = np.linspace(x0, xf, n_steps).flatten()
    guess_controls = np.zeros(n_steps * n_controls)
    z0 = np.concatenate([guess_states, guess_controls])

    # Contrainte de dynamique
    cons = [{'type': 'eq', 'fun': constraint,
             'jac': '2-point'}]

    result = minimize(objective, z0, method='SLSQP',
                      constraints=cons,
                      options={'maxiter': 5000, 'ftol': 1e-6})

    t = np.linspace(0, T, n_steps)
    states_opt = result.x[:n_states * n_steps].reshape(n_steps, n_states)
    controls_opt = result.x[n_states * n_steps:].reshape(n_steps, n_controls)

    return t, states_opt, controls_opt
```

---

## 4. Applications en IA et Robotique

### 4.1 Apprentissage par Renforcement et HJB

L'équation de **Hamilton-Jacobi-Bellman** en RL continu est une extension directe :

$$
-\frac{\partial V}{\partial t} = \min_u \left( L(x, u) + \nabla V \cdot f(x, u) \right)
```

où $V$ est la fonction de valeur et $f$ la dynamique. La condition de minimum donne la loi de commande optimale, exactement comme la condition de stationnarité en calcul variationnel.

### 4.2 Régularisation par Variation Totale

En traitement d'images et en IA générative, la régularisation TV (Total Variation) s'écrit :

\[
J[u] = \int_\Omega |\nabla u| \, dx + \frac{\lambda}{2} \int_\Omega (u - f)^2 \, dx
$$

L'équation d'Euler-Lagrange correspondante donne le flot de diffusion :

$$
-\nabla \cdot \left( \frac{\nabla u}{|\nabla u|} \right) + \lambda (u - f) = 0
```

### 4.3 Systèmes Multi-Agents et Formation Optimale

Pour $N$ agents avec positions $p_i(t)$, la formation optimale minimise :

\[
J[\{p_i\}] = \int_0^T \sum_{i=1}^N \left( \frac{1}{2} \|\dot{p}_i\|^2 + \sum_{j \neq i} V(\|p_i - p_j\|) \right) dt
$$

où $V$ est un potentiel d'interaction (attraction-répulsion). Les équations d'Euler-Lagrange donnent directement les lois de commande décentralisées.

### 4.4 Neural ODE et Contrôle Continu

Les Neural ODE (Chen et al., 2018) paramètrent la dynamique par un réseau de neurones :

$$
\frac{dh}{dt} = f_\theta(h(t), t)
$$

L'entraînement minimise une fonctionnelle de coût via la méthode adjointe, qui est une application directe du calcul variationnel :

$$
\frac{d\lambda}{dt} = -\lambda^T \frac{\partial f_\theta}{\partial h}, \quad
\lambda(T) = \frac{\partial \mathcal{L}}{\partial h(T)}
$$

---

## 5. Pièges Courants

| Piège | Symptôme | Solution |
|-------|----------|----------|
| **Conditions aux limites oubliées** | Solution ne respecte pas les extrémités | Vérifier les conditions de transversalité ; utiliser `bounds=` dans l'optimiseur |
| **Mauvais conditionnement numérique** | L'optimiseur ne converge pas | Normaliser les variables ; utiliser des échelles adaptées |
| **Contrainte isopérimétrique mal posée** | La contrainte n'est jamais satisfaite | Vérifier que $C$ est physiquement réalisable ; ajouter une pénalité quadratique |
| **Minimum local au lieu de global** | Solution sous-optimale visible | Multi-départs aléatoires ; utiliser une devine initiale physique |
| **Singularité dans le lagrangien** | Dérivées infinies ou NaN | Régulariser : ajouter $\varepsilon \|y'\|^2$ au lagrangien |
| **Méthode de tir instable** | L'ODE diverge pour certaines conditions initiales | Utiliser une méthode de différences finies à la place |
| **Oubli des contraintes d'inégalité** | Trajectoire non physique ($y < 0$) | Ajouter des contraintes d'inégalité : $y(x) \geq 0$ |
| **Discrétisation trop grossière** | Solution numérique imprécise | Augmenter $n$ et vérifier la convergence |

---

## 6. Checklist d'Implémentation

- [ ] La fonctionnelle $J[y]$ est définie avec son lagrangien $L(x, y, y')$.
- [ ] Les conditions aux limites sont spécifiées (fixes, libres, ou mixtes).
- [ ] Les multiplicateurs de Lagrange sont introduits pour les contraintes isopérimétriques.
- [ ] L'équation d'Euler-Lagrange est dérivée analytiquement ou numériquement.
- [ ] La discrétisation est suffisamment fine (test de convergence : doubler $n$ et vérifier la stabilité).
- [ ] L'optimiseur SLSQP ou une méthode de tir est implémenté.
- [ ] Les contraintes d'inégalité sont gérées (bornes, non-négativité).
- [ ] La solution est validée sur un cas test connu (brachistochrone, géodésique).
- [ ] Les dérivées numériques sont vérifiées (gradient versus différences finies).
- [ ] Le coût final et les métriques (énergie, temps, longueur) sont rapportés.
- [ ] La visualisation de la trajectoire optimale est produite.
- [ ] Les résultats sont exportés dans un format reproductible (JSON, NumPy).

---

## Références

1. Gelfand, I. M., & Fomin, S. V. (1963). *Calculus of Variations*. Dover Publications.
2. Liberzon, D. (2012). *Calculus of Variations and Optimal Control Theory*. Princeton University Press.
3. Chen, R. T., Rubanova, Y., Bettencourt, J., & Duvenaud, D. (2018). Neural Ordinary Differential Equations. *NeurIPS 2018*.
4. Pontryagin, L. S. (1962). *The Mathematical Theory of Optimal Processes*. Wiley.
5. Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
