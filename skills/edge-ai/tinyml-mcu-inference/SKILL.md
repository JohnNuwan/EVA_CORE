---
name: tinyml-mcu-inference
description: "Inférence ML optimisée sur microcontrôleurs — CMSIS-NN (ARM Cortex-M), Xtensa NN (ESP32), RV32IMC (RISC-V), kernels optimisés, SIMD vectoriel, DSP intrinsics, mémoire TCM/SRAM, pipeline DMA, benchmark cross-platform et débogage."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - tinyml
      - cmsis-nn
      - arm-cortex-m
      - xtensa
      - risc-v
      - simd
      - dsp
      - dma
      - microcontroller
      - optimized-kernels
    related_skills:
      - tinyml-fundamentals
      - esp32-s3-deep-learning
      - tensorflow-lite-deep-dive
      - model-optimization-edge
---

# Inférence ML sur Microcontrôleurs

## Vue d'ensemble

L'inférence ML sur microcontrôleurs (µC) nécessite des kernels **extrêmement optimisés** qui exploitent chaque instruction et byte de mémoire disponibles. Cette skill couvre en profondeur les bibliothèques de kernels ML par architecture (ARM Cortex-M CMSIS-NN, Xtensa LX7 ESP-NN, RISC-V P-ext), les techniques SIMD/DSP, la gestion mémoire TCM/SRAM, et le déploiement cross-platform.

### Architectures cibles et optimisations

| Architecture | µC représentatifs | Instructions SIMD/DSP | Bibliothèque kernels | Perf relative |
|:------------|:------------------|:--------------------|:-------------------|:------------:|
| **Cortex-M4/M7** | STM32F4/H7, nRF52 | **SIMD** (16-bit) + DSP (MAC single-cycle) | CMSIS-NN | 1× (réf) |
| **Cortex-M33** | STM32U5, NXP i.MX RT | Helium (MVE) **128-bit SIMD** | CMSIS-NN v2 | 1.5-3× |
| **Cortex-M55** | Alif Ensemble | Helium (MVE) + **Matrix** | CMSIS-NN v2 | 2-4× |
| **Cortex-M85** | NXP i.MX RT700 | Helium (MVE 256-bit) | CMSIS-NN v2 | 3-5× |
| **Xtensa LX6/LX7** | ESP32, ESP32-S3 | **PIE** (instruction vectorielle) | ESP-NN | 1-2× |
| **RISC-V (P-ext)** | GD32V, Bouffalo | **P** extension (SIMD/DSP) | NMSIS-NN | 0.8-1× |

---

## 1. CMSIS-NN (ARM Cortex-M)

### 1.1 Architecture CMSIS-NN

CMSIS-NN (Cortex Microcontroller Software Interface Standard - Neural Networks) est la bibliothèque de référence pour l'inférence ML sur ARM Cortex-M. Elle est intégrée à TFLite Micro et utilisée par l'écosystème ARM.

```c
// Hiérarchie CMSIS-NN v2 :
//
// ┌──────────────────────────────────────┐
// │     TFLite Micro Interpreter         │
// ├──────────────────────────────────────┤
// │     CMSIS-NN Wrapper Layer           │
// │     (t_flite_cmsis_nn/)              │
// ├──────────────────────────────────────┤
// │     CMSIS-NN Kernels                 │
// │  ┌──────┐ ┌──────┐ ┌─────────────┐  │
// │  │ Conv │ │ Pool │ │ Activation  │  │
// │  │ S8   │ │ S8   │ │ S8 / S16   │  │
// │  └──────┘ └──────┘ └─────────────┘  │
// ├──────────────────────────────────────┤
// │     CMSIS-DSP (SIMD Intrinsics)      │
// │  ┌──────┐ ┌──────┐ ┌─────────────┐  │
// │  │MAC   │ │Add   │ │ Dot Product │  │
// │  │SIMD  │ │SIMD  │ │ SIMD        │  │
// │  └──────┘ └──────┘ └─────────────┘  │
// └──────────────────────────────────────┘
```

### 1.2 Convolution INT8 optimisée CMSIS-NN

