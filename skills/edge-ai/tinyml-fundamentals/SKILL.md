---
name: tinyml-fundamentals
description: "Fondations TinyML — concevoir, entraîner et déployer des modèles ML sur microcontrôleurs (ARM Cortex-M, ESP32, RISC-V) avec TFLite Micro, contraintes mémoire, budget énergétique et optimisation ultra-low-power."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - tinyml
      - tflite-micro
      - microcontroller
      - ultra-low-power
      - cortex-m
      - risc-v
      - embedded-ml
      - tensorflow
      - quantization
      - edge-ai
    related_skills:
      - esp32-s3-deep-learning
      - tinyml-mcu-inference
      - tensorflow-lite-deep-dive
      - model-optimization-edge
---

# TinyML — Fondamentaux

## Vue d'ensemble

Le **TinyML** est l'ensemble des techniques permettant d'exécuter des modèles d'apprentissage automatique sur des microcontrôleurs (µC) avec mémoire de 2 KB à 512 KB et une consommation de l'ordre du milliwatt. Contrairement aux dispositifs Edge Linux (Raspberry Pi, Jetson), un µC **n'a pas d'OS généraliste** — il tourne du bare-metal ou FreeRTOS/Zephyr, avec un runtime d'inférence minimaliste.

### Contraintes typiques d'un µC TinyML

| Paramètre | Plage | Exemple (Cortex-M4) |
|:---------|:-----|:-------------------|
| RAM      | 2 – 512 KB | 128 KB |
| Flash    | 32 – 2048 KB | 512 KB |
| Fréquence CPU | 16 – 400 MHz | 120 MHz |
| Consommation | 1 – 100 mW | 15 mW (inference) |
| Taille modèle | 10 – 500 KB | 50 KB (quantifié) |

### Stack TinyML type

```
┌──────────────────────────────────────────────┐
│         Application (détection, KWS, IMU)     │
├──────────────────────────────────────────────┤
│   TFLite Micro Interpreter (~16 KB Flash)     │
├──────────────────────────────────────────────┤
│   Optimized kernels (CMSIS-NN / Xtensa / ...) │
├──────────────────────────────────────────────┤
│   RTOS / Bare-metal scheduler                 │
├──────────────────────────────────────────────┤
│   µC HAL (STM32Cube / ESP-IDF / Arduino Core) │
└──────────────────────────────────────────────┘
```

---

## 1. Conception de modèle pour TinyML

### 1.1 Budget mémoire : le calcul critique

Un modèle TinyML doit tenir dans la RAM disponible **avec les données d'entrée, les activations intermédiaires et la sortie**.

```python
def estimer_memoire_modele(n_parametres: int, n_couches: int, 
                            taille_entree: tuple, precision: int = 1) -> dict:
    """
    Estime la mémoire nécessaire pour un modèle TinyML.
    
    Args:
        n_parametres: nombre de paramètres
        n_couches: nombre de couches
        taille_entree: format d'entrée (H, W, C) ou (features,)
        precision: bytes par paramètre (1 = INT8, 2 = FP16)
    
    Returns:
        dict: ventilation mémoire
    """
    # Poids
    poids = n_parametres * precision  # bytes
    
    # Activations : buffer de la plus grande couche
    # Approximation : entrée * 4 (pour conv depthwise)
    h, w, c = taille_entree
    activations_max = h * w * c * 4 * precision
    
    # Tensors intermédiaires (scratch)
    scratch = max(2048, activations_max // 4)
    
    # Runtime TFLite Micro (~16 KB)
    runtime = 16384
    
    # Stack + heap overhead
    system = 4096
    
    total = poids + activations_max + scratch + runtime + system
    
    return {
        "poids_kb": poids / 1024,
        "activations_kb": activations_max / 1024,
        "scratch_kb": scratch / 1024,
        "runtime_kb": runtime / 1024,
        "system_kb": system / 1024,
        "total_kb": total / 1024,
    }


# Exemple : modèle KWS (KeyWord Spotting) 50K params, entrée MFCC 10×10×1
mem = estimer_memoire_modele(50000, 5, (10, 10, 1))
print(f"Total RAM estimée : {mem['total_kb']:.1f} KB")
# Résultat : ~93 KB → tient dans un STM32F4 (128 KB RAM)
```

### 1.2 Architectures recommandées pour TinyML

