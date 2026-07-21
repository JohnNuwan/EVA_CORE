---
name: "bootloaders"
description: "Bootloaders embarqués — stages, vector table, dual-bank, secure boot, MCU bootloader, USB DFU, OTA"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# Bootloaders Embarqués

## Vue d'ensemble

Conception et implémentation de bootloaders pour systèmes embarqués : architecture multi-stage, vector table remapping, dual-bank (A/B) swap, secure boot, bootloader STM32, USB DFU, FOTA (Firmware Over-The-Air).

## Architecture Bootloader

### Stages

```
Power-On Reset
    │
    ├── Stage 1 : ROM Bootloader (fabricant)
    │   ├── Charge depuis UART, USB, SPI, CAN, NAND, SD
    │   └── Vérifie signature (optionnel)
    │
    ├── Stage 2 : Primary Bootloader (flash)
    │   ├── Initialisation minimale (clocks, RAM, console)
    │   ├── Vérifie l'intégrité du firmware (CRC, signature)
    │   ├── Décision : boot normal vs update mode
    │   └── Jump au firmware
    │
    ├── Stage 3 : Application Firmware
    │   └── RTOS, stack réseau, application
    │
    └── Fallback : Recovery Mode
        └── Si le firmware est corrompu → attendre nouvelle image
```

### Map mémoire typique (STM32 1MB Flash)

```
Adresse         Taille   Contenu
0x08000000      32KB     Bootloader (Stage 2)
0x08008000      960KB    Firmware Application
0x0807F000      4KB      Configuration/Persistent
0x08080000              Fin flash

Avec dual-bank (A/B) :
Adresse         Taille   Contenu
0x08000000      32KB     Bootloader (protégé)
0x08008000      480KB    Bank A (firmware actif)
0x08080000      480KB    Bank B (firmware backup)
0x080F8000      32KB     Configuration
```

## Bootloader Minimal (Cortex-M)

### Startup

```c
// bootloader.c — Bootloader minimal, 2KB
#include <stdint.h>

#define APP_ADDRESS     0x08008000  // Adresse du firmware
#define BOOTLOADER_SIZE 0x8000      // 32KB
#define FW_MAGIC        0xDEADBEEF

// Structure d'en-tête du firmware
typedef struct __attribute__((packed)) {
    uint32_t magic;         // 0xDEADBEEF
    uint32_t version;       // Version majeure.mineure.patch
    uint32_t size;          // Taille en octets
    uint32_t crc32;         // CRC32 du payload
    uint32_t timestamp;     // Unix timestamp
    uint32_t reserved[2];
    uint8_t  description[32]; // Chaîne texte
    // Payload suit immédiatement
} fw_header_t;

// Vecteur d'interruption du firmware
typedef void (*vector_func_t)(void);
typedef struct {
    uint32_t *initial_sp;      // Stack pointer
    vector_func_t reset;       // Reset handler
    vector_func_t nmi;         // NMI
    vector_func_t hard_fault;  // HardFault
    // ... autres vecteurs
} vector_table_t;

// CRC32 logiciel
uint32_t crc32(const uint8_t *data, uint32_t len) {
    uint32_t crc = 0xFFFFFFFF;
    for (uint32_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++)
            crc = (crc >> 1) ^ (crc & 1 ? 0xEDB88320 : 0);
    }
    return ~crc;
}

// Vérification du firmware
bool verify_firmware(uint32_t addr) {
    fw_header_t *hdr = (fw_header_t*)addr;

    // 1. Vérifier magic
    if (hdr->magic != FW_MAGIC) return false;

    // 2. Vérifier CRC
    uint32_t calc = crc32((uint8_t*)(addr + sizeof(fw_header_t)),
                           hdr->size);
    if (calc != hdr->crc32) return false;

    // 3. Vérifier version (optionnel : ne pas downgrade)
    // if (hdr->version < current_version) return false;

    return true;
}

// Jump au firmware
void jump_to_app(uint32_t addr) {
    vector_table_t *vt = (vector_table_t*)addr;

    // Désactiver toutes les interruptions
    __disable_irq();
    for (int i = 0; i < 8; i++)
        NVIC->ICER[i] = 0xFFFFFFFF;

    // Désactiver SysTick
    SysTick->CTRL = 0;

    // Désactiver FPU si activé
    SCB->CPACR = 0;

    // Nettoyer les pending
    SCB->ICSR = SCB_ICSR_PENDSVCLR_Msk | SCB_ICSR_PENDSTCLR_Msk;

    // Remapper la vector table
    SCB->VTOR = addr;

    // Configurer le stack pointer
    __set_MSP((uint32_t)vt->initial_sp);

    // Jump
    vt->reset();
    // Ne revient jamais
}

int main(void) {
    // Initialisation minimale
    init_clocks();     // HSI + PLL rapide
    init_uart();       // Console debug
    init_led();

    uart_puts("Bootloader v1.0.0\n");
    uart_puts("Vérification du firmware...\n");

    // Vérifier intégrité
    if (verify_firmware(APP_ADDRESS)) {
        uart_puts("Firmware OK, démarrage...\n");
        jump_to_app(APP_ADDRESS);
    } else {
        uart_puts("Firmware corrompu !\n");
        uart_puts("Mode update : attente téléchargement...\n");
        wait_for_update();
    }

    // Attente update
    while(1) {
        process_uart_update();
        process_led();
    }
}
```

