---
name: esp32-s3-deep-learning
description: "Deep Learning natif sur ESP32-S3 — ESP-DL, ESP-NN (optimisé pour Xtensa), accélération matérielle PIE/TIE, TFLite Micro avec custom kernels, traitement audio/vision temps réel, PSRAM, optimisation énergétique et déploiement."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags:
      - esp32-s3
      - esp-dl
      - esp-nn
      - xtensa
      - tflite-micro
      - edge-ai
      - esp-idf
      - deep-learning
      - audio
      - computer-vision
    related_skills:
      - tinyml-fundamentals
      - tinyml-mcu-inference
      - tensorflow-lite-deep-dive
      - model-optimization-edge
---

# Deep Learning sur ESP32-S3

## Vue d'ensemble

L'ESP32-S3 d'Espressif est le SoC le plus performant de la gamme ESP32 pour l'IA embarquée. Il intègre un processeur Xtensa LX7 dual-core à 240 MHz, une **extension vectorielle (PIE) optimisée pour les réseaux de neurones**, jusqu'à 512 KB SRAM + 16 MB PSRAM, et un accélérateur cryptographique.

### Spécifications clés

| Paramètre | Valeur |
|:----------|:------|
| CPU | Xtensa LX7 dual-core @ 240 MHz |
| SRAM | 512 KB (TCM + cache) |
| PSRAM | Jusqu'à 16 MB (octal SPI) |
| Flash | Jusqu'à 16 MB |
| DSP | PIE (Parallel Instruction Engine) — SIMD vectoriel |
| Instructions NN | S3E (esp-nn optimisé Xtensa) |
| Connectivité | WiFi 802.11 b/g/n + BLE 5.0 |
| Périphériques | USB OTG, LCD (8080), Camera (DVP), I2S |
| Consommation inference | ~40 mW (ML), ~10 μW (deep sleep) |

### Pipeline d'inférence ML sur ESP32-S3

```
┌──────────────────────────────────────────────────────┐
│        Entrée (Camera/Mic/IMU via I2S/SPI/DVP)       │
├──────────────────────────────────────────────────────┤
│               Prétraitement (PIE vectorisé)           │
├──────────────────────────────────────────────────────┤
│                 Inférence ML                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ TFLite   │  │ ESP-DL   │  │ ESP-NN kernels   │   │
│  │ Micro    │  │ (C++ ML) │  │ (Xtensa LX7 opt.) │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
├──────────────────────────────────────────────────────┤
│               Post-traitement (IA, filtrage)          │
└──────────────────────────────────────────────────────┘
```

---

## 1. ESP-NN : Bibliothèque de Kernels Neuronaux

### 1.1 Architecture ESP-NN

ESP-NN est la bibliothèque de kernels ML optimisés pour les processeurs Xtensa d'Espressif. Elle exploite l'extension **PIE (Parallel Instruction Engine)** qui permet des opérations SIMD vectorielles en une seule instruction.

```c
// Architecture des kernels ESP-NN :
// 1. Convolution 2D (INT8) — esp_nn_conv_s8()
// 2. Depthwise Convolution — esp_nn_depthwise_conv_s8()
// 3. Fully Connected — esp_nn_fully_connected_s8()
// 4. Pooling (Avg, Max) — esp_nn_avg_pool_s8(), esp_nn_max_pool_s8()
// 5. Activation (ReLU, ReLU6) — esp_nn_relu_s8()
// 6. Softmax — esp_nn_softmax_s8()
// 7. Multiplication élémentaire — esp_nn_mul_s8()
// 8. Add élémentaire — esp_nn_add_s8()

// Optimisations PIE :
// - Load multiple : AE_LS8X3_XP (charge 3 vecteurs 8-bit en 1 instruction)
// - Multiply-accumulate : AE_MULAAP8S_AAAA (8 MACs en 1 cycle)
// - Alignement automatique avec buffers de ping-pong
```

### 1.2 Convolution 2D avec ESP-NN

