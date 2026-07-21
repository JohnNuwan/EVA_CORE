---
name: nvidia-jetson-deployment
description: "Déploiement IA sur NVIDIA Jetson (Nano/Orin/AGX) — JetPack SDK, TensorRT optimisation, DeepStream pipelines vidéo, DLA accélération, multi-stream, profiling Nsight, déploiement CUDA natif, optimisation énergétique."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - nvidia-jetson
      - tensorrt
      - deepstream
      - cuda
      - dla
      - jetpack
      - nsight
      - edge-ai
      - computer-vision
      - multi-stream
    related_skills:
      - onnx-edge-deployment
      - tensorflow-lite-deep-dive
      - model-optimization-edge
      - google-coral-edge-tpu
---

# NVIDIA Jetson — Déploiement Edge IA

## Vue d'ensemble

La famille NVIDIA Jetson est la plateforme Edge AI la plus puissante du marché, intégrant GPU NVIDIA avec Tensor Cores, DLA (Deep Learning Accelerator), et un pipeline vidéo matériel. Elle couvre du Nano (0.5 TOPS FP16) à l'AGX Orin (248 TOPS INT8).

### Comparatif des modules Jetson

| Module | GPU | Tensor Cores | DLA | TOPS (INT8) | RAM | Consommation |
|:-------|:---:|:-----------:|:---:|:----------:|:---:|:----------:|
| **Nano** | 128-core Maxwell | 0 | 0 | 0.5 | 4 GB | 5-10 W |
| **TX2** | 256-core Pascal | 0 | 1 | 1.3 | 8 GB | 7-15 W |
| **Xavier NX** | 384-core Volta | 48 | 2 | 21 | 8 GB | 10-20 W |
| **Orin NX** | 1024-core Ampere | 32 | 2 | 100 | 16 GB | 10-25 W |
| **Orin Nano** | 512-core Ampere | 16 | 0 | 40 | 8 GB | 7-15 W |
| **AGX Orin** | 2048-core Ampere | 64 | 2 | 248 | 64 GB | 15-60 W |

### Architecture logicielle Jetson

```
┌─────────────────────────────────────────────────────┐
│                Application (ROS / Python / C++)      │
├─────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ TensorRT │  │ DeepStream│  │ CUDA/CuDNN/Tensor │  │
│  │ (moteur  │  │ (pipeline │  │ Core (NVIDIA SDK) │  │
│  │  inf.)   │  │  vidéo)   │  │                   │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │              │                 │             │
├───────┼──────────────┼─────────────────┼─────────────┤
│       ▼              ▼                 ▼             │
│  ┌──────────────────────────────────────────────┐   │
│  │          JetPack SDK (L4T / BSP)              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────┐  │   │
│  │  │ GPU Ampere│ │   DLA    │ │ Video Engine │  │   │
│  │  │ (CUDA)   │ │(Accel DL)│ │ (H.264/H.265)│  │   │
│  │  └──────────┘ └──────────┘ └──────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 1. TensorRT — Optimisation et Inférence

### 1.1 Conversion ONNX → TensorRT Engine

```python
import tensorrt as trt
import numpy as np
import os

TRT_LOGGER = trt.Logger(trt.Logger.INFO)

