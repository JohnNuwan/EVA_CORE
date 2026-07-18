---
name: language-b
title: "Doctorat — Langage B"
description: "Compétence niveau docteur en langage B. Couvre l'histoire du langage B (Ken Thompson, 1969), syntaxe, types, relations avec BCPL et C, le compilateur, la machine PDP-11, l'impact sur l'évolution des langages, et la préservation numérique."
category: research
lang: fr
---

# Doctorat : Langage B

## Présentation
Le langage B est un langage de programmation développé par Ken Thompson et Dennis Ritchie aux Bell Labs en 1969-1970, principalement pour le système d'exploitation UNIX sur la machine PDP-11. B est le prédécesseur direct du langage C et a servi de pont entre BCPL (Basic Combined Programming Language, 1967) et C (1972). Bien que B soit aujourd'hui un langage historiquement important plutôt qu'utilisé, son influence sur la programmation système moderne est incommensurable : il a introduit ou popularisé des concepts qui sont devenus la base de C, C++, Java, C#, et une grande partie de la programmation impérative moderne. B est un langage non typé (typeless), interprété/compilé vers du code threadé (threaded code), utilisant des pointeurs comme mécanisme central.

## Histoire et Contexte
- **1966** : Martin Richards développe BCPL (Basic Combined Programming Language) au MIT
- **1969** : Ken Thompson (Bell Labs) développe le langage B en s'inspirant de BCPL
- **1969-1970** : Thompson utilise B pour implémenter les premières versions d'UNIX sur PDP-7
- **1971** : B est porté sur la PDP-11 (le premier système UNIX largement utilisé)
- **1971-1972** : Dennis Ritchie commence à étendre B, donnant naissance à "New B" puis C
- **1973** : Le noyau UNIX est réécrit en C, remplaçant B
- **1975-1980** : B devient largement obsolète, remplacé par C
- **Importance historique** : B est le chaînon manquant entre les langages de haut niveau d'exploration (BCPL) et les langages système modernes (C)

## Architecture du Langage
- **Typeless** : B n'a pas de système de types — toutes les données sont des mots (words)
- **Interpréteur/compilateur** : B était initialement implémenté comme un compilateur vers du code threadé
- **Interpréteur** : Le B compiler produisait du "threaded code" exécuté par un interpréteur
- **P-code like** : B compile en bytecode interprété (précurseur du p-code Pascal, JVM bytecode)
- **Pointeurs omniprésents** : Le seul mécanisme de données était les pointeurs et les tableaux
- **Auto-increment** : L'opérateur *p++ (emprunté par C)
- **Fonctions** : Fonctions récursives, paramètres par valeur
- **Fichiers** : Les bibliothèques externes ("library" et "sys" sous UNIX)
- **Système d'exploitation** : B était le langage principal d'UNIX v1 (avant la réécriture en C)

## Système de Types
- **Pas de types** : B est un langage typeless — contrairement à BCPL et à C
- **Mot (word)** : L'unité de donnée fondamentale est le mot machine
- **Pointeurs** : Toute donnée peut être traité comme un pointeur (ou inversement)
- **Tableaux** : Les tableaux sont des pointeurs — a[i] est équivalent à *(a+i)
- **Entiers** : Pas de distinction entre entier et pointeur
- **Caractères** : Pas de type char distinct — les caractères sont stockés dans des mots
- **auto et extrn** : Classes de stockage (auto = local, extrn = externe)
- **Structures** : Pas de struct — remplacées par des tableaux de mots
- **Fonctions** : Les fonctions retournent des mots

## Compilation et Interprétation
- **Compilateur B** : B compile en threaded code (code threadé) — pas en code machine natif
- **Threaded code** : Suite d'adresses de sous-routines exécutées par l'interpréteur
- **Interpréteur B** : Exécute le code threadé généré par le compilateur
- **Précurseur du bytecode** : L'approche threaded code de B est un ancêtre du bytecode JVM
- **Compilation rapide** : La compilation B était conçue pour être rapide (itération rapide)
- **PDP-7** : Premier système cible (mots de 18-bit)
- **PDP-11** : Second système cible (mots de 16-bit)
- **Aucun compilateur moderne** : Pas de compilateur B maintenu pour les systèmes modernes
- **Émulation** : Les implémentations B historiques ne fonctionnent que sur des émulateurs PDP-11
- **B compiler recovery** : Des efforts de préservation numérique existent (PDP-11 Unix emulation)
- **bcpl/b** : BCPL (source de B) a une descendance plus accessible

## Mémoire et Performances
- **Mots machine** : Toute la mémoire est adressée par mots (word-addressable)
- **PDP-7** : 8K mots de mémoire (16K octets) — extrêmement contraint
- **PDP-11** : 24K mots (48K octets) typiquement — espace d'adressage très limité
- **Threaded code overhead** : Interprétation threaded code = plus lent que code natif
- **Mémoire compacte** : Le threaded code est très dense (un mot par instruction virtuelle)
- **Pas d'allocation dynamique** : Pas de malloc — la mémoire est gérée statiquement
- **Stack** : Stack d'appel limitée (taille fixe dans l'interpréteur)
- **Buffer overflow** : Pas de vérification de bornes — comme BCPL et le C pré-ANSI
- **Performance** : Environ 10x plus lent que le code PDP-11 natif