## Dual-Bank (A/B Swap)

### Stratégie

```
Boot normal :
  Bootloader → Bank A (active) → application

Update (FOTA) :
  Bootloader → écrit Bank B (pendant que Bank A tourne)
  → Flag "swap" dans backup SRAM
  → Reset
  Bootloader → lit flag → Bank B (active) → nouvelle app

Rollback (update failed) :
  Bootloader → Bank A toujours valide
  → 3 tentatives de Bank B échouées → Bank A (fallback)
  → Reset flag
```

### Implémentation

```c
// Backup SRAM pour drapeaux (non-volatile, survive au reset)
#define BACKUP_SRAM_BASE 0x40024000
#define BKP_FLAG_ADDR    (BACKUP_SRAM_BASE + 0)

#define FLAG_BOOT_BANK_A 0xA5A5A5A5
#define FLAG_BOOT_BANK_B 0x5A5A5A5A
#define FLAG_BOOT_RECOVERY 0x00000000

// Activer backup SRAM
void bkp_sram_enable(void) {
    RCC->APB1ENR |= RCC_APB1ENR_PWREN;
    PWR->CR |= PWR_CR_DBP;  // Disable backup domain write protect
    RCC->CSR |= RCC_CSR_BACKUPSRAMEN;
    __DSB();
}

// Choisir la banque
uint32_t select_boot_bank(void) {
    volatile uint32_t *flag = (uint32_t*)BKP_FLAG_ADDR;

    if (*flag == FLAG_BOOT_BANK_A) {
        if (verify_firmware(BANK_A_ADDR)) {
            return BANK_A_ADDR;
        }
        // Bank A corrompue → essayer B
        *flag = FLAG_BOOT_BANK_B;
    }

    if (*flag == FLAG_BOOT_BANK_B) {
        if (verify_firmware(BANK_B_ADDR)) {
            return BANK_B_ADDR;
        }
        // Les deux corrompues → recovery
        *flag = FLAG_BOOT_RECOVERY;
    }

    return 0;  // Recovery mode
}

// Commuter vers la nouvelle banque après update
void commit_update(void) {
    volatile uint32_t *flag = (uint32_t*)BKP_FLAG_ADDR;
    *flag = (*flag == FLAG_BOOT_BANK_A) ? FLAG_BOOT_BANK_B : FLAG_BOOT_BANK_A;
    NVIC_SystemReset();
}

// Rollback (après N tentatives échouées)
void rollback_update(void) {
    volatile uint32_t *flag = (uint32_t*)BKP_FLAG_ADDR;
    *flag = (*flag == FLAG_BOOT_BANK_A) ? FLAG_BOOT_BANK_A : FLAG_BOOT_BANK_B;
    // Retour à l'ancienne banque
    NVIC_SystemReset();
}
```