```c
#include "esp_nn.h"

void convolution_int8_example() {
    // Configuration de la convolution
    const int input_h = 32, input_w = 32, input_c = 3;
    const int output_h = 16, output_w = 16, output_c = 8;
    const int kernel_h = 3, kernel_w = 3;
    const int stride_h = 2, stride_w = 2;
    const int pad_h = 1, pad_w = 1;
    
    // Allocation
    int8_t *input_data = (int8_t *)heap_caps_malloc(
        input_h * input_w * input_c, MALLOC_CAP_DEFAULT);
    int8_t *output_data = (int8_t *)heap_caps_malloc(
        output_h * output_w * output_c, MALLOC_CAP_DEFAULT);
    
    // Poids (output_c, input_c, kernel_h, kernel_w)
    int8_t *weights = (int8_t *)heap_caps_malloc(
        output_c * input_c * kernel_h * kernel_w, MALLOC_CAP_DEFAULT);
    
    // Bias (int32_t)
    int32_t *bias = (int32_t *)heap_caps_malloc(
        output_c * sizeof(int32_t), MALLOC_CAP_DEFAULT);
    
    // Paramètres de quantification
    const int32_t input_offset = -128;  // zero_point pour INT8 asymétrique
    const int32_t output_offset = -128;
    const int32_t *bias_data = bias;
    const int32_t *output_shift = (int32_t[]){-5, -4, -6, -3, -5, -4, -7, -3};
    const int32_t *output_mult = (int32_t[]){
        1683492048, 1894522341, 1456789123, 2012345678,
        1789234567, 1567890123, 1345678901, 1890123456
    };
    const int32_t activation_min = -128;
    const int32_t activation_max = 127;
    
    // Exécution de la convolution ESP-NN
    esp_nn_conv_s8(
        input_data,
        input_w, input_h, input_c,
        weights,
        output_data,
        output_w, output_h, output_c,
        kernel_w, kernel_h,
        stride_w, stride_h,
        pad_w, pad_h,
        input_offset, output_offset,
        bias_data,
        output_shift,
        output_mult,
        activation_min, activation_max,
        NULL  // scratch buffer optionnel
    );
    
    printf("Convolution ESP-NN terminée\n");
    
    // Libération
    heap_caps_free(input_data);
    heap_caps_free(output_data);
    heap_caps_free(weights);
    heap_caps_free(bias);
}
```

### 1.3 Benchmark ESP-NN vs CMSIS-NN

```c
void bench_esp_nn() {
    const int iterations = 1000;
    uint32_t start, elapsed;
    float total = 0;
    
    // Convolution 16×16×3 → 8×8×8 (noeud typique d'un détecteur)
    for (int i = 0; i < iterations; i++) {
        start = esp_timer_get_time();
        
        esp_nn_conv_s8(
            input, 16, 16, 3,
            weights,
            output, 8, 8, 8,
            3, 3, 2, 2, 1, 1,
            input_offset, output_offset,
            bias, shift, mult,
            -128, 127, scratch
        );
        
        elapsed = esp_timer_get_time() - start;
        total += elapsed;
    }
    
    printf("Temps moyen per conv (ESP-NN) : %.2f µs\n", total / iterations);
    // ESP32-S3 @ 240 MHz : ~25-40 µs pour une conv 3×3 strided 2
    // CMSIS-NN sur Cortex-M7 @ 480 MHz : ~15-25 µs
    // Ratio perf/Hz comparable grâce à PIE
}
```

---

## 2. ESP-DL : Framework Deep Learning

### 2.1 Architecture ESP-DL

ESP-DL est le framework DL natif d'Espressif pour ESP32-S3/S2. Il permet de définir et exécuter des réseaux de neurones en C++ natif (sans TFLite).

