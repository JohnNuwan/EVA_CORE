---
name: reverse-engineering
description: Guide complet de rétro-ingénierie — Ghidra, Radare2, IDA Free, GDB, objdump, strace, ltrace, strings, xxd, analyse statique et dynamique de binaires.
---

# Reverse Engineering — Guide Complet

---

## Concepts fondamentaux

### Approches
| Type | Description |
|------|-------------|
| **Analyse statique** | Examiner le binaire sans l'exécuter |
| **Analyse dynamique** | Exécuter et observer le comportement |
| **Disassembly** | Reconstruire l'assembleur depuis le code machine |
| **Decompilation** | Reconstruire du pseudo-C depuis l'assembleur |

---

## 1. Outils de base — Première approche

### Identifier le fichier
```bash
file binaire                # Type de fichier
checksec --file=binaire     # Protections (PIE, NX, canary, RELRO)
```

### Strings — Extraire les chaînes
```bash
strings binaire
strings -n 8 binaire        # Chaînes de 8+ caractères
strings -t x binaire        # Avec offset hexadécimal
```

### Analyse des sections
```bash
readelf -h binaire          # Header ELF
readelf -S binaire          # Sections
readelf -s binaire          # Symboles
readelf -d binaire          # Sections dynamiques
objdump -d binaire          # Désassemblage complet
objdump -t binaire          # Table des symboles
nm binaire                  # Symboles (compact)
```

---

## 2. Analyse dynamique

### strace — Appels système
```bash
strace ./binaire
strace -f ./binaire         # Suivre les forks
strace -e open ./binaire    # Filtrer les appels open()
strace -o trace.log ./binaire  # Sauvegarder dans un fichier
```

### ltrace — Appels de bibliothèque
```bash
ltrace ./binaire
ltrace -e memcpy+strlen ./binaire  # Filtrer des fonctions spécifiques
```

### GDB — Debugger GNU
```bash
gdb ./binaire
(gdb) run
(gdb) break main
(gdb) break *0x08048400
(gdb) continue
(gdb) info registers
(gdb) x/32wx $esp            # Examiner la pile (32 mots en hex)
(gdb) x/s $esp               # Afficher comme chaîne
(gdb) disas main             # Désassembler main
(gdb) set $eax = 0           # Modifier un registre
(gdb) stepi / nexti          # Pas à pas instruction
```

### Pwntools (framework CTF)
```python
from pwn import *
p = process('./binaire')
p.sendline(b'AAAA')
print(p.recvline())
```

### GDB + Pwndbg (meilleure UX)
```bash
# Installer pwndbg
git clone https://github.com/pwndbg/pwndbg
cd pwndbg && ./setup.sh

# Commandes utiles pwndbg
(gdb) context              # Vue contextuelle (stack, regs, code)
(gdb) vmmap                # Carte mémoire
(gdb) search "/bin/sh"     # Recherche en mémoire
(gdb) ropgadget            # Trouver des gadgets ROP
```

---

## 3. Ghidra — Décompilateur NSA (Gratuit)

### Workflow Ghidra
```
1. File → New Project → Import File
2. Double-clic sur le binaire → Analyse → Accepter les analyseurs par défaut
3. Symbol Tree → trouver main()
4. Fenêtre Decompile → pseudo-code C
5. Renommer les variables (clic droit → Rename)
6. Identifier les structures et les flux de contrôle
```

### Raccourcis Ghidra
```
G          Aller à une adresse
L          Renommer un symbole
;          Ajouter un commentaire
Ctrl+E     Éditer le type de données
Ctrl+Shift+D  Afficher le graphe de flux
```

---

## 4. Radare2 — Framework CLI complet

### Commandes essentielles
```bash
r2 binaire                 # Ouvrir un binaire
r2 -A binaire              # Analyse automatique
r2 -d binaire              # Mode debug
r2 -w binaire              # Mode écriture (patching)
```

### Analyse
```bash
[0x08048000]> aaa          # Analyse complète
[0x08048000]> afl          # Lister toutes les fonctions
[0x08048000]> s main       # Aller à main
[0x08048000]> pdf          # Désassembler la fonction courante
[0x08048000]> V            # Mode visuel
[0x08048000]> VV           # Mode graphe visuel
```

### Recherche et patching
```bash
[0x08048000]> / flag        # Rechercher la chaîne "flag"
[0x08048000]> izz           # Lister toutes les strings
[0x08048000]> iI            # Info binaire (type, arch, bits)
[0x08048000]> is            # Symboles
```

### Utilitaire rabin2 (sans ouvrir le shell)
```bash
rabin2 -I binaire          # Info
rabin2 -z binaire          # Strings avec adresses
rabin2 -i binaire          # Imports
rabin2 -E binaire          # Exports
rabin2 -R binaire          # Relocations
rabin2 -S binaire          # Sections
```

---

## 5. Techniques d'analyse

### Cracker un simple password check
```
1. strings binaire → trouver la chaîne "Incorrect"
2. objdump -d binaire | grep -A5 "Incorrect"
3. Identifier la comparaison (cmp, test, jne, je)
4. Patcher le saut conditionnel ou inverser la logique
```

### Détection de packers
```bash
# Un binaire packé a peu de strings, sections bizarres (UPX0, UPX1)
strings binaire | wc -l     # Moins de 100 strings = suspect
# Dépacker UPX :
upx -d binaire
```

### Analyse de shellcode
```bash
# Convertir en binaire puis analyser
echo 'shellcode en hex' | xxd -r -p > shellcode.bin
r2 -a x86 -b 32 shellcode.bin
# ou : rabin2 -a x86 -b 32 shellcode.bin
```

---

## 6. Outils spécifiques par plateforme

### APK Android
```bash
# Décompiler un APK
apktool d application.apk
# Dex vers Java
jadx application.apk
d2j-dex2jar classes.dex
# Analyse dynamique
adb logcat
frida -U -l script.js com.package
```

### .NET / C#
```bash
# Décompiler un assembly .NET
# dnSpy (Windows GUI)
# ILSpy (Windows GUI)
# dotPeek (Windows GUI)
# monodis (Linux)
monodis assembly.exe
```

### Mach-O (macOS)
```bash
otool -L binaire            # Librairies liées
otool -tV binaire           # Désassemblage
```

---

## 7. Cheatsheet rapide

```bash
# Première approche d'un binaire
file binaire                    # Type
checksec --file=binaire         # Protections
strings binaire | less          # Chaînes
objdump -d binaire | grep main  # Désassemblage ciblé
strace ./binaire                # Appels système
ltrace ./binaire                # Appels librairie

# Ghidra : File → Import → Analyze → main() → Decompile
# r2 : r2 -A binaire → aaa → afl → s main → pdf → VV
# GDB : gdb binaire → break main → run → stepi
```

### Ressources
- **Ghidra** : https://ghidra-sre.org
- **Radare2** : https://rada.re
- **Pwndbg** : https://github.com/pwndbg/pwndbg
- **dogbolt.org** : Décompilateur en ligne
- **crackmes.one** : Entraînement reverse