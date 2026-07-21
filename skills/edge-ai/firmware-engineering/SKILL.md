---
name: "firmware-engineering"
description: "Ingénierie du firmware embarqué — bare-metal, HAL, boot sequence, linker, debugging, optimisation"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Ingénierie du Firmware Embarqué

## Vue d'ensemble

Développement professionnel de firmware pour systèmes embarqués : architecture bare-metal, HAL, séquence de boot, linkers, optimisation mémoire/temps, tests, et déploiement.

## Architecture Firmware

### Couches logicielles

```
┌──────────────────────────────────────┐
│           Application Layer           │  main(), tasks, state machines
├──────────────────────────────────────┤
│           Service Layer              │  CLI, logging, update OTA, crypto
├──────────────────────────────────────┤
│            HAL (Hardware Abstraction) │  API portable (init, read, write)
├──────────────────────────────────────┤
│           MCU Abstraction           │  CMSIS, STM32 HAL, ESP-IDF, Zephyr
├──────────────────────────────────────┤
│              Hardware                │  CPU, GPIO, timers, DMA, periph
└──────────────────────────────────────┘
```

### Patterns architecturaux

```c
// Pattern 1 : Round-Robin (Super Loop)
void main(void) {
    init();
    while(1) {
        process_uart();
        process_sensor();
        process_led();
        // Chaque fonction doit retourner vite (< 1ms)
    }
}

// Pattern 2 : State Machine
typedef enum { STATE_IDLE, STATE_MEASURE, STATE_TX, STATE_ERROR } system_state_t;
system_state_t state = STATE_IDLE;

void system_tick(void) {
    switch(state) {
        case STATE_IDLE:
            if (measure_ready()) state = STATE_MEASURE;
            break;
        case STATE_MEASURE:
            start_adc();
            state = STATE_TX;
            break;
        case STATE_TX:
            if (tx_complete()) state = STATE_IDLE;
            break;
        case STATE_ERROR:
            reset_system();
            break;
    }
}

// Pattern 3 : Coopératif (Protothreads / coroutines)
// Chaque "tâche" a son propre compteur d'état

// Pattern 4 : RTOS (FreeRTOS)
// Voir skill freertos-rtos
```

## Séquence de Boot

### Cortex-M Boot Sequence

```
Reset Vector → Reset_Handler
    │
    ├── 1. Set SP (Stack Pointer) from vector[0]
    ├── 2. Set PC = Reset_Handler from vector[1]
    │
    ├── 3. SystemInit() — Horloges, PLL, prescalers
    │      └── HSE → PLL → SYSCLK → AHB/APB dividers
    │
    ├── 4. .data copy (FLASH → RAM)
    │      └── Load LMA from _sidata → VMA at _sdata
    │
    ├── 5. .bss zero (RAM)
    │      └── Fill _sbss.._ebss with 0
    │
    ├── 6. Constructors (.init_array) — C++ global objects
    │      └── For each entry in __init_array_start..__init_array_end
    │
    ├── 7. main()
    │      ├── Hardware init (GPIO, UART, clocks, ADC)
    │      ├── RTOS init (xTaskCreate, vTaskStartScheduler)
    │      └── while(1) app loop
    │
    └── 8. HardFault si main() retourne
```

### Implementation Startup

```c
// SystemInit — Configuration horloge STM32F407
void SystemInit(void) {
    // Activer HSE
    RCC->CR |= RCC_CR_HSEON;
    while(!(RCC->CR & RCC_CR_HSERDY));

    // Configurer PLL : HSE 8MHz × 336 / 2 / 84 = 168MHz
    RCC->PLLCFGR = (8 << 0)  |    // PLL_M = 8
                   (336 << 6) |   // PLL_N = 336
                   (0 << 16) |    // PLL_P = 2 (bit 16=0 → /2)
                   (7 << 24) |    // PLL_Q = 7 (USB 48MHz)
                   RCC_PLLCFGR_PLLSRC_HSE;

    RCC->CR |= RCC_CR_PLLON;
    while(!(RCC->CR & RCC_CR_PLLRDY));

    // Configurer AHB/APB prescalers
    RCC->CFGR = RCC_CFGR_HPRE_DIV1 |    // AHB = SYSCLK /1
                RCC_CFGR_PPRE1_DIV4 |   // APB1 = AHB /4 = 42MHz
                RCC_CFGR_PPRE2_DIV2 |   // APB2 = AHB /2 = 84MHz
                RCC_CFGR_SW_PLL;        // Select PLL as SYSCLK

    while((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL);

    // Activer FPU
    SCB->CPACR |= (3 << 20) | (3 << 22);
}
```

