---
name: tensorflow-lite-deep-dive
description: "Pipeline TFLite complet — conversion avancée, quantification INT8/FP16/FP32, GPU Delegates (OpenGL/OpenCL/Vulkan), NNAPI/XNNPACK, benchmarking, profilage mémoire, personnalisation d'opérateurs et déploiement cross-platform."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - tensorflow-lite
      - tflite
      - quantization
      - delegate
      - gpu
      - xnnpack
      - nnapi
      - benchmarking
      - edge-ai
      - model-optimization
    related_skills:
      - tinyml-fundamentals
      - onnx-edge-deployment
      - nvidia-jetson-deployment
      - model-optimization-edge
---

# TensorFlow Lite — Plongée Approfondie

## Vue d'ensemble

TensorFlow Lite est le moteur d'inférence léger de TensorFlow pour les dispositifs mobiles, embarqués et Edge. Cette skill couvre le pipeline complet de **conversion avancée**, les **delegates matériels**, l'**optimisation mémoire**, le **benchmarking systématique** et le **déploiement cross-platform** (Android, iOS, Linux ARM, MCU).

### Architecture TFLite

```
┌──────────────────────────────────────────────────────┐
│               Modèle source (Keras / SavedModel)      │
├──────────────────────────────────────────────────────┤
│             TFLite Converter (conversion avancée)      │
├──────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ XNNPACK     │  │ GPU Delegate│  │ NNAPI        │ │
│  │ (CPU NEON/  │  │ (OpenGL/    │  │ (Android HW  │ │
│  │  SSE/AVX)   │  │  Vulkan)    │  │  acceleration│ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │ CoreML      │  │ Hexagon     │  │ Edge TPU     │ │
│  │ (iOS)       │  │ (DSP)       │  │ (Coral)      │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
├──────────────────────────────────────────────────────┤
│           Interpreter (Runtime TFLite)                │
└──────────────────────────────────────────────────────┘
```

---

## 1. Conversion Avancée

### 1.1 Paramètres fins du Converter

```python
import tensorflow as tf

def converter_tflite_avance(model_path: str, quant_mode: str = "int8",
                            representative_data=None) -> bytes:
    """
    Conversion TFLite avec contrôle précis de chaque paramètre.
    
    Args:
        model_path: chemin du modèle Keras/SavedModel
        quant_mode: "float16", "int8", "dynamic_range", "float32"
        representative_data: générateur de calibration (obligatoire pour int8)
    
    Returns:
        modèle TFLite en bytes
    """
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    
    # ===== Optimisations =====
    if quant_mode in ("int8", "float16", "dynamic_range"):
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
    else:
        converter.optimizations = []
    
    # ===== Précision cible =====
    if quant_mode == "float16":
        converter.target_spec.supported_types = [tf.float16]
    elif quant_mode == "int8":
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS_INT8
        ]
        converter.inference_input_type = tf.int8
        converter.inference_output_type = tf.int8
        if representative_data:
            converter.representative_dataset = representative_data
    elif quant_mode == "dynamic_range":
        # Poids quantifiés, activations FP32
        pass  # DEFAULT suffit
    
    # ===== Contrôle des opérateurs =====
    # Permet des ops sélectionnées en FP32 même en mode INT8
    converter.target_spec.supported_ops += [
        tf.lite.OpsSet.TFLITE_BUILTINS
    ]
    # Sélectionner ops qui doivent rester FP32
    # ex: converter._experimental_allow_all_select_tf_ops = True
    
    # ===== Expérimental =====
    converter._experimental_disable_batchmatmul_unfold = False
    converter._experimental_lower_tensor_list_ops = True
    converter._experimental_default_to_single_batch_in_tensor_list_ops = True
    
    return converter.convert()
```

### 1.2 Sélecteur de précision par opérateur (mixed-precision)

```python
# TFLite permet de spécifier la précision par opérateur
# Utile : ops critiques en FP16, le reste en INT8

# Depuis TF 2.16+ :
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8,
    tf.lite.OpsSet.TFLITE_BUILTINS,  # fallback FP32
]
# Les ops non supportées en INT8 tombent en FP32
# = mélange INT8 + FP32 automatique
```

