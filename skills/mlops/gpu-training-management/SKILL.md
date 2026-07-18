---
name: gpu-training-management
description: Gestion multi-GPU pour l'entraînement ML/RL — libération de GPU, allocation, monitoring, et résolution des conflits avec les services (vLLM, Label Studio, etc.)
version: 1.0.0
author: Eva
---

# Gestion Multi-GPU pour l'Entraînement ML

Guide pour gérer efficacement plusieurs GPUs (RTX 3090 ×2) entre les services permanents (vLLM, ComfyUI, Label Studio) et l'entraînement ML/RL.

## Architecture GPU typique

| GPU | Usage permanent | Usage entraînement |
|-----|----------------|-------------------|
| GPU 0 | Label Studio (birefnet) | Entraînement principal |
| GPU 1 | vLLM (small) | Entraînement secondaire / validation |

## Vérification de l'état GPU

```bash
# État actuel
nvidia-smi

# Détail par processus
nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_memory --format=csv

# Monitoring en temps réel
watch -n 1 nvidia-smi
```

## Libération d'un GPU pour l'entraînement

### Méthode 1 : Arrêt propre du service (recommandée)

```bash
# Identifier le processus
nvidia-smi | grep python

# Arrêter le service Docker
docker stop vllm-small  # ou vllm-big, label-studio, etc.

# Vérifier la libération
nvidia-smi  # GPU doit montrer ~10-20 MiB (Xorg seulement)
```

### Méthode 2 : Kill direct (si le service ne répond pas)

```bash
# Trouver le PID
nvidia-smi --query-compute-apps=pid --format=csv,noheader

# Kill
kill -9 <PID>

# Vérifier
nvidia-smi
```

### Méthode 3 : Redémarrage du service après entraînement

```bash
# Redémarrer le service
docker start vllm-small

# Vérifier qu'il reprend le GPU
nvidia-smi
```

## Allocation GPU pour l'entraînement

### PyTorch

```python
import torch

# Vérifier les GPUs disponibles
print(f"GPUs disponibles: {torch.cuda.device_count()}")
for i in range(torch.cuda.device_count()):
    print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
    print(f"    Mémoire: {torch.cuda.get_device_properties(i).total_memory / 1e9:.1f} GB")

# Forcer l'utilisation d'un GPU spécifique
device = torch.device("cuda:1")  # GPU 1
# ou
torch.cuda.set_device(1)

# Dans un script, via variable d'environnement
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "1"  # N'utiliser que GPU 1
```

### EVO-ARENA / ES

```python
# Dans train_evo.py ou es_agent.py
devices = ('cuda:0', 'cuda:1') if torch.cuda.device_count() >= 2 else \
          ('cuda:0',) if torch.cuda.device_count() == 1 else \
          ('cpu', 'cpu')

# Répartition de la population
# pop[i] → devices[i % len(devices)]
```

## Conflits courants et solutions

### 1. GPU "occupé" mais 0% utilisation

**Symptôme** : `nvidia-smi` montre un processus avec 2-5 GB alloués mais 0% utilisation.

**Cause** : Le processus a réservé de la mémoire mais ne calcule pas (idle).

**Solution** : Le GPU est techniquement disponible. On peut soit :
- Le partager (si la mémoire totale suffit)
- Tuer le processus pour libérer complètement

```bash
# Vérifier la mémoire réellement utilisée
nvidia-smi --query-compute-apps=pid,used_memory --format=csv

# Si besoin de tuer
kill -9 <PID>
```

### 2. OOM (Out of Memory) malgré GPU libre

**Symptôme** : `CUDA out of memory` alors que `nvidia-smi` montre de la mémoire libre.

**Cause** : Fragmentation mémoire ou autre processus sur le même GPU.