## Écosystème et Outils
- **Interpréteur mini-B** : Version simplifiée incluse dans les premiers UNIX
- **lib** : Bibliothèque standard B (I/O, chaînes)
- **sys** : Interface système UNIX (lecture/écriture de fichiers, etc.)
- **Éditeur** : ed (éditeur ligne standard UNIX)
- **Debogueur** : Pas de débogueur pour B (db pour PDP-11 assembly)
- **Assembleur** : as (assembleur PDP-11) pour les parties critiques
- **Système** : UNIX premier edition (V1) — écrit principalement en B + assembleur
- **Fichiers** : Source B (suffixe .b), code threadé (.o)
- **BCPL** : Compilateur BCPL plus largement disponible (sur Multics, etc.)
- **Disponibilité moderne** : B n'est pas disponible sur les systèmes modernes (sauf émulation PDP-11)

## Concurrence et Parallélisme
- **Pas de concurrence native** : B est séquentiel (UNIX v1 ne supportait pas le multitâche)
- **Processus** : UNIX fork() était en assembleur — pas accessible depuis B
- **Signaux** : Pas de signaux dans le langage
- **Parallélisme** : Pas de support — les machines PDP n'avaient qu'un seul CPU
- **Context switching** : Le contexte d'exécution B est défini par l'interpréteur

## Patterns Avancés
- **Tableaux comme pointeurs** : a[i] = *(a+i) — convention héritée par C
- **Pointeurs auto-incrément** : *p++ = val — pattern adopté par C (et des décennies de code C)
- **Setjmp/longjmp** : Patterns de contrôle non-local (précurseur des exceptions)
- **Opaque types** : Pointeurs vers des structures de données non typées
- **Interpréteur dans le langage** : Le threaded code de B est un précurseur des DSL
- **Paradigme impur** : Fonctions avec effets de bord (modification de pointeurs globaux)
- **String (août 1972)** : Les chaînes sont des tableaux de mots terminés par un mot nul
- **Interrupt handlers** : Gestion des entrées/sorties et interruptions (code machine)

## Optimisation
- **Threaded code density** : Optimise la taille du code (important sur les machines à mémoire limitée)
- **Direct threading** : Optimisation du threaded code pour réduire l'overhead d'interprétation
- **Tail-call optimization** : Les fonctions terminales optimisées par le compilateur B
- **Inlining** : Certaines fonctions sont inlinées manuellement (écrites en assembleur)
- **Optimisation manuelle** : Réécriture des points chauds en assembleur PDP-11
- **Pas d'optimisation du compilateur** : Le compilateur B ne faisait pas d'optimisation significative

## Interopérabilité
- **B ↔ assembleur PDP-11** : Les fonctions B peuvent appeler du code assembleur
- **Assembleur pour les performances** : Les parties critiques d'UNIX étaient en assembleur
- **Syscalls** : Interface système UNIX via des appels assembleur (trap)
- **B ↔ BCPL** : Pas d'interop directe (BCPL était sur Multics/Honeywell)
- **B → C** : La transition de B à C s'est faite progressivement (fonction par fonction)
- **bcpl → b → c** : Évolution linéaire de la syntaxe et des concepts

## Applications Industrielles
- **UNIX Operating System v1** : Premier système d'exploitation UNIX (1971)
- **PDP-11** : Systèmes de mini-ordinateurs DEC
- **Text processing** : ed, roff (traitement de texte)
- **File system** : Gestionnaire de fichiers UNIX
- **Device drivers** : Pilotes de périphériques PDP-11
- **Assembleur, linker** : Outils de développement
- **Background** : B était avant tout un outil de recherche aux Bell Labs
- **Impact indirect** : A influencé des systèmes non-UNIX via C
- **Usage moderne** : Aucun — B est strictement historique

## Sécurité
- **Pas de mémoire safe** : B n'a aucune protection mémoire (typeless)
- **Word access** : Les mots sont la seule abstraction — pas de type checking
- **Buffer overflow** : Aucune vérification de bornes
- **Pointeurs sauvages** : L'absence de types rend tout pointeur plausible
- **Privilège** : Le code B s'exécutait en mode noyau (UNIX v1 n'avait pas de distinction kernel/user)
- **Aucun exploit connu** : Pas de CVE connues pour B (obsolète avant les bases de données de vulnérabilités)
- **Leçons pour C** : Les problèmes de sécurité de C (buffer overflow, format string) ont leurs racines dans B

## Veille Technologique
- **"The Development of the C Language"** (Ritchie, 1993) : Histoire de B et C
- **"UNIX Time-Sharing System"** (Ritchie & Thompson, 1974) : Contexte UNIX v4
- **"Bell Labs PDP-11 Unix Emulation"** : Projets de préservation (SIMH, PUPS)
- **BCPL Language Documentation** : docs.crayne.net — BCPL (précurseur)
- **History of Programming Languages (HOPL)** : Conférences ACM
- **Computer History Museum** : Archives de code source UNIX ancien
- **Bell Labs** : Archives des documents originaux B
- **TUHS** (The UNIX Heritage Society) : Préservation des sources UNIX anciens
- **Ressources** :
  - "The B Manual" (Ken Thompson, 1972) — spécification originale
  - "BCPL to B to C" (Dennis Ritchie) — article historique
  - "The Unix Tree" (TUHS) — code source UNIX V1 en B
- **Impact moderne** : Le langage B a montré qu'un langage simple et typeless peut construire un système d'exploitation complet — une leçon qui a mené au succès de C