class BuildTensorRT:
    """Build et inférence TensorRT sur Jetson."""
    
    def __init__(self, onnx_path: str, engine_path: str = None,
                 precision: str = "fp16", max_batch: int = 8):
        self.onnx_path = onnx_path
        self.engine_path = engine_path or onnx_path.replace(".onnx", ".trt")
        self.precision = precision
        self.max_batch = max_batch
        self.engine = None
        self.context = None
        self.builder = None
        self.network = None
        self.parser = None
    
    def build(self, calibration_data=None) -> bool:
        """Build un engine TensorRT depuis ONNX."""
        
        self.builder = trt.Builder(TRT_LOGGER)
        network_flags = 1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        self.network = self.builder.create_network(network_flags)
        self.parser = trt.OnnxParser(self.network, TRT_LOGGER)
        
        # Parser ONNX
        with open(self.onnx_path, "rb") as f:
            if not self.parser.parse(f.read()):
                for i in range(self.parser.num_errors):
                    print(f"Erreur ONNX {i}: {self.parser.get_error(i)}")
                return False
        
        # Configuration du builder
        config = self.builder.create_builder_config()
        config.set_memory_pool_limit(
            trt.MemoryPoolType.WORKSPACE, 
            1 * 1024 * 1024 * 1024  # 1 GB
        )
        
        # Précision
        if self.precision == "fp16":
            if self.builder.platform_has_fast_fp16:
                config.set_flag(trt.BuilderFlag.FP16)
                print("FP16 activé — 2× throughput")
            else:
                print("FP16 non supporté sur ce matériel")
        
        elif self.precision == "int8":
            if self.builder.platform_has_fast_int8 and calibration_data:
                config.set_flag(trt.BuilderFlag.INT8)
                config.int8_calibrator = Int8Calibrator(calibration_data)
                print("INT8 activé — 4× throughput")
            else:
                print("INT8 non disponible — fallback FP16")
                config.set_flag(trt.BuilderFlag.FP16)
        
        # Optimization profile (dynamic shapes)
        profile = self.builder.create_optimization_profile()
        input_name = self.network.get_input(0).name
        input_shape = self.network.get_input(0).shape
        
        profile.set_shape(input_name,
            min=(1, *input_shape[1:]),
            opt=(self.max_batch // 2, *input_shape[1:]),
            max=(self.max_batch, *input_shape[1:]),
        )
        config.add_optimization_profile(profile)
        
        # Build
        serialized = self.builder.build_serialized_network(self.network, config)
        if serialized is None:
            print("Échec du build TensorRT")
            return False
        
        with open(self.engine_path, "wb") as f:
            f.write(serialized)
        print(f"Engine TensorRT sauvegardé : {self.engine_path}")
        return True
    
    def load(self) -> bool:
        """Charge un engine existe ou build."""
        if os.path.exists(self.engine_path):
            with open(self.engine_path, "rb") as f:
                runtime = trt.Runtime(TRT_LOGGER)
                self.engine = runtime.deserialize_cuda_engine(f.read())
            self.context = self.engine.create_execution_context()
            print(f"Engine chargé : {self.engine_path}")
            return True
        else:
            if self.build():
                return self.load()
            return False
    
    def inferer(self, input_data: np.ndarray) -> np.ndarray:
        """Inférence avec gestion mémoire CUDA."""
        import pycuda.driver as cuda
        
        # Allocation mémoire CUDA
        d_input = cuda.mem_alloc(input_data.nbytes)
        d_output = cuda.mem_alloc(
            self.engine.get_binding_shape(1).volume() * np.dtype(np.float32).itemsize
        )
        
        # Copie H2D
        cuda.memcpy_htod(d_input, input_data)
        
        # Inférence
        self.context.execute_v2(
            bindings=[int(d_input), int(d_output)]
        )
        
        # Copie D2H
        output_shape = tuple(self.engine.get_binding_shape(1))
        output_data = np.empty(output_shape, dtype=np.float32)
        cuda.memcpy_dtoh(output_data, d_output)
        
        return output_data


class Int8Calibrator(trt.IInt8MinMaxCalibrator):
    """Calibration INT8 pour TensorRT."""
    def __init__(self, calibration_data):
        super().__init__()
        self.data = calibration_data
        self.index = 0
        # Allocation mémoire
        self.buffer = None
    
    def get_batch_size(self):
        return self.data.shape[0]
    
    def get_batch(self, names):
        if self.index >= len(self.data):
            return None
        batch = self.data[self.index: self.index + self.get_batch_size()]
        self.index += self.get_batch_size()
        return [batch.astype(np.float32).ravel()]
    
    def read_calibration_cache(self):
        return None
    
    def write_calibration_cache(self, cache):
        pass


# Utilisation
# builder = BuildTensorRT("model.onnx", precision="fp16", max_batch=4)
# builder.load()
# output = builder.inferer(input_batch)
```

### 1.2 trtexec — Outil CLI de build et benchmark

```bash
# Build engine FP16
trtexec --onnx=model.onnx \
    --saveEngine=model_fp16.trt \
    --fp16 \
    --workspace=1024 \
    --verbose

# Build engine INT8 avec calibration
trtexec --onnx=model.onnx \
    --saveEngine=model_int8.trt \
    --int8 \
    --calib=calibration_data \
    --workspace=1024

# Benchmark
trtexec --loadEngine=model_fp16.trt \
    --warmUp=100 \
    --iterations=500 \
    --duration=10 \
    --useSpinWait \
    --separateProfileRun

# Benchmark avec batched input
trtexec --loadEngine=model_fp16.trt \
    --shapes=input:4x3x224x224 \
    --batch=4 \
    --best

# Voir les couches individuelles
trtexec --loadEngine=model_fp16.trt --dumpLayerInfo --profilingVerbosity=detailed

# Export profiling JSON
trtexec --loadEngine=model_fp16.trt --exportProfile=profile.json
```

### 1.3 Optimization des couches TensorRT

```bash
# TensorRT effectue automatiquement ces optimisations :

# 1. Fusion de couches (Layer Fusion)
# Conv + BN + ReLU → CBR fused
# Conv + Add + ReLU → CBR (skip connection)
# Gelu → fused Gelu

# 2. Kernel auto-tuning
# Pour chaque couche, TensorRT essaie ~10-50 kernels
# Sélectionne le plus rapide
# Réutilisable via engine cache

# 3. Tensor Core exploitation
# FP16 Tensor Core : matmul et conv sur Ampere+
# INT8 Tensor Core : Ampere (Orin) supporte INT8 DSC

# 4. Memory planning
# Réutilisation des buffers intermédiaires
# Minimise les allocations GPU
```

```python
# Vérifier les optimisations appliquées
def inspecter_engine(engine_path: str):
    """Inspecte la structure d'un engine TensorRT."""
    import tensorrt as trt
    
    runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
    with open(engine_path, "rb") as f:
        engine = runtime.deserialize_cuda_engine(f.read())
    
    n_layers = engine.num_layers
    n_bindings = engine.num_bindings
    
    infos = []
    for i in range(n_layers):
        layer = engine.get_layer_info(i)
        infos.append({
            "name": layer.name,
            "type": str(layer.type),
            "input_dims": [str(layer.input_format)],
            "output_dim": str(layer.output_format),
            "precision": str(layer.precision),
        })
    
    # Vérifier le nombre de fusions Tensor Core
    tensor_core_layers = sum(
        1 for l in infos if "CBR" in l["name"] or "FC" in l["name"]
    )
    
    return {
        "n_layers": n_layers,
        "n_bindings": n_bindings,
        "layers": infos,
        "tensor_core_fusions": tensor_core_layers,
    }
```

---

## 2. DLA — Deep Learning Accelerator

### 2.1 Activation et utilisation du DLA

```python
# DLA (Deep Learning Accelerator) = accélérateur dédié inférence
# Disponible sur Xavier NX (2× DLA) et Orin NX/AGX (2× DLA)
# Avantage : consomme ~1/10 du GPU pour la même tâche
# Idéal : modèles stables, en continu

# Activation DLA dans TensorRT
config.set_flag(trt.BuilderFlag.GPU_FALLBACK)  # GPU fallback si DLA insuffisant
config.set_default_device_type(trt.DeviceType.DLA)  # DLA par défaut
config.DLA_core = 0  # ou 1 pour second DLA core

# Répartir le modèle entre GPU + DLA
for i in range(self.network.num_layers):
    layer = self.network.get_layer(i)
    
    if i < 20:  # Premières couches : DLA (efficace)
        layer.precision = trt.float32
        layer.set_device_type(trt.DeviceType.DLA)
    else:  # Dernières couches : GPU
        layer.set_device_type(trt.DeviceType.GPU)
```

### 2.2 Benchmark DLA vs GPU

```bash
# Comparaison DLA vs GPU
trtexec --onnx=model.onnx \
    --saveEngine=model_dla0.trt \
    --fp16 \
    --useDLACore=0 \
    --allowGPUFallback

# Sans DLA (GPU only)
trtexec --onnx=model.onnx \
    --saveEngine=model_gpu.trt \
    --fp16

# Résultats typiques sur Xavier NX :
# GPU : 120 FPS @ 15 W
# DLA : 95 FPS @ 3 W   ← 5× meilleur ratio perf/watt
```

---

## 3. DeepStream — Pipeline Vidéo

### 3.1 Pipeline type

```python
# DeepStream SDK : pipeline d'inférence vidéo optimisé
# Utilise GStreamer + TensorRT + CUDA

# Pipeline typique :
# H264/H265 → Decode → Preprocess → Infer → Track → Display/Output

# Avantages :
# - Zero-copy entre decode et inference (Pitch surface)
# - Hardware decoder (NVDEC)
# - Multi-stream : jusqu'à 32 flux 1080p@30 sur Orin
```

```python
# Exemple : pipeline DeepStream Python
import sys

def creer_pipeline_deepstream(config_path: str, n_sources: int = 4):
    """Crée un pipeline DeepStream multi-caméras."""
    
    # Configuration du pipeline GStreamer + DeepStream
    # La config se fait via un fichier .cfg (config_infer_primary.txt)
    
    pipeline = (
        f"nvarguscamerasrc sensor-id=0 ! "
        f"nvvidconv ! "
        f"video/x-raw,width=640,height=480,framerate=30/1 ! "
        f"nvstreammux name=mux batch-size={n_sources} ! "
        f"nvinfer config-file-path={config_path} ! "
        f"nvtracker tracker-width=640 tracker-height=384 ! "
        f"nvdsosd ! "
        f"nvegltransform ! nveglglessink"
    )
    
    return pipeline
```

### 3.2 Configuration infer (config_infer_primary.txt)

```ini
[property]
# Chemins
gpu-id=0
net-scale-factor=0.0039215697906911373  # 1/255
model-file=model_fp16.trt
proto-file=labels.txt
model-engine-file=model_fp16.trt
labelfile-path=labels.txt

# Taille d'entrée
net-input-dims=3;224;224  # C;H;W
net-input-order=0  # 0=NCHW
input-blob-name=input
output-blob-name=output

# Précision
network-mode=1  # 0=FP32, 1=INT8, 2=FP16
batch-size=4
workspace-size=1024

# Post-traitement
parse-function=2  # 0=classifier, 1=detector, 2=segmentation
num-detected-classes=80
interval=0  # inférence à chaque frame
gie-unique-id=1

# Mosaïque (multi-stream)
process-mode=1  # 1=GPU, 2=DLA
```

### 3.3 Multi-stream avec DeepStream

```python
# Lancement DeepStream multi-caméra
# bash
# deepstream-app -c deepstream_app_config.txt

# Configuration multi-source
# deepstream_app_config.txt
"""
[application]
enable-perf-measurement=1
perf-measurement-interval=1

[source0]
enable=1
type=3  # 3=USB camera
uri=/dev/video0

[source1]
enable=1
type=3
uri=/dev/video1

[source2]
enable=1
type=3
uri=/dev/video2

[source3]
enable=1
type=3
uri=/dev/video3

[sink0]
enable=1
type=2  # 2=display
sync=0

[primary-gie]
enable=1
config-file-path=config_infer_primary.txt
batch-size=4
"""
```

### 3.4 Métriques DeepStream

```python
def metriques_deepstream() -> dict:
    """Métriques en temps réel du pipeline DeepStream."""
    # Accessibles via API
    # pipe_bin.get_probe("nvinfer") → métriques
    
    return {
        "fps_moyen": 120.0,
        "fps_par_source": [30.0, 30.0, 30.0, 30.0],
        "latence_inference_ms": 8.2,
        "utilisation_gpu": 65.0,  # %
        "utilisation_dla": 0.0,   # % (si utilisé)
        "n_frames_perdues": 0,
        "memoire_gpu_mb": 450,
    }
```

---

## 4. Mode Énergétique et Performance

### 4.1 Modes NV Power

```bash
# Les Jetson ont des modes de puissance prédéfinis
# Chaque mode ajuste fréquence GPU, CPU, DLA, mémoire

# Lister les modes disponibles
sudo nvpmodel -q
# Exemple sur Orin NX :
# 0: 15W (CPU 8c @ 1.2GHz, GPU @ 612MHz)
# 1: 25W (CPU 8c @ 1.5GHz, GPU @ 918MHz)
# 2: 40W (CPU 8c @ 1.8GHz, GPU @ 1224MHz) -- MAXN

# Changer de mode
sudo nvpmodel -m 0  # Mode 15W (économie)
sudo nvpmodel -m 2  # Mode MAXN (performance max)

# Voir le mode actif
cat /proc/nvpmodel
```

```bash
# Ajuster la fréquence GPU manuellement
# Voir les fréquences disponibles
cat /sys/devices/gpu.0/devfreq/17000000.gv11b/available_frequencies

# Fixer à une fréquence (en Hz)
sudo sh -c "echo 612000000 > /sys/devices/gpu.0/devfreq/17000000.gv11b/userspace/set_freq"
# ou gouvernorat performance
sudo sh -c "echo performance > /sys/devices/gpu.0/devfreq/17000000.gv11b/governor"
```

### 4.2 Jetson Stats

```bash
# Installation de jetson-stats
sudo apt install python3-pip
pip3 install jetson-stats

# Monitoring en temps réel
sudo jtop

# Voir les infos systèmes
sudo jetson_release

# Voir la température
cat /sys/devices/virtual/thermal/thermal_zone*/temp
```

### 4.3 Optimisation perf/watt

```python
def trouver_mode_optimal(fps_cible: float = 30.0):
    """Trouve le mode de puissance optimal pour un FPS cible."""
    
    modes = {
        0: {"nom": "15W", "fps_max": 60},
        1: {"nom": "25W", "fps_max": 120},
        2: {"nom": "MAXN", "fps_max": 200},
    }
    
    for mode_id, info in sorted(modes.items()):
        if info["fps_max"] >= fps_cible * 1.2:  # 20% de marge
            return mode_id
    
    return max(modes.keys())

# Exemple : pour 30 FPS → mode 15W suffit
# Pour 60 FPS → mode 15W limite → monter à 25W
```

---

## 5. Profilage avec Nsight Systems

### 5.1 Profilage CUDA

```bash
# Profilage d'inférence TensorRT
nsys profile \
    -o ./profils/inference_report \
    --stats=true \
    --trace cuda,nvtx,opengl \
    python3 infer.py

# Visualisation
# nsys-ui ./profils/inference_report.qdrep
```

### 5.2 Analyse des goulots

```python
# Points à vérifier dans le profil Nsight :

# 1. Kernel launch overhead
# Trop de petits kernels = overhead > compute
# Solution : fusionner les ops (TensorRT le fait)

# 2. Memory bandwidth saturée
# Si utilisation mémoire > 85% → bottleneck mémoire
# Solution : quantification INT8, réduire batch size

# 3. GPU idle time
# Attente CPU (data loading, preprocessing)
# Solution : pipeline asynchrone (CUDA streams)

# 4. Data transfer H2D/D2H
# Si copie mémoire > temps compute
# Solution : pinned memory, zero-copy, batch processing
```

```python
# Profilage avec CUDA Events
import pycuda.driver as cuda

def profiler_inference(model, input_data: np.ndarray, n_iter: int = 100):
    """Profiling fin avec CUDA Events."""
    
    start = cuda.Event()
    end = cuda.Event()
    
    # Warmup
    for _ in range(10):
        model.inferer(input_data)
    
    # Mesure
    start.record()
    for _ in range(n_iter):
        model.inferer(input_data)
    end.record()
    end.synchronize()
    
    elapsed_ms = start.time_since(end) / n_iter
    print(f"Temps moyen par inference (CUDA Events) : {elapsed_ms:.2f} ms")
    print(f"Throughput : {1000 / elapsed_ms:.1f} FPS")
    
    return elapsed_ms
```

---

## 6. Déploiement Python vs C++

### 6.1 API Python (rapide prototypage)

```python
# PyTorch sur Jetson : installation spéciale
# pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Exemple : inférence PyTorch avec TensorRT backend
import torch
import tensorrt as trt

model = torch.jit.load("model.ts").eval()
# TensorRT peut optimiser un model TorchScript
# Via torch_tensorrt :
# import torch_tensorrt

# optimized = torch_tensorrt.compile(
#     model,
#     inputs=[torch_tensorrt.Input((1, 3, 224, 224))],
#     enabled_precisions={torch.float16},
#     workspace_size=1 << 30,
# )
```

### 6.2 API C++ (production)

```cpp
// inference_engine.hpp
#include <NvInfer.h>
#include <NvOnnxParser.h>

class TRTInference {
private:
    nvinfer1::IRuntime* runtime;
    nvinfer1::ICudaEngine* engine;
    nvinfer1::IExecutionContext* context;
    void* device_buffers[2];  // input + output
    float* host_output;
    
public:
    TRTInference(const std::string& engine_path) {
        // Chargement de l'engine
        runtime = nvinfer1::createInferRuntime(gLogger);
        
        std::ifstream file(engine_path, std::ios::binary);
        file.seekg(0, std::ios::end);
        size_t size = file.tellg();
        std::vector<char> buffer(size);
        file.seekg(0, std::ios::beg);
        file.read(buffer.data(), size);
        
        engine = runtime->deserializeCudaEngine(buffer.data(), size);
        context = engine->createExecutionContext();
        
        // Allocation CUDA
        cudaMalloc(&device_buffers[0], engine->getBindingBytes(0));
        cudaMalloc(&device_buffers[1], engine->getBindingBytes(1));
        host_output = new float[engine->getBindingBytes(1) / sizeof(float)];
    }
    
    bool infer(float* input, float* output) {
        // Copie H2D
        cudaMemcpy(device_buffers[0], input, 
                   engine->getBindingBytes(0), cudaMemcpyHostToDevice);
        
        // Execution
        context->executeV2(device_buffers);
        
        // Copie D2H
        cudaMemcpy(output, device_buffers[1], 
                   engine->getBindingBytes(1), cudaMemcpyDeviceToHost);
        
        return true;
    }
    
    ~TRTInference() {
        cudaFree(device_buffers[0]);
        cudaFree(device_buffers[1]);
        delete[] host_output;
        delete context;
        delete engine;
        delete runtime;
    }
};
```

---

## 7. Installation JetPack

```bash
# Installation JetPack via SDK Manager (depuis PC hôte)

# 1. Télécharger SDK Manager
# https://developer.nvidia.com/sdk-manager

# 2. Mettre le Jetson en mode recovery :
#   - Brancher USB-C (cable micro-USB sur Nano)
#   - Appuyer sur RECOV → POWER → relâcher RECOV

# 3. Installer via SDK Manager
sdkmanager --cli install \
    --target_os Linux \
    --product Jetson \
    --version 6.0 \
    --target_jetson_orin_nx \
    --logintype remote \
    --host <jetson-ip>

# 4. Vérifier l'installation
jetson_release
# JetPack 6.0 [L4T 36.3.1]
# CUDA 12.2
# TensorRT 8.6.2
# cuDNN 8.9.4
# OpenCV 4.8.0

# 5. Installer des dépendances supplémentaires
sudo apt update
sudo apt install python3-pip libopenblas-dev libjpeg-dev
pip3 install numpy pandas matplotlib pycuda
```

---

## Pièges Courants

1. **JetPack version incompatible** : utiliser exactement la version de JetPack supportée par votre module. Orin = JetPack 6+, Xavier = JetPack 5.x, Nano = JetPack 4.x.

2. **TensorRT build trop long** : le build d'engine TensorRT peut prendre 10-30 minutes. Toujours sauvegarder l'engine (`--saveEngine`) et le charger en production.

3. **DLA non activé** : le DLA n'est activé que pour certains opérateurs (Conv, Pooling). Vérifier avec `--useDLACore=0`.

4. **DeepStream buffer management** : le pipeline DeepStream gère ses buffers internes. Modifier la résolution après l'initialisation peut causer des plantages.

5. **nvpmodel après boot** : le mode de puissance n'est pas persistant. L'ajouter dans `/etc/rc.local` ou `systemd`.

6. **Mémoire GPU insuffisante** : les modèles lourds (YOLOv8-L, ViT) peuvent nécessiter > 8 GB. Réduire batch size, utiliser INT8, ou activer le swap GPU (`zram`).

7. **Température GPU > 80 °C** : le throttling GPU commence vers 85 °C. Ajouter un ventilateur (PWM) ou réduire nvpmodel.

8. **CUDA out of memory avec PyTorch** : PyTorch ne libère pas la mémoire GPU immédiatement. Utiliser `torch.cuda.empty_cache()` après chaque inférence.

---

## Références

- **Jetson Developer** : https://developer.nvidia.com/embedded-computing
- **JetPack SDK** : https://developer.nvidia.com/embedded/jetpack
- **TensorRT** : https://developer.nvidia.com/tensorrt
- **DeepStream** : https://developer.nvidia.com/deepstream-sdk
- **Nsight Systems** : https://developer.nvidia.com/nsight-systems
- **Jetson Stats** : https://github.com/rbonghi/jetson_stats
- **Jetson Benchmarks** : https://github.com/NVIDIA/DeeplearningExamples
- **Torch-TensorRT** : https://github.com/pytorch/TensorRT