```cpp
// Hiérarchie des couches ESP-DL :
// - Layer (base)
//   - Conv2D
//   - DepthwiseConv2D
//   - FullyConnected
//   - Pooling2D
//   - Activation (ReLU, PReLU, LeakyReLU, TanH, Sigmoid)
//   - Softmax
//   - Flatten, Reshape
//   - Add (skip connection)
//   - GlobalAveragePool2D
//   - Concatenate
//   - BatchNorm (fusionnée dans Conv)

#include "esp_dl.hpp"

using namespace dl;

// Définition d'un détecteur de visages simple
class DetecteurVisage : public Model {
private:
    Conv2D *conv1;
    DepthwiseConv2D *dw2;
    Conv2D *pw2;
    Conv2D *conv3;
    Conv2D *conv_out;
    GlobalAveragePool2D *gap;
    
public:
    DetecteurVisage() {
        // Définition manuelle des couches
        // Format : nom, sortie canaux, kernel, stride, padding, activation
        conv1 = new Conv2D(8, {3, 3}, {2, 2}, {1, 1}, "conv1");
        conv1->set_activation(ReLU::get_instance());
        
        dw2 = new DepthwiseConv2D({3, 3}, {1, 1}, {1, 1}, "dw2");
        dw2->set_activation(nullptr);  // linear
        
        pw2 = new Conv2D(16, {1, 1}, {1, 1}, {0, 0}, "pw2");
        pw2->set_activation(ReLU::get_instance());
        
        conv3 = new Conv2D(32, {3, 3}, {2, 2}, {1, 1}, "conv3");
        conv3->set_activation(ReLU::get_instance());
        
        conv_out = new Conv2D(2, {1, 1}, {1, 1}, {0, 0}, "conv_out");
        conv_out->set_activation(nullptr);  // scores bruts
        
        gap = new GlobalAveragePool2D("gap");
    }
    
    Tensor<int8_t> *forward(Tensor<int8_t> *input) override {
        auto x = conv1->forward(input);
        auto x_dw = dw2->forward(x);
        auto x_pw = pw2->forward(x_dw);
        // Skip connection (Add)
        auto x_add = x->add(x_pw);  // x + pw(x)
        delete x;
        delete x_dw;
        
        auto x2 = conv3->forward(x_add);
        delete x_add;
        
        auto x3 = conv_out->forward(x2);
        delete x2;
        
        auto output = gap->forward(x3);
        delete x3;
        
        return output;  // 2 scores (face / pas face)
    }
};
```

### 2.2 Entraînement et conversion ESP-DL

```python
# Étape 1 : entraîner le modèle en Python (PyTorch ou TensorFlow)
# Étape 2 : exporter les poids au format ESP-DL
# Étape 3 : copier les poids dans le projet ESP-IDF

# Export script Python → fichier de poids ESP-DL (.cpp/.hpp)
def exporter_poids_espdl(poids_numpy: np.ndarray, nom: str, taille_coeff: int):
    """Exporte des poids numpy vers format ESP-DL (INT8 + coeff)."""
    # ESP-DL stocke : poids INT8 + multiplicateur en Q-format
    # coeff = (real_range / quantized_range) * 2^Q
    
    # Quantifier les poids
    max_val = np.max(np.abs(poids_numpy))
    scale = max_val / 127.0
    poids_int8 = np.round(poids_numpy / scale).astype(np.int8)
    
    # Générer le fichier C++
    with open(f"{nom}.hpp", "w") as f:
        f.write("#pragma once\n\n")
        f.write("#include <stdint.h>\n\n")
        f.write(f"// Poids pour couche {nom}\n")
        f.write(f"// Scale = {scale:.10f}\n\n")
        
        # Formater en tableau 1D
        flat = poids_int8.flatten()
        f.write(f"const int8_t {nom}_weight[] = {{\n")
        for i in range(0, len(flat), 16):
            line = ", ".join(f"{v}" for v in flat[i:i+16])
            f.write(f"    {line},\n")
        f.write("};\n\n")
        f.write(f"const int {nom}_weight_size = {len(flat)};\n")
        
        # Multiplicateur (coeff)
        coeff = int(scale * (1 << taille_coeff))
        f.write(f"const int {nom}_coeff = {coeff};\n")
        f.write(f"const int {nom}_coeff_q = {taille_coeff};\n")
    
    print(f"Fichier ESP-DL généré : {nom}.hpp")
```

### 2.3 Détection de visages avec ESP-DL