```c
// Cœur de CMSIS-NN : convolution 2D INT8
// Utilise des instructions SIMD 16-bit (SMLAD) et DSP (SMLALD)

#include "arm_nnfunctions.h"
#include "arm_nnsupportfunctions.h"

// Structure de contexte pour convolution CMSIS-NN
typedef struct {
    int16_t *im2col_buffer;   // Buffer de réarrangement
    int16_t *scratch_buffer;  // Buffer temporaire
    int buf_size;             // Taille du buffer
} ConvContext;

// Convolution 2D INT8 avec CMSIS-NN
arm_cmsis_nn_status conv2d_s8_cmsis(
    const int8_t *input,
    const int16_t *input_dims,    // [batch, H, W, C_in]
    const int8_t *weights,
    const int16_t *weight_dims,   // [C_out, H_k, W_k, C_in]
    const int32_t *bias,
    int8_t *output,
    const int16_t *output_dims,   // [batch, H_out, W_out, C_out]
    int stride_h, int stride_w,
    int pad_h, int pad_w,
    int32_t input_offset, int32_t output_offset,
    int32_t *output_mult, int32_t *output_shift,
    int32_t activation_min, int32_t activation_max,
    int8_t *buffer_a,             // Buffer de travail
    int16_t *buffer_b             // Buffer im2col
) {
    // Configuration des paramètres
    cmsis_nn_conv_params conv_params;
    conv_params.input_offset = input_offset;
    conv_params.output_offset = output_offset;
    conv_params.stride.h = stride_h;
    conv_params.stride.w = stride_w;
    conv_params.padding.h = pad_h;
    conv_params.padding.w = pad_w;
    conv_params.activation.min = activation_min;
    conv_params.activation.max = activation_max;
    
    // Dimensions
    cmsis_nn_dims input_d;
    input_d.n = input_dims[0];
    input_d.h = input_dims[1];
    input_d.w = input_dims[2];
    input_d.c = input_dims[3];
    
    cmsis_nn_dims weight_d;
    weight_d.n = weight_dims[0];
    weight_d.h = weight_dims[1];
    weight_d.w = weight_dims[2];
    weight_d.c = weight_dims[3];
    
    cmsis_nn_dims output_d;
    output_d.n = output_dims[0];
    output_d.h = output_dims[1];
    output_d.w = output_dims[2];
    output_d.c = output_dims[3];
    
    cmsis_nn_dims filter_d = {weight_d.n, weight_d.h, weight_d.w, weight_d.c};
    
    // Exécution CMSIS-NN optimisée
    // Sur Cortex-M4/M7 : utilise SMLAD (dual 16-bit MAC) + SMLALD
    // Sur Cortex-M55 : utilise Helium MVE (128-bit vector)
    return arm_convolve_wrapper_s8(
        &conv_params,
        &input_d,
        input,
        &filter_d,
        weights,
        &weight_d,  // pour la quantification per-channel
        bias,
        &output_d,
        output,
        output_mult,
        output_shift,
        buffer_a,    // ~2 * C_out * sizeof(int32_t) pour l'accumulation
        buffer_b     // ~H_k * W_k * C_in * sizeof(int16_t) pour im2col
    );
}

// Benchmark
uint32_t bench_cmsis_conv() {
    uint32_t start = DWT->CYCCNT;  // Compteur de cycles DWT (Cortex-M)
    
    arm_convolve_wrapper_s8(...);
    
    uint32_t cycles = DWT->CYCCNT - start;
    float us = cycles / (float)SystemCoreClock * 1e6f;
    
    printf("CMSIS-NN Conv: %u cycles (%.1f µs)\n", cycles, us);
    return cycles;
}
```

### 1.3 CMSIS-NN sur Cortex-M55 (Helium)

