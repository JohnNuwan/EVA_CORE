---
name: "freertos-rtos"
description: "FreeRTOS — gestion des tâches, files, sémaphores, timers, scheduling, ports ARM/RISC-V"
category: "edge-ai"
author: "E.V.A"
version: "1.0.0"
---

# FreeRTOS — Système d'Exploitation Temps Réel Embarqué

## Vue d'ensemble

FreeRTOS est le RTOS open-source le plus déployé au monde sur MCU. Kernel ~6-12 KB, préemptif, priorités fixes, 100% C. Ce guide couvre la configuration avancée, les patterns de synchronisation, l'optimisation mémoire et les ports ARM/RISC-V.

## Architecture du Noyau

### Composants principaux

```
FreeRTOS Kernel
├── Tâches (Task) — threads coopératifs/préemptifs
│   ├── États : Ready, Running, Blocked, Suspended
│   └── Context switch via PendSV (ARM) / Machine SWI (RISC-V)
├── Synchronisation
│   ├── Queue — FIFO générique, ISR-safe
│   ├── Semaphore — binaire, compteur, mutex (avec inheritance)
│   └── Event Group — 24 bits de flags
├── Timers
│   └── Software Timer — callback, auto-reload ou one-shot
├── Memory Management
│   └── heap_1..heap_5 — stratégies d'allocation
└── Ports — 40+ architectures (ARM, RISC-V, AVR, PIC, TriCore)
```

### Configuration (FreeRTOSConfig.h)

```c
/* Paramètres critiques — impacter taille kernel et comportement */
#define configUSE_PREEMPTION           1      // Préemptif (1) ou coopératif (0)
#define configUSE_TIME_SLICING         1      // Round-robin même priorité
#define configUSE_TICKLESS_IDLE        0      // Tick suppression en idle (power)
#define configCPU_CLOCK_HZ             ((unsigned long) 168000000)
#define configTICK_RATE_HZ             ((TickType_t) 1000)  // 1ms tick
#define configMAX_PRIORITIES           5      // 0..4 (5 niveaux)
#define configMINIMAL_STACK_SIZE       ((unsigned short) 128)  // Words
#define configTOTAL_HEAP_SIZE          ((size_t) (64 * 1024))  // 64KB

/* Hooks */
#define configUSE_IDLE_HOOK            1
#define configUSE_TICK_HOOK            0
#define configUSE_MALLOC_FAILED_HOOK   1
#define configCHECK_FOR_STACK_OVERFLOW 2      // Méthode 2 (registre + pattern)

/* Tracing et assert */
#define configUSE_TRACE_FACILITY       1
#define configUSE_STATS_FORMATTING_FUNCTIONS 1
#define configASSERT(x) if(!(x)) { taskDISABLE_INTERRUPTS(); while(1); }
```

## Gestion des Tâches

### Création

```c
// Stack allouée statiquement (recommandé — pas de heap fragment)
StackType_t task_stack[256];
StaticTask_t task_buf;

void vTaskFunction(void *pvParameters) {
    while(1) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

TaskHandle_t xTask = xTaskCreateStatic(
    vTaskFunction, "TaskName",
    256,           // stack size (words)
    NULL,          // parameters
    3,             // priority (0=idle, configMAX_PRIORITIES-1=max)
    task_stack,    // stack buffer
    &task_buf      // task control block
);

// Ou dynamique
xTaskCreate(vTaskFunction, "TaskName", 256, NULL, 3, NULL);
```

### Transitions d'état

```
        ┌──────────┐
        │  Running │ ←── Sélectionné par le scheduler
        └────┬─────┘
             │ Preempted (tick IRQ, priorité plus haute prête)
     ┌───────┴───────┐
     │               │
┌────▼────┐   ┌──────▼───────┐
│  Ready  │   │   Blocked    │ ← vTaskDelay, queue pend, sem pend
└────▲────┘   └──────▲───────┘
     │               │ vTaskResume / Timeout / Data available
     └───────────────┘
```

### Priorités et Inheritance

```c
// Priority Inheritance (Mutex uniquement — pas Semaphore)
// Évite l'inversion de priorité : une tâche basse priorité emprunte
// temporairement la priorité haute quand elle tient un mutex convoité

// Exemple d'inversion (sans inheritance) :
// Tâche H (prio 3) attend mutex → Tâche L (prio 1) tient mutex
// → Tâche M (prio 2) préempte L → H bloque sur L → mais L ne tourne pas !
// Mutex fixe ça : L emprunte prio 3 → M ne préempte plus → L libère vite
```