```cpp
// EspFaceDetection : détection de visages temps réel
#include "esp_dl.hpp"
#include "esp_camera.h"
#include "model_face_coeff.hpp"  // Poids exportés

#define CAMERA_FRAME_SIZE FRAMESIZE_QVGA  // 320×240
#define INPUT_SIZE 64  // Taille d'entrée du réseau (64×64)

// Buffer d'image pour le réseau
int8_t *input_buffer;

extern "C" void app_main() {
    // Initialisation camera
    camera_config_t camera_config = {
        .pin_pwdn = -1,
        .pin_reset = -1,
        .pin_xclk = GPIO_NUM_15,
        .pin_sscb_sda = GPIO_NUM_4,
        .pin_sscb_scl = GPIO_NUM_5,
        .pin_d7 = GPIO_NUM_16,
        .pin_d6 = GPIO_NUM_17,
        .pin_d5 = GPIO_NUM_18,
        .pin_d4 = GPIO_NUM_12,
        .pin_d3 = GPIO_NUM_10,
        .pin_d2 = GPIO_NUM_8,
        .pin_d1 = GPIO_NUM_9,
        .pin_d0 = GPIO_NUM_11,
        .pin_vsync = GPIO_NUM_6,
        .pin_href = GPIO_NUM_7,
        .pin_pclk = GPIO_NUM_13,
        .xclk_freq_hz = 20000000,
        .ledc_timer = LEDC_TIMER_0,
        .ledc_channel = LEDC_CHANNEL_0,
        .pixel_format = PIXFORMAT_GRAYSCALE,
        .frame_size = CAMERA_FRAME_SIZE,
        .jpeg_quality = 12,
        .fb_count = 1,
    };
    esp_camera_init(&camera_config);
    
    // Chargement du modèle
    DetecteurVisage detecteur;
    
    // Allocation du buffer d'entrée (64×64×1 = 4096 bytes)
    input_buffer = (int8_t *)heap_caps_malloc(
        64 * 64, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    
    Tensor<int8_t> input;
    input.set_element(input_buffer);
    input.set_shape({64, 64, 1});
    input.set_exponent(-1);  // scale = 0.5
    
    while (1) {
        // Capture frame
        camera_fb_t *fb = esp_camera_fb_get();
        if (!fb) {
            printf("Erreur capture\n");
            continue;
        }
        
        // Redimensionnement en 64×64 (interpolation bilinéaire simple)
        resize_image(fb->buf, fb->width, fb->height,
                    input_buffer, 64, 64);
        
        // Inférence
        Tensor<int8_t> *output = detecteur.forward(&input);
        
        // Lecture du résultat
        int8_t *scores = output->get_element();
        float face_score = scores[1] * 0.5f;  // scale exponent
        float pas_face_score = scores[0] * 0.5f;
        
        if (face_score > 0.7) {
            printf("Visage détecté! (confiance: %.1f%%)\n", face_score * 100);
        }
        
        delete output;
        esp_camera_fb_return(fb);
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

---

## 3. TFLite Micro sur ESP32-S3

### 3.1 Intégration TFLite Micro + ESP-NN

```cpp
// TFLite Micro avec kernels ESP-NN optimisés
// build/CMakeLists.txt
//
// idf_component_register(
//     SRCS "main.cpp"
//     INCLUDE_DIRS "."
//     REQUIRES esp_nn tflite-micro
// )

#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/micro/kernels/esp_nn/esp_nn_conv.h"