```c
// Le Cortex-M55 dispose de l'extension Helium (MVE - M-profile Vector Extension)
// Vecteurs 128-bit → 16× INT8 simultanés

// arm_convolve_helium_s8() utilise :
// - VMLA : vector multiply-accumulate 16× INT8
// - VADD : vector add
// - VMOVL : vector move and extend
// - VLDR / VSTR : vector load/store 128-bit

// Exemple : code Helium pour une convolution partielle
__attribute__((always_inline))
static void helium_conv_partial(const int8_t *input, 
                                const int8_t *weights,
                                int32_t *accum, 
                                int n_elements) {
    // Chargement vecteur 16× INT8 des poids
    int8x16_t w_vec = vld1q_s8(weights);
    
    int i;
    for (i = 0; i < n_elements - 15; i += 16) {
        // Chargement vecteur 16× INT8 des entrées
        int8x16_t i_vec = vld1q_s8(&input[i]);
        
        // Multiplication élémentaire (16× INT8 → 16× INT16)
        int16x8_t prod_lo = vmull_s8(vget_low_s8(w_vec), vget_low_s8(i_vec));
        int16x8_t prod_hi = vmull_s8(vget_high_s8(w_vec), vget_high_s8(i_vec));
        
        // Accumulation pairwise (32-bit)
        accum[0] += vaddlvq_s16(prod_lo);  // Sum all 8 elements
        accum[0] += vaddlvq_s16(prod_hi);
    }
    
    // Reste (boucle scalaire)
    for (; i < n_elements; i++) {
        accum[0] += weights[i] * input[i];
    }
}
```

### 1.4 Intégration CMSIS-NN dans TFLite Micro

```makefile
# CMakeLists.txt — activation CMSIS-NN dans TFLite Micro

# Option 1 : via TFLite Micro + CMSIS-NN (recommandé)
set(TFLITE_MICRO_CMAKE_DIR "${TFLITE_ROOT}/tensorflow/lite/micro/tools/cmake")
add_subdirectory("${TFLITE_MICRO_CMAKE_DIR}" "${CMAKE_BINARY_DIR}/tflite-micro")

# Activer CMSIS-NN
target_compile_definitions(tflite-micro PRIVATE
    CMSIS_NN=1
    ARM_MATH_DSP=1
    ARM_MATH_LOOPUNROLL=1
)

# Lier CMSIS
target_link_libraries(tflite-micro PRIVATE
    cmsis-nn
    cmsis-dsp
)

# Option 2 : via l'outil de build TFLite Micro
# make -f tensorflow/lite/micro/tools/make/Makefile \
#     TARGET=cortex_m_generic \
#     TARGET_ARCH=cortex-m4+fp \
#     OPTIMIZED_KERNEL_DIR=cmsis_nn \
#     BUILD_TYPE=release \
#     microlite
```

---

## 2. Optimisations SIMD/DSP par Architecture

### 2.1 ARM Cortex-M4/M7 (SIMD 16-bit)

```c
// Instructions SIMD disponibles sur Cortex-M4/M7 :
// SMLAD : Dual 16-bit signed multiply-add → 32-bit accumulate
// SMLALD : Dual 16-bit signed multiply-add → 64-bit accumulate
// SMLADX : Crossed version (takes high/low from different halves)
// SMMLA : 8-bit × 8-bit → 32-bit (via SSAT16)

// Utilisation manuelle des intrinsics SIMD
#include "arm_math.h"

int32_t dot_product_simd(const int16_t *a, const int16_t *b, int n) {
    int32_t result = 0;
    
    // Traiter 2 éléments par instruction SIMD
    for (int i = 0; i < n - 1; i += 2) {
        // SMLAD : a[i]*b[i] + a[i+1]*b[i+1] → accumulate
        __asm volatile(
            "SMLAD %0, %1, %2, %0"
            : "+r"(result)
            : "r"(__PKHBT(a[i], a[i+1], 16)),  // Pack [a[i], a[i+1]]
              "r"(__PKHBT(b[i], b[i+1], 16))
        );
    }
    
    // Élément impair restant
    if (n % 2) {
        result += a[n-1] * b[n-1];
    }
    
    return result;
}

// Version plus efficace avec boucle déroulée
int32_t dot_product_simd_unrolled(const int16_t *a, const int16_t *b) {
    int32_t result = 0;
    
    // SMLAD peut traiter 4 paires en 4 instructions
    __asm volatile(
        "SMLAD %0, %1, %2, %0\n"
        "SMLAD %0, %3, %4, %0\n"
        "SMLAD %0, %5, %6, %0\n"
        "SMLAD %0, %7, %8, %0"
        : "+r"(result)
        : "r"(__PKHBT(a[0], a[1], 16)),  "r"(__PKHBT(b[0], b[1], 16)),
          "r"(__PKHBT(a[2], a[3], 16)),  "r"(__PKHBT(b[2], b[3], 16)),
          "r"(__PKHBT(a[4], a[5], 16)),  "r"(__PKHBT(b[4], b[5], 16)),
          "r"(__PKHBT(a[6], a[7], 16)),  "r"(__PKHBT(b[6], b[7], 16))
    );
    
    return result;
}
```

