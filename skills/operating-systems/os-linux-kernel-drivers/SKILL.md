---
name: os-linux-kernel-drivers
description: "Développer au niveau du noyau Linux (Kernel Space), compiler des noyaux personnalisés, concevoir des modules noyau chargeables (LKM) en C et écrire des pilotes de périphériques."
version: 1.0.0
author: EVA
license: Privée EVA St-Étienne
platforms: [linux]
metadata:
  EVA:
    tags: [linux, kernel, drivers, lkm, system-programming, c, makefile, low-level]
    related_skills: [os-linux-admin, embedded-systems-firmware]
---

# Développement Kernel Linux & Pilotes (LKM)

## Vue d'ensemble

Cette compétence guide le développement en espace noyau (**Kernel Space**) sous Linux. Travailler dans le noyau nécessite d'écrire du code C hautement optimisé, sans accès aux bibliothèques standards utilisateur (comme `glibc`). Elle couvre la compilation personnalisée du noyau Linux, l'écriture de modules noyau chargeables (**LKM - Loadable Kernel Modules**), la gestion des interruptions matérielles et la conception de pilotes de périphériques (en particulier les pilotes orientés caractères ou *char devices*).

## Quand l'utiliser

À utiliser lorsque l'utilisateur demande de :
- Compiler un noyau Linux personnalisé avec des options de configuration spécifiques (`make menuconfig`).
- Écrire ou déboguer un module de noyau Linux (`.ko`) pour interagir directement avec le matériel ou le processeur.
- Implémenter un pilote de périphérique de type caractère (Char Driver) pour communiquer avec un matériel connecté (via GPIO, I2C, SPI au niveau noyau).
- Gérer l'allocation de mémoire noyau (`kmalloc` / `vmalloc`) et la synchronisation (mutexes, spinlocks).
- Analyser des crashs de noyau (Kernel Panic / Oops) à l'aide des logs système (`dmesg`, `kdump`).

## Exemple de Module Noyau Simple (LKM en C)

### 1. Code source : `EVA_module.c`

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("EVA");
MODULE_DESCRIPTION("Module de test d'affichage Kernel Space");
MODULE_VERSION("1.0");

// Fonction appelée lors du chargement du module
static int __init EVA_init(void) {
    pr_info("EVA Module : Chargement réussi dans le noyau Linux.\n");
    return 0; // 0 signifie succès du chargement
}

// Fonction appelée lors du déchargement du module
static void __exit EVA_exit(void) {
    pr_info("EVA Module : Déchargement du module.\n");
}

module_init(EVA_init);
module_exit(EVA_exit);
```

### 2. Le Makefile d'accompagnement :

```makefile
obj-m += EVA_module.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

*Commandes d'utilisation* :
- **Compiler** : `make`
- **Charger** : `sudo insmod EVA_module.ko`
- **Vérifier** : `dmesg | tail`
- **Lister** : `lsmod | grep EVA`
- **Décharger** : `sudo rmmod EVA_module`

## Concepts Clés de Sécurité Noyau

1.  **Différence Kernel vs User Space** : Le code noyau s'exécute avec les privilèges maximum du processeur (Ring 0). Un simple plantage (ex: pointeur nul) dans le noyau provoque un blocage complet de la machine (**Kernel Panic**), alors qu'en espace utilisateur, cela fermerait uniquement l'application concernée.
2.  **Gestion de la mémoire** : Ne jamais utiliser `malloc()` ou `free()`. Utiliser `kmalloc()` pour de petites allocations continues physiquement (mémoire rapide) et `kfree()`.
3.  **Transfert User/Kernel** : Pour échanger des données entre une application utilisateur et le noyau, utiliser impérativement les fonctions sécurisées `copy_to_user()` et `copy_from_user()` pour éviter des corruptions de mémoire ou des failles de sécurité.

## Pièges Courants (Common Pitfalls) (Pièges Courants)

1.  **Utilisation de fonctions bloquantes sous Spinlock :**
   * *Erreur :* Mettre le CPU en veille (`msleep()`) ou faire une allocation mémoire pouvant bloquer (`GFP_KERNEL`) alors qu'un verrou tournant (Spinlock) est actif. Cela provoque un interblocage (Deadlock) instantané du système.
   * *Correction :* Ne jamais bloquer le thread ou dormir sous Spinlock. Si l'on doit s'endormir ou attendre, utiliser des Mutexes à la place des Spinlocks.

2.  **Fuites de mémoire noyau (Kernel Memory Leaks) :**
   * *Erreur :* Omettre de libérer la mémoire allouée par `kmalloc()` dans la fonction d'erreur ou lors du déchargement (`exit`). Le système perdra progressivement de la RAM disponible jusqu'au crash de la machine.
   * *Correction :* Libérer rigoureusement toutes les ressources allouées dans l'ordre inverse de leur création lors du déchargement ou en cas de retour d'erreur anticipé.

## Liste de vérification (Checklist)

- [ ] Le module compile sans aucun avertissement (Warning) du compilateur GCC.
- [ ] Tous les accès aux données utilisateurs utilisent `copy_to_user()` et `copy_from_user()`.
- [ ] Les verrous (spinlocks et mutexes) sont correctement appairés et libérés dans toutes les branches logiques (y compris en cas d'erreur).
- [ ] La fonction d'initialisation (`__init`) libère proprement les ressources déjà acquises si l'initialisation échoue à mi-parcours.
- [ ] Les messages de log système utilisent les niveaux de priorité noyau adéquats (ex: `pr_info()`, `pr_err()`).