void setup_tflite_esp32s3() {
    // Créer le résolveur d'ops avec kernels ESP-NN
    tflite::MicroMutableOpResolver<15> resolver;
    
    // Enregistrement des ops avec backend ESP-NN
    resolver.AddConv2D(
        tflite::Register_CONV_2D_ESP_NN()  // kernel ESP-NN, pas Xtensa générique
    );
    resolver.AddDepthwiseConv2D(
        tflite::Register_DEPTHWISE_CONV_2D_ESP_NN()
    );
    resolver.AddAveragePool2D();
    resolver.AddMaxPool2D();
    resolver.AddFullyConnected(
        tflite::Register_FULLY_CONNECTED_ESP_NN()
    );
    resolver.AddSoftmax();
    resolver.AddRelu();
    resolver.AddConcatenation();
    resolver.AddReshape();
    
    // Allocation tensors
    constexpr int kTensorArenaSize = 120 * 1024;  // 120 KB
    static uint8_t tensor_arena[kTensorArenaSize];
    
    tflite::MicroInterpreter interpreter(
        tflite::GetModel(g_model),
        resolver,
        tensor_arena,
        kTensorArenaSize
    );
    
    // ... inférence normale
}
```

### 3.2 Custom kernels pour TFLite Micro

```c
// Si une op n'est pas disponible dans ESP-NN, créer un custom kernel
// Exemple : custom kernel ESP32-S3 pour un prétraitement couleur

#include "esp_dsp.h"  // Bibliothèque DSP Espressif

TfLiteStatus PretraitementCouleurEval(TfLiteContext* context, TfLiteNode* node) {
    const TfLiteTensor* input = tflite::GetInput(context, node, 0);
    TfLiteTensor* output = tflite::GetOutput(context, node, 0);
    
    const float* in_data = tflite::GetTensorData<float>(input);
    float* out_data = tflite::GetTensorData<float>(output);
    
    int size = tflite::GetTensorShape(input).FlatSize();
    
    // Utiliser le DSP Xtensa pour transformation RGB → grayscale
    // Y = 0.299R + 0.587G + 0.114B
    // Optimisé via PIE vector instructions
    
    // Version 1 : C standard
    for (int i = 0; i < size; i += 3) {
        out_data[i/3] = 0.299f * in_data[i] +      // R
                        0.587f * in_data[i + 1] +   // G
                        0.114f * in_data[i + 2];    // B
    }
    
    // Version 2 : DSP Espressif (dsps_mul_f32, etc.)
    // À décommenter si esp-dsp disponible
    /*
    float coeff[3] = {0.299f, 0.587f, 0.114f};
    for (int i = 0; i < size/3; i++) {
        dsps_dotprod_f32_ae32(&in_data[i*3], coeff, &out_data[i], 3);
    }
    */
    
    return kTfLiteOk;
}
```

### 3.3 Gestion de la PSRAM

```cpp
// L'ESP32-S3 peut avoir jusqu'à 16 MB de PSRAM
// Le modèle TFLite et les tensors peuvent être placés en PSRAM
// Mais les calculs doivent utiliser la SRAM pour la vitesse

#include "esp_heap_caps.h"

// Allocation de la Tensor Arena : SRAM pour la vitesse
static uint8_t tensor_arena[120 * 1024]
    __attribute__((section(".dram1")));  // Forcer en SRAM

// Allocation des poids du modèle : PSRAM si > 512 KB
int8_t *model_weights;
size_t model_size;

void charger_modele_psram(const char *path) {
    // Lire le modèle depuis flash vers PSRAM
    FILE *f = fopen(path, "rb");
    if (!f) return;
    
    fseek(f, 0, SEEK_END);
    model_size = ftell(f);
    fseek(f, 0, SEEK_SET);
    
    // Allouer en PSRAM
    model_weights = (int8_t *)heap_caps_malloc(
        model_size, MALLOC_CAP_SPIRAM);
    
    fread(model_weights, 1, model_size, f);
    fclose(f);
    
    printf("Modèle chargé en PSRAM : %zu bytes\n", model_size);
}

// Vérification de l'espace libre
void check_memory() {
    printf("SRAM libre : %d bytes\n", 
           heap_caps_get_free_size(MALLOC_CAP_INTERNAL));
    printf("PSRAM libre : %d bytes\n", 
           heap_caps_get_free_size(MALLOC_CAP_SPIRAM));
    printf("Plus grand bloc SRAM : %d bytes\n",
           heap_caps_get_largest_free_block(MALLOC_CAP_INTERNAL));
}
```

---

## 4. Traitement Audio (Keyword Spotting)

### 4.1 Pipeline audio complet

```cpp
// Keyword Spotting sur ESP32-S3 avec I2S microphone