### 2.2 ARM Cortex-M55 (Helium 128-bit)

```c
// Helium (MVE) : instructions vectorielles 128-bit
// 16× INT8, 8× INT16, 4× INT32, 4× FP32 par instruction

#include "arm_mve.h"

// Convolution 1D avec Helium
void conv1d_helium(const int8_t *input, const int8_t *kernel,
                   int32_t *output, int len, int klen) {
    
    for (int i = 0; i < len; i++) {
        int32x4_t acc = vdupq_n_s32(0);
        
        // Charger 4× INT8 et multiplier en une instruction
        int j;
        for (j = 0; j < klen - 3; j += 4) {
            // VLD1 : charger 4× INT8
            int8x16_t in = vld1q_s8(&input[i + j]);
            int8x16_t ker = vld1q_s8(&kernel[j]);
            
            // VMLADAV : multiply-add accumulate across vector
            // Effectue : acc += sum(in[0..3] * ker[0..3])
            acc = vmladavaq_s8(acc, in, ker);
        }
        
        // Reste scalaire
        for (; j < klen; j++) {
            output[i] += input[i + j] * kernel[j];
        }
        
        output[i] += vaddvq_s32(acc);  // Sum des 4 accumulateurs
    }
}
```

### 2.3 Xtensa LX7 (ESP32-S3 — PIE)

```c
// Xtensa LX7 : PIE (Parallel Instruction Engine)
// Instructions spécifiques pour ML :
// AE_LS8X3_XP : charge 3 vecteurs 8-bit (24 octets)
// AE_MULAAP8S_AAAA : 8 MACs INT8 en 1 cycle
// AE_MULAAFP4S : 4 MACs FP16

// Utilisation dans ESP-NN :
#include "esp_nn.h"

// La fonction esp_nn_conv_s8() utilise PIE si disponible
// Sinon fallback sur une boucle C standard

// Exemple de kernel PIE manuel
void conv_pie_manual(const int8_t *input, const int8_t *kernel,
                     int8_t *output, int n_elements) {
    
    // Initialisation du registre d'accumulation PIE
    __asm__ volatile(
        "AE_SETQ_AA  a0, %0\n"    // Charger input pointer
        "AE_SETQ_AA  a1, %1\n"    // Charger kernel pointer
        "AE_SETQ_AA  a2, %2\n"    // Charger output pointer
        :
        : "r"(input), "r"(kernel), "r"(output)
    );
    
    // Boucle PIE
    for (int i = 0; i < n_elements / 8; i++) {
        __asm__ volatile(
            "AE_LS8X3_IP  %0, %1, %2, 24\n"     // Load 3×8 inputs
            "AE_MULAAP8S_AAAA  %0, %1\n"         // MAC 8× pairs
            :
            : "r"(input), "r"(kernel)
            : "memory"
        );
    }
}
```

### 2.4 RISC-V (P-ext ou V-ext)

```c
// RISC-V P-extension (DSP/SIMD) :
// Instructions SIMD 16/32-bit pour DSP et ML
// moins mature que ARM/Xtensa, mais en développement actif

// Utilisation de NMSIS-NN (équivalent CMSIS-NN pour RISC-V)
// https://github.com/Nuclei-Software/NMSIS

#include "riscv_nnfunctions.h"
#include "riscv_nnsupportfunctions.h"

// Convolution RISC-V P-ext
riscv_nn_status riscv_convolve_s8(
    const int8_t *input,
    const int16_t *dim_input,
    const int8_t *weights,
    const int16_t *dim_weights,
    const int32_t *bias,
    int8_t *output,
    const int16_t *dim_output,
    int32_t input_offset, 
    int32_t output_offset,
    int32_t *output_mult,
    int32_t *output_shift,
    int32_t activation_min, 
    int32_t activation_max,
    int16_t *buffer_a
) {
    // Utilise : pvdotsp (dot product SIMD RISC-V)
    // Similaire à CMSIS-NN mais pour RISC-V
    
    return riscv_convolve_wrapper_s8(
        input, dim_input, weights, dim_weights,
        bias, output, dim_output,
        input_offset, output_offset,
        output_mult, output_shift,
        activation_min, activation_max,
        buffer_a
    );
}
```

