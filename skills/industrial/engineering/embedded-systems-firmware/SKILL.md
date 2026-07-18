---
name: embedded-systems-firmware
description: "Développer du firmware pour systèmes embarqués industriels sur microcontrôleurs (STM32, ESP32) en C/C++, configurer les périphériques matériels (HAL, timers, interruptions) et les bus de communication (I2C, SPI, CAN)."
version: 2.0.0
author: Actemium
license: Privée Actemium St-Étienne
platforms: [linux, macos, windows]
metadata:
  helios:
    tags: [embedded, firmware, microcontroller, stm32, esp32, c-plus-plus, spi, i2c, can-bus, rtos, freertos, hal, cmake]
    related_skills: [pcb-design-altium, pid-tuning-control, electrical-schematics-eplan]
---

# Électronique Embarquée et Firmware

## Vue d'ensemble

Cette compétence encadre le développement de **firmware** (logiciel embarqué) pour microcontrôleurs utilisés dans l'industrie et l'IoT, principalement les familles **STM32** (ARM Cortex-M), **ESP32** (Xtensa LX6/LX7) et **AVR** (Arduino). Le firmware s'exécute directement sur le matériel, soit en mode **bare-metal** (boucle principale + interruptions), soit sur un système d'exploitation temps réel (**RTOS — Real-Time Operating System** comme FreeRTOS, Zephyr ou Azure RTOS ThreadX).

Le développement firmware industriel couvre les domaines suivants :

- **Configuration des périphériques** : GPIO, timers (PWM, capture), ADC, DAC, DMA.
- **Communication série** : UART, SPI, I²C, CAN (Controller Area Network), USB, Ethernet.
- **Gestion des entrées/sorties temps réel** : lecture de capteurs analogiques/numériques, commande d'actionneurs (relais, moteurs DC/brushless, vannes proportionnelles).
- **Protocoles industriels** : Modbus RTU (sur RS-485), CANopen, J1939.
- **Sécurité fonctionnelle** : Watchdog matériel (IWDG), chien de garde logiciel (WWDG), CRC sur la mémoire flash, gestion des modes basse consommation.

Un firmware industriel doit respecter des contraintes sévères de **fiabilité** (fonctionnement ininterrompu pendant des années), **déterministe** (respect des échéances temporelles) et **de sécurité fonctionnelle** (IEC 61508, ISO 13849).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :

- Rédiger du code C/C++ pour lire un capteur analogique via l'ADC du microcontrôleur ou commander une sortie numérique via les GPIO.
- Configurer des protocoles de communication matérielle : I²C (capteur de température, accéléromètre), SPI (écran TFT, codeur incrémental), UART (debug, GPS, Modbus RTU), ou **CAN-Bus** (automobile, machines agricoles, industrielles).
- Gérer le traitement d'événements asynchrones via des routines de service d'interruption (ISR) avec un temps de traitement critique.
- Développer une application multitâche temps réel avec synchronisation (sémaphores, files de messages, mutex sous FreeRTOS).
- Résoudre un problème de blocage matériel (HardFault), de débordement de pile (stack overflow), de corruption mémoire (buffer overflow, race condition) ou de consommation excessive.
- Mettre en œuvre un bootloader sécurisé pour les mises à jour firmware à distance (OTA — Over-The-Air).

## Architecture du Firmware : Bare-metal vs RTOS

### 1. Bare-metal (Boucle infinie supervisée par interruptions)

Structure simple pour les applications à faibles ressources et faible complexité. La boucle `while(1)` gère les tâches de fond non critiques, tandis que les interruptions matérielles (IRQ) traitent les événements urgents.

