---
name: language-cobol
title: "Doctorat — COBOL (Common Business-Oriented Language)"
description: "Compétence niveau docteur en COBOL. Couvre COBOL 85/2002/2023, divisions, sections, paragraphs, file handling, report writer, CICS, DB2, JCL, mainframe modernization, legacy migration, et l'interopérabilité avec systèmes modernes."
category: research
lang: fr
---

# Doctorat : COBOL

## Présentation
COBOL (Common Business-Oriented Language) est un langage de programmation conçu pour les applications de gestion et commerciales, créé par le CODASYL (Conference on Data Systems Languages) en 1959. Conçu pour être lisible par des non-programmeurs (syntaxe proche de l'anglais), il est devenu le langage dominant du traitement des données sur mainframe. Plus de 70% des transactions commerciales mondiales passent par du code COBOL. Des systèmes critiques (banques, assurances, gouvernements, transports) tournent encore sur COBOL, avec des milliards de lignes de code en production.

## Histoire et Contexte
- 1959 : Création par le CODASYL (Grace Hopper participe à la conception)
- 1960 : COBOL 60 — première spécification
- 1968 : ANSI COBOL — première standardisation américaine
- 1974 : COBOL 74 — structuration améliorée
- 1985 : COBOL 85 — programmation structurée, END-IF, scope terminators
- 1989 : COBOL 85 amendements — intrinsic functions
- 2002 : COBOL 2002 — OOP, UNICODE, floating-point, XML, locaux
- 2014 : COBOL 2014 — améliorations OOP, JSON, comptabilité
- 2023 : COBOL 2023 — améliorations modernisation, performances
- Compilateurs : IBM Enterprise COBOL (z/OS), GnuCOBOL (OpenCOBOL), Micro Focus COBOL, AcuCOBOL

## Architecture du Langage
- **Structure divisionnelle** : Le code COBOL est divisé en 4 divisions obligatoires
- **IDENTIFICATION DIVISION** : Programme ID, author, date, remarques
- **ENVIRONMENT DIVISION** : Configuration hardware (fichiers, imprimantes)
- **DATA DIVISION** : Déclarations de données (WORKING-STORAGE, LINKAGE, FILE SECTION)
- **PROCEDURE DIVISION** : Code exécutable (paragraphs, sections)
- **Divisions/Sections/Paragraphs** : Hiérarchie du code
- **Sentences/Statements** : READ, WRITE, MOVE, ADD, PERFORM, IF, EVALUATE
- **Copybooks** : Fichiers inclus (COPY) pour les structures de données partagées
- **77 levels** : Éléments de données indépendants
- **01-49 levels** : Hiérarchie des structures de données
- **88 levels** : Noms de condition pour des valeurs spécifiques

## Système de Types
- **PICTURE clause (PIC)** : Définition des données — PIC 9(5) pour entier 5 digits
- **Alphabétique** : PIC A — lettres
- **Numérique** : PIC 9 — chiffres, PIC S9 signé, PIC V pour virgule implicite
- **Alphanumérique** : PIC X — caractères quelconques
- **USAGE** : BINARY, COMP, COMP-1, COMP-2, COMP-3 (packed decimal), DISPLAY
- **Packed Decimal (COMP-3)** : Stockage BCD (Binary Coded Decimal) — précis pour les calculs financiers
- **UNICODE** (COBOL 2002+) : PIC U pour caractères Unicode
- **Floating-point** (COBOL 2002+) : USAGE COMP-2 (IEEE 754 double)
- **OCCURS** : Tableaux (REDEFINES, DEPENDING ON)
- **REDEFINES** : Chevauchement de zones mémoires
- **RENAMES** : Regroupement de champs sous un nouveau nom
- **CONDITION-NAME (88 level)** : Noms pour conditions : 88 Approved VALUE "A"

## Compilation et Interprétation
- **Compilation trad** : Source (.cob/.cbl/.cpy) → Compilateur → Load module (.so/.dll)
- **IBM Enterprise COBOL** : Compilateur optimisé pour z/OS mainframe
- **GnuCOBOL** : Compilateur libre — COBOL → C → natif
- **Micro Focus COBOL** : Compilateur cross-platform (Windows, Linux, Unix)
- **JCL** (Job Control Language) : Langage de contrôle pour les batchs sur mainframe
- **Batch processing** : Traitement par lots (batch jobs) — entrée/sortie fichier
- **Online (CICS)** : Traitement transactionnel en ligne
- **DB2** : Base de données relationnelle IBM (SQL embarqué en COBOL)
- **IMS DB/DC** : Base de données hiérarchique IBM
- **CICS** : Customer Information Control System — moniteur transactionnel
- **BMS** : Basic Mapping Support — gestion des écrans 3270

## Mémoire et Performances
- **Efficacité mainframe** : COBOL est optimisé pour les architectures mainframe IBM z/Architecture
- **Packed decimal (COMP-3)** : Calculs décimaux sans erreurs d'arrondi — adapté à la finance
- **Binary (COMP)** : Pour les index et calculs binaires
- **Fichiers VSAM** : Indexed/Sequential access — accès performant aux fichiers sur mainframe
- **Buffer management** : Contrôle des buffers d'entrée/sortie fichier
- **GDGs (Generation Data Groups)** : Groupes de fichiers générationnels
- **Memory** : Gestion mémoire manuelle via WORKING-STORAGE, LINKAGE
- **Performance** : COBOL est extrêmement performant pour le batch processing — des milliards d'enregistrements traités quotidiennement
- **SORT/MERGE** : Tris et fusions intégrés (COBOL SORT statement)
- **File I/O** : Accès séquentiel, indexé, relatif, VSAM

## Écosystème et Outils
- **IBM Enterprise COBOL** : z/OS, compilateur avec optimisation
- **IBM z/OS** : Système d'exploitation mainframe
- **JCL** : Job Control Language — orchestration des batchs
- **TSO/ISPF** : Environnement de développement interactif mainframe
- **Endevor / Changeman** : Gestion de versions mainframe
- **CICS** : Moniteur transactionnel
- **IMS** : Database et transaction manager
- **DB2** : Base de données relationnelle IBM
- **GnuCOBOL** : Compilateur libre (OpenCOBOL) — COBOL vers C
- **Micro Focus COBOL** : Solutions cross-platform, Visual COBOL
- **COBOL IT** : Compilateur Windows/Unix
- **Modern IDEs** : VS Code avec extensions COBOL, Micro Focus Visual COBOL
- **Unit testing** : GnuCOBOL unit tests, COBOL-IT tests

## Concurrence et Parallélisme
- **Batch processing** : Traitement séquentiel de masse — parallélisme via JCL et lots multiples
- **CICS multi-threading** : Transactions multiples simultanées (Online)
- **MVS multitasking** : Parallelism au niveau OS (z/OS)
- **DB2 parallelism** : Parallélisme dans les requêtes SQL
- **IMS** : Traitement transactionnel parallèle
- **Parallel sysplex** : Clustering mainframe (z/OS Parallel Sysplex)
- **Coupling Facility** : Partage de données entre plusieurs mainframes
- **Workload Manager (WLM)** : Gestion de charge et parallélisme
- **JCL job steps** : Étapes parallèles dans un même batch job

## Patterns Avancés
- **Copybooks** : Partage de structures de données (DSECT-like)
- **Table-driven processing** : Traitement par tables de décision
- **PERFORM VARYING** : Boucles avec variations
- **PERFORM UNTIL/THRU** : Contrôle de flot structuré
- **EVALUATE** : Switch-case amélioré (COBOL 85+)
- **INLINE PERFORM** : Boucles inline
- **Dynamic CALL** : Appel dynamique de sous-programmes
- **Nested programs** : Programmes imbriqués
- **CICS BMS** : Gestion des écrans (mapping)
- **COMMAREA** : Zone de communication entre programmes CICS
- **DFHRESP** : Gestion des réponses CICS
- **File status checking** : Vérification de statut après opération fichier
- **Error handling via DECLARATIVES** : Gestion d'erreur structurée
- **Date arithmetic** : Manipulation de dates avec INTDATE, FUNCTION INTEGER-OF-DATE

## Optimisation
- **COBOL SORT** : Algorithme de tri optimisé (tri externe pour grandes quantités de données)
- **File organization** : Choix entre fichier séquentiel, indexé (VSAM), relatif
- **VSAM optimization** : CI (Control Interval) sizing, CAS (Control Area Sizing)
- **Buffer sizing** : Optimisation des buffers pour accès séquentiels
- **In-memory tables** : Tables COBOL en mémoire via OCCURS
- **Compiler options** : OPTIMIZE(STANDARD), OPTIMIZE(FULL) chez IBM
- **Inline code** : PERFORM inline plutôt que PERFORM THRU
- **Data alignment** : Alignement sur les frontières mainframe
- **Packed decimal** : Plus compact et précis que DISPLAY
- **BINARY vs DISPLAY** : BINARY plus rapide pour les calculs

## Interopérabilité
- **COBOL ↔ C** : CALL to C programs, CICS LINK to C modules
- **COBOL ↔ Java** : IBM JZOS — Java dans la JVM sur z/OS, appel depuis COBOL
- **Web services** : COBOL 2002+ — SOAP/XML, JSON, HTTP
- **CICS Web Support** : CICS en tant que serveur HTTP
- **DB2 SQL** : SQL embarqué (EXEC SQL)
- **CICS LINK/START** : Communication entre transactions CICS
- **XML PARSE** (COBOL 2002+) : Parsing XML natif
- **JSON GENERATE/PARSE** (COBOL 2014+) : JSON natif
- **REST APIs** : Micro Focus, IBM z/OS Connect — exposition COBOL en API REST
- **z/OS Connect** : API REST pour services mainframe
- **SOAP** : Web services SOAP COBOL
- **MQ Series** : IBM MQ — messaging entre COBOL et systèmes ouverts
- **Kafka connect** : Modern streaming connect pour COBOL

## Applications Industrielles
- **Banques** : Systèmes de comptes courants, transactions, crédits, SWIFT
- **Assurances** : Gestion des polices, sinistres, primes
- **Gouvernement** : Sécurité sociale, impôts, retraites
- **Administration** : Paie, RAM, gestion RH
- **Transport aérien** : Réservations (Sabre, Amadeus — historique)
- **Distribution** : Grands magasins, inventaire, chaîne logistique
- **Télécommunications** : Facturation (billions de transactions)
- **Compagnies ferroviaires** : SNCF, Deutsche Bahn — réservation
- **Santé** : Medicare, systèmes hospitaliers legacy
- **Services publics** : EDF, eau, gaz — facturation
- **Systèmes de réservation** : Hôtels, locations de voiture
- **Plus de 70% des transactions financières mondiales** passent par du COBOL

## Sécurité
- **Mainframe security** : RACF, Top Secret, ACF2 — sécurité mainframe mature
- **Data encryption** : ICSF (Integrated Cryptographic Service Facility)
- **SSL/TLS** : CICS TLS support
- **Audit** : SMF (System Management Facility) — logging et audit
- **Authorization** : RACF access control pour programmes et fichiers
- **Program security** : Authorized program facility, APF authorized
- **Transaction security** : CICS security (userid, password, profile)
- **SQL injection** : Les EXEC SQL paramétrés réduisent les risques
- **Legacy security** : Pas de buffer overflow natif (COBOL est safe)
- **Modern concerns** : Exposition via APIs REST nécessite une sécurisation moderne

## Veille Technologique
- **IBM z/OS** : ibm.com/products/zos — nouvelles versions, modernisation
- **GnuCOBOL** : gnucobol.sourceforge.io — projet open-source
- **Micro Focus** : microfocus.com — solutions COBOL modernes
- **Open Mainframe Project** : openmainframeproject.org — Linux Foundation
- **SHARE** : Conférence mainframe
- **IBM Z Developer** : IBM Z Developer Community
- **Mainframe modernization** : z/OS Connect, API exposure
- **COBOL 2023** : Dernier standard ISO — améliorations modernisation
- **Migration patterns** : COBOL → Java, COBOL → Microservices (event sourcing)