---

## 3. Gestion Mémoire pour Inférence

### 3.1 Hiérarchie mémoire Cortex-M

```c
// Hiérarchie mémoire typique d'un µC ML :
//
// ┌──────────────────────┐  Taille  Vitesse
// │    TCM (DTCM/ITCM)   │  64 KB  0 wait-state (1 cycle)
// │   — Tensor Arena     │         ← DONNÉES CRITIQUES
// │   — Buffers d'entrée │
// ├──────────────────────┤
// │    SRAM (Cacheable)   │  128 KB  2-3 cycles
// │   — Poids du modèle  │         ← SI TIENT EN SRAM
// │   — Big buffers      │
// ├──────────────────────┤
// │    SRAM (Non-cache)   │  64 KB  3-5 cycles
// │   — DMA descriptors  │
// │   — FIFO périphérie  │
// ├──────────────────────┤
// │    Flash (Execute)    │  1-2 MB  ~10 cycles (cache)
// │   — Modèle TFLite    │         ← Données en lecture seule
// │   — Code programme   │
// └──────────────────────┘
```

### 3.2 Placement mémoire des modèles

```ld
// Linker script — placement optimisé pour TFLite Micro

MEMORY
{
    /* Flash : modèle TFLite (lecture seule) */
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
    
    /* SRAM principale : utilisation générale */
    RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 256K
    
    /* DTCM : Tensor Arena (accès critique 0-wait) */
    DTCM  (rw)  : ORIGIN = 0x10000000, LENGTH = 64K
    
    /* ITCM : code critique (boucles d'inférence) */
    ITCM  (rx)  : ORIGIN = 0x00000000, LENGTH = 16K
}

SECTIONS
{
    /* 1. Modèle TFLite en flash */
    .tflite_model : ALIGN(4) {
        KEEP(*model_data.o(.rodata*))
    } > FLASH
    
    /* 2. Code critique d'inférence en ITCM */
    .itcm_code : ALIGN(4) {
        *cmsis_nn_conv*.o(.text*)
        *cmsis_nn_pool*.o(.text*)
        *arm_convolve*.o(.text*)
    } > ITCM AT > FLASH
    
    /* 3. Tensor Arena en DTCM */
    .tensor_arena (NOLOAD) : ALIGN(16) {
        . += 60K;  /* 60 KB pour Tensor Arena */
    } > DTCM
    
    /* 4. Buffers de travail en SRAM */
    .work_buffers (NOLOAD) : ALIGN(4) {
        . += 32K;  /* Buffers im2col + scratch */
    } > RAM
}
```

### 3.3 DMA pour le chargement des poids

