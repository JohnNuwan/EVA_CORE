---
name: jax
description: Guide complet de JAX — JIT, vmap, grad, pmap, Haiku/Flax, transformations de programmes, calcul numérique haute performance. En français.
---

# JAX — Guide Complet (Français)

JAX = NumPy + Autograd + XLA. Calcul numérique accéléré GPU/TPU avec différenciation automatique.

---

## 1. Installation et Concepts

```bash
pip install jax jaxlib       # CPU
pip install jax[cuda12]      # GPU NVIDIA
pip install optax flax       # Optimiseur + réseaux de neurones
```

### Principes fondamentaux
- **JAX = NumPy accéléré** : API identique à NumPy mais en XLA
- **JIT** : compilation Just-In-Time vers XLA (accélération GPU/TPU)
- **grad** : différenciation automatique (avant et arrière)
- **vmap** : vectorisation automatique (batching)
- **pmap** : parallélisation multi-appareils
- **Fonctions pures** : pas d'effets de bord, immutabilité

---

## 2. NumPy avec JAX

```python
import jax
import jax.numpy as jnp

# Arrays JAX (immutables)
x = jnp.array([1.0, 2.0, 3.0])
y = jnp.ones((3, 3))
z = jnp.zeros_like(x)

# Opérations comme NumPy
resultat = jnp.dot(y, x)
carres = jnp.square(x)

# Générateurs aléatoires (explicites, purs)
from jax import random
cle = random.PRNGKey(42)
cle, sous_cle = random.split(cle)
donnees = random.normal(sous_cle, (100, 10))

# Conversion NumPy ↔ JAX
import numpy as np
jax_array = jnp.array(np_array)
np_array = np.array(jax_array)
```

---

## 3. JIT — Compilation Just-In-Time

```python
from jax import jit
import time

@jit
def fonction_lourde(x: jnp.ndarray) -> jnp.ndarray:
    """Compilée en XLA à la première exécution."""
    return jnp.sum(jnp.sin(x) * jnp.cos(x))


# Première exécution : compilation + exécution (lent)
x = jnp.arange(1_000_000.0)
resultat = fonction_lourde(x)  # ~200ms (compilation)
resultat = fonction_lourde(x)  # ~0.5ms (compilé !)

# JIT avec arguments statiques
@jit
def puissance(x, n):
    return x ** n

# n=2 devient une constante dans le code compilé
# (mais il faut recompiler si n change)

# Avec static_argnums
@partial(jit, static_argnums=(1,))
def repeter(fonction, n):
    for _ in range(n):
        ...
```

---

## 4. Grad — Différenciation Automatique

```python
from jax import grad, value_and_grad, jacfwd, jacrev, hessian

# Gradient d'une fonction scalaire
def f(x):
    return jnp.sum(x ** 2)

grad_f = grad(f)
print(grad_f(jnp.array([1.0, 2.0, 3.0])))  # [2, 4, 6] = 2x

# Gradient + valeur en un seul appel
valeur, gradient = value_and_grad(f)(x)

# Gradient d'ordre supérieur
grad2_f = grad(grad(f))     # Hessienne

# Jacobienne
jacobienne_avant = jacfwd(f)(x)  # Mode forward (peu de paramètres)
jacobienne_arriere = jacrev(f)(x) # Mode reverse (peu de sorties)

# Hessienne
hessienne = hessian(f)(x)

# Gradient avec paramètres supplémentaires
def perte(params, x, y):
    return jnp.sum((x @ params - y) ** 2)

grad_perte = grad(perte)

# Gradient par rapport à un argument spécifique
grad_perte_params = grad(perte, argnums=0)  # ∂/∂params
```

---

## 5. Vmap — Vectorisation Automatique

```python
from jax import vmap

# Fonction qui opère sur un scalaire
def traiter_element(x: float) -> float:
    return jnp.sin(x) * jnp.exp(-x)

# Vectoriser automatiquement (batch dimension en première position)
traiter_batch = vmap(traiter_element)
x_batch = jnp.linspace(0, 10, 100)
resultats = traiter_batch(x_batch)  # Équivalent à une boucle, mais parallèle

# Vmap avec paramètres supplémentaires
def predire(params, x):
    return jnp.dot(x, params)

# Batcher sur plusieurs arguments
predire_batch = vmap(predire, in_axes=(None, 0))  # params fixe, x batché
predire_batch = vmap(predire, in_axes=(0, 0))     # Les deux batchés

# Vmap composé avec JIT et Grad
@jit
@vmap
@grad
def pipeline(x):
    ...

# Vmap sur des batches de matrices (in_axes contrôle les dimensions)
vmap(lambda x, y: x @ y, in_axes=(0, 0))(matrices_a, matrices_b)
```

---

## 6. Réseaux de Neurones avec Flax