## Secure Boot

### Chaîne de confiance

```
Boot ROM (fabricant) → vérifie signature Bootloader
    ↓ (signature RSA/Elliptic Curve)
Bootloader (flash) → vérifie signature Firmware
    ↓ (signature ECDSA)
Firmware Application
    ↓ (crypto vérifie chaque mise à jour)
OTA Update
```

### Implémentation vérification ECDSA (micro-ecc)

```c
// Utilisation de micro-ecc (uECC) — < 5KB flash
#include "uECC.h"

// Clé publique du firmware (hash dans le bootloader)
// 256-bit P-256 curve
static const uint8_t public_key[64] = {
    0x...  // 64 bytes (x,y)
};

bool verify_signature(const uint8_t *data, uint32_t len,
                      const uint8_t *signature) {
    // Hash SHA-256 du firmware
    uint8_t hash[32];
    sha256_calculate(data, len, hash);

    // Vérifier signature ECDSA
    return uECC_verify(public_key, hash, sizeof(hash),
                       signature, uECC_secp256r1());
}

// Le bootloader contient le hash de la clé publique
// (pas la clé elle-même — attaque impossible)
bool verify_public_key(const uint8_t *key) {
    uint8_t hash[32];
    sha256_calculate(key, 64, hash);
    // Comparer avec le hash stocké en ROM bootloader
    return memcmp(hash, stored_hash, 32) == 0;
}
```

### Anti-downgrade

```c
// Version minimum autorisée (stockée en OTP / backup SRAM)
uint32_t min_allowed_version = 0x01000000;  // 1.0.0

bool check_version(fw_header_t *hdr) {
    if (hdr->version < min_allowed_version) {
        // Downgrade attack détecté
        uart_puts("ANTI-DOWNGRADE : version trop ancienne\n");
        report_security_event();
        return false;
    }
    // Mettre à jour la version minimum
    // (en OTP — ne peut pas être réécrit à un nombre inférieur)
    write_otp_version(hdr->version);
    return true;
}
```

## Bootloader USB DFU (Device Firmware Update)

### STM32 System Bootloader (ROM)

```bash
# Activation (BOOT0=1, BOOT1=0)
# USB DFU sur STM32F4 — DFU mode
# Outil : dfu-util
sudo dfu-util -l  # Lister devices

# Flasher firmware
sudo dfu-util -a 0 -s 0x08000000:leave -D firmware.bin

# Avec Dual Bank
sudo dfu-util -a 0 -s 0x08080000 -D update.bin  # Bank B
```

### Custom DFU

```c
// Implémentation DFU minimal (protocole USB DFU 1.1)
// Requiert : USB device stack (TinyUSB, ST USB, etc.)

typedef enum {
    DFU_DNLOAD = 1,  // Télécharger
    DFU_UPLOAD = 2,  // Téléverser
    DFU_GETSTATUS = 3,
    DFU_CLRSTATUS = 4,
    DFU_GETSTATE = 5,
    DFU_ABORT = 6
} dfu_request_t;

// États DFU
typedef enum {
    DFU_STATE_IDLE = 2,
    DFU_STATE_DNLOAD_IDLE = 3,
    DFU_STATE_DNLOAD_BUSY = 4,
    DFU_STATE_DNLOAD_DONE = 5,
    DFU_STATE_MANIFEST = 7,
    DFU_STATE_ERROR = 10
} dfu_state_t;

// Gestionnaire DFU
void dfu_handle_request(uint8_t bRequest, uint16_t wValue,
                        uint16_t wIndex, uint16_t wLength) {
    static uint32_t flash_addr = APP_ADDRESS;
    static uint32_t total_bytes = 0;

    switch (bRequest) {
        case DFU_DNLOAD:
            // Écrire en flash (wValue = block num, wLength = taille)
            uint32_t block = wValue;
            if (block == 0) {
                // Block 0 : en-tête (adresse, taille)
                flash_addr = flash_buf[0] | (flash_buf[1] << 8);
                total_bytes = 0;
            } else {
                // Écrire ce bloc en flash
                flash_write(flash_addr + total_bytes,
                           flash_buf, wLength);
                total_bytes += wLength;
            }
            break;

        case DFU_GETSTATUS:
            dfu_status.bState = DFU_STATE_DNLOAD_IDLE;
            dfu_status.bStatus = 0;
            break;
    }
}
```