#include "driver/i2s.h"
#include "esp_dsp.h"
#include "esp_nn.h"

class KWS {
private:
    // MFCC parameters
    static const int N_FFT = 256;
    static const int N_MFCC = 10;
    static const int N_FRAMES = 10;
    static const int SAMPLE_RATE = 16000;
    
    int16_t *audio_buffer;
    float *fft_buffer;
    float *mel_buffer;
    float *mfcc_buffer;
    
    // Modèle TFLite
    tflite::MicroInterpreter *interpreter;
    
public:
    KWS() {
        // Allocation des buffers
        audio_buffer = (int16_t *)heap_caps_malloc(
            N_FFT * sizeof(int16_t), MALLOC_CAP_INTERNAL);
        fft_buffer = (float *)heap_caps_malloc(
            N_FFT * sizeof(float), MALLOC_CAP_INTERNAL);
        mel_buffer = (float *)heap_caps_malloc(
            20 * sizeof(float), MALLOC_CAP_INTERNAL);  // 20 filtre Mel
        mfcc_buffer = (float *)heap_caps_malloc(
            N_MFCC * sizeof(float), MALLOC_CAP_INTERNAL);
        
        // Configuration I2S (MEMs microphone)
        i2s_config_t i2s_config = {
            .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
            .sample_rate = SAMPLE_RATE,
            .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = 4,
            .dma_buf_len = N_FFT,
        };
        i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
        
        // Pins microphone
        i2s_pin_config_t pin_config = {
            .bck_io_num = GPIO_NUM_26,
            .ws_io_num = GPIO_NUM_25,
            .data_out_num = -1,
            .data_in_num = GPIO_NUM_27,
        };
        i2s_set_pin(I2S_NUM_0, &pin_config);
    }
    
    void compute_mfcc() {
        // 1. Pre-emphasis (filtre HF boost)
        for (int i = N_FFT - 1; i > 0; i--) {
            fft_buffer[i] = audio_buffer[i] - 0.97f * audio_buffer[i - 1];
        }
        fft_buffer[0] = audio_buffer[0];
        
        // 2. Fenêtrage (Hamming)
        for (int i = 0; i < N_FFT; i++) {
            fft_buffer[i] *= 0.54f - 0.46f * cosf(2 * M_PI * i / (N_FFT - 1));
        }
        
        // 3. FFT (via esp-dsp)
        dsps_fft2r_fc32(fft_buffer, N_FFT);
        
        // 4. Puissance spectrale
        float power[N_FFT/2];
        for (int i = 0; i < N_FFT/2; i++) {
            float re = fft_buffer[2*i];
            float im = fft_buffer[2*i + 1];
            power[i] = re * re + im * im;
        }
        
        // 5. Filtres Mel (20 filtres triangulaires)
        // (implémentation simplifiée — utiliser esp-dsp ou computation manuelle)
        
        // 6. Log + DCT pour les coefficients MFCC
        // (les 10 premiers coefficients = MFCC)
    }
    
    void infer() {
        // Capturer N_FRAMES frames audio
        float input_buffer[N_FRAMES * N_MFCC];
        
        for (int f = 0; f < N_FRAMES; f++) {
            // Lecture I2S
            size_t bytes_read;
            i2s_read(I2S_NUM_0, audio_buffer, 
                    N_FFT * sizeof(int16_t), &bytes_read, portMAX_DELAY);
            
            compute_mfcc();
            memcpy(&input_buffer[f * N_MFCC], mfcc_buffer, 
                   N_MFCC * sizeof(float));
        }
        
        // Inférence TFLite Micro
        auto input = interpreter->input(0);
        memcpy(input->data.int8, quantize_input(input_buffer), input->bytes);
        
        interpreter->Invoke();
        
        auto output = interpreter->output(0);
        int8_t predicted = dequantize_output(output->data.int8[0]);
        
        printf("Mot détecté : %d\n", predicted);
    }
};
```

---

## 5. Optimisations Spécifiques ESP32-S3

### 5.1 Cache et préchargement

```c
// ESP32-S3 a 16 KB de cache d'instructions et 8 KB de cache de données
// Optimiser le cache pour l'inférence ML

