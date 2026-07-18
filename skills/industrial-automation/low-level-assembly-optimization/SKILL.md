---
name: low-level-assembly-optimization
description: "Rétro-ingénierie et optimisation de firmware en assembleur."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
metadata:
  EVA:
    maturity: pilot
    tags: [assembly, embedded, reverse-engineering, optimization, arm, x86, edge-mcu]
    related_skills: [siemens-scl-expert, industrial-ai-pipeline]
---

# Assembleur Bas Niveau : Optimisation et Rétro-Ingénierie Industrielle

## Rôle et Identité
Vous êtes un ingénieur principal en systèmes embarqués et un expert en rétro-ingénierie de micrologiciels (firmwares) industriels. Votre rôle est d'écrire, d'analyser et d'optimiser du code en langage assembleur (ARM Cortex-M, x86/x64, RISC-V) pour des applications industrielles critiques (acquisition haute vitesse, drivers temps réel) et de reconstruire le comportement de systèmes existants (legacy) dont le code source a été perdu.

## Vue d'ensemble
L'utilisation de l'assembleur dans l'industrie moderne répond à trois besoins critiques :
1.  **Optimisation de performance extrême** : Contrôle précis des cycles d'horloge pour l'acquisition de signaux physiques à haute fréquence.
2.  **Rétro-ingénierie (Reverse Engineering)** : Audit et maintenance de processeurs obsolètes ou d'automates propriétaires dont les codes sources originaux ne sont plus disponibles.
3.  **Garantie de déterminisme** : Éviter les variations imprévisibles d'optimisation introduites par les compilateurs C/C++ dans les boucles de sécurité SIL.

---

## 1. Architecture Mémoire d'un Système Embarqué Industriel

```
┌───────────────────────────────────────────────────────────┐
│                    Carte Mémoire Système                  │
├───────────────────────────────────────────────────────────┤
│ 0x0000_0000 ──► Table des vecteurs (VTR)                  │
│ 0x0800_0000 ──► Mémoire Flash (Code, Constantes)          │
│ 0x2000_0000 ──► SRAM (Variables, Stack / Tas)             │
│ 0x4000_0000 ──► Registres Périphériques (MMIO - Vannes,   │
│                 Timers, ADC)                              │
└───────────────────────────────────────────────────────────┘
```

---

## 2. Code de Référence : Assembleur ARM Cortex-M (Thumb-2)

Ce bloc calcule une moyenne glissante filtrée sur des mesures de capteurs directement en registres pour un microcontrôleur d'acquisition Edge.

```assembly
/*
 * Fonction : filter_sensor_samples
 * Entrée : R0 = adresse du tableau de mesures (32-bit float)
 *          R1 = nombre d'éléments (N)
 * Sortie : S0 = moyenne filtrée (float)
 */
    .syntax unified
    .cpu cortex-m4
    .thumb
    .section .text.filter_sensor_samples, "ax", %progbits
    .align 2
    .global filter_sensor_samples
    .type filter_sensor_samples, %function

filter_sensor_samples:
    .fnstart
    PUSH    {R4, LR}            @ Sauvegarder les registres préservés sur la pile
    VSUB.F32 S0, S0, S0         @ Initialiser l'accumulateur (S0 = 0.0)
    CBZ     R1, end_loop        @ Si N == 0, quitter immédiatement
    MOV     R4, R1              @ R4 = compteur de boucle

loop:
    VLDR.F32 S1, [R0], #4       @ Charger la mesure et incrémenter le pointeur R0
    VADD.F32 S0, S0, S1         @ S0 = S0 + S1
    SUBS    R4, R4, #1          @ Décrémenter le compteur et mettre à jour les flags
    BNE     loop                @ Boucler si R4 != 0 (Z flag non mis)

    @ Calculer la division par N (conversion de type requise)
    VMOV    S1, R1              @ Transférer N du registre CPU vers registre FPU
    VCVT.F32.S32 S1, S1         @ Convertir N (entier signé) en float dans S1
    VDIV.F32 S0, S0, S1         @ S0 = Somme / N

end_loop:
    POP     {R4, PC}            @ Restaurer les registres et retourner
    .fnend
```

---

## 3. Code de Référence : Assembleur C Inline (x86/x64)

Ce code s'insère dans un driver C/C++ pour interroger directement les ports d'E/S de cartes d'acquisition industrielles avec une latence minimale.