```c
// Utiliser DMA pour charger les poids en arrière-plan
// Technique : double buffering (ping-pong)
// → Pendant que le CPU calcule, le DMA charge les poids suivants

#include "stm32h7xx_hal.h"

DMA_HandleTypeDef hdma;

typedef struct {
    int8_t *ping_buffer;
    int8_t *pong_buffer;
    volatile int active_buffer;
    volatile int dma_busy;
} DMADoubleBuffer;

void dma_init_ping_pong(DMADoubleBuffer *db, int buffer_size) {
    db->ping_buffer = (int8_t *)0x30000000;  // SRAM1 ping
    db->pong_buffer = (int8_t *)0x30020000;  // SRAM2 pong
    db->active_buffer = 0;
    db->dma_busy = 0;
    
    // Configuration DMA (MDMA pour transferts rapides)
    hdma.Instance = MDMA_Channel0;
    hdma.Init.Request = MDMA_REQUEST_SW;
    hdma.Init.Priority = MDMA_PRIORITY_HIGH;
    hdma.Init.SourceInc = MDMA_SRC_INC_BYTE;
    hdma.Init.DestInc = MDMA_DEST_INC_BYTE;
    hdma.Init.SourceDataSize = MDMA_SRC_DATASIZE_BYTE;
    hdma.Init.DestDataSize = MDMA_DEST_DATASIZE_BYTE;
    hdma.Init.DataAlignment = MDMA_DATAALIGN_PACK;
    hdma.Init.BufferTransferLength = buffer_size;
    HAL_MDMA_Init(&hdma);
}

void inference_with_dma(TFLiteInterpreter *interp, DMADoubleBuffer *db) {
    // Phase 1 : démarrer le DMA pour charger le lot 0
    int current = db->active_buffer;
    int8_t *target = current ? db->pong_buffer : db->ping_buffer;
    
    // DMA : flash → buffer (asynchrone)
    HAL_MDMA_Start_IT(&hdma, 
        (uint32_t)interp->model_data, 
        (uint32_t)target, 
        interp->model_size);
    db->dma_busy = 1;
    
    while (db->dma_busy) {
        // Phase 2 : pendant le DMA, faire du preprocessing
        preprocess_sensor_data();
    }
    
    // Phase 3 : DMA terminé → lancer l'inférence
    memcpy(interp->tensor_arena, target, interp->allocated_bytes);
    interp->Invoke();
    
    db->active_buffer = !current;
}

// Callback DMA
void HAL_MDMA_XferCpltCallback(MDMA_HandleTypeDef *hmdma) {
    DMADoubleBuffer *db = get_dma_context(hmdma);
    db->dma_busy = 0;
}
```

---

## 4. Techniques Avancées

### 4.1 Sub-byte quantization (INT4/INT2)

```c
// Certains µC supportent des poids sub-byte (INT4, INT2)
// Utile quand la RAM est très limitée (ex: 32 KB)

// Décodage de poids INT4 vers INT8 pour calcul
void load_int4_weights(const uint8_t *packed, int8_t *unpacked, int n) {
    for (int i = 0; i < n / 2; i++) {
        // Chaque octet contient 2× INT4
        uint8_t byte = packed[i];
        
        // INT4 signé : étendre le signe
        unpacked[2*i] = (int8_t)((byte & 0x0F) << 4) >> 4;    // low nibble
        unpacked[2*i+1] = (int8_t)((byte & 0xF0)) >> 4;        // high nibble
    }
}

// Convolution avec poids INT4
void conv_s8_int4_weights(
    const int8_t *input,
    const uint8_t *weights_int4,  // Poids empaquetés INT4
    int8_t *output,
    int input_c, int output_c,
    int kernel_size
) {
    // Buffer pour décompresser les poids INT4 → INT8
    int8_t weights_unpacked[output_c * input_c * kernel_size * kernel_size];
    load_int4_weights(weights_int4, weights_unpacked, 
                      output_c * input_c * kernel_size * kernel_size);
    
    // Convolution avec poids INT8 (standard)
    arm_convolve_wrapper_s8(
        ...
        weights_unpacked,  // Poids décompressés
        ...
    );
    
    // Résultat : 50% de mémoire poids économisée
    // Coût : ~10% de cycles CPU pour la décompression
}
```

### 4.2 Winograd pour convolutions 3×3

```c
// Winograd minimal filtering algorithm (F(2×2, 3×3))
// Réduit les multiplications de 9 par pixel à 4
// Gain ~2.25× pour les convolutions 3×3

// Utilisé dans CMSIS-NN pour certaines configurations
// Automatique si les dimensions le permettent

// Condition Winograd :
// - Kernel 3×3
// - Stride = 1
// - C_out >= 4 (pour justifier le overhead)
```

### 4.3 Scratch buffer optimisé