### Idle Hook et Stack Overflow

```c
void vApplicationIdleHook(void) {
    // Tourne quand aucune tâche n'est prête
    // NE PAS bloquer ici — pas de yield possible
    // Patterns : WFI (ARM) pour basse conso, debug counters
    __asm volatile("WFI");  // Attendre interruption
}

void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    (void) pcTaskName;
    // Méthode 2 : compare pattern 0xa5a5a5a5 sur la stack
    // Si corrompu → overflow
    taskDISABLE_INTERRUPTS();
    while(1);
}
```

## Queues (Files de messages)

### Création et Usage

```c
// Création
QueueHandle_t xQueue = xQueueCreate(10, sizeof(struct DataPacket));

// Envoi (depuis tâche)
struct DataPacket pkt = {.id = 42, .value = 3.14f};
xQueueSend(xQueue, &pkt, pdMS_TO_TICKS(100));

// Envoi (depuis ISR — NE PAS BLOQUER)
BaseType_t xHigherPriorityTaskWoken = pdFALSE;
xQueueSendFromISR(xQueue, &pkt, &xHigherPriorityTaskWoken);
portYIELD_FROM_ISR(xHigherPriorityTaskWoken);

// Réception
struct DataPacket rx;
if (xQueueReceive(xQueue, &rx, portMAX_DELAY) == pdPASS) {
    process_packet(&rx);
}

// Interrogation : uxQueueMessagesWaiting(), uxQueueSpacesAvailable()
```

### Queue Set (Plusieurs files)

```c
// Attendre sur plusieurs files simultanément
QueueSetHandle_t xSet = xQueueCreateSet(5);  // 5 queues max

// Ajouter des files
xQueueAddToSet(xUART_Queue, xSet);
xQueueAddToSet(xCAN_Queue, xSet);
xQueueAddToSet(xButton_Queue, xSet);

// Attendre sur le set
QueueSetMemberHandle_t xMember;
xMember = xQueueSelectFromSet(xSet, portMAX_DELAY);
// Identifier quelle file a reçu
if (xMember == xUART_Queue) {
    xQueueReceive(xUART_Queue, &data, 0);
} else if (xMember == xCAN_Queue) { ... }
```

## Sémaphores

### Binaire

```c
// Création
SemaphoreHandle_t xSem = xSemaphoreCreateBinary();

// Donner (signal — depuis ISR aussi)
xSemaphoreGiveFromISR(xSem, &xHigherPriorityTaskWoken);

// Prendre (attendre)
xSemaphoreTake(xSem, pdMS_TO_TICKS(1000));  // timeout 1s
```

### Compteur

```c
// Compteur avec max=10, initial=3
SemaphoreHandle_t xCountSem = xSemaphoreCreateCounting(10, 3);

// Patterns : pool d'objets, compteur d'événements
```

### Mutex (avec Priority Inheritance)

```c
// Toujours utiliser Mutex (pas binaire) pour exclusion mutuelle
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();

xSemaphoreTake(xMutex, portMAX_DELAY);
// Section critique
xSemaphoreGive(xMutex);

// Recursive Mutex (même tâche peut prendre N fois)
SemaphoreHandle_t xRecMutex = xSemaphoreCreateRecursiveMutex();
xSemaphoreTakeRecursive(xRecMutex, portMAX_DELAY);
xSemaphoreGiveRecursive(xRecMutex);
```

### Deadlock Prevention

```c
// RÈGLE : toujours prendre les mutex dans le même ordre
// OU utiliser xSemaphoreTake avec timeout (pas portMAX_DELAY)

// Exemple safe :
void safe_transfer(SemaphoreHandle_t m1, SemaphoreHandle_t m2) {
    // Tenter en séquence avec timeout
    if (xSemaphoreTake(m1, pdMS_TO_TICKS(100)) == pdTRUE) {
        if (xSemaphoreTake(m2, pdMS_TO_TICKS(100)) == pdTRUE) {
            // Transfert
            xSemaphoreGive(m2);
        }
        xSemaphoreGive(m1);
    }
    // Si deuxième échoue, premier est relâché proprement
}
```

## Event Groups

```c
// 24 bits indépendants (bits 0-23)
EventGroupHandle_t xEG = xEventGroupCreate();

// Dans ISR ou tâche :
xEventGroupSetBits(xEG, BIT_0 | BIT_3);  // Set bits 0 et 3

// Dans tâche qui attend :
EventBits_t bits = xEventGroupWaitBits(
    xEG,
    BIT_0 | BIT_3,          // Bits à tester
    pdTRUE,                  // Clear on exit
    pdTRUE,                  // Wait for ALL (pdFALSE = any)
    pdMS_TO_TICKS(1000)     // Timeout
);
```