### 1.3 Quantification sélective avec signature

```python
# Quantification par sous-graphe (signature)
# Utile : encoder quantifié, decodeur FP16

converter.target_spec.supported_ops_by_signature = {
    "encoder": [tf.lite.OpsSet.TFLITE_BUILTINS_INT8],
    "decoder": [tf.lite.OpsSet.TFLITE_BUILTINS],
}
```

### 1.4 Sélection d'opérateurs (Allowlisting)

```python
# Réduire la taille du binaire en ne gardant que les ops nécessaires
from tensorflow.lite.python.op_hint import OpHint

# Permet d'exclure des ops rarement utilisées
ALLOWED_OPS = {
    "CONV_2D", "DEPTHWISE_CONV_2D", "FULLY_CONNECTED",
    "SOFTMAX", "AVERAGE_POOL_2D", "MAX_POOL_2D",
    "RESHAPE", "CONCATENATION", "ADD", "MUL",
}

# Utilisation dans le build embedded :
# TFLITE_ONLY_SELECTIVE_OPS dans le BUILD config
```

---

## 2. Delegates (Accélération Matérielle)

### 2.1 XNNPACK Delegate (CPU optimisé)

```python
# XNNPACK : optimisation CPU via NEON/SSE/AVX
# Activé par défaut dans TFLite ≥ 2.3 sur architectures supportées

import tflite_runtime.interpreter as tflite

# Activation explicite
from tflite_runtime.interpreter import Interpreter
from tflite_runtime.interpreter import load_delegate

# Vérifier si XNNPACK est disponible
try:
    delegate = load_delegate("libXNNPACK.so")
    interpreter = Interpreter(
        model_path="model.tflite",
        experimental_delegates=[delegate],
    )
    print("XNNPACK Delegate activé")
except:
    print("XNNPACK non disponible, fallback CPU standard")
    interpreter = Interpreter(model_path="model.tflite")
```

```bash
# Compilation XNNPACK depuis les sources
git clone https://github.com/google/XNNPACK.git
cd XNNPACK
mkdir build && cd build
cmake -DXNNPACK_BUILD_TESTS=OFF -DXNNPACK_BUILD_BENCHMARKS=OFF ..
make -j$(nproc)
sudo make install

# Lier avec TFLite
# CMakeLists.txt :
#   find_package(XNNPACK REQUIRED)
#   target_link_libraries(my_app XNNPACK::XNNPACK)
```

### 2.2 GPU Delegate (OpenGL / Vulkan / Metal)

```python
# GPU Delegate : utilise le GPU pour les ops tensorielles
# Supporte OpenGL ES 3.1+ (Android), Metal (iOS), Vulkan

import tflite_runtime.interpreter as tflite
from tflite_runtime.interpreter import load_delegate

# Android / Linux avec OpenGL
gpu_delegate = load_delegate("libgpu_delegate.so")
interpreter = tflite.Interpreter(
    model_path="model.tflite",
    experimental_delegates=[gpu_delegate],
)

# Options GPU avancées
from tensorflow.lite.python.interpreter import OpResolverType

# Préférences de précision
GPU_OPTIONS = {
    "precision_loss_allowed": 0,          # 0 = FP16, 1 = FP32
    "inference_priority1": 1,              # 1 = min latence, 2 = min mémoire
    "inference_preference": 1,             # 1 = sustained speed
    "cache_directory": "/tmp/gpu_cache",
    "model_token": "model_v1",
}
```

```python
# Vérifier si le GPU Delegate est compatible
def verifier_gpu_delegate():
    """Teste la disponibilité et la couverture GPU."""
    from tensorflow.lite.python.interpreter import Interpreter
    
    delegate = load_delegate("libgpu_delegate.so")
    interpreter = Interpreter(
        model_path="model.tflite",
        experimental_delegates=[delegate],
    )
    interpreter.allocate_tensors()
    
    # Tester une inférence
    import numpy as np
    input_details = interpreter.get_input_details()
    interpreter.set_tensor(input_details[0]["index"],
                           np.random.randn(*input_details[0]["shape"]).astype(
                               input_details[0]["dtype"]))
    interpreter.invoke()
    return True
```

