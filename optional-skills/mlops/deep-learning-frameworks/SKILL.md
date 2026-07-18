---
name: deep-learning-frameworks
description: "Programmer sous PyTorch, TensorFlow, JAX et Diffusers."
version: 1.1.0
author: Actemium
license: MIT
platforms: [linux, macos, windows]
metadata:
  tags: [pytorch, tensorflow, keras, jax, stable-baselines, diffusers, reinforcement-learning, stable-diffusion]
  related_skills: [data-analysis-exploration, simplify-code]
---

# Apprentissage Profond & MLOps (PyTorch, TensorFlow, JAX, SB3, Stable Diffusion)

## Vue d'ensemble

L'implémentation de solutions d'intelligence artificielle modernes s'appuie sur des architectures variées allant des réseaux de neurones classiques au traitement d'images génératif et à l'apprentissage par renforcement. Cette compétence fournit des recettes de code rigoureuses et des bonnes pratiques opérationnelles pour :
- **PyTorch** & **TensorFlow/Keras** (Optimisation mémoire et pipelines de données).
- **JAX** (Paradigme fonctionnel pur et compilation XLA).
- **Stable-Baselines3** (Apprentissage par renforcement sur environnements Gymnasium).
- **Stable Diffusion** (IA générative d'images via la bibliothèque Diffusers).

---

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Concevoir, entraîner ou optimiser des réseaux de neurones (MLP, CNN, Transformers,RL , RNN , GNN).
- Implémenter des algorithmes de contrôle ou de décision basés sur l'apprentissage par renforcement (PPO, DQN).
- Déployer des modèles de génération d'images ou d'inpainting/outpainting (Stable Diffusion, SDXL, Flux).
- Gérer l'accélération matérielle (CUDA, MPS) et les optimisations mémoire sous-jacentes.

---

## 1. PyTorch : Gestion Mémoire et Entraînement Optimisé

PyTorch utilise un graphe de calcul dynamique (Eager execution). L'entraînement à grande échelle nécessite une gestion mémoire GPU stricte pour éviter les erreurs `OutOfMemory` (OOM).

### Recette d'entraînement robuste avec Précision Mixte et CPU Pinning :
```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

class NeuralNetwork(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, output_dim)
        )
    def forward(self, x):
        return self.net(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = NeuralNetwork(10, 1).to(device)

# Dataset et DataLoader avec Pinning mémoire
dataset = TensorDataset(torch.randn(1000, 10), torch.randn(1000, 1))
loader = DataLoader(dataset, batch_size=32, shuffle=True, pin_memory=True)

optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
criterion = nn.MSELoss()
scaler = torch.cuda.amp.GradScaler(enabled=(device.type == "cuda"))

model.train()
for epoch in range(5):
    for x_batch, y_batch in loader:
        x_batch = x_batch.to(device, non_blocking=True)
        y_batch = y_batch.to(device, non_blocking=True)
        
        optimizer.zero_grad(set_to_none=True) # Libère la mémoire des gradients précédents
        
        with torch.cuda.amp.autocast(enabled=(device.type == "cuda")):
            predictions = model(x_batch)
            loss = criterion(predictions, y_batch)
            
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
```

---

## 2. TensorFlow & Keras : Pipelines de Données et Traces de Graphes

Keras fournit des abstractions de haut niveau tandis que `tf.data` permet de créer des pipelines d'acquisition asynchrones performants.

### Recette Keras Subclassing & Optimisation Pipeline `tf.data` :
```python
import tensorflow as tf
from tensorflow.keras import layers, Model

def create_dataset(features, labels, batch_size=32):
    dataset = tf.data.Dataset.from_tensor_slices((features, labels))
    dataset = dataset.cache()
    dataset = dataset.shuffle(buffer_size=1000)
    dataset = dataset.batch(batch_size)
    dataset = dataset.prefetch(buffer_size=tf.data.AUTOTUNE) # Chargement asynchrone
    return dataset

class CustomModel(Model):
    def __init__(self):
        super().__init__()
        self.dense1 = layers.Dense(64, activation="relu")
        self.dense2 = layers.Dense(1)
        
    def call(self, inputs):
        x = self.dense1(inputs)
        return self.dense2(x)

model = CustomModel()
model.compile(optimizer="adam", loss="mse")

@tf.function # Compile l'étape en graphe statique XLA
def train_step(x, y):
    with tf.GradientTape() as tape:
        logits = model(x, training=True)
        loss_value = model.loss(y, logits)
    grads = tape.gradient(loss_value, model.trainable_weights)
    model.optimizer.apply_gradients(zip(grads, model.trainable_weights))
    return loss_value
```

---

## 3. JAX : Immuabilité Stricte et Transformations Fonctionnelles (JIT, VMAP)

JAX repose sur la programmation fonctionnelle pure : les structures de données y sont strictement immuables et les transformations de fonctions sont appliquées à l'aide du compilateur XLA.

### Recette d'optimisation JAX :
```python
import jax
import jax.numpy as jnp

# 1. Gestion explicite des clés de hasard (PRNG) - JAX est sans état
key = jax.random.PRNGKey(42)
key, subkey = jax.random.split(key)

# 2. Immuabilité : pas de modification de tableau sur place
x = jnp.zeros((5,))
# Écriture correcte : retourne un NOUVEAU tableau modifié
x_new = x.at[0].set(10.0)

# 3. Définition de fonction pure et calcul du gradient
def loss_fn(weights, x, y):
    prediction = jnp.dot(x, weights)
    return jnp.mean((prediction - y) ** 2)

weights = jax.random.normal(subkey, (3,))
x_sample = jnp.array([1.0, 2.0, 3.0])
y_sample = jnp.array(5.0)

# 4. Transformations JAX : Différenciation (grad) et JIT compilation
grad_fn = jax.grad(loss_fn) # Calcule les gradients par rapport aux poids
fast_grad_fn = jax.jit(grad_fn) # Compile la fonction avec XLA pour GPU/TPU

gradients = fast_grad_fn(weights, x_sample, y_sample)

# 5. Vectorisation automatique avec vmap (application sur un batch de données)
# in_axes=(None, 0, 0) -> n'applique pas la vectorisation sur les poids (None)
# mais applique sur la dimension 0 de x et y.
batched_loss_fn = jax.vmap(loss_fn, in_axes=(None, 0, 0))
```

---

## 4. Apprentissage par Renforcement : Stable-Baselines3 (SB3)

Stable-Baselines3 propose des implémentations fiables d'algorithmes d'apprentissage par renforcement (PPO, DQN, SAC) s'appuyant sur l'interface d'environnement **Gymnasium**.

### Recette d'entraînement et de sauvegarde avec SB3 et Gymnasium :
```python
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.monitor import Monitor

# 1. Création et enveloppement (Wrapper) de l'environnement
env = gym.make("CartPole-v1", render_mode="rgb_array")
env = Monitor(env) # Requis pour suivre les métriques dans les callbacks

# 2. Configuration d'un callback d'évaluation périodique
eval_callback = EvalCallback(
    env,
    best_model_save_path="./logs/best_model",
    log_path="./logs/",
    eval_freq=5000,
    deterministic=True,
    render=False
)

# 3. Instanciation de l'agent PPO avec un réseau de neurones MLP (Multi-Layer Perceptron)
model = PPO(
    policy="MlpPolicy",
    env=env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    verbose=1,
    tensorboard_log="./tb_logs/"
)

# 4. Apprentissage de l'agent
model.learn(total_timesteps=10000, callback=eval_callback)

# 5. Sauvegarde et chargement du modèle
model.save("ppo_cartpole_model")
del model # Suppression de l'instance pour simuler un redémarrage

# Chargement à chaud
loaded_model = PPO.load("ppo_cartpole_model", env=env)
```

---

## 5. IA Générative : Image Generation via Stable Diffusion (Diffusers)

La bibliothèque HuggingFace `diffusers` permet d'exécuter des modèles de diffusion (Stable Diffusion 1.5, SDXL, Flux) de façon optimisée sur du matériel grand public.

### Recette Text-to-Image avec SDXL et optimisations de mémoire VRAM :
```python
import torch
from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler

# 1. Chargement de la pipeline en précision float16 (économise 50% de mémoire VRAM)
pipe = StableDiffusionXLPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    variant="fp16"
)

# 2. Configuration d'un scheduler performant (DPM-Solver Multistep) pour réduire le nombre d'étapes
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

# 3. Activation des optimisations mémoire critiques
pipe.enable_model_cpu_offload()       # Décharge les composants du GPU vers le CPU hors calcul
pipe.enable_attention_slicing()       # Découpe le calcul d'attention pour éviter les pics de VRAM
pipe.enable_vae_tiling()              # Découpe l'encodage/décodage VAE en tuiles pour les grandes résolutions

# 4. Génération de l'image
prompt = "A modern clean automated assembly line in a factory, hyper-realistic, 8k resolution"
negative_prompt = "blurry, low quality, drawing, sketch, deformed machinery"

generator = torch.Generator(device="cuda").manual_seed(42) # Reproductibilité

image = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=25, # DPM-Solver nécessite seulement 20-30 étapes
    guidance_scale=7.5,     # Respect strict du prompt
    generator=generator,
    height=1024,
    width=1024
).images[0]

image.save("factory_assembly_line.png")
```

---

## Pièges Courants (Common Pitfalls)

1. **Oubli de réinitialisation des gradients dans PyTorch :**
   * *Erreur :* Ne pas appeler `optimizer.zero_grad()`. Les gradients s'accumulent à chaque `.backward()`, détruisant la convergence du modèle.
   * *Correction :* Appeler `optimizer.zero_grad(set_to_none=True)`.

2. **Recompilation répétitive de graphe statique (`tf.function` tracing) :**
   * *Erreur :* Passer des valeurs Python natives variables (comme des entiers différents) en argument d'une fonction décorée de `@tf.function`. Cela force la recompilation constante du graphe d'exécution.
   * *Correction :* Passer des tenseurs `tf.Tensor` stables en arguments.

3. **Génération d'images bloquée sur des images noires (Black Images) :**
   * *Erreur :* Stable Diffusion retourne des images entièrement noires en raison du déclenchement du filtre de sécurité (NSFW Safety Checker) provoqué par des valeurs float16 instables.
   * *Correction :* Forcer la pipeline ou le VAE à s'exécuter en float32 pour l'étape de décodage avec `pipe.upcast_vae()`.

4. **Variables globales non constantes dans JAX :**
   * *Erreur :* Modifier des variables globales mutables Python à l'intérieur d'une fonction décorée avec `@jax.jit`. Le moteur XLA ne prendra pas en compte ces changements après la première compilation.
   * *Correction :* Passer tous les états modifiables en arguments explicites et les retourner dans le résultat de la fonction.

5. **Déconnexion de l'environnement d'apprentissage dans Stable-Baselines3 :**
   * *Erreur :* Omettre d'envelopper l'environnement avec un wrapper de type `Monitor` ou `DummyVecEnv` lors de l'utilisation de callbacks d'évaluation, causant des crashs d'indexation.
   * *Correction :* Toujours encapsuler l'environnement avec `Monitor(env)`.

---

## Liste de Vérification (Checklist)

- [ ] L'accélération matérielle appropriée (CUDA, MPS ou CPU) est détectée et appliquée dynamiquement.
- [ ] Le calcul d'évaluation ou d'inférence désactive explicitement les calculs de gradient (`torch.no_grad()` ou `training=False`).
- [ ] Toutes les métriques de perte accumulées pour l'affichage sont converties en scalaires standards avec `.item()` pour éviter les fuites de mémoire.
- [ ] Les fonctions compilées par JAX (`@jit`) ou TensorFlow (`@tf.function`) sont pures et exemptes d'effets de bord.
- [ ] L'environnement de simulation pour Stable-Baselines3 est enveloppé dans un `Monitor` et respecte strictement les signatures d'API de Gymnasium.
- [ ] Les optimisations mémoire (`enable_model_cpu_offload()`, `enable_attention_slicing()`) de Stable Diffusion sont activées sur les machines à ressources VRAM limitées (moins de 12 Go).