```python
# 1. DS-CNN (Depthwise Separable Convolution)
# Architecture reine du TinyML : sépare conv spatiale et conv 1x1
# → réduit les paramètres par ~8× par rapport à une conv standard

# 2. Sequential + global average pooling
# Évite les Fully Connected géantes (gouffre à paramètres)
# GAP réduit à 1×1 avant la couche de sortie

# 3. Tiny ConvNet
# Conv 3x3 → DepthwiseConv → PointwiseConv → GAP → FC

# 4. MobileNetV1 micro
# Facteur de largeur (alpha) = 0.25 → 0.5 pour réduire les filtres
```

```python
# Modèle TinyML exemple : détecteur de mots-clés (10 classes)
import tensorflow as tf

def creer_dscnn_micro(filtres: int = 8, n_classes: int = 10):
    """DS-CNN ultra-léger pour KWS."""
    model = tf.keras.Sequential([
        # Entrée : MFCC (10×10×1)
        tf.keras.layers.Input(shape=(10, 10, 1)),
        
        # Première conv standard (peu de params)
        tf.keras.layers.Conv2D(filtres, (3, 3), padding='same', strides=2),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        
        # Depthwise separable blocks
        tf.keras.layers.DepthwiseConv2D((3, 3), padding='same', strides=1),
        tf.keras.layers.Conv2D(filtres * 2, (1, 1), padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        
        tf.keras.layers.DepthwiseConv2D((3, 3), padding='same', strides=2),
        tf.keras.layers.Conv2D(filtres * 4, (1, 1), padding='same'),
        tf.keras.layers.BatchNormalization(),
        tf.keras.layers.ReLU(),
        
        # Global Average Pooling (évite les grosses FC)
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dropout(0.3),
        
        # Classification
        tf.keras.layers.Dense(n_classes, activation='softmax'),
    ])
    return model

model = creer_dscnn_micro()
model.summary()
print(f"Paramètres : {model.count_params():,}")
# ~15K-30K params → tient dans 15-30 KB en INT8
```

### 1.3 Règles d'or pour la conception TinyML

1. **Préférer DepthwiseConv2D** à Conv2D (7-8× moins de paramètres)
2. **Éviter les couches Dense > 64 neurones** — utiliser GAP
3. **Éviter les convolutions avec stride=1** sur grandes entrées — downsample tôt
4. **BatchNorm avant ReLU** (fusion possible en inférence)
5. **Compter les activations, pas juste les poids** — les activations intermédiaires consomment la RAM
6. **Préférer des modèles profonds et fins** plutôt que larges et peu profonds

---

## 2. Conversion pour TFLite Micro

### 2.1 Pipeline de conversion

```python
# Étape 1 : entraînement (TensorFlow Keras)
model = creer_dscnn_micro()
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(x_train, y_train, epochs=50, batch_size=32,
          validation_data=(x_val, y_val))

# Étape 2 : conversion TFLite avec quantification INT8
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Quantification INT8 avec calibration (obligatoire pour TFLite Micro)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
converter.representative_dataset = lambda: [
    [tf.cast(x_train[i:i+1], tf.float32)] 
    for i in range(min(100, len(x_train)))
]

tflite_model = converter.convert()

# Étape 3 : vérification de la compatibilité TFLite Micro
# Les opérateurs doivent être supportés par TFLite Micro
# Voir : https://github.com/tensorflow/tflite-micro/blob/main/tensorflow/lite/micro/all_ops_resolver.cc

import tensorflow.lite as tflite
interpreter = tflite.Interpreter(model_content=tflite_model)
interpreter.allocate_tensors()
print(f"Taille du modèle : {len(tflite_model) / 1024:.1f} KB")

# Vérifier que tous les opérateurs sont supportés par TFLite Micro
ops = [op.code for op in interpreter.get_tensor_details()]
print(f"Opérateurs : {ops}")
```

### 2.2 Opérateurs supportés par TFLite Micro

| Opérateur | Support | Notes |
|:---------|:-------:|:------|
| Conv2D | ✅ | Depthwise OK |
| FullyConnected | ✅ | |
| Softmax | ✅ | |
| ReLU / ReLU6 | ✅ | |
| DepthwiseConv2D | ✅ | |
| AveragePool2D / MaxPool2D | ✅ | |
| Reshape | ✅ | |
| Concatenation | ✅ | |
| Add / Sub / Mul | ✅ | |
| BatchNorm (fused) | ✅ | Fusionné dans Conv |
| LSTM | ⚠️ | UnidirectionalLSTM seulement |
| TransposeConv | ⚠️ | Limité |
| Neg / Abs / Rsqrt | ✅ | Opérations arithmétiques |