### 2.3 NNAPI Delegate (Android Neural Networks API)

```python
# NNAPI : accélération matérielle Android (DSP, NPU, GPU)
# Disponible sur Android 8.1+ (API 27+)

from tflite_runtime.interpreter import Interpreter, load_delegate

nnapi_delegate = load_delegate("libnnapi_delegate.so")
interpreter = Interpreter(
    model_path="model.tflite",
    experimental_delegates=[nnapi_delegate],
)

# Forcer NNAPI pour TOUS les opérateurs
nnapi_delegate = load_delegate("libnnapi_delegate.so", {
    "disable_nnapi_cpu": "1",   # Ne pas utiliser CPU NNAPI
    "accelerator_name": "qti-dsp", # Forcer DSP Qualcomm
})
```

### 2.4 Hexagon Delegate (Qualcomm DSP)

```python
# Hexagon : accélération DSP Qualcomm
# Nécessite SDK Qualcomm Hexagon

# Activation
hexagon_delegate = load_delegate("libhexagon_delegate.so")
interpreter = Interpreter(
    model_path="model_quantized.tflite",
    experimental_delegates=[hexagon_delegate],
)
```

### 2.5 CoreML Delegate (iOS)

```python
# CoreML Delegate : Apple Neural Engine
# Uniquement sur iOS

# Activation depuis l'application iOS
let coreml_delegate = CoreMLDelegate()
var interpreter: Interpreter

if coreml_delegate != nil {
    interpreter = try Interpreter(
        modelPath: "model.tflite",
        delegates: [coreml_delegate!]
    )
} else {
    interpreter = try Interpreter(modelPath: "model.tflite")
}
```

### 2.6 Tableau Comparatif des Delegates

| Delegate | Plateforme | Accélération | Précision | Taille binaire |
|:---------|:----------|:------------|:---------:|:-------------:|
| **XNNPACK** | Linux/Android/Windows | CPU NEON/SSE/AVX | FP32/FP16 | ~500 KB |
| **GPU** (OpenGL) | Android/Linux | GPU (shaders) | FP16 | ~300 KB |
| **GPU** (Vulkan) | Android/Linux | GPU (compute) | FP16/FP32 | ~400 KB |
| **Metal** | iOS | GPU (Apple) | FP16 | ~200 KB |
| **NNAPI** | Android 8.1+ | DSP/NPU/GPU | INT8/FP16 | ~100 KB |
| **Hexagon** | Qualcomm | DSP | INT8 | ~2 MB |
| **CoreML** | iOS 12+ | Neural Engine | FP16 | ~300 KB |
| **Edge TPU** | Coral | TPU | INT8 | ~200 KB |

---

## 3. Benchmarking et Profilage

### 3.1 TFLite Benchmark Tool (officiel)

```bash
# Outil de benchmark officiel TFLite
# https://github.com/tensorflow/tensorflow/tree/master/tensorflow/lite/tools/benchmark

# Compilation
bazel build -c opt tensorflow/lite/tools/benchmark:benchmark_model

# Benchmark basique
./benchmark_model \
    --graph=model.tflite \
    --num_threads=4 \
    --num_runs=100 \
    --warmup_runs=10

# Benchmark avec delegate GPU
./benchmark_model \
    --graph=model.tflite \
    --use_gpu=true \
    --allow_fp16_precision_for_fp32=true

# Benchmark avec XNNPACK
./benchmark_model \
    --graph=model.tflite \
    --use_xnnpack=true \
    --num_threads=8

# Sortie détaillée
./benchmark_model --graph=model.tflite --profiling=true --profiling_output_csv_file=profile.csv
```

### 3.2 Benchmark Python