// 1. Aligner les poids sur 16 bytes pour un cache efficace
__attribute__((aligned(16))) int8_t weights_aligned[1024];

// 2. Préchargement des poids dans le cache avant l'inférence
__attribute__((optimize("-O3")))
void prefetch_weights(int8_t *weights, size_t size) {
    // Toucher la mémoire pour charger dans le cache DCache
    volatile int8_t sum = 0;
    for (size_t i = 0; i < size; i += 16) {
        sum += weights[i];  // Charge dans le cache
    }
    (void)sum;  // Empêche optimisation
}

// 3. Utiliser SPIRAM en cache direct (Flash MMU)
// Config : CONFIG_SPIRAM_FETCH_INSTRUCTIONS=y
//          CONFIG_SPIRAM_RODATA=y
```

### 5.2 Dual-core pour pipeline ML

```c
// Pipeline dual-core : capture + inférence simultanées

// Core 0 : capture et prétraitement
void task_capture(void *arg) {
    while (1) {
        // Capturer frame camera
        // Prétraiter (redimensionner, normaliser)
        // Copier dans buffer partagé
        // Notifier core 1
        xSemaphoreGive(sem_inference);
        vTaskDelay(pdMS_TO_TICKS(33));  // 30 FPS
    }
}

// Core 1 : inférence ML
void task_inference(void *arg) {
    while (1) {
        xSemaphoreTake(sem_inference, portMAX_DELAY);
        
        // Exécuter l'inférence sur le buffer partagé
        interpreter->Invoke();
        
        // Post-traitement
        process_output();
    }
}

void app_main() {
    sem_inference = xSemaphoreCreateBinary();
    
    xTaskCreatePinnedToCore(task_capture, "capture", 4096, NULL, 5, NULL, 0);
    xTaskCreatePinnedToCore(task_inference, "inference", 8192, NULL, 5, NULL, 1);
}
```

### 5.3 Optimisation énergétique

```c
// Stratégies de réduction de consommation :

// 1. Duty cycling : inférence périodique
void inference_periodique() {
    const int INTERVAL_SEC = 2;  // Inférence toutes les 2 secondes
    
    while (1) {
        // Réveil + inférence
        esp_light_sleep_start();  // ou esp_deep_sleep_start()
        
        int8_t result = run_inference();
        
        if (result > 0) {
            // Événement détecté → envoyer notification WiFi
            wifi_send_alert(result);
        }
        
        // Deep sleep jusqu'à la prochaine inference
        esp_sleep_enable_timer_wakeup(INTERVAL_SEC * 1000000);
    }
}

// 2. Ajustement dynamique de la fréquence CPU (DFS)
// Modulateur de fréquence basé sur la charge ML
void adjust_cpu_freq() {
    // Inference ML : 240 MHz
    esp_clk_cpu_freq_t freq = ESP_CPU_FREQ_240M;
    
    switch (current_mode) {
        case MODE_INFERENCE:
            freq = ESP_CPU_FREQ_240M;  // Pleine puissance
            break;
        case MODE_IDLE:
            freq = ESP_CPU_FREQ_40M;   // Économie
            break;
        case MODE_DEEP_SLEEP:
            // Arrêt complet du CPU
            break;
    }
    
    esp_clk_cpu_set(freq);
}

// 3. Activation sélective du PIE
// Le PIE (accélération vectorielle) consomme plus
// Ne l'activer que pendant la phase d'inférence
void enable_pie(bool enable) {
    if (enable) {
        // Activer le PIE (registre PS.PIE = 1)
        __asm__ volatile("wsr.ps %0" :: "r"(0x000F));
    } else {
        // Désactiver le PIE (registre PS.PIE = 0)
        __asm__ volatile("wsr.ps %0" :: "r"(0x000E));
    }
}
```

---

## 6. Exemples Complets

### 6.1 Détection de mouvements (IMU)

```c
// Détection de gestes avec MPU6050 + CNN
// Modèle : 6 entrées (accel+gyro) × 32 frames → Conv1D → 5 classes