```c
// Le scratch buffer est un buffer partagé entre les couches
// Objectif : réduire la mémoire totale de la Tensor Arena

// Stratégie d'allocation :
// 1. Calculer la mémoire max nécessaire par couche
// 2. Allouer UN SEUL buffer de cette taille
// 3. Chaque couche utilise ce buffer (non simultané)

typedef struct {
    int8_t *im2col_buffer;    // Pour réarrangement im2col
    int32_t *accum_buffer;    // Pour accumulation MAC
    int size;                 // Taille totale allouée
} ScratchBuffer;

// Allocation optimale
int taille_scratch_optimale(
    int max_kh, int max_kw, int max_c_in,
    int max_c_out
) {
    // im2col : kh * kw * cin
    int im2col_size = max_kh * max_kw * max_c_in * sizeof(int16_t);
    
    // Accumulation : 2 * cout (pour CMSIS-NN)
    int accum_size = 2 * max_c_out * sizeof(int32_t);
    
    // Prendre le max des deux (non simultanés)
    return (im2col_size > accum_size) ? im2col_size : accum_size;
}
```

---

## 5. Benchmark Cross-Platform

### 5.1 Harness de benchmark

```c
// Harness de benchmark uniforme pour tous les µC

typedef struct {
    uint32_t cycles;          // Cycles CPU
    float time_us;            // Microsecondes
    int bytes_processed;      // Octets traités
    float ops_per_cycle;      // Opérations par cycle
} BenchResult;

BenchResult bench_conv2d(
    int input_h, int input_w, int input_c,
    int output_c, int kernel_size, int stride
) {
    BenchResult result = {0};
    
    // Calcul des opérations
    int output_h = (input_h - kernel_size) / stride + 1;
    int output_w = (input_w - kernel_size) / stride + 1;
    int macs = output_h * output_w * output_c * input_c * kernel_size * kernel_size;
    
    // Mesure des cycles
    uint32_t start = DWT->CYCCNT;
    
    arm_convolve_wrapper_s8(...);
    
    result.cycles = DWT->CYCCNT - start;
    result.time_us = result.cycles / (float)SystemCoreClock * 1e6f;
    result.ops_per_cycle = (float)macs / result.cycles;
    result.bytes_processed = input_h * input_w * input_c + 
                             output_h * output_w * output_c;
    
    return result;
}

// Profilage complet
void benchmark_complet() {
    printf("=== Benchmark ML µC ===\n");
    printf("CPU: %d MHz\n", SystemCoreClock / 1000000);
    
    // Test 1 : Conv 3×3 stride 1
    BenchResult r1 = bench_conv2d(32, 32, 3, 16, 3, 1);
    printf("Conv 3×3 stride 1: %.1f µs (%.2f MAC/cycle)\n", 
           r1.time_us, r1.ops_per_cycle);
    
    // Test 2 : Conv 3×3 stride 2 (downsample)
    BenchResult r2 = bench_conv2d(32, 32, 3, 16, 3, 2);
    printf("Conv 3×3 stride 2: %.1f µs (%.2f MAC/cycle)\n",
           r2.time_us, r2.ops_per_cycle);
    
    // Test 3 : Depthwise Conv 3×3 stride 1
    BenchResult r3 = bench_depthwise_conv(32, 32, 16, 3, 1);
    printf("DW Conv 3×3: %.1f µs (%.2f MAC/cycle)\n",
           r3.time_us, r3.ops_per_cycle);
    
    // Test 4 : Fully connected (8->16)
    BenchResult r4 = bench_fully_connected(8, 16);
    printf("FC 8→16: %.1f µs (%.2f MAC/cycle)\n",
           r4.time_us, r4.ops_per_cycle);
}
```

### 5.2 Résultats attendus (Cortex-M4 @ 120 MHz)

| Couche | Type | µs | MAC/cycle |
|:-------|:---:|:--:|:--------:|
| Conv 3×3, stride 1, 3→16 (32×32) | Standard | 1250 | 0.85 |
| Conv 3×3, stride 2, 3→16 | Standard | 410 | 0.88 |
| DW Conv 3×3, stride 1, 16 | Depthwise | 310 | 1.62 |
| FC 8→16 | Dense | 0.2 | 0.72 |
| Conv 3×3 + ReLU | Fused | 1270 | 0.83 |

---

## 6. Débogage et Profilage

### 6.1 Utilisation du DWT (Data Watchpoint and Trace)