## Software Timers

```c
// Périphérique : timer software, callback dans contexte de timer (pas tâche !)
// Précision : configTICK_RATE_HZ (souvent 1ms)

TimerHandle_t xTimer = xTimerCreate(
    "LED",                    // Name
    pdMS_TO_TICKS(500),       // Period
    pdTRUE,                   // Auto-reload
    NULL,                     // ID
    vTimerCallback            // Callback
);

void vTimerCallback(TimerHandle_t xTimer) {
    // NE PAS bloquer — appelé dans le contexte du timer daemon
    // Utiliser queue pour passer à une tâche si nécessaire
    toggle_LED();
}

xTimerStart(xTimer, 0);  // Lancer

// Initier depuis ISR : xTimerResetFromISR, xTimerStartFromISR
```

## Gestion Mémoire

### Stratégies heap (heap_1..heap_5)

| Stratégie | Allocation | Free | Fragmentation | Cas d'usage |
|-----------|-----------|------|---------------|-------------|
| **heap_1** | Simple array | NON | N/A | Sécurité critique, pas de delete |
| **heap_2** | Best-fit list | OUI | OUI | Anciens projets |
| **heap_3** | malloc/free (newlib) | OUI | Selon libc | Avec OS complet |
| **heap_4** | Best-fit + coalesce | OUI | NON | **Recommandé** général |
| **heap_5** | heap_4 + régions non-contiguës | OUI | NON | RAM externe + interne |

```c
// heap_4 : configTOTAL_HEAP_SIZE dans FreeRTOSConfig.h
// Voir le taux d'utilisation :
UBaseType_t free_bytes = xPortGetFreeHeapSize();
UBaseType_t min_free = xPortGetMinimumEverFreeHeapSize();
printf("Heap used: %d bytes\n", configTOTAL_HEAP_SIZE - free_bytes);
```

### Allocation Statique (recommandé critique)

```c
// Activer :
#define configSUPPORT_STATIC_ALLOCATION  1
#define configSUPPORT_DYNAMIC_ALLOCATION 0

// Fournir ces callbacks :
void vApplicationGetIdleTaskMemory(StaticTask_t **ppxIdleTaskTCBBuffer,
    StackType_t **ppxIdleTaskStackBuffer, uint32_t *pulIdleTaskStackSize)
{
    static StaticTask_t xIdleTaskTCB;
    static StackType_t uxIdleTaskStack[configMINIMAL_STACK_SIZE];
    *ppxIdleTaskTCBBuffer = &xIdleTaskTCB;
    *ppxIdleTaskStackBuffer = uxIdleTaskStack;
    *pulIdleTaskStackSize = configMINIMAL_STACK_SIZE;
}
```

## Task Notifications (ultra-rapide)

```c
// Chaque tâche a 32-bit notification (plus rapide que queue/semaphore)
// Utiliser comme semaphore/event group léger

// Tâche productrice :
xTaskNotifyGive(xTaskConsumer);  // Incrémente la notification
// Ou :
xTaskNotify(xTaskConsumer, BIT_0, eSetBits);

// Tâche consommatrice :
ulTaskNotifyTake(pdTRUE, portMAX_DELAY);  // Wait for notification

// Ou valeur complète :
uint32_t ulValue;
xTaskNotifyWait(0x00, ULONG_MAX, &ulValue, portMAX_DELAY);
```

## Port ARM Cortex-M

### Context Switch via PendSV

```asm
; PendSV_Handler — context switch (appelé par yield ou tick IRQ)
; Sauvegarde/Restaure R4-R11, PSP
__asm void xPortPendSVHandler(void) {
    mrs r0, psp
    isb

    ldr r3, =pxCurrentTCB
    ldr r2, [r3]

    stmdb r0!, {r4-r11}     ; Sauvegarder R4-R11
    str r0, [r2]            ; pxCurrentTCB->pxTopOfStack = PSP

    stmdb sp!, {r3, r14}
    mov r0, #configMAX_SYSCALL_INTERRUPT_PRIORITY
    msr basepri, r0
    dsb
    isb
    bl vTaskSwitchContext
    mov r0, #0
    msr basepri, r0
    ldmia sp!, {r3, r14}

    ldr r1, [r3]
    ldr r0, [r1]            ; Nouveau pxTopOfStack
    ldmia r0!, {r4-r11}     ; Restaurer R4-R11
    msr psp, r0
    isb
    bx r14
}
```

