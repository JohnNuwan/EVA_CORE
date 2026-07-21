---
name: stm32-arm-cortex
description: "Programmer les microcontrôleurs STM32 (ARM Cortex-M0/M3/M4/M7) — HAL/LL, CubeMX, FreeRTOS, périphériques (TIM, ADC, DAC, DMA, USB, CAN), DSP avec FPU et CMSIS, debogage, bootloader."
version: 2.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux, macos, windows]
metadata:
  EVA:
    tags: [stm32, arm, cortex-m, hal, ll, cubemx, freertos, dma, tim, adc, dac, can-bus, usb, pwm, spi, i2c, uart, cmsis, dsp, swd, jtag, bootloader, openocd]
    related_skills: [embedded-systems-firmware, signal-processing-digital, esp32-iot, pcb-design-electronique]
---

# STM32 — Microcontrôleurs ARM Cortex-M

## Vue d'ensemble

Les microcontrôleurs STM32 (STMicroelectronics) sont basés sur l'architecture ARM Cortex-M (M0, M0+, M3, M4, M7, M33) et couvrent une large gamme de performances et de consommation. Ils sont le standard de facto pour l'embarqué industriel, l'IoT, la robotique et l'instrumentation. Cette compétence couvre la programmation bas niveau (HAL, LL, registres), les périphériques, le temps réel (FreeRTOS), le DSP (FPU + CMSIS-DSP), et les outils de développement.

### Gamme STM32

| Famille | Cœur | Fréquence max | FPU | DSP | RAM max | Flash max | Usage |
|:---|---|---:|---:|---:|---:|:---|
| **STM32F0** | Cortex-M0 | 48 MHz | — | — | 32 KB | 256 KB | Bas coût, simple |
| **STM32G0** | Cortex-M0+ | 64 MHz | — | — | 36 KB | 512 KB | Remplacement F0 |
| **STM32F1** | Cortex-M3 | 72 MHz | — | — | 96 KB | 1 MB | Usage général |
| **STM32F3** | Cortex-M4F | 72 MHz | ✓ | ✓ | 64 KB | 512 KB | DSP + analogique |
| **STM32F4** | Cortex-M4F | 180-240 MHz | ✓ | ✓ | 384 KB | 2 MB | Haute performance |
| **STM32H7** | Cortex-M7 + M4 | 480+240 MHz | ✓ | ✓ | 1 MB | 2 MB | Très haute perf. |
| **STM32L4** | Cortex-M4F | 80 MHz | ✓ | ✓ | 256 KB | 1 MB | Basse consommation |
| **STM32U5** | Cortex-M33 | 160 MHz | ✓ | ✓ | 768 KB | 2 MB | IoT sécurisé |
| **STM32WL** | Cortex-M4F | 48 MHz | ✓ | ✓ | 64 KB | 256 KB | LoRa intégré |

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Programmer un microcontrôleur STM32 avec la HAL (Hardware Abstraction Layer) ou la LL (Low Layer).
- Configurer un périphérique : GPIO, TIM (PWM, capture, encodeur), ADC (scan, injected), DAC, DMA.
- Mettre en œuvre une communication USB (HID, CDC, MSC, DFU) sur STM32.
- Implémenter un contrôle moteur (FOC, BLDC, stepper) avec TIM + ADC + DMA.
- Développer un système multitâche temps réel avec FreeRTOS sur STM32.
- Utiliser l'unité FPU (float) et les instructions DSP (SIMD) du Cortex-M4/M7 pour du traitement de signal.
- Programmer le bootloader (system memory, DFU, UART, CAN, USB) pour les mises à jour firmware.
- Déboguer avec SWD/JTAG, OpenOCD, GDB, printf via SEGGER RTT ou semihosting.

Ne pas utiliser pour : les projets très simples avec Arduino (préférer `arduino-programmation`), l'IoT Wi-Fi (préférer `esp32-iot`), les très gros volumes avec contrainte de coût maximal (préférer des MCU chinois comme GD32).

---

## 1. Environnement de Développement

### 1.1 Chaîne d'outils