```c
#include <stdint.h>

// Lecture asynchrone ultra-rapide sur port d'E/S (PCI/ISA)
uint16_t read_io_port_fast(uint16_t port_address) {
    uint16_t data;
    
    // Assembleur inline avec syntaxe GCC/Clang (Volatile évite l'optimisation par le compilateur)
    __asm__ __volatile__(
        "inw %1, %0"        // Commande d'entrée d'un mot (16 bits) du port (%1) vers data (%0)
        : "=a"(data)        // Output : registre AX ('a') écrit dans data
        : "d"(port_address) // Input : registre DX ('d') chargé avec la valeur port_address
        : "memory"          // Clobber : signale que la mémoire a été modifiée
    );
    
    return data;
}
```

---

## 4. Rétro-Ingénierie de Code Assembleur (Analyse Comparative)

Lors de l'analyse d'un binaire désassemblé (via IDA Pro ou Ghidra), vous devez être capable de reconstruire la logique de haut niveau à partir des instructions brutes.

### Exemple de conversion : De l'Assembleur x86-64 vers le C d'Origine

**Code Assembleur Brut (désassemblé) :**
```assembly
xor eax, eax
.L2:
movsx rdx, eax
mov ecx, DWORD PTR [rdi+rdx*4]
test ecx, ecx
js .L3
add eax, 1
cmp eax, esi
jl .L2
```

**Analyse de Reconstruction :**
1.  `xor eax, eax` : Initialise le registre index `i = 0`.
2.  `movsx rdx, eax` et `[rdi+rdx*4]` : Charge l'élément d'index `i` du tableau d'entiers pointé par `RDI` (le registre d'argument `array`).
3.  `test ecx, ecx` et `js .L3` : Teste si la valeur chargée est négative (flag de signe `S` activé → saut vers `.L3` en cas d'erreur ou d'arrêt).
4.  `add eax, 1` et `cmp eax, esi` : Incrémente `i` et compare avec la taille `N` stockée dans `ESI`.

**Code C Reconstruit correspondant :**
```c
int find_first_negative(int *array, int size) {
    for (int i = 0; i < size; i++) {
        if (array[i] < 0) {
            return i; // Correspond à la cible du saut .L3
        }
    }
    return -1;
}
```

---

## 5. Spécifications des Conventions d'Appel (ABI)

Pour écrire de l'assembleur compatible avec du code C compilé, vous devez respecter scrupuleusement l'ABI de la plateforme cible.

| Architecture / OS | Registres d'Arguments | Registres à Préserver (Callee-saved) | Registre de Retour |
|---|---|---|---|
| **ARM AAPCS (32-bit)** | `R0, R1, R2, R3` | `R4, R5, R6, R7, R8, R9, R10, R11` | `R0` (ou `S0` pour float) |
| **x86-64 System V (Linux)** | `RDI, RSI, RDX, RCX, R8, R9` | `RBX, RSP, RBP, R12, R13, R14, R15` | `RAX` |
| **x86-64 Windows** | `RCX, RDX, R8, R9` | `RBX, RSI, RDI, RBP, RSP, R12, R13, R14, R15` | `RAX` |

---

## 6. Pièges Courants (Common Pitfalls)
*   **Trashing de Registres (Register Corruption)** : Écrire dans des registres volatils (comme R0-R3 sous ARM) sans respecter la convention d'appel (ABI), corrompant ainsi le code appelant.
*   **Problème d'alignement mémoire** : Effectuer des accès mémoire non alignés (ex: charger un mot 32 bits à une adresse impaire), ce qui provoque un crash immédiat (HardFault) sur la plupart des processeurs embarqués industriels.
*   **Ignorer la cohérence du cache** : Modifier du code à la volée en RAM sans vider le cache d'instructions (Instruction Cache Sync), provoquant une exécution de l'ancien code.
*   **Lack of volatile in compilers** : Omettre la clause `volatile` dans l'assembleur inline C, ce qui autorise le compilateur à optimiser et potentiellement supprimer vos accès matériels directs.

---

## 7. Liste de vérification (Checklist)
- [ ] Identifier l'architecture du processeur cible (ARM, x86, RISC-V, 8051, 68k).
- [ ] Valider le respect des conventions d'appel de l'ABI cible pour le passage d'arguments.
- [ ] Sauvegarder et restaurer systématiquement tous les registres non-volatils sur la pile (`PUSH`/`POP`).
- [ ] Utiliser des accès mémoire alignés sur la taille des données (16/32/64 bits).
- [ ] Documenter les adresses d'E/S physiques (MMIO) accédées par le code.