> **Règle :** si vous utilisez des ops TensorFlow non listées, vérifiez leur présence dans `all_ops_resolver.cc`.

### 2.3 Génération du tableau C (modèle embarqué)

```bash
# Convertir le modèle TFLite en tableau C pour inclusion directe
xxd -i model_kws.tflite > model_kws_data.cc

# Vérifier la taille
wc -c model_kws.tflite
```

Ou en Python :

```python
# Génération du tableau C avec alignement
def tflite_to_c_array(tflite_path: str, output_path: str, var_name: str = "g_model"):
    """Convertit un modèle TFLite en tableau C aligné sur 32 bytes."""
    with open(tflite_path, 'rb') as f:
        data = f.read()
    
    with open(output_path, 'w') as f:
        f.write(f'#include <cstdint>\n\n')
        f.write(f'#ifdef __has_attribute\n')
        f.write(f'#if __has_attribute(aligned)\n')
        f.write(f'__attribute__((aligned(32)))\n')
        f.write(f'#endif\n')
        f.write(f'#endif\n')
        f.write(f'const unsigned char {var_name}[] = {{\n')
        
        for i in range(0, len(data), 12):
            hex_bytes = ', '.join(f'0x{b:02x}' for b in data[i:i+12])
            f.write(f'  {hex_bytes},\n')
        
        f.write(f'};\n')
        f.write(f'const unsigned int {var_name}_len = {len(data)};\n')
    
    print(f"Tableau C généré : {output_path} ({len(data)} bytes)")

tflite_to_c_array("model_kws.tflite", "model_kws_data.cc")
```

---

## 3. Inférence TFLite Micro sur µC

### 3.1 Architecture du runtime TFLite Micro

```
┌──────────────────────────────────────────────────────────────────┐
│                       Application                                 │
│   MicroInterpreter::Invoke() → TensorAreana → OpResolver          │
├──────────────────────────────────────────────────────────────────┤
│  Tensor Arena (pré-allouée statiquement, ~10-100 KB)              │
│  ┌──────────────┬──────────────────┬────────────────────────┐     │
│  │ Tensors      │ Scratch buffer   │ Graph metadata         │     │
│  │ d'entrée/sortie│ (intermediate)  │ (tensors, ops, etc.) │     │
│  └──────────────┴──────────────────┴────────────────────────┘     │
├──────────────────────────────────────────────────────────────────┤
│  MicroOpResolver → kernels optimisés (CMSIS-NN / Xtensa)         │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Code µC complet (Arduino / PlatformIO)

```cpp
// model_kws_inference.cpp
#include <TensorFlowLite.h>
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "model_kws_data.cc"  // modèle converti en tableau C

// Constantes du modèle
constexpr int kTensorArenaSize = 50 * 1024;  // 50 KB pour le TensorArena
alignas(16) uint8_t tensor_arena[kTensorArenaSize];

// Résolveur d'opérateurs (n'inscrire que ceux utilisés)
tflite::MicroMutableOpResolver<10> resolver;

// Interpréteur
tflite::MicroInterpreter interpreter(
    tflite::GetModel(g_model),       // le modèle en tableau C
    resolver,
    tensor_arena,
    kTensorArenaSize
);

void setup() {
    Serial.begin(115200);
    
    // Enregistrement des opérateurs nécessaires
    resolver.AddConv2D();
    resolver.AddDepthwiseConv2D();
    resolver.AddFullyConnected();
    resolver.AddSoftmax();
    resolver.AddReshape();
    resolver.AddAveragePool2D();
    resolver.AddRelu();
    resolver.AddConcatenation();
    
    // Allocation des tensors
    TfLiteStatus allocate_status = interpreter.AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        Serial.println("ERREUR : allocation des tensors échouée");
        while (1);
    }
    
    Serial.print("TensorArena utilisée : ");
    Serial.print(interpreter.arena_used_bytes());
    Serial.println(" bytes");
    
    // Pointeurs vers les tensors d'entrée/sortie
    TfLiteTensor* input = interpreter.input(0);
    TfLiteTensor* output = interpreter.output(0);
    
    Serial.print("Entrée : ");
    Serial.print(input->dims->data[1]);
    Serial.print("x");
    Serial.print(input->dims->data[2]);
    Serial.print("x");
    Serial.println(input->dims->data[3]);
}