```bash
# Installation sur Linux (ARM GCC + OpenOCD + STM32CubeCLT)
sudo apt install gcc-arm-none-eabi binutils-arm-none-eabi \
                 openocd stlink-tools

# STM32CubeMX (génération de code, Linux)
# Télécharger depuis st.com et exécuter
wget https://www.st.com/en/development-tools/stm32cubemx.html
# Extraction et lancement
java -jar STM32CubeMX

# STM32CubeCLT (ligne de commande)
# Télécharger depuis st.com, installer
sudo ./st-stm32cubeclt_*.sh

# IDE recommandés : STM32CubeIDE (basé Eclipse, gratuit),
# CLion + STM32 plugin, VS Code + Cortex-Debug
```

### 1.2 Structure d'un projet STM32 (HAL)

```
projet_stm32/
├── Core/
│   ├── Src/
│   │   ├── main.c              # Programme principal
│   │   ├── stm32f4xx_hal_msp.c # Configuration des périphériques
│   │   ├── stm32f4xx_it.c      # Gestionnaires d'interruptions
│   │   └── system_stm32f4xx.c  # Configuration système/Horloge
│   └── Inc/
│       ├── main.h
│       └── stm32f4xx_hal_conf.h
├── Drivers/
│   ├── STM32F4xx_HAL_Driver/   # HAL et LL
│   └── CMSIS/                  # CMSIS-Core, DSP, RTOS
├── Middlewares/                 # FreeRTOS, USB, FATFS, LwIP
└── .ioc                        # Fichier de configuration CubeMX
```

### 1.3 Configuration de l'horloge (HAL)

```c
void SystemClock_Config(void) {
    RCC_OscInitTypeDef RCC_OscInit = {0};
    RCC_ClkInitTypeDef RCC_ClkInit = {0};

    // Configuration des oscillateurs
    RCC_OscInit.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInit.HSEState = RCC_HSE_ON;
    RCC_OscInit.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInit.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInit.PLL.PLLM = 8;       // Diviseur d'entrée HSE (8 MHz / 8 = 1 MHz)
    RCC_OscInit.PLL.PLLN = 336;     // Multiplicateur (1 MHz × 336 = 336 MHz)
    RCC_OscInit.PLL.PLLP = RCC_PLLP_DIV2;  // Diviseur système (336 / 2 = 168 MHz)
    RCC_OscInit.PLL.PLLQ = 7;       // Diviseur USB (336 / 7 = 48 MHz)
    HAL_RCC_OscConfig(&RCC_OscInit);

    // Configuration des bus AHB/APB
    RCC_ClkInit.ClockType = RCC_CLOCKTYPE_HCLK | RCC_CLOCKTYPE_SYSCLK
                          | RCC_CLOCKTYPE_PCLK1 | RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInit.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInit.AHBCLKDivider = RCC_SYSCLK_DIV1;     // HCLK = 168 MHz
    RCC_ClkInit.APB1CLKDivider = RCC_HCLK_DIV4;      // APB1 = 42 MHz
    RCC_ClkInit.APB2CLKDivider = RCC_HCLK_DIV2;      // APB2 = 84 MHz
    HAL_RCC_ClockConfig(&RCC_ClkInit, FLASH_LATENCY_5);
}
```

---

## 2. Périphériques Fondamentaux

### 2.1 GPIO (Entrées/Sorties)

```c
void GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_Init = {0};

    // Activer l'horloge des GPIO
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    // Sortie : LED sur PA5 (push-pull, 50 MHz)
    GPIO_Init.Pin = GPIO_PIN_5;
    GPIO_Init.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_Init.Pull = GPIO_NOPULL;
    GPIO_Init.Speed = GPIO_SPEED_FREQ_HIGH;
    HAL_GPIO_Init(GPIOA, &GPIO_Init);

    // Entrée : bouton sur PB2 (pull-up, interruption)
    GPIO_Init.Pin = GPIO_PIN_2;
    GPIO_Init.Mode = GPIO_MODE_IT_FALLING;
    GPIO_Init.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOB, &GPIO_Init);

    // Activation des interruptions EXTI
    HAL_NVIC_SetPriority(EXTI2_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI2_IRQn);

    // État initial
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
}
```

### 2.2 Timer PWM