## HAL Design Patterns

### HAL Portable

```c
// my_hal.h — Interface portable
#include <stdint.h>
#include <stdbool.h>

typedef enum { MY_OK = 0, MY_ERR_TIMEOUT, MY_ERR_BUSY, MY_ERR_INVAL } my_status_t;
typedef void (*my_callback_t)(void *arg);

// GPIO
void     my_gpio_set(uint8_t pin);
void     my_gpio_clear(uint8_t pin);
bool     my_gpio_read(uint8_t pin);
my_status_t my_gpio_irq_enable(uint8_t pin, my_callback_t cb);

// Timer
my_status_t my_timer_start(uint32_t us, my_callback_t cb);
void     my_timer_stop(void);
uint32_t my_timer_now_us(void);

// UART
my_status_t my_uart_init(uint32_t baud);
void     my_uart_send(const uint8_t *data, uint32_t len);
my_status_t my_uart_receive(uint8_t *buf, uint32_t len, uint32_t timeout);

// I2C
my_status_t my_i2c_write(uint8_t addr, const uint8_t *data, uint32_t len);
my_status_t my_i2c_read(uint8_t addr, uint8_t *buf, uint32_t len, uint32_t timeout);

// SPI
my_status_t my_spi_transfer(const uint8_t *tx, uint8_t *rx, uint32_t len);
```

### Implémentation STM32 (exemple)

```c
// my_hal_stm32f4.c
#include "my_hal.h"

void my_gpio_set(uint8_t pin) {
    // pin encoding : port<<4 | bit
    GPIO_TypeDef *gpio = gpio_port(pin >> 4);
    uint8_t bit = pin & 0x0F;
    gpio->BSRR = (1 << bit);
}

void my_gpio_clear(uint8_t pin) {
    GPIO_TypeDef *gpio = gpio_port(pin >> 4);
    uint8_t bit = pin & 0x0F;
    gpio->BSRR = (1 << (bit + 16));
}
```

## Gestion Mémoire

### Linker Script Avancé

```ld
MEMORY {
    FLASH  (rx)  : ORIGIN = 0x08000000, LENGTH = 1024K
    RAM    (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
    CCMRAM (rw)  : ORIGIN = 0x10000000, LENGTH = 64K
    BKPSRAM(rw)  : ORIGIN = 0x40024000, LENGTH = 4K   /* Backup SRAM */
}

SECTIONS {
    /* ITCMRAM — code critique temps réel */
    .itcm : ALIGN(32) {
        *(.isr_vector)
        . = ALIGN(256);
        _itim_start = .;
        *(.ramfunc)       /* Code temps réel en RAM */
        . = ALIGN(4);
        _itim_end = .;
    } > RAM AT > FLASH

    /* DMA buffers — alignés 32 bytes pour cache coherence */
    .dma_buffers (NOLOAD) : ALIGN(32) {
        *(.dma_buffer)
    } > CCMRAM

    /* Backup SRAM — données persistantes après reset */
    .backup (NOLOAD) : {
        *(.backup_data)
    } > BKPSRAM
}
```

### Memory Pool (statique, sans fragmentation)

```c
#define POOL_SIZE 16
#define BLOCK_SIZE 64

static uint8_t pool[POOL_SIZE][BLOCK_SIZE];
static uint32_t pool_mask = 0;  // Bitmap des blocs alloués

void *pool_alloc(void) {
    for (int i = 0; i < POOL_SIZE; i++) {
        if (!(pool_mask & (1 << i))) {
            pool_mask |= (1 << i);
            memset(pool[i], 0, BLOCK_SIZE);
            return &pool[i];
        }
    }
    return NULL;  // Pool epuisé
}

void pool_free(void *ptr) {
    int idx = ((uint8_t*)ptr - (uint8_t*)pool) / BLOCK_SIZE;
    pool_mask &= ~(1 << idx);
}
```