## FOTA (Firmware Over-The-Air)

### Architecture client

```c
// Téléchargement par trames
#define FOTA_CHUNK_SIZE 512  // 512 bytes par frame
#define FOTA_RETRIES 3

typedef struct {
    uint32_t total_size;
    uint32_t received;
    uint32_t crc32;
    uint32_t version;
    uint8_t  signature[64];
} fota_session_t;

static fota_session_t session;

bool fota_start(const char *url, uint32_t version) {
    // Vérifier version
    if (version <= current_version) return false;

    // Vérifier espace
    if (get_free_flash() < MAX_FIRMWARE_SIZE) {
        uart_puts("FOTA: Pas assez de flash\n");
        return false;
    }

    // Initialiser session
    session.total_size = 0;
    session.received = 0;
    session.version = version;

    // Activer bank B (inactive)
    flash_erase(BANK_B_ADDR, BANK_SIZE);

    uart_puts("FOTA: Début téléchargement...\n");
    return true;
}

bool fota_chunk(uint32_t offset, const uint8_t *data, uint32_t len) {
    if (offset != session.received) {
        // Perte de paquet — demander retransmission
        return false;
    }

    // Écrire en flash bank B
    flash_write(BANK_B_ADDR + offset, data, len);
    session.received += len;
    return true;
}

bool fota_finish(void) {
    // Vérifier intégrité
    fw_header_t *hdr = (fw_header_t*)BANK_B_ADDR;
    if (!verify_firmware(BANK_B_ADDR)) {
        uart_puts("FOTA: Échec CRC\n");
        flash_erase(BANK_B_ADDR, BANK_SIZE);
        return false;
    }

    // Vérifier signature
    if (!verify_signature((uint8_t*)BANK_B_ADDR,
                          hdr->size + sizeof(fw_header_t),
                          session.signature)) {
        uart_puts("FOTA: Signature invalide\n");
        flash_erase(BANK_B_ADDR, BANK_SIZE);
        return false;
    }

    // Commuter
    commit_update();
    return true;  // Ne sera jamais atteint (reset)
}
```

## Bootloader pour divers MCU

### STM32 (System Memory Bootloader)

```c
// ROM bootloader dans 0x1FFF0000 (STM32F4)
// Activation : BOOT0=1, BOOT1=0
// Protocoles : USART1, USART3, CAN2, USB OTG FS, DFU, I2C, SPI

// Protocole UART bootloader :
// Host → MCU : 0x7F (sync)
// MCU → Host : 0x79 (ACK) ou 0x1F (NACK)
// Commandes : Get, GetVersion, GetID, ReadMemory, WriteMemory, Erase, Go

// Exemple : WriteMemory via UART
// 1. Sync : 0x7F
// 2. WriteMemory cmd : 0x31
// 3. Adresse (3 bytes) + checksum
// 4. Data length (1 byte) + data + checksum
```

### ESP32 (ROM Bootloader)