```python
import flax.linen as nn
import optax

class MLP(nn.Module):
    """Perceptron multicouche avec Flax.
    
    Attributes:
        taille_cachee: Nombre de neurones par couche cachée.
        taille_sortie: Dimension de la sortie.
    """
    
    taille_cachee: int = 128
    taille_sortie: int = 10
    
    @nn.compact
    def __call__(self, x: jnp.ndarray) -> jnp.ndarray:
        x = nn.Dense(self.taille_cachee)(x)
        x = nn.relu(x)
        x = nn.Dense(self.taille_cachee)(x)
        x = nn.relu(x)
        x = nn.Dense(self.taille_sortie)(x)
        return x

# Initialisation
modele = MLP(taille_cachee=256, taille_sortie=10)
cle = random.PRNGKey(0)
x = jnp.ones((1, 784))
params = modele.init(cle, x)

# Forward pass
sortie = modele.apply(params, x)

# Entraînement
@jit
def etape_entrainement(params, opt_state, x, y):
    def perte(params):
        predictions = modele.apply(params, x)
        return jnp.mean(optax.softmax_cross_entropy(
            logits=predictions, labels=y
        ))
    
    valeur_perte, grads = value_and_grad(perte)(params)
    mises_a_jour, opt_state = optimiseur.update(grads, opt_state)
    params = optax.apply_updates(params, mises_a_jour)
    return params, opt_state, valeur_perte

# Optimiseur
optimiseur = optax.adam(learning_rate=1e-3)
opt_state = optimiseur.init(params)
```

---

## 7. Pm distributed

```python
from jax import pmap, devices

# Distribution sur plusieurs GPU/TPU
@pmap
def entrainement_distribue(params, x, y):
    perte = calculer_perte(params, x, y)
    grads = grad(calculer_perte)(params, x, y)
    # Les gradients sont moyennés automatiquement
    return jax.lax.pmean(grads, axis_name='devices')

# Avec Flax
@functools.partial(pmap, axis_name='batch')
def etape_entrainement(params, x, y):
    def perte_fn(params):
        return jnp.mean(optax.softmax_cross_entropy(
            logits=modele.apply(params, x), labels=y
        ))
    
    perte, grads = value_and_grad(perte_fn)(params)
    grads = jax.lax.pmean(grads, axis_name='batch')
    return perte, grads
```

---

## 8. Lax — Opérations Bas Niveau

```python
from jax import lax

# Boucles compilées
def boucle_while(x):
    def condition(etat):
        return etat < 100
    
    def corps(etat):
        return etat * 2
    
    return lax.while_loop(condition, corps, x)

# Scan (fold avec état)
def scan_exemple(porteur, x):
    nouveau_porteur = porteur + x
    return nouveau_porteur, nouveau_porteur

initial = 0
porteur_final, sequence = lax.scan(scan_exemple, initial, jnp.arange(5))
# sequence = [0, 1, 3, 6, 10]

# Fori_loop (for sur indices)
def corps(i, val):
    return val + i

lax.fori_loop(0, 10, corps, 0)  # 45

# Opérations de réduction parallèles
lax.psum(x, axis_name='devices')  # Somme distribuée
lax.pmean(x, axis_name='devices')  # Moyenne distribuée
```

---

## 9. Pytree

```python
# Toute structure imbriquée (dict, list, tuple, dataclass)
pytree = {
    'params': {
        'dense1': {'w': jnp.ones((10, 10)), 'b': jnp.zeros(10)},
        'dense2': {'w': jnp.ones((10, 1)), 'b': jnp.zeros(1)},
    },
    'config': {'lr': 0.01},
}

# Appliquer une fonction à toutes les feuilles
nouvel_arbre = jax.tree_map(lambda x: x * 2, pytree)

# Aplatir
feuilles, structure = jax.tree_flatten(pytree)

# Reconstruire
reconstruit = jax.tree_unflatten(structure, feuilles)
```

---

## 10. Bonnes Pratiques JAX

1. **Fonctions pures** — pas d'effets de bord, pas de mutation
2. **JIT tôt** — décorer les fonctions critiques avec `@jit`
3. **static_argnums** — pour les paramètres qui ne changent pas
4. **PRNGKeys** — toujours passer la clé aléatoire explicitement
5. **vmap > boucles** — vectoriser plutôt que boucler
6. **Éviter les structures Python** dans les fonctions JIT (if/for dynamiques)
7. **Utiliser `lax.switch`** plutôt que if/elif dans le code JIT
8. **Profiler avec `jax.profiler`** pour optimiser la compilation XLA

---

## Références
- JAX docs : https://jax.readthedocs.io/
- Flax : https://flax.readthedocs.io/
- Optax : https://optax.readthedocs.io/
- JAX Cheat Sheet : https://jax.readthedocs.io/en/latest/jax-101/