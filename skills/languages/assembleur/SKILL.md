---
name: assembleur
description: Guide complet de l'assembleur (x86-64, ARM, RISC-V) — registres, instructions, conventions d'appel, optimisation, reverse engineering. En français.

---

# Assembleur — Guide Complet (Français)

Programmation bas niveau x86-64, ARM64 et RISC-V. Syntaxes Intel et AT&T.

---

## 1. Architecture x86-64

### Registres

```
Registres 64 bits (RAX, RBX, ...) :
┌─────────────────────────────────────────┐
│ RAX  ┌─────────────────┐                │
│      │       EAX       ┌──────┐         │
│      │                 │  AX  ┌───┐     │
│      │                 │      │AL │     │
└─────────────────────────────────────────┘
  64b         32b          16b   8b (low)

Registres généraux (x86-64) :
RAX  - Accumulateur / valeur de retour
RBX  - Base (préservé)
RCX  - Compteur (4e argument)
RDX  - Données (3e argument)
RSI  - Source index (2e argument)
RDI  - Destination index (1er argument)
RBP  - Base pointer (frame)
RSP  - Stack pointer
R8-R15 - Registres supplémentaires

Registres spéciaux :
RIP  - Instruction pointer
RFLAGS - Flags (ZF, SF, CF, OF, PF)
```

### Conventions d'appel (System V AMD64 ABI)

```
Arguments : RDI, RSI, RDX, RCX, R8, R9, puis pile
Retour    : RAX (et RDX pour 128 bits)
Préservés : RBX, RBP, R12-R15
Volatils  : RAX, RCX, RDX, RSI, RDI, R8-R11
```

---

## 2. Instructions x86-64 Essentielles

### Mouvement de données

```asm
; MOV : copier
mov rax, rbx         ; RAX = RBX
mov rax, [rbx]       ; RAX = *RBX (charger de la mémoire)
mov [rbx], rax       ; *RBX = RAX (écrire en mémoire)
mov rax, 42          ; RAX = 42 (immédiat)

; LEA : charger adresse effective (sans déréférencement)
lea rax, [rbx + rcx*4 + 8]  ; RAX = RBX + RCX*4 + 8 (calcul d'adresse)

; PUSH / POP
push rax             ; RSP -= 8; *RSP = RAX
pop rax              ; RAX = *RSP; RSP += 8

; MOVSX / MOVZX : extension de signe / zéro
movsx rax, al        ; Étendre AL (8 bits signé) en RAX
movzx rax, al        ; Étendre AL (8 bits) en RAX (zéro)
```

### Arithmétique

```asm
; ADD / SUB
add rax, rbx         ; RAX += RBX
sub rax, 10          ; RAX -= 10

; INC / DEC
inc rax              ; RAX++
dec rbx              ; RBX--

; MUL / IMUL
mul rbx              ; RDX:RAX = RAX * RBX (non signé)
imul rax, rbx        ; RAX *= RBX (signé)
imul rax, rbx, 10    ; RAX = RBX * 10 (3 opérandes)

; DIV / IDIV
div rbx              ; RAX = RDX:RAX / RBX, RDX = reste (non signé)
idiv rcx             ; Division signée

; NEG / NOT
neg rax              ; RAX = -RAX
not rax              ; RAX = ~RAX (complément à 1)
```

### Logique et Décalage

```asm
; AND / OR / XOR / TEST
and rax, rbx         ; RAX &= RBX
or  rax, 0xFF        ; RAX |= 0xFF
xor rax, rax         ; RAX = 0 (optimisation : plus rapide que mov rax, 0)
test rax, rax        ; RAX & RAX (met les flags, jette le résultat)

; SHL / SHR / SAR
shl rax, 1           ; RAX <<= 1 (décalage logique gauche)
shr rax, cl          ; RAX >>= CL (décalage logique droite)
sar rax, cl          ; RAX >>= CL (décalage arithmétique droite)
```

### Contrôle de Flux

```asm
; CMP : comparer (fait SUB mais jette le résultat)
cmp rax, 10          ; Met les flags en fonction de RAX - 10

; Sauts conditionnels (après CMP)
je  etiquette        ; Jump if Equal         (ZF=1)
jne etiquette        ; Jump if Not Equal     (ZF=0)
jg  etiquette        ; Jump if Greater       (signé, ZF=0 et SF=OF)
jge etiquette        ; Jump if Greater/Equal (signé, SF=OF)
jl  etiquette        ; Jump if Less          (signé, SF≠OF)
jle etiquette        ; Jump if Less/Equal    (signé, ZF=1 ou SF≠OF)
ja  etiquette        ; Jump if Above         (non signé, CF=0 et ZF=0)
jb  etiquette        ; Jump if Below         (non signé, CF=1)

; JMP (inconditionnel)
jmp etiquette

; CALL / RET
call fonction        ; PUSH RIP; JMP fonction
ret                  ; POP RIP

; LOOP
mov rcx, 10
boucle:
    ; corps
    loop boucle       ; RCX--; si RCX ≠ 0 → boucle
```

---

## 3. Fonctions et Pile

```asm
section .text
global ma_fonction

ma_fonction:
    ; Prologue
    push rbp           ; Sauvegarder frame pointer
    mov rbp, rsp       ; Nouveau frame pointer
    sub rsp, 16        ; Réserver 16 octets pour variables locales
    
    ; RDI = 1er argument, RSI = 2e argument
    mov [rbp-8], rdi   ; Variable locale 1
    mov [rbp-4], esi   ; Variable locale 2 (32 bits)
    
    ; Corps de la fonction
    mov eax, [rbp-8]
    add eax, [rbp-4]
    
    ; Épilogue
    mov rsp, rbp       ; Restaurer stack pointer
    pop rbp            ; Restaurer frame pointer
    ret                ; Retour (RAX = valeur de retour)
```