## Ring Buffer (Circular Buffer)

```c
#define RBUF_SIZE 256

struct ringbuf {
    uint8_t buf[RBUF_SIZE];
    volatile uint32_t head;  // ISR écrit ici
    volatile uint32_t tail;  // Main lit ici
};

bool ringbuf_put(struct ringbuf *rb, uint8_t byte) {
    uint32_t next = (rb->head + 1) & (RBUF_SIZE - 1);
    if (next == rb->tail) return false;  // Full
    rb->buf[rb->head] = byte;
    __DMB();  // Data memory barrier
    rb->head = next;
    return true;
}

bool ringbuf_get(struct ringbuf *rb, uint8_t *byte) {
    if (rb->head == rb->tail) return false;  // Empty
    *byte = rb->buf[rb->tail];
    __DMB();
    rb->tail = (rb->tail + 1) & (RBUF_SIZE - 1);
    return true;
}

// ISR-safe : head modifié seulement par l'ISR, tail par le main
// Taille doit être une puissance de 2 (masque AND)
```

## Watchdog et Supervision

```c
// IWDG (Independent Watchdog) — horloge LSI, reset si non refresh
void iwdg_init(uint32_t timeout_ms) {
    IWDG->KR = 0x5555;  // Unlock
    IWDG->PR = IWDG_PR_PR_4;     // Prescaler 64
    IWDG->RLR = timeout_ms * (LSI_FREQ / 64) / 1000;
    IWDG->KR = 0xCCCC;  // Start
}

void iwdg_refresh(void) {
    IWDG->KR = 0xAAAA;
}

// WWDG (Window Watchdog) — fenêtre temporelle pour refresh
void wwdg_init(uint32_t window_ms) {
    WWDG->CFR = WWDG_CFR_WDGTB_1 |  // Prescaler
                (window_count << 0); // Window upper limit
    WWDG->CR = WWDG_CR_WDGA | 0x7F;  // Enable, counter
}

// Pattern supervision
void supervisor_check(void) {
    static uint32_t last_tick = 0;
    uint32_t now = HAL_GetTick();

    // Vérifier que chaque tâche a tourné
    if (task1_last_run < now - 100) error_handler();  // Task1 bloquée
    if (task2_last_run < now - 10)  error_handler();  // Task2 trop lente

    // Pas de boucle infinie dans le main
    if (!main_loop_flag) error_handler();

    iwdg_refresh();
    main_loop_flag = false;
}
```

## Cli Embarqué

```c
// Console série minimaliste
void cli_process(uint8_t byte) {
    static char line[128];
    static int pos = 0;

    if (byte == '\r') {
        line[pos] = '\0';
        cli_execute(line);
        pos = 0;
    } else if (byte == '\b' && pos > 0) {
        pos--;
    } else if (pos < sizeof(line) - 1) {
        line[pos++] = byte;
    }
}

void cli_execute(const char *cmd) {
    if (strcmp(cmd, "help") == 0) {
        uart_puts("Commands: help, info, reset, stats, echo <text>\n");
    } else if (strcmp(cmd, "info") == 0) {
        char buf[64];
        snprintf(buf, sizeof(buf), "CPU: %lu MHz, Free heap: %u\n",
                 SystemCoreClock / 1000000, (unsigned)xPortGetFreeHeapSize());
        uart_puts(buf);
    } else if (strcmp(cmd, "reset") == 0) {
        NVIC_SystemReset();
    } else if (strncmp(cmd, "echo ", 5) == 0) {
        uart_puts(cmd + 5); uart_puts("\n");
    }
}
```

## FOTA (Firmware Over-The-Air)

```c
// Structure de firmware
typedef struct {
    uint32_t magic;         // 0xDEADBEEF
    uint32_t version;
    uint32_t size;          // Taille totale
    uint32_t crc32;         // CRC du payload
    uint32_t reserved[3];
    uint8_t  payload[];     // Binaire firmware
} __attribute__((packed)) firmware_header_t;

// Dual-bank (A/B) swapping
// Bank A : 0x08000000 (active)
// Bank B : 0x08080000 (backup)

bool fota_validate(firmware_header_t *fh) {
    if (fh->magic != 0xDEADBEEF) return false;
    if (fh->size > MAX_FIRMWARE_SIZE) return false;

    uint32_t calc_crc = crc32_le(0, (uint8_t*)fh->payload, fh->size);
    return calc_crc == fh->crc32;
}

void fota_switch_bank(void) {
    // Sur STM32 : modifier l'adresse de boot dans Option Bytes
    // Ou : jumper sur le vector table en RAM
    SCB->VTOR = VECTOR_TABLE_BANK_B;  // ARM Cortex-M
    __DSB();
    __ISB();
    // Reset logiciel
    NVIC_SystemReset();
}
```