### Critical Sections

```c
/* BASEPRI — masque les interruptions de priorité < configMAX_SYSCALL */
#define taskENTER_CRITICAL()       portDISABLE_INTERRUPTS()
#define taskEXIT_CRITICAL()        portENABLE_INTERRUPTS()

// Usage minimum — sur ARM, peut désactiver NMI si trop agressif
// Préférer les mutex aux sections critiques longues
```

## Port RISC-V

### Machine-mode trap handler

```assembly
.section .text
.globl trap_handler
.type trap_handler, @function

.align 6  # MTVEC aligné 64 bytes
trap_handler:
    # Sauvegarder contexte
    addi sp, sp, -32*4
    sw x1, 1*4(sp)   # ra
    sw x5, 5*4(sp)   # t0
    # ... sauvegarder tous les registres (x1-x31)

    # Lire MCAUSE pour identifier la source
    csrr t0, mcause
    li t1, 0x80000000
    and t1, t0, t1     # Bit d'interruption
    beqz t1, 1f        # Exception (pas d'interruption)

    # Interruption — appeler vPortSysTickHandler
    csrr a0, mepc
    call xPortSysTickHandler
    j 2f

1:  # Exception
    call vApplicationExceptionHandler

2:  # Restaurer contexte
    lw x1, 1*4(sp)
    # ... restaurer tous les registres
    addi sp, sp, 32*4
    mret
```

## Profiling et Debug

```c
// Activer run-time stats :
#define configUSE_TRACE_FACILITY 1
#define configUSE_STATS_FORMATTING_FUNCTIONS 1
#define configGENERATE_RUN_TIME_STATS 1

// Fournir compteur haute résolution
void configureTimerForRunTimeStats(void) {
    TIM2->PSC = 0;           // Pas de prescaler
    TIM2->ARR = 0xFFFF;
    TIM2->CR1 |= TIM_CR1_CEN;
}
unsigned long getRunTimeCounterValue(void) {
    return TIM2->CNT;
}

// Afficher les stats :
TaskStatus_t *pxTaskStatusArray = pvPortMalloc(
    uxTaskGetNumberOfTasks() * sizeof(TaskStatus_t)
);
UBaseType_t uxArraySize = uxTaskGetSystemState(
    pxTaskStatusArray, uxTaskGetNumberOfTasks(), NULL
);
// Afficher pour chaque tâche : pcTaskName, uxCurrentPriority,
// eCurrentState, ulRunTimeCounter
```

## Trace (SEGGER SystemView / Percepio)

```c
// Activer configUSE_TRACE_FACILITY dans FreeRTOSConfig.h
// Ajouter TraceRecorder enregistrements (TRC_Software_*)
// ou les macros natives :
traceTASK_SWITCHED_IN();
vTraceSetQueueName(xQueue, "UART_TX");
vTracePrint(1, "State machine enter RUN");
```

## Pitfalls

1. **Stack overflow** : configCHECK_FOR_STACK_OVERFLOW=2 (registre), mais utiliser aussi des patterns (0xa5a5a5a5)
2. **ISR blocking** : Jamais `xSemaphoreTake()` ou `xQueueReceive()` avec timeout > 0 dans une ISR
3. **Priorité ISR ARM** : configMAX_SYSCALL_INTERRUPT_PRIORITY = éviter de masquer des NMI
4. **Tickless idle** : Le timer doit être configurable pour one-shot — vérifier le port
5. **Mutex vs Semaphore** : Mutex a inheritance — utiliser pour exclusion ; Semaphore pour signalisation
6. **Task notification overflow** : Un appel sans consume peut saturer (max 1 notification)
7. **heap_4 fragmentation** : Malgré coalesce, allocations de tailles très diverses fragmentent
8. **FreeRTOS+TCP** : Nécessite configIP_TASK_STACK_SIZE ~512+ pour TCP stack

## Ressources

- Documentation officielle FreeRTOS : https://www.freertos.org/Documentation/RTOS_book.html
- FreeRTOS Kernel : https://github.com/FreeRTOS/FreeRTOS-Kernel
- Trace Recorder : https://github.com/FreeRTOS/FreeRTOS-Plus-Trace
- SEGGER SystemView : https://www.segger.com/products/development-tools/systemview/
- Percepio Tracealyzer : https://percepio.com/tracealyzer/