---

## 4. Assembly Inline (GCC)

```c
// Assembly inline dans du C
int additionner(int a, int b) {
    int resultat;
    __asm__ __volatile__(
        "addl %%ebx, %%eax"
        : "=a" (resultat)       // Sorties : resultat dans EAX
        : "a" (a), "b" (b)      // Entrées : a dans EAX, b dans EBX
        :                       // Registres modifiés (aucun ici)
    );
    return resultat;
}

// CPUID (instruction spéciale)
void obtenir_cpuid(int code, unsigned int *a, unsigned int *b,
                   unsigned int *c, unsigned int *d) {
    __asm__ __volatile__(
        "cpuid"
        : "=a"(*a), "=b"(*b), "=c"(*c), "=d"(*d)
        : "a"(code)
    );
}
```

---

## 5. ARM64 (AArch64)

### Registres ARM64

```
X0-X30   - Registres généraux 64 bits
W0-W30   - Moitiés basses 32 bits
SP       - Stack pointer
PC       - Program counter
LR (X30) - Link register (adresse de retour)
FP (X29) - Frame pointer
XZR/WZR  - Zero register (toujours 0)

Convention d'appel ARM64 :
Arguments : X0-X7, puis pile
Retour    : X0 (et X1 pour 128 bits)
Préservés : X19-X29
```

### Instructions ARM64

```asm
; Mouvement
mov x0, x1           ; X0 = X1
mov x0, #42          ; X0 = 42 (immédiat)
ldr x0, [x1]         ; X0 = *X1 (charger)
str x0, [x1]         ; *X1 = X0 (stocker)
ldr x0, [x1, #8]     ; X0 = *(X1 + 8)

; Arithmétique
add x0, x1, x2       ; X0 = X1 + X2
sub x0, x1, x2       ; X0 = X1 - X2
mul x0, x1, x2       ; X0 = X1 * X2
udiv x0, x1, x2      ; X0 = X1 / X2 (non signé)

; Logique
and x0, x1, x2
orr x0, x1, x2
eor x0, x1, x2       ; XOR

; Comparaison et branchement
cmp x0, #10
b.eq etiquette       ; Branch if equal
b.ne etiquette       ; Branch if not equal
b.gt etiquette       ; Branch if greater than (signé)
b.lt etiquette       ; Branch if less than

; Fonction
stp x29, x30, [sp, #-16]!  ; Sauver FP et LR
mov x29, sp                 ; Nouveau frame
add x0, x0, x1              ; Corps
ldp x29, x30, [sp], #16     ; Restaurer
ret
```

---

## 6. RISC-V

```asm
# Registres RISC-V (RV64)
# x0 = zéro, x1 = ra, x2 = sp, x3 = gp
# x5-x7, x28-x31 = temporaires
# x8, x9, x18-x27 = sauvegardés
# x10-x17 = arguments

# Arithmétique
add  t0, t1, t2    # t0 = t1 + t2
sub  t0, t1, t2
addi t0, t1, 42    # t0 = t1 + immédiat

# Chargement / Stockage
lw   t0, 0(sp)     # Load word (32 bits)
ld   t0, 0(sp)     # Load double (64 bits)
sw   t0, 0(sp)     # Store word
sd   t0, 0(sp)     # Store double

# Branchements
beq  t0, t1, label # Branch if equal
bne  t0, t1, label # Branch if not equal
blt  t0, t1, label # Branch if less than
bge  t0, t1, label # Branch if greater/equal

# Appel de fonction
jal  ra, fonction  # Jump and link (ra = retour)
jalr zero, ra, 0   # Retour (pseudo-instruction : ret)
```

---

## 7. Outils

```bash
# NASM (assembleur x86, syntaxe Intel)
nasm -f elf64 fichier.asm -o fichier.o
ld fichier.o -o programme
./programme

# GCC (inline assembly + compilation)
gcc -S programme.c -o programme.s   # Générer l'assembleur
gcc -O2 -S programme.c -o programme.s  # Avec optimisations

# Objdump (désassembler)
objdump -d executable | less
objdump -M intel -d executable     # Syntaxe Intel

# GDB (débogage assembleur)
gdb ./programme
layout asm       # Afficher l'assembleur
stepi            # Pas à pas instruction
info registers   # Voir les registres
x/10i $rip       # 10 instructions à partir de RIP

# Godbolt Compiler Explorer (en ligne)
# https://godbolt.org/
```

---

## 8. Patterns et Optimisations

```asm
; RAX = 0 (3 façons) :
mov rax, 0      ; 7 octets
xor rax, rax    ; 3 octets (meilleur)
xor eax, eax    ; 2 octets (zero-extend RAX automatiquement)

; Multiplier par constante sans MUL :
; x * 3 = x + x*2
lea rax, [rax + rax*2]       ; RAX *= 3

; x * 5 = x*4 + x
lea rax, [rax + rax*4]       ; RAX *= 5

; x * 9
lea rax, [rax + rax*8]       ; RAX *= 9

; Échange sans registre temporaire :
xor rax, rbx
xor rbx, rax
xor rax, rbx

; strlen manuel :
xor al, al       ; AL = 0 (terminateur)
mov rdi, string  ; RDI = adresse de la chaîne
repne scasb      ; Scanner jusqu'à trouver 0
```

---

## Références
- Intel x86-64 Manuals : https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
- ARM Architecture Reference : https://developer.arm.com/documentation
- RISC-V Spec : https://riscv.org/technical/specifications/
- Compiler Explorer : https://godbolt.org/