## Optimisation Code / Taille

### Flags GCC

```makefile
# Taille minimale (-Os)
CFLAGS += -Os -ffunction-sections -fdata-sections -Wl,--gc-sections

# Optimisation vitesse (-O2 avec contrainte taille)
CFLAGS += -O2 -fomit-frame-pointer -funroll-loops --param max-unroll-times=2

# Debug (pas de strip)
CFLAGS += -g3 -gdwarf-4
LDFLAGS += -Wl,--print-memory-usage  # Rapport taille sections
```

### Techniques de compaction

```c
// 1. Constantes en flash (pas en RAM)
const uint8_t lookup_table[256] = { ... };  // Va en .rodata (flash)

// 2. Bit fields pour flags
typedef struct {
    uint8_t flag_a : 1;
    uint8_t flag_b : 1;
    uint8_t flag_c : 1;
    uint8_t spare  : 5;
} status_flags_t;

// 3. Union pour économiser RAM
typedef union {
    struct {
        uint32_t timestamp;
        uint16_t value;
    } sensor_data;
    uint8_t raw[6];           // Même espace pour DMA
} packet_t;

// 4. Fonction inline (gain performance, perte taille)
static inline uint32_t min_u32(uint32_t a, uint32_t b) {
    return (a < b) ? a : b;
}
```

## Tests de Firmware

### Tests unitaires (host)

```c
// test_ringbuf.c — compile et tourne sur Linux (cross-compilation)
// Pas besoin de MCU pour tester la logique
#include <assert.h>
#include <string.h>

// Copier le code à tester avec un #define HOST_TEST
#define HOST_TEST
#include "ringbuf.c"

void test_basic() {
    struct ringbuf rb;
    memset(&rb, 0, sizeof(rb));

    assert(ringbuf_put(&rb, 0x42) == true);
    assert(ringbuf_put(&rb, 0x43) == true);

    uint8_t byte;
    assert(ringbuf_get(&rb, &byte) == true);
    assert(byte == 0x42);
    assert(ringbuf_get(&rb, &byte) == true);
    assert(byte == 0x43);
    assert(ringbuf_get(&rb, &byte) == false);  // Empty
}

void test_full() {
    struct ringbuf rb;
    memset(&rb, 0, sizeof(rb));
    for (int i = 0; i < RBUF_SIZE - 1; i++)  // -1 car head != tail
        assert(ringbuf_put(&rb, i));
    assert(ringbuf_put(&rb, 0xFF) == false);  // Full
}
```

## Pitfalls

1. **Volatile** : Variables partagées ISR ↔ main doivent être `volatile`
2. **Stack overflow** : Toujours configurer un stack guard (MPU) ou au moins un pattern de remplissage
3. **Watchdog** : Toujours superviser les tâches (pas juste un toggle GPIO)
4. **.bss initialisation** : Sur MCU, .bss n'est PAS initialisé par le linker — c'est la startup qui le fait
5. **Endianness** : ARM Cortex-M est little-endian par défaut (configurable pour M3+)
6. **FPU stacking** : Sur M4/M7, lazy stacking peut causer des latences d'interruption
7. **Timing** : Ne pas utiliser HAL_Delay() dans les ISR — utiliser un timestamp tick
8. **CRC** : Toujours valider le firmware avant de le copier en flash (FOTA)
9. **Bootloader** : Le bootloader doit vérifier la validité du firmware avant de sauter

## Ressources

- ARM CMSIS : https://github.com/ARM-software/CMSIS_5
- STM32Cube FW : https://github.com/STMicroelectronics/STM32Cube
- MISRA-C:2012 Guidelines for safety-critical systems
- Embedded Artistry : https://embeddedartistry.com/