void setup_imu_ml() {
    // I2C initialization
    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = GPIO_NUM_21,
        .scl_io_num = GPIO_NUM_22,
        .master.clk_speed = 400000,
    };
    i2c_param_config(I2C_NUM_0, &conf);
    i2c_driver_install(I2C_NUM_0, I2C_MODE_MASTER, 0, 0, 0);
    
    // Buffer circulaire pour 32 frames
    static int16_t imu_buffer[32 * 6];  // 32 frames × 6 axes
    
    while (1) {
        // Lecture MPU6050
        for (int i = 0; i < 32; i++) {
            read_mpu6050(&imu_buffer[i * 6]);
            vTaskDelay(pdMS_TO_TICKS(10));  // 100 Hz
        }
        
        // Normalisation
        float float_input[32 * 6];
        for (int i = 0; i < 32 * 6; i++) {
            float_input[i] = imu_buffer[i] / 16384.0f;  // ±2g
        }
        
        // Inférence
        run_tflite_inference(float_input);
    }
}
```

### 6.2 Classification d'images (Camera)

```bash
# Exemple complet : classification d'images ESP32-S3

# 1. Prérequis ESP-IDF 5.1+
. ~/esp/esp-idf/export.sh

# 2. Créer le projet
idf.py create-project esp32_classification

# 3. Configurer les composants
idf.py menuconfig
# → Component config → ESP-NN → Activer ESP-NN optimizations
# → Component config → TensorFlow Lite Micro → Activer
# → ESP32S3-specific → Support PSRAM → Activer

# 4. Copier le modèle TFLite
cp ~/models/mobilenet_v1_0.25_128_quant.tflite \
   components/main/model.tflite

# 5. Convertir en tableau C
xxd -i components/main/model.tflite > components/main/model_data.cc

# 6. Compiler et flasher
idf.py build
idf.py -p /dev/ttyUSB0 flash monitor
```

---

## Pièges Courants

1. **PSRAM lente pour l'inférence** : la PSRAM a une latence de ~12 cycles vs 0 pour SRAM. Ne JAMAIS placer la Tensor Arena ou les buffers de calcul en PSRAM — réserver la SRAM interne pour les données critiques.

2. **Fréquence CPU insuffisante** : à 240 MHz, l'ESP32-S3 est ~2× plus lent qu'un Cortex-M7 à 480 MHz. Compenser par les optimisations PIE et la quantification INT8.

3. **ESP-NN pas activé par défaut** : vérifier dans menuconfig que `CONFIG_ESP_NN_ENABLE=y`. Sans cela, les kernels génériques sont utilisés (3-5× plus lents).

4. **WiFi + inférence simultanée** : le WiFi utilise le même CPU et peut interrompre l'inférence. Réserver un core pour le WiFi et un pour l'inférence.

5. **Débordement de pile (stack overflow)** : l'inférence TFLite Micro consomme ~4-8 KB de stack. Augmenter la taille de pile des tâches : `configMINIMAL_STACK_SIZE` → 8192.

6. **Modèle trop grand pour PSRAM** : 16 MB max PSRAM, mais au-delà de 4 MB, l'adressage nécessite un mapping de page MMU. Réduire le modèle ou utiliser la quantification.

7. **ALIGNEMENT des buffers** : les opérations PIE nécessitent un alignement 16 bytes. Utiliser `heap_caps_aligned_alloc(16, size, MALLOC_CAP_INTERNAL)`.

---

## Références

- **ESP-DL** : https://github.com/espressif/esp-dl
- **ESP-NN** : https://github.com/espressif/esp-nn
- **ESP-DSP** : https://github.com/espressif/esp-dsp
- **ESP-IDF** : https://github.com/espressif/esp-idf
- **ESP-Protocols** : https://github.com/espressif/esp-protocols
- **TFLite Micro ESP** : https://github.com/espressif/tflite-micro-esp
- **Espressif AI** : https://github.com/espressif/esp-ai
- **ESP-WHO** : https://github.com/espressif/esp-who (détection visage)
- **ESP-Skainet** : https://github.com/espressif/esp-skainet (KWS)