```c
// Le compteur de cycles DWT est disponible sur tous les Cortex-M3+
// Idéal pour le profiling ML

void init_dwt() {
    if (!(CoreDebug->DEMCR & CoreDebug_DEMCR_TRCENA_Msk)) {
        CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
        DWT->CYCCNT = 0;
        DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
    }
}

uint32_t get_cycle_count() {
    return DWT->CYCCNT;
}

// Mesure fine grain
void profile_layer(const char *name, void (*layer_fn)(void)) {
    init_dwt();
    
    uint32_t start = get_cycle_count();
    layer_fn();
    uint32_t cycles = get_cycle_count() - start;
    
    printf("%-20s : %6u cycles (%.1f µs)\n", 
           name, cycles, cycles / (float)SystemCoreClock * 1e6f);
}
```

### 6.2 Vérification de l'intégrité mémoire

```c
// Vérifier que la Tensor Arena n'est pas corrompue
// Technique : canary values aux limites

#define CANARY_VALUE 0xDEADBEEF

typedef struct {
    uint32_t canary_start;
    uint8_t arena[TENSOR_ARENA_SIZE];
    uint32_t canary_end;
} SafeTensorArena;

SafeTensorArena safe_arena;

void init_safe_arena() {
    safe_arena.canary_start = CANARY_VALUE;
    safe_arena.canary_end = CANARY_VALUE;
}

int check_arena_overflow() {
    int ok = 1;
    if (safe_arena.canary_start != CANARY_VALUE) {
        printf("ERREUR: Canary start corrompu (début de l'arena)\n");
        ok = 0;
    }
    if (safe_arena.canary_end != CANARY_VALUE) {
        printf("ERREUR: Canary end corrompu (dépassement de l'arena)\n");
        ok = 0;
    }
    return ok;
}
```

---

## Pièges Courants

1. **Alignement mémoire** : les opérations SIMD nécessitent un alignement 16 bytes. Utiliser `__attribute__((aligned(16)))` ou `memalign()`.

2. **Cache coherency** : sur les Cortex-M7, le cache peut retourner des données périmées après un DMA. Invalider le cache avec `SCB_InvalidateDCache_by_Addr()`.

3. **Im2col buffer overflow** : `im2col` réarrange les données d'entrée et peut exploser la RAM. Pour une conv 3×3 stride 1 avec 16 entrées : 3×3×16 = 144 bytes par pixel de sortie. Vérifier la taille.

4. **Helium/MVE non disponible** : certains Cortex-M55 en configuration basse consommation désactivent Helium. Vérifier `__ARM_FEATURE_MVE`.

5. **PIE sur ESP32-S3 obsolète** : PIE est disponible sur S3 mais pas S2. Vérifier le target dans sdkconfig. `CONFIG_ESP32S3_PIE=y`.

6. **RISC-V P-ext immature** : la P-extension RISC-V n'est pas encore finalisée (draft v0.5.1). Les implémentations varient entre fabricants.

7. **Optimisation -O0 vs -O3** : les kernels CMSIS-NN nécessitent -O2 minimum pour activer les intrinsics SIMD. Sans optimisation, les performances chutent de 10×.

8. **Hardware divider** : vérifier que `__FPU_PRESENT` et `__DSP_PRESENT` sont définis. Sans FPU, les calculs d'échelle (mult/ shift) utilisent des softmath lentes.

---

## Références

- **CMSIS-NN** : https://github.com/ARM-software/CMSIS-NN
- **CMSIS-DSP** : https://github.com/ARM-software/CMSIS-DSP
- **Helium MVE** : https://developer.arm.com/Architectures/M-Profile%20Vector%20Extension
- **TFLite Micro CMSIS** : https://www.tensorflow.org/lite/microcontrollers
- **ESP-NN** : https://github.com/espressif/esp-nn
- **NMSIS-NN (RISC-V)** : https://github.com/Nuclei-Software/NMSIS
- **Arm ML Embedded Benchmark** : https://github.com/ARM-software/ML-embedded-evaluation-kit
- **Ethos-U NPU** : https://developer.arm.com/Processors/ Ethos-U55
- **MicroTVM** : https://tvm.apache.org/docs/topic/microtvm/index.html