void loop() {
    // 1. Remplir le tensor d'entrée avec les données du capteur
    // (ex: MFCC d'un microphone, accéléromètre, etc.)
    TfLiteTensor* input = interpreter.input(0);
    for (int i = 0; i < input->bytes; i++) {
        input->data.int8[i] = sensor_data[i];  // données INT8
    }
    
    // 2. Exécuter l'inférence
    uint32_t start = micros();
    TfLiteStatus invoke_status = interpreter.Invoke();
    uint32_t elapsed = micros() - start;
    
    if (invoke_status != kTfLiteOk) {
        Serial.println("ERREUR : inférence échouée");
        return;
    }
    
    // 3. Lire la sortie
    TfLiteTensor* output = interpreter.output(0);
    int8_t predicted_class = output->data.int8[0];
    // Désentrelacer la sortie INT8 → valeurs réelles
    float scale = output->params.scale;
    int zero_point = output->params.zero_point;
    
    float* scores = (float*)malloc(output->bytes * sizeof(float));
    for (int i = 0; i < output->bytes; i++) {
        scores[i] = (output->data.int8[i] - zero_point) * scale;
    }
    
    // 4. Trouver la classe avec le score max
    int max_idx = 0;
    float max_score = scores[0];
    for (int i = 1; i < output->bytes; i++) {
        if (scores[i] > max_score) {
            max_score = scores[i];
            max_idx = i;
        }
    }
    
    Serial.print("Classe détectée : ");
    Serial.print(max_idx);
    Serial.print(" (");
    Serial.print(max_score * 100, 1);
    Serial.print("%) — Latence : ");
    Serial.print(elapsed / 1000.0f);
    Serial.println(" ms");
    
    free(scores);
    delay(500);  // Période d'échantillonnage
}
```

### 3.3 Configuration mémoire (CMSIS / linker script)

```ld
/* STM32F4 linker script — secteurs critiques pour TinyML */
MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 512K
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
    
    /* TCM (Tightly Coupled Memory) — accès 0-wait-state */
    DTCM  (rw)  : ORIGIN = 0x10000000, LENGTH = 64K
    ITCM  (rx)  : ORIGIN = 0x00000000, LENGTH = 16K
}

SECTIONS
{
    /* Modèle TFLite en flash (via la section .rodata) */
    .tflite_model : {
        KEEP(*model_data.o(.rodata*))
    } > FLASH
    
    /* Tensor Arena en DTCM (accès rapide) */
    .tensor_arena (NOLOAD) : {
        . += 50K;  /* Réserver 50 KB */
    } > DTCM
}
```

---

## 4. Benchmark et Métriques

### 4.1 Script de benchmark (côté hôte)

```python
def benchmark_tflite_micro(model_path: str, input_shape: tuple, 
                           n_iterations: int = 100) -> dict:
    """Benchmark un modèle TFLite Micro sur hôte (x86/ARM)."""
    import tflite_micro  # pip install tflite-micro
    
    model = open(model_path, 'rb').read()
    interpreter = tflite_micro.Interpreter.from_bytes(model)
    
    # Préparer l'entrée aléatoire
    np.random.seed(42)
    dummy_input = np.random.randint(-128, 127, size=input_shape, dtype=np.int8)
    
    interpreter.set_input(dummy_input, 0)
    
    import time
    latencies = []
    
    for _ in range(n_iterations):
        start = time.perf_counter()
        interpreter.invoke()
        elapsed = (time.perf_counter() - start) * 1000
        latencies.append(elapsed)
    
    output = interpreter.get_output(0)
    
    return {
        "latence_moyenne_ms": float(np.mean(latencies)),
        "latence_min_ms": float(np.min(latencies)),
        "latence_max_ms": float(np.max(latencies)),
        "latence_p99_ms": float(np.percentile(latencies, 99)),
        "fps": 1000 / np.mean(latencies),
        "taille_modele_kb": len(model) / 1024,
        "forme_sortie": output.shape,
    }

# Exemple
# bench = benchmark_tflite_micro("model_kws.tflite", (1, 10, 10, 1))
```

### 4.2 Repères performance par plateforme

| Plateforme | CPU | RAM | Modèle KWS (~20K params) | Latence | Consommation |
|:----------|:---|:---:|:------------------------:|:------:|:-----------:|
| **Cortex-M4** (STM32F4) | 120 MHz | 128 KB | DS-CNN INT8 | 8–15 ms | 8 mW |
| **Cortex-M7** (STM32H7) | 480 MHz | 1 MB | DS-CNN INT8 | 2–5 ms | 25 mW |
| **ESP32-S3** | 240 MHz | 512 KB | DS-CNN INT8 | 3–8 ms | 40 mW |
| **Cortex-M0+** (SAMD21) | 48 MHz | 32 KB | Tiny Conv (5K params) | 50–100 ms | 3 mW |
| **RISC-V** (GD32V) | 108 MHz | 32 KB | Tiny Conv (5K params) | 40–80 ms | 5 mW |
| **Cortex-M55** (Helium) | 400 MHz | 256 KB | DS-CNN INT8 | 1–2 ms | 15 mW |

---

## 5. Techniques Avancées

### 5.1 Quantification par plage dynamique (per-channel)

```python
# TFLite Micro supporte la quantification per-channel pour Conv2D
# → Meilleure précision que per-tensor pour les canaux peu actifs