```python
# Benchmark programmatique complet
import time
import numpy as np
import tensorflow as tf

class TFLiteBenchmark:
    """Benchmark systématique d'un modèle TFLite."""
    
    def __init__(self, model_path: str, delegate: str = "cpu"):
        self.model_path = model_path
        self.delegate = delegate
        self.interpreter = self._creer_interpreteur()
        self.details_entree = self.interpreter.get_input_details()
        self.details_sortie = self.interpreter.get_output_details()
    
    def _creer_interpreteur(self):
        """Crée l'interpréteur avec le delegate spécifié."""
        if self.delegate == "cpu":
            return tf.lite.Interpreter(model_path=self.model_path)
        elif self.delegate == "xnnpack":
            from tflite_runtime.interpreter import load_delegate
            delegate = load_delegate("libXNNPACK.so")
            return tf.lite.Interpreter(
                model_path=self.model_path,
                experimental_delegates=[delegate],
            )
        elif self.delegate == "gpu":
            from tflite_runtime.interpreter import load_delegate
            delegate = load_delegate("libgpu_delegate.so")
            return tf.lite.Interpreter(
                model_path=self.model_path,
                experimental_delegates=[delegate],
            )
    
    def mesurer_latence(self, input_data: np.ndarray = None,
                        n_iterations: int = 100, warmup: int = 10) -> dict:
        """Mesure la latence d'inférence."""
        self.interpreter.allocate_tensors()
        
        # Entrée par défaut
        if input_data is None:
            shape = self.details_entree[0]["shape"]
            dtype = self.details_entree[0]["dtype"]
            input_data = np.random.randn(*shape).astype(dtype)
        
        # Warmup
        for _ in range(warmup):
            self.interpreter.set_tensor(
                self.details_entree[0]["index"], input_data)
            self.interpreter.invoke()
        
        # Mesure
        latences = []
        for _ in range(n_iterations):
            self.interpreter.set_tensor(
                self.details_entree[0]["index"], input_data)
            
            start = time.perf_counter()
            self.interpreter.invoke()
            elapsed = (time.perf_counter() - start) * 1000  # ms
            latences.append(elapsed)
        
        return {
            "delegate": self.delegate,
            "latence_moyenne_ms": float(np.mean(latences)),
            "latence_ecart_type_ms": float(np.std(latences)),
            "latence_p50_ms": float(np.percentile(latences, 50)),
            "latence_p90_ms": float(np.percentile(latences, 90)),
            "latence_p99_ms": float(np.percentile(latences, 99)),
            "fps": 1000 / float(np.mean(latences)),
            "n_iterations": n_iterations,
        }
    
    def profiler_memoire(self) -> dict:
        """Profile l'utilisation mémoire du modèle."""
        self.interpreter.allocate_tensors()
        
        details_tous = self.interpreter.get_tensor_details()
        memoire_totale = 0
        memoire_par_type = {}
        
        for det in details_tous:
            taille = np.prod(det["shape"]) * np.dtype(det["dtype"]).itemsize
            memoire_totale += taille
            type_name = str(det["dtype"])
            memoire_par_type[type_name] = memoire_par_type.get(type_name, 0) + taille
        
        return {
            "memoire_totale_bytes": int(memoire_totale),
            "memoire_totale_kb": memoire_totale / 1024,
            "memoire_par_type": {k: f"{v/1024:.1f} KB" for k, v in memoire_par_type.items()},
            "n_tensors": len(details_tous),
        }
    
    def analyser_ops(self) -> list:
        """Liste tous les opérateurs du modèle."""
        ops = []
        for op_details in self.interpreter._get_ops_details():
            ops.append({
                "index": op_details["index"],
                "nom": op_details["op_name"],
                "entrees": op_details["inputs"],
                "sorties": op_details["outputs"],
            })
        return ops

# Utilisation :
bench = TFLiteBenchmark("model_quant.tflite", delegate="cpu")
lat = bench.mesurer_latence(n_iterations=200)
print(f"Latence moyenne : {lat['latence_moyenne_ms']:.2f} ms")
print(f"FPS : {lat['fps']:.1f}")
```

### 3.3 Profilage mémoire détaillé

