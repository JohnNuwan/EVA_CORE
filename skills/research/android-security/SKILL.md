---
name: android-security
description: Compétence niveau expert en sécurité Android — architecture, reverse engineering, pentest mobile, exploitation, malware, et automation.
category: research
---

# Sécurité Android — Reverse, Pentest & Exploitation

## Architecture de sécurité
- **Sandboxing** : UID/GID par application, SELinux (enforcing), seccomp-bpf
- **Permissions** : Évolution API 1→34, runtime permissions (Android 6+), permission groups
- **Keystore / TEE / StrongBox** : matériel dédié, attestation, KeyGenParameterSpec
- **Verified Boot** : dm-verity, AVB (Android Verified Boot), vbmeta, rollback protection

## Root & Déverrouillage
- **Magisk** : Systemless root, modules, Zygisk, MagiskHide, Shamiko (contournement detection)
- **KernelSU** : Root noyau, GKI, modules
- **APatch** : Patch APK sans root
- **Détection** : SafetyNet, Play Integrity API, rootbeer, détection via /system/xbin/su
- **Contournement** : Zygisk modules, KernelSU, hide my applist

## Reverse Engineering APK
- **Chaîne complète** : apktool (décodage resources + smali) → jadx (décompilation Java) → analyse smali/bytecode
- **Frida** : Hooking dynamique (Java.choose, Interceptor.attach), bypass SSL pinning, crypto tracing
- **Objection** : Exploration runtime, dump mémoire, bypass jailbreak/root, patch APK
- **MobSF** : Analyse statique + dynamique automatisée (API, permissions, data storage)
- **Ghidra / radare2** : Reverse natif (.so, ELF)
- **Androguard** : Analyse statique Python
- **APKLeaks** : Extraction d'endpoints, tokens, secrets

## Pentest Mobile (OWASP Mobile Top 10)
- **M1** : Improper platform usage (WebView, intents, IPC)
- **M2** : Insecure data storage (SharedPreferences, SQLite, SD card, keystore)
- **M3** : Insecure communication (HTTP, SSL pinning bypass)
- **M4** : Insecure authentication (local auth, biometric bypass)
- **M5** : Insufficient cryptography (hardcoded keys, weak algo)
- **M6** : Insecure authorization (deep links, content providers)
- **M7** : Client code quality (buffer overflow, format string)
- **Drozer** : Content provider injection, SQLi, activity hijacking, intent test
- **Objection** : Bypass jailbreak, disable SSL pinning, dump keychain

## Exploits Android connus
- **BlueBorne** (CVE-2017-0781) : RCE Bluetooth
- **Broadpwn** (CVE-2017-9417) : RCE WiFi Broadcom
- **Stagefright** (CVE-2015-1538) : RCE MMS
- **Dirty COW** (CVE-2016-5195) : LPE race condition
- **Dirty Pipe** (CVE-2022-0847) : LPE noyau Linux
- **Binder** (CVE-2019-2215) : Use-after-free LPE
- **Fuzzing** : Honggfuzz, AFL sur HAL, services, noyau

## Malware Android
- **Taxonomie** : Banking trojan, spyware, ransomware, adware, SMS trojan, dropper, backdoor, bootkit, ransomware
- **Techniques infection** : Dropper, repackaging, update hijacking, sideloading
- **Anti-analyse** : Emulator detection, Frida detection, obfuscation (ProGuard, OLLVM, DexGuard), packing (UPX, custom)
- **Chaîne analyse** : Capture réseau → analyse statique MobSF → dynamic sandbox → désobfuscation → signature

## Attaques réseau & SSL Pinning
- **MITM** : mitmproxy, Bettercap, sslstrip
- **Bypass SSL Pinning** : 4 techniques — Objection (android sslpinning disable), Frida script, patch APK (NetworkSecurityConfig), Xposed module
- **Bluetooth** : BlueBorne, BLE, BlueZ, hijacking
- **NFC** : Tag cloning, card emulation, relay attack
- **Automation** : ADB, Frida scripts automatisés, Drozer auto-scan, pipeline CI/CD MobSF + APKLeaks

## Références
- OWASP Mobile Security Testing Guide (MSTG)
- OWASP Mobile Application Security Verification Standard (MASVS)
- Android Security Bulletins (AOSP)
- Frida CodeShare (codeshare.frida.re)
- Mobile Security Framework (MobSF) docs