```c
// ESP32 ROM bootloader à 0x40000000
// Stages :
//   1. ROM : UART download, SPI flash detection
//   2. Bootloader (flash) : partition table, OTA selection
//   3. Application

// Partition table :
// # ESP-IDF partition table
// # Name, Type, SubType, Offset, Size, Flags
// nvs,      data, nvs,     0x9000,  0x4000,
// otadata,  data, ota,     0xd000,  0x2000,
// phy_init, data, phy,     0xf000,  0x1000,
// factory,  app,  factory, 0x10000, 1M,
// ota_0,    app,  ota_0,   0x110000, 1M,
// ota_1,    app,  ota_1,   0x210000, 1M,

// OTA sélection (otadata) :
// 0xFFFFFFFF → factory
// 0x00000000 → ota_0
// 0x00000001 → ota_1
```

### i.MX RT (ROM Bootloader)

```
// NXP i.MX RT — boot from QSPI Flash, NAND, SD, eMMC
// ROM supporte flexSPI NOR, NAND, SD/MMC, SDP (Serial Download Protocol)
// Image header obligatoire (IVT + DCD)

// IVT (Image Vector Table) :
// 0x000 : Header (tag, length, version)
// 0x008 : Entry point
// 0x00C : Reserved
// 0x010 : DCD (Device Configuration Data) pointer
// 0x014 : Boot Data (start, size, plugin)
// 0x018 : Self pointer
// 0x01C : CSF (Command Sequence File) pointer
// 0x020 : Reserved
```

## Linker Script pour Bootloader

```ld
/* Bootloader spécifique — il doit ignorer l'espace du firmware */
MEMORY {
    FLASH_BL (rx) : ORIGIN = 0x08000000, LENGTH = 32K
    RAM (rwx)     : ORIGIN = 0x20000000, LENGTH = 64K
    BACKUP (rw)   : ORIGIN = 0x40024000, LENGTH = 4K
}

SECTIONS {
    /* Vector table à l'adresse de boot */
    .isr_vector : ALIGN(256) {
        KEEP(*(.isr_vector))
    } > FLASH_BL

    /* Code bootloader */
    .text : {
        *(.text*)
        *(.rodata*)
    } > FLASH_BL

    /* Données en RAM */
    .data : {
        _sdata = .;
        *(.data*)
        _edata = .;
    } > RAM AT > FLASH_BL

    .bss : {
        _sbss = .;
        *(.bss*)
        _ebss = .;
    } > RAM

    /* Section persistante dans backup SRAM */
    .backup (NOLOAD) : {
        *(.backup_data)
    } > BACKUP
}
```

## Pitfalls

1. **Vector table remap** : SCB->VTOR doit être aligné sur 256 bytes (Cortex-M)
2. **Stack pointer** : Toujours lire le SP depuis le vecteur du firmware — ne pas conserver celui du bootloader
3. **Peripherals state** : Désactiver tous les périphériques avant de sauter au firmware (DMA, timers, IRQ)
4. **Flash wait states** : Adapter les WS à la fréquence avant d'écrire en flash
5. **Hardfault dans le firmware** : Le bootloader doit avoir son propre HardFault_Handler (pas celui du firmware)
6. **Watchdog** : Désactiver IWDG avant de sauter au firmware (ou le firmware doit le gérer)
7. **CRC** : Utiliser un CRC matériel (DMA) pour les gros firmwares — le CRC software est lent
8. **Signature** : La clé publique dans le bootloader rend le bootloader non modifiable — flash protect
9. **Dual bank** : Les deux banques doivent avoir la même taille — bien vérifier les adresses
10. **Rollback counter** : Limiter le nombre de rollbacks (attaque DoS possible)

## Ressources

- STM32 System Memory Bootloader (AN3155, AN2606)
- ESP32 ROM Bootloader : https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/system/ota.html
- i.MX RT ROM Boot (AN12107)
- TF-A (Trusted Firmware-A) : https://www.trustedfirmware.org/
- MCUboot : https://github.com/mcu-tools/mcuboot — bootloader open source pour MCU
- TinyUSB DFU : https://github.com/hathach/tinyusb