**Solution** :
```python
import torch

# Vider le cache
torch.cuda.empty_cache()

# Forcer la libération
import gc
gc.collect()
torch.cuda.empty_cache()

# Vérifier la mémoire par GPU
for i in range(torch.cuda.device_count()):
    print(f"GPU {i}: {torch.cuda.memory_allocated(i)/1e9:.1f} GB alloués, "
          f"{torch.cuda.memory_reserved(i)/1e9:.1f} GB réservés")
```

### 3. Processus zombie sur GPU

**Symptôme** : Le processus est mort mais la mémoire GPU n'est pas libérée.

**Solution** :
```bash
# Trouver les processus GPU
nvidia-smi --query-compute-apps=pid --format=csv,noheader

# Tuer tous les processus GPU
sudo kill -9 $(nvidia-smi --query-compute-apps=pid --format=csv,noheader)

# Ou plus proprement
sudo fuser -v /dev/nvidia*
```

## Scripts utiles

### Script de libération GPU

```bash
#!/bin/bash
# free_gpu.sh — Libère un GPU spécifique

GPU_ID=${1:-1}  # Par défaut GPU 1

echo "Libération GPU $GPU_ID..."

# Trouver les processus sur ce GPU
PIDS=$(nvidia-smi --query-compute-apps=pid,gpu_uuid --format=csv,noheader | \
       grep "$(nvidia-smi --query-gpu=uuid --format=csv,noheader -i $GPU_ID)" | \
       cut -d',' -f1)

if [ -z "$PIDS" ]; then
    echo "Aucun processus trouvé sur GPU $GPU_ID"
else
    echo "Processus trouvés: $PIDS"
    for PID in $PIDS; do
        echo "Arrêt de $PID..."
        kill -9 $PID 2>/dev/null || true
    done
fi

sleep 2
echo "État GPU $GPU_ID:"
nvidia-smi -i $GPU_ID
```

### Script de monitoring GPU

```bash
#!/bin/bash
# gpu_monitor.sh — Monitoring continu des GPUs

while true; do
    clear
    echo "=== $(date) ==="
    nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader
    echo ""
    echo "Processus:"
    nvidia-smi --query-compute-apps=pid,process_name,gpu_uuid,used_memory --format=csv,noheader
    sleep 5
done
```

## Bonnes pratiques

### Avant l'entraînement

1. **Vérifier les GPUs disponibles** :
   ```bash
   python3 -c "import torch; print(torch.cuda.device_count())"
   ```

2. **Libérer les GPUs nécessaires** :
   ```bash
   # Arrêter les services non essentiels
   docker stop vllm-small label-studio
   ```

3. **Vérifier la mémoire** :
   ```bash
   nvidia-smi
   ```

### Pendant l'entraînement

1. **Monitoring léger** :
   ```bash
   # Dans un autre terminal
   watch -n 5 'nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader'
   ```

2. **Alertes OOM** :
   ```python
   # Dans le code d'entraînement
   if torch.cuda.memory_allocated() > 0.9 * torch.cuda.get_device_properties(0).total_memory:
       print("⚠️ Mémoire GPU > 90%")
       torch.cuda.empty_cache()
   ```

### Après l'entraînement

1. **Nettoyer** :
   ```python
   torch.cuda.empty_cache()
   ```

2. **Redémarrer les services** :
   ```bash
   docker start vllm-small
   ```

## Configuration recommandée The Hive

| Service | GPU par défaut | Mémoire | Priorité |
|---------|---------------|---------|----------|
| Entraînement EVO-ARENA | GPU 0 + GPU 1 | 48 GB | Haute |
| vLLM (inférence) | GPU 1 | 5-10 GB | Moyenne |
| Label Studio | GPU 0 | 2-3 GB | Basse |
| ComfyUI | GPU 1 | 4-8 GB | Basse |

**Stratégie** : Arrêter vLLM et Label Studio pendant l'entraînement, les redémarrer après.

## Références

- `references/gpu-conflict-resolution.md` — Résolution des conflits GPU spécifiques
- `references/pytorch-multi-gpu.md` — Patterns PyTorch DataParallel/DistributedDataParallel
