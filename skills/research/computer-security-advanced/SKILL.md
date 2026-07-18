---
name: computer-security-advanced
description: "Compétence niveau expert en sécurité informatique avancée. Couvre l'exploitation binaire, reverse engineering, kernel exploitation, Windows internals, macOS/iOS security, firmware security, trusted execution TEE SGX/SEV, side-channel, fault attacks, cryptanalysis, advanced persistent threats APT, supply chain attacks, zero-day research, CVE research, et exploit development."
keywords: [security, exploitation, reverse engineering, kernel, APT, zero-day, binary exploitation, cryptanalysis]
categories: [cs.CR, cs.SE, cs.PL, cs.DC, cs.AI]
---

# Compétence Sécurité Informatique Avancée

## Présentation

Cette compétence couvre la sécurité informatique avancée, de l'exploitation binaire à l'analyse de malwares APT, en passant par le reverse engineering, l'exploitation kernel et la sécurité Web3.

---

## Exploitation Binaire

- **Buffer Overflow** : Débordement de tampon classique (stack-based)
- **ROP (Return-Oriented Programming)** : Programmation orientée retour (gadgets chaînés)
- **JOP (Jump-Oriented Programming)** : Programmation orientée saut
- **ret2libc / ret2plt** : Retour à la libc ou à la PLT
- **Heap Exploitation** : Use-after-free, double free, heap spray, tcache poisoning
- **Format String** : Attaque par chaîne de format (%n, %x)
- **ASLR Bypass** : Contournement de l'ASLR (Address Space Layout Randomization)
- **NX Bypass** : Bypass de NX/XD (No-Execute)
- **Stack Canary Bypass** : Bypass des stack canaries (stack leak, brute-force)
- **WinDbg / GDB** : Debuggers pour analyse d'exploitation
- **pwntools** : Framework Python pour exploitation binaire
- **ROPgadget** : Outil de recherche de gadgets ROP
- **one_gadget** : Gadget execve("/bin/sh") automatique
- **seccomp Bypass** : Bypass des restrictions seccomp
- **Sandbox Escape** : Évasion de sandbox (browser, container, VM escape)

## Reverse Engineering

- **IDA Pro** : Désassembleur/décompilateur interactif
- **Ghidra** : Reverse engineering suite (NSA, open source)
- **Binary Ninja** : Plateforme de reverse engineering moderne
- **x64dbg** : Debugger pour Windows x64/x86
- **radare2 / r2** : Framework de reverse engineering open source
- **angr** : Concolic/symbolic execution pour binaires
- **Decompilation / Lifting** : Décompilation et lifting (intermédiaire représentation)
- **SMT Z3** : Solver SMT pour contraintes symboliques (Z3 Prover)
- **Firmware Reversing** : Reverse de firmware embarqué
- **Bootloader / UEFI / BIOS** : Reverse du boot process
- **JTAG / SWD / SVD** : Debug hardware et accès physique
- **Decapping** : Imagerie de puce (microscopie électronique)
- **Side-Channel (SCA)** : Analyse par canaux auxiliaires (timing, power, EM)

## Kernel Exploitation

- **Windows Kernel** : Analyse de noyau Windows (NT kernel)
- **Driver Exploits** : Exploitation de drivers Windows (IOCTL)
- **HEVD (HackSys Extreme Vulnerable Driver)** : Driver vulnérable pédagogique
- **Kernel Pool** : Exploitation du pool noyau (overflows, use-after-free)
- **Token Stealing** : Vol de token SYSTEM
- **Kernel ROP** : ROP en mode noyau
- **SMEP Bypass** : Bypass de Supervisor Mode Execution Prevention
- **KASLR Bypass** : Bypass de Kernel ASLR
- **Linux Kernel (LKM)** : Modules kernel Linux, exploitation
- **eBPF Exploitation** : Exploitation via eBPF
- **LPE (Local Privilege Escalation)** : Élévation de privilèges locale
- **Container Escape** : Évasion de conteneur (Docker, K8s)
- **K8s Privilege Escalation** : Escalade dans Kubernetes
- **Cloud Escape** : Évasion d'environnement cloud

## Web3 et Smart Contract

- **Solidity Reversing** : Reverse de bytecode Solidity
- **EVM Bytecode** : Désassemblage et analyse EVM
- **Slither** : Analyseur statique Solidity
- **Mythril** : Security analysis tool pour smart contracts
- **Echidna** : Fuzzer pour smart contracts
- **Reentrancy** : Attaque par réentrance
- **Flash Loan Attacks** : Attaques par flash loans
- **DeFi Hacks** : Hacks de protocoles DeFi (wallets, bridges, lending)
- **Oracle Manipulation** : Manipulation d'oracles de prix
- **Sandwich MEV** : Attaques sandwich (MEV extraction)
- **Rug Pulls** : Rug pulls (scams crypto)
- **Signature Replay** : Rejeu de signatures
- **Private Key Leak** : Fuite et vol de clés privées

## APT et Menaces Avancées

- **APT Nation-State** : Acteurs étatiques (APT, groupes sponsorisés)
- **Initial Access** : Phishing, exploitation, supply chain
- **Persistence** : Mécanismes de persistance (services, registry, cron)
- **C2 (Command & Control)** : Infrastructure de contrôle
- **Exfiltration** : Exfiltration de données
- **Living-off-the-Land (LOLBins)** : Binaires système pour evasion
- **Fileless Malware** : Malware sans fichier (mémoire uniquement)
- **PowerShell / WMI / .NET** : Exécution via outils Microsoft
- **BITS / Scheduled Tasks** : Utilisation de fonctionnalités Windows
- **Stealth / EDR Bypass** : Contournement de détection (EDR, AV)
- **Kernel Callbacks** : Utilisation de callbacks noyau pour evasion