```c
TIM_HandleTypeDef htim2;

void TIM_PWM_Init(void) {
    TIM_OC_InitTypeDef sConfigOC = {0};

    __HAL_RCC_TIM2_CLK_ENABLE();

    htim2.Instance = TIM2;
    htim2.Init.Prescaler = 168 - 1;         // 168 MHz / 168 = 1 MHz (1 µs par tick)
    htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim2.Init.Period = 20000 - 1;           // Période = 20000 ticks = 20 ms (50 Hz)
    htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_PWM_Init(&htim2);

    // Canal 1 (PA0) — Servo SG90
    sConfigOC.OCMode = TIM_OCMODE_PWM1;
    sConfigOC.Pulse = 1500;                  // 1500 µs = position neutre (90°)
    sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
    sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
    HAL_TIM_PWM_ConfigChannel(&htim2, &sConfigOC, TIM_CHANNEL_1);

    // Démarrer le PWM
    HAL_TIM_PWM_Start(&htim2, TIM_CHANNEL_1);
}

// Définir l'angle du servo (0°-180°)
void Servo_SetAngle(uint8_t angle) {
    // Pulse : 1000 µs (0°) à 2000 µs (180°)
    uint16_t pulse = 1000 + (angle * 1000 / 180);
    __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse);
}
```

### 2.3 ADC avec DMA (scan continu)

```c
ADC_HandleTypeDef hadc1;
DMA_HandleTypeDef hdma_adc1;

#define ADC_BUFFER_SIZE 3
uint32_t adc_buffer[ADC_BUFFER_SIZE];  // 3 canaux : A0, A1, A2

void ADC_DMA_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};

    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_DMA2_CLK_ENABLE();

    // Configuration DMA
    hdma_adc1.Instance = DMA2_Stream0;
    hdma_adc1.Init.Channel = DMA_CHANNEL_0;
    hdma_adc1.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_adc1.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_adc1.Init.MemInc = DMA_MINC_ENABLE;
    hdma_adc1.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
    hdma_adc1.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
    hdma_adc1.Init.Mode = DMA_CIRCULAR;         // Mode circulaire
    hdma_adc1.Init.Priority = DMA_PRIORITY_HIGH;
    HAL_DMA_Init(&hdma_adc1);
    __HAL_LINKDMA(&hadc1, DMA_Handle, hdma_adc1);

    // Configuration ADC
    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;
    hadc1.Init.ScanConvMode = ENABLE;            // Scan de plusieurs canaux
    hadc1.Init.ContinuousConvMode = ENABLE;       // Continu
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.NbrOfConversion = ADC_BUFFER_SIZE; // 3 canaux
    hadc1.Init.DMAContinuousRequests = ENABLE;
    HAL_ADC_Init(&hadc1);

    // Configuration des canaux
    sConfig.Channel = ADC_CHANNEL_0;              // PA0
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_3CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    sConfig.Channel = ADC_CHANNEL_1;              // PA1
    sConfig.Rank = 2;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    sConfig.Channel = ADC_CHANNEL_2;              // PA2
    sConfig.Rank = 3;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);

    // Démarrage du DMA circulaire
    HAL_ADC_Start_DMA(&hadc1, adc_buffer, ADC_BUFFER_SIZE);
}
```

---

## 3. FreeRTOS sur STM32

### 3.1 Configuration FreeRTOS (FreeRTOSConfig.h)

```c
#define configUSE_PREEMPTION          1
#define configUSE_IDLE_HOOK           0
#define configUSE_TICK_HOOK           0
#define configCPU_CLOCK_HZ            ((uint32_t)168000000)
#define configTICK_RATE_HZ            ((TickType_t)1000)    // 1 ms par tick
#define configMAX_PRIORITIES          7
#define configMINIMAL_STACK_SIZE      ((uint16_t)128)
#define configTOTAL_HEAP_SIZE         ((size_t)(40 * 1024))  // 40 KB heap
#define configMAX_TASK_NAME_LEN       16
#define configUSE_16_BIT_TICKS        0
#define configUSE_MUTEXES             1
#define configUSE_QUEUE_SZ            10
#define configUSE_COUNTING_SEMAPHORES 1
#define configUSE_RECURSIVE_MUTEXES   1
#define configUSE_TIMERS              1
#define configTIMER_TASK_PRIORITY     2
#define configTIMER_QUEUE_LENGTH      10
#define configTIMER_TASK_STACK_DEPTH  256
```

### 3.2 Création de tâches

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

QueueHandle_t xSensorQueue;