```c
#include "stm32f4xx_hal.h"
#include <stdio.h>

// Drapeau levé par l'interruption externe
volatile uint8_t sensor_data_ready = 0;

/**
 * @brief Callback d'interruption sur front montant GPIO
 *        Déclenché par un capteur connecté à la broche PA0
 */
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_0) {
        sensor_data_ready = 1;   // ← Uniquement un drapeau, pas de traitement lourd
    }
}

/**
 * @brief Fonction d'initialisation du système
 *        Configure l'horloge, les GPIO, l'ADC et l'UART
 */
static void System_Init(void) {
    HAL_Init();                         // Initialisation de la bibliothèque HAL
    SystemClock_Config_HSE_168MHz();    // Horloge système à 168 MHz (STM32F4)

    MX_GPIO_Init();                     // GPIO : PA0 en entrée avec interruption
    MX_ADC1_Init();                     // ADC1 : résolution 12 bits, scan continu
    MX_USART2_UART_Init();              // UART2 : 115200 bauds, 8N1
}

int main(void) {
    System_Init();                      // Initialisations matérielles
    uint16_t adc_value = 0;

    while (1) {
        if (sensor_data_ready) {
            sensor_data_ready = 0;      // Réinitialiser le drapeau

            // Traitement « lourd » (hors interruption)
            HAL_ADC_Start(&hadc1);
            if (HAL_ADC_PollForConversion(&hadc1, 10) == HAL_OK) {
                adc_value = HAL_ADC_GetValue(&hadc1);
            }
            HAL_ADC_Stop(&hadc1);

            // Envoi de la valeur par UART
            char buffer[32];
            snprintf(buffer, sizeof(buffer), "ADC: %u\r\n", adc_value);
            HAL_UART_Transmit(&huart2, (uint8_t*)buffer, strlen(buffer), 100);
        }
    }
}
```

**Avantages** : Simplicité, pas de surcharge de scheduler, prévisible pour les tâches uniques.
**Limites** : Pas de multitâche, difficile à maintenir au-delà d'une certaine complexité.

### 2. RTOS (Multitâche préemptif avec FreeRTOS)

Indispensable dès que le système gère simultanément : affichage graphique (TFT), communication réseau (Wi-Fi/Ethernet TCP/IP), contrôle de moteurs pas-à-pas ou brushless, et acquisition de capteurs. Chaque fonctionnalité s'exécute dans sa propre **tâche** avec pile, priorité et période de scrutation dédiées.

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// File de messages entre les tâches
QueueHandle_t sensor_queue;

/**
 * @brief Tâche d'acquisition : lit le capteur toutes les 10 ms
 */
void vTaskSensorAcquisition(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(10);  // 10 ms

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        uint16_t sensor_value = Read_Sensor_I2C();
        xQueueSend(sensor_queue, &sensor_value, 0);
    }
}

/**
 * @brief Tâche de contrôle : applique l'algorithme PID toutes les 100 ms
 */
void vTaskPIDControl(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(100); // 100 ms
    uint16_t sensor_value;

    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        if (xQueueReceive(sensor_queue, &sensor_value, 0) == pdTRUE) {
            float output = PID_Compute((float)sensor_value);
            Set_Actuator(output);
        }
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_I2C1_Init();

    sensor_queue = xQueueCreate(10, sizeof(uint16_t));

    // Création des tâches avec priorités
    xTaskCreate(vTaskSensorAcquisition, "Sensor", 256, NULL, 2, NULL);
    xTaskCreate(vTaskPIDControl,        "PID",    256, NULL, 1, NULL);

    vTaskStartScheduler();  // Lancement du RTOS

    // Ne devrait jamais arriver
    for (;;);
}
```

**Règles de dimensionnement des piles FreeRTOS** :

| Tâche | Usage | Taille de pile recommandée |
|:---|:---|---:|
| Acquisition (ISR + queue) | Légère | 128-256 mots |
| Contrôle PID | Intermédiaire | 256-512 mots |
| Communication (Wi-Fi, TCP) | Lourde (printf, malloc possible) | 512-1024 mots |
| Affichage TFT | Lourde | 1024-2048 mots |

## Protocoles de Communication Embarqués

### I²C (Inter-Integrated Circuit)

- Bus série synchrone à 2 fils : **SDA** (data) et **SCL** (clock).
- Topologie maître-esclave avec adressage 7 bits (ou 10 bits).
- Résistances de tirage (pull-up) externes $4.7\;k\Omega$ typiques pour la fréquence standard $100\;kHz$.
- Fréquences standard : $100\;kHz$ (Standard), $400\;kHz$ (Fast), $1\;MHz$ (Fast Mode Plus).

**Configuration typique (STM32 HAL)** :

```c
// Adresse du capteur (0x76 pour BMP280)
#define BMP280_ADDR   (0x76 << 1)