```python
def profilage_memoire_tflite(model_path: str) -> dict:
    """Analyse détaillée de la mémoire d'un modèle TFLite."""
    import struct
    
    with open(model_path, "rb") as f:
        model_data = f.read()
    
    info = {
        "taille_fichier_kb": len(model_data) / 1024,
    }
    
    # Analyser le FlatBuffer TFLite
    # Header (4 bytes = magic number 0x1C 0x00 0x00 0x00)
    magic = model_data[:4]
    assert magic == b'\x1c\x00\x00\x00', "Format TFLite invalide"
    
    # Version
    version = struct.unpack("<i", model_data[4:8])[0]
    info["version_modele"] = f"TFLite {version}"
    
    # Approximation : les poids sont dans les buffers
    # Dans un modèle quantifié INT8, les poids dominent
    interpreter = tf.lite.Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    
    details = interpreter.get_tensor_details()
    poids_total = 0
    activations_total = 0
    
    for det in details:
        taille = np.prod(det["shape"]) * np.dtype(det["dtype"]).itemsize
        if "weight" in det["name"].lower():
            poids_total += taille
        else:
            activations_total += taille
    
    info["poids_kb"] = poids_total / 1024
    info["activations_kb"] = activations_total / 1024
    info["ratio_poids_activation"] = f"{poids_total/activations_total:.1f}x"
    
    return info
```

---

## 4. Opérateurs Personnalisés (Custom Ops)

### 4.1 Création d'un opérateur personnalisé C++

```cpp
// custom_op.h
#ifndef CUSTOM_OP_H_
#define CUSTOM_OP_H_

#include "tensorflow/lite/core/c/common.h"
#include "tensorflow/lite/kernels/register.h"

namespace tflite {
namespace ops {
namespace custom {

// Pré-traitement audio : preemphasis filter
// y[n] = x[n] - alpha * x[n-1]
TfLiteRegistration* Register_PREEMPHASIS();

// Implémentation
TfLiteStatus PreemphasisPrepare(TfLiteContext* context, TfLiteNode* node) {
    // Vérifier les dimensions
    const TfLiteTensor* input = GetInput(context, node, 0);
    TfLiteTensor* output = GetOutput(context, node, 0);
    
    TfLiteIntArray* output_dims = TfLiteIntArrayCopy(input->dims);
    return context->ResizeTensor(context, output, output_dims);
}

TfLiteStatus PreemphasisEval(TfLiteContext* context, TfLiteNode* node) {
    const TfLiteTensor* input = GetInput(context, node, 0);
    const TfLiteTensor* alpha_tensor = GetInput(context, node, 1);
    TfLiteTensor* output = GetOutput(context, node, 0);
    
    float alpha = *GetTensorData<float>(alpha_tensor);
    const float* in_data = GetTensorData<float>(input);
    float* out_data = GetTensorData<float>(output);
    
    int size = GetTensorShape(input).FlatSize();
    
    // y[0] = x[0]
    out_data[0] = in_data[0];
    // y[n] = x[n] - alpha * x[n-1]
    for (int i = 1; i < size; i++) {
        out_data[i] = in_data[i] - alpha * in_data[i - 1];
    }
    
    return kTfLiteOk;
}

TfLiteRegistration* Register_PREEMPHASIS() {
    static TfLiteRegistration r = {
        .init = nullptr,
        .free = nullptr,
        .prepare = PreemphasisPrepare,
        .invoke = PreemphasisEval,
    };
    return &r;
}

}  // namespace custom
}  // namespace ops
}  // namespace tflite
```

### 4.2 Enregistrement du custom op dans le résolveur

```cpp
// Enregistrement de l'op personnalisé
MicroMutableOpResolver<10> resolver;
resolver.AddCustom("Preemphasis", 
                   tflite::ops::custom::Register_PREEMPHASIS());
```

### 4.3 Utilisation du custom op en Python