// Tâche d'acquisition capteur (500 Hz, priorité 3)
void vTaskSensor(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(2);  // 2 ms = 500 Hz

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);

        // Lire l'ADC (via DMA, valeur déjà dans adc_buffer)
        uint16_t raw = (uint16_t)adc_buffer[0];
        xQueueSend(xSensorQueue, &raw, 0);  // Envoyer à la file
    }
}

// Tâche de contrôle PID (100 Hz, priorité 2)
void vTaskControl(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(10);  // 10 ms = 100 Hz
    uint16_t sensor_value;

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);

        if (xQueueReceive(xSensorQueue, &sensor_value, 0) == pdTRUE) {
            float output = PID_Update((float)sensor_value);
            TIM3->CCR1 = (uint16_t)output;  // Sortie PWM directe via registre
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    GPIO_Init();
    ADC_DMA_Init();

    xSensorQueue = xQueueCreate(10, sizeof(uint16_t));

    xTaskCreate(vTaskSensor, "Sensor", 256, NULL, 3, NULL);
    xTaskCreate(vTaskControl, "Control", 256, NULL, 2, NULL);

    vTaskStartScheduler();  // Ne retourne jamais

    for (;;);
}
```

---

## 4. DSP et FPU sur Cortex-M4/M7

### 4.1 Activation de la FPU (Single Precision)

```c
// Dans SystemCoreClockUpdate() ou au début de main() :

/* Activation FPU (Cortex-M4F/M7F) */
/* SCB->CPACR register, bits 20-23 */
/* 00 = FPU disabled, 11 = full access */
SCB->CPACR |= (3UL << 20) | (3UL << 22);

// Vérification
if ((SCB->CPACR & 0x00F00000) == 0x00F00000) {
    // FPU activée — les calculs float utilisent le matériel
}
```

### 4.2 Filtrage FIR avec CMSIS-DSP

```c
#include "arm_math.h"

#define BLOCK_SIZE  64
#define NUM_TAPS    32

// Coefficients FIR pré-calculés (filtre passe-bas, fc = 2 kHz, fs = 16 kHz)
float32_t fir_coeffs[NUM_TAPS] = {
    -0.0001, -0.0005, -0.0009, -0.0006, 0.0012, 0.0048, 0.0090,
     0.0112,  0.0091,  0.0021, -0.0075, -0.0152, -0.0158, -0.0062,
     0.0129,  0.0368,  0.0579,  0.0678,  0.0602,  0.0335, -0.0065,
    -0.0487, -0.0770, -0.0770, -0.0420,  0.0241,  0.1102,  0.1979,
     0.2664,  0.2988,  0.2869,  0.2329
};

arm_fir_instance_f32 fir_instance;
static float32_t fir_state[NUM_TAPS + BLOCK_SIZE];

void fir_init(void) {
    arm_fir_init_f32(&fir_instance, NUM_TAPS, fir_coeffs, fir_state, BLOCK_SIZE);
}

// Traitement d'un bloc (optimisé SIMD)
void process_block(float32_t *input, float32_t *output) {
    arm_fir_f32(&fir_instance, input, output, BLOCK_SIZE);
    // ~0.5 µs par échantillon sur STM32F4 à 168 MHz
}
```

### 4.3 FFT 256 points sur STM32

```c
#define FFT_SIZE 256

float32_t fft_input[FFT_SIZE * 2];  // Complexe : réelle + imaginaire
float32_t fft_output[FFT_SIZE];

void compute_fft(float32_t *samples) {
    arm_cfft_radix4_instance_f32 fft_instance;

    // Initialisation FFT (une seule fois)
    arm_cfft_radix4_init_f32(&fft_instance, FFT_SIZE, 0, 1);

    // Copie des échantillons (réelle) dans le buffer complexe
    for (uint16_t i = 0; i < FFT_SIZE; i++) {
        fft_input[2 * i] = samples[i];
        fft_input[2 * i + 1] = 0.0f;
    }

    // FFT (transformée complexe)
    arm_cfft_radix4_f32(&fft_instance, fft_input);

    // Calcul du module (magnitude)
    arm_cmplx_mag_f32(fft_input, fft_output, FFT_SIZE);

    // fft_output[i] contient l'amplitude pour la fréquence i * (fs / FFT_SIZE)
    // Exemple : fs = 16 kHz, FFT_SIZE = 256 → résolution = 62.5 Hz/bin
}
```

---

## 5. USB Device (CDC Virtual COM)

```c
// Configuration CubeMX : USB_OTG_FS en mode Device, CDC class