# Activation : per-tensor (scale/zp communs)
# Poids : per-channel (scale/zp par canal de sortie) 
# → Supporté par CMSIS-NN via arm_convolve_s8()
```

### 5.2 Fusion d'opérateurs (operator fusion)

```python
# TFLite fusionne automatiquement :
# Conv2D + BatchNorm + ReLU6 → un seul opérateur
# Conv2D + ReLU → fusionné
# Conv2D + activation → fusionné

# Vérifier la fusion :
interpreter = tflite.Interpreter(model_content=tflite_model)
import flatbuffers
from tflite.Model import Model

# Les opérateurs fusionnés apparaissent comme des builtins
# "CONV_2D" avec fused_activation_function != NONE
```

### 5.3 Réduction de la Tensor Arena

```python
# La Tensor Arena est le plus grand consommateur de RAM.
# Techniques pour la réduire :

# 1. Utiliser un MicroMutableOpResolver au lieu de AllOpsResolver
#    → N'enregistrer QUE les ops utilisées
#    → Économie ~50 KB de code

# 2. Réordonner les tensors (planification mémoire)
#    TFLite Micro planifie automatiquement le buffer partagé
#    Vérifier : interpreter.arena_used_bytes()

# 3. Utiliser le buffer de sortie comme buffer d'entrée
#    (in-place) si la forme le permet

# 4. Réduire la taille du scratch buffer
#    Voir : tflite::MicroAllocator::GetDefaultTailUsage()
```

---

## 6. Workflow de Déploiement

```bash
# Pipeline complet : entraînement → déploiement µC

# 1. Entraîner le modèle
python3 train_kws_model.py --architecture dscnn_micro --epochs 50

# 2. Convertir en TFLite INT8
python3 convert_to_tflite.py --model model.h5 --output model_kws.tflite

# 3. Vérifier le modèle
python3 validate_tflite.py --model model_kws.tflite --test_data test.npy

# 4. Générer le tableau C
xxd -i model_kws.tflite > src/model_data.cc

# 5. Copier dans le projet embeddé (PlatformIO)
cp src/model_data.cc ~/projects/kws_esp32/src/

# 6. Compiler et flasher
cd ~/projects/kws_esp32
pio run --target upload

# 7. Tester sur cible
pio device monitor --baud 115200
```

---

## Pièges Courants

1. **Tensor Arena trop petite** : l'inférence échoue silencieusement. Toujours vérifier `interpreter.arena_used_bytes()` après allocation.

2. **Opérateur non supporté** : TFLite Micro a un sous-ensemble d'ops plus petit que TFLite. Vérifier avant déploiement.

3. **Modèle FP32 déployé sur µC** : TFLite Micro ne supporte que INT8. Toujours quantifier avec `representative_dataset`.

4. **Entrée INT8 mal interprétée** : le scale et zero_point de l'entrée doivent correspondre au format attendu par le modèle. Les données brutes µC doivent être converties.

5. **Overflow mémoire stack vs heap** : la Tensor Arena est souvent placée en BSS (heap), mais les buffers d'application locaux peuvent déborder le stack. Préférer l'allocation statique.

6. **Consommation énergétique de l'inférence continue** : si l'inférence tourne à 100% du temps, un µC peut consommer plus qu'un dispositif Linux idle. Utiliser des cycles veille/éveil (duty cycle).

---

## Références

- **TFLite Micro** : https://github.com/tensorflow/tflite-micro
- **TinyML Benchmark** : https://github.com/mlcommons/tiny
- **CMSIS-NN** : https://github.com/ARM-software/CMSIS-NN
- **PetitRoo (RISC-V TinyML)** : https://github.com/five-embeds/petitroo
- **TensorFlow Model Optimization** : https://www.tensorflow.org/model_optimization
- **MLCommons Tiny** : https://mlcommons.org/en/groups/research-tiny/