```python
# Créer un modèle TF qui utilise l'op personnalisé
import tensorflow as tf

@tf.function
def preemphasis(x, alpha=0.97):
    """Filtre pre-emphasis personnalisé."""
    # Sera converti en custom op TFLite
    y = tf.concat([[x[0]], x[1:] - alpha * x[:-1]], axis=0)
    return y

# Export avec signature
concrete_fn = preemphasis.get_concrete_function(
    x=tf.TensorSpec((None, 128), tf.float32)
)

converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_fn])
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,
    tf.lite.OpsSet.SELECT_TF_OPS,  # Permet les ops TF
]
tflite_model = converter.convert()
```

```python
# Ou depuis un modèle Keras avec un custom layer
class PreemphasisLayer(tf.keras.layers.Layer):
    def __init__(self, alpha=0.97, **kwargs):
        super().__init__(**kwargs)
        self.alpha = alpha
    
    def call(self, x):
        # Implémentation
        return tf.concat([[x[0]], x[1:] - self.alpha * x[:-1]], axis=0)
    
    def get_config(self):
        return {"alpha": self.alpha}
```

---

## 5. Compression et Taille de Modèle

### 5.1 Analyse détaillée du FlatBuffer

```python
def analyser_flatbuffer_tflite(model_path: str) -> dict:
    """Extrait la structure interne du FlatBuffer TFLite."""
    from flatbuffers import util
    from tflite import Model, SubGraph, OperatorCode
    
    with open(model_path, "rb") as f:
        buf = f.read()
    
    model = Model.Model.GetRootAsModel(buf, 0)
    
    info = {
        "version": model.Version(),
        "description": model.Description().decode() if model.Description() else "",
        "n_subgraphs": model.SubgraphsLength(),
        "n_operator_codes": model.OperatorCodesLength(),
        "n_buffers": model.BuffersLength(),
    }
    
    # Détails des opérateurs
    codes = []
    for i in range(model.OperatorCodesLength()):
        op_code = model.OperatorCodes(i)
        builtin = op_code.BuiltinCode()
        custom = op_code.CustomCode()
        codes.append({
            "index": i,
            "builtin": builtin,
            "custom": custom.decode() if custom else None,
        })
    info["operator_codes"] = codes
    
    # Taille des buffers
    buffer_sizes = []
    for i in range(model.BuffersLength()):
        buf = model.Buffers(i)
        data = buf.DataAsNumpy()
        if data is not None:
            buffer_sizes.append(len(data))
    info["buffer_sizes"] = {
        "total_bytes": sum(buffer_sizes),
        "max_buffer": max(buffer_sizes) if buffer_sizes else 0,
        "n_buffers_data": len(buffer_sizes),
    }
    
    return info
```

### 5.2 Réduction de taille

```python
# Techniques de réduction de la taille du fichier .tflite :

# 1. Suppression des métadonnées inutiles
converter._experimental_strip_unsupported_ops = True

# 2. Quantification des poids (le plus efficace)
# INT8 : jusqu'à 4× plus petit que FP32

# 3. Sparsité (pruning)
from tensorflow_model_optimization.sparsity import keras as sparsity

pruning_params = {
    "pruning_schedule": sparsity.PolynomialDecay(
        initial_sparsity=0.30,
        final_sparsity=0.80,
        begin_step=1000,
        end_step=5000,
    )
}
model_prune = sparsity.prune_low_magnitude(model, **pruning_params)

# 4. Clustering (partage de poids)
from tensorflow_model_optimization.clustering import keras as clustering

cluster_weights = clustering.cluster_weights(model, number_of_clusters=16)
model_clustered = cluster_weights()

# 5. Distillation (modèle student plus petit)
# → Voir skill model-optimization-edge
```

---

## 6. Déploiement Cross-Platform

### 6.1 Android AAR

```bash
# Build AAR personnalisé
python3 tensorflow/lite/tools/build_aar.py \
    --input_model=model.tflite \
    --target_archs=arm64-v8a,armeabi-v7a,x86_64 \
    --include_ops="CONV_2D,DEPTHWISE_CONV_2D,SOFTMAX"

# Inclure dans app/build.gradle :
# dependencies {
#     implementation fileTree(dir: 'libs', include: ['*.aar'])
# }
```

### 6.2 iOS CocoaPods / SPM