// Variables
USBD_HandleTypeDef hUsbDeviceFS;
uint8_t UserRxBufferFS[APP_RX_DATA_SIZE];

// Callback de réception USB → série
static int8_t CDC_Itf_Receive_FS(uint8_t *Buf, uint32_t *Len) {
    // Recopier les données reçues dans un buffer circulaire
    // pour le traitement par la boucle principale
    HAL_UART_Transmit(&huart2, Buf, *Len, 1000);  // Relai vers UART
    USBD_CDC_ReceivePacket(&hUsbDeviceFS);  // Réarmer la réception
    return (USBD_OK);
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USB_DEVICE_Init();  // USB CDC

    // L'interface apparaît comme "Virtual COM Port" sur le PC
    // Communication : 64 KB/s, full-speed 12 Mbps
    while (1) {
        // La boucle principale peut envoyer des données USB :
        // uint8_t msg[] = "Hello USB\n";
        // USBD_CDC_SetTxBuffer(&hUsbDeviceFS, msg, sizeof(msg));
        // USBD_CDC_TransmitPacket(&hUsbDeviceFS);
    }
}
```

---

## Pièges Courants

1. **Configuration d'horloge incorrecte :** Les STM32 ont un arbre d'horloge complexe (HSE, HSI, PLL, AHB, APB1, APB2). Une configuration erronée entraîne un fonctionnement à la mauvaise fréquence ou un blocage au démarrage. Vérifier les sorties MCO avec un oscilloscope.

2. **Accès DMA sans alignement mémoire :** Le DMA des STM32 F4/H7 peut exiger un alignement mémoire spécifique (32 bits alignés sur adresse 32 bits). Un buffer non aligné provoque des transferts erronés. Déclarer les buffers avec `__attribute__((aligned(4)))`.

3. **Interruptions non gérées (HardFault) :** Une interruption déclenchée sans handler installé provoque un HardFault. Configurer tous les vecteurs d'interruption dans `stm32f4xx_it.c`, même ceux non utilisés (pointer vers `HAL_Delay` ou une fonction vide).

4. **Configuration de l'ordre des canaux ADC :** En mode scan, l'ordre des canaux doit correspondre exactement à l'ordre de déclaration des `sConfig.Rank`. Un mauvais ordre donne des valeurs inversées.

5. **Watchdog mal rafraîchi dans FreeRTOS :** Le watchdog (IWDG) doit être rafraîchi par la tâche idle ou une tâche watchdog dédiée. Ne pas le rafraîchir dans une ISR (masque le blocage de la boucle principale).

6. **Buffer overflow dans les files FreeRTOS :** Une queue de taille insuffisante bloque l'expéditeur (si `portMAX_DELAY` est utilisé) ou perd des données (si `0` est utilisé). Dimensionner les queues selon la fréquence de production/consommation.

---

## Liste de vérification (Checklist)

- [ ] L'arbre d'horloge (HSE/PLL/AHB/APB) est correctement configuré pour la fréquence cible.
- [ ] Les GPIO sont configurés avec le bon mode, la bonne vitesse et les pull-up/pull-down.
- [ ] Les interruptions ont une priorité configurée et sont activées dans le NVIC.
- [ ] Les buffers DMA sont alignés sur 4 octets et déclarés avec l'attribut approprié.
- [ ] Les tâches FreeRTOS ont une pile dimensionnée avec marge de 30 % minimum.
- [ ] La FPU est activée (SCB->CPACR) et les calculs float utilisent le matériel.
- [ ] Les appels CMSIS-DSP utilisent les instructions SIMD du Cortex-M4/M7.
- [ ] L'USB est configuré avec les bons pull-up (DP) et l'oscillateur HSE calibré.
- [ ] Le CAN-Bus a la terminaison 120 Ω et le bon bit timing (SJW, BS1, BS2).
- [ ] Le bootloader est accessible (BOOT0/BOOT1) pour les mises à jour firmware.
- [ ] Les alimentations (VDD, VDDA, VREF) sont correctement découplées.
- [ ] Le watchdog est activé et rafraîchi dans la boucle principale ou une tâche dédiée.