uint8_t reg = 0xD0;  // Registre d'identification
uint8_t chip_id;

// Lecture d'un registre I²C
HAL_I2C_Master_Transmit(&hi2c1, BMP280_ADDR, &reg, 1, 100);
HAL_I2C_Master_Receive(&hi2c1, BMP280_ADDR, &chip_id, 1, 100);
```

### SPI (Serial Peripheral Interface)

- Bus série synchrone à 4 fils : **SCLK**, **MOSI**, **MISO**, **CS** (Chip Select).
- Communication full-duplex, rapide (jusqu'à $80\;MHz$ sur STM32).
- Sélection par chip select (SS/CS) : chaque esclave a sa propre ligne CS.

**Configuration typique (STM32 HAL)** :

```c
uint8_t tx_data[2] = {0x0A, 0x00};  // Commande + donnée
uint8_t rx_data[2] = {0};

// Sélection de l'esclave (CS = PA4)
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);

// Échange SPI
HAL_SPI_TransmitReceive(&hspi1, tx_data, rx_data, 2, 100);

// Désélection de l'esclave
HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
```

### CAN-Bus (Controller Area Network)

- Bus différentiel à 2 fils : **CAN_H** et **CAN_L** (terminaison $120\;\Omega$ à chaque extrémité).
- Messages prioritaires par arbitration bitwise ; pas de maître unique.
- Vitesses standard : $125\;kbps$, $250\;kbps$, $500\;kbps$ (standard industriel), $1\;Mbps$.
- Utilisé dans l'automobile (J1939), les machines agricoles (ISOBUS), l'industrie (CANopen).

**Attributs d'un message CAN** :

```c
typedef struct {
    uint32_t id;           // Identifiant 11 bits (standard) ou 29 bits (extended)
    uint8_t  dlc;          // Data Length Code (0 à 8 octets)
    uint8_t  data[8];      // Données utiles
    uint8_t  rtr;          // Remote Transmission Request (0 = data frame)
} CAN_Msg;
```

## Pièges Courants (Common Pitfalls)

1. **Variables partagées non déclarées `volatile` ou non protégées :**
   - *Erreur :* Modifier une variable globale dans une interruption (ISR) et la lire dans la boucle principale sans le mot-clé `volatile`. Le compilateur (qui ne voit pas les chemins d'accès depuis l'ISR) optimise la variable dans un registre CPU et la valeur modifiée par l'ISR n'est jamais relue depuis la RAM.
   - *Correction :* Déclarer toutes les variables partagées entre le code normal et les ISR avec le mot-clé `volatile` (ex : `volatile uint8_t irq_flag`). Pour les variables de taille $> 1$ octet sur un CPU 8 bits (AVR), protéger les accès par des sections critiques (`__disable_irq()` / `__enable_irq()`).

2. **Appel de fonctions bloquantes ou d'allocation dynamique dans une ISR :**
   - *Erreur :* Invoquer `printf()`, `HAL_Delay()`, `malloc()` ou `new()` dans une routine de service d'interruption. Ces fonctions sont bloquantes (attente active ou accès lent à des ressources partagées) et peuvent ne pas être réentrantes. L'ISR fige le CPU et provoque un plantage du type **HardFault**.
   - *Correction :* Une ISR doit être la plus courte possible (quelques dizaines de cycles CPU max). Elle doit uniquement : lever un drapeau (`volatile`), écrire dans une file d'attente (Queue RTOS) ou déclencher une tâche via une notification (Task Notification). Le traitement métier se fait dans la tâche correspondante.

3. **Débordement de pile (Stack Overflow) :**
   - *Erreur :* Allouer une pile trop petite pour une tâche RTOS (par exemple $128$ mots pour une tâche qui utilise `snprintf` et des appels de fonctions profondément imbriqués). La mémoire située après la pile est corrompue, causant des plantages aléatoires difficiles à diagnostiquer.
   - *Correction :* Utiliser l'option de vérification de pile du RTOS (`configCHECK_FOR_STACK_OVERFLOW` dans FreeRTOS). Dimensionner les piles par itération (compter les besoins de la fonction la plus profonde). Ajouter une marge de sécurité de $30\%$ à $50\%$ au résultat de l'estimation.

4. **Pull-up/Pull-down manquants sur les bus I²C et les lignes de remise à zéro :**
   - *Erreur :* Connecter directement les lignes SDA et SCL d'un bus I²C au microcontrôleur sans résistances de tirage externes. Les broches en mode open-drain ne peuvent pas passer à l'état haut, le bus reste à 0 V et aucune communication n'est possible.
   - *Correction :* Vérifier la présence de résistances de tirage (pull-up) sur SDA et SCL, typiquement $4.7\;k\Omega$ pour une horloge de $100\;kHz$. Pour les lignes de reset, le pull-up est conseillé ($10\;k\Omega$ vers $V_{DD}$). Configurer les GPIO internes en mode pull-up si les résistances externes sont absentes.

5. **Watchdog non configuré ou mal rafraîchi :**
   - *Erreur :* Développer un firmware sans activer le watchdog matériel (IWDG). En cas de boucle infinie non traitée ou de blocage du CPU (débordement de pile, accès mémoire invalide), le système reste figé indéfiniment sans reprise, ce qui est inacceptable dans un contexte industriel.
   - *Correction :* Activer le watchdog indépendant (IWDG) avec un délai de $T_{IWDG} \approx 2 \times T_{cycle\_max}$ où $T_{cycle\_max}$ est le temps du cycle principal le plus long. Rafraîchir le watchdog à un endroit unique de la boucle principale (ou une tâche watchdog dédiée). Ne jamais rafraîchir le watchdog dans une ISR (cela masquerait le blocage de la boucle principale).

6. **Accès concurrents non protégés (Race Conditions) :**
   - *Erreur :* Deux tâches FreeRTOS écrivent dans la même variable ou structure sans mutex ni section critique. La valeur finale est indéterministe (dépend du séquencement du scheduler).
   - *Correction :* Utiliser un **mutex** (`xSemaphoreCreateMutex()`) pour protéger les ressources partagées. Pour les transferts de données entre tâches, préférer une **file d'attente** (`xQueueCreate()`), qui offre une synchronisation intégrée.

## Liste de vérification (Checklist)

- [ ] Les variables partagées entre les interruptions et le programme principal sont déclarées `volatile` et protégées contre les accès concurrents.
- [ ] Aucune fonction d'attente active (`delay`, `HAL_Delay`) ou d'allocation dynamique (`malloc`, `new`) n'est appelée dans les routines d'interruption (ISR).
- [ ] La taille des piles (stack sizes) de chaque tâche RTOS a été dimensionnée avec une marge ($30\%$ à $50\%$) pour éviter les dépassements (Stack Overflow).
- [ ] La vérification de débordement de pile du RTOS est activée (`configCHECK_FOR_STACK_OVERFLOW = 1`).
- [ ] Les résistances de tirage (Pull-up) sont présentes matériellement ou configurées en interne pour les bus I²C (SDA/SCL) et les lignes de reset.
- [ ] Un Watchdog matériel (IWDG) est configuré et rafraîchi à un emplacement unique dans la boucle principale (pas dans une ISR).
- [ ] Les accès aux ressources partagées entre tâches (mutex, queue, sémaphore) sont correctement implémentés sans race condition.
- [ ] Le protocole de communication (UART, SPI, I²C, CAN) est configuré avec les bons paramètres physique (vitesse, polarité, phase, terminaison).
- [ ] Les erreurs de communication sont gérées par une machine d'état avec temporisation (timeout) et reprise (retry).
- [ ] La consommation mémoire (Flash ROM utilisée, RAM utilisée) a été vérifiée à la compilation et ne dépasse pas les capacités du microcontrôleur cible.