```ruby
# Podfile
pod 'TensorFlowLiteSwift', '~> 2.14.0'
# ou avec délégués
pod 'TensorFlowLiteSwift/Metal', '~> 2.14.0'
```

```swift
// Swift inference
import TensorFlowLite

class EdgeInference {
    private var interpreter: Interpreter
    
    init(modelPath: String) throws {
        interpreter = try Interpreter(modelPath: modelPath)
        try interpreter.allocateTensors()
    }
    
    func predict(input: [Float]) throws -> [Float] {
        let inputData = Data(bytes: input, count: input.count * MemoryLayout<Float>.stride)
        try interpreter.copy(inputData, toInputAt: 0)
        try interpreter.invoke()
        let outputData = try interpreter.output(at: 0)
        return outputData.toArray(type: Float.self)
    }
}
```

### 6.3 Linux ARM (Raspberry Pi, Jetson)

```bash
# Installation TFLite Runtime sur ARM64
pip3 install tflite-runtime

# Ou compilation depuis les sources
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
./tensorflow/lite/tools/make/download_dependencies.sh
./tensorflow/lite/tools/make/build_aarch64_lib.sh

# Compilation de l'application
g++ my_app.cpp -I tensorflow/lite/tools/make/downloads \
    -L tensorflow/lite/tools/make/gen/aarch64_armv8-a/lib \
    -ltensorflow-lite -ldl -lpthread -o my_app
```

---

## 7. Métriques et Surveillance

### 7.1 Métriques de déploiement TFLite

```python
def metriques_deploiement_tflite(model_path: str) -> dict:
    """Calcule les métriques clés pour le déploiement."""
    bench = TFLiteBenchmark(model_path)
    
    latence = bench.mesurer_latence(n_iterations=200)
    memoire = bench.profiler_memoire()
    
    return {
        "performance": latence,
        "memoire": memoire,
        "compatibilite": {
            "tflite_version": tf.__version__,
            "ops_count": len(bench.analyser_ops()),
            "quantized": "int8" in model_path or "quant" in model_path,
        }
    }
```

---

## Pièges Courants

1. **Conversion INT8 sans calibration** : dégrade la précision de 10-15%. Toujours fournir un `representative_dataset` représentatif des données réelles de production.

2. **Ops SELECT_TF_OPS vs TFLITE_BUILTINS** : SELECT_TF_OPS augmente la taille du binaire de ~2 MB. Utiliser uniquement pour les ops TF non disponibles en builtins.

3. **GPU Delegate silencieux** : certains ops ne sont pas supportés par le GPU Delegate (tombent silencieusement sur CPU → pas d'accélération). Vérifier avec `--use_gpu=true --profiling=true`.

4. **Threading implicite** : par défaut TFLite utilise 1 thread. Pour CPU multi-cœur, définir explicitement `num_threads` (optimal = nombre de cœurs P). Sur mobile, le thread count peut varier selon l'état thermique.

5. **XNNPACK FP16 sur ARM** : XNNPACK utilise FP16 par défaut sur ARM64 (2× throughput). Mais certains modèles peuvent perdre en précision. Forcer FP32 si nécessaire.

6. **TFLite Micro vs TFLite standard** : TFLite Micro a un sous-ensemble d'ops réduit. Toujours vérifier la compatibilité avant déploiement µC.

7. **Buffer d'entrée non aligné** : l'entrée des delegates GPU nécessite un alignement 16-bytes. Utiliser `np.ascontiguousarray()`.

---

## Références

- **TFLite Guide** : https://www.tensorflow.org/lite/guide
- **TFLite Converter** : https://www.tensorflow.org/lite/models/convert
- **XNNPACK** : https://github.com/google/XNNPACK
- **GPU Delegate** : https://www.tensorflow.org/lite/performance/gpu
- **NNAPI** : https://developer.android.com/ndk/guides/neuralnetworks
- **TFLite Benchmark** : https://www.tensorflow.org/lite/performance/measurement
- **Custom Ops** : https://www.tensorflow.org/lite/